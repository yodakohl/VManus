#!/usr/bin/env python3
"""Build a current 40-component + 23-whole-card atomic edition of all prose."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD_DIR = ROOT / "experiments/yolo/sidequest_semantic_complete_sixty_three_entry_deck_two_hundred_sixty_fourth"
OLD_GENERATION = OLD_DIR / "TWO_HUNDRED_SIXTY_FOURTH_173_COMPLETE_GENERATION.tsv"
OLD_COMPONENTS = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth/TWO_HUNDRED_SEVENTY_FOURTH_REVISED_40_COMPONENTS.tsv"
CURRENT_DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"
CURRENT_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
BIO_ATOMIC_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
SHARED_ANALYSES = ROOT / "experiments/yolo/sidequest_semantic_shared_components_three_hundred_twenty_sixth/THREE_HUNDRED_TWENTY_SIXTH_17_CARD_ANALYSES.tsv"

COMPONENT_VALUES = {
    "OK": "Einsetzen", "OL": "Fortsetzung", "OT": "Folge", "AR": "Quelle", "AL": "Stelle",
    "L": "Abzug", "P": "Zuführung", "AIN": "Portion", "AN": "Zweitportion", "AIIN": "Sollmaß",
    "IIN": "Stufe", "E": "Kurzgrad", "EE": "Langgrad", "EEE": "Vollgrad", "Y": "Diesposten",
    "DY": "Schluss", "OR": "Ansatz", "HO": "Zutat", "CHEO": "Auszug", "AIR": "Wasserlauf",
    "CHED": "Überführen", "CHD": "Umsetzen", "CTH": "Bereit", "SHED": "Absetzen", "CHK": "Wärme",
    "CKH": "Durchlass", "CKHE": "Seihen", "SOLK": "Auffangen", "LSH": "Waschen", "TY": "Teil",
    "CHO_INPUT": "Eingabe", "O_WITHDRAW": "Rücknahme", "OS_RECEIVER": "Aufnahme", "CH_POUR": "Zuguss",
    "TCH_PREPARATION": "Zubereitung", "OYK_VESSEL": "Gefäß", "K_BINDER": "Binder", "YTY_PART": "Folgeteil",
    "SHFY_DURATION": "Standzeit", "D_PREVIOUS": "Vorposten",
}

NONBIO_ATOMIC = {
    "chokcheo": "Auszugzugabe",
    "qokokchy": "Wiedereinsatz",
    "oykchor": "Glasiergefäß",
    "tchody": "Kühlschluss",
    "okchol": "Fortsetzungseinsatz",
    "ykain": "Postenportion",
    "kaiiin": "Weichstufe",
    "otol": "Folgefortsetzung",
    "shoyty": "Blütenrückhalt",
    "cheoar": "Auszugnahme",
    "cheeckhody": "Auftragsschluss",
    "ody": "Kühlschluss",
    "chokchy|okchy|qokchy": "Einsetzen",
    "keol": "Einzelgabe",
    "qotchy": "Blütenrückhalt",
    "kchey": "Grobzerreiben",
    "ykan": "Diesportion",
    "cthaiin": "Krautzerstoßen",
    "ykaiin": "Postensollmaß",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def surface_key(value: str) -> tuple[str, ...]:
    return tuple(sorted(value.split("|")))


def is_one_word(value: str) -> bool:
    return not any(mark in value for mark in [" ", "/", ";"])


def main() -> None:
    current_cards = read(CURRENT_DICTIONARY)
    current_events = read(CURRENT_EVENTS)
    current_by_surface = {surface_key(x["surface_family"]): x for x in current_cards}
    event_by_id = {x["event_id"]: x for x in current_events}

    bio_atomic: dict[str, set[str]] = defaultdict(set)
    for row in read(BIO_ATOMIC_EVENTS):
        bio_atomic[event_by_id[row["event_id"]]["joint_tuple_id"]].add(row["atomic_gloss_de"])
    if any(len(values) != 1 for values in bio_atomic.values()):
        raise ValueError("Bio atomic values not invariant")

    shared_atomic = {x["joint_tuple_id"]: x["atomic_card_value_de"] for x in read(SHARED_ANALYSES)}
    old_generation = read(OLD_GENERATION)
    dictionary = []
    old_by_joint = {}
    for old in old_generation:
        current = current_by_surface[surface_key(old["registered_surfaces"])]
        joint = current["joint_tuple_id"]
        old_by_joint[joint] = old
        if joint in shared_atomic:
            atom = shared_atomic[joint]
            atom_source = "PASS326_SHARED_COMPONENT_DECK"
        elif joint in bio_atomic:
            atom = next(iter(bio_atomic[joint]))
            atom_source = "PASS314_BIO_ATOMIC_GLOSSARY"
        elif current["surface_family"] in NONBIO_ATOMIC:
            atom = NONBIO_ATOMIC[current["surface_family"]]
            atom_source = "PASS327_HERBAL_ATOMIC_COLLAPSE"
        elif is_one_word(current["concrete_word_reading_de"]):
            atom = current["concrete_word_reading_de"].capitalize()
            atom_source = "CURRENT_ONE_WORD_READING"
        else:
            raise ValueError(f"missing atomic collapse: {current['surface_family']} {current['concrete_word_reading_de']}")
        dictionary.append(
            {
                "joint_tuple_id": joint,
                "surface_family": current["surface_family"],
                "occurrences": current["occurrences"],
                "records": current["records"],
                "pages": current["pages"],
                "deck_class": "PRODUCTIVE_COMPOSITION" if old["new_generation_class"] == "GENERATED_FROM_FORTY_COMPONENTS" else "MEMORIZED_WHOLE_CARD",
                "component_formula": old["component_parse"] if old["new_generation_class"] == "GENERATED_FROM_FORTY_COMPONENTS" else "WHOLE_CARD",
                "atomic_value_de": atom,
                "atomic_value_source": atom_source,
                "current_long_reading_de": current["concrete_word_reading_de"],
                "one_word_value": "YES" if is_one_word(atom) else "NO",
            }
        )

    component_rows = []
    for row in read(OLD_COMPONENTS):
        component_rows.append(
            {
                "deck_order": row["deck_order"],
                "component_id": row["component_id"],
                "component_tier": row["component_tier"],
                "atomic_value_de": COMPONENT_VALUES[row["component_id"]],
                "teaching_rule": row["learning_rule"],
                "support_event_count": row["support_event_count"],
                "licensing_scope": row["licensing_scope"],
            }
        )

    atom_by_joint = {x["joint_tuple_id"]: x["atomic_value_de"] for x in dictionary}
    class_by_joint = {x["joint_tuple_id"]: x["deck_class"] for x in dictionary}
    event_rows = []
    statements: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in current_events:
        atom = atom_by_joint[row["joint_tuple_id"]]
        out = {
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"],
            "surface": row["surface_display"],
            "deck_class": class_by_joint[row["joint_tuple_id"]],
            "atomic_value_de": atom,
            "contextual_expansion_de": row["contextual_event_reading_de"],
        }
        event_rows.append(out)
        statements[row["statement_id"]].append(out)

    statement_rows = []
    for statement_id, rows in statements.items():
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "event_ids": "|".join(x["event_id"] for x in rows),
                "surface_sequence": " ".join(x["surface"] for x in rows),
                "atomic_sequence": " → ".join(x["atomic_value_de"] for x in rows),
                "event_count": str(len(rows)),
                "productive_events": str(sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in rows)),
                "whole_card_events": str(sum(x["deck_class"] == "MEMORIZED_WHOLE_CARD" for x in rows)),
            }
        )

    whole_rows = [x for x in dictionary if x["deck_class"] == "MEMORIZED_WHOLE_CARD"]
    write("THREE_HUNDRED_TWENTY_SEVENTH_40_COMPONENTS.tsv", component_rows)
    write("THREE_HUNDRED_TWENTY_SEVENTH_23_WHOLE_CARDS.tsv", whole_rows)
    write("THREE_HUNDRED_TWENTY_SEVENTH_173_ATOMIC_DICTIONARY.tsv", dictionary)
    write("THREE_HUNDRED_TWENTY_SEVENTH_381_ATOMIC_EVENTS.tsv", event_rows)
    write("THREE_HUNDRED_TWENTY_SEVENTH_116_ATOMIC_STATEMENTS.tsv", statement_rows)
    names = [
        "THREE_HUNDRED_TWENTY_SEVENTH_40_COMPONENTS.tsv",
        "THREE_HUNDRED_TWENTY_SEVENTH_23_WHOLE_CARDS.tsv",
        "THREE_HUNDRED_TWENTY_SEVENTH_173_ATOMIC_DICTIONARY.tsv",
        "THREE_HUNDRED_TWENTY_SEVENTH_381_ATOMIC_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_SEVENTH_116_ATOMIC_STATEMENTS.tsv",
    ]
    summary = {
        "status": "PASS",
        "components": len(component_rows),
        "dictionary_cards": len(dictionary),
        "productive_cards": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in dictionary),
        "whole_cards": len(whole_rows),
        "events": len(event_rows),
        "productive_events": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in event_rows),
        "whole_card_events": sum(x["deck_class"] == "MEMORIZED_WHOLE_CARD" for x in event_rows),
        "statements": len(statement_rows),
        "one_word_values": sum(x["one_word_value"] == "YES" for x in dictionary),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
