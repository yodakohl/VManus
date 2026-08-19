#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt350_lunar_28_binary_specificity"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    panel = EXP / "artifacts/gdt350_source_panel.tsv"
    result = json.loads((EXP / "artifacts/gdt350_freeze.json").read_text())
    with panel.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    checks = []

    def check(name, value):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    check("six_rows", len(rows) == 6)
    check("unique_ids", len({r["witness_id"] for r in rows}) == 6)
    check("five_core", sum(r["panel_role"] == "CORE_28" for r in rows) == 5)
    check("two_pending", sum(r["direct_review_required"] == "YES" for r in rows) == 2)
    check("a65_source_claim", rows[0]["pre_review_presentation_evidence"] == "ODD_RED_EVEN_BLACK_SOURCE_ASSERTED")
    check("bl_source_claim", rows[1]["pre_review_presentation_evidence"] == "EVERY_OTHER_MINIATURE_GOLD_SOURCE_ASSERTED")
    check("no_voynich_paths", all("semantic_assumptions/results" not in v for v in result["inputs"]))
    check("no_f84", "f84" not in panel.read_text().lower() and not result["access"]["f84_accessed"])
    check("hashes", all(sha(ROOT / p) == h for p, h in result["inputs"].items()))
    check("status", result["status"] == "FROZEN_EXTERNAL_PANEL_BEFORE_DIRECT_FACSIMILE_REVIEW")
    out = {
        "experiment": "GDT350_FREEZE",
        "status": "PASS",
        "checks": len(checks),
        "check_names": checks,
        "result_sha256": sha(EXP / "artifacts/gdt350_freeze.json"),
    }
    (EXP / "artifacts/gdt350_freeze_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
