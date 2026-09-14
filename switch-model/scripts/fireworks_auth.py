#!/usr/bin/python3
"""Codex command-backed credential reader. Never invoke without --check in tool output."""
import argparse
import os
from pathlib import Path
import stat
import subprocess
import sys


def credential():
    value = os.environ.get('FIREWORKS_API_KEY', '').strip()
    if value:
        return value
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    path = Path(os.environ.get('FIREWORKS_API_KEY_FILE', str(home / 'credentials/fireworks-api-key'))).expanduser()
    if path.exists():
        if path.is_symlink() or not path.is_file():
            raise ValueError('Fireworks credential must be a regular, non-symlink file.')
        metadata = path.stat()
        if metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError('Fireworks credential file must belong to you and have mode 0600.')
        value = path.read_text().strip()
        if value:
            return value
    try:
        result = subprocess.run(['/usr/bin/security', 'find-generic-password', '-s', 'codex-fireworks-api-key', '-w'], capture_output=True, text=True, timeout=8)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    raise ValueError('Fireworks credential unavailable. Set FIREWORKS_API_KEY, store a mode-0600 credential file, or add Keychain service codex-fireworks-api-key.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report availability without revealing the key.')
    args = parser.parse_args()
    try:
        value = credential()
        if any(char.isspace() for char in value):
            raise ValueError('Fireworks credential contains whitespace.')
        print('Fireworks credential available.' if args.check else value)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
