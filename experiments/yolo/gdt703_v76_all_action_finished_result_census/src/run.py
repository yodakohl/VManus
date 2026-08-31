#!/usr/bin/env python3
"""Build GDT703's all-action successor census and cumulative V76 relation graph."""

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
EXP = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V76_83_ACTION_RIGHT_CONTEXTS__60_NOMINAL_15_ACTION_8_EOS__"
    "7_FINISHED_STATE_FIRSTS__3_LOCAL_READS_4_OPEN__C013_C014_ADDED__ZERO_WORD_DELTA"
)
QUESTION = (
    "Does the no-skip census of all 83 current action clauses isolate every immediate "
    "written finished-state successor, and can the seven cases support two additional "
    "occurrence-bound practical readings without changing a word meaning or exporting a default?"
)
CLAIM = (
    "V76 exhausts the first semantic item after all 83 current action clauses: 60 lead to a "
    "nominal block, 15 to another action and 8 to line end. Exactly seven first items are already "
    "typed HIGH nominal finished-result states. C012 is retained; C013 locally reads f26r.2#5 as "
    "the written state reached by #4, and C014 locally reads f115r.23#4 as the written preparation "
    "completed by #3. Four plausible but materially or operationally weaker juxtapositions remain "
    "open non-edge readings. These are replaceable workshop relations, not recovered plaintext, "
    "portable word rules or historical decipherment."
)
NEXT_GAP = (
    "Use the now complete seven-case result deck to inspect whether the two new written results "
    "receive a later compatible consumer or repeated material head inside the existing 36-page "
    "scope. Keep C013 and C014 local unless a second occurrence predicts the same composition; "
    "open no page and change no token gloss."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G687 = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G700 = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_10_ANA_CENSUS.tsv"
G702 = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast/artifacts"
G702_RESULT = G702 / "RESULT.json"
G702_MEMBERSHIP = G702 / "V75_12_EDGE_COMPONENT_MEMBERSHIP.tsv"
G702_COMPONENTS = G702 / "V75_9_CONNECTED_COMPONENTS.tsv"
G702_POSITIONS = G702 / "V75_27_COMPONENT_POSITION_ROLES.tsv"
G702_TOKENS = G702 / "V75_479_TOKEN_RELATION_OVERLAY.tsv"
G702_LINES = G702 / "V75_51_LINE_RELATION_OVERLAY.tsv"
G702_SPANS = G702 / "V75_3_BOUND_SPAN_FREEZE.tsv"
SPEC = SRC / "V76_7_FINISHED_RESULT_CASE_SPECS.tsv"

CENSUS_OUT = ART / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv"
CANDIDATE_OUT = ART / "V76_7_FINISHED_RESULT_FIRSTS.tsv"
EDGE_OUT = ART / "V76_2_NEW_LOCAL_RESULT_EDGES.tsv"
MEMBERSHIP_OUT = ART / "V76_14_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V76_10_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V76_29_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V76_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V76_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V76_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V76_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V76_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V76_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT703_V76_ALL_ACTION_RESULT_READER.md"
RESULT_OUT = ART / "RESULT.json"
ARTIFACT_README = ART / "README.md"

SPEC_FIELDS = [
    "candidate_id", "locus", "action_clause_id", "action_ordinal", "action_surface",
    "action_gloss_de", "right_clause_id", "result_ordinal", "result_surface",
    "result_gloss_de", "result_dispatch", "result_confidence",
    "material_or_output_basis", "decision", "edge_id", "component_id", "support_tier",
    "relation_class", "working_reading_de", "strongest_rival_de", "portability",
]
CENSUS_FIELDS = [
    "action_case_id", "page", "locus", "action_clause_id", "action_clause_start",
    "action_clause_end", "action_clause_surfaces", "action_ordinal", "action_surface",
    "action_gloss_de", "right_clause_id", "right_clause_type", "right_clause_start",
    "right_clause_end", "right_first_ordinal", "right_first_surface", "right_first_gloss_de",
    "right_dispatch", "right_confidence", "intervening_semantic_items", "candidate_id",
    "candidate_decision", "full_clause_then_first_item_exact", "word_delta", "status",
]
CANDIDATE_FIELDS = [*SPEC_FIELDS, "action_case_id", "right_context_is_immediate", "word_delta", "status"]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "edge_node_ordinals", "source_action_ordinal", "source_action_surface",
    "source_action_gloss_de", "written_result_ordinal", "written_result_surface",
    "written_result_gloss_de", "written_result_dispatch", "material_or_output_basis",
    "admission_basis", "working_microrecord_de", "strongest_rival_de", "portability",
    "gdt388_score_ready", "forbidden_inference", "edge_delta", "word_delta", "status",
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
    "v76_action_census_ids", "v76_action_census_roles", "v76_finished_candidate_ids",
    "v76_candidate_decisions", "v76_component_id", "v76_component_position",
    "v76_component_role", "v76_component_edge_ids", "v76_component_membership_class",
    "v76_component_microrecord_de", "v76_new_result_edge_ids", "v76_token_gloss_de",
    "v76_word_delta", "v76_status",
]
LINE_EXTRA = [
    "v76_action_census_ids", "v76_finished_candidate_ids", "v76_candidate_decisions",
    "v76_component_ids", "v76_edge_ids", "v76_component_topologies",
    "v76_component_microrecords_de", "v76_new_result_edge_ids",
    "v76_working_relation_reading_de", "v76_line_translation_de", "v76_word_delta",
    "v76_status",
]
SPAN_EXTRA = ["v76_selected_gloss_de", "v76_byte_identical", "v76_relation_change", "v76_status"]

M009_READING = (
    "Die Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von ‚hiervon‘ offen]. "
    "Zustand: mittlere Trockenstufe erreicht. Dieselbe erhitzte Krautdroge bis zur "
    "Mittelstufe abkühlen und abschließen [C011/C013-Arbeitshypothese]."
)
M010_READING = (
    "Heißen Auszug bereiten und abschließen. Ergebnis: leicht getrocknete, "
    "abgeschlossene Zubereitung."
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


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    assert len(hits) == 1, (wanted, len(hits))
    return hits[0]


def pipe(values: Sequence[str]) -> str:
    cleaned = [str(value) for value in values if value and value != "NONE"]
    return "|".join(dict.fromkeys(cleaned)) if cleaned else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(SPEC)
    assert spec_fields == SPEC_FIELDS and len(specs) == 7
    assert [row["candidate_id"] for row in specs] == [f"F{i:03d}" for i in range(1, 8)]
    assert Counter(row["decision"] for row in specs) == {
        "HOLD_OPEN": 4, "ADMIT_NEW": 2, "ADMIT_INHERITED": 1,
    }
    assert {row["edge_id"] for row in specs if row["decision"] == "ADMIT_NEW"} == {"C013", "C014"}

    _, clauses = read_tsv(G695)
    _, dispatch = read_tsv(G687)
    token_fields, tokens = read_tsv(G702_TOKENS)
    line_fields, lines = read_tsv(G702_LINES)
    span_fields, spans = read_tsv(G702_SPANS)
    membership_fields, old_membership = read_tsv(G702_MEMBERSHIP)
    component_fields, old_components = read_tsv(G702_COMPONENTS)
    position_fields, old_positions = read_tsv(G702_POSITIONS)
    result702 = json.loads(G702_RESULT.read_text(encoding="utf-8"))
    assert len(clauses) == 175 and Counter(row["clause_type"] for row in clauses) == {
        "NOMINAL_BLOCK": 92, "ACTION_CLAUSE": 83,
    }
    assert len(tokens) == 479 and len(lines) == 51 and len(spans) == 3
    assert all(not row["page"].startswith("f84") for row in tokens)
    assert all(not row["page"].startswith("f84") for row in clauses)
    assert len({row["page"] for row in tokens}) == 36 and len({row["locus"] for row in tokens}) == 51
    assert len(old_membership) == 12 and len(old_components) == 9 and len(old_positions) == 27
    assert result702["basis"]["relation_edges_after"] == 12
    assert result702["basis"]["edge_nodes"] == 24

    token_index = {(row["locus"], row["token_ordinal"]): row for row in tokens}
    dispatch_index = {(row["locus"], row["ordinal"]): row for row in dispatch}
    clauses_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_locus[row["locus"]].append(row)
    for local in clauses_by_locus.values():
        local.sort(key=lambda row: int(row["clause_id"]))
        assert [int(row["clause_id"]) for row in local] == list(range(1, len(local) + 1))
        assert all(int(right["start_ordinal"]) == int(left["end_ordinal"]) + 1 for left, right in zip(local, local[1:]))

    spec_index = {
        (row["locus"], row["action_ordinal"], row["result_ordinal"]): row for row in specs
    }
    census_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    candidate_seen: set[str] = set()
    action_counter = 0
    for clause in clauses:
        if clause["clause_type"] != "ACTION_CLAUSE":
            continue
        action_counter += 1
        case_id = f"A{action_counter:03d}"
        assert clause["action_ordinals"] != "NONE" and "|" not in clause["action_ordinals"]
        action_ordinal = clause["action_ordinals"]
        action_token = token_index[(clause["locus"], action_ordinal)]
        local = clauses_by_locus[clause["locus"]]
        local_index = local.index(clause)
        right = local[local_index + 1] if local_index + 1 < len(local) else None
        if right is None:
            right_values = {
                "right_clause_id": "NONE", "right_clause_type": "END_OF_LINE",
                "right_clause_start": "NONE", "right_clause_end": "NONE",
                "right_first_ordinal": "NONE", "right_first_surface": "NONE",
                "right_first_gloss_de": "NONE", "right_dispatch": "NONE",
                "right_confidence": "NONE",
            }
            spec = None
        else:
            first_ordinal = right["start_ordinal"]
            first_token = token_index[(clause["locus"], first_ordinal)]
            drow = dispatch_index.get((clause["locus"], first_ordinal))
            right_values = {
                "right_clause_id": right["clause_id"], "right_clause_type": right["clause_type"],
                "right_clause_start": right["start_ordinal"], "right_clause_end": right["end_ordinal"],
                "right_first_ordinal": first_ordinal, "right_first_surface": first_token["surface"],
                "right_first_gloss_de": first_token["v75_token_gloss_de"],
                "right_dispatch": drow["dispatch_class"] if drow else "NOT_IN_GDT687_TARGET_DECK",
                "right_confidence": drow["confidence"] if drow else "NONE",
            }
            spec = spec_index.get((clause["locus"], action_ordinal, first_ordinal))
        is_finished = right_values["right_dispatch"] == "NOMINAL_FINISHED_RESULT_STATE"
        assert is_finished == (spec is not None)
        candidate_id = spec["candidate_id"] if spec else "NONE"
        decision = spec["decision"] if spec else "OUTSIDE_FINISHED_RESULT_GATE"
        row = {
            "action_case_id": case_id, "page": clause["page"], "locus": clause["locus"],
            "action_clause_id": clause["clause_id"], "action_clause_start": clause["start_ordinal"],
            "action_clause_end": clause["end_ordinal"], "action_clause_surfaces": clause["surfaces"],
            "action_ordinal": action_ordinal, "action_surface": action_token["surface"],
            "action_gloss_de": action_token["v75_token_gloss_de"], **right_values,
            "intervening_semantic_items": 0, "candidate_id": candidate_id,
            "candidate_decision": decision, "full_clause_then_first_item_exact": 1,
            "word_delta": 0, "status": STATUS,
        }
        census_rows.append(row)
        if spec:
            assert spec["action_clause_id"] == clause["clause_id"]
            assert spec["action_surface"] == action_token["surface"]
            assert spec["action_gloss_de"] == action_token["v75_token_gloss_de"]
            assert spec["right_clause_id"] == right_values["right_clause_id"]
            assert spec["result_surface"] == right_values["right_first_surface"]
            assert spec["result_gloss_de"] == right_values["right_first_gloss_de"]
            assert spec["result_dispatch"] == right_values["right_dispatch"]
            assert spec["result_confidence"] == right_values["right_confidence"]
            drow = dispatch_index[(spec["locus"], spec["result_ordinal"])]
            assert drow["action_licensed_before"] == "0"
            assert drow["dy_contribution"] == "FINISHED_ENDPOINT_NOT_NEW_VERB"
            candidate_rows.append({
                **spec, "action_case_id": case_id, "right_context_is_immediate": 1,
                "word_delta": 0, "status": STATUS,
            })
            candidate_seen.add(spec["candidate_id"])

    assert action_counter == 83 and len(census_rows) == 83
    assert Counter(row["right_clause_type"] for row in census_rows) == {
        "NOMINAL_BLOCK": 60, "ACTION_CLAUSE": 15, "END_OF_LINE": 8,
    }
    assert candidate_seen == {row["candidate_id"] for row in specs}
    assert len(candidate_rows) == 7
    assert all(row["right_confidence"] == "HIGH" for row in census_rows if row["candidate_id"] != "NONE")
    write_tsv(CENSUS_OUT, census_rows, CENSUS_FIELDS)
    write_tsv(CANDIDATE_OUT, candidate_rows, CANDIDATE_FIELDS)

    # GDT700 already marked f26r.2#5 as the exact state-only checkpoint inside C011.
    _, g700_rows = read_tsv(G700)
    g700_f26 = one(g700_rows, locus="f26r.2")
    assert (g700_f26["source_start_ordinal"], g700_f26["checkpoint_ordinal"], g700_f26["target_start_ordinal"]) == ("4", "5", "6")
    assert g700_f26["checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT"
    assert g700_f26["exact_state_only_checkpoint"] == "1"

    new_edge_rows: list[dict[str, object]] = []
    for spec in specs:
        if spec["decision"] != "ADMIT_NEW":
            continue
        forbidden = (
            "Do not export CHEDY as the output of every heating action or infer a #5→#6 edge."
            if spec["edge_id"] == "C013" else
            "Do not export QOKEOD as a drying rule, CHODY as every left action's result, or attach #5 QOKCHO."
        )
        new_edge_rows.append({
            "edge_id": spec["edge_id"], "component_id": spec["component_id"],
            "locus": spec["locus"], "support_tier": spec["support_tier"],
            "relation_class": spec["relation_class"],
            "edge_node_ordinals": f"{spec['action_ordinal']}|{spec['result_ordinal']}",
            "source_action_ordinal": spec["action_ordinal"],
            "source_action_surface": spec["action_surface"],
            "source_action_gloss_de": spec["action_gloss_de"],
            "written_result_ordinal": spec["result_ordinal"],
            "written_result_surface": spec["result_surface"],
            "written_result_gloss_de": spec["result_gloss_de"],
            "written_result_dispatch": spec["result_dispatch"],
            "material_or_output_basis": spec["material_or_output_basis"],
            "admission_basis": "IMMEDIATE_WRITTEN_RESULT_PLUS_LOCAL_OPERATION_MATERIAL_COMPATIBILITY",
            "working_microrecord_de": spec["working_reading_de"],
            "strongest_rival_de": spec["strongest_rival_de"],
            "portability": spec["portability"], "gdt388_score_ready": 0,
            "forbidden_inference": forbidden, "edge_delta": 1, "word_delta": 0,
            "status": STATUS,
        })
    assert [row["edge_id"] for row in new_edge_rows] == ["C014", "C013"]
    new_edge_rows.sort(key=lambda row: str(row["edge_id"]))
    write_tsv(EDGE_OUT, new_edge_rows, EDGE_FIELDS)

    topology_m009 = "ACTION_STATE_AND_DOWNSTREAM_CARRY_FORK"
    membership_out_fields = [*membership_fields[:-1], "v76_change", "status"]
    membership_rows: list[dict[str, object]] = []
    for old in old_membership:
        row: dict[str, object] = {**old, "v76_change": "NONE", "status": STATUS}
        if old["edge_id"] == "C011":
            row.update({
                "component_edge_count": 2, "component_topology": topology_m009,
                "shared_edge_node_ordinals": "4",
                "v76_change": "COMPONENT_EXTENDED_BY_C013__C011_ENDPOINTS_UNCHANGED",
            })
        membership_rows.append(row)
    membership_rows.extend([
        {
            "edge_id": "C013", "component_id": "M009", "locus": "f26r.2",
            "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_WRITTEN_STATE_CHECKPOINT",
            "edge_node_ordinals": "4|5", "source_ordinals": "4", "target_ordinal": "5",
            "target_role": "WRITTEN_INTERMEDIATE_STATE_CHECKPOINT", "component_edge_count": 2,
            "component_topology": topology_m009, "shared_edge_node_ordinals": "4",
            "origin": "GDT703_NEW_OCCURRENCE_BOUND", "v75_change": "NONE",
            "v76_change": "NEW_EDGE", "status": STATUS,
        },
        {
            "edge_id": "C014", "component_id": "M010", "locus": "f115r.23",
            "support_tier": "B_LOW_WORKING_LOCAL",
            "relation_class": "ACTION_TO_WRITTEN_FINISHED_PREPARATION_STATE",
            "edge_node_ordinals": "3|4", "source_ordinals": "3", "target_ordinal": "4",
            "target_role": "WRITTEN_FINAL_PREPARATION_STATE", "component_edge_count": 1,
            "component_topology": "ACTION_WRITTEN_FINISHED_PREPARATION_PAIR",
            "shared_edge_node_ordinals": "NONE", "origin": "GDT703_NEW_OCCURRENCE_BOUND",
            "v75_change": "NONE", "v76_change": "NEW_EDGE", "status": STATUS,
        },
    ])
    membership_rows.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert [row["edge_id"] for row in membership_rows] == [f"C{i:03d}" for i in range(1, 15)]
    write_tsv(MEMBERSHIP_OUT, membership_rows, membership_out_fields)

    component_out_fields = [*component_fields[:-1], "v76_change", "status"]
    components: list[dict[str, object]] = []
    for old in old_components:
        row = {**old, "v76_change": "NONE", "status": STATUS}
        if old["component_id"] == "M009":
            row.update({
                "edge_ids": "C011|C013", "edge_count": 2, "edge_node_ordinals": "4|5|6",
                "edge_node_count": 3, "shared_edge_node_ordinals": "4",
                "hull_only_ordinals": "NONE", "topology": topology_m009,
                "support_profile": "B_ONLY", "microrecord_de": M009_READING,
                "component_basis": (
                    "C013 binds #4 to its immediately written exact state checkpoint #5; C011 independently "
                    "carries the heated herb result from #4 to deictic cooling action #6."
                ),
                "boundary_note_de": (
                    "#5 is now a C013 edge node but remains no C011 donor; free DY #7 is structural and #8 remains outside."
                ),
                "forbidden_inference": (
                    "Keinen #5→#6-Edge, keinen allgemeinen CHEDY-Ausgang und keinen Export zu #8 ergänzen."
                ),
                "final_result_status": "WRITTEN_INTERMEDIATE_STATE_CHECKPOINT:C013",
                "origin": "GDT703_EXTENDED_EXACT", "edge_delta": 1,
                "v76_change": "C013_ADDED__CHECKPOINT_PROMOTED_TO_EDGE_NODE",
            })
        components.append(row)
    components.append({
        "component_id": "M010", "locus": "f115r.23", "edge_ids": "C014", "edge_count": 1,
        "edge_node_ordinals": "3|4", "edge_node_count": 2, "shared_edge_node_ordinals": "NONE",
        "edge_hull_start": 3, "edge_hull_end": 4, "edge_hull_position_count": 2,
        "hull_only_ordinals": "NONE", "render_window_start": 3, "render_window_end": 4,
        "render_only_structural_ordinals": "NONE", "render_window_token_count": 2,
        "topology": "ACTION_WRITTEN_FINISHED_PREPARATION_PAIR", "action_ordinals": "3",
        "support_profile": "B_LOW_ONLY", "expected_surfaces": "qokeod|chody",
        "observed_surfaces": "qokeod|chody", "microrecord_de": M010_READING,
        "component_basis": (
            "C014 locally joins the complete hot-extract preparation action to the immediately written, "
            "independently typed completed preparation state."
        ),
        "boundary_note_de": "#2 remains the preceding heat register; #5 QOKCHO starts a new action and remains outside.",
        "forbidden_inference": (
            "QOKEOD nicht als allgemeines Trocknungsverb und CHODY nicht als Ergebnis jeder linken Aktion exportieren."
        ),
        "final_result_status": "WRITTEN_FINAL_PREPARATION_STATE:C014",
        "origin": "GDT703_NEW_EXPLORATORY", "edge_delta": 1, "word_delta": 0,
        "v76_change": "NEW_COMPONENT", "status": STATUS,
    })
    components.sort(key=lambda row: int(str(row["component_id"])[1:]))
    assert len(components) == 10
    write_tsv(COMPONENTS_OUT, components, component_out_fields)

    position_out_fields = [*position_fields[:-1], "v76_change", "status"]
    positions: list[dict[str, object]] = []
    for old in old_positions:
        row = {**old, "v76_change": "NONE", "status": STATUS}
        if old["component_id"] == "M009":
            row["component_microrecord_de"] = M009_READING
            if old["token_ordinal"] == "4":
                row.update({
                    "component_role": "INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:C011|SOURCE_ACTION:C013",
                    "edge_ids": "C011|C013", "source_edge_ids": "C011|C013",
                    "is_shared_edge_node": 1,
                    "action_output_role": "INFERRED_C011_SOURCE_RESULT|C013_WRITTEN_STATE_SOURCE",
                    "v76_change": "SHARED_SOURCE_FOR_C011_C013",
                })
            elif old["token_ordinal"] == "5":
                row.update({
                    "component_role": "WRITTEN_INTERMEDIATE_STATE_CHECKPOINT:C013",
                    "edge_ids": "C013", "target_edge_ids": "C013", "membership_class": "EDGE_NODE",
                    "is_edge_node": 1, "is_hull_only": 0,
                    "action_output_role": "WRITTEN_C013_STATE_RESULT",
                    "v76_change": "HULL_ONLY_TO_C013_EDGE_NODE",
                })
            else:
                row["v76_change"] = "COMPONENT_READING_EXTENDED_BY_C013"
        positions.append(row)
    for ordinal, role, source_ids, target_ids, output_role in [
        (3, "SOURCE_ACTION:C014", "C014", "NONE", "C014_WRITTEN_RESULT_SOURCE"),
        (4, "WRITTEN_FINAL_PREPARATION_STATE:C014", "NONE", "C014", "WRITTEN_C014_FINAL_PREPARATION"),
    ]:
        token = token_index[("f115r.23", str(ordinal))]
        positions.append({
            "page": token["page"], "locus": "f115r.23", "token_ordinal": ordinal,
            "surface": token["surface"], "token_gloss_de": token["v75_token_gloss_de"],
            "component_id": "M010", "render_position": ordinal - 2, "render_size": 2,
            "component_role": role, "edge_ids": "C014", "source_edge_ids": source_ids,
            "reference_edge_ids": "NONE", "target_edge_ids": target_ids,
            "membership_class": "EDGE_NODE", "is_edge_node": 1, "is_hull_only": 0,
            "is_render_only_structural": 0, "is_action_target": 0, "is_shared_edge_node": 0,
            "action_output_role": output_role, "component_microrecord_de": M010_READING,
            "word_delta": 0, "v76_change": "NEW_C014_EDGE_NODE", "status": STATUS,
        })
    positions.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(positions) == 29
    assert len({(row["locus"], str(row["token_ordinal"])) for row in positions}) == 29
    assert Counter(row["membership_class"] for row in positions) == {
        "EDGE_NODE": 27, "HULL_ONLY": 1, "RENDER_ONLY_STRUCTURAL": 1,
    }
    assert sum(int(row["is_shared_edge_node"]) for row in positions) == 4
    assert one(positions, component_id="M009", token_ordinal="5")["edge_ids"] == "C013"
    write_tsv(POSITIONS_OUT, positions, position_out_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_rows: list[dict[str, object]] = []
    for value in sorted(topology_groups):
        ids = topology_groups[value]
        topology_rows.append({
            "dimension": "TOPOLOGY", "value": value, "count": len(ids),
            "component_ids": pipe(ids), "note": "exact occurrence-component topology",
            "status": STATUS,
        })
    for value in sorted(support_groups):
        ids = support_groups[value]
        topology_rows.append({
            "dimension": "SUPPORT_PROFILE", "value": value, "count": len(ids),
            "component_ids": pipe(ids), "note": "tiers remain local and are not averaged",
            "status": STATUS,
        })
    all_components = "M001|M002|M003|M004|M005|M006|M007|M008|M009|M010"
    topology_rows.extend([
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 27, "component_ids": all_components, "note": "unique occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 1, "component_ids": "M008", "note": "only f86v5.24#2 remains hull-only", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 1, "component_ids": "M009", "note": "f26r.2#7 remains structural closure", "status": STATUS},
        {"dimension": "WRITTEN_RESULT_STATUS", "value": "FINAL_MATERIAL_OR_PREPARATION_RESULT", "count": 2, "component_ids": "M002|M010", "note": "C012 and C014 terminate in written material/preparation results", "status": STATUS},
        {"dimension": "WRITTEN_RESULT_STATUS", "value": "INTERMEDIATE_STATE_CHECKPOINT", "count": 1, "component_ids": "M009", "note": "C013 ends at #5 while C011 separately continues #4 to #6", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "EDGE_INCIDENCE", "count": 31, "component_ids": all_components, "note": "sum of edge endpoint incidences", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "MINIMAL_HULL_POSITION", "count": 28, "component_ids": all_components, "note": "sum of component hull sizes", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "RENDER_POSITION", "count": 29, "component_ids": all_components, "note": "sum of render-window sizes", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packets = [
        {
            "edge_id": "C013", "batch_id": "GDT703_V76", "page": "f26r", "physical_folio": "f26",
            "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_4_YKECTHEY_ACTION",
            "pivot_locus": "f26r.2@4", "target_visual_id": "TOKEN_5_CHEDY_STATE",
            "target_locus": "f26r.2@5", "relation_type": "WORKSHOP_ACTION_TO_WRITTEN_STATE_CHECKPOINT",
            "direction_basis": "FULL_ACTION_THEN_FIRST_SEMANTIC_FINISHED_STATE",
            "ownership_basis": "WRITTEN_HERB_PATIENT_PLUS_GDT700_EXACT_STATE_CHECKPOINT",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT703",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT703_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "B_WORKING_LOCAL", "ambiguity_state": "WORKSHOP_ONLY",
            "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
        },
        {
            "edge_id": "C014", "batch_id": "GDT703_V76", "page": "f115r", "physical_folio": "f115",
            "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_3_QOKEOD_ACTION",
            "pivot_locus": "f115r.23@3", "target_visual_id": "TOKEN_4_CHODY_RESULT_STATE",
            "target_locus": "f115r.23@4", "relation_type": "WORKSHOP_ACTION_TO_WRITTEN_PREPARATION_STATE",
            "direction_basis": "FULL_ACTION_THEN_FIRST_SEMANTIC_FINISHED_STATE",
            "ownership_basis": "LOCAL_EXTRACT_TO_COMPLETED_PREPARATION_COMPATIBILITY",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT703",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT703_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "B_LOW_WORKING_LOCAL", "ambiguity_state": "WORKSHOP_ONLY",
            "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
        },
    ]
    write_tsv(PACKET_OUT, packets, PACKET_FIELDS)
    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", rel(PACKET_OUT)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 2, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": [
            "edge row 2: formal access is not sealed",
            "edge row 3: formal access is not sealed",
        ],
    }
    assert intake_run.returncode == 1 and not intake_run.stderr
    assert json.loads(intake_run.stdout) == expected_intake
    INTAKE_OUT.write_text(json.dumps(expected_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    census_ids_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    census_roles_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    candidates_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    decisions_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in census_rows:
        locus = str(row["locus"])
        for ordinal in range(int(row["action_clause_start"]), int(row["action_clause_end"]) + 1):
            census_ids_by_position[(locus, ordinal)].add(str(row["action_case_id"]))
            census_roles_by_position[(locus, ordinal)].add(f"ACTION_CLAUSE:{row['action_case_id']}")
        if row["right_first_ordinal"] != "NONE":
            key = (locus, int(row["right_first_ordinal"]))
            census_ids_by_position[key].add(str(row["action_case_id"]))
            census_roles_by_position[key].add(f"FIRST_RIGHT_ITEM:{row['action_case_id']}")
        if row["candidate_id"] != "NONE":
            for ordinal in (int(row["action_ordinal"]), int(row["right_first_ordinal"])):
                key = (locus, ordinal)
                candidates_by_position[key].add(str(row["candidate_id"]))
                decisions_by_position[key].add(str(row["candidate_decision"]))

    position_index = {(str(row["locus"]), int(row["token_ordinal"])): row for row in positions}
    token_overlay: list[dict[str, object]] = []
    for old in tokens:
        key = (old["locus"], int(old["token_ordinal"]))
        position = position_index.get(key)
        edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **old,
            "v76_action_census_ids": pipe(sorted(census_ids_by_position.get(key, set()))),
            "v76_action_census_roles": pipe(sorted(census_roles_by_position.get(key, set()))),
            "v76_finished_candidate_ids": pipe(sorted(candidates_by_position.get(key, set()))),
            "v76_candidate_decisions": pipe(sorted(decisions_by_position.get(key, set()))),
            "v76_component_id": position["component_id"] if position else "NONE",
            "v76_component_position": position["render_position"] if position else "NONE",
            "v76_component_role": position["component_role"] if position else "NONE",
            "v76_component_edge_ids": edges,
            "v76_component_membership_class": position["membership_class"] if position else "NONE",
            "v76_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v76_new_result_edge_ids": pipe([edge for edge in edges.split("|") if edge in {"C013", "C014"}]),
            "v76_token_gloss_de": old["v75_token_gloss_de"], "v76_word_delta": 0,
            "v76_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v76_token_gloss_de"] == old["v75_token_gloss_de"] for new, old in zip(token_overlay, tokens))
    assert sum(row["v76_new_result_edge_ids"] != "NONE" for row in token_overlay) == 4
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    census_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    candidate_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in census_rows:
        census_by_locus[str(row["locus"])].append(row)
        if row["candidate_id"] != "NONE":
            candidate_by_locus[str(row["locus"])].append(row)
    component_by_locus = {str(row["locus"]): row for row in components}
    line_overlay: list[dict[str, object]] = []
    for old in lines:
        local_census = census_by_locus.get(old["locus"], [])
        local_candidates = candidate_by_locus.get(old["locus"], [])
        component = component_by_locus.get(old["locus"])
        new_edges = pipe([edge for edge in str(component["edge_ids"]).split("|") if edge in {"C013", "C014"}]) if component else "NONE"
        line_overlay.append({
            **old,
            "v76_action_census_ids": pipe([str(row["action_case_id"]) for row in local_census]),
            "v76_finished_candidate_ids": pipe([str(row["candidate_id"]) for row in local_candidates]),
            "v76_candidate_decisions": pipe([str(row["candidate_decision"]) for row in local_candidates]),
            "v76_component_ids": component["component_id"] if component else "NONE",
            "v76_edge_ids": component["edge_ids"] if component else "NONE",
            "v76_component_topologies": component["topology"] if component else "NONE",
            "v76_component_microrecords_de": component["microrecord_de"] if component else "NONE",
            "v76_new_result_edge_ids": new_edges,
            "v76_working_relation_reading_de": component["microrecord_de"] if component else "NONE",
            "v76_line_translation_de": old["v75_line_translation_de"], "v76_word_delta": 0,
            "v76_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v76_line_translation_de"] == old["v75_line_translation_de"] for new, old in zip(line_overlay, lines))
    assert sum(row["v76_new_result_edge_ids"] != "NONE" for row in line_overlay) == 2
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{
        **old, "v76_selected_gloss_de": old["v75_selected_gloss_de"],
        "v76_byte_identical": 1, "v76_relation_change": "NONE", "v76_status": STATUS,
    } for old in spans]
    assert all(new["v76_selected_gloss_de"] == old["v75_selected_gloss_de"] for new, old in zip(span_overlay, spans))
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT703 — V76 all-action result reader", "", f"Status: `{STATUS}`", "",
        "## Was die zwei neuen Arbeitslesarten konkret sagen", "",
        f"> **C013 / f26r.2:** {M009_READING}", "",
        f"> **C014 / f115r.23:** {M010_READING}", "",
        "C013 macht den schon geschriebenen Zustandsvermerk #5 zum Ergebnis von #4; C011 bleibt die "
        "separate Fortführung desselben #4-Ausgangs zu #6. Es gibt ausdrücklich keinen #5→#6-Pfeil. "
        "C014 endet an #4; die neue Aktion #5 bleibt außerhalb.", "",
        "## Alle sieben unmittelbaren Fertigzustände", "",
        "| Fall | Stelle | Aktion → geschriebener Zustand | Arbeitsentscheidung | stärkste Gegenlesung |",
        "|---|---|---|---|---|",
    ]
    for row in candidate_rows:
        reader.append(
            f"| {row['candidate_id']} | `{row['locus']}` | #{row['action_ordinal']} `{row['action_surface']}` → "
            f"#{row['result_ordinal']} `{row['result_surface']}` | {row['decision']} | {row['strongest_rival_de']} |"
        )
    reader.extend([
        "", "## Vollständigkeit", "",
        "Der Zensus umfasst **alle 83 Aktionsklauseln**. Unmittelbar rechts folgen **60 Nominalblöcke, "
        "15 Aktionsklauseln und 8 Zeilenenden**. Genau **7** erste rechte Einträge sind bereits als "
        "`HIGH`-Fertigzustand typisiert: ein bestehender lokaler Edge (C012), zwei neue lokale "
        "Arbeitsedges (C013/C014) und vier offen gehaltene Nicht-Edges. Kein attraktiveres späteres Wort "
        "wurde übergangen.", "",
        "Der kumulative Leser besitzt jetzt **14 Kanten in 10 Komponenten**. Die 479 Wortglossen, "
        "51 Zeilenübersetzungen und 3 gebundenen Spannen bleiben unverändert; hinzu kommt keine neue "
        "Wortbedeutung und keine Seite.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")

    ARTIFACT_README.write_text(
        "# GDT703 artifacts\n\n"
        "- `V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv`: every complete action clause and its first immediate right item.\n"
        "- `V76_7_FINISHED_RESULT_FIRSTS.tsv`: complete seven-case finished-state contrast with open rivals.\n"
        "- `V76_2_NEW_LOCAL_RESULT_EDGES.tsv`: C013 and C014 only.\n"
        "- `V76_14_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V76_10_CONNECTED_COMPONENTS.tsv`, and "
        "`V76_29_COMPONENT_POSITION_ROLES.tsv`: cumulative graph.\n"
        "- `V76_COMPONENT_TOPOLOGY_CENSUS.tsv`: graph, position, support and result accounting.\n"
        "- `V76_GDT388_EDGE_PACKET.tsv` and `V76_GDT388_EDGE_INTAKE.json`: explicit invalid/not-score-ready intake.\n"
        "- `V76_479_TOKEN_RELATION_OVERLAY.tsv`, `V76_51_LINE_RELATION_OVERLAY.tsv`, and "
        "`V76_3_BOUND_SPAN_FREEZE.tsv`: unchanged V75 words with separate V76 relation metadata.\n"
        "- `GDT703_V76_ALL_ACTION_RESULT_READER.md`: concrete working readings and the seven-case table.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    graph_node_keys = {
        (str(row["locus"]), ordinal)
        for row in membership_rows
        for ordinal in str(row["edge_node_ordinals"]).split("|")
    }
    assert len(graph_node_keys) == 27
    assert sum(len(str(row["edge_node_ordinals"]).split("|")) for row in membership_rows) == 31
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 28
    assert sum(int(row["render_window_token_count"]) for row in components) == 29
    assert json.loads(G388.read_text(encoding="utf-8"))["acquisition"]["scoring_authorized"] is False

    generated = [
        CENSUS_OUT, CANDIDATE_OUT, EDGE_OUT, MEMBERSHIP_OUT, COMPONENTS_OUT, POSITIONS_OUT,
        TOPOLOGY_OUT, PACKET_OUT, INTAKE_OUT, TOKENS_OUT, LINES_OUT, SPANS_OUT, READER_OUT,
        ARTIFACT_README,
    ]
    inputs = [
        G388, G687, G695, G700, G702_RESULT, G702_MEMBERSHIP, G702_COMPONENTS,
        G702_POSITIONS, G702_TOKENS, G702_LINES, G702_SPANS, SPEC, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "source_clauses": 175, "action_clauses": 83, "nominal_clauses": 92,
            "bound_spans": 3, "action_right_contexts": 83,
            "nominal_right_contexts": 60, "following_action_contexts": 15,
            "end_of_line_right_contexts": 8, "finished_result_firsts": 7,
            "inherited_local_reads": 1, "new_local_reads": 2, "open_nonedge_reads": 4,
            "relation_edges_before": 12, "relation_edges_after": 14, "new_edges": 2,
            "connected_components": 10, "edge_nodes": 27, "edge_node_incidences": 31,
            "minimal_hull_positions": 28, "render_positions": 29, "shared_edge_nodes": 4,
            "hull_only_positions": 1, "render_only_structural_positions": 1,
            "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "retained_edge": "C012", "new_edge_ids": ["C013", "C014"],
            "c013": "f26r.2#4→f26r.2#5", "c014": "f115r.23#3→f115r.23#4",
            "c013_component": "M009", "c014_component": "M010",
            "written_result_state_targets": 3, "written_final_material_or_preparation_results": 2,
            "written_intermediate_state_checkpoints": 1, "new_participant_identities": 3,
            "changed_existing_edges": 0, "later_token_skip": False,
            "adjacency_default": False, "action_surface_output_default": False,
            "result_surface_left_action_default": False, "new_word_meanings": 0,
        },
        "graph": {
            "component_partition": [
                ["C009"], ["C001", "C012"], ["C002"], ["C003"], ["C004", "C008"],
                ["C005"], ["C006", "C007"], ["C010"], ["C011", "C013"], ["C014"],
            ],
            "shared_nodes": ["f105v.1#4", "f26r.2#4", "f80v.35#3", "f86v6.25#4"],
            "sole_hull_only_position": "f86v5.24#2",
            "sole_render_only_structural_position": "f26r.2#7",
        },
        "gdt388": expected_intake,
        "freeze": {
            "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0,
            "changed_word_meanings": 0, "content_word_additions": 0,
            "content_word_deletions": 0, "content_word_reorders": 0,
        },
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated},
        "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": STATUS, "actions": 83, "right_context_split": "60/15/8",
        "finished_result_firsts": 7, "new_edges": ["C013", "C014"],
        "edges": 14, "components": 10, "edge_nodes": 27,
        "render_positions": 29, "new_word_meanings": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
