#!/usr/bin/env python3
"""Independent structural validator for the V71 R3 owner ledger."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = HERE / "V71_R3_OWNER_LEDGER.tsv"
REVISIONS = HERE / "V71_R3_REVISIONS.tsv"
REPORT = HERE / "V71_R3_TECHNICAL_REPORT.md"
FIELD_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
ASTRO_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
OUTPUT = HERE / "V71_R3_VALIDATION.json"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def gate(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"gate": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> None:
    rows = read(LEDGER)
    revisions = read(REVISIONS)
    fields = read(FIELD_SOURCE)
    groups = read(ASTRO_SOURCE)
    prose = [r for r in rows if r["source_level"] == "PROSE_FIELD"]
    astro = [r for r in rows if r["source_level"] == "ASTRO_LOCUS"]
    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    allowed_status = {"DIRECT_VISIBLE", "INHERITED_VISIBLE", "PAGE_OWNER_ONLY", "UNRESOLVED"}
    required = {
        "owner_row_id", "source_level", "source_id", "page", "section",
        "record_or_diagram", "locus", "member_count", "member_ids",
        "v69_formal_role", "image_namespace", "owner_class", "owner_id",
        "ownership_status", "technical_silent_argument_default",
        "visible_geometric_basis", "strongest_rival", "confidence",
        "v69_change", "direction_policy", "semantic_ceiling",
    }

    source_loci = []
    seen = set()
    for group in groups:
        key = (group["diagram_id"], group["page"], group["locus"])
        if key not in seen:
            seen.add(key)
            source_loci.append(key)
    output_loci = [(r["record_or_diagram"], r["page"], r["locus"]) for r in astro]
    prose_ids = [r["source_id"] for r in prose]
    source_field_ids = [r["field_id"] for r in fields]
    report = REPORT.read_text(encoding="utf-8")

    g = []
    g.append(gate("schema_complete", required == set(rows[0]), sorted(set(rows[0]) ^ required)))
    g.append(gate("exact_277_rows", len(rows) == 277, len(rows)))
    g.append(gate("exact_135_prose", len(prose) == 135, len(prose)))
    g.append(gate("exact_142_astro", len(astro) == 142, len(astro)))
    g.append(gate("unique_owner_row_ids", len({r["owner_row_id"] for r in rows}) == 277, len({r["owner_row_id"] for r in rows})))
    g.append(gate("prose_field_identity_and_order", prose_ids == source_field_ids, {"first": prose_ids[:2], "last": prose_ids[-2:]}))
    g.append(gate("astro_locus_identity_and_order", output_loci == source_loci, {"first": output_loci[:2], "last": output_loci[-2:]}))
    g.append(gate("prose_event_sum_381", sum(int(r["member_count"]) for r in prose) == 381, sum(int(r["member_count"]) for r in prose)))
    g.append(gate("astro_group_sum_395", sum(int(r["member_count"]) for r in astro) == 395, sum(int(r["member_count"]) for r in astro)))
    g.append(gate("allowed_pages_only", {r["page"] for r in rows} == allowed_pages, sorted({r["page"] for r in rows})))
    g.append(gate("f84_and_f84r_absent", not any(r["page"].startswith("f84") for r in rows), "no sealed selector"))
    g.append(gate("ownership_status_enum", {r["ownership_status"] for r in rows} <= allowed_status, sorted({r["ownership_status"] for r in rows})))
    g.append(gate("all_required_cells_nonempty", all(all(r[key].strip() for key in required) for r in rows), "all 277 rows complete"))
    g.append(gate("semantic_ceiling_constant", {r["semantic_ceiling"] for r in rows} == {"VISIBLE_OWNER_NOT_WORD_CARD_STEM_OR_MEANING"}, sorted({r["semantic_ceiling"] for r in rows})))

    namespace_ok = all(
        (r["page"] == "f67r2" and r["image_namespace"].startswith("A1_"))
        or (r["page"] == "f68r1" and r["image_namespace"].startswith("A2_"))
        or (r["page"] == "f69v" and r["image_namespace"].startswith("A3_"))
        for r in astro
    )
    g.append(gate("astro_page_local_namespaces", namespace_ok, "A1/A2/A3 never cross pages"))
    f69_slots = [r for r in astro if r["page"] == "f69v" and 4 <= int(r["locus"].split(".")[1]) <= 31]
    g.append(gate("f69_exact_28_left_slots", len(f69_slots) == 28 and all(r["owner_id"] == f"A3_LEFT_RADIAL_SLOT_{i:02d}" for i, r in enumerate(f69_slots, 1)), len(f69_slots)))
    g.append(gate("f69_no_direction_or_join", all(r["direction_policy"] == "NO_START_ROTATION_OR_CROSS_WHEEL_JOIN_FROM_IMAGE" for r in astro if r["page"] == "f69v"), "all 31 loci"))

    b2 = [r for r in prose if r["record_or_diagram"] == "B2"]
    b2_owners = {r["owner_id"] for r in b2}
    g.append(gate("f82_local_station_partition", len(b2_owners) == 5 and "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION" in b2_owners, sorted(b2_owners)))
    g.append(gate("f82_gap_unresolved", all(r["ownership_status"] == "UNRESOLVED" for r in b2 if r["locus"] == "f82r.19"), [r["source_id"] for r in b2 if r["locus"] == "f82r.19"]))
    g.append(gate("bio_no_image_direction", all(r["direction_policy"] == "NO_DIRECTION_FROM_IMAGE" for r in prose if r["section"] == "BIOLOGICAL"), "115 fields"))
    b5 = {r["owner_id"] for r in prose if r["record_or_diagram"] == "B5"}
    b6 = {r["owner_id"] for r in prose if r["record_or_diagram"] == "B6"}
    g.append(gate("f83_b5_b6_owner_separation", b5 == {"B5_LEFT_OPEN_FRINGE_STATION"} and b6 == {"B6_RIGHT_S_RUN_MULTIPORT_STATION"} and b5.isdisjoint(b6), {"B5": sorted(b5), "B6": sorted(b6)}))

    report_ids = all(r["source_id"] in report for r in rows)
    g.append(gate("report_complete_trace_ids", report_ids, "all 277 source IDs occur"))
    g.append(gate("report_required_sections", all(title in report for title in ("Vollständige Herbal-Spur (20/20)", "Vollständige Biological-Spur (115/115)", "Vollständige Astro-Spur (142/142)", "Ausführbare OWNER-Registerregeln")), "four headings"))
    g.append(gate("revision_rows_present", len(revisions) == 14, len(revisions)))

    passed = all(item["status"] == "PASS" for item in g)
    payload = {
        "status": "PASS" if passed else "FAIL",
        "gate_count": len(g),
        "passed_gates": sum(item["status"] == "PASS" for item in g),
        "owner_rows": len(rows),
        "status_counts": dict(sorted(Counter(r["ownership_status"] for r in rows).items())),
        "gates": g,
        "sealed": ["f84", "f84r"],
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
