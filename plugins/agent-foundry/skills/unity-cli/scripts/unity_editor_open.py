"""Open a Unity Editor without going over the repository's Editor limit.

Agents call this instead of `unity open`. It takes an OS-held lock that every
checkout and worktree of the repository shares, counts the Unity Editors whose
project lies in one of the repository's checkouts, opens the project only when
this project has no Editor and the count is under the limit, and returns once
the new Editor process appears. The lock covers the count, the open and the PID
detection, so two sessions cannot both see room and both open. The OS releases
the lock when this process exits, so a crashed caller leaves nothing stale and
no lock file is ever deleted.

Editors are counted from the process table (their `-projectPath` argument), not
from `unity status`, which lists only Editors the Pipeline package can reach.

Exit codes: 0 OPENED (or WOULD_OPEN with --dry-run), 2 usage error,
3 ALREADY_OPEN, 4 LIMIT_REACHED, 5 LOCK_TIMEOUT, 6 OPEN_FAILED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXIT_OPENED = 0
EXIT_USAGE = 2
EXIT_ALREADY_OPEN = 3
EXIT_LIMIT_REACHED = 4
EXIT_LOCK_TIMEOUT = 5
EXIT_OPEN_FAILED = 6
DEFAULT_LIMIT = 2
POLL_SECONDS = 2.0
LOCK_NAME = "unity-editor-open.lock"
OWNER_NAME = "unity-editor-open.json"
# Unity accepts -projectPath in any case. The Hub passes it and its value unquoted
# (the value may contain spaces); other launchers quote the flag, the value, or both.
PROJECT_ARG = re.compile(r'-projectpath"?\s+(?:"([^"]+)"|(.+?))(?=\s+"?-[A-Za-z]|\s*$)', re.IGNORECASE)
IMPORT_WORKER = re.compile(r"AssetImportWorker", re.IGNORECASE)


def normalize(path: str | Path) -> str:
    return os.path.normcase(os.path.realpath(str(path).strip().strip('"')))


def inside(child: str, parent: str) -> bool:
    """True when the normalized path `child` is `parent` or lies below it."""
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def project_of(command_line: str) -> str | None:
    """The project of a main Editor process; None for import workers, the Hub and the CLI."""
    if not command_line or IMPORT_WORKER.search(command_line):
        return None
    match = PROJECT_ARG.search(command_line)
    if not match:
        return None
    return normalize(match.group(1) or match.group(2))


def process_rows() -> list[dict]:
    """Every running process that may be a Unity Editor, as {pid, command}."""
    override = os.environ.get("UNITY_EDITOR_OPEN_PROCESSES")
    if override:
        return json.loads(Path(override).read_text(encoding="utf-8"))
    if os.name == "nt":
        script = (
            "Get-CimInstance Win32_Process -Filter \"Name='Unity.exe'\" | "
            "Select-Object @{n='pid';e={$_.ProcessId}},@{n='command';e={$_.CommandLine}} | "
            "ConvertTo-Json -Compress"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True
        )
        text = completed.stdout.strip()
        if not text:
            return []
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    completed = subprocess.run(["ps", "-axww", "-o", "pid=,command="], capture_output=True, text=True)
    rows = []
    for line in completed.stdout.splitlines():
        pid, _, command = line.strip().partition(" ")
        if pid.isdigit() and "Unity" in command:
            rows.append({"pid": int(pid), "command": command})
    return rows


def running_editors() -> list[tuple[int, str]]:
    """(pid, normalized project) for every running main Unity Editor."""
    editors = []
    for row in process_rows():
        project = project_of(row.get("command") or "")
        if project:
            editors.append((int(row["pid"]), project))
    return editors


def repository_scope(project: Path) -> tuple[list[str], Path]:
    """The repository's checkout roots and the directory of the lock they share.

    Outside Git, the project itself is the scope and the lock lives in the temp folder.
    """
    git = shutil.which("git")
    if git:
        common = subprocess.run(
            [git, "-C", str(project), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
        )
        listing = subprocess.run([git, "-C", str(project), "worktree", "list", "--porcelain"], capture_output=True, text=True)
        if common.returncode == 0 and listing.returncode == 0:
            roots = [normalize(line[len("worktree "):]) for line in listing.stdout.splitlines() if line.startswith("worktree ")]
            return roots, Path(common.stdout.strip())
    digest = hashlib.sha1(normalize(project).encode("utf-8")).hexdigest()[:16]
    return [normalize(project)], Path(tempfile.gettempdir()) / "unity-editor-open" / digest


class RepositoryLock:
    """An exclusive OS lock on one byte of the shared lock file. The OS drops it when the process exits."""

    def __init__(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self.directory = directory
        self.handle = open(directory / LOCK_NAME, "a+b")
        self.held = False

    def try_acquire(self) -> bool:
        try:
            if os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        self.held = True
        return True

    def release(self) -> None:
        if self.held:
            try:
                (self.directory / OWNER_NAME).unlink()
            except OSError:
                pass
            if os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle, fcntl.LOCK_UN)
            self.held = False
        self.handle.close()


def write_owner(directory: Path, owner: str, project: Path) -> None:
    record = {"owner": owner, "project": str(project), "pid": os.getpid(), "started": time.time()}
    (directory / OWNER_NAME).write_text(json.dumps(record), encoding="utf-8")


def describe_holder(directory: Path) -> str:
    """Who the last lock holder said it was; informational only, never used to break the lock."""
    try:
        record = json.loads((directory / OWNER_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "holder unknown"
    return f"held by {record.get('owner') or 'unknown owner'} for {record.get('project')}"


def unity_command(unity_bin: str) -> list[str] | None:
    override = os.environ.get("UNITY_EDITOR_OPEN_CLI")
    if override:
        return json.loads(override)
    path = shutil.which(unity_bin)
    return [path] if path else None


def start_open(command: list[str], project: Path) -> subprocess.Popen:
    """Start `unity open` detached: it may keep running after the Editor is up, and it must outlive us."""
    flags = 0
    if os.name == "nt":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(
        [*command, "open", str(project), "--non-interactive", "--no-banner"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
        start_new_session=os.name != "nt",
    )


def wait_for_editor(target: str, before: set[int], seconds: float, opener: subprocess.Popen) -> tuple[int | None, int | None]:
    """The PID of a new Editor for `target`, or None; plus the opener's exit code if it failed early."""
    deadline = time.monotonic() + seconds
    while True:
        for pid, project in running_editors():
            if project == target and pid not in before:
                return pid, None
        code = opener.poll()
        if code not in (None, 0):
            return None, code
        if time.monotonic() >= deadline:
            return None, None
        time.sleep(POLL_SECONDS)


def open_editor(options: argparse.Namespace) -> int:
    project = Path(options.project).resolve()
    if not (project / "ProjectSettings" / "ProjectVersion.txt").is_file():
        print(f"EDITOR_OPEN: USAGE {project} is not a Unity project (ProjectSettings/ProjectVersion.txt is missing)")
        return EXIT_USAGE
    target = normalize(project)
    roots, lock_dir = repository_scope(project)
    lock = RepositoryLock(lock_dir)
    try:
        deadline = time.monotonic() + options.wait_seconds
        waiting = False
        while not lock.try_acquire():
            if time.monotonic() >= deadline:
                print(f"EDITOR_OPEN: LOCK_TIMEOUT another open of this repository did not finish within "
                      f"{options.wait_seconds:g}s ({describe_holder(lock_dir)})")
                return EXIT_LOCK_TIMEOUT
            if not waiting:
                print(f"waiting for another open of this repository ({describe_holder(lock_dir)})", flush=True)
                waiting = True
            time.sleep(POLL_SECONDS)
        write_owner(lock_dir, options.owner, project)
        editors = [(pid, path) for pid, path in running_editors() if any(inside(path, root) for root in roots)]
        mine = [pid for pid, path in editors if path == target]
        if mine:
            print(f"EDITOR_OPEN: ALREADY_OPEN pid={mine[0]} project={project} editors={len(editors)}/{options.limit}")
            return EXIT_ALREADY_OPEN
        if len(editors) >= options.limit:
            listing = "; ".join(f"pid={pid} {path}" for pid, path in editors)
            print(f"EDITOR_OPEN: LIMIT_REACHED editors={len(editors)}/{options.limit} ({listing}). "
                  "Continue code-only work and queue the Editor-bound step.")
            return EXIT_LIMIT_REACHED
        if options.dry_run:
            print(f"EDITOR_OPEN: WOULD_OPEN project={project} editors={len(editors)}/{options.limit}")
            return EXIT_OPENED
        command = unity_command(options.unity_bin)
        if not command:
            print(f"EDITOR_OPEN: OPEN_FAILED unity CLI '{options.unity_bin}' not found on PATH")
            return EXIT_OPEN_FAILED
        before = {pid for pid, _ in running_editors()}
        opener = start_open(command, project)
        pid, code = wait_for_editor(target, before, options.detect_seconds, opener)
        if pid is None:
            reason = f"`unity open` exited {code}" if code is not None else (
                f"no Editor process appeared within {options.detect_seconds:g}s")
            print(f"EDITOR_OPEN: OPEN_FAILED {reason} for {project}. "
                  "Check `unity status` and the process list before trying again; do not open twice.")
            return EXIT_OPEN_FAILED
        print(f"EDITOR_OPEN: OPENED pid={pid} project={project} editors={len(editors) + 1}/{options.limit}")
        return EXIT_OPENED
    finally:
        lock.release()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open a Unity Editor without going over the repository's Editor limit.")
    parser.add_argument("--project", required=True, help="Unity project root (the folder that holds ProjectSettings/).")
    parser.add_argument("--owner", default="", help="Task ID or session that will own the Editor; shown to waiting callers.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Editors allowed across the repository (default 2).")
    parser.add_argument("--wait-seconds", type=float, default=900, help="How long to wait for another open to finish (default 900).")
    parser.add_argument("--detect-seconds", type=float, default=180, help="How long to wait for the new Editor process (default 180).")
    parser.add_argument("--dry-run", action="store_true", help="Count and report under the lock, but do not open.")
    parser.add_argument("--unity-bin", default="unity", help="Unity CLI executable (default: unity on PATH).")
    try:
        options = parser.parse_args(argv)
    except SystemExit as error:
        return EXIT_USAGE if error.code else 0
    if options.limit < 1:
        print("EDITOR_OPEN: USAGE --limit must be at least 1")
        return EXIT_USAGE
    return open_editor(options)


if __name__ == "__main__":
    sys.exit(main())
