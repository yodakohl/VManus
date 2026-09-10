#!/usr/bin/env python3
"""Validate the frozen source packet; this is not a Voynich model test."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

D = Path(__file__).resolve().parent


def read(name):
    return json.loads((D / name).read_text())


def check_hash(name, expected):
    assert hashlib.sha256((D / name).read_bytes()).hexdigest() == expected, name


images = read("IMAGE_SOURCES.json")
for item in images["files"]:
    check_hash(item["path"], item["sha256"])
rules = read("SOURCE_RULES_M.json")
check_hash("manifest.json", rules["institutional_manifest"]["sha256"])
for item in rules["image_bindings"]:
    check_hash(item["file"], item["sha256"])

replay = json.loads(subprocess.check_output(
    [sys.executable, str(D / "check_source_example.py")], text=True))
assert replay == read("SOURCE_EXAMPLE_CHECK_ROOT.json"), "root receipt differs"
peer = read("SOURCE_EXAMPLE_CHECK_B.json")
assert peer["source_receipt_sha256"] == replay["source_receipt_sha256"]
assert len(peer["checks"]) == len(replay["checks"]) == 11
for a, b in zip(replay["checks"], peer["checks"]):
    assert a["output"] == b["output_position"]
    assert a["inputs"] == b["input_positions"]
    assert [v % 2 for v in a["expected"]] == b["expected_bits"]
    assert [v % 2 for v in a["observed"]] == b["observed_bits"]
    assert a["equal"] and b["equal"]
assert rules["requested_full_program_gate"]["complete"] is False
print(json.dumps({"status": "PASS", "image_hashes": len(images["files"]),
                  "replayed_relations": 11, "peer_receipt_parity": True,
                  "complete_historical_program": False, "target_test": False}))
