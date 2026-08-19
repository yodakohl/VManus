#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    sel = EXP / "artifacts/gdt349_selection.tsv"
    freeze = json.loads((EXP / "artifacts/gdt349_freeze.json").read_text())
    with sel.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    checks = []
    def ck(name: str, cond: bool) -> None:
        assert cond, name; checks.append(name)
    ck("exact_235_rows", len(rows) == 235)
    ck("unique_targets", len({r["target_id"] for r in rows}) == 235)
    ck("unique_page_ring_ordinals", len({(r["page"], r["ring_scope"], r["grove_ordinal"]) for r in rows}) == 235)
    ck("eleven_pages", len({r["page"] for r in rows}) == 11)
    ck("four_folios", {r["physical_folio"] for r in rows} == {"f70", "f71", "f72", "f73"})
    ck("no_f84", not any(r["page"].lower().startswith("f84") or r["current_locus"].lower().startswith("f84") for r in rows))
    ck("all_sealed", all(r["review_state"] == "SEALED_UNREVIEWED" for r in rows))
    ck("selection_hash", freeze["selection_sha256"] == sha(sel))
    for rel, expected in freeze["inputs"].items():
        ck("hash_" + Path(rel).name, sha(ROOT / rel) == expected)
    by_ring = Counter((r["page"], r["ring_scope"]) for r in rows)
    ck("twenty_one_complete_rings", len(by_ring) == 21 and sum(by_ring.values()) == 235)
    result = {
        "experiment": "GDT349_ZODIAC_FACING_ORIENTATION_FREEZE_VALIDATION",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "selection_sha256": sha(sel),
        "f84_rows": 0,
    }
    (EXP / "artifacts/gdt349_freeze_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
