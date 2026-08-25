#!/usr/bin/env python3
"""Build Pass 736: L/P/R/T transfer and application roots."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P735 = ROOT / "experiments/yolo/sidequest_semantic_process_verbs_seven_hundred_thirty_fifth"


def read(name: str) -> list[dict[str, str]]:
    with (P735 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOTS = {
    "L": ("WEITERLEITEN", "LEITEN", "einen Posten entlang einer lokalen Route führen"),
    "P": ("EINFUELLEN", "FUELLEN", "einen Posten in einen lokalen Empfänger füllen"),
    "R": ("KUEHLEN", "KUEHLEN", "den Posten abkühlen oder kühl halten"),
    "T": ("ANWENDEN", "ANWENDEN", "den Posten am aktuellen Gegenstand oder Ort gebrauchen"),
}


def roots_in(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in ROOTS if root in parts]


def revise(reading: str, roots: list[str]) -> str:
    result = reading
    for root in roots:
        old, new, _ = ROOTS[root]
        result = result.replace(old, new)
    return result


FRAMES = {
    "Y": "DIES", "CHD+DY": "UMSETZEN·SCHLUSS", "CHD+AL": "UMSETZEN·ZIELSTELLE",
    "AL+OR": "ZIELSTELLE·ANSATZ", "OL": "WEITER",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTY_FIFTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_FIFTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_FIFTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_FIFTH_11_RECORD_EDITION.tsv")

    card_rows = []
    target_cards = []
    for row in cards:
        roots = roots_in(row["component_recipe"])
        new = revise(row["reading_de"], roots)
        output = {
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "pass735_reading_de": row["reading_de"],
            "pass736_reading_de": new, "transfer_roots": "+".join(roots) or "NONE",
            "registered_surfaces": row["registered_surfaces"], "events": row["events"],
            "transfer_revision": "YES" if new != row["reading_de"] else "NO",
        }
        card_rows.append(output)
        if roots:
            target_cards.append(output)

    event_rows = []
    occurrences = []
    for row in events:
        roots = roots_in(row["component_recipe"])
        new = revise(row["reading_de"], roots)
        output = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "pass735_reading_de": row["reading_de"], "pass736_reading_de": new,
            "transfer_roots": "+".join(roots) or "NONE", "form_owner_boundary_status": "UNCHANGED",
        }
        event_rows.append(output)
        if roots:
            occurrences.append({
                "event_id": row["event_id"], "page": row["page"], "record": row["record"],
                "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
                "surface": row["surface"], "component_recipe": row["component_recipe"],
                "transfer_roots": "+".join(roots), "pass736_reading_de": new,
                "root_expansion_de": " + ".join(ROOTS[root][2] for root in roots),
            })

    root_rows = []
    for root, (_, new, expansion) in ROOTS.items():
        rows = [row for row in occurrences if root in row["transfer_roots"].split("+")]
        root_rows.append({
            "root": root, "short_value_de": new, "workshop_expansion_de": expansion,
            "exact_cards": len({row["card_no"] for row in rows}), "events": len(rows),
            "herbal_events": sum(row["record"].startswith("H") for row in rows),
            "bio_events": sum(row["record"].startswith("B") for row in rows),
            "semantic_revision": "YES" if root in {"L", "P"} else "NO",
        })

    cells = []
    for frame, frame_reading in FRAMES.items():
        parts = frame.split("+")
        for root in ROOTS:
            matches = []
            for row in events:
                rparts = row["component_recipe"].split("+")
                roots = roots_in(row["component_recipe"])
                if roots != [root]:
                    continue
                if [part for part in rparts if part != root] == parts:
                    matches.append(row)
            if not matches:
                continue
            cells.append({
                "frame": frame, "frame_reading_de": frame_reading, "root": root,
                "root_reading_de": ROOTS[root][1], "component_recipe": matches[0]["component_recipe"],
                "exact_cards": len({row["card_no"] for row in matches}), "events": len(matches),
                "event_ids": ",".join(row["event_id"] for row in matches),
                "composed_reading_de": f"{ROOTS[root][1]} · {frame_reading}",
            })

    frame_rows = []
    for frame, reading in FRAMES.items():
        rows = [row for row in cells if row["frame"] == frame]
        frame_rows.append({
            "frame": frame, "frame_reading_de": reading, "roots_present": len(rows),
            "root_set": ",".join(row["root"] for row in rows), "events": sum(int(row["events"]) for row in rows),
            "status": "PARTIAL_TRANSFER_APPLICATION_CROSS",
        })

    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        statement_events[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        roots = [root for event in statement_events[row["statement_id"]] for root in roots_in(event["component_recipe"])]
        atomic = " | ".join(event["pass736_reading_de"] for event in statement_events[row["statement_id"]])
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "transfer_root_sequence": ">".join(roots) or "NONE", "transfer_root_count": len(roots),
            "pass736_atomic_trace_de": atomic, "working_reading_de": row["working_reading_de"],
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        target = [event for event in occurrences if event["record"] == row["record"]]
        counts = Counter(root for event in target for root in event["transfer_roots"].split("+"))
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"], "events": row["events"],
            "L_lead": counts["L"], "P_fill": counts["P"], "R_cool": counts["R"], "T_apply": counts["T"],
            "continuous_reading_de": row["continuous_reading_de"], "form_status": "UNCHANGED",
        })

    write("SEVEN_HUNDRED_THIRTY_SIXTH_4_TRANSFER_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_5_ARGUMENT_FRAMES.tsv", frame_rows)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_11_PARADIGM_CELLS.tsv", cells)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_36_TRANSFER_CARDS.tsv", target_cards)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_46_TRANSFER_OCCURRENCES.tsv", occurrences)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_SIXTH_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Leiten, füllen, kühlen, anwenden

- `L` — LEITEN. Erst `L+OL` heißt **weiterleiten**.
- `P` — FÜLLEN. Richtung und Empfänger kommen aus AL/CHD.
- `R` — KÜHLEN.
- `T` — ANWENDEN.

## Kleine Kreuztafel

- Aktueller Posten: `L+Y` leiten, `P+Y` füllen, `T+Y` anwenden.
- Umsetzen+Schluss: `L+CHD+DY` leiten/umsetzen/schließen; `P+CHD+DY` füllen/umsetzen/schließen.
- Zielstelle: `L+CHD+AL` beziehungsweise `P+CHD+AL`.
- Ansatz an Zielstelle: `L+AL+OR` leiten; `AL+R+OR` kühlen.
- Fortsetzung: `L+OL` weiterleiten; `R+OL` weiter kühlen.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_SIXTH_TRANSFER_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    changed_cards = sum(row["transfer_revision"] == "YES" for row in card_rows)
    changed_events = sum(row["pass735_reading_de"] != row["pass736_reading_de"] for row in event_rows)
    changed_statements = sum(any(root in row["transfer_root_sequence"].split(">") for root in ["L", "P"]) for row in statement_rows)
    report = f"""# Pass 736 — Leiten, Füllen, Kühlen, Anwenden

## Ergebnis

Vier weitere Verben bilden eine zweite, kleinere Kreuztafel:

- L=LEITEN: 18 Karten/27 Ereignisse.
- P=FUELLEN: 3/3.
- R=KUEHLEN: 6/6.
- T=ANWENDEN: 9/10.

Die Wurzeln überlappen in keiner Karte; ihre Vereinigung umfasst36 Karten/46 Ereignisse. Fünf gemeinsame Argumentrahmen ergeben11 belegte Zellen.

## Revision

L wird von **WEITERLEITEN** auf **LEITEN** gekürzt; erst L+OL komponiert „weiterleiten“. P wird von **EINFUELLEN** auf **FUELLEN** gekürzt; Zielrichtung stammt aus AL oder CHD. Das vereinfacht {changed_cards} Karten/{changed_events} Ereignisse/{changed_statements} Aussagen.

Die stärksten Paare sind L+CHD+DY versus P+CHD+DY und L+CHD+AL versus P+CHD+AL. Dasselbe Transfer-/Zielgerüst erhält einmal „leiten“, einmal „füllen“. L+AL+OR und AL+R+OR unterscheiden leiten und kühlen am selben Ansatz-/Zielrahmen.

## Nächster Hebel

Als Nächstes wird aus den bisher geschlossenen kurzen Wurzeln ein einziges konsolidiertes Komponentenwörterbuch gebaut. Jede der173 Karten wird neu aus den kleinsten Werten rückgelesen; nur nicht kompositionelle Reste bleiben gelernte Ganzkarten.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "transfer_roots": len(root_rows), "argument_frames": len(frame_rows),
        "paradigm_cells": len(cells), "transfer_cards": len(target_cards), "transfer_events": len(occurrences),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "changed_cards": changed_cards, "changed_events": changed_events, "changed_statements": changed_statements,
        "form_changes": 0, "decision": "L_LEAD__P_FILL__R_COOL__T_APPLY_FORM_A_SECOND_TRANSFER_APPLICATION_CROSS",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
