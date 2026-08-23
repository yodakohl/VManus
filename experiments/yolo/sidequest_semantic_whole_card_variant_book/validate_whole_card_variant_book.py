#!/usr/bin/env python3
"""Check that the workshop variant book covers every learned whole-card use."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
APPRENTICE = HERE.parent / "sidequest_semantic_apprentice_codebook"
COMPACT = HERE.parent / "sidequest_semantic_nomenclator_family_completion"

CARDS_IN = APPRENTICE / "WHOLE_CARD_22_CODEBOOK.tsv"
HEADS_IN = APPRENTICE / "WHOLE_HEADWORD_16.tsv"
COPYBOOK_IN = APPRENTICE / "COPYBOOK_116_STATEMENTS.tsv"
EVENTS_IN = COMPACT / "COMPACT_381_EVENT_INTERLINEAR.tsv"

RULES = HERE / "WHOLE_16_VARIANT_RULES.tsv"
OCCURRENCES = HERE / "WHOLE_28_VARIANT_OCCURRENCES.tsv"
ENCODER = HERE / "ENCODER_116_STATEMENTS.tsv"
DRILLS = HERE / "VARIANT_7_DRILLS.tsv"
MANUAL = HERE / "VARIANT_SELECTOR_LEAF.md"
SUMMARY = HERE / "BUILD_SUMMARY.json"
VALIDATION = HERE / "VALIDATION.json"
BUILDER = HERE / "build_whole_card_variant_book.py"
OUTPUTS = [RULES, OCCURRENCES, ENCODER, DRILLS, MANUAL, SUMMARY]
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

    cards = read_tsv(CARDS_IN)
    heads = read_tsv(HEADS_IN)
    copybook = read_tsv(COPYBOOK_IN)
    events = read_tsv(EVENTS_IN)
    rules = read_tsv(RULES)
    occurrences = read_tsv(OCCURRENCES)
    encoder = read_tsv(ENCODER)
    drills = read_tsv(DRILLS)

    check("source_counts", (len(cards), len(heads), len(copybook), len(events)) == (22, 16, 116, 381),
          f"cards={len(cards)}, heads={len(heads)}, statements={len(copybook)}, events={len(events)}")
    check("output_counts", (len(rules), len(occurrences), len(encoder), len(drills)) == (16, 28, 116, 7),
          f"rules={len(rules)}, occurrences={len(occurrences)}, statements={len(encoder)}, drills={len(drills)}")
    check("page_scope", {row["page"] for row in occurrences} <= ALLOWED_PAGES,
          "all occurrence selectors stay on the seven fixed prose pages")

    mode_counts = Counter(row["selection_mode"] for row in rules)
    expected_modes = Counter({"ONLY_FORM": 9, "SEMANTIC_VARIANT_MENU": 5, "RENDERER_ALLOGRAPH": 2})
    check("selection_modes", mode_counts == expected_modes,
          ", ".join(f"{key}={mode_counts[key]}" for key in sorted(mode_counts)))

    card_by_id = {row["joint_tuple_id"]: row for row in cards}
    whole_ids = set(card_by_id)
    source_whole_events = [row for row in events if row["joint_tuple_id"] in whole_ids]
    source_whole_by_event = {row["event_id"]: row for row in source_whole_events}
    output_by_event = {row["event_id"]: row for row in occurrences}
    check("whole_event_set", len(source_whole_events) == 28 and set(output_by_event) == set(source_whole_by_event),
          "all 28 and only the learned whole-card events are selected")

    occurrence_binding_ok = all(
        row["joint_tuple_id"] == source_whole_by_event[event_id]["joint_tuple_id"]
        and row["visible_surface"] == source_whole_by_event[event_id]["surface_display"]
        and row["statement_id"] == source_whole_by_event[event_id]["statement_id"]
        and row["surface_family"] == card_by_id[row["joint_tuple_id"]]["surface_family"]
        and bool(row["source_trigger_de"])
        and bool(row["exact_card_rule_de"])
        for event_id, row in output_by_event.items()
    )
    check("occurrence_binding", occurrence_binding_ok, "tuple, surface, statement, trigger, and rule match at every occurrence")

    rules_by_head = {row["headword_id"]: row for row in rules}
    head_ids = {row["headword_id"] for row in heads}
    check("headword_set", len(rules_by_head) == 16 and set(rules_by_head) == head_ids,
          "all sixteen teaching headwords have one selector rule")
    head_occurrence_counts = Counter(row["headword_id"] for row in occurrences)
    check("headword_occurrence_counts", all(
        int(row["occurrences"]) == head_occurrence_counts[row["headword_id"]] for row in rules
    ) and sum(head_occurrence_counts.values()) == 28, "rule occurrence counts sum to 28")

    semantic_heads = {row["headword_id"] for row in rules if row["selection_mode"] == "SEMANTIC_VARIANT_MENU"}
    renderer_heads = {row["headword_id"] for row in rules if row["selection_mode"] == "RENDERER_ALLOGRAPH"}
    only_heads = {row["headword_id"] for row in rules if row["selection_mode"] == "ONLY_FORM"}
    check("semantic_variant_cards", len({row["joint_tuple_id"] for row in occurrences if row["headword_id"] in semantic_heads}) == 11,
          "five semantic menus select eleven exact cards")
    check("only_form_cards", len({row["joint_tuple_id"] for row in occurrences if row["headword_id"] in only_heads}) == 9,
          "nine one-form heads select nine exact cards")

    renderer_rows = [row for row in occurrences if row["headword_id"] in renderer_heads]
    renderer_tuple_counts: dict[str, set[str]] = defaultdict(set)
    renderer_surface_counts: dict[str, set[str]] = defaultdict(set)
    for row in renderer_rows:
        renderer_tuple_counts[row["headword_id"]].add(row["joint_tuple_id"])
        renderer_surface_counts[row["headword_id"]].add(row["visible_surface"])
    renderer_ok = all(len(renderer_tuple_counts[head]) == 1 and len(renderer_surface_counts[head]) == 2 for head in renderer_heads)
    check("renderer_allographs", renderer_ok,
          "KLARLAUF and VORIGES each keep one tuple while alternating between two local surfaces")

    copy_by_statement = {row["statement_id"]: row for row in copybook}
    encoder_by_statement = {row["statement_id"]: row for row in encoder}
    check("encoder_statement_set", len(encoder_by_statement) == 116 and set(encoder_by_statement) == set(copy_by_statement),
          "all 116 copybook statements have an encoder row")
    plan_count = sum(int(row["whole_variant_count"]) for row in encoder)
    codebook_statement_count = sum(int(row["whole_variant_count"]) > 0 for row in encoder)
    sequence_binding_ok = all(
        row["target_surface_sequence"] == copy_by_statement[row["statement_id"]]["surface_sequence"]
        and row["target_architecture_sequence"] == copy_by_statement[row["statement_id"]]["architecture_sequence"]
        for row in encoder
    )
    check("encoder_full_binding", sequence_binding_ok and plan_count == 28 and codebook_statement_count == 22,
          f"whole_events={plan_count}, codebook_statements={codebook_statement_count}")

    drill_heads = {row["headword_id"] for row in drills}
    check("variant_drills", drill_heads == semantic_heads | renderer_heads and len(drill_heads) == 7,
          "the five semantic menus and two renderer allographs each receive one contrast drill")

    manual = MANUAL.read_text(encoding="utf-8")
    check("manual_contract", all(token in manual for token in ["ONLY_FORM", "SEMANTIC_VARIANT_MENU", "RENDERER_ALLOGRAPH", "sieben"]),
          "the manual distinguishes the three selection mechanisms and seven questions")
    check("sealed_selectors_absent", not any(page in "\n".join(
        "\t".join(row.values()) for table in [rules, occurrences, encoder, drills] for row in table
    ) for page in ["f84", "f84r", "f84v"]), "no sealed selector occurs in generated tables")

    before = {path.name: digest(path) for path in OUTPUTS}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True)
    after = {path.name: digest(path) for path in OUTPUTS}
    check("deterministic_rebuild", rebuilt.returncode == 0 and before == after,
          "all generated variant-book artifacts rebuilt byte-identically")

    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    result = {
        "status": status,
        "checks_passed": sum(bool(row["passed"]) for row in checks),
        "checks_total": len(checks),
        "counts": {
            "headwords": 16,
            "exact_whole_cards": 22,
            "whole_occurrences": 28,
            "statements": 116,
            "only_form_heads": mode_counts["ONLY_FORM"],
            "semantic_variant_heads": mode_counts["SEMANTIC_VARIANT_MENU"],
            "renderer_allograph_heads": mode_counts["RENDERER_ALLOGRAPH"],
            "variant_drills": len(drills),
        },
        "checks": checks,
        "artifact_sha256": {path.name: digest(path) for path in OUTPUTS},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
