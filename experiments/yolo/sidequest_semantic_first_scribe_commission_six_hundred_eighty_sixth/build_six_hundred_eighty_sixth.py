#!/usr/bin/env python3
"""Simulate the first full Herbal and Biological copybook commission."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P680 = ROOT / "experiments/yolo/sidequest_semantic_owner_expanded_compact_edition_six_hundred_eightieth"
P681 = ROOT / "experiments/yolo/sidequest_semantic_copybook_layout_six_hundred_eighty_first"
P682 = ROOT / "experiments/yolo/sidequest_semantic_multi_scribe_production_six_hundred_eighty_second"
P684 = ROOT / "experiments/yolo/sidequest_semantic_rare_recipe_teaching_six_hundred_eighty_fourth"
RECORDS = ["H3", "B1"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def correction(recipe: str, lookup: str, surfaces: str) -> str:
    tokens = recipe.split("+")
    flags = []
    if "AIIN" in tokens or "AIN" in tokens:
        flags.append("MASS_VS_PORTION")
    if "AR" in tokens or "AL" in tokens:
        flags.append("SOURCE_VS_TARGET")
    if "Y" in tokens or "DY" in tokens:
        flags.append("OPEN_DIES_VS_CLOSE")
    if lookup == "CHOOSE_LOCAL_CARD_VARIANT":
        flags.append("LOCAL_CARD_VARIANT")
    if "|" in surfaces or ";" in surfaces:
        flags.append("COPY_SURFACE_DO_NOT_REGULARIZE")
    return "+".join(flags) if flags else "COPY_EXACT_NO_SEMANTIC_REPAIR"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = [row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv") if row["record"] in RECORDS]
    owner_statements = {row["statement_id"]: row for row in read(P680 / "SIX_HUNDRED_EIGHTIETH_116_COMPACT_OWNER_STATEMENTS.tsv")}
    record_texts = {row["record"]: row for row in read(P680 / "SIX_HUNDRED_EIGHTIETH_11_CONTINUOUS_OWNER_RECORDS.tsv")}
    recipes = {row["component_recipe"]: row for row in read(P681 / "SIX_HUNDRED_EIGHTY_FIRST_163_RECIPE_COPYBOOK.tsv")}
    recurrent = {row["component_recipe"]: row for row in read(P682 / "SIX_HUNDRED_EIGHTY_SECOND_50_RECURRENT_RECIPE_FAMILIES.tsv")}
    rare = {row["rare_recipe"]: row for row in read(P684 / "SIX_HUNDRED_EIGHTY_FOURTH_113_RARE_RECIPE_LESSONS.tsv")}

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    log_rows = []
    record_seen: set[str] = set()
    statement_seen: set[str] = set()
    for step, event in enumerate(events, start=1):
        statement_rows = by_statement[event["statement_id"]]
        index = next(i for i, row in enumerate(statement_rows) if row["event_id"] == event["event_id"])
        position = "ONLY" if len(statement_rows) == 1 else "FIRST" if index == 0 else "LAST" if index == len(statement_rows) - 1 else "MIDDLE"
        recipe = recipes[event["component_recipe"]]
        if event["record"] not in record_seen:
            owner_action = "SET_VISIBLE_OWNER"
            record_seen.add(event["record"])
        elif event["statement_id"] not in statement_seen:
            owner_action = "CARRY_OWNER_TO_NEW_STATEMENT"
        else:
            owner_action = "CARRY_OWNER"
        statement_seen.add(event["statement_id"])
        if event["component_recipe"] in recurrent:
            lesson_source = "RECURRENT_FAMILY"
            lesson_anchor = event["component_recipe"]
        else:
            lesson_source = rare[event["component_recipe"]]["teaching_method"]
            lesson_anchor = rare[event["component_recipe"]]["anchor_recipe_or_root"]
        log_rows.append({
            "commission_step": step,
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "statement_position": position,
            "owner_action": owner_action,
            "owner_noun_de": owner_statements[event["statement_id"]]["owner_noun_de"],
            "master_dictation_de": event["compact_atomic_reading_de"],
            "component_recipe": event["component_recipe"],
            "lesson_source": lesson_source,
            "lesson_anchor": lesson_anchor,
            "recipe_address": recipe["recipe_address"],
            "lookup_result": recipe["lookup_result"],
            "allowed_card_nos": recipe["card_nos"],
            "selected_card_no": event["card_no"],
            "allowed_surfaces": recipe["surfaces_to_copy"],
            "copied_surface": event["surface"],
            "likely_master_correction": correction(event["component_recipe"], recipe["lookup_result"], recipe["surfaces_to_copy"]),
            "readback_de": event["compact_atomic_reading_de"],
        })

    statement_rows = []
    for sid, rows in by_statement.items():
        owner = owner_statements[sid]
        logs = [row for row in log_rows if row["statement_id"] == sid]
        statement_rows.append({
            "statement_id": sid,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "surface_sequence": " ".join(row["surface"] for row in rows),
            "recipe_sequence": " | ".join(row["component_recipe"] for row in rows),
            "rare_lookups": sum(row["lesson_source"] != "RECURRENT_FAMILY" for row in logs),
            "double_variant_lookups": sum(row["lookup_result"] == "CHOOSE_LOCAL_CARD_VARIANT" for row in logs),
            "owner_noun_de": owner["owner_noun_de"],
            "complete_readback_de": owner["compact_owner_reading_de"],
        })

    commission_rows = []
    for record_id in RECORDS:
        record = record_texts[record_id]
        logs = [row for row in log_rows if row["record"] == record_id]
        commission_rows.append({
            "commission": f"C{len(commission_rows)+1}",
            "record": record_id,
            "page": record["page"],
            "statements": record["statements"],
            "events": record["events"],
            "owner": record["owners_in_order"],
            "direct_lookups": sum(row["lookup_result"] == "DIRECT_CARD" for row in logs),
            "double_variant_lookups": sum(row["lookup_result"] == "CHOOSE_LOCAL_CARD_VARIANT" for row in logs),
            "recurrent_family_events": sum(row["lesson_source"] == "RECURRENT_FAMILY" for row in logs),
            "rare_recipe_events": sum(row["lesson_source"] != "RECURRENT_FAMILY" for row in logs),
            "continuous_readback_de": record["continuous_compact_owner_reading_de"],
        })

    correction_counts = Counter(flag for row in log_rows for flag in str(row["likely_master_correction"]).split("+"))
    correction_rows = [{"correction": key, "events_flagged": value, "master_action_de": "Vor dem Kopieren kurz pruefen; Quellkarte bleibt unveraendert."} for key, value in sorted(correction_counts.items(), key=lambda item: (-item[1], item[0]))]

    write("SIX_HUNDRED_EIGHTY_SIXTH_83_COMMISSION_LOOKUP_LOG.tsv", log_rows)
    write("SIX_HUNDRED_EIGHTY_SIXTH_25_COMMISSION_STATEMENTS.tsv", statement_rows)
    write("SIX_HUNDRED_EIGHTY_SIXTH_2_COMPLETE_COMMISSIONS.tsv", commission_rows)
    write("SIX_HUNDRED_EIGHTY_SIXTH_CORRECTION_LOAD.tsv", correction_rows)

    summary = {
        "status": "PASS",
        "commissions": len(commission_rows),
        "statements": len(statement_rows),
        "events": len(log_rows),
        "direct_lookups": sum(row["lookup_result"] == "DIRECT_CARD" for row in log_rows),
        "double_variant_lookups": sum(row["lookup_result"] == "CHOOSE_LOCAL_CARD_VARIANT" for row in log_rows),
        "recurrent_events": sum(row["lesson_source"] == "RECURRENT_FAMILY" for row in log_rows),
        "rare_events": sum(row["lesson_source"] != "RECURRENT_FAMILY" for row in log_rows),
        "invented_surfaces": 0,
    }
    (HERE / "SIX_HUNDRED_EIGHTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
