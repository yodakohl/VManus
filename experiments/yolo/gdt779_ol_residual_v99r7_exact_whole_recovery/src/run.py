#!/usr/bin/env python3
"""Recover residual exact complete-word cards after ``ol``.

Selection is deliberately narrow: a row must still be a GDT778 fallback, its
complete right surface must have a frozen V99R7 card, and the right reader must
be exact. Occurrence identifiers and semantic content are output only; neither
is allowed to select a row.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
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
EXP = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SPECS_PATH = SRC / "RESIDUAL_V99R7_EXACT_WHOLE_SPECS.tsv"
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

ACTIVE_BANNED_RE = re.compile(r"(?i)(pulver|samen|wurzel|holz|droge|filtrat|abgeseih)")
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
SELECTION_RULE = "GDT778_RENDERER_CONTEXTUAL_0_AND_COMPLETE_RIGHT_SURFACE_V99R7_CARD_MATCH_AND_RIGHT_READER_EXACT_1"
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    return int(value) if isinstance(value, bool) else value


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    material = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in material:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_locks() -> int:
    rows = read_tsv(SRC / "SOURCE_LOCK.tsv")
    assert rows, "empty SOURCE_LOCK"
    seen: set[str] = set()
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert str(relative) not in seen, f"duplicate source lock: {relative}"
        seen.add(str(relative))
        source = ROOT / relative
        assert source.is_file(), source
        assert sha256(source) == row["expected_sha256"], f"source changed: {relative}"
    return len(rows)


def one_by(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for source in rows:
        value = source[key]
        assert value not in output, (key, value)
        output[value] = dict(source)
    return output


def validate_specs(rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, str]]:
    required = {
        "right_surface", "selected_default_de", "alternate_1_de", "alternate_2_de", "confidence",
        "card_class", "scope_status", "positive_evidence", "counterevidence",
    }
    assert len(rows) == 44 and rows and required <= set(rows[0])
    specs = one_by(rows, "right_surface")
    assert Counter(row["card_class"] for row in rows) == CLASS_COUNTS
    class_sets = {
        name: {row["right_surface"] for row in rows if row["card_class"] == name}
        for name in CLASS_COUNTS
    }
    assert class_sets["RETIRED_PATIENT_SANITIZATION"] == SANITIZED
    assert class_sets["NEW_EXACT_OL_SCOPE"] == NEW_SCOPES
    assert class_sets["COMPOSITION_DERIVED_WHOLE__NO_COMPONENT_EXPORT"] == COMPOSED
    assert class_sets["GDT755_LATER_COMPLETE_WHOLE_REPLACEMENT"] == QOCKHEY
    for form, row in specs.items():
        assert form and " " not in form
        assert row["confidence"] in {"C0", "C1", "C2"}
        assert row["scope_status"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY"
        values = (row["selected_default_de"], row["alternate_1_de"], row["alternate_2_de"])
        assert all(value and value != "NONE" for value in values)
        assert len(set(values)) == 3
        assert ACTIVE_BANNED_RE.search(" ".join((*values, row["positive_evidence"], row["counterevidence"]))) is None
    assert specs["cheor"]["selected_default_de"] == "trockener Teil"
    assert specs["qockhey"]["selected_default_de"] == "mische"
    assert specs["qockhey"]["confidence"] == "C0"
    return specs


def v99_registry(rows: Sequence[Mapping[str, str]]) -> dict[str, list[dict[str, str]]]:
    assert len(rows) == 1606
    output: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        assert row["surface"] and " " not in row["surface"]
        output[row["surface"]].append(dict(row))
    return output


def select_gdt779_row(gdt778_renderer_contextual: str, right_surface: str,
                      right_reader_exact: str, fixed_complete_surfaces: frozenset[str]) -> bool:
    """Occurrence-free selector over exactly three declared row properties."""
    return (
        gdt778_renderer_contextual == "0"
        and right_reader_exact == "1"
        and right_surface in fixed_complete_surfaces
    )


def inherited_owner_map(base: Sequence[Mapping[str, str]]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for row in base:
        value = row["gdt778_consumed_token_ids"]
        count = int(row["gdt778_consumed_token_count"])
        ids = [] if value == "NONE" else value.split("|")
        assert len(ids) == count
        for token_id in ids:
            assert token_id not in owners, token_id
            owners[token_id] = row["target_occurrence_id"]
    assert len(owners) == 155
    return owners


def build_cohort(base: Sequence[Mapping[str, str]], specs: Mapping[str, Mapping[str, str]],
                 cards: Mapping[str, Sequence[Mapping[str, str]]]) -> tuple[
                     list[dict[str, object]], list[dict[str, object]], set[str], list[dict[str, str]]
                 ]:
    fallback = [row for row in base if row["gdt778_renderer_contextual"] == "0"]
    assert len(fallback) == 181
    raw = [row for row in fallback if row["right_surface"] in cards]
    raw_forms = {row["right_surface"] for row in raw}
    assert len(raw) == 99 and len(raw_forms) == 76
    assert all(len(cards[form]) == 1 for form in raw_forms)
    fixed_complete_surfaces = frozenset(specs)
    exact = [
        row for row in base
        if select_gdt779_row(
            row["gdt778_renderer_contextual"], row["right_surface"],
            row["right_reader_exact"], fixed_complete_surfaces,
        )
    ]
    raw_exact = [row for row in raw if row["right_reader_exact"] == "1"]
    rejected = [row for row in raw if row["right_reader_exact"] != "1"]
    assert exact == raw_exact
    assert len(exact) == 50 and len(rejected) == 49
    assert {row["right_surface"] for row in exact} == fixed_complete_surfaces
    assert len({row["right_surface"] for row in rejected}) == 36

    owners = inherited_owner_map(base)
    spans: list[dict[str, object]] = []
    for number, source in enumerate(exact, 1):
        surface = source["right_surface"]
        spec, card = specs[surface], cards[surface][0]
        ol_ordinal, right_ordinal = int(source["ordinal"]), int(source["right_ordinal"])
        tokens = source["written_line_eva"].split()
        assert source["gdt778_default_de"] == "Ansatz-/Zubereitungsposten"
        assert source["gdt778_consumed_token_count"] == "0"
        assert source["gdt778_consumed_token_ids"] == "NONE"
        assert right_ordinal == ol_ordinal + 1
        assert tokens[ol_ordinal - 1] == "ol" and tokens[right_ordinal - 1] == surface
        token_id = f"{source['locus']}@{right_ordinal}"
        assert token_id not in owners
        spans.append({
            "span_id": f"G779-S{number:03d}", "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "ol_ordinal": ol_ordinal, "right_ordinal": right_ordinal, "line_token_count": len(tokens),
            "right_surface": surface, "written_span_eva": f"ol {surface}",
            "written_line_eva": source["written_line_eva"], "right_reader_exact": 1,
            "old_gdt778_branch": source["gdt778_branch"], "old_gdt778_default_de": source["gdt778_default_de"],
            "old_gdt778_contextual": int(source["gdt778_renderer_contextual"]),
            "v99_reading_id": card["reading_id"], "v99_source_gdts": card["source_gdts"],
            "v99_card_decision": card["v99_audit_decision"], "v99_evidence_class": card["v99_evidence_class"],
            "v99_unconditional_global_export_allowed": int(card["unconditional_global_export_allowed"]),
            "selected_whole_default_de": spec["selected_default_de"],
            "new_gdt779_default_de": spec["selected_default_de"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "card_class": spec["card_class"],
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "scope_status": spec["scope_status"], "semantic_change_class": "FALLBACK_REPLACEMENT",
            "fallback_replacement": 1, "display_changed": 1,
            "inherited_consumed_token_ids": source["gdt778_consumed_token_ids"],
            "gdt779_consumed_token_id": token_id, "same_row_inherited_consumption_takeover": 0,
            "new_unique_consumption": 1, "cross_row_consumption_collision": 0,
            "selection_rule": SELECTION_RULE, "selection_uses_occurrence_id": 0,
            "selection_uses_semantics": 0, "exact_complete_whole_only": 1,
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })

    exclusions: list[dict[str, object]] = []
    for number, source in enumerate(rejected, 1):
        surface, card = source["right_surface"], cards[source["right_surface"]][0]
        exclusions.append({
            "exclusion_id": f"G779-X{number:03d}", "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "ol_ordinal": int(source["ordinal"]), "right_ordinal": int(source["right_ordinal"]),
            "right_surface": surface, "right_reader_exact": int(source["right_reader_exact"]),
            "v99_reading_id": card["reading_id"], "final_44_deck_member": int(surface in specs),
            "exclusion_reason": "V99R7_COMPLETE_WORD_CARD_MATCH_BUT_RIGHT_READER_NONEXACT",
            "selection_rule": SELECTION_RULE, "selection_uses_occurrence_id": 0,
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })

    assert len({row["locus"] for row in spans}) == 49
    assert len({row["page"] for row in spans}) == 33
    assert len({row["physical_folio"] for row in spans}) == 24
    assert Counter(row["locus"] for row in spans)["f75r.26"] == 2
    assert all(value == 1 for value in Counter(row["target_occurrence_id"] for row in spans).values())
    return spans, exclusions, raw_forms, raw


def build_renderer(base: Sequence[Mapping[str, str]], spans: Sequence[Mapping[str, object]]) -> tuple[
    list[dict[str, object]], dict[str, str]
]:
    by_target = {str(row["target_occurrence_id"]): row for row in spans}
    assert len(by_target) == len(spans)
    output: list[dict[str, object]] = []
    for source in base:
        row: dict[str, object] = {field: source[field] for field in (*CORE_FIELDS, *PARENT_STATE_FIELDS)}
        row.update({
            "gdt779_branch": "INHERITED_GDT778", "gdt779_default_de": source["gdt778_default_de"],
            "gdt779_renderer_contextual": int(source["gdt778_renderer_contextual"]),
            "gdt779_span_id": source["gdt778_span_id"], "gdt779_exact_whole": source["gdt778_exact_whole"],
            "gdt779_confidence": source["gdt778_confidence"],
            "gdt779_consumed_token_count": int(source["gdt778_consumed_token_count"]),
            "gdt779_consumed_token_ids": source["gdt778_consumed_token_ids"],
            "gdt779_fallback_replacement": 0, "gdt779_display_changed": 0,
            "gdt779_new_unique_consumption": 0, "gdt779_positive_evidence": "INHERITED_GDT778",
            "gdt779_counterevidence": "INHERITED_GDT778", "gdt779_dispatch_rule": "INHERITED_GDT778",
            "gdt779_scope_status": "INHERITED_GDT778", "gdt779_card_class": "INHERITED_GDT778",
            "gdt779_default_is_translation": 0, "gdt779_confirmed_lexeme": 0,
            "gdt779_confirmed_plaintext": 0, "gdt779_component_export_credit": 0,
        })
        span = by_target.get(source["target_occurrence_id"])
        if span is not None:
            row.update({
                "gdt779_branch": "GDT779_EXACT_OL_PLUS_RESIDUAL_V99R7_WHOLE",
                "gdt779_default_de": span["new_gdt779_default_de"], "gdt779_renderer_contextual": 1,
                "gdt779_span_id": span["span_id"], "gdt779_exact_whole": span["right_surface"],
                "gdt779_confidence": span["confidence"], "gdt779_consumed_token_count": 1,
                "gdt779_consumed_token_ids": span["gdt779_consumed_token_id"],
                "gdt779_fallback_replacement": 1, "gdt779_display_changed": 1,
                "gdt779_new_unique_consumption": 1, "gdt779_positive_evidence": span["positive_evidence"],
                "gdt779_counterevidence": span["counterevidence"], "gdt779_dispatch_rule": SELECTION_RULE,
                "gdt779_scope_status": span["scope_status"], "gdt779_card_class": span["card_class"],
            })
        assert ACTIVE_BANNED_RE.search(str(row["gdt779_default_de"])) is None
        output.append(row)

    owners: dict[str, str] = {}
    for row in output:
        value, count = str(row["gdt779_consumed_token_ids"]), int(row["gdt779_consumed_token_count"])
        ids = [] if value == "NONE" else value.split("|")
        assert len(ids) == count
        for token_id in ids:
            assert token_id not in owners, (token_id, owners.get(token_id), row["target_occurrence_id"])
            owners[token_id] = str(row["target_occurrence_id"])
    assert len(output) == 376
    assert sum(int(row["gdt779_renderer_contextual"]) for row in output) == 245
    assert sum(1 - int(row["gdt779_renderer_contextual"]) for row in output) == 131
    assert sum(int(row["gdt779_fallback_replacement"]) for row in output) == 50
    assert sum(int(row["gdt779_display_changed"]) for row in output) == 50
    assert sum(int(row["gdt779_new_unique_consumption"]) for row in output) == 50
    assert len(owners) == 205
    return output, owners


def build_shadow(base: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, object]], raw_forms: set[str],
                 specs: Mapping[str, Mapping[str, str]]) -> list[dict[str, object]]:
    new_by_target = {str(row["target_occurrence_id"]): row for row in renderer}
    output: list[dict[str, object]] = []
    for number, source in enumerate((row for row in base if row["right_surface"] in raw_forms), 1):
        final = source["right_surface"] in specs
        fallback = source["gdt778_renderer_contextual"] == "0"
        exact = source["right_reader_exact"] == "1"
        if final and exact and fallback:
            disposition = "SELECTED_GDT779_FALLBACK"
        elif final and exact and not fallback:
            disposition = "PROTECTED_EXACT_CONTEXTUAL"
        elif final and not exact and fallback:
            disposition = "EXCLUDED_NONEXACT_FINAL_FORM"
        elif final and not exact and not fallback:
            disposition = "PROTECTED_NONEXACT_CONTEXTUAL"
        elif not final and exact and fallback:
            disposition = "UNEXPECTED_EXACT_RAW_ONLY_FALLBACK"
        elif not final and exact and not fallback:
            disposition = "PROTECTED_EXACT_CONTEXTUAL_RAW_ONLY_FORM"
        elif not final and not exact and fallback:
            disposition = "EXCLUDED_NONEXACT_RAW_ONLY_FORM"
        else:
            disposition = "PROTECTED_NONEXACT_CONTEXTUAL_RAW_ONLY_FORM"
        new = new_by_target[source["target_occurrence_id"]]
        semantic_same = (
            str(new["gdt779_default_de"]) == source["gdt778_default_de"]
            and int(new["gdt779_renderer_contextual"]) == int(source["gdt778_renderer_contextual"])
        )
        consumption_same = (
            int(new["gdt779_consumed_token_count"]) == int(source["gdt778_consumed_token_count"])
            and str(new["gdt779_consumed_token_ids"]) == source["gdt778_consumed_token_ids"]
        )
        parent_state_same = semantic_same and consumption_same and (
            str(new["gdt779_span_id"]) == source["gdt778_span_id"]
            and str(new["gdt779_exact_whole"]) == source["gdt778_exact_whole"]
            and str(new["gdt779_confidence"]) == source["gdt778_confidence"]
        )
        output.append({
            "shadow_id": f"G779-H{number:03d}", "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "ol_ordinal": int(source["ordinal"]), "right_ordinal": int(source["right_ordinal"]),
            "right_surface": source["right_surface"], "right_reader_exact": int(exact),
            "parent_gdt778_fallback": int(fallback), "parent_gdt778_contextual": int(not fallback),
            "raw_76_deck_member": 1, "final_44_deck_member": int(final),
            "deck_phase": "FINAL_44_FROZEN_DECK" if final else "RAW_76_SCREEN_ONLY",
            "precedence_disposition": disposition,
            "old_gdt778_branch": source["gdt778_branch"], "old_gdt778_default_de": source["gdt778_default_de"],
            "old_gdt778_consumed_token_count": int(source["gdt778_consumed_token_count"]),
            "old_gdt778_consumed_token_ids": source["gdt778_consumed_token_ids"],
            "new_gdt779_branch": new["gdt779_branch"], "new_gdt779_default_de": new["gdt779_default_de"],
            "new_gdt779_contextual": int(new["gdt779_renderer_contextual"]),
            "new_gdt779_consumed_token_count": int(new["gdt779_consumed_token_count"]),
            "new_gdt779_consumed_token_ids": new["gdt779_consumed_token_ids"],
            "semantic_state_unchanged": int(semantic_same),
            "consumption_state_unchanged": int(consumption_same),
            "represented_parent_state_unchanged": int(parent_state_same),
            "selected_by_gdt779": int(disposition == "SELECTED_GDT779_FALLBACK"),
            "component_export_credit": 0,
        })

    assert len(output) == 179
    assert Counter((row["parent_gdt778_fallback"], row["parent_gdt778_contextual"]) for row in output) == Counter({(1, 0): 99, (0, 1): 80})
    exact_split = Counter(row["parent_gdt778_fallback"] for row in output if int(row["right_reader_exact"]))
    assert exact_split == Counter({0: 77, 1: 50})
    final_rows = [row for row in output if int(row["final_44_deck_member"])]
    assert len(final_rows) == 68 and sum(int(row["right_reader_exact"]) for row in final_rows) == 63
    assert sum(int(row["selected_by_gdt779"]) for row in final_rows) == 50
    protected_exact = [row for row in output if int(row["right_reader_exact"]) and int(row["parent_gdt778_contextual"])]
    assert len(protected_exact) == 77
    assert all(int(row["represented_parent_state_unchanged"]) for row in protected_exact)
    assert all(
        int(row["represented_parent_state_unchanged"])
        for row in output if int(row["parent_gdt778_contextual"])
    )
    assert Counter(row["precedence_disposition"] for row in output) == Counter({
        "SELECTED_GDT779_FALLBACK": 50, "PROTECTED_EXACT_CONTEXTUAL": 13,
        "EXCLUDED_NONEXACT_FINAL_FORM": 4, "PROTECTED_NONEXACT_CONTEXTUAL": 1,
        "PROTECTED_EXACT_CONTEXTUAL_RAW_ONLY_FORM": 64,
        "EXCLUDED_NONEXACT_RAW_ONLY_FORM": 45,
        "PROTECTED_NONEXACT_CONTEXTUAL_RAW_ONLY_FORM": 2,
    })
    return output


def build_dictionary(specs: Mapping[str, Mapping[str, str]], spans: Sequence[Mapping[str, object]],
                     exclusions: Sequence[Mapping[str, object]], shadow: Sequence[Mapping[str, object]],
                     cards: Mapping[str, Sequence[Mapping[str, str]]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for form in sorted(specs):
        spec, card = specs[form], cards[form][0]
        local = [row for row in spans if row["right_surface"] == form]
        final_shadow = [row for row in shadow if row["right_surface"] == form]
        output.append({
            "entry": form, "preferred_gdt779_default_de": spec["selected_default_de"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "card_class": spec["card_class"],
            "v99_reading_id": card["reading_id"],
            "v99_unconditional_global_export_allowed": int(card["unconditional_global_export_allowed"]),
            "selected_exact_fallback_contexts": len(local), "final_form_raw_parent_contexts": len(final_shadow),
            "final_form_exact_parent_contexts": sum(int(row["right_reader_exact"]) for row in final_shadow),
            "protected_exact_contextual_contexts": sum(
                int(row["right_reader_exact"]) and int(row["parent_gdt778_contextual"]) for row in final_shadow
            ),
            "nonexact_fallback_exclusions": sum(row["right_surface"] == form for row in exclusions),
            "rendered_displays_de": " || ".join(sorted({str(row["new_gdt779_default_de"]) for row in local})),
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "scope": "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT",
            "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(output) == 44
    assert sum(int(row["selected_exact_fallback_contexts"]) for row in output) == 50
    assert sum(int(row["final_form_raw_parent_contexts"]) for row in output) == 68
    assert sum(int(row["final_form_exact_parent_contexts"]) for row in output) == 63
    assert sum(int(row["protected_exact_contextual_contexts"]) for row in output) == 13
    assert sum(int(row["nonexact_fallback_exclusions"]) for row in output) == 4
    return output


def lookup_optional(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: dict(row) for row in rows}


def build_provenance(specs: Mapping[str, Mapping[str, str]], cards: Mapping[str, Sequence[Mapping[str, str]]],
                     spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    g737 = lookup_optional(read_tsv(G737_PATH), "body")
    g738 = lookup_optional(read_tsv(G738_PATH), "body")
    g749 = lookup_optional(read_tsv(G749_PATH), "target_surface")
    g754 = lookup_optional(read_tsv(G754_PATH), "surface")
    g755 = lookup_optional(read_tsv(G755_GLOSS_PATH), "surface")
    g755_occ = [row for row in read_tsv(G755_OCC_PATH) if row["surface"] == "qockhey"]
    g758 = lookup_optional(read_tsv(G758_PATH), "surface")
    assert len(g737) == len(g738) == 120
    assert g749["qokaiin"]["outside_role_status"] == "K1_OPEN_OR_BASELINE_LIKE"
    assert g754["qockhey"]["source_literal_prose_spoken_after_gdt754"] == "0"
    assert g754["qockhey"]["renderer_disposition"] == "COMPOSITION_AXES_HYPOTHESIS_ONLY"
    assert g755["qockhey"]["gdt755_working_candidate_de"] == "mische"
    assert g755["qockhey"]["working_confidence"] == "C0_FORCED_DEFAULT"
    assert len(g755_occ) == 12 and sum(int(row["boundary_complete"]) for row in g755_occ) == 7
    assert g758["oky"]["gdt758_renderer_value_de"] == "erste Wärmestufe"
    assert g758["sheol"]["gdt758_renderer_value_de"] == "eingeweicht/feucht"

    output: list[dict[str, object]] = []
    for form in sorted(specs):
        spec, card = specs[form], cards[form][0]
        old_patient = int(ACTIVE_BANNED_RE.search(card["working_meaning_de"]) is not None)
        r737, r738, r749, r758 = g737.get(form), g738.get(form), g749.get(form), g758.get(form)
        qockhey = form == "qockhey"
        output.append({
            "right_surface": form, "card_class": spec["card_class"],
            "selected_default_de": spec["selected_default_de"], "confidence": spec["confidence"],
            "v99_reading_id": card["reading_id"],
            "v99_old_working_meaning_de_provenance_only": card["working_meaning_de"],
            "v99_old_spoken_default_de_provenance_only": card["v99r7_spoken_default_de"],
            "v99_source_gdts": card["source_gdts"], "v99_positive_evidence_de": card["positive_evidence_de"],
            "v99_counterevidence_de": card["counterevidence_de"],
            "v99_unconditional_global_export_allowed": int(card["unconditional_global_export_allowed"]),
            "v99_candidate_composition": card["gdt734_candidate_composition"],
            "old_literal_patient_detected": old_patient,
            "patient_sanitization_applied": int(form in SANITIZED),
            "gdt737_family": r737["family"] if r737 else "NONE",
            "gdt737_candidate_de": r737["concrete_body_role_de"] if r737 else "NONE",
            "gdt737_renderer_license": int(r737["renderer_license"]) if r737 else 0,
            "gdt738_discovery_decision": r738["discovery_decision"] if r738 else "NONE",
            "gdt738_w23_decision": r738["w23_decision"] if r738 else "NONE",
            "gdt738_body_renderer_license": int(r738["body_renderer_license"]) if r738 else 0,
            "gdt749_outside_role_status": r749["outside_role_status"] if r749 else "NONE",
            "gdt758_later_whole_default_de": r758["gdt758_renderer_value_de"] if r758 else "NONE",
            "qockhey_gdt754_source_composition_quarantined": int(qockhey),
            "qockhey_gdt754_current_source_prose_de_provenance_only": g754[form]["current_source_prose_de"] if qockhey else "NONE",
            "qockhey_gdt754_source_composition": g754[form]["source_composition"] if qockhey else "NONE",
            "qockhey_gdt755_complete_whole_candidate_de": g755[form]["gdt755_working_candidate_de"] if qockhey else "NONE",
            "qockhey_gdt755_confidence": g755[form]["working_confidence"] if qockhey else "NONE",
            "qockhey_gdt755_exact_occurrences": len(g755_occ) if qockhey else 0,
            "qockhey_gdt755_boundary_complete_occurrences": sum(int(row["boundary_complete"]) for row in g755_occ) if qockhey else 0,
            "selected_exact_fallback_occurrences": sum(row["right_surface"] == form for row in spans),
            "exact_complete_whole_only": 1, "old_prose_used_as_active_default": 0,
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    assert len(output) == 44
    assert {row["right_surface"] for row in output if int(row["old_literal_patient_detected"])} == SANITIZED
    assert sum(int(row["patient_sanitization_applied"]) for row in output) == 6
    assert sum(int(row["qockhey_gdt754_source_composition_quarantined"]) for row in output) == 1
    assert all(int(row["v99_unconditional_global_export_allowed"]) == (0 if row["right_surface"] in NEW_SCOPES else 1) for row in output)
    assert all((row["v99_candidate_composition"] != "NONE") == (row["right_surface"] in COMPOSED) for row in output)
    return output


def render_line(locus: str, written_line: str,
                renderer_by_position: Mapping[tuple[str, int], Mapping[str, object]], generation: str) -> str:
    assert generation in {"gdt778", "gdt779"}
    tokens, rendered, consumed = written_line.split(), [], set()
    for ordinal, token in enumerate(tokens, 1):
        if ordinal in consumed:
            continue
        dispatch = renderer_by_position.get((locus, ordinal))
        if dispatch is None:
            rendered.append(token)
            continue
        if int(dispatch[f"{generation}_renderer_contextual"]):
            rendered.append(f"⟦{dispatch[f'{generation}_default_de']}⟧")
            count = int(dispatch[f"{generation}_consumed_token_count"])
            consumed.update(range(ordinal + 1, ordinal + count + 1))
        else:
            rendered.append(token)
    return " ".join(rendered)


def build_passages(base: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, object]],
                   spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    old_by_pos = {(row["locus"], int(row["ordinal"])): row for row in base}
    new_by_pos = {(str(row["locus"]), int(row["ordinal"])): row for row in renderer}
    by_locus: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for span in spans:
        by_locus[str(span["locus"])].append(span)
    output: list[dict[str, object]] = []
    for number, (locus, local) in enumerate(sorted(by_locus.items()), 1):
        local = sorted(local, key=lambda row: int(row["ol_ordinal"]))
        written = str(local[0]["written_line_eva"])
        assert all(str(row["written_line_eva"]) == written for row in local)
        old_patch = render_line(locus, written, old_by_pos, "gdt778")
        new_patch = render_line(locus, written, new_by_pos, "gdt779")
        assert old_patch != new_patch
        output.append({
            "passage_patch_id": f"G779-P{number:03d}",
            "span_ids": "|".join(str(row["span_id"]) for row in local),
            "target_occurrence_ids": "|".join(str(row["target_occurrence_id"]) for row in local),
            "page": local[0]["page"], "physical_folio": local[0]["physical_folio"], "locus": locus,
            "target_count": len(local), "right_surfaces": "|".join(str(row["right_surface"]) for row in local),
            "right_token_ids": "|".join(str(row["gdt779_consumed_token_id"]) for row in local),
            "selected_whole_defaults_de": " || ".join(str(row["selected_whole_default_de"]) for row in local),
            "written_line_eva": written, "inherited_gdt778_patch_de": old_patch,
            "gdt779_practical_patch_de": new_patch,
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(output) == 49 and sum(int(row["target_count"]) for row in output) == 50
    doubles = [(row["locus"], row["target_count"], row["right_surfaces"]) for row in output if int(row["target_count"]) == 2]
    assert doubles == [("f75r.26", 2, "sheol|qoly")]
    return output


def build_residual(renderer: Sequence[Mapping[str, object]], cards: Mapping[str, Sequence[Mapping[str, str]]],
                   specs: Mapping[str, Mapping[str, str]], raw_forms: set[str]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    residual = [row for row in renderer if int(row["gdt779_renderer_contextual"]) == 0]
    for number, row in enumerate(residual, 1):
        surface = str(row["right_surface"])
        if surface == "NONE" or int(row["right_ordinal"]) == 0:
            reason = "LINE_FINAL_NO_RIGHT"
        elif surface not in cards:
            reason = (
                "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT"
                if int(row["right_reader_exact"])
                else "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT"
            )
        elif surface in specs:
            assert not int(row["right_reader_exact"])
            reason = "V99_CARD_NONEXACT_FINAL44"
        else:
            assert surface in raw_forms and not int(row["right_reader_exact"])
            reason = "V99_CARD_NONEXACT_RAW_ONLY"
        output.append({
            "residual_id": f"G779-R{number:03d}", "target_occurrence_id": row["target_occurrence_id"],
            "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
            "ol_ordinal": int(row["ordinal"]), "right_ordinal": int(row["right_ordinal"]),
            "right_surface": surface, "right_reader_exact": int(row["right_reader_exact"]),
            "residual_reason": reason, "gdt779_default_de": row["gdt779_default_de"],
            "v99_complete_card_present": int(surface in cards), "final_44_deck_member": int(surface in specs),
            "component_export_credit": 0,
        })
    assert len(output) == 131
    assert Counter(row["residual_reason"] for row in output) == Counter({
        "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 25,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
        "V99_CARD_NONEXACT_RAW_ONLY": 45, "LINE_FINAL_NO_RIGHT": 37,
        "V99_CARD_NONEXACT_FINAL44": 4,
    })
    return output


def make_packet(spans: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        edge_id = f"G779-E{number:03d}"
        packet.append({
            "edge_id": edge_id, "batch_id": "GDT779_EXACT_OL_RESIDUAL_V99R7_WHOLE",
            "page": span["page"], "physical_folio": span["physical_folio"],
            "diagram_unit_id": f"LINE:{span['locus']}",
            "pivot_visual_id": f"TOKEN:{span['locus']}:{span['ol_ordinal']}",
            "pivot_locus": f"{span['locus']}@{span['ol_ordinal']}",
            "target_visual_id": f"TOKEN:{span['locus']}:{span['right_ordinal']}",
            "target_locus": f"{span['locus']}@{span['right_ordinal']}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT778", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT779_RUNNER",
            "relation_reviewer": "GDT779_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION", "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": "GDT779_EXACT_OL_RESIDUAL_V99R7_WHOLE",
            "span_id": span["span_id"], "target_occurrence_id": span["target_occurrence_id"],
            "page": span["page"], "physical_folio": span["physical_folio"], "locus": span["locus"],
            "ol_ordinal": span["ol_ordinal"], "right_ordinal": span["right_ordinal"],
            "right_surface": span["right_surface"], "written_span_eva": span["written_span_eva"],
            "selection_rule": SELECTION_RULE, "score_eligible": 0, "component_export_credit": 0,
        })
    assert len(packet) == len(crosswalk) == 50
    return packet, crosswalk


def build_report(result: Mapping[str, object], spans: Sequence[Mapping[str, object]]) -> str:
    examples = []
    for span in spans[:6]:
        examples.append(
            f"- `{span['locus']}`: `{span['written_span_eva']}` — "
            f"`{span['old_gdt778_default_de']}` → **{span['new_gdt779_default_de']}**."
        )
    return f"""# GDT779 — residuale exakte V99R7-Ganzwörter nach `ol`

Status: `{result['status']}`.

## Ergebnis

Die occurrence-ID-freie Regel beginnt ausschließlich bei den **181** noch
generischen GDT778-Fallbacks. Unter ihnen besitzen **99** Zeilen in **76**
vollständigen rechten Formen eine V99R7-Ganzwortkarte. Reader-Exaktheit lässt
**50** Spannen in **44** Formen auf **49** loci übrig; **49** nicht-exakte
Kandidaten bleiben sichtbar ausgeschlossen.

Alle 50 Treffer ersetzen direkt den generischen Ansatz-/Zubereitungswert. Die
kontextuelle Abdeckung steigt **195→245**, die Fallbackzahl fällt **181→131**
und der eindeutige Rechte-Token-Verbrauch steigt kollisionsfrei **155→205**.
Die Doppelstelle `f75r.26` wird als eine Passage mit zwei Zielspannen gerendert.

## Precedence-Kontrolle

Der vollständige 76er-Shadow enthält **179** Elternzeilen: 99 Fallbacks und 80
bereits kontextuelle Zeilen. Seine 127 exakten Zeilen teilen sich in 50 neue
Fallbacktreffer und **77 unverändert geschützte kontextuelle** Zeilen. Im finalen
44er-Deck stehen 68 rohe und 63 exakte Elternmatches; 13 der exakten Matches
waren bereits kontextuell und bleiben vollständig geerbt.

## Praktische Beispiele

{chr(10).join(examples)}

## Verbleibende Restschuld

Die 131 Fallbacks zerfallen jetzt ohne erneuten Korpuszugriff in 37 Stellen
ohne rechtes Token, 49 nicht-exakte Stellen mit V99R7-Karte, 20 nicht-exakte
Stellen ohne Karte und 25 reader-exakte Stellen ohne Karte. Nur die letzte
25er-Klasse ist sofort für neue vollständige Ganzwortkandidaten zugänglich;
nicht-exakte oder leere Rechtsfelder werden nicht still repariert.

## Kartenhygiene und Grenze

Die 44 Karten teilen sich disjunkt in 32 direkt geerbte Ganzwortkarten, sechs
patientenfrei sanierte Karten, drei ausschließlich für die neue exakte
`ol + Ganzwort`-Spanne lizenzierte Karten, zwei als Ganzwort geerbte
Kompositionskarten ohne Teilformexport und eine spätere vollständige
GDT755-Ganzwortkarte (`qockhey` → **mische**). Alte Quellenformulierungen sind
nur im Provenienzaudit sichtbar und steuern weder Auswahl noch Renderer.

Die Werte bleiben ersetzbare praktische Ganzwortdefaults. GDT779 bestätigt
kein EVA-Zeichen, keinen Wortteil, kein Lexem, keine Sprache und keinen
Klartextsatz. Es wurden keine neuen Seiten, Bilder, OCR oder Transkriptionen
geöffnet; `f84` und `f84r` blieben gesperrt. Das GDT388-Paket bleibt
`{result['relation_packet']['status']}`.
"""


def build_artifact_readme() -> str:
    return """# GDT779 artifacts

- `GDT779_50_EXACT_WHOLE_ATLAS.tsv`: all selected exact fallback spans.
- `GDT779_49_EXACTNESS_EXCLUSIONS.tsv`: all nonexact raw card matches.
- `GDT779_179_PRECEDENCE_SHADOW_AUDIT.tsv`: full-parent raw-76 and final-44 precedence control.
- `GDT779_376_RENDERER.tsv`: compact parent/current renderer with GDT779 precedence.
- `GDT779_WORKING_DICTIONARY.tsv`: one replaceable default and two rivals for each of 44 wholes.
- `GDT779_PASSAGE_PATCHES.tsv`: 49 grouped changed line renderings for 50 spans.
- `GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv`: old-card provenance, hygiene and source controls.
- `GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv`: every remaining fallback and reason.
- `GDT779_GDT388_RELATION_PACKET.tsv`: explicitly ineligible descriptive adjacency packet.
- `GDT779_RELATION_EDGE_CROSSWALK.tsv`: packet-to-span crosswalk.
- `RELATION_PACKET_INTAKE.json`: executable GDT388 intake result.
- `RESULT.json`: compact machine-readable result.

All German values are replaceable complete-whole defaults, not translations.
"""


def ensure_no_active_leaks(artifacts: Path, report_path: Path, provenance_name: str) -> None:
    for path in sorted(artifacts.iterdir()):
        if not path.is_file() or path.name == provenance_name:
            continue
        text = path.read_text(encoding="utf-8")
        assert ACTIVE_BANNED_RE.search(text) is None, f"retired patient leaked outside provenance: {path}"
    assert ACTIVE_BANNED_RE.search(report_path.read_text(encoding="utf-8")) is None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()

    lock_count = verify_locks()
    specs = validate_specs(read_tsv(SPECS_PATH))
    base = read_tsv(PARENT_RENDERER)
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    assert len(base) == 376
    assert all(field in base[0] for field in (*CORE_FIELDS, *PARENT_STATE_FIELDS))
    assert sum(int(row["gdt778_renderer_contextual"]) for row in base) == 195
    assert sum(1 - int(row["gdt778_renderer_contextual"]) for row in base) == 181
    assert parent_result["renderer"]["gdt778_contextual"] == 195
    assert parent_result["consumption"]["total_unique_right_tokens"] == 155

    cards = v99_registry(read_tsv(V99_PATH))
    assert all(form in cards and len(cards[form]) == 1 for form in specs)
    assert sum(int(cards[form][0]["unconditional_global_export_allowed"]) for form in specs) == 41
    spans, exclusions, raw_forms, raw = build_cohort(base, specs, cards)
    renderer, owners = build_renderer(base, spans)
    shadow = build_shadow(base, renderer, raw_forms, specs)
    dictionary = build_dictionary(specs, spans, exclusions, shadow, cards)
    provenance = build_provenance(specs, cards, spans)
    passages = build_passages(base, renderer, spans)
    residual = build_residual(renderer, cards, specs, raw_forms)
    packet, crosswalk = make_packet(spans)

    renderer_by_target = {str(row["target_occurrence_id"]): row for row in renderer}
    chol = [row for row in base if row["gdt778_exact_whole"] == "chol"]
    ols = [row for row in base if row["gdt778_exact_whole"] == "ols"]
    assert len(chol) == 2 and all(row["gdt778_default_de"] == "Zustand: trocken" for row in chol)
    assert len(ols) == 1 and ols[0]["gdt778_default_de"] == "Produktposten"
    for source in (*chol, *ols):
        new = renderer_by_target[source["target_occurrence_id"]]
        assert new["gdt779_branch"] == "INHERITED_GDT778"
        assert new["gdt779_default_de"] == source["gdt778_default_de"]
        assert new["gdt779_consumed_token_ids"] == source["gdt778_consumed_token_ids"]

    outputs = [
        ("GDT779_50_EXACT_WHOLE_ATLAS.tsv", spans),
        ("GDT779_49_EXACTNESS_EXCLUSIONS.tsv", exclusions),
        ("GDT779_179_PRECEDENCE_SHADOW_AUDIT.tsv", shadow),
        ("GDT779_376_RENDERER.tsv", renderer),
        ("GDT779_WORKING_DICTIONARY.tsv", dictionary),
        ("GDT779_PASSAGE_PATCHES.tsv", passages),
        ("GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv", provenance),
        ("GDT779_RESIDUAL_131_FALLBACK_CENSUS.tsv", residual),
        ("GDT779_GDT388_RELATION_PACKET.tsv", packet),
        ("GDT779_RELATION_EDGE_CROSSWALK.tsv", crosswalk),
    ]
    for name, rows in outputs:
        write_tsv(artifacts / name, rows, list(rows[0]))

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet

    intake = validate_relation_edge_packet(artifacts / "GDT779_GDT388_RELATION_PACKET.tsv")
    assert intake == {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 50, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    result: dict[str, object] = {
        "experiment_id": "GDT779",
        "status": "PASS__50_EXACT_FALLBACK_WHOLES__44_FORMS__49_LOCI__245_CONTEXTUAL__131_FALLBACKS__205_CONSUMED__6_SANITIZATIONS__NO_COMPONENT_EXPORT",
        "source_locks": lock_count, "inherited_guard": parent_result["inherited_guard"],
        "cohort": {
            "renderer_rows": 376, "raw_v99r7_candidates": len(raw), "raw_candidate_forms": len(raw_forms),
            "reader_exact_selected_spans": len(spans), "selected_forms": len(specs),
            "exactness_exclusions": len(exclusions), "excluded_forms": len({row["right_surface"] for row in exclusions}),
            "loci": len({row["locus"] for row in spans}), "page_labels": len({row["page"] for row in spans}),
            "physical_folios": len({row["physical_folio"] for row in spans}),
        },
        "precedence_shadow": {
            "raw_76_full_parent_matches": len(shadow), "parent_fallback_matches": 99,
            "parent_contextual_matches": 80, "reader_exact_matches": 127,
            "selected_exact_fallback_matches": 50, "protected_exact_contextual_matches": 77,
            "final_44_raw_parent_matches": 68, "final_44_exact_parent_matches": 63,
            "final_44_protected_exact_contextual_matches": 13,
        },
        "changes": {"fallback_replacements": 50, "actual_display_changes": 50, "passage_patches": len(passages)},
        "renderer": {
            "gdt778_contextual": 195, "gdt779_contextual": 245,
            "gdt778_fallbacks": 181, "gdt779_fallbacks": 131,
        },
        "consumption": {
            "gdt778_unique_right_tokens": 155, "gdt779_selected_right_tokens": 50,
            "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 50,
            "total_unique_right_tokens": len(owners), "cross_row_collisions": 0,
        },
        "card_partition": dict(sorted(CLASS_COUNTS.items())),
        "source_hygiene": {
            "patient_sanitizations": 6, "new_exact_ol_scopes": 3,
            "composition_derived_complete_wholes": 2, "qockhey_later_complete_whole_replacements": 1,
            "globally_exportable_v99_cards": 41, "old_literal_patient_leaks_outside_provenance": 0,
            "qockhey_source_composed_prose_used": False, "chol_confirmations_changed": 0,
            "ols_rejected_legacy_process_reading_restored": False,
        },
        "dictionary_rows": len(dictionary), "residual_fallback_rows": len(residual),
        "residual_partition": {
            "line_final_no_right": 37, "v99_card_nonexact": 49,
            "no_card_reader_nonexact": 20, "no_card_reader_exact": 25,
        },
        "relation_packet": intake, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "component_exports": 0, "new_pages": 0, "new_images": 0, "new_ocr": 0,
        "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "Replaceable exact ol plus complete-whole meanings only; no EVA component, lexeme, language, plaintext, specific recipe, substance, disease, or treatment.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, spans), encoding="utf-8")
    (artifacts / "README.md").write_text(build_artifact_readme(), encoding="utf-8")
    ensure_no_active_leaks(artifacts, report_path, "GDT779_PROVENANCE_SANITIZATION_AUDIT.tsv")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
