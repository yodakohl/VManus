#!/usr/bin/env python3
"""Independent validator for GDT704; deliberately does not import run.py."""

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
EXP = ROOT / "experiments/yolo/gdt704_v77_repeated_written_material_continuation"
ART, SRC = EXP / "artifacts", EXP / "src"
VALIDATION = ART / "VALIDATION.json"
STATUS = (
    "PASS_V77_15_ACTION_CONTINUATIONS__4_EXACT_HEAD_REPEATS__"
    "1_NEW_C015__C016_HELD__15_EDGES_10_COMPONENTS__ZERO_WORD_DELTA"
)
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G703 = ROOT / "experiments/yolo/gdt703_v76_all_action_finished_result_census/artifacts"


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


def key_rows(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    return {tuple(row[field] for field in fields): row for row in rows}


def validate() -> dict[str, Any]:
    a = Audit()
    paths = {
        "spec": SRC / "V77_15_ACTION_CONTINUATION_SPECS.tsv",
        "result_spec": SRC / "V77_2_OBJECTLESS_POST_RESULT_SPECS.tsv",
        "cont": ART / "V77_15_ACTION_TO_ACTION_CONTINUATIONS.tsv",
        "repeat": ART / "V77_4_EXACT_REPEATED_MATERIAL_HEADS.tsv",
        "controls": ART / "V77_2_OBJECTLESS_POST_RESULT_CONTROLS.tsv",
        "edge": ART / "V77_1_NEW_REPEATED_MATERIAL_EDGE.tsv",
        "membership": ART / "V77_15_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": ART / "V77_10_CONNECTED_COMPONENTS.tsv",
        "positions": ART / "V77_30_COMPONENT_POSITION_ROLES.tsv",
        "topology": ART / "V77_COMPONENT_TOPOLOGY_CENSUS.tsv",
        "packet": ART / "V77_GDT388_EDGE_PACKET.tsv",
        "intake": ART / "V77_GDT388_EDGE_INTAKE.json",
        "tokens": ART / "V77_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": ART / "V77_51_LINE_RELATION_OVERLAY.tsv",
        "spans": ART / "V77_3_BOUND_SPAN_FREEZE.tsv",
        "result": ART / "RESULT.json",
    }
    loaded = {name: read_tsv(path, a)[1] for name, path in paths.items() if path.suffix == ".tsv"}
    specs, result_specs = loaded["spec"], loaded["result_spec"]
    continuations, repeats = loaded["cont"], loaded["repeat"]
    controls, edges = loaded["controls"], loaded["edge"]
    memberships, components = loaded["membership"], loaded["components"]
    positions, topology = loaded["positions"], loaded["topology"]
    packet, tokens, lines, spans = loaded["packet"], loaded["tokens"], loaded["lines"], loaded["spans"]

    _, old_census = read_tsv(G703 / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv", a)
    _, clauses = read_tsv(G695, a)
    _, old_memberships = read_tsv(G703 / "V76_14_EDGE_COMPONENT_MEMBERSHIP.tsv", a)
    _, old_tokens = read_tsv(G703 / "V76_479_TOKEN_RELATION_OVERLAY.tsv", a)
    _, old_lines = read_tsv(G703 / "V76_51_LINE_RELATION_OVERLAY.tsv", a)
    _, old_spans = read_tsv(G703 / "V76_3_BOUND_SPAN_FREEZE.tsv", a)

    # Rebuild the complete GDT703 ACTION -> ACTION subset independently.
    action_subset = [row for row in old_census if row["right_clause_type"] == "ACTION_CLAUSE"]
    a.equal(len(old_census), 83, "GDT703 action population")
    a.equal(len(action_subset), 15, "complete action-to-action subset")
    expected_ids = [row["action_case_id"] for row in action_subset]
    a.equal([row["action_case_id"] for row in continuations], expected_ids, "continuation order/completeness")
    a.equal([row["action_case_id"] for row in specs], expected_ids, "spec order/completeness")
    a.equal(len(set(expected_ids)), 15, "unique continuation IDs")
    clause_index = key_rows(clauses, ("locus", "clause_id"))
    old_token_index = key_rows(old_tokens, ("locus", "token_ordinal"))
    spec_index = {row["action_case_id"]: row for row in specs}
    cont_index = {row["action_case_id"]: row for row in continuations}
    copied_left = {
        "page": "page", "locus": "locus", "left_clause_id": "action_clause_id",
        "left_clause_start": "action_clause_start", "left_clause_end": "action_clause_end",
        "left_clause_surfaces": "action_clause_surfaces", "left_action_ordinal": "action_ordinal",
        "left_action_surface": "action_surface", "left_action_gloss_de": "action_gloss_de",
        "right_clause_id": "right_clause_id",
    }
    spec_fields = [
        "left_material_head_de", "right_material_head_de", "material_head_class",
        "left_patient_or_output_role", "process_relation_class", "decision", "edge_id",
        "support_tier", "working_reading_de", "strongest_rival_de", "portable_default",
    ]
    for old in action_subset:
        case_id = old["action_case_id"]
        new, spec = cont_index[case_id], spec_index[case_id]
        for new_field, old_field in copied_left.items():
            a.equal(new[new_field], old[old_field], f"{case_id} copied {new_field}")
        right = clause_index[(old["locus"], old["right_clause_id"])]
        a.equal(right["clause_type"], "ACTION_CLAUSE", f"{case_id} right clause type")
        a.equal(int(right["start_ordinal"]), int(old["action_clause_end"]) + 1, f"{case_id} immediate full-clause boundary")
        a.equal(new["right_clause_start"], right["start_ordinal"], f"{case_id} right start")
        a.equal(new["right_clause_end"], right["end_ordinal"], f"{case_id} right end")
        a.equal(new["right_clause_surfaces"], right["surfaces"], f"{case_id} right surfaces")
        a.equal(new["right_action_ordinal"], right["action_ordinals"], f"{case_id} right action ordinal")
        action_token = old_token_index[(old["locus"], right["action_ordinals"])]
        a.equal(new["right_action_surface"], action_token["surface"], f"{case_id} right action surface")
        a.equal(new["right_action_gloss_de"], action_token["v76_token_gloss_de"], f"{case_id} right action gloss")
        for field in spec_fields:
            a.equal(new[field], spec[field], f"{case_id} source spec {field}")
        a.equal((new["full_clause_boundary_preserved"], new["word_delta"], new["status"]), ("1", "0", STATUS), f"{case_id} flags")

    a.equal(Counter(row["material_head_class"] for row in specs), Counter({
        "EXACT_EXPLICIT_REPEAT": 4, "DEICTIC_TARGET": 2, "RELATED_EXPLICIT": 3,
        "DIFFERENT_EXPLICIT": 5, "NO_WRITTEN_MATERIAL_HEAD": 1,
    }), "material-head class census")
    a.equal(Counter(row["decision"] for row in specs), Counter({"HOLD_OPEN": 13, "ADMIT_NEW": 1, "REPLAY_EXISTING": 1}), "decision census")
    a.require(all(row["portable_default"] == "NO" for row in specs), "no portable default")
    a.equal([row["action_case_id"] for row in repeats], ["A034", "A062", "A080", "A081"], "exact repeated-head set")
    for row in repeats:
        a.equal(row, cont_index[row["action_case_id"]], f"repeat exact projection {row['action_case_id']}")
    a.equal([row["action_case_id"] for row in repeats if row["decision"] == "ADMIT_NEW"], ["A034"], "only A034 admitted")
    a.require(all("ADDITION" in row["process_relation_class"] for row in repeats if row["action_case_id"] != "A034"), "repeat controls are ingredient additions")

    # C015 exact occurrence and complete source/target boundary.
    a.equal(len(edges), 1, "one new edge")
    c015 = edges[0]
    for field, expected in {
        "edge_id": "C015", "component_id": "M009", "locus": "f26r.2",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_OUTPUT_TO_REPEATED_WRITTEN_MATERIAL_ACTION",
        "source_clause_ordinals": "6|7", "source_edge_node_ordinal": "6",
        "source_action_surface": "ytedy", "structural_closure_ordinal": "7",
        "structural_closure_surface": "dy", "target_action_ordinal": "8",
        "target_action_surface": "checthedy", "repeated_material_head_de": "Krautdroge",
        "right_break_ordinal": "9", "right_break_surface": "ls", "portability": "OCCURRENCE_BOUND_ONLY",
        "gdt388_score_ready": "0", "edge_delta": "1", "word_delta": "0", "status": STATUS,
    }.items():
        a.equal(c015[field], expected, f"C015 {field}")
    for ordinal, surface in (("6", "ytedy"), ("7", "dy"), ("8", "checthedy"), ("9", "ls")):
        a.equal(old_token_index[("f26r.2", ordinal)]["surface"], surface, f"C015 token #{ordinal}")
    source_clause = one(clauses, "C015 source", locus="f26r.2", start_ordinal="6", end_ordinal="7")
    target_clause = one(clauses, "C015 target", locus="f26r.2", start_ordinal="8", end_ordinal="8")
    a.equal((source_clause["surfaces"], source_clause["action_ordinals"]), ("ytedy|dy", "6"), "C015 source clause")
    a.equal((target_clause["surfaces"], target_clause["action_ordinals"]), ("checthedy", "8"), "C015 target clause")

    # C011 replay and explicitly held C016.
    a.equal((len(controls), len(result_specs)), (2, 2), "two controls/specs")
    for spec in result_specs:
        control = one(controls, "control projection", control_id=spec["control_id"])
        for field, value in spec.items():
            a.equal(control[field], value, f"{spec['control_id']} spec {field}")
        a.equal((control["verified"], control["word_delta"]), ("1", "0"), f"{spec['control_id']} flags")
    o001, o002 = one(controls, "O001", control_id="O001"), one(controls, "O002", control_id="O002")
    a.equal((o001["locus"], o001["result_ordinal"], o001["target_clause_start"], o001["target_clause_end"], o001["decision"], o001["edge_id"]),
            ("f26r.2", "5", "6", "7", "REPLAY_C011_NO_REDUNDANT_EDGE", "C011"), "C011 no-redundancy control")
    a.equal((o002["locus"], o002["result_ordinal"], o002["target_clause_start"], o002["target_clause_end"], o002["target_surfaces"], o002["decision"], o002["edge_id"], o002["support_tier"]),
            ("f115r.23", "4", "5", "5", "qokcho", "HOLD_OPEN_C016", "C016", "B_LOW"), "C016 held")
    a.equal((o002["deixis"], o002["repeated_material_head"], o002["right_patient_candidate"]), ("NO", "NO", "#6 Samenposten"), "C016 missing anchors and rival")

    # Existing graph stays intact; recompute its counts and connectivity.
    a.equal((len(old_memberships), len(memberships)), (14, 15), "edge table sizes")
    a.equal({row["edge_id"] for row in memberships}, {f"C{i:03d}" for i in range(1, 16)}, "edge IDs")
    old_by_edge = {row["edge_id"]: row for row in old_memberships}
    new_by_edge = {row["edge_id"]: row for row in memberships}
    immutable = ["edge_id", "component_id", "locus", "support_tier", "relation_class", "edge_node_ordinals", "source_ordinals", "target_ordinal", "target_role", "origin"]
    for edge_id, old in old_by_edge.items():
        for field in immutable:
            a.equal(new_by_edge[edge_id][field], old[field], f"unchanged {edge_id} {field}")
    c015_member = new_by_edge["C015"]
    a.equal((c015_member["component_id"], c015_member["locus"], c015_member["edge_node_ordinals"], c015_member["source_ordinals"], c015_member["target_ordinal"]),
            ("M009", "f26r.2", "6|8", "6", "8"), "C015 membership")
    a.require("C016" not in new_by_edge, "C016 absent")
    a.require(not any(row["locus"] == "f26r.2" and row["edge_node_ordinals"] in {"5|6", "5|8", "4|8", "6|7", "8|9"} for row in memberships), "forbidden redundant edges absent")

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
        all_nodes.update(nodes)
        incidence_count += len(nodes)
        for node in nodes[1:]:
            union(nodes[0], node)
    graph_components: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for node in all_nodes:
        graph_components[find(node)].add(node)
    a.equal((len(all_nodes), incidence_count, len(graph_components)), (28, 33, 10), "recomputed graph 28/33/10")
    a.equal((len(components), sum(int(row["edge_count"]) for row in components)), (10, 15), "component/edge counts")
    a.equal(sum(int(row["edge_hull_position_count"]) for row in components), 30, "hull count")
    a.equal(sum(int(row["render_window_token_count"]) for row in components), 30, "render count")
    expected_partition = {
        frozenset({"C009"}), frozenset({"C001", "C012"}), frozenset({"C002"}), frozenset({"C003"}),
        frozenset({"C004", "C008"}), frozenset({"C005"}), frozenset({"C006", "C007"}),
        frozenset({"C010"}), frozenset({"C011", "C013", "C015"}), frozenset({"C014"}),
    }
    a.equal({frozenset(row["edge_ids"].split("|")) for row in components}, expected_partition, "component partition")
    m009 = one(components, "M009", component_id="M009")
    for field, expected in {
        "locus": "f26r.2", "edge_ids": "C011|C013|C015", "edge_count": "3",
        "edge_node_ordinals": "4|5|6|8", "edge_node_count": "4", "shared_edge_node_ordinals": "4|6",
        "edge_hull_start": "4", "edge_hull_end": "8", "edge_hull_position_count": "5",
        "hull_only_ordinals": "7", "render_window_start": "4", "render_window_end": "8",
        "render_only_structural_ordinals": "NONE", "render_window_token_count": "5",
        "topology": "ACTION_STATE_FORK_WITH_DOWNSTREAM_ACTION_CHAIN", "action_ordinals": "4|6|8",
        "expected_surfaces": "ykecthey|chedy|ytedy|dy|checthedy",
        "observed_surfaces": "ykecthey|chedy|ytedy|dy|checthedy", "v77_edge_delta": "1",
    }.items():
        a.equal(m009[field], expected, f"M009 {field}")

    a.equal(len(positions), 30, "position rows")
    a.equal(len({(row["locus"], row["token_ordinal"]) for row in positions}), 30, "unique positions")
    a.equal(Counter(row["membership_class"] for row in positions), Counter({"EDGE_NODE": 28, "HULL_ONLY": 2}), "position classes")
    a.equal(sum(int(row["is_shared_edge_node"]) for row in positions), 5, "shared nodes")
    a.equal(sum(int(row["is_render_only_structural"]) for row in positions), 0, "render-only structural")
    p7 = one(positions, "f26 #7", locus="f26r.2", token_ordinal="7")
    a.equal((p7["surface"], p7["component_id"], p7["membership_class"], p7["is_edge_node"], p7["is_hull_only"], p7["is_render_only_structural"]),
            ("dy", "M009", "HULL_ONLY", "0", "1", "0"), "structural #7")
    a.require("STRUCTURAL_CLOSURE" in p7["component_role"], "#7 closure role")
    p8 = one(positions, "f26 #8", locus="f26r.2", token_ordinal="8")
    a.equal((p8["surface"], p8["membership_class"], p8["edge_ids"], p8["target_edge_ids"], p8["is_action_target"]),
            ("checthedy", "EDGE_NODE", "C015", "C015", "1"), "C015 target position")
    topology_index = {(row["dimension"], row["value"]): row for row in topology}
    for key, count in {
        ("POSITION_CLASS", "EDGE_NODE"): "28", ("POSITION_CLASS", "HULL_ONLY_NOT_NODE"): "2",
        ("POSITION_CLASS", "RENDER_ONLY_STRUCTURAL"): "0", ("STRUCTURAL_ROLE", "CLAUSE_CLOSURE_NONNODE"): "1",
        ("GRAPH_COUNT", "EDGE_INCIDENCE"): "33", ("GRAPH_COUNT", "MINIMAL_HULL_POSITION"): "30",
        ("GRAPH_COUNT", "RENDER_POSITION"): "30", ("CONTINUATION_CONTROL", "EXACT_REPEATED_MATERIAL_HEAD"): "4",
        ("CONTINUATION_CONTROL", "ADMITTED_NEW_OUTPUT_CONTINUATION"): "1",
    }.items():
        a.equal(topology_index[key]["count"], count, f"topology {key}")

    # Byte-identical frozen words, lines and spans.
    a.equal((len(tokens), len(lines), len(spans)), (479, 51, 3), "freeze sizes")
    for name, new_rows, old_rows, key_fields, selected_field in (
        ("token", tokens, old_tokens, ("locus", "token_ordinal"), "v77_token_gloss_de"),
        ("line", lines, old_lines, ("locus",), "v77_line_translation_de"),
        ("span", spans, old_spans, ("span_id",), "v77_selected_gloss_de"),
    ):
        old_index = key_rows(old_rows, key_fields)
        a.equal(len(new_rows), len(old_rows), f"{name} freeze length")
        for new in new_rows:
            key = tuple(new[field] for field in key_fields)
            a.require(key in old_index, f"{name} frozen key {key}")
            old = old_index[key]
            for field, value in old.items():
                a.equal(new[field], value, f"{name} old field {key} {field}")
            expected = old["v76_token_gloss_de"] if name == "token" else old["v76_line_translation_de"] if name == "line" else old["v76_selected_gloss_de"]
            a.equal(new[selected_field], expected, f"{name} selected freeze {key}")
    a.require(all(row["v77_word_delta"] == "0" for row in tokens), "token word deltas")
    a.require(all(row["v77_word_delta"] == "0" for row in lines), "line word deltas")
    a.require(all(row["v77_byte_identical"] == "1" for row in spans), "span byte flags")

    # Selector-bearing outputs must not touch sealed material.
    for table_name, rows_to_scan in (("continuations", continuations), ("controls", controls), ("edges", edges), ("memberships", memberships), ("positions", positions), ("tokens", tokens), ("lines", lines)):
        for row in rows_to_scan:
            for field in ("page", "locus", "physical_folio"):
                value = row.get(field, "")
                a.require(not value.lower().startswith("f84"), f"sealed selector {table_name}.{field}={value}")

    # Exact executable GDT388 one-error intake.
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0, "eligible_folios": 0,
        "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    a.equal(len(packet), 1, "GDT388 packet row")
    a.equal((packet[0]["edge_id"], packet[0]["formal_access_state"], packet[0]["eligibility_status"]),
            ("C015", "FORMAL_ACCESSED", "INELIGIBLE_WORKSHOP_EDGE"), "GDT388 packet state")
    a.equal(json.loads(paths["intake"].read_text(encoding="utf-8")), expected_intake, "stored GDT388 intake")
    replay = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(paths["packet"].relative_to(ROOT))], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    a.equal(replay.returncode, 1, "GDT388 return")
    a.equal(replay.stderr, "", "GDT388 stderr")
    a.equal(json.loads(replay.stdout), expected_intake, "GDT388 exact replay")

    # RESULT values and all recorded digests.
    result = json.loads(paths["result"].read_text(encoding="utf-8"))
    a.equal(result["status"], STATUS, "RESULT status")
    expected_basis = {
        "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51, "source_clauses": 175,
        "action_clauses": 83, "bound_spans": 3, "direct_action_continuations": 15,
        "exact_repeated_material_heads": 4, "deictic_targets": 2, "related_material_heads": 3,
        "different_material_heads": 5, "no_written_material_head": 1, "admitted_new_continuations": 1,
        "replayed_existing_continuations": 1, "open_continuations": 13, "objectless_post_result_controls": 2,
        "relation_edges_before": 14, "relation_edges_after": 15, "new_edges": 1,
        "connected_components": 10, "edge_nodes": 28, "edge_node_incidences": 33,
        "minimal_hull_positions": 30, "render_positions": 30, "shared_edge_nodes": 5,
        "hull_only_positions": 2, "render_only_structural_positions": 0,
        "structural_closure_positions": 1, "f84_access": 0, "f84r_access": 0,
    }
    a.equal(result["basis"], expected_basis, "RESULT basis")
    for field, expected in {
        "new_edge": "C015", "c015": "f26r.2#6→f26r.2#8", "source_clause": "f26r.2#6-7",
        "target_action": "f26r.2#8", "c016": "HOLD_OPEN_B_LOW", "redundant_5_to_6_edge": False,
        "portable_material_repeat_default": False, "new_word_meanings": 0,
    }.items():
        a.equal(result["decision"][field], expected, f"RESULT decision {field}")
    a.equal(result["gdt388"], expected_intake, "RESULT GDT388")
    a.equal(result["freeze"], {
        "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
        "bound_spans_byte_identical": 3, "new_word_meanings": 0, "changed_word_meanings": 0,
        "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0,
    }, "RESULT freeze")
    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        a.require(path.is_file(), f"RESULT input {relative}")
        a.equal(sha256(path), digest, f"RESULT input hash {relative}")
    for filename, digest in result["files"].items():
        path = ART / filename
        a.require(path.is_file(), f"RESULT artifact {filename}")
        a.equal(sha256(path), digest, f"RESULT artifact hash {filename}")

    # Final documentation and manifest checks.  A manifest scaffold is allowed
    # only during the first validator pass, before VALIDATION.json can be hashed.
    docs = [EXP / "README.md", EXP / "METHOD.md", EXP / "REPORT.md"]
    docs_ready = any(path.exists() for path in docs)
    if docs_ready:
        a.require(all(path.is_file() for path in docs), "complete docs")
        for path in docs:
            text = path.read_text(encoding="utf-8")
            a.require("GDT704" in text, f"{path.name} GDT704")
            a.require("C015" in text, f"{path.name} C015")
            a.require("C016" in text, f"{path.name} C016")
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    a.equal(manifest["experiment_id"], "GDT704", "manifest ID")
    a.equal(manifest["sealed_data"], {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    manifest_final = manifest.get("status") == STATUS
    if manifest_final:
        a.equal(manifest["question"], result["question"], "manifest question")
        a.equal(manifest["claim_ceiling"], result["claim_ceiling"], "manifest claim")
        a.equal(manifest["validation"]["status"], "PASS", "manifest validation status")
        a.equal(manifest["validation"]["artifact"], str(VALIDATION.relative_to(ROOT)), "manifest validation path")
        outputs = {row["path"] for row in manifest["outputs"]}
        for filename in result["files"]:
            a.require(str((ART / filename).relative_to(ROOT)) in outputs, f"manifest output {filename}")

    return {
        "status": "PASS", "experiment_status": STATUS, "checks": a.checks,
        "action_continuations": 15, "exact_repeated_material_heads": ["A034", "A062", "A080", "A081"],
        "new_edge": "C015", "held_candidate": "C016",
        "graph": {"edges": 15, "components": 10, "nodes": 28, "incidences": 33,
                  "hull_positions": 30, "render_positions": 30, "shared_nodes": 5,
                  "hull_only": 2, "render_only_structural": 0},
        "freeze": {"tokens": 479, "lines": 51, "spans": 3},
        "gdt388_errors": expected_intake["errors"], "docs_checked": docs_ready,
        "manifest_final_checked": manifest_final,
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
