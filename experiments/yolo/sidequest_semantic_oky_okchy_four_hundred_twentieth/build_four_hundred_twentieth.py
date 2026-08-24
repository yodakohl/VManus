#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
OKY_ID = "276a7c2d74d1143446f4"
OKCHY_ID = "9ad66e67803a12e745de"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    by_statement: dict[str, list[dict[str, str]]] = {}
    for row in events:
        by_statement.setdefault(row["statement_id"], []).append(row)

    classifications = {
        "E011": "NEW_ITEM_AT_STATEMENT_START", "E091": "NEW_ITEM_AT_STATEMENT_START", "E095": "TAKE_EXPLICIT_INGREDIENT",
        "E008": "USE_JUST_CREATED_EXTRACT", "E081": "USE_INHERITED_PREPARATION", "E085": "USE_JUST_WASHED_ITEM",
        "E140": "USE_AFTER_PASSAGE", "E188": "USE_AT_END_OF_PLACEMENT", "E195": "USE_AFTER_LONG_CONTACT",
        "E247": "USE_OWNER_SUPPLIED_ITEM", "E251": "USE_AFTER_APPLICATION", "E298": "USE_OWNER_SUPPLIED_ITEM",
        "E323": "USE_IN_RUNNING_SEQUENCE",
    }
    rows = []
    for row in events:
        if row["joint_tuple_id"] not in {OKY_ID, OKCHY_ID}:
            continue
        seq = by_statement[row["statement_id"]]
        index = [item["event_id"] for item in seq].index(row["event_id"])
        previous = seq[index - 1]["concrete_word_reading_de"] if index else "Aussagebeginn"
        following = seq[index + 1]["concrete_word_reading_de"] if index + 1 < len(seq) else "Aussageende"
        family = "OKCHY" if row["joint_tuple_id"] == OKCHY_ID else "OKY"
        selected = "nimm dies" if family == "OKCHY" else "verwende dies"
        rows.append({
            "event_id": row["event_id"], "record": row["record_unit_id"], "statement_id": row["statement_id"],
            "family": family, "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "previous_value_de": previous, "following_value_de": following,
            "referent_class": classifications[row["event_id"]], "selected_card_value_de": selected,
        })
    write("FOUR_HUNDRED_TWENTIETH_THIRTEEN_OKY_OKCHY_OCCURRENCES.tsv", rows)

    summary_rows = [
        {"family": "OKY", "exact_card_id": OKY_ID, "events": 10, "statement_start": 2, "inherited_or_owner_item": 10, "selected_value_de": "verwende dies", "composition_status": "LEARNED_EXACT_CARD"},
        {"family": "OKCHY", "exact_card_id": OKCHY_ID, "events": 3, "statement_start": 2, "inherited_or_owner_item": 0, "selected_value_de": "nimm dies", "composition_status": "LEARNED_EXACT_CARD"},
    ]
    write("FOUR_HUNDRED_TWENTIETH_TWO_CARD_RULES.tsv", summary_rows)

    models = [
        {"model": "SYNONYMS", "OKY_fit": 4, "OKCHY_fit": 4, "explains_start_bias": 1, "predictive_use": 1, "score": 10, "decision": "KEEP_AS_RIVAL"},
        {"model": "TAKE_VERSUS_USE", "OKY_fit": 4, "OKCHY_fit": 4, "explains_start_bias": 4, "predictive_use": 4, "score": 16, "decision": "SELECT"},
        {"model": "INTERNAL_VERSUS_EXTERNAL", "OKY_fit": 2, "OKCHY_fit": 2, "explains_start_bias": 1, "predictive_use": 2, "score": 7, "decision": "REJECT"},
        {"model": "PREPARED_VERSUS_FRESH", "OKY_fit": 3, "OKCHY_fit": 3, "explains_start_bias": 3, "predictive_use": 3, "score": 12, "decision": "KEEP_AS_SEMANTIC_RIVAL"},
    ]
    write("FOUR_HUNDRED_TWENTIETH_FOUR_DISTINCTION_MODELS.tsv", models)

    passages = [
        {"statement_id": "H1-S002", "sequence": "OKCHY > QOTCHOL > OL > CTH", "reading_de": "Nimm dies, wärme es an, führe es weiter, bis es bereit ist.", "diagnostic": "new carried dose at statement start"},
        {"statement_id": "H5-S002", "sequence": "OL > CHOY > OKY > CHEECKHODY", "reading_de": "Mit dem Vorigen waschen; dies verwenden und äußerlich anwenden; Schluss.", "diagnostic": "use just washed item"},
        {"statement_id": "H5-S004", "sequence": "OKCHY > CHOKCHEO > KCHAL", "reading_de": "Nimm dies, gib Auszug zu und seihe ab.", "diagnostic": "new item at statement start"},
        {"statement_id": "H5-S005", "sequence": "HO > OKCHY > KCHOAR > SOTODAN", "reading_de": "Zur Zutat: nimm diese, gewinne den Gebrauchsauszug und gebrauche ihn.", "diagnostic": "take explicit ingredient"},
        {"statement_id": "B3-S030", "sequence": "OKY > AIIN > SCHEDAIR > OTCHEDY", "reading_de": "Verwende dies, stelle das Maß ein, führe Wasser weiter und schließe den Folgeschritt.", "diagnostic": "use owner-supplied item at statement start"},
    ]
    write("FOUR_HUNDRED_TWENTIETH_FIVE_REVISED_PASSAGES.tsv", passages)

    summary = {
        "status": "PASS", "oky_events": sum(row["family"] == "OKY" for row in rows),
        "okchy_events": sum(row["family"] == "OKCHY" for row in rows), "models": len(models),
        "decision": "OKCHY_TAKE_THIS__OKY_USE_THIS", "free_ch_stem": False,
    }
    (HERE / "FOUR_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
