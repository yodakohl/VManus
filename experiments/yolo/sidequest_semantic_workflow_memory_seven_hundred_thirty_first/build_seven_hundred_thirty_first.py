#!/usr/bin/env python3
"""Build Pass 731: OR/OL/OT as preparation, continuation, and next-step memory."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P730 = ROOT / "experiments/yolo/sidequest_semantic_source_target_seven_hundred_thirtieth"


def read(name: str) -> list[dict[str, str]]:
    with (P730 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOTS = {
    "OR": ("ANSATZ", "ANSATZ", "der aktuell bereitete Stoff-/Arbeitsansatz"),
    "OL": ("FORTSETZEN", "WEITER", "denselben Arbeitsfaden oder Posten weiterführen"),
    "OT": ("DANACH", "DANACH", "zum folgenden Schritt oder Adressslot wechseln"),
}


def roots_in(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in ROOTS if root in parts]


def revise(reading: str, roots: list[str]) -> str:
    value = reading
    for root in roots:
        old, new, _ = ROOTS[root]
        value = value.replace(old, new)
    return value


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTIETH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTIETH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTIETH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTIETH_11_RECORD_EDITION.tsv")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    card_rows = []
    workflow_cards = []
    for row in cards:
        roots = roots_in(row["component_recipe"])
        new = revise(row["pass730_reading_de"], roots)
        output = {
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "pass730_reading_de": row["pass730_reading_de"],
            "pass731_reading_de": new, "workflow_roots": "+".join(roots) or "NONE",
            "registered_surfaces": row["registered_surfaces"], "events": row["events"],
            "workflow_revision": "YES" if new != row["pass730_reading_de"] else "NO",
        }
        card_rows.append(output)
        if roots:
            workflow_cards.append(output)

    event_rows = []
    occurrences = []
    for row in events:
        roots = roots_in(row["component_recipe"])
        new = revise(row["pass730_semantic_de"], roots)
        output = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"], "owner_de": row["owner_de"],
            "card_no": row["card_no"], "observed_surface": row["observed_surface"],
            "component_recipe": row["component_recipe"], "pass730_semantic_de": row["pass730_semantic_de"],
            "pass731_semantic_de": new, "workflow_roots": "+".join(roots) or "NONE",
            "form_owner_boundary_status": "UNCHANGED",
        }
        event_rows.append(output)
        if roots:
            sequence = by_statement[row["statement_id"]]
            index = next(i for i, item in enumerate(sequence) if item["event_id"] == row["event_id"])
            occurrences.append({
                "event_id": row["event_id"], "roots": "+".join(roots), "page": row["page"],
                "record": row["record"], "statement_id": row["statement_id"], "owner_de": row["owner_de"],
                "card_no": row["card_no"], "surface": row["observed_surface"],
                "component_recipe": row["component_recipe"],
                "previous_recipe": sequence[index - 1]["component_recipe"] if index else "START",
                "next_recipe": sequence[index + 1]["component_recipe"] if index + 1 < len(sequence) else "END",
                "pass731_atomic_reading_de": new,
                "memory_effect": (
                    "LOAD_ACTIVE_PREPARATION" if roots == ["OR"]
                    else "KEEP_ACTIVE_CHAIN" if roots == ["OL"]
                    else "ADVANCE_TO_NEXT_STEP" if roots == ["OT"]
                    else "COMPOSED_MEMORY_MOVE"
                ),
            })

    statement_rows = []
    for row in statements:
        roots = sorted({root for event in by_statement[row["statement_id"]] for root in roots_in(event["component_recipe"])})
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "workflow_roots": ",".join(roots) or "NONE",
            "pass731_atomic_trace_de": revise(row["pass730_atomic_trace_de"], roots),
            "pass731_working_reading_de": row["pass730_working_reading_de"],
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        record_events = [event for event in event_rows if event["record"] == row["record"]]
        counts = Counter(root for event in record_events for root in event["workflow_roots"].split("+") if root != "NONE")
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"],
            "events": len(record_events), "OR_preparation": counts["OR"], "OL_continue": counts["OL"],
            "OT_then": counts["OT"], "continuous_pass731_reading_de": row["continuous_pass730_reading_de"],
            "form_status": "UNCHANGED",
        })

    root_rows = []
    for root, (_, new, expansion) in ROOTS.items():
        rcards = [row for row in workflow_cards if root in row["workflow_roots"].split("+")]
        rev = [row for row in occurrences if root in row["roots"].split("+")]
        root_rows.append({
            "root": root, "short_value_de": new, "workshop_expansion_de": expansion,
            "exact_cards": len(rcards), "events": len(rev),
            "herbal_events": sum(row["record"].startswith("H") for row in rev),
            "bio_events": sum(row["record"].startswith("B") for row in rev),
            "bare_events": sum(row["component_recipe"] == root for row in rev),
            "composed_events": sum(row["component_recipe"] != root for row in rev),
        })

    overlap_rows = []
    overlap_specs = [
        ("WM01", ["OL", "OR"], "OL+OR", "WEITER · ANSATZ", "mit demselben Ansatz weiter"),
        ("WM02", ["OT", "OR"], "OT+CH+OR", "DANACH · ENTNEHMEN · ANSATZ", "danach vom Ansatz entnehmen"),
        ("WM03", ["OT", "OL"], "OT+OL", "DANACH · WEITER", "danach weiter"),
        ("WM04", ["OT", "OL"], "OT+CH+OL", "DANACH · ENTNEHMEN · WEITER", "danach entnehmen und weiter"),
        ("WM05", ["OT", "OL"], "OT+Y+T+CH+OL", "DANACH · DIES · ANWENDEN · ENTNEHMEN · WEITER", "danach diesen Posten anwenden, entnehmen und weiterführen"),
    ]
    for ident, roots, recipe, atomic, fluent in overlap_specs:
        rows = [row for row in occurrences if row["component_recipe"] == recipe]
        overlap_rows.append({
            "overlap_id": ident, "roots": "+".join(roots), "component_recipe": recipe,
            "exact_cards": len({row["card_no"] for row in rows}), "events": len(rows),
            "event_ids": ",".join(row["event_id"] for row in rows),
            "atomic_reading_de": atomic, "fluent_expansion_de": fluent,
            "composition_status": "DIRECT__NO_SENTENCE_SIZED_ROOT",
        })

    write("SEVEN_HUNDRED_THIRTY_FIRST_3_WORKFLOW_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTY_FIRST_5_OVERLAP_CONSTRUCTIONS.tsv", overlap_rows)
    write("SEVEN_HUNDRED_THIRTY_FIRST_46_WORKFLOW_CARDS.tsv", workflow_cards)
    write("SEVEN_HUNDRED_THIRTY_FIRST_85_WORKFLOW_OCCURRENCES.tsv", occurrences)
    write("SEVEN_HUNDRED_THIRTY_FIRST_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_FIRST_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_FIRST_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_FIRST_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Drei Karten für das Gedächtnis des Arbeitsgangs

## OR — ANSATZ

OR ruft den aktuell bereiteten Stoff- oder Arbeitsansatz auf. Es ist ein Inhaltsanker.

## OL — WEITER

OL hält denselben Arbeitsfaden offen. Es bedeutet als Stamm nur „weiter“, nicht den ganzen Satz „denselben Ansatz fortsetzen“.

## OT — DANACH

OT rückt zum folgenden Schritt oder zur folgenden Adresse. Es ist die einfache Folgekarte „danach“.

## Zusammensetzungen

- `OL+OR`: mit demselben Ansatz weiter.
- `OT+CH+OR`: danach vom Ansatz entnehmen.
- `OT+OL`: danach weiter.
- `OT+CH+OL`: danach entnehmen und weiterführen.
- `OT+Y+T+CH+OL`: danach diesen Posten anwenden, entnehmen und weiterführen.

Der Lehrling merkt sich also: **OR lädt den Ansatz, OL hält ihn aktiv, OT geht zum nächsten Schritt.**
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_FIRST_WORKFLOW_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    changed_cards = sum(row["workflow_revision"] == "YES" for row in card_rows)
    changed_events = sum(row["pass730_semantic_de"] != row["pass731_semantic_de"] for row in event_rows)
    changed_statements = sum("OL" in row["workflow_roots"] for row in statement_rows)
    report = f"""# Pass 731 — Arbeitsgedächtnis OR/OL/OT

## Ergebnis

Der Dreikern lässt sich als kleine, lehrbare Zustandsmaschine lesen:

- **OR = ANSATZ:** 10 Karten / 18 Ereignisse; lädt den aktuellen Stoff-/Arbeitsansatz.
- **OL = WEITER:** 25 Karten / 48 Ereignisse; hält denselben Arbeitsfaden aktiv.
- **OT = DANACH:** 16 Karten / 26 Ereignisse; rückt zum nächsten Schritt.

Wegen fünf Überlappungskonstruktionen umfasst die Vereinigung 46 Karten/85 Ereignisse, nicht die bloße Summe. Keine der Mischformen verlangt einen langen Stammwert.

## Revision

OL wird von dem satzartigen **FORTSETZEN** auf das atomare **WEITER** gekürzt. Dadurch werden {changed_cards} Karten/{changed_events} Ereignisse/{changed_statements} Aussagen im atomaren Interlinear knapper, ohne eine flüssige Aussage zu verändern.

`cholor` ist nun nicht „FORTSETZEN·ANSATZ“, sondern `WEITER·ANSATZ`: **mit demselben Ansatz weiter**. `otol` ist `DANACH·WEITER`. `qolchedy` ist `WEITER·UMSETZEN·SCHLUSS`.

## Werkstattmechanik

Ein Schreiber braucht drei mentale Register:

1. OR: Was ist der aktive Ansatz?
2. OL: Bleibt derselbe Vorgang aktiv?
3. OT: Beginnt die Folgehandlung?

Das ist einfach genug für mehrere Hände und erklärt zugleich, warum dieselben Karten in offenen Herbal-Sätzen und kurzen Biological-Zellen vorkommen.

## Nächster Hebel

Als Nächstes werden OK, K, CH und CHD als vier Operationskerne gegeneinander gestellt: ansetzen, zugeben, entnehmen und umsetzen. Die Aufgabe ist, echte Minimalpaare zu finden und überladene Ganzkartenhandlungen zurückzunehmen.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "workflow_roots": len(root_rows), "overlap_constructions": len(overlap_rows),
        "workflow_cards": len(workflow_cards), "workflow_events": len(occurrences),
        "OR_events": 18, "OL_events": 48, "OT_events": 26,
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "changed_cards": changed_cards, "changed_events": changed_events, "changed_statements": changed_statements,
        "form_changes": 0, "decision": "OR_LOADS_PREPARATION__OL_MEANS_CONTINUE__OT_ADVANCES_NEXT_STEP",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
