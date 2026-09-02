#!/usr/bin/env python3
"""Audit complete qX/X pairs against raw placement and prefix controls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
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
BASE_REL = Path("experiments/yolo/gdt751_q_base_carrier_shell_audit")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G750_RUN_REL = Path(
    "experiments/yolo/gdt750_form_gated_direct_host_dispatch/src/run.py"
)
G750_ACTIVE_REL = Path(
    "experiments/yolo/gdt750_form_gated_direct_host_dispatch/artifacts/"
    "ACTIVE_OCCURRENCE_CARDS.tsv"
)
LINES_REL = Path("transcription/voynich_zl3b_lines.tsv")
OUTPUT_NAMES = (
    "Q_BASE_51_PAIR_DECK.tsv",
    "Q_BASE_3761_OCCURRENCE_FEATURES.tsv",
    "NONQ_PREFIX_160_CONTROL_DECK.tsv",
    "MATCHED_51_CONTROL_MAP.tsv",
    "PAIR_GROUP_COMPARISON.tsv",
    "DIRECT_Q_BASE_CONTACTS.tsv",
    "OKEEY_10_CARRIER_ENRICHED_CARDS.tsv",
    "GDT751_Q_BASE_PAIR_READER.md",
    "GDT751_GDT388_Q_BASE_EDGE_PACKET.tsv",
    "GDT751_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
QUALITY_STAGE = (
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g750 = load_module("gdt750_builder_for_gdt751", ROOT / G750_RUN_REL)


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


def joined(values: Iterable[str]) -> str:
    order = g750.g749.AXIS_ORDER
    chosen = set(values)
    return "|".join(axis for axis in order if axis in chosen) or "NONE"


def mode_axes(rows: list[tuple[str, ...]]) -> tuple[tuple[str, ...], int]:
    counts = Counter(rows)
    maximum = max(counts.values())
    winner = min(value for value, count in counts.items() if count == maximum)
    return winner, maximum


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return sum(selected) / len(selected) if selected else 0.0


def rate_text(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.6f}" if denominator else "0.000000"


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def load_context() -> tuple[object, dict[str, dict[str, str]], dict[str, object]]:
    context = g750.Context()
    g738 = g750.g749.g746.g745.g739.g738
    pages = g738.g737.allowed_pages()
    line_rows, line_guard = g738.g737.g631.guarded_query(
        LINES_REL, pages,
        "page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean",
    )
    line_meta = {row["locus"]: row for row in line_rows}
    if set(context.by_line) - set(line_meta):
        raise AssertionError("guarded line metadata missing token loci")
    return context, line_meta, line_guard


def build_occurrence_universe(
    context: object,
    line_meta: dict[str, dict[str, str]],
) -> tuple[
    dict[str, list[dict[str, object]]],
    dict[str, list[tuple[str, ...]]],
    dict[str, float],
]:
    occurrences: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    clean_axes: defaultdict[str, list[tuple[str, ...]]] = defaultdict(list)
    section_values: defaultdict[str, list[float]] = defaultdict(list)
    for locus, line in context.by_line.items():
        meta = line_meta[locus]
        written = " ".join(token["eva"] for token in line)
        for ordinal, token in enumerate(line, start=1):
            exact = context.exact[(locus, int(token["token_index"]))]
            cell = context.cells[(locus, ordinal)]
            axes = tuple(g750.g749.g746.clean_axes(
                cell, exact, context.patterns
            ))
            if axes:
                clean_axes[token["eva"]].append(axes)
            if not exact:
                continue
            normalized = (ordinal - 1) / max(1, len(line) - 1)
            section_values[token["section"]].append(normalized)
            occurrences[token["eva"]].append({
                "surface": token["eva"],
                "page": token["page"],
                "physical_folio": g750.g749.g746.g745.physical_folio(token["page"]),
                "locus": locus,
                "token_ordinal": ordinal,
                "line_token_count": len(line),
                "normalized_position": normalized,
                "line_position": line_position(ordinal, len(line)),
                "line_first": int(ordinal == 1),
                "line_last": int(ordinal == len(line)),
                "paragraph_start_line": int(meta["paragraph_start"]),
                "paragraph_end_line": int(meta["paragraph_end"]),
                "paragraph_first_token": int(meta["paragraph_start"] == "1" and ordinal == 1),
                "paragraph_last_token": int(meta["paragraph_end"] == "1" and ordinal == len(line)),
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "left_surface": line[ordinal - 2]["eva"] if ordinal > 1 else "EDGE",
                "right_surface": line[ordinal]["eva"] if ordinal < len(line) else "EDGE",
                "written_line_eva": written,
            })
    section_means = {
        section: mean(values) for section, values in section_values.items()
    }
    return dict(occurrences), dict(clean_axes), section_means


def canonical_axis_deck(
    clean_rows: dict[str, list[tuple[str, ...]]]
) -> tuple[dict[str, set[str]], dict[str, int], dict[str, int]]:
    canonical: dict[str, set[str]] = {}
    support: dict[str, int] = {}
    totals: dict[str, int] = {}
    for surface, rows in clean_rows.items():
        selected, count = mode_axes(rows)
        canonical[surface] = set(selected)
        support[surface] = count
        totals[surface] = len(rows)
    return canonical, support, totals


def direct_contacts(
    prefix: str,
    base: str,
    occurrences: dict[str, list[dict[str, object]]],
    context: object,
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for occurrence in occurrences[prefix]:
        locus = str(occurrence["locus"])
        ordinal = int(occurrence["token_ordinal"])
        line = context.by_line[locus]
        for offset in (-1, 1):
            other_ordinal = ordinal + offset
            if not 1 <= other_ordinal <= len(line):
                continue
            token = line[other_ordinal - 1]
            if token["eva"] != base:
                continue
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            output.append({
                "page": occurrence["page"],
                "physical_folio": occurrence["physical_folio"],
                "locus": locus,
                "prefix_ordinal": ordinal,
                "base_ordinal": other_ordinal,
                "signed_base_from_prefix": offset,
                "written_order": "PREFIX_THEN_BASE" if offset == 1 else "BASE_THEN_PREFIX",
                "written_line_eva": occurrence["written_line_eva"],
            })
    return output


def pair_statistics(
    pair_id: str,
    prefix: str,
    base: str,
    canonical: dict[str, set[str]],
    support: dict[str, int],
    clean_totals: dict[str, int],
    occurrences: dict[str, list[dict[str, object]]],
    section_means: dict[str, float],
    context: object,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    prefix_rows = occurrences[prefix]
    base_rows = occurrences[base]
    contacts = direct_contacts(prefix, base, occurrences, context)

    def feature_delta(field: str) -> float:
        return mean(float(row[field]) for row in prefix_rows) - mean(
            float(row[field]) for row in base_rows
        )

    prefix_position = mean(float(row["normalized_position"]) for row in prefix_rows)
    base_position = mean(float(row["normalized_position"]) for row in base_rows)
    prefix_residual = mean(
        float(row["normalized_position"]) - section_means[str(row["section"])]
        for row in prefix_rows
    )
    base_residual = mean(
        float(row["normalized_position"]) - section_means[str(row["section"])]
        for row in base_rows
    )
    prefix_axes = canonical[prefix]
    base_axes = canonical[base]
    prefix_qs = prefix_axes & set(QUALITY_STAGE)
    base_qs = base_axes & set(QUALITY_STAGE)
    prep_relation = (
        "BOTH" if "PREPARATION" in prefix_axes and "PREPARATION" in base_axes
        else "PREFIX_ONLY" if "PREPARATION" in prefix_axes
        else "BASE_ONLY" if "PREPARATION" in base_axes
        else "NEITHER"
    )
    row = {
        "pair_id": pair_id,
        "prefix_character": prefix[0],
        "prefix_surface": prefix,
        "base_surface": base,
        "base_initial": base[0],
        "base_length": len(base),
        "prefix_canonical_axes": joined(prefix_axes),
        "base_canonical_axes": joined(base_axes),
        "prefix_quality_stage_axes": joined(prefix_qs),
        "base_quality_stage_axes": joined(base_qs),
        "quality_stage_exactly_preserved": int(prefix_qs == base_qs),
        "preparation_relation": prep_relation,
        "axes_shared": joined(prefix_axes & base_axes),
        "axes_prefix_only": joined(prefix_axes - base_axes),
        "axes_base_only": joined(base_axes - prefix_axes),
        "prefix_clean_mode_support": support[prefix],
        "prefix_clean_axis_occurrences": clean_totals[prefix],
        "base_clean_mode_support": support[base],
        "base_clean_axis_occurrences": clean_totals[base],
        "prefix_reader_exact_occurrences": len(prefix_rows),
        "base_reader_exact_occurrences": len(base_rows),
        "prefix_reader_exact_pages": len({row["page"] for row in prefix_rows}),
        "base_reader_exact_pages": len({row["page"] for row in base_rows}),
        "prefix_mean_normalized_position": f"{prefix_position:.6f}",
        "base_mean_normalized_position": f"{base_position:.6f}",
        "raw_position_delta_prefix_minus_base": f"{prefix_position - base_position:.6f}",
        "section_residual_position_delta_prefix_minus_base": f"{prefix_residual - base_residual:.6f}",
        "line_first_delta_prefix_minus_base": f"{feature_delta('line_first'):.6f}",
        "line_last_delta_prefix_minus_base": f"{feature_delta('line_last'):.6f}",
        "paragraph_first_delta_prefix_minus_base": f"{feature_delta('paragraph_first_token'):.6f}",
        "paragraph_last_delta_prefix_minus_base": f"{feature_delta('paragraph_last_token'):.6f}",
        "paragraph_start_line_delta_prefix_minus_base": f"{feature_delta('paragraph_start_line'):.6f}",
        "paragraph_end_line_delta_prefix_minus_base": f"{feature_delta('paragraph_end_line'):.6f}",
        "direct_contacts": len(contacts),
        "direct_contact_pages": len({item["page"] for item in contacts}),
        "prefix_then_base_contacts": sum(item["written_order"] == "PREFIX_THEN_BASE" for item in contacts),
        "base_then_prefix_contacts": sum(item["written_order"] == "BASE_THEN_PREFIX" for item in contacts),
        "contacts_per_1000_min_occurrences": f"{1000 * len(contacts) / min(len(prefix_rows), len(base_rows)):.6f}",
        "literal_identity": "OPEN",
        "confirmed_lexeme": 0,
        "component_export_credit": 0,
    }
    return row, contacts


def group_row(group_id: str, rows: list[dict[str, object]]) -> dict[str, object]:
    def avg(field: str) -> float:
        return mean(float(row[field]) for row in rows)

    contacts = sum(int(row["direct_contacts"]) for row in rows)
    min_occurrences = sum(min(
        int(row["prefix_reader_exact_occurrences"]),
        int(row["base_reader_exact_occurrences"]),
    ) for row in rows)
    raw = [float(row["raw_position_delta_prefix_minus_base"]) for row in rows]
    return {
        "group_id": group_id,
        "pair_count": len(rows),
        "reader_exact_prefix_occurrences": sum(int(row["prefix_reader_exact_occurrences"]) for row in rows),
        "reader_exact_base_occurrences": sum(int(row["base_reader_exact_occurrences"]) for row in rows),
        "quality_stage_exactly_preserved_pairs": sum(int(row["quality_stage_exactly_preserved"]) for row in rows),
        "preparation_base_only_pairs": sum(row["preparation_relation"] == "BASE_ONLY" for row in rows),
        "preparation_prefix_only_pairs": sum(row["preparation_relation"] == "PREFIX_ONLY" for row in rows),
        "mean_raw_position_delta_prefix_minus_base": f"{mean(raw):.6f}",
        "prefix_earlier_pairs": sum(value < 0 for value in raw),
        "prefix_later_pairs": sum(value > 0 for value in raw),
        "position_ties": sum(value == 0 for value in raw),
        "mean_section_residual_position_delta": f"{avg('section_residual_position_delta_prefix_minus_base'):.6f}",
        "mean_line_first_delta": f"{avg('line_first_delta_prefix_minus_base'):.6f}",
        "mean_line_last_delta": f"{avg('line_last_delta_prefix_minus_base'):.6f}",
        "mean_paragraph_first_delta": f"{avg('paragraph_first_delta_prefix_minus_base'):.6f}",
        "mean_paragraph_last_delta": f"{avg('paragraph_last_delta_prefix_minus_base'):.6f}",
        "mean_paragraph_start_line_delta": f"{avg('paragraph_start_line_delta_prefix_minus_base'):.6f}",
        "mean_paragraph_end_line_delta": f"{avg('paragraph_end_line_delta_prefix_minus_base'):.6f}",
        "direct_contact_pair_types": sum(int(row["direct_contacts"]) > 0 for row in rows),
        "direct_contacts": contacts,
        "contacts_per_1000_min_occurrences": f"{1000 * contacts / min_occurrences:.6f}",
        "literal_identity_credit": 0,
        "confirmed_lexeme": 0,
        "component_export_credit": 0,
    }


def match_controls(
    q_rows: list[dict[str, object]],
    controls: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    available = {str(row["pair_id"]): row for row in controls}
    matches: list[dict[str, object]] = []
    selected: list[dict[str, object]] = []
    ordered = sorted(
        q_rows,
        key=lambda row: (
            int(row["base_length"]),
            -min(int(row["prefix_reader_exact_occurrences"]), int(row["base_reader_exact_occurrences"])),
            str(row["pair_id"]),
        ),
    )
    for q_row in ordered:
        def cost(control: dict[str, object]) -> tuple[float, str]:
            value = (
                4.0 * abs(int(q_row["base_length"]) - int(control["base_length"]))
                + abs(math.log1p(int(q_row["prefix_reader_exact_occurrences"])) - math.log1p(int(control["prefix_reader_exact_occurrences"])))
                + abs(math.log1p(int(q_row["base_reader_exact_occurrences"])) - math.log1p(int(control["base_reader_exact_occurrences"])))
                + (0.0 if control["base_initial"] == "o" else 1.0)
            )
            return value, str(control["pair_id"])

        chosen = min(available.values(), key=cost)
        value = cost(chosen)[0]
        selected.append(chosen)
        matches.append({
            "gdt751_match_id": f"G751-M{len(matches) + 1:03d}",
            "q_pair_id": q_row["pair_id"],
            "q_surface": q_row["prefix_surface"],
            "q_base_surface": q_row["base_surface"],
            "control_pair_id": chosen["pair_id"],
            "control_prefix_character": chosen["prefix_character"],
            "control_prefix_surface": chosen["prefix_surface"],
            "control_base_surface": chosen["base_surface"],
            "match_cost_pre_outcome": f"{value:.6f}",
            "q_base_length": q_row["base_length"],
            "control_base_length": chosen["base_length"],
            "q_prefix_occurrences": q_row["prefix_reader_exact_occurrences"],
            "control_prefix_occurrences": chosen["prefix_reader_exact_occurrences"],
            "q_base_occurrences": q_row["base_reader_exact_occurrences"],
            "control_base_occurrences": chosen["base_reader_exact_occurrences"],
            "matching_used_position_or_semantic_outcome": 0,
            "component_export_credit": 0,
        })
        del available[str(chosen["pair_id"])]
    return matches, selected


def occurrence_rows(
    q_rows: list[dict[str, object]],
    occurrences: dict[str, list[dict[str, object]]],
    canonical: dict[str, set[str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for pair in q_rows:
        q_surface = str(pair["prefix_surface"])
        base = str(pair["base_surface"])
        for side, surface, paired in (
            ("Q_SIDE", q_surface, base), ("UNPREFIXED_SIDE", base, q_surface)
        ):
            for occurrence in occurrences[surface]:
                left = str(occurrence["left_surface"])
                right = str(occurrence["right_surface"])
                output.append({
                    "gdt751_occurrence_id": f"G751-O{len(output) + 1:04d}",
                    "pair_id": pair["pair_id"],
                    "pair_side": side,
                    "surface": surface,
                    "paired_surface": paired,
                    "page": occurrence["page"],
                    "physical_folio": occurrence["physical_folio"],
                    "locus": occurrence["locus"],
                    "token_ordinal": occurrence["token_ordinal"],
                    "line_token_count": occurrence["line_token_count"],
                    "normalized_position": f"{float(occurrence['normalized_position']):.6f}",
                    "line_position": occurrence["line_position"],
                    "line_first": occurrence["line_first"],
                    "line_last": occurrence["line_last"],
                    "paragraph_start_line": occurrence["paragraph_start_line"],
                    "paragraph_end_line": occurrence["paragraph_end_line"],
                    "paragraph_first_token": occurrence["paragraph_first_token"],
                    "paragraph_last_token": occurrence["paragraph_last_token"],
                    "section": occurrence["section"],
                    "language": occurrence["language"],
                    "hand": occurrence["hand"],
                    "left_surface": left,
                    "right_surface": right,
                    "direct_pair_contact": int(left == paired or right == paired),
                    "canonical_axes_inherited": joined(canonical[surface]),
                    "written_line_eva": occurrence["written_line_eva"],
                    "literal_identity": "OPEN",
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                })
    return output


def enriched_cards(
    q_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    pair_map = {str(row["prefix_surface"]): row for row in q_rows}
    active = read_tsv(ROOT / G750_ACTIVE_REL)
    selected = [
        row for row in active
        if row["target_surface"] == "okeey"
        and ":qokeey:" in row["contributing_hosts"]
    ]
    pair = pair_map["qokeey"]
    output: list[dict[str, object]] = []
    for row in selected:
        axes = set(g750.split_axes(row["emitted_axes"]))
        if axes == {"HOT", "END_STAGE"}:
            render = "heiße Zubereitung an der End-/Vollstufe"
        elif axes == {"HOT"}:
            render = "heiße Zubereitung"
        elif axes == {"END_STAGE"}:
            render = "Zubereitung an der End-/Vollstufe"
        else:
            render = f"Zubereitung; {row['working_render_de']}"
        output.append({
            "gdt751_carrier_card_id": f"G751-A{len(output) + 1:02d}",
            "gdt750_active_card_id": row["gdt750_active_card_id"],
            "target_surface": row["target_surface"],
            "q_pair_surface": "qokeey",
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "gdt750_emitted_axes": row["emitted_axes"],
            "added_carrier_role": "PREPARATION",
            "working_render_de": render,
            "local_direct_pair_host": row["contributing_hosts"],
            "pair_quality_stage_preserved": pair["quality_stage_exactly_preserved"],
            "pair_preparation_relation": pair["preparation_relation"],
            "confidence": "C2_EXPLORATORY_MODEL_INTERNAL_PLUS_DIRECT_PAIR",
            "scope": "THIS_OCCURRENCE_ONLY",
            "written_line_eva": row["written_line_eva"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    groups: list[dict[str, object]],
    q_rows: list[dict[str, object]],
    contacts: list[dict[str, object]],
    enriched: list[dict[str, object]],
) -> None:
    group_map = {str(row["group_id"]): row for row in groups}
    q_group = group_map["Q_PREFIX_51"]
    nonq = group_map["ALL_NONQ_PREFIX_160"]
    o_control = group_map["NONQ_O_BASE_PREFIX_14"]
    lines = [
        "# GDT751 q/base complete-pair reader", "",
        "The inherited renderer encodes a strong q/base carrier asymmetry, but",
        "raw placement does not make q a special entry shell relative to other",
        "one-character prefix pairs. Direct q/base pairing remains enriched.", "",
        "## Group comparison", "",
        "| group | pairs | mean position delta | earlier/later | QS same | base-only PREP | contacts/rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in groups:
        lines.append(
            f"| {row['group_id']} | {row['pair_count']} | "
            f"{float(row['mean_raw_position_delta_prefix_minus_base']):.3f} | "
            f"{row['prefix_earlier_pairs']}/{row['prefix_later_pairs']} | "
            f"{row['quality_stage_exactly_preserved_pairs']} | "
            f"{row['preparation_base_only_pairs']} | "
            f"{row['direct_contacts']}/{float(row['contacts_per_1000_min_occurrences']):.1f} |"
        )
    lines.extend([
        "", "## Decision", "",
        f"- q position delta `{q_group['mean_raw_position_delta_prefix_minus_base']}` is not more entry-biased than all non-q controls `{nonq['mean_raw_position_delta_prefix_minus_base']}` or o-base controls `{o_control['mean_raw_position_delta_prefix_minus_base']}`.",
        f"- q/base direct contact density is `{q_group['contacts_per_1000_min_occurrences']}` per 1,000 minimum-side occurrences versus `{nonq['contacts_per_1000_min_occurrences']}` for all non-q prefix pairs.",
        "- Keep qX/X as a real complete-pair alternation. Keep the PREPARATION toggle as an inherited working hypothesis, not an EVA q meaning.",
        "", "## Ten locally enriched `okeey` cards", "",
    ])
    for row in enriched:
        lines.append(
            f"- `{row['locus']}`: **{row['working_render_de']}**; "
            f"host `{row['local_direct_pair_host']}`; `{row['written_line_eva']}`"
        )
    lines.extend([
        "", "## Direct pair concentration", "",
        f"The deck contains {len(contacts)} reader-exact direct contacts. The most frequent pair is `qokeey/okeey` with "
        f"{sum(row['q_surface'] == 'qokeey' for row in contacts)} contacts.", "",
        "No line above identifies a plaintext word, and no q character or substring value is exported.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path,
    contacts: list[dict[str, object]],
) -> dict[str, object]:
    packet: list[dict[str, object]] = []
    for number, contact in enumerate(contacts, start=1):
        packet.append({
            "edge_id": f"G751E{number:03d}",
            "batch_id": "GDT751_Q_BASE_COMPLETE_PAIR",
            "page": contact["page"],
            "physical_folio": contact["physical_folio"],
            "diagram_unit_id": "CACHED_TEXT_Q_BASE_COMPLETE_PAIR",
            "pivot_visual_id": f"Q_WHOLE_{contact['q_surface']}",
            "pivot_locus": f"{contact['locus']}@{contact['q_ordinal']}",
            "target_visual_id": f"BASE_WHOLE_{contact['base_surface']}",
            "target_locus": f"{contact['locus']}@{contact['base_ordinal']}",
            "relation_type": "DIRECT_Q_BASE_COMPLETE_WHOLE_PAIR",
            "direction_basis": "FORMAL_PAIR_RECURRENCE_AND_RENDERER_ROLE",
            "ownership_basis": "READER_EXACT_ADJACENT_COMPLETE_SURFACES",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT751",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT751_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "FORMAL_DIRECT_PAIR_SEMANTIC_TOGGLE_INHERITED",
            "ambiguity_state": "Q_CHARACTER_VALUE_OPEN_COMPLETE_PAIR_ONLY",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
        })
    path = output_dir / "GDT751_GDT388_Q_BASE_EDGE_PACKET.tsv"
    write_tsv(path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(path)],
        cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("GDT751 packet unexpectedly score-ready")
    (output_dir / "GDT751_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    context, line_meta, line_guard = load_context()
    occurrences, clean_rows, section_means = build_occurrence_universe(
        context, line_meta
    )
    canonical, support, clean_totals = canonical_axis_deck(clean_rows)
    prefix_pairs = [
        (surface, surface[1:], surface[0])
        for surface in sorted(canonical)
        if len(surface) > 1 and surface[1:] in canonical
    ]
    q_pairs = [pair for pair in prefix_pairs if pair[2] == "q"]
    nonq_pairs = [pair for pair in prefix_pairs if pair[2] != "q"]
    if len(q_pairs) != 51 or len(nonq_pairs) != 160:
        raise AssertionError("clean prefix-pair universe changed")

    q_rows: list[dict[str, object]] = []
    q_contacts: list[dict[str, object]] = []
    for prefix, base, _ in q_pairs:
        pair_id = f"G751-Q{len(q_rows) + 1:03d}"
        row, contacts = pair_statistics(
            pair_id, prefix, base, canonical, support, clean_totals,
            occurrences, section_means, context,
        )
        q_rows.append(row)
        for contact in contacts:
            q_contacts.append({
                "gdt751_contact_id": f"G751-D{len(q_contacts) + 1:03d}",
                "pair_id": pair_id,
                "q_surface": prefix,
                "base_surface": base,
                "q_canonical_axes": row["prefix_canonical_axes"],
                "base_canonical_axes": row["base_canonical_axes"],
                "quality_stage_exactly_preserved": row["quality_stage_exactly_preserved"],
                "preparation_relation": row["preparation_relation"],
                "page": contact["page"],
                "physical_folio": contact["physical_folio"],
                "locus": contact["locus"],
                "q_ordinal": contact["prefix_ordinal"],
                "base_ordinal": contact["base_ordinal"],
                "signed_base_from_q": contact["signed_base_from_prefix"],
                "written_order": contact["written_order"].replace("PREFIX", "Q"),
                "written_line_eva": contact["written_line_eva"],
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })

    control_rows: list[dict[str, object]] = []
    for prefix, base, _ in nonq_pairs:
        pair_id = f"G751-C{len(control_rows) + 1:03d}"
        row, _ = pair_statistics(
            pair_id, prefix, base, canonical, support, clean_totals,
            occurrences, section_means, context,
        )
        control_rows.append(row)
    matches, matched_controls = match_controls(q_rows, control_rows)
    o_base_controls = [row for row in control_rows if row["base_initial"] == "o"]

    groups = [
        group_row("Q_PREFIX_51", q_rows),
        group_row("MATCHED_NONQ_PREFIX_51", matched_controls),
        group_row("ALL_NONQ_PREFIX_160", control_rows),
        group_row("NONQ_O_BASE_PREFIX_14", o_base_controls),
    ]
    occurrence_deck = occurrence_rows(q_rows, occurrences, canonical)
    enriched = enriched_cards(q_rows)
    if len(occurrence_deck) != 3761 or len(q_contacts) != 44 or len(enriched) != 10:
        raise AssertionError("GDT751 core counts changed")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / OUTPUT_NAMES[0], q_rows, list(q_rows[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], occurrence_deck, list(occurrence_deck[0]))
    write_tsv(output_dir / OUTPUT_NAMES[2], control_rows, list(control_rows[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], matches, list(matches[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], groups, list(groups[0]))
    write_tsv(output_dir / OUTPUT_NAMES[5], q_contacts, list(q_contacts[0]))
    write_tsv(output_dir / OUTPUT_NAMES[6], enriched, list(enriched[0]))
    write_reader(
        output_dir / OUTPUT_NAMES[7], groups, q_rows, q_contacts, enriched
    )
    intake = edge_packet(output_dir, q_contacts)

    group_map = {str(row["group_id"]): row for row in groups}
    q_group = group_map["Q_PREFIX_51"]
    all_control = group_map["ALL_NONQ_PREFIX_160"]
    o_control = group_map["NONQ_O_BASE_PREFIX_14"]
    q_specific_position = (
        float(q_group["mean_raw_position_delta_prefix_minus_base"])
        < min(
            float(all_control["mean_raw_position_delta_prefix_minus_base"]),
            float(o_control["mean_raw_position_delta_prefix_minus_base"]),
        )
    )
    contact_ratio = (
        float(q_group["contacts_per_1000_min_occurrences"])
        / float(all_control["contacts_per_1000_min_occurrences"])
    )
    status = (
        "PARTIAL__51_Q_BASE_PAIRS__3761_EXACT_OCCURRENCES__"
        "47_QS_PRESERVED_INHERITED__41_BASE_ONLY_PREPARATION_INHERITED__"
        "Q_POSITION_EFFECT_NOT_SPECIFIC__44_DIRECT_CONTACTS_12_PAIR_TYPES__"
        "10_OKEEY_PREPARATION_CARDS__ZERO_Q_COMPONENT_EXPORT__NO_NEW_PAGE"
    )
    result = {
        "schema": "GDT751_RESULT_V1",
        "status": status,
        "question": (
            "Do fifty-one clean complete qX/X pairs support a q-specific raw "
            "carrier shell beyond matched non-q prefix effects, and which local "
            "GDT750 okeey cards can receive a preparation carrier?"
        ),
        "scope": {
            "allowed_pages": context.guard["allowed_pages"],
            "clean_complete_surfaces": len(canonical),
            "all_prefix_pairs": len(prefix_pairs),
            "q_base_pairs": len(q_rows),
            "nonq_prefix_controls": len(control_rows),
            "q_reader_exact_occurrences": sum(int(row["prefix_reader_exact_occurrences"]) for row in q_rows),
            "base_reader_exact_occurrences": sum(int(row["base_reader_exact_occurrences"]) for row in q_rows),
            "direct_q_base_contacts": len(q_contacts),
            "direct_q_base_pair_types": sum(int(row["direct_contacts"]) > 0 for row in q_rows),
            "direct_q_base_pages": len({row["page"] for row in q_contacts}),
            "okeey_carrier_enriched_positions": len(enriched),
        },
        "inherited_semantic_pattern": {
            "quality_stage_exactly_preserved_pairs": int(q_group["quality_stage_exactly_preserved_pairs"]),
            "preparation_base_only_pairs": int(q_group["preparation_base_only_pairs"]),
            "preparation_q_only_pairs": int(q_group["preparation_prefix_only_pairs"]),
            "evidence_status": "MODEL_INTERNAL_NOT_INDEPENDENT",
        },
        "independent_formal_controls": {
            "q_mean_position_delta": float(q_group["mean_raw_position_delta_prefix_minus_base"]),
            "matched_control_mean_position_delta": float(group_map["MATCHED_NONQ_PREFIX_51"]["mean_raw_position_delta_prefix_minus_base"]),
            "all_nonq_mean_position_delta": float(all_control["mean_raw_position_delta_prefix_minus_base"]),
            "nonq_o_base_mean_position_delta": float(o_control["mean_raw_position_delta_prefix_minus_base"]),
            "q_specific_entry_position_supported": q_specific_position,
            "q_contacts_per_1000_min_occurrences": float(q_group["contacts_per_1000_min_occurrences"]),
            "all_nonq_contacts_per_1000_min_occurrences": float(all_control["contacts_per_1000_min_occurrences"]),
            "q_to_nonq_contact_density_ratio": round(contact_ratio, 6),
            "direct_pair_relation": "WEAK_ENRICHMENT_COMPLETE_PAIR_RELATION",
        },
        "working_decision": (
            "Retain qX/X as a real complete-pair alternation and preserve the "
            "inherited preparation toggle only as a model-internal working "
            "hypothesis. Raw position does not support a q-specific entry shell. "
            "At the ten GDT750 okeey positions directly hosted by qokeey, add "
            "occurrence-local PREPARATION and render a hot end-stage preparation."
        ),
        "edge_intake": {
            "status": intake["status"],
            "score_ready": intake["score_ready"],
            "errors": intake["errors"],
        },
        "guard": {
            "tokens_cross": context.guard,
            "lines": line_guard,
        },
        "claim_ceiling": (
            "Complete-pair and occurrence-local renderer hypotheses only. No q "
            "character, prefix, morpheme, sound, abbreviation, substring, lexeme, "
            "literal preparation, ingredient, plant, disease, cure, person, vessel, "
            "unit, plaintext, unseen form, image, transcription, new page, f84 or f84r."
        ),
        "inputs": {
            str(G750_RUN_REL): sha256(ROOT / G750_RUN_REL),
            str(G750_ACTIVE_REL): sha256(ROOT / G750_ACTIVE_REL),
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
    print(json.dumps(build(args.output_dir.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
