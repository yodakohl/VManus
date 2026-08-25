#!/usr/bin/env python3
"""Build Pass 1001: split old specialist headwords into rooted contextual spellings."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_formula_ligature_reconciliation_nine_hundred_ninety_eighth/PASS998_159_RECONCILED_CODEBOOK.tsv"
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_53_PORTABLE_ROOTS.tsv"
SPECIALISTS = ROOT / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_56_SPECIALIST_HEADWORDS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_2511_EVENT_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    base = read_tsv(BASE)
    roots = read_tsv(ROOTS)
    specialist_units = {row["teaching_unit_id"]: row for row in read_tsv(SPECIALISTS)}
    events = read_tsv(EVENTS)
    meaning = {row["recognition_form"]: row["atomic_meaning_de"] for row in roots}

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for event in events:
        unit_id = event["primary_teaching_unit_ids"]
        if unit_id in specialist_units:
            grouped[(unit_id, event["surface"], event["component_recipe"])].append(event)

    contextual_rows: list[dict[str, object]] = []
    by_old_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    for old_id, surface, recipe in sorted(grouped):
        rows = grouped[(old_id, surface, recipe)]
        tokens = recipe.split("+")
        missing = [token for token in tokens if token not in meaning]
        if missing:
            raise ValueError(f"Unmapped roots in {surface}: {missing}")
        root_sum = " · ".join(meaning[token] for token in tokens)
        old = specialist_units[old_id]
        row: dict[str, object] = {
            "old_teaching_unit_id": old_id,
            "surface": surface,
            "component_recipe": recipe,
            "root_sum_default_de": root_sum,
            "old_specialist_headword_de": old["selected_headword_de"],
            "contextual_expansions_de": "|".join(sorted({event["complete_working_reading_de"] for event in rows})),
            "occurrences": len(rows),
            "pages": "|".join(sorted({event["physical_page"] for event in rows})),
            "event_ids": "|".join(event["event_id"] for event in rows),
            "new_status": "ROOTED_CONTEXTUAL_COMPOSITION__NO_NEW_PORTABLE_WORD",
            "scribe_instruction_de": "Wurzeln lesen; Bildbesitzer und lokales Exemplar liefern erst danach die konkrete Sache oder Fachhandlung.",
        }
        contextual_rows.append(row)
        by_old_id[old_id].append(row)

    for old_id, rows in sorted(by_old_id.items()):
        for index, row in enumerate(rows, 1):
            row["new_teaching_unit_id"] = f"C-{old_id}-{index:02d}"

    contextual_rows = sorted(
        contextual_rows,
        key=lambda row: (str(row["old_teaching_unit_id"]), str(row["new_teaching_unit_id"])),
    )
    contextual_fields = [
        "old_teaching_unit_id",
        "new_teaching_unit_id",
        "surface",
        "component_recipe",
        "root_sum_default_de",
        "old_specialist_headword_de",
        "contextual_expansions_de",
        "occurrences",
        "pages",
        "event_ids",
        "new_status",
        "scribe_instruction_de",
    ]

    contextual_path = OUT / "PASS1001_72_CONTEXTUAL_COMPOSITIONS.tsv"
    write_tsv(contextual_path, contextual_rows, contextual_fields)

    split_rows: list[dict[str, object]] = []
    for old_id, rows in sorted(by_old_id.items()):
        if len(rows) <= 1:
            continue
        split_rows.append({
            "old_teaching_unit_id": old_id,
            "old_specialist_headword_de": specialist_units[old_id]["selected_headword_de"],
            "distinct_surface_recipe_units": len(rows),
            "surfaces": "|".join(str(row["surface"]) for row in rows),
            "component_recipes": "|".join(str(row["component_recipe"]) for row in rows),
            "root_sum_defaults_de": "|".join(str(row["root_sum_default_de"]) for row in rows),
            "decision": "SPLIT_INTO_SURFACE_SPECIFIC_CONTEXTUAL_COMPOSITIONS",
        })
    split_path = OUT / "PASS1001_13_SPLIT_HEADWORD_GROUPS.tsv"
    write_tsv(split_path, split_rows, list(split_rows[0]))

    base_fields = list(base[0])
    revised: list[dict[str, object]] = []
    expanded_old_ids: set[str] = set()
    for row in base:
        old_id = row["teaching_unit_id"]
        if old_id not in specialist_units:
            revised.append(dict(row))
            continue
        if old_id in expanded_old_ids:
            continue
        expanded_old_ids.add(old_id)
        for comp in by_old_id[old_id]:
            revised.append({
                "teaching_unit_id": comp["new_teaching_unit_id"],
                "layer": "C_CONTEXTUAL_COMPOSITION",
                "unit_type": "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD",
                "recognition_forms": comp["surface"],
                "spoken_value_de": comp["root_sum_default_de"],
                "concrete_context_values_de": comp["contextual_expansions_de"],
                "specialist_surface_forms": comp["surface"],
                "observed_specialist_events": comp["occurrences"],
                "pages": comp["pages"],
                "teaching_rule_de": "Komposition zuerst; lokale Bild-/Exemplarbedeutung nur als Kontextausbau.",
            })
    revised_path = OUT / "PASS1001_175_REVISED_CODEBOOK.tsv"
    write_tsv(revised_path, revised, base_fields)

    unit_type_counts: dict[str, int] = defaultdict(int)
    for row in revised:
        unit_type_counts[str(row["unit_type"])] += 1
    summary = {
        "pass": 1001,
        "old_codebook_units": len(base),
        "old_specialist_headword_groups": len(specialist_units),
        "specialist_surface_recipe_units": len(contextual_rows),
        "specialist_events": sum(int(row["occurrences"]) for row in contextual_rows),
        "old_multi_surface_headword_groups_split": len(split_rows),
        "new_codebook_units": len(revised),
        "new_portable_semantic_roots_required": 0,
        "memorized_specialist_semantic_whole_words_remaining": 0,
        "contextual_composition_units": len(contextual_rows),
        "unit_type_counts": dict(sorted(unit_type_counts.items())),
        "input_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (BASE, ROOTS, SPECIALISTS, EVENTS)},
        "output_sha256": {path.name: sha256(path) for path in (contextual_path, split_path, revised_path)},
    }
    (OUT / "PASS1001_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
