#!/usr/bin/env python3
"""Independent cohort, meaning, renderer, provenance, packet, and replay audit for GDT778."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN, REPORT = SRC / "run.py", EXP / "REPORT.md"
G777_RENDERER = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer/artifacts/GDT777_376_RENDERER.tsv"
G777_RESULT = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer/artifacts/RESULT.json"
G734_WORDS = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G734_RESIDUAL = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_TOP100_RESIDUAL_SPLIT_INVENTORY.tsv"
G736_BODIES = ROOT / "experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/BODY_ROLE_DICTIONARY_V2.tsv"
G737_BODIES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G738_BRIDGE = ROOT / "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/BODY_120_SEMANTIC_BRIDGE.tsv"
G758_CENSUS = ROOT / "experiments/yolo/gdt758_ychor_follower_global_content_census/artifacts/FOLLOWER_11_GLOBAL_CENSUS.tsv"
G759_DICTIONARY = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/GDT759_EXACT_CONSTRUCTION_DICTIONARY.tsv"
G768_DICTIONARY = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G769_DICTIONARY = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/GDT769_5_WORKING_DICTIONARY.tsv"
G772_DICTIONARY = ROOT / "experiments/yolo/gdt772_expanded_ol_branch_masked_rescore/artifacts/GDT772_4_WORKING_DICTIONARY.tsv"

EXPECTED_FORMS = frozenset({
    "ain", "air", "ar", "chaiin", "char", "chedar", "cheos", "chol", "chor", "choy", "chs",
    "chy", "dair", "dal", "dar", "dol", "kain", "kar", "keey", "oaiin", "oldaiin", "olkaiin",
    "olkain", "olkeey", "ols", "ory", "otaiin", "sheckhy", "shol",
})
LATER_WHOLES = frozenset({"ar", "chor", "chol", "dair"})
SOURCE_CONFLICT_WHOLES = frozenset({"ols"})
G736_PROMOTIONS = frozenset({"air", "oaiin", "chy"})
G737_PROMOTIONS = EXPECTED_FORMS - LATER_WHOLES - SOURCE_CONFLICT_WHOLES - G736_PROMOTIONS
EXPECTED_EXCLUSIONS = {
    "G769-T0284": ("keey", "f76r.12", 6, 7),
    "G769-T0391": ("dal", "f80v.15", 11, 12),
}
EXPECTED_OUTPUTS = (
    "EXACT_WHOLE_29_REGISTRY.tsv", "GDT778_39_EXACT_WHOLE_ATLAS.tsv",
    "GDT778_EXACTNESS_EXCLUSIONS.tsv", "GDT778_PROVENANCE_SOURCE_CONFLICT_AUDIT.tsv",
    "GDT778_376_RENDERER.tsv", "GDT778_WORKING_DICTIONARY.tsv",
    "GDT778_PASSAGE_PATCHES.tsv", "GDT778_GDT388_RELATION_PACKET.tsv",
    "GDT778_RELATION_EDGE_CROSSWALK.tsv", "RELATION_PACKET_INTAKE.json", "RESULT.json",
)
BANNED_DEFAULT = re.compile(r"(?i)(pulver|samen|wurzel|holz|drogen|filtrat|abgeseih)")
SEALED_LABEL = re.compile(r"(?i)^f84r?$")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one_by(rows: Iterable[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for source in rows:
        value = source[key]
        if value in output:
            raise ValueError(f"duplicate {key}: {value}")
        output[value] = dict(source)
    return output


def split_ids(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def as_text(value: object) -> str:
    return str(int(value)) if isinstance(value, bool) else str(value)


def structural_frame(old_default: str) -> str:
    if old_default == "und":
        return "UND_LINK"
    if old_default.startswith("Ansatz:"):
        return "ANSATZ_FRAME"
    if old_default.startswith("Zustand:"):
        return "STATE_FRAME"
    return "NONE"


def compose(surface: str, default: str, old_default: str, old_contextual: int) -> tuple[str, str, int, int, int]:
    if old_contextual == 0:
        return default, "FALLBACK_REPLACEMENT", 1, 0, 0
    frame = structural_frame(old_default)
    if surface == "chol" and old_default == "Zustand: trocken" and frame == "STATE_FRAME":
        return old_default, "CONTEXTUAL_CONFIRMATION", 0, 0, 1
    if frame == "UND_LINK":
        return f"und; {default}", "CONTEXTUAL_SHARPENING", 0, 1, 0
    if frame == "ANSATZ_FRAME":
        return f"Ansatz: {default}", "CONTEXTUAL_SHARPENING", 0, 1, 0
    raise ValueError(f"unlicensed inherited composition: {surface!r}, {old_default!r}")


def render_line(locus: str, written_line: str, by_position: Mapping[tuple[str, int], Mapping[str, str]], prefix: str) -> str:
    tokens = written_line.split()
    output: list[str] = []
    consumed: set[int] = set()
    for ordinal, token in enumerate(tokens, 1):
        if ordinal in consumed:
            continue
        row = by_position.get((locus, ordinal))
        if row is None:
            output.append(token)
        elif int(row[f"{prefix}_renderer_contextual"]):
            output.append(f"⟦{row[f'{prefix}_default_de']}⟧")
            count = int(row[f"{prefix}_consumed_token_count"])
            consumed.update(range(ordinal + 1, ordinal + count + 1))
        else:
            output.append(token)
    return " ".join(output)


def main() -> int:
    checks = 0
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(label)

    def equal(actual: object, expected: object, label: str) -> None:
        check(actual == expected, f"{label}: expected {expected!r}, got {actual!r}")

    # Independently hash all locked inputs and forbid sealed source paths.
    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    expected_locked_paths = {
        G777_RENDERER.relative_to(ROOT).as_posix(), G777_RESULT.relative_to(ROOT).as_posix(),
        G734_WORDS.relative_to(ROOT).as_posix(), G734_RESIDUAL.relative_to(ROOT).as_posix(),
        G736_BODIES.relative_to(ROOT).as_posix(), G737_BODIES.relative_to(ROOT).as_posix(),
        G738_BRIDGE.relative_to(ROOT).as_posix(), G758_CENSUS.relative_to(ROOT).as_posix(),
        G759_DICTIONARY.relative_to(ROOT).as_posix(), G768_DICTIONARY.relative_to(ROOT).as_posix(),
        G769_DICTIONARY.relative_to(ROOT).as_posix(), G772_DICTIONARY.relative_to(ROOT).as_posix(),
        "tools/relation_edge_intake.py",
    }
    equal(len(locks), 13, "source-lock count")
    equal({row["path"] for row in locks}, expected_locked_paths, "source-lock path set")
    for row in locks:
        relative = Path(row["path"])
        check(not relative.is_absolute() and ".." not in relative.parts, f"safe source path {relative}")
        check(not any(SEALED_LABEL.fullmatch(part) for part in relative.parts), f"sealed source absent {relative}")
        locked = ROOT / relative
        check(locked.is_file(), f"source exists {relative}")
        if locked.is_file():
            equal(sha256(locked), row["expected_sha256"], f"source hash {relative}")

    specs_list = read_tsv(SRC / "EXACT_WHOLE_SPECS.tsv")
    specs = one_by(specs_list, "right_surface")
    equal(len(specs_list), 29, "29 authored rows")
    equal(frozenset(specs), EXPECTED_FORMS, "fixed 29-form fingerprint")
    equal(Counter(row["promotion_status"] for row in specs_list), Counter({
        "EXACT_OL_PLUS_WHOLE_ONLY_NEW_PROMOTION": 24,
        "EXACT_OL_PLUS_WHOLE_ONLY": 4,
        "EXACT_OL_PLUS_WHOLE_ONLY__SOURCE_CONFLICT": 1,
    }), "promotion-status partition")
    equal({form for form, row in specs.items() if row["provenance_path"].startswith("GDT736_")},
          set(G736_PROMOTIONS), "three GDT736 sources")
    equal({form for form, row in specs.items() if row["provenance_path"].startswith("GDT737_")},
          set(G737_PROMOTIONS), "21 GDT737 sources")
    for form, row in specs.items():
        check(bool(re.fullmatch(r"[a-z]+", form)), f"complete surface syntax {form}")
        check(row["confidence"] in {"C0", "C1", "C2"}, f"confidence {form}")
        defaults = (row["selected_default_de"], row["alternate_1_de"], row["alternate_2_de"])
        check(all(default and default != "NONE" for default in defaults), f"three nonempty defaults {form}")
        equal(len(set(defaults)), 3, f"three distinct defaults {form}")
        check(BANNED_DEFAULT.search(" ".join(defaults)) is None, f"retired patient absent from deck {form}")
        check(bool(row["positive_evidence"]), f"positive evidence {form}")
        check(bool(row["counterevidence"]), f"counterevidence {form}")
    equal(specs["ols"]["selected_default_de"], "Produktposten", "ols throughput default")
    equal(specs["ols"]["confidence"], "C0", "ols low confidence")

    parent = read_tsv(G777_RENDERER)
    parent_result = json.loads(G777_RESULT.read_text(encoding="utf-8"))
    equal(len(parent), 376, "parent renderer length")
    equal(len({row["target_occurrence_id"] for row in parent}), 376, "parent IDs unique")
    equal(sum(int(row["gdt777_renderer_contextual"]) for row in parent), 163, "parent contextual")
    equal(sum(1 - int(row["gdt777_renderer_contextual"]) for row in parent), 213, "parent fallback")
    equal(parent_result["renderer"]["total_consumed_right_tokens"], 120, "parent result consumption")

    # Reconstruct the form-wide join without importing any GDT778 function.
    raw: list[dict[str, str]] = []
    selected: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    raw_counts: Counter[str] = Counter()
    exact_counts: Counter[str] = Counter()
    parent_owners: dict[str, str] = {}
    for source in parent:
        tokens = source["written_line_eva"].split()
        ol_ordinal, right_ordinal = int(source["ordinal"]), int(source["right_ordinal"])
        check(1 <= ol_ordinal <= len(tokens), f"parent ol ordinal {source['target_occurrence_id']}")
        if source["right_surface"] == "NONE":
            equal(right_ordinal, 0, f"line-final right sentinel {source['target_occurrence_id']}")
        else:
            check(1 <= right_ordinal <= len(tokens), f"parent right ordinal {source['target_occurrence_id']}")
        if 1 <= ol_ordinal <= len(tokens) and source["right_surface"] != "NONE":
            equal(tokens[ol_ordinal - 1], "ol", f"parent pivot {source['target_occurrence_id']}")
            equal(tokens[right_ordinal - 1], source["right_surface"], f"parent right whole {source['target_occurrence_id']}")
            equal(right_ordinal, ol_ordinal + 1, f"parent adjacency {source['target_occurrence_id']}")
        for token_id in split_ids(source["gdt777_consumed_token_ids"]):
            check(token_id not in parent_owners, f"parent cross-row collision {token_id}")
            parent_owners[token_id] = source["target_occurrence_id"]
        surface = source["right_surface"]
        if surface not in specs:
            continue
        raw.append(source)
        raw_counts[surface] += 1
        if source["right_reader_exact"] != "1":
            excluded.append({"source": source, "surface": surface})
            continue
        exact_counts[surface] += 1
        default = specs[surface]["selected_default_de"]
        old_contextual = int(source["gdt777_renderer_contextual"])
        try:
            display, change_class, fallback, sharpening, confirmation = compose(
                surface, default, source["gdt777_default_de"], old_contextual
            )
        except ValueError as error:
            failures.append(str(error))
            display, change_class, fallback, sharpening, confirmation = "INVALID", "INVALID", 0, 0, 0
        token_id = f"{source['locus']}@{right_ordinal}"
        takeover = int(parent_owners.get(token_id) == source["target_occurrence_id"])
        selected.append({
            "source": source, "surface": surface, "display": display, "change_class": change_class,
            "fallback": fallback, "sharpening": sharpening, "confirmation": confirmation,
            "changed": int(display != source["gdt777_default_de"]), "token_id": token_id,
            "takeover": takeover, "new_unique": 1 - takeover,
        })

    equal(len(parent_owners), 120, "independent parent owner count")
    equal(len(raw), 41, "raw 29-deck join")
    equal(len(selected), 39, "reader-exact 29-deck join")
    equal(len(excluded), 2, "nonexact exclusions")
    equal(len(raw_counts), 29, "all 29 forms have raw matches")
    equal(len(exact_counts), 29, "all 29 forms have exact matches")
    equal({row["source"]["target_occurrence_id"]: (
        row["surface"], row["source"]["locus"], int(row["source"]["ordinal"]),
        int(row["source"]["right_ordinal"]),
    ) for row in excluded}, EXPECTED_EXCLUSIONS, "exclusion fingerprint")
    equal(len({row["source"]["page"] for row in selected}), 31, "selected page labels")
    equal(len({row["source"]["physical_folio"] for row in selected}), 25, "selected physical folios")
    equal(len({row["source"]["locus"] for row in selected}), 39, "selected loci")
    equal(sum(int(row["fallback"]) for row in selected), 32, "fallback replacements")
    equal(Counter(row["surface"] for row in selected if int(row["sharpening"])),
          Counter({"ar": 1, "kain": 2, "chy": 2}), "five real sharpening surfaces")
    equal(Counter(row["surface"] for row in selected if int(row["confirmation"])),
          Counter({"chol": 2}), "two chol confirmations")
    equal(sum(int(row["changed"]) for row in selected), 37, "actual display changes")
    equal(Counter(row["surface"] for row in selected if int(row["takeover"])),
          Counter({"chol": 2, "chy": 2}), "four same-row takeovers")
    equal(sum(int(row["new_unique"]) for row in selected), 35, "35 net new consumption IDs")

    # IDs may be copied into audit records, but no ID/locus/page may dispatch selection.
    source_text = RUN.read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    cohort_functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_cohort"]
    equal(len(cohort_functions), 1, "one AST cohort function")
    predicate_text: list[str] = []
    if cohort_functions:
        for node in ast.walk(cohort_functions[0]):
            if isinstance(node, (ast.If, ast.IfExp, ast.While)):
                predicate_text.append(ast.get_source_segment(source_text, node.test) or ast.dump(node.test))
            elif isinstance(node, ast.comprehension):
                predicate_text.extend(ast.get_source_segment(source_text, item) or ast.dump(item) for item in node.ifs)
    forbidden_predicate_terms = ("target_occurrence_id", "span_id", "exclusion_id", "G769-T",
                                 "source[\"locus\"]", "source['locus']", "source[\"page\"]", "source['page']")
    check(not any(term in text for text in predicate_text for term in forbidden_predicate_terms),
          "occurrence-free AST selection predicates")
    check(any("surface not in specs" in text for text in predicate_text), "AST fixed-deck membership predicate")
    check(any("right_reader_exact" in text for text in predicate_text), "AST exactness predicate")

    atlas = read_tsv(ART / "GDT778_39_EXACT_WHOLE_ATLAS.tsv")
    exclusions_art = read_tsv(ART / "GDT778_EXACTNESS_EXCLUSIONS.tsv")
    equal(len(atlas), 39, "atlas row count")
    equal(len(exclusions_art), 2, "exclusion artifact count")
    atlas_by_id = one_by(atlas, "target_occurrence_id")
    equal(set(atlas_by_id), {row["source"]["target_occurrence_id"] for row in selected},
          "atlas equals independent exact join")
    selected_by_id = {row["source"]["target_occurrence_id"]: row for row in selected}
    for number, expected in enumerate(selected, 1):
        source = expected["source"]
        form = str(expected["surface"])
        row = atlas_by_id[source["target_occurrence_id"]]
        spec = specs[form]
        expected_values = {
            "span_id": f"G778-S{number:03d}", "page": source["page"],
            "physical_folio": source["physical_folio"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "ol_ordinal": source["ordinal"], "right_ordinal": source["right_ordinal"],
            "line_token_count": len(source["written_line_eva"].split()), "right_surface": form,
            "written_span_eva": f"ol {form}", "written_line_eva": source["written_line_eva"],
            "right_reader_exact": 1, "old_gdt777_branch": source["gdt777_branch"],
            "old_gdt777_default_de": source["gdt777_default_de"],
            "old_gdt777_contextual": source["gdt777_renderer_contextual"],
            "inherited_structural_frame": structural_frame(source["gdt777_default_de"]),
            "selected_whole_default_de": spec["selected_default_de"],
            "new_gdt778_default_de": expected["display"], "semantic_change_class": expected["change_class"],
            "fallback_replacement": expected["fallback"], "contextual_sharpening": expected["sharpening"],
            "contextual_confirmation": expected["confirmation"], "display_changed": expected["changed"],
            "confidence": spec["confidence"], "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"], "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"], "provenance_path": spec["provenance_path"],
            "promotion_status": spec["promotion_status"],
            "inherited_consumed_token_ids": source["gdt777_consumed_token_ids"],
            "gdt778_consumed_token_id": expected["token_id"],
            "same_row_inherited_consumption_takeover": expected["takeover"],
            "new_unique_consumption": expected["new_unique"], "cross_row_consumption_collision": 0,
            "selection_rule": "RIGHT_SURFACE_IN_FIXED_29_DECK_AND_RIGHT_READER_EXACT__ALL_MATCHES__NO_OCCURRENCE_ID",
            "composition_rule": ("PRESERVE_STATE_FRAME_CONFIRMATION" if expected["confirmation"] else
                                 "PRESERVE_STRUCTURAL_FRAME_AND_APPEND_EXACT_WHOLE" if expected["sharpening"] else
                                 "REPLACE_GENERIC_FALLBACK_WITH_EXACT_WHOLE"),
            "scope_status": "EXPLORATORY_EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY",
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        }
        for field, value in expected_values.items():
            equal(row[field], as_text(value), f"atlas {source['target_occurrence_id']} {field}")
        check(BANNED_DEFAULT.search(row["new_gdt778_default_de"]) is None,
              f"atlas default hygiene {source['target_occurrence_id']}")

    excluded_by_id = one_by(exclusions_art, "target_occurrence_id")
    equal(set(excluded_by_id), set(EXPECTED_EXCLUSIONS), "exclusion artifact IDs")
    for number, expected in enumerate(excluded, 1):
        source, form = expected["source"], str(expected["surface"])
        row = excluded_by_id[source["target_occurrence_id"]]
        expected_values = {
            "exclusion_id": f"G778-X{number:03d}", "page": source["page"],
            "physical_folio": source["physical_folio"], "locus": source["locus"],
            "ol_ordinal": source["ordinal"], "right_ordinal": source["right_ordinal"],
            "right_surface": form, "right_reader_exact": 0,
            "exclusion_reason": "RIGHT_COMPLETE_WHOLE_NOT_READER_EXACT",
            "selection_rule": "RIGHT_SURFACE_IN_FIXED_29_DECK_AND_RIGHT_READER_EXACT",
            "selection_uses_occurrence_id": 0, "component_export_credit": 0,
        }
        for field, value in expected_values.items():
            equal(row[field], as_text(value), f"exclusion {source['target_occurrence_id']} {field}")

    # Independently bind the 29 promotions to their locked predecessor cards.
    g734_words = one_by((row for row in read_tsv(G734_WORDS) if row["surface"] in specs), "surface")
    g734_residual = one_by((row for row in read_tsv(G734_RESIDUAL) if row["surface"] in specs), "surface")
    g736 = one_by(read_tsv(G736_BODIES), "body")
    g737 = one_by(read_tsv(G737_BODIES), "body")
    g738 = one_by(read_tsv(G738_BRIDGE), "body")
    g758 = one_by(read_tsv(G758_CENSUS), "surface")
    g759 = one_by(read_tsv(G759_DICTIONARY), "exact_expression_eva")
    g768 = one_by(read_tsv(G768_DICTIONARY), "surface")
    g769 = one_by(read_tsv(G769_DICTIONARY), "surface")
    g772 = one_by(read_tsv(G772_DICTIONARY), "whole_form")
    equal(len(g734_words), 27, "27 legacy complete cards")
    equal(set(specs) - set(g734_words), {"oldaiin", "ory"}, "two residual legacy forms")
    check({"oldaiin", "ory"} <= set(g734_residual), "residual legacy sources present")
    equal(g768["chor"]["concrete_default_de"], "Blütenstand", "later chor source")
    equal(g768["dair"]["concrete_default_de"], "Anteil II", "later dair source")
    equal(g758["ar"]["gdt758_renderer_value_de"], "Anteil", "later ar source")
    equal(g758["chol"]["gdt758_renderer_value_de"], "trocken/getrocknet", "later chol source")
    equal(int(g758["chol"]["reader_exact_occurrences"]), 303, "chol source occurrences")
    equal(int(g759["chor chol"]["exact_occurrences"]) + int(g759["chol chor"]["exact_occurrences"]),
          15, "15 bidirectional state pairs")
    equal(g769["ols"]["working_default_de"], "Maß-/Produktposten", "ols weak product rival")
    equal(g772["ols"]["formal_policy_decision"], "OLS_NULL", "ols formal null")
    check("Colatura" in g772["ols"]["concrete_replaceable_default_de"], "ols older filtrate candidate exposed")
    check("abgeseiht" in g758["ols"]["gdt758_renderer_value_de"], "ols older straining source exposed")
    for form in G736_PROMOTIONS:
        equal(g736[form]["confirmed_lexeme"], "0", f"GDT736 no lexeme {form}")
        equal(g736[form]["component_export_credit"], "0", f"GDT736 no component {form}")
    for form in G737_PROMOTIONS:
        equal(g737[form]["renderer_license"], "0", f"GDT737 unlicensed source {form}")
        equal(g737[form]["component_export_credit"], "0", f"GDT737 no component {form}")
        equal(g738[form]["body_renderer_license"], "0", f"GDT738 unlicensed source {form}")
        equal(g738[form]["component_export_credit"], "0", f"GDT738 no component {form}")

    provenance = read_tsv(ART / "GDT778_PROVENANCE_SOURCE_CONFLICT_AUDIT.tsv")
    provenance_by_form = one_by(provenance, "right_surface")
    equal(len(provenance), 29, "provenance rows")
    equal(set(provenance_by_form), set(specs), "provenance form set")
    for form in sorted(specs):
        spec = specs[form]
        if form in g734_words:
            legacy = g734_words[form]
            legacy_values = {
                "gdt734_legacy_source": "GDT734_V99R7_COMPLETE_WORD_CONFIDENCE",
                "gdt734_legacy_reading_id": legacy["reading_id"],
                "gdt734_legacy_working_meaning_de": legacy["working_meaning_de"],
                "gdt734_legacy_status": legacy["v99_audit_decision"],
            }
        else:
            legacy = g734_residual[form]
            legacy_values = {
                "gdt734_legacy_source": "GDT734_V99R7_RESIDUAL_SPLIT_INVENTORY",
                "gdt734_legacy_reading_id": "NONE",
                "gdt734_legacy_working_meaning_de": legacy["exact_v99r4_routes"],
                "gdt734_legacy_status": legacy["selection_reason"],
            }
        if form in G736_PROMOTIONS:
            source = g736[form]
            source_values: dict[str, object] = {
                "source_kind": "GDT736_BODY_CANDIDATE", "source_axis_de": source["revised_concrete_default_de"],
                "source_status": source["revision_decision"], "source_confidence": source["role_confidence"],
                "source_headed_or_target_occurrences": source["target_occurrences"], "source_bare_occurrences": "NA",
                "gdt738_discovery_decision": "NOT_APPLICABLE_GDT736_TRAINING",
                "gdt738_w23_decision": "NOT_APPLICABLE_GDT736_TRAINING",
                "source_renderer_license_before_gdt778": 0,
            }
        elif form in G737_PROMOTIONS:
            source, bridge = g737[form], g738[form]
            source_values = {
                "source_kind": "GDT737_BODY_CANDIDATE", "source_axis_de": source["concrete_body_role_de"],
                "source_status": source["export_rule"], "source_confidence": source["confidence"],
                "source_headed_or_target_occurrences": source["occurrence_total"],
                "source_bare_occurrences": source["bare_body_occurrences"],
                "gdt738_discovery_decision": bridge["discovery_decision"],
                "gdt738_w23_decision": bridge["w23_decision"],
                "source_renderer_license_before_gdt778": 0,
            }
        elif form in {"chor", "dair"}:
            source = g768[form]
            source_values = {
                "source_kind": "GDT768_LATER_COMPLETE_WHOLE", "source_axis_de": source["concrete_default_de"],
                "source_status": source["tournament_result"], "source_confidence": source["working_confidence"],
                "source_headed_or_target_occurrences": (g758[form]["reader_exact_occurrences"]
                                                        if form in g758 else raw_counts[form]),
                "source_bare_occurrences": "NA",
                "gdt738_discovery_decision": "SUPERSEDED_BY_LATER_COMPLETE_WHOLE",
                "gdt738_w23_decision": "SUPERSEDED_BY_LATER_COMPLETE_WHOLE",
                "source_renderer_license_before_gdt778": 1,
            }
        elif form in {"ar", "chol"}:
            source = g758[form]
            source_values = {
                "source_kind": "GDT758_GDT759_LATER_COMPLETE_WHOLE",
                "source_axis_de": source["gdt758_renderer_value_de"],
                "source_status": "GDT758_GLOBAL" + ("__GDT759_15_BIDIRECTIONAL_STATE_PAIRS" if form == "chol" else ""),
                "source_confidence": source["working_confidence"],
                "source_headed_or_target_occurrences": source["reader_exact_occurrences"],
                "source_bare_occurrences": "NA",
                "gdt738_discovery_decision": "SUPERSEDED_BY_LATER_COMPLETE_WHOLE",
                "gdt738_w23_decision": "SUPERSEDED_BY_LATER_COMPLETE_WHOLE",
                "source_renderer_license_before_gdt778": 1,
            }
        else:
            equal(form, "ols", "only source-conflict form")
            source = g769[form]
            source_values = {
                "source_kind": "GDT769_GDT772_SOURCE_CONFLICT", "source_axis_de": source["working_default_de"],
                "source_status": f"{source['role_disposition']}__{g772[form]['formal_policy_decision']}",
                "source_confidence": source["working_confidence"],
                "source_headed_or_target_occurrences": g758[form]["reader_exact_occurrences"],
                "source_bare_occurrences": "NA",
                "gdt738_discovery_decision": "SUPERSEDED_BY_LATER_SOURCE_CONFLICT",
                "gdt738_w23_decision": "SUPERSEDED_BY_LATER_SOURCE_CONFLICT",
                "source_renderer_license_before_gdt778": 0,
            }
        expected_provenance = {
            "right_surface": form, "provenance_path": spec["provenance_path"],
            "promotion_status": spec["promotion_status"], "selected_default_de": spec["selected_default_de"],
            "confidence": spec["confidence"], **source_values, **legacy_values,
            "ol_local_raw_occurrences": raw_counts[form],
            "ol_local_reader_exact_occurrences": exact_counts[form], "source_conflict": int(form == "ols"),
            "source_conflict_detail": ("GDT758_ABGESEIHTES_ENDPRODUKT_RETIRED__GDT769_MASS_PRODUCT_FIELD_RIVAL__GDT772_OLS_NULL"
                                       if form == "ols" else "NONE"),
            "gdt778_conflict_decision": ("NEW_C0_PRODUKTPOSTEN_EXACT_OL_PLUS_WHOLE_ONLY__FILTRATE_OR_STRAINING_NOT_SELECTED"
                                         if form == "ols" else "NO_SOURCE_CONFLICT"),
            "legacy_literal_patient_quarantined": 1, "exact_complete_whole_only": 1,
            "free_component_export": 0, "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0,
        }
        for field, value in expected_provenance.items():
            equal(provenance_by_form[form][field], as_text(value), f"provenance {form} {field}")
    equal(Counter(row["source_kind"] for row in provenance), Counter({
        "GDT737_BODY_CANDIDATE": 21, "GDT736_BODY_CANDIDATE": 3,
        "GDT768_LATER_COMPLETE_WHOLE": 2, "GDT758_GDT759_LATER_COMPLETE_WHOLE": 2,
        "GDT769_GDT772_SOURCE_CONFLICT": 1,
    }), "provenance source partition")

    registry = read_tsv(ART / "EXACT_WHOLE_29_REGISTRY.tsv")
    dictionary = read_tsv(ART / "GDT778_WORKING_DICTIONARY.tsv")
    registry_by_form = one_by(registry, "right_surface")
    dictionary_by_form = one_by(dictionary, "entry")
    equal(len(registry), 29, "registry rows")
    equal(len(dictionary), 29, "dictionary rows")
    equal(set(registry_by_form), set(specs), "registry form set")
    equal(set(dictionary_by_form), set(specs), "dictionary form set")
    selected_by_form: dict[str, list[dict[str, object]]] = {
        form: [row for row in selected if row["surface"] == form] for form in specs
    }
    for form, spec in specs.items():
        local = selected_by_form[form]
        prov = provenance_by_form[form]
        expected_registry = {
            "selected_default_de": spec["selected_default_de"], "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"], "confidence": spec["confidence"],
            "provenance_path": spec["provenance_path"], "promotion_status": spec["promotion_status"],
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "local_raw_occurrences": raw_counts[form], "local_reader_exact_occurrences": exact_counts[form],
            "local_nonexact_exclusions": raw_counts[form] - exact_counts[form],
            "fallback_replacements": sum(int(row["fallback"]) for row in local),
            "contextual_sharpenings": sum(int(row["sharpening"]) for row in local),
            "contextual_confirmations": sum(int(row["confirmation"]) for row in local),
            "actual_display_changes": sum(int(row["changed"]) for row in local),
            "source_kind": prov["source_kind"], "source_status": prov["source_status"],
            "scope_status": "EXACT_OL_PLUS_COMPLETE_WHOLE_OCCURRENCES_ONLY",
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        }
        for field, value in expected_registry.items():
            equal(registry_by_form[form][field], as_text(value), f"registry {form} {field}")
        expected_dictionary = {
            "preferred_gdt778_default_de": spec["selected_default_de"], "confidence": spec["confidence"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "reader_exact_ol_contexts": len(local),
            "rendered_displays_de": " || ".join(sorted({str(row["display"]) for row in local})),
            "fallback_replacements": expected_registry["fallback_replacements"],
            "contextual_sharpenings": expected_registry["contextual_sharpenings"],
            "contextual_confirmations": expected_registry["contextual_confirmations"],
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "provenance_path": spec["provenance_path"], "promotion_status": spec["promotion_status"],
            "scope": "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT", "replaceable": 1,
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        }
        for field, value in expected_dictionary.items():
            equal(dictionary_by_form[form][field], as_text(value), f"dictionary {form} {field}")
        check(BANNED_DEFAULT.search(registry_by_form[form]["selected_default_de"]) is None,
              f"registry default hygiene {form}")
        check(BANNED_DEFAULT.search(dictionary_by_form[form]["preferred_gdt778_default_de"]) is None,
              f"dictionary default hygiene {form}")

    renderer = read_tsv(ART / "GDT778_376_RENDERER.tsv")
    equal(len(renderer), 376, "renderer rows")
    equal([row["target_occurrence_id"] for row in renderer],
          [row["target_occurrence_id"] for row in parent], "renderer preserves row order")
    renderer_by_id = one_by(renderer, "target_occurrence_id")
    for source in parent:
        row = renderer_by_id[source["target_occurrence_id"]]
        for field, value in source.items():
            equal(row[field], value, f"renderer inherited field {source['target_occurrence_id']} {field}")
        expected = selected_by_id.get(source["target_occurrence_id"])
        if expected is None:
            expected_new = {
                "gdt778_branch": "INHERITED_GDT777", "gdt778_default_de": source["gdt777_default_de"],
                "gdt778_renderer_contextual": source["gdt777_renderer_contextual"],
                "gdt778_span_id": source["gdt777_span_id"], "gdt778_exact_whole": "NONE",
                "gdt778_confidence": source["gdt777_confidence"],
                "gdt778_consumed_token_count": source["gdt777_consumed_token_count"],
                "gdt778_consumed_token_ids": source["gdt777_consumed_token_ids"],
                "gdt778_fallback_replacement": 0, "gdt778_contextual_sharpening": 0,
                "gdt778_contextual_confirmation": 0, "gdt778_display_changed": 0,
                "gdt778_same_row_consumption_takeover": 0, "gdt778_new_unique_consumption": 0,
                "gdt778_positive_evidence": source["gdt777_positive_evidence"],
                "gdt778_counterevidence": source["gdt777_counterevidence"],
                "gdt778_dispatch_rule": "INHERITED_GDT777", "gdt778_scope_status": "INHERITED_GDT777",
            }
        else:
            form = str(expected["surface"])
            spec = specs[form]
            expected_new = {
                "gdt778_branch": "GDT778_EXACT_OL_PLUS_COMPLETE_WHOLE",
                "gdt778_default_de": expected["display"], "gdt778_renderer_contextual": 1,
                "gdt778_span_id": atlas_by_id[source["target_occurrence_id"]]["span_id"],
                "gdt778_exact_whole": form, "gdt778_confidence": spec["confidence"],
                "gdt778_consumed_token_count": 1, "gdt778_consumed_token_ids": expected["token_id"],
                "gdt778_fallback_replacement": expected["fallback"],
                "gdt778_contextual_sharpening": expected["sharpening"],
                "gdt778_contextual_confirmation": expected["confirmation"],
                "gdt778_display_changed": expected["changed"],
                "gdt778_same_row_consumption_takeover": expected["takeover"],
                "gdt778_new_unique_consumption": expected["new_unique"],
                "gdt778_positive_evidence": spec["positive_evidence"],
                "gdt778_counterevidence": spec["counterevidence"],
                "gdt778_dispatch_rule": "RIGHT_SURFACE_IN_FIXED_29_DECK_AND_RIGHT_READER_EXACT__ALL_MATCHES__NO_OCCURRENCE_ID",
                "gdt778_scope_status": "EXPLORATORY_EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY",
            }
        expected_new.update({
            "gdt778_default_is_translation": 0, "gdt778_confirmed_lexeme": 0,
            "gdt778_confirmed_plaintext": 0, "gdt778_component_export_credit": 0,
        })
        for field, value in expected_new.items():
            equal(row[field], as_text(value), f"renderer dispatch {source['target_occurrence_id']} {field}")
        check(BANNED_DEFAULT.search(row["gdt778_default_de"]) is None,
              f"renderer default hygiene {source['target_occurrence_id']}")

    equal(sum(int(row["gdt778_renderer_contextual"]) for row in renderer), 195, "renderer contextual 195")
    equal(sum(1 - int(row["gdt778_renderer_contextual"]) for row in renderer), 181, "renderer fallback 181")
    equal(sum(int(row["gdt778_fallback_replacement"]) for row in renderer), 32, "renderer replacements 32")
    equal(sum(int(row["gdt778_contextual_sharpening"]) for row in renderer), 5, "renderer sharpenings 5")
    equal(sum(int(row["gdt778_contextual_confirmation"]) for row in renderer), 2, "renderer confirmations 2")
    equal(sum(int(row["gdt778_display_changed"]) for row in renderer), 37, "renderer display changes 37")
    equal(sum(int(row["gdt778_same_row_consumption_takeover"]) for row in renderer), 4,
          "renderer same-row takeovers 4")
    equal(sum(int(row["gdt778_new_unique_consumption"]) for row in renderer), 35,
          "renderer new consumption 35")

    owners: dict[str, str] = {}
    collisions: list[tuple[str, str, str]] = []
    for row in renderer:
        for token_id in split_ids(row["gdt778_consumed_token_ids"]):
            if token_id in owners:
                collisions.append((token_id, owners[token_id], row["target_occurrence_id"]))
            owners[token_id] = row["target_occurrence_id"]
            check(token_id.startswith(row["locus"] + "@"), f"consumption stays on row locus {token_id}")
            try:
                ordinal = int(token_id.rsplit("@", 1)[1])
            except (IndexError, ValueError):
                ordinal = 0
            check(1 <= ordinal <= len(row["written_line_eva"].split()), f"consumption ordinal valid {token_id}")
    equal(collisions, [], "zero cross-row collisions")
    equal(len(owners), 155, "155 unique consumed token IDs")

    passages = read_tsv(ART / "GDT778_PASSAGE_PATCHES.tsv")
    changed = [row for row in selected if int(row["changed"])]
    equal(len(passages), 37, "changed passage count")
    passages_by_id = one_by(passages, "target_occurrence_id")
    equal(set(passages_by_id), {row["source"]["target_occurrence_id"] for row in changed},
          "passages equal changed spans")
    old_by_position = {(row["locus"], int(row["ordinal"])): row for row in parent}
    new_by_position = {(row["locus"], int(row["ordinal"])): row for row in renderer}
    for number, expected in enumerate(changed, 1):
        source = expected["source"]
        row = passages_by_id[source["target_occurrence_id"]]
        expected_values = {
            "passage_patch_id": f"G778-P{number:03d}",
            "span_id": atlas_by_id[source["target_occurrence_id"]]["span_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "right_surface": expected["surface"], "semantic_change_class": expected["change_class"],
            "old_display_de": source["gdt777_default_de"], "new_display_de": expected["display"],
            "selected_whole_default_de": specs[str(expected["surface"])]["selected_default_de"],
            "written_line_eva": source["written_line_eva"],
            "inherited_gdt777_patch_de": render_line(source["locus"], source["written_line_eva"],
                                                      old_by_position, "gdt777"),
            "gdt778_practical_patch_de": render_line(source["locus"], source["written_line_eva"],
                                                      new_by_position, "gdt778"),
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        }
        for field, value in expected_values.items():
            equal(row[field], as_text(value), f"passage {source['target_occurrence_id']} {field}")
        check(row["inherited_gdt777_patch_de"] != row["gdt778_practical_patch_de"],
              f"passage actually changed {source['target_occurrence_id']}")

    packet_path = ART / "GDT778_GDT388_RELATION_PACKET.tsv"
    packet = read_tsv(packet_path)
    crosswalk = read_tsv(ART / "GDT778_RELATION_EDGE_CROSSWALK.tsv")
    equal(len(packet), 39, "packet rows")
    equal(len(crosswalk), 39, "crosswalk rows")
    for number, (edge, cross, atlas_row) in enumerate(zip(packet, crosswalk, atlas), 1):
        edge_id = f"G778-E{number:03d}"
        expected_edge = {
            "edge_id": edge_id, "batch_id": "GDT778_EXACT_OL_COMPLETE_WHOLE",
            "page": atlas_row["page"], "physical_folio": atlas_row["physical_folio"],
            "diagram_unit_id": f"LINE:{atlas_row['locus']}",
            "pivot_visual_id": f"TOKEN:{atlas_row['locus']}:{atlas_row['ol_ordinal']}",
            "pivot_locus": f"{atlas_row['locus']}@{atlas_row['ol_ordinal']}",
            "target_visual_id": f"TOKEN:{atlas_row['locus']}:{atlas_row['right_ordinal']}",
            "target_locus": f"{atlas_row['locus']}@{atlas_row['right_ordinal']}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT777", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT778_RUNNER",
            "relation_reviewer": "GDT778_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION", "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        }
        for field, value in expected_edge.items():
            equal(edge[field], value, f"packet {edge_id} {field}")
        expected_cross = {
            "edge_id": edge_id, "batch_id": "GDT778_EXACT_OL_COMPLETE_WHOLE",
            "span_id": atlas_row["span_id"], "target_occurrence_id": atlas_row["target_occurrence_id"],
            "page": atlas_row["page"], "physical_folio": atlas_row["physical_folio"],
            "locus": atlas_row["locus"], "ol_ordinal": atlas_row["ol_ordinal"],
            "right_ordinal": atlas_row["right_ordinal"], "right_surface": atlas_row["right_surface"],
            "written_span_eva": atlas_row["written_span_eva"], "selection_rule": atlas_row["selection_rule"],
            "score_eligible": "0", "component_export_credit": "0",
        }
        for field, value in expected_cross.items():
            equal(cross[field], value, f"crosswalk {edge_id} {field}")
    completed_intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, text=True, capture_output=True,
    )
    equal(completed_intake.returncode, 0, "relation packet checker exit")
    intake = json.loads(completed_intake.stdout) if completed_intake.returncode == 0 else {}
    stored_intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    equal(intake, stored_intake, "relation intake replay")
    expected_intake = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 39, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    equal(intake, expected_intake, "packet gates remain closed")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    equal(result["cohort"], {
        "renderer_rows": 376, "deck_forms": 29, "raw_candidates": 41,
        "reader_exact_spans": 39, "exactness_exclusions": 2, "page_labels": 31,
        "physical_folios": 25, "loci": 39,
    }, "result cohort")
    equal(result["changes"], {
        "fallback_replacements": 32, "contextual_sharpenings": 5,
        "contextual_confirmations": 2, "actual_display_changes": 37, "passage_patches": 37,
    }, "result changes")
    equal(result["renderer"], {
        "gdt777_contextual": 163, "gdt778_contextual": 195,
        "gdt777_fallbacks": 213, "gdt778_fallbacks": 181,
    }, "result renderer")
    equal(result["consumption"], {
        "gdt777_unique_right_tokens": 120, "gdt778_selected_right_tokens": 39,
        "same_row_inherited_takeovers": 4, "new_unique_right_tokens": 35,
        "total_unique_right_tokens": 155, "cross_row_collisions": 0,
    }, "result consumption")
    equal(result["source_model"], {
        "later_complete_whole_defaults": 4, "new_body_candidate_promotions": 24,
        "explicit_source_conflicts": 1, "ols_selected_default_de": "Produktposten",
        "ols_confidence": "C0", "ols_formal_prior": "OLS_NULL",
        "older_filtrate_or_straining_reading_selected": False,
    }, "result source model")
    equal(result["relation_packet"], intake, "result packet summary")
    for field in ("retired_literal_patient_leaks_in_selected_defaults", "confirmed_lexemes",
                  "confirmed_plaintext_clauses", "component_exports", "new_pages", "new_images",
                  "new_ocr", "new_transcriptions", "sealed_pages_accessed"):
        equal(result[field], 0, f"result zero {field}")
    equal(result["source_locks"], 13, "result source locks")
    equal(result["dictionary_rows"], 29, "result dictionary rows")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    equal(manifest["sealed_data"], {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed manifest")
    for rows, label in ((parent, "parent"), (atlas, "atlas"), (exclusions_art, "exclusions"),
                        (renderer, "renderer"), (packet, "packet"), (crosswalk, "crosswalk"),
                        (passages, "passages")):
        for row in rows:
            for field in ("page", "physical_folio"):
                if field in row:
                    check(not SEALED_LABEL.fullmatch(row[field]), f"sealed page absent {label} {field}")

    report_text = REPORT.read_text(encoding="utf-8")
    for fragment in (
        "**41** rohe", "**39** exakte", "**31** Seitenlabels", "**25** physischen Folios",
        "**32** den generischen Fallback", "**37** wirklich", "**120→155**",
        "keine Übersetzung oder\nLexemidentifikation",
    ):
        check(fragment in report_text, f"report claim {fragment}")

    # Byte-replay every runner artifact plus the report in a temporary directory under EXP.
    replayed = 0
    replay_hashes: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="gdt778_validate_", dir=EXP) as temporary:
        temporary_path = Path(temporary)
        replay_artifacts = temporary_path / "artifacts"
        replay_artifacts.mkdir()
        replay_report = temporary_path / "REPORT.md"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_artifacts),
             "--report-path", str(replay_report)],
            cwd=ROOT, text=True, capture_output=True,
        )
        equal(completed.returncode, 0, "runner replay exit")
        for name in EXPECTED_OUTPUTS:
            generated, published = replay_artifacts / name, ART / name
            check(generated.is_file(), f"replay output exists {name}")
            if generated.is_file():
                equal(generated.read_bytes(), published.read_bytes(), f"byte replay {name}")
                replay_hashes[name] = sha256(generated)
                replayed += 1
        check(replay_report.is_file(), "replay output exists REPORT.md")
        if replay_report.is_file():
            equal(replay_report.read_bytes(), REPORT.read_bytes(), "byte replay REPORT.md")
            replay_hashes["REPORT.md"] = sha256(replay_report)
            replayed += 1

    validation = {
        "experiment_id": "GDT778", "status": "PASS" if not failures else "FAIL",
        "checks": checks, "failures": failures, "source_locks": len(locks),
        "independent_cohort": {
            "renderer_rows": len(parent), "deck_forms": len(specs), "raw_candidates": len(raw),
            "reader_exact_spans": len(selected), "nonexact_exclusions": len(excluded),
            "page_labels": len({row["source"]["page"] for row in selected}),
            "physical_folios": len({row["source"]["physical_folio"] for row in selected}),
            "fallback_replacements": sum(int(row["fallback"]) for row in selected),
            "contextual_sharpenings": sum(int(row["sharpening"]) for row in selected),
            "contextual_confirmations": sum(int(row["confirmation"]) for row in selected),
            "display_changes": sum(int(row["changed"]) for row in selected),
        },
        "independent_consumption": {
            "inherited_unique": len(parent_owners),
            "same_row_takeovers": sum(int(row["takeover"]) for row in selected),
            "new_unique": sum(int(row["new_unique"]) for row in selected),
            "final_unique": len(owners), "cross_row_collisions": len(collisions),
        },
        "occurrence_free_ast_selection": not any(
            term in text for text in predicate_text for term in forbidden_predicate_terms
        ),
        "relation_packet_status": intake.get("status", "CHECK_FAILED"),
        "relation_packet_score_ready": intake.get("score_ready", False),
        "runner_outputs_plus_report_replayed": replayed, "replay_sha256": replay_hashes,
        "sealed_pages_accessed": 0,
        "claim_ceiling": "Replaceable exact ol plus complete-whole defaults only; no component, lexeme, plaintext, language, or substance identity.",
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
