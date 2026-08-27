#!/usr/bin/env python3
"""Independently validate GDT533's nested odas-tail revision."""

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
BASE = ROOT / "experiments/yolo/gdt533_nested_odas_tail_revision"
OUT = BASE / "artifacts"
VALIDATION = OUT / "gdt533_validation.json"
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
    result = json.loads((OUT / "gdt533_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt533_159_working_revision.tsv")
    comparison = read_tsv(OUT / "gdt533_dairykodas_candidate_comparison.tsv")
    tiles = read_tsv(OUT / "gdt533_dairykodas_exact_card_certificate.tsv")
    nested = read_tsv(OUT / "gdt533_nested_das_odas_atlas.tsv")
    pairs = read_tsv(OUT / "gdt533_candidate_pair_support_atlas.tsv")
    as_endings = read_tsv(OUT / "gdt533_old_as_ending_control.tsv")
    statement = read_tsv(OUT / "gdt533_target_statement_atlas.tsv")
    unresolved = read_tsv(OUT / "gdt533_remaining_unresolved_atlas.tsv")
    old = read_tsv(OLD)
    signatures = read_tsv(SIGNATURES)
    candidate_rows = read_tsv(CANDIDATES)
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_NESTED_ODAS_TAIL_WORKING_REVISION",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_NESTED_EXACT_TERMINAL_WHOLE_CARD_REVISION__NO_GLOBAL_ODAS_OR_AS_SUFFIX",
        result["claim_ceiling"],
    )
    check("edition_count", len(edition) == 159, len(edition))
    check(
        "edition_unique", len({row["surface"] for row in edition}) == 159, len(edition)
    )
    changed = [
        row
        for row in edition
        if row["gdt532_working_recipe"] != row["gdt533_working_recipe"]
    ]
    check(
        "one_working_change",
        len(changed) == 1 and changed[0]["surface"] == "dairykodas",
        [row["surface"] for row in changed],
    )
    selected = changed[0]
    check(
        "selected_recipe_and_rank",
        selected["gdt532_working_recipe"]
        == "D_ADDR+AIR+Y+K+O+D_ADDR+A_ADDR+S"
        and selected["gdt532_candidate_rank"] == "2"
        and selected["gdt533_working_recipe"] == "D_ADDR+AIR+Y+K+O+DA+S"
        and selected["gdt533_candidate_rank"] == "1",
        selected,
    )
    check(
        "selected_reading",
        selected["gdt533_short_phrase_de"]
        == "Hier entlang der Bahn posten; zur Ausführung geben und Stufe II wählen."
        and "DA+S:STEUERUNG=STUFE II WÄHLEN" in selected["gdt533_literal_reading_de"],
        selected["gdt533_short_phrase_de"],
    )
    check(
        "selected_resolution",
        selected["gdt533_resolution_status"]
        == "RESOLVED_BY_NESTED_EXACT_TERMINAL_WHOLE_CARD",
        selected["gdt533_resolution_status"],
    )

    check("comparison_count", len(comparison) == 12, len(comparison))
    comparison_by_rank = {row["gdt529_rank"]: row for row in comparison}
    check(
        "only_two_tileable_candidates",
        comparison_by_rank["1"]["exact_card_tiling_route_count"] == "4"
        and comparison_by_rank["2"]["exact_card_tiling_route_count"] == "8"
        and all(
            row["exact_card_tiling_route_count"] == "0"
            for rank, row in comparison_by_rank.items()
            if rank not in {"1", "2"}
        ),
        {rank: row["exact_card_tiling_route_count"] for rank, row in comparison_by_rank.items()},
    )
    check(
        "selected_and_rival_tilings",
        comparison_by_rank["1"]["preferred_surface_tiling"] == "dair|y|k|odas"
        and comparison_by_rank["1"]["preserves_exact_terminal_odas"] == "YES"
        and comparison_by_rank["1"]["nested_das_odas_certificate"] == "YES"
        and comparison_by_rank["2"]["preferred_surface_tiling"] == "dair|y|kod|as"
        and comparison_by_rank["2"]["preserves_exact_terminal_odas"] == "NO",
        {"rank1": comparison_by_rank["1"], "rank2": comparison_by_rank["2"]},
    )
    source_candidates = {
        (row["candidate_recipe"], row["gdt529_rank"])
        for row in candidate_rows
        if row["surface"] == "dairykodas"
    }
    check(
        "candidate_ranks_exact_source",
        all((row["candidate_recipe"], row["gdt529_rank"]) in source_candidates for row in comparison),
        len(source_candidates),
    )

    old_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old:
        old_by_surface[row["surface"]].append(row)
    check("tile_certificate_count", len(tiles) == 8, len(tiles))
    check(
        "tile_route_orders",
        [row["tile_surface"] for row in tiles if row["route"] == "SELECTED_NESTED_ODAS"]
        == ["dair", "y", "k", "odas"]
        and [row["tile_surface"] for row in tiles if row["route"] == "RIVAL_KOD_AS"]
        == ["dair", "y", "kod", "as"],
        [(row["route"], row["tile_surface"]) for row in tiles],
    )
    tile_integrity = True
    for row in tiles:
        source = old_by_surface[row["tile_surface"]]
        tile_integrity &= (
            len(source) == int(row["old_event_count"])
            and {item["component_recipe"] for item in source} == {row["tile_recipe"]}
        )
    check("all_tile_cards_exact", tile_integrity, "8/8")
    selected_counts = {
        row["tile_surface"]: int(row["old_event_count"])
        for row in tiles
        if row["route"] == "SELECTED_NESTED_ODAS"
    }
    check(
        "selected_card_counts",
        selected_counts == {"dair": 9, "y": 39, "k": 4, "odas": 1},
        selected_counts,
    )

    check("nested_atlas_count", len(nested) == 2, len(nested))
    nested_by_surface = {row["surface"]: row for row in nested}
    check(
        "nested_exact_cards",
        nested_by_surface["das"]["recipe"] == "DA+S"
        and nested_by_surface["das"]["old_event_count"] == "1"
        and nested_by_surface["odas"]["recipe"] == "O+DA+S"
        and nested_by_surface["odas"]["old_event_count"] == "1"
        and nested_by_surface["odas"]["visible_derivation"] == "odas-o=das"
        and nested_by_surface["odas"]["recipe_derivation"] == "O+DA+S-O=DA+S",
        nested_by_surface,
    )
    source_signature = next(
        row
        for row in signatures
        if row["visible_insert"] == "o"
        and row["visible_position"] == "LEFT"
        and row["atom_insert"] == "O"
        and row["atom_position"] == "LEFT"
    )
    check(
        "left_o_O_signature",
        source_signature["support_pair_count"] == "31"
        and source_signature["visible_condition_total"] == "37"
        and source_signature["conditional_probability"] == "0.797468354"
        and source_signature["reliability"] == "0.939393939"
        and nested_by_surface["odas"]["left_o_O_support"] == "31"
        and nested_by_surface["odas"]["left_o_O_reliability"] == "0.939393939",
        source_signature,
    )

    check("pair_atlas_count", len(pairs) == 13, len(pairs))
    pair_counts = {
        (row["route"], row["pair"]): int(row["occurrence_count"])
        for row in pairs
    }
    check(
        "selected_pair_counts",
        [
            pair_counts[("SELECTED_RANK1", pair)]
            for pair in ["D_ADDR+AIR", "AIR+Y", "Y+K", "K+O", "O+DA", "DA+S"]
        ]
        == [16, 2, 69, 21, 6, 2],
        {"|".join(key): value for key, value in pair_counts.items() if key[0] == "SELECTED_RANK1"},
    )
    check(
        "rival_pair_counts",
        [
            pair_counts[("RIVAL_RANK2", pair)]
            for pair in [
                "D_ADDR+AIR",
                "AIR+Y",
                "Y+K",
                "K+O",
                "O+D_ADDR",
                "D_ADDR+A_ADDR",
                "A_ADDR+S",
            ]
        ]
        == [16, 2, 69, 21, 114, 1, 9],
        {"|".join(key): value for key, value in pair_counts.items() if key[0] == "RIVAL_RANK2"},
    )
    check(
        "critical_pair_contrast",
        pair_counts[("SELECTED_RANK1", "DA+S")] == 2
        and pair_counts[("RIVAL_RANK2", "D_ADDR+A_ADDR")] == 1
        and result["selected_pair_minimum_support"] == 2
        and result["rival_pair_minimum_support"] == 1,
        result["critical_pair_support"],
    )

    check("as_ending_count", len(as_endings) == 6, len(as_endings))
    as_by_surface = {row["surface"]: row for row in as_endings}
    check(
        "as_ending_is_contextual",
        {row["ends_A_ADDR_S"] for row in as_endings} == {"YES", "NO"}
        and as_by_surface["as"]["recipes"] == "A_ADDR+S"
        and as_by_surface["odas"]["recipes"] == "O+DA+S"
        and as_by_surface["das"]["recipes"] == "DA+S"
        and as_by_surface["okeeas"]["recipes"] == "OK+EE+Y",
        as_by_surface,
    )
    check("statement_count", len(statement) == 22, len(statement))
    target_statement_rows = [row for row in statement if row["relation"] == "TARGET"]
    check(
        "target_statement_exact",
        len(target_statement_rows) == 1
        and target_statement_rows[0]["event_id"] == "G515-E0364"
        and target_statement_rows[0]["locus"] == "f66r.57"
        and target_statement_rows[0]["card_ordinal_in_statement"] == "7",
        target_statement_rows,
    )

    previous = result["previous_candidate_agreement_metrics"]
    revised = result["gdt533_candidate_agreement_metrics"]
    check(
        "previous_metrics",
        previous["top1_exact_count"] == 154
        and previous["top2_exact_count"] == 157
        and previous["rank_sum"] == 175,
        previous,
    )
    check(
        "revised_metrics",
        revised["top1_exact_count"] == 155
        and revised["top2_exact_count"] == 157
        and revised["rank_sum"] == 174,
        revised,
    )
    check(
        "one_rank_improvement_no_other_change",
        sum(
            int(row["gdt533_candidate_rank"]) < int(row["gdt532_candidate_rank"])
            for row in edition
        )
        == 1
        and all(
            int(row["gdt533_candidate_rank"]) <= int(row["gdt532_candidate_rank"])
            for row in edition
        ),
        "dairykodas 2->1",
    )
    check(
        "unresolved_queue",
        len(unresolved) == 3
        and [row["surface"] for row in unresolved]
        == ["aiicthy", "dalcheeeky", "qef"]
        and result["remaining_unresolved_surfaces"]
        == ["aiicthy", "dalcheeeky", "qef"],
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

    aligned = align("dairykodas", "G515-E0364", "f66r")
    check(
        "executable_dairykodas_revision",
        aligned["gdt532_default_selection"]
        == "D_ADDR+AIR+Y+K+O+D_ADDR+A_ADDR+S"
        and aligned["default_selection"] == "D_ADDR+AIR+Y+K+O+DA+S"
        and aligned["nested_odas_certificate"]["surface_tiling"]
        == "dair|y|k|odas"
        and aligned["nested_odas_certificate"]["candidate_rank"] == 1,
        aligned,
    )
    dshold = align("dsholdaiir", "G515-E0366", "f66r")
    check(
        "gdt532_dsholdaiir_revision_preserved",
        dshold["default_selection"] == "D_ADDR+SH+OL+DA+IIN+R"
        and dshold["working_revision"] == "D_ADDR+SH+OL+DA+IIN+R"
        and dshold["nested_odas_certificate"] == "NONE",
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
        "experiment_id": "GDT533",
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
