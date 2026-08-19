#!/usr/bin/env python3
"""Independent static validator for GDT373."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt373_functional_operator_roadmap"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    rp = ART / "gdt373_result.json"
    result = json.loads(rp.read_text())
    hyp = read_tsv(ART / "gdt373_hypothesis_registry.tsv")
    cross = read_tsv(ART / "gdt373_prior_route_crosswalk.tsv")
    sig = read_tsv(ART / "gdt373_candidate_signature_schema.tsv")
    expected = {
        "VARIABLE_RECORD_REWRITES", "HIERARCHICAL_SPACE_ATTACHMENT_SCOPE", "RECORD_DISCOURSE_OPERATORS",
        "VALENCY_RELATION_MARKERS", "COORDINATION_LIST_STRUCTURE", "ANAPHORA_ELLIPSIS_REPEAT",
        "PAIRED_CORRELATIVE_OPERATORS", "MARKEDNESS_NEGATION_EXCLUSION", "AGREEMENT",
        "ASSIGNMENT_EQUATION_POSSESSION", "QUANTIFICATION_PLURALITY", "TEMPORAL_PROCESS_OPERATORS",
        "OR_LIKE_MUTUAL_EXCLUSION", "COMPARISON_EQUALITY_RANGE", "CONDITIONAL_BRANCHING",
        "ACTION_IMPERATIVE_HEADS", "EMBEDDING_COMPLEMENTIZERS", "ARGUMENT_ALTERNATIONS",
        "DEIXIS_REFERENCE", "REGISTER_SPECIFIC_ALLOMORPHY", "ANALOGY_PARADIGM_RELATIONS",
        "OPEN_CLOSED_CLASS_DIAGNOSTICS",
    }
    check("schema", result["schema"] == "GDT373_RESULT_V1")
    check("family_count", len(hyp) == 22, str(len(hyp)))
    check("family_set", {x["hypothesis_family"] for x in hyp} == expected)
    check("unique_priorities", sorted(int(x["priority"]) for x in hyp) == list(range(1, 23)))
    check("distinct_endpoints", all(x["held_endpoint"] and x["registered_failure"] for x in hyp))
    check("crosswalk_size", len(cross) == 8, str(len(cross)))
    check("closed_ancestors", {x["prior_family"] for x in cross} >= {"STRING_PARADIGM", "SYNONYM_MINIMAL_PAIR", "MARGINAL_SCOPE_ORDER", "NEXT_STATE_OPERATOR", "PAGE_HOST_SUBSTRING_CONTEXT"})
    required_sig = {"symmetry", "valency_delta", "scope_level", "host_diversity", "optionality", "mutual_exclusion", "downstream_state_change", "record_length_effect", "physical_folios", "registers", "held_gain_bits", "max_search_p", "selector_cost_bits"}
    check("signature_fields", {x["field"] for x in sig} >= required_sig)
    check("no_scoring", result["candidate_forms_scored"] == 0)
    check("no_semantics", result["semantic_roles_assigned"] == 0)
    check("f84", result["f84_accessed"] is False)
    text = "\n".join(p.read_text() for p in (BASE / "METHOD.md", BASE / "REPORT.md"))
    check("atomic_tuple_rule", "atomic" in text.lower() and "PAGE_HOST is not factored" in text)
    check("prospective_rule", "untouched non-f84" in text)
    for rel, digest in result["inputs"].items():
        check("input_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["outputs"].items():
        check("output_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        check("implementation_" + rel, sha(ROOT / rel) == digest)
    payload = dict(result)
    stored = payload.pop("content_hash")
    check("content_hash", hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == stored)
    validation = {
        "schema": "GDT373_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_STATIC_REGISTRY_AND_HASH_VALIDATION",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": sha(rp),
        "validator_sha256": sha(BASE / "src/validate.py"),
        "f84_accessed": False,
    }
    (ART / "gdt373_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
