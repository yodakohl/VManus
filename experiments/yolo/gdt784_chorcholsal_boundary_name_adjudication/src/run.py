#!/usr/bin/env python3
"""Build GDT784's boundary-aware chorcholsal whole/name adjudication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
TARGET_SPEC = SRC / "TARGET_BOUNDARY_SPEC.tsv"
DOT_SPECS = SRC / "STOLFI_COMPARATOR_LOCUS_SPECS.tsv"
VISUAL_SPEC = SRC / "VISUAL_AUDIT_SPEC.tsv"
SEGMENT_SPECS = SRC / "SEGMENTATION_MODEL_SPECS.tsv"
CANDIDATE_SPECS = SRC / "CANDIDATE_4_SPECS.tsv"
FINAL_SPEC = SRC / "FINAL_SELECTION_SPEC.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_COMPARATOR_SPECS.tsv"

ALLOWLIST = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv"
G782_RUN = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
STOLFI = Path("transcription/voynich_stolfi25e1_lines.tsv")
G759_PAIRS = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/PART_STATE_23_EXACT_PAIR_ATLAS.tsv"
G768_WORKING = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G762_REPAIR = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv"
G777_SAL = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer/artifacts/SAL_SPLIT_NEGATIVE_CONTROL.tsv"
G779_DICTIONARY = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_WORKING_DICTIONARY.tsv"
G775_FRAMES = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/EXACT_FRAME_REPETITION.tsv"
G781_SELECTED = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv"
G783_RENDERER = ROOT / "experiments/yolo/gdt783_chsky_majority_variant_external_field/artifacts/GDT783_376_RENDERER.tsv"

TARGET = "chorcholsal"
STATUS = (
    "PASS__1_TARGET_WHOLE__3_CURRENT_READERS_FUSED__STOLFI_SPLIT__"
    "13_STOLFI_DOT_COMPARATOR_LOCI__VISUAL_EXTERNAL_GAP_INTERNAL_NO_EQUAL_GAP__"
    "190_176_CHOR__343_303_CHOL__37_33_SAL__8_7_PART_STATE_PAIRS__"
    "SLOT_TWIN_F100V20__PRACTICAL_TROCKENE_BLUETENDROGE__"
    "270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__ZERO_COMPONENT_EXPORT"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output: {path.name}")
    fields = list(rows[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: int(value) if isinstance(value := row.get(field, ""), bool) else value for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def one_by(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        if row[key] in output:
            raise AssertionError(f"duplicate {key}: {row[key]}")
        output[row[key]] = dict(row)
    return output


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if len(rows) != 15:
        raise AssertionError(f"expected 15 locks, got {len(rows)}")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source path: {relative}")
        if sha256(ROOT / relative) != row["expected_sha256"]:
            raise AssertionError(f"source changed: {relative}")
    return len(rows), sha256(SOURCE_LOCK)


def load_base():
    spec = importlib.util.spec_from_file_location("gdt782_locked", G782_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT782 guarded context helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_surface_census(by_line, exact) -> list[dict[str, object]]:
    expected = {TARGET: (1, 1, 1), "chor": (190, 176, 97), "chol": (343, 303, 125), "sal": (37, 33, 28)}
    all_tokens = [row for rows in by_line.values() for row in rows]
    output = []
    for surface in (TARGET, "chor", "chol", "sal"):
        rows = [row for row in all_tokens if row["eva"] == surface]
        values = (len(rows), sum(exact[row["locus"], int(row["token_index"])] for row in rows), len({row["page"] for row in rows}))
        if values != expected[surface]:
            raise AssertionError(f"surface census changed for {surface}: {values}")
        output.append({"surface": surface, "cache_occurrences": values[0], "reader_exact_occurrences": values[1], "page_labels": values[2], "allowed_page_count": 179, "target_surface": int(surface == TARGET), "substring_counts_used_as_target_identity": 0, "confirmed_lexeme": 0, "component_export_credit": 0})
    return output


def build_reader_boundaries(cross, stolfi_by_locus, target) -> list[dict[str, object]]:
    locus, expected = target["locus"], target["current_line_eva"]
    current = cross[locus]
    if any(current[field] != expected for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")):
        raise AssertionError("current three-reader target boundary changed")
    output = []
    for edition, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")):
        output.append({"reader_id": edition, "reader_class": "CURRENT_READER", "page": target["page"], "locus": locus, "clean_line_eva": current[field], "target_written_group": TARGET, "target_group_count": 1, "external_boundary_after_ol": "DEFINITE_SPACE", "internal_chor_chol_boundary": "NONE", "internal_chol_sal_boundary": "NONE", "surface_whole_preserved": 1, "supports_surface_whole": 1, "supports_internal_segmentation": 0, "reader_vote_weight": 1, "meaning_credit": 0, "component_export_credit": 0})
    stolfi = stolfi_by_locus[locus]
    if target["stolfi_target_fragment"] not in stolfi["raw_text"] or stolfi["clean_text"].split()[-3:] != ["chor", "chol", "sal"]:
        raise AssertionError("Stolfi target boundary changed")
    output.append({"reader_id": "Stolfi25e1", "reader_class": "LEGACY_BOUNDARY_READER", "page": target["page"], "locus": locus, "clean_line_eva": stolfi["clean_text"], "target_written_group": target["stolfi_target_fragment"], "target_group_count": 3, "external_boundary_after_ol": "DOT", "internal_chor_chol_boundary": "COMMA", "internal_chol_sal_boundary": "DOT", "surface_whole_preserved": 0, "supports_surface_whole": 0, "supports_internal_segmentation": 1, "reader_vote_weight": 1, "meaning_credit": 0, "component_export_credit": 0})
    return output


def build_dot_atlas(stolfi_by_locus, pair_rows, target, specs) -> list[dict[str, object]]:
    pairs_by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in pair_rows:
        if row["rule_id"] in {"P01", "P02"}:
            pairs_by_locus[row["locus"]].append(row)
    output: list[dict[str, object]] = [{"audit_id": "G784-D000", "audit_role": "TARGET_LEGACY_SPLIT", "page": target["page"], "physical_folio": target["physical_folio"], "locus": target["locus"], "modern_exact_pair_directions": "TARGET_LONG_WHOLE", "relevant_stolfi_fragment": target["stolfi_target_fragment"], "stolfi_boundary_class": "COMMA_THEN_DOT", "representative_definite_dot": 0, "available_stolfi_line": 1, "target_excluded_from_comparator_count": 0, "supports_general_stolfi_dot_as_physical_gap": 0, "semantic_credit": 0}]
    for source_spec in specs:
        locus, expected_direction = source_spec["locus"], source_spec["expected_direction"]
        source = stolfi_by_locus[locus]
        directions = {"CHOR_CHOL" if row["left_surface"] == "chor" else "CHOL_CHOR" for row in pairs_by_locus[locus]}
        actual = "BOTH" if len(directions) == 2 else next(iter(directions))
        if actual != expected_direction:
            raise AssertionError(f"dot direction changed: {locus}")
        fragment = "chol.chor.chol" if actual == "BOTH" else "chor.chol" if actual == "CHOR_CHOL" else "chol.chor"
        if fragment not in source["raw_text"]:
            raise AssertionError(f"Stolfi dot fragment missing: {locus} {fragment}")
        folio_match = re.match(r"^(f\d+)", source["page"])
        if folio_match is None:
            raise AssertionError(source["page"])
        output.append({"audit_id": source_spec["comparator_id"], "audit_role": "GDT759_PAIR_DOT_COMPARATOR", "page": source["page"], "physical_folio": folio_match.group(1), "locus": locus, "modern_exact_pair_directions": actual, "relevant_stolfi_fragment": fragment, "stolfi_boundary_class": "DOT", "representative_definite_dot": 1, "available_stolfi_line": 1, "target_excluded_from_comparator_count": 1, "supports_general_stolfi_dot_as_physical_gap": 0, "semantic_credit": 0})
    if len(output) != 14 or sum(int(row["representative_definite_dot"]) for row in output) != 13:
        raise AssertionError("expected target plus thirteen dot comparators")
    return output


def build_pair_evidence(pair_rows) -> list[dict[str, object]]:
    chosen = [row for row in pair_rows if row["rule_id"] in {"P01", "P02"}]
    if len(chosen) != 15 or len({row["locus"] for row in chosen}) != 14:
        raise AssertionError("GDT759 part-state cohort changed")
    output = []
    for left, right, expected in (("chor", "chol", 8), ("chol", "chor", 7)):
        rows = [row for row in chosen if row["left_surface"] == left and row["right_surface"] == right]
        if len(rows) != expected or any(row["fused_counterpart_reader_exact_occurrences"] != "0" for row in rows):
            raise AssertionError("pair direction or fused-null changed")
        output.append({"direction": f"{left}_TO_{right}", "exact_pair_occurrences": len(rows), "physical_loci": len({row["locus"] for row in rows}), "page_labels": len({row["page"] for row in rows}), "working_pair_role": "PART_PLUS_DRY", "working_render_de": rows[0]["primary_render_de"], "fused_counterpart_surface": rows[0]["fused_counterpart_surface"], "fused_counterpart_reader_exact_occurrences": 0, "internal_echo_credit": 1, "free_component_export": 0, "confirmed_plaintext": 0})
    return output


def build_current_provenance() -> list[dict[str, object]]:
    chor = next(row for row in read_tsv(G768_WORKING) if row["surface"] == "chor")
    sal_repair = next(row for row in read_tsv(G762_REPAIR) if row["surface"] == "sal")
    sal_split = read_tsv(G777_SAL)
    if len(sal_split) != 1 or (sal_split[0]["guarded_fused_exact_occurrences"], sal_split[0]["guarded_raw_split_occurrences"], sal_split[0]["guarded_reader_exact_split_occurrences"]) != ("33", "5", "0"):
        raise AssertionError("sal split control changed")
    cheor = next(row for row in read_tsv(G779_DICTIONARY) if row["entry"] == "cheor")
    parent = next(row for row in read_tsv(G781_SELECTED) if row["right_surface"] == TARGET)
    return [
        {"surface": "chor", "current_role_or_default_de": chor["portable_default_de"], "concrete_display_de": chor["concrete_default_de"], "working_confidence": chor["working_confidence"], "usable_credit": "PART_ROLE_C2__FLOWER_DIRECTION_C0", "counterevidence_de": chor["counterevidence_de"], "component_export_credit": 0},
        {"surface": "chol", "current_role_or_default_de": "trocken/getrocknet", "concrete_display_de": "trocken", "working_confidence": "C2_RECURRENT_PART_STATE", "usable_credit": "DRY_WHOLE_ROLE", "counterevidence_de": "Qualität, Zustand und Trocknungsprozess sind nicht abschließend getrennt.", "component_export_credit": 0},
        {"surface": "sal", "current_role_or_default_de": "semantisch offen", "concrete_display_de": "offene Ganzform", "working_confidence": "C0_OPEN", "usable_credit": "33_READER_EXACT_FUSED__0_OF_5_READER_EXACT_S_PLUS_AL", "counterevidence_de": f"GDT762 entfernt den alten Saatpatienten ({sal_repair['decision']}); GDT777 lizenziert weder s+al noch Salz, Form oder Materialstufe.", "component_export_credit": 0},
        {"surface": "cheor", "current_role_or_default_de": cheor["preferred_gdt779_default_de"], "concrete_display_de": cheor["rendered_displays_de"], "working_confidence": cheor["confidence"], "usable_credit": "DRY_PART_SLOT_CONTEXT", "counterevidence_de": cheor["counterevidence"], "component_export_credit": 0},
        {"surface": TARGET, "current_role_or_default_de": "MASKED", "concrete_display_de": "MASKED", "working_confidence": parent["confidence"], "usable_credit": "SURFACE_SINGLETON_AND_PARENT_SCOPE_ONLY", "counterevidence_de": parent["counterevidence"], "component_export_credit": 0},
    ]


def build_slot_twin(renderer, target) -> list[dict[str, object]]:
    by_locus = {row["locus"]: row for row in renderer if row["locus"] in {target["locus"], "f100v.20"}}
    frames = {row["frame"]: row for row in read_tsv(G775_FRAMES)}
    if set(by_locus) != {target["locus"], "f100v.20"} or frames["cheor|ol|chockhar"]["occurrences"] != "1" or frames["cheor|ol|chorcholsal"]["occurrences"] != "1":
        raise AssertionError("slot twin changed")
    output = []
    for role, locus, ordinals in (("TARGET_MASKED", target["locus"], (4, 5, 6)), ("EXACT_SLOT_TWIN", "f100v.20", (6, 7, 8))):
        row = by_locus[locus]
        output.append({"slot_role": role, "page": row["page"], "physical_folio": row["physical_folio"], "locus": locus, "register": f"{row['section']}|{row['language']}|{row['hand']}", "frame": f"cheor|ol|{row['right_surface']}", "cheor_ordinal": ordinals[0], "ol_ordinal": ordinals[1], "x_ordinal": ordinals[2], "x_surface": row["right_surface"], "x_line_final": 1, "reader_exact": row["right_reader_exact"], "current_x_or_span_default_de": "MASKED" if role == "TARGET_MASKED" else row["gdt783_default_de"], "current_axes": "MASKED" if role == "TARGET_MASKED" else row["gdt783_functional_axes"], "supports_preparation_value_slot": int(role == "EXACT_SLOT_TWIN"), "target_meaning_used": 0, "component_export_credit": 0})
    if output[0]["register"] != "P|A|1" or output[1]["register"] != "P|A|1" or output[1]["current_x_or_span_default_de"] != "erhitzter Ansatz":
        raise AssertionError("same-register preparation twin changed")
    return output


def build_segmentation(boundaries, visual, pairs) -> list[dict[str, object]]:
    current_fused = sum(row["reader_class"] == "CURRENT_READER" and int(row["surface_whole_preserved"]) for row in boundaries)
    legacy_split = sum(row["reader_class"] == "LEGACY_BOUNDARY_READER" and not int(row["surface_whole_preserved"]) for row in boundaries)
    output = []
    for source in read_tsv(SEGMENT_SPECS):
        output.append({**source, "current_reader_fused_support": current_fused, "legacy_stolfi_split_support": legacy_split, "visual_external_gap_support": visual["supports_external_ol_target_boundary"], "visual_equal_internal_gap_support": visual["supports_internal_equal_gap"], "chor_chol_exact_forward": pairs[0]["exact_pair_occurrences"], "chol_chor_exact_reverse": pairs[1]["exact_pair_occurrences"], "standalone_chorchol_exact": 0, "adjudication": "SELECT" if source["model_id"] == "M02" else "RETAIN_RIVAL", "default_is_translation": 0, "confirmed_lexeme": 0})
    if (current_fused, legacy_split, len(output)) != (3, 1, 4):
        raise AssertionError("segmentation atlas changed")
    return output


def build_candidates(final) -> list[dict[str, object]]:
    output = []
    for source in read_tsv(CANDIDATE_SPECS):
        score = sum(int(source[field]) for field in ("surface_whole_fit_points", "slot_twin_fit_points", "part_dry_echo_points", "historical_architecture_points")) - int(source["semantic_overreach_penalty"])
        output.append({**source, "diagnostic_score": score, "score_is_probability": 0, "practical_selection": int(source["candidate_id"] == final["selected_candidate_id"]), "selection_scope": "ONE_EXACT_WHOLE_PLUS_EXISTING_OL_SPAN"})
    output.sort(key=lambda row: (-int(row["diagnostic_score"]), row["candidate_id"]))
    for rank, row in enumerate(output, 1):
        row["score_rank"] = rank
    if [row["candidate_id"] for row in output] != ["C01_DRY_FLOWER_DRUG", "C02_NAMED_DRY_COMPOUND", "C04_NAMED_DRUG_POWDER", "C03_DRY_FLOWER_HEAD"] or [int(row["diagnostic_score"]) for row in output] != [10, 9, 5, 4]:
        raise AssertionError("candidate ranking changed")
    return output


def build_revision(final, boundaries, visual, dots, slots) -> dict[str, object]:
    parent = next(row for row in read_tsv(G781_SELECTED) if row["right_surface"] == TARGET)
    return {"surface": TARGET, "target_occurrence_id": parent["target_occurrence_id"], "locus": parent["locus"], "parent_default_de": parent["new_gdt781_default_de"], "selected_candidate_id": final["selected_candidate_id"], "practical_whole_default_de": final["practical_whole_default_de"], "target_span_default_de": final["target_span_default_de"], "portable_role_de": final["portable_role_de"], "decision": final["decision"], "confidence": final["confidence"], "whole_boundary_confidence": final["whole_boundary_confidence"], "part_dry_echo_confidence": final["part_dry_echo_confidence"], "sal_semantic_confidence": final["sal_semantic_confidence"], "current_readers_fused": sum(row["reader_class"] == "CURRENT_READER" and int(row["surface_whole_preserved"]) for row in boundaries), "legacy_stolfi_split": sum(row["reader_class"] == "LEGACY_BOUNDARY_READER" and not int(row["surface_whole_preserved"]) for row in boundaries), "stolfi_dot_comparator_loci": sum(int(row["representative_definite_dot"]) for row in dots), "visual_external_gap": visual["observed_external_boundary"], "visual_internal_gap": visual["observed_internal_boundary"], "exact_preparation_slot_twin": slots[1]["locus"], "selection_rule": final["selection_rule"], "positive_evidence_de": final["positive_evidence_de"], "counterevidence_de": final["counterevidence_de"], "target_meaning_masked_during_adjudication": 1, "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0, "specific_substance_confirmed": 0}


def build_renderer(parent, revision) -> tuple[list[dict[str, object]], set[str]]:
    output, owners, target_hits = [], set(), 0
    for row in parent:
        target = row["locus"] == "f88r.22" and row["right_surface"] == TARGET
        target_hits += int(target)
        default = revision["target_span_default_de"] if target else row["gdt783_default_de"]
        new = dict(row)
        new.update({"gdt784_branch": "GDT784_BOUNDARY_NAME_ADJUDICATION" if target else "INHERITED_GDT783", "gdt784_default_de": default, "gdt784_practical_whole_default_de": revision["practical_whole_default_de"] if target else "INHERITED_GDT783", "gdt784_target_span_default_de": revision["target_span_default_de"] if target else "INHERITED_GDT783", "gdt784_portable_role_de": revision["portable_role_de"] if target else "INHERITED_GDT783", "gdt784_confidence": revision["confidence"] if target else "INHERITED_GDT783", "gdt784_decision": revision["decision"] if target else "INHERITED_GDT783", "gdt784_surface_whole_preserved": int(target), "gdt784_part_dry_echo": int(target), "gdt784_sal_semantic_open": int(target), "gdt784_renderer_contextual": row["gdt783_renderer_contextual"], "gdt784_consumed_token_count": row["gdt783_consumed_token_count"], "gdt784_consumed_token_ids": row["gdt783_consumed_token_ids"], "gdt784_display_changed": int(target and default != row["gdt783_default_de"]), "gdt784_default_is_translation": 0, "gdt784_confirmed_lexeme": 0, "gdt784_confirmed_plaintext": 0, "gdt784_component_export_credit": 0})
        output.append(new)
        ids = row["gdt783_consumed_token_ids"]
        if ids not in {"", "NONE"}:
            for token_id in ids.split("|"):
                if token_id in owners:
                    raise AssertionError(f"consumption collision: {token_id}")
                owners.add(token_id)
    if (len(output), target_hits, sum(int(row["gdt784_renderer_contextual"]) for row in output), len(owners), sum(int(row["gdt784_display_changed"]) for row in output)) != (376, 1, 270, 230, 1):
        raise AssertionError("renderer totals changed")
    return output, owners


def build_patch(revision) -> dict[str, object]:
    return {"patch_id": "G784-P001", "target_occurrence_id": revision["target_occurrence_id"], "page": "f88r", "physical_folio": "f88", "locus": "f88r.22", "target_ordinal": 6, "target_surface": TARGET, "written_line_eva": "ychey okaiin chol cheor ol chorcholsal", "parent_working_display_de": "Trocknung bis zur Mittelstufe, dann Abschluss | Heißansatz, Grad III | trocken | trockener Teil | getrocknete Stoffzubereitung", "gdt784_field_display_de": "Trocknung bis zur Mittelstufe, dann Abschluss | Heißansatz, Grad III | trocken | trockener Teil | Ansatz: trockene Blütendroge", "gdt784_bracketed_line_de": "ychey okaiin chol cheor ⟦Ansatz: trockene Blütendroge⟧", "readable_compact_de": "Trocknung bis Mittelstufe abschließen | Heißansatz III | trockenes Teilgut | Ansatz: trockene Blütendroge", "display_status": "WORKING_DISPLAY_NOT_PLAINTEXT", "target_meaning_masked_during_adjudication": 1, "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0}


def build_historical() -> list[dict[str, object]]:
    rows = read_tsv(HISTORICAL_SPECS)
    if len(rows) != 5 or any(row["selects_voynich_identity"] != "0" or row["spelling_credit"] != "0" for row in rows):
        raise AssertionError("historical comparator specs changed")
    return [{**row, "allowed_use_in_gdt784": "ARCHITECTURE_AND_CANDIDATE_CLASS_ONLY", "voynich_identity_credit": 0, "component_export_credit": 0} for row in rows]


def make_packet(visual) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    def edge(edge_id: str, pivot_visual_id: str, pivot_locus: str, target_visual_id: str, target_locus: str, relation_type: str, ambiguity_state: str) -> dict[str, object]:
        # Field order is the executable GDT388 intake contract.
        return {
            "edge_id": edge_id, "batch_id": "GDT784_CHORCHOLSAL_BOUNDARY_AUDIT", "page": "f88r", "physical_folio": "f88",
            "diagram_unit_id": "LINE:f88r.22", "pivot_visual_id": pivot_visual_id, "pivot_locus": pivot_locus,
            "target_visual_id": target_visual_id, "target_locus": target_locus, "relation_type": relation_type,
            "direction_basis": "MANUAL_VISUAL_GAP_COMPARISON", "ownership_basis": "VISIBLE_INK_AND_INTERWORD_GAP",
            "geometry_only_selection": "TRUE", "source_manifest_id": "GDT784", "page_crop_sha256": visual["crop_sha256"],
            "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE", "source_aware_localizer": "GDT784_VISUAL_AUDIT_SPEC",
            "relation_reviewer": "GDT784_VALIDATOR", "relation_confidence": "EXPLORATORY", "ambiguity_state": ambiguity_state,
            "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_BOUNDARY_RELATION",
        }
    packet = [
        edge("G784-E001", "TOKEN:f88r.22:5", "f88r.22@5", "TOKEN:f88r.22:6", "f88r.22@6", "CLEAR_EXTERNAL_WORD_GAP", "CLEAR_GAP_AFTER_OL"),
        edge("G784-E002", "SUBSPAN:f88r.22:6:CHOR", "f88r.22@6chor", "SUBSPAN:f88r.22:6:CHOL", "f88r.22@6chol", "NO_EQUAL_INTERNAL_GAP", "INTERNAL_ECHO_NOT_VISUAL_WORD_SPLIT"),
    ]
    crosswalk = [{"edge_id": row["edge_id"], "batch_id": row["batch_id"], "page": row["page"], "physical_folio": row["physical_folio"], "locus": "f88r.22", "relation_type": row["relation_type"], "crop_sha256": visual["crop_sha256"], "surface_whole_preserved": 1, "semantic_score_eligible": 0, "component_export_credit": 0} for row in packet]
    return packet, crosswalk


def artifact_readme() -> str:
    return """# GDT784 artifacts

- `GDT784_4_SURFACE_CENSUS.tsv`: guarded 179-page target/constituent counts.
- `GDT784_4_READER_BOUNDARY_ATLAS.tsv`: three current fused readings plus Stolfi's legacy split.
- `GDT784_14_STOLFI_BOUNDARY_CONTROL_ATLAS.tsv`: target plus thirteen target-free GDT759 contact loci with representative Stolfi dots.
- `GDT784_VISUAL_BOUNDARY_AUDIT.tsv`: bound Yale crop observation; no new image access.
- `GDT784_2_GDT759_PAIR_EVIDENCE.tsv`: independent `chor chol` / `chol chor` counts.
- `GDT784_5_CURRENT_WHOLE_PROVENANCE.tsv`: current whole roles; `sal` is semantically open.
- `GDT784_2_SLOT_TWIN_ATLAS.tsv`: same-register line-final `cheor ol X` target/twin.
- `GDT784_4_SEGMENTATION_ATLAS.tsv`: whole, lexicalized-echo and legacy split models.
- `GDT784_5_HISTORICAL_COMPARATOR_AUDIT.tsv`: architecture-only witnesses.
- `GDT784_4_CANDIDATE_SCORECARDS.tsv`: transparent non-probabilistic ranking.
- `GDT784_1_WORKING_REVISION.tsv`: selected whole and span defaults.
- `GDT784_1_TARGET_PASSAGE_PATCH.tsv`: readable target line.
- `GDT784_376_RENDERER.tsv`: all GDT783 columns inherited; one display revised.
- relation packet, crosswalk, intake and `RESULT.json`: acquisition and replay metadata.

No artifact licenses a substring, lexeme, plaintext clause or specific plant identity.
"""


def build_report(result, boundaries, pairs, candidates, patch, historical) -> str:
    boundary_table = "\n".join(f"| {row['reader_id']} | `{row['target_written_group']}` | {row['external_boundary_after_ol']} | {row['internal_chor_chol_boundary']} / {row['internal_chol_sal_boundary']} | {row['surface_whole_preserved']} |" for row in boundaries)
    candidate_table = "\n".join(f"| {row['score_rank']} | {row['candidate_id']} | {row['whole_default_de']} | {row['span_default_de']} | {row['diagnostic_score']} |" for row in candidates)
    historical_lines = "\n".join(f"- {row['shelfmark']} ({row['date_band']}): {row['architecture_relevant_to_gdt784']}" for row in historical)
    return f"""# GDT784 — `chorcholsal`: boundary, learned name and part-state echo

Status: `{result['status']}`

## Working result

The written surface is preserved as one complete whole at **C2**. ZL3b, IT2a
and RF1b all have `chorcholsal`; the bound visual audit finds a clear gap after
`ol` and no equal internal gap. Stolfi's older `chor,chol.sal` remains real
counterevidence, not a licence to turn three EVA substrings into lexemes.

The practical C0 card is **`chorcholsal=trockene Blütendroge`**. At the already
existing target span, **`ol chorcholsal=Ansatz: trockene Blütendroge`**. The
portable role is only a learned or lexicalized plant-drug whole with a C1
PART+DRY echo. `sal` stays C0/open. Flower versus fruit or seed, the exact drug,
language and plaintext all remain unresolved.

## Four boundary readings

| reader | target group | external boundary | internal boundaries | whole |
|---|---|---|---|---:|
{boundary_table}

Thirteen target-free Stolfi lines among the fourteen modern GDT759 contact
loci have a representative definite dot between `chor` and `chol` or the
reverse. This shows Stolfi's dot convention, but the target comma-plus-dot is
not by itself physical-gap proof. The visual crop decides only the written
whole boundary, never a meaning.

## Independent constituent-order evidence

GDT759 supplies {pairs[0]['exact_pair_occurrences']} exact `chor chol` and
{pairs[1]['exact_pair_occurrences']} exact `chol chor` occurrences over fourteen
loci, with zero standalone exact `chorchol`. Current provenance gives `chor`
a non-leaf plant-part role (concrete flower display still C0), `chol` a strong
DRY role and `cheor` a sanitized dry-part role. `sal` has 33 reader-exact fused
occurrences but zero exact `s al` among five raw split candidates; its semantics
stay fully open. PART+DRY can inform the complete whole at C1, but no substring
is exported.

## Exact slot twin

`f88r.22` and `f100v.20` are both P|A|1 and end `cheor ol X`. In the latter,
X is the current complete whole `chockhar`, rendered **erhitzter Ansatz** with
HOT|PREPARATION. That exact same-register geometry supports a preparation-bearing
value after `ol`; it does not prove that `ol` means “aus”.

## Four concrete candidates

| rank | id | whole | exact `ol` span | diagnostic score |
|---:|---|---|---|---:|
{candidate_table}

The scores are throughput weights, not lexical probabilities. `benanntes
Trockenkompositum` is the strongest dissent. Powder is period-appropriate but
has no Voynich-internal identity, while `trockener Blütenstand` overstates the
still-open botanical direction.

## Readable target

> `{patch['written_line_eva']}`

> **{patch['readable_compact_de']}**

This is `WORKING_DISPLAY_NOT_PLAINTEXT`.

## Historical architecture controls

{historical_lines}

They license learned-name, drug-form and powder candidates as period-appropriate
classes only. They select no Voynich spelling or identity.

## Renderer and claim ceiling

All {result['renderer']['inherited_parent_columns']} GDT783 columns are inherited
for all 376 rows. Contextual/fallback/consumption totals stay 270/106/230; one
target display changes and no new token is consumed. Confirmed lexemes,
plaintext clauses, component values and specific substances remain zero.
No new page, image, OCR or transcription was opened; f84/f84r remained sealed.

## Reproduction

```bash
python3 -B experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/src/run.py
python3 -B experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/artifacts/GDT784_GDT388_BOUNDARY_PACKET.tsv
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()
    lock_count, lock_hash = verify_locks()
    base = load_base()
    by_line, exact, cross, _, _, guard = base.load_context()
    pages = {row["page"] for row in read_tsv(ALLOWLIST)}
    stolfi_rows, stolfi_guard = base.guarded_query(STOLFI, pages, "page,locus,clean_text,raw_text")
    stolfi_by_locus = one_by(stolfi_rows, "locus")
    target_rows, final_rows = read_tsv(TARGET_SPEC), read_tsv(FINAL_SPEC)
    if len(target_rows) != 1 or len(final_rows) != 1:
        raise AssertionError("single target/final specs required")
    target, final = target_rows[0], final_rows[0]
    if any(final[field] != "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit", "specific_substance_confirmed")):
        raise AssertionError("final claim ceiling changed")
    pair_rows, renderer_parent = read_tsv(G759_PAIRS), read_tsv(G783_RENDERER)
    census = build_surface_census(by_line, exact)
    boundaries = build_reader_boundaries(cross, stolfi_by_locus, target)
    dots = build_dot_atlas(stolfi_by_locus, pair_rows, target, read_tsv(DOT_SPECS))
    visual_specs = read_tsv(VISUAL_SPEC)
    if len(visual_specs) != 1:
        raise AssertionError("one visual spec required")
    visual = {**visual_specs[0], "supports_external_ol_target_boundary": 1, "supports_internal_equal_gap": 0, "supports_surface_whole": 1, "observation_scope": "BOUNDARY_ONLY", "meaning_credit": 0, "component_export_credit": 0}
    if (visual["canvas_id"], visual["crop_sha256"], visual["full_image_sha256"], visual["full_width"], visual["full_height"]) != ("1037112", "18064888e8af233e35b90b318c2773d4c4639fd759512dff452262f04f5ff55a", "a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013", "2714", "3735"):
        raise AssertionError("bound visual audit changed")
    pairs = build_pair_evidence(pair_rows)
    provenance = build_current_provenance()
    slots = build_slot_twin(renderer_parent, target)
    segmentation = build_segmentation(boundaries, visual, pairs)
    historical = build_historical()
    candidates = build_candidates(final)
    revision = build_revision(final, boundaries, visual, dots, slots)
    renderer, owners = build_renderer(renderer_parent, revision)
    patch = build_patch(revision)
    packet, crosswalk = make_packet(visual)
    outputs = {
        "GDT784_4_SURFACE_CENSUS.tsv": census, "GDT784_4_READER_BOUNDARY_ATLAS.tsv": boundaries,
        "GDT784_14_STOLFI_BOUNDARY_CONTROL_ATLAS.tsv": dots, "GDT784_VISUAL_BOUNDARY_AUDIT.tsv": [visual],
        "GDT784_2_GDT759_PAIR_EVIDENCE.tsv": pairs, "GDT784_5_CURRENT_WHOLE_PROVENANCE.tsv": provenance,
        "GDT784_2_SLOT_TWIN_ATLAS.tsv": slots, "GDT784_4_SEGMENTATION_ATLAS.tsv": segmentation,
        "GDT784_5_HISTORICAL_COMPARATOR_AUDIT.tsv": historical, "GDT784_4_CANDIDATE_SCORECARDS.tsv": candidates,
        "GDT784_1_WORKING_REVISION.tsv": [revision], "GDT784_1_TARGET_PASSAGE_PATCH.tsv": [patch],
        "GDT784_376_RENDERER.tsv": renderer, "GDT784_GDT388_BOUNDARY_PACKET.tsv": packet,
        "GDT784_RELATION_EDGE_CROSSWALK.tsv": crosswalk,
    }
    for name, rows in outputs.items():
        write_tsv(artifacts / name, rows)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet
    intake = validate_relation_edge_packet(artifacts / "GDT784_GDT388_BOUNDARY_PACKET.tsv")
    expected_intake = {"status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 2, "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False, "holdout_gate": False, "mobile_null_gate": False, "score_ready": False, "errors": []}
    if intake != expected_intake:
        raise AssertionError(f"unexpected intake: {intake}")
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)
    result: dict[str, object] = {
        "experiment_id": "GDT784", "status": STATUS, "source_locks": lock_count, "source_lock_sha256": lock_hash,
        "source_spec_sha256": {"target_boundary": sha256(TARGET_SPEC), "stolfi_comparators": sha256(DOT_SPECS), "visual_audit": sha256(VISUAL_SPEC), "segmentation_models": sha256(SEGMENT_SPECS), "candidates": sha256(CANDIDATE_SPECS), "final_selection": sha256(FINAL_SPEC), "historical_comparators": sha256(HISTORICAL_SPECS)},
        "inherited_guard": guard, "stolfi_guard": stolfi_guard,
        "surface_census": {row["surface"]: {"cache": row["cache_occurrences"], "reader_exact": row["reader_exact_occurrences"], "pages": row["page_labels"]} for row in census},
        "boundary": {"current_fused_readers": 3, "legacy_stolfi_split_readers": 1, "stolfi_dot_comparator_loci": 13, "visual_clear_external_gap": True, "visual_equal_internal_gap": False, "surface_whole_confidence": "C2"},
        "constituent_order": {"chor_chol": 8, "chol_chor": 7, "contact_occurrences": 15, "contact_loci": 14, "standalone_chorchol_exact": 0, "part_dry_echo_confidence": "C1", "sal_semantic_confidence": "C0_OPEN"},
        "adjudication": {"candidate_rows": 4, "score_winner": final["selected_candidate_id"], "practical_whole_default_de": final["practical_whole_default_de"], "target_span_default_de": final["target_span_default_de"], "portable_role_de": final["portable_role_de"], "target_meaning_masked": True, "identity_confidence": "C0"},
        "historical": {"comparators": len(historical), "identity_credit": 0, "spelling_credit": 0},
        "renderer": {"rows": len(renderer), "contextual": sum(int(row["gdt784_renderer_contextual"]) for row in renderer), "fallbacks": sum(1-int(row["gdt784_renderer_contextual"]) for row in renderer), "unique_consumed_tokens": len(owners), "display_changes": sum(int(row["gdt784_display_changed"]) for row in renderer), "unchanged_non_target_rows": 375, "inherited_parent_columns": len(renderer_parent[0])},
        "relation_packet": intake, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "specific_substances": 0, "component_exports": 0, "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "One C0 replaceable complete-whole plant-drug default and existing ol span; C2 surface whole, C1 nonexporting PART+DRY echo, sal and identity open; no lexeme, plaintext or component.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.write_text(build_report(result, boundaries, pairs, candidates, patch, historical), encoding="utf-8")
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
