#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"

import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import sha256_file  # noqa: E402


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / "artifacts" / name).open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def main() -> None:
    p = json.loads((BASE / "artifacts/gdt362_visual_freeze.json").read_text())
    sel, loc, obs = rows("gdt362_selection.tsv"), rows("gdt362_localizations.tsv"), rows("gdt362_visual_observations.tsv")
    checks: list[str] = []
    def ok(name: str, value: bool) -> None:
        assert value, name
        checks.append(name)
    ids = [r["target_id"] for r in sel]
    ok("nine_rows", len(ids) == len(loc) == len(obs) == 9)
    ok("id_order", ids == [r["target_id"] for r in loc] == [r["target_id"] for r in obs])
    ok("locus_order", [r["locus"] for r in obs] == [f"f101v2.{i}" for i in range(10, 19)])
    ok("states", Counter(r["visual_state"] for r in obs) == Counter({"CLEAR_GAP": 5, "CONTACT": 3, "UNCERTAIN": 1}))
    ok("provenance", all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in loc + obs))
    ok("fold_ambiguous", loc[3]["localization_status"] == "LOCALIZED_FOLD_AMBIGUOUS" and obs[3]["visual_state"] == "UNCERTAIN")
    ok("canvas_scopes", [r["canvas_id"] for r in loc] == ["1006250"] * 3 + ["1006250|1006251"] + ["1006251"] * 5)
    ok("hash_shapes", all(all(len(x) == 64 for x in r["context_crop_sha256"].split("|")) and all(len(x) == 64 for x in r["target_crop_sha256"].split("|")) for r in loc))
    ok("formal_sealed_at_freeze", p["status"].endswith("BEFORE_ANY_TARGET_FORMAL_REVEAL"))
    ok("f84_sealed", not p["access"]["f84_accessed"])
    for rel, expected in p["inputs"].items():
        ok("hash_" + hashlib.sha256(rel.encode()).hexdigest()[:8], sha256_file(ROOT / rel) == expected)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
