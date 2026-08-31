#!/usr/bin/env python3
"""Build GDT705's complete immediate ACTION-to-NOMINAL result audit and V78 graph."""

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
EXP = ROOT / "experiments/yolo/gdt705_v78_complete_action_nominal_result_census"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V78_60_ACTION_NOMINAL_RESULTS__2_NEW_C017_C018__5_NEW_HOLDS__"
    "20_OPEN_26_CONTROLS__17_EDGES_12_COMPONENTS__ZERO_WORD_DELTA"
)
QUESTION = (
    "When all sixty immediate ACTION-to-NOMINAL successors are compared by operation, degree, "
    "material and completion agreement, do the cases omitted by GDT703's narrow seven-case gate "
    "support concrete occurrence-bound written-result readings?"
)
CLAIM = (
    "V78 completes the first-token classification of all 60 immediate ACTION-to-NOMINAL transitions. "
    "A057 binds f80r.17 sheky to the written soaked-and-heated drug state shkeol as C017; A056 binds "
    "f7r.2 dold to the written measured finished dry portion dchey as lower-tier C018. A066, A072, "
    "A046, A006 and A043 remain attractive open candidates. The other two sheky occurrences and the weaker "
    "A043-to-dchey pairing block any portable surface or target default. These are replaceable "
    "occurrence readings, not recovered plaintext or historical decipherment."
)
NEXT_GAP = (
    "Audit later explicit result candidates only for actions still result-unwritten after this "
    "complete immediate census. Start with the ranked delayed cases already identified, retain "
    "A066/A072/A046/A006/A043 as open comparators, open no page and change no word meaning."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G703 = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census/artifacts"
OLD_ACTION_CENSUS = G703 / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv"
OLD_FINISHED = G703 / "V76_7_FINISHED_RESULT_FIRSTS.tsv"
G704 = ROOT / "experiments/yolo/gdt704_v77_repeated_written_material_continuation/artifacts"
OLD_RESULT = G704 / "RESULT.json"
OLD_MEMBERSHIP = G704 / "V77_15_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_COMPONENTS = G704 / "V77_10_CONNECTED_COMPONENTS.tsv"
OLD_POSITIONS = G704 / "V77_30_COMPONENT_POSITION_ROLES.tsv"
OLD_TOKENS = G704 / "V77_479_TOKEN_RELATION_OVERLAY.tsv"
OLD_LINES = G704 / "V77_51_LINE_RELATION_OVERLAY.tsv"
OLD_SPANS = G704 / "V77_3_BOUND_SPAN_FREEZE.tsv"
DECISION_SPEC = SRC / "V78_60_ACTION_NOMINAL_DECISION_SPECS.tsv"
LEADING_SPEC = SRC / "V78_7_LEADING_RESULT_CASE_SPECS.tsv"

CENSUS_OUT = ART / "V78_60_ACTION_NOMINAL_RESULT_CENSUS.tsv"
LEADING_OUT = ART / "V78_7_LEADING_RESULT_CANDIDATES.tsv"
SHEKY_OUT = ART / "V78_3_SHEKY_OCCURRENCE_CONTRAST.tsv"
DCHEY_OUT = ART / "V78_2_DCHEY_TARGET_CONTRAST.tsv"
EDGE_OUT = ART / "V78_2_NEW_LOCAL_RESULT_EDGES.tsv"
MEMBERSHIP_OUT = ART / "V78_17_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V78_12_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V78_34_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V78_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V78_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V78_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V78_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V78_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V78_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT705_V78_COMPLETE_RESULT_READER.md"
RESULT_OUT = ART / "RESULT.json"

DECISION_SPEC_FIELDS = [
    "action_case_id", "operation_agreement", "degree_agreement", "material_agreement",
    "completion_agreement", "result_role", "competing_or_missing_patient", "decision",
    "decision_reason_de", "portable_default",
]
LEADING_SPEC_FIELDS = [
    "candidate_id", "rank", "action_case_id", "edge_id", "component_id", "support_tier",
    "relation_class", "working_reading_de", "strongest_rival_de", "boundary_note_de",
    "portability",
]
CENSUS_FIELDS = [
    "action_case_id", "page", "locus", "action_clause_id", "action_clause_start",
    "action_clause_end", "action_clause_surfaces", "action_ordinal", "action_surface",
    "action_gloss_de", "right_clause_id", "right_clause_start", "right_clause_end",
    "right_first_ordinal", "right_first_surface", "right_first_gloss_de", "right_dispatch",
    "right_confidence", "prior_candidate_id", "prior_candidate_decision",
    *DECISION_SPEC_FIELDS[1:], "full_clause_then_first_item_exact", "word_delta", "status",
]
LEADING_FIELDS = [
    *LEADING_SPEC_FIELDS, "page", "locus", "action_clause_id", "action_clause_start",
    "action_clause_end", "action_clause_surfaces", "action_ordinal", "action_surface",
    "action_gloss_de", "target_clause_id", "target_ordinal", "target_surface",
    "target_gloss_de", "target_dispatch", "target_confidence", "operation_agreement",
    "degree_agreement", "material_agreement", "completion_agreement", "result_role",
    "competing_or_missing_patient", "decision", "decision_reason_de", "word_delta", "status",
]
CONTRAST_FIELDS = [
    "contrast_id", "action_case_id", "page", "locus", "action_clause_id",
    "action_clause_start", "action_clause_end", "action_surface", "action_gloss_de",
    "right_clause_type", "right_clause_id", "right_first_ordinal", "right_first_surface",
    "right_first_gloss_de", "contrast_role", "decision", "contrast_note_de", "word_delta",
    "status",
]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "source_clause_ordinals", "source_action_ordinal", "source_action_surface",
    "source_action_gloss_de", "written_result_ordinal", "written_result_surface",
    "written_result_gloss_de", "operation_agreement", "degree_agreement",
    "material_agreement", "completion_agreement", "admission_basis",
    "working_microrecord_de", "strongest_rival_de", "boundary_note_de", "portability",
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
    "v78_action_nominal_case_ids", "v78_action_nominal_roles", "v78_result_decisions",
    "v78_leading_candidate_ids", "v78_sheky_contrast_ids", "v78_dchey_contrast_ids",
    "v78_component_id", "v78_component_position", "v78_component_role",
    "v78_component_edge_ids", "v78_component_membership_class",
    "v78_component_microrecord_de", "v78_new_result_edge_ids", "v78_token_gloss_de",
    "v78_word_delta", "v78_status",
]
LINE_EXTRA = [
    "v78_action_nominal_case_ids", "v78_result_decisions", "v78_leading_candidate_ids",
    "v78_sheky_contrast_ids", "v78_dchey_contrast_ids", "v78_component_ids",
    "v78_edge_ids", "v78_component_topologies", "v78_component_microrecords_de",
    "v78_new_result_edge_ids", "v78_working_relation_reading_de",
    "v78_line_translation_de", "v78_word_delta", "v78_status",
]
SPAN_EXTRA = ["v78_selected_gloss_de", "v78_byte_identical", "v78_relation_change", "v78_status"]

C017_READING = (
    "Bis zur Mittelstufe einweichen, erhitzen und abschließen. Ergebnis: eingeweichter "
    "Drogenstoff, bis Mittelstufe erhitzt."
)
C018_READING = (
    "Drogenstoff abmessen und abschließen. Ergebnis: fertige abgemessene "
    "Mittelstufen-Trockenportion."
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


def pipe(values: Sequence[str]) -> str:
    clean = [str(value) for value in values if value and value != "NONE"]
    return "|".join(dict.fromkeys(clean)) if clean else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(DECISION_SPEC)
    leading_fields, leading_specs = read_tsv(LEADING_SPEC)
    assert spec_fields == DECISION_SPEC_FIELDS and len(specs) == 60
    assert leading_fields == LEADING_SPEC_FIELDS and len(leading_specs) == 7
    assert len({row["action_case_id"] for row in specs}) == 60
    assert all(row["portable_default"] == "NO" for row in specs)
    expected_decisions = {
        "ADMIT_NEW": 2, "HOLD_NEW": 5, "REPLAY_ADMITTED": 3,
        "RETAIN_PRIOR_HOLD": 4, "OPEN_PARTIAL": 20, "CONTROL_CONFLICT": 26,
    }
    assert Counter(row["decision"] for row in specs) == expected_decisions
    assert [row["candidate_id"] for row in leading_specs] == [f"R{i:03d}" for i in range(1, 8)]
    assert [int(row["rank"]) for row in leading_specs] == list(range(1, 8))
    assert [row["action_case_id"] for row in leading_specs] == ["A057", "A056", "A066", "A072", "A046", "A006", "A043"]
    assert {row["edge_id"] for row in leading_specs if row["edge_id"] != "NONE"} == {"C017", "C018"}

    _, clauses = read_tsv(G695)
    _, old_action_census = read_tsv(OLD_ACTION_CENSUS)
    _, old_finished = read_tsv(OLD_FINISHED)
    membership_fields, old_memberships = read_tsv(OLD_MEMBERSHIP)
    component_fields, old_components = read_tsv(OLD_COMPONENTS)
    position_fields, old_positions = read_tsv(OLD_POSITIONS)
    token_fields, old_tokens = read_tsv(OLD_TOKENS)
    line_fields, old_lines = read_tsv(OLD_LINES)
    span_fields, old_spans = read_tsv(OLD_SPANS)
    old_result = json.loads(OLD_RESULT.read_text(encoding="utf-8"))
    assert len(clauses) == 175 and len(old_action_census) == 83 and len(old_finished) == 7
    assert len(old_memberships) == 15 and len(old_components) == 10 and len(old_positions) == 30
    assert len(old_tokens) == 479 and len(old_lines) == 51 and len(old_spans) == 3
    assert old_result["basis"]["relation_edges_after"] == 15
    assert old_result["basis"]["connected_components"] == 10
    assert all(not row["page"].startswith("f84") for row in old_tokens)

    nominal_inputs = [row for row in old_action_census if row["right_clause_type"] == "NOMINAL_BLOCK"]
    assert len(nominal_inputs) == 60
    assert [row["action_case_id"] for row in nominal_inputs] == [row["action_case_id"] for row in specs]
    spec_index = {row["action_case_id"]: row for row in specs}
    prior_finished = {row["action_case_id"]: row for row in old_finished}
    assert set(prior_finished) == {"A005", "A007", "A009", "A024", "A026", "A033", "A053"}

    census_rows: list[dict[str, object]] = []
    for old in nominal_inputs:
        spec = spec_index[old["action_case_id"]]
        prior = prior_finished.get(old["action_case_id"])
        census_rows.append({
            "action_case_id": old["action_case_id"], "page": old["page"], "locus": old["locus"],
            "action_clause_id": old["action_clause_id"], "action_clause_start": old["action_clause_start"],
            "action_clause_end": old["action_clause_end"], "action_clause_surfaces": old["action_clause_surfaces"],
            "action_ordinal": old["action_ordinal"], "action_surface": old["action_surface"],
            "action_gloss_de": old["action_gloss_de"], "right_clause_id": old["right_clause_id"],
            "right_clause_start": old["right_clause_start"], "right_clause_end": old["right_clause_end"],
            "right_first_ordinal": old["right_first_ordinal"], "right_first_surface": old["right_first_surface"],
            "right_first_gloss_de": old["right_first_gloss_de"], "right_dispatch": old["right_dispatch"],
            "right_confidence": old["right_confidence"],
            "prior_candidate_id": prior["candidate_id"] if prior else "NONE",
            "prior_candidate_decision": prior["decision"] if prior else "OUTSIDE_V76_SEVEN_CASE_GATE",
            **{field: spec[field] for field in DECISION_SPEC_FIELDS[1:]},
            "full_clause_then_first_item_exact": 1, "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["decision"] for row in census_rows) == expected_decisions
    write_tsv(CENSUS_OUT, census_rows, CENSUS_FIELDS)
    census_index = {str(row["action_case_id"]): row for row in census_rows}

    leading_rows: list[dict[str, object]] = []
    for lead in leading_specs:
        row = census_index[lead["action_case_id"]]
        leading_rows.append({
            **lead, "page": row["page"], "locus": row["locus"],
            "action_clause_id": row["action_clause_id"], "action_clause_start": row["action_clause_start"],
            "action_clause_end": row["action_clause_end"], "action_clause_surfaces": row["action_clause_surfaces"],
            "action_ordinal": row["action_ordinal"], "action_surface": row["action_surface"],
            "action_gloss_de": row["action_gloss_de"], "target_clause_id": row["right_clause_id"],
            "target_ordinal": row["right_first_ordinal"], "target_surface": row["right_first_surface"],
            "target_gloss_de": row["right_first_gloss_de"], "target_dispatch": row["right_dispatch"],
            "target_confidence": row["right_confidence"], "operation_agreement": row["operation_agreement"],
            "degree_agreement": row["degree_agreement"], "material_agreement": row["material_agreement"],
            "completion_agreement": row["completion_agreement"], "result_role": row["result_role"],
            "competing_or_missing_patient": row["competing_or_missing_patient"],
            "decision": row["decision"], "decision_reason_de": row["decision_reason_de"],
            "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["decision"] for row in leading_rows) == {"ADMIT_NEW": 2, "HOLD_NEW": 5}
    write_tsv(LEADING_OUT, leading_rows, LEADING_FIELDS)

    sheky_roles = {
        "A057": ("S001", "ADMITTED_EXACT_OPERATION_STAGE_RESULT", "ADMIT_NEW_C017",
                 "Einweichen und Erhitzen sowie Mittelstufe werden im ersten rechten Zustand gespiegelt."),
        "A058": ("S002", "FOLLOWED_BY_ACTION_NOT_NOMINAL_RESULT", "CONTROL_NO_RESULT_LABEL",
                 "Dasselbe sheky wird sofort von einer Trocknen-und-Kühlen-Handlung fortgesetzt."),
        "A060": ("S003", "CONFLICTING_NOMINAL_SUCCESSOR", "CONTROL_CONFLICT",
                 "Dasselbe sheky verliert Einweichen und Mittelstufe; rechts steht heißer Rohstoff am Gradanfang."),
    }
    old_action_index = {row["action_case_id"]: row for row in old_action_census}
    sheky_rows: list[dict[str, object]] = []
    for case_id in ("A057", "A058", "A060"):
        old = old_action_index[case_id]
        contrast_id, role, decision, note = sheky_roles[case_id]
        assert old["action_surface"] == "sheky"
        sheky_rows.append({
            "contrast_id": contrast_id, "action_case_id": case_id, "page": old["page"],
            "locus": old["locus"], "action_clause_id": old["action_clause_id"],
            "action_clause_start": old["action_clause_start"], "action_clause_end": old["action_clause_end"],
            "action_surface": old["action_surface"], "action_gloss_de": old["action_gloss_de"],
            "right_clause_type": old["right_clause_type"], "right_clause_id": old["right_clause_id"],
            "right_first_ordinal": old["right_first_ordinal"], "right_first_surface": old["right_first_surface"],
            "right_first_gloss_de": old["right_first_gloss_de"], "contrast_role": role,
            "decision": decision, "contrast_note_de": note, "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["right_clause_type"] for row in sheky_rows) == {"NOMINAL_BLOCK": 2, "ACTION_CLAUSE": 1}
    write_tsv(SHEKY_OUT, sheky_rows, CONTRAST_FIELDS)

    dchey_rows: list[dict[str, object]] = []
    for contrast_id, case_id, role, note in [
        ("D001", "A056", "ADMITTED_MEASURE_COMPLETION_MIRROR",
         "Dold liefert Abmessen und Abschluss; dchey schreibt beides als abgemessene fertige Portion."),
        ("D002", "A043", "HELD_DRY_RELATED_WITH_MAJOR_ADDITIONS",
         "Ykcho liefert Trockenmischung und Bereiten, aber nicht Abmessen, Portion oder Mittelstufe."),
    ]:
        row = census_index[case_id]
        assert row["right_first_surface"] == "dchey"
        dchey_rows.append({
            "contrast_id": contrast_id, "action_case_id": case_id, "page": row["page"],
            "locus": row["locus"], "action_clause_id": row["action_clause_id"],
            "action_clause_start": row["action_clause_start"], "action_clause_end": row["action_clause_end"],
            "action_surface": row["action_surface"], "action_gloss_de": row["action_gloss_de"],
            "right_clause_type": "NOMINAL_BLOCK", "right_clause_id": row["right_clause_id"],
            "right_first_ordinal": row["right_first_ordinal"], "right_first_surface": row["right_first_surface"],
            "right_first_gloss_de": row["right_first_gloss_de"], "contrast_role": role,
            "decision": row["decision"], "contrast_note_de": note, "word_delta": 0, "status": STATUS,
        })
    assert {row["decision"] for row in dchey_rows} == {"ADMIT_NEW", "HOLD_NEW"}
    write_tsv(DCHEY_OUT, dchey_rows, CONTRAST_FIELDS)

    new_edges: list[dict[str, object]] = []
    for lead in leading_rows:
        if lead["decision"] != "ADMIT_NEW":
            continue
        forbidden = (
            "Kein allgemeines SHEKY-Ergebnis, keine Bindung an #5 und keine Übertragung auf A058 oder A060."
            if lead["edge_id"] == "C017" else
            "Kein allgemeines DCHEY-Ziel, keine Bindung an #7-9 und keine Übertragung auf A043."
        )
        new_edges.append({
            "edge_id": lead["edge_id"], "component_id": lead["component_id"],
            "locus": lead["locus"], "support_tier": lead["support_tier"],
            "relation_class": lead["relation_class"],
            "source_clause_ordinals": (
                lead["action_clause_start"] if lead["action_clause_start"] == lead["action_clause_end"]
                else f"{lead['action_clause_start']}|{lead['action_clause_end']}"
            ),
            "source_action_ordinal": lead["action_ordinal"], "source_action_surface": lead["action_surface"],
            "source_action_gloss_de": lead["action_gloss_de"],
            "written_result_ordinal": lead["target_ordinal"], "written_result_surface": lead["target_surface"],
            "written_result_gloss_de": lead["target_gloss_de"],
            "operation_agreement": lead["operation_agreement"], "degree_agreement": lead["degree_agreement"],
            "material_agreement": lead["material_agreement"],
            "completion_agreement": lead["completion_agreement"],
            "admission_basis": "MEASURE_PLUS_COMPLETION_EQUIVALENCE" if lead["edge_id"] == "C018" else "TWO_OPERATION_PLUS_EXACT_STAGE_MIRROR",
            "working_microrecord_de": lead["working_reading_de"],
            "strongest_rival_de": lead["strongest_rival_de"], "boundary_note_de": lead["boundary_note_de"],
            "portability": lead["portability"], "gdt388_score_ready": 0,
            "forbidden_inference": forbidden, "edge_delta": 1, "word_delta": 0, "status": STATUS,
        })
    new_edges.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert [(row["edge_id"], row["locus"]) for row in new_edges] == [("C017", "f80r.17"), ("C018", "f7r.2")]
    write_tsv(EDGE_OUT, new_edges, EDGE_FIELDS)

    membership_out_fields = [*membership_fields[:-1], "v78_change", "status"]
    memberships: list[dict[str, object]] = [
        {**old, "v78_change": "NONE", "status": STATUS} for old in old_memberships
    ]
    memberships.extend([
        {
            "edge_id": "C017", "component_id": "M011", "locus": "f80r.17",
            "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_WRITTEN_PROCESSED_MATERIAL_STATE",
            "edge_node_ordinals": "3|4", "source_ordinals": "3", "target_ordinal": "4",
            "target_role": "WRITTEN_PROCESSED_MATERIAL_STATE", "component_edge_count": 1,
            "component_topology": "ACTION_WRITTEN_PROCESSED_MATERIAL_PAIR",
            "shared_edge_node_ordinals": "NONE", "origin": "GDT705_NEW_OCCURRENCE_BOUND",
            "v75_change": "NONE", "v76_change": "NONE", "v77_change": "NONE",
            "v78_change": "NEW_EDGE", "status": STATUS,
        },
        {
            "edge_id": "C018", "component_id": "M012", "locus": "f7r.2",
            "support_tier": "B_LOW_WORKING_LOCAL", "relation_class": "ACTION_TO_WRITTEN_FINISHED_PORTION_STATE",
            "edge_node_ordinals": "5|6", "source_ordinals": "5", "target_ordinal": "6",
            "target_role": "WRITTEN_FINISHED_PORTION_STATE", "component_edge_count": 1,
            "component_topology": "ACTION_WRITTEN_FINISHED_PORTION_PAIR",
            "shared_edge_node_ordinals": "NONE", "origin": "GDT705_NEW_OCCURRENCE_BOUND",
            "v75_change": "NONE", "v76_change": "NONE", "v77_change": "NONE",
            "v78_change": "NEW_EDGE", "status": STATUS,
        },
    ])
    memberships.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert [row["edge_id"] for row in memberships] == [f"C{i:03d}" for i in range(1, 19) if i != 16]
    write_tsv(MEMBERSHIP_OUT, memberships, membership_out_fields)

    component_out_fields = [*component_fields[:-1], "v78_edge_delta", "v78_change", "status"]
    components: list[dict[str, object]] = [
        {**old, "v78_edge_delta": 0, "v78_change": "NONE", "status": STATUS} for old in old_components
    ]
    components.extend([
        {
            "component_id": "M011", "locus": "f80r.17", "edge_ids": "C017", "edge_count": 1,
            "edge_node_ordinals": "3|4", "edge_node_count": 2, "shared_edge_node_ordinals": "NONE",
            "edge_hull_start": 3, "edge_hull_end": 4, "edge_hull_position_count": 2,
            "hull_only_ordinals": "NONE", "render_window_start": 3, "render_window_end": 4,
            "render_only_structural_ordinals": "NONE", "render_window_token_count": 2,
            "topology": "ACTION_WRITTEN_PROCESSED_MATERIAL_PAIR", "action_ordinals": "3",
            "support_profile": "B_ONLY", "expected_surfaces": "sheky|shkeol",
            "observed_surfaces": "sheky|shkeol", "microrecord_de": C017_READING,
            "component_basis": "Einweichen, Erhitzen und Mittelstufe werden unmittelbar im geschriebenen Drogenstoffzustand gespiegelt; die Materialidentität bleibt wegen #2 offen.",
            "boundary_note_de": "Nur #4 ist Ziel; #5 qokar ist ein ungebundener späterer Registereintrag, A058 und A060 bleiben außerhalb.",
            "forbidden_inference": "Kein allgemeines SHEKY-Ergebnis und keine weitere Kante aus bloßer Oberflächenwiederholung.",
            "final_result_status": "WRITTEN_PROCESSED_MATERIAL_RESULT:C017",
            "origin": "GDT705_NEW_EXPLORATORY", "edge_delta": 1, "word_delta": 0,
            "v76_change": "NONE", "v77_edge_delta": 0, "v77_change": "NONE",
            "v78_edge_delta": 1, "v78_change": "NEW_COMPONENT", "status": STATUS,
        },
        {
            "component_id": "M012", "locus": "f7r.2", "edge_ids": "C018", "edge_count": 1,
            "edge_node_ordinals": "5|6", "edge_node_count": 2, "shared_edge_node_ordinals": "NONE",
            "edge_hull_start": 5, "edge_hull_end": 6, "edge_hull_position_count": 2,
            "hull_only_ordinals": "NONE", "render_window_start": 5, "render_window_end": 6,
            "render_only_structural_ordinals": "NONE", "render_window_token_count": 2,
            "topology": "ACTION_WRITTEN_FINISHED_PORTION_PAIR", "action_ordinals": "5",
            "support_profile": "B_LOW_ONLY", "expected_surfaces": "dold|dchey",
            "observed_surfaces": "dold|dchey", "microrecord_de": C018_READING,
            "component_basis": "Abmessen wird unmittelbar als abgemessen ausgeschrieben; Abschließen entspricht semantisch fertig, während die Materialidentität ungeschrieben bleibt.",
            "boundary_note_de": "Nur #6 ist Ziel; #7-9 sind ungebundene spätere Registereinträge.",
            "forbidden_inference": "Kein allgemeines DCHEY-Ziel und keine Übertragung auf A043 oder andere linke Handlungen.",
            "final_result_status": "WRITTEN_FINISHED_PORTION_RESULT:C018",
            "origin": "GDT705_NEW_EXPLORATORY", "edge_delta": 1, "word_delta": 0,
            "v76_change": "NONE", "v77_edge_delta": 0, "v77_change": "NONE",
            "v78_edge_delta": 1, "v78_change": "NEW_COMPONENT", "status": STATUS,
        },
    ])
    components.sort(key=lambda row: int(str(row["component_id"])[1:]))
    assert len(components) == 12
    write_tsv(COMPONENTS_OUT, components, component_out_fields)

    token_index = {(row["locus"], row["token_ordinal"]): row for row in old_tokens}
    position_out_fields = [*position_fields[:-1], "v78_change", "status"]
    positions: list[dict[str, object]] = [
        {**old, "v78_change": "NONE", "status": STATUS} for old in old_positions
    ]
    new_position_specs = [
        ("M011", "f80r.17", 3, 1, "SOURCE_ACTION:C017", "C017", "NONE", "C017_WRITTEN_RESULT_SOURCE", C017_READING),
        ("M011", "f80r.17", 4, 2, "WRITTEN_PROCESSED_MATERIAL_STATE:C017", "NONE", "C017", "WRITTEN_C017_PROCESSED_MATERIAL", C017_READING),
        ("M012", "f7r.2", 5, 1, "SOURCE_ACTION:C018", "C018", "NONE", "C018_WRITTEN_RESULT_SOURCE", C018_READING),
        ("M012", "f7r.2", 6, 2, "WRITTEN_FINISHED_PORTION_STATE:C018", "NONE", "C018", "WRITTEN_C018_FINISHED_PORTION", C018_READING),
    ]
    for component_id, locus, ordinal, render_pos, role, source_ids, target_ids, output_role, reading in new_position_specs:
        token = token_index[(locus, str(ordinal))]
        edge_id = "C017" if component_id == "M011" else "C018"
        positions.append({
            "page": token["page"], "locus": locus, "token_ordinal": ordinal,
            "surface": token["surface"], "token_gloss_de": token["v77_token_gloss_de"],
            "component_id": component_id, "render_position": render_pos, "render_size": 2,
            "component_role": role, "edge_ids": edge_id, "source_edge_ids": source_ids,
            "reference_edge_ids": "NONE", "target_edge_ids": target_ids,
            "membership_class": "EDGE_NODE", "is_edge_node": 1, "is_hull_only": 0,
            "is_render_only_structural": 0, "is_action_target": 0, "is_shared_edge_node": 0,
            "action_output_role": output_role, "component_microrecord_de": reading,
            "word_delta": 0, "v76_change": "NONE", "v77_change": "NONE",
            "v78_change": f"NEW_{edge_id}_EDGE_NODE", "status": STATUS,
        })
    positions.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(positions) == 34 and len({(row["locus"], str(row["token_ordinal"])) for row in positions}) == 34
    assert Counter(row["membership_class"] for row in positions) == {"EDGE_NODE": 32, "HULL_ONLY": 2}
    assert sum(int(row["is_shared_edge_node"]) for row in positions) == 5
    write_tsv(POSITIONS_OUT, positions, position_out_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_rows: list[dict[str, object]] = []
    for dimension, groups, note in (
        ("TOPOLOGY", topology_groups, "exact occurrence-component topology"),
        ("SUPPORT_PROFILE", support_groups, "local tiers are not portable defaults"),
    ):
        for value in sorted(groups):
            topology_rows.append({
                "dimension": dimension, "value": value, "count": len(groups[value]),
                "component_ids": pipe(groups[value]), "note": note, "status": STATUS,
            })
    all_components = pipe([f"M{i:03d}" for i in range(1, 13)])
    topology_rows.extend([
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 32, "component_ids": all_components, "note": "unique occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 2, "component_ids": "M008|M009", "note": "f86v5.24#2 and structural f26r.2#7", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 0, "component_ids": "NONE", "note": "no render-only structural position", "status": STATUS},
        {"dimension": "STRUCTURAL_ROLE", "value": "CLAUSE_CLOSURE_NONNODE", "count": 1, "component_ids": "M009", "note": "f26r.2#7 remains the only graph structural closure", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "EDGE_INCIDENCE", "count": 37, "component_ids": all_components, "note": "sum of edge endpoint incidences", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "MINIMAL_HULL_POSITION", "count": 34, "component_ids": all_components, "note": "sum of component hull sizes", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "RENDER_POSITION", "count": 34, "component_ids": all_components, "note": "sum of render-window sizes", "status": STATUS},
        {"dimension": "RESULT_DECISION", "value": "ADMIT_NEW", "count": 2, "component_ids": "M011|M012", "note": "A057 and A056 only", "status": STATUS},
        {"dimension": "RESULT_DECISION", "value": "HOLD_NEW", "count": 5, "component_ids": "NONE", "note": "A066 A072 A046 A006 A043", "status": STATUS},
        {"dimension": "RESULT_DECISION", "value": "OPEN_PARTIAL", "count": 20, "component_ids": "NONE", "note": "partial argument quantity material or state compatibility", "status": STATUS},
        {"dimension": "RESULT_DECISION", "value": "CONTROL_CONFLICT", "count": 26, "component_ids": "NONE", "note": "explicit material state operation or degree mismatch", "status": STATUS},
        {"dimension": "SURFACE_CONTROL", "value": "SHEKY_OCCURRENCES", "count": 3, "component_ids": "M011", "note": "one admitted result one following action one conflicting result", "status": STATUS},
        {"dimension": "TARGET_CONTROL", "value": "DCHEY_HIGH_TARGETS", "count": 2, "component_ids": "M012", "note": "A056 admitted A043 held", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packets = [
        {
            "edge_id": "C017", "batch_id": "GDT705_V78", "page": "f80r", "physical_folio": "f80",
            "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_3_SHEKY_ACTION",
            "pivot_locus": "f80r.17@3", "target_visual_id": "TOKEN_4_SHKEOL_RESULT",
            "target_locus": "f80r.17@4", "relation_type": "WORKSHOP_ACTION_TO_WRITTEN_PROCESSED_MATERIAL_STATE",
            "direction_basis": "COMPLETE_ACTION_THEN_IMMEDIATE_NOMINAL_FIRST_ITEM",
            "ownership_basis": "SOAK_HEAT_AND_MIDDLE_STAGE_MIRROR",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT705",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT705_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "B_WORKING_LOCAL", "ambiguity_state": "WORKSHOP_ONLY",
            "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
        },
        {
            "edge_id": "C018", "batch_id": "GDT705_V78", "page": "f7r", "physical_folio": "f7",
            "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_5_DOLD_ACTION",
            "pivot_locus": "f7r.2@5", "target_visual_id": "TOKEN_6_DCHEY_RESULT",
            "target_locus": "f7r.2@6", "relation_type": "WORKSHOP_ACTION_TO_WRITTEN_FINISHED_PORTION_STATE",
            "direction_basis": "COMPLETE_ACTION_THEN_IMMEDIATE_NOMINAL_FIRST_ITEM",
            "ownership_basis": "MEASURE_AND_COMPLETION_MIRROR",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT705",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT705_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
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
        "errors": ["edge row 2: formal access is not sealed", "edge row 3: formal access is not sealed"],
    }
    assert intake_run.returncode == 1 and not intake_run.stderr
    assert json.loads(intake_run.stdout) == expected_intake
    INTAKE_OUT.write_text(json.dumps(expected_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    case_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    case_roles: dict[tuple[str, int], set[str]] = defaultdict(set)
    decisions_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    leading_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in census_rows:
        locus = str(row["locus"])
        for ordinal in range(int(row["action_clause_start"]), int(row["action_clause_end"]) + 1):
            key = (locus, ordinal)
            case_ids[key].add(str(row["action_case_id"])); case_roles[key].add("ACTION_CLAUSE")
            decisions_by_pos[key].add(str(row["decision"]))
        key = (locus, int(row["right_first_ordinal"]))
        case_ids[key].add(str(row["action_case_id"])); case_roles[key].add("FIRST_NOMINAL_ITEM")
        decisions_by_pos[key].add(str(row["decision"]))
    for row in leading_rows:
        for ordinal in range(int(row["action_clause_start"]), int(row["action_clause_end"]) + 1):
            leading_by_pos[(str(row["locus"]), ordinal)].add(str(row["candidate_id"]))
        leading_by_pos[(str(row["locus"]), int(row["target_ordinal"]))].add(str(row["candidate_id"]))
    sheky_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    dchey_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    for rows, mapping in ((sheky_rows, sheky_by_pos), (dchey_rows, dchey_by_pos)):
        for row in rows:
            for ordinal in range(int(row["action_clause_start"]), int(row["action_clause_end"]) + 1):
                mapping[(str(row["locus"]), ordinal)].add(str(row["contrast_id"]))
            mapping[(str(row["locus"]), int(row["right_first_ordinal"]))].add(str(row["contrast_id"]))

    position_index = {(str(row["locus"]), int(row["token_ordinal"])): row for row in positions}
    token_overlay: list[dict[str, object]] = []
    for old in old_tokens:
        key = (old["locus"], int(old["token_ordinal"]))
        position = position_index.get(key)
        edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **old, "v78_action_nominal_case_ids": pipe(sorted(case_ids.get(key, set()))),
            "v78_action_nominal_roles": pipe(sorted(case_roles.get(key, set()))),
            "v78_result_decisions": pipe(sorted(decisions_by_pos.get(key, set()))),
            "v78_leading_candidate_ids": pipe(sorted(leading_by_pos.get(key, set()))),
            "v78_sheky_contrast_ids": pipe(sorted(sheky_by_pos.get(key, set()))),
            "v78_dchey_contrast_ids": pipe(sorted(dchey_by_pos.get(key, set()))),
            "v78_component_id": position["component_id"] if position else "NONE",
            "v78_component_position": position["render_position"] if position else "NONE",
            "v78_component_role": position["component_role"] if position else "NONE",
            "v78_component_edge_ids": edges,
            "v78_component_membership_class": position["membership_class"] if position else "NONE",
            "v78_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v78_new_result_edge_ids": pipe([edge for edge in edges.split("|") if edge in {"C017", "C018"}]),
            "v78_token_gloss_de": old["v77_token_gloss_de"], "v78_word_delta": 0, "v78_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v78_token_gloss_de"] == old["v77_token_gloss_de"] for new, old in zip(token_overlay, old_tokens))
    assert sum(row["v78_new_result_edge_ids"] != "NONE" for row in token_overlay) == 4
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    census_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    leading_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    sheky_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    dchey_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in census_rows: census_by_locus[str(row["locus"])].append(row)
    for row in leading_rows: leading_by_locus[str(row["locus"])].append(row)
    for row in sheky_rows: sheky_by_locus[str(row["locus"])].append(row)
    for row in dchey_rows: dchey_by_locus[str(row["locus"])].append(row)
    component_by_locus = {str(row["locus"]): row for row in components}
    line_overlay: list[dict[str, object]] = []
    for old in old_lines:
        local = census_by_locus.get(old["locus"], [])
        local_leading = leading_by_locus.get(old["locus"], [])
        component = component_by_locus.get(old["locus"])
        edges = str(component["edge_ids"]) if component else "NONE"
        reading = C017_READING if old["locus"] == "f80r.17" else C018_READING if old["locus"] == "f7r.2" else "NONE"
        line_overlay.append({
            **old, "v78_action_nominal_case_ids": pipe([str(row["action_case_id"]) for row in local]),
            "v78_result_decisions": pipe([str(row["decision"]) for row in local]),
            "v78_leading_candidate_ids": pipe([str(row["candidate_id"]) for row in local_leading]),
            "v78_sheky_contrast_ids": pipe([str(row["contrast_id"]) for row in sheky_by_locus.get(old["locus"], [])]),
            "v78_dchey_contrast_ids": pipe([str(row["contrast_id"]) for row in dchey_by_locus.get(old["locus"], [])]),
            "v78_component_ids": component["component_id"] if component else "NONE",
            "v78_edge_ids": edges, "v78_component_topologies": component["topology"] if component else "NONE",
            "v78_component_microrecords_de": component["microrecord_de"] if component else "NONE",
            "v78_new_result_edge_ids": pipe([edge for edge in edges.split("|") if edge in {"C017", "C018"}]),
            "v78_working_relation_reading_de": reading,
            "v78_line_translation_de": old["v77_line_translation_de"], "v78_word_delta": 0,
            "v78_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v78_line_translation_de"] == old["v77_line_translation_de"] for new, old in zip(line_overlay, old_lines))
    assert sum(row["v78_new_result_edge_ids"] != "NONE" for row in line_overlay) == 2
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{
        **old, "v78_selected_gloss_de": old["v77_selected_gloss_de"],
        "v78_byte_identical": 1, "v78_relation_change": "NONE", "v78_status": STATUS,
    } for old in old_spans]
    assert all(new["v78_selected_gloss_de"] == old["v77_selected_gloss_de"] for new, old in zip(span_overlay, old_spans))
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT705 — V78 complete immediate first-token reader", "", f"Status: `{STATUS}`", "",
        "## Zwei neue konkrete Satzlesungen", "", f"> **C017 / f80r.17:** {C017_READING}", "",
        f"> **C018 / f7r.2:** {C018_READING}", "",
        "C017 bindet nur `sheky#3 → shkeol#4`; #5 ist ein ungebundener späterer Registereintrag. C018 bindet nur "
        "`dold#5 → dchey#6`; #7-9 sind ungebundene spätere Registereinträge. Beide Beziehungen sind lokale "
        "Arbeitslesungen und keine neuen Wortbedeutungen.", "", "## Warum diese zwei vorne liegen", "",
        "- Bei C017 werden **Einweichen**, **Erhitzen** und **Mittelstufe** unmittelbar gespiegelt.",
        "- Bei C018 wird **Abmessen** direkt als **abgemessen** gespiegelt; **fertig** ist die semantische Entsprechung zu **abschließen**.",
        "- A066, A072 und A046 spiegeln je eine starke Einzelkomponente; A006 nur Abschluss; A043 nur einen verwandten Trockenstand.",
        "", "## Die entscheidenden Gegenproben", "",
        "Das identische `sheky` steht dreimal. Nur A057 führt zum eingeweichten, bis Mittelstufe erhitzten "
        "Drogenstoff. A058 führt direkt zu einer weiteren Handlung; A060 zu heißem Rohstoff am Gradanfang. "
        "Daher bedeutet `sheky` nicht automatisch dieses Ergebnis.", "",
        "Das identische Ziel `dchey` folgt sowohl A056 als auch A043. Nur A056 schreibt vorher Abmessen und "
        "Abschließen; A043 liefert weder Abmessen noch Portion noch Mittelstufe. Daher bindet `dchey` nicht "
        "automatisch an jede linke Handlung.", "", "## Vollständiger 60er-Bestand", "",
        "| Entscheidung | Anzahl | Bedeutung |", "|---|---:|---|",
        "| neue lokale Kante | 2 | A057/C017 und A056/C018 |",
        "| neue attraktive offene Lesart | 5 | A066, A072, A046, A006, A043 |",
        "| bereits aufgenommene Lesart wiederholt | 3 | A007, A026, A033 |",
        "| vorher offen, weiter offen | 4 | A005, A009, A024, A053 |",
        "| partielle Kompatibilität | 20 | mögliche Patienten, Mengen oder Einzelzustände ohne komplettes Ergebnis |",
        "| sichtbarer Konflikt | 26 | Material-, Prozess-, Temperatur-, Feuchte- oder Gradbruch |", "",
        "Damit besitzen wir **17 Kanten in 12 Komponenten**. Die 479 Token-Glossen, 51 Zeilenübersetzungen, "
        "3 Spannen und 36 Seiten bleiben unverändert.", "",
    ]
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")
    (ART / "README.md").write_text(
        "# GDT705 artifacts\n\n"
        "- `V78_60_ACTION_NOMINAL_RESULT_CENSUS.tsv`: complete first-token classification of immediate ACTION-to-NOMINAL transitions.\n"
        "- `V78_7_LEADING_RESULT_CANDIDATES.tsv`: two admitted and five held concrete candidates.\n"
        "- `V78_3_SHEKY_OCCURRENCE_CONTRAST.tsv`: same-action control.\n"
        "- `V78_2_DCHEY_TARGET_CONTRAST.tsv`: same-target control.\n"
        "- `V78_2_NEW_LOCAL_RESULT_EDGES.tsv`: C017 and C018 only.\n"
        "- `V78_17_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V78_12_CONNECTED_COMPONENTS.tsv`, and "
        "`V78_34_COMPONENT_POSITION_ROLES.tsv`: cumulative graph.\n"
        "- `V78_COMPONENT_TOPOLOGY_CENSUS.tsv`: graph and decision accounting.\n"
        "- `V78_GDT388_EDGE_PACKET.tsv` and `V78_GDT388_EDGE_INTAKE.json`: explicit invalid/not-score-ready intake.\n"
        "- `V78_479_TOKEN_RELATION_OVERLAY.tsv`, `V78_51_LINE_RELATION_OVERLAY.tsv`, and "
        "`V78_3_BOUND_SPAN_FREEZE.tsv`: unchanged words with V78 relation metadata.\n"
        "- `GDT705_V78_COMPLETE_RESULT_READER.md`: concise practical German reader.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    node_keys = {
        (str(row["locus"]), ordinal)
        for row in memberships for ordinal in str(row["edge_node_ordinals"]).split("|")
    }
    assert len(node_keys) == 32
    assert sum(len(str(row["edge_node_ordinals"]).split("|")) for row in memberships) == 37
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 34
    assert sum(int(row["render_window_token_count"]) for row in components) == 34
    assert json.loads(G388.read_text(encoding="utf-8"))["acquisition"]["scoring_authorized"] is False

    generated = [
        CENSUS_OUT, LEADING_OUT, SHEKY_OUT, DCHEY_OUT, EDGE_OUT, MEMBERSHIP_OUT,
        COMPONENTS_OUT, POSITIONS_OUT, TOPOLOGY_OUT, PACKET_OUT, INTAKE_OUT,
        TOKENS_OUT, LINES_OUT, SPANS_OUT, READER_OUT, ART / "README.md",
    ]
    inputs = [
        G388, G695, OLD_ACTION_CENSUS, OLD_FINISHED, OLD_RESULT, OLD_MEMBERSHIP,
        OLD_COMPONENTS, OLD_POSITIONS, OLD_TOKENS, OLD_LINES, OLD_SPANS,
        DECISION_SPEC, LEADING_SPEC, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "source_clauses": 175, "action_clauses": 83, "bound_spans": 3,
            "immediate_action_nominal_cases": 60, "new_admits": 2, "new_holds": 5,
            "replayed_admits": 3, "retained_prior_holds": 4, "open_partial": 20,
            "conflict_controls": 26, "sheky_occurrences": 3, "dchey_high_target_contrast": 2,
            "relation_edges_before": 15, "relation_edges_after": 17, "new_edges": 2,
            "connected_components": 12, "edge_nodes": 32, "edge_node_incidences": 37,
            "minimal_hull_positions": 34, "render_positions": 34, "shared_edge_nodes": 5,
            "hull_only_positions": 2, "render_only_structural_positions": 0,
            "structural_closure_positions": 1, "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "new_edge_ids": ["C017", "C018"], "c017": "f80r.17#3→f80r.17#4",
            "c018": "f7r.2#5→f7r.2#6", "c017_component": "M011",
            "c018_component": "M012", "held_new_cases": ["A066", "A072", "A046", "A006", "A043"],
            "same_surface_default": False, "same_target_default": False,
            "adjacency_default": False, "new_word_meanings": 0,
        },
        "graph": {
            "component_partition": [
                ["C009"], ["C001", "C012"], ["C002"], ["C003"], ["C004", "C008"],
                ["C005"], ["C006", "C007"], ["C010"], ["C011", "C013", "C015"],
                ["C014"], ["C017"], ["C018"],
            ],
            "shared_nodes": ["f105v.1#4", "f26r.2#4", "f26r.2#6", "f80v.35#3", "f86v6.25#4"],
            "hull_only_positions": ["f26r.2#7", "f86v5.24#2"],
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
        "status": STATUS, "immediate_action_nominal_cases": 60,
        "new_edges": ["C017", "C018"], "held_new": ["A066", "A072", "A046", "A006", "A043"],
        "edges": 17, "components": 12, "edge_nodes": 32,
        "render_positions": 34, "new_word_meanings": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
