"""Tests for the refused-land escalation in factory/bin/job.

Every test builds its own sandbox git repo in a temp dir and runs a copy of the
branch's factory/bin/job inside it. The real factory/jobs/, .worktrees/ and
factory/usage/ are never read or written.
"""

import ast
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOB_SRC = ROOT / "factory" / "bin" / "job"
CONFIG_SRC = ROOT / "factory" / "config.json"
JOB_ID = "012-fix-merge-escalation-on-conflicts"

# The base commit's transition table. Editing TRANSITIONS to get around the
# merging ancestor check must fail T9.
EXPECTED_TRANSITIONS = {
    "triage": {"needs-info", "rejected", "spec"},
    "needs-info": {"triage", "rejected"},
    "spec": {"build"},
    "build": {"gate", "needs-human"},
    "gate": {"review", "build", "needs-human"},
    "review": {"approve", "build", "needs-human"},
    "approve": {"merging", "needs-human"},
    "merging": {"merged", "spec", "needs-human"},
    "needs-human": {"build", "rejected", "merging"},
}

GATE_OK = "import sys\nsys.exit(0)\n"
GATE_FAIL = "import sys\nprint('gate output: tests failed')\nsys.exit(1)\n"


def git(cwd, *args):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr}")
    return res.stdout


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="factory-merge-test-"))
        self.sandbox = self.tmp / "repo"
        self.claude_cfg = self.tmp / "claude-config"  # empty: no transcripts
        self.claude_cfg.mkdir()
        self.sandbox.mkdir()
        git(self.sandbox, "init", "-b", "main")
        git(self.sandbox, "config", "user.name", "Sandbox Test")
        git(self.sandbox, "config", "user.email", "sandbox@example.invalid")
        git(self.sandbox, "config", "commit.gpgsign", "false")
        self.job_path = self.sandbox / "factory" / "bin" / "job"
        (self.sandbox / "factory" / "bin").mkdir(parents=True)
        shutil.copyfile(JOB_SRC, self.job_path)
        shutil.copyfile(CONFIG_SRC, self.sandbox / "factory" / "config.json")
        (self.sandbox / "factory" / "inbox").mkdir()
        (self.sandbox / "factory" / "inbox" / "fix-merge.md").write_text("# Fix merge\n")
        self.set_gate(GATE_OK)
        (self.sandbox / ".gitignore").write_text("factory/jobs/\n.worktrees/\n")
        (self.sandbox / "calc.txt").write_text("base\n")
        git(self.sandbox, "add", ".gitignore", "calc.txt")
        git(self.sandbox, "commit", "-m", "base")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- fixtures -----------------------------------------------------------

    def set_gate(self, src):
        gate = self.sandbox / "factory" / "bin" / "gate"
        gate.write_text(src)

    def make_branch(self, conflict=True):
        """Create the job branch and worktree. conflict=True makes main diverge
        on calc.txt so `git merge` conflicts; otherwise main is untouched."""
        self.worktree = self.sandbox / ".worktrees" / JOB_ID
        self.worktree.parent.mkdir(parents=True, exist_ok=True)
        git(self.sandbox, "worktree", "add", "-b", f"factory/{JOB_ID}",
            str(self.worktree), "main")
        (self.worktree / "calc.txt").write_text("branch\n")
        git(self.worktree, "commit", "-am", "branch change")
        if conflict:
            (self.sandbox / "calc.txt").write_text("main\n")
            git(self.sandbox, "commit", "-am", "main change")

    def make_job(self, stage, passes_outcome=None):
        job_dir = self.sandbox / "factory" / "jobs" / JOB_ID
        pass_dir = job_dir / "01-build"
        pass_dir.mkdir(parents=True)
        job = {
            "id": JOB_ID, "topic": "fix-merge", "title": "Fix merge",
            "stage": stage, "line": "build", "pass": 1,
            "passes": [{"pass": 1, "line": "build", "outcome": passes_outcome}],
            "handoff_to": None,
            "branch": f"factory/{JOB_ID}",
            "worktree": str(self.sandbox / ".worktrees" / JOB_ID),
            "round": 1, "round_limit": 3,
            "triage": None, "agents": {"reviewers": []}, "reviews": {},
            "gate": None, "cost_usd": 0.0, "models": [],
            "started": "2026-01-01T00:00:00Z", "ended": None,
            "human_approvals": 0,
        }
        self.write_job(job)
        if stage == "approve" or stage == "merging":
            (pass_dir / "decision.md").write_text("APPROVE\n\n## Summary\nlooks good\n")
        return job

    def write_job(self, job):
        path = self.sandbox / "factory" / "jobs" / JOB_ID / "job.json"
        path.write_text(json.dumps(job, indent=2) + "\n")

    def job_bytes(self):
        return (self.sandbox / "factory" / "jobs" / JOB_ID / "job.json").read_bytes()

    def pass_dirs(self):
        job_dir = self.sandbox / "factory" / "jobs" / JOB_ID
        return sorted(p.name for p in job_dir.iterdir() if p.is_dir())

    def decision(self):
        return (self.sandbox / "factory" / "jobs" / JOB_ID / "01-build" / "decision.md").read_text()

    def load_job(self):
        return json.loads(self.job_bytes())

    def run_job(self, *args):
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(self.claude_cfg))
        return subprocess.run([sys.executable, "-I", str(self.job_path), *args],
                              cwd=self.sandbox, capture_output=True, text=True,
                              encoding="utf-8", env=env)

    def load_module(self):
        loader = importlib.machinery.SourceFileLoader("job_sandbox_copy", str(self.job_path))
        spec = importlib.util.spec_from_file_location("job_sandbox_copy", self.job_path, loader=loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


class RefusedLandTests(SandboxTest):
    def test_conflicting_merge_escalates_to_needs_human(self):  # T1
        self.make_branch(conflict=True)
        before = self.make_job("approve")
        res = self.run_job("merge", JOB_ID)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue(res.stdout.startswith(f"{JOB_ID}: needs-human:"), res.stdout)
        job = self.load_job()
        self.assertEqual(job["stage"], "needs-human")
        self.assertIsNotNone(job["ended"])
        self.assertIsNone(job["passes"][-1]["outcome"])
        decision = self.decision()
        self.assertEqual(decision.split("\n", 1)[0], "ESCALATE")
        self.assertIn("conflicts with main", decision)
        self.assertTrue(self.worktree.is_dir())
        self.assertIn(f"factory/{JOB_ID}", git(self.sandbox, "branch", "--list"))
        self.assertEqual(job["worktree"], before["worktree"])

    def test_gate_failure_after_clean_sync_escalates_to_needs_human(self):  # T2
        self.make_branch(conflict=False)
        self.set_gate(GATE_FAIL)
        self.make_job("approve")
        res = self.run_job("merge", JOB_ID)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(self.load_job()["stage"], "needs-human")
        decision = self.decision()
        self.assertEqual(decision.split("\n", 1)[0], "ESCALATE")
        self.assertIn("The gate failed after syncing", decision)

    def test_merging_to_spec_still_requires_branch_on_main(self):  # T3
        self.make_branch(conflict=True)
        self.make_job("merging")
        before = self.job_bytes()
        passes_before = self.pass_dirs()
        res = self.run_job("advance", JOB_ID, "spec")
        self.assertEqual(res.returncode, 1)
        self.assertIn("isn't on main yet", res.stderr)
        self.assertEqual(self.job_bytes(), before)
        self.assertEqual(self.load_job()["stage"], "merging")
        self.assertEqual(self.pass_dirs(), passes_before)

    def test_merging_to_merged_still_requires_branch_on_main(self):  # T4
        self.make_branch(conflict=True)
        self.make_job("merging")
        before = self.job_bytes()
        res = self.run_job("advance", JOB_ID, "merged")
        self.assertEqual(res.returncode, 1)
        self.assertIn("isn't on main yet", res.stderr)
        self.assertEqual(self.job_bytes(), before)
        self.assertEqual(self.load_job()["stage"], "merging")

    def test_merging_to_merged_allowed_when_branch_on_main(self):  # T5
        self.make_branch(conflict=False)
        self.make_job("merging")
        git(self.sandbox, "merge", "--ff-only", f"factory/{JOB_ID}")
        res = self.run_job("advance", JOB_ID, "merged")
        self.assertEqual(res.returncode, 0, res.stderr)
        job = self.load_job()
        self.assertEqual(job["stage"], "merged")
        self.assertEqual(job["passes"][-1]["outcome"], "merged")

    def test_cli_advance_merging_to_needs_human_still_refused(self):  # T6
        self.make_branch(conflict=True)
        self.make_job("merging")
        job_before = self.job_bytes()
        decision_before = self.decision()
        res = self.run_job("advance", JOB_ID, "needs-human")
        self.assertEqual(res.returncode, 1)
        self.assertIn("isn't on main yet", res.stderr)
        self.assertEqual(self.load_job()["stage"], "merging")
        self.assertEqual(self.job_bytes(), job_before)
        self.assertEqual(self.decision(), decision_before)
        self.assertEqual(self.decision(), "APPROVE\n\n## Summary\nlooks good\n")

    def test_refuse_land_only_runs_from_merging(self):  # T7
        mod = self.load_module()
        self.make_job("approve")
        job = {"id": JOB_ID, "stage": "approve", "ended": None}
        before = self.job_bytes()
        decision_before = self.decision()
        with self.assertRaises(mod.Refused):
            mod.refuse_land(job, "conflict text")
        self.assertEqual(self.decision(), decision_before)
        self.assertEqual(self.job_bytes(), before)
        self.assertEqual(job["stage"], "approve")
        self.assertIsNone(job["ended"])

    def test_refuse_land_has_one_caller_in_cmd_merge(self):  # T8
        tree = ast.parse(self.job_path.read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "refuse_land"]
        self.assertEqual(len(calls), 1, "refuse_land must have exactly one call site")

        # The one call must sit in cmd_merge's `except Refused` handler.
        handlers = [n for n in ast.walk(funcs["cmd_merge"])
                    if isinstance(n, ast.ExceptHandler)
                    and isinstance(n.type, ast.Name) and n.type.id == "Refused"]
        self.assertEqual(len(handlers), 1)
        inside = [c for c in ast.walk(handlers[0]) if c in calls]
        self.assertEqual(len(inside), 1, "refuse_land call must be inside cmd_merge's except Refused")

        # main() must never name refuse_land.
        names = [n for n in ast.walk(funcs["main"])
                 if isinstance(n, ast.Name) and n.id == "refuse_land"]
        self.assertEqual(names, [])

    def test_transition_table_unchanged(self):  # T9
        mod = self.load_module()
        self.assertEqual(mod.TRANSITIONS, EXPECTED_TRANSITIONS)


if __name__ == "__main__":
    unittest.main()
