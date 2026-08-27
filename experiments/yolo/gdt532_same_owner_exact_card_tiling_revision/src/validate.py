#!/usr/bin/env python3
"""Independently validate GDT532's exact-card composition override."""

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
BASE = ROOT / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt532_validation.json"
OLD_RUNNING = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
OLD_LOCAL = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_693_local_group_edition.tsv"
)
CURRENT_EVENTS = (
    ROOT
    / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
    / "gdt516_597_contextualized_event_edition.tsv"
)
CANDIDATES = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_candidate_score_atlas.tsv"
)
ALIGN = BASE / "src/align_surface.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result = json.loads((OUT / "gdt532_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt532_159_working_revision.tsv")
    routes = read_tsv(OUT / "gdt532_residual_candidate_tiling_atlas.tsv")
    summaries = read_tsv(OUT / "gdt532_distinct_candidate_tiling_summary.tsv")
    certificate = read_tsv(OUT / "gdt532_dsholdaiir_tile_certificate.tsv")
    competitors = read_tsv(OUT / "gdt532_dsholdaiir_competing_route_atlas.tsv")
    block = read_tsv(OUT / "gdt532_same_owner_block_atlas.tsv")
    unresolved = read_tsv(OUT / "gdt532_remaining_unresolved_atlas.tsv")
    old_running = read_tsv(OLD_RUNNING)
    old_local = read_tsv(OLD_LOCAL)
    current_events = read_tsv(CURRENT_EVENTS)
    candidate_rows = read_tsv(CANDIDATES)
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_UNIQUE_SAME_OWNER_EXACT_CARD_TILING_REVISION",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_UNIQUE_EXACT_CARD_COMPOSITION_OVERRIDE__NO_FREE_TILING_OR_CONFIRMED_PLAINTEXT",
        result["claim_ceiling"],
    )
    check("edition_count", len(edition) == 159, len(edition))
    check(
        "edition_unique", len({row["surface"] for row in edition}) == 159, len(edition)
    )
    changed = [
        row
        for row in edition
        if row["gdt531_working_recipe"] != row["gdt532_working_recipe"]
    ]
    check(
        "one_working_change",
        len(changed) == 1 and changed[0]["surface"] == "dsholdaiir",
        [row["surface"] for row in changed],
    )
    selected = changed[0]
    check(
        "selected_recipe_and_rank",
        selected["gdt531_working_recipe"] == "D_ADDR+SH+OL+D_ADDR+IIN+R"
        and selected["gdt531_working_rank"] == "2"
        and selected["gdt532_working_recipe"] == "D_ADDR+SH+OL+DA+IIN+R"
        and selected["gdt532_candidate_rank"] == "6",
        selected,
    )
    check(
        "selected_reading",
        selected["gdt532_short_phrase_de"]
        == "Hier halten und fortsetzen; Stufe II markieren."
        and "DA+IIN:STEUERUNG=STUFE II" in selected["gdt532_literal_reading_de"],
        selected["gdt532_short_phrase_de"],
    )
    check(
        "selected_resolution_status",
        selected["gdt532_resolution_status"]
        == "RESOLVED_BY_EXACT_CARD_COMPOSITION_OVERRIDE",
        selected["gdt532_resolution_status"],
    )

    route_counts = Counter(row["surface"] for row in routes)
    check("route_count", len(routes) == 16, len(routes))
    check(
        "route_surface_counts",
        route_counts == Counter({"dairykodas": 12, "dsholdaiir": 4}),
        dict(route_counts),
    )
    check(
        "distinct_surface_recipes",
        len({(row["surface"], row["candidate_recipe"]) for row in routes}) == 3,
        sorted({(row["surface"], row["candidate_recipe"]) for row in routes}),
    )
    candidate_rank = {
        (row["surface"], row["candidate_recipe"]): row["gdt529_rank"]
        for row in candidate_rows
    }
    route_integrity = all(
        "".join(row["surface_tiling"].split("|")) == row["surface"]
        and "+".join(row["recipe_tiling"].split(" | ")) == row["candidate_recipe"]
        and candidate_rank[(row["surface"], row["candidate_recipe"])]
        == row["gdt529_rank"]
        for row in routes
    )
    check("all_route_tilings_exact", route_integrity, "16/16")

    running_recipes: dict[str, set[str]] = defaultdict(set)
    running_counts: Counter[str] = Counter()
    local_recipes: dict[str, set[str]] = defaultdict(set)
    local_counts: Counter[str] = Counter()
    for row in old_running:
        running_recipes[row["surface"]].add(row["component_recipe"])
        running_counts[row["surface"]] += 1
    for row in old_local:
        local_recipes[row["surface"]].add(row["component_recipe"])
        local_counts[row["surface"]] += 1

    inventory_integrity = True
    for route in routes:
        for tile_surface, tile_recipe in zip(
            route["surface_tiling"].split("|"), route["recipe_tiling"].split(" | ")
        ):
            if tile_surface in running_recipes:
                inventory_integrity &= running_recipes[tile_surface] == {tile_recipe}
            else:
                inventory_integrity &= local_recipes[tile_surface] == {tile_recipe}
    check("all_tiles_invariant_old_cards", inventory_integrity, "all route tiles")

    check("summary_count", len(summaries) == 3, len(summaries))
    summary_by_key = {
        (row["surface"], row["candidate_recipe"]): row for row in summaries
    }
    dshold_summary = summary_by_key[("dsholdaiir", "D_ADDR+SH+OL+DA+IIN+R")]
    check(
        "dshold_unique_candidate_recipe",
        dshold_summary["distinct_tileable_candidate_recipe_count"] == "1"
        and dshold_summary["exact_tiling_route_count"] == "4"
        and dshold_summary["minimum_tile_count"] == "3"
        and dshold_summary["preferred_surface_tiling"] == "d|shol|daiir"
        and dshold_summary["gdt529_rank"] == "6",
        dshold_summary,
    )
    dair_summaries = [row for row in summaries if row["surface"] == "dairykodas"]
    check(
        "dairykodas_remains_ambiguous",
        len(dair_summaries) == 2
        and {row["gdt529_rank"] for row in dair_summaries} == {"1", "2"}
        and all(
            row["decision"] == "AMBIGUOUS_MULTIPLE_EXACTLY_TILEABLE_RECIPES"
            for row in dair_summaries
        ),
        dair_summaries,
    )
    check(
        "three_residuals_have_no_candidate_tiling",
        {"aiicthy", "dalcheeeky", "qef"}.isdisjoint(route_counts),
        sorted(route_counts),
    )

    check("certificate_count", len(certificate) == 3, len(certificate))
    certificate_by_surface = {row["tile_surface"]: row for row in certificate}
    check(
        "certificate_order",
        [row["tile_surface"] for row in certificate] == ["d", "shol", "daiir"],
        [row["tile_surface"] for row in certificate],
    )
    check(
        "d_card",
        certificate_by_surface["d"]["tile_recipe"] == "D_ADDR"
        and certificate_by_surface["d"]["source_tier"] == "OLD_RUNNING_INVARIANT"
        and certificate_by_surface["d"]["old_event_count"] == "11"
        and running_recipes["d"] == {"D_ADDR"}
        and running_counts["d"] == 11,
        certificate_by_surface["d"],
    )
    check(
        "shol_card",
        certificate_by_surface["shol"]["tile_recipe"] == "SH+OL"
        and certificate_by_surface["shol"]["source_tier"]
        == "OLD_RUNNING_INVARIANT"
        and certificate_by_surface["shol"]["old_event_count"] == "18"
        and running_recipes["shol"] == {"SH+OL"}
        and running_counts["shol"] == 18,
        certificate_by_surface["shol"],
    )
    check(
        "daiir_old_local_card",
        certificate_by_surface["daiir"]["tile_recipe"] == "DA+IIN+R"
        and certificate_by_surface["daiir"]["source_tier"]
        == "OLD_LOCAL_INVARIANT"
        and certificate_by_surface["daiir"]["old_event_count"] == "2"
        and local_recipes["daiir"] == {"DA+IIN+R"}
        and local_counts["daiir"] == 2,
        certificate_by_surface["daiir"],
    )
    current_daiir = [row for row in current_events if row["surface"] == "daiir"]
    check(
        "daiir_cross_role_current",
        len(current_daiir) == 2
        and {row["gdt516_context_recipe"] for row in current_daiir}
        == {"DA+IIN+R"}
        and {row["physical_page"] for row in current_daiir} == {"f31r", "f66r"},
        [row["event_id"] for row in current_daiir],
    )
    check(
        "daiir_same_owner_certificate",
        certificate_by_surface["daiir"]["same_owner_block_other_event_count"]
        == "1"
        and certificate_by_surface["daiir"]["same_owner_block_other_event_ids"]
        == "G515-E0408",
        certificate_by_surface["daiir"],
    )

    check("same_owner_block_count", len(block) == 56, len(block))
    relations = Counter(row["relation_to_selected_route"] for row in block)
    check(
        "same_owner_block_relations",
        relations
        == Counter(
            {
                "SAME_OWNER_BLOCK_CONTEXT": 53,
                "TARGET": 1,
                "SAME_OWNER_SHOL_PACKAGE_CARRIER": 1,
                "SAME_OWNER_EXACT_TAIL_CARRIER": 1,
            }
        ),
        dict(relations),
    )
    target = next(row for row in block if row["relation_to_selected_route"] == "TARGET")
    tail = next(
        row
        for row in block
        if row["relation_to_selected_route"] == "SAME_OWNER_EXACT_TAIL_CARRIER"
    )
    check(
        "target_and_tail_same_owner_block",
        target["event_id"] == "G515-E0366"
        and target["locus"] == "f66r.58"
        and tail["event_id"] == "G515-E0408"
        and tail["locus"] == "f66r.62"
        and target["owner_id"] == tail["owner_id"] == "F66R_TEXT_BLOCK_02"
        and target["prose_block_id"] == tail["prose_block_id"] == "F66R_PROSE_02",
        {"target": target, "tail": tail},
    )

    check("competitor_count", len(competitors) == 12, len(competitors))
    competitor_by_rank = {row["gdt529_rank"]: row for row in competitors}
    check(
        "only_rank6_tiles_exactly",
        competitor_by_rank["6"]["exact_card_tiling_route_count"] == "4"
        and competitor_by_rank["6"]["candidate_recipe"]
        == "D_ADDR+SH+OL+DA+IIN+R"
        and all(
            row["exact_card_tiling_route_count"] == "0"
            for rank, row in competitor_by_rank.items()
            if rank != "6"
        ),
        {rank: row["exact_card_tiling_route_count"] for rank, row in competitor_by_rank.items()},
    )
    check(
        "rank1_and_previous_have_no_tiling",
        competitor_by_rank["1"]["preferred_surface_tiling"] == "NONE"
        and competitor_by_rank["2"]["preferred_surface_tiling"] == "NONE"
        and competitor_by_rank["2"]["decision"]
        == "REPLACE_PREVIOUS_WORKING_NO_EXACT_CARD_TILING",
        {"rank1": competitor_by_rank["1"], "rank2": competitor_by_rank["2"]},
    )

    previous = result["previous_candidate_agreement_metrics"]
    revised = result["gdt532_candidate_agreement_metrics"]
    check(
        "previous_metrics",
        previous["top1_exact_count"] == 154
        and previous["top2_exact_count"] == 158
        and previous["rank_sum"] == 171,
        previous,
    )
    check(
        "revised_rank_diagnostic",
        revised["top1_exact_count"] == 154
        and revised["top2_exact_count"] == 157
        and revised["top5_exact_count"] == 157
        and revised["rank_sum"] == 175
        and result["candidate_rank_cost"]["selected_surface_rank_change"] == "2->6",
        {"metrics": revised, "cost": result["candidate_rank_cost"]},
    )
    check(
        "rank_cost_explicit_not_hidden",
        result["candidate_rank_cost"]["rank_sum_change"] == 4
        and result["candidate_rank_cost"]["top2_change"] == -1
        and "OVERRIDES" in result["candidate_rank_cost"]["interpretation"],
        result["candidate_rank_cost"],
    )
    check(
        "unresolved_queue",
        len(unresolved) == 4
        and [row["surface"] for row in unresolved]
        == ["aiicthy", "dairykodas", "dalcheeeky", "qef"]
        and result["remaining_unresolved_surfaces"]
        == ["aiicthy", "dairykodas", "dalcheeeky", "qef"],
        [row["surface"] for row in unresolved],
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
                "12",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    aligned = align("dsholdaiir", "G515-E0366", "f66r")
    check(
        "executable_dsholdaiir_override",
        aligned["gdt531_default_selection"] == "D_ADDR+SH+OL+D_ADDR+IIN+R"
        and aligned["default_selection"] == "D_ADDR+SH+OL+DA+IIN+R"
        and aligned["working_revision"] == "D_ADDR+SH+OL+DA+IIN+R"
        and aligned["exact_card_tiling_certificate"]["surface_tiling"]
        == "d|shol|daiir"
        and aligned["exact_card_tiling_certificate"]["candidate_rank"] == 6,
        aligned,
    )
    saiis = align("saiis", "G515-E0243", "f31r")
    check(
        "gdt531_saiis_revision_preserved",
        saiis["default_selection"] == "S+A_ADDR+IIN+S"
        and saiis["working_revision"] == "S+A_ADDR+IIN+S"
        and saiis["exact_card_tiling_certificate"] == "NONE",
        saiis["default_selection"],
    )
    chekchy = align("chekchy", "G515-E0426", "f66r")
    check(
        "gdt530_chekchy_revision_preserved",
        chekchy["default_selection"] == "CH+K+Y"
        and chekchy["working_revision"] == "CH+K+Y",
        chekchy["default_selection"],
    )
    check(
        "no_new_page_guard",
        result["guard"].endswith("NO_NEW_PAGES"),
        result["guard"],
    )

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    validation = {
        "experiment_id": "GDT532",
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
