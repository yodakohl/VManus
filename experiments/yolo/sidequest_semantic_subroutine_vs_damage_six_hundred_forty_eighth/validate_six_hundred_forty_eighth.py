#!/usr/bin/env python3
"""Validate short-subroutine versus gapped-remnant classification."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    shapes = read("SIX_HUNDRED_FORTY_EIGHTH_37_FRAGMENT_SHAPES.tsv")
    contexts = read("SIX_HUNDRED_FORTY_EIGHTH_74_CONTEXT_JUDGMENTS.tsv")
    backbone = read("SIX_HUNDRED_FORTY_EIGHTH_4_C1_C3_BACKBONE_CONTEXTS.tsv")
    c1 = [row for row in backbone if row["source_case"] == "C1"]
    c3 = [row for row in backbone if row["source_case"] == "C3"]
    checks = {
        "thirty_seven_shapes": len(shapes) == 37,
        "seventy_four_contexts": len(contexts) == 74,
        "two_contexts_per_shape": all(sum(row["fragment_id"] == shape["fragment_id"] for row in contexts) == 2 for shape in shapes),
        "forty_four_contiguous": sum(row["contiguous_in_owner_case"] == "YES" for row in contexts) == 44,
        "thirty_gapped": sum(row["contiguous_in_owner_case"] == "NO" for row in contexts) == 30,
        "four_backbone_contexts": len(backbone) == 4 and len(c1) == 2 and len(c3) == 2,
        "c1_backbone_gapped": all(row["position_shape"] == "GAPPED_SUBSEQUENCE" and row["source_positions"] == "1|4|5|6" and row["missing_internal_positions"] == "2|3" for row in c1),
        "c3_backbone_closed_suffix": all(row["position_shape"] == "CONTIGUOUS_CLOSED_SUFFIX" and row["source_positions"] == "3|4|5|6" and row["missing_internal_positions"] == "NONE" for row in c3),
        "owner_address_resolved": all(row["owner_address_resolved"] == "YES" for row in contexts),
        "zero_insertions": all(row["automatic_insertions"] == "0" for row in contexts),
        "contiguous_not_expanded": all(row["editor_action"] == "READ_AS_POSSIBLE_SHORT_UNIT__DO_NOT_EXPAND" for row in contexts if row["contiguous_in_owner_case"] == "YES"),
        "gapped_requires_evidence": all(row["editor_action"] == "MARK_POSSIBLE_LOSS__SEEK_SECOND_COPY_OR_VISIBLE_DAMAGE" for row in contexts if row["contiguous_in_owner_case"] == "NO"),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
