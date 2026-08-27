#!/usr/bin/env python3
"""Validate the GDT537 final-surface overlay and all seven route cards."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from intake_surface import exact_final_lookup


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt537_seven_route_final_intake_supplement"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
CLI = BASE / "src/intake_surface.py"
VALIDATION = OUT / "gdt537_validation.json"
EDITION = (
    ROOT
    / "experiments/yolo/gdt536_aii_renderer_square_aiicthy_closure/artifacts"
    / "gdt536_159_working_revision.tsv"
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


def cli_probe(*arguments: str) -> tuple[int, dict, str]:
    completed = subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = json.loads(completed.stdout) if completed.stdout else {}
    return completed.returncode, value, completed.stderr


def main() -> int:
    before = snapshot()
    replay_process = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    after = snapshot()

    result = json.loads((OUT / "gdt537_result.json").read_text(encoding="utf-8"))
    dictionary = read_tsv(OUT / "gdt537_159_final_surface_dictionary.tsv")
    routes = read_tsv(OUT / "gdt537_7_revision_route_cards.tsv")
    regression = read_tsv(OUT / "gdt537_7_base_to_final_regression.tsv")
    summary = read_tsv(OUT / "gdt537_route_class_summary.tsv")
    precedence = read_tsv(OUT / "gdt537_intake_precedence.tsv")
    replay = read_tsv(OUT / "gdt537_159_cli_replay.tsv")
    edition = read_tsv(EDITION)

    expected_special = {
        "aiicthy",
        "chekchy",
        "dairykodas",
        "dalcheeeky",
        "dsholdaiir",
        "qef",
        "saiis",
    }
    independent_special = {
        row["surface"]
        for row in edition
        if row["gdt536_working_recipe"] != row["revised_working_recipe"]
        or row["gdt536_resolution_status"].startswith("RESOLVED_BY_")
    }

    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check("runner_exit", replay_process.returncode == 0, replay_process.stderr[-1000:])
    check("byte_identical_replay", before == after, {"before": before, "after": after})
    check(
        "result_status",
        result["status"] == "PASS_SEVEN_ROUTE_FINAL_INTAKE_SUPPLEMENT",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "FINAL_WORKING_PROSE_SURFACE_OVERLAY_AND_SEVEN_NAMED_ROUTE_CARDS__NO_GLOBAL_EXTENSION_OR_CONFIRMED_PLAINTEXT",
        result["claim_ceiling"],
    )
    check("edition_count", len(edition) == 159 and len({row["surface"] for row in edition}) == 159, len(edition))
    check("independent_special_set", independent_special == expected_special, sorted(independent_special))
    check("route_count_unique", len(routes) == 7 and len({row["surface"] for row in routes}) == 7, len(routes))
    check("route_set", {row["surface"] for row in routes} == expected_special, sorted(row["surface"] for row in routes))
    check(
        "route_order",
        [row["surface"] for row in routes]
        == ["chekchy", "saiis", "dsholdaiir", "dairykodas", "dalcheeeky", "qef", "aiicthy"],
        [row["surface"] for row in routes],
    )
    check(
        "route_sources",
        [row["source_experiment"] for row in routes]
        == ["GDT530", "GDT531", "GDT532", "GDT533", "GDT534", "GDT535", "GDT536"],
        [row["source_experiment"] for row in routes],
    )
    check("route_classes_unique", len({row["route_class"] for row in routes}) == 7, [row["route_class"] for row in routes])
    check("route_evidence_nonempty", all(row["primary_evidence"] and row["transfer_scope"] for row in routes), "seven evidence cards")
    changed = [row for row in routes if row["recipe_changed"] == "YES"]
    resolution_only = [row for row in routes if row["revision_kind"] == "RESOLUTION_ONLY"]
    check("six_recipe_revisions", len(changed) == 6, [row["surface"] for row in changed])
    check("qef_resolution_only", len(resolution_only) == 1 and resolution_only[0]["surface"] == "qef", resolution_only)

    check("dictionary_count_unique", len(dictionary) == 159 and len({row["surface"] for row in dictionary}) == 159, len(dictionary))
    check("dictionary_lock_keys", len({row["lock_key"] for row in dictionary}) == 159 and all(row["lock_key"].startswith("PROSE_STREAM|") for row in dictionary), "159 prose keys")
    check("dictionary_all_resolved", all(row["resolution_status"] != "UNRESOLVED_NON_TOP1" for row in dictionary), "159 resolved")
    check("dictionary_special_count", sum(row["special_route"] == "YES" for row in dictionary) == 7, Counter(row["special_route"] for row in dictionary))
    check("dictionary_ordinary_count", sum(row["route_class"] == "ORDINARY_FINAL_SURFACE_LOCK" for row in dictionary) == 152, Counter(row["route_class"] for row in dictionary))
    rank_counts = Counter(row["gdt529_candidate_rank"] for row in dictionary)
    check("rank_distribution", rank_counts == Counter({"1": 156, "2": 1, "6": 1, "UNGENERATED": 1}), dict(rank_counts))
    check(
        "dictionary_matches_edition",
        all(
            next(item for item in edition if item["surface"] == row["surface"])["gdt536_working_recipe"]
            == row["final_working_recipe"]
            for row in dictionary
        ),
        "159 final recipes",
    )

    check("regression_count", len(regression) == 7 and {row["surface"] for row in regression} == expected_special, len(regression))
    check("regression_six_would_lose", sum(row["baseline_would_lose_final_choice"] == "YES" for row in regression) == 6, [row["surface"] for row in regression if row["baseline_would_lose_final_choice"] == "YES"])
    check("class_summary_count", len(summary) == 8, len(summary))
    check("class_summary_total", sum(int(row["surface_count"]) for row in summary) == 159, sum(int(row["surface_count"]) for row in summary))
    check("precedence_four_steps", len(precedence) == 4 and [row["priority"] for row in precedence] == ["1", "2", "3", "4"], precedence)
    check("replay_count", len(replay) == 159, len(replay))
    check("replay_all_recipes", all(row["recipe_match"] == "YES" for row in replay), [row["surface"] for row in replay if row["recipe_match"] != "YES"])
    check("replay_all_routes", all(row["route_match"] == "YES" for row in replay), [row["surface"] for row in replay if row["route_match"] != "YES"])

    direct_results = [
        exact_final_lookup(row["surface"], "PROSE_STREAM", dictionary, routes)
        for row in dictionary
    ]
    check("direct_cli_159", all(value is not None for value in direct_results), sum(value is not None for value in direct_results))
    check(
        "direct_cli_recipes",
        all(value["final_recipe"] == row["final_working_recipe"] for value, row in zip(direct_results, dictionary)),
        "159/159",
    )
    check(
        "local_domain_never_locks",
        all(exact_final_lookup(row["surface"], "LOCAL_RECORD", dictionary, routes) is None for row in dictionary),
        "159 delegated",
    )

    code, aiicthy, error = cli_probe("--surface", "aiicthy", "--domain", "PROSE_STREAM", "--top", "3")
    check("cli_aiicthy_exit", code == 0, error)
    check(
        "cli_aiicthy_final",
        aiicthy.get("status") == "GDT537_FINAL_PROSE_SURFACE_LOCK"
        and aiicthy.get("final_recipe") == "AIIN+CH+T+Y"
        and aiicthy.get("special_route") == "YES",
        {key: aiicthy.get(key) for key in ["status", "final_recipe", "special_route"]},
    )
    code, local, error = cli_probe("--surface", "aiicthy", "--domain", "LOCAL_RECORD", "--top", "1")
    check("cli_local_exit", code == 0, error)
    check(
        "cli_local_delegation",
        local.get("status") == "DELEGATED_TO_GDT517_BASE"
        and local.get("reason") == "LOCAL_RECORD_DOMAIN_NOT_COVERED_BY_GDT537_PROSE_LOCK",
        {key: local.get(key) for key in ["status", "reason"]},
    )
    code, old, error = cli_probe("--surface", "aiin", "--domain", "PROSE_STREAM", "--top", "1")
    check("cli_old_exit", code == 0, error)
    check(
        "cli_old_delegation",
        old.get("status") == "DELEGATED_TO_GDT517_BASE"
        and old.get("base_intake", {}).get("default_selection") == "AIIN",
        {"status": old.get("status"), "selection": old.get("base_intake", {}).get("default_selection")},
    )
    code, unseen, error = cli_probe("--surface", "zzzz", "--domain", "PROSE_STREAM", "--top", "1")
    check("cli_unseen_exit", code == 0, error)
    check(
        "cli_unseen_delegation",
        unseen.get("status") == "DELEGATED_TO_GDT517_BASE"
        and unseen.get("reason") == "SURFACE_NOT_IN_GDT537_FINAL_159",
        {key: unseen.get(key) for key in ["status", "reason"]},
    )

    correction = result["route_scope_correction"]
    check(
        "four_to_seven_correction",
        correction["previous_short_route_count"] == 4
        and correction["complete_revision_route_count"] == 7
        and set(correction["previously_omitted_rank1_surfaces"]) == {"chekchy", "saiis", "dairykodas"},
        correction,
    )
    check(
        "result_dictionary_metrics",
        result["final_dictionary"]
        == {
            "surface_count": 159,
            "resolved_count": 159,
            "ordinary_surface_count": 152,
            "special_route_surface_count": 7,
            "recipe_revision_count": 6,
            "resolution_only_count": 1,
            "candidate_rank_distribution": {"1": 156, "2": 1, "6": 1, "UNGENERATED": 1},
        },
        result["final_dictionary"],
    )
    check(
        "result_cli_metrics",
        result["cli_replay"] == {"probe_count": 159, "recipe_match_count": 159, "route_match_count": 159},
        result["cli_replay"],
    )
    check(
        "no_sealed_page_in_dictionary",
        not any("f84" in row["physical_pages"] for row in dictionary),
        "f84/f84r absent",
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
        "experiment_id": "GDT537",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "runner_exit_code": replay_process.returncode,
        "byte_identical_replay": before == after,
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
