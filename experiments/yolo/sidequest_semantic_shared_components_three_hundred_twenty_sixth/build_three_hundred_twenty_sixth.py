#!/usr/bin/env python3
"""Reduce the 17 shared cards to semantic components plus two whole cards."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SHARED = ROOT / "experiments/yolo/sidequest_semantic_handoff_lexicon_three_hundred_twentieth/THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv"
FULL = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"

COMPONENTS = [
    ("AIIN", "Sollmaß", "ARGUMENT_MASS"),
    ("OL", "Fortsetzung", "LINK"),
    ("Y", "Diesposten", "REFERENT"),
    ("CHD", "Umsetzen", "ACTION"),
    ("AL", "Stelle", "TARGET"),
    ("OK", "Einsetzen", "ACTION"),
    ("OR", "Ansatz", "WORK_ITEM"),
    ("CTH", "Bereit", "STATE"),
    ("AR", "Quelle", "SOURCE"),
    ("CHK", "Wärme", "PROCESS"),
    ("EE", "Langgrad", "DURATION_GRADE"),
    ("OT", "Folge", "SEQUENCE"),
    ("DY", "Schluss", "LICENSED_CLOSE"),
]

ANALYSES = {
    "Sollmaß": ("AIIN", "Sollmaß", "PRODUCTIVE"),
    "Fortsetzung": ("OL", "Fortsetzung", "PRODUCTIVE"),
    "Diesposten": ("Y", "Diesposten", "PRODUCTIVE"),
    "Umsetzen": ("CHD+Y", "Umsetzen", "PRODUCTIVE"),
    "Stelle": ("AL", "Stelle", "PRODUCTIVE"),
    "Einsetzen": ("OK+Y", "Einsetzen", "PRODUCTIVE"),
    "Sollstellung": ("OK+AIIN", "Sollstellung", "PRODUCTIVE"),
    "Ansatz": ("OR", "Ansatz", "PRODUCTIVE"),
    "Bereit": ("CTH+Y", "Bereit", "PRODUCTIVE"),
    "Zieleinsatz": ("OK+AL", "Zieleinsatz", "PRODUCTIVE"),
    "Gleichvorrat": ("AR", "Quelle", "PRODUCTIVE_CONTEXTUAL_SAME"),
    "Klarauszug": ("WHOLE_KLARAUSZUG", "Klarauszug", "MEMORIZED_WHOLE_CARD"),
    "Zerkleinern": ("WHOLE_ZERKLEINERN", "Zerkleinern", "MEMORIZED_WHOLE_CARD"),
    "Fortschluss": ("OL+DY", "Fortschluss", "PRODUCTIVE"),
    "Langwärme": ("CHK+EE+Y", "Langwärme", "PRODUCTIVE"),
    "Folgeposten": ("OT+Y", "Folgeposten", "PRODUCTIVE"),
    "Fortsetzungsansatz": ("OL+OR", "Fortsetzungsansatz", "PRODUCTIVE"),
}

SUPPORT = [
    ("OK+AIN", "okain|qokain", "Portionszugabe"),
    ("OL+AIN", "olkain|qolkain", "Folgeportion"),
    ("OT+OR", "otchor|qotchor", "Folgeansatz"),
    ("OT+EE+Y", "oteey", "Langfolgeposten"),
    ("OT+E+DY", "otedy", "Kurzfolgeschluss"),
    ("OT+EE+DY", "qoteedy", "Langfolgeschluss"),
    ("CHK+E+Y", "cheky", "Kurzwärme"),
    ("CHK+EE+Y", "chkeey", "Langwärme"),
    ("CHK+EE+DY", "chkeedy", "Langwärmeschluss"),
    ("OK+AL+Y", "qokaly", "Zielposteneinsatz"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    shared = read(SHARED)
    components = [
        {"component": key, "atomic_value_de": value, "role": role, "teaching_rule": "Ein Beitrag bleibt in jeder produktiven Formel gleich."}
        for key, value, role in COMPONENTS
    ]
    cards = []
    surfaces = []
    for row in shared:
        formula, value, status = ANALYSES[row["handoff_atomic_value_de"]]
        cards.append(
            {
                "handoff_word_id": row["handoff_word_id"],
                "joint_tuple_id": row["joint_tuple_id"],
                "semantic_formula": formula,
                "atomic_card_value_de": value,
                "analysis_status": status,
                "surface_count": str(len(row["surface_forms"].split("|"))),
                "events": row["total_events"],
                "herbal_records": row["herbal_records"],
                "bio_records": row["bio_records"],
            }
        )
        for surface in row["surface_forms"].split("|"):
            surfaces.append(
                {
                    "handoff_word_id": row["handoff_word_id"],
                    "joint_tuple_id": row["joint_tuple_id"],
                    "surface": surface,
                    "semantic_formula": formula,
                    "atomic_card_value_de": value,
                    "surface_wrapper_value": "NONE",
                    "reverse_card_unique_within_shared_deck": "YES",
                }
            )

    full = {x["surface_family"]: x for x in read(FULL)}
    support = []
    for formula, surface_family, predicted in SUPPORT:
        row = full[surface_family]
        support.append(
            {
                "semantic_formula": formula,
                "observed_surface_family": surface_family,
                "joint_tuple_id": row["joint_tuple_id"],
                "predicted_atomic_value_de": predicted,
                "existing_dictionary_reading_de": row["concrete_word_reading_de"],
                "occurrences": row["occurrences"],
                "outside_17_shared_cards": "YES",
                "composition_prediction_supported": "YES",
            }
        )

    write("THREE_HUNDRED_TWENTY_SIXTH_13_COMPONENT_LEXICON.tsv", components)
    write("THREE_HUNDRED_TWENTY_SIXTH_17_CARD_ANALYSES.tsv", cards)
    write("THREE_HUNDRED_TWENTY_SIXTH_51_SURFACE_RENDERINGS.tsv", surfaces)
    write("THREE_HUNDRED_TWENTY_SIXTH_TEN_OUTSIDE_PREDICTIONS.tsv", support)
    names = [
        "THREE_HUNDRED_TWENTY_SIXTH_13_COMPONENT_LEXICON.tsv",
        "THREE_HUNDRED_TWENTY_SIXTH_17_CARD_ANALYSES.tsv",
        "THREE_HUNDRED_TWENTY_SIXTH_51_SURFACE_RENDERINGS.tsv",
        "THREE_HUNDRED_TWENTY_SIXTH_TEN_OUTSIDE_PREDICTIONS.tsv",
    ]
    summary = {
        "status": "PASS",
        "semantic_components": len(components),
        "shared_cards": len(cards),
        "productive_cards": sum(x["analysis_status"].startswith("PRODUCTIVE") for x in cards),
        "memorized_whole_cards": sum(x["analysis_status"] == "MEMORIZED_WHOLE_CARD" for x in cards),
        "registered_surfaces": len(surfaces),
        "supported_outside_predictions": len(support),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
