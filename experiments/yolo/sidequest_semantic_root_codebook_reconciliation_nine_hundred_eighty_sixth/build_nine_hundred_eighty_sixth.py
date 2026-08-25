#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P984 = ROOT / "experiments/yolo/sidequest_semantic_53_root_plain_dictionary_nine_hundred_eighty_fourth"
P985 = ROOT / "experiments/yolo/sidequest_semantic_canonical_image_owned_workshop_edition_nine_hundred_eighty_fifth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def token_reconcile(value: str) -> str:
    tokens = value.split(" · ")
    replacements = {
        "DIES": "POSTEN",
        "SCHLIESSEN": "SCHLUSS",
    }
    return " · ".join(replacements.get(token, token) for token in tokens)


def main() -> None:
    roots = read(P984 / "PASS984_53_PORTABLE_ROOT_DICTIONARY.tsv")
    codebook = read(P985 / "PASS985_159_CODEBOOK.tsv")
    events = read(P985 / "PASS985_2511_EVENT_INTERLINEAR.tsv")
    clauses = read(P985 / "PASS985_354_COMPLETE_CLAUSE_EDITION.tsv")

    atomic_by_id = {row["root_id"]: row["atomic_meaning_de"] for row in roots}
    atomic_by_form = {row["recognition_form"]: row["atomic_meaning_de"] for row in roots}
    expansions_by_id = {
        row["root_id"]: " | ".join(
            [
                row["material_workshop_expansion_de"],
                row["station_workshop_expansion_de"],
                row["celestial_relational_expansion_de"],
            ]
        )
        for row in roots
    }

    codebook_changes: list[dict[str, str]] = []
    for row in codebook:
        old_spoken = row["spoken_value_de"]
        old_context = row["concrete_context_values_de"]
        if row["teaching_unit_id"] in atomic_by_id:
            row["spoken_value_de"] = atomic_by_id[row["teaching_unit_id"]]
            row["concrete_context_values_de"] = expansions_by_id[row["teaching_unit_id"]]
        elif row["layer"] == "C_LEARNED_FORMULA_CARD":
            components = row["recognition_forms"].split("+")
            row["spoken_value_de"] = " · ".join(atomic_by_form[part] for part in components)
            row["concrete_context_values_de"] = row["spoken_value_de"]
        if row["spoken_value_de"] != old_spoken or row["concrete_context_values_de"] != old_context:
            codebook_changes.append(
                {
                    "teaching_unit_id": row["teaching_unit_id"],
                    "layer": row["layer"],
                    "recognition_forms": row["recognition_forms"],
                    "old_spoken_value_de": old_spoken,
                    "new_spoken_value_de": row["spoken_value_de"],
                    "old_context_value_de": old_context,
                    "new_context_value_de": row["concrete_context_values_de"],
                    "reason": "PASS984_ROOT_DICTIONARY_IS_AUTHORITATIVE",
                }
            )

    event_changes = 0
    for row in events:
        old = row["complete_working_reading_de"]
        row["complete_working_reading_de"] = token_reconcile(old)
        event_changes += row["complete_working_reading_de"] != old

    clause_changes = 0
    for row in clauses:
        old = row["complete_working_translation_de"]
        new = old.replace("DIES", "POSTEN").replace("SCHLIESSEN", "SCHLUSS")
        row["complete_working_translation_de"] = new
        clause_changes += new != old

    write(HERE / "PASS986_159_RECONCILED_CODEBOOK.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS986_2511_RECONCILED_EVENT_INTERLINEAR.tsv", events, list(events[0]))
    write(HERE / "PASS986_354_RECONCILED_CLAUSES.tsv", clauses, list(clauses[0]))
    write(
        HERE / "PASS986_CODEBOOK_CHANGES.tsv",
        codebook_changes,
        [
            "teaching_unit_id",
            "layer",
            "recognition_forms",
            "old_spoken_value_de",
            "new_spoken_value_de",
            "old_context_value_de",
            "new_context_value_de",
            "reason",
        ],
    )

    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "portable_roots": len(roots),
        "formula_cards": sum(row["layer"] == "C_LEARNED_FORMULA_CARD" for row in codebook),
        "codebook_rows_changed": len(codebook_changes),
        "events_changed": event_changes,
        "clauses_changed": clause_changes,
    }
    (HERE / "PASS986_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
