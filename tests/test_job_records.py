"""Durable job records: factory/bin/job writes factory/records/<id>.json at final merge and reject.

Every test runs against a throwaway git repository under a temp directory. The
module globals that point into the real checkout (REPO, FACTORY, JOBS, INBOX,
RECORDS, BIN) are replaced per test, and so is `run`, whose default `cwd=REPO`
is bound at definition time and would otherwise reach the real repository.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REAL_REPO = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("job_bin", str(REAL_REPO / "factory" / "bin" / "job"))
spec = importlib.util.spec_from_loader("job_bin", loader)
job = importlib.util.module_from_spec(spec)
loader.exec_module(job)

SECRET_BODY = "SECRET BODY TEXT never belongs in a record"
RECORD_KEYS = {"id", "topic", "title", "stage", "line", "pass", "triage", "started", "ended", "cost_usd", "models"}
TRIAGE_KEYS = {"decision", "line", "risk", "surfaces"}


class RecordTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="job-records-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        factory = self.repo / "factory"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.set_gate(0)

        self.patch("REPO", self.repo)
        self.patch("FACTORY", factory)
        self.patch("JOBS", factory / "jobs")
        self.patch("INBOX", factory / "inbox")
        self.patch("RECORDS", factory / "records")
        self.patch("BIN", self.bin)
        self.patch("ingest_usage", lambda: None)
        self.patch("usage_by_step", lambda j: [])
        real_run = job.run
        self.patch("run", lambda cmd, cwd=None, check=True: real_run(cmd, cwd=cwd or self.repo, check=check))

        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test Builder")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.repo / ".gitignore").write_text("/factory/jobs/\n/factory/inbox/\n/.worktrees/\n")
        (self.repo / "README.md").write_text("base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")

    def tearDown(self):
        for lock in list(job._locks.values()):
            lock.close()
        job._locks.clear()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def patch(self, name, value):
        original = getattr(job, name)
        setattr(job, name, value)
        self.addCleanup(setattr, job, name, original)

    def set_gate(self, code):
        (self.bin / "gate").write_text(f"import sys\nsys.exit({code})\n")

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.strip()

    def base_sha(self):
        return self.git("rev-parse", "main")

    def make_job(self, line="docs", stage="merging", job_id="001-new-topic", topic="new-topic"):
        """A job with its own worktree and one commit of work, ready for `cmd_merge` or `cmd_reject`."""
        job.INBOX.mkdir(parents=True, exist_ok=True)
        (job.INBOX / f"{topic}.md").write_text(f"# Add a thing\n\n{SECRET_BODY}\n")
        worktree = self.tmp / "worktrees" / job_id
        branch = f"factory/{job_id}"
        self.git("worktree", "add", "-b", branch, str(worktree), "main")
        (worktree / "change.txt").write_text(f"work for {job_id}\n")
        self.git("add", "change.txt", cwd=worktree)
        self.git("commit", "-m", f"Work for {job_id}", cwd=worktree)
        j = {
            "id": job_id, "topic": topic, "title": "Add a thing",
            "stage": stage, "line": line, "pass": 1,
            "passes": [{"pass": 1, "line": line, "outcome": None}], "handoff_to": None,
            "branch": branch, "worktree": str(worktree),
            "round": 1, "round_limit": 3,
            "triage": {"decision": "ACCEPT", "line": line, "rescoped": False, "risk": "low", "surfaces": ["ui"]},
            "agents": {"reviewers": {}}, "gate": None, "reviews": {},
            "cost_usd": 1.25,
            "models": [{"step": "build", "model": "claude-haiku-5-5", "calls": 3, "tokens": 900, "cost": 1.25}],
            "started": "2026-11-24T10:00:00Z", "ended": None,
        }
        job.job_dir(job_id).mkdir(parents=True, exist_ok=True)
        job.pass_dir(j).mkdir(parents=True, exist_ok=True)
        job.save(j)
        return j

    def read_job(self, job_id):
        return json.loads((job.job_dir(job_id) / "job.json").read_text())

    def quiet(self, fn, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return fn(*args)


class JobRecordTests(RecordTestCase):
    def test_record_has_only_allowlisted_fields(self):
        j = self.make_job(line="docs", stage="merged")
        j["ended"] = "2026-11-24T11:00:00Z"
        rec = job.job_record(j)
        self.assertEqual(set(rec), RECORD_KEYS)
        self.assertEqual(set(rec["triage"]), TRIAGE_KEYS)
        text = job.record_text(rec)
        self.assertNotIn(str(self.tmp), text)
        self.assertNotIn(self.tmp.as_posix(), text)
        self.assertNotIn(j["worktree"], text)
        self.assertNotIn(SECRET_BODY, text)
        self.assertNotIn("rescoped", text)

    def test_record_id_rejects_traversal(self):
        for bad in ("../x", "a/b", "", ".hidden/x", "a\\b"):
            with self.subTest(id=bad), self.assertRaises(job.Refused):
                job.check_record_id(bad)
            with self.subTest(id=bad), self.assertRaises(job.Refused):
                job.write_record(self.tmp / "out", {"id": bad})
        self.assertFalse((self.tmp / "x.json").exists())
        self.assertEqual(job.check_record_id("011-keep-finished_job.records"), "011-keep-finished_job.records")

    def test_merge_final_line_commits_record_to_base(self):
        j = self.make_job(line="docs", stage="merging")
        self.quiet(job.cmd_merge, j)
        self.assertEqual(self.git("show", "--name-only", "--format=", "main"),
                         "factory/records/001-new-topic.json")
        rec = json.loads(self.git("show", "main:factory/records/001-new-topic.json"))
        self.assertEqual(rec["stage"], "merged")
        self.assertIn("cost_usd", rec)
        self.assertEqual(rec["models"][0]["model"], "claude-haiku-5-5")
        self.assertEqual(self.read_job("001-new-topic")["stage"], "merged")
        self.assertEqual(subprocess.run(["git", "rev-parse", "--verify", "-q", "factory/001-new-topic"],
                                        cwd=self.repo, capture_output=True).returncode, 1)

    def test_merge_handoff_writes_no_record(self):
        j = self.make_job(line="build", stage="merging")
        self.quiet(job.cmd_merge, j)
        self.assertFalse(job.RECORDS.exists())
        self.assertNotIn("factory/records", self.git("log", "--name-only", "--format=", "main"))
        self.assertEqual(self.read_job("001-new-topic")["stage"], "spec")
        self.assertEqual(self.read_job("001-new-topic")["line"], "docs")

    def test_gate_failure_writes_no_record(self):
        self.set_gate(1)
        j = self.make_job(line="docs", stage="merging")
        before = self.base_sha()
        self.quiet(job.cmd_merge, j)
        self.assertEqual(self.base_sha(), before)
        self.assertFalse((Path(j["worktree"]) / "factory" / "records").exists())
        self.assertNotIn("factory/records", self.git("log", "--name-only", "--format=", "main"))
        self.assertEqual(self.read_job("001-new-topic")["stage"], "needs-human")

    def test_record_commit_failure_leaves_base_untouched(self):
        j = self.make_job(line="docs", stage="merging")
        before, branch_tip = self.base_sha(), self.git("rev-parse", j["branch"])

        def broken_commit(job_arg, record):
            raise OSError("disk full")

        self.patch("commit_record", broken_commit)
        self.quiet(job.cmd_merge, j)
        self.assertEqual(self.base_sha(), before)
        self.assertEqual(self.git("rev-parse", j["branch"]), branch_tip)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "needs-human")

    def test_reject_writes_uncommitted_record(self):
        j = self.make_job(line="docs", stage="needs-human")
        before = self.base_sha()
        self.quiet(job.cmd_reject, j, "not wanted")
        record_path = job.RECORDS / "001-new-topic.json"
        self.assertTrue(record_path.exists())
        self.assertEqual(json.loads(record_path.read_text())["stage"], "rejected")
        status = self.git("status", "--porcelain", "--untracked-files=all")
        self.assertIn("?? factory/records/001-new-topic.json", status.splitlines())
        self.assertEqual(self.base_sha(), before)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")
        self.assertFalse(Path(j["worktree"]).exists())
        self.assertEqual(self.git("branch", "--list", j["branch"]), "")

    def test_reject_record_failure_keeps_job_waiting(self):
        blocker = self.tmp / "afile"
        blocker.write_text("not a directory")
        self.patch("RECORDS", blocker / "records")
        j = self.make_job(line="docs", stage="needs-human")
        with self.assertRaises(SystemExit):
            self.quiet(job.cmd_reject, j, "not wanted")
        self.assertEqual(self.read_job("001-new-topic")["stage"], "needs-human")
        self.assertTrue(Path(j["worktree"]).exists())

    def test_create_numbering_skips_recorded_ids(self):
        job.RECORDS.mkdir(parents=True)
        (job.RECORDS / "005-old-topic.json").write_text("{}\n")
        job.INBOX.mkdir(parents=True)
        (job.INBOX / "new-topic.md").write_text("# New topic\n")
        self.quiet(job.cmd_create, "new-topic")
        self.assertTrue((job.JOBS / "006-new-topic" / "job.json").exists())

    def test_no_record_for_in_progress_stages(self):
        job.INBOX.mkdir(parents=True)
        (job.INBOX / "new-topic.md").write_text("# New topic\n")
        self.quiet(job.cmd_create, "new-topic")
        d = job.job_dir("001-new-topic")
        (d / "triage.md").write_text("DECISION: ACCEPT\nLINE: docs\nRISK: low\nSURFACES: none\n\nok\n")
        j = job.sync(job.load("001-new-topic"))
        j["agents"] = {"reviewers": {}}
        job.advance(j, "spec")
        job.save(j)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "spec")
        self.assertFalse(job.RECORDS.exists())

    def test_dashboard_reads_records_and_dedupes(self):
        text = (REAL_REPO / "factory" / "dashboard.html").read_text(encoding="utf-8")
        self.assertIn("fetchText('records/')", text)
        self.assertIn("from record", text)
        self.assertIn("jobIds", text)


if __name__ == "__main__":
    unittest.main()
