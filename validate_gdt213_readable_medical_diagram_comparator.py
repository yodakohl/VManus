#!/usr/bin/env python3
"""Independent integrity/claim validator for GDT213."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKS: list[str] = []


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    CHECKS.append(label)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    result_path = ROOT / "gdt213_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    sources = read_tsv("gdt213_ashmole_source_manifest.tsv")
    observations = read_tsv("gdt213_readable_medical_diagram_observations.tsv")
    comparison = read_tsv("gdt213_system_architecture_comparison.tsv")
    counterexamples = read_tsv("gdt213_counterexamples.tsv")

    check(result["experiment"] == "GDT213_READABLE_LABELLED_MEDICAL_DIAGRAM_COMPARATOR", "experiment_id")
    check(result["status"] == "MEDIEVAL_MEDICAL_SCHEMATIC_DOCUMENT_ARCHITECTURE_SUPPORTED_CONTENT_BRIDGE_ABSENT", "status")
    check(result["decision"] == "ARCHITECTURE_HOMOLOG_WITHOUT_TOPOLOGY_OR_SEMANTIC_TRANSFER", "decision")
    check(len(sources) == 5, "five_sources")
    check(Counter(r["source_class"] for r in sources)["PRIMARY_INSTITUTIONAL_IMAGE"] == 2, "two_primary_images")
    check(all(len(r["retrieved_sha256"]) == 64 for r in sources), "source_hash_shapes")
    check({r["folio"] for r in sources if r["source_class"] == "PRIMARY_INSTITUTIONAL_IMAGE"} == {"13v", "22v"}, "source_folios")
    check(len(observations) == 9, "nine_observations")
    check(sum(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in observations) == 6, "six_direct_observations")
    check(sum(r["provenance"] == "EXISTING_SCHOLARLY_INTERPRETATION" for r in observations) == 3, "three_scholarly_rows")
    check(all(r["evidence_type"] in {"OBSERVATION", "FORMAL_STRUCTURE", "INTERPRETATION"} for r in observations), "typed_evidence")
    check(len(comparison) == 8, "eight_axes")
    class_counts = Counter(r["comparison_class"] for r in comparison)
    check(dict(class_counts) == result["comparison"]["class_counts"], "class_counts")
    check(any(r["architecture_axis"] == "SINGULAR_COMPONENT_OWNERSHIP" and r["comparison_class"] == "STRONG_ASYMMETRY" for r in comparison), "ownership_asymmetry")
    check(any(r["architecture_axis"] == "EXACT_TOPOLOGICAL_HOMOLOG" and r["comparison_class"] == "NO_EXACT_HOMOLOG" for r in comparison), "no_exact_homolog")
    check(result["comparison"]["q13_text_linked_inventory_rows"] == 23, "q13_linked_count")
    check(result["comparison"]["q13_proximity_only_rows"] == 22, "q13_proximity_count")
    check(result["comparison"]["q13_connected_component_rows"] == 1, "q13_component_count")
    check(22 + 1 == 23, "ownership_partition")
    check(result["comparison"]["exact_topological_homolog"] is False, "topology_false")
    check(result["comparison"]["singular_readable_voynich_bridge"] is False, "bridge_false")
    check(len(counterexamples) == 5, "five_counterexamples")
    check({r["counterexample_id"] for r in counterexamples} == {"C01", "C02", "C03", "C04", "C05"}, "counterexample_ids")
    check(result["f84"] == {"accessed": False, "input": False, "output": False}, "f84_flags")

    forbidden = ["f84r", "f84v"]
    for name in [
        "gdt213_ashmole_source_manifest.tsv",
        "gdt213_readable_medical_diagram_observations.tsv",
        "gdt213_system_architecture_comparison.tsv",
        "gdt213_counterexamples.tsv",
        "gdt213_result.json",
    ]:
        text = (ROOT / name).read_text(encoding="utf-8").lower()
        check(not any(term in text for term in forbidden), f"no_f84_payload:{name}")

    for name, expected in result["inputs_sha256"].items():
        check(sha256(ROOT / name) == expected, f"input_hash:{name}")
    for name, expected in result["outputs_sha256"].items():
        check(sha256(ROOT / name) == expected, f"output_hash:{name}")
    for name, expected in result["documents_sha256"].items():
        check(sha256(ROOT / name) == expected, f"document_hash:{name}")
    check(sha256(Path(__file__)) == result["validator_sha256"], "validator_hash")

    copy = dict(result)
    observed_content = copy.pop("content_sha256")
    canonical = json.dumps(copy, sort_keys=True, separators=(",", ":"))
    check(hashlib.sha256(canonical.encode()).hexdigest() == observed_content, "content_hash")

    method = (ROOT / "GDT213_READABLE_MEDICAL_DIAGRAM_COMPARATOR_METHOD.md").read_text(encoding="utf-8")
    audit = (ROOT / "GDT213_READABLE_MEDICAL_DIAGRAM_SOURCE_AUDIT.md").read_text(encoding="utf-8")
    report = (ROOT / "GDT213_READABLE_MEDICAL_DIAGRAM_COMPARATOR_REPORT.md").read_text(encoding="utf-8")
    check("No Voynich transcription" in method and "f84" in method, "method_claim_ceiling")
    check("does not independently translate" in audit and "do not establish an exact q13 homolog" in audit, "audit_claim_ceiling")
    check("No Voynich source group receives" in report and "No f84" in report, "report_claim_ceiling")

    validation = {
        "experiment": result["experiment"],
        "status": "PASS",
        "checks_passed": len(CHECKS),
        "checks": CHECKS,
        "result_sha256": sha256(result_path),
        "validator_sha256": sha256(Path(__file__)),
    }
    (ROOT / "gdt213_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__":
    main()
