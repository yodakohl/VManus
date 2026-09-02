#!/usr/bin/env python3
"""Build the V99R6 integrated 32,339-cell cache and practical unit reader."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt733_v99r6_integrated_legacy_grade_cache_renderer"
SRC, ART = EXP / "src", EXP / "artifacts"
G664 = ROOT / "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts"
G665 = ROOT / "experiments/yolo/gdt665_one_hundred_forty_eight_residual_family_completion/artifacts"
G671 = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts"
G696 = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
G730 = ROOT / "experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/artifacts"
G731 = ROOT / "experiments/yolo/gdt731_v99r4_occurrence_passage_impact"
G732 = ROOT / "experiments/yolo/gdt732_v99r5_grade_frame_spoken_renderer/artifacts"

LINES = G671 / "ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
PAGES = G671 / "PAGE_ALLOWLIST.tsv"
CONTEXTS = G727 / "V99_479_CONTEXT_REALIZATIONS.tsv"
V99_UNITS = G727 / "V99_471_PRACTICAL_RENDERED_UNITS.tsv"
DICTIONARY = G730 / "V99R4_COMPLETE_WORD_CONFIDENCE.tsv"
G732_OVERLAY = G732 / "V99R5_2431_LICENSED_POSITION_OVERLAY.tsv"
G732_RESIDUAL = G732 / "V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv"
PRECEDENCE = SRC / "INTEGRATION_PRECEDENCE.tsv"
LEGACY_POLICY = SRC / "LEGACY_GRADE_TEMPLATE_POLICY.tsv"
SPECIAL_SPECS = SRC / "SPECIAL_EXACT_GRADE_SPECS.tsv"
MERGE_SPECS = SRC / "ALIAS_MERGE_SPECS.tsv"
PUNCTUATION_SPECS = SRC / "STRUCTURAL_PUNCTUATION_SPECS.tsv"
BLOCKER_RULES = G731 / "src/PRACTICAL_BLOCKER_RULES.tsv"

PARITY_PATHS = (
    G696 / "V69_51_LINE_RELATION_OVERLAY.tsv",
    G696 / "V69_479_TOKEN_RELATION_OVERLAY.tsv",
    G696 / "GDT696_V69_LOCAL_OBJECT_CARRY_READER.md",
    G727 / "V99_324_ACTIVE_LEXICAL_READINGS.tsv",
    G727 / "V99_479_CONTEXT_REALIZATIONS.tsv",
    G727 / "V99_471_PRACTICAL_RENDERED_UNITS.tsv",
    G727 / "V99_51_PRACTICAL_LINE_READER.tsv",
    G727 / "GDT727_V99_51_LINE_WORKING_READER.md",
    G730 / "V99R4_COMPLETE_WORD_CONFIDENCE.tsv",
    G732 / "V99R5_COMPLETE_SPOKEN_RENDERER.tsv",
    G732 / "V99R5_2431_LICENSED_POSITION_OVERLAY.tsv",
    G732 / "V99R5_4752_RESIDUAL_CACHE_GRADE_FRAME_CELLS.tsv",
)

STATUS = (
    "PASS_32339_CELL_CURRENT_CACHE__479_EXACT_CONTEXTS__2431_GDT732_SPOKEN__"
    "6866_ADDITIONAL_UNCONDITIONAL_GLOBALS__4692_LEGACY_CONTEXT_GRADE_RENDERS__"
    "52_SUPERSEDED_EXACT_V48_CELLS__8_CURRENT_V99_BOUND_SPANS__8_LEGACY_ALIAS_"
    "MERGES__4_STRUCTURAL_PUNCTUATION_ATTACHMENTS__7132_GRADE_CELLS_SPOKEN__"
    "ZERO_AUDIBLE_GRADE_FRAMES__32319_PRACTICAL_UNITS__NO_DEBUG_TEXT_IN_"
    "PRACTICAL_OUTPUT__NO_DOUBLED_SEPARATORS__NO_NEW_MEANING_NO_NEW_PAGE"
)

GRADE_RX = re.compile(r"(?:Grades|Gradanfang|Gradmitte|Gradende)", re.IGNORECASE)
UNKNOWN_RX = re.compile(r"\[[^]]+:\?]")
NOMINAL_VERB_RX = re.compile(
    r"(?<!\w)(?:miss|nimm|nehme|gib|füge|setze|trockne|erhitze|kühle|"
    r"weiche|schließe|fülle|trenne|reibe|bringe)(?!\w)", re.IGNORECASE,
)
MODALITY_SOURCE = {
    "HEISS": re.compile(r"heiß", re.IGNORECASE),
    "KALT": re.compile(r"kalt", re.IGNORECASE),
    "TROCKEN": re.compile(r"trocken", re.IGNORECASE),
    "FEUCHT": re.compile(r"feucht", re.IGNORECASE),
}
MODALITY_OUTPUT = {
    "HEISS": re.compile(r"(?:heiß|erhitz)", re.IGNORECASE),
    "KALT": re.compile(r"(?:kalt|abgekühl)", re.IGNORECASE),
    "TROCKEN": re.compile(r"(?:trocken|getrockn)", re.IGNORECASE),
    "FEUCHT": re.compile(r"(?:feucht|angefeucht)", re.IGNORECASE),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    data = list(rows)
    fields = fields or (list(data[0]) if data else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in data:
            writer.writerow({field: row.get(field, "") for field in fields})


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_for(row: dict[str, str], ordinal_field: str = "token_ordinal") -> tuple[str, str, int, str]:
    return row["page"], row["locus"], int(row[ordinal_field]), row["surface"]


def ordered_modalities(text: str, patterns: dict[str, re.Pattern[str]]) -> list[str]:
    hits: list[tuple[int, str]] = []
    for code, pattern in patterns.items():
        hits.extend((match.start(), code) for match in pattern.finditer(text))
    output: list[str] = []
    for _, code in sorted(hits):
        if code not in output:
            output.append(code)
    return output


def closure_counts(text: str) -> tuple[int, int]:
    return (
        len(re.findall(r"(?<!\w)abgeschlossen(?!\w)", text, re.IGNORECASE)),
        len(re.findall(r"(?<!\w)fertig(?!\w)", text, re.IGNORECASE)),
    )


def practicalize(units: list[str]) -> str:
    normalized = [re.sub(r"\s+", " ", unit).strip() for unit in units]
    text = ""
    for unit in normalized:
        if not text:
            text = unit
        elif unit.startswith((".", ";", ":", ",")):
            # A connective such as "; hierzu:" already owns its boundary.
            text += unit
        elif text.endswith((".", ";", ":")):
            text += " " + unit
        else:
            text += "; " + unit
    return re.sub(r";{2,}", ";", text).strip()


def authority_fields(dictionary_row: dict[str, str] | None) -> dict[str, str]:
    if dictionary_row is None:
        return {
            "authority_reading_id": "NONE",
            "authority_score_0_100_not_probability": "NA",
            "authority_confidence_level": "NA",
            "authority_semantic_scope": "OCCURRENCE_LOCAL_OR_INHERITED",
            "authority_global_export_scope": "NONE",
        }
    return {
        "authority_reading_id": dictionary_row["reading_id"],
        "authority_score_0_100_not_probability": dictionary_row[
            "working_model_score_0_100_not_probability"
        ],
        "authority_confidence_level": dictionary_row["working_model_level"],
        "authority_semantic_scope": dictionary_row["semantic_scope"],
        "authority_global_export_scope": dictionary_row["global_export_scope"],
    }


def load_and_validate_specs(
    residual_rows: list[dict[str, str]], contexts: list[dict[str, str]],
) -> tuple[
    dict[str, dict[str, str]], dict[tuple[str, str, int, str], dict[str, str]],
    list[dict[str, str]], list[dict[str, str]],
]:
    precedence = read_tsv(PRECEDENCE)
    assert [int(row["priority"]) for row in precedence] == list(range(1, 9))
    assert sum(int(row["expected_cell_count"]) for row in precedence) == 32339

    policy = read_tsv(LEGACY_POLICY)
    assert len(policy) == 52 and len({row["old_v48_context_de"] for row in policy}) == 52
    assert sum(int(row["expected_occurrences"]) for row in policy) == 4692
    policy_by_old = {row["old_v48_context_de"]: row for row in policy}
    legacy = [
        row for row in residual_rows if row["residual_class"] in {
            "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS",
            "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE",
        }
    ]
    assert len(legacy) == 4692
    assert Counter(row["residual_gloss_de"] for row in legacy) == Counter({
        row["old_v48_context_de"]: int(row["expected_occurrences"]) for row in policy
    })
    for row in policy:
        assert GRADE_RX.search(row["old_v48_context_de"])
        assert not GRADE_RX.search(row["new_spoken_context_de"])
        assert ordered_modalities(row["old_v48_context_de"], MODALITY_SOURCE) == ordered_modalities(
            row["new_spoken_context_de"], MODALITY_OUTPUT
        )
        assert closure_counts(row["old_v48_context_de"]) == closure_counts(
            row["new_spoken_context_de"]
        )
        # Permit the intended result-state form "abgekühlt", but reject the
        # bare process wording "gekühlt" that the policy explicitly replaced.
        assert not re.search(r"(?<!ab)gekühlt", row["new_spoken_context_de"], re.IGNORECASE)
        assert not re.search(r"(?:Anfangs|Mittel|End)stufe abgeschlossen", row["new_spoken_context_de"])

    special_rows = read_tsv(SPECIAL_SPECS)
    assert len(special_rows) == 1
    special_by_key = {key_for(row): row for row in special_rows}
    context_by_key = {key_for(row): row for row in contexts}
    special = special_rows[0]
    context = context_by_key[key_for(special)]
    assert context["position_id"] == special["position_id"]
    assert context["v99_reading_id"] == special["reading_id"]
    assert context["v99_context_realization_de"] == special["expected_v99_context_de"]
    assert GRADE_RX.search(special["expected_v99_context_de"])
    assert not GRADE_RX.search(special["new_spoken_render_de"])

    merge_rows = read_tsv(MERGE_SPECS)
    assert len(merge_rows) == 8 and len({row["spec_id"] for row in merge_rows}) == 8
    assert len({(row["locus"], row["span_start_ordinal"]) for row in merge_rows}) == 8
    for row in merge_rows:
        assert int(row["span_end_ordinal"]) == int(row["span_start_ordinal"]) + 1
        assert GRADE_RX.search(row["old_anchor_v48_de"])
        assert not GRADE_RX.search(row["new_spoken_unit_de"])
        assert ordered_modalities(row["old_anchor_v48_de"], MODALITY_SOURCE) == ordered_modalities(
            row["new_spoken_unit_de"], MODALITY_OUTPUT
        )
        assert closure_counts(row["old_anchor_v48_de"]) == closure_counts(row["new_spoken_unit_de"])
        if row["unit_kind"] == "NOMINAL_STATE":
            assert not NOMINAL_VERB_RX.search(row["new_spoken_unit_de"])
        else:
            assert row["unit_kind"] == "ACTION" and row["source_card_id"] == "G665-C022"
            assert row["new_spoken_unit_de"].startswith("miss eine Handvoll")
            assert row["new_spoken_unit_de"].endswith("für den Ansatz ab")
    return policy_by_old, special_by_key, merge_rows, precedence


def build_practical_unit_plan(
    contexts: list[dict[str, str]], merge_rows: list[dict[str, str]],
) -> tuple[
    dict[tuple[str, str, int, str], dict[str, str]],
    list[dict[str, str]], list[dict[str, str]],
]:
    """Unify inherited V99 spans, legacy aliases and punctuation attachments."""
    contexts_by_id = {row["position_id"]: row for row in contexts}
    assert len(contexts_by_id) == 479
    unit_rows = read_tsv(V99_UNITS)
    assert len(unit_rows) == 471
    current_spans = [row for row in unit_rows if row["source_kind"] == "BOUND_SPAN"]
    assert len(current_spans) == 8
    punctuation_rows = read_tsv(PUNCTUATION_SPECS)
    assert len(punctuation_rows) == 4

    plan: dict[tuple[str, str, int, str], dict[str, str]] = {}

    for unit in current_spans:
        position_ids = unit["consumed_position_ids"].split("|")
        assert len(position_ids) == int(unit["consumed_position_count"]) == 2
        left, right = (contexts_by_id[position_id] for position_id in position_ids)
        assert left["page"] == right["page"] == unit["page"]
        assert left["locus"] == right["locus"] == unit["locus"]
        assert int(right["token_ordinal"]) == int(left["token_ordinal"]) + 1
        assert unit["source_surfaces"] == f"{left['surface']}|{right['surface']}"
        assert unit["v99_context_inputs_de"] == (
            f"{left['v99_context_realization_de']} || {right['v99_context_realization_de']}"
        )
        assert unit["rendered_text_de"]
        assert not GRADE_RX.search(unit["rendered_text_de"])
        assert "keine Einzelausgabe" not in unit["rendered_text_de"]
        assert "Gesamtspan" not in unit["rendered_text_de"]
        for role, context in zip(("SPAN_START_EMITS_ONCE", "SPAN_COMPANION_SUPPRESSED"), (left, right), strict=True):
            key = key_for(context)
            assert key not in plan
            plan[key] = {
                "practical_unit_layer": "CURRENT_V99_BOUND_SPAN",
                "practical_unit_id": unit["source_ref"],
                "practical_unit_role": role,
                "practical_render_once_de": unit["rendered_text_de"],
                "practical_source_positions": unit["consumed_position_ids"],
                "practical_source_surfaces": unit["source_surfaces"],
            }

    for spec in merge_rows:
        start, end = int(spec["span_start_ordinal"]), int(spec["span_end_ordinal"])
        anchor = int(spec["anchor_ordinal"])
        start_surface = spec["anchor_surface"] if anchor == start else spec["companion_surface"]
        end_surface = spec["anchor_surface"] if anchor == end else spec["companion_surface"]
        for ordinal, surface, role in (
            (start, start_surface, "SPAN_START_EMITS_ONCE"),
            (end, end_surface, "SPAN_COMPANION_SUPPRESSED"),
        ):
            key = (spec["page"], spec["locus"], ordinal, surface)
            assert key not in plan
            plan[key] = {
                "practical_unit_layer": "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE",
                "practical_unit_id": spec["spec_id"],
                "practical_unit_role": role,
                "practical_render_once_de": spec["new_spoken_unit_de"],
                "practical_source_positions": (
                    f"{spec['locus']}:{spec['span_start_ordinal']}|"
                    f"{spec['locus']}:{spec['span_end_ordinal']}"
                ),
                "practical_source_surfaces": f"{start_surface}|{end_surface}",
            }

    for spec in punctuation_rows:
        assert spec["attachment_direction"] == "PREVIOUS_UNIT"
        context = contexts_by_id[spec["position_id"]]
        key = key_for(context)
        assert key == key_for(spec)
        assert context["v99_context_realization_de"] == spec["punctuation"]
        assert spec["punctuation"] in {";", "."}
        assert key not in plan
        plan[key] = {
            "practical_unit_layer": "STRUCTURAL_PUNCTUATION_ATTACHMENT",
            "practical_unit_id": spec["spec_id"],
            "practical_unit_role": "ATTACH_PREVIOUS_NO_UNIT",
            "practical_render_once_de": spec["punctuation"],
            "practical_source_positions": spec["position_id"],
            "practical_source_surfaces": spec["surface"],
        }

    assert len(plan) == 36
    return plan, current_spans, punctuation_rows


def build_cell_register(
    lines: list[dict[str, str]], dictionary: list[dict[str, str]],
    contexts: list[dict[str, str]], g732_overlay: list[dict[str, str]],
    residual_rows: list[dict[str, str]], policy_by_old: dict[str, dict[str, str]],
    special_by_key: dict[tuple[str, str, int, str], dict[str, str]],
    merge_rows: list[dict[str, str]], precedence: list[dict[str, str]],
    practical_unit_plan: dict[tuple[str, str, int, str], dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    dictionary_by_id = {row["reading_id"]: row for row in dictionary}
    assert len(dictionary_by_id) == len(dictionary) == 1586
    context_by_key = {key_for(row): row for row in contexts}
    overlay_by_key = {key_for(row): row for row in g732_overlay}
    residual_by_key = {key_for(row): row for row in residual_rows}
    assert len(context_by_key) == 479 and len(overlay_by_key) == 2431
    assert len(residual_by_key) == 4752

    g732_global_surfaces = {
        row["surface"] for row in g732_overlay if row["dispatch_scope"] == "GLOBAL_SURFACE"
    }
    assert len(g732_global_surfaces) == 162
    unconditional = {
        row["surface"]: row for row in dictionary
        if row["current_layer"] == "GLOBAL_V48_DEFAULT"
        and row["unconditional_global_export_allowed"] == "1"
        and row["surface"] not in g732_global_surfaces
    }
    assert len(unconditional) == 1021
    merge_by_anchor = {
        (row["page"], row["locus"], int(row["anchor_ordinal"]), row["anchor_surface"]): row
        for row in merge_rows
    }

    expected_counts = {
        row["integration_class"]: int(row["expected_cell_count"]) for row in precedence
    }
    records: list[dict[str, Any]] = []
    by_locus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    class_counts = Counter()
    additional_global_counts = Counter()

    for line in lines:
        tokens = line["zl3b_line"].split()
        inherited_cells = line["token_glosses_de"].split(" | ")
        assert len(tokens) == len(inherited_cells) == int(line["token_count"]), line["locus"]
        for ordinal, (surface, inherited) in enumerate(zip(tokens, inherited_cells, strict=True), 1):
            key = (line["page"], line["locus"], ordinal, surface)
            context = context_by_key.get(key)
            overlay = overlay_by_key.get(key)
            residual = residual_by_key.get(key)
            dictionary_row: dict[str, str] | None = None
            grade_policy_id = "NONE"
            formal_stage = workflow_closure = modality_class = "NONE"

            if context is not None:
                dictionary_row = dictionary_by_id[context["v99_reading_id"]]
                semantic = context["v99_context_realization_de"]
                authority = context["position_id"]
                if overlay is not None:
                    integration_class = "V99_EXACT_CONTEXT_GDT732_SPOKEN"
                    assert overlay["dispatch_scope"] == "ACTIVE_EXACT_POSITION"
                    assert overlay["active_position_id"] == context["position_id"]
                    assert overlay["old_v99r4_meaning_de"] == semantic
                    final = overlay["new_v99r5_spoken_render_de"]
                    grade_policy_id = f"GDT732:{overlay['renderer_mode']}"
                    formal_stage = overlay["formal_stage_sequence"]
                    workflow_closure = overlay["workflow_closure"]
                    modality_class = overlay["modality_class"]
                elif residual is not None:
                    integration_class = "V99_EXACT_CONTEXT_SUPERSEDES_V48_GRADE"
                    assert residual["residual_class"] == (
                        "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL"
                    )
                    special = special_by_key.get(key)
                    if special is not None:
                        assert special["expected_v48_gloss_de"] == inherited
                        assert special["expected_v99_context_de"] == semantic
                        final = special["new_spoken_render_de"]
                        grade_policy_id = special["spec_id"]
                        formal_stage = special["formal_stage_sequence"]
                        workflow_closure = special["workflow_closure"]
                        modality_class = special["modality_class"]
                    else:
                        final = semantic
                else:
                    integration_class = "V99_EXACT_CONTEXT_OTHER"
                    final = semantic
            elif overlay is not None:
                integration_class = "GDT732_GLOBAL_SPOKEN_OVERLAY"
                assert overlay["dispatch_scope"] == "GLOBAL_SURFACE"
                dictionary_row = dictionary_by_id[overlay["reading_id"]]
                semantic = overlay["old_v99r4_meaning_de"]
                final = overlay["new_v99r5_spoken_render_de"]
                authority = overlay["reading_id"]
                grade_policy_id = f"GDT732:{overlay['renderer_mode']}"
                formal_stage = overlay["formal_stage_sequence"]
                workflow_closure = overlay["workflow_closure"]
                modality_class = overlay["modality_class"]
            elif residual is not None and residual["residual_class"] in {
                "TARGET_ACTIVE_SURFACE_OUTSIDE_30_EXACT_POSITIONS",
                "OTHER_ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE",
            }:
                integration_class = "ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE_LEGACY"
                semantic = inherited
                policy = policy_by_old[inherited]
                final = policy["new_spoken_context_de"]
                authority = residual["residual_id"]
                grade_policy_id = policy["template_id"]
                formal_stage = policy["formal_stage"]
                workflow_closure = policy["workflow_closure"]
                modality_class = policy["modality_class"]
            elif residual is not None:
                integration_class = "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
                assert residual["residual_class"] == "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
                spec = merge_by_anchor[key]
                assert spec["old_anchor_v48_de"] == inherited
                semantic = inherited
                final = spec["new_spoken_unit_de"]
                authority = spec["source_card_id"]
                grade_policy_id = spec["spec_id"]
                formal_stage = spec["formal_stage"]
                workflow_closure = spec["workflow_closure"]
                modality_class = spec["modality_class"]
            elif surface in unconditional:
                integration_class = "ADDITIONAL_UNCONDITIONAL_V99R4_GLOBAL"
                dictionary_row = unconditional[surface]
                semantic = dictionary_row["working_meaning_de"]
                final = semantic
                authority = dictionary_row["reading_id"]
                additional_global_counts[surface] += 1
            else:
                integration_class = "INHERITED_OTHER"
                semantic = final = inherited
                authority = "GDT671_V48_CACHE_CELL"

            assert final
            fields = authority_fields(dictionary_row)
            practical_fields = practical_unit_plan.get(key, {
                "practical_unit_layer": "SINGLE_CELL_UNIT",
                "practical_unit_id": "SELF",
                "practical_unit_role": "EMIT_CELL_ONCE",
                "practical_render_once_de": final,
                "practical_source_positions": f"{line['locus']}:{ordinal}",
                "practical_source_surfaces": surface,
            })
            record: dict[str, Any] = {
                "cell_id": f"G733-C{len(records)+1:05d}",
                "page": line["page"], "locus": line["locus"], "token_ordinal": ordinal,
                "surface": surface, "inherited_v48_gloss_de": inherited,
                "current_semantic_value_de": semantic, "v99r6_spoken_cell_de": final,
                "integration_class": integration_class, "authority_id": authority,
                **fields,
                "grade_policy_id": grade_policy_id, "formal_stage": formal_stage,
                "workflow_closure": workflow_closure, "modality_class": modality_class,
                **practical_fields,
                "semantic_changed_from_v48": int(semantic != inherited),
                "spoken_changed_from_semantic": int(final != semantic),
                "final_changed_from_v48": int(final != inherited),
                "component_relation_credit": 0,
            }
            records.append(record)
            by_locus[line["locus"]].append(record)
            class_counts[integration_class] += 1

    assert len(records) == 32339
    assert class_counts == Counter(expected_counts)
    assert sum(additional_global_counts.values()) == 6866
    assert all(
        additional_global_counts[surface] == int(row["occurrence_count"])
        for surface, row in unconditional.items()
    )
    assert not any(GRADE_RX.search(str(row["v99r6_spoken_cell_de"])) for row in records)
    return records, by_locus


def validate_and_build_merge_audit(
    merge_rows: list[dict[str, str]], by_locus: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    cards_by_path: dict[str, dict[str, dict[str, str]]] = {}
    output: list[dict[str, Any]] = []
    occupied: set[tuple[str, int]] = set()
    for spec in merge_rows:
        source_path = ROOT / spec["source_artifact"]
        if spec["source_artifact"] not in cards_by_path:
            cards_by_path[spec["source_artifact"]] = {
                row["card_id"]: row for row in read_tsv(source_path)
            }
        card = cards_by_path[spec["source_artifact"]][spec["source_card_id"]]
        assert card["reader_merge_surface"] == spec["merged_surface"]
        assert card["working_render_de"] == spec["old_anchor_v48_de"]
        records = by_locus[spec["locus"]]
        start, end = int(spec["span_start_ordinal"]), int(spec["span_end_ordinal"])
        assert (spec["locus"], start) not in occupied and (spec["locus"], end) not in occupied
        occupied.update({(spec["locus"], start), (spec["locus"], end)})
        first, second = records[start - 1], records[end - 1]
        anchor = records[int(spec["anchor_ordinal"]) - 1]
        companion = second if int(spec["anchor_ordinal"]) == start else first
        assert anchor["surface"] == spec["anchor_surface"]
        assert companion["surface"] == spec["companion_surface"]
        assert anchor["inherited_v48_gloss_de"] == spec["old_anchor_v48_de"]
        assert companion["inherited_v48_gloss_de"] == spec["old_companion_v48_de"]
        assert first["surface"] + second["surface"] == spec["merged_surface"]
        output.append({
            **spec,
            "anchor_cell_id": anchor["cell_id"], "companion_cell_id": companion["cell_id"],
            "anchor_integration_class": anchor["integration_class"],
            "companion_integration_class": companion["integration_class"],
            "anchor_final_cell_de": anchor["v99r6_spoken_cell_de"],
            "companion_final_cell_de": companion["v99r6_spoken_cell_de"],
            "practical_unit_de": spec["new_spoken_unit_de"],
            "source_card_sha256": file_sha(source_path),
            "span_positions_consumed": 2, "practical_units_emitted": 1,
            "component_export_credit": 0,
        })
    assert len(occupied) == 16
    return output


def build_current_span_audit(
    current_spans: list[dict[str, str]], records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records_by_position = {
        str(row["authority_id"]): row for row in records
        if str(row["authority_id"]).startswith("P")
    }
    output: list[dict[str, Any]] = []
    occupied: set[str] = set()
    for unit in current_spans:
        position_ids = unit["consumed_position_ids"].split("|")
        assert len(position_ids) == 2 and not (set(position_ids) & occupied)
        occupied.update(position_ids)
        left, right = (records_by_position[position_id] for position_id in position_ids)
        assert left["practical_unit_role"] == "SPAN_START_EMITS_ONCE"
        assert right["practical_unit_role"] == "SPAN_COMPANION_SUPPRESSED"
        assert left["practical_unit_id"] == right["practical_unit_id"] == unit["source_ref"]
        assert left["practical_render_once_de"] == right["practical_render_once_de"] == unit["rendered_text_de"]
        output.append({
            **unit,
            "left_cell_id": left["cell_id"], "right_cell_id": right["cell_id"],
            "left_v99r6_cell_de": left["v99r6_spoken_cell_de"],
            "right_v99r6_cell_de": right["v99r6_spoken_cell_de"],
            "integrated_practical_unit_de": unit["rendered_text_de"],
            "debug_text_in_practical_unit": int(
                "keine Einzelausgabe" in unit["rendered_text_de"]
                or "Gesamtspan" in unit["rendered_text_de"]
            ),
            "span_positions_consumed": 2, "practical_units_emitted": 1,
            "component_export_credit": 0,
        })
    assert len(output) == 8 and len(occupied) == 16
    assert not any(int(row["debug_text_in_practical_unit"]) for row in output)
    return output


def build_punctuation_audit(
    punctuation_specs: list[dict[str, str]], records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records_by_position = {
        str(row["authority_id"]): row for row in records
        if str(row["authority_id"]).startswith("P")
    }
    output: list[dict[str, Any]] = []
    for spec in punctuation_specs:
        record = records_by_position[spec["position_id"]]
        assert record["practical_unit_layer"] == "STRUCTURAL_PUNCTUATION_ATTACHMENT"
        assert record["practical_unit_role"] == "ATTACH_PREVIOUS_NO_UNIT"
        assert record["v99r6_spoken_cell_de"] == spec["punctuation"]
        output.append({
            **spec, "cell_id": record["cell_id"],
            "integration_class": record["integration_class"],
            "cell_value_retained": 1, "independent_practical_unit_emitted": 0,
            "attachment_applied": 1, "component_export_credit": 0,
        })
    assert len(output) == 4
    return output


def build_line_register(
    lines: list[dict[str, str]], by_locus: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output: list[dict[str, Any]] = []
    total_units = 0
    for line in lines:
        records = by_locus[line["locus"]]
        units: list[str] = []
        spans: list[str] = []
        punctuation: list[str] = []
        current_span_count = legacy_span_count = 0
        grade_unit_ids = {
            (
                f"SPAN:{record['practical_unit_layer']}:{record['practical_unit_id']}"
                if record["practical_unit_layer"] in {
                    "CURRENT_V99_BOUND_SPAN", "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
                }
                else f"CELL:{record['locus']}:{record['token_ordinal']}"
            )
            for record in records
            if record["grade_policy_id"] != "NONE"
            and record["practical_unit_layer"] != "STRUCTURAL_PUNCTUATION_ATTACHMENT"
        }
        for index, record in enumerate(records):
            role = str(record["practical_unit_role"])
            layer = str(record["practical_unit_layer"])
            unit_id = str(record["practical_unit_id"])
            if role == "SPAN_START_EMITS_ONCE":
                assert index + 1 < len(records)
                companion = records[index + 1]
                assert companion["practical_unit_role"] == "SPAN_COMPANION_SUPPRESSED"
                assert companion["practical_unit_id"] == unit_id
                assert companion["practical_unit_layer"] == layer
                units.append(str(record["practical_render_once_de"]))
                spans.append(
                    f"{record['token_ordinal']}-{companion['token_ordinal']}:"
                    f"{record['practical_source_surfaces']}:{unit_id}:{layer}"
                )
                if layer == "CURRENT_V99_BOUND_SPAN":
                    current_span_count += 1
                else:
                    assert layer == "LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"
                    legacy_span_count += 1
            elif role == "SPAN_COMPANION_SUPPRESSED":
                assert index > 0
                previous = records[index - 1]
                assert previous["practical_unit_role"] == "SPAN_START_EMITS_ONCE"
                assert previous["practical_unit_id"] == unit_id
            elif role == "ATTACH_PREVIOUS_NO_UNIT":
                assert units
                mark = str(record["practical_render_once_de"])
                assert mark in {";", "."}
                if not units[-1].endswith(mark):
                    units[-1] += mark
                punctuation.append(f"{record['token_ordinal']}:{record['surface']}:{mark}:{unit_id}")
            else:
                assert role == "EMIT_CELL_ONCE" and layer == "SINGLE_CELL_UNIT"
                units.append(str(record["v99r6_spoken_cell_de"]))
        total_units += len(units)
        inherited = [str(row["inherited_v48_gloss_de"]) for row in records]
        semantic = [str(row["current_semantic_value_de"]) for row in records]
        final = [str(row["v99r6_spoken_cell_de"]) for row in records]
        changed = [str(row["token_ordinal"]) for row in records if int(row["final_changed_from_v48"])]
        grade_rendered = [str(row["token_ordinal"]) for row in records if row["grade_policy_id"] != "NONE"]
        output.append({
            "page": line["page"], "locus": line["locus"], "section": line["section"],
            "language": line["language"], "hand": line["hand"],
            "token_count": line["token_count"], "practical_unit_count": len(units),
            "changed_cell_count": len(changed),
            "semantic_changed_cell_count": sum(int(row["semantic_changed_from_v48"]) for row in records),
            "spoken_changed_cell_count": sum(int(row["spoken_changed_from_semantic"]) for row in records),
            "grade_rendered_cell_count": len(grade_rendered),
            "grade_rendered_practical_unit_count": len(grade_unit_ids),
            "merge_unit_count": len(spans),
            "current_v99_bound_span_unit_count": current_span_count,
            "legacy_alias_merge_unit_count": legacy_span_count,
            "structural_punctuation_attachment_count": len(punctuation),
            "unknown_cells_v48": sum(bool(UNKNOWN_RX.fullmatch(cell)) for cell in inherited),
            "unknown_cells_v99r6": sum(bool(UNKNOWN_RX.fullmatch(cell)) for cell in final),
            "grade_frame_cells_v48": sum(bool(GRADE_RX.search(cell)) for cell in inherited),
            "grade_frame_cells_v99r6": sum(bool(GRADE_RX.search(cell)) for cell in final),
            "changed_ordinals": "|".join(changed) or "NONE",
            "grade_rendered_ordinals": "|".join(grade_rendered) or "NONE",
            "merge_spans": " | ".join(spans) or "NONE",
            "structural_punctuation_attachments": " | ".join(punctuation) or "NONE",
            "integration_classes": " | ".join(str(row["integration_class"]) for row in records),
            "zl3b_line": line["zl3b_line"],
            "inherited_v48_token_glosses_de": " | ".join(inherited),
            "current_semantic_token_glosses_de": " | ".join(semantic),
            "v99r6_spoken_token_glosses_de": " | ".join(final),
            "v99r6_practical_units_de": " | ".join(units),
            "inherited_v48_render_de": practicalize(inherited),
            "v99r6_practical_render_de": practicalize(units),
        })
    assert len(output) == 4128 and total_units == 32319
    dense = sorted(
        output,
        key=lambda row: (
            -int(row["changed_cell_count"]), -int(row["grade_rendered_cell_count"]),
            int(row["unknown_cells_v99r6"]), row["locus"],
        ),
    )[:50]
    dense = [{"rank": rank, **row} for rank, row in enumerate(dense, 1)]
    return output, dense


def build_superseded_audit(
    records: list[dict[str, Any]], residual_rows: list[dict[str, str]],
    contexts: list[dict[str, str]], special_by_key: dict[tuple[str, str, int, str], dict[str, str]],
) -> list[dict[str, Any]]:
    record_by_key = {
        (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]): row
        for row in records
    }
    context_by_key = {key_for(row): row for row in contexts}
    residuals = [
        row for row in residual_rows
        if row["residual_class"] == "OTHER_ACTIVE_EXACT_POSITION_WITH_SUPERSEDED_V48_CELL"
    ]
    output: list[dict[str, Any]] = []
    for residual in residuals:
        key = key_for(residual)
        context, record = context_by_key[key], record_by_key[key]
        special = special_by_key.get(key)
        assert residual["current_v99_position_id"] == context["position_id"]
        assert residual["current_v99_reading_id"] == context["v99_reading_id"]
        assert residual["current_v99_context_realization_de"] == context["v99_context_realization_de"]
        output.append({
            "audit_id": f"G733-SX{len(output)+1:02d}",
            "page": residual["page"], "locus": residual["locus"],
            "token_ordinal": residual["token_ordinal"], "surface": residual["surface"],
            "position_id": context["position_id"], "reading_id": context["v99_reading_id"],
            "superseded_v48_gloss_de": residual["residual_gloss_de"],
            "current_v99_context_de": context["v99_context_realization_de"],
            "final_v99r6_spoken_de": record["v99r6_spoken_cell_de"],
            "special_grade_policy_id": special["spec_id"] if special else "NONE",
            "v48_grade_frame": int(bool(GRADE_RX.search(residual["residual_gloss_de"]))),
            "current_v99_grade_frame": int(bool(GRADE_RX.search(context["v99_context_realization_de"]))),
            "final_v99r6_grade_frame": int(bool(GRADE_RX.search(str(record["v99r6_spoken_cell_de"])))),
            "component_relation_credit": 0,
        })
    assert len(output) == 52
    assert sum(int(row["current_v99_grade_frame"]) for row in output) == 1
    assert sum(int(row["final_v99r6_grade_frame"]) for row in output) == 0
    return output


def build_class_summary(
    records: list[dict[str, Any]], precedence: list[dict[str, str]],
) -> list[dict[str, Any]]:
    expected = {row["integration_class"]: row for row in precedence}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["integration_class"])].append(record)
    output: list[dict[str, Any]] = []
    for class_name, spec in sorted(expected.items(), key=lambda item: int(item[1]["priority"])):
        rows = grouped[class_name]
        output.append({
            "priority": spec["priority"], "integration_class": class_name,
            "authority": spec["authority"], "expected_cell_count": spec["expected_cell_count"],
            "actual_cell_count": len(rows),
            "semantic_changes_from_v48": sum(int(row["semantic_changed_from_v48"]) for row in rows),
            "spoken_changes_from_semantic": sum(int(row["spoken_changed_from_semantic"]) for row in rows),
            "final_changes_from_v48": sum(int(row["final_changed_from_v48"]) for row in rows),
            "grade_cells_v48": sum(bool(GRADE_RX.search(str(row["inherited_v48_gloss_de"]))) for row in rows),
            "grade_cells_current_semantic": sum(bool(GRADE_RX.search(str(row["current_semantic_value_de"]))) for row in rows),
            "grade_cells_v99r6": sum(bool(GRADE_RX.search(str(row["v99r6_spoken_cell_de"]))) for row in rows),
            "change_rule": spec["change_rule"],
        })
    return output


def build_template_summary(
    records: list[dict[str, Any]], policy_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        if str(row["grade_policy_id"]).startswith("G733-T"):
            by_policy[str(row["grade_policy_id"])].append(row)
    output: list[dict[str, Any]] = []
    for policy in policy_rows:
        rows = by_policy[policy["template_id"]]
        output.append({
            **policy,
            "actual_occurrences": len(rows),
            "surface_count": len({row["surface"] for row in rows}),
            "locus_count": len({row["locus"] for row in rows}),
            "all_occurrences_outside_exact_scope": int(all(
                row["integration_class"] == "ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE_LEGACY"
                for row in rows
            )),
        })
    return output


def build_blocker_census(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules = read_tsv(BLOCKER_RULES)
    output: list[dict[str, Any]] = []
    for rule in rules:
        pattern = re.compile(rule["regex"], re.IGNORECASE)
        scope = rule["field_scope"]
        if scope == "working_meaning_de":
            before = [row for row in records if pattern.search(str(row["inherited_v48_gloss_de"]))]
            after = [row for row in records if pattern.search(str(row["v99r6_spoken_cell_de"]))]
        elif scope == "surface":
            before = after = [row for row in records if pattern.search(str(row["surface"]))]
        elif scope == "passage_cell_status":
            before = [
                row for row in records
                if pattern.search("UNKNOWN" if UNKNOWN_RX.fullmatch(str(row["inherited_v48_gloss_de"])) else "RESOLVED")
            ]
            after = [
                row for row in records
                if pattern.search("UNKNOWN" if UNKNOWN_RX.fullmatch(str(row["v99r6_spoken_cell_de"])) else "RESOLVED")
            ]
        else:
            raise AssertionError(scope)
        output.append({
            "priority": rule["priority"], "blocker_class": rule["blocker_class"],
            "field_scope": scope, "v48_before_cells": len(before),
            "v99r6_after_cells": len(after), "delta_after_minus_before": len(after) - len(before),
            "interpretation_de": rule["interpretation_de"],
        })
    grade = next(row for row in output if row["blocker_class"] == "GRADE_FRAME")
    assert int(grade["v99r6_after_cells"]) == 0
    return output


def build_quality_summary(records: list[dict[str, Any]], line_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rendered = [row for row in records if row["grade_policy_id"] != "NONE"]
    old_rendered = [str(row["current_semantic_value_de"]) for row in rendered]
    new_rendered = [str(row["v99r6_spoken_cell_de"]) for row in rendered]
    metrics: list[tuple[str, int | float, int | float, str]] = [
        ("cache_cells", 32339, 32339, "all token positions retained"),
        ("practical_units", 32339, 32319, "sixteen exact two-token spans emit once and four punctuation cells attach structurally"),
        ("bound_span_units", 0, 16, "eight inherited V99 spans plus eight legacy alias or merge spans"),
        ("punctuation_cells_emitted_as_independent_units", 4, 0, "four exact structural marks attach to the preceding unit"),
        ("debug_renderer_fragments_in_practical_output", 2, sum(
            bool(re.search(r"(?:keine Einzelausgabe|Gesamtspan)", str(row["v99r6_practical_render_de"])))
            for row in line_rows
        ), "bound-span diagnostics remain in token audit cells but are never spoken"),
        ("doubled_semicolon_separators_in_practical_output", 48, sum(
            bool(re.search(r";\s*;", str(row["v99r6_practical_render_de"])))
            for row in line_rows
        ), "a connective beginning with punctuation supplies its own boundary"),
        ("audible_grade_frame_cells", sum(bool(GRADE_RX.search(str(row["inherited_v48_gloss_de"]))) for row in records), 0, "full target-only V48 baseline to integrated spoken cache"),
        ("grade_cells_after_current_semantic_precedence", 0, sum(bool(GRADE_RX.search(str(row["current_semantic_value_de"]))) for row in records), "current semantics before spoken formatting"),
        ("grade_cells_spoken_by_gdt733_or_gdt732", 0, len(rendered), "formatting operations; not new meanings"),
        ("grade_affected_practical_units", 0, sum(int(row["grade_rendered_practical_unit_count"]) for row in line_rows), "multiple grade-bearing cells inside one bound span count once in practical output"),
        ("rendered_closure_markers", sum(sum(closure_counts(text)) for text in old_rendered), sum(sum(closure_counts(text)) for text in new_rendered), "closure preserved inside every spoken grade cell"),
        ("rendered_modality_mentions", sum(len(ordered_modalities(text, MODALITY_SOURCE)) for text in old_rendered), sum(len(ordered_modalities(text, MODALITY_OUTPUT)) for text in new_rendered), "heat cold dry moist polarity preserved"),
        ("unknown_cells", sum(bool(UNKNOWN_RX.fullmatch(str(row["inherited_v48_gloss_de"]))) for row in records), sum(bool(UNKNOWN_RX.fullmatch(str(row["v99r6_spoken_cell_de"]))) for row in records), "integration may install already licensed current values; no default invented for residual unknowns"),
        ("lines_with_grade_frames", sum(int(row["grade_frame_cells_v48"]) > 0 for row in line_rows), sum(int(row["grade_frame_cells_v99r6"]) > 0 for row in line_rows), "all 4,128 lines audited"),
    ]
    return [{
        "metric": name, "v48_or_pre_before": before, "v99r6_after": after,
        "delta_after_minus_before": after - before, "interpretation": note,
    } for name, before, after, note in metrics]


def build_parity() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for path in PARITY_PATHS:
        output.append({
            "source_artifact": str(path.relative_to(ROOT)), "sha256": file_sha(path),
            "gdt733_rewrite_count": 0, "parity_status": "BYTE_STABLE_INPUT_NOT_REWRITTEN",
        })
    assert len(output) == 12
    return output


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = [row["page"] for row in read_tsv(PAGES)]
    assert len(pages) == len(set(pages)) == 179
    assert not any(re.match(r"^f84(?:r|v|$)", page) for page in pages)
    lines = read_tsv(LINES)
    assert len(lines) == 4128 and sum(int(row["token_count"]) for row in lines) == 32339
    assert {row["page"] for row in lines} <= set(pages)
    dictionary = read_tsv(DICTIONARY)
    contexts = read_tsv(CONTEXTS)
    g732_overlay = read_tsv(G732_OVERLAY)
    residual_rows = read_tsv(G732_RESIDUAL)
    policy_by_old, special_by_key, merge_rows, precedence = load_and_validate_specs(
        residual_rows, contexts
    )
    practical_unit_plan, current_spans, punctuation_specs = build_practical_unit_plan(
        contexts, merge_rows
    )
    records, by_locus = build_cell_register(
        lines, dictionary, contexts, g732_overlay, residual_rows, policy_by_old,
        special_by_key, merge_rows, precedence, practical_unit_plan,
    )
    merge_audit = validate_and_build_merge_audit(merge_rows, by_locus)
    current_span_audit = build_current_span_audit(current_spans, records)
    punctuation_audit = build_punctuation_audit(punctuation_specs, records)
    line_rows, dense = build_line_register(lines, by_locus)
    superseded = build_superseded_audit(records, residual_rows, contexts, special_by_key)
    class_summary = build_class_summary(records, precedence)
    template_summary = build_template_summary(records, read_tsv(LEGACY_POLICY))
    blockers = build_blocker_census(records)
    quality = build_quality_summary(records, line_rows)
    parity = build_parity()

    write_tsv(ART / "V99R6_32339_CELL_REGISTER.tsv", records)
    write_tsv(ART / "V99R6_4128_INTEGRATED_LINE_READER.tsv", line_rows)
    write_tsv(ART / "V99R6_50_CHANGE_DENSE_PASSAGES.tsv", dense)
    write_tsv(ART / "V99R6_8_ALIAS_MERGE_AUDIT.tsv", merge_audit)
    write_tsv(ART / "V99R6_8_CURRENT_V99_BOUND_SPAN_AUDIT.tsv", current_span_audit)
    write_tsv(ART / "V99R6_4_PUNCTUATION_ATTACHMENT_AUDIT.tsv", punctuation_audit)
    write_tsv(ART / "V99R6_52_SUPERSEDED_EXACT_V48_AUDIT.tsv", superseded)
    write_tsv(ART / "V99R6_INTEGRATION_CLASS_SUMMARY.tsv", class_summary)
    write_tsv(ART / "V99R6_52_LEGACY_TEMPLATE_AUDIT.tsv", template_summary)
    write_tsv(ART / "V99R6_FULL_CACHE_BLOCKER_CENSUS.tsv", blockers)
    write_tsv(ART / "V99R6_RENDER_QUALITY_SUMMARY.tsv", quality)
    write_tsv(ART / "V99R6_INHERITED_ARTIFACT_PARITY.tsv", parity)

    reader = [
        "# GDT733 — 50 änderungsdichteste integrierte Cache-Passagen", "",
        "Die Rangfolge misst geänderte Zellen, nicht semantische Wichtigkeit oder Übersetzungswahrheit. Exakte V99-Kontexte schlagen geerbte V48-Zellen; Legacy-Gradwerte bleiben positionsgebunden.", "",
    ]
    for row in dense:
        reader.extend([
            f"## {row['rank']}. {row['locus']} ({row['changed_cell_count']} geänderte Zellen; {row['grade_rendered_cell_count']} Grad-Renderings)", "",
            f"Voynich: `{row['zl3b_line']}`", "",
            f"Klassen: {row['integration_classes']}", "",
            f"Merge-Spans: {row['merge_spans']}", "",
            f"Satzzeichen-Anschlüsse: {row['structural_punctuation_attachments']}", "",
            f"V48: {row['inherited_v48_render_de']}", "",
            f"V99R6: {row['v99r6_practical_render_de']}", "",
        ])
    (ART / "GDT733_V99R6_50_CHANGE_DENSE_READER.md").write_text(
        "\n".join(reader).rstrip() + "\n", encoding="utf-8"
    )

    class_count = Counter(str(row["integration_class"]) for row in records)
    result = {
        "experiment_id": "GDT733", "status": STATUS,
        "allowed_pages": 179, "cached_lines": 4128, "cache_cells": 32339,
        "practical_units": 32319, "exact_v99_contexts": 479,
        "v99_exact_context_gdt732_spoken": class_count["V99_EXACT_CONTEXT_GDT732_SPOKEN"],
        "v99_exact_context_supersedes_v48_grade": class_count["V99_EXACT_CONTEXT_SUPERSEDES_V48_GRADE"],
        "v99_exact_context_other": class_count["V99_EXACT_CONTEXT_OTHER"],
        "gdt732_global_spoken_positions": class_count["GDT732_GLOBAL_SPOKEN_OVERLAY"],
        "legacy_active_outside_exact_grade_positions": class_count["ACTIVE_SURFACE_OUTSIDE_EXACT_SCOPE_LEGACY"],
        "legacy_alias_merge_anchor_positions": class_count["LEGACY_CONTEXTUAL_ALIAS_OR_MERGE"],
        "additional_unconditional_v99r4_global_positions": class_count["ADDITIONAL_UNCONDITIONAL_V99R4_GLOBAL"],
        "inherited_other_positions": class_count["INHERITED_OTHER"],
        "legacy_grade_templates": 52, "superseded_exact_v48_grade_cells": 52,
        "superseded_exact_current_contexts_grade_free": 51,
        "special_exact_current_grade_renderings": 1,
        "current_v99_bound_spans": 8, "current_v99_bound_positions_consumed": 16,
        "legacy_alias_merge_spans": 8, "legacy_alias_merge_positions_consumed": 16,
        "all_bound_spans": 16, "all_bound_span_positions_consumed": 32,
        "structural_punctuation_tokens_attached": 4,
        "grade_cells_spoken": sum(row["grade_policy_id"] != "NONE" for row in records),
        "grade_affected_practical_units": sum(
            int(row["grade_rendered_practical_unit_count"]) for row in line_rows
        ),
        "audible_grade_frame_cells_after": sum(bool(GRADE_RX.search(str(row["v99r6_spoken_cell_de"]))) for row in records),
        "lines_with_audible_grade_frames_after": sum(int(row["grade_frame_cells_v99r6"]) > 0 for row in line_rows),
        "semantic_changes_from_v48": sum(int(row["semantic_changed_from_v48"]) for row in records),
        "spoken_changes_from_semantic": sum(int(row["spoken_changed_from_semantic"]) for row in records),
        "final_changes_from_v48": sum(int(row["final_changed_from_v48"]) for row in records),
        "component_relation_credit": 0, "dictionary_changes": 0,
        "score_changes": 0, "confidence_changes": 0, "evidence_changes": 0,
        "scope_changes": 0, "export_changes": 0, "new_pages": 0,
        "inherited_artifacts_byte_stable": len(PARITY_PATHS),
        "canonical_cell_register": str((ART / "V99R6_32339_CELL_REGISTER.tsv").relative_to(ROOT)),
        "canonical_line_reader": str((ART / "V99R6_4128_INTEGRATED_LINE_READER.tsv").relative_to(ROOT)),
        "claim_ceiling": "integrated current-cache renderer over existing V99R4/V99/GDT732 meanings; no plaintext or new meaning",
    }
    assert result["grade_cells_spoken"] == 7132
    assert result["audible_grade_frame_cells_after"] == 0
    assert not any(re.search(
        r"(?:keine Einzelausgabe|Gesamtspan)", str(row["v99r6_practical_render_de"])
    ) for row in line_rows)
    assert not any(re.search(
        r";\s*;", str(row["v99r6_practical_render_de"])
    ) for row in line_rows)
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
