#!/usr/bin/env python3
"""Validate the GDT418 P/L closure."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt418_p_l_weak_core_compositional_closure"
OUT = BASE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    occurrences = rows("gdt418_430_p_l_occurrence_audit.tsv")
    recipes = rows("gdt418_231_p_l_recipe_inventory.tsv")
    profiles = rows("gdt418_p_l_profiles.tsv")
    scores = rows("gdt418_p_l_candidate_scorecard.tsv")
    result = json.loads((OUT / "gdt418_result.json").read_text(encoding="utf-8"))
    p = next(r for r in profiles if r["root"] == "P")
    l = next(r for r in profiles if r["root"] == "L")
    selected = {r["root"]: r for r in scores if r["status"] == "SELECTED"}
    checks = {
        "occurrences_430": len(occurrences) == 430,
        "p_160": sum(r["root"] == "P" for r in occurrences) == 160,
        "l_270": sum(r["root"] == "L" for r in occurrences) == 270,
        "occurrence_ids_consistent": all(r["root"] in r["component_recipe"].split("+") for r in occurrences),
        "recipes_231": len(recipes) == 231,
        "recipe_keys_unique": len({(r["root"], r["component_recipe"]) for r in recipes}) == 231,
        "profiles_2": len(profiles) == 2 and {r["root"] for r in profiles} == {"P", "L"},
        "p_positions_exact": (p["first_count"], p["middle_count"], p["last_count"], p["only_count"]) == ("49", "107", "4", "0"),
        "l_positions_exact": (l["first_count"], l["middle_count"], l["last_count"], l["only_count"]) == ("179", "20", "53", "18"),
        "p_coactions_126": p["with_other_action_count"] == "126",
        "l_coaction_mentions_184": l["with_other_action_count"] == "184",
        "cross_recipe_counts": p["cross_register_recipe_type_count"] == "10" and l["cross_register_recipe_type_count"] == "9",
        "self_contained_cross_counts": p["fully_self_contained_cross_recipe_type_count"] == "8" and l["fully_self_contained_cross_recipe_type_count"] == "2",
        "score_candidates_8": len(scores) == 8,
        "one_selected_per_root": set(selected) == {"P", "L"},
        "selected_values_exact": selected["P"]["candidate_de"] == "EINSETZEN" and selected["L"]["candidate_de"] == "VERBINDUNG",
        "selected_scores_highest": all(int(selected[root]["total_0_20"]) > max(int(r["total_0_20"]) for r in scores if r["root"] == root and r["status"] != "SELECTED") for root in selected),
        "no_forbidden_page": all(not r["physical_page"].startswith("f84") for r in occurrences),
        "predictions_exist": (OUT / "P_L_NEXT_PAGE_COMPOSITION_CARDS.md").is_file(),
        "no_dictionary_revision": result["dictionary_revisions"] == 0,
        "no_new_pages": result["new_pages"] == 0,
    }
    tracked = [
        OUT / "gdt418_430_p_l_occurrence_audit.tsv",
        OUT / "gdt418_231_p_l_recipe_inventory.tsv",
        OUT / "gdt418_p_l_profiles.tsv",
        OUT / "gdt418_p_l_candidate_scorecard.tsv",
        OUT / "P_L_NEXT_PAGE_COMPOSITION_CARDS.md",
        OUT / "gdt418_result.json",
    ]
    before = {path.name: digest(path) for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    checks["deterministic_rebuild"] = before == {path.name: digest(path) for path in tracked}
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "failure_count": sum(not value for value in checks.values()),
        "checks": checks,
    }
    (OUT / "gdt418_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
