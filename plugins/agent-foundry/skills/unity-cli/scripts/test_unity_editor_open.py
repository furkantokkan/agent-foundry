"""Tests for unity_editor_open.py. Run: python test_unity_editor_open.py"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "unity_editor_open.py"
SPEC = importlib.util.spec_from_file_location("unity_editor_open", SCRIPT)
opener = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(opener)

# Appends a new Editor process for the opened project, like a real `unity open`.
FAKE_UNITY = textwrap.dedent(
    """
    import json, os, sys, time
    rows_path = os.environ["UNITY_EDITOR_OPEN_PROCESSES"]
    with open(os.environ["FAKE_UNITY_CALLS"], "a", encoding="utf-8") as log:
        log.write(json.dumps(sys.argv[1:]) + "\\n")
    if os.environ.get("FAKE_UNITY_FAIL"):
        sys.exit(1)
    time.sleep(float(os.environ.get("FAKE_UNITY_DELAY", "0")))
    project = sys.argv[sys.argv.index("open") + 1]
    rows = json.load(open(rows_path, encoding="utf-8"))
    rows.append({"pid": os.getpid(), "command": f'"C:/Unity/Editor/Unity.exe" -projectpath {project} -useHub -hubIPC'})
    with open(rows_path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle)
    """
)

HOLD_LOCK = textwrap.dedent(
    """
    import importlib.util, sys, time
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("unity_editor_open", sys.argv[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lock = module.RepositoryLock(Path(sys.argv[2]))
    print("locked" if lock.try_acquire() else "busy", flush=True)
    time.sleep(60)
    """
)


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


def editor_row(pid: int, project: Path, extra: str = "-useHub -hubIPC") -> dict:
    return {"pid": pid, "command": f'"C:/Unity/Editor/Unity.exe" -projectpath {project} {extra}'}


def unity_project(root: Path) -> Path:
    (root / "ProjectSettings").mkdir(parents=True)
    (root / "ProjectSettings" / "ProjectVersion.txt").write_text("m_EditorVersion: 6000.3.8f1\n")
    return root


class ParsingTests(unittest.TestCase):
    def test_project_of_reads_hub_batch_quoted_and_equals_launches(self) -> None:
        hub = r'"C:\Unity\Editor\Unity.exe" -projectpath C:\Repos\SM Launcher -acceptSoftwareTermsForThisRunOnly -useHub'
        batch = r'"C:\Unity\Editor\Unity.exe" -batchmode -runTests -projectPath C:\Repos\Coin -testResults C:\out.xml'
        quoted = r'"C:\Unity\Editor\Unity.exe" "-projectPath" "C:/Repos/BRN Game" "-logFile" "Logs/x.log"'
        equals = r'"C:\Unity\Editor\Unity.exe" -projectPath=C:\Repos\Çalışma\Game -logFile x.log'
        double = r'"C:\Unity\Editor\Unity.exe" --projectPath=C:\Repos\Other -logFile x.log'
        self.assertEqual(opener.project_of(double), opener.normalize(r"C:\Repos\Other"))
        last = r'/Applications/Unity/Unity.app/Contents/MacOS/Unity -projectPath /Users/me/Game'
        self.assertEqual(opener.project_of(hub), opener.normalize(r"C:\Repos\SM Launcher"))
        self.assertEqual(opener.project_of(batch), opener.normalize(r"C:\Repos\Coin"))
        self.assertEqual(opener.project_of(quoted), opener.normalize("C:/Repos/BRN Game"))
        self.assertEqual(opener.project_of(equals), opener.normalize(r"C:\Repos\Çalışma\Game"))
        self.assertEqual(opener.project_of(last), opener.normalize("/Users/me/Game"))

    def test_project_of_ignores_workers_hub_and_cli(self) -> None:
        worker = r'"C:\Unity\Editor\Unity.exe" "-adb2" "-batchMode" "-name" "AssetImportWorker4" "-projectPath" "C:/Repos/Coin"'
        bare_worker = r'"C:\Unity\Editor\Unity.exe" -batchMode -name AssetImportWorker0 -projectPath C:\Repos\Coin'
        hub = r'"C:\Program Files\Unity Hub\resources\unity.exe" serve'
        cli = r"C:\Tools\Unity\bin\unity.EXE test C:\Repos\Coin --mode PlayMode"
        for command in (worker, bare_worker, hub, cli, ""):
            self.assertIsNone(opener.project_of(command), command)

    def test_editor_whose_path_mentions_import_workers_still_counts(self) -> None:
        editor = r'"C:\Unity\Editor\Unity.exe" -projectpath C:\Repos\AssetImportWorkerTools\Game -useHub -hubIPC'
        self.assertEqual(opener.project_of(editor), opener.normalize(r"C:\Repos\AssetImportWorkerTools\Game"))

    def test_inside_respects_path_boundaries(self) -> None:
        root = opener.normalize("C:/Repos/game")
        self.assertTrue(opener.inside(opener.normalize("C:/Repos/game/unity/Game"), root))
        self.assertTrue(opener.inside(root, root))
        self.assertFalse(opener.inside(opener.normalize("C:/Repos/game-wt/unity/Game"), root))

    def test_failed_process_table_read_is_an_error_not_an_empty_table(self) -> None:
        failure = subprocess.CompletedProcess([], 1, stdout="", stderr="Access denied")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("UNITY_EDITOR_OPEN_PROCESSES", None)
            with mock.patch.object(opener.subprocess, "run", return_value=failure):
                with self.assertRaises(opener.ScanError):
                    opener.process_rows()


class OpenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name).resolve()
        # A non-ASCII name with a space exercises git and process-table decoding end to end.
        self.repo = base / "Çalışma repo"
        self.project = unity_project(self.repo / "unity" / "Game")
        git("init", "-q", cwd=self.repo)
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", "init", cwd=self.repo)
        self.lane = base / "Çalışma repo-wt"
        git("worktree", "add", "-q", "-b", "lane", str(self.lane), cwd=self.repo)
        self.lane_project = self.lane / "unity" / "Game"
        self.other = base / "other" / "Game"
        self.rows = base / "processes.json"
        self.calls = base / "calls.log"
        self.calls.write_text("")
        self.fake = base / "fake_unity.py"
        self.fake.write_text(FAKE_UNITY, encoding="utf-8")
        self.environ = {
            "UNITY_EDITOR_OPEN_PROCESSES": str(self.rows),
            "UNITY_EDITOR_OPEN_CLI": json.dumps([sys.executable, str(self.fake)]),
            "FAKE_UNITY_CALLS": str(self.calls),
        }
        self.environment = mock.patch.dict(os.environ, self.environ)
        self.environment.start()
        self.poll = mock.patch.object(opener, "POLL_SECONDS", 0.05)
        self.poll.start()

    def tearDown(self) -> None:
        self.poll.stop()
        self.environment.stop()
        self.temp.cleanup()

    def set_editors(self, *rows: dict) -> None:
        self.rows.write_text(json.dumps(list(rows)), encoding="utf-8")

    def run_main(self, *args: str, project: Path | None = None) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = opener.main(["--project", str(project or self.project), *args])
        return code, output.getvalue()

    def cli_calls(self) -> list[str]:
        return [line for line in self.calls.read_text(encoding="utf-8").splitlines() if line]

    def test_limit_counts_editors_in_every_worktree_but_not_other_repositories(self) -> None:
        self.set_editors(editor_row(11, self.lane_project), editor_row(12, self.other))
        code, output = self.run_main("--limit", "1")
        self.assertEqual(code, opener.EXIT_LIMIT_REACHED, output)
        self.assertIn("editors=1/1", output)
        self.assertNotIn("pid=12", output)
        self.assertEqual(self.cli_calls(), [])

    def test_existing_editor_for_the_project_is_reported_not_reopened(self) -> None:
        self.set_editors(editor_row(21, self.project))
        code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_ALREADY_OPEN, output)
        self.assertIn("pid=21", output)
        self.assertNotIn("batch run", output)
        self.assertEqual(self.cli_calls(), [])

    def test_batch_run_on_the_project_is_reported_as_transient(self) -> None:
        self.set_editors(editor_row(22, self.project, "-batchmode -runTests -testResults out.xml"))
        code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_ALREADY_OPEN, output)
        self.assertIn("batch run", output)

    def test_dry_run_reports_room_without_opening(self) -> None:
        self.set_editors(editor_row(31, self.other))
        code, output = self.run_main("--dry-run")
        self.assertEqual(code, opener.EXIT_OPENED, output)
        self.assertIn("WOULD_OPEN", output)
        self.assertIn("editors=0/2", output)
        self.assertEqual(self.cli_calls(), [])

    def test_opens_and_reports_the_new_editor_pid(self) -> None:
        self.set_editors(editor_row(41, self.lane_project))
        code, output = self.run_main("--detect-seconds", "20")
        self.assertEqual(code, opener.EXIT_OPENED, output)
        self.assertRegex(output, r"OPENED pid=\d+ ")
        self.assertIn("editors=2/2", output)
        self.assertEqual(len(self.cli_calls()), 1)

    def test_failed_open_is_reported(self) -> None:
        self.set_editors()
        with mock.patch.dict(os.environ, {"FAKE_UNITY_FAIL": "1"}):
            code, output = self.run_main("--detect-seconds", "20")
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("exited 1", output)
        self.assertIn("never open twice", output)

    def test_unstartable_cli_is_a_verdict_not_a_traceback(self) -> None:
        self.set_editors()
        missing = str(Path(self.temp.name) / "missing" / "unity.exe")
        with mock.patch.dict(os.environ, {"UNITY_EDITOR_OPEN_CLI": json.dumps([missing])}):
            code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("cannot start `unity open`", output)

    def test_unreadable_process_table_opens_nothing(self) -> None:
        with mock.patch.object(opener, "process_rows", side_effect=opener.ScanError("WMI unavailable")):
            code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("cannot count the running Editors", output)
        self.assertEqual(self.cli_calls(), [])

    def test_git_failure_inside_a_repository_opens_nothing(self) -> None:
        dubious = subprocess.CompletedProcess([], 128, stdout="", stderr="fatal: detected dubious ownership in repository")
        self.set_editors()
        with mock.patch.object(opener, "run_text", return_value=dubious):
            code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("dubious ownership", output)
        self.assertEqual(self.cli_calls(), [])

    def test_project_outside_git_uses_its_own_scope(self) -> None:
        loose = unity_project(Path(self.temp.name).resolve() / "loose" / "Game")
        if opener.inside_git_repository(loose):
            self.skipTest("the temp folder is inside a Git repository on this machine")
        self.set_editors(editor_row(51, self.project))
        code, output = self.run_main("--dry-run", project=loose)
        self.assertEqual(code, opener.EXIT_OPENED, output)
        self.assertIn("editors=0/2", output)

    def test_lock_is_shared_by_worktrees_and_dropped_with_its_process(self) -> None:
        self.set_editors()
        _, lock_dir = opener.repository_scope(self.lane_project)
        self.assertEqual(lock_dir, opener.repository_scope(self.project)[1])
        holder = subprocess.Popen([sys.executable, "-c", HOLD_LOCK, str(SCRIPT), str(lock_dir)],
                                  stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(holder.stdout.readline().strip(), "locked")
            code, output = self.run_main("--dry-run", "--wait-seconds", "0.5")
            self.assertEqual(code, opener.EXIT_LOCK_TIMEOUT, output)
        finally:
            holder.kill()
            holder.wait()
            holder.stdout.close()
        code, output = self.run_main("--dry-run", "--wait-seconds", "5")
        self.assertEqual(code, opener.EXIT_OPENED, output)

    def test_concurrent_opens_from_two_processes_respect_the_limit(self) -> None:
        self.set_editors()
        environment = {**os.environ, **self.environ, "FAKE_UNITY_DELAY": "0.5", "PYTHONUTF8": "1"}
        runs = [
            subprocess.Popen([sys.executable, str(SCRIPT), "--project", str(project), "--limit", "1", "--detect-seconds", "30"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment, encoding="utf-8")
            for project in (self.project, self.lane_project)
        ]
        results = [(run.wait(timeout=120), run.stdout.read()) for run in runs]
        for run in runs:
            run.stdout.close()
        codes = sorted(code for code, _ in results)
        self.assertEqual(codes, [opener.EXIT_OPENED, opener.EXIT_LIMIT_REACHED], results)
        self.assertEqual(len(self.cli_calls()), 1, results)
        self.assertEqual(len(json.loads(self.rows.read_text(encoding="utf-8"))), 1)
        self.assertTrue(any(re.search(r"LIMIT_REACHED editors=1/1", output) for _, output in results), results)

    def reservations(self) -> dict:
        lock_dir = opener.repository_scope(self.project)[1]
        path = lock_dir / opener.RESERVATIONS_NAME
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def test_slow_launch_keeps_its_slot_until_its_editor_appears(self) -> None:
        self.set_editors()
        with mock.patch.dict(os.environ, {"FAKE_UNITY_DELAY": "2"}):
            code, output = self.run_main("--detect-seconds", "0.3")
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("keeps its slot", output)
        code, output = self.run_main("--limit", "1", project=self.lane_project)
        self.assertEqual(code, opener.EXIT_LIMIT_REACHED, output)
        self.assertIn("starting", output)
        code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_ALREADY_OPEN, output)
        self.assertIn("still starting", output)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not json.loads(self.rows.read_text(encoding="utf-8")):
            time.sleep(0.1)
        code, output = self.run_main("--dry-run", project=self.lane_project)
        self.assertEqual(code, opener.EXIT_OPENED, output)
        self.assertIn("editors=1/2", output)
        self.assertEqual(self.reservations(), {})

    def test_old_reservation_keeps_its_slot_until_cleared(self) -> None:
        self.set_editors()
        lock_dir = opener.repository_scope(self.project)[1]
        old = {opener.normalize(self.lane_project): {"started": time.time() - opener.OLD_RESERVATION_SECONDS - 60}}
        opener.save_reservations(lock_dir, old)
        code, output = self.run_main("--dry-run", "--limit", "1")
        self.assertEqual(code, opener.EXIT_LIMIT_REACHED, output)
        self.assertIn("likely failed", output)
        self.assertIn("--clear-reservation", output)
        code, output = self.run_main("--clear-reservation", project=self.lane_project)
        self.assertEqual(code, opener.EXIT_OPENED, output)
        self.assertIn("RESERVATION_CLEARED", output)
        self.assertEqual(self.reservations(), {})
        code, output = self.run_main("--dry-run", "--limit", "1")
        self.assertEqual(code, opener.EXIT_OPENED, output)

    def test_clearing_without_a_reservation_changes_nothing(self) -> None:
        self.set_editors()
        code, output = self.run_main("--clear-reservation")
        self.assertEqual(code, opener.EXIT_OPENED, output)
        self.assertIn("NO_RESERVATION", output)

    def test_unity_process_without_a_readable_command_line_opens_nothing(self) -> None:
        self.set_editors({"pid": 77, "command": None})
        code, output = self.run_main()
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("no readable command line", output)
        self.assertEqual(self.cli_calls(), [])

    def test_failed_launch_gives_its_slot_back(self) -> None:
        self.set_editors()
        with mock.patch.dict(os.environ, {"FAKE_UNITY_FAIL": "1"}):
            code, output = self.run_main("--detect-seconds", "20")
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertEqual(self.reservations(), {})

    def test_rejects_a_folder_that_is_not_a_unity_project(self) -> None:
        code, output = self.run_main(project=self.repo)
        self.assertEqual(code, opener.EXIT_USAGE, output)


if __name__ == "__main__":
    unittest.main()
