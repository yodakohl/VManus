#!/usr/bin/env python3
"""Compose the nine V69 occurrence edges into seven exact V70 microrecords."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords"
SRC = EXP / "src"
ART = EXP / "artifacts"
G696 = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries"
G696_ART = G696 / "artifacts"

SPECS = SRC / "V70_MICRORECORD_SPECS.tsv"
EDGES = G696_ART / "V69_9_LOCAL_ACTION_EDGES.tsv"
REFERENCES = G696_ART / "V69_27_REFERENCE_CENSUS.tsv"
RIVALS = G696_ART / "V69_17_RELATION_RIVALS.tsv"
TOKENS = G696_ART / "V69_479_TOKEN_RELATION_OVERLAY.tsv"
LINES = G696_ART / "V69_51_LINE_RELATION_OVERLAY.tsv"
SPANS = G696_ART / "V69_3_BOUND_SPAN_FREEZE.tsv"
G696_RESULT = G696_ART / "RESULT.json"

MICRORECORDS_OUT = ART / "V70_7_EXACT_MICRORECORDS.tsv"
EDGE_COVERAGE_OUT = ART / "V70_9_EDGE_WINDOW_COVERAGE.tsv"
WINDOW_TOKENS_OUT = ART / "V70_19_WINDOW_TOKEN_ROLES.tsv"
TOKENS_OUT = ART / "V70_479_TOKEN_FREEZE.tsv"
LINES_OUT = ART / "V70_51_LINE_MICRORECORD_OVERLAY.tsv"
SPANS_OUT = ART / "V70_3_BOUND_SPAN_FREEZE.tsv"
CENSUS_OUT = ART / "V70_TOPOLOGY_CENSUS.tsv"
READER_OUT = ART / "GDT697_V70_EXACT_MICRORECORD_READER.md"
ARTIFACT_README = ART / "README.md"
RESULT_OUT = ART / "RESULT.json"

STATUS = (
    "PASS_V70_7_EXACT_MICRORECORDS__9_EDGE_COVERAGE__"
    "1_SERIAL_CHAIN_1_SHARED_DESTINATION_REPEAT_5_SINGLE__"
    "ZERO_WORD_MEANING_DELTA"
)
CLAIM_CEILING = (
    "V70 composes only the nine already admitted occurrence-bound V69 edges "
    "into seven minimal local German microrecords. It changes no token gloss, "
    "line translation, bound span, word meaning, page, or unresolved relation; "
    "the microrecords remain an exploratory editorial rendering, not deciphered plaintext."
)

MICRO_FIELDS = [
    "microrecord_id", "locus", "window_start_ordinal", "window_end_ordinal",
    "window_token_count", "edge_ids", "edge_count", "topology", "action_ordinals",
    "action_count", "working_edge_ids", "strong_edge_ids", "support_profile",
    "expected_surfaces", "observed_surfaces", "expected_glosses_de",
    "observed_glosses_de", "expected_role_trace", "observed_role_trace",
    "v68_clause_ids", "microrecord_de", "left_boundary", "right_boundary",
    "left_neighbor_ordinal", "left_neighbor_surface", "right_neighbor_ordinal",
    "right_neighbor_surface", "outside_reference_ids", "outside_rival_ids",
    "boundary_note_de", "composition_basis", "forbidden_inference",
    "minimal_convex_hull", "edge_coverage_exact", "final_result_status",
    "v69_word_delta", "status",
]
EDGE_FIELDS = [
    "edge_id", "microrecord_id", "locus", "support_tier", "relation_class",
    "source_ordinals", "reference_ordinals", "target_action_ordinal",
    "right_participant_ordinals", "node_ordinals", "window_start_ordinal",
    "window_end_ordinal", "operation_rank", "topology", "edge_role_in_window",
    "shared_node_ordinals", "source_join_exact", "reference_join_exact",
    "target_join_exact", "covered_once", "v68_word_delta", "status",
]
WINDOW_TOKEN_FIELDS = [
    "page", "locus", "token_ordinal", "surface", "v69_token_gloss_de",
    "microrecord_id", "window_position", "window_size", "role_trace", "edge_ids",
    "source_edge_ids", "reference_edge_ids", "target_edge_ids",
    "right_participant_edge_ids", "is_action_target", "is_shared_node",
    "is_action_output_bridge", "is_window_start", "is_window_end",
    "v68_clause_id", "v68_clause_type", "v70_microrecord_de", "v69_word_delta",
    "status",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tsv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.reader(handle, delimiter="\t"))
    require(bool(raw), f"empty TSV: {path}")
    fields = raw[0]
    require(len(set(fields)) == len(fields), f"duplicate TSV header: {path}")
    for number, row in enumerate(raw[1:], 2):
        require(len(row) == len(fields), f"TSV width mismatch {path}:{number}")
    return [dict(zip(fields, row)) for row in raw[1:]], fields


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def parse_ordinals(value: str) -> list[int]:
    if not value or value == "NONE":
        return []
    out: list[int] = []
    for part in value.split("|"):
        if "-" in part:
            left, right = (int(item) for item in part.split("-", 1))
            require(left <= right, f"reversed ordinal range: {value}")
            out.extend(range(left, right + 1))
        else:
            out.append(int(part))
    require(len(out) == len(set(out)), f"duplicate ordinal: {value}")
    return out


def pipe(values: list[object] | set[object]) -> str:
    material = list(values)
    return "NONE" if not material else "|".join(str(value) for value in material)


def split_pipe(value: str) -> list[str]:
    return [] if not value or value == "NONE" else value.split("|")


def split_double_bar(value: str) -> list[str]:
    return [] if not value or value == "NONE" else value.split(" || ")


def normalized_topology(value: str) -> str:
    if value.startswith("SINGLE_"):
        return "SINGLE_EDGE"
    if value in {"SHARED_DESTINATION_REPEAT", "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT"}:
        return "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT"
    require(value == "SERIAL_ACTION_OUTPUT_CHAIN", f"unknown topology: {value}")
    return value


def support_profile(member_edges: list[dict[str, str]]) -> str:
    tiers = {edge["support_tier"] for edge in member_edges}
    mapping = {
        frozenset({"A_STRONG_LICENSED"}): "A_ONLY",
        frozenset({"B_WORKING_LOCAL"}): "B_ONLY",
        frozenset({"A_STRONG_LICENSED", "B_WORKING_LOCAL"}): "A_PLUS_B",
        frozenset({"A_MINUS_EXPLICIT_OUTPUT", "B_WORKING_LOCAL"}): "A_MINUS_PLUS_B",
    }
    require(frozenset(tiers) in mapping, f"unsupported window tier mix: {tiers}")
    return mapping[frozenset(tiers)]


def edge_nodes(edge: dict[str, str]) -> set[int]:
    nodes = set(range(int(edge["source_start_ordinal"]), int(edge["source_end_ordinal"]) + 1))
    nodes.update(parse_ordinals(edge["reference_ordinal"]))
    nodes.add(int(edge["target_action_ordinal"]))
    nodes.update(parse_ordinals(edge["right_participant_ordinals"]))
    return nodes


def exact_components(edges: list[dict[str, str]]) -> list[set[str]]:
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in edges:
        by_locus[edge["locus"]].append(edge)
    components: list[set[str]] = []
    for locus_edges in by_locus.values():
        unused = {edge["edge_id"] for edge in locus_edges}
        lookup = {edge["edge_id"]: edge for edge in locus_edges}
        while unused:
            seed = min(unused)
            component = {seed}
            frontier = [seed]
            unused.remove(seed)
            while frontier:
                current = frontier.pop()
                current_nodes = edge_nodes(lookup[current])
                joined = [other for other in sorted(unused) if current_nodes & edge_nodes(lookup[other])]
                for other in joined:
                    unused.remove(other)
                    component.add(other)
                    frontier.append(other)
            components.append(component)
    return components


def md(value: str) -> str:
    return value.replace("|", "<br>").replace("\n", " ")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs, _ = read_tsv(SPECS)
    edges, _ = read_tsv(EDGES)
    references, _ = read_tsv(REFERENCES)
    rivals, _ = read_tsv(RIVALS)
    tokens, token_fields = read_tsv(TOKENS)
    lines, line_fields = read_tsv(LINES)
    spans, span_fields = read_tsv(SPANS)
    g696_result = json.loads(G696_RESULT.read_text(encoding="utf-8"))

    require(g696_result["status"].startswith("PASS_V69_"), "GDT696 is not a passing V69 base")
    require(len(specs) == 7, "V70 must contain seven microrecord specs")
    require([row["microrecord_id"] for row in specs] == [f"M{i:03d}" for i in range(1, 8)], "microrecord IDs/order changed")
    require(len({row["locus"] for row in specs}) == 7, "one exact window per locus required")
    require(len(edges) == 9 and len({row["edge_id"] for row in edges}) == 9, "V69 edge deck changed")
    require(len(references) == 27 and len(rivals) == 17, "V69 reference/rival census changed")
    require(len(tokens) == 479 and len(lines) == 51 and len(spans) == 3, "V69 freeze size changed")
    require(not any(row["locus"].lower().startswith("f84") for row in tokens), "f84/f84r entered scope")
    require(all(row["v69_word_delta"] == "0" for row in tokens + lines), "V69 word delta is not zero")
    require(all(row["v69_byte_identical"] == "1" for row in spans), "V69 span freeze changed")

    edge_by_id = {row["edge_id"]: row for row in edges}
    token_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in tokens}
    require(len(token_by_key) == 479, "duplicate V69 token key")
    line_by_locus = {row["locus"]: row for row in lines}
    require(len(line_by_locus) == 51, "duplicate V69 locus")
    components = exact_components(edges)
    require(len(components) == 7, f"expected 7 exact-node components, got {len(components)}")
    component_keys = {frozenset(component) for component in components}

    micro_rows: list[dict[str, object]] = []
    edge_rows: list[dict[str, object]] = []
    window_token_rows: list[dict[str, object]] = []
    edge_usage: Counter[str] = Counter()
    window_positions: set[tuple[str, int]] = set()
    touched_clause_keys: set[tuple[str, str]] = set()
    clause_aligned_starts = 0
    all_end_at_clause_boundary = 0
    per_edge_hull_positions = 0

    refs_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    rivals_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in references:
        refs_by_locus[row["locus"]].append(row)
    for row in rivals:
        rivals_by_locus[row["locus"]].append(row)

    for spec in specs:
        micro_id = spec["microrecord_id"]
        locus = spec["locus"]
        require(locus in line_by_locus and not locus.lower().startswith("f84"), f"bad locus: {locus}")
        start = int(spec["window_start_ordinal"])
        end = int(spec["window_end_ordinal"])
        require(start <= end, f"reversed window {micro_id}")
        positions = list(range(start, end + 1))
        member_ids = split_pipe(spec["edge_ids"])
        require(member_ids and len(member_ids) == len(set(member_ids)), f"bad member edges {micro_id}")
        require(all(edge_id in edge_by_id for edge_id in member_ids), f"unknown edge in {micro_id}")
        require(frozenset(member_ids) in component_keys, f"{micro_id} is not an exact endpoint-sharing component")
        member_edges = [edge_by_id[edge_id] for edge_id in member_ids]
        require({edge["locus"] for edge in member_edges} == {locus}, f"cross-locus window {micro_id}")
        for edge_id in member_ids:
            edge_usage[edge_id] += 1

        union_nodes = set().union(*(edge_nodes(edge) for edge in member_edges))
        require((min(union_nodes), max(union_nodes)) == (start, end), f"nonminimal convex hull {micro_id}")
        require(union_nodes <= set(positions), f"edge node outside {micro_id}")
        for edge in member_edges:
            nodes = edge_nodes(edge)
            per_edge_hull_positions += max(nodes) - min(nodes) + 1

        topology = normalized_topology(spec["topology"])
        if len(member_ids) == 1:
            require(topology == "SINGLE_EDGE", f"single component has wrong topology {micro_id}")
        else:
            require(len(member_ids) == 2, f"unexpected component arity {micro_id}")

        action_ordinals = [int(value) for value in split_pipe(spec["action_ordinals"])]
        expected_actions = sorted(int(edge["target_action_ordinal"]) for edge in member_edges)
        require(action_ordinals == expected_actions, f"action order changed {micro_id}")
        working_ids = [edge["edge_id"] for edge in member_edges if edge["support_tier"] == "B_WORKING_LOCAL"]
        require(split_pipe(spec["working_edge_ids"]) == working_ids, f"working IDs changed {micro_id}")
        strong_ids = [edge["edge_id"] for edge in member_edges if edge["support_tier"] != "B_WORKING_LOCAL"]
        profile = support_profile(member_edges)

        observed_tokens = [token_by_key[(locus, ordinal)] for ordinal in positions]
        observed_surfaces = [row["surface"] for row in observed_tokens]
        observed_glosses = [row["v69_token_gloss_de"] for row in observed_tokens]
        observed_roles = [row["v69_relation_roles"] for row in observed_tokens]
        require(observed_surfaces == split_pipe(spec["expected_surfaces"]), f"surface join changed {micro_id}")
        require(observed_glosses == split_double_bar(spec["expected_glosses_de"]), f"gloss join changed {micro_id}")
        require(observed_roles == split_double_bar(spec["expected_role_trace"]), f"role trace changed {micro_id}")

        clause_ids: list[str] = []
        for token in observed_tokens:
            clause_id = token["v68_clause_id"]
            if not clause_ids or clause_ids[-1] != clause_id:
                clause_ids.append(clause_id)
            touched_clause_keys.add((locus, clause_id))
        first_clause_id = observed_tokens[0]["v68_clause_id"]
        first_clause_positions = [int(row["token_ordinal"]) for row in tokens if row["locus"] == locus and row["v68_clause_id"] == first_clause_id]
        if start == min(first_clause_positions):
            clause_aligned_starts += 1
        clause_ends = parse_ordinals(line_by_locus[locus]["v68_clause_end_ordinals"])
        require(end in clause_ends, f"window does not end at a clause boundary: {micro_id}")
        all_end_at_clause_boundary += 1

        internal_linked_refs = {
            row["reference_id"] for row in refs_by_locus[locus]
            if set(split_pipe(row["linked_edge_ids"])) & set(member_ids)
        }
        outside_refs = [row["reference_id"] for row in refs_by_locus[locus] if row["reference_id"] not in internal_linked_refs]
        require(outside_refs == split_pipe(spec["outside_reference_ids"]), f"outside reference deck changed {micro_id}")
        outside_rivals = [row["rival_id"] for row in rivals_by_locus[locus]]
        require(outside_rivals == split_pipe(spec["outside_rival_ids"]), f"outside rival deck changed {micro_id}")
        require(not any(start <= int(row["target_action_ordinal"]) <= end for row in rivals_by_locus[locus]), f"held rival target entered {micro_id}")

        max_ordinal = int(line_by_locus[locus]["token_count"])
        left_ordinal = start - 1 if start > 1 else None
        right_ordinal = end + 1 if end < max_ordinal else None
        left_surface = token_by_key[(locus, left_ordinal)]["surface"] if left_ordinal else "NONE"
        right_surface = token_by_key[(locus, right_ordinal)]["surface"] if right_ordinal else "NONE"
        require(left_ordinal is not None and str(left_ordinal) in spec["left_boundary"], f"left boundary mismatch {micro_id}")
        if right_ordinal is None:
            require(spec["right_boundary"] == "END_OF_LINE", f"line-end boundary mismatch {micro_id}")
        else:
            require(str(right_ordinal) in spec["right_boundary"], f"right boundary mismatch {micro_id}")

        if topology == "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT":
            require(set(member_ids) == {"C004", "C008"} and locus == "f80v.35", "fanout identity changed")
            require(edge_nodes(edge_by_id["C004"]) & edge_nodes(edge_by_id["C008"]) == {3}, "fanout destination changed")
            require(action_ordinals == [5, 6], "fanout operations changed")
        if topology == "SERIAL_ACTION_OUTPUT_CHAIN":
            require(set(member_ids) == {"C006", "C007"} and locus == "f86v6.25", "serial identity changed")
            require(int(edge_by_id["C007"]["target_action_ordinal"]) == int(edge_by_id["C006"]["source_start_ordinal"]) == 4, "serial bridge changed")
            require("DONOR_ACTION_OUTPUT:C006" in observed_roles[2] and "TARGET_ACTION:C007" in observed_roles[2], "serial bridge roles changed")

        shared_nodes: set[int] = set()
        for edge in member_edges:
            for other in member_edges:
                if other["edge_id"] != edge["edge_id"]:
                    shared_nodes.update(edge_nodes(edge) & edge_nodes(other))

        for position, token in zip(positions, observed_tokens):
            window_positions.add((locus, position))
            source_edge_ids: list[str] = []
            reference_edge_ids: list[str] = []
            target_edge_ids: list[str] = []
            right_edge_ids: list[str] = []
            touching_edge_ids: list[str] = []
            for edge in member_edges:
                edge_id = edge["edge_id"]
                source_positions = set(range(int(edge["source_start_ordinal"]), int(edge["source_end_ordinal"]) + 1))
                reference_positions = set(parse_ordinals(edge["reference_ordinal"]))
                target_position = int(edge["target_action_ordinal"])
                right_positions = set(parse_ordinals(edge["right_participant_ordinals"]))
                if position in edge_nodes(edge):
                    touching_edge_ids.append(edge_id)
                if position in source_positions:
                    source_edge_ids.append(edge_id)
                if position in reference_positions:
                    reference_edge_ids.append(edge_id)
                if position == target_position:
                    target_edge_ids.append(edge_id)
                if position in right_positions:
                    right_edge_ids.append(edge_id)
            inherited_touching = split_pipe(token["v69_edge_ids"])
            require(set(inherited_touching) == set(touching_edge_ids), f"token edge membership changed {locus}#{position}")
            touching_edge_ids = inherited_touching
            window_token_rows.append({
                "page": token["page"], "locus": locus, "token_ordinal": position,
                "surface": token["surface"], "v69_token_gloss_de": token["v69_token_gloss_de"],
                "microrecord_id": micro_id, "window_position": position - start + 1,
                "window_size": len(positions), "role_trace": token["v69_relation_roles"],
                "edge_ids": pipe(touching_edge_ids), "source_edge_ids": pipe(source_edge_ids),
                "reference_edge_ids": pipe(reference_edge_ids), "target_edge_ids": pipe(target_edge_ids),
                "right_participant_edge_ids": pipe(right_edge_ids), "is_action_target": int(bool(target_edge_ids)),
                "is_shared_node": int(position in shared_nodes),
                "is_action_output_bridge": int("DONOR_ACTION_OUTPUT" in token["v69_relation_roles"] and bool(target_edge_ids)),
                "is_window_start": int(position == start), "is_window_end": int(position == end),
                "v68_clause_id": token["v68_clause_id"], "v68_clause_type": token["v68_clause_type"],
                "v70_microrecord_de": spec["microrecord_de"], "v69_word_delta": 0,
                "status": "V69_TOKEN_AND_GLOSS_FROZEN__V70_WINDOW_ROLE_ONLY",
            })

        ordered_edges = sorted(member_edges, key=lambda row: int(row["target_action_ordinal"]))
        for rank, edge in enumerate(ordered_edges, 1):
            nodes = edge_nodes(edge)
            source_ordinals = list(range(int(edge["source_start_ordinal"]), int(edge["source_end_ordinal"]) + 1))
            reference_ordinals = parse_ordinals(edge["reference_ordinal"])
            right_ordinals = parse_ordinals(edge["right_participant_ordinals"])
            if topology == "SINGLE_EDGE":
                role = "SINGLE_OPERATION"
            elif topology == "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT":
                role = "COMMON_DESTINATION_FIRST" if rank == 1 else "COMMON_DESTINATION_REPEAT_WORKING"
            else:
                role = "SERIAL_PRODUCER" if edge["edge_id"] == "C007" else "SERIAL_CONSUMER"
            edge_rows.append({
                "edge_id": edge["edge_id"], "microrecord_id": micro_id, "locus": locus,
                "support_tier": edge["support_tier"], "relation_class": edge["relation_class"],
                "source_ordinals": pipe(source_ordinals), "reference_ordinals": pipe(reference_ordinals),
                "target_action_ordinal": edge["target_action_ordinal"],
                "right_participant_ordinals": pipe(right_ordinals), "node_ordinals": pipe(sorted(nodes)),
                "window_start_ordinal": start, "window_end_ordinal": end, "operation_rank": rank,
                "topology": topology, "edge_role_in_window": role,
                "shared_node_ordinals": pipe(sorted(nodes & shared_nodes)),
                "source_join_exact": edge["source_join_exact"], "reference_join_exact": edge["reference_join_exact"],
                "target_join_exact": edge["target_join_exact"], "covered_once": 1,
                "v68_word_delta": 0, "status": "V69_EDGE_USED_ONCE_IN_MINIMAL_V70_WINDOW",
            })

        micro_rows.append({
            "microrecord_id": micro_id, "locus": locus, "window_start_ordinal": start,
            "window_end_ordinal": end, "window_token_count": len(positions), "edge_ids": pipe(member_ids),
            "edge_count": len(member_ids), "topology": topology, "action_ordinals": pipe(action_ordinals),
            "action_count": len(action_ordinals), "working_edge_ids": pipe(working_ids),
            "strong_edge_ids": pipe(strong_ids), "support_profile": profile,
            "expected_surfaces": spec["expected_surfaces"], "observed_surfaces": pipe(observed_surfaces),
            "expected_glosses_de": spec["expected_glosses_de"], "observed_glosses_de": " || ".join(observed_glosses),
            "expected_role_trace": spec["expected_role_trace"], "observed_role_trace": " || ".join(observed_roles),
            "v68_clause_ids": pipe(clause_ids), "microrecord_de": spec["microrecord_de"],
            "left_boundary": spec["left_boundary"], "right_boundary": spec["right_boundary"],
            "left_neighbor_ordinal": left_ordinal if left_ordinal is not None else "NONE",
            "left_neighbor_surface": left_surface,
            "right_neighbor_ordinal": right_ordinal if right_ordinal is not None else "NONE",
            "right_neighbor_surface": right_surface, "outside_reference_ids": pipe(outside_refs),
            "outside_rival_ids": pipe(outside_rivals), "boundary_note_de": spec["boundary_note_de"],
            "composition_basis": spec["composition_basis"], "forbidden_inference": spec["forbidden_inference"],
            "minimal_convex_hull": 1, "edge_coverage_exact": 1,
            "final_result_status": "UNNAMED_NO_OUTGOING_EDGE", "v69_word_delta": 0,
            "status": "EXACT_OCCURRENCE_MICRORECORD__NO_NEW_EDGE_OR_WORD",
        })

    require(edge_usage == Counter({f"C{i:03d}": 1 for i in range(1, 10)}), f"edge coverage changed: {edge_usage}")
    require(len(window_positions) == 19, f"expected 19 window positions, got {len(window_positions)}")
    require(per_edge_hull_positions == 23, f"expected 23 summed per-edge hull positions, got {per_edge_hull_positions}")
    require(len(touched_clause_keys) == 16, f"expected 16 touched V68 clauses, got {len(touched_clause_keys)}")
    require(clause_aligned_starts == 1 and all_end_at_clause_boundary == 7, "window/clause boundary census changed")
    require(Counter(row["topology"] for row in micro_rows) == Counter({
        "SINGLE_EDGE": 5, "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT": 1,
        "SERIAL_ACTION_OUTPUT_CHAIN": 1,
    }), "topology census changed")
    require(Counter(row["support_profile"] for row in micro_rows) == Counter({
        "A_ONLY": 4, "A_PLUS_B": 1, "A_MINUS_PLUS_B": 1, "B_ONLY": 1,
    }), "support profile census changed")
    require(sum(int(row["is_action_output_bridge"]) for row in window_token_rows) == 1, "action-output bridge count changed")
    require(sum(int(row["is_shared_node"]) for row in window_token_rows) == 2, "shared-node count changed")

    membership_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in window_token_rows}
    token_out: list[dict[str, object]] = []
    for row in tokens:
        member = membership_by_key.get((row["locus"], int(row["token_ordinal"])))
        new = dict(row)
        new.update({
            "v70_microrecord_id": member["microrecord_id"] if member else "NONE",
            "v70_window_role_trace": member["role_trace"] if member else "NONE",
            "v70_window_position": member["window_position"] if member else "NONE",
            "v70_window_size": member["window_size"] if member else "NONE",
            "v70_microrecord_de": member["v70_microrecord_de"] if member else "NONE",
            "v70_token_gloss_de": row["v69_token_gloss_de"], "v70_word_delta": 0,
            "v70_status": "V69_TOKEN_GLOSS_BYTE_IDENTICAL__SEPARATE_WINDOW_METADATA",
        })
        token_out.append(new)

    micro_by_locus = {row["locus"]: row for row in micro_rows}
    line_out: list[dict[str, object]] = []
    for row in lines:
        micro = micro_by_locus.get(row["locus"])
        new = dict(row)
        new.update({
            "v70_microrecord_ids": micro["microrecord_id"] if micro else "NONE",
            "v70_microrecords_de": micro["microrecord_de"] if micro else "NONE",
            "v70_window_ordinals": f"{micro['window_start_ordinal']}-{micro['window_end_ordinal']}" if micro else "NONE",
            "v70_topologies": micro["topology"] if micro else "NONE",
            "v70_support_profiles": micro["support_profile"] if micro else "NONE",
            "v70_named_intermediate_output_count": 1 if micro and micro["topology"] == "SERIAL_ACTION_OUTPUT_CHAIN" else 0,
            "v70_named_final_result_count": 0, "v70_clause_translation_de": row["v69_clause_translation_de"],
            "v70_word_delta": 0,
            "v70_status": "V69_LINE_BYTE_IDENTICAL__SEPARATE_EXACT_MICRORECORD" if micro else "V69_LINE_BYTE_IDENTICAL__NO_MICRORECORD",
        })
        line_out.append(new)

    span_out: list[dict[str, object]] = []
    span_overlap_count = 0
    for row in spans:
        overlap = any((row["locus"], ordinal) in window_positions for ordinal in range(int(row["start_ordinal"]), int(row["end_ordinal"]) + 1))
        span_overlap_count += int(overlap)
        new = dict(row)
        new.update({
            "v70_selected_gloss_de": row["v69_selected_gloss_de"], "v70_byte_identical": 1,
            "v70_microrecord_overlap": "OVERLAP_METADATA_ONLY" if overlap else "NONE",
            "v70_status": "V69_BOUND_SPAN_BYTE_IDENTICAL",
        })
        span_out.append(new)
    require(span_overlap_count == 0, "a frozen bound span unexpectedly overlaps a V70 window")

    census_rows: list[dict[str, object]] = []
    census_specs = [
        ("TOPOLOGY", "SINGLE_EDGE", [row["microrecord_id"] for row in micro_rows if row["topology"] == "SINGLE_EDGE"], "one admitted edge and one target action"),
        ("TOPOLOGY", "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT", [row["microrecord_id"] for row in micro_rows if row["topology"] == "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT"], "two ordered additions share only the written destination; no first-output carry"),
        ("TOPOLOGY", "SERIAL_ACTION_OUTPUT_CHAIN", [row["microrecord_id"] for row in micro_rows if row["topology"] == "SERIAL_ACTION_OUTPUT_CHAIN"], "the first action output is the exact donor of the second action"),
    ]
    for dimension, value, members, note in census_specs:
        census_rows.append({"dimension": dimension, "value": value, "count": len(members), "member_ids": pipe(members), "note": note})
    for value in ["A_ONLY", "A_PLUS_B", "A_MINUS_PLUS_B", "B_ONLY"]:
        members = [row["microrecord_id"] for row in micro_rows if row["support_profile"] == value]
        census_rows.append({"dimension": "SUPPORT_PROFILE", "value": value, "count": len(members), "member_ids": pipe(members), "note": "support tiers remain visible and are not averaged"})
    for value in ["A_STRONG_LICENSED", "A_MINUS_EXPLICIT_OUTPUT", "B_WORKING_LOCAL"]:
        members = [row["edge_id"] for row in edge_rows if row["support_tier"] == value]
        census_rows.append({"dimension": "EDGE_SUPPORT_TIER", "value": value, "count": len(members), "member_ids": pipe(members), "note": "unchanged GDT696 edge tier"})
    census_rows.extend([
        {"dimension": "RESULT_STATUS", "value": "NAMED_INTERMEDIATE_OUTPUT", "count": 1, "member_ids": "M007", "note": "qodar at f86v6.25#4 is both C007 target and C006 donor"},
        {"dimension": "RESULT_STATUS", "value": "NAMED_FINAL_RESULT", "count": 0, "member_ids": "NONE", "note": "no final target has an admitted outgoing result carry"},
        {"dimension": "BOUNDARY", "value": "CLAUSE_ALIGNED_START", "count": clause_aligned_starts, "member_ids": "M007", "note": "the other six windows start inside the tail of an existing V68 nominal block"},
        {"dimension": "BOUNDARY", "value": "TARGET_CLAUSE_ALIGNED_END", "count": all_end_at_clause_boundary, "member_ids": pipe([row["microrecord_id"] for row in micro_rows]), "note": "every window ends exactly at an admitted target action boundary"},
    ])

    write_tsv(MICRORECORDS_OUT, micro_rows, MICRO_FIELDS)
    write_tsv(EDGE_COVERAGE_OUT, sorted(edge_rows, key=lambda row: row["edge_id"]), EDGE_FIELDS)
    write_tsv(WINDOW_TOKENS_OUT, window_token_rows, WINDOW_TOKEN_FIELDS)
    write_tsv(TOKENS_OUT, token_out, token_fields + [
        "v70_microrecord_id", "v70_window_role_trace", "v70_window_position",
        "v70_window_size", "v70_microrecord_de", "v70_token_gloss_de", "v70_word_delta", "v70_status",
    ])
    write_tsv(LINES_OUT, line_out, line_fields + [
        "v70_microrecord_ids", "v70_microrecords_de", "v70_window_ordinals", "v70_topologies",
        "v70_support_profiles", "v70_named_intermediate_output_count", "v70_named_final_result_count",
        "v70_clause_translation_de", "v70_word_delta", "v70_status",
    ])
    write_tsv(SPANS_OUT, span_out, span_fields + [
        "v70_selected_gloss_de", "v70_byte_identical", "v70_microrecord_overlap", "v70_status",
    ])
    write_tsv(CENSUS_OUT, census_rows, ["dimension", "value", "count", "member_ids", "note"])

    reader: list[str] = [
        "# GDT697 / V70 — sieben exakte Relations-Mikrorecords", "", f"Status: `{STATUS}`", "",
        "V70 setzt die neun bereits in V69 zugelassenen lokalen Kanten zu sieben eng begrenzten Arbeitsanweisungen zusammen. Die bisherigen 479 Glossen und 51 Zeilen bleiben unverändert; der praktische Text steht in einer getrennten Spalte.",
        "", "## Die sieben konkreten Fenster", "",
        "| ID | Stelle | Formen | Stütze | konkrete Mikroanweisung |",
        "|---|---|---|---|---|",
    ]
    for row in micro_rows:
        reader.append(
            f"| {row['microrecord_id']} | `{row['locus']} #{row['window_start_ordinal']}–{row['window_end_ordinal']}` | "
            f"`{md(str(row['observed_surfaces']))}` | `{row['support_profile']}` | {md(str(row['microrecord_de']))} |"
        )
    reader.extend([
        "",
        "Nur M007 ist eine wirkliche Zweischrittkette mit benanntem Zwischenprodukt. M006 sind zwei getrennte Zugaben an dasselbe Ziel; die erste Zugabe erzeugt keinen geschriebenen Ausgang für die zweite. In keinem Fenster ist ein Endprodukt nach der letzten Handlung benannt.",
        "", "## Token- und Grenzapparat",
    ])
    window_tokens_by_micro: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in window_token_rows:
        window_tokens_by_micro[str(row["microrecord_id"])].append(row)
    for row in micro_rows:
        reader.extend([
            "", f"### {row['microrecord_id']} — `{row['locus']} #{row['window_start_ordinal']}–{row['window_end_ordinal']}`", "",
            f"**Lesetext:** {row['microrecord_de']}", "",
        ])
        for token in window_tokens_by_micro[str(row["microrecord_id"])]:
            reader.append(f"- `#{token['token_ordinal']} {token['surface']}` — {token['v69_token_gloss_de']} [`{token['role_trace']}`]")
        reader.extend([
            "", f"Grenze: `{row['left_boundary']}` / `{row['right_boundary']}`. {row['boundary_note_de']}", "",
            f"Nicht einziehen: {row['forbidden_inference']}",
        ])
    reader.extend([
        "", "## Vollständige 51-Zeilen-Projektion", "",
        "Die mittlere Spalte ist der byte-identische V69-Reader. Die rechte Spalte enthält nur an sieben Stellen eine zusätzliche V70-Mikroanweisung.",
        "", "| Stelle | unveränderte V69-Zeile | zusätzliche V70-Mikroanweisung |", "|---|---|---|",
    ])
    for row in line_out:
        micro_text = row["v70_microrecords_de"] if row["v70_microrecord_ids"] != "NONE" else "—"
        reader.append(f"| `{row['locus']}` | {md(row['v69_clause_translation_de'])} | {md(str(micro_text))} |")
    reader.extend([
        "", "## Harte Reichweite", "",
        "- 9/9 V69-Kanten genau einmal; keine aus bloßer Nachbarschaft erzeugte Kante.",
        "- 7 disjunkte Minimalfenster mit 19 Tokenpositionen und 16 berührten V68-Klauseln.",
        "- 5 Einzelhandlungen, 1 geordnete Zielwiederholung, 1 serielle Ausgangskette.",
        "- 1 benanntes Zwischenprodukt, 0 benannte Endprodukte.",
        "- 479 Token, 51 Zeilen und 3 gebundene Spannen unverändert; 0 neue Wortbedeutungen.", "",
        "Diese Mikrorecords sagen lokal mehr als der alte Semikolon-Reader, ohne die offenen Anschlüsse vor oder nach dem Fenster zu erfinden.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")

    ARTIFACT_README.write_text(
        "# GDT697 artifacts\n\n"
        "- `V70_7_EXACT_MICRORECORDS.tsv`: seven minimal practical relation windows.\n"
        "- `V70_9_EDGE_WINDOW_COVERAGE.tsv`: exact once-only use of every V69 edge.\n"
        "- `V70_19_WINDOW_TOKEN_ROLES.tsv`: token-level role trace inside the windows.\n"
        "- `V70_479_TOKEN_FREEZE.tsv`: full unchanged V69 token deck plus V70 membership.\n"
        "- `V70_51_LINE_MICRORECORD_OVERLAY.tsv`: full unchanged line reader plus separate microrecords.\n"
        "- `V70_3_BOUND_SPAN_FREEZE.tsv`: unchanged bound-span deck.\n"
        "- `V70_TOPOLOGY_CENSUS.tsv`: topology, support, result, and boundary census.\n"
        "- `GDT697_V70_EXACT_MICRORECORD_READER.md`: compact human reader and full 51-line projection.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n", encoding="utf-8",
    )

    generated_for_hash = [
        MICRORECORDS_OUT, EDGE_COVERAGE_OUT, WINDOW_TOKENS_OUT, TOKENS_OUT,
        LINES_OUT, SPANS_OUT, CENSUS_OUT, READER_OUT, ARTIFACT_README,
    ]
    input_paths = [SPECS, EDGES, REFERENCES, RIVALS, TOKENS, LINES, SPANS, G696_RESULT, Path(__file__).resolve()]
    result = {
        "status": STATUS,
        "question": "Can the nine admitted V69 occurrence edges be composed into concrete minimal source/action microrecords without inventing another relation or word meaning?",
        "claim_ceiling": CLAIM_CEILING,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51, "bound_spans": 3,
            "v69_admitted_edges": 9, "v69_reference_positions": 27, "v69_held_rivals": 17,
            "f84_access": 0, "f84r_access": 0,
        },
        "composition": {
            "microrecords": 7, "affected_loci": 7, "window_token_positions": 19,
            "summed_per_edge_convex_hull_positions": per_edge_hull_positions,
            "edges_covered_exactly_once": 9, "multi_edge_microrecords": 2,
            "distinct_v68_clauses_touched": len(touched_clause_keys), "action_target_positions": 9,
            "written_reference_positions": 6, "action_output_bridges": 1,
            "common_destination_fanouts": 1, "preposed_output_label_nodes": 1,
            "final_target_outgoing_carries": 0, "named_intermediate_outputs": 1,
            "named_final_results": 0, "held_rival_targets_inside_windows": 0,
            "generic_nearest_donor_rules": 0, "adjacency_derived_edges": 0,
        },
        "topologies": {
            "SINGLE_EDGE": 5, "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT": 1,
            "SERIAL_ACTION_OUTPUT_CHAIN": 1,
        },
        "support_profiles": {"A_ONLY": 4, "A_PLUS_B": 1, "A_MINUS_PLUS_B": 1, "B_ONLY": 1},
        "edge_support_tiers": dict(sorted(Counter(row["support_tier"] for row in edges).items())),
        "boundaries": {
            "clause_aligned_window_starts": clause_aligned_starts,
            "nominal_tail_window_starts": 7 - clause_aligned_starts,
            "target_clause_aligned_window_ends": all_end_at_clause_boundary,
        },
        "freeze": {
            "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0, "changed_word_meanings": 0,
            "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0,
        },
        "inputs": {rel(path): digest(path) for path in input_paths},
        "files": {path.name: digest(path) for path in generated_for_hash},
        "next_gap": "Within the same 479-token scope, inventory every occurrence of the action surfaces used by the seven microrecords and test only exact repeated participant frames for additional occurrence-level microrecords; do not use mere adjacency, infer final products, or reopen held rivals.",
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": STATUS, "microrecords": len(micro_rows), "edges_once": sum(edge_usage.values()),
        "window_positions": len(window_positions), "named_intermediate_outputs": 1, "named_final_results": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
