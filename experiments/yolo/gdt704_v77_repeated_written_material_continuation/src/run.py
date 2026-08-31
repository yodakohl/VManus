#!/usr/bin/env python3
"""Build GDT704's repeated-written-material continuation census and V77 graph."""

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
EXP = ROOT / "experiments/yolo/gdt704_v77_repeated_written_material_continuation"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V77_15_ACTION_CONTINUATIONS__4_EXACT_HEAD_REPEATS__"
    "1_NEW_C015__C016_HELD__15_EDGES_10_COMPONENTS__ZERO_WORD_DELTA"
)
QUESTION = (
    "Among all fifteen immediate action-to-action transitions already exposed by GDT703, "
    "does an exact repeated written material head distinguish a genuine output continuation, "
    "and does that support one occurrence-bound C015 edge without admitting C016?"
)
CLAIM = (
    "V77 compares all 15 immediate action-to-action transitions. Four repeat an explicit "
    "material head exactly, but three are parallel ingredient additions; only f26r.2 combines "
    "the repeated Krautdroge with the already carried C011 batch. C015 therefore extends M009 "
    "from cooling clause #6-7 to drying action #8. C016 remains an open lower-tier reading "
    "because qokcho is neither deictic nor material-headed and #6 Samenposten competes as its "
    "patient. This is an occurrence-bound practical working relation, not recovered plaintext "
    "or a portable word rule."
)
NEXT_GAP = (
    "Inspect the complete set of actions whose final result is not separately written, beginning "
    "with C015 target #8, for a later explicit state or material reuse inside the same frozen "
    "36-page scope. Preserve C016 as open and add no edge without a written participant anchor."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G703 = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census/artifacts"
OLD_RESULT = G703 / "RESULT.json"
OLD_CENSUS = G703 / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv"
OLD_MEMBERSHIP = G703 / "V76_14_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_COMPONENTS = G703 / "V76_10_CONNECTED_COMPONENTS.tsv"
OLD_POSITIONS = G703 / "V76_29_COMPONENT_POSITION_ROLES.tsv"
OLD_TOKENS = G703 / "V76_479_TOKEN_RELATION_OVERLAY.tsv"
OLD_LINES = G703 / "V76_51_LINE_RELATION_OVERLAY.tsv"
OLD_SPANS = G703 / "V76_3_BOUND_SPAN_FREEZE.tsv"
CONT_SPEC = SRC / "V77_15_ACTION_CONTINUATION_SPECS.tsv"
RESULT_SPEC = SRC / "V77_2_OBJECTLESS_POST_RESULT_SPECS.tsv"

CONT_OUT = ART / "V77_15_ACTION_TO_ACTION_CONTINUATIONS.tsv"
REPEAT_OUT = ART / "V77_4_EXACT_REPEATED_MATERIAL_HEADS.tsv"
RESULT_CONTROL_OUT = ART / "V77_2_OBJECTLESS_POST_RESULT_CONTROLS.tsv"
EDGE_OUT = ART / "V77_1_NEW_REPEATED_MATERIAL_EDGE.tsv"
MEMBERSHIP_OUT = ART / "V77_15_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V77_10_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V77_30_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V77_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V77_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V77_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V77_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V77_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V77_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT704_V77_REPEATED_MATERIAL_READER.md"
RESULT_OUT = ART / "RESULT.json"

CONT_SPEC_FIELDS = [
    "action_case_id", "left_material_head_de", "right_material_head_de",
    "material_head_class", "left_patient_or_output_role", "process_relation_class",
    "decision", "edge_id", "support_tier", "working_reading_de",
    "strongest_rival_de", "portable_default",
]
RESULT_SPEC_FIELDS = [
    "control_id", "locus", "result_ordinal", "result_surface", "result_gloss_de",
    "target_clause_start", "target_clause_end", "target_surfaces",
    "target_action_gloss_de", "deixis", "repeated_material_head",
    "right_patient_candidate", "decision", "edge_id", "support_tier",
    "working_reading_de", "strongest_rival_de",
]
CONT_FIELDS = [
    "action_case_id", "page", "locus", "left_clause_id", "left_clause_start",
    "left_clause_end", "left_clause_surfaces", "left_action_ordinal",
    "left_action_surface", "left_action_gloss_de", "right_clause_id",
    "right_clause_start", "right_clause_end", "right_clause_surfaces",
    "right_action_ordinal", "right_action_surface", "right_action_gloss_de",
    *CONT_SPEC_FIELDS[1:], "full_clause_boundary_preserved", "word_delta", "status",
]
RESULT_CONTROL_FIELDS = [*RESULT_SPEC_FIELDS, "target_clause_id", "verified", "word_delta", "status"]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "source_clause_ordinals", "source_edge_node_ordinal", "source_action_surface",
    "source_action_gloss_de", "structural_closure_ordinal", "structural_closure_surface",
    "target_action_ordinal", "target_action_surface", "target_action_gloss_de",
    "repeated_material_head_de", "continuation_basis", "working_microrecord_de",
    "strongest_rival_de", "right_break_ordinal", "right_break_surface",
    "portability", "gdt388_score_ready", "forbidden_inference", "edge_delta",
    "word_delta", "status",
]
PACKET_FIELDS = [
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
    "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
    "source_aware_localizer", "relation_reviewer", "relation_confidence",
    "ambiguity_state", "formal_access_state", "fold_assignment", "eligibility_status",
]
TOPOLOGY_FIELDS = ["dimension", "value", "count", "component_ids", "note", "status"]
TOKEN_EXTRA = [
    "v77_action_continuation_ids", "v77_action_continuation_roles",
    "v77_material_head_classes", "v77_continuation_decisions",
    "v77_objectless_result_control_ids", "v77_component_id", "v77_component_position",
    "v77_component_role", "v77_component_edge_ids", "v77_component_membership_class",
    "v77_component_microrecord_de", "v77_new_continuation_edge_ids",
    "v77_token_gloss_de", "v77_word_delta", "v77_status",
]
LINE_EXTRA = [
    "v77_action_continuation_ids", "v77_exact_head_repeat_ids",
    "v77_continuation_decisions", "v77_objectless_result_control_ids",
    "v77_component_ids", "v77_edge_ids", "v77_component_topologies",
    "v77_component_microrecords_de", "v77_new_continuation_edge_ids",
    "v77_working_relation_reading_de", "v77_line_translation_de",
    "v77_word_delta", "v77_status",
]
SPAN_EXTRA = ["v77_selected_gloss_de", "v77_byte_identical", "v77_relation_change", "v77_status"]

M009_READING = (
    "Die Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von ‚hiervon‘ offen]. "
    "Zustand: mittlere Trockenstufe erreicht. Dieselbe erhitzte Krautdroge bis zur "
    "Mittelstufe abkühlen und abschließen. Die so abgekühlte Krautdroge mäßig trocknen, "
    "nochmals mäßig trocknen und abschließen [C011/C013/C015-Arbeitshypothese]."
)
C015_READING = (
    "Dieselbe Krautdroge bis zur Mittelstufe abkühlen und abschließen; anschließend die so "
    "abgekühlte Krautdroge mäßig trocknen, nochmals mäßig trocknen und abschließen."
)
C016_READING = "Die leicht getrocknete fertige Zubereitung weiter erhitzen, trocknen und ansetzen."


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


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    assert len(hits) == 1, (wanted, len(hits))
    return hits[0]


def pipe(values: Sequence[str]) -> str:
    clean = [str(value) for value in values if value and value != "NONE"]
    return "|".join(dict.fromkeys(clean)) if clean else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(CONT_SPEC)
    result_spec_fields, result_specs = read_tsv(RESULT_SPEC)
    assert spec_fields == CONT_SPEC_FIELDS and len(specs) == 15
    assert result_spec_fields == RESULT_SPEC_FIELDS and len(result_specs) == 2
    assert Counter(row["decision"] for row in specs) == {
        "HOLD_OPEN": 13, "ADMIT_NEW": 1, "REPLAY_EXISTING": 1,
    }
    assert Counter(row["material_head_class"] for row in specs) == {
        "DIFFERENT_EXPLICIT": 5, "RELATED_EXPLICIT": 3, "EXACT_EXPLICIT_REPEAT": 4,
        "DEICTIC_TARGET": 2, "NO_WRITTEN_MATERIAL_HEAD": 1,
    }
    assert all(row["portable_default"] == "NO" for row in specs)

    _, clauses = read_tsv(G695)
    _, old_census = read_tsv(OLD_CENSUS)
    membership_fields, old_membership = read_tsv(OLD_MEMBERSHIP)
    component_fields, old_components = read_tsv(OLD_COMPONENTS)
    position_fields, old_positions = read_tsv(OLD_POSITIONS)
    token_fields, old_tokens = read_tsv(OLD_TOKENS)
    line_fields, old_lines = read_tsv(OLD_LINES)
    span_fields, old_spans = read_tsv(OLD_SPANS)
    old_result = json.loads(OLD_RESULT.read_text(encoding="utf-8"))
    assert len(clauses) == 175 and len(old_census) == 83
    assert len(old_membership) == 14 and len(old_components) == 10 and len(old_positions) == 29
    assert len(old_tokens) == 479 and len(old_lines) == 51 and len(old_spans) == 3
    assert old_result["basis"]["relation_edges_after"] == 14
    assert all(not row["page"].startswith("f84") for row in old_tokens)

    clause_index = {(row["locus"], row["clause_id"]): row for row in clauses}
    token_index = {(row["locus"], row["token_ordinal"]): row for row in old_tokens}
    action_census = [row for row in old_census if row["right_clause_type"] == "ACTION_CLAUSE"]
    assert len(action_census) == 15
    assert [row["action_case_id"] for row in action_census] == [row["action_case_id"] for row in specs]
    spec_index = {row["action_case_id"]: row for row in specs}

    continuations: list[dict[str, object]] = []
    for old in action_census:
        spec = spec_index[old["action_case_id"]]
        right = clause_index[(old["locus"], old["right_clause_id"])]
        assert right["clause_type"] == "ACTION_CLAUSE" and right["action_ordinals"] != "NONE"
        assert int(right["start_ordinal"]) == int(old["action_clause_end"]) + 1
        right_action = token_index[(old["locus"], right["action_ordinals"])]
        continuations.append({
            "action_case_id": old["action_case_id"], "page": old["page"], "locus": old["locus"],
            "left_clause_id": old["action_clause_id"], "left_clause_start": old["action_clause_start"],
            "left_clause_end": old["action_clause_end"], "left_clause_surfaces": old["action_clause_surfaces"],
            "left_action_ordinal": old["action_ordinal"], "left_action_surface": old["action_surface"],
            "left_action_gloss_de": old["action_gloss_de"], "right_clause_id": right["clause_id"],
            "right_clause_start": right["start_ordinal"], "right_clause_end": right["end_ordinal"],
            "right_clause_surfaces": right["surfaces"], "right_action_ordinal": right["action_ordinals"],
            "right_action_surface": right_action["surface"], "right_action_gloss_de": right_action["v76_token_gloss_de"],
            **{k: spec[k] for k in CONT_SPEC_FIELDS[1:]},
            "full_clause_boundary_preserved": 1, "word_delta": 0, "status": STATUS,
        })
    write_tsv(CONT_OUT, continuations, CONT_FIELDS)
    repeats = [row for row in continuations if row["material_head_class"] == "EXACT_EXPLICIT_REPEAT"]
    assert [row["action_case_id"] for row in repeats] == ["A034", "A062", "A080", "A081"]
    assert Counter(row["decision"] for row in repeats) == {"HOLD_OPEN": 3, "ADMIT_NEW": 1}
    write_tsv(REPEAT_OUT, repeats, CONT_FIELDS)

    result_controls: list[dict[str, object]] = []
    for spec in result_specs:
        result_token = token_index[(spec["locus"], spec["result_ordinal"])]
        target = one(clauses, locus=spec["locus"], start_ordinal=spec["target_clause_start"], end_ordinal=spec["target_clause_end"])
        assert result_token["surface"] == spec["result_surface"]
        assert result_token["v76_token_gloss_de"] == spec["result_gloss_de"]
        assert target["clause_type"] == "ACTION_CLAUSE" and target["surfaces"] == spec["target_surfaces"]
        result_controls.append({**spec, "target_clause_id": target["clause_id"], "verified": 1, "word_delta": 0, "status": STATUS})
    assert {row["decision"] for row in result_controls} == {"REPLAY_C011_NO_REDUNDANT_EDGE", "HOLD_OPEN_C016"}
    write_tsv(RESULT_CONTROL_OUT, result_controls, RESULT_CONTROL_FIELDS)

    c015 = {
        "edge_id": "C015", "component_id": "M009", "locus": "f26r.2", "support_tier": "B_WORKING_LOCAL",
        "relation_class": "ACTION_OUTPUT_TO_REPEATED_WRITTEN_MATERIAL_ACTION",
        "source_clause_ordinals": "6|7", "source_edge_node_ordinal": 6,
        "source_action_surface": "ytedy", "source_action_gloss_de": "hiervon bis zur Mittelstufe abkühlen und abschließen",
        "structural_closure_ordinal": 7, "structural_closure_surface": "dy",
        "target_action_ordinal": 8, "target_action_surface": "checthedy",
        "target_action_gloss_de": "Krautdroge mäßig trocknen, nochmals mäßig trocknen und abschließen",
        "repeated_material_head_de": "Krautdroge",
        "continuation_basis": "C011 bindet dieselbe Krautdroge an #6; #8 schreibt Krautdroge erneut und verarbeitet sie weiter.",
        "working_microrecord_de": C015_READING,
        "strongest_rival_de": "Der Abschluss #7 kann den Posten trennen und #8 einen neuen gleich bezeichneten Krautposten eröffnen.",
        "right_break_ordinal": 9, "right_break_surface": "ls", "portability": "OCCURRENCE_BOUND_ONLY",
        "gdt388_score_ready": 0,
        "forbidden_inference": "Keinen allgemeinen Krautdroge-Wiederholungsedge und keine #5→#6, #5→#8, #4→#8, #6→#7 oder #8→#9-Kante exportieren.",
        "edge_delta": 1, "word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [c015], EDGE_FIELDS)

    membership_out_fields = [*membership_fields[:-1], "v77_change", "status"]
    memberships: list[dict[str, object]] = []
    for old in old_membership:
        row: dict[str, object] = {**old, "v77_change": "NONE", "status": STATUS}
        if old["component_id"] == "M009":
            row.update({"component_edge_count": 3, "component_topology": "ACTION_STATE_FORK_WITH_DOWNSTREAM_ACTION_CHAIN", "shared_edge_node_ordinals": "4|6", "v77_change": "COMPONENT_EXTENDED_BY_C015__EXISTING_ENDPOINTS_UNCHANGED"})
        memberships.append(row)
    memberships.append({
        "edge_id": "C015", "component_id": "M009", "locus": "f26r.2", "support_tier": "B_WORKING_LOCAL",
        "relation_class": "ACTION_OUTPUT_TO_REPEATED_WRITTEN_MATERIAL_ACTION", "edge_node_ordinals": "6|8",
        "source_ordinals": "6", "target_ordinal": "8", "target_role": "TARGET_ACTION_WITH_REPEATED_WRITTEN_MATERIAL",
        "component_edge_count": 3, "component_topology": "ACTION_STATE_FORK_WITH_DOWNSTREAM_ACTION_CHAIN",
        "shared_edge_node_ordinals": "4|6", "origin": "GDT704_NEW_OCCURRENCE_BOUND",
        "v75_change": "NONE", "v76_change": "NONE", "v77_change": "NEW_EDGE", "status": STATUS,
    })
    memberships.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert len(memberships) == 15
    write_tsv(MEMBERSHIP_OUT, memberships, membership_out_fields)

    component_out_fields = [*component_fields[:-1], "v77_edge_delta", "v77_change", "status"]
    components: list[dict[str, object]] = []
    for old in old_components:
        row: dict[str, object] = {**old, "v77_edge_delta": 0, "v77_change": "NONE", "status": STATUS}
        if old["component_id"] == "M009":
            row.update({
                "edge_ids": "C011|C013|C015", "edge_count": 3, "edge_node_ordinals": "4|5|6|8", "edge_node_count": 4,
                "shared_edge_node_ordinals": "4|6", "edge_hull_start": 4, "edge_hull_end": 8,
                "edge_hull_position_count": 5, "hull_only_ordinals": "7", "render_window_start": 4,
                "render_window_end": 8, "render_only_structural_ordinals": "NONE", "render_window_token_count": 5,
                "topology": "ACTION_STATE_FORK_WITH_DOWNSTREAM_ACTION_CHAIN", "action_ordinals": "4|6|8",
                "expected_surfaces": "ykecthey|chedy|ytedy|dy|checthedy", "observed_surfaces": "ykecthey|chedy|ytedy|dy|checthedy",
                "microrecord_de": M009_READING,
                "component_basis": "C013 binds #4 to written checkpoint #5; C011 carries the #4 herb output to #6; C015 carries the completed #6-7 cooling output to #8, which explicitly rewrites Krautdroge.",
                "boundary_note_de": "#7 remains the structural closure of the C015 source clause but is now hull-only; #9 ls (Holz) is the right break.",
                "forbidden_inference": "Keinen #5→#6, #5→#8, #4→#8, #6→#7 oder #8→#9-Edge und keinen portablen Materialkopf-Default ergänzen.",
                "final_result_status": "WRITTEN_INTERMEDIATE_STATE_CHECKPOINT:C013|FINAL_ACTION_RESULT_UNWRITTEN:C015",
                "origin": "GDT704_EXTENDED_EXACT", "v77_edge_delta": 1,
                "v77_change": "C015_ADDED__STRUCTURAL_POSITION_MOVED_INTO_HULL",
            })
        components.append(row)
    assert len(components) == 10
    write_tsv(COMPONENTS_OUT, components, component_out_fields)

    position_out_fields = [*position_fields[:-1], "v77_change", "status"]
    positions: list[dict[str, object]] = []
    for old in old_positions:
        row: dict[str, object] = {**old, "v77_change": "NONE", "status": STATUS}
        if old["component_id"] == "M009":
            ordinal = old["token_ordinal"]
            row.update({"render_size": 5, "component_microrecord_de": M009_READING})
            if ordinal == "4":
                row["v77_change"] = "COMPONENT_READING_EXTENDED_BY_C015"
            elif ordinal == "5":
                row["v77_change"] = "CHECKPOINT_REMAINS_LEAF"
            elif ordinal == "6":
                row.update({"component_role": "REFERENCE:C011|TARGET_ACTION:C011|SOURCE_ACTION_OUTPUT:C015", "edge_ids": "C011|C015", "source_edge_ids": "C015", "reference_edge_ids": "C011", "target_edge_ids": "C011", "is_shared_edge_node": 1, "action_output_role": "C011_TARGET_ACTION_OUTPUT_SOURCE:C015", "v77_change": "TARGET_TO_SHARED_SERIAL_BRIDGE"})
            elif ordinal == "7":
                row.update({"component_role": "FREE_DY_STRUCTURAL_CLOSURE:C011|C015_SOURCE_CLAUSE", "membership_class": "HULL_ONLY", "is_hull_only": 1, "is_render_only_structural": 0, "v77_change": "RENDER_ONLY_STRUCTURAL_TO_HULL_ONLY_STRUCTURAL"})
        positions.append(row)
    target_token = token_index[("f26r.2", "8")]
    positions.append({
        "page": target_token["page"], "locus": "f26r.2", "token_ordinal": 8, "surface": target_token["surface"],
        "token_gloss_de": target_token["v76_token_gloss_de"], "component_id": "M009", "render_position": 5,
        "render_size": 5, "component_role": "REPEATED_WRITTEN_MATERIAL_TARGET_ACTION:C015", "edge_ids": "C015",
        "source_edge_ids": "NONE", "reference_edge_ids": "NONE", "target_edge_ids": "C015",
        "membership_class": "EDGE_NODE", "is_edge_node": 1, "is_hull_only": 0,
        "is_render_only_structural": 0, "is_action_target": 1, "is_shared_edge_node": 0,
        "action_output_role": "C015_TARGET_RESULT_UNWRITTEN", "component_microrecord_de": M009_READING,
        "word_delta": 0, "v76_change": "NONE", "v77_change": "NEW_C015_TARGET_EDGE_NODE", "status": STATUS,
    })
    positions.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(positions) == 30 and len({(row["locus"], str(row["token_ordinal"])) for row in positions}) == 30
    assert Counter(row["membership_class"] for row in positions) == {"EDGE_NODE": 28, "HULL_ONLY": 2}
    assert sum(int(row["is_shared_edge_node"]) for row in positions) == 5
    write_tsv(POSITIONS_OUT, positions, position_out_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_rows: list[dict[str, object]] = []
    for dimension, groups, note in (("TOPOLOGY", topology_groups, "exact occurrence-component topology"), ("SUPPORT_PROFILE", support_groups, "tiers remain local and are not averaged")):
        for value in sorted(groups):
            topology_rows.append({"dimension": dimension, "value": value, "count": len(groups[value]), "component_ids": pipe(groups[value]), "note": note, "status": STATUS})
    all_components = pipe([f"M{i:03d}" for i in range(1, 11)])
    topology_rows.extend([
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 28, "component_ids": all_components, "note": "unique occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 2, "component_ids": "M008|M009", "note": "f86v5.24#2 plus structural f26r.2#7", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 0, "component_ids": "NONE", "note": "f26r.2#7 moved into the C015 hull but remains structural", "status": STATUS},
        {"dimension": "STRUCTURAL_ROLE", "value": "CLAUSE_CLOSURE_NONNODE", "count": 1, "component_ids": "M009", "note": "f26r.2#7 remains a structural closure", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "EDGE_INCIDENCE", "count": 33, "component_ids": all_components, "note": "sum of edge endpoint incidences", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "MINIMAL_HULL_POSITION", "count": 30, "component_ids": all_components, "note": "sum of component hull sizes", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "RENDER_POSITION", "count": 30, "component_ids": all_components, "note": "sum of render-window sizes", "status": STATUS},
        {"dimension": "CONTINUATION_CONTROL", "value": "EXACT_REPEATED_MATERIAL_HEAD", "count": 4, "component_ids": "M006|M009", "note": "one output continuation and three ingredient additions", "status": STATUS},
        {"dimension": "CONTINUATION_CONTROL", "value": "ADMITTED_NEW_OUTPUT_CONTINUATION", "count": 1, "component_ids": "M009", "note": "C015 only", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packet = [{
        "edge_id": "C015", "batch_id": "GDT704_V77", "page": "f26r", "physical_folio": "f26",
        "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_6_YTEDY_ACTION_OUTPUT",
        "pivot_locus": "f26r.2@6-7", "target_visual_id": "TOKEN_8_CHECTHEDY_REPEATED_HERB_ACTION",
        "target_locus": "f26r.2@8", "relation_type": "WORKSHOP_ACTION_OUTPUT_TO_REPEATED_WRITTEN_MATERIAL_ACTION",
        "direction_basis": "COMPLETE_COOLING_CLAUSE_THEN_IMMEDIATE_ACTION_WITH_REPEATED_HERB_HEAD",
        "ownership_basis": "C011_CARRIED_HERB_BATCH_PLUS_EXPLICIT_REPEATED_KRAUTDROGE",
        "geometry_only_selection": "FALSE", "source_manifest_id": "GDT704", "page_crop_sha256": "NONE",
        "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE", "source_aware_localizer": "GDT704_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "B_WORKING_LOCAL",
        "ambiguity_state": "WORKSHOP_ONLY", "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
    }]
    write_tsv(PACKET_OUT, packet, PACKET_FIELDS)
    intake_run = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", rel(PACKET_OUT)], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0, "eligible_folios": 0,
        "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    assert intake_run.returncode == 1 and not intake_run.stderr
    assert json.loads(intake_run.stdout) == expected_intake
    INTAKE_OUT.write_text(json.dumps(expected_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cont_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    cont_roles: dict[tuple[str, int], set[str]] = defaultdict(set)
    head_classes: dict[tuple[str, int], set[str]] = defaultdict(set)
    decisions: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in continuations:
        locus = str(row["locus"])
        for ordinal in range(int(row["left_clause_start"]), int(row["left_clause_end"]) + 1):
            key = (locus, ordinal); cont_ids[key].add(str(row["action_case_id"])); cont_roles[key].add("LEFT_ACTION")
            head_classes[key].add(str(row["material_head_class"])); decisions[key].add(str(row["decision"]))
        for ordinal in range(int(row["right_clause_start"]), int(row["right_clause_end"]) + 1):
            key = (locus, ordinal); cont_ids[key].add(str(row["action_case_id"])); cont_roles[key].add("RIGHT_ACTION")
            head_classes[key].add(str(row["material_head_class"])); decisions[key].add(str(row["decision"]))
    result_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in result_controls:
        result_ids[(str(row["locus"]), int(row["result_ordinal"]))].add(str(row["control_id"]))
        for ordinal in range(int(row["target_clause_start"]), int(row["target_clause_end"]) + 1):
            result_ids[(str(row["locus"]), ordinal)].add(str(row["control_id"]))
    position_index = {(str(row["locus"]), int(row["token_ordinal"])): row for row in positions}
    token_overlay: list[dict[str, object]] = []
    for old in old_tokens:
        key = (old["locus"], int(old["token_ordinal"])); position = position_index.get(key)
        edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **old, "v77_action_continuation_ids": pipe(sorted(cont_ids.get(key, set()))),
            "v77_action_continuation_roles": pipe(sorted(cont_roles.get(key, set()))),
            "v77_material_head_classes": pipe(sorted(head_classes.get(key, set()))),
            "v77_continuation_decisions": pipe(sorted(decisions.get(key, set()))),
            "v77_objectless_result_control_ids": pipe(sorted(result_ids.get(key, set()))),
            "v77_component_id": position["component_id"] if position else "NONE",
            "v77_component_position": position["render_position"] if position else "NONE",
            "v77_component_role": position["component_role"] if position else "NONE",
            "v77_component_edge_ids": edges,
            "v77_component_membership_class": position["membership_class"] if position else "NONE",
            "v77_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v77_new_continuation_edge_ids": "C015" if "C015" in edges.split("|") else "NONE",
            "v77_token_gloss_de": old["v76_token_gloss_de"], "v77_word_delta": 0, "v77_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v77_token_gloss_de"] == old["v76_token_gloss_de"] for new, old in zip(token_overlay, old_tokens))
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    cont_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    results_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in continuations: cont_by_locus[str(row["locus"])].append(row)
    for row in result_controls: results_by_locus[str(row["locus"])].append(row)
    component_by_locus = {str(row["locus"]): row for row in components}
    line_overlay: list[dict[str, object]] = []
    for old in old_lines:
        local = cont_by_locus.get(old["locus"], []); local_results = results_by_locus.get(old["locus"], [])
        component = component_by_locus.get(old["locus"]); edges = str(component["edge_ids"]) if component else "NONE"
        line_overlay.append({
            **old, "v77_action_continuation_ids": pipe([str(row["action_case_id"]) for row in local]),
            "v77_exact_head_repeat_ids": pipe([str(row["action_case_id"]) for row in local if row["material_head_class"] == "EXACT_EXPLICIT_REPEAT"]),
            "v77_continuation_decisions": pipe([str(row["decision"]) for row in local]),
            "v77_objectless_result_control_ids": pipe([str(row["control_id"]) for row in local_results]),
            "v77_component_ids": component["component_id"] if component else "NONE", "v77_edge_ids": edges,
            "v77_component_topologies": component["topology"] if component else "NONE",
            "v77_component_microrecords_de": component["microrecord_de"] if component else "NONE",
            "v77_new_continuation_edge_ids": "C015" if "C015" in edges.split("|") else "NONE",
            "v77_working_relation_reading_de": C015_READING if old["locus"] == "f26r.2" else (C016_READING + " [OFFEN, kein Edge]") if old["locus"] == "f115r.23" else "NONE",
            "v77_line_translation_de": old["v76_line_translation_de"], "v77_word_delta": 0, "v77_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v77_line_translation_de"] == old["v76_line_translation_de"] for new, old in zip(line_overlay, old_lines))
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{**old, "v77_selected_gloss_de": old["v76_selected_gloss_de"], "v77_byte_identical": 1, "v77_relation_change": "NONE", "v77_status": STATUS} for old in old_spans]
    assert all(new["v77_selected_gloss_de"] == old["v76_selected_gloss_de"] for new, old in zip(span_overlay, old_spans))
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT704 — V77 repeated-material continuation reader", "", f"Status: `{STATUS}`", "",
        "## Konkrete neue Fortsetzung", "", f"> **C015 / f26r.2:** {M009_READING}", "",
        "Die enge neue Aussage lautet: Nach dem Abkühlen wird **dieselbe Krautdroge** weitergetrocknet. Der Grund ist nicht bloße Nachbarschaft: C011 trägt die Krautcharge in die Kühlhandlung #6–7, und die sofort folgende Handlung #8 schreibt den Materialkopf Krautdroge erneut. #7 bleibt nur der strukturelle Abschluss der linken Handlung. #9 `ls` (Holz) ist der sichtbare rechte Bruch.", "",
        "## Die vier exakten Materialkopf-Wiederholungen", "", "| Fall | Stelle | Wiederholung | Prozessrolle | Entscheidung |", "|---|---|---|---|---|",
    ]
    for row in repeats:
        reader.append(f"| {row['action_case_id']} | `{row['locus']}` | {row['left_material_head_de']} → {row['right_material_head_de']} | {row['process_relation_class']} | {row['decision']}{' ' + row['edge_id'] if row['edge_id'] != 'NONE' else ''} |")
    reader.extend([
        "", "Die drei Drogenstoff-Wiederholungen sind Zutatenserien: Sie wiederholen das Hinzugegebene, nicht den Ausgang der vorangehenden Zugabe. Nur A034 ist zugleich Materialwiederholung und plausible Ausgangsfortsetzung.", "",
        "## C016 bleibt absichtlich offen", "", f"> **Offene Lesart / f115r.23:** {C016_READING}", "",
        "Sie ist praktisch möglich, aber `qokcho` schreibt weder einen Rückverweis noch einen Materialkopf; unmittelbar danach steht mit #6 ein Samenposten. Deshalb ist C016 keine Kante. Offen bedeutet hier nicht verworfen: Eine spätere passendere Bindung darf sie ersetzen oder bestätigen.", "",
        "## Vollständigkeit", "", "Der Vergleich umfasst alle **15** direkten Aktion→Aktion-Übergänge: vier exakte Materialkopf-Wiederholungen, zwei deiktische Ziele, drei verwandte Köpfe, fünf klare Kopfwechsel und einen materialkopf-losen Übergang. C006 wird einmal wiederholt, C015 einmal neu aufgenommen, 13 Fälle bleiben offen. Der kumulative Graph besitzt **15 Kanten in 10 Komponenten**. Die 479 Token-Glossen, 51 Zeilenübersetzungen, 3 Spannen und 36 Seiten bleiben unverändert.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")
    (ART / "README.md").write_text(
        "# GDT704 artifacts\n\n"
        "- `V77_15_ACTION_TO_ACTION_CONTINUATIONS.tsv`: complete direct action-continuation deck.\n"
        "- `V77_4_EXACT_REPEATED_MATERIAL_HEADS.tsv`: the exact-head comparison that isolates C015.\n"
        "- `V77_2_OBJECTLESS_POST_RESULT_CONTROLS.tsv`: C011 replay and open C016 contrast.\n"
        "- `V77_1_NEW_REPEATED_MATERIAL_EDGE.tsv`: C015 only.\n"
        "- `V77_15_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V77_10_CONNECTED_COMPONENTS.tsv`, and `V77_30_COMPONENT_POSITION_ROLES.tsv`: cumulative graph.\n"
        "- `V77_COMPONENT_TOPOLOGY_CENSUS.tsv`: graph and control accounting.\n"
        "- `V77_GDT388_EDGE_PACKET.tsv` and `V77_GDT388_EDGE_INTAKE.json`: explicit invalid/not-score-ready intake.\n"
        "- `V77_479_TOKEN_RELATION_OVERLAY.tsv`, `V77_51_LINE_RELATION_OVERLAY.tsv`, and `V77_3_BOUND_SPAN_FREEZE.tsv`: unchanged words with V77 relation metadata.\n"
        "- `GDT704_V77_REPEATED_MATERIAL_READER.md`: practical German reading.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    node_keys = {(str(row["locus"]), ordinal) for row in memberships for ordinal in str(row["edge_node_ordinals"]).split("|")}
    assert len(node_keys) == 28
    assert sum(len(str(row["edge_node_ordinals"]).split("|")) for row in memberships) == 33
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 30
    assert sum(int(row["render_window_token_count"]) for row in components) == 30
    assert json.loads(G388.read_text(encoding="utf-8"))["acquisition"]["scoring_authorized"] is False

    generated = [CONT_OUT, REPEAT_OUT, RESULT_CONTROL_OUT, EDGE_OUT, MEMBERSHIP_OUT, COMPONENTS_OUT, POSITIONS_OUT, TOPOLOGY_OUT, PACKET_OUT, INTAKE_OUT, TOKENS_OUT, LINES_OUT, SPANS_OUT, READER_OUT, ART / "README.md"]
    inputs = [G388, G695, OLD_RESULT, OLD_CENSUS, OLD_MEMBERSHIP, OLD_COMPONENTS, OLD_POSITIONS, OLD_TOKENS, OLD_LINES, OLD_SPANS, CONT_SPEC, RESULT_SPEC, Path(__file__).resolve()]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51, "source_clauses": 175,
            "action_clauses": 83, "bound_spans": 3, "direct_action_continuations": 15,
            "exact_repeated_material_heads": 4, "deictic_targets": 2, "related_material_heads": 3,
            "different_material_heads": 5, "no_written_material_head": 1,
            "admitted_new_continuations": 1, "replayed_existing_continuations": 1,
            "open_continuations": 13, "objectless_post_result_controls": 2,
            "relation_edges_before": 14, "relation_edges_after": 15, "new_edges": 1,
            "connected_components": 10, "edge_nodes": 28, "edge_node_incidences": 33,
            "minimal_hull_positions": 30, "render_positions": 30, "shared_edge_nodes": 5,
            "hull_only_positions": 2, "render_only_structural_positions": 0,
            "structural_closure_positions": 1, "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "new_edge": "C015", "c015": "f26r.2#6→f26r.2#8", "source_clause": "f26r.2#6-7",
            "target_action": "f26r.2#8", "repeated_material_head": "Krautdroge", "component": "M009",
            "c016": "HOLD_OPEN_B_LOW", "c016_candidate": "f115r.23#4→f115r.23#5",
            "c006_replayed": True, "changed_existing_edges": 0, "redundant_5_to_6_edge": False,
            "portable_material_repeat_default": False, "new_word_meanings": 0,
        },
        "graph": {
            "component_partition": [["C009"], ["C001", "C012"], ["C002"], ["C003"], ["C004", "C008"], ["C005"], ["C006", "C007"], ["C010"], ["C011", "C013", "C015"], ["C014"]],
            "shared_nodes": ["f105v.1#4", "f26r.2#4", "f26r.2#6", "f80v.35#3", "f86v6.25#4"],
            "hull_only_positions": ["f26r.2#7", "f86v5.24#2"], "render_only_structural_positions": [],
            "structural_closure": "f26r.2#7",
        },
        "gdt388": expected_intake,
        "freeze": {
            "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0, "changed_word_meanings": 0,
            "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0,
        },
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated}, "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "action_continuations": 15, "exact_head_repeats": 4, "new_edge": "C015", "c016": "HOLD_OPEN", "edges": 15, "components": 10, "edge_nodes": 28, "render_positions": 30, "new_word_meanings": 0}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
