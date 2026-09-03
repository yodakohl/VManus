#!/usr/bin/env python3
"""Independent validator for the frozen GDT779 residual-whole experiment."""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
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
EXP = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
REPORT = EXP / "REPORT.md"
SPECS = SRC / "RESIDUAL_V99R7_EXACT_WHOLE_SPECS.tsv"
LOCKS = SRC / "SOURCE_LOCK.tsv"

PARENT = ROOT / "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion/artifacts/GDT778_376_RENDERER.tsv"
PARENT_RESULT = ROOT / "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion/artifacts/RESULT.json"
V99 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G754 = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G755_GLOSS = ROOT / "experiments/yolo/gdt755_top24_historical_register_crosswalk/artifacts/TOP24_WORKING_GLOSS_UPDATE.tsv"
G755_OCC = ROOT / "experiments/yolo/gdt755_top24_historical_register_crosswalk/artifacts/TOP24_448_OCCURRENCE_FIELDS.tsv"

ATLAS = ART / "GDT779_50_EXACT_WHOLE_ATLAS.tsv"
EXCLUSIONS = ART / "GDT779_49_EXACTNESS_EXCLUSIONS.tsv"
SHADOW = ART / "GDT779_179_PRECEDENCE_SHADOW_AUDIT.tsv"
RENDERER = ART / "GDT779_376_RENDERER.tsv"
DICTIONARY = ART / "GDT779_WORKING_DICTIONARY.tsv"
PASSAGES = ART / "GDT779_PASSAGE_PATCHES.tsv"
PROVENANCE = ART / "GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv"
RESIDUAL = ART / "GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv"
PACKET = ART / "GDT779_GDT388_RELATION_PACKET.tsv"
CROSSWALK = ART / "GDT779_RELATION_EDGE_CROSSWALK.tsv"
INTAKE = ART / "RELATION_PACKET_INTAKE.json"
RESULT = ART / "RESULT.json"
ARTIFACT_README = ART / "README.md"

REPLAY_OUTPUTS = (
    ATLAS, EXCLUSIONS, SHADOW, RENDERER, DICTIONARY, PASSAGES, PROVENANCE,
    RESIDUAL, PACKET, CROSSWALK, INTAKE, RESULT, ARTIFACT_README, REPORT,
)

EXPECTED_LOCKS = {
    "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion/artifacts/GDT778_376_RENDERER.tsv":
        "799a22476c313894b3ab7f879be1fed3b1232c752a033e115f67179be544726e",
    "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion/artifacts/RESULT.json":
        "a0c3fb491072995ce999fac1f0d5bcf34c1fa86f7509b5fa05e2960de93474b0",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv":
        "9646b8960840f0a6bb10985f0f9d7eef1237725f0763b712a96f0190aeaf7816",
    "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv":
        "1983d5644000938182a7a8390835117393c2651e8a2eb46ab513172eb90df405",
    "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/BODY_120_SEMANTIC_BRIDGE.tsv":
        "620335302efe3554347f0e2942ac48bf1ac7fee72db7545d136a8ab08170872b",
    "experiments/yolo/gdt749_outside_frame_whole_role_distribution/artifacts/TARGET_OUTSIDE_ROLE_CENSUS.tsv":
        "69ef0ad57b150a8ea4580bbfaa9c3c1ff63f5e17cc943af38466f62274bcbec3",
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv":
        "25f2af6f38af1b8aee8fb2d6160f2742ab28ec71e704b51df3daf6d03251718d",
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/artifacts/TOP24_WORKING_GLOSS_UPDATE.tsv":
        "edff3477150905dab60acb5e89f0c953a1a64854d257652576308c922b6161bf",
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/artifacts/TOP24_448_OCCURRENCE_FIELDS.tsv":
        "9d9a3814fede69167021b1b001721bf2cf825e678af07c028658aa01633e9ec3",
    "experiments/yolo/gdt758_ychor_follower_global_content_census/artifacts/FOLLOWER_11_GLOBAL_CENSUS.tsv":
        "021439ab271db5052642619d1d025ad9db6cbc5301a3fee1e53d5f1b85457d49",
    "tools/relation_edge_intake.py":
        "fb8447470aa81ed608b90aedf7478893ddf6a445351aa12ab23c6fd725be3a47",
}

EXPECTED_FORMS = frozenset({
    "chckhy", "chcphy", "chcthy", "cheal", "checkhy", "chedaiin", "cheedy",
    "cheeky", "cheeor", "cheky", "cheol", "cheor", "chety", "chody",
    "chokaiin", "daiin", "daldy", "dam", "dl", "kaiiin", "lkedy", "loeees",
    "ochedar", "oeeal", "okchy", "okeeey", "oky", "olshdy", "otchy", "otol",
    "qockhey", "qokaiin", "qokar", "qokeedy", "qoly", "shal", "sham",
    "sheol", "sho", "tedy", "teedy", "teey", "teody", "tey",
})
SANITIZED = frozenset({"cheeor", "cheor", "lkedy", "loeees", "olshdy", "qokar"})
NEW_SCOPES = frozenset({"chcthy", "daiin", "kaiiin"})
COMPOSED = frozenset({"chcphy", "okeeey"})
QOCKHEY = frozenset({"qockhey"})
CLASS_SETS = {
    "DIRECT_INHERITED_WHOLE_CARD": EXPECTED_FORMS - SANITIZED - NEW_SCOPES - COMPOSED - QOCKHEY,
    "RETIRED_PATIENT_SANITIZATION": SANITIZED,
    "NEW_EXACT_OL_SCOPE": NEW_SCOPES,
    "COMPOSITION_DERIVED_WHOLE__NO_COMPONENT_EXPORT": COMPOSED,
    "GDT755_LATER_COMPLETE_WHOLE_REPLACEMENT": QOCKHEY,
}
CLASS_COUNTS = Counter({name: len(forms) for name, forms in CLASS_SETS.items()})
EXPECTED_SELECTED_COUNTS = Counter({form: 1 for form in EXPECTED_FORMS})
EXPECTED_SELECTED_COUNTS.update({"cheal": 1, "cheedy": 2, "cheeky": 1, "cheol": 1, "otol": 1})
EXPECTED_OVERLAP = frozenset({"cheedy", "cheol", "daiin", "dam"})
SELECTION_RULE = "GDT778_RENDERER_CONTEXTUAL_0_AND_COMPLETE_RIGHT_SURFACE_V99R7_CARD_MATCH_AND_RIGHT_READER_EXACT_1"
PATIENT_RE = re.compile(r"(?i)(pulver|samen|wurzel|holz|droge|filtrat|abgeseih)")
SEALED_RE = re.compile(r"(?<![A-Za-z0-9])f84r?(?![A-Za-z0-9])", re.I)
GENERIC_RE = re.compile(r"(?i)(ansatz-/zubereitungsposten|arbeitshypothese|unbestimmt|unresolved|offen|^none$)")

EXPECTED_INTAKE = {
    "status": "VALID_ACQUISITION_NOT_SCORE_READY",
    "packet_rows": 50,
    "eligible_edges": 0,
    "eligible_folios": 0,
    "discovery_edges": 0,
    "holdout_edges": 0,
    "mobile_edges": 0,
    "capacity_gate_50_edges_5_folios": False,
    "holdout_gate": False,
    "mobile_null_gate": False,
    "score_ready": False,
    "errors": [],
}


class Audit:
    def __init__(self) -> None:
        self.count = 0
        self.labels: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        self.count += 1
        self.labels.append(label)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def unique(rows: Sequence[Mapping[str, str]], field: str) -> dict[str, Mapping[str, str]]:
    result: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = row[field]
        if key in result:
            raise AssertionError("duplicate " + field + ": " + key)
        result[key] = row
    return result


def zero_fields(rows: Iterable[Mapping[str, str]], fields: Sequence[str]) -> bool:
    return all(row.get(field, "0") == "0" for row in rows for field in fields if field in row)


def active_state_equal(parent: Mapping[str, str], current: Mapping[str, str]) -> bool:
    pairs = (
        ("gdt778_default_de", "gdt779_default_de"),
        ("gdt778_renderer_contextual", "gdt779_renderer_contextual"),
        ("gdt778_span_id", "gdt779_span_id"),
        ("gdt778_exact_whole", "gdt779_exact_whole"),
        ("gdt778_confidence", "gdt779_confidence"),
        ("gdt778_consumed_token_count", "gdt779_consumed_token_count"),
        ("gdt778_consumed_token_ids", "gdt779_consumed_token_ids"),
    )
    return all(parent[left] == current[right] for left, right in pairs)


def expected_residual_reason(row: Mapping[str, str], card_forms: set[str],
                             final_forms: frozenset[str], raw_forms: set[str]) -> str:
    surface = row["right_surface"]
    if surface == "NONE" or int(row["right_ordinal"]) == 0:
        return "LINE_FINAL_NO_RIGHT"
    if surface not in card_forms:
        if row["right_reader_exact"] == "1":
            return "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT"
        return "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT"
    if surface in final_forms:
        return "V99_CARD_NONEXACT_FINAL44"
    if surface not in raw_forms:
        raise AssertionError("card-backed residual outside reconstructed raw deck")
    return "V99_CARD_NONEXACT_RAW_ONLY"


def validate_runner_ast(audit: Audit) -> None:
    tree = ast.parse(RUN.read_text(encoding="utf-8"), filename=str(RUN))
    functions = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "select_gdt779_row"
    ]
    audit.check(len(functions) == 1, "one pure named selection function")
    function = functions[0]
    args = [arg.arg for arg in function.args.args]
    audit.check(
        args == [
            "gdt778_renderer_contextual", "right_surface",
            "right_reader_exact", "fixed_complete_surfaces",
        ]
        and not function.args.defaults
        and function.args.vararg is None
        and function.args.kwarg is None,
        "selection function has only four declared inputs",
    )
    returns = [node for node in ast.walk(function) if isinstance(node, ast.Return)]
    audit.check(len(returns) == 1, "selection function has one return")
    expected = ast.parse(
        "gdt778_renderer_contextual == '0' and "
        "right_reader_exact == '1' and "
        "right_surface in fixed_complete_surfaces",
        mode="eval",
    ).body
    audit.check(
        ast.dump(returns[0].value, include_attributes=False)
        == ast.dump(expected, include_attributes=False),
        "selection AST is exact fallback, exact-reader, fixed-whole membership predicate",
    )
    forbidden_nodes = (ast.Subscript, ast.Call, ast.Attribute, ast.BinOp, ast.IfExp, ast.Lambda)
    audit.check(
        not any(isinstance(node, forbidden_nodes) for node in ast.walk(returns[0].value)),
        "selection has no substring, lookup, call, arithmetic, or conditional selector",
    )
    names = {node.id for node in ast.walk(returns[0].value) if isinstance(node, ast.Name)}
    audit.check(set(args) == names, "selection references every and only declared row properties")
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "select_gdt779_row"
    ]
    audit.check(len(calls) == 1, "runner constructs actual exact list through pure selector")
    call = calls[0]
    audit.check(
        [ast.unparse(arg) for arg in call.args] == [
            "row['gdt778_renderer_contextual']", "row['right_surface']",
            "row['right_reader_exact']", "fixed_complete_surfaces",
        ],
        "pure selector call uses only exact declared columns and frozen deck",
    )
    assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "exact" for target in node.targets)
    ]
    assignment = [
        node for node in assignments
        if any(
            isinstance(descendant, ast.Call)
            and isinstance(descendant.func, ast.Name)
            and descendant.func.id == "select_gdt779_row"
            for descendant in ast.walk(node.value)
        )
    ]
    audit.check(
        len(assignment) == 1
        and any(node is call for node in ast.walk(assignment[0].value)),
        "actual exact cohort is the pure-selector comprehension",
    )
    forbidden_words = {
        "target_occurrence_id", "locus", "page", "physical_folio",
        "selected_default_de", "positive_evidence", "counterevidence",
    }
    audit.check(
        not (forbidden_words & names),
        "selection is occurrence-free and semantics-free",
    )


def validate_source_locks(audit: Audit) -> dict[str, str]:
    rows = read_tsv(LOCKS)
    audit.check(len(rows) == 11, "eleven source locks")
    by_path = unique(rows, "path")
    audit.check(set(by_path) == set(EXPECTED_LOCKS), "source lock path set frozen")
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_LOCKS.items():
        row = by_path[relative]
        path = Path(relative)
        audit.check(
            not path.is_absolute() and ".." not in path.parts,
            "safe relative lock path: " + relative,
        )
        audit.check(row["expected_sha256"] == expected, "hard-coded lock hash: " + relative)
        actual = sha256(ROOT / path)
        audit.check(actual == expected, "reconstructed source hash: " + relative)
        observed[relative] = actual
    return observed


def validate_specs(audit: Audit) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    rows = read_tsv(SPECS)
    audit.check(len(rows) == 44, "44 specification rows")
    by_form = {key: dict(value) for key, value in unique(rows, "right_surface").items()}
    audit.check(frozenset(by_form) == EXPECTED_FORMS, "exact frozen 44-form deck")
    observed_sets = {
        name: frozenset(row["right_surface"] for row in rows if row["card_class"] == name)
        for name in CLASS_SETS
    }
    audit.check(
        Counter(row["card_class"] for row in rows) == CLASS_COUNTS,
        "card-class partition is 32/6/3/2/1",
    )
    audit.check(observed_sets == CLASS_SETS, "card-class memberships exact and disjoint")
    audit.check(
        all(row["scope_status"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY" for row in rows),
        "all cards are exact complete-whole scoped",
    )
    audit.check(
        all(
            row["selected_default_de"]
            and len({
                row["selected_default_de"], row["alternate_1_de"], row["alternate_2_de"]
            }) == 3
            for row in rows
        ),
        "each card has one nonempty default and two distinct rivals",
    )
    audit.check(
        all(PATIENT_RE.search(row["selected_default_de"]) is None for row in rows),
        "active defaults contain no retired patient wording",
    )
    audit.check(
        all(GENERIC_RE.search(row["selected_default_de"]) is None for row in rows),
        "active defaults contain no generic null phrase",
    )
    audit.check(
        by_form["cheor"]["selected_default_de"] == "trockener Teil",
        "cheor corrected practical default",
    )
    audit.check(
        by_form["qockhey"]["selected_default_de"] == "mische"
        and by_form["qockhey"]["confidence"] == "C0",
        "qockhey forced complete-whole default",
    )
    return rows, by_form


def validate_selection(
    audit: Audit,
    specs: Mapping[str, Mapping[str, str]],
) -> tuple[
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]],
    set[str], dict[str, list[dict[str, str]]],
]:
    parent = read_tsv(PARENT)
    audit.check(len(parent) == 376, "parent renderer has 376 rows")
    audit.check(
        len(unique(parent, "target_occurrence_id")) == 376,
        "parent occurrence IDs unique",
    )
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check(
        sum(row["gdt778_renderer_contextual"] == "1" for row in parent) == 195
        and sum(row["gdt778_renderer_contextual"] == "0" for row in parent) == 181,
        "parent renderer reconstructs 195 contextual and 181 fallback",
    )
    audit.check(
        parent_result["renderer"]["gdt778_contextual"] == 195
        and parent_result["consumption"]["total_unique_right_tokens"] == 155,
        "parent RESULT independently agrees on coverage and consumption",
    )

    v99_rows = read_tsv(V99)
    audit.check(len(v99_rows) == 1606, "V99R7 registry has 1606 rows")
    cards: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in v99_rows:
        cards[row["surface"]].append(row)
    card_forms = set(cards)

    fallback = [row for row in parent if row["gdt778_renderer_contextual"] == "0"]
    raw = [row for row in fallback if row["right_surface"] in card_forms]
    raw_forms = {row["right_surface"] for row in raw}
    audit.check(len(raw) == 99 and len(raw_forms) == 76, "99 raw card hits in 76 forms")
    audit.check(
        all(len(cards[form]) == 1 for form in raw_forms),
        "every raw candidate has one complete-word card",
    )
    raw_exact = [row for row in raw if row["right_reader_exact"] == "1"]
    raw_nonexact = [row for row in raw if row["right_reader_exact"] != "1"]
    selected = [
        row for row in parent
        if row["gdt778_renderer_contextual"] == "0"
        and row["right_reader_exact"] == "1"
        and row["right_surface"] in specs
    ]
    audit.check(
        [row["target_occurrence_id"] for row in selected]
        == [row["target_occurrence_id"] for row in raw_exact],
        "fixed-deck predicate equals every raw-card exact hit",
    )
    audit.check(
        len(selected) == 50
        and len({row["right_surface"] for row in selected}) == 44,
        "50 selected spans cover exactly 44 forms",
    )
    audit.check(
        Counter(row["right_surface"] for row in selected) == EXPECTED_SELECTED_COUNTS,
        "all repeated form hits retained with no first-row truncation",
    )
    audit.check(
        len(selected) - len({row["right_surface"] for row in selected}) == 6,
        "six beyond-first repeated occurrences are retained",
    )
    audit.check(
        len(raw_nonexact) == 49
        and len({row["right_surface"] for row in raw_nonexact}) == 36,
        "49 nonexact exclusions cover 36 forms",
    )
    audit.check(
        frozenset(row["right_surface"] for row in raw_exact)
        & frozenset(row["right_surface"] for row in raw_nonexact)
        == EXPECTED_OVERLAP,
        "exact/nonexact form overlap is the frozen four-form set",
    )
    audit.check(
        len({row["locus"] for row in selected}) == 49
        and len({row["page"] for row in selected}) == 33
        and len({row["physical_folio"] for row in selected}) == 24,
        "selected geography is 49 loci, 33 pages, 24 folios",
    )
    audit.check(
        Counter(row["locus"] for row in selected) == Counter({
            **{row["locus"]: 1 for row in selected if row["locus"] != "f75r.26"},
            "f75r.26": 2,
        }),
        "f75r.26 is the only double-selected locus",
    )
    audit.check(
        {
            row["right_surface"] for row in selected if row["locus"] == "f75r.26"
        } == {"sheol", "qoly"},
        "f75r.26 contains sheol and qoly",
    )
    audit.check(
        all(
            int(row["right_ordinal"]) == int(row["ordinal"]) + 1
            and row["written_line_eva"].split()[int(row["ordinal"]) - 1] == "ol"
            and row["written_line_eva"].split()[int(row["right_ordinal"]) - 1] == row["right_surface"]
            for row in selected
        ),
        "all selected spans are literal adjacent ol plus complete right surface",
    )
    return parent, selected, raw_nonexact, raw_forms, cards


def validate_atlas_and_exclusions(
    audit: Audit,
    parent: Sequence[Mapping[str, str]],
    selected: Sequence[Mapping[str, str]],
    rejected: Sequence[Mapping[str, str]],
    specs: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], set[str]]:
    atlas = read_tsv(ATLAS)
    exclusions = read_tsv(EXCLUSIONS)
    audit.check(len(atlas) == 50, "atlas has 50 rows")
    audit.check(
        [row["target_occurrence_id"] for row in atlas]
        == [row["target_occurrence_id"] for row in selected],
        "atlas is exactly all predicate hits in parent order",
    )
    audit.check(
        [row["span_id"] for row in atlas]
        == [f"G779-S{number:03d}" for number in range(1, 51)],
        "atlas span IDs complete and ordered",
    )
    by_target = unique(parent, "target_occurrence_id")
    audit.check(
        all(
            row["right_surface"] == by_target[row["target_occurrence_id"]]["right_surface"]
            and row["right_reader_exact"] == "1"
            and row["old_gdt778_contextual"] == "0"
            and row["old_gdt778_default_de"] == "Ansatz-/Zubereitungsposten"
            and row["new_gdt779_default_de"] == specs[row["right_surface"]]["selected_default_de"]
            and row["selected_whole_default_de"] == specs[row["right_surface"]]["selected_default_de"]
            and row["card_class"] == specs[row["right_surface"]]["card_class"]
            and row["scope_status"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY"
            and row["selection_rule"] == SELECTION_RULE
            for row in atlas
        ),
        "atlas semantics and selection fields reconstruct from parent plus specs",
    )
    audit.check(
        all(
            row["selection_uses_occurrence_id"] == "0"
            and row["selection_uses_semantics"] == "0"
            and row["fallback_replacement"] == "1"
            and row["display_changed"] == "1"
            and row["exact_complete_whole_only"] == "1"
            for row in atlas
        ),
        "atlas records occurrence-free exact fallback replacements",
    )
    audit.check(
        zero_fields(
            atlas,
            (
                "same_row_inherited_consumption_takeover",
                "cross_row_consumption_collision", "default_is_translation",
                "confirmed_lexeme", "confirmed_plaintext", "component_export_credit",
            ),
        ),
        "atlas claim and collision ceilings are zero",
    )

    inherited_ids: set[str] = set()
    for row in parent:
        value = row["gdt778_consumed_token_ids"]
        ids = [] if value == "NONE" else value.split("|")
        audit.check(
            len(ids) == int(row["gdt778_consumed_token_count"]),
            "parent consumption arity " + row["target_occurrence_id"],
        )
        for token_id in ids:
            if token_id in inherited_ids:
                raise AssertionError("parent cross-row token collision: " + token_id)
            inherited_ids.add(token_id)
    audit.check(len(inherited_ids) == 155, "155 inherited unique right tokens")
    new_ids = {row["gdt779_consumed_token_id"] for row in atlas}
    audit.check(len(new_ids) == 50, "50 selected right token IDs unique")
    audit.check(not (new_ids & inherited_ids), "new token IDs do not collide with inherited consumption")
    audit.check(len(new_ids | inherited_ids) == 205, "combined consumption reconstructs 205 tokens")
    audit.check(
        all(
            row["gdt779_consumed_token_id"]
            == row["locus"] + "@" + row["right_ordinal"]
            for row in atlas
        ),
        "selected token IDs reconstruct from locus and right ordinal",
    )

    audit.check(len(exclusions) == 49, "exclusion table has 49 rows")
    audit.check(
        [row["target_occurrence_id"] for row in exclusions]
        == [row["target_occurrence_id"] for row in rejected],
        "exclusion table is exactly every raw nonexact hit",
    )
    audit.check(
        len({row["right_surface"] for row in exclusions}) == 36
        and all(row["right_reader_exact"] == "0" for row in exclusions),
        "exclusion table contains 36 forms and no exact row",
    )
    audit.check(
        all(
            row["exclusion_reason"]
            == "V99R7_COMPLETE_WORD_CARD_MATCH_BUT_RIGHT_READER_NONEXACT"
            and row["selection_rule"] == SELECTION_RULE
            and row["selection_uses_occurrence_id"] == "0"
            for row in exclusions
        ),
        "all exclusions use the predeclared exactness rule",
    )
    audit.check(
        sum(row["final_44_deck_member"] == "1" for row in exclusions) == 4,
        "four exclusions belong to final 44-form deck",
    )
    return atlas, exclusions, inherited_ids


def validate_renderer_and_shadow(
    audit: Audit,
    parent: Sequence[Mapping[str, str]],
    selected: Sequence[Mapping[str, str]],
    raw_forms: set[str],
    specs: Mapping[str, Mapping[str, str]],
    atlas: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    renderer = read_tsv(RENDERER)
    audit.check(len(renderer) == 376, "new renderer has 376 rows")
    audit.check(
        [row["target_occurrence_id"] for row in renderer]
        == [row["target_occurrence_id"] for row in parent],
        "renderer preserves parent row order and identity",
    )
    shared_parent_fields = set(parent[0]) & set(renderer[0])
    audit.check(
        {
            "target_occurrence_id", "page", "physical_folio", "locus",
            "ordinal", "right_surface", "right_ordinal", "right_reader_exact",
            "written_line_eva", "gdt778_branch", "gdt778_default_de",
            "gdt778_renderer_contextual", "gdt778_span_id",
            "gdt778_exact_whole", "gdt778_confidence",
            "gdt778_consumed_token_count", "gdt778_consumed_token_ids",
        } <= shared_parent_fields,
        "renderer retains all core and GDT778 parent-state fields",
    )
    audit.check(
        all(
            all(current[field] == old[field] for field in shared_parent_fields)
            for old, current in zip(parent, renderer)
        ),
        "every retained parent byte-field is unchanged in renderer",
    )
    selected_ids = {row["target_occurrence_id"] for row in selected}
    atlas_by_target = unique(atlas, "target_occurrence_id")
    for old, current in zip(parent, renderer):
        target = old["target_occurrence_id"]
        if target in selected_ids:
            span = atlas_by_target[target]
            audit.check(
                current["gdt779_branch"] == "GDT779_EXACT_OL_PLUS_RESIDUAL_V99R7_WHOLE"
                and current["gdt779_renderer_contextual"] == "1"
                and current["gdt779_default_de"] == specs[old["right_surface"]]["selected_default_de"]
                and current["gdt779_consumed_token_count"] == "1"
                and current["gdt779_consumed_token_ids"] == span["gdt779_consumed_token_id"]
                and current["gdt779_fallback_replacement"] == "1"
                and current["gdt779_display_changed"] == "1",
                "selected renderer replacement " + target,
            )
        else:
            audit.check(
                current["gdt779_branch"] == "INHERITED_GDT778"
                and active_state_equal(old, current)
                and current["gdt779_fallback_replacement"] == "0"
                and current["gdt779_display_changed"] == "0"
                and current["gdt779_new_unique_consumption"] == "0",
                "nonselected renderer row inherited " + target,
            )
    audit.check(
        sum(row["gdt779_renderer_contextual"] == "1" for row in renderer) == 245
        and sum(row["gdt779_renderer_contextual"] == "0" for row in renderer) == 131,
        "renderer coverage moves 195 to 245 and fallbacks 181 to 131",
    )
    audit.check(
        sum(row["gdt779_fallback_replacement"] == "1" for row in renderer) == 50
        and sum(row["gdt779_display_changed"] == "1" for row in renderer) == 50,
        "renderer has exactly 50 replacements and 50 display changes",
    )
    current_tokens: list[str] = []
    for row in renderer:
        ids = [] if row["gdt779_consumed_token_ids"] == "NONE" else row["gdt779_consumed_token_ids"].split("|")
        audit.check(
            len(ids) == int(row["gdt779_consumed_token_count"]),
            "current consumption arity " + row["target_occurrence_id"],
        )
        current_tokens.extend(ids)
    audit.check(
        len(current_tokens) == len(set(current_tokens)) == 205,
        "renderer has 205 unique tokens and no collision",
    )

    raw_shadow_parent = [row for row in parent if row["right_surface"] in raw_forms]
    raw_exact_parent = [row for row in raw_shadow_parent if row["right_reader_exact"] == "1"]
    final_parent = [row for row in parent if row["right_surface"] in specs]
    final_exact_parent = [row for row in final_parent if row["right_reader_exact"] == "1"]
    protected = [
        row for row in raw_exact_parent if row["gdt778_renderer_contextual"] == "1"
    ]
    final_protected = [row for row in protected if row["right_surface"] in specs]
    audit.check(
        len(raw_shadow_parent) == 179 and len(raw_exact_parent) == 127,
        "raw 76-deck shadow reconstructs 179 rows and 127 exact",
    )
    audit.check(
        Counter(row["gdt778_renderer_contextual"] for row in raw_shadow_parent)
        == Counter({"0": 99, "1": 80}),
        "raw shadow partitions into 99 fallback and 80 contextual",
    )
    audit.check(
        len(final_parent) == 68 and len(final_exact_parent) == 63,
        "final 44-deck shadow reconstructs 68 raw and 63 exact",
    )
    audit.check(
        len(protected) == 77 and len(final_protected) == 13,
        "protected exact contexts reconstruct as 77 raw-deck and 13 final-deck",
    )
    current_by_target = unique(renderer, "target_occurrence_id")
    audit.check(
        all(active_state_equal(row, current_by_target[row["target_occurrence_id"]]) for row in protected),
        "all 77 protected exact contextual states are byte-field unchanged",
    )
    audit.check(
        all(active_state_equal(row, current_by_target[row["target_occurrence_id"]]) for row in final_protected),
        "all 13 final-deck protected exact states are byte-field unchanged",
    )

    shadow = read_tsv(SHADOW)
    audit.check(len(shadow) == 179, "published precedence shadow has 179 rows")
    audit.check(
        [row["target_occurrence_id"] for row in shadow]
        == [row["target_occurrence_id"] for row in raw_shadow_parent],
        "published shadow exactly covers reconstructed raw-deck parent rows",
    )
    shadow_by_target = unique(shadow, "target_occurrence_id")
    audit.check(
        all(
            shadow_by_target[row["target_occurrence_id"]]["represented_parent_state_unchanged"] == "1"
            for row in protected
        ),
        "published shadow marks all 77 protected exact rows unchanged",
    )
    audit.check(
        all(
            shadow_by_target[row["target_occurrence_id"]]["represented_parent_state_unchanged"] == "1"
            for row in raw_shadow_parent if row["gdt778_renderer_contextual"] == "1"
        ),
        "all 80 contextual raw-shadow rows preserve represented parent state",
    )
    audit.check(
        Counter(row["precedence_disposition"] for row in shadow) == Counter({
            "SELECTED_GDT779_FALLBACK": 50,
            "PROTECTED_EXACT_CONTEXTUAL": 13,
            "EXCLUDED_NONEXACT_FINAL_FORM": 4,
            "PROTECTED_NONEXACT_CONTEXTUAL": 1,
            "PROTECTED_EXACT_CONTEXTUAL_RAW_ONLY_FORM": 64,
            "EXCLUDED_NONEXACT_RAW_ONLY_FORM": 45,
            "PROTECTED_NONEXACT_CONTEXTUAL_RAW_ONLY_FORM": 2,
        }),
        "precedence dispositions reconstruct the full 179-row partition",
    )
    return renderer


def validate_dictionary_provenance_passages(
    audit: Audit,
    specs: Mapping[str, Mapping[str, str]],
    atlas: Sequence[Mapping[str, str]],
    exclusions: Sequence[Mapping[str, str]],
) -> None:
    dictionary = read_tsv(DICTIONARY)
    audit.check(len(dictionary) == 44, "working dictionary has 44 rows")
    audit.check(
        [row["entry"] for row in dictionary] == sorted(EXPECTED_FORMS),
        "dictionary has exact sorted frozen deck",
    )
    audit.check(
        all(
            row["preferred_gdt779_default_de"] == specs[row["entry"]]["selected_default_de"]
            and row["alternate_1_de"] == specs[row["entry"]]["alternate_1_de"]
            and row["alternate_2_de"] == specs[row["entry"]]["alternate_2_de"]
            and row["scope"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT"
            for row in dictionary
        ),
        "dictionary copies only declared whole-card values and no substring scope",
    )
    audit.check(
        sum(int(row["selected_exact_fallback_contexts"]) for row in dictionary) == 50
        and sum(int(row["final_form_raw_parent_contexts"]) for row in dictionary) == 68
        and sum(int(row["final_form_exact_parent_contexts"]) for row in dictionary) == 63
        and sum(int(row["protected_exact_contextual_contexts"]) for row in dictionary) == 13
        and sum(int(row["nonexact_fallback_exclusions"]) for row in dictionary) == 4,
        "dictionary occurrence summaries reproduce cohort and precedence counts",
    )
    audit.check(
        zero_fields(
            dictionary,
            ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit"),
        ),
        "dictionary exports no translation, lexeme, plaintext, or component",
    )

    provenance = read_tsv(PROVENANCE)
    audit.check(len(provenance) == 44, "provenance audit has 44 rows")
    audit.check(
        {row["right_surface"] for row in provenance} == EXPECTED_FORMS,
        "provenance covers exact frozen deck",
    )
    audit.check(
        {
            row["right_surface"] for row in provenance
            if row["old_literal_patient_detected"] == "1"
        } == SANITIZED
        and {
            row["right_surface"] for row in provenance
            if row["patient_sanitization_applied"] == "1"
        } == SANITIZED,
        "exactly six retired-patient cards are detected and sanitized",
    )
    audit.check(
        all(
            PATIENT_RE.search(row["selected_default_de"]) is None
            and row["old_prose_used_as_active_default"] == "0"
            for row in provenance
        ),
        "no retired source prose remains active",
    )
    audit.check(
        {
            row["right_surface"] for row in provenance
            if row["v99_unconditional_global_export_allowed"] == "0"
        } == NEW_SCOPES,
        "only three new exact ol scopes lack global export",
    )
    audit.check(
        {
            row["right_surface"] for row in provenance
            if row["v99_candidate_composition"] != "NONE"
        } == COMPOSED,
        "exactly two composition-derived wholes remain whole-only",
    )
    audit.check(
        zero_fields(
            provenance,
            (
                "old_prose_used_as_active_default", "default_is_translation",
                "confirmed_lexeme", "confirmed_plaintext", "component_export_credit",
            ),
        ),
        "provenance grants no old prose, plaintext, lexeme, or component export",
    )

    g754 = unique(read_tsv(G754), "surface")["qockhey"]
    g755 = unique(read_tsv(G755_GLOSS), "surface")["qockhey"]
    g755_occ = [row for row in read_tsv(G755_OCC) if row["surface"] == "qockhey"]
    audit.check(
        g754["source_literal_prose_spoken_after_gdt754"] == "0"
        and g754["renderer_disposition"] == "COMPOSITION_AXES_HYPOTHESIS_ONLY"
        and g754["component_export_credit"] == "0",
        "qockhey GDT754 composed source is quarantined",
    )
    audit.check(
        g755["gdt755_working_candidate_de"] == "mische"
        and g755["working_confidence"] == "C0_FORCED_DEFAULT"
        and g755["candidate_layer_scope"] == "EXACT_COMPLETE_SURFACE_ON_ENUMERATED_READER_EXACT_POSITIONS",
        "qockhey default comes from later GDT755 complete-whole card",
    )
    audit.check(
        len(g755_occ) == 12
        and sum(row["boundary_complete"] == "1" for row in g755_occ) == 7,
        "qockhey source has 12 exact occurrences and seven complete boundaries",
    )
    qockhey_anchor = [
        row for row in g755_occ if row["gdt755_occurrence_id"] == "G755-O0156"
    ]
    audit.check(
        len(qockhey_anchor) == 1
        and qockhey_anchor[0]["locus"] == "f80r.34"
        and qockhey_anchor[0]["token_ordinal"] == "6"
        and qockhey_anchor[0]["reader_exact_target"] == "1"
        and qockhey_anchor[0]["boundary_complete"] == "1",
        "qockhey target fingerprint is exact complete f80r.34 ordinal 6",
    )
    qockhey_prov = [row for row in provenance if row["right_surface"] == "qockhey"]
    audit.check(
        len(qockhey_prov) == 1
        and qockhey_prov[0]["qockhey_gdt754_source_composition_quarantined"] == "1"
        and qockhey_prov[0]["qockhey_gdt755_complete_whole_candidate_de"] == "mische"
        and qockhey_prov[0]["qockhey_gdt755_exact_occurrences"] == "12"
        and qockhey_prov[0]["qockhey_gdt755_boundary_complete_occurrences"] == "7",
        "published qockhey provenance retains quarantine and later source",
    )

    passages = read_tsv(PASSAGES)
    audit.check(len(passages) == 49, "passage output groups 50 spans into 49 loci")
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in atlas:
        grouped[row["locus"]].append(row)
    audit.check(
        set(grouped) == {row["locus"] for row in passages}
        and sum(int(row["target_count"]) for row in passages) == 50,
        "passage rows exactly cover selected loci and targets",
    )
    for row in passages:
        local = grouped[row["locus"]]
        audit.check(
            int(row["target_count"]) == len(local)
            and row["span_ids"] == "|".join(item["span_id"] for item in local)
            and row["target_occurrence_ids"] == "|".join(item["target_occurrence_id"] for item in local)
            and row["right_surfaces"] == "|".join(item["right_surface"] for item in local)
            and row["inherited_gdt778_patch_de"] != row["gdt779_practical_patch_de"],
            "grouped passage reconstruction " + row["locus"],
        )
    doubles = [
        (row["locus"], row["target_count"], row["right_surfaces"])
        for row in passages if row["target_count"] == "2"
    ]
    audit.check(
        doubles == [("f75r.26", "2", "sheol|qoly")],
        "only f75r.26 aggregates two targets in sheol-qoly order",
    )
    audit.check(
        zero_fields(passages, ("default_is_translation", "confirmed_plaintext", "component_export_credit")),
        "passages claim no translation, plaintext, or component export",
    )
    audit.check(
        sum(int(row["nonexact_fallback_exclusions"]) for row in dictionary)
        == sum(row["final_44_deck_member"] == "1" for row in exclusions),
        "dictionary and exclusion tables agree on final-deck nonexact rows",
    )


def validate_residual_relation_result(
    audit: Audit,
    renderer: Sequence[Mapping[str, str]],
    card_forms: set[str],
    raw_forms: set[str],
) -> None:
    residual = read_tsv(RESIDUAL)
    fallback = [row for row in renderer if row["gdt779_renderer_contextual"] == "0"]
    audit.check(len(residual) == len(fallback) == 131, "residual census covers all 131 fallbacks")
    audit.check(
        [row["target_occurrence_id"] for row in residual]
        == [row["target_occurrence_id"] for row in fallback],
        "residual census preserves every fallback in renderer order",
    )
    audit.check(
        all(
            row["residual_reason"]
            == expected_residual_reason(source, card_forms, EXPECTED_FORMS, raw_forms)
            for row, source in zip(residual, fallback)
        ),
        "every residual reason independently reconstructs from exactness and card state",
    )
    reason_counts = Counter(row["residual_reason"] for row in residual)
    audit.check(
        reason_counts == Counter({
            "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 25,
            "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
            "V99_CARD_NONEXACT_RAW_ONLY": 45,
            "V99_CARD_NONEXACT_FINAL44": 4,
            "LINE_FINAL_NO_RIGHT": 37,
        }),
        "residual reason split is exactly 25/20/45/4/37",
    )
    audit.check(zero_fields(residual, ("component_export_credit",)), "residuals export no components")

    packet = read_tsv(PACKET)
    crosswalk = read_tsv(CROSSWALK)
    atlas = read_tsv(ATLAS)
    audit.check(len(packet) == len(crosswalk) == len(atlas) == 50, "relation packet and crosswalk have 50 edges")
    audit.check(
        [row["edge_id"] for row in packet]
        == [row["edge_id"] for row in crosswalk]
        == [f"G779-E{number:03d}" for number in range(1, 51)],
        "relation edge IDs are complete, unique, and crosswalked",
    )
    audit.check(
        all(
            row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION"
            and row["geometry_only_selection"] == "FALSE"
            and row["formal_access_state"] == "SEALED_NOT_ACCESSED"
            and row["fold_assignment"] == "NONE"
            for row in packet
        ),
        "relation packet is explicitly nonvisual, ineligible, and unscored",
    )
    audit.check(
        all(
            row["score_eligible"] == "0"
            and row["selection_rule"] == SELECTION_RULE
            and row["component_export_credit"] == "0"
            for row in crosswalk
        ),
        "relation crosswalk preserves selection rule and zero score/component credit",
    )
    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    audit.check(intake == EXPECTED_INTAKE, "stored relation intake has exact not-score-ready result")
    gate = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    audit.check(gate.returncode == 0, "external check-edge-packet exits successfully")
    try:
        gate_value = json.loads(gate.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError("external edge-packet output is not JSON") from error
    audit.check(gate_value == EXPECTED_INTAKE, "external edge-packet gate reproduces stored intake")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT779", "RESULT experiment identity")
    audit.check(
        result["status"]
        == "PASS__50_EXACT_FALLBACK_WHOLES__44_FORMS__49_LOCI__245_CONTEXTUAL__131_FALLBACKS__205_CONSUMED__6_SANITIZATIONS__NO_COMPONENT_EXPORT",
        "RESULT exact PASS status",
    )
    audit.check(
        result["cohort"] == {
            "renderer_rows": 376, "raw_v99r7_candidates": 99, "raw_candidate_forms": 76,
            "reader_exact_selected_spans": 50, "selected_forms": 44,
            "exactness_exclusions": 49, "excluded_forms": 36, "loci": 49,
            "page_labels": 33, "physical_folios": 24,
        },
        "RESULT cohort values exact",
    )
    audit.check(
        result["precedence_shadow"] == {
            "raw_76_full_parent_matches": 179, "parent_fallback_matches": 99,
            "parent_contextual_matches": 80, "reader_exact_matches": 127,
            "selected_exact_fallback_matches": 50,
            "protected_exact_contextual_matches": 77,
            "final_44_raw_parent_matches": 68,
            "final_44_exact_parent_matches": 63,
            "final_44_protected_exact_contextual_matches": 13,
        },
        "RESULT precedence values exact",
    )
    audit.check(
        result["renderer"] == {
            "gdt778_contextual": 195, "gdt779_contextual": 245,
            "gdt778_fallbacks": 181, "gdt779_fallbacks": 131,
        },
        "RESULT renderer transition exact",
    )
    audit.check(
        result["consumption"] == {
            "gdt778_unique_right_tokens": 155, "gdt779_selected_right_tokens": 50,
            "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 50,
            "total_unique_right_tokens": 205, "cross_row_collisions": 0,
        },
        "RESULT consumption transition exact and collision-free",
    )
    audit.check(
        result["card_partition"] == dict(CLASS_COUNTS),
        "RESULT card partition exact",
    )
    audit.check(
        result["residual_partition"] == {
            "line_final_no_right": 37, "v99_card_nonexact": 49,
            "no_card_reader_nonexact": 20, "no_card_reader_exact": 25,
        },
        "RESULT residual partition exact",
    )
    audit.check(
        result["source_hygiene"] == {
            "patient_sanitizations": 6, "new_exact_ol_scopes": 3,
            "composition_derived_complete_wholes": 2,
            "qockhey_later_complete_whole_replacements": 1,
            "globally_exportable_v99_cards": 41,
            "old_literal_patient_leaks_outside_provenance": 0,
            "qockhey_source_composed_prose_used": False,
            "chol_confirmations_changed": 0,
            "ols_rejected_legacy_process_reading_restored": False,
        },
        "RESULT source hygiene exact including rejected ols restoration",
    )
    audit.check(
        result["relation_packet"] == EXPECTED_INTAKE
        and result["confirmed_lexemes"] == 0
        and result["confirmed_plaintext_clauses"] == 0
        and result["component_exports"] == 0
        and result["sealed_pages_accessed"] == 0
        and result["new_pages"] == result["new_images"] == result["new_ocr"]
        == result["new_transcriptions"] == 0,
        "RESULT relation, claim, sealed-data, and acquisition ceilings exact",
    )
    report = REPORT.read_text(encoding="utf-8")
    audit.check(
        "**50** Spannen in **44** Formen auf **49** loci" in report
        and "**195→245**" in report
        and "**181→131**" in report
        and "**155→205**" in report,
        "REPORT states cohort and renderer transitions",
    )
    audit.check(
        "37 Stellen" in report
        and "49 nicht-exakte Stellen mit V99R7-Karte" in report
        and "20 nicht-exakte" in report
        and "25 reader-exakte" in report,
        "REPORT states complete residual debt split",
    )
    audit.check(
        "f84" in report and "f84r" in report,
        "REPORT explicitly records both sealed pages",
    )


def validate_hygiene(audit: Audit) -> None:
    tabular_outputs = (
        ATLAS, EXCLUSIONS, SHADOW, RENDERER, DICTIONARY, PASSAGES,
        PROVENANCE, RESIDUAL, PACKET, CROSSWALK,
    )
    for path in tabular_outputs:
        rows = read_tsv(path)
        audit.check(
            all(
                not any(
                    SEALED_RE.search(value)
                    for value in row.values()
                )
                for row in rows
            ),
            "sealed f84/f84r absent from " + path.name,
        )
    for path in (ATLAS, EXCLUSIONS, SHADOW, RENDERER, DICTIONARY, PASSAGES, RESIDUAL, PACKET, CROSSWALK, INTAKE, RESULT, ARTIFACT_README):
        audit.check(
            PATIENT_RE.search(path.read_text(encoding="utf-8")) is None,
            "retired patient wording absent outside provenance: " + path.name,
        )
    audit.check(
        PATIENT_RE.search(REPORT.read_text(encoding="utf-8")) is None,
        "retired patient wording absent from REPORT",
    )
    renderer = read_tsv(RENDERER)
    by_target = unique(renderer, "target_occurrence_id")
    protected = [
        row for row in renderer if row["gdt778_exact_whole"] in {"chol", "ols"}
    ]
    audit.check(
        Counter(row["gdt778_exact_whole"] for row in protected)
        == Counter({"chol": 2, "ols": 1}),
        "two chol and one ols inherited control rows found",
    )
    audit.check(
        all(
            row["gdt779_branch"] == "INHERITED_GDT778"
            and active_state_equal(row, by_target[row["target_occurrence_id"]])
            for row in protected
        ),
        "chol and ols controls remain inherited without restoration",
    )


def byte_replay(audit: Audit, runner_hash_before: str) -> dict[str, str]:
    published_hashes = {str(path.relative_to(EXP)): sha256(path) for path in REPLAY_OUTPUTS}
    with tempfile.TemporaryDirectory(prefix="gdt779-validator-") as temporary:
        temp = Path(temporary)
        temp_artifacts = temp / "artifacts"
        temp_report = temp / "REPORT.md"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        replay = subprocess.run(
            [
                sys.executable, "-B", str(RUN),
                "--artifacts-dir", str(temp_artifacts),
                "--report-path", str(temp_report),
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        audit.check(replay.returncode == 0, "runner tempdir replay exits successfully")
        for published in REPLAY_OUTPUTS:
            generated = temp_report if published == REPORT else temp_artifacts / published.name
            audit.check(generated.is_file(), "replay generated " + published.name)
            audit.check(
                generated.read_bytes() == published.read_bytes(),
                "byte replay exact for " + published.name,
            )
    audit.check(sha256(RUN) == runner_hash_before, "runner hash stable across replay")
    return published_hashes


def main() -> int:
    audit = Audit()
    runner_hash = sha256(RUN)
    source_hashes = validate_source_locks(audit)
    validate_runner_ast(audit)
    _, specs = validate_specs(audit)
    parent, selected, rejected, raw_forms, cards = validate_selection(audit, specs)
    atlas, exclusions, _ = validate_atlas_and_exclusions(
        audit, parent, selected, rejected, specs,
    )
    renderer = validate_renderer_and_shadow(
        audit, parent, selected, raw_forms, specs, atlas,
    )
    validate_dictionary_provenance_passages(audit, specs, atlas, exclusions)
    validate_residual_relation_result(audit, renderer, set(cards), raw_forms)
    validate_hygiene(audit)
    output_hashes = byte_replay(audit, runner_hash)

    value = {
        "experiment_id": "GDT779",
        "status": "PASS",
        "validator_independence": "SOURCE_HASHED__PREDICATE_RECONSTRUCTED__AST_GATED__BYTE_REPLAYED",
        "checks_passed": audit.count,
        "runner_output_replay_count": len(REPLAY_OUTPUTS),
        "source_hash_count": len(source_hashes),
        "source_hashes": source_hashes,
        "spec_sha256": sha256(SPECS),
        "runner_sha256": runner_hash,
        "runner_output_sha256": output_hashes,
        "selection": {
            "selected_spans": 50, "selected_forms": 44,
            "grouped_loci": 49, "page_labels": 33, "physical_folios": 24,
            "nonexact_exclusions": 49, "excluded_forms": 36,
            "selection_uses_occurrence_id": False,
            "selection_uses_semantics": False,
            "selection_uses_substrings": False,
        },
        "precedence": {
            "raw_parent_rows": 179, "raw_exact_rows": 127,
            "final_parent_rows": 68, "final_exact_rows": 63,
            "protected_raw_exact_contexts": 77,
            "protected_final_exact_contexts": 13,
        },
        "renderer": {
            "contextual_before": 195, "contextual_after": 245,
            "fallback_before": 181, "fallback_after": 131,
            "consumed_before": 155, "consumed_after": 205,
            "cross_row_collisions": 0,
        },
        "relation_packet_gate": EXPECTED_INTAKE,
        "errors": [],
    }
    destination = ART / "VALIDATION.json"
    destination.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
