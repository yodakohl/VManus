#!/usr/bin/env python3
from pathlib import Path

from necessary_bound import run

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def main() -> int:
    out = ROOT / "experiments/yolo/gdt614_core_run_macro_recovery/artifacts"
    result = run(ROOT, out)
    print(
        result["decision"],
        f"minimum={result['minimum_paid_subtree_hits_required']}",
        f"registered={result['registered_paid_cards']}",
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
