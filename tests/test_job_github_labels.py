"""GitHub labels and the reject comment: factory/bin/job's merge and reject paths.

A final merge adds `factory-done` to the linked issue. A reject posts the reason as
a comment and adds `factory-rejected`. Every `gh` call is best-effort and must never
change the outcome of a merge or a reject.

Each test runs in a throwaway git repository. The module globals that point into the
real checkout are replaced, the usage ingest is a no-op, and PATH holds only a temp
bin directory with a stub `gh` (when the test wants one) and a `git` symlink. The real
`gh` is never reachable from these tests, and nothing touches the network.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REAL_REPO = Path(__file__).resolve().parents[1]
MODULE_NAME = "job_github_labels_under_test"
loader = importlib.machinery.SourceFileLoader(MODULE_NAME, str(REAL_REPO / "factory" / "bin" / "job"))
spec = importlib.util.spec_from_loader(MODULE_NAME, loader)
job = importlib.util.module_from_spec(spec)
loader.exec_module(job)

GH_STUB_OUTPUT = "GH-STUB-OUTPUT must never reach the job's output"
REASON = 'Not wanted: "quotes", $HOME, `ticks`\n- a leading dash line\nlast line'
GH_STUB = f"""import json, os, sys
argv = sys.argv[1:]
stdin = sys.stdin.read() if "--body-file" in argv else ""
with open(os.environ["GH_STUB_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps({{"argv": argv, "stdin": stdin}}) + "\\n")
mode = os.environ.get("GH_STUB_MODE", "ok")
labels_path = os.environ["GH_STUB_LABELS"]
with open(labels_path, encoding="utf-8") as f:
    labels = set(f.read().split())
print("{GH_STUB_OUTPUT}")
print("{GH_STUB_OUTPUT}", file=sys.stderr)
if mode == "fail":
    sys.exit(1)
if argv[:2] == ["issue", "edit"] and "--add-label" in argv:
    if argv[argv.index("--add-label") + 1] not in labels:
        sys.exit(1)
    sys.exit(0)
if argv[:2] == ["label", "create"]:
    labels.add(argv[2])
    with open(labels_path, "w", encoding="utf-8") as f:
        f.write("\\n".join(sorted(labels)) + "\\n")
    sys.exit(0)
sys.exit(0)
"""


@unittest.skipIf(os.name == "nt", "the stub gh is a script that needs a POSIX shebang")
class GitHubLabelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="job-github-labels-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        factory = self.repo / "factory"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.log = self.tmp / "gh-calls.jsonl"
        self.labels = self.tmp / "labels.txt"
        self.labels.write_text("")

        for name, value in {"REPO": self.repo, "FACTORY": factory, "JOBS": factory / "jobs",
                            "INBOX": factory / "inbox", "RECORDS": factory / "records",
                            "BIN": self.bin}.items():
            self.patch(name, value)
        self.patch("ingest_usage", lambda: None)
        self.patch("usage_by_step", lambda j: [])
        self.patch("land", self.fake_land)

        # Set up the repository with the normal PATH, then narrow PATH for the test body.
        git_path = shutil.which("git")
        self.assertIsNotNone(git_path, "git is needed to run these tests")
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test Builder")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.repo / ".gitignore").write_text("/factory/jobs/\n/factory/inbox/\n/.worktrees/\n")
        (self.repo / "README.md").write_text("base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")

        os.symlink(git_path, self.bin / "git")
        env = dict(os.environ, PATH=str(self.bin), GH_STUB_LOG=str(self.log),
                   GH_STUB_LABELS=str(self.labels), GH_STUB_MODE="ok")
        patcher = mock.patch.dict(os.environ, env, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.close_locks)

    def close_locks(self):
        for lock in list(job._locks.values()):
            lock.close()
        job._locks.clear()

    def patch(self, name, value):
        original = getattr(job, name)
        setattr(job, name, value)
        self.addCleanup(setattr, job, name, original)

    def fake_land(self, j, record=False):
        """Stand-in for land(): fast-forward base to the job branch. No gate, no record."""
        self.git("merge", "--ff-only", j["branch"])

    def install_gh(self, mode="ok", labels=()):
        """Write the stub gh into the bin directory and set how it behaves."""
        stub = self.bin / "gh"
        stub.write_text(f"#!{os.path.abspath(sys.executable)}\n" + GH_STUB)
        stub.chmod(0o755)
        self.labels.write_text("".join(f"{name}\n" for name in labels))
        os.environ["GH_STUB_MODE"] = mode

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.strip()

    def gh_calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def make_job(self, line="docs", stage="merging", job_id="001-new-topic", topic="new-topic",
                 topic_text=None):
        """A job with its own worktree, one commit of work, and an approved decision."""
        job.INBOX.mkdir(parents=True, exist_ok=True)
        if topic_text is None:
            topic_text = "<!-- factory-issue: 7 -->\n# Add a thing\n\nBody text.\n"
        (job.INBOX / f"{topic}.md").write_text(topic_text, encoding="utf-8")
        worktree = self.repo / ".worktrees" / job_id
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
            "triage": {"decision": "ACCEPT", "line": line, "rescoped": False, "risk": "low", "surfaces": []},
            "agents": {"reviewers": {}}, "gate": None, "reviews": {},
            "cost_usd": 0.0, "models": [],
            "started": "2026-11-24T10:00:00Z", "ended": None,
        }
        job.job_dir(job_id).mkdir(parents=True, exist_ok=True)
        pdir = job.pass_dir(j)
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "decision.md").write_text("APPROVE\n\n## Summary\n\nLooks good.\n", encoding="utf-8")
        job.save(j)
        return j

    def read_job(self, job_id):
        return json.loads((job.job_dir(job_id) / "job.json").read_text(encoding="utf-8"))

    def quiet(self, fn, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn(*args)
        return out.getvalue() + err.getvalue()

    def label_calls(self, label):
        return [c for c in self.gh_calls() if label in c["argv"]]


class MergeLabelTests(GitHubLabelTests):
    def test_missing_label_is_created_then_applied(self):
        self.install_gh(labels=())
        j = self.make_job(line="docs", stage="merging")
        self.quiet(job.cmd_merge, j)
        argvs = [c["argv"] for c in self.gh_calls()]
        create = ["label", "create", "factory-done", "--description", "Merged into the base branch by the factory"]
        add = ["issue", "edit", "7", "--add-label", "factory-done"]
        self.assertIn(create, argvs)
        self.assertNotIn("--force", argvs[argvs.index(create)])
        self.assertLess(argvs.index(create), len(argvs) - 1)
        self.assertEqual(argvs[-1], add, "the retry of the add is the last label call")
        self.assertEqual(argvs.count(add), 2)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "merged")

    def test_existing_label_is_applied_without_create(self):
        self.install_gh(labels=("factory-done",))
        j = self.make_job(line="docs", stage="merging")
        self.quiet(job.cmd_merge, j)
        argvs = [c["argv"] for c in self.gh_calls()]
        self.assertNotIn(["label", "create"], [a[:2] for a in argvs])
        self.assertEqual(argvs.count(["issue", "edit", "7", "--add-label", "factory-done"]), 1)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "merged")

    def test_handoff_merge_makes_no_github_call(self):
        self.install_gh(labels=("factory-done",))
        j = self.make_job(line="build", stage="merging")
        self.quiet(job.cmd_merge, j)
        self.assertEqual(self.gh_calls(), [])
        reloaded = self.read_job("001-new-topic")
        self.assertEqual(reloaded["stage"], "spec")
        self.assertEqual(reloaded["line"], "docs")

    def test_final_merge_keeps_comment_and_close_before_label(self):
        self.install_gh(labels=("factory-done",))
        j = self.make_job(line="docs", stage="merging")
        self.quiet(job.cmd_merge, j)
        argvs = [c["argv"] for c in self.gh_calls()]
        self.assertEqual([a[:3] for a in argvs[:2]], [["issue", "comment", "7"], ["issue", "close", "7"]])
        self.assertEqual(argvs[2], ["issue", "edit", "7", "--add-label", "factory-done"])
        self.assertEqual(self.read_job("001-new-topic")["stage"], "merged")

    def test_missing_gh_does_not_change_merge(self):
        j = self.make_job(line="docs", stage="merging")
        self.assertIsNone(shutil.which("gh", path=str(self.bin)))
        self.quiet(job.cmd_merge, j)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "merged")

    def test_failing_gh_does_not_change_merge_or_leak_output(self):
        self.install_gh(mode="fail", labels=())
        j = self.make_job(line="docs", stage="merging")
        output = self.quiet(job.cmd_merge, j)
        self.assertTrue(self.gh_calls(), "gh must have been called, or the test proves nothing")
        self.assertEqual(self.read_job("001-new-topic")["stage"], "merged")
        self.assertNotIn(GH_STUB_OUTPUT, output)


class RejectLabelTests(GitHubLabelTests):
    def test_reject_comment_contains_the_actual_reason(self):
        self.install_gh(labels=("factory-rejected",))
        j = self.make_job(line="docs", stage="needs-human")
        self.quiet(job.cmd_reject, j, REASON)
        calls = self.gh_calls()
        comment = [c for c in calls if c["argv"][:2] == ["issue", "comment"]]
        self.assertEqual(len(comment), 1)
        self.assertEqual(comment[0]["argv"], ["issue", "comment", "7", "--body-file", "-"])
        self.assertEqual(comment[0]["stdin"], f"Factory: rejected.\n\nReason from the operator:\n\n{REASON}\n")
        for c in calls:
            self.assertNotIn(REASON, " ".join(c["argv"]), "the reason must never be in argv")
        self.assertEqual(calls[-1]["argv"], ["issue", "edit", "7", "--add-label", "factory-rejected"])
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")

    def test_reject_without_marker_makes_no_github_call(self):
        self.install_gh(labels=())
        j = self.make_job(line="docs", stage="needs-human", topic_text="# Add a thing\n\nBody.\n")
        self.quiet(job.cmd_reject, j, REASON)
        self.assertEqual(self.gh_calls(), [])
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")

    def test_reject_with_missing_topic_file_does_not_raise(self):
        self.install_gh(labels=())
        j = self.make_job(line="docs", stage="needs-human")
        (job.INBOX / "new-topic.md").unlink()
        self.quiet(job.cmd_reject, j, REASON)
        self.assertEqual(self.gh_calls(), [])
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")

    def test_reject_with_empty_topic_file_does_not_raise(self):
        self.install_gh(labels=())
        j = self.make_job(line="docs", stage="needs-human", topic_text="")
        self.quiet(job.cmd_reject, j, REASON)
        self.assertEqual(self.gh_calls(), [])
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")

    def test_missing_gh_does_not_change_reject(self):
        j = self.make_job(line="docs", stage="needs-human")
        self.assertIsNone(shutil.which("gh", path=str(self.bin)))
        self.quiet(job.cmd_reject, j, REASON)
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")

    def test_failing_gh_does_not_change_reject_or_leak_output(self):
        self.install_gh(mode="fail", labels=())
        j = self.make_job(line="docs", stage="needs-human")
        output = self.quiet(job.cmd_reject, j, REASON)
        self.assertTrue(self.gh_calls(), "gh must have been called, or the test proves nothing")
        self.assertEqual(self.read_job("001-new-topic")["stage"], "rejected")
        self.assertNotIn(GH_STUB_OUTPUT, output)


if __name__ == "__main__":
    unittest.main()
