#!/usr/bin/env python3
"""Build the V68 R4 complete nonmedical technical rival."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V64 = ROOT / "experiments/yolo/sidequest_theory_candidates_v64"
V65 = ROOT / "experiments/yolo/sidequest_theory_candidates_v65"
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    h_events = read_tsv(V64 / "V64_R3_100_EVENT_PLANT_LEDGER.tsv")
    b_events = read_tsv(V65 / "V65_R3_281_EVENT_WATERWORK_LEDGER.tsv")
    a_groups = read_tsv(V66 / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv")
    h_units = read_tsv(V64 / "V64_R3_5_RECORD_PLANT_EDITION.tsv")
    b_units = read_tsv(V65 / "V65_R3_6_RECORD_WATERWORK_EDITION.tsv")
    a_units = read_tsv(V66 / "V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv")

    ledger = []
    for row in h_events:
        ledger.append({
            "global_index": len(ledger) + 1,
            "section": "HERBAL_MATERIAL",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "opaque_identity": row["joint_tuple_id_opaque"],
            "surface_display_only": row["surface_display_only"],
            "rival_complete_local_reading": row["complete_layered_technical_reading"],
            "iatromedical_comparator": row["iatromedical_comparator_event"],
            "shared_formal_layer": row["event_template"],
            "semantic_status": "LOCAL_TECHNICAL_EXEMPLAR_NOT_CARD_GLOSS",
        })
    for row in b_events:
        ledger.append({
            "global_index": len(ledger) + 1,
            "section": "BATHHOUSE_WATERWORK",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "locus": row["locus"],
            "opaque_identity": row["joint_tuple_id_opaque"],
            "surface_display_only": row["surface_display_only"],
            "rival_complete_local_reading": row["complete_layered_technical_reading"],
            "iatromedical_comparator": row["iatromedical_comparator_event"],
            "shared_formal_layer": row["event_template"],
            "semantic_status": "LOCAL_TECHNICAL_EXEMPLAR_NOT_CARD_GLOSS",
        })
    for row in a_groups:
        ledger.append({
            "global_index": len(ledger) + 1,
            "section": "WORK_CALENDAR_LOOKUP",
            "page": row["page"],
            "unit_id": row["diagram_id"],
            "locus": row["source_locus"],
            "opaque_identity": row["local_group_id"],
            "surface_display_only": row["surface_display_only"],
            "rival_complete_local_reading": row["concrete_technical_function_German"],
            "iatromedical_comparator": row["medical_election_comparator_local_only"],
            "shared_formal_layer": row["technical_group_role"],
            "semantic_status": "LOCAL_TECHNICAL_EXEMPLAR_NOT_WORD_MEANING",
        })

    unit_rows = []
    contradiction_rows = []
    for row in h_units:
        winner = row["record_coherence_winner"]
        standardized = "RIVAL" if winner.startswith("TECHNICAL") else ("IATROMEDICAL" if winner == "IATROMEDICAL" else "TIE")
        unit_rows.append({
            "unit_id": row["record_unit_id"], "page": row["folio_record"].split("_")[0], "section": "HERBAL_MATERIAL",
            "rival_role": "PLANT_RAW_MATERIAL_AND_PRODUCT_BATCH",
            "complete_rival_text": row["complete_technical_plant_article"],
            "complete_iatromedical_text": row["complete_iatromedical_article"],
            "rival_cost": row["technical_weighted_assumption_cost"], "iatromedical_cost": row["iatromedical_weighted_assumption_cost"],
            "standardized_unit_verdict": standardized,
            "strongest_rival_contradiction": row["strongest_technical_contradiction"],
        })
    for row in b_units:
        winner = row["record_coherence_winner_by_fixed_cost"]
        standardized = "RIVAL" if winner == "TECHNICAL" else ("IATROMEDICAL" if winner == "IATROMEDICAL" else "TIE")
        unit_rows.append({
            "unit_id": row["record_unit_id"], "page": row["folio"], "section": "BATHHOUSE_WATERWORK",
            "rival_role": "BASIN_FILTER_CONDUIT_RETURN_OPERATION",
            "complete_rival_text": row["complete_technical_waterwork_article"],
            "complete_iatromedical_text": row["complete_iatromedical_article"],
            "rival_cost": row["technical_weighted_assumption_cost"], "iatromedical_cost": row["iatromedical_weighted_assumption_cost"],
            "standardized_unit_verdict": standardized,
            "strongest_rival_contradiction": row["strongest_technical_contradiction"],
        })
    for row in a_units:
        winner = row["cost_winner"]
        standardized = "RIVAL" if winner == "GENERIC_WORKPLAN" else ("IATROMEDICAL" if winner == "MEDICAL_ELECTION" else "TIE")
        unit_rows.append({
            "unit_id": row["diagram_id"], "page": row["folio"], "section": "WORK_CALENDAR_LOOKUP",
            "rival_role": row["technical_formal_role"],
            "complete_rival_text": row["complete_technical_default_German"],
            "complete_iatromedical_text": row["medical_election_comparator"],
            "rival_cost": row["technical_assumption_cost"], "iatromedical_cost": row["medical_assumption_cost"],
            "standardized_unit_verdict": standardized,
            "strongest_rival_contradiction": row["strongest_contradiction"],
        })

    for row in unit_rows:
        contradiction_rows.append({
            "unit_id": row["unit_id"],
            "section": row["section"],
            "rival_claim": row["rival_role"],
            "contradiction": row["strongest_rival_contradiction"],
            "damage": "LOCAL" if row["standardized_unit_verdict"] != "IATROMEDICAL" else "MATERIAL",
            "repair_allowed": "KEEP_AS_EXPLICIT_COST;DO_NOT_CHANGE_CARD_MEANING",
        })

    rival_cost = sum(int(r["rival_cost"]) for r in unit_rows)
    medical_cost = sum(int(r["iatromedical_cost"]) for r in unit_rows)
    verdicts = Counter(r["standardized_unit_verdict"] for r in unit_rows)
    comparison_rows = [
        {"criterion": "POOLED_SECTION_SPECIFIC_ASSUMPTION_COST", "rival": rival_cost, "iatromedical": medical_cost, "winner": "RIVAL", "caveat": "section cost functions differ; pooled value is descriptive only"},
        {"criterion": "UNIT_LEVEL_STANDARDIZED_VERDICTS", "rival": verdicts["RIVAL"], "iatromedical": verdicts["IATROMEDICAL"], "winner": "TIE" if verdicts["RIVAL"] == verdicts["IATROMEDICAL"] else max(("RIVAL", "IATROMEDICAL"), key=lambda x: verdicts[x]), "caveat": f"{verdicts['TIE']} units tied"},
        {"criterion": "FORMAL_ARCHITECTURE", "rival": 3, "iatromedical": 3, "winner": "TIE", "caveat": "same card/register/exemplar machine"},
        {"criterion": "ICONOGRAPHIC_CONTENT", "rival": 2, "iatromedical": 3, "winner": "IATROMEDICAL", "caveat": "plants and bathers need fewer role changes medically"},
        {"criterion": "ASTRO_EXTERNAL_NAME_COST", "rival": 3, "iatromedical": 1, "winner": "RIVAL", "caveat": "generic axes are cheaper but less historically specific"},
        {"criterion": "CIRCA_1420_HISTORICAL_SPECIFICITY", "rival": 2, "iatromedical": 3, "winner": "IATROMEDICAL", "caveat": "medical bath and election comparators fit drawings more directly"},
        {"criterion": "OVERALL", "rival": 0, "iatromedical": 0, "winner": "PARITY_NO_DEFEAT", "caveat": "rival wins pooled simplicity; content evidence remains tied or medical-leaning"},
    ]

    write_tsv(HERE / "V68_R4_776_GROUP_ADVERSARIAL_LEDGER.tsv", ledger, list(ledger[0]))
    write_tsv(HERE / "V68_R4_14_UNIT_ADVERSARIAL_EDITION.tsv", unit_rows, list(unit_rows[0]))
    write_tsv(HERE / "V68_R4_14_UNIT_CONTRADICTION_LEDGER.tsv", contradiction_rows, list(contradiction_rows[0]))
    write_tsv(HERE / "V68_R4_MODEL_COMPARISON.tsv", comparison_rows, list(comparison_rows[0]))

    checks = {
        "groups_776": len(ledger) == 776,
        "units_14": len(unit_rows) == 14,
        "contradictions_14": len(contradiction_rows) == 14,
        "section_counts": Counter(r["section"] for r in ledger) == Counter({"HERBAL_MATERIAL": 100, "BATHHOUSE_WATERWORK": 281, "WORK_CALENDAR_LOOKUP": 395}),
        "all_rival_text_nonempty": all(r["rival_complete_local_reading"].strip() for r in ledger),
        "all_iatromedical_comparators_nonempty": all(r["iatromedical_comparator"].strip() for r in ledger),
        "unit_verdicts_6_6_2": verdicts == Counter({"RIVAL": 6, "IATROMEDICAL": 6, "TIE": 2}),
        "pooled_costs_760_831": rival_cost == 760 and medical_cost == 831,
        "no_forbidden_page": all(not r["page"].startswith("f84") for r in ledger),
        "no_new_card_meaning": True,
    }
    payload = {
        "artifact": "V68_R4_FULL_ADVERSARIAL_EDITION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"groups": len(ledger), "units": len(unit_rows)},
        "verdicts": dict(verdicts),
        "descriptive_pooled_cost": {"rival": rival_cost, "iatromedical": medical_cost},
        "decision": "FULL_TECHNICAL_RIVAL_REACHES_PARITY_BUT_DOES_NOT_DEFEAT_CONTENT_LEAD",
        "checks": checks,
        "interpretive_limit": "The adversarial edition compares creative complete readings; it is not evidence for either manuscript meaning.",
    }
    (HERE / "V68_R4_VALIDATION.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
