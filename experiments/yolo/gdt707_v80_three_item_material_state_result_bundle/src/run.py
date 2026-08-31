#!/usr/bin/env python3
"""Build GDT707's exhaustive three-item bundle census and local C020 graph edge."""

from __future__ import annotations

import csv
import hashlib
import json
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
EXP = ROOT / "experiments/yolo/gdt707_v80_three_item_material_state_result_bundle"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V80_119_TRIPLES__32_ACTION_ADJACENT_BUNDLES__1_NEW_C020_4_HOLDS_"
    "27_STOPS__9_DCHEY_CONTEXTS__19_EDGES_13_COMPONENTS__ZERO_WORD_DELTA"
)
QUESTION = (
    "Does the complete action-adjacent three-item bundle census support A083 "
    "f8r.15#1→#2-4 as a concrete local material-quality-degree result reading?"
)
C020_READING = (
    "Eine abgemessene Portion bis zur Mittelstufe trocknen. Als möglicher Ergebnisblock folgt: "
    "Drogenstoff aus Arzneikompositum – trocken; trocken in der Mitte des Grades."
)
CLAIM = (
    "V80 accounts for all 119 consecutive semantic triples in the 42 delayed nominal windows, "
    "including all 32 action-adjacent leading triples and 87 later-starting controls. C020 locally "
    "links f8r.15#1 dchey to #4 chey while retaining #2 ckhol as the material carrier and #3 chol "
    "as the broad dry-state carrier. The local relation does not assert patient identity, a finished "
    "state, portable syntax, or a word meaning."
)
NEXT_GAP = (
    "Use the 32-row bundle census to inspect whether the four retained bundles A012/A014/A024/A043 "
    "share one predictive material-state architecture; do not reopen A083's word values or a page."
)

G388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G706 = ROOT / "experiments/yolo/gdt706_v79_second_nominal_item_result_census/artifacts"
OLD_ACTIONS = G706 / "V79_83_ACTION_DISPOSITIONS.tsv"
OLD_PAIRS = G706 / "V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv"
OLD_RESULT = G706 / "RESULT.json"
OLD_MEMBERSHIP = G706 / "V79_18_EDGE_COMPONENT_MEMBERSHIP.tsv"
OLD_COMPONENTS = G706 / "V79_12_CONNECTED_COMPONENTS.tsv"
OLD_POSITIONS = G706 / "V79_36_COMPONENT_POSITION_ROLES.tsv"
OLD_TOKENS = G706 / "V79_479_TOKEN_RELATION_OVERLAY.tsv"
OLD_LINES = G706 / "V79_51_LINE_RELATION_OVERLAY.tsv"
OLD_SPANS = G706 / "V79_3_BOUND_SPAN_FREEZE.tsv"
SPEC = SRC / "V80_32_LEADING_BUNDLE_SPECS.tsv"

TRIPLES_OUT = ART / "V80_119_SEMANTIC_TRIPLE_UNIVERSE.tsv"
BUNDLES_OUT = ART / "V80_32_ACTION_ADJACENT_BUNDLE_CENSUS.tsv"
SHORT_OUT = ART / "V80_10_TWO_ITEM_LENGTH_CONTROLS.tsv"
DCHEY_OUT = ART / "V80_9_DCHEY_ACTION_CONTEXTS.tsv"
SURFACE_OUT = ART / "V80_10_BUNDLE_SURFACE_OCCURRENCES.tsv"
EDGE_OUT = ART / "V80_1_NEW_MATERIAL_QUALITY_DEGREE_RESULT_EDGE.tsv"
MEMBERSHIP_OUT = ART / "V80_19_EDGE_COMPONENT_MEMBERSHIP.tsv"
COMPONENTS_OUT = ART / "V80_13_CONNECTED_COMPONENTS.tsv"
POSITIONS_OUT = ART / "V80_40_COMPONENT_POSITION_ROLES.tsv"
TOPOLOGY_OUT = ART / "V80_COMPONENT_TOPOLOGY_CENSUS.tsv"
PACKET_OUT = ART / "V80_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V80_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V80_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V80_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V80_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT707_V80_THREE_ITEM_RESULT_READER.md"
RESULT_OUT = ART / "RESULT.json"

SPEC_FIELDS = [
    "bundle_case_id", "action_case_id", "expected_item_surfaces", "decision",
    "practical_reading_de", "decisive_reason_de", "portable_default",
]
TRIPLE_FIELDS = [
    "triple_id", "action_case_id", "page", "locus", "action_ordinal", "action_surface",
    "action_gloss_de", "right_clause_id", "semantic_start_rank", "item_ordinals",
    "item_surfaces", "item_glosses_de", "action_adjacent", "search_role", "word_delta", "status",
]
BUNDLE_FIELDS = [
    "bundle_case_id", "triple_id", "action_case_id", "page", "locus", "action_ordinal",
    "action_surface", "action_gloss_de", "right_clause_id", "item_ordinals", "item_surfaces",
    "item_glosses_de", "v78_immediate_decision", "bundle_decision", "decision_mode",
    "practical_reading_de", "decisive_reason_de", "right_stop_ordinals", "right_stop_surfaces",
    "right_stop_glosses_de", "immediate_decision_preserved", "portable_default", "word_delta", "status",
]
SHORT_FIELDS = [
    "control_id", "action_case_id", "page", "locus", "action_ordinal", "action_surface",
    "action_gloss_de", "item_ordinals", "item_surfaces", "item_glosses_de", "semantic_item_count",
    "control_role", "word_delta", "status",
]
DCHEY_FIELDS = [
    "dchey_case_id", "action_case_id", "page", "locus", "action_ordinal", "action_gloss_de",
    "right_clause_type", "semantic_item_count", "context_ordinals", "context_surfaces",
    "context_glosses_de", "context_decision", "control_reason_de", "portable_dchey_default",
    "word_delta", "status",
]
SURFACE_FIELDS = [
    "surface_occurrence_id", "surface", "page", "locus", "token_ordinal", "token_gloss_de",
    "a083_role", "portability_role", "note_de", "portable_default", "word_delta", "status",
]
EDGE_FIELDS = [
    "edge_id", "component_id", "locus", "support_tier", "relation_class",
    "source_action_ordinal", "source_action_surface", "source_action_gloss_de",
    "result_material_ordinal", "result_material_surface", "result_material_gloss_de",
    "result_quality_ordinal", "result_quality_surface", "result_quality_gloss_de",
    "written_result_ordinal", "written_result_surface", "written_result_gloss_de",
    "edge_node_ordinals", "rendered_result_bundle_ordinals", "rendered_result_bundle_surfaces",
    "operation_agreement", "degree_agreement", "material_agreement", "quantity_agreement",
    "completion_agreement", "patient_basis", "admission_basis", "working_microrecord_de",
    "strongest_rival_de", "boundary_note_de", "portability", "gdt388_score_ready",
    "forbidden_inference", "edge_delta", "word_delta", "status",
]
PACKET_FIELDS = [
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id", "pivot_visual_id",
    "pivot_locus", "target_visual_id", "target_locus", "relation_type", "direction_basis",
    "ownership_basis", "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
    "relation_confidence", "ambiguity_state", "formal_access_state", "fold_assignment",
    "eligibility_status",
]
TOPOLOGY_FIELDS = ["dimension", "value", "count", "component_ids", "note", "status"]
TOKEN_EXTRA = [
    "v80_bundle_case_ids", "v80_bundle_roles", "v80_bundle_decisions", "v80_component_id",
    "v80_component_position", "v80_component_role", "v80_component_edge_ids",
    "v80_component_membership_class", "v80_component_microrecord_de",
    "v80_new_three_item_result_edge_ids", "v80_token_gloss_de", "v80_word_delta", "v80_status",
]
LINE_EXTRA = [
    "v80_bundle_case_ids", "v80_bundle_decisions", "v80_component_ids", "v80_edge_ids",
    "v80_component_topologies", "v80_component_microrecords_de", "v80_new_three_item_result_edge_ids",
    "v80_working_relation_reading_de", "v80_line_translation_de", "v80_word_delta", "v80_status",
]
SPAN_EXTRA = ["v80_selected_gloss_de", "v80_byte_identical", "v80_relation_change", "v80_status"]


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    assert fields and len(fields) == len(set(fields)), path
    assert all(None not in row and set(row) == set(fields) for row in rows), path
    return fields, rows


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def pipe(values: Sequence[object]) -> str:
    clean = [str(value) for value in values if value not in (None, "", "NONE")]
    return "|".join(dict.fromkeys(clean)) if clean else "NONE"


def pipe_all(values: Sequence[object]) -> str:
    clean = [str(value) for value in values if value not in (None, "", "NONE")]
    return "|".join(clean) if clean else "NONE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(SPEC)
    _, actions = read_tsv(OLD_ACTIONS)
    _, delayed_pairs = read_tsv(OLD_PAIRS)
    membership_fields, old_memberships = read_tsv(OLD_MEMBERSHIP)
    component_fields, old_components = read_tsv(OLD_COMPONENTS)
    position_fields, old_positions = read_tsv(OLD_POSITIONS)
    token_fields, old_tokens = read_tsv(OLD_TOKENS)
    line_fields, old_lines = read_tsv(OLD_LINES)
    span_fields, old_spans = read_tsv(OLD_SPANS)
    old_result = json.loads(OLD_RESULT.read_text(encoding="utf-8"))

    assert spec_fields == SPEC_FIELDS and len(specs) == 32
    assert [row["bundle_case_id"] for row in specs] == [f"B{i:03d}" for i in range(1, 33)]
    assert Counter(row["decision"] for row in specs) == {
        "ADMIT_RESULT_BUNDLE": 1, "HOLD": 4, "STOP": 27,
    }
    assert all(row["portable_default"] == "NO" for row in specs)
    assert len(actions) == 83 and len(delayed_pairs) == 161
    assert len(old_memberships) == 18 and len(old_components) == 12 and len(old_positions) == 36
    assert len(old_tokens) == 479 and len(old_lines) == 51 and len(old_spans) == 3
    assert old_result["basis"]["relation_edges_after"] == 18
    assert all(not row["page"].startswith("f84") for row in old_tokens)

    token_index = {(row["locus"], int(row["token_ordinal"])): row for row in old_tokens}
    action_index = {row["action_case_id"]: row for row in actions}
    semantic_windows: dict[str, list[dict[str, str]]] = {}
    for action in actions:
        if action["right_clause_type"] != "NOMINAL_BLOCK":
            continue
        start, end = int(action["right_clause_start"]), int(action["right_clause_end"])
        items = [
            token_index[(action["locus"], ordinal)] for ordinal in range(start, end + 1)
            if token_index[(action["locus"], ordinal)]["v79_token_gloss_de"] != "."
        ]
        assert len(items) == int(action["nominal_semantic_item_count"])
        semantic_windows[action["action_case_id"]] = items

    triple_rows: list[dict[str, object]] = []
    for action in actions:
        items = semantic_windows.get(action["action_case_id"], [])
        if action["disposition"] != "DELAYED_NOMINAL_WINDOW" or len(items) < 3:
            continue
        for start in range(0, len(items) - 2):
            triple = items[start:start + 3]
            adjacent = int(start == 0)
            triple_rows.append({
                "triple_id": f"T{len(triple_rows) + 1:03d}", "action_case_id": action["action_case_id"],
                "page": action["page"], "locus": action["locus"], "action_ordinal": action["action_ordinal"],
                "action_surface": action["action_surface"], "action_gloss_de": action["action_gloss_de"],
                "right_clause_id": action["right_clause_id"], "semantic_start_rank": start + 1,
                "item_ordinals": pipe_all([item["token_ordinal"] for item in triple]),
                "item_surfaces": pipe_all([item["surface"] for item in triple]),
                "item_glosses_de": pipe_all([item["v79_token_gloss_de"] for item in triple]),
                "action_adjacent": adjacent,
                "search_role": "LEADING_ACTION_RESULT_BUNDLE" if adjacent else "LATER_STARTING_TRIPLE_CONTROL",
                "word_delta": 0, "status": STATUS,
            })
    assert len(triple_rows) == 119
    assert Counter(int(row["action_adjacent"]) for row in triple_rows) == {1: 32, 0: 87}
    write_tsv(TRIPLES_OUT, triple_rows, TRIPLE_FIELDS)

    leading = {row["action_case_id"]: row for row in triple_rows if int(row["action_adjacent"]) == 1}
    assert len(leading) == 32 and set(leading) == {row["action_case_id"] for row in specs}
    bundle_rows: list[dict[str, object]] = []
    for spec in specs:
        triple = leading[spec["action_case_id"]]
        action = action_index[spec["action_case_id"]]
        assert triple["item_surfaces"] == spec["expected_item_surfaces"]
        right_ordinals = right_surfaces = right_glosses = "NONE"
        if spec["action_case_id"] == "A083":
            boundary = [token_index[("f8r.15", ordinal)] for ordinal in (5, 6)]
            right_ordinals = pipe_all([row["token_ordinal"] for row in boundary])
            right_surfaces = pipe_all([row["surface"] for row in boundary])
            right_glosses = pipe_all([row["v79_token_gloss_de"] for row in boundary])
        decision_mode = {
            "ADMIT_RESULT_BUNDLE": "BUNDLE_ADMIT_AFTER_IMMEDIATE_CONFLICT",
            "HOLD": "BUNDLE_HOLD",
            "STOP": "BUNDLE_STOP",
        }[spec["decision"]]
        bundle_rows.append({
            "bundle_case_id": spec["bundle_case_id"], "triple_id": triple["triple_id"],
            **{field: triple[field] for field in BUNDLE_FIELDS[2:12]},
            "v78_immediate_decision": action["v78_decision"], "bundle_decision": spec["decision"],
            "decision_mode": decision_mode, "practical_reading_de": spec["practical_reading_de"],
            "decisive_reason_de": spec["decisive_reason_de"], "right_stop_ordinals": right_ordinals,
            "right_stop_surfaces": right_surfaces, "right_stop_glosses_de": right_glosses,
            "immediate_decision_preserved": 1, "portable_default": spec["portable_default"],
            "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["bundle_decision"] for row in bundle_rows) == {
        "ADMIT_RESULT_BUNDLE": 1, "HOLD": 4, "STOP": 27,
    }
    write_tsv(BUNDLES_OUT, bundle_rows, BUNDLE_FIELDS)

    short_rows: list[dict[str, object]] = []
    for action in actions:
        items = semantic_windows.get(action["action_case_id"], [])
        if action["disposition"] != "DELAYED_NOMINAL_WINDOW" or len(items) != 2:
            continue
        short_rows.append({
            "control_id": f"L{len(short_rows) + 1:03d}", "action_case_id": action["action_case_id"],
            "page": action["page"], "locus": action["locus"], "action_ordinal": action["action_ordinal"],
            "action_surface": action["action_surface"], "action_gloss_de": action["action_gloss_de"],
            "item_ordinals": pipe_all([item["token_ordinal"] for item in items]),
            "item_surfaces": pipe_all([item["surface"] for item in items]),
            "item_glosses_de": pipe_all([item["v79_token_gloss_de"] for item in items]),
            "semantic_item_count": 2, "control_role": "NO_THREE_ITEM_BUNDLE_AVAILABLE",
            "word_delta": 0, "status": STATUS,
        })
    assert len(short_rows) == 10
    write_tsv(SHORT_OUT, short_rows, SHORT_FIELDS)

    dchey_decisions = {
        "A013": ("NEXT_ACTION_BOUNDARY", "Auf dchey folgt sofort eine neue Aktion qoteos."),
        "A017": ("THREE_ITEM_CONTROL_STOP", "Trockenheit passt, aber chty schreibt kalt und Gradanfang statt Mittelstufe."),
        "A025": ("ONE_ITEM_LENGTH_CONTROL", "Nur keey folgt: heiß am Gradende, ohne Material und ohne Mittelstufe."),
        "A032": ("THREE_ITEM_CONTROL_STOP", "Heißer abgezogener Auszug und Materialwechsel ergeben keinen trockenen Mittelgrad-Pfad."),
        "A036": ("THREE_ITEM_CONTROL_STOP", "Erhitzter Auszug wechselt zum Mazerat; trocken allein schließt die Mittelstufe nicht."),
        "A037": ("NEXT_ACTION_BOUNDARY", "Auf dchey folgt sofort die neue Aktion qochar."),
        "A068": ("ONE_ITEM_LENGTH_CONTROL", "Nur ein kalter Ansatz Grad II folgt; Trockenstatus und Mittelstufe fehlen."),
        "A079": ("TWO_ITEM_LENGTH_CONTROL", "Heißer Absud und Grad III liefern kein dreiteiliges Material-Trocken-Mitte-Bündel."),
        "A083": ("BUNDLE_ADMIT_AFTER_IMMEDIATE_CONFLICT", "ckhol|chol|chey schreibt Material, trocken und exakt Mitte ohne inneren Bruch."),
    }
    dchey_rows: list[dict[str, object]] = []
    for action in actions:
        if action["action_surface"] != "dchey":
            continue
        items = semantic_windows.get(action["action_case_id"], [])[:3]
        if items:
            ordinals = pipe_all([item["token_ordinal"] for item in items])
            surfaces = pipe_all([item["surface"] for item in items])
            glosses = pipe_all([item["v79_token_gloss_de"] for item in items])
        else:
            ordinals = action["right_first_ordinal"] or "NONE"
            surfaces = action["right_first_surface"] or "NONE"
            glosses = action["right_first_gloss_de"] or "NONE"
        decision, reason = dchey_decisions[action["action_case_id"]]
        dchey_rows.append({
            "dchey_case_id": f"H{len(dchey_rows) + 1:03d}", "action_case_id": action["action_case_id"],
            "page": action["page"], "locus": action["locus"], "action_ordinal": action["action_ordinal"],
            "action_gloss_de": action["action_gloss_de"], "right_clause_type": action["right_clause_type"],
            "semantic_item_count": len(semantic_windows.get(action["action_case_id"], [])),
            "context_ordinals": ordinals, "context_surfaces": surfaces, "context_glosses_de": glosses,
            "context_decision": decision, "control_reason_de": reason, "portable_dchey_default": "NO",
            "word_delta": 0, "status": STATUS,
        })
    assert len(dchey_rows) == 9
    assert Counter(row["context_decision"] for row in dchey_rows) == {
        "BUNDLE_ADMIT_AFTER_IMMEDIATE_CONFLICT": 1, "THREE_ITEM_CONTROL_STOP": 3,
        "ONE_ITEM_LENGTH_CONTROL": 2, "TWO_ITEM_LENGTH_CONTROL": 1, "NEXT_ACTION_BOUNDARY": 2,
    }
    write_tsv(DCHEY_OUT, dchey_rows, DCHEY_FIELDS)

    surface_notes = {
        ("f8r.15", 2): ("RESULT_MATERIAL_CARRIER:C020", "UNIQUE_CKHOL", "ckhol kommt im 479-Token-Bestand nur hier vor; Einzelfall verhindert Export."),
        ("f8r.15", 3): ("RESULT_DRY_QUALITY:C020", "LOCAL_C020_QUALITY", "chol trägt hier den breiten Trockenstatus innerhalb C020."),
        ("f8r.15", 4): ("WRITTEN_MIDDLE_DRY_RESULT:C020", "LOCAL_C020_TARGET", "chey ist hier nur der lokale Endpunkt des vollständig sichtbaren Dreierbündels."),
        ("f107r.2", 11): ("NONE", "INACCESSIBLE_LATER_CHEY", "A015 stoppt bereits am zweiten Item #8 cheockhy; dieses spätere chey ist kein alternatives dchey-Ergebnis."),
        ("f107r.40", 2): ("NONE", "UNBOUND_NOMINAL_CHEY", "Kein lokaler dchey-Aktionspfad bindet dieses chey als Ergebnis."),
        ("f27r.9", 4): ("NONE", "DCHEY_CONTROL_CHOL", "A036 bleibt wegen Auszug-zu-Mazerat-Wechsel ein Stopp."),
        ("f30r.9", 3): ("NONE", "OPEN_PARTIAL_CHOL", "GDT705 hält chol als unmittelbaren Zustandswert offen; GDT706 stoppt erst das folgende #4 keeaiin als widersprüchlichen Heizzustand."),
        ("f86v3.19", 5): ("NONE", "A070_FIRST_CHOL", "Breiter Trockenwert vor dem früher plausiblen heiß-trockenen Anfang, kein Endpunktstandard."),
        ("f86v3.19", 7): ("NONE", "A070_LATER_CHOL", "Wiederholter Trockenwert nach einem früher plausiblen Zustand, kein zweites Ergebnis."),
        ("f86v6.5", 3): ("NONE", "UNBOUND_NOMINAL_CHOL", "Trockenwert außerhalb C020 ohne portable Ergebnisbindung."),
    }
    relevant = [row for row in old_tokens if row["surface"] in {"ckhol", "chol", "chey"}]
    assert len(relevant) == 10 and {(row["locus"], int(row["token_ordinal"])) for row in relevant} == set(surface_notes)
    surface_rows: list[dict[str, object]] = []
    for row in relevant:
        role, portability_role, note = surface_notes[(row["locus"], int(row["token_ordinal"]))]
        surface_rows.append({
            "surface_occurrence_id": f"S{len(surface_rows) + 1:03d}", "surface": row["surface"], "page": row["page"],
            "locus": row["locus"], "token_ordinal": row["token_ordinal"],
            "token_gloss_de": row["v79_token_gloss_de"], "a083_role": role,
            "portability_role": portability_role, "note_de": note,
            "portable_default": "NO", "word_delta": 0, "status": STATUS,
        })
    assert Counter(row["surface"] for row in surface_rows) == {"ckhol": 1, "chol": 6, "chey": 3}
    write_tsv(SURFACE_OUT, surface_rows, SURFACE_FIELDS)

    new_edge = {
        "edge_id": "C020", "component_id": "M013", "locus": "f8r.15",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_THREE_ITEM_MATERIAL_QUALITY_DEGREE_RESULT",
        "source_action_ordinal": 1, "source_action_surface": "dchey",
        "source_action_gloss_de": "Eine abgemessene Portion bis zur Mittelstufe trocknen",
        "result_material_ordinal": 2, "result_material_surface": "ckhol",
        "result_material_gloss_de": "Drogenstoff aus Arzneikompositum",
        "result_quality_ordinal": 3, "result_quality_surface": "chol", "result_quality_gloss_de": "trocken",
        "written_result_ordinal": 4, "written_result_surface": "chey",
        "written_result_gloss_de": "trocken in der Mitte des Grades", "edge_node_ordinals": "1|4",
        "rendered_result_bundle_ordinals": "2|3|4", "rendered_result_bundle_surfaces": "ckhol|chol|chey",
        "operation_agreement": "DRY_TO_DRY", "degree_agreement": "MIDDLE_STAGE_TO_MIDDLE_OF_GRADE",
        "material_agreement": "LOCAL_COMPATIBLE_MATERIAL_CARRIER_NOT_IDENTICAL_PATIENT",
        "quantity_agreement": "ACTION_ONLY_NOT_REPEATED", "completion_agreement": "NONE_MIDDLE_IS_NOT_FINISHED",
        "patient_basis": "LOCAL_SEQUENCE_ONLY_NO_PRIOR_PATIENT_CARRY",
        "admission_basis": "COMPLETE_MATERIAL_THEN_DRY_QUALITY_THEN_MIDDLE_DEGREE_BUNDLE_WITHOUT_INNER_BREAK",
        "working_microrecord_de": C020_READING,
        "strongest_rival_de": "Die drei Nominalitems können selbständige Registereinträge sein; die Patientengleichheit ist nicht ausgeschrieben.",
        "boundary_note_de": "In der lokalen Arbeitslesung bilden #5 kc mit Charge und Wärme sowie #6 chy mit dem Reset von Mitte auf Anfang gemeinsam eine semantische Grenze; #5 allein ist kein harter Materialbruch.",
        "portability": "OCCURRENCE_BOUND_ONLY", "gdt388_score_ready": 0,
        "forbidden_inference": "Keine sichere Patientengleichheit, keine Menge rechts, kein Abschluss, kein dchey-, ckhol-, chol- oder chey-Standard.",
        "edge_delta": 1, "word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [new_edge], EDGE_FIELDS)

    membership_out_fields = [*membership_fields[:-1], "v80_change", "status"]
    memberships = [
        {**{field: row[field] for field in membership_fields[:-1]}, "v80_change": "NONE", "status": STATUS}
        for row in old_memberships
    ]
    memberships.append({
        "edge_id": "C020", "component_id": "M013", "locus": "f8r.15",
        "support_tier": "B_WORKING_LOCAL", "relation_class": "ACTION_TO_THREE_ITEM_MATERIAL_QUALITY_DEGREE_RESULT",
        "edge_node_ordinals": "1|4", "source_ordinals": "1", "target_ordinal": "4",
        "target_role": "WRITTEN_MIDDLE_DRY_RESULT", "component_edge_count": 1,
        "component_topology": "ACTION_TO_THREE_ITEM_MATERIAL_QUALITY_DEGREE_RESULT",
        "shared_edge_node_ordinals": "NONE", "origin": "GDT707_NEW_OCCURRENCE_BOUND",
        "v75_change": "NONE", "v76_change": "NONE", "v77_change": "NONE", "v78_change": "NONE",
        "v79_change": "NONE", "v80_change": "NEW_EDGE_AND_COMPONENT", "status": STATUS,
    })
    memberships.sort(key=lambda row: int(str(row["edge_id"])[1:]))
    assert len(memberships) == 19
    write_tsv(MEMBERSHIP_OUT, memberships, membership_out_fields)

    component_out_fields = [*component_fields[:-1], "v80_edge_delta", "v80_change", "status"]
    components = [
        {**{field: row[field] for field in component_fields[:-1]}, "v80_edge_delta": 0,
         "v80_change": "NONE", "status": STATUS}
        for row in old_components
    ]
    components.append({
        "component_id": "M013", "locus": "f8r.15", "edge_ids": "C020", "edge_count": 1,
        "edge_node_ordinals": "1|4", "edge_node_count": 2, "shared_edge_node_ordinals": "NONE",
        "edge_hull_start": 1, "edge_hull_end": 4, "edge_hull_position_count": 4,
        "hull_only_ordinals": "2|3", "render_window_start": 1, "render_window_end": 4,
        "render_only_structural_ordinals": "NONE", "render_window_token_count": 4,
        "topology": "ACTION_TO_THREE_ITEM_MATERIAL_QUALITY_DEGREE_RESULT", "action_ordinals": "1",
        "support_profile": "B_WORKING_LOCAL", "expected_surfaces": "dchey|ckhol|chol|chey",
        "observed_surfaces": "dchey|ckhol|chol|chey", "microrecord_de": C020_READING,
        "component_basis": "C020 bewahrt #2 als Materialträger und #3 als breiten Trockenstatus; nur #1 und #4 sind Knoten.",
        "boundary_note_de": "Nur lokal erschlossen: #5 Charge und Wärme plus #6 Gradanfang bilden gemeinsam die rechte semantische Grenze; #5 allein bleibt kompatibel.",
        "forbidden_inference": "Keine Patientengleichheit, kein Abschluss und keine portable Wort- oder Bündelregel.",
        "final_result_status": "WRITTEN_MIDDLE_DRY_RESULT:C020", "origin": "GDT707_NEW_EXACT",
        "edge_delta": 1, "word_delta": 0, "v76_change": "NONE", "v77_edge_delta": 0,
        "v77_change": "NONE", "v78_edge_delta": 0, "v78_change": "NONE", "v79_edge_delta": 0,
        "v79_change": "NONE", "v80_edge_delta": 1, "v80_change": "NEW_COMPONENT", "status": STATUS,
    })
    components.sort(key=lambda row: int(str(row["component_id"])[1:]))
    assert len(components) == 13
    write_tsv(COMPONENTS_OUT, components, component_out_fields)

    position_out_fields = [*position_fields[:-1], "v80_change", "status"]
    positions = [
        {**{field: row[field] for field in position_fields[:-1]}, "v80_change": "NONE", "status": STATUS}
        for row in old_positions
    ]
    m013_specs = {
        1: ("SOURCE_ACTION:C020", "C020", "C020", "NONE", "NONE", "EDGE_NODE", 1, 0, 0, 0, 0, "C020_RESULT_SOURCE_ACTION"),
        2: ("RESULT_BUNDLE_MATERIAL_CARRIER:C020", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", 0, 1, 0, 0, 0, "WRITTEN_C020_MATERIAL_CARRIER_NOT_EDGE_NODE"),
        3: ("RESULT_BUNDLE_DRY_QUALITY:C020", "NONE", "NONE", "NONE", "NONE", "HULL_ONLY", 0, 1, 0, 0, 0, "WRITTEN_C020_DRY_QUALITY_NOT_EDGE_NODE"),
        4: ("WRITTEN_MIDDLE_DRY_RESULT:C020", "C020", "NONE", "NONE", "C020", "EDGE_NODE", 1, 0, 0, 0, 0, "WRITTEN_C020_MIDDLE_DRY_RESULT"),
    }
    for ordinal in range(1, 5):
        token = token_index[("f8r.15", ordinal)]
        role, edges, sources, refs, targets, member, node, hull, structural, action_target, shared, output_role = m013_specs[ordinal]
        positions.append({
            "page": token["page"], "locus": "f8r.15", "token_ordinal": ordinal,
            "surface": token["surface"], "token_gloss_de": token["v79_token_gloss_de"],
            "component_id": "M013", "render_position": ordinal, "render_size": 4,
            "component_role": role, "edge_ids": edges, "source_edge_ids": sources,
            "reference_edge_ids": refs, "target_edge_ids": targets, "membership_class": member,
            "is_edge_node": node, "is_hull_only": hull, "is_render_only_structural": structural,
            "is_action_target": action_target, "is_shared_edge_node": shared,
            "action_output_role": output_role, "component_microrecord_de": C020_READING,
            "word_delta": 0, "v76_change": "NONE", "v77_change": "NONE", "v78_change": "NONE",
            "v79_change": "NONE", "v80_change": "NEW_COMPONENT_POSITION", "status": STATUS,
        })
    positions.sort(key=lambda row: (int(str(row["component_id"])[1:]), int(row["render_position"])))
    assert len(positions) == 40 and Counter(row["membership_class"] for row in positions) == {
        "EDGE_NODE": 35, "HULL_ONLY": 5,
    }
    assert sum(int(row["is_shared_edge_node"]) for row in positions) == 6
    write_tsv(POSITIONS_OUT, positions, position_out_fields)

    topology_groups: dict[str, list[str]] = defaultdict(list)
    support_groups: dict[str, list[str]] = defaultdict(list)
    for row in components:
        topology_groups[str(row["topology"])].append(str(row["component_id"]))
        support_groups[str(row["support_profile"])].append(str(row["component_id"]))
    topology_rows: list[dict[str, object]] = []
    for dimension, groups, note in (
        ("TOPOLOGY", topology_groups, "current exact component topology"),
        ("SUPPORT_PROFILE", support_groups, "local working tiers are not portable defaults"),
    ):
        for value in sorted(groups):
            topology_rows.append({
                "dimension": dimension, "value": value, "count": len(groups[value]),
                "component_ids": pipe(groups[value]), "note": note, "status": STATUS,
            })
    all_components = pipe([row["component_id"] for row in components])
    topology_rows.extend([
        {"dimension": "TRIPLE_UNIVERSE", "value": "ACTION_ADJACENT_LEADING", "count": 32, "component_ids": "NONE", "note": "complete leading three-item population", "status": STATUS},
        {"dimension": "TRIPLE_UNIVERSE", "value": "LATER_STARTING_CONTROL", "count": 87, "component_ids": "NONE", "note": "cannot skip earlier nominal items", "status": STATUS},
        {"dimension": "LENGTH_CONTROL", "value": "TWO_SEMANTIC_ITEMS_ONLY", "count": 10, "component_ids": "NONE", "note": "no three-item bundle available", "status": STATUS},
        {"dimension": "BUNDLE_DECISION", "value": "ADMIT_RESULT_BUNDLE", "count": 1, "component_ids": "M013", "note": "A083 only", "status": STATUS},
        {"dimension": "BUNDLE_DECISION", "value": "HOLD", "count": 4, "component_ids": "NONE", "note": "A012 A014 A024 A043", "status": STATUS},
        {"dimension": "BUNDLE_DECISION", "value": "STOP", "count": 27, "component_ids": "NONE", "note": "visible material operation state or earlier-result break", "status": STATUS},
        {"dimension": "DCHEY_CONTEXT", "value": "ALL_OCCURRENCES", "count": 9, "component_ids": "M013", "note": "one local bundle and eight controls", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "EDGE_NODE", "count": 35, "component_ids": all_components, "note": "unique occurrence nodes", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "HULL_ONLY_NOT_NODE", "count": 5, "component_ids": "M007|M008|M009|M013", "note": "two new C020 bundle carriers", "status": STATUS},
        {"dimension": "POSITION_CLASS", "value": "RENDER_ONLY_STRUCTURAL", "count": 0, "component_ids": "NONE", "note": "none", "status": STATUS},
        {"dimension": "STRUCTURAL_ROLE", "value": "CLAUSE_CLOSURE_NONNODE", "count": 1, "component_ids": "M009", "note": "f26r.2#7 remains the only structural closure", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "EDGE_INCIDENCE", "count": 41, "component_ids": all_components, "note": "sum of edge-node incidences", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "MINIMAL_HULL_POSITION", "count": 40, "component_ids": all_components, "note": "sum of component hull sizes", "status": STATUS},
        {"dimension": "GRAPH_COUNT", "value": "RENDER_POSITION", "count": 40, "component_ids": all_components, "note": "sum of render-window sizes", "status": STATUS},
    ])
    write_tsv(TOPOLOGY_OUT, topology_rows, TOPOLOGY_FIELDS)

    packet = {
        "edge_id": "C020", "batch_id": "GDT707_V80", "page": "f8r", "physical_folio": "f8",
        "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE", "pivot_visual_id": "TOKEN_1_DCHEY_ACTION",
        "pivot_locus": "f8r.15@1", "target_visual_id": "TOKEN_2_4_MATERIAL_DRY_MIDDLE_RESULT_BUNDLE",
        "target_locus": "f8r.15@2-4", "relation_type": "WORKSHOP_ACTION_TO_THREE_ITEM_WRITTEN_RESULT",
        "direction_basis": "ACTION_THEN_MATERIAL_THEN_DRY_QUALITY_THEN_MIDDLE_DEGREE",
        "ownership_basis": "LOCAL_COMPLETE_BUNDLE_WITHOUT_PATIENT_IDENTITY_CLAIM", "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT707", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE", "source_aware_localizer": "GDT707_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "B_WORKING_LOCAL",
        "ambiguity_state": "WORKSHOP_ONLY", "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
    }
    write_tsv(PACKET_OUT, [packet], PACKET_FIELDS)
    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", rel(PACKET_OUT)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    assert intake_run.returncode == 1 and not intake_run.stderr
    assert json.loads(intake_run.stdout) == expected_intake
    INTAKE_OUT.write_text(json.dumps(expected_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bundle_ids_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    bundle_roles_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    bundle_decisions_by_pos: dict[tuple[str, int], set[str]] = defaultdict(set)
    for row in bundle_rows:
        locus, case_id, decision = str(row["locus"]), str(row["bundle_case_id"]), str(row["bundle_decision"])
        action_key = (locus, int(row["action_ordinal"]))
        bundle_ids_by_pos[action_key].add(case_id)
        bundle_roles_by_pos[action_key].add("SOURCE_ACTION")
        bundle_decisions_by_pos[action_key].add(decision)
        for rank, ordinal in enumerate(str(row["item_ordinals"]).split("|"), 1):
            key = (locus, int(ordinal))
            bundle_ids_by_pos[key].add(case_id)
            bundle_roles_by_pos[key].add(f"LEADING_ITEM_{rank}")
            bundle_decisions_by_pos[key].add(decision)
    bundle_roles_by_pos[("f8r.15", 2)].add("ADMITTED_RESULT_MATERIAL_CARRIER")
    bundle_roles_by_pos[("f8r.15", 3)].add("ADMITTED_RESULT_DRY_QUALITY")
    bundle_roles_by_pos[("f8r.15", 4)].add("ADMITTED_RESULT_MIDDLE_DEGREE")

    position_index = {(str(row["locus"]), int(row["token_ordinal"])): row for row in positions}
    token_overlay: list[dict[str, object]] = []
    for old in old_tokens:
        key = (old["locus"], int(old["token_ordinal"]))
        position = position_index.get(key)
        edges = str(position["edge_ids"]) if position else "NONE"
        token_overlay.append({
            **old, "v80_bundle_case_ids": pipe(sorted(bundle_ids_by_pos.get(key, set()))),
            "v80_bundle_roles": pipe(sorted(bundle_roles_by_pos.get(key, set()))),
            "v80_bundle_decisions": pipe(sorted(bundle_decisions_by_pos.get(key, set()))),
            "v80_component_id": position["component_id"] if position else "NONE",
            "v80_component_position": position["render_position"] if position else "NONE",
            "v80_component_role": position["component_role"] if position else "NONE",
            "v80_component_edge_ids": edges,
            "v80_component_membership_class": position["membership_class"] if position else "NONE",
            "v80_component_microrecord_de": position["component_microrecord_de"] if position else "NONE",
            "v80_new_three_item_result_edge_ids": "C020" if "C020" in edges.split("|") else "NONE",
            "v80_token_gloss_de": old["v79_token_gloss_de"], "v80_word_delta": 0, "v80_status": STATUS,
        })
    assert len(token_overlay) == 479
    assert all(new["v80_token_gloss_de"] == old["v79_token_gloss_de"] for new, old in zip(token_overlay, old_tokens))
    assert sum(row["v80_new_three_item_result_edge_ids"] == "C020" for row in token_overlay) == 2
    for ordinal in (2, 3):
        local = next(row for row in token_overlay if row["locus"] == "f8r.15" and row["token_ordinal"] == str(ordinal))
        assert local["v80_new_three_item_result_edge_ids"] == "NONE"
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA])

    bundles_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in bundle_rows:
        bundles_by_locus[str(row["locus"])].append(row)
    components_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in components:
        components_by_locus[str(row["locus"])].append(row)
    line_overlay: list[dict[str, object]] = []
    for old in old_lines:
        local_bundles = bundles_by_locus.get(old["locus"], [])
        local_components = components_by_locus.get(old["locus"], [])
        edge_ids = pipe([row["edge_ids"] for row in local_components])
        line_overlay.append({
            **old, "v80_bundle_case_ids": pipe([row["bundle_case_id"] for row in local_bundles]),
            "v80_bundle_decisions": pipe([row["bundle_decision"] for row in local_bundles]),
            "v80_component_ids": pipe([row["component_id"] for row in local_components]),
            "v80_edge_ids": edge_ids, "v80_component_topologies": pipe([row["topology"] for row in local_components]),
            "v80_component_microrecords_de": pipe([row["microrecord_de"] for row in local_components]),
            "v80_new_three_item_result_edge_ids": "C020" if "C020" in edge_ids.split("|") else "NONE",
            "v80_working_relation_reading_de": C020_READING if old["locus"] == "f8r.15" else "NONE",
            "v80_line_translation_de": old["v79_line_translation_de"], "v80_word_delta": 0,
            "v80_status": STATUS,
        })
    assert len(line_overlay) == 51
    assert all(new["v80_line_translation_de"] == old["v79_line_translation_de"] for new, old in zip(line_overlay, old_lines))
    assert sum(row["v80_new_three_item_result_edge_ids"] == "C020" for row in line_overlay) == 1
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA])

    span_overlay = [{
        **old, "v80_selected_gloss_de": old["v79_selected_gloss_de"], "v80_byte_identical": 1,
        "v80_relation_change": "NONE", "v80_status": STATUS,
    } for old in old_spans]
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA])

    reader = [
        "# GDT707 — V80 three-item result reader", "", f"Status: `{STATUS}`", "",
        "## Neue konkrete Lesung", "", f"> **C020 / f8r.15#1-4:** {C020_READING}", "",
        "Die Aktion bleibt wörtlich getrennt vom möglichen Ergebnisblock. Dadurch behauptet C020 weder, "
        "dass die namenlose Portion sicher derselbe Stoff wie `ckhol` ist, noch dass ein Abschluss erreicht wurde.", "",
        "## Warum das Bündel lokal funktioniert", "",
        "- `#2 ckhol` nennt den Materialträger: Drogenstoff aus Arzneikompositum.",
        "- `#3 chol` nennt den breiten Zustand: trocken.",
        "- `#4 chey` verengt genau diesen Zustand auf die Mitte des Grades.",
        "- In der lokalen Arbeitslesung bilden erst `#5 kc` (Charge/Wärme) und `#6 chy` (Reset auf Gradanfang) gemeinsam die rechte semantische Grenze; #5 allein ist noch kompatibel.", "",
        "## Vollständige Gegenprobe", "",
        "Alle 42 verzögerten Nominalfenster ergeben 119 semantische Dreierfolgen: 32 beginnen direkt nach "
        "einer Aktion, 87 beginnen später und dürfen nicht über frühere Items springen. Die 32 führenden "
        "Bündel ergeben 1 Aufnahme, 4 offene Lesarten und 27 Stopps. Zusätzlich sind alle neun `dchey`-Kontexte "
        "und alle zehn Vorkommen von `ckhol`, `chol` oder `chey` sichtbar. Nur A083 trägt die vollständige "
        "Material–trocken–Mitte-Folge.", "",
        "## Graph", "",
        "C020 bildet die neue Komponente M013. Nur #1 und #4 sind Knoten; #2 und #3 bleiben sichtbare "
        "hull-only Träger. Der kumulative Bestand hat 19 Kanten, 13 Komponenten, 35 eindeutige Knoten "
        "und 40 Renderpositionen. Wörter und alte Zeilenübersetzungen bleiben unverändert.", "",
    ]
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")
    (ART / "README.md").write_text(
        "# GDT707 artifacts\n\n"
        "- `V80_119_SEMANTIC_TRIPLE_UNIVERSE.tsv`: 32 leading plus 87 later-starting triples.\n"
        "- `V80_32_ACTION_ADJACENT_BUNDLE_CENSUS.tsv`: complete manual leading-bundle decisions.\n"
        "- `V80_10_TWO_ITEM_LENGTH_CONTROLS.tsv`: delayed windows too short for a triple.\n"
        "- `V80_9_DCHEY_ACTION_CONTEXTS.tsv`: one positive context plus eight same-action controls.\n"
        "- `V80_10_BUNDLE_SURFACE_OCCURRENCES.tsv`: three local bundle roles plus seven external ckhol/chol/chey controls.\n"
        "- `V80_1_NEW_MATERIAL_QUALITY_DEGREE_RESULT_EDGE.tsv`: occurrence-bound C020.\n"
        "- `V80_19_EDGE_COMPONENT_MEMBERSHIP.tsv`, `V80_13_CONNECTED_COMPONENTS.tsv`, and "
        "`V80_40_COMPONENT_POSITION_ROLES.tsv`: cumulative relation graph.\n"
        "- `V80_GDT388_EDGE_PACKET.tsv` and `V80_GDT388_EDGE_INTAKE.json`: explicit not-score-ready intake.\n"
        "- `V80_479_TOKEN_RELATION_OVERLAY.tsv`, `V80_51_LINE_RELATION_OVERLAY.tsv`, and "
        "`V80_3_BOUND_SPAN_FREEZE.tsv`: unchanged text with V80 relation metadata.\n"
        "- `GDT707_V80_THREE_ITEM_RESULT_READER.md`: compact practical reader.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    node_keys = {
        (str(row["locus"]), ordinal)
        for row in memberships for ordinal in str(row["edge_node_ordinals"]).split("|")
    }
    assert len(node_keys) == 35
    assert sum(len(str(row["edge_node_ordinals"]).split("|")) for row in memberships) == 41
    assert sum(int(row["edge_hull_position_count"]) for row in components) == 40
    assert sum(int(row["render_window_token_count"]) for row in components) == 40
    assert json.loads(G388.read_text(encoding="utf-8"))["acquisition"]["scoring_authorized"] is False

    generated = [
        TRIPLES_OUT, BUNDLES_OUT, SHORT_OUT, DCHEY_OUT, SURFACE_OUT, EDGE_OUT, MEMBERSHIP_OUT,
        COMPONENTS_OUT, POSITIONS_OUT, TOPOLOGY_OUT, PACKET_OUT, INTAKE_OUT, TOKENS_OUT, LINES_OUT,
        SPANS_OUT, READER_OUT, ART / "README.md",
    ]
    inputs = [
        G388, OLD_ACTIONS, OLD_PAIRS, OLD_RESULT, OLD_MEMBERSHIP, OLD_COMPONENTS, OLD_POSITIONS,
        OLD_TOKENS, OLD_LINES, OLD_SPANS, SPEC, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS, "question": QUESTION, "claim_ceiling": CLAIM,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "action_clauses": 83, "delayed_nominal_windows": 42,
            "semantic_triples": 119, "action_adjacent_leading_triples": 32,
            "later_starting_triple_controls": 87, "two_item_length_controls": 10,
            "new_admits": 1, "holds": 4, "stops": 27, "dchey_contexts": 9,
            "bundle_surface_occurrences": 10, "external_surface_controls": 7,
            "local_bundle_surface_roles": 3, "relation_edges_before": 18,
            "relation_edges_after": 19, "new_edges": 1, "connected_components": 13,
            "edge_nodes": 35, "edge_node_incidences": 41, "minimal_hull_positions": 40,
            "render_positions": 40, "shared_edge_nodes": 6, "hull_only_positions": 5,
            "render_only_structural_positions": 0, "structural_closure_positions": 1,
            "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "new_edge_ids": ["C020"], "c020": "f8r.15#1→f8r.15#4",
            "rendered_result_bundle": "f8r.15#2-4", "component": "M013",
            "intermediate_material_and_quality_are_edge_nodes": False,
            "held_bundle_cases": ["B006", "B007", "B012", "B018"],
            "immediate_a083_decision_preserved": "CONTROL_CONFLICT",
            "patient_identity_asserted": False, "completion_asserted": False,
            "portable_default": False, "new_word_meanings": 0,
        },
        "graph": {
            "component_partition": [
                ["C009"], ["C001", "C012"], ["C002"], ["C003"], ["C004", "C008"],
                ["C005"], ["C006", "C007", "C019"], ["C010"], ["C011", "C013", "C015"],
                ["C014"], ["C017"], ["C018"], ["C020"],
            ],
            "shared_nodes": ["f105v.1#4", "f26r.2#4", "f26r.2#6", "f80v.35#3", "f86v6.25#4", "f86v6.25#5"],
            "hull_only_positions": ["f26r.2#7", "f86v5.24#2", "f86v6.25#6", "f8r.15#2", "f8r.15#3"],
            "render_only_structural_positions": [], "structural_closure": "f26r.2#7",
        },
        "gdt388": expected_intake,
        "word_preservation": {
            "token_glosses_byte_identical": 479, "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3, "new_word_meanings": 0,
            "changed_word_meanings": 0, "content_word_additions": 0,
            "content_word_deletions": 0, "content_word_reorders": 0,
        },
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated}, "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": STATUS, "semantic_triples": 119, "leading_bundles": 32,
        "new_edge": "C020", "edges": 19, "components": 13, "edge_nodes": 35,
        "render_positions": 40, "new_word_meanings": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
