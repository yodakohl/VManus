#!/usr/bin/env python3
"""Validate the frozen V72 R2 116-statement reconstruction."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"

STATEMENTS = V69 / "V69_R4_FINAL_116_STATEMENT_EDITION.tsv"
FIELDS = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
EVENTS = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
LEDGER = OUT / "V72_R2_116_STATEMENTS.tsv"
REVISIONS = OUT / "V72_R2_REVISIONS.tsv"
REPORT = OUT / "V72_R2_HISTORICAL_STATEMENT_REPORT.md"
VALIDATION = OUT / "V72_R2_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(condition: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = bool(condition)


def main() -> None:
    source_statements = read_tsv(STATEMENTS)
    source_fields = read_tsv(FIELDS)
    source_events = read_tsv(EVENTS)
    owner_rows = {
        row["unit_id"]: row
        for row in read_tsv(OWNERS)
        if row["unit_kind"] == "PROSE_FIELD"
    }
    rows = read_tsv(LEDGER)
    revisions = read_tsv(REVISIONS)
    report = REPORT.read_text(encoding="utf-8")

    source_ids = [row["statement_id"] for row in source_statements]
    output_ids = [row["statement_id"] for row in rows]
    source_field_ids = {row["field_id"] for row in source_fields}
    output_field_ids = {
        fid for row in rows for fid in row["constituent_fields"].split("|")
    }
    source_event_ids = [row["event_serial"] for row in source_events]
    output_event_ids = [
        eid
        for row in rows
        for eid in re.findall(r"E(\d+):", row["literal_owner_card_exemplar_layer"])
    ]
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in source_events:
        events_by_statement[event["statement_id"]].append(event)

    checks: dict[str, bool] = {}
    check(len(rows) == 116, "exactly_116_rows", checks)
    check(len(set(output_ids)) == 116, "statement_ids_unique", checks)
    check(output_ids == source_ids, "statement_order_and_membership_exact", checks)
    check(len(revisions) == 116, "revision_rows_exactly_116", checks)
    check([r["statement_id"] for r in revisions] == source_ids, "revision_membership_exact", checks)
    check(output_field_ids == source_field_ids and len(output_field_ids) == 135, "all_135_fields_covered", checks)
    check(output_event_ids == source_event_ids and len(output_event_ids) == 381, "all_381_events_once_in_order", checks)
    check(set(row["record_unit_id"] for row in rows) == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}, "all_11_records_present", checks)
    check(all(row["concrete_source_class_paraphrase"].strip() for row in rows), "every_paraphrase_nonempty", checks)
    check(all(row["strongest_rival"].strip() for row in rows), "every_rival_nonempty", checks)
    check(all(row["strongest_contradiction"].strip() for row in rows), "every_contradiction_nonempty", checks)
    check(all(row["repair_cost_0_4"] in {"0", "1", "2", "3", "4"} for row in rows), "repair_costs_in_range", checks)
    check(all("[OWNER:" in row["literal_owner_card_exemplar_layer"] for row in rows), "literal_layer_has_owner", checks)
    check(all("[EXEMPLAR " in row["literal_owner_card_exemplar_layer"] or "[CARD:" in row["literal_owner_card_exemplar_layer"] or "[FORMAL:" in row["literal_owner_card_exemplar_layer"] for row in rows), "literal_layer_typed", checks)

    expected_owner_exact = True
    event_literal_exact = True
    for row in rows:
        fids = row["constituent_fields"].split("|")
        expected_owners = list(dict.fromkeys(owner_rows[fid]["selected_visible_owner"] for fid in fids))
        expected_statuses = list(dict.fromkeys(owner_rows[fid]["owner_status"] for fid in fids))
        if row["v71_visible_owners"].split("|") != expected_owners:
            expected_owner_exact = False
        if row["v71_owner_statuses"].split("|") != expected_statuses:
            expected_owner_exact = False
        literal = row["literal_owner_card_exemplar_layer"]
        for event in events_by_statement[row["statement_id"]]:
            if event["selected_exact_mnemonic"] != "UNKNOWN" and f"[CARD:{event['selected_exact_mnemonic']}]" not in literal:
                event_literal_exact = False
            if event["strict_formal_prompt"] != "NONE" and f"[FORMAL:{event['strict_formal_prompt']}]" not in literal:
                event_literal_exact = False
    check(expected_owner_exact, "v71_selected_owners_and_statuses_exact", checks)
    check(event_literal_exact, "known_cards_and_formal_prompts_retained", checks)

    owner_cross = [row for row in rows if len(row["v71_visible_owners"].split("|")) > 1]
    unresolved = [row for row in rows if "UNRESOLVED" in row["v71_owner_statuses"]]
    herbals = [row for row in rows if row["record_unit_id"].startswith("H")]
    check(all(row["repair_cost_0_4"] == "4" and row["owner_crossing"] == "CROSS_FIELD_OWNER_CHANGE" for row in owner_cross), "owner_crossings_cost_four", checks)
    check(all(int(row["repair_cost_0_4"]) >= 3 for row in unresolved), "unresolved_cost_at_least_three", checks)
    check(all(int(row["repair_cost_0_4"]) >= 3 for row in herbals), "herbal_taxon_repairs_cost_at_least_three", checks)
    check({row["statement_id"] for row in owner_cross} == {"B2-S012", "B3-S016", "B3-S026", "B4-S015"}, "owner_crossing_set_frozen", checks)

    forbidden_in_paraphrases = re.compile(r"Teufelsabbiss|Veilchen|Bärlauch|Sonnentau|PAGE_HOST|joint.tuple|EVA|prefix|suffix|stem|Stamm", re.I)
    check(not any(forbidden_in_paraphrases.search(row["concrete_source_class_paraphrase"]) for row in rows), "no_taxon_sound_stem_or_tuple_value_in_paraphrases", checks)
    check(not any("f84" in row["concrete_source_class_paraphrase"].casefold() for row in rows), "no_sealed_page_content", checks)
    check("### H1" in report and "### B6" in report and all(f"| {sid} |" in report for sid in source_ids), "report_walks_all_116_statements_in_11_records", checks)
    check("keine Übersetzung" in report or "keine Entzifferung" in report, "report_states_semantic_ceiling", checks)

    sha = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (LEDGER, REVISIONS, REPORT, Path(__file__), OUT / "build_v72_r2_statement_reconstruction.py")
    }
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "statements": len(rows),
            "fields": len(output_field_ids),
            "events": len(output_event_ids),
            "records": len(set(row["record_unit_id"] for row in rows)),
            "owner_crossing_statements": len(owner_cross),
            "unresolved_owner_statements": len(unresolved),
            "repair_cost_distribution": dict(sorted(Counter(row["repair_cost_0_4"] for row in rows).items())),
        },
        "sealed": {"f84": True, "f84r": True},
        "sha256": sha,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
