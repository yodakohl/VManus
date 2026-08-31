#!/usr/bin/env python3
"""Independent publication validator for GDT703; never imports the builder."""

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


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
PREFIX = "experiments/yolo/gdt703_v76_all_action_finished_result_census/"
EXP, ART = ROOT / PREFIX, ROOT / PREFIX / "artifacts"
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

CLAUSES = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
DISPATCH = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv"
OLD_MEMBERSHIP = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast/artifacts/V75_12_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_TOKENS = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast/artifacts/V75_479_TOKEN_RELATION_OVERLAY.tsv"
OLD_LINES = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast/artifacts/V75_51_LINE_RELATION_OVERLAY.tsv"
OLD_SPANS = ROOT / "experiments/yolo/gdt702_v75_exact_written_result_contrast/artifacts/V75_3_BOUND_SPAN_FREEZE.tsv"
SPEC = EXP / "src/V76_7_FINISHED_RESULT_CASE_SPECS.tsv"
CENSUS = ART / "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv"
CANDIDATES = ART / "V76_7_FINISHED_RESULT_FIRSTS.tsv"
EDGES = ART / "V76_2_NEW_LOCAL_RESULT_EDGES.tsv"
MEMBERSHIP = ART / "V76_14_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS = ART / "V76_10_CONNECTED_COMPONENTS.tsv"
POSITIONS = ART / "V76_29_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY = ART / "V76_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET = ART / "V76_GDT388_EDGE_PACKET.tsv"
INTAKE = ART / "V76_GDT388_EDGE_INTAKE.json"
TOKENS = ART / "V76_479_TOKEN_RELATION_OVERLAY.tsv"
LINES = ART / "V76_51_LINE_RELATION_OVERLAY.tsv"
SPANS = ART / "V76_3_BOUND_SPAN_FREEZE.tsv"
RESULT = ART / "RESULT.json"
READER = ART / "GDT703_V76_ALL_ACTION_RESULT_READER.md"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    assert fields and len(fields) == len(set(fields)), path
    assert all(None not in row and set(row) == set(fields) for row in rows), path
    return fields, rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    assert len(hits) == 1, (wanted, len(hits))
    return hits[0]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, condition: bool, name: str) -> None:
        self.rows.append({"check": name, "pass": bool(condition)})
        if not condition:
            raise AssertionError(name)


def main() -> int:
    audit = Audit()
    _, clauses = read_tsv(CLAUSES)
    _, dispatch = read_tsv(DISPATCH)
    _, old_tokens = read_tsv(OLD_TOKENS)
    _, old_lines = read_tsv(OLD_LINES)
    _, old_spans = read_tsv(OLD_SPANS)
    _, specs = read_tsv(SPEC)
    _, census = read_tsv(CENSUS)
    _, candidates = read_tsv(CANDIDATES)
    _, edges = read_tsv(EDGES)
    _, membership = read_tsv(MEMBERSHIP)
    _, old_membership = read_tsv(OLD_MEMBERSHIP)
    _, components = read_tsv(COMPONENTS)
    _, positions = read_tsv(POSITIONS)
    _, topology = read_tsv(TOPOLOGY)
    _, packet = read_tsv(PACKET)
    token_fields, tokens = read_tsv(TOKENS)
    line_fields, lines = read_tsv(LINES)
    span_fields, spans = read_tsv(SPANS)

    audit.check(len(clauses) == 175, "175 source clauses")
    audit.check(Counter(row["clause_type"] for row in clauses) == {"NOMINAL_BLOCK": 92, "ACTION_CLAUSE": 83}, "83 action and 92 nominal clauses")
    audit.check(len({row["locus"] for row in clauses}) == 51 and len({row["page"] for row in clauses}) == 36, "51 loci and 36 pages")
    audit.check(all(not row["page"].startswith("f84") for row in clauses), "source clauses exclude f84 and f84r")

    clauses_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_locus[row["locus"]].append(row)
    for locus, local in clauses_by_locus.items():
        local.sort(key=lambda row: int(row["clause_id"]))
        audit.check([int(row["clause_id"]) for row in local] == list(range(1, len(local) + 1)), f"contiguous clause ids {locus}")
        audit.check(all(int(b["start_ordinal"]) == int(a["end_ordinal"]) + 1 for a, b in zip(local, local[1:])), f"contiguous clause ordinals {locus}")

    audit.check(len(census) == 83 and [row["action_case_id"] for row in census] == [f"A{i:03d}" for i in range(1, 84)], "complete ordered 83-action census")
    audit.check(Counter(row["right_clause_type"] for row in census) == {"NOMINAL_BLOCK": 60, "ACTION_CLAUSE": 15, "END_OF_LINE": 8}, "exact 60/15/8 successor split")
    audit.check(all(row["intervening_semantic_items"] == "0" and row["full_clause_then_first_item_exact"] == "1" for row in census), "no semantic item skipped")
    source_actions = [row for row in clauses if row["clause_type"] == "ACTION_CLAUSE"]
    for source, published in zip(source_actions, census):
        local = clauses_by_locus[source["locus"]]
        index = local.index(source)
        right = local[index + 1] if index + 1 < len(local) else None
        audit.check((published["locus"], published["action_clause_id"], published["action_clause_start"], published["action_clause_end"]) == (source["locus"], source["clause_id"], source["start_ordinal"], source["end_ordinal"]), f"action source exact {published['action_case_id']}")
        if right is None:
            audit.check(published["right_clause_type"] == "END_OF_LINE" and published["right_first_ordinal"] == "NONE", f"EOS exact {published['action_case_id']}")
        else:
            audit.check((published["right_clause_id"], published["right_clause_type"], published["right_first_ordinal"]) == (right["clause_id"], right["clause_type"], right["start_ordinal"]), f"immediate successor exact {published['action_case_id']}")

    exact_candidates = {
        ("f105r.2", "11", "12"), ("f105v.1", "4", "5"),
        ("f105v.14", "3", "4"), ("f115r.1", "3", "4"),
        ("f115r.23", "3", "4"), ("f26r.2", "4", "5"),
        ("f77v.7", "5", "6"),
    }
    found_candidates = {
        (row["locus"], row["action_ordinal"], row["right_first_ordinal"])
        for row in census if row["candidate_id"] != "NONE"
    }
    audit.check(found_candidates == exact_candidates, "exact seven immediate finished-state coordinates")
    audit.check(len(candidates) == 7 and Counter(row["decision"] for row in candidates) == {"HOLD_OPEN": 4, "ADMIT_NEW": 2, "ADMIT_INHERITED": 1}, "seven decisions partition 4/2/1")
    audit.check({row["edge_id"] for row in candidates if row["decision"] != "HOLD_OPEN"} == {"C012", "C013", "C014"}, "only C012 C013 C014 admitted")
    dispatch_index = {(row["locus"], row["ordinal"]): row for row in dispatch}
    for row in candidates:
        drow = dispatch_index[(row["locus"], row["result_ordinal"])]
        audit.check((drow["dispatch_class"], drow["confidence"], drow["action_licensed_before"], drow["dy_contribution"]) == ("NOMINAL_FINISHED_RESULT_STATE", "HIGH", "0", "FINISHED_ENDPOINT_NOT_NEW_VERB"), f"independent result dispatch {row['candidate_id']}")
        audit.check(row["right_context_is_immediate"] == "1" and row["word_delta"] == "0", f"candidate immediate and zero-delta {row['candidate_id']}")

    audit.check([row["edge_id"] for row in edges] == ["C013", "C014"], "exact two new edges")
    audit.check({(row["edge_id"], row["locus"], row["edge_node_ordinals"]) for row in edges} == {("C013", "f26r.2", "4|5"), ("C014", "f115r.23", "3|4")}, "new edge coordinates exact")
    audit.check(all(row["portability"] == "OCCURRENCE_BOUND_ONLY" and row["gdt388_score_ready"] == "0" and row["word_delta"] == "0" for row in edges), "new edges local not score-ready zero-word")
    audit.check(one(edges, edge_id="C013")["support_tier"] == "B_WORKING_LOCAL" and one(edges, edge_id="C014")["support_tier"] == "B_LOW_WORKING_LOCAL", "edge tiers explicit")

    audit.check([row["edge_id"] for row in membership] == [f"C{i:03d}" for i in range(1, 15)], "membership covers C001-C014")
    old_by_id = {row["edge_id"]: row for row in old_membership}
    new_by_id = {row["edge_id"]: row for row in membership}
    invariant_fields = ["edge_id", "component_id", "locus", "support_tier", "relation_class", "edge_node_ordinals", "source_ordinals", "target_ordinal", "target_role", "origin"]
    for edge_id in [f"C{i:03d}" for i in range(1, 13)]:
        audit.check(all(new_by_id[edge_id][field] == old_by_id[edge_id][field] for field in invariant_fields), f"inherited edge endpoints exact {edge_id}")
    audit.check(new_by_id["C011"]["edge_node_ordinals"] == "4|6" and new_by_id["C013"]["edge_node_ordinals"] == "4|5", "M009 is common-source fork")
    audit.check(not any(row["locus"] == "f26r.2" and row["source_ordinals"] == "5" and row["target_ordinal"] == "6" for row in membership), "no invented f26r.2 #5 to #6 edge")
    audit.check(not any(row["locus"] == "f115r.23" and row["target_ordinal"] == "5" for row in membership), "M010 stops before qokcho #5")

    graph_nodes = {(row["locus"], ordinal) for row in membership for ordinal in row["edge_node_ordinals"].split("|")}
    audit.check(len(membership) == 14 and len(graph_nodes) == 27, "14 edges and 27 unique nodes")
    audit.check(sum(len(row["edge_node_ordinals"].split("|")) for row in membership) == 31, "31 edge incidences")
    component_sets = {row["component_id"]: set(row["edge_ids"].split("|")) for row in components}
    audit.check(component_sets == {
        "M001": {"C009"}, "M002": {"C001", "C012"}, "M003": {"C002"},
        "M004": {"C003"}, "M005": {"C005"}, "M006": {"C004", "C008"},
        "M007": {"C006", "C007"}, "M008": {"C010"}, "M009": {"C011", "C013"},
        "M010": {"C014"},
    }, "exact ten-component partition")
    audit.check(sum(int(row["edge_hull_position_count"]) for row in components) == 28, "28 minimal hull positions")
    audit.check(sum(int(row["render_window_token_count"]) for row in components) == 29, "29 render positions")
    m009, m010 = one(components, component_id="M009"), one(components, component_id="M010")
    audit.check((m009["edge_node_ordinals"], m009["shared_edge_node_ordinals"], m009["hull_only_ordinals"], m009["render_only_structural_ordinals"]) == ("4|5|6", "4", "NONE", "7"), "M009 exact node hull structural contract")
    audit.check((m010["locus"], m010["edge_node_ordinals"], m010["render_window_start"], m010["render_window_end"]) == ("f115r.23", "3|4", "3", "4"), "M010 exact closed pair")
    audit.check("#5→#6" in m009["forbidden_inference"] and "#5 QOKCHO" in m010["boundary_note_de"], "component collision controls explicit")

    audit.check(len(positions) == 29 and len({(row["locus"], row["token_ordinal"]) for row in positions}) == 29, "29 unique position rows")
    audit.check(Counter(row["membership_class"] for row in positions) == {"EDGE_NODE": 27, "HULL_ONLY": 1, "RENDER_ONLY_STRUCTURAL": 1}, "position classes 27/1/1")
    shared = {(row["locus"], row["token_ordinal"]) for row in positions if row["is_shared_edge_node"] == "1"}
    audit.check(shared == {("f105v.1", "4"), ("f26r.2", "4"), ("f80v.35", "3"), ("f86v6.25", "4")}, "four shared nodes exact")
    audit.check({(row["locus"], row["token_ordinal"]) for row in positions if row["membership_class"] == "HULL_ONLY"} == {("f86v5.24", "2")}, "sole hull-only position exact")
    audit.check({(row["locus"], row["token_ordinal"]) for row in positions if row["membership_class"] == "RENDER_ONLY_STRUCTURAL"} == {("f26r.2", "7")}, "sole structural position exact")
    audit.check(one(positions, locus="f26r.2", token_ordinal="5")["v76_change"] == "HULL_ONLY_TO_C013_EDGE_NODE", "f26r.2#5 promoted exactly once")

    audit.check(len(tokens) == len(old_tokens) == 479 and len(token_fields) == len(set(token_fields)), "479 token overlay rows")
    for old, new in zip(old_tokens, tokens):
        audit.check((old["page"], old["locus"], old["token_ordinal"], old["surface"], old["v75_token_gloss_de"]) == (new["page"], new["locus"], new["token_ordinal"], new["surface"], new["v76_token_gloss_de"]), f"token freeze {new['locus']}#{new['token_ordinal']}")
        audit.check(new["v76_word_delta"] == "0" and not new["page"].startswith("f84"), f"token zero delta and unsealed {new['locus']}#{new['token_ordinal']}")
    audit.check(sum(row["v76_new_result_edge_ids"] != "NONE" for row in tokens) == 4, "four token rows carry C013 or C014")
    audit.check(len(lines) == len(old_lines) == 51 and len(line_fields) == len(set(line_fields)), "51 line overlay rows")
    for old, new in zip(old_lines, lines):
        audit.check((old["page"], old["locus"], old["v75_line_translation_de"]) == (new["page"], new["locus"], new["v76_line_translation_de"]), f"line freeze {new['locus']}")
    audit.check(sum(row["v76_new_result_edge_ids"] != "NONE" for row in lines) == 2, "two lines carry new edges")
    audit.check(len(spans) == len(old_spans) == 3 and len(span_fields) == len(set(span_fields)), "three span rows")
    for old, new in zip(old_spans, spans):
        audit.check(old["v75_selected_gloss_de"] == new["v76_selected_gloss_de"] and new["v76_byte_identical"] == "1" and new["v76_relation_change"] == "NONE", f"span freeze {new.get('span_id', new.get('locus', 'row'))}")

    audit.check(len(packet) == 2 and [(row["edge_id"], row["pivot_locus"], row["target_locus"]) for row in packet] == [("C013", "f26r.2@4", "f26r.2@5"), ("C014", "f115r.23@3", "f115r.23@4")], "two exact GDT388 packet rows")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET.relative_to(ROOT))], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    expected_intake = {
        "capacity_gate_50_edges_5_folios": False, "discovery_edges": 0,
        "eligible_edges": 0, "eligible_folios": 0,
        "errors": ["edge row 2: formal access is not sealed", "edge row 3: formal access is not sealed"],
        "holdout_edges": 0, "holdout_gate": False, "mobile_edges": 0,
        "mobile_null_gate": False, "packet_rows": 2, "score_ready": False,
        "status": "INVALID_PACKET",
    }
    audit.check(completed.returncode == 1 and not completed.stderr and json.loads(completed.stdout) == expected_intake, "official GDT388 intake exact")
    audit.check(json.loads(INTAKE.read_text(encoding="utf-8")) == expected_intake, "published intake JSON exact")

    audit.check(any(row["dimension"] == "WRITTEN_RESULT_STATUS" and row["value"] == "INTERMEDIATE_STATE_CHECKPOINT" and row["count"] == "1" for row in topology), "topology distinguishes C013 intermediate state")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit.check((result["status"], result["question"], result["claim_ceiling"]) == (STATUS, QUESTION, CLAIM), "RESULT identity and claim exact")
    expected_basis = {
        "action_clauses": 83, "action_right_contexts": 83, "bound_spans": 3,
        "connected_components": 10, "edge_node_incidences": 31, "edge_nodes": 27,
        "end_of_line_right_contexts": 8, "f84_access": 0, "f84r_access": 0,
        "finished_result_firsts": 7, "following_action_contexts": 15,
        "hull_only_positions": 1, "inherited_local_reads": 1, "lines": 51,
        "minimal_hull_positions": 28, "new_edges": 2, "new_local_reads": 2,
        "new_pages": 0, "nominal_clauses": 92, "nominal_right_contexts": 60,
        "open_nonedge_reads": 4, "pages": 36, "relation_edges_after": 14,
        "relation_edges_before": 12, "render_only_structural_positions": 1,
        "render_positions": 29, "shared_edge_nodes": 4, "source_clauses": 175,
        "token_positions": 479,
    }
    audit.check(result["basis"] == expected_basis, "RESULT complete numeric basis exact")
    audit.check(result["decision"]["new_edge_ids"] == ["C013", "C014"] and result["decision"]["retained_edge"] == "C012", "RESULT decisions exact")
    audit.check(result["decision"]["changed_existing_edges"] == 0 and result["decision"]["new_word_meanings"] == 0, "zero changed edges and meanings")
    audit.check(all(result["decision"][key] is False for key in ("later_token_skip", "adjacency_default", "action_surface_output_default", "result_surface_left_action_default")), "unsafe defaults remain false")
    audit.check(result["gdt388"] == expected_intake, "RESULT binds GDT388 intake")
    audit.check(result["freeze"] == {"bound_spans_byte_identical": 3, "changed_word_meanings": 0, "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0, "line_translations_byte_identical": 51, "new_word_meanings": 0, "token_glosses_byte_identical": 479}, "RESULT freeze exact")

    generated = {path.name: path for path in (CENSUS, CANDIDATES, EDGES, MEMBERSHIP, COMPONENTS, POSITIONS, TOPOLOGY, PACKET, INTAKE, TOKENS, LINES, SPANS, READER, ART / "README.md")}
    audit.check(result["files"] == {name: sha256(path) for name, path in generated.items()}, "RESULT builder artifact hashes exact")
    audit.check(all(sha256(ROOT / relative) == digest for relative, digest in result["inputs"].items()), "all RESULT input hashes exact")

    reader = READER.read_text(encoding="utf-8")
    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    method = (EXP / "METHOD.md").read_text(encoding="utf-8")
    readme = (EXP / "README.md").read_text(encoding="utf-8")
    audit.check(STATUS in reader and "83 Aktionsklauseln" in reader and "C013 / f26r.2" in reader and "C014 / f115r.23" in reader, "reader exposes concrete results and complete census")
    audit.check(STATUS in report and "60 nominal" in report and "27 unique edge nodes" in report, "REPORT exposes census and graph")
    audit.check(STATUS in readme and all(term in method for term in ("C013", "C014", "GDT388", "HOLD_OPEN")), "entry docs expose method and ceiling")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    audit.check((manifest["experiment_id"], manifest["slug"], manifest["status"], manifest["question"], manifest["claim_ceiling"]) == ("GDT703", "v76_all_action_finished_result_census", STATUS, QUESTION, CLAIM), "manifest identity exact")
    audit.check(manifest["dependencies"] == ["GDT388", "GDT687", "GDT695", "GDT700", "GDT702"] and manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest dependencies and seals exact")
    audit.check(manifest["validation"] == {"artifact": PREFIX + "artifacts/VALIDATION.json", "status": "PASS"}, "manifest validation contract exact")
    external_inputs = {relative: digest for relative, digest in result["inputs"].items() if not relative.startswith(PREFIX)}
    manifest_inputs = {entry["path"]: entry for entry in manifest["inputs"]}
    audit.check(set(manifest_inputs) == set(external_inputs), "manifest exact external input set")
    audit.check(all(entry["sha256"] == external_inputs[path] and bool(entry["role"]) for path, entry in manifest_inputs.items()), "manifest input hashes and roles exact")
    expected_outputs = {
        PREFIX + name for name in ("README.md", "METHOD.md", "REPORT.md", "src/V76_7_FINISHED_RESULT_CASE_SPECS.tsv", "src/run.py", "src/validate.py")
    } | {
        PREFIX + "artifacts/" + name for name in (
            "GDT703_V76_ALL_ACTION_RESULT_READER.md", "README.md", "RESULT.json", "VALIDATION.json",
            "V76_83_ACTION_RIGHT_CONTEXT_CENSUS.tsv", "V76_7_FINISHED_RESULT_FIRSTS.tsv",
            "V76_2_NEW_LOCAL_RESULT_EDGES.tsv", "V76_14_EDGE_COMPONENT_MEMBERSHIP.tsv",
            "V76_10_CONNECTED_COMPONENTS.tsv", "V76_29_COMPONENT_POSITION_ROLES.tsv",
            "V76_COMPONENT_TOPOLOGY_CENSUS.tsv", "V76_GDT388_EDGE_PACKET.tsv",
            "V76_GDT388_EDGE_INTAKE.json", "V76_479_TOKEN_RELATION_OVERLAY.tsv",
            "V76_51_LINE_RELATION_OVERLAY.tsv", "V76_3_BOUND_SPAN_FREEZE.tsv",
        )
    }
    manifest_outputs = {entry["path"]: entry for entry in manifest["outputs"]}
    audit.check(set(manifest_outputs) == expected_outputs and len(expected_outputs) == 22, "manifest exact 22-file output tree")
    for relative, entry in sorted(manifest_outputs.items()):
        audit.check(bool(entry["role"]) and bool(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])), f"manifest output syntax {Path(relative).name}")
        if not relative.endswith("/VALIDATION.json"):
            audit.check(sha256(ROOT / relative) == entry["sha256"], f"manifest output digest {relative}")

    payload = {
        "status": "PASS", "checks": len(audit.rows), "failed": 0,
        "summary": {
            "action_clauses": 83, "successor_split": "60/15/8", "finished_state_firsts": 7,
            "retained_edges": ["C012"], "new_edges": ["C013", "C014"],
            "open_cases": 4, "relation_edges": 14, "connected_components": 10,
            "edge_nodes": 27, "edge_node_incidences": 31, "minimal_hull_positions": 28,
            "render_positions": 29, "shared_edge_nodes": 4, "hull_only_positions": 1,
            "render_only_structural_positions": 1, "tokens_frozen": 479,
            "lines_frozen": 51, "spans_frozen": 3, "new_word_meanings": 0,
        },
        "audit": audit.rows,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
