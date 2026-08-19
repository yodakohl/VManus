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
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt364_reproductive_structure_joint_atlas"
ART = EXP / "artifacts"


def main() -> None:
    with (ART / "gdt364_panel.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    payload = json.loads((ART / "gdt364_freeze.json").read_text())
    checks = [len(rows) == 34, len({r["page"] for r in rows}) == 34,
              len({r["physical_folio"] for r in rows}) == 29,
              Counter(r["visual_state"] for r in rows) == Counter(FLOWER_SIDE=19, BERRY_NO_CIRCLES=8, NO_FRUIT_OR_FLOWER=7),
              all(r["provenance"] == "EXISTING_HUMAN_ANNOTATION" for r in rows),
              not any(r["page"].startswith("f84") for r in rows),
              payload["old_results"]["rewritten"] is False,
              all(sha256_file(ROOT / rel) == digest for rel, digest in payload["inputs"].items()),
              all(sha256_file(ROOT / rel) == digest for rel, digest in payload["implementation"].items()),
              all(sha256_file(ROOT / rel) == digest for rel, digest in payload["outputs"].items())]
    copy = dict(payload); digest = copy.pop("content_hash")
    checks.append(hashlib.sha256(canonical_json_bytes(copy)).hexdigest() == digest)
    assert all(checks)
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__": main()
