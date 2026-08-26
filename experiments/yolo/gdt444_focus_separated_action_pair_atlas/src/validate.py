#!/usr/bin/env python3
"""Validate GDT444's focus-separated action-pair atlas."""

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
BASE = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas"
OUT = BASE / "artifacts"
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"
STOP_DECK = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck/artifacts/gdt442_47_stop_rule_deck.tsv"


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
        OUT / "gdt444_484_focus_separated_pair_matrix.tsv",
        OUT / "gdt444_44_pair_separator_summary.tsv",
        OUT / "gdt444_11_focus_separator_summary.tsv",
        OUT / "gdt444_28_observed_separated_pair_occurrences.tsv",
        OUT / "gdt444_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    matrix = read_tsv(tracked[0])
    pairs = read_tsv(tracked[1])
    foci = read_tsv(tracked[2])
    observed = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    source_pairs = [row for row in read_tsv(STOP_DECK) if row["factor_family"] == "ADJACENT_ACTION_PAIR"]
    reader = load_module("gdt441_reader_for_gdt444_validation", READER_PATH)

    matrix_keys = {(row["direct_pair"], row["separator_focus"]) for row in matrix}
    status_counts = Counter(row["separator_decision"] for row in matrix)
    stop_rows = [row for row in matrix if row["separator_decision"] == "SEPARATED_CHAIN_STILL_STOPPED"]
    amber_rows = [row for row in matrix if row["separator_decision"] == "SEPARATED_CHAIN_AMBER"]
    focus_counts = {
        row["separator_focus"]: (int(row["green_pair_count"]), int(row["amber_pair_count"]), int(row["stop_pair_count"]))
        for row in foci
    }
    direct_checks = []
    for row in matrix:
        left, right = row["direct_pair"].split(">")
        direct = reader.gate_recipe(f"{left}+{right}", "NONE")
        direct_checks.append(direct["factor_gate_status"] == "STOP__UNLICENSED_FACTOR" and f"PAIR:{row['direct_pair']}" in direct["blocked_factor_rules"].split("|"))
    separated_checks = []
    for row in matrix:
        separated = reader.gate_recipe(row["separated_recipe"], "NONE")
        separated_checks.append(
            separated["factor_gate_status"] == row["separated_factor_gate_status"]
            and all(separated[field] == row[field] for field in (
                "scope_selector_rules", "portable_factor_rules", "amber_factor_rules", "blocked_factor_rules"
            ))
        )

    expected_stop = {
        (pair, "EEE", f"FOCUS:{pair.split('>')[0]}<-EEE")
        for pair in {row["direct_pair"] for row in matrix}
        if pair.startswith("CHD>") or pair.startswith("R>")
    }
    expected_amber = {
        *((pair, "EE", "FOCUS:R<-EE") for pair in {row["direct_pair"] for row in matrix} if pair.startswith("R>")),
        *((pair, "EEE", "FOCUS:S<-EEE") for pair in {row["direct_pair"] for row in matrix} if pair.startswith("S>")),
        ("R>R", "AIR", "FOCUS:R<-AIR"),
    }
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    checks = {
        "source_44_pairs_unique": len(source_pairs) == len({row["blocked_rule"] for row in source_pairs}) == 44,
        "matrix_484_unique": len(matrix) == len(matrix_keys) == 484,
        "matrix_pairs_match_source": {row["direct_pair"] for row in matrix} == {row["blocked_rule"].removeprefix("PAIR:") for row in source_pairs},
        "matrix_eleven_foci": {row["separator_focus"] for row in matrix} == reader.FOCUS_ROOTS,
        "matrix_counts_460_11_13": status_counts == {"SEPARATED_CHAIN_GREEN": 460, "SEPARATED_CHAIN_AMBER": 11, "SEPARATED_CHAIN_STILL_STOPPED": 13},
        "all_direct_pairs_still_stop": all(direct_checks),
        "all_separated_cells_recompute": all(separated_checks),
        "no_direct_pair_promoted": all(row["direct_pair_promoted"] == "NO" for row in matrix),
        "matrix_no_prediction": all(row["surface_or_occurrence_prediction"] == "NO" for row in matrix),
        "stop_cells_exact_grade_three": {(row["direct_pair"], row["separator_focus"], row["blocked_factor_rules"]) for row in stop_rows} == expected_stop,
        "amber_cells_exact": {(row["direct_pair"], row["separator_focus"], row["amber_factor_rules"]) for row in amber_rows} == expected_amber,
        "pair_summary_44_unique": len(pairs) == len({row["direct_pair"] for row in pairs}) == 44,
        "pair_summary_eleven_each": all(int(row["separator_count"]) == 11 for row in pairs),
        "pair_summary_31_all_13_ten": Counter((row["all_eleven_separators_accepted"], row["accepted_separator_count"]) for row in pairs) == {("YES", "11"): 31, ("NO", "10"): 13},
        "all_pairs_have_at_least_ten": all(int(row["accepted_separator_count"]) >= 10 for row in pairs),
        "pair_summary_keeps_direct_red": all(row["direct_pair_remains_unlicensed"] == "YES" for row in pairs),
        "focus_summary_11_unique": len(foci) == len(focus_counts) == 11,
        "focus_air_43_1_0": focus_counts["AIR"] == (43, 1, 0),
        "focus_ee_39_5_0": focus_counts["EE"] == (39, 5, 0),
        "focus_eee_26_5_13": focus_counts["EEE"] == (26, 5, 13),
        "other_eight_foci_all_green": all(focus_counts[focus] == (44, 0, 0) for focus in reader.FOCUS_ROOTS - {"AIR", "EE", "EEE"}),
        "observed_28_unique_positions": len(observed) == len({(row["event_id"], row["triple_start_atom_ordinal"]) for row in observed}) == 28,
        "observed_counts_27_18_16_13": len({row["full_component_recipe"] for row in observed}) == 27 and len({(row["direct_red_pair"], row["separator_focus"]) for row in observed}) == 18 and len({row["direct_red_pair"] for row in observed}) == 16 and len({row["physical_page"] for row in observed}) == 13,
        "observed_all_triples_green": all(row["triple_factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" and row["triple_blocked_factor_rules"] == "NONE" for row in observed),
        "observed_never_promotes_direct": all(row["direct_pair_promoted"] == "NO" for row in observed),
        "result_status_exact": result["status"] == "ALL_FORTY_FOUR_RED_DIRECT_PAIRS_HAVE_AT_LEAST_TEN_READABLE_FOCUS_SEPARATORS",
        "result_matrix_exact": result["red_direct_pair_count"] == 44 and result["focus_separator_count"] == 11 and result["separator_matrix_cell_count"] == 484 and result["green_cell_count"] == 460 and result["amber_cell_count"] == 11 and result["stop_cell_count"] == 13,
        "result_pair_exact": result["pairs_with_all_eleven_separators_accepted"] == 31 and result["pairs_with_ten_of_eleven_separators_accepted"] == 13,
        "result_observed_exact": result["observed_separated_occurrence_count"] == 28 and result["observed_full_recipe_count"] == 27 and result["observed_pair_focus_pattern_count"] == 18 and result["observed_red_pair_count"] == 16 and result["observed_page_count"] == 13 and result["observed_green_triple_count"] == 28,
        "result_no_expansion": result["direct_pair_promotions"] == result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt444_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
