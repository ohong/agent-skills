"""Behavior checks use temporary projects and never alter a user's notes."""

from concurrent.futures import ProcessPoolExecutor
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "take_notes.py"
sys.path.insert(0, str(SCRIPT.parent))
import take_notes as notes


def concurrent_save(arguments):
    directory, index = arguments
    return notes.save(Path(directory), "shared-session", "Concurrent notes", f"Useful item {index}".encode())


class TakeNotesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def run_git(self, cwd, *arguments):
        result = subprocess.run(["git", "-C", str(cwd), *arguments], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_main_and_linked_worktrees_share_one_note(self):
        main = self.root / "main"
        main.mkdir()
        self.run_git(main, "init")
        self.run_git(main, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                     "commit", "--allow-empty", "-m", "Test fixture")
        linked = self.root / "linked"
        self.run_git(main, "worktree", "add", "-b", "linked", str(linked))
        nested = linked / "nested"
        nested.mkdir()
        main_dir = notes.notes_directory(main)
        linked_dir = notes.notes_directory(nested)
        self.assertEqual(main_dir, main / "notes")
        self.assertEqual(main_dir, linked_dir)
        first = notes.save(main_dir, "session", "Worktree learning", b"First learning")
        second = notes.save(linked_dir, "session", "New title", b"Second learning")
        self.assertEqual(first["path"], second["path"])
        self.assertEqual(second["status"], "appended")
        self.assertFalse((linked / "notes").exists())

    def test_later_date_and_title_preserve_filename(self):
        directory = self.root / "notes"
        first = notes.save(directory, "session", "Explore research prompts", b"First", date(2026, 8, 28))
        second = notes.save(directory, "session", "Different title", b"Second", date(2026, 9, 8))
        self.assertEqual(first["path"], second["path"])
        self.assertEqual(Path(first["path"]).name, "2026-08-28-explore-research-prompts.md")

    def test_separate_sessions_with_same_title_do_not_overwrite(self):
        directory = self.root / "notes"
        first = notes.save(directory, "one", "One two three four five six", b"A", date(2026, 8, 28))
        before = Path(first["path"]).read_bytes()
        second = notes.save(directory, "two", "One two three four five six", b"B", date(2026, 8, 28))
        self.assertNotEqual(first["path"], second["path"])
        self.assertEqual(Path(first["path"]).read_bytes(), before)
        self.assertEqual(Path(second["path"]).name, "2026-08-28-one-two-three-four-2.md")
        self.assertEqual(notes.find_note(directory, "two"), Path(second["path"]))

    def test_projectless_and_automatic_fallback(self):
        with patch.object(Path, "home", return_value=self.root / "home"):
            expected = self.root / "home" / "dev" / "notes"
            self.assertEqual(notes.notes_directory(self.root, projectless=True), expected)
            self.assertEqual(notes.notes_directory(self.root), expected)
            result = notes.save(expected, "projectless", "Research notes", b"Keep this")
            self.assertTrue(Path(result["path"]).is_file())

    def test_explicit_non_git_root(self):
        project = self.root / "non-git-project"
        project.mkdir()
        directory = notes.notes_directory(self.root, project_root=project)
        self.assertEqual(directory, project / "notes")
        result = notes.save(directory, "session", "Research notes", b"Keep this")
        self.assertEqual(Path(result["path"]).parent, directory)

    def test_malformed_git_fails_without_fallback(self):
        (self.root / ".git").write_text("gitdir: missing-location\n")
        with self.assertRaisesRegex(ValueError, "Cannot resolve Git project"):
            notes.notes_directory(self.root)
        self.assertFalse((self.root / "notes").exists())

    def test_empty_body_and_bad_titles_do_not_create_directory(self):
        directory = self.root / "notes"
        for body in (b"", b" \n\t"):
            with self.assertRaisesRegex(ValueError, "Body"):
                notes.save(directory, "session", "Valid title", body)
        for title in ("", " \t", "Bad\ntitle", "!!!", "a" * 201):
            with self.assertRaisesRegex(ValueError, "Title"):
                notes.save(directory, "session", title, b"Content")
        self.assertFalse(directory.exists())

    def test_missing_session_fails_and_environment_is_used(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "session ID"):
                notes.session_identity()
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "verified-session"}):
            self.assertEqual(notes.session_identity(), "verified-session")
            self.assertEqual(notes.session_identity("explicit-session"), "explicit-session")

    def test_byte_preserving_append_and_verbatim_prompt(self):
        directory = self.root / "notes"
        original = b"A learning with CRLF.\r\nNo final newline"
        result = notes.save(directory, "session", "Prompt research", original)
        path = Path(result["path"])
        before = path.read_bytes()
        prompt = '```text\nKeep $HOME and $(literal) verbatim.\nDo not omit constraints.\n\n  Preserve spaces.\n```'.encode()
        notes.save(directory, "session", "New title", prompt)
        after = path.read_bytes()
        self.assertEqual(after[:len(before)], before)
        self.assertTrue(after.endswith(prompt))
        self.assertIn(original, after)

    def test_exact_duplicate_is_noop_even_after_other_appends(self):
        directory = self.root / "notes"
        first = notes.save(directory, "session", "Title", b"First payload")
        notes.save(directory, "session", "Title", b"Second payload")
        path = Path(first["path"])
        before = path.read_bytes()
        before_mtime = path.stat().st_mtime_ns
        result = notes.save(directory, "session", "Changed title", b"First payload")
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(path.stat().st_mtime_ns, before_mtime)

    def test_concurrent_saves_keep_all_payloads_in_one_file(self):
        directory = self.root / "notes"
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(concurrent_save, [(str(directory), n) for n in range(8)]))
        self.assertEqual(len({item["path"] for item in results}), 1)
        content = Path(results[0]["path"]).read_bytes()
        for n in range(8):
            self.assertEqual(content.count(f"Useful item {n}".encode()), 1)

    def test_cli_inspect_is_read_only_and_save_uses_body_file(self):
        project = self.root / "project"
        project.mkdir()
        body = self.root / "body.md"
        body.write_text("A useful learning.\n")
        base = [sys.executable, str(SCRIPT)]
        options = ["--project-root", str(project), "--session-id", "verified-session"]
        inspected = subprocess.run(base + ["inspect"] + options, capture_output=True, text=True, check=True)
        self.assertIsNone(json.loads(inspected.stdout)["path"])
        self.assertEqual(list(project.iterdir()), [])
        saved = subprocess.run(base + ["save"] + options + ["--title", "Learning", "--body-file", str(body)],
                               capture_output=True, text=True, check=True)
        saved_path = json.loads(saved.stdout)["path"]
        inspected = subprocess.run(base + ["inspect"] + options, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(inspected.stdout)["path"], saved_path)


if __name__ == "__main__":
    unittest.main()
