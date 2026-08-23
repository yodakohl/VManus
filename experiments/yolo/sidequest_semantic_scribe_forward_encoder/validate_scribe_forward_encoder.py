#!/usr/bin/env python3
"""Validate the creative ten-page scribe forward encoder."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
CASEBOOK = ROOT / "experiments/yolo/sidequest_semantic_integrated_workshop_casebook"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    rules = rows(OUT / "FORWARD_ENCODER_RULES.tsv")
    cards = rows(OUT / "ENCODER_173_CARD_TABLE.tsv")
    events = rows(OUT / "ENCODER_381_EVENT_TRACE.tsv")
    exercises = rows(OUT / "GENERATED_DICTATION_EXERCISES.tsv")
    unified = rows(OUT / "TEN_PAGE_776_ENCODER_TRACE.tsv")
    source_cards = rows(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    source_events = rows(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    source_phrases = rows(PROSE / "CLOSED_116_PHRASES.tsv")
    source_context = rows(CASEBOOK / "TEN_PAGE_776_CASE_CONTEXT.tsv")

    check("37_rules", len(rules) == 37, len(rules))
    check("rule_ids", [r["rule_id"] for r in rules] == [f"P{i:02d}" for i in range(1, 38)], [r["rule_id"] for r in rules])
    check("rule_tuple_unique", len({r["exact_tuple_id"] for r in rules}) == 37, len({r["exact_tuple_id"] for r in rules}))
    check("rules_generate_registered_only", all(r["status"] == "OBSERVED_PARADIGM__GENERATE_ONLY_REGISTERED_CARD" for r in rules), "all")
    source_card_ids = {r["joint_tuple_id"] for r in source_cards}
    check("all_rule_cards_exist", {r["exact_tuple_id"] for r in rules} <= source_card_ids, "all")

    check("173_cards", len(cards) == 173, len(cards))
    check("card_ids_exact", {r["joint_tuple_id"] for r in cards} == source_card_ids, "same IDs")
    check("card_occurrences_sum", sum(int(r["occurrences"]) for r in cards) == 381, sum(int(r["occurrences"]) for r in cards))
    card_modes = Counter(r["encoder_mode"] for r in cards)
    check("card_mode_counts", card_modes == Counter({"PARADIGM_RULE": 37, "COMPOSE_FROM_COMPONENTS": 115, "COPY_WHOLE_CARD": 21}), card_modes)
    source_arch = Counter(r["closed_architecture"] for r in source_cards)
    check("source_architecture_retained", source_arch == Counter({"PRODUCTIVE_COMPOSITION": 151, "MEMORIZED_WHOLE_CARD": 22}), source_arch)
    check("one_memorized_family_inside_rules", sum(r["encoder_mode"] == "PARADIGM_RULE" and next(x for x in source_cards if x["joint_tuple_id"] == r["joint_tuple_id"])["closed_architecture"] == "MEMORIZED_WHOLE_CARD" for r in cards) == 1, "CHEEY/SHEY whole family is P37")

    check("381_event_rows", len(events) == 381 == len(source_events), len(events))
    check("event_ids_ordered", [r["event_id"] for r in events] == [r["event_id"] for r in source_events], "ordered")
    src_by_id = {r["event_id"]: r for r in source_events}
    check("event_surface_preserved", all(r["selected_surface"] == src_by_id[r["event_id"]]["surface_display"] for r in events), "all")
    check("event_tuple_preserved", all(r["selected_exact_tuple_id"] == src_by_id[r["event_id"]]["joint_tuple_id"] for r in events), "all")
    check("event_semantics_preserved", all(r["semantic_input_de"] == src_by_id[r["event_id"]]["contextual_event_reading_de"] for r in events), "all")
    event_modes = Counter(r["encoder_mode"] for r in events)
    check("event_mode_counts", event_modes == Counter({"PARADIGM_RULE": 221, "COMPOSE_FROM_COMPONENTS": 136, "COPY_WHOLE_CARD": 24}), event_modes)
    check("commit_count", sum(r["local_close"] == "COMMIT_CELL" for r in events) == 89, Counter(r["local_close"] for r in events))
    check("renderer_values", set(r["renderer_choice"] for r in events) <= {"LINE_ENTRY_S_ALLOGRAPH", "POST_COMMIT_Q_ALLOGRAPH", "REGISTERED_LOCAL_ALLOGRAPH", "FIXED_SURFACE"}, Counter(r["renderer_choice"] for r in events))

    check("16_exercises", len(exercises) == 16, len(exercises))
    check("all_exercises_new", all(r["sequence_status"] == "NEW_SEQUENCE_FROM_OBSERVED_CARDS" for r in exercises), Counter(r["sequence_status"] for r in exercises))
    check("all_exercises_marked_nonmanuscript", all(r["use_status"] == "APPRENTICE_EXERCISE__NOT_MANUSCRIPT_TEXT" for r in exercises), "all")
    observed_surfaces = {r["surface_display"] for r in source_events}
    generated_tokens = [token for r in exercises for token in r["generated_surface_sequence"].split()]
    check("exercise_tokens_all_observed", set(generated_tokens) <= observed_surfaces, sorted(set(generated_tokens) - observed_surfaces))
    source_sequences = {r["surface_sequence"] for r in source_phrases}
    check("exercise_sequences_not_existing_statements", not ({r["generated_surface_sequence"] for r in exercises} & source_sequences), "none")

    check("776_unified", len(unified) == 776 == len(source_context), len(unified))
    check("unified_serial_order", [r["unified_serial"] for r in unified] == [r["unified_serial"] for r in source_context], "ordered")
    check("unified_surface_preserved", all(r["selected_surface"] == src["surface_display"] for r, src in zip(unified, source_context)), "all")
    check("unified_register_counts", Counter(r["register"] for r in unified) == Counter({"PROSE_WORKSHOP": 381, "ASTRO_DIAGRAM": 395}), Counter(r["register"] for r in unified))
    astro_modes = Counter(r["encoder_mode"] for r in unified if r["register"] == "ASTRO_DIAGRAM")
    check("astro_mode_counts", astro_modes == Counter({"ASTRO_SHARED_COMPOSITION": 332, "ASTRO_LOCAL_NOMENCLATOR_COPY": 63}), astro_modes)

    edition = (OUT / "FOUR_REENCODED_DOSSIERS.md").read_text(encoding="utf-8")
    check("all_116_statements_in_edition", all(edition.count(f"### {r['statement_id']} /") == 1 for r in source_phrases), "exactly once")
    check("all_16_exercises_in_edition", all(edition.count(f"**{r['exercise_id']}**") == 1 for r in exercises), "exactly once")
    report = (OUT / "SCRIBE_FORWARD_ENCODER_REPORT.md").read_text(encoding="utf-8")
    check("report_marks_exercises_nontext", "kein neu entdeckter Manuskripttext" in report and "nicht als Voynich-Text" in report, "present")

    content_names = ["FORWARD_ENCODER_RULES.tsv", "ENCODER_173_CARD_TABLE.tsv", "ENCODER_381_EVENT_TRACE.tsv",
                     "GENERATED_DICTATION_EXERCISES.tsv", "TEN_PAGE_776_ENCODER_TRACE.tsv", "FOUR_REENCODED_DOSSIERS.md",
                     "SCRIBE_ENCODER_MANUAL.md", "SCRIBE_FORWARD_ENCODER_REPORT.md"]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed_page_token = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed_page_token.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_scribe_forward_encoder.py")], cwd=ROOT, check=True)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    passed = all(bool(r["pass"]) for r in checks)
    result = {"status": "PASS" if passed else "FAIL", "checks_passed": sum(bool(r["pass"]) for r in checks),
              "checks_total": len(checks), "checks": checks,
              "counts": {"rules": 37, "cards": 173, "events": 381, "statements": 116,
                         "exercises": 16, "unified_groups": 776, "astro_shared": 332, "astro_local": 63}}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for item in checks:
            if not item["pass"]:
                print(f"FAIL {item['check']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
