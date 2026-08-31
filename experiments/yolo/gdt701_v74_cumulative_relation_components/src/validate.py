#!/usr/bin/env python3
"""Independent fail-closed validation for GDT701.

The builder is never imported or inspected.  Its externally declared digest
is checked as bytes, while every graph and freeze assertion is reconstructed
from the frozen primary inputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
STATUS = "PASS_V74_11_EDGES__9_CONNECTED_COMPONENTS__23_EDGE_NODES_2_HULL_ONLY_1_STRUCTURAL__ZERO_EDGE_WORD_DELTA"
QUESTION = (
    "Do the complete current C001-C011 relation edges form exactly nine occurrence-node "
    "connected components whose practical microrecords can be published without adding "
    "an edge, participant identity, result name or word meaning?"
)
CLAIM = (
    "V74 compiles the eleven existing occurrence-bound relation edges into nine exact "
    "graph components and nine practical German microrecords. It adds no relation or "
    "meaning. C010#2 and C011#5 are hull-only rather than edge nodes; C011#7 is "
    "render-only structural closure. The C011 heated-herb identity remains a B-tier "
    "hypothesis, and no final action result is named. This is an exploratory working "
    "edition, not plaintext, a portable grammar or historical decipherment."
)
NEXT_GAP = (
    "Preserve the nine-component atlas. Next inventory the exact immediate right "
    "contexts of all eleven target actions for an explicitly written result label, "
    "without using adjacency, fluent recipe order or a default output carry; add no "
    "page or word meaning."
)
RUN_REL = "experiments/yolo/gdt701_v74_cumulative_relation_components/src/run.py"
RUN_SHA = "326e3466e2b05b0f870a10b75f1527da26d9c21b15b8f0f7b21a96f5c3d1b2a6"
SPEC = SRC / "V74_2_NEW_COMPONENT_SPECS.tsv"
SPEC_SHA = "d14c737f6501db2159c439dc2a468154c61e798bd806ede1769382e464a4330a"

INPUT_HASHES = {
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_17_RELATION_RIVALS.tsv": "8c97948f25f94f59e141b65230de23d2fcf75de0da926e20caaa46507d7916dd",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_27_REFERENCE_CENSUS.tsv": "f289027471897b4605b0821c6378985ff4d1fc03b37868feaa6e24704b95f6d2",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_9_LOCAL_ACTION_EDGES.tsv": "06a5b402b2ddf3d956e4031f753e63e1ff32290ca522f5a8e72b8410b88af227",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/RESULT.json": "0d85be4ad35b1643eb619040f9da7a081fdd8839db73a68f3b2909fb2901bcaf",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_19_WINDOW_TOKEN_ROLES.tsv": "0cbb1c67603d0df7f207cc807b3b6a78c497fcb28bf8cea7742eaefe3907bcf2",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_7_EXACT_MICRORECORDS.tsv": "c4b8b8e87e729b70da6f43115f666297b441035cebb210bdc7d37e59e52bcdcc",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv": "02be802b569c39354f5bff77786cc2143e8d9e344bae09d4c8d14562f37a6aac",
    "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_1_NEW_LOCAL_HEAT_EDGE.tsv": "c6fafffcc1f248dd40e212dfcb196c65e1e60e6d4fa9df6cca6d0d3785c7895a",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/RESULT.json": "abfdc1c54f19f89738cea23dbd07fecf07e7c7245da02bca7c57f969170352f9",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_11_RELATION_EDGE_REGISTER.tsv": "eb987eb285edca11f1c05c20f93ba702d9d21d59b91887646f1eae3251cb7ed2",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_1_NEW_LOCAL_CHECKPOINT_EDGE.tsv": "36ebc55da7b00a5173e75da4a1304884e82f000337dc7ffac41001b5dd315c39",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_2_DEICTIC_ANA_CONTRASTS.tsv": "8668b88332fa12f56f1f9811ba294cee7dfd6793eb618d127648d58a61a8c634",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_3_BOUND_SPAN_FREEZE.tsv": "17a7c501274c5fa2bb4c355e6ae39560165f3e3d227adbe4ee50eaa4f11ef60d",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_479_TOKEN_RELATION_OVERLAY.tsv": "adf7c0300e011315aae74eae121eafc9bdd09ed8707fe44b2dfd2fdc8eac3598",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_4_C011_BOUNDARY_CONTROLS.tsv": "690506b2c74528df4c36119347539c28952c4e1a0d1f5a293150c1fdbf6cf9ca",
    "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/artifacts/V73_51_LINE_RELATION_OVERLAY.tsv": "f255a17a969a43e4b10afbc88e77782cbe697ea1422bd3f9984404046f15cda7",
}


def ipath(fragment: str) -> Path:
    return ROOT / next(path for path in INPUT_HASHES if fragment in path)


RIVALS, REFS, OLD_EDGES = ipath("V69_17_"), ipath("V69_27_"), ipath("V69_9_")
G697_RESULT, OLD_ROLES = ipath("gdt697_v69_exact_relation_microrecords/artifacts/RESULT"), ipath("V70_19_")
OLD_MICROS, COVERAGE = ipath("V70_7_"), ipath("V70_9_")
C010, G700_RESULT = ipath("V72_1_"), ipath("gdt700_v73_action_output_state_checkpoint_carry/artifacts/RESULT")
REGISTER, C011 = ipath("V73_11_"), ipath("V73_1_")
CONTRASTS, PRIOR_SPANS = ipath("V73_2_"), ipath("V73_3_")
PRIOR_TOKENS, CONTROLS, PRIOR_LINES = ipath("V73_479_"), ipath("V73_4_"), ipath("V73_51_")

COMPONENTS = ART / "V74_9_CONNECTED_COMPONENTS.tsv"
MEMBERSHIP = ART / "V74_11_EDGE_COMPONENT_MEMBERSHIP.tsv"
POSITIONS = ART / "V74_26_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY = ART / "V74_COMPONENT_TOPOLOGY_CENSUS.tsv"
TOKENS = ART / "V74_479_TOKEN_COMPONENT_OVERLAY.tsv"
LINES = ART / "V74_51_LINE_COMPONENT_OVERLAY.tsv"
SPANS = ART / "V74_3_BOUND_SPAN_FREEZE.tsv"
READER = ART / "GDT701_V74_CUMULATIVE_RELATION_COMPONENT_READER.md"
RESULT = ART / "RESULT.json"
TOKEN_EXTRA = ["v74_component_id", "v74_component_position", "v74_component_role", "v74_component_edge_ids", "v74_component_membership_class", "v74_component_microrecord_de", "v74_token_gloss_de", "v74_word_delta", "v74_status"]
LINE_EXTRA = ["v74_component_ids", "v74_edge_ids", "v74_component_topologies", "v74_component_microrecords_de", "v74_line_translation_de", "v74_word_delta", "v74_status"]
SPAN_EXTRA = ["v74_selected_gloss_de", "v74_byte_identical", "v74_component_change", "v74_status"]
GENERATED = {path.name: path for path in [READER, ART / "README.md", MEMBERSHIP, POSITIONS, SPANS, TOKENS, LINES, COMPONENTS, TOPOLOGY]}
PREFIX = "experiments/yolo/gdt701_v74_cumulative_relation_components/"
EXPECTED_OUTPUTS = {PREFIX + name for name in [
    "README.md", "METHOD.md", "REPORT.md", "src/V74_2_NEW_COMPONENT_SPECS.tsv", "src/run.py", "src/validate.py",
    "artifacts/GDT701_V74_CUMULATIVE_RELATION_COMPONENT_READER.md", "artifacts/README.md", "artifacts/RESULT.json",
    "artifacts/V74_11_EDGE_COMPONENT_MEMBERSHIP.tsv", "artifacts/V74_26_COMPONENT_POSITION_ROLES.tsv",
    "artifacts/V74_3_BOUND_SPAN_FREEZE.tsv", "artifacts/V74_479_TOKEN_COMPONENT_OVERLAY.tsv",
    "artifacts/V74_51_LINE_COMPONENT_OVERLAY.tsv", "artifacts/V74_9_CONNECTED_COMPONENTS.tsv",
    "artifacts/V74_COMPONENT_TOPOLOGY_CENSUS.tsv", "artifacts/VALIDATION.json",
]}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, value: object, name: str) -> None:
        passed = bool(value)
        self.rows.append({"check": name, "pass": int(passed)})
        if not passed:
            raise AssertionError(name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    if not fields or len(fields) != len(set(fields)):
        raise AssertionError(f"invalid TSV header: {path}")
    if any(None in row or set(row) != set(fields) or any(value is None for value in row.values()) for row in rows):
        raise AssertionError(f"malformed TSV: {path}")
    return fields, rows


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"expected one row for {wanted}, got {len(hits)}")
    return hits[0]


def ordinals(value: str) -> set[int]:
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


def component_partition(edges: Mapping[str, Mapping[str, object]]) -> list[set[str]]:
    ids = sorted(edges, key=lambda edge_id: int(edge_id[1:]) if edge_id[1:].isdigit() else edge_id)
    parent = {edge_id: edge_id for edge_id in ids}

    def find(edge_id: str) -> str:
        while parent[edge_id] != edge_id:
            parent[edge_id] = parent[parent[edge_id]]
            edge_id = parent[edge_id]
        return edge_id

    for index, left in enumerate(ids):
        for right in ids[index + 1:]:
            if edges[left]["locus"] == edges[right]["locus"] and set(edges[left]["nodes"]) & set(edges[right]["nodes"]):
                a, b = find(left), find(right)
                if a != b:
                    parent[b] = a
    groups: dict[str, set[str]] = defaultdict(set)
    for edge_id in ids:
        groups[find(edge_id)].add(edge_id)
    return sorted(groups.values(), key=lambda group: min(int(edge_id[1:]) for edge_id in group if edge_id[1:].isdigit()))


def projection(source_fields: Sequence[str], source_rows: Sequence[Mapping[str, str]], out_fields: Sequence[str], out_rows: Sequence[Mapping[str, str]], extra: Sequence[str]) -> bool:
    return list(out_fields) == [*source_fields, *extra] and len(source_rows) == len(out_rows) and all(all(out[field] == source[field] for field in source_fields) for source, out in zip(source_rows, out_rows))


def main() -> int:
    audit = Audit()
    audit.check(sha256(ROOT / RUN_REL) == RUN_SHA, "externally declared builder digest exact")
    audit.check(sha256(SPEC) == SPEC_SHA, "new-component specification hash exact")
    for relative, expected in INPUT_HASHES.items():
        audit.check(sha256(ROOT / relative) == expected, f"upstream hash exact {Path(relative).name}")

    _, rivals = read_tsv(RIVALS)
    _, references = read_tsv(REFS)
    audit.check(len(rivals) == 17 and [row["rival_id"] for row in rivals] == [*[f"H{i:03d}" for i in range(1, 8)], *[f"P{i:03d}" for i in range(1, 11)]] and all(row["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED" for row in rivals), "all 17 rivals remain held")
    audit.check(len(references) == 27 and [row["reference_id"] for row in references] == [f"R{i:03d}" for i in range(1, 28)], "all 27 references retained in exact order")

    prior697 = json.loads(G697_RESULT.read_text(encoding="utf-8"))
    prior700 = json.loads(G700_RESULT.read_text(encoding="utf-8"))
    audit.check(prior697["status"].startswith("PASS_V70_7_EXACT_MICRORECORDS__9_EDGE_COVERAGE") and prior697["basis"]["v69_admitted_edges"] == 9 and prior697["composition"]["microrecords"] == 7, "GDT697 seven-record nine-edge scope exact")
    audit.check(prior700["status"].startswith("PASS_V73_10_ANA_WINDOWS") and prior700["basis"]["token_positions"] == 479 and prior700["basis"]["lines"] == 51 and prior700["basis"]["bound_spans"] == 3 and prior700["decision"]["cumulative_relation_edges"] == 11, "GDT700 cumulative edge and freeze scope exact")

    _, coverage = read_tsv(COVERAGE)
    _, c10rows = read_tsv(C010)
    _, c11rows = read_tsv(C011)
    _, register = read_tsv(REGISTER)
    c10, c11 = c10rows[0], c11rows[0]
    audit.check(len(coverage) == 9 and [row["edge_id"] for row in coverage] == [f"C{i:03d}" for i in range(1, 10)], "C001-C009 coverage source exact")
    audit.check(len(c10rows) == len(c11rows) == 1 and c10["edge_id"] == "C010" and c11["edge_id"] == "C011", "C010 and C011 source rows exact")
    audit.check(len(register) == 11 and [row["edge_id"] for row in register] == [f"C{i:03d}" for i in range(1, 12)], "C001-C011 register exact")

    edges: dict[str, dict[str, object]] = {}
    for row in coverage:
        edges[row["edge_id"]] = {
            "locus": row["locus"], "nodes": ordinals(row["node_ordinals"]),
            "target": row["target_action_ordinal"], "tier": row["support_tier"],
            "relation": row["relation_class"], "legacy": row["microrecord_id"],
        }
    edges["C010"] = {
        "locus": c10["locus"],
        "nodes": ordinals(c10["source_ordinals"]) | ordinals(c10["reference_ordinals"]) | {int(c10["target_action_ordinal"])},
        "target": c10["target_action_ordinal"], "tier": c10["support_tier"],
        "relation": c10["relation_class"], "legacy": "M008",
    }
    edges["C011"] = {
        "locus": c11["locus"], "nodes": ordinals(c11["edge_node_ordinals"]),
        "target": c11["target_action_ordinal"], "tier": c11["support_tier"],
        "relation": c11["relation_class"], "legacy": "M009",
    }
    for edge_id, edge in edges.items():
        row = one(register, edge_id=edge_id)
        audit.check(row["locus"] == edge["locus"] and row["target_action_ordinal"] == edge["target"] and row["support_tier"] == edge["tier"] and row["relation_class"] == edge["relation"], f"register geometry and class exact {edge_id}")

    groups = component_partition(edges)
    expected_sets = [
        {"C001"}, {"C002"}, {"C003"}, {"C004", "C008"}, {"C005"},
        {"C006", "C007"}, {"C009"}, {"C010"}, {"C011"},
    ]
    audit.check(groups == expected_sets, "exact nine occurrence-node components")
    audit.check(component_partition({"S001": {"locus": "same.1", "nodes": {1, 2}}, "S002": {"locus": "same.1", "nodes": {3, 4}}}) == [{"S001"}, {"S002"}], "synthetic same-locus adjacent but disjoint edges do not join")

    comp_by_id: dict[str, set[str]] = {}
    for group in groups:
        legacy_ids = {str(edges[edge_id]["legacy"]) for edge_id in group}
        audit.check(len(legacy_ids) == 1, f"component has one source record identity {sorted(group)}")
        comp_by_id[next(iter(legacy_ids))] = group
    audit.check(set(comp_by_id) == {f"M{i:03d}" for i in range(1, 10)}, "M001-M009 component identities exact")
    unique_nodes = {(str(edge["locus"]), ordinal) for edge in edges.values() for ordinal in set(edge["nodes"])}
    incidences = sum(len(set(edge["nodes"])) for edge in edges.values())
    component_hulls = {
        component_id: set(range(min(set().union(*(set(edges[e]["nodes"]) for e in group))), max(set().union(*(set(edges[e]["nodes"]) for e in group))) + 1))
        for component_id, group in comp_by_id.items()
    }
    component_nodes = {component_id: set().union(*(set(edges[e]["nodes"]) for e in group)) for component_id, group in comp_by_id.items()}
    hull_only = {component_id: component_hulls[component_id] - component_nodes[component_id] for component_id in comp_by_id}
    audit.check(len(edges) == 11 and len(groups) == 9 and len(unique_nodes) == 23 and incidences == 25, "11 edges 9 components 23 nodes and 25 incidences")
    audit.check(sum(len(hull) for hull in component_hulls.values()) == 25 and {key: value for key, value in hull_only.items() if value} == {"M008": {2}, "M009": {5}}, "25 hull positions and exactly two hull-only positions")
    shared = []
    for component_id, group in comp_by_id.items():
        counts = Counter(ordinal for edge_id in group for ordinal in set(edges[edge_id]["nodes"]))
        shared.extend((str(edges[next(iter(group))]["locus"]), ordinal) for ordinal, count in counts.items() if count > 1)
    audit.check(sorted(shared) == [("f80v.35", 3), ("f86v6.25", 4)], "only two exact shared edge nodes")

    spec_fields, specs = read_tsv(SPEC)
    component_fields, components = read_tsv(COMPONENTS)
    audit.check(len(specs) == 2 and [row["component_id"] for row in specs] == ["M008", "M009"], "two new component specs exact")
    audit.check(len(components) == 9 and [row["component_id"] for row in components] == [f"M{i:03d}" for i in range(1, 10)], "nine component rows exact")
    _, old_micros = read_tsv(OLD_MICROS)
    audit.check(len(old_micros) == 7 and [row["microrecord_id"] for row in old_micros] == [f"M{i:03d}" for i in range(1, 8)], "seven legacy microrecords exact")
    old_map = {
        "component_id": "microrecord_id", "locus": "locus", "edge_ids": "edge_ids",
        "edge_count": "edge_count", "edge_hull_start": "window_start_ordinal",
        "edge_hull_end": "window_end_ordinal", "edge_hull_position_count": "window_token_count",
        "render_window_start": "window_start_ordinal", "render_window_end": "window_end_ordinal",
        "render_window_token_count": "window_token_count", "topology": "topology",
        "action_ordinals": "action_ordinals", "support_profile": "support_profile",
        "expected_surfaces": "expected_surfaces", "observed_surfaces": "observed_surfaces",
        "microrecord_de": "microrecord_de", "component_basis": "composition_basis",
        "boundary_note_de": "boundary_note_de", "forbidden_inference": "forbidden_inference",
        "final_result_status": "final_result_status",
    }
    for old in old_micros:
        out = one(components, component_id=old["microrecord_id"])
        audit.check(all(out[target] == old[source] for target, source in old_map.items()) and out["edge_node_ordinals"] == "|".join(map(str, sorted(component_nodes[out["component_id"]]))) and out["edge_node_count"] == str(len(component_nodes[out["component_id"]])) and out["hull_only_ordinals"] == out["render_only_structural_ordinals"] == "NONE" and out["origin"] == "GDT697_INHERITED_EXACT" and out["edge_delta"] == out["word_delta"] == "0" and out["status"] == STATUS, f"legacy microrecord unchanged {old['microrecord_id']}")
    for spec in specs:
        out = one(components, component_id=spec["component_id"])
        audit.check(all(out[field] == spec[field] for field in spec_fields) and out["edge_count"] == "1" and out["edge_node_count"] == "2" and out["shared_edge_node_ordinals"] == "NONE" and out["edge_hull_position_count"] == "3" and out["render_window_token_count"] == ("3" if spec["component_id"] == "M008" else "4") and out["observed_surfaces"] == spec["expected_surfaces"] and out["edge_delta"] == out["word_delta"] == "0" and out["status"] == STATUS, f"new component exact {spec['component_id']}")
    audit.check(one(components, component_id="M006")["shared_edge_node_ordinals"] == "3" and one(components, component_id="M007")["shared_edge_node_ordinals"] == "4", "component shared-node fields exact")

    membership_fields, membership = read_tsv(MEMBERSHIP)
    audit.check(len(membership) == 11 and [row["edge_id"] for row in membership] == [f"C{i:03d}" for i in range(1, 12)], "eleven membership rows exact")
    expected_origins = {**{f"C{i:03d}": "GDT697_INHERITED" for i in range(1, 10)}, "C010": "GDT699_INHERITED", "C011": "GDT700_INHERITED"}
    for edge_id, edge in edges.items():
        row = one(membership, edge_id=edge_id)
        component_id = str(edge["legacy"])
        component = one(components, component_id=component_id)
        audit.check(row["component_id"] == component_id and row["locus"] == edge["locus"] and row["support_tier"] == edge["tier"] and row["relation_class"] == edge["relation"] and row["edge_node_ordinals"] == "|".join(map(str, sorted(set(edge["nodes"])))) and row["target_action_ordinal"] == edge["target"] and row["component_edge_count"] == component["edge_count"] and row["component_topology"] == component["topology"] and row["shared_edge_node_ordinals"] == component["shared_edge_node_ordinals"] and row["origin"] == expected_origins[edge_id] and row["v74_change"] == "NONE" and row["status"] == STATUS, f"edge membership independently exact {edge_id}")

    _, old_roles = read_tsv(OLD_ROLES)
    position_fields, positions = read_tsv(POSITIONS)
    audit.check(len(old_roles) == 19 and len(positions) == 26 and len({(row["locus"], row["token_ordinal"]) for row in positions}) == 26, "19 old plus 7 new render positions exact")
    position_index = {(row["locus"], row["token_ordinal"]): row for row in positions}
    for old in old_roles:
        out = position_index[(old["locus"], old["token_ordinal"])]
        audit.check(out["page"] == old["page"] and out["surface"] == old["surface"] and out["token_gloss_de"] == old["v69_token_gloss_de"] and out["component_id"] == old["microrecord_id"] and out["render_position"] == old["window_position"] and out["render_size"] == old["window_size"] and out["component_role"] == old["role_trace"] and out["edge_ids"] == old["edge_ids"] and out["source_edge_ids"] == old["source_edge_ids"] and out["reference_edge_ids"] == old["reference_edge_ids"] and out["target_edge_ids"] == old["target_edge_ids"] and out["membership_class"] == "EDGE_NODE" and out["is_edge_node"] == "1" and out["is_hull_only"] == out["is_render_only_structural"] == "0" and out["is_action_target"] == old["is_action_target"] and out["is_shared_edge_node"] == old["is_shared_node"] and out["component_microrecord_de"] == old["v70_microrecord_de"] and out["word_delta"] == "0" and out["status"] == STATUS, f"legacy position exact {old['locus']}#{old['token_ordinal']}")
        expected_output = "WRITTEN_SERIAL_ACTION_OUTPUT_BRIDGE" if old["is_action_output_bridge"] == "1" else "NONE"
        audit.check(out["action_output_role"] == expected_output, f"legacy output role exact {old['locus']}#{old['token_ordinal']}")

    prior_token_fields, prior_tokens = read_tsv(PRIOR_TOKENS)
    prior_by_pos = {(row["locus"], row["token_ordinal"]): row for row in prior_tokens}
    expected_new_roles = {
        ("f86v5.24", "1"): ("M008", "DONOR_MATERIAL:C010", "C010", "C010", "NONE", "NONE", "EDGE_NODE", "1", "0", "0", "0", "NONE"),
        ("f86v5.24", "2"): ("M008", "UNBOUND_QUANTITY_REGISTER_HULL_ONLY", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", "0", "1", "0", "0", "NONE"),
        ("f86v5.24", "3"): ("M008", "REFERENCE:C010|TARGET_ACTION:C010", "C010", "NONE", "C010", "C010", "EDGE_NODE", "1", "0", "0", "1", "NONE"),
        ("f26r.2", "4"): ("M009", "INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:C011", "C011", "C011", "NONE", "NONE", "EDGE_NODE", "1", "0", "0", "0", "INFERRED_C011_SOURCE_RESULT"),
        ("f26r.2", "5"): ("M009", "EXACT_STATE_CHECKPOINT_HULL_ONLY:C011", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", "0", "1", "0", "0", "NONE"),
        ("f26r.2", "6"): ("M009", "REFERENCE:C011|TARGET_ACTION:C011", "C011", "NONE", "C011", "C011", "EDGE_NODE", "1", "0", "0", "1", "NONE"),
        ("f26r.2", "7"): ("M009", "FREE_DY_STRUCTURAL_CLOSURE:C011", "NONE", "NONE", "NONE", "NONE", "RENDER_ONLY_STRUCTURAL", "0", "0", "1", "0", "NONE"),
    }
    fields = ["component_id", "component_role", "edge_ids", "source_edge_ids", "reference_edge_ids", "target_edge_ids", "membership_class", "is_edge_node", "is_hull_only", "is_render_only_structural", "is_action_target", "action_output_role"]
    for key, expected in expected_new_roles.items():
        out, source = position_index[key], prior_by_pos[key]
        audit.check(tuple(out[field] for field in fields) == expected and out["surface"] == source["surface"] and out["token_gloss_de"] == source["v73_token_gloss_de"] and out["word_delta"] == "0" and out["status"] == STATUS, f"new position exact {key[0]}#{key[1]}")
    audit.check(Counter(row["membership_class"] for row in positions) == {"EDGE_NODE": 23, "HULL_ONLY": 2, "RENDER_ONLY_STRUCTURAL": 1} and sum(row["is_shared_edge_node"] == "1" for row in positions) == 2, "position class and shared-node counts exact")

    _, controls = read_tsv(CONTROLS)
    audit.check(one(controls, token_ordinal="3")["decision"] == "KEEP_H002_HELD" and one(controls, token_ordinal="5")["edge_membership"] == "HULL_ONLY_NOT_NODE" and one(controls, token_ordinal="7")["decision"] == "KEEP_STRUCTURAL_ONLY" and one(controls, token_ordinal="8")["decision"] == "STOP_C011_BEFORE_ORDINAL_8", "C011 boundary controls remain exact")
    _, contrasts = read_tsv(CONTRASTS)
    audit.check(len(contrasts) == 2 and contrasts[0]["source_material_role"] == "INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:Krautdroge" and contrasts[1]["decision"] == "KEEP_HELD_MATERIAL_COMPETITOR", "C011 hypothesis and held countercase unchanged")

    out_token_fields, out_tokens = read_tsv(TOKENS)
    prior_line_fields, prior_lines = read_tsv(PRIOR_LINES)
    out_line_fields, out_lines = read_tsv(LINES)
    prior_span_fields, prior_spans = read_tsv(PRIOR_SPANS)
    out_span_fields, out_spans = read_tsv(SPANS)
    audit.check(projection(prior_token_fields, prior_tokens, out_token_fields, out_tokens, TOKEN_EXTRA), "479-token V73 prefix projection exact")
    audit.check(projection(prior_line_fields, prior_lines, out_line_fields, out_lines, LINE_EXTRA), "51-line V73 prefix projection exact")
    audit.check(projection(prior_span_fields, prior_spans, out_span_fields, out_spans, SPAN_EXTRA), "three-span V73 prefix projection exact")
    audit.check(all(row["v74_token_gloss_de"] == row["v73_token_gloss_de"] and row["v74_word_delta"] == "0" and row["v74_status"] == STATUS for row in out_tokens), "479 token glosses byte-identical")
    audit.check(all(row["v74_line_translation_de"] == row["v73_clause_translation_de"] and row["v74_word_delta"] == "0" and row["v74_status"] == STATUS for row in out_lines), "51 line translations byte-identical")
    audit.check(all(row["v74_selected_gloss_de"] == row["v73_selected_gloss_de"] and row["v74_byte_identical"] == "1" and row["v74_component_change"] == "NONE" and row["v74_status"] == STATUS for row in out_spans), "three bound spans byte-identical")
    out_token_index = {(row["locus"], row["token_ordinal"]): row for row in out_tokens}
    audit.check(all(out_token_index[key]["v74_component_id"] == position_index[key]["component_id"] and out_token_index[key]["v74_component_role"] == position_index[key]["component_role"] and out_token_index[key]["v74_component_edge_ids"] == position_index[key]["edge_ids"] and out_token_index[key]["v74_component_membership_class"] == position_index[key]["membership_class"] for key in position_index), "all 26 position roles reach token overlay exactly")
    audit.check(sum(row["v74_component_id"] != "NONE" for row in out_tokens) == 26 and all(row["v74_component_id"] == "NONE" for key, row in out_token_index.items() if key not in position_index), "no component metadata outside 26 render positions")
    line_components = [(row["v74_component_ids"], row["v74_edge_ids"]) for row in out_lines if row["v74_component_ids"] != "NONE"]
    audit.check(len(line_components) == 9 and {component_id for component_id, _ in line_components} == {f"M{i:03d}" for i in range(1, 10)}, "nine components appear on nine exact lines")

    _, topology = read_tsv(TOPOLOGY)
    audit.check(len(topology) == 16 and all(row["status"] == STATUS for row in topology), "topology census has 16 status-bound rows")
    topo = {(row["dimension"], row["value"]): row for row in topology}
    expected_counts = {
        ("TOPOLOGY", "SINGLE_EDGE"): "5",
        ("TOPOLOGY", "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT"): "1",
        ("TOPOLOGY", "SERIAL_ACTION_OUTPUT_CHAIN"): "1",
        ("TOPOLOGY", "SINGLE_EDGE_WITH_UNBOUND_QUANTITY_HULL"): "1",
        ("TOPOLOGY", "SINGLE_EDGE_ACROSS_EXACT_STATE_CHECKPOINT"): "1",
        ("POSITION_CLASS", "EDGE_NODE"): "23",
        ("POSITION_CLASS", "HULL_ONLY_NOT_NODE"): "2",
        ("POSITION_CLASS", "RENDER_ONLY_STRUCTURAL"): "1",
        ("RESULT_STATUS", "NAMED_INTERMEDIATE_OUTPUT"): "1",
        ("RESULT_STATUS", "NAMED_FINAL_RESULT"): "0",
        ("SOURCE_FINAL_STATUS", "UNNAMED_NO_OUTGOING_EDGE"): "8",
        ("SOURCE_FINAL_STATUS", "NOT_DECLARED_IN_V72"): "1",
    }
    audit.check(all(topo[key]["count"] == value for key, value in expected_counts.items()), "topology position and result counts exact")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit.check(result["status"] == STATUS and result["question"] == QUESTION and result["claim_ceiling"] == CLAIM, "RESULT identity and claim ceiling exact")
    expected_basis = {"bound_spans": 3, "connected_components": 9, "edge_node_incidences": 25, "edge_nodes": 23, "f84_access": 0, "f84r_access": 0, "held_rival_rows": 17, "hull_only_positions": 2, "lines": 51, "minimal_hull_positions": 25, "new_pages": 0, "pages": 36, "reference_rows": 27, "relation_edges": 11, "render_only_structural_positions": 1, "render_positions": 26, "source_clauses": 175, "token_positions": 479}
    audit.check(result["basis"] == expected_basis, "RESULT complete numeric basis exact")
    expected_decision = {"c010_hull_only": "f86v5.24#2", "c011_hull_only": "f26r.2#5", "c011_render_only_structural": "f26r.2#7", "changed_edges": 0, "changed_participant_identities": 0, "component_ids": [f"M{i:03d}" for i in range(1, 10)], "component_join_rule": "IDENTICAL_LOCUS_ORDINAL_EDGE_NODE_ONLY", "new_edges": 0, "new_participant_identities": 0, "reference_changes": 0, "rival_changes": 0, "same_locus_without_shared_node_join": False, "shared_edge_nodes": ["f80v.35#3", "f86v6.25#4"]}
    audit.check(result["decision"] == expected_decision, "RESULT exact graph decision and zero deltas")
    audit.check(result["topology"] == {"common_destination_fanouts": 1, "exact_state_checkpoint_components": 1, "generic_single_edge_components": 7, "named_final_results": 0, "named_intermediate_outputs": 1, "plain_single_edge_components": 5, "serial_action_output_chains": 1, "unbound_quantity_hull_components": 1}, "RESULT topology exact")
    audit.check(result["freeze"] == {"bound_spans_byte_identical": 3, "changed_word_meanings": 0, "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0, "line_translations_byte_identical": 51, "new_word_meanings": 0, "token_glosses_byte_identical": 479} and result["next_gap"] == NEXT_GAP, "RESULT freeze and next gap exact")
    expected_inputs = {**INPUT_HASHES, str(SPEC.relative_to(ROOT)): SPEC_SHA, RUN_REL: RUN_SHA}
    audit.check(result["inputs"] == expected_inputs, "RESULT binds all inputs spec and builder")
    audit.check(result["files"] == {name: sha256(path) for name, path in GENERATED.items()}, "RESULT binds generated artifacts")

    reader = READER.read_text(encoding="utf-8")
    audit.check(STATUS in reader and all(f"M{i:03d}" in reader for i in range(1, 10)), "reader contains status and nine components")
    audit.check("23 unique edge nodes and 25 edge-node incidences" in reader and "C010#2 and C011#5" in reader and "C011#7 is render-only structural closure" in reader, "reader states graph accounting and nonnodes")
    audit.check("M007 remains the sole written serial intermediate" in reader and "No component has a named final action result" in reader and "All 479 token glosses, 51 line translations and 3 bound spans are byte-identical" in reader, "reader states result and freeze ceilings")

    report_path = EXP / "REPORT.md"
    audit.check(report_path.is_file(), "REPORT exists for final publication")
    report = report_path.read_text(encoding="utf-8")
    audit.check(STATUS in report and "11" in report and "9" in report and "23" in report and "25" in report, "REPORT contains status and graph counts")
    audit.check("C010" in report and "C011" in report and "hull" in report.lower() and "mere adjacency" in report.lower(), "REPORT exposes nonnode hull and rejects adjacency joins")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    audit.check(manifest["experiment_id"] == "GDT701" and manifest["slug"] == "v74_cumulative_relation_components", "manifest identity exact")
    audit.check(manifest["status"] == STATUS and manifest["question"] == QUESTION and manifest["claim_ceiling"] == CLAIM, "manifest result contract exact")
    audit.check(manifest["dependencies"] == ["GDT696", "GDT697", "GDT699", "GDT700"] and manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest dependencies and seals exact")
    audit.check(manifest["commands"] == {"run": "python3 " + RUN_REL, "validate": "python3 " + PREFIX + "src/validate.py"} and manifest["validation"] == {"artifact": PREFIX + "artifacts/VALIDATION.json", "status": "PASS"}, "manifest commands and validation exact")
    audit.check(manifest["artifact_policy"]["max_inline_bytes"] == 5_000_000 and bool(manifest["artifact_policy"]["large_artifact_justification"]), "manifest full-freeze justification present")
    input_map = {entry["path"]: entry for entry in manifest["inputs"]}
    audit.check(set(input_map) == set(INPUT_HASHES), "manifest exact external input set")
    for relative, expected in INPUT_HASHES.items():
        audit.check(input_map[relative]["sha256"] == expected and bool(input_map[relative]["role"]), f"manifest input binding exact {Path(relative).name}")
    output_map = {entry["path"]: entry for entry in manifest["outputs"]}
    audit.check(set(output_map) == EXPECTED_OUTPUTS, "manifest exact reproducible output tree")
    for relative in sorted(EXPECTED_OUTPUTS):
        entry = output_map[relative]
        audit.check(bool(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])) and bool(entry["role"]), f"manifest output syntax exact {Path(relative).name}")
        if relative == RUN_REL:
            audit.check(entry["sha256"] == RUN_SHA, "manifest binds externally declared builder digest")
        elif not relative.endswith("/VALIDATION.json"):
            audit.check(sha256(ROOT / relative) == entry["sha256"], f"manifest output digest exact {relative}")

    payload = {
        "status": "PASS", "checks": len(audit.rows), "failed": 0,
        "summary": {"relation_edges": 11, "connected_components": 9, "edge_nodes": 23, "edge_node_incidences": 25, "minimal_hull_positions": 25, "hull_only_positions": 2, "render_only_structural_positions": 1, "render_positions": 26, "shared_edge_nodes": 2, "same_locus_disjoint_negative_components": 2, "held_rivals": 17, "references": 27, "tokens_frozen": 479, "lines_frozen": 51, "spans_frozen": 3, "new_edges": 0, "new_participant_identities": 0, "new_word_meanings": 0},
        "audit": audit.rows,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
