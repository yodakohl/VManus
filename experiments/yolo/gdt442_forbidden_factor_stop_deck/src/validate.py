#!/usr/bin/env python3
"""Validate GDT442's complete factor-stop deck."""

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
BASE = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck"
OUT = BASE / "artifacts"
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"
EXPLAINER = BASE / "src/explain_stop.py"
CANDIDATES = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4938_candidate_factor_gate.tsv"


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
        OUT / "gdt442_269_stop_candidate_audit.tsv",
        OUT / "gdt442_complete_201_factor_lattice.tsv",
        OUT / "gdt442_47_stop_rule_deck.tsv",
        OUT / "gdt442_47_stop_state_probes.tsv",
        OUT / "gdt442_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(
        ["python3", str(BASE / "src/run.py")], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    after = {path: path.read_bytes() for path in tracked}

    audit = read_tsv(tracked[0])
    lattice = read_tsv(tracked[1])
    deck = read_tsv(tracked[2])
    probes = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    candidates = read_tsv(CANDIDATES)
    stopped = [row for row in candidates if row["factor_gate_status"] == "STOP__UNLICENSED_FACTOR"]
    reader = load_module("gdt441_reader_for_gdt442_validation", READER_PATH)

    lattice_family = Counter(row["factor_family"] for row in lattice)
    lattice_status = Counter((row["factor_family"], row["factor_status"]) for row in lattice)
    deck_family = Counter(row["factor_family"] for row in deck)
    audit_family = Counter(row["stop_family"] for row in audit)
    audit_rule_count = Counter(row["blocked_rule_count"] for row in audit)
    stop_rules = {row["blocked_rule"] for row in deck}
    candidate_rules = {
        reason for row in audit for reason in row["blocked_rules"].split("|")
    }
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    direct_gate_matches = []
    for row in deck:
        gate = reader.gate_recipe(row["minimal_probe_recipe"], "NONE")
        direct_gate_matches.append(
            gate["factor_gate_status"] == "STOP__UNLICENSED_FACTOR"
            and row["blocked_rule"] in gate["blocked_factor_rules"].split("|")
        )
    red_explanation = json.loads(subprocess.check_output(
        ["python3", str(EXPLAINER), "--recipe", "A_ADDR+T+S+OR"],
        cwd=ROOT, text=True,
    ))
    green_explanation = json.loads(subprocess.check_output(
        ["python3", str(EXPLAINER), "--recipe", "AIIN+AIN+S+Y"],
        cwd=ROOT, text=True,
    ))

    checks = {
        "audit_269_unique": len(audit) == len({row["candidate_recipe"] for row in audit}) == 269,
        "audit_matches_gdt441_stops": {row["candidate_recipe"] for row in audit} == {row["candidate_recipe"] for row in stopped},
        "audit_status_263_absent_6_observed": Counter(row["current_status"] for row in audit) == {"ABSENT": 263, "OBSERVED": 6},
        "audit_families_217_52": audit_family == {"ADJACENT_ACTION_PAIR": 217, "CLOSE_CONTEXT": 52},
        "audit_reason_multiplicity_263_6": audit_rule_count == {"1": 263, "2": 6},
        "audit_no_auto_repair": all(row["automatic_repair"] == "NONE" for row in audit),
        "lattice_201_unique": len(lattice) == len({(row["factor_family"], row["factor_rule"]) for row in lattice}) == 201,
        "lattice_family_counts_81_110_10": lattice_family == {"ADJACENT_ACTION_PAIR": 81, "FOCUS_HEAD_EDGE": 110, "CLOSE_TARGET": 9, "CLOSE_CONTEXT": 1},
        "lattice_pair_counts_31_6_44": {
            key[1]: value for key, value in lattice_status.items() if key[0] == "ADJACENT_ACTION_PAIR"
        } == {"GREEN_CROSS_PAGE": 31, "AMBER_LOCAL_APPENDIX": 6, "STOP_UNLICENSED": 44},
        "lattice_focus_counts_104_4_2": {
            key[1]: value for key, value in lattice_status.items() if key[0] == "FOCUS_HEAD_EDGE"
        } == {"GREEN_CROSS_PAGE_OR_OLD_R_TOPOLOGY": 104, "AMBER_LOCAL_APPENDIX": 4, "STOP_UNLICENSED": 2},
        "lattice_close_counts_9_1": lattice_status[("CLOSE_TARGET", "GREEN_CROSS_PAGE")] == 9 and lattice_status[("CLOSE_CONTEXT", "STOP_MISSING_CONTEXT")] == 1,
        "deck_47_unique": len(deck) == len(stop_rules) == len({row["stop_rule_id"] for row in deck}) == 47,
        "deck_family_counts_44_2_1": deck_family == {"ADJACENT_ACTION_PAIR": 44, "FOCUS_HEAD_EDGE": 2, "CLOSE_CONTEXT": 1},
        "deck_rules_match_lattice_stops": stop_rules == {
            row["factor_rule"] for row in lattice if row["factor_status"].startswith("STOP")
        },
        "candidate_rules_subset_deck": candidate_rules <= stop_rules,
        "candidate_rule_count_24": len(candidate_rules) == 24,
        "deck_queue_presence_24_23": Counter(row["present_in_269_candidate_queue"] for row in deck) == {"YES": 24, "NO": 23},
        "deck_candidate_count_sum_275": sum(int(row["candidate_stop_row_count"]) for row in deck) == 275,
        "deck_no_meaning_or_auto_repair": all(row["meaning_change_allowed"] == "NO" and row["automatic_repair"] == "NONE" for row in deck),
        "direct_gate_reproduces_all_47_stops": all(direct_gate_matches),
        "explainer_names_red_pair": red_explanation["factor_gate_status"] == "STOP__UNLICENSED_FACTOR" and red_explanation["blocked_rule_explanations"][0]["blocked_rule"] == "PAIR:T>S",
        "explainer_passes_green_recipe": green_explanation["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" and green_explanation["blocked_rule_explanations"] == [],
        "probes_47_unique": len(probes) == len({row["stop_rule_id"] for row in probes}) == 47,
        "probe_ids_match_deck": {row["stop_rule_id"] for row in probes} == {row["stop_rule_id"] for row in deck},
        "all_probes_stop": all(row["probe_reader_status"] == "STOP__UNLICENSED_FACTOR" for row in probes),
        "all_probe_rules_exact": all(row["blocked_rule"] in row["probe_blocked_factor_rules"].split("|") for row in probes),
        "all_stops_preserve_state": all(row["state_preserved"] == "YES" for row in probes),
        "all_recoveries_succeed": all(row["recovery_succeeds"] == "YES" and not row["recovery_reader_status"].startswith("STOP") for row in probes),
        "result_status_exact": result["status"] == "COMPLETE_47_RULE_STOP_DECK__ALL_STOPS_STATE_SAFE",
        "result_candidate_counts_exact": result["candidate_stop_row_count"] == 269 and result["candidate_absent_count"] == 263 and result["candidate_observed_neutral_context_stop_count"] == 6 and result["candidate_rows_with_two_pair_blocks"] == 6,
        "result_lattice_deck_exact": result["factor_lattice_row_count"] == 201 and result["stop_rule_count"] == 47 and result["unlicensed_action_pair_count"] == 44 and result["unlicensed_focus_edge_count"] == 2 and result["missing_close_context_count"] == 1,
        "result_probe_counts_exact": result["stop_probe_count"] == result["state_preserved_count"] == result["recovery_succeeds_count"] == 47,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
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
    (OUT / "gdt442_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
