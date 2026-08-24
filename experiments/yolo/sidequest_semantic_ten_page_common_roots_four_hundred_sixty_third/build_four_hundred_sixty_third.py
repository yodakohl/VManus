#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROSE_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_final_reverse_writer_four_hundred_fifty_ninth/FOUR_HUNDRED_FIFTY_NINTH_381_EVENT_FINAL_REVERSE_WRITER.tsv"
PROSE_CARDS = ROOT / "experiments/yolo/sidequest_semantic_final_reverse_writer_four_hundred_fifty_ninth/FOUR_HUNDRED_FIFTY_NINTH_173_CARD_FINAL_DICTIONARY.tsv"
PROSE_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_current_prose_edition_four_hundred_sixtieth/FOUR_HUNDRED_SIXTIETH_116_STATEMENT_CURRENT_EDITION.tsv"
COMPONENTS = ROOT / "experiments/yolo/sidequest_semantic_combined_prose_manual_four_hundred_fifty_sixth/FOUR_HUNDRED_FIFTY_SIXTH_35_COMPONENT_MANUAL.tsv"
ASTRO_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_astro_component_transfer_four_hundred_sixty_first/FOUR_HUNDRED_SIXTY_FIRST_395_ASTRO_GROUP_TRANSFER.tsv"

ATOMIC_VALUE = {
    "AIIN": "Mass", "AIN": "Portion", "AIR": "Lauf", "AL": "Stelle", "AR": "von dort",
    "CH": "abziehen", "CHD": "umsetzen", "CHK": "waermen", "CKH": "Durchlass", "CKHE": "seihen",
    "CTH": "bereit", "DY": "Schluss", "E": "kurz", "EE": "laenger", "EEE": "vollstaendig",
    "IIN": "Sollstufe", "K": "zufuehren", "L": "fuehren", "LDDY": "befestigen und schliessen",
    "LS": "abfuehren", "LSH": "Waschgang", "O": "Arbeitsgang", "OK": "ansetzen",
    "OL": "fortsetzen", "OR": "Ansatz", "OT": "danach", "P": "hinein", "R": "abkuehlen",
    "SH": "halten", "SHED": "absetzen", "SOLK": "auffangen", "T": "eintragen", "Y": "dies",
    "HO": "Gabe", "CHEO": "Auszug",
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


def revise_value(value: str) -> str:
    return (value.replace("Wasserlauf", "Lauf")
                 .replace("Wasser", "Lauf")
                 .replace("Zutat", "Gabe")
                 .replace("Gefäß", "Fach")
                 .replace("gefuellt", "eingetragen")
                 .replace("fuellen", "eintragen")
                 .replace("Klarauszug", "Ergebnis"))


def main() -> None:
    old_cards = read(PROSE_CARDS)
    cards = []
    revised_card_ids = set()
    for row in old_cards:
        value = revise_value(row["small_value_de"])
        out = dict(row)
        out["wet_context_value_de"] = row["small_value_de"]
        out["small_value_de"] = value
        out["common_root_revision"] = "YES" if value != row["small_value_de"] else "NO"
        if value != row["small_value_de"]:
            revised_card_ids.add(row["joint_tuple_id"])
        cards.append(out)
    write("FOUR_HUNDRED_SIXTY_THIRD_173_CARD_COMMON_ROOT_DICTIONARY.tsv", cards)
    card_by_id = {row["joint_tuple_id"]: row for row in cards}

    prose_events = []
    for row in read(PROSE_EVENTS):
        card = card_by_id[row["joint_tuple_id"]]
        out = dict(row)
        out["wet_context_value_de"] = row["small_value_de"]
        out["small_value_de"] = card["small_value_de"]
        out["common_root_revision"] = "YES" if row["joint_tuple_id"] in revised_card_ids else "NO"
        prose_events.append(out)
    write("FOUR_HUNDRED_SIXTY_THIRD_381_PROSE_EVENT_COMMON_ROOTS.tsv", prose_events)

    old_statement = {row["statement_id"]: row for row in read(PROSE_STATEMENTS)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose_events:
        by_statement[row["statement_id"]].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        statements.append({
            "statement_id": statement_id, "register": rows[0]["register"], "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "owner_zones": "|".join(dict.fromkeys(row["owner_zone"] for row in rows)),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "atomic_common_root_reading_de": "; ".join(row["small_value_de"] for row in rows) + ".",
            "wet_context_expansion_de": old_statement[statement_id]["current_fluent_reading_de"],
            "revised_events": sum(row["common_root_revision"] == "YES" for row in rows),
        })
    write("FOUR_HUNDRED_SIXTY_THIRD_116_PROSE_STATEMENT_DUAL_READINGS.tsv", statements)

    astro_groups = []
    for row in read(ASTRO_GROUPS):
        out = dict(row)
        parse = row["selected_component_parse"]
        if row["transfer_status"] == "EXACT_PROSE_SURFACE":
            atomic = card_by_id[row["exact_prose_joint_tuple_id"]]["small_value_de"]
        elif row["transfer_status"] == "UNIQUE_COMPONENT_SEQUENCE":
            atomic = " + ".join(ATOMIC_VALUE[component] for component in parse.split("+"))
        elif row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE":
            atomic = "mehrdeutige lokale Etikette"
        else:
            atomic = "lokale Etikette"
        out["previous_candidate_value_de"] = row["candidate_workshop_value_de"]
        out["atomic_common_root_value_de"] = atomic
        out["common_root_revision"] = "YES" if atomic != row["candidate_workshop_value_de"] and row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"} else "NO"
        astro_groups.append(out)
    write("FOUR_HUNDRED_SIXTY_THIRD_395_ASTRO_GROUP_COMMON_ROOTS.tsv", astro_groups)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro_groups:
        by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in by_locus.items():
        loci.append({
            "locus_row": len(loci) + 1, "diagram_id": rows[0]["diagram_id"], "page": rows[0]["page"],
            "locus": locus, "local_namespace": rows[0]["local_namespace"],
            "visible_owners": "|".join(dict.fromkeys(row["visible_owner"] for row in rows)),
            "groups": len(rows), "group_serials": "|".join(row["group_serial"] for row in rows),
            "atomic_common_root_reading_de": "; ".join(row["atomic_common_root_value_de"] for row in rows),
            "revised_groups": sum(row["common_root_revision"] == "YES" for row in rows),
            "orientation": "UNSPECIFIED", "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_THIRD_142_ASTRO_LOCUS_COMMON_ROOTS.tsv", loci)

    components = []
    for row in read(COMPONENTS):
        out = dict(row)
        out["previous_value_de"] = row["value_de"]
        if row["component"] in ATOMIC_VALUE:
            out["value_de"] = ATOMIC_VALUE[row["component"]]
        out["common_root_revision"] = "YES" if out["value_de"] != row["value_de"] else "NO"
        components.append(out)
    write("FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv", components)

    revisions = []
    for target, old, new, wet, astro in (
        ("AIR", "Wasser", "Lauf", "Wasserlauf", "Lauf oder Umlauf"),
        ("HO", "Zutat", "Gabe", "Zutat", "Gabe oder Eintrag"),
        ("OS", "Gefäß", "Fach", "Gefäß", "Diagrammfach"),
        ("T", "fuellen", "eintragen", "einfuellen", "eintragen"),
        ("CHEEY_SHEY", "Klarauszug", "Ergebnis", "Klarauszug", "Ergebnis"),
    ):
        revisions.append({
            "target": target, "old_default_de": old, "new_atomic_default_de": new,
            "wet_context_expansion_de": wet, "astro_context_expansion_de": astro,
            "prose_events": sum(row["common_root_revision"] == "YES" and (target in row["component_parse"].split("+") or (target == "OS" and row["surface"] == "os") or (target == "CHEEY_SHEY" and row["surface"] in {"cheey", "shey"})) for row in prose_events),
            "astro_groups": sum(row["common_root_revision"] == "YES" and (target in row["selected_component_parse"].split("+") or (target == "OS" and row["surface"] == "os") or (target == "CHEEY_SHEY" and row["surface"] in {"cheey", "shey"})) for row in astro_groups),
        })
    write("FOUR_HUNDRED_SIXTY_THIRD_FIVE_COMMON_ROOT_REVISIONS.tsv", revisions)

    unified = []
    for row in prose_events:
        unified.append({
            "unified_order": len(unified) + 1, "unified_id": f"P:{row['event_id']}", "domain": "PROSE",
            "unit_id": row["record_unit_id"], "page": row["page"], "locus": row["locus"],
            "visible_surface": row["surface"], "formal_parse": row["component_parse"],
            "atomic_default_de": row["small_value_de"], "context_expansion_de": row["wet_context_value_de"],
            "interpretation_status": "EXACT_PROSE_CARD", "owner_or_namespace": row["owner_zone"],
        })
    for row in astro_groups:
        unified.append({
            "unified_order": len(unified) + 1, "unified_id": f"A:{int(row['group_serial']):03d}", "domain": "ASTRO",
            "unit_id": row["diagram_id"], "page": row["page"], "locus": row["locus"],
            "visible_surface": row["surface"], "formal_parse": row["selected_component_parse"],
            "atomic_default_de": row["atomic_common_root_value_de"], "context_expansion_de": row["atomic_common_root_value_de"],
            "interpretation_status": row["transfer_status"], "owner_or_namespace": row["local_namespace"],
        })
    write("FOUR_HUNDRED_SIXTY_THIRD_776_GROUP_TEN_PAGE_LEDGER.tsv", unified)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in prose_events if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1, "unit_id": unit, "domain": "PROSE", "page": rows[0]["page"],
            "groups": len(rows), "loci": len({row["locus"] for row in rows}), "statements": len({row["statement_id"] for row in rows}),
            "transferred_or_exact": len(rows), "ambiguous": 0, "local_only": 0,
        })
    for diagram in ("A1", "A2", "A3"):
        rows = [row for row in astro_groups if row["diagram_id"] == diagram]
        units.append({
            "unit_order": len(units) + 1, "unit_id": diagram, "domain": "ASTRO", "page": rows[0]["page"],
            "groups": len(rows), "loci": len({row["locus"] for row in rows}), "statements": 0,
            "transferred_or_exact": sum(row["transfer_status"] in {"EXACT_PROSE_SURFACE", "UNIQUE_COMPONENT_SEQUENCE"} for row in rows),
            "ambiguous": sum(row["transfer_status"] == "AMBIGUOUS_COMPONENT_SEQUENCE" for row in rows),
            "local_only": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in rows),
        })
    write("FOUR_HUNDRED_SIXTY_THIRD_14_UNIT_SUMMARY.tsv", units)

    md = ["# Ten-page common-root working edition", "", "Atomic defaults: AIR=LAUF, HO=GABE, OS=FACH, T=EINTRAGEN, CHEEY/SHEY=ERGEBNIS.", ""]
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        md.extend([f"## {unit}", ""])
        for row in statements:
            if row["record_unit_id"] == unit:
                md.append(f"- **{row['statement_id']}** atomar: {row['atomic_common_root_reading_de']} Kontext: {row['wet_context_expansion_de']}")
        md.append("")
    for diagram in ("A1", "A2", "A3"):
        md.extend([f"## {diagram}", ""])
        for row in loci:
            if row["diagram_id"] == diagram:
                md.append(f"- **{row['locus']}**: {row['atomic_common_root_reading_de']}")
        md.append("")
    (HERE / "FOUR_HUNDRED_SIXTY_THIRD_TEN_PAGE_WORKING_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS", "pages": 10, "units": len(units), "prose_cards": len(cards),
        "prose_events": len(prose_events), "prose_statements": len(statements), "astro_groups": len(astro_groups),
        "astro_loci": len(loci), "unified_groups": len(unified), "components": len(components),
        "revised_card_types": len(revised_card_ids),
        "revised_prose_events": sum(row["common_root_revision"] == "YES" for row in prose_events),
        "revised_astro_groups": sum(row["common_root_revision"] == "YES" for row in astro_groups),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
