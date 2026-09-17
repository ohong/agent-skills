"""Run: python3 -m unittest discover -s /absolute/skill-directory/scripts -v"""

import os
import json
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

from inventory import Inventory


class WorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cleanup fixture ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "main checkout"
        self.env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
        self.env_patch = patch.dict(os.environ, self.env)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.git(self.root, "init", "--initial-branch=main", str(self.repo))
        (self.repo / "tracked").write_text("base\n")
        (self.repo / ".gitignore").write_text(".env\n")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "base")

    def git(self, repo, *args):
        return subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                               "-c", "core.hooksPath=/dev/null", "-C", str(repo), *args],
                              env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    def worktree(self, name, detached=False):
        path = self.root / name
        self.git(self.repo, "worktree", "add", *( ["--detach"] if detached else ["-b", name.replace(" ", "-")] ), str(path))
        return path

    def inspect(self, path):
        report = Inventory().repository(str(self.repo))
        self.assertNotIn("error", report)
        self.assertNotIn("list_error", report)
        return next(item for item in report["worktrees"] if item["path"] == str(path))

    def test_dirty_untracked_and_ignored_paths_with_spaces(self):
        path = self.worktree("dirty with spaces")
        (path / "tracked").write_text("staged\n")
        self.git(path, "add", "tracked")
        (path / "tracked").write_text("unstaged\n")
        (path / "new file").write_text("untracked")
        (path / ".env").write_text("fixture-local-data")
        item = self.inspect(path)
        self.assertEqual({s["path"]: s["code"] for s in item["status"]},
                         {"tracked": "MM", "new file": "??", ".env": "!!"})
        self.assertTrue(item["review_required"])
        self.assertFalse(item["main_worktree"])
        self.assertGreater(item["size"]["allocated_bytes"], 0)

    def test_clean_unique_branch_requires_review_and_excludes_own_ref(self):
        path = self.worktree("unique branch")
        (path / "tracked").write_text("unique\n")
        self.git(path, "commit", "-am", "unique")
        item = self.inspect(path)
        self.assertEqual(item["status"], [])
        self.assertEqual(item["other_local_refs_containing_head"], [])
        self.assertEqual(item["branch"], "refs/heads/unique-branch")
        self.assertTrue(item["review_required"])
        self.git(path, "tag", "retained")
        self.assertEqual(self.inspect(path)["other_local_refs_containing_head"], ["refs/tags/retained"])

    def test_detached_unique_commit_and_rename(self):
        path = self.worktree("detached checkout", detached=True)
        (path / "tracked").write_text("detached\n")
        self.git(path, "commit", "-am", "detached")
        item = self.inspect(path)
        self.assertTrue(item["detached"])
        self.assertIsNone(item["branch"])
        self.assertEqual(item["other_local_refs_containing_head"], [])
        self.git(path, "mv", "tracked", "renamed file")
        self.assertIn({"code": "R ", "path": "renamed file", "original_path": "tracked"}, self.inspect(path)["status"])

    def test_missing_locked_and_prunable_are_evidence_not_verdicts(self):
        locked = self.worktree("locked checkout")
        self.git(self.repo, "worktree", "lock", "--reason", "external drive fixture", str(locked))
        locked.rename(self.root / "retained locked files")
        item = self.inspect(locked)
        self.assertTrue(item["locked"])
        self.assertEqual(item["lock_reason"], "external drive fixture")
        self.assertTrue(item["missing"])
        self.assertIsNone(item["status"])
        self.assertIn("error", item["size"])
        missing = self.worktree("missing checkout")
        missing.rename(self.root / "retained missing files")
        item = self.inspect(missing)
        self.assertTrue(item["missing"])
        self.assertTrue(item["prunable"])
        self.assertTrue(item["review_required"])


class SizeAndFailureTests(unittest.TestCase):
    def test_explicit_sizes_symlinks_and_overlap_have_no_aggregate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            child = root / "child space"
            child.mkdir()
            (child / "data").write_bytes(b"x" * 8192)
            (root / "link").symlink_to(child, target_is_directory=True)
            inventory = Inventory()
            self.assertGreater(inventory.size(str(child))["allocated_bytes"], 0)
            self.assertIn("error", inventory.size(str(root / "link")))
            self.assertIn("error", inventory.size(str(root / "link" / "data")))
            self.assertIsNone(inventory.size(str(root / "missing"))["allocated_bytes"])
            measured = inventory.size(str(root))
            self.assertNotIn("total_bytes", measured)
            self.assertGreater(measured["volume"]["available_bytes"], 0)

    def test_du_failure_preserves_partial_output_and_unknown_size(self):
        with tempfile.TemporaryDirectory() as directory:
            failure = subprocess.CompletedProcess([], 1, b"12\tpartial\n", b"Permission denied")
            with patch("inventory.subprocess.run", return_value=failure):
                item = Inventory().size(str(Path(directory).resolve()))
            self.assertIsNone(item["allocated_bytes"])
            self.assertEqual(item["size_error"]["stderr"], "Permission denied")
            self.assertEqual(item["size_error"]["exit_code"], 1)

    def test_timeouts_budget_and_read_only_git_environment(self):
        with patch("inventory.subprocess.run", side_effect=subprocess.TimeoutExpired(["du"], 1, b"partial", b"error")):
            result = Inventory().run(["du", "-skP", "/fixture"])
        self.assertEqual(result["error"], "command timed out")
        self.assertEqual(result["stdout"], "partial")
        inventory = Inventory()
        inventory.deadline = 0
        self.assertEqual(inventory.run(["git"])["error"], "total scan budget exhausted")
        with patch("inventory.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"", b"")) as call:
            Inventory().git("/fixture with spaces", "status", "--porcelain=v1")
        args, kwargs = call.call_args
        self.assertEqual(args[0][:5], ["git", "-c", "core.fsmonitor=false", "-C", "/fixture with spaces"])
        self.assertEqual(kwargs["env"]["GIT_OPTIONAL_LOCKS"], "0")
        self.assertLessEqual(kwargs["timeout"], 10)

    def test_git_failure_is_not_empty_worktree_list(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Inventory().repository(str(Path(directory).resolve()))
        self.assertIn("list_error", report)
        self.assertNotEqual(report["list_error"]["exit_code"], 0)

    def test_cli_requires_explicit_scope_and_reports_errors(self):
        script = str(Path(__file__).with_name("inventory.py"))
        rejected = subprocess.run([sys.executable, script], capture_output=True, text=True)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("supply at least one", rejected.stderr)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            result = subprocess.run([sys.executable, script, "--path", str(root),
                                     "--path", str(root / "missing")], capture_output=True, text=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(len(report["paths"]), 2)
        self.assertIsNone(report["paths"][1]["allocated_bytes"])
        self.assertIn("error", report["paths"][1])
        self.assertNotIn("total_bytes", report)

    def test_internal_symlink_target_is_not_measured(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            target = root / "measured"
            target.mkdir()
            (root / "outside").write_bytes(b"x" * (2 * 1024 * 1024))
            (target / "link").symlink_to(root / "outside")
            self.assertLess(Inventory().size(str(target))["allocated_bytes"], 128 * 1024)


if __name__ == "__main__":
    unittest.main()
