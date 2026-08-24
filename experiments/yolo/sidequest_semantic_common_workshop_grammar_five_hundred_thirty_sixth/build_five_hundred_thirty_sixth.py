#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth/FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


PRIMITIVES = {
    "ACTIVATE_CHARGE": ("ANSETZEN", "REFERENCE", "aktuellen Arbeitsposten ansetzen/aktivieren"),
    "CONTINUE_USE": ("FORTSETZEN", "REFERENCE", "mit dem aktuellen Posten fortfahren"),
    "SOURCE_DRAW": ("QUELLE", "ADDRESS", "von der bezeichneten Quelle nehmen"),
    "METER_CHECK": ("MASS", "ADDRESS", "Maß, Menge oder Arbeitsstufe setzen"),
    "TARGET_HANDOFF": ("ZIEL", "ADDRESS", "eine Ziel- oder Arbeitsstelle setzen"),
    "MOVE_PASS": ("FÜHREN", "PROCESS", "Posten führen, umsetzen oder durchlassen"),
    "HOLD_STATE": ("HALTEN", "STATE", "Posten halten, erwärmen, absetzen oder prüfen"),
    "CLOSE": ("SCHLUSS", "CLOSE", "die lokale Arbeitszelle abschließen"),
}


OWNER_NAMES = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": "abgebildete breit gezähnte radialblütige Pflanze",
    "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT": "abgebildete dicht blau blühende Kronenpflanze",
    "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT": "abgebildete breitblättrige rispige Pflanze",
    "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB": "abgebildete mehrköpfige stachelige Pflanze",
    "B1_SHARED_TWO_ROW_POOL": "gemeinsame zweireihige Figuren-/Beckenstation",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "oberes Beckenpaar mit Zylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "mittleres linkes Handgerät mit Inline-Knoten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "mittlere rechte unklare Station",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "unteres grünes Mehrfigurenbecken",
    "B2_LOWER_POOL_EDGE_STATIONS": "kleine Randstationen des unteren Beckens",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "obere offene Fächerstation am Rand",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "mittlere Randfigur im runden Gefäß",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "untere Randfigur im korbartigen Gefäß",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "unverbundener Zwischenbereich",
    "B3_MAIN_ARCH_LINKED_PAIR": "sichtbares Figurenpaar mit gemeinsamem Bogen in B3",
    "B4_MAIN_ARCH_LINKED_PAIR": "sichtbares Figurenpaar mit gemeinsamem Bogen in B4",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "linke Hauptstation mit offenem Fransenlauf",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "rechte Hauptstation mit S-Lauf und Mehrarmknoten",
    "B5_LEFT_OPEN_FRINGE_STATION": "linke Fransenstation im B5-Nachtrag",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "rechter S-Lauf im B6-Nachtrag",
}


def section(record: str) -> str:
    return "HERBAL" if record.startswith("H") else "BIOLOGICAL"


def main() -> None:
    source = read_tsv(SOURCE)
    herbal_cards = {row["card_no"] for row in source if row["record"].startswith("H")}
    bio_cards = {row["card_no"] for row in source if row["record"].startswith("B")}

    primitive_rows: list[dict[str, str]] = []
    for order, (primitive, (word, lane, meaning)) in enumerate(PRIMITIVES.items(), 1):
        herbal_count = sum(
            primitive in row["procedure_tokens"].split(">")
            for row in source if row["record"].startswith("H")
        )
        bio_count = sum(
            primitive in row["procedure_tokens"].split(">")
            for row in source if row["record"].startswith("B")
        )
        primitive_rows.append(
            {
                "order": str(order),
                "primitive": primitive,
                "short_workshop_word_de": word,
                "syntactic_lane": lane,
                "minimal_contribution_de": meaning,
                "herbal_atoms": str(herbal_count),
                "biological_atoms": str(bio_count),
                "total_atoms": str(herbal_count + bio_count),
                "portable_across_sections": "YES" if herbal_count and bio_count else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SIXTH_EIGHT_PRIMITIVE_WORKSHOP_WORDS.tsv", primitive_rows)

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_card[row["card_no"]].append(row)
    cards: list[dict[str, str]] = []
    for card_no, rows in by_card.items():
        readings = {row["apprentice_spoken_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"reading drift {card_no}: {readings}")
        sections = list(dict.fromkeys(section(row["record"]) for row in rows))
        cards.append(
            {
                "card_no": card_no,
                "component_parse": rows[0]["component_parse"],
                "invariant_card_reading_de": next(iter(readings)),
                "primitive_program": rows[0]["procedure_tokens"],
                "grammar_lanes": ">".join(PRIMITIVES[p][1] for p in rows[0]["procedure_tokens"].split(">")),
                "occurrences": str(len(rows)),
                "sections": "|".join(sections),
                "records": "|".join(dict.fromkeys(row["record"] for row in rows)),
                "shared_herbal_biological": "YES" if card_no in herbal_cards and card_no in bio_cards else "NO",
                "semantic_noun_carried_by_card": "NO__OPERATION_OR_CONTROL_ONLY",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_SEVENTY_THREE_COMMON_CARD_GRAMMAR.tsv", cards)

    events: list[dict[str, str]] = []
    for row in source:
        primitives = row["procedure_tokens"].split(">")
        events.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "silent_owner_id": row["owner_code"],
                "silent_owner_de": OWNER_NAMES[row["owner_code"]],
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "card_reading_de": row["apprentice_spoken_reading_de"],
                "primitive_program": row["procedure_tokens"],
                "workshop_words_de": ">".join(PRIMITIVES[p][0] for p in primitives),
                "grammar_lanes": ">".join(PRIMITIVES[p][1] for p in primitives),
                "owner_noun_source": "IMAGE_OR_LOCAL_EXEMPLAR",
                "material_noun_source": "NOT_FIXED_BY_COMMON_OPERATOR_GRAMMAR",
                "disease_bodypart_species_source": "NOT_ENCODED_IN_COMMON_OPERATOR_GRAMMAR",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv", events)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    statements: list[dict[str, str]] = []
    transition_counts: Counter[tuple[str, str, str]] = Counter()
    for statement_id, members in by_statement.items():
        atom_lanes = [lane for row in members for lane in row["grammar_lanes"].split(">")]
        collapsed = [lane for i, lane in enumerate(atom_lanes) if i == 0 or lane != atom_lanes[i - 1]]
        path = ["START", *atom_lanes, "END"]
        sec = section(members[0]["record"])
        for before, after in zip(path, path[1:]):
            transition_counts[(before, after, sec)] += 1
        owners = list(dict.fromkeys(row["silent_owner_id"] for row in members))
        statements.append(
            {
                "statement_id": statement_id,
                "page": members[0]["page"],
                "record": members[0]["record"],
                "silent_owner_ids": "|".join(owners),
                "silent_owner_de": " | ".join(OWNER_NAMES[o] for o in owners),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_readings_de": "; ".join(row["card_reading_de"] for row in members),
                "primitive_sequence": ">".join(p for row in members for p in row["primitive_program"].split(">")),
                "lane_sequence": ">".join(atom_lanes),
                "collapsed_lane_skeleton": ">".join(collapsed),
                "grammar_parse": "SILENT_OWNER :: " + ">".join(atom_lanes),
                "terminal": "YES" if atom_lanes[-1] == "CLOSE" else "NO",
                "silent_noun_expansion_de": (
                    "diese abgebildete Pflanze oder ihr aktueller Teil"
                    if sec == "HERBAL"
                    else "diese sichtbare Figuren-, Becken- oder Arbeitsstation"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_SIXTEEN_STATEMENT_GRAMMAR.tsv", statements)

    transitions: list[dict[str, str]] = []
    pairs = list(dict.fromkeys((before, after) for before, after, _ in transition_counts))
    for before, after in pairs:
        h = transition_counts[(before, after, "HERBAL")]
        b = transition_counts[(before, after, "BIOLOGICAL")]
        transitions.append(
            {
                "from_state": before,
                "to_state": after,
                "herbal_uses": str(h),
                "biological_uses": str(b),
                "total_uses": str(h + b),
                "shared_across_sections": "YES" if h and b else "NO",
                "teaching_rule": f"Nach {before} darf {after} folgen",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SIXTH_ATTESTED_LANE_TRANSITIONS.tsv", transitions)

    owners: list[dict[str, str]] = []
    for number, owner_id in enumerate(dict.fromkeys(row["silent_owner_id"] for row in events), 1):
        members = [row for row in events if row["silent_owner_id"] == owner_id]
        sec = section(members[0]["record"])
        owners.append(
            {
                "owner_no": str(number),
                "section": sec,
                "pages": "|".join(dict.fromkeys(row["page"] for row in members)),
                "records": "|".join(dict.fromkeys(row["record"] for row in members)),
                "silent_owner_id": owner_id,
                "silent_owner_de": OWNER_NAMES[owner_id],
                "events": str(len(members)),
                "supplied_noun_class": "PICTURED_PLANT_OR_PART" if sec == "HERBAL" else "VISIBLE_STATION_OR_FIGURE_GROUP",
                "operator_cards_supply_this_noun": "NO",
                "still_unsupplied_specifics": (
                    "species|exact_part|liquid|ailment|patient"
                    if sec == "HERBAL"
                    else "person_identity|body_part|liquid|temperature|flow_direction|ailment"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SIXTH_TWENTY_IMAGE_SUPPLIED_OWNER_NOUNS.tsv", owners)

    summary = {
        "status": "PASS",
        "events": len(events),
        "cards": len(cards),
        "statements": len(statements),
        "owners": len(owners),
        "primitive_atoms": sum(int(row["total_atoms"]) for row in primitive_rows),
        "primitive_counts": {row["primitive"]: int(row["total_atoms"]) for row in primitive_rows},
        "primitive_words": len(primitive_rows),
        "lanes": 5,
        "transitions": len(transitions),
        "transition_uses": sum(int(row["total_uses"]) for row in transitions),
        "shared_cards": sum(row["shared_herbal_biological"] == "YES" for row in cards),
        "image_supplied_owner_nouns": len(owners),
        "specific_species_bodypart_disease_words_licensed": 0,
    }
    (HERE / "FIVE_HUNDRED_THIRTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
