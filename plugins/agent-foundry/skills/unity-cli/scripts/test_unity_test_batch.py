"""Tests for unity_test_batch.py. Run: python test_unity_test_batch.py"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("unity_test_batch", HERE / "unity_test_batch.py")
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)

CASES = [
    {"fullname": "Game.Inventory.InventoryTests.Add_Stacks", "result": "Passed"},
    {"fullname": "Game.Inventory.InventoryTests.Remove_Underflows", "result": "Failed", "message": "Expected 1 but was 2"},
    {"fullname": "Game.Reward.RewardTests.Claim_Grants", "result": "Passed"},
    {"fullname": "Game.Reward.RewardTests.Claim_Twice(1,2)", "result": "Passed"},
]

FAKE_UNITY = textwrap.dedent(
    """
    import json, os, re, sys
    from xml.sax.saxutils import quoteattr
    args = sys.argv[1:]
    def value(flag):
        return args[args.index(flag) + 1] if flag in args else None
    with open(os.environ["FAKE_UNITY_CALLS"], "a", encoding="utf-8") as log:
        log.write(json.dumps(args) + "\\n")
    cases = json.load(open(os.environ["FAKE_UNITY_CASES"], encoding="utf-8"))
    patterns = (value("--filter") or "").split(";")
    if value("--filter"):
        cases = [c for c in cases if any(c["fullname"] == p or c["fullname"].startswith(p + ".") or re.search(p, c["fullname"]) for p in patterns)]
    rows = []
    for c in cases:
        failure = f"<failure><message><![CDATA[{c.get('message', '')}]]></message></failure>" if c["result"] == "Failed" else ""
        rows.append(f"<test-case fullname={quoteattr(c['fullname'])} result={quoteattr(c['result'])}>{failure}</test-case>")
    with open(value("--output"), "w", encoding="utf-8") as report:
        report.write("<test-run><test-suite>" + "".join(rows) + "</test-suite></test-run>")
    sys.exit(8 if any(c["result"] == "Failed" for c in cases) else 0)
    """
)

FAKE_COMPILE_CHECK = textwrap.dedent(
    """
    import os, sys
    print(os.environ.get("FAKE_COMPILE_OUTPUT", "COMPILE_OK"))
    sys.exit(int(os.environ.get("FAKE_COMPILE_EXIT", "0")))
    """
)


class BatchTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="unity-test-batch-"))
        self.project = self.temp / "Game"
        (self.project / "ProjectSettings").mkdir(parents=True)
        (self.project / "Assets" / "Scripts").mkdir(parents=True)
        (self.project / "Assets" / "Scripts" / "Inventory.cs").write_text("class Inventory {}", encoding="utf-8")
        (self.project / "Assets" / "Scripts" / "Reward.cs").write_text("class Reward {}", encoding="utf-8")
        self.calls = self.temp / "calls.log"
        cases = self.temp / "cases.json"
        cases.write_text(json.dumps(CASES), encoding="utf-8")
        fake_unity = self.temp / "fake_unity.py"
        fake_unity.write_text(FAKE_UNITY, encoding="utf-8")
        if os.name == "nt":
            self.unity_bin = self.temp / "fake_unity.cmd"
            self.unity_bin.write_text(f'@"{sys.executable}" "{fake_unity}" %*\r\n@exit /b %ERRORLEVEL%\r\n', encoding="utf-8")
        else:
            self.unity_bin = self.temp / "fake_unity"
            self.unity_bin.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{fake_unity}" "$@"\n', encoding="utf-8")
            self.unity_bin.chmod(0o755)
        fake_check = self.temp / "fake_compile_check.py"
        fake_check.write_text(FAKE_COMPILE_CHECK, encoding="utf-8")
        environment = {
            "UNITY_TEST_BATCH_HOME": str(self.temp / "state"),
            "UNITY_TEST_BATCH_COMPILE_CHECK": str(fake_check),
            "FAKE_UNITY_CALLS": str(self.calls),
            "FAKE_UNITY_CASES": str(cases),
            "FAKE_COMPILE_EXIT": "0",
        }
        patcher = mock.patch.dict(os.environ, environment)
        patcher.start()
        self.addCleanup(patcher.stop)
        seal = mock.patch.object(batch, "should_seal", return_value=True)
        seal.start()
        self.addCleanup(seal.stop)
        self.queue = batch.Queue(self.project.resolve())

    def enqueue(self, filters: str, files: list[str], mode: str = "EditMode") -> dict:
        """Queue a request the way another session's submit would, without waiting."""
        root = self.project.resolve()
        request = {
            "id": f"other{len(self.queue.pending())}",
            "task": "GAME-2",
            "session": "other",
            "mode": mode,
            "filters": batch.split_filters(filters),
            "files": files,
            "digest": batch.files_digest(root, files),
            "runner_project": None,
            "created": time.time(),
        }
        batch.write_json(self.queue.requests / f"{request['id']}.json", request)
        return request

    def submit(self, filters: str, files: list[str], *extra: str) -> tuple[int, str]:
        arguments = ["submit", "--project", str(self.project), "--mode", "EditMode", "--filter", filters,
                     "--task", "GAME-1", "--unity-bin", str(self.unity_bin), "--wait-limit", "30", "--files", *files]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = batch.main(arguments + list(extra))
        return code, output.getvalue()

    def result(self, request_id: str) -> dict:
        return batch.read_json(self.queue.result_path(request_id))

    def unity_calls(self) -> list[list[str]]:
        if not self.calls.exists():
            return []
        return [json.loads(line) for line in self.calls.read_text(encoding="utf-8").splitlines()]


class FilterTests(unittest.TestCase):
    def test_matches_exact_parent_regex_and_parameterized_names(self) -> None:
        self.assertTrue(batch.filter_matches("Game.Reward.RewardTests", "Game.Reward.RewardTests.Claim_Grants"))
        self.assertTrue(batch.filter_matches("Game.Reward.RewardTests.Claim_Twice(1,2)", "Game.Reward.RewardTests.Claim_Twice(1,2)"))
        self.assertTrue(batch.filter_matches("Game.Reward.RewardTests.Claim_Twice", "Game.Reward.RewardTests.Claim_Twice(1,2)"))
        self.assertTrue(batch.filter_matches("Claim_.*", "Game.Reward.RewardTests.Claim_Grants"))
        self.assertFalse(batch.filter_matches("Game.Inventory", "Game.Reward.RewardTests.Claim_Grants"))

    def test_exclusion_filters_are_rejected(self) -> None:
        with self.assertRaises(batch.UsageError):
            batch.split_filters("Game.Reward;!Game.Reward.Slow")

    def test_one_whole_platform_request_widens_the_merged_run(self) -> None:
        self.assertEqual(batch.merge_filters([{"filters": ["A"]}, {"filters": ["B", "A"]}]), ["A", "B"])
        self.assertIsNone(batch.merge_filters([{"filters": ["A"]}, {"filters": []}]))

    def test_zero_matched_tests_is_no_tests_not_pass(self) -> None:
        # Unity reports an empty filter match as result="Passed" with total="0".
        report = Path(tempfile.mkdtemp()) / "empty.xml"
        report.write_text('<test-run testcasecount="0" result="Passed" total="0"><test-suite result="Passed"/></test-run>', encoding="utf-8")
        self.assertEqual(batch.classify(batch.parse_results(report)), "NO_TESTS")

    def test_live_editor_json_results_are_accepted(self) -> None:
        report = Path(tempfile.mkdtemp()) / "results.json"
        report.write_text(json.dumps({"tests": [{"fullName": "A.B.C", "state": "Success"}, {"name": "A.B.D", "outcome": "Failure", "message": "x"}]}), encoding="utf-8")
        cases = batch.parse_results(report)
        self.assertEqual([case["result"] for case in cases], ["Passed", "Failed"])


class PolicyTests(unittest.TestCase):
    def test_leader_waits_for_a_quiet_period_and_never_past_the_cap(self) -> None:
        self.assertFalse(batch.should_seal(1, oldest_wait=5, quiet_for=5))
        self.assertTrue(batch.should_seal(1, oldest_wait=20, quiet_for=20))
        self.assertFalse(batch.should_seal(4, oldest_wait=60, quiet_for=3))
        self.assertTrue(batch.should_seal(4, oldest_wait=90, quiet_for=3))


class SharedRunTests(BatchTestCase):
    def test_two_sessions_share_one_unity_run_and_get_only_their_tests(self) -> None:
        other = self.enqueue("Game.Reward", ["Assets/Scripts/Reward.cs"])
        code, output = self.submit("Game.Inventory", ["Assets/Scripts/Inventory.cs"])

        calls = self.unity_calls()
        self.assertEqual(len(calls), 1, "both requests must share one Unity launch")
        self.assertEqual(calls[0][calls[0].index("--filter") + 1], "Game.Reward;Game.Inventory")
        self.assertEqual(code, batch.EXIT_CODES["FAIL"])
        self.assertIn("TEST_BATCH: FAIL (1/2)", output)
        self.assertIn("Remove_Underflows: Expected 1 but was 2", output)
        reward = self.result(other["id"])
        self.assertEqual((reward["status"], reward["passed"], reward["matched"]), ("PASS", 2, 2))
        self.assertEqual(reward["batch_requests"], 2)
        self.assertFalse(self.queue.claim_path.exists(), "the leader releases its claim")

    def test_file_changed_after_submit_is_stale_and_not_run(self) -> None:
        other = self.enqueue("Game.Reward", ["Assets/Scripts/Reward.cs"])
        (self.project / "Assets" / "Scripts" / "Reward.cs").write_text("class Reward { int changed; }", encoding="utf-8")
        code, _ = self.submit("Game.Inventory.InventoryTests.Add_Stacks", ["Assets/Scripts/Inventory.cs"])

        self.assertEqual(code, batch.EXIT_CODES["PASS"])
        self.assertEqual(self.result(other["id"])["status"], "STALE")
        calls = self.unity_calls()
        self.assertEqual(calls[0][calls[0].index("--filter") + 1], "Game.Inventory.InventoryTests.Add_Stacks")

    def test_compile_errors_blame_the_owner_and_block_the_others_without_launching_unity(self) -> None:
        other = self.enqueue("Game.Reward", ["Assets/Scripts/Reward.cs"])
        output = "Assets/Scripts/Inventory.cs(3,5): error CS0103: The name 'x' does not exist\nCOMPILE_ERRORS"
        with mock.patch.dict(os.environ, {"FAKE_COMPILE_EXIT": "1", "FAKE_COMPILE_OUTPUT": output}):
            code, _ = self.submit("Game.Inventory", ["Assets/Scripts/Inventory.cs"])

        self.assertEqual(code, batch.EXIT_CODES["COMPILE_ERRORS"])
        self.assertEqual(self.result(other["id"])["status"], "BLOCKED_BY_OTHER_COMPILE")
        self.assertEqual(self.unity_calls(), [])

    def test_request_that_matches_no_test_is_not_a_pass(self) -> None:
        code, output = self.submit("Game.Typo", ["Assets/Scripts/Inventory.cs"])
        self.assertEqual(code, batch.EXIT_CODES["NO_TESTS"])
        self.assertIn("TEST_BATCH: NO_TESTS (0/0)", output)

    def test_open_editor_hands_the_plan_to_the_leader_and_publish_fans_out(self) -> None:
        other = self.enqueue("Game.Reward", ["Assets/Scripts/Reward.cs"])
        with mock.patch.object(batch, "project_locked", return_value=True):
            code, output = self.submit("Game.Inventory", ["Assets/Scripts/Inventory.cs"])

        self.assertEqual(code, batch.EXIT_LEADER_RUN_REQUIRED)
        self.assertIn("filter=Game.Reward;Game.Inventory", output)
        self.assertEqual(self.unity_calls(), [])
        claim = batch.read_json(self.queue.claim_path)
        self.assertIsNotNone(claim["external_until"], "the claim outlives the leader process during the live run")

        report = self.temp / "live.xml"
        rows = "".join(f'<test-case fullname="{case["fullname"]}" result="{case["result"]}"/>' for case in CASES)
        report.write_text(f"<test-run>{rows}</test-run>", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            publish_code = batch.main(["publish", "--project", str(self.project), "--batch", claim["batch"],
                                       "--mode", "EditMode", "--results", str(report)])

        self.assertEqual(publish_code, batch.EXIT_CODES["FAIL"])
        self.assertEqual(self.result(other["id"])["status"], "PASS")
        self.assertFalse(self.queue.claim_path.exists())

    def test_runner_project_that_does_not_share_assets_is_not_used(self) -> None:
        runner = self.temp / "Runner"
        (runner / "Assets").mkdir(parents=True)
        request = {"runner_project": str(runner)}
        chosen, note = batch.choose_runner(self.project.resolve(), [request])
        self.assertEqual(chosen, self.project.resolve())
        self.assertIn("does not share", note)


class ClaimTests(BatchTestCase):
    def write_claim(self, pid: int, **fields: object) -> None:
        record = {"token": "staletoken", "pid": pid, "host": socket.gethostname(), "heartbeat": time.time(),
                  "external_until": None, "batch": None}
        record.update(fields)
        batch.write_json(self.queue.claim_path, record)

    def test_claim_of_a_dead_leader_is_recovered(self) -> None:
        finished = subprocess.Popen([sys.executable, "-c", "pass"])
        finished.wait()
        self.write_claim(finished.pid)
        claim = batch.LeaderClaim(self.queue)
        self.assertTrue(claim.try_acquire())
        self.assertTrue(list(self.queue.root.glob("leader.claim.stale-*")))
        claim.release()

    def test_claim_of_a_live_leader_is_respected(self) -> None:
        self.write_claim(os.getpid())
        self.assertFalse(batch.LeaderClaim(self.queue).try_acquire())

    def test_wait_timeout_withdraws_a_request_that_never_ran(self) -> None:
        self.write_claim(os.getpid())
        code, output = self.submit("Game.Inventory", ["Assets/Scripts/Inventory.cs"], "--wait-limit", "0")
        self.assertEqual(code, batch.EXIT_WAIT_TIMEOUT)
        self.assertIn("withdrawn", output)
        self.assertEqual(self.queue.pending(), [])

    def test_requests_of_a_dead_leaders_batch_return_to_the_queue(self) -> None:
        request = self.enqueue("Game.Reward", ["Assets/Scripts/Reward.cs"])
        sealed_batch, _ = batch.seal(self.queue, self.queue.pending())
        batch.requeue_orphans(self.queue)
        self.assertEqual([path.stem for path in self.queue.pending()], [request["id"]])
        self.assertTrue((sealed_batch / "abandoned.json").exists())


@unittest.skipUnless(os.name == "nt", "Windows byte-range lock")
class EditorLockTests(unittest.TestCase):
    def test_locked_lockfile_means_an_open_editor(self) -> None:
        import msvcrt

        project = Path(tempfile.mkdtemp())
        lockfile = project / "Temp" / "UnityLockfile"
        lockfile.parent.mkdir()
        lockfile.write_text("", encoding="utf-8")
        self.assertFalse(batch.project_locked(project))
        with open(lockfile, "a") as holder:
            holder.seek(0)
            msvcrt.locking(holder.fileno(), msvcrt.LK_NBLCK, 1)
            self.assertTrue(batch.project_locked(project))
            msvcrt.locking(holder.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == "__main__":
    unittest.main()
