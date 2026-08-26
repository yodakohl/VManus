#!/usr/bin/env python3
"""Validate GDT435's context-safe replay, fallback, and order controls."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt435_observed_recipe_shadow_fallback"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def invoke_reader(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        ["python3", str(BASE / "src/context_safe_read_recipe.py"), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def main() -> int:
    tracked = [
        OUT / "gdt435_2465_context_key_map.tsv",
        OUT / "gdt435_1766_recipe_register_ambiguity.tsv",
        OUT / "gdt435_4576_event_shadow_replay.tsv",
        OUT / "gdt435_1268_recipe_jackknife.tsv",
        OUT / "gdt435_49_order_reversal_controls.tsv",
        OUT / "gdt435_121_catalog_phrase_collisions.tsv",
        OUT / "gdt435_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    contexts = read_tsv(tracked[0])
    ambiguity = read_tsv(tracked[1])
    replay = read_tsv(tracked[2])
    jackknife = read_tsv(tracked[3])
    reversals = read_tsv(tracked[4])
    collisions = read_tsv(tracked[5])
    result = json.loads(tracked[6].read_text(encoding="utf-8"))
    source = read_tsv(CLAUSES)
    source_by_event = {row["global_running_event_id"]: row for row in source}
    context_by_id = {row["context_key_id"]: row for row in contexts}

    singleton = [row for row in jackknife if int(row["current_event_count"]) == 1]
    singleton_counts = Counter(row["one_event_jackknife_outcome"] for row in singleton)
    all_fallback_counts = Counter(row["regenerated_fallback_rank"] for row in jackknife)
    reversal_counts = Counter(row["reversed_intake_tier"] for row in reversals)
    ambiguous = [row for row in ambiguity if row["context_required"] == "YES"]

    ambiguous_probe = invoke_reader("--recipe", "AIIN", "--register", "HERBAL")
    event_probe = invoke_reader("--recipe", "AIIN", "--register", "HERBAL", "--event-id", "G407-E0231")
    state_probe = invoke_reader(
        "--recipe", "AIIN", "--register", "HERBAL",
        "--owner", "zweiknolliges blauköpfiges Heilkraut",
        "--inherited-action", "OK", "--inherited-argument", "NONE",
    )
    future_probe = invoke_reader("--recipe", "AL+AIN", "--register", "BIOLOGICAL")
    stop_probe = invoke_reader("--recipe", "AIIN+AIN+S+Y", "--register", "HERBAL")

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    checks = {
        "event_replay_rows_4576": len(replay) == 4576 and len({row["event_id"] for row in replay}) == 4576,
        "event_replay_matches_source_ids": {row["event_id"] for row in replay} == set(source_by_event),
        "event_replay_source_alignment": all(
            row["component_recipe"] == source_by_event[row["event_id"]]["component_recipe"]
            and row["register"] == source_by_event[row["event_id"]]["register"]
            and row["actual_context_clause_de"] == source_by_event[row["event_id"]]["imperative_clause_de"]
            for row in replay
        ),
        "all_observed_events_t0": all(row["catalog_tier"] == "T0_EXACT_OBSERVED" for row in replay),
        "recipe_register_keys_1766": len(ambiguity) == 1766 and len({(row["component_recipe"], row["register"]) for row in ambiguity}) == 1766,
        "ambiguous_keys_276": len(ambiguous) == 276,
        "ambiguous_events_2162": sum(int(row["event_count"]) for row in ambiguous) == 2162,
        "naive_first_mismatches_1401": sum(int(row["naive_first_clause_mismatch_count"]) for row in ambiguity) == 1401 and sum(row["naive_first_clause_matches_actual"] == "NO" for row in replay) == 1401,
        "context_keys_2465": len(contexts) == 2465 and len(context_by_id) == 2465,
        "context_keys_tuple_unique": len({(row["component_recipe"], row["register"], row["inherited_action_root"], row["inherited_argument_root"]) for row in contexts}) == 2465,
        "context_keys_clause_unique": all(int(row["distinct_clause_count"]) == 1 and row["unique_clause_de"] != "CONFLICT" for row in contexts),
        "all_replay_context_links_valid": all(
            row["context_key_id"] in context_by_id
            and row["context_key_clause_unique"] == "YES"
            and context_by_id[row["context_key_id"]]["component_recipe"] == row["component_recipe"]
            and context_by_id[row["context_key_id"]]["unique_clause_de"] == row["actual_context_clause_de"]
            for row in replay
        ),
        "jackknife_recipe_rows_1268": len(jackknife) == 1268 and len({row["component_recipe"] for row in jackknife}) == 1268,
        "jackknife_event_total_4576": sum(int(row["current_event_count"]) for row in jackknife) == 4576,
        "singletons_836": len(singleton) == 836,
        "one_event_exact_survival_3740": sum(int(row["current_event_count"]) for row in jackknife if int(row["current_event_count"]) > 1) == 3740,
        "singleton_fallback_counts_exact": singleton_counts == Counter({
            "NO_NEIGHBOR__STOP": 681,
            "ONE_NEIGHBOR__STOP": 105,
            "REGENERATED_NARROW": 36,
            "REGENERATED_STRONG": 13,
            "REGENERATED_HIGH": 1,
        }),
        "all_recipe_fallback_counts_exact": all_fallback_counts == Counter({
            "NO_NEIGHBOR__STOP": 896,
            "ONE_NEIGHBOR__STOP": 185,
            "REGENERATED_NARROW": 88,
            "REGENERATED_STRONG": 64,
            "REGENERATED_HIGH": 35,
        }),
        "fixed_reader_deletion_stops_all": all(row["whole_recipe_deletion_fixed_reader_outcome"] == "T5_STOP__FIXED_PREDICTIVE_TIERS_ARE_DISJOINT" for row in jackknife),
        "reversal_rows_49": len(reversals) == 49 and len({row["component_recipe"] for row in reversals}) == 49,
        "reversal_counts_exact": reversal_counts == Counter({"T5_NO_LICENSED_RECIPE": 36, "T0_EXACT_OBSERVED": 7, "T4_NARROW_APPENDIX": 3, "T2_FUTURE_STRONG": 3}),
        "reversal_exact_keys_distinct": all(row["exact_key_keeps_distinct"] == "YES" for row in reversals),
        "catalog_collision_groups_121": len(collisions) == 121 and len({row["generic_workshop_phrase_de"] for row in collisions}) == 121,
        "catalog_collision_recipes_261": sum(int(row["recipe_count"]) for row in collisions) == 261,
        "collision_match_rule_exact": all(row["matcher_rule"] == "EXACT_COMPONENT_RECIPE_ONLY__NEVER_PHRASE" for row in collisions),
        "ambiguous_probe_safe": ambiguous_probe["match_status"] == "EXACT_OBSERVED_RECIPE__CONTEXT_REQUIRED" and "observed_event_id" not in ambiguous_probe and ambiguous_probe["available_clause_variant_count"] == 7,
        "event_probe_exact": event_probe["match_status"] == "EXACT_OBSERVED_EVENT_CONTEXT" and event_probe["reading_de"] == source_by_event["G407-E0231"]["imperative_clause_de"],
        "state_probe_exact": state_probe["match_status"] == "EXACT_OBSERVED_CONTEXT_STATE" and state_probe["reading_de"] == source_by_event["G407-E0231"]["imperative_clause_de"],
        "future_probe_unchanged": future_probe["intake_tier"] == "T1_FUTURE_HIGH" and future_probe["match_status"] == "EXACT_MAIN_FUTURE_CARD",
        "stop_probe_stops": stop_probe["intake_tier"] == "T5_NO_LICENSED_RECIPE" and str(stop_probe["match_status"]).endswith("__STOP"),
        "result_status_exact": result["status"] == "CONTEXT_SAFE_READER_REQUIRED__49_CARD_DECK_UNCHANGED",
        "result_counts_exact": result["event_shadow_replay_count"] == 4576 and result["ambiguous_recipe_register_key_count"] == 276 and result["naive_first_clause_mismatch_event_count"] == 1401 and result["context_state_key_count"] == 2465 and result["context_state_conflict_count"] == 0,
        "no_meaning_surface_page_change": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_page_in_outputs": "f84" not in output_text.lower(),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt435_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
