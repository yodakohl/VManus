#!/usr/bin/env python3
"""Independent validator for GDT707; deliberately does not import run.py."""

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
EXP = ROOT / "experiments/yolo/gdt707_v80_three_item_material_state_result_bundle"
SRC, ART = EXP / "src", EXP / "artifacts"
VALIDATION = ART / "VALIDATION.json"
STATUS = (
    "PASS_V80_119_TRIPLES__32_ACTION_ADJACENT_BUNDLES__1_NEW_C020_4_HOLDS_"
    "27_STOPS__9_DCHEY_CONTEXTS__19_EDGES_13_COMPONENTS__ZERO_WORD_DELTA"
)
C020_READING = (
    "Eine abgemessene Portion bis zur Mittelstufe trocknen. Als möglicher Ergebnisblock folgt: "
    "Drogenstoff aus Arzneikompositum – trocken; trocken in der Mitte des Grades."
)
G706 = ROOT / "experiments/yolo/gdt706_v79_second_nominal_item_result_census/artifacts"


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
        "spec": SRC / "V80_32_LEADING_BUNDLE_SPECS.tsv",
        "triples": ART / "V80_119_SEMANTIC_TRIPLE_UNIVERSE.tsv",
        "bundles": ART / "V80_32_ACTION_ADJACENT_BUNDLE_CENSUS.tsv",
        "short": ART / "V80_10_TWO_ITEM_LENGTH_CONTROLS.tsv",
        "dchey": ART / "V80_9_DCHEY_ACTION_CONTEXTS.tsv",
        "surface": ART / "V80_10_BUNDLE_SURFACE_OCCURRENCES.tsv",
        "edge": ART / "V80_1_NEW_MATERIAL_QUALITY_DEGREE_RESULT_EDGE.tsv",
        "memberships": ART / "V80_19_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": ART / "V80_13_CONNECTED_COMPONENTS.tsv",
        "positions": ART / "V80_40_COMPONENT_POSITION_ROLES.tsv",
        "topology": ART / "V80_COMPONENT_TOPOLOGY_CENSUS.tsv",
        "packet": ART / "V80_GDT388_EDGE_PACKET.tsv",
        "tokens": ART / "V80_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": ART / "V80_51_LINE_RELATION_OVERLAY.tsv",
        "spans": ART / "V80_3_BOUND_SPAN_FREEZE.tsv",
    }
    fields: dict[str, list[str]] = {}
    loaded: dict[str, list[dict[str, str]]] = {}
    for name, path in paths.items():
        fields[name], loaded[name] = read_tsv(path, a)

    old_paths = {
        "actions": G706 / "V79_83_ACTION_DISPOSITIONS.tsv",
        "pairs": G706 / "V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv",
        "memberships": G706 / "V79_18_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": G706 / "V79_12_CONNECTED_COMPONENTS.tsv",
        "positions": G706 / "V79_36_COMPONENT_POSITION_ROLES.tsv",
        "tokens": G706 / "V79_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": G706 / "V79_51_LINE_RELATION_OVERLAY.tsv",
        "spans": G706 / "V79_3_BOUND_SPAN_FREEZE.tsv",
    }
    old_fields: dict[str, list[str]] = {}
    old: dict[str, list[dict[str, str]]] = {}
    for name, path in old_paths.items():
        old_fields[name], old[name] = read_tsv(path, a)

    specs, triples, bundles = loaded["spec"], loaded["triples"], loaded["bundles"]
    shorts, dchey, surfaces, edge = loaded["short"], loaded["dchey"], loaded["surface"], loaded["edge"]
    memberships, components = loaded["memberships"], loaded["components"]
    positions, topology = loaded["positions"], loaded["topology"]
    tokens, lines, spans = loaded["tokens"], loaded["lines"], loaded["spans"]

    a.equal((len(specs), len(triples), len(bundles), len(shorts), len(dchey), len(surfaces)),
            (32, 119, 32, 10, 9, 10), "census populations")
    a.equal((len(edge), len(memberships), len(components), len(positions)), (1, 19, 13, 40), "graph populations")
    a.equal((len(tokens), len(lines), len(spans)), (479, 51, 3), "overlay populations")
    a.equal([row["bundle_case_id"] for row in specs], [f"B{i:03d}" for i in range(1, 33)], "spec IDs")
    a.equal([row["triple_id"] for row in triples], [f"T{i:03d}" for i in range(1, 120)], "triple IDs")
    a.equal(Counter(row["decision"] for row in specs), Counter({"ADMIT_RESULT_BUNDLE": 1, "HOLD": 4, "STOP": 27}), "spec decisions")
    a.equal(Counter(row["bundle_decision"] for row in bundles), Counter({"ADMIT_RESULT_BUNDLE": 1, "HOLD": 4, "STOP": 27}), "bundle decisions")
    a.equal(Counter(row["action_adjacent"] for row in triples), Counter({"1": 32, "0": 87}), "triple roles")
    a.require(all(row["portable_default"] == "NO" for row in specs + bundles + surfaces), "no portable bundle/surface default")
    a.require(all(row["portable_dchey_default"] == "NO" for row in dchey), "no dchey default")
    a.require(all(row["status"] == STATUS for rows in loaded.values() for row in rows if "status" in row), "single output status")
    a.require(all(not row["page"].startswith("f84") for row in tokens), "no f84 token")

    action_index = keyed(old["actions"], ("action_case_id",))
    old_token_index = keyed(old["tokens"], ("locus", "token_ordinal"))
    semantic_windows: dict[str, list[dict[str, str]]] = {}
    for action in old["actions"]:
        if action["right_clause_type"] != "NOMINAL_BLOCK":
            continue
        items = []
        for ordinal in range(int(action["right_clause_start"]), int(action["right_clause_end"]) + 1):
            item = old_token_index[(action["locus"], str(ordinal))]
            if item["v79_token_gloss_de"] != ".":
                items.append(item)
        a.equal(len(items), int(action["nominal_semantic_item_count"]), f"semantic count {action['action_case_id']}")
        semantic_windows[action["action_case_id"]] = items

    reconstructed: list[tuple[str, str, str, str, str, str, str]] = []
    for action in old["actions"]:
        items = semantic_windows.get(action["action_case_id"], [])
        if action["disposition"] != "DELAYED_NOMINAL_WINDOW" or len(items) < 3:
            continue
        for start in range(len(items) - 2):
            tri = items[start:start + 3]
            reconstructed.append((
                action["action_case_id"], str(start + 1),
                "|".join(item["token_ordinal"] for item in tri),
                "|".join(item["surface"] for item in tri),
                "|".join(item["v79_token_gloss_de"] for item in tri),
                str(int(start == 0)),
                "LEADING_ACTION_RESULT_BUNDLE" if start == 0 else "LATER_STARTING_TRIPLE_CONTROL",
            ))
    observed = [
        (row["action_case_id"], row["semantic_start_rank"], row["item_ordinals"], row["item_surfaces"],
         row["item_glosses_de"], row["action_adjacent"], row["search_role"])
        for row in triples
    ]
    a.equal(observed, reconstructed, "complete triple reconstruction")
    a.equal(sum(
        max(0, len(semantic_windows.get(action["action_case_id"], [])) - 2)
        for action in old["actions"] if action["disposition"] == "DELAYED_NOMINAL_WINDOW"
    ), 119, "triple formula")

    spec_index = keyed(specs, ("action_case_id",))
    triple_index = keyed([row for row in triples if row["action_adjacent"] == "1"], ("action_case_id",))
    bundle_index = keyed(bundles, ("action_case_id",))
    a.equal(set(spec_index), set(triple_index), "specs exhaust leading triples")
    a.equal(set(bundle_index), set(triple_index), "bundle rows exhaust leading triples")
    for key, bundle in bundle_index.items():
        spec, triple, action = spec_index[key], triple_index[key], action_index[key]
        for field in ("page", "locus", "action_ordinal", "action_surface", "action_gloss_de",
                      "right_clause_id", "item_ordinals", "item_surfaces", "item_glosses_de"):
            a.equal(bundle[field], triple[field], f"{key[0]} triple join {field}")
        a.equal(bundle["item_surfaces"], spec["expected_item_surfaces"], f"{key[0]} spec surfaces")
        a.equal(bundle["bundle_decision"], spec["decision"], f"{key[0]} spec decision")
        a.equal(bundle["practical_reading_de"], spec["practical_reading_de"], f"{key[0]} spec reading")
        a.equal(bundle["decisive_reason_de"], spec["decisive_reason_de"], f"{key[0]} spec reason")
        a.equal(bundle["v78_immediate_decision"], action["v78_decision"], f"{key[0]} immediate preservation")
        a.equal((bundle["immediate_decision_preserved"], bundle["portable_default"], bundle["word_delta"]),
                ("1", "NO", "0"), f"{key[0]} preservation flags")

    b032 = one(bundles, "A083 bundle", action_case_id="A083")
    a.equal((b032["bundle_case_id"], b032["locus"], b032["action_ordinal"], b032["action_surface"]),
            ("B032", "f8r.15", "1", "dchey"), "A083 source")
    a.equal((b032["item_ordinals"], b032["item_surfaces"]), ("2|3|4", "ckhol|chol|chey"), "A083 bundle")
    a.equal((b032["v78_immediate_decision"], b032["decision_mode"], b032["bundle_decision"]),
            ("CONTROL_CONFLICT", "BUNDLE_ADMIT_AFTER_IMMEDIATE_CONFLICT", "ADMIT_RESULT_BUNDLE"), "A083 decisions")
    a.equal((b032["right_stop_ordinals"], b032["right_stop_surfaces"]), ("5|6", "kc|chy"), "A083 right boundary")
    a.equal(b032["practical_reading_de"], C020_READING, "A083 cautious reader")
    a.require("möglicher Ergebnisblock" in b032["practical_reading_de"], "A083 epistemic wording")

    reconstructed_short = []
    for action in old["actions"]:
        items = semantic_windows.get(action["action_case_id"], [])
        if action["disposition"] == "DELAYED_NOMINAL_WINDOW" and len(items) == 2:
            reconstructed_short.append((
                action["action_case_id"], "|".join(item["token_ordinal"] for item in items),
                "|".join(item["surface"] for item in items),
                "|".join(item["v79_token_gloss_de"] for item in items),
            ))
    a.equal([(row["action_case_id"], row["item_ordinals"], row["item_surfaces"], row["item_glosses_de"]) for row in shorts],
            reconstructed_short, "two-item controls complete")
    a.equal({row["action_case_id"] for row in shorts},
            {"A005", "A038", "A041", "A048", "A049", "A071", "A072", "A075", "A079", "A082"},
            "exact short cases")

    a.equal({row["action_case_id"] for row in dchey},
            {"A013", "A017", "A025", "A032", "A036", "A037", "A068", "A079", "A083"},
            "all dchey contexts")
    a.equal(Counter(row["context_decision"] for row in dchey), Counter({
        "BUNDLE_ADMIT_AFTER_IMMEDIATE_CONFLICT": 1, "THREE_ITEM_CONTROL_STOP": 3,
        "ONE_ITEM_LENGTH_CONTROL": 2, "TWO_ITEM_LENGTH_CONTROL": 1, "NEXT_ACTION_BOUNDARY": 2,
    }), "dchey decision deck")
    for row in dchey:
        action = action_index[(row["action_case_id"],)]
        a.equal(action["action_surface"], "dchey", f"{row['action_case_id']} exact action")
        a.equal(row["right_clause_type"], action["right_clause_type"], f"{row['action_case_id']} right type")
        a.equal(row["semantic_item_count"], str(len(semantic_windows.get(row["action_case_id"], []))),
                f"{row['action_case_id']} item count")

    expected_surface = [row for row in old["tokens"] if row["surface"] in {"ckhol", "chol", "chey"}]
    a.equal(Counter(row["surface"] for row in surfaces), Counter({"ckhol": 1, "chol": 6, "chey": 3}), "surface counts")
    a.equal([(row["locus"], row["token_ordinal"], row["surface"], row["token_gloss_de"]) for row in surfaces],
            [(row["locus"], row["token_ordinal"], row["surface"], row["v79_token_gloss_de"]) for row in expected_surface],
            "surface controls complete")
    a.equal(sum(row["a083_role"] == "NONE" for row in surfaces), 7, "seven external surface controls")
    a.equal(Counter(row["a083_role"] for row in surfaces if row["a083_role"] != "NONE"), Counter({
        "RESULT_MATERIAL_CARRIER:C020": 1,
        "RESULT_DRY_QUALITY:C020": 1,
        "WRITTEN_MIDDLE_DRY_RESULT:C020": 1,
    }), "three local C020 surface roles")
    early_chey = one(surfaces, "f107r inaccessible chey", locus="f107r.2", token_ordinal="11")
    a.require("zweiten Item #8 cheockhy" in early_chey["note_de"], "f107r chey earliest stop provenance")
    open_chol = one(surfaces, "f30r open chol", locus="f30r.9", token_ordinal="3")
    a.require("GDT705 hält chol" in open_chol["note_de"] and "#4 keeaiin" in open_chol["note_de"],
              "f30r chol provenance")
    unique_ckhol = one(surfaces, "unique ckhol", surface="ckhol")
    a.equal((unique_ckhol["locus"], unique_ckhol["token_ordinal"], unique_ckhol["a083_role"]),
            ("f8r.15", "2", "RESULT_MATERIAL_CARRIER:C020"), "ckhol role")

    c020 = one(edge, "C020 edge", edge_id="C020")
    a.equal((c020["component_id"], c020["locus"], c020["edge_node_ordinals"]),
            ("M013", "f8r.15", "1|4"), "C020 endpoints")
    a.equal((c020["result_material_ordinal"], c020["result_material_surface"],
             c020["result_quality_ordinal"], c020["result_quality_surface"],
             c020["written_result_ordinal"], c020["written_result_surface"]),
            ("2", "ckhol", "3", "chol", "4", "chey"), "C020 result members")
    a.equal((c020["rendered_result_bundle_ordinals"], c020["rendered_result_bundle_surfaces"]),
            ("2|3|4", "ckhol|chol|chey"), "C020 rendered bundle")
    a.equal((c020["material_agreement"], c020["quantity_agreement"], c020["completion_agreement"]),
            ("LOCAL_COMPATIBLE_MATERIAL_CARRIER_NOT_IDENTICAL_PATIENT", "ACTION_ONLY_NOT_REPEATED",
             "NONE_MIDDLE_IS_NOT_FINISHED"), "C020 non-overclaim flags")
    a.equal((c020["portability"], c020["gdt388_score_ready"], c020["edge_delta"], c020["word_delta"]),
            ("OCCURRENCE_BOUND_ONLY", "0", "1", "0"), "C020 edge flags")
    a.equal(c020["working_microrecord_de"], C020_READING, "C020 exact reader")

    old_membership_index = keyed(old["memberships"], ("edge_id",))
    membership_index = keyed(memberships, ("edge_id",))
    a.equal(set(membership_index), {(f"C{i:03d}",) for i in range(1, 21) if i != 16}, "edge IDs")
    for key, old_row in old_membership_index.items():
        new_row = membership_index[key]
        for field in old_fields["memberships"][:-1]:
            a.equal(new_row[field], old_row[field], f"{key[0]} inherited membership {field}")
        a.equal(new_row["v80_change"], "NONE", f"{key[0]} no V80 change")
    c020_member = membership_index[("C020",)]
    a.equal((c020_member["component_id"], c020_member["edge_node_ordinals"], c020_member["source_ordinals"],
             c020_member["target_ordinal"], c020_member["shared_edge_node_ordinals"]),
            ("M013", "1|4", "1", "4", "NONE"), "C020 membership")

    old_component_index = keyed(old["components"], ("component_id",))
    component_index = keyed(components, ("component_id",))
    for key, old_row in old_component_index.items():
        new_row = component_index[key]
        for field in old_fields["components"][:-1]:
            a.equal(new_row[field], old_row[field], f"{key[0]} inherited component {field}")
        a.equal((new_row["v80_edge_delta"], new_row["v80_change"]), ("0", "NONE"), f"{key[0]} no V80 delta")
    m013 = component_index[("M013",)]
    a.equal((m013["locus"], m013["edge_ids"], m013["edge_node_ordinals"], m013["hull_only_ordinals"]),
            ("f8r.15", "C020", "1|4", "2|3"), "M013 identity")
    a.equal((m013["edge_hull_start"], m013["edge_hull_end"], m013["edge_hull_position_count"],
             m013["render_window_start"], m013["render_window_end"], m013["render_window_token_count"]),
            ("1", "4", "4", "1", "4", "4"), "M013 hull")
    a.equal(m013["microrecord_de"], C020_READING, "M013 reader")

    old_position_index = keyed(old["positions"], ("component_id", "token_ordinal"))
    position_index = keyed(positions, ("component_id", "token_ordinal"))
    for key, old_row in old_position_index.items():
        new_row = position_index[key]
        for field in old_fields["positions"][:-1]:
            a.equal(new_row[field], old_row[field], f"{key} inherited position {field}")
        a.equal(new_row["v80_change"], "NONE", f"{key} no V80 position change")
    m013_positions = [row for row in positions if row["component_id"] == "M013"]
    a.equal([(row["token_ordinal"], row["surface"], row["membership_class"]) for row in m013_positions],
            [("1", "dchey", "EDGE_NODE"), ("2", "ckhol", "HULL_ONLY"),
             ("3", "chol", "HULL_ONLY"), ("4", "chey", "EDGE_NODE")], "M013 positions")
    for row in m013_positions:
        if row["token_ordinal"] in {"2", "3"}:
            a.equal((row["edge_ids"], row["source_edge_ids"], row["reference_edge_ids"], row["target_edge_ids"]),
                    ("NONE", "NONE", "NONE", "NONE"), f"M013 hull-only IDs {row['token_ordinal']}")
            a.equal((row["is_edge_node"], row["is_hull_only"]), ("0", "1"), f"M013 hull-only flags {row['token_ordinal']}")
    a.equal(Counter(row["membership_class"] for row in positions), Counter({"EDGE_NODE": 35, "HULL_ONLY": 5}), "position classes")
    a.equal(sum(int(row["is_shared_edge_node"]) for row in positions), 6, "shared positions")

    node_keys = {(row["locus"], ordinal) for row in memberships for ordinal in row["edge_node_ordinals"].split("|")}
    a.equal(len(node_keys), 35, "unique nodes")
    a.equal(sum(len(row["edge_node_ordinals"].split("|")) for row in memberships), 41, "edge incidences")
    a.equal(sum(int(row["edge_hull_position_count"]) for row in components), 40, "hull positions")
    a.equal(sum(int(row["render_window_token_count"]) for row in components), 40, "render positions")
    topology_index = keyed(topology, ("dimension", "value"))
    for key, expected in {
        ("TRIPLE_UNIVERSE", "ACTION_ADJACENT_LEADING"): "32",
        ("TRIPLE_UNIVERSE", "LATER_STARTING_CONTROL"): "87",
        ("LENGTH_CONTROL", "TWO_SEMANTIC_ITEMS_ONLY"): "10",
        ("BUNDLE_DECISION", "ADMIT_RESULT_BUNDLE"): "1",
        ("BUNDLE_DECISION", "HOLD"): "4",
        ("BUNDLE_DECISION", "STOP"): "27",
        ("GRAPH_COUNT", "EDGE_INCIDENCE"): "41",
        ("GRAPH_COUNT", "MINIMAL_HULL_POSITION"): "40",
        ("GRAPH_COUNT", "RENDER_POSITION"): "40",
    }.items():
        a.equal(topology_index[key]["count"], expected, f"topology count {key}")

    packet = one(loaded["packet"], "C020 packet", edge_id="C020")
    a.equal((packet["page"], packet["physical_folio"], packet["pivot_locus"], packet["target_locus"]),
            ("f8r", "f8", "f8r.15@1", "f8r.15@2-4"), "packet loci")
    a.equal((packet["formal_access_state"], packet["eligibility_status"]),
            ("FORMAL_ACCESSED", "INELIGIBLE_WORKSHOP_EDGE"), "packet formal state")
    packet_run = subprocess.run(
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
    a.equal(packet_run.returncode, 1, "packet must fail score gate")
    a.equal(packet_run.stderr, "", "packet stderr")
    a.equal(json.loads(packet_run.stdout), expected_intake, "packet stdout")
    a.equal(json.loads((ART / "V80_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8")),
            expected_intake, "saved packet intake")

    a.equal(fields["tokens"][:len(old_fields["tokens"])], old_fields["tokens"], "token prefix schema")
    a.equal(fields["lines"][:len(old_fields["lines"])], old_fields["lines"], "line prefix schema")
    a.equal(fields["spans"][:len(old_fields["spans"])], old_fields["spans"], "span prefix schema")
    for number, (new_row, old_row) in enumerate(zip(tokens, old["tokens"], strict=True), 1):
        for field in old_fields["tokens"]:
            a.equal(new_row[field], old_row[field], f"token {number} inherited {field}")
        a.equal(new_row["v80_token_gloss_de"], old_row["v79_token_gloss_de"], f"token {number} gloss")
        a.equal(new_row["v80_word_delta"], "0", f"token {number} word delta")
    for number, (new_row, old_row) in enumerate(zip(lines, old["lines"], strict=True), 1):
        for field in old_fields["lines"]:
            a.equal(new_row[field], old_row[field], f"line {number} inherited {field}")
        a.equal(new_row["v80_line_translation_de"], old_row["v79_line_translation_de"], f"line {number} translation")
        a.equal(new_row["v80_word_delta"], "0", f"line {number} word delta")
    for number, (new_row, old_row) in enumerate(zip(spans, old["spans"], strict=True), 1):
        for field in old_fields["spans"]:
            a.equal(new_row[field], old_row[field], f"span {number} inherited {field}")
        a.equal(new_row["v80_selected_gloss_de"], old_row["v79_selected_gloss_de"], f"span {number} gloss")
        a.equal((new_row["v80_byte_identical"], new_row["v80_relation_change"]), ("1", "NONE"), f"span {number} flags")

    token_out_index = keyed(tokens, ("locus", "token_ordinal"))
    for ordinal, expected in {
        "1": ("C020", "EDGE_NODE", "C020"),
        "2": ("NONE", "HULL_ONLY", "NONE"),
        "3": ("NONE", "HULL_ONLY", "NONE"),
        "4": ("C020", "EDGE_NODE", "C020"),
    }.items():
        row = token_out_index[("f8r.15", ordinal)]
        a.equal((row["v80_component_edge_ids"], row["v80_component_membership_class"],
                 row["v80_new_three_item_result_edge_ids"]), expected, f"f8r.15#{ordinal} overlay")
        a.equal(row["v80_component_id"], "M013", f"f8r.15#{ordinal} component")
    a.equal(sum(row["v80_new_three_item_result_edge_ids"] == "C020" for row in tokens), 2, "two C020 token endpoints")
    a.equal(sum(row["v80_new_three_item_result_edge_ids"] == "C020" for row in lines), 1, "one C020 line")
    c020_line = one(lines, "C020 line", locus="f8r.15")
    a.equal(c020_line["v80_working_relation_reading_de"], C020_READING, "line C020 reader")

    result_path = ART / "RESULT.json"
    a.require(result_path.is_file(), "RESULT exists")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    a.equal(result["status"], STATUS, "result status")
    expected_basis = {
        "semantic_triples": 119, "action_adjacent_leading_triples": 32,
        "later_starting_triple_controls": 87, "two_item_length_controls": 10,
        "new_admits": 1, "holds": 4, "stops": 27, "dchey_contexts": 9,
        "bundle_surface_occurrences": 10, "external_surface_controls": 7,
        "local_bundle_surface_roles": 3, "relation_edges_before": 18,
        "relation_edges_after": 19, "connected_components": 13, "edge_nodes": 35,
        "edge_node_incidences": 41, "minimal_hull_positions": 40,
        "render_positions": 40, "shared_edge_nodes": 6, "hull_only_positions": 5,
        "render_only_structural_positions": 0, "structural_closure_positions": 1,
        "f84_access": 0, "f84r_access": 0,
    }
    for field, expected in expected_basis.items():
        a.equal(result["basis"][field], expected, f"result basis {field}")
    a.equal(result["decision"]["c020"], "f8r.15#1→f8r.15#4", "result C020")
    a.equal(result["decision"]["rendered_result_bundle"], "f8r.15#2-4", "result bundle")
    a.equal(result["decision"]["immediate_a083_decision_preserved"], "CONTROL_CONFLICT", "result immediate decision")
    a.equal(result["decision"]["held_bundle_cases"], ["B006", "B007", "B012", "B018"], "result holds")
    a.equal((result["decision"]["patient_identity_asserted"], result["decision"]["completion_asserted"],
             result["decision"]["portable_default"], result["decision"]["new_word_meanings"]),
            (False, False, False, 0), "result no overclaim")
    a.equal(result["word_preservation"], {
        "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
        "bound_spans_byte_identical": 3, "new_word_meanings": 0,
        "changed_word_meanings": 0, "content_word_additions": 0,
        "content_word_deletions": 0, "content_word_reorders": 0,
    }, "word preservation summary")
    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        a.require(path.is_file(), f"result input exists {relative}")
        a.equal(sha256(path), digest, f"result input hash {relative}")
    for name, digest in result["files"].items():
        path = ART / name
        a.require(path.is_file(), f"result file exists {name}")
        a.equal(sha256(path), digest, f"result file hash {name}")

    reader = (ART / "GDT707_V80_THREE_ITEM_RESULT_READER.md").read_text(encoding="utf-8")
    a.require(C020_READING in reader, "reader exact C020")
    a.require("Portion sicher derselbe Stoff" in reader and "Abschluss" in reader, "reader caveats")
    a.require("19 Kanten" in reader and "13 Komponenten" in reader, "reader graph")
    a.require("Wörter und alte Zeilenübersetzungen bleiben unverändert" in reader, "reader preservation")
    a.require("des Drogenstoffs" not in C020_READING, "no fused patient syntax")

    return {
        "status": "PASS_INDEPENDENT_V80_POPULATION_GRAPH_AND_WORD_PRESERVATION_AUDIT",
        "experiment_status": STATUS, "checks": a.checks,
        "populations": {
            "semantic_triples": 119, "action_adjacent_bundles": 32,
            "later_starting_controls": 87, "two_item_controls": 10,
            "dchey_contexts": 9, "bundle_surface_occurrences": 10,
            "external_surface_controls": 7, "local_bundle_surface_roles": 3,
        },
        "decisions": {"admit": 1, "holds": 4, "stops": 27, "new_edge": "C020"},
        "graph": {
            "edges": 19, "components": 13, "edge_nodes": 35, "incidences": 41,
            "hull_positions": 40, "render_positions": 40, "shared_nodes": 6,
            "hull_only": 5, "structural_closures": 1,
        },
        "word_preservation": {"tokens": 479, "lines": 51, "spans": 3, "new_word_meanings": 0},
        "gdt388_score_ready": False, "f84_access": 0, "f84r_access": 0,
    }


def main() -> int:
    result = validate()
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
