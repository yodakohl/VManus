#!/usr/bin/env python3
"""Independently validate GDT531's atomic block-superform revision."""

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
BASE = ROOT / "experiments/yolo/gdt531_atomic_renderer_block_superform_peel"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt531_validation.json"
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
    result = json.loads((OUT / "gdt531_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt531_159_working_revision.tsv")
    routes = read_tsv(OUT / "gdt531_atomic_block_peel_route_atlas.tsv")
    selected = read_tsv(OUT / "gdt531_selected_revision_atlas.tsv")
    competitors = read_tsv(OUT / "gdt531_saiis_competing_route_atlas.tsv")
    family = read_tsv(OUT / "gdt531_saii_family_atlas.tsv")
    remaining = read_tsv(OUT / "gdt531_remaining_working_error_atlas.tsv")
    old = read_tsv(OLD)
    signature_rows = read_tsv(SIGNATURES)
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL__NO_GLOBAL_OL_SUFFIX_OR_CONFIRMED_PLAINTEXT",
        result["claim_ceiling"],
    )
    policy = result["selected_policy"]
    check(
        "selected_policy",
        policy["visible_block_widths"] == [2, 3]
        and policy["atom_block_widths"] == [1, 2, 3]
        and "GDT522" in policy["license"],
        policy,
    )
    check("edition_count", len(edition) == 159, len(edition))
    check(
        "edition_unique", len({row["surface"] for row in edition}) == 159, len(edition)
    )
    changed = [
        row
        for row in edition
        if row["gdt530_working_recipe"] != row["gdt531_working_recipe"]
    ]
    check(
        "one_working_change",
        len(changed) == 1 and changed[0]["surface"] == "saiis",
        [row["surface"] for row in changed],
    )
    saiis = changed[0]
    check(
        "saiis_recipe",
        saiis["gdt530_working_recipe"] == "S+IIN+S"
        and saiis["gdt529_top1"] == "S+A_ADDR+IIN+S"
        and saiis["gdt531_working_recipe"] == "S+A_ADDR+IIN+S"
        and saiis["gdt530_working_rank"] == "3"
        and saiis["gdt531_working_rank"] == "1",
        saiis,
    )
    check(
        "saiis_reading",
        saiis["gdt531_literal_reading_de"] == "WÄHLEN · HIER · STUFE · WÄHLEN"
        and saiis["gdt531_short_phrase_de"] == "Wählen; hier die Stufe wählen.",
        saiis["gdt531_short_phrase_de"],
    )
    check("route_count", len(routes) == 29, len(routes))
    check(
        "route_surface_count",
        len({row["surface"] for row in routes}) == 15,
        len({row["surface"] for row in routes}),
    )
    route_classes = Counter(row["route_class"] for row in routes)
    check(
        "route_classes",
        route_classes
        == Counter(
            {
                "SUPPORTS_EXISTING_WORKING_AND_TOP1": 28,
                "SUPPORTS_TOP1_ALTERNATIVE": 1,
            }
        ),
        dict(route_classes),
    )
    check("single_selected_revision", len(selected) == 1, len(selected))
    sel = selected[0]
    check(
        "selected_exact_route",
        sel["surface"] == "saiis"
        and sel["old_superform"] == "saiisol"
        and sel["old_superform_recipe"] == "S+A_ADDR+IIN+S+OL"
        and sel["supported_candidate_recipe"] == "S+A_ADDR+IIN+S",
        sel,
    )
    check(
        "selected_block_peel",
        sel["removed_visible_block"] == "ol"
        and sel["visible_block_width"] == "2"
        and sel["visible_position"] == "RIGHT"
        and sel["removed_atom_block"] == "OL"
        and sel["atom_block_width"] == "1"
        and sel["atom_position"] == "RIGHT",
        sel,
    )
    check(
        "selected_signature",
        sel["support_pair_count"] == "29"
        and sel["visible_condition_total"] == "33"
        and sel["conditional_probability"] == "0.830985915"
        and sel["reliability"] == "0.935483871",
        sel,
    )

    old_recipes: dict[str, set[str]] = defaultdict(set)
    old_counts: Counter[str] = Counter()
    for row in old:
        old_recipes[row["surface"]].add(row["component_recipe"])
        old_counts[row["surface"]] += 1
    check(
        "old_superform_exact",
        old_recipes["saiisol"] == {"S+A_ADDR+IIN+S+OL"}
        and old_counts["saiisol"] == 1,
        {"recipes": sorted(old_recipes["saiisol"]), "events": old_counts["saiisol"]},
    )
    check(
        "target_not_old_exact",
        "saiis" not in old_recipes,
        sorted(old_recipes.get("saiis", set())),
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
    signature = signature_index[("ol", "RIGHT", "OL", "RIGHT")]
    check(
        "source_signature_exact",
        signature["support_pair_count"] == "29"
        and signature["visible_condition_total"] == "33"
        and signature["conditional_probability"] == "0.830985915"
        and signature["reliability"] == "0.935483871",
        signature,
    )

    route_integrity = True
    source_integrity = True
    signature_integrity = True
    for route in routes:
        big = route["old_superform"]
        vi = int(route["visible_index"])
        vw = int(route["visible_block_width"])
        recipe = route["old_superform_recipe"].split("+")
        ai = int(route["atom_index"])
        aw = int(route["atom_block_width"])
        route_integrity &= (
            big[:vi] + big[vi + vw :] == route["surface"]
            and "+".join(recipe[:ai] + recipe[ai + aw :])
            == route["supported_candidate_recipe"]
        )
        source_integrity &= old_recipes.get(big) == {route["old_superform_recipe"]}
        source = signature_index.get(
            (
                route["removed_visible_block"],
                route["visible_position"],
                route["removed_atom_block"],
                route["atom_position"],
            )
        )
        signature_integrity &= (
            source is not None
            and source["support_pair_count"] == route["support_pair_count"]
            and source["conditional_probability"] == route["conditional_probability"]
            and source["reliability"] == route["reliability"]
        )
    check("all_route_deletions_exact", route_integrity, "29/29")
    check("all_route_sources_invariant", source_integrity, "29/29")
    check("all_route_signatures_exact", signature_integrity, "29/29")
    check(
        "all_routes_strong",
        all(
            int(row["support_pair_count"]) >= 3
            and float(row["conditional_probability"]) >= 0.5
            and float(row["reliability"]) >= 0.6
            for row in routes
        ),
        "29/29",
    )

    previous = result["previous_working_metrics"]
    revised = result["gdt531_working_metrics"]
    previous_ranks = [int(row["gdt530_working_rank"]) for row in edition]
    revised_ranks = [int(row["gdt531_working_rank"]) for row in edition]
    check(
        "previous_metrics",
        previous["top1_exact_count"] == 153
        and previous["top2_exact_count"] == 157
        and previous["rank_sum"] == 173
        and sum(previous_ranks) == 173,
        previous,
    )
    check(
        "revised_metrics",
        revised["top1_exact_count"] == 154
        and revised["top2_exact_count"] == 158
        and revised["rank_sum"] == 171
        and sum(revised_ranks) == 171,
        revised,
    )
    check(
        "one_rank_improvement_no_loss",
        sum(new < old for old, new in zip(previous_ranks, revised_ranks)) == 1
        and all(new <= old for old, new in zip(previous_ranks, revised_ranks)),
        "one improved by two ranks; zero worsened",
    )
    check("competitor_count", len(competitors) == 3, len(competitors))
    competitor_by_recipe = {row["candidate_recipe"]: row for row in competitors}
    check(
        "competitor_ranks",
        competitor_by_recipe["S+A_ADDR+IIN+S"]["gdt529_rank"] == "1"
        and competitor_by_recipe["S+AIIN+S"]["gdt529_rank"] == "2"
        and competitor_by_recipe["S+IIN+S"]["gdt529_rank"] == "3",
        {key: row["gdt529_rank"] for key, row in competitor_by_recipe.items()},
    )
    check(
        "specific_route_selected",
        competitor_by_recipe["S+A_ADDR+IIN+S"]["decision"] == "SELECTED"
        and competitor_by_recipe["S+AIIN+S"]["decision"].startswith("RUNNER_UP"),
        {key: row["decision"] for key, row in competitor_by_recipe.items()},
    )
    family_counts = {row["surface"]: int(row["event_count"]) for row in family}
    check(
        "saii_family",
        family_counts == {"saii": 1, "saiin": 20, "saiisol": 1}
        and result["saii_family_surface_count"] == 3
        and result["saii_family_event_count"] == 22,
        family_counts,
    )
    check(
        "remaining_queue",
        len(remaining) == 5
        and [row["surface"] for row in remaining]
        == ["aiicthy", "dairykodas", "dalcheeeky", "dsholdaiir", "qef"]
        and result["remaining_surfaces"]
        == ["aiicthy", "dairykodas", "dalcheeeky", "dsholdaiir", "qef"],
        [row["surface"] for row in remaining],
    )

    def align(surface: str, event: str, page: str) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                str(ALIGN),
                "--surface",
                surface,
                "--event-id",
                event,
                "--page",
                page,
                "--top",
                "5",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    aligned = align("saiis", "G515-E0243", "f31r")
    check(
        "executable_saiis_default",
        aligned["default_selection"] == "S+A_ADDR+IIN+S"
        and aligned["working_revision"] == "S+A_ADDR+IIN+S"
        and aligned["block_superform_certificate"]["old_superform"] == "saiisol",
        aligned,
    )
    inherited = align("chekchy", "G515-E0426", "f66r")
    check(
        "gdt530_revision_preserved",
        inherited["default_selection"] == "CH+K+Y"
        and inherited["working_revision"] == "CH+K+Y"
        and inherited["block_superform_certificate"] == "NONE",
        inherited["default_selection"],
    )
    check(
        "no_new_page_guard",
        result["guard"].endswith("NO_NEW_PAGES"),
        result["guard"],
    )

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    validation = {
        "experiment_id": "GDT531",
        "status": status,
        "check_count": len(checks),
        "passed_count": sum(row["pass"] for row in checks),
        "failed_count": sum(not row["pass"] for row in checks),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
