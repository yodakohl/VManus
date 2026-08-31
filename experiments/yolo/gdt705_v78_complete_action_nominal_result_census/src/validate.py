#!/usr/bin/env python3
"""Independent validator for GDT705; deliberately does not import run.py."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt705_v78_complete_action_nominal_result_census"
SRC, ART = EXP / "src", EXP / "artifacts"
VALIDATION = ART / "VALIDATION.json"
STATUS = (
    "PASS_V78_60_ACTION_NOMINAL_RESULTS__2_NEW_C017_C018__5_NEW_HOLDS__"
    "20_OPEN_26_CONTROLS__17_EDGES_12_COMPONENTS__ZERO_WORD_DELTA"
)
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G703 = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census/artifacts"
G704 = ROOT / "experiments/yolo/gdt704_v77_repeated_written_material_continuation/artifacts"


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(rows: list[dict[str, str]], label: str, **wanted: str) -> dict[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"{label}: expected one row for {wanted}, got {len(hits)}")
    return hits[0]


def keyed(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    return {tuple(row[field] for field in fields): row for row in rows}


def validate() -> dict[str, Any]:
    a = Audit()
    paths = {
        "decision_spec": SRC / "V78_60_ACTION_NOMINAL_DECISION_SPECS.tsv",
        "leading_spec": SRC / "V78_7_LEADING_RESULT_CASE_SPECS.tsv",
        "census": ART / "V78_60_ACTION_NOMINAL_RESULT_CENSUS.tsv",
        "leading": ART / "V78_7_LEADING_RESULT_CANDIDATES.tsv",
        "sheky": ART / "V78_3_SHEKY_OCCURRENCE_CONTRAST.tsv",
        "dchey": ART / "V78_2_DCHEY_TARGET_CONTRAST.tsv",
        "edges": ART / "V78_2_NEW_LOCAL_RESULT_EDGES.tsv",
        "memberships": ART / "V78_17_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": ART / "V78_12_CONNECTED_COMPONENTS.tsv",
        "positions": ART / "V78_34_COMPONENT_POSITION_ROLES.tsv",
        "topology": ART / "V78_COMPONENT_TOPOLOGY_CENSUS.tsv",
        "packet": ART / "V78_GDT388_EDGE_PACKET.tsv",
        "intake": ART / "V78_GDT388_EDGE_INTAKE.json",
        "tokens": ART / "V78_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": ART / "V78_51_LINE_RELATION_OVERLAY.tsv",
        "spans": ART / "V78_3_BOUND_SPAN_FREEZE.tsv",
        "result": ART / "RESULT.json",
    }
    loaded = {name: read_tsv(path, a)[1] for name, path in paths.items() if path.suffix == ".tsv"}
    specs, leading_specs = loaded["decision_spec"], loaded["leading_spec"]
    census, leading = loaded["census"], loaded["leading"]
    sheky, dchey, edges = loaded["sheky"], loaded["dchey"], loaded["edges"]
    memberships, components = loaded["memberships"], loaded["components"]
    positions, topology = loaded["positions"], loaded["topology"]
    packet, tokens, lines, spans = loaded["packet"], loaded["tokens"], loaded["lines"], loaded["spans"]

    _, old_actions = read_tsv(G703 / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv", a)
    _, old_finished = read_tsv(G703 / "V76_7_FINISHED_RESULT_FIRSTS.tsv", a)
    _, clauses = read_tsv(G695, a)
    _, old_memberships = read_tsv(G704 / "V77_15_EDGE_COMPONENT_MEMBERSHIP.tsv", a)
    _, old_components = read_tsv(G704 / "V77_10_CONNECTED_COMPONENTS.tsv", a)
    _, old_positions = read_tsv(G704 / "V77_30_COMPONENT_POSITION_ROLES.tsv", a)
    _, old_tokens = read_tsv(G704 / "V77_479_TOKEN_RELATION_OVERLAY.tsv", a)
    _, old_lines = read_tsv(G704 / "V77_51_LINE_RELATION_OVERLAY.tsv", a)
    _, old_spans = read_tsv(G704 / "V77_3_BOUND_SPAN_FREEZE.tsv", a)

    expected_decisions = Counter({
        "ADMIT_NEW": 2, "HOLD_NEW": 5, "REPLAY_ADMITTED": 3,
        "RETAIN_PRIOR_HOLD": 4, "OPEN_PARTIAL": 20, "CONTROL_CONFLICT": 26,
    })
    nominal_old = [row for row in old_actions if row["right_clause_type"] == "NOMINAL_BLOCK"]
    a.equal((len(old_actions), len(nominal_old), len(census), len(specs)), (83, 60, 60, 60), "complete populations")
    expected_ids = [row["action_case_id"] for row in nominal_old]
    a.equal([row["action_case_id"] for row in specs], expected_ids, "spec order")
    a.equal([row["action_case_id"] for row in census], expected_ids, "census order")
    a.equal(Counter(row["decision"] for row in specs), expected_decisions, "source decision counts")
    a.equal(Counter(row["decision"] for row in census), expected_decisions, "output decision counts")
    a.require(all(row["portable_default"] == "NO" for row in specs), "no portable defaults")

    spec_index = {row["action_case_id"]: row for row in specs}
    census_index = {row["action_case_id"]: row for row in census}
    old_index = {row["action_case_id"]: row for row in nominal_old}
    prior_index = {row["action_case_id"]: row for row in old_finished}
    copied = [
        "page", "locus", "action_clause_id", "action_clause_start", "action_clause_end",
        "action_clause_surfaces", "action_ordinal", "action_surface", "action_gloss_de",
        "right_clause_id", "right_clause_start", "right_clause_end", "right_first_ordinal",
        "right_first_surface", "right_first_gloss_de", "right_dispatch", "right_confidence",
    ]
    spec_copied = [
        "operation_agreement", "degree_agreement", "material_agreement", "completion_agreement",
        "result_role", "competing_or_missing_patient", "decision", "decision_reason_de", "portable_default",
    ]
    for case_id in expected_ids:
        old, new, spec = old_index[case_id], census_index[case_id], spec_index[case_id]
        for field in copied:
            a.equal(new[field], old[field], f"{case_id} copied {field}")
        for field in spec_copied:
            a.equal(new[field], spec[field], f"{case_id} spec {field}")
        prior = prior_index.get(case_id)
        a.equal(new["prior_candidate_id"], prior["candidate_id"] if prior else "NONE", f"{case_id} prior ID")
        a.equal(new["prior_candidate_decision"], prior["decision"] if prior else "OUTSIDE_V76_SEVEN_CASE_GATE", f"{case_id} prior decision")
        a.equal((new["full_clause_then_first_item_exact"], new["word_delta"], new["status"]), ("1", "0", STATUS), f"{case_id} flags")

    # Explicitly guard the audit corrections that prevent exaggerated agreement labels.
    for case_id, expected in {
        "A043": ("DRY_STATE_RELATED", "UNSPECIFIED"),
        "A046": ("SINGLE_EXACT", "UNSPECIFIED"),
        "A047": ("CONFLICT", "UNSPECIFIED"),
        "A070": ("NONE", "UNSPECIFIED"),
        "A077": ("NONE", "UNSPECIFIED"),
        "A078": ("QUANTITY_RELATED", "UNSPECIFIED"),
    }.items():
        row = census_index[case_id]
        a.equal((row["operation_agreement"], row["degree_agreement"]), expected, f"corrected taxonomy {case_id}")
    a.equal(census_index["A057"]["material_agreement"], "MATERIAL_IDENTITY_UNRESOLVED", "C017 material open")
    a.require("SHECKHY_ARZNEIKOMPOSITUM" in census_index["A057"]["competing_or_missing_patient"], "C017 names left patient")
    a.equal((census_index["A056"]["operation_agreement"], census_index["A056"]["completion_agreement"], census_index["A056"]["material_agreement"]),
            ("ONE_OPERATION_PLUS_COMPLETION_EQUIVALENT", "SEMANTIC_EQUIVALENT", "GENERIC_PORTION_NO_MATERIAL_HEAD"), "C018 exactness ceiling")

    a.equal((len(leading_specs), len(leading)), (7, 7), "leading deck size")
    a.equal([row["candidate_id"] for row in leading_specs], [f"R{i:03d}" for i in range(1, 8)], "leading IDs")
    a.equal([row["action_case_id"] for row in leading_specs], ["A057", "A056", "A066", "A072", "A046", "A006", "A043"], "leading ranking")
    a.equal(Counter(row["decision"] for row in leading), Counter({"ADMIT_NEW": 2, "HOLD_NEW": 5}), "leading decisions")
    leading_spec_index = {row["candidate_id"]: row for row in leading_specs}
    for row in leading:
        source = leading_spec_index[row["candidate_id"]]
        for field, value in source.items():
            a.equal(row[field], value, f"leading {row['candidate_id']} source {field}")
        census_row = census_index[row["action_case_id"]]
        a.equal((row["action_surface"], row["target_surface"], row["decision"]),
                (census_row["action_surface"], census_row["right_first_surface"], census_row["decision"]),
                f"leading {row['candidate_id']} occurrence")

    a.equal([row["action_case_id"] for row in sheky], ["A057", "A058", "A060"], "three sheky cases")
    a.require(all(row["action_surface"] == "sheky" for row in sheky), "same SHEKY surface")
    a.equal(Counter(row["right_clause_type"] for row in sheky), Counter({"NOMINAL_BLOCK": 2, "ACTION_CLAUSE": 1}), "SHEKY right types")
    a.equal([(row["action_case_id"], row["decision"]) for row in sheky],
            [("A057", "ADMIT_NEW_C017"), ("A058", "CONTROL_NO_RESULT_LABEL"), ("A060", "CONTROL_CONFLICT")], "SHEKY decisions")
    a.equal([(row["action_case_id"], row["right_first_surface"], row["decision"]) for row in dchey],
            [("A056", "dchey", "ADMIT_NEW"), ("A043", "dchey", "HOLD_NEW")], "DCHEY target contrast")

    a.equal(len(edges), 2, "two new edges")
    c017, c018 = one(edges, "C017", edge_id="C017"), one(edges, "C018", edge_id="C018")
    for row, expected in [
        (c017, ("M011", "f80r.17", "3", "3", "sheky", "4", "shkeol", "B_WORKING_LOCAL")),
        (c018, ("M012", "f7r.2", "5", "5", "dold", "6", "dchey", "B_LOW_WORKING_LOCAL")),
    ]:
        a.equal((row["component_id"], row["locus"], row["source_clause_ordinals"], row["source_action_ordinal"],
                 row["source_action_surface"], row["written_result_ordinal"], row["written_result_surface"], row["support_tier"]),
                expected, f"edge occurrence {row['edge_id']}")
        a.equal((row["portability"], row["gdt388_score_ready"], row["edge_delta"], row["word_delta"], row["status"]),
                ("OCCURRENCE_BOUND_ONLY", "0", "1", "0", STATUS), f"edge flags {row['edge_id']}")
    a.equal(c017["written_result_gloss_de"], "eingeweichter Drogenstoff, bis Mittelstufe erhitzt", "C017 exact target wording")
    a.require("sheckhy" in c017["strongest_rival_de"], "C017 rival names sheckhy")
    a.equal((c018["operation_agreement"], c018["completion_agreement"], c018["material_agreement"]),
            ("ONE_OPERATION_PLUS_COMPLETION_EQUIVALENT", "SEMANTIC_EQUIVALENT", "GENERIC_PORTION_NO_MATERIAL_HEAD"), "C018 edge ceiling")

    clause_index = keyed(clauses, ("locus", "clause_id"))
    token_index = keyed(old_tokens, ("locus", "token_ordinal"))
    for edge, action_case in ((c017, "A057"), (c018, "A056")):
        census_row = census_index[action_case]
        clause = clause_index[(edge["locus"], census_row["action_clause_id"])]
        a.equal((clause["start_ordinal"], clause["end_ordinal"], clause["surfaces"]),
                (census_row["action_clause_start"], census_row["action_clause_end"], census_row["action_clause_surfaces"]),
                f"{edge['edge_id']} source clause")
        a.equal(token_index[(edge["locus"], edge["written_result_ordinal"])]["surface"], edge["written_result_surface"], f"{edge['edge_id']} target token")

    # Cumulative graph: old rows stay semantically intact and the two pairs are disjoint.
    a.equal((len(old_memberships), len(memberships)), (15, 17), "membership sizes")
    a.equal({row["edge_id"] for row in memberships}, {f"C{i:03d}" for i in range(1, 19) if i != 16}, "edge IDs with held C016 gap")
    old_by_edge = {row["edge_id"]: row for row in old_memberships}
    new_by_edge = {row["edge_id"]: row for row in memberships}
    immutable = [
        "edge_id", "component_id", "locus", "support_tier", "relation_class",
        "edge_node_ordinals", "source_ordinals", "target_ordinal", "target_role", "origin",
    ]
    for edge_id, old in old_by_edge.items():
        for field in immutable:
            a.equal(new_by_edge[edge_id][field], old[field], f"unchanged {edge_id} {field}")
    a.equal((new_by_edge["C017"]["component_id"], new_by_edge["C017"]["locus"], new_by_edge["C017"]["edge_node_ordinals"]),
            ("M011", "f80r.17", "3|4"), "C017 membership")
    a.equal((new_by_edge["C018"]["component_id"], new_by_edge["C018"]["locus"], new_by_edge["C018"]["edge_node_ordinals"]),
            ("M012", "f7r.2", "5|6"), "C018 membership")
    a.require("C016" not in new_by_edge, "C016 remains absent")

    all_nodes: set[tuple[str, str]] = set()
    incidence_count = 0
    parent: dict[tuple[str, str], tuple[str, str]] = {}

    def find(node: tuple[str, str]) -> tuple[str, str]:
        parent.setdefault(node, node)
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    def union(left: tuple[str, str], right: tuple[str, str]) -> None:
        root_l, root_r = find(left), find(right)
        if root_l != root_r:
            parent[root_r] = root_l

    for row in memberships:
        nodes = [(row["locus"], ordinal) for ordinal in row["edge_node_ordinals"].split("|")]
        all_nodes.update(nodes); incidence_count += len(nodes)
        for node in nodes[1:]:
            union(nodes[0], node)
    graph_components: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for node in all_nodes:
        graph_components[find(node)].add(node)
    a.equal((len(all_nodes), incidence_count, len(graph_components)), (32, 37, 12), "recomputed graph 32/37/12")
    a.equal((len(old_components), len(components), sum(int(row["edge_count"]) for row in components)), (10, 12, 17), "component totals")
    a.equal(sum(int(row["edge_hull_position_count"]) for row in components), 34, "hull positions")
    a.equal(sum(int(row["render_window_token_count"]) for row in components), 34, "render positions")
    expected_partition = {
        frozenset({"C009"}), frozenset({"C001", "C012"}), frozenset({"C002"}),
        frozenset({"C003"}), frozenset({"C004", "C008"}), frozenset({"C005"}),
        frozenset({"C006", "C007"}), frozenset({"C010"}),
        frozenset({"C011", "C013", "C015"}), frozenset({"C014"}),
        frozenset({"C017"}), frozenset({"C018"}),
    }
    a.equal({frozenset(row["edge_ids"].split("|")) for row in components}, expected_partition, "component partition")
    m011, m012 = one(components, "M011", component_id="M011"), one(components, "M012", component_id="M012")
    a.equal((m011["locus"], m011["edge_ids"], m011["edge_node_ordinals"], m011["edge_hull_start"], m011["edge_hull_end"], m011["topology"]),
            ("f80r.17", "C017", "3|4", "3", "4", "ACTION_WRITTEN_PROCESSED_MATERIAL_PAIR"), "M011 exact")
    a.equal((m012["locus"], m012["edge_ids"], m012["edge_node_ordinals"], m012["edge_hull_start"], m012["edge_hull_end"], m012["topology"]),
            ("f7r.2", "C018", "5|6", "5", "6", "ACTION_WRITTEN_FINISHED_PORTION_PAIR"), "M012 exact")
    a.require("ungebundene spätere Registereinträge" in m012["boundary_note_de"], "M012 boundary wording")

    a.equal((len(old_positions), len(positions)), (30, 34), "position sizes")
    a.equal(len({(row["locus"], row["token_ordinal"]) for row in positions}), 34, "unique positions")
    a.equal(Counter(row["membership_class"] for row in positions), Counter({"EDGE_NODE": 32, "HULL_ONLY": 2}), "position classes")
    a.equal(sum(int(row["is_shared_edge_node"]) for row in positions), 5, "shared nodes unchanged")
    a.equal(sum(int(row["is_render_only_structural"]) for row in positions), 0, "no render-only structural")
    for locus, ordinal, surface, component, edge in [
        ("f80r.17", "3", "sheky", "M011", "C017"),
        ("f80r.17", "4", "shkeol", "M011", "C017"),
        ("f7r.2", "5", "dold", "M012", "C018"),
        ("f7r.2", "6", "dchey", "M012", "C018"),
    ]:
        row = one(positions, "new graph position", locus=locus, token_ordinal=ordinal)
        a.equal((row["surface"], row["component_id"], row["edge_ids"], row["membership_class"]),
                (surface, component, edge, "EDGE_NODE"), f"new position {locus}#{ordinal}")
    p7 = one(positions, "structural f26 #7", locus="f26r.2", token_ordinal="7")
    a.equal((p7["surface"], p7["membership_class"], p7["is_hull_only"]), ("dy", "HULL_ONLY", "1"), "sole structural closure unchanged")
    topology_index = {(row["dimension"], row["value"]): row for row in topology}
    for key, count in {
        ("POSITION_CLASS", "EDGE_NODE"): "32", ("POSITION_CLASS", "HULL_ONLY_NOT_NODE"): "2",
        ("POSITION_CLASS", "RENDER_ONLY_STRUCTURAL"): "0", ("STRUCTURAL_ROLE", "CLAUSE_CLOSURE_NONNODE"): "1",
        ("GRAPH_COUNT", "EDGE_INCIDENCE"): "37", ("GRAPH_COUNT", "MINIMAL_HULL_POSITION"): "34",
        ("GRAPH_COUNT", "RENDER_POSITION"): "34", ("RESULT_DECISION", "ADMIT_NEW"): "2",
        ("RESULT_DECISION", "HOLD_NEW"): "5", ("RESULT_DECISION", "OPEN_PARTIAL"): "20",
        ("RESULT_DECISION", "CONTROL_CONFLICT"): "26", ("SURFACE_CONTROL", "SHEKY_OCCURRENCES"): "3",
        ("TARGET_CONTROL", "DCHEY_HIGH_TARGETS"): "2",
    }.items():
        a.equal(topology_index[key]["count"], count, f"topology {key}")

    # Old fields and selected semantic strings remain byte-identical.
    a.equal((len(tokens), len(lines), len(spans)), (479, 51, 3), "overlay sizes")
    for name, new_rows, old_rows, key_fields, selected_field, old_selected in (
        ("token", tokens, old_tokens, ("locus", "token_ordinal"), "v78_token_gloss_de", "v77_token_gloss_de"),
        ("line", lines, old_lines, ("locus",), "v78_line_translation_de", "v77_line_translation_de"),
        ("span", spans, old_spans, ("span_id",), "v78_selected_gloss_de", "v77_selected_gloss_de"),
    ):
        old_table = keyed(old_rows, key_fields)
        a.equal(len(new_rows), len(old_rows), f"{name} length")
        for new in new_rows:
            key = tuple(new[field] for field in key_fields)
            a.require(key in old_table, f"{name} key {key}")
            old = old_table[key]
            for field, value in old.items():
                a.equal(new[field], value, f"{name} old field {key} {field}")
            a.equal(new[selected_field], old[old_selected], f"{name} selected text {key}")
    a.require(all(row["v78_word_delta"] == "0" for row in tokens), "token word deltas")
    a.require(all(row["v78_word_delta"] == "0" for row in lines), "line word deltas")
    a.require(all(row["v78_byte_identical"] == "1" for row in spans), "span byte flags")
    a.equal(sum(row["v78_new_result_edge_ids"] != "NONE" for row in tokens), 4, "four new edge tokens")
    a.equal(sum(row["v78_new_result_edge_ids"] != "NONE" for row in lines), 2, "two new edge lines")

    # No selector-bearing output may touch sealed material.
    for table_name, rows_to_scan in (
        ("census", census), ("leading", leading), ("sheky", sheky), ("dchey", dchey),
        ("edges", edges), ("memberships", memberships), ("positions", positions),
        ("packet", packet), ("tokens", tokens), ("lines", lines),
    ):
        for row in rows_to_scan:
            for field in ("page", "locus", "physical_folio"):
                value = row.get(field, "")
                a.require(not value.lower().startswith("f84"), f"sealed selector {table_name}.{field}={value}")

    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 2, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed", "edge row 3: formal access is not sealed"],
    }
    a.equal([(row["edge_id"], row["formal_access_state"], row["eligibility_status"]) for row in packet],
            [("C017", "FORMAL_ACCESSED", "INELIGIBLE_WORKSHOP_EDGE"),
             ("C018", "FORMAL_ACCESSED", "INELIGIBLE_WORKSHOP_EDGE")], "packet states")
    a.equal(json.loads(paths["intake"].read_text(encoding="utf-8")), expected_intake, "stored intake")
    replay = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(paths["packet"].relative_to(ROOT))],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    a.equal((replay.returncode, replay.stderr), (1, ""), "packet replay process")
    a.equal(json.loads(replay.stdout), expected_intake, "packet exact replay")

    result = json.loads(paths["result"].read_text(encoding="utf-8"))
    a.equal(result["status"], STATUS, "RESULT status")
    expected_basis = {
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
    }
    a.equal(result["basis"], expected_basis, "RESULT basis")
    for field, expected in {
        "new_edge_ids": ["C017", "C018"], "c017": "f80r.17#3→f80r.17#4",
        "c018": "f7r.2#5→f7r.2#6", "held_new_cases": ["A066", "A072", "A046", "A006", "A043"],
        "same_surface_default": False, "same_target_default": False,
        "adjacency_default": False, "new_word_meanings": 0,
    }.items():
        a.equal(result["decision"][field], expected, f"RESULT decision {field}")
    a.equal(result["gdt388"], expected_intake, "RESULT intake")
    a.equal(result["word_preservation"], {
        "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
        "bound_spans_byte_identical": 3, "new_word_meanings": 0,
        "changed_word_meanings": 0, "content_word_additions": 0,
        "content_word_deletions": 0, "content_word_reorders": 0,
    }, "RESULT word preservation")
    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        a.require(path.is_file(), f"RESULT input {relative}")
        a.equal(sha256(path), digest, f"RESULT input hash {relative}")
    for filename, digest in result["files"].items():
        path = ART / filename
        a.require(path.is_file(), f"RESULT artifact {filename}")
        a.equal(sha256(path), digest, f"RESULT artifact hash {filename}")

    docs = [EXP / "README.md", EXP / "METHOD.md", EXP / "REPORT.md"]
    a.require(all(path.is_file() for path in docs), "complete docs")
    for path in docs:
        text = path.read_text(encoding="utf-8")
        a.require("GDT705" in text, f"{path.name} GDT705")
        a.require("C017" in text, f"{path.name} C017")
        a.require("C018" in text, f"{path.name} C018")
        a.require("17" in text and "12" in text, f"{path.name} graph totals")
    report_text = (EXP / "REPORT.md").read_text(encoding="utf-8")
    a.require("bis Mittelstufe erhitzt" in report_text, "REPORT exact C017 result wording")
    a.require("unbound later register" in report_text, "REPORT boundary ceiling")
    a.require("A072" in report_text and "A046" in report_text, "REPORT hidden holds exposed")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    a.equal(manifest["experiment_id"], "GDT705", "manifest ID")
    a.equal(manifest["sealed_data"], {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    manifest_final = manifest.get("status") == STATUS
    if manifest_final:
        a.equal(manifest["question"], result["question"], "manifest question")
        a.equal(manifest["claim_ceiling"], result["claim_ceiling"], "manifest claim")
        a.equal(manifest["validation"]["status"], "PASS", "manifest validation status")
        a.equal(manifest["validation"]["artifact"], str(VALIDATION.relative_to(ROOT)), "manifest validation path")
        outputs = {row["path"] for row in manifest["outputs"]}
        for filename in result["files"]:
            a.require(str((ART / filename).relative_to(ROOT)) in outputs, f"manifest artifact {filename}")
        a.require(str(Path(__file__).resolve().relative_to(ROOT)) in outputs, "manifest validator output")
        a.require(str(VALIDATION.relative_to(ROOT)) in outputs, "manifest validation output")

    return {
        "status": "PASS", "experiment_status": STATUS, "checks": a.checks,
        "immediate_action_nominal_cases": 60,
        "new_edges": ["C017", "C018"],
        "held_new_cases": ["A066", "A072", "A046", "A006", "A043"],
        "graph": {"edges": 17, "components": 12, "nodes": 32, "incidences": 37,
                  "hull_positions": 34, "render_positions": 34, "shared_nodes": 5,
                  "hull_only": 2, "render_only_structural": 0},
        "word_preservation": {"tokens": 479, "lines": 51, "spans": 3},
        "gdt388_errors": expected_intake["errors"],
        "docs_checked": True, "manifest_final_checked": manifest_final,
    }


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        failure = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        VALIDATION.parent.mkdir(parents=True, exist_ok=True)
        VALIDATION.write_text(json.dumps(failure, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1
    VALIDATION.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
