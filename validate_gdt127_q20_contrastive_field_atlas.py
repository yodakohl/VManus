#!/usr/bin/env python3
"""Validate GDT127 field census, contrastive atlas, nulls, and hashes."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt127_result.json"
FILES = {
    "fields": ROOT / "gdt127_q20_field_inventory.tsv",
    "templates": ROOT / "gdt127_q20_field_templates.tsv",
    "subs": ROOT / "gdt127_q20_field_substitutions.tsv",
    "null": ROOT / "gdt127_q20_field_null.tsv",
    "visual": ROOT / "gdt127_q20_field_visual_leads.tsv",
    "counter": ROOT / "gdt127_q20_field_counterexamples.tsv",
}
OUT = ROOT / "gdt127_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=2e-10):
    return abs(float(a) - float(b)) <= tolerance


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    data = {key: read(path) for key, path in FILES.items()}
    checks = {}
    checks["schema"] = result["schema"] == "GDT127_Q20_CONTRASTIVE_FIELD_ATLAS_RESULT_V1"
    checks["status"] = result["status"] == "Q20_CONTRASTIVE_FIELD_SLOTS_PRESENT_NOT_ENRICHED"
    checks["field_count"] = len(data["fields"]) == 4443 and Counter(row["edition"] for row in data["fields"]) == {"ZL3b": 1483, "IT2a": 1487, "RF1b": 1473}
    checks["field_ids"] = len({row["field_id"] for row in data["fields"]}) == len(data["fields"])
    checks["field_geometry"] = all(int(row["field_group_count"]) == len(row["group_tokens"].split("|")) == len(row["page_hosts"].split("|")) for row in data["fields"])
    checks["f84_absent"] = not any(row["page"].startswith("f84r") or row["locus"].startswith("f84r") for row in data["fields"])
    checks["template_count"] = len(data["templates"]) == result["eligible_templates"] == 26
    checks["template_eligibility"] = all(int(row["occurrences"]) >= 4 and int(row["physical_folios"]) >= 2 and int(row["distinct_host_fills"]) >= 2 for row in data["templates"])
    checks["substitution_count"] = len(data["subs"]) == result["one_slot_substitution_types"] == 21 and sum(int(row["cross_folio_pair_support"]) for row in data["subs"]) == 22
    checks["substitution_positions"] = all(1 <= int(row["changed_position_1based"]) <= int(row["field_group_count"]) for row in data["subs"])
    checks["strongest_formula"] = result["strongest_formula"]["host_a"] == "polor" and result["strongest_formula"]["host_b"] == "yshor" and int(result["strongest_formula"]["cross_folio_pair_support"]) == 2 and result["strongest_formula"]["skeleton_stable_all_readings"] == 1
    checks["visual_count"] = len(data["visual"]) == 4
    visual = {(row["page"], row["field_tokens"]): (row["rays"], row["tail"], row["color"]) for row in data["visual"]}
    checks["visual_overlay"] = visual[("f104v", "yshor|sheedy")][:2] == ("8", "1") and visual[("f105r", "okeeddl|sheokedy")][:2] == ("8", "2") and visual[("f112v", "polor|sheedy")][:2] == ("7", "1") and visual[("f115v", "polor|sheedy")][:2] == ("7", "1")
    checks["visual_postselected"] = all(row["overlay_state"] == "POSTSELECTED_EXPLORATORY_VISUAL_OVERLAY" for row in data["visual"])
    checks["null_count"] = len(data["null"]) == 2 and {row["null_model"] for row in data["null"]} == {"PAGE_CELL_LENGTH", "PAGE_CELL_LENGTH_EDGE"}
    checks["null_observed"] = all(int(row["worlds"]) == 4096 and int(row["observed_exact_fill_pairs"]) == result["observed_exact_fill_pairs"] == 1 and int(row["observed_one_slot_pairs"]) == result["observed_one_slot_pairs"] == 22 for row in data["null"])
    edge = next(row for row in data["null"] if row["null_model"] == "PAGE_CELL_LENGTH_EDGE")
    checks["null_non_enrichment"] = close(edge["one_slot_inclusive_p"], .384427629973) and float(edge["one_slot_inclusive_p"]) > .05
    checks["counterexamples"] = len(data["counter"]) == 3
    checks["f84_flags"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded_hash = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded_hash
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("Formal contrastive", "no star", "plaintext", "translation"))
    status = "PASS_FIELD_CENSUS_NULL_AND_HASHES" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT127_Q20_CONTRASTIVE_FIELD_ATLAS_VALIDATION_V1", "status": status,
        "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
        "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
