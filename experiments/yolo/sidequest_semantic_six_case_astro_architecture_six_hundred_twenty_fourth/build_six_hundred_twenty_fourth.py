#!/usr/bin/env python3
"""Build the corrected six-case architecture and optional Astro appendix."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LAYER_DIR = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
WORD_DIR = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth"
CASE_DIR = ROOT / "experiments/yolo/sidequest_semantic_c5_c6_contrast_six_hundred_twenty_third"
ASTRO_DIR = ROOT / "experiments/yolo/sidequest_semantic_astro_case_interface_six_hundred_fourth"
ASTRO_SOURCE_DIR = ROOT / "experiments/yolo/sidequest_semantic_astro_condition_interface_five_hundred_ninety_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CASE_ARCHITECTURE = {
    "C1": {
        "order": 1,
        "class": "BASE_COMPLETE_PAIR",
        "title": "Grundauszug und mildes gemeinsames Bad",
        "relation": "selbstaendiger Grundfall",
        "book_role": "Bildpflanze bereiten und im zweireihigen Gemeinschaftsbecken mild anwenden",
    },
    "C2": {
        "order": 2,
        "class": "STRENGTH_VARIANT_COMPLETE_PAIR",
        "title": "Nach- oder Spuelauszug und mehrstufige Behandlung",
        "relation": "staerkere und staerker dosierte Variante neben C1; kein blosses Duplikat",
        "book_role": "denselben sichtbaren Pflanzenbesitzer in einen geteilten Vollbehandlungs- und Spuelgang ueberfuehren",
    },
    "C3": {
        "order": 3,
        "class": "FLOWER_IMMERSION_COMPLETE_PAIR",
        "title": "Bluetenauszug und Eintauch-/Waschfolge",
        "relation": "selbstaendiger Blueten- und Gefaessfall",
        "book_role": "Bluetenmaterial bereiten und an lokalen Gefaess-, Wasch- und Eintauchstationen einsetzen",
    },
    "C4": {
        "order": 4,
        "class": "CONTACT_VARIANT_COMPLETE_PAIR",
        "title": "Temperierte Portion und Kontakt-/Auflagefolge",
        "relation": "selbstaendiger Kontaktfall mit Portion und Nachportion",
        "book_role": "temperierte Pflanzenportion am sichtbaren Figurenpaar auftragen, halten, befestigen und verwahren",
    },
    "C5": {
        "order": 5,
        "class": "CONCENTRATE_TRANSFER_COMPLETE_PAIR",
        "title": "Konzentrat und linker Transfer-/Haltegang",
        "relation": "selbstaendiger Konzentratfall",
        "book_role": "konzentrierten Auszug bereiten, uebertragen, halten und lokal sammeln",
    },
    "C6": {
        "order": 6,
        "class": "OPTIONAL_TECHNICAL_APPENDIX",
        "title": "Offenes Kuehl-/Auffang-/Dosierformular",
        "relation": "C5-vertraeglich, aber weder von C5 abgeleitet noch sichtbar daran gebunden",
        "book_role": "separaten oder uebernommenen Werkstattvorrat kuehlen, auffangen, dosieren und offen weiterfuehren",
    },
}


ASTRO_CASE_PLANS = {
    "C1": ("F69_LEFT_WHEEL_NS", "F69_MIDDLE_WHEEL_NS|F67_RIGHT_WHEEL_NS", "optionalen lokalen Bade-/Waschplatz oder groben Bedingungsplatz zeigen"),
    "C2": ("F67_RIGHT_WHEEL_NS", "F69_LEFT_WHEEL_NS", "optionalen groben Abschnitt oder lokalen Arbeitsslot zeigen"),
    "C3": ("F68_LOCAL_STAR_SLOT_NS", "F69_MIDDLE_WHEEL_NS", "optionalen Sternplatz oder lokalen Himmelszustand zeigen"),
    "C4": ("F69_RIGHT_WHEEL_NS", "F67_LEFT_WHEEL_NS", "optionalen Licht-/Gestirnplatz oder feineren Radplatz zeigen"),
    "C5": ("F67_LEFT_WHEEL_NS", "F69_LEFT_WHEEL_NS", "optionalen feineren Lage- oder Arbeitsslot zeigen"),
    "C6": ("F69_LEFT_WHEEL_NS", "F69_MIDDLE_WHEEL_NS", "optional einen Platz fuer die spaetere Verwendung des offenen Vorrats zeigen"),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    case_source = read_tsv(CASE_DIR / "SIX_HUNDRED_TWENTY_THIRD_6_REVISED_CASE_NOUN_LEDGER.tsv")
    events = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_116_LAYERED_STATEMENTS.tsv")
    record_summary = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_11_RECORD_LAYERED_SUMMARY.tsv")
    words = read_tsv(WORD_DIR / "SIX_HUNDRED_SEVENTEENTH_39_SHARP_WORDS.tsv")
    commands = read_tsv(WORD_DIR / "SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv")
    old_namespaces = read_tsv(ASTRO_DIR / "SIX_HUNDRED_FOURTH_THIRTEEN_NAMESPACE_CASE_INTERFACE.tsv")
    old_loci = read_tsv(ASTRO_DIR / "SIX_HUNDRED_FOURTH_142_LOCUS_CASE_INTERFACE.tsv")
    astro_groups = read_tsv(ASTRO_SOURCE_DIR / "FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv")

    case_by_id = {row["case_id"]: row for row in case_source}
    records_by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in record_summary:
        records_by_case[row["case_id"]].append(row)
    statements_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statements:
        statements_by_record[row["record"]].append(row)

    architecture = []
    for case_id in sorted(CASE_ARCHITECTURE, key=lambda x: CASE_ARCHITECTURE[x]["order"]):
        spec = CASE_ARCHITECTURE[case_id]
        source = case_by_id[case_id]
        recs = records_by_case[case_id]
        primary, secondary, question = ASTRO_CASE_PLANS[case_id]
        architecture.append({
            "book_order": spec["order"],
            "case_id": case_id,
            "architecture_class": spec["class"],
            "case_title_de": spec["title"],
            "preparation_record": source["preparation_record"],
            "application_record": source["application_record"],
            "complete_preparation_application_pair": "NO" if case_id == "C6" else "YES",
            "statements": sum(int(row["statements"]) for row in recs),
            "events": sum(int(row["events"]) for row in recs),
            "case_material_de": source["case_material_de"],
            "application_de": source["application_de"],
            "relation_to_other_cases_de": spec["relation"],
            "book_role_de": spec["book_role"],
            "dependency_status": source["c5_link_status"],
            "optional_astro_primary_namespace": primary,
            "optional_astro_secondary_namespaces": secondary,
            "optional_master_prompt_de": question,
            "astro_required_for_case": "NO",
            "prose_to_astro_pointer": "NONE",
        })

    namespace_rows = []
    for row in old_namespaces:
        namespace_rows.append({
            **row,
            "interface_status": "OPTIONAL_EXTERNAL_CONDITION_OR_ADDRESS",
            "required_for_case": "NO",
            "selection_mode": "MASTER_OR_IMAGE_LOCAL__NO_PROSE_POINTER",
            "label_reading": "WHOLE_LOCAL_LABEL__NO_WORD_DECOMPOSITION",
            "orientation": "NONE",
            "cross_page_key": "NONE",
        })

    locus_rows = []
    for row in old_loci:
        locus_rows.append({
            **row,
            "architecture_role": "OPTIONAL_CONDITION_OR_ADDRESS_LOCUS",
            "required_for_case": "NO",
            "selection_mode": "MASTER_OR_IMAGE_LOCAL__NO_PROSE_POINTER",
            "label_reading": "WHOLE_LOCAL_LABEL__NO_WORD_DECOMPOSITION",
        })

    astro_group_rows = []
    for row in astro_groups:
        astro_group_rows.append({
            "group_serial": row["group_serial"],
            "page": row["page"],
            "locus": row["locus"],
            "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"],
            "surface_display_only": row["surface_display_only"],
            "canonical_namespace_id": row["canonical_namespace_id"],
            "local_image_owner": row["local_image_owner"],
            "interface_role": row["interface_role"],
            "architecture_role": "OPTIONAL_CONDITION_OR_ADDRESS_LABEL",
            "label_reading": "WHOLE_LOCAL_LABEL__NO_WORD_DECOMPOSITION",
            "required_for_case": "NO",
            "prose_dictionary_import": "NONE",
            "cross_section_pointer": "NONE",
            "orientation_or_rotation": "NONE",
            "f68_f69_key": "NONE",
        })

    ns_cases = {row["canonical_namespace_id"]: row["applicable_case_ids"] for row in old_namespaces}
    unified = []
    for row in events:
        unified.append({
            "unified_id": f"PROSE:{row['event_id']}",
            "section": "PROSE_CASE",
            "page": row["page"],
            "record_or_locus": row["record"],
            "case_ids": row["case_id"],
            "surface": row["surface"],
            "local_identity": row["card_no"],
            "semantic_component_parse": row["semantic_component_parse"],
            "workshop_role_de": row["standard_command_de"],
            "owner_or_namespace_de": row["image_owner_or_station_de"],
            "case_material_or_label_policy_de": row["case_material_de"],
            "architecture_role": "CASE_PREPARATION_OR_APPLICATION_COMMAND",
            "learning_mode": "39_WORD_COMPOSITION_OR_173_LEARNED_CARD",
            "required_for_case": "YES",
            "orientation": "NOT_APPLICABLE",
            "cross_page_key": "NONE",
        })
    for row in astro_groups:
        unified.append({
            "unified_id": f"ASTRO:{row['opaque_local_id']}",
            "section": "ASTRO_OPTIONAL_LABEL",
            "page": row["page"],
            "record_or_locus": row["locus"],
            "case_ids": ns_cases[row["canonical_namespace_id"]],
            "surface": row["surface_display_only"],
            "local_identity": row["opaque_local_id"],
            "semantic_component_parse": "NOT_APPLICABLE_TO_ASTRO_LOCAL_LABEL",
            "workshop_role_de": "lokale Himmels-, Wahl- oder Adressmarke als Ganzes kopieren",
            "owner_or_namespace_de": row["canonical_namespace_id"],
            "case_material_or_label_policy_de": "WHOLE_LOCAL_LABEL__NO_WORD_DECOMPOSITION",
            "architecture_role": "OPTIONAL_CONDITION_OR_ADDRESS_LABEL",
            "learning_mode": "COPY_COMPLETE_LOCAL_LABEL",
            "required_for_case": "NO",
            "orientation": "NONE",
            "cross_page_key": "NONE",
        })

    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FOURTH_6_CASE_ARCHITECTURE.tsv", architecture, list(architecture[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FOURTH_13_ASTRO_NAMESPACE_INTERFACE.tsv", namespace_rows, list(namespace_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FOURTH_142_ASTRO_LOCUS_INTERFACE.tsv", locus_rows, list(locus_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FOURTH_395_ASTRO_GROUP_INTERFACE.tsv", astro_group_rows, list(astro_group_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_FOURTH_776_TEN_PAGE_LEDGER.tsv", unified, list(unified[0]))

    md = [
        "# Vollstaendiges Zehn-Seiten-Werkstattbuch: fuenf Hauptfaelle, ein Nachtrag, drei Himmelsinstrumente",
        "",
        "## Leseregel",
        "",
        "Die sieben Prosaseiten bilden fuenf vollstaendige Bildpflanze-Zubereitung-Anwendung-Paare und einen optionalen technischen Nachtrag. Die drei Astro-Seiten sind getrennte, optionale Wahl- oder Adressinstrumente. Keine Astro-Marke wird in Prosa-Woerter zerlegt und kein Fall benoetigt eine Astro-Marke.",
        "",
    ]
    for case in architecture:
        case_id = case["case_id"]
        md.extend([
            f"## {case_id}: {case['case_title_de']}",
            "",
            f"**Ordnung:** {case['architecture_class']}. {case['relation_to_other_cases_de']}",
            "",
            f"**Stoff:** {case['case_material_de']}",
            "",
            f"**Gebrauch:** {case['book_role_de']}",
            "",
        ])
        for record in records_by_case[case_id]:
            md.extend([f"### {record['record']} auf {record['page']}", ""])
            for statement in statements_by_record[record["record"]]:
                md.extend([
                    f"- **{statement['statement_id']}** — `{statement['surface_sequence']}`",
                    f"  {statement['layered_reading_de']}",
                ])
            md.append("")
        md.extend([
            f"**Optionale Astrofrage:** {case['optional_master_prompt_de']}. Der Meister zeigt den Bildplatz; die vollstaendige lokale Marke wird kopiert. Sie ist weder ein Prosawort noch ein geschriebener Verweis auf diesen Fall.",
            "",
        ])

    md.extend([
        "# Getrennter Astro-Anhang",
        "",
        "f67r2 bleibt ein Paar lokaler Raeder, f68r1 ein mehrpaneeliges Sternadressbuch und f69v drei getrennte heterogene Raeder. Start, Laufrichtung, Rotation und f68-f69-Schluessel bleiben ungesetzt.",
        "",
    ])
    loci_by_ns: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in locus_rows:
        loci_by_ns[row["canonical_namespace_id"]].append(row)
    for ns in namespace_rows:
        ns_id = ns["canonical_namespace_id"]
        md.extend([
            f"## {ns_id} ({ns['page']})",
            "",
            f"{ns['instrument_reading_de']}. Gebrauch: {ns['possible_condition_use_de']}. Alle Etiketten bleiben lokale Ganzmarken.",
            "",
        ])
        for locus in loci_by_ns[ns_id]:
            md.append(f"- **{locus['locus']} / {locus['local_image_owner']}** — `{locus['complete_surface_display_only']}`")
        md.append("")
    (HERE / "SIX_HUNDRED_TWENTY_FOURTH_COMPLETE_TEN_PAGE_WORKSHOP_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    counts = Counter(row["section"] for row in unified)
    summary = {
        "status": "PASS",
        "cases": len(architecture),
        "complete_pairs": sum(row["complete_preparation_application_pair"] == "YES" for row in architecture),
        "optional_technical_appendices": sum(row["architecture_class"] == "OPTIONAL_TECHNICAL_APPENDIX" for row in architecture),
        "prose_records": len(record_summary),
        "prose_statements": len(statements),
        "prose_events": len(events),
        "prose_card_types": len({row["card_no"] for row in events}),
        "spoken_words": len(words),
        "invariant_commands": len({row["standard_command_de"] for row in commands}),
        "astro_namespaces": len(namespace_rows),
        "astro_loci": len(locus_rows),
        "astro_groups": len(astro_group_rows),
        "unified_groups": len(unified),
        "section_counts": counts,
        "astro_required_cases": 0,
        "orientation_claims": 0,
        "cross_page_keys": 0,
        "decision": "FIVE_COMPLETE_CASE_PAIRS_PLUS_ONE_OPTIONAL_TECHNICAL_APPENDIX_AND_OPTIONAL_ASTRO_ADDRESS_LAYER",
    }
    (HERE / "SIX_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
