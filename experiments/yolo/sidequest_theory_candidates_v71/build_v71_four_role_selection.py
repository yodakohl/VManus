#!/usr/bin/env python3
"""Build the V71 four-role selected owner layer."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
COLS = [
    "selection_row", "selected_from_role", "unit_kind", "unit_id", "page",
    "section", "record_or_diagram", "locus", "member_count", "owner_status",
    "selected_visible_owner", "silent_argument_default", "visible_basis",
    "strongest_rival", "confidence", "v69_revision", "semantic_ceiling",
]


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def main() -> None:
    r2 = read("V71_R2_OWNER_LEDGER.tsv")
    r3 = read("V71_R3_OWNER_LEDGER.tsv")
    selected: list[dict[str, str]] = []

    # Herbal has no object leaders; the historical whole-article reading is the
    # least assumptive. Bio and Astro need R3's explicit contact/namespace map.
    for row in r2:
        if row["section"] != "HERBAL":
            continue
        selected.append({
            "selection_row": f"V71S{len(selected)+1:03d}",
            "selected_from_role": "R2_HISTORICAL",
            "unit_kind": row["unit_type"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "section": row["section"],
            "record_or_diagram": row["source_record"],
            "locus": row["locus"],
            "member_count": row["source_group_count"],
            "owner_status": row["ownership_status"],
            "selected_visible_owner": row["smallest_visible_owner"],
            "silent_argument_default": row["silent_argument_or_source_default"],
            "visible_basis": row["image_basis"],
            "strongest_rival": row["strongest_rival"],
            "confidence": row["confidence"],
            "v69_revision": row["v69_revision"],
            "semantic_ceiling": "VISIBLE_OWNER_OR_ARTICLE_FRAME_NOT_CARD_MEANING",
        })

    for row in r3:
        if row["section"] == "HERBAL":
            continue
        selected.append({
            "selection_row": f"V71S{len(selected)+1:03d}",
            "selected_from_role": "R3_TECHNICAL",
            "unit_kind": row["source_level"],
            "unit_id": row["source_id"],
            "page": row["page"],
            "section": row["section"],
            "record_or_diagram": row["record_or_diagram"],
            "locus": row["locus"],
            "member_count": row["member_count"],
            "owner_status": row["ownership_status"],
            "selected_visible_owner": row["owner_id"],
            "silent_argument_default": row["technical_silent_argument_default"],
            "visible_basis": row["visible_geometric_basis"],
            "strongest_rival": row["strongest_rival"],
            "confidence": row["confidence"],
            "v69_revision": row["v69_change"],
            "semantic_ceiling": row["semantic_ceiling"],
        })

    expected_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    ids = [row["unit_id"] for row in selected]
    checks = {
        "selected_rows_277": len(selected) == 277,
        "unique_unit_ids": len(ids) == len(set(ids)),
        "prose_fields_135": sum(row["unit_kind"] == "PROSE_FIELD" for row in selected) == 135,
        "astro_loci_142": sum(row["unit_kind"] == "ASTRO_LOCUS" for row in selected) == 142,
        "member_total_776": sum(int(row["member_count"]) for row in selected) == 776,
        "exact_pages": {row["page"] for row in selected} == expected_pages,
        "no_blank_owner": all(row["selected_visible_owner"].strip() for row in selected),
        "no_card_semantic_claim": all(
            row["semantic_ceiling"] in {
                "VISIBLE_OWNER_OR_ARTICLE_FRAME_NOT_CARD_MEANING",
                "VISIBLE_OWNER_NOT_WORD_CARD_STEM_OR_MEANING",
            }
            for row in selected
        ),
        "f69_slots_local_28": sum(
            row["page"] == "f69v" and row["unit_id"] not in {"f69v.1", "f69v.2", "f69v.3"}
            and row["selected_visible_owner"].startswith("A3_LEFT_RADIAL_SLOT_")
            for row in selected
        ) == 28,
    }
    with (HERE / "V71_SELECTED_OWNER_LEDGER.tsv").open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(selected)

    modes = Counter(row["owner_status"] for row in selected)
    result = {
        "schema": "V71_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {"rows": len(selected), "members": sum(int(row["member_count"]) for row in selected), **dict(modes)},
        "bindings": {f"V71_R{role}_OWNER_LEDGER.tsv": sha(f"V71_R{role}_OWNER_LEDGER.tsv") for role in range(1, 5)},
        "sealed_pages_opened": [],
    }
    (HERE / "V71_VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], len(selected), dict(modes))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
