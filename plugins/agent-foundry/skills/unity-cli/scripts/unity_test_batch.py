"""Shared final-stage Unity test runs for several agent sessions.

Every session that needs its final-stage EditMode/PlayMode tests calls `submit`.
Requests for the same Unity project join one queue. The first caller becomes the
leader: it seals the queue, gates it with the Roslyn compile check, runs one
`unity test` per test platform with the merged filter, and gives each request
only the results its own filter selects. The other callers wait for their result.

When the project is open in an Editor, batch mode cannot run. The leader then
prints a plan with the merged filter and exits with LEADER_RUN_REQUIRED; that
session runs the plan through the live Editor and calls `publish`.

Exit codes: 0 PASS, 1 COMPILE_ERRORS, 2 usage error, 3 NO_TESTS, 4 WAIT_TIMEOUT,
5 STALE, 6 INFRA_ERROR, 7 BLOCKED_BY_OTHER_COMPILE, 8 FAIL, 10 LEADER_RUN_REQUIRED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ElementTree
from pathlib import Path

EXIT_CODES = {
    "PASS": 0,
    "COMPILE_ERRORS": 1,
    "NO_TESTS": 3,
    "STALE": 5,
    "INFRA_ERROR": 6,
    "BLOCKED_BY_OTHER_COMPILE": 7,
    "FAIL": 8,
}
EXIT_USAGE = 2
EXIT_WAIT_TIMEOUT = 4
EXIT_LEADER_RUN_REQUIRED = 10
MODES = ("EditMode", "PlayMode")
POLL_SECONDS = 1.0
SEAL_QUIET_SECONDS = 20
SEAL_MAX_WAIT_SECONDS = 90
HEARTBEAT_SECONDS = 2.0
HEARTBEAT_STALE_SECONDS = 600
EXTERNAL_RUN_TTL_SECONDS = 2700
MAX_FAILURES_REPORTED = 20
MAX_MESSAGE_LENGTH = 500
RUNNER_SHARED_FILES = ("Packages/manifest.json", "Packages/packages-lock.json", "ProjectSettings/ProjectVersion.txt")
SCRIPT = Path(__file__).resolve()


class UsageError(Exception):
    """The request cannot be accepted as given."""


# --- Collection policy --------------------------------------------------------


def should_seal(pending_count: int, oldest_wait: float, quiet_for: float) -> bool:
    """Return True when the leader should stop collecting and start the batch.

    pending_count: requests waiting in the queue (at least 1).
    oldest_wait: seconds since the oldest waiting request was submitted.
    quiet_for: seconds since the newest waiting request was submitted.

    Waiting longer lets more sessions share one Unity launch, which costs
    roughly one to three minutes of Editor start-up and domain reload.
    Waiting less returns a lone request sooner.
    """
    # A short quiet period catches sessions that finish at about the same time;
    # the cap stops a steady trickle of requests from holding the first one back.
    return quiet_for >= SEAL_QUIET_SECONDS or oldest_wait >= SEAL_MAX_WAIT_SECONDS


# --- Files and state ------------------------------------------------------------


def state_root() -> Path:
    override = os.environ.get("UNITY_TEST_BATCH_HOME")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".cache")
    return Path(base) / "unity-test-batch"


def session_id() -> str:
    return os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("CODEX_SESSION_ID") or f"pid-{os.getppid()}"


def write_json(path: Path, data: dict) -> None:
    temporary = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
    for attempt in range(20):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            # Windows refuses to replace a file another process is reading.
            if attempt == 19:
                raise
            time.sleep(0.05)


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return None


def resolve_project(value: str) -> Path:
    project = Path(value).resolve()
    if not (project / "ProjectSettings").is_dir():
        raise UsageError(f"{project} is not a Unity project root (no ProjectSettings/).")
    return project


def relative_path(project: Path, file: str) -> str:
    path = Path(file)
    if path.is_absolute():
        try:
            path = Path(os.path.abspath(path)).relative_to(project)
        except ValueError:
            raise UsageError(f"{file} is outside the project {project}.") from None
    return path.as_posix()


def files_digest(project: Path, files: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(set(files)):
        path = project / relative
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(path.read_bytes() if path.is_file() else b"<missing>")
        digest.update(b"\0")
    return f"files-sha256:{digest.hexdigest()}"


class Queue:
    """The shared state of one Unity project: queue, results, batches, leader claim."""

    def __init__(self, project: Path):
        self.project = project
        key = hashlib.sha256(os.path.normcase(str(project)).encode("utf-8")).hexdigest()[:16]
        self.root = state_root() / key
        self.requests = self.root / "queue"
        self.results = self.root / "results"
        self.batches = self.root / "batches"
        self.claim_path = self.root / "leader.claim"
        for folder in (self.requests, self.results, self.batches):
            folder.mkdir(parents=True, exist_ok=True)

    def pending(self) -> list[Path]:
        return sorted(self.requests.glob("*.json"))

    def result_path(self, request_id: str) -> Path:
        return self.results / f"{request_id}.json"


# --- Leader claim ---------------------------------------------------------------


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5  # ERROR_ACCESS_DENIED: it exists
        try:
            code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def claim_is_stale(record: dict, now: float) -> bool:
    external_until = record.get("external_until")
    if external_until:
        return now > external_until
    if record.get("host") == socket.gethostname() and not process_alive(int(record.get("pid", 0))):
        return True
    return now - float(record.get("heartbeat", 0)) > HEARTBEAT_STALE_SECONDS


class LeaderClaim:
    """One leader per project. The claim file is created atomically; its heartbeat proves liveness."""

    def __init__(self, queue: Queue):
        self.queue = queue
        self.path = queue.claim_path
        self.record: dict | None = None

    def try_acquire(self) -> bool:
        current = read_json(self.path)
        if current is not None and claim_is_stale(current, time.time()):
            self._recover(current)
        record = {
            "token": uuid.uuid4().hex,
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "session": session_id(),
            "heartbeat": time.time(),
            "external_until": None,
            "batch": None,
        }
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(record, handle)
        self.record = record
        return True

    def _recover(self, stale: dict) -> None:
        """Move a stale claim aside, but only the exact stale claim that was read."""
        audit = self.path.with_name(f"leader.claim.stale-{int(time.time())}-{stale.get('token', 'unknown')[:8]}")
        if (read_json(self.path) or {}).get("token") != stale.get("token"):
            return
        try:
            os.rename(self.path, audit)
        except (FileNotFoundError, FileExistsError, PermissionError):
            return
        moved = read_json(audit) or {}
        if moved.get("token") != stale.get("token"):
            # A fresh claim was created between the check and the rename: give it back.
            try:
                os.rename(audit, self.path)
            except OSError:
                pass

    def heartbeat(self, **changes: object) -> None:
        if self.record is None:
            return
        self.record.update(changes, heartbeat=time.time())
        write_json(self.path, self.record)

    def release(self) -> None:
        if self.record is None:
            return
        if (read_json(self.path) or {}).get("token") == self.record["token"]:
            self.path.unlink(missing_ok=True)
        self.record = None


# --- Filters and results ------------------------------------------------------


def split_filters(value: str | None) -> list[str]:
    filters = [item.strip() for item in (value or "").split(";") if item.strip()]
    if any(item.startswith("!") for item in filters):
        raise UsageError("A shared batch cannot carry '!' exclusions: they would hide other sessions' tests. Name the wanted tests.")
    return filters


def merge_filters(requests: list[dict]) -> list[str] | None:
    """Return the merged Unity filter, or None when one request needs the whole platform."""
    merged: list[str] = []
    for request in requests:
        if not request["filters"]:
            return None
        for item in request["filters"]:
            if item not in merged:
                merged.append(item)
    return merged


def filter_matches(pattern: str, full_name: str) -> bool:
    """Mirror Unity's -testFilter: an exact or parent full name, or a regular expression searched in the full name."""
    if full_name == pattern or full_name.startswith(pattern + ".") or full_name.startswith(pattern + "("):
        return True
    try:
        return re.search(pattern, full_name) is not None
    except re.error:
        return pattern in full_name


def select_cases(cases: list[dict], filters: list[str]) -> list[dict]:
    if not filters:
        return cases
    return [case for case in cases if any(filter_matches(pattern, case["fullname"]) for pattern in filters)]


def normalize_outcome(value: str) -> str:
    lowered = value.lower()
    if "pass" in lowered or lowered == "success":
        return "Passed"
    if "fail" in lowered or "error" in lowered:
        return "Failed"
    if "inconclusive" in lowered:
        return "Inconclusive"
    return "Skipped"


def parse_results(path: Path) -> list[dict]:
    """Read an NUnit3 XML report, or a JSON list of {fullname, result, message} from a live-Editor run."""
    text = path.read_text(encoding="utf-8-sig")
    if text.lstrip().startswith("<"):
        cases = []
        for case in ElementTree.fromstring(text).iter("test-case"):
            message = (case.findtext("failure/message") or "").strip()
            cases.append(
                {"fullname": case.get("fullname", ""), "result": normalize_outcome(case.get("result", "")), "message": message}
            )
        return cases
    data = json.loads(text)
    items = data if isinstance(data, list) else data.get("tests") or data.get("results") or []
    cases = []
    for item in items:
        name = item.get("fullname") or item.get("fullName") or item.get("full_name") or item.get("name") or ""
        outcome = item.get("result") or item.get("state") or item.get("outcome") or item.get("status") or ""
        cases.append({"fullname": name, "result": normalize_outcome(str(outcome)), "message": str(item.get("message") or "")})
    return cases


def classify(selected: list[dict]) -> str:
    """Zero matched tests is NO_TESTS, never PASS: Unity reports an empty filter match as passed."""
    if any(case["result"] == "Failed" for case in selected):
        return "FAIL"
    if not any(case["result"] == "Passed" for case in selected):
        return "NO_TESTS"
    return "PASS"


def outcome_record(request: dict, status: str, **fields: object) -> dict:
    record = {
        "request": request["id"],
        "task": request.get("task"),
        "mode": request["mode"],
        "filters": request["filters"],
        "digest": request["digest"],
        "status": status,
        "matched": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "inconclusive": 0,
        "failures": [],
        "detail": "",
        "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    record.update(fields)
    return record


def cases_record(request: dict, cases: list[dict], **fields: object) -> dict:
    selected = select_cases(cases, request["filters"])
    failures = [
        {"fullname": case["fullname"], "message": case["message"][:MAX_MESSAGE_LENGTH]}
        for case in selected
        if case["result"] == "Failed"
    ]
    return outcome_record(
        request,
        classify(selected),
        matched=len(selected),
        passed=sum(1 for case in selected if case["result"] == "Passed"),
        failed=len(failures),
        skipped=sum(1 for case in selected if case["result"] == "Skipped"),
        inconclusive=sum(1 for case in selected if case["result"] == "Inconclusive"),
        failures=failures[:MAX_FAILURES_REPORTED],
        **fields,
    )


# --- Gates ------------------------------------------------------------------------


def dirty_csharp_files(project: Path) -> list[str]:
    """Uncommitted C# files of every session in a Git working tree; empty outside Git."""
    if shutil.which("git") is None:
        return []
    completed = subprocess.run(
        ["git", "-C", str(project), "status", "--porcelain", "-z", "--untracked-files=all", "--", "*.cs"],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return []
    top = subprocess.run(["git", "-C", str(project), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    root = Path(top.stdout.strip()).resolve()
    entries = completed.stdout.split("\0")
    files = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if len(entry) < 4:
            continue
        if entry[0] in "RC":
            index += 1  # -z prints a rename's source path as the next entry
        try:
            files.append(Path(os.path.abspath(root / entry[3:])).relative_to(project).as_posix())
        except ValueError:
            continue
    return files


def roslyn_gate(project: Path, requests: list[dict]) -> tuple[str, str, list[str]]:
    """Compile every requested and every dirty C# file once before a Unity launch is spent.

    Returns the verdict, the compile output, and the dirty files no request declared.
    """
    requested = {file for request in requests for file in request["files"]}
    unrequested = sorted(set(dirty_csharp_files(project)) - requested)
    csharp = [file for file in sorted(requested | set(unrequested)) if file.lower().endswith(".cs")]
    if not csharp:
        return "COMPILE_OK", "no C# changes to compile", unrequested
    check = os.environ.get("UNITY_TEST_BATCH_COMPILE_CHECK") or str(SCRIPT.with_name("unity_compile_check.py"))
    completed = subprocess.run(
        [sys.executable, check, "--project", str(project), "--dependents", "--files", *csharp],
        capture_output=True,
        text=True,
    )
    verdicts = {0: "COMPILE_OK", 1: "COMPILE_ERRORS"}
    return verdicts.get(completed.returncode, "COMPILE_UNVERIFIED"), completed.stdout[-6000:], unrequested


def mentions_any(files: list[str], compile_output: str) -> bool:
    text = compile_output.replace("\\", "/").lower()
    return any(file.lower() in text for file in files)


def compile_statuses(requests: list[dict], compile_output: str, unrequested: list[str]) -> dict[str, str]:
    """Blame the sessions whose files hold the errors; the others are blocked, not failed.

    Errors only in another session's undeclared dirty files block everyone. Errors in
    files nobody touched (a caller of a changed API) cannot be attributed, so every
    request gets COMPILE_ERRORS and each session inspects the output.
    """
    owners = {request["id"] for request in requests if mentions_any(request["files"], compile_output)}
    if not owners and not mentions_any(unrequested, compile_output):
        owners = {request["id"] for request in requests}
    return {request["id"]: "COMPILE_ERRORS" if request["id"] in owners else "BLOCKED_BY_OTHER_COMPILE" for request in requests}


def project_locked(project: Path) -> bool:
    """True when a Unity Editor holds the project, so batch mode cannot open it."""
    lockfile = project / "Temp" / "UnityLockfile"
    if not lockfile.exists():
        return False
    try:
        handle = open(lockfile, "a")
    except PermissionError:
        return True
    with handle:
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.lockf(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.lockf(handle, fcntl.LOCK_UN)
        except OSError:
            return True
    return False


def choose_runner(project: Path, requests: list[dict]) -> tuple[Path, str]:
    """Use an agreed shadow runner project (same Assets, own Library) or the project itself."""
    runners = {request["runner_project"] for request in requests if request.get("runner_project")}
    if len(runners) != 1:
        return project, "" if not runners else "requests disagree on --runner-project; using the project itself"
    runner = Path(runners.pop())
    if (runner / "Assets").resolve() != (project / "Assets").resolve():
        return project, f"runner {runner} does not share this project's Assets; using the project itself"
    for relative in RUNNER_SHARED_FILES:
        source, copy = project / relative, runner / relative
        if source.is_file() != copy.is_file() or (source.is_file() and source.read_bytes() != copy.read_bytes()):
            return project, f"runner {runner} differs in {relative}; using the project itself"
    return runner, ""


# --- Leader ----------------------------------------------------------------------


def requeue_orphans(queue: Queue) -> None:
    """Return requests of a batch whose leader died to the queue."""
    for batch in queue.batches.iterdir():
        if not batch.is_dir() or (batch / "done.json").exists() or (batch / "abandoned.json").exists():
            continue
        for request in (batch / "requests").glob("*.json"):
            if not queue.result_path(request.stem).exists():
                os.replace(request, queue.requests / request.name)
        write_json(batch / "abandoned.json", {"at": time.time()})


def collect(queue: Queue, claim: LeaderClaim) -> list[Path]:
    while True:
        pending = queue.pending()
        if not pending:
            return []
        created = [float((read_json(path) or {}).get("created", time.time())) for path in pending]
        now = time.time()
        if should_seal(len(pending), now - min(created), now - max(created)):
            return pending
        claim.heartbeat()
        time.sleep(POLL_SECONDS)


def seal(queue: Queue, pending: list[Path]) -> tuple[Path, list[dict]]:
    batch = queue.batches / f"{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    (batch / "requests").mkdir(parents=True)
    sealed = []
    for path in pending:
        target = batch / "requests" / path.name
        try:
            os.replace(path, target)
        except FileNotFoundError:
            continue  # withdrawn after a wait timeout
        request = read_json(target)
        if request:
            sealed.append(request)
    sealed.sort(key=lambda request: request["created"])
    return batch, sealed


def run_unity(unity: str, runner: Path, mode: str, filters: list[str] | None, report: Path, log: Path,
              timeout: int, claim: LeaderClaim) -> int:
    command = [unity, "test", str(runner), "--mode", mode, "--output", str(report), "--format", "json",
               "--non-interactive", "--no-banner", "--timeout", str(timeout)]
    if filters:
        command += ["--filter", ";".join(filters)]
    with open(log, "w", encoding="utf-8") as output:
        output.write(" ".join(command) + "\n")
        output.flush()
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
        while process.poll() is None:
            claim.heartbeat()
            time.sleep(HEARTBEAT_SECONDS)
    return process.returncode


def run_batch(queue: Queue, claim: LeaderClaim, batch: Path, requests: list[dict], options: argparse.Namespace) -> Path | None:
    """Run one sealed batch. Return the plan path when a live Editor must run it."""
    project = queue.project
    shared = {"batch": batch.name, "batch_requests": len(requests)}
    live = []
    for request in requests:
        if files_digest(project, request["files"]) != request["digest"]:
            write_json(queue.result_path(request["id"]), outcome_record(request, "STALE", detail="files changed after submit", **shared))
        else:
            live.append(request)
    verdict, compile_output, unrequested = roslyn_gate(project, live) if live else ("COMPILE_OK", "", [])
    (batch / "roslyn.txt").write_text(f"{verdict}\n{compile_output}", encoding="utf-8")
    if verdict == "COMPILE_ERRORS":
        statuses = compile_statuses(live, compile_output, unrequested)
        for request in live:
            record = outcome_record(request, statuses[request["id"]], detail=compile_output, roslyn=verdict, **shared)
            write_json(queue.result_path(request["id"]), record)
        live = []
    runner, runner_note = choose_runner(project, live)
    runs = [(mode, [request for request in live if request["mode"] == mode]) for mode in MODES]
    runs = [(mode, group) for mode, group in runs if group]
    if runs and project_locked(runner):
        plan = {
            "batch": batch.name,
            "project": str(project),
            "runner": str(runner),
            "roslyn": verdict,
            "runs": [
                {"mode": mode, "filter": ";".join(merge_filters(group) or []) or None,
                 "requests": [request["id"] for request in group], "publish": publish_command(project, batch.name, mode)}
                for mode, group in runs
            ],
        }
        write_json(batch / "plan.json", plan)
        claim.heartbeat(external_until=time.time() + EXTERNAL_RUN_TTL_SECONDS, batch=batch.name)
        return batch / "plan.json"
    unity = shutil.which(options.unity_bin) or ""
    for mode, group in runs:
        report, log = batch / f"{mode}.xml", batch / f"{mode}.log"
        fields = dict(shared, runner=str(runner), report=str(report), log=str(log), unity_runs=len(runs), roslyn=verdict)
        if not unity:
            code = -1
            log.write_text(f"unity CLI '{options.unity_bin}' not found on PATH\n", encoding="utf-8")
        else:
            code = run_unity(unity, runner, mode, merge_filters(group), report, log, options.timeout, claim)
        cases = parse_results(report) if code in (0, 8) and report.is_file() else None
        for request in group:
            if cases is None:
                record = outcome_record(request, "INFRA_ERROR", detail=f"unity test exited {code} without a report; see log. {runner_note}".strip(), **fields)
            elif files_digest(project, request["files"]) != request["digest"]:
                record = outcome_record(request, "STALE", detail="files changed during the run", **fields)
            else:
                record = cases_record(request, cases, detail=runner_note, **fields)
            write_json(queue.result_path(request["id"]), record)
    write_json(batch / "done.json", {"at": time.time(), "unity_runs": len(runs)})
    return None


def publish_command(project: Path, batch: str, mode: str) -> str:
    return f'python "{SCRIPT}" publish --project "{project}" --batch {batch} --mode {mode} --results <report.xml|results.json>'


def lead(queue: Queue, claim: LeaderClaim, options: argparse.Namespace) -> Path | None:
    """Run one batch as leader. Release the claim unless a live Editor must run the plan."""
    plan = None
    try:
        requeue_orphans(queue)
        pending = collect(queue, claim)
        if pending:
            batch, requests = seal(queue, pending)
            plan = run_batch(queue, claim, batch, requests, options)
        return plan
    finally:
        if plan is None:
            claim.release()


# --- Commands ---------------------------------------------------------------------


def print_result(queue: Queue, result: dict) -> int:
    print(
        f"TEST_BATCH: {result['status']} ({result['passed']}/{result['matched']}) request={result['request']} "
        f"mode={result['mode']} batch={result.get('batch')} shared_requests={result.get('batch_requests', 1)} "
        f"unity_runs={result.get('unity_runs', 0)}"
    )
    for failure in result["failures"]:
        print(f"  FAILED {failure['fullname']}: {failure['message']}")
    if result.get("detail"):
        print(f"  detail: {result['detail'][-2000:]}")
    print(f"  result: {queue.result_path(result['request'])}")
    if result.get("report"):
        print(f"  report: {result['report']}  log: {result.get('log')}")
    return EXIT_CODES[result["status"]]


def print_plan(plan_path: Path) -> None:
    plan = read_json(plan_path) or {}
    print(f"LEADER_RUN_REQUIRED plan={plan_path}")
    print(f"  The project is open in an Editor. Run each line through the live Editor ({plan.get('runner')}),")
    print("  save the report, then publish it. Other sessions keep waiting for these results.")
    for run in plan.get("runs", []):
        print(f"  {run['mode']}: filter={run['filter'] or '<whole platform>'} requests={len(run['requests'])}")
        print(f"    then: {run['publish']}")


def wait_for(queue: Queue, request_id: str, options: argparse.Namespace) -> int:
    deadline = time.time() + options.wait_limit
    while True:
        result = read_json(queue.result_path(request_id))
        if result:
            return print_result(queue, result)
        claim = LeaderClaim(queue)
        if claim.try_acquire():
            plan = lead(queue, claim, options)
            if plan is not None:
                print_plan(plan)
                return EXIT_LEADER_RUN_REQUIRED
            continue
        if time.time() > deadline:
            try:
                (queue.requests / f"{request_id}.json").unlink()
                print(f"WAIT_TIMEOUT request={request_id} withdrawn from the queue")
            except FileNotFoundError:
                print(f"WAIT_TIMEOUT request={request_id} is in a running batch; resume with: wait --project ... --id {request_id}")
            return EXIT_WAIT_TIMEOUT
        time.sleep(POLL_SECONDS)


def command_submit(options: argparse.Namespace) -> int:
    project = resolve_project(options.project)
    queue = Queue(project)
    files = [relative_path(project, file) for file in options.files]
    runner = str(Path(options.runner_project).resolve()) if options.runner_project else None
    request = {
        "id": uuid.uuid4().hex[:12],
        "task": options.task,
        "session": session_id(),
        "mode": options.mode,
        "filters": split_filters(options.filter),
        "files": files,
        "digest": files_digest(project, files),
        "runner_project": runner,
        "created": time.time(),
    }
    write_json(queue.requests / f"{request['id']}.json", request)
    print(f"TEST_BATCH_REQUEST: {request['id']} project={project} mode={options.mode} digest={request['digest']}")
    sys.stdout.flush()
    return wait_for(queue, request["id"], options)


def command_wait(options: argparse.Namespace) -> int:
    return wait_for(Queue(resolve_project(options.project)), options.id, options)


def command_publish(options: argparse.Namespace) -> int:
    queue = Queue(resolve_project(options.project))
    batch = queue.batches / options.batch
    plan = read_json(batch / "plan.json")
    claim = read_json(queue.claim_path) or {}
    if plan is None or (batch / "abandoned.json").exists() or claim.get("batch") != options.batch:
        raise UsageError(f"Batch {options.batch} is not waiting for a live-Editor run.")
    run = next((item for item in plan["runs"] if item["mode"] == options.mode), None)
    if run is None:
        raise UsageError(f"Batch {options.batch} has no {options.mode} run.")
    cases = parse_results(Path(options.results))
    fields = {"batch": options.batch, "batch_requests": sum(len(item["requests"]) for item in plan["runs"]),
              "runner": plan["runner"], "report": str(Path(options.results).resolve()), "unity_runs": len(plan["runs"]),
              "roslyn": plan.get("roslyn")}
    exit_code = 0
    for request_id in run["requests"]:
        request = read_json(batch / "requests" / f"{request_id}.json")
        if request is None:
            continue
        if files_digest(queue.project, request["files"]) != request["digest"]:
            record = outcome_record(request, "STALE", detail="files changed during the live-Editor run", **fields)
        else:
            record = cases_record(request, cases, **fields)
        write_json(queue.result_path(request_id), record)
        exit_code = max(exit_code, print_result(queue, record))
    write_json(batch / f"published-{options.mode}.json", {"at": time.time()})
    if all((batch / f"published-{item['mode']}.json").exists() for item in plan["runs"]):
        write_json(batch / "done.json", {"at": time.time(), "unity_runs": len(plan["runs"])})
        if (read_json(queue.claim_path) or {}).get("batch") == options.batch:
            queue.claim_path.unlink(missing_ok=True)
    return exit_code


def command_status(options: argparse.Namespace) -> int:
    queue = Queue(resolve_project(options.project))
    claim = read_json(queue.claim_path)
    print(f"state: {queue.root}")
    print(f"pending requests: {len(queue.pending())}")
    print(f"leader: {json.dumps(claim) if claim else 'none'}")
    for batch in sorted(queue.batches.iterdir())[-5:]:
        state = "done" if (batch / "done.json").exists() else "abandoned" if (batch / "abandoned.json").exists() else "running"
        print(f"batch {batch.name}: {state}, {len(list((batch / 'requests').glob('*.json')))} request(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Shared final-stage Unity test runs for several agent sessions.")
    commands = parser.add_subparsers(dest="command", required=True)

    submit = commands.add_parser("submit", help="Queue this session's tests and wait for their result.")
    submit.add_argument("--project", required=True, help="Unity project root (the folder that holds ProjectSettings/).")
    submit.add_argument("--mode", required=True, choices=MODES)
    submit.add_argument("--filter", help="Unity test filter: full names or regular expressions, ';'-separated. Omit for the whole platform.")
    submit.add_argument("--files", nargs="+", required=True, help="Changed files the result must prove, including test files. Deleted files too.")
    submit.add_argument("--task", help="Tracked task ID, recorded in the result.")
    submit.add_argument("--runner-project", help="Shadow project that shares this project's Assets, used while the Editor is open.")
    wait = commands.add_parser("wait", help="Resume waiting for a submitted request.")
    wait.add_argument("--project", required=True)
    wait.add_argument("--id", required=True)
    for command in (submit, wait):
        command.add_argument("--wait-limit", type=int, default=3600, help="Seconds to wait for the result (default 3600).")
        command.add_argument("--timeout", type=int, default=1800, help="Seconds before a Unity run is killed (default 1800).")
        command.add_argument("--unity-bin", default="unity", help="Unity CLI executable (default: unity on PATH).")

    publish = commands.add_parser("publish", help="Hand a live-Editor run's report to every request in the batch.")
    publish.add_argument("--project", required=True)
    publish.add_argument("--batch", required=True)
    publish.add_argument("--mode", required=True, choices=MODES)
    publish.add_argument("--results", required=True, help="NUnit3 XML report, or a JSON list of {fullname, result, message}.")

    status = commands.add_parser("status", help="Show the queue, the leader, and recent batches.")
    status.add_argument("--project", required=True)

    arguments = parser.parse_args(argv)
    handlers = {"submit": command_submit, "wait": command_wait, "publish": command_publish, "status": command_status}
    try:
        return handlers[arguments.command](arguments)
    except UsageError as error:
        print(f"USAGE: {error}")
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
