#!/usr/bin/env python3
"""Resolve and append a session note without rewriting existing bytes."""

import argparse
from contextlib import contextmanager
from datetime import date
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata


SESSION_PREFIX = b"<!-- take-notes-session: "


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, check=False
    )


def notes_directory(cwd, project_root=None, projectless=False):
    if projectless:
        return Path.home() / "dev" / "notes"
    start = Path(project_root or cwd).expanduser().resolve()
    if not start.is_dir():
        raise ValueError(f"Project directory does not exist: {start}")
    probe = git(start, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if probe.returncode:
        has_marker = any((p / ".git").exists() or (p / ".git").is_symlink()
                         for p in (start, *start.parents))
        # Only Git's explicit not-a-repository result permits the non-Git route.
        if has_marker or "not a git repository" not in probe.stderr.lower():
            raise ValueError(f"Cannot resolve Git project: {probe.stderr.strip()}")
        return start / "notes" if project_root else Path.home() / "dev" / "notes"
    common = Path(probe.stdout.strip()).resolve()
    listing = git(start, "worktree", "list", "--porcelain", "-z")
    if listing.returncode:
        raise ValueError(f"Cannot list Git worktrees: {listing.stderr.strip()}")
    # The main checkout uses the common Git directory directly. Linked
    # worktrees use a child directory under common/worktrees instead.
    for field in listing.stdout.split("\0"):
        if not field.startswith("worktree "):
            continue
        checkout = Path(field[len("worktree "):])
        result = git(checkout, "rev-parse", "--absolute-git-dir")
        bare = git(checkout, "rev-parse", "--is-bare-repository")
        if (result.returncode == 0 and bare.returncode == 0
                and bare.stdout.strip() == "false"
                and Path(result.stdout.strip()).resolve() == common):
            return checkout.resolve() / "notes"
    raise ValueError("Cannot locate the main Git checkout; supply a valid project location.")


def session_identity(explicit=None):
    identity = explicit if explicit is not None else os.environ.get("CODEX_THREAD_ID", "")
    if (not identity.strip() or len(identity) > 256
            or any(ord(char) < 32 for char in identity)):
        raise ValueError("A nonempty stable session ID is required (CODEX_THREAD_ID or --session-id).")
    return identity


def session_header(identity):
    return SESSION_PREFIX + json.dumps(identity, ensure_ascii=True).encode() + b" -->\n"


def find_note(directory, identity):
    matches = []
    if directory.exists():
        for path in sorted(directory.glob("*.md")):
            with path.open("rb") as source:
                if source.readline() == session_header(identity):
                    matches.append(path)
    if len(matches) > 1:
        raise ValueError("Multiple notes have this session ID; resolve the duplicate files before saving.")
    return matches[0] if matches else None


def title_slug(title):
    if not title.strip() or len(title) > 200 or any(ord(char) < 32 for char in title):
        raise ValueError("Title must be nonempty, one line, and at most 200 characters.")
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", ascii_title.lower())[:5]
    if not words:
        raise ValueError("Title must contain a letter or digit usable in the filename.")
    return "-".join(words)


@contextmanager
def save_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    # All writers recheck session identity while holding this shared lock.
    with (directory / ".take-notes.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield


def save(directory, identity, title, body, today=None):
    slug = title_slug(title)
    if not body.strip():
        raise ValueError("Body must contain useful, nonempty text.")
    body.decode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    marker = f"<!-- take-notes-payload-sha256: {digest} -->\n".encode()
    with save_lock(directory):
        path = find_note(directory, identity)
        existing = path.read_bytes() if path else b""
        if marker in existing.splitlines(keepends=True):
            return {"status": "unchanged", "path": str(path)}
        if path is None:
            stamp = (today or date.today()).isoformat()
            path = directory / f"{stamp}-{slug}.md"
            suffix = 2
            while path.exists():
                # A numeric disambiguator counts toward the five-word limit.
                short_slug = "-".join(slug.split("-")[:4])
                path = directory / f"{stamp}-{short_slug}-{suffix}.md"
                suffix += 1
            prefix = session_header(identity) + f"# {title.strip()}\n\n".encode()
            mode = "xb"
        else:
            prefix = b"\n\n"
            mode = "ab"
        with path.open(mode) as target:
            target.write(prefix + marker + body)
            target.flush()
            os.fsync(target.fileno())
        return {"status": "created" if not existing else "appended", "path": str(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "save"):
        command = commands.add_parser(name)
        root = command.add_mutually_exclusive_group()
        root.add_argument("--project-root", type=Path, help="Known project root, including non-Git projects")
        root.add_argument("--projectless", action="store_true", help="Use ~/dev/notes")
        command.add_argument("--session-id", help="Verified stable ID; otherwise use CODEX_THREAD_ID")
        if name == "save":
            command.add_argument("--title", required=True)
            command.add_argument("--body-file", type=Path, required=True)
    args = parser.parse_args()
    try:
        identity = session_identity(args.session_id)
        directory = notes_directory(Path.cwd(), args.project_root, args.projectless)
        if args.command == "inspect":
            path = find_note(directory, identity)
            result = {"notes_dir": str(directory), "path": str(path) if path else None,
                      "session_id": identity}
        else:
            result = save(directory, identity, args.title, args.body_file.read_bytes())
        print(json.dumps(result))
    except (ValueError, OSError, UnicodeError) as error:
        print(f"take-notes: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
