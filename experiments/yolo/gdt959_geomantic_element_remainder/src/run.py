#!/usr/bin/env python3
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def main() -> int:
    raise NotImplementedError


if __name__ == '__main__':
    raise SystemExit(main())
