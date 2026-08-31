#!/usr/bin/env python3
"""Independent fail-closed validation for GDT699.

The builder is neither imported nor read.  This validator reconstructs the
five-case decision from hash-bound upstream artifacts, replays the official
GDT388 intake, and verifies that V72 adds only C010 while preserving the
479-token, 51-line and three-span V71 reader byte-for-byte.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence

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
NEXT_GAP = (
    "Keep C010 occurrence-bound. Next test only the f26r.2 H003 split: "
    "ykecthey#4 ACTION_OUTPUT(Krautdroge) to objectless ytedy#6 across exactly "
    "one state-only chedy#5 register. Exclude #3 and #5 as donors, do not "
    "export the output beyond #6, and do not infer a general carry rule."
)
WORKING_READING = (
    "Anteil I des Ansatzes. [Ungebundene Mengenangabe #2: „Menge III“.] "
    "Den Ansatzanteil auf Stufe II erhitzen."
)

CASE_SPEC = SRC / "V72_HEAT_REFERENCE_CASE_SPECS.tsv"
RULE_SPEC = SRC / "V72_YKA_SISTER_RULE.tsv"
RUN_RELATIVE = "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/src/run.py"
RUN_DECLARED_SHA256 = "2c8b41ae1960a50bfcfc4811bb8ede64d865b0b7cec129769db37708e255350c"
CASE_SPEC_SHA256 = "f7c2ebfa6affc721dff00012866e5e61b1881b47a40a01330cf0621474258a3f"
RULE_SPEC_SHA256 = "57bddefb8e2a8c106e5a38de22db8f5a0e08ba590aaad90475a6765cc58d1e13"

INPUT_HASHES = {
    "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json": "79cf873aa0f718d69d2af321ea8ebbae6c1db5fdef796ea099fe6b71045a9ac6",
    "experiments/yolo/gdt626_mobile_operation_lexicon/artifacts/MINIM_FAMILY_SUMMARY.tsv": "da48ba0041048298947ace1d9cbba69032d80f9e6377861e6b90e32b1c65dd7e",
    "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/FAMILY_COMPOSITION_ATLAS.tsv": "826fe2b66e264723a2d65f4ef54499a4de8916b7f670b781c6c75b6b3e5e1ea5",
    "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/READER_VARIANT_AUDIT.tsv": "521e45502c1a07251fd3ab6e581ce1a6f646c1bcb7f21e3b79cc17caab592e22",
    "experiments/yolo/gdt665_one_hundred_forty_eight_residual_family_completion/artifacts/FAMILY_COMPOSITION_ATLAS.tsv": "4ae31120e98ccdc0c1fd180704e442d8bdeb3a4bc26c912d84ecf37b9ddf8e16",
    "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/V62_51_LINE_READER.tsv": "03b5d6f31a99acb9c8c29d2647529301e37b6b45d356517668c3bb8335a6091d",
    "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts/V66_16_SELECTED_SURFACE_RULES.tsv": "ce8ad4720f28db86df7c23c894f43dcd494a7f6ec796f5c3243f2168c0a56e30",
    "experiments/yolo/gdt693_ar_head_semantic_tournament/artifacts/V66_30_R_N_TERMINAL_PAIR_OCCURRENCES.tsv": "245a4ad58bae30fc263a76e022e0bb4c36af8d57a2985b1fa1ec2dcae3bb3617",
    "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv": "805c246ee7daf213329bec3e3d5f5a0ef32be0f6db6c6f790f69c74b6169d66b",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_17_RELATION_RIVALS.tsv": "8c97948f25f94f59e141b65230de23d2fcf75de0da926e20caaa46507d7916dd",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_27_REFERENCE_CENSUS.tsv": "f289027471897b4605b0821c6378985ff4d1fc03b37868feaa6e24704b95f6d2",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv": "02be802b569c39354f5bff77786cc2143e8d9e344bae09d4c8d14562f37a6aac",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/RESULT.json": "6f3e17cf0457820e893b9c6032bc7e00e2c537fcc8bb380d35dbf9867a22c174",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_3_BOUND_SPAN_FREEZE.tsv": "a75bfdf203ee352360412260ee3458bddc5246af88b31cea4880f9446750ce7b",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_479_TOKEN_FREEZE.tsv": "9400bcf8209c864d3960da27f2c882e541aa86ea3d5bfc12d62565a147658c45",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_51_LINE_FREEZE.tsv": "a66cfd78044fd21b584951a34507e156a0c712550e8c3b8304e272a09b4e13b0",
}

G388 = ROOT / next(path for path in INPUT_HASHES if "gdt388_" in path)
G626 = ROOT / next(path for path in INPUT_HASHES if "gdt626_" in path)
G664_ATLAS = ROOT / next(path for path in INPUT_HASHES if "gdt664_" in path and "FAMILY_" in path)
G664_READERS = ROOT / next(path for path in INPUT_HASHES if "gdt664_" in path and "READER_" in path)
G665_ATLAS = ROOT / next(path for path in INPUT_HASHES if "gdt665_" in path)
G689_LINES = ROOT / next(path for path in INPUT_HASHES if "gdt689_" in path)
G693_RULES = ROOT / next(path for path in INPUT_HASHES if "gdt693_" in path and "SELECTED_" in path)
G693_PAIRS = ROOT / next(path for path in INPUT_HASHES if "gdt693_" in path and "PAIR_" in path)
G695_CLAUSES = ROOT / next(path for path in INPUT_HASHES if "gdt695_" in path)
G696_RIVALS = ROOT / next(path for path in INPUT_HASHES if "gdt696_" in path and "RIVALS" in path)
G696_REFS = ROOT / next(path for path in INPUT_HASHES if "gdt696_" in path and "CENSUS" in path)
G697_EDGES = ROOT / next(path for path in INPUT_HASHES if "gdt697_" in path)
G698_RESULT = ROOT / next(path for path in INPUT_HASHES if "gdt698_" in path and path.endswith("RESULT.json"))
G698_TOKENS = ROOT / next(path for path in INPUT_HASHES if "gdt698_" in path and "479_TOKEN" in path)
G698_LINES = ROOT / next(path for path in INPUT_HASHES if "gdt698_" in path and "51_LINE" in path)
G698_SPANS = ROOT / next(path for path in INPUT_HASHES if "gdt698_" in path and "3_BOUND" in path)

CASES = ART / "V72_5_HEAT_REFERENCE_CASES.tsv"
YKA = ART / "V72_3_YKA_ACTION_OCCURRENCES.tsv"
EDGE = ART / "V72_1_NEW_LOCAL_HEAT_EDGE.tsv"
CONTROLS = ART / "V72_3_CONTROL_EXCLUSIONS.tsv"
PACKET = ART / "V72_GDT388_EDGE_PACKET.tsv"
INTAKE = ART / "V72_GDT388_EDGE_INTAKE.json"
TOKENS = ART / "V72_479_TOKEN_RELATION_OVERLAY.tsv"
LINES = ART / "V72_51_LINE_RELATION_OVERLAY.tsv"
SPANS = ART / "V72_3_BOUND_SPAN_FREEZE.tsv"
READER = ART / "GDT699_V72_OBJECTLESS_HEAT_FRAME_READER.md"
RESULT = ART / "RESULT.json"

CASE_EXTRA = [
    "page", "observed_action_surface", "observed_action_gloss_de",
    "observed_action_lemmas", "observed_prior_source_surfaces",
    "previous_clause_id", "previous_clause_type", "previous_clause_start_ordinal",
    "previous_clause_end_ordinal", "previous_clause_semantic_units",
    "previous_clause_binding_ids", "typed_material_ordinals",
    "quantity_register_ordinals", "written_action_object", "new_edge_id",
    "word_meaning_delta", "status",
]
TOKEN_EXTRA = [
    "v72_heat_case_ids", "v72_relation_roles", "v72_edge_ids",
    "v72_reference_decision", "v72_token_gloss_de", "v72_word_delta", "v72_status",
]
LINE_EXTRA = [
    "v72_heat_case_ids", "v72_new_heat_edge_ids", "v72_held_heat_references",
    "v72_relation_annotations_de", "v72_working_relation_reading_de",
    "v72_clause_translation_de", "v72_word_delta", "v72_status",
]
SPAN_EXTRA = ["v72_selected_gloss_de", "v72_byte_identical", "v72_relation_change", "v72_status"]

GENERATED = {
    "GDT699_V72_OBJECTLESS_HEAT_FRAME_READER.md": READER,
    "README.md": ART / "README.md",
    "V72_1_NEW_LOCAL_HEAT_EDGE.tsv": EDGE,
    "V72_3_BOUND_SPAN_FREEZE.tsv": SPANS,
    "V72_3_CONTROL_EXCLUSIONS.tsv": CONTROLS,
    "V72_3_YKA_ACTION_OCCURRENCES.tsv": YKA,
    "V72_479_TOKEN_RELATION_OVERLAY.tsv": TOKENS,
    "V72_51_LINE_RELATION_OVERLAY.tsv": LINES,
    "V72_5_HEAT_REFERENCE_CASES.tsv": CASES,
    "V72_GDT388_EDGE_INTAKE.json": INTAKE,
    "V72_GDT388_EDGE_PACKET.tsv": PACKET,
}

PREFIX = "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/"
EXPECTED_OUTPUTS = {
    PREFIX + name for name in (
        "README.md", "METHOD.md", "REPORT.md",
        "src/V72_HEAT_REFERENCE_CASE_SPECS.tsv", "src/V72_YKA_SISTER_RULE.tsv",
        "src/run.py", "src/validate.py",
        "artifacts/GDT699_V72_OBJECTLESS_HEAT_FRAME_READER.md",
        "artifacts/README.md", "artifacts/RESULT.json",
        "artifacts/V72_1_NEW_LOCAL_HEAT_EDGE.tsv",
        "artifacts/V72_3_BOUND_SPAN_FREEZE.tsv",
        "artifacts/V72_3_CONTROL_EXCLUSIONS.tsv",
        "artifacts/V72_3_YKA_ACTION_OCCURRENCES.tsv",
        "artifacts/V72_479_TOKEN_RELATION_OVERLAY.tsv",
        "artifacts/V72_51_LINE_RELATION_OVERLAY.tsv",
        "artifacts/V72_5_HEAT_REFERENCE_CASES.tsv",
        "artifacts/V72_GDT388_EDGE_INTAKE.json",
        "artifacts/V72_GDT388_EDGE_PACKET.tsv",
        "artifacts/VALIDATION.json",
    )
}


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, object]] = []

    def check(self, condition: object, name: str) -> None:
        passed = bool(condition)
        self.checks.append({"check": name, "pass": int(passed)})
        if not passed:
            raise AssertionError(name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if not fields or len(fields) != len(set(fields)):
        raise AssertionError(f"invalid TSV header: {path}")
    for number, row in enumerate(rows, 2):
        if None in row or set(row) != set(fields) or any(value is None for value in row.values()):
            raise AssertionError(f"malformed TSV row {number}: {path}")
    return fields, rows


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"expected one row for {wanted}, got {len(hits)}")
    return hits[0]


def guarded(path: Path, selector: str, allowed: Sequence[str], columns: Sequence[str]) -> list[dict[str, str]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", selector, "--columns", ",".join(columns),
        "--forbid-prefix", "f84",
    ]
    for value in sorted(set(allowed)):
        command.extend(["--allow", value])
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0 or (completed.stderr and "GUARD_STATS" not in completed.stderr):
        raise AssertionError(f"guarded query failed: {path}: {completed.stderr}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if rows and list(rows[0]) != list(columns):
        raise AssertionError(f"guarded schema mismatch: {path}")
    return rows


def assert_projection(
    audit: Audit,
    source_fields: Sequence[str], source_rows: Sequence[Mapping[str, str]],
    output_fields: Sequence[str], output_rows: Sequence[Mapping[str, str]],
    extra_fields: Sequence[str], label: str,
) -> None:
    audit.check(list(output_fields) == [*source_fields, *extra_fields], f"{label} schema extends source exactly")
    audit.check(len(source_rows) == len(output_rows), f"{label} row count unchanged")
    for index, (source, output) in enumerate(zip(source_rows, output_rows), 1):
        audit.check(all(output[field] == source[field] for field in source_fields), f"{label} source projection exact {index}")


def main() -> int:
    audit = Audit()

    # Immutable inputs.  The builder path is intentionally not opened here.
    audit.check(sha256(CASE_SPEC) == CASE_SPEC_SHA256, "case specification hash exact")
    audit.check(sha256(RULE_SPEC) == RULE_SPEC_SHA256, "YKA rule specification hash exact")
    for relative, digest in INPUT_HASHES.items():
        audit.check(sha256(ROOT / relative) == digest, f"upstream input hash exact {Path(relative).name}")

    g388 = json.loads(G388.read_text(encoding="utf-8"))
    audit.check(
        g388["status"] == "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES"
        and g388["schema"] == "GDT388_RESULT_V1"
        and g388["acquisition"]["minimum_edges"] == 50
        and g388["acquisition"]["minimum_physical_folios"] == 5
        and g388["acquisition"]["scoring_authorized"] is False,
        "GDT388 packet capacity contract exact",
    )

    spec_fields, specs = read_tsv(CASE_SPEC)
    rule_fields, rules = read_tsv(RULE_SPEC)
    audit.check(len(specs) == 5 and len(rules) == 1, "fixed five-case and one-rule decks")
    audit.check([row["case_id"] for row in specs] == [f"V72H00{i}" for i in range(1, 6)], "collision-free V72 case IDs exact")
    audit.check([row["reference_id"] for row in specs] == ["R004", "R024", "R010", "R012", "R021"], "five reference IDs exact")
    audit.check([row["case_role"] for row in specs].count("ADMITTED_PROTOTYPE") == 2, "two replay prototypes fixed")
    candidate = one(specs, case_id="V72H005")
    audit.check(
        candidate["locus"] == "f86v5.24" and candidate["action_ordinal"] == "3"
        and candidate["action_surface"] == "ykain" and candidate["expected_v72_source_ordinals"] == "1"
        and candidate["excluded_ordinals"] == "2" and candidate["working_reading_de"] == WORKING_READING,
        "candidate fixes only oar#1 to ykain#3 and excludes aiin#2",
    )
    rule = rules[0]
    audit.check(
        rule["rule_id"] == "YKA-R01" and rule["family_head"] == "yka"
        and rule["surface_II"] == "ykain" and rule["surface_III"] == "ykaiin"
        and rule["aggregate_count_II"] == "11" and rule["aggregate_count_III"] == "43"
        and rule["candidate_donor_ordinal"] == "1"
        and rule["candidate_excluded_quantity_ordinal"] == "2"
        and rule["claim_scope"] == "ONE_OCCURRENCE_BOUND_B_EDGE_NOT_PORTABLE",
        "registered YKA sister rule and scope exact",
    )

    # Independent source reconstruction.
    _, family_rows = read_tsv(G626)
    family = one(family_rows, head="yka")
    audit.check(
        family["surface_II"] == "ykain" and family["surface_III"] == "ykaiin"
        and family["count_II"] == "11" and family["count_III"] == "43"
        and family["present_values"] == "I|II|III" and family["complete_I_II_III"] == "1",
        "GDT626 YKA II/III family exact",
    )
    _, atlas_ii_rows = read_tsv(G664_ATLAS)
    _, atlas_iii_rows = read_tsv(G665_ATLAS)
    atlas_ii = one(atlas_ii_rows, surface="ykain")
    atlas_iii = one(atlas_iii_rows, surface="ykaiin")
    audit.check(atlas_ii["composition"] == rule["exact_card_II"] and atlas_ii["working_default_de"] == "erhitze hiervon auf Stufe II", "YKA-II inherited working card exact")
    audit.check(atlas_iii["composition"] == rule["exact_card_III"] and atlas_iii["working_default_de"] == "erhitze hiervon auf Stufe III", "YKA-III inherited working card exact")
    reader_rows = guarded(
        G664_READERS, "locus", ["f86v5.24"],
        ["occurrence_id", "page", "locus", "ordinal", "surface", "reader_exact", "split_normalized", "all_present_exact", "zl3b_line", "it2a_line", "rf1b_line", "claim_boundary"],
    )
    rr = one(reader_rows, locus="f86v5.24", ordinal="3")
    audit.check(rr["surface"] == "ykain" and rr["reader_exact"] == rr["split_normalized"] == rr["all_present_exact"] == "1", "three-reader ykain occurrence exact")
    audit.check(rr["zl3b_line"] == rr["it2a_line"] == rr["rf1b_line"] == "oar aiin ykain okal kchody chckhy otaiin olkar otaiin", "three readers agree on complete f86v5.24 line")

    _, head_rules = read_tsv(G693_RULES)
    oar_rule = one(head_rules, surface="oar")
    audit.check(
        oar_rule["selected_gloss_de"] == "Anteil I des Ansatzes"
        and oar_rule["selected_formal_role"] == "R_INDEXED_MATERIAL_SHARE_SELECTOR"
        and oar_rule["selected_candidate"] == "share",
        "GDT693 oar material-share slot exact",
    )
    pair_rows = guarded(
        G693_PAIRS, "locus", ["f86v5.24"],
        ["locus", "token_ordinal", "surface", "v66_selected_gloss_de", "typed_role", "v66_selected_terminal_semantics"],
    )
    aiin_pair = one(pair_rows, token_ordinal="2", surface="aiin")
    audit.check(
        aiin_pair["v66_selected_gloss_de"] == "Menge III"
        and aiin_pair["typed_role"] == "typed_value_III"
        and aiin_pair["v66_selected_terminal_semantics"] == "N_HEAD_TYPED_GRADE_AMOUNT_OR_BATCH_VALUE",
        "aiin is a separate typed value-III register",
    )

    loci = [row["locus"] for row in specs]
    clause_rows = guarded(
        G695_CLAUSES, "locus", loci,
        ["page", "locus", "clause_id", "clause_type", "start_ordinal", "end_ordinal", "token_positions", "semantic_units", "surfaces", "action_ordinals", "verb_lemmas", "binding_ids", "v68_clause_de", "realization_rule", "content_word_delta"],
    )
    nominal = one(clause_rows, locus="f86v5.24", start_ordinal="1", end_ordinal="2")
    action = one(clause_rows, locus="f86v5.24", action_ordinals="3")
    audit.check(nominal["clause_type"] == "NOMINAL_BLOCK" and nominal["surfaces"] == "oar|aiin" and nominal["semantic_units"] == "2" and nominal["binding_ids"] == "NONE", "oar and aiin are two unbound semantic units")
    audit.check(action["clause_type"] == "ACTION_CLAUSE" and action["surfaces"] == "ykain" and action["verb_lemmas"] == "erhitzen", "candidate action is the separate ykain heat clause")

    ref_rows = guarded(
        G696_REFS, "locus", loci,
        ["reference_id", "locus", "reference_ordinal", "expected_surface", "expected_gloss_de", "decision", "linked_edge_ids", "source_ordinals", "target_ordinals", "scope_class", "provenance", "note"],
    )
    refs = {row["reference_id"]: row for row in ref_rows}
    audit.check(all(ref in refs for ref in ["R004", "R024", "R010", "R012", "R021"]), "all five upstream references recovered")
    for spec in specs:
        ref = refs[spec["reference_id"]]
        audit.check(ref["locus"] == spec["locus"] and ref["reference_ordinal"] == spec["action_ordinal"] and ref["expected_surface"] == spec["action_surface"], f"reference geometry exact {spec['reference_id']}")
        audit.check(ref["decision"] == spec["prior_decision"] and ref["source_ordinals"] == spec["prior_source_ordinals"], f"reference prior decision exact {spec['reference_id']}")

    rival_rows = guarded(
        G696_RIVALS, "locus", ["f26r.2", "f86v5.24"],
        ["rival_id", "locus", "source_ordinals", "target_action_ordinal", "decision", "plausible_reading_de"],
    )
    h002 = one(rival_rows, rival_id="H002")
    h007 = one(rival_rows, rival_id="H007")
    audit.check(h002["decision"] == h007["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED", "H002 and H007 remain held")
    audit.check(h007["source_ordinals"] == "1-2" and h007["target_action_ordinal"] == "3" and "in Menge III" in h007["plausible_reading_de"], "stronger whole-block H007 rival identified")

    edge_rows = guarded(
        G697_EDGES, "locus", ["f105v.1", "f86v6.25"],
        ["edge_id", "locus", "source_ordinals", "target_action_ordinal", "support_tier", "relation_class"],
    )
    c001 = one(edge_rows, edge_id="C001")
    c006 = one(edge_rows, edge_id="C006")
    audit.check(c001["locus"] == "f105v.1" and c001["source_ordinals"] == "3" and c001["target_action_ordinal"] == "4" and c001["support_tier"] == "A_STRONG_LICENSED", "C001 written-material prototype exact")
    audit.check(c006["locus"] == "f86v6.25" and c006["source_ordinals"] == "4" and c006["target_action_ordinal"] == "5" and c006["support_tier"] == "A_MINUS_EXPLICIT_OUTPUT", "C006 action-output prototype exact")

    v62_rows = guarded(
        G689_LINES, "locus", loci,
        ["page", "locus", "v62_action_ordinals", "v62_action_surfaces", "v62_verb_occurrences", "v62_provenance_status"],
    )
    audit.check(len(v62_rows) == 5 and {row["locus"] for row in v62_rows} == set(loci), "five action lines independently recovered")
    for spec in specs:
        row = one(v62_rows, locus=spec["locus"])
        pairs = dict(zip(row["v62_action_ordinals"].split("|"), row["v62_action_surfaces"].split("|")))
        audit.check(pairs[spec["action_ordinal"]] == spec["action_surface"], f"action ordinal exact {spec['case_id']}")

    # Complete V71 source and exact V72 projections.
    prior = json.loads(G698_RESULT.read_text(encoding="utf-8"))
    audit.check(prior["status"].startswith("PASS_V71_") and prior["basis"] == {"bound_spans": 3, "f84_access": 0, "f84r_access": 0, "lines": 51, "new_pages": 0, "pages": 36, "token_positions": 479, "v70_edges": 9, "v70_microrecords": 7}, "V71 scope contract exact")
    token_fields, token_rows = read_tsv(G698_TOKENS)
    line_fields, line_rows = read_tsv(G698_LINES)
    span_fields, span_rows = read_tsv(G698_SPANS)
    audit.check(len(token_rows) == 479 and len(line_rows) == 51 and len(span_rows) == 3, "479/51/3 source scope exact")
    audit.check(len({row["page"] for row in token_rows}) == 36, "36 current pages exact")
    audit.check(all(not row["page"].lower().startswith("f84") for row in token_rows + line_rows) and all(not row["locus"].lower().startswith("f84") for row in span_rows), "forbidden folios absent from complete source")

    by_pos = {(row["locus"], row["token_ordinal"]): row for row in token_rows}
    audit.check(len(by_pos) == 479, "all token positions unique")
    expected_tokens = {
        ("f105v.1", "4"): ("ykaiin", "erhitze hiervon auf Stufe III"),
        ("f86v5.24", "1"): ("oar", "Anteil I des Ansatzes"),
        ("f86v5.24", "2"): ("aiin", "Menge III"),
        ("f86v5.24", "3"): ("ykain", "erhitze hiervon auf Stufe II"),
        ("f86v6.25", "5"): ("ykaiin", "erhitze hiervon auf Stufe III"),
        ("f26r.2", "4"): ("ykecthey", "hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen"),
    }
    for position, expected in expected_tokens.items():
        row = by_pos[position]
        audit.check((row["surface"], row["v71_token_gloss_de"]) == expected, f"source token and gloss exact {position}")
    yka_scan = [
        (row["locus"], row["token_ordinal"], row["surface"])
        for row in token_rows
        if row["surface"] in {"ykain", "ykaiin"} and row["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL"
    ]
    audit.check(yka_scan == [("f105v.1", "4", "ykaiin"), ("f86v5.24", "3", "ykain"), ("f86v6.25", "5", "ykaiin")], "exhaustive current YKA action census exact")

    out_token_fields, out_tokens = read_tsv(TOKENS)
    out_line_fields, out_lines = read_tsv(LINES)
    out_span_fields, out_spans = read_tsv(SPANS)
    assert_projection(audit, token_fields, token_rows, out_token_fields, out_tokens, TOKEN_EXTRA, "token overlay")
    assert_projection(audit, line_fields, line_rows, out_line_fields, out_lines, LINE_EXTRA, "line overlay")
    assert_projection(audit, span_fields, span_rows, out_span_fields, out_spans, SPAN_EXTRA, "span overlay")
    audit.check(all(row["v72_token_gloss_de"] == row["v71_token_gloss_de"] and row["v72_word_delta"] == "0" and row["v72_status"] == STATUS for row in out_tokens), "all 479 token glosses byte-identical")
    audit.check(all(row["v72_clause_translation_de"] == row["v71_clause_translation_de"] and row["v72_word_delta"] == "0" and row["v72_status"] == STATUS for row in out_lines), "all 51 line readings byte-identical")
    audit.check(all(row["v72_selected_gloss_de"] == row["v71_selected_gloss_de"] and row["v72_byte_identical"] == "1" and row["v72_relation_change"] == "NONE" for row in out_spans), "all three bound spans byte-identical")
    overlay_by_pos = {(row["locus"], row["token_ordinal"]): row for row in out_tokens}
    audit.check(overlay_by_pos[("f86v5.24", "1")]["v72_relation_roles"] == "DONOR_MATERIAL:C010" and overlay_by_pos[("f86v5.24", "1")]["v72_edge_ids"] == "C010", "C010 donor marker only at oar#1")
    audit.check(overlay_by_pos[("f86v5.24", "2")]["v72_relation_roles"] == "UNBOUND_QUANTITY_REGISTER:R021" and overlay_by_pos[("f86v5.24", "2")]["v72_edge_ids"] == "NONE" and overlay_by_pos[("f86v5.24", "2")]["v72_reference_decision"] == "EXCLUDE_FROM_C010", "aiin#2 visibly unbound and excluded")
    audit.check(overlay_by_pos[("f86v5.24", "3")]["v72_relation_roles"] == "REFERENCE:C010|TARGET_ACTION:C010" and overlay_by_pos[("f86v5.24", "3")]["v72_edge_ids"] == "C010", "C010 target marker only at ykain#3")
    audit.check(sum(row["v72_edge_ids"] == "C010" for row in out_tokens) == 2 and all("C010" not in row["v72_edge_ids"] for row in out_tokens if (row["locus"], row["token_ordinal"]) not in {("f86v5.24", "1"), ("f86v5.24", "3")}), "no hidden C010 token export")
    audit.check(sum(row["v72_new_heat_edge_ids"] == "C010" for row in out_lines) == 1 and one(out_lines, locus="f86v5.24")["v72_new_heat_edge_ids"] == "C010", "C010 appears on one line only")

    # Compact decision artifacts.
    case_fields, case_rows = read_tsv(CASES)
    audit.check(case_fields == [*spec_fields, *CASE_EXTRA] and len(case_rows) == 5, "case artifact exact schema and size")
    for spec, row in zip(specs, case_rows):
        audit.check(all(row[field] == spec[field] for field in spec_fields), f"case specification prefix exact {spec['case_id']}")
        audit.check(row["observed_action_surface"] == spec["action_surface"] and row["observed_action_lemmas"] == spec["action_lemma"] and row["word_meaning_delta"] == "0" and row["status"] == STATUS, f"case observation exact {spec['case_id']}")
    candidate_row = one(case_rows, case_id="V72H005")
    audit.check(candidate_row["previous_clause_type"] == "NOMINAL_BLOCK" and candidate_row["previous_clause_start_ordinal"] == "1" and candidate_row["previous_clause_end_ordinal"] == "2" and candidate_row["previous_clause_semantic_units"] == "2" and candidate_row["previous_clause_binding_ids"] == "NONE", "candidate preceding block typed without binding")
    audit.check(candidate_row["typed_material_ordinals"] == "1" and candidate_row["quantity_register_ordinals"] == "2" and candidate_row["new_edge_id"] == "C010", "candidate assigns distinct material and quantity roles")
    audit.check(one(case_rows, case_id="V72H004")["written_action_object"] == "Krautdroge", "R012 written Krautdroge control preserved")

    _, yka_rows = read_tsv(YKA)
    audit.check([(row["locus"], row["token_ordinal"], row["surface"]) for row in yka_rows] == yka_scan, "published three-row YKA census exhaustive")
    audit.check([row["prior_edge_id"] for row in yka_rows] == ["C001", "NONE", "C006"] and [row["v72_edge_id"] for row in yka_rows] == ["NONE", "C010", "NONE"], "two replays and one new edge exact")
    audit.check(all(row["status"] == STATUS for row in yka_rows), "YKA census status exact")

    _, edge_out = read_tsv(EDGE)
    audit.check(len(edge_out) == 1, "exactly one new edge")
    e = edge_out[0]
    audit.check(e["edge_id"] == "C010" and e["locus"] == "f86v5.24" and e["source_ordinals"] == "1" and e["target_action_ordinal"] == "3" and e["excluded_ordinals"] == "2", "C010 geometry exact")
    audit.check(e["source_surface"] == "oar" and e["target_surface"] == "ykain" and e["support_tier"] == "B_WORKING_LOCAL" and e["portability"] == "OCCURRENCE_BOUND_ONLY", "C010 surface and ceiling exact")
    audit.check(e["prototype_edge_ids"] == "C001|C006" and e["reference_id"] == "R021" and e["prior_rival_id"] == "H007" and e["prior_rival_decision"] == "HELD_AS_RIVAL_NOT_ADMITTED", "C010 provenance exact")
    audit.check(e["working_reading_de"] == WORKING_READING and e["gdt388_score_ready"] == "0" and e["v71_word_delta"] == "0" and e["status"] == STATUS, "C010 reading, score and word ceiling exact")

    _, control_rows = read_tsv(CONTROLS)
    audit.check([(row["control_id"], row["case_id"], row["surface"], row["decision"]) for row in control_rows] == [
        ("X001", "V72H003", "yky", "KEEP_UNRESOLVED_MULTI_DONOR"),
        ("X002", "V72H004", "ykecthey", "KEEP_HELD_WRITTEN_OBJECT"),
        ("X003", "V72H005", "aiin", "EXCLUDE_FROM_C010"),
    ], "three exclusions exact")
    audit.check(one(control_rows, control_id="X003")["excluded_from_edge"] == "2" and "Nicht „in Menge III“" in one(control_rows, control_id="X003")["forbidden_inference"], "AIIN exclusion is explicit")

    # Official edge-intake replay must remain invalid and not score-ready.
    _, packet_rows = read_tsv(PACKET)
    audit.check(len(packet_rows) == 1 and packet_rows[0]["edge_id"] == "C010", "one-row GDT388 packet exact")
    audit.check(packet_rows[0]["formal_access_state"] == "FORMAL_ACCESSED" and packet_rows[0]["eligibility_status"] == "INELIGIBLE_WORKSHOP_EDGE" and packet_rows[0]["fold_assignment"] == "NONE", "packet exposes formal-selection ineligibility")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET.relative_to(ROOT))], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    audit.check(completed.returncode == 1 and not completed.stderr, "official GDT388 checker rejects packet cleanly")
    replay = json.loads(completed.stdout)
    expected_intake = {
        "capacity_gate_50_edges_5_folios": False, "discovery_edges": 0,
        "eligible_edges": 0, "eligible_folios": 0,
        "errors": ["edge row 2: formal access is not sealed"],
        "holdout_edges": 0, "holdout_gate": False, "mobile_edges": 0,
        "mobile_null_gate": False, "packet_rows": 1, "score_ready": False,
        "status": "INVALID_PACKET",
    }
    audit.check(replay == expected_intake, "official GDT388 failure payload exact")
    audit.check(json.loads(INTAKE.read_text(encoding="utf-8")) == expected_intake, "published GDT388 intake exact")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit.check(result["status"] == STATUS and result["question"] == QUESTION and result["claim_ceiling"] == CLAIM_CEILING, "RESULT identity and claim ceiling exact")
    audit.check(result["basis"] == {"bound_spans": 3, "current_yka_action_occurrences": 3, "f84_access": 0, "f84r_access": 0, "heat_reference_cases": 5, "lines": 51, "new_pages": 0, "pages": 36, "token_positions": 479}, "RESULT basis exact")
    audit.check(result["family"] == {"admitted_prototype_edges": ["C001", "C006"], "current_scope_II": 1, "current_scope_III": 2, "head": "yka", "inherited_aggregate_count_II": 11, "inherited_aggregate_count_III": 43, "surface_II": "ykain", "surface_III": "ykaiin"}, "RESULT family census exact")
    audit.check(result["decisions"] == {"excluded_from_edge": "f86v5.24#2", "excluded_quantity_registers": 1, "held_outside_family_controls": 2, "new_edge_id": "C010", "new_edge_source": "f86v5.24#1", "new_edge_target": "f86v5.24#3", "new_occurrence_bound_edges": 1, "old_h007_promoted": 0, "prototype_replays": 2, "working_reading_de": WORKING_READING}, "RESULT decisions exact")
    audit.check(result["freeze"] == {"bound_spans_byte_identical": 3, "changed_word_meanings": 0, "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0, "line_translations_byte_identical": 51, "new_word_meanings": 0, "token_glosses_byte_identical": 479}, "RESULT zero-word-delta freeze exact")
    audit.check(result["gdt388_edge_intake"] == expected_intake and result["next_gap"] == NEXT_GAP, "RESULT intake and corrected next gap exact")
    expected_result_inputs = {
        **INPUT_HASHES,
        str(CASE_SPEC.relative_to(ROOT)): CASE_SPEC_SHA256,
        str(RULE_SPEC.relative_to(ROOT)): RULE_SPEC_SHA256,
        RUN_RELATIVE: RUN_DECLARED_SHA256,
    }
    audit.check(result["inputs"] == expected_result_inputs, "RESULT binds all external inputs, specs and declared builder")
    expected_files = {name: sha256(path) for name, path in GENERATED.items()}
    audit.check(result["files"] == expected_files, "RESULT binds all generated artifacts")

    reader = READER.read_text(encoding="utf-8")
    audit.check(STATUS in reader and WORKING_READING in reader, "reader prints exact status and practical reading")
    audit.check("Only `oar#1 → ykain#3` is the new edge" in reader and "`aiin#2` remains a separate, unbound quantity register" in reader, "reader exposes the narrow edge and AIIN exclusion")
    audit.check("The stronger old H007 reading “in Menge III” is not admitted" in reader, "reader keeps H007 rejected")
    audit.check(all(case_id in reader for case_id in ["V72H001", "V72H002", "V72H003", "V72H004", "V72H005"]), "reader prints all five cases")
    audit.check("exactly three occurrences" in reader and "not score-ready" in reader and "479 token glosses, 51 inherited clause readings and 3 spans remain unchanged" in reader, "reader prints census, intake ceiling and freeze")
    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    flat_report = " ".join(report.split())
    audit.check("There is no second `oar` occurrence" in flat_report and "narrower H003 split" in flat_report and "Neither #3 nor #5 may become a donor" in flat_report, "report fixes the nonexistent-oar next route")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    audit.check(manifest["experiment_id"] == "GDT699" and manifest["slug"] == "v72_objectless_deictic_heat_frame", "manifest identity exact")
    audit.check(manifest["status"] == STATUS and manifest["question"] == QUESTION and manifest["claim_ceiling"] == CLAIM_CEILING, "manifest result contract exact")
    audit.check(manifest["dependencies"] == ["GDT388", "GDT626", "GDT664", "GDT665", "GDT689", "GDT693", "GDT695", "GDT696", "GDT697", "GDT698"], "manifest dependency chain exact")
    audit.check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest forbids sealed folios")
    audit.check(manifest["commands"] == {"run": "python3 " + RUN_RELATIVE, "validate": "python3 " + PREFIX + "src/validate.py"}, "manifest commands exact")
    audit.check(manifest["validation"] == {"artifact": PREFIX + "artifacts/VALIDATION.json", "status": "PASS"}, "manifest validation contract exact")
    audit.check(manifest["artifact_policy"]["max_inline_bytes"] == 5_000_000 and bool(manifest["artifact_policy"]["large_artifact_justification"]), "manifest justifies complete freeze artifacts")
    input_map = {entry["path"]: entry for entry in manifest["inputs"]}
    audit.check(set(input_map) == set(INPUT_HASHES), "manifest lists exactly the external inputs")
    for relative, digest in INPUT_HASHES.items():
        audit.check(input_map[relative]["sha256"] == digest and bool(input_map[relative]["role"]), f"manifest input binding exact {Path(relative).name}")
    output_map = {entry["path"]: entry for entry in manifest["outputs"]}
    audit.check(set(output_map) == EXPECTED_OUTPUTS, "manifest lists exact reproducible output tree")
    for relative in sorted(EXPECTED_OUTPUTS):
        entry = output_map[relative]
        digest = entry["sha256"]
        audit.check(bool(re.fullmatch(r"[0-9a-f]{64}", digest)) and bool(entry["role"]), f"manifest output binding syntax exact {Path(relative).name}")
        if relative == RUN_RELATIVE:
            audit.check(digest == RUN_DECLARED_SHA256, "manifest preserves declared builder hash without reading builder")
        elif relative.endswith("/VALIDATION.json"):
            pass  # rewritten below; repository preflight binds the stable result afterward
        else:
            audit.check(sha256(ROOT / relative) == digest, f"manifest output hash exact {relative}")

    payload = {
        "status": "PASS",
        "checks": len(audit.checks),
        "failed": 0,
        "summary": {
            "heat_reference_cases": 5,
            "yka_action_occurrences": 3,
            "prototype_replays": 2,
            "new_occurrence_bound_edges": 1,
            "held_controls": 2,
            "excluded_quantity_registers": 1,
            "old_h007_promoted": 0,
            "gdt388_score_ready": False,
            "tokens_frozen": 479,
            "lines_frozen": 51,
            "spans_frozen": 3,
            "new_word_meanings": 0,
            "changed_word_meanings": 0,
        },
        "audit": audit.checks,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
