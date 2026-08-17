#!/usr/bin/env python3
"""Independent validation of the GDT219 pre-target freeze."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent; CHECKS: list[str] = []


def check(value: bool, name: str) -> None:
    if not value: raise AssertionError(name)
    CHECKS.append(name)


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    result_path = ROOT / "gdt219_prediction_freeze.json"; result = json.loads(result_path.read_text(encoding="utf-8"))
    labels = read("gdt219_f76_label_key_freeze.tsv"); nulls = read("gdt219_null_training_distribution.tsv")
    source = [row for row in read("gdt012_annotated_core_inventory.tsv") if row["page"] == "f76r"]
    discovery = [row for row in read("gdt217_terminal_key_inventory.tsv") if row["side"] == "PARAGRAPH_INITIAL"]
    check(result["experiment"] == "GDT219_SINGLE_SIGN_KEY_FREEZE", "experiment")
    check(result["status"] == "FROZEN_BEFORE_F76_PARAGRAPH_KEY_REVEAL", "status")
    check(len(source) == len(labels) == 9, "nine_labels")
    check(all(row["kind"] == "L" and row["family_length"] == "1" and row["group_count"] == "1" for row in source), "all_single_group_signs")
    expected = sorted((row["locus"], row["family_surface"]) for row in source)
    check(sorted((row["locus"], row["family_key"]) for row in labels) == expected, "label_keys_exact")
    check(result["label_key_set"] == sorted({row["family_key"] for row in labels}), "key_set")
    check(len(discovery) == 42, "forty_two_training_openings")
    counts = Counter(row["family_surface"][:1] for row in discovery)
    check({row["family_key"]: int(row["discovery_paragraph_opening_occurrences"]) for row in nulls} == dict(counts), "null_frequency_exact")
    check(result["null"] == {"training_opening_occurrences": 42, "draw_size": 2, "without_replacement": True, "worlds": 861}, "null_freeze")
    check(result["decision"] == {"required_hits": 2, "required_distinct_target_keys": 2, "maximum_exact_p": .05}, "decision_freeze")
    check(result["target"] == {"page": "f76r", "physical_folio": "f76", "label_loci": 9, "paragraph_start_loci": 2, "paragraph_family_payload_opened": False}, "target_unopened")
    check(result["access_disclosure"]["raw_label_surfaces_previously_displayed"] is True, "raw_access_disclosed")
    check(result["access_disclosure"]["target_paragraph_keys_displayed_or_retained"] is False, "paragraph_keys_unopened")
    check("gdt016" not in (ROOT / "freeze_gdt219_single_sign_key.py").read_text(encoding="utf-8"), "freezer_has_no_target_source")
    check(result["f84r"] == {"accessed": False, "input": False, "output": False}, "f84r")
    for group in ("inputs_sha256", "outputs_sha256", "documents_sha256"):
        for name, digest in result[group].items(): check(sha(ROOT / name) == digest, f"hash:{group}:{name}")
    check(sha(ROOT / "freeze_gdt219_single_sign_key.py") == result["implementation_sha256"], "implementation_hash")
    check(sha(Path(__file__)) == result["validator_sha256"], "validator_hash")
    payload = dict(result); observed = payload.pop("content_sha256")
    check(hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == observed, "content_hash")
    validation = {"experiment": result["experiment"], "status": "PASS", "checks_passed": len(CHECKS), "checks": CHECKS, "result_sha256": sha(result_path), "validator_sha256": sha(Path(__file__))}
    (ROOT / "gdt219_freeze_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__": main()
