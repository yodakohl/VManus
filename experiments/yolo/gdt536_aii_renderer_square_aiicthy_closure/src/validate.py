#!/usr/bin/env python3
"""Independently validate GDT536's aii renderer-square closure."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt536_aii_renderer_square_aiicthy_closure"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION = OUT / "gdt536_validation.json"
OLD = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
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
PREVIOUS = (
    ROOT
    / "experiments/yolo/gdt535_same_statement_q_null_qef_closure/artifacts"
    / "gdt535_159_working_revision.tsv"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def snapshot() -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.iterdir())
        if path.is_file() and path != VALIDATION
    }


def main() -> int:
    before = snapshot()
    replay = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    after = snapshot()

    result = json.loads((OUT / "gdt536_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt536_159_working_revision.tsv")
    square = read_tsv(OUT / "gdt536_aii_renderer_square.tsv")
    terminal = read_tsv(OUT / "gdt536_terminal_n_pair_control.tsv")
    prefixes = read_tsv(OUT / "gdt536_s_prefix_pair_control.tsv")
    cthy = read_tsv(OUT / "gdt536_cthy_exact_carriers.tsv")
    contexts = read_tsv(OUT / "gdt536_aii_context_control.tsv")
    page = read_tsv(OUT / "gdt536_f31r_aii_family_atlas.tsv")
    comparison = read_tsv(OUT / "gdt536_aiicthy_candidate_comparison.tsv")
    certificate = read_tsv(OUT / "gdt536_aiicthy_resolution_certificate.tsv")
    unresolved = read_tsv(OUT / "gdt536_remaining_unresolved_atlas.tsv")
    old = read_tsv(OLD)
    current_events = read_tsv(CURRENT_EVENTS)
    candidate_source = [
        row for row in read_tsv(CANDIDATES) if row["surface"] == "aiicthy"
    ]
    previous = read_tsv(PREVIOUS)

    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old:
        by_surface[row["surface"]].append(row)

    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check("runner_exit", replay.returncode == 0, replay.stderr[-1000:])
    check("byte_identical_replay", before == after, {"before": before, "after": after})
    check(
        "result_status",
        result["status"] == "PASS_AII_RENDERER_SQUARE_aiicthy_CLOSURE",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_FAMILY_SPECIFIC_AII_VALUE_RENDERER_AND_COMPOSITIONAL_CLOSURE__NO_GLOBAL_AII_OR_N_NULL_RULE_OR_CONFIRMED_PLAINTEXT",
        result["claim_ceiling"],
    )
    check("source_counts", len(old) == 4576 and len(by_surface) == 1558, [len(old), len(by_surface)])
    check("current_counts", len(current_events) == 597 and len(previous) == 159, [len(current_events), len(previous)])

    expected_profiles = {
        "aiin": Counter({"AIIN": 55}),
        "saiin": Counter({"S+AIIN": 20}),
        "saii": Counter({"S+AIIN": 1}),
        "cthy": Counter({"CH+T+Y": 13}),
    }
    for surface, expected in expected_profiles.items():
        actual = Counter(row["component_recipe"] for row in by_surface[surface])
        check(f"old_profile_{surface}", actual == expected, dict(actual))
    check("old_aii_missing", "aii" not in by_surface, len(by_surface.get("aii", [])))

    square_by_cell = {row["cell"]: row for row in square}
    check("square_four_cells", len(square) == 4 and len(square_by_cell) == 4, list(square_by_cell))
    check(
        "square_three_observed",
        sum(row["cell_state"] == "OBSERVED_OLD_EXACT" for row in square) == 3,
        [row["cell_state"] for row in square],
    )
    inferred = square_by_cell.get("BASE_MINUS_N", {})
    check(
        "square_inferred_aii",
        inferred.get("surface") == "aii"
        and inferred.get("working_recipe") == "AIIN"
        and inferred.get("event_count") == "0",
        inferred,
    )

    check("terminal_pair_count", len(terminal) == 3, len(terminal))
    same_terminal = [row for row in terminal if row["same_recipe"] == "YES"]
    check(
        "unique_same_recipe_terminal_pair",
        len(same_terminal) == 1
        and same_terminal[0]["long_surface"] == "saiin"
        and same_terminal[0]["short_surface"] == "saii"
        and same_terminal[0]["common_recipes"] == "S+AIIN",
        same_terminal,
    )
    check(
        "terminal_controls_retained",
        {(row["long_surface"], row["short_surface"], row["same_recipe"]) for row in terminal}
        == {("chtaiin", "chtaii", "NO"), ("dn", "d", "NO"), ("saiin", "saii", "YES")},
        terminal,
    )

    prefix_hits = [row for row in prefixes if row["literal_s_prefix_match"] == "YES"]
    check("s_prefix_control_counts", len(prefixes) == 47 and len(prefix_hits) == 25, [len(prefixes), len(prefix_hits)])
    aiin_prefix = [row for row in prefixes if row["base_surface"] == "aiin"]
    check(
        "aiin_s_prefix_edge",
        len(aiin_prefix) == 1
        and aiin_prefix[0]["prefixed_surface"] == "saiin"
        and aiin_prefix[0]["matching_recipes"] == "S+AIIN",
        aiin_prefix,
    )

    check("cthy_carrier_count", len(cthy) == 13, len(cthy))
    check(
        "cthy_carrier_invariance",
        {row["surface"] for row in cthy} == {"cthy"}
        and {row["recipe"] for row in cthy} == {"CH+T+Y"}
        and len({row["physical_page"] for row in cthy}) == 6,
        sorted({row["physical_page"] for row in cthy}),
    )

    old_contexts = [row for row in contexts if row["corpus"] == "OLD26"]
    current_contexts = [row for row in contexts if row["corpus"] == "CURRENT_NEW159"]
    check("aii_context_counts", len(old_contexts) == 19 and len(current_contexts) == 7, [len(old_contexts), len(current_contexts)])
    check(
        "aii_contexts_remain_diverse",
        len({row["invariant_recipe"] for row in old_contexts + current_contexts}) > 10,
        len({row["invariant_recipe"] for row in old_contexts + current_contexts}),
    )

    check("f31r_family_count", len(page) == 15, len(page))
    check(
        "f31r_aiin_counts",
        sum(row["surface"] == "aiin" and row["live_working_recipe"] == "AIIN" for row in page) == 4
        and sum(row["surface"] == "daiin" and row["live_working_recipe"] == "AIIN" for row in page) == 4,
        sorted(
            (surface, recipe, count)
            for (surface, recipe), count in Counter(
                (row["surface"], row["live_working_recipe"]) for row in page
            ).items()
        ),
    )
    target_page = [row for row in page if row["event_id"] == "G515-E0253"]
    check(
        "target_page_selection",
        len(target_page) == 1
        and target_page[0]["surface"] == "aiicthy"
        and target_page[0]["live_working_recipe"] == "AIIN+CH+T+Y",
        target_page,
    )

    check("candidate_count", len(candidate_source) == 12 and len(comparison) == 12, [len(candidate_source), len(comparison)])
    matches = [row for row in comparison if row["matches_both_blocks"] == "YES"]
    check(
        "unique_candidate_match",
        len(matches) == 1
        and matches[0]["candidate_recipe"] == "AIIN+CH+T+Y"
        and matches[0]["gdt529_rank"] == "1",
        matches,
    )
    check("certificate_six_steps", len(certificate) == 6 and [row["step"] for row in certificate] == [str(i) for i in range(1, 7)], certificate)

    check("edition_count_unique", len(edition) == 159 and len({row["surface"] for row in edition}) == 159, len(edition))
    changes = [row for row in edition if row["gdt535_working_recipe"] != row["gdt536_working_recipe"]]
    check("one_recipe_change", len(changes) == 1 and changes[0]["surface"] == "aiicthy", [row["surface"] for row in changes])
    target = changes[0] if changes else {}
    check(
        "target_recipe_and_rank",
        target.get("gdt536_working_recipe") == "AIIN+CH+T+Y"
        and target.get("gdt536_gdt529_candidate_rank") == "1"
        and target.get("gdt536_renderer_square_rank") == "1",
        target,
    )
    check(
        "target_reading",
        target.get("gdt536_literal_reading_de") == "WERT · NEHMEN · EINSTELLEN · POSTEN"
        and target.get("gdt536_short_phrase_de") == "Den Wert nehmen, einstellen und posten.",
        target.get("gdt536_short_phrase_de"),
    )
    check(
        "target_resolution",
        target.get("gdt536_resolution_status") == "RESOLVED_BY_AII_RENDERER_SQUARE_AND_EXACT_CTHY",
        target.get("gdt536_resolution_status"),
    )
    inherited = [row for row in edition if row["surface"] != "aiicthy"]
    check(
        "all_other_recipes_inherited",
        all(row["gdt535_working_recipe"] == row["gdt536_working_recipe"] for row in inherited),
        len(inherited),
    )
    check("zero_unresolved_rows", unresolved == [], len(unresolved))
    check(
        "result_complete",
        result["working_resolved_surface_count"] == 159
        and result["remaining_unresolved_surface_count"] == 0
        and result["remaining_unresolved_surfaces"] == [],
        result["remaining_unresolved_surfaces"],
    )
    check(
        "working_rank_distribution",
        result["working_candidate_rank_distribution"] == {"1": 156, "2": 1, "6": 1, "UNGENERATED": 1},
        result["working_candidate_rank_distribution"],
    )
    check(
        "result_selected_resolution",
        result["selected_resolution"]["recipe"] == "AIIN+CH+T+Y"
        and result["selected_resolution"]["global_candidate_rank"] == 1
        and result["selected_resolution"]["target_page_exact_aiin_count"] == 4,
        result["selected_resolution"],
    )
    check(
        "no_sealed_pages_materialized",
        not any(row["physical_page"].startswith("f84") for row in old)
        and not any(row["physical_page"].startswith("f84") for row in current_events),
        "f84/f84r absent from loaded selectors",
    )
    check(
        "no_absolute_paths_in_artifacts",
        not any(
            (b"/" + b"home/") in path.read_bytes()
            or (b"/" + b"Users/") in path.read_bytes()
            for path in OUT.iterdir()
            if path.is_file()
        ),
        "artifact path scan",
    )

    passed = sum(row["pass"] for row in checks)
    validation = {
        "experiment_id": "GDT536",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "runner_exit_code": replay.returncode,
        "byte_identical_replay": before == after,
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
