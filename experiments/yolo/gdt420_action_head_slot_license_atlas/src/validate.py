#!/usr/bin/env python3
"""Validate GDT420 action-slot atlas."""

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
BASE = ROOT / "experiments/yolo/gdt420_action_head_slot_license_atlas"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt420_547_single_head_recipe_inventory.tsv",
        OUT / "gdt420_360_action_slot_atlas.tsv",
        OUT / "gdt420_9_action_head_profiles.tsv",
        OUT / "gdt420_52_gdt419_prediction_gates.tsv",
        OUT / "NINE_ACTION_HEAD_CARDS.md",
        OUT / "gdt420_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    recipes = read_tsv("gdt420_547_single_head_recipe_inventory.tsv")
    atlas = read_tsv("gdt420_360_action_slot_atlas.tsv")
    profiles = read_tsv("gdt420_9_action_head_profiles.tsv")
    gates = read_tsv("gdt420_52_gdt419_prediction_gates.tsv")
    result = json.loads((OUT / "gdt420_result.json").read_text(encoding="utf-8"))
    statuses = {row["status"] for row in atlas}

    checks = {
        "single_head_recipes_547": len(recipes) == 547,
        "single_head_events_2184": sum(int(row["event_count"]) for row in recipes) == 2184,
        "clean_recipes_495": sum(row["clean_single_slot_recipe"] == "YES" for row in recipes) == 495,
        "clean_events_2099": sum(int(row["event_count"]) for row in recipes if row["clean_single_slot_recipe"] == "YES") == 2099,
        "atlas_cells_360": len(atlas) == 360,
        "atlas_keys_unique": len({(row["action_head"], row["grade_slot"], row["argument_slot"], row["endpoint_slot"]) for row in atlas}) == 360,
        "profiles_9": len(profiles) == 9,
        "prediction_gates_52": len(gates) == 52,
        "heads_exact": {row["action_head"] for row in profiles} == {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"},
        "statuses_exact": statuses == {"ATTESTED_MULTI_REGISTER", "ATTESTED_LOCAL", "OPEN_COMBINATION_GAP", "BLOCKED_BY_HEAD_INVENTORY"},
        "attested_cells_108": sum(row["status"].startswith("ATTESTED") for row in atlas) == 108,
        "multi_cells_80": sum(row["status"] == "ATTESTED_MULTI_REGISTER" for row in atlas) == 80,
        "local_cells_28": sum(row["status"] == "ATTESTED_LOCAL" for row in atlas) == 28,
        "open_gaps_145": sum(row["status"] == "OPEN_COMBINATION_GAP" for row in atlas) == 145,
        "blocked_cells_107": sum(row["status"] == "BLOCKED_BY_HEAD_INVENTORY" for row in atlas) == 107,
        "prediction_gate_distribution": {decision: sum(row["gate_decision"] == decision for row in gates) for decision in {row["gate_decision"] for row in gates}} == {
            "MULTI_HEAD_REQUIRES_SEPARATE_LICENSE": 31,
            "OPEN_GAP_CONDITIONAL_READING": 8,
            "BLOCKED__DO_NOT_PREDICT_AS_REGULAR_FORM": 6,
            "SKELETON_ALREADY_ATTESTED_LOCAL": 4,
            "SKELETON_ALREADY_ATTESTED_MULTI_REGISTER": 3,
        },
        "chd_no_grade": next(row for row in profiles if row["action_head"] == "CHD")["grade_license"] == "NO_GRADE_SLOT",
        "r_no_grade_or_close": next(row for row in profiles if row["action_head"] == "R")["grade_license"] == "NO_GRADE_SLOT" and next(row for row in profiles if row["action_head"] == "R")["endpoint_license"] == "NO_CLOSE_SLOT",
        "attested_cells_have_recipes": all(int(row["exact_recipe_type_count"]) > 0 for row in atlas if row["status"].startswith("ATTESTED")),
        "empty_cells_have_no_recipes": all(int(row["exact_recipe_type_count"]) == 0 for row in atlas if not row["status"].startswith("ATTESTED")),
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
    (OUT / "gdt420_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
