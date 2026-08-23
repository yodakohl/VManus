#!/usr/bin/env python3
"""Validate the bounded four-scribe creative copyshop."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
ENCODER = ROOT / "experiments/yolo/sidequest_semantic_scribe_forward_encoder"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    profiles = rows(OUT / "FOUR_SCRIBE_PROFILES.tsv")
    census = rows(OUT / "MULTI_SURFACE_FAMILY_CENSUS.tsv")
    statements = rows(OUT / "FOUR_HAND_116_STATEMENT_RENDERINGS.tsv")
    exercises = rows(OUT / "FOUR_HAND_16_EXERCISE_RENDERINGS.tsv")
    trace = rows(OUT / "RENDERER_TOKEN_TRACE.tsv")
    dictionary = rows(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    source_events = rows(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    source_phrases = rows(PROSE / "CLOSED_116_PHRASES.tsv")
    source_exercises = rows(ENCODER / "GENERATED_DICTATION_EXERCISES.tsv")

    profile_ids = ["S1_BARE_MASTER", "S2_Q_CELL_SCRIBE", "S3_S_LINE_SCRIBE", "S4_MIXED_COMPACT"]
    check("four_profiles", len(profiles) == 4, len(profiles))
    check("profile_ids", [r["scribe_id"] for r in profiles] == profile_ids, [r["scribe_id"] for r in profiles])
    check("same_dictionary", all(r["shared_dictionary"] == "SAME_173_EXACT_CARDS" for r in profiles), "all")
    check("meaning_tuple_invariant_policy", all(r["semantic_policy"] == "MEANING_AND_TUPLE_SEQUENCE_INVARIANT" for r in profiles), "all")

    multi_source = [r for r in dictionary if "|" in r["surface_family"]]
    check("34_multi_surface_families", len(census) == 34 == len(multi_source), len(census))
    check("multi_tuple_ids_exact", {r["joint_tuple_id"] for r in census} == {r["joint_tuple_id"] for r in multi_source}, "same IDs")
    check("all_family_meanings_invariant", all(r["tuple_meaning_status"] == "INVARIANT_ACROSS_REGISTERED_SURFACES" for r in census), "all")

    check("464_statement_renderings", len(statements) == 116 * 4, len(statements))
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statements:
        by_statement[row["statement_id"]].append(row)
    check("116_statement_ids", set(by_statement) == {r["statement_id"] for r in source_phrases}, len(by_statement))
    check("four_profiles_per_statement", all({r["scribe_id"] for r in rr} == set(profile_ids) and len(rr) == 4 for rr in by_statement.values()), "all")
    check("statement_tuple_invariant", all(len({r["tuple_sequence"] for r in rr}) == 1 for rr in by_statement.values()), "all")
    check("statement_meaning_invariant", all(len({r["semantic_readback_de"] for r in rr}) == 1 for rr in by_statement.values()), "all")
    check("statement_flags", all(r["tuple_sequence_changed"] == "NO" and r["meaning_changed"] == "NO" and r["copy_status"] == "COUNTERFACTUAL_WORKSHOP_COPY__NOT_MANUSCRIPT_TRANSCRIPTION" for r in statements), "all")
    statement_surface_sets = {sid: {r["counterfactual_surface_sequence"] for r in rr} for sid, rr in by_statement.items()}
    check("68_statements_visibly_vary", sum(len(values) > 1 for values in statement_surface_sets.values()) == 68, sum(len(values) > 1 for values in statement_surface_sets.values()))

    check("64_exercise_renderings", len(exercises) == 16 * 4, len(exercises))
    by_exercise: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in exercises:
        by_exercise[row["exercise_id"]].append(row)
    check("16_exercise_ids", set(by_exercise) == {r["exercise_id"] for r in source_exercises}, len(by_exercise))
    check("four_profiles_per_exercise", all({r["scribe_id"] for r in rr} == set(profile_ids) and len(rr) == 4 for rr in by_exercise.values()), "all")
    check("exercise_tuple_invariant", all(len({r["tuple_sequence"] for r in rr}) == 1 for rr in by_exercise.values()), "all")
    check("exercise_flags", all(r["tuple_sequence_changed"] == "NO" and r["meaning_changed"] == "NO" and r["all_surfaces_registered"] == "YES" and r["copy_status"] == "APPRENTICE_EXERCISE__NOT_MANUSCRIPT_TEXT" for r in exercises), "all")
    exercise_surface_sets = {sid: {r["scribe_surface_sequence"] for r in rr} for sid, rr in by_exercise.items()}
    check("10_exercises_visibly_vary", sum(len(values) > 1 for values in exercise_surface_sets.values()) == 10, sum(len(values) > 1 for values in exercise_surface_sets.values()))

    expected_trace = 381 * 4 + sum(len(r["generated_surface_sequence"].split()) for r in source_exercises) * 4
    check("1732_token_trace", len(trace) == expected_trace == 1732, len(trace))
    family_by_tuple = {r["joint_tuple_id"]: set(r["surface_family"].split("|")) for r in dictionary}
    check("every_chosen_surface_registered", all(r["chosen_surface"] in family_by_tuple[r["joint_tuple_id"]] for r in trace), "all")
    check("meaning_never_changes", all(r["meaning_change"] == "NONE" for r in trace), "all")
    reason_counts = Counter(r["choice_reason"] for r in trace)
    check("q_choices_present", reason_counts["REGISTERED_Q_AFTER_COMMIT"] == 70, reason_counts)
    check("s_choices_present", reason_counts["REGISTERED_S_LINE_ENTRY"] == 136, reason_counts)
    check("q_only_after_commit", all(r["previous_card_closed"] == "YES" and r["chosen_surface"].startswith("q") for r in trace if r["choice_reason"] == "REGISTERED_Q_AFTER_COMMIT"), "all")
    check("s_only_at_line_start", all(r["line_start"] == "YES" and r["chosen_surface"].startswith("s") for r in trace if r["choice_reason"] == "REGISTERED_S_LINE_ENTRY"), "all")

    copybook = (OUT / "FOUR_SCRIBE_COPYBOOK.md").read_text(encoding="utf-8")
    check("all_exercises_in_copybook", all(copybook.count(f"## {r['exercise_id']}:") == 1 for r in source_exercises), "all")
    check("copybook_not_real_hand_claim", "keine Identifikation realer Voynich-Hände" in copybook, "present")
    report = (OUT / "FOUR_SCRIBE_COPYSHOP_REPORT.md").read_text(encoding="utf-8")
    check("report_role_caveat", "keine Zuweisung an reale Handschriftenhände" in report, "present")

    content_names = ["FOUR_SCRIBE_PROFILES.tsv", "MULTI_SURFACE_FAMILY_CENSUS.tsv",
                     "FOUR_HAND_116_STATEMENT_RENDERINGS.tsv", "FOUR_HAND_16_EXERCISE_RENDERINGS.tsv",
                     "RENDERER_TOKEN_TRACE.tsv", "FOUR_SCRIBE_COPYBOOK.md", "FOUR_SCRIBE_COPYSHOP_REPORT.md"]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed_page_token = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed_page_token.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_four_scribe_copyshop.py")], cwd=ROOT, check=True)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    passed = all(bool(r["pass"]) for r in checks)
    result = {"status": "PASS" if passed else "FAIL", "checks_passed": sum(bool(r["pass"]) for r in checks),
              "checks_total": len(checks), "checks": checks,
              "counts": {"profiles": 4, "multi_surface_families": 34, "statements": 116,
                         "statement_renderings": 464, "varying_statements": 68, "exercises": 16,
                         "exercise_renderings": 64, "varying_exercises": 10, "token_trace": 1732,
                         "q_choices": 70, "s_choices": 136}}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for item in checks:
            if not item["pass"]:
                print(f"FAIL {item['check']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
