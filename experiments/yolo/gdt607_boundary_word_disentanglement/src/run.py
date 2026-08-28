#!/usr/bin/env python3
"""Run the GDT607 boundary-versus-whole-word capacity grid."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
SRC = Path(__file__).resolve().parent


def main() -> int:
    subprocess.run(
        [sys.executable, str(SRC / "context_role_attack.py")], cwd=ROOT, check=True
    )
    with tempfile.TemporaryDirectory(prefix="gdt607-references-") as temporary:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "experiments/yolo/gdt604_naibbe_frozen_target_attack/src/fetch_references.py"),
                "--output-dir",
                temporary,
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(SRC / "boundary_word_attack.py"),
                "--reference-dir",
                temporary,
                "--iterations",
                "8000",
                "--workers",
                "12",
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, str(SRC / "analyze.py")], cwd=ROOT, check=True
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
