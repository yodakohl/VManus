#!/usr/bin/env python3
"""Validate productive-family versus operating-mode crosswalk."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_NINTH_281_EVENT_STEM_MODE_MEMBERSHIPS.tsv")
    matrix = read("THREE_HUNDRED_NINTH_29_FAMILY_MODE_MATRIX.tsv")
    layers = read("THREE_HUNDRED_NINTH_LAYER_MODE_CROSSWALK.tsv")
    predictive = {r["family_id"] for r in matrix if r["operational_interpretation"] == "MODE_PREDICTIVE_CONTENT_FAMILY"}
    checks = {
        "events_281": len(events) == 281 and len({r["event_id"] for r in events}) == 281,
        "families_29": len(matrix) == 29 and len({r["family_id"] for r in matrix}) == 29,
        "layers_2": len(layers) == 2,
        "layer_events_281": sum(int(r["event_count"]) for r in layers) == 281,
        "layer_cards_124": sum(int(r["distinct_card_types"]) for r in layers) == 124,
        "composed_264_whole_17": {r["teaching_layer"]: int(r["event_count"]) for r in layers} == {"PRODUCTIVE_COMPOSITION": 264, "LEARNED_WHOLE_OR_MICROSIGN": 17},
        "predictive_ten": predictive == {"L", "AIN", "AIIN", "IIN", "OR", "SHED", "CHK", "CKH", "CKHE", "LSH"},
        "ched_directional": next(r for r in matrix if r["family_id"] == "CHED_TRANSFER")["operational_interpretation"] == "DIRECTIONALLY_CONDITIONED_TRANSFER_CORE",
        "ok_activator": next(r for r in matrix if r["family_id"] == "OK")["operational_interpretation"] == "MULTIMODE_OPERATION_ACTIVATOR",
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
