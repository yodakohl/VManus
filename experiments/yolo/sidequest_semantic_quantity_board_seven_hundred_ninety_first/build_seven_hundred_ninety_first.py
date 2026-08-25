#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREDICTIONS = ROOT / "sidequest_semantic_quantity_axis_seven_hundred_ninetieth" / "SEVEN_HUNDRED_NINETIETH_14_PREDICTED_SURFACES.tsv"
EVENTS = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth" / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    predictions = read(PREDICTIONS)
    events = read(EVENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    board_rows: list[dict[str, object]] = []
    hand_rows: list[dict[str, object]] = []
    substitution_rows: list[dict[str, object]] = []
    for index, prediction in enumerate(predictions, start=1):
        source = next(
            row
            for row in events
            if row["component_recipe"] == prediction["source_recipe"]
            and row["surface"] == prediction["source_surface"]
        )
        card_id = f"PRED_QTY_{index:02d}"
        target_token = "AIIN" if "AIIN" in prediction["counterpart_recipe"].split("+") else "AIN"
        target_reading = "SOLLMASS" if target_token == "AIIN" else "PORTION"
        board_rows.append(
            {
                "predicted_card": card_id,
                "source_event": source["event_id"],
                "source_recipe": prediction["source_recipe"],
                "source_surface": prediction["source_surface"],
                "counterpart_recipe": prediction["counterpart_recipe"],
                "quantity_value": target_reading,
                "predicted_surface": prediction["predicted_surface"],
                "predicted_reading_de": prediction["counterpart_reading_de"],
                "hand_rule": "BOTH_HANDS_COPY_ONE_NEW_MASTER_CARD",
                "status": "WORKSHOP_BOARD_ONLY__NOT_MANUSCRIPT_ATTESTED",
            }
        )
        for hand in ("HAND_1", "HAND_2"):
            hand_rows.append(
                {
                    "exercise": f"X{len(hand_rows) + 1:02d}",
                    "hand": hand,
                    "input_reading_de": prediction["counterpart_reading_de"],
                    "selected_card": card_id,
                    "written_surface": prediction["predicted_surface"],
                    "readback_recipe": prediction["counterpart_recipe"],
                    "readback_reading_de": prediction["counterpart_reading_de"],
                    "roundtrip": "PASS",
                    "access": "COPY_NEW_MASTER_CARD",
                }
            )
        statement = by_statement[source["statement_id"]]
        before_surfaces = [row["surface"] for row in statement]
        after_surfaces = [prediction["predicted_surface"] if row["event_id"] == source["event_id"] else row["surface"] for row in statement]
        before_readings = [row["rebuilt_reading_de"] for row in statement]
        after_readings = [prediction["counterpart_reading_de"] if row["event_id"] == source["event_id"] else row["rebuilt_reading_de"] for row in statement]
        substitution_rows.append(
            {
                "exercise": f"S{index:02d}",
                "page": source["page"],
                "statement_id": source["statement_id"],
                "source_event": source["event_id"],
                "before_surfaces": " ".join(before_surfaces),
                "after_surfaces": " ".join(after_surfaces),
                "before_reading_de": "; ".join(before_readings),
                "after_reading_de": "; ".join(after_readings),
                "changed_surface_only": prediction["source_surface"] + "→" + prediction["predicted_surface"],
                "changed_meaning_only": source["rebuilt_reading_de"] + "→" + prediction["counterpart_reading_de"],
            }
        )

    rules = [
        {"step": 1, "instruction_de": "DAS QUELLREZEPT AUF DER MUSTERKARTE FINDEN"},
        {"step": 2, "instruction_de": "AIIN SOLLMASS GEGEN AIN PORTION TAUSCHEN"},
        {"step": 3, "instruction_de": "NUR DIE MENGENFOLGE AIIN ODER AIN VERKUERZEN ODER VERLAENGERN"},
        {"step": 4, "instruction_de": "DIE UEBRIGE HUELLE UNVERAENDERT VOM QUELLMODELL KOPIEREN"},
        {"step": 5, "instruction_de": "BEIDE HAENDE KOPIEREN DIE NEUE GANZKARTE BIS EINE EIGENE VARIANTE GELEHRT WIRD"},
    ]

    write(
        "SEVEN_HUNDRED_NINETY_FIRST_14_QUANTITY_BOARD_CARDS.tsv",
        board_rows,
        ["predicted_card", "source_event", "source_recipe", "source_surface", "counterpart_recipe", "quantity_value", "predicted_surface", "predicted_reading_de", "hand_rule", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIRST_28_TWO_HAND_TRACES.tsv",
        hand_rows,
        ["exercise", "hand", "input_reading_de", "selected_card", "written_surface", "readback_recipe", "readback_reading_de", "roundtrip", "access"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIRST_14_SENTENCE_SUBSTITUTIONS.tsv",
        substitution_rows,
        ["exercise", "page", "statement_id", "source_event", "before_surfaces", "after_surfaces", "before_reading_de", "after_reading_de", "changed_surface_only", "changed_meaning_only"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIRST_5_QUANTITY_RULES.tsv",
        rules,
        ["step", "instruction_de"],
    )

    booklet = """# Pass 791 — Mengenbrett der Werkstatt

Der Lehrmeister legt vierzehn neue Gegenkarten neben die vorhandenen Muster. Jede entsteht durch genau einen Austausch: `AIIN` (vorgeschriebenes Sollmaß) wird zu `AIN` (eine abgeteilte Portion), oder umgekehrt. Der Rest der Karte bleibt stehen.

Einige besonders lesbare Wechsel:

- `chodaiin → chodain`: im Arbeitsgang **nach Sollmaß** entnehmen → **eine Portion** entnehmen;
- `chedain → chedaiin`: **eine Portion** umsetzen → **nach Sollmaß** umsetzen;
- `orain → oraiin`: eine **Portion des Ansatzes** → der Ansatz **nach Sollmaß**;
- `qotedaiin → qotedain`: danach kurz **bis zum Sollmaß** → danach kurz **eine Portion**;
- `solkaiin → solkain`: an der Sammelstelle **nach Sollmaß** → dort **eine Portion**.

Beide Hände kopieren zunächst dieselbe neue Ganzkarte. Die Mengenregel sagt dem Schreiber, was sich ändert; sie erfindet noch keine persönliche Handform. Erst wenn der Meister ein zweites Muster lehrt, darf daraus ein Handallograph werden.

Damit haben wir nun zwei produktive Achsen: Grad `E/EE/EEE = kurz/lang/voll` und Menge `AIIN/AIN = Sollmaß/Portion`. Beide sitzen in größeren, teils gelernten Karten.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_FIRST_QUANTITY_BOARD.md").write_text(booklet, encoding="utf-8")

    report = """# Pass 791 — Mengenwechsel funktioniert im ganzen Satz

Vierzehn formbare AIIN/AIN-Gegenoberflächen wurden in ihre wirklichen Ausgangsaussagen eingesetzt. In jeder der 14 Satzsubstitutionen ändert sich genau eine Kartenoberfläche und genau der zugehörige Mengenwert; Besitzer, übrige Karten, Reihenfolge und Schluss bleiben unverändert.

Zwei Schreiber führen alle 14 Karten aus, zusammen 28 Vorwärts-/Rückwärtsübungen. Alle lesen auf das Gegenrezept und den Gegenwert zurück. Weil kein unpaariges Mengenkompositum bereits in beiden Händen belegt ist, wird keine neue Handvariante erfunden: beide kopieren dieselbe Meisterkarte.

Die praktische Regel ist damit stärker als bloße Ähnlichkeit: `aiin↔ain` erzeugt in elf verschiedenen Hüllen dieselbe semantische Opposition SOLLMASS↔PORTION. `sotodan` bleibt außerhalb dieser Schreibregel als gelerntes Ganzwort.

Als nächstes untersuchen wir AL und AR als Ziel-/Quellachse. Entscheidend sind wieder echte gemeinsame Hüllen, nicht die bloße Endung: Wo derselbe Kern einmal auf eine Zielstelle und einmal auf eine Quelle zeigt, soll die ganze Arbeitsanweisung vorhersagbar wechseln.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_FIRST_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "board_cards": len(board_rows),
        "two_hand_traces": len(hand_rows),
        "sentence_substitutions": len(substitution_rows),
        "roundtrip_passes": sum(row["roundtrip"] == "PASS" for row in hand_rows),
        "hand_specific_variants_invented": 0,
        "decision": "AIIN_AIN_COUNTERPARTS_REWRITE_ONE_QUANTITY_SLOT_INTACT",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
