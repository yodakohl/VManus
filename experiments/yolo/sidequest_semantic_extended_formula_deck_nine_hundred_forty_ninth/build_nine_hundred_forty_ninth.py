#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_three_layer_codebook_nine_hundred_forty_sixth/PASS946_2511_THREE_LAYER_EVENT_EDITION.tsv"
OLD_FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_renderer_consolidated_card_deck_nine_hundred_forty_second/PASS942_47_LEARNED_CARD_FAMILIES.tsv"
OLD_VARIANTS = ROOT / "experiments/yolo/sidequest_semantic_renderer_consolidated_card_deck_nine_hundred_forty_second/PASS942_97_SURFACE_VARIANTS.tsv"

NEW_VALUES = {
    "OK+OL": ("ANSETZEN UND WEITERFÜHREN", "Bildgang aktivieren und fortsetzen"),
    "OL+Y": ("MIT DIESEM POSTEN WEITER", "diesem Bildplatz weiter folgen"),
    "SOLK+EE+DY": ("LÄNGER AUFFANGEN; ENDE", "Sammelplatz länger halten und schließen"),
    "OL+CHD+DY": ("WEITER UMSETZEN; ENDE", "Folgeplatz wechseln und Eintrag schließen"),
    "OK+CHD+DY": ("ANSETZEN, UMSETZEN; ENDE", "Bildgang beginnen, Platz wechseln, schließen"),
    "OT+AL": ("ZUR NÄCHSTEN STELLE", "nächster Zielplatz"),
    "D_ADDR+OL": ("DEN BEZEICHNETEN TEIL WEITERFÜHREN", "Unterplatz der Folge"),
    "SH+E+OL": ("KURZ HALTEN UND WEITERFÜHREN", "Bezug kurz halten und fortsetzen"),
    "LSH+E+DY": ("KURZ SPÜLEN; ENDE", "lokalen Prüfweg kurz ausführen und schließen"),
    "SH+E+DY": ("KURZ HALTEN; ENDE", "Bezug kurz halten und schließen"),
    "CHK+EE+Y": ("DIESEN POSTEN LÄNGER BEHANDELN", "diesen Eintrag länger behandeln"),
    "D_ADDR+OR": ("BEZEICHNETER TEILANSATZ", "untergeordnete Reihe"),
    "S+OR": ("ZUBEREITUNGSVARIANTE", "Reihenklasse"),
    "K+AR": ("VON DER ENTNAHMESTELLE ZUGEBEN", "Wert am Quellplatz zuordnen"),
    "K+OL": ("WEITER ZUGEBEN", "Wert in der Folgereihe zuordnen"),
    "SOLK+EE+Y": ("DIESEN POSTEN LÄNGER AUFFANGEN", "diesen Sammelplatz länger halten"),
}

REGISTER = {
    "f10r": "HERBAL", "f11r": "HERBAL", "f13r": "HERBAL", "f55v": "HERBAL", "f56r": "HERBAL",
    "f88r": "PHARMA", "f75r": "BIOLOGICAL", "f81v": "BIOLOGICAL", "f82r": "BIOLOGICAL", "f83r": "BIOLOGICAL",
    "f67r2": "ZODIAC", "f68r1": "ZODIAC", "f69v": "ZODIAC", "f70v": "ZODIAC",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read_tsv(EVENTS)
    old_families = read_tsv(OLD_FAMILIES)
    old_variants = read_tsv(OLD_VARIANTS)
    old_recipe_ids = {row["component_recipe"]: row["learned_card_id"] for row in old_families}
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        if row["component_recipe"] in NEW_VALUES:
            by_recipe[row["component_recipe"]].append(row)

    new_families: list[dict[str, object]] = []
    new_variants: list[dict[str, object]] = []
    recipe_ids: dict[str, str] = {}
    ordered = sorted(NEW_VALUES, key=lambda recipe: (-sum(row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" for row in by_recipe[recipe]), recipe))
    for offset, recipe in enumerate(ordered, 48):
        family_id = f"P949-K{offset:02d}"
        recipe_ids[recipe] = family_id
        workshop, image = NEW_VALUES[recipe]
        members = by_recipe[recipe]
        surface_counts = Counter(row["surface"] for row in members)
        surfaces = sorted(surface_counts, key=lambda surface: (-surface_counts[surface], surface))
        productive_events = sum(row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" for row in members)
        new_families.append({
            "learned_card_id": family_id,
            "component_recipe": recipe,
            "workshop_learned_value_de": workshop,
            "image_register_value_de": image,
            "surface_variants": "|".join(surfaces),
            "surface_variant_count": len(surfaces),
            "events": len(members),
            "physical_pages": "|".join(sorted({row["physical_page"] for row in members})),
            "registers": "|".join(sorted({REGISTER[row["physical_page"]] for row in members})),
            "learning_rule_de": f"Als Ganzkarte lernen: {productive_events} bisher einzeln zusammengesetzte Belege auf mehreren Seiten verwenden dieselbe Formel.",
        })
        for index, surface in enumerate(surfaces):
            surface_members = [row for row in members if row["surface"] == surface]
            channels = {row["channel"] for row in surface_members}
            new_variants.append({
                "surface": surface,
                "learned_card_id": family_id,
                "component_recipe": recipe,
                "workshop_learned_value_de": workshop,
                "image_register_value_de": image,
                "events": len(surface_members),
                "physical_pages": "|".join(sorted({row["physical_page"] for row in surface_members})),
                "channel_class": "BICHANNEL" if len(channels) > 1 else next(iter(channels)),
                "surface_role": "PRIMARY_FORM" if index == 0 else "POSITION_OR_HAND_VARIANT",
            })

    families = [*old_families, *new_families]
    variants = [*old_variants, *new_variants]
    write_tsv(OUT / "PASS949_63_LEARNED_CARD_FAMILIES.tsv", families)
    write_tsv(OUT / "PASS949_132_SURFACE_VARIANTS.tsv", variants)

    revised: list[dict[str, object]] = []
    promoted = 0
    for row in events:
        promote = row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" and row["component_recipe"] in NEW_VALUES
        promoted += int(promote)
        recipe = row["component_recipe"]
        value = row["current_value_de"]
        if promote:
            value = NEW_VALUES[recipe][0] if row["channel"] == "WORKSHOP_PROSE" else NEW_VALUES[recipe][1]
        learned_card_id = "NONE"
        if promote:
            learned_card_id = recipe_ids[recipe]
        elif row["codebook_layer"] == "LEARNED_FORMULA_CARD":
            learned_card_id = old_recipe_ids[recipe]
        revised.append({
            **row,
            "codebook_layer": "LEARNED_FORMULA_CARD" if promote else row["codebook_layer"],
            "current_value_de": value,
            "learned_card_id": learned_card_id,
            "pass949_revision": "PROMOTED_RECURRENT_FORMULA" if promote else "UNCHANGED",
        })
    write_tsv(OUT / "PASS949_2511_EXTENDED_THREE_LAYER_EDITION.tsv", revised)

    counts = Counter(row["codebook_layer"] for row in revised)
    manual = [
        "# Die sechzehn neu erkannten Formelkarten",
        "",
        "Diese Folgen waren bisher jedes Mal neu aus Kürzeln zusammengesetzt worden. Ihre Wiederkehr über mehrere Seiten macht sie als gelernte Werkstattkarten einfacher.",
        "",
    ]
    for row in new_families:
        manual.extend([
            f"- **{row['learned_card_id']} `{row['component_recipe']}` — {row['workshop_learned_value_de']}**; Formen `{row['surface_variants']}`; {row['events']} Belege auf {row['physical_pages']}.",
            "",
        ])
    (OUT / "PASS949_EXTENDED_FORMULA_DECK.md").write_text("\n".join(manual), encoding="utf-8")

    report = f"""# Pass 949 — die Werkstatt lernt 63 statt 47 Formelkarten

Sechzehn häufige, seitenübergreifende Komponentenfolgen werden nicht länger bei
jedem Auftreten neu buchstabiert. Sie werden als feste Formelkarten gelernt. Das
verschiebt **{promoted} Ereignisse** von der produktiven Kürzelschicht in die
Formelschicht.

Die neue Bilanz lautet: **{counts['PRODUCTIVE_ABBREVIATION_COMPOSITION']} produktiv
zusammengesetzte**, **{counts['LEARNED_FORMULA_CARD']} gelernte Formel-** und
**{counts['LOCAL_NOMENCLATOR_OR_ADDRESS']} lokale Bild-/Adressereignisse**. Das
System wird dadurch näher an einem realen Werkstattgebrauch: häufige ganze
Anweisungen werden memoriert, seltene Kombinationen bleiben produktiv lesbar.
"""
    (OUT / "PASS949_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS949_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"families": len(families), "surface_variants": len(variants), "promoted_events": promoted, "layer_counts": counts, "outputs": outputs}
    (OUT / "PASS949_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
