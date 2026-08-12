#!/usr/bin/env python3
"""Validate the registered LTG001 target-free calibration artifact."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULT = RESULTS / "ltg001_latent_channel_calibration.json"
REPORT = RESULTS / "ltg001_latent_channel_calibration_report.md"
VALIDATION = RESULTS / "ltg001_latent_channel_calibration_validation.json"
RUNNER = HERE / "run_ltg001_latent_channel_calibration.py"
CORE = HERE / "ltg001_latent_channel_core.py"
EXPECTED_FAMILIES = {
    "NULL_DIRECT": (16, 0),
    "SHARED_CHANNEL": (16, 16),
    "ONE_FOLIO_CHANNEL": (8, 0),
    "FAMILY_PRIVATE_CHANNEL": (8, 0),
    "DOMINANT_POLICY_ONLY": (8, 0),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = RESULT.read_bytes()
    data = json.loads(raw)
    assert raw == (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    checks = 1
    assert data["status"] == "PASS_TARGET_FREE_LATENT_CHANNEL_INSTRUMENT"; checks += 1
    assert data["world_count"] == 56 == len(data["worlds"]); checks += 1
    assert data["real_panel_scored"] is False; checks += 1
    assert all(data["gates"].values()) and len(data["gates"]) == 6; checks += 1
    assert [row["family"] for row in data["world_registry"]] == list(EXPECTED_FAMILIES); checks += 1
    seen = set()
    for family, (world_count, expected_pass) in EXPECTED_FAMILIES.items():
        worlds = [world for world in data["worlds"] if world["family"] == family]
        assert len(worlds) == world_count
        assert [world["index"] for world in worlds] == list(range(world_count))
        assert data["by_family"][family]["worlds"] == world_count
        decisions = sum(world["summary"]["decision"] == "PASS_REUSABLE_LATENT_CHANNEL" for world in worlds)
        assert decisions == expected_pass == data["by_family"][family]["pass_count"]
        checks += 4
        for world in worlds:
            assert world["world_id"] not in seen
            seen.add(world["world_id"])
            summary = world["summary"]
            expected_decision = "PASS_REUSABLE_LATENT_CHANNEL" if all(summary["gates"].values()) else "FINAL_NONCONFIRMATION"
            assert summary["decision"] == expected_decision
            assert summary["event_count"] > 0 and summary["folio_count"] >= 80
            assert len(world["selected_k_by_fold"]) == 5
            assert all(value in {2, 3, 4, 6, 8} for value in world["selected_k_by_fold"])
            checks += 5
    shared = [world for world in data["worlds"] if world["family"] == "SHARED_CHANNEL"]
    recovered = sum(abs(world["selected_k_median"] - world["planted_k"]) <= 1 for world in shared)
    assert recovered == data["by_family"]["SHARED_CHANNEL"]["k_within_one"] == 16; checks += 1
    for path in (RUNNER, CORE):
        ast.parse(path.read_text(encoding="utf-8")); checks += 1
    source = RUNNER.read_text(encoding="utf-8")
    assert "real_panel_scored\": False" in source
    assert "DOMINANT_POLICY_ONLY" in source and "|BACKGROUND" in source
    checks += 2
    report = REPORT.read_text(encoding="utf-8")
    assert "0/16 positive" in report and "16/16 positive" in report
    assert "0/8 positive" in report and "No manuscript member outcome was scored" in report
    checks += 2
    validation = {
        "status": "PASS_LTG001_CALIBRATION_ARTIFACT_VALIDATION",
        "checks": checks,
        "result_sha256": sha(RESULT),
        "report_sha256": sha(REPORT),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
