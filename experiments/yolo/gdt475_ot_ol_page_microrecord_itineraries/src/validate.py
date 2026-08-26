#!/usr/bin/env python3
"""Validate GDT475 order positions, records, and page itineraries."""

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
BASE = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
VALIDATION = OUT / "gdt475_validation.json"
BUNDLES_IN = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts/gdt474_146_locus_bundle_meaning_triptych.tsv"
EVENTS_IN = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts/gdt474_183_event_meaning_triptych.tsv"
ORDER_PROFILES = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts/gdt429_10_nonaction_semantic_profiles.tsv"
BOUNDARIES = OUT / "gdt475_146_bundle_boundary_roles.tsv"
ORDER = OUT / "gdt475_69_order_occurrence_positions.tsv"
RECORDS = OUT / "gdt475_135_page_microrecords.tsv"
CHAINS = OUT / "gdt475_8_cross_locus_continuation_chains.tsv"
PAGES = OUT / "gdt475_6_page_itinerary_summary.tsv"
READABLE = OUT / "GDT475_SIX_PAGE_MICRORECORD_ITINERARIES.md"
RESULT = OUT / "gdt475_result.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def atoms(event: dict[str, str]) -> list[str]:
    return [] if event["working_recipe"] == "NONE" else event["working_recipe"].split("+")


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [BOUNDARIES, ORDER, RECORDS, CHAINS, PAGES, READABLE, RESULT]
    check("all_outputs_present", all(path.is_file() for path in generated), [path.name for path in generated])
    if not all(path.is_file() for path in generated):
        raise RuntimeError("Run GDT475 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    bundles_in = read_tsv(BUNDLES_IN)
    events_in = read_tsv(EVENTS_IN)
    profiles = {row["core_root"]: row for row in read_tsv(ORDER_PROFILES)}
    boundaries = read_tsv(BOUNDARIES)
    occurrences = read_tsv(ORDER)
    records = read_tsv(RECORDS)
    chains = read_tsv(CHAINS)
    pages = read_tsv(PAGES)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("input_bundles_146", len(bundles_in) == 146, len(bundles_in))
    check("input_events_183", len(events_in) == 183, len(events_in))
    check("boundary_rows_146", len(boundaries) == 146, len(boundaries))
    check("boundary_bundle_order_exact", [row["bundle_id"] for row in boundaries] == [row["bundle_id"] for row in bundles_in], "bundle_id")
    check("boundary_surface_sequences_exact", [row["surface_sequence"] for row in boundaries] == [row["surface_sequence"] for row in bundles_in], "surface_sequence")
    check("boundary_recipe_sequences_exact", [row["recipe_sequence"] for row in boundaries] == [row["recipe_sequence"] for row in bundles_in], "recipe_sequence")
    check("boundary_selected_models_exact", [row["selected_model"] for row in boundaries] == [row["selected_model"] for row in bundles_in], "selected_model")
    check("boundary_selected_readings_exact", [row["selected_bundle_reading_de"] for row in boundaries] == [row["selected_bundle_reading_de"] for row in bundles_in], "selected reading")
    check("boundary_ids_unique", len({row["boundary_id"] for row in boundaries}) == 146, len({row["boundary_id"] for row in boundaries}))

    profiles_expected = {"OT": "DANACH", "OL": "FORTSETZEN"}
    check("order_meanings_exact_gdt429", {root: profiles[root]["working_meaning_de"] for root in profiles_expected} == profiles_expected, {root: profiles[root]["working_meaning_de"] for root in profiles_expected})
    check("order_occurrence_rows_69", len(occurrences) == 69, len(occurrences))
    check("order_occurrence_ids_unique", len({row["order_occurrence_id"] for row in occurrences}) == 69, len({row["order_occurrence_id"] for row in occurrences}))
    check("order_roots_closed", {row["root"] for row in occurrences} == {"OT", "OL"}, sorted({row["root"] for row in occurrences}))
    check("order_working_meanings_unchanged", all(row["working_meaning_de"] == profiles_expected[row["root"]] for row in occurrences), "69/69")
    check("order_component_change_zero", all(row["component_meaning_change"] == "NO" for row in occurrences), "69/69")
    root_counts = Counter(row["root"] for row in occurrences)
    check("order_counts_ot41_ol28", root_counts == Counter({"OT": 41, "OL": 28}), dict(root_counts))
    position_counts = Counter((row["root"], row["position_role"]) for row in occurrences)
    expected_positions = Counter({
        ("OT", "BUNDLE_LEADING"): 40,
        ("OT", "LATER_EVENT_LEADING"): 1,
        ("OL", "BUNDLE_LEADING"): 11,
        ("OL", "LATER_EVENT_LEADING"): 1,
        ("OL", "EVENT_INTERNAL"): 16,
    })
    check("order_position_counts_exact", position_counts == expected_positions, {"|".join(key): value for key, value in position_counts.items()})
    check("ot_never_event_internal", not any(row["root"] == "OT" and row["position_role"] == "EVENT_INTERNAL" for row in occurrences), "0")
    check("ot_always_opens_event", all(row["position_role"] in {"BUNDLE_LEADING", "LATER_EVENT_LEADING"} for row in occurrences if row["root"] == "OT"), "41/41")
    check("ol_internal_16_of_28", sum(row["root"] == "OL" and row["position_role"] == "EVENT_INTERNAL" for row in occurrences) == 16, "16/28")

    expected_boundary_counts = Counter({
        "PAGE_START": 6,
        "EXPLICIT_NEXT_SIBLING_OT": 39,
        "EXPLICIT_CONTINUATION_OL": 11,
        "UNMARKED_NEW_LOCUS": 84,
        "UNMARKED_NEW_LOCUS_WITH_INTERNAL_CONTROL": 6,
    })
    boundary_counts = Counter(row["boundary_role"] for row in boundaries)
    check("boundary_role_counts_exact", boundary_counts == expected_boundary_counts, dict(boundary_counts))
    check("page_start_count_6", sum(row["boundary_role"] == "PAGE_START" for row in boundaries) == 6, "6")
    check("leading_ot_boundaries_exact", all(row["leading_root"] == "OT" for row in boundaries if row["boundary_role"] == "EXPLICIT_NEXT_SIBLING_OT"), "39/39")
    check("leading_ol_boundaries_exact", all(row["leading_root"] == "OL" and row["begins_new_record"] == "NO" for row in boundaries if row["boundary_role"] == "EXPLICIT_CONTINUATION_OL"), "11/11")
    check("all_non_ol_boundaries_begin_records", all((row["leading_root"] != "OL") == (row["begins_new_record"] == "YES") for row in boundaries if row["boundary_role"] != "PAGE_START"), "140/140")
    check("previous_bundle_links_page_safe", all(
        row["previous_bundle_id"] == "NONE" if int(row["page_bundle_ordinal"]) == 1 else row["previous_bundle_id"] != "NONE"
        for row in boundaries
    ), "146/146")
    check("bundle_claim_status_fixed", all(row["claim_status"] == "ORDER_ROLE_WORKING_READING__NO_ROOT_OR_NAME_CHANGE" for row in boundaries), "146/146")

    check("record_rows_135", len(records) == 135, len(records))
    check("record_ids_unique", len({row["record_id"] for row in records}) == 135, len({row["record_id"] for row in records}))
    check("record_bundle_total_146", sum(int(row["bundle_count"]) for row in records) == 146, sum(int(row["bundle_count"]) for row in records))
    record_sizes = Counter(int(row["bundle_count"]) for row in records)
    check("record_sizes_127_5_3", record_sizes == Counter({1: 127, 2: 5, 3: 3}), dict(record_sizes))
    check("record_continuation_total_11", sum(int(row["continuation_bundle_count"]) for row in records) == 11, sum(int(row["continuation_bundle_count"]) for row in records))
    check("record_bundle_counts_echo_boundaries", all(int(row["record_bundle_count"]) == next(int(record["bundle_count"]) for record in records if record["record_id"] == row["record_id"]) for row in boundaries), "146/146")
    check("record_locus_counts_match", all(len(row["locus_sequence"].split("|")) == int(row["bundle_count"]) for row in records), "135/135")
    check("record_boundary_sequences_start_noncontinuation", all(not row["boundary_role_sequence"].startswith("EXPLICIT_CONTINUATION_OL") for row in records), "135/135")
    check("record_followers_are_ol_continuations", all(all(role == "EXPLICIT_CONTINUATION_OL" for role in row["boundary_role_sequence"].split("|")[1:]) for row in records), "135/135")

    check("continuation_chain_rows_8", len(chains) == 8, len(chains))
    check("chain_ids_unique", len({row["continuation_chain_id"] for row in chains}) == 8, len({row["continuation_chain_id"] for row in chains}))
    check("chains_cover_19_bundles", sum(int(row["bundle_count"]) for row in chains) == 19, sum(int(row["bundle_count"]) for row in chains))
    check("chains_have_11_ol_joins", sum(int(row["explicit_ol_join_count"]) for row in chains) == 11, sum(int(row["explicit_ol_join_count"]) for row in chains))
    check("chain_record_join_exact", all(any(record["record_id"] == row["record_id"] and record["bundle_ids"] == row["bundle_ids"] for record in records) for row in chains), "8/8")
    expected_chain_pages = Counter({"f72r": 4, "f77r": 1, "f89r": 3})
    check("chain_page_counts", Counter(row["physical_page"] for row in chains) == expected_chain_pages, dict(Counter(row["physical_page"] for row in chains)))

    expected_pages = {
        "f17r": (1, 2, 1, 0, 0),
        "f71v": (15, 22, 15, 6, 0),
        "f72r": (74, 96, 68, 16, 6),
        "f77r": (10, 11, 9, 6, 1),
        "f88v": (13, 14, 13, 6, 0),
        "f89r": (33, 38, 29, 5, 4),
    }
    check("page_rows_6", len(pages) == 6, len(pages))
    actual_pages = {
        row["physical_page"]: (
            int(row["bundle_count"]), int(row["event_count"]), int(row["record_count"]),
            int(row["explicit_ot_next_count"]), int(row["explicit_ol_continuation_count"]),
        ) for row in pages
    }
    check("page_counts_exact", actual_pages == expected_pages, actual_pages)
    check("page_itineraries_complete", all(row["itinerary_complete"] == "YES" for row in pages), "6/6")
    check("page_record_total_135", sum(int(row["record_count"]) for row in pages) == 135, sum(int(row["record_count"]) for row in pages))
    check("no_new_pages", {row["physical_page"] for row in boundaries} == set(expected_pages), sorted({row["physical_page"] for row in boundaries}))
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in boundaries), sorted({row["physical_page"] for row in boundaries}))

    exact = {row["surface_sequence"]: row["recipe_sequence"] for row in boundaries if row["surface_sequence"] in {"ykyd", "yddy"}}
    check("exact_packages_preserved", exact == {"ykyd": "Y+K+Y+D_ADDR", "yddy": "Y+D_ADDR+Y"}, exact)
    check("result_status", result["status"] == "OT_OPENS_EVENTS_AND_NEXT_SIBLINGS__OL_CONTINUES_RECORDS_OR_STAYS_INTERNAL", result["status"])
    check("result_position_counts_exact", result["order_position_counts"] == {
        "OT": {"TOTAL": 41, "BUNDLE_LEADING": 40, "LATER_EVENT_LEADING": 1, "EVENT_INTERNAL": 0},
        "OL": {"TOTAL": 28, "BUNDLE_LEADING": 11, "LATER_EVENT_LEADING": 1, "EVENT_INTERNAL": 16},
    }, result["order_position_counts"])
    check("result_boundary_counts_exact", result["boundary_role_counts"] == dict(expected_boundary_counts), result["boundary_role_counts"])
    check("result_no_changes", result["component_meaning_change_count"] == result["learned_name_change_count"] == result["selected_model_change_count"] == result["new_page_count"] == 0, "all zero")
    check("result_record_counts", result["record_count"] == 135 and result["multi_locus_continuation_chain_count"] == 8 and result["explicit_ol_continuation_join_count"] == 11, result)

    readable = READABLE.read_text(encoding="utf-8")
    check("readable_has_all_pages", all(f"## {page}" in readable for page in expected_pages), sorted(expected_pages))
    check("readable_has_all_records", all(str(row["record_id"]) in readable for row in records), "135/135")
    check("readable_has_all_chains", all(str(row["record_id"]) in readable for row in chains), "8/8")

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
