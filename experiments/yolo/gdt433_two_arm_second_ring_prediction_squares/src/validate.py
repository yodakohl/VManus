#!/usr/bin/env python3
"""Validate GDT433's bounded two-arm second-ring prediction squares."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt433_two_arm_second_ring_prediction_squares"
OUT = BASE / "artifacts"
STRONG = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_47_strong_prediction_phrasebook.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def difference_count(left: str, right: str) -> int:
    left_atoms = left.split("+")
    right_atoms = right.split("+")
    return sum(a != b for a, b in zip(left_atoms, right_atoms)) if len(left_atoms) == len(right_atoms) else 99


def main() -> int:
    tracked = [
        OUT / "gdt433_21_two_arm_squares.tsv",
        OUT / "gdt433_14_second_ring_targets.tsv",
        OUT / "gdt433_10_new_second_ring_register_cards.tsv",
        OUT / "TWO_SECOND_RING_AMBER_CARDS.md",
        OUT / "gdt433_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}
    squares = read_tsv(tracked[0])
    targets = read_tsv(tracked[1])
    registers = read_tsv(tracked[2])
    strong = {row["candidate_recipe"] for row in read_tsv(STRONG)}
    observed = {row["component_recipe"] for row in read_tsv(CLAUSES)}
    result = json.loads((OUT / "gdt433_result.json").read_text(encoding="utf-8"))
    selected = {row["target_recipe"] for row in targets if row["decision"] == "SECOND_RING_AMBER_NEW"}
    target_square_counts = Counter(row["target_recipe"] for row in squares)
    target_base_counts = {target: len({row["observed_base_recipe"] for row in squares if row["target_recipe"] == target}) for target in target_square_counts}
    target_arm_counts = {target: len({value for row in squares if row["target_recipe"] == target for value in (row["strong_arm_a"], row["strong_arm_b"])}) for target in target_square_counts}
    register_counts = Counter(row["target_recipe"] for row in registers)
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "square_rows_21": len(squares) == 21,
        "square_ids_unique": len({row["square_id"] for row in squares}) == 21,
        "target_rows_14": len(targets) == 14 and len({row["target_recipe"] for row in targets}) == 14,
        "square_targets_exact": {row["target_recipe"] for row in targets} == set(target_square_counts),
        "observed_bases_real": all(row["observed_base_recipe"] in observed for row in squares),
        "arms_all_strong": all(row["strong_arm_a"] in strong and row["strong_arm_b"] in strong for row in squares),
        "base_to_each_arm_one_change": all(difference_count(row["observed_base_recipe"], row["strong_arm_a"]) == difference_count(row["observed_base_recipe"], row["strong_arm_b"]) == 1 for row in squares),
        "each_arm_to_target_one_change": all(difference_count(row["strong_arm_a"], row["target_recipe"]) == difference_count(row["strong_arm_b"], row["target_recipe"]) == 1 for row in squares),
        "base_to_target_two_changes": all(difference_count(row["observed_base_recipe"], row["target_recipe"]) == 2 for row in squares),
        "distinct_changed_positions": all(len(set(row["changed_positions"].split("|"))) == 2 for row in squares),
        "target_square_counts_exact": all(int(row["square_count"]) == target_square_counts[row["target_recipe"]] for row in targets),
        "target_base_counts_exact": all(int(row["distinct_observed_base_count"]) == target_base_counts[row["target_recipe"]] for row in targets),
        "target_arm_counts_exact": all(int(row["distinct_strong_arm_count"]) == target_arm_counts[row["target_recipe"]] for row in targets),
        "selected_two_exact": selected == {"AIR+AIN", "P+L"},
        "selected_outside_gdt430": all(row["target_current_status"] == "OUTSIDE_GDT430_293" for row in targets if row["target_recipe"] in selected),
        "selected_four_bases_four_arms": all(int(row["distinct_observed_base_count"]) == int(row["distinct_strong_arm_count"]) == int(row["square_count"]) == 4 for row in targets if row["target_recipe"] in selected),
        "single_square_outside_not_promoted": all(row["decision"] == "SINGLE_SQUARE_NOT_PROMOTED" for row in targets if row["target_recipe"] in {"AIN+AIIN", "AIN+OR"}),
        "air_or_reinforces_narrow": next(row for row in targets if row["target_recipe"] == "AIR+OR")["decision"] == "SECOND_RING_REINFORCES_EXISTING_NARROW",
        "register_rows_10": len(registers) == 10,
        "five_registers_each_selected": all(register_counts[target] == 5 for target in selected),
        "register_names_exact": {row["register"] for row in registers} == {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"},
        "no_phrase_collision_with_gdt431": all(row["generic_phrase_collides_with_gdt431"] == "NO" for row in targets if row["target_recipe"] in selected) and all(row["collides_with_gdt431_in_register"] == "NO" for row in registers),
        "surface_rules_fixed": all(row["surface_rule"].startswith("DO_NOT_INVENT_SURFACE") for row in targets + registers),
        "result_status": result["status"] == "TWO_NEW_SECOND_RING_AMBER_CARDS_FROM_FOUR_BY_FOUR_SQUARES",
        "result_counts": result["two_arm_square_count"] == 21 and result["second_ring_target_count"] == 14 and result["selected_new_second_ring_card_count"] == 2 and result["register_reading_count"] == 10,
        "result_selected_exact": set(result["selected_new_second_ring_cards"]) == selected,
        "no_new_values_pages_surfaces": result["surface_predictions"] == result["new_component_values"] == result["new_pages"] == 0,
        "no_placeholder_language": all(term not in output_text.upper() for term in ("UNKNOWN", "EXEMPLAR_VALUE", "UNTRANSLATED")),
        "no_forbidden_page": "f84" not in output_text.lower(),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt433_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
