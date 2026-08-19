#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt361_aq_contact_prospective"


def main() -> None:
    checks = []
    freeze = json.loads((BASE / "artifacts/gdt361_freeze.json").read_text())
    with (BASE / "artifacts/gdt361_selection.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checks.append(len(rows) == 7)
    checks.append([r["locus"] for r in rows] == [f"f102v2.{i}" for i in range(10, 17)])
    checks.append(sum(r["prospective_score_eligible"] == "1" for r in rows) == 6)
    checks.append(rows[0]["prospective_score_eligible"] == "0")
    checks.append(all(r["visual_state"] == "SEALED_PENDING_DIRECT_REVIEW" for r in rows))
    checks.append(all(not r["page"].startswith("f84") for r in rows))
    checks.append(freeze["prediction"]["formal_predicate"] == "FIRST_GROUP_PREFIX_2:AQ")
    checks.append(freeze["access"]["f84_accessed"] is False)
    for rel, digest in freeze["inputs"].items():
        checks.append(sha256_file(ROOT / rel) == digest)
    for rel, digest in freeze["outputs"].items():
        checks.append(sha256_file(ROOT / rel) == digest)
    if not all(checks):
        raise SystemExit("FAIL")
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
