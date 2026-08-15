#!/usr/bin/env python3
"""Independently validate the scored GDT124 f106r transfer."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt124_result.json"
SCORES = ROOT / "gdt124_f106r_ar_ray_predictions.tsv"
FREEZE = ROOT / "gdt124_frozen_predictions.tsv"
TARGET = ROOT / "experiments/semantic_assumptions/star_morphology_entry/source_panel.tsv"
OUT = ROOT / "gdt124_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def metrics(rows, key):
    eligible = [row for row in rows if row[key] in {"7", "8"}]
    actual = Counter(row["actual_rays"] for row in eligible)
    hits = sum(row[key] == row["actual_rays"] for row in eligible)
    majority = max(actual.values())
    return {
        "eligible": len(eligible),
        "hits": hits,
        "accuracy": hits / len(eligible),
        "majority_baseline_hits": majority,
        "majority_baseline_accuracy": majority / len(eligible),
        "actual_7": actual["7"],
        "actual_8": actual["8"],
    }


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    frozen = read_tsv(FREEZE)
    scored = read_tsv(SCORES)
    target = {
        int(row["star_ordinal"]): row
        for row in read_tsv(TARGET)
        if row["page"] == "f106r"
    }
    checks = {}
    checks["schema"] = result["schema"] == "GDT124_Q20_AR_RAY_TRANSFER_RESULT_V1"
    checks["status"] = result["status"] == "Q20_AR_RAY_PROSPECTIVE_TRANSFER_FAILED"
    checks["target_census"] = len(target) == 15 and set(target) == set(range(1, 16))
    checks["row_order"] = len(scored) == len(frozen) == 14 and [r["star_ordinal"] for r in scored] == [r["star_ordinal"] for r in frozen]
    checks["freeze_preserved"] = all(all(row[key] == frozen[i][key] for key in frozen[i]) for i, row in enumerate(scored))
    checks["target_join"] = all(
        row["actual_rays"] == target[int(row["star_ordinal"])]["rays"]
        and row["actual_color"] == target[int(row["star_ordinal"])]["color"]
        and row["actual_tail"] == target[int(row["star_ordinal"])]["tail"]
        for row in scored
    )
    primary = metrics([r for r in scored if r["predicted_rays"] in {"7", "8"}], "predicted_rays")
    checks["primary_arithmetic"] = all(result["primary"][key] == value for key, value in primary.items())
    checks["primary_exact"] = primary["eligible"] == 11 and primary["hits"] == 5 and primary["majority_baseline_hits"] == 6 and primary["actual_7"] == 5 and primary["actual_8"] == 6
    positive = next(row for row in scored if row["star_ordinal"] == "13")
    checks["frozen_positive_failed"] = positive["predicted_rays"] == "7" and positive["actual_rays"] == "8" and result["primary"]["ordinal13_directional_hit"] is False and result["primary"]["one_sided_single_positive_hypergeometric_p"] == 1.0
    reading_keys = {"ZL3b": "zl_prediction", "IT2a": "it_prediction", "RF1b": "rf_prediction"}
    recomputed = {edition: metrics(scored, key) for edition, key in reading_keys.items()}
    checks["reading_arithmetic"] = all(all(result["reading_sensitivities"][edition][key] == value for key, value in values.items()) for edition, values in recomputed.items())
    checks["reading_exact"] = [recomputed[e]["hits"] for e in ("ZL3b", "IT2a", "RF1b")] == [6, 7, 7] and all(recomputed[e]["majority_baseline_hits"] == 8 for e in recomputed)
    checks["f84_sealed"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded_content_hash = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["result_content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded_content_hash
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("no star", "number", "plaintext", "translation"))
    status = "PASS_INDEPENDENT_TARGET_JOIN_AND_ARITHMETIC" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "GDT124_Q20_AR_RAY_TRANSFER_VALIDATION_V1",
        "status": status,
        "checks_total": len(checks),
        "checks_passed": sum(checks.values()),
        "checks": checks,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
