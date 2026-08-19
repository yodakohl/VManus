#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"

import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import sha256_file  # noqa: E402


def main() -> None:
    p = json.loads((BASE / "artifacts/gdt362_canvas_correction.json").read_text())
    checks = []
    def ok(name: str, value: bool) -> None:
        assert value, name
        checks.append(name)
    ok("two_canvases", [x["canvas_id"] for x in p["corrected_canvases"]] == ["1006250", "1006251"])
    ok("fold_target_both", p["locus_canvas_scope"]["f101v2.13"] == ["1006250", "1006251"])
    ok("right_targets", all(p["locus_canvas_scope"][f"f101v2.{i}"] == ["1006251"] for i in range(14, 19)))
    ok("right_pixels_not_displayed", not p["access_at_correction"]["canvas_1006251_pixels_displayed"])
    ok("formal_sealed", not p["access_at_correction"]["target_formal_values_queried"])
    ok("f84_sealed", not p["access_at_correction"]["f84_accessed"])
    for rel, expected in p["inputs"].items():
        ok("hash_" + Path(rel).name, sha256_file(ROOT / rel) == expected)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
