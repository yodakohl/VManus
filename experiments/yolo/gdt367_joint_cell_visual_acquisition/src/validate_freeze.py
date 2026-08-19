#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa:E402

EXP = ROOT / "experiments/yolo/gdt367_joint_cell_visual_acquisition"
ART = EXP / "artifacts"


def main():
    freeze = json.loads((ART / "gdt367_freeze.json").read_text())
    with (ART / "gdt367_target_manifest.tsv").open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    body = dict(freeze); content_hash = body.pop("content_hash")
    checks = [
        len(rows) == 27,
        len({r["locus"] for r in rows}) == 27,
        Counter(r["physical_folio"] for r in rows) == Counter({"f89": 3, "f99": 14, "f100": 10}),
        Counter(r["contact_gap_state"] for r in rows) == Counter({"CONTACT": 8, "CLEAR_GAP": 18, "UNCERTAIN": 1}),
        all(r["new_visual_call_state"] == "NOT_YET_REVIEWED" for r in rows),
        all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in rows),
        freeze["new_axes"] == ["BROAD_CLOSED_FORM", "FORK_OR_BRANCH", "COLORED_FILL"],
        freeze["formal_access_before_visual_freeze"] is False,
        freeze["postexposure"] is True and freeze["single_observer"] is True,
        all(sha256_file(ROOT / p) == h for p, h in freeze["inputs"].items()),
        all(sha256_file(ROOT / p) == h for p, h in freeze["outputs"].items()),
        all(sha256_file(ROOT / p) == h for p, h in freeze["implementation"].items()),
        hashlib.sha256(canonical_json_bytes(body)).hexdigest() == content_hash,
    ]
    assert all(checks)
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
