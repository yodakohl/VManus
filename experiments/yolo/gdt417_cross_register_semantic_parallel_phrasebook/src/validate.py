#!/usr/bin/env python3
"""Validate the GDT417 cross-register parallel phrasebook."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt417_cross_register_semantic_parallel_phrasebook"
OUT = BASE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    recipes = rows("gdt417_298_cross_register_recipes.tsv")
    events = rows("gdt417_3317_cross_register_events.tsv")
    exact = rows("gdt417_45_exact_statement_parallels.tsv")
    templates = rows("gdt417_168_template_statement_parallels.tsv")
    roots = rows("gdt417_19_root_portability.tsv")
    result = json.loads((OUT / "gdt417_result.json").read_text(encoding="utf-8"))
    tier_counts = Counter(r["portability_tier"] for r in recipes)
    recipe_by_id = {r["component_recipe"]: r for r in recipes}
    checks = {
        "recipes_298": len(recipes) == 298,
        "recipes_unique": len(recipe_by_id) == 298,
        "events_3317": len(events) == 3317,
        "events_unique": len({r["global_running_event_id"] for r in events}) == 3317,
        "events_recipes_known": {r["component_recipe"] for r in events} == set(recipe_by_id),
        "recipe_event_counts": all(int(r["event_count"]) == sum(e["component_recipe"] == r["component_recipe"] for e in events) for r in recipes),
        "tiers_exact": tier_counts == Counter({"TWO_REGISTERS": 168, "THREE_REGISTERS": 80, "FOUR_REGISTERS": 30, "ALL_FIVE_REGISTERS": 20}),
        "register_counts_match": all(int(r["register_count"]) == len(r["registers"].split("|")) for r in recipes),
        "context_counts_bounded": all(int(r["context_bound_event_count"]) <= int(r["event_count"]) for r in recipes),
        "context_modes_known": all(r["context_mode"] in {"FULLY_SELF_CONTAINED", "FULLY_CONTEXT_BOUND", "MIXED_SELF_CONTAINED_AND_CONTEXT_BOUND"} for r in recipes),
        "all_five_examples_complete": all(all(r[f"{reg.lower()}_example"] != "NONE" for reg in ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")) for r in recipes if r["portability_tier"] == "ALL_FIVE_REGISTERS"),
        "exact_45": len(exact) == 45,
        "exact_patterns_3": len({r["parallel_id"] for r in exact}) == 3,
        "template_168": len(templates) == 168,
        "template_patterns_11": len({r["parallel_id"] for r in templates}) == 11,
        "roots_19": len(roots) == 19 and len({r["root"] for r in roots}) == 19,
        "root_mentions_positive": all(int(r["cross_register_mention_count"]) > 0 for r in roots),
        "root_mentions_bounded": all(int(r["cross_register_mention_count"]) <= int(r["total_mention_count"]) for r in roots),
        "no_forbidden_page": all(not r["physical_page"].startswith("f84") for r in events),
        "phrasebook_exists": (OUT / "ALL_FIVE_REGISTER_PARALLEL_PHRASEBOOK.md").is_file(),
        "no_new_pages": result["new_pages"] == 0,
        "no_new_roots": result["new_roots"] == 0,
        "no_new_meanings": result["new_meanings"] == 0,
    }
    tracked = [
        OUT / "gdt417_298_cross_register_recipes.tsv",
        OUT / "gdt417_3317_cross_register_events.tsv",
        OUT / "gdt417_45_exact_statement_parallels.tsv",
        OUT / "gdt417_168_template_statement_parallels.tsv",
        OUT / "gdt417_19_root_portability.tsv",
        OUT / "ALL_FIVE_REGISTER_PARALLEL_PHRASEBOOK.md",
        OUT / "gdt417_result.json",
    ]
    before = {p.name: digest(p) for p in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    checks["deterministic_rebuild"] = before == {p.name: digest(p) for p in tracked}
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "failure_count": sum(not value for value in checks.values()),
        "checks": checks,
    }
    (OUT / "gdt417_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
