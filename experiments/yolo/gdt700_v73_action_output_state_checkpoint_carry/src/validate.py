#!/usr/bin/env python3
"""Independent fail-closed validator for GDT700; never reads/imports run.py."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V73_10_ANA_WINDOWS__1_EXACT_STATE_ONLY_2_WORKING_STATE_LIKE_2_DEICTIC__"
    "1_UNIQUE_CANDIDATE_1_NEW_B_EDGE__C011_OCCURRENCE_BOUND__ZERO_WORD_DELTA"
)
QUESTION = (
    "Does the complete ten-case ACTION-to-one-token-NOMINAL-to-ACTION census support "
    "nominating one occurrence-bound B-tier hypothesis in which the result of "
    "f26r.2#4, whose written material patient is Krautdroge, remains the participant "
    "of deictic objectless #6 across exactly evidenced state-only #5, while the "
    "material-bearing f77v.7 countercase remains held?"
)
CLAIM = (
    "V73 adds one occurrence-bound B-tier working hypothesis from f26r.2#4 ykecthey "
    "to #6 ytedy: the Krautdroge written as #4's material patient is hypothesized to "
    "persist as its action result across the exactly evidenced state-only checkpoint "
    "#5 chedy. No output label is written at #4. The checkpoint is not a donor or "
    "edge node; H002, the old whole-span H003, H004 and H005 remain unpromoted and no "
    "carry reaches #8. This is an exploratory German relation reading, not a portable "
    "carry rule, confirmed word meaning, plaintext, language, or externally grounded edge."
)
MICRO = (
    "Hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von "
    "‚hiervon‘ offen]. [Zustandsvermerk ohne eigenen Materialträger: Mittlere "
    "Trockenstufe erreicht.] Die erhitzte Krautdroge bis zur Mittelstufe abkühlen "
    "und abschließen [C011-Arbeitshypothese]."
)
NEXT_GAP = (
    "Keep C011 occurrence-bound. Next compile the eleven cumulative relation edges "
    "into their exact connected components and practical microrecords, treating "
    "f26r.2#5 as hull-only rather than an edge node. Preserve C010, all prior "
    "boundaries and every held rival; add no edge or word meaning."
)
RUN_REL = "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/src/run.py"
RUN_SHA = "7bcd55681744e63f90fdd7e0eba66473965c39f73d175238fe442e3f1fda306b"
SPEC = SRC / "V73_10_ANA_CENSUS_SPEC.tsv"
SPEC_SHA = "013fa6e1e94a4379f2fc99fbad67d86b2af6f54cb279c1d78c0e814cfbadecea"

INPUT_HASHES = {
    "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json": "79cf873aa0f718d69d2af321ea8ebbae6c1db5fdef796ea099fe6b71045a9ac6",
    "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv": "57a357d1b7b3b022aa08fe5044a15dafb2541a1096dc4be7946a69c1f1985910",
    "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_175_CLAUSE_REALIZATIONS.tsv": "805c246ee7daf213329bec3e3d5f5a0ef32be0f6db6c6f790f69c74b6169d66b",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_17_RELATION_RIVALS.tsv": "8c97948f25f94f59e141b65230de23d2fcf75de0da926e20caaa46507d7916dd",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_27_REFERENCE_CENSUS.tsv": "f289027471897b4605b0821c6378985ff4d1fc03b37868feaa6e24704b95f6d2",
    "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts/V69_9_LOCAL_ACTION_EDGES.tsv": "06a5b402b2ddf3d956e4031f753e63e1ff32290ca522f5a8e72b8410b88af227",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv": "02be802b569c39354f5bff77786cc2143e8d9e344bae09d4c8d14562f37a6aac",
    "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/RESULT.json": "ed896b9ff7e5d308ed95744ad78990be925e8bdef36a676fb2ee59cbc7fbe3f7",
    "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_1_NEW_LOCAL_HEAT_EDGE.tsv": "c6fafffcc1f248dd40e212dfcb196c65e1e60e6d4fa9df6cca6d0d3785c7895a",
    "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_3_BOUND_SPAN_FREEZE.tsv": "5e04f534b1db45e67cd25e3711e7de1188c2ff14f6dbd316ae18c29074e6eeb7",
    "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_479_TOKEN_RELATION_OVERLAY.tsv": "1779d209a276a200a019f68c1e268a619b03de9c4365556b61bad66e4f62829f",
    "experiments/yolo/gdt699_v72_objectless_deictic_heat_frame/artifacts/V72_51_LINE_RELATION_OVERLAY.tsv": "aa0addb2f7aa31197aaced00268993dc4c723d339e61d3444fde4b5bfdb17737",
}


def ipart(fragment: str) -> Path:
    return ROOT / next(path for path in INPUT_HASHES if fragment in path)


G388, G687, G695 = ipart("gdt388_"), ipart("gdt687_"), ipart("gdt695_")
RIVALS, REFS, OLD_EDGES = ipart("V69_17_"), ipart("V69_27_"), ipart("V69_9_")
COVERAGE = ipart("gdt697_")
PRIOR_RESULT = ipart("gdt699_v72_objectless_deictic_heat_frame/artifacts/RESULT")
PRIOR_EDGE, PRIOR_SPANS = ipart("V72_1_"), ipart("V72_3_BOUND")
PRIOR_TOKENS, PRIOR_LINES = ipart("V72_479_"), ipart("V72_51_")

CENSUS, REGISTER = ART / "V73_10_ANA_CENSUS.tsv", ART / "V73_11_RELATION_EDGE_REGISTER.tsv"
EDGE, CONTRASTS = ART / "V73_1_NEW_LOCAL_CHECKPOINT_EDGE.tsv", ART / "V73_2_DEICTIC_ANA_CONTRASTS.tsv"
SPANS, CONTROLS = ART / "V73_3_BOUND_SPAN_FREEZE.tsv", ART / "V73_4_C011_BOUNDARY_CONTROLS.tsv"
TOKENS, LINES = ART / "V73_479_TOKEN_RELATION_OVERLAY.tsv", ART / "V73_51_LINE_RELATION_OVERLAY.tsv"
PACKET, INTAKE = ART / "V73_GDT388_EDGE_PACKET.tsv", ART / "V73_GDT388_EDGE_INTAKE.json"
READER, RESULT = ART / "GDT700_V73_STATE_CHECKPOINT_CARRY_READER.md", ART / "RESULT.json"

CENSUS_EXTRA = [
    "page", "source_clause_id", "source_clause_type", "checkpoint_clause_id",
    "checkpoint_clause_type", "checkpoint_token_positions", "checkpoint_verb_occurrences",
    "target_clause_id", "target_clause_type", "exact_state_only_checkpoint",
    "working_state_like_checkpoint", "deictic_target", "written_source_material",
    "unique_signature_match", "word_meaning_delta", "status",
]
TOKEN_EXTRA = ["v73_ana_window_ids", "v73_relation_roles", "v73_new_edge_ids", "v73_checkpoint_class", "v73_reference_decision", "v73_token_gloss_de", "v73_word_delta", "v73_status"]
LINE_EXTRA = ["v73_ana_window_ids", "v73_new_checkpoint_edge_ids", "v73_held_ana_controls", "v73_relation_annotations_de", "v73_working_microrecord_de", "v73_clause_translation_de", "v73_word_delta", "v73_status"]
SPAN_EXTRA = ["v73_selected_gloss_de", "v73_byte_identical", "v73_relation_change", "v73_status"]
GENERATED = {path.name: path for path in [READER, ART / "README.md", CENSUS, REGISTER, EDGE, CONTRASTS, SPANS, CONTROLS, TOKENS, LINES, INTAKE, PACKET]}
PREFIX = "experiments/yolo/gdt700_v73_action_output_state_checkpoint_carry/"
EXPECTED_OUTPUTS = {PREFIX + name for name in [
    "README.md", "METHOD.md", "REPORT.md", "src/V73_10_ANA_CENSUS_SPEC.tsv", "src/run.py", "src/validate.py",
    "artifacts/GDT700_V73_STATE_CHECKPOINT_CARRY_READER.md", "artifacts/README.md", "artifacts/RESULT.json",
    "artifacts/V73_10_ANA_CENSUS.tsv", "artifacts/V73_11_RELATION_EDGE_REGISTER.tsv",
    "artifacts/V73_1_NEW_LOCAL_CHECKPOINT_EDGE.tsv", "artifacts/V73_2_DEICTIC_ANA_CONTRASTS.tsv",
    "artifacts/V73_3_BOUND_SPAN_FREEZE.tsv", "artifacts/V73_4_C011_BOUNDARY_CONTROLS.tsv",
    "artifacts/V73_479_TOKEN_RELATION_OVERLAY.tsv", "artifacts/V73_51_LINE_RELATION_OVERLAY.tsv",
    "artifacts/V73_GDT388_EDGE_INTAKE.json", "artifacts/V73_GDT388_EDGE_PACKET.tsv", "artifacts/VALIDATION.json",
]}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, value: object, name: str) -> None:
        passed = bool(value)
        self.rows.append({"check": name, "pass": int(passed)})
        if not passed:
            raise AssertionError(name)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    if not fields or len(fields) != len(set(fields)):
        raise AssertionError(f"invalid TSV header: {path}")
    if any(None in row or set(row) != set(fields) or any(v is None for v in row.values()) for row in rows):
        raise AssertionError(f"malformed TSV: {path}")
    return fields, rows


def one(rows: Sequence[Mapping[str, str]], **wanted: str) -> Mapping[str, str]:
    hits = [row for row in rows if all(row.get(key) == value for key, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"expected one row for {wanted}, got {len(hits)}")
    return hits[0]


def guarded(path: Path, selector: str, allowed: Sequence[str], columns: Sequence[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)), "--selector", selector, "--columns", ",".join(columns), "--forbid-prefix", "f84"]
    for value in sorted(set(allowed)):
        command.extend(["--allow", value])
    done = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    stats = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats) != 1:
        raise AssertionError(f"guarded query failed: {path}: {done.stderr}")
    reader = csv.DictReader(io.StringIO(done.stdout), delimiter="\t")
    rows = list(reader)
    if list(reader.fieldnames or []) != list(columns):
        raise AssertionError(f"guarded projection mismatch: {path}")
    return rows, json.loads(stats[0].removeprefix("GUARD_STATS "))


def projection(sf: Sequence[str], sr: Sequence[Mapping[str, str]], of: Sequence[str], rows: Sequence[Mapping[str, str]], extra: Sequence[str]) -> bool:
    return list(of) == [*sf, *extra] and len(sr) == len(rows) and all(all(out[field] == source[field] for field in sf) for source, out in zip(sr, rows))


def main() -> int:
    a = Audit()
    a.check(digest(SPEC) == SPEC_SHA, "specification hash exact")
    for relative, expected in INPUT_HASHES.items():
        a.check(digest(ROOT / relative) == expected, f"upstream hash exact {Path(relative).name}")

    protocol = json.loads(G388.read_text(encoding="utf-8"))
    a.check(protocol["status"] == "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES" and protocol["schema"] == "GDT388_RESULT_V1" and protocol["acquisition"]["minimum_edges"] == 50 and protocol["acquisition"]["minimum_physical_folios"] == 5 and protocol["acquisition"]["scoring_authorized"] is False, "GDT388 capacity contract exact")
    prior = json.loads(PRIOR_RESULT.read_text(encoding="utf-8"))
    a.check(prior["status"].startswith("PASS_V72_") and prior["basis"] == {"bound_spans": 3, "current_yka_action_occurrences": 3, "f84_access": 0, "f84r_access": 0, "heat_reference_cases": 5, "lines": 51, "new_pages": 0, "pages": 36, "token_positions": 479}, "V72 scope contract exact")
    ptf, pt = tsv(PRIOR_TOKENS)
    plf, pl = tsv(PRIOR_LINES)
    psf, ps = tsv(PRIOR_SPANS)
    safe_loci = [row["locus"] for row in pl]
    a.check(len(pt) == 479 and len(pl) == len(set(safe_loci)) == 51 and len(ps) == 3 and len({row["page"] for row in pt}) == 36, "complete 479/51/3 scope")
    a.check(all(not locus.lower().startswith("f84") for locus in safe_loci), "all 51 selector loci are f84-free")

    sf, specs = tsv(SPEC)
    a.check(len(specs) == 10 and [row["window_id"] for row in specs] == [f"V73A{i:03d}" for i in range(1, 11)], "ten fixed case IDs exact")
    cols = ["page", "locus", "clause_id", "clause_type", "start_ordinal", "end_ordinal", "token_positions", "semantic_units", "surfaces", "action_ordinals", "verb_lemmas", "verb_occurrences", "binding_ids", "v68_clause_de", "realization_rule", "content_word_delta"]
    clauses, stats = guarded(G695, "locus", safe_loci, cols)
    a.check(stats == {"selected": 175, "skipped_forbidden": 0, "skipped_not_allowed": 0} and len(clauses) == 175, "all 175 clauses recovered through guarded query-tsv")
    a.check(all(row["content_word_delta"] == "0" for row in clauses), "175 clauses have zero word delta")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        grouped[row["locus"]].append(row)
    windows: list[tuple[dict[str, str], dict[str, str], dict[str, str]]] = []
    for locus in safe_loci:
        rows = sorted(grouped[locus], key=lambda row: int(row["clause_id"]))
        a.check([int(row["clause_id"]) for row in rows] == list(range(1, len(rows) + 1)), f"clause order exact {locus}")
        for source, middle, target in zip(rows, rows[1:], rows[2:]):
            if (source["clause_type"] == target["clause_type"] == "ACTION_CLAUSE" and middle["clause_type"] == "NOMINAL_BLOCK" and middle["token_positions"] == middle["semantic_units"] == "1" and middle["verb_occurrences"] == "0" and int(source["end_ordinal"]) + 1 == int(middle["start_ordinal"]) and int(middle["end_ordinal"]) + 1 == int(target["start_ordinal"])):
                windows.append((source, middle, target))
    a.check(len(windows) == 10, "exactly ten mechanical A-N-A windows")
    observed = {(source["locus"], source["start_ordinal"]): (source, middle, target) for source, middle, target in windows}
    a.check(len(observed) == 10, "ten unique window keys")
    derived_fields = {
        "source_start_ordinal": (0, "start_ordinal"), "source_end_ordinal": (0, "end_ordinal"),
        "source_surfaces": (0, "surfaces"), "source_verb_lemmas": (0, "verb_lemmas"), "source_working_de": (0, "v68_clause_de"),
        "checkpoint_ordinal": (1, "start_ordinal"), "checkpoint_surface": (1, "surfaces"), "checkpoint_working_de": (1, "v68_clause_de"),
        "target_start_ordinal": (2, "start_ordinal"), "target_end_ordinal": (2, "end_ordinal"), "target_surfaces": (2, "surfaces"),
        "target_verb_lemmas": (2, "verb_lemmas"), "target_working_de": (2, "v68_clause_de"),
    }
    for spec in specs:
        triple = observed[(spec["locus"], spec["source_start_ordinal"])]
        a.check(all(spec[field] == triple[index][source_field] for field, (index, source_field) in derived_fields.items()), f"window source exact {spec['window_id']}")
    a.check(sum(row["checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT" for row in specs) == 1 and sum(row["checkpoint_class"] == "WORKING_STATE_LIKE_NO_MATERIAL_HEAD" for row in specs) == 2 and sum(row["checkpoint_class"] == "MATERIAL_BEARING_NOMINAL" for row in specs) == 7 and sum(row["target_reference_class"] == "DEICTIC_OBJECTLESS" for row in specs) == 2, "1 exact state 2 working state-like 7 material and 2 deictic")
    candidates = [row for row in specs if row["checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT" and row["target_reference_class"] == "DEICTIC_OBJECTLESS" and row["source_material_class"] == "WRITTEN_MATERIAL_IN_ACTION"]
    a.check([row["window_id"] for row in candidates] == ["V73A004"], "one unique exact candidate")
    a.check([(row["window_id"], row["checkpoint_surface"]) for row in specs if row["checkpoint_class"] == "WORKING_STATE_LIKE_NO_MATERIAL_HEAD"] == [("V73A002", "keey"), ("V73A006", "kain")], "keey and kain remain working classifications only")

    cf, census = tsv(CENSUS)
    a.check(cf == [*sf, *CENSUS_EXTRA] and len(census) == 10, "census schema and size exact")
    for spec in specs:
        row = one(census, window_id=spec["window_id"])
        source, middle, target = observed[(spec["locus"], spec["source_start_ordinal"])]
        exact = int(spec["checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT")
        working = int(spec["checkpoint_class"] == "WORKING_STATE_LIKE_NO_MATERIAL_HEAD")
        deictic = int(spec["target_reference_class"] == "DEICTIC_OBJECTLESS")
        written = int(spec["source_material_class"] == "WRITTEN_MATERIAL_IN_ACTION")
        a.check(all(row[field] == spec[field] for field in sf) and row["page"] == source["page"] and row["source_clause_id"] == source["clause_id"] and row["checkpoint_clause_id"] == middle["clause_id"] and row["target_clause_id"] == target["clause_id"] and row["checkpoint_token_positions"] == middle["token_positions"] and row["checkpoint_verb_occurrences"] == middle["verb_occurrences"] and row["exact_state_only_checkpoint"] == str(exact) and row["working_state_like_checkpoint"] == str(working) and row["deictic_target"] == str(deictic) and row["written_source_material"] == str(written) and row["unique_signature_match"] == str(exact * deictic * written) and row["word_meaning_delta"] == "0" and row["status"] == STATUS, f"census row derived exact {spec['window_id']}")

    dispatch, _ = guarded(G687, "locus", ["f26r.2"], ["locus", "ordinal", "surface", "action_licensed_before", "dispatch_class", "v60_literal_gloss_de", "dy_contribution", "mechanical_flags_before", "mechanical_flags_after"])
    chedy = one(dispatch, ordinal="5", surface="chedy")
    a.check(chedy["action_licensed_before"] == "0" and chedy["dispatch_class"] == "NOMINAL_FINISHED_RESULT_STATE" and chedy["v60_literal_gloss_de"] == "fertige mittlere Trockenstufe" and chedy["dy_contribution"] == "FINISHED_ENDPOINT_NOT_NEW_VERB" and chedy["mechanical_flags_before"] == chedy["mechanical_flags_after"] == "STATE_ONLY_NO_OBJECT", "chedy exact state-only evidence before and after dispatch")

    rivals, _ = guarded(RIVALS, "locus", ["f26r.2", "f77v.7"], ["rival_id", "locus", "source_ordinals", "target_action_ordinal", "expected_source_surfaces", "expected_target_surface", "source_target_join_exact", "decision"])
    rivals = {row["rival_id"]: row for row in rivals if row["rival_id"] in {"H002", "H003", "H004", "H005"}}
    a.check(set(rivals) == {"H002", "H003", "H004", "H005"} and all(row["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED" and row["source_target_join_exact"] == "1" for row in rivals.values()), "H002-H005 exact and held")
    a.check([(rivals[key]["source_ordinals"], rivals[key]["target_action_ordinal"]) for key in ["H002", "H003", "H004", "H005"]] == [("3", "4"), ("4-5", "6"), ("2|4", "3"), ("4", "5")], "held rival geometry exact")
    refs, _ = guarded(REFS, "locus", ["f26r.2", "f77v.7"], ["reference_id", "locus", "reference_ordinal", "expected_surface", "decision", "linked_edge_ids", "source_ordinals", "target_ordinals", "exact_v68_match", "v69_resolution_scope"])
    refs = {row["reference_id"]: row for row in refs if row["reference_id"] in {"R012", "R013", "R016", "R017"}}
    a.check(set(refs) == {"R012", "R013", "R016", "R017"} and all(row["decision"] == "HOLD_OBJECT_RIVAL" and row["linked_edge_ids"] == "NONE" and row["exact_v68_match"] == "1" and row["v69_resolution_scope"] == "NO_NEW_OBJECT_EDGE" for row in refs.values()), "R012 R013 R016 R017 remain held")

    old, _ = guarded(OLD_EDGES, "locus", ["f80v.35", "f86v6.25"], ["edge_id", "locus", "source_start_ordinal", "source_end_ordinal", "target_action_ordinal", "relation_class", "support_tier", "edge_status"])
    c006, c008 = one(old, edge_id="C006"), one(old, edge_id="C008")
    a.check((c006["source_start_ordinal"], c006["target_action_ordinal"], c006["relation_class"], c006["support_tier"]) == ("4", "5", "MEASURED_SHARE_OUTPUT_CARRY", "A_MINUS_EXPLICIT_OUTPUT") and (c008["source_start_ordinal"], c008["target_action_ordinal"], c008["relation_class"], c008["support_tier"]) == ("3", "6", "REPEATED_QOL_DESTINATION_CARRY", "B_WORKING_LOCAL"), "C006 and C008 prototypes exact")
    _, coverage = tsv(COVERAGE)
    a.check(len(coverage) == 9 and [row["edge_id"] for row in coverage] == [f"C{i:03d}" for i in range(1, 10)], "GDT697 nine-edge coverage exact")
    c6c, c8c = one(coverage, edge_id="C006"), one(coverage, edge_id="C008")
    a.check(c6c["topology"] == "SERIAL_ACTION_OUTPUT_CHAIN" and c6c["edge_role_in_window"] == "SERIAL_CONSUMER" and c6c["shared_node_ordinals"] == "4" and c8c["topology"] == "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT" and c8c["edge_role_in_window"] == "COMMON_DESTINATION_REPEAT_WORKING" and c8c["shared_node_ordinals"] == "3", "C006 serial and C008 fanout topology unchanged")
    _, c10rows = tsv(PRIOR_EDGE)
    c010 = one(c10rows, edge_id="C010")
    a.check((c010["locus"], c010["source_ordinals"], c010["target_action_ordinal"], c010["excluded_ordinals"], c010["support_tier"], c010["portability"]) == ("f86v5.24", "1", "3", "2", "B_WORKING_LOCAL", "OCCURRENCE_BOUND_ONLY"), "C010 exact and occurrence-bound")

    otf, ot = tsv(TOKENS)
    olf, ol = tsv(LINES)
    osf, os = tsv(SPANS)
    a.check(projection(ptf, pt, otf, ot, TOKEN_EXTRA), "479-token V72 projection exact")
    a.check(projection(plf, pl, olf, ol, LINE_EXTRA), "51-line V72 projection exact")
    a.check(projection(psf, ps, osf, os, SPAN_EXTRA), "three-span V72 projection exact")
    a.check(all(row["v73_token_gloss_de"] == row["v72_token_gloss_de"] and row["v73_word_delta"] == "0" and row["v73_status"] == STATUS for row in ot), "479 token glosses byte-identical")
    a.check(all(row["v73_clause_translation_de"] == row["v72_clause_translation_de"] and row["v73_word_delta"] == "0" and row["v73_status"] == STATUS for row in ol), "51 line translations byte-identical")
    a.check(all(row["v73_selected_gloss_de"] == row["v72_selected_gloss_de"] and row["v73_byte_identical"] == "1" and row["v73_relation_change"] == "NONE" and row["v73_status"] == STATUS for row in os), "three spans byte-identical")
    positions = {(row["locus"], row["token_ordinal"]): row for row in ot}
    a.check(len(positions) == 479, "479 unique token positions")
    p3, p4, p5, p6, p7, p8 = [positions[("f26r.2", str(i))] for i in range(3, 9)]
    a.check(p4["v73_relation_roles"] == "INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:C011" and p4["v73_new_edge_ids"] == "C011", "#4 is inferred action-result donor, not written output label")
    a.check(p6["v73_relation_roles"] == "REFERENCE:C011|TARGET_ACTION:C011" and p6["v73_new_edge_ids"] == "C011", "#6 is sole C011 target")
    a.check(p5["v73_relation_roles"] == "STATE_ONLY_CHECKPOINT:C011" and p5["v73_new_edge_ids"] == "NONE" and p5["v73_checkpoint_class"] == "EXACT_STATE_ONLY_RESULT_CHECKPOINT", "#5 exact checkpoint is hull-only")
    a.check(p3["v73_new_edge_ids"] == p5["v73_new_edge_ids"] == p8["v73_new_edge_ids"] == "NONE" and p3["v73_reference_decision"] == "KEEP_H002_HELD" and p8["v73_reference_decision"] == "STOP_C011_BEFORE_ORDINAL_8", "no edge export to #3 #5 #8")
    a.check(p7["v73_new_edge_ids"] == "NONE" and p7["v73_relation_roles"] == "STRUCTURAL_CLAUSE_STOP:C011", "free dy #7 is structural only")
    a.check([(row["locus"], row["token_ordinal"]) for row in ot if row["v73_new_edge_ids"] == "C011"] == [("f26r.2", "4"), ("f26r.2", "6")], "C011 appears on exactly two edge nodes")
    a.check(sum(row["v73_new_checkpoint_edge_ids"] == "C011" for row in ol) == 1 and one(ol, locus="f26r.2")["v73_new_checkpoint_edge_ids"] == "C011", "C011 occurs on one line only")

    _, contrasts = tsv(CONTRASTS)
    a.check([(row["window_id"], row["locus"], row["decision"]) for row in contrasts] == [("V73A004", "f26r.2", "ADMIT_C011_OCCURRENCE_BOUND"), ("V73A008", "f77v.7", "KEEP_HELD_MATERIAL_COMPETITOR")] and contrasts[0]["source_material_role"] == "INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT:Krautdroge" and contrasts[1]["checkpoint_role"] == "COMPETING_WRITTEN_MATERIAL:getrocknete_Wurzel", "two deictic contrasts exact")
    _, controls = tsv(CONTROLS)
    a.check([(row["token_ordinal"], row["edge_membership"], row["decision"]) for row in controls] == [("3", "NONE", "KEEP_H002_HELD"), ("5", "HULL_ONLY_NOT_NODE", "EXCLUDE_FROM_C011_SOURCE_AND_DONOR"), ("7", "NONE", "KEEP_STRUCTURAL_ONLY"), ("8", "NONE", "STOP_C011_BEFORE_ORDINAL_8")], "four boundary controls exact")
    _, edge_rows = tsv(EDGE)
    a.check(len(edge_rows) == 1, "one new edge row")
    c011 = edge_rows[0]
    a.check((c011["edge_id"], c011["locus"], c011["support_tier"], c011["relation_class"], c011["topology"], c011["window_hull_ordinals"], c011["edge_node_ordinals"], c011["source_ordinals"], c011["checkpoint_ordinals"], c011["target_action_ordinal"], c011["structural_closure_ordinals"], c011["excluded_ordinals"]) == ("C011", "f26r.2", "B_WORKING_LOCAL", "ACTION_OUTPUT_ACROSS_ONE_STATE_CHECKPOINT", "SINGLE_ACTION_OUTPUT_CARRY_ACROSS_ONE_STATE_ONLY_CHECKPOINT", "4-6", "4|6", "4", "5", "6", "7", "3|5|8"), "C011 minimal hull and graph exact")
    a.check(c011["source_output_label_de"] == "C011-Hypothese: die erhitzte Krautdroge" and c011["prototype_edge_id"] == "C006" and c011["nonadjacent_b_precedent_edge_id"] == "C008" and c011["prior_rival_id"] == "H003" and c011["prior_rival_source_ordinals"] == "4-5" and c011["working_microrecord_de"] == MICRO and c011["unresolved_reference"] == "f26r.2#4:FIRST_HIERVON_UNBOUND" and c011["portability"] == "OCCURRENCE_BOUND_ONLY" and c011["gdt388_score_ready"] == "0" and c011["final_result_status"] == "UNNAMED_NO_OUTGOING_EDGE" and c011["v72_word_delta"] == "0" and c011["status"] == STATUS, "C011 hypothesis provenance and final-result ceiling exact")

    _, register = tsv(REGISTER)
    a.check(len(register) == 11 and [row["edge_id"] for row in register] == [f"C{i:03d}" for i in range(1, 12)], "C001-C011 register complete")
    for old_edge in coverage:
        row = one(register, edge_id=old_edge["edge_id"])
        a.check(all(row[field] == old_edge[field] for field in ["locus", "source_ordinals", "target_action_ordinal", "support_tier", "relation_class"]) and row["origin"] == "GDT697_INHERITED" and row["v73_change"] == "NONE", f"inherited edge unchanged {old_edge['edge_id']}")
    r10, r11 = one(register, edge_id="C010"), one(register, edge_id="C011")
    a.check(all(r10[field] == c010[field] for field in ["locus", "source_ordinals", "target_action_ordinal", "support_tier", "relation_class"]) and r10["v73_change"] == "NONE", "C010 register unchanged")
    a.check(r11["locus"] == "f26r.2" and r11["source_ordinals"] == "4" and r11["target_action_ordinal"] == "6" and r11["v73_change"] == "ADD_ONE_EDGE" and sum(row["v73_change"] == "ADD_ONE_EDGE" for row in register) == 1 and sum(row["locus"] == "f26r.2" for row in register) == 1, "only C011 added and no outgoing final-result edge")

    _, packet = tsv(PACKET)
    a.check(len(packet) == 1 and packet[0]["edge_id"] == "C011" and packet[0]["pivot_locus"] == "f26r.2@4" and packet[0]["target_locus"] == "f26r.2@6" and packet[0]["formal_access_state"] == "FORMAL_ACCESSED" and packet[0]["eligibility_status"] == "INELIGIBLE_WORKSHOP_EDGE" and packet[0]["fold_assignment"] == "NONE" and packet[0]["geometry_only_selection"] == "FALSE", "GDT388 packet exposes formal-access ineligibility")
    done = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET.relative_to(ROOT))], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    expected_intake = {"capacity_gate_50_edges_5_folios": False, "discovery_edges": 0, "eligible_edges": 0, "eligible_folios": 0, "errors": ["edge row 2: formal access is not sealed"], "holdout_edges": 0, "holdout_gate": False, "mobile_edges": 0, "mobile_null_gate": False, "packet_rows": 1, "score_ready": False, "status": "INVALID_PACKET"}
    a.check(done.returncode == 1 and not done.stderr and json.loads(done.stdout) == expected_intake and json.loads(INTAKE.read_text(encoding="utf-8")) == expected_intake, "official and published GDT388 INVALID_PACKET exact")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    a.check(result["status"] == STATUS and result["question"] == QUESTION and result["claim_ceiling"] == CLAIM, "RESULT identity and ceiling exact")
    a.check(result["basis"] == {"ana_windows": 10, "bound_spans": 3, "census_loci": 51, "deictic_targets": 2, "exact_state_only_checkpoints": 1, "f84_access": 0, "f84r_access": 0, "lines": 51, "material_bearing_checkpoints": 7, "new_pages": 0, "pages": 36, "source_clauses": 175, "token_positions": 479, "working_state_like_checkpoints": 2}, "RESULT basis exact")
    a.check(result["decision"] == {"census_exclusions": 9, "cumulative_relation_edges": 11, "excluded_ordinals": [3, 5, 8], "held_deictic_countercase": "f77v.7#3-5", "new_edge_checkpoint_hull_only": "f26r.2#5", "new_edge_id": "C011", "new_edge_source": "f26r.2#4", "new_edge_target": "f26r.2#6", "new_occurrence_bound_edges": 1, "structural_closure_ordinal": 7, "unique_signature_matches": 1, "working_microrecord_de": MICRO}, "RESULT graph decision exact")
    a.check(result["freeze"] == {"bound_spans_byte_identical": 3, "changed_word_meanings": 0, "content_word_additions": 0, "content_word_deletions": 0, "content_word_reorders": 0, "line_translations_byte_identical": 51, "new_word_meanings": 0, "token_glosses_byte_identical": 479} and result["gdt388_edge_intake"] == expected_intake and result["next_gap"] == NEXT_GAP, "RESULT freeze intake and route exact")
    expected_inputs = {**INPUT_HASHES, str(SPEC.relative_to(ROOT)): SPEC_SHA, RUN_REL: RUN_SHA}
    a.check(result["inputs"] == expected_inputs, "RESULT binds inputs spec and declared builder")
    a.check(result["files"] == {name: digest(path) for name, path in GENERATED.items()}, "RESULT binds generated artifacts")

    reader = READER.read_text(encoding="utf-8")
    a.check(STATUS in reader and MICRO in reader and all(f"V73A{i:03d}" in reader for i in range(1, 11)), "reader contains status microrecord and ten cases")
    a.check("INFERRED_ACTION_OUTPUT_OF_WRITTEN_PATIENT" in reader and "no output label is written at #4" in reader and "hull-only and never an edge node" in reader and "stops before #8" in reader, "reader states inferred output and minimal boundary")
    a.check("1 exactly evidenced state-only checkpoint, 2 working state-like blocks, 7 material-bearing checkpoints and 2 deictic targets" in reader and "H004 and H005 therefore remain held" in reader and "invalid/not score-ready" in reader and "All 479 token glosses, 51 inherited line readings and 3 bound spans remain byte-identical" in reader, "reader states evidence tiers controls intake and freeze")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    a.check(manifest["experiment_id"] == "GDT700" and manifest["slug"] == "v73_action_output_state_checkpoint_carry", "manifest identity exact")
    a.check(manifest["status"] == STATUS and manifest["question"] == QUESTION and manifest["claim_ceiling"] == CLAIM, "manifest result contract exact")
    a.check(manifest["dependencies"] == ["GDT388", "GDT687", "GDT695", "GDT696", "GDT697", "GDT699"] and manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest dependencies and seals exact")
    a.check(manifest["commands"] == {"run": "python3 " + RUN_REL, "validate": "python3 " + PREFIX + "src/validate.py"} and manifest["validation"] == {"artifact": PREFIX + "artifacts/VALIDATION.json", "status": "PASS"}, "manifest commands and validation exact")
    a.check(manifest["artifact_policy"]["max_inline_bytes"] == 5_000_000 and bool(manifest["artifact_policy"]["large_artifact_justification"]), "manifest complete-freeze justification present")
    inputs = {entry["path"]: entry for entry in manifest["inputs"]}
    a.check(set(inputs) == set(INPUT_HASHES), "manifest exact external input set")
    for relative, expected in INPUT_HASHES.items():
        a.check(inputs[relative]["sha256"] == expected and bool(inputs[relative]["role"]), f"manifest input binding exact {Path(relative).name}")
    outputs = {entry["path"]: entry for entry in manifest["outputs"]}
    a.check(set(outputs) == EXPECTED_OUTPUTS, "manifest exact output tree")
    for relative in sorted(EXPECTED_OUTPUTS):
        entry, path = outputs[relative], ROOT / relative
        a.check(bool(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])) and bool(entry["role"]), f"manifest output syntax exact {Path(relative).name}")
        if relative == RUN_REL:
            a.check(entry["sha256"] == RUN_SHA, "manifest builder digest matches external declaration")
        elif not relative.endswith("/VALIDATION.json"):
            a.check(digest(path) == entry["sha256"], f"manifest output digest exact {relative}")

    payload = {
        "status": "PASS", "checks": len(a.rows), "failed": 0,
        "summary": {"clauses_guarded": 175, "census_loci": 51, "ana_windows": 10, "exact_state_only_checkpoints": 1, "working_state_like_checkpoints": 2, "material_bearing_checkpoints": 7, "deictic_targets": 2, "unique_signature_matches": 1, "new_occurrence_bound_edges": 1, "cumulative_relation_edges": 11, "c011_edge_nodes": 2, "c011_hull_only_positions": 1, "gdt388_score_ready": False, "tokens_frozen": 479, "lines_frozen": 51, "spans_frozen": 3, "new_word_meanings": 0, "changed_word_meanings": 0},
        "audit": a.rows,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
