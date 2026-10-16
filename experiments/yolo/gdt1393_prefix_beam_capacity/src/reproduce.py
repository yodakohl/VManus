#!/usr/bin/env python3
"""Replay frozen computations in a fresh directory without altering originals."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        raise SystemExit("Choose a fresh output directory; no existing result is overwritten")
    artifacts, arrays = output / "artifacts", output / "arrays"
    artifacts.mkdir(parents=True)
    producer = load("prefix_capacity_producer", E / "src/run.py")
    validator = load("prefix_capacity_validator", E / "src/validate.py")
    producer.A = validator.A = artifacts
    producer.generate(arrays)
    save(artifacts / "BEAMS_SEAL.json", {
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "beams_sha256": sha(artifacts / "BEAMS.json"),
        "scope": "Replay seal on already exposed source-only outputs; no new blind test"})
    truth = ROOT / "experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts/TRUTH.json"
    save(artifacts / "TRUTH_RELEASE_RECEIPT.json", {
        "released_utc": datetime.now(timezone.utc).isoformat(),
        "beams_seal_sha256": sha(artifacts / "BEAMS_SEAL.json"),
        "truth_sha256": sha(truth), "historical_truth_previously_public": True})
    producer.compare(arrays, truth)
    validator.validate(arrays, truth)
    actual = json.loads((artifacts / "COMPARISON.json").read_text())
    expected = json.loads((E / "artifacts/COMPARISON.json").read_text())
    fields = ["status", "cases", "positive_prefix_hits", "positive_cases",
              "negative_prefix_hits", "negative_cases", "truth_sha256", "cases_sha256", "lock_sha256"]
    assert all(actual[field] == expected[field] for field in fields)
    result = {"status": "PASS_REPLAY_SCIENTIFIC_FIELDS", "fields": fields,
              "independent_validation": "PASS_INDEPENDENT_VALIDATION",
              "scope": "All six beams and all eighteen old case comparisons replayed; no new evidence"}
    save(output / "REPLAY_VALIDATION.json", result)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
