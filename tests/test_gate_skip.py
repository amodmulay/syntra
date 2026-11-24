"""Tests that the gate skips the real checks script when a branch's diff
touches nothing under config.json's code_paths (e.g. a docs-only pass), but
still runs it for any branch that touches src/ or tests/, and still fails on
a protected-path change even when the check run itself is skipped.

Uses the real factory/config.json (code_paths, protected_paths, lines.build)
loaded at import time; only REPO is pointed at a sandbox so no real worktree
or job state is touched.
"""

import importlib.machinery
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / rel))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


gate_module = load("gate_under_test_skip", "factory/bin/gate")


def git(cwd, *args):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr}")
    return res.stdout


class GateSkipTests(unittest.TestCase):
    JOB_ID = "999-gate-skip-test"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name).resolve() / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "Sandbox")
        git(self.repo, "config", "user.email", "sandbox@example.invalid")
        git(self.repo, "config", "commit.gpgsign", "false")

        self.marker = self.repo / "ran.marker"
        (self.repo / "factory" / "bin").mkdir(parents=True)
        (self.repo / "factory" / "bin" / "fake-checks.sh").write_text(
            f"#!/usr/bin/env bash\ntouch {self.marker}\nexit 0\n"
        )
        (self.repo / "src").mkdir()
        (self.repo / "src" / "calc.py").write_text("x = 1\n")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "t.py").write_text("# placeholder\n")
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "readme.md").write_text("docs\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "base")

        self.worktree = self.repo / ".worktrees" / self.JOB_ID
        self.worktree.parent.mkdir(parents=True, exist_ok=True)
        git(self.repo, "worktree", "add", "-b", f"factory/{self.JOB_ID}", str(self.worktree), "main")

        self.patch(gate_module, "REPO", self.repo)
        self.patch(gate_module, "FACTORY", self.repo / "factory")
        self.patch(gate_module.CONFIG["lines"]["build"], "checks", "factory/bin/fake-checks.sh")

    def patch(self, obj, key, value):
        if isinstance(obj, dict):
            old = obj.get(key)
            obj[key] = value
            self.addCleanup(lambda: obj.__setitem__(key, old))
        else:
            old = getattr(obj, key)
            setattr(obj, key, value)
            self.addCleanup(lambda: setattr(obj, key, old))

    def make_job(self, round_=1):
        return {
            "id": self.JOB_ID, "branch": f"factory/{self.JOB_ID}",
            "worktree": str(self.worktree), "line": "build", "pass": 1,
            "round": round_,
        }

    def write_job(self, job):
        jobs_dir = self.repo / "factory" / "jobs" / self.JOB_ID
        jobs_dir.mkdir(parents=True, exist_ok=True)
        import json
        (jobs_dir / "job.json").write_text(json.dumps(job))
        self.patch(gate_module, "load_job", lambda jid: job)

    def round_dir(self, job):
        return self.repo / "factory" / "jobs" / job["id"] / f"{job['pass']:02d}-{job['line']}" / f"round-{job['round']}"

    def test_docs_only_diff_skips_the_check_script(self):
        (self.worktree / "docs" / "readme.md").write_text("docs changed\n")
        git(self.worktree, "commit", "-am", "docs change")
        job = self.make_job()
        self.write_job(job)
        with self.assertRaises(SystemExit) as cm:
            gate_module.gate(self.JOB_ID, merge=False)
        self.assertEqual(cm.exception.code, 0)
        self.assertFalse(self.marker.exists(), "the check script must not run for a docs-only diff")
        checks_md = (self.round_dir(job) / "checks.md").read_text()
        self.assertTrue(checks_md.startswith("GATE: PASS"))
        self.assertIn("skipped", checks_md)

    def test_src_change_still_runs_the_check_script(self):
        (self.worktree / "src" / "calc.py").write_text("x = 2\n")
        git(self.worktree, "commit", "-am", "code change")
        job = self.make_job()
        self.write_job(job)
        with self.assertRaises(SystemExit) as cm:
            gate_module.gate(self.JOB_ID, merge=False)
        self.assertEqual(cm.exception.code, 0)
        self.assertTrue(self.marker.exists(), "a src/ change must still run the real check script")
        checks_md = (self.round_dir(job) / "checks.md").read_text()
        self.assertTrue(checks_md.startswith("GATE: PASS"))
        self.assertNotIn("skipped", checks_md.splitlines()[0])

    def test_protected_only_diff_still_fails_even_when_skipped(self):
        (self.repo / "factory" / "checks.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
        git(self.repo, "add", "factory/checks.sh")
        git(self.repo, "commit", "-m", "add protected file")
        git(self.worktree, "merge", "main")
        (self.worktree / "factory" / "checks.sh").write_text("#!/usr/bin/env bash\nexit 1\n")
        git(self.worktree, "commit", "-am", "touch protected file")
        job = self.make_job()
        self.write_job(job)
        with self.assertRaises(SystemExit) as cm:
            gate_module.gate(self.JOB_ID, merge=False)
        self.assertEqual(cm.exception.code, 1)
        self.assertFalse(self.marker.exists(), "still skipped: the protected-path diff isn't under code_paths")
        checks_md = (self.round_dir(job) / "checks.md").read_text()
        self.assertTrue(checks_md.startswith("GATE: FAIL"))
        self.assertIn("factory/checks.sh", checks_md)


if __name__ == "__main__":
    unittest.main()
