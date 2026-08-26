#!/usr/bin/env python3
"""Validate GDT437's relation/argument order repair."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair"
OUT = BASE / "artifacts"
REGISTERS = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt437_12005_state_transition_matrix.tsv",
        OUT / "gdt437_245_baseline_collision_cells.tsv",
        OUT / "gdt437_49_transition_signatures.tsv",
        OUT / "gdt437_1176_pairwise_signature_audit.tsv",
        OUT / "gdt437_68_current_order_repairs.tsv",
        OUT / "gdt437_59_current_statement_order_repairs.tsv",
        OUT / "gdt437_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    matrix = read_tsv(tracked[0])
    collisions = read_tsv(tracked[1])
    signatures = read_tsv(tracked[2])
    pairs = read_tsv(tracked[3])
    current = read_tsv(tracked[4])
    statements = read_tsv(tracked[5])
    result = json.loads(tracked[6].read_text(encoding="utf-8"))

    cards = {row["component_recipe"] for row in matrix}
    states = {(row["incoming_action"], row["incoming_argument"]) for row in matrix}
    card_counts = Counter(row["component_recipe"] for row in matrix)
    baseline_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    repaired_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for row in matrix:
        common = (
            row["register"], row["incoming_action"], row["incoming_argument"],
            row["outgoing_action"], row["outgoing_argument"],
        )
        baseline_groups[common + (row["baseline_clause_de"],)].append(row["component_recipe"])
        repaired_groups[common + (row["order_safe_clause_de"],)].append(row["component_recipe"])
    baseline_collisions = [recipes for recipes in baseline_groups.values() if len(recipes) > 1]
    repaired_collisions = [recipes for recipes in repaired_groups.values() if len(recipes) > 1]
    universal_baseline = [row for row in pairs if row["baseline_universal_collision"] == "YES"]
    universal_repaired = [row for row in pairs if row["order_safe_universal_collision"] == "YES"]
    repaired_ids = {row["event_id"] for row in current}
    statement_ids = {event_id for row in statements for event_id in row["order_repaired_event_ids"].split("|")}
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "transition_rows_12005": len(matrix) == 12005,
        "transition_cells_unique": len({(row["component_recipe"], row["register"], row["incoming_action"], row["incoming_argument"]) for row in matrix}) == 12005,
        "main_cards_49": len(cards) == 49 and all(count == 245 for count in card_counts.values()),
        "reachable_states_49": len(states) == 49,
        "registers_five_exact": {row["register"] for row in matrix} == REGISTERS,
        "all_clauses_nonempty": all(row["baseline_clause_de"] and row["order_safe_clause_de"] for row in matrix),
        "baseline_collision_cells_245": len(baseline_collisions) == len(collisions) == 245,
        "baseline_collision_pair_exact": all(sorted(recipes) == ["AIR+Y", "Y+AIR"] for recipes in baseline_collisions) and all(row["colliding_recipes"] == "AIR+Y|Y+AIR" for row in collisions),
        "all_baseline_collisions_resolved": all(row["repair_status"] == "RESOLVED" and int(row["repaired_clause_count"]) == 2 for row in collisions),
        "repaired_collision_cells_zero": len(repaired_collisions) == 0,
        "signature_rows_49": len(signatures) == 49 and {row["component_recipe"] for row in signatures} == cards,
        "signature_hashes_unique": len({row["transition_signature_sha256"] for row in signatures}) == 49,
        "signature_cell_counts_245": all(int(row["transition_cell_count"]) == 245 and int(row["reachable_state_count"]) == 49 and int(row["register_count"]) == 5 for row in signatures),
        "pair_rows_1176": len(pairs) == 1176 and len({(row["left_recipe"], row["right_recipe"]) for row in pairs}) == 1176,
        "one_baseline_universal_pair": len(universal_baseline) == 1 and {universal_baseline[0]["left_recipe"], universal_baseline[0]["right_recipe"]} == {"AIR+Y", "Y+AIR"} and int(universal_baseline[0]["baseline_equal_transition_count"]) == 245,
        "no_order_safe_universal_pair": len(universal_repaired) == 0 and all(int(row["order_safe_equal_transition_count"]) == 0 for row in pairs),
        "current_event_repairs_68": len(current) == len(repaired_ids) == 68,
        "current_repairs_order_only": all(row["meaning_change"] == "NO__RELATION_ARGUMENT_ORDER_ONLY" and row["old_clause_de"] != row["order_safe_clause_de"] for row in current),
        "current_statement_repairs_59": len(statements) == 59 and len({row["global_statement_id"] for row in statements}) == 59,
        "statement_repairs_cover_events_exact": statement_ids == repaired_ids and sum(int(row["order_repaired_event_count"]) for row in statements) == 68,
        "statement_readings_changed": all(row["old_imperative_reading_de"] != row["order_safe_imperative_reading_de"] for row in statements),
        "result_status_exact": result["status"] == "RELATION_ARGUMENT_ORDER_COLLISION_REPAIRED",
        "result_counts_exact": result["reachable_state_count"] == result["main_future_card_count"] == 49 and result["register_count"] == 5 and result["transition_cell_count"] == 12005 and result["baseline_collision_cell_count"] == 245 and result["order_safe_collision_cell_count"] == 0 and result["unique_order_safe_transition_signature_count"] == 49,
        "result_current_repairs_exact": result["current_event_order_repair_count"] == 68 and result["current_statement_order_repair_count"] == 59,
        "result_pair_counts_exact": result["pairwise_comparison_count"] == 1176 and result["baseline_universal_pair_count"] == 1 and result["order_safe_universal_pair_count"] == 0,
        "no_meaning_surface_page_change": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        # A SHA-256 may naturally contain the hexadecimal substring ``f84``.
        # Reject only a folio-like token, not arbitrary hash bytes.
        "no_forbidden_page_in_outputs": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt437_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
