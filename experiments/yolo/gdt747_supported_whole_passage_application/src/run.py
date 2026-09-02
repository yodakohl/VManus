#!/usr/bin/env python3
"""Apply GDT746's intersected complete-whole axes to cached passages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
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
BASE_REL = Path("experiments/yolo/gdt747_supported_whole_passage_application")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G745_RUN_REL = Path(
    "experiments/yolo/gdt745_exact_open_content_role_expansion/src/run.py"
)
G746_CENSUS_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "CANDIDATE_17_DISTRIBUTION_CENSUS.tsv"
)
G746_OCCURRENCE_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "SURFACE_63_OCCURRENCE_FEATURES.tsv"
)
G743_PATCH_REL = Path(
    "experiments/yolo/gdt743_r2_run_intersection_adjudication/artifacts/"
    "TARGET_202_RENDERER_PATCH_V5.tsv"
)
SAFE_VALUES_REL = BASE_REL / "src/PASSAGE_SAFE_VALUES.tsv"
BLOCK_SPECS_REL = BASE_REL / "src/PASSAGE_BLOCK_SPECS.tsv"
MANUAL_BLOCK_REL = BASE_REL / "src/MANUAL_BLOCK_ASSESSMENTS.tsv"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g745 = load_module("gdt745_builder_for_gdt747", ROOT / G745_RUN_REL)

AXIS_ORDER = tuple(g745.ANALOGY_TAG_ORDER)
RETIRED_LITERAL_WORDS = (
    "pulver", "samen", "saat", "wurzel", "holz", "blatt", "kraut", "pflanz",
    "wasser", "wein", "öl", "salz", "pfund", "handvoll", "gewichtseinheit",
)
GENERIC_WORDS = ("arbeitsgut", "arbeitschritt", "arbeitsmaterial")
OUTPUT_NAMES = (
    "SUPPORTED_12_PASSAGE_VALUES.tsv",
    "TOKEN_PASSAGE_RENDER.tsv",
    "OCCURRENCE_64_LOCAL_SUPPORT.tsv",
    "LINE_62_PASSAGE_CENSUS.tsv",
    "CANDIDATE_12_PASSAGE_CENSUS.tsv",
    "BLOCK_6_PASSAGE_CENSUS.tsv",
    "GDT747_SUPPORTED_WHOLE_PASSAGE_READER.md",
    "GDT747_GDT388_SERIAL_PARADIGM_EDGE_PACKET.tsv",
    "GDT747_GDT388_EDGE_INTAKE.json",
)


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


def split_values(value: str) -> set[str]:
    return set() if value in {"", "NONE", "OPEN", "NA"} else set(value.split("|"))


def joined(values: Iterable[str]) -> str:
    members = sorted(set(values))
    return "|".join(members) or "NONE"


def count_string(values: Iterable[str]) -> str:
    counter = Counter(values)
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter)) or "NONE"


def line_number(locus: str) -> int:
    match = re.search(r"\.(\d+)$", locus)
    if not match:
        raise AssertionError(f"cannot extract line number from {locus}")
    return int(match.group(1))


def semantic_axes(text: str, patterns: dict[str, object]) -> tuple[str, ...]:
    axes = set(g745.g739.axes_for(text, patterns))
    for name, pattern in g745.STAGE_PATTERNS.items():
        if pattern.search(text):
            axes.add(name)
    return tuple(axis for axis in AXIS_ORDER if axis in axes)


def safe_semantic(text: str) -> bool:
    lower = text.lower()
    return (
        bool(text)
        and not (text.startswith("[") and text.endswith(":?]"))
        and not any(word in lower for word in RETIRED_LITERAL_WORDS)
        and not any(word in lower for word in GENERIC_WORDS)
    )


def build_value_cards(
    g746_census: list[dict[str, str]], safe_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    supported = {
        row["candidate_surface"]: row
        for row in g746_census
        if row["distribution_status"].startswith(("S2_", "S3_"))
    }
    safe_map = {row["candidate_surface"]: row for row in safe_rows}
    if len(supported) != 12 or set(supported) != set(safe_map):
        raise AssertionError("supported candidate or passage-safe deck changed")
    output = []
    for candidate in sorted(supported):
        source = supported[candidate]
        manual = safe_map[candidate]
        expected = source["form_and_top5_axis_agreement"]
        if manual["passage_credit"] == "FORM_AND_DISTRIBUTION_INTERSECTION":
            if set(manual["passage_core_axes"].split("|")) != split_values(expected):
                raise AssertionError(f"passage axes do not match intersection for {candidate}")
        elif manual["passage_core_axes"] != "NONE" or expected != "NONE":
            raise AssertionError(f"form-only passage card mismatch for {candidate}")
        output.append({
            "gdt747_value_id": f"G747-V{len(output) + 1:02d}",
            "candidate_surface": candidate,
            "gdt746_distribution_status": source["distribution_status"],
            "gdt746_form_consensus_axes": source["gdt745_consensus_axes"],
            "gdt746_top5_consensus_axes": source["top5_distribution_consensus_axes"],
            "passage_core_axes": manual["passage_core_axes"],
            "passage_safe_value_de": manual["passage_safe_value_de"],
            "details_retained_as_rivals_de": manual["details_retained_as_rivals_de"],
            "passage_credit": manual["passage_credit"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def token_card(
    locus: str,
    ordinal: int,
    token: dict[str, str],
    cell: dict[str, str],
    reader_exact: int,
    value_map: dict[str, dict[str, object]],
    candidate_coordinates: set[tuple[str, int]],
    patch_map: dict[tuple[str, int], dict[str, str]],
    patterns: dict[str, object],
) -> dict[str, object]:
    coordinate = (locus, ordinal)
    surface = cell["surface"]
    if coordinate in candidate_coordinates:
        value = value_map[surface]
        axes = split_values(str(value["passage_core_axes"]))
        if value["passage_credit"] == "FORM_AND_DISTRIBUTION_INTERSECTION":
            source_class = "GDT746_FORM_DISTRIBUTION_INTERSECTION"
            after = str(value["passage_safe_value_de"])
            strong = 1
        else:
            source_class = "GDT746_FORM_ONLY_OPEN"
            after = str(value["passage_safe_value_de"])
            strong = 0
        return {
            "source_class": source_class,
            "semantic_axes": joined(axes),
            "before_render_de": f"[{surface}:?]",
            "after_render_de": after,
            "strong_concrete_credit": strong,
            "weak_visible_credit": 0,
            "candidate_token": 1,
            "retired_literal_withheld": 0,
        }

    patch = patch_map.get(coordinate)
    if patch is not None:
        text = patch["gdt743_working_render_de"]
        axes = semantic_axes(text, patterns)
        if safe_semantic(text) and axes:
            return {
                "source_class": "GDT743_OCCURRENCE_WHOLE",
                "semantic_axes": joined(axes),
                "before_render_de": text,
                "after_render_de": text,
                "strong_concrete_credit": 1,
                "weak_visible_credit": 0,
                "candidate_token": 0,
                "retired_literal_withheld": 0,
            }

    text = cell["v99r7_semantic_value_de"]
    retired = any(word in text.lower() for word in RETIRED_LITERAL_WORDS)
    clean = (
        cell["unknown_v99r7"] == "0"
        and cell["gdt734_composition_semantic_credit"] == "0"
        and cell["component_export_credit"] == "0"
        and safe_semantic(text)
    )
    axes = semantic_axes(text, patterns) if clean else ()
    if clean and axes and cell["gdt734_confidence_level"].startswith(("W2", "W3")):
        return {
            "source_class": "GDT734_W23_SAFE_WHOLE",
            "semantic_axes": joined(axes),
            "before_render_de": text,
            "after_render_de": text,
            "strong_concrete_credit": 1,
            "weak_visible_credit": 0,
            "candidate_token": 0,
            "retired_literal_withheld": 0,
        }
    if clean and axes:
        return {
            "source_class": "GDT734_WEAK_SAFE_WHOLE",
            "semantic_axes": joined(axes),
            "before_render_de": f"[{text}; schwach]",
            "after_render_de": f"[{text}; schwach]",
            "strong_concrete_credit": 0,
            "weak_visible_credit": 1,
            "candidate_token": 0,
            "retired_literal_withheld": 0,
        }
    return {
        "source_class": "WITHHELD_RETIRED_LITERAL" if retired else "OPEN",
        "semantic_axes": "NONE",
        "before_render_de": f"[{surface}:?]",
        "after_render_de": (
            f"[{surface}: zurückgehaltene Altidentität]" if retired else f"[{surface}:?]"
        ),
        "strong_concrete_credit": 0,
        "weak_visible_credit": 0,
        "candidate_token": 0,
        "retired_literal_withheld": int(retired),
    }


def build_token_rows(
    value_cards: list[dict[str, object]],
    candidate_occurrences: list[dict[str, str]],
) -> tuple[
    list[dict[str, object]],
    dict[tuple[str, int], dict[str, object]],
    dict[str, list[dict[str, str]]],
    dict[str, object],
]:
    value_map = {str(row["candidate_surface"]): row for row in value_cards}
    candidate_coordinates = {
        (row["locus"], int(row["token_ordinal"])) for row in candidate_occurrences
    }
    line_loci = sorted({row["locus"] for row in candidate_occurrences})
    by_line, exact, guard = g745.g739.g738.token_context()
    cells = g745.g739.g738.compact_cells()
    _, patterns = g745.g739.load_axis_specs()
    patch_rows = read_tsv(ROOT / G743_PATCH_REL)
    patch_map = {
        (row["locus"], int(row["token_ordinal"])): row for row in patch_rows
    }
    output: list[dict[str, object]] = []
    token_map: dict[tuple[str, int], dict[str, object]] = {}
    for locus in line_loci:
        line = by_line[locus]
        for ordinal, token in enumerate(line, start=1):
            cell = cells[(locus, ordinal)]
            if token["eva"] != cell["surface"]:
                raise AssertionError(f"raw/cache mismatch at {locus}:{ordinal}")
            reader_exact = exact[(locus, int(token["token_index"]))]
            card = token_card(
                locus, ordinal, token, cell, reader_exact, value_map,
                candidate_coordinates, patch_map, patterns,
            )
            row = {
                "gdt747_token_id": f"G747-T{len(output) + 1:04d}",
                "page": cell["page"],
                "locus": locus,
                "line_number": line_number(locus),
                "token_ordinal": ordinal,
                "surface": cell["surface"],
                "reader_exact": reader_exact,
                **card,
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            }
            output.append(row)
            token_map[(locus, ordinal)] = row
    return output, token_map, by_line, guard


def build_local_support(
    candidate_occurrences: list[dict[str, str]],
    token_map: dict[tuple[str, int], dict[str, object]],
    by_line: dict[str, list[dict[str, str]]],
    value_cards: list[dict[str, object]],
) -> list[dict[str, object]]:
    value_map = {str(row["candidate_surface"]): row for row in value_cards}
    output = []
    for source in sorted(candidate_occurrences, key=lambda row: row["cell_id"]):
        locus = source["locus"]
        ordinal = int(source["token_ordinal"])
        candidate = source["surface"]
        core = split_values(str(value_map[candidate]["passage_core_axes"]))
        neighbors = []
        for delta in (-2, -1, 1, 2):
            if not 1 <= ordinal + delta <= len(by_line[locus]):
                continue
            row = token_map[(locus, ordinal + delta)]
            if row["source_class"] not in {
                "GDT734_W23_SAFE_WHOLE", "GDT743_OCCURRENCE_WHOLE"
            }:
                continue
            axes = split_values(str(row["semantic_axes"]))
            shared = core & axes
            if shared:
                neighbors.append((delta, row, axes, shared))
        shared_axes = set().union(*(item[3] for item in neighbors)) if neighbors else set()
        contrast_axes = set().union(*(item[2] - core for item in neighbors)) if neighbors else set()
        distinct = {str(item[1]["surface"]) for item in neighbors}
        if not core:
            tier = "L0_FORM_ONLY_NO_CORE"
        elif len(distinct) >= 2 and (
            {"HOT", "COLD"} <= contrast_axes or {"DRY", "MOIST"} <= contrast_axes
        ):
            tier = "L3_CONTRASTIVE_SERIAL_PARADIGM"
        elif len(distinct) >= 2:
            tier = "L2_MULTIWHOLE_LOCAL_SUPPORT"
        elif len(distinct) == 1:
            tier = "L1_SINGLE_WHOLE_LOCAL_SUPPORT"
        else:
            tier = "L0_NO_LOCAL_W23_SUPPORT"
        output.append({
            "gdt747_occurrence_id": f"G747-O{len(output) + 1:03d}",
            "candidate_surface": candidate,
            "page": source["page"],
            "physical_folio": source["physical_folio"],
            "locus": locus,
            "token_ordinal": ordinal,
            "reader_exact": source["reader_exact"],
            "passage_core_axes": joined(core),
            "local_support_tier": tier,
            "supporting_whole_count": len(distinct),
            "supporting_whole_surfaces": joined(distinct),
            "supporting_signed_offsets": joined(str(item[0]) for item in neighbors),
            "locally_supported_core_axes": joined(shared_axes),
            "locally_supported_core_fraction": (
                f"{len(shared_axes) / len(core):.3f}" if core else "0.000"
            ),
            "neighbor_contrast_axes": joined(contrast_axes),
            "local_support_evidence_de": " || ".join(
                f"{item[0]:+d}:{item[1]['surface']}={item[1]['after_render_de']}"
                for item in neighbors
            ) or "NONE",
            "candidate_passage_value_de": value_map[candidate]["passage_safe_value_de"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def render_line(rows: list[dict[str, object]], field: str) -> str:
    return "; ".join(str(row[field]) for row in rows)


def build_line_census(
    token_rows: list[dict[str, object]],
    local_support: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    support_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in token_rows:
        by_locus[str(row["locus"])].append(row)
    for row in local_support:
        support_by_locus[str(row["locus"])].append(row)
    output = []
    for locus in sorted(by_locus, key=lambda value: (by_locus[value][0]["page"], line_number(value))):
        rows = sorted(by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        supports = support_by_locus[locus]
        candidate_rows = [row for row in rows if int(row["candidate_token"])]
        before_strong = sum(
            int(row["strong_concrete_credit"]) for row in rows
            if not int(row["candidate_token"])
        )
        after_strong = sum(int(row["strong_concrete_credit"]) for row in rows)
        output.append({
            "gdt747_line_id": f"G747-L{len(output) + 1:03d}",
            "page": rows[0]["page"],
            "locus": locus,
            "line_number": line_number(locus),
            "line_tokens": len(rows),
            "candidate_occurrences": len(candidate_rows),
            "candidate_surfaces": joined(str(row["surface"]) for row in candidate_rows),
            "candidate_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in candidate_rows),
            "before_strong_concrete_tokens": before_strong,
            "after_strong_concrete_tokens": after_strong,
            "strong_concrete_delta": after_strong - before_strong,
            "after_weak_visible_tokens": sum(int(row["weak_visible_credit"]) for row in rows),
            "after_open_tokens": sum(row["source_class"] in {"OPEN", "GDT746_FORM_ONLY_OPEN"} for row in rows),
            "retired_literal_withheld_tokens": sum(int(row["retired_literal_withheld"]) for row in rows),
            "after_strong_coverage_fraction": f"{after_strong / len(rows):.3f}",
            "local_support_tier_counts": count_string(str(row["local_support_tier"]) for row in supports),
            "locally_supported_candidate_occurrences": sum(
                row["local_support_tier"].startswith(("L1_", "L2_", "L3_"))
                for row in supports
            ),
            "eva_line": " ".join(str(row["surface"]) for row in rows),
            "before_render_de": render_line(rows, "before_render_de"),
            "after_render_de": render_line(rows, "after_render_de"),
            "literal_plaintext_credit": 0,
            "component_export_credit": 0,
        })
    return output


def build_candidate_census(
    value_cards: list[dict[str, object]],
    local_support: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_candidate: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in local_support:
        by_candidate[str(row["candidate_surface"])].append(row)
    output = []
    for value in value_cards:
        candidate = str(value["candidate_surface"])
        rows = by_candidate[candidate]
        tiers = Counter(str(row["local_support_tier"]) for row in rows)
        supported = sum(
            tier.startswith(("L1_", "L2_", "L3_")) for tier in (
                str(row["local_support_tier"]) for row in rows
            )
        )
        if tiers["L3_CONTRASTIVE_SERIAL_PARADIGM"]:
            passage_status = "P3_CONTRASTIVE_PASSAGE_SUPPORT"
        elif tiers["L2_MULTIWHOLE_LOCAL_SUPPORT"] >= 2:
            passage_status = "P2_RECURRENT_MULTIWHOLE_PASSAGE_SUPPORT"
        elif supported:
            passage_status = "P1_LOCAL_PASSAGE_SUPPORT"
        elif value["passage_credit"] == "FORM_ONLY_NO_PASSAGE_CREDIT":
            passage_status = "P0_FORM_ONLY_HELD_OPEN"
        else:
            passage_status = "P0_NO_LOCAL_PASSAGE_SUPPORT"
        output.append({
            "gdt747_candidate_id": f"G747-C{len(output) + 1:02d}",
            "candidate_surface": candidate,
            "passage_core_axes": value["passage_core_axes"],
            "passage_safe_value_de": value["passage_safe_value_de"],
            "cache_occurrences": len(rows),
            "cache_pages": len({row["page"] for row in rows}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in rows),
            "local_support_tier_counts": count_string(str(row["local_support_tier"]) for row in rows),
            "locally_supported_occurrences": supported,
            "local_support_pages": len({row["page"] for row in rows if row["local_support_tier"].startswith(("L1_", "L2_", "L3_"))}),
            "passage_status": passage_status,
            "best_local_evidence_de": next(
                (
                    str(row["local_support_evidence_de"])
                    for row in rows
                    if row["local_support_tier"] == "L3_CONTRASTIVE_SERIAL_PARADIGM"
                ),
                next(
                    (
                        str(row["local_support_evidence_de"])
                        for row in rows
                        if row["local_support_tier"].startswith(("L1_", "L2_"))
                    ),
                    "NONE",
                ),
            ),
            "details_retained_as_rivals_de": value["details_retained_as_rivals_de"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def render_block_lines(
    page: str,
    start: int,
    end: int,
    by_line: dict[str, list[dict[str, str]]],
    candidate_coordinates: set[tuple[str, int]],
    value_map: dict[str, dict[str, object]],
    patch_map: dict[tuple[str, int], dict[str, str]],
    exact: dict[tuple[str, int], int],
    cells: dict[tuple[str, int], dict[str, str]],
    patterns: dict[str, object],
) -> list[dict[str, object]]:
    selected_loci = sorted(
        (
            locus for locus, line in by_line.items()
            if line and line[0]["page"] == page and start <= line_number(locus) <= end
        ),
        key=line_number,
    )
    output = []
    for locus in selected_loci:
        for ordinal, token in enumerate(by_line[locus], start=1):
            cell = cells[(locus, ordinal)]
            card = token_card(
                locus, ordinal, token, cell,
                exact[(locus, int(token["token_index"]))], value_map,
                candidate_coordinates, patch_map, patterns,
            )
            output.append({
                "page": page,
                "locus": locus,
                "line_number": line_number(locus),
                "token_ordinal": ordinal,
                "surface": cell["surface"],
                **card,
            })
    return output


def build_blocks(
    specs: list[dict[str, str]],
    candidate_occurrences: list[dict[str, str]],
    value_cards: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_line, exact, _ = g745.g739.g738.token_context()
    cells = g745.g739.g738.compact_cells()
    _, patterns = g745.g739.load_axis_specs()
    patch_map = {
        (row["locus"], int(row["token_ordinal"])): row
        for row in read_tsv(ROOT / G743_PATCH_REL)
    }
    candidate_coordinates = {
        (row["locus"], int(row["token_ordinal"])) for row in candidate_occurrences
    }
    value_map = {str(row["candidate_surface"]): row for row in value_cards}
    manual = (
        {row["block_id"]: row for row in read_tsv(ROOT / MANUAL_BLOCK_REL)}
        if (ROOT / MANUAL_BLOCK_REL).is_file() else {}
    )
    output = []
    for spec in specs:
        rows = render_block_lines(
            spec["page"], int(spec["start_line"]), int(spec["end_line"]),
            by_line, candidate_coordinates, value_map, patch_map, exact, cells,
            patterns,
        )
        if not rows:
            raise AssertionError(f"empty passage block {spec['block_id']}")
        loci = sorted({str(row["locus"]) for row in rows}, key=line_number)
        candidates = [row for row in rows if int(row["candidate_token"])]
        manual_row = manual.get(spec["block_id"], {})
        eva_lines = []
        rendered_lines = []
        for locus in loci:
            line_rows = sorted(
                (row for row in rows if row["locus"] == locus),
                key=lambda row: int(row["token_ordinal"]),
            )
            eva_lines.append(f"{locus} " + " ".join(str(row["surface"]) for row in line_rows))
            rendered_lines.append(f"{locus} " + render_line(line_rows, "after_render_de"))
        output.append({
            "block_id": spec["block_id"],
            "page": spec["page"],
            "start_line": spec["start_line"],
            "end_line": spec["end_line"],
            "physical_lines": len(loci),
            "tokens": len(rows),
            "candidate_occurrences": len(candidates),
            "candidate_surfaces": joined(str(row["surface"]) for row in candidates),
            "strong_concrete_tokens_after": sum(int(row["strong_concrete_credit"]) for row in rows),
            "weak_visible_tokens_after": sum(int(row["weak_visible_credit"]) for row in rows),
            "open_tokens_after": sum(row["source_class"] in {"OPEN", "GDT746_FORM_ONLY_OPEN"} for row in rows),
            "retired_literal_withheld_tokens": sum(int(row["retired_literal_withheld"]) for row in rows),
            "selection_reason": spec["selection_reason"],
            "manual_passage_type": manual_row.get("manual_passage_type", "PENDING"),
            "manual_information_gain": manual_row.get("manual_information_gain", "PENDING"),
            "manual_assessment_de": manual_row.get("manual_assessment_de", "PENDING"),
            "eva_block": " || ".join(eva_lines),
            "safe_render_block_de": " || ".join(rendered_lines),
            "literal_plaintext_credit": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    candidates: list[dict[str, object]],
    lines: list[dict[str, object]],
    blocks: list[dict[str, object]],
    local: list[dict[str, object]],
) -> None:
    local_rank = {
        "L3_CONTRASTIVE_SERIAL_PARADIGM": 3,
        "L2_MULTIWHOLE_LOCAL_SUPPORT": 2,
        "L1_SINGLE_WHOLE_LOCAL_SUPPORT": 1,
        "L0_NO_LOCAL_W23_SUPPORT": 0,
        "L0_FORM_ONLY_NO_CORE": 0,
    }
    focus_local = sorted(
        local,
        key=lambda row: (
            -local_rank[str(row["local_support_tier"])],
            -int(row["supporting_whole_count"]),
            str(row["candidate_surface"]), str(row["locus"]),
        ),
    )[:20]
    lines_out = [
        "# GDT747 Passage reader", "",
        "Nur vollständige Ganzwörter werden eingesetzt. Eine eckige Klammer ist",
        "schwach, zurückgehalten oder offen; sie ist keine verdeckte Übersetzung.", "",
        "## Kandidaten", "",
    ]
    for row in candidates:
        lines_out.append(
            f"- `{row['candidate_surface']}` — {row['passage_status']}: "
            f"{row['passage_safe_value_de']} ({row['local_support_tier_counts']})"
        )
    lines_out.extend(["", "## Passage blocks", ""])
    for block in blocks:
        lines_out.extend([
            f"### {block['block_id']} — {block['page']} {block['start_line']}–{block['end_line']}", "",
            f"- Typ: {block['manual_passage_type']}",
            f"- Informationsgewinn: {block['manual_information_gain']}",
            f"- Einschätzung: {block['manual_assessment_de']}",
            f"- Deckung: {block['strong_concrete_tokens_after']} stark, "
            f"{block['weak_visible_tokens_after']} schwach, {block['open_tokens_after']} offen, "
            f"{block['retired_literal_withheld_tokens']} Altidentitäten zurückgehalten", "",
            "```text", str(block["eva_block"]).replace(" || ", "\n"), "```", "",
            str(block["safe_render_block_de"]).replace(" || ", "\n"), "",
        ])
    lines_out.extend(["## Die 20 stärksten lokalen Stellen", ""])
    for row in focus_local:
        lines_out.append(
            f"- `{row['locus']}@{row['token_ordinal']}` `{row['candidate_surface']}` — "
            f"{row['local_support_tier']}: {row['local_support_evidence_de']}"
        )
    lines_out.extend(["", "## Höchste Kandidatenzeilen", ""])
    for row in sorted(
        lines,
        key=lambda item: (
            -int(item["candidate_occurrences"]),
            -int(item["strong_concrete_delta"]),
            -float(item["after_strong_coverage_fraction"]),
            str(item["locus"]),
        ),
    )[:20]:
        lines_out.extend([
            f"### `{row['locus']}`", "",
            f"`{row['eva_line']}`", "",
            str(row["after_render_de"]), "",
        ])
    path.write_text("\n".join(lines_out).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path, local_support: list[dict[str, object]]
) -> dict[str, object]:
    contrastive = [
        row for row in local_support
        if row["local_support_tier"] == "L3_CONTRASTIVE_SERIAL_PARADIGM"
    ]
    selected = next(
        (
            row for row in contrastive
            if row["candidate_surface"] == "qochey" and row["locus"] == "f104v.23"
        ),
        contrastive[0] if contrastive else None,
    )
    if selected is None:
        raise AssertionError("no contrastive serial paradigm for edge packet")
    packet = [{
        "edge_id": "G747E001",
        "batch_id": "GDT747_SERIAL_WHOLE_PASSAGE",
        "page": selected["page"],
        "physical_folio": selected["physical_folio"],
        "diagram_unit_id": "CACHED_TEXT_SERIAL_PARADIGM",
        "pivot_visual_id": f"UNKNOWN_WHOLE_{selected['candidate_surface']}",
        "pivot_locus": f"{selected['locus']}@{selected['token_ordinal']}",
        "target_visual_id": "KNOWN_WHOLE_qokchey_f104v",
        "target_locus": "f104v.23@2",
        "relation_type": "SERIAL_COMPLETE_WHOLE_AXIS_PARADIGM",
        "direction_basis": "WRITTEN_LINE_ORDER_RADIUS2",
        "ownership_basis": "COMPLETE_WHOLE_FORM_DISTRIBUTION_INTERSECTION",
        "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT747",
        "page_crop_sha256": "NONE",
        "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT747_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": selected["local_support_tier"],
        "ambiguity_state": "AXIS_ONLY_LITERAL_IDENTITY_OPEN",
        "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
    }]
    path = output_dir / "GDT747_GDT388_SERIAL_PARADIGM_EDGE_PACKET.tsv"
    write_tsv(path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(path)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("serial paradigm packet unexpectedly score-ready")
    (output_dir / "GDT747_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    g746_census = read_tsv(ROOT / G746_CENSUS_REL)
    all_occurrences = read_tsv(ROOT / G746_OCCURRENCE_REL)
    safe_rows = read_tsv(ROOT / SAFE_VALUES_REL)
    block_specs = read_tsv(ROOT / BLOCK_SPECS_REL)
    value_cards = build_value_cards(g746_census, safe_rows)
    supported = {str(row["candidate_surface"]) for row in value_cards}
    candidate_occurrences = [
        row for row in all_occurrences
        if row["surface"] in supported and "A3_CANDIDATE" in row["surface_roles"]
    ]
    if len(candidate_occurrences) != 64 or len({row["locus"] for row in candidate_occurrences}) != 62:
        raise AssertionError("GDT746 supported passage occurrence boundary changed")
    token_rows, token_map, by_line, guard = build_token_rows(
        value_cards, candidate_occurrences
    )
    local_support = build_local_support(
        candidate_occurrences, token_map, by_line, value_cards
    )
    line_census = build_line_census(token_rows, local_support)
    candidate_census = build_candidate_census(value_cards, local_support)
    blocks = build_blocks(block_specs, candidate_occurrences, value_cards)
    if len(local_support) != 64 or len(line_census) != 62 or len(candidate_census) != 12 or len(blocks) != 6:
        raise AssertionError("GDT747 output cardinality changed")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "SUPPORTED_12_PASSAGE_VALUES.tsv", value_cards, list(value_cards[0]))
    write_tsv(output_dir / "TOKEN_PASSAGE_RENDER.tsv", token_rows, list(token_rows[0]))
    write_tsv(output_dir / "OCCURRENCE_64_LOCAL_SUPPORT.tsv", local_support, list(local_support[0]))
    write_tsv(output_dir / "LINE_62_PASSAGE_CENSUS.tsv", line_census, list(line_census[0]))
    write_tsv(output_dir / "CANDIDATE_12_PASSAGE_CENSUS.tsv", candidate_census, list(candidate_census[0]))
    write_tsv(output_dir / "BLOCK_6_PASSAGE_CENSUS.tsv", blocks, list(blocks[0]))
    write_reader(
        output_dir / "GDT747_SUPPORTED_WHOLE_PASSAGE_READER.md",
        candidate_census, line_census, blocks, local_support,
    )
    intake = edge_packet(output_dir, local_support)

    local_counts = Counter(str(row["local_support_tier"]) for row in local_support)
    candidate_counts = Counter(str(row["passage_status"]) for row in candidate_census)
    strong_delta = sum(int(row["strong_concrete_delta"]) for row in line_census)
    status = (
        "PARTIAL__12_GDT746_SUPPORTED_WHOLES__64_OCCURRENCES__62_LINES__"
        f"{local_counts['L3_CONTRASTIVE_SERIAL_PARADIGM']}_CONTRASTIVE_LOCAL_PARADIGMS__"
        f"{local_counts['L2_MULTIWHOLE_LOCAL_SUPPORT']}_MULTIWHOLE_LOCAL_SUPPORTS__"
        f"{local_counts['L1_SINGLE_WHOLE_LOCAL_SUPPORT']}_SINGLE_WHOLE_LOCAL_SUPPORTS__"
        f"{strong_delta}_STRONG_CONCRETE_TOKEN_DELTA__6_PASSAGE_BLOCKS__"
        "ZERO_LITERAL_IDENTITIES__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
    )
    result = {
        "schema": "GDT747_RESULT_V1",
        "status": status,
        "question": (
            "When only the intersection of GDT746 complete-whole form and "
            "distribution axes is inserted into every cached candidate line, "
            "which local serial paradigms and multi-line passages become "
            "concretely more informative without component or literal-name export?"
        ),
        "scope": {
            "supported_candidate_wholes": len(value_cards),
            "candidate_occurrences": len(candidate_occurrences),
            "candidate_lines": len(line_census),
            "candidate_pages": len({row["page"] for row in candidate_occurrences}),
            "candidate_line_tokens": len(token_rows),
            "passage_blocks": len(blocks),
            "passage_block_tokens": sum(int(row["tokens"]) for row in blocks),
        },
        "local_support_tier_counts": dict(sorted(local_counts.items())),
        "candidate_passage_status_counts": dict(sorted(candidate_counts.items())),
        "line_coverage": {
            "strong_concrete_token_delta": strong_delta,
            "lines_with_positive_delta": sum(int(row["strong_concrete_delta"]) > 0 for row in line_census),
            "lines_with_at_most_one_open_after": sum(int(row["after_open_tokens"]) <= 1 for row in line_census),
            "lines_with_retired_literal_withheld": sum(int(row["retired_literal_withheld_tokens"]) > 0 for row in line_census),
        },
        "candidate_cards": [
            {
                "candidate_surface": row["candidate_surface"],
                "passage_status": row["passage_status"],
                "passage_safe_value_de": row["passage_safe_value_de"],
                "best_local_evidence_de": row["best_local_evidence_de"],
            }
            for row in candidate_census
        ],
        "block_cards": [
            {
                "block_id": row["block_id"],
                "page": row["page"],
                "lines": f"{row['start_line']}-{row['end_line']}",
                "candidate_surfaces": row["candidate_surfaces"],
                "manual_passage_type": row["manual_passage_type"],
                "manual_information_gain": row["manual_information_gain"],
                "manual_assessment_de": row["manual_assessment_de"],
            }
            for row in blocks
        ],
        "guard": guard,
        "edge_intake": intake,
        "claim_ceiling": {
            "confirmed_lexemes": 0,
            "literal_identifications": 0,
            "component_export_credit": 0,
            "unseen_form_predictions": 0,
        },
        "artifacts": {},
    }
    for name in OUTPUT_NAMES:
        result["artifacts"][name] = sha256(output_dir / name)
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
