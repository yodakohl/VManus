#!/usr/bin/env python3
"""Independently validate GDT530's exact-superform working revision."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt530_exact_superform_peel_revision"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt530_validation.json"
OLD = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
SIGNATURES = (
    ROOT
    / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/artifacts"
    / "gdt522_local_edit_analogy_atlas.tsv"
)
ALIGN = BASE / "src/align_surface.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result = json.loads((OUT / "gdt530_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt530_159_working_revision.tsv")
    routes = read_tsv(OUT / "gdt530_superform_peel_route_atlas.tsv")
    selected = read_tsv(OUT / "gdt530_selected_revision_atlas.tsv")
    old_chy = read_tsv(OUT / "gdt530_old_chy_tail_atlas.tsv")
    current_chy = read_tsv(OUT / "gdt530_current_chy_tail_atlas.tsv")
    remaining = read_tsv(OUT / "gdt530_remaining_working_error_atlas.tsv")
    old = read_tsv(OLD)
    signature_rows = read_tsv(SIGNATURES)
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_EXACT_SUPERFORM_PEEL_WORKING_REVISION",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_EXACT_SUPERFORM_PEEL_WORKING_REVISION__NO_GLOBAL_CHY_RULE_OR_CONFIRMED_PLAINTEXT",
        result["claim_ceiling"],
    )
    check("edition_count", len(edition) == 159, len(edition))
    check(
        "edition_unique", len({row["surface"] for row in edition}) == 159, len(edition)
    )
    changed = [
        row
        for row in edition
        if row["revised_working_recipe"] != row["gdt530_working_recipe"]
    ]
    check(
        "one_working_change",
        len(changed) == 1 and changed[0]["surface"] == "chekchy",
        [row["surface"] for row in changed],
    )
    chek = changed[0]
    check(
        "chekchy_recipe",
        chek["revised_working_recipe"] == "CH+K+CH+Y"
        and chek["gdt529_top1"] == "CH+K+Y"
        and chek["gdt530_working_recipe"] == "CH+K+Y"
        and chek["gdt529_revised_rank"] == "2"
        and chek["gdt530_working_rank"] == "1",
        chek,
    )
    check(
        "chekchy_reading",
        chek["gdt530_literal_reading_de"] == "NEHMEN · GEBEN · POSTEN"
        and chek["gdt530_short_phrase_de"] == "Nehmen, geben und posten.",
        chek["gdt530_short_phrase_de"],
    )
    check("route_count", len(routes) == 25, len(routes))
    check(
        "route_surface_count",
        len({row["surface"] for row in routes}) == 14,
        len({row["surface"] for row in routes}),
    )
    route_classes = Counter(row["route_class"] for row in routes)
    check(
        "route_classes",
        route_classes
        == Counter(
            {
                "SUPPORTS_EXISTING_WORKING_AND_TOP1": 24,
                "SUPPORTS_TOP1_ALTERNATIVE": 1,
            }
        ),
        dict(route_classes),
    )
    check("single_selected_revision", len(selected) == 1, len(selected))
    sel = selected[0]
    check(
        "selected_exact_route",
        sel["surface"] == "chekchy"
        and sel["old_superform"] == "ychekchy"
        and sel["old_superform_recipe"] == "Y+CH+K+Y"
        and sel["supported_candidate_recipe"] == "CH+K+Y",
        sel,
    )
    check(
        "selected_peel",
        sel["removed_visible"] == "y"
        and sel["visible_position"] == "LEFT"
        and sel["removed_atom"] == "Y"
        and sel["atom_position"] == "LEFT",
        sel,
    )
    check(
        "selected_signature",
        sel["support_pair_count"] == "54"
        and sel["visible_condition_total"] == "59"
        and sel["conditional_probability"] == "0.886178862"
        and sel["reliability"] == "0.964285714",
        sel,
    )

    old_recipes: dict[str, set[str]] = defaultdict(set)
    old_counts: Counter[str] = Counter()
    for row in old:
        old_recipes[row["surface"]].add(row["component_recipe"])
        old_counts[row["surface"]] += 1
    check(
        "old_superform_exact",
        old_recipes["ychekchy"] == {"Y+CH+K+Y"}
        and old_counts["ychekchy"] == 1,
        {"recipes": sorted(old_recipes["ychekchy"]), "events": old_counts["ychekchy"]},
    )
    check(
        "independent_ckhy_support",
        old_recipes["ckhy"] == {"CH+K+Y"} and old_counts["ckhy"] == 2,
        {"recipes": sorted(old_recipes["ckhy"]), "events": old_counts["ckhy"]},
    )
    check(
        "target_not_old_exact",
        "chekchy" not in old_recipes,
        sorted(old_recipes.get("chekchy", set())),
    )
    signature_index = {
        (
            row["visible_insert"],
            row["visible_position"],
            row["atom_insert"],
            row["atom_position"],
        ): row
        for row in signature_rows
    }
    signature = signature_index[("y", "LEFT", "Y", "LEFT")]
    check(
        "source_signature_exact",
        signature["support_pair_count"] == "54"
        and signature["visible_condition_total"] == "59"
        and signature["conditional_probability"] == "0.886178862"
        and signature["reliability"] == "0.964285714",
        signature,
    )

    route_integrity = True
    route_source_integrity = True
    route_signature_integrity = True
    for route in routes:
        big = route["old_superform"]
        visible_index = int(route["visible_index"])
        big_recipe = route["old_superform_recipe"].split("+")
        atom_index = int(route["atom_index"])
        route_integrity &= (
            big[:visible_index] + big[visible_index + 1 :] == route["surface"]
            and "+".join(big_recipe[:atom_index] + big_recipe[atom_index + 1 :])
            == route["supported_candidate_recipe"]
        )
        route_source_integrity &= old_recipes.get(big) == {route["old_superform_recipe"]}
        key = (
            route["removed_visible"],
            route["visible_position"],
            route["removed_atom"],
            route["atom_position"],
        )
        source = signature_index.get(key)
        route_signature_integrity &= (
            source is not None
            and source["support_pair_count"] == route["support_pair_count"]
            and source["conditional_probability"] == route["conditional_probability"]
            and source["reliability"] == route["reliability"]
        )
    check("all_route_deletions_exact", route_integrity, "25/25")
    check("all_route_sources_invariant", route_source_integrity, "25/25")
    check("all_route_signatures_exact", route_signature_integrity, "25/25")

    previous_ranks = [int(row["gdt529_revised_rank"]) for row in edition]
    revised_ranks = [int(row["gdt530_working_rank"]) for row in edition]
    previous = result["previous_working_metrics"]
    revised = result["gdt530_working_metrics"]
    check(
        "previous_metrics",
        previous["top1_exact_count"] == 152
        and previous["top2_exact_count"] == 157
        and previous["rank_sum"] == 174
        and sum(previous_ranks) == 174,
        previous,
    )
    check(
        "revised_metrics",
        revised["top1_exact_count"] == 153
        and revised["top2_exact_count"] == 157
        and revised["rank_sum"] == 173
        and sum(revised_ranks) == 173,
        revised,
    )
    check(
        "one_rank_improvement_no_loss",
        sum(new < old for old, new in zip(previous_ranks, revised_ranks)) == 1
        and all(new <= old for old, new in zip(previous_ranks, revised_ranks)),
        "one improved; zero worsened",
    )

    old_tail_types = Counter(row["tail_category"] for row in old_chy)
    old_tail_events: Counter[str] = Counter()
    for row in old_chy:
        old_tail_events[row["tail_category"]] += int(row["event_count"])
    check("old_chy_type_count", len(old_chy) == 54, len(old_chy))
    check(
        "old_chy_type_split",
        old_tail_types
        == Counter({"TAIL_Y_WITHOUT_CH": 28, "TAIL_CH_PLUS_Y": 26}),
        dict(old_tail_types),
    )
    check(
        "old_chy_event_split",
        old_tail_events
        == Counter({"TAIL_Y_WITHOUT_CH": 69, "TAIL_CH_PLUS_Y": 34}),
        dict(old_tail_events),
    )
    check("current_chy_count", len(current_chy) == 7, len(current_chy))
    current_tail_types = Counter(row["gdt530_tail_category"] for row in current_chy)
    check(
        "current_chy_split",
        current_tail_types
        == Counter({"TAIL_CH_PLUS_Y": 6, "TAIL_Y_WITHOUT_CH": 1}),
        dict(current_tail_types),
    )
    check(
        "chy_context_guard",
        result["guard"].startswith("CHY_IS_CONTEXT_DEPENDENT")
        and {row["gdt530_tail_category"] for row in current_chy}
        == {"TAIL_CH_PLUS_Y", "TAIL_Y_WITHOUT_CH"},
        result["guard"],
    )
    check(
        "remaining_queue",
        len(remaining) == 6
        and [row["surface"] for row in remaining]
        == ["aiicthy", "dairykodas", "dalcheeeky", "dsholdaiir", "qef", "saiis"]
        and result["remaining_surfaces"]
        == ["aiicthy", "dairykodas", "dalcheeeky", "dsholdaiir", "qef", "saiis"],
        [row["surface"] for row in remaining],
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(ALIGN),
            "--surface",
            "chekchy",
            "--event-id",
            "G515-E0426",
            "--page",
            "f66r",
            "--top",
            "5",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    aligned = json.loads(completed.stdout)
    check(
        "executable_default",
        aligned["default_selection"] == "CH+K+Y"
        and aligned["working_revision"] == "CH+K+Y"
        and aligned["superform_certificate"]["old_superform"] == "ychekchy",
        aligned,
    )
    check(
        "no_new_page_guard",
        result["guard"].endswith("NO_NEW_PAGES"),
        result["guard"],
    )

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    validation = {
        "experiment_id": "GDT530",
        "status": status,
        "check_count": len(checks),
        "passed_count": sum(row["pass"] for row in checks),
        "failed_count": sum(not row["pass"] for row in checks),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
