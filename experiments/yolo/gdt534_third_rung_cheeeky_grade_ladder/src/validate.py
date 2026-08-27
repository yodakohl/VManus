#!/usr/bin/env python3
"""Independently validate GDT534's cheeeky grade-ladder revision."""

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
BASE = ROOT / "experiments/yolo/gdt534_third_rung_cheeeky_grade_ladder"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt534_validation.json"
OLD = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
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


def invariant_inventory(rows: list[dict[str, str]]) -> dict[str, dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["surface"]].append(row)
    return {
        surface: {"recipe": next(iter(recipes)), "rows": surface_rows}
        for surface, surface_rows in grouped.items()
        if len(recipes := {row["component_recipe"] for row in surface_rows}) == 1
    }


def transition(left: str, right: str) -> tuple[str, int] | None:
    a = left.split("+")
    b = right.split("+")
    if len(a) != len(b):
        return None
    changed = [index for index in range(len(a)) if a[index] != b[index]]
    if len(changed) != 1:
        return None
    index = changed[0]
    if (a[index], b[index]) == ("E", "EE"):
        return "E_TO_EE", index
    if (a[index], b[index]) == ("EE", "EEE"):
        return "EE_TO_EEE", index
    return None


def independent_pairs(inventory: dict[str, dict]) -> set[tuple[str, str, str, str, str, int]]:
    pairs = set()
    for extended_surface, extended in inventory.items():
        bases = {
            extended_surface[:index] + extended_surface[index + 1 :]
            for index, char in enumerate(extended_surface)
            if char == "e"
        }
        for base_surface in bases & inventory.keys():
            base = inventory[base_surface]
            step = transition(base["recipe"], extended["recipe"])
            if step:
                pairs.add(
                    (
                        base_surface,
                        extended_surface,
                        base["recipe"],
                        extended["recipe"],
                        step[0],
                        step[1] + 1,
                    )
                )
    return pairs


def independent_ladders(
    pairs: set[tuple[str, str, str, str, str, int]],
) -> set[tuple[str, str, str, str, str, str, int]]:
    low = [row for row in pairs if row[4] == "E_TO_EE"]
    high = [row for row in pairs if row[4] == "EE_TO_EEE"]
    return {
        (first[0], first[1], second[1], first[2], first[3], second[3], first[5])
        for first in low
        for second in high
        if first[1] == second[0]
        and first[3] == second[2]
        and first[5] == second[5]
    }


def main() -> int:
    result = json.loads((OUT / "gdt534_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt534_159_working_revision.tsv")
    pair_atlas = read_tsv(OUT / "gdt534_old_grade_step_pair_atlas.tsv")
    ladder_atlas = read_tsv(OUT / "gdt534_complete_grade_ladder_atlas.tsv")
    family = read_tsv(OUT / "gdt534_cheky_family_ladder.tsv")
    contexts = read_tsv(OUT / "gdt534_cheky_family_contexts.tsv")
    long_e = read_tsv(OUT / "gdt534_long_e_renderer_context_control.tsv")
    comparison = read_tsv(OUT / "gdt534_dalcheeeky_candidate_comparison.tsv")
    certificate = read_tsv(OUT / "gdt534_target_composition_certificate.tsv")
    block = read_tsv(OUT / "gdt534_target_owner_block_atlas.tsv")
    unresolved = read_tsv(OUT / "gdt534_remaining_unresolved_atlas.tsv")
    old = read_tsv(OLD)
    source_candidates = read_tsv(CANDIDATES)
    inventory = invariant_inventory(old)
    pairs = independent_pairs(inventory)
    ladders = independent_ladders(pairs)
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_THIRD_RUNG_cheeeky_WORKING_REVISION",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_LOCAL_K_GRADE_FAMILY_COMPLETION__NO_GLOBAL_cheee_PARSE__NO_CONFIRMED_LEXEME_OR_PLAINTEXT",
        result["claim_ceiling"],
    )
    check("old_event_count", len(old) == 4576, len(old))
    check("edition_count", len(edition) == 159, len(edition))
    check(
        "edition_unique", len({row["surface"] for row in edition}) == 159, len(edition)
    )
    changed = [
        row
        for row in edition
        if row["gdt533_working_recipe"] != row["gdt534_working_recipe"]
    ]
    check(
        "one_working_change",
        len(changed) == 1 and changed[0]["surface"] == "dalcheeeky",
        [row["surface"] for row in changed],
    )
    selected = changed[0]
    check(
        "selected_recipe",
        selected["gdt533_working_recipe"] == "AL+CH+EEE+K+Y"
        and selected["gdt533_candidate_rank"] == "2"
        and selected["gdt534_working_recipe"] == "AL+CH+K+EEE+Y"
        and selected["gdt534_candidate_rank"] == "UNGENERATED"
        and selected["gdt534_candidate_space_status"] == "OUTSIDE_GDT529_FINITE_SET",
        selected,
    )
    check(
        "selected_reading",
        selected["gdt534_short_phrase_de"]
        == "Am Zielort nehmen und geben; auf Grad III posten."
        and selected["gdt534_literal_reading_de"]
        == "ZIELORT · NEHMEN · GEBEN · [EEE:STEUERUNG=GRAD III] · POSTEN",
        selected["gdt534_short_phrase_de"],
    )
    check(
        "selected_resolution",
        selected["gdt534_resolution_status"]
        == "RESOLVED_BY_THIRD_GRADE_FAMILY_COMPLETION",
        selected["gdt534_resolution_status"],
    )

    source_target_candidates = {
        (row["candidate_recipe"], row["gdt529_rank"])
        for row in source_candidates
        if row["surface"] == "dalcheeeky"
    }
    check("source_candidate_count", len(source_target_candidates) == 12, len(source_target_candidates))
    check(
        "selected_outside_source_candidates",
        all(recipe != "AL+CH+K+EEE+Y" for recipe, _ in source_target_candidates),
        sorted(source_target_candidates, key=lambda item: int(item[1])),
    )
    generated = [row for row in comparison if row["candidate_space_status"] == "GENERATED"]
    outside = [
        row
        for row in comparison
        if row["candidate_space_status"] == "OUTSIDE_GDT529_FINITE_SET"
    ]
    check(
        "comparison_space_accounting",
        len(comparison) == 13 and len(generated) == 12 and len(outside) == 1,
        {"all": len(comparison), "generated": len(generated), "outside": len(outside)},
    )
    check(
        "generated_candidates_exact",
        {(row["candidate_recipe"], row["gdt529_rank"]) for row in generated}
        == source_target_candidates,
        len(generated),
    )
    check(
        "outside_candidate_selected",
        outside[0]["candidate_recipe"] == "AL+CH+K+EEE+Y"
        and outside[0]["matches_exact_cheky_grade_frame"] == "YES"
        and outside[0]["decision"] == "SELECT_THIRD_RUNG_FAMILY_COMPLETION",
        outside[0],
    )

    check("independent_pair_count", len(pairs) == 57, len(pairs))
    independent_counts = Counter(row[4] for row in pairs)
    check(
        "independent_pair_steps",
        independent_counts == Counter({"E_TO_EE": 49, "EE_TO_EEE": 8}),
        dict(independent_counts),
    )
    artifact_pairs = {
        (
            row["base_surface"],
            row["extended_surface"],
            row["base_recipe"],
            row["extended_recipe"],
            row["grade_step"],
            int(row["grade_atom_ordinal"]),
        )
        for row in pair_atlas
    }
    check("pair_atlas_exact", artifact_pairs == pairs, len(artifact_pairs))
    check(
        "cheky_pair_exact",
        (
            "cheky",
            "cheeky",
            "CH+K+E+Y",
            "CH+K+EE+Y",
            "E_TO_EE",
            3,
        )
        in pairs,
        "cheky -> cheeky",
    )

    check("independent_ladder_count", len(ladders) == 5, len(ladders))
    artifact_ladders = {
        (
            row["rung_I_surface"],
            row["rung_II_surface"],
            row["rung_III_surface"],
            row["rung_I_recipe"],
            row["rung_II_recipe"],
            row["rung_III_recipe"],
            int(row["grade_atom_ordinal"]),
        )
        for row in ladder_atlas
    }
    check("ladder_atlas_exact", artifact_ladders == ladders, len(artifact_ladders))
    visible_ladders = {
        (row[0], row[1], row[2]) for row in ladders
    }
    check(
        "five_expected_complete_ladders",
        visible_ladders
        == {
            ("okey", "okeey", "okeeey"),
            ("qokedy", "qokeedy", "qokeeedy"),
            ("qokey", "qokeey", "qokeeey"),
            ("qotedy", "qoteedy", "qoteeedy"),
            ("tey", "teey", "teeey"),
        },
        sorted(visible_ladders),
    )

    family_by_rung = {row["rung"]: row for row in family}
    check("family_rung_count", len(family) == 3, len(family))
    check(
        "family_observed_rungs",
        family_by_rung["I"]["surface_or_embedded_stem"] == "cheky"
        and family_by_rung["I"]["recipe"] == "CH+K+E+Y"
        and family_by_rung["I"]["old_event_count"] == "9"
        and family_by_rung["II"]["surface_or_embedded_stem"] == "cheeky"
        and family_by_rung["II"]["recipe"] == "CH+K+EE+Y"
        and family_by_rung["II"]["old_event_count"] == "5",
        family_by_rung,
    )
    check(
        "family_predicted_third_rung",
        family_by_rung["III"]["surface_or_embedded_stem"] == "cheeeky"
        and family_by_rung["III"]["recipe"] == "CH+K+EEE+Y"
        and family_by_rung["III"]["current_event_id"] == "G515-E0423"
        and family_by_rung["III"]["status"] == "WORKING_FAMILY_COMPLETION",
        family_by_rung["III"],
    )
    check(
        "family_context_counts",
        len(contexts) == 14
        and Counter(row["surface"] for row in contexts)
        == Counter({"cheky": 9, "cheeky": 5}),
        dict(Counter(row["surface"] for row in contexts)),
    )
    check(
        "family_cross_register",
        {row["register"] for row in contexts}
        == {"HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA"},
        sorted({row["register"] for row in contexts}),
    )

    prefix = inventory["dal"]
    check(
        "exact_dal_prefix",
        prefix["recipe"] == "AL" and len(prefix["rows"]) == 44,
        {"recipe": prefix["recipe"], "events": len(prefix["rows"])},
    )
    check(
        "composition_certificate",
        len(certificate) == 2
        and certificate[0]["surface_piece"] == "dal"
        and certificate[0]["recipe_piece"] == "AL"
        and certificate[0]["old_event_count"] == "44"
        and certificate[1]["surface_piece"] == "cheeeky"
        and certificate[1]["recipe_piece"] == "CH+K+EEE+Y",
        certificate,
    )

    long_by_surface = {row["surface"]: row for row in long_e}
    check(
        "global_cheee_control_retained",
        long_by_surface["cheeety"]["recipe"] == "EEE+T+Y"
        and long_by_surface["cheeety"]["contains_CH_atom"] == "NO",
        long_by_surface["cheeety"],
    )
    check(
        "target_local_frame_distinct",
        long_by_surface["dalcheeeky"]["recipe"] == "AL+CH+K+EEE+Y"
        and long_by_surface["dalcheeeky"]["relation"]
        == "TARGET_LOCAL_cheeeky_K_GRADE_FAMILY",
        long_by_surface["dalcheeeky"],
    )

    check("target_block_count", len(block) == 37, len(block))
    target_block = [row for row in block if row["relation"] == "TARGET"]
    check(
        "target_event_exact",
        len(target_block) == 1
        and target_block[0]["event_id"] == "G515-E0423"
        and target_block[0]["locus"] == "f66r.64"
        and target_block[0]["statement_id"] == "G515-S047"
        and target_block[0]["card_ordinal_in_statement"] == "10"
        and target_block[0]["gdt516_context_recipe"] == "AL+CH+EEE+K+Y",
        target_block,
    )
    check(
        "target_statement_count",
        sum(row["statement_id"] == "G515-S047" for row in block) == 12,
        Counter(row["statement_id"] for row in block),
    )

    inherited = result["inherited_gdt533_candidate_metrics"]
    in_space = result["gdt534_in_space_candidate_metrics"]
    check(
        "inherited_metrics",
        inherited["target_count"] == 159
        and inherited["top1_exact_count"] == 155
        and inherited["top2_exact_count"] == 157
        and inherited["rank_sum"] == 174,
        inherited,
    )
    check(
        "in_space_metrics",
        in_space["target_count"] == 158
        and in_space["top1_exact_count"] == 155
        and in_space["top2_exact_count"] == 156
        and in_space["rank_sum"] == 172,
        in_space,
    )
    check(
        "unresolved_queue",
        len(unresolved) == 2
        and [row["surface"] for row in unresolved] == ["aiicthy", "qef"]
        and result["remaining_unresolved_surfaces"] == ["aiicthy", "qef"],
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

    aligned = align("dalcheeeky", "G515-E0423", "f66r")
    check(
        "executable_target_revision",
        aligned["gdt533_default_selection"] == "AL+CH+EEE+K+Y"
        and aligned["default_selection"] == "AL+CH+K+EEE+Y"
        and aligned["grade_ladder_certificate"]["candidate_rank"] == "UNGENERATED"
        and aligned["grade_ladder_certificate"]["complete_old_three_rung_ladder_count"] == 5,
        aligned,
    )
    dairykodas = align("dairykodas", "G515-E0364", "f66r")
    check(
        "gdt533_dairykodas_revision_preserved",
        dairykodas["default_selection"] == "D_ADDR+AIR+Y+K+O+DA+S"
        and dairykodas["working_revision"] == "D_ADDR+AIR+Y+K+O+DA+S"
        and dairykodas["grade_ladder_certificate"] == "NONE",
        dairykodas["default_selection"],
    )
    dshold = align("dsholdaiir", "G515-E0366", "f66r")
    check(
        "gdt532_dsholdaiir_revision_preserved",
        dshold["default_selection"] == "D_ADDR+SH+OL+DA+IIN+R"
        and dshold["working_revision"] == "D_ADDR+SH+OL+DA+IIN+R",
        dshold["default_selection"],
    )
    saiis = align("saiis", "G515-E0243", "f31r")
    check(
        "gdt531_saiis_revision_preserved",
        saiis["default_selection"] == "S+A_ADDR+IIN+S"
        and saiis["working_revision"] == "S+A_ADDR+IIN+S",
        saiis["default_selection"],
    )
    check(
        "no_new_page_guard",
        result["guard"].endswith("NO_NEW_PAGES"),
        result["guard"],
    )

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    validation = {
        "experiment_id": "GDT534",
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
