#!/usr/bin/env python3
"""Build Pass 735: consolidate prepare/hold/settle/warm/wash roots."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P734 = ROOT / "experiments/yolo/sidequest_semantic_workshop_inventory_seven_hundred_thirty_fourth"


def read(name: str) -> list[dict[str, str]]:
    with (P734 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOTS = {
    "CTH": ("BEREITEN", "den laufenden Posten arbeitsbereit machen"),
    "SH": ("HALTEN", "den Posten im aktuellen Zustand oder an der aktuellen Stelle halten"),
    "SHED": ("ABSETZEN", "den Posten ruhen, sich setzen oder stehen lassen"),
    "CHK": ("WAERMEN", "den Posten auf Arbeitswärme bringen oder warm halten"),
    "LSH": ("WASCHEN", "den Arbeitsgang oder Posten kurz durchwaschen"),
}


def roots_in(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in ROOTS if root in parts]


CELL_SPECS = [
    ("PV01", "CTH+Y", "diesen Posten bereiten"),
    ("PV02", "CTH+E+Y", "diesen Posten kurz bereiten"),
    ("PV03", "CTH+AIIN", "bis zum Sollmaß bereiten"),
    ("PV04", "SH", "halten"),
    ("PV05", "SH+E+Y", "diesen Posten kurz halten"),
    ("PV06", "SH+EE+Y", "diesen Posten lange halten"),
    ("PV07", "SH+E+DY", "kurz halten und schließen"),
    ("PV08", "SH+EE+DY", "lange halten und schließen"),
    ("PV09", "SHED+DY", "absetzen lassen und schließen"),
    ("PV10", "SHED+AL", "an der Zielstelle absetzen lassen"),
    ("PV11", "CHK+E+Y", "diesen Posten kurz wärmen"),
    ("PV12", "CHK+EE+Y", "diesen Posten lange warm halten"),
    ("PV13", "CHK+EE+DY", "lange warm halten und schließen"),
    ("PV14", "LSH+O", "den Arbeitsgang waschen"),
    ("PV15", "LSH+E+DY", "kurz waschen und schließen"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_FOURTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_FOURTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_FOURTH_11_RECORD_EDITION.tsv")

    target_events = [row for row in events if roots_in(row["component_recipe"])]
    target_cards_ids = {row["card_no"] for row in target_events}
    target_cards = []
    for row in cards:
        if row["exact_card_id"] not in target_cards_ids:
            continue
        roots = roots_in(row["component_recipe"])
        target_cards.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "process_roots": "+".join(roots),
            "reading_de": row["pass734_reading_de"], "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "semantic_status": "UNCHANGED__SHORT_ROOT_CONFIRMED",
        })

    occurrence_rows = []
    for row in target_events:
        roots = roots_in(row["component_recipe"])
        occurrence_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "process_roots": "+".join(roots), "reading_de": row["pass734_reading_de"],
            "root_expansion_de": " + ".join(ROOTS[root][1] for root in roots),
            "form_owner_boundary_status": "UNCHANGED",
        })

    root_rows = []
    for root, (meaning, expansion) in ROOTS.items():
        rows = [row for row in occurrence_rows if root in row["process_roots"].split("+")]
        root_rows.append({
            "root": root, "short_value_de": meaning, "workshop_expansion_de": expansion,
            "exact_cards": len({row["card_no"] for row in rows}), "events": len(rows),
            "herbal_events": sum(row["record"].startswith("H") for row in rows),
            "bio_events": sum(row["record"].startswith("B") for row in rows),
            "family_rule": "SEPARATE_ROOT__DO_NOT_MERGE_BY_SURFACE_SIMILARITY",
        })

    cell_rows = []
    for ident, recipe, reading in CELL_SPECS:
        rows = [row for row in events if row["component_recipe"] == recipe]
        cell_rows.append({
            "cell_id": ident, "component_recipe": recipe, "process_roots": "+".join(roots_in(recipe)),
            "exact_cards": len({row["card_no"] for row in rows}), "events": len(rows),
            "event_ids": ",".join(row["event_id"] for row in rows), "fluent_reading_de": reading,
        })

    overlap_rows = []
    for recipe in ["SH+E+CTH+CHD+Y", "SH+E+CTH+Y"]:
        rows = [row for row in events if row["component_recipe"] == recipe]
        overlap_rows.append({
            "component_recipe": recipe, "process_sequence": "HALTEN THEN BEREITEN",
            "exact_cards": len({row["card_no"] for row in rows}), "events": len(rows),
            "event_ids": ",".join(row["event_id"] for row in rows),
            "reading_de": rows[0]["pass734_reading_de"],
            "decision": "SEQUENTIAL_COMPOSITION__SH_AND_CTH_REMAIN_DISTINCT",
        })

    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        roots = [root for event in statement_events[row["statement_id"]] for root in roots_in(event["component_recipe"])]
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "process_root_sequence": ">".join(roots) or "NONE", "process_root_count": len(roots),
            "atomic_trace_de": row["pass734_atomic_trace_de"], "working_reading_de": row["pass734_working_reading_de"],
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        target = [event for event in occurrence_rows if event["record"] == row["record"]]
        counts = Counter(root for event in target for root in event["process_roots"].split("+"))
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"], "events": row["events"],
            "CTH_prepare": counts["CTH"], "SH_hold": counts["SH"], "SHED_settle": counts["SHED"],
            "CHK_warm": counts["CHK"], "LSH_wash": counts["LSH"],
            "continuous_reading_de": row["continuous_pass734_reading_de"], "form_status": "UNCHANGED",
        })

    card_rows = []
    for row in cards:
        roots = roots_in(row["component_recipe"])
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "reading_de": row["pass734_reading_de"],
            "process_roots": "+".join(roots) or "NONE", "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "semantic_status": "UNCHANGED",
        })
    event_rows = []
    for row in events:
        roots = roots_in(row["component_recipe"])
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "reading_de": row["pass734_reading_de"], "process_roots": "+".join(roots) or "NONE",
            "form_owner_boundary_status": "UNCHANGED",
        })

    write("SEVEN_HUNDRED_THIRTY_FIFTH_5_PROCESS_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_15_CANONICAL_PROCESS_CELLS.tsv", cell_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_2_SH_CTH_OVERLAPS.tsv", overlap_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_35_PROCESS_CARDS.tsv", target_cards)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_63_PROCESS_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_FIFTH_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Fünf kurze Prozessverben

- `CTH` — BEREITEN.
- `SH` — HALTEN.
- `SHED` — ABSETZEN.
- `CHK` — WÄRMEN.
- `LSH` — WASCHEN.

SH und SHED bleiben verschieden: SH hält einen Posten aktiv und kann mit E/EE offen oder geschlossen erscheinen; SHED lässt ihn sich setzen und ist meist ein abgeschlossener Arbeitsschritt. CHK nimmt dieselben Grade kurz/lang. LSH ist die kleine Waschhandlung.

`shey/cheey` ist keine Satzabkürzung „bis die Flüssigkeit klar abläuft“. Die gelernte Karte ist `SH+EE+Y`: **diesen Posten lange halten**.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_FIFTH_PROCESS_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    report = """# Pass 735 — fünf kurze Prozessverben

## Ergebnis

Fünf weitere Fachkerne bleiben klein und getrennt:

- CTH=BEREITEN: 8 Karten/15 Ereignisse.
- SH=HALTEN: 20/25.
- SHED=ABSETZEN: 3/15.
- CHK=WÄRMEN: 4/7.
- LSH=WASCHEN: 2/3.

Ihre Vereinigung umfasst35 Karten/63 Ereignisse; nur zwei Karten kombinieren SH und CTH, beide als lesbare Folge „kurz halten, bereiten“. Es gibt keinen Grund, SH/SHED oder CHK/CKH wegen ähnlicher Schriftbilder zusammenzuwerfen.

## Fünfzehn kanonische Zellen

Die klarsten Reihen sind CTH+Y / CTH+E+Y / CTH+AIIN; SH mit kurz/lang und Y/DY; SHED+DY / SHED+AL; CHK+E+Y / CHK+EE+Y / CHK+EE+DY; sowie LSH+O / LSH+E+DY. Grad, aktueller Posten, Zielstelle und Schluss stammen aus den bereits geschlossenen Komponenten.

## Wichtige Wörterbuchkorrektur

Die alte, viel zu komplexe Lesung `shey = bis die Flüssigkeit klar abläuft` bleibt endgültig zurückgezogen. `cheey|shey` und `sheey` realisieren dieselbe einfache Komposition SH+EE+Y: **diesen Posten lange halten**. Klarlauf wäre zusätzlicher, hier nicht kodierter Inhalt.

## Nächster Hebel

Als Nächstes wird das Transfersystem L/P/R/T geprüft: weiterleiten, einfüllen, kühlen und anwenden. Daraus soll zusammen mit Quelle/Zielstelle die zweite Hälfte des praktischen Verbrasters entstehen.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "process_roots": len(root_rows), "canonical_cells": len(cell_rows),
        "overlap_cards": len(overlap_rows), "process_cards": len(target_cards), "process_events": len(occurrence_rows),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "semantic_changes": 0, "form_changes": 0,
        "retired_complex_shey_gloss": "UNTIL_CLEAR_LIQUID_RUNS_OUT",
        "replacement_shey_gloss": "SH_PLUS_EE_PLUS_Y__HOLD_CURRENT_ITEM_LONG",
        "decision": "CTH_SH_SHED_CHK_LSH_REMAIN_FIVE_SHORT_DISTINCT_PROCESS_ROOTS",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
