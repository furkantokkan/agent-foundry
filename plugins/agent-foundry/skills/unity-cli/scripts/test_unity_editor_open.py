"""Tests for unity_editor_open.py. Run: python test_unity_editor_open.py"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("unity_editor_open", HERE / "unity_editor_open.py")
opener = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(opener)

# Appends a new Editor process for the opened project, like a real `unity open`.
FAKE_UNITY = textwrap.dedent(
    """
    import json, os, sys
    rows_path = os.environ["UNITY_EDITOR_OPEN_PROCESSES"]
    with open(os.environ["FAKE_UNITY_CALLS"], "a", encoding="utf-8") as log:
        log.write(json.dumps(sys.argv[1:]) + "\\n")
    if os.environ.get("FAKE_UNITY_FAIL"):
        sys.exit(1)
    project = sys.argv[sys.argv.index("open") + 1]
    rows = json.load(open(rows_path, encoding="utf-8"))
    rows.append({"pid": 4242, "command": f'"C:/Unity/Editor/Unity.exe" -projectpath {project} -useHub -hubIPC'})
    json.dump(rows, open(rows_path, "w", encoding="utf-8"))
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


def editor_row(pid: int, project: Path) -> dict:
    return {"pid": pid, "command": f'"C:/Unity/Editor/Unity.exe" -projectpath {project} -useHub -hubIPC'}


class ParsingTests(unittest.TestCase):
    def test_project_of_reads_hub_batch_and_quoted_launches(self) -> None:
        hub = r'"C:\Unity\Editor\Unity.exe" -projectpath C:\Repos\SM Launcher -acceptSoftwareTermsForThisRunOnly -useHub'
        batch = r'"C:\Unity\Editor\Unity.exe" -batchmode -runTests -projectPath C:\Repos\Coin -testResults C:\out.xml'
        quoted = r'"C:\Unity\Editor\Unity.exe" "-projectPath" "C:/Repos/BRN Game" "-logFile" "Logs/x.log"'
        last = r'/Applications/Unity/Unity.app/Contents/MacOS/Unity -projectPath /Users/me/Game'
        self.assertEqual(opener.project_of(hub), opener.normalize(r"C:\Repos\SM Launcher"))
        self.assertEqual(opener.project_of(batch), opener.normalize(r"C:\Repos\Coin"))
        self.assertEqual(opener.project_of(quoted), opener.normalize("C:/Repos/BRN Game"))
        self.assertEqual(opener.project_of(last), opener.normalize("/Users/me/Game"))

    def test_project_of_ignores_workers_hub_and_cli(self) -> None:
        worker = r'"C:\Unity\Editor\Unity.exe" "-adb2" "-batchMode" "-name" "AssetImportWorker4" "-projectPath" "C:/Repos/Coin"'
        hub = r'"C:\Program Files\Unity Hub\resources\unity.exe" serve'
        cli = r"C:\Tools\Unity\bin\unity.EXE test C:\Repos\Coin --mode PlayMode"
        for command in (worker, hub, cli, ""):
            self.assertIsNone(opener.project_of(command), command)

    def test_inside_respects_path_boundaries(self) -> None:
        root = opener.normalize("C:/Repos/game")
        self.assertTrue(opener.inside(opener.normalize("C:/Repos/game/unity/Game"), root))
        self.assertTrue(opener.inside(root, root))
        self.assertFalse(opener.inside(opener.normalize("C:/Repos/game-wt/unity/Game"), root))


class OpenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name).resolve()
        self.repo = base / "repo"
        self.project = self.repo / "unity" / "Game"
        (self.project / "ProjectSettings").mkdir(parents=True)
        (self.project / "ProjectSettings" / "ProjectVersion.txt").write_text("m_EditorVersion: 6000.3.8f1\n")
        git("init", "-q", cwd=self.repo)
        git("add", "-A", cwd=self.repo)
        git("commit", "-q", "-m", "init", cwd=self.repo)
        self.lane = base / "repo-wt"
        git("worktree", "add", "-q", "-b", "lane", str(self.lane), cwd=self.repo)
        self.lane_project = self.lane / "unity" / "Game"
        self.other = base / "other" / "Game"
        self.rows = base / "processes.json"
        self.calls = base / "calls.log"
        self.calls.write_text("")
        fake = base / "fake_unity.py"
        fake.write_text(FAKE_UNITY)
        self.environment = mock.patch.dict(os.environ, {
            "UNITY_EDITOR_OPEN_PROCESSES": str(self.rows),
            "UNITY_EDITOR_OPEN_CLI": json.dumps([sys.executable, str(fake)]),
            "FAKE_UNITY_CALLS": str(self.calls),
        })
        self.environment.start()
        self.poll = mock.patch.object(opener, "POLL_SECONDS", 0.05)
        self.poll.start()

    def tearDown(self) -> None:
        self.poll.stop()
        self.environment.stop()
        self.temp.cleanup()

    def set_editors(self, *rows: dict) -> None:
        self.rows.write_text(json.dumps(list(rows)))

    def run_main(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = opener.main(["--project", str(self.project), *args])
        return code, output.getvalue()

    def cli_calls(self) -> list[str]:
        return [line for line in self.calls.read_text().splitlines() if line]

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
        self.assertEqual(self.cli_calls(), [])

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
        self.assertIn("OPENED pid=4242", output)
        self.assertIn("editors=2/2", output)
        self.assertEqual(len(self.cli_calls()), 1)

    def test_failed_open_is_reported(self) -> None:
        self.set_editors()
        with mock.patch.dict(os.environ, {"FAKE_UNITY_FAIL": "1"}):
            code, output = self.run_main("--detect-seconds", "20")
        self.assertEqual(code, opener.EXIT_OPEN_FAILED, output)
        self.assertIn("exited 1", output)

    def test_lock_is_shared_by_worktrees_and_dropped_with_its_process(self) -> None:
        self.set_editors()
        _, lock_dir = opener.repository_scope(self.lane_project)
        self.assertEqual(lock_dir, opener.repository_scope(self.project)[1])
        holder = subprocess.Popen([sys.executable, "-c", HOLD_LOCK, str(HERE / "unity_editor_open.py"), str(lock_dir)],
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

    def test_rejects_a_folder_that_is_not_a_unity_project(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = opener.main(["--project", str(self.repo)])
        self.assertEqual(code, opener.EXIT_USAGE, output.getvalue())


if __name__ == "__main__":
    unittest.main()
