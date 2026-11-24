"""Tests for resolving a job's stored worktree to this machine's worktree.

factory/bin/job and factory/bin/gate are loaded by path (they have no .py
suffix). Every test uses its own sandbox git repo in a temp dir, with the
module globals REPO and JOBS pointed at it. The real .worktrees/ and
factory/jobs/ are never read or written, and job.save() is never called.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOB_ID = "013-resolve-foreign-worktree-paths-in"
FOREIGN = "D:\\repo\\syntra\\.worktrees\\" + JOB_ID


def load(name, rel):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / rel))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


job_module = load("job_under_test", "factory/bin/job")
gate_module = load("gate_under_test", "factory/bin/gate")


def git(cwd, *args):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr}")
    return res.stdout


class SandboxCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "Sandbox")
        git(self.repo, "config", "user.email", "sandbox@example.invalid")
        git(self.repo, "config", "commit.gpgsign", "false")
        (self.repo / "README.md").write_text("sandbox\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "init")
        (self.repo / ".worktrees").mkdir()
        self.jobs = self.root / "jobs"
        self.jobs.mkdir()
        self.patch(job_module, "REPO", self.repo)
        self.patch(job_module, "JOBS", self.jobs)
        self.patch(gate_module, "REPO", self.repo)

    def patch(self, module, name, value):
        old = getattr(module, name)
        setattr(module, name, value)
        self.addCleanup(setattr, module, name, old)

    def make_job(self, stored, job_id=JOB_ID):
        return {"id": job_id, "topic": "resolve-foreign-worktree-paths-in",
                "branch": f"factory/{job_id}", "worktree": stored, "stage": "build",
                "line": "build", "pass": 1, "passes": [], "round": 1,
                "round_limit": 3, "gate": None, "reviews": {}}

    def add_local_worktree(self, job_id=JOB_ID):
        path = self.repo / ".worktrees" / job_id
        git(self.repo, "worktree", "add", "-b", f"factory/{job_id}", str(path), "main")
        return path


class ForeignPathTests(SandboxCase):
    def test_foreign_absolute_path_runs_git_in_local_worktree(self):
        local = self.add_local_worktree()
        job = self.make_job(FOREIGN)
        top = job_module.git(job, "rev-parse", "--show-toplevel").stdout.strip()
        self.assertEqual(os.path.realpath(top), os.path.realpath(local))

    def test_local_existing_path_is_used_unchanged(self):
        elsewhere = self.root / "elsewhere" / JOB_ID
        elsewhere.parent.mkdir()
        git(self.repo, "worktree", "add", "-b", f"factory/{JOB_ID}-alt", str(elsewhere), "main")
        job = self.make_job(str(elsewhere))
        self.assertEqual(job_module.worktree_path(job), str(elsewhere))
        top = job_module.git(job, "rev-parse", "--show-toplevel").stdout.strip()
        self.assertEqual(os.path.realpath(top), os.path.realpath(elsewhere))

    def test_missing_local_worktree_refuses(self):
        job = self.make_job(FOREIGN)
        with self.assertRaises(job_module.Refused) as cm:
            job_module.git(job, "rev-parse", "HEAD")
        self.assertIn(JOB_ID, str(cm.exception))

    def test_traversal_like_ids_are_refused(self):
        (self.repo / "x").mkdir()
        (self.repo / "b").mkdir()
        bad_ids = ["../x", "013-../x", "013-a/../../b", "013-a\\b", "013-A", "13-x", "013-x\n"]
        for bad in bad_ids:
            with self.subTest(job_id=bad):
                job = self.make_job(FOREIGN, job_id=bad)
                with self.assertRaises(job_module.Refused):
                    job_module.worktree_path(job)
                with self.assertRaises(SystemExit):
                    with contextlib.redirect_stderr(io.StringIO()):
                        gate_module.worktree_path(job)

    @unittest.skipIf(os.name == "nt", "symlinks need extra rights on Windows")
    def test_symlink_escaping_worktrees_is_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.repo / ".worktrees" / JOB_ID, target_is_directory=True)
        job = self.make_job(FOREIGN)
        with self.assertRaises(job_module.Refused):
            job_module.worktree_path(job)
        self.assertIsNone(job_module.existing_worktree(job))


class NoStateTests(SandboxCase):
    def test_job_json_is_not_rewritten(self):
        self.add_local_worktree()
        job_dir = self.jobs / JOB_ID
        job_dir.mkdir()
        (job_dir / "job.json").write_text(json.dumps(self.make_job(FOREIGN), indent=2))
        before_bytes = (job_dir / "job.json").read_bytes()
        before_listing = sorted(os.listdir(job_dir))

        job = json.loads(before_bytes)
        job_module.git(job, "rev-parse", "HEAD")
        job_module.worktree_path(job)
        job_module.drop_worktree(job)

        self.assertEqual((job_dir / "job.json").read_bytes(), before_bytes)
        self.assertEqual(sorted(os.listdir(job_dir)), before_listing)
        self.assertEqual(job["worktree"], FOREIGN)

    def test_drop_worktree_foreign_path(self):
        local = self.add_local_worktree()
        job = self.make_job(FOREIGN)
        job_module.drop_worktree(job)
        self.assertFalse(local.exists())
        self.assertEqual(git(self.repo, "branch", "--list", f"factory/{JOB_ID}").strip(), "")
        # Nothing left to remove: must succeed without error.
        job_module.drop_worktree(job)

    def test_start_pass_creates_local_worktree_for_foreign_job(self):
        job = self.make_job(FOREIGN)
        job["passes"] = []
        job["pass"] = 0
        job["round"] = 0
        job["line"] = None
        job_module.start_pass(job, "build")
        self.assertTrue((self.repo / ".worktrees" / JOB_ID).is_dir())
        self.assertFalse(Path(FOREIGN).exists())
        self.assertEqual(job["worktree"], FOREIGN)
        self.assertEqual(job["pass"], 1)


class ParityTests(SandboxCase):
    def test_gate_and_job_resolve_identically(self):
        job = self.make_job(FOREIGN)
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                gate_module.worktree_path(job)
        local = self.add_local_worktree()
        resolved = gate_module.worktree_path(job)
        self.assertEqual(resolved, job_module.worktree_path(job))
        self.assertEqual(os.path.realpath(resolved), os.path.realpath(local))


if __name__ == "__main__":
    unittest.main()
