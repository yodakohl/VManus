#!/usr/bin/env python3
"""Promote the fixed legacy singleton deck only after exact ``ol``.

The selection key is the complete right-token surface plus reader exactness.
No occurrence identifier, EVA substring, free component, or new transcription
enters the rule.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
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
EXP = ROOT / "experiments/yolo/gdt778_ol_singleton_exact_whole_promotion"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SPECS = SRC / "EXACT_WHOLE_SPECS.tsv"
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

RETIRED_SELECTED_RE = re.compile(r"(?i)(pulver|samen|wurzel|holz|drogen|filtrat|abgeseih)")
LATER_WHOLES = frozenset({"ar", "chor", "chol", "dair"})
SOURCE_CONFLICT_WHOLES = frozenset({"ols"})
G736_PROMOTIONS = frozenset({"air", "oaiin", "chy"})


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    return value


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
    assert len(rows) == 13
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert sha256(ROOT / relative) == row["expected_sha256"], f"source changed: {relative}"
    return len(rows)


def one_by(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        assert value not in output, (key, value)
        output[value] = dict(row)
    return output


def validate_specs(rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, str]]:
    required = {
        "right_surface", "selected_default_de", "alternate_1_de", "alternate_2_de",
        "confidence", "provenance_path", "promotion_status", "positive_evidence", "counterevidence",
    }
    assert len(rows) == 29 and required <= set(rows[0])
    specs = one_by(rows, "right_surface")
    assert Counter(row["promotion_status"] for row in rows) == Counter({
        "EXACT_OL_PLUS_WHOLE_ONLY_NEW_PROMOTION": 24,
        "EXACT_OL_PLUS_WHOLE_ONLY": 4,
        "EXACT_OL_PLUS_WHOLE_ONLY__SOURCE_CONFLICT": 1,
    })
    assert {form for form, row in specs.items() if row["provenance_path"].startswith("GDT736_")} == G736_PROMOTIONS
    assert {form for form, row in specs.items() if row["provenance_path"].startswith("GDT737_")} == (
        set(specs) - LATER_WHOLES - SOURCE_CONFLICT_WHOLES - G736_PROMOTIONS
    )
    for form, row in specs.items():
        assert form and " " not in form
        assert row["confidence"] in {"C0", "C1", "C2"}
        values = (row["selected_default_de"], row["alternate_1_de"], row["alternate_2_de"])
        assert all(value and value != "NONE" for value in values)
        assert len(set(values)) == 3
        assert RETIRED_SELECTED_RE.search(" ".join(values)) is None, (form, values)
    assert specs["ols"]["selected_default_de"] == "Produktposten"
    assert specs["ols"]["confidence"] == "C0"
    return specs


def build_legacy_registry(specs: Mapping[str, Mapping[str, str]]) -> dict[str, dict[str, str]]:
    word_rows = [row for row in read_tsv(G734_WORDS) if row["surface"] in specs]
    word_by_surface = one_by(word_rows, "surface")
    residual_rows = [row for row in read_tsv(G734_RESIDUAL) if row["surface"] in specs]
    residual_by_surface = one_by(residual_rows, "surface")
    assert len(word_by_surface) == 27
    assert set(specs) - set(word_by_surface) == {"oldaiin", "ory"}
    assert {"oldaiin", "ory"} <= set(residual_by_surface)
    output: dict[str, dict[str, str]] = {}
    for form in specs:
        if form in word_by_surface:
            source = word_by_surface[form]
            output[form] = {
                "legacy_source": "GDT734_V99R7_COMPLETE_WORD_CONFIDENCE",
                "legacy_reading_id": source["reading_id"],
                "legacy_working_meaning_de": source["working_meaning_de"],
                "legacy_source_status": source["v99_audit_decision"],
            }
        else:
            source = residual_by_surface[form]
            output[form] = {
                "legacy_source": "GDT734_V99R7_RESIDUAL_SPLIT_INVENTORY",
                "legacy_reading_id": "NONE",
                "legacy_working_meaning_de": source["exact_v99r4_routes"],
                "legacy_source_status": source["selection_reason"],
            }
    return output


def build_provenance(specs: Mapping[str, Mapping[str, str]],
                     raw_counts: Mapping[str, int], exact_counts: Mapping[str, int]) -> list[dict[str, object]]:
    legacy = build_legacy_registry(specs)
    g736 = one_by(read_tsv(G736_BODIES), "body")
    g737 = one_by(read_tsv(G737_BODIES), "body")
    g738 = one_by(read_tsv(G738_BRIDGE), "body")
    g758 = one_by(read_tsv(G758_CENSUS), "surface")
    g759 = one_by(read_tsv(G759_DICTIONARY), "exact_expression_eva")
    g768 = one_by(read_tsv(G768_DICTIONARY), "surface")
    g769 = one_by(read_tsv(G769_DICTIONARY), "surface")
    g772 = one_by(read_tsv(G772_DICTIONARY), "whole_form")
    assert g768["chor"]["concrete_default_de"] == "Blütenstand"
    assert g768["dair"]["concrete_default_de"] == "Anteil II"
    assert g758["ar"]["gdt758_renderer_value_de"] == "Anteil"
    assert g758["chol"]["gdt758_renderer_value_de"] == "trocken/getrocknet"
    assert int(g758["chol"]["reader_exact_occurrences"]) == 303
    assert int(g759["chor chol"]["exact_occurrences"]) + int(g759["chol chor"]["exact_occurrences"]) == 15
    assert g769["ols"]["working_default_de"] == "Maß-/Produktposten"
    assert g772["ols"]["formal_policy_decision"] == "OLS_NULL"
    assert "Colatura" in g772["ols"]["concrete_replaceable_default_de"]
    assert "abgeseiht" in g758["ols"]["gdt758_renderer_value_de"]

    output: list[dict[str, object]] = []
    for form in sorted(specs):
        spec = specs[form]
        if form in G736_PROMOTIONS:
            source = g736[form]
            source_kind = "GDT736_BODY_CANDIDATE"
            source_axis = source["revised_concrete_default_de"]
            source_status = source["revision_decision"]
            source_confidence = source["role_confidence"]
            source_occurrences = int(source["target_occurrences"])
            source_bare_occurrences: object = "NA"
            g738_discovery = "NOT_APPLICABLE_GDT736_TRAINING"
            g738_w23 = "NOT_APPLICABLE_GDT736_TRAINING"
            source_renderer_license = 0
        elif form not in LATER_WHOLES and form not in SOURCE_CONFLICT_WHOLES:
            source, bridge = g737[form], g738[form]
            source_kind = "GDT737_BODY_CANDIDATE"
            source_axis = source["concrete_body_role_de"]
            source_status = source["export_rule"]
            source_confidence = source["confidence"]
            source_occurrences = int(source["occurrence_total"])
            source_bare_occurrences = int(source["bare_body_occurrences"])
            g738_discovery = bridge["discovery_decision"]
            g738_w23 = bridge["w23_decision"]
            source_renderer_license = int(source["renderer_license"])
            assert source_renderer_license == int(bridge["body_renderer_license"]) == 0
        elif form in {"chor", "dair"}:
            source = g768[form]
            source_kind = "GDT768_LATER_COMPLETE_WHOLE"
            source_axis = source["concrete_default_de"]
            source_status = source["tournament_result"]
            source_confidence = source["working_confidence"]
            source_occurrences = int(g758[form]["reader_exact_occurrences"]) if form in g758 else int(raw_counts[form])
            source_bare_occurrences = "NA"
            g738_discovery = "SUPERSEDED_BY_LATER_COMPLETE_WHOLE"
            g738_w23 = "SUPERSEDED_BY_LATER_COMPLETE_WHOLE"
            source_renderer_license = 1
        elif form in {"ar", "chol"}:
            source = g758[form]
            source_kind = "GDT758_GDT759_LATER_COMPLETE_WHOLE"
            source_axis = source["gdt758_renderer_value_de"]
            source_status = "GDT758_GLOBAL" + ("__GDT759_15_BIDIRECTIONAL_STATE_PAIRS" if form == "chol" else "")
            source_confidence = source["working_confidence"]
            source_occurrences = int(source["reader_exact_occurrences"])
            source_bare_occurrences = "NA"
            g738_discovery = "SUPERSEDED_BY_LATER_COMPLETE_WHOLE"
            g738_w23 = "SUPERSEDED_BY_LATER_COMPLETE_WHOLE"
            source_renderer_license = 1
        else:
            assert form == "ols"
            source = g769[form]
            source_kind = "GDT769_GDT772_SOURCE_CONFLICT"
            source_axis = source["working_default_de"]
            source_status = f"{source['role_disposition']}__{g772[form]['formal_policy_decision']}"
            source_confidence = source["working_confidence"]
            source_occurrences = int(g758[form]["reader_exact_occurrences"])
            source_bare_occurrences = "NA"
            g738_discovery = "SUPERSEDED_BY_LATER_SOURCE_CONFLICT"
            g738_w23 = "SUPERSEDED_BY_LATER_SOURCE_CONFLICT"
            source_renderer_license = 0
        conflict = form == "ols"
        output.append({
            "right_surface": form, "provenance_path": spec["provenance_path"],
            "promotion_status": spec["promotion_status"], "selected_default_de": spec["selected_default_de"],
            "confidence": spec["confidence"], "source_kind": source_kind, "source_axis_de": source_axis,
            "source_status": source_status, "source_confidence": source_confidence,
            "source_headed_or_target_occurrences": source_occurrences,
            "source_bare_occurrences": source_bare_occurrences,
            "gdt738_discovery_decision": g738_discovery, "gdt738_w23_decision": g738_w23,
            "source_renderer_license_before_gdt778": source_renderer_license,
            "gdt734_legacy_source": legacy[form]["legacy_source"],
            "gdt734_legacy_reading_id": legacy[form]["legacy_reading_id"],
            "gdt734_legacy_working_meaning_de": legacy[form]["legacy_working_meaning_de"],
            "gdt734_legacy_status": legacy[form]["legacy_source_status"],
            "ol_local_raw_occurrences": raw_counts[form],
            "ol_local_reader_exact_occurrences": exact_counts[form],
            "source_conflict": int(conflict),
            "source_conflict_detail": (
                "GDT758_ABGESEIHTES_ENDPRODUKT_RETIRED__GDT769_MASS_PRODUCT_FIELD_RIVAL__GDT772_OLS_NULL"
                if conflict else "NONE"
            ),
            "gdt778_conflict_decision": (
                "NEW_C0_PRODUKTPOSTEN_EXACT_OL_PLUS_WHOLE_ONLY__FILTRATE_OR_STRAINING_NOT_SELECTED"
                if conflict else "NO_SOURCE_CONFLICT"
            ),
            "legacy_literal_patient_quarantined": 1, "exact_complete_whole_only": 1,
            "free_component_export": 0, "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0,
        })
    assert len(output) == 29
    assert sum(int(row["source_conflict"]) for row in output) == 1
    assert sum(row["source_kind"] == "GDT737_BODY_CANDIDATE" for row in output) == 21
    assert sum(row["source_kind"] == "GDT736_BODY_CANDIDATE" for row in output) == 3
    return output


def structural_frame(old_default: str) -> str:
    if old_default == "und":
        return "UND_LINK"
    if old_default.startswith("Ansatz:"):
        return "ANSATZ_FRAME"
    if old_default.startswith("Zustand:"):
        return "STATE_FRAME"
    return "NONE"


def compose_display(surface: str, selected_default: str, old_default: str,
                    old_contextual: int) -> tuple[str, str, int, int, int]:
    if not old_contextual:
        return selected_default, "FALLBACK_REPLACEMENT", 1, 0, 0
    frame = structural_frame(old_default)
    if surface == "chol":
        assert frame == "STATE_FRAME" and old_default == "Zustand: trocken"
        return old_default, "CONTEXTUAL_CONFIRMATION", 0, 0, 1
    if frame == "UND_LINK":
        return f"und; {selected_default}", "CONTEXTUAL_SHARPENING", 0, 1, 0
    if frame == "ANSATZ_FRAME":
        return f"Ansatz: {selected_default}", "CONTEXTUAL_SHARPENING", 0, 1, 0
    raise AssertionError((surface, old_default, old_contextual))


def build_cohort(base: Sequence[Mapping[str, str]], specs: Mapping[str, Mapping[str, str]]) -> tuple[
    list[dict[str, object]], list[dict[str, object]], Counter[str], Counter[str]
]:
    raw_counts: Counter[str] = Counter()
    exact_counts: Counter[str] = Counter()
    selected: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for source in base:
        surface = source["right_surface"]
        if surface not in specs:
            continue
        raw_counts[surface] += 1
        if source["right_reader_exact"] != "1":
            exclusions.append({
                "exclusion_id": "PENDING", "target_occurrence_id": source["target_occurrence_id"],
                "page": source["page"], "physical_folio": source["physical_folio"],
                "locus": source["locus"], "ol_ordinal": int(source["ordinal"]),
                "right_ordinal": int(source["right_ordinal"]), "right_surface": surface,
                "right_reader_exact": int(source["right_reader_exact"]),
                "exclusion_reason": "RIGHT_COMPLETE_WHOLE_NOT_READER_EXACT",
                "selection_rule": "RIGHT_SURFACE_IN_FIXED_29_DECK_AND_RIGHT_READER_EXACT",
                "selection_uses_occurrence_id": 0, "component_export_credit": 0,
            })
            continue
        exact_counts[surface] += 1
        spec = specs[surface]
        old_contextual = int(source["gdt777_renderer_contextual"])
        display, change_class, fallback, sharpening, confirmation = compose_display(
            surface, spec["selected_default_de"], source["gdt777_default_de"], old_contextual
        )
        tokens = source["written_line_eva"].split()
        ol_ordinal, right_ordinal = int(source["ordinal"]), int(source["right_ordinal"])
        assert right_ordinal == ol_ordinal + 1
        assert tokens[ol_ordinal - 1] == "ol" and tokens[right_ordinal - 1] == surface
        inherited_ids = source["gdt777_consumed_token_ids"]
        token_id = f"{source['locus']}@{right_ordinal}"
        same_row_takeover = int(token_id in inherited_ids.split("|") if inherited_ids != "NONE" else False)
        selected.append({
            "span_id": "PENDING", "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "ol_ordinal": ol_ordinal, "right_ordinal": right_ordinal, "line_token_count": len(tokens),
            "right_surface": surface, "written_span_eva": f"ol {surface}",
            "written_line_eva": source["written_line_eva"], "right_reader_exact": 1,
            "old_gdt777_branch": source["gdt777_branch"],
            "old_gdt777_default_de": source["gdt777_default_de"],
            "old_gdt777_contextual": old_contextual,
            "inherited_structural_frame": structural_frame(source["gdt777_default_de"]),
            "selected_whole_default_de": spec["selected_default_de"],
            "new_gdt778_default_de": display, "semantic_change_class": change_class,
            "fallback_replacement": fallback, "contextual_sharpening": sharpening,
            "contextual_confirmation": confirmation, "display_changed": int(display != source["gdt777_default_de"]),
            "confidence": spec["confidence"], "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"], "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"], "provenance_path": spec["provenance_path"],
            "promotion_status": spec["promotion_status"],
            "inherited_consumed_token_ids": inherited_ids,
            "gdt778_consumed_token_id": token_id,
            "same_row_inherited_consumption_takeover": same_row_takeover,
            "new_unique_consumption": 1 - same_row_takeover,
            "cross_row_consumption_collision": 0,
            "selection_rule": "RIGHT_SURFACE_IN_FIXED_29_DECK_AND_RIGHT_READER_EXACT__ALL_MATCHES__NO_OCCURRENCE_ID",
            "composition_rule": (
                "PRESERVE_STATE_FRAME_CONFIRMATION" if confirmation else
                "PRESERVE_STRUCTURAL_FRAME_AND_APPEND_EXACT_WHOLE" if sharpening else
                "REPLACE_GENERIC_FALLBACK_WITH_EXACT_WHOLE"
            ),
            "scope_status": "EXPLORATORY_EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY",
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    for number, row in enumerate(selected, 1):
        row["span_id"] = f"G778-S{number:03d}"
    for number, row in enumerate(exclusions, 1):
        row["exclusion_id"] = f"G778-X{number:03d}"

    assert len(raw_counts) == len(exact_counts) == 29
    assert sum(raw_counts.values()) == 41 and sum(exact_counts.values()) == len(selected) == 39
    assert len(exclusions) == 2
    assert {(row["target_occurrence_id"], row["right_surface"]) for row in exclusions} == {
        ("G769-T0284", "keey"), ("G769-T0391", "dal")
    }
    assert len({row["locus"] for row in selected}) == 39
    assert len({row["page"] for row in selected}) == 31
    assert len({row["physical_folio"] for row in selected}) == 25
    assert sum(int(row["fallback_replacement"]) for row in selected) == 32
    assert Counter(row["right_surface"] for row in selected if int(row["contextual_sharpening"])) == Counter({
        "ar": 1, "kain": 2, "chy": 2,
    })
    assert Counter(row["right_surface"] for row in selected if int(row["contextual_confirmation"])) == Counter({"chol": 2})
    assert sum(int(row["display_changed"]) for row in selected) == 37
    assert sum(int(row["same_row_inherited_consumption_takeover"]) for row in selected) == 4
    assert Counter(row["right_surface"] for row in selected if int(row["same_row_inherited_consumption_takeover"])) == Counter({
        "chol": 2, "chy": 2,
    })
    return selected, exclusions, raw_counts, exact_counts


def inherited_owner_map(base: Sequence[Mapping[str, str]]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for row in base:
        value = row["gdt777_consumed_token_ids"]
        if value == "NONE":
            continue
        for token_id in value.split("|"):
            assert token_id not in owners, token_id
            owners[token_id] = row["target_occurrence_id"]
    assert len(owners) == 120
    return owners


def build_renderer(base: Sequence[Mapping[str, str]], spans: Sequence[Mapping[str, object]]) -> tuple[
    list[dict[str, object]], dict[str, str]
]:
    by_occurrence = {str(row["target_occurrence_id"]): row for row in spans}
    assert len(by_occurrence) == len(spans)
    inherited_owners = inherited_owner_map(base)
    for span in spans:
        token_id = str(span["gdt778_consumed_token_id"])
        owner = inherited_owners.get(token_id)
        if owner is not None:
            assert owner == span["target_occurrence_id"], (token_id, owner, span["target_occurrence_id"])

    output: list[dict[str, object]] = []
    for source in base:
        row: dict[str, object] = dict(source)
        row.update({
            "gdt778_branch": "INHERITED_GDT777", "gdt778_default_de": source["gdt777_default_de"],
            "gdt778_renderer_contextual": int(source["gdt777_renderer_contextual"]),
            "gdt778_span_id": source["gdt777_span_id"], "gdt778_exact_whole": "NONE",
            "gdt778_confidence": source["gdt777_confidence"],
            "gdt778_consumed_token_count": int(source["gdt777_consumed_token_count"]),
            "gdt778_consumed_token_ids": source["gdt777_consumed_token_ids"],
            "gdt778_fallback_replacement": 0, "gdt778_contextual_sharpening": 0,
            "gdt778_contextual_confirmation": 0, "gdt778_display_changed": 0,
            "gdt778_same_row_consumption_takeover": 0, "gdt778_new_unique_consumption": 0,
            "gdt778_positive_evidence": source["gdt777_positive_evidence"],
            "gdt778_counterevidence": source["gdt777_counterevidence"],
            "gdt778_dispatch_rule": "INHERITED_GDT777", "gdt778_scope_status": "INHERITED_GDT777",
            "gdt778_default_is_translation": 0, "gdt778_confirmed_lexeme": 0,
            "gdt778_confirmed_plaintext": 0, "gdt778_component_export_credit": 0,
        })
        span = by_occurrence.get(source["target_occurrence_id"])
        if span is not None:
            row.update({
                "gdt778_branch": "GDT778_EXACT_OL_PLUS_COMPLETE_WHOLE",
                "gdt778_default_de": span["new_gdt778_default_de"], "gdt778_renderer_contextual": 1,
                "gdt778_span_id": span["span_id"], "gdt778_exact_whole": span["right_surface"],
                "gdt778_confidence": span["confidence"], "gdt778_consumed_token_count": 1,
                "gdt778_consumed_token_ids": span["gdt778_consumed_token_id"],
                "gdt778_fallback_replacement": span["fallback_replacement"],
                "gdt778_contextual_sharpening": span["contextual_sharpening"],
                "gdt778_contextual_confirmation": span["contextual_confirmation"],
                "gdt778_display_changed": span["display_changed"],
                "gdt778_same_row_consumption_takeover": span["same_row_inherited_consumption_takeover"],
                "gdt778_new_unique_consumption": span["new_unique_consumption"],
                "gdt778_positive_evidence": span["positive_evidence"],
                "gdt778_counterevidence": span["counterevidence"],
                "gdt778_dispatch_rule": span["selection_rule"], "gdt778_scope_status": span["scope_status"],
            })
        assert RETIRED_SELECTED_RE.search(str(row["gdt778_default_de"])) is None
        output.append(row)

    owners: dict[str, str] = {}
    for row in output:
        value = str(row["gdt778_consumed_token_ids"])
        if value == "NONE":
            continue
        for token_id in value.split("|"):
            assert token_id not in owners, (token_id, owners.get(token_id), row["target_occurrence_id"])
            owners[token_id] = str(row["target_occurrence_id"])
    assert len(output) == 376
    assert sum(int(row["gdt778_renderer_contextual"]) for row in output) == 195
    assert sum(1 - int(row["gdt778_renderer_contextual"]) for row in output) == 181
    assert sum(int(row["gdt778_fallback_replacement"]) for row in output) == 32
    assert sum(int(row["gdt778_contextual_sharpening"]) for row in output) == 5
    assert sum(int(row["gdt778_contextual_confirmation"]) for row in output) == 2
    assert sum(int(row["gdt778_display_changed"]) for row in output) == 37
    assert sum(int(row["gdt778_same_row_consumption_takeover"]) for row in output) == 4
    assert sum(int(row["gdt778_new_unique_consumption"]) for row in output) == 35
    assert len(owners) == 155
    return output, owners


def build_registry(specs: Mapping[str, Mapping[str, str]], provenance: Sequence[Mapping[str, object]],
                   raw_counts: Mapping[str, int], exact_counts: Mapping[str, int],
                   spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    prov = {str(row["right_surface"]): row for row in provenance}
    output: list[dict[str, object]] = []
    for form in sorted(specs):
        spec = specs[form]
        local = [row for row in spans if row["right_surface"] == form]
        output.append({
            "right_surface": form, "selected_default_de": spec["selected_default_de"],
            "alternate_1_de": spec["alternate_1_de"], "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "provenance_path": spec["provenance_path"],
            "promotion_status": spec["promotion_status"], "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"], "local_raw_occurrences": raw_counts[form],
            "local_reader_exact_occurrences": exact_counts[form],
            "local_nonexact_exclusions": raw_counts[form] - exact_counts[form],
            "fallback_replacements": sum(int(row["fallback_replacement"]) for row in local),
            "contextual_sharpenings": sum(int(row["contextual_sharpening"]) for row in local),
            "contextual_confirmations": sum(int(row["contextual_confirmation"]) for row in local),
            "actual_display_changes": sum(int(row["display_changed"]) for row in local),
            "source_kind": prov[form]["source_kind"], "source_status": prov[form]["source_status"],
            "scope_status": "EXACT_OL_PLUS_COMPLETE_WHOLE_OCCURRENCES_ONLY",
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    assert len(output) == 29
    return output


def build_dictionary(registry: Sequence[Mapping[str, object]], spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in registry:
        form = str(source["right_surface"])
        local = [row for row in spans if row["right_surface"] == form]
        output.append({
            "entry": form, "preferred_gdt778_default_de": source["selected_default_de"],
            "confidence": source["confidence"], "alternate_1_de": source["alternate_1_de"],
            "alternate_2_de": source["alternate_2_de"], "reader_exact_ol_contexts": len(local),
            "rendered_displays_de": " || ".join(sorted({str(row["new_gdt778_default_de"]) for row in local})),
            "fallback_replacements": source["fallback_replacements"],
            "contextual_sharpenings": source["contextual_sharpenings"],
            "contextual_confirmations": source["contextual_confirmations"],
            "positive_evidence": source["positive_evidence"], "counterevidence": source["counterevidence"],
            "provenance_path": source["provenance_path"], "promotion_status": source["promotion_status"],
            "scope": "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY__NO_SUBSTRING_EXPORT",
            "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(output) == 29
    return output


def render_line(locus: str, written_line: str, renderer_by_position: Mapping[tuple[str, int], Mapping[str, object]],
                generation: str) -> str:
    assert generation in {"gdt777", "gdt778"}
    tokens = written_line.split()
    rendered: list[str] = []
    consumed: set[int] = set()
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
    old_by_position = {(row["locus"], int(row["ordinal"])): row for row in base}
    new_by_position = {(str(row["locus"]), int(row["ordinal"])): row for row in renderer}
    changed = [row for row in spans if int(row["display_changed"])]
    output: list[dict[str, object]] = []
    for number, span in enumerate(changed, 1):
        locus, written = str(span["locus"]), str(span["written_line_eva"])
        old_patch = render_line(locus, written, old_by_position, "gdt777")
        new_patch = render_line(locus, written, new_by_position, "gdt778")
        assert old_patch != new_patch
        output.append({
            "passage_patch_id": f"G778-P{number:03d}", "span_id": span["span_id"],
            "target_occurrence_id": span["target_occurrence_id"], "page": span["page"],
            "physical_folio": span["physical_folio"], "locus": locus,
            "right_surface": span["right_surface"], "semantic_change_class": span["semantic_change_class"],
            "old_display_de": span["old_gdt777_default_de"], "new_display_de": span["new_gdt778_default_de"],
            "selected_whole_default_de": span["selected_whole_default_de"],
            "written_line_eva": written, "inherited_gdt777_patch_de": old_patch,
            "gdt778_practical_patch_de": new_patch,
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(output) == 37
    assert Counter(row["semantic_change_class"] for row in output) == Counter({
        "FALLBACK_REPLACEMENT": 32, "CONTEXTUAL_SHARPENING": 5,
    })
    return output


def make_packet(spans: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        edge_id = f"G778-E{number:03d}"
        packet.append({
            "edge_id": edge_id, "batch_id": "GDT778_EXACT_OL_COMPLETE_WHOLE", "page": span["page"],
            "physical_folio": span["physical_folio"], "diagram_unit_id": f"LINE:{span['locus']}",
            "pivot_visual_id": f"TOKEN:{span['locus']}:{span['ol_ordinal']}",
            "pivot_locus": f"{span['locus']}@{span['ol_ordinal']}",
            "target_visual_id": f"TOKEN:{span['locus']}:{span['right_ordinal']}",
            "target_locus": f"{span['locus']}@{span['right_ordinal']}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT777", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT778_RUNNER",
            "relation_reviewer": "GDT778_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION", "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": "GDT778_EXACT_OL_COMPLETE_WHOLE", "span_id": span["span_id"],
            "target_occurrence_id": span["target_occurrence_id"], "page": span["page"],
            "physical_folio": span["physical_folio"], "locus": span["locus"],
            "ol_ordinal": span["ol_ordinal"], "right_ordinal": span["right_ordinal"],
            "right_surface": span["right_surface"], "written_span_eva": span["written_span_eva"],
            "selection_rule": span["selection_rule"], "score_eligible": 0,
            "component_export_credit": 0,
        })
    assert len(packet) == len(crosswalk) == 39
    return packet, crosswalk


def build_report(result: Mapping[str, object], spans: Sequence[Mapping[str, object]]) -> str:
    examples: list[str] = []
    for locus in ("f104v.33", "f80v.35", "f78v.4", "f17v.18", "f78v.27"):
        row = next(item for item in spans if item["locus"] == locus)
        examples.append(
            f"- `{row['locus']}`: `{row['written_span_eva']}` — "
            f"`{row['old_gdt777_default_de']}` → **{row['new_gdt778_default_de']}** "
            f"(`{row['semantic_change_class']}`)."
        )
    return f"""# GDT778 — exakte Ganzwort-Promotion des alten Singleton-Decks nach `ol`

Status: `{result['status']}`.

## Ergebnis

Die occurrence-ID-freie Regel prüft alle 376 Positionen des finalen GDT777-
Renderers und nimmt **jedes** Vorkommen auf, dessen vollständiges rechtes Wort
im festen 29er-Deck steht und reader-exakt ist. Das ergibt **41** rohe
Kandidaten und **39** exakte `ol + Ganzwort`-Spannen auf **31** Seitenlabels
und **25** physischen Folios. Nur `keey` bei `G769-T0284` und `dal` bei
`G769-T0391` fallen wegen nicht-exakter rechter Lesung aus.

Von den 39 exakten Fällen ersetzen **32** den generischen Fallback. Fünf
vorhandene Strukturwerte werden tatsächlich konkreter: `ar` einmal, `kain`
zweimal und `chy` zweimal. Die zwei `chol`-Stellen bestätigen dagegen nur das
schon vorhandene `Zustand: trocken` und werden nicht als Verbesserung gezählt.
Damit steigt die kontextuelle Abdeckung **163→195**, während die Fallbacks
**213→181** fallen. Die Passage-Tabelle enthält genau die **37** wirklich
veränderten Anzeigen.

## Strukturtreue Komposition

{chr(10).join(examples)}

`und` und `Ansatz:` bleiben als geerbte Strukturrahmen sichtbar; das neue
Ganzwort wird darin ergänzt. Eine unveränderte `chol`-Bestätigung wird nicht
als semantische Schärfung umetikettiert.

## Bedeutungsbasis und Quellenkonflikt

Vier Werte (`ar`, `chor`, `chol`, `dair`) stützen sich auf spätere
Ganzwortbefunde. **24** weitere Werte werden bewusst neu aus den gebundenen
GDT736/GDT737-body-Kandidaten befördert: ausschließlich als vollständiges
rechtes Wort in einer exakten `ol X`-Spanne. Sie exportieren weder ein Präfix
noch einen body oder ein einzelnes EVA-Zeichen.

`ols` bleibt der explizite Sonderfall. GDT769 bietet nur einen schwachen
Maß-/Produktposten-Rivalen, während GDT772 formal `OLS_NULL` wählt. GDT778
setzt für Durchsatz den neuen lokalen C0-Default **Produktposten**; die ältere
Filtrat-/Abseihlesung ist verworfen und liefert dem neuen Wert keine Evidenz.

## Konsum und Grenze

Vier rechte Token (`chol` zweimal, `chy` zweimal) waren bereits im selben
Elternziel konsumiert und wechseln nur den Besitzer. Die übrigen 35 sind neu;
so steigt die eindeutige Gesamtmenge **120→155**. Es gibt keine Kollision mit
einem anderen Ziel.

Das GDT388-Paket enthält 39 rein deskriptive Textnachbarschaften und bleibt
`{result['relation_packet']['status']}`. Es wurden keine neuen Seiten, Bilder,
OCR, Transkriptionen, `f84`- oder `f84r`-Daten geöffnet. Die deutschen Werte
sind ersetzbare explorative Renderer-Defaults, keine Übersetzung oder
Lexemidentifikation.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()

    lock_count = verify_locks()
    specs = validate_specs(read_tsv(SPECS))
    base = read_tsv(G777_RENDERER)
    parent_result = json.loads(G777_RESULT.read_text(encoding="utf-8"))
    assert len(base) == 376
    assert sum(int(row["gdt777_renderer_contextual"]) for row in base) == 163
    assert parent_result["renderer"]["total_consumed_right_tokens"] == 120
    assert parent_result["renderer"]["fallbacks"] == 213
    spans, exclusions, raw_counts, exact_counts = build_cohort(base, specs)
    provenance = build_provenance(specs, raw_counts, exact_counts)
    registry = build_registry(specs, provenance, raw_counts, exact_counts, spans)
    renderer, owners = build_renderer(base, spans)
    dictionary = build_dictionary(registry, spans)
    passages = build_passages(base, renderer, spans)
    packet, crosswalk = make_packet(spans)

    outputs = [
        ("EXACT_WHOLE_29_REGISTRY.tsv", registry, list(registry[0])),
        ("GDT778_39_EXACT_WHOLE_ATLAS.tsv", spans, list(spans[0])),
        ("GDT778_EXACTNESS_EXCLUSIONS.tsv", exclusions, list(exclusions[0])),
        ("GDT778_PROVENANCE_SOURCE_CONFLICT_AUDIT.tsv", provenance, list(provenance[0])),
        ("GDT778_376_RENDERER.tsv", renderer, list(renderer[0])),
        ("GDT778_WORKING_DICTIONARY.tsv", dictionary, list(dictionary[0])),
        ("GDT778_PASSAGE_PATCHES.tsv", passages, list(passages[0])),
        ("GDT778_GDT388_RELATION_PACKET.tsv", packet, list(packet[0])),
        ("GDT778_RELATION_EDGE_CROSSWALK.tsv", crosswalk, list(crosswalk[0])),
    ]
    for name, rows, fields in outputs:
        write_tsv(artifacts / name, rows, fields)

    intake_done = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(artifacts / "GDT778_GDT388_RELATION_PACKET.tsv")],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    intake = json.loads(intake_done.stdout)
    assert intake == {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 39, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    result: dict[str, object] = {
        "experiment_id": "GDT778",
        "status": "PASS__39_EXACT_WHOLES__32_FALLBACK_REPLACEMENTS__5_SHARPENINGS__2_CONFIRMATIONS__195_CONTEXTUAL__155_CONSUMED__NO_COMPONENT_EXPORT",
        "source_locks": lock_count, "inherited_guard": parent_result["guard"],
        "cohort": {
            "renderer_rows": 376, "deck_forms": 29, "raw_candidates": 41,
            "reader_exact_spans": 39, "exactness_exclusions": 2,
            "page_labels": 31, "physical_folios": 25, "loci": 39,
        },
        "changes": {
            "fallback_replacements": 32, "contextual_sharpenings": 5,
            "contextual_confirmations": 2, "actual_display_changes": 37,
            "passage_patches": len(passages),
        },
        "renderer": {
            "gdt777_contextual": 163, "gdt778_contextual": 195,
            "gdt777_fallbacks": 213, "gdt778_fallbacks": 181,
        },
        "consumption": {
            "gdt777_unique_right_tokens": 120, "gdt778_selected_right_tokens": 39,
            "same_row_inherited_takeovers": 4, "new_unique_right_tokens": 35,
            "total_unique_right_tokens": len(owners), "cross_row_collisions": 0,
        },
        "source_model": {
            "later_complete_whole_defaults": 4, "new_body_candidate_promotions": 24,
            "explicit_source_conflicts": 1, "ols_selected_default_de": "Produktposten",
            "ols_confidence": "C0", "ols_formal_prior": "OLS_NULL",
            "older_filtrate_or_straining_reading_selected": False,
        },
        "dictionary_rows": len(dictionary), "relation_packet": intake,
        "retired_literal_patient_leaks_in_selected_defaults": 0,
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0,
        "sealed_pages_accessed": 0,
        "claim_ceiling": "Replaceable exact ol plus complete-whole meanings only; no EVA component, lexeme, language, plaintext, specific recipe, substance, disease, or treatment.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, spans), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
