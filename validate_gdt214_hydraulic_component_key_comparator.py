#!/usr/bin/env python3
"""Independent integrity and claim validation for GDT214."""

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
    result_path = ROOT / "gdt214_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    sources = rows("gdt214_aljazari_source_manifest.tsv")
    obs = rows("gdt214_hydraulic_component_observations.tsv")
    comp = rows("gdt214_component_key_comparison.tsv")
    counter = rows("gdt214_counterexamples.tsv")
    parent = json.loads((ROOT / "gdt187_result.json").read_text(encoding="utf-8"))

    check(result["experiment"] == "GDT214_HYDRAULIC_COMPONENT_KEY_COMPARATOR", "experiment")
    check(result["status"] == "HYDRAULIC_COMPONENT_KEY_FORMAT_HISTORICALLY_ATTESTED_VOYNICH_CROSS_REFERENCE_PREDICTION_UNSUPPORTED", "status")
    check(result["decision"] == "RENDERING_ARCHITECTURE_LEAD_WITHOUT_KEY_DICTIONARY", "decision")
    check(len(sources) == 4, "four_sources")
    check(sum(r["source_class"] == "PRIMARY_INSTITUTIONAL_IMAGE" for r in sources) == 2, "two_images")
    check({r["object_id"] for r in sources if r["source_class"] == "PRIMARY_INSTITUTIONAL_IMAGE"} == {"55.121.11 obverse", "55.121.11 reverse"}, "two_sides")
    check(len(obs) == 6, "six_observations")
    check(sum(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs) == 4, "four_direct")
    check(sum(r["provenance"].startswith("EXISTING_") for r in obs) == 2, "two_source_interpretations")
    check(len(comp) == 7, "seven_axes")
    check(any(r["axis"] == "LABEL_KEY_REUSE_IN_EXPLANATORY_PROSE" and r["verdict"] == "VOYNICH_PREDICTION_NOT_SUPPORTED" for r in comp), "key_falsifier")
    check(any(r["axis"] == "EXACT_TOPOLOGY_OR_SOURCE_DESCENT" and r["verdict"] == "NO_EXACT_HOMOLOG" for r in comp), "no_exact_homolog")
    check(len(counter) == 4, "four_counterexamples")
    check(parent["status"] == "FOXTON_KEYED_OMISSION_NOT_SUPPORTED_REGISTER_LOCAL_WEAK_LEAD", "parent_status")
    check(parent["counts"]["label_groups"] == 215, "parent_label_groups")
    check(result["gdt187"]["same_page_prose_exact_host_reuse"] == 57, "reuse_57")
    check(result["gdt187"]["paragraph_opening_exact_host_reuse"] == 22, "opening_22")
    check(result["gdt187"]["max_ten_p"] == 0.2963, "parent_p")
    check(result["gdt187"]["key_dictionary_supported"] is False, "key_false")
    check(result["f84"] == {"accessed": False, "input": False, "output": False}, "f84_flags")

    for name in [
        "gdt214_aljazari_source_manifest.tsv",
        "gdt214_hydraulic_component_observations.tsv",
        "gdt214_component_key_comparison.tsv",
        "gdt214_counterexamples.tsv",
        "gdt214_result.json",
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
    (ROOT / "gdt214_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__":
    main()
