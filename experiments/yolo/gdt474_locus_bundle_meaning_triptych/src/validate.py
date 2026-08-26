#!/usr/bin/env python3
"""Validate GDT474 and its deterministic three-reading reconstruction."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
BASE = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
VALIDATION = OUT / "gdt474_validation.json"
EDITION = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts/gdt473_183_unified_address_working_edition.tsv"
CORES = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"
EVENTS = OUT / "gdt474_183_event_meaning_triptych.tsv"
BUNDLES = OUT / "gdt474_146_locus_bundle_meaning_triptych.tsv"
ROOTS = OUT / "gdt474_19_root_grammatical_recasts.tsv"
PAGES = OUT / "gdt474_6_page_model_profile.tsv"
PATTERNS = OUT / "gdt474_6_choice_pattern_summary.tsv"
READABLE = OUT / "GDT474_LOCUS_BUNDLE_READING_BOOK.md"
RESULT = OUT / "gdt474_result.json"

NAME_RE = re.compile(r"\[(?:PFLANZENNAME|STERNSTELLENNAME|BADSTATIONSNAME|DROGENNAME):([^\]]+)\]")
FAMILY_RE = re.compile(r"([^ ·:]+):(?:PFLANZENFAMILIE|STERNSTELLENFAMILIE|BADSTATIONSFAMILIE|DROGENFAMILIE)")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [EVENTS, BUNDLES, ROOTS, PAGES, PATTERNS, READABLE, RESULT]
    check("all_outputs_present", all(path.is_file() for path in generated), [path.name for path in generated])
    if not all(path.is_file() for path in generated):
        raise RuntimeError("Run GDT474 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    edition = read_tsv(EDITION)
    cores = read_tsv(CORES)
    events = read_tsv(EVENTS)
    bundles = read_tsv(BUNDLES)
    roots = read_tsv(ROOTS)
    pages = read_tsv(PAGES)
    patterns = read_tsv(PATTERNS)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_event_count_183", len(edition) == 183, len(edition))
    check("triptych_event_count_183", len(events) == 183, len(events))
    check("event_source_order_exact", [row["source_event_id"] for row in events] == [row["source_event_id"] for row in edition], "source_event_id")
    check("event_surfaces_exact", [row["surface"] for row in events] == [row["surface"] for row in edition], "surface")
    check("event_recipes_exact", [row["working_recipe"] for row in events] == [row["working_recipe"] for row in edition], "working_recipe")
    check("event_literals_exact", [row["literal_working_reading_de"] for row in events] == [row["working_reading_de"] for row in edition], "working_reading_de")
    check("event_ids_unique", len({row["triptych_event_id"] for row in events}) == 183, len({row["triptych_event_id"] for row in events}))
    check("source_ids_unique", len({row["source_event_id"] for row in events}) == 183, len({row["source_event_id"] for row in events}))

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in edition:
        grouped[(row["physical_page"], row["locus"], row["owner_de"])].append(row)
    check("bundle_count_146", len(bundles) == len(grouped) == 146, [len(bundles), len(grouped)])
    check("bundle_ids_unique", len({row["bundle_id"] for row in bundles}) == 146, len({row["bundle_id"] for row in bundles}))
    expected_keys = list(grouped)
    actual_keys = [(row["physical_page"], row["locus"], row["owner_de"]) for row in bundles]
    check("bundle_key_order_exact", actual_keys == expected_keys, "page/locus/owner")
    check("bundle_event_total_183", sum(int(row["event_count"]) for row in bundles) == 183, sum(int(row["event_count"]) for row in bundles))
    size_counts = Counter(int(row["event_count"]) for row in bundles)
    check("bundle_size_counts_116_23_7", size_counts == Counter({1: 116, 2: 23, 3: 7}), dict(size_counts))
    multi = [row for row in bundles if int(row["event_count"]) > 1]
    check("multi_bundle_count_30", len(multi) == 30, len(multi))
    check("multi_bundle_events_67", sum(int(row["event_count"]) for row in multi) == 67, sum(int(row["event_count"]) for row in multi))
    check("bundle_source_ids_exact", all(
        row["source_event_ids"] == "|".join(item["source_event_id"] for item in grouped[(row["physical_page"], row["locus"], row["owner_de"])])
        for row in bundles
    ), "146/146")
    check("bundle_surface_sequences_exact", all(
        row["surface_sequence"] == "|".join(item["surface"] for item in grouped[(row["physical_page"], row["locus"], row["owner_de"])])
        for row in bundles
    ), "146/146")

    candidate_fields = ["coordinate_bundle_reading_de", "instruction_bundle_reading_de", "catalogue_bundle_reading_de"]
    check("three_bundle_readings_nonempty", all(all(row[field].strip() for field in candidate_fields) for row in bundles), "438/438")
    check("three_event_readings_nonempty", all(row["coordinate_event_reading_de"] and row["instruction_event_reading_de"] and row["catalogue_event_reading_de"] for row in events), "549/549")
    check("selected_bundle_reading_exact", all(row["selected_bundle_reading_de"] == row[f"{row['selected_model'].lower()}_bundle_reading_de"] for row in bundles), "146/146")
    check("selected_event_reading_exact", all(row["selected_event_reading_de"] == row[f"{row['bundle_selected_model'].lower()}_event_reading_de"] for row in events), "183/183")
    check("selected_models_closed", {row["selected_model"] for row in bundles} == {"COORDINATE", "INSTRUCTION", "CATALOGUE"}, sorted({row["selected_model"] for row in bundles}))
    check("best_models_include_selected", all(row["selected_model"] in row["best_models"].split("|") for row in bundles), "146/146")
    check("selected_cost_is_minimum", all(
        int(row[f"{row['selected_model'].lower()}_repair_count"]) == min(int(row[f"{model}_repair_count"]) for model in ("coordinate", "instruction", "catalogue"))
        for row in bundles
    ), "146/146")

    totals = {
        "COORDINATE": sum(int(row["coordinate_repair_count"]) for row in bundles),
        "INSTRUCTION": sum(int(row["instruction_repair_count"]) for row in bundles),
        "CATALOGUE": sum(int(row["catalogue_repair_count"]) for row in bundles),
    }
    check("universal_repair_totals_89_120_146", totals == {"COORDINATE": 89, "INSTRUCTION": 120, "CATALOGUE": 146}, totals)
    selected_counts = Counter(row["selected_model"] for row in bundles)
    check("selected_counts_27_54_65", selected_counts == Counter({"COORDINATE": 27, "INSTRUCTION": 54, "CATALOGUE": 65}), dict(selected_counts))
    mixed_total = sum(int(row[f"{row['selected_model'].lower()}_repair_count"]) for row in bundles)
    check("mixed_repair_total_14", mixed_total == 14, mixed_total)
    unique_wins = Counter(row["best_models"] for row in bundles if "|" not in row["best_models"])
    check("unique_wins_25_52_5", unique_wins == Counter({"COORDINATE": 25, "INSTRUCTION": 52, "CATALOGUE": 5}), dict(unique_wins))
    check("tied_bundle_count_64", sum("|" in row["best_models"] for row in bundles) == 64, sum("|" in row["best_models"] for row in bundles))
    check("choice_patterns_6", len(patterns) == len({row["best_models"] for row in bundles}) == 6, [len(patterns), len({row["best_models"] for row in bundles})])
    check("choice_pattern_bundle_total", sum(int(row["bundle_count"]) for row in patterns) == 146, sum(int(row["bundle_count"]) for row in patterns))

    check("root_recast_count_19", len(roots) == len(cores) == 19, [len(roots), len(cores)])
    check("root_order_exact", [row["root"] for row in roots] == [row["root"] for row in cores], "root")
    check("root_values_exact", [row["working_value_de"] for row in roots] == [row["selected_minimal_value_de"] for row in cores], "working value")
    check("root_semantics_unchanged", all(row["semantic_change"] == "NO__GRAMMATICAL_RECAST_ONLY" for row in roots), "19/19")
    check("all_root_recasts_nonempty", all(row["coordinate_recast_de"] and row["instruction_recast_de"] and row["catalogue_recast_de"] for row in roots), "57/57")

    edition_by_event = {row["source_event_id"]: row for row in edition}
    check("name_strings_preserved_in_all_readings", all(
        all(name in event["coordinate_event_reading_de"] and name in event["instruction_event_reading_de"] and name in event["catalogue_event_reading_de"] for name in NAME_RE.findall(edition_by_event[event["source_event_id"]]["working_reading_de"]))
        for event in events
    ), "all learned cores visible")
    check("family_stems_preserved_in_all_readings", all(
        all(stem in event["coordinate_event_reading_de"] and stem in event["instruction_event_reading_de"] and stem in event["catalogue_event_reading_de"] for stem in FAMILY_RE.findall(edition_by_event[event["source_event_id"]]["working_reading_de"]))
        for event in events
    ), "all family stems visible")
    check("event_change_flags_zero", all(row["component_meaning_change"] == "NO" and row["learned_name_change"] == "NO" for row in events), "183/183")

    expected_pages = {"f17r": (1, 2), "f71v": (15, 22), "f72r": (74, 96), "f77r": (10, 11), "f88v": (13, 14), "f89r": (33, 38)}
    check("page_rows_6", len(pages) == 6, len(pages))
    check("page_counts_exact", {row["physical_page"]: (int(row["bundle_count"]), int(row["event_count"])) for row in pages} == expected_pages, {row["physical_page"]: (row["bundle_count"], row["event_count"]) for row in pages})
    check("page_selected_totals", all(int(row["coordinate_selected_count"]) + int(row["instruction_selected_count"]) + int(row["catalogue_selected_count"]) == int(row["bundle_count"]) for row in pages), "6/6")
    check("no_new_pages", {row["physical_page"] for row in events} == set(expected_pages), sorted({row["physical_page"] for row in events}))
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in events), sorted({row["physical_page"] for row in events}))

    exact = {row["surface"]: row for row in events if row["surface"] in {"ykyd", "yddy"}}
    check("exact_packages_present", set(exact) == {"ykyd", "yddy"}, sorted(exact))
    check("exact_package_recipes_unchanged", exact["ykyd"]["working_recipe"] == "Y+K+Y+D_ADDR" and exact["yddy"]["working_recipe"] == "Y+D_ADDR+Y", {key: row["working_recipe"] for key, row in exact.items()})

    check("result_status", result["status"] == "MIXED_LOCUS_GRAMMAR_REQUIRES_FEWEST_WORKING_REPAIRS__COORDINATE_BEST_SINGLE_DEFAULT", result["status"])
    check("result_totals_exact", result["universal_repair_totals"] == totals and result["mixed_selected_repair_total"] == mixed_total and result["selected_model_counts"] == dict(selected_counts), result)
    check("result_no_semantic_or_page_changes", result["component_meaning_change_count"] == result["learned_name_change_count"] == result["new_page_count"] == 0, "all zero")
    readable = READABLE.read_text(encoding="utf-8")
    check("readable_has_all_pages", all(f"## {page}" in readable for page in expected_pages), sorted(expected_pages))
    check("readable_has_all_bundle_loci", all(f"### {row['locus']} —" in readable for row in bundles), "146/146")
    check("readable_has_all_roots", all(f"`{row['root']}`" in readable for row in roots), "19/19")

    passed = sum(bool(row["pass"]) for row in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "details": checks,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("status", "checks", "passed", "failed")}, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
