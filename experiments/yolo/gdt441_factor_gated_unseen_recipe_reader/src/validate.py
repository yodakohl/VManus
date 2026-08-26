#!/usr/bin/env python3
"""Validate GDT441's factor-gated fallback reader."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader"
OUT = BASE / "artifacts"
READER_PATH = BASE / "src/factor_gate_stream_read.py"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
GDT438 = ROOT / "experiments/yolo/gdt438_order_safe_streaming_reader/artifacts/gdt438_4576_order_safe_stream_readings.tsv"
GDT440 = ROOT / "experiments/yolo/gdt440_dual_channel_order_trace_reader/artifacts/gdt440_4576_dual_channel_stream_readings.tsv"
PRIVATE_SOURCE = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_861_page_private_recipe_replay.tsv"
CANDIDATE_SOURCE = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_4938_candidate_density.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tracked = [
        OUT / "gdt441_4576_factor_reader_replay.tsv",
        OUT / "gdt441_861_page_private_factor_replay.tsv",
        OUT / "gdt441_4938_candidate_factor_gate.tsv",
        OUT / "gdt441_factor_gate_inventory.tsv",
        OUT / "gdt441_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(
        ["python3", str(BASE / "src/run.py")], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    after = {path: path.read_bytes() for path in tracked}

    current = read_tsv(tracked[0])
    private = read_tsv(tracked[1])
    candidates = read_tsv(tracked[2])
    inventory = read_tsv(tracked[3])
    result = json.loads(tracked[4].read_text(encoding="utf-8"))
    catalog = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
    gdt438 = {row["event_id"]: row for row in read_tsv(GDT438)}
    gdt440 = {row["event_id"]: row for row in read_tsv(GDT440)}
    private_source = read_tsv(PRIVATE_SOURCE)
    candidate_source = read_tsv(CANDIDATE_SOURCE)
    reader = load_module("gdt441_reader_for_validation", READER_PATH)

    current_by_id = {row["event_id"]: row for row in current}
    private_keys = {(row["held_page"], row["private_target_recipe"]) for row in private}
    private_source_keys = {(row["held_page"], row["private_target_recipe"]) for row in private_source}
    candidate_by_recipe = {row["candidate_recipe"]: row for row in candidates}
    candidate_source_by_recipe = {row["candidate_recipe"]: row for row in candidate_source}
    private_counts = Counter(row["factor_replay_decision"] for row in private)
    candidate_gate_counts = Counter(row["factor_gate_status"] for row in candidates)
    candidate_cross = Counter((row["current_status"], row["factor_gate_status"]) for row in candidates)

    state_fields = [
        "state_bank_was_new", "active_action_before", "active_argument_before",
        "explicit_action_roots", "explicit_argument_roots", "inherited_action_root",
        "inherited_argument_root", "active_action_after", "active_argument_after",
    ]
    synthetic = [
        {"event_id": "T1", "statement_id": "ST1", "physical_page": "TEST", "register": "HERBAL", "owner_de": "OWNER", "surface": "x1", "component_recipe": "OK+Y"},
        {"event_id": "T2", "statement_id": "ST1", "physical_page": "TEST", "register": "HERBAL", "owner_de": "OWNER", "surface": "x2", "component_recipe": "AIIN+AIN+S+Y"},
        {"event_id": "T3", "statement_id": "ST1", "physical_page": "TEST", "register": "HERBAL", "owner_de": "OWNER", "surface": "x3", "component_recipe": "A_ADDR+T+S+OR"},
        {"event_id": "T4", "statement_id": "ST1", "physical_page": "TEST", "register": "HERBAL", "owner_de": "OWNER", "surface": "x4", "component_recipe": "AIIN+DY"},
    ]
    synthetic_rows = reader.stream_rows(synthetic)
    with tempfile.TemporaryDirectory(prefix="gdt441_validate_") as tmp:
        input_path = Path(tmp) / "input.tsv"
        output_path = Path(tmp) / "output.tsv"
        with input_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(synthetic[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(synthetic)
        subprocess.run(
            ["python3", str(READER_PATH), "--input", str(input_path), "--output", str(output_path)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        cli_synthetic_rows = read_tsv(output_path)

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    inventory_counts = {row["factor_family"]: int(row["rule_count"]) for row in inventory}
    checks = {
        "current_4576_unique": len(current) == len(current_by_id) == 4576,
        "current_event_set_matches_gdt438_gdt440": set(current_by_id) == set(gdt438) == set(gdt440),
        "current_recipe_surface_page_match": all(
            all(row[field] == gdt440[row["event_id"]][field] for field in ("component_recipe", "surface", "physical_page"))
            for row in current
        ),
        "current_state_matches_gdt438": all(
            all(row[field] == gdt438[row["event_id"]][field] for field in state_fields)
            for row in current
        ),
        "current_clause_literal_matches_gdt440": all(
            row["reader_clause_de"] == gdt440[row["event_id"]]["order_safe_clause_de"]
            and row["ordered_literal_reading_de"] == gdt440[row["event_id"]]["ordered_literal_reading_de"]
            and row["dual_channel_reading_de"] == gdt440[row["event_id"]]["dual_channel_reading_de"]
            for row in current
        ),
        "current_match_flags_all_yes": all(row["state_clause_literal_match_gdt440"] == "YES" for row in current),
        "current_all_exact_catalog": all(row["component_recipe"] in catalog and row["recipe_source"] == "EXACT_CATALOG_KEY" for row in current),
        "current_factor_status_4566_10": Counter(row["factor_gate_status"] for row in current) == {
            "FACTOR_GREEN_CROSS_PAGE": 4566,
            "FACTOR_AMBER_LOCAL_APPENDIX": 10,
        },
        "current_selectors_nonempty": all(row["scope_selector_rules"] != "" for row in current),
        "private_861_unique": len(private) == len(private_keys) == 861,
        "private_keys_match_source": private_keys == private_source_keys,
        "private_decisions_853_8_0": private_counts == {"READ_GREEN": 853, "READ_AMBER": 8},
        "private_no_stop_or_block": all(row["factor_replay_decision"] != "STOP" and row["blocked_factor_rules"] == "NONE" for row in private),
        "private_literal_matches_source": all(row["factor_conditional_reading_de"] == row["target_reading_de"] for row in private),
        "private_never_occurrence_prediction": all(row["occurrence_prediction"] == "NO__VISIBLE_RECIPE_REQUIRED" for row in private),
        "candidate_4938_unique": len(candidates) == len(candidate_by_recipe) == 4938,
        "candidate_recipes_match_source": set(candidate_by_recipe) == set(candidate_source_by_recipe),
        "candidate_source_columns_match": all(
            row["current_status"] == candidate_source_by_recipe[row["candidate_recipe"]]["current_status"]
            and row["source_neighbor_count"] == candidate_source_by_recipe[row["candidate_recipe"]]["source_neighbor_count"]
            for row in candidates
        ),
        "candidate_gate_counts_exact": candidate_gate_counts == {
            "FACTOR_GREEN_CROSS_PAGE": 4476,
            "FACTOR_AMBER_LOCAL_APPENDIX": 193,
            "STOP__UNLICENSED_FACTOR": 269,
        },
        "candidate_cross_counts_exact": candidate_cross == {
            ("ABSENT", "FACTOR_GREEN_CROSS_PAGE"): 4114,
            ("ABSENT", "FACTOR_AMBER_LOCAL_APPENDIX"): 189,
            ("ABSENT", "STOP__UNLICENSED_FACTOR"): 263,
            ("OBSERVED", "FACTOR_GREEN_CROSS_PAGE"): 362,
            ("OBSERVED", "FACTOR_AMBER_LOCAL_APPENDIX"): 4,
            ("OBSERVED", "STOP__UNLICENSED_FACTOR"): 6,
        },
        "candidate_never_prediction": all(row["factor_gate_is_occurrence_prediction"] == "NO" for row in candidates),
        "candidate_gate_recomputes": all(
            all(row[field] == reader.gate_recipe(row["candidate_recipe"], "NONE")[field] for field in (
                "factor_gate_status", "scope_selector_rules", "portable_factor_rules",
                "amber_factor_rules", "blocked_factor_rules",
            )) for row in candidates
        ),
        "inventory_seven_families": len(inventory) == len(inventory_counts) == 7,
        "inventory_counts_exact": inventory_counts == {
            "PORTABLE_FOCUS_EDGE": 103,
            "LOCAL_FOCUS_EDGE": 3,
            "LOCAL_OWNER_FOCUS_EDGE": 1,
            "PORTABLE_ADJACENT_ACTION_PAIR": 31,
            "LOCAL_ADJACENT_ACTION_PAIR": 6,
            "PORTABLE_CLOSE_TARGET": 9,
            "R_POSITIONAL_TOPOLOGY": 1,
        },
        "synthetic_new_green_not_catalog": synthetic_rows[1]["reader_status"] == "READ_NEW_FACTOR_COMPOSITION" and synthetic_rows[1]["component_recipe"] not in catalog,
        "synthetic_stop_exact": synthetic_rows[2]["reader_status"] == "STOP__UNLICENSED_FACTOR" and synthetic_rows[2]["blocked_factor_rules"] == "PAIR:T>S",
        "synthetic_stop_preserves_state": synthetic_rows[2]["active_action_before"] == synthetic_rows[2]["active_action_after"] == synthetic_rows[3]["active_action_before"] == "S",
        "synthetic_resume_after_stop": synthetic_rows[3]["reader_status"] == "READ_NEW_FACTOR_COMPOSITION" and synthetic_rows[3]["active_action_after"] == "S",
        "cli_matches_module": all(
            all(cli.get(key, "") == ("" if module.get(key) is None else str(module.get(key, ""))) for key in set(cli) | set(module))
            for cli, module in zip(cli_synthetic_rows, synthetic_rows)
        ) and len(cli_synthetic_rows) == len(synthetic_rows),
        "result_status_exact": result["status"] == "ALL_PAGE_PRIVATE_RECIPES_CONDITIONALLY_READABLE__NOT_OCCURRENCE_PREDICTION",
        "result_current_exact": result["current_event_count"] == result["current_exact_replay_match_count"] == 4576,
        "result_private_exact": result["page_private_recipe_count"] == 861 and result["page_private_green_count"] == 853 and result["page_private_amber_count"] == 8 and result["page_private_stop_count"] == 0,
        "result_candidate_exact": result["candidate_recipe_count"] == 4938 and result["absent_candidate_factor_accepted_count"] == 4303,
        "result_factor_counts_exact": [
            result["portable_focus_edge_count"], result["local_focus_edge_count"],
            result["local_owner_focus_edge_count"], result["portable_action_pair_count"],
            result["local_action_pair_count"], result["portable_close_target_count"],
        ] == [103, 3, 1, 31, 6, 9],
        "result_not_prediction": result["factor_gate_occurrence_prediction"] is False,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt441_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
