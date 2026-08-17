#!/usr/bin/env python3
"""Independent integrity and claim validation for GDT215."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKS: list[str] = []


def check(value: bool, name: str) -> None:
    if not value:
        raise AssertionError(name)
    CHECKS.append(name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    result_path = ROOT / "gdt215_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    evidence = rows("gdt215_theory_evidence_matrix.tsv")
    schema = rows("gdt215_latent_record_schema.tsv")
    predictions = rows("gdt215_prediction_registry.tsv")
    counter = rows("gdt215_counterexamples.tsv")

    check(result["experiment"] == "GDT215_Q13_GENERATIVE_THEORY_SYNTHESIS", "experiment")
    check(result["status"] == "HYBRID_BALNEOLOGICAL_RECORD_COMPILER_LEADING_SEMANTIC_KEY_ZERO", "status")
    check(result["leading_theory"] == "HYBRID_MEDICAL_RECORD_COMPILER_WITH_DIAGRAM_REFERENCE_REGISTER", "leading_theory")
    ranks = result["theory_class_ranking"]
    check([r["rank"] for r in ranks] == [1, 2, 3], "three_ranked_classes")
    check(ranks[0] == {"rank": 1, "class": "HYBRID_LANGUAGE_ABBREVIATION_NOTATION", "assessment": "LEADING"}, "hybrid_first")
    check(ranks[1]["class"] == "SEMANTIC_OR_TECHNICAL_NOTATION", "notation_second")
    check(ranks[2]["class"] == "COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE", "language_third")

    check(len(evidence) == 12, "twelve_evidence_rows")
    check({r["evidence_id"] for r in evidence} == {f"E{i:02d}" for i in range(1, 13)}, "evidence_ids")
    check(sum(r["strength"] == "STRONG_NEGATIVE" for r in evidence) == 4, "four_strong_negatives")
    check(any(r["source"] == "GDT187" and r["opposes"] == "EXACT_LABEL_TO_PROSE_KEY_DICTIONARY" for r in evidence), "key_negative_preserved")
    check(any(r["source"] == "GDT169" and r["opposes"] == "ONE_REFERENT_ONE_FIXED_HOST" for r in evidence), "referent_negative_preserved")
    check(any(r["source"] == "GDT168-174" and r["supports"] == "INSTRUMENT_LIMITED_HYBRID" for r in evidence), "calibration_preserved")

    check(len(schema) == 8, "eight_schema_layers")
    check([int(r["layer_order"]) for r in schema] == list(range(1, 9)), "schema_order")
    check({r["latent_layer"] for r in schema} == {"PAGE_PROFILE", "VISUAL_SYSTEM", "GRAPHICAL_LABEL_REGISTER", "RECORD_OPEN", "RECORD_BODY", "FIELD", "PAGE_HOST", "RENDERER"}, "schema_layers")
    host = next(r for r in schema if r["latent_layer"] == "PAGE_HOST")
    check(host["confidence"] == "BEST_FORMAL_CONTENT_CANDIDATE_NOT_DICTIONARY", "host_not_dictionary")
    check(host["prohibited_gloss"] == "lexical word; translated stem", "host_gloss_prohibited")
    check(all(r["prohibited_gloss"] for r in schema), "all_glosses_bounded")

    check(len(predictions) == 5, "five_predictions")
    check({r["prediction_id"] for r in predictions} == {f"P{i:02d}" for i in range(1, 6)}, "prediction_ids")
    check(sum(r["used_to_construct_theory"] == "NO" for r in predictions) == 4, "four_novel_predictions")
    check(sum(r["used_to_construct_theory"] == "PARTLY" for r in predictions) == 1, "one_partial_prediction")
    check(all(r["required_new_evidence"] and r["failure_effect"] for r in predictions), "predictions_falsifiable")

    check(len(counter) == 6, "six_counterexamples")
    check(all(r["unresolved"] == "1" for r in counter), "counterexamples_unresolved")
    check(any("22 are proximity-only" in r["awkward_fact"] for r in counter), "ownership_asymmetry")
    check(any("GDT187" in r["awkward_fact"] for r in counter), "key_failure_counterexample")

    semantic = result["semantic_coverage"]
    check(semantic["confirmed_words"] == 0, "zero_words")
    check(semantic["plaintext_clauses"] == 0, "zero_plaintext")
    check(semantic["licensed_semantic_states"] == 0, "zero_semantic_states")
    check(result["counts"] == {"evidence_rows": 12, "schema_layers": 8, "novel_predictions": 5, "counterexamples": 6}, "result_counts")
    check(len(result["hard_limits"]) == 5, "five_hard_limits")
    check("do not mine another internal host gloss" in result["next_route"], "external_next_route")
    check(result["f84"] == {"accessed": False, "input": False, "output": False}, "f84_flags")

    for name in [
        "gdt215_theory_evidence_matrix.tsv",
        "gdt215_latent_record_schema.tsv",
        "gdt215_prediction_registry.tsv",
        "gdt215_counterexamples.tsv",
        "gdt215_result.json",
    ]:
        low = (ROOT / name).read_text(encoding="utf-8").lower()
        check("f84r" not in low and "f84v" not in low, f"no_f84_payload:{name}")

    for name, expected in result["inputs_sha256"].items():
        check(sha(ROOT / name) == expected, f"input_hash:{name}")
    for name, expected in result["outputs_sha256"].items():
        check(sha(ROOT / name) == expected, f"output_hash:{name}")
    for name, expected in result["documents_sha256"].items():
        check(sha(ROOT / name) == expected, f"document_hash:{name}")
    check(sha(Path(__file__)) == result["validator_sha256"], "validator_hash")

    payload = dict(result)
    observed = payload.pop("content_sha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    check(hashlib.sha256(canonical.encode()).hexdigest() == observed, "content_hash")

    validation = {
        "experiment": result["experiment"],
        "status": "PASS",
        "checks_passed": len(CHECKS),
        "checks": CHECKS,
        "result_sha256": sha(result_path),
        "validator_sha256": sha(Path(__file__)),
    }
    (ROOT / "gdt215_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__":
    main()
