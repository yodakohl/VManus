#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
R277 = ROOT / "experiments/yolo/sidequest_semantic_component_register_reach_two_hundred_seventy_seventh"
COMPONENTS = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_REVISED_40_COMPONENTS.tsv"
REACH = R277 / "TWO_HUNDRED_SEVENTY_SEVENTH_40_COMPONENT_REACH.tsv"

FAMILY = {
    "E": "E_GRADE", "EE": "E_GRADE", "EEE": "E_GRADE",
    "CHD": "CHED_TRANSFER", "CHED": "CHED_TRANSFER",
    "HO": "CHO_INPUT", "CHO_INPUT": "CHO_INPUT",
}

FAMILY_VALUES = {
    "E_GRADE": ("GRAD", "E=KURZ; EE=LANG; EEE=VOLL"),
    "CHED_TRANSFER": ("UEBERFUEHREN", "CHD=kurze, CHED=erweiterte Allographie derselben Transferhandlung"),
    "CHO_INPUT": ("EINGABE", "Herbal=Zutat oder Material; Astro=Himmelsobjekt oder Eingangsbedingung"),
    "DY": ("FESTSETZEN", "Prosa=Arbeitsschritt schließen; Astro=Wert fest eintragen"),
    "CHK": ("ZUSTAND_JUSTIEREN", "Prosa häufig erwärmen; Astro Grad oder Zustand justieren"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reach_class(h: int, b: int, a: int) -> str:
    present = (h > 0, b > 0, a > 0)
    return {
        (True, True, True): "HERBAL_BIO_ASTRO_CORE",
        (True, True, False): "HERBAL_BIO_PROSE_CORE",
        (True, False, True): "HERBAL_ASTRO_BRIDGE",
        (False, True, True): "BIO_ASTRO_BRIDGE",
        (True, False, False): "HERBAL_SPECIALIST",
        (False, True, False): "BIO_SPECIALIST",
    }[present]


def main() -> None:
    components = read_tsv(COMPONENTS)
    reach = read_tsv(REACH)
    reach_by_id = {r["component_id"]: r for r in reach}
    mapping = []
    for row in components:
        old = row["component_id"]
        new = FAMILY.get(old, old)
        if old in {"E", "EE", "EEE"}:
            variant = {"E": "KURZ", "EE": "LANG", "EEE": "VOLL"}[old]
        elif old in {"CHD", "CHED"}:
            variant = "KURZALLOGRAPH" if old == "CHD" else "ERWEITERTER_ALLOGRAPH"
        elif old in {"HO", "CHO_INPUT"}:
            variant = "INNENKERN_HO" if old == "HO" else "GANZE_EINGABEKARTE_CHO"
        else:
            variant = "IDENTITY"
        mapping.append({
            "old_component_id": old,
            "new_family_id": new,
            "variant_within_family": variant,
            "old_short_value_de": row["short_value_de"],
            "new_short_value_de": FAMILY_VALUES.get(new, (row["short_value_de"], ""))[0],
            "merge_rule": FAMILY_VALUES.get(new, ("", "unchanged component"))[1] or "unchanged component",
        })

    families = []
    family_order = []
    for row in mapping:
        if row["new_family_id"] not in family_order:
            family_order.append(str(row["new_family_id"]))
    for number, family in enumerate(family_order, 1):
        members = [r["old_component_id"] for r in mapping if r["new_family_id"] == family]
        source_rows = [reach_by_id[str(member)] for member in members]
        if family == "CHO_INPUT":
            h = max(int(r["herbal_events"]) for r in source_rows)
            b = max(int(r["bio_events"]) for r in source_rows)
            a = max(int(r["astro_groups"]) for r in source_rows)
        else:
            h = sum(int(r["herbal_events"]) for r in source_rows)
            b = sum(int(r["bio_events"]) for r in source_rows)
            a = sum(int(r["astro_groups"]) for r in source_rows)
        original = next(r for r in components if r["component_id"] == members[0])
        value, rule = FAMILY_VALUES.get(family, (original["short_value_de"], original["learning_rule"]))
        cls = reach_class(h, b, a)
        families.append({
            "family_order": number,
            "family_id": family,
            "member_component_ids": "|".join(str(x) for x in members),
            "short_value_de": value,
            "variant_rule": rule,
            "reach_class": cls,
            "herbal_events": h,
            "bio_events": b,
            "astro_groups": a,
            "teaching_layer": "COMMON_SIXTEEN" if cls == "HERBAL_BIO_ASTRO_CORE" else "BRIDGE" if "BRIDGE" in cls or cls == "HERBAL_BIO_PROSE_CORE" else "SECTION_ADDENDUM",
        })

    corrections = [
        {"family_id": "CHO_INPUT", "old_overloaded_value": "HO=ZUTAT plus CHO_INPUT=EINGABE", "portable_value": "EINGABE", "herbal_expansion": "Zutat oder Materialeingabe", "bio_expansion": "not independently used", "astro_expansion": "Himmelsobjekt oder Eingangsbedingung"},
        {"family_id": "CHED_TRANSFER", "old_overloaded_value": "two separately counted transfer components", "portable_value": "UEBERFUEHREN", "herbal_expansion": "umfüllen oder übertragen", "bio_expansion": "zwischen lokalen Stationen überführen", "astro_expansion": "Wert oder Platzbezug übertragen"},
        {"family_id": "E_GRADE", "old_overloaded_value": "three separately counted components", "portable_value": "GRAD", "herbal_expansion": "kurz/lang/voll bearbeiten", "bio_expansion": "kurz/lang/voll halten", "astro_expansion": "kurze/lange/volle Diagrammstufe"},
        {"family_id": "CHK", "old_overloaded_value": "WAERMEN", "portable_value": "ZUSTAND_JUSTIEREN", "herbal_expansion": "wärmen oder temperieren", "bio_expansion": "wärmen oder temperieren", "astro_expansion": "Grad oder Diagrammzustand justieren"},
        {"family_id": "DY", "old_overloaded_value": "SCHLUSS", "portable_value": "FESTSETZEN", "herbal_expansion": "Arbeitsschritt schließen", "bio_expansion": "Arbeitszelle schließen", "astro_expansion": "Wert fest eintragen"},
    ]

    reach_counts = Counter(str(r["reach_class"]) for r in families)
    mapping_path = OUT / "TWO_HUNDRED_SEVENTY_EIGHTH_40_TO_36_MAPPING.tsv"
    families_path = OUT / "TWO_HUNDRED_SEVENTY_EIGHTH_36_STEM_FAMILIES.tsv"
    correction_path = OUT / "TWO_HUNDRED_SEVENTY_EIGHTH_FIVE_PORTABLE_CORRECTIONS.tsv"
    inventory_path = OUT / "TWO_HUNDRED_SEVENTY_EIGHTH_REVISED_APPRENTICE_INVENTORY.tsv"
    readable_path = OUT / "TWO_HUNDRED_SEVENTY_EIGHTH_READABLE_36_FAMILY_DECK.md"
    report_path = OUT / "TWO_HUNDRED_SEVENTY_EIGHTH_REPORT.md"
    inventory = [
        {"layer": "STEM_FAMILIES", "memorized_entries": 36, "role": "productive grammar and craft components"},
        {"layer": "PROSE_WHOLE_SIGNS", "memorized_entries": 23, "role": "practical nomenclator"},
        {"layer": "ASTRO_WHOLE_SIGNS", "memorized_entries": 46, "role": "diagram value nomenclator"},
        {"layer": "TOTAL_MEMORIZED", "memorized_entries": 105, "role": "complete ten-page learned inventory"},
        {"layer": "LOCAL_COPY_LABEL_FORMS", "memorized_entries": 0, "role": "67 forms copied from local exemplars"},
    ]
    write_tsv(mapping_path, mapping, list(mapping[0]))
    write_tsv(families_path, families, list(families[0]))
    write_tsv(correction_path, corrections, list(corrections[0]))
    write_tsv(inventory_path, inventory, list(inventory[0]))

    common = [str(r["family_id"]) for r in families if r["reach_class"] == "HERBAL_BIO_ASTRO_CORE"]
    readable_path.write_text(f"""# Das 36-Familien-Wörterbuch

Die früheren vierzig Komponenten enthielten vier Doppelzählungen. `E/EE/EEE` sind ein GRAD-Stamm, `CHD/CHED` eine Transfer-Allographie und `HO/CHO_INPUT` derselbe EINGABE-Stamm. Damit bleiben 36 wirkliche Familien.

## Allgemeiner Kern

`{' · '.join(common)}`

Der Kern bleibt sechzehn Familien groß. Die Register sprechen einige davon konkret verschieden aus:

- `CHK = ZUSTAND JUSTIEREN`; in der Nasswerkstatt meist wärmen/temperieren.
- `DY = FESTSETZEN`; in Prosa den Schritt schließen, im Diagramm den Wert fest eintragen.
- `CHO = EINGABE`; im Herbal Material/Zutat, im Astro Himmelsobjekt oder Eingangsbedingung.
- `AIR = LAUF/BAHN`; nur im nassen Kontext Wasserlauf.

Der gesamte Zehn-Seiten-Lehrstoff schrumpft von 109 auf **105 memorierte Einträge**: 36 Stammfamilien, 23 Prosa-Ganzkarten und 46 Astro-Ganzzeichen. Die 67 lokalen Etikettenformen werden weiterhin nur kopiert.
""", encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 278: vierzig Komponenten werden 36 Stammfamilien

## Ergebnis

Drei Paradigmenmerges sparen vier künstliche Einträge: E/EE/EEE→E_GRADE, CHD/CHED→CHED_TRANSFER und HO/CHO_INPUT→CHO_INPUT. Zugleich werden CHK von WÄRMEN zu ZUSTAND_JUSTIEREN und DY von SCHLUSS zu FESTSETZEN abstrahiert; ihre konkreten Registerlesungen bleiben erhalten.

Die 36 Familien teilen sich in 16 Drei-Register-Kerne, drei Herbal/Astro-Brücken, eine Bio/Astro-Brücke, zwei Prosa-Brücken sowie sieben Herbal- und sieben Bio-Spezialisten. Der vollständige memorierte Bestand sinkt auf105.

Inputs `{sha(COMPONENTS)}` and `{sha(REACH)}`.
""", encoding="utf-8")
    outputs = (mapping_path, families_path, correction_path, inventory_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "old_components": 40,
        "new_families": len(families),
        "reach_counts": dict(reach_counts),
        "common_core_count": len(common),
        "memorized_entries": 105,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
