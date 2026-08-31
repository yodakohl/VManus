#!/usr/bin/env python3
"""Build GDT702's exact written-result contrast and cumulative V75 atlas."""

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
EXP = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = "PASS_V75_11_TARGET_RIGHT_CONTEXTS__7_NOMINAL_3_ACTION_1_EOS__1_EXACT_WRITTEN_RESULT__2X2_DEFAULTS_REJECTED__C012_OCCURRENCE_BOUND__ZERO_WORD_DELTA"
QUESTION = (
    "Does the complete immediate-right-context census of all eleven GDT701 target actions, "
    "together with both YKAIIN targets and both in-scope OLPCHEDY occurrences, support one "
    "occurrence-bound C012 link from f105v.1#4 to written result-state label #5 without "
    "generalizing adjacency, action surface or morphology?"
)
CLAIM = (
    "V75 adds one B-tier occurrence-bound relation C012 from f105v.1#4 ykaiin to the "
    "immediately written #5 olpchedy result-state label. The old German meanings and the "
    "old GDT682 result prose are not new evidence: the only new decision is a contrastive "
    "re-admission in the current graph. The second YKAIIN target and second OLPCHEDY "
    "occurrence reject portable action, adjacency and word-family defaults. This is an "
    "exploratory local working relation, not plaintext, productive morphology or historical decipherment."
)
NEXT_GAP = (
    "Preserve C012 and the two negative defaults. Next census all 83 current action clauses "
    "for a first semantic right token independently typed as a finished result state, then "
    "require an already written compatible patient or output; do not use adjacency alone, "
    "skip intervening entries, add a word meaning or open a page."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G682_LINE = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/FINAL_COMPLETED_LINE_V56.tsv"
G682_AUDIT = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
G687_DISPATCH = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv"
G689_SURFACES = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/SURFACE_DY_60_FORM_INVENTORY.tsv"
G689_POSITIONS = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/SURFACE_DY_74_POSITION_INVENTORY.tsv"
G695_CLAUSES = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G696_EDGES = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_9_LOCAL_ACTION_EDGES.tsv"
G697_MICROS = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_7_EXACT_MICRORECORDS.tsv"
G698_OCCURRENCES = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_10_ACTION_SURFACE_OCCURRENCES.tsv"
G698_SURFACES = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_6_ACTION_SURFACE_CENSUS.tsv"
G701_RESULT = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/RESULT.json"
G701_COMPONENTS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_9_CONNECTED_COMPONENTS.tsv"
G701_MEMBERSHIP = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_11_EDGE_COMPONENT_MEMBERSHIP.tsv"
G701_POSITIONS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_26_COMPONENT_POSITION_ROLES.tsv"
G701_TOKENS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_479_TOKEN_COMPONENT_OVERLAY.tsv"
G701_LINES = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_51_LINE_COMPONENT_OVERLAY.tsv"
G701_SPANS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_3_BOUND_SPAN_FREEZE.tsv"
SPEC = SRC / "V75_11_TARGET_RIGHT_CONTEXT_SPECS.tsv"

CENSUS_OUT = ART / "V75_11_TARGET_RIGHT_CONTEXT_CENSUS.tsv"
NOMINAL_OUT = ART / "V75_7_NOMINAL_RIGHT_CONTEXT_CONTRASTS.tsv"
YKAIIN_OUT = ART / "V75_2_YKAIIN_RIGHT_CONTEXTS.tsv"
OLPCHEDY_OUT = ART / "V75_2_OLPCHEDY_LEFT_CONTEXTS.tsv"
EDGE_OUT = ART / "V75_1_NEW_WRITTEN_RESULT_EDGE.tsv"
MEMBERSHIP_OUT = ART / "V75_12_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V75_9_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V75_27_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V75_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V75_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V75_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V75_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V75_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V75_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT702_V75_WRITTEN_RESULT_READER.md"
RESULT_OUT = ART / "RESULT.json"
ARTIFACT_README = ART / "README.md"

SPEC_FIELDS = [
    "census_id", "edge_id", "component_id", "locus", "target_action_ordinal",
    "target_surface", "target_clause_id", "target_clause_start", "target_clause_end",
    "target_clause_surfaces", "target_clause_de", "right_clause_id", "right_clause_type",
    "right_start_ordinal", "right_end_ordinal", "right_first_semantic_ordinal",
    "right_first_surface", "right_first_gloss_de", "right_context_class",
    "result_dispatch", "result_confidence", "material_head_status",
    "intervening_semantic_items", "decision", "reason_de", "anti_skip_ordinals",
    "forbidden_inference",
]
CENSUS_FIELDS = [*SPEC_FIELDS, "page", "target_is_gdt701_edge_target", "full_action_then_first_semantic_exact", "candidate_gate_match", "word_delta", "status"]
YKAIIN_FIELDS = [
    "case_id", "locus", "target_ordinal", "target_surface", "input_edge_id",
    "input_node_ordinals", "input_gloss_de", "right_clause_id", "right_first_ordinal",
    "right_first_surface", "right_first_gloss_de", "right_dispatch", "right_confidence",
    "material_concordance", "decision", "default_rejected", "status",
]
OLPCHEDY_FIELDS = [
    "case_id", "locus", "result_ordinal", "result_surface", "result_gloss_de",
    "result_dispatch", "result_confidence", "left_clause_id", "left_action_ordinal",
    "left_action_surface", "left_action_gloss_de", "left_material_basis",
    "material_concordance", "visible_surface_frame", "decision", "default_rejected", "status",
]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "edge_node_ordinals", "source_action_ordinal", "source_action_surface",
    "written_result_ordinal", "written_result_surface", "source_material_edge_id",
    "source_material_ordinal", "source_material_surface", "source_material_gloss_de",
    "written_result_gloss_de", "written_result_dispatch", "admission_basis",
    "prior_prose_status", "morphology_status", "working_microrecord_de", "portability",
    "gdt388_score_ready", "forbidden_inference", "edge_delta", "word_delta", "status",
]
MEMBERSHIP_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "edge_node_ordinals", "source_ordinals", "target_ordinal", "target_role",
    "component_edge_count", "component_topology", "shared_edge_node_ordinals",
    "origin", "v75_change", "status",
]
TOKEN_EXTRA = [
    "v75_right_context_census_ids", "v75_right_context_roles", "v75_olpchedy_control_ids",
    "v75_component_id", "v75_component_position", "v75_component_role",
    "v75_component_edge_ids", "v75_component_membership_class",
    "v75_component_microrecord_de", "v75_new_result_edge_ids", "v75_token_gloss_de",
    "v75_word_delta", "v75_status",
]
LINE_EXTRA = [
    "v75_right_context_census_ids", "v75_olpchedy_control_ids", "v75_component_ids",
    "v75_edge_ids", "v75_component_topologies", "v75_component_microrecords_de",
    "v75_new_result_edge_ids", "v75_working_relation_reading_de",
    "v75_line_translation_de", "v75_word_delta", "v75_status",
]
SPAN_EXTRA = ["v75_selected_gloss_de", "v75_byte_identical", "v75_relation_change", "v75_status"]
PACKET_FIELDS = [
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
    "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
    "source_aware_localizer", "relation_reviewer", "relation_confidence",
    "ambiguity_state", "formal_access_state", "fold_assignment", "eligibility_status",
]
TOPOLOGY_FIELDS = ["dimension", "value", "count", "component_ids", "note", "status"]
M002_READING = (
    "Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. "
    "Ergebnis: fertiges Holzextraktpulver."
)


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    assert fields and len(fields) == len(set(fields))
    assert all(None not in row and set(row) == set(fields) for row in rows)
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def pipe(values: Sequence[str]) -> str:
    cleaned = [value for value in values if value and value != "NONE"]
    return "|".join(dict.fromkeys(cleaned)) if cleaned else "NONE"


def ordinals(value: str) -> list[int]:
    if value == "NONE":
        return []
    result: list[int] = []
    for part in value.split("|"):
        if "-" in part:
            lo, hi = map(int, part.split("-"))
            result.extend(range(lo, hi + 1))
        else:
            result.append(int(part))
    return sorted(set(result))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(SPEC)
    assert spec_fields == SPEC_FIELDS and len(specs) == 11
    assert [row["census_id"] for row in specs] == [f"V75R{i:03d}" for i in range(1, 12)]
    assert [row["edge_id"] for row in specs] == [f"C{i:03d}" for i in range(1, 12)]
    assert len({row["locus"] + "#" + row["target_action_ordinal"] for row in specs}) == 11

    _, clauses = read_tsv(G695_CLAUSES)
    assert len(clauses) == 175 and len({row["locus"] for row in clauses}) == 51
    clauses_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_locus[row["locus"]].append(row)
    for rows in clauses_by_locus.values():
        rows.sort(key=lambda row: int(row["clause_id"]))

    token_fields, tokens = read_tsv(G701_TOKENS)
    line_fields, lines = read_tsv(G701_LINES)
    span_fields, spans = read_tsv(G701_SPANS)
    component_fields, old_components = read_tsv(G701_COMPONENTS)
    _, old_membership = read_tsv(G701_MEMBERSHIP)
    position_fields, old_positions = read_tsv(G701_POSITIONS)
    assert len(tokens) == 479 and len(lines) == 51 and len(spans) == 3
    assert len(old_components) == 9 and len(old_membership) == 11 and len(old_positions) == 26
    result701 = json.loads(G701_RESULT.read_text(encoding="utf-8"))
    assert result701["status"].startswith("PASS_V74_11_EDGES__9_CONNECTED_COMPONENTS")
    assert result701["basis"]["source_clauses"] == 175

    token_index = {(row["locus"], row["token_ordinal"]): row for row in tokens}
    membership_index = {row["edge_id"]: row for row in old_membership}
    census_rows: list[dict[str, object]] = []
    for spec in specs:
        edge = membership_index[spec["edge_id"]]
        assert edge["component_id"] == spec["component_id"] and edge["locus"] == spec["locus"]
        assert edge["target_action_ordinal"] == spec["target_action_ordinal"]
        target = token_index[(spec["locus"], spec["target_action_ordinal"])]
        assert target["surface"] == spec["target_surface"]
        rows = clauses_by_locus[spec["locus"]]
        target_clause = one(rows, clause_id=spec["target_clause_id"])
        assert target_clause["clause_type"] == "ACTION_CLAUSE"
        observed_target = {
            "target_clause_start": target_clause["start_ordinal"],
            "target_clause_end": target_clause["end_ordinal"],
            "target_clause_surfaces": target_clause["surfaces"],
            "target_clause_de": target_clause["v68_clause_de"],
        }
        assert all(spec[key] == value for key, value in observed_target.items())
        index = rows.index(target_clause)
        right = rows[index + 1] if index + 1 < len(rows) else None
        if right is None:
            observed_right = {
                "right_clause_id": "NONE", "right_clause_type": "END_OF_LINE",
                "right_start_ordinal": "NONE", "right_end_ordinal": "NONE",
                "right_first_semantic_ordinal": "NONE", "right_first_surface": "NONE",
                "right_first_gloss_de": "NONE",
            }
        else:
            first_ordinal = right["start_ordinal"]
            first = token_index[(spec["locus"], first_ordinal)]
            observed_right = {
                "right_clause_id": right["clause_id"], "right_clause_type": right["clause_type"],
                "right_start_ordinal": right["start_ordinal"], "right_end_ordinal": right["end_ordinal"],
                "right_first_semantic_ordinal": first_ordinal, "right_first_surface": first["surface"],
                "right_first_gloss_de": first["v74_token_gloss_de"],
            }
        assert all(spec[key] == value for key, value in observed_right.items())
        candidate = spec["decision"] == "CANDIDATE_C012"
        census_rows.append({
            **spec, "page": target["page"], "target_is_gdt701_edge_target": "1",
            "full_action_then_first_semantic_exact": "1",
            "candidate_gate_match": "1" if candidate else "0", "word_delta": "0", "status": STATUS,
        })

    assert Counter(row["right_clause_type"] for row in specs) == {"NOMINAL_BLOCK": 7, "ACTION_CLAUSE": 3, "END_OF_LINE": 1}
    candidates = [row for row in specs if row["decision"] == "CANDIDATE_C012"]
    assert len(candidates) == 1 and candidates[0]["edge_id"] == "C001"
    assert candidates[0]["right_first_surface"] == "olpchedy"
    assert candidates[0]["result_dispatch"] == "NOMINAL_FINISHED_RESULT_STATE"
    assert candidates[0]["result_confidence"] == "HIGH"
    assert candidates[0]["material_head_status"] == "PRESENT_CONCORDANT_WOOD_POWDER_RESULT"
    write_tsv(CENSUS_OUT, census_rows, CENSUS_FIELDS)
    nominal_rows = [row for row in census_rows if row["right_clause_type"] == "NOMINAL_BLOCK"]
    write_tsv(NOMINAL_OUT, nominal_rows, CENSUS_FIELDS)

    # Reconstruct the two-by-two contrast from its primary sources.  The old
    # prose is deliberately recorded as prior wording, never counted as an
    # independent witness for the new graph edge.
    _, dispatch = read_tsv(G687_DISPATCH)
    olp_dispatch = [row for row in dispatch if row["surface"] == "olpchedy"]
    assert {(row["locus"], row["ordinal"]) for row in olp_dispatch} == {
        ("f105v.1", "5"), ("f105v.14", "4"),
    }
    assert all(row["dispatch_class"] == "NOMINAL_FINISHED_RESULT_STATE" for row in olp_dispatch)
    assert all(row["confidence"] == "HIGH" for row in olp_dispatch)
    assert all(row["action_licensed_before"] == "0" for row in olp_dispatch)
    assert all(row["dy_contribution"] == "FINISHED_ENDPOINT_NOT_NEW_VERB" for row in olp_dispatch)

    _, surface_inventory = read_tsv(G689_SURFACES)
    olp_surface = one(surface_inventory, surface="olpchedy")
    assert olp_surface["positions"] == "2" and olp_surface["v60_result_positions"] == "2"
    assert olp_surface["v60_action_positions"] == "0"
    assert olp_surface["v62_class"] == "UNPAIRED_WHOLE_RETAINED"
    assert olp_surface["transfer_policy"] == "WHOLE_ONLY_NO_PAIR_EXPORT"
    _, dy_positions = read_tsv(G689_POSITIONS)
    olp_positions = [row for row in dy_positions if row["surface"] == "olpchedy"]
    assert {(row["locus"], row["ordinal"]) for row in olp_positions} == {
        ("f105v.1", "5"), ("f105v.14", "4"),
    }

    _, g696_edges = read_tsv(G696_EDGES)
    c001_old, c006_old = one(g696_edges, edge_id="C001"), one(g696_edges, edge_id="C006")
    assert (c001_old["locus"], c001_old["source_start_ordinal"], c001_old["source_end_ordinal"], c001_old["target_action_ordinal"]) == ("f105v.1", "3", "3", "4")
    assert (c006_old["locus"], c006_old["source_start_ordinal"], c006_old["source_end_ordinal"], c006_old["target_action_ordinal"]) == ("f86v6.25", "4", "4", "5")
    assert "GDT682" in c001_old["license_basis"]
    _, old_micros = read_tsv(G697_MICROS)
    old_m002 = one(old_micros, microrecord_id="M002")
    assert old_m002["window_end_ordinal"] == "4"
    assert old_m002["right_boundary"] == "CUT_BEFORE_UNLINKED_5"
    assert (old_m002["right_neighbor_ordinal"], old_m002["right_neighbor_surface"]) == ("5", "olpchedy")
    assert "without a separate edge" in old_m002["forbidden_inference"]

    _, old_lines682 = read_tsv(G682_LINE)
    old_line682 = one(old_lines682, line_rank="1", locus="f105v.1")
    assert "Ergebnis ist fertiges Trockenpulver aus Holzdrogenansatz" in old_line682["practical_translation_de"]
    _, audit682 = read_tsv(G682_AUDIT)
    old_object682 = one(audit682, locus="f105v.1", ordinal="3", surface="olpcheey")
    assert old_object682["context_role"] == "NOMINAL_HEAT_OBJECT"
    assert old_object682["right_surface"] == "ykaiin"

    _, action_occurrences = read_tsv(G698_OCCURRENCES)
    ykaiin_occurrences = [row for row in action_occurrences if row["action_surface"] == "ykaiin"]
    assert {(row["locus"], row["token_ordinal"]) for row in ykaiin_occurrences} == {
        ("f105v.1", "4"), ("f86v6.25", "5"),
    }
    assert all(row["decision"] == "ALREADY_ADMITTED_EXACT_SELF_REPLAY" for row in ykaiin_occurrences)
    _, action_surface_census = read_tsv(G698_SURFACES)
    ykaiin_surface = one(action_surface_census, action_surface="ykaiin")
    assert ykaiin_surface["occurrence_count"] == "2"
    assert ykaiin_surface["cross_occurrence_hits"] == "0"
    assert ykaiin_surface["decision"] == "SURFACE_DOES_NOT_DETERMINE_PARTICIPANT_FRAME"

    ykaiin_rows = [
        {
            "case_id": "Y001", "locus": "f105v.1", "target_ordinal": 4,
            "target_surface": "ykaiin", "input_edge_id": "C001", "input_node_ordinals": "3|4",
            "input_gloss_de": "trocken gebundenes Holzpulver, Form II",
            "right_clause_id": 3, "right_first_ordinal": 5, "right_first_surface": "olpchedy",
            "right_first_gloss_de": token_index[("f105v.1", "5")]["v74_token_gloss_de"],
            "right_dispatch": "NOMINAL_FINISHED_RESULT_STATE", "right_confidence": "HIGH",
            "material_concordance": "WOOD_POWDER_TO_FINISHED_WOOD_EXTRACT_POWDER",
            "decision": "ADMIT_C012_OCCURRENCE_BOUND",
            "default_rejected": "NO_YKAIIN_OUTPUT_DEFAULT", "status": STATUS,
        },
        {
            "case_id": "Y002", "locus": "f86v6.25", "target_ordinal": 5,
            "target_surface": "ykaiin", "input_edge_id": "C006", "input_node_ordinals": "4|5",
            "input_gloss_de": "abgemessener Drogenanteil I",
            "right_clause_id": 5, "right_first_ordinal": 6, "right_first_surface": "or",
            "right_first_gloss_de": token_index[("f86v6.25", "6")]["v74_token_gloss_de"],
            "right_dispatch": "NOT_RESULT_STATE", "right_confidence": "NOT_APPLICABLE",
            "material_concordance": "DRUG_SHARE_TO_UNMARKED_DRUG_PORTION_ONLY",
            "decision": "HOLD_NO_EXACT_RESULT_STATE",
            "default_rejected": "NO_YKAIIN_OUTPUT_DEFAULT", "status": STATUS,
        },
    ]
    write_tsv(YKAIIN_OUT, ykaiin_rows, YKAIIN_FIELDS)

    olpchedy_rows = [
        {
            "case_id": "O001", "locus": "f105v.1", "result_ordinal": 5,
            "result_surface": "olpchedy", "result_gloss_de": token_index[("f105v.1", "5")]["v74_token_gloss_de"],
            "result_dispatch": "NOMINAL_FINISHED_RESULT_STATE", "result_confidence": "HIGH",
            "left_clause_id": 2, "left_action_ordinal": 4, "left_action_surface": "ykaiin",
            "left_action_gloss_de": token_index[("f105v.1", "4")]["v74_token_gloss_de"],
            "left_material_basis": "C001:olpcheey#3 trocken gebundenes Holzpulver, Form II",
            "material_concordance": "CONCORDANT_WOOD_POWDER_RESULT",
            "visible_surface_frame": "olpcheey#3→ykaiin#4→olpchedy#5",
            "decision": "ADMIT_C012_OCCURRENCE_BOUND",
            "default_rejected": "NO_OLPCHEDY_LEFT_ACTION_DEFAULT", "status": STATUS,
        },
        {
            "case_id": "O002", "locus": "f105v.14", "result_ordinal": 4,
            "result_surface": "olpchedy", "result_gloss_de": token_index[("f105v.14", "4")]["v74_token_gloss_de"],
            "result_dispatch": "NOMINAL_FINISHED_RESULT_STATE", "result_confidence": "HIGH",
            "left_clause_id": 2, "left_action_ordinal": 3, "left_action_surface": "qokaiir",
            "left_action_gloss_de": token_index[("f105v.14", "3")]["v74_token_gloss_de"],
            "left_material_basis": "qokaiir#3:nimm den heißen Drogenanteil III",
            "material_concordance": "MISMATCH_DRUG_SHARE_TO_WOOD_EXTRACT_POWDER",
            "visible_surface_frame": "qokaiir#3→olpchedy#4",
            "decision": "REJECT_LEFT_ACTION_DEFAULT_MATERIAL_MISMATCH",
            "default_rejected": "NO_OLPCHEDY_LEFT_ACTION_DEFAULT", "status": STATUS,
        },
    ]
    write_tsv(OLPCHEDY_OUT, olpchedy_rows, OLPCHEDY_FIELDS)

    edge_row = {
        "edge_id": "C012", "component_id": "M002", "locus": "f105v.1",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_OUTPUT_TO_WRITTEN_RESULT_STATE",
        "edge_node_ordinals": "4|5", "source_action_ordinal": 4,
        "source_action_surface": "ykaiin", "written_result_ordinal": 5,
        "written_result_surface": "olpchedy", "source_material_edge_id": "C001",
        "source_material_ordinal": 3, "source_material_surface": "olpcheey",
        "source_material_gloss_de": token_index[("f105v.1", "3")]["v74_token_gloss_de"],
        "written_result_gloss_de": token_index[("f105v.1", "5")]["v74_token_gloss_de"],
        "written_result_dispatch": "NOMINAL_FINISHED_RESULT_STATE_HIGH",
        "admission_basis": "OCCURRENCE_BOUND_MATERIAL_CONCORDANCE_CONTRAST",
        "prior_prose_status": "ALREADY_PRESENT_IN_GDT682_NOT_NEW_EVIDENCE",
        "morphology_status": "WHOLE_FORM_ONLY_GDT689_NO_PAIR_EXPORT",
        "working_microrecord_de": M002_READING, "portability": "OCCURRENCE_BOUND_ONLY",
        "gdt388_score_ready": "NO_INVALID_FORMAL_ACCESS_PACKET",
        "forbidden_inference": "No YKAIIN output default, no OLPCHEDY left-action default, no adjacency default and no productive olpche* morphology.",
        "edge_delta": 1, "word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [edge_row], EDGE_FIELDS)

    # Extend only M002.  Every other V74 component remains field-identical
    # except for provenance/status metadata.
    components: list[dict[str, object]] = []
    for old in old_components:
        row: dict[str, object] = dict(old)
        row["origin"] = "GDT701_INHERITED_EXACT"
        row["edge_delta"] = 0
        row["word_delta"] = 0
        row["status"] = STATUS
        if old["component_id"] == "M002":
            row.update({
                "edge_ids": "C001|C012", "edge_count": 2,
                "edge_node_ordinals": "3|4|5", "edge_node_count": 3,
                "shared_edge_node_ordinals": "4", "edge_hull_start": 3,
                "edge_hull_end": 5, "edge_hull_position_count": 3,
                "hull_only_ordinals": "NONE", "render_window_start": 3,
                "render_window_end": 5, "render_only_structural_ordinals": "NONE",
                "render_window_token_count": 3,
                "topology": "INPUT_ACTION_WRITTEN_RESULT_CHAIN", "action_ordinals": "4",
                "support_profile": "A_PLUS_B",
                "expected_surfaces": "olpcheey|ykaiin|olpchedy",
                "observed_surfaces": "olpcheey|ykaiin|olpchedy",
                "microrecord_de": M002_READING,
                "component_basis": "C001 binds the written wood powder to YKAIIN; C012 locally binds that action to the immediately written, independently typed finished wood-extract-powder state.",
                "boundary_note_de": "#2 remains outside; #5 is now the written terminal result node. #6 and #7 remain later entries, not skipped alternatives.",
                "forbidden_inference": "Do not export a YKAIIN output rule, an OLPCHEDY adjacency rule or productive olpche* morphology.",
                "final_result_status": "WRITTEN_FINAL_RESULT_STATE:C012",
                "origin": "GDT702_EXTENDED_EXACT", "edge_delta": 1,
            })
        components.append(row)
    components.sort(key=lambda row: int(str(row["component_id"])[1:]))
    assert [row["component_id"] for row in components] == [f"M{i:03d}" for i in range(1, 10)]
    assert sum(int(row["edge_count"]) for row in components) == 12
    assert sum(int(row["edge_node_count"]) for row in components) == 24
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 26
    assert sum(int(row["render_window_token_count"]) for row in components) == 27
    assert sum(len(ordinals(str(row["hull_only_ordinals"]))) for row in components) == 2
    assert sum(len(ordinals(str(row["render_only_structural_ordinals"]))) for row in components) == 1
    write_tsv(COMPONENTS_OUT, components, component_fields)

    components_by_id = {str(row["component_id"]): row for row in components}
    membership_rows: list[dict[str, object]] = []
    for old in old_membership:
        component = components_by_id[old["component_id"]]
        target = int(old["target_action_ordinal"])
        sources = [value for value in ordinals(old["edge_node_ordinals"]) if value != target]
        membership_rows.append({
            "edge_id": old["edge_id"], "component_id": old["component_id"],
            "locus": old["locus"], "support_tier": old["support_tier"],
            "relation_class": old["relation_class"],
            "edge_node_ordinals": old["edge_node_ordinals"],
            "source_ordinals": pipe([str(value) for value in sources]),
            "target_ordinal": target, "target_role": "TARGET_ACTION",
            "component_edge_count": component["edge_count"],
            "component_topology": component["topology"],
            "shared_edge_node_ordinals": component["shared_edge_node_ordinals"],
            "origin": old["origin"],
            "v75_change": "COMPONENT_EXTENDED_BY_C012_EDGE_UNCHANGED" if old["edge_id"] == "C001" else "NONE",
            "status": STATUS,
        })
    membership_rows.append({
        "edge_id": "C012", "component_id": "M002", "locus": "f105v.1",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_OUTPUT_TO_WRITTEN_RESULT_STATE",
        "edge_node_ordinals": "4|5", "source_ordinals": "4", "target_ordinal": 5,
        "target_role": "WRITTEN_RESULT_STATE_LABEL", "component_edge_count": 2,
        "component_topology": "INPUT_ACTION_WRITTEN_RESULT_CHAIN",
        "shared_edge_node_ordinals": "4", "origin": "NEW_GDT702",
        "v75_change": "ADD_C012", "status": STATUS,
    })
    membership_rows.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert [row["edge_id"] for row in membership_rows] == [f"C{i:03d}" for i in range(1, 13)]
    assert sum(len(ordinals(str(row["edge_node_ordinals"]))) for row in membership_rows) == 27
    write_tsv(MEMBERSHIP_OUT, membership_rows, MEMBERSHIP_FIELDS)

    position_rows: list[dict[str, object]] = []
    for old in old_positions:
        row: dict[str, object] = dict(old)
        row["status"] = STATUS
        if old["component_id"] == "M002":
            row["render_size"] = 3
            row["component_microrecord_de"] = M002_READING
            if old["token_ordinal"] == "4":
                row.update({
                    "component_role": "REFERENCE:C001|TARGET_ACTION:C001|DONOR_ACTION_OUTPUT:C012",
                    "edge_ids": "C001|C012", "source_edge_ids": "C012",
                    "reference_edge_ids": "C001", "target_edge_ids": "C001",
                    "is_shared_edge_node": 1,
                    "action_output_role": "WRITTEN_RESULT_SOURCE_ACTION:C012",
                })
        position_rows.append(row)
    result_token = token_index[("f105v.1", "5")]
    position_rows.append({
        "page": result_token["page"], "locus": "f105v.1", "token_ordinal": 5,
        "surface": "olpchedy", "token_gloss_de": result_token["v74_token_gloss_de"],
        "component_id": "M002", "render_position": 3, "render_size": 3,
        "component_role": "WRITTEN_RESULT_STATE_LABEL:C012", "edge_ids": "C012",
        "source_edge_ids": "NONE", "reference_edge_ids": "NONE", "target_edge_ids": "C012",
        "membership_class": "EDGE_NODE", "is_edge_node": 1, "is_hull_only": 0,
        "is_render_only_structural": 0, "is_action_target": 0,
        "is_shared_edge_node": 0, "action_output_role": "WRITTEN_FINAL_RESULT_STATE:C012",
        "component_microrecord_de": M002_READING, "word_delta": 0, "status": STATUS,
    })
    position_rows.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(position_rows) == 27
    assert len({(row["locus"], str(row["token_ordinal"])) for row in position_rows}) == 27
    assert Counter(row["membership_class"] for row in position_rows) == {
        "EDGE_NODE": 24, "HULL_ONLY": 2, "RENDER_ONLY_STRUCTURAL": 1,
    }
    assert sum(int(row["is_action_target"]) for row in position_rows) == 11
    assert sum(int(row["is_shared_edge_node"]) for row in position_rows) == 3
    assert one(position_rows, component_id="M002", token_ordinal="4")["edge_ids"] == "C001|C012"
    assert one(position_rows, component_id="M002", token_ordinal=5)["component_role"] == "WRITTEN_RESULT_STATE_LABEL:C012"
    write_tsv(POSITIONS_OUT, position_rows, position_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_notes = {
        "SINGLE_EDGE": "four unchanged plain one-edge components",
        "INPUT_ACTION_WRITTEN_RESULT_CHAIN": "C001 supplies the written patient and C012 attaches the action to one written final-result state",
        "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT": "two actions share one written destination; no serial output carry",
        "SERIAL_ACTION_OUTPUT_CHAIN": "the written first action result is consumed by the second action",
        "SINGLE_EDGE_WITH_UNBOUND_QUANTITY_HULL": "C010 skips one unbound quantity register inside its hull",
        "SINGLE_EDGE_ACROSS_EXACT_STATE_CHECKPOINT": "C011 skips one exact state checkpoint inside its hull",
    }
    topology_rows: list[dict[str, object]] = []
    for value in sorted(topology_groups):
        ids = topology_groups[value]
        topology_rows.append({
            "dimension": "TOPOLOGY", "value": value, "count": len(ids),
            "component_ids": pipe(ids), "note": topology_notes[value], "status": STATUS,
        })
    for value in sorted(support_groups):
        ids = support_groups[value]
        topology_rows.append({
            "dimension": "SUPPORT_PROFILE", "value": value, "count": len(ids),
            "component_ids": pipe(ids),
            "note": "edge tiers remain explicit; the new B edge is not averaged into C001's A tier",
            "status": STATUS,
        })
    topology_rows.extend([
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 24, "component_ids": "M001|M002|M003|M004|M005|M006|M007|M008|M009", "note": "unique exact occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 2, "component_ids": "M008|M009", "note": "f86v5.24#2 and f26r.2#5 remain hull-only", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 1, "component_ids": "M009", "note": "free DY at f26r.2#7 remains structural", "status": STATUS},
        {"dimension": "RESULT_STATUS", "value": "NAMED_INTERMEDIATE_OUTPUT", "count": 1, "component_ids": "M007", "note": "qodar#4 remains the sole written serial intermediate", "status": STATUS},
        {"dimension": "SOURCE_FINAL_STATUS", "value": "UNNAMED_NO_OUTGOING_EDGE", "count": 7, "component_ids": "M001|M003|M004|M005|M006|M007|M009", "note": "unchanged inherited final status", "status": STATUS},
        {"dimension": "SOURCE_FINAL_STATUS", "value": "NOT_DECLARED_IN_V72", "count": 1, "component_ids": "M008", "note": "C010 has no source final-result-status field", "status": STATUS},
        {"dimension": "RESULT_STATUS", "value": "NAMED_FINAL_RESULT", "count": 1, "component_ids": "M002", "note": "olpchedy#5 is the sole admitted written final-result state", "status": STATUS},
    ])
    assert len(topology_rows) == 17
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packet_row = {
        "edge_id": "C012", "batch_id": "GDT702_V75", "page": "f105v",
        "physical_folio": "f105", "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE",
        "pivot_visual_id": "TOKEN_4_YKAIIN_ACTION", "pivot_locus": "f105v.1@4",
        "target_visual_id": "TOKEN_5_OLPCHEDY_RESULT_STATE", "target_locus": "f105v.1@5",
        "relation_type": "WORKSHOP_ACTION_TO_WRITTEN_RESULT_STATE",
        "direction_basis": "FULL_ACTION_THEN_FIRST_SEMANTIC_RESULT_CONTRAST",
        "ownership_basis": "C001_WRITTEN_PATIENT_MATERIAL_CONCORDANCE",
        "geometry_only_selection": "FALSE", "source_manifest_id": "GDT702",
        "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT702_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": "B_WORKING_LOCAL", "ambiguity_state": "WORKSHOP_ONLY",
        "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
    }
    write_tsv(PACKET_OUT, [packet_row], PACKET_FIELDS)
    intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", rel(PACKET_OUT)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    assert intake.returncode == 1 and not intake.stderr
    assert json.loads(intake.stdout) == expected_intake
    INTAKE_OUT.write_text(json.dumps(expected_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    census_ids_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    census_roles_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    for spec in specs:
        locus, census_id = spec["locus"], spec["census_id"]
        for ordinal in range(int(spec["target_clause_start"]), int(spec["target_clause_end"]) + 1):
            census_ids_by_position[(locus, ordinal)].add(census_id)
            census_roles_by_position[(locus, ordinal)].add(f"TARGET_ACTION_CLAUSE:{census_id}")
        if spec["right_first_semantic_ordinal"] != "NONE":
            ordinal = int(spec["right_first_semantic_ordinal"])
            census_ids_by_position[(locus, ordinal)].add(census_id)
            census_roles_by_position[(locus, ordinal)].add(f"FIRST_RIGHT_SEMANTIC:{census_id}")
        for ordinal in ordinals(spec["anti_skip_ordinals"]):
            census_ids_by_position[(locus, ordinal)].add(census_id)
            census_roles_by_position[(locus, ordinal)].add(f"ANTI_SKIP_CONTROL:{census_id}")

    control_ids_by_position = {
        ("f105v.1", 5): "O001",
        ("f105v.14", 4): "O002",
    }
    positions_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in position_rows}
    token_overlay: list[dict[str, object]] = []
    for row in tokens:
        key = (row["locus"], int(row["token_ordinal"]))
        position = positions_by_key.get(key)
        component_edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **row,
            "v75_right_context_census_ids": pipe(sorted(census_ids_by_position.get(key, set()))),
            "v75_right_context_roles": pipe(sorted(census_roles_by_position.get(key, set()))),
            "v75_olpchedy_control_ids": control_ids_by_position.get(key, "NONE"),
            "v75_component_id": position["component_id"] if position else "NONE",
            "v75_component_position": position["render_position"] if position else "NONE",
            "v75_component_role": position["component_role"] if position else "NONE",
            "v75_component_edge_ids": component_edges,
            "v75_component_membership_class": position["membership_class"] if position else "NONE",
            "v75_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v75_new_result_edge_ids": "C012" if "C012" in component_edges.split("|") else "NONE",
            "v75_token_gloss_de": row["v74_token_gloss_de"],
            "v75_word_delta": 0, "v75_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v75_token_gloss_de"] == old["v74_token_gloss_de"] for new, old in zip(token_overlay, tokens))
    assert sum(row["v75_new_result_edge_ids"] == "C012" for row in token_overlay) == 2
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    specs_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        specs_by_locus[spec["locus"]].append(spec)
    controls_by_locus: dict[str, list[str]] = defaultdict(list)
    for (locus, _), control_id in control_ids_by_position.items():
        controls_by_locus[locus].append(control_id)
    components_by_locus = {str(row["locus"]): row for row in components}
    assert len(components_by_locus) == 9
    line_overlay: list[dict[str, object]] = []
    for row in lines:
        local_specs = specs_by_locus.get(row["locus"], [])
        component = components_by_locus.get(row["locus"])
        line_overlay.append({
            **row,
            "v75_right_context_census_ids": pipe([spec["census_id"] for spec in local_specs]),
            "v75_olpchedy_control_ids": pipe(controls_by_locus.get(row["locus"], [])),
            "v75_component_ids": component["component_id"] if component else "NONE",
            "v75_edge_ids": component["edge_ids"] if component else "NONE",
            "v75_component_topologies": component["topology"] if component else "NONE",
            "v75_component_microrecords_de": component["microrecord_de"] if component else "NONE",
            "v75_new_result_edge_ids": "C012" if row["locus"] == "f105v.1" else "NONE",
            "v75_working_relation_reading_de": component["microrecord_de"] if component else "NONE",
            "v75_line_translation_de": row["v74_line_translation_de"],
            "v75_word_delta": 0, "v75_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v75_line_translation_de"] == old["v74_line_translation_de"] for new, old in zip(line_overlay, lines))
    assert sum(row["v75_new_result_edge_ids"] == "C012" for row in line_overlay) == 1
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{
        **row, "v75_selected_gloss_de": row["v74_selected_gloss_de"],
        "v75_byte_identical": 1, "v75_relation_change": "NONE", "v75_status": STATUS,
    } for row in spans]
    assert len(span_overlay) == 3
    assert all(new["v75_selected_gloss_de"] == old["v74_selected_gloss_de"] for new, old in zip(span_overlay, spans))
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT702 — V75 exact written-result reader", "", f"Status: `{STATUS}`", "",
        "## Konkrete neue Arbeitskette", "", f"> {M002_READING}", "",
        "Die neue Kante ist ausschließlich `C012: f105v.1#4 ykaiin → #5 olpchedy`. "
        "C001 liefert weiterhin den geschriebenen Patienten `#3 olpcheey`; #4 ist damit "
        "die gemeinsame Aktionsbrücke zwischen Eingang und geschriebenem Resultatzustand.", "",
        "## Vollständiger Rechtskontext-Zensus", "",
        "| Kante | Locus | vollständige Zielaktion | erster rechter Eintrag | Klasse | Entscheidung |",
        "|---|---|---|---|---|---|",
    ]
    for row in census_rows:
        right = "—" if row["right_first_surface"] == "NONE" else f"#{row['right_first_semantic_ordinal']} `{row['right_first_surface']}`"
        reader.append(
            f"| {row['edge_id']} | `{row['locus']}` | #{row['target_clause_start']}–#{row['target_clause_end']} "
            f"`{row['target_clause_surfaces']}` | {right} | {row['right_clause_type']} | {row['decision']} |"
        )
    reader.extend([
        "", "Exakte Verteilung: **7 Nominalblöcke, 3 Aktionsklauseln, 1 Zeilenende**. "
        "Kein späteres attraktiveres Wort wird über den ersten rechten semantischen Eintrag hinweg ausgewählt.", "",
        "## Der 2×2-Kontrast", "",
        "- Das zweite `ykaiin` (`f86v6.25#5`) wird rechts von `or` gefolgt, nicht von einem exakt typisierten Fertigresultat.",
        "- Das zweite `olpchedy` (`f105v.14#4`) folgt auf `qokaiir` ‚nimm den heißen Drogenanteil III‘; das passt materiell nicht zum Holzextraktpulver.",
        "- Deshalb gelten weder `ykaiin → Ergebnis`, noch `olpchedy → vorherige Aktion`, noch bloße Nachbarschaft als Default.",
        "- GDT689 lässt `olpchedy` nur als gelerntes Ganzwort zu; eine produktive `olpche*`-Ableitung bleibt verboten.", "",
        "## Evidenzgrenze", "",
        "GDT682 formulierte dieses Ergebnis bereits in der alten praktischen Prosa. GDT687 typisierte beide "
        "OLPCHEDY-Stellen als nominale Fertigresultatzustände. Beides macht C012 nachvollziehbar, aber nicht unabhängig: "
        "C012 bleibt daher B-tier, occurrence-bound und nicht score-ready. Die 479 Wortglossen, 51 Zeilenübersetzungen "
        "und 3 gebundenen Spannen bleiben unverändert; hinzu kommt keine Wortbedeutung und keine Seite.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")

    ARTIFACT_README.write_text(
        "# GDT702 artifacts\n\n"
        "- `V75_11_TARGET_RIGHT_CONTEXT_CENSUS.tsv`: first semantic item after every complete C001–C011 target action.\n"
        "- `V75_7_NOMINAL_RIGHT_CONTEXT_CONTRASTS.tsv`: the seven nominal right contexts without later-token skipping.\n"
        "- `V75_2_YKAIIN_RIGHT_CONTEXTS.tsv` and `V75_2_OLPCHEDY_LEFT_CONTEXTS.tsv`: exact 2×2 default controls.\n"
        "- `V75_1_NEW_WRITTEN_RESULT_EDGE.tsv`: occurrence-bound C012 only.\n"
        "- `V75_12_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V75_9_CONNECTED_COMPONENTS.tsv`, and `V75_27_COMPONENT_POSITION_ROLES.tsv`: cumulative graph after C012.\n"
        "- `V75_COMPONENT_TOPOLOGY_CENSUS.tsv`: topology, support, position, and result accounting.\n"
        "- `V75_GDT388_EDGE_PACKET.tsv` and `V75_GDT388_EDGE_INTAKE.json`: explicit invalid/not-score-ready relation packet.\n"
        "- `V75_479_TOKEN_RELATION_OVERLAY.tsv`, `V75_51_LINE_RELATION_OVERLAY.tsv`, and `V75_3_BOUND_SPAN_FREEZE.tsv`: unchanged V74 language plus separate V75 relation metadata.\n"
        "- `GDT702_V75_WRITTEN_RESULT_READER.md`: practical reading and complete contrast table.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    g388_result = json.loads(G388.read_text(encoding="utf-8"))
    assert g388_result["status"] == "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES"
    assert g388_result["acquisition"]["scoring_authorized"] is False
    assert sum(row["clause_type"] == "ACTION_CLAUSE" for row in clauses) == 83
    generated = [
        CENSUS_OUT, NOMINAL_OUT, YKAIIN_OUT, OLPCHEDY_OUT, EDGE_OUT,
        MEMBERSHIP_OUT, COMPONENTS_OUT, POSITIONS_OUT, TOPOLOGY_OUT,
        PACKET_OUT, INTAKE_OUT, TOKENS_OUT, LINES_OUT, SPANS_OUT,
        READER_OUT, ARTIFACT_README,
    ]
    inputs = [
        G388, G682_LINE, G682_AUDIT, G687_DISPATCH, G689_SURFACES, G689_POSITIONS,
        G695_CLAUSES, G696_EDGES, G697_MICROS, G698_OCCURRENCES, G698_SURFACES,
        G701_RESULT, G701_COMPONENTS, G701_MEMBERSHIP, G701_POSITIONS,
        G701_TOKENS, G701_LINES, G701_SPANS, SPEC, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "source_clauses": 175, "action_clauses": 83, "bound_spans": 3,
            "target_action_right_contexts": 11, "nominal_right_contexts": 7,
            "action_right_contexts": 3, "end_of_line_right_contexts": 1,
            "ykaiin_target_occurrences": 2, "olpchedy_occurrences": 2,
            "relation_edges_before": 11, "relation_edges_after": 12, "new_edges": 1,
            "held_rival_rows": result701["basis"]["held_rival_rows"],
            "reference_rows": result701["basis"]["reference_rows"],
            "connected_components": 9, "minimal_hull_positions": 26,
            "render_positions": 27, "edge_nodes": 24, "edge_node_incidences": 27,
            "shared_edge_nodes": 3, "hull_only_positions": 2,
            "render_only_structural_positions": 1, "f84_access": 0, "f84r_access": 0,
        },
        "topology": {
            "generic_one_edge_components": 6, "plain_single_edge_components": 4,
            "input_action_written_result_chains": 1, "common_destination_fanouts": 1,
            "serial_action_output_chains": 1, "unbound_quantity_hull_components": 1,
            "exact_state_checkpoint_components": 1, "named_intermediate_outputs": 1,
            "named_final_results": 1,
        },
        "decision": {
            "new_edge_id": "C012", "support_tier": "B_WORKING_LOCAL",
            "relation_class": "ACTION_OUTPUT_TO_WRITTEN_RESULT_STATE",
            "edge": "f105v.1#4→f105v.1#5", "source_material_edge": "C001",
            "admission_basis": "OCCURRENCE_BOUND_MATERIAL_CONCORDANCE_CONTRAST",
            "component_id": "M002", "component_nodes": "3|4|5",
            "component_topology": "INPUT_ACTION_WRITTEN_RESULT_CHAIN",
            "shared_edge_nodes": ["f80v.35#3", "f86v6.25#4", "f105v.1#4"],
            "ykaiin_output_default": False, "olpchedy_left_action_default": False,
            "adjacency_default": False, "productive_olpche_morphology": False,
            "later_nominal_skip": False, "changed_existing_edges": 0,
            "new_participant_identities": 1, "new_word_meanings": 0,
        },
        "provenance_caution": {
            "gdt682_prior_result_prose": True,
            "gdt682_c001_patient_context_shared": True,
            "gdt687_types_result_but_not_producer": True,
            "independent_a_tier_support": False,
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
        "status": STATUS, "right_contexts": 11, "right_context_split": "7/3/1",
        "new_edge": "C012", "edges": 12, "components": 9, "edge_nodes": 24,
        "render_positions": 27, "new_word_meanings": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
