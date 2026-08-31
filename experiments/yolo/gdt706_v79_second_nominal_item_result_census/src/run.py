#!/usr/bin/env python3
"""Build GDT706's complete delayed universe and bounded V79 result census."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt706_v79_second_nominal_item_result_census"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V79_83_ACTION_DISPOSITIONS__161_DELAYED_PAIRS__28_BOUNDED_CELLS__"
    "1_NEW_C019_BUNDLE_10_HOLDS_17_STOPS__18_EDGES_12_COMPONENTS__ZERO_WORD_DELTA"
)
QUESTION = (
    "After exposing every still-unwritten later nominal item, does the bounded rank-2/rank-3 "
    "window behind GDT705's twenty partial-open sources support a concrete written result bundle?"
)
CLAIM = (
    "V79 maps all 161 semantic delayed action/item pairs from 42 source actions and manually "
    "classifies the bounded 28-cell inner window. One occurrence-bound relation, C019, extends "
    "M007: f86v6.25#5 ykaiin consumes the already measured drug share; #6 or writes the drug "
    "portion inside the rendered bundle; #7 okeeeey writes the completed final-heating state. "
    "The bridge is retained as a hull position, not skipped or counted as an edge endpoint. "
    "This adds no word meaning and is not recovered plaintext or historical decipherment."
)
NEXT_GAP = (
    "Use the published 161-pair outer map to inspect the strongest longer result bundles, beginning "
    "with A083#1→#2-4 and the controls A073/A002/A012, without opening a page or changing a word."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G703 = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census/artifacts"
OLD_ACTIONS = G703 / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv"
G705 = ROOT / "experiments/yolo/gdt705_v78_complete_action_nominal_result_census/artifacts"
OLD_CENSUS = G705 / "V78_60_ACTION_NOMINAL_RESULT_CENSUS.tsv"
OLD_RESULT = G705 / "RESULT.json"
OLD_MEMBERSHIP = G705 / "V78_17_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_COMPONENTS = G705 / "V78_12_CONNECTED_COMPONENTS.tsv"
OLD_POSITIONS = G705 / "V78_34_COMPONENT_POSITION_ROLES.tsv"
OLD_TOKENS = G705 / "V78_479_TOKEN_RELATION_OVERLAY.tsv"
OLD_LINES = G705 / "V78_51_LINE_RELATION_OVERLAY.tsv"
OLD_SPANS = G705 / "V78_3_BOUND_SPAN_FREEZE.tsv"
CELL_SPEC = SRC / "V79_28_DELAYED_RESULT_CELL_SPECS.tsv"

ACTION_GATE_OUT = ART / "V79_83_ACTION_DISPOSITIONS.tsv"
PAIR_OUT = ART / "V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv"
PUNCT_OUT = ART / "V79_2_DELAYED_PUNCTUATION_CONTROLS.tsv"
CELL_OUT = ART / "V79_28_DELAYED_RESULT_CENSUS.tsv"
LIVE_OUT = ART / "V79_11_LIVE_DELAYED_READINGS.tsv"
EDGE_OUT = ART / "V79_1_NEW_DELAYED_RESULT_BUNDLE_EDGE.tsv"
MEMBERSHIP_OUT = ART / "V79_18_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V79_12_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V79_36_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V79_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V79_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V79_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V79_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V79_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V79_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT706_V79_DELAYED_RESULT_READER.md"
RESULT_OUT = ART / "RESULT.json"

SPEC_FIELDS = [
    "delayed_cell_id", "action_case_id", "target_rank", "expected_target_ordinal",
    "expected_target_surface", "expected_bridge_ordinals", "expected_bridge_surfaces",
    "decision", "result_role", "practical_reading_de", "bridge_interpretation_de",
    "decisive_reason_de", "portable_default",
]
ACTION_GATE_FIELDS = [
    "action_case_id", "page", "locus", "action_clause_id", "action_clause_start",
    "action_clause_end", "action_clause_surfaces", "action_ordinal", "action_surface",
    "action_gloss_de", "right_clause_id", "right_clause_type", "right_clause_start",
    "right_clause_end", "right_first_ordinal", "right_first_surface", "right_first_gloss_de",
    "v78_decision", "immediate_result_bound", "nominal_raw_position_count",
    "nominal_semantic_item_count", "later_raw_position_count", "later_semantic_item_count",
    "disposition", "word_delta", "status",
]
PAIR_FIELDS = [
    "delayed_pair_id", "action_case_id", "page", "locus", "action_clause_id",
    "action_clause_start", "action_clause_end", "action_clause_surfaces", "action_ordinal",
    "action_surface", "action_gloss_de", "right_clause_id", "right_clause_start",
    "right_clause_end", "v78_decision", "target_rank", "target_ordinal", "target_surface",
    "target_gloss_de", "intervening_ordinals", "intervening_surfaces",
    "intervening_glosses_de", "inner_v79_window", "semantic_item", "word_delta", "status",
]
PUNCT_FIELDS = [*PAIR_FIELDS[:-4], "punctuation_control", "semantic_item", "word_delta", "status"]
CELL_FIELDS = [
    "delayed_cell_id", "action_case_id", "page", "locus", "action_clause_id",
    "action_clause_start", "action_clause_end", "action_clause_surfaces", "action_ordinal",
    "action_surface", "action_gloss_de", "right_clause_id", "right_clause_start",
    "right_clause_end", "v78_decision", "target_rank", "target_ordinal", "target_surface",
    "target_gloss_de", "bridge_ordinals", "bridge_surfaces", "bridge_glosses_de",
    "decision", "result_role", "practical_reading_de", "bridge_interpretation_de",
    "decisive_reason_de", "admitted_result_bundle_ordinals", "admitted_result_bundle_surfaces",
    "portable_default", "full_window_exact", "word_delta", "status",
]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "source_action_ordinal", "source_action_surface", "source_action_gloss_de",
    "intervening_ordinal", "intervening_surface", "intervening_gloss_de",
    "written_result_ordinal", "written_result_surface", "written_result_gloss_de",
    "edge_node_ordinals", "rendered_result_bundle_ordinals", "rendered_result_bundle_surfaces",
    "operation_agreement", "degree_agreement", "material_agreement", "completion_agreement",
    "patient_basis", "admission_basis", "working_microrecord_de", "strongest_rival_de",
    "boundary_note_de", "portability", "gdt388_score_ready", "forbidden_inference",
    "edge_delta", "word_delta", "status",
]
PACKET_FIELDS = [
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id", "pivot_visual_id",
    "pivot_locus", "target_visual_id", "target_locus", "relation_type", "direction_basis",
    "ownership_basis", "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
    "relation_confidence", "ambiguity_state", "formal_access_state", "fold_assignment",
    "eligibility_status",
]
TOPOLOGY_FIELDS = ["dimension", "value", "count", "component_ids", "note", "status"]
TOKEN_EXTRA = [
    "v79_delayed_cell_ids", "v79_delayed_cell_roles", "v79_delayed_decisions",
    "v79_component_id", "v79_component_position", "v79_component_role",
    "v79_component_edge_ids", "v79_component_membership_class",
    "v79_component_microrecord_de", "v79_new_delayed_result_edge_ids",
    "v79_token_gloss_de", "v79_word_delta", "v79_status",
]
LINE_EXTRA = [
    "v79_delayed_cell_ids", "v79_delayed_decisions", "v79_component_ids",
    "v79_edge_ids", "v79_component_topologies", "v79_component_microrecords_de",
    "v79_new_delayed_result_edge_ids", "v79_working_relation_reading_de",
    "v79_line_translation_de", "v79_word_delta", "v79_status",
]
SPAN_EXTRA = ["v79_selected_gloss_de", "v79_byte_identical", "v79_relation_change", "v79_status"]

C019_READING = (
    "Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. "
    "Den so abgemessenen Drogenanteil I auf Stufe III erhitzen. Ergebnis: Die Drogenportion "
    "ist vollständig bis zur letzten Heizstufe geführt."
)


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    assert fields and len(fields) == len(set(fields)), path
    assert all(None not in row and set(row) == set(fields) for row in rows), path
    return fields, rows


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def pipe(values: Sequence[object]) -> str:
    clean = [str(value) for value in values if value not in (None, "", "NONE")]
    return "|".join(dict.fromkeys(clean)) if clean else "NONE"


def pipe_all(values: Sequence[object]) -> str:
    """Serialize an ordered path without collapsing repeated semantic items."""
    clean = [str(value) for value in values if value not in (None, "", "NONE")]
    return "|".join(clean) if clean else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(CELL_SPEC)
    _, old_actions = read_tsv(OLD_ACTIONS)
    _, old_census = read_tsv(OLD_CENSUS)
    membership_fields, old_memberships = read_tsv(OLD_MEMBERSHIP)
    component_fields, old_components = read_tsv(OLD_COMPONENTS)
    position_fields, old_positions = read_tsv(OLD_POSITIONS)
    token_fields, old_tokens = read_tsv(OLD_TOKENS)
    line_fields, old_lines = read_tsv(OLD_LINES)
    span_fields, old_spans = read_tsv(OLD_SPANS)
    _, clauses = read_tsv(G695)
    old_result = json.loads(OLD_RESULT.read_text(encoding="utf-8"))

    assert spec_fields == SPEC_FIELDS and len(specs) == 28
    assert [row["delayed_cell_id"] for row in specs] == [f"D{i:03d}" for i in range(1, 29)]
    assert len({(row["action_case_id"], row["target_rank"]) for row in specs}) == 28
    assert Counter(row["decision"] for row in specs) == {
        "ADMIT_RESULT_BUNDLE": 1, "HOLD": 10, "STOP": 17,
    }
    assert all(row["portable_default"] == "NO" for row in specs)
    assert len(old_actions) == 83 and len(old_census) == 60 and len(clauses) == 175
    assert len(old_memberships) == 17 and len(old_components) == 12 and len(old_positions) == 34
    assert len(old_tokens) == 479 and len(old_lines) == 51 and len(old_spans) == 3
    assert old_result["basis"]["relation_edges_after"] == 17
    assert all(not row["page"].startswith("f84") for row in old_tokens)

    census_index = {row["action_case_id"]: row for row in old_census}
    token_index = {(row["locus"], int(row["token_ordinal"])): row for row in old_tokens}

    action_gate: list[dict[str, object]] = []
    for old in old_actions:
        right_type = old["right_clause_type"]
        v78 = census_index.get(old["action_case_id"])
        decision = v78["decision"] if v78 else "OUTSIDE_ACTION_TO_NOMINAL_CENSUS"
        bound = bool(v78 and decision in {"ADMIT_NEW", "REPLAY_ADMITTED"})
        if right_type == "NOMINAL_BLOCK":
            start, end = int(old["right_clause_start"]), int(old["right_clause_end"])
            raw_count = end - start + 1
            semantic_count = sum(
                token_index[(old["locus"], ordinal)]["v78_token_gloss_de"] != "."
                for ordinal in range(start, end + 1)
            )
            later_raw, later_semantic = max(0, raw_count - 1), max(0, semantic_count - 1)
            if bound:
                disposition = "IMMEDIATE_RESULT_ALREADY_BOUND"
            elif later_semantic:
                disposition = "DELAYED_NOMINAL_WINDOW"
            else:
                disposition = "SINGLE_NOMINAL_ITEM_NO_DELAY"
        elif right_type == "ACTION_CLAUSE":
            raw_count = semantic_count = later_raw = later_semantic = 0
            disposition = "NEXT_ACTION_BOUNDARY"
        else:
            assert right_type == "END_OF_LINE"
            raw_count = semantic_count = later_raw = later_semantic = 0
            disposition = "END_OF_LINE"
        action_gate.append({
            **{field: old[field] for field in ACTION_GATE_FIELDS[:17]},
            "v78_decision": decision, "immediate_result_bound": int(bound),
            "nominal_raw_position_count": raw_count,
            "nominal_semantic_item_count": semantic_count,
            "later_raw_position_count": later_raw,
            "later_semantic_item_count": later_semantic,
            "disposition": disposition, "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["disposition"] for row in action_gate) == {
        "IMMEDIATE_RESULT_ALREADY_BOUND": 5, "DELAYED_NOMINAL_WINDOW": 42,
        "SINGLE_NOMINAL_ITEM_NO_DELAY": 13, "NEXT_ACTION_BOUNDARY": 15, "END_OF_LINE": 8,
    }
    write_tsv(ACTION_GATE_OUT, action_gate, ACTION_GATE_FIELDS)

    semantic_pairs: list[dict[str, object]] = []
    punctuation_pairs: list[dict[str, object]] = []
    raw_counter = 0
    for gate in action_gate:
        if gate["disposition"] != "DELAYED_NOMINAL_WINDOW":
            continue
        start, end = int(gate["right_clause_start"]), int(gate["right_clause_end"])
        for ordinal in range(start + 1, end + 1):
            raw_counter += 1
            target = token_index[(str(gate["locus"]), ordinal)]
            preceding = [token_index[(str(gate["locus"]), value)] for value in range(start, ordinal)]
            rank = ordinal - start + 1
            row: dict[str, object] = {
                "action_case_id": gate["action_case_id"], "page": gate["page"],
                "locus": gate["locus"], "action_clause_id": gate["action_clause_id"],
                "action_clause_start": gate["action_clause_start"],
                "action_clause_end": gate["action_clause_end"],
                "action_clause_surfaces": gate["action_clause_surfaces"],
                "action_ordinal": gate["action_ordinal"], "action_surface": gate["action_surface"],
                "action_gloss_de": gate["action_gloss_de"], "right_clause_id": gate["right_clause_id"],
                "right_clause_start": start, "right_clause_end": end,
                "v78_decision": gate["v78_decision"], "target_rank": rank,
                "target_ordinal": ordinal, "target_surface": target["surface"],
                "target_gloss_de": target["v78_token_gloss_de"],
                "intervening_ordinals": pipe_all([item["token_ordinal"] for item in preceding]),
                "intervening_surfaces": pipe_all([item["surface"] for item in preceding]),
                "intervening_glosses_de": pipe_all([item["v78_token_gloss_de"] for item in preceding]),
                "semantic_item": int(target["v78_token_gloss_de"] != "."), "word_delta": 0,
                "status": STATUS,
            }
            if target["v78_token_gloss_de"] == ".":
                row["punctuation_control"] = "EXCLUDED_NONSEMANTIC_PERIOD"
                punctuation_pairs.append(row)
            else:
                row["inner_v79_window"] = int(
                    gate["v78_decision"] == "OPEN_PARTIAL" and rank in {2, 3}
                )
                semantic_pairs.append(row)
    assert raw_counter == 163 and len(semantic_pairs) == 161 and len(punctuation_pairs) == 2
    assert {(row["action_case_id"], row["target_ordinal"], row["target_surface"]) for row in punctuation_pairs} == {
        ("A043", 6, "y"), ("A047", 10, "dy"),
    }
    for number, row in enumerate(semantic_pairs, 1):
        row["delayed_pair_id"] = f"P{number:03d}"
    for number, row in enumerate(punctuation_pairs, 1):
        row["delayed_pair_id"] = f"X{number:03d}"
    assert sum(int(row["inner_v79_window"]) for row in semantic_pairs) == 28
    write_tsv(PAIR_OUT, semantic_pairs, PAIR_FIELDS)
    write_tsv(PUNCT_OUT, punctuation_pairs, PUNCT_FIELDS)

    pair_index = {(row["action_case_id"], str(row["target_rank"])): row for row in semantic_pairs}
    cell_rows: list[dict[str, object]] = []
    for spec in specs:
        pair = pair_index[(spec["action_case_id"], spec["target_rank"])]
        assert pair["v78_decision"] == "OPEN_PARTIAL" and pair["inner_v79_window"] == 1
        assert str(pair["target_ordinal"]) == spec["expected_target_ordinal"]
        assert pair["target_surface"] == spec["expected_target_surface"]
        assert pair["intervening_ordinals"] == spec["expected_bridge_ordinals"]
        assert pair["intervening_surfaces"] == spec["expected_bridge_surfaces"]
        bundle_ordinals = "6|7" if spec["delayed_cell_id"] == "D026" else "NONE"
        bundle_surfaces = "or|okeeeey" if spec["delayed_cell_id"] == "D026" else "NONE"
        cell_rows.append({
            "delayed_cell_id": spec["delayed_cell_id"],
            **{field: pair[field] for field in CELL_FIELDS[1:19]},
            "bridge_ordinals": pair["intervening_ordinals"],
            "bridge_surfaces": pair["intervening_surfaces"],
            "bridge_glosses_de": pair["intervening_glosses_de"],
            "decision": spec["decision"], "result_role": spec["result_role"],
            "practical_reading_de": spec["practical_reading_de"],
            "bridge_interpretation_de": spec["bridge_interpretation_de"],
            "decisive_reason_de": spec["decisive_reason_de"],
            "admitted_result_bundle_ordinals": bundle_ordinals,
            "admitted_result_bundle_surfaces": bundle_surfaces,
            "portable_default": spec["portable_default"], "full_window_exact": 1,
            "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["target_rank"] for row in cell_rows) == {2: 16, 3: 12}
    assert Counter(row["decision"] for row in cell_rows) == {
        "ADMIT_RESULT_BUNDLE": 1, "HOLD": 10, "STOP": 17,
    }
    write_tsv(CELL_OUT, cell_rows, CELL_FIELDS)
    live_rows = [row for row in cell_rows if row["decision"] != "STOP"]
    assert len(live_rows) == 11
    write_tsv(LIVE_OUT, live_rows, CELL_FIELDS)

    admitted = next(row for row in cell_rows if row["decision"] == "ADMIT_RESULT_BUNDLE")
    assert (admitted["action_case_id"], admitted["locus"], admitted["action_ordinal"],
            admitted["bridge_ordinals"], admitted["target_ordinal"]) == ("A077", "f86v6.25", "5", "6", 7)
    new_edge = {
        "edge_id": "C019", "component_id": "M007", "locus": "f86v6.25",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_DELAYED_WRITTEN_FINAL_HEAT_RESULT_BUNDLE",
        "source_action_ordinal": 5, "source_action_surface": "ykaiin",
        "source_action_gloss_de": "erhitze hiervon auf Stufe III", "intervening_ordinal": 6,
        "intervening_surface": "or", "intervening_gloss_de": "Drogenportion",
        "written_result_ordinal": 7, "written_result_surface": "okeeeey",
        "written_result_gloss_de": "Zubereitung vollständig bis zur letzten Heizstufe geführt",
        "edge_node_ordinals": "5|7", "rendered_result_bundle_ordinals": "6|7",
        "rendered_result_bundle_surfaces": "or|okeeeey", "operation_agreement": "EXACT_HEAT",
        "degree_agreement": "STAGE_III_TO_LAST_HEAT_STAGE", "material_agreement": "COMPATIBLE_DRUG_PORTION_RESTATEMENT",
        "completion_agreement": "TARGET_WRITES_COMPLETION", "patient_basis": "C006_BINDS_MEASURED_DRUG_SHARE_TO_SOURCE_ACTION_AND_OR_WRITES_DRUG_PORTION",
        "admission_basis": "BOUND_PATIENT_PLUS_RETAINED_MATERIAL_CARRIER_PLUS_OPERATION_AND_STAGE_MIRROR",
        "working_microrecord_de": C019_READING,
        "strongest_rival_de": "Der Nominalblock kann ein Register mehrerer selbständiger Einträge sein; #9 qokaiin ist ein späterer Grad-III-Wert.",
        "boundary_note_de": "#6 bleibt als Materialträger im Renderfenster; #8 Blütenmasse beendet den Ergebniszugriff.",
        "portability": "OCCURRENCE_BOUND_ONLY", "gdt388_score_ready": 0,
        "forbidden_inference": "Kein YKAIIN-Ausgabestandard, kein Überspringen von #6, keine Bindung an #8 oder #9.",
        "edge_delta": 1, "word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [new_edge], EDGE_FIELDS)

    membership_out_fields = [*membership_fields[:-1], "v79_change", "status"]
    memberships: list[dict[str, object]] = []
    for old in old_memberships:
        row = {field: old[field] for field in membership_fields[:-1]}
        if old["component_id"] == "M007":
            row.update({
                "component_edge_count": 3,
                "component_topology": "SERIAL_ACTION_OUTPUT_CHAIN_WITH_DELAYED_RESULT",
                "shared_edge_node_ordinals": "4|5", "v79_change": "COMPONENT_EXTENDED_EDGE_UNCHANGED",
            })
        else:
            row["v79_change"] = "NONE"
        row["status"] = STATUS
        memberships.append(row)
    memberships.append({
        "edge_id": "C019", "component_id": "M007", "locus": "f86v6.25",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_DELAYED_WRITTEN_FINAL_HEAT_RESULT_BUNDLE",
        "edge_node_ordinals": "5|7", "source_ordinals": "5", "target_ordinal": "7",
        "target_role": "WRITTEN_DELAYED_FINAL_HEAT_RESULT", "component_edge_count": 3,
        "component_topology": "SERIAL_ACTION_OUTPUT_CHAIN_WITH_DELAYED_RESULT",
        "shared_edge_node_ordinals": "4|5", "origin": "GDT706_NEW_OCCURRENCE_BOUND",
        "v75_change": "NONE", "v76_change": "NONE", "v77_change": "NONE", "v78_change": "NONE",
        "v79_change": "NEW_EDGE", "status": STATUS,
    })
    memberships.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert [row["edge_id"] for row in memberships] == [f"C{i:03d}" for i in range(1, 20) if i != 16]
    write_tsv(MEMBERSHIP_OUT, memberships, membership_out_fields)

    component_out_fields = [*component_fields[:-1], "v79_edge_delta", "v79_change", "status"]
    components: list[dict[str, object]] = []
    for old in old_components:
        row = {field: old[field] for field in component_fields[:-1]}
        if old["component_id"] == "M007":
            row.update({
                "edge_ids": "C007|C006|C019", "edge_count": 3,
                "edge_node_ordinals": "2|3|4|5|7", "edge_node_count": 5,
                "shared_edge_node_ordinals": "4|5", "edge_hull_start": 2, "edge_hull_end": 7,
                "edge_hull_position_count": 6, "hull_only_ordinals": "6",
                "render_window_start": 2, "render_window_end": 7,
                "render_only_structural_ordinals": "NONE", "render_window_token_count": 6,
                "topology": "SERIAL_ACTION_OUTPUT_CHAIN_WITH_DELAYED_RESULT", "action_ordinals": "4|5",
                "support_profile": "A_MINUS_PLUS_B_PLUS_B", "expected_surfaces": "qokar|olkar|qodar|ykaiin|or|okeeeey",
                "observed_surfaces": "qokar|olkar|qodar|ykaiin|or|okeeeey", "microrecord_de": C019_READING,
                "component_basis": "C007 misst den heißen Drogenanteil aus dem Holzansatz; C006 trägt ihn in YKAIIN; C019 verbindet diese Handlung mit dem geschriebenen Heizabschluss.",
                "boundary_note_de": "#6 or bleibt als sichtbarer Materialträger hull-only; #8 ofchedy ist der Stoff- und Operationsbruch.",
                "forbidden_inference": "Kein allgemeines YKAIIN-Ergebnis, kein nacktes #5→#7 ohne #6 im Renderbündel und keine Erweiterung bis #9.",
                "final_result_status": "WRITTEN_DELAYED_FINAL_HEAT_RESULT:C019",
                "origin": "GDT701_INHERITED_GDT706_EXTENDED", "v79_edge_delta": 1,
                "v79_change": "COMPONENT_EXTENDED",
            })
        else:
            row.update({"v79_edge_delta": 0, "v79_change": "NONE"})
        row["status"] = STATUS
        components.append(row)
    components.sort(key=lambda row: int(str(row["component_id"])[1:]))
    assert len(components) == 12
    write_tsv(COMPONENTS_OUT, components, component_out_fields)

    position_out_fields = [*position_fields[:-1], "v79_change", "status"]
    positions: list[dict[str, object]] = []
    old_position_index = {(row["locus"], int(row["token_ordinal"])): row for row in old_positions}
    for old in old_positions:
        if old["component_id"] != "M007":
            positions.append({
                **{field: old[field] for field in position_fields[:-1]},
                "v79_change": "NONE", "status": STATUS,
            })
    m007_specs = {
        2: ("OUTPUT_LABEL:C007", "C007", "C007", "NONE", "NONE", "EDGE_NODE", 1, 0, 0, 0, 0, "NONE"),
        3: ("DONOR_SOURCE_SHARE:C007", "C007", "C007", "NONE", "NONE", "EDGE_NODE", 1, 0, 0, 0, 0, "NONE"),
        4: ("DONOR_ACTION_OUTPUT:C006|TARGET_ACTION:C007", "C006|C007", "C006", "NONE", "C007", "EDGE_NODE", 1, 0, 0, 1, 1, "WRITTEN_SERIAL_ACTION_OUTPUT_BRIDGE"),
        5: ("REFERENCE:C006|TARGET_ACTION:C006|RESULT_SOURCE:C019", "C006|C019", "C019", "C006", "C006", "EDGE_NODE", 1, 0, 0, 1, 1, "WRITTEN_SERIAL_ACTION_RESULT_SOURCE"),
        6: ("RESULT_BUNDLE_MATERIAL_CARRIER:C019", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", 0, 1, 0, 0, 0, "WRITTEN_C019_RESULT_MATERIAL_CARRIER_NOT_EDGE_NODE"),
        7: ("WRITTEN_DELAYED_FINAL_HEAT_RESULT:C019", "C019", "NONE", "NONE", "C019", "EDGE_NODE", 1, 0, 0, 0, 0, "WRITTEN_C019_FINAL_HEAT_RESULT"),
    }
    for render_position, ordinal in enumerate(range(2, 8), 1):
        token = token_index[("f86v6.25", ordinal)]
        role, edges, source_ids, reference_ids, target_ids, member, edge_node, hull_only, structural, action_target, shared, output_role = m007_specs[ordinal]
        historical = old_position_index.get(("f86v6.25", ordinal), {})
        positions.append({
            "page": token["page"], "locus": "f86v6.25", "token_ordinal": ordinal,
            "surface": token["surface"], "token_gloss_de": token["v78_token_gloss_de"],
            "component_id": "M007", "render_position": render_position, "render_size": 6,
            "component_role": role, "edge_ids": edges, "source_edge_ids": source_ids,
            "reference_edge_ids": reference_ids, "target_edge_ids": target_ids,
            "membership_class": member, "is_edge_node": edge_node, "is_hull_only": hull_only,
            "is_render_only_structural": structural, "is_action_target": action_target,
            "is_shared_edge_node": shared, "action_output_role": output_role,
            "component_microrecord_de": C019_READING, "word_delta": 0,
            "v76_change": historical.get("v76_change", "NONE"),
            "v77_change": historical.get("v77_change", "NONE"),
            "v78_change": historical.get("v78_change", "NONE"),
            "v79_change": "COMPONENT_EXTENDED" if ordinal <= 5 else "NEW_RENDER_POSITION",
            "status": STATUS,
        })
    positions.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(positions) == 36 and Counter(row["membership_class"] for row in positions) == {
        "EDGE_NODE": 33, "HULL_ONLY": 3,
    }
    assert sum(int(row["is_shared_edge_node"]) for row in positions) == 6
    write_tsv(POSITIONS_OUT, positions, position_out_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_rows: list[dict[str, object]] = []
    for dimension, groups, note in (
        ("TOPOLOGY", topology_groups, "current exact component topology"),
        ("SUPPORT_PROFILE", support_groups, "local working tiers are not portable defaults"),
    ):
        for value in sorted(groups):
            topology_rows.append({
                "dimension": dimension, "value": value, "count": len(groups[value]),
                "component_ids": pipe(groups[value]), "note": note, "status": STATUS,
            })
    all_components = pipe([row["component_id"] for row in components])
    topology_rows.extend([
        {"dimension": "ACTION_DISPOSITION", "value": value, "count": count, "component_ids": "NONE", "note": "complete 83-action accounting", "status": STATUS}
        for value, count in sorted(Counter(row["disposition"] for row in action_gate).items())
    ])
    topology_rows.extend([
        {"dimension": "DELAYED_UNIVERSE", "value": "SEMANTIC_PAIR", "count": 161, "component_ids": "NONE", "note": "all semantic later items from 42 result-unwritten nominal windows", "status": STATUS},
        {"dimension": "DELAYED_UNIVERSE", "value": "PUNCTUATION_CONTROL", "count": 2, "component_ids": "NONE", "note": "A043#6 and A047#10 excluded as periods", "status": STATUS},
        {"dimension": "BOUNDED_DECISION", "value": "ADMIT_RESULT_BUNDLE", "count": 1, "component_ids": "M007", "note": "D026/A077 only", "status": STATUS},
        {"dimension": "BOUNDED_DECISION", "value": "HOLD", "count": 10, "component_ids": "NONE", "note": "concrete but incomplete delayed readings", "status": STATUS},
        {"dimension": "BOUNDED_DECISION", "value": "STOP", "count": 17, "component_ids": "NONE", "note": "visible material operation state or earlier-result blocker", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 33, "component_ids": all_components, "note": "unique occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 3, "component_ids": "M007|M008|M009", "note": "f86v6.25#6, f86v5.24#2 and f26r.2#7", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 0, "component_ids": "NONE", "note": "none", "status": STATUS},
        {"dimension": "STRUCTURAL_ROLE", "value": "CLAUSE_CLOSURE_NONNODE", "count": 1, "component_ids": "M009", "note": "f26r.2#7 remains the only structural closure", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "EDGE_INCIDENCE", "count": 39, "component_ids": all_components, "note": "sum of edge-node incidences", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "MINIMAL_HULL_POSITION", "count": 36, "component_ids": all_components, "note": "sum of component hull sizes", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "RENDER_POSITION", "count": 36, "component_ids": all_components, "note": "sum of render-window sizes", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packet = {
        "edge_id": "C019", "batch_id": "GDT706_V79", "page": "f86v6", "physical_folio": "f86",
        "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_5_YKAIIN_ACTION",
        "pivot_locus": "f86v6.25@5", "target_visual_id": "TOKEN_6_7_MATERIAL_HEAT_RESULT_BUNDLE",
        "target_locus": "f86v6.25@6-7", "relation_type": "WORKSHOP_ACTION_TO_DELAYED_WRITTEN_FINAL_HEAT_RESULT",
        "direction_basis": "ACTION_THEN_MATERIAL_CARRIER_THEN_FINAL_HEAT_STATE",
        "ownership_basis": "BOUND_PATIENT_PLUS_HEAT_AND_STAGE_MIRROR", "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT706", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE", "source_aware_localizer": "GDT706_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "B_WORKING_LOCAL",
        "ambiguity_state": "WORKSHOP_ONLY", "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
    }
    write_tsv(PACKET_OUT, [packet], PACKET_FIELDS)
    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", rel(PACKET_OUT)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    assert intake_run.returncode == 1 and not intake_run.stderr
    assert json.loads(intake_run.stdout) == expected_intake
    INTAKE_OUT.write_text(json.dumps(expected_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cells_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    roles_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    decisions_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in cell_rows:
        locus, cell_id, decision = str(row["locus"]), str(row["delayed_cell_id"]), str(row["decision"])
        for ordinal in range(int(row["action_clause_start"]), int(row["action_clause_end"]) + 1):
            cells_by_pos[(locus, ordinal)].add(cell_id); roles_by_pos[(locus, ordinal)].add("SOURCE_ACTION")
            decisions_by_pos[(locus, ordinal)].add(decision)
        for ordinal in str(row["bridge_ordinals"]).split("|"):
            key = (locus, int(ordinal)); cells_by_pos[key].add(cell_id); roles_by_pos[key].add("RETAINED_BRIDGE")
            decisions_by_pos[key].add(decision)
        key = (locus, int(row["target_ordinal"])); cells_by_pos[key].add(cell_id)
        roles_by_pos[key].add(f"CANDIDATE_TARGET_RANK_{row['target_rank']}"); decisions_by_pos[key].add(decision)
    roles_by_pos[("f86v6.25", 6)].add("ADMITTED_RESULT_MATERIAL_CARRIER")
    roles_by_pos[("f86v6.25", 7)].add("ADMITTED_RESULT_STATE")

    position_index = {(str(row["locus"]), int(row["token_ordinal"])): row for row in positions}
    token_overlay: list[dict[str, object]] = []
    for old in old_tokens:
        key = (old["locus"], int(old["token_ordinal"]))
        position = position_index.get(key)
        edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **old, "v79_delayed_cell_ids": pipe(sorted(cells_by_pos.get(key, set()))),
            "v79_delayed_cell_roles": pipe(sorted(roles_by_pos.get(key, set()))),
            "v79_delayed_decisions": pipe(sorted(decisions_by_pos.get(key, set()))),
            "v79_component_id": position["component_id"] if position else "NONE",
            "v79_component_position": position["render_position"] if position else "NONE",
            "v79_component_role": position["component_role"] if position else "NONE",
            "v79_component_edge_ids": edges,
            "v79_component_membership_class": position["membership_class"] if position else "NONE",
            "v79_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v79_new_delayed_result_edge_ids": "C019" if "C019" in edges.split("|") else "NONE",
            "v79_token_gloss_de": old["v78_token_gloss_de"], "v79_word_delta": 0,
            "v79_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v79_token_gloss_de"] == old["v78_token_gloss_de"] for new, old in zip(token_overlay, old_tokens))
    assert sum(row["v79_new_delayed_result_edge_ids"] == "C019" for row in token_overlay) == 2
    assert next(row for row in token_overlay if row["locus"] == "f86v6.25" and row["token_ordinal"] == "6")["v79_new_delayed_result_edge_ids"] == "NONE"
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    cells_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in cell_rows:
        cells_by_locus[str(row["locus"])].append(row)
    component_by_locus = {str(row["locus"]): row for row in components}
    line_overlay: list[dict[str, object]] = []
    for old in old_lines:
        local = cells_by_locus.get(old["locus"], [])
        component = component_by_locus.get(old["locus"])
        edges = str(component["edge_ids"]) if component else "NONE"
        line_overlay.append({
            **old, "v79_delayed_cell_ids": pipe([row["delayed_cell_id"] for row in local]),
            "v79_delayed_decisions": pipe([row["decision"] for row in local]),
            "v79_component_ids": component["component_id"] if component else "NONE",
            "v79_edge_ids": edges, "v79_component_topologies": component["topology"] if component else "NONE",
            "v79_component_microrecords_de": component["microrecord_de"] if component else "NONE",
            "v79_new_delayed_result_edge_ids": "C019" if "C019" in edges.split("|") else "NONE",
            "v79_working_relation_reading_de": C019_READING if old["locus"] == "f86v6.25" else "NONE",
            "v79_line_translation_de": old["v78_line_translation_de"], "v79_word_delta": 0,
            "v79_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v79_line_translation_de"] == old["v78_line_translation_de"] for new, old in zip(line_overlay, old_lines))
    assert sum(row["v79_new_delayed_result_edge_ids"] == "C019" for row in line_overlay) == 1
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{
        **old, "v79_selected_gloss_de": old["v78_selected_gloss_de"],
        "v79_byte_identical": 1, "v79_relation_change": "NONE", "v79_status": STATUS,
    } for old in old_spans]
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT706 — V79 delayed-result reader", "", f"Status: `{STATUS}`", "",
        "## Neue konkrete Lesung", "", f"> **C019 / f86v6.25#2-7:** {C019_READING}", "",
        "Die eigentliche neue Beziehung ist `#5 ykaiin → #7 okeeeey`. `#6 or` wird dabei nicht "
        "übersprungen: Es bleibt als sichtbarer Materialträger **Drogenportion** im Ergebnisbündel "
        "`#6-7`, ist aber kein eigener Graph-Endpunkt.", "", "## Vollständige Reichweite", "",
        "- 83 Aktionen sind in fünf Dispositionen vollständig verbucht.",
        "- 42 zu Beginn ergebnisoffene Nominalfenster enthalten 163 spätere Positionen; nach C019 bleiben 41 davon ohne spätes Ergebnis.",
        "- Zwei davon sind Punktzeichen; 161 semantische Aktions-/Item-Paare bleiben sichtbar.",
        "- Der enge, praktisch lesbare Rang-2/Rang-3-Bestand umfasst 28 Zellen: 1 Aufnahme, 10 offene Lesarten, 17 Stopps.",
        "", "## Stärkste offene Lesarten", "",
        "| Fall | Arbeitslesung | offener Punkt |", "|---|---|---|",
        "| A029 | leicht erhitzter Ansatzstoff | Abmessen ist nicht lizenziert; leicht fehlt rechts |",
        "| A070 | trockenes Maß bis zum heiß-trockenen Anfang erhitzen | Maß und genauer Zielgrad bleiben ungeschrieben |",
        "| A017 | getrockneter Krautanteil I | Mittelstufe fehlt; Materialidentität nur kompatibel |",
        "| A063 | Drogenstoff in heißen Empfänger geben | konkrete Argumentkette, aber kein geschriebenes Transformationsprodukt |",
        "", "## Graph", "",
        "C019 erweitert M007, erzeugt also keine dreizehnte Komponente. Der kumulative Bestand hat "
        "18 Kanten, 12 Komponenten, 33 eindeutige Knoten und 36 Renderpositionen. Wörter, Seiten und "
        "alte Zeilenübersetzungen bleiben unverändert.", "",
    ]
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")
    (ART / "README.md").write_text(
        "# GDT706 artifacts\n\n"
        "- `V79_83_ACTION_DISPOSITIONS.tsv`: complete action/source accounting.\n"
        "- `V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv`: exhaustive outer delayed-item map.\n"
        "- `V79_2_DELAYED_PUNCTUATION_CONTROLS.tsv`: excluded period controls.\n"
        "- `V79_28_DELAYED_RESULT_CENSUS.tsv`: bounded rank-2/rank-3 manual census.\n"
        "- `V79_11_LIVE_DELAYED_READINGS.tsv`: one admitted and ten held practical readings.\n"
        "- `V79_1_NEW_DELAYED_RESULT_BUNDLE_EDGE.tsv`: occurrence-bound C019.\n"
        "- `V79_18_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V79_12_CONNECTED_COMPONENTS.tsv`, and "
        "`V79_36_COMPONENT_POSITION_ROLES.tsv`: cumulative relation graph.\n"
        "- `V79_COMPONENT_TOPOLOGY_CENSUS.tsv`: graph and decision accounting.\n"
        "- `V79_GDT388_EDGE_PACKET.tsv` and `V79_GDT388_EDGE_INTAKE.json`: explicit invalid/not-score-ready intake.\n"
        "- `V79_479_TOKEN_RELATION_OVERLAY.tsv`, `V79_51_LINE_RELATION_OVERLAY.tsv`, and "
        "`V79_3_BOUND_SPAN_FREEZE.tsv`: unchanged words with V79 relation metadata.\n"
        "- `GDT706_V79_DELAYED_RESULT_READER.md`: concise practical German reader.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    node_keys = {
        (str(row["locus"]), ordinal)
        for row in memberships for ordinal in str(row["edge_node_ordinals"]).split("|")
    }
    assert len(node_keys) == 33
    assert sum(len(str(row["edge_node_ordinals"]).split("|")) for row in memberships) == 39
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 36
    assert sum(int(row["render_window_token_count"]) for row in components) == 36
    assert json.loads(G388.read_text(encoding="utf-8"))["acquisition"]["scoring_authorized"] is False

    generated = [
        ACTION_GATE_OUT, PAIR_OUT, PUNCT_OUT, CELL_OUT, LIVE_OUT, EDGE_OUT, MEMBERSHIP_OUT,
        COMPONENTS_OUT, POSITIONS_OUT, TOPOLOGY_OUT, PACKET_OUT, INTAKE_OUT, TOKENS_OUT,
        LINES_OUT, SPANS_OUT, READER_OUT, ART / "README.md",
    ]
    inputs = [
        G388, G695, OLD_ACTIONS, OLD_CENSUS, OLD_RESULT, OLD_MEMBERSHIP, OLD_COMPONENTS,
        OLD_POSITIONS, OLD_TOKENS, OLD_LINES, OLD_SPANS, CELL_SPEC, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "source_clauses": 175, "action_clauses": 83, "bound_spans": 3,
            "immediate_result_bound_actions_before": 5,
            "result_unwritten_actions_before": 78, "result_unwritten_actions_after": 77,
            "censused_delayed_nominal_windows": 42,
            "delayed_nominal_windows_unresolved_after": 41, "single_nominal_no_delay": 13,
            "next_action_boundaries": 15, "end_of_line": 8,
            "raw_delayed_positions": 163, "punctuation_controls": 2,
            "semantic_delayed_pairs": 161, "bounded_delayed_cells": 28,
            "rank2_cells": 16, "rank3_cells": 12, "new_admits": 1, "holds": 10, "stops": 17,
            "relation_edges_before": 17, "relation_edges_after": 18, "new_edges": 1,
            "connected_components": 12, "edge_nodes": 33, "edge_node_incidences": 39,
            "minimal_hull_positions": 36, "render_positions": 36, "shared_edge_nodes": 6,
            "hull_only_positions": 3, "render_only_structural_positions": 0,
            "structural_closure_positions": 1, "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "new_edge_ids": ["C019"], "c019": "f86v6.25#5→f86v6.25#7",
            "rendered_result_bundle": "f86v6.25#6-7", "component": "M007",
            "intervening_material_carrier_is_edge_node": False,
            "held_cells": [row["delayed_cell_id"] for row in cell_rows if row["decision"] == "HOLD"],
            "portable_default": False, "new_word_meanings": 0,
        },
        "graph": {
            "component_partition": [
                ["C009"], ["C001", "C012"], ["C002"], ["C003"], ["C004", "C008"],
                ["C005"], ["C006", "C007", "C019"], ["C010"], ["C011", "C013", "C015"],
                ["C014"], ["C017"], ["C018"],
            ],
            "shared_nodes": ["f105v.1#4", "f26r.2#4", "f26r.2#6", "f80v.35#3", "f86v6.25#4", "f86v6.25#5"],
            "hull_only_positions": ["f26r.2#7", "f86v5.24#2", "f86v6.25#6"],
            "render_only_structural_positions": [], "structural_closure": "f26r.2#7",
        },
        "gdt388": expected_intake,
        "word_preservation": {
            "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0,
            "changed_word_meanings": 0, "content_word_additions": 0,
            "content_word_deletions": 0, "content_word_reorders": 0,
        },
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated}, "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": STATUS, "semantic_delayed_pairs": 161, "bounded_cells": 28,
        "new_edge": "C019", "edges": 18, "components": 12, "edge_nodes": 33,
        "render_positions": 36, "new_word_meanings": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
