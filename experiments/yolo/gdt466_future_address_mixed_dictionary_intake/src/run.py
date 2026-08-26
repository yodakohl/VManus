#!/usr/bin/env python3
"""Compile and replay the frozen mixed-dictionary address intake gate."""

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
BASE = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
OUT = BASE / "artifacts"
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, matching_families, read_tsv, select_function_channels  # noqa: E402


LABEL_PATH = ROOT / "experiments/yolo/gdt465_oiil_cross_reading_renderer_closure/artifacts/gdt465_107_final_hybrid_dictionary.tsv"
EDGE_PATH = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_27_calibrated_edge_stems.tsv"
INTERNAL_PATH = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts/gdt461_9_calibrated_internal_stems.tsv"
FAMILY_PATH = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_17_owner_class_family_stems.tsv"
CHEO_PATH = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts/gdt461_residual_owner_family_bridge.tsv"
AR_PATH = ROOT / "experiments/yolo/gdt462_near_threshold_ar_edge_exception_audit/artifacts/gdt462_residual_edge_channel_inventory.tsv"
THIN_PATH = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges/artifacts/gdt463_4_bridge_decisions.tsv"
BRIDGE_PATH = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge/artifacts/gdt464_4_bridge_decisions.tsv"


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def truth_mask(row: dict[str, str]) -> list[int]:
    surface = row["surface"]
    mask = [0] * len(surface)
    prefix = row["prefix_stem"]
    if prefix != "NONE":
        if not surface.startswith(prefix):
            raise RuntimeError(f"Bad prefix in frozen label: {surface} / {prefix}")
        for position in range(len(prefix)):
            mask[position] = 1
    suffix = row["suffix_stem"]
    if suffix != "NONE":
        if not surface.endswith(suffix):
            raise RuntimeError(f"Bad suffix in frozen label: {surface} / {suffix}")
        for position in range(len(surface) - len(suffix), len(surface)):
            mask[position] = 1
    if row["internal_stem_trace"] != "NONE":
        for token in row["internal_stem_trace"].split("|"):
            position_text, remainder = token.split(":", 1)
            stem, _recipe = remainder.split("=", 1)
            start = int(position_text)
            if surface[start:start + len(stem)] != stem:
                raise RuntimeError(f"Bad internal stem in frozen label: {surface} / {token}")
            for position in range(start, start + len(stem)):
                mask[position] = 1
    if sum(mask) != int(row["known_function_character_count"]):
        raise RuntimeError(f"Frozen mask count mismatch: {surface}")
    return mask


def selected_mask(surface: str, selected: list[dict[str, object]]) -> list[int]:
    mask = [0] * len(surface)
    for item in selected:
        for position in range(int(item["start"]), int(item["end"])):
            if mask[position]:
                raise RuntimeError(f"Overlapping intake intervals on {surface}")
            mask[position] = 1
    return mask


def trace(selected: list[dict[str, object]]) -> str:
    return "|".join(
        f"{item['start']}:{item['end']}:{item['surface_stem']}={item['component_recipe']}@{item['channel_id']}"
        for item in selected
    ) or "NONE"


def compile_rules() -> list[dict[str, str]]:
    raw: list[dict[str, str]] = []
    for row in read_tsv(EDGE_PATH):
        raw.append({
            "source_experiment": "GDT460", "source_rule_id": row["edge_stem_id"],
            "channel_kind": row["edge"], "surface_stem": row["surface_stem"],
            "component_recipe": row["component_recipe"], "literal_working_value_de": row["literal_working_value_de"],
            "calibration_type_count": row["running_extension_type_count"], "matching_type_count": row["running_matching_type_count"],
            "calibration_precision": row["running_type_precision"], "calibration_pages": row["running_matching_pages"],
            "admission_basis": "CALIBRATED_DIRECTIONAL_EDGE",
        })
    for row in read_tsv(INTERNAL_PATH):
        raw.append({
            "source_experiment": "GDT461", "source_rule_id": row["internal_stem_id"],
            "channel_kind": "INTERNAL", "surface_stem": row["surface_stem"],
            "component_recipe": row["component_recipe"], "literal_working_value_de": row["literal_working_value_de"],
            "calibration_type_count": row["running_internal_extension_type_count"], "matching_type_count": row["running_matching_type_count"],
            "calibration_precision": row["running_type_precision"], "calibration_pages": row["running_matching_pages"],
            "admission_basis": "CALIBRATED_STRICT_INTERNAL",
        })
    promoted_ar = [row for row in read_tsv(AR_PATH) if row["decision"] == "PROMOTE_AFTER_PACKAGE_EXCEPTION"]
    if len(promoted_ar) != 1:
        raise RuntimeError("Expected one promoted GDT462 channel")
    row = promoted_ar[0]
    raw.append({
        "source_experiment": "GDT462", "source_rule_id": "G462-PREFIX-ar",
        "channel_kind": row["edge"], "surface_stem": row["surface_stem"],
        "component_recipe": row["component_recipe"], "literal_working_value_de": row["literal_working_value_de"],
        "calibration_type_count": row["running_extension_type_count"], "matching_type_count": row["running_matching_type_count"],
        "calibration_precision": row["running_type_precision"], "calibration_pages": "PACKAGE_EXCEPTION_TWO_PAGES",
        "admission_basis": "NAMED_REPEATED_RELATION_PACKAGE_EXCEPTION",
    })
    for row in read_tsv(THIN_PATH):
        raw.append({
            "source_experiment": "GDT463", "source_rule_id": row["bridge_id"],
            "channel_kind": row["edge"], "surface_stem": row["surface_stem"],
            "component_recipe": row["component_recipe"], "literal_working_value_de": row["literal_working_value_de"],
            "calibration_type_count": row["edge_extension_type_count"], "matching_type_count": row["edge_matching_type_count"],
            "calibration_precision": row["edge_type_precision"], "calibration_pages": row["recipe_sequence_page_count"],
            "admission_basis": "EXACT_CARD_EDGE_PLUS_DISTRIBUTED_RECIPE_SEQUENCE",
        })
    for row in read_tsv(BRIDGE_PATH):
        channel_kind = row["channel"].split("_", 1)[0]
        if channel_kind not in {"PREFIX", "SUFFIX"}:
            continue
        raw.append({
            "source_experiment": "GDT464", "source_rule_id": row["bridge_id"],
            "channel_kind": channel_kind, "surface_stem": row["channel"].split("_", 1)[1],
            "component_recipe": row["selected_recipe"], "literal_working_value_de": row["literal_working_value_de"],
            "calibration_type_count": row["calibration_candidate_type_count"], "matching_type_count": row["calibration_matching_type_count"],
            "calibration_precision": row["calibration_precision"], "calibration_pages": row["matching_page_count"],
            "admission_basis": row["channel_kind"],
        })
    if len(raw) != 44:
        raise RuntimeError(f"Expected 44 frozen function channels, got {len(raw)}")
    if len({(row["channel_kind"], row["surface_stem"]) for row in raw}) != len(raw):
        raise RuntimeError("Duplicate direction/stem function rule")
    ordered = sorted(raw, key=lambda row: ({"PREFIX": 0, "SUFFIX": 1, "INTERNAL": 2}[row["channel_kind"]], -len(row["surface_stem"]), row["surface_stem"], row["source_rule_id"]))
    return [{"channel_id": f"G466-C{ordinal:02d}", **row} for ordinal, row in enumerate(ordered, start=1)]


def compile_families() -> list[dict[str, str]]:
    raw: list[dict[str, str]] = []
    for row in read_tsv(FAMILY_PATH):
        raw.append({
            "source_experiment": "GDT460", "source_rule_id": row["family_stem_id"],
            "surface_stem": row["surface_substring"], "working_family_value_de": row["working_family_value_de"],
            "content_class": row["content_class"], "support_surface_count": row["label_count"],
            "support_pages": row["pages"], "selection_rule": row["selection_rule"],
        })
    for row in read_tsv(CHEO_PATH):
        raw.append({
            "source_experiment": "GDT461", "source_rule_id": row["residual_family_bridge_id"],
            "surface_stem": row["surface_substring"], "working_family_value_de": row["working_family_value_de"],
            "content_class": row["content_class"], "support_surface_count": row["unique_address_surface_count"],
            "support_pages": row["pages"], "selection_rule": row["selection_rule"],
        })
    if len(raw) != 18:
        raise RuntimeError(f"Expected 18 frozen owner-family channels, got {len(raw)}")
    ordered = sorted(raw, key=lambda row: (row["content_class"], -len(row["surface_stem"]), row["surface_stem"], row["source_rule_id"]))
    return [{"family_id": f"G466-F{ordinal:02d}", **row} for ordinal, row in enumerate(ordered, start=1)]


def revise_dictionary(source: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    revised: list[dict[str, object]] = []
    corrections: list[dict[str, object]] = []
    for ordinal, old in enumerate(source, start=1):
        row: dict[str, object] = {
            "gdt466_label_id": f"G466-L{ordinal:03d}",
            **old,
            "gdt466_hybrid_status": old["gdt465_hybrid_status"],
            "gdt466_change": "UNCHANGED_FROM_GDT465",
            "gdt466_decision_evidence": "NOT_IN_PROPAGATION_GAP",
        }
        if old["surface"] == "ararchodaiin":
            row.update({
                "surface_segmentation": "ar|ar|[DROGENNAME:cho]|daiin",
                "prefix_stem": "ar", "prefix_recipe": "AR",
                "known_function_character_count": 9, "remaining_learned_character_count": 3,
                "known_function_fraction": "0.750000", "ordered_function_recipe_trace": "AR+AR+AIIN",
                "revised_short_default_de": "AUSGANG · AUSGANG · [DROGENNAME:cho] · WERT",
                "gdt466_change": "GDT462_AR_PREFIX_PROPAGATION_COMPLETED",
                "gdt466_decision_evidence": "FROZEN_PREFIX_ar_APPLIES_BEFORE_OLD_INTERNAL_ar_AND_SUFFIX_daiin",
            })
            corrections.append({
                "surface": old["surface"], "source_event_id": old["source_event_id"], "physical_page": old["physical_page"],
                "content_class": old["content_class"], "accepted_channel": "PREFIX ar=AR",
                "old_known_function_character_count": old["known_function_character_count"], "new_known_function_character_count": 9,
                "old_segmentation": old["surface_segmentation"], "new_segmentation": row["surface_segmentation"],
                "old_default_de": old["revised_short_default_de"], "new_default_de": row["revised_short_default_de"],
                "correction_kind": "MISSED_PROPAGATION_OF_ALREADY_ACCEPTED_GDT462_CHANNEL__NO_NEW_MEANING",
            })
        revised.append(row)
    if len(corrections) != 1:
        raise RuntimeError("Expected exactly one propagation correction")
    return revised, corrections


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_labels = read_tsv(LABEL_PATH)
    labels, corrections = revise_dictionary(source_labels)
    exact = {row["surface"]: row for row in labels}
    if len(exact) != 107:
        raise RuntimeError("Frozen labels are not surface-unique")
    rules = compile_rules()
    families = compile_families()
    write_tsv(OUT / "gdt466_44_function_channel_deck.tsv", rules)
    write_tsv(OUT / "gdt466_18_owner_family_channel_deck.tsv", families)
    write_tsv(OUT / "gdt466_propagation_correction.tsv", corrections)
    write_tsv(OUT / "gdt466_107_intake_dictionary.tsv", labels)

    exact_rows: list[dict[str, object]] = []
    cold_rows: list[dict[str, object]] = []
    core_probe_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(labels, start=1):
        production = intake(row["surface"], row["content_class"], rules, families, exact)
        exact_rows.append({
            "replay_id": f"G466-E{ordinal:03d}", "surface": row["surface"], "content_class": row["content_class"],
            "observed_route": production["route"], "observed_status": production["hybrid_status"],
            "observed_known_function_character_count": production["known_function_character_count"],
            "observed_reading_de": production["reading_de"], "source_reading_de": row["revised_short_default_de"],
            "exact_replay": "YES" if production["reading_de"] == row["revised_short_default_de"] and production["hybrid_status"] == row["gdt466_hybrid_status"] else "NO",
        })

        source_mask = truth_mask(row)
        selected = select_function_channels(row["surface"], rules)
        cold_mask = selected_mask(row["surface"], selected)
        cold = intake(row["surface"], row["content_class"], rules, families, {})
        missing = sum(expected and not observed for expected, observed in zip(source_mask, cold_mask))
        extra = sum(observed and not expected for expected, observed in zip(source_mask, cold_mask))
        relation = "EXACT" if not missing and not extra else "UNDER" if missing and not extra else "OVER" if extra and not missing else "MIXED"
        cold_rows.append({
            "replay_id": f"G466-C{ordinal:03d}", "surface": row["surface"], "content_class": row["content_class"],
            "source_status": row["gdt466_hybrid_status"], "source_function_mask": "".join(map(str, source_mask)),
            "cold_function_mask": "".join(map(str, cold_mask)), "mask_relation": relation,
            "recovered_function_character_count": sum(expected and observed for expected, observed in zip(source_mask, cold_mask)),
            "missing_function_character_count": missing, "extra_function_character_count": extra,
            "selected_channel_trace": trace(selected), "observed_route": cold["route"],
            "cold_disposition": "EXACT_PACKAGE_ONLY" if row["surface"] in {"ykyd", "yddy"} else "GENERAL_CHANNEL_REPLAY",
            "observed_reading_de": cold["reading_de"],
        })

        if 0 in source_mask:
            insert_at = source_mask.index(0) + 1
            probe_surface = row["surface"][:insert_at] + "x" + row["surface"][insert_at:]
            expected_mask = source_mask[:insert_at] + [0] + source_mask[insert_at:]
            probe_selected = select_function_channels(probe_surface, rules)
            probe_mask = selected_mask(probe_surface, probe_selected)
            probe = intake(probe_surface, row["content_class"], rules, families, exact)
            core_probe_rows.append({
                "probe_id": f"G466-U{len(core_probe_rows) + 1:03d}", "source_surface": row["surface"],
                "synthetic_unseen_surface": probe_surface, "content_class": row["content_class"],
                "insertion_index": insert_at, "expected_function_mask": "".join(map(str, expected_mask)),
                "observed_function_mask": "".join(map(str, probe_mask)),
                "expected_known_function_character_count": sum(source_mask), "observed_known_function_character_count": sum(probe_mask),
                "observed_route": probe["route"], "exact_known_route_blocked": "YES" if probe["known_label"] == "NO" else "NO",
                "selected_channel_trace": trace(probe_selected), "observed_reading_de": probe["reading_de"],
                "probe_pass": "YES" if expected_mask == probe_mask and probe["known_label"] == "NO" else "NO",
            })

    write_tsv(OUT / "gdt466_107_exact_label_replay.tsv", exact_rows)
    write_tsv(OUT / "gdt466_107_cold_shell_replay.tsv", cold_rows)
    write_tsv(OUT / "gdt466_89_unseen_core_insertion_probes.tsv", core_probe_rows)

    probe_rows: list[dict[str, object]] = []
    for rule in rules:
        kind, stem = rule["channel_kind"], rule["surface_stem"]
        surface = stem + "x" if kind == "PREFIX" else "x" + stem if kind == "SUFFIX" else "x" + stem + "x"
        selected = select_function_channels(surface, rules)
        selected_ids = [str(item["channel_id"]) for item in selected]
        observed = intake(surface, "PICTURED_PLANT", rules, families, {})
        probe_rows.append({
            "probe_id": f"G466-P{len(probe_rows) + 1:03d}", "probe_kind": "FUNCTION_CHANNEL",
            "source_rule_id": rule["channel_id"], "surface": surface, "content_class": "PICTURED_PLANT",
            "expected": f"SELECT_{rule['channel_id']}", "observed_route": observed["route"],
            "observed_function_ids": "|".join(selected_ids) or "NONE", "observed_family_ids": "NONE",
            "probe_pass": "YES" if rule["channel_id"] in selected_ids and observed["known_label"] == "NO" else "NO",
        })
    for family in families:
        surface = "x" + family["surface_stem"] + "x"
        correct = matching_families(surface, family["content_class"], families)
        correct_ids = [row["family_id"] for row in correct]
        observed = intake(surface, family["content_class"], rules, families, {})
        probe_rows.append({
            "probe_id": f"G466-P{len(probe_rows) + 1:03d}", "probe_kind": "OWNER_FAMILY_CORRECT_CLASS",
            "source_rule_id": family["family_id"], "surface": surface, "content_class": family["content_class"],
            "expected": f"MATCH_{family['family_id']}", "observed_route": observed["route"],
            "observed_function_ids": "|".join(str(item["channel_id"]) for item in select_function_channels(surface, rules)) or "NONE",
            "observed_family_ids": "|".join(correct_ids) or "NONE", "probe_pass": "YES" if family["family_id"] in correct_ids else "NO",
        })
        wrong_class = "STAR_BEARING_RING_POSITION" if family["content_class"] == "DRUG_OR_INGREDIENT_OBJECT" else "DRUG_OR_INGREDIENT_OBJECT"
        wrong = matching_families(surface, wrong_class, families)
        wrong_ids = [row["family_id"] for row in wrong]
        probe_rows.append({
            "probe_id": f"G466-P{len(probe_rows) + 1:03d}", "probe_kind": "OWNER_FAMILY_WRONG_CLASS",
            "source_rule_id": family["family_id"], "surface": surface, "content_class": wrong_class,
            "expected": f"BLOCK_{family['family_id']}", "observed_route": intake(surface, wrong_class, rules, families, {})["route"],
            "observed_function_ids": "|".join(str(item["channel_id"]) for item in select_function_channels(surface, rules)) or "NONE",
            "observed_family_ids": "|".join(wrong_ids) or "NONE", "probe_pass": "YES" if family["family_id"] not in wrong_ids else "NO",
        })
    fallback_surface = "zxqv"
    fallback = intake(fallback_surface, "PICTURED_PLANT", rules, families, {})
    probe_rows.append({
        "probe_id": f"G466-P{len(probe_rows) + 1:03d}", "probe_kind": "WHOLE_NAME_FALLBACK",
        "source_rule_id": "NONE", "surface": fallback_surface, "content_class": "PICTURED_PLANT",
        "expected": "WHOLE_LEARNED_OWNER_NAME", "observed_route": fallback["route"],
        "observed_function_ids": "NONE", "observed_family_ids": "NONE",
        "probe_pass": "YES" if fallback["route"] == "WHOLE_LEARNED_OWNER_NAME" and fallback["reading_de"] == "[PFLANZENNAME:zxqv]" else "NO",
    })
    write_tsv(OUT / "gdt466_81_channel_and_fallback_probes.tsv", probe_rows)

    contract = {
        "status": "FROZEN_MIXED_DICTIONARY_INTAKE_READY",
        "precedence": [
            {"order": 1, "route": "EXACT_KNOWN_LABEL", "rule": "Return the frozen GDT465 label reading."},
            {"order": 2, "route": "CALIBRATED_FUNCTION_CHANNELS", "rule": "Longest prefix, longest nonoverlapping suffix, then longest nonoverlapping strict-internal channels."},
            {"order": 3, "route": "STRICT_OWNER_FAMILY", "rule": "Expose only markers whose frozen content class matches the supplied owner class."},
            {"order": 4, "route": "WHOLE_LEARNED_OWNER_NAME", "rule": "Preserve every otherwise unread surface character inside an owner-class name placeholder."},
        ],
        "known_label_count": len(labels), "function_channel_count": len(rules), "owner_family_channel_count": len(families),
        "propagation_correction_count": len(corrections),
        "accepted_content_classes": ["STAR_BEARING_RING_POSITION", "DRUG_OR_INGREDIENT_OBJECT", "BATH_OR_OUTLET_STATION", "PICTURED_PLANT", "UNKNOWN_LOCAL_ADDRESS"],
        "forbidden_outputs": ["NEW_COMPONENT_MEANING", "INDIVIDUAL_OBJECT_IDENTITY", "SURFACE_PREDICTION", "CROSS_OWNER_FAMILY_TRANSFER"],
        "cli": "python3 experiments/yolo/gdt466_future_address_mixed_dictionary_intake/src/read_address.py SURFACE CONTENT_CLASS",
    }
    (OUT / "gdt466_intake_contract.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cold_relations = Counter(row["mask_relation"] for row in cold_rows)
    result = {
        "status": "FROZEN_MIXED_DICTIONARY_INTAKE_READY",
        "known_label_count": len(labels), "function_channel_count": len(rules), "owner_family_channel_count": len(families),
        "propagation_correction_count": len(corrections), "propagation_corrected_surface": "ararchodaiin",
        "exact_label_replay_pass_count": sum(row["exact_replay"] == "YES" for row in exact_rows),
        "cold_shell_mask_relations": dict(sorted(cold_relations.items())),
        "cold_recovered_function_character_count": sum(int(row["recovered_function_character_count"]) for row in cold_rows),
        "cold_missing_function_character_count": sum(int(row["missing_function_character_count"]) for row in cold_rows),
        "cold_extra_function_character_count": sum(int(row["extra_function_character_count"]) for row in cold_rows),
        "revised_known_function_character_count": sum(int(row["known_function_character_count"]) for row in labels),
        "surface_character_count": sum(int(row["surface_character_count"]) for row in labels),
        "unseen_core_insertion_probe_count": len(core_probe_rows),
        "unseen_core_insertion_pass_count": sum(row["probe_pass"] == "YES" for row in core_probe_rows),
        "channel_and_fallback_probe_count": len(probe_rows),
        "channel_and_fallback_pass_count": sum(row["probe_pass"] == "YES" for row in probe_rows),
        "new_pages": 0, "new_component_meanings": 0, "surface_predictions": 0, "confirmed_lexemes": 0,
    }
    (OUT / "gdt466_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
