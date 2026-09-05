#!/usr/bin/env python3
"""Run the repaired formal-head audit and the bounded paragraph comparison."""
from pathlib import Path
import subprocess
import sys


def main():
    here = Path(__file__).resolve().parent
    for script in ("run.py", "joint_passages.py"):
        completed = subprocess.run([sys.executable, "-B", str(here / script), *sys.argv[1:]])
        if completed.returncode:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
