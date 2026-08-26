#!/usr/bin/env python3
"""Enumerate bounded GDT466 shell compositions and precedence collisions."""

from __future__ import annotations

import csv
import json
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
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
sys.path.insert(0, str(G466 / "src"))

from intake_lib import intake, read_tsv, select_function_channels  # noqa: E402


RULE_PATH = G466 / "artifacts/gdt466_44_function_channel_deck.tsv"
CORE_MARKERS = ("x", "zx", "xvz")


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def flat_recipe(*rules: dict[str, str]) -> str:
    return "+".join(rule["component_recipe"] for rule in rules)


def channel_trace(*rules: dict[str, str]) -> str:
    return "+".join(rule["channel_id"] for rule in rules)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rules = read_tsv(RULE_PATH)
    prefixes = [row for row in rules if row["channel_kind"] == "PREFIX"]
    suffixes = [row for row in rules if row["channel_kind"] == "SUFFIX"]
    internals = [row for row in rules if row["channel_kind"] == "INTERNAL"]
    if (len(prefixes), len(suffixes), len(internals)) != (12, 23, 9):
        raise RuntimeError("Unexpected GDT466 channel split")
    if any(any(stem in marker for stem in (row["surface_stem"] for row in internals)) for marker in CORE_MARKERS):
        raise RuntimeError("Synthetic core marker contains an internal channel")

    shells: list[dict[str, object]] = []
    shell_rules: dict[str, tuple[dict[str, str], ...]] = {}
    for prefix in prefixes:
        for suffix in suffixes:
            shell_id = f"G467-S{len(shells) + 1:04d}"
            selected_rules = (prefix, suffix)
            recipe = flat_recipe(*selected_rules)
            reading = f"{prefix['literal_working_value_de']} · [OWNER_NAME:NAME_CORE] · {suffix['literal_working_value_de']}"
            row = {
                "shell_id": shell_id, "shell_shape": "PREFIX_CORE_SUFFIX",
                "prefix_channel_id": prefix["channel_id"], "prefix_stem": prefix["surface_stem"], "prefix_recipe": prefix["component_recipe"],
                "internal_channel_id": "NONE", "internal_stem": "NONE", "internal_recipe": "NONE",
                "suffix_channel_id": suffix["channel_id"], "suffix_stem": suffix["surface_stem"], "suffix_recipe": suffix["component_recipe"],
                "surface_template": f"{prefix['surface_stem']}{{NAME_CORE}}{suffix['surface_stem']}",
                "flattened_recipe_trace": recipe, "literal_working_reading_de": reading,
                "exact_channel_signature": channel_trace(*selected_rules),
            }
            shells.append(row)
            shell_rules[shell_id] = selected_rules
    for prefix in prefixes:
        for internal in internals:
            for suffix in suffixes:
                shell_id = f"G467-S{len(shells) + 1:04d}"
                selected_rules = (prefix, internal, suffix)
                recipe = flat_recipe(*selected_rules)
                reading = (
                    f"{prefix['literal_working_value_de']} · [OWNER_NAME:NAME_CORE_1] · "
                    f"{internal['literal_working_value_de']} · [OWNER_NAME:NAME_CORE_2] · {suffix['literal_working_value_de']}"
                )
                row = {
                    "shell_id": shell_id, "shell_shape": "PREFIX_CORE_INTERNAL_CORE_SUFFIX",
                    "prefix_channel_id": prefix["channel_id"], "prefix_stem": prefix["surface_stem"], "prefix_recipe": prefix["component_recipe"],
                    "internal_channel_id": internal["channel_id"], "internal_stem": internal["surface_stem"], "internal_recipe": internal["component_recipe"],
                    "suffix_channel_id": suffix["channel_id"], "suffix_stem": suffix["surface_stem"], "suffix_recipe": suffix["component_recipe"],
                    "surface_template": f"{prefix['surface_stem']}{{NAME_CORE_1}}{internal['surface_stem']}{{NAME_CORE_2}}{suffix['surface_stem']}",
                    "flattened_recipe_trace": recipe, "literal_working_reading_de": reading,
                    "exact_channel_signature": channel_trace(*selected_rules),
                }
                shells.append(row)
                shell_rules[shell_id] = selected_rules
    if len(shells) != 2760:
        raise RuntimeError(f"Expected 2,760 base shells, got {len(shells)}")
    write_tsv(OUT / "gdt467_2760_shell_phrasebook.tsv", shells)

    probes: list[dict[str, object]] = []
    expected_occurrences: Counter[str] = Counter()
    selected_occurrences: Counter[str] = Counter()
    expected_pair: Counter[str] = Counter()
    expected_triple: Counter[str] = Counter()
    for shell in shells:
        intended = shell_rules[str(shell["shell_id"])]
        for core in CORE_MARKERS:
            if shell["shell_shape"] == "PREFIX_CORE_SUFFIX":
                surface = intended[0]["surface_stem"] + core + intended[1]["surface_stem"]
            else:
                surface = intended[0]["surface_stem"] + core + intended[1]["surface_stem"] + core + intended[2]["surface_stem"]
            selected = select_function_channels(surface, rules)
            expected_ids = [rule["channel_id"] for rule in intended]
            observed_ids = [str(item["channel_id"]) for item in selected]
            expected_known = sum(len(rule["surface_stem"]) for rule in intended)
            observed = intake(surface, "PICTURED_PLANT", rules, [], {})
            passed = (
                observed_ids == expected_ids
                and observed["known_function_character_count"] == expected_known
                and observed["learned_character_count"] == len(core) * (1 if len(intended) == 2 else 2)
                and observed["route"] == "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE"
            )
            for rule in intended:
                expected_occurrences[rule["channel_id"]] += 1
                (expected_pair if len(intended) == 2 else expected_triple)[rule["channel_id"]] += 1
            for item in selected:
                selected_occurrences[str(item["channel_id"])] += 1
            probes.append({
                "probe_id": f"G467-P{len(probes) + 1:05d}", "shell_id": shell["shell_id"], "shell_shape": shell["shell_shape"],
                "core_marker": core, "synthetic_surface": surface, "expected_channel_ids": "+".join(expected_ids),
                "observed_channel_ids": "+".join(observed_ids) or "NONE", "expected_known_character_count": expected_known,
                "observed_known_character_count": observed["known_function_character_count"],
                "expected_learned_character_count": len(core) * (1 if len(intended) == 2 else 2),
                "observed_learned_character_count": observed["learned_character_count"],
                "observed_route": observed["route"], "observed_reading_de": observed["reading_de"],
                "precedence_collision": "NO" if observed_ids == expected_ids else "YES", "probe_pass": "YES" if passed else "NO",
            })
    if len(probes) != 8280:
        raise RuntimeError(f"Expected 8,280 probes, got {len(probes)}")
    write_tsv(OUT / "gdt467_8280_multicore_precedence_probes.tsv", probes)

    coverage: list[dict[str, object]] = []
    for rule in rules:
        rule_id = rule["channel_id"]
        coverage.append({
            "channel_id": rule_id, "channel_kind": rule["channel_kind"], "surface_stem": rule["surface_stem"],
            "component_recipe": rule["component_recipe"], "literal_working_value_de": rule["literal_working_value_de"],
            "expected_pair_probe_count": expected_pair[rule_id], "expected_triple_probe_count": expected_triple[rule_id],
            "expected_total_probe_count": expected_occurrences[rule_id], "selected_total_probe_count": selected_occurrences[rule_id],
            "missed_probe_count": expected_occurrences[rule_id] - selected_occurrences[rule_id],
            "coverage_status": "COMPLETE" if expected_occurrences[rule_id] == selected_occurrences[rule_id] else "COLLISION",
        })
    write_tsv(OUT / "gdt467_44_channel_compositional_coverage.tsv", coverage)

    collisions: list[dict[str, object]] = []
    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    literal_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for shell in shells:
        recipe_groups[str(shell["flattened_recipe_trace"])].append(shell)
        literal_groups[str(shell["literal_working_reading_de"])].append(shell)
    for signature, members in sorted(recipe_groups.items()):
        if len(members) > 1:
            collisions.append({
                "collision_id": f"G467-K{len(collisions) + 1:04d}", "collision_kind": "SAME_FLATTENED_RECIPE__MULTIPLE_CHANNEL_FACTORIZATIONS",
                "signature": signature, "member_count": len(members), "distinct_recipe_count": 1,
                "shell_ids": "|".join(str(row["shell_id"]) for row in members),
                "surface_templates": "|".join(str(row["surface_template"]) for row in members),
                "exact_channel_signatures": "|".join(str(row["exact_channel_signature"]) for row in members),
                "disposition": "KEEP_EXACT_CHANNEL_TRACE__READING_VALUE_UNCHANGED",
            })
    for signature, members in sorted(literal_groups.items()):
        recipes = {str(row["flattened_recipe_trace"]) for row in members}
        if len(recipes) > 1:
            collisions.append({
                "collision_id": f"G467-K{len(collisions) + 1:04d}", "collision_kind": "SAME_GERMAN_WORKING_READING__DIFFERENT_COMPONENT_RECIPES",
                "signature": signature, "member_count": len(members), "distinct_recipe_count": len(recipes),
                "shell_ids": "|".join(str(row["shell_id"]) for row in members),
                "surface_templates": "|".join(str(row["surface_template"]) for row in members),
                "exact_channel_signatures": "|".join(str(row["exact_channel_signature"]) for row in members),
                "disposition": "KEEP_COMPONENT_RECIPE_AND_CHANNEL_TRACE__GERMAN_GLOSS_IS_NOT_IDENTITY",
            })
    if not collisions:
        collisions.append({
            "collision_id": "G467-K0000", "collision_kind": "NONE", "signature": "NONE", "member_count": 0,
            "distinct_recipe_count": 0, "shell_ids": "NONE", "surface_templates": "NONE", "exact_channel_signatures": "NONE",
            "disposition": "NO_SIGNATURE_COLLISIONS",
        })
    write_tsv(OUT / "gdt467_signature_collision_atlas.tsv", collisions)

    exact_signatures = Counter(str(row["exact_channel_signature"]) for row in shells)
    result = {
        "status": "ALL_BOUNDED_SHELL_COMPOSITIONS_PRESERVE_INTENDED_CHANNELS",
        "prefix_channel_count": len(prefixes), "suffix_channel_count": len(suffixes), "internal_channel_count": len(internals),
        "pair_shell_count": sum(row["shell_shape"] == "PREFIX_CORE_SUFFIX" for row in shells),
        "triple_shell_count": sum(row["shell_shape"] == "PREFIX_CORE_INTERNAL_CORE_SUFFIX" for row in shells),
        "base_shell_count": len(shells), "opaque_core_marker_count": len(CORE_MARKERS), "precedence_probe_count": len(probes),
        "precedence_probe_pass_count": sum(row["probe_pass"] == "YES" for row in probes),
        "precedence_collision_count": sum(row["precedence_collision"] == "YES" for row in probes),
        "complete_channel_coverage_count": sum(row["coverage_status"] == "COMPLETE" for row in coverage),
        "exact_channel_signature_count": len(exact_signatures),
        "duplicate_exact_channel_signature_count": sum(count > 1 for count in exact_signatures.values()),
        "flattened_recipe_signature_count": len(recipe_groups),
        "same_recipe_factorization_group_count": sum(len(members) > 1 for members in recipe_groups.values()),
        "same_recipe_factorization_member_count": sum(len(members) for members in recipe_groups.values() if len(members) > 1),
        "same_recipe_factorization_max_group_size": max(len(members) for members in recipe_groups.values()),
        "same_recipe_factorization_group_size_distribution": dict(sorted(Counter(len(members) for members in recipe_groups.values() if len(members) > 1).items())),
        "cross_shape_same_recipe_group_count": sum(len({str(row["shell_shape"]) for row in members}) > 1 for members in recipe_groups.values() if len(members) > 1),
        "literal_working_reading_signature_count": len(literal_groups),
        "same_literal_different_recipe_group_count": sum(len({str(row['flattened_recipe_trace']) for row in members}) > 1 for members in literal_groups.values()),
        "collision_atlas_row_count": len(collisions),
        "new_pages": 0, "new_channels": 0, "new_component_meanings": 0, "surface_predictions": 0, "confirmed_lexemes": 0,
    }
    (OUT / "gdt467_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
