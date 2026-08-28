#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def main() -> int:
    experiment = Path(__file__).resolve().parents[1]
    analyze = experiment / "src" / "analyze.py"
    validate = experiment / "src" / "validate.py"
    first = subprocess.run([sys.executable, str(analyze)], cwd=ROOT).returncode
    if first:
        return first
    return subprocess.run([sys.executable, str(validate)], cwd=ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())
