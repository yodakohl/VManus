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
PANEL = EXP / "artifacts/gdt350_source_panel.tsv"
OUT = EXP / "artifacts/gdt350_freeze.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    with PANEL.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert len(rows) == 6
    assert len({r["witness_id"] for r in rows}) == 6
    assert sum(r["panel_role"] == "CORE_28" for r in rows) == 5
    assert sum(r["direct_review_required"] == "YES" for r in rows) == 2
    assert all("f84" not in json.dumps(r).lower() for r in rows)
    payload = {
        "experiment": "GDT350",
        "status": "FROZEN_EXTERNAL_PANEL_BEFORE_DIRECT_FACSIMILE_REVIEW",
        "counts": {
            "witnesses": len(rows),
            "core_28_witnesses": sum(r["panel_role"] == "CORE_28" for r in rows),
            "context_controls": sum(r["panel_role"] != "CORE_28" for r in rows),
            "direct_review_pending": sum(r["direct_review_required"] == "YES" for r in rows),
            "source_asserted_exact_alternation": 2,
        },
        "frozen_witness_ids": [r["witness_id"] for r in rows],
        "inputs": {
            str(PANEL.relative_to(ROOT)): sha(PANEL),
            str((EXP / "METHOD.md").relative_to(ROOT)): sha(EXP / "METHOD.md"),
            str((EXP / "SOURCE_AUDIT.md").relative_to(ROOT)): sha(EXP / "SOURCE_AUDIT.md"),
        },
        "access": {
            "voynich_source_tables_loaded": False,
            "voynich_images_opened": False,
            "voynich_formal_payload_opened": False,
            "f84_accessed": False,
        },
        "claim_ceiling": "External-source panel freeze only; no Voynich target score, slot alignment, cultural identification, language, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
