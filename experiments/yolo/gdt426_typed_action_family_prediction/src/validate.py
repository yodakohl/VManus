#!/usr/bin/env python3
"""Validate GDT426 typed action-family predictions."""

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
BASE = ROOT / "experiments/yolo/gdt426_typed_action_family_prediction"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt426_9_typed_local_predictions.tsv",
        OUT / "gdt426_16_action_class_transition_atlas.tsv",
        OUT / "gdt426_12_action_class_focus_family_atlas.tsv",
        OUT / "gdt426_81_exact_action_pair_status.tsv",
        OUT / "TYPED_LOCAL_PREDICTION_CARD.md",
        OUT / "gdt426_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}
    predictions = read_tsv("gdt426_9_typed_local_predictions.tsv")
    transitions = read_tsv("gdt426_16_action_class_transition_atlas.tsv")
    focus = read_tsv("gdt426_12_action_class_focus_family_atlas.tsv")
    pairs = read_tsv("gdt426_81_exact_action_pair_status.tsv")
    result = json.loads((OUT / "gdt426_result.json").read_text(encoding="utf-8"))

    checks = {
        "predictions_9": len(predictions) == 9,
        "prediction_ids_unique": len({row["rule_id"] for row in predictions}) == 9,
        "all_predictions_amber": all(row["prediction_status"].startswith("AMBER") for row in predictions),
        "hard_local_zero": sum(row["prediction_status"] == "HARD_LOCAL_UNEXPLAINED" for row in predictions) == 0,
        "exact_pair_with_slots_2": sum(row["prediction_status"] == "AMBER_EXACT_ORDERED_PAIR_WITH_INTERVENING_SLOTS" for row in predictions) == 2,
        "action_class_transition_4": sum(row["prediction_status"] == "AMBER_ACTION_CLASS_TRANSITION" for row in predictions) == 4,
        "head_focus_rectangle_2": sum(row["prediction_status"] == "AMBER_HEAD_FOCUS_FAMILY_RECTANGLE" for row in predictions) == 2,
        "class_focus_family_1": sum(row["prediction_status"] == "AMBER_ACTION_CLASS_FOCUS_FAMILY" for row in predictions) == 1,
        "class_transition_cells_16": len(transitions) == 16,
        "all_class_transitions_attested": all(row["transition_status"] == "ATTESTED" and int(row["event_count"]) > 0 for row in transitions),
        "class_focus_cells_12": len(focus) == 12,
        "all_class_focus_cells_attested": all(row["edge_status"] == "ATTESTED" and int(row["event_count"]) > 0 for row in focus),
        "exact_pair_cells_81": len(pairs) == 81,
        "exact_pair_multi_page_49": sum(row["pair_status"] == "ATTESTED_MULTI_PAGE" for row in pairs) == 49,
        "exact_pair_one_page_15": sum(row["pair_status"] == "ATTESTED_ONE_PAGE" for row in pairs) == 15,
        "exact_pair_unattested_class_old_17": sum(row["pair_status"] == "UNATTESTED_EXACT_PAIR__CLASS_TRANSITION_OLD" for row in pairs) == 17,
        "no_empty_class_transition_pair": all(row["pair_status"] != "UNATTESTED_EXACT_PAIR__CLASS_TRANSITION_EMPTY" for row in pairs),
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_roots": result["new_roots"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt426_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
