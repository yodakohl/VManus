#!/usr/bin/env python3
"""Independent retained-artifact validation for GDT186."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = [
    ROOT / "gdt186_source_manifest.tsv",
    ROOT / "gdt186_historical_mechanisms.tsv",
    ROOT / "gdt186_architecture_comparison.tsv",
    ROOT / "gdt186_predictions.tsv",
    ROOT / "gdt186_counterexamples.tsv",
]
METHOD = ROOT / "GDT186_FOXTON_HYBRID_CIPHER_COMPARATOR_METHOD.md"
REPORT = ROOT / "GDT186_FOXTON_HYBRID_CIPHER_COMPARATOR_REPORT.md"
RESULT = ROOT / "gdt186_result.json"
VALID = ROOT / "gdt186_validation.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    manifest, facts, comparison, predictions, counter = map(read, FILES)
    checks = []

    def ck(name, condition):
        assert condition, name
        checks.append(name)

    ck("status", result["status"] == "FOXTON_SIMPLE_SUBSTITUTION_INSUFFICIENT_HYBRID_RUBRIC_POINTER_ROUTE_OPEN")
    ck("source_count", len(manifest) == 10)
    ck("source_ids_unique", len({x["source_id"] for x in manifest}) == 10)
    ck("primary_scholarly_source", any(x["source_id"] == "FOXTON_ARTICLE" and x["authority"] == "SCHOLARLY_ARTICLE" for x in manifest))
    ck("official_catalogue", any(x["source_id"] == "TRINITY_CATALOGUE" and x["authority"] == "OFFICIAL_MANUSCRIPT_CATALOGUE" for x in manifest))
    ck("payload_hash_shapes", all(len(x["retrieved_payload_sha256"]) == 64 for x in manifest))
    ck("facts_count", len(facts) == 13)
    ck("facts_unique", len({x["fact_id"] for x in facts}) == 13)
    ck("facts_sources_resolve", {x["source_id"] for x in facts} <= {x["source_id"] for x in manifest})
    ck("facts_supported", all(x["support"].startswith("SUPPORTED") for x in facts))
    ck("architecture_count", len(comparison) == 13)
    ck("fit_vocabulary", {x["fit"] for x in comparison} <= {"MATCH", "PARTIAL", "CONTRADICTION", "UNRESOLVED"})
    counts = result["counts"]
    ck("fit_counts", counts["matches"] == 1 and counts["partials"] == 8 and counts["contradictions"] == 4)
    ck("prediction_count", len(predictions) == 4)
    ck("prediction_ids", [x["prediction_id"] for x in predictions] == ["P01", "P02", "P03", "P04"])
    ck("new_routes_unrun", all(x["status"] == "FROZEN_NOT_RUN" for x in predictions[:3]))
    ck("direct_route_failed", predictions[3]["status"] == "ALREADY_FALSIFIED_FOR_TESTED_FAMILIES")
    ck("counterexample_count", len(counter) == 7)
    ck("direct_model_insufficient", result["direct_foxton_selective_substitution"] == "INSUFFICIENT")
    ck("hybrid_only_open", result["historical_hybrid_rubric_codebook_mechanism"] == "ATTESTED_ROUTE_OPEN_NOT_VOYNICH_CONFIRMED")
    ck("f84_false", result["f84r_accessed"] is False)
    ck("no_f84_artifact_payload", all("f84r" not in p.read_text(encoding="utf-8").lower() for p in FILES))
    ck("output_hashes", all(result["outputs"][p.name] == sha(p) for p in FILES))
    ck("document_hashes", result["documents"][METHOD.name] == sha(METHOD) and result["documents"][REPORT.name] == sha(REPORT))
    ck("implementation_hash", result["implementation"] == sha(ROOT / "run_gdt186_foxton_hybrid_cipher_comparator.py"))
    validation = {
        "experiment": "GDT186_VALIDATION",
        "status": "PASS",
        "checks": len(checks),
        "check_names": checks,
        "result_sha256": sha(RESULT),
        "scope": "retained source/fact/architecture integrity; external-source statements remain scholarly-source claims",
    }
    VALID.write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("PASS", len(checks))


if __name__ == "__main__":
    main()
