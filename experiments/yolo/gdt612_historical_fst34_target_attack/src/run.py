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
    source = Path(__file__).resolve().parent
    for name in (
        "oracle_objective_audit.py",
        "method_audit.py",
        "validate.py",
        "build_compact_manifest.py",
    ):
        result = subprocess.run([sys.executable, str(source / name)], cwd=ROOT)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
