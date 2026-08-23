#!/usr/bin/env python3
"""Validate the compact apprentice codebook and its complete copybook."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_nomenclator_family_completion"
DICT_IN = SOURCE / "COMPACT_173_CARD_DICTIONARY.tsv"
EVENTS_IN = SOURCE / "COMPACT_381_EVENT_INTERLINEAR.tsv"
PHRASES_IN = SOURCE / "COMPACT_116_PHRASES.tsv"

CARDS = HERE / "WHOLE_CARD_22_CODEBOOK.tsv"
HEADS = HERE / "WHOLE_HEADWORD_16.tsv"
COPYBOOK = HERE / "COPYBOOK_116_STATEMENTS.tsv"
EXERCISES = HERE / "APPRENTICE_16_EXERCISES.tsv"
MANUAL = HERE / "APPRENTICE_ONE_PAGE_MANUAL.md"
SUMMARY = HERE / "BUILD_SUMMARY.json"
VALIDATION = HERE / "VALIDATION.json"
BUILDER = HERE / "build_apprentice_codebook.py"

OUTPUTS = [CARDS, HEADS, COPYBOOK, EXERCISES, MANUAL, SUMMARY]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENTS_IN)
    phrases = read_tsv(PHRASES_IN)
    cards = read_tsv(CARDS)
    heads = read_tsv(HEADS)
    copybook = read_tsv(COPYBOOK)
    exercises = read_tsv(EXERCISES)

    check("source_inventory", (len(dictionary), len(events), len(phrases)) == (173, 381, 116),
          f"dictionary={len(dictionary)}, events={len(events)}, statements={len(phrases)}")
    check("page_scope", {row["page"] for row in events} <= ALLOWED_PAGES,
          "only the seven fixed prose pages occur")

    source_whole = [row for row in dictionary if row["compact_architecture"] == "MEMORIZED_WHOLE_CARD"]
    source_whole_ids = {row["joint_tuple_id"] for row in source_whole}
    source_whole_surfaces = {row["surface_family"] for row in source_whole}
    whole_events = [row for row in events if row["joint_tuple_id"] in source_whole_ids]
    check("source_whole_inventory", len(source_whole) == 22 and len(whole_events) == 28,
          f"types={len(source_whole)}, occurrences={len(whole_events)}")

    check("codebook_inventory", len(cards) == 22 and len({row["joint_tuple_id"] for row in cards}) == 22,
          f"rows={len(cards)}, unique_ids={len({row['joint_tuple_id'] for row in cards})}")
    check("codebook_exact_binding", {row["joint_tuple_id"] for row in cards} == source_whole_ids
          and {row["surface_family"] for row in cards} == source_whole_surfaces,
          "the 22 codebook cards equal the complete source whole-card set")

    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_card[row["joint_tuple_id"]].append(row)
        events_by_statement[row["statement_id"]].append(row)
    occurrence_ok = all(
        int(row["occurrences"]) == len(events_by_card[row["joint_tuple_id"]])
        and row["event_ids"].split("|") == [event["event_id"] for event in events_by_card[row["joint_tuple_id"]]]
        for row in cards
    )
    check("codebook_occurrences", occurrence_ok and sum(int(row["occurrences"]) for row in cards) == 28,
          f"occurrence_sum={sum(int(row['occurrences']) for row in cards)}")

    head_ids = {row["headword_id"] for row in heads}
    assigned_surfaces = [surface for row in heads for surface in row["surface_families"].split(";")]
    check("headword_inventory", len(heads) == 16 and len(head_ids) == 16,
          f"rows={len(heads)}, unique_heads={len(head_ids)}")
    check("headword_partition", len(assigned_surfaces) == 22 and len(set(assigned_surfaces)) == 22
          and set(assigned_surfaces) == source_whole_surfaces,
          "16 headwords partition all 22 exact whole cards once")
    head_count_ok = all(
        int(row["exact_card_types"]) == len(row["surface_families"].split(";"))
        and int(row["occurrences"]) == sum(
            int(card["occurrences"]) for card in cards if card["headword_id"] == row["headword_id"]
        )
        for row in heads
    )
    check("headword_counts", head_count_ok and sum(int(row["occurrences"]) for row in heads) == 28,
          f"headword_occurrence_sum={sum(int(row['occurrences']) for row in heads)}")

    phrase_map = {row["statement_id"]: row for row in phrases}
    copy_map = {row["statement_id"]: row for row in copybook}
    check("copybook_inventory", len(copybook) == 116 and set(copy_map) == set(phrase_map),
          f"rows={len(copybook)}, unique_statements={len(copy_map)}")

    architecture_lookup = {
        "PRODUCTIVE_COMPOSITION": "P",
        "PARTIAL_COMPOSITION": "p",
        "MEMORIZED_WHOLE_CARD": "W",
    }
    statement_binding_ok = True
    architecture_counts: Counter[str] = Counter()
    for statement_id, copy in copy_map.items():
        statement_events = events_by_statement[statement_id]
        expected_surfaces = " ".join(row["surface_display"] for row in statement_events)
        expected_architecture = " ".join(architecture_lookup[row["compact_architecture"]] for row in statement_events)
        statement_binding_ok &= copy["surface_sequence"] == expected_surfaces
        statement_binding_ok &= copy["architecture_sequence"] == expected_architecture
        statement_binding_ok &= len(statement_events) == int(phrase_map[statement_id]["event_count"])
        architecture_counts.update(copy["architecture_sequence"].split())
    check("copybook_source_binding", statement_binding_ok, "all 116 surface and P/p/W sequences match source event order")
    check("copybook_full_event_coverage", sum(architecture_counts.values()) == 381
          and architecture_counts == Counter({"P": 332, "p": 21, "W": 28}),
          f"P={architecture_counts['P']}, p={architecture_counts['p']}, W={architecture_counts['W']}")

    level_counts = Counter(row["lesson_level"] for row in copybook)
    expected_levels = Counter({"L1_PRODUCTIVE": 79, "L2_BOUND_CARRIERS": 15, "L3_CODEBOOK": 22})
    check("lesson_levels", level_counts == expected_levels,
          ", ".join(f"{key}={level_counts[key]}" for key in sorted(level_counts)))

    exercise_heads = {row["headword_id"] for row in exercises}
    exercise_statement_ok = all(
        row["statement_id"] in copy_map
        and row["focus_surface_present"]
        and row["focus_surface_present"] != "NONE"
        and row["headword_id"] in copy_map[row["statement_id"]]["whole_headword_ids"].split("|")
        for row in exercises
    )
    check("exercise_inventory", len(exercises) == 16 and len(exercise_heads) == 16 and exercise_heads == head_ids,
          f"rows={len(exercises)}, covered_headwords={len(exercise_heads)}")
    check("exercise_binding", exercise_statement_ok, "each exercise contains the exact whole-card headword it teaches")

    manual_text = MANUAL.read_text(encoding="utf-8")
    check("manual_contract", all(token in manual_text for token in ["`P`", "`p`", "`W`", "sechzehn", "Ganzkarten"]),
          "manual teaches productive, partial, and whole-card layers")
    check("sealed_pages_absent", not any(page in "\n".join(
        "\t".join(row.values()) for table in [cards, heads, copybook, exercises] for row in table
    ) for page in ["f84", "f84r", "f84v"]), "no sealed selector occurs in generated tables")

    hashes_before = {path.name: digest(path) for path in OUTPUTS}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True)
    hashes_after = {path.name: digest(path) for path in OUTPUTS}
    check("deterministic_rebuild", rebuilt.returncode == 0 and hashes_before == hashes_after,
          "all generated artifacts rebuilt byte-identically")

    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    result = {
        "status": status,
        "checks_passed": sum(bool(row["passed"]) for row in checks),
        "checks_total": len(checks),
        "counts": {
            "cards": 173,
            "events": 381,
            "statements": 116,
            "whole_cards": len(cards),
            "whole_occurrences": sum(int(row["occurrences"]) for row in cards),
            "headwords": len(heads),
            "exercises": len(exercises),
            "productive_events": architecture_counts["P"],
            "partial_events": architecture_counts["p"],
            "whole_events": architecture_counts["W"],
        },
        "checks": checks,
        "artifact_sha256": {path.name: digest(path) for path in OUTPUTS},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
