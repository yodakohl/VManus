#!/usr/bin/env python3
"""Validate GDT421 ordered action-pair slot licenses."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt421_356_two_head_recipe_inventory.tsv",
        OUT / "gdt421_81_ordered_pair_profiles.tsv",
        OUT / "gdt421_3240_pair_slot_atlas.tsv",
        OUT / "gdt421_45_pair_directionality.tsv",
        OUT / "gdt421_31_multi_head_prediction_gates.tsv",
        OUT / "TWENTY_ORDERED_ACTION_PAIR_CARDS.md",
        OUT / "gdt421_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    recipes = read_tsv("gdt421_356_two_head_recipe_inventory.tsv")
    profiles = read_tsv("gdt421_81_ordered_pair_profiles.tsv")
    atlas = read_tsv("gdt421_3240_pair_slot_atlas.tsv")
    directions = read_tsv("gdt421_45_pair_directionality.tsv")
    gates = read_tsv("gdt421_31_multi_head_prediction_gates.tsv")
    result = json.loads((OUT / "gdt421_result.json").read_text(encoding="utf-8"))

    gate_counts = {decision: sum(row["gate_decision"] == decision for row in gates) for decision in {row["gate_decision"] for row in gates}}
    checks = {
        "two_head_recipes_356": len(recipes) == 356,
        "two_head_events_608": sum(int(row["event_count"]) for row in recipes) == 608,
        "clean_pair_recipes_315": sum(row["clean_pair_slot_recipe"] == "YES" for row in recipes) == 315,
        "clean_pair_events_563": sum(int(row["event_count"]) for row in recipes if row["clean_pair_slot_recipe"] == "YES") == 563,
        "profiles_81": len(profiles) == 81,
        "profile_keys_unique": len({row["ordered_pair"] for row in profiles}) == 81,
        "attested_pairs_54": sum(row["status"] == "PAIR_ATTESTED" for row in profiles) == 54,
        "atlas_cells_3240": len(atlas) == 3240,
        "atlas_keys_unique": len({(row["ordered_pair"], row["grade_slot"], row["argument_slot"], row["endpoint_slot"]) for row in atlas}) == 3240,
        "attested_slot_cells_170": sum(row["status"].startswith("ATTESTED") for row in atlas) == 170,
        "multi_register_slot_cells_59": sum(row["status"] == "ATTESTED_MULTI_REGISTER" for row in atlas) == 59,
        "directions_45": len(directions) == 45,
        "direction_distribution": {verdict: sum(row["direction_verdict"] == verdict for row in directions) for verdict in {row["direction_verdict"] for row in directions}} == {
            "DIRECTIONAL": 13,
            "BALANCED": 7,
            "REVERSE_ONLY": 7,
            "BOTH_ABSENT": 6,
            "SELF_ABSENT": 5,
            "SELF_ATTESTED": 4,
            "FORWARD_ONLY": 3,
        },
        "prediction_gates_31": len(gates) == 31,
        "prediction_gate_distribution": gate_counts == {
            "BLOCKED__DO_NOT_PREDICT_AS_REGULAR_PAIR": 19,
            "OPEN_PAIR_CONDITIONAL_READING": 6,
            "SKELETON_ALREADY_ATTESTED_LOCAL": 4,
            "SKELETON_ALREADY_ATTESTED_MULTI_REGISTER": 2,
        },
        "all_prediction_pairs_two_heads": all(len(row["ordered_pair"].split("+")) == 2 for row in gates),
        "ch_k_before_ch_t": int(next(row for row in profiles if row["ordered_pair"] == "CH+K")["event_count"]) > int(next(row for row in profiles if row["ordered_pair"] == "CH+T")["event_count"]),
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_pages": result["new_pages"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt421_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
