#!/usr/bin/env python3
"""Independently validate GDT516 family compression and context overlay."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation"
ART = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
OUT = ART / "gdt516_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(recipe.split("+"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    new_input = read_tsv(G515 / "gdt515_159_genuinely_new_surface_audit.tsv")
    event_input = read_tsv(G515 / "gdt515_597_complete_event_edition.tsv")
    running30 = read_tsv(G515 / "gdt515_5122_running_event_edition.tsv")
    unified30 = read_tsv(G515 / "gdt515_5866_unified_group_ledger.tsv")
    old_running = read_tsv(G407 / "gdt407_4576_running_event_edition.tsv")
    dictionary_rows = read_tsv(G413 / "gdt413_46_component_working_dictionary.tsv")

    family = read_tsv(ART / "gdt516_159_new_surface_family_atlas.tsv")
    portable = read_tsv(ART / "gdt516_20_recurrent_portable_skeleton_families.tsv")
    carriers = read_tsv(ART / "gdt516_10_exact_old_recipe_carriers.tsv")
    cross = read_tsv(ART / "gdt516_3_cross_new_page_recurrences.tsv")
    context = read_tsv(ART / "gdt516_10_old_local_new_context_decisions.tsv")
    open_rows = read_tsv(ART / "gdt516_6_open_parse_decisions.tsv")
    local_tags = read_tsv(ART / "gdt516_4_local_tag_registry.tsv")
    dy_pairs = read_tsv(ART / "gdt516_110_dy_y_pair_atlas.tsv")
    dy_summary = read_tsv(ART / "gdt516_dy_ending_summary.tsv")
    transitions = read_tsv(ART / "gdt516_31_new_action_transition_atlas.tsv")
    events = read_tsv(ART / "gdt516_597_contextualized_event_edition.tsv")
    unified = read_tsv(ART / "gdt516_5866_contextualized_unified_group_ledger.tsv")
    result = json.loads((ART / "gdt516_result.json").read_text(encoding="utf-8"))

    actual_counts = {
        "family": len(family),
        "portable": len(portable),
        "carriers": len(carriers),
        "cross": len(cross),
        "context": len(context),
        "open": len(open_rows),
        "local_tags": len(local_tags),
        "dy_pairs": len(dy_pairs),
        "dy_summary": len(dy_summary),
        "transitions": len(transitions),
        "events": len(events),
        "unified": len(unified),
    }
    expected_counts = {
        "family": 159,
        "portable": 20,
        "carriers": 10,
        "cross": 3,
        "context": 10,
        "open": 6,
        "local_tags": 4,
        "dy_pairs": 110,
        "dy_summary": 3,
        "transitions": 31,
        "events": 597,
        "unified": 5866,
    }
    check("artifact_row_counts", actual_counts == expected_counts, str(actual_counts))

    input_surfaces = {row["surface"] for row in new_input}
    family_surfaces = {row["surface"] for row in family}
    check(
        "new_surface_exactness",
        len(input_surfaces) == 159 and family_surfaces == input_surfaces,
        f"input={len(input_surfaces)} output={len(family_surfaces)}",
    )
    check(
        "one_new_surface_one_recipe",
        len({row["gdt516_context_recipe"] for row in family}) == 159,
        "159 context recipes for 159 new surfaces",
    )

    tier_counts = Counter(row["support_tier"] for row in family)
    check(
        "support_tier_distribution",
        tier_counts
        == {
            "FULL_OLD_RECIPE_CARRIER": 10,
            "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": 29,
            "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": 91,
            "ATOMS_AND_FACTORS_ONLY": 29,
        },
        str(dict(tier_counts)),
    )
    covered = sum(int(row["max_disjoint_old_recipe_coverage_atoms"]) for row in family)
    total = sum(int(row["recipe_atom_count"]) for row in family)
    check(
        "old_recipe_tile_coverage",
        (covered, total) == (426, 643),
        f"covered={covered} total={total}",
    )
    fully_tiled = sum(
        row["max_disjoint_old_recipe_coverage_atoms"] == row["recipe_atom_count"]
        for row in family
    )
    fragment_supported = sum(
        row["old_exact_recipe_event_count"] == "0"
        and int(row["longest_old_complete_recipe_fragment_atoms"]) >= 2
        for row in family
    )
    check(
        "tiling_and_fragment_counts",
        fully_tiled == 39 and fragment_supported == 120,
        f"fully_tiled={fully_tiled} nonexact_fragment={fragment_supported}",
    )

    old_recipe_events: dict[tuple[str, ...], int] = Counter(
        atoms(row["component_recipe"]) for row in old_running
    )
    recomputed_carriers = {
        row["surface"]
        for row in family
        if old_recipe_events[atoms(row["gdt516_context_recipe"])] > 0
    }
    check(
        "exact_carriers_recomputed",
        recomputed_carriers == {row["surface"] for row in carriers}
        and len(recomputed_carriers) == 10,
        "|".join(sorted(recomputed_carriers)),
    )
    expected_carriers = {
        "chekeey", "dalol", "doiiin", "okoy", "qocthedy",
        "qokaiir", "qokchey", "qokee", "qokees", "shee",
    }
    check(
        "exact_carrier_names",
        recomputed_carriers == expected_carriers,
        "|".join(sorted(recomputed_carriers)),
    )

    check(
        "portable_family_counts",
        len(portable) == 20
        and sum(int(row["surface_count"]) for row in portable) == 48,
        f"families={len(portable)} surfaces={sum(int(row['surface_count']) for row in portable)}",
    )
    check(
        "cross_page_anchor_names",
        {row["surface"] for row in cross} == {"keody", "qokees", "shain"},
        "|".join(sorted(row["surface"] for row in cross)),
    )
    check(
        "cross_page_anchor_counts",
        {row["surface"]: int(row["occurrence_count"]) for row in cross}
        == {"keody": 3, "qokees": 2, "shain": 2},
        str({row["surface"]: row["occurrence_count"] for row in cross}),
    )

    decision_counts = Counter(row["decision"] for row in context)
    check(
        "finite_context_policy_distribution",
        decision_counts
        == {
            "EXACT_RECIPE_AGREEMENT": 3,
            "COMMON_VISIBLE_RECIPE_PROMOTION": 2,
            "LEARNED_LABEL_SHELL_REPLAY": 1,
            "ROLE_CONDITIONED_HOMOGRAPH": 4,
        },
        str(dict(decision_counts)),
    )
    check(
        "context_policy_no_portable_retune",
        all(row["portable_meaning_change"] == "NO" for row in context),
        "10/10 keep portable meanings",
    )
    context_by_surface = {row["surface"]: row for row in context}
    check(
        "common_recipe_promotions_exact",
        context_by_surface["chekey"]["old_context_recipe"]
        == context_by_surface["chekey"]["new_context_recipe"]
        == "CH+K+E+Y"
        and context_by_surface["saiir"]["old_context_recipe"]
        == context_by_surface["saiir"]["new_context_recipe"]
        == "S+IIN+R",
        "chekey and saiir share one visible recipe across roles",
    )
    check(
        "role_homographs_remain_explicit",
        all(
            context_by_surface[surface]["old_context_recipe"]
            != context_by_surface[surface]["new_context_recipe"]
            for surface in ("okyd", "sos", "ykady", "ykeeody")
        ),
        "four label/prose recipe pairs remain distinct",
    )
    check(
        "learned_doly_shell",
        context_by_surface["doly"]["old_context_recipe"]
        == context_by_surface["doly"]["new_context_recipe"]
        == "LOCAL_NAME_CORE_D+OL+Y",
        context_by_surface["doly"]["new_context_recipe"],
    )

    check(
        "local_tag_inventory",
        {row["local_tag"] for row in local_tags}
        == {"LOCAL_X", "LOCAL_C", "LOCAL_NAME_CORE_D", "LOCAL_NAME_CORE_YD"}
        and all(row["portable_value"] == "NONE" for row in local_tags),
        "four bounded local tags, no portable value",
    )
    open_by_surface = {row["surface"]: row for row in open_rows}
    check(
        "open_parse_surface_set",
        set(open_by_surface) == {"axor", "chxar", "cthdy", "okedam", "qocthedy", "ykady"},
        "|".join(sorted(open_by_surface)),
    )
    check(
        "local_x_unification",
        open_by_surface["axor"]["gdt516_recipe"] == "A_ADDR+LOCAL_X+OR"
        and open_by_surface["chxar"]["gdt516_recipe"] == "CH+LOCAL_X+AR",
        "axor/chxar share LOCAL_X",
    )
    check(
        "supported_open_parse_decisions",
        open_by_surface["cthdy"]["gdt516_recipe"] == "CH+T+D_ADDR+Y"
        and open_by_surface["okedam"]["gdt516_recipe"] == "OK+E+D_ADDR+AM_ADDR"
        and open_by_surface["qocthedy"]["gdt516_recipe"] == "CARRIER_Q+O+CH+T+E+Y",
        "cthdy/okedam/qocthedy retained with family evidence",
    )

    dy_summary_map = {row["category"]: row for row in dy_summary}
    check(
        "dy_ending_distribution",
        {
            category: (int(row["surface_type_count"]), int(row["event_count"]))
            for category, row in dy_summary_map.items()
        }
        == {
            "RECIPE_END_DY": (174, 695),
            "RECIPE_END_Y": (111, 385),
            "OTHER_OR_MIXED": (2, 2),
        },
        str({category: row["surface_type_count"] for category, row in dy_summary_map.items()}),
    )
    dy_relation_counts = Counter(row["recipe_relation"] for row in dy_pairs)
    check(
        "dy_y_pair_distribution",
        dy_relation_counts == {"SAME_RECIPE": 11, "DIFFERENT_RECIPE": 99},
        str(dict(dy_relation_counts)),
    )
    dy_by_surface = {row["dy_surface"]: row for row in dy_pairs}
    check(
        "critical_dy_pair_contrasts",
        dy_by_surface["cthdy"]["recipe_relation"] == "DIFFERENT_RECIPE"
        and dy_by_surface["qocthedy"]["recipe_relation"] == "SAME_RECIPE"
        and dy_by_surface["dy"]["recipe_relation"] == "SAME_RECIPE",
        "cthdy contrasts; qocthedy and dy allograph",
    )

    transition_by_pair = {row["ordered_pair"]: row for row in transitions}
    check(
        "action_transition_totals",
        sum(int(row["new_event_count"]) for row in transitions) == 90
        and sum(int(row["new_direct_adjacency_event_count"]) for row in transitions) == 45,
        "ordered=90 direct=45",
    )
    check(
        "new_order_chd_r",
        transition_by_pair["CHD>R"]["new_event_count"] == "2"
        and transition_by_pair["CHD>R"]["old_order_event_count"] == "0"
        and transition_by_pair["CHD>R"]["gdt427_negative_control_result"]
        == "FALSE_AMBER_ALLOWED"
        and transition_by_pair["CHD>R"]["new_surfaces"] == "chedaiir|fchedyr",
        str(transition_by_pair["CHD>R"]),
    )
    check(
        "new_direct_sh_s",
        transition_by_pair["SH>S"]["new_direct_adjacency_event_count"] == "1"
        and int(transition_by_pair["SH>S"]["old_order_event_count"]) > 0
        and transition_by_pair["SH>S"]["gdt421_pair_status"] == "PAIR_ATTESTED",
        str(transition_by_pair["SH>S"]),
    )
    check(
        "only_one_new_order_and_direct_adjacency",
        [
            row["ordered_pair"]
            for row in transitions
            if row["thirty_page_decision"].startswith("NEW_ORDER")
        ]
        == ["CHD>R"]
        and [
            row["ordered_pair"]
            for row in transitions
            if row["thirty_page_decision"]
            == "NEW_DIRECT_ADJACENCY__OLD_ORDER_ATTESTED"
        ]
        == ["SH>S"],
        "CHD>R order; SH>S direct adjacency",
    )

    input_event_projection = [
        (row["event_id"], row["surface"], row["visible_recipe"]) for row in event_input
    ]
    output_event_projection = [
        (row["event_id"], row["surface"], row["visible_recipe"]) for row in events
    ]
    check(
        "event_overlay_preserves_source",
        input_event_projection == output_event_projection,
        "597 original event ids, surfaces and recipes unchanged",
    )
    changed_events = Counter(
        row["surface"] for row in events if row["gdt516_recipe_changed"] == "YES"
    )
    check(
        "event_overlay_changed_set",
        changed_events == {"x": 3, "doly": 1, "c": 1, "axor": 1, "chxar": 1},
        str(dict(changed_events)),
    )

    input_unified_projection = [
        (row["global_group_id"], row["surface"], row["component_recipe"])
        for row in unified30
    ]
    output_unified_projection = [
        (row["global_group_id"], row["surface"], row["component_recipe"])
        for row in unified
    ]
    check(
        "unified_overlay_preserves_source",
        input_unified_projection == output_unified_projection,
        "5866 original groups retained in order",
    )
    changed_unified = Counter(
        row["surface"] for row in unified if row["gdt516_recipe_changed"] == "YES"
    )
    check(
        "unified_overlay_changed_set",
        changed_unified
        == {
            "x": 3,
            "doly": 2,
            "saiir": 1,
            "chekey": 1,
            "okyd": 1,
            "c": 1,
            "axor": 1,
            "chxar": 1,
        },
        str(dict(changed_unified)),
    )

    dictionary_atoms = {row["atom"] for row in dictionary_rows}
    local_atom_set = {row["local_tag"] for row in local_tags}
    overlay_atoms = {
        atom
        for row in unified
        for atom in atoms(row["gdt516_context_recipe"])
    }
    original_atoms = {
        atom
        for row in unified30
        for atom in atoms(row["component_recipe"])
    }
    check(
        "overlay_atom_inventory_bounded",
        overlay_atoms <= dictionary_atoms | local_atom_set | original_atoms,
        str(sorted(overlay_atoms - dictionary_atoms - local_atom_set - original_atoms)),
    )
    check(
        "no_forbidden_page_material",
        not any(
            row["physical_page"].startswith("f84")
            for row in events + unified
        ),
        "f84/f84r absent from overlays",
    )

    result_compression = result["family_compression"]
    check(
        "result_family_metrics_match",
        result_compression["exact_old_complete_recipe_carriers"] == 10
        and result_compression["nonexact_surfaces_with_old_complete_recipe_fragment"] == 120
        and result_compression["fully_tiled_by_old_multicomponent_recipes"] == 39
        and result_compression["covered_recipe_atoms"] == 426
        and result_compression["total_recipe_atoms"] == 643,
        str(result_compression),
    )
    check(
        "result_context_metrics_match",
        result["context_policy"]
        == {
            "common_recipe_promotions": 2,
            "exact_agreements": 3,
            "learned_label_shell_replays": 1,
            "local_tags": 4,
            "new_portable_values": 0,
            "old_local_new_context_contacts": 10,
            "role_conditioned_homographs": 4,
        },
        str(result["context_policy"]),
    )
    check(
        "status_and_guard",
        result["status"] == "PASS_NEW_FORMS_COMPRESSED_WITH_FINITE_CONTEXT_POLICY"
        and all(
            row["guard"]
            == "EXPLORATORY_WORKING_COMPOSITION__NO_CONFIRMED_LEXEME_OR_PLAINTEXT"
            for row in family + context + open_rows + local_tags + dy_pairs + transitions
        ),
        result["status"],
    )

    passed = all(row["passed"] for row in checks)
    payload = {
        "experiment_id": "GDT516",
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(row["passed"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "input_hashes": {
            "gdt515_new": sha256(G515 / "gdt515_159_genuinely_new_surface_audit.tsv"),
            "gdt515_events": sha256(G515 / "gdt515_597_complete_event_edition.tsv"),
            "gdt515_running30": sha256(G515 / "gdt515_5122_running_event_edition.tsv"),
            "gdt515_unified30": sha256(G515 / "gdt515_5866_unified_group_ledger.tsv"),
            "gdt407_old_running": sha256(G407 / "gdt407_4576_running_event_edition.tsv"),
            "gdt413_dictionary": sha256(G413 / "gdt413_46_component_working_dictionary.tsv"),
        },
    }
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
