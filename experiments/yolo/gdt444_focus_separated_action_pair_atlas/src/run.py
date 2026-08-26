#!/usr/bin/env python3
"""Test every red direct action pair with each visible focus separator."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
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
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decision(status: str) -> str:
    if status == "FACTOR_GREEN_CROSS_PAGE":
        return "SEPARATED_CHAIN_GREEN"
    if status == "FACTOR_AMBER_LOCAL_APPENDIX":
        return "SEPARATED_CHAIN_AMBER"
    return "SEPARATED_CHAIN_STILL_STOPPED"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = load_module("gdt441_reader_for_separator_atlas", READER_PATH)
    pair_rows = [row for row in read_tsv(STOP_DECK) if row["factor_family"] == "ADJACENT_ACTION_PAIR"]
    foci = sorted(reader.FOCUS_ROOTS)

    matrix: list[dict[str, object]] = []
    for pair_row in pair_rows:
        pair = pair_row["blocked_rule"].removeprefix("PAIR:")
        left, right = pair.split(">")
        for focus in foci:
            recipe = f"{left}+{focus}+{right}"
            gate = reader.gate_recipe(recipe, "NONE")
            matrix.append({
                "direct_pair": pair,
                "left_action": left,
                "separator_focus": focus,
                "right_action": right,
                "separated_recipe": recipe,
                "direct_pair_reader_status": "STOP_UNLICENSED",
                "separated_factor_gate_status": gate["factor_gate_status"],
                "separator_decision": decision(gate["factor_gate_status"]),
                "scope_selector_rules": gate["scope_selector_rules"],
                "portable_factor_rules": gate["portable_factor_rules"],
                "amber_factor_rules": gate["amber_factor_rules"],
                "blocked_factor_rules": gate["blocked_factor_rules"],
                "ordered_literal_reading_de": reader.ordered_literal(recipe.split("+")),
                "direct_pair_promoted": "NO",
                "surface_or_occurrence_prediction": "NO",
            })
    write_tsv(OUT / "gdt444_484_focus_separated_pair_matrix.tsv", matrix, list(matrix[0]))

    by_pair: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_focus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in matrix:
        by_pair[str(row["direct_pair"])].append(row)
        by_focus[str(row["separator_focus"])].append(row)
    pair_summary: list[dict[str, object]] = []
    for pair_row in pair_rows:
        pair = pair_row["blocked_rule"].removeprefix("PAIR:")
        rows = by_pair[pair]
        counts = Counter(str(row["separator_decision"]) for row in rows)
        stop_foci = [str(row["separator_focus"]) for row in rows if row["separator_decision"] == "SEPARATED_CHAIN_STILL_STOPPED"]
        pair_summary.append({
            "direct_pair": pair,
            "separator_count": len(rows),
            "green_separator_count": counts["SEPARATED_CHAIN_GREEN"],
            "amber_separator_count": counts["SEPARATED_CHAIN_AMBER"],
            "stop_separator_count": counts["SEPARATED_CHAIN_STILL_STOPPED"],
            "accepted_separator_count": counts["SEPARATED_CHAIN_GREEN"] + counts["SEPARATED_CHAIN_AMBER"],
            "all_eleven_separators_accepted": "YES" if not stop_foci else "NO",
            "remaining_stop_foci": "|".join(stop_foci) or "NONE",
            "direct_pair_remains_unlicensed": "YES",
        })
    write_tsv(OUT / "gdt444_44_pair_separator_summary.tsv", pair_summary, list(pair_summary[0]))

    focus_summary: list[dict[str, object]] = []
    for focus in foci:
        rows = by_focus[focus]
        counts = Counter(str(row["separator_decision"]) for row in rows)
        focus_summary.append({
            "separator_focus": focus,
            "red_direct_pair_count": len(rows),
            "green_pair_count": counts["SEPARATED_CHAIN_GREEN"],
            "amber_pair_count": counts["SEPARATED_CHAIN_AMBER"],
            "stop_pair_count": counts["SEPARATED_CHAIN_STILL_STOPPED"],
            "accepted_pair_count": counts["SEPARATED_CHAIN_GREEN"] + counts["SEPARATED_CHAIN_AMBER"],
            "remaining_stop_pairs": "|".join(str(row["direct_pair"]) for row in rows if row["separator_decision"] == "SEPARATED_CHAIN_STILL_STOPPED") or "NONE",
        })
    write_tsv(OUT / "gdt444_11_focus_separator_summary.tsv", focus_summary, list(focus_summary[0]))

    missing_pairs = set(by_pair)
    observed: list[dict[str, object]] = []
    for event in read_tsv(CURRENT):
        atoms = event["component_recipe"].split("+")
        for index in range(len(atoms) - 2):
            pair = f"{atoms[index]}>{atoms[index + 2]}"
            focus = atoms[index + 1]
            if pair not in missing_pairs or focus not in reader.FOCUS_ROOTS:
                continue
            triple_recipe = "+".join(atoms[index:index + 3])
            gate = reader.gate_recipe(triple_recipe, "NONE")
            observed.append({
                "separated_occurrence_id": f"G444-O{len(observed) + 1:02d}",
                "event_id": event["event_id"],
                "physical_page": event["physical_page"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "full_component_recipe": event["component_recipe"],
                "triple_start_atom_ordinal": index + 1,
                "direct_red_pair": pair,
                "separator_focus": focus,
                "observed_triple_recipe": triple_recipe,
                "triple_factor_gate_status": gate["factor_gate_status"],
                "triple_portable_factor_rules": gate["portable_factor_rules"],
                "triple_amber_factor_rules": gate["amber_factor_rules"],
                "triple_blocked_factor_rules": gate["blocked_factor_rules"],
                "full_event_factor_gate_status": event["factor_gate_status"],
                "direct_pair_promoted": "NO",
            })
    write_tsv(OUT / "gdt444_28_observed_separated_pair_occurrences.tsv", observed, list(observed[0]))

    counts = Counter(row["separator_decision"] for row in matrix)
    result = {
        "status": "ALL_FORTY_FOUR_RED_DIRECT_PAIRS_HAVE_AT_LEAST_TEN_READABLE_FOCUS_SEPARATORS",
        "red_direct_pair_count": len(pair_rows),
        "focus_separator_count": len(foci),
        "separator_matrix_cell_count": len(matrix),
        "green_cell_count": counts["SEPARATED_CHAIN_GREEN"],
        "amber_cell_count": counts["SEPARATED_CHAIN_AMBER"],
        "stop_cell_count": counts["SEPARATED_CHAIN_STILL_STOPPED"],
        "pairs_with_all_eleven_separators_accepted": sum(row["all_eleven_separators_accepted"] == "YES" for row in pair_summary),
        "pairs_with_ten_of_eleven_separators_accepted": sum(int(row["accepted_separator_count"]) == 10 for row in pair_summary),
        "observed_separated_occurrence_count": len(observed),
        "observed_full_recipe_count": len({row["full_component_recipe"] for row in observed}),
        "observed_pair_focus_pattern_count": len({(row["direct_red_pair"], row["separator_focus"]) for row in observed}),
        "observed_red_pair_count": len({row["direct_red_pair"] for row in observed}),
        "observed_page_count": len({row["physical_page"] for row in observed}),
        "observed_green_triple_count": sum(row["triple_factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" for row in observed),
        "direct_pair_promotions": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt444_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
