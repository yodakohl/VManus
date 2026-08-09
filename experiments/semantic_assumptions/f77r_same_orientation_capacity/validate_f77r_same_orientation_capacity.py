#!/usr/bin/env python3
"""Independent source-only validation of same-orientation capacity audit."""

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
AUDIT = BASE / "audit_f77r_same_orientation_capacity.py"
DESIGN = BASE / "DESIGN.md"
LEADS = BASE / "SOURCE_LEAD_AUDIT.tsv"
EXACT = Path("experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv")
PAGES = Path("experiments/semantic_assumptions/results/existing_human_page_annotations.tsv")
RESULT = Path("experiments/semantic_assumptions/results/f77r_same_orientation_capacity.json")
WORDS = {
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


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def active_outputs(page: dict[str, str] | None) -> int | None:
    if page is None:
        return None
    prose = (page["illustrations"] + " " + page["tentative_identifications"]).casefold()
    match = re.search(
        r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)"
        r"\s+of\s+the\s+openings\b[^.]*\beject",
        prose,
    )
    if match is None:
        return None
    token = match.group(1)
    return int(token) if token.isdecimal() else WORDS[token]


def reconstruct_row(
    page: str,
    unit: str,
    rows: list[dict[str, str]],
    page_data: dict[str, str] | None,
) -> dict[str, object]:
    comments = [row["local_comment"] for row in rows]
    between = sum(re.search(r"\bbetween\b", comment, re.I) is not None for comment in comments)
    numbers = set()
    for comment in comments:
        for match in re.finditer(r"\bside branch(?:es)?\s+(\d+)\b", comment, re.I):
            numbers.add(int(match.group(1)))
    ordered_numbers = sorted(numbers)
    boundary_count = None
    if ordered_numbers and ordered_numbers == list(range(1, max(ordered_numbers) + 1)):
        boundary_count = max(ordered_numbers)
    emitting = active_outputs(page_data)
    all_between = between == len(rows)
    slots_fit = boundary_count is not None and len(rows) == boundary_count + 1
    mixed = boundary_count is not None and emitting is not None and 0 < emitting < boundary_count
    passed = all_between and slots_fit and mixed
    failures = []
    if not all_between:
        failures.append("NOT_ALL_SLOTS_EXPLICITLY_BETWEEN_BOUNDARIES")
    if not slots_fit:
        failures.append("NO_CONTIGUOUS_BOUNDARY_PLUS_ONE_SLOT_ARRAY")
    if not mixed:
        failures.append("NO_HUMAN_REPORTED_MIXED_ACTIVE_INACTIVE_BOUNDARIES")
    return {
        "page": page,
        "unit": unit,
        "unit_description": rows[0]["unit_description"],
        "exact_locus_count": len(rows),
        "loci": [row["locus"] for row in rows],
        "between_comment_count": between,
        "contiguous_side_branch_numbers": ordered_numbers,
        "internal_boundary_count": boundary_count,
        "reported_emitting_boundary_count": emitting,
        "page_annotation_available_under_exact_source_page_id": page_data is not None,
        "every_slot_explicitly_between_boundaries": all_between,
        "slot_count_equals_boundary_count_plus_one": slots_fit,
        "mixed_active_inactive_boundaries": mixed,
        "same_orientation_gate": passed,
        "failed_components": failures,
        "is_exposed_target_control": (page, unit) == ("f77r", "V1"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = json.loads((ROOT / RESULT).read_text(encoding="utf-8"))
    exact = table(ROOT / EXACT)
    pages = table(ROOT / PAGES)
    leads = table(ROOT / LEADS)
    checks = []

    expected_inputs = {
        str(path): sha(ROOT / path) for path in (DESIGN, LEADS, EXACT, PAGES)
    }
    assert result["inputs"] == expected_inputs
    assert result["implementation_sha256"] == sha(ROOT / AUDIT)
    checks.extend(["four exact input hashes", "audit implementation hash"])

    assert set(exact[0]) == {
        "page", "locus", "source_locus", "old_locus", "unit", "normalized_code",
        "unit_description", "local_comment", "object_tags", "context_class",
        "local_relation_tags", "unit_relation_tags", "relation_scope", "certainty",
        "source_path",
    }
    assert "surface" not in exact[0] and "root_sequence" not in exact[0]
    assert result["prohibited_inputs_used"] == {
        "transcription_surfaces": False,
        "parsed_roots_or_grammar": False,
        "ocr": False,
        "automated_or_neural_vision": False,
    }
    checks.extend(["annotation-only exact schema", "no transcription or root fields", "prohibited-input declaration"])

    page_map = {row["page"]: row for row in pages}
    assert len(page_map) == len(pages) == result["page_annotation_rows"]
    assert len(exact) == result["exact_annotation_rows"]
    checks.extend(["unique 228-page atlas", "exact annotation row count"])

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in exact:
        grouped[(row["page"], row["unit"])].append(row)
    broad = []
    for (page, unit), rows in sorted(grouped.items()):
        description = rows[0]["unit_description"]
        if len(rows) < 5 or "label" not in description.casefold():
            continue
        if not any("WATER_OR_APPARATUS" in row["object_tags"].split(";") for row in rows):
            continue
        assert all(row["unit_description"] == description for row in rows)
        broad.append(reconstruct_row(page, unit, rows, page_map.get(page)))
    assert broad == result["candidate_units"]
    checks.extend(["broad-unit reconstruction", "unit-description consistency", "all candidate gate fields"])

    keys = [(row["page"], row["unit"]) for row in broad]
    assert keys == [
        ("f75r", "N1"), ("f75v", "N1"), ("f77r", "V1"),
        ("f77v", "N1"), ("f78r", "X1"), ("f80r", "N1"),
        ("f82r", "N1"), ("f82v", "X2"), ("f84r", "N1"),
        ("f84v", "N1"), ("f85v2", "X1"),
    ]
    assert result["broad_candidate_units"] == 11
    checks.extend(["eleven broad candidate identities", "broad count"])

    passes = [row for row in broad if row["same_orientation_gate"]]
    assert [(row["page"], row["unit"]) for row in passes] == [("f77r", "V1")]
    target = passes[0]
    assert (target["exact_locus_count"], target["internal_boundary_count"], target["reported_emitting_boundary_count"]) == (6, 5, 4)
    assert result["exposed_target_control_pass_count"] == 1
    assert result["second_same_orientation_pass_count"] == 0
    assert result["second_same_orientation_passes"] == []
    checks.extend(["unique exposed target control", "f77r six-five-four topology", "zero second passes"])

    foldout = next(row for row in broad if row["page"] == "f85v2")
    assert foldout["page_annotation_available_under_exact_source_page_id"] is False
    assert foldout["same_orientation_gate"] is False
    checks.append("compound-foldout missing literal page record retained as failure")

    assert len(leads) == result["source_lead_rows"] == 5
    assert len({row["url"] for row in leads}) == 5
    assert any(row["outcome"].startswith("EXCLUDED_") for row in leads)
    checks.extend(["five bounded public leads", "unique source URLs", "speculative decipherment exclusion"])

    assert result["decision"]["status"] == "STOP_ZERO_SECOND_SAME_ORIENTATION_HUMAN_ANNOTATED_APPARATUS"
    assert "translation" in result["decision"]["forbid"]
    checks.extend(["stop-decision reconstruction", "translation ceiling"])

    validation = {
        "status": "PASS_INDEPENDENT_SOURCE_ONLY_SAME_ORIENTATION_CAPACITY_VALIDATION",
        "imports_audit_code": False,
        "result_sha256": sha(ROOT / RESULT),
        "audit_implementation_sha256": sha(ROOT / AUDIT),
        "check_count": len(checks),
        "checks": checks,
        "broad_candidate_units": 11,
        "second_same_orientation_passes": 0,
    }
    data = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
