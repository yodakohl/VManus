#!/usr/bin/env python3
"""Build GDT708's variable-length batch-card audit and local C021 edge."""

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
EXP = ROOT / "experiments/yolo/gdt708_v81_variable_batch_terminal_product"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V81_9_VARIABLE_BUNDLES__1_NEW_C021_8_LIVE_HOLDS__"
    "20_EDGES_14_COMPONENTS__ZERO_WORD_DELTA"
)
QUESTION = (
    "Do the four retained three-item bundles and five shorter live prefixes support a variable "
    "attribute-stack-to-terminal-product architecture, and does the A012 endpoint #6 selected in "
    "that exact comparison "
    "license one concrete occurrence-bound result reading?"
)
C021_READING = (
    "Das Arzneikompositum bis zur Mittelstufe aufbereiten. Danach stehen: abgemessener Anteil II; "
    "Rohstoff I; heiße Mittelstufe. Mögliches terminales Produkt: bis zur Mittelstufe "
    "eingeweichtes und abgeschlossenes Arzneikompositum."
)
CLAIM = (
    "V81 compares the exact nine still-live variable-length bundle candidates. A012 alone adds a "
    "terminal field that restores both the written material head Arzneikompositum and the middle "
    "degree while adding completion; C021 links f106r.23#2 to #6 across three visible hull-only "
    "attribute carriers. The other eight readings remain live holds. No surface default, patient "
    "identity, word meaning, recovered plaintext, or historical decipherment is asserted."
)
NEXT_GAP = (
    "Apply the first-terminal-material-product rule without skipping to all 42 delayed nominal "
    "windows, recording each earliest endpoint and first blocker; open no page or word value."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G707 = ROOT / "experiments/yolo/gdt707_v80_three_item_material_state_result_bundle/artifacts"
OLD_BUNDLES = G707 / "V80_32_ACTION_ADJACENT_BUNDLE_CENSUS.tsv"
OLD_RESULT = G707 / "RESULT.json"
OLD_MEMBERSHIP = G707 / "V80_19_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_COMPONENTS = G707 / "V80_13_CONNECTED_COMPONENTS.tsv"
OLD_POSITIONS = G707 / "V80_40_COMPONENT_POSITION_ROLES.tsv"
OLD_TOKENS = G707 / "V80_479_TOKEN_RELATION_OVERLAY.tsv"
OLD_LINES = G707 / "V80_51_LINE_RELATION_OVERLAY.tsv"
OLD_SPANS = G707 / "V80_3_BOUND_SPAN_FREEZE.tsv"
SPEC = SRC / "V81_9_VARIABLE_BUNDLE_SPECS.tsv"

CENSUS_OUT = ART / "V81_9_VARIABLE_BUNDLE_CENSUS.tsv"
TERMINAL_OUT = ART / "V81_4_TERMINAL_PRODUCT_ORDER_TEST.tsv"
PREFIX_OUT = ART / "V81_5_RANK2_PREFIX_BOUNDARY_TEST.tsv"
EDGE_OUT = ART / "V81_1_NEW_VARIABLE_RESULT_EDGE.tsv"
MEMBERSHIP_OUT = ART / "V81_20_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V81_14_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V81_45_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V81_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V81_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V81_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V81_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V81_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V81_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT708_V81_VARIABLE_BATCH_READER.md"
RESULT_OUT = ART / "RESULT.json"

SPEC_FIELDS = [
    "candidate_id", "action_case_id", "candidate_family", "selected_item_ordinals",
    "expected_item_surfaces", "role_trace", "selected_length", "decision", "live_hold",
    "first_boundary_ordinals", "first_boundary_surfaces", "practical_reading_de",
    "decisive_reason_de", "portable_default",
]
CENSUS_FIELDS = [
    "candidate_id", "action_case_id", "page", "locus", "action_ordinal", "action_surface",
    "action_gloss_de", "candidate_family", "selected_item_ordinals", "selected_item_surfaces",
    "selected_item_glosses_de", "role_trace", "selected_length", "hypothetical_edge_node_ordinals",
    "hypothetical_hull_only_ordinals", "gdt707_full_bundle_decision", "v81_decision", "live_hold",
    "first_boundary_ordinals", "first_boundary_surfaces", "first_boundary_glosses_de",
    "boundary_class", "practical_reading_de", "decisive_reason_de", "patient_identity_asserted",
    "portable_default", "word_delta", "status",
]
TERMINAL_FIELDS = [
    "test_id", "action_case_id", "locus", "attribute_ordinals", "terminal_ordinal",
    "terminal_surface", "terminal_gloss_de", "observed_order", "material_recurrence",
    "degree_recurrence", "action_productivity", "order_test", "v81_decision", "status",
]
PREFIX_FIELDS = [
    "test_id", "action_case_id", "locus", "selected_rank", "selected_ordinals",
    "selected_surfaces", "selected_glosses_de", "first_rejected_rank", "first_rejected_ordinal",
    "first_rejected_surface", "first_rejected_gloss_de", "rejection_type", "v81_decision", "status",
]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "source_action_ordinal", "source_action_surface", "source_action_gloss_de",
    "attribute_ordinals", "attribute_surfaces", "attribute_glosses_de", "attribute_roles",
    "written_result_ordinal", "written_result_surface", "written_result_gloss_de",
    "edge_node_ordinals", "render_window_ordinals", "render_window_surfaces",
    "operation_agreement", "degree_agreement", "material_agreement", "quantity_agreement",
    "completion_agreement", "patient_basis", "admission_basis", "working_microrecord_de",
    "strongest_rival_de", "boundary_note_de", "portability", "gdt388_score_ready",
    "forbidden_inference", "edge_delta", "word_delta", "status",
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
    "v81_candidate_ids", "v81_candidate_roles", "v81_candidate_decisions", "v81_component_id",
    "v81_component_position", "v81_component_role", "v81_component_edge_ids",
    "v81_component_membership_class", "v81_component_microrecord_de",
    "v81_new_variable_result_edge_ids", "v81_token_gloss_de", "v81_word_delta", "v81_status",
]
LINE_EXTRA = [
    "v81_candidate_ids", "v81_candidate_decisions", "v81_component_ids", "v81_edge_ids",
    "v81_component_topologies", "v81_component_microrecords_de",
    "v81_new_variable_result_edge_ids", "v81_working_relation_reading_de",
    "v81_line_translation_de", "v81_word_delta", "v81_status",
]
SPAN_EXTRA = ["v81_selected_gloss_de", "v81_byte_identical", "v81_relation_change", "v81_status"]


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
    clean = [str(value) for value in values if value not in (None, "", "NONE")]
    return "|".join(clean) if clean else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(SPEC)
    _, old_bundles = read_tsv(OLD_BUNDLES)
    membership_fields, old_memberships = read_tsv(OLD_MEMBERSHIP)
    component_fields, old_components = read_tsv(OLD_COMPONENTS)
    position_fields, old_positions = read_tsv(OLD_POSITIONS)
    token_fields, old_tokens = read_tsv(OLD_TOKENS)
    line_fields, old_lines = read_tsv(OLD_LINES)
    span_fields, old_spans = read_tsv(OLD_SPANS)
    old_result = json.loads(OLD_RESULT.read_text(encoding="utf-8"))

    assert spec_fields == SPEC_FIELDS and len(specs) == 9
    assert [row["candidate_id"] for row in specs] == [f"V81C{i:03d}" for i in range(1, 10)]
    assert Counter(row["decision"] for row in specs) == {
        "ADMIT_C021": 1, "HOLD_OBJECT_BLOCK": 2,
        "STOP_LONGER_RETAIN_IMMEDIATE_HOLD": 1, "HOLD_TWO_ITEM_PREFIX": 5,
    }
    assert sum(int(row["live_hold"]) for row in specs) == 8
    assert all(row["portable_default"] == "NO" for row in specs)
    assert (len(old_bundles), len(old_memberships), len(old_components), len(old_positions)) == (32, 19, 13, 40)
    assert (len(old_tokens), len(old_lines), len(old_spans)) == (479, 51, 3)
    assert old_result["basis"]["relation_edges_after"] == 19
    assert all(not row["page"].startswith("f84") for row in old_tokens)

    bundle_index = {row["action_case_id"]: row for row in old_bundles}
    token_index = {(row["locus"], int(row["token_ordinal"])): row for row in old_tokens}
    boundary_classes = {
        "A012": "STATE_AND_DEGREE_RESET", "A014": "NEXT_ACTION",
        "A024": "NEW_QUANTITY_MATERIAL_START", "A043": "DEGREE_RESET_AFTER_TERMINAL_PRODUCT",
        "A073": "MATERIAL_CHANGE_AND_DEGREE_RESET", "A070": "STATE_RESTART_THEN_THERMAL_REVERSAL",
        "A029": "NEW_OPERATION_COMPLETION_BLOCK", "A017": "DEGREE_CONTRADICTION",
        "A004": "DEGREE_RESET",
    }
    hypothetical = {
        "A012": ("2|6", "3|4|5"), "A014": ("2|5", "3|4"),
        "A024": ("3|7", "4|5|6"), "A043": ("1|3", "2"),
        "A073": ("3|5", "4"), "A070": ("4|6", "5"),
        "A029": ("5|7", "6"), "A017": ("1|3", "2"), "A004": ("6|8", "7"),
    }
    census_rows: list[dict[str, object]] = []
    for spec in specs:
        action = bundle_index[spec["action_case_id"]]
        ordinals = [int(value) for value in spec["selected_item_ordinals"].split("|")]
        items = [token_index[(action["locus"], ordinal)] for ordinal in ordinals]
        boundaries = [token_index[(action["locus"], int(value))] for value in spec["first_boundary_ordinals"].split("|")]
        assert pipe_all([row["surface"] for row in items]) == spec["expected_item_surfaces"]
        assert len(items) == int(spec["selected_length"])
        nodes, hull = hypothetical[spec["action_case_id"]]
        census_rows.append({
            "candidate_id": spec["candidate_id"], "action_case_id": spec["action_case_id"],
            "page": action["page"], "locus": action["locus"], "action_ordinal": action["action_ordinal"],
            "action_surface": action["action_surface"], "action_gloss_de": action["action_gloss_de"],
            "candidate_family": spec["candidate_family"], "selected_item_ordinals": spec["selected_item_ordinals"],
            "selected_item_surfaces": pipe_all([row["surface"] for row in items]),
            "selected_item_glosses_de": pipe_all([row["v80_token_gloss_de"] for row in items]),
            "role_trace": spec["role_trace"], "selected_length": spec["selected_length"],
            "hypothetical_edge_node_ordinals": nodes, "hypothetical_hull_only_ordinals": hull,
            "gdt707_full_bundle_decision": action["bundle_decision"], "v81_decision": spec["decision"],
            "live_hold": spec["live_hold"], "first_boundary_ordinals": spec["first_boundary_ordinals"],
            "first_boundary_surfaces": pipe_all([row["surface"] for row in boundaries]),
            "first_boundary_glosses_de": pipe_all([row["v80_token_gloss_de"] for row in boundaries]),
            "boundary_class": boundary_classes[spec["action_case_id"]],
            "practical_reading_de": spec["practical_reading_de"],
            "decisive_reason_de": spec["decisive_reason_de"], "patient_identity_asserted": 0,
            "portable_default": spec["portable_default"], "word_delta": 0, "status": STATUS,
        })
    assert Counter(int(row["selected_length"]) for row in census_rows) == {2: 5, 4: 2, 3: 1, 1: 1}
    write_tsv(CENSUS_OUT, census_rows, CENSUS_FIELDS)

    terminal_specs = {
        "A012": ("3|4|5", "6", "AFTER_ATTRIBUTES", "EXACT_COMPOSITE", "EXACT_MIDDLE", "PRODUCTIVE_PREPARE", "SUPPORTS_AND_ADMITS"),
        "A014": ("3|4", "5", "AFTER_ATTRIBUTES", "CHARGE_TO_EXTRACT_OPEN", "RELATED_MIDDLE", "NONPRODUCTIVE_TAKE", "SUPPORTS_DESCRIPTION_ONLY"),
        "A024": ("4|5|6", "7", "AFTER_ATTRIBUTES", "POWDER_TO_PREPARATION_OPEN", "ATTRIBUTE_ONLY_MIDDLE", "NONPRODUCTIVE_MEASURE", "SUPPORTS_ORDER_ONLY"),
        "A043": ("4|5", "3", "BEFORE_LATER_ATTRIBUTES", "RELATED_DRY_PRODUCT", "MIDDLE_THEN_END_RESET", "PRODUCTIVE_PREPARE", "ORDER_COUNTERCASE"),
    }
    terminal_rows: list[dict[str, object]] = []
    for number, action_id in enumerate(("A012", "A014", "A024", "A043"), 1):
        row = next(item for item in census_rows if item["action_case_id"] == action_id)
        attrs, terminal, order, material, degree, productive, order_test = terminal_specs[action_id]
        token = token_index[(str(row["locus"]), int(terminal))]
        terminal_rows.append({
            "test_id": f"TP{number:03d}", "action_case_id": action_id, "locus": row["locus"],
            "attribute_ordinals": attrs, "terminal_ordinal": terminal, "terminal_surface": token["surface"],
            "terminal_gloss_de": token["v80_token_gloss_de"], "observed_order": order,
            "material_recurrence": material, "degree_recurrence": degree,
            "action_productivity": productive, "order_test": order_test,
            "v81_decision": row["v81_decision"], "status": STATUS,
        })
    write_tsv(TERMINAL_OUT, terminal_rows, TERMINAL_FIELDS)

    rejection_types = {
        "A073": "MATERIAL_CHANGE_AND_STAGE_RESET",
        "A070": "NONCONTRIBUTORY_REPEAT_BOUNDARY_CONFIRMED_BY_NEXT_COLD_REVERSAL",
        "A029": "NEW_DRYING_COMPLETION_OPERATION", "A017": "MIDDLE_TO_COLD_START_CONTRADICTION",
        "A004": "MIDDLE_TO_END_RESET",
    }
    prefix_rows: list[dict[str, object]] = []
    for number, action_id in enumerate(("A073", "A070", "A029", "A017", "A004"), 1):
        row = next(item for item in census_rows if item["action_case_id"] == action_id)
        boundary_ordinal = str(row["first_boundary_ordinals"]).split("|")[0]
        boundary = token_index[(str(row["locus"]), int(boundary_ordinal))]
        prefix_rows.append({
            "test_id": f"P{number:03d}", "action_case_id": action_id, "locus": row["locus"],
            "selected_rank": 2, "selected_ordinals": row["selected_item_ordinals"],
            "selected_surfaces": row["selected_item_surfaces"], "selected_glosses_de": row["selected_item_glosses_de"],
            "first_rejected_rank": 3, "first_rejected_ordinal": boundary_ordinal,
            "first_rejected_surface": boundary["surface"], "first_rejected_gloss_de": boundary["v80_token_gloss_de"],
            "rejection_type": rejection_types[action_id], "v81_decision": "HOLD_TWO_ITEM_PREFIX", "status": STATUS,
        })
    write_tsv(PREFIX_OUT, prefix_rows, PREFIX_FIELDS)

    edge = {
        "edge_id": "C021", "component_id": "M014", "locus": "f106r.23",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_TERMINAL_COMPOSITE_PRODUCT_AFTER_ATTRIBUTE_STACK",
        "source_action_ordinal": 2, "source_action_surface": "qckhedy",
        "source_action_gloss_de": "das Arzneikompositum bis zur Mittelstufe aufbereiten",
        "attribute_ordinals": "3|4|5", "attribute_surfaces": "dair|al|qokedy",
        "attribute_glosses_de": "abgemessener Anteil II|Rohstoffklasse I|heiße Mittelstufe erreicht",
        "attribute_roles": "QUANTITY|MATERIAL|STATE_DEGREE", "written_result_ordinal": 6,
        "written_result_surface": "shecphy",
        "written_result_gloss_de": "bis zur Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum",
        "edge_node_ordinals": "2|6", "render_window_ordinals": "2|3|4|5|6",
        "render_window_surfaces": "qckhedy|dair|al|qokedy|shecphy",
        "operation_agreement": "PREPARE_TO_SOAKED_CLOSED_PRODUCT_COMPATIBLE_NOT_IDENTICAL",
        "degree_agreement": "EXACT_MIDDLE_STAGE_RESTORED_AT_TERMINAL_PRODUCT",
        "material_agreement": "EXACT_ARZNEIKOMPOSITUM_RESTORED_AT_TERMINAL_PRODUCT",
        "quantity_agreement": "RIGHT_ATTRIBUTE_ONLY_NOT_BOUND_TO_PATIENT",
        "completion_agreement": "RIGHT_TERMINAL_PRODUCT_ADDS_EXPLICIT_COMPLETION",
        "patient_basis": "LOCAL_BUNDLE_ONLY_NO_ASSERTED_IDENTITY_ACROSS_ATTRIBUTE_FIELDS",
        "admission_basis": "FIRST_TERMINAL_FIELD_RESTORES_ACTION_MATERIAL_AND_DEGREE_AND_ADDS_COMPLETION",
        "working_microrecord_de": C021_READING,
        "strongest_rival_de": "Die drei Attribute und das Endprodukt können selbständige Registereinträge sein; ihre gemeinsame Charge ist nicht ausdrücklich markiert.",
        "boundary_note_de": "Die Arbeitslesung endet vor #7 qokchy, wo Mitte und eingeweicht/abgeschlossen zu heiß-trocken am Gradanfang wechseln. Das ist eine analytische Ausschlussstelle ohne Satzzeichen oder geschriebenen Patientenwechsel; #7 kann eine nächste Phase desselben Materials sein.",
        "portability": "OCCURRENCE_BOUND_ONLY", "gdt388_score_ready": 0,
        "forbidden_inference": "Keine Patientengleichheit, keine Kanten zwischen den Attributfeldern und kein portables Q-M-SG-P-, qckhedy- oder shecphy-Default.",
        "edge_delta": 1, "word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [edge], EDGE_FIELDS)

    membership_out_fields = [*membership_fields[:-1], "v81_change", "status"]
    memberships = [
        {**{field: row[field] for field in membership_fields[:-1]}, "v81_change": "NONE", "status": STATUS}
        for row in old_memberships
    ]
    memberships.append({
        "edge_id": "C021", "component_id": "M014", "locus": "f106r.23",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_TERMINAL_COMPOSITE_PRODUCT_AFTER_ATTRIBUTE_STACK",
        "edge_node_ordinals": "2|6", "source_ordinals": "2", "target_ordinal": "6",
        "target_role": "WRITTEN_MIDDLE_COMPOSITE_PRODUCT_RESULT", "component_edge_count": 1,
        "component_topology": "ACTION_TO_TERMINAL_PRODUCT_AFTER_THREE_ATTRIBUTE_CARRIERS",
        "shared_edge_node_ordinals": "NONE", "origin": "GDT708_NEW_OCCURRENCE_BOUND",
        "v75_change": "NONE", "v76_change": "NONE", "v77_change": "NONE", "v78_change": "NONE",
        "v79_change": "NONE", "v80_change": "NONE", "v81_change": "NEW_EDGE_AND_COMPONENT", "status": STATUS,
    })
    memberships.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert len(memberships) == 20
    write_tsv(MEMBERSHIP_OUT, memberships, membership_out_fields)

    component_out_fields = [*component_fields[:-1], "v81_edge_delta", "v81_change", "status"]
    components = [
        {**{field: row[field] for field in component_fields[:-1]}, "v81_edge_delta": 0,
         "v81_change": "NONE", "status": STATUS} for row in old_components
    ]
    components.append({
        "component_id": "M014", "locus": "f106r.23", "edge_ids": "C021", "edge_count": 1,
        "edge_node_ordinals": "2|6", "edge_node_count": 2, "shared_edge_node_ordinals": "NONE",
        "edge_hull_start": 2, "edge_hull_end": 6, "edge_hull_position_count": 5,
        "hull_only_ordinals": "3|4|5", "render_window_start": 2, "render_window_end": 6,
        "render_only_structural_ordinals": "NONE", "render_window_token_count": 5,
        "topology": "ACTION_TO_TERMINAL_PRODUCT_AFTER_THREE_ATTRIBUTE_CARRIERS", "action_ordinals": "2",
        "support_profile": "B_WORKING_LOCAL", "expected_surfaces": "qckhedy|dair|al|qokedy|shecphy",
        "observed_surfaces": "qckhedy|dair|al|qokedy|shecphy", "microrecord_de": C021_READING,
        "component_basis": "Nur #2 und #6 sind Knoten; #3 Menge, #4 Material und #5 Zustand/Grad bleiben hull-only Attributträger.",
        "boundary_note_de": "Erste analytische Ausschlussstelle vor #7 qokchy wegen des Zustands- und Gradwechsels; kein Satzzeichen und kein geschriebener Patientenwechsel.",
        "forbidden_inference": "Keine Patientengleichheit und keine portable Wort-, Reihenfolge- oder Chargenblockregel.",
        "final_result_status": "WRITTEN_MIDDLE_COMPOSITE_PRODUCT_RESULT:C021",
        "origin": "GDT708_NEW_EXACT", "edge_delta": 1, "word_delta": 0,
        "v76_change": "NONE", "v77_edge_delta": 0, "v77_change": "NONE",
        "v78_edge_delta": 0, "v78_change": "NONE", "v79_edge_delta": 0, "v79_change": "NONE",
        "v80_edge_delta": 0, "v80_change": "NONE", "v81_edge_delta": 1,
        "v81_change": "NEW_COMPONENT", "status": STATUS,
    })
    components.sort(key=lambda row: int(str(row["component_id"])[1:]))
    assert len(components) == 14
    write_tsv(COMPONENTS_OUT, components, component_out_fields)

    position_out_fields = [*position_fields[:-1], "v81_change", "status"]
    positions = [
        {**{field: row[field] for field in position_fields[:-1]}, "v81_change": "NONE", "status": STATUS}
        for row in old_positions
    ]
    local_specs = {
        2: ("SOURCE_ACTION:C021", "C021", "C021", "NONE", "EDGE_NODE", 1, 0, "C021_RESULT_SOURCE_ACTION"),
        3: ("ATTRIBUTE_QUANTITY_CARRIER:C021", "NONE", "NONE", "NONE", "HULL_ONLY", 0, 1, "WRITTEN_C021_QUANTITY_ATTRIBUTE_NOT_EDGE_NODE"),
        4: ("ATTRIBUTE_MATERIAL_CARRIER:C021", "NONE", "NONE", "NONE", "HULL_ONLY", 0, 1, "WRITTEN_C021_MATERIAL_ATTRIBUTE_NOT_EDGE_NODE"),
        5: ("ATTRIBUTE_STATE_DEGREE_CARRIER:C021", "NONE", "NONE", "NONE", "HULL_ONLY", 0, 1, "WRITTEN_C021_STATE_DEGREE_ATTRIBUTE_NOT_EDGE_NODE"),
        6: ("WRITTEN_MIDDLE_COMPOSITE_PRODUCT_RESULT:C021", "C021", "NONE", "C021", "EDGE_NODE", 1, 0, "WRITTEN_C021_TERMINAL_PRODUCT_RESULT"),
    }
    for render_position, ordinal in enumerate(range(2, 7), 1):
        token = token_index[("f106r.23", ordinal)]
        role, edges, sources, targets, member, node, hull, output_role = local_specs[ordinal]
        positions.append({
            "page": token["page"], "locus": "f106r.23", "token_ordinal": ordinal,
            "surface": token["surface"], "token_gloss_de": token["v80_token_gloss_de"],
            "component_id": "M014", "render_position": render_position, "render_size": 5,
            "component_role": role, "edge_ids": edges, "source_edge_ids": sources,
            "reference_edge_ids": "NONE", "target_edge_ids": targets, "membership_class": member,
            "is_edge_node": node, "is_hull_only": hull, "is_render_only_structural": 0,
            "is_action_target": 0, "is_shared_edge_node": 0, "action_output_role": output_role,
            "component_microrecord_de": C021_READING, "word_delta": 0,
            "v76_change": "NONE", "v77_change": "NONE", "v78_change": "NONE",
            "v79_change": "NONE", "v80_change": "NONE", "v81_change": "NEW_COMPONENT_POSITION",
            "status": STATUS,
        })
    positions.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(positions) == 45
    assert Counter(row["membership_class"] for row in positions) == {"EDGE_NODE": 37, "HULL_ONLY": 8}
    assert sum(int(row["is_shared_edge_node"]) for row in positions) == 6
    write_tsv(POSITIONS_OUT, positions, position_out_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
    topology_rows = [{
        "dimension": "TOPOLOGY", "value": value, "count": len(ids), "component_ids": pipe(ids),
        "note": "current exact component topology", "status": STATUS,
    } for value, ids in sorted(topology_groups.items())]
    all_components = pipe([row["component_id"] for row in components])
    topology_rows.extend([
        {"dimension": "VARIABLE_BUNDLE_DECISION", "value": "ADMIT_C021", "count": 1, "component_ids": "M014", "note": "A012 only", "status": STATUS},
        {"dimension": "VARIABLE_BUNDLE_DECISION", "value": "LIVE_HOLD", "count": 8, "component_ids": "NONE", "note": "all other candidates", "status": STATUS},
        {"dimension": "SELECTED_LENGTH", "value": "ONE_ITEM", "count": 1, "component_ids": "NONE", "note": "A043", "status": STATUS},
        {"dimension": "SELECTED_LENGTH", "value": "TWO_ITEMS", "count": 5, "component_ids": "NONE", "note": "all shorter prefixes", "status": STATUS},
        {"dimension": "SELECTED_LENGTH", "value": "THREE_ITEMS", "count": 1, "component_ids": "NONE", "note": "A014", "status": STATUS},
        {"dimension": "SELECTED_LENGTH", "value": "FOUR_ITEMS", "count": 2, "component_ids": "M014", "note": "A012 A024", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 37, "component_ids": all_components, "note": "unique occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 8, "component_ids": "M007|M008|M009|M013|M014", "note": "three new C021 attributes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 0, "component_ids": "NONE", "note": "none", "status": STATUS},
        {"dimension": "STRUCTURAL_ROLE", "value": "CLAUSE_CLOSURE_NONNODE", "count": 1, "component_ids": "M009", "note": "unchanged", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "EDGE_INCIDENCE", "count": 43, "component_ids": all_components, "note": "sum of incidences", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "MINIMAL_HULL_POSITION", "count": 45, "component_ids": all_components, "note": "sum of hull sizes", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "RENDER_POSITION", "count": 45, "component_ids": all_components, "note": "sum of render sizes", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packet = {
        "edge_id": "C021", "batch_id": "GDT708_V81", "page": "f106r", "physical_folio": "f106",
        "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_2_QCKHEDY_ACTION",
        "pivot_locus": "f106r.23@2", "target_visual_id": "TOKEN_6_SHECPHY_TERMINAL_PRODUCT",
        "target_locus": "f106r.23@6", "relation_type": "WORKSHOP_ACTION_TO_TERMINAL_PRODUCT_AFTER_ATTRIBUTE_STACK",
        "direction_basis": "ACTION_THEN_QUANTITY_MATERIAL_STATE_DEGREE_THEN_TERMINAL_PRODUCT",
        "ownership_basis": "LOCAL_COMPLETE_WINDOW_WITHOUT_PATIENT_IDENTITY_CLAIM",
        "geometry_only_selection": "FALSE", "source_manifest_id": "GDT708",
        "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT708_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": "B_WORKING_LOCAL", "ambiguity_state": "WORKSHOP_ONLY",
        "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
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

    ids_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    roles_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    decisions_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in census_rows:
        locus, candidate, decision = str(row["locus"]), str(row["candidate_id"]), str(row["v81_decision"])
        action_key = (locus, int(row["action_ordinal"]))
        ids_by_pos[action_key].add(candidate); roles_by_pos[action_key].add("SOURCE_ACTION"); decisions_by_pos[action_key].add(decision)
        for rank, ordinal in enumerate(str(row["selected_item_ordinals"]).split("|"), 1):
            key = (locus, int(ordinal)); ids_by_pos[key].add(candidate); roles_by_pos[key].add(f"SELECTED_ITEM_{rank}"); decisions_by_pos[key].add(decision)
        for ordinal in str(row["first_boundary_ordinals"]).split("|"):
            key = (locus, int(ordinal)); ids_by_pos[key].add(candidate); roles_by_pos[key].add("FIRST_BOUNDARY"); decisions_by_pos[key].add(decision)

    position_index = {(str(row["locus"]), int(row["token_ordinal"])): row for row in positions}
    token_overlay: list[dict[str, object]] = []
    for old in old_tokens:
        key = (old["locus"], int(old["token_ordinal"])); position = position_index.get(key)
        edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **old, "v81_candidate_ids": pipe(sorted(ids_by_pos.get(key, set()))),
            "v81_candidate_roles": pipe(sorted(roles_by_pos.get(key, set()))),
            "v81_candidate_decisions": pipe(sorted(decisions_by_pos.get(key, set()))),
            "v81_component_id": position["component_id"] if position else "NONE",
            "v81_component_position": position["render_position"] if position else "NONE",
            "v81_component_role": position["component_role"] if position else "NONE",
            "v81_component_edge_ids": edges,
            "v81_component_membership_class": position["membership_class"] if position else "NONE",
            "v81_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v81_new_variable_result_edge_ids": "C021" if "C021" in edges.split("|") else "NONE",
            "v81_token_gloss_de": old["v80_token_gloss_de"], "v81_word_delta": 0, "v81_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v81_token_gloss_de"] == old["v80_token_gloss_de"] for new, old in zip(token_overlay, old_tokens))
    assert sum(row["v81_new_variable_result_edge_ids"] == "C021" for row in token_overlay) == 2
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    candidates_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    components_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in census_rows: candidates_by_locus[str(row["locus"])].append(row)
    for row in components: components_by_locus[str(row["locus"])].append(row)
    line_overlay: list[dict[str, object]] = []
    for old in old_lines:
        local_candidates = candidates_by_locus.get(old["locus"], [])
        local_components = components_by_locus.get(old["locus"], [])
        edge_ids = pipe([row["edge_ids"] for row in local_components])
        line_overlay.append({
            **old, "v81_candidate_ids": pipe([row["candidate_id"] for row in local_candidates]),
            "v81_candidate_decisions": pipe([row["v81_decision"] for row in local_candidates]),
            "v81_component_ids": pipe([row["component_id"] for row in local_components]),
            "v81_edge_ids": edge_ids, "v81_component_topologies": pipe([row["topology"] for row in local_components]),
            "v81_component_microrecords_de": pipe([row["microrecord_de"] for row in local_components]),
            "v81_new_variable_result_edge_ids": "C021" if "C021" in edge_ids.split("|") else "NONE",
            "v81_working_relation_reading_de": C021_READING if old["locus"] == "f106r.23" else "NONE",
            "v81_line_translation_de": old["v80_line_translation_de"], "v81_word_delta": 0, "v81_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v81_line_translation_de"] == old["v80_line_translation_de"] for new, old in zip(line_overlay, old_lines))
    assert sum(row["v81_new_variable_result_edge_ids"] == "C021" for row in line_overlay) == 1
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])
    span_overlay = [{
        **old, "v81_selected_gloss_de": old["v80_selected_gloss_de"], "v81_byte_identical": 1,
        "v81_relation_change": "NONE", "v81_status": STATUS,
    } for old in old_spans]
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT708 — V81 variabler Chargenblock-Reader", "", f"Status: `{STATUS}`", "",
        "## Neue konkrete Lesung", "", f"> **C021 / f106r.23#2-6:** {C021_READING}", "",
        "Erst #6 stellt Arzneikompositum, Mittelstufe und einen abgeschlossenen Produktzustand gemeinsam wieder her. #3 Menge, #4 Material und #5 Zustand/Grad bleiben sichtbare Attribute, aber keine eigenen Kanten.", "",
        "## Arbeitsform", "", "Aktion, danach die kürzeste kohärente Angaben-/Ergebnisfolge bis zum ersten fertigen materialtragenden Produkt oder bis zu einem Material-, Operations- oder Gradreset. Das ist ein Strukturtest und behauptet noch keine gemeinsame Charge.", "",
        "## Alle neun konkreten Lesungen", "",
    ]
    reader.extend(f"- **{row['action_case_id']} ({row['locus']}):** {row['practical_reading_de']}" for row in census_rows)
    reader.extend([
        "", "C021 bleibt an dieses Vorkommen gebunden. Es behauptet weder eine sichere gemeinsame Charge aller Attribute noch eine allgemeine Q–M–S/G–P-Syntax. Der Graph hat nun 20 Kanten, 14 Komponenten, 37 Knoten und 45 Renderpositionen; 479 Wortglossen und 51 Zeilenübersetzungen bleiben unverändert.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")
    (ART / "README.md").write_text(
        "# GDT708 artifacts\n\n"
        "- `V81_9_VARIABLE_BUNDLE_CENSUS.tsv`: all nine live candidates.\n"
        "- `V81_4_TERMINAL_PRODUCT_ORDER_TEST.tsv`: three terminal-after-attribute cases plus A043.\n"
        "- `V81_5_RANK2_PREFIX_BOUNDARY_TEST.tsv`: five exact two-item holds and blockers.\n"
        "- `V81_1_NEW_VARIABLE_RESULT_EDGE.tsv`: occurrence-bound C021.\n"
        "- `V81_20_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V81_14_CONNECTED_COMPONENTS.tsv`, and `V81_45_COMPONENT_POSITION_ROLES.tsv`: cumulative graph.\n"
        "- `V81_GDT388_EDGE_PACKET.tsv` and `V81_GDT388_EDGE_INTAKE.json`: not-score-ready intake.\n"
        "- `V81_479_TOKEN_RELATION_OVERLAY.tsv`, `V81_51_LINE_RELATION_OVERLAY.tsv`, and `V81_3_BOUND_SPAN_FREEZE.tsv`: unchanged text plus relation metadata.\n"
        "- `GDT708_V81_VARIABLE_BATCH_READER.md`, `RESULT.json`, and `VALIDATION.json`: reader and summaries.\n",
        encoding="utf-8",
    )

    node_keys = {(str(row["locus"]), ordinal) for row in memberships for ordinal in str(row["edge_node_ordinals"]).split("|")}
    assert len(node_keys) == 37
    assert sum(len(str(row["edge_node_ordinals"]).split("|")) for row in memberships) == 43
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 45
    assert sum(int(row["render_window_token_count"]) for row in components) == 45
    assert json.loads(G388.read_text(encoding="utf-8"))["acquisition"]["scoring_authorized"] is False

    generated = [CENSUS_OUT, TERMINAL_OUT, PREFIX_OUT, EDGE_OUT, MEMBERSHIP_OUT, COMPONENTS_OUT,
                 POSITIONS_OUT, TOPOLOGY_OUT, PACKET_OUT, INTAKE_OUT, TOKENS_OUT, LINES_OUT,
                 SPANS_OUT, READER_OUT, ART / "README.md"]
    inputs = [G388, OLD_BUNDLES, OLD_RESULT, OLD_MEMBERSHIP, OLD_COMPONENTS, OLD_POSITIONS,
              OLD_TOKENS, OLD_LINES, OLD_SPANS, SPEC, Path(__file__).resolve()]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "variable_bundle_candidates": 9, "terminal_order_tests": 4, "rank2_prefix_tests": 5,
            "new_admits": 1, "live_holds": 8, "selected_lengths": {"1": 1, "2": 5, "3": 1, "4": 2},
            "relation_edges_before": 19, "relation_edges_after": 20, "new_edges": 1,
            "connected_components": 14, "edge_nodes": 37, "edge_node_incidences": 43,
            "minimal_hull_positions": 45, "render_positions": 45, "shared_edge_nodes": 6,
            "hull_only_positions": 8, "render_only_structural_positions": 0,
            "structural_closure_positions": 1, "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "new_edge_ids": ["C021"], "c021": "f106r.23#2→f106r.23#6",
            "render_window": "f106r.23#2-6", "component": "M014",
            "hull_only_attributes": ["f106r.23#3", "f106r.23#4", "f106r.23#5"],
            "held_action_cases": ["A014", "A024", "A043", "A073", "A070", "A029", "A017", "A004"],
            "a043_longer_extension": "STOP_LONGER_RETAIN_IMMEDIATE_HOLD",
            "patient_identity_asserted": False, "portable_default": False, "new_word_meanings": 0,
        },
        "graph": {
            "component_partition": [["C009"], ["C001", "C012"], ["C002"], ["C003"], ["C004", "C008"],
                ["C005"], ["C006", "C007", "C019"], ["C010"], ["C011", "C013", "C015"],
                ["C014"], ["C017"], ["C018"], ["C020"], ["C021"]],
            "shared_nodes": ["f105v.1#4", "f26r.2#4", "f26r.2#6", "f80v.35#3", "f86v6.25#4", "f86v6.25#5"],
            "hull_only_positions": ["f26r.2#7", "f86v5.24#2", "f86v6.25#6", "f8r.15#2", "f8r.15#3",
                "f106r.23#3", "f106r.23#4", "f106r.23#5"],
            "render_only_structural_positions": [], "structural_closure": "f26r.2#7",
        },
        "gdt388": expected_intake,
        "word_preservation": {"token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0, "changed_word_meanings": 0,
            "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0},
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated}, "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "candidates": 9, "new_edge": "C021", "live_holds": 8,
                      "edges": 20, "components": 14, "edge_nodes": 37, "render_positions": 45,
                      "new_word_meanings": 0}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
