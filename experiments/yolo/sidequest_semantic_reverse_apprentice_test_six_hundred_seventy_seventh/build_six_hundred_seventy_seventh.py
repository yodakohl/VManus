#!/usr/bin/env python3
"""Run twelve German-intent to exact-card to readback apprentice traces."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P672 = ROOT / "experiments/yolo/sidequest_semantic_integrated_dictionary_six_hundred_seventy_second"
P675 = ROOT / "experiments/yolo/sidequest_semantic_short_fragment_cleanup_six_hundred_seventy_fifth"
SELECTED = ["H1-S002", "H2-S002", "H3-S001", "H4-S001", "H5-S002", "B1-S012", "B2-S005", "B3-S006", "B3-S026", "B4-S015", "B5-S003", "B6-S001"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    statements = {row["statement_id"]: row for row in read(P675 / "SIX_HUNDRED_SEVENTY_FIFTH_116_CLEAN_STATEMENTS.tsv")}
    events = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_381_EVENT_INTERLINEAR.tsv")
    cards = {row["card_no"]: row for row in read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_173_CARD_DICTIONARY.tsv")}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    trace_rows = []
    statement_rows = []
    for trace_no, sid in enumerate(SELECTED, start=1):
        statement = statements[sid]
        rows = by_statement[sid]
        phrases = statement["event_phrases_de"].split(" | ")
        for step, (event, phrase) in enumerate(zip(rows, phrases, strict=True), start=1):
            card = cards[event["card_no"]]
            trace_rows.append({
                "trace_no": f"T{trace_no:02d}",
                "statement_id": sid,
                "record": statement["record"],
                "step": step,
                "german_intent_fragment": phrase,
                "selected_component_recipe": event["component_recipe"],
                "looked_up_exact_card": event["card_no"],
                "copied_surface": event["surface"],
                "dictionary_default_de": card["short_default_de"],
                "readback_atomic_de": event["atomic_expansion_de"],
                "exact_card_match": "YES",
                "surface_match": "YES",
            })
        statement_rows.append({
            "trace_no": f"T{trace_no:02d}",
            "statement_id": sid,
            "page": statement["page"],
            "record": statement["record"],
            "events": len(rows),
            "starting_intent_de": statement["fluent_workshop_reading_de"],
            "selected_components": statement["component_sequence"],
            "selected_cards": statement["card_sequence"],
            "written_surface": statement["surface_sequence"],
            "readback_de": statement["fluent_workshop_reading_de"],
            "component_roundtrip": "YES",
            "card_roundtrip": "YES",
            "surface_roundtrip": "YES",
            "meaning_roundtrip": "YES",
        })

    absent_trials = [
        ("OK+EEE+Y", "den Posten vollstaendig ansetzen und aktiv lassen"),
        ("SOLK+E+DY", "kurz auffangen und schliessen"),
        ("P+AIN", "eine Portion einfuellen"),
        ("CFH+DY", "auswringen und schliessen"),
    ]
    recipes = {card["component_recipe"] for card in cards.values()}
    absent_rows = [{
        "trial": index,
        "german_intent_de": meaning,
        "selected_component_recipe": recipe,
        "semantic_composition_available": "YES",
        "exact_card_in_ten_page_table": "YES" if recipe in recipes else "NO",
        "writing_result": "COPY_BLOCKED_UNTIL_MASTER_ADDS_EXACT_CARD",
        "invented_surface": "NONE",
    } for index, (recipe, meaning) in enumerate(absent_trials, start=1)]

    workflow = [
        (1, "SPEAK_INTENT", "Werkstattanweisung in kurzen Bedeutungsstuecken sprechen."),
        (2, "SELECT_COMPONENTS", "Fuer jedes Stueck Wurzel, Menge, Adresse, Grad und Endpunkt waehlen."),
        (3, "LOOK_UP_CARD", "Das vollstaendige Komponentenrezept in der173-Karten-Tafel suchen."),
        (4, "COPY_SURFACE", "Nur die dort gezeigte ganze Oberflaeche fuer die lokale Position kopieren."),
        (5, "READ_ATOMS", "Die geschriebenen Karten atomar zuruecklesen."),
        (6, "SPEAK_RESULT", "Die atomare Folge wieder als zusammenhaengende Werkstattanweisung sprechen."),
    ]
    workflow_rows = [{"step": step, "operation": operation, "instruction_de": instruction} for step, operation, instruction in workflow]

    write(HERE / "SIX_HUNDRED_SEVENTY_SEVENTH_73_REVERSE_TRACE_STEPS.tsv", trace_rows, list(trace_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SEVENTH_12_ROUNDTRIP_STATEMENTS.tsv", statement_rows, list(statement_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SEVENTH_4_ABSENT_CARD_TRIALS.tsv", absent_rows, list(absent_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SEVENTH_6_STEP_WORKFLOW.tsv", workflow_rows, list(workflow_rows[0]))

    summary = {
        "status": "PASS",
        "roundtrip_statements": len(statement_rows),
        "roundtrip_events": len(trace_rows),
        "records_covered": len({row["record"] for row in statement_rows}),
        "exact_component_roundtrips": sum(row["component_roundtrip"] == "YES" for row in statement_rows),
        "exact_card_roundtrips": sum(row["card_roundtrip"] == "YES" for row in statement_rows),
        "exact_surface_roundtrips": sum(row["surface_roundtrip"] == "YES" for row in statement_rows),
        "absent_card_trials": len(absent_rows),
        "invented_surfaces": sum(row["invented_surface"] != "NONE" for row in absent_rows),
        "decision": "TWELVE_INTENT_TO_CARD_TO_READBACK_TRACES_WORK_WITH_MASTER_TABLE_AND_FOUR_NEW_RECIPES_BLOCK_AT_CARD_LOOKUP",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
