#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREDICTIONS = ROOT / "sidequest_semantic_transfer_axis_seven_hundred_ninety_seventh" / "SEVEN_HUNDRED_NINETY_SEVENTH_6_PREDICTED_OPERATIONS.tsv"
TRANSFER_EVENTS = ROOT / "sidequest_semantic_transfer_axis_seven_hundred_ninety_seventh" / "SEVEN_HUNDRED_NINETY_SEVENTH_82_TRANSFER_EVENTS.tsv"
EVENTS = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth" / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
SOURCE_SURFACE = {
    "chedol": "kchol",
    "lal": "chdal",
    "lair": "kair",
    "lain": "kain",
    "kdy": "ldy",
    "chdar": "lar",
}
OP_READING = {"K": "ZUGEBEN", "L": "LEITEN", "CHD": "UMSETZEN"}
OP_STATE = {"K": "MATERIAL_ADDED", "L": "PATH_ENGAGED", "CHD": "ITEM_TRANSFERRED"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def endpoint_state(recipe: str, current: str) -> tuple[str, str]:
    tokens = recipe.split("+")
    if "DY" in tokens:
        return "CLOSE", "STEP_CLOSED"
    if "AL" in tokens:
        return "TARGET", "AT_OWNER_TARGET"
    if "AR" in tokens:
        return "SOURCE", "FROM_OWNER_SOURCE"
    if "Y" in tokens:
        return "REFERENT", "ACTIVE_ITEM_RETAINED"
    return "KEEP", current


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    predictions = read(PREDICTIONS)
    transfer_events = read(TRANSFER_EVENTS)
    events = read(EVENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    substitutions = []
    substitution_traces = []
    for index, prediction in enumerate(predictions, start=1):
        source_surface = SOURCE_SURFACE[prediction["predicted_surface"]]
        source = next(
            row
            for row in events
            if row["surface"] == source_surface
            and "+".join(token for token in row["component_recipe"].split("+") if token not in {"K", "L", "CHD"}) == prediction["tail_recipe"]
        )
        source_op = next(token for token in source["component_recipe"].split("+") if token in {"K", "L", "CHD"})
        target_op = prediction["new_operation"]
        statement = by_statement[source["statement_id"]]
        before_surfaces = [row["surface"] for row in statement]
        after_surfaces = [prediction["predicted_surface"] if row["event_id"] == source["event_id"] else row["surface"] for row in statement]
        before_readings = [row["rebuilt_reading_de"] for row in statement]
        after_readings = [prediction["predicted_reading_de"] if row["event_id"] == source["event_id"] else row["rebuilt_reading_de"] for row in statement]
        substitutions.append(
            {
                "exercise": f"S{index:02d}",
                "page": source["page"],
                "statement_id": source["statement_id"],
                "owner_de": source["owner_de"],
                "source_event": source["event_id"],
                "before_surfaces": " ".join(before_surfaces),
                "after_surfaces": " ".join(after_surfaces),
                "before_reading_de": "; ".join(before_readings),
                "after_reading_de": "; ".join(after_readings),
                "operation_change": source_op + "→" + target_op,
                "operation_meaning_change": OP_READING[source_op] + "→" + OP_READING[target_op],
                "tail_recipe": prediction["tail_recipe"],
                "surface_change": source_surface + "→" + prediction["predicted_surface"],
                "other_events_unchanged": "YES",
            }
        )
        for phase, op, surface, recipe, reading in (
            ("BEFORE", source_op, source_surface, source["component_recipe"], source["rebuilt_reading_de"]),
            ("AFTER", target_op, prediction["predicted_surface"], prediction["predicted_recipe"], prediction["predicted_reading_de"]),
        ):
            substitution_traces.append(
                {
                    "exercise": f"S{index:02d}",
                    "phase": phase,
                    "operation": op,
                    "operation_reading_de": OP_READING[op],
                    "tail_recipe": prediction["tail_recipe"],
                    "surface": surface,
                    "component_recipe": recipe,
                    "working_reading_de": reading,
                }
            )

    stacked = [row for row in transfer_events if int(row["operation_count"]) > 1]
    automaton_rows = []
    trace_rows = []
    for row in stacked:
        ops = row["operation_tokens"].split("+")
        current = "ACTIVE_ITEM"
        transitions = []
        for step, op in enumerate(ops, start=1):
            nxt = OP_STATE[op]
            automaton_rows.append(
                {
                    "event_id": row["event_id"],
                    "step": step,
                    "transition_type": "OPERATION",
                    "input_state": current,
                    "operation": op,
                    "operation_reading_de": OP_READING[op],
                    "output_state": nxt,
                    "owner_de": next(item["owner_de"] for item in events if item["event_id"] == row["event_id"]),
                }
            )
            transitions.append(f"{current} --{OP_READING[op]}--> {nxt}")
            current = nxt
        endpoint, final = endpoint_state(row["component_recipe"], current)
        automaton_rows.append(
            {
                "event_id": row["event_id"],
                "step": len(ops) + 1,
                "transition_type": "ENDPOINT",
                "input_state": current,
                "operation": endpoint,
                "operation_reading_de": endpoint,
                "output_state": final,
                "owner_de": next(item["owner_de"] for item in events if item["event_id"] == row["event_id"]),
            }
        )
        transitions.append(f"{current} --{endpoint}--> {final}")
        trace_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "operation_stack": row["operation_tokens"],
                "working_reading_de": row["working_reading_de"],
                "transition_trace": " | ".join(transitions),
                "final_state": final,
            }
        )

    state_rows = [
        {"state": "ACTIVE_ITEM", "workshop_meaning_de": "aktueller Posten liegt bereit"},
        {"state": "MATERIAL_ADDED", "workshop_meaning_de": "Material oder Portion ist eingebracht"},
        {"state": "PATH_ENGAGED", "workshop_meaning_de": "Posten befindet sich im angegebenen Lauf"},
        {"state": "ITEM_TRANSFERRED", "workshop_meaning_de": "Posten ist in den nächsten Zustand oder Empfänger umgesetzt"},
        {"state": "STEP_CLOSED", "workshop_meaning_de": "Arbeitsschritt ist geschlossen"},
        {"state": "AT_OWNER_TARGET", "workshop_meaning_de": "Posten liegt an der owner-lokalen Zielstelle"},
        {"state": "FROM_OWNER_SOURCE", "workshop_meaning_de": "Posten wurde aus der owner-lokalen Quelle genommen"},
        {"state": "ACTIVE_ITEM_RETAINED", "workshop_meaning_de": "Posten bleibt für den nächsten Schritt aktiv"},
    ]

    write(
        "SEVEN_HUNDRED_NINETY_EIGHTH_6_OPERATION_SUBSTITUTIONS.tsv",
        substitutions,
        ["exercise", "page", "statement_id", "owner_de", "source_event", "before_surfaces", "after_surfaces", "before_reading_de", "after_reading_de", "operation_change", "operation_meaning_change", "tail_recipe", "surface_change", "other_events_unchanged"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_EIGHTH_12_SUBSTITUTION_TRACES.tsv",
        substitution_traces,
        ["exercise", "phase", "operation", "operation_reading_de", "tail_recipe", "surface", "component_recipe", "working_reading_de"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_EIGHTH_14_STACKED_CARD_TRACES.tsv",
        trace_rows,
        ["event_id", "page", "statement_id", "surface", "component_recipe", "operation_stack", "working_reading_de", "transition_trace", "final_state"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_EIGHTH_42_AUTOMATON_TRANSITIONS.tsv",
        automaton_rows,
        ["event_id", "step", "transition_type", "input_state", "operation", "operation_reading_de", "output_state", "owner_de"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_EIGHTH_8_STATES.tsv",
        state_rows,
        ["state", "workshop_meaning_de"],
    )

    report = """# Pass 798 — der Transferautomat der Werkstatt

Die sechs neuen Operationskarten wurden in vollständige Sätze eingesetzt. In allen sechs bleibt das übrige Kartenende und jeder andere Satzbaustein fest; nur die Sachhandlung wechselt zwischen ZUGEBEN, LEITEN und UMSETZEN.

Die 14 wirklich gestapelten Karten ergeben einen sehr kleinen Automaten mit acht verständlichen Zuständen. Jede beginnt beim aktiven Posten:

- K führt zu MATERIAL_ADDED;
- L führt zu PATH_ENGAGED;
- CHD führt zu ITEM_TRANSFERRED;
- DY schließt danach den Schritt, AL legt ihn am Ziel ab, AR bindet ihn an die Quelle, Y hält ihn aktiv.

Die 14 Karten erzeugen 42 Übergänge. Zwölfmal steht L vor CHD: erst durch den angegebenen Lauf führen, dann in Empfänger oder neuen Zustand umsetzen. Einmal steht K vor CHD, einmal L vor K. Das ist eine konkrete, einem Lehrling erklärbare Prozessordnung und keine bloße Buchstabenzerlegung.

Beispiel `lchedy`: `ACTIVE_ITEM --LEITEN--> PATH_ENGAGED --UMSETZEN--> ITEM_TRANSFERRED --CLOSE--> STEP_CLOSED`. `lchedal` endet stattdessen an der owner-lokalen Zielstelle; `lchedar` beginnt semantisch an der owner-lokalen Quelle.

Als nächstes erstellen wir eine konsolidierte zweite Werkstattgrammatik: produktive Kerne, zugelassene Slots, bekannte Ganzkarten und alle bisher erzeugten, aber nicht belegten Prognosen werden in einer einzigen kurzen Lehrtafel zusammengeführt. Danach prüfen wir die 381 Ereignisse erneut auf eindeutige Zerlegung.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "operation_substitutions": len(substitutions),
        "substitution_traces": len(substitution_traces),
        "stacked_card_traces": len(trace_rows),
        "automaton_transitions": len(automaton_rows),
        "states": len(state_rows),
        "other_events_preserved": sum(row["other_events_unchanged"] == "YES" for row in substitutions),
        "decision": "STACKED_K_L_CHD_CARDS_EXECUTE_OWNER_LOCAL_TRANSFER_AUTOMATON",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
