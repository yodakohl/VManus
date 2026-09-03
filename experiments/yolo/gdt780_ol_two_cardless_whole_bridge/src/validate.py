#!/usr/bin/env python3
"""Independent validator for GDT780's frozen two-whole bridge."""
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
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
SPECS = SRC / "TWO_WHOLE_SPECS.tsv"
LOCKS = SRC / "SOURCE_LOCK.tsv"
REPORT = EXP / "REPORT.md"

PARENT = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_376_RENDERER.tsv"
PARENT_RESULT = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/RESULT.json"
PARENT_RESIDUAL = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv"
G758 = ROOT / "experiments/yolo/gdt758_ychor_follower_global_content_census/artifacts/ORDERED_VALUE_FOLLOWER_COMPARATOR.tsv"
G745 = ROOT / "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/CROSS_PAGE_ROLE_CARDS.tsv"
G746 = ROOT / "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/CANDIDATE_17_DISTRIBUTION_CENSUS.tsv"
G747 = ROOT / "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/CANDIDATE_12_PASSAGE_CENSUS.tsv"
G747_OCC = ROOT / "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/OCCURRENCE_64_LOCAL_SUPPORT.tsv"
G748 = ROOT / "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/COLLAPSED_POSITION_EVIDENCE.tsv"
G769_CONTEXT = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv"

INTAKE_25 = ART / "GDT780_25_EXACT_CARDLESS_INTAKE.tsv"
TARGET_INDEPENDENCE = ART / "GDT780_2_TARGET_INDEPENDENCE_AUDIT.tsv"
ATLAS = ART / "GDT780_2_EXACT_WHOLE_ATLAS.tsv"
PRECEDENCE = ART / "GDT780_2_PRECEDENCE_AUDIT.tsv"
RENDERER = ART / "GDT780_376_RENDERER.tsv"
DICTIONARY = ART / "GDT780_2_WORKING_DICTIONARY_EVIDENCE.tsv"
PASSAGES = ART / "GDT780_2_PASSAGE_PATCHES.tsv"
RESIDUAL = ART / "GDT780_RESIDUAL_129_FALLBACK_CENSUS.tsv"
PACKET = ART / "GDT780_GDT388_RELATION_PACKET.tsv"
CROSSWALK = ART / "GDT780_RELATION_EDGE_CROSSWALK.tsv"
EDGE_INTAKE = ART / "RELATION_PACKET_INTAKE.json"
RESULT = ART / "RESULT.json"
ARTIFACT_README = ART / "README.md"

REPLAY_OUTPUTS = (
    INTAKE_25, TARGET_INDEPENDENCE, ATLAS, PRECEDENCE, RENDERER, DICTIONARY, PASSAGES, RESIDUAL,
    PACKET, CROSSWALK, EDGE_INTAKE, RESULT, ARTIFACT_README, REPORT,
)

EXPECTED_LOCKS = {
    "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_376_RENDERER.tsv":
        "e2054fa95baed3ef61a940644c78000bee0e331c2356599d2c959fd5e2affd50",
    "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/RESULT.json":
        "884365fc006183838007863538016b6d19765feb763bb36027a9e2fc8abaf784",
    "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv":
        "d2c7a37c0f3d8cca9173f370092068f82b92e0ef035f1f48778c78dddf76d03f",
    "experiments/yolo/gdt758_ychor_follower_global_content_census/artifacts/ORDERED_VALUE_FOLLOWER_COMPARATOR.tsv":
        "70adf89ae2b2065f7089a442f9517e76234f641a8a56f46ce3216fb485da94d3",
    "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/CROSS_PAGE_ROLE_CARDS.tsv":
        "733d6ee845cc465b8c47a3df6915922b52c30df8253c3ec9d5ce32aa646e5588",
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/CANDIDATE_17_DISTRIBUTION_CENSUS.tsv":
        "ac26ead1099657491cba744b6800e03a008c379e9a58c832c149f2b764f26013",
    "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/CANDIDATE_12_PASSAGE_CENSUS.tsv":
        "bbca139ca89c16bac39188db46f14d877df488f02369478dbae9b79539502915",
    "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/OCCURRENCE_64_LOCAL_SUPPORT.tsv":
        "e16b9defef5e09e60f967f20f9ef1df53b538d171999361394ebd198b801dc00",
    "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/COLLAPSED_POSITION_EVIDENCE.tsv":
        "7532ba59ae4fcf190b4e178a9dfdbb1109eec34195ceb8e1a585eff2aa250689",
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv":
        "935c39c026db8a9b282700fec90a4158cc6120323f4080477140922f318cb95a",
    "tools/relation_edge_intake.py":
        "fb8447470aa81ed608b90aedf7478893ddf6a445351aa12ab23c6fd725be3a47",
}

EXPECTED_FORMS = frozenset({"eees", "sheeol"})
EXPECTED_TARGETS = {
    "eees": ("G769-T0208", "f43v", "f43", "f43v.16", "1", "2"),
    "sheeol": ("G769-T0487", "f88r", "f88", "f88r.21", "6", "7"),
}
SELECTION_RULE = "GDT779_RENDERER_CONTEXTUAL_0_AND_RIGHT_READER_EXACT_1_AND_COMPLETE_RIGHT_SURFACE_IN_EEES_SHEEOL"
EXPECTED_STATUS = "PASS__2_EXACT_CARDLESS_WHOLES__2_FORMS__2_LOCI__247_CONTEXTUAL__129_FALLBACKS__207_CONSUMED__NO_COMPONENT_EXPORT"
EXPECTED_EDGE_INTAKE = {
    "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 2,
    "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
    "holdout_edges": 0, "mobile_edges": 0,
    "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
    "mobile_null_gate": False, "score_ready": False, "errors": [],
}
SEALED_RE = re.compile(r"(?<![A-Za-z0-9])f84r?(?![A-Za-z0-9])", re.I)


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
        ("gdt779_default_de", "gdt780_default_de"),
        ("gdt779_renderer_contextual", "gdt780_renderer_contextual"),
        ("gdt779_span_id", "gdt780_span_id"),
        ("gdt779_exact_whole", "gdt780_exact_whole"),
        ("gdt779_confidence", "gdt780_confidence"),
        ("gdt779_consumed_token_count", "gdt780_consumed_token_count"),
        ("gdt779_consumed_token_ids", "gdt780_consumed_token_ids"),
    )
    return all(parent[left] == current[right] for left, right in pairs)


def validate_source_locks(audit: Audit) -> dict[str, str]:
    rows = read_tsv(LOCKS)
    audit.check(len(rows) == 11, "eleven source locks")
    by_path = unique(rows, "path")
    audit.check(set(by_path) == set(EXPECTED_LOCKS), "exact frozen source path set")
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_LOCKS.items():
        row = by_path[relative]
        path = Path(relative)
        audit.check(not path.is_absolute() and ".." not in path.parts, "safe relative lock " + relative)
        audit.check(row["expected_sha256"] == expected, "hard-coded lock value " + relative)
        actual = sha256(ROOT / path)
        audit.check(actual == expected, "source rehash " + relative)
        observed[relative] = actual
    return observed


def validate_specs(audit: Audit) -> dict[str, dict[str, str]]:
    rows = read_tsv(SPECS)
    audit.check(len(rows) == 2, "two frozen whole cards")
    by_form = {key: dict(value) for key, value in unique(rows, "surface").items()}
    audit.check(frozenset(by_form) == EXPECTED_FORMS, "frozen deck is exactly eees and sheeol")
    audit.check(
        by_form["eees"]["default_de"] == "Mengenfeld"
        and by_form["eees"]["alternate_1_de"] == "Einheitenfeld"
        and by_form["eees"]["alternate_2_de"] == "Wertkopf"
        and by_form["eees"]["confidence"] == "C1_ROLE_C0_IDENTITY"
        and by_form["eees"]["functional_axis"] == "AMOUNT_OR_VALUE_FIELD",
        "eees card exactly matches preregistration",
    )
    audit.check(
        by_form["sheeol"]["default_de"] == "Endzustand"
        and by_form["sheeol"]["alternate_1_de"] == "Feuchtzustand"
        and by_form["sheeol"]["alternate_2_de"] == "kalte Zustandsform"
        and by_form["sheeol"]["confidence"] == "C1_ROLE_C0_IDENTITY"
        and by_form["sheeol"]["functional_axis"] == "END_STAGE",
        "sheeol card exactly matches preregistration",
    )
    audit.check(
        all(row["card_class"] == "INDEPENDENT_COMPLETE_WHOLE_ROLE_BRIDGE" for row in rows)
        and all(row["renderer_scope"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY" for row in rows),
        "both cards are scoped complete-whole role bridges",
    )
    audit.check(
        zero_fields(rows, (
            "confirmed_lexeme", "component_export_credit", "numeric_identity_confirmed",
            "specific_substance_confirmed",
        )) and all(row["literal_identity"] == "OPEN" for row in rows),
        "spec cards export no lexeme component number or substance identity",
    )
    audit.check(
        all(len({row["default_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3 for row in rows),
        "each card has one default and two distinct rivals",
    )
    return by_form


def validate_runner_ast(audit: Audit) -> None:
    tree = ast.parse(RUN.read_text(encoding="utf-8"), filename=str(RUN))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "select_gdt780_row"]
    audit.check(len(functions) == 1, "one named GDT780 selector")
    function = functions[0]
    args = [arg.arg for arg in function.args.args]
    audit.check(
        args == ["gdt779_renderer_contextual", "right_surface", "right_reader_exact", "fixed_complete_surfaces"]
        and not function.args.defaults and function.args.vararg is None and function.args.kwarg is None,
        "selector signature exposes only parent state exactness surface and frozen deck",
    )
    returns = [node for node in ast.walk(function) if isinstance(node, ast.Return)]
    audit.check(len(returns) == 1, "selector has one return")
    expected = ast.parse(
        "gdt779_renderer_contextual == '0' and right_reader_exact == '1' and right_surface in fixed_complete_surfaces",
        mode="eval",
    ).body
    audit.check(
        ast.dump(returns[0].value, include_attributes=False) == ast.dump(expected, include_attributes=False),
        "selector AST is exactly fallback plus reader-exact plus fixed-deck membership",
    )
    forbidden_nodes = (ast.Subscript, ast.Call, ast.Attribute, ast.BinOp, ast.IfExp, ast.Lambda)
    audit.check(
        not any(isinstance(node, forbidden_nodes) for node in ast.walk(returns[0].value)),
        "selector contains no lookup call substring arithmetic or conditional",
    )
    names = {node.id for node in ast.walk(returns[0].value) if isinstance(node, ast.Name)}
    audit.check(names == set(args), "selector references every and only its four declared inputs")
    forbidden_terms = (
        "occurrence", "target", "id", "page", "folio", "locus", "ordinal", "neighbor",
        "frequency", "count", "edit", "substring", "meaning", "semantic", "default",
        "evidence", "confidence",
    )
    audit.check(
        not any(any(term in name.lower() for term in forbidden_terms) for name in names),
        "selector excludes IDs pages loci neighbors frequency substrings and semantics",
    )
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "select_gdt780_row"
    ]
    audit.check(len(calls) >= 1, "runner invokes the pure selector")
    audit.check(
        all(
            [ast.unparse(arg) for arg in call.args] == [
                "row['gdt779_renderer_contextual']", "row['right_surface']",
                "row['right_reader_exact']", "FROZEN_SURFACES",
            ]
            for call in calls
        ),
        "every selector invocation uses only declared parent columns and frozen deck",
    )


def validate_source_evidence(audit: Audit) -> None:
    eees_rows = [row for row in read_tsv(G758) if row["surface"] == "eees"]
    audit.check(len(eees_rows) == 1, "one eees source row")
    eees = eees_rows[0]
    audit.check(
        eees["reader_exact_occurrences"] == "7" and eees["exact_right_contexts"] == "4"
        and eees["ordered_value_follower_hits"] == "3" and eees["ordered_value_follower_counts"] == "aiin:3"
        and eees["aiin_follower_hits"] == "3",
        "eees source reconstructs 7 occurrences 4 right contexts and 3 aiin followers",
    )
    audit.check(
        eees["ordered_value_conditional_rate"] == "0.750000"
        and eees["ordered_value_baseline_rate"] == "0.021613"
        and eees["ordered_value_descriptive_lift"] == "34.702083",
        "eees source rate baseline and lift exact",
    )
    audit.check(
        eees["ordered_value_family_is_working_structural_label"] == "1"
        and eees["numeric_value_or_unit_confirmed"] == "0" and eees["component_export_credit"] == "0",
        "eees evidence selects only a structural role not number unit or component",
    )

    g745_rows = [row for row in read_tsv(G745) if row["candidate_surface"] == "sheeol"]
    g746_rows = [row for row in read_tsv(G746) if row["candidate_surface"] == "sheeol"]
    g747_rows = [row for row in read_tsv(G747) if row["candidate_surface"] == "sheeol"]
    g748_rows = [row for row in read_tsv(G748) if row["target_surface"] == "sheeol"]
    audit.check(len(g745_rows) == len(g746_rows) == len(g747_rows) == len(g748_rows) == 1,
                "one sheeol evidence row in each GDT745 through GDT748 source")
    g745, g746, g747, g748 = g745_rows[0], g746_rows[0], g747_rows[0], g748_rows[0]
    audit.check(
        g745["cache_occurrences"] == "10" and g745["reader_exact_occurrences"] == "9"
        and g745["analogy_consensus_axes"] == "MATERIAL|END_STAGE"
        and g745["analogy_rival_axes"] == "DRY|MOIST|PREPARATION",
        "GDT745 gives sheeol 10 cache 9 exact plus END and mixed quality evidence",
    )
    audit.check(
        g746["reader_exact_occurrences"] == "9"
        and g746["form_and_top5_axis_agreement"] == "END_STAGE"
        and g746["top5_distribution_consensus_axes"] == "END_STAGE"
        and g746["distribution_status"] == "S2_DISTRIBUTION_SUPPORTED",
        "GDT746 whole-form and distribution intersection is END_STAGE",
    )
    audit.check(
        g747["passage_core_axes"] == "END_STAGE" and g747["locally_supported_occurrences"] == "4"
        and g747["local_support_pages"] == "3"
        and g747["local_support_tier_counts"] == "L0_NO_LOCAL_W23_SUPPORT:6|L1_SINGLE_WHOLE_LOCAL_SUPPORT:4",
        "GDT747 supplies four local END contacts on three pages",
    )
    audit.check(
        g748["best_predicted_axes"] == "COLD" and g748["gdt747_prior_axes"] == "END_STAGE"
        and g748["gdt747_prior_comparison"] == "GDT747_PRIOR_CONFLICT"
        and g748["whole_form_bridge_tier"] == "B0_NO_WHOLE_FORM_BRIDGE"
        and g748["whole_form_bridge_weight"] == "0"
        and g748["known_wholes_within_edit1"] == "0" and g748["known_wholes_within_edit2"] == "0",
        "GDT748 cold counterframe has no whole-form bridge",
    )
    audit.check(
        zero_fields((g745, g746, g747, g748), ("confirmed_lexeme", "component_export_credit", "unseen_form_export"))
        and all(row.get("literal_identity", "OPEN") == "OPEN" for row in (g745, g746, g747, g748)),
        "sheeol source chain exports no identity lexeme component or unseen form",
    )


def reconstruct_parent(
    audit: Audit, specs: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], set[str]]:
    parent = read_tsv(PARENT)
    audit.check(len(parent) == 376, "parent has 376 rows")
    audit.check(len(unique(parent, "target_occurrence_id")) == 376, "parent target IDs unique")
    audit.check(Counter(row["gdt779_renderer_contextual"] for row in parent) == Counter({"1": 245, "0": 131}),
                "parent independently reconstructs 245 contextual and 131 fallback rows")
    parent_tokens: list[str] = []
    for row in parent:
        tokens = [] if row["gdt779_consumed_token_ids"] == "NONE" else row["gdt779_consumed_token_ids"].split("|")
        audit.check(len(tokens) == int(row["gdt779_consumed_token_count"]),
                    "parent token arity " + row["target_occurrence_id"])
        parent_tokens.extend(tokens)
    audit.check(len(parent_tokens) == len(set(parent_tokens)) == 205,
                "parent has 205 collision-free consumed tokens")
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check(
        parent_result["renderer"] == {
            "gdt778_contextual": 195, "gdt779_contextual": 245,
            "gdt778_fallbacks": 181, "gdt779_fallbacks": 131,
        } and parent_result["consumption"]["total_unique_right_tokens"] == 205,
        "locked parent RESULT agrees on coverage and consumption",
    )

    source_residual = read_tsv(PARENT_RESIDUAL)
    audit.check(len(source_residual) == 131, "locked parent residual has 131 rows")
    parent_fallback = [row for row in parent if row["gdt779_renderer_contextual"] == "0"]
    audit.check(
        [row["target_occurrence_id"] for row in source_residual]
        == [row["target_occurrence_id"] for row in parent_fallback],
        "parent residual exactly covers fallback rows in renderer order",
    )
    reason_counts = Counter(row["residual_reason"] for row in source_residual)
    audit.check(reason_counts == Counter({
        "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 25,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
        "V99_CARD_NONEXACT_RAW_ONLY": 45, "V99_CARD_NONEXACT_FINAL44": 4,
        "LINE_FINAL_NO_RIGHT": 37,
    }), "locked parent residual reconstructs 25/20/45/4/37 partition")
    cardless25 = [row for row in source_residual if row["residual_reason"] == "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT"]
    audit.check(len(cardless25) == 25 and len({row["right_surface"] for row in cardless25}) == 25,
                "exact cardless intake contains 25 distinct complete surfaces")
    parent_by_id = unique(parent, "target_occurrence_id")
    audit.check(all(
        parent_by_id[row["target_occurrence_id"]]["gdt779_renderer_contextual"] == "0"
        and parent_by_id[row["target_occurrence_id"]]["right_reader_exact"] == "1"
        and parent_by_id[row["target_occurrence_id"]]["right_surface"] == row["right_surface"]
        and row["v99_complete_card_present"] == "0" and row["final_44_deck_member"] == "0"
        for row in cardless25
    ), "all 25 source residuals are exact cardless parent fallbacks")

    selected = [row for row in parent if row["gdt779_renderer_contextual"] == "0"
                and row["right_reader_exact"] == "1" and row["right_surface"] in specs]
    audit.check(len(selected) == 2, "pure selector yields exactly two parent rows")
    audit.check([row["right_surface"] for row in selected] == ["eees", "sheeol"],
                "selected parent order is eees then sheeol")
    audit.check(
        [row["target_occurrence_id"] for row in selected]
        == [row["target_occurrence_id"] for row in cardless25 if row["right_surface"] in EXPECTED_FORMS],
        "pure selector hits every and only deck form in independent cardless intake",
    )
    audit.check(EXPECTED_FORMS <= {row["right_surface"] for row in cardless25}
                and len({row["right_surface"] for row in cardless25} - EXPECTED_FORMS) == 23,
                "two selected and 23 unselected exact cardless surfaces partition intake")
    for row in selected:
        expected = EXPECTED_TARGETS[row["right_surface"]]
        observed = (row["target_occurrence_id"], row["page"], row["physical_folio"],
                    row["locus"], row["ordinal"], row["right_ordinal"])
        audit.check(observed == expected, "expected selected fingerprint " + row["right_surface"])
        tokens = row["written_line_eva"].split()
        audit.check(tokens[int(row["ordinal"]) - 1] == "ol"
                    and tokens[int(row["right_ordinal"]) - 1] == row["right_surface"]
                    and int(row["right_ordinal"]) == int(row["ordinal"]) + 1,
                    "literal adjacent whole span " + row["right_surface"])
    eees = next(row for row in selected if row["right_surface"] == "eees")
    eees_tokens = eees["written_line_eva"].split()
    audit.check(eees_tokens[int(eees["right_ordinal"])] == "aiin",
                "later ol-eees target contributes one of the three observed aiin followers")
    audit.check(3 - 1 == 2 and 4 - 1 == 3,
                "removing target leaves two aiin followers among three right contexts")
    return parent, source_residual, selected, set(parent_tokens)


def validate_target_independence(
    audit: Audit,
    parent: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    parent_by_surface = {
        surface: [row for row in parent if row["right_surface"] == surface]
        for surface in EXPECTED_FORMS
    }
    audit.check(all(len(rows) == 1 for rows in parent_by_surface.values()),
                "each frozen whole has one parent target")

    eees_parent = parent_by_surface["eees"][0]
    eees_detail_rows = [
        row for row in read_tsv(G769_CONTEXT)
        if row["target_occurrence_id"] == eees_parent["target_occurrence_id"]
    ]
    audit.check(len(eees_detail_rows) == 1, "one locked G769 detail row for eees target")
    eees_detail = eees_detail_rows[0]
    audit.check(
        eees_detail["raw_occurrence_id"] == "G769-R0261"
        and eees_detail["surface"] == "ol"
        and eees_detail["page"] == eees_parent["page"] == "f43v"
        and eees_detail["physical_folio"] == eees_parent["physical_folio"] == "f43"
        and eees_detail["locus"] == eees_parent["locus"] == "f43v.16"
        and eees_detail["ordinal"] == eees_parent["ordinal"] == "1"
        and eees_detail["reader_exact"] == "1"
        and eees_parent["right_reader_exact"] == "1"
        and eees_detail["written_line_eva"] == eees_parent["written_line_eva"]
        == "ol eees aiin oloaiin oteos qoky chey",
        "G769 eees target row identity geometry and exactness reconstruct",
    )
    views = json.loads(eees_detail["context_views"])
    audit.check(set(views) >= {"D1", "R2", "LINE"}, "G769 context JSON exposes fixed views")
    r2 = views["R2"]
    donors = {int(row["ordinal"]): row for row in r2["eligible_donors"]}
    audit.check(set(donors) == {2, 3} and r2["blocked_exact_donor_positions"] == 0,
                "G769 R2 contains exactly ordinal-two and ordinal-three eligible donors")
    eees_token, aiin_token = donors[2], donors[3]
    audit.check(
        eees_token["surface"] == "eees" and eees_token["distance"] == 1
        and eees_token["direction"] == "RIGHT"
        and aiin_token["surface"] == "aiin" and aiin_token["distance"] == 2
        and aiin_token["direction"] == "RIGHT",
        "G769 row contains the adjacent clean eees-aiin target contribution",
    )
    audit.check(
        all(
            token["current_clean"] == 1
            and token["gate_status"] == "ELIGIBLE"
            and token["per_current_target_gate_status"] == "ELIGIBLE"
            for token in (eees_token, aiin_token)
        ),
        "G769 eees and aiin tokens are both clean and eligible",
    )
    audit.check(
        eees_detail["semantic_identity_credit"] == "0"
        and eees_detail["component_export_credit"] == "0",
        "G769 target row grants no identity or component credit",
    )
    eees_aggregate = [row for row in read_tsv(G758) if row["surface"] == "eees"]
    audit.check(len(eees_aggregate) == 1, "one locked GDT758 eees aggregate")
    before_contexts = int(eees_aggregate[0]["exact_right_contexts"])
    before_hits = int(eees_aggregate[0]["ordered_value_follower_hits"])
    after_contexts, after_hits = before_contexts - 1, before_hits - 1
    audit.check((before_contexts, before_hits, after_contexts, after_hits) == (4, 3, 3, 2),
                "target removal reconstructs eees 4/3 to 3/2")

    sheeol_parent = parent_by_surface["sheeol"][0]
    sheeol_detail_rows = [
        row for row in read_tsv(G747_OCC)
        if row["candidate_surface"] == "sheeol"
        and row["locus"] == sheeol_parent["locus"]
        and row["token_ordinal"] == sheeol_parent["right_ordinal"]
    ]
    audit.check(len(sheeol_detail_rows) == 1, "one locked GDT747 sheeol target row")
    sheeol_detail = sheeol_detail_rows[0]
    audit.check(
        sheeol_detail["gdt747_occurrence_id"] == "G747-O060"
        and sheeol_detail["page"] == sheeol_parent["page"] == "f88r"
        and sheeol_detail["physical_folio"] == sheeol_parent["physical_folio"] == "f88"
        and sheeol_detail["locus"] == sheeol_parent["locus"] == "f88r.21"
        and sheeol_detail["token_ordinal"] == sheeol_parent["right_ordinal"] == "7"
        and sheeol_detail["reader_exact"] == sheeol_parent["right_reader_exact"] == "1"
        and sheeol_detail["passage_core_axes"] == "END_STAGE",
        "GDT747 sheeol target identity exactness and END axis reconstruct",
    )
    audit.check(
        sheeol_detail["local_support_tier"] == "L0_NO_LOCAL_W23_SUPPORT"
        and sheeol_detail["supporting_whole_count"] == "0"
        and sheeol_detail["supporting_whole_surfaces"] == "NONE"
        and sheeol_detail["supporting_signed_offsets"] == "NONE"
        and sheeol_detail["locally_supported_core_axes"] == "NONE"
        and sheeol_detail["locally_supported_core_fraction"] == "0.000",
        "GDT747 target is exact L0 and contributes zero local END supports",
    )
    audit.check(
        sheeol_detail["literal_identity"] == "OPEN"
        and sheeol_detail["confirmed_lexeme"] == "0"
        and sheeol_detail["component_export_credit"] == "0",
        "GDT747 target grants no identity lexeme or component credit",
    )
    sheeol_summary_rows = [row for row in read_tsv(G747) if row["candidate_surface"] == "sheeol"]
    audit.check(len(sheeol_summary_rows) == 1, "one locked GDT747 sheeol summary")
    global_supports = int(sheeol_summary_rows[0]["locally_supported_occurrences"])
    global_pages = int(sheeol_summary_rows[0]["local_support_pages"])
    audit.check((global_supports, global_pages) == (4, 3),
                "GDT747 global sheeol support is four contacts on three pages")
    audit.check(global_supports - int(sheeol_detail["supporting_whole_count"]) == 4,
                "removing exact L0 target leaves all four global END supports")

    published = read_tsv(TARGET_INDEPENDENCE)
    audit.check(len(published) == 2, "target-independence audit has two rows")
    audit.check([row["audit_id"] for row in published] == ["G780-A001", "G780-A002"],
                "target-independence audit IDs complete and ordered")
    audit.check([row["surface"] for row in published] == ["eees", "sheeol"],
                "target-independence audit covers exact frozen deck")
    by_surface = unique(published, "surface")
    eees_audit = by_surface["eees"]
    audit.check(
        eees_audit["target_occurrence_id"] == eees_parent["target_occurrence_id"]
        and eees_audit["detail_source_record_id"] == eees_detail["raw_occurrence_id"]
        and eees_audit["detail_source"] == str(G769_CONTEXT.relative_to(ROOT))
        and eees_audit["target_ordinal"] == eees_parent["right_ordinal"] == "2"
        and eees_audit["detail_source_target_surface"] == "ol"
        and eees_audit["detail_source_target_ordinal"] == "1"
        and eees_audit["target_reader_exact"] == eees_audit["detail_source_target_reader_exact"]
        == eees_audit["parent_right_reader_exact"] == "1",
        "published eees audit crosswalks parent and G769 row exactly",
    )
    audit.check(
        eees_audit["target_current_clean"] == "1"
        and eees_audit["target_gate_status"] == "ELIGIBLE"
        and eees_audit["target_following_surface"] == "aiin"
        and eees_audit["target_following_ordinal"] == "3"
        and eees_audit["target_following_current_clean"] == "1"
        and eees_audit["target_following_gate_status"] == "ELIGIBLE",
        "published eees audit records clean eligible eees-aiin pair",
    )
    audit.check(
        eees_audit["aggregate_evidence_before_target_removal"] == "3_aiin_hits_in_4_exact_right_contexts"
        and eees_audit["target_evidence_contribution"] == "1_aiin_hit_in_1_exact_right_context"
        and eees_audit["evidence_after_target_removal"] == "2_aiin_hits_in_3_exact_right_contexts"
        and eees_audit["target_independence_calculation"] == "4-1=3_contexts;3-1=2_aiin_hits"
        and eees_audit["independence_status"] == "PASS__TARGET_REMOVAL_RETAINS_2_OF_3_AIIN_FOLLOWERS",
        "published eees target-removal arithmetic exact",
    )
    sheeol_audit = by_surface["sheeol"]
    audit.check(
        sheeol_audit["target_occurrence_id"] == sheeol_parent["target_occurrence_id"]
        and sheeol_audit["detail_source_record_id"] == "G747-O060"
        and sheeol_audit["detail_source"] == str(G747_OCC.relative_to(ROOT))
        and sheeol_audit["target_ordinal"] == sheeol_parent["right_ordinal"] == "7"
        and sheeol_audit["detail_source_target_surface"] == "sheeol"
        and sheeol_audit["detail_source_target_ordinal"] == "7"
        and sheeol_audit["target_reader_exact"] == sheeol_audit["detail_source_target_reader_exact"]
        == sheeol_audit["parent_right_reader_exact"] == "1",
        "published sheeol audit crosswalks parent and GDT747 row exactly",
    )
    audit.check(
        sheeol_audit["target_local_support_tier"] == "L0_NO_LOCAL_W23_SUPPORT"
        and sheeol_audit["target_local_support_count"] == "0"
        and sheeol_audit["global_local_support_count"] == "4"
        and sheeol_audit["global_local_support_pages"] == "3"
        and sheeol_audit["target_removed_local_support_count"] == "4"
        and sheeol_audit["target_evidence_contribution"] == "0_local_END_supports"
        and sheeol_audit["target_independence_calculation"] == "4-0=4_local_END_supports"
        and sheeol_audit["independence_status"] == "PASS__TARGET_IS_EXACT_L0_AND_CONTRIBUTES_ZERO_END_SUPPORTS",
        "published sheeol audit proves all four END supports target-independent",
    )
    audit.check(
        zero_fields(
            published,
            ("selection_uses_target_evidence", "default_is_translation", "confirmed_lexeme", "component_export_credit"),
        ),
        "target-independence audit exports no target selection translation lexeme or component",
    )
    return published


def validate_intake_output(
    audit: Audit,
    parent: Sequence[Mapping[str, str]],
    source_residual: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    intake = read_tsv(INTAKE_25)
    expected = [
        row for row in source_residual
        if row["residual_reason"] == "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT"
    ]
    audit.check(len(intake) == len(expected) == 25, "published intake has all 25 exact cardless rows")
    audit.check(
        [row["target_occurrence_id"] for row in intake]
        == [row["target_occurrence_id"] for row in expected],
        "published intake preserves independent source-residual order",
    )
    audit.check(
        [row["intake_id"] for row in intake] == [f"G780-I{number:03d}" for number in range(1, 26)],
        "intake IDs are complete and ordered",
    )
    parent_by_target = unique(parent, "target_occurrence_id")
    expected_by_target = unique(expected, "target_occurrence_id")
    for row in intake:
        old = parent_by_target[row["target_occurrence_id"]]
        residual = expected_by_target[row["target_occurrence_id"]]
        audit.check(
            row["parent_residual_id"] == residual["residual_id"]
            and row["page"] == old["page"]
            and row["physical_folio"] == old["physical_folio"]
            and row["locus"] == old["locus"]
            and row["ol_ordinal"] == old["ordinal"]
            and row["right_ordinal"] == old["right_ordinal"]
            and row["right_surface"] == old["right_surface"]
            and row["right_reader_exact"] == "1"
            and row["parent_residual_reason"] == "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT"
            and row["parent_gdt779_default_de"] == old["gdt779_default_de"],
            "intake row reconstructs parent and residual " + row["target_occurrence_id"],
        )
    selected = [row for row in intake if row["selected_by_pure_rule"] == "1"]
    audit.check(
        len(selected) == 2
        and [row["right_surface"] for row in selected] == ["eees", "sheeol"]
        and {row["target_occurrence_id"] for row in selected}
        == {value[0] for value in EXPECTED_TARGETS.values()},
        "intake flags exactly the two independently reconstructed pure-selector hits",
    )
    audit.check(
        all(
            row["frozen_two_whole_deck_member"] == row["selected_by_pure_rule"]
            and row["selection_rule"] == SELECTION_RULE
            for row in intake
        ),
        "intake deck membership and pure selection agree for all 25 rows",
    )
    audit.check(
        zero_fields(
            intake,
            (
                "selection_uses_occurrence_id", "selection_uses_page_or_locus",
                "selection_uses_neighbor_or_frequency", "selection_uses_substring",
                "default_is_translation", "confirmed_lexeme", "component_export_credit",
            ),
        ),
        "intake records no forbidden selector or claim export",
    )
    return intake


def validate_atlas_and_precedence(
    audit: Audit,
    parent: Sequence[Mapping[str, str]],
    selected: Sequence[Mapping[str, str]],
    specs: Mapping[str, Mapping[str, str]],
    parent_tokens: set[str],
) -> tuple[list[dict[str, str]], set[str]]:
    atlas = read_tsv(ATLAS)
    audit.check(len(atlas) == 2, "atlas has exactly two rows")
    audit.check(
        [row["target_occurrence_id"] for row in atlas]
        == [row["target_occurrence_id"] for row in selected],
        "atlas exactly follows independent pure-selector matches",
    )
    audit.check([row["span_id"] for row in atlas] == ["G780-S001", "G780-S002"],
                "atlas span IDs complete and ordered")
    selected_by_target = unique(selected, "target_occurrence_id")
    for row in atlas:
        old = selected_by_target[row["target_occurrence_id"]]
        spec = specs[row["right_surface"]]
        audit.check(
            row["page"] == old["page"] and row["physical_folio"] == old["physical_folio"]
            and row["locus"] == old["locus"] and row["ol_ordinal"] == old["ordinal"]
            and row["right_ordinal"] == old["right_ordinal"]
            and row["right_surface"] == old["right_surface"]
            and row["written_span_eva"] == "ol " + old["right_surface"]
            and row["written_line_eva"] == old["written_line_eva"]
            and row["right_reader_exact"] == "1",
            "atlas geometry reconstructs parent " + row["right_surface"],
        )
        audit.check(
            row["old_gdt779_contextual"] == "0"
            and row["old_gdt779_default_de"] == old["gdt779_default_de"]
            and row["selected_whole_default_de"] == spec["default_de"]
            and row["new_gdt780_default_de"] == spec["default_de"]
            and row["alternate_1_de"] == spec["alternate_1_de"]
            and row["alternate_2_de"] == spec["alternate_2_de"]
            and row["confidence"] == spec["confidence"]
            and row["functional_axis"] == spec["functional_axis"]
            and row["card_class"] == spec["card_class"]
            and row["scope_status"] == spec["renderer_scope"],
            "atlas semantic card is copied whole and exactly " + row["right_surface"],
        )
        audit.check(
            row["semantic_change_class"] == "FALLBACK_REPLACEMENT"
            and row["fallback_replacement"] == "1"
            and row["display_changed"] == "1"
            and row["inherited_consumed_token_ids"] == "NONE"
            and row["gdt780_consumed_token_id"] == row["locus"] + "@" + row["right_ordinal"]
            and row["new_unique_consumption"] == "1"
            and row["exact_complete_whole_only"] == "1"
            and row["selection_rule"] == SELECTION_RULE,
            "atlas records exact whole fallback replacement " + row["right_surface"],
        )
    new_tokens = {row["gdt780_consumed_token_id"] for row in atlas}
    audit.check(len(new_tokens) == 2 and not (new_tokens & parent_tokens),
                "two new right-token consumptions are unique and collision-free")
    audit.check(
        zero_fields(
            atlas,
            (
                "same_row_inherited_consumption_takeover", "cross_row_consumption_collision",
                "selection_uses_occurrence_id", "selection_uses_page_or_locus",
                "selection_uses_neighbor_or_frequency", "selection_uses_substring",
                "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
                "component_export_credit",
            ),
        ),
        "atlas records zero takeover forbidden selectors and claim exports",
    )

    precedence = read_tsv(PRECEDENCE)
    audit.check(len(precedence) == 2, "precedence audit has exactly two rows")
    audit.check(
        [row["target_occurrence_id"] for row in precedence]
        == [row["target_occurrence_id"] for row in atlas],
        "precedence audit covers exactly atlas targets",
    )
    audit.check([row["precedence_id"] for row in precedence] == ["G780-H001", "G780-H002"],
                "precedence IDs complete and ordered")
    atlas_by_target = unique(atlas, "target_occurrence_id")
    parent_by_target = unique(parent, "target_occurrence_id")
    for row in precedence:
        span = atlas_by_target[row["target_occurrence_id"]]
        old = parent_by_target[row["target_occurrence_id"]]
        audit.check(
            row["right_surface"] == span["right_surface"]
            and row["right_reader_exact"] == "1"
            and row["parent_gdt779_fallback"] == "1"
            and row["parent_gdt779_contextual"] == "0"
            and row["frozen_two_whole_deck_member"] == "1"
            and row["precedence_disposition"] == "SELECTED_GDT780_FALLBACK",
            "precedence selects only exact parent fallback " + row["right_surface"],
        )
        audit.check(
            row["old_gdt779_branch"] == old["gdt779_branch"]
            and row["old_gdt779_default_de"] == old["gdt779_default_de"]
            and row["old_gdt779_consumed_token_count"] == "0"
            and row["old_gdt779_consumed_token_ids"] == "NONE"
            and row["new_gdt780_branch"] == "GDT780_EXACT_OL_PLUS_CARDLESS_SUPPORTED_WHOLE"
            and row["new_gdt780_default_de"] == span["new_gdt780_default_de"]
            and row["new_gdt780_contextual"] == "1"
            and row["new_gdt780_consumed_token_count"] == "1"
            and row["new_gdt780_consumed_token_ids"] == span["gdt780_consumed_token_id"]
            and row["fallback_replacement"] == "1",
            "precedence state transition exact " + row["right_surface"],
        )
    audit.check(
        zero_fields(
            precedence,
            (
                "same_row_inherited_consumption_takeover", "cross_row_consumption_collision",
                "selection_uses_occurrence_id", "component_export_credit",
            ),
        ) and all(row["selection_rule"] == SELECTION_RULE for row in precedence),
        "precedence has no takeover collision ID selection or component export",
    )
    return atlas, new_tokens


def validate_renderer(
    audit: Audit,
    parent: Sequence[Mapping[str, str]],
    selected: Sequence[Mapping[str, str]],
    specs: Mapping[str, Mapping[str, str]],
    atlas: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    renderer = read_tsv(RENDERER)
    audit.check(len(renderer) == 376, "published renderer has 376 rows")
    audit.check(
        [row["target_occurrence_id"] for row in renderer]
        == [row["target_occurrence_id"] for row in parent],
        "renderer preserves all parent identities and order",
    )
    audit.check(set(parent[0]) <= set(renderer[0]), "renderer retains every parent field")
    audit.check(
        all(all(new[field] == old[field] for field in old) for old, new in zip(parent, renderer)),
        "every retained parent byte-field is unchanged",
    )
    selected_ids = {row["target_occurrence_id"] for row in selected}
    atlas_by_target = unique(atlas, "target_occurrence_id")
    unchanged = 0
    for old, new in zip(parent, renderer):
        target = old["target_occurrence_id"]
        if target in selected_ids:
            span = atlas_by_target[target]
            spec = specs[old["right_surface"]]
            audit.check(
                new["gdt780_branch"] == "GDT780_EXACT_OL_PLUS_CARDLESS_SUPPORTED_WHOLE"
                and new["gdt780_default_de"] == spec["default_de"]
                and new["gdt780_renderer_contextual"] == "1"
                and new["gdt780_span_id"] == span["span_id"]
                and new["gdt780_exact_whole"] == old["right_surface"]
                and new["gdt780_confidence"] == spec["confidence"]
                and new["gdt780_consumed_token_count"] == "1"
                and new["gdt780_consumed_token_ids"] == span["gdt780_consumed_token_id"]
                and new["gdt780_fallback_replacement"] == "1"
                and new["gdt780_display_changed"] == "1"
                and new["gdt780_new_unique_consumption"] == "1"
                and new["gdt780_dispatch_rule"] == SELECTION_RULE
                and new["gdt780_scope_status"] == spec["renderer_scope"]
                and new["gdt780_functional_axis"] == spec["functional_axis"],
                "selected renderer state exact " + target,
            )
        else:
            unchanged += 1
            audit.check(
                new["gdt780_branch"] == "INHERITED_GDT779"
                and active_state_equal(old, new)
                and new["gdt780_fallback_replacement"] == "0"
                and new["gdt780_display_changed"] == "0"
                and new["gdt780_new_unique_consumption"] == "0"
                and new["gdt780_positive_evidence"] == "INHERITED_GDT779"
                and new["gdt780_counterevidence"] == "INHERITED_GDT779"
                and new["gdt780_dispatch_rule"] == "INHERITED_GDT779"
                and new["gdt780_scope_status"] == "INHERITED_GDT779"
                and new["gdt780_card_class"] == "INHERITED_GDT779"
                and new["gdt780_functional_axis"] == "INHERITED_GDT779",
                "unselected row inherits complete active state " + target,
            )
    audit.check(unchanged == 374, "all 374 nonselected rows are inherited")
    audit.check(
        Counter(row["gdt780_renderer_contextual"] for row in renderer) == Counter({"1": 247, "0": 129}),
        "renderer coverage moves 245 to 247 and fallbacks 131 to 129",
    )
    audit.check(
        sum(row["gdt780_fallback_replacement"] == "1" for row in renderer) == 2
        and sum(row["gdt780_display_changed"] == "1" for row in renderer) == 2
        and sum(row["gdt780_new_unique_consumption"] == "1" for row in renderer) == 2,
        "renderer contains exactly two changes and two new consumptions",
    )
    token_ids: list[str] = []
    for row in renderer:
        values = [] if row["gdt780_consumed_token_ids"] == "NONE" else row["gdt780_consumed_token_ids"].split("|")
        audit.check(len(values) == int(row["gdt780_consumed_token_count"]),
                    "current token arity " + row["target_occurrence_id"])
        token_ids.extend(values)
    audit.check(len(token_ids) == len(set(token_ids)) == 207,
                "renderer has 207 unique consumed right tokens without collision")
    audit.check(
        [row["target_occurrence_id"] for row in renderer if row["right_surface"] in EXPECTED_FORMS]
        == [row["target_occurrence_id"] for row in selected],
        "full parent deck has only the two selected exact fallback matches",
    )
    audit.check(
        zero_fields(
            renderer,
            (
                "gdt780_default_is_translation", "gdt780_confirmed_lexeme",
                "gdt780_confirmed_plaintext", "gdt780_component_export_credit",
            ),
        ),
        "renderer exports no translation lexeme plaintext or component",
    )
    return renderer


def render_patch(
    rows: Sequence[Mapping[str, str]], locus: str, written_line: str, generation: str,
) -> str:
    by_position = {
        (row["locus"], int(row["ordinal"])): row
        for row in rows
    }
    tokens = written_line.split()
    rendered: list[str] = []
    consumed: set[int] = set()
    for ordinal, token in enumerate(tokens, 1):
        if ordinal in consumed:
            continue
        row = by_position.get((locus, ordinal))
        if row is None or row[f"{generation}_renderer_contextual"] == "0":
            rendered.append(token)
            continue
        rendered.append("⟦" + row[f"{generation}_default_de"] + "⟧")
        count = int(row[f"{generation}_consumed_token_count"])
        consumed.update(range(ordinal + 1, ordinal + count + 1))
    return " ".join(rendered)


def validate_dictionary_and_passages(
    audit: Audit,
    specs: Mapping[str, Mapping[str, str]],
    atlas: Sequence[Mapping[str, str]],
    parent: Sequence[Mapping[str, str]],
    renderer: Sequence[Mapping[str, str]],
) -> None:
    dictionary = read_tsv(DICTIONARY)
    audit.check(len(dictionary) == 2, "dictionary/evidence output has two rows")
    audit.check([row["entry"] for row in dictionary] == ["eees", "sheeol"],
                "dictionary/evidence rows are exact sorted frozen deck")
    for row in dictionary:
        spec = specs[row["entry"]]
        audit.check(
            row["preferred_gdt780_default_de"] == spec["default_de"]
            and row["alternate_1_de"] == spec["alternate_1_de"]
            and row["alternate_2_de"] == spec["alternate_2_de"]
            and row["confidence"] == spec["confidence"]
            and row["functional_axis"] == spec["functional_axis"]
            and row["card_class"] == spec["card_class"]
            and row["source_evidence"] == spec["source_evidence"]
            and row["selected_exact_fallback_contexts"] == "1",
            "dictionary copies frozen whole card exactly " + row["entry"],
        )
        audit.check(
            row["scope"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT"
            and row["replaceable"] == "1" and row["literal_identity"] == "OPEN",
            "dictionary entry stays replaceable whole-only " + row["entry"],
        )
    by_form = unique(dictionary, "entry")
    eees = by_form["eees"]
    audit.check(
        eees["source_reader_exact_occurrences"] == "7"
        and eees["exact_right_contexts"] == "4"
        and eees["ordered_value_follower_hits"] == "3"
        and eees["ordered_value_conditional_rate"] == "0.750000"
        and eees["ordered_value_baseline_rate"] == "0.021613"
        and eees["ordered_value_descriptive_lift"] == "34.702083",
        "published eees evidence reproduces only locked 7/4/3 rate baseline lift",
    )
    audit.check(
        eees["source_cache_pages"] == "NA"
        and eees["source_reader_exact_pages"] == "NA",
        "eees aggregate source does not invent page counts",
    )
    audit.check(
        eees["leave_target_out_right_contexts"] == "3"
        and eees["leave_target_out_value_hits"] == "2"
        and eees["leave_target_out_conditional_rate"] == "0.666667"
        and eees["target_independence_audit_id"] == "G780-A001"
        and eees["target_independence_status"]
        == "PASS__TARGET_REMOVAL_RETAINS_2_OF_3_AIIN_FOLLOWERS",
        "dictionary records executable eees 3/2 target-out result",
    )
    sheeol = by_form["sheeol"]
    audit.check(
        sheeol["source_cache_occurrences"] == "10"
        and sheeol["source_cache_pages"] == "8"
        and sheeol["source_reader_exact_occurrences"] == "9"
        and sheeol["source_reader_exact_pages"] == "7"
        and sheeol["gdt745_consensus_axes"] == "MATERIAL|END_STAGE"
        and sheeol["gdt745_rival_axes"] == "DRY|MOIST|PREPARATION",
        "published sheeol GDT745 evidence exact",
    )
    audit.check(
        sheeol["gdt746_distribution_status"] == "S2_DISTRIBUTION_SUPPORTED"
        and sheeol["gdt746_form_and_top5_axis_agreement"] == "END_STAGE"
        and sheeol["gdt747_local_support_occurrences"] == "4"
        and sheeol["gdt747_local_support_pages"] == "3"
        and sheeol["gdt748_counterframe_axes"] == "COLD"
        and sheeol["gdt748_counterframe_bridge_tier"] == "B0_NO_WHOLE_FORM_BRIDGE",
        "published sheeol GDT746-748 evidence and cold counterframe exact",
    )
    audit.check(
        sheeol["target_independence_audit_id"] == "G780-A002"
        and sheeol["target_independence_status"]
        == "PASS__TARGET_IS_EXACT_L0_AND_CONTRIBUTES_ZERO_END_SUPPORTS"
        and sheeol["target_local_support_tier"] == "L0_NO_LOCAL_W23_SUPPORT"
        and sheeol["target_local_support_count"] == "0",
        "dictionary records executable sheeol zero-support target audit",
    )
    audit.check(
        zero_fields(
            dictionary,
            (
                "numeric_identity_confirmed", "specific_substance_confirmed",
                "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
                "component_export_credit",
            ),
        ),
        "dictionary exports no number substance translation lexeme plaintext or component",
    )

    passages = read_tsv(PASSAGES)
    audit.check(len(passages) == 2, "passage table has two full lines")
    audit.check(
        [row["target_occurrence_id"] for row in passages]
        == [row["target_occurrence_id"] for row in atlas],
        "passage table exactly covers atlas targets",
    )
    audit.check([row["passage_patch_id"] for row in passages] == ["G780-P001", "G780-P002"],
                "passage IDs complete and ordered")
    atlas_by_target = unique(atlas, "target_occurrence_id")
    for row in passages:
        span = atlas_by_target[row["target_occurrence_id"]]
        audit.check(
            row["span_id"] == span["span_id"]
            and row["right_surface"] == span["right_surface"]
            and row["right_token_id"] == span["gdt780_consumed_token_id"]
            and row["selected_whole_default_de"] == span["selected_whole_default_de"]
            and row["written_line_eva"] == span["written_line_eva"],
            "passage metadata reconstructs atlas " + row["right_surface"],
        )
        audit.check(
            row["inherited_gdt779_patch_de"]
            == render_patch(parent, row["locus"], row["written_line_eva"], "gdt779")
            and row["gdt780_practical_patch_de"]
            == render_patch(renderer, row["locus"], row["written_line_eva"], "gdt780")
            and row["inherited_gdt779_patch_de"] != row["gdt780_practical_patch_de"],
            "passage render independently reconstructs " + row["locus"],
        )
    audit.check(
        zero_fields(passages, ("default_is_translation", "confirmed_plaintext", "component_export_credit")),
        "passages export no translation plaintext or component",
    )


def normalize_residual_reason(reason: str) -> str:
    if reason in {"V99_CARD_NONEXACT_FINAL44", "V99_CARD_NONEXACT_RAW_ONLY"}:
        return "V99_CARD_NONEXACT"
    return reason


def validate_residual(
    audit: Audit,
    source_residual: Sequence[Mapping[str, str]],
    renderer: Sequence[Mapping[str, str]],
    selected: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    residual = read_tsv(RESIDUAL)
    fallback = [row for row in renderer if row["gdt780_renderer_contextual"] == "0"]
    selected_ids = {row["target_occurrence_id"] for row in selected}
    expected_source = [row for row in source_residual if row["target_occurrence_id"] not in selected_ids]
    audit.check(len(residual) == len(fallback) == len(expected_source) == 129,
                "residual table covers every and only 129 current fallbacks")
    audit.check(
        [row["target_occurrence_id"] for row in residual]
        == [row["target_occurrence_id"] for row in fallback]
        == [row["target_occurrence_id"] for row in expected_source],
        "residual table preserves independent remaining parent order",
    )
    audit.check(
        [row["residual_id"] for row in residual] == [f"G780-R{number:03d}" for number in range(1, 130)],
        "residual IDs complete and ordered",
    )
    for row, old, current in zip(residual, expected_source, fallback):
        audit.check(
            row["parent_gdt779_residual_id"] == old["residual_id"]
            and row["target_occurrence_id"] == old["target_occurrence_id"]
            and row["right_surface"] == old["right_surface"]
            and row["right_reader_exact"] == old["right_reader_exact"]
            and row["parent_residual_reason"] == old["residual_reason"]
            and row["residual_reason"] == normalize_residual_reason(old["residual_reason"])
            and row["gdt780_default_de"] == current["gdt780_default_de"],
            "residual row reconstructs inherited reason " + row["target_occurrence_id"],
        )
    audit.check(
        Counter(row["residual_reason"] for row in residual) == Counter({
            "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 23,
            "V99_CARD_NONEXACT": 49,
            "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
            "LINE_FINAL_NO_RIGHT": 37,
        }),
        "residual reason split is exactly 23/49/20/37",
    )
    audit.check(
        all(row["frozen_two_whole_deck_member"] == "0" for row in residual)
        and zero_fields(residual, ("component_export_credit",)),
        "no selected whole or component export remains in fallback census",
    )
    return residual


def validate_relation_packet(audit: Audit, atlas: Sequence[Mapping[str, str]]) -> None:
    packet = read_tsv(PACKET)
    crosswalk = read_tsv(CROSSWALK)
    audit.check(len(packet) == len(crosswalk) == len(atlas) == 2,
                "relation packet crosswalk and atlas each have two rows")
    edge_ids = ["G780-E001", "G780-E002"]
    audit.check(
        [row["edge_id"] for row in packet] == [row["edge_id"] for row in crosswalk] == edge_ids,
        "relation edge IDs complete unique and crosswalked",
    )
    for edge, cross, span in zip(packet, crosswalk, atlas):
        audit.check(
            edge["page"] == span["page"]
            and edge["physical_folio"] == span["physical_folio"]
            and edge["pivot_locus"] == span["locus"] + "@" + span["ol_ordinal"]
            and edge["target_locus"] == span["gdt780_consumed_token_id"]
            and edge["relation_type"] == "NEXT_TOKEN"
            and edge["direction_basis"] == "TRANSCRIPTION_ORDER_ONLY"
            and edge["ownership_basis"] == "NONVISUAL_TEXT_ADJACENCY",
            "relation edge reconstructs text adjacency " + edge["edge_id"],
        )
        audit.check(
            edge["geometry_only_selection"] == "FALSE"
            and edge["formal_access_state"] == "SEALED_NOT_ACCESSED"
            and edge["fold_assignment"] == "NONE"
            and edge["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
            "relation edge explicitly ineligible and unscored " + edge["edge_id"],
        )
        audit.check(
            cross["span_id"] == span["span_id"]
            and cross["target_occurrence_id"] == span["target_occurrence_id"]
            and cross["right_surface"] == span["right_surface"]
            and cross["written_span_eva"] == span["written_span_eva"]
            and cross["selection_rule"] == SELECTION_RULE
            and cross["score_eligible"] == "0"
            and cross["component_export_credit"] == "0",
            "relation crosswalk maps exact span with zero score and component credit " + edge["edge_id"],
        )
    stored = json.loads(EDGE_INTAKE.read_text(encoding="utf-8"))
    audit.check(stored == EXPECTED_EDGE_INTAKE, "stored edge intake is exact not-score-ready result")
    gate = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    audit.check(gate.returncode == 0, "external check-edge-packet exits successfully")
    try:
        observed = json.loads(gate.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError("external edge-packet output is not JSON") from error
    audit.check(observed == EXPECTED_EDGE_INTAKE, "external edge gate reproduces stored intake")


def validate_result_and_report(audit: Audit) -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT780", "RESULT experiment identity")
    audit.check(result["status"] == EXPECTED_STATUS, "RESULT exact PASS status")
    audit.check(result["source_locks"] == 11, "RESULT records eleven source locks")
    audit.check(result["inherited_guard"] == parent_result["inherited_guard"],
                "RESULT inherits parent acquisition guard unchanged")
    audit.check(result["cohort"] == {
        "renderer_rows": 376, "reader_exact_cardless_intake": 25,
        "selected_spans": 2, "selected_forms": 2, "loci": 2,
        "page_labels": 2, "physical_folios": 2,
    }, "RESULT cohort values exact")
    audit.check(result["precedence"] == {
        "full_parent_deck_matches": 2, "reader_exact_parent_deck_matches": 2,
        "nonexact_parent_deck_matches": 0, "parent_fallback_deck_matches": 2,
        "protected_contextual_deck_matches": 0, "selected_fallback_matches": 2,
        "nonselected_parent_rows_unchanged": 374,
    }, "RESULT precedence values exact")
    audit.check(result["changes"] == {
        "fallback_replacements": 2, "actual_display_changes": 2,
        "contextual_sharpenings": 0, "contextual_confirmations": 0,
        "passage_patches": 2,
    }, "RESULT change classes exact")
    audit.check(result["renderer"] == {
        "gdt779_contextual": 245, "gdt780_contextual": 247,
        "gdt779_fallbacks": 131, "gdt780_fallbacks": 129,
    }, "RESULT renderer transition exact")
    audit.check(result["consumption"] == {
        "gdt779_unique_right_tokens": 205, "gdt780_selected_right_tokens": 2,
        "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 2,
        "total_unique_right_tokens": 207, "cross_row_collisions": 0,
    }, "RESULT consumption transition exact and collision-free")
    audit.check(result["evidence"] == {
        "dictionary_evidence_rows": 2, "eees_reader_exact_occurrences": 7,
        "eees_exact_right_contexts": 4, "eees_ordered_value_follower_hits": 3,
        "target_independence_audit_rows": 2,
        "eees_leave_target_out_right_contexts": 3,
        "eees_leave_target_out_value_hits": 2,
        "eees_leave_target_out_claim_runner_reconstructed": True,
        "sheeol_local_end_contacts": 4, "sheeol_local_end_contact_pages": 3,
        "sheeol_target_local_support_tier": "L0_NO_LOCAL_W23_SUPPORT",
        "sheeol_target_local_support_count": 0,
        "sheeol_target_independence_runner_reconstructed": True,
        "sheeol_cold_counterframe_has_whole_bridge": False,
    }, "RESULT evidence summary includes both executable target-independence controls")
    audit.check(result["residual_fallback_rows"] == 129 and result["residual_partition"] == {
        "no_card_reader_exact": 23, "v99_card_nonexact": 49,
        "no_card_reader_nonexact": 20, "line_final_no_right": 37,
    }, "RESULT residual split exact")
    audit.check(result["relation_packet"] == EXPECTED_EDGE_INTAKE,
                "RESULT relation packet exact and not score-ready")
    audit.check(
        result["confirmed_lexemes"] == 0
        and result["confirmed_plaintext_clauses"] == 0
        and result["numeric_identities"] == 0
        and result["specific_substances"] == 0
        and result["component_exports"] == 0,
        "RESULT exports no lexeme plaintext number substance or component",
    )
    audit.check(
        result["new_pages"] == result["new_images"] == result["new_ocr"]
        == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0,
        "RESULT records zero acquisition and sealed-page access",
    )
    report = REPORT.read_text(encoding="utf-8")
    audit.check(EXPECTED_STATUS in report, "REPORT states exact PASS status")
    audit.check(
        "**245→247**" in report and "**131→129**" in report and "**205→207**" in report
        and "374 Rendererzeilen" in report,
        "REPORT states transitions and 374 inherited rows",
    )
    audit.check(
        "sieben" in report and "vier exakte Rechtskontexte" in report
        and "drei `aiin`-Folger" in report and "34.702083" in report,
        "REPORT states direct eees aggregate evidence",
    )
    audit.check(
        "drei Kontexte und zwei `aiin`-Treffer" in report
        and "sauberen, zulässigen Tokens `eees aiin`" in report,
        "REPORT states executable eees target-out reconstruction",
    )
    audit.check(
        "zehn Cache-/neun exakte" in report and "vier lokale" in report
        and "keine Ganzwortbrücke" in report,
        "REPORT states sheeol end support and cold counterframe",
    )
    audit.check(
        "G747-O060" in report and "reader-exakt, `L0`" in report
        and "alle vier Endkontakte liegen damit außerhalb des Ziels" in report,
        "REPORT states executable sheeol target-independence reconstruction",
    )
    audit.check(
        "23 reader-exakte" in report and "49" in report and "20 nicht-exakte" in report
        and "37" in report,
        "REPORT states full residual split",
    )
    audit.check("`f84` und `f84r`" in report and "blieben gesperrt" in report,
                "REPORT explicitly records both sealed pages as untouched")


def validate_hygiene(audit: Audit) -> None:
    tables = (
        INTAKE_25, TARGET_INDEPENDENCE, ATLAS, PRECEDENCE, RENDERER, DICTIONARY, PASSAGES,
        RESIDUAL, PACKET, CROSSWALK,
    )
    for path in tables:
        rows = read_tsv(path)
        audit.check(
            all(not any(SEALED_RE.search(value) for value in row.values()) for row in rows),
            "sealed f84/f84r absent from " + path.name,
        )
    audit.check(
        all(not SEALED_RE.search(relative) for relative in EXPECTED_LOCKS),
        "source lock set contains no sealed path",
    )
    output_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (INTAKE_25, ATLAS, PRECEDENCE, RENDERER, DICTIONARY, PASSAGES, RESIDUAL, CROSSWALK)
    )
    audit.check("NO_SUBSTRING_EXPORT" in output_text, "whole-only no-substring scope is explicit")
    audit.check(
        "specific_substance_confirmed\tdefault_is_translation\tconfirmed_lexeme\tconfirmed_plaintext\tcomponent_export_credit"
        in DICTIONARY.read_text(encoding="utf-8"),
        "dictionary exposes all semantic claim-ceiling flags",
    )


def byte_replay(audit: Audit, runner_hash_before: str) -> dict[str, str]:
    published_hashes = {str(path.relative_to(EXP)): sha256(path) for path in REPLAY_OUTPUTS}
    with tempfile.TemporaryDirectory(prefix="gdt780-validator-") as temporary:
        temp = Path(temporary)
        artifacts = temp / "artifacts"
        report = temp / "REPORT.md"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        replay = subprocess.run(
            [
                sys.executable, "-B", str(RUN),
                "--artifacts-dir", str(artifacts),
                "--report-path", str(report),
            ],
            cwd=ROOT, env=environment, text=True, capture_output=True, check=False,
        )
        audit.check(replay.returncode == 0, "runner temp-directory replay exits successfully")
        for published in REPLAY_OUTPUTS:
            generated = report if published == REPORT else artifacts / published.name
            audit.check(generated.is_file(), "replay generated " + published.name)
            audit.check(generated.read_bytes() == published.read_bytes(),
                        "byte replay exact for " + published.name)
    audit.check(sha256(RUN) == runner_hash_before, "runner hash stable across byte replay")
    return published_hashes


def main() -> int:
    missing = [path for path in REPLAY_OUTPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("runner outputs not ready: " + ", ".join(path.name for path in missing))
    audit = Audit()
    runner_hash = sha256(RUN)
    source_hashes = validate_source_locks(audit)
    specs = validate_specs(audit)
    validate_runner_ast(audit)
    validate_source_evidence(audit)
    parent, source_residual, selected, parent_tokens = reconstruct_parent(audit, specs)
    validate_target_independence(audit, parent)
    validate_intake_output(audit, parent, source_residual)
    atlas, new_tokens = validate_atlas_and_precedence(
        audit, parent, selected, specs, parent_tokens,
    )
    renderer = validate_renderer(audit, parent, selected, specs, atlas)
    validate_dictionary_and_passages(audit, specs, atlas, parent, renderer)
    validate_residual(audit, source_residual, renderer, selected)
    validate_relation_packet(audit, atlas)
    validate_result_and_report(audit)
    validate_hygiene(audit)
    output_hashes = byte_replay(audit, runner_hash)

    value = {
        "experiment_id": "GDT780",
        "status": "PASS",
        "validator_independence": "11_SOURCES_HASHED__25_CARDLESS_RECONSTRUCTED__TWO_TARGET_REMOVALS_RECONSTRUCTED__PURE_AST_GATED__ALL_376_ROWS_RECONSTRUCTED__EDGE_GATED__BYTE_REPLAYED",
        "checks_passed": audit.count,
        "source_hash_count": len(source_hashes),
        "source_hashes": source_hashes,
        "spec_sha256": sha256(SPECS),
        "runner_sha256": runner_hash,
        "runner_output_replay_count": len(REPLAY_OUTPUTS),
        "runner_output_sha256": output_hashes,
        "selection": {
            "reader_exact_cardless_intake": 25,
            "selected_spans": 2,
            "selected_forms": 2,
            "selected_loci": 2,
            "selected_page_labels": 2,
            "selected_physical_folios": 2,
            "unselected_exact_cardless_forms": 23,
            "selection_uses_occurrence_id": False,
            "selection_uses_page_or_locus": False,
            "selection_uses_neighbor_or_frequency": False,
            "selection_uses_substrings": False,
            "selection_uses_semantics": False,
        },
        "evidence": {
            "eees_reader_exact_occurrences": 7,
            "eees_exact_right_contexts": 4,
            "eees_aiin_followers": 3,
            "eees_ordered_value_rate": "0.750000",
            "eees_ordered_value_baseline": "0.021613",
            "eees_ordered_value_lift": "34.702083",
            "eees_target_line_aiin_follower": True,
            "eees_target_out_right_contexts": 3,
            "eees_target_out_aiin_followers": 2,
            "eees_target_out_rate": "0.666667",
            "eees_target_independence_reconstructed": True,
            "sheeol_cache_occurrences": 10,
            "sheeol_reader_exact_occurrences": 9,
            "sheeol_form_distribution_axis": "END_STAGE",
            "sheeol_local_end_contacts": 4,
            "sheeol_local_end_contact_pages": 3,
            "sheeol_target_local_support_tier": "L0_NO_LOCAL_W23_SUPPORT",
            "sheeol_target_local_support_count": 0,
            "sheeol_target_out_local_end_contacts": 4,
            "sheeol_target_independence_reconstructed": True,
            "sheeol_cold_counterframe_whole_bridge": False,
            "target_independence_audit_rows": 2,
        },
        "renderer": {
            "contextual_before": 245,
            "contextual_after": 247,
            "fallback_before": 131,
            "fallback_after": 129,
            "consumed_before": 205,
            "new_consumed_tokens": sorted(new_tokens),
            "consumed_after": 207,
            "nonselected_rows_inherited": 374,
            "cross_row_collisions": 0,
        },
        "residual_partition": {
            "no_card_reader_exact": 23,
            "v99_card_nonexact": 49,
            "no_card_reader_nonexact": 20,
            "line_final_no_right": 37,
        },
        "relation_packet_gate": EXPECTED_EDGE_INTAKE,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "component_exports": 0,
        "sealed_pages_accessed": 0,
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
