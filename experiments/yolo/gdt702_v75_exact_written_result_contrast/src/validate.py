#!/usr/bin/env python3
"""Independent publication validator for GDT702.

This file never imports or executes the builder.  It reconstructs the clause
cut, controls and graph directly from frozen upstream tables and published
GDT702 artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast"
ART = EXP / "artifacts"
PREFIX = "experiments/yolo/gdt702_v75_exact_written_result_contrast/"
RUN_REL = PREFIX + "src/run.py"
RUN_SHA = "9cbb8093d7a6d0f0b76adb50d99a5611f2308a647e31fea0ec083369a269dd5f"
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

SPEC = EXP / "src/V75_11_TARGET_RIGHT_CONTEXT_SPECS.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G682_LINE = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/FINAL_COMPLETED_LINE_V56.tsv"
G682_AUDIT = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv"
DISPATCH = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv"
DY_SURFACES = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/SURFACE_DY_60_FORM_INVENTORY.tsv"
DY_POSITIONS = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/SURFACE_DY_74_POSITION_INVENTORY.tsv"
G696_EDGES = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_9_LOCAL_ACTION_EDGES.tsv"
G697_MICROS = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_7_EXACT_MICRORECORDS.tsv"
G698_OCC = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_10_ACTION_SURFACE_OCCURRENCES.tsv"
G698_SURFACES = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_6_ACTION_SURFACE_CENSUS.tsv"
OLD_RESULT = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/RESULT.json"
OLD_COMPONENTS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_9_CONNECTED_COMPONENTS.tsv"
OLD_MEMBERSHIP = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_11_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_POSITIONS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_26_COMPONENT_POSITION_ROLES.tsv"
OLD_TOKENS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_479_TOKEN_COMPONENT_OVERLAY.tsv"
OLD_LINES = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_51_LINE_COMPONENT_OVERLAY.tsv"
OLD_SPANS = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components/artifacts/V74_3_BOUND_SPAN_FREEZE.tsv"

CENSUS = ART / "V75_11_TARGET_RIGHT_CONTEXT_CENSUS.tsv"
NOMINAL = ART / "V75_7_NOMINAL_RIGHT_CONTEXT_CONTRASTS.tsv"
YKAIIN = ART / "V75_2_YKAIIN_RIGHT_CONTEXTS.tsv"
OLPCHEDY = ART / "V75_2_OLPCHEDY_LEFT_CONTEXTS.tsv"
EDGE = ART / "V75_1_NEW_WRITTEN_RESULT_EDGE.tsv"
MEMBERSHIP = ART / "V75_12_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS = ART / "V75_9_CONNECTED_COMPONENTS.tsv"
POSITIONS = ART / "V75_27_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY = ART / "V75_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET = ART / "V75_GDT388_EDGE_PACKET.tsv"
INTAKE = ART / "V75_GDT388_EDGE_INTAKE.json"
TOKENS = ART / "V75_479_TOKEN_RELATION_OVERLAY.tsv"
LINES = ART / "V75_51_LINE_RELATION_OVERLAY.tsv"
SPANS = ART / "V75_3_BOUND_SPAN_FREEZE.tsv"
READER = ART / "GDT702_V75_WRITTEN_RESULT_READER.md"
RESULT = ART / "RESULT.json"

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


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    if not fields or len(fields) != len(set(fields)):
        raise AssertionError(f"invalid header: {path.name}")
    if any(None in row or set(row) != set(fields) for row in rows):
        raise AssertionError(f"invalid rows: {path.name}")
    return fields, rows


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError((wanted, len(hits)))
    return hits[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordinal_set(value: str) -> set[int]:
    if value == "NONE":
        return set()
    result: set[int] = set()
    for part in value.split("|"):
        if "-" in part:
            lo, hi = map(int, part.split("-"))
            result.update(range(lo, hi + 1))
        else:
            result.add(int(part))
    return result


def prefix_projection(
    old_fields: Sequence[str], old_rows: Sequence[Mapping[str, str]],
    new_fields: Sequence[str], new_rows: Sequence[Mapping[str, str]], extra: Sequence[str],
) -> bool:
    return (
        list(new_fields) == [*old_fields, *extra]
        and len(old_rows) == len(new_rows)
        and all(all(new[field] == old[field] for field in old_fields) for old, new in zip(old_rows, new_rows))
    )


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, condition: bool, label: str) -> None:
        self.rows.append({"check": label, "pass": bool(condition)})
        if not condition:
            raise AssertionError(label)


def connected_components(edges: Mapping[str, Mapping[str, object]]) -> list[frozenset[str]]:
    unseen = set(edges)
    groups: list[frozenset[str]] = []
    while unseen:
        seed = min(unseen)
        group, stack = {seed}, [seed]
        unseen.remove(seed)
        while stack:
            current = stack.pop()
            for other in sorted(list(unseen)):
                if edges[current]["locus"] == edges[other]["locus"] and set(edges[current]["nodes"]) & set(edges[other]["nodes"]):
                    unseen.remove(other)
                    group.add(other)
                    stack.append(other)
        groups.append(frozenset(group))
    return sorted(groups, key=lambda group: sorted(group))


def main() -> int:
    audit = Audit()
    audit.check(sha256(ROOT / RUN_REL) == RUN_SHA, "externally frozen builder digest exact")
    audit.check(not (EXP / "src/__pycache__").exists(), "no generated Python cache in publication tree")

    spec_fields, specs = read_tsv(SPEC)
    _, clauses = read_tsv(CLAUSES)
    old_token_fields, old_tokens = read_tsv(OLD_TOKENS)
    token_index = {(row["locus"], row["token_ordinal"]): row for row in old_tokens}
    audit.check(len(specs) == 11 and [row["edge_id"] for row in specs] == [f"C{i:03d}" for i in range(1, 12)], "fixed C001-C011 specification complete")
    audit.check(len(clauses) == 175 and Counter(row["clause_type"] for row in clauses) == {"ACTION_CLAUSE": 83, "NOMINAL_BLOCK": 92}, "175 clauses split into 83 actions and 92 nominals")
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_locus[row["locus"]].append(row)
    for rows in by_locus.values():
        rows.sort(key=lambda row: int(row["clause_id"]))

    expected_contexts: list[dict[str, str]] = []
    for spec in specs:
        rows = by_locus[spec["locus"]]
        target = one(rows, clause_id=spec["target_clause_id"])
        audit.check(target["clause_type"] == "ACTION_CLAUSE", f"{spec['edge_id']} target is a complete action clause")
        audit.check(
            (target["start_ordinal"], target["end_ordinal"], target["surfaces"], target["v68_clause_de"])
            == (spec["target_clause_start"], spec["target_clause_end"], spec["target_clause_surfaces"], spec["target_clause_de"]),
            f"{spec['edge_id']} complete action boundary exact",
        )
        index = rows.index(target)
        right = rows[index + 1] if index + 1 < len(rows) else None
        if right is None:
            observed = ("NONE", "END_OF_LINE", "NONE", "NONE", "NONE", "NONE", "NONE")
        else:
            first = token_index[(spec["locus"], right["start_ordinal"])]
            observed = (
                right["clause_id"], right["clause_type"], right["start_ordinal"], right["end_ordinal"],
                right["start_ordinal"], first["surface"], first["v74_token_gloss_de"],
            )
        expected = tuple(spec[field] for field in (
            "right_clause_id", "right_clause_type", "right_start_ordinal", "right_end_ordinal",
            "right_first_semantic_ordinal", "right_first_surface", "right_first_gloss_de",
        ))
        audit.check(observed == expected, f"{spec['edge_id']} first semantic right item exact")
        expected_contexts.append(spec)
    audit.check(Counter(row["right_clause_type"] for row in expected_contexts) == {"NOMINAL_BLOCK": 7, "ACTION_CLAUSE": 3, "END_OF_LINE": 1}, "right-context partition is exactly 7/3/1")
    audit.check(one(specs, edge_id="C011")["target_clause_surfaces"] == "ytedy|dy" and one(specs, edge_id="C011")["right_first_surface"] == "checthedy", "C011 consumes structural dy before selecting right action")

    census_fields, census = read_tsv(CENSUS)
    nominal_fields, nominal = read_tsv(NOMINAL)
    audit.check(census_fields[:len(spec_fields)] == spec_fields and len(census) == 11, "published census has exact specification prefix")
    audit.check(all(all(row[field] == spec[field] for field in spec_fields) for row, spec in zip(census, specs)), "all eleven published census rows reproduce fixed specification")
    audit.check(all(row["target_is_gdt701_edge_target"] == row["full_action_then_first_semantic_exact"] == "1" and row["word_delta"] == "0" and row["status"] == STATUS for row in census), "census target joins status and zero-word delta exact")
    audit.check(sum(row["candidate_gate_match"] == "1" for row in census) == 1 and one(census, candidate_gate_match="1")["edge_id"] == "C001", "C001 is the sole gate match")
    audit.check(nominal_fields == census_fields and nominal == [row for row in census if row["right_clause_type"] == "NOMINAL_BLOCK"], "seven-row nominal table is exact census subset")

    _, dispatch = read_tsv(DISPATCH)
    olp_dispatch = [row for row in dispatch if row["surface"] == "olpchedy"]
    audit.check({(row["locus"], row["ordinal"]) for row in olp_dispatch} == {("f105v.1", "5"), ("f105v.14", "4")}, "exactly two GDT687 olpchedy positions")
    audit.check(all(row["action_licensed_before"] == "0" and row["dispatch_class"] == "NOMINAL_FINISHED_RESULT_STATE" and row["dy_contribution"] == "FINISHED_ENDPOINT_NOT_NEW_VERB" and row["confidence"] == "HIGH" for row in olp_dispatch), "both olpchedy positions are high nominal finished states, never actions")
    _, dy_surfaces = read_tsv(DY_SURFACES)
    olp_surface = one(dy_surfaces, surface="olpchedy")
    audit.check((olp_surface["positions"], olp_surface["v60_action_positions"], olp_surface["v60_result_positions"]) == ("2", "0", "2"), "olpchedy surface counts exact")
    audit.check((olp_surface["derived_one_edit_sister"], olp_surface["pair_status"], olp_surface["v62_class"], olp_surface["transfer_policy"]) == ("olpchey", "VISIBLE_SISTER_WITHOUT_CARD", "UNPAIRED_WHOLE_RETAINED", "WHOLE_ONLY_NO_PAIR_EXPORT"), "olpchedy remains whole-only without productive sister")
    _, dy_positions = read_tsv(DY_POSITIONS)
    audit.check({(row["locus"], row["ordinal"]) for row in dy_positions if row["surface"] == "olpchedy"} == {("f105v.1", "5"), ("f105v.14", "4")}, "GDT689 occurrence inventory has the same two olpchedy positions")

    _, g698_occ = read_tsv(G698_OCC)
    y_occ = [row for row in g698_occ if row["action_surface"] == "ykaiin"]
    audit.check({(row["locus"], row["token_ordinal"]) for row in y_occ} == {("f105v.1", "4"), ("f86v6.25", "5")}, "exactly two ykaiin action occurrences")
    _, g698_surfaces = read_tsv(G698_SURFACES)
    y_surface = one(g698_surfaces, action_surface="ykaiin")
    audit.check((y_surface["occurrence_count"], y_surface["already_bound_count"], y_surface["template_count"], y_surface["self_source_hits"], y_surface["cross_occurrence_hits"], y_surface["new_candidate_hits"], y_surface["participant_frame_multiplicity"]) == ("2", "2", "2", "2", "0", "0", "2"), "ykaiin frame census rejects portable output identity")
    audit.check(y_surface["frame_determinacy"] == "MULTIPLE_ADMITTED_PARTICIPANT_FRAMES" and y_surface["decision"] == "SURFACE_DOES_NOT_DETERMINE_PARTICIPANT_FRAME", "ykaiin action surface is nondeterministic")

    _, y_rows = read_tsv(YKAIIN)
    _, o_rows = read_tsv(OLPCHEDY)
    audit.check(len(y_rows) == 2 and {(row["locus"], row["right_first_surface"], row["decision"]) for row in y_rows} == {("f105v.1", "olpchedy", "ADMIT_C012_OCCURRENCE_BOUND"), ("f86v6.25", "or", "HOLD_NO_EXACT_RESULT_STATE")}, "published ykaiin 2-way contrast exact")
    audit.check(len(o_rows) == 2 and {(row["locus"], row["left_action_surface"], row["decision"]) for row in o_rows} == {("f105v.1", "ykaiin", "ADMIT_C012_OCCURRENCE_BOUND"), ("f105v.14", "qokaiir", "REJECT_LEFT_ACTION_DEFAULT_MATERIAL_MISMATCH")}, "published olpchedy 2-way contrast exact")
    audit.check(all(row["default_rejected"] == "NO_YKAIIN_OUTPUT_DEFAULT" for row in y_rows) and all(row["default_rejected"] == "NO_OLPCHEDY_LEFT_ACTION_DEFAULT" for row in o_rows), "both portable defaults explicitly rejected")

    _, old_edges696 = read_tsv(G696_EDGES)
    c001 = one(old_edges696, edge_id="C001")
    audit.check((c001["locus"], c001["source_start_ordinal"], c001["target_action_ordinal"]) == ("f105v.1", "3", "4") and "GDT682" in c001["license_basis"], "C001 input and shared GDT682 provenance exact")
    _, old_micros = read_tsv(G697_MICROS)
    m002_old = one(old_micros, microrecord_id="M002")
    audit.check((m002_old["right_boundary"], m002_old["right_neighbor_ordinal"], m002_old["right_neighbor_surface"]) == ("CUT_BEFORE_UNLINKED_5", "5", "olpchedy") and "without a separate edge" in m002_old["forbidden_inference"], "GDT697 old M002 cut and edge requirement exact")
    _, old_line682 = read_tsv(G682_LINE)
    _, old_audit682 = read_tsv(G682_AUDIT)
    audit.check("Ergebnis ist fertiges Trockenpulver aus Holzdrogenansatz" in one(old_line682, line_rank="1", locus="f105v.1")["practical_translation_de"], "GDT682 result prose is explicitly prior")
    audit.check(one(old_audit682, locus="f105v.1", ordinal="3", surface="olpcheey")["context_role"] == "NOMINAL_HEAT_OBJECT", "GDT682 old patient context recorded")

    edge_fields, edge_rows = read_tsv(EDGE)
    audit.check(len(edge_rows) == 1, "exactly one new-edge row")
    edge = edge_rows[0]
    expected_edge = {
        "edge_id": "C012", "component_id": "M002", "locus": "f105v.1",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_OUTPUT_TO_WRITTEN_RESULT_STATE",
        "edge_node_ordinals": "4|5", "source_action_ordinal": "4", "source_action_surface": "ykaiin",
        "written_result_ordinal": "5", "written_result_surface": "olpchedy",
        "source_material_edge_id": "C001", "source_material_ordinal": "3",
        "source_material_surface": "olpcheey", "written_result_dispatch": "NOMINAL_FINISHED_RESULT_STATE_HIGH",
        "admission_basis": "OCCURRENCE_BOUND_MATERIAL_CONCORDANCE_CONTRAST",
        "prior_prose_status": "ALREADY_PRESENT_IN_GDT682_NOT_NEW_EVIDENCE",
        "morphology_status": "WHOLE_FORM_ONLY_GDT689_NO_PAIR_EXPORT",
        "portability": "OCCURRENCE_BOUND_ONLY", "gdt388_score_ready": "NO_INVALID_FORMAL_ACCESS_PACKET",
        "edge_delta": "1", "word_delta": "0", "status": STATUS,
    }
    audit.check(all(edge[key] == value for key, value in expected_edge.items()), "C012 occurrence-bound edge fields exact")
    audit.check("fertiges Holzextraktpulver" in edge["working_microrecord_de"] and all(term in edge["forbidden_inference"] for term in ("YKAIIN", "OLPCHEDY", "adjacency", "olpche*")), "C012 concrete reading and four prohibitions explicit")

    old_membership_fields, old_membership = read_tsv(OLD_MEMBERSHIP)
    membership_fields, membership = read_tsv(MEMBERSHIP)
    audit.check(len(membership) == 12 and [row["edge_id"] for row in membership] == [f"C{i:03d}" for i in range(1, 13)], "C001-C012 membership complete and ordered")
    for old in old_membership:
        new = one(membership, edge_id=old["edge_id"])
        sources = ordinal_set(old["edge_node_ordinals"]) - {int(old["target_action_ordinal"])}
        expected_sources = "|".join(map(str, sorted(sources))) if sources else "NONE"
        audit.check(all(new[key] == old[key] for key in ("edge_id", "component_id", "locus", "support_tier", "relation_class", "edge_node_ordinals", "origin")), f"{old['edge_id']} inherited identity exact")
        audit.check(new["source_ordinals"] == expected_sources and new["target_ordinal"] == old["target_action_ordinal"] and new["target_role"] == "TARGET_ACTION", f"{old['edge_id']} direction re-expressed exactly")
    c012 = one(membership, edge_id="C012")
    audit.check((c012["edge_node_ordinals"], c012["source_ordinals"], c012["target_ordinal"], c012["target_role"], c012["origin"]) == ("4|5", "4", "5", "WRITTEN_RESULT_STATE_LABEL", "NEW_GDT702"), "C012 membership preserves nominal target role")

    edge_defs = {
        row["edge_id"]: {"locus": row["locus"], "nodes": ordinal_set(row["edge_node_ordinals"]), "component": row["component_id"]}
        for row in membership
    }
    groups = connected_components(edge_defs)
    expected_groups = {
        frozenset({"C009"}), frozenset({"C001", "C012"}), frozenset({"C002"}),
        frozenset({"C003"}), frozenset({"C005"}), frozenset({"C004", "C008"}),
        frozenset({"C006", "C007"}), frozenset({"C010"}), frozenset({"C011"}),
    }
    audit.check(set(groups) == expected_groups, "exact-node union independently yields nine expected components")
    unique_nodes = {(str(defn["locus"]), ordinal) for defn in edge_defs.values() for ordinal in set(defn["nodes"])}
    incidences = sum(len(set(defn["nodes"])) for defn in edge_defs.values())
    audit.check(len(unique_nodes) == 24 and incidences == 27, "graph has 24 unique nodes and 27 incidences")
    shared: set[tuple[str, int]] = set()
    for group in groups:
        counts = Counter((str(edge_defs[edge_id]["locus"]), ordinal) for edge_id in group for ordinal in set(edge_defs[edge_id]["nodes"]))
        shared.update(node for node, count in counts.items() if count > 1)
    audit.check(shared == {("f80v.35", 3), ("f86v6.25", 4), ("f105v.1", 4)}, "three exact shared edge nodes")

    old_component_fields, old_components = read_tsv(OLD_COMPONENTS)
    component_fields, components = read_tsv(COMPONENTS)
    audit.check(component_fields == old_component_fields and len(components) == 9, "nine components retain V74 component schema")
    m002 = one(components, component_id="M002")
    expected_m002 = {
        "edge_ids": "C001|C012", "edge_count": "2", "edge_node_ordinals": "3|4|5",
        "edge_node_count": "3", "shared_edge_node_ordinals": "4", "edge_hull_start": "3",
        "edge_hull_end": "5", "edge_hull_position_count": "3", "hull_only_ordinals": "NONE",
        "render_window_start": "3", "render_window_end": "5", "render_only_structural_ordinals": "NONE",
        "render_window_token_count": "3", "topology": "INPUT_ACTION_WRITTEN_RESULT_CHAIN",
        "action_ordinals": "4", "support_profile": "A_PLUS_B",
        "expected_surfaces": "olpcheey|ykaiin|olpchedy", "observed_surfaces": "olpcheey|ykaiin|olpchedy",
        "final_result_status": "WRITTEN_FINAL_RESULT_STATE:C012", "origin": "GDT702_EXTENDED_EXACT",
        "edge_delta": "1", "word_delta": "0", "status": STATUS,
    }
    audit.check(all(m002[key] == value for key, value in expected_m002.items()), "M002 input-action-written-result chain exact")
    ignored_component_fields = {"origin", "edge_delta", "word_delta", "status"}
    for old in old_components:
        if old["component_id"] == "M002":
            continue
        new = one(components, component_id=old["component_id"])
        audit.check(all(new[field] == old[field] for field in old_component_fields if field not in ignored_component_fields), f"{old['component_id']} substantive component fields unchanged")
        audit.check((new["origin"], new["edge_delta"], new["word_delta"], new["status"]) == ("GDT701_INHERITED_EXACT", "0", "0", STATUS), f"{old['component_id']} inherited provenance exact")
    audit.check(sum(int(row["edge_count"]) for row in components) == 12 and sum(int(row["edge_node_count"]) for row in components) == 24 and sum(int(row["edge_hull_position_count"]) for row in components) == 26 and sum(int(row["render_window_token_count"]) for row in components) == 27, "component totals are 12 edges 24 nodes 26 hull and 27 render positions")

    old_position_fields, old_positions = read_tsv(OLD_POSITIONS)
    position_fields, positions = read_tsv(POSITIONS)
    audit.check(position_fields == old_position_fields and len(positions) == 27, "position table keeps schema and adds exactly one row")
    position_index = {(row["locus"], row["token_ordinal"]): row for row in positions}
    old_non_m002 = [row for row in old_positions if row["component_id"] != "M002"]
    for old in old_non_m002:
        new = position_index[(old["locus"], old["token_ordinal"])]
        audit.check(all(new[field] == old[field] for field in old_position_fields if field != "status") and new["status"] == STATUS, f"position unchanged {old['locus']}#{old['token_ordinal']}")
    p3, p4, p5 = (one(positions, locus="f105v.1", token_ordinal=str(value)) for value in (3, 4, 5))
    audit.check((p3["surface"], p3["render_position"], p3["render_size"], p3["edge_ids"]) == ("olpcheey", "1", "3", "C001"), "M002 patient position exact")
    audit.check((p4["surface"], p4["render_position"], p4["edge_ids"], p4["source_edge_ids"], p4["reference_edge_ids"], p4["target_edge_ids"], p4["is_shared_edge_node"], p4["action_output_role"]) == ("ykaiin", "2", "C001|C012", "C012", "C001", "C001", "1", "WRITTEN_RESULT_SOURCE_ACTION:C012"), "M002 action bridge position exact")
    audit.check((p5["surface"], p5["render_position"], p5["component_role"], p5["edge_ids"], p5["target_edge_ids"], p5["action_output_role"]) == ("olpchedy", "3", "WRITTEN_RESULT_STATE_LABEL:C012", "C012", "C012", "WRITTEN_FINAL_RESULT_STATE:C012"), "M002 written result position exact")
    audit.check(Counter(row["membership_class"] for row in positions) == {"EDGE_NODE": 24, "HULL_ONLY": 2, "RENDER_ONLY_STRUCTURAL": 1} and sum(row["is_shared_edge_node"] == "1" for row in positions) == 3 and sum(row["is_action_target"] == "1" for row in positions) == 11, "position classes shared nodes and action targets exact")
    audit.check({(row["locus"], row["token_ordinal"]) for row in positions if row["is_hull_only"] == "1"} == {("f86v5.24", "2"), ("f26r.2", "5")} and {(row["locus"], row["token_ordinal"]) for row in positions if row["is_render_only_structural"] == "1"} == {("f26r.2", "7")}, "two hull-only and one structural positions unchanged")

    _, topology = read_tsv(TOPOLOGY)
    topo = {(row["dimension"], row["value"]): row for row in topology}
    expected_topology = {
        ("TOPOLOGY", "SINGLE_EDGE"): "4", ("TOPOLOGY", "INPUT_ACTION_WRITTEN_RESULT_CHAIN"): "1",
        ("TOPOLOGY", "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT"): "1",
        ("TOPOLOGY", "SERIAL_ACTION_OUTPUT_CHAIN"): "1",
        ("TOPOLOGY", "SINGLE_EDGE_WITH_UNBOUND_QUANTITY_HULL"): "1",
        ("TOPOLOGY", "SINGLE_EDGE_ACROSS_EXACT_STATE_CHECKPOINT"): "1",
        ("POSITION_CLASS", "EDGE_NODE"): "24", ("POSITION_CLASS", "HULL_ONLY_NOT_NODE"): "2",
        ("POSITION_CLASS", "RENDER_ONLY_STRUCTURAL"): "1",
        ("RESULT_STATUS", "NAMED_INTERMEDIATE_OUTPUT"): "1", ("RESULT_STATUS", "NAMED_FINAL_RESULT"): "1",
        ("SOURCE_FINAL_STATUS", "UNNAMED_NO_OUTGOING_EDGE"): "7",
        ("SOURCE_FINAL_STATUS", "NOT_DECLARED_IN_V72"): "1",
    }
    audit.check(len(topology) == 17 and all(row["status"] == STATUS for row in topology), "topology census has 17 status-bound rows")
    audit.check(all(topo[key]["count"] == count for key, count in expected_topology.items()), "topology position and result counts exact")

    token_fields, tokens = read_tsv(TOKENS)
    old_line_fields, old_lines = read_tsv(OLD_LINES)
    line_fields, lines = read_tsv(LINES)
    old_span_fields, old_spans = read_tsv(OLD_SPANS)
    span_fields, spans = read_tsv(SPANS)
    audit.check(prefix_projection(old_token_fields, old_tokens, token_fields, tokens, TOKEN_EXTRA), "479-token V74 prefix byte-identical")
    audit.check(prefix_projection(old_line_fields, old_lines, line_fields, lines, LINE_EXTRA), "51-line V74 prefix byte-identical")
    audit.check(prefix_projection(old_span_fields, old_spans, span_fields, spans, SPAN_EXTRA), "three-span V74 prefix byte-identical")
    audit.check(all(row["v75_token_gloss_de"] == row["v74_token_gloss_de"] and row["v75_word_delta"] == "0" and row["v75_status"] == STATUS for row in tokens), "479 token glosses unchanged")
    audit.check(all(row["v75_line_translation_de"] == row["v74_line_translation_de"] and row["v75_word_delta"] == "0" and row["v75_status"] == STATUS for row in lines), "51 line translations unchanged")
    audit.check(all(row["v75_selected_gloss_de"] == row["v74_selected_gloss_de"] and row["v75_byte_identical"] == "1" and row["v75_relation_change"] == "NONE" and row["v75_status"] == STATUS for row in spans), "three bound spans unchanged")
    audit.check({(row["locus"], row["token_ordinal"]) for row in tokens if row["v75_new_result_edge_ids"] == "C012"} == {("f105v.1", "4"), ("f105v.1", "5")}, "C012 token overlay touches only source and result")
    audit.check([row["locus"] for row in lines if row["v75_new_result_edge_ids"] == "C012"] == ["f105v.1"], "C012 line overlay touches only f105v.1")
    audit.check(len({row["page"] for row in tokens}) == 36 and all(not row["page"].lower().startswith("f84") for row in tokens + lines), "36 pages and no f84 family access")

    packet_fields, packet_rows = read_tsv(PACKET)
    packet = packet_rows[0]
    audit.check(len(packet_rows) == 1 and (packet["edge_id"], packet["pivot_locus"], packet["target_locus"], packet["formal_access_state"], packet["eligibility_status"]) == ("C012", "f105v.1@4", "f105v.1@5", "FORMAL_ACCESSED", "INELIGIBLE_WORKSHOP_EDGE"), "single C012 packet uses exact GDT388 @ loci")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET.relative_to(ROOT))], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    expected_intake = {
        "capacity_gate_50_edges_5_folios": False, "discovery_edges": 0, "eligible_edges": 0,
        "eligible_folios": 0, "errors": ["edge row 2: formal access is not sealed"],
        "holdout_edges": 0, "holdout_gate": False, "mobile_edges": 0,
        "mobile_null_gate": False, "packet_rows": 1, "score_ready": False,
        "status": "INVALID_PACKET",
    }
    audit.check(completed.returncode == 1 and not completed.stderr and json.loads(completed.stdout) == expected_intake, "official GDT388 check returns exact sole formal-access error")
    audit.check(json.loads(INTAKE.read_text(encoding="utf-8")) == expected_intake, "published intake JSON exact")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit.check((result["status"], result["question"], result["claim_ceiling"], result["next_gap"]) == (STATUS, QUESTION, CLAIM, NEXT_GAP), "RESULT identity claim and next gap exact")
    expected_basis = {
        "action_clauses": 83, "action_right_contexts": 3, "bound_spans": 3,
        "connected_components": 9, "edge_node_incidences": 27, "edge_nodes": 24,
        "end_of_line_right_contexts": 1, "f84_access": 0, "f84r_access": 0,
        "held_rival_rows": 17, "hull_only_positions": 2, "lines": 51,
        "minimal_hull_positions": 26, "new_edges": 1, "new_pages": 0,
        "nominal_right_contexts": 7, "olpchedy_occurrences": 2, "pages": 36,
        "reference_rows": 27, "relation_edges_after": 12, "relation_edges_before": 11,
        "render_only_structural_positions": 1, "render_positions": 27,
        "shared_edge_nodes": 3, "source_clauses": 175, "target_action_right_contexts": 11,
        "token_positions": 479, "ykaiin_target_occurrences": 2,
    }
    audit.check(result["basis"] == expected_basis, "RESULT complete numeric basis exact")
    audit.check(result["decision"]["new_edge_id"] == "C012" and result["decision"]["new_participant_identities"] == 1 and result["decision"]["changed_existing_edges"] == 0 and result["decision"]["new_word_meanings"] == 0, "RESULT adds one participant edge and zero word meanings")
    audit.check(all(result["decision"][key] is False for key in ("ykaiin_output_default", "olpchedy_left_action_default", "adjacency_default", "productive_olpche_morphology", "later_nominal_skip")), "RESULT rejects all five unsafe defaults")
    audit.check(result["freeze"] == {"bound_spans_byte_identical": 3, "changed_word_meanings": 0, "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0, "line_translations_byte_identical": 51, "new_word_meanings": 0, "token_glosses_byte_identical": 479}, "RESULT freeze exact")
    audit.check(result["gdt388"] == expected_intake and result["provenance_caution"] == {"gdt682_c001_patient_context_shared": True, "gdt682_prior_result_prose": True, "gdt687_types_result_but_not_producer": True, "independent_a_tier_support": False}, "RESULT packet and circularity caution exact")

    generated = {
        path.name: path for path in (
            CENSUS, NOMINAL, YKAIIN, OLPCHEDY, EDGE, MEMBERSHIP, COMPONENTS,
            POSITIONS, TOPOLOGY, PACKET, INTAKE, TOKENS, LINES, SPANS, READER, ART / "README.md",
        )
    }
    audit.check(result["files"] == {name: sha256(path) for name, path in generated.items()}, "RESULT binds all builder-generated artifacts")
    audit.check(result["inputs"][RUN_REL] == RUN_SHA and result["inputs"][str(SPEC.relative_to(ROOT))] == sha256(SPEC), "RESULT binds builder digest and fixed specification")
    audit.check(all(sha256(ROOT / relative) == digest for relative, digest in result["inputs"].items()), "all RESULT input digests exact")

    reader = READER.read_text(encoding="utf-8")
    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    readme = (EXP / "README.md").read_text(encoding="utf-8")
    method = (EXP / "METHOD.md").read_text(encoding="utf-8")
    audit.check(STATUS in reader and "Das trocken gebundene Holzpulver" in reader and "7 Nominalblöcke, 3 Aktionsklauseln, 1 Zeilenende" in reader, "reader exposes concrete result and full census")
    audit.check(STATUS in report and "11 auf 12 Kanten" in report and "23 auf 24" in report and "26 auf 27" in report, "REPORT exposes exact graph delta")
    audit.check(STATUS in readme and all(term in method for term in ("C012", "B_WORKING_LOCAL", "Symmetric 2×2", "GDT388")), "entry docs expose status method and claim ceiling")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    dependencies = ["GDT388", "GDT682", "GDT687", "GDT689", "GDT695", "GDT696", "GDT697", "GDT698", "GDT701"]
    audit.check((manifest["experiment_id"], manifest["slug"], manifest["status"], manifest["question"], manifest["claim_ceiling"]) == ("GDT702", "v75_exact_written_result_contrast", STATUS, QUESTION, CLAIM), "manifest identity and result contract exact")
    audit.check(manifest["dependencies"] == dependencies and manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest dependencies and seals exact")
    audit.check(manifest["commands"] == {"run": "python3 " + RUN_REL, "validate": "python3 " + PREFIX + "src/validate.py"} and manifest["validation"] == {"artifact": PREFIX + "artifacts/VALIDATION.json", "status": "PASS"}, "manifest commands and validation contract exact")
    audit.check(manifest["artifact_policy"]["max_inline_bytes"] == 5_000_000 and bool(manifest["artifact_policy"]["large_artifact_justification"]), "manifest full-projection justification present")
    external_inputs = {relative: digest for relative, digest in result["inputs"].items() if not relative.startswith(PREFIX)}
    manifest_inputs = {entry["path"]: entry for entry in manifest["inputs"]}
    audit.check(set(manifest_inputs) == set(external_inputs), "manifest exact external input set")
    audit.check(all(entry["sha256"] == external_inputs[path] and bool(entry["role"]) for path, entry in manifest_inputs.items()), "manifest external input hashes and roles exact")
    expected_outputs = {
        PREFIX + name for name in ("README.md", "METHOD.md", "REPORT.md", "src/V75_11_TARGET_RIGHT_CONTEXT_SPECS.tsv", "src/run.py", "src/validate.py")
    } | {
        PREFIX + "artifacts/" + name for name in (
            "GDT702_V75_WRITTEN_RESULT_READER.md", "README.md", "RESULT.json",
            "V75_11_TARGET_RIGHT_CONTEXT_CENSUS.tsv", "V75_12_EDGE_COMPONENT_MEMBERSHIP.tsv",
            "V75_1_NEW_WRITTEN_RESULT_EDGE.tsv", "V75_27_COMPONENT_POSITION_ROLES.tsv",
            "V75_2_OLPCHEDY_LEFT_CONTEXTS.tsv", "V75_2_YKAIIN_RIGHT_CONTEXTS.tsv",
            "V75_3_BOUND_SPAN_FREEZE.tsv", "V75_479_TOKEN_RELATION_OVERLAY.tsv",
            "V75_51_LINE_RELATION_OVERLAY.tsv", "V75_7_NOMINAL_RIGHT_CONTEXT_CONTRASTS.tsv",
            "V75_9_CONNECTED_COMPONENTS.tsv", "V75_COMPONENT_TOPOLOGY_CENSUS.tsv",
            "V75_GDT388_EDGE_INTAKE.json", "V75_GDT388_EDGE_PACKET.tsv", "VALIDATION.json",
        )
    }
    manifest_outputs = {entry["path"]: entry for entry in manifest["outputs"]}
    audit.check(set(manifest_outputs) == expected_outputs and len(expected_outputs) == 24, "manifest exact 24-file reproducible output tree")
    for relative, entry in sorted(manifest_outputs.items()):
        audit.check(bool(entry["role"]) and bool(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])), f"manifest output syntax {Path(relative).name}")
        if not relative.endswith("/VALIDATION.json"):
            audit.check(sha256(ROOT / relative) == entry["sha256"], f"manifest output digest {relative}")

    payload = {
        "status": "PASS", "checks": len(audit.rows), "failed": 0,
        "summary": {
            "target_right_contexts": 11, "nominal_right_contexts": 7,
            "action_right_contexts": 3, "end_of_line_right_contexts": 1,
            "ykaiin_controls": 2, "olpchedy_controls": 2, "new_edge": "C012",
            "relation_edges": 12, "connected_components": 9, "edge_nodes": 24,
            "edge_node_incidences": 27, "minimal_hull_positions": 26,
            "render_positions": 27, "shared_edge_nodes": 3, "hull_only_positions": 2,
            "render_only_structural_positions": 1, "tokens_frozen": 479,
            "lines_frozen": 51, "spans_frozen": 3, "new_participant_identities": 1,
            "new_word_meanings": 0,
        },
        "audit": audit.rows,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
