"""factory/bin/update: bring an installed factory up to a newer Syntra without losing local work.

Each test builds a fake "Syntra source" folder and a fake "project" folder under a temp directory
and points the module's ROOT/STATE at the project.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REAL_REPO = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("update_bin", str(REAL_REPO / "factory" / "bin" / "update"))
spec = importlib.util.spec_from_loader("update_bin", loader)
update = importlib.util.module_from_spec(spec)
loader.exec_module(update)

MANIFEST = {
    "version": 1,
    "managed": ["factory/bin/job", "start-dashboard.sh"],
    "adapted": ["factory/checks.sh"],
    "merge_json": ["factory/config.json"],
    "executable": ["factory/bin/job"],
}


class UpdateTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="update-test-"))
        self.src = self.tmp / "src"
        self.proj = self.tmp / "proj"
        for d in (self.src, self.proj):
            (d / "factory" / "bin").mkdir(parents=True)
        (self.src / "factory" / "manifest.json").write_text(json.dumps(MANIFEST))
        self.write(self.src, "factory/bin/job", "job v1\n")
        self.write(self.src, "start-dashboard.sh", "dash v1\n")
        self.write(self.src, "factory/checks.sh", "template checks\n")
        self.write(self.src, "factory/config.json", json.dumps({"a": 1, "nested": {"x": 1}}))
        update.ROOT = self.proj
        update.STATE = self.proj / "factory" / ".installed.json"
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def write(self, base, rel, text):
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def text(self, rel):
        return (self.proj / rel).read_text(encoding="utf-8")

    def run_update(self, *flags):
        out = io.StringIO()
        argv = ["update", str(self.src), *flags]
        old = sys.argv
        sys.argv = argv
        try:
            with contextlib.redirect_stdout(out):
                try:
                    update.main()
                except SystemExit as e:
                    out.write(f"EXIT:{e.code}")
        finally:
            sys.argv = old
        return out.getvalue()

    def install(self):
        for rel in ("factory/bin/job", "start-dashboard.sh", "factory/checks.sh", "factory/config.json"):
            self.write(self.proj, rel, (self.src / rel).read_text(encoding="utf-8"))
        self.run_update("--adopt")

    def test_dry_run_changes_nothing(self):
        self.install()
        self.write(self.src, "factory/bin/job", "job v2\n")
        out = self.run_update()
        self.assertIn("update   factory/bin/job", out)
        self.assertIn("Dry run", out)
        self.assertEqual(self.text("factory/bin/job"), "job v1\n")

    def test_apply_updates_unedited_managed_files(self):
        self.install()
        self.write(self.src, "factory/bin/job", "job v2\n")
        self.run_update("--apply")
        self.assertEqual(self.text("factory/bin/job"), "job v2\n")
        state = json.loads(update.STATE.read_text())
        self.assertEqual(state["managed"]["factory/bin/job"], update.digest(b"job v2\n"))

    def test_edited_managed_file_is_skipped_unless_forced(self):
        self.install()
        self.write(self.proj, "factory/bin/job", "my local edit\n")
        self.write(self.src, "factory/bin/job", "job v2\n")
        out = self.run_update("--apply")
        self.assertIn("EDITED", out)
        self.assertEqual(self.text("factory/bin/job"), "my local edit\n")
        self.run_update("--apply", "--force")
        self.assertEqual(self.text("factory/bin/job"), "job v2\n")

    def test_adapted_file_is_never_overwritten(self):
        self.install()
        self.write(self.proj, "factory/checks.sh", "my real checks\n")
        self.write(self.src, "factory/checks.sh", "template checks v2\n")
        out = self.run_update("--apply")
        self.assertIn("review  factory/checks.sh", out)
        self.assertEqual(self.text("factory/checks.sh"), "my real checks\n")

    def test_missing_adapted_file_is_added_from_template(self):
        self.install()
        (self.proj / "factory/checks.sh").unlink()
        self.run_update("--apply")
        self.assertEqual(self.text("factory/checks.sh"), "template checks\n")

    def test_new_managed_file_is_added(self):
        self.install()
        (self.proj / "start-dashboard.sh").unlink()
        self.run_update("--apply")
        self.assertEqual(self.text("start-dashboard.sh"), "dash v1\n")

    def test_config_gets_new_keys_but_keeps_local_values(self):
        self.install()
        self.write(self.proj, "factory/config.json", json.dumps({"a": 99, "nested": {}}))
        self.write(self.src, "factory/config.json",
                   json.dumps({"a": 1, "b": 2, "nested": {"x": 1, "y": 2}}))
        self.run_update("--apply")
        cfg = json.loads(self.text("factory/config.json"))
        self.assertEqual(cfg, {"a": 99, "nested": {"x": 1, "y": 2}, "b": 2})

    def test_crlf_checkout_counts_as_unedited(self):
        self.install()
        (self.proj / "factory/bin/job").write_bytes(b"job v1\r\n")
        self.write(self.src, "factory/bin/job", "job v2\n")
        self.run_update("--apply")
        self.assertEqual(self.text("factory/bin/job"), "job v2\n")

    def test_running_jobs_block_apply(self):
        self.install()
        job = self.proj / "factory" / "jobs" / "001-x"
        job.mkdir(parents=True)
        (job / "job.json").write_text(json.dumps({"stage": "build"}))
        self.write(self.src, "factory/bin/job", "job v2\n")
        out = self.run_update("--apply")
        self.assertIn("EXIT:", out)
        self.assertEqual(self.text("factory/bin/job"), "job v1\n")
        self.run_update("--apply", "--force")
        self.assertEqual(self.text("factory/bin/job"), "job v2\n")

    def test_finished_jobs_do_not_block(self):
        self.install()
        job = self.proj / "factory" / "jobs" / "001-x"
        job.mkdir(parents=True)
        (job / "job.json").write_text(json.dumps({"stage": "merged"}))
        self.write(self.src, "factory/bin/job", "job v2\n")
        self.run_update("--apply")
        self.assertEqual(self.text("factory/bin/job"), "job v2\n")

    def test_source_must_not_be_the_project(self):
        out = io.StringIO()
        sys.argv = ["update", str(self.proj)]
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            update.main()

    def test_manifest_rejects_paths_into_job_state(self):
        bad = dict(MANIFEST, managed=["factory/jobs/001/job.json"])
        (self.src / "factory" / "manifest.json").write_text(json.dumps(bad))
        out = self.run_update()
        self.assertIn("not allowed", out)

    def test_real_manifest_lists_files_that_exist(self):
        manifest = json.loads((REAL_REPO / "factory" / "manifest.json").read_text(encoding="utf-8"))
        for key in ("managed", "adapted", "merge_json", "executable"):
            for rel in manifest[key]:
                self.assertTrue((REAL_REPO / rel).exists(), f"{key}: {rel} is missing")


if __name__ == "__main__":
    unittest.main()
