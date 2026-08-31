#!/usr/bin/env python3
"""Build the bounded V73 action-output/state-checkpoint carry experiment."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry"
SRC = EXP / "src"
ART = EXP / "artifacts"

STATUS = (
    "PASS_V73_10_ANA_WINDOWS__1_EXACT_STATE_ONLY_2_WORKING_STATE_LIKE_2_DEICTIC__"
    "1_UNIQUE_CANDIDATE_1_NEW_B_EDGE__C011_OCCURRENCE_BOUND__ZERO_WORD_DELTA"
)
QUESTION = (
    "Does the complete ten-case ACTION-to-one-token-NOMINAL-to-ACTION census "
    "support nominating one occurrence-bound B-tier hypothesis in which the "
    "result of f26r.2#4, whose written material patient is Krautdroge, remains "
    "the participant of deictic objectless #6 across exactly evidenced "
    "state-only #5, while the material-bearing f77v.7 countercase remains held?"
)
CLAIM_CEILING = (
    "V73 adds one occurrence-bound B-tier working hypothesis from f26r.2#4 "
    "ykecthey to #6 ytedy: the Krautdroge written as #4's material patient is "
    "hypothesized to persist as its action result across the exactly evidenced "
    "state-only checkpoint #5 chedy. No output label is written at #4. The "
    "checkpoint is not a donor or edge node; H002, the old whole-span H003, "
    "H004 and H005 remain unpromoted and no carry reaches #8. This is an "
    "exploratory German relation reading, not a portable carry rule, confirmed "
    "word meaning, plaintext, language, or externally grounded edge."
)
WORKING_MICRORECORD = (
    "Hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen "
    "[Quelle von ‚hiervon‘ offen]. [Zustandsvermerk ohne eigenen "
    "Materialträger: Mittlere Trockenstufe erreicht.] Die erhitzte Krautdroge "
    "bis zur Mittelstufe abkühlen und abschließen [C011-Arbeitshypothese]."
)
NEXT_GAP = (
    "Keep C011 occurrence-bound. Next compile the eleven cumulative relation "
    "edges into their exact connected components and practical microrecords, "
    "treating f26r.2#5 as hull-only rather than an edge node. Preserve C010, "
    "all prior boundaries and every held rival; add no edge or word meaning."
)

SPEC = SRC / "V73_10_ANA_CENSUS_SPEC.tsv"
G388_RESULT = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G687_DISPATCH = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv"
G695_CLAUSES = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G696_RIVALS = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_17_RELATION_RIVALS.tsv"
G696_REFS = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_27_REFERENCE_CENSUS.tsv"
G696_EDGES = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_9_LOCAL_ACTION_EDGES.tsv"
G697_COVERAGE = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv"
G699_RESULT = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/RESULT.json"
G699_EDGE = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_1_NEW_LOCAL_HEAT_EDGE.tsv"
G699_TOKENS = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_479_TOKEN_RELATION_OVERLAY.tsv"
G699_LINES = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_51_LINE_RELATION_OVERLAY.tsv"
G699_SPANS = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_3_BOUND_SPAN_FREEZE.tsv"

CENSUS_OUT = ART / "V73_10_ANA_CENSUS.tsv"
CONTRAST_OUT = ART / "V73_2_DEICTIC_ANA_CONTRASTS.tsv"
EDGE_OUT = ART / "V73_1_NEW_LOCAL_CHECKPOINT_EDGE.tsv"
CONTROLS_OUT = ART / "V73_4_C011_BOUNDARY_CONTROLS.tsv"
REGISTER_OUT = ART / "V73_11_RELATION_EDGE_REGISTER.tsv"
PACKET_OUT = ART / "V73_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V73_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V73_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V73_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V73_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT700_V73_STATE_CHECKPOINT_CARRY_READER.md"
ARTIFACT_README = ART / "README.md"
RESULT_OUT = ART / "RESULT.json"

SPEC_FIELDS = [
    "window_id", "locus", "source_start_ordinal", "source_end_ordinal",
    "source_surfaces", "source_verb_lemmas", "source_working_de",
    "checkpoint_ordinal", "checkpoint_surface", "checkpoint_working_de",
    "checkpoint_class", "target_start_ordinal", "target_end_ordinal",
    "target_surfaces", "target_verb_lemmas", "target_working_de",
    "target_reference_class", "source_material_class",
    "competing_checkpoint_material", "expected_decision", "rationale_de",
    "forbidden_inference",
]
CENSUS_FIELDS = [
    *SPEC_FIELDS, "page", "source_clause_id", "source_clause_type",
    "checkpoint_clause_id", "checkpoint_clause_type", "checkpoint_token_positions",
    "checkpoint_verb_occurrences", "target_clause_id", "target_clause_type",
    "exact_state_only_checkpoint", "working_state_like_checkpoint",
    "deictic_target", "written_source_material",
    "unique_signature_match", "word_meaning_delta", "status",
]
CONTRAST_FIELDS = [
    "contrast_id", "window_id", "locus", "source_ordinals", "source_surfaces",
    "source_material_role", "checkpoint_ordinal", "checkpoint_surface",
    "checkpoint_role", "target_ordinals", "target_surfaces", "target_role",
    "prior_rival_ids", "decision", "reason_de", "forbidden_inference", "status",
]
EDGE_FIELDS = [
    "edge_id", "locus", "support_tier", "relation_class", "topology",
    "window_hull_ordinals", "edge_node_ordinals", "source_ordinals",
    "checkpoint_ordinals", "target_action_ordinal", "structural_closure_ordinals",
    "excluded_ordinals", "source_surface", "checkpoint_surface", "target_surface",
    "source_action_gloss_de", "source_output_label_de", "checkpoint_gloss_de",
    "target_action_gloss_de", "prototype_edge_id", "nonadjacent_b_precedent_edge_id",
    "prior_rival_id", "prior_rival_source_ordinals", "selection_basis",
    "working_microrecord_de", "unresolved_reference", "portability",
    "gdt388_score_ready", "final_result_status", "v72_word_delta", "status",
]
CONTROL_FIELDS = [
    "control_id", "locus", "token_ordinal", "surface", "control_role",
    "edge_membership", "decision", "reason_de", "forbidden_inference", "status",
]
REGISTER_FIELDS = [
    "edge_id", "locus", "source_ordinals", "target_action_ordinal",
    "support_tier", "relation_class", "origin", "portability", "v73_change", "status",
]
TOKEN_EXTRA_FIELDS = [
    "v73_ana_window_ids", "v73_relation_roles", "v73_new_edge_ids",
    "v73_checkpoint_class", "v73_reference_decision", "v73_token_gloss_de",
    "v73_word_delta", "v73_status",
]
LINE_EXTRA_FIELDS = [
    "v73_ana_window_ids", "v73_new_checkpoint_edge_ids", "v73_held_ana_controls",
    "v73_relation_annotations_de", "v73_working_microrecord_de",
    "v73_clause_translation_de", "v73_word_delta", "v73_status",
]
SPAN_EXTRA_FIELDS = [
    "v73_selected_gloss_de", "v73_byte_identical", "v73_relation_change", "v73_status",
]
PACKET_FIELDS = [
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
]


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def guarded_query(
    path: Path, *, selector: str, allowed: Iterable[str], columns: Sequence[str],
) -> list[dict[str, str]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", selector, "--columns", ",".join(columns),
        "--forbid-prefix", "f84",
    ]
    for value in sorted(set(allowed)):
        command.extend(["--allow", value])
    completed = subprocess.run(
        command, cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.stderr and "GUARD_STATS" not in completed.stderr:
        raise AssertionError(completed.stderr)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if rows and list(rows[0]) != list(columns):
        raise AssertionError(f"guarded column mismatch for {path}")
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"expected one row for {wanted}, found {len(hits)}")
    return hits[0]


def edge_number(edge_id: str) -> int:
    return int(edge_id[1:])


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    spec_fields, specs = read_tsv(SPEC)
    assert spec_fields == SPEC_FIELDS
    assert [row["window_id"] for row in specs] == [f"V73A{i:03d}" for i in range(1, 11)]
    assert len({row["locus"] for row in specs}) == 9
    assert sum(row["checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT" for row in specs) == 1
    assert sum(row["checkpoint_class"] == "WORKING_STATE_LIKE_NO_MATERIAL_HEAD" for row in specs) == 2
    assert sum(row["target_reference_class"] == "DEICTIC_OBJECTLESS" for row in specs) == 2
    assert sum(row["expected_decision"] == "ADMIT_C011_OCCURRENCE_BOUND" for row in specs) == 1

    g388 = json.loads(G388_RESULT.read_text(encoding="utf-8"))
    assert g388["status"] == "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES"
    assert g388["acquisition"]["minimum_edges"] == 50
    assert g388["acquisition"]["minimum_physical_folios"] == 5
    assert g388["acquisition"]["scoring_authorized"] is False

    prior = json.loads(G699_RESULT.read_text(encoding="utf-8"))
    assert prior["status"].startswith("PASS_V72_")
    assert prior["basis"] == {
        "bound_spans": 3, "current_yka_action_occurrences": 3,
        "f84_access": 0, "f84r_access": 0, "heat_reference_cases": 5,
        "lines": 51, "new_pages": 0, "pages": 36, "token_positions": 479,
    }
    assert prior["decisions"]["new_edge_id"] == "C010"
    assert prior["decisions"]["excluded_from_edge"] == "f86v5.24#2"

    token_fields, token_rows = read_tsv(G699_TOKENS)
    line_fields, line_rows = read_tsv(G699_LINES)
    span_fields, span_rows = read_tsv(G699_SPANS)
    assert len(token_rows) == 479 and len(line_rows) == 51 and len(span_rows) == 3
    assert len({row["page"] for row in token_rows}) == 36
    assert all(not row["page"].lower().startswith("f84") for row in token_rows + line_rows)
    assert all(not row["locus"].lower().startswith("f84") for row in span_rows)
    assert all(row["v72_word_delta"] == "0" for row in token_rows + line_rows)
    assert all(row["v72_byte_identical"] == "1" for row in span_rows)

    # The census must be reconstructed from the complete inherited 51-line
    # scope, not merely replayed at the nine loci named by the specification.
    # The already f84-free V72 line projection supplies the explicit selector
    # allow-list required by query-tsv.
    loci = {row["locus"] for row in line_rows}
    assert len(loci) == 51
    clause_columns = [
        "page", "locus", "clause_id", "clause_type", "start_ordinal",
        "end_ordinal", "token_positions", "semantic_units", "surfaces",
        "action_ordinals", "verb_lemmas", "binding_ids", "v68_clause_de",
        "realization_rule", "verb_occurrences", "content_word_delta",
    ]
    clauses = guarded_query(
        G695_CLAUSES, selector="locus", allowed=loci, columns=clause_columns,
    )
    assert len(clauses) == 175
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_locus[row["locus"]].append(row)
    observed_windows: list[tuple[dict[str, str], dict[str, str], dict[str, str]]] = []
    for locus in sorted(by_locus):
        ordered = sorted(by_locus[locus], key=lambda row: int(row["clause_id"]))
        for source, checkpoint, target in zip(ordered, ordered[1:], ordered[2:]):
            if (
                source["clause_type"] == "ACTION_CLAUSE"
                and checkpoint["clause_type"] == "NOMINAL_BLOCK"
                and checkpoint["start_ordinal"] == checkpoint["end_ordinal"]
                and target["clause_type"] == "ACTION_CLAUSE"
            ):
                observed_windows.append((source, checkpoint, target))
    assert len(observed_windows) == 10
    observed_windows.sort(key=lambda triple: (triple[0]["locus"], int(triple[0]["start_ordinal"])))
    assert [(a["locus"], a["start_ordinal"], n["start_ordinal"], b["start_ordinal"]) for a, n, b in observed_windows] == [
        (row["locus"], row["source_start_ordinal"], row["checkpoint_ordinal"], row["target_start_ordinal"])
        for row in specs
    ]

    census_rows: list[dict[str, object]] = []
    for spec, (source, checkpoint, target) in zip(specs, observed_windows):
        assert source["end_ordinal"] == spec["source_end_ordinal"]
        assert source["surfaces"] == spec["source_surfaces"]
        assert source["verb_lemmas"] == spec["source_verb_lemmas"]
        assert source["v68_clause_de"] == spec["source_working_de"]
        assert checkpoint["surfaces"] == spec["checkpoint_surface"]
        assert checkpoint["v68_clause_de"] == spec["checkpoint_working_de"]
        assert checkpoint["verb_lemmas"] == "NONE"
        assert checkpoint["verb_occurrences"] == "0"
        assert target["end_ordinal"] == spec["target_end_ordinal"]
        assert target["surfaces"] == spec["target_surfaces"]
        assert target["verb_lemmas"] == spec["target_verb_lemmas"]
        assert target["v68_clause_de"] == spec["target_working_de"]
        exact_state_only = int(spec["checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT")
        working_state_like = int(spec["checkpoint_class"] == "WORKING_STATE_LIKE_NO_MATERIAL_HEAD")
        deictic = int(spec["target_reference_class"] == "DEICTIC_OBJECTLESS")
        written_material = int(spec["source_material_class"] == "WRITTEN_MATERIAL_IN_ACTION")
        unique = int(exact_state_only == deictic == written_material == 1)
        assert unique == int(spec["expected_decision"] == "ADMIT_C011_OCCURRENCE_BOUND")
        census_rows.append({
            **spec,
            "page": source["page"],
            "source_clause_id": source["clause_id"],
            "source_clause_type": source["clause_type"],
            "checkpoint_clause_id": checkpoint["clause_id"],
            "checkpoint_clause_type": checkpoint["clause_type"],
            "checkpoint_token_positions": checkpoint["token_positions"],
            "checkpoint_verb_occurrences": int(checkpoint["verb_occurrences"]),
            "target_clause_id": target["clause_id"],
            "target_clause_type": target["clause_type"],
            "exact_state_only_checkpoint": exact_state_only,
            "working_state_like_checkpoint": working_state_like,
            "deictic_target": deictic,
            "written_source_material": written_material,
            "unique_signature_match": unique,
            "word_meaning_delta": 0,
            "status": STATUS,
        })
    write_tsv(CENSUS_OUT, census_rows, CENSUS_FIELDS)

    dispatch_columns = [
        "page", "locus", "ordinal", "surface", "action_licensed_before",
        "dispatch_class", "v60_literal_gloss_de", "dy_contribution", "confidence",
        "left_surface", "right_surface", "reader_support",
        "mechanical_flags_before", "mechanical_flags_after",
        "specificity_open_before", "specificity_open_after",
    ]
    dispatch = guarded_query(
        G687_DISPATCH, selector="locus", allowed={"f26r.2", "f77v.7"},
        columns=dispatch_columns,
    )
    chedy = one(dispatch, locus="f26r.2", ordinal="5", surface="chedy")
    ytedy = one(dispatch, locus="f26r.2", ordinal="6", surface="ytedy")
    dy = one(dispatch, locus="f26r.2", ordinal="7", surface="dy")
    ycheedy = one(dispatch, locus="f77v.7", ordinal="5", surface="ycheedy")
    assert chedy["dispatch_class"] == "NOMINAL_FINISHED_RESULT_STATE"
    assert chedy["action_licensed_before"] == "0" and chedy["v60_literal_gloss_de"] == "fertige mittlere Trockenstufe"
    assert chedy["mechanical_flags_before"] == chedy["mechanical_flags_after"] == "STATE_ONLY_NO_OBJECT"
    assert chedy["specificity_open_before"] == chedy["specificity_open_after"] == "1"
    assert ytedy["dispatch_class"] == ycheedy["dispatch_class"] == "ACTION_WHOLE_WITH_FINISHED_ENDPOINT"
    assert ytedy["action_licensed_before"] == ycheedy["action_licensed_before"] == "1"
    assert dy["dispatch_class"] == "CLAUSE_STOP" and dy["action_licensed_before"] == "0"

    rival_columns = [
        "rival_id", "rival_kind", "locus", "source_ordinals",
        "target_action_ordinal", "expected_source_surfaces",
        "expected_target_surface", "plausible_reading_de", "rejection_reason",
        "source_target_join_exact", "decision",
    ]
    rivals = guarded_query(
        G696_RIVALS, selector="locus", allowed={"f26r.2", "f77v.7"},
        columns=rival_columns,
    )
    assert {row["rival_id"] for row in rivals} == {"H002", "H003", "H004", "H005"}
    assert all(row["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED" for row in rivals)
    h002 = one(rivals, rival_id="H002")
    h003 = one(rivals, rival_id="H003")
    h004 = one(rivals, rival_id="H004")
    h005 = one(rivals, rival_id="H005")
    assert h002["source_ordinals"] == "3" and h002["target_action_ordinal"] == "4"
    assert h003["source_ordinals"] == "4-5" and h003["target_action_ordinal"] == "6"
    assert h004["target_action_ordinal"] == "3" and h005["source_ordinals"] == "4"

    reference_columns = [
        "reference_id", "locus", "reference_ordinal", "expected_surface",
        "expected_gloss_de", "decision", "linked_edge_ids", "source_ordinals",
        "target_ordinals", "scope_class", "provenance", "note",
    ]
    references = guarded_query(
        G696_REFS, selector="locus", allowed={"f26r.2", "f77v.7"},
        columns=reference_columns,
    )
    assert {row["reference_id"] for row in references} == {"R012", "R013", "R016", "R017"}
    assert all(row["decision"] == "HOLD_OBJECT_RIVAL" and row["linked_edge_ids"] == "NONE" for row in references)
    assert one(references, reference_id="R013")["source_ordinals"] == "4-5"
    assert one(references, reference_id="R017")["source_ordinals"] == "4"

    local_edge_columns = [
        "edge_id", "locus", "source_start_ordinal", "source_end_ordinal",
        "left_role_map", "target_action_ordinal", "relation_class", "support_tier",
        "expected_source_surfaces", "expected_target_surface", "relation_explicit_de",
        "license_basis", "rival_control", "edge_status",
    ]
    local_edges = guarded_query(
        G696_EDGES, selector="locus", allowed={"f80v.35", "f86v6.25"},
        columns=local_edge_columns,
    )
    c006 = one(local_edges, edge_id="C006")
    c008 = one(local_edges, edge_id="C008")
    assert c006["left_role_map"] == "4:DONOR_ACTION_OUTPUT"
    assert c006["relation_class"] == "MEASURED_SHARE_OUTPUT_CARRY"
    assert c006["support_tier"] == "A_MINUS_EXPLICIT_OUTPUT"
    assert c008["left_role_map"] == "3:DESTINATION"
    assert c008["support_tier"] == "B_WORKING_LOCAL"

    coverage_columns = [
        "edge_id", "microrecord_id", "locus", "support_tier", "relation_class",
        "source_ordinals", "target_action_ordinal", "topology",
        "edge_role_in_window", "shared_node_ordinals", "covered_once", "status",
    ]
    coverage = guarded_query(
        G697_COVERAGE, selector="locus",
        allowed={"f104v.2", "f105v.1", "f113v.17", "f75r.3", "f77r.38", "f80v.35", "f86v6.25"},
        columns=coverage_columns,
    )
    assert sorted((row["edge_id"] for row in coverage), key=edge_number) == [f"C{i:03d}" for i in range(1, 10)]
    assert all(row["covered_once"] == "1" for row in coverage)
    assert one(coverage, edge_id="C006")["topology"] == "SERIAL_ACTION_OUTPUT_CHAIN"

    _, c010_rows = read_tsv(G699_EDGE)
    c010 = one(c010_rows, edge_id="C010")
    assert c010["source_ordinals"] == "1" and c010["target_action_ordinal"] == "3"
    assert c010["excluded_ordinals"] == "2" and c010["portability"] == "OCCURRENCE_BOUND_ONLY"

    contrast_rows = [
        {
            "contrast_id": "D001", "window_id": "V73A004", "locus": "f26r.2",
            "source_ordinals": "4", "source_surfaces": "ykecthey",
            "source_material_role": "INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:Krautdroge",
            "checkpoint_ordinal": "5", "checkpoint_surface": "chedy",
            "checkpoint_role": "STATE_ONLY_CHECKPOINT_NOT_EDGE_NODE",
            "target_ordinals": "6-7", "target_surfaces": "ytedy|dy",
            "target_role": "DEICTIC_OBJECTLESS_TARGET_ACTION",
            "prior_rival_ids": "H002|H003", "decision": "ADMIT_C011_OCCURRENCE_BOUND",
            "reason_de": "Einziger Zehner-Census-Fall mit geschriebenem Materialpatienten in der Ausgangsaktion, exakt belegtem objektlosen Ergebniszustand und deiktischer objektloser Zielaktion; dies selektiert eine B-Hypothese, beweist sie aber nicht.",
            "forbidden_inference": "H002 und der alte H003-Gesamtspan bleiben unpromoviert; #5 ist kein Donor oder Edge-Knoten; keine Fortsetzung zu #8.",
            "status": STATUS,
        },
        {
            "contrast_id": "D002", "window_id": "V73A008", "locus": "f77v.7",
            "source_ordinals": "3", "source_surfaces": "qy",
            "source_material_role": "UNRESOLVED_REFERENCE_OUTPUT",
            "checkpoint_ordinal": "4", "checkpoint_surface": "rr",
            "checkpoint_role": "COMPETING_WRITTEN_MATERIAL:getrocknete_Wurzel",
            "target_ordinals": "5", "target_surfaces": "ycheedy",
            "target_role": "DEICTIC_OBJECTLESS_TARGET_ACTION",
            "prior_rival_ids": "H004|H005", "decision": "KEEP_HELD_MATERIAL_COMPETITOR",
            "reason_de": "RR ist ein sichtbarer Materialdonor und schon QY besitzt keine eindeutige Quelle; A-N-A-Geometrie wählt keinen Teilnehmer.",
            "forbidden_inference": "Weder RR noch einen hypothetischen QY-Ausgang an YCHEEDY binden.",
            "status": STATUS,
        },
    ]
    write_tsv(CONTRAST_OUT, contrast_rows, CONTRAST_FIELDS)

    edge_row = {
        "edge_id": "C011", "locus": "f26r.2", "support_tier": "B_WORKING_LOCAL",
        "relation_class": "ACTION_OUTPUT_ACROSS_ONE_STATE_CHECKPOINT",
        "topology": "SINGLE_ACTION_OUTPUT_CARRY_ACROSS_ONE_STATE_ONLY_CHECKPOINT",
        "window_hull_ordinals": "4-6", "edge_node_ordinals": "4|6",
        "source_ordinals": "4", "checkpoint_ordinals": "5",
        "target_action_ordinal": "6", "structural_closure_ordinals": "7",
        "excluded_ordinals": "3|5|8", "source_surface": "ykecthey",
        "checkpoint_surface": "chedy", "target_surface": "ytedy",
        "source_action_gloss_de": "hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen",
        "source_output_label_de": "C011-Hypothese: die erhitzte Krautdroge",
        "checkpoint_gloss_de": "mittlere Trockenstufe erreicht",
        "target_action_gloss_de": "hiervon bis zur Mittelstufe abkühlen und abschließen",
        "prototype_edge_id": "C006", "nonadjacent_b_precedent_edge_id": "C008",
        "prior_rival_id": "H003", "prior_rival_source_ordinals": "4-5",
        "selection_basis": "UNIQUE_10_WINDOW_B_NOMINATION_WRITTEN_SOURCE_PATIENT_PLUS_EXACT_STATE_ONLY_CHECKPOINT_PLUS_DEICTIC_OBJECTLESS_TARGET",
        "working_microrecord_de": WORKING_MICRORECORD,
        "unresolved_reference": "f26r.2#4:FIRST_HIERVON_UNBOUND",
        "portability": "OCCURRENCE_BOUND_ONLY", "gdt388_score_ready": 0,
        "final_result_status": "UNNAMED_NO_OUTGOING_EDGE",
        "v72_word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [edge_row], EDGE_FIELDS)

    controls = [
        {
            "control_id": "B001", "locus": "f26r.2", "token_ordinal": 3,
            "surface": "adeeody", "control_role": "HELD_UPSTREAM_SOURCE:H002",
            "edge_membership": "NONE", "decision": "KEEP_H002_HELD",
            "reason_de": "Das erste hiervon in #4 bleibt ohne zugelassene Quelle.",
            "forbidden_inference": "Nicht aus dem gleichen abgemessenen Teil oder aus der fertigen Zubereitung lesen.", "status": STATUS,
        },
        {
            "control_id": "B002", "locus": "f26r.2", "token_ordinal": 5,
            "surface": "chedy", "control_role": "STATE_ONLY_CHECKPOINT:C011",
            "edge_membership": "HULL_ONLY_NOT_NODE", "decision": "EXCLUDE_FROM_C011_SOURCE_AND_DONOR",
            "reason_de": "Ein-Token-Nominalblock ohne Verb oder Materialkopf; nur Zustandscheckpoint.",
            "forbidden_inference": "Nicht als Trocknungsaktion, Materialdonor oder Teil der Quellspanne lesen.", "status": STATUS,
        },
        {
            "control_id": "B003", "locus": "f26r.2", "token_ordinal": 7,
            "surface": "dy", "control_role": "STRUCTURAL_CLAUSE_STOP",
            "edge_membership": "NONE", "decision": "KEEP_STRUCTURAL_ONLY",
            "reason_de": "Freies DY markiert hier nur den strukturellen Klauselstopp und ist keine Aktion oder Teilnehmerquelle.",
            "forbidden_inference": "Kein eigenes Schließen oder weiterer Carry-Knoten.", "status": STATUS,
        },
        {
            "control_id": "B004", "locus": "f26r.2", "token_ordinal": 8,
            "surface": "checthedy", "control_role": "NEW_ACTION_WITH_WRITTEN_KRAUTDROGE",
            "edge_membership": "NONE", "decision": "STOP_C011_BEFORE_ORDINAL_8",
            "reason_de": "Die neue Aktionsklausel schreibt ihr eigenes Materialobjekt Krautdroge; es gibt keine Identitätskante von #6.",
            "forbidden_inference": "Nicht die abgekühlte Krautdroge anschließend weiter trocknen; auch keine neue Krautdroge behaupten.", "status": STATUS,
        },
    ]
    write_tsv(CONTROLS_OUT, controls, CONTROL_FIELDS)

    register_rows: list[dict[str, object]] = []
    for row in sorted(coverage, key=lambda item: edge_number(item["edge_id"])):
        register_rows.append({
            "edge_id": row["edge_id"], "locus": row["locus"],
            "source_ordinals": row["source_ordinals"],
            "target_action_ordinal": row["target_action_ordinal"],
            "support_tier": row["support_tier"], "relation_class": row["relation_class"],
            "origin": "GDT697_INHERITED", "portability": "INHERITED_OCCURRENCE_BOUND",
            "v73_change": "NONE", "status": STATUS,
        })
    register_rows.append({
        "edge_id": "C010", "locus": c010["locus"],
        "source_ordinals": c010["source_ordinals"],
        "target_action_ordinal": c010["target_action_ordinal"],
        "support_tier": c010["support_tier"], "relation_class": c010["relation_class"],
        "origin": "GDT699_INHERITED", "portability": c010["portability"],
        "v73_change": "NONE", "status": STATUS,
    })
    register_rows.append({
        "edge_id": "C011", "locus": "f26r.2", "source_ordinals": "4",
        "target_action_ordinal": "6", "support_tier": "B_WORKING_LOCAL",
        "relation_class": "ACTION_OUTPUT_ACROSS_ONE_STATE_CHECKPOINT",
        "origin": "NEW_GDT700", "portability": "OCCURRENCE_BOUND_ONLY",
        "v73_change": "ADD_ONE_EDGE", "status": STATUS,
    })
    assert [row["edge_id"] for row in register_rows] == [f"C{i:03d}" for i in range(1, 12)]
    write_tsv(REGISTER_OUT, register_rows, REGISTER_FIELDS)

    packet_row = {
        "edge_id": "C011", "batch_id": "GDT700_V73", "page": "f26r",
        "physical_folio": "f26", "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE",
        "pivot_visual_id": "TOKEN_4_YKECTHEY_OUTPUT", "pivot_locus": "f26r.2@4",
        "target_visual_id": "TOKEN_6_YTEDY", "target_locus": "f26r.2@6",
        "relation_type": "WORKSHOP_ACTION_OUTPUT_CARRY",
        "direction_basis": "FORMAL_ANA_CENSUS_UNIQUE_SIGNATURE",
        "ownership_basis": "WRITTEN_SOURCE_MATERIAL_ACROSS_STATE_ONLY_CHECKPOINT",
        "geometry_only_selection": "FALSE", "source_manifest_id": "GDT700",
        "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE", "source_aware_localizer": "GDT700_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "B_WORKING_LOCAL",
        "ambiguity_state": "WORKSHOP_ONLY", "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
    }
    write_tsv(PACKET_OUT, [packet_row], PACKET_FIELDS)
    intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", rel(PACKET_OUT)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert intake.returncode == 1 and not intake.stderr
    intake_payload = json.loads(intake.stdout)
    assert intake_payload == {
        "status": "INVALID_PACKET", "packet_rows": 1, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": ["edge row 2: formal access is not sealed"],
    }
    INTAKE_OUT.write_text(json.dumps(intake_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    window_ids_by_position: dict[tuple[str, int], set[str]] = defaultdict(set)
    for spec in specs:
        for ordinal in range(int(spec["source_start_ordinal"]), int(spec["target_end_ordinal"]) + 1):
            window_ids_by_position[(spec["locus"], ordinal)].add(spec["window_id"])

    special = {
        ("f26r.2", 3): ("EXCLUDED_UPSTREAM_SOURCE:H002", "NONE", "NONE", "KEEP_H002_HELD"),
        ("f26r.2", 4): ("INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:C011", "C011", "NONE", "ADMIT_C011_OCCURRENCE_BOUND"),
        ("f26r.2", 5): ("STATE_ONLY_CHECKPOINT:C011", "NONE", "EXACT_STATE_ONLY_RESULT_CHECKPOINT", "EXCLUDE_FROM_C011_SOURCE_AND_DONOR"),
        ("f26r.2", 6): ("REFERENCE:C011|TARGET_ACTION:C011", "C011", "NONE", "ADMIT_C011_OCCURRENCE_BOUND"),
        ("f26r.2", 7): ("STRUCTURAL_CLAUSE_STOP:C011", "NONE", "NONE", "KEEP_STRUCTURAL_ONLY"),
        ("f26r.2", 8): ("CARRY_STOP_WRITTEN_OBJECT", "NONE", "NONE", "STOP_C011_BEFORE_ORDINAL_8"),
    }
    token_overlay: list[dict[str, object]] = []
    for row in token_rows:
        position = (row["locus"], int(row["token_ordinal"]))
        roles, edge_ids, checkpoint_class, decision = special.get(position, ("NONE", "NONE", "NONE", "NONE"))
        token_overlay.append({
            **row,
            "v73_ana_window_ids": "|".join(sorted(window_ids_by_position.get(position, set()))) or "NONE",
            "v73_relation_roles": roles,
            "v73_new_edge_ids": edge_ids,
            "v73_checkpoint_class": checkpoint_class,
            "v73_reference_decision": decision,
            "v73_token_gloss_de": row["v72_token_gloss_de"],
            "v73_word_delta": 0,
            "v73_status": STATUS,
        })
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA_FIELDS])

    specs_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        specs_by_locus[spec["locus"]].append(spec)
    line_overlay: list[dict[str, object]] = []
    for row in line_rows:
        local = specs_by_locus.get(row["locus"], [])
        annotations = " | ".join(item["rationale_de"] for item in local) or "NONE"
        held = "NONE"
        if row["locus"] == "f26r.2":
            held = "H002|H003_WHOLE_BLOCK_SUPERSEDED_NOT_PROMOTED"
        elif row["locus"] == "f77v.7":
            held = "H004|H005"
        line_overlay.append({
            **row,
            "v73_ana_window_ids": "|".join(item["window_id"] for item in local) or "NONE",
            "v73_new_checkpoint_edge_ids": "C011" if row["locus"] == "f26r.2" else "NONE",
            "v73_held_ana_controls": held,
            "v73_relation_annotations_de": annotations,
            "v73_working_microrecord_de": WORKING_MICRORECORD if row["locus"] == "f26r.2" else "NONE",
            "v73_clause_translation_de": row["v72_clause_translation_de"],
            "v73_word_delta": 0,
            "v73_status": STATUS,
        })
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA_FIELDS])

    span_overlay = [
        {
            **row,
            "v73_selected_gloss_de": row["v72_selected_gloss_de"],
            "v73_byte_identical": 1,
            "v73_relation_change": "NONE",
            "v73_status": STATUS,
        }
        for row in span_rows
    ]
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA_FIELDS])

    reader = [
        "# GDT700 — V73 action output across one state checkpoint", "",
        f"Status: `{STATUS}`", "", "## Concrete new microrecord", "",
        "Surface window: `ykecthey chedy ytedy dy`", "",
        f"> {WORKING_MICRORECORD}", "",
        "C011 is only the B-hypothesis `ykecthey#4 INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT(Krautdroge) → ytedy#6`; no output label is written at #4. "
        "The intervening `chedy#5` is hull-only and never an edge node. The first "
        "reference inside #4 remains unresolved, and C011 stops before #8.", "",
        "## Complete ten-window census", "",
        "| ID | locus | source | checkpoint | target | checkpoint class | target class | decision |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in census_rows:
        reader.append(
            f"| {row['window_id']} | `{row['locus']}` | `{row['source_surfaces']}` | "
            f"`{row['checkpoint_surface']}` | `{row['target_surfaces']}` | "
            f"{row['checkpoint_class']} | {row['target_reference_class']} | {row['expected_decision']} |"
        )
    reader.extend([
        "", "## Decisive countercase", "",
        "At `f77v.7`, `qy#3 → rr#4 → ycheedy#5` has the same broad A–N–A "
        "geometry, but `rr` is the written material *getrocknete Wurzel*. H004 "
        "and H005 therefore remain held; neither possible participant is selected.", "",
        "## Boundaries", "",
        "- 1 exactly evidenced state-only checkpoint, 2 working state-like blocks, 7 material-bearing checkpoints and 2 deictic targets occur in the ten windows.",
        "- Among the two deictic targets, only f26r.2 has a written material patient in the source action and no material-bearing middle competitor; this nominates one B-tier occurrence hypothesis, not a grammar default or verified identity.",
        "- C006 is only the action-output role prototype. It has no intervening checkpoint, so C011 is not a GDT697 serial chain replay.",
        "- C008 is only a nonadjacent B-tier precedent, not the same topology as C011.",
        "- The GDT388 packet remains invalid/not score-ready because the edge was selected with formal access and has no external capacity, holdout or mobile null.",
        "- All 479 token glosses, 51 inherited line readings and 3 bound spans remain byte-identical; no word meaning is added.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")

    ARTIFACT_README.write_text(
        "# GDT700 artifacts\n\n"
        "- `V73_10_ANA_CENSUS.tsv`: exhaustive action–one-token nominal–action census.\n"
        "- `V73_2_DEICTIC_ANA_CONTRASTS.tsv`: admitted f26r signature versus held f77v material competitor.\n"
        "- `V73_1_NEW_LOCAL_CHECKPOINT_EDGE.tsv`: C011, only #4 to #6; #5 is hull-only.\n"
        "- `V73_4_C011_BOUNDARY_CONTROLS.tsv`: #3/#5/#7/#8 non-edge roles and stop conditions.\n"
        "- `V73_11_RELATION_EDGE_REGISTER.tsv`: nine V70 edges, inherited C010 and new C011.\n"
        "- `V73_GDT388_EDGE_PACKET.tsv` and `V73_GDT388_EDGE_INTAKE.json`: explicit not-score-ready audit.\n"
        "- `V73_479_TOKEN_RELATION_OVERLAY.tsv`, `V73_51_LINE_RELATION_OVERLAY.tsv`, `V73_3_BOUND_SPAN_FREEZE.tsv`: unchanged V72 reader plus separate V73 metadata.\n"
        "- `GDT700_V73_STATE_CHECKPOINT_CARRY_READER.md`: concrete microrecord and full census.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    generated = [
        CENSUS_OUT, CONTRAST_OUT, EDGE_OUT, CONTROLS_OUT, REGISTER_OUT,
        PACKET_OUT, INTAKE_OUT, TOKENS_OUT, LINES_OUT, SPANS_OUT,
        READER_OUT, ARTIFACT_README,
    ]
    inputs = [
        SPEC, G388_RESULT, G687_DISPATCH, G695_CLAUSES, G696_RIVALS,
        G696_REFS, G696_EDGES, G697_COVERAGE, G699_RESULT, G699_EDGE, G699_TOKENS,
        G699_LINES, G699_SPANS, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS,
        "question": QUESTION,
        "claim_ceiling": CLAIM_CEILING,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479,
            "lines": 51, "census_loci": 51, "source_clauses": 175,
            "bound_spans": 3, "ana_windows": 10,
            "exact_state_only_checkpoints": 1,
            "working_state_like_checkpoints": 2,
            "material_bearing_checkpoints": 7,
            "deictic_targets": 2, "f84_access": 0, "f84r_access": 0,
        },
        "decision": {
            "census_exclusions": 9,
            "unique_signature_matches": 1,
            "new_occurrence_bound_edges": 1,
            "new_edge_id": "C011",
            "new_edge_source": "f26r.2#4",
            "new_edge_checkpoint_hull_only": "f26r.2#5",
            "new_edge_target": "f26r.2#6",
            "excluded_ordinals": [3, 5, 8],
            "structural_closure_ordinal": 7,
            "held_deictic_countercase": "f77v.7#3-5",
            "cumulative_relation_edges": 11,
            "working_microrecord_de": WORKING_MICRORECORD,
        },
        "freeze": {
            "token_glosses_byte_identical": 479,
            "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3,
            "new_word_meanings": 0, "changed_word_meanings": 0,
            "content_word_additions": 0, "content_word_deletions": 0,
            "content_word_reorders": 0,
        },
        "gdt388_edge_intake": intake_payload,
        "inputs": {rel(path): sha256(path) for path in inputs},
        "files": {path.name: sha256(path) for path in generated},
        "next_gap": NEXT_GAP,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": STATUS, "ana_windows": 10, "exact_state_only": 1,
        "working_state_like": 2,
        "deictic_targets": 2, "unique_candidates": 1, "new_edges": 1,
        "cumulative_edges": 11, "gdt388_score_ready": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
