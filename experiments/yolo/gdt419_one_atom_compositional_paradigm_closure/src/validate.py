#!/usr/bin/env python3
"""Validate GDT419 outputs and deterministic reconstruction."""

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
BASE = ROOT / "experiments/yolo/gdt419_one_atom_compositional_paradigm_closure"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt419_199_attested_one_atom_neighbors.tsv",
        OUT / "gdt419_120_role_safe_paradigm_cells.tsv",
        OUT / "gdt419_52_unique_missing_predictions.tsv",
        OUT / "gdt419_7_anchor_paradigm_summary.tsv",
        OUT / "gdt419_6_change_family_summary.tsv",
        OUT / "TWENTY_MISSING_COMPOSITION_PREDICTIONS.md",
        OUT / "gdt419_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    neighbors = read_tsv("gdt419_199_attested_one_atom_neighbors.tsv")
    cells = read_tsv("gdt419_120_role_safe_paradigm_cells.tsv")
    missing = read_tsv("gdt419_52_unique_missing_predictions.tsv")
    summaries = read_tsv("gdt419_7_anchor_paradigm_summary.tsv")
    changes = read_tsv("gdt419_6_change_family_summary.tsv")
    result = json.loads((OUT / "gdt419_result.json").read_text(encoding="utf-8"))

    checks = {
        "anchors_7": len(summaries) == 7,
        "change_families_6": len(changes) == 6,
        "anchor_names_unique": len({row["anchor_recipe"] for row in summaries}) == 7,
        "neighbor_pairs_199": len(neighbors) == 199,
        "unique_neighbors_171": len({row["neighbor_recipe"] for row in neighbors}) == 171,
        "neighbor_edit_kinds_valid": {row["edit_kind"] for row in neighbors} <= {"SUBSTITUTE", "INSERT", "DELETE"},
        "all_neighbors_attested": all(int(row["neighbor_event_count"]) > 0 for row in neighbors),
        "paradigm_cells_120": len(cells) == 120,
        "attested_cells_55": sum(row["attested"] == "YES" for row in cells) == 55,
        "missing_cells_65": sum(row["attested"] == "NO" for row in cells) == 65,
        "grade_insertion_zero_of_six": next(row for row in changes if row["change_kind"] == "INSERT_GRADE")["attested_cell_count"] == "0" and next(row for row in changes if row["change_kind"] == "INSERT_GRADE")["candidate_cell_count"] == "6",
        "grade_deletion_five_of_five": next(row for row in changes if row["change_kind"] == "DELETE_GRADE")["attested_cell_count"] == "5" and next(row for row in changes if row["change_kind"] == "DELETE_GRADE")["candidate_cell_count"] == "5",
        "unique_missing_recipes_52": len(missing) == 52 and len({row["candidate_recipe"] for row in missing}) == 52,
        "unique_attested_recipes_43": len({row["candidate_recipe"] for row in cells if row["attested"] == "YES"}) == 43,
        "attested_predictions_match": all(row["reading_matches_prediction"] == "YES" for row in cells if row["attested"] == "YES"),
        "missing_predictions_marked": all(row["decision"] == "MISSING_FUTURE_PREDICTION" for row in cells if row["attested"] == "NO"),
        "candidate_status_complete": all(row["decision"] != "" for row in cells),
        "all_anchor_registers_five": all(int(row["anchor_register_count"]) == 5 for row in summaries),
        "anchor_event_counts_exact": [int(row["anchor_event_count"]) for row in summaries] == [107, 67, 64, 44, 13, 9, 6],
        "no_forbidden_page_token": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_pages": result["new_pages"] == 0,
        "no_dictionary_revision": result["dictionary_revisions"] == 0,
        "mismatch_zero": result["attested_prediction_mismatch_count"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt419_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
