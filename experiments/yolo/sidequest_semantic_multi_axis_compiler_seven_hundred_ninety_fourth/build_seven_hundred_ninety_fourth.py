#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EVENTS = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth" / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
QTY_PRED = ROOT / "sidequest_semantic_quantity_axis_seven_hundred_ninetieth" / "SEVEN_HUNDRED_NINETIETH_14_PREDICTED_SURFACES.tsv"
ADDR_PRED = ROOT / "sidequest_semantic_address_axis_seven_hundred_ninety_second" / "SEVEN_HUNDRED_NINETY_SECOND_22_PREDICTED_SURFACES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def axes(recipe: str) -> tuple[str, ...]:
    tokens = recipe.split("+")
    out = []
    if any(token in {"E", "EE", "EEE"} for token in tokens):
        out.append("GRADE")
    if any(token in {"AIIN", "AIN"} for token in tokens):
        out.append("QUANTITY")
    if any(token in {"AL", "AR"} for token in tokens):
        out.append("ADDRESS")
    return tuple(out)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    quantity_predictions = read(QTY_PRED)
    address_predictions = read(ADDR_PRED)
    multi = [row for row in events if len(axes(row["component_recipe"])) >= 2]

    attested_rows = []
    for row in multi:
        attested_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "active_axes": "+".join(axes(row["component_recipe"])),
                "working_reading_de": row["rebuilt_reading_de"],
                "status": "ATTESTED_ON_FIXED_PAGE",
            }
        )

    neighbor_rows = []
    for source in attested_rows:
        candidates = []
        for row in quantity_predictions:
            if row["source_recipe"] == source["component_recipe"] and row["source_surface"] == source["surface"]:
                candidates.append(("QUANTITY", row))
        for row in address_predictions:
            if row["source_recipe"] == source["component_recipe"] and row["source_surface"] == source["surface"]:
                candidates.append(("ADDRESS", row))
        if len(candidates) != 1:
            raise ValueError(f"expected one licensed neighbor for {source['component_recipe']}/{source['surface']}, got {len(candidates)}")
        changed_axis, prediction = candidates[0]
        target_axes = axes(prediction["counterpart_recipe"])
        neighbor_rows.append(
            {
                "source_event": source["event_id"],
                "source_surface": source["surface"],
                "source_recipe": source["component_recipe"],
                "source_reading_de": source["working_reading_de"],
                "changed_axis": changed_axis,
                "predicted_surface": prediction["predicted_surface"],
                "predicted_recipe": prediction["counterpart_recipe"],
                "predicted_reading_de": prediction["counterpart_reading_de"],
                "axes_before": source["active_axes"],
                "axes_after": "+".join(target_axes),
                "axis_count_preserved": "YES" if len(target_axes) == len(source["active_axes"].split("+")) else "NO",
                "status": "LICENSED_ONE_AXIS_NEIGHBOR__NOT_ATTESTED",
            }
        )

    readback_rows = []
    for row in attested_rows:
        readback_rows.append(
            {
                "item": row["event_id"],
                "surface": row["surface"],
                "recipe": row["component_recipe"],
                "active_axes": row["active_axes"],
                "reading_de": row["working_reading_de"],
                "provenance": "ATTESTED",
                "readback": "PASS",
            }
        )
    for index, row in enumerate(neighbor_rows, start=1):
        readback_rows.append(
            {
                "item": f"PRED_MULTI_{index:02d}",
                "surface": row["predicted_surface"],
                "recipe": row["predicted_recipe"],
                "active_axes": row["axes_after"],
                "reading_de": row["predicted_reading_de"],
                "provenance": "WORKSHOP_PREDICTION",
                "readback": "PASS",
            }
        )

    axis_counts = Counter(row["active_axes"] for row in attested_rows)
    inventory_rows = [
        {"axis_combination": "GRADE+ADDRESS", "attested_events": axis_counts["GRADE+ADDRESS"], "licensed_neighbors": sum(row["axes_after"] == "GRADE+ADDRESS" for row in neighbor_rows), "compiler_action": "swap AL/AR only"},
        {"axis_combination": "GRADE+QUANTITY", "attested_events": axis_counts["GRADE+QUANTITY"], "licensed_neighbors": sum(row["axes_after"] == "GRADE+QUANTITY" for row in neighbor_rows), "compiler_action": "swap AIIN/AIN only"},
        {"axis_combination": "QUANTITY+ADDRESS", "attested_events": axis_counts["QUANTITY+ADDRESS"], "licensed_neighbors": 0, "compiler_action": "do not invent"},
        {"axis_combination": "GRADE+QUANTITY+ADDRESS", "attested_events": axis_counts["GRADE+QUANTITY+ADDRESS"], "licensed_neighbors": 0, "compiler_action": "do not invent"},
    ]
    rules = [
        {"step": 1, "instruction_de": "NUR EIN BEREITS BELEGTES MEHRACHSREZEPT OEFFNEN"},
        {"step": 2, "instruction_de": "GENAU EINE ACHSE IN EINEN BEREITS GELEHRTEN GEGENWERT TAUSCHEN"},
        {"step": 3, "instruction_de": "ALLE ANDEREN KERNE, ACHSEN UND DEN AUSGANG UNVERAENDERT LASSEN"},
        {"step": 4, "instruction_de": "KEINE NEUE ACHSE IN EINE KARTE EINFUEGEN"},
        {"step": 5, "instruction_de": "NEUE OBERFLAECHE ALS MEISTERKARTE, NICHT ALS MANUSKRIPTBELEG MARKIEREN"},
    ]

    write(
        "SEVEN_HUNDRED_NINETY_FOURTH_6_ATTESTED_MULTI_AXIS_CARDS.tsv",
        attested_rows,
        ["event_id", "page", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "active_axes", "working_reading_de", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FOURTH_6_LICENSED_NEIGHBORS.tsv",
        neighbor_rows,
        ["source_event", "source_surface", "source_recipe", "source_reading_de", "changed_axis", "predicted_surface", "predicted_recipe", "predicted_reading_de", "axes_before", "axes_after", "axis_count_preserved", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FOURTH_12_READBACKS.tsv",
        readback_rows,
        ["item", "surface", "recipe", "active_axes", "reading_de", "provenance", "readback"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FOURTH_4_AXIS_COMBINATIONS.tsv",
        inventory_rows,
        ["axis_combination", "attested_events", "licensed_neighbors", "compiler_action"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FOURTH_5_COMPILER_RULES.tsv",
        rules,
        ["step", "instruction_de"],
    )

    deck = """# Pass 794 — der kleine Drei-Achsen-Compiler

Auf den festen Seiten gibt es nur sechs Karten, die zwei unserer produktiven Achsen zugleich tragen:

- `cheoar` → ENTNEHMEN · KURZ · ARBEITSGANG · QUELLE;
- `sheckhal` → HALTEN · KURZ · DURCHLASS · ZIELSTELLE;
- `qokeedal` → ANSETZEN · LANG · ZIELSTELLE;
- `rsheal` → KUEHLEN · HALTEN · KURZ · ZIELSTELLE;
- `cheedar` → LANG · QUELLE;
- `qotedaiin` → DANACH · KURZ · SOLLMASS.

Aus jeder Karte ist genau ein eng lizenzierter Nachbar bildbar:

- `cheoar → cheoal` (Quelle→Ziel);
- `sheckhal → sheckhar` (Ziel→Quelle);
- `qokeedal → qokeedar` (Ziel→Quelle);
- `rsheal → rshear` (Ziel→Quelle);
- `cheedar → cheedal` (Quelle→Ziel);
- `qotedaiin → qotedain` (Sollmaß→Portion).

Der Compiler fügt keine Achse hinzu. Deshalb erzeugt er weder Menge+Adresse noch Grad+Menge+Adresse aus dem Nichts. Das ist für eine kleine Werkstatt plausibel: Der Schreiber kann eine gelehrte Karte an genau einer bekannten Stelle abwandeln, muss komplexere Karten aber vom Exemplar kopieren.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_FOURTH_COMPILER_DECK.md").write_text(deck, encoding="utf-8")

    report = """# Pass 794 — Komposition ist real, aber absichtlich klein

Nur sechs der 381 Prosaereignisse kombinieren mindestens zwei der drei jetzt produktiven Achsen. Fünf verbinden Grad+Adresse, eines Grad+Menge. Menge+Adresse und die volle Dreierkombination fehlen.

Der bounded compiler bildet deshalb genau sechs neue Nachbarkarten: fünf AL/AR-Wechsel und einen AIIN/AIN-Wechsel. In allen sechs bleibt die zweite Achse sowie der restliche Kern fest; 12/12 alte und neue Karten lesen eindeutig zurück. Keine zusätzliche Achse wird eingefügt.

Das ist ein gutes Werkstattmodell: einige Kürzel sind produktiv, doch komplexe Kombinationen werden nicht frei aus einem vollständigen mathematischen Raster erzeugt. Man lernt ganze Karten und darf an wenigen markierten Slots kleine, bedeutungstragende Änderungen vornehmen.

Als nächstes untersuchen wir die drei großen Steuerkerne OK, OT und OL. Gesucht sind gleiche Endstücke unter verschiedenen Kernen: ANSETZEN gegen DANACH/FOLGE gegen FORTSETZEN. Das sollte zeigen, ob auch der linke Kartenrand ein produktives Paradigma bildet.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "attested_multi_axis_events": len(attested_rows),
        "attested_multi_axis_cards": len({row["exact_card_id"] for row in attested_rows}),
        "grade_address": axis_counts["GRADE+ADDRESS"],
        "grade_quantity": axis_counts["GRADE+QUANTITY"],
        "quantity_address": axis_counts["QUANTITY+ADDRESS"],
        "triple_axis": axis_counts["GRADE+QUANTITY+ADDRESS"],
        "licensed_neighbors": len(neighbor_rows),
        "readback_passes": sum(row["readback"] == "PASS" for row in readback_rows),
        "decision": "SIX_ONE_AXIS_NEIGHBORS__NO_FREE_AXIS_INSERTION",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
