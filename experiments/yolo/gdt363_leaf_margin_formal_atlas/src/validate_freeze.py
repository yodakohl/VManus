#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt363_leaf_margin_formal_atlas"

import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import sha256_file  # noqa: E402


def main() -> None:
    with (BASE / "artifacts/gdt363_panel.tsv").open(encoding="utf-8", newline="") as h:
        rows = list(csv.DictReader(h, delimiter="\t"))
    p = json.loads((BASE / "artifacts/gdt363_freeze.json").read_text())
    checks = [len(rows) == 44, len({r["physical_folio"] for r in rows}) == 44,
              Counter(r["leaf_margin_state"] for r in rows) == Counter(SMOOTH=29, TOOTHED=13, UNCERTAIN=2),
              sum(r["score_eligible"] == "1" for r in rows) == 42,
              not any(r["page"].startswith("f84") for r in rows),
              not p["access"]["formal_source_opened_by_freezer"], not p["access"]["f84_accessed"]]
    checks += [sha256_file(ROOT / rel) == digest for rel, digest in p["inputs"].items()]
    checks += [sha256_file(ROOT / rel) == digest for rel, digest in p["outputs"].items()]
    assert all(checks)
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__": main()
