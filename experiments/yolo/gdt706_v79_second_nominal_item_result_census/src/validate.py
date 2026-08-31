#!/usr/bin/env python3
"""Independent validator for GDT706; deliberately does not import run.py."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt706_v79_second_nominal_item_result_census"
SRC, ART = EXP / "src", EXP / "artifacts"
VALIDATION = ART / "VALIDATION.json"
STATUS = (
    "PASS_V79_83_ACTION_DISPOSITIONS__161_DELAYED_PAIRS__28_BOUNDED_CELLS__"
    "1_NEW_C019_BUNDLE_10_HOLDS_17_STOPS__18_EDGES_12_COMPONENTS__ZERO_WORD_DELTA"
)
G703 = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census/artifacts"
G705 = ROOT / "experiments/yolo/gdt705_v78_complete_action_nominal_result_census/artifacts"


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def require(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.checks += 1
        if actual != expected:
            raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def read_tsv(path: Path, audit: Audit) -> tuple[list[str], list[dict[str, str]]]:
    audit.require(path.is_file(), f"missing TSV {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    audit.require(bool(fields), f"empty header {path}")
    audit.equal(len(fields), len(set(fields)), f"unique header {path}")
    for number, row in enumerate(rows, 2):
        audit.require(None not in row, f"extra cells {path}:{number}")
        audit.equal(set(row), set(fields), f"row schema {path}:{number}")
    return fields, rows


def keyed(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    result = {tuple(row[field] for field in fields): row for row in rows}
    if len(result) != len(rows):
        raise AssertionError(f"duplicate key {fields}")
    return result


def one(rows: list[dict[str, str]], label: str, **wanted: str) -> dict[str, str]:
    hits = [row for row in rows if all(row.get(field) == value for field, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"{label}: expected one row for {wanted}, got {len(hits)}")
    return hits[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, Any]:
    a = Audit()
    paths = {
        "spec": SRC / "V79_28_DELAYED_RESULT_CELL_SPECS.tsv",
        "actions": ART / "V79_83_ACTION_DISPOSITIONS.tsv",
        "pairs": ART / "V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv",
        "punct": ART / "V79_2_DELAYED_PUNCTUATION_CONTROLS.tsv",
        "cells": ART / "V79_28_DELAYED_RESULT_CENSUS.tsv",
        "live": ART / "V79_11_LIVE_DELAYED_READINGS.tsv",
        "edge": ART / "V79_1_NEW_DELAYED_RESULT_BUNDLE_EDGE.tsv",
        "memberships": ART / "V79_18_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": ART / "V79_12_CONNECTED_COMPONENTS.tsv",
        "positions": ART / "V79_36_COMPONENT_POSITION_ROLES.tsv",
        "topology": ART / "V79_COMPONENT_TOPOLOGY_CENSUS.tsv",
        "packet": ART / "V79_GDT388_EDGE_PACKET.tsv",
        "tokens": ART / "V79_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": ART / "V79_51_LINE_RELATION_OVERLAY.tsv",
        "spans": ART / "V79_3_BOUND_SPAN_FREEZE.tsv",
    }
    loaded: dict[str, list[dict[str, str]]] = {}
    fields: dict[str, list[str]] = {}
    for name, path in paths.items():
        fields[name], loaded[name] = read_tsv(path, a)
    specs, actions, pairs, punct = loaded["spec"], loaded["actions"], loaded["pairs"], loaded["punct"]
    cells, live, edge = loaded["cells"], loaded["live"], loaded["edge"]
    memberships, components, positions = loaded["memberships"], loaded["components"], loaded["positions"]
    topology = loaded["topology"]
    tokens, lines, spans = loaded["tokens"], loaded["lines"], loaded["spans"]

    old_action_fields, old_actions = read_tsv(G703 / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv", a)
    old_census_fields, old_census = read_tsv(G705 / "V78_60_ACTION_NOMINAL_RESULT_CENSUS.tsv", a)
    old_membership_fields, old_memberships = read_tsv(G705 / "V78_17_EDGE_COMPONENT_MEMBERSHIP.tsv", a)
    old_component_fields, old_components = read_tsv(G705 / "V78_12_CONNECTED_COMPONENTS.tsv", a)
    old_position_fields, old_positions = read_tsv(G705 / "V78_34_COMPONENT_POSITION_ROLES.tsv", a)
    old_token_fields, old_tokens = read_tsv(G705 / "V78_479_TOKEN_RELATION_OVERLAY.tsv", a)
    old_line_fields, old_lines = read_tsv(G705 / "V78_51_LINE_RELATION_OVERLAY.tsv", a)
    old_span_fields, old_spans = read_tsv(G705 / "V78_3_BOUND_SPAN_FREEZE.tsv", a)

    a.equal((len(specs), len(actions), len(pairs), len(punct), len(cells), len(live)),
            (28, 83, 161, 2, 28, 11), "population sizes")
    a.equal((len(edge), len(memberships), len(components), len(positions)), (1, 18, 12, 36), "graph sizes")
    a.equal(len(topology), 31, "topology census size")
    a.equal((len(tokens), len(lines), len(spans)), (479, 51, 3), "overlay sizes")
    a.equal([row["delayed_cell_id"] for row in specs], [f"D{i:03d}" for i in range(1, 29)], "spec IDs")
    a.equal([row["delayed_pair_id"] for row in pairs], [f"P{i:03d}" for i in range(1, 162)], "pair IDs")
    a.equal([row["delayed_pair_id"] for row in punct], ["X001", "X002"], "punctuation IDs")
    a.equal(Counter(row["decision"] for row in specs), Counter({"ADMIT_RESULT_BUNDLE": 1, "HOLD": 10, "STOP": 17}), "spec decisions")
    a.equal(Counter(row["decision"] for row in cells), Counter({"ADMIT_RESULT_BUNDLE": 1, "HOLD": 10, "STOP": 17}), "cell decisions")
    a.equal(Counter(row["target_rank"] for row in cells), Counter({"2": 16, "3": 12}), "cell ranks")
    a.require(all(row["portable_default"] == "NO" for row in specs + cells), "no portable default")
    a.require(all(row["status"] == STATUS for rows in loaded.values() for row in rows if "status" in row), "one output status")
    a.require(all(not row["page"].startswith("f84") for row in tokens), "no f84 token")

    old_token_index = keyed(old_tokens, ("locus", "token_ordinal"))
    old_action_index = keyed(old_actions, ("action_case_id",))
    old_census_index = keyed(old_census, ("action_case_id",))
    action_index = keyed(actions, ("action_case_id",))
    a.equal(list(action_index), list(old_action_index), "action order and IDs")
    copied_action = [
        "page", "locus", "action_clause_id", "action_clause_start", "action_clause_end",
        "action_clause_surfaces", "action_ordinal", "action_surface", "action_gloss_de",
        "right_clause_id", "right_clause_type", "right_clause_start", "right_clause_end",
        "right_first_ordinal", "right_first_surface", "right_first_gloss_de",
    ]
    for case_key, row in action_index.items():
        old = old_action_index[case_key]
        for field in copied_action:
            a.equal(row[field], old[field], f"{case_key[0]} copied action {field}")
        if old["right_clause_type"] == "NOMINAL_BLOCK":
            source = old_census_index[case_key]
            a.equal(row["v78_decision"], source["decision"], f"{case_key[0]} V78 decision")
            start, end = int(old["right_clause_start"]), int(old["right_clause_end"])
            raw_count = end - start + 1
            semantic_count = sum(
                old_token_index[(old["locus"], str(ordinal))]["v78_token_gloss_de"] != "."
                for ordinal in range(start, end + 1)
            )
            a.equal(
                (row["nominal_raw_position_count"], row["nominal_semantic_item_count"],
                 row["later_raw_position_count"], row["later_semantic_item_count"]),
                (str(raw_count), str(semantic_count), str(max(raw_count - 1, 0)),
                 str(max(semantic_count - 1, 0))), f"{case_key[0]} window counts",
            )
        else:
            a.equal(row["v78_decision"], "OUTSIDE_ACTION_TO_NOMINAL_CENSUS", f"{case_key[0]} outside V78")
    a.equal(Counter(row["disposition"] for row in actions), Counter({
        "IMMEDIATE_RESULT_ALREADY_BOUND": 5, "DELAYED_NOMINAL_WINDOW": 42,
        "SINGLE_NOMINAL_ITEM_NO_DELAY": 13, "NEXT_ACTION_BOUNDARY": 15, "END_OF_LINE": 8,
    }), "action dispositions")
    a.equal(sum(int(row["later_raw_position_count"]) for row in actions if row["disposition"] == "DELAYED_NOMINAL_WINDOW"), 163, "raw delayed count")
    a.equal(sum(int(row["later_semantic_item_count"]) for row in actions if row["disposition"] == "DELAYED_NOMINAL_WINDOW"), 161, "semantic delayed count")

    reconstructed: list[tuple[str, str, str, str, str, str]] = []
    reconstructed_punct: list[tuple[str, str, str]] = []
    for source in actions:
        if source["disposition"] != "DELAYED_NOMINAL_WINDOW":
            continue
        start, end = int(source["right_clause_start"]), int(source["right_clause_end"])
        for ordinal in range(start + 1, end + 1):
            target = old_token_index[(source["locus"], str(ordinal))]
            rank = str(ordinal - start + 1)
            bridge_ordinals = "|".join(str(value) for value in range(start, ordinal))
            bridge_surfaces = "|".join(old_token_index[(source["locus"], str(value))]["surface"] for value in range(start, ordinal))
            if target["v78_token_gloss_de"] == ".":
                reconstructed_punct.append((source["action_case_id"], str(ordinal), target["surface"]))
            else:
                reconstructed.append((source["action_case_id"], rank, str(ordinal), target["surface"], bridge_ordinals, bridge_surfaces))
    observed_pairs = [
        (row["action_case_id"], row["target_rank"], row["target_ordinal"], row["target_surface"], row["intervening_ordinals"], row["intervening_surfaces"])
        for row in pairs
    ]
    a.equal(observed_pairs, reconstructed, "exhaustive delayed pair reconstruction")
    a.equal([(row["action_case_id"], row["target_ordinal"], row["target_surface"]) for row in punct], reconstructed_punct, "punctuation reconstruction")
    a.equal(set(reconstructed_punct), {("A043", "6", "y"), ("A047", "10", "dy")}, "two exact punctuation controls")
    for row in pairs:
        expected_inner = int(row["v78_decision"] == "OPEN_PARTIAL" and row["target_rank"] in {"2", "3"})
        a.equal(row["inner_v79_window"], str(expected_inner), f"inner flag {row['delayed_pair_id']}")
        a.equal(row["semantic_item"], "1", f"semantic pair {row['delayed_pair_id']}")
        a.require(int(row["right_clause_start"]) < int(row["target_ordinal"]) <= int(row["right_clause_end"]), f"same block {row['delayed_pair_id']}")
    a.equal(sum(row["inner_v79_window"] == "1" for row in pairs), 28, "28 inner cells")

    spec_index = keyed(specs, ("delayed_cell_id",))
    cell_index = keyed(cells, ("delayed_cell_id",))
    inner_index = keyed([row for row in pairs if row["inner_v79_window"] == "1"], ("action_case_id", "target_rank"))
    a.equal(set((row["action_case_id"], row["target_rank"]) for row in cells), set(inner_index), "cells exhaust inner window")
    for cell_id, row in cell_index.items():
        spec, pair = spec_index[cell_id], inner_index[(row["action_case_id"], row["target_rank"])]
        a.equal((row["target_ordinal"], row["target_surface"]),
                (spec["expected_target_ordinal"], spec["expected_target_surface"]), f"{cell_id[0]} target spec")
        a.equal((row["bridge_ordinals"], row["bridge_surfaces"]),
                (spec["expected_bridge_ordinals"], spec["expected_bridge_surfaces"]), f"{cell_id[0]} bridge spec")
        for source_field, output_field in [
            ("decision", "decision"), ("result_role", "result_role"),
            ("practical_reading_de", "practical_reading_de"),
            ("bridge_interpretation_de", "bridge_interpretation_de"),
            ("decisive_reason_de", "decisive_reason_de"), ("portable_default", "portable_default"),
        ]:
            a.equal(row[output_field], spec[source_field], f"{cell_id[0]} spec {output_field}")
        a.equal((row["locus"], row["target_gloss_de"], row["bridge_glosses_de"]),
                (pair["locus"], pair["target_gloss_de"], pair["intervening_glosses_de"]), f"{cell_id[0]} pair join")
        a.equal((row["full_window_exact"], row["word_delta"]), ("1", "0"), f"{cell_id[0]} flags")
    a.equal([row["delayed_cell_id"] for row in live], [row["delayed_cell_id"] for row in cells if row["decision"] != "STOP"], "live subset exact")

    d026 = one(cells, "D026", delayed_cell_id="D026")
    a.equal((d026["action_case_id"], d026["locus"], d026["action_ordinal"], d026["action_surface"]),
            ("A077", "f86v6.25", "5", "ykaiin"), "D026 source")
    a.equal((d026["bridge_ordinals"], d026["bridge_surfaces"], d026["target_ordinal"], d026["target_surface"]),
            ("6", "or", "7", "okeeeey"), "D026 bundle members")
    a.equal((d026["admitted_result_bundle_ordinals"], d026["admitted_result_bundle_surfaces"]),
            ("6|7", "or|okeeeey"), "D026 bundle retained")
    a.require("nicht übersprungen" in d026["bridge_interpretation_de"], "D026 explicitly does not skip #6")
    d027 = one(cells, "D027", delayed_cell_id="D027")
    a.equal((d027["decision"], d027["target_ordinal"], d027["target_surface"]), ("STOP", "8", "ofchedy"), "post-C019 blocker")

    c019 = one(edge, "C019 edge", edge_id="C019")
    a.equal((c019["component_id"], c019["locus"], c019["edge_node_ordinals"]), ("M007", "f86v6.25", "5|7"), "C019 endpoints")
    a.equal((c019["intervening_ordinal"], c019["intervening_surface"], c019["rendered_result_bundle_ordinals"]),
            ("6", "or", "6|7"), "C019 visible bridge")
    a.equal((c019["portability"], c019["gdt388_score_ready"], c019["edge_delta"], c019["word_delta"]),
            ("OCCURRENCE_BOUND_ONLY", "0", "1", "0"), "C019 flags")

    old_membership_index = keyed(old_memberships, ("edge_id",))
    membership_index = keyed(memberships, ("edge_id",))
    a.equal(set(membership_index), {(f"C{i:03d}",) for i in range(1, 20) if i != 16}, "edge IDs")
    immutable_membership = [
        "edge_id", "component_id", "locus", "support_tier", "relation_class",
        "edge_node_ordinals", "source_ordinals", "target_ordinal", "target_role", "origin",
        "v75_change", "v76_change", "v77_change", "v78_change",
    ]
    for edge_key, old in old_membership_index.items():
        new = membership_index[edge_key]
        for field in immutable_membership:
            a.equal(new[field], old[field], f"{edge_key[0]} immutable {field}")
        if old["component_id"] == "M007":
            a.equal((new["component_edge_count"], new["component_topology"], new["shared_edge_node_ordinals"]),
                    ("3", "SERIAL_ACTION_OUTPUT_CHAIN_WITH_DELAYED_RESULT", "4|5"), f"{edge_key[0]} M007 denormalization")
        else:
            for field in ("component_edge_count", "component_topology", "shared_edge_node_ordinals"):
                a.equal(new[field], old[field], f"{edge_key[0]} unchanged {field}")
    c019m = membership_index[("C019",)]
    a.equal((c019m["component_id"], c019m["edge_node_ordinals"], c019m["source_ordinals"], c019m["target_ordinal"]),
            ("M007", "5|7", "5", "7"), "C019 membership")
    node_keys = {(row["locus"], ordinal) for row in memberships for ordinal in row["edge_node_ordinals"].split("|")}
    a.equal(len(node_keys), 33, "unique graph nodes")
    a.equal(sum(len(row["edge_node_ordinals"].split("|")) for row in memberships), 39, "edge incidences")

    old_component_index = keyed(old_components, ("component_id",))
    component_index = keyed(components, ("component_id",))
    a.equal(set(component_index), {(f"M{i:03d}",) for i in range(1, 13)}, "component IDs")
    for component_key, old in old_component_index.items():
        new = component_index[component_key]
        if component_key != ("M007",):
            for field in old_component_fields[:-1]:
                a.equal(new[field], old[field], f"{component_key[0]} unchanged {field}")
            a.equal((new["v79_edge_delta"], new["v79_change"]), ("0", "NONE"), f"{component_key[0]} V79 unchanged")
    m007 = component_index[("M007",)]
    a.equal((m007["edge_ids"], m007["edge_count"], m007["edge_node_ordinals"], m007["shared_edge_node_ordinals"]),
            ("C007|C006|C019", "3", "2|3|4|5|7", "4|5"), "M007 graph")
    a.equal((m007["edge_hull_start"], m007["edge_hull_end"], m007["edge_hull_position_count"], m007["hull_only_ordinals"]),
            ("2", "7", "6", "6"), "M007 hull")
    a.equal((m007["render_window_start"], m007["render_window_end"], m007["render_window_token_count"]),
            ("2", "7", "6"), "M007 render")
    a.equal((m007["v79_edge_delta"], m007["v79_change"]), ("1", "COMPONENT_EXTENDED"), "M007 delta")
    a.equal(sum(int(row["edge_hull_position_count"]) for row in components), 36, "hull total")
    a.equal(sum(int(row["render_window_token_count"]) for row in components), 36, "render total")

    old_position_index = keyed(old_positions, ("locus", "token_ordinal"))
    position_index = keyed(positions, ("locus", "token_ordinal"))
    for key, old in old_position_index.items():
        if old["component_id"] == "M007":
            continue
        new = position_index[key]
        for field in old_position_fields[:-1]:
            a.equal(new[field], old[field], f"position {key} unchanged {field}")
        a.equal(new["v79_change"], "NONE", f"position {key} no change")
    a.equal(Counter(row["membership_class"] for row in positions), Counter({"EDGE_NODE": 33, "HULL_ONLY": 3}), "position classes")
    a.equal(sum(row["is_shared_edge_node"] == "1" for row in positions), 6, "shared positions")
    m007_positions = [position_index[("f86v6.25", str(ordinal))] for ordinal in range(2, 8)]
    a.equal([row["render_position"] for row in m007_positions], [str(value) for value in range(1, 7)], "M007 render order")
    a.require(all(row["render_size"] == "6" for row in m007_positions), "M007 render size")
    p5, p6, p7 = m007_positions[3:]
    a.equal((p5["membership_class"], p5["edge_ids"], p5["is_shared_edge_node"]), ("EDGE_NODE", "C006|C019", "1"), "C019 source position")
    a.equal((p6["surface"], p6["membership_class"], p6["edge_ids"], p6["is_edge_node"], p6["is_hull_only"]),
            ("or", "HULL_ONLY", "NONE", "0", "1"), "visible bridge is hull-only")
    a.equal((p6["component_role"], p6["action_output_role"]),
            ("RESULT_BUNDLE_MATERIAL_CARRIER:C019", "WRITTEN_C019_RESULT_MATERIAL_CARRIER_NOT_EDGE_NODE"),
            "visible bridge exact roles")
    a.equal((p7["surface"], p7["membership_class"], p7["edge_ids"], p7["target_edge_ids"]),
            ("okeeeey", "EDGE_NODE", "C019", "C019"), "C019 target position")

    topology_index = keyed(topology, ("dimension", "value"))
    expected_topology_counts = {
        ("DELAYED_UNIVERSE", "SEMANTIC_PAIR"): 161,
        ("DELAYED_UNIVERSE", "PUNCTUATION_CONTROL"): 2,
        ("BOUNDED_DECISION", "ADMIT_RESULT_BUNDLE"): 1,
        ("BOUNDED_DECISION", "HOLD"): 10,
        ("BOUNDED_DECISION", "STOP"): 17,
        ("POSITION_CLASS", "EDGE_NODE"): 33,
        ("POSITION_CLASS", "HULL_ONLY_NOT_NODE"): 3,
        ("POSITION_CLASS", "RENDER_ONLY_STRUCTURAL"): 0,
        ("STRUCTURAL_ROLE", "CLAUSE_CLOSURE_NONNODE"): 1,
        ("GRAPH_COUNT", "EDGE_INCIDENCE"): 39,
        ("GRAPH_COUNT", "MINIMAL_HULL_POSITION"): 36,
        ("GRAPH_COUNT", "RENDER_POSITION"): 36,
    }
    for key, expected in expected_topology_counts.items():
        a.equal(int(topology_index[key]["count"]), expected, f"topology count {key}")
    for disposition, expected in Counter(row["disposition"] for row in actions).items():
        a.equal(int(topology_index[("ACTION_DISPOSITION", disposition)]["count"]), expected,
                f"topology action disposition {disposition}")

    for new, old in zip(tokens, old_tokens):
        for field in old_token_fields:
            a.equal(new[field], old[field], f"token {old['locus']}#{old['token_ordinal']} inherited {field}")
        a.equal(new["v79_token_gloss_de"], old["v78_token_gloss_de"], f"token {old['locus']}#{old['token_ordinal']} gloss")
        a.equal((new["v79_word_delta"], new["v79_status"]), ("0", STATUS), f"token {old['locus']}#{old['token_ordinal']} flags")
    c019_tokens = [(row["locus"], row["token_ordinal"]) for row in tokens if row["v79_new_delayed_result_edge_ids"] == "C019"]
    a.equal(c019_tokens, [("f86v6.25", "5"), ("f86v6.25", "7")], "C019 token endpoints")
    token6 = one(tokens, "f86v6.25#6", locus="f86v6.25", token_ordinal="6")
    a.equal((token6["surface"], token6["v79_component_membership_class"], token6["v79_new_delayed_result_edge_ids"]),
            ("or", "HULL_ONLY", "NONE"), "bridge retained without edge incidence")
    a.require("ADMITTED_RESULT_MATERIAL_CARRIER" in token6["v79_delayed_cell_roles"], "bridge role visible")

    for new, old in zip(lines, old_lines):
        for field in old_line_fields:
            a.equal(new[field], old[field], f"line {old['locus']} inherited {field}")
        a.equal(new["v79_line_translation_de"], old["v78_line_translation_de"], f"line {old['locus']} translation")
    a.equal([(row["locus"], row["v79_new_delayed_result_edge_ids"]) for row in lines if row["v79_new_delayed_result_edge_ids"] != "NONE"],
            [("f86v6.25", "C019")], "one C019 line")
    for new, old in zip(spans, old_spans):
        for field in old_span_fields:
            a.equal(new[field], old[field], f"span {old['span_id']} inherited {field}")
        a.equal((new["v79_selected_gloss_de"], new["v79_byte_identical"], new["v79_relation_change"]),
                (old["v78_selected_gloss_de"], "1", "NONE"), f"span {old['span_id']} frozen")

    packet = loaded["packet"]
    a.equal(len(packet), 1, "one GDT388 row")
    a.equal((packet[0]["edge_id"], packet[0]["physical_folio"], packet[0]["formal_access_state"]),
            ("C019", "f86", "FORMAL_ACCESSED"), "packet identity")
    command = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(paths["packet"].relative_to(ROOT))],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    a.equal(command.returncode, 1, "GDT388 return code")
    a.equal(command.stderr, "", "GDT388 stderr")
    a.equal(json.loads(command.stdout), expected_intake, "GDT388 output")
    a.equal(json.loads((ART / "V79_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8")), expected_intake, "stored intake")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    a.equal(result["status"], STATUS, "result status")
    expected_basis = {
        "action_clauses": 83, "result_unwritten_actions_before": 78,
        "result_unwritten_actions_after": 77, "censused_delayed_nominal_windows": 42,
        "delayed_nominal_windows_unresolved_after": 41,
        "raw_delayed_positions": 163, "punctuation_controls": 2, "semantic_delayed_pairs": 161,
        "bounded_delayed_cells": 28, "rank2_cells": 16, "rank3_cells": 12,
        "new_admits": 1, "holds": 10, "stops": 17, "relation_edges_after": 18,
        "connected_components": 12, "edge_nodes": 33, "edge_node_incidences": 39,
        "minimal_hull_positions": 36, "render_positions": 36, "shared_edge_nodes": 6,
        "hull_only_positions": 3, "new_pages": 0, "f84_access": 0, "f84r_access": 0,
    }
    for field, expected in expected_basis.items():
        a.equal(result["basis"][field], expected, f"result basis {field}")
    a.equal(result["decision"]["new_edge_ids"], ["C019"], "result edge")
    a.equal(result["decision"]["rendered_result_bundle"], "f86v6.25#6-7", "result bundle")
    a.equal(result["decision"]["intervening_material_carrier_is_edge_node"], False, "bridge is not endpoint")
    a.equal(result["word_preservation"], {
        "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
        "bound_spans_byte_identical": 3, "new_word_meanings": 0,
        "changed_word_meanings": 0, "content_word_additions": 0,
        "content_word_deletions": 0, "content_word_reorders": 0,
    }, "word preservation")
    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        a.require(path.is_file(), f"hashed input exists {relative}")
        a.equal(sha256(path), digest, f"input hash {relative}")
    for filename, digest in result["files"].items():
        path = ART / filename
        a.require(path.is_file(), f"hashed file exists {filename}")
        a.equal(sha256(path), digest, f"hash {filename}")

    return {
        "status": "PASS", "experiment_status": STATUS, "checks": a.checks,
        "populations": {
            "actions": 83, "semantic_delayed_pairs": 161, "bounded_cells": 28,
            "admitted": 1, "holds": 10, "stops": 17,
        },
        "graph": {
            "edges": 18, "components": 12, "edge_nodes": 33,
            "incidences": 39, "render_positions": 36, "hull_only": 3, "shared": 6,
        },
        "new_edge": "C019", "new_word_meanings": 0,
    }


def main() -> int:
    result = validate()
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
