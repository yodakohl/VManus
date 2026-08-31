#!/usr/bin/env python3
"""Build the bounded V72 YKA-II/III object-frame experiment.

This is an exploratory working-relation pass.  It does not change a token
gloss and it deliberately keeps the neighbouring ``aiin`` quantity outside
the one newly admitted occurrence edge.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame"
SRC = EXP / "src"
ART = EXP / "artifacts"

STATUS = (
    "PASS_V72_YKA_II_III_SISTER_FRAME__5_CASES_2_REPLAY_"
    "1_NEW_B_EDGE_2_HELD__AIIN_UNBOUND__ZERO_WORD_DELTA"
)
QUESTION = (
    "Can the two admitted objectless YKA-III heat frames license the YKA-II "
    "sister at f86v5.24 to take one uniquely typed material share from the "
    "immediately preceding complete nominal block without binding its separate "
    "quantity register?"
)
CLAIM_CEILING = (
    "V72 adds one occurrence-bound B-tier working edge from f86v5.24#1 oar to "
    "#3 ykain under the inherited YKA-II/III sister family. The adjacent aiin "
    "remains an unbound quantity register; R010 and R012 remain held. This is "
    "an exploratory German relation reading, not a portable YKAIN rule, "
    "confirmed word meaning, plaintext, language, or externally grounded edge."
)

CASE_SPEC = SRC / "V72_HEAT_REFERENCE_CASE_SPECS.tsv"
RULE_SPEC = SRC / "V72_YKA_SISTER_RULE.tsv"

G388_RESULT = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
G626_FAMILY = ROOT / "experiments/yolo/gdt626_mobile_operation_lexicon/artifacts/MINIM_FAMILY_SUMMARY.tsv"
G664_ATLAS = ROOT / "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/FAMILY_COMPOSITION_ATLAS.tsv"
G664_READERS = ROOT / "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/READER_VARIANT_AUDIT.tsv"
G665_ATLAS = ROOT / "experiments/yolo/gdt665_one_hundred_forty_eight_residual_family_completion/artifacts/FAMILY_COMPOSITION_ATLAS.tsv"
G689_LINES = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/V62_51_LINE_READER.tsv"
G693_RULES = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts/V66_16_SELECTED_SURFACE_RULES.tsv"
G693_RN_PAIRS = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts/V66_30_R_N_TERMINAL_PAIR_OCCURRENCES.tsv"
G695_CLAUSES = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
G696_REFS = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_27_REFERENCE_CENSUS.tsv"
G696_RIVALS = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_17_RELATION_RIVALS.tsv"
G697_EDGES = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv"
G698_RESULT = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/RESULT.json"
G698_TOKENS = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_479_TOKEN_FREEZE.tsv"
G698_LINES = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_51_LINE_FREEZE.tsv"
G698_SPANS = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_3_BOUND_SPAN_FREEZE.tsv"

CASES_OUT = ART / "V72_5_HEAT_REFERENCE_CASES.tsv"
YKA_OUT = ART / "V72_3_YKA_ACTION_OCCURRENCES.tsv"
EDGE_OUT = ART / "V72_1_NEW_LOCAL_HEAT_EDGE.tsv"
CONTROLS_OUT = ART / "V72_3_CONTROL_EXCLUSIONS.tsv"
PACKET_OUT = ART / "V72_GDT388_EDGE_PACKET.tsv"
INTAKE_OUT = ART / "V72_GDT388_EDGE_INTAKE.json"
TOKENS_OUT = ART / "V72_479_TOKEN_RELATION_OVERLAY.tsv"
LINES_OUT = ART / "V72_51_LINE_RELATION_OVERLAY.tsv"
SPANS_OUT = ART / "V72_3_BOUND_SPAN_FREEZE.tsv"
READER_OUT = ART / "GDT699_V72_OBJECTLESS_HEAT_FRAME_READER.md"
ARTIFACT_README = ART / "README.md"
RESULT_OUT = ART / "RESULT.json"

CASE_SPEC_FIELDS = [
    "case_id", "reference_id", "case_role", "locus", "action_ordinal",
    "action_surface", "action_lemma", "action_grade", "family_membership",
    "prior_source_ordinals", "prior_source_surfaces", "prior_relation_or_rival",
    "prior_decision", "expected_v72_source_ordinals", "excluded_ordinals",
    "expected_v72_decision", "expected_support_tier", "working_reading_de",
    "reason_de", "forbidden_inference",
]
RULE_SPEC_FIELDS = [
    "rule_id", "family_head", "surface_II", "surface_III",
    "aggregate_count_II", "aggregate_count_III", "exact_card_II",
    "exact_card_III", "current_scope_occurrences", "prototype_edge_ids",
    "candidate_reference_id", "candidate_donor_ordinal",
    "candidate_excluded_quantity_ordinal", "admission_gate", "claim_scope",
]
CASE_FIELDS = [
    *CASE_SPEC_FIELDS,
    "page", "observed_action_surface", "observed_action_gloss_de",
    "observed_action_lemmas", "observed_prior_source_surfaces",
    "previous_clause_id", "previous_clause_type", "previous_clause_start_ordinal",
    "previous_clause_end_ordinal", "previous_clause_semantic_units",
    "previous_clause_binding_ids", "typed_material_ordinals",
    "quantity_register_ordinals", "written_action_object",
    "new_edge_id", "word_meaning_delta", "status",
]
YKA_FIELDS = [
    "page", "locus", "token_ordinal", "surface", "grade",
    "v71_token_gloss_de", "reference_id", "case_id", "case_role",
    "prior_edge_id", "v72_edge_id", "v72_decision", "status",
]
EDGE_FIELDS = [
    "edge_id", "locus", "support_tier", "relation_class", "source_ordinals",
    "reference_ordinals", "target_action_ordinal", "excluded_ordinals",
    "source_surface", "target_surface", "source_gloss_de", "target_gloss_de",
    "rule_id", "prototype_edge_ids", "reference_id", "prior_rival_id",
    "prior_rival_decision", "selection_basis", "quantity_exclusion_basis",
    "working_reading_de", "portability", "gdt388_score_ready",
    "v71_word_delta", "status",
]
CONTROL_FIELDS = [
    "control_id", "case_id", "reference_id", "locus", "token_ordinal",
    "surface", "control_type", "excluded_from_edge", "decision", "reason_de",
    "forbidden_inference", "status",
]
TOKEN_EXTRA_FIELDS = [
    "v72_heat_case_ids", "v72_relation_roles", "v72_edge_ids",
    "v72_reference_decision", "v72_token_gloss_de", "v72_word_delta",
    "v72_status",
]
LINE_EXTRA_FIELDS = [
    "v72_heat_case_ids", "v72_new_heat_edge_ids", "v72_held_heat_references",
    "v72_relation_annotations_de", "v72_working_relation_reading_de",
    "v72_clause_translation_de", "v72_word_delta", "v72_status",
]
SPAN_EXTRA_FIELDS = [
    "v72_selected_gloss_de", "v72_byte_identical", "v72_relation_change",
    "v72_status",
]

EDGE_PACKET_FIELDS = [
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
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def guarded_query(
    path: Path,
    *,
    selector: str,
    allowed: Iterable[str],
    columns: Sequence[str],
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
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if completed.stderr and "GUARD_STATS" not in completed.stderr:
        raise AssertionError(completed.stderr)
    if rows and tuple(rows[0]) != tuple(columns):
        raise AssertionError(f"guarded column mismatch for {path}")
    return rows


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def split_pipe(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def expand_ordinals(expression: str) -> list[int]:
    if expression in {"", "NONE"}:
        return []
    values: list[int] = []
    for part in expression.split("|"):
        if "-" in part:
            start, end = (int(item) for item in part.split("-", 1))
            values.extend(range(start, end + 1))
        else:
            values.append(int(part))
    return values


def action_ordinals(clause: Mapping[str, str]) -> set[int]:
    return {int(value) for value in split_pipe(clause["action_ordinals"])}


def exact_one(rows: Sequence[dict[str, str]], **conditions: str) -> dict[str, str]:
    selected = [row for row in rows if all(row.get(key) == value for key, value in conditions.items())]
    if len(selected) != 1:
        raise AssertionError(f"expected one row for {conditions}, found {len(selected)}")
    return selected[0]


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    case_fields, specs = read_tsv(CASE_SPEC)
    rule_fields, rule_rows = read_tsv(RULE_SPEC)
    assert case_fields == CASE_SPEC_FIELDS
    assert rule_fields == RULE_SPEC_FIELDS
    assert [row["case_id"] for row in specs] == ["V72H001", "V72H002", "V72H003", "V72H004", "V72H005"]
    assert [row["reference_id"] for row in specs] == ["R004", "R024", "R010", "R012", "R021"]
    assert len(rule_rows) == 1
    rule = rule_rows[0]
    assert rule == {
        "rule_id": "YKA-R01",
        "family_head": "yka",
        "surface_II": "ykain",
        "surface_III": "ykaiin",
        "aggregate_count_II": "11",
        "aggregate_count_III": "43",
        "exact_card_II": "Y_REFERENCE+K_HOT+A+IN_II",
        "exact_card_III": "Y_REFERENCE+K_HOT+AIIN_III",
        "current_scope_occurrences": "f105v.1#4|f86v5.24#3|f86v6.25#5",
        "prototype_edge_ids": "C001|C006",
        "candidate_reference_id": "R021",
        "candidate_donor_ordinal": "1",
        "candidate_excluded_quantity_ordinal": "2",
        "admission_gate": "REGISTERED_YKA_II_III_SISTERS+OBJECTLESS_DEICTIC_HEAT+IMMEDIATE_PRECEDING_COMPLETE_NOMINAL_BLOCK+EXACTLY_ONE_TYPED_MATERIAL_SHARE+NO_WRITTEN_ACTION_OBJECT",
        "claim_scope": "ONE_OCCURRENCE_BOUND_B_EDGE_NOT_PORTABLE",
    }

    g388 = json.loads(G388_RESULT.read_text(encoding="utf-8"))
    assert g388["status"] == "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES"
    assert g388["schema"] == "GDT388_RESULT_V1"
    assert g388["acquisition"]["minimum_edges"] == 50
    assert g388["acquisition"]["minimum_physical_folios"] == 5
    assert g388["acquisition"]["scoring_authorized"] is False

    result_698 = json.loads(G698_RESULT.read_text(encoding="utf-8"))
    assert result_698["status"].startswith("PASS_V71_")
    assert result_698["basis"] == {
        "bound_spans": 3, "f84_access": 0, "f84r_access": 0, "lines": 51,
        "new_pages": 0, "pages": 36, "token_positions": 479,
        "v70_edges": 9, "v70_microrecords": 7,
    }
    token_fields, token_rows = read_tsv(G698_TOKENS)
    line_fields, line_rows = read_tsv(G698_LINES)
    span_fields, span_rows = read_tsv(G698_SPANS)
    assert len(token_rows) == 479 and len(line_rows) == 51 and len(span_rows) == 3
    assert len({row["page"] for row in token_rows}) == 36
    assert all(not row["page"].startswith("f84") for row in token_rows + line_rows)
    assert all(not row["locus"].startswith("f84") for row in span_rows)
    assert all(row["v71_word_delta"] == "0" for row in token_rows + line_rows)
    assert all(row["v71_byte_identical"] == "1" for row in span_rows)

    loci = {row["locus"] for row in specs}
    clause_columns = [
        "page", "locus", "clause_id", "clause_type", "start_ordinal",
        "end_ordinal", "token_positions", "semantic_units", "surfaces",
        "action_ordinals", "verb_lemmas", "binding_ids", "v68_clause_de",
        "realization_rule", "content_word_delta",
    ]
    clauses = guarded_query(
        G695_CLAUSES, selector="locus", allowed=loci, columns=clause_columns,
    )
    ref_columns = [
        "reference_id", "locus", "reference_ordinal", "expected_surface",
        "expected_gloss_de", "decision", "linked_edge_ids", "source_ordinals",
        "target_ordinals", "scope_class", "provenance", "note",
    ]
    refs = guarded_query(G696_REFS, selector="locus", allowed=loci, columns=ref_columns)
    v62_line_columns = [
        "page", "locus", "v62_action_ordinals", "v62_action_surfaces",
        "v62_verb_occurrences", "v62_provenance_status",
    ]
    v62_lines = guarded_query(
        G689_LINES, selector="locus", allowed=loci, columns=v62_line_columns,
    )
    assert len(v62_lines) == 5
    v62_by_locus = {row["locus"]: row for row in v62_lines}
    assert set(v62_by_locus) == loci
    reader_columns = [
        "occurrence_id", "page", "locus", "ordinal", "surface", "reader_exact",
        "split_normalized", "all_present_exact", "zl3b_line", "it2a_line",
        "rf1b_line", "claim_boundary",
    ]
    reader_rows = guarded_query(
        G664_READERS, selector="locus", allowed={"f86v5.24"}, columns=reader_columns,
    )
    assert len(reader_rows) == 1
    reader_row = reader_rows[0]
    assert reader_row["ordinal"] == "3" and reader_row["surface"] == "ykain"
    assert reader_row["reader_exact"] == reader_row["split_normalized"] == reader_row["all_present_exact"] == "1"
    assert reader_row["zl3b_line"] == reader_row["it2a_line"] == reader_row["rf1b_line"]
    assert reader_row["zl3b_line"] == "oar aiin ykain okal kchody chckhy otaiin olkar otaiin"

    _, family_rows = read_tsv(G626_FAMILY)
    family = exact_one(family_rows, head="yka")
    assert family["surface_II"] == "ykain" and family["surface_III"] == "ykaiin"
    assert family["count_II"] == "11" and family["count_III"] == "43"
    assert family["present_values"] == "I|II|III" and family["complete_I_II_III"] == "1"

    _, atlas_664 = read_tsv(G664_ATLAS)
    _, atlas_665 = read_tsv(G665_ATLAS)
    card_ii = exact_one(atlas_664, surface="ykain")
    card_iii = exact_one(atlas_665, surface="ykaiin")
    assert card_ii["working_default_de"] == "erhitze hiervon auf Stufe II"
    assert card_ii["composition"] == rule["exact_card_II"]
    assert card_iii["working_default_de"] == "erhitze hiervon auf Stufe III"
    assert card_iii["composition"] == rule["exact_card_III"]

    _, head_rules = read_tsv(G693_RULES)
    oar_rule = exact_one(head_rules, surface="oar")
    assert oar_rule["selected_gloss_de"] == "Anteil I des Ansatzes"
    assert oar_rule["selected_formal_role"] == "R_INDEXED_MATERIAL_SHARE_SELECTOR"
    assert oar_rule["selected_candidate"] == "share"
    _, rn_pairs = read_tsv(G693_RN_PAIRS)
    aiin_pair = exact_one(rn_pairs, locus="f86v5.24", token_ordinal="2", surface="aiin")
    assert aiin_pair["v66_selected_gloss_de"] == "Menge III"
    assert aiin_pair["typed_role"] == "typed_value_III"
    assert aiin_pair["v66_selected_terminal_semantics"] == "N_HEAD_TYPED_GRADE_AMOUNT_OR_BATCH_VALUE"

    _, edges = read_tsv(G697_EDGES)
    prototype_edges = {edge_id: exact_one(edges, edge_id=edge_id) for edge_id in ("C001", "C006")}
    assert prototype_edges["C001"]["source_ordinals"] == "3"
    assert prototype_edges["C001"]["target_action_ordinal"] == "4"
    assert prototype_edges["C001"]["support_tier"] == "A_STRONG_LICENSED"
    assert prototype_edges["C006"]["source_ordinals"] == "4"
    assert prototype_edges["C006"]["target_action_ordinal"] == "5"
    assert prototype_edges["C006"]["support_tier"] == "A_MINUS_EXPLICIT_OUTPUT"

    _, rivals = read_tsv(G696_RIVALS)
    h002 = exact_one(rivals, rival_id="H002")
    h007 = exact_one(rivals, rival_id="H007")
    assert h002["decision"] == h007["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED"
    assert h007["source_ordinals"] == "1-2" and h007["target_action_ordinal"] == "3"
    assert "in Menge III" in h007["plausible_reading_de"]

    token_by_position = {
        (row["locus"], int(row["token_ordinal"])): row for row in token_rows
    }
    clauses_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for clause in clauses:
        clauses_by_locus[clause["locus"]].append(clause)
    refs_by_id = {row["reference_id"]: row for row in refs}
    assert set(refs_by_id) >= {row["reference_id"] for row in specs} | {"R009"}
    assert refs_by_id["R009"]["decision"] == "STRUCTURAL_SEQUENCE_ONLY"

    case_rows: list[dict[str, object]] = []
    for spec in specs:
        ref = refs_by_id[spec["reference_id"]]
        ordinal = int(spec["action_ordinal"])
        action = token_by_position[(spec["locus"], ordinal)]
        assert ref["locus"] == spec["locus"]
        assert ref["reference_ordinal"] == spec["action_ordinal"]
        assert ref["expected_surface"] == spec["action_surface"] == action["surface"]
        assert ref["decision"] == spec["prior_decision"]
        assert ref["source_ordinals"] == spec["prior_source_ordinals"]
        assert action["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL"
        assert action["v71_token_gloss_de"] == action["v70_token_gloss_de"]
        v62_line = v62_by_locus[spec["locus"]]
        v62_pairs = dict(zip(split_pipe(v62_line["v62_action_ordinals"]), split_pipe(v62_line["v62_action_surfaces"])))
        assert v62_pairs[spec["action_ordinal"]] == spec["action_surface"]
        assert v62_line["v62_provenance_status"] == "ALL_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL"

        action_clauses = [
            row for row in clauses_by_locus[spec["locus"]]
            if row["clause_type"] == "ACTION_CLAUSE" and ordinal in action_ordinals(row)
        ]
        assert len(action_clauses) == 1
        action_clause = action_clauses[0]
        observed_lemmas = action_clause["verb_lemmas"]
        assert observed_lemmas == spec["action_lemma"]
        previous = exact_one(
            clauses_by_locus[spec["locus"]],
            clause_id=str(int(action_clause["clause_id"]) - 1),
        )
        source_positions = expand_ordinals(spec["prior_source_ordinals"])
        observed_sources = [token_by_position[(spec["locus"], value)]["surface"] for value in source_positions]
        assert "|".join(observed_sources) == spec["prior_source_surfaces"]

        typed_material = "NONE"
        quantity_register = "NONE"
        written_object = "NONE"
        new_edge_id = "NONE"
        if spec["case_id"] == "V72H001":
            typed_material = "3"
            assert prototype_edges["C001"]["locus"] == spec["locus"]
        elif spec["case_id"] == "V72H002":
            typed_material = "4:ADMITTED_ACTION_OUTPUT"
            assert previous["clause_type"] == "ACTION_CLAUSE"
            assert prototype_edges["C006"]["locus"] == spec["locus"]
        elif spec["case_id"] == "V72H003":
            typed_material = "1|3"
            assert len(source_positions) == 3
            assert spec["expected_v72_source_ordinals"] == "NONE"
        elif spec["case_id"] == "V72H004":
            written_object = "Krautdroge"
            assert "Krautdroge" in action["v71_token_gloss_de"]
            assert h002["locus"] == spec["locus"]
        elif spec["case_id"] == "V72H005":
            typed_material = "1"
            quantity_register = "2"
            new_edge_id = "C010"
            assert previous["clause_type"] == "NOMINAL_BLOCK"
            assert previous["start_ordinal"] == "1" and previous["end_ordinal"] == "2"
            assert previous["semantic_units"] == "2" and previous["binding_ids"] == "NONE"
            assert previous["surfaces"] == "oar|aiin"
            assert token_by_position[(spec["locus"], 1)]["v71_token_gloss_de"] == "Anteil I des Ansatzes"
            assert token_by_position[(spec["locus"], 2)]["v71_token_gloss_de"] == "Menge III"
            assert spec["expected_v72_source_ordinals"] == "1"
            assert spec["excluded_ordinals"] == "2"
            assert h007["locus"] == spec["locus"]
        else:
            raise AssertionError(spec["case_id"])

        case_rows.append({
            **spec,
            "page": action["page"],
            "observed_action_surface": action["surface"],
            "observed_action_gloss_de": action["v71_token_gloss_de"],
            "observed_action_lemmas": observed_lemmas,
            "observed_prior_source_surfaces": "|".join(observed_sources),
            "previous_clause_id": previous["clause_id"],
            "previous_clause_type": previous["clause_type"],
            "previous_clause_start_ordinal": previous["start_ordinal"],
            "previous_clause_end_ordinal": previous["end_ordinal"],
            "previous_clause_semantic_units": previous["semantic_units"],
            "previous_clause_binding_ids": previous["binding_ids"],
            "typed_material_ordinals": typed_material,
            "quantity_register_ordinals": quantity_register,
            "written_action_object": written_object,
            "new_edge_id": new_edge_id,
            "word_meaning_delta": 0,
            "status": STATUS,
        })
    write_tsv(CASES_OUT, case_rows, CASE_FIELDS)

    yka_token_rows = [
        row for row in token_rows
        if row["surface"] in {rule["surface_II"], rule["surface_III"]}
        and row["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL"
    ]
    assert [(row["locus"], row["token_ordinal"], row["surface"]) for row in yka_token_rows] == [
        ("f105v.1", "4", "ykaiin"),
        ("f86v5.24", "3", "ykain"),
        ("f86v6.25", "5", "ykaiin"),
    ]
    spec_by_position = {(row["locus"], row["action_ordinal"]): row for row in specs}
    yka_rows: list[dict[str, object]] = []
    for token in yka_token_rows:
        spec = spec_by_position[(token["locus"], token["token_ordinal"])]
        prior_edge = {"V72H001": "C001", "V72H002": "C006", "V72H005": "NONE"}[spec["case_id"]]
        new_edge = "C010" if spec["case_id"] == "V72H005" else "NONE"
        yka_rows.append({
            "page": token["page"], "locus": token["locus"],
            "token_ordinal": token["token_ordinal"], "surface": token["surface"],
            "grade": spec["action_grade"], "v71_token_gloss_de": token["v71_token_gloss_de"],
            "reference_id": spec["reference_id"], "case_id": spec["case_id"],
            "case_role": spec["case_role"], "prior_edge_id": prior_edge,
            "v72_edge_id": new_edge, "v72_decision": spec["expected_v72_decision"],
            "status": STATUS,
        })
    write_tsv(YKA_OUT, yka_rows, YKA_FIELDS)

    candidate = exact_one(specs, case_id="V72H005")
    edge_row = {
        "edge_id": "C010", "locus": "f86v5.24", "support_tier": "B_WORKING_LOCAL",
        "relation_class": "YKA_DEGREE_SISTER_TYPED_MATERIAL_CARRY",
        "source_ordinals": "1", "reference_ordinals": "3",
        "target_action_ordinal": "3", "excluded_ordinals": "2",
        "source_surface": "oar", "target_surface": "ykain",
        "source_gloss_de": "Anteil I des Ansatzes",
        "target_gloss_de": "erhitze hiervon auf Stufe II",
        "rule_id": "YKA-R01", "prototype_edge_ids": "C001|C006",
        "reference_id": "R021", "prior_rival_id": "H007",
        "prior_rival_decision": "HELD_AS_RIVAL_NOT_ADMITTED",
        "selection_basis": "UNIQUE_GDT693_TYPED_MATERIAL_SHARE_IN_IMMEDIATE_COMPLETE_V68_BLOCK",
        "quantity_exclusion_basis": "V68_TWO_SEMANTIC_UNITS_BINDING_NONE__AIIN_QUANTITY_REGISTER_NOT_EDGE_SOURCE",
        "working_reading_de": candidate["working_reading_de"],
        "portability": "OCCURRENCE_BOUND_ONLY", "gdt388_score_ready": 0,
        "v71_word_delta": 0, "status": STATUS,
    }
    write_tsv(EDGE_OUT, [edge_row], EDGE_FIELDS)

    controls = [
        {
            "control_id": "X001", "case_id": "V72H003", "reference_id": "R010",
            "locus": "f23r.6", "token_ordinal": 5, "surface": "yky",
            "control_type": "OUTSIDE_YKA_MULTIPLE_DONORS", "excluded_from_edge": "1|3-4",
            "decision": "KEEP_UNRESOLVED_MULTI_DONOR",
            "reason_de": "Außerhalb der YKA-II/III-Familie; mehrere lebende Donoren; R009 wählt kein Objekt.",
            "forbidden_inference": "Kein Hierzu-, Nähe- oder Nächster-Nominalausdruck-Default.", "status": STATUS,
        },
        {
            "control_id": "X002", "case_id": "V72H004", "reference_id": "R012",
            "locus": "f26r.2", "token_ordinal": 4, "surface": "ykecthey",
            "control_type": "OUTSIDE_YKA_WRITTEN_OBJECT", "excluded_from_edge": "3",
            "decision": "KEEP_HELD_WRITTEN_OBJECT",
            "reason_de": "Außerhalb der YKA-II/III-Familie; die Aktion nennt Krautdroge bereits als Materialobjekt.",
            "forbidden_inference": "Quellbezug nicht mit dem geschriebenen Objekt gleichsetzen.", "status": STATUS,
        },
        {
            "control_id": "X003", "case_id": "V72H005", "reference_id": "R021",
            "locus": "f86v5.24", "token_ordinal": 2, "surface": "aiin",
            "control_type": "UNBOUND_QUANTITY_REGISTER", "excluded_from_edge": "2",
            "decision": "EXCLUDE_FROM_C010",
            "reason_de": "V68 führt oar und aiin als zwei semantische Einheiten ohne Bindung; nur oar ist typisierter Materialanteil.",
            "forbidden_inference": "Nicht „in Menge III“ lesen und AIIN weder an OAR noch YKAIN binden.", "status": STATUS,
        },
    ]
    write_tsv(CONTROLS_OUT, controls, CONTROL_FIELDS)

    packet_row = {
        "edge_id": "C010", "batch_id": "GDT699_V72", "page": "f86v5",
        "physical_folio": "f86", "diagram_unit_id": "TEXTUAL_WORKSHOP_LINE",
        "pivot_visual_id": "TOKEN_1_OAR", "pivot_locus": "f86v5.24@1",
        "target_visual_id": "TOKEN_3_YKAIN", "target_locus": "f86v5.24@3",
        "relation_type": "WORKSHOP_OBJECT_CARRY",
        "direction_basis": "FORMAL_YKA_SISTER_REPLAY",
        "ownership_basis": "UNIQUE_TYPED_LEFT_PREDECESSOR",
        "geometry_only_selection": "FALSE", "source_manifest_id": "GDT699",
        "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE", "source_aware_localizer": "GDT699_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "B_WORKING_LOCAL",
        "ambiguity_state": "WORKSHOP_ONLY", "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_WORKSHOP_EDGE",
    }
    write_tsv(PACKET_OUT, [packet_row], EDGE_PACKET_FIELDS)
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
    INTAKE_OUT.write_text(
        json.dumps(intake_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    position_case_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    action_decisions: dict[tuple[str, int], str] = {}
    for spec in specs:
        locus = spec["locus"]
        for ordinal in set(expand_ordinals(spec["prior_source_ordinals"]) + [int(spec["action_ordinal"])]):
            position_case_ids[(locus, ordinal)].add(spec["case_id"])
        action_decisions[(locus, int(spec["action_ordinal"]))] = spec["expected_v72_decision"]

    token_overlay: list[dict[str, object]] = []
    for row in token_rows:
        position = (row["locus"], int(row["token_ordinal"]))
        relation_roles = "NONE"
        edge_ids = "NONE"
        decision = action_decisions.get(position, "NONE")
        if position == ("f86v5.24", 1):
            relation_roles, edge_ids = "DONOR_MATERIAL:C010", "C010"
        elif position == ("f86v5.24", 2):
            relation_roles, decision = "UNBOUND_QUANTITY_REGISTER:R021", "EXCLUDE_FROM_C010"
        elif position == ("f86v5.24", 3):
            relation_roles, edge_ids = "REFERENCE:C010|TARGET_ACTION:C010", "C010"
        token_overlay.append({
            **row,
            "v72_heat_case_ids": "|".join(sorted(position_case_ids.get(position, set()))) or "NONE",
            "v72_relation_roles": relation_roles,
            "v72_edge_ids": edge_ids,
            "v72_reference_decision": decision,
            "v72_token_gloss_de": row["v71_token_gloss_de"],
            "v72_word_delta": 0,
            "v72_status": STATUS,
        })
    write_tsv(TOKENS_OUT, token_overlay, [*token_fields, *TOKEN_EXTRA_FIELDS])

    cases_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        cases_by_locus[spec["locus"]].append(spec)
    line_overlay: list[dict[str, object]] = []
    for row in line_rows:
        local_cases = cases_by_locus.get(row["locus"], [])
        case_ids = "|".join(item["case_id"] for item in local_cases) or "NONE"
        held = "|".join(
            item["reference_id"] for item in local_cases
            if item["expected_v72_decision"].startswith("KEEP_")
        ) or "NONE"
        new_edges = "C010" if row["locus"] == "f86v5.24" else "NONE"
        annotation = "NONE"
        working = "NONE"
        if local_cases:
            annotation = " | ".join(item["reason_de"] for item in local_cases)
            working = " | ".join(item["working_reading_de"] for item in local_cases)
        line_overlay.append({
            **row,
            "v72_heat_case_ids": case_ids,
            "v72_new_heat_edge_ids": new_edges,
            "v72_held_heat_references": held,
            "v72_relation_annotations_de": annotation,
            "v72_working_relation_reading_de": working,
            "v72_clause_translation_de": row["v71_clause_translation_de"],
            "v72_word_delta": 0,
            "v72_status": STATUS,
        })
    write_tsv(LINES_OUT, line_overlay, [*line_fields, *LINE_EXTRA_FIELDS])

    span_overlay = [
        {
            **row,
            "v72_selected_gloss_de": row["v71_selected_gloss_de"],
            "v72_byte_identical": 1,
            "v72_relation_change": "NONE",
            "v72_status": STATUS,
        }
        for row in span_rows
    ]
    write_tsv(SPANS_OUT, span_overlay, [*span_fields, *SPAN_EXTRA_FIELDS])

    target_line = exact_one(line_rows, locus="f86v5.24")
    reader: list[str] = [
        "# GDT699 — V72 objectless YKA heat frame reader", "",
        f"Status: `{STATUS}`", "", "## Concrete result", "",
        "Surface window: `oar aiin ykain`", "",
        "> Anteil I des Ansatzes. [Ungebundene Mengenangabe #2: „Menge III“.] Den Ansatzanteil auf Stufe II erhitzen.", "",
        "Only `oar#1 → ykain#3` is the new edge. `aiin#2` remains a separate, unbound quantity register. The stronger old H007 reading “in Menge III” is not admitted.", "",
        "## Five-case deck", "",
        "| case | locus | action | role | V72 decision | working reading |", "|---|---|---|---|---|---|",
    ]
    for row in case_rows:
        reader.append(
            f"| {row['case_id']} | `{row['locus']}#{row['action_ordinal']}` | `{row['action_surface']}` | "
            f"{row['case_role']} | {row['expected_v72_decision']} | {md(str(row['working_reading_de']))} |"
        )
    reader.extend([
        "", "## Exact current line", "",
        f"Surface: `{target_line['zl3b_line']}`", "",
        f"Inherited clause reader: {target_line['v71_clause_translation_de']}", "",
        "V72 changes only the participant relation in the first operation; all token glosses and the inherited clause string remain byte-identical.", "",
        "## Boundaries", "",
        "- Current-scope YKA action census: exactly three occurrences—two admitted `ykaiin` prototypes and the one `ykain` candidate.",
        "- R010 stays open because it is outside YKA and has multiple donors.",
        "- R012 stays open as a source relation because its action already names `Krautdroge`.",
        "- C010 is B-tier and occurrence-bound; no generic left-object or YKAIN default is created.",
        "- The GDT388 acquisition packet is intentionally not score-ready: this edge was selected with formal text access and has no capacity, holdout, crop provenance or mobile null.",
        "- 479 token glosses, 51 inherited clause readings and 3 spans remain unchanged.", "",
    ])
    READER_OUT.write_text("\n".join(reader), encoding="utf-8")

    ARTIFACT_README.write_text(
        "# GDT699 artifacts\n\n"
        "- `V72_5_HEAT_REFERENCE_CASES.tsv`: two admitted prototypes, two held controls and one YKA-II candidate.\n"
        "- `V72_3_YKA_ACTION_OCCURRENCES.tsv`: exhaustive current-scope YKA action census.\n"
        "- `V72_1_NEW_LOCAL_HEAT_EDGE.tsv`: C010, only oar#1 to ykain#3.\n"
        "- `V72_3_CONTROL_EXCLUSIONS.tsv`: R010, R012 and the unbound aiin quantity.\n"
        "- `V72_GDT388_EDGE_PACKET.tsv` and `V72_GDT388_EDGE_INTAKE.json`: explicit not-score-ready external-edge audit.\n"
        "- `V72_479_TOKEN_RELATION_OVERLAY.tsv`, `V72_51_LINE_RELATION_OVERLAY.tsv`, `V72_3_BOUND_SPAN_FREEZE.tsv`: complete unchanged inherited reader plus separate V72 relation fields.\n"
        "- `GDT699_V72_OBJECTLESS_HEAT_FRAME_READER.md`: compact practical reading.\n"
        "- `RESULT.json` and `VALIDATION.json`: machine summaries.\n",
        encoding="utf-8",
    )

    generated = [
        CASES_OUT, YKA_OUT, EDGE_OUT, CONTROLS_OUT, PACKET_OUT, INTAKE_OUT,
        TOKENS_OUT, LINES_OUT, SPANS_OUT, READER_OUT, ARTIFACT_README,
    ]
    inputs = [
        CASE_SPEC, RULE_SPEC, G388_RESULT, G626_FAMILY, G664_ATLAS, G664_READERS, G665_ATLAS,
        G689_LINES, G693_RULES, G693_RN_PAIRS, G695_CLAUSES, G696_REFS, G696_RIVALS, G697_EDGES,
        G698_RESULT, G698_TOKENS, G698_LINES, G698_SPANS, Path(__file__).resolve(),
    ]
    result = {
        "status": STATUS,
        "question": QUESTION,
        "claim_ceiling": CLAIM_CEILING,
        "basis": {
            "pages": 36, "new_pages": 0, "token_positions": 479, "lines": 51,
            "bound_spans": 3, "heat_reference_cases": 5,
            "current_yka_action_occurrences": 3, "f84_access": 0, "f84r_access": 0,
        },
        "family": {
            "head": "yka", "surface_II": "ykain", "surface_III": "ykaiin",
            "inherited_aggregate_count_II": 11, "inherited_aggregate_count_III": 43,
            "current_scope_II": 1, "current_scope_III": 2,
            "admitted_prototype_edges": ["C001", "C006"],
        },
        "decisions": {
            "prototype_replays": 2, "new_occurrence_bound_edges": 1,
            "held_outside_family_controls": 2, "excluded_quantity_registers": 1,
            "new_edge_id": "C010", "new_edge_source": "f86v5.24#1",
            "new_edge_target": "f86v5.24#3", "excluded_from_edge": "f86v5.24#2",
            "old_h007_promoted": 0,
            "working_reading_de": candidate["working_reading_de"],
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
        "next_gap": "Keep C010 occurrence-bound. Next test only the f26r.2 H003 split: ykecthey#4 ACTION_OUTPUT(Krautdroge) to objectless ytedy#6 across exactly one state-only chedy#5 register. Exclude #3 and #5 as donors, do not export the output beyond #6, and do not infer a general carry rule.",
    }
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": STATUS, "cases": 5, "yka_actions": 3,
        "prototype_replays": 2, "new_edges": 1, "held_controls": 2,
        "aiin_bound": 0, "gdt388_score_ready": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
