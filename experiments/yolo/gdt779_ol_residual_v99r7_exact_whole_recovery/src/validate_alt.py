#!/usr/bin/env python3
"""Independent alternate validator for GDT779.

This validator does not import the experiment builder or the primary validator.
It reconstructs the fixed cohort and every material invariant from locked
inputs, then runs the builder only in an isolated temporary directory for a
byte-for-byte replay check.
"""
from __future__ import annotations

import csv
import hashlib
import json
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
    raise RuntimeError("repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery"
SRC = EXP / "src"
ART = EXP / "artifacts"
ALT_RESULT = ART / "ALT_VALIDATION.json"

PARENT_RENDERER = ROOT / "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion/artifacts/GDT778_376_RENDERER.tsv"
PARENT_RESULT = ROOT / "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion/artifacts/RESULT.json"
V99_PATH = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G737_PATH = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G738_PATH = ROOT / "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/BODY_120_SEMANTIC_BRIDGE.tsv"
G749_PATH = ROOT / "experiments/yolo/gdt749_outside_frame_whole_role_distribution/artifacts/TARGET_OUTSIDE_ROLE_CENSUS.tsv"
G754_PATH = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G755_GLOSS_PATH = ROOT / "experiments/yolo/gdt755_top24_historical_register_crosswalk/artifacts/TOP24_WORKING_GLOSS_UPDATE.tsv"
G755_OCC_PATH = ROOT / "experiments/yolo/gdt755_top24_historical_register_crosswalk/artifacts/TOP24_448_OCCURRENCE_FIELDS.tsv"
G758_PATH = ROOT / "experiments/yolo/gdt758_ychor_follower_global_content_census/artifacts/FOLLOWER_11_GLOBAL_CENSUS.tsv"

SPECS_PATH = SRC / "RESIDUAL_V99R7_EXACT_WHOLE_SPECS.tsv"
SOURCE_LOCK_PATH = SRC / "SOURCE_LOCK.tsv"
RUNNER_PATH = SRC / "run.py"

SELECTION_RULE = "GDT778_RENDERER_CONTEXTUAL_0_AND_COMPLETE_RIGHT_SURFACE_V99R7_CARD_MATCH_AND_RIGHT_READER_EXACT_1"
SELECTED_BRANCH = "GDT779_EXACT_OL_PLUS_RESIDUAL_V99R7_WHOLE"
SCOPE = "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY"
SANITIZED = frozenset({"cheeor", "cheor", "lkedy", "loeees", "olshdy", "qokar"})
NEW_SCOPES = frozenset({"chcthy", "daiin", "kaiiin"})
COMPOSED = frozenset({"chcphy", "okeeey"})
QOCKHEY = frozenset({"qockhey"})
CLASS_COUNTS = Counter({
    "DIRECT_INHERITED_WHOLE_CARD": 32,
    "RETIRED_PATIENT_SANITIZATION": 6,
    "NEW_EXACT_OL_SCOPE": 3,
    "COMPOSITION_DERIVED_WHOLE__NO_COMPONENT_EXPORT": 2,
    "GDT755_LATER_COMPLETE_WHOLE_REPLACEMENT": 1,
})
CONFIDENCE_COUNTS = Counter({"C0": 13, "C1": 17, "C2": 14})
ACTIVE_BANNED_RE = re.compile(r"(?i)(pulver|samen|wurzel|holz|droge|filtrat|abgeseih)")

CORE_FIELDS = (
    "target_occurrence_id", "page", "physical_folio", "locus", "section", "language", "hand",
    "ordinal", "right_surface", "right_ordinal", "right_reader_exact", "written_line_eva",
)
PARENT_STATE_FIELDS = (
    "gdt778_branch", "gdt778_default_de", "gdt778_renderer_contextual", "gdt778_span_id",
    "gdt778_exact_whole", "gdt778_confidence", "gdt778_consumed_token_count",
    "gdt778_consumed_token_ids", "gdt778_fallback_replacement", "gdt778_contextual_sharpening",
    "gdt778_contextual_confirmation", "gdt778_display_changed",
    "gdt778_same_row_consumption_takeover", "gdt778_new_unique_consumption",
    "gdt778_dispatch_rule", "gdt778_scope_status", "gdt778_default_is_translation",
    "gdt778_confirmed_lexeme", "gdt778_confirmed_plaintext", "gdt778_component_export_credit",
)
REPLAY_FILES = (
    "GDT779_50_EXACT_WHOLE_ATLAS.tsv",
    "GDT779_49_EXACTNESS_EXCLUSIONS.tsv",
    "GDT779_179_PRECEDENCE_SHADOW_AUDIT.tsv",
    "GDT779_376_RENDERER.tsv",
    "GDT779_WORKING_DICTIONARY.tsv",
    "GDT779_PASSAGE_PATCHES.tsv",
    "GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv",
    "GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv",
    "GDT779_GDT388_RELATION_PACKET.tsv",
    "GDT779_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json",
    "RESULT.json",
    "README.md",
)


class ValidationError(RuntimeError):
    """Raised on the first independently detected mismatch."""


CHECKS: list[dict[str, object]] = []


def compact_value(value: object) -> object:
    """Make failure diagnostics JSON-safe without embedding full artifacts."""
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, Counter):
        return {str(key): count for key, count in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (set, frozenset)):
        return sorted(compact_value(item) for item in value)
    if isinstance(value, tuple):
        return [compact_value(item) for item in value]
    if isinstance(value, list):
        return [compact_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): compact_value(item) for key, item in value.items()}
    return value


def record(name: str, condition: bool, actual: object = None, expected: object = None) -> None:
    entry: dict[str, object] = {"name": name, "passed": bool(condition)}
    if not condition and actual is not None:
        entry["actual"] = compact_value(actual)
    if not condition and expected is not None:
        entry["expected"] = compact_value(expected)
    CHECKS.append(entry)
    if not condition:
        raise ValidationError(f"{name}: actual={actual!r}, expected={expected!r}")


def equal(name: str, actual: object, expected: object) -> None:
    record(name, actual == expected, actual, expected)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_by(rows: Sequence[Mapping[str, str]], key: str, label: str) -> dict[str, Mapping[str, str]]:
    result: dict[str, Mapping[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in result:
            raise ValidationError(f"duplicate {label} key {value}")
        result[value] = row
    return result


def one_card_by_surface(rows: Sequence[Mapping[str, str]]) -> dict[str, list[Mapping[str, str]]]:
    result: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        result[row["surface"]].append(row)
    return result


def split_token_ids(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def select_row(contextual: str, reader_exact: str, right_surface: str,
               fixed_deck: frozenset[str]) -> bool:
    """The full selector: deliberately no row, ID, page, locus or semantics argument."""
    return contextual == "0" and reader_exact == "1" and right_surface in fixed_deck


def expected_disposition(parent: Mapping[str, str], final_deck: frozenset[str]) -> str:
    final = parent["right_surface"] in final_deck
    fallback = parent["gdt778_renderer_contextual"] == "0"
    exact = parent["right_reader_exact"] == "1"
    if final and exact and fallback:
        return "SELECTED_GDT779_FALLBACK"
    if final and exact and not fallback:
        return "PROTECTED_EXACT_CONTEXTUAL"
    if final and not exact and fallback:
        return "EXCLUDED_NONEXACT_FINAL_FORM"
    if final and not exact and not fallback:
        return "PROTECTED_NONEXACT_CONTEXTUAL"
    if not final and exact and fallback:
        return "UNEXPECTED_EXACT_RAW_ONLY_FALLBACK"
    if not final and exact and not fallback:
        return "PROTECTED_EXACT_CONTEXTUAL_RAW_ONLY_FORM"
    if not final and not exact and fallback:
        return "EXCLUDED_NONEXACT_RAW_ONLY_FORM"
    return "PROTECTED_NONEXACT_CONTEXTUAL_RAW_ONLY_FORM"


def render_line(locus: str, written_line: str,
                rows_by_position: Mapping[tuple[str, int], Mapping[str, str]], prefix: str) -> str:
    rendered: list[str] = []
    consumed: set[int] = set()
    for ordinal, token in enumerate(written_line.split(), 1):
        if ordinal in consumed:
            continue
        row = rows_by_position.get((locus, ordinal))
        if row is None:
            rendered.append(token)
            continue
        if int(row[f"{prefix}_renderer_contextual"]):
            rendered.append(f"⟦{row[f'{prefix}_default_de']}⟧")
            count = int(row[f"{prefix}_consumed_token_count"])
            consumed.update(range(ordinal + 1, ordinal + count + 1))
        else:
            rendered.append(token)
    return " ".join(rendered)


def validate() -> dict[str, object]:
    # Locked inputs and sealed-page boundary.
    locks = read_tsv(SOURCE_LOCK_PATH)
    equal("source_lock_count", len(locks), 11)
    lock_paths: set[str] = set()
    for lock in locks:
        relative = Path(lock["path"])
        record("source_lock_relative_paths", not relative.is_absolute() and ".." not in relative.parts)
        record("source_lock_unique_paths", lock["path"] not in lock_paths)
        lock_paths.add(lock["path"])
        source = ROOT / relative
        record("source_lock_file_exists", source.is_file(), lock["path"], "existing file")
        equal("source_lock_sha256", sha256(source), lock["expected_sha256"])

    specs_rows = read_tsv(SPECS_PATH)
    specs = unique_by(specs_rows, "right_surface", "spec")
    deck = frozenset(specs)
    equal("fixed_deck_rows", len(specs_rows), 44)
    equal("fixed_deck_unique_forms", len(deck), 44)
    equal("card_class_partition", Counter(row["card_class"] for row in specs_rows), CLASS_COUNTS)
    equal("confidence_partition", Counter(row["confidence"] for row in specs_rows), CONFIDENCE_COUNTS)
    class_sets = {
        cls: frozenset(row["right_surface"] for row in specs_rows if row["card_class"] == cls)
        for cls in CLASS_COUNTS
    }
    equal("sanitized_form_set", class_sets["RETIRED_PATIENT_SANITIZATION"], SANITIZED)
    equal("new_scope_form_set", class_sets["NEW_EXACT_OL_SCOPE"], NEW_SCOPES)
    equal("composition_whole_set", class_sets["COMPOSITION_DERIVED_WHOLE__NO_COMPONENT_EXPORT"], COMPOSED)
    equal("qockhey_replacement_set", class_sets["GDT755_LATER_COMPLETE_WHOLE_REPLACEMENT"], QOCKHEY)
    record("spec_scope_is_exact_whole_only", all(row["scope_status"] == SCOPE for row in specs_rows))
    record("spec_forms_are_complete_surfaces", all(row["right_surface"] and " " not in row["right_surface"] for row in specs_rows))
    record("spec_defaults_and_rivals_distinct", all(
        len({row["selected_default_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3
        and all(row[key] and row[key] != "NONE" for key in ("selected_default_de", "alternate_1_de", "alternate_2_de"))
        for row in specs_rows
    ))
    record("no_retired_patient_in_active_specs", all(
        ACTIVE_BANNED_RE.search(" ".join((row["selected_default_de"], row["alternate_1_de"],
                                          row["alternate_2_de"], row["positive_evidence"],
                                          row["counterevidence"]))) is None
        for row in specs_rows
    ))
    equal("cheor_short_sanitized_default", specs["cheor"]["selected_default_de"], "trockener Teil")
    equal("qockhey_short_later_default", specs["qockhey"]["selected_default_de"], "mische")
    equal("qockhey_exploratory_confidence", specs["qockhey"]["confidence"], "C0")

    v99_rows = read_tsv(V99_PATH)
    v99 = one_card_by_surface(v99_rows)
    equal("v99_registry_rows", len(v99_rows), 1606)
    record("fixed_forms_have_one_v99_card", all(len(v99.get(form, [])) == 1 for form in deck))

    parent = read_tsv(PARENT_RENDERER)
    parent_result = read_json(PARENT_RESULT)
    equal("parent_renderer_rows", len(parent), 376)
    equal("parent_unique_target_ids", len({row["target_occurrence_id"] for row in parent}), 376)
    record("parent_required_columns", bool(parent) and set((*CORE_FIELDS, *PARENT_STATE_FIELDS)) <= set(parent[0]))
    equal("parent_contextual_count", sum(int(row["gdt778_renderer_contextual"]) for row in parent), 195)
    equal("parent_fallback_count", sum(row["gdt778_renderer_contextual"] == "0" for row in parent), 181)
    equal("parent_result_contextual", parent_result["renderer"]["gdt778_contextual"], 195)
    equal("parent_result_consumed", parent_result["consumption"]["total_unique_right_tokens"], 155)
    record("sealed_pages_absent_from_parent", all(
        not row["page"].lower().startswith("f84") and not row["physical_folio"].lower().startswith("f84")
        for row in parent
    ))
    geometry_ok = True
    for row in parent:
        tokens = row["written_line_eva"].split()
        ordinal = int(row["ordinal"])
        right_ordinal = int(row["right_ordinal"])
        geometry_ok &= 1 <= ordinal <= len(tokens) and tokens[ordinal - 1] == "ol"
        if right_ordinal == 0:
            geometry_ok &= row["right_surface"] == "NONE"
        else:
            geometry_ok &= right_ordinal == ordinal + 1 and right_ordinal <= len(tokens)
            geometry_ok &= tokens[right_ordinal - 1] == row["right_surface"]
    record("parent_ol_right_geometry", geometry_ok)

    # Truth table and actual pure selection.
    probe_deck = frozenset({"x"})
    truth = {
        (contextual, exact, member): select_row(contextual, exact, "x" if member else "y", probe_deck)
        for contextual in ("0", "1") for exact in ("0", "1") for member in (False, True)
    }
    equal("selector_truth_table", {k for k, value in truth.items() if value}, {("0", "1", True)})

    fallbacks = [row for row in parent if row["gdt778_renderer_contextual"] == "0"]
    raw = [row for row in fallbacks if row["right_surface"] in v99]
    raw_forms = frozenset(row["right_surface"] for row in raw)
    selected = [row for row in parent if select_row(
        row["gdt778_renderer_contextual"], row["right_reader_exact"], row["right_surface"], deck
    )]
    raw_exact = [row for row in raw if row["right_reader_exact"] == "1"]
    nonexact = [row for row in raw if row["right_reader_exact"] != "1"]
    equal("raw_card_fallback_rows", len(raw), 99)
    equal("raw_card_fallback_forms", len(raw_forms), 76)
    record("raw_forms_have_one_v99_card", all(len(v99[form]) == 1 for form in raw_forms))
    equal("pure_selection_equals_raw_exact", [row["target_occurrence_id"] for row in selected],
          [row["target_occurrence_id"] for row in raw_exact])
    equal("selected_rows", len(selected), 50)
    equal("selected_forms", frozenset(row["right_surface"] for row in selected), deck)
    equal("selected_loci", len({row["locus"] for row in selected}), 49)
    equal("selected_page_labels", len({row["page"] for row in selected}), 33)
    equal("selected_physical_folios", len({row["physical_folio"] for row in selected}), 24)
    equal("nonexact_exclusion_rows", len(nonexact), 49)
    equal("nonexact_exclusion_forms", len({row["right_surface"] for row in nonexact}), 36)
    exact_forms = {row["right_surface"] for row in raw_exact}
    nonexact_forms = {row["right_surface"] for row in nonexact}
    equal("exact_nonexact_form_overlap", exact_forms & nonexact_forms, {"cheedy", "cheol", "daiin", "dam"})
    equal("only_double_selected_locus", {locus: count for locus, count in Counter(row["locus"] for row in selected).items() if count > 1}, {"f75r.26": 2})

    atlas = read_tsv(ART / "GDT779_50_EXACT_WHOLE_ATLAS.tsv")
    exclusions = read_tsv(ART / "GDT779_49_EXACTNESS_EXCLUSIONS.tsv")
    shadow = read_tsv(ART / "GDT779_179_PRECEDENCE_SHADOW_AUDIT.tsv")
    renderer = read_tsv(ART / "GDT779_376_RENDERER.tsv")
    dictionary = read_tsv(ART / "GDT779_WORKING_DICTIONARY.tsv")
    passages = read_tsv(ART / "GDT779_PASSAGE_PATCHES.tsv")
    provenance = read_tsv(ART / "GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv")
    residual = read_tsv(ART / "GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv")
    packet = read_tsv(ART / "GDT779_GDT388_RELATION_PACKET.tsv")
    crosswalk = read_tsv(ART / "GDT779_RELATION_EDGE_CROSSWALK.tsv")
    result = read_json(ART / "RESULT.json")

    equal("atlas_rows", len(atlas), 50)
    equal("atlas_parent_order", [row["target_occurrence_id"] for row in atlas],
          [row["target_occurrence_id"] for row in selected])
    equal("atlas_sequential_span_ids", [row["span_id"] for row in atlas],
          [f"G779-S{number:03d}" for number in range(1, 51)])
    parent_by_id = unique_by(parent, "target_occurrence_id", "parent")
    atlas_by_id = unique_by(atlas, "target_occurrence_id", "atlas")
    atlas_ok = True
    for row in atlas:
        source = parent_by_id[row["target_occurrence_id"]]
        spec = specs[source["right_surface"]]
        card = v99[source["right_surface"]][0]
        token_id = f"{source['locus']}@{source['right_ordinal']}"
        expected_pairs = {
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "ol_ordinal": source["ordinal"], "right_ordinal": source["right_ordinal"],
            "right_surface": source["right_surface"], "written_line_eva": source["written_line_eva"],
            "written_span_eva": f"ol {source['right_surface']}", "right_reader_exact": "1",
            "old_gdt778_branch": source["gdt778_branch"], "old_gdt778_default_de": source["gdt778_default_de"],
            "old_gdt778_contextual": "0", "v99_reading_id": card["reading_id"],
            "v99_source_gdts": card["source_gdts"], "v99_card_decision": card["v99_audit_decision"],
            "v99_evidence_class": card["v99_evidence_class"],
            "v99_unconditional_global_export_allowed": card["unconditional_global_export_allowed"],
            "selected_whole_default_de": spec["selected_default_de"],
            "new_gdt779_default_de": spec["selected_default_de"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "card_class": spec["card_class"],
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "scope_status": SCOPE, "semantic_change_class": "FALLBACK_REPLACEMENT",
            "fallback_replacement": "1", "display_changed": "1",
            "inherited_consumed_token_ids": "NONE", "gdt779_consumed_token_id": token_id,
            "same_row_inherited_consumption_takeover": "0", "new_unique_consumption": "1",
            "cross_row_consumption_collision": "0", "selection_rule": SELECTION_RULE,
            "selection_uses_occurrence_id": "0", "selection_uses_semantics": "0",
            "exact_complete_whole_only": "1", "default_is_translation": "0",
            "confirmed_lexeme": "0", "confirmed_plaintext": "0", "component_export_credit": "0",
        }
        atlas_ok &= all(row[key] == value for key, value in expected_pairs.items())
        atlas_ok &= int(row["line_token_count"]) == len(source["written_line_eva"].split())
        atlas_ok &= row["register_id"] == f"{source['section']}|{source['language']}|{source['hand']}"
    record("atlas_reconstructs_pure_selection", atlas_ok)

    equal("exclusion_rows", len(exclusions), 49)
    equal("exclusion_parent_order", [row["target_occurrence_id"] for row in exclusions],
          [row["target_occurrence_id"] for row in nonexact])
    exclusion_ok = True
    for row, source in zip(exclusions, nonexact):
        card = v99[source["right_surface"]][0]
        exclusion_ok &= all((
            row["target_occurrence_id"] == source["target_occurrence_id"],
            row["page"] == source["page"], row["physical_folio"] == source["physical_folio"],
            row["locus"] == source["locus"], row["ol_ordinal"] == source["ordinal"],
            row["right_ordinal"] == source["right_ordinal"], row["right_surface"] == source["right_surface"],
            row["right_reader_exact"] == "0", row["v99_reading_id"] == card["reading_id"],
            row["final_44_deck_member"] == str(int(source["right_surface"] in deck)),
            row["exclusion_reason"] == "V99R7_COMPLETE_WORD_CARD_MATCH_BUT_RIGHT_READER_NONEXACT",
            row["selection_rule"] == SELECTION_RULE, row["selection_uses_occurrence_id"] == "0",
            row["default_is_translation"] == "0", row["confirmed_lexeme"] == "0",
            row["component_export_credit"] == "0",
        ))
    record("all_and_only_nonexact_raw_candidates_excluded", exclusion_ok)

    # Renderer and token ownership.
    equal("renderer_rows", len(renderer), 376)
    equal("renderer_parent_order", [row["target_occurrence_id"] for row in renderer],
          [row["target_occurrence_id"] for row in parent])
    renderer_by_id = unique_by(renderer, "target_occurrence_id", "renderer")
    record("renderer_copies_parent_columns", all(
        all(new[field] == old[field] for field in (*CORE_FIELDS, *PARENT_STATE_FIELDS))
        for old, new in zip(parent, renderer)
    ))
    selected_ids = set(atlas_by_id)
    selected_renderer_ok = True
    inherited_renderer_ok = True
    for source, row in zip(parent, renderer):
        if source["target_occurrence_id"] in selected_ids:
            span = atlas_by_id[source["target_occurrence_id"]]
            selected_renderer_ok &= all((
                row["gdt779_branch"] == SELECTED_BRANCH,
                row["gdt779_default_de"] == span["new_gdt779_default_de"],
                row["gdt779_renderer_contextual"] == "1", row["gdt779_span_id"] == span["span_id"],
                row["gdt779_exact_whole"] == span["right_surface"], row["gdt779_confidence"] == span["confidence"],
                row["gdt779_consumed_token_count"] == "1",
                row["gdt779_consumed_token_ids"] == span["gdt779_consumed_token_id"],
                row["gdt779_fallback_replacement"] == "1", row["gdt779_display_changed"] == "1",
                row["gdt779_new_unique_consumption"] == "1",
                row["gdt779_positive_evidence"] == span["positive_evidence"],
                row["gdt779_counterevidence"] == span["counterevidence"],
                row["gdt779_dispatch_rule"] == SELECTION_RULE, row["gdt779_scope_status"] == SCOPE,
                row["gdt779_card_class"] == span["card_class"], row["gdt779_default_is_translation"] == "0",
                row["gdt779_confirmed_lexeme"] == "0", row["gdt779_confirmed_plaintext"] == "0",
                row["gdt779_component_export_credit"] == "0",
            ))
        else:
            inherited_renderer_ok &= all((
                row["gdt779_branch"] == "INHERITED_GDT778",
                row["gdt779_default_de"] == source["gdt778_default_de"],
                row["gdt779_renderer_contextual"] == source["gdt778_renderer_contextual"],
                row["gdt779_span_id"] == source["gdt778_span_id"],
                row["gdt779_exact_whole"] == source["gdt778_exact_whole"],
                row["gdt779_confidence"] == source["gdt778_confidence"],
                row["gdt779_consumed_token_count"] == source["gdt778_consumed_token_count"],
                row["gdt779_consumed_token_ids"] == source["gdt778_consumed_token_ids"],
                row["gdt779_fallback_replacement"] == "0", row["gdt779_display_changed"] == "0",
                row["gdt779_new_unique_consumption"] == "0",
                row["gdt779_positive_evidence"] == "INHERITED_GDT778",
                row["gdt779_counterevidence"] == "INHERITED_GDT778",
                row["gdt779_dispatch_rule"] == "INHERITED_GDT778",
                row["gdt779_scope_status"] == "INHERITED_GDT778",
                row["gdt779_card_class"] == "INHERITED_GDT778",
                row["gdt779_default_is_translation"] == "0", row["gdt779_confirmed_lexeme"] == "0",
                row["gdt779_confirmed_plaintext"] == "0", row["gdt779_component_export_credit"] == "0",
            ))
    record("selected_renderer_rows_reconstructed", selected_renderer_ok)
    record("unselected_renderer_rows_inherited", inherited_renderer_ok)
    equal("new_contextual_count", sum(int(row["gdt779_renderer_contextual"]) for row in renderer), 245)
    equal("new_fallback_count", sum(row["gdt779_renderer_contextual"] == "0" for row in renderer), 131)
    equal("renderer_fallback_replacements", sum(int(row["gdt779_fallback_replacement"]) for row in renderer), 50)
    equal("renderer_display_changes", sum(int(row["gdt779_display_changed"]) for row in renderer), 50)

    parent_token_ids: list[str] = []
    renderer_token_ids: list[str] = []
    consumption_count_matches = True
    for row in parent:
        ids = split_token_ids(row["gdt778_consumed_token_ids"])
        consumption_count_matches &= len(ids) == int(row["gdt778_consumed_token_count"])
        parent_token_ids.extend(ids)
    for row in renderer:
        ids = split_token_ids(row["gdt779_consumed_token_ids"])
        consumption_count_matches &= len(ids) == int(row["gdt779_consumed_token_count"])
        renderer_token_ids.extend(ids)
    new_token_ids = [row["gdt779_consumed_token_id"] for row in atlas]
    record("consumed_count_fields_match_ids", consumption_count_matches)
    equal("parent_unique_consumption", len(set(parent_token_ids)), 155)
    equal("parent_has_no_token_collision", len(parent_token_ids), len(set(parent_token_ids)))
    equal("selected_unique_consumption", len(set(new_token_ids)), 50)
    equal("same_row_or_cross_row_takeovers", set(parent_token_ids) & set(new_token_ids), set())
    equal("new_total_unique_consumption", len(set(renderer_token_ids)), 205)
    equal("renderer_has_no_token_collision", len(renderer_token_ids), len(set(renderer_token_ids)))

    # Full raw-76 and final-44 precedence shadow.
    full_shadow_sources = [row for row in parent if row["right_surface"] in raw_forms]
    equal("shadow_rows", len(shadow), 179)
    equal("shadow_parent_order", [row["target_occurrence_id"] for row in shadow],
          [row["target_occurrence_id"] for row in full_shadow_sources])
    equal("shadow_parent_fallbacks", sum(row["gdt778_renderer_contextual"] == "0" for row in full_shadow_sources), 99)
    equal("shadow_parent_contextual", sum(row["gdt778_renderer_contextual"] == "1" for row in full_shadow_sources), 80)
    equal("shadow_reader_exact", sum(row["right_reader_exact"] == "1" for row in full_shadow_sources), 127)
    exact_fallback_shadow = [row for row in full_shadow_sources if row["right_reader_exact"] == "1" and row["gdt778_renderer_contextual"] == "0"]
    protected_exact_shadow = [row for row in full_shadow_sources if row["right_reader_exact"] == "1" and row["gdt778_renderer_contextual"] == "1"]
    equal("shadow_selected_exact_fallbacks", len(exact_fallback_shadow), 50)
    equal("shadow_protected_exact_contextual", len(protected_exact_shadow), 77)
    final_shadow_sources = [row for row in full_shadow_sources if row["right_surface"] in deck]
    equal("final44_raw_parent_matches", len(final_shadow_sources), 68)
    equal("final44_exact_parent_matches", sum(row["right_reader_exact"] == "1" for row in final_shadow_sources), 63)
    final_protected_exact = [row for row in final_shadow_sources if row["right_reader_exact"] == "1" and row["gdt778_renderer_contextual"] == "1"]
    equal("final44_protected_exact_contexts", len(final_protected_exact), 13)
    equal("final44_protected_exact_forms", len({row["right_surface"] for row in final_protected_exact}), 8)
    shadow_ok = True
    for row, source in zip(shadow, full_shadow_sources):
        new = renderer_by_id[source["target_occurrence_id"]]
        disposition = expected_disposition(source, deck)
        semantic_same = (new["gdt779_default_de"] == source["gdt778_default_de"] and
                         new["gdt779_renderer_contextual"] == source["gdt778_renderer_contextual"])
        consumption_same = (new["gdt779_consumed_token_count"] == source["gdt778_consumed_token_count"] and
                            new["gdt779_consumed_token_ids"] == source["gdt778_consumed_token_ids"])
        state_same = semantic_same and consumption_same and all((
            new["gdt779_span_id"] == source["gdt778_span_id"],
            new["gdt779_exact_whole"] == source["gdt778_exact_whole"],
            new["gdt779_confidence"] == source["gdt778_confidence"],
        ))
        expected_pairs = {
            "target_occurrence_id": source["target_occurrence_id"], "page": source["page"],
            "physical_folio": source["physical_folio"], "locus": source["locus"],
            "ol_ordinal": source["ordinal"], "right_ordinal": source["right_ordinal"],
            "right_surface": source["right_surface"], "right_reader_exact": source["right_reader_exact"],
            "parent_gdt778_fallback": str(int(source["gdt778_renderer_contextual"] == "0")),
            "parent_gdt778_contextual": source["gdt778_renderer_contextual"], "raw_76_deck_member": "1",
            "final_44_deck_member": str(int(source["right_surface"] in deck)),
            "deck_phase": "FINAL_44_FROZEN_DECK" if source["right_surface"] in deck else "RAW_76_SCREEN_ONLY",
            "precedence_disposition": disposition, "old_gdt778_branch": source["gdt778_branch"],
            "old_gdt778_default_de": source["gdt778_default_de"],
            "old_gdt778_consumed_token_count": source["gdt778_consumed_token_count"],
            "old_gdt778_consumed_token_ids": source["gdt778_consumed_token_ids"],
            "new_gdt779_branch": new["gdt779_branch"], "new_gdt779_default_de": new["gdt779_default_de"],
            "new_gdt779_contextual": new["gdt779_renderer_contextual"],
            "new_gdt779_consumed_token_count": new["gdt779_consumed_token_count"],
            "new_gdt779_consumed_token_ids": new["gdt779_consumed_token_ids"],
            "semantic_state_unchanged": str(int(semantic_same)),
            "consumption_state_unchanged": str(int(consumption_same)),
            "represented_parent_state_unchanged": str(int(state_same)),
            "selected_by_gdt779": str(int(disposition == "SELECTED_GDT779_FALLBACK")),
            "component_export_credit": "0",
        }
        shadow_ok &= all(row[key] == value for key, value in expected_pairs.items())
    record("precedence_shadow_reconstructed", shadow_ok)
    record("all_contextual_shadow_rows_unchanged", all(
        row["represented_parent_state_unchanged"] == "1"
        for row in shadow if row["parent_gdt778_contextual"] == "1"
    ))
    equal("shadow_disposition_partition", Counter(row["precedence_disposition"] for row in shadow), Counter({
        "SELECTED_GDT779_FALLBACK": 50,
        "PROTECTED_EXACT_CONTEXTUAL": 13,
        "EXCLUDED_NONEXACT_FINAL_FORM": 4,
        "PROTECTED_NONEXACT_CONTEXTUAL": 1,
        "PROTECTED_EXACT_CONTEXTUAL_RAW_ONLY_FORM": 64,
        "EXCLUDED_NONEXACT_RAW_ONLY_FORM": 45,
        "PROTECTED_NONEXACT_CONTEXTUAL_RAW_ONLY_FORM": 2,
    }))

    # Dictionary counts and complete-whole semantics.
    equal("dictionary_rows", len(dictionary), 44)
    dictionary_by_form = unique_by(dictionary, "entry", "dictionary")
    equal("dictionary_forms", frozenset(dictionary_by_form), deck)
    dictionary_ok = True
    for form, row in dictionary_by_form.items():
        spec = specs[form]
        card = v99[form][0]
        selected_local = [source for source in selected if source["right_surface"] == form]
        final_local = [source for source in parent if source["right_surface"] == form]
        exclusions_local = [source for source in nonexact if source["right_surface"] == form]
        protected_local = [source for source in final_local if source["right_reader_exact"] == "1" and source["gdt778_renderer_contextual"] == "1"]
        expected_pairs = {
            "preferred_gdt779_default_de": spec["selected_default_de"], "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"], "confidence": spec["confidence"],
            "card_class": spec["card_class"], "v99_reading_id": card["reading_id"],
            "v99_unconditional_global_export_allowed": card["unconditional_global_export_allowed"],
            "selected_exact_fallback_contexts": str(len(selected_local)),
            "final_form_raw_parent_contexts": str(len(final_local)),
            "final_form_exact_parent_contexts": str(sum(source["right_reader_exact"] == "1" for source in final_local)),
            "protected_exact_contextual_contexts": str(len(protected_local)),
            "nonexact_fallback_exclusions": str(len(exclusions_local)),
            "rendered_displays_de": spec["selected_default_de"], "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"],
            "scope": "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT",
            "replaceable": "1", "default_is_translation": "0", "confirmed_lexeme": "0",
            "confirmed_plaintext": "0", "component_export_credit": "0",
        }
        dictionary_ok &= all(row[key] == value for key, value in expected_pairs.items())
    record("dictionary_reconstructed", dictionary_ok)
    equal("dictionary_selected_context_sum", sum(int(row["selected_exact_fallback_contexts"]) for row in dictionary), 50)
    equal("dictionary_raw_parent_sum", sum(int(row["final_form_raw_parent_contexts"]) for row in dictionary), 68)
    equal("dictionary_exact_parent_sum", sum(int(row["final_form_exact_parent_contexts"]) for row in dictionary), 63)
    equal("dictionary_protected_exact_sum", sum(int(row["protected_exact_contextual_contexts"]) for row in dictionary), 13)
    equal("dictionary_nonexact_final_sum", sum(int(row["nonexact_fallback_exclusions"]) for row in dictionary), 4)

    # Independent provenance reconstruction from locked upstream sources.
    g737 = unique_by(read_tsv(G737_PATH), "body", "GDT737 body")
    g738 = unique_by(read_tsv(G738_PATH), "body", "GDT738 body")
    g749 = unique_by(read_tsv(G749_PATH), "target_surface", "GDT749 target")
    g754 = unique_by(read_tsv(G754_PATH), "surface", "GDT754 surface")
    g755 = unique_by(read_tsv(G755_GLOSS_PATH), "surface", "GDT755 surface")
    g755_occ = [row for row in read_tsv(G755_OCC_PATH) if row["surface"] == "qockhey"]
    g758 = unique_by(read_tsv(G758_PATH), "surface", "GDT758 surface")
    equal("gdt737_body_registry_rows", len(g737), 120)
    equal("gdt738_body_registry_rows", len(g738), 120)
    equal("qokaiin_outside_status", g749["qokaiin"]["outside_role_status"], "K1_OPEN_OR_BASELINE_LIKE")
    equal("qockhey_gdt754_literal_prose_spoken", g754["qockhey"]["source_literal_prose_spoken_after_gdt754"], "0")
    equal("qockhey_gdt754_disposition", g754["qockhey"]["renderer_disposition"], "COMPOSITION_AXES_HYPOTHESIS_ONLY")
    equal("qockhey_gdt755_candidate", g755["qockhey"]["gdt755_working_candidate_de"], "mische")
    equal("qockhey_gdt755_confidence", g755["qockhey"]["working_confidence"], "C0_FORCED_DEFAULT")
    equal("qockhey_gdt755_exact_occurrences", len(g755_occ), 12)
    equal("qockhey_gdt755_complete_fields", sum(int(row["boundary_complete"]) for row in g755_occ), 7)
    equal("oky_later_whole_default", g758["oky"]["gdt758_renderer_value_de"], "erste Wärmestufe")
    equal("sheol_later_whole_default", g758["sheol"]["gdt758_renderer_value_de"], "eingeweicht/feucht")

    equal("provenance_rows", len(provenance), 44)
    provenance_by_form = unique_by(provenance, "right_surface", "provenance")
    equal("provenance_forms", frozenset(provenance_by_form), deck)
    old_patient_set = frozenset(
        form for form in deck if ACTIVE_BANNED_RE.search(v99[form][0]["working_meaning_de"]) is not None
    )
    equal("old_literal_patient_set_recomputed", old_patient_set, SANITIZED)
    provenance_ok = True
    for form, row in provenance_by_form.items():
        spec = specs[form]
        card = v99[form][0]
        r737, r738, r749, r758 = g737.get(form), g738.get(form), g749.get(form), g758.get(form)
        is_qockhey = form == "qockhey"
        expected_pairs = {
            "card_class": spec["card_class"], "selected_default_de": spec["selected_default_de"],
            "confidence": spec["confidence"], "v99_reading_id": card["reading_id"],
            "v99_old_working_meaning_de_provenance_only": card["working_meaning_de"],
            "v99_old_spoken_default_de_provenance_only": card["v99r7_spoken_default_de"],
            "v99_source_gdts": card["source_gdts"], "v99_positive_evidence_de": card["positive_evidence_de"],
            "v99_counterevidence_de": card["counterevidence_de"],
            "v99_unconditional_global_export_allowed": card["unconditional_global_export_allowed"],
            "v99_candidate_composition": card["gdt734_candidate_composition"],
            "old_literal_patient_detected": str(int(form in old_patient_set)),
            "patient_sanitization_applied": str(int(form in SANITIZED)),
            "gdt737_family": r737["family"] if r737 else "NONE",
            "gdt737_candidate_de": r737["concrete_body_role_de"] if r737 else "NONE",
            "gdt737_renderer_license": r737["renderer_license"] if r737 else "0",
            "gdt738_discovery_decision": r738["discovery_decision"] if r738 else "NONE",
            "gdt738_w23_decision": r738["w23_decision"] if r738 else "NONE",
            "gdt738_body_renderer_license": r738["body_renderer_license"] if r738 else "0",
            "gdt749_outside_role_status": r749["outside_role_status"] if r749 else "NONE",
            "gdt758_later_whole_default_de": r758["gdt758_renderer_value_de"] if r758 else "NONE",
            "qockhey_gdt754_source_composition_quarantined": str(int(is_qockhey)),
            "qockhey_gdt754_current_source_prose_de_provenance_only": g754[form]["current_source_prose_de"] if is_qockhey else "NONE",
            "qockhey_gdt754_source_composition": g754[form]["source_composition"] if is_qockhey else "NONE",
            "qockhey_gdt755_complete_whole_candidate_de": g755[form]["gdt755_working_candidate_de"] if is_qockhey else "NONE",
            "qockhey_gdt755_confidence": g755[form]["working_confidence"] if is_qockhey else "NONE",
            "qockhey_gdt755_exact_occurrences": str(len(g755_occ) if is_qockhey else 0),
            "qockhey_gdt755_boundary_complete_occurrences": str(sum(int(source["boundary_complete"]) for source in g755_occ) if is_qockhey else 0),
            "selected_exact_fallback_occurrences": str(sum(source["right_surface"] == form for source in selected)),
            "exact_complete_whole_only": "1", "old_prose_used_as_active_default": "0",
            "default_is_translation": "0", "confirmed_lexeme": "0", "confirmed_plaintext": "0",
            "component_export_credit": "0",
        }
        provenance_ok &= all(row[key] == value for key, value in expected_pairs.items())
    record("provenance_audit_reconstructed", provenance_ok)
    equal("globally_exportable_card_count", sum(int(v99[form][0]["unconditional_global_export_allowed"]) for form in deck), 41)
    equal("non_global_card_set", frozenset(form for form in deck if v99[form][0]["unconditional_global_export_allowed"] == "0"), NEW_SCOPES)
    equal("composition_provenance_set", frozenset(form for form in deck if v99[form][0]["gdt734_candidate_composition"] != "NONE"), COMPOSED)
    record("active_selected_defaults_are_patient_free", all(ACTIVE_BANNED_RE.search(row["gdt779_default_de"]) is None for row in renderer))
    record("qockhey_old_prose_not_active", all(
        row["gdt779_default_de"] != g754["qockhey"]["current_source_prose_de"]
        for row in renderer if row["gdt779_exact_whole"] == "qockhey"
    ))

    leak_files = [ART / name for name in REPLAY_FILES if name != "GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv"]
    leak_files.append(EXP / "REPORT.md")
    record("retired_patient_strings_confined_to_provenance", all(
        ACTIVE_BANNED_RE.search(path.read_text(encoding="utf-8")) is None for path in leak_files
    ))

    # Residual census.
    residual_sources = [row for row in renderer if row["gdt779_renderer_contextual"] == "0"]
    equal("residual_rows", len(residual), 131)
    equal("residual_parent_order", [row["target_occurrence_id"] for row in residual],
          [row["target_occurrence_id"] for row in residual_sources])
    residual_ok = True
    expected_residual_reasons: list[str] = []
    for row, source in zip(residual, residual_sources):
        surface = source["right_surface"]
        if surface == "NONE" or source["right_ordinal"] == "0":
            reason = "LINE_FINAL_NO_RIGHT"
        elif surface not in v99:
            reason = "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT" if source["right_reader_exact"] == "1" else "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT"
        elif surface in deck:
            reason = "V99_CARD_NONEXACT_FINAL44"
        else:
            reason = "V99_CARD_NONEXACT_RAW_ONLY"
        expected_residual_reasons.append(reason)
        expected_pairs = {
            "target_occurrence_id": source["target_occurrence_id"], "page": source["page"],
            "physical_folio": source["physical_folio"], "locus": source["locus"],
            "ol_ordinal": source["ordinal"], "right_ordinal": source["right_ordinal"],
            "right_surface": surface, "right_reader_exact": source["right_reader_exact"],
            "residual_reason": reason, "gdt779_default_de": source["gdt779_default_de"],
            "v99_complete_card_present": str(int(surface in v99)),
            "final_44_deck_member": str(int(surface in deck)), "component_export_credit": "0",
        }
        residual_ok &= all(row[key] == value for key, value in expected_pairs.items())
    record("residual_census_reconstructed", residual_ok)
    equal("residual_reason_partition", Counter(expected_residual_reasons), Counter({
        "LINE_FINAL_NO_RIGHT": 37,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 25,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
        "V99_CARD_NONEXACT_RAW_ONLY": 45,
        "V99_CARD_NONEXACT_FINAL44": 4,
    }))

    # Grouped passage patches, including the one double-target locus.
    old_by_position = {(row["locus"], int(row["ordinal"])): row for row in parent}
    new_by_position = {(row["locus"], int(row["ordinal"])): row for row in renderer}
    atlas_by_locus: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in atlas:
        atlas_by_locus[row["locus"]].append(row)
    equal("passage_rows", len(passages), 49)
    equal("passage_locus_order", [row["locus"] for row in passages], sorted(atlas_by_locus))
    passage_ok = True
    for row in passages:
        local = sorted(atlas_by_locus[row["locus"]], key=lambda source: int(source["ol_ordinal"]))
        written = local[0]["written_line_eva"]
        old_patch = render_line(row["locus"], written, old_by_position, "gdt778")
        new_patch = render_line(row["locus"], written, new_by_position, "gdt779")
        expected_pairs = {
            "span_ids": "|".join(source["span_id"] for source in local),
            "target_occurrence_ids": "|".join(source["target_occurrence_id"] for source in local),
            "page": local[0]["page"], "physical_folio": local[0]["physical_folio"],
            "target_count": str(len(local)), "right_surfaces": "|".join(source["right_surface"] for source in local),
            "right_token_ids": "|".join(source["gdt779_consumed_token_id"] for source in local),
            "selected_whole_defaults_de": " || ".join(source["selected_whole_default_de"] for source in local),
            "written_line_eva": written, "inherited_gdt778_patch_de": old_patch,
            "gdt779_practical_patch_de": new_patch,
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": "0", "confirmed_plaintext": "0", "component_export_credit": "0",
        }
        passage_ok &= all(row[key] == value for key, value in expected_pairs.items())
        passage_ok &= old_patch != new_patch
    record("passage_patches_reconstructed", passage_ok)
    equal("passage_target_sum", sum(int(row["target_count"]) for row in passages), 50)
    equal("double_passage", [(row["locus"], row["target_count"], row["right_surfaces"])
                              for row in passages if int(row["target_count"]) > 1],
          [("f75r.26", "2", "sheol|qoly")])

    # Relation packet/crosswalk plus the executable GDT388 intake gate.
    equal("relation_packet_rows", len(packet), 50)
    equal("relation_crosswalk_rows", len(crosswalk), 50)
    packet_by_edge = unique_by(packet, "edge_id", "packet edge")
    crosswalk_by_edge = unique_by(crosswalk, "edge_id", "crosswalk edge")
    packet_ok = True
    for number, span in enumerate(atlas, 1):
        edge_id = f"G779-E{number:03d}"
        edge = packet_by_edge[edge_id]
        walk = crosswalk_by_edge[edge_id]
        packet_ok &= all((
            edge["page"] == span["page"], edge["physical_folio"] == span["physical_folio"],
            edge["diagram_unit_id"] == f"LINE:{span['locus']}",
            edge["pivot_locus"] == f"{span['locus']}@{span['ol_ordinal']}",
            edge["target_locus"] == f"{span['locus']}@{span['right_ordinal']}",
            edge["relation_type"] == "NEXT_TOKEN", edge["direction_basis"] == "TRANSCRIPTION_ORDER_ONLY",
            edge["ownership_basis"] == "NONVISUAL_TEXT_ADJACENCY", edge["geometry_only_selection"] == "FALSE",
            edge["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
            edge["formal_access_state"] == "SEALED_NOT_ACCESSED",
            walk["span_id"] == span["span_id"], walk["target_occurrence_id"] == span["target_occurrence_id"],
            walk["right_surface"] == span["right_surface"], walk["written_span_eva"] == span["written_span_eva"],
            walk["selection_rule"] == SELECTION_RULE, walk["score_eligible"] == "0",
            walk["component_export_credit"] == "0",
        ))
    record("relation_packet_and_crosswalk_reconstructed", packet_ok)
    gate_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / "GDT779_GDT388_RELATION_PACKET.tsv")],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    equal("edge_packet_gate_exit", gate_run.returncode, 0)
    gate = json.loads(gate_run.stdout)
    expected_gate = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 50,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
        "holdout_edges": 0, "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    equal("edge_packet_gate_result", gate, expected_gate)
    equal("edge_packet_intake_artifact", read_json(ART / "RELATION_PACKET_INTAKE.json"), expected_gate)

    # Compact result is checked against independently recomputed quantities.
    equal("result_status", result["status"], "PASS__50_EXACT_FALLBACK_WHOLES__44_FORMS__49_LOCI__245_CONTEXTUAL__131_FALLBACKS__205_CONSUMED__6_SANITIZATIONS__NO_COMPONENT_EXPORT")
    equal("result_cohort", result["cohort"], {
        "renderer_rows": 376, "raw_v99r7_candidates": 99, "raw_candidate_forms": 76,
        "reader_exact_selected_spans": 50, "selected_forms": 44, "exactness_exclusions": 49,
        "excluded_forms": 36, "loci": 49, "page_labels": 33, "physical_folios": 24,
    })
    equal("result_precedence_shadow", result["precedence_shadow"], {
        "raw_76_full_parent_matches": 179, "parent_fallback_matches": 99,
        "parent_contextual_matches": 80, "reader_exact_matches": 127,
        "selected_exact_fallback_matches": 50, "protected_exact_contextual_matches": 77,
        "final_44_raw_parent_matches": 68, "final_44_exact_parent_matches": 63,
        "final_44_protected_exact_contextual_matches": 13,
    })
    equal("result_renderer", result["renderer"], {
        "gdt778_contextual": 195, "gdt778_fallbacks": 181,
        "gdt779_contextual": 245, "gdt779_fallbacks": 131,
    })
    equal("result_consumption", result["consumption"], {
        "gdt778_unique_right_tokens": 155, "gdt779_selected_right_tokens": 50,
        "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 50,
        "total_unique_right_tokens": 205, "cross_row_collisions": 0,
    })
    equal("result_card_partition", result["card_partition"], dict(CLASS_COUNTS))
    equal("result_residual_partition", result["residual_partition"], {
        "line_final_no_right": 37, "no_card_reader_exact": 25,
        "no_card_reader_nonexact": 20, "v99_card_nonexact": 49,
    })
    equal("result_relation_packet", result["relation_packet"], expected_gate)
    equal("result_zero_claim_exports", {
        key: result[key] for key in (
            "component_exports", "confirmed_lexemes", "confirmed_plaintext_clauses",
            "new_pages", "new_images", "new_ocr", "new_transcriptions", "sealed_pages_accessed",
        )
    }, {key: 0 for key in (
        "component_exports", "confirmed_lexemes", "confirmed_plaintext_clauses",
        "new_pages", "new_images", "new_ocr", "new_transcriptions", "sealed_pages_accessed",
    )})
    equal("result_source_hygiene", result["source_hygiene"], {
        "patient_sanitizations": 6, "new_exact_ol_scopes": 3,
        "composition_derived_complete_wholes": 2,
        "qockhey_later_complete_whole_replacements": 1,
        "globally_exportable_v99_cards": 41,
        "old_literal_patient_leaks_outside_provenance": 0,
        "qockhey_source_composed_prose_used": False,
        "chol_confirmations_changed": 0,
        "ols_rejected_legacy_process_reading_restored": False,
    })
    equal("result_changes", result["changes"], {
        "actual_display_changes": 50, "fallback_replacements": 50, "passage_patches": 49,
    })
    equal("result_dictionary_and_residual_rows", (result["dictionary_rows"], result["residual_fallback_rows"]), (44, 131))
    equal("result_source_locks", result["source_locks"], 11)
    equal("result_inherited_guard", result["inherited_guard"], parent_result["inherited_guard"])

    # Isolated deterministic replay. The builder is used only here, after the
    # independent logical reconstruction above has already passed.
    replay_hashes: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="gdt779-alt-replay-") as temporary:
        temp = Path(temporary)
        temp_art = temp / "artifacts"
        temp_report = temp / "REPORT.md"
        replay = subprocess.run(
            [sys.executable, "-B", str(RUNNER_PATH), "--artifacts-dir", str(temp_art),
             "--report-path", str(temp_report)],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        equal("deterministic_replay_exit", replay.returncode, 0)
        equal("deterministic_replay_artifact_names", {path.name for path in temp_art.iterdir()}, set(REPLAY_FILES))
        for name in REPLAY_FILES:
            canonical = ART / name
            replayed = temp_art / name
            equal(f"byte_replay::{name}", replayed.read_bytes(), canonical.read_bytes())
            replay_hashes[name] = sha256(canonical)
        equal("byte_replay::REPORT.md", temp_report.read_bytes(), (EXP / "REPORT.md").read_bytes())
        replay_hashes["REPORT.md"] = sha256(EXP / "REPORT.md")

    return {
        "experiment_id": "GDT779",
        "validator": "INDEPENDENT_ALTERNATE_VALIDATOR",
        "status": "PASS__INDEPENDENT_ALT_VALIDATION__PURE_44_DECK_RULE__50_SPANS__49_LOCI__205_CONSUMED__BYTE_REPLAY",
        "checks_total": len(CHECKS),
        "checks_passed": sum(bool(check["passed"]) for check in CHECKS),
        "failures": [check for check in CHECKS if not check["passed"]],
        "selection_recomputed": {
            "parent_rows": 376, "parent_fallbacks": 181, "raw_card_fallbacks": 99,
            "raw_forms": 76, "selected_spans": 50, "selected_forms": 44,
            "loci": 49, "page_labels": 33, "physical_folios": 24,
            "nonexact_exclusions": 49, "excluded_forms": 36,
            "selector_inputs": ["gdt778_renderer_contextual", "right_reader_exact", "right_surface_in_fixed_44_deck"],
            "selector_forbidden_inputs": ["occurrence_id", "page", "folio", "locus", "frequency", "neighbours", "substring", "semantics"],
        },
        "precedence_recomputed": {
            "raw76_full_parent": 179, "raw76_exact": 127,
            "selected_exact_fallback": 50, "protected_exact_contextual": 77,
            "final44_raw": 68, "final44_exact": 63,
            "final44_protected_exact_contextual": 13,
        },
        "renderer_recomputed": {
            "contextual_before": 195, "contextual_after": 245,
            "fallback_before": 181, "fallback_after": 131,
            "consumption_before": 155, "consumption_after": 205,
            "new_unique_consumptions": 50, "collisions": 0,
        },
        "provenance_recomputed": {
            "card_partition": dict(sorted(CLASS_COUNTS.items())),
            "retired_patient_sanitizations": 6, "new_exact_ol_scopes": 3,
            "composition_derived_wholes_no_component_export": 2,
            "qockhey_later_whole_replacement": 1,
            "active_patient_leaks": 0, "component_exports": 0,
        },
        "relation_packet_gate": gate,
        "deterministic_replay": {
            "files_compared": len(replay_hashes), "byte_identical": True,
            "sha256": dict(sorted(replay_hashes.items())),
        },
        "sealed_scope": {
            "new_pages": 0, "new_images": 0, "new_ocr": 0,
            "new_transcriptions": 0, "f84_accessed": False, "f84r_accessed": False,
        },
        "checks": CHECKS,
    }


def write_result(payload: Mapping[str, object]) -> None:
    ALT_RESULT.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    try:
        payload = validate()
    except Exception as exc:
        payload = {
            "experiment_id": "GDT779",
            "validator": "INDEPENDENT_ALTERNATE_VALIDATOR",
            "status": "FAIL__INDEPENDENT_ALT_VALIDATION",
            "checks_total": len(CHECKS),
            "checks_passed": sum(bool(check["passed"]) for check in CHECKS),
            "failures": [*([check for check in CHECKS if not check["passed"]]), {"exception": str(exc)}],
            "checks": CHECKS,
        }
        write_result(payload)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
        return 1
    write_result(payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
