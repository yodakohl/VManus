#!/usr/bin/env python3
"""Independent integrity checks for the GDT395 pair protocol amendment."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
ART = EXP / "artifacts/gdt395_pair_protocol_amendment.json"
OUT = EXP / "artifacts/gdt395_pair_protocol_amendment_validation.json"


def main() -> None:
    data = json.loads(ART.read_text())
    checks = {}
    checks["bindings"] = all(
        hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
        for item in data["bindings"].values()
    )
    interface = json.loads((ROOT / data["bindings"]["original_interface"]["path"]).read_text())
    checks["original_method_preserved"] = data["original_method_sha256"] == interface["hashes"]["experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/METHOD.md"]
    checks["amended_method_is_new"] = data["bindings"]["amended_method"]["sha256"] != data["original_method_sha256"]
    with (ROOT / data["bindings"]["matches"]["path"]).open(newline="") as handle:
        matches = list(csv.DictReader(handle, delimiter="\t"))
    with (ROOT / data["bindings"]["audit"]["path"]).open(newline="") as handle:
        audit = list(csv.DictReader(handle, delimiter="\t"))
    counts = Counter((row["pair_id"], int(row["corpus_seed"])) for row in matches)
    checks["selection_exact"] = len(matches) == 400 and len(counts) == 40 and set(counts.values()) == {10}
    checks["records_unique"] = all(
        len({row["left_record_id"] for row in matches if row["pair_id"] == pair and int(row["corpus_seed"]) == seed}) == 10
        and len({row["right_record_id"] for row in matches if row["pair_id"] == pair and int(row["corpus_seed"]) == seed}) == 10
        for pair, seed in counts
    )
    checks["audit_exact"] = len(audit) == 40 and all(
        row["gate"] == "PASS"
        and int(row["matched_records"]) == 10
        and all(float(row[key]) == 0.0 for key in ("record_length_tv", "ordered_line_profile_tv", "within_record_separator_tv", "ambiguity_tv"))
        and max(float(row[key]) for key in ("ttr_difference", "top_type_rate_difference", "hapax_fraction_difference")) <= 0.1000001
        for row in audit
    )
    checks["scope_narrowed"] = data["pair_view_scope"] == "RECORD_LINE_LOCAL_ONLY" and len(data["masked_noncomparable_channels"]) == 6
    checks["no_truth_or_target"] = not data["oracle_read_by_pair_freezer"] and data["voynich_rows"] == 0 and not any(data["f84"].values())
    tmp = dict(data)
    expected = tmp.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    result = {
        "schema": "GDT395_PAIR_PROTOCOL_AMENDMENT_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "artifact_sha256": hashlib.sha256(ART.read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"})
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
