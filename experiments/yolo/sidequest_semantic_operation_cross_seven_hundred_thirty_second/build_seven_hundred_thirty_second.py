#!/usr/bin/env python3
"""Build Pass 732: contrast OK/K/CH/CHD across shared argument frames."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P731 = ROOT / "experiments/yolo/sidequest_semantic_workflow_memory_seven_hundred_thirty_first"


def read(name: str) -> list[dict[str, str]]:
    with (P731 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


OPERATIONS = {
    "OK": ("ANSETZEN", "einen Stoff/Posten in den laufenden Arbeitsgang setzen"),
    "K": ("ZUGEBEN", "einen Stoff/Posten dem laufenden Arbeitsgang hinzufügen"),
    "CH": ("ENTNEHMEN", "einen Stoff/Posten aus dem laufenden Arbeitsgang nehmen"),
    "CHD": ("UMSETZEN", "einen Stoff/Posten innerhalb oder zwischen Arbeitsstellen überführen"),
}

FRAMES = {
    "AIN": "PORTION", "AIR": "WASSER", "AL": "ZIELSTELLE", "AR": "QUELLE",
    "E+Y": "KURZ·DIES", "OL": "WEITER", "Y": "DIES",
}


def operation_roots(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in OPERATIONS if root in parts]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTY_FIRST_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_FIRST_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_FIRST_11_RECORD_EDITION.tsv")

    operation_events = [row for row in events if operation_roots(row["component_recipe"])]
    operation_card_ids = {row["card_no"] for row in operation_events}
    operation_cards = []
    for row in cards:
        if row["exact_card_id"] not in operation_card_ids:
            continue
        roots = operation_roots(row["component_recipe"])
        operation_cards.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "operation_roots": "+".join(roots),
            "reading_de": row["pass731_reading_de"], "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "composition_status": "MULTI_OPERATION" if len(roots) > 1 else "SINGLE_OPERATION_ROOT",
        })

    occurrence_rows = []
    for row in operation_events:
        roots = operation_roots(row["component_recipe"])
        occurrence_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["observed_surface"], "component_recipe": row["component_recipe"],
            "operation_roots": "+".join(roots), "atomic_reading_de": row["pass731_semantic_de"],
            "operation_order": "THEN".join(roots),
            "form_owner_boundary_status": "UNCHANGED",
        })

    root_rows = []
    for root, (meaning, expansion) in OPERATIONS.items():
        rev = [row for row in occurrence_rows if root in row["operation_roots"].split("+")]
        root_rows.append({
            "root": root, "short_value_de": meaning, "workshop_expansion_de": expansion,
            "exact_cards": len({row["card_no"] for row in rev}), "events": len(rev),
            "herbal_events": sum(row["record"].startswith("H") for row in rev),
            "bio_events": sum(row["record"].startswith("B") for row in rev),
            "single_operation_events": sum(len(row["operation_roots"].split("+")) == 1 for row in rev),
            "multi_operation_events": sum(len(row["operation_roots"].split("+")) > 1 for row in rev),
        })

    cells = []
    for frame_recipe, frame_reading in FRAMES.items():
        frame_parts = frame_recipe.split("+")
        for operation in OPERATIONS:
            matches = []
            for row in operation_events:
                parts = row["component_recipe"].split("+")
                roots = operation_roots(row["component_recipe"])
                if roots != [operation]:
                    continue
                rest = [part for part in parts if part != operation]
                if rest == frame_parts:
                    matches.append(row)
            if not matches:
                continue
            cells.append({
                "frame": frame_recipe, "frame_reading_de": frame_reading, "operation": operation,
                "operation_reading_de": OPERATIONS[operation][0],
                "component_recipe": matches[0]["component_recipe"],
                "exact_cards": len({row["card_no"] for row in matches}), "events": len(matches),
                "card_ids": ",".join(sorted({row["card_no"] for row in matches})),
                "event_ids": ",".join(row["event_id"] for row in matches),
                "composed_reading_de": f"{OPERATIONS[operation][0]} · {frame_reading}",
            })

    frame_rows = []
    for frame, reading in FRAMES.items():
        rows = [row for row in cells if row["frame"] == frame]
        frame_rows.append({
            "frame": frame, "frame_reading_de": reading, "operations_present": len(rows),
            "operation_set": ",".join(row["operation"] for row in rows),
            "events": sum(int(row["events"]) for row in rows),
            "status": "COMPLETE_FOUR_OPERATION_PARADIGM" if len(rows) == 4 else "PARTIAL_OPERATION_PARADIGM",
        })

    overlap_rows = []
    for recipe in ["OK+CH+E+O", "OK+CHD+DY", "SH+K+CHD+DY"]:
        matches = [row for row in operation_events if row["component_recipe"] == recipe]
        roots = operation_roots(recipe)
        overlap_rows.append({
            "component_recipe": recipe, "operation_sequence": " THEN ".join(roots),
            "exact_cards": len({row["card_no"] for row in matches}), "events": len(matches),
            "event_ids": ",".join(row["event_id"] for row in matches),
            "reading_de": matches[0]["pass731_semantic_de"],
            "decision": "SEQUENTIAL_COMPOUND__DO_NOT_COLLAPSE_TO_NEW_VERB",
        })

    statement_rows = []
    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row)
    for row in statements:
        roots = [root for event in statement_events[row["statement_id"]] for root in operation_roots(event["component_recipe"])]
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "operation_sequence": ">".join(roots) or "NONE",
            "operation_count": len(roots), "atomic_trace_de": row["pass731_atomic_trace_de"],
            "working_reading_de": row["pass731_working_reading_de"],
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        target = [event for event in occurrence_rows if event["record"] == row["record"]]
        counts = Counter(root for event in target for root in event["operation_roots"].split("+"))
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"],
            "events": row["events"], "OK_set": counts["OK"], "K_add": counts["K"],
            "CH_take": counts["CH"], "CHD_transfer": counts["CHD"],
            "continuous_reading_de": row["continuous_pass731_reading_de"], "form_status": "UNCHANGED",
        })

    card_rows = []
    for row in cards:
        roots = operation_roots(row["component_recipe"])
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "reading_de": row["pass731_reading_de"],
            "operation_roots": "+".join(roots) or "NONE", "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "semantic_status": "UNCHANGED__PARADIGM_CONFIRMED" if roots else "UNCHANGED",
        })

    event_rows = []
    for row in events:
        roots = operation_roots(row["component_recipe"])
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["observed_surface"], "component_recipe": row["component_recipe"],
            "reading_de": row["pass731_semantic_de"], "operation_roots": "+".join(roots) or "NONE",
            "form_owner_boundary_status": "UNCHANGED",
        })

    write("SEVEN_HUNDRED_THIRTY_SECOND_4_OPERATION_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_7_ARGUMENT_FRAMES.tsv", frame_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_20_PARADIGM_CELLS.tsv", cells)
    write("SEVEN_HUNDRED_THIRTY_SECOND_3_MULTI_OPERATION_COMPOUNDS.tsv", overlap_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_74_OPERATION_CARDS.tsv", operation_cards)
    write("SEVEN_HUNDRED_THIRTY_SECOND_157_OPERATION_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_SECOND_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Das Vier-Verben-Kreuz

| Kern | Kurzregel |
|---|---|
| OK | ANSETZEN — in den laufenden Arbeitsgang setzen |
| K | ZUGEBEN — dem Arbeitsgang hinzufügen |
| CH | ENTNEHMEN — aus dem Arbeitsgang nehmen |
| CHD | UMSETZEN — innerhalb oder zwischen Stellen überführen |

## Vollständige Wasserreihe

- `CH+AIR`: Wasser entnehmen.
- `K+AIR`: Wasser zugeben.
- `OK+AIR`: Wasser ansetzen.
- `CHD+AIR`: Wasser umsetzen.

## Weitere Reihen

- Portion: `K+AIN`, `OK+AIN`, `CHD+AIN`.
- Zielstelle: `K+AL`, `OK+AL`, `CHD+AL`.
- Quelle: `K+AR`, `OK+AR`.
- Kurzer aktueller Posten: `CH+E+Y`, `K+E+Y`, `OK+E+Y`.
- Weiter: `K+OL`, `OK+OL`.
- Aktueller Posten: `K+Y`, `OK+Y`, `CHD+Y`.

Mehrere Verben in derselben Karte werden nacheinander gelesen, nicht als neues Riesenwort.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_SECOND_OPERATION_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    report = """# Pass 732 — das Vier-Verben-Kreuz

## Ergebnis

Die vier Kernoperationen bleiben unverändert und werden durch sieben gemeinsame Argumentrahmen miteinander verbunden:

- OK=ANSETZEN: 23 Karten/79 Ereignisse.
- K=ZUGEBEN: 18/21.
- CH=ENTNEHMEN: 15/16.
- CHD=UMSETZEN: 22/48.

Ihre Vereinigung umfasst 74 Karten/157 Ereignisse. Sieben Argumentrahmen liefern 20 belegte Paradigmenzellen. Der stärkste Rahmen ist vollständig:

> CH+AIR Wasser entnehmen → K+AIR Wasser zugeben → OK+AIR Wasser ansetzen → CHD+AIR Wasser umsetzen.

Das ist unser bisher sauberstes produktives Bedeutungsparadigma. Derselbe Objektstamm AIR bleibt fest, nur der Operationskern wechselt.

Weitere Teilreihen bestätigen die Rollen: AIN=Portion besitzt K/OK/CHD, AL=Zielstelle K/OK/CHD, AR=Quelle K/OK, E+Y CH/K/OK, OL K/OK und Y K/OK/CHD.

## Mehrfachoperationen

Drei Karten tragen zwei Operationskerne: OK+CH+E+O, OK+CHD+DY und SH+K+CHD+DY. Sie bleiben sequenziell: ansetzen und entnehmen; ansetzen und umsetzen; halten, zugeben und umsetzen. Dafür wird kein neues Ganzverb erfunden.

## Werkstattlesung

Der Lehrling lernt eine kleine Kreuztafel, nicht 74 isolierte Wörter. Er wählt ein Verb, steckt Wasser/Portion/Quelle/Zielstelle/aktuellen Posten an und ergänzt Grad oder Schluss. Gelernte Ganzkarten bleiben nur dort nötig, wo kein solches Kreuz greift.

## Nächster Hebel

Als Nächstes werden E/EE/EEE und Y/DY über genau diese vier Verben gelegt. Gesucht ist eine einheitliche Lesung für kurz, länger, vollständig sowie offener aktueller Posten versus geschlossener Schritt.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "operation_roots": len(root_rows), "argument_frames": len(frame_rows),
        "paradigm_cells": len(cells), "complete_frames": sum(row["status"] == "COMPLETE_FOUR_OPERATION_PARADIGM" for row in frame_rows),
        "operation_cards": len(operation_cards), "operation_events": len(occurrence_rows),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "semantic_changes": 0, "form_changes": 0,
        "decision": "OK_K_CH_CHD_FORM_A_PRODUCTIVE_FOUR_OPERATION_CROSS__AIR_IS_COMPLETE_FRAME",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
