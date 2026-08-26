#!/usr/bin/env python3
"""Validate GDT467 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt467_bounded_shell_composition_atlas"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
RULE_PATH = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake/artifacts/gdt466_44_function_channel_deck.tsv"

PHRASEBOOK = OUT / "gdt467_2760_shell_phrasebook.tsv"
COVERAGE = OUT / "gdt467_44_channel_compositional_coverage.tsv"
PROBES = OUT / "gdt467_8280_multicore_precedence_probes.tsv"
COLLISIONS = OUT / "gdt467_signature_collision_atlas.tsv"
RESULT = OUT / "gdt467_result.json"
VALIDATION = OUT / "gdt467_validation.json"
GENERATED = (PHRASEBOOK, COVERAGE, PROBES, COLLISIONS, RESULT)
CORE_MARKERS = {"x", "zx", "xvz"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    rules = read_tsv(RULE_PATH)
    shells = read_tsv(PHRASEBOOK)
    coverage = read_tsv(COVERAGE)
    probes = read_tsv(PROBES)
    collisions = read_tsv(COLLISIONS)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rule_map = {row["channel_id"]: row for row in rules}
    prefixes = [row for row in rules if row["channel_kind"] == "PREFIX"]
    suffixes = [row for row in rules if row["channel_kind"] == "SUFFIX"]
    internals = [row for row in rules if row["channel_kind"] == "INTERNAL"]

    check("rule_count", len(rules) == 44 and len(rule_map) == 44, f"observed={len(rules)}")
    check("rule_kind_counts", Counter(row["channel_kind"] for row in rules) == Counter({"PREFIX": 12, "SUFFIX": 23, "INTERNAL": 9}), str(Counter(row["channel_kind"] for row in rules)))
    check("core_marker_safety", all(not any(row["surface_stem"] in marker for row in internals) for marker in CORE_MARKERS), "no marker contains internal stem")

    check("phrasebook_count", len(shells) == 2760, f"observed={len(shells)}")
    check("phrasebook_ids", [row["shell_id"] for row in shells] == [f"G467-S{i:04d}" for i in range(1, 2761)], "S0001-S2760")
    shape_counts = Counter(row["shell_shape"] for row in shells)
    check("phrasebook_shape_counts", shape_counts == Counter({"PREFIX_CORE_SUFFIX": 276, "PREFIX_CORE_INTERNAL_CORE_SUFFIX": 2484}), str(shape_counts))
    check("phrasebook_unique_templates", len({row["surface_template"] for row in shells}) == 2760, "all templates unique")
    check("phrasebook_unique_channel_signatures", len({row["exact_channel_signature"] for row in shells}) == 2760, "all exact traces unique")
    check("phrasebook_recipe_signature_count", len({row["flattened_recipe_trace"] for row in shells}) == 2300, f"observed={len({row['flattened_recipe_trace'] for row in shells})}")
    check("phrasebook_literal_signature_count", len({row["literal_working_reading_de"] for row in shells}) == 2400, f"observed={len({row['literal_working_reading_de'] for row in shells})}")
    check("phrasebook_owner_placeholders", all("[OWNER_NAME:" in row["literal_working_reading_de"] for row in shells), "all preserve opaque core")

    expected_pair_keys = {(prefix["channel_id"], suffix["channel_id"]) for prefix in prefixes for suffix in suffixes}
    observed_pair_keys = {(row["prefix_channel_id"], row["suffix_channel_id"]) for row in shells if row["shell_shape"] == "PREFIX_CORE_SUFFIX"}
    check("pair_cartesian_complete", observed_pair_keys == expected_pair_keys and len(expected_pair_keys) == 276, "12x23")
    expected_triple_keys = {(prefix["channel_id"], internal["channel_id"], suffix["channel_id"]) for prefix in prefixes for internal in internals for suffix in suffixes}
    observed_triple_keys = {(row["prefix_channel_id"], row["internal_channel_id"], row["suffix_channel_id"]) for row in shells if row["shell_shape"] == "PREFIX_CORE_INTERNAL_CORE_SUFFIX"}
    check("triple_cartesian_complete", observed_triple_keys == expected_triple_keys and len(expected_triple_keys) == 2484, "12x9x23")

    recipe_ok = True
    trace_ok = True
    template_ok = True
    for row in shells:
        selected_ids = [row["prefix_channel_id"]]
        if row["internal_channel_id"] != "NONE":
            selected_ids.append(row["internal_channel_id"])
        selected_ids.append(row["suffix_channel_id"])
        selected = [rule_map[rule_id] for rule_id in selected_ids]
        recipe_ok &= row["flattened_recipe_trace"] == "+".join(rule["component_recipe"] for rule in selected)
        trace_ok &= row["exact_channel_signature"] == "+".join(selected_ids)
        if len(selected) == 2:
            expected_template = selected[0]["surface_stem"] + "{NAME_CORE}" + selected[1]["surface_stem"]
        else:
            expected_template = selected[0]["surface_stem"] + "{NAME_CORE_1}" + selected[1]["surface_stem"] + "{NAME_CORE_2}" + selected[2]["surface_stem"]
        template_ok &= row["surface_template"] == expected_template
    check("phrasebook_flat_recipes", recipe_ok, "all recipes flatten source channels")
    check("phrasebook_channel_traces", trace_ok, "all traces exact")
    check("phrasebook_templates", template_ok, "all templates exact")

    check("probe_count", len(probes) == 8280, f"observed={len(probes)}")
    check("probe_ids", [row["probe_id"] for row in probes] == [f"G467-P{i:05d}" for i in range(1, 8281)], "P00001-P08280")
    check("probe_core_counts", Counter(row["core_marker"] for row in probes) == Counter({"x": 2760, "zx": 2760, "xvz": 2760}), str(Counter(row["core_marker"] for row in probes)))
    check("probe_shape_counts", Counter(row["shell_shape"] for row in probes) == Counter({"PREFIX_CORE_SUFFIX": 828, "PREFIX_CORE_INTERNAL_CORE_SUFFIX": 7452}), str(Counter(row["shell_shape"] for row in probes)))
    check("probe_shell_counts", all(count == 3 for count in Counter(row["shell_id"] for row in probes).values()) and len({row["shell_id"] for row in probes}) == 2760, "three markers per shell")
    check("probe_routes", all(row["observed_route"] == "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE" for row in probes), "8280 shell routes")
    check("probe_channels", all(row["expected_channel_ids"] == row["observed_channel_ids"] for row in probes), "8280 intended traces")
    check("probe_character_counts", all(row["expected_known_character_count"] == row["observed_known_character_count"] and row["expected_learned_character_count"] == row["observed_learned_character_count"] for row in probes), "all counts exact")
    check("probe_no_precedence_collision", all(row["precedence_collision"] == "NO" for row in probes), "0/8280")
    check("probe_all_pass", all(row["probe_pass"] == "YES" for row in probes), "8280/8280")

    check("coverage_count", len(coverage) == 44 and {row["channel_id"] for row in coverage} == set(rule_map), f"observed={len(coverage)}")
    coverage_map = {row["channel_id"]: row for row in coverage}
    prefix_counts_ok = all((row["expected_pair_probe_count"], row["expected_triple_probe_count"], row["expected_total_probe_count"]) == ("69", "621", "690") for row in coverage if row["channel_kind"] == "PREFIX")
    suffix_counts_ok = all((row["expected_pair_probe_count"], row["expected_triple_probe_count"], row["expected_total_probe_count"]) == ("36", "324", "360") for row in coverage if row["channel_kind"] == "SUFFIX")
    internal_counts_ok = all((row["expected_pair_probe_count"], row["expected_triple_probe_count"], row["expected_total_probe_count"]) == ("0", "828", "828") for row in coverage if row["channel_kind"] == "INTERNAL")
    check("coverage_prefix_counts", prefix_counts_ok, "69 pair + 621 triple each")
    check("coverage_suffix_counts", suffix_counts_ok, "36 pair + 324 triple each")
    check("coverage_internal_counts", internal_counts_ok, "828 triple each")
    check("coverage_selected_counts", all(row["expected_total_probe_count"] == row["selected_total_probe_count"] and row["missed_probe_count"] == "0" for row in coverage), "all selected")
    check("coverage_status", all(row["coverage_status"] == "COMPLETE" for row in coverage), "44/44")
    check("coverage_source_values", all(row["surface_stem"] == rule_map[row["channel_id"]]["surface_stem"] and row["component_recipe"] == rule_map[row["channel_id"]]["component_recipe"] and row["literal_working_value_de"] == rule_map[row["channel_id"]]["literal_working_value_de"] for row in coverage), "all source values exact")

    recipe_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    literal_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in shells:
        recipe_groups[row["flattened_recipe_trace"]].append(row)
        literal_groups[row["literal_working_reading_de"]].append(row)
    repeated_recipes = {key: rows for key, rows in recipe_groups.items() if len(rows) > 1}
    expected_collision_keys = set(repeated_recipes)
    check("collision_count", len(collisions) == 423 and len(repeated_recipes) == 423, f"observed={len(collisions)}")
    check("collision_kind", all(row["collision_kind"] == "SAME_FLATTENED_RECIPE__MULTIPLE_CHANNEL_FACTORIZATIONS" for row in collisions), "recipe factorizations only")
    check("collision_signature_set", {row["signature"] for row in collisions} == expected_collision_keys, "all repeated recipes once")
    collision_map = {row["signature"]: row for row in collisions}
    check("collision_member_counts", all(int(collision_map[key]["member_count"]) == len(rows) for key, rows in repeated_recipes.items()), "all group sizes exact")
    check("collision_shell_members", all(collision_map[key]["shell_ids"].split("|") == [row["shell_id"] for row in rows] for key, rows in repeated_recipes.items()), "all shell lists exact")
    group_sizes = Counter(len(rows) for rows in repeated_recipes.values())
    check("collision_size_distribution", group_sizes == Counter({2: 395, 3: 20, 4: 7, 5: 1}), str(group_sizes))
    check("collision_member_total", sum(len(rows) for rows in repeated_recipes.values()) == 883, "883 shells in repeated recipes")
    check("collision_max_group", max(len(rows) for rows in repeated_recipes.values()) == 5 and collision_map["OT+OL+AIIN"]["member_count"] == "5", "OT+OL+AIIN has five factorizations")
    cross_shape = sum(len({row["shell_shape"] for row in rows}) > 1 for rows in repeated_recipes.values())
    check("collision_cross_shape", cross_shape == 86, f"observed={cross_shape}")
    same_literal_different_recipe = sum(len({row["flattened_recipe_trace"] for row in rows}) > 1 for rows in literal_groups.values())
    check("no_literal_different_recipe", same_literal_different_recipe == 0, f"observed={same_literal_different_recipe}")
    check("collision_disposition", all(row["disposition"] == "KEEP_EXACT_CHANNEL_TRACE__READING_VALUE_UNCHANGED" for row in collisions), "exact trace retained")

    check("result_status", result["status"] == "ALL_BOUNDED_SHELL_COMPOSITIONS_PRESERVE_INTENDED_CHANNELS", result["status"])
    check("result_channel_counts", (result["prefix_channel_count"], result["suffix_channel_count"], result["internal_channel_count"]) == (12, 23, 9), str(result))
    check("result_shell_counts", result["pair_shell_count"] == 276 and result["triple_shell_count"] == 2484 and result["base_shell_count"] == 2760, str(result))
    check("result_probe_counts", result["opaque_core_marker_count"] == 3 and result["precedence_probe_count"] == result["precedence_probe_pass_count"] == 8280 and result["precedence_collision_count"] == 0, str(result))
    check("result_signature_counts", result["exact_channel_signature_count"] == 2760 and result["duplicate_exact_channel_signature_count"] == 0 and result["flattened_recipe_signature_count"] == 2300 and result["literal_working_reading_signature_count"] == 2400, str(result))
    check("result_collision_counts", result["same_recipe_factorization_group_count"] == 423 and result["same_recipe_factorization_member_count"] == 883 and result["same_recipe_factorization_max_group_size"] == 5 and result["same_recipe_factorization_group_size_distribution"] == {"2": 395, "3": 20, "4": 7, "5": 1} and result["cross_shape_same_recipe_group_count"] == 86, str(result))
    check("result_channel_coverage", result["complete_channel_coverage_count"] == 44, str(result["complete_channel_coverage_count"]))
    check("result_claim_ceiling", result["new_pages"] == result["new_channels"] == result["new_component_meanings"] == result["surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {"status": "PASS" if failed == 0 else "FAIL", "check_count": len(checks), "passed": passed, "failed": failed, "checks": checks}
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
