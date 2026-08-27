#!/usr/bin/env python3
"""Independent validation for the exact-key GDT546 fragment reader."""

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
BASE = ROOT / "experiments/yolo/gdt546_consolidated_fragment_reader"
OUT = BASE / "artifacts"
G543 = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames/artifacts"
G544 = ROOT / "experiments/yolo/gdt544_flagged_equal_length_anchor_availability/artifacts"
G545 = ROOT / "experiments/yolo/gdt545_shorter_secondary_fragment_bridges/artifacts"

CARD_IN = G543 / "gdt543_81_fragment_extension_cards.tsv"
ARM_IN = G543 / "gdt543_93_directional_extension_arms.tsv"
FAMILY_IN = G543 / "gdt543_16_recurrent_anchor_families.tsv"
FLAG_IN = G544 / "gdt544_16_flagged_target_anchor_availability.tsv"
BRIDGE_IN = G545 / "gdt545_4_secondary_bridge_cards.tsv"
UNREPAIRED_IN = G545 / "gdt545_12_unrepaired_flagged_cards.tsv"

READER = OUT / "gdt546_81_consolidated_fragment_reader.tsv"
SUMMARY = OUT / "gdt546_fragment_reader_summary.tsv"
BOOK = OUT / "GDT546_81_CARD_FRAGMENT_READER.md"
RESULT = OUT / "gdt546_result.json"
VALIDATION = OUT / "gdt546_validation.json"
RUN = BASE / "src/run.py"
CLI = BASE / "src/read_fragment.py"
STATUS = "PASS_81_CARD_FRAGMENT_READER__4_DUAL_BRIDGES__12_EXPLICIT_DEFAULTS"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field} in {len(rows)} rows")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cards = read_tsv(CARD_IN)
    arms = read_tsv(ARM_IN)
    families = read_tsv(FAMILY_IN)
    flags = read_tsv(FLAG_IN)
    bridges = read_tsv(BRIDGE_IN)
    unrepaired = read_tsv(UNREPAIRED_IN)
    reader = read_tsv(READER)
    summary_rows = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    book = BOOK.read_text(encoding="utf-8")

    card_map = keyed(cards, "surface")
    reader_map = keyed(reader, "surface")
    flag_map = keyed(flags, "surface")
    bridge_map = keyed(bridges, "surface")
    unrepaired_map = keyed(unrepaired, "surface")
    family_map = keyed(families, "anchor_recipe")
    arm_map = {(row["target_surface"], row["side"]): row for row in arms}
    summary = {row["metric"]: row["value"] for row in summary_rows}

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("source_card_count", len(cards) == 81, len(cards))
    check("source_arm_count", len(arms) == 93 and len(arm_map) == 93, [len(arms), len(arm_map)])
    check("source_family_count", len(families) == 16, len(families))
    check("source_flag_count", len(flags) == 16, len(flags))
    check("source_bridge_count", len(bridges) == 4, len(bridges))
    check("source_unrepaired_count", len(unrepaired) == 12, len(unrepaired))
    check("reader_card_count", len(reader) == 81 and len(reader_map) == 81, [len(reader), len(reader_map)])
    check("reader_surface_set_exact", set(reader_map) == set(card_map), sorted(set(reader_map) ^ set(card_map)))
    check(
        "bridge_default_partition",
        set(bridge_map) | set(unrepaired_map) == set(flag_map)
        and not (set(bridge_map) & set(unrepaired_map)),
        [sorted(bridge_map), sorted(unrepaired_map)],
    )

    copied_fields = {
        "final_recipe": "final_recipe",
        "observed_requirement_modes": "observed_requirement_modes",
        "neutral_component_reading_de": "neutral_surface_phrase_de",
        "known_contextual_readings_de": "known_contextual_readings_de",
        "primary_anchor_recipe": "anchor_recipe",
        "primary_anchor_start_atom": "anchor_start_atom",
        "primary_anchor_atom_count": "anchor_atom_count",
        "primary_anchor_old_event_count": "old_anchor_event_count",
        "primary_anchor_old_surfaces": "old_anchor_surfaces",
        "primary_visible_stem_status": "visible_stem_status",
        "primary_visible_stem_surface": "visible_stem_surface",
        "extension_direction": "extension_direction",
        "left_extension_recipe": "left_extension_recipe",
        "left_visible_affix": "visible_left_extension",
        "right_extension_recipe": "right_extension_recipe",
        "right_visible_affix": "visible_right_extension",
        "primary_old_supported_interfaces": "old_supported_interface_count",
        "primary_interface_count": "interface_count",
        "primary_full_arm_joint_count": "full_arm_joint_count",
        "primary_repeated_invariant_channel_count": "repeated_invariant_visible_channel_count",
        "primary_anchor_context_modes": "anchor_context_modes",
        "primary_anchor_context_relation": "anchor_context_relation",
        "old_supercard_recipe_count": "old_supercard_recipe_count",
        "old_supercard_recipes": "old_supercard_recipes",
        "old_supercard_context_relation": "old_supercard_context_relation",
        "primary_structural_support_class": "structural_support_class",
        "working_default": "working_default",
    }
    copy_errors = []
    for surface, source in card_map.items():
        target = reader_map[surface]
        for target_field, source_field in copied_fields.items():
            if target[target_field] != source[source_field]:
                copy_errors.append([surface, target_field, target[target_field], source[source_field]])
    check("all_gdt543_card_fields_copied", not copy_errors, copy_errors[:10])

    formula_errors = []
    for surface, row in reader_map.items():
        reconstructed = row["primary_structural_formula"].replace("[", "").replace("]", "")
        if reconstructed != row["final_recipe"]:
            formula_errors.append([surface, reconstructed, row["final_recipe"]])
    check("primary_structural_formula_replay", not formula_errors, formula_errors)

    aligned_visible_errors = []
    for surface, row in reader_map.items():
        if row["primary_visible_stem_status"] != "ALIGNED_EXACT_OLD_SURFACE_STEM":
            continue
        reconstructed = (
            row["primary_visible_formula"]
            .replace("[", "")
            .replace("]", "")
            .replace("+", "")
        )
        if reconstructed != surface:
            aligned_visible_errors.append([surface, reconstructed])
    check("aligned_visible_formula_replay", not aligned_visible_errors, aligned_visible_errors)

    arm_errors = []
    side_fields = {
        "LEFT": {
            "visible_channel_class": "left_channel_class",
            "visible_channel_observation_count": "left_channel_observation_count",
            "visible_channel_recipe_variants": "left_channel_recipe_variants",
            "interface_pair": "left_interface_pair",
            "old_interface_event_count": "left_interface_old_event_count",
        },
        "RIGHT": {
            "visible_channel_class": "right_channel_class",
            "visible_channel_observation_count": "right_channel_observation_count",
            "visible_channel_recipe_variants": "right_channel_recipe_variants",
            "interface_pair": "right_interface_pair",
            "old_interface_event_count": "right_interface_old_event_count",
        },
    }
    for (surface, side), arm in arm_map.items():
        row = reader_map[surface]
        for source_field, target_field in side_fields[side].items():
            if row[target_field] != arm[source_field]:
                arm_errors.append([surface, side, target_field, row[target_field], arm[source_field]])
    check("all_93_arm_fields_copied", not arm_errors, arm_errors[:10])

    absent_arm_errors = []
    for surface, row in reader_map.items():
        for side in ("LEFT", "RIGHT"):
            if (surface, side) in arm_map:
                continue
            if row[f"{side.lower()}_channel_class"] != "NONE":
                absent_arm_errors.append([surface, side])
    check("absent_arm_channels_marked_none", not absent_arm_errors, absent_arm_errors)

    family_errors = []
    for surface, row in reader_map.items():
        family = family_map.get(row["primary_anchor_recipe"])
        expected = family["target_count"] if family else "1"
        if row["recurrent_primary_anchor_family_target_count"] != expected:
            family_errors.append([surface, row["primary_anchor_recipe"], expected])
    check("anchor_family_counts_replay", not family_errors, family_errors)

    flag_errors = []
    for surface, row in reader_map.items():
        expected = flag_map[surface]["flag_reasons"] if surface in flag_map else "NONE"
        if row["initial_flag_reasons"] != expected:
            flag_errors.append([surface, row["initial_flag_reasons"], expected])
    check("initial_flags_replay", not flag_errors, flag_errors)

    bridge_fields = {
        "secondary_anchor_recipe": "secondary_anchor_recipe",
        "secondary_visible_stem_status": "secondary_visible_stem_status",
        "secondary_visible_stem_surface": "secondary_visible_stem_surface",
        "secondary_context_relation": "secondary_context_relation",
        "secondary_supported_interfaces": "secondary_supported_interfaces",
        "secondary_interface_count": "secondary_interface_count",
        "secondary_repaired_dimension": "repaired_dimension",
    }
    bridge_errors = []
    for surface, bridge in bridge_map.items():
        row = reader_map[surface]
        if row["secondary_bridge_present"] != "YES":
            bridge_errors.append([surface, "missing"])
        for target_field, source_field in bridge_fields.items():
            if row[target_field] != bridge[source_field]:
                bridge_errors.append([surface, target_field, row[target_field], bridge[source_field]])
        reconstructed = row["secondary_structural_formula"].replace("[", "").replace("]", "")
        if reconstructed != row["final_recipe"]:
            bridge_errors.append([surface, "formula", reconstructed, row["final_recipe"]])
    check("four_secondary_bridges_replay", not bridge_errors, bridge_errors)
    check(
        "secondary_bridge_inventory",
        {surface for surface, row in reader_map.items() if row["secondary_bridge_present"] == "YES"}
        == set(bridge_map),
        sorted(bridge_map),
    )

    default_inventory = {
        surface
        for surface, row in reader_map.items()
        if row["flag_resolution"] == "EXPLICIT_WORKING_DEFAULT__NO_QUALIFIED_SECONDARY"
    }
    check("twelve_explicit_defaults_replay", default_inventory == set(unrepaired_map), sorted(default_inventory))
    check(
        "all_cards_have_working_reading",
        all(row["neutral_component_reading_de"] and row["known_contextual_readings_de"] for row in reader),
        sum(bool(row["neutral_component_reading_de"]) for row in reader),
    )
    check(
        "all_reader_decisions_exact",
        {row["reader_decision"] for row in reader} == {"READ_KNOWN_FRAGMENT_WORKING_CARD"},
        sorted({row["reader_decision"] for row in reader}),
    )
    check(
        "guard_exact_key_only",
        {row["guard"] for row in reader}
        == {"EXACT_SURFACE_KEY_ONLY__NO_FUZZY_EXTENSION_OR_NEW_MEANING"},
        sorted({row["guard"] for row in reader}),
    )

    counts = {
        "reader_card_count": len(reader),
        "exact_surface_key_count": len(reader_map),
        "directional_arm_count": len(arms),
        "aligned_primary_visible_stem_count": sum(
            row["primary_visible_stem_status"] == "ALIGNED_EXACT_OLD_SURFACE_STEM" for row in reader
        ),
        "direction_mismatch_primary_visible_stem_count": sum(
            row["primary_visible_stem_status"] == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM"
            for row in reader
        ),
        "no_exact_primary_visible_stem_count": sum(
            row["primary_visible_stem_status"] == "NO_EXACT_OLD_SURFACE_STEM" for row in reader
        ),
        "primary_context_compatible_count": sum(row["primary_context_compatible"] == "YES" for row in reader),
        "primary_context_default_count": sum(row["primary_context_compatible"] == "NO" for row in reader),
        "primary_old_supported_interface_count": sum(int(row["primary_old_supported_interfaces"]) for row in reader),
        "primary_interface_count": sum(int(row["primary_interface_count"]) for row in reader),
        "targets_with_recurrent_invariant_channel_count": sum(
            int(row["primary_repeated_invariant_channel_count"]) > 0 for row in reader
        ),
        "targets_in_recurrent_primary_anchor_family_count": sum(
            int(row["recurrent_primary_anchor_family_target_count"]) > 1 for row in reader
        ),
        "old_supercard_target_count": sum(int(row["old_supercard_recipe_count"]) > 0 for row in reader),
        "initial_flagged_card_count": len(flag_map),
        "secondary_bridge_card_count": len(bridge_map),
        "unresolved_explicit_default_count": len(unrepaired_map),
        "known_surface_read_count": len(reader),
    }
    expected_counts = {
        "reader_card_count": 81,
        "exact_surface_key_count": 81,
        "directional_arm_count": 93,
        "aligned_primary_visible_stem_count": 72,
        "direction_mismatch_primary_visible_stem_count": 1,
        "no_exact_primary_visible_stem_count": 8,
        "primary_context_compatible_count": 69,
        "primary_context_default_count": 12,
        "primary_old_supported_interface_count": 87,
        "primary_interface_count": 93,
        "targets_with_recurrent_invariant_channel_count": 34,
        "targets_in_recurrent_primary_anchor_family_count": 34,
        "old_supercard_target_count": 8,
        "initial_flagged_card_count": 16,
        "secondary_bridge_card_count": 4,
        "unresolved_explicit_default_count": 12,
        "known_surface_read_count": 81,
    }
    check("core_metric_replay", counts == expected_counts, counts)
    check(
        "summary_core_metric_replay",
        all(summary.get(key) == str(value) for key, value in counts.items()),
        {key: summary.get(key) for key in counts},
    )
    expected_result = {
        **counts,
        "status": STATUS,
        "unknown_surface_policy": "STOP_UNKNOWN_FRAGMENT_SURFACE",
        "primary_anchor_changes": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "new_pages": 0,
    }
    check("result_exact", result == expected_result, result)

    known_probe = subprocess.run(
        [sys.executable, str(CLI), "--surface", "chepakeo", "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    known_payload = json.loads(known_probe.stdout) if known_probe.returncode == 0 else {}
    check(
        "known_cli_probe",
        known_probe.returncode == 0
        and known_payload.get("final_recipe") == card_map["chepakeo"]["final_recipe"]
        and known_payload.get("secondary_anchor_recipe") == "E+O",
        {"returncode": known_probe.returncode, "recipe": known_payload.get("final_recipe")},
    )
    unknown_probe = subprocess.run(
        [sys.executable, str(CLI), "--surface", "not_an_exact_fragment", "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    unknown_payload = json.loads(unknown_probe.stdout) if unknown_probe.stdout else {}
    check(
        "unknown_cli_stops_without_fuzzy_card",
        unknown_probe.returncode == 2
        and unknown_payload
        == {
            "status": "STOP_UNKNOWN_FRAGMENT_SURFACE",
            "surface": "not_an_exact_fragment",
            "known_surface_count": 81,
            "guard": "EXACT_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE",
        },
        {"returncode": unknown_probe.returncode, "payload": unknown_payload},
    )
    list_probe = subprocess.run(
        [sys.executable, str(CLI), "--list-surfaces"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    listed = list_probe.stdout.splitlines()
    check(
        "cli_lists_exact_inventory",
        list_probe.returncode == 0 and len(listed) == 81 and set(listed) == set(reader_map),
        [list_probe.returncode, len(listed)],
    )

    check("book_status", f"Status: `{STATUS}`" in book, STATUS)
    check("book_bridge_inventory", all(f"`{surface}`" in book for surface in bridge_map), sorted(bridge_map))
    check("book_default_inventory", all(f"`{surface}`" in book for surface in unrepaired_map), len(unrepaired_map))

    generated = [READER, SUMMARY, BOOK, RESULT]
    before = {path.name: digest(path) for path in generated}
    rerun = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = {path.name: digest(path) for path in generated}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout[-1000:] + rerun.stderr[-1000:])
    check("generator_byte_determinism", before == after, after)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
