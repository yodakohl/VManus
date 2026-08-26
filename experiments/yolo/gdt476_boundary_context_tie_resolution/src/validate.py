#!/usr/bin/env python3
"""Validate the complete GDT476 contextual tie working edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
BUNDLES_IN = G474 / "gdt474_146_locus_bundle_meaning_triptych.tsv"
BOUNDARIES_IN = G475 / "gdt475_146_bundle_boundary_roles.tsv"
RECORDS_IN = G475 / "gdt475_135_page_microrecords.tsv"
CHAINS_IN = G475 / "gdt475_8_cross_locus_continuation_chains.tsv"
DECISIONS = OUT / "gdt476_64_tie_context_decisions.tsv"
RECORD_READINGS = OUT / "gdt476_8_contextual_record_readings.tsv"
PAGE_SUMMARY = OUT / "gdt476_6_page_tie_summary.tsv"
READABLE = OUT / "GDT476_CONTEXTUAL_TIE_WORKING_EDITION.md"
RESULT = OUT / "gdt476_result.json"
VALIDATION = OUT / "gdt476_validation.json"


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

    generated = [DECISIONS, RECORD_READINGS, PAGE_SUMMARY, READABLE, RESULT]
    check("all_outputs_present", all(path.is_file() for path in generated), [path.name for path in generated])
    if not all(path.is_file() for path in generated):
        raise RuntimeError("Run GDT476 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    bundles = read_tsv(BUNDLES_IN)
    boundaries = read_tsv(BOUNDARIES_IN)
    records = read_tsv(RECORDS_IN)
    chains = read_tsv(CHAINS_IN)
    decisions = read_tsv(DECISIONS)
    record_readings = read_tsv(RECORD_READINGS)
    pages = read_tsv(PAGE_SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    bundle_map = {row["bundle_id"]: row for row in bundles}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    tied = [row for row in bundles if "|" in row["best_models"]]

    check("input_bundles_146", len(bundles) == 146, len(bundles))
    check("input_boundaries_146", len(boundaries) == 146, len(boundaries))
    check("input_records_135", len(records) == 135, len(records))
    check("input_chains_8", len(chains) == 8, len(chains))
    check("input_ties_64", len(tied) == 64, len(tied))
    check("decision_rows_64", len(decisions) == 64, len(decisions))
    check("decision_ids_unique", len({row["tie_id"] for row in decisions}) == 64, len({row["tie_id"] for row in decisions}))
    check("decision_bundle_order_exact", [row["bundle_id"] for row in decisions] == [row["bundle_id"] for row in tied], "64/64")
    check("decision_bundle_ids_unique", len({row["bundle_id"] for row in decisions}) == 64, len({row["bundle_id"] for row in decisions}))
    check("tie_pattern_counts", Counter(row["local_best_models"] for row in decisions) == Counter({
        "COORDINATE|CATALOGUE": 58,
        "COORDINATE|INSTRUCTION|CATALOGUE": 4,
        "COORDINATE|INSTRUCTION": 2,
    }), dict(Counter(row["local_best_models"] for row in decisions)))
    check("old_selection_counts", Counter(row["gdt474_selected_model"] for row in decisions) == Counter({"CATALOGUE": 60, "INSTRUCTION": 2, "COORDINATE": 2}), dict(Counter(row["gdt474_selected_model"] for row in decisions)))

    for field in ("physical_page", "register", "locus", "owner_de", "surface_sequence", "recipe_sequence"):
        check(
            f"source_{field}_exact",
            all(row[field] == bundle_map[row["bundle_id"]][field] for row in decisions),
            "64/64",
        )
    check("boundary_roles_exact", all(row["boundary_role"] == boundary_map[row["bundle_id"]]["boundary_role"] for row in decisions), "64/64")
    check("record_ids_exact", all(row["record_id"] == boundary_map[row["bundle_id"]]["record_id"] for row in decisions), "64/64")
    check("gdt474_models_exact", all(row["gdt474_selected_model"] == bundle_map[row["bundle_id"]]["selected_model"] for row in decisions), "64/64")
    check("gdt474_readings_exact", all(row["gdt474_selected_reading_de"] == bundle_map[row["bundle_id"]]["selected_bundle_reading_de"] for row in decisions), "64/64")

    context = [row for row in decisions if row["context_decided"] == "YES"]
    local = [row for row in decisions if row["context_decided"] == "NO"]
    check("context_ties_12", len(context) == 12, len(context))
    check("local_defaults_52", len(local) == 52, len(local))
    expected_context = {
        "G474-B061": "INSTRUCTION",
        "G474-B071": "INSTRUCTION",
        "G474-B072": "INSTRUCTION",
        "G474-B081": "CATALOGUE",
        "G474-B082": "CATALOGUE",
        "G474-B090": "COORDINATE",
        "G474-B091": "CATALOGUE",
        "G474-B092": "CATALOGUE",
        "G474-B115": "INSTRUCTION",
        "G474-B116": "INSTRUCTION",
        "G474-B127": "CATALOGUE",
        "G474-B128": "CATALOGUE",
    }
    check("context_bundle_models_exact", {row["bundle_id"]: row["context_selected_model"] for row in context} == expected_context, {row["bundle_id"]: row["context_selected_model"] for row in context})
    check("context_only_multi_locus", all(int(row["record_bundle_count"]) > 1 for row in context), "12/12")
    check("local_only_single_locus", all(int(row["record_bundle_count"]) == 1 for row in local), "52/52")
    check("all_ties_have_model", all(row["context_selected_model"] in {"COORDINATE", "INSTRUCTION", "CATALOGUE"} for row in decisions), "64/64")
    check("all_ties_have_reading", all(row["context_selected_reading_de"].strip() and row["contextual_line_de"].strip() for row in decisions), "64/64")
    check("selected_reading_matches_model", all(
        row["context_selected_reading_de"] == bundle_map[row["bundle_id"]][f"{row['context_selected_model'].lower()}_bundle_reading_de"]
        for row in decisions
    ), "64/64")
    check("local_defaults_models_unchanged", all(row["context_selected_model"] == row["gdt474_selected_model"] for row in local), "52/52")
    check("local_defaults_readings_unchanged", all(row["context_selected_reading_de"] == row["gdt474_selected_reading_de"] for row in local), "52/52")

    changed = {row["bundle_id"] for row in decisions if row["model_changed_from_gdt474"] == "YES"}
    expected_changed = {"G474-B061", "G474-B071", "G474-B072", "G474-B090", "G474-B115", "G474-B116"}
    check("model_changes_exact_6", changed == expected_changed, sorted(changed))
    overrides = {
        row["bundle_id"]
        for row in decisions
        if row["context_selected_model"] not in row["local_best_models"].split("|")
    }
    expected_overrides = {"G474-B061", "G474-B072", "G474-B115", "G474-B116"}
    check("local_minimum_overrides_exact_4", overrides == expected_overrides, sorted(overrides))
    credited = {row["bundle_id"] for row in decisions if int(row["inherited_context_repair_credit"]) == 1}
    check("inherited_action_credits_exact_4", credited == expected_overrides, sorted(credited))
    check("credits_only_leading_ol", all(boundary_map[bundle_id]["boundary_role"] == "EXPLICIT_CONTINUATION_OL" for bundle_id in credited), sorted(credited))
    check("credits_match_one_local_repair", all(int(next(row for row in decisions if row["bundle_id"] == bundle_id)["local_selected_repair_count"]) == 1 for bundle_id in credited), sorted(credited))
    check("credited_net_repairs_zero", all(int(next(row for row in decisions if row["bundle_id"] == bundle_id)["net_context_repair_count"]) == 0 for bundle_id in credited), sorted(credited))
    check("context_selection_counts", Counter(row["context_selected_model"] for row in decisions) == Counter({"CATALOGUE": 54, "INSTRUCTION": 7, "COORDINATE": 3}), dict(Counter(row["context_selected_model"] for row in decisions)))

    check("root_meaning_changes_zero", all(row["root_meaning_change"] == "NO" for row in decisions), "64/64")
    check("learned_name_changes_zero", all(row["learned_name_change"] == "NO" for row in decisions), "64/64")
    check("claim_status_exact", all(row["claim_status"] == "COMPLETE_CONTEXTUAL_WORKING_DEFAULT__ALTERNATIVES_PRESERVED" for row in decisions), "64/64")
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in decisions), sorted({row["physical_page"] for row in decisions}))
    check("no_new_pages", {row["physical_page"] for row in decisions} == {"f17r", "f71v", "f72r", "f77r", "f88v", "f89r"}, sorted({row["physical_page"] for row in decisions}))

    check("record_readings_8", len(record_readings) == 8, len(record_readings))
    check("record_ids_match_chains", [row["record_id"] for row in record_readings] == [row["record_id"] for row in chains], "8/8")
    check("record_bundle_ids_exact", all(row["bundle_ids"] == chain["bundle_ids"] for row, chain in zip(record_readings, chains, strict=True)), "8/8")
    expected_sequences = {
        "G475-R060": "INSTRUCTION|INSTRUCTION|COORDINATE",
        "G475-R069": "INSTRUCTION|INSTRUCTION",
        "G475-R078": "CATALOGUE|CATALOGUE|INSTRUCTION",
        "G475-R084": "COORDINATE|COORDINATE",
        "G475-R085": "CATALOGUE|CATALOGUE",
        "G475-R107": "INSTRUCTION|INSTRUCTION|INSTRUCTION",
        "G475-R110": "INSTRUCTION|INSTRUCTION",
        "G475-R117": "CATALOGUE|CATALOGUE",
    }
    check("record_model_sequences_exact", {row["record_id"]: row["context_selected_model_sequence"] for row in record_readings} == expected_sequences, {row["record_id"]: row["context_selected_model_sequence"] for row in record_readings})
    check("record_model_changes_sum_6", sum(int(row["model_change_count"]) for row in record_readings) == 6, sum(int(row["model_change_count"]) for row in record_readings))
    check("record_context_ties_sum_12", sum(int(row["context_decided_tie_count"]) for row in record_readings) == 12, sum(int(row["context_decided_tie_count"]) for row in record_readings))
    check("record_readings_nonempty", all(row["context_record_reading_de"].strip() for row in record_readings), "8/8")

    expected_pages = {"f17r": (1, 0, 1, 0), "f71v": (6, 0, 6, 0), "f72r": (28, 6, 22, 4), "f77r": (6, 2, 4, 0), "f88v": (9, 0, 9, 0), "f89r": (14, 4, 10, 2)}
    actual_pages = {row["physical_page"]: (int(row["tie_count"]), int(row["context_decided_count"]), int(row["local_default_count"]), int(row["model_change_count"])) for row in pages}
    check("page_rows_6", len(pages) == 6, len(pages))
    check("page_counts_exact", actual_pages == expected_pages, actual_pages)
    check("page_defaults_complete", all(row["all_ties_have_working_default"] == "YES" for row in pages), "6/6")

    check("result_status", result["status"] == "TWELVE_TIES_GAIN_RECORD_CONTEXT__SIX_WORKING_MODELS_CHANGE", result["status"])
    check("result_core_counts", result["tie_count"] == 64 and result["context_decided_tie_count"] == 12 and result["local_default_tie_count"] == 52 and result["model_change_count"] == 6, result)
    check("result_changed_ids", set(result["model_change_bundle_ids"]) == expected_changed, result["model_change_bundle_ids"])
    check("result_override_ids", set(result["context_override_local_minimum_bundle_ids"]) == expected_overrides, result["context_override_local_minimum_bundle_ids"])
    check("result_credit_total_4", result["inherited_action_repair_credit_total"] == 4, result["inherited_action_repair_credit_total"])
    check("result_no_source_changes", all(result[key] == 0 for key in ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "new_page_count")), {key: result[key] for key in ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "new_page_count")})

    readable = READABLE.read_text(encoding="utf-8")
    check("readable_has_all_pages", all(f"### {page}" in readable for page in expected_pages), sorted(expected_pages))
    check("readable_has_all_ties", all(row["bundle_id"] in readable for row in decisions), "64/64")
    check("readable_has_all_records", all(row["record_id"] in readable for row in record_readings), "8/8")

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
