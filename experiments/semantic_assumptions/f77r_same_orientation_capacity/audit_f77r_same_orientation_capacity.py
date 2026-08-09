#!/usr/bin/env python3
"""Audit existing human annotations for a second f77r-oriented apparatus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/f77r_same_orientation_capacity")
DESIGN = BASE / "DESIGN.md"
LEADS = BASE / "SOURCE_LEAD_AUDIT.tsv"
EXACT = Path("experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv")
PAGES = Path("experiments/semantic_assumptions/results/existing_human_page_annotations.tsv")
TARGET = ("f77r", "V1")
NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def emitting_count(page_row: dict[str, str] | None) -> int | None:
    if page_row is None:
        return None
    text = " ".join(
        [page_row["illustrations"], page_row["tentative_identifications"]]
    ).lower()
    pattern = re.compile(
        r"\b(" + "|".join(NUMBER_WORDS) + r"|\d+)\s+of\s+the\s+openings\b[^.]*\beject"
    )
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1)
    return NUMBER_WORDS.get(value, int(value) if value.isdigit() else None)


def candidate_row(
    key: tuple[str, str],
    rows: list[dict[str, str]],
    page_row: dict[str, str] | None,
) -> dict[str, object]:
    page, unit = key
    comments = [row["local_comment"] for row in rows]
    between_count = sum(bool(re.search(r"\bbetween\b", text, re.I)) for text in comments)
    branch_numbers = sorted(
        {
            int(number)
            for text in comments
            for number in re.findall(r"\bside branch(?:es)?\s+(\d+)\b", text, re.I)
        }
    )
    boundary_count = (
        branch_numbers[-1]
        if branch_numbers and branch_numbers == list(range(1, branch_numbers[-1] + 1))
        else None
    )
    active_count = emitting_count(page_row)
    every_slot_between = between_count == len(rows)
    slot_boundary_match = boundary_count is not None and len(rows) == boundary_count + 1
    mixed_output = (
        boundary_count is not None
        and active_count is not None
        and 0 < active_count < boundary_count
    )
    passes = every_slot_between and slot_boundary_match and mixed_output
    failed = []
    if not every_slot_between:
        failed.append("NOT_ALL_SLOTS_EXPLICITLY_BETWEEN_BOUNDARIES")
    if not slot_boundary_match:
        failed.append("NO_CONTIGUOUS_BOUNDARY_PLUS_ONE_SLOT_ARRAY")
    if not mixed_output:
        failed.append("NO_HUMAN_REPORTED_MIXED_ACTIVE_INACTIVE_BOUNDARIES")
    return {
        "page": page,
        "unit": unit,
        "unit_description": rows[0]["unit_description"],
        "exact_locus_count": len(rows),
        "loci": [row["locus"] for row in rows],
        "between_comment_count": between_count,
        "contiguous_side_branch_numbers": branch_numbers,
        "internal_boundary_count": boundary_count,
        "reported_emitting_boundary_count": active_count,
        "page_annotation_available_under_exact_source_page_id": page_row is not None,
        "every_slot_explicitly_between_boundaries": every_slot_between,
        "slot_count_equals_boundary_count_plus_one": slot_boundary_match,
        "mixed_active_inactive_boundaries": mixed_output,
        "same_orientation_gate": passes,
        "failed_components": failed,
        "is_exposed_target_control": key == TARGET,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = [ROOT / DESIGN, ROOT / LEADS, ROOT / EXACT, ROOT / PAGES]
    exact_rows = read_tsv(ROOT / EXACT)
    page_rows = read_tsv(ROOT / PAGES)
    leads = read_tsv(ROOT / LEADS)
    by_page = {row["page"]: row for row in page_rows}
    if len(by_page) != len(page_rows):
        raise ValueError("duplicate page annotation")

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in exact_rows:
        groups[(row["page"], row["unit"])].append(row)

    broad = []
    for key, rows in sorted(groups.items()):
        description = rows[0]["unit_description"]
        if len(rows) < 5 or "label" not in description.lower():
            continue
        if not any("WATER_OR_APPARATUS" in row["object_tags"].split(";") for row in rows):
            continue
        if any(row["unit_description"] != description for row in rows):
            raise ValueError(f"unit-description drift at {key}")
        broad.append(candidate_row(key, rows, by_page.get(key[0])))

    target_rows = [row for row in broad if row["is_exposed_target_control"]]
    second_passes = [
        row for row in broad if row["same_orientation_gate"] and not row["is_exposed_target_control"]
    ]
    if len(target_rows) != 1 or not target_rows[0]["same_orientation_gate"]:
        raise ValueError("exposed f77r target control did not reconstruct uniquely")

    result = {
        "status": "SOURCE_ONLY_SAME_ORIENTATION_CAPACITY_AUDIT",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in paths},
        "implementation_sha256": sha256(Path(__file__)),
        "prohibited_inputs_used": {
            "transcription_surfaces": False,
            "parsed_roots_or_grammar": False,
            "ocr": False,
            "automated_or_neural_vision": False,
        },
        "source_lead_rows": len(leads),
        "exact_annotation_rows": len(exact_rows),
        "page_annotation_rows": len(page_rows),
        "broad_candidate_units": len(broad),
        "candidate_units": broad,
        "exposed_target_control_pass_count": len(target_rows),
        "second_same_orientation_pass_count": len(second_passes),
        "second_same_orientation_passes": second_passes,
        "decision": {
            "status": "STOP_ZERO_SECOND_SAME_ORIENTATION_HUMAN_ANNOTATED_APPARATUS",
            "retain": "f77r is the sole exact annotated same-orientation unit in the current source layer and remains a provisional post-hoc structural bridge",
            "next": "acquire a new provenance-clean public human annotation with successive apparatus segments and mixed active/inactive boundaries before opening strings",
            "forbid": "no generic circle pool figure path tube proximity or speculative decipherment may substitute; no quality element object lexeme plaintext language or translation",
        },
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
