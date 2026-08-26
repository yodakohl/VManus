#!/usr/bin/env python3
"""Validate GDT427's specificity-repaired typed prediction gate."""

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
BASE = ROOT / "experiments/yolo/gdt427_typed_prediction_specificity_repair"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt427_7_model_specificity_comparison.tsv",
        OUT / "gdt427_15_singleton_pair_leaveout.tsv",
        OUT / "gdt427_17_absent_pair_negative_controls.tsv",
        OUT / "gdt427_9_local_rule_reclassification.tsv",
        OUT / "gdt427_25_selected_transition_atlas.tsv",
        OUT / "SELECTED_FIVE_CLASS_GATE.md",
        OUT / "gdt427_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(
        ["python3", str(BASE / "src/run.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after = {path: path.read_bytes() for path in tracked}

    models = read_tsv("gdt427_7_model_specificity_comparison.tsv")
    singleton = read_tsv("gdt427_15_singleton_pair_leaveout.tsv")
    absent = read_tsv("gdt427_17_absent_pair_negative_controls.tsv")
    local = read_tsv("gdt427_9_local_rule_reclassification.tsv")
    transitions = read_tsv("gdt427_25_selected_transition_atlas.tsv")
    result = json.loads((OUT / "gdt427_result.json").read_text(encoding="utf-8"))
    selected = [row for row in models if row["selection"] == "SELECTED"]
    red_ids = {
        row["rule_id"]
        for row in local
        if row["specificity_repaired_status"].startswith("RED")
    }

    checks = {
        "models_7": len(models) == 7,
        "one_selected_model": len(selected) == 1,
        "selected_model_id": bool(selected) and selected[0]["model_id"] == "M5_SPLIT_CONTROL_SELECTED",
        "selected_classes_5": bool(selected) and selected[0]["class_count"] == "5",
        "selected_transitions_22_of_25": bool(selected) and selected[0]["filled_transition_count"] == "22" and selected[0]["possible_transition_count"] == "25",
        "selected_singleton_tp_12_fn_3": bool(selected) and selected[0]["singleton_pair_true_positive"] == "12" and selected[0]["singleton_pair_false_negative"] == "3",
        "selected_absent_fp_10_tn_7": bool(selected) and selected[0]["absent_pair_false_positive"] == "10" and selected[0]["absent_pair_true_negative"] == "7",
        "selected_balanced_accuracy": bool(selected) and selected[0]["balanced_accuracy"] == "0.605882",
        "singleton_rows_15": len(singleton) == 15,
        "singleton_amber_12_red_3": sum(row["prediction"] == "AMBER_PREDICTED" for row in singleton) == 12 and sum(row["prediction"] == "RED_LOCAL" for row in singleton) == 3,
        "absent_rows_17": len(absent) == 17,
        "absent_false_amber_10_true_red_7": sum(row["negative_control_result"] == "FALSE_AMBER_ALLOWED" for row in absent) == 10 and sum(row["negative_control_result"] == "TRUE_RED_BLOCKED" for row in absent) == 7,
        "local_rows_9": len(local) == 9,
        "local_amber_7_red_2": sum(row["specificity_repaired_status"].startswith("AMBER") for row in local) == 7 and len(red_ids) == 2,
        "local_red_ids_exact": red_ids == {"PAIR:R>T", "FOCUS:R<-EE"},
        "transition_rows_25": len(transitions) == 25,
        "transition_attested_22_empty_3": sum(row["transition_status"] == "ATTESTED" for row in transitions) == 22 and sum(row["transition_status"] == "EMPTY_RED" for row in transitions) == 3,
        "result_status": result["status"] == "FIVE_CLASS_SPECIFICITY_GATE_SELECTED__SEVEN_AMBER_TWO_LOCAL",
        "no_new_roots": result["new_roots"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt427_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
