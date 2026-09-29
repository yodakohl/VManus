#!/usr/bin/env python3
"""Validate bounded metadata and the stopped GDT1086 decision."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt1086_f68v2_cardinal_side_reference"

def main():
    x = json.loads((EXP / "artifacts/RESULT.json").read_text())
    assert x["status"] == "INVALID_OWNER_MAPPING__TEXT_ECHO_NOT_RUN"
    assert x["transcription_tsv_queried"] is False and x["transcription_content_scored"] is False
    assert len(x["inventory_rows"]) == 12
    assert [r["slot_index"] for r in x["inventory_rows"] if r["unit"] == "S1"] == ["1", "2", "3", "4"]
    assert [r["slot_index"] for r in x["inventory_rows"] if r["unit"] == "E1"] == [str(i) for i in range(1,9)]
    inv = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
    assert hashlib.sha256(inv.read_bytes()).hexdigest() == x["text_blind_inventory_sha256"]
    assert x["sealed_f84_f84r"] == "CLOSED" and x["confirmed_lexemes"] == 0
    v = {"experiment":"GDT1086","status":"PASS","scope":"machine checks metadata and stop only; does not verify human image reading"}
    (EXP / "artifacts/VALIDATION.json").write_text(json.dumps(v,indent=2)+"\n")
    print("PASS")

if __name__ == "__main__":
    main()
