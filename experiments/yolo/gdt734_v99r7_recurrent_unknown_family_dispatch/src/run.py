#!/usr/bin/env python3
"""Build the V99R7 active-whole repair and recurrent unknown-family reader."""
from __future__ import annotations

import csv
import hashlib
import json
import os
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
EXP = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch"
SRC = EXP / "src"
ART = Path(os.environ.get("VMANUS_GDT734_ARTIFACT_DIR", str(EXP / "artifacts")))
REPORT_PATH = Path(os.environ.get("VMANUS_GDT734_REPORT_PATH", str(EXP / "REPORT.md")))
G637 = ROOT / "experiments/yolo/gdt637_ladder_completion_one_unknown_passages/artifacts"
G678 = ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion/artifacts"
G730 = ROOT / "experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/artifacts"
G733 = ROOT / "experiments/yolo/gdt733_v99r6_integrated_legacy_grade_cache_renderer/artifacts"

BASE_CELLS = G733 / "V99R6_32339_CELL_REGISTER.tsv"
BASE_LINES = G733 / "V99R6_4128_INTEGRATED_LINE_READER.tsv"
DICTIONARY = G730 / "V99R4_COMPLETE_WORD_CONFIDENCE.tsv"
CANDIDATE_SPECS = SRC / "CANDIDATE_SPECS.tsv"
EDITORIAL_SPECS = SRC / "ACTIVE_WHOLE_EDITORIAL_SPECS.tsv"
ROLE_MATRIX_SPECS = SRC / "ROLE_MATRIX_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_MICROENTRY_SPECS.tsv"
BLOCKER_RULES = ROOT / "experiments/yolo/gdt731_v99r4_occurrence_passage_impact/src/PRACTICAL_BLOCKER_RULES.tsv"

PARITY_PATHS = (
    BASE_CELLS, BASE_LINES, G733 / "RESULT.json", DICTIONARY,
    G637 / "LADDER_16_HEAD_CELL_GRID.tsv", G678 / "TARGET_FAMILY_CARDS.tsv",
)

UNKNOWN_RX = re.compile(r"\[[^]]+:\?]")
GRADE_RX = re.compile(r"(?:Grades|Gradanfang|Gradmitte|Gradende)", re.IGNORECASE)
GENERIC_NONSENSE_RX = re.compile(
    r"(?:Arbeitsgut|Arbeitsitem|Arbeitszyklus|working material|work item|destination place)",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    data = list(rows)
    fields = fields or (list(data[0]) if data else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in data:
            writer.writerow({field: row.get(field, "") for field in fields})


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_unknown(value: str) -> bool:
    return bool(UNKNOWN_RX.fullmatch(value))


def score_level(score: int) -> str:
    if score < 20:
        return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"
    if score < 40:
        return "W1_WEAK_WORKING"
    if score < 60:
        return "W2_PROVISIONAL_WORKING"
    return "W3_SOLID_WORKING_THEORY"


def candidate_score(
    decision: str, prefix_score: int, suffix_score: int, occurrences: int,
) -> tuple[int, int, str]:
    """Score a whole from its weaker part, recurrence and semantic route.

    The score is an internal working-theory rank, never a probability. A
    unique visible cut earns no score by itself. Recurrence contributes two
    points per completed doubling. The route then limits what that recurrence
    may support: compositional wholes cap at W2, role-constrained wholes at W1,
    and semantically redundant splits become low W1 learned wholes.
    """
    base = min(prefix_score, suffix_score)
    recurrence_bonus = min(12, 2 * (occurrences.bit_length() - 1))
    if decision == "PROMOTE_COMPOSITIONAL_WHOLE":
        score = min(59, base + recurrence_bonus)
        formula = "MIN_COMPONENT_PLUS_RECURRENCE_CAP59"
    elif decision == "REVISE_ROLE_CONSTRAINED_WHOLE":
        score = min(39, max(20, base + recurrence_bonus - 5))
        formula = "MIN_COMPONENT_PLUS_RECURRENCE_MINUS5_CAP39"
    else:
        assert decision == "LEARNED_WHOLE_NO_COMPOSITIONAL_CREDIT"
        score = min(35, max(20, base + recurrence_bonus - 10))
        formula = "MIN_COMPONENT_PLUS_RECURRENCE_MINUS10_FLOOR20_CAP35"
    return score, recurrence_bonus, formula


def practicalize(units: list[str]) -> str:
    normalized = [re.sub(r"\s+", " ", unit).strip() for unit in units]
    text = ""
    for unit in normalized:
        if not text:
            text = unit
        elif unit.startswith((".", ";", ":", ",")):
            text += unit
        elif text.endswith((".", ";", ":")):
            text += " " + unit
        else:
            text += "; " + unit
    return re.sub(r";{2,}", ";", text).strip()


def group_by_surface(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        output[row["surface"]].append(row)
    return output


def build_top_residual_inventory(
    base_cells: list[dict[str, str]], dictionary: list[dict[str, str]],
    repair_surfaces: set[str], selected_surfaces: set[str],
) -> list[dict[str, Any]]:
    residual = Counter(
        row["surface"] for row in base_cells
        if is_unknown(row["v99r6_spoken_cell_de"]) and row["surface"] not in repair_surfaces
    )
    concrete_by_surface = group_by_surface([
        row for row in dictionary if not is_unknown(row["working_meaning_de"])
    ])
    output: list[dict[str, Any]] = []
    for rank, (surface, count) in enumerate(
        sorted(residual.items(), key=lambda item: (-item[1], item[0]))[:100], 1,
    ):
        routes: list[str] = []
        cuts: set[tuple[str, str]] = set()
        for index in range(1, len(surface)):
            left, right = surface[:index], surface[index:]
            if left not in concrete_by_surface or right not in concrete_by_surface:
                continue
            cuts.add((left, right))
            for left_row in concrete_by_surface[left]:
                for right_row in concrete_by_surface[right]:
                    routes.append(
                        f"{left_row['reading_id']}={left_row['working_meaning_de']} + "
                        f"{right_row['reading_id']}={right_row['working_meaning_de']}"
                    )
        status = "NO_SPLIT" if not routes else "UNIQUE_SPLIT" if len(routes) == 1 else "MULTI_SPLIT"
        output.append({
            "frequency_rank": rank, "surface": surface,
            "residual_unknown_occurrences": count, "split_status": status,
            "graphemic_cut_count": len(cuts), "reading_combination_count": len(routes),
            "exact_v99r4_routes": " || ".join(routes) or "NONE",
            "selected_gdt734_candidate": int(surface in selected_surfaces),
            "selection_reason": "RECURRENT_EXACT_WHOLE_WITH_UNIQUE_NAVIGATION_SPLIT" if surface in selected_surfaces else "NOT_SELECTED_THIS_TRANCHE",
        })
    assert len(output) == 100
    assert Counter(row["split_status"] for row in output) == Counter({
        "NO_SPLIT": 25, "UNIQUE_SPLIT": 29, "MULTI_SPLIT": 46,
    })
    assert sum(int(row["selected_gdt734_candidate"]) for row in output) == 20
    assert all(
        row["split_status"] == "UNIQUE_SPLIT"
        for row in output if int(row["selected_gdt734_candidate"])
    )
    return output


def build_dictionary(
    base_cells: list[dict[str, str]], dictionary: list[dict[str, str]],
    candidate_specs: list[dict[str, str]], editorial_specs: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    base_fields = list(dictionary[0])
    by_reading = {row["reading_id"]: row for row in dictionary}
    assert len(by_reading) == len(dictionary) == 1586
    editorial_by_surface = {row["surface"]: row for row in editorial_specs}
    assert len(editorial_by_surface) == len(editorial_specs) == 28
    for surface, spec in editorial_by_surface.items():
        source = by_reading[spec["expected_reading_id"]]
        assert source["surface"] == surface
        assert source["working_meaning_de"] == spec["expected_old_default_de"]
        assert source["global_export_scope"] == "ACTIVE_WORKING_DEFAULT"
        assert source["unconditional_global_export_allowed"] == "1"

    output: list[dict[str, Any]] = []
    for source in dictionary:
        spec = editorial_by_surface.get(source["surface"])
        row: dict[str, Any] = dict(source)
        row.update({
            "v99r7_spoken_default_de": spec["spoken_default_de"] if spec else source["working_meaning_de"],
            "gdt734_renderer_decision": spec["decision"] if spec else "INHERITED_UNCHANGED",
            "gdt734_renderer_blocker_status": spec["blocker_status"] if spec else "NONE",
            "gdt734_renderer_positive_evidence_de": spec["reason_de"] if spec else "INHERITED_GDT730_EVIDENCE",
            "gdt734_renderer_counterevidence_de": spec["counterevidence_de"] if spec else "INHERITED_GDT730_COUNTEREVIDENCE",
            "gdt734_candidate_composition": "NONE",
            "gdt734_component_reading_ids": "NONE",
            "gdt734_component_export_allowed": 0,
            "gdt734_exact_whole_default_allowed": source["v99_exact_whole_surface_default_allowed"],
            "gdt734_candidate_decision": "NONE",
            "gdt734_composition_semantic_credit": 0,
            "gdt734_score_formula": "INHERITED_SCORE_UNCHANGED",
        })
        output.append(row)

    unknown_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in base_cells:
        if is_unknown(row["v99r6_spoken_cell_de"]):
            unknown_by_surface[row["surface"]].append(row)
    known_surfaces = {row["surface"] for row in dictionary}
    candidate_by_surface: dict[str, dict[str, Any]] = {}
    for spec in candidate_specs:
        surface = spec["surface"]
        assert surface == spec["prefix_surface"] + spec["suffix_surface"]
        assert surface not in known_surfaces and surface not in candidate_by_surface
        left = by_reading[spec["prefix_reading_id"]]
        right = by_reading[spec["suffix_reading_id"]]
        assert left["surface"] == spec["prefix_surface"]
        assert right["surface"] == spec["suffix_surface"]
        occurrences = unknown_by_surface[surface]
        assert len(occurrences) == int(spec["expected_occurrences"])
        score, recurrence_bonus, score_formula = candidate_score(
            spec["candidate_decision"],
            int(left["working_model_score_0_100_not_probability"]),
            int(right["working_model_score_0_100_not_probability"]),
            len(occurrences),
        )
        assert score == int(spec["working_model_score_0_100_not_probability"])
        assert spec["working_model_level"] == score_level(score)
        row = {field: "" for field in base_fields}
        row.update({
            "surface": surface, "reading_id": f"{surface}#G734",
            "working_meaning_de": spec["working_meaning_de"],
            "current_layer": "GDT734_EXPLORATORY_EXACT_WHOLE",
            "semantic_scope": "EXPLORATORY_EXACT_WHOLE_READING",
            "semantic_applicability": "SEMANTIC_WORKING_READING",
            "form_level": "F3_EXACT_ZL3B_WHOLE",
            "occurrence_count": len(occurrences),
            "page_count": len({item["page"] for item in occurrences}),
            "locus_count": len({item["locus"] for item in occurrences}),
            "working_model_score_0_100_not_probability": score,
            "working_model_level": spec["working_model_level"],
            "source_gdts": "GDT637|GDT678|GDT710|GDT733|GDT734",
            "positive_evidence_de": spec["positive_evidence_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "historical_confirmation": "H0_NONE",
            "historical_analogue": "PHARMACOLOGICAL_MICROENTRY_ARCHITECTURE_ONLY",
            "relation_word_delta": "0_GDT734",
            "global_export_scope": "GDT734_EXPLORATORY_EXACT_WHOLE_DEFAULT",
            "bound_span_ids": "NONE", "unconditional_global_export_allowed": 1,
            "v99_context_realizations_de": spec["spoken_render_de"],
            "source_reading_ids": f"{left['reading_id']}|{right['reading_id']}",
            "v99_audit_decision": "GDT734_UNIQUE_SPLIT_PROMOTE",
            "v99_evidence_class": (
                "UNIQUE_SPLIT_COMPOSITIONAL_WHOLE"
                if spec["candidate_decision"] == "PROMOTE_COMPOSITIONAL_WHOLE"
                else "UNIQUE_SPLIT_ROLE_CONSTRAINED_WHOLE"
                if spec["candidate_decision"] == "REVISE_ROLE_CONSTRAINED_WHOLE"
                else "RECURRENT_LEARNED_WHOLE_UNIQUE_SPLIT_NAVIGATION_ONLY"
            ),
            "v99_open_semantic_slots": spec["open_semantic_slots"],
            "v99_component_global_export_allowed": 0,
            "v99_exact_whole_surface_default_allowed": 1,
            "v99_lineage_class": "GDT734_UNIQUE_SPLIT_EXACT_WHOLE",
            "v99_value_kind": "EXPLORATORY_COMPOSITE_WHOLE",
            "v99_structural_tag": "NONE",
            "v99_action_default_allowed": spec["action_default_allowed"],
            "v99r7_spoken_default_de": spec["spoken_render_de"],
            "gdt734_renderer_decision": "NEW_UNIQUE_SPLIT_DEFAULT",
            "gdt734_renderer_blocker_status": "NONE",
            "gdt734_renderer_positive_evidence_de": spec["positive_evidence_de"],
            "gdt734_renderer_counterevidence_de": spec["counterevidence_de"],
            "gdt734_candidate_composition": spec["composition"],
            "gdt734_component_reading_ids": f"{left['reading_id']}|{right['reading_id']}",
            "gdt734_component_export_allowed": 0,
            "gdt734_exact_whole_default_allowed": 1,
            "gdt734_candidate_decision": spec["candidate_decision"],
            "gdt734_composition_semantic_credit": spec["composition_semantic_credit"],
            "gdt734_score_formula": f"{score_formula};RECURRENCE_BONUS={recurrence_bonus}",
        })
        output.append(row)
        candidate_by_surface[surface] = row

    assert len(output) == 1606
    assert len({row["surface"] for row in output}) == 1602
    assert all(row["working_meaning_de"] for row in output)
    assert all(row["positive_evidence_de"] and row["counterevidence_de"] for row in output)
    assert all(row["working_model_level"] for row in output)
    return output, candidate_by_surface, editorial_by_surface


def determine_repairs(
    base_cells: list[dict[str, str]], dictionary_rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dictionary_rows:
        if row["current_layer"] == "GDT734_EXPLORATORY_EXACT_WHOLE":
            continue
        by_surface[str(row["surface"])].append(row)
    unknown_surfaces = {row["surface"] for row in base_cells if is_unknown(row["v99r6_spoken_cell_de"])}
    known_intersection = unknown_surfaces & set(by_surface)
    repair: dict[str, dict[str, Any]] = {}
    for surface in known_intersection:
        eligible = [
            row for row in by_surface[surface]
            if row["current_layer"].startswith("ACTIVE_")
            and row["global_export_scope"] == "ACTIVE_WORKING_DEFAULT"
            and str(row["unconditional_global_export_allowed"]) == "1"
        ]
        if eligible:
            assert len(eligible) == 1
            repair[surface] = eligible[0]
    denied = known_intersection - set(repair)
    assert len(known_intersection) == 73 and len(repair) == 71
    assert denied == {"dchey", "olkar"}
    return repair, denied


def build_repair_audit(
    base_cells: list[dict[str, str]], repair: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    unknown_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in base_cells:
        if is_unknown(row["v99r6_spoken_cell_de"]):
            unknown_by_surface[row["surface"]].append(row)
    output: list[dict[str, Any]] = []
    for surface, authority in repair.items():
        cells = unknown_by_surface[surface]
        output.append({
            "repair_id": "PENDING", "surface": surface, "reading_id": authority["reading_id"],
            "cache_occurrences_repaired": len(cells),
            "page_count": len({row["page"] for row in cells}),
            "locus_count": len({row["locus"] for row in cells}),
            "v99r4_semantic_default_de": authority["working_meaning_de"],
            "v99r7_spoken_default_de": authority["v99r7_spoken_default_de"],
            "working_model_score_0_100_not_probability": authority["working_model_score_0_100_not_probability"],
            "working_model_level": authority["working_model_level"],
            "positive_evidence_de": authority["positive_evidence_de"],
            "counterevidence_de": authority["counterevidence_de"],
            "semantic_scope": authority["semantic_scope"],
            "global_export_scope": authority["global_export_scope"],
            "unconditional_global_export_allowed": authority["unconditional_global_export_allowed"],
            "gdt734_renderer_decision": authority["gdt734_renderer_decision"],
            "gdt734_renderer_blocker_status": authority["gdt734_renderer_blocker_status"],
            "component_export_allowed": 0,
            "repair_basis": "GDT733_OMITTED_ACTIVE_WORKING_DEFAULT_LAYER",
        })
    output.sort(key=lambda row: (-int(row["cache_occurrences_repaired"]), row["surface"]))
    for index, row in enumerate(output, 1):
        row["repair_id"] = f"G734-R{index:03d}"
    assert len(output) == 71
    assert sum(int(row["cache_occurrences_repaired"]) for row in output) == 305
    return output


def build_candidate_audit(
    base_cells: list[dict[str, str]], candidate_specs: list[dict[str, str]],
    candidates: dict[str, dict[str, Any]], dictionary: list[dict[str, str]],
) -> list[dict[str, Any]]:
    base_by_id = {row["reading_id"]: row for row in dictionary}
    unknown_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in base_cells:
        if is_unknown(row["v99r6_spoken_cell_de"]):
            unknown_by_surface[row["surface"]].append(row)
    output: list[dict[str, Any]] = []
    for spec in candidate_specs:
        left = base_by_id[spec["prefix_reading_id"]]
        right = base_by_id[spec["suffix_reading_id"]]
        cells = unknown_by_surface[spec["surface"]]
        output.append({
            **spec, "candidate_reading_id": candidates[spec["surface"]]["reading_id"],
            "actual_occurrences": len(cells),
            "actual_pages": len({row["page"] for row in cells}),
            "actual_loci": len({row["locus"] for row in cells}),
            "sample_loci": "|".join(sorted({row["locus"] for row in cells})[:8]),
            "prefix_meaning_de": left["working_meaning_de"],
            "prefix_score": left["working_model_score_0_100_not_probability"],
            "prefix_level": left["working_model_level"],
            "prefix_export_scope": left["global_export_scope"],
            "suffix_meaning_de": right["working_meaning_de"],
            "suffix_score": right["working_model_score_0_100_not_probability"],
            "suffix_level": right["working_model_level"],
            "suffix_export_scope": right["global_export_scope"],
            "exact_graphemic_split_count": 1, "exact_reading_combination_count": 1,
            "semantic_scope": "EXPLORATORY_EXACT_WHOLE_READING",
            "global_export_scope": "GDT734_EXPLORATORY_EXACT_WHOLE_DEFAULT",
            "exact_whole_surface_default_allowed": 1,
            "component_global_export_allowed": 0, "historical_confirmation": "H0_NONE",
            "score_formula": candidates[spec["surface"]]["gdt734_score_formula"],
        })
    assert len(output) == 20
    assert sum(int(row["actual_occurrences"]) for row in output) == 226
    return output


def build_editorial_scope_audit(
    base_cells: list[dict[str, str]], editorial_specs: list[dict[str, str]],
    repair: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in base_cells:
        by_surface[row["surface"]].append(row)
    output: list[dict[str, Any]] = []
    for spec in editorial_specs:
        rows = by_surface[spec["surface"]]
        repaired = [row for row in rows if is_unknown(row["v99r6_spoken_cell_de"])]
        retained = [row for row in rows if not is_unknown(row["v99r6_spoken_cell_de"])]
        assert spec["surface"] in repair and repaired
        output.append({
            "surface": spec["surface"], "reading_id": spec["expected_reading_id"],
            "total_cache_occurrences": len(rows),
            "omitted_unknown_occurrences_receiving_portable_renderer": len(repaired),
            "higher_precedence_occurrences_retained": len(retained),
            "retained_v99r6_realizations_de": " || ".join(sorted({
                row["v99r6_spoken_cell_de"] for row in retained
            })) or "NONE",
            "portable_v99r7_repair_renderer_de": spec["spoken_default_de"],
            "renderer_decision": spec["decision"],
            "scope_decision": "REPAIR_OMISSION_ONLY__EXACT_CONTEXT_AND_SPAN_PRECEDENCE_RETAINED",
            "local_variants_explicitly_marked": int(bool(retained)),
            "silent_second_global_default": 0,
        })
    assert len(output) == len(editorial_specs) == 28
    return output


def build_cells(
    base_cells: list[dict[str, str]], repair: dict[str, dict[str, Any]],
    candidates: dict[str, dict[str, Any]], editorial: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output: list[dict[str, Any]] = []
    delta: list[dict[str, Any]] = []
    for base in base_cells:
        surface = base["surface"]
        unknown = is_unknown(base["v99r6_spoken_cell_de"])
        authority: dict[str, Any] | None = None
        dispatch = "UNCHANGED_GDT733"
        semantic = base["current_semantic_value_de"]
        spoken = base["v99r6_spoken_cell_de"]
        editorial_applied = 0
        if unknown and surface in repair:
            authority = repair[surface]
            dispatch = "ACTIVE_WHOLE_EXPORT_REPAIR"
            semantic = str(authority["working_meaning_de"])
            spoken = str(authority["v99r7_spoken_default_de"])
            editorial_applied = int(authority["gdt734_renderer_decision"] == "RENDERER_REVISE")
        elif unknown and surface in candidates:
            authority = candidates[surface]
            dispatch = "UNIQUE_SPLIT_EXPLORATORY_WHOLE"
            semantic = str(authority["working_meaning_de"])
            spoken = str(authority["v99r7_spoken_default_de"])
        changed = int(spoken != base["v99r6_spoken_cell_de"])
        if changed:
            assert unknown and authority is not None
            assert base["practical_unit_layer"] == "SINGLE_CELL_UNIT"
            assert base["practical_unit_role"] == "EMIT_CELL_ONCE"
            assert not is_unknown(spoken)
        practical = spoken if changed else base["practical_render_once_de"]
        row = {
            "cell_id": base["cell_id"], "page": base["page"], "locus": base["locus"],
            "token_ordinal": base["token_ordinal"], "surface": surface,
            "v99r6_spoken_cell_de": base["v99r6_spoken_cell_de"],
            "v99r7_semantic_value_de": semantic, "v99r7_spoken_cell_de": spoken,
            "gdt734_dispatch_class": dispatch,
            "gdt734_authority_id": authority["reading_id"] if authority else base["authority_id"],
            "gdt734_score_0_100_not_probability": authority["working_model_score_0_100_not_probability"] if authority else base["authority_score_0_100_not_probability"],
            "gdt734_confidence_level": authority["working_model_level"] if authority else base["authority_confidence_level"],
            "gdt734_semantic_scope": authority["semantic_scope"] if authority else base["authority_semantic_scope"],
            "gdt734_global_export_scope": authority["global_export_scope"] if authority else base["authority_global_export_scope"],
            "gdt734_candidate_decision": authority["gdt734_candidate_decision"] if authority else "NONE",
            "gdt734_composition_semantic_credit": authority["gdt734_composition_semantic_credit"] if authority else 0,
            "practical_unit_layer": base["practical_unit_layer"],
            "practical_unit_id": base["practical_unit_id"],
            "practical_unit_role": base["practical_unit_role"],
            "v99r6_practical_render_once_de": base["practical_render_once_de"],
            "v99r7_practical_render_once_de": practical,
            "v99r7_changed_from_v99r6": changed,
            "editorial_override_applied": editorial_applied,
            "unknown_v99r6": int(unknown), "unknown_v99r7": int(is_unknown(spoken)),
            "component_export_credit": 0,
        }
        output.append(row)
        if changed:
            spec = editorial.get(surface)
            delta.append({
                "change_id": f"G734-P{len(delta)+1:04d}", "cell_id": base["cell_id"],
                "page": base["page"], "locus": base["locus"],
                "token_ordinal": base["token_ordinal"], "surface": surface,
                "v99r6_before_de": base["v99r6_spoken_cell_de"],
                "v99r7_semantic_de": semantic, "v99r7_spoken_de": spoken,
                "dispatch_class": dispatch, "authority_id": authority["reading_id"],
                "working_model_score_0_100_not_probability": authority["working_model_score_0_100_not_probability"],
                "working_model_level": authority["working_model_level"],
                "positive_evidence_de": authority["positive_evidence_de"],
                "counterevidence_de": authority["counterevidence_de"],
                "semantic_scope": authority["semantic_scope"],
                "global_export_scope": authority["global_export_scope"],
                "exact_whole_surface_default_allowed": 1,
                "component_global_export_allowed": 0,
                "candidate_decision": authority["gdt734_candidate_decision"],
                "composition_semantic_credit": authority["gdt734_composition_semantic_credit"],
                "score_formula": authority["gdt734_score_formula"],
                "editorial_decision": spec["decision"] if spec else "NONE",
                "editorial_blocker_status": spec["blocker_status"] if spec else "NONE",
            })
    assert len(output) == len(base_cells) == 32339 and len(delta) == 531
    assert Counter(row["gdt734_dispatch_class"] for row in output) == Counter({
        "UNCHANGED_GDT733": 31808, "ACTIVE_WHOLE_EXPORT_REPAIR": 305,
        "UNIQUE_SPLIT_EXPLORATORY_WHOLE": 226,
    })
    assert sum(int(row["unknown_v99r6"]) for row in output) == 7989
    assert sum(int(row["unknown_v99r7"]) for row in output) == 7458
    return output, delta


def render_units(rows: list[dict[str, Any]], version: str) -> list[str]:
    spoken_field = f"{version}_spoken_cell_de"
    practical_field = f"{version}_practical_render_once_de"
    units: list[str] = []
    for index, row in enumerate(rows):
        role = row["practical_unit_role"]
        if role == "SPAN_START_EMITS_ONCE":
            assert index + 1 < len(rows)
            companion = rows[index + 1]
            assert companion["practical_unit_role"] == "SPAN_COMPANION_SUPPRESSED"
            assert companion["practical_unit_id"] == row["practical_unit_id"]
            units.append(str(row[practical_field]))
        elif role == "SPAN_COMPANION_SUPPRESSED":
            assert index > 0 and rows[index - 1]["practical_unit_id"] == row["practical_unit_id"]
        elif role == "ATTACH_PREVIOUS_NO_UNIT":
            assert units
            mark = str(row[practical_field])
            assert mark in {";", "."}
            if not units[-1].endswith(mark):
                units[-1] += mark
        else:
            assert role == "EMIT_CELL_ONCE"
            units.append(str(row[spoken_field]))
    return units


def build_lines(
    base_lines: list[dict[str, str]], cells: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_locus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cells:
        by_locus[row["locus"]].append(row)
    for rows in by_locus.values():
        rows.sort(key=lambda row: int(row["token_ordinal"]))
    output: list[dict[str, Any]] = []
    for base in base_lines:
        rows = by_locus[base["locus"]]
        assert len(rows) == int(base["token_count"])
        before_units = render_units(rows, "v99r6")
        after_units = render_units(rows, "v99r7")
        before_render = practicalize(before_units)
        after_render = practicalize(after_units)
        assert before_render == base["v99r6_practical_render_de"]
        changed = [row for row in rows if int(row["v99r7_changed_from_v99r6"])]
        unknown_before = sum(int(row["unknown_v99r6"]) for row in rows)
        unknown_after = sum(int(row["unknown_v99r7"]) for row in rows)
        output.append({
            "page": base["page"], "locus": base["locus"], "section": base["section"],
            "language": base["language"], "hand": base["hand"],
            "token_count": base["token_count"], "practical_unit_count": len(after_units),
            "gdt734_changed_cell_count": len(changed),
            "active_whole_repair_count": sum(row["gdt734_dispatch_class"] == "ACTIVE_WHOLE_EXPORT_REPAIR" for row in rows),
            "unique_split_candidate_count": sum(row["gdt734_dispatch_class"] == "UNIQUE_SPLIT_EXPLORATORY_WHOLE" for row in rows),
            "editorial_override_count": sum(int(row["editorial_override_applied"]) for row in rows),
            "unknown_cells_v99r6": unknown_before, "unknown_cells_v99r7": unknown_after,
            "unknown_delta": unknown_after - unknown_before,
            "complete_line_v99r6": int(unknown_before == 0),
            "complete_line_v99r7": int(unknown_after == 0),
            "newly_complete_line": int(unknown_before > 0 and unknown_after == 0),
            "gdt734_changed_ordinals": "|".join(str(row["token_ordinal"]) for row in changed) or "NONE",
            "gdt734_dispatch_classes": " | ".join(row["gdt734_dispatch_class"] for row in rows),
            "zl3b_line": base["zl3b_line"],
            "v99r7_semantic_token_values_de": " | ".join(row["v99r7_semantic_value_de"] for row in rows),
            "v99r7_spoken_token_values_de": " | ".join(row["v99r7_spoken_cell_de"] for row in rows),
            "v99r7_practical_units_de": " | ".join(after_units),
            "v99r6_practical_render_de": before_render,
            "v99r7_practical_render_de": after_render,
        })
    assert len(output) == len(base_lines) == 4128
    assert sum(int(row["practical_unit_count"]) for row in output) == 32319
    assert not any(GENERIC_NONSENSE_RX.search(row["v99r7_practical_render_de"]) for row in output)
    assert not any(re.search(r";\s*;", row["v99r7_practical_render_de"]) for row in output)
    dense = [row for row in output if int(row["gdt734_changed_cell_count"])]
    dense.sort(key=lambda row: (-int(row["gdt734_changed_cell_count"]), int(row["unknown_cells_v99r7"]), row["locus"]))
    dense = [{"rank": index, **row} for index, row in enumerate(dense[:50], 1)]
    assert len(dense) == 50
    return output, dense


def build_role_matrix(
    specs: list[dict[str, str]], base_cells: list[dict[str, str]],
    dictionary: list[dict[str, str]],
) -> list[dict[str, Any]]:
    by_surface = group_by_surface(dictionary)
    cells_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in base_cells:
        cells_by_surface[row["surface"]].append(row)
    output: list[dict[str, Any]] = []
    for spec in specs:
        cells = cells_by_surface[spec["surface"]]
        assert len(cells) == int(spec["expected_cache_occurrences"])
        output.append({
            **spec, "actual_cache_occurrences": len(cells),
            "page_count": len({row["page"] for row in cells}),
            "locus_count": len({row["locus"] for row in cells}),
            "current_dictionary_readings": " || ".join(
                f"{row['reading_id']}={row['working_meaning_de']}" for row in by_surface[spec["surface"]]
            ) or "NONE",
            "portable_tail_role_adopted": int(spec["decision"] in {"PROMOTE_ROLE_TEMPLATE", "PROMOTE_TAIL_ONLY"}),
            "free_head_or_tail_lexeme_exported": 0, "historical_relation_credit": 0,
        })
    assert len(output) == 19
    return output


def build_blockers(
    base_cells: list[dict[str, str]], cells: list[dict[str, Any]],
    repair_audit: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for rule in read_tsv(BLOCKER_RULES):
        pattern = re.compile(rule["regex"], re.IGNORECASE)
        if rule["field_scope"] == "working_meaning_de":
            before = sum(bool(pattern.search(row["v99r6_spoken_cell_de"])) for row in base_cells)
            after = sum(bool(pattern.search(row["v99r7_spoken_cell_de"])) for row in cells)
        elif rule["field_scope"] == "surface":
            before = after = sum(bool(pattern.search(row["surface"])) for row in base_cells)
        elif rule["field_scope"] == "passage_cell_status":
            before = sum(is_unknown(row["v99r6_spoken_cell_de"]) for row in base_cells)
            after = sum(is_unknown(row["v99r7_spoken_cell_de"]) for row in cells)
        else:
            raise AssertionError(rule["field_scope"])
        output.append({
            "priority": rule["priority"], "blocker_class": rule["blocker_class"],
            "field_scope": rule["field_scope"], "v99r6_before_cells": before,
            "v99r7_after_cells": after, "delta_after_minus_before": after - before,
            "interpretation_de": rule["interpretation_de"],
        })
    generic_surfaces = {
        row["surface"] for row in repair_audit
        if row["gdt734_renderer_blocker_status"] == "GENERIC_BLOCKER"
    }
    generic_count = sum(row["surface"] in generic_surfaces for row in cells)
    output.append({
        "priority": 6, "blocker_class": "ACTIVE_WHOLE_GENERIC_HOLD",
        "field_scope": "surface", "v99r6_before_cells": 0,
        "v99r7_after_cells": generic_count, "delta_after_minus_before": generic_count,
        "interpretation_de": "Formal aufgelöste Ganzwörter, deren deutscher Default weiterhin zu allgemein ist; sie zählen nicht mehr als unbekannt, bleiben aber redaktionelle Schuld.",
    })
    assert next(row for row in output if row["blocker_class"] == "UNKNOWN_CELL")["v99r7_after_cells"] == 7458
    return output


def build_quality(
    base_cells: list[dict[str, str]], cells: list[dict[str, Any]],
    lines: list[dict[str, Any]], repair_audit: list[dict[str, Any]],
    candidate_audit: list[dict[str, Any]], editorial_specs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    unknown_surfaces_before = {row["surface"] for row in base_cells if is_unknown(row["v99r6_spoken_cell_de"])}
    unknown_surfaces_after = {row["surface"] for row in cells if is_unknown(row["v99r7_spoken_cell_de"])}
    metrics: list[tuple[str, int, int, str]] = [
        ("cache_cells", 32339, len(cells), "all admitted cache positions retained"),
        ("practical_units", 32319, sum(int(row["practical_unit_count"]) for row in lines), "existing spans and punctuation precedence retained"),
        ("unknown_cells", 7989, sum(int(row["unknown_v99r7"]) for row in cells), "71 existing wholes plus 20 unique-split wholes receive defaults"),
        ("unknown_surfaces", 5107, len(unknown_surfaces_after), "exact surface types removed from the unknown tail"),
        ("active_whole_export_omission_cells", 305, 0, "all formally licensed active-whole omissions repaired"),
        ("active_whole_export_omission_surfaces", 71, 0, "all eligible omitted surfaces repaired; dchey and olkar remain scoped"),
        ("new_unique_split_candidate_cells", 0, sum(int(row["actual_occurrences"]) for row in candidate_audit), "twenty recurrent exact-whole candidate defaults"),
        ("new_unique_split_candidate_surfaces", 0, len(candidate_audit), "no multi-split candidate promoted"),
        ("compositionally_supported_candidate_surfaces", 0, sum(row["candidate_decision"] == "PROMOTE_COMPOSITIONAL_WHOLE" for row in candidate_audit), "unique split plus compatible roles support the whole meaning"),
        ("role_constrained_candidate_surfaces", 0, sum(row["candidate_decision"] == "REVISE_ROLE_CONSTRAINED_WHOLE" for row in candidate_audit), "nominal or patient-free revision after manual audit"),
        ("learned_whole_no_composition_credit_surfaces", 0, sum(row["candidate_decision"] == "LEARNED_WHOLE_NO_COMPOSITIONAL_CREDIT" for row in candidate_audit), "recurrence keeps a default while the visible split is semantically redundant or unsafe"),
        ("changed_cache_cells", 0, sum(int(row["v99r7_changed_from_v99r6"]) for row in cells), "all changes are recorded in the position delta"),
        ("changed_lines", 0, sum(int(row["gdt734_changed_cell_count"]) > 0 for row in lines), "lines gaining at least one concrete value"),
        ("complete_lines", sum(int(row["complete_line_v99r6"]) for row in lines), sum(int(row["complete_line_v99r7"]) for row in lines), "lines without an audible unknown cell"),
        ("editorially_audited_active_wholes", 0, len(editorial_specs), "manual practical-language audit of the weakest export repairs"),
        ("editorially_revised_active_wholes", 0, sum(row["gdt734_renderer_decision"] == "RENDERER_REVISE" for row in repair_audit), "renderer-only simplifications retain dictionary evidence and score"),
        ("generic_nonsense_lines", sum(bool(GENERIC_NONSENSE_RX.search(row["v99r6_practical_render_de"])) for row in lines), sum(bool(GENERIC_NONSENSE_RX.search(row["v99r7_practical_render_de"])) for row in lines), "forbidden work-item filler remains absent"),
        ("audible_grade_frame_cells", sum(bool(GRADE_RX.search(row["v99r6_spoken_cell_de"])) for row in base_cells), sum(bool(GRADE_RX.search(row["v99r7_spoken_cell_de"])) for row in cells), "GDT733 spoken-grade cleanup retained"),
    ]
    assert len(unknown_surfaces_before) == 5107 and len(unknown_surfaces_after) == 5016
    return [{
        "metric": name, "v99r6_before": before, "v99r7_after": after,
        "delta_after_minus_before": after - before, "interpretation": note,
    } for name, before, after, note in metrics]


def build_reader_markdown(dense: list[dict[str, Any]]) -> str:
    output = [
        "# GDT734 — 50 änderungsdichteste V99R7-Passagen", "",
        "Die Ausgabe kombiniert die 71 reparierten aktiven Ganzwortdefaults mit 20 neuen, genau einmal zerlegbaren Arbeits-Ganzwörtern. Mehrdeutige Formen bleiben `?`.", "",
    ]
    for row in dense:
        output.extend([
            f"## {row['rank']}. {row['locus']} ({row['gdt734_changed_cell_count']} neue Werte; {row['unknown_cells_v99r7']} Lücken verbleiben)", "",
            f"`{row['zl3b_line']}`", "", f"Vorher: {row['v99r6_practical_render_de']}", "",
            f"V99R7: {row['v99r7_practical_render_de']}", "",
        ])
    return "\n".join(output).rstrip() + "\n"


def build_report(result: dict[str, Any]) -> str:
    unknown_cells = f"{result['unknown_cells_after']:,}".replace(",", ".")
    unknown_surfaces = f"{result['unknown_surfaces_after']:,}".replace(",", ".")
    return f"""# GDT734 — V99R7 recurrent unknown-family dispatch

Status: `{result['status']}`

## Ergebnis

Der erste, rein technische Pass findet einen reproduzierbaren
V99R6/V99R7-Projektionsfehler: 71 aktive Ganzwortlesungen
waren als `ACTIVE_WORKING_DEFAULT` und bedingungslos exportierbar markiert,
blieben in GDT733 aber an 305 identischen Cache-Stellen `?`, weil dessen
Projektionsfilter nur die ältere `GLOBAL_V48_DEFAULT`-Schicht einsammelte.
V99R7 repariert alle 305 Stellen. `dchey` und `olkar` bleiben als die beiden
bewusst kontext- beziehungsweise spangebundenen Ausnahmen draußen.

Davon getrennt prüft der zweite, explorative Pass 20 häufige Restformen an 226
Stellen und gibt jeder einen konkreten Ganzwortdefault. Jede besitzt genau eine
Zweiteilung unter den derzeit konkreten V99R4-Lesartenkombinationen; das ist
keine Behauptung einer sprachlich eindeutigen Segmentierung. Der manuelle
Gegencheck trennt neun kompositionell gestützte,
fünf rollenbeschränkte und sechs nur als gelernte Ganzwörter lesbare Formen.
Eine eindeutige Trennstelle zählt ausdrücklich nicht automatisch als
semantischer Beleg. Die neue Tranche spricht unter anderem trockenes Pulver,
Drogenholz, Blütenfraktion, Ansatz, Trocknen, Kühlen, Einweichen und Abmessen
aus. Kein Kandidat mit mehreren Zerlegungen wird übernommen.

Damit sinkt die Zahl der `[surface:?]`-Marker in diesem festen Cache von 7.989
auf **{unknown_cells}** Zellen und von 5.107 auf **{unknown_surfaces}** Formen.
Diese Abdeckungsmetrik misst keine Übersetzungswahrheit. Insgesamt
ändern sich 531 Zellen auf {result['changed_lines']} Zeilen; die Zahl vollständig
lesbarer Cache-Zeilen steigt von {result['complete_lines_before']} auf
{result['complete_lines_after']} (+{result['newly_complete_lines']}).

## Praktischer Renderer

{result['editorially_audited_wholes']} der formal exportierbaren aktiven Ganzwörter wurden zusätzlich redaktionell
geprüft. {result['editorially_revised_wholes']} erhalten eine kürzere gesprochene
Fassung, ohne Score, Evidenz oder gespeicherten semantischen Kern umzuschreiben.
So wird etwa `Mischgut` zu `Mischung`, `heißen Auszug bereiten` zu `Ansatz
erhitzen`, und occurrence-lokale Patienten verschwinden aus portablen Kernen.
`os=Zubereitung` und `dold=abmessen und abschließen` bleiben sichtbar offen,
statt mit erfundenem Stoff oder Patienten aufgefüllt zu werden.

Diese gesprochene Fassung gilt für die 305 zuvor ausgelassenen
Ganzwortprojektionen. Bereits vorhandene exakte V99-Kontexte und gebundene
Spans behalten als höhere Präzedenz ihre positionsgebundene Realisierung; die
abweichende Ausgabe derselben Oberfläche ist damit explizit lokal und kein
zweiter stiller globaler Default.

## Wortstamm- und Codebuchmodell

Innerhalb des aktuellen Arbeitswörterbuchs ist die ausgewählte 19-Formen-
Kreuzmatrix mit Rollen konsistenter als mit universellen Wörtern:
`-ol` verhält sich als Stoff-/Materialrolle, `-or` als Portion, `-aiin/-ain`
als Index III/II und `-ar` als Anteil I. `cth`, `p` und `s` sind dabei
exakte-Ganzwort-Arbeitsköpfe für Pflanzendroge, Pulver und Samen; kein freier
Kopfwert wird exportiert. `olk` bleibt gebunden, `olkol` begrenzt die
`-ol`-Regel und `-dy` wird nicht als portable Rolle freigegeben. Der nächste
historische Architekturvergleich ist ein Apothekerbuch-Mikroeintrag aus
gelerntem Drogenwort, kurzem Qualitätsrahmen und separatem Mengen-/Gradslot.
Diese Parallelen bestätigen weder eine Form noch eine Bedeutung: Sie erhalten
exakt null Relations- und Zeichenwertkredit.

## Confidence und Evidenz

Das vollständige V99R7-Wörterbuch enthält 1.606 Lesarten für 1.602 Formen.
Jede Zeile trägt Arbeitsbedeutung, Score, Confidence, positive Evidenz,
Gegenbeleg, Scope und Exportrecht. Die 20 neuen Formen liegen bewusst nur in
W1/W2. Ihre Scores werden aus dem schwächeren Teilwert, einem begrenzten
Wiederholungsbonus und einem expliziten Routenabzug berechnet. Wiederholung und
Score sind ausschließlich interne Arbeitsmodell-Rangwerte, keine semantische
oder historische Bestätigung. Die Teilwerte werden nicht frei exportiert. Die
ganze Form darf im
bereits zugelassenen Cache als explorativer Default laufen.

## Grenze

Dies ist ein konkreter explorativer Arbeitsrenderer, kein bestätigter Klartext. Die
{result['residual_singleton_surfaces']:,} singletonlastigen Restformen, konkrete Pflanzenarten, Krankheiten,
Heilungen, historische Einheiten und die mehrdeutigen Spitzenformen
`qokeody`, `okeody`, `qokeor`, `chdaiin`, `ory` bleiben offen. Keine neue
Seite, kein Bild, keine Transkription, kein `f84` und kein `f84r` wurde benutzt.
""".replace(f"{result['residual_singleton_surfaces']:,}", f"{result['residual_singleton_surfaces']:,}".replace(",", "."))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    base_cells = read_tsv(BASE_CELLS)
    base_lines = read_tsv(BASE_LINES)
    dictionary = read_tsv(DICTIONARY)
    candidate_specs = read_tsv(CANDIDATE_SPECS)
    editorial_specs = read_tsv(EDITORIAL_SPECS)
    role_specs = read_tsv(ROLE_MATRIX_SPECS)
    historical_specs = read_tsv(HISTORICAL_SPECS)
    assert len(base_cells) == 32339 and len(base_lines) == 4128
    assert len(candidate_specs) == 20 and len(role_specs) == 19 and len(historical_specs) == 5
    assert not any(re.match(r"^f84(?:r|v|$)", row["page"]) for row in base_cells)

    complete_dictionary, candidates, editorial = build_dictionary(
        base_cells, dictionary, candidate_specs, editorial_specs,
    )
    repair, denied = determine_repairs(base_cells, complete_dictionary)
    repair_audit = build_repair_audit(base_cells, repair)
    candidate_audit = build_candidate_audit(base_cells, candidate_specs, candidates, dictionary)
    editorial_scope = build_editorial_scope_audit(
        base_cells, editorial_specs, repair,
    )
    top_residual = build_top_residual_inventory(base_cells, dictionary, set(repair), set(candidates))
    cells, delta = build_cells(base_cells, repair, candidates, editorial)
    lines, dense = build_lines(base_lines, cells)
    role_matrix = build_role_matrix(role_specs, base_cells, dictionary)
    blockers = build_blockers(base_cells, cells, repair_audit)
    quality = build_quality(base_cells, cells, lines, repair_audit, candidate_audit, editorial_specs)
    parity = [{
        "source_artifact": str(path.relative_to(ROOT)), "sha256": file_sha(path),
        "gdt734_rewrite_count": 0, "parity_status": "BYTE_STABLE_INPUT_NOT_REWRITTEN",
    } for path in PARITY_PATHS]
    historical = [{
        **row,
        "adoption_in_gdt734": "ADOPT_MACRO_ARCHITECTURE" if row["comparator_id"] == "G734-H01" else "ADOPT_LIMITED_ROLE" if row["comparator_id"] in {"G734-H02", "G734-H03", "G734-H04"} else "RESIDUAL_ONLY",
        "voynich_sign_value_credit": 0,
    } for row in historical_specs]

    complete_before = sum(int(row["complete_line_v99r6"]) for row in lines)
    complete_after = sum(int(row["complete_line_v99r7"]) for row in lines)
    newly_complete = sum(int(row["newly_complete_line"]) for row in lines)
    assert complete_after - complete_before == newly_complete
    changed_lines = sum(int(row["gdt734_changed_cell_count"]) > 0 for row in lines)
    revised_wholes = sum(row["gdt734_renderer_decision"] == "RENDERER_REVISE" for row in repair_audit)
    status = (
        "PASS_V99R7_71_ACTIVE_WHOLE_EXPORT_REPAIRS_305_CELLS__"
        "20_UNIQUE_SPLIT_EXACT_WHOLES_226_CELLS__531_CHANGED_CELLS__"
        "7989_TO_7458_UNKNOWNS__5107_TO_5016_FORMS__"
        f"{newly_complete}_NEW_COMPLETE_LINES__9_COMPOSITIONAL_5_ROLE_CONSTRAINED_6_LEARNED__"
        f"{len(editorial_specs)}_EDITORIAL_AUDITS_{revised_wholes}_REVISED__"
        "1606_CONFIDENCE_EVIDENCE_ROWS__19_ROLE_MATRIX__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
    )
    result = {
        "experiment_id": "GDT734", "status": status,
        "cache_pages": len({row["page"] for row in cells}),
        "cache_lines": len(lines), "cache_cells": len(cells),
        "practical_units": sum(int(row["practical_unit_count"]) for row in lines),
        "unknown_cells_before": 7989,
        "unknown_cells_after": sum(int(row["unknown_v99r7"]) for row in cells),
        "unknown_surfaces_before": 5107,
        "unknown_surfaces_after": len({row["surface"] for row in cells if int(row["unknown_v99r7"])}),
        "residual_singleton_surfaces": sum(
            count == 1 for count in Counter(
                row["surface"] for row in cells if int(row["unknown_v99r7"])
            ).values()
        ),
        "known_dictionary_intersection": 73,
        "active_whole_repair_surfaces": len(repair),
        "active_whole_repair_cells": sum(row["gdt734_dispatch_class"] == "ACTIVE_WHOLE_EXPORT_REPAIR" for row in cells),
        "scope_denied_known_surfaces": sorted(denied),
        "new_candidate_surfaces": len(candidates),
        "new_candidate_cells": sum(row["gdt734_dispatch_class"] == "UNIQUE_SPLIT_EXPLORATORY_WHOLE" for row in cells),
        "compositional_candidate_wholes": sum(
            row["candidate_decision"] == "PROMOTE_COMPOSITIONAL_WHOLE"
            for row in candidate_audit
        ),
        "role_constrained_candidate_wholes": sum(
            row["candidate_decision"] == "REVISE_ROLE_CONSTRAINED_WHOLE"
            for row in candidate_audit
        ),
        "learned_candidate_wholes": sum(
            row["candidate_decision"] == "LEARNED_WHOLE_NO_COMPOSITIONAL_CREDIT"
            for row in candidate_audit
        ),
        "changed_cells": len(delta), "changed_lines": changed_lines,
        "complete_lines_before": complete_before, "complete_lines_after": complete_after,
        "newly_complete_lines": newly_complete,
        "editorially_audited_wholes": len(editorial_specs),
        "editorially_revised_wholes": revised_wholes,
        "editorial_scope_audit_rows": len(editorial_scope),
        "complete_dictionary_readings": len(complete_dictionary),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete_dictionary}),
        "role_matrix_rows": len(role_matrix), "historical_comparators": len(historical),
        "top_residual_inventory_rows": len(top_residual),
        "component_global_export_credit": 0,
        "new_pages": 0, "f84_accessed": 0, "f84r_accessed": 0,
    }
    assert result["cache_pages"] == 179
    assert result["unknown_cells_after"] == 7458 and result["unknown_surfaces_after"] == 5016
    assert result["active_whole_repair_cells"] == 305 and result["new_candidate_cells"] == 226
    assert result["changed_cells"] == 531
    assert (
        result["compositional_candidate_wholes"],
        result["role_constrained_candidate_wholes"],
        result["learned_candidate_wholes"],
    ) == (9, 5, 6)

    write_tsv(ART / "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv", complete_dictionary)
    write_tsv(ART / "V99R7_71_ACTIVE_WHOLE_EXPORT_REPAIR.tsv", repair_audit)
    write_tsv(ART / "V99R7_20_UNIQUE_SPLIT_CANDIDATE_DECK.tsv", candidate_audit)
    write_tsv(ART / "V99R7_28_EDITORIAL_SCOPE_PRECEDENCE_AUDIT.tsv", editorial_scope)
    write_tsv(ART / "V99R7_TOP100_RESIDUAL_SPLIT_INVENTORY.tsv", top_residual)
    write_tsv(ART / "V99R7_531_POSITION_DELTA.tsv", delta)
    write_tsv(ART / "V99R7_32339_COMPACT_CELL_REGISTER.tsv", cells)
    write_tsv(ART / "V99R7_4128_INTEGRATED_LINE_READER.tsv", lines)
    write_tsv(ART / "V99R7_50_CHANGE_DENSE_PASSAGES.tsv", dense)
    write_tsv(ART / "V99R7_19_FAMILY_ROLE_MATRIX.tsv", role_matrix)
    write_tsv(ART / "HISTORICAL_MICROENTRY_COMPARATORS.tsv", historical)
    write_tsv(ART / "V99R7_BLOCKER_CENSUS.tsv", blockers)
    write_tsv(ART / "V99R7_RENDER_QUALITY_SUMMARY.tsv", quality)
    write_tsv(ART / "V99R7_INHERITED_ARTIFACT_PARITY.tsv", parity)
    (ART / "GDT734_V99R7_50_CHANGE_DENSE_READER.md").write_text(build_reader_markdown(dense), encoding="utf-8")
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    REPORT_PATH.write_text(build_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
