#!/usr/bin/env python3
"""Independent retained-artifact validator for GDT181."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[str] = []
    result = json.loads((ROOT / "gdt181_result.json").read_text())
    quality = rows("gdt179_quality_decoder.tsv")
    steps = rows("gdt180_f77_process_steps.tsv")
    transitions = rows("gdt180_f77_transition_translation.tsv")
    parses = rows("gdt181_worked_parses.tsv")
    evidence = rows("gdt181_evidence_matrix.tsv")
    models = rows("gdt181_model_comparison.tsv")
    lexicon = rows("gdt181_provisional_translation_lexicon.tsv")
    predictions = rows("gdt181_predictions.tsv")
    counter = rows("gdt181_counterexamples.tsv")
    grammar = json.loads((ROOT / "gdt181_generative_grammar.json").read_text())

    assert len(quality) == 8 and len(steps) == 6 and len(transitions) == 5
    n1_map = {"00":"COLD", "01":"MOIST", "10":"HOT", "11":"DRY"}
    d1_map = {"00":"HOT", "01":"DRY", "10":"COLD", "11":"MOIST"}
    for row in quality:
        bits = row["selector_bit"] + row["terminal_y_bit"]
        state_map = n1_map if row["register"] == "N1" else d1_map
        assert state_map[bits] == row["decoded_quality"] == row["frozen_position_quality"]
        expected = next(x for x in parses if x["parse_id"] == f"F57_{row['locus']}")
        assert expected["local_bits"] == bits
        assert expected["provisional_translation"] == state_map[bits] + "_POSITION"
        checks.append(f"f57:{row['locus']}")
    for row in steps:
        assert n1_map[row["local_state_bits"]] == row["provisional_quality_state"]
        expected = next(x for x in parses if x["parse_id"] == f"F77_{row['locus']}")
        assert expected["local_bits"] == row["local_state_bits"]
        checks.append(f"f77:{row['locus']}")
    expected_transitions = ["EARTH", "FIRE", "NONE_HOT_HOLD", "AIR", "WATER"]
    assert [r["provisional_transition_class"] for r in transitions] == expected_transitions
    assert [int(r["visible_emission"]) for r in transitions] == [1,1,0,1,1]
    assert all(int(r["exact_relation_match"]) == 1 for r in transitions)
    checks.append("f77_transition_topology")

    assert len(evidence) == 17
    assert {r["grade"] for r in evidence} >= {"CONFIRMED_STRUCTURAL","NEGATIVE_CONSTRAINT","PROVISIONAL_POSTHOC_PAGE_LOCAL"}
    checks.append("evidence_scope")
    totals = next(r for r in models if r["axis"] == "TOTAL")
    scores = {k:int(totals[k]) for k in ("COMPRESSED_NATURAL_LANGUAGE","PURE_TECHNICAL_NOTATION","HYBRID_TECHNICAL_COMPILER")}
    assert scores == result["abductive_scores"]
    assert max(scores, key=scores.get) == "HYBRID_TECHNICAL_COMPILER"
    checks.append("model_ranking")

    assert len(lexicon) == 17
    assert all(r["english_gloss"] == "UNASSIGNED" for r in lexicon[:9])
    assert all(r["translation_level"] != "SOURCE_WORD" for r in parses)
    assert len(parses) == 19
    checks.append("no_word_gloss_promotion")
    assert len(predictions) == 7 and all(r["failure"] and r["status"] == "UNTESTED" for r in predictions)
    assert len(counter) == 9
    checks.append("predictions_and_falsifiers")

    assert grammar["theory"] == result["leading_theory"]
    assert grammar["translation_policy"]["local_position_glosses_are_words"] is False
    assert grammar["local_state_decoder"]["surface_predicates_are_morpheme_boundaries"] is False
    assert grammar["translation_policy"]["f84r_target"] is False
    checks.append("grammar_claim_ceiling")

    for name, digest in result["inputs"].items():
        assert sha(ROOT / name) == digest
        checks.append(f"input:{name}")
    for name, digest in result["outputs"].items():
        assert sha(ROOT / name) == digest
        checks.append(f"output:{name}")
    for name, digest in result["documents"].items():
        assert sha(ROOT / name) == digest
        checks.append(f"document:{name}")
    assert sha(ROOT / "build_gdt181_hybrid_compiler_theory.py") == result["implementation"]
    checks.append("implementation")
    assert not result["f84r_accessed"] and not result["f84r_prediction_created"]
    checks.append("f84r_seal")

    validation = {
        "experiment":result["experiment"], "status":"PASS",
        "checks":checks, "checks_passed":len(checks),
        "result_sha256":sha(ROOT / "gdt181_result.json"),
    }
    (ROOT / "gdt181_validation.json").write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
