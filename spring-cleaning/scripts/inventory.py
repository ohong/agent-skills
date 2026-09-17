#!/usr/bin/env python3
"""Read-only, explicitly scoped disk and Git worktree evidence. Python stdlib only."""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time


def path_error(path):
    """Reject symlinks in the supplied path, including ancestor components."""
    for part in [*reversed(path.parents), path]:
        if part.is_symlink():
            return f"symlink path refused: {part}"
    try:
        path.stat()
    except OSError as exc:
        return str(exc)
    return None


class Inventory:
    def __init__(self, timeout=10.0, budget=120.0):
        self.timeout = timeout
        self.deadline = time.monotonic() + budget

    def run(self, args):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            return {"error": "total scan budget exhausted", "command": args}
        env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"}
        try:
            result = subprocess.run(args, capture_output=True, timeout=min(self.timeout, remaining), env=env)
        except subprocess.TimeoutExpired as exc:
            return {"error": "command timed out", "command": args,
                    "stdout": (exc.stdout or b"").decode(errors="replace"),
                    "stderr": (exc.stderr or b"").decode(errors="replace")}
        except OSError as exc:
            return {"error": str(exc), "command": args}
        output = {"stdout": result.stdout.decode(errors="surrogateescape"),
                  "stderr": result.stderr.decode(errors="surrogateescape")}
        if result.returncode:
            output.update(error="command failed", exit_code=result.returncode, command=args)
        return output

    def git(self, repo, *args):
        return self.run(["git", "-c", "core.fsmonitor=false", "-C", str(repo), *args])

    def size(self, supplied):
        path = Path(os.path.abspath(os.path.expanduser(supplied)))
        result = {"path": str(path), "review_required": True, "allocated_bytes": None}
        error = path_error(path)
        if error:
            result["error"] = error
            return result
        try:
            usage = shutil.disk_usage(path)
            result["volume"] = {"device": path.stat().st_dev, "total_bytes": usage.total,
                                "available_bytes": usage.free}
        except OSError as exc:
            result["volume_error"] = str(exc)
        # Stay on this filesystem and avoid symlink traversal or option-like operands.
        command = self.run(["du", "-skPx", str(path)])
        if "error" in command:
            result["size_error"] = command
        else:
            try:
                result["allocated_bytes"] = int(command["stdout"].split("\t", 1)[0]) * 1024
            except (ValueError, IndexError):
                result["size_error"] = {"error": "unrecognized du output", **command}
            if command["stderr"]:
                result["size_warning"] = command["stderr"]
        return result

    def repository(self, supplied):
        repo = Path(os.path.abspath(os.path.expanduser(supplied)))
        result = {"repository": str(repo), "review_required": True, "worktrees": []}
        error = path_error(repo)
        if error:
            result["error"] = error
            return result
        listing = self.git(repo, "worktree", "list", "--porcelain", "-z")
        if "error" in listing:
            result["list_error"] = listing
            return result
        if listing["stderr"]:
            result["list_warning"] = listing["stderr"]
        for index, record in enumerate(parse_worktrees(listing["stdout"])):
            path = record["worktree"]
            item = {"path": path, "review_required": True, "main_worktree": index == 0,
                    "head": record.get("HEAD"), "branch": record.get("branch"),
                    "detached": "detached" in record, "bare": "bare" in record,
                    "locked": "locked" in record, "lock_reason": record.get("locked"),
                    "prunable": "prunable" in record, "prunable_reason": record.get("prunable"),
                    "missing": not os.path.lexists(path), "activity": "unknown",
                    "current_directory_within": os.path.commonpath([os.getcwd(), path]) == path,
                    "status": None, "other_local_refs_containing_head": None,
                    "remote_freshness": "unknown"}
            item["size"] = self.size(path)
            if not item["bare"] and "error" not in item["size"]:
                status = self.git(path, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored")
                if "error" in status:
                    item["status_error"] = status
                else:
                    item["status"] = parse_status(status["stdout"])
                    if status["stderr"]:
                        item["status_warning"] = status["stderr"]
            if item["head"] and set(item["head"]) != {"0"}:
                refs = self.git(repo, "for-each-ref", f"--contains={item['head']}",
                                "--format=%(refname)", "refs/heads/", "refs/tags/")
                if "error" in refs:
                    item["refs_error"] = refs
                else:
                    item["other_local_refs_containing_head"] = [
                        ref for ref in refs["stdout"].splitlines() if ref != item["branch"]]
                    if refs["stderr"]:
                        item["refs_warning"] = refs["stderr"]
            result["worktrees"].append(item)
        return result


def parse_worktrees(output):
    records, current = [], {}
    for field in output.split("\0"):
        if not field:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = field.partition(" ")
        current[key] = value
    if current:
        records.append(current)
    return records


def parse_status(output):
    records, fields = [], iter(output.split("\0"))
    for field in fields:
        if not field:
            continue
        item = {"code": field[:2], "path": field[3:]}
        if "R" in item["code"] or "C" in item["code"]:
            item["original_path"] = next(fields)
        records.append(item)
    return records


def positive_seconds(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be positive finite seconds")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", default=[], help="Exact file or directory to measure; repeatable")
    parser.add_argument("--repo", action="append", default=[], help="Repository whose registered worktrees to inspect; repeatable")
    parser.add_argument("--timeout", type=positive_seconds, default=10, help="Seconds per command (default: 10)")
    parser.add_argument("--budget", type=positive_seconds, default=120, help="Total subprocess time budget in seconds (default: 120)")
    args = parser.parse_args()
    if not args.path and not args.repo:
        parser.error("supply at least one --path or --repo; no default scan")
    inventory = Inventory(args.timeout, args.budget)
    output = {"review_required": True, "limits": {"command_seconds": args.timeout, "budget_seconds": args.budget},
              "limitations": ["Sizes are not reclaimable bytes; no aggregate total is calculated.",
                              "Inputs and worktrees can overlap; APFS/shared blocks and snapshots affect recovery.",
                              "Symlink paths are refused; du does not follow internal symlinks.",
                              "du skips nested filesystems; directory estimates exclude their contents.",
                              "Activity, remote freshness, backups, and recoverability remain unknown.",
                              "Git refs are local branches and tags; own branch is excluded; no fetch occurs.",
                              "Status is not a recursive submodule audit and evidence can change after inspection.",
                              "Filesystem metadata calls are not covered by subprocess timeouts."],
              "paths": [inventory.size(path) for path in args.path],
              "repositories": [inventory.repository(repo) for repo in args.repo]}
    print(json.dumps(output, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
