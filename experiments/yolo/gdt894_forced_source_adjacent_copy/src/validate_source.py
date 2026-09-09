#!/usr/bin/env python3
"""Replay the independent GDT894 source/map binding audit.

No target query, new source acquisition, model fitting, or key modification.
The historical byte comparison uses the published pre-target commit.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
OLD = ROOT / "experiments/yolo/gdt893_global_source_montage_word_code/artifacts"
PRE_TARGET_COMMIT = "9c2d4b55"


def audit(source_units_path):
    prediction_path = E / "artifacts/PREDICTION.json"
    forced_path = OLD / "RF_FORCED_SOURCE.json"
    prediction = json.loads(prediction_path.read_text())
    forced = json.loads(forced_path.read_text())
    source_units = json.loads(source_units_path.read_text())
    lock = json.loads((OLD / "INPUT_LOCK.json").read_text())
    source_hash = sha256(source_units_path.read_bytes()).hexdigest()
    checks = {}
    checks["source_units_hash"] = source_hash == prediction["source_units_sha256"] == lock["source_units_sha256"]
    checks["conditional_map"] = prediction["conditional_map"] == forced["conditional_global_map"]
    anchor = prediction["anchor"]
    checks["anchor_arrays"] = (anchor["source_group_ids"] == forced["source_group_ids"]
                               and anchor["cipher_words"] == forced["literal_cipher_words"]
                               and anchor["source_words"] == forced["written_source_words"])
    checks["anchor_scope"] = (anchor["edition"] == forced["edition"] == "RF1b"
                              and anchor["page"] == forced["page"] == "f103v")
    checks["all_provenance_retained"] = anchor["provenance"] == forced["provenance"]
    checks["single_provenance"] = len(forced["provenance"]) == 1
    if not checks["single_provenance"]:
        raise ValueError("The frozen single-provenance audit no longer applies")
    provenance = forced["provenance"][0]
    units = [item for item in source_units["units"] if item["id"] == provenance["unit"]]
    checks["unique_unit"] = len(units) == 1
    if not checks["unique_unit"]:
        raise ValueError("The frozen source unit is missing or duplicated")
    unit = units[0]
    start = provenance["start"]
    end = start + provenance["length"]
    words = unit["words"]
    checks["source_unit_identity"] = unit["source"] == provenance["source"]
    checks["anchor_exact_source_slice"] = words[start:end] == anchor["source_words"]
    left, right = max(0, start - 128), min(len(words), end + 128)
    checks["preceding_exact_source_slice"] = prediction["horizons"]["preceding"] == {
        "offsets": list(range(left - start, 0)), "source_words": words[left:start]}
    checks["following_exact_source_slice"] = prediction["horizons"]["following"] == {
        "offsets": list(range(1, right - end + 1)), "source_words": words[end:right]}
    checks["primary_symbolic_hash"] = (sha256((OLD / "RF1b_SYMBOLIC.json").read_bytes()).hexdigest()
                                        == forced["primary_symbolic_result_sha256"])
    for label, path in (("prediction", prediction_path), ("forced_source", forced_path)):
        historical = subprocess.run(
            ["git", "show", PRE_TARGET_COMMIT + ":" + path.relative_to(ROOT).as_posix()],
            cwd=ROOT, check=True, capture_output=True).stdout
        checks[label + "_matches_pre_target_commit"] = historical == path.read_bytes()
    return dict(status="PASS" if all(checks.values()) else "FAIL", checks=checks,
                pre_target_commit=PRE_TARGET_COMMIT, source_unit=provenance["unit"],
                source_unit_tokens=len(words), anchor_start=start, anchor_length=end - start,
                preceding_positions=start - left, following_positions=right - end,
                conditional_values=len(prediction["conditional_map"]), source_units_sha256=source_hash,
                forced_source_sha256=sha256(forced_path.read_bytes()).hexdigest(),
                prediction_sha256=sha256(prediction_path.read_bytes()).hexdigest(),
                validator_sha256=sha256(Path(__file__).read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-units", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=E / "artifacts/SOURCE_VALIDATION.json")
    args = parser.parse_args()
    result = audit(args.source_units)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]),
                      "source_unit": result["source_unit"],
                      "validator_sha256": result["validator_sha256"]}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
