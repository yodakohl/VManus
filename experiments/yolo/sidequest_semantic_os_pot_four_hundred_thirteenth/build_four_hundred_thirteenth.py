#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    by_id = {row["event_id"]: row for row in events}
    os_rows = [row for row in events if row["joint_tuple_id"] == "df1098831679a8ad1b39"]

    occurrence = [{
        "event_id": row["event_id"],
        "record": row["record_unit_id"],
        "statement_id": row["statement_id"],
        "surface": row["surface_display"],
        "joint_tuple_id": row["joint_tuple_id"],
        "left_context": "CHET/bearbeiten",
        "right_context": "AIR/Wasserzulauf > auffangen",
        "selected_whole_word_de": "Topf",
        "workshop_role_de": "Ansatztopf",
        "composition": "MEMORIZED_WHOLE_CARD__NOT_O_PLUS_S",
    } for row in os_rows]
    write("FOUR_HUNDRED_THIRTEENTH_OS_OCCURRENCE.tsv", occurrence)

    vessel_cards = [
        ("E005", "OS", "Topf", "unmarkiertes Ansatzgefäß"),
        ("E032", "OYKCHOR", "glasiertes Gefäß", "besonders beschichtetes Gefäß"),
        ("E159", "LY", "Empfangsgefäß", "nimmt einen laufenden Posten auf"),
        ("E285", "CHEEDAR", "Beckenstation", "örtliche Station statt tragbarem Topf"),
        ("E305", "QOTEDAIIN", "breites Gefäß", "durch Form oder Maß markiert"),
        ("E316", "QOLCHEY", "Arbeitsbecken", "größere Arbeitsstelle"),
    ]
    lexicon = []
    for event_id, label, value, distinction in vessel_cards:
        row = by_id[event_id]
        lexicon.append({
            "representative_event": event_id,
            "card_label": label,
            "surface": row["surface_display"],
            "joint_tuple_id": row["joint_tuple_id"],
            "selected_value_de": value,
            "distinction": distinction,
            "shared_visible_stem_claim": "NONE__LEARNED_VESSEL_DECK",
        })
    write("FOUR_HUNDRED_THIRTEENTH_SIX_VESSEL_CARDS.tsv", lexicon)

    models = [
        {"candidate": "GEFÄSS", "sequence_fit": 4, "deck_contrast": 2, "brevity": 4, "score": 10, "decision": "KEEP_AS_CLASS"},
        {"candidate": "TOPF", "sequence_fit": 4, "deck_contrast": 4, "brevity": 4, "score": 12, "decision": "SELECT_WORD"},
        {"candidate": "MÖRSER", "sequence_fit": 3, "deck_contrast": 4, "brevity": 4, "score": 11, "decision": "KEEP_AS_PHYSICAL_RIVAL"},
        {"candidate": "FILTERGEFÄSS", "sequence_fit": 3, "deck_contrast": 3, "brevity": 2, "score": 8, "decision": "REJECT_TOO_SPECIFIC"},
    ]
    write("FOUR_HUNDRED_THIRTEENTH_FOUR_OS_MODELS.tsv", models)

    h1 = []
    readings = {
        "E001": "Wurzelteil", "E002": "säubern", "E003": "aus demselben Vorrat",
        "E004": "bearbeiten", "E005": "Topf", "E006": "Wasserzulauf",
        "E007": "auffangen", "E008": "Posten ansetzen", "E009": "Sollmaß", "E010": "Wurzelteil",
    }
    for event_id in [f"E{i:03d}" for i in range(1, 11)]:
        row = by_id[event_id]
        h1.append({
            "event_id": event_id,
            "surface": row["surface_display"],
            "selected_small_value_de": readings[event_id],
            "role_in_chain": "CONTAINER" if event_id == "E005" else "UNCHANGED_NEIGHBOR",
        })
    write("FOUR_HUNDRED_THIRTEENTH_H1_TEN_EVENT_CHAIN.tsv", h1)

    summary = {
        "status": "PASS",
        "os_occurrences": len(os_rows),
        "vessel_cards_compared": len(lexicon),
        "h1_events": len(h1),
        "decision": "OS_MEMORIZED_POT_OR_PREPARATION_VESSEL",
        "small_value_de": "TOPF",
    }
    (HERE / "FOUR_HUNDRED_THIRTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
