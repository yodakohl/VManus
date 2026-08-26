#!/usr/bin/env python3
"""Validate GDT445's integrated prospective intake certificates."""

from __future__ import annotations

import csv
import importlib.util
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
BASE = ROOT / "experiments/yolo/gdt445_prospective_intake_certificate"
OUT = BASE / "artifacts"
CERTIFIER_PATH = BASE / "src/intake_certificate.py"
SOURCE_CANDIDATES = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4938_candidate_factor_gate.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tracked = [
        OUT / "gdt445_4576_current_intake_certificates.tsv",
        OUT / "gdt445_4938_candidate_intake_certificates.tsv",
        OUT / "gdt445_1468_mechanism_probe_certificates.tsv",
        OUT / "gdt445_13_route_intake_manual.tsv",
        OUT / "gdt445_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    current = read_tsv(tracked[0])
    candidates = read_tsv(tracked[1])
    probes = read_tsv(tracked[2])
    manual = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    source_candidates = {row["candidate_recipe"]: row for row in read_tsv(SOURCE_CANDIDATES)}
    certifier = load_module("gdt445_certifier_for_validation", CERTIFIER_PATH)

    candidate_routes = Counter(row["primary_intake_route"] for row in candidates)
    candidate_decisions = Counter(row["certificate_decision"] for row in candidates)
    probe_families = Counter(row["probe_family"] for row in probes)
    probe_routes = Counter(row["primary_intake_route"] for row in probes)
    current_gates = Counter(row["factor_gate_status"] for row in current)
    absent = [row for row in candidates if row["current_status"] == "ABSENT"]
    close_probes = [row for row in probes if row["probe_family"] == "INHERITED_HEAD_CLOSE_MATRIX"]
    slot_probes = [row for row in probes if row["probe_family"] == "VISIBLE_SLOT_SEPARATED_PAIR_MATRIX"]
    stop_probes = [row for row in probes if row["probe_family"] == "FIXED_STOP_DECK"]

    recomputed_candidates = []
    for row in candidates:
        source = source_candidates[row["component_recipe"]]
        gate = certifier.READER.gate_recipe(row["component_recipe"], "NONE")
        fresh = certifier.issue_certificate(row["component_recipe"], precomputed_gate=gate)
        recomputed_candidates.append(
            all(gate[field] == source[field] == row[field] for field in (
                "factor_gate_status", "scope_selector_rules", "portable_factor_rules",
                "amber_factor_rules", "blocked_factor_rules",
            ))
            and all(str(fresh[field]) == row[field] for field in (
                "primary_intake_route", "certificate_decision", "mechanism_flags",
                "outgoing_action", "outgoing_argument",
            ))
        )

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    all_rows = current + candidates + probes
    checks = {
        "current_4576_unique": len(current) == len({row["event_id"] for row in current}) == 4576,
        "current_all_exact_catalog": all(row["primary_intake_route"] == "EXACT_CATALOG" and row["exact_catalog_key"] == "YES" for row in current),
        "current_state_4576_match": sum(row["state_transition_match"] == "YES" for row in current) == 4576,
        "current_factor_status_4566_10": current_gates == {"FACTOR_GREEN_CROSS_PAGE": 4566, "FACTOR_AMBER_LOCAL_APPENDIX": 10},
        "current_28_visible_slot_occurrences": sum("VISIBLE_SLOT_SEPARATED_CHAIN" in row["mechanism_flags"] for row in current) == 28,
        "candidate_4938_unique": len(candidates) == len({row["component_recipe"] for row in candidates}) == 4938,
        "candidate_source_set_exact": set(source_candidates) == {row["component_recipe"] for row in candidates},
        "candidate_all_recompute": all(recomputed_candidates),
        "candidate_all_factor_match_flag": all(row["factor_gate_matches_gdt441"] == "YES" for row in candidates),
        "candidate_route_counts_exact": candidate_routes == {
            "EXACT_CATALOG": 667,
            "KNOWN_FACTOR_COMPOSITION_GREEN": 3649,
            "KNOWN_FACTOR_COMPOSITION_AMBER": 160,
            "VISIBLE_SLOT_SEPARATED_CHAIN_GREEN": 203,
            "VISIBLE_SLOT_SEPARATED_CHAIN_AMBER": 1,
            "STOP_UNLICENSED_DIRECT_PAIR": 210,
            "STOP_CLOSE_NEEDS_ACTIVE_HEAD": 42,
            "STOP_MULTIPLE_UNLICENSED_FACTORS": 6,
        },
        "candidate_decision_counts_exact": candidate_decisions == {"READ": 4519, "READ_AMBER": 161, "STOP": 258},
        "candidate_372_observed_exact": sum(row["current_status"] == "OBSERVED" and row["primary_intake_route"] == "EXACT_CATALOG" for row in candidates) == 372,
        "candidate_295_absent_exact": sum(row["current_status"] == "ABSENT" and row["primary_intake_route"] == "EXACT_CATALOG" for row in candidates) == 295,
        "candidate_absent_partition": len(absent) == 4566 and Counter(row["certificate_decision"] for row in absent) == {"READ": 4147, "READ_AMBER": 161, "STOP": 258},
        "probe_1468_unique": len(probes) == len({row["probe_id"] for row in probes}) == 1468,
        "probe_family_counts_exact": probe_families == {
            "FIXED_STOP_DECK": 47,
            "INHERITED_HEAD_CLOSE_MATRIX": 936,
            "VISIBLE_SLOT_SEPARATED_PAIR_MATRIX": 484,
            "UNSEEN_ATOM_GUARD": 1,
        },
        "probe_all_match_source": all(row["probe_matches_source"] == "YES" for row in probes),
        "fixed_stop_47_stop": len(stop_probes) == 47 and all(row["certificate_decision"] == "STOP" for row in stop_probes),
        "fixed_stop_routes_44_2_1": Counter(row["primary_intake_route"] for row in stop_probes) == {
            "STOP_UNLICENSED_DIRECT_PAIR": 44,
            "STOP_UNLICENSED_FOCUS_EDGE": 2,
            "STOP_CLOSE_NEEDS_ACTIVE_HEAD": 1,
        },
        "close_gate_841_93_2": Counter(row["factor_gate_status"] for row in close_probes) == {
            "FACTOR_GREEN_CROSS_PAGE": 841,
            "FACTOR_AMBER_LOCAL_APPENDIX": 93,
            "STOP__UNLICENSED_FACTOR": 2,
        },
        "close_all_visibly_flagged": len(close_probes) == 936 and all("INHERITED_HEAD_CLOSE" in row["mechanism_flags"] for row in close_probes),
        "close_two_stops_focus_only": sum(row["certificate_decision"] == "STOP" for row in close_probes) == 2 and all(row["primary_intake_route"] == "STOP_UNLICENSED_FOCUS_EDGE" for row in close_probes if row["certificate_decision"] == "STOP"),
        "slot_gate_460_11_13": Counter(row["factor_gate_status"] for row in slot_probes) == {
            "FACTOR_GREEN_CROSS_PAGE": 460,
            "FACTOR_AMBER_LOCAL_APPENDIX": 11,
            "STOP__UNLICENSED_FACTOR": 13,
        },
        "slot_all_visibly_flagged": len(slot_probes) == 484 and all("VISIBLE_SLOT_SEPARATED_CHAIN" in row["mechanism_flags"] for row in slot_probes),
        "slot_never_promotes_direct": all(row["direct_pair_promoted"] == "NO" for row in slot_probes),
        "unseen_guard_exact": probe_routes["STOP_UNSEEN_ATOM"] == 1 and any(row["probe_family"] == "UNSEEN_ATOM_GUARD" and row["certificate_decision"] == "STOP" for row in probes),
        "manual_13_unique_routes": len(manual) == len({row["primary_intake_route"] for row in manual}) == 13,
        "manual_stop_never_mutates": all(row["may_mutate_state"] == "NO" for row in manual if row["primary_intake_route"].startswith("STOP")),
        "all_stops_state_safe": all(row["state_preserved_on_stop"] == "YES" for row in all_rows if row["certificate_decision"] == "STOP"),
        "no_direct_pair_promotions": all(row["direct_pair_promoted"] == "NO" for row in all_rows),
        "no_invisible_separators": all(row["invisible_separator_invented"] == "NO" for row in all_rows),
        "no_meaning_revisions": all(row["meaning_revision"] == "NO" for row in all_rows),
        "no_surface_predictions": all(row["surface_prediction"] == "NO" for row in all_rows),
        "no_occurrence_predictions": all(row["occurrence_prediction"] == "NO" for row in all_rows),
        "result_status_exact": result["status"] == "ONE_EXECUTABLE_CERTIFICATE_INTEGRATES_EXACT_FACTOR_CONTEXT_SLOT_AND_STOP_ROUTES",
        "result_counts_exact": result["current_event_certificate_count"] == 4576 and result["current_exact_catalog_count"] == 4576 and result["current_state_transition_match_count"] == 4576 and result["candidate_certificate_count"] == 4938 and result["mechanism_probe_count"] == 1468 and result["mechanism_probe_match_count"] == 1468,
        "result_absent_counts_exact": result["candidate_absent_read_count"] == 4147 and result["candidate_absent_exact_catalog_count"] == 295 and result["candidate_absent_factor_green_count"] == 3852 and result["candidate_absent_amber_count"] == 161 and result["candidate_absent_stop_count"] == 258,
        "result_no_expansion": result["state_unsafe_stop_count"] == result["direct_pair_promotions"] == result["invisible_separators_invented"] == result["meaning_revisions"] == result["surface_predictions"] == result["occurrence_predictions"] == result["new_pages"] == 0,
        "cli_green_example": json.loads(subprocess.run([
            "python3", str(CERTIFIER_PATH), "--recipe", "CHD+Y+K"
        ], cwd=ROOT, check=True, capture_output=True, text=True).stdout)["primary_intake_route"] == "VISIBLE_SLOT_SEPARATED_CHAIN_GREEN",
        "cli_stop_example": json.loads(subprocess.run([
            "python3", str(CERTIFIER_PATH), "--recipe", "CHD+K"
        ], cwd=ROOT, check=True, capture_output=True, text=True).stdout)["primary_intake_route"] == "STOP_UNLICENSED_DIRECT_PAIR",
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
    (OUT / "gdt445_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
