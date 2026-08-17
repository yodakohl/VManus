#!/usr/bin/env python3
"""Independent integrity/status validation for GDT202."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
RESULT = R / "gdt202_result.json"
PRED = R / "gdt202_prediction_reconciliation.tsv"
LEX = R / "gdt202_lexicon_disposition.tsv"
MODEL = R / "gdt202_model_disposition.tsv"
OUT = R / "gdt202_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()


def rows(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    result = json.loads(RESULT.read_text())
    pred, lex, model = rows(PRED), rows(LEX), rows(MODEL)
    source_pred = rows(R / "gdt181_predictions.tsv")
    checks = []

    def ck(name, condition):
        checks.append((name, bool(condition)))

    ck("schema", result["schema"] == "GDT202_HYBRID_THEORY_RECONCILIATION_RESULT_V1")
    ck("status", result["status"] == "HYBRID_COMPILER_ARCHITECTURE_RETAINED_F57_F77_SEMANTIC_DECODER_WITHDRAWN")
    ck("seven_predictions", len(pred) == len(source_pred) == 7)
    ck("prediction_ids", [r["id"] for r in pred] == [r["id"] for r in source_pred] == [f"P{i}" for i in range(1, 8)])
    ck("predictions_verbatim", all(a["original_prediction"] == b["prediction"] and a["original_failure"] == b["failure"] for a, b in zip(pred, source_pred)))
    ck("zero_translation_successes", all(r["translation_bearing_success"] == "0" and r["semantic_value_recovered"] == "NONE" for r in pred))
    ck("one_supported_negative", sum(r["reconciliation_status"] == "NEGATIVE_PREDICTION_SUPPORTED" for r in pred) == 1)
    ck("seventeen_lexicon_rows", len(lex) == 17)
    ck("six_formal_retained", sum(r["disposition"] == "FORMAL_ONLY_RETAINED" for r in lex) == 6)
    ck("eleven_semantic_withdrawn", sum(r["disposition"] == "SEMANTIC_GLOSS_WITHDRAWN" for r in lex) == 11)
    ck("no_active_english_gloss", all(r["active_english_gloss"] == "UNASSIGNED" for r in lex))
    disposition = {r["component"]: r["disposition"] for r in model}
    ck("compiler_retained", disposition.get("PAGE_CONDITIONED_HYBRID_TECHNICAL_COMPILER") == "LEADING_ABDUCTIVE_ARCHITECTURE_ONLY")
    ck("f57_withdrawn", disposition.get("F57_TWO_BIT_QUALITY_DECODER") == "WITHDRAWN_FROM_ACTIVE_SEMANTICS")
    ck("f77_withdrawn", disposition.get("F77_QUALITY_STATE_PROCESS") == "WITHDRAWN_FROM_ACTIVE_SEMANTICS")
    ck("result_counts", result["counts"] == {"predictions_reconciled": 7, "translation_bearing_prediction_successes": 0, "negative_architectural_predictions_supported": 1, "formal_entries_retained": 6, "semantic_entries_withdrawn": 11, "confirmed_source_words": 0, "confirmed_plaintext_clauses": 0, "licensed_semantic_state_assignments": 0})
    expected_status = {
        "gdt182_result.json": "LOCAL_F57_DECODER_DESCRIPTIVE_NOT_ABOVE_FEATURE_MULTIPLICITY",
        "gdt184_result.json": "R2_FOURFOLD_REFERENCE_SEQUENCE_LEADING_FOUR_ELEMENT_ID_TABLE_FAILED",
        "gdt185_result.json": "F57_R2_DOES_NOT_INDEX_F67V1_17_SECTOR_TEXT",
        "gdt195_result.json": "ALCHEMICAL_SOURCE_FAMILY_PLAUSIBLE_EXACT_F77_HOMOLOG_NOT_FOUND",
        "gdt197_result.json": "TERMINAL_Y_SEQUENCE_SIGNAL_NOT_UNIQUE_OT_AXIS_NOT_SELECTED",
        "gdt199_result.json": "F77_RENDERER_SWITCH_DOES_NOT_TRANSFER_TO_ARCHIVED_LABELS",
        "gdt201_result.json": "F77_ZONE_RENDERER_FAILS_COMPARABLE_F83_PANEL",
    }
    for name, status in expected_status.items():
        ck("source_status:" + name, json.loads((R / name).read_text())["status"] == status)
    ck("gdt199_one_of_four", json.loads((R / "gdt199_result.json").read_text())["exact_hits"] == 1)
    ck("gdt201_zero_of_four", json.loads((R / "gdt201_result.json").read_text())["exact_hits"] == 0 and json.loads((R / "gdt201_result.json").read_text())["exact_predictions"] == 4)
    ck("all_named_evidence_exists", all((R / name).exists() for r in pred for name in r["downstream_evidence"].split(";")))
    ck("no_f84_prediction", not any("f84" in (r["original_prediction"] + r["finding"]).lower() for r in pred) and not any(result["f84r"].values()))
    for section in ("inputs", "implementation", "outputs", "documents"):
        for name, digest in result[section].items():
            ck("hash:" + name, sha(R / name) == digest)
    content = dict(result)
    stored = content.pop("result_content_sha256")
    ck("content_hash", csha(content) == stored)
    bad = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT202_VALIDATION_V1",
        "status": "PASS" if not bad else "FAIL",
        "checks_passed": sum(passed for _, passed in checks),
        "checks_total": len(checks),
        "failed": bad,
        "result_sha256": sha(RESULT),
        "scope": "Independent prediction-text, downstream-status, lexicon-disposition, count, seal-flag, and hash validation; no semantic decoder is validated.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps(validation, sort_keys=True))
    raise SystemExit(bool(bad))


if __name__ == "__main__":
    main()
