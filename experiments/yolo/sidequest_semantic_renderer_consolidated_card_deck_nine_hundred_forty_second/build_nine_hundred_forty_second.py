#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
WHOLE = ROOT / "experiments/yolo/sidequest_semantic_hybrid_abbreviation_nomenclator_nine_hundred_forty_first/PASS941_64_LEARNED_WHOLE_CARDS.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_dictionary_nine_hundred_thirty_sixth/PASS936_1078_COMPLETE_SURFACE_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_2511_CURRENT_EVENT_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    whole = read_tsv(WHOLE)
    surfaces = read_tsv(SURFACES)
    events = read_tsv(EVENTS)

    value_by_recipe: dict[str, str] = {}
    for row in whole:
        recipe = row["component_recipe"]
        value = row["learned_whole_card_de"]
        previous = value_by_recipe.setdefault(recipe, value)
        if previous != value:
            raise SystemExit(f"inconsistent learned value for {recipe}: {previous} vs {value}")

    all_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in surfaces:
        all_by_recipe[row["component_recipe"]].append(row)

    family_rows: list[dict[str, object]] = []
    surface_rows: list[dict[str, object]] = []
    family_id_by_recipe: dict[str, str] = {}
    ordered = sorted(value_by_recipe, key=lambda recipe: (-sum(int(row["events"]) for row in all_by_recipe[recipe]), recipe))
    for index, recipe in enumerate(ordered, 1):
        family_id = f"P942-K{index:02d}"
        family_id_by_recipe[recipe] = family_id
        members = sorted(all_by_recipe[recipe], key=lambda row: (-int(row["events"]), row["surface"]))
        family_rows.append({
            "learned_card_id": family_id,
            "component_recipe": recipe,
            "workshop_learned_value_de": value_by_recipe[recipe],
            "image_register_value_de": members[0]["image_composition_de"],
            "surface_variants": "|".join(row["surface"] for row in members),
            "surface_variant_count": len(members),
            "events": sum(int(row["events"]) for row in members),
            "physical_pages": "|".join(sorted({page for row in members for page in row["physical_pages"].split("|")})),
            "registers": "|".join(sorted({register for row in members for register in row["registers"].split("|")})),
            "learning_rule_de": "Eine Bedeutung als Ganzkarte lernen; q/s/ch/d-Varianten werden über dieselbe Komponentenfolge erkannt.",
        })
        for row in members:
            surface_rows.append({
                "surface": row["surface"],
                "learned_card_id": family_id,
                "component_recipe": recipe,
                "workshop_learned_value_de": value_by_recipe[recipe],
                "image_register_value_de": row["image_composition_de"],
                "events": row["events"],
                "physical_pages": row["physical_pages"],
                "channel_class": row["channel_class"],
                "surface_role": "PRIMARY_FORM" if row is members[0] else "POSITION_OR_HAND_VARIANT",
            })
    write_tsv(OUT / "PASS942_47_LEARNED_CARD_FAMILIES.tsv", family_rows, list(family_rows[0]))
    write_tsv(OUT / "PASS942_97_SURFACE_VARIANTS.tsv", surface_rows, list(surface_rows[0]))

    event_rows: list[dict[str, object]] = []
    learned_events = 0
    for row in events:
        recipe = row["component_recipe"]
        learned = recipe in family_id_by_recipe
        learned_events += int(learned)
        event_rows.append({
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "channel": row["channel"],
            "surface": row["surface"],
            "component_recipe": recipe,
            "reading_route": "LEARNED_CARD_FAMILY" if learned else "PRODUCTIVE_COMPOSITION",
            "learned_card_id": family_id_by_recipe.get(recipe, "NONE"),
            "spoken_value_de": (
                value_by_recipe[recipe]
                if learned and row["channel"] == "WORKSHOP_PROSE"
                else row["current_compositional_reading_de"]
            ),
        })
    write_tsv(OUT / "PASS942_2511_RENDERER_CONSOLIDATED_READINGS.tsv", event_rows, list(event_rows[0]))

    manual = [
        "# Pass 942 — 47 Ganzkarten in ihren Schreibvarianten",
        "",
        "Die Oberfläche ist nicht das Wörterbuch. Eine Karte wird an ihrer Komponentenfolge erkannt; die Werkstatt darf sie am Zeilenanfang, nach einem Abschluss oder in einer anderen Hand anders zeichnen.",
        "",
    ]
    for row in family_rows:
        manual.extend([
            f"## {row['learned_card_id']} — {row['workshop_learned_value_de']}",
            "",
            f"Komposition `{row['component_recipe']}`; Schreibformen `{row['surface_variants']}`; {row['events']} Vorkommen. Im Bildregister: {row['image_register_value_de']}.",
            "",
        ])
    (OUT / "PASS942_RENDERER_CONSOLIDATED_CARD_DECK.md").write_text("\n".join(manual), encoding="utf-8")

    report = f"""# Pass 942 — aus 64 Oberflächen werden 47 gelernte Karten

## Ergebnis

Die häufigen Formeln aus Pass 941 kollabieren zu **47 Kartenfamilien** mit
**97 sichtbaren Schreibvarianten**. Sie decken **{learned_events} von 2.511
Ereignissen**. Die häufigsten Gleichungen sind `dy/chey/y/chy/shy/sy = DIESER
POSTEN`, `ol/chol/qol/sol/ls = DAMIT WEITER` und
`qokedy/okedy = KURZ ANSETZEN; ENDE`.

## Schreiberregel

Der Lehrling merkt sich eine Karte pro Komponentenfolge. Der Eintrittsträger
`q`, die Zeilenform `s` und bestimmte `ch/d`-Schreiblagen erzeugen keine neuen
Wörter. Dadurch besteht das Mischsystem jetzt aus 56 produktiven Kürzeln plus 47
wirklich gelernten Formelkarten, nicht aus 120 voneinander unabhängigen Wörtern.

Eine noch ungesehene Oberfläche kann damit vorhergesagt werden: Ergibt ihre
Komponentenfolge eine der 47 Familien, erhält sie sofort deren Ganzkartenwert;
sonst wird sie regelhaft aus den 56 Kürzeln zusammengesetzt.
"""
    (OUT / "PASS942_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "learned_card_families": len(family_rows),
        "surface_variants": len(surface_rows),
        "learned_events": learned_events,
        "events": len(event_rows),
        "outputs": {},
    }
    for path in sorted(OUT.glob("PASS942_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS942_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
