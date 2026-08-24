#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P468 = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth"
P472 = ROOT / "experiments/yolo/sidequest_semantic_continuous_ten_page_edition_four_hundred_seventy_second"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_20_FIELD_EDITION.tsv"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_97_STATEMENT_EDITION.tsv"
V75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"


HERBAL = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": ("H_BROAD_TOOTHED", "breitblättrige gezähnte Blütenpflanze", "Material dieser Pflanze"),
    "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT": ("H_BLUE_CROWN", "dicht beblätterte Pflanze mit blauer Blütenkrone", "Material dieser Pflanze"),
    "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT": ("H_BROAD_PANICLE", "breitblättrige Rispenpflanze mit auffälligem Wurzelkörper", "Material dieser Pflanze"),
    "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB": ("H_MULTIHEAD", "mehrköpfige stachelige oder zeichenhaft gezeichnete Pflanze", "Material dieser Pflanze"),
}

BIO = {
    "B1_SHARED_TWO_ROW_POOL": ("B1_POOL", "gemeinsame zweireihige Figuren- und Beckenanlage", "Arbeitsflüssigkeit oder Körperposten im gemeinsamen Becken"),
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": ("B2_UPPER", "obere Doppelbecken mit Zylinderstation", "Arbeitsflüssigkeit in den oberen Becken"),
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": ("B2_MIDDLE_LEFT", "mittlere linke Seitenstation mit Zwischenknoten", "Arbeitsflüssigkeit am linken Zwischenknoten"),
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": ("B2_MIDDLE_RIGHT", "mittlere rechte Einzelstation", "Arbeitsposten an der rechten Einzelstation"),
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": ("B2_LOWER_POOL", "unteres grünes Mehrpersonenbecken", "Arbeitsflüssigkeit oder Körperposten im unteren Becken"),
    "B2_LOWER_POOL_EDGE_STATIONS": ("B2_EDGE", "untere Beckenrand- und Endstationen", "Arbeitsflüssigkeit am unteren Beckenrand"),
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": ("B3_UPPER_FAN", "obere offene Fächerstation am Rand", "Arbeitsgut an der oberen Fächerstation"),
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": ("B3_MIDDLE_VESSEL", "mittlere runde Gefäßstation am Rand", "Arbeitsflüssigkeit im runden Gefäß"),
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": ("B3_LOWER_BASKET", "untere Korb- oder Gefäßstation am Rand", "Arbeitsgut im unteren Korbgefäß"),
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": ("B3_GAP", "nicht gezeichneter Übergang vom Rand zum Hauptfeld", "übernommener Arbeitsposten ohne sichtbare Verbindung"),
    "B3_MAIN_ARCH_LINKED_PAIR": ("B3_ARCH_PAIR", "durch einen Bogen verbundenes Hauptpaar", "Arbeitsflüssigkeit im verbundenen Hauptpaar"),
    "B4_MAIN_ARCH_LINKED_PAIR": ("B4_ARCH_PAIR", "durch einen Bogen verbundenes Hauptpaar", "Arbeitsflüssigkeit im verbundenen Hauptpaar"),
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": ("B4_LEFT_FRINGE", "linke offene Randstation", "Arbeitsgut an der linken Randstation"),
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": ("B4_RIGHT_RUN", "rechte S-förmige Mehrarmstation", "Arbeitsflüssigkeit in der rechten Mehrarmstation"),
    "B5_LEFT_OPEN_FRINGE_STATION": ("B5_LEFT", "linke offene Randstation des Nachtrags", "Arbeitsposten an der linken Nachtragsstation"),
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": ("B6_RIGHT", "rechte S-förmige Mehrarmstation des Nachtrags", "Arbeitsflüssigkeit in der rechten Nachtragsstation"),
}

ASTRO_CLASS_DEFAULTS = {
    "A1_RIGHT_SECTOR": ("A1_RIGHT_SECTOR_SLOT_*", "nummerierter Sektorplatz des rechten Rades", "Wert dieses rechten Sektorplatzes"),
    "A1_RIGHT_RING": ("A1_RIGHT_RING_BAND_*", "Ringband des rechten Rades", "Wert dieses Ringbandes"),
    "A1_LEFT_FIELD": ("A1_LEFT_LOCAL_FIELD_*", "nummeriertes Feld des linken Rades", "Wert dieses linken Feldes"),
    "A1_OUTER_STAR": ("A1_LEFT_OUTER_STAR_STATION_*", "äußere Sternstelle des linken Rades", "Wert dieser Sternstelle"),
    "A1_PHASE": ("A1_RIGHT_PHASE_STATION_*", "Phasenstelle des rechten Rades", "Wert dieser Phasenstelle"),
    "A1_LEFT_RING_TEXT": ("A1_LEFT_OUTER_RING_TEXT", "äußere Beschriftung des linken Rades", "Beschriftung des linken Außenrings"),
    "A1_RIGHT_RING_TEXT": ("A1_RIGHT_OUTER_RING_TEXT", "äußere Beschriftung des rechten Rades", "Beschriftung des rechten Außenrings"),
    "A1_LEGEND": ("A1_PAIRED_WHEEL_LEGEND_UNRESOLVED", "Legende zwischen den beiden Rädern", "Legendenposten des Radpaares"),
    "A2_PANEL_HEADER": ("A2_*_PANEL_HEADER", "Kopf eines Sternpanels", "Kopfwert dieses Sternpanels"),
    "A2_HEADER_FRAGMENT": ("A2_MULTIPANEL_HEADER_FRAGMENT_*", "Kopffragment der Sternpanels", "Wert dieses Kopffragments"),
    "A2_CENTRE": ("A2_CENT*_UNRESOLVED", "zentrale Sternfeldlegende", "zentraler Schlüsselwert"),
    "A2_STAR": ("A2_STAR_STATION_*", "nummerierte Sternstelle des Mehrpanelfeldes", "Wert dieser Sternstelle"),
    "A3_RING_TEXT": ("A3_*_WHEEL_RING_TEXT", "Ringbeschriftung eines der drei Räder", "Wert dieser Ringbeschriftung"),
    "A3_RADIAL_SLOT": ("A3_LEFT_RADIAL_SLOT_*", "nummerierter Radialplatz des linken Rades", "Wert dieses Radialplatzes"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(code: str) -> str:
    match = re.search(r"_(\d+)$", code)
    return str(int(match.group(1))) if match else ""


def astro_owner(code: str) -> tuple[str, str, str]:
    n = number(code)
    if code.startswith("A1_RIGHT_SECTOR_SLOT_"):
        return "A1_RIGHT_SECTOR", f"Sektorplatz {n} des rechten Rades", f"Wert am rechten Sektorplatz {n}"
    if code.startswith("A1_RIGHT_RING_BAND_"):
        return "A1_RIGHT_RING", f"Ringband {n} des rechten Rades", f"Ringwert {n} des rechten Rades"
    if code.startswith("A1_LEFT_LOCAL_FIELD_"):
        return "A1_LEFT_FIELD", f"Feld {n} des linken Rades", f"Wert im linken Feld {n}"
    if code.startswith("A1_LEFT_OUTER_STAR_STATION_"):
        return "A1_OUTER_STAR", f"äußere Sternstelle {n} des linken Rades", f"Sternwert {n} des linken Außenrings"
    if code.startswith("A1_RIGHT_PHASE_STATION_"):
        return "A1_PHASE", f"Phasenstelle {n} des rechten Rades", f"Phasenwert {n}"
    fixed_a1 = {
        "A1_LEFT_OUTER_RING_TEXT": ("A1_LEFT_RING_TEXT", "äußere Beschriftung des linken Rades", "Beschriftung des linken Außenrings"),
        "A1_RIGHT_OUTER_RING_TEXT": ("A1_RIGHT_RING_TEXT", "äußere Beschriftung des rechten Rades", "Beschriftung des rechten Außenrings"),
        "A1_PAIRED_WHEEL_LEGEND_UNRESOLVED": ("A1_LEGEND", "Legende zwischen den beiden Rädern", "Legendenposten des Radpaares"),
    }
    if code in fixed_a1:
        return fixed_a1[code]
    if code == "A2_LEFT_PANEL_HEADER":
        return "A2_PANEL_HEADER", "Kopf des linken Sternpanels", "Kopfwert des linken Panels"
    if code == "A2_MIDDLE_PANEL_HEADER":
        return "A2_PANEL_HEADER", "Kopf des mittleren Sternpanels", "Kopfwert des mittleren Panels"
    if code == "A2_RIGHT_PANEL_HEADER":
        return "A2_PANEL_HEADER", "Kopf des rechten Sternpanels", "Kopfwert des rechten Panels"
    if code.startswith("A2_MULTIPANEL_HEADER_FRAGMENT_"):
        return "A2_HEADER_FRAGMENT", f"Kopffragment {n} der Sternpanels", f"Kopfwertfragment {n}"
    if code in {"A2_CENTRE_KEY_UNRESOLVED", "A2_CENTRAL_LEGEND_UNRESOLVED"}:
        return "A2_CENTRE", "zentrale Sternfeldlegende", "zentraler Schlüsselwert"
    if code.startswith("A2_STAR_STATION_"):
        return "A2_STAR", f"Sternstelle {n} des Mehrpanelfeldes", f"Wert der Sternstelle {n}"
    if code == "A3_LEFT_WHEEL_RING_TEXT":
        return "A3_RING_TEXT", "Ringbeschriftung des linken Rades", "Ringwert des linken Rades"
    if code == "A3_MIDDLE_WHEEL_RING_TEXT":
        return "A3_RING_TEXT", "Ringbeschriftung des mittleren Rades", "Ringwert des mittleren Rades"
    if code == "A3_RIGHT_WHEEL_RING_TEXT":
        return "A3_RING_TEXT", "Ringbeschriftung des rechten Rades", "Ringwert des rechten Rades"
    if code.startswith("A3_LEFT_RADIAL_SLOT_"):
        return "A3_RADIAL_SLOT", f"Radialplatz {n} des linken Rades", f"Wert am Radialplatz {n}"
    raise ValueError(code)


def join_owner(codes: str, mapping: dict[str, tuple[str, str, str]]) -> tuple[str, str, str]:
    parts = codes.split("|")
    entries = [mapping[part] for part in parts]
    if len(entries) == 1:
        return entries[0]
    return (
        "+".join(entry[0] for entry in entries),
        "sichtbarer Wechsel von " + entries[0][1] + " zu " + entries[-1][1],
        "Arbeitsposten am Stationswechsel",
    )


def prose_expansion(text: str, concrete: str, active: str, source: str, target: str) -> str:
    return f"Beim Bildbesitzer {concrete}: [DIES={active}; DORT/QUELLE={source}; STELLE={target}] {text}"


def astro_expansion(text: str, concrete: str, active: str) -> str:
    replacements = [
        ("von dieser Position", f"von {concrete}"),
        ("dieser Eintrag", active),
        ("Position", concrete),
        ("Eintrag", active),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return f"Bei {concrete}: {out}"


def main() -> None:
    statements = read(P468 / "FOUR_HUNDRED_SIXTY_EIGHTH_116_PROSE_STATEMENT_COMMON_ACTIONS.tsv")
    h_fields = read(V73)
    b_statements = read(V74)
    astro_loci = read(P472 / "FOUR_HUNDRED_SEVENTY_SECOND_142_ASTRO_LOCUS_CONTEXT_READINGS.tsv")
    v75_loci = read(V75)

    h_owner: dict[str, str] = {}
    for row in h_fields:
        previous = h_owner.setdefault(row["statement_id"], row["whole_plant_owner"])
        if previous != row["whole_plant_owner"]:
            raise ValueError(row["statement_id"])
    b_owner = {row["statement_id"]: row["local_owner_sequence"] for row in b_statements}

    prose_rows = []
    owner_counts: Counter[tuple[str, str, str, str]] = Counter()
    for row in statements:
        if row["register"] == "HERBAL":
            owner_code = h_owner[row["statement_id"]]
            owner_class, concrete, active = HERBAL[owner_code]
            owner_source = "V73_SELECTED_VISIBLE_PLANT_OWNER"
            dort = "diese Pflanze oder ihr laufender Ansatz"
            stelle = "örtlich gelernte, im Bild nicht sichtbare Zielstelle"
        else:
            owner_code = b_owner[row["statement_id"]]
            owner_class, concrete, active = join_owner(owner_code, BIO)
            owner_source = "V74_SELECTED_LOCAL_STATION_OWNER"
            dort = "diese Station oder ihr laufender Bestand"
            stelle = concrete
        owner_counts[(owner_class, owner_code, concrete, active)] += 1
        prose_rows.append({
            **row,
            "owner_class": owner_class,
            "owner_code": owner_code,
            "concrete_owner_de": concrete,
            "dies_resolves_to_de": active,
            "dort_quelle_resolves_to_de": dort,
            "stelle_resolves_to_de": stelle,
            "owner_source": owner_source,
            "owner_expanded_reading_de": prose_expansion(row["wet_context_expansion_de"], concrete, active, dort, stelle),
        })
    write("FOUR_HUNDRED_SEVENTY_THIRD_116_OWNER_EXPANDED_PROSE_STATEMENTS.tsv", prose_rows)

    v75_by_locus = {row["locus"]: row for row in v75_loci}
    astro_rows = []
    for row in astro_loci:
        source = v75_by_locus[row["locus"]]
        owner_code = source["local_image_owner"]
        owner_class, concrete, active = astro_owner(owner_code)
        owner_counts[(owner_class, owner_code if number(owner_code) == "" else owner_class, concrete if number(owner_code) == "" else owner_class, active if number(owner_code) == "" else owner_class)] += 1
        astro_rows.append({
            **row,
            "owner_class": owner_class,
            "owner_code": owner_code,
            "concrete_owner_de": concrete,
            "dies_resolves_to_de": active,
            "dort_quelle_resolves_to_de": concrete,
            "stelle_resolves_to_de": concrete,
            "owner_status": source["owner_status"],
            "owner_expanded_reading_de": astro_expansion(row["celestial_context_reading_de"], concrete, active),
        })
    write("FOUR_HUNDRED_SEVENTY_THIRD_142_OWNER_EXPANDED_ASTRO_LOCI.tsv", astro_rows)

    owner_dictionary = []
    class_rows: dict[str, list[tuple[str, str, str, int]]] = defaultdict(list)
    for (owner_class, code, concrete, active), count in owner_counts.items():
        class_rows[owner_class].append((code, concrete, active, count))
    for owner_class, entries in sorted(class_rows.items()):
        if owner_class.startswith("A"):
            code_default, concrete_default, active_default = ASTRO_CLASS_DEFAULTS[owner_class]
        else:
            code_default = "|".join(sorted({entry[0] for entry in entries}))
            concrete_default = entries[0][1]
            active_default = entries[0][2]
        owner_dictionary.append({
            "owner_class": owner_class,
            "scope": "ASTRO" if owner_class.startswith("A") else "HERBAL" if owner_class.startswith("H") else "BIOLOGICAL",
            "instances": sum(entry[3] for entry in entries),
            "owner_codes_or_pattern": code_default,
            "concrete_owner_default_de": concrete_default,
            "active_referent_default_de": active_default,
            "teaching_rule_de": "Das Bild setzt diesen Besitzer; folgende DIES/DORT/STELLE-Ausdrücke bleiben dort, bis ein sichtbarer Besitzerwechsel eintritt.",
        })
    write("FOUR_HUNDRED_SEVENTY_THIRD_OWNER_CLASS_DICTIONARY.tsv", owner_dictionary)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in prose_rows if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "owner_classes": "|".join(dict.fromkeys(row["owner_class"] for row in rows)),
            "owner_expanded_continuous_reading_de": " ".join(row["owner_expanded_reading_de"] for row in rows),
        })
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro_rows if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": "ASTRO",
            "statements_or_loci": len(rows),
            "groups": sum(int(row["groups"]) for row in rows),
            "owner_classes": "|".join(dict.fromkeys(row["owner_class"] for row in rows)),
            "owner_expanded_continuous_reading_de": " ".join(row["owner_expanded_reading_de"] for row in rows),
        })
    write("FOUR_HUNDRED_SEVENTY_THIRD_14_OWNER_EXPANDED_UNIT_EDITIONS.tsv", units)

    md = ["# Owner-expanded ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["owner_expanded_continuous_reading_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_THIRD_OWNER_EXPANDED_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "owner_classes": len(owner_dictionary),
        "prose_statements": len(prose_rows),
        "prose_events": sum(int(row["events"]) for row in prose_rows),
        "astro_loci": len(astro_rows),
        "astro_groups": sum(int(row["groups"]) for row in astro_rows),
        "units": len(units),
        "owner_expanded_units": sum(bool(row["owner_expanded_continuous_reading_de"]) for row in units),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
