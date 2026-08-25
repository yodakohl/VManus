#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_extended_formula_deck_nine_hundred_forty_ninth/PASS949_2511_EXTENDED_THREE_LAYER_EDITION.tsv"
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_extended_formula_deck_nine_hundred_forty_ninth/PASS949_63_LEARNED_CARD_FAMILIES.tsv"
VARIANTS = ROOT / "experiments/yolo/sidequest_semantic_extended_formula_deck_nine_hundred_forty_ninth/PASS949_132_SURFACE_VARIANTS.tsv"

NEW_VALUES = {
    "OK+SH+E+DY": ("ANSETZEN, KURZ HALTEN; ENDE", "Platz aktivieren, kurz halten und schließen"),
    "P+CHD+DY": ("EINSETZEN, UMSETZEN; ENDE", "Eintrag einsetzen, zum Folgeplatz wechseln und schließen"),
    "Y+T+Y": ("DIESEN POSTEN EINSTELLEN", "diesen Bildplatz einstellen"),
    "O+CKH+E+Y": ("DIESEN POSTEN KURZ DURCHFÜHREN", "diesen Bildplatz kurz durch den Gang führen"),
    "OT+CH+OL": ("DANACH TEIL ENTNEHMEN UND WEITER", "nächste Klasse wählen und weiter"),
    "OL+SH+E+DY": ("WEITER KURZ HALTEN; ENDE", "Folgebezug kurz halten und schließen"),
    "T+CHD+Y": ("DIESEN POSTEN UMSTELLEN", "diesen Bildplatz umstellen"),
    "CH+E+CKH+Y": ("DIESEN TEIL KURZ DURCHFÜHREN", "gewählte Klasse kurz durch den Gang führen"),
    "CH+O+D_ADDR+Y": ("DEN BEZEICHNETEN TEIL BEARBEITEN", "den bezeichneten Unterplatz bearbeiten"),
    "D_ADDR+CHD+Y": ("DEN BEZEICHNETEN TEIL UMSETZEN", "den Unterplatz zum Folgeplatz wechseln"),
    "OT+CH+OR": ("DANACH TEIL FÜR DEN ANSATZ ENTNEHMEN", "nächste Klasse des Eintrags wählen"),
    "Y+K+EE+Y": ("DIESEN POSTEN LÄNGER ZUGEBEN", "diesem Bildplatz länger einen Wert zuordnen"),
    "Y+K+OR": ("DIESEN POSTEN DEM ANSATZ ZUGEBEN", "diesen Bildplatz der Eintragsklasse zuordnen"),
    "CH+O+S": ("TEIL BEARBEITEN UND VARIANTE WÄHLEN", "Klasse bearbeiten und Unterklasse wählen"),
    "L+K+E+DY": ("AM WEG KURZ ZUGEBEN; ENDE", "am Bildweg kurz einen Wert zuordnen und schließen"),
    "SH+CKH+E+DY": ("KURZ IM DURCHLASS HALTEN; ENDE", "Bezug kurz im Gang halten und schließen"),
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
    old_families = read_tsv(FAMILIES)
    old_variants = read_tsv(VARIANTS)
    old_ids = {row["component_recipe"]: row["learned_card_id"] for row in old_families}
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        if row["component_recipe"] in NEW_VALUES:
            by_recipe[row["component_recipe"]].append(row)

    new_families: list[dict[str, object]] = []
    new_variants: list[dict[str, object]] = []
    new_ids: dict[str, str] = {}
    ordered = sorted(NEW_VALUES, key=lambda recipe: (-sum(row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" for row in by_recipe[recipe]), recipe))
    for offset, recipe in enumerate(ordered, 64):
        family_id = f"P952-K{offset:02d}"
        new_ids[recipe] = family_id
        workshop, image = NEW_VALUES[recipe]
        members = by_recipe[recipe]
        counts = Counter(row["surface"] for row in members)
        surfaces = sorted(counts, key=lambda surface: (-counts[surface], surface))
        productive = sum(row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" for row in members)
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
            "learning_rule_de": f"Lange wiederkehrende Formel als eine Karte lernen; {productive} freie Belege werden dadurch verkürzt.",
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
    write_tsv(OUT / "PASS952_79_LEARNED_CARD_FAMILIES.tsv", [*old_families, *new_families])
    write_tsv(OUT / "PASS952_155_SURFACE_VARIANTS.tsv", [*old_variants, *new_variants])

    revised: list[dict[str, object]] = []
    promoted = 0
    for row in events:
        recipe = row["component_recipe"]
        promote = row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION" and recipe in NEW_VALUES
        promoted += int(promote)
        layer = "LEARNED_FORMULA_CARD" if promote else row["codebook_layer"]
        value = NEW_VALUES[recipe][0 if row["channel"] == "WORKSHOP_PROSE" else 1] if promote else row["current_value_de"]
        card_id = "NONE"
        if promote:
            card_id = new_ids[recipe]
        elif layer == "LEARNED_FORMULA_CARD":
            card_id = old_ids[recipe]
        revised.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"], "locus": row["locus"], "channel": row["channel"],
            "surface": row["surface"], "component_recipe": recipe, "codebook_layer": layer, "current_value_de": value,
            "learned_card_id": card_id,
            "formula_deck_revision": "PROMOTED_LONG_FORMULA" if promote else row["pass949_revision"],
        })
    write_tsv(OUT / "PASS952_2511_LONG_FORMULA_EDITION.tsv", revised)

    counts = Counter(row["codebook_layer"] for row in revised)
    manual = ["# Sechzehn lange Formelkarten", ""]
    for row in new_families:
        manual.extend([f"- **{row['learned_card_id']} `{row['component_recipe']}` — {row['workshop_learned_value_de']}** ({row['events']} Belege; `{row['surface_variants']}`).", ""])
    (OUT / "PASS952_LONG_FORMULA_DRAWER.md").write_text("\n".join(manual), encoding="utf-8")
    report = f"""# Pass 952 — lange wiederkehrende Anweisungen werden Karten

Sechzehn Folgen mit mindestens drei Bestandteilen werden als fertige
Werkstattformeln gelernt. {promoted} bislang produktiv gelesene Ereignisse werden
dadurch kürzer. Die Bilanz ist nun {dict(counts)}; das Deck umfasst 79 Karten.

Kurze transparente Zweierfolgen bleiben bewusst produktiv. Der Kartensatz wächst
also dort, wo die Gedächtnisentlastung am größten ist, nicht bloß dort, wo eine
Form häufig ist.
"""
    (OUT / "PASS952_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS952_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"families": 79, "variants": 155, "promoted_events": promoted, "layer_counts": counts, "outputs": outputs}
    (OUT / "PASS952_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
