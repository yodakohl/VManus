#!/usr/bin/env python3
"""Build the cumulative C001-C011 connected-component working edition."""

from __future__ import annotations

import csv
import hashlib
import json
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
EXP = ROOT / "experiments/yolo/gdt701_v74_cumulative_relation_components"
SRC, ART = EXP / "src", EXP / "artifacts"

STATUS = (
    "PASS_V74_11_EDGES__9_CONNECTED_COMPONENTS__23_EDGE_NODES_"
    "2_HULL_ONLY_1_STRUCTURAL__ZERO_EDGE_WORD_DELTA"
)
QUESTION = (
    "Do the complete current C001-C011 relation edges form exactly nine "
    "occurrence-node connected components whose practical microrecords can be "
    "published without adding an edge, participant identity, result name or "
    "word meaning?"
)
CLAIM_CEILING = (
    "V74 compiles the eleven existing occurrence-bound relation edges into "
    "nine exact graph components and nine practical German microrecords. It "
    "adds no relation or meaning. C010#2 and C011#5 are hull-only rather than "
    "edge nodes; C011#7 is render-only structural closure. The C011 heated-herb "
    "identity remains a B-tier hypothesis, and no final action result is named. "
    "This is an exploratory working edition, not plaintext, a portable grammar "
    "or historical decipherment."
)
NEXT_GAP = (
    "Preserve the nine-component atlas. Next inventory the exact immediate "
    "right contexts of all eleven target actions for an explicitly written "
    "result label, without using adjacency, fluent recipe order or a default "
    "output carry; add no page or word meaning."
)

SPEC = SRC / "V74_2_NEW_COMPONENT_SPECS.tsv"
G697_RESULT = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/RESULT.json"
G696_EDGES = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_9_LOCAL_ACTION_EDGES.tsv"
G696_RIVALS = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_17_RELATION_RIVALS.tsv"
G696_REFS = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_27_REFERENCE_CENSUS.tsv"
G697_MICRO = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_7_EXACT_MICRORECORDS.tsv"
G697_COVERAGE = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv"
G697_ROLES = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_19_WINDOW_TOKEN_ROLES.tsv"
G699_EDGE = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_1_NEW_LOCAL_HEAT_EDGE.tsv"
G700_RESULT = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/RESULT.json"
G700_REGISTER = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_11_RELATION_EDGE_REGISTER.tsv"
G700_EDGE = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_1_NEW_LOCAL_CHECKPOINT_EDGE.tsv"
G700_CONTRASTS = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_2_DEICTIC_ANA_CONTRASTS.tsv"
G700_CONTROLS = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_4_C011_BOUNDARY_CONTROLS.tsv"
G700_TOKENS = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_479_TOKEN_RELATION_OVERLAY.tsv"
G700_LINES = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_51_LINE_RELATION_OVERLAY.tsv"
G700_SPANS = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_3_BOUND_SPAN_FREEZE.tsv"

COMPONENTS_OUT = ART / "V74_9_CONNECTED_COMPONENTS.tsv"
MEMBERSHIP_OUT = ART / "V74_11_EDGE_COMPONENT_MEMBERSHIP.tsv"
POSITIONS_OUT = ART / "V74_26_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V74_COMPONENT_TOPOLOGY_CENSUS.tsv"
TOKENS_OUT = ART / "V74_479_TOKEN_COMPONENT_OVERLAY.tsv"
LINES_OUT = ART / "V74_51_LINE_COMPONENT_OVERLAY.tsv"
SPANS_OUT = ART / "V74_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT701_V74_CUMULATIVE_RELATION_COMPONENT_READER.md"
ARTIFACT_README = ART / "README.md"
RESULT_OUT = ART / "RESULT.json"

SPEC_FIELDS = [
    "component_id", "locus", "edge_ids", "edge_node_ordinals",
    "edge_hull_start", "edge_hull_end", "hull_only_ordinals",
    "render_window_start", "render_window_end",
    "render_only_structural_ordinals", "topology", "support_profile",
    "action_ordinals", "expected_surfaces", "microrecord_de",
    "component_basis", "boundary_note_de", "forbidden_inference",
    "final_result_status",
]
COMPONENT_FIELDS = [
    "component_id", "locus", "edge_ids", "edge_count",
    "edge_node_ordinals", "edge_node_count", "shared_edge_node_ordinals",
    "edge_hull_start", "edge_hull_end", "edge_hull_position_count",
    "hull_only_ordinals", "render_window_start", "render_window_end",
    "render_only_structural_ordinals", "render_window_token_count",
    "topology", "action_ordinals", "support_profile", "expected_surfaces",
    "observed_surfaces", "microrecord_de", "component_basis",
    "boundary_note_de", "forbidden_inference", "final_result_status",
    "origin", "edge_delta", "word_delta", "status",
]
MEMBERSHIP_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "edge_node_ordinals", "target_action_ordinal", "component_edge_count",
    "component_topology", "shared_edge_node_ordinals", "origin",
    "v74_change", "status",
]
POSITION_FIELDS = [
    "page", "locus", "token_ordinal", "surface", "token_gloss_de",
    "component_id", "render_position", "render_size", "component_role",
    "edge_ids", "source_edge_ids", "reference_edge_ids", "target_edge_ids",
    "membership_class", "is_edge_node", "is_hull_only",
    "is_render_only_structural", "is_action_target", "is_shared_edge_node",
    "action_output_role", "component_microrecord_de", "word_delta", "status",
]
TOPOLOGY_FIELDS = ["dimension", "value", "count", "component_ids", "note", "status"]
TOKEN_EXTRA = [
    "v74_component_id", "v74_component_position", "v74_component_role",
    "v74_component_edge_ids", "v74_component_membership_class",
    "v74_component_microrecord_de", "v74_token_gloss_de", "v74_word_delta",
    "v74_status",
]
LINE_EXTRA = [
    "v74_component_ids", "v74_edge_ids", "v74_component_topologies",
    "v74_component_microrecords_de", "v74_line_translation_de",
    "v74_word_delta", "v74_status",
]
SPAN_EXTRA = ["v74_selected_gloss_de", "v74_byte_identical", "v74_component_change", "v74_status"]


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


def split_ids(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def ordinals(value: str) -> set[int]:
    return {int(item) for item in split_ids(value)}


def ordered_ordinals(values: set[int]) -> str:
    return "|".join(str(value) for value in sorted(values)) if values else "NONE"


def edge_number(edge_id: str) -> int:
    return int(edge_id[1:])


def component_number(component_id: str) -> int:
    return int(component_id[1:])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def exact_node_components(definitions: Mapping[str, Mapping[str, object]]) -> set[frozenset[str]]:
    """Connect edges only through identical occurrence nodes at one locus."""
    parent = {edge_id: edge_id for edge_id in definitions}

    def find(edge_id: str) -> str:
        while parent[edge_id] != edge_id:
            parent[edge_id] = parent[parent[edge_id]]
            edge_id = parent[edge_id]
        return edge_id

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    edge_ids = sorted(definitions)
    for i, left in enumerate(edge_ids):
        for right in edge_ids[i + 1:]:
            if (
                definitions[left]["locus"] == definitions[right]["locus"]
                and set(definitions[left]["nodes"]) & set(definitions[right]["nodes"])
            ):
                union(left, right)
    groups: dict[str, set[str]] = defaultdict(set)
    for edge_id in edge_ids:
        groups[find(edge_id)].add(edge_id)
    return {frozenset(group) for group in groups.values()}


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    spec_fields, new_specs = read_tsv(SPEC)
    assert spec_fields == SPEC_FIELDS
    assert [row["component_id"] for row in new_specs] == ["M008", "M009"]

    prior697 = json.loads(G697_RESULT.read_text(encoding="utf-8"))
    prior700 = json.loads(G700_RESULT.read_text(encoding="utf-8"))
    assert prior697["status"].startswith("PASS_V70_")
    assert prior697["composition"]["microrecords"] == 7
    assert prior697["composition"]["edges_covered_exactly_once"] == 9
    assert prior700["status"].startswith("PASS_V73_")
    assert prior700["decision"]["cumulative_relation_edges"] == 11
    assert prior700["decision"]["new_edge_id"] == "C011"

    _, g696_edges = read_tsv(G696_EDGES)
    _, g696_rivals = read_tsv(G696_RIVALS)
    _, g696_refs = read_tsv(G696_REFS)
    micro_fields, old_micro = read_tsv(G697_MICRO)
    coverage_fields, old_coverage = read_tsv(G697_COVERAGE)
    role_fields, old_roles = read_tsv(G697_ROLES)
    register_fields, register = read_tsv(G700_REGISTER)
    _, c010_rows = read_tsv(G699_EDGE)
    _, c011_rows = read_tsv(G700_EDGE)
    _, c011_contrasts = read_tsv(G700_CONTRASTS)
    _, c011_controls = read_tsv(G700_CONTROLS)
    token_fields, base_tokens = read_tsv(G700_TOKENS)
    line_fields, base_lines = read_tsv(G700_LINES)
    span_fields, base_spans = read_tsv(G700_SPANS)
    assert len(g696_edges) == 9 and len(g696_rivals) == 17 and len(g696_refs) == 27
    assert all(row["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED" for row in g696_rivals)
    assert Counter(row["decision"] for row in g696_refs) == {
        "ADMITTED_STRONG_EDGE": 5, "ADMITTED_WORKING_EDGE": 1,
        "EXACT_NOMINAL_REFERENCE": 1, "HOLD_OBJECT_RIVAL": 7,
        "INHERITED_NOMINAL_BINDING": 1, "PROCESS_SCOPE_ONLY": 1,
        "SELF_CONTAINED_INTRATOKEN": 1, "STRUCTURAL_SEQUENCE_ONLY": 3,
        "UNRESOLVED_LINE_INITIAL": 5, "UNRESOLVED_LOCAL_RIVAL": 2,
    }
    assert len(old_micro) == 7 and len(old_coverage) == 9 and len(old_roles) == 19
    assert len(register) == 11 and [row["edge_id"] for row in register] == [f"C{i:03d}" for i in range(1, 12)]
    assert len(base_tokens) == 479 and len(base_lines) == 51 and len(base_spans) == 3
    assert len({row["page"] for row in base_tokens}) == 36
    assert all(not row["page"].lower().startswith("f84") for row in base_tokens + base_lines)
    assert all(not row["locus"].lower().startswith("f84") for row in base_spans)

    c010, c011 = one(c010_rows, edge_id="C010"), one(c011_rows, edge_id="C011")
    assert c010["excluded_ordinals"] == "2" and c010["portability"] == "OCCURRENCE_BOUND_ONLY"
    assert c011["edge_node_ordinals"] == "4|6" and c011["checkpoint_ordinals"] == "5"
    assert c011["structural_closure_ordinals"] == "7" and c011["excluded_ordinals"] == "3|5|8"
    assert {row["token_ordinal"] for row in c011_controls} == {"3", "5", "7", "8"}
    assert {row["decision"] for row in c011_contrasts} == {"ADMIT_C011_OCCURRENCE_BOUND", "KEEP_HELD_MATERIAL_COMPETITOR"}
    for row in g696_edges:
        covered = one(old_coverage, edge_id=row["edge_id"])
        assert covered["locus"] == row["locus"]
        assert covered["support_tier"] == row["support_tier"]
        assert covered["relation_class"] == row["relation_class"]
        assert covered["target_action_ordinal"] == row["target_action_ordinal"]

    edge_defs: dict[str, dict[str, object]] = {}
    for row in old_coverage:
        edge_defs[row["edge_id"]] = {
            "locus": row["locus"], "nodes": ordinals(row["node_ordinals"]),
            "support_tier": row["support_tier"], "relation_class": row["relation_class"],
            "target_action_ordinal": row["target_action_ordinal"], "origin": "GDT697_INHERITED",
        }
    edge_defs["C010"] = {
        "locus": c010["locus"], "nodes": {1, 3}, "support_tier": c010["support_tier"],
        "relation_class": c010["relation_class"], "target_action_ordinal": c010["target_action_ordinal"],
        "origin": "GDT699_INHERITED",
    }
    edge_defs["C011"] = {
        "locus": c011["locus"], "nodes": ordinals(c011["edge_node_ordinals"]),
        "support_tier": c011["support_tier"], "relation_class": c011["relation_class"],
        "target_action_ordinal": c011["target_action_ordinal"], "origin": "GDT700_INHERITED",
    }
    assert set(edge_defs) == {f"C{i:03d}" for i in range(1, 12)}
    for edge_id, definition in edge_defs.items():
        reg = one(register, edge_id=edge_id)
        assert reg["locus"] == definition["locus"]
        assert reg["support_tier"] == definition["support_tier"]
        assert reg["relation_class"] == definition["relation_class"]
        assert reg["target_action_ordinal"] == definition["target_action_ordinal"]

    # Connectedness is purely the intersection graph of exact occurrence nodes
    # inside one locus. Hull-only and render-only positions never join edges.
    component_sets = exact_node_components(edge_defs)
    synthetic = {
        "S1": {"locus": "same", "nodes": {1, 2}},
        "S2": {"locus": "same", "nodes": {4, 5}},
        "S3": {"locus": "same", "nodes": {2, 3}},
    }
    assert exact_node_components(synthetic) == {frozenset({"S1", "S3"}), frozenset({"S2"})}
    expected_map = {
        "M001": frozenset({"C009"}), "M002": frozenset({"C001"}),
        "M003": frozenset({"C002"}), "M004": frozenset({"C003"}),
        "M005": frozenset({"C005"}), "M006": frozenset({"C004", "C008"}),
        "M007": frozenset({"C006", "C007"}), "M008": frozenset({"C010"}),
        "M009": frozenset({"C011"}),
    }
    assert component_sets == set(expected_map.values()) and len(component_sets) == 9

    token_by_position = {(row["locus"], int(row["token_ordinal"])): row for row in base_tokens}
    components: list[dict[str, object]] = []
    old_micro_by_id = {row["microrecord_id"]: row for row in old_micro}
    coverage_by_component: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old_coverage:
        coverage_by_component[row["microrecord_id"]].append(row)

    for component_id in [f"M{i:03d}" for i in range(1, 8)]:
        row = old_micro_by_id[component_id]
        covered = coverage_by_component[component_id]
        nodes = set().union(*(ordinals(edge["node_ordinals"]) for edge in covered))
        node_counts = Counter(value for edge in covered for value in ordinals(edge["node_ordinals"]))
        shared = {value for value, count in node_counts.items() if count > 1}
        assert frozenset(row["edge_ids"].split("|")) == expected_map[component_id]
        assert int(row["window_token_count"]) == int(row["window_end_ordinal"]) - int(row["window_start_ordinal"]) + 1
        assert min(nodes) == int(row["window_start_ordinal"]) and max(nodes) == int(row["window_end_ordinal"])
        assert nodes == set(range(min(nodes), max(nodes) + 1))
        components.append({
            "component_id": component_id, "locus": row["locus"], "edge_ids": row["edge_ids"],
            "edge_count": row["edge_count"], "edge_node_ordinals": ordered_ordinals(nodes),
            "edge_node_count": len(nodes), "shared_edge_node_ordinals": ordered_ordinals(shared),
            "edge_hull_start": row["window_start_ordinal"], "edge_hull_end": row["window_end_ordinal"],
            "edge_hull_position_count": row["window_token_count"], "hull_only_ordinals": "NONE",
            "render_window_start": row["window_start_ordinal"], "render_window_end": row["window_end_ordinal"],
            "render_only_structural_ordinals": "NONE", "render_window_token_count": row["window_token_count"],
            "topology": row["topology"], "action_ordinals": row["action_ordinals"],
            "support_profile": row["support_profile"], "expected_surfaces": row["expected_surfaces"],
            "observed_surfaces": row["observed_surfaces"], "microrecord_de": row["microrecord_de"],
            "component_basis": row["composition_basis"], "boundary_note_de": row["boundary_note_de"],
            "forbidden_inference": row["forbidden_inference"], "final_result_status": row["final_result_status"],
            "origin": "GDT697_INHERITED_EXACT", "edge_delta": 0, "word_delta": 0, "status": STATUS,
        })

    for spec in new_specs:
        start, end = int(spec["render_window_start"]), int(spec["render_window_end"])
        observed = "|".join(token_by_position[(spec["locus"], ordinal)]["surface"] for ordinal in range(start, end + 1))
        assert observed == spec["expected_surfaces"]
        nodes = ordinals(spec["edge_node_ordinals"])
        hull_only = ordinals(spec["hull_only_ordinals"])
        structural = ordinals(spec["render_only_structural_ordinals"])
        assert nodes.isdisjoint(hull_only | structural) and hull_only.isdisjoint(structural)
        hull = set(range(int(spec["edge_hull_start"]), int(spec["edge_hull_end"]) + 1))
        assert hull == nodes | hull_only
        assert structural.isdisjoint(hull)
        assert frozenset(spec["edge_ids"].split("|")) == expected_map[spec["component_id"]]
        if spec["component_id"] == "M008":
            assert spec["microrecord_de"] == c010["working_reading_de"]
        else:
            assert spec["microrecord_de"] == c011["working_microrecord_de"]
        components.append({
            **spec, "edge_count": len(split_ids(spec["edge_ids"])), "edge_node_count": len(nodes),
            "shared_edge_node_ordinals": "NONE",
            "edge_hull_position_count": int(spec["edge_hull_end"]) - int(spec["edge_hull_start"]) + 1,
            "render_window_token_count": end - start + 1, "observed_surfaces": observed,
            "origin": "GDT699_EXACT" if spec["component_id"] == "M008" else "GDT700_EXACT",
            "edge_delta": 0, "word_delta": 0, "status": STATUS,
        })
    components.sort(key=lambda row: component_number(str(row["component_id"])))
    assert [row["component_id"] for row in components] == [f"M{i:03d}" for i in range(1, 10)]
    assert sum(int(row["edge_count"]) for row in components) == 11
    assert sum(int(row["edge_node_count"]) for row in components) == 23
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 25
    assert sum(len(definition["nodes"]) for definition in edge_defs.values()) == 25
    assert sum(len(ordinals(str(row["hull_only_ordinals"]))) for row in components) == 2
    assert sum(len(ordinals(str(row["render_only_structural_ordinals"]))) for row in components) == 1
    assert sum(int(row["render_window_token_count"]) for row in components) == 26
    seen_component_nodes: set[tuple[str, int]] = set()
    for component in components:
        local_nodes = {(str(component["locus"]), value) for value in ordinals(str(component["edge_node_ordinals"]))}
        assert seen_component_nodes.isdisjoint(local_nodes)
        seen_component_nodes |= local_nodes
    write_tsv(COMPONENTS_OUT, components, COMPONENT_FIELDS)

    membership_rows: list[dict[str, object]] = []
    for component in components:
        component_edges = split_ids(str(component["edge_ids"]))
        for edge_id in component_edges:
            definition = edge_defs[edge_id]
            membership_rows.append({
                "edge_id": edge_id, "component_id": component["component_id"],
                "locus": definition["locus"], "support_tier": definition["support_tier"],
                "relation_class": definition["relation_class"],
                "edge_node_ordinals": ordered_ordinals(definition["nodes"]),
                "target_action_ordinal": definition["target_action_ordinal"],
                "component_edge_count": component["edge_count"],
                "component_topology": component["topology"],
                "shared_edge_node_ordinals": component["shared_edge_node_ordinals"],
                "origin": definition["origin"], "v74_change": "NONE", "status": STATUS,
            })
    membership_rows.sort(key=lambda row: edge_number(str(row["edge_id"])))
    assert [row["edge_id"] for row in membership_rows] == [f"C{i:03d}" for i in range(1, 12)]
    write_tsv(MEMBERSHIP_OUT, membership_rows, MEMBERSHIP_FIELDS)

    components_by_id = {str(row["component_id"]): row for row in components}
    position_rows: list[dict[str, object]] = []
    for row in old_roles:
        output_role = "WRITTEN_SERIAL_ACTION_OUTPUT_BRIDGE" if row["is_action_output_bridge"] == "1" else "NONE"
        position_rows.append({
            "page": row["page"], "locus": row["locus"], "token_ordinal": row["token_ordinal"],
            "surface": row["surface"], "token_gloss_de": row["v69_token_gloss_de"],
            "component_id": row["microrecord_id"], "render_position": row["window_position"],
            "render_size": row["window_size"], "component_role": row["role_trace"],
            "edge_ids": row["edge_ids"], "source_edge_ids": row["source_edge_ids"],
            "reference_edge_ids": row["reference_edge_ids"], "target_edge_ids": row["target_edge_ids"],
            "membership_class": "EDGE_NODE", "is_edge_node": 1, "is_hull_only": 0,
            "is_render_only_structural": 0, "is_action_target": row["is_action_target"],
            "is_shared_edge_node": row["is_shared_node"], "action_output_role": output_role,
            "component_microrecord_de": row["v70_microrecord_de"], "word_delta": 0, "status": STATUS,
        })

    new_position_specs = {
        ("M008", 1): ("DONOR_MATERIAL:C010", "C010", "C010", "NONE", "NONE", "EDGE_NODE", 0, "NONE"),
        ("M008", 2): ("UNBOUND_QUANTITY_REGISTER_HULL_ONLY", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", 0, "NONE"),
        ("M008", 3): ("REFERENCE:C010|TARGET_ACTION:C010", "C010", "NONE", "C010", "C010", "EDGE_NODE", 1, "NONE"),
        ("M009", 4): ("INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:C011", "C011", "C011", "NONE", "NONE", "EDGE_NODE", 0, "INFERRED_C011_SOURCE_RESULT"),
        ("M009", 5): ("EXACT_STATE_CHECKPOINT_HULL_ONLY:C011", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", 0, "NONE"),
        ("M009", 6): ("REFERENCE:C011|TARGET_ACTION:C011", "C011", "NONE", "C011", "C011", "EDGE_NODE", 1, "NONE"),
        ("M009", 7): ("FREE_DY_STRUCTURAL_CLOSURE:C011", "NONE", "NONE", "NONE", "NONE", "RENDER_ONLY_STRUCTURAL", 0, "NONE"),
    }
    for component_id in ("M008", "M009"):
        component = components_by_id[component_id]
        start, end = int(component["render_window_start"]), int(component["render_window_end"])
        for ordinal in range(start, end + 1):
            source = token_by_position[(str(component["locus"]), ordinal)]
            role, edges, sources, references, targets, member_class, action_target, output_role = new_position_specs[(component_id, ordinal)]
            position_rows.append({
                "page": source["page"], "locus": source["locus"], "token_ordinal": ordinal,
                "surface": source["surface"], "token_gloss_de": source["v73_token_gloss_de"],
                "component_id": component_id, "render_position": ordinal - start + 1,
                "render_size": end - start + 1, "component_role": role, "edge_ids": edges,
                "source_edge_ids": sources, "reference_edge_ids": references,
                "target_edge_ids": targets, "membership_class": member_class,
                "is_edge_node": int(member_class == "EDGE_NODE"),
                "is_hull_only": int(member_class == "HULL_ONLY"),
                "is_render_only_structural": int(member_class == "RENDER_ONLY_STRUCTURAL"),
                "is_action_target": action_target, "is_shared_edge_node": 0,
                "action_output_role": output_role,
                "component_microrecord_de": component["microrecord_de"], "word_delta": 0, "status": STATUS,
            })
    position_rows.sort(key=lambda row: (component_number(str(row["component_id"])), int(row["render_position"])))
    assert len(position_rows) == 26 and len({(row["locus"], row["token_ordinal"]) for row in position_rows}) == 26
    assert sum(int(row["is_edge_node"]) for row in position_rows) == 23
    assert sum(int(row["is_hull_only"]) for row in position_rows) == 2
    assert sum(int(row["is_render_only_structural"]) for row in position_rows) == 1
    assert sum(int(row["is_action_target"]) for row in position_rows) == 11
    assert sum(int(row["is_shared_edge_node"]) for row in position_rows) == 2
    write_tsv(POSITIONS_OUT, position_rows, POSITION_FIELDS)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_rows: list[dict[str, object]] = []
    topology_notes = {
        "SINGLE_EDGE": "five unchanged GDT697 one-operation components",
        "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT": "two actions share one written destination; no serial output carry",
        "SERIAL_ACTION_OUTPUT_CHAIN": "the written first action result is consumed by the second action",
        "SINGLE_EDGE_WITH_UNBOUND_QUANTITY_HULL": "C010 skips one unbound quantity register inside its hull",
        "SINGLE_EDGE_ACROSS_EXACT_STATE_CHECKPOINT": "C011 skips one exact state checkpoint inside its hull",
    }
    for value in sorted(topology_groups):
        ids = topology_groups[value]
        topology_rows.append({"dimension": "TOPOLOGY", "value": value, "count": len(ids), "component_ids": "|".join(ids), "note": topology_notes[value], "status": STATUS})
    for value in sorted(support_groups):
        ids = support_groups[value]
        topology_rows.append({"dimension": "SUPPORT_PROFILE", "value": value, "count": len(ids), "component_ids": "|".join(ids), "note": "inherited edge tiers remain visible and are not averaged", "status": STATUS})
    topology_rows.extend([
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 23, "component_ids": "M001|M002|M003|M004|M005|M006|M007|M008|M009", "note": "unique occurrence nodes in the nine disjoint locus components", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 2, "component_ids": "M008|M009", "note": "exactly C010#2 and C011#5", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 1, "component_ids": "M009", "note": "free DY at f26r.2#7", "status": STATUS},
        {"dimension": "RESULT_STATUS", "value": "NAMED_INTERMEDIATE_OUTPUT", "count": 1, "component_ids": "M007", "note": "qodar#4 remains the sole written serial intermediate", "status": STATUS},
        {"dimension": "SOURCE_FINAL_STATUS", "value": "UNNAMED_NO_OUTGOING_EDGE", "count": 8, "component_ids": "M001|M002|M003|M004|M005|M006|M007|M009", "note": "explicit inherited final status", "status": STATUS},
        {"dimension": "SOURCE_FINAL_STATUS", "value": "NOT_DECLARED_IN_V72", "count": 1, "component_ids": "M008", "note": "C010 has no source final-result-status field", "status": STATUS},
        {"dimension": "RESULT_STATUS", "value": "NAMED_FINAL_RESULT", "count": 0, "component_ids": "NONE", "note": "no target action has an admitted outgoing named-result edge", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    positions_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in position_rows}
    token_overlay: list[dict[str, object]] = []
    for row in base_tokens:
        position = positions_by_key.get((row["locus"], int(row["token_ordinal"])))
        token_overlay.append({
            **row,
            "v74_component_id": position["component_id"] if position else "NONE",
            "v74_component_position": position["render_position"] if position else "NONE",
            "v74_component_role": position["component_role"] if position else "NONE",
            "v74_component_edge_ids": position["edge_ids"] if position else "NONE",
            "v74_component_membership_class": position["membership_class"] if position else "NONE",
            "v74_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v74_token_gloss_de": row["v73_token_gloss_de"], "v74_word_delta": 0, "v74_status": STATUS,
        })
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    components_by_locus = {str(row["locus"]): row for row in components}
    assert len(components_by_locus) == 9
    line_overlay: list[dict[str, object]] = []
    for row in base_lines:
        component = components_by_locus.get(row["locus"])
        line_overlay.append({
            **row,
            "v74_component_ids": component["component_id"] if component else "NONE",
            "v74_edge_ids": component["edge_ids"] if component else "NONE",
            "v74_component_topologies": component["topology"] if component else "NONE",
            "v74_component_microrecords_de": component["microrecord_de"] if component else "NONE",
            "v74_line_translation_de": row["v73_clause_translation_de"],
            "v74_word_delta": 0, "v74_status": STATUS,
        })
    assert sum(row["v74_component_ids"] != "NONE" for row in line_overlay) == 9
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{
        **row, "v74_selected_gloss_de": row["v73_selected_gloss_de"],
        "v74_byte_identical": 1, "v74_component_change": "NONE", "v74_status": STATUS,
    } for row in base_spans]
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT701 — V74 cumulative relation components", "", f"Status: `{STATUS}`", "",
        "## Nine complete practical components", "",
        "| component | locus | edges | support | topology | practical microrecord |", "|---|---|---|---|---|---|",
    ]
    for row in components:
        reader.append(f"| {row['component_id']} | `{row['locus']}` | {md(str(row['edge_ids']))} | {row['support_profile']} | {row['topology']} | {md(str(row['microrecord_de']))} |")
    reader.extend([
        "", "## Graph accounting", "",
        "- 11 inherited edges form exactly 9 connected components on exact locus+ordinal nodes.",
        "- The components contain 23 unique edge nodes and 25 edge-node incidences; only f80v.35#3 and f86v6.25#4 are shared nodes.",
        "- C010#2 and C011#5 lie inside their convex hulls but are not edge nodes. C011#7 is render-only structural closure outside hull 4–6.",
        "- M007 remains the sole written serial intermediate. No component has a named final action result or an admitted outgoing final-result edge.",
        "- M008 preserves AIIN as an unbound quantity register. M009 preserves the heated-Krautdroge identity as an explicit B-hypothesis, not a written output word.",
        "- All 479 token glosses, 51 line translations and 3 bound spans are byte-identical; no edge, word meaning or page is added.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")

    ARTIFACT_README.write_text(
        "# GDT701 artifacts\n\n"
        "- `V74_9_CONNECTED_COMPONENTS.tsv`: complete cumulative practical component atlas.\n"
        "- `V74_11_EDGE_COMPONENT_MEMBERSHIP.tsv`: one component assignment for every C001-C011 edge.\n"
        "- `V74_26_COMPONENT_POSITION_ROLES.tsv`: 23 edge nodes, two hull-only positions and one render-only structural closure.\n"
        "- `V74_COMPONENT_TOPOLOGY_CENSUS.tsv`: topology, support, position and result census.\n"
        "- `V74_479_TOKEN_COMPONENT_OVERLAY.tsv`, `V74_51_LINE_COMPONENT_OVERLAY.tsv`, `V74_3_BOUND_SPAN_FREEZE.tsv`: unchanged V73 reader plus separate V74 metadata.\n"
        "- `GDT701_V74_CUMULATIVE_RELATION_COMPONENT_READER.md`: nine concrete microrecords.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    generated = [COMPONENTS_OUT, MEMBERSHIP_OUT, POSITIONS_OUT, TOPOLOGY_OUT, TOKENS_OUT, LINES_OUT, SPANS_OUT, READER_OUT, ARTIFACT_README]
    inputs = [SPEC, G696_EDGES, G696_RIVALS, G696_REFS, G697_RESULT, G697_MICRO, G697_COVERAGE, G697_ROLES, G699_EDGE, G700_RESULT, G700_REGISTER, G700_EDGE, G700_CONTRASTS, G700_CONTROLS, G700_TOKENS, G700_LINES, G700_SPANS, Path(__file__).resolve()]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM_CEILING,
        "basis": {"pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51, "source_clauses": 175, "bound_spans": 3, "relation_edges": 11, "held_rival_rows": 17, "reference_rows": 27, "connected_components": 9, "minimal_hull_positions": 25, "render_positions": 26, "edge_nodes": 23, "edge_node_incidences": 25, "hull_only_positions": 2, "render_only_structural_positions": 1, "f84_access": 0, "f84r_access": 0},
        "topology": {"generic_single_edge_components": 7, "plain_single_edge_components": 5, "common_destination_fanouts": 1, "serial_action_output_chains": 1, "unbound_quantity_hull_components": 1, "exact_state_checkpoint_components": 1, "named_intermediate_outputs": 1, "named_final_results": 0},
        "decision": {"component_ids": [f"M{i:03d}" for i in range(1, 10)], "component_join_rule": "IDENTICAL_LOCUS_ORDINAL_EDGE_NODE_ONLY", "same_locus_without_shared_node_join": False, "new_edges": 0, "changed_edges": 0, "rival_changes": 0, "reference_changes": 0, "new_participant_identities": 0, "changed_participant_identities": 0, "c010_hull_only": "f86v5.24#2", "c011_hull_only": "f26r.2#5", "c011_render_only_structural": "f26r.2#7", "shared_edge_nodes": ["f80v.35#3", "f86v6.25#4"]},
        "freeze": {"token_glosses_byte_identical": 479, "line_translations_byte_identical": 51, "bound_spans_byte_identical": 3, "new_word_meanings": 0, "changed_word_meanings": 0, "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0},
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated}, "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "edges": 11, "components": 9, "edge_nodes": 23, "hull_only": 2, "structural": 1, "new_edges": 0, "new_word_meanings": 0}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
