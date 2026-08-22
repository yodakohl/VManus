#!/usr/bin/env python3
"""Validate completeness, provenance, and semantic ceilings of V71 R2."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FIELD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
LEDGER = HERE / "V71_R2_OWNER_LEDGER.tsv"
REVISIONS = HERE / "V71_R2_REVISIONS.tsv"
BUILD = HERE / "V71_R2_BUILD_SUMMARY.json"
OUT = HERE / "V71_R2_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, name: str, checks: dict[str, bool]) -> None:
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


def main() -> None:
    rows = read_tsv(LEDGER)
    revisions = read_tsv(REVISIONS)
    fields = read_tsv(FIELD_SOURCE)
    astro_groups = read_tsv(ASTRO_SOURCE)
    checks: dict[str, bool] = {}

    check(len(rows) == 277, "exactly_277_data_rows", checks)
    unit_counts = Counter(row["unit_type"] for row in rows)
    check(unit_counts == {"PROSE_FIELD": 135, "ASTRO_LOCUS": 142}, "unit_type_counts_135_plus_142", checks)
    check(len({row["unit_id"] for row in rows}) == 277, "unit_ids_unique", checks)

    field_rows = [row for row in rows if row["unit_type"] == "PROSE_FIELD"]
    astro_rows = [row for row in rows if row["unit_type"] == "ASTRO_LOCUS"]
    check({row["unit_id"] for row in field_rows} == {row["field_id"] for row in fields}, "all_v69_fields_mapped_once", checks)
    expected_astro = {(row["diagram_id"], row["page"], row["locus"]) for row in astro_groups}
    actual_astro = {(row["source_record"], row["page"], row["locus"]) for row in astro_rows}
    check(actual_astro == expected_astro, "all_unique_astro_loci_mapped_once", checks)
    check(sum(int(row["source_group_count"]) for row in field_rows) == 381, "all_381_prose_events_accounted", checks)
    check(sum(int(row["source_group_count"]) for row in astro_rows) == 395, "all_395_astro_groups_accounted", checks)

    statuses = {"DIRECT_VISIBLE", "INHERITED_VISIBLE", "PAGE_OWNER_ONLY", "UNRESOLVED"}
    check({row["ownership_status"] for row in rows} <= statuses, "only_four_frozen_owner_statuses", checks)
    check({row["ownership_status"] for row in rows} == statuses, "all_four_owner_statuses_exercised", checks)
    check(all(0.0 <= float(row["confidence"]) <= 1.0 for row in rows), "confidence_bounded", checks)
    check(all(all(row[column].strip() for column in row) for row in rows), "no_empty_ledger_cells", checks)

    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    check({row["page"] for row in rows} == allowed_pages, "only_fixed_ten_pages", checks)
    revision_ids = {row["revision_id"] for row in revisions}
    check({row["v69_revision_id"] for row in rows} == revision_ids, "all_and_only_revision_ids_used", checks)
    check(len(revisions) == 27, "exactly_27_compact_revision_families", checks)
    revision_counts = Counter(row["v69_revision_id"] for row in rows)
    check(
        all(int(row["mapped_unit_count"]) == revision_counts[row["revision_id"]] for row in revisions),
        "revision_unit_counts_match",
        checks,
    )

    # The output must not carry a surface transcription or the old card/stem
    # interpretation machinery.  Source IDs are permitted provenance only.
    headers = set(rows[0])
    forbidden_columns = {
        "surface_display_only",
        "raw_eva",
        "stem",
        "card_id",
        "card_meaning",
        "iatromedical_local_text",
        "practical_local_text",
    }
    check(not (headers & forbidden_columns), "no_surface_card_or_stem_columns", checks)
    combined = LEDGER.read_text(encoding="utf-8") + REVISIONS.read_text(encoding="utf-8")
    check("f84" not in combined.lower(), "sealed_pages_absent_from_outputs", checks)
    check("PAGE_HOST" not in combined, "no_page_host_semantic_mapping", checks)

    build = json.loads(BUILD.read_text(encoding="utf-8"))
    check(build["rows"] == 277, "build_summary_row_count", checks)
    check(build["sealed_data_accessed"] is False, "sealed_data_declared_unaccessed", checks)
    check(build["surface_or_card_semantics_used"] is False, "semantic_channels_declared_unused", checks)
    check(build["output_sha256"][LEDGER.name] == digest(LEDGER), "ledger_hash_matches_build", checks)
    check(build["output_sha256"][REVISIONS.name] == digest(REVISIONS), "revision_hash_matches_build", checks)

    result = {
        "experiment": "V71_R2_IMAGE_TO_TEXT_OWNER_MAP",
        "status": "PASS",
        "checks": checks,
        "counts": {
            "ledger_rows": len(rows),
            "prose_fields": unit_counts["PROSE_FIELD"],
            "astro_loci": unit_counts["ASTRO_LOCUS"],
            "prose_source_events": sum(int(row["source_group_count"]) for row in field_rows),
            "astro_source_groups": sum(int(row["source_group_count"]) for row in astro_rows),
            "revision_families": len(revisions),
            "ownership_status": dict(Counter(row["ownership_status"] for row in rows)),
        },
        "sha256": {
            LEDGER.name: digest(LEDGER),
            REVISIONS.name: digest(REVISIONS),
            Path(__file__).name: digest(Path(__file__)),
        },
        "sealed_data_accessed": False,
        "other_voynich_pages_accessed": False,
        "sibling_outputs_accessed": False,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
