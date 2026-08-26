#!/usr/bin/env python3
"""Validate the GDT446 identity/execution split and transformation audit."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt446_identity_execution_intake_split"
OUT = BASE / "artifacts"
CERTIFIER = BASE / "src/intake_certificate_v2.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt446_1563_catalog_identity_execution.tsv",
        OUT / "gdt446_4576_current_identity_execution.tsv",
        OUT / "gdt446_4938_candidate_identity_execution.tsv",
        OUT / "gdt446_1468_probe_identity_execution.tsv",
        OUT / "gdt446_1405_route_change_transformations.tsv",
        OUT / "gdt446_73_gdt445_decision_corrections.tsv",
        OUT / "gdt446_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    catalog = read_tsv(tracked[0])
    current = read_tsv(tracked[1])
    candidates = read_tsv(tracked[2])
    probes = read_tsv(tracked[3])
    transformations = read_tsv(tracked[4])
    corrections = read_tsv(tracked[5])
    result = json.loads(tracked[6].read_text(encoding="utf-8"))

    catalog_tiers = Counter(row["identity_route"] for row in catalog)
    catalog_decisions = Counter(row["execution_decision"] for row in catalog)
    current_decisions = Counter(row["execution_decision"] for row in current)
    candidate_decisions = Counter(row["execution_decision"] for row in candidates)
    absent_decisions = Counter(row["execution_decision"] for row in candidates if row["current_status"] == "ABSENT")
    probe_decisions = Counter(row["execution_decision"] for row in probes)
    transform_families = Counter(row["transformation_family"] for row in transformations)
    correction_datasets = Counter(row["dataset"] for row in corrections)
    catalog_stops = [row for row in catalog if row["execution_decision"] == "STOP"]
    delete_rows = [row for row in transformations if row["transformation_family"] == "DELETE_VISIBLE_FOCUS_SEPARATOR"]
    head_rows = [row for row in transformations if row["transformation_family"] == "REMOVE_INHERITED_ACTION_HEAD"]

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    cli_neutral_close = json.loads(subprocess.run([
        "python3", str(CERTIFIER), "--recipe", "AIR+DY"
    ], cwd=ROOT, check=True, capture_output=True, text=True).stdout)
    cli_context_close = json.loads(subprocess.run([
        "python3", str(CERTIFIER), "--recipe", "AIR+DY", "--incoming-action", "CH", "--scope-incoming-action", "NONE"
    ], cwd=ROOT, check=True, capture_output=True, text=True).stdout)
    cli_narrow_pair = json.loads(subprocess.run([
        "python3", str(CERTIFIER), "--recipe", "S+P+AL"
    ], cwd=ROOT, check=True, capture_output=True, text=True).stdout)

    checks = {
        "catalog_1563_unique": len(catalog) == len({row["component_recipe"] for row in catalog}) == 1563,
        "catalog_tiers_exact": catalog_tiers == {
            "IDENTITY_EXACT_OBSERVED": 1268,
            "IDENTITY_EXACT_FUTURE_HIGH": 4,
            "IDENTITY_EXACT_FUTURE_STRONG": 43,
            "IDENTITY_EXACT_SECOND_RING_AMBER": 2,
            "IDENTITY_EXACT_NARROW_APPENDIX": 246,
        },
        "catalog_execution_1482_45_36": catalog_decisions == {"READ": 1482, "READ_AMBER": 45, "STOP": 36},
        "catalog_stop_35_close_1_pair": Counter(row["blocked_factor_rules"] for row in catalog_stops) == {"CLOSE:NO_ACTIVE_ACTION": 35, "PAIR:S>P": 1},
        "catalog_observed_31_neutral_close_stops": sum(row["source_catalog_tier"] == "T0_EXACT_OBSERVED" and row["execution_decision"] == "STOP" and row["blocked_factor_rules"] == "CLOSE:NO_ACTIVE_ACTION" for row in catalog) == 31,
        "catalog_narrow_5_stops": sum(row["source_catalog_tier"] == "T4_NARROW_APPENDIX" and row["execution_decision"] == "STOP" for row in catalog) == 5,
        "catalog_identity_never_overrides": all(row["identity_does_not_override_execution"] == "YES" for row in catalog),
        "current_4576_unique": len(current) == len({row["event_id"] for row in current}) == 4576,
        "current_execution_4566_10_0": current_decisions == {"READ": 4566, "READ_AMBER": 10},
        "current_state_4576_match": sum(row["state_transition_match"] == "YES" for row in current) == 4576,
        "current_no_stop": all(row["execution_decision"] != "STOP" for row in current),
        "candidate_4938_unique": len(candidates) == len({row["component_recipe"] for row in candidates}) == 4938,
        "candidate_execution_4476_193_269": candidate_decisions == {"READ": 4476, "READ_AMBER": 193, "STOP": 269},
        "candidate_absent_4114_189_263": absent_decisions == {"READ": 4114, "READ_AMBER": 189, "STOP": 263},
        "candidate_667_exact_identity": sum(row["identity_route"] != "IDENTITY_NEW_VISIBLE_RECIPE" for row in candidates) == 667,
        "candidate_11_identity_only_stops": sum(row["identity_only_when_execution_stops"] == "YES" for row in candidates) == 11,
        "probe_1468_unique": len(probes) == len({row["probe_id"] for row in probes}) == 1468,
        "probe_gate_matches": all(row["probe_matches_source_gate"] == "YES" for row in probes),
        "probe_execution_1301_104_63": probe_decisions == {"READ": 1301, "READ_AMBER": 104, "STOP": 63},
        "transform_1405_unique": len(transformations) == len({row["transformation_id"] for row in transformations}) == 1405,
        "transform_family_471_934": transform_families == {"DELETE_VISIBLE_FOCUS_SEPARATOR": 471, "REMOVE_INHERITED_ACTION_HEAD": 934},
        "transform_all_pass": all(row["transformation_pass"] == "YES" for row in transformations),
        "transform_all_stop": all(row["transformed_execution_decision"] == "STOP" for row in transformations),
        "transform_all_state_safe": all(row["state_preserved"] == "YES" for row in transformations),
        "delete_all_named_pair": len(delete_rows) == 471 and all(row["transformed_blocked_rules"] == "PAIR:" + row["expected_change"].removeprefix("STOP_ON_PAIR:") for row in delete_rows),
        "head_all_named_close": len(head_rows) == 934 and all("CLOSE:NO_ACTIVE_ACTION" in row["transformed_blocked_rules"].split("|") for row in head_rows),
        "transform_no_identity_override": all(row["identity_override_used"] == "NO" for row in transformations),
        "corrections_73_unique": len(corrections) == len({row["correction_id"] for row in corrections}) == 73,
        "correction_dataset_10_43_20": correction_datasets == {"CURRENT": 10, "CANDIDATE": 43, "PROBE": 20},
        "correction_62_amber_11_stop": Counter(row["corrected_execution_decision"] for row in corrections) == {"READ_AMBER": 62, "STOP": 11},
        "corrections_all_old_read": all(row["legacy_gdt445_decision"] == "READ" for row in corrections),
        "corrections_reason_exact": all(row["correction_reason"] == "IDENTITY_CANNOT_OVERRIDE_FACTOR_EXECUTION" for row in corrections),
        "cli_neutral_close_identifies_but_stops": cli_neutral_close["identity_route"] == "IDENTITY_EXACT_NARROW_APPENDIX" and cli_neutral_close["execution_decision"] == "STOP" and cli_neutral_close["blocked_factor_rules"] == "CLOSE:NO_ACTIVE_ACTION",
        "cli_context_close_executes": cli_context_close["identity_route"] == "IDENTITY_EXACT_NARROW_APPENDIX" and cli_context_close["execution_decision"] in {"READ", "READ_AMBER"},
        "cli_narrow_pair_identifies_but_stops": cli_narrow_pair["identity_route"] == "IDENTITY_EXACT_NARROW_APPENDIX" and cli_narrow_pair["execution_decision"] == "STOP" and cli_narrow_pair["blocked_factor_rules"] == "PAIR:S>P",
        "all_execution_stops_state_safe": all(row["execution_stop_preserves_state"] == "YES" for row in catalog + current + candidates + probes if row["execution_decision"] == "STOP"),
        "result_status_exact": result["status"] == "IDENTITY_AND_EXECUTION_SPLIT__ELEVEN_FALSE_EXECUTIONS_STOPPED",
        "result_core_counts_exact": result["catalog_key_count"] == 1563 and result["current_event_count"] == 4576 and result["candidate_count"] == 4938 and result["probe_count"] == 1468 and result["transformation_count"] == result["transformation_pass_count"] == 1405,
        "result_corrections_exact": result["legacy_decision_correction_count"] == 73 and result["legacy_read_to_amber_count"] == 62 and result["legacy_read_to_stop_count"] == 11,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["occurrence_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt446_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
