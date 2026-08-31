#!/usr/bin/env python3
"""Independent validator for the GDT693 V66 selected-share renderer."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament"
SRC = BASE / "src"
ART = BASE / "artifacts"
RUN_PATH = SRC / "run.py"
RESULT_PATH = ART / "RESULT.json"

G692 = ROOT / "experiments/yolo/gdt692_o_q_fraction_sister_compositor"
V65_TOKENS = G692 / "artifacts/V65_479_TOKEN_READER.tsv"
V65_LINES = G692 / "artifacts/V65_51_LINE_COMPOSITIONAL_READER.tsv"
V65_TARGETS = G692 / "artifacts/V64_41_FRACTION_SISTER_OCCURRENCES.tsv"
V65_VERBS = G692 / "artifacts/V65_113_VERB_PRESERVATION.tsv"

SURFACE_SOURCE = SRC / "V66_SURFACE_HEAD_CANDIDATES.tsv"
CONTROL_SOURCE = SRC / "V66_AR_OR_CONTROL_CANDIDATES.tsv"
SPAN_SOURCE = SRC / "V66_BOUND_SPAN_CANDIDATES.tsv"
PAIR_SOURCE = SRC / "V66_R_N_TERMINAL_PAIR_RULES.tsv"
MODEL_SOURCE = SRC / "V66_SELECTED_HEAD_MODEL.tsv"
SELECTION_SOURCE = SRC / "V66_HEAD_SELECTION.tsv"
RIVAL_SOURCE = SRC / "V66_SELECTED_PRODUCT_RIVALS.tsv"
OVERRIDE_SOURCE = SRC / "V66_SELECTED_TOKEN_OVERRIDES.tsv"

TARGET_ART = ART / "V66_41_TARGET_FOUR_HEAD_RENDERERS.tsv"
CONTROL_ART = ART / "V66_22_AR_OR_CONTROL_OCCURRENCES.tsv"
TOKEN_ART = ART / "V66_479_TOKEN_FOUR_HEAD_RENDERERS.tsv"
LINE_ART = ART / "V66_51_LINE_FOUR_HEAD_READERS.tsv"
VERB_ART = ART / "V66_113_VERB_FOUR_HEAD_PRESERVATION.tsv"
CENSUS_ART = ART / "V66_FOUR_HEAD_CENSUS.tsv"
PRIOR_ART = ART / "V66_GDT654_NINE_AR_OR_PAIR_PRIORS.tsv"
PAIR_ART = ART / "V66_30_R_N_TERMINAL_PAIR_OCCURRENCES.tsv"

SELECTED_TOKEN_ART = ART / "V66_479_TOKEN_SELECTED_SHARE_READER.tsv"
REVISION_ART = ART / "V66_57_SELECTED_REVISIONS.tsv"
SELECTED_LINE_ART = ART / "V66_51_LINE_SELECTED_SHARE_READER.tsv"
SELECTED_SPAN_ART = ART / "V66_2_SELECTED_BOUND_SPANS.tsv"
SELECTED_RIVAL_ART = ART / "V66_6_SELECTED_PRODUCT_RIVALS.tsv"
SELECTED_SURFACE_ART = ART / "V66_16_SELECTED_SURFACE_RULES.tsv"
SELECTED_MODEL_ART = ART / "V66_9_SELECTED_HEAD_MODEL.tsv"
SELECTION_ART = ART / "V66_4_HEAD_SELECTION.tsv"
SELECTED_VERB_ART = ART / "V66_113_SELECTED_VERB_PRESERVATION.tsv"
RESIDUAL_ART = ART / "V66_22_RESIDUAL_FRACTION_BEARING_OCCURRENCES.tsv"

STATUS = "PASS_V66_SCOPED_INDEXED_R_SELECTOR__55_HEAD_PLUS_2_READER_REVISIONS__6_R_N_PAIRS__OR_PORTION_PRESERVED"
CANDIDATES = ("fraction", "share", "stage", "class")
PURE_OR_ROLES = {"OR_PORTION", "OR_PORTION_ACTION"}
AR_BEARING_ROLES = {"AR_HEAD", "AR_PLUS_OR", "OR_PLUS_AR"}
EXPECTED_CONTROL_COUNTS = {
    "or": 5,
    "kor": 1,
    "lor": 1,
    "tar": 2,
    "sar": 1,
    "sair": 1,
    "dar": 5,
    "dair": 3,
    "qodor": 1,
    "aror": 1,
    "oroiir": 1,
}
EXPECTED_FILES = {
    "GDT693_V66_FOUR_HEAD_READER.md",
    "GDT693_V66_SELECTED_SHARE_READER.md",
    "V66_113_SELECTED_VERB_PRESERVATION.tsv",
    "V66_113_VERB_FOUR_HEAD_PRESERVATION.tsv",
    "V66_16_SELECTED_SURFACE_RULES.tsv",
    "V66_22_AR_OR_CONTROL_OCCURRENCES.tsv",
    "V66_22_RESIDUAL_FRACTION_BEARING_OCCURRENCES.tsv",
    "V66_2_SELECTED_BOUND_SPANS.tsv",
    "V66_30_R_N_TERMINAL_PAIR_OCCURRENCES.tsv",
    "V66_41_TARGET_FOUR_HEAD_RENDERERS.tsv",
    "V66_479_TOKEN_FOUR_HEAD_RENDERERS.tsv",
    "V66_479_TOKEN_SELECTED_SHARE_READER.tsv",
    "V66_4_HEAD_SELECTION.tsv",
    "V66_51_LINE_FOUR_HEAD_READERS.tsv",
    "V66_51_LINE_SELECTED_SHARE_READER.tsv",
    "V66_57_SELECTED_REVISIONS.tsv",
    "V66_6_SELECTED_PRODUCT_RIVALS.tsv",
    "V66_9_SELECTED_HEAD_MODEL.tsv",
    "V66_FOUR_HEAD_CENSUS.tsv",
    "V66_GDT654_NINE_AR_OR_PAIR_PRIORS.tsv",
}
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(glosses: list[str]) -> str:
    text = ""
    for gloss in glosses:
        if gloss in {";", "."}:
            text = text.rstrip(" ,;.") + gloss
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:] if text else text


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def root_count(text: str, root: str) -> int:
    return sum(root in word.casefold() for word in words(text))


def assert_no_f84(rows: list[dict[str, str]]) -> None:
    for row in rows:
        for field in ("page", "locus"):
            value = row.get(field, "").casefold()
            assert not value.startswith("f84"), (field, value)


def keyed(rows: list[dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    output: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        key = (row["locus"], int(row["token_ordinal"]))
        assert key not in output, key
        output[key] = row
    return output


def keyed_verbs(rows: list[dict[str, str]]) -> dict[tuple[str, int, str], dict[str, str]]:
    output: dict[tuple[str, int, str], dict[str, str]] = {}
    for row in rows:
        key = (row["locus"], int(row["token_ordinal"]), row["verb_de"])
        assert key not in output, key
        output[key] = row
    return output


def main() -> int:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    checks: list[str] = []

    assert result["status"] == STATUS
    checks.append("selected_share_result_status")

    assert set(result["files"]) == EXPECTED_FILES
    for relative, expected in result["inputs"].items():
        path = ROOT / relative
        assert path.is_file() and sha256(path) == expected, relative
    for name, expected in result["files"].items():
        path = ART / name
        assert path.is_file() and sha256(path) == expected, name
    checks.append("all_declared_input_and_output_hashes")

    surface_source = read_tsv(SURFACE_SOURCE)
    control_source = read_tsv(CONTROL_SOURCE)
    span_source = read_tsv(SPAN_SOURCE)
    pair_source = read_tsv(PAIR_SOURCE)
    model_source = read_tsv(MODEL_SOURCE)
    selection_source = read_tsv(SELECTION_SOURCE)
    rival_source = read_tsv(RIVAL_SOURCE)
    override_source = read_tsv(OVERRIDE_SOURCE)
    v65_tokens = read_tsv(V65_TOKENS)
    v65_lines = read_tsv(V65_LINES)
    v65_targets = read_tsv(V65_TARGETS)
    v65_verbs = read_tsv(V65_VERBS)

    targets = read_tsv(TARGET_ART)
    controls = read_tsv(CONTROL_ART)
    tokens = read_tsv(TOKEN_ART)
    lines = read_tsv(LINE_ART)
    verbs = read_tsv(VERB_ART)
    census = read_tsv(CENSUS_ART)
    priors = read_tsv(PRIOR_ART)
    pairs = read_tsv(PAIR_ART)
    selected_tokens = read_tsv(SELECTED_TOKEN_ART)
    revisions = read_tsv(REVISION_ART)
    selected_lines = read_tsv(SELECTED_LINE_ART)
    selected_spans = read_tsv(SELECTED_SPAN_ART)
    selected_rivals = read_tsv(SELECTED_RIVAL_ART)
    selected_surfaces = read_tsv(SELECTED_SURFACE_ART)
    selected_model = read_tsv(SELECTED_MODEL_ART)
    selection = read_tsv(SELECTION_ART)
    selected_verbs = read_tsv(SELECTED_VERB_ART)
    residuals = read_tsv(RESIDUAL_ART)

    assert len(surface_source) == len(selected_surfaces) == 16
    assert len(control_source) == 11 and len(controls) == 22
    assert len(span_source) == len(selected_spans) == 2
    assert len(pair_source) == 6 and len(pairs) == 30
    assert len(model_source) == len(selected_model) == 9
    assert len(selection_source) == len(selection) == 4
    assert len(rival_source) == len(selected_rivals) == 6
    assert len(override_source) == 2
    assert len(v65_tokens) == len(tokens) == len(selected_tokens) == 479
    assert len(v65_lines) == len(lines) == len(selected_lines) == 51
    assert len(v65_targets) == len(targets) == 41
    assert len(v65_verbs) == len(verbs) == len(selected_verbs) == 113
    assert len(revisions) == 57 and len(residuals) == 22
    assert len(census) == 4 and len(priors) == 9
    checks.append("populations_51_479_41_22_55_plus_2_2_6_30_9_and_113")

    expected_basis = {
        "lines": 51,
        "token_positions": 479,
        "pages": 36,
        "target_occurrences": 41,
        "control_occurrences": 22,
        "ar_bearing_control_occurrences": 14,
        "or_bearing_control_occurrences": 10,
        "selected_revisions": 57,
        "selected_head_revisions": 55,
        "selected_reader_repairs": 2,
        "selected_changed_lines": 31,
        "bound_spans": 2,
        "product_rivals": 6,
        "new_pages": 0,
        "f84_access": 0,
        "f84r_access": 0,
    }
    assert result["basis"] == expected_basis
    assert result["selected_changes"] == {
        "total": 57,
        "head_total": 55,
        "targets": 41,
        "ar_controls": 14,
        "neutral_grammar_repairs": 1,
        "bound_carry_token_repairs": 1,
        "or_bearing_controls_preserving_portion": 10,
        "bound_spans": 2,
        "local_product_rivals": 6,
    }
    for rowset in (
        v65_tokens, v65_lines, v65_targets, v65_verbs, targets, controls,
        tokens, lines, verbs, pairs, selected_tokens, revisions, selected_lines,
        selected_rivals, selected_verbs, residuals,
    ):
        assert_no_f84(rowset)
    assert len({row["page"] for row in selected_tokens}) == 36
    checks.append("same_36_page_admitted_deck_no_f84_or_f84r")

    assert MODEL_SOURCE.read_bytes() == SELECTED_MODEL_ART.read_bytes()
    assert SELECTION_SOURCE.read_bytes() == SELECTION_ART.read_bytes()
    selection_by_candidate = {row["candidate"]: row for row in selection}
    assert set(selection_by_candidate) == set(CANDIDATES)
    assert {candidate: row["decision"] for candidate, row in selection_by_candidate.items()} == result["selection_decisions"]
    assert selection_by_candidate["share"]["decision"] == "SELECTED"
    assert selection_by_candidate["fraction"]["decision"] == "RUNNER_UP"
    assert selection_by_candidate["stage"]["decision"] == "REJECTED_AS_GLOBAL"
    assert selection_by_candidate["class"]["decision"] == "LIVE_RIVAL"
    assert result["selected"]["candidate"] == "share"
    assert result["selected"]["running_head_de"] == "Anteil"
    checks.append("share_is_unique_selected_head")

    model_by_id = {row["model_id"]: row for row in selected_model}
    assert set(model_by_id) == {f"S{number:03d}" for number in range(1, 10)}
    assert {row["formal_role"] for row in selected_model} == {
        "INDEX", "R_SELECTOR", "N_VALUE", "PORTION", "PREPARATION_FRAME",
        "QO_FRAME", "QUALITY_TAG", "MEASURE_ACTION", "WOOD_HEAD",
    }
    assert model_by_id["S001"]["visible_pattern"] == "A+I^(level-1)"
    assert model_by_id["S002"]["visible_pattern"] == "A+I^(level-1)+R"
    assert "Stoffanteil" in model_by_id["S002"]["selected_value_de"]
    assert model_by_id["S003"]["visible_pattern"] == "A+I^(level-1)+N"
    assert model_by_id["S004"]["visible_pattern"] == "OR"
    assert "not decomposed as O+R" in model_by_id["S004"]["bounded_scope"]
    checks.append("nine_piece_selected_semantic_model")

    v65_token_by_key = keyed(v65_tokens)
    token_by_key = keyed(tokens)
    selected_token_by_key = keyed(selected_tokens)
    target_by_key = keyed(targets)
    control_by_key = keyed(controls)
    revision_by_key = keyed(revisions)
    assert set(v65_token_by_key) == set(token_by_key) == set(selected_token_by_key)
    assert set(target_by_key).isdisjoint(control_by_key)
    override_by_key = {
        (row["locus"], int(row["token_ordinal"])): row for row in override_source
    }
    assert len(override_by_key) == 2
    assert set(override_by_key) == {("f105r.2", 6), ("f86v3.13", 5)}

    changed_keys: set[tuple[str, int]] = set()
    for key, row in selected_token_by_key.items():
        base = v65_token_by_key[key]
        tournament = token_by_key[key]
        assert row["page"] == base["page"] and row["surface"] == base["surface"]
        assert row["v65_token_gloss_de"] == base["v65_token_gloss_de"]
        assert row["v66_fraction_de"] == base["v65_token_gloss_de"]
        assert int(row["v66_fraction_changed"]) == 0
        assert row["v66_selected_candidate"] == "share"
        assert row["v66_share_de"] == tournament["v66_share_de"]
        override = override_by_key.get(key)
        if override:
            assert row["surface"] == override["surface"]
            assert row["v66_share_de"] == override["expected_share_de"]
            assert row["v66_selected_gloss_de"] == override["selected_de"]
            assert row["v66_selected_override_id"] == override["override_id"]
            assert row["v66_selected_semantic_role"] == override["semantic_role"]
        else:
            assert row["v66_selected_gloss_de"] == row["v66_share_de"]
            assert row["v66_selected_override_id"] == "NONE"
        changed = int(row["v66_selected_gloss_de"] != base["v65_token_gloss_de"])
        assert int(row["v66_selected_changed"]) == changed
        if not override:
            assert changed == int(row["v66_share_changed"])
        if changed:
            changed_keys.add(key)
    assert len(changed_keys) == 57
    assert changed_keys == set(revision_by_key)
    checks.append("fraction_equals_v65__selected_equals_share_except_two_sealed_repairs")

    assert Counter(row["surface"] for row in controls) == EXPECTED_CONTROL_COUNTS
    ar_control_keys = {key for key, row in control_by_key.items() if row["role"] in AR_BEARING_ROLES}
    pure_or_keys = {key for key, row in control_by_key.items() if row["role"] in PURE_OR_ROLES}
    or_bearing_keys = {key for key, row in control_by_key.items() if "OR" in row["role"]}
    assert len(ar_control_keys) == 14 and len(pure_or_keys) == 8 and len(or_bearing_keys) == 10
    assert changed_keys == set(target_by_key) | ar_control_keys | set(override_by_key)
    for key in pure_or_keys:
        row = control_by_key[key]
        assert row["share_de"] == row["fraction_de"] == row["v65_gloss_de"]
    for key in or_bearing_keys:
        row = control_by_key[key]
        selected_gloss = selected_token_by_key[key]["v66_selected_gloss_de"]
        assert root_count(selected_gloss, "portion") == root_count(row["v65_gloss_de"], "portion") == 1
    assert selected_token_by_key[("f105r.2", 6)]["v66_selected_gloss_de"] == "eine Portion des Ansatzes abmessen"
    assert selected_token_by_key[("f86v3.13", 5)]["v66_selected_gloss_de"] == "drei Portionen des folgenden Anteils"
    assert Counter(row["revision_class"] for row in revisions) == {
        "TARGET_HEAD": 41,
        "AR_CONTROL_HEAD": 14,
        "NEUTRAL_GRAMMAR": 1,
        "BOUND_RIGHT_HEAD_CARRY_TOKEN": 1,
    }
    checks.append("55_head_changes_plus_two_repairs__10_or_portions_semantically_preserved")

    surface_source_by_form = {row["surface"]: row for row in surface_source}
    selected_surface_by_form = {row["surface"]: row for row in selected_surfaces}
    assert len(surface_source_by_form) == len(selected_surface_by_form) == 16
    for surface, source in surface_source_by_form.items():
        selected = selected_surface_by_form[surface]
        assert all(selected[field] == value for field, value in source.items())
        assert selected["selected_candidate"] == "share"
        assert selected["selected_gloss_de"] == source["share_de"]
        assert selected["selected_formal_role"] == "R_INDEXED_MATERIAL_SHARE_SELECTOR"
    for key, row in target_by_key.items():
        source = surface_source_by_form[row["surface"]]
        assert row["fraction_de"] == row["v65_fraction_de"] == source["fraction_de"]
        assert row["share_de"] == source["share_de"] == selected_token_by_key[key]["v66_selected_gloss_de"]
        assert root_count(row["share_de"], "anteil") >= 1
    checks.append("all_16_surface_cards_and_41_target_occurrences_replay")

    census_by_candidate = {row["candidate"]: row for row in census}
    assert set(census_by_candidate) == set(CANDIDATES)
    assert (int(census_by_candidate["fraction"]["changed_token_positions"]),
            int(census_by_candidate["fraction"]["target_changes"]),
            int(census_by_candidate["fraction"]["control_changes"])) == (0, 0, 0)
    for candidate in ("share", "stage", "class"):
        assert (
            int(census_by_candidate[candidate]["changed_token_positions"]),
            int(census_by_candidate[candidate]["target_changes"]),
            int(census_by_candidate[candidate]["control_changes"]),
        ) == (55, 41, 14)
    assert int(census_by_candidate["share"]["anteil_word_occurrences"]) == 56
    assert int(census_by_candidate["share"]["portion_word_occurrences"]) == 49
    assert int(census_by_candidate["share"]["fraktion_word_occurrences"]) == 23
    assert result["selected"]["candidate_share_before_reader_repairs_fraction_word_occurrences"] == 23
    assert result["selected"]["unmigrated_inherited_fraction_word_occurrences"] == 22
    assert result["selected"]["unmigrated_inherited_fraction_positions"] == 22
    residual_by_key = keyed(residuals)
    expected_residual_keys = {
        key for key, row in selected_token_by_key.items()
        if root_count(row["v66_selected_gloss_de"], "fraktion")
    }
    assert set(residual_by_key) == expected_residual_keys
    assert len({row["surface"] for row in residuals}) == 22
    for key, row in residual_by_key.items():
        selected = selected_token_by_key[key]
        assert row["surface"] == selected["surface"]
        assert row["v66_selected_gloss_de"] == selected["v66_selected_gloss_de"]
        assert row["v65_composition"] == selected["v65_composition"]
        assert row["v65_family"] == selected["v65_family"]
        assert row["v65_basis"] == selected["v65_basis"]
        assert row["v66_scope_status"] == "INHERITED_OUTSIDE_GDT693_HEAD_SCOPE"
        assert row["next_question"] == "MIGRATE_AS_COMPOSED_R_SHARE_OR_RETAIN_AS_INDEPENDENT_LEARNED_WHOLE"
    checks.append("candidate_share_has_23_but_selected_repairs_reduce_residual_positions_to_22")

    selected_span_by_start: dict[tuple[str, int], dict[str, str]] = {}
    covered: set[tuple[str, int]] = set()
    for source, selected in zip(span_source, selected_spans, strict=True):
        assert all(selected[field] == value for field, value in source.items())
        assert selected["selected_candidate"] == "share"
        assert selected["selected_gloss_de"] == source["share_de"]
        assert selected["selected_semantics"] == "R_INDEXED_MATERIAL_SHARE_WITH_BOUND_QUANTITY"
        start = int(selected["start_ordinal"])
        end = int(selected["end_ordinal"])
        key = (selected["locus"], start)
        assert key not in selected_span_by_start
        selected_span_by_start[key] = selected
        for ordinal in range(start, end + 1):
            covered_key = (selected["locus"], ordinal)
            assert covered_key not in covered
            covered.add(covered_key)
    assert len(selected_span_by_start) == 2 and len(covered) == 4

    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_tokens:
        tokens_by_locus[row["locus"]].append(row)
    selected_line_by_locus = {row["locus"]: row for row in selected_lines}
    four_line_by_locus = {row["locus"]: row for row in lines}
    v65_line_by_locus = {row["locus"]: row for row in v65_lines}
    assert set(tokens_by_locus) == set(selected_line_by_locus) == set(four_line_by_locus) == set(v65_line_by_locus)
    changed_line_count = 0
    selected_vs_candidate_line_differences: set[str] = set()
    for locus, locus_tokens in tokens_by_locus.items():
        locus_tokens.sort(key=lambda row: int(row["token_ordinal"]))
        assert [int(row["token_ordinal"]) for row in locus_tokens] == list(range(1, len(locus_tokens) + 1))
        assert " ".join(row["surface"] for row in locus_tokens) == selected_line_by_locus[locus]["zl3b_line"]
        units: list[str] = []
        ordinal = 1
        while ordinal <= len(locus_tokens):
            span = selected_span_by_start.get((locus, ordinal))
            if span:
                end = int(span["end_ordinal"])
                assert "|".join(row["surface"] for row in locus_tokens[ordinal - 1:end]) == span["surfaces"]
                units.append(span["selected_gloss_de"])
                ordinal = end + 1
            else:
                units.append(locus_tokens[ordinal - 1]["v66_selected_gloss_de"])
                ordinal += 1
        selected_line = selected_line_by_locus[locus]
        assert render(units) == selected_line["v66_selected_translation_de"]
        if selected_line["v66_selected_translation_de"] != four_line_by_locus[locus]["v66_share_translation_de"]:
            selected_vs_candidate_line_differences.add(locus)
        assert four_line_by_locus[locus]["v66_fraction_translation_de"] == v65_line_by_locus[locus]["v65_compositional_translation_de"]
        locus_revision_ordinals = sorted(
            int(row["token_ordinal"]) for row in revisions if row["locus"] == locus
        )
        assert int(selected_line["v66_selected_changed_token_positions"]) == len(locus_revision_ordinals)
        expected_ordinals = "|".join(map(str, locus_revision_ordinals)) if locus_revision_ordinals else "NONE"
        assert selected_line["v66_selected_changed_ordinals"] == expected_ordinals
        if selected_line["v66_selected_translation_de"] != selected_line["v65_compositional_translation_de"]:
            changed_line_count += 1
    assert sum(int(row["token_count"]) for row in selected_lines) == 479
    assert changed_line_count == 31
    assert selected_vs_candidate_line_differences == {"f105r.2"}
    checks.append("51_line_selected_share_replay_with_two_bound_spans_and_two_token_repairs")

    pair_source_by_id = {row["pair_id"]: row for row in pair_source}
    assert set(pair_source_by_id) == {f"M{number:03d}" for number in range(1, 7)}
    expected_pair_counts = {
        (row["pair_id"], terminal.upper()): int(row[f"expected_{terminal}_count"])
        for row in pair_source
        for terminal in ("r", "n")
    }
    assert Counter((row["pair_id"], row["terminal"]) for row in pairs) == expected_pair_counts
    pair_keys: set[tuple[str, int]] = set()
    for row in pairs:
        source = pair_source_by_id[row["pair_id"]]
        terminal = row["terminal"].casefold()
        assert terminal in {"r", "n"}
        assert row["left_body"] == source["left_body"]
        assert row["surface"] == source[f"{terminal}_surface"] == source["left_body"] + terminal
        assert row["typed_role"] == source[f"{terminal}_role"]
        key = (row["locus"], int(row["token_ordinal"]))
        assert key not in pair_keys
        pair_keys.add(key)
        selected = selected_token_by_key[key]
        assert row["v65_gloss_de"] == v65_token_by_key[key]["v65_token_gloss_de"]
        assert row["v66_selected_gloss_de"] == selected["v66_selected_gloss_de"]
        if terminal == "r":
            assert row["v66_selected_terminal_semantics"] == "R_INDEXED_MATERIAL_SHARE_SELECTOR"
            assert int(selected["v66_selected_changed"]) == 1
            assert root_count(row["v66_selected_gloss_de"], "anteil") >= 1
        else:
            assert row["v66_selected_terminal_semantics"] == "N_HEAD_TYPED_GRADE_AMOUNT_OR_BATCH_VALUE"
            assert int(selected["v66_selected_changed"]) == 0
    assert len(pair_keys) == 30
    assert result["r_n_terminal_evidence"]["minimal_pairs"] == 6
    assert result["r_n_terminal_evidence"]["current_occurrences"] == 30
    checks.append("six_r_n_minimal_pairs_and_30_typed_occurrences")

    assert len(priors) == 9
    assert sum(int(row["pair_occurrences"]) for row in priors) == 1369
    assert sum(int(row["pair_reader_exact"]) for row in priors) == 1069
    assert {(row["shell"], row["qualifier"]) for row in priors} == {
        (shell, qualifier)
        for shell in ("BARE", "O", "QO")
        for qualifier in ("UNQUALIFIED", "K", "T")
    }
    assert result["gdt654_prior"]["pair_cells"] == 9
    assert result["gdt654_prior"]["occurrences"] == 1369
    assert result["gdt654_prior"]["reader_exact"] == 1069
    checks.append("nine_cell_gdt654_ar_or_prior_1369_1069")

    rival_source_by_id = {row["rival_id"]: row for row in rival_source}
    rival_by_id = {row["rival_id"]: row for row in selected_rivals}
    assert set(rival_source_by_id) == set(rival_by_id) == {f"R{number:03d}" for number in range(1, 7)}
    for rival_id, row in rival_by_id.items():
        source = rival_source_by_id[rival_id]
        assert all(row[field] == value for field, value in source.items())
        assert row["selected_candidate"] == "share" and row["main_span_exact"] == "1"
        assert row["semantic_scope"] == "LOCAL_REFERENT_RIVAL_ONLY__R_REMAINS_INDEXED_MATERIAL_SHARE"
        assert "Anteil" in row["selected_main_span_de"] and "Holzauszug" in row["local_product_rival_de"]
        start = int(row["start_ordinal"])
        end = int(row["end_ordinal"])
        if start == end:
            main = selected_token_by_key[(row["locus"], start)]["v66_selected_gloss_de"]
        else:
            main = selected_span_by_start[(row["locus"], start)]["selected_gloss_de"]
            assert int(selected_span_by_start[(row["locus"], start)]["end_ordinal"]) == end
        assert main == row["selected_main_span_de"]
    checks.append("six_local_product_rivals_preserve_selected_r_head")

    v65_verb_by_key = keyed_verbs(v65_verbs)
    verb_by_key = keyed_verbs(verbs)
    selected_verb_by_key = keyed_verbs(selected_verbs)
    assert set(v65_verb_by_key) == set(verb_by_key) == set(selected_verb_by_key)
    for key, row in selected_verb_by_key.items():
        source = v65_verb_by_key[key]
        base = verb_by_key[key]
        assert row["surface"] == source["surface"] and row["verb_de"] == source["verb_de"]
        assert int(row["preserved_exact_ordinal"]) == 1
        assert int(row["gdt692_additional_verb_form_loss"]) == 0
        assert row["v66_selected_candidate"] == "share"
        token_key = (key[0], key[1])
        assert row["v66_selected_gloss_de"] == selected_token_by_key[token_key]["v66_selected_gloss_de"]
        assert int(row["v66_selected_exact_form_present"]) == int(source["v65_exact_form_present"])
        for candidate in CANDIDATES:
            assert int(base[f"v66_{candidate}_exact_form_present"]) == int(source["v65_exact_form_present"])
    assert sum(int(row["v65_exact_form_present"]) for row in v65_verbs) == 110
    assert sum(int(row["v66_selected_exact_form_present"]) for row in selected_verbs) == 110
    assert result["verbs"] == {
        "ordinals": 113,
        "all_four_exact_profiles_preserved": 1,
        "selected_exact_profile_preserved": 1,
    }
    checks.append("all_113_verb_profiles_preserved_110_exact")

    spec = importlib.util.spec_from_file_location("gdt693_run", RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="gdt693_replay_") as temporary:
        replay_dir = Path(temporary)
        replay_result = module.build(replay_dir)
        assert replay_result == result
        assert {path.name for path in replay_dir.iterdir() if path.is_file()} == EXPECTED_FILES
        for name in EXPECTED_FILES:
            assert (replay_dir / name).read_bytes() == (ART / name).read_bytes(), name
    checks.append("exact_tempdir_byte_replay_all_20_generated_files")

    validation = {
        "experiment": "GDT693",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "result_sha256": sha256(RESULT_PATH),
        "validator_sha256": sha256(Path(__file__).resolve()),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
