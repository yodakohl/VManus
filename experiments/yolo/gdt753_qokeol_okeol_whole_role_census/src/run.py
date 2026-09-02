#!/usr/bin/env python3
"""Test qokeol/okeol complete-whole roles across every exact occurrence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt753_qokeol_okeol_whole_role_census")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G752_RUN_REL = Path(
    "experiments/yolo/gdt752_q_base_microfield_role_audit/src/run.py"
)
G751_PAIR_REL = Path(
    "experiments/yolo/gdt751_q_base_carrier_shell_audit/artifacts/"
    "Q_BASE_51_PAIR_DECK.tsv"
)
G751_CONTROL_REL = Path(
    "experiments/yolo/gdt751_q_base_carrier_shell_audit/artifacts/"
    "NONQ_PREFIX_160_CONTROL_DECK.tsv"
)
G664_DECISION_REL = Path(
    "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/"
    "artifacts/TARGET_DECISION_DECK.tsv"
)
G666_DECISION_REL = Path(
    "experiments/yolo/gdt666_one_hundred_fifty_one_residual_family_completion/"
    "artifacts/TARGET_DECISION_DECK.tsv"
)
TARGET_PREFIX = "qokeol"
TARGET_BASE = "okeol"
TARGET_PAIR_ID = "G751-Q025"
CONTROL_COUNT_PER_GROUP = 5
STATUS = (
    "PARTIAL__75_EXACT_TARGET_OCCURRENCES_40_PAGES__34_COMPLETE_FIELDS__"
    "Q_PROCESS_MATERIAL_MIDDLE_3_BASE_4__Q_PREPARATION_6_BASE_8__"
    "DIRECTIONAL_GATE_FAILS__TEN_MATCHED_PAIR_GATES_ZERO__"
    "GDT664_GDT666_COMPOSITIONAL_PROSE_DEMOTED__"
    "SHARED_HEAT_MIDDLE_HYPOTHESIS_RETAINED__WHOLE_PAIR_LEAD_RETAINED__"
    "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "MATCHED_11_PAIR_CONTROL_DECK.tsv",
    "TARGET_AND_CONTROL_OCCURRENCE_FIELDS.tsv",
    "SURFACE_22_ROLE_CENSUS.tsv",
    "PAIR_11_ROLE_COMPARISON.tsv",
    "INHERITED_ROLE_PROVENANCE_AUDIT.tsv",
    "QOKEOL_OKEOL_75_OCCURRENCE_READER.tsv",
    "GDT753_QOKEOL_OKEOL_ROLE_READER.md",
    "RESULT.json",
)
QUALITY_STAGE = {
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "LEVEL_II", "LEVEL_III",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g752 = load_module("gdt752_builder_for_gdt753", ROOT / G752_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pair_cost(row: dict[str, str], target: dict[str, str]) -> float:
    prefix = int(row["prefix_reader_exact_occurrences"])
    base = int(row["base_reader_exact_occurrences"])
    target_prefix = int(target["prefix_reader_exact_occurrences"])
    target_base = int(target["base_reader_exact_occurrences"])
    return (
        2.0 * abs(int(row["base_length"]) - int(target["base_length"]))
        + abs(math.log((prefix + 1) / (target_prefix + 1)))
        + abs(math.log((base + 1) / (target_base + 1)))
    )


def select_pairs() -> list[dict[str, object]]:
    q_pairs = read_tsv(ROOT / G751_PAIR_REL)
    controls = read_tsv(ROOT / G751_CONTROL_REL)
    target = next(row for row in q_pairs if row["pair_id"] == TARGET_PAIR_ID)

    def ranked(rows: list[dict[str, str]]) -> list[dict[str, str]]:
        return sorted(rows, key=lambda row: (pair_cost(row, target), row["pair_id"]))

    selected: list[tuple[str, dict[str, str], int]] = [
        ("TARGET_Q_PAIR", target, 0)
    ]
    for rank, row in enumerate(
        ranked([row for row in q_pairs if row["pair_id"] != TARGET_PAIR_ID])[
            :CONTROL_COUNT_PER_GROUP
        ], start=1,
    ):
        selected.append(("MATCHED_Q_PAIR", row, rank))
    for rank, row in enumerate(ranked(controls)[:CONTROL_COUNT_PER_GROUP], start=1):
        selected.append(("MATCHED_NONQ_PAIR", row, rank))

    output: list[dict[str, object]] = []
    for number, (group, row, rank) in enumerate(selected, start=1):
        output.append({
            "gdt753_pair_id": f"G753-P{number:02d}",
            "comparison_group": group,
            "source_pair_id": row["pair_id"],
            "control_rank_within_group": rank,
            "prefix_character": row["prefix_character"],
            "prefix_surface": row["prefix_surface"],
            "base_surface": row["base_surface"],
            "base_length": row["base_length"],
            "prefix_reader_exact_occurrences": row["prefix_reader_exact_occurrences"],
            "base_reader_exact_occurrences": row["base_reader_exact_occurrences"],
            "pre_outcome_match_cost": f"{pair_cost(row, target):.6f}",
            "matching_used_position_semantics_or_role_outcome": 0,
            "source_prefix_canonical_axes_not_used_for_matching": row["prefix_canonical_axes"],
            "source_base_canonical_axes_not_used_for_matching": row["base_canonical_axes"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def scan_side(
    context: object,
    locus: str,
    target_ordinal: int,
    direction: int,
    pair_surfaces: set[str],
) -> tuple[list[dict[str, object]], str]:
    line = context.by_line[locus]
    span: list[dict[str, object]] = []
    boundary = "RADIUS5_CENSORED"
    for distance in range(1, 6):
        ordinal = target_ordinal + direction * distance
        if not 1 <= ordinal <= len(line):
            boundary = f"LINE_EDGE_AFTER_R{distance - 1}"
            break
        token, cell, axes = g752.clean_cell(context, locus, ordinal)
        surface = token["eva"]
        if surface in pair_surfaces:
            boundary = f"PAIR_SURFACE_BEFORE_R{distance}"
            break
        if g752.g751.g750.g749.g746.g745.g739.strict_initial_head(surface):
            boundary = f"STRICT_INITIAL_BEFORE_R{distance}"
            break
        if direction == -1 and "CLOSE" in axes:
            boundary = f"PRIOR_CLOSE_BEFORE_R{distance}"
            break
        span.append({
            "side": "L" if direction == -1 else "R",
            "distance": distance,
            "ordinal": ordinal,
            "surface": surface,
            "semantic": cell["v99r7_semantic_value_de"],
            "confidence": cell["gdt734_confidence_level"],
            "unknown": int(cell["unknown_v99r7"]),
            "axes": axes,
        })
        if direction == 1 and "CLOSE" in axes:
            boundary = f"CURRENT_CLOSE_INCLUDED_R{distance}"
            break
    return span, boundary


def centered_field(
    context: object,
    rules: list[dict[str, str]],
    locus: str,
    ordinal: int,
    pair_surfaces: set[str],
) -> dict[str, object]:
    left, left_reason = scan_side(context, locus, ordinal, -1, pair_surfaces)
    right, right_reason = scan_side(context, locus, ordinal, 1, pair_surfaces)
    span = left + right
    anchors = [item for item in span if item["axes"]]
    tags = {axis for item in anchors for axis in item["axes"]}
    channel = g752.g744.channel_for(tags, rules)
    evidence = " || ".join(
        f"{item['side']}{item['distance']} {item['surface']}={item['semantic']}"
        f" [{g752.joined(item['axes'])};{item['confidence']}]"
        for item in sorted(anchors, key=lambda item: int(item["ordinal"]))
    ) or "NONE"
    complete = int(
        not left_reason.startswith("RADIUS5")
        and not right_reason.startswith("RADIUS5")
    )
    return {
        "left_extent": len(left),
        "right_extent": len(right),
        "left_boundary_reason": left_reason,
        "right_boundary_reason": right_reason,
        "boundary_complete": complete,
        "anchor_count": len(anchors),
        "anchor_surfaces": "|".join(str(item["surface"]) for item in anchors) or "NONE",
        "anchor_tags": g752.joined(tags),
        "anchor_evidence": evidence,
        "field_channel": channel,
        "slot_class": g752.g744.content_slot_class(channel, tags),
        "slot_label_de": g752.g744.slot_label_de(channel, tags),
        "process_or_material_middle_support": int(
            complete and "MIDDLE_STAGE" in tags
            and bool({"PROCESS", "MATERIAL"} & tags)
        ),
        "preparation_support": int(complete and "PREPARATION" in tags),
        "quality_stage_support": int(complete and bool(tags & QUALITY_STAGE)),
        "process_support": int(complete and "PROCESS" in tags),
        "material_support": int(complete and "MATERIAL" in tags),
        "middle_stage_support": int(complete and "MIDDLE_STAGE" in tags),
        "unknown_cells_inside": sum(int(item["unknown"]) for item in span),
    }


def occurrence_rows(
    pairs: list[dict[str, object]], context: object,
    rules: list[dict[str, str]],
) -> list[dict[str, object]]:
    pair_by_surface: defaultdict[str, list[tuple[dict[str, object], str]]] = defaultdict(list)
    for pair in pairs:
        pair_by_surface[str(pair["prefix_surface"])].append((pair, "PREFIX"))
        pair_by_surface[str(pair["base_surface"])].append((pair, "BASE"))

    output: list[dict[str, object]] = []
    number = 0
    for locus, line in context.by_line.items():
        written = " ".join(token["eva"] for token in line)
        for ordinal, token in enumerate(line, start=1):
            memberships = pair_by_surface.get(token["eva"], [])
            if not memberships:
                continue
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            for pair, side in memberships:
                number += 1
                pair_surfaces = {
                    str(pair["prefix_surface"]), str(pair["base_surface"])
                }
                field = centered_field(context, rules, locus, ordinal, pair_surfaces)
                cell = context.cells[(locus, ordinal)]
                row: dict[str, object] = {
                    "gdt753_occurrence_id": f"G753-O{number:04d}",
                    "gdt753_pair_id": pair["gdt753_pair_id"],
                    "comparison_group": pair["comparison_group"],
                    "pair_side": side,
                    "surface": token["eva"],
                    "paired_surface": (
                        pair["base_surface"] if side == "PREFIX"
                        else pair["prefix_surface"]
                    ),
                    "page": token["page"],
                    "physical_folio": g752.g751.g750.g749.g746.g745.physical_folio(token["page"]),
                    "locus": locus,
                    "token_ordinal": ordinal,
                    "line_token_count": len(line),
                    "normalized_position": f"{(ordinal - 1) / max(1, len(line) - 1):.6f}",
                    "current_inherited_semantic_value_de_not_used_as_field_anchor": cell["v99r7_semantic_value_de"],
                    "current_inherited_confidence_not_used_for_field_anchor": cell["gdt734_confidence_level"],
                    "current_inherited_authority_not_used_for_field_anchor": cell["gdt734_authority_id"],
                    "current_inherited_dispatch_not_used_for_field_anchor": cell["gdt734_dispatch_class"],
                    "written_line_eva": written,
                }
                row.update(field)
                row.update({
                    "literal_identity": "OPEN",
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                })
                output.append(row)
    return output


def provenance_audit_rows(
    occurrences: list[dict[str, object]],
    target_comparison: dict[str, object],
) -> list[dict[str, object]]:
    """Trace the two concrete readings back to their actual analyst cards."""
    sources = {
        TARGET_BASE: (
            "GDT664", G664_DECISION_REL,
            "Grundansatz bis zur mittleren Heizstufe erwärmt",
            "O_PREP+K_HOT+E_MIDDLE+OL_BASE",
        ),
        TARGET_PREFIX: (
            "GDT666", G666_DECISION_REL,
            "erhitze den Drogenstoff bis zur Mittelstufe",
            "QO_COMMAND+K_HOT+E_MIDDLE+OL_MATERIAL",
        ),
    }
    target_rows = [
        row for row in occurrences if row["comparison_group"] == "TARGET_Q_PAIR"
    ]
    output: list[dict[str, object]] = []
    for surface in (TARGET_PREFIX, TARGET_BASE):
        experiment, path, expected_default, expected_composition = sources[surface]
        source = next(row for row in read_tsv(ROOT / path) if row["surface"] == surface)
        if source["working_default_de"] != expected_default:
            raise AssertionError(f"{surface} source default changed")
        if source["composition"] != expected_composition:
            raise AssertionError(f"{surface} source composition changed")
        rows = [row for row in target_rows if row["surface"] == surface]
        semantics = sorted({
            str(row["current_inherited_semantic_value_de_not_used_as_field_anchor"])
            for row in rows
        })
        confidence = sorted({
            str(row["current_inherited_confidence_not_used_for_field_anchor"])
            for row in rows
        })
        authorities = sorted({
            str(row["current_inherited_authority_not_used_for_field_anchor"])
            for row in rows
        })
        dispatches = sorted({
            str(row["current_inherited_dispatch_not_used_for_field_anchor"])
            for row in rows
        })
        output.append({
            "surface": surface,
            "current_reader_exact_occurrences": len(rows),
            "current_reader_exact_pages": len({str(row["page"]) for row in rows}),
            "current_inherited_value_de": " || ".join(semantics),
            "current_inherited_confidence": "|".join(confidence),
            "current_inherited_authority": "|".join(authorities),
            "current_inherited_dispatch": "|".join(dispatches),
            "source_experiment": experiment,
            "source_decision_id": source["decision_id"],
            "source_card_type": source["card_type"],
            "source_working_default_de": source["working_default_de"],
            "source_composition": source["composition"],
            "source_strength": source["strength"],
            "source_status": source["status"],
            "independent_directional_whole_role_gate": target_comparison["cross_page_directional_role_gate"],
            "provenance_finding": "CONCRETE_PROSE_DERIVED_FROM_ANALYST_COMPONENT_COMPOSITION",
            "current_spoken_disposition": "DEMOTE_LITERAL_COMMAND_PATIENT_AND_PREPARATION_ROLE",
            "current_working_whole_default_de": "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen",
            "retained_background_hypothesis_de": "Wärme-/Mittelstufenbezug; genaue Operation und Stoffrolle offen",
            "whole_pair_relation": "RETAIN_COMPLETE_FORM_PAIR_LEAD",
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def surface_census(
    pairs: list[dict[str, object]], occurrences: list[dict[str, object]]
) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[(str(row["gdt753_pair_id"]), str(row["pair_side"]))].append(row)
    output: list[dict[str, object]] = []
    for pair in pairs:
        for side, surface in (
            ("PREFIX", pair["prefix_surface"]), ("BASE", pair["base_surface"])
        ):
            rows = grouped[(str(pair["gdt753_pair_id"]), side)]
            complete = [row for row in rows if int(row["boundary_complete"])]
            process_mid = [
                row for row in complete
                if int(row["process_or_material_middle_support"])
            ]
            preparation = [
                row for row in complete if int(row["preparation_support"])
            ]
            output.append({
                "gdt753_surface_id": f"{pair['gdt753_pair_id']}-{side}",
                "gdt753_pair_id": pair["gdt753_pair_id"],
                "comparison_group": pair["comparison_group"],
                "pair_side": side,
                "surface": surface,
                "reader_exact_occurrences": len(rows),
                "reader_exact_pages": len({str(row["page"]) for row in rows}),
                "complete_fields": len(complete),
                "complete_field_pages": len({str(row["page"]) for row in complete}),
                "anchored_complete_fields": sum(int(row["anchor_count"]) > 0 for row in complete),
                "process_or_material_middle_support_fields": len(process_mid),
                "process_or_material_middle_support_pages": len({str(row["page"]) for row in process_mid}),
                "preparation_support_fields": len(preparation),
                "preparation_support_pages": len({str(row["page"]) for row in preparation}),
                "process_support_fields": sum(int(row["process_support"]) for row in complete),
                "material_support_fields": sum(int(row["material_support"]) for row in complete),
                "middle_stage_support_fields": sum(int(row["middle_stage_support"]) for row in complete),
                "quality_stage_support_fields": sum(int(row["quality_stage_support"]) for row in complete),
                "process_or_material_middle_rate": f"{len(process_mid) / len(complete):.6f}" if complete else "0.000000",
                "preparation_rate": f"{len(preparation) / len(complete):.6f}" if complete else "0.000000",
                "channel_counts_complete": "|".join(
                    f"{name}:{count}" for name, count in sorted(
                        Counter(str(row["field_channel"]) for row in complete).items()
                    )
                ) or "NONE",
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output


def pair_comparison(
    pairs: list[dict[str, object]], census: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_pair_side = {
        (row["gdt753_pair_id"], row["pair_side"]): row for row in census
    }
    output: list[dict[str, object]] = []
    for pair in pairs:
        prefix = by_pair_side[(pair["gdt753_pair_id"], "PREFIX")]
        base = by_pair_side[(pair["gdt753_pair_id"], "BASE")]
        process_delta = float(prefix["process_or_material_middle_rate"]) - float(
            base["process_or_material_middle_rate"]
        )
        prep_delta = float(base["preparation_rate"]) - float(prefix["preparation_rate"])
        cross_page = int(
            int(prefix["process_or_material_middle_support_pages"]) >= 2
            and int(base["preparation_support_pages"]) >= 2
            and process_delta > 0
            and prep_delta > 0
        )
        output.append({
            "gdt753_pair_id": pair["gdt753_pair_id"],
            "comparison_group": pair["comparison_group"],
            "source_pair_id": pair["source_pair_id"],
            "prefix_surface": pair["prefix_surface"],
            "base_surface": pair["base_surface"],
            "pre_outcome_match_cost": pair["pre_outcome_match_cost"],
            "prefix_complete_fields": prefix["complete_fields"],
            "base_complete_fields": base["complete_fields"],
            "prefix_process_material_middle_fields": prefix["process_or_material_middle_support_fields"],
            "prefix_process_material_middle_pages": prefix["process_or_material_middle_support_pages"],
            "base_process_material_middle_fields": base["process_or_material_middle_support_fields"],
            "base_process_material_middle_pages": base["process_or_material_middle_support_pages"],
            "prefix_preparation_fields": prefix["preparation_support_fields"],
            "prefix_preparation_pages": prefix["preparation_support_pages"],
            "base_preparation_fields": base["preparation_support_fields"],
            "base_preparation_pages": base["preparation_support_pages"],
            "process_material_middle_rate_delta_prefix_minus_base": f"{process_delta:.6f}",
            "preparation_rate_delta_base_minus_prefix": f"{prep_delta:.6f}",
            "cross_page_directional_role_gate": cross_page,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def target_reader_rows(
    occurrences: list[dict[str, object]]
) -> list[dict[str, object]]:
    rows = [
        row for row in occurrences if row["comparison_group"] == "TARGET_Q_PAIR"
    ]
    output: list[dict[str, object]] = []
    for number, row in enumerate(rows, start=1):
        if not int(row["boundary_complete"]):
            decision = "CENSORED_FIELD_NO_ROLE_CREDIT"
            render = f"{row['surface']}: Ganzformrolle offen (Feld abgeschnitten)"
        elif int(row["process_or_material_middle_support"]):
            decision = "PROCESS_MATERIAL_MIDDLE_CONTEXT"
            render = f"{row['surface']}: Mittelstufen-Verarbeitungs-/Stoffkontext"
        elif int(row["preparation_support"]):
            decision = "PREPARATION_CONTEXT"
            render = f"{row['surface']}: Zubereitungskontext; genaue Ganzformrolle offen"
        elif int(row["anchor_count"]):
            decision = "OTHER_ANCHORED_CONTEXT"
            render = f"{row['surface']}: {row['field_channel']}; genaue Ganzformrolle offen"
        else:
            decision = "COMPLETE_OPEN_CONTEXT"
            render = f"{row['surface']}: Ganzformrolle offen"
        output.append({
            "gdt753_reader_id": f"G753-R{number:03d}",
            "gdt753_occurrence_id": row["gdt753_occurrence_id"],
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "boundary_complete": row["boundary_complete"],
            "anchor_tags": row["anchor_tags"],
            "field_channel": row["field_channel"],
            "role_evidence_decision": decision,
            "old_composition_derived_render_de": row["current_inherited_semantic_value_de_not_used_as_field_anchor"],
            "old_concrete_render_disposition": "DEMOTED_TO_BACKGROUND_HYPOTHESIS",
            "current_working_whole_default_de": "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen",
            "safe_occurrence_render_de": render,
            "written_line_eva": row["written_line_eva"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    pairs: list[dict[str, object]],
    surface_rows: list[dict[str, object]],
    comparisons: list[dict[str, object]],
    provenance: list[dict[str, object]],
) -> None:
    target = next(row for row in comparisons if row["comparison_group"] == "TARGET_Q_PAIR")
    surfaces = {
        (row["gdt753_pair_id"], row["pair_side"]): row for row in surface_rows
    }
    tp = surfaces[(target["gdt753_pair_id"], "PREFIX")]
    tb = surfaces[(target["gdt753_pair_id"], "BASE")]
    lines = [
        "# GDT753 qokeol/okeol whole-role reader", "",
        "## Renderer correction", "",
        "| form | old concrete prose | actual source | current working whole default |",
        "|---|---|---|---|",
    ]
    for row in provenance:
        lines.append(
            f"| `{row['surface']}` | {row['source_working_default_de']} | "
            f"{row['source_experiment']} `{row['source_card_type']}` from "
            f"`{row['source_composition']}` | {row['current_working_whole_default_de']} |"
        )
    lines.extend([
        "",
        "Both old sentences came from analyst component composition, not an independent whole-word identification. The literal command/patient versus preparation split is therefore demoted. The shared heat/middle-stage idea remains available as an exploratory family hypothesis, while the exact operation and carrier stay open.",
        "",
        "## Target complete-field census", "",
        "| form | exact occurrences | complete fields | process/material+middle fields/pages | preparation fields/pages |",
        "|---|---:|---:|---:|---:|",
        f"| `qokeol` | {tp['reader_exact_occurrences']} | {tp['complete_fields']} | {tp['process_or_material_middle_support_fields']}/{tp['process_or_material_middle_support_pages']} | {tp['preparation_support_fields']}/{tp['preparation_support_pages']} |",
        f"| `okeol` | {tb['reader_exact_occurrences']} | {tb['complete_fields']} | {tb['process_or_material_middle_support_fields']}/{tb['process_or_material_middle_support_pages']} | {tb['preparation_support_fields']}/{tb['preparation_support_pages']} |",
        "",
        f"Directional cross-page gate: `{target['cross_page_directional_role_gate']}`; process delta `{target['process_material_middle_rate_delta_prefix_minus_base']}`; preparation delta `{target['preparation_rate_delta_base_minus_prefix']}`.",
        "", "## Outcome-free matched pairs", "",
        "| group | prefix/base | exact counts | cost | process delta | preparation delta | gate |",
        "|---|---|---|---:|---:|---:|---:|",
    ])
    pair_map = {row["gdt753_pair_id"]: row for row in pairs}
    for row in comparisons:
        pair = pair_map[row["gdt753_pair_id"]]
        lines.append(
            f"| {row['comparison_group']} | `{row['prefix_surface']}/{row['base_surface']}` | "
            f"{pair['prefix_reader_exact_occurrences']}/{pair['base_reader_exact_occurrences']} | "
            f"{row['pre_outcome_match_cost']} | {row['process_material_middle_rate_delta_prefix_minus_base']} | "
            f"{row['preparation_rate_delta_base_minus_prefix']} | {row['cross_page_directional_role_gate']} |"
        )
    lines.extend([
        "", "Pair members and their inherited current meanings never anchor their own fields. These are complete-whole role tests, not q substring evidence or plaintext.",
        "",
        "The two target distributions are nearly the same, so the data do not recover the old directional prose. The complete-form pair remains a live relation lead; no value is exported to EVA `q`, `o`, `k`, `e`, `ol`, or any substring.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pairs = select_pairs()
    context, _, line_guard = g752.g751.load_context()
    rules = g752.g744.load_channel_rules()
    occurrences = occurrence_rows(pairs, context, rules)
    census = surface_census(pairs, occurrences)
    comparisons = pair_comparison(pairs, census)
    reader_rows = target_reader_rows(occurrences)

    target_occurrences = [
        row for row in occurrences if row["comparison_group"] == "TARGET_Q_PAIR"
    ]
    if Counter(row["surface"] for row in target_occurrences) != Counter({
        TARGET_PREFIX: 34, TARGET_BASE: 41,
    }):
        raise AssertionError("target 34/41 exact occurrence deck changed")

    target_comparison = next(
        row for row in comparisons if row["comparison_group"] == "TARGET_Q_PAIR"
    )
    provenance = provenance_audit_rows(occurrences, target_comparison)

    write_tsv(output_dir / OUTPUT_NAMES[0], pairs, list(pairs[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], occurrences, list(occurrences[0]))
    write_tsv(output_dir / OUTPUT_NAMES[2], census, list(census[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], comparisons, list(comparisons[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], provenance, list(provenance[0]))
    write_tsv(output_dir / OUTPUT_NAMES[5], reader_rows, list(reader_rows[0]))
    write_reader(output_dir / OUTPUT_NAMES[6], pairs, census, comparisons, provenance)
    q_controls = [
        row for row in comparisons if row["comparison_group"] == "MATCHED_Q_PAIR"
    ]
    nonq_controls = [
        row for row in comparisons if row["comparison_group"] == "MATCHED_NONQ_PAIR"
    ]
    result = {
        "schema": "GDT753_RESULT_V1",
        "status": STATUS,
        "scope": {
            "target_prefix_exact_occurrences": 34,
            "target_base_exact_occurrences": 41,
            "target_total_exact_occurrences": 75,
            "target_combined_pages": len({str(row["page"]) for row in target_occurrences}),
            "target_complete_fields": sum(
                int(row["boundary_complete"]) for row in target_occurrences
            ),
            "matched_q_pairs": len(q_controls),
            "matched_nonq_pairs": len(nonq_controls),
            "total_pair_deck": len(pairs),
            "total_occurrence_fields": len(occurrences),
        },
        "target_role_result": target_comparison,
        "provenance_correction": provenance,
        "renderer_correction": {
            "old_qokeol_literal_prose_active": 0,
            "old_okeol_literal_prose_active": 0,
            "current_working_default_both": "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen",
            "shared_heat_middle_background_hypothesis_retained": 1,
            "complete_form_pair_lead_retained": 1,
        },
        "control_gate_counts": {
            "matched_q_directional_gates": sum(int(row["cross_page_directional_role_gate"]) for row in q_controls),
            "matched_nonq_directional_gates": sum(int(row["cross_page_directional_role_gate"]) for row in nonq_controls),
        },
        "guard": line_guard,
        "claim_boundary": {
            "q_component_export_credit": 0,
            "confirmed_lexemes": 0,
            "literal_process_or_preparation_words": 0,
            "plaintext_clauses": 0,
            "new_pages": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({
        "status": result["status"],
        "scope": result["scope"],
        "target": result["target_role_result"],
        "control_gates": result["control_gate_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
