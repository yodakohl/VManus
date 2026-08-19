#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt361_aq_contact_prospective"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks = []
    loc = read(BASE / "artifacts/gdt361_localizations.tsv")
    obs = read(BASE / "artifacts/gdt361_visual_observations.tsv")
    frozen = json.loads((BASE / "artifacts/gdt361_visual_freeze.json").read_text())
    checks += [len(loc) == 7, len(obs) == 7]
    checks.append([r["locus"] for r in loc] == [f"f102v2.{i}" for i in range(10, 17)])
    checks.append([r["target_id"] for r in loc] == [r["target_id"] for r in obs])
    checks.append(Counter(r["visual_state"] for r in obs) == Counter(CONTACT=4, CLEAR_GAP=2, UNCERTAIN=1))
    scored = [r for r in obs if r["prospective_score_eligible"] == "1"]
    checks.append(Counter(r["visual_state"] for r in scored) == Counter(CONTACT=3, CLEAR_GAP=2, UNCERTAIN=1))
    checks.append(all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs))
    checks.append(all(r["canvas_id"] == "1006252" for r in loc))
    checks.append(all(re.fullmatch(r"[0-9a-f]{64}", r["target_crop_sha256"]) for r in loc))
    for row in loc:
        cw, ch = int(row["canvas_width"]), int(row["canvas_height"])
        for field in ("context_xywh", "target_xywh"):
            x, y, w, h = map(int, row[field].split(","))
            checks.append(x >= 0 and y >= 0 and w > 0 and h > 0 and x + w <= cw and y + h <= ch)
    checks.append(frozen["status"] == "VISUAL_CALLS_FROZEN_BEFORE_SIX_ROW_FORMAL_REVEAL")
    checks.append(frozen["observer"]["independent_second_reviewer"] is False)
    checks.append(frozen["observer"]["target_formal_families_11_to_16_displayed_before_calls"] is False)
    checks.append(frozen["access"]["f84_accessed"] is False)
    for rel, digest in frozen["inputs"].items():
        checks.append(sha256_file(ROOT / rel) == digest)
    if not all(checks):
        raise SystemExit("FAIL")
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
