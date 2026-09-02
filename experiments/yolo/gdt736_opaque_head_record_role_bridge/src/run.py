#!/usr/bin/env python3
"""Build GDT736: opaque-head record roles and a corrected 96-form renderer.

The EVA p/s/r/l characters are provenance labels only. The experiment may
assign distributional record roles to opaque H1-H4 classes, but it never turns
those labels into historical letters, sounds, Latin initials, or lexemes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt736_opaque_head_record_role_bridge")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G635_BASE = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps")
G635_RUN_REL = G635_BASE / "src/run.py"
ALLOW_REL = G635_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
FULL_PROFILE_REL = G635_BASE / "artifacts/INITIAL_HEAD_SCOPE_PROFILE.tsv"
G735_GRID_REL = Path("experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/OPAQUE_96_HEAD_BODY_GRID.tsv")
G623_VISUAL_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/VISUAL_OBSERVATIONS.tsv")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
LINES_REL = Path("transcription/voynich_zl3b_lines.tsv")
STA_REL = Path("transcription/sources/sta/STA-Eva_def.bit")

spec = importlib.util.spec_from_file_location("gdt635_builder", ROOT / G635_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT635 guarded helpers")
g635 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g635)
g634 = g635.g634
g631 = g634.g633.g632.g631

HEAD_ORDER = ("H1", "H2", "H3", "H4")
EVA_TO_HEAD = {"p": "H1", "s": "H2", "r": "H3", "l": "H4"}
PAIR = {"H1": "ENTRY_PAIR", "H2": "ENTRY_PAIR", "H3": "INTERNAL_PAIR", "H4": "INTERNAL_PAIR"}
STATUS = (
    "RECORD_LOCATION_X_BODY_AFFINITY_2X2_SELECTED__PARAGRAPH_SUBENTRY_SPLIT_STRONG__"
    "FREE_FORM_AXIS_SUPPORTING_PROXY_ONLY__96_SCOPED_ROLE_RENDERINGS__"
    "ZERO_HEAD_LEXEMES__NO_NEW_PAGE"
)

OUTPUT_NAMES = (
    "OPAQUE_1166_OCCURRENCE_CONTEXTS.tsv",
    "HEAD_RECORD_ROLE_PROFILE.tsv",
    "BODY_CONTROLLED_POSITION_CONTRAST.tsv",
    "PAIR_POSITION_BY_SECTION.tsv",
    "RECORD_ROLE_2X2_GRID.tsv",
    "GLYPH_CLASS_AND_READER_AUDIT.tsv",
    "BODY_ROLE_DICTIONARY_V2.tsv",
    "OPAQUE_96_CONCRETE_ROLE_GRID.tsv",
    "CORRECTED_ROLE_TRANSLATION_EXAMPLES.tsv",
    "HISTORICAL_RECORD_MODEL_COMPARISON.tsv",
    "HEAD_BODY_AFFINITY_PROFILE.tsv",
    "HEAD_PAIR_BODY_COSINE.tsv",
    "ROLE_AXIS_TESTS.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fmt_rate(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.6f}" if denominator else "0.000000"


def fmt_mean(values: list[float]) -> str:
    return f"{mean(values):.6f}" if values else "0.000000"


def allowed_pages() -> set[str]:
    rows = read_tsv(ROOT / ALLOW_REL)
    pages = {row["page"] for row in rows}
    if len(pages) != 179:
        raise AssertionError(f"expected inherited 179-page allowlist, found {len(pages)}")
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise AssertionError("forbidden page in inherited allowlist")
    return pages


def sta_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in (ROOT / STA_REL).read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] in EVA_TO_HEAD:
            mapping[fields[1]] = fields[0]
    expected = {"p": "P1", "s": "C2", "r": "C1", "l": "B2"}
    if mapping != expected:
        raise AssertionError(f"unexpected STA mapping: {mapping}")
    return mapping


def normalized_position(ordinal: int, line_length: int) -> float:
    return 0.0 if line_length <= 1 else (ordinal - 1) / (line_length - 1)


def load_source_decks() -> tuple[
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]
]:
    heads = read_tsv(SRC / "HEAD_ROLE_SPECS.tsv")
    bodies = read_tsv(SRC / "BODY_ROLE_SPECS.tsv")
    models = read_tsv(SRC / "HISTORICAL_RECORD_MODEL_SPECS.tsv")
    examples = read_tsv(SRC / "CORRECTED_EXAMPLE_SPECS.tsv")
    if len(heads) != 4 or len(bodies) != 24 or len(examples) != 24:
        raise AssertionError("expected 4 head, 24 body, and 24 corrected-example source rows")
    if {row["opaque_head_id"] for row in heads} != set(HEAD_ORDER):
        raise AssertionError("head source deck does not cover H1-H4")
    if any(not row["literal_lexeme_status"].startswith("UNRESOLVED") for row in heads):
        raise AssertionError("head lexemes must remain unresolved")
    if any(int(row["component_export_credit"]) != 0 for row in heads):
        raise AssertionError("head component export credit must remain zero")
    return heads, bodies, models, examples


def build_occurrences(
    token_rows: list[dict[str, str]], line_rows: list[dict[str, str]],
    cross_rows: list[dict[str, str]], grid: list[dict[str, str]],
    heads: list[dict[str, str]], bodies: list[dict[str, str]], sta: dict[str, str],
) -> tuple[list[dict[str, object]], dict[tuple[str, int], int], dict[tuple[str, int], int], dict[str, list[dict[str, object]]]]:
    grid_by_form = {row["form"]: row for row in grid}
    head_by_id = {row["opaque_head_id"]: row for row in heads}
    body_by_id = {row["body"]: row for row in bodies}
    by_line, _ = g631.line_maps(token_rows)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    line_meta = {row["locus"]: row for row in line_rows}
    if not set(by_line).issubset(cross_by_locus) or not set(by_line).issubset(line_meta):
        raise AssertionError("a guarded token-bearing locus lacks line or cross-reader metadata")
    exact, boundary = g634.stable_maps(token_rows, cross_by_locus)

    rows: list[dict[str, object]] = []
    by_body: dict[str, list[dict[str, object]]] = defaultdict(list)
    for source in sorted(token_rows, key=g631.token_sort_key):
        if source["eva"] not in grid_by_form:
            continue
        cell = grid_by_form[source["eva"]]
        head_id = cell["opaque_head_id"]
        head = head_by_id[head_id]
        body = body_by_id[cell["body"]]
        line = by_line[source["locus"]]
        ordinal = next(i for i, token in enumerate(line, 1) if int(token["token_index"]) == int(source["token_index"]))
        line_length = len(line)
        key = (source["locus"], int(source["token_index"]))
        reader_exact = exact[key]
        reader_boundary = boundary[key]
        previous_surface = str(line[ordinal - 2]["eva"]) if ordinal > 1 else "NONE"
        next_surface = str(line[ordinal]["eva"]) if ordinal < line_length else "NONE"
        previous_head = grid_by_form.get(previous_surface, {}).get("opaque_head_id", "NONE")
        next_head = grid_by_form.get(next_surface, {}).get("opaque_head_id", "NONE")
        meta = line_meta[source["locus"]]
        revised = body["revised_concrete_default_de"]
        structural = head["render_template_de"].replace("{body}", revised)
        aggressive = head["aggressive_renderer_template_de"].replace("{body}", revised)
        row: dict[str, object] = {
            "occurrence_id": f"G736-O{len(rows) + 1:04d}", "source_cell_id": cell["bridge_cell_id"],
            "source_experiment": cell["source_experiment"],
            "form": source["eva"], "opaque_head_id": head_id,
            "eva_transcription_label": head["eva_transcription_label"], "sta_code": sta[head["eva_transcription_label"]],
            "sta_family": head["sta_family"], "body": cell["body"], "body_role_de": revised,
            "semantic_family": body["semantic_family"], "page": source["page"], "locus": source["locus"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "token_index": int(source["token_index"]), "token_ordinal": ordinal, "line_length": line_length,
            "line_position": "FIRST" if ordinal == 1 else "LAST" if ordinal == line_length else "MIDDLE",
            "normalized_position": f"{normalized_position(ordinal, line_length):.6f}",
            "paragraph_start_line": int(meta["paragraph_start"]),
            "paragraph_first_token": int(meta["paragraph_start"] == "1" and ordinal == 1),
            "page_line1_first": int(int(meta["line_number"]) == 1 and ordinal == 1), "line_end": int(ordinal == line_length),
            "previous_surface": previous_surface, "previous_target_head": previous_head,
            "next_surface": next_surface, "next_target_head": next_head,
            "all_readers_exact": reader_exact, "split_normalized_all_readers": reader_boundary,
            "reader_status": "EXACT" if reader_exact else "SPLIT_ONLY" if reader_boundary else "OTHER_VARIANT_OR_OMISSION",
            "record_location_axis": head["record_location_axis"], "free_form_proxy_axis": head["free_form_proxy_axis"],
            "body_affinity_axis": head["body_affinity_axis"],
            "selected_formal_role": head["selected_formal_role"], "structural_render_de": structural,
            "aggressive_pharmaceutical_renderer_de": aggressive,
            "physical_attachment": "UNKNOWN__NO_DIPLOMATIC_SHAPE_DESCRIPTOR_IN_ADMITTED_CACHE",
            "literal_head_lexeme": "UNRESOLVED", "eva_initial_credit": 0, "sound_credit": 0,
            "component_export_credit": 0,
        }
        rows.append(row)
        by_body[cell["body"]].append(row)

    expected_counts = Counter({"H1": 135, "H2": 440, "H3": 197, "H4": 394})
    if len(rows) != 1166 or Counter(str(row["opaque_head_id"]) for row in rows) != expected_counts:
        raise AssertionError("target occurrence reconstruction changed")
    if len({str(row["page"]) for row in rows}) != 141 or len({str(row["locus"]) for row in rows}) != 946:
        raise AssertionError("target page/locus footprint changed")
    if sum(int(row["all_readers_exact"]) for row in rows) != 875:
        raise AssertionError("target reader-exact total changed")
    return rows, exact, boundary, by_body


def head_profiles(
    occurrences: list[dict[str, object]], token_rows: list[dict[str, str]],
    line_rows: list[dict[str, str]], exact: dict[tuple[str, int], int],
    boundary: dict[tuple[str, int], int], heads: list[dict[str, str]],
) -> list[dict[str, object]]:
    old_profiles = {EVA_TO_HEAD[row["head"]]: row for row in read_tsv(ROOT / FULL_PROFILE_REL)}
    head_by_id = {row["opaque_head_id"]: row for row in heads}
    line_meta = {row["locus"]: row for row in line_rows}
    by_line, _ = g631.line_maps(token_rows)
    all_initial: dict[str, list[dict[str, object]]] = defaultdict(list)
    for source in sorted(token_rows, key=g631.token_sort_key):
        parsed = g635.split_initial(source["eva"])
        if parsed is None:
            continue
        head_id = EVA_TO_HEAD[parsed[0]]
        line = by_line[source["locus"]]
        ordinal = next(i for i, token in enumerate(line, 1) if int(token["token_index"]) == int(source["token_index"]))
        key = (source["locus"], int(source["token_index"]))
        meta = line_meta[source["locus"]]
        all_initial[head_id].append({
            "line_position": "FIRST" if ordinal == 1 else "LAST" if ordinal == len(line) else "MIDDLE",
            "paragraph_start_line": int(meta["paragraph_start"]),
            "paragraph_first_token": int(meta["paragraph_start"] == "1" and ordinal == 1),
            "page_line1_first": int(int(meta["line_number"]) == 1 and ordinal == 1),
            "exact": exact[key], "boundary": boundary[key],
        })

    rows: list[dict[str, object]] = []
    for head_id in HEAD_ORDER:
        head = head_by_id[head_id]
        target = [row for row in occurrences if row["opaque_head_id"] == head_id]
        full = all_initial[head_id]
        target_pos = Counter(str(row["line_position"]) for row in target)
        full_pos = Counter(str(row["line_position"]) for row in full)
        old = old_profiles[head_id]
        row = {
            "opaque_head_id": head_id, "eva_transcription_label": head["eva_transcription_label"],
            "sta_code": head["sta_code"], "sta_family": head["sta_family"],
            "record_location_axis": head["record_location_axis"], "free_form_proxy_axis": head["free_form_proxy_axis"],
            "body_affinity_axis": head["body_affinity_axis"],
            "selected_formal_role": head["selected_formal_role"], "target_occurrences": len(target),
            "target_reader_exact": sum(int(item["all_readers_exact"]) for item in target),
            "target_reader_exact_rate": fmt_rate(sum(int(item["all_readers_exact"]) for item in target), len(target)),
            "target_split_normalized": sum(int(item["split_normalized_all_readers"]) for item in target),
            "target_split_only": sum(item["reader_status"] == "SPLIT_ONLY" for item in target),
            "target_line_first": target_pos["FIRST"], "target_line_middle": target_pos["MIDDLE"],
            "target_line_last": target_pos["LAST"],
            "target_mean_normalized_position": fmt_mean([float(item["normalized_position"]) for item in target]),
            "target_paragraph_start_line": sum(int(item["paragraph_start_line"]) for item in target),
            "target_paragraph_first_token": sum(int(item["paragraph_first_token"]) for item in target),
            "target_page_line1_first": sum(int(item["page_line1_first"]) for item in target),
            "full_initial_occurrences": len(full), "full_line_first": full_pos["FIRST"],
            "full_line_middle": full_pos["MIDDLE"], "full_line_last": full_pos["LAST"],
            "full_paragraph_start_line": sum(int(item["paragraph_start_line"]) for item in full),
            "full_paragraph_first_token": sum(int(item["paragraph_first_token"]) for item in full),
            "full_page_line1_first": sum(int(item["page_line1_first"]) for item in full),
            "full_standalone_occurrences": int(old["standalone_occurrences"]),
            "standalone_to_initial_proxy_rate": fmt_rate(int(old["standalone_occurrences"]), len(full)),
            "literal_head_lexeme": "UNRESOLVED", "physical_attachment": "UNKNOWN", "component_export_credit": 0,
        }
        rows.append(row)

    expected = {
        "H1": (72, 61, 2, 93, 49, 421, 318), "H2": (222, 159, 59, 36, 3, 90, 11),
        "H3": (4, 146, 47, 53, 0, 85, 0), "H4": (35, 281, 78, 39, 0, 231, 1),
    }
    for row in rows:
        observed = tuple(int(row[field]) for field in (
            "target_line_first", "target_line_middle", "target_line_last", "target_paragraph_start_line",
            "target_paragraph_first_token", "full_paragraph_start_line", "full_paragraph_first_token",
        ))
        if observed != expected[str(row["opaque_head_id"])]:
            raise AssertionError(f"paragraph/position profile changed for {row['opaque_head_id']}: {observed}")
    return rows


def body_contrasts(by_body: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for body in sorted(by_body):
        selected = by_body[body]
        entry = [float(row["normalized_position"]) for row in selected if PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR"]
        internal = [float(row["normalized_position"]) for row in selected if PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR"]
        difference = mean(internal) - mean(entry)
        rows.append({
            "body": body, "entry_pair_occurrences": len(entry), "internal_pair_occurrences": len(internal),
            "entry_pair_mean_normalized_position": fmt_mean(entry),
            "internal_pair_mean_normalized_position": fmt_mean(internal), "internal_minus_entry": f"{difference:.6f}",
            "direction": "ENTRY_EARLIER" if difference > 0 else "TIE" if difference == 0 else "INTERNAL_EARLIER",
            "claim": "BODY_CONTROLLED_RECORD_LOCATION_CONTRAST",
        })
    if len(rows) != 24 or Counter(str(row["direction"]) for row in rows)["ENTRY_EARLIER"] != 21:
        raise AssertionError("body-controlled 21/24 direction result changed")
    return rows


def section_contrasts(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for section in sorted({str(row["section"]) for row in occurrences}):
        selected = [row for row in occurrences if row["section"] == section]
        entry = [float(row["normalized_position"]) for row in selected if PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR"]
        internal = [float(row["normalized_position"]) for row in selected if PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR"]
        difference = mean(internal) - mean(entry)
        rows.append({
            "section": section, "entry_pair_occurrences": len(entry), "internal_pair_occurrences": len(internal),
            "entry_pair_mean_normalized_position": fmt_mean(entry),
            "internal_pair_mean_normalized_position": fmt_mean(internal), "internal_minus_entry": f"{difference:.6f}",
            "direction": "ENTRY_EARLIER" if difference > 0 else "INTERNAL_EARLIER" if difference < 0 else "TIE",
        })
    if any(float(row["internal_minus_entry"]) <= 0 for row in rows):
        raise AssertionError("entry/internal ordering did not persist in every represented section")
    return rows


def odds_ratio(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    if min(a, b, c, d) <= 0:
        raise AssertionError("odds-ratio cell must be positive")
    value = (a * d) / (b * c)
    error = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return value, math.exp(math.log(value) - 1.96 * error), math.exp(math.log(value) + 1.96 * error)


def mantel_haenszel_first_or(
    occurrences: list[dict[str, object]], strata_fields: tuple[str, ...]
) -> float:
    strata: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        strata[tuple(str(row[field]) for field in strata_fields)].append(row)
    numerator = 0.0
    denominator = 0.0
    for selected in strata.values():
        a = sum(PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR" and row["line_position"] == "FIRST" for row in selected)
        b = sum(PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR" and row["line_position"] != "FIRST" for row in selected)
        c = sum(PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR" and row["line_position"] == "FIRST" for row in selected)
        d = sum(PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR" and row["line_position"] != "FIRST" for row in selected)
        total = a + b + c + d
        if total:
            numerator += a * d / total
            denominator += b * c / total
    return numerator / denominator


def role_axis_tests(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    def binary_row(
        test_id: str, description: str, a: int, b: int, c: int, d: int,
        conditioning: str, interpretation: str, claim_limit: str,
    ) -> dict[str, object]:
        value, low, high = odds_ratio(a, b, c, d)
        return {
            "test_id": test_id, "description": description, "a": a, "b": b, "c": c, "d": d,
            "odds_ratio": f"{value:.6f}", "ci95_low": f"{low:.6f}", "ci95_high": f"{high:.6f}",
            "conditioning": conditioning, "interpretation": interpretation, "claim_limit": claim_limit,
        }

    entry = [row for row in occurrences if PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR"]
    internal = [row for row in occurrences if PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR"]
    h1 = [row for row in occurrences if row["opaque_head_id"] == "H1"]
    h2 = [row for row in occurrences if row["opaque_head_id"] == "H2"]
    high_free = [row for row in occurrences if row["free_form_proxy_axis"] == "HIGH_FREE_FORM_PROXY"]
    low_free = [row for row in occurrences if row["free_form_proxy_axis"] == "LOW_FREE_FORM_PROXY"]
    residual_exact = [
        row for row in occurrences
        if row["source_experiment"] == "GDT636_RESIDUAL" and int(row["all_readers_exact"]) == 1
    ]
    residual_entry = [row for row in residual_exact if PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR"]
    residual_internal = [row for row in residual_exact if PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR"]
    rows = [
        binary_row(
            "T01_FIRST_ENTRY_VS_INTERNAL", "Line-first enrichment: H1/H2 versus H3/H4",
            sum(row["line_position"] == "FIRST" for row in entry), sum(row["line_position"] != "FIRST" for row in entry),
            sum(row["line_position"] == "FIRST" for row in internal), sum(row["line_position"] != "FIRST" for row in internal),
            "UNADJUSTED_TARGET_1166", "STRONG_ENTRY_INTERNAL_LOCATION_SPLIT", "FORMAL_POSITION_ONLY",
        ),
        binary_row(
            "T02_FINAL_ENTRY_VS_INTERNAL", "Line-final enrichment: H1/H2 versus H3/H4",
            sum(row["line_position"] == "LAST" for row in entry), sum(row["line_position"] != "LAST" for row in entry),
            sum(row["line_position"] == "LAST" for row in internal), sum(row["line_position"] != "LAST" for row in internal),
            "UNADJUSTED_TARGET_1166", "ENTRY_PAIR_IS_LESS_FINAL", "FORMAL_POSITION_ONLY",
        ),
        binary_row(
            "T03_PARAGRAPH_FIRST_H1_VS_H2", "Paragraph-first enrichment: H1 versus H2",
            sum(int(row["paragraph_first_token"]) for row in h1), sum(not int(row["paragraph_first_token"]) for row in h1),
            sum(int(row["paragraph_first_token"]) for row in h2), sum(not int(row["paragraph_first_token"]) for row in h2),
            "TARGET_GRID", "H1_PARAGRAPH_OPENER_VS_H2_SUBENTRY", "FORMAL_HIERARCHY_ONLY",
        ),
        binary_row(
            "T04_SPLIT_HIGH_FREE_VS_LOW_FREE", "Split-only reader normalization: H2/H3 versus H1/H4",
            sum(row["reader_status"] == "SPLIT_ONLY" for row in high_free), sum(row["reader_status"] != "SPLIT_ONLY" for row in high_free),
            sum(row["reader_status"] == "SPLIT_ONLY" for row in low_free), sum(row["reader_status"] != "SPLIT_ONLY" for row in low_free),
            "ALTERNATE_READINGS_ONE_WITNESS", "SUPPORTS_FREE_FORM_PROXY_PAIRING", "NOT_PHYSICAL_ATTACHMENT_OR_INDEPENDENT_WITNESSES",
        ),
        binary_row(
            "T05_READER_EXACT_ENTRY_VS_INTERNAL", "All-reader exactness: H1/H2 versus H3/H4",
            sum(int(row["all_readers_exact"]) for row in entry), sum(not int(row["all_readers_exact"]) for row in entry),
            sum(int(row["all_readers_exact"]) for row in internal), sum(not int(row["all_readers_exact"]) for row in internal),
            "ALTERNATE_READINGS_ONE_WITNESS", "READER_EXACTNESS_DOES_NOT_DEFINE_SEMANTIC_ROLE", "PALAEOGRAPHIC_CONTROL_ONLY",
        ),
        binary_row(
            "T06_FIRST_EXACT_RESIDUAL", "Line-first enrichment in all-reader-exact GDT636 residual cells",
            sum(row["line_position"] == "FIRST" for row in residual_entry), sum(row["line_position"] != "FIRST" for row in residual_entry),
            sum(row["line_position"] == "FIRST" for row in residual_internal), sum(row["line_position"] != "FIRST" for row in residual_internal),
            "GDT636_RESIDUAL_AND_ALL_READERS_EXACT", "LOCATION_SPLIT_SURVIVES_STRICT_READER_SUBSET", "FORMAL_POSITION_ONLY",
        ),
    ]
    for test_id, fields, interpretation in (
        ("T07_MH_BODY_SECTION", ("body", "section"), "LOCATION_SPLIT_SURVIVES_BODY_AND_SECTION_CONTROL"),
        ("T08_MH_BODY_SECTION_LANGUAGE", ("body", "section", "language"), "LOCATION_SPLIT_SURVIVES_BODY_SECTION_LANGUAGE_CONTROL"),
    ):
        value = mantel_haenszel_first_or(occurrences, fields)
        rows.append({
            "test_id": test_id, "description": "Mantel-Haenszel line-first odds ratio",
            "a": "STRATIFIED", "b": "STRATIFIED", "c": "STRATIFIED", "d": "STRATIFIED",
            "odds_ratio": f"{value:.6f}", "ci95_low": "NOT_COMPUTED", "ci95_high": "NOT_COMPUTED",
            "conditioning": "|".join(fields).upper(), "interpretation": interpretation,
            "claim_limit": "FORMAL_POSITION_ONLY__CACHED_LANGUAGE_IS_METADATA_NOT_LANGUAGE_IDENTIFICATION",
        })
    if not (14.7 < float(rows[0]["odds_ratio"]) < 14.9):
        raise AssertionError("unadjusted entry/internal first-position odds ratio changed")
    return rows


def role_grid(heads: list[dict[str, str]], profiles: list[dict[str, object]]) -> list[dict[str, object]]:
    profile_by_id = {str(row["opaque_head_id"]): row for row in profiles}
    rows: list[dict[str, object]] = []
    for head in heads:
        profile = profile_by_id[head["opaque_head_id"]]
        rows.append({
            "opaque_head_id": head["opaque_head_id"], "eva_transcription_label": head["eva_transcription_label"],
            "sta_code": head["sta_code"], "sta_family": head["sta_family"],
            "record_location_axis": head["record_location_axis"], "free_form_proxy_axis": head["free_form_proxy_axis"],
            "body_affinity_axis": head["body_affinity_axis"],
            "selected_formal_role": head["selected_formal_role"],
            "pharmaceutical_working_role": head["pharmaceutical_working_role"],
            "target_line_first_rate": fmt_rate(int(profile["target_line_first"]), int(profile["target_occurrences"])),
            "target_paragraph_first_rate": fmt_rate(int(profile["target_paragraph_first_token"]), int(profile["target_occurrences"])),
            "full_standalone_to_initial_proxy_rate": profile["standalone_to_initial_proxy_rate"],
            "structural_confidence": head["structural_confidence"], "semantic_confidence": head["semantic_confidence"],
            "primary_evidence": head["primary_evidence"], "counterevidence": head["counterevidence"],
            "live_rivals": head["live_rivals"],
            "physical_attachment": "UNKNOWN__FREE_FORM_AXIS_IS_DISTRIBUTIONAL_PROXY",
            "literal_lexeme_status": head["literal_lexeme_status"], "component_export_credit": 0,
        })
    return sorted(rows, key=lambda row: HEAD_ORDER.index(str(row["opaque_head_id"])))


def reader_audit(profiles: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for profile in profiles:
        target = int(profile["target_occurrences"])
        split = int(profile["target_split_only"])
        rows.append({
            "opaque_head_id": profile["opaque_head_id"], "eva_transcription_label": profile["eva_transcription_label"],
            "sta_code": profile["sta_code"], "sta_family": profile["sta_family"], "target_occurrences": target,
            "all_reader_exact": profile["target_reader_exact"], "all_reader_exact_rate": profile["target_reader_exact_rate"],
            "split_only": split, "split_only_rate": fmt_rate(split, target),
            "other_variant_or_omission": target - int(profile["target_reader_exact"]) - split,
            "physical_graph_description": "UNOBSERVED_IN_ADMITTED_CACHE", "baseline_joining": "UNOBSERVED",
            "superscript_or_overmark": "UNOBSERVED", "historical_shape_match": "NOT_SCORED",
            "reader_evidence_scope": "THREE_ALTERNATE_READINGS_OF_ONE_MANUSCRIPT__NOT_INDEPENDENT_WITNESSES",
            "eva_letter_sound_or_initial_credit": 0, "literal_lexeme_credit": 0,
        })
    return rows


def body_dictionary(bodies: list[dict[str, str]], grid: list[dict[str, str]]) -> list[dict[str, object]]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for cell in grid:
        counts[cell["body"]][0] += int(cell["occurrences"])
        counts[cell["body"]][1] += int(cell["reader_exact_occurrences"])
    rows: list[dict[str, object]] = []
    for body in bodies:
        herbal_override = (
            "Wurzel- oder Untergrundteil; nur die fünf bereits in GDT623 VIS006 geprüften Herbal-p...air-Köpfe"
            if body["body"] == "air" else "NONE"
        )
        rows.append({
            **body, "target_occurrences": counts[body["body"]][0],
            "target_reader_exact_occurrences": counts[body["body"]][1],
            "herbal_visual_override_de": herbal_override, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return rows


def concrete_grid(
    grid: list[dict[str, str]], heads: list[dict[str, str]], bodies: list[dict[str, str]],
) -> list[dict[str, object]]:
    head_by_id = {row["opaque_head_id"]: row for row in heads}
    body_by_id = {row["body"]: row for row in bodies}
    rows: list[dict[str, object]] = []
    for source in grid:
        head = head_by_id[source["opaque_head_id"]]
        body = body_by_id[source["body"]]
        meaning = body["revised_concrete_default_de"]
        rows.append({
            "role_cell_id": f"G736-C{len(rows) + 1:03d}", "source_cell_id": source["bridge_cell_id"],
            "form": source["form"], "opaque_head_id": source["opaque_head_id"],
            "eva_transcription_label": source["eva_transcription_label"], "sta_code": head["sta_code"],
            "body": source["body"], "occurrences": int(source["occurrences"]),
            "reader_exact_occurrences": int(source["reader_exact_occurrences"]),
            "record_location_axis": head["record_location_axis"], "free_form_proxy_axis": head["free_form_proxy_axis"],
            "body_affinity_axis": head["body_affinity_axis"],
            "selected_formal_role": head["selected_formal_role"], "revised_body_role_de": meaning,
            "structural_role_render_de": head["render_template_de"].replace("{body}", meaning),
            "aggressive_pharmaceutical_renderer_de": head["aggressive_renderer_template_de"].replace("{body}", meaning),
            "body_role_confidence": body["role_confidence"], "head_structural_confidence": head["structural_confidence"],
            "head_semantic_confidence": head["semantic_confidence"],
            "live_rivals": f"HEAD={head['live_rivals']} || BODY={body['live_rivals']}",
            "herbal_visual_override_de": (
                "Wurzel-/Untergrundteil only in the inherited five-page GDT623 p...air visual family"
                if source["body"] == "air" and source["opaque_head_id"] == "H1" else "NONE"
            ),
            "literal_head_lexeme": "UNRESOLVED", "literal_body_lexeme_confidence": body["literal_lexeme_confidence"],
            "eva_initial_credit": 0, "sound_credit": 0, "component_export_credit": 0,
            "status": "SCOPED_ROLE_DEFAULT__REPLACEABLE_BY_EXACT_WHOLE_EVIDENCE",
        })
    if len(rows) != 96 or len({str(row["form"]) for row in rows}) != 96:
        raise AssertionError("concrete role grid must contain 96 unique forms")
    return rows


def cosine(left: list[int], right: list[int]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    denominator = (sum(value * value for value in left) * sum(value * value for value in right)) ** 0.5
    return numerator / denominator if denominator else 0.0


def body_affinity(
    grid: list[dict[str, str]], heads: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    body_order = sorted({row["body"] for row in grid})
    head_by_id = {row["opaque_head_id"]: row for row in heads}
    counts = {head_id: {body: 0 for body in body_order} for head_id in HEAD_ORDER}
    exact = {head_id: {body: 0 for body in body_order} for head_id in HEAD_ORDER}
    for row in grid:
        counts[row["opaque_head_id"]][row["body"]] = int(row["occurrences"])
        exact[row["opaque_head_id"]][row["body"]] = int(row["reader_exact_occurrences"])

    selected_pairs = {frozenset(("H1", "H4")), frozenset(("H2", "H3"))}
    pair_rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(HEAD_ORDER, 2):
        occurrence_cosine = cosine([counts[left][body] for body in body_order], [counts[right][body] for body in body_order])
        exact_cosine = cosine([exact[left][body] for body in body_order], [exact[right][body] for body in body_order])
        pair_rows.append({
            "head_a": left, "head_b": right, "body_dimensions": len(body_order),
            "occurrence_cosine": f"{occurrence_cosine:.6f}", "reader_exact_cosine": f"{exact_cosine:.6f}",
            "selected_cross_axis_pair": int(frozenset((left, right)) in selected_pairs),
            "interpretation": (
                "SAME_BODY_AFFINITY_CLUSTER" if frozenset((left, right)) in selected_pairs
                else "CROSS_CLUSTER_COMPARISON"
            ),
            "semantic_limit": "CLUSTER_IS_REAL__FORM_STATE_VS_MATERIA_VALUE_LABELS_ARE_INHERITED_WORKING_ORIENTATION",
        })

    ranked = sorted(pair_rows, key=lambda row: float(row["occurrence_cosine"]), reverse=True)
    if {frozenset((row["head_a"], row["head_b"])) for row in ranked[:2]} != selected_pairs:
        raise AssertionError("expected H1-H4 and H2-H3 to be the two strongest body-frequency pairs")
    paired = {"H1": "H4", "H4": "H1", "H2": "H3", "H3": "H2"}
    profile_rows: list[dict[str, object]] = []
    for head_id in HEAD_ORDER:
        top = sorted(body_order, key=lambda body: (-counts[head_id][body], body))[:5]
        pair_row = next(
            row for row in pair_rows if {str(row["head_a"]), str(row["head_b"])} == {head_id, paired[head_id]}
        )
        profile_rows.append({
            "opaque_head_id": head_id, "paired_head": paired[head_id],
            "body_affinity_axis": head_by_id[head_id]["body_affinity_axis"],
            "target_occurrences": sum(counts[head_id].values()),
            "target_reader_exact": sum(exact[head_id].values()),
            "paired_occurrence_cosine": pair_row["occurrence_cosine"],
            "paired_reader_exact_cosine": pair_row["reader_exact_cosine"],
            "top_five_bodies": "|".join(f"{body}:{counts[head_id][body]}" for body in top),
            "complete_occurrence_vector": "|".join(f"{body}:{counts[head_id][body]}" for body in body_order),
            "complete_reader_exact_vector": "|".join(f"{body}:{exact[head_id][body]}" for body in body_order),
            "cluster_confidence": "HIGH_DISTRIBUTIONAL",
            "semantic_orientation_confidence": "LOW_TO_MEDIUM_WORKING_ROLE",
            "literal_lexeme_credit": 0, "component_export_credit": 0,
        })
    summary = {
        "selected_pairs": ["H1-H4", "H2-H3"],
        "H1_H4_occurrence_cosine": next(row["occurrence_cosine"] for row in pair_rows if {row["head_a"], row["head_b"]} == {"H1", "H4"}),
        "H2_H3_occurrence_cosine": next(row["occurrence_cosine"] for row in pair_rows if {row["head_a"], row["head_b"]} == {"H2", "H3"}),
        "strongest_nonselected_cosine": max(float(row["occurrence_cosine"]) for row in pair_rows if not int(row["selected_cross_axis_pair"])),
    }
    return profile_rows, pair_rows, summary


def corrected_examples(examples: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, row in enumerate(examples, 1):
        rows.append({
            "example_id": f"G736-E{index:02d}", **row, "old_head_noun_status": "REMOVED",
            "literal_translation_status": "NOT_CLAIMED__WORKING_ROLE_RENDER_ONLY", "component_export_credit": 0,
        })
    return rows


def historical_models(models: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in models:
        selected = row["model_id"] == "HRM01"
        rows.append({
            **row, "target_entry_first": 294 if selected else "NOT_MODEL_SPECIFIC",
            "target_internal_first": 39 if selected else "NOT_MODEL_SPECIFIC",
            "body_controlled_entry_earlier": "21_OF_24" if selected else "NOT_MODEL_SPECIFIC",
            "literal_head_lexemes_identified": 0, "eva_letter_or_sound_credit": 0,
            "physical_shape_match_credit": 0, "component_export_credit": 0,
        })
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = allowed_pages()
    heads, bodies, models, examples = load_source_decks()
    sta = sta_map()
    grid = read_tsv(ROOT / G735_GRID_REL)
    if len(grid) != 96 or len({row["body"] for row in grid}) != 24:
        raise AssertionError("GDT735 target grid changed")

    token_rows, token_guard = g631.guarded_query(
        TOKENS_REL, pages, "page,page_order,locus,line_number,section,language,hand,token_index,eva"
    )
    cross_rows, cross_guard = g631.guarded_query(
        CROSS_REL, pages, "page,locus,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    line_rows, line_guard = g631.guarded_query(
        LINES_REL, pages, "page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean"
    )
    occurrences, exact, boundary, by_body = build_occurrences(
        token_rows, line_rows, cross_rows, grid, heads, bodies, sta
    )
    profiles = head_profiles(occurrences, token_rows, line_rows, exact, boundary, heads)
    body_rows = body_dictionary(bodies, grid)
    contrast_rows = body_contrasts(by_body)
    section_rows = section_contrasts(occurrences)
    role_rows = role_grid(heads, profiles)
    reader_rows = reader_audit(profiles)
    concrete_rows = concrete_grid(grid, heads, bodies)
    affinity_rows, cosine_rows, affinity_summary = body_affinity(grid, heads)
    axis_test_rows = role_axis_tests(occurrences)
    example_rows = corrected_examples(examples)
    model_rows = historical_models(models)

    occurrence_fields = [
        "occurrence_id", "source_cell_id", "source_experiment", "form", "opaque_head_id", "eva_transcription_label",
        "sta_code", "sta_family", "body", "body_role_de", "semantic_family", "page", "locus",
        "section", "language", "hand", "token_index", "token_ordinal", "line_length", "line_position",
        "normalized_position", "paragraph_start_line", "paragraph_first_token", "page_line1_first", "line_end",
        "previous_surface", "previous_target_head", "next_surface", "next_target_head", "all_readers_exact",
        "split_normalized_all_readers", "reader_status", "record_location_axis", "free_form_proxy_axis",
        "body_affinity_axis", "selected_formal_role", "structural_render_de", "aggressive_pharmaceutical_renderer_de",
        "physical_attachment", "literal_head_lexeme", "eva_initial_credit", "sound_credit", "component_export_credit",
    ]
    profile_fields = [
        "opaque_head_id", "eva_transcription_label", "sta_code", "sta_family", "record_location_axis",
        "free_form_proxy_axis", "body_affinity_axis", "selected_formal_role", "target_occurrences", "target_reader_exact",
        "target_reader_exact_rate", "target_split_normalized", "target_split_only", "target_line_first",
        "target_line_middle", "target_line_last", "target_mean_normalized_position", "target_paragraph_start_line",
        "target_paragraph_first_token", "target_page_line1_first", "full_initial_occurrences", "full_line_first",
        "full_line_middle", "full_line_last", "full_paragraph_start_line", "full_paragraph_first_token",
        "full_page_line1_first", "full_standalone_occurrences", "standalone_to_initial_proxy_rate",
        "literal_head_lexeme", "physical_attachment", "component_export_credit",
    ]
    write_tsv(output_dir / OUTPUT_NAMES[0], occurrences, occurrence_fields)
    write_tsv(output_dir / OUTPUT_NAMES[1], profiles, profile_fields)
    write_tsv(output_dir / OUTPUT_NAMES[2], contrast_rows, list(contrast_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[3], section_rows, list(section_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[4], role_rows, list(role_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[5], reader_rows, list(reader_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[6], body_rows, list(body_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[7], concrete_rows, list(concrete_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[8], example_rows, list(example_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[9], model_rows, list(model_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[10], affinity_rows, list(affinity_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[11], cosine_rows, list(cosine_rows[0].keys()))
    write_tsv(output_dir / OUTPUT_NAMES[12], axis_test_rows, list(axis_test_rows[0].keys()))

    pair_entry = [row for row in occurrences if PAIR[str(row["opaque_head_id"])] == "ENTRY_PAIR"]
    pair_internal = [row for row in occurrences if PAIR[str(row["opaque_head_id"])] == "INTERNAL_PAIR"]
    result: dict[str, object] = {
        "schema": "GDT736_OPAQUE_HEAD_RECORD_ROLE_BRIDGE_RESULT_V1", "status": STATUS,
        "scope": {
            "inherited_allowlist_pages": len(pages),
            "target_pages_with_occurrences": len({str(row["page"]) for row in occurrences}),
            "target_loci": len({str(row["locus"]) for row in occurrences}), "new_pages_used": 0,
            "f84_used": False, "f84r_used": False,
            "guard_stats": {"tokens": token_guard, "cross": cross_guard, "lines": line_guard},
        },
        "target": {
            "forms": len(concrete_rows), "bodies": len(body_rows), "occurrences": len(occurrences),
            "reader_exact": sum(int(row["all_readers_exact"]) for row in occurrences),
            "head_occurrences": dict(sorted(Counter(str(row["opaque_head_id"]) for row in occurrences).items())),
        },
        "record_hierarchy": {
            "entry_pair_line_first": sum(row["line_position"] == "FIRST" for row in pair_entry),
            "entry_pair_occurrences": len(pair_entry),
            "internal_pair_line_first": sum(row["line_position"] == "FIRST" for row in pair_internal),
            "internal_pair_occurrences": len(pair_internal),
            "entry_pair_mean_position": fmt_mean([float(row["normalized_position"]) for row in pair_entry]),
            "internal_pair_mean_position": fmt_mean([float(row["normalized_position"]) for row in pair_internal]),
            "body_controlled_entry_earlier": sum(row["direction"] == "ENTRY_EARLIER" for row in contrast_rows),
            "body_controlled_bodies": len(contrast_rows),
            "all_represented_sections_same_direction": all(row["direction"] == "ENTRY_EARLIER" for row in section_rows),
            "H1_paragraph_first": int(profiles[0]["target_paragraph_first_token"]),
            "H2_paragraph_first": int(profiles[1]["target_paragraph_first_token"]),
            "unadjusted_first_position_odds_ratio": axis_test_rows[0]["odds_ratio"],
            "body_section_adjusted_first_position_odds_ratio": axis_test_rows[6]["odds_ratio"],
            "body_section_language_adjusted_first_position_odds_ratio": axis_test_rows[7]["odds_ratio"],
        },
        "body_affinity_axis": affinity_summary,
        "claims": {
            "formal_record_location_axis_selected": True, "body_affinity_cross_axis_selected": True,
            "body_affinity_semantic_orientation_is_working_only": True,
            "paragraph_opener_vs_subentry_selected": True,
            "free_form_axis_is_proxy_not_physical_attachment": True,
            "pharmaceutical_roles_are_aggressive_working_renderer_only": True,
            "literal_head_lexemes_identified": 0, "literal_body_lexemes_confirmed": 0,
            "eva_letters_sounds_or_latin_initials_identified": 0, "physical_glyph_shapes_identified": 0,
            "species_identified": 0, "plaintext_translations_claimed": 0, "component_export_credit": 0,
        },
        "artifact_hashes": {
            str(BASE_REL / "artifacts" / name): sha256(output_dir / name) for name in OUTPUT_NAMES
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({"status": result["status"], "target": result["target"], "record_hierarchy": result["record_hierarchy"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
