#!/usr/bin/env python3
"""Build the GDT470 core-mutation replay and future address worksheet."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"
OUT = BASE / "artifacts"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G468 = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"
G469 = ROOT / "experiments/yolo/gdt469_provenance_aware_address_reader"
sys.path.insert(0, str(G466 / "src"))
sys.path.insert(0, str(G469 / "src"))
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, read_tsv, select_function_channels  # noqa: E402
from support_lib import supported_intake  # noqa: E402
from worksheet_lib import OLD_CARRIER_TIERS, WORKSHEET_FIELDS  # noqa: E402


def write_tsv(
    path: Path,
    rows: list[dict[str, object]],
    fieldnames: list[str] | None = None,
) -> None:
    columns = fieldnames or (list(rows[0]) if rows else None)
    if not columns:
        raise ValueError(f"No columns supplied for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def channel_shape(signature: str, rule_map: dict[str, dict[str, str]]) -> str:
    if signature == "NONE":
        return "NONE"
    return "+".join(rule_map[channel_id]["channel_kind"] for channel_id in signature.split("+"))


def count_columns(rows: list[dict[str, object]], key: str, values: list[str]) -> dict[str, int]:
    counts = Counter(str(row[key]) for row in rows)
    return {value.lower(): counts[value] for value in values}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rules = read_tsv(G466 / "artifacts/gdt466_44_function_channel_deck.tsv")
    families = read_tsv(G466 / "artifacts/gdt466_18_owner_family_channel_deck.tsv")
    probes = read_tsv(G466 / "artifacts/gdt466_89_unseen_core_insertion_probes.tsv")
    recipes = read_tsv(G468 / "artifacts/gdt468_2300_recipe_support_atlas.tsv")
    shells = read_tsv(G468 / "artifacts/gdt468_2760_supported_shell_phrasebook.tsv")
    recipe_map = {row["flattened_recipe_trace"]: row for row in recipes}
    shell_map = {row["exact_channel_signature"]: row for row in shells}
    rule_map = {row["channel_id"]: row for row in rules}

    def read_cold(surface: str, content_class: str) -> dict[str, object]:
        return supported_intake(
            surface,
            content_class,
            rules,
            families,
            {},
            recipe_map,
            shell_map,
            intake,
            select_function_channels,
        )

    replay_rows: list[dict[str, object]] = []
    for ordinal, probe in enumerate(probes, start=1):
        source = read_cold(probe["source_surface"], probe["content_class"])
        observed = read_cold(probe["synthetic_unseen_surface"], probe["content_class"])
        signature_stable = source["exact_channel_signature"] == observed["exact_channel_signature"]
        recipe_stable = source["ordered_recipe_trace"] == observed["ordered_recipe_trace"]
        tier_stable = (
            source["recipe_support_tier"] == observed["recipe_support_tier"]
            and source["recipe_support_rank"] == observed["recipe_support_rank"]
        )
        shell_stable = source["bounded_shell_id"] == observed["bounded_shell_id"]
        reading_stable = observed["reading_de"] == probe["observed_reading_de"]
        passed = (
            probe["probe_pass"] == "YES"
            and probe["observed_route"] == observed["route"]
            and probe["expected_function_mask"] == probe["observed_function_mask"]
            and signature_stable
            and recipe_stable
            and tier_stable
            and shell_stable
            and reading_stable
        )
        replay_rows.append({
            "replay_id": f"G470-U{ordinal:03d}",
            "source_probe_id": probe["probe_id"],
            "source_surface": probe["source_surface"],
            "synthetic_unseen_surface": probe["synthetic_unseen_surface"],
            "content_class": probe["content_class"],
            "insertion_index": probe["insertion_index"],
            "expected_function_mask": probe["expected_function_mask"],
            "observed_function_mask": probe["observed_function_mask"],
            "source_cold_route": source["route"],
            "observed_route": observed["route"],
            "source_channel_signature": source["exact_channel_signature"],
            "observed_channel_signature": observed["exact_channel_signature"],
            "shell_shape": channel_shape(str(observed["exact_channel_signature"]), rule_map),
            "source_ordered_recipe_trace": source["ordered_recipe_trace"],
            "observed_ordered_recipe_trace": observed["ordered_recipe_trace"],
            "source_recipe_support_tier": source["recipe_support_tier"],
            "observed_recipe_support_tier": observed["recipe_support_tier"],
            "source_recipe_support_rank": source["recipe_support_rank"],
            "observed_recipe_support_rank": observed["recipe_support_rank"],
            "source_bounded_shell_id": source["bounded_shell_id"],
            "observed_bounded_shell_id": observed["bounded_shell_id"],
            "bounded_shell_match": observed["bounded_shell_match"],
            "running_event_count": observed["running_event_count"],
            "running_page_count": observed["running_page_count"],
            "address_full_formula_count": observed["address_full_formula_count"],
            "address_hybrid_shell_count": observed["address_hybrid_shell_count"],
            "observed_reading_de": observed["reading_de"],
            "signature_stable": "YES" if signature_stable else "NO",
            "recipe_stable": "YES" if recipe_stable else "NO",
            "tier_and_rank_stable": "YES" if tier_stable else "NO",
            "shell_id_stable": "YES" if shell_stable else "NO",
            "reading_stable": "YES" if reading_stable else "NO",
            "replay_pass": "YES" if passed else "NO",
        })
    write_tsv(OUT / "gdt470_89_supported_unseen_core_replay.tsv", replay_rows)

    tier_values = [
        "RUNNING_EXACT_RECIPE",
        "ADDRESS_FULL_FORMULA_ONLY",
        "ADDRESS_HYBRID_SHELL_ONLY",
        "COMPOSITION_ONLY",
        "OUTSIDE_BOUNDED_SHELL_ATLAS",
    ]
    content_rows: list[dict[str, object]] = []
    for content_class in sorted({str(row["content_class"]) for row in replay_rows}):
        subset = [row for row in replay_rows if row["content_class"] == content_class]
        tier_counts = count_columns(subset, "observed_recipe_support_tier", tier_values)
        content_rows.append({
            "content_class": content_class,
            "probe_count": len(subset),
            "shell_shape_count": len({row["shell_shape"] for row in subset}),
            "function_shell_route_count": sum(row["observed_route"] == "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE" for row in subset),
            "whole_name_route_count": sum(row["observed_route"] == "WHOLE_LEARNED_OWNER_NAME" for row in subset),
            "running_exact_recipe_count": tier_counts["running_exact_recipe"],
            "address_full_formula_only_count": tier_counts["address_full_formula_only"],
            "address_hybrid_shell_only_count": tier_counts["address_hybrid_shell_only"],
            "composition_only_count": tier_counts["composition_only"],
            "outside_bounded_shell_atlas_count": tier_counts["outside_bounded_shell_atlas"],
            "old_carrier_backed_count": sum(row["observed_recipe_support_tier"] in OLD_CARRIER_TIERS for row in subset),
            "bounded_shell_match_count": sum(row["bounded_shell_match"] == "YES" for row in subset),
            "all_five_invariants_stable_count": sum(
                all(row[key] == "YES" for key in ("signature_stable", "recipe_stable", "tier_and_rank_stable", "shell_id_stable", "reading_stable"))
                for row in subset
            ),
            "replay_pass_count": sum(row["replay_pass"] == "YES" for row in subset),
        })
    write_tsv(OUT / "gdt470_4_content_class_stability.tsv", content_rows)

    shape_rows: list[dict[str, object]] = []
    for shape in sorted({str(row["shell_shape"]) for row in replay_rows}):
        subset = [row for row in replay_rows if row["shell_shape"] == shape]
        tier_counts = count_columns(subset, "observed_recipe_support_tier", tier_values)
        class_counts = Counter(str(row["content_class"]) for row in subset)
        shape_rows.append({
            "shell_shape": shape,
            "probe_count": len(subset),
            "content_class_count": len(class_counts),
            "content_class_distribution": "|".join(f"{key}:{class_counts[key]}" for key in sorted(class_counts)),
            "running_exact_recipe_count": tier_counts["running_exact_recipe"],
            "address_full_formula_only_count": tier_counts["address_full_formula_only"],
            "address_hybrid_shell_only_count": tier_counts["address_hybrid_shell_only"],
            "composition_only_count": tier_counts["composition_only"],
            "outside_bounded_shell_atlas_count": tier_counts["outside_bounded_shell_atlas"],
            "old_carrier_backed_count": sum(row["observed_recipe_support_tier"] in OLD_CARRIER_TIERS for row in subset),
            "bounded_shell_match_count": sum(row["bounded_shell_match"] == "YES" for row in subset),
            "all_five_invariants_stable_count": sum(
                all(row[key] == "YES" for key in ("signature_stable", "recipe_stable", "tier_and_rank_stable", "shell_id_stable", "reading_stable"))
                for row in subset
            ),
            "replay_pass_count": sum(row["replay_pass"] == "YES" for row in subset),
        })
    write_tsv(OUT / "gdt470_11_shell_shape_stability.tsv", shape_rows)

    decisions = [
        {"priority": 1, "working_state": "EXACT_KNOWN_LABEL", "trigger": "visible surface has an exact label card", "default_action": "REUSE_EXACT_LABEL_CARD", "meaning_policy": "return its complete old working reading", "provenance_policy": "report recipe tier but do not rematch the card as a shell"},
        {"priority": 2, "working_state": "SUPPORTED_FULL_FUNCTION_FORMULA", "trigger": "all characters are function channels and recipe has an old carrier", "default_action": "READ_SUPPORTED_FULL_FUNCTION_FORMULA", "meaning_policy": "compose all frozen component values", "provenance_policy": "report the strongest old carrier tier"},
        {"priority": 3, "working_state": "SUPPORTED_FUNCTION_SHELL", "trigger": "visible function channels surround a learned core and recipe has an old carrier", "default_action": "READ_SUPPORTED_FUNCTION_SHELL_KEEP_NAME_CORE", "meaning_policy": "read functions and retain the core as owner-class name", "provenance_policy": "report the strongest old carrier tier"},
        {"priority": 4, "working_state": "COMPOSITION_ONLY", "trigger": "visible channels form a bounded atlas recipe without an old whole-recipe carrier", "default_action": "READ_COMPOSED_FUNCTION_SHELL_KEEP_NAME_CORE", "meaning_policy": "compose functions and retain any core as owner-class name", "provenance_policy": "mark composition-only explicitly"},
        {"priority": 5, "working_state": "VISIBLE_FUNCTIONS_OUTSIDE_ATLAS", "trigger": "one-sided or other visible function channel shape is outside the bounded atlas", "default_action": "READ_VISIBLE_FUNCTION_SHELL_KEEP_NAME_CORE", "meaning_policy": "read visible functions and retain the remainder as owner-class name", "provenance_policy": "mark outside-atlas; do not erase visible functions"},
        {"priority": 6, "working_state": "STRICT_OWNER_FAMILY", "trigger": "no function channel but an owner-class family marker matches", "default_action": "KEEP_OWNER_FAMILY_AND_LEARN_NAME", "meaning_policy": "retain family marker and default the whole item to its owner class", "provenance_policy": "do not invent a recipe"},
        {"priority": 7, "working_state": "WHOLE_OWNER_NAME", "trigger": "no exact card, function channel or owner-family marker matches", "default_action": "LEARN_WHOLE_OWNER_BOUND_NAME", "meaning_policy": "every character remains inside one owner-class name", "provenance_policy": "mark outside-atlas with zero carrier counts"},
    ]
    write_tsv(OUT / "gdt470_7_intake_decision_catalog.tsv", decisions)

    page_slots = [
        {
            "page_slot": f"PAGE_SLOT_{ordinal}",
            "release_status": "UNRELEASED",
            "page_id": "PENDING_USER_RELEASE",
            "source_reference": "PENDING",
            "source_sha256": "PENDING",
            "address_item_count": "PENDING",
            "intake_status": "NOT_STARTED",
            "notes": "Do not populate before user release",
        }
        for ordinal in range(1, 5)
    ]
    write_tsv(OUT / "gdt470_four_page_address_slots.tsv", page_slots)
    write_tsv(OUT / "gdt470_address_item_template.tsv", [], WORKSHEET_FIELDS)

    contract = {
        "status": "FUTURE_ADDRESS_INTAKE_WORKSHEET_READY",
        "page_slots": 4,
        "page_slot_state": "UNRELEASED",
        "base_precedence": "EXACT_LABEL_THEN_FUNCTION_CHANNELS_THEN_OWNER_FAMILY_THEN_WHOLE_OWNER_NAME",
        "provenance_is_annotation_only": True,
        "all_visible_sequences_receive_a_default": True,
        "opaque_default_form": "[OWNER_CLASS_NAME:VISIBLE_REMAINDER]",
        "required_manual_capture": ["page_id", "locus_id", "owner_description", "content_class", "selected_surface", "available_ZL3b_IT2a_RF1b_readings"],
        "reader_command": "python3 experiments/yolo/gdt470_future_address_intake_worksheet/src/prepare_future_address.py SURFACE CONTENT_CLASS [metadata options]",
        "claim_boundary": "The worksheet records a working meaning and recipe provenance after a form is supplied; it predicts neither a new surface nor an individual object name.",
    }
    (OUT / "gdt470_future_address_intake_contract.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tiers = Counter(str(row["observed_recipe_support_tier"]) for row in replay_rows)
    routes = Counter(str(row["observed_route"]) for row in replay_rows)
    result = {
        "status": "MUTATED_NAME_CORES_PRESERVE_READING_AND_PROVENANCE__WORKSHEET_READY",
        "unseen_core_probe_count": len(replay_rows),
        "unseen_core_probe_pass_count": sum(row["replay_pass"] == "YES" for row in replay_rows),
        "channel_signature_stable_count": sum(row["signature_stable"] == "YES" for row in replay_rows),
        "ordered_recipe_stable_count": sum(row["recipe_stable"] == "YES" for row in replay_rows),
        "support_tier_and_rank_stable_count": sum(row["tier_and_rank_stable"] == "YES" for row in replay_rows),
        "bounded_shell_id_stable_count": sum(row["shell_id_stable"] == "YES" for row in replay_rows),
        "working_reading_stable_count": sum(row["reading_stable"] == "YES" for row in replay_rows),
        "content_class_counts": dict(sorted(Counter(str(row["content_class"]) for row in replay_rows).items())),
        "route_counts": dict(sorted(routes.items())),
        "recipe_support_tier_counts": dict(sorted(tiers.items())),
        "old_recipe_carrier_backed_count": sum(row["observed_recipe_support_tier"] in OLD_CARRIER_TIERS for row in replay_rows),
        "bounded_shell_match_count": sum(row["bounded_shell_match"] == "YES" for row in replay_rows),
        "shell_shape_count": len(shape_rows),
        "future_page_slots": len(page_slots),
        "released_page_slots": sum(row["release_status"] != "UNRELEASED" for row in page_slots),
        "new_pages": 0,
        "new_channels": 0,
        "new_component_meanings": 0,
        "new_surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt470_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
