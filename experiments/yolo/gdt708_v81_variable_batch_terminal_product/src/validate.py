#!/usr/bin/env python3
"""Independent validator for GDT708; deliberately does not import run.py."""

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
EXP = ROOT / "experiments/yolo/gdt708_v81_variable_batch_terminal_product"
SRC, ART = EXP / "src", EXP / "artifacts"
VALIDATION = ART / "VALIDATION.json"
STATUS = (
    "PASS_V81_9_VARIABLE_BUNDLES__1_NEW_C021_8_LIVE_HOLDS__"
    "20_EDGES_14_COMPONENTS__ZERO_WORD_DELTA"
)
C021_READING = (
    "Das Arzneikompositum bis zur Mittelstufe aufbereiten. Danach stehen: abgemessener Anteil II; "
    "Rohstoff I; heiße Mittelstufe. Mögliches terminales Produkt: bis zur Mittelstufe "
    "eingeweichtes und abgeschlossenes Arzneikompositum."
)
G707 = ROOT / "experiments/yolo/gdt707_v80_three_item_material_state_result_bundle/artifacts"


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
        "spec": SRC / "V81_9_VARIABLE_BUNDLE_SPECS.tsv",
        "census": ART / "V81_9_VARIABLE_BUNDLE_CENSUS.tsv",
        "terminal": ART / "V81_4_TERMINAL_PRODUCT_ORDER_TEST.tsv",
        "prefix": ART / "V81_5_RANK2_PREFIX_BOUNDARY_TEST.tsv",
        "edge": ART / "V81_1_NEW_VARIABLE_RESULT_EDGE.tsv",
        "memberships": ART / "V81_20_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": ART / "V81_14_CONNECTED_COMPONENTS.tsv",
        "positions": ART / "V81_45_COMPONENT_POSITION_ROLES.tsv",
        "topology": ART / "V81_COMPONENT_TOPOLOGY_CENSUS.tsv",
        "packet": ART / "V81_GDT388_EDGE_PACKET.tsv",
        "tokens": ART / "V81_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": ART / "V81_51_LINE_RELATION_OVERLAY.tsv",
        "spans": ART / "V81_3_BOUND_SPAN_FREEZE.tsv",
    }
    fields: dict[str, list[str]] = {}
    loaded: dict[str, list[dict[str, str]]] = {}
    for name, path in paths.items():
        fields[name], loaded[name] = read_tsv(path, a)

    old_paths = {
        "bundles": G707 / "V80_32_ACTION_ADJACENT_BUNDLE_CENSUS.tsv",
        "memberships": G707 / "V80_19_EDGE_COMPONENT_MEMBERSHIP.tsv",
        "components": G707 / "V80_13_CONNECTED_COMPONENTS.tsv",
        "positions": G707 / "V80_40_COMPONENT_POSITION_ROLES.tsv",
        "tokens": G707 / "V80_479_TOKEN_RELATION_OVERLAY.tsv",
        "lines": G707 / "V80_51_LINE_RELATION_OVERLAY.tsv",
        "spans": G707 / "V80_3_BOUND_SPAN_FREEZE.tsv",
    }
    old_fields: dict[str, list[str]] = {}
    old: dict[str, list[dict[str, str]]] = {}
    for name, path in old_paths.items():
        old_fields[name], old[name] = read_tsv(path, a)

    specs, census = loaded["spec"], loaded["census"]
    terminal, prefix, edge = loaded["terminal"], loaded["prefix"], loaded["edge"]
    memberships, components, positions = loaded["memberships"], loaded["components"], loaded["positions"]
    tokens, lines, spans = loaded["tokens"], loaded["lines"], loaded["spans"]
    a.equal((len(specs), len(census), len(terminal), len(prefix)), (9, 9, 4, 5), "candidate populations")
    a.equal((len(edge), len(memberships), len(components), len(positions)), (1, 20, 14, 45), "graph populations")
    a.equal((len(tokens), len(lines), len(spans)), (479, 51, 3), "overlay populations")
    a.equal([row["candidate_id"] for row in specs], [f"V81C{i:03d}" for i in range(1, 10)], "spec IDs")
    a.equal(Counter(row["decision"] for row in specs), Counter({
        "ADMIT_C021": 1, "HOLD_OBJECT_BLOCK": 2,
        "STOP_LONGER_RETAIN_IMMEDIATE_HOLD": 1, "HOLD_TWO_ITEM_PREFIX": 5,
    }), "spec decisions")
    a.equal(sum(int(row["live_hold"]) for row in specs), 8, "eight live holds")
    a.equal(Counter(row["selected_length"] for row in census), Counter({"1": 1, "2": 5, "3": 1, "4": 2}), "variable lengths")
    a.require(all(row["portable_default"] == "NO" for row in specs + census), "no portable default")
    a.require(all(row["patient_identity_asserted"] == "0" for row in census), "no patient identity")
    a.require(all(row["status"] == STATUS for rows in loaded.values() for row in rows if "status" in row), "single output status")

    bundle_index = keyed(old["bundles"], ("action_case_id",))
    token_index = keyed(old["tokens"], ("locus", "token_ordinal"))
    spec_index = keyed(specs, ("candidate_id",))
    census_index = keyed(census, ("candidate_id",))
    a.equal(set(spec_index), set(census_index), "spec/census identity")
    for key, row in census_index.items():
        spec = spec_index[key]
        action = bundle_index[(row["action_case_id"],)]
        for field in ("page", "locus", "action_ordinal", "action_surface", "action_gloss_de"):
            a.equal(row[field], action[field], f"{key[0]} action join {field}")
        ordinals = spec["selected_item_ordinals"].split("|")
        selected = [token_index[(row["locus"], ordinal)] for ordinal in ordinals]
        boundaries = [token_index[(row["locus"], ordinal)] for ordinal in spec["first_boundary_ordinals"].split("|")]
        a.equal(row["selected_item_ordinals"], spec["selected_item_ordinals"], f"{key[0]} ordinals")
        a.equal(row["selected_item_surfaces"], "|".join(item["surface"] for item in selected), f"{key[0]} surfaces")
        a.equal(row["selected_item_surfaces"], spec["expected_item_surfaces"], f"{key[0]} expected surfaces")
        a.equal(row["selected_item_glosses_de"], "|".join(item["v80_token_gloss_de"] for item in selected), f"{key[0]} glosses")
        a.equal(row["first_boundary_surfaces"], "|".join(item["surface"] for item in boundaries), f"{key[0]} boundary surfaces")
        a.equal(row["first_boundary_glosses_de"], "|".join(item["v80_token_gloss_de"] for item in boundaries), f"{key[0]} boundary glosses")
        a.equal(row["v81_decision"], spec["decision"], f"{key[0]} decision")
        a.equal(row["practical_reading_de"], spec["practical_reading_de"], f"{key[0]} reading")
        a.equal(row["decisive_reason_de"], spec["decisive_reason_de"], f"{key[0]} reason")
        a.equal(row["gdt707_full_bundle_decision"], action["bundle_decision"], f"{key[0]} inherited decision")
    a.equal({row["action_case_id"] for row in census}, {"A012", "A014", "A024", "A043", "A073", "A070", "A029", "A017", "A004"}, "exact candidate deck")
    a.equal({row["action_case_id"] for row in census if row["gdt707_full_bundle_decision"] == "HOLD"}, {"A012", "A014", "A024", "A043"}, "four inherited full holds")
    a.equal({row["action_case_id"] for row in census if row["gdt707_full_bundle_decision"] == "STOP"}, {"A073", "A070", "A029", "A017", "A004"}, "five shorter salvages")

    c021_case = one(census, "C021 candidate", action_case_id="A012")
    a.equal((c021_case["locus"], c021_case["action_ordinal"], c021_case["selected_item_ordinals"]), ("f106r.23", "2", "3|4|5|6"), "A012 path")
    a.equal((c021_case["selected_item_surfaces"], c021_case["hypothetical_edge_node_ordinals"], c021_case["hypothetical_hull_only_ordinals"]), ("dair|al|qokedy|shecphy", "2|6", "3|4|5"), "A012 structure")
    a.equal((c021_case["first_boundary_ordinals"], c021_case["first_boundary_surfaces"], c021_case["boundary_class"]), ("7", "qokchy", "STATE_AND_DEGREE_RESET"), "A012 boundary")
    a.equal(c021_case["practical_reading_de"], C021_READING, "A012 reader")
    a.require("Arzneikompositum" in c021_case["selected_item_glosses_de"] and "abgeschlossen" in c021_case["selected_item_glosses_de"], "A012 terminal product payload")
    a043 = one(census, "A043 countercase", action_case_id="A043")
    a.equal((a043["selected_length"], a043["v81_decision"], a043["live_hold"]), ("1", "STOP_LONGER_RETAIN_IMMEDIATE_HOLD", "1"), "A043 hold preservation")
    a.equal((a043["first_boundary_ordinals"], a043["first_boundary_surfaces"]), ("4|5", "keey|daiin"), "A043 reset")

    a.equal([row["test_id"] for row in terminal], ["TP001", "TP002", "TP003", "TP004"], "terminal IDs")
    a.equal([(row["action_case_id"], row["terminal_ordinal"], row["terminal_surface"]) for row in terminal], [
        ("A012", "6", "shecphy"), ("A014", "5", "oteed"),
        ("A024", "7", "teeedy"), ("A043", "3", "dchey"),
    ], "terminal endpoints")
    a.equal(Counter(row["observed_order"] for row in terminal), Counter({"AFTER_ATTRIBUTES": 3, "BEFORE_LATER_ATTRIBUTES": 1}), "terminal order contrast")
    a.equal(one(terminal, "A012 terminal", action_case_id="A012")["order_test"], "SUPPORTS_AND_ADMITS", "A012 terminal decision")
    a.equal(one(terminal, "A043 terminal", action_case_id="A043")["order_test"], "ORDER_COUNTERCASE", "A043 terminal countercase")

    a.equal([row["test_id"] for row in prefix], ["P001", "P002", "P003", "P004", "P005"], "prefix IDs")
    a.equal([row["action_case_id"] for row in prefix], ["A073", "A070", "A029", "A017", "A004"], "prefix order")
    a.require(all((row["selected_rank"], row["first_rejected_rank"], row["v81_decision"]) == ("2", "3", "HOLD_TWO_ITEM_PREFIX") for row in prefix), "all rank2 holds")
    for row in prefix:
        census_row = one(census, f"{row['action_case_id']} census", action_case_id=row["action_case_id"])
        a.equal(row["selected_ordinals"], census_row["selected_item_ordinals"], f"{row['action_case_id']} selected ordinals")
        a.equal(row["first_rejected_ordinal"], census_row["first_boundary_ordinals"].split("|")[0], f"{row['action_case_id']} rejected ordinal")

    c021 = one(edge, "C021 edge", edge_id="C021")
    a.equal((c021["component_id"], c021["locus"], c021["edge_node_ordinals"]), ("M014", "f106r.23", "2|6"), "C021 identity")
    a.equal((c021["attribute_ordinals"], c021["attribute_surfaces"], c021["attribute_roles"]), ("3|4|5", "dair|al|qokedy", "QUANTITY|MATERIAL|STATE_DEGREE"), "C021 attributes")
    a.equal((c021["written_result_ordinal"], c021["written_result_surface"]), ("6", "shecphy"), "C021 terminal")
    a.equal(c021["working_microrecord_de"], C021_READING, "C021 microrecord")
    a.equal((c021["portability"], c021["gdt388_score_ready"], c021["word_delta"]), ("OCCURRENCE_BOUND_ONLY", "0", "0"), "C021 ceiling")
    a.require("Keine Patientengleichheit" in c021["forbidden_inference"], "C021 patient ceiling")

    old_membership_index = keyed(old["memberships"], ("edge_id",))
    membership_index = keyed(memberships, ("edge_id",))
    a.equal(set(membership_index) - set(old_membership_index), {("C021",)}, "one new membership")
    for key, old_row in old_membership_index.items():
        new_row = membership_index[key]
        for field in old_fields["memberships"][:-1]:
            a.equal(new_row[field], old_row[field], f"preserve membership {key[0]} {field}")
        a.equal(new_row["v81_change"], "NONE", f"preserve membership {key[0]} flag")
    new_membership = membership_index[("C021",)]
    a.equal((new_membership["component_id"], new_membership["edge_node_ordinals"], new_membership["source_ordinals"], new_membership["target_ordinal"]), ("M014", "2|6", "2", "6"), "C021 membership")

    old_component_index = keyed(old["components"], ("component_id",))
    component_index = keyed(components, ("component_id",))
    a.equal(set(component_index) - set(old_component_index), {("M014",)}, "one new component")
    for key, old_row in old_component_index.items():
        new_row = component_index[key]
        for field in old_fields["components"][:-1]:
            a.equal(new_row[field], old_row[field], f"preserve component {key[0]} {field}")
        a.equal((new_row["v81_edge_delta"], new_row["v81_change"]), ("0", "NONE"), f"preserve component {key[0]} flags")
    m014 = component_index[("M014",)]
    a.equal((m014["locus"], m014["edge_ids"], m014["edge_node_ordinals"]), ("f106r.23", "C021", "2|6"), "M014 identity")
    a.equal((m014["edge_hull_start"], m014["edge_hull_end"], m014["hull_only_ordinals"]), ("2", "6", "3|4|5"), "M014 hull")
    a.equal((m014["render_window_start"], m014["render_window_end"], m014["render_window_token_count"]), ("2", "6", "5"), "M014 render")
    a.equal(m014["microrecord_de"], C021_READING, "M014 microrecord")

    old_position_index = keyed(old["positions"], ("component_id", "locus", "token_ordinal"))
    position_index = keyed(positions, ("component_id", "locus", "token_ordinal"))
    a.equal(len(set(position_index) - set(old_position_index)), 5, "five new positions")
    for key, old_row in old_position_index.items():
        new_row = position_index[key]
        for field in old_fields["positions"][:-1]:
            a.equal(new_row[field], old_row[field], f"preserve position {key} {field}")
        a.equal(new_row["v81_change"], "NONE", f"preserve position {key} flag")
    m014_positions = [row for row in positions if row["component_id"] == "M014"]
    a.equal([row["token_ordinal"] for row in m014_positions], ["2", "3", "4", "5", "6"], "M014 ordinals")
    a.equal([row["surface"] for row in m014_positions], ["qckhedy", "dair", "al", "qokedy", "shecphy"], "M014 surfaces")
    a.equal([row["membership_class"] for row in m014_positions], ["EDGE_NODE", "HULL_ONLY", "HULL_ONLY", "HULL_ONLY", "EDGE_NODE"], "M014 position classes")
    a.equal(Counter(row["membership_class"] for row in positions), Counter({"EDGE_NODE": 37, "HULL_ONLY": 8}), "position totals")
    a.equal(sum(int(row["is_shared_edge_node"]) for row in positions), 6, "shared nodes")
    a.equal(sum(int(row["is_render_only_structural"]) for row in positions), 0, "render-only structural")
    node_keys = {(row["locus"], ordinal) for row in memberships for ordinal in row["edge_node_ordinals"].split("|")}
    a.equal(len(node_keys), 37, "unique graph nodes")
    a.equal(sum(len(row["edge_node_ordinals"].split("|")) for row in memberships), 43, "edge incidences")
    a.equal(sum(int(row["edge_hull_position_count"]) for row in components), 45, "hull positions")
    a.equal(sum(int(row["render_window_token_count"]) for row in components), 45, "render positions")

    a.equal(fields["tokens"][:-13], old_fields["tokens"], "token schema extension")
    for number, (new, old_row) in enumerate(zip(tokens, old["tokens"]), 1):
        for field in old_fields["tokens"]:
            a.equal(new[field], old_row[field], f"token {number} preserve {field}")
        a.equal(new["v81_token_gloss_de"], old_row["v80_token_gloss_de"], f"token {number} gloss")
        a.equal((new["v81_word_delta"], new["v81_status"]), ("0", STATUS), f"token {number} flags")
        a.require(not new["page"].startswith("f84"), f"token {number} f84-free")
    a.equal({(row["locus"], row["token_ordinal"]) for row in tokens if row["v81_new_variable_result_edge_ids"] == "C021"}, {("f106r.23", "2"), ("f106r.23", "6")}, "C021 token endpoints only")
    for ordinal in ("3", "4", "5"):
        row = one(tokens, f"C021 hull {ordinal}", locus="f106r.23", token_ordinal=ordinal)
        a.equal((row["v81_component_membership_class"], row["v81_new_variable_result_edge_ids"]), ("HULL_ONLY", "NONE"), f"C021 hull {ordinal} not edge")

    a.equal(fields["lines"][:-11], old_fields["lines"], "line schema extension")
    for number, (new, old_row) in enumerate(zip(lines, old["lines"]), 1):
        for field in old_fields["lines"]:
            a.equal(new[field], old_row[field], f"line {number} preserve {field}")
        a.equal(new["v81_line_translation_de"], old_row["v80_line_translation_de"], f"line {number} translation")
    c021_line = one(lines, "C021 line", locus="f106r.23")
    a.equal((c021_line["v81_new_variable_result_edge_ids"], c021_line["v81_working_relation_reading_de"]), ("C021", C021_READING), "C021 line metadata")
    a.equal(sum(row["v81_new_variable_result_edge_ids"] == "C021" for row in lines), 1, "one C021 line")

    a.equal(fields["spans"][:-4], old_fields["spans"], "span schema extension")
    for number, (new, old_row) in enumerate(zip(spans, old["spans"]), 1):
        for field in old_fields["spans"]:
            a.equal(new[field], old_row[field], f"span {number} preserve {field}")
        a.equal((new["v81_selected_gloss_de"], new["v81_byte_identical"], new["v81_relation_change"]), (old_row["v80_selected_gloss_de"], "1", "NONE"), f"span {number} freeze")

    packet_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(paths["packet"].relative_to(ROOT))],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    a.equal(packet_run.returncode, 1, "GDT388 expected failure")
    a.equal(packet_run.stderr, "", "GDT388 stderr")
    intake = json.loads((ART / "V81_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    a.equal(json.loads(packet_run.stdout), intake, "GDT388 stored replay")
    a.equal(intake, {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }, "GDT388 exact expected status")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    a.equal(result["status"], STATUS, "result status")
    a.equal(result["basis"]["variable_bundle_candidates"], 9, "result candidates")
    a.equal(result["basis"]["new_admits"], 1, "result admit")
    a.equal(result["basis"]["live_holds"], 8, "result holds")
    a.equal((result["basis"]["relation_edges_after"], result["basis"]["connected_components"], result["basis"]["edge_nodes"]), (20, 14, 37), "result graph")
    a.equal(result["decision"]["c021"], "f106r.23#2→f106r.23#6", "result C021")
    a.equal(result["decision"]["a043_longer_extension"], "STOP_LONGER_RETAIN_IMMEDIATE_HOLD", "result A043")
    a.equal((result["decision"]["patient_identity_asserted"], result["decision"]["portable_default"], result["decision"]["new_word_meanings"]), (False, False, 0), "result ceiling")
    for relative, digest in result["inputs"].items():
        a.equal(sha256(ROOT / relative), digest, f"input hash {relative}")
    for name, digest in result["files"].items():
        a.equal(sha256(ART / name), digest, f"file hash {name}")

    reader = (ART / "GDT708_V81_VARIABLE_BATCH_READER.md").read_text(encoding="utf-8")
    a.require(C021_READING in reader, "reader contains C021")
    for action_id in ("A012", "A014", "A024", "A043", "A073", "A070", "A029", "A017", "A004"):
        a.require(f"**{action_id} (" in reader, f"reader contains {action_id}")
    a.require("Q–M–S/G–P" in reader, "reader portability ceiling")

    return {
        "status": STATUS, "checks": a.checks, "candidate_rows": len(census),
        "terminal_order_rows": len(terminal), "rank2_prefix_rows": len(prefix),
        "new_edge": "C021", "relation_edges": len(memberships),
        "components": len(components), "positions": len(positions),
        "token_glosses_preserved": len(tokens), "line_translations_preserved": len(lines),
        "bound_spans_preserved": len(spans), "new_word_meanings": 0,
        "f84_access": 0, "f84r_access": 0,
    }


def main() -> int:
    result = validate()
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
