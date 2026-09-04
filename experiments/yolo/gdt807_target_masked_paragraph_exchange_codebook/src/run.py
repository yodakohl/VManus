#!/usr/bin/env python3
"""Build GDT807's target-line-masked paragraph exchange codebook.

Mixed transcription tables are materialised only through guarded
``vmanus-exp query-tsv`` calls.  Every output is structural and carries zero
semantic and renderer credit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
RUN = SRC / "run.py"
PREREG = BASE / "PREREGISTRATION.md"
METHOD = BASE / "METHOD.md"
MANIFEST = BASE / "experiment.json"

PAIR_SPECS = SRC / "TARGET_PAIR_SPECS.tsv"
VIEW_SPECS = SRC / "MODEL_VIEW_SPECS.tsv"
MARKER_SPECS = SRC / "POSITIONAL_MARKER_SPECS.tsv"
RIVAL_SPECS = SRC / "CONCRETE_RIVAL_DISPLAY_SPECS.tsv"
ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
LINES_RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
G805_ATLAS = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv"
G806_K12 = ROOT / "experiments/yolo/gdt806_three_channel_whole_context_replication/artifacts/GDT806_K12_POOL_MEMBERSHIP.tsv"
G806_CONTACTS = ROOT / "experiments/yolo/gdt806_three_channel_whole_context_replication/artifacts/GDT806_TARGET_AND_K12_CONTACTS.tsv"
G804_CONTROLS = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_NEAREST_CONTROL_POOLS.tsv"
G800_OCCURRENCES = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G757_ROLES = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_11_WHOLE_ROLE_ATLAS.tsv"
G757_OCCURRENCES = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv"
G757_LOW = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/LOW_PURITY_HIGH_TRIAD_COMPARATORS.tsv"
VMANUS_EXP = ROOT / "vmanus-exp"
GUARDED_TOOL = ROOT / "tools/guarded_tsv_query.py"
EDGE_TOOL = ROOT / "tools/relation_edge_intake.py"

TARGETS = ("cheol", "otal", "okal", "ol", "qokeol", "qokol", "qotal")
TARGET_SET = frozenset(TARGETS)
ALPHA = 0.5
CYCLIC_OFFSETS = tuple(range(1, 13))
EXPECTED = {
    "selectors": 179, "source_lines": 4137, "source_tokens": 32339,
    "strict_paragraphs": 665, "strict_lines": 3807,
    "strict_tokens": 31938, "outside_lines": 330, "outside_tokens": 401,
}

OUTPUT_NAMES = (
    "SOURCE_LOCK.tsv",
    "GDT807_IMPLEMENTATION_CLARIFICATIONS.tsv",
    "GDT807_GUARDED_QUERY_STATS.tsv",
    "GDT807_SOURCE_CENSUS.tsv",
    "GDT807_665_STRICT_PARAGRAPH_ATLAS.tsv",
    "GDT807_TARGET_MEMBERSHIP_CAPACITY.tsv",
    "GDT807_PAIR_UNITS.tsv",
    "GDT807_FOLD_VOCABULARY_AUDIT.tsv",
    "GDT807_HELD_FOLIO_PREDICTIONS.tsv",
    "GDT807_PAIR_SCORE_SUMMARY.tsv",
    "GDT807_CYCLIC_EXCHANGE_NULL.tsv",
    "GDT807_CYCLIC_STRATUM_AUDIT.tsv",
    "GDT807_K24_PSEUDO_PAIR_SPECS.tsv",
    "GDT807_K24_PSEUDO_PAIR_SCORES.tsv",
    "GDT807_FOLIO_REMOVAL_DIAGNOSTICS.tsv",
    "GDT807_LANDMARKS.tsv",
    "GDT807_POSITIONAL_MARKER_OVERLAY.tsv",
    "GDT807_CONCRETE_RIVAL_DISPLAY.tsv",
    "GDT807_LCS_TARGET_AUDIT.tsv",
    "GDT807_GDT388_PARAGRAPH_EDGE_PACKET.tsv",
    "GDT807_GDT388_EDGE_INTAKE.json",
    "GDT807_STRUCTURAL_CARD.tsv",
    "RESULT.json",
)

EDGE_FIELDS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str] | None = None) -> None:
    materialized = list(rows)
    if fields is None:
        if not materialized:
            raise RuntimeError(f"empty TSV without explicit schema: {path.name}")
        fields = tuple(materialized[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in materialized:
            writer.writerow({name: row.get(name, "") for name in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def f12(value: float | None) -> str:
    return "NA" if value is None else f"{value:.12g}"


def pipe(values: Iterable[str]) -> str:
    output: list[str] = []
    for value in values:
        if value and value != "NONE" and value not in output:
            output.append(value)
    return "|".join(output) if output else "NONE"


def selector_sort_key(value: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", value)
    if match is None:
        return (10**9, 9, 9, value)
    return (int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), value)


def physical_folio(selector: str) -> str:
    match = re.match(r"^(f\d+[rv])", selector)
    if match is None:
        raise RuntimeError(f"cannot normalize physical folio: {selector}")
    return match.group(1)


def leaf_folio(selector: str) -> str:
    match = re.match(r"^(f\d+)", selector)
    if match is None:
        raise RuntimeError(f"cannot normalize leaf folio: {selector}")
    return match.group(1)


def feature_string(counts: Counter[str]) -> str:
    return "|".join(f"{surface}={counts[surface]}" for surface in sorted(counts)) or "NONE"


def assert_no_sealed(rows: Iterable[Mapping[str, Any]]) -> None:
    for row in rows:
        for name in ("page", "source_selector", "locus", "physical_folio"):
            if str(row.get(name, "")).startswith("f84"):
                raise RuntimeError(f"sealed selector materialized: {name}={row.get(name)}")


def guarded_query(path: Path, pages: Sequence[str], columns: Sequence[str], query_id: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    command = [str(VMANUS_EXP), "query-tsv", rel(path), "--selector", "page"]
    for page in sorted(pages, key=selector_sort_key):
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded query failed: {query_id}")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError(f"guard statistics missing or duplicated: {query_id}")
    stats = json.loads(stats_lines[0][12:])
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    assert_no_sealed(rows)
    return rows, {
        "query_id": query_id, "source_path": rel(path), "selector_column": "page",
        "allowed_value_count": len(pages), "output_columns": ",".join(columns),
        "forbidden_prefixes": "f84|f84r", "selected_rows": int(stats["selected"]),
        "skipped_forbidden_rows": int(stats["skipped_forbidden"]),
        "skipped_not_allowed_rows": int(stats["skipped_not_allowed"]),
        "query_returncode": completed.returncode,
    }


def verify_manifest_inputs() -> list[dict[str, Any]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("experiment_id") != "GDT807":
        raise RuntimeError("wrong experiment manifest")
    if manifest.get("sealed_data") != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise RuntimeError("sealed-data manifest drift")
    raw_paths = {rel(LINES_RAW), rel(CROSS_RAW), rel(TOKENS_RAW)}
    output: list[dict[str, Any]] = []
    for item in manifest["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file():
            raise RuntimeError(f"manifest input missing: {item['path']}")
        if item["path"] in raw_paths:
            actual, mode = item["sha256"], "MANIFEST_HASH__MIXED_TSV_QUERIED_ONLY"
        else:
            actual, mode = sha256(path), "DIRECT_SAFE_INPUT"
            if actual != item["sha256"]:
                raise RuntimeError(f"manifest input hash mismatch: {item['path']}")
        output.append({"path": item["path"], "sha256": actual, "purpose": item["role"], "access_mode": mode, "manifest_hash_match": 1})
    for path, purpose in (
        (RUN, "official GDT807 builder implementation"),
        (VMANUS_EXP, "guarded-query and edge-intake dispatcher"),
        (GUARDED_TOOL, "selector-before-materialization implementation"),
        (EDGE_TOOL, "GDT388 relation-packet intake implementation"),
    ):
        output.append({"path": rel(path), "sha256": sha256(path), "purpose": purpose, "access_mode": "RUNTIME_IMPLEMENTATION", "manifest_hash_match": "NA"})
    return output


@dataclass
class Line:
    page: str
    locus: str
    number: int
    section: str
    language: str
    hand: str
    paragraph_start: bool
    paragraph_end: bool
    tokens: tuple[str, ...]
    token_stable: tuple[int, ...]
    cross: dict[str, str]


@dataclass
class Paragraph:
    paragraph_id: str
    ordinal: int
    page_ordinal: int
    page: str
    physical_folio: str
    section: str
    language: str
    hand: str
    lines: tuple[Line, ...]
    raw_memberships: set[str] = field(default_factory=set)
    stable_memberships: set[str] = field(default_factory=set)
    lcs_memberships: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Representation:
    paragraph_id: str
    line_mask: frozenset[str]
    surviving_loci: tuple[str, ...]
    masked_loci: tuple[str, ...]
    basis_token_count: int
    basis_nonempty_line_count: int
    eligible: bool
    length_bin: int | None
    exact_counts: Counter[str]
    ed1_counts: Counter[str]


@dataclass(frozen=True)
class Unit:
    paragraph: Paragraph
    label: int
    class_surface: str
    counts: Counter[str]
    basis_token_count: int
    basis_nonempty_line_count: int
    length_bin: int


def contiguous_count(tokens: Sequence[str], gram: tuple[str, ...]) -> int:
    width = len(gram)
    return sum(tuple(tokens[index:index + width]) == gram for index in range(len(tokens) - width + 1))


def lcs_length_table(left: Sequence[str], right: Sequence[str]) -> list[list[int]]:
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(len(left) - 1, -1, -1):
        for j in range(len(right) - 1, -1, -1):
            table[i][j] = 1 + table[i + 1][j + 1] if left[i] == right[j] else max(table[i + 1][j], table[i][j + 1])
    return table


def exact_lcs_token_alignment(reference: Sequence[str], alternate: Sequence[str], reference_index: int) -> tuple[str, int | str, int]:
    suffix = lcs_length_table(reference, alternate)
    optimum = suffix[0][0]
    prefix = [[0] * (len(alternate) + 1) for _ in range(len(reference) + 1)]
    for i, left in enumerate(reference):
        for j, right in enumerate(alternate):
            prefix[i + 1][j + 1] = 1 + prefix[i][j] if left == right else max(prefix[i][j + 1], prefix[i + 1][j])
    partners = [j for j, value in enumerate(alternate) if reference[reference_index] == value and prefix[reference_index][j] + 1 + suffix[reference_index + 1][j + 1] == optimum]
    without = list(reference[:reference_index]) + list(reference[reference_index + 1:])
    forced = lcs_length_table(without, alternate)[0][0] < optimum
    if forced and len(partners) == 1:
        return "UNIQUE_FORCED_EXACT", partners[0] + 1, optimum
    if forced:
        return "FORCED_DUPLICATE_EXACT", "NA", optimum
    if partners:
        return "OPTIONAL_OR_DUPLICATE_EXACT", "NA", optimum
    return "NO_EXACT_ALIGNMENT", "NA", optimum


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, start=1):
        current = [i]
        for j, b in enumerate(right, start=1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + int(a != b)))
        previous = current
    return previous[-1]


def load_corpus() -> tuple[
    list[Line], list[Paragraph], dict[str, Paragraph], dict[str, Line],
    list[dict[str, Any]], dict[tuple[str, str, int], int], list[dict[str, str]],
]:
    pages = [row["page"] for row in read_tsv(ALLOWLIST)]
    if len(pages) != EXPECTED["selectors"] or len(set(pages)) != len(pages):
        raise RuntimeError("179-selector allow-list drift")
    if any(page.startswith("f84") for page in pages):
        raise RuntimeError("sealed selector in allow-list")
    line_rows, line_stats = guarded_query(
        LINES_RAW, pages,
        ("page", "locus", "line_number", "section", "language", "hand",
         "paragraph_start", "paragraph_end", "token_count", "eva_clean"),
        "ZL3B_LINES_179",
    )
    token_rows, token_stats = guarded_query(
        TOKENS_RAW, pages,
        ("page", "locus", "token_index", "eva", "section", "language", "hand"),
        "ZL3B_TOKENS_179",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_RAW, pages,
        ("page", "locus", "all_three_present", "all_present_exact",
         "zl3b_clean", "it2a_clean", "rf1b_clean"),
        "CROSS_READER_LINES_179",
    )
    if (len(line_rows), len(token_rows), len(cross_rows)) != (
        EXPECTED["source_lines"], EXPECTED["source_tokens"], EXPECTED["source_lines"],
    ):
        raise RuntimeError("guarded source cardinality drift")
    line_by_key = {(row["page"], row["locus"]): row for row in line_rows}
    cross_by_key = {(row["page"], row["locus"]): row for row in cross_rows}
    if len(line_by_key) != len(line_rows) or len(cross_by_key) != len(cross_rows):
        raise RuntimeError("line/cross key duplication")
    if set(line_by_key) != set(cross_by_key):
        raise RuntimeError("line/cross key-set mismatch")
    token_by_line: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    token_keys: set[tuple[str, str, int]] = set()
    for row in token_rows:
        key = (row["page"], row["locus"], int(row["token_index"]))
        if key in token_keys:
            raise RuntimeError(f"duplicate token key: {key}")
        token_keys.add(key)
        token_by_line[(row["page"], row["locus"])].append(row)
    for rows in token_by_line.values():
        rows.sort(key=lambda row: int(row["token_index"]))
        if [int(row["token_index"]) for row in rows] != list(range(1, len(rows) + 1)):
            raise RuntimeError(f"noncontiguous token ordinals at {rows[0]['locus']}")

    lines: list[Line] = []
    token_stability: dict[tuple[str, str, int], int] = {}
    ordered_rows = sorted(
        line_rows, key=lambda row: (selector_sort_key(row["page"]), int(row["line_number"])),
    )
    for row in ordered_rows:
        key = (row["page"], row["locus"])
        tokens = tuple(token["eva"] for token in token_by_line.get(key, []))
        cross = cross_by_key[key]
        if " ".join(tokens) != row["eva_clean"] or row["eva_clean"] != cross["zl3b_clean"]:
            raise RuntimeError(f"line/token/cross parity mismatch at {row['locus']}")
        if len(tokens) != int(row["token_count"]):
            raise RuntimeError(f"line token-count mismatch at {row['locus']}")
        for token in token_by_line.get(key, []):
            if (token["section"], token["language"], token["hand"]) != (
                row["section"], row["language"], row["hand"],
            ):
                raise RuntimeError(f"token metadata mismatch at {row['locus']}")
        reader_tokens = [cross[name].split() for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        ranks: Counter[str] = Counter()
        stable: list[int] = []
        for index, surface in enumerate(tokens, start=1):
            ranks[surface] += 1
            value = int(ranks[surface] <= min(reader.count(surface) for reader in reader_tokens))
            stable.append(value)
            token_stability[(row["page"], row["locus"], index)] = value
        lines.append(Line(
            page=row["page"], locus=row["locus"], number=int(row["line_number"]),
            section=row["section"], language=row["language"], hand=row["hand"],
            paragraph_start=row["paragraph_start"] == "1",
            paragraph_end=row["paragraph_end"] == "1", tokens=tokens,
            token_stable=tuple(stable), cross=cross,
        ))

    paragraphs: list[Paragraph] = []
    outside: list[Line] = []
    by_page: defaultdict[str, list[Line]] = defaultdict(list)
    for line in lines:
        by_page[line.page].append(line)
    global_ordinal = 0
    for page in sorted(by_page, key=selector_sort_key):
        current: list[Line] | None = None
        page_ordinal = 0
        for line in sorted(by_page[page], key=lambda item: item.number):
            if line.paragraph_start:
                if current is not None:
                    raise RuntimeError(f"nested paragraph start before close: {line.locus}")
                current = []
            if current is None:
                outside.append(line)
                if line.paragraph_end:
                    raise RuntimeError(f"paragraph end without open start: {line.locus}")
                continue
            current.append(line)
            if line.paragraph_end:
                global_ordinal += 1
                page_ordinal += 1
                metadata = {(value.section, value.language, value.hand) for value in current}
                if len(metadata) != 1:
                    raise RuntimeError(f"paragraph metadata not homogeneous: {page}:{page_ordinal}")
                section, language, hand = next(iter(metadata))
                paragraphs.append(Paragraph(
                    paragraph_id=f"G807-P{global_ordinal:04d}", ordinal=global_ordinal,
                    page_ordinal=page_ordinal, page=page,
                    physical_folio=physical_folio(page), section=section,
                    language=language, hand=hand, lines=tuple(current),
                ))
                current = None
        if current is not None:
            raise RuntimeError(f"unclosed paragraph at page boundary: {page}")

    actual = {
        "strict_paragraphs": len(paragraphs),
        "strict_lines": sum(len(paragraph.lines) for paragraph in paragraphs),
        "strict_tokens": sum(len(line.tokens) for paragraph in paragraphs for line in paragraph.lines),
        "outside_lines": len(outside),
        "outside_tokens": sum(len(line.tokens) for line in outside),
    }
    for name, value in actual.items():
        if value != EXPECTED[name]:
            raise RuntimeError(f"strict corpus drift: {name}={value}, expected {EXPECTED[name]}")
    paragraph_by_locus: dict[str, Paragraph] = {}
    for paragraph in paragraphs:
        for line in paragraph.lines:
            if line.locus in paragraph_by_locus:
                raise RuntimeError(f"line assigned twice: {line.locus}")
            paragraph_by_locus[line.locus] = paragraph
    line_by_locus = {line.locus: line for line in lines}
    if len(line_by_locus) != len(lines):
        raise RuntimeError("locus duplicated across selector scope")
    return lines, paragraphs, paragraph_by_locus, line_by_locus, [line_stats, token_stats, cross_stats], token_stability, token_rows


def attach_target_memberships(
    paragraphs: Sequence[Paragraph], paragraph_by_locus: Mapping[str, Paragraph],
    line_by_locus: Mapping[str, Line], token_stability: Mapping[tuple[str, str, int], int],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, str]]], set[str]]:
    atlas = read_tsv(G805_ATLAS)
    if len(atlas) != 1086:
        raise RuntimeError("GDT805 external atlas capacity drift")
    all_g805_targets = {
        row["target_surface"] for row in read_tsv(G804_CONTROLS)
        if row["pool_variant"] == "PRIMARY_K12"
    }
    if len(all_g805_targets) != 11 or not TARGET_SET <= all_g805_targets or {row["surface"] for row in atlas} - all_g805_targets:
        raise RuntimeError("GDT805 target cohort drift")
    events_by_target: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    audit: list[dict[str, Any]] = []
    seen_events: set[str] = set()
    for row in atlas:
        if row["occurrence_id"] in seen_events:
            raise RuntimeError(f"duplicate GDT805 occurrence: {row['occurrence_id']}")
        seen_events.add(row["occurrence_id"])
        line = line_by_locus.get(row["locus"])
        if line is None or line.page != row["source_selector"]:
            raise RuntimeError(f"GDT805 event line join failure: {row['occurrence_id']}")
        index = int(row["token_index"])
        if index < 1 or index > len(line.tokens) or line.tokens[index - 1] != row["surface"]:
            raise RuntimeError(f"GDT805 token replay failure: {row['occurrence_id']}")
        computed_stable = token_stability[(line.page, line.locus, index)]
        if computed_stable != int(row["target_token_stable_all_three"]):
            raise RuntimeError(f"GDT805 rank-stability replay failure: {row['occurrence_id']}")
        paragraph = paragraph_by_locus.get(row["locus"])
        if row["surface"] in TARGET_SET:
            events_by_target[row["surface"]].append(row)
            if paragraph is not None:
                paragraph.raw_memberships.add(row["surface"])
                if computed_stable:
                    paragraph.stable_memberships.add(row["surface"])
        if row["surface"] not in TARGET_SET:
            continue
        reference = list(line.tokens)
        it2a_status, it2a_ordinal, it2a_length = exact_lcs_token_alignment(reference, line.cross["it2a_clean"].split(), index - 1)
        rf1b_status, rf1b_ordinal, rf1b_length = exact_lcs_token_alignment(reference, line.cross["rf1b_clean"].split(), index - 1)
        lcs_stable = it2a_status == rf1b_status == "UNIQUE_FORCED_EXACT"
        if paragraph is not None and lcs_stable:
            paragraph.lcs_memberships.add(row["surface"])
        audit.append({
            "occurrence_id": row["occurrence_id"], "surface": row["surface"],
            "page": line.page, "physical_folio": physical_folio(line.page),
            "locus": line.locus, "token_index": index,
            "strict_paragraph_id": paragraph.paragraph_id if paragraph else "OUTSIDE_PARAGRAPH",
            "in_strict_paragraph": int(paragraph is not None),
            "legacy_rank_stable_all_three": computed_stable,
            "it2a_alignment_status": it2a_status, "it2a_aligned_token_ordinal": it2a_ordinal,
            "it2a_lcs_length": it2a_length,
            "rf1b_alignment_status": rf1b_status, "rf1b_aligned_token_ordinal": rf1b_ordinal,
            "rf1b_lcs_length": rf1b_length,
            "all_three_unique_forced_exact_alignment": int(lcs_stable),
            "audit_only_membership": 1, "primary_membership_replacement": 0,
            "semantic_credit": 0,
        })
    return audit, events_by_target, all_g805_targets


def paired_partner_quarantine(all_targets: set[str]) -> tuple[set[str], dict[str, str]]:
    rows = read_tsv(G800_OCCURRENCES)
    if len(rows) != 4137:
        raise RuntimeError("GDT800 paired-terminal event capacity drift")
    by_stem: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row["surface"] != row["stem"] + row["terminal"] or row["terminal"] not in {"l", "m"}:
            raise RuntimeError(f"GDT800 paired-terminal row malformed: {row['occurrence_id']}")
        by_stem[row["stem"]].add(row["terminal"])
    partners: dict[str, str] = {}
    for target in all_targets:
        if not target.endswith("l") or by_stem.get(target[:-1]) != {"l", "m"}:
            raise RuntimeError(f"GDT800 paired partner unavailable: {target}")
        partners[target] = target[:-1] + "m"
    if len(set(partners.values())) != 11:
        raise RuntimeError("GDT800 target-partner quarantine collision")
    return set(all_targets) | set(partners.values()), partners


def build_representation(
    paragraph: Paragraph, line_mask: frozenset[str], exact_quarantine: frozenset[str],
    ed1_quarantine: frozenset[str],
) -> Representation:
    masked: list[str] = []
    surviving: list[Line] = []
    for line in paragraph.lines:
        if set(line.tokens) & line_mask:
            masked.append(line.locus)
        else:
            surviving.append(line)
    basis_tokens = [surface for line in surviving for surface in line.tokens]
    nonempty = sum(bool(line.tokens) for line in surviving)
    eligible = len(basis_tokens) >= 12 and nonempty >= 2
    length_bin = int(math.floor(math.log2(len(basis_tokens)))) if basis_tokens else None
    exact = Counter(surface for surface in basis_tokens if surface not in exact_quarantine)
    ed1 = Counter(surface for surface in basis_tokens if surface not in exact_quarantine and surface not in ed1_quarantine)
    if set(exact) & exact_quarantine or set(ed1) & (exact_quarantine | ed1_quarantine):
        raise RuntimeError("feature quarantine failure")
    return Representation(
        paragraph_id=paragraph.paragraph_id, line_mask=line_mask,
        surviving_loci=tuple(line.locus for line in surviving), masked_loci=tuple(masked),
        basis_token_count=len(basis_tokens), basis_nonempty_line_count=nonempty,
        eligible=eligible, length_bin=length_bin, exact_counts=exact, ed1_counts=ed1,
    )


def view_memberships(paragraph: Paragraph, view_id: str) -> set[str]:
    return paragraph.stable_memberships if view_id.startswith("STABLE") else paragraph.raw_memberships


def view_counts(rep: Representation, view_id: str) -> Counter[str]:
    return rep.ed1_counts if "ED1" in view_id else rep.exact_counts


def make_units(
    paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
    view_id: str, positive: str, negative: str,
    membership_override: Mapping[str, set[str]] | None = None,
) -> tuple[list[Unit], int]:
    units: list[Unit] = []
    both_excluded = 0
    for paragraph in paragraphs:
        rep = representations[paragraph.paragraph_id]
        if not rep.eligible:
            continue
        memberships = membership_override[paragraph.paragraph_id] if membership_override is not None else view_memberships(paragraph, view_id)
        pos, neg = positive in memberships, negative in memberships
        if pos and neg:
            both_excluded += 1
            continue
        if not (pos or neg):
            continue
        if rep.length_bin is None:
            raise RuntimeError("eligible representation has no length bin")
        units.append(Unit(
            paragraph=paragraph, label=int(pos), class_surface=positive if pos else negative,
            counts=view_counts(rep, view_id), basis_token_count=rep.basis_token_count,
            basis_nonempty_line_count=rep.basis_nonempty_line_count,
            length_bin=rep.length_bin,
        ))
    return units, both_excluded


def auc_ties_half(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positive = [score for label, score in zip(labels, scores) if label == 1]
    negative = [score for label, score in zip(labels, scores) if label == 0]
    if not positive or not negative:
        return None
    credit = 0.0
    for pos in positive:
        for neg in negative:
            credit += 1.0 if pos > neg else 0.5 if pos == neg else 0.0
    return credit / (len(positive) * len(negative))


def balanced_accuracy_zero_ties_half(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positive = [score for label, score in zip(labels, scores) if label == 1]
    negative = [score for label, score in zip(labels, scores) if label == 0]
    if not positive or not negative:
        return None
    pos_credit = sum(1.0 if score > 0 else 0.5 if score == 0 else 0.0 for score in positive) / len(positive)
    neg_credit = sum(1.0 if score < 0 else 0.5 if score == 0 else 0.0 for score in negative) / len(negative)
    return (pos_credit + neg_credit) / 2


def training_vocabulary(units: Sequence[Unit]) -> tuple[set[str], Counter[str], Counter[str], Counter[str]]:
    token_counts: Counter[str] = Counter()
    paragraph_counts: Counter[str] = Counter()
    positive: Counter[str] = Counter()
    negative: Counter[str] = Counter()
    for unit in units:
        token_counts.update(unit.counts)
        paragraph_counts.update(unit.counts.keys())
        (positive if unit.label else negative).update(unit.counts)
    vocabulary = {
        surface for surface, count in token_counts.items()
        if count >= 2 and paragraph_counts[surface] >= 2
    }
    return vocabulary, positive, negative, paragraph_counts


def fold_weights(units: Sequence[Unit]) -> tuple[set[str], dict[str, float], int, int]:
    vocabulary, positive, negative, _paragraph_counts = training_vocabulary(units)
    if not vocabulary:
        return vocabulary, {}, 0, 0
    pos_total = sum(positive[surface] for surface in vocabulary)
    neg_total = sum(negative[surface] for surface in vocabulary)
    pos_denominator = pos_total + ALPHA * len(vocabulary)
    neg_denominator = neg_total + ALPHA * len(vocabulary)
    weights = {
        surface: math.log((positive[surface] + ALPHA) / pos_denominator)
        - math.log((negative[surface] + ALPHA) / neg_denominator)
        for surface in vocabulary
    }
    return vocabulary, weights, pos_total, neg_total


def score_units(
    units: Sequence[Unit], pair_id: str, view_id: str,
    include_predictions: bool = True, context: str = "TARGET",
) -> dict[str, Any]:
    ordered = sorted(units, key=lambda unit: (unit.paragraph.physical_folio, unit.paragraph.paragraph_id))
    folios = sorted({unit.paragraph.physical_folio for unit in ordered})
    predictions: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    scores_by_paragraph: dict[str, float] = {}
    invalid_folds = 0
    for held in folios:
        train = [unit for unit in ordered if unit.paragraph.physical_folio != held]
        test = [unit for unit in ordered if unit.paragraph.physical_folio == held]
        train_pos = sum(unit.label == 1 for unit in train)
        train_neg = sum(unit.label == 0 for unit in train)
        fold_valid = bool(train_pos and train_neg)
        vocabulary: set[str] = set()
        weights: dict[str, float] = {}
        pos_tokens = neg_tokens = 0
        if fold_valid:
            vocabulary, weights, pos_tokens, neg_tokens = fold_weights(train)
        else:
            invalid_folds += 1
        fold_rows.append({
            "fold_id": f"{context}:{pair_id}:{view_id}:{held}", "context": context,
            "pair_id": pair_id, "view_id": view_id, "held_physical_folio": held,
            "train_paragraphs": len(train), "train_positive_paragraphs": train_pos,
            "train_negative_paragraphs": train_neg, "test_paragraphs": len(test),
            "test_positive_paragraphs": sum(unit.label == 1 for unit in test),
            "test_negative_paragraphs": sum(unit.label == 0 for unit in test),
            "training_vocabulary_types": len(vocabulary),
            "training_positive_vocabulary_tokens": pos_tokens,
            "training_negative_vocabulary_tokens": neg_tokens,
            "both_training_classes_present": int(fold_valid),
            "empty_vocabulary_neutral_tie_policy": int(fold_valid and not vocabulary),
            "fold_scoreable": int(fold_valid),
            "fold_status": "SCOREABLE" if fold_valid else "UNSCOREABLE_MISSING_TRAINING_CLASS",
        })
        for unit in test:
            score: float | None = None
            in_vocab = 0
            if fold_valid:
                in_vocab = sum(count for surface, count in unit.counts.items() if surface in vocabulary)
                score = (
                    math.fsum(
                        weights[surface]
                        for surface, count in unit.counts.items() if surface in vocabulary
                        for _ in range(count)
                    ) / in_vocab
                    if in_vocab else 0.0
                )
                scores_by_paragraph[unit.paragraph.paragraph_id] = score
            if include_predictions:
                predictions.append({
                    "prediction_id": f"{context}:{pair_id}:{view_id}:{unit.paragraph.paragraph_id}",
                    "context": context, "pair_id": pair_id, "view_id": view_id,
                    "paragraph_id": unit.paragraph.paragraph_id, "page": unit.paragraph.page,
                    "held_physical_folio": held, "true_label": unit.label,
                    "true_surface": unit.class_surface, "score": f12(score),
                    "decision": "NA" if score is None else "POSITIVE" if score > 0 else "NEGATIVE" if score < 0 else "TIE",
                    "correct_credit": "NA" if score is None else f12(1.0 if (score > 0 and unit.label == 1) or (score < 0 and unit.label == 0) else 0.5 if score == 0 else 0.0),
                    "train_paragraphs": len(train), "train_positive_paragraphs": train_pos,
                    "train_negative_paragraphs": train_neg,
                    "training_vocabulary_types": len(vocabulary),
                    "test_post_quarantine_tokens": sum(unit.counts.values()),
                    "test_tokens_in_fold_vocabulary": in_vocab,
                    "all_oov_neutral_tie": int(fold_valid and in_vocab == 0),
                    "fold_scoreable": int(fold_valid),
                })
    complete = len(scores_by_paragraph) == len(ordered) and bool(ordered)
    labels = [unit.label for unit in ordered if unit.paragraph.paragraph_id in scores_by_paragraph]
    scores = [scores_by_paragraph[unit.paragraph.paragraph_id] for unit in ordered if unit.paragraph.paragraph_id in scores_by_paragraph]
    both_classes = {0, 1} <= set(labels)
    scoreable = complete and both_classes and invalid_folds == 0
    auc = auc_ties_half(labels, scores) if scoreable else None
    balanced = balanced_accuracy_zero_ties_half(labels, scores) if scoreable else None
    return {
        "predictions": predictions, "folds": fold_rows, "scoreable": scoreable,
        "scores_by_paragraph": scores_by_paragraph, "auc": auc,
        "balanced_accuracy": balanced, "invalid_folds": invalid_folds,
        "paragraphs": len(ordered), "positive_paragraphs": sum(unit.label for unit in ordered),
        "negative_paragraphs": sum(1 - unit.label for unit in ordered),
        "positive_folios": len({unit.paragraph.physical_folio for unit in ordered if unit.label}),
        "negative_folios": len({unit.paragraph.physical_folio for unit in ordered if not unit.label}),
        "scoreable_predictions": len(scores),
        "zero_scores": sum(score == 0 for score in scores),
    }


def direct_pair_models(
    paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
    pair_specs: Sequence[dict[str, str]], view_specs: Sequence[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[tuple[str, str], list[Unit]], dict[tuple[str, str], dict[str, Any]]]:
    unit_rows: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    unit_lookup: dict[tuple[str, str], list[Unit]] = {}
    score_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for pair in pair_specs:
        pair_id, positive, negative = pair["pair_id"], pair["positive_surface"], pair["negative_surface"]
        for view in view_specs:
            view_id = view["view_id"]
            units, both = make_units(paragraphs, representations, view_id, positive, negative)
            unit_lookup[(pair_id, view_id)] = units
            for unit in units:
                unit_rows.append({
                    "unit_id": f"{pair_id}:{view_id}:{unit.paragraph.paragraph_id}",
                    "pair_id": pair_id, "view_id": view_id,
                    "positive_surface": positive, "negative_surface": negative,
                    "paragraph_id": unit.paragraph.paragraph_id, "page": unit.paragraph.page,
                    "physical_folio": unit.paragraph.physical_folio,
                    "section": unit.paragraph.section, "language": unit.paragraph.language,
                    "hand": unit.paragraph.hand, "true_label": unit.label,
                    "class_surface": unit.class_surface,
                    "basis_retained_token_count": unit.basis_token_count,
                    "basis_nonempty_retained_lines": unit.basis_nonempty_line_count,
                    "post_mask_length_bin": unit.length_bin,
                    "model_feature_tokens": sum(unit.counts.values()),
                    "model_feature_types": len(unit.counts),
                    "model_feature_counts": feature_string(unit.counts),
                    "exclusive_pair_membership": 1, "paragraph_vote_weight": 1,
                    "semantic_credit": 0,
                })
            result = score_units(units, pair_id, view_id)
            score_lookup[(pair_id, view_id)] = result
            predictions.extend(result["predictions"])
            fold_rows.extend(result["folds"])
            summaries.append({
                "pair_id": pair_id, "view_id": view_id,
                "positive_surface": positive, "negative_surface": negative,
                "positive_paragraphs": result["positive_paragraphs"],
                "negative_paragraphs": result["negative_paragraphs"],
                "positive_folios": result["positive_folios"],
                "negative_folios": result["negative_folios"],
                "both_member_paragraphs_excluded": both,
                "exclusive_eligible_paragraphs": result["paragraphs"],
                "scoreable_predictions": result["scoreable_predictions"],
                "invalid_training_folds": result["invalid_folds"],
                "zero_score_ties": result["zero_scores"],
                "auc_ties_half": f12(result["auc"]),
                "balanced_accuracy_zero_ties_half": f12(result["balanced_accuracy"]),
                "model_scoreable": int(result["scoreable"]),
                "model_status": "SCOREABLE" if result["scoreable"] else "UNSCOREABLE_FAIL_CLOSED",
            })
    return unit_rows, fold_rows, predictions, summaries, unit_lookup, score_lookup


def cyclic_nulls(
    paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
    pair_specs: Sequence[dict[str, str]], view_specs: Sequence[dict[str, str]],
    target_scores: Mapping[tuple[str, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    null_rows: list[dict[str, Any]] = []
    stratum_rows: list[dict[str, Any]] = []
    eligible = [paragraph for paragraph in paragraphs if representations[paragraph.paragraph_id].eligible]
    for view in view_specs:
        view_id = view["view_id"]
        strata: defaultdict[tuple[str, str, str, int], list[Paragraph]] = defaultdict(list)
        for paragraph in eligible:
            rep = representations[paragraph.paragraph_id]
            if rep.length_bin is None:
                raise RuntimeError("eligible paragraph missing length bin")
            strata[(paragraph.section, paragraph.language, paragraph.hand, rep.length_bin)].append(paragraph)
        for members in strata.values():
            members.sort(key=lambda p: (p.page, p.lines[0].number, p.paragraph_id))
        for offset in CYCLIC_OFFSETS:
            rotated: dict[str, set[str]] = {}
            total_moved = 0
            total_identity = 0
            for stratum_index, (key, members) in enumerate(sorted(strata.items()), start=1):
                n = len(members)
                step = offset % n
                before = [set(view_memberships(paragraph, view_id)) for paragraph in members]
                after = [before[(index - step) % n] for index in range(n)]
                moved = sum(left != right for left, right in zip(before, after))
                total_moved += moved
                total_identity += n - moved
                for paragraph, membership in zip(members, after):
                    rotated[paragraph.paragraph_id] = set(membership)
                stratum_rows.append({
                    "stratum_id": f"{view_id}:O{offset:02d}:S{stratum_index:03d}",
                    "view_id": view_id, "offset": offset,
                    "section": key[0], "language": key[1], "hand": key[2],
                    "post_mask_length_bin": key[3], "eligible_paragraphs": n,
                    "rotation_step_mod_n": step,
                    "moved_membership_sets": moved,
                    "identity_membership_sets": n - moved,
                    "empty_membership_sets_before": sum(not value for value in before),
                    "empty_membership_sets_after": sum(not value for value in after),
                    "target_memberships_before": sum(len(value) for value in before),
                    "target_memberships_after": sum(len(value) for value in after),
                    "deterministic_sort": "page_lexicographic|paragraph_start_line_numeric|paragraph_id",
                    "rotation_rule": "dest_i<-source_(i-k_mod_n)",
                })
            if set(rotated) != {paragraph.paragraph_id for paragraph in eligible}:
                raise RuntimeError("cyclic rotation did not cover every eligible paragraph")
            for pair in pair_specs:
                pair_id, positive, negative = pair["pair_id"], pair["positive_surface"], pair["negative_surface"]
                units, both = make_units(paragraphs, representations, view_id, positive, negative, rotated)
                result = score_units(units, pair_id, view_id, include_predictions=False, context=f"CYCLIC_OFFSET_{offset:02d}")
                target_auc = target_scores[(pair_id, view_id)]["auc"]
                null_rows.append({
                    "pair_id": pair_id, "view_id": view_id, "offset": offset,
                    "eligible_rotation_universe": len(eligible),
                    "moved_membership_sets": total_moved,
                    "identity_membership_sets": total_identity,
                    "moved_fraction": f12(total_moved / len(eligible)),
                    "positive_paragraphs": result["positive_paragraphs"],
                    "negative_paragraphs": result["negative_paragraphs"],
                    "positive_folios": result["positive_folios"],
                    "negative_folios": result["negative_folios"],
                    "both_member_paragraphs_excluded": both,
                    "scoreable_predictions": result["scoreable_predictions"],
                    "invalid_training_folds": result["invalid_folds"],
                    "auc_ties_half": f12(result["auc"]),
                    "balanced_accuracy_zero_ties_half": f12(result["balanced_accuracy"]),
                    "model_scoreable": int(result["scoreable"]),
                    "target_auc": f12(target_auc),
                    "null_auc_ge_target_ties_against": int(result["scoreable"] and target_auc is not None and result["auc"] >= target_auc),
                })
    return null_rows, stratum_rows


def build_k24_specs() -> list[dict[str, Any]]:
    rows = [row for row in read_tsv(G804_CONTROLS) if row["pool_variant"] == "PRIMARY_K12"]
    grouped: defaultdict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        rank = int(row["neighbor_rank"])
        if rank in grouped[row["target_surface"]]:
            raise RuntimeError(f"duplicate GDT804 K12 rank: {row['target_surface']}:{rank}")
        grouped[row["target_surface"]][rank] = row
    required = {surface for pair in read_tsv(PAIR_SPECS) for surface in (pair["positive_surface"], pair["negative_surface"])}
    for target in required:
        if set(grouped[target]) != set(range(1, 13)):
            raise RuntimeError(f"incomplete GDT804 PRIMARY_K12 list: {target}")
    output: list[dict[str, Any]] = []
    for pair in read_tsv(PAIR_SPECS):
        positive_target, negative_target = pair["positive_surface"], pair["negative_surface"]
        for index in range(1, 25):
            positive_rank = (index - 1) % 12 + 1
            half = "ALIGNED_RANK" if index <= 12 else "NEXT_CYCLIC_NEGATIVE_RANK"
            requested_negative_rank = positive_rank if index <= 12 else positive_rank % 12 + 1
            used_negative_rank = requested_negative_rank
            positive_control = grouped[positive_target][positive_rank]["control_surface"]
            negative_control = grouped[negative_target][used_negative_rank]["control_surface"]
            advances = 0
            while negative_control == positive_control and advances < 12:
                used_negative_rank = used_negative_rank % 12 + 1
                negative_control = grouped[negative_target][used_negative_rank]["control_surface"]
                advances += 1
            if negative_control == positive_control:
                raise RuntimeError(f"K24 cannot find distinct negative surface: {pair['pair_id']}:{index}")
            output.append({
                "pseudo_pair_id": f"{pair['pair_id']}-K{index:02d}",
                "target_pair_id": pair["pair_id"], "deck_half": half,
                "positive_target_surface": positive_target,
                "negative_target_surface": negative_target,
                "positive_control_rank": positive_rank,
                "negative_control_rank_requested": requested_negative_rank,
                "negative_control_rank_used": used_negative_rank,
                "collision_advances": advances,
                "positive_control_surface": positive_control,
                "negative_control_surface": negative_control,
                "positive_individual_covariate_distance": grouped[positive_target][positive_rank]["individual_covariate_distance"],
                "negative_individual_covariate_distance": grouped[negative_target][used_negative_rank]["individual_covariate_distance"],
                "pool_variant": "PRIMARY_K12", "membership_universe": "GDT800_TERMINAL_L_ONLY",
                "line_mask": pipe((*TARGETS, positive_control, negative_control)),
                "added_feature_quarantine": pipe((positive_control, negative_control)),
                "view_id": "STABLE_PAIRED", "semantic_credit": 0,
            })
    if len(output) != 72:
        raise RuntimeError("K24 pseudo-pair deck cardinality drift")
    grouped_pairs: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in output:
        key = f"{row['positive_control_surface']}::{row['negative_control_surface']}"
        row["surface_pair_key"] = key
        grouped_pairs[(str(row["target_pair_id"]), key)].append(row)
    for (_target_pair, _key), members in grouped_pairs.items():
        first = str(members[0]["pseudo_pair_id"])
        for ordinal, row in enumerate(members, start=1):
            row["surface_pair_multiplicity"] = len(members)
            row["surface_pair_duplicate_ordinal"] = ordinal
            row["surface_pair_first_id"] = first
            row["unique_surface_pair_first_occurrence"] = int(ordinal == 1)
    return output


def g800_control_memberships(
    k24_specs: Sequence[dict[str, Any]], paragraph_by_locus: Mapping[str, Paragraph],
    line_by_locus: Mapping[str, Line], token_stability: Mapping[tuple[str, str, int], int],
    token_rows: Sequence[dict[str, str]],
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, dict[str, int]]]:
    controls = {
        str(spec[name]) for spec in k24_specs
        for name in ("positive_control_surface", "negative_control_surface")
    }
    raw: defaultdict[str, set[str]] = defaultdict(set)
    stable: defaultdict[str, set[str]] = defaultdict(set)
    g800_counts: Counter[str] = Counter()
    outside_counts: Counter[str] = Counter()
    rows = read_tsv(G800_OCCURRENCES)
    seen: set[str] = set()
    for row in rows:
        if row["occurrence_id"] in seen:
            raise RuntimeError(f"duplicate GDT800 occurrence: {row['occurrence_id']}")
        seen.add(row["occurrence_id"])
        if row["terminal"] != "l" or row["surface"] not in controls:
            continue
        surface = row["surface"]
        line = line_by_locus.get(row["locus"])
        index = int(row["token_index"])
        if line is None or line.page != row["page"] or index > len(line.tokens) or line.tokens[index - 1] != surface:
            raise RuntimeError(f"GDT800 control token replay failure: {row['occurrence_id']}")
        g800_counts[surface] += 1
        paragraph = paragraph_by_locus.get(row["locus"])
        if paragraph is None:
            outside_counts[surface] += 1
            continue
        raw[surface].add(paragraph.paragraph_id)
        if token_stability[(line.page, line.locus, index)]:
            stable[surface].add(paragraph.paragraph_id)
    guarded_counts = Counter(row["eva"] for row in token_rows if row["eva"] in controls)
    audit: dict[str, dict[str, int]] = {}
    for surface in sorted(controls):
        audit[surface] = {
            "gdt800_l_occurrences": g800_counts[surface],
            "guarded_all_token_occurrences": guarded_counts[surface],
            "guarded_occurrence_parity": int(g800_counts[surface] == guarded_counts[surface]),
            "strict_raw_paragraphs": len(raw[surface]),
            "strict_stable_paragraphs": len(stable[surface]),
            "outside_occurrences": outside_counts[surface],
        }
        if not audit[surface]["guarded_occurrence_parity"]:
            raise RuntimeError(f"GDT800/control guarded occurrence parity drift: {surface}")
    # GDT806 is a subset bridge, never the membership source.  Where present,
    # its frozen occurrence census must agree with GDT800.
    for row in read_tsv(G806_K12):
        surface = row["control_surface"]
        if surface in controls and int(row["control_occurrences"]) != g800_counts[surface]:
            raise RuntimeError(f"GDT806/GDT800 K12 occurrence parity drift: {surface}")
    return dict(raw), dict(stable), audit


def score_k24(
    paragraphs: Sequence[Paragraph], k24_specs: list[dict[str, Any]],
    exact_quarantine: frozenset[str], ed1_quarantine: frozenset[str],
    raw_membership: Mapping[str, set[str]], stable_membership: Mapping[str, set[str]],
    membership_audit: Mapping[str, Mapping[str, int]],
    target_scores: Mapping[tuple[str, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    spec_output: list[dict[str, Any]] = []
    score_output: list[dict[str, Any]] = []
    for spec in k24_specs:
        positive = str(spec["positive_control_surface"])
        negative = str(spec["negative_control_surface"])
        spec_output.append({
            **spec,
            "positive_gdt800_l_occurrences": membership_audit[positive]["gdt800_l_occurrences"],
            "negative_gdt800_l_occurrences": membership_audit[negative]["gdt800_l_occurrences"],
            "positive_guarded_all_token_occurrences": membership_audit[positive]["guarded_all_token_occurrences"],
            "negative_guarded_all_token_occurrences": membership_audit[negative]["guarded_all_token_occurrences"],
            "positive_guarded_parity": membership_audit[positive]["guarded_occurrence_parity"],
            "negative_guarded_parity": membership_audit[negative]["guarded_occurrence_parity"],
        })
        line_mask = frozenset(TARGET_SET | {positive, negative})
        pseudo_quarantine = frozenset(set(exact_quarantine) | {positive, negative})
        representations = {
            paragraph.paragraph_id: build_representation(paragraph, line_mask, pseudo_quarantine, ed1_quarantine)
            for paragraph in paragraphs
        }
        memberships: dict[str, set[str]] = {}
        for paragraph in paragraphs:
            values: set[str] = set()
            if paragraph.paragraph_id in stable_membership.get(positive, set()):
                values.add(positive)
            if paragraph.paragraph_id in stable_membership.get(negative, set()):
                values.add(negative)
            memberships[paragraph.paragraph_id] = values
        units, both = make_units(
            paragraphs, representations, "STABLE_PAIRED", positive, negative,
            membership_override=memberships,
        )
        result = score_units(
            units, str(spec["pseudo_pair_id"]), "STABLE_PAIRED",
            include_predictions=False, context="K24_PSEUDO_PAIR",
        )
        target_auc = target_scores[(str(spec["target_pair_id"]), "STABLE_PAIRED")]["auc"]
        score_output.append({
            "pseudo_pair_id": spec["pseudo_pair_id"], "target_pair_id": spec["target_pair_id"],
            "view_id": "STABLE_PAIRED", "positive_control_surface": positive,
            "negative_control_surface": negative,
            "eligible_paragraph_universe": sum(rep.eligible for rep in representations.values()),
            "positive_paragraphs": result["positive_paragraphs"],
            "negative_paragraphs": result["negative_paragraphs"],
            "positive_folios": result["positive_folios"],
            "negative_folios": result["negative_folios"],
            "both_member_paragraphs_excluded": both,
            "scoreable_predictions": result["scoreable_predictions"],
            "invalid_training_folds": result["invalid_folds"],
            "auc_ties_half": f12(result["auc"]),
            "balanced_accuracy_zero_ties_half": f12(result["balanced_accuracy"]),
            "model_scoreable": int(result["scoreable"]),
            "target_stable_paired_auc": f12(target_auc),
            "pseudo_auc_ge_target_ties_against": int(result["scoreable"] and target_auc is not None and result["auc"] >= target_auc),
            "membership_source": "GDT800_TERMINAL_L_ONLY",
            "guarded_all_token_membership_credit": 0,
        })
    return spec_output, score_output


def folio_removal_diagnostics(
    pair_specs: Sequence[dict[str, str]], unit_lookup: Mapping[tuple[str, str], list[Unit]],
    target_scores: Mapping[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    view_id = "STABLE_PAIRED"
    for pair in pair_specs:
        pair_id = pair["pair_id"]
        units = unit_lookup[(pair_id, view_id)]
        full_auc = target_scores[(pair_id, view_id)]["auc"]
        for removed in sorted({unit.paragraph.physical_folio for unit in units}):
            retained = [unit for unit in units if unit.paragraph.physical_folio != removed]
            result = score_units(retained, pair_id, view_id, include_predictions=False, context=f"REMOVED_{removed}")
            output.append({
                "pair_id": pair_id, "view_id": view_id, "removed_physical_folio": removed,
                "removed_paragraphs": len(units) - len(retained),
                "remaining_positive_paragraphs": result["positive_paragraphs"],
                "remaining_negative_paragraphs": result["negative_paragraphs"],
                "remaining_positive_folios": result["positive_folios"],
                "remaining_negative_folios": result["negative_folios"],
                "scoreable_predictions": result["scoreable_predictions"],
                "invalid_training_folds": result["invalid_folds"],
                "auc_ties_half": f12(result["auc"]),
                "balanced_accuracy_zero_ties_half": f12(result["balanced_accuracy"]),
                "full_stable_paired_auc": f12(full_auc),
                "auc_delta_from_full": f12(None if result["auc"] is None or full_auc is None else result["auc"] - full_auc),
                "removal_scoreable": int(result["scoreable"]),
                "auc_above_half": int(result["scoreable"] and result["auc"] > 0.5),
                "removal_status": "SCOREABLE" if result["scoreable"] else "UNSCOREABLE_FAIL_CLOSED",
            })
    return output


def landmark_rows(
    pair_specs: Sequence[dict[str, str]], unit_lookup: Mapping[tuple[str, str], list[Unit]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    view_id = "STABLE_PAIRED"
    for pair in pair_specs:
        pair_id = pair["pair_id"]
        units = unit_lookup[(pair_id, view_id)]
        vocabulary, full_weights, _pos_total, _neg_total = fold_weights(units)
        paragraph_counts: Counter[str] = Counter()
        folios_by_surface: defaultdict[str, set[str]] = defaultdict(set)
        positive_counts: Counter[str] = Counter()
        negative_counts: Counter[str] = Counter()
        for unit in units:
            paragraph_counts.update(unit.counts.keys())
            for surface in unit.counts:
                folios_by_surface[surface].add(unit.paragraph.physical_folio)
            (positive_counts if unit.label else negative_counts).update(unit.counts)
        folios = sorted({unit.paragraph.physical_folio for unit in units})
        for surface in sorted(vocabulary):
            full_weight = full_weights[surface]
            full_sign = 1 if full_weight > 0 else -1 if full_weight < 0 else 0
            scoreable_folds = 0
            same_sign_folds = 0
            zero_sign_folds = 0
            for held in folios:
                train = [unit for unit in units if unit.paragraph.physical_folio != held]
                if not any(unit.label for unit in train) or not any(not unit.label for unit in train):
                    continue
                fold_vocab, weights, _pt, _nt = fold_weights(train)
                if surface not in fold_vocab:
                    continue
                scoreable_folds += 1
                sign = 1 if weights[surface] > 0 else -1 if weights[surface] < 0 else 0
                same_sign_folds += int(sign == full_sign and full_sign != 0)
                zero_sign_folds += int(sign == 0)
            rate = same_sign_folds / scoreable_folds if scoreable_folds else None
            capacity = paragraph_counts[surface] >= 5 and len(folios_by_surface[surface]) >= 4
            direction = rate is not None and rate >= 0.8
            output.append({
                "pair_id": pair_id, "view_id": view_id, "surface": surface,
                "positive_token_count": positive_counts[surface],
                "negative_token_count": negative_counts[surface],
                "eligible_paragraphs_with_surface": paragraph_counts[surface],
                "eligible_folios_with_surface": len(folios_by_surface[surface]),
                "full_training_log_odds": f12(full_weight),
                "full_direction": "POSITIVE" if full_sign > 0 else "NEGATIVE" if full_sign < 0 else "TIE",
                "scoreable_folds": scoreable_folds,
                "same_direction_folds": same_sign_folds,
                "zero_direction_folds": zero_sign_folds,
                "same_direction_rate": f12(rate),
                "capacity_gate_5_paragraphs_4_folios": int(capacity),
                "direction_gate_80_percent": int(direction),
                "landmark_status": "PARAGRAPH_ECOLOGY_LANDMARK" if capacity and direction and full_sign else "NOT_LANDMARK",
                "structural_label_only": 1, "semantic_credit": 0,
            })
    return output


def target_capacity_rows(
    paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
    paragraph_by_locus: Mapping[str, Paragraph], events_by_target: Mapping[str, list[dict[str, str]]],
    lcs_audit: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    audit_by_id = {row["occurrence_id"]: row for row in lcs_audit}
    output: list[dict[str, Any]] = []
    for surface in TARGETS:
        events = events_by_target[surface]
        for mode in ("RAW", "GDT805_RANK_STABLE", "UNIQUE_FORCED_LCS_AUDIT"):
            if mode == "RAW":
                selected = events
                memberships = {p.paragraph_id for p in paragraphs if surface in p.raw_memberships}
            elif mode == "GDT805_RANK_STABLE":
                selected = [row for row in events if row["target_token_stable_all_three"] == "1"]
                memberships = {p.paragraph_id for p in paragraphs if surface in p.stable_memberships}
            else:
                selected = [row for row in events if audit_by_id[row["occurrence_id"]]["all_three_unique_forced_exact_alignment"] == 1]
                memberships = {p.paragraph_id for p in paragraphs if surface in p.lcs_memberships}
            strict_events = [row for row in selected if row["locus"] in paragraph_by_locus]
            eligible_ids = {pid for pid in memberships if representations[pid].eligible}
            selected_folios = {
                paragraph_by_locus[row["locus"]].physical_folio for row in strict_events
            }
            output.append({
                "surface": surface, "membership_mode": mode,
                "gdt805_external_occurrences": len(events),
                "selected_occurrences": len(selected),
                "selected_strict_occurrences": len(strict_events),
                "selected_outside_occurrences": len(selected) - len(strict_events),
                "strict_paragraph_memberships": len(memberships),
                "strict_folios": len(selected_folios),
                "post_mask_eligible_paragraphs": len(eligible_ids),
                "post_mask_eligible_folios": len({
                    paragraph.physical_folio for paragraph in paragraphs
                    if paragraph.paragraph_id in eligible_ids
                }),
                "paragraph_vote_per_surface": 1,
                "common_seven_target_line_mask": 1,
                "primary_membership": int(mode != "UNIQUE_FORCED_LCS_AUDIT"),
                "audit_only": int(mode == "UNIQUE_FORCED_LCS_AUDIT"),
                "semantic_credit": 0,
            })
    return output


def paragraph_atlas_rows(
    paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        rep = representations[paragraph.paragraph_id]
        output.append({
            "paragraph_id": paragraph.paragraph_id, "paragraph_ordinal": paragraph.ordinal,
            "page": paragraph.page, "physical_folio": paragraph.physical_folio,
            "paragraph_ordinal_on_page": paragraph.page_ordinal,
            "start_locus": paragraph.lines[0].locus, "end_locus": paragraph.lines[-1].locus,
            "start_line_number": paragraph.lines[0].number, "end_line_number": paragraph.lines[-1].number,
            "section": paragraph.section, "language": paragraph.language, "hand": paragraph.hand,
            "source_line_count": len(paragraph.lines),
            "source_token_count": sum(len(line.tokens) for line in paragraph.lines),
            "common_masked_line_count": len(rep.masked_loci),
            "common_masked_loci": pipe(rep.masked_loci),
            "surviving_line_count": len(rep.surviving_loci),
            "surviving_loci": pipe(rep.surviving_loci),
            "basis_retained_token_count": rep.basis_token_count,
            "basis_nonempty_retained_lines": rep.basis_nonempty_line_count,
            "post_mask_length_bin": rep.length_bin if rep.length_bin is not None else "NA",
            "basis_eligible_12_tokens_2_lines": int(rep.eligible),
            "exact_feature_token_count": sum(rep.exact_counts.values()),
            "exact_feature_type_count": len(rep.exact_counts),
            "exact_feature_counts": feature_string(rep.exact_counts),
            "ed1_feature_token_count": sum(rep.ed1_counts.values()),
            "ed1_feature_type_count": len(rep.ed1_counts),
            "ed1_feature_counts": feature_string(rep.ed1_counts),
            "raw_target_memberships": pipe(sorted(paragraph.raw_memberships)),
            "stable_target_memberships": pipe(sorted(paragraph.stable_memberships)),
            "lcs_audit_target_memberships": pipe(sorted(paragraph.lcs_memberships)),
            "raw_target_membership_count": len(paragraph.raw_memberships),
            "stable_target_membership_count": len(paragraph.stable_memberships),
            "lcs_audit_target_membership_count": len(paragraph.lcs_memberships),
            "semantic_credit": 0,
        })
    return output


def source_census_rows(
    lines: Sequence[Line], paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
    exact_quarantine: frozenset[str], ed1_quarantine: frozenset[str], partners: Mapping[str, str],
) -> list[dict[str, Any]]:
    strict_loci = {line.locus for paragraph in paragraphs for line in paragraph.lines}
    metrics = [
        ("allowlist_selectors", EXPECTED["selectors"], EXPECTED["selectors"], "inherited page selector scope"),
        ("normalized_physical_folios", len({physical_folio(line.page) for line in lines}), 173, "split selectors collapsed by ^(f\\d+[rv])"),
        ("guarded_source_lines", len(lines), EXPECTED["source_lines"], "line/cross key parity"),
        ("guarded_source_tokens", sum(len(line.tokens) for line in lines), EXPECTED["source_tokens"], "token/line text parity"),
        ("empty_source_lines", sum(not line.tokens for line in lines), 9, "retained in source census"),
        ("strict_complete_paragraphs", len(paragraphs), EXPECTED["strict_paragraphs"], "start=1 through end=1 only"),
        ("strict_included_lines", len(strict_loci), EXPECTED["strict_lines"], "no nearest-previous fill"),
        ("strict_included_tokens", sum(len(line.tokens) for line in lines if line.locus in strict_loci), EXPECTED["strict_tokens"], "strict start/end membership"),
        ("outside_paragraph_lines", sum(line.locus not in strict_loci for line in lines), EXPECTED["outside_lines"], "explicit outside class"),
        ("outside_paragraph_tokens", sum(len(line.tokens) for line in lines if line.locus not in strict_loci), EXPECTED["outside_tokens"], "never assigned to a paragraph"),
        ("common_target_masked_strict_lines", sum(len(rep.masked_loci) for rep in representations.values()), None, "complete lines containing any registered target"),
        ("basis_eligible_paragraphs", sum(rep.eligible for rep in representations.values()), None, "after line mask before feature quarantine"),
        ("gdt805_target_wholes_quarantined", 11, 11, "complete wholes only"),
        ("gdt800_exact_partner_wholes_quarantined", len(partners), 11, "one m-partner per target l-whole"),
        ("exact_family_quarantine_wholes", len(exact_quarantine), 22, "11 targets plus 11 exact partners"),
        ("global_target_ed1_quarantine_wholes_observed", len(ed1_quarantine), None, "observed surfaces at edit distance <=1 from seven targets"),
    ]
    return [{
        "metric": metric, "observed_value": observed,
        "registered_expected_value": expected if expected is not None else "NOT_FIXED",
        "expected_match": "NA" if expected is None else int(observed == expected),
        "definition": definition,
    } for metric, observed, expected, definition in metrics]


def marker_overlay_rows(
    paragraphs: Sequence[Paragraph], line_by_locus: Mapping[str, Line],
    paragraph_by_locus: Mapping[str, Paragraph], representations: Mapping[str, Representation],
    pair_specs: Sequence[dict[str, str]], view_specs: Sequence[dict[str, str]],
    unit_lookup: Mapping[tuple[str, str], list[Unit]],
) -> list[dict[str, Any]]:
    specs = {row["surface"]: row for row in read_tsv(MARKER_SPECS)}
    high = read_tsv(G757_OCCURRENCES)
    if len(high) != 79:
        raise RuntimeError("GDT757 high-marker occurrence capacity drift")
    events: defaultdict[str, list[str]] = defaultdict(list)
    for row in high:
        surface, locus = row["surface"], row["locus"]
        if surface not in specs or specs[surface]["marker_class"] != "HIGH_LINE_INITIAL_PURITY_WHOLE":
            raise RuntimeError(f"unregistered high positional marker: {surface}")
        line = line_by_locus.get(locus)
        if line is None or line.page != row["page"] or not line.tokens or line.tokens[0] != surface:
            raise RuntimeError(f"GDT757 high-marker replay failure: {row['occurrence_id']}")
        events[surface].append(locus)
    low_rows = {row["surface"]: row for row in read_tsv(G757_LOW)}
    for surface, spec in specs.items():
        if spec["marker_class"] != "LOW_PURITY_POSITIONAL_CONTROL":
            continue
        loci = [
            line.locus for line in line_by_locus.values()
            if line.tokens and line.tokens[0] == surface and line.token_stable[0] == 1
        ]
        if surface not in low_rows or len(loci) != int(low_rows[surface]["reader_exact_line_initial_occurrences"]):
            raise RuntimeError(f"low positional-marker census drift: {surface}")
        events[surface].extend(sorted(loci))
    output: list[dict[str, Any]] = []
    for pair in pair_specs:
        for view in view_specs:
            key = (pair["pair_id"], view["view_id"])
            units = unit_lookup[key]
            unit_by_pid = {unit.paragraph.paragraph_id: unit for unit in units}
            for surface, spec in specs.items():
                strict = [locus for locus in events[surface] if locus in paragraph_by_locus]
                surviving = [
                    locus for locus in strict
                    if locus in representations[paragraph_by_locus[locus].paragraph_id].surviving_loci
                ]
                eligible_events = [
                    locus for locus in surviving
                    if paragraph_by_locus[locus].paragraph_id in unit_by_pid
                ]
                positive_pids = {
                    paragraph_by_locus[locus].paragraph_id for locus in eligible_events
                    if unit_by_pid[paragraph_by_locus[locus].paragraph_id].label == 1
                }
                negative_pids = {
                    paragraph_by_locus[locus].paragraph_id for locus in eligible_events
                    if unit_by_pid[paragraph_by_locus[locus].paragraph_id].label == 0
                }
                output.append({
                    "pair_id": pair["pair_id"], "view_id": view["view_id"],
                    "marker_surface": surface, "marker_class": spec["marker_class"],
                    "source_line_initial_events": len(events[surface]),
                    "strict_paragraph_events": len(strict),
                    "common_masked_line_events": len(strict) - len(surviving),
                    "common_surviving_line_events": len(surviving),
                    "eligible_exclusive_pair_events": len(eligible_events),
                    "positive_paragraphs_with_marker": len(positive_pids),
                    "negative_paragraphs_with_marker": len(negative_pids),
                    "eligible_paragraphs_with_marker": len(positive_pids | negative_pids),
                    "eligible_folios_with_marker": len({
                        paragraph_by_locus[locus].physical_folio for locus in eligible_events
                    }),
                    "selection_credit": 0, "semantic_credit": 0,
                    "german_renderer_credit": 0,
                })
    return output


def build_edges(
    paragraphs: Sequence[Paragraph], representations: Mapping[str, Representation],
    events_by_target: Mapping[str, list[dict[str, str]]], paragraph_by_locus: Mapping[str, Paragraph],
) -> list[dict[str, Any]]:
    first_event: dict[tuple[str, str], dict[str, str]] = {}
    for surface, events in events_by_target.items():
        for row in sorted(events, key=lambda value: (value["source_selector"], value["locus"], int(value["token_index"]))):
            if row["target_token_stable_all_three"] != "1" or row["locus"] not in paragraph_by_locus:
                continue
            paragraph = paragraph_by_locus[row["locus"]]
            if not representations[paragraph.paragraph_id].eligible:
                continue
            first_event.setdefault((surface, paragraph.paragraph_id), row)
    output: list[dict[str, Any]] = []
    for (surface, paragraph_id), row in sorted(first_event.items()):
        paragraph = next(value for value in paragraphs if value.paragraph_id == paragraph_id)
        output.append({
            "edge_id": f"G807E{len(output) + 1:04d}",
            "batch_id": "GDT807_TARGET_MASKED_PARAGRAPH_MEMBERSHIP",
            "page": paragraph.page, "physical_folio": leaf_folio(paragraph.page),
            "diagram_unit_id": f"STRICT_PARAGRAPH_{paragraph.paragraph_id}",
            "pivot_visual_id": f"TARGET_WHOLE_{surface}",
            "pivot_locus": f"{row['locus']}@{row['token_index']}",
            "target_visual_id": f"TARGET_MASKED_REMAINDER_{paragraph.paragraph_id}",
            "target_locus": paragraph.lines[0].locus,
            "relation_type": "TARGET_LINE_TO_STRICT_PARAGRAPH_REMAINDER",
            "direction_basis": "ORIGINAL_TARGET_MEMBERSHIP_BEFORE_COMMON_LINE_MASK",
            "ownership_basis": "SAME_STRICT_START_END_PARAGRAPH",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT807",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT807_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "EXACT_GDT805_RANK_STABLE_PARAGRAPH_MEMBERSHIP",
            "ambiguity_state": "STRUCTURAL_TEXT_RELATION_ZERO_SEMANTIC_CREDIT",
            "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
    return output


def run_edge_intake(packet: Path, output: Path, expected_rows: int) -> dict[str, Any]:
    if packet.is_relative_to(ROOT):
        checked_packet = packet
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix=".gdt807_edge_", dir=BASE)
        checked_packet = Path(temporary.name) / packet.name
        shutil.copyfile(packet, checked_packet)
    try:
        completed = subprocess.run(
            [str(VMANUS_EXP), "check-edge-packet", str(checked_packet)], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    finally:
        if temporary is not None:
            temporary.cleanup()
    if completed.returncode != 1 or completed.stderr:
        raise RuntimeError(f"GDT388 intake execution drift: rc={completed.returncode} stderr={completed.stderr}")
    result = json.loads(completed.stdout)
    if result.get("status") != "INVALID_PACKET" or result.get("packet_rows") != expected_rows or result.get("eligible_edges") != 0 or result.get("score_ready") is not False:
        raise RuntimeError("GDT388 edge packet did not fail closed as registered")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def structural_cards(
    pair_specs: Sequence[dict[str, str]], score_lookup: Mapping[tuple[str, str], dict[str, Any]],
    null_rows: Sequence[dict[str, Any]], k24_specs: Sequence[dict[str, Any]],
    k24_scores: Sequence[dict[str, Any]], removals: Sequence[dict[str, Any]],
    landmarks: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for pair in pair_specs:
        pair_id = pair["pair_id"]
        raw = score_lookup[(pair_id, "RAW_PAIRED")]
        stable = score_lookup[(pair_id, "STABLE_PAIRED")]
        stable_ed1 = score_lookup[(pair_id, "STABLE_ED1_SENSITIVITY")]
        stable_null = [
            row for row in null_rows
            if row["pair_id"] == pair_id and row["view_id"] == "STABLE_PAIRED"
        ]
        null_aucs = [float(row["auc_ties_half"]) for row in stable_null if row["model_scoreable"] == 1]
        cyclic_median = statistics.median(null_aucs) if null_aucs else None
        cyclic_rank = (
            1 + sum(value >= stable["auc"] for value in null_aucs)
            + (12 - len(null_aucs))
            if stable["auc"] is not None else None
        )
        cyclic_delta = None if cyclic_median is None or stable["auc"] is None else stable["auc"] - cyclic_median
        pseudo = [row for row in k24_scores if row["target_pair_id"] == pair_id]
        pseudo_aucs = [float(row["auc_ties_half"]) for row in pseudo if row["model_scoreable"] == 1]
        k24_rank = (
            1 + sum(value >= stable["auc"] for value in pseudo_aucs)
            if stable["auc"] is not None else None
        )
        pair_specs_k24 = [row for row in k24_specs if row["target_pair_id"] == pair_id]
        removal = [row for row in removals if row["pair_id"] == pair_id]
        scoreable_removals = [row for row in removal if row["removal_scoreable"] == 1]
        removal_successes = sum(row["auc_above_half"] == 1 for row in scoreable_removals)
        removal_rate = removal_successes / len(scoreable_removals) if scoreable_removals else None
        gate_capacity = (
            stable["positive_paragraphs"] >= 24 and stable["negative_paragraphs"] >= 24
            and stable["positive_folios"] >= 16 and stable["negative_folios"] >= 16
        )
        gate_raw_auc = raw["scoreable"] and raw["auc"] >= 0.60
        gate_stable_auc = stable["scoreable"] and stable["auc"] >= 0.60
        gate_stable_ed1_auc = stable_ed1["scoreable"] and stable_ed1["auc"] >= 0.60
        gate_stable_ba = stable["scoreable"] and stable["balanced_accuracy"] >= 0.60
        gate_cyclic = len(null_aucs) == 12 and cyclic_delta is not None and cyclic_delta >= 0.03 and cyclic_rank is not None and cyclic_rank <= 3
        gate_k24 = len(pseudo_aucs) >= 18 and k24_rank is not None and k24_rank <= 6
        gate_removal = removal_rate is not None and removal_rate >= 0.80
        robust = all((gate_capacity, gate_raw_auc, gate_stable_auc, gate_stable_ed1_auc, gate_stable_ba, gate_cyclic, gate_k24, gate_removal))
        provisional = (
            raw["scoreable"] and stable["scoreable"]
            and raw["auc"] >= 0.60 and stable["auc"] >= 0.60
            and stable["balanced_accuracy"] >= 0.60
        )
        decision = (
            "ROBUST_NONLOCAL_PARAGRAPH_ECOLOGY_SPLIT" if robust
            else "PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT" if provisional
            else "NO_PARAGRAPH_ECOLOGY_SPLIT"
        )
        output.append({
            "pair_id": pair_id, "positive_surface": pair["positive_surface"],
            "negative_surface": pair["negative_surface"], "purpose": pair["purpose"],
            "stable_positive_paragraphs": stable["positive_paragraphs"],
            "stable_negative_paragraphs": stable["negative_paragraphs"],
            "stable_positive_folios": stable["positive_folios"],
            "stable_negative_folios": stable["negative_folios"],
            "raw_paired_auc": f12(raw["auc"]),
            "stable_paired_auc": f12(stable["auc"]),
            "stable_paired_balanced_accuracy": f12(stable["balanced_accuracy"]),
            "stable_ed1_auc": f12(stable_ed1["auc"]),
            "stable_ed1_balanced_accuracy": f12(stable_ed1["balanced_accuracy"]),
            "cyclic_scoreable_offsets": len(null_aucs),
            "cyclic_auc_median": f12(cyclic_median),
            "stable_auc_minus_cyclic_median": f12(cyclic_delta),
            "cyclic_rank_of_13_ties_against": cyclic_rank if cyclic_rank is not None else "NA",
            "k24_scoreable_pseudo_pair_ids": len(pseudo_aucs),
            "k24_unique_surface_pairs": len({row["surface_pair_key"] for row in pair_specs_k24}),
            "k24_target_rank_ties_against": k24_rank if k24_rank is not None else "NA",
            "removal_diagnostics_total": len(removal),
            "removal_diagnostics_scoreable": len(scoreable_removals),
            "removal_auc_above_half": removal_successes,
            "removal_success_rate_scoreable": f12(removal_rate),
            "selected_landmarks": sum(
                row["pair_id"] == pair_id and row["landmark_status"] == "PARAGRAPH_ECOLOGY_LANDMARK"
                for row in landmarks
            ),
            "gate_stable_capacity_24_paragraphs_16_folios_each": int(gate_capacity),
            "gate_raw_paired_auc_ge_0_60": int(gate_raw_auc),
            "gate_stable_paired_auc_ge_0_60": int(gate_stable_auc),
            "gate_stable_ed1_auc_ge_0_60": int(gate_stable_ed1_auc),
            "gate_stable_paired_balanced_accuracy_ge_0_60": int(gate_stable_ba),
            "gate_cyclic_delta_ge_0_03_rank_le_3": int(gate_cyclic),
            "gate_k24_n_ge_18_rank_le_6": int(gate_k24),
            "gate_removal_success_rate_ge_0_80": int(gate_removal),
            "fallback_raw_stable_auc_and_stable_ba_ge_0_60": int(provisional),
            "decision": decision, "semantic_promotion": 0,
            "claim_ceiling": "STRUCTURAL_PARAGRAPH_ECOLOGY_ONLY",
        })
    return output


def rival_display_rows(
    capacities: Sequence[dict[str, Any]], cards: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    cap = {(row["surface"], row["membership_mode"]): row for row in capacities}
    output: list[dict[str, Any]] = []
    for rival in read_tsv(RIVAL_SPECS):
        surface = rival["surface"]
        associations = []
        decisions = []
        for card in cards:
            if card["positive_surface"] == surface:
                associations.append(f"{card['pair_id']}:POSITIVE")
                decisions.append(f"{card['pair_id']}={card['decision']}")
            if card["negative_surface"] == surface:
                associations.append(f"{card['pair_id']}:NEGATIVE")
                decisions.append(f"{card['pair_id']}={card['decision']}")
        output.append({
            "surface": surface, "rival_a_de": rival["rival_a_de"],
            "rival_b_de": rival["rival_b_de"],
            "registered_pair_roles": pipe(associations),
            "associated_structural_decisions": pipe(decisions),
            "raw_external_occurrences": cap[(surface, "RAW")]["selected_occurrences"],
            "raw_strict_paragraphs": cap[(surface, "RAW")]["strict_paragraph_memberships"],
            "stable_strict_paragraphs": cap[(surface, "GDT805_RANK_STABLE")]["strict_paragraph_memberships"],
            "stable_post_mask_eligible_paragraphs": cap[(surface, "GDT805_RANK_STABLE")]["post_mask_eligible_paragraphs"],
            "score_credit": 0, "semantic_credit": 0, "renderer_credit": 0,
            "selected_rival": "NONE", "display_only": 1,
        })
    return output


def implementation_clarifications() -> list[dict[str, Any]]:
    rows = (
        ("STRICT_BOUNDS", "paragraph construction", "Open only on paragraph_start=1; close only on paragraph_end=1; never nearest-fill outside lines."),
        ("BASIS_ELIGIBILITY", "eligibility", "Count >=12 tokens and >=2 nonempty lines after complete-line mask and before exact/ED1 feature quarantine."),
        ("LENGTH_BIN", "cyclic stratum", "floor(log2(post-line-mask pre-feature-quarantine token count))."),
        ("FAMILY_QUARANTINE", "feature exclusion", "Eleven GDT805 target l-wholes plus exactly their eleven paired GDT800 m-counterparts."),
        ("OOV_MEAN", "MNB score", "Mean denominator is only test tokens present in the held-fold vocabulary; OOV tokens are ignored."),
        ("ALL_OOV", "MNB score", "A paragraph with zero in-vocabulary tokens receives score 0 and remains a tied vote."),
        ("BA_ZERO", "balanced accuracy", "Score 0 contributes one-half correct credit to either true class."),
        ("FOLD_SCOREABLE", "LOFO", "A fold is scoreable only when both classes remain in training; empty vocabulary is permitted as all-zero ties."),
        ("CYCLIC_UNIVERSE", "exchange null", "Rotate whole membership sets including empty sets across every eligible paragraph; apply pair exclusivity afterward."),
        ("CYCLIC_DIRECTION", "exchange null", "Sort by page lexicographic, start line numeric, paragraph id; dest_i receives source_(i-k mod n)."),
        ("K24_UNIVERSE", "specificity control", "Control membership comes only from GDT800 terminal=l occurrences; guarded tokens are parity only."),
        ("K24_MASK", "specificity control", "Mask common seven targets plus both control wholes; add both controls to exact feature quarantine."),
        ("K24_VIEW", "specificity control", "Score only STABLE_PAIRED and rank against direct STABLE_PAIRED target AUC."),
        ("K24_DUPLICATES", "specificity disclosure", "Keep all 24 deterministic IDs but report repeated surface-pair keys; IDs are not claimed independent."),
        ("REMOVAL", "robustness", "Remove each union folio and rebuild complete LOFO; >0.5 fraction uses scoreable removals only."),
    )
    return [{
        "clarification_id": f"G807-I{index:02d}", "topic": topic,
        "implementation": implementation, "registered_source": "METHOD.md@390645a1",
        "score_or_pair_posthoc_adjustment": 0, "semantic_credit": 0,
    } for index, (_key, topic, implementation) in enumerate(rows, start=1)]


def report_text(result: Mapping[str, Any], cards: Sequence[dict[str, Any]], k24_specs: Sequence[dict[str, Any]], landmarks: Sequence[dict[str, Any]]) -> str:
    lines = [
        "# GDT807 — target-maskierte Absatzökologie", "",
        f"Status: `{result['status']}`", "", "## Ergebnis", "",
        "Der offizielle Lauf rekonstruiert exakt 665 vollständig durch Start-/Endflags",
        "begrenzte Absätze aus 4.137 guarded gelesenen Zeilen. Vor jedem Modell werden",
        "alle vollständigen Zeilen entfernt, die eines der sieben registrierten Zielwörter",
        "enthalten. Eligibility und Längenbin entstehen danach, aber noch vor der",
        "Ganzwort- beziehungsweise ED1-Featurequarantäne.", "",
        "| Paar | raw AUC | stable AUC | stable BA | stable ED1 AUC | cyclic Rang | K24 Rang | Removal | Entscheidung |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for card in cards:
        lines.append(
            f"| `{card['positive_surface']}` / `{card['negative_surface']}` | "
            f"{card['raw_paired_auc']} | {card['stable_paired_auc']} | {card['stable_paired_balanced_accuracy']} | {card['stable_ed1_auc']} | "
            f"{card['cyclic_rank_of_13_ties_against']}/13 | {card['k24_target_rank_ties_against']} | "
            f"{card['removal_success_rate_scoreable']} | `{card['decision']}` |"
        )
    gate_labels = {
        "gate_stable_capacity_24_paragraphs_16_folios_each": "stable capacity",
        "gate_raw_paired_auc_ge_0_60": "raw AUC",
        "gate_stable_paired_auc_ge_0_60": "stable AUC",
        "gate_stable_ed1_auc_ge_0_60": "stable ED1 AUC",
        "gate_stable_paired_balanced_accuracy_ge_0_60": "stable BA",
        "gate_cyclic_delta_ge_0_03_rank_le_3": "cyclic null",
        "gate_k24_n_ge_18_rank_le_6": "K24 specificity",
        "gate_removal_success_rate_ge_0_80": "single-folio removal",
    }
    lines.extend(["", "Fehlende Robust-Gates:", ""])
    for card in cards:
        failed = [label for field, label in gate_labels.items() if card[field] == 0]
        lines.append(f"- `{card['pair_id']}`: {', '.join(failed) if failed else 'keine'}.")
    decision_counts = Counter(card["decision"] for card in cards)
    lines.extend([
        "", "Kein Ergebnis ist eine Übersetzung. Ein positiver Ausgang benennt höchstens",
        "eine reproduzierbare Verteilung verschiedener exakter Ganzwörter in den übrigen",
        "Absatzzeilen. Deutsche Rivalen, Bilddeutungen und historische Rollen hatten null",
        "Auswahlgewicht.", "", "## Kontroll- und Leakage-Audit", "",
        "Die zyklische Null rotiert vollständige Membership-Sets einschließlich leerer Sets",
        "in den vorregistrierten section×language×hand×length-Strata. Die 24 K24-IDs pro",
        "Zielpaar sind eine deterministische Spezifitätskalibrierung, keine 24 unabhängigen",
        "Kontrollen und ausdrücklich kein p-Wert. Jedes Pseudopaar entfernt zusätzlich alle",
        "Zeilen mit seinen beiden Kontrollwörtern, damit das Modell sein Label nicht sieht.", "",
    ])
    for pair_id in sorted({row["target_pair_id"] for row in k24_specs}):
        rows = [row for row in k24_specs if row["target_pair_id"] == pair_id]
        lines.append(
            f"- `{pair_id}`: 24 feste IDs, {len({row['surface_pair_key'] for row in rows})} "
            "verschiedene Oberflächenpaare."
        )
    selected = [row for row in landmarks if row["landmark_status"] == "PARAGRAPH_ECOLOGY_LANDMARK"]
    lines.extend(["", "## Strukturelle Landmarks", ""])
    for card in cards:
        pair_rows = [row for row in landmarks if row["pair_id"] == card["pair_id"]]
        pair_selected = [row for row in pair_rows if row["landmark_status"] == "PARAGRAPH_ECOLOGY_LANDMARK"]
        strongest = sorted(pair_selected, key=lambda row: (-abs(float(row["full_training_log_odds"])), row["surface"]))[:8]
        examples = ", ".join(
            f"`{row['surface']}` ({'+' if float(row['full_training_log_odds']) > 0 else ''}{float(row['full_training_log_odds']):.3f})"
            for row in strongest
        ) or "keine"
        lines.append(
            f"- `{card['pair_id']}`: {len(pair_selected)}/{len(pair_rows)} Full-fit-Vokabularzeilen passieren "
            f"den breiten Stabilitätsgate; stärkste Beispiele: {examples}."
        )
    lines.extend([
        "", "Insbesondere ist 101/353 für `G807-P03` breit und nicht selektiv. Formen wie",
        "`qokedy` und `qokeody` können bloße Familien-Echos jenseits der ED1-Maske sein;",
        "kein Landmark erhält deshalb einen Gloss oder semantischen Kredit.",
    ])
    lines.extend([
        "", "## Claim ceiling", "",
        f"Entscheidungen: {decision_counts.get('ROBUST_NONLOCAL_PARAGRAPH_ECOLOGY_SPLIT', 0)} robust, "
        f"{decision_counts.get('PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT', 0)} provisional, "
        f"{decision_counts.get('NO_PARAGRAPH_ECOLOGY_SPLIT', 0)} ohne Split. "
        f"Der feste Landmark-Gate markiert {len(selected)} Paar×Oberflächen-Zeilen.", "",
        "`PARAGRAPH_ECOLOGY_LANDMARK` ist ausschließlich ein strukturelles Label. GDT807",
        "bestätigt kein Wort, Morphem, Rezept, Material, Verfahren, Medium, Leiden, Maß,",
        "Latein oder Deutsch. Das GDT388-Paket bleibt wegen bereits erfolgtem Formalzugriff",
        "absichtlich fail-closed und ist nicht score-ready.", "",
        "## Reproduktion", "",
        "```bash",
        "python3 experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/src/run.py",
        "python3 experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/src/validate.py",
        "./vmanus-exp check-edge-packet experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/artifacts/GDT807_GDT388_PARAGRAPH_EDGE_PACKET.tsv",
        "```", "",
    ])
    return "\n".join(lines)


def build(output_dir: Path) -> dict[str, Any]:
    started = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_lock = verify_manifest_inputs()
    lines, paragraphs, paragraph_by_locus, line_by_locus, query_stats, token_stability, token_rows = load_corpus()
    lcs_audit, events_by_target, all_g805_targets = attach_target_memberships(
        paragraphs, paragraph_by_locus, line_by_locus, token_stability,
    )
    exact_quarantine_set, partners = paired_partner_quarantine(all_g805_targets)
    exact_quarantine = frozenset(exact_quarantine_set)
    observed_surfaces = {surface for line in lines for surface in line.tokens}
    ed1_quarantine = frozenset(
        surface for surface in observed_surfaces
        if min(levenshtein(surface, target) for target in TARGETS) <= 1
    )
    common_representations = {
        paragraph.paragraph_id: build_representation(
            paragraph, TARGET_SET, exact_quarantine, ed1_quarantine,
        )
        for paragraph in paragraphs
    }
    pair_specs = read_tsv(PAIR_SPECS)
    view_specs = read_tsv(VIEW_SPECS)
    if len(pair_specs) != 3 or len(view_specs) != 4:
        raise RuntimeError("registered pair/view deck drift")
    if [row["view_id"] for row in view_specs] != [
        "RAW_PAIRED", "STABLE_PAIRED", "RAW_ED1_SENSITIVITY", "STABLE_ED1_SENSITIVITY",
    ]:
        raise RuntimeError("registered view order/content drift")

    paragraph_rows = paragraph_atlas_rows(paragraphs, common_representations)
    capacities = target_capacity_rows(
        paragraphs, common_representations, paragraph_by_locus, events_by_target, lcs_audit,
    )
    unit_rows, fold_rows, predictions, score_summaries, unit_lookup, score_lookup = direct_pair_models(
        paragraphs, common_representations, pair_specs, view_specs,
    )
    null_rows, stratum_rows = cyclic_nulls(
        paragraphs, common_representations, pair_specs, view_specs, score_lookup,
    )
    k24_seed = build_k24_specs()
    control_raw, control_stable, control_audit = g800_control_memberships(
        k24_seed, paragraph_by_locus, line_by_locus, token_stability, token_rows,
    )
    k24_specs, k24_scores = score_k24(
        paragraphs, k24_seed, exact_quarantine, ed1_quarantine,
        control_raw, control_stable, control_audit, score_lookup,
    )
    removals = folio_removal_diagnostics(pair_specs, unit_lookup, score_lookup)
    landmarks = landmark_rows(pair_specs, unit_lookup)
    markers = marker_overlay_rows(
        paragraphs, line_by_locus, paragraph_by_locus, common_representations,
        pair_specs, view_specs, unit_lookup,
    )
    cards = structural_cards(
        pair_specs, score_lookup, null_rows, k24_specs, k24_scores, removals, landmarks,
    )
    rivals = rival_display_rows(capacities, cards)
    census = source_census_rows(
        lines, paragraphs, common_representations, exact_quarantine,
        ed1_quarantine, partners,
    )
    clarifications = implementation_clarifications()

    write_tsv(output_dir / "SOURCE_LOCK.tsv", source_lock)
    write_tsv(output_dir / "GDT807_IMPLEMENTATION_CLARIFICATIONS.tsv", clarifications)
    write_tsv(output_dir / "GDT807_GUARDED_QUERY_STATS.tsv", query_stats)
    write_tsv(output_dir / "GDT807_SOURCE_CENSUS.tsv", census)
    write_tsv(output_dir / "GDT807_665_STRICT_PARAGRAPH_ATLAS.tsv", paragraph_rows)
    write_tsv(output_dir / "GDT807_TARGET_MEMBERSHIP_CAPACITY.tsv", capacities)
    write_tsv(output_dir / "GDT807_PAIR_UNITS.tsv", unit_rows)
    write_tsv(output_dir / "GDT807_FOLD_VOCABULARY_AUDIT.tsv", fold_rows)
    write_tsv(output_dir / "GDT807_HELD_FOLIO_PREDICTIONS.tsv", predictions)
    write_tsv(output_dir / "GDT807_PAIR_SCORE_SUMMARY.tsv", score_summaries)
    write_tsv(output_dir / "GDT807_CYCLIC_EXCHANGE_NULL.tsv", null_rows)
    write_tsv(output_dir / "GDT807_CYCLIC_STRATUM_AUDIT.tsv", stratum_rows)
    write_tsv(output_dir / "GDT807_K24_PSEUDO_PAIR_SPECS.tsv", k24_specs)
    write_tsv(output_dir / "GDT807_K24_PSEUDO_PAIR_SCORES.tsv", k24_scores)
    write_tsv(output_dir / "GDT807_FOLIO_REMOVAL_DIAGNOSTICS.tsv", removals)
    write_tsv(output_dir / "GDT807_LANDMARKS.tsv", landmarks)
    write_tsv(output_dir / "GDT807_POSITIONAL_MARKER_OVERLAY.tsv", markers)
    write_tsv(output_dir / "GDT807_CONCRETE_RIVAL_DISPLAY.tsv", rivals)
    write_tsv(output_dir / "GDT807_LCS_TARGET_AUDIT.tsv", lcs_audit)
    edge_packet = output_dir / "GDT807_GDT388_PARAGRAPH_EDGE_PACKET.tsv"
    edges = build_edges(paragraphs, common_representations, events_by_target, paragraph_by_locus)
    write_tsv(edge_packet, edges, EDGE_FIELDS)
    edge_intake = run_edge_intake(
        edge_packet, output_dir / "GDT807_GDT388_EDGE_INTAKE.json", len(edges),
    )
    write_tsv(output_dir / "GDT807_STRUCTURAL_CARD.tsv", cards)

    decision_counts = Counter(card["decision"] for card in cards)
    status = (
        f"COMPLETE__{decision_counts['ROBUST_NONLOCAL_PARAGRAPH_ECOLOGY_SPLIT']}_ROBUST__"
        f"{decision_counts['PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT']}_PROVISIONAL__"
        f"{decision_counts['NO_PARAGRAPH_ECOLOGY_SPLIT']}_NO_SPLIT__"
        "ZERO_SEMANTIC_PROMOTION"
    )
    artifacts_before_result = [
        output_dir / name for name in OUTPUT_NAMES
        if name != "RESULT.json" and (output_dir / name).is_file()
    ]
    result: dict[str, Any] = {
        "schema": "GDT807_RESULT_V1", "experiment_id": "GDT807", "status": status,
        "official_registered_basis_commit": "390645a1",
        "corpus": {
            "selectors": EXPECTED["selectors"], "physical_folios": len({p.physical_folio for p in paragraphs}),
            "guarded_lines": len(lines), "guarded_tokens": sum(len(line.tokens) for line in lines),
            "strict_complete_paragraphs": len(paragraphs),
            "strict_included_lines": sum(len(p.lines) for p in paragraphs),
            "strict_included_tokens": sum(len(line.tokens) for p in paragraphs for line in p.lines),
            "outside_lines": len(lines) - sum(len(p.lines) for p in paragraphs),
            "outside_tokens": sum(len(line.tokens) for line in lines) - sum(len(line.tokens) for p in paragraphs for line in p.lines),
            "basis_eligible_paragraphs": sum(rep.eligible for rep in common_representations.values()),
        },
        "mask": {
            "common_targets": list(TARGETS), "gdt805_target_wholes": sorted(all_g805_targets),
            "gdt800_exact_partner_wholes": sorted(partners.values()),
            "exact_quarantine_size": len(exact_quarantine), "observed_ed1_quarantine_size": len(ed1_quarantine),
            "eligibility_before_feature_quarantine": True,
        },
        "model": {
            "views": [row["view_id"] for row in view_specs], "alpha": ALPHA,
            "equal_class_priors": True, "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
            "physical_folio_regex": "^(f\\d+[rv])", "vocabulary_min_tokens": 2,
            "vocabulary_min_paragraphs": 2, "score": "MEAN_LOG_LIKELIHOOD_DIFFERENCE_OVER_IN_FOLD_VOCAB_TOKENS",
            "all_oov_score": 0, "auc_tie_credit": 0.5, "balanced_accuracy_zero_credit": 0.5,
        },
        "pairs": cards,
        "decision_counts": dict(sorted(decision_counts.items())),
        "cyclic": {"offsets": list(CYCLIC_OFFSETS), "stratification": "section|language|hand|floor_log2_basis_tokens", "ties_against_target": True},
        "k24": {
            "pseudo_pair_ids": len(k24_specs), "score_rows": len(k24_scores),
            "view": "STABLE_PAIRED", "membership": "GDT800_TERMINAL_L_ONLY",
            "unique_surface_pairs_by_target_pair": {
                pair["pair_id"]: len({row["surface_pair_key"] for row in k24_specs if row["target_pair_id"] == pair["pair_id"]})
                for pair in pair_specs
            },
            "independent_control_claim": False, "p_value_claim": False,
        },
        "landmarks": {
            "selected_pair_surface_rows": sum(row["landmark_status"] == "PARAGRAPH_ECOLOGY_LANDMARK" for row in landmarks),
            "structural_only": True,
        },
        "edge_intake": edge_intake,
        "sealed_data": {"f84": "NOT_OPENED", "f84r": "NOT_OPENED"},
        "new_pages_opened": 0, "semantic_promotions": 0,
        "confirmed_plaintexts": 0, "confirmed_lexemes": 0,
        "claim_ceiling": "STRUCTURAL_TARGET_MASKED_PARAGRAPH_ECOLOGY_ONLY",
        "inputs": {row["path"]: row["sha256"] for row in source_lock},
        "outputs": {rel(path) if path.is_relative_to(ROOT) else path.name: sha256(path) for path in artifacts_before_result},
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if output_dir.resolve() == DEFAULT_ARTIFACTS.resolve():
        (BASE / "REPORT.md").write_text(report_text(result, cards, k24_specs, landmarks), encoding="utf-8")
    elapsed = time.monotonic() - started
    print(json.dumps({"status": status, "output_dir": str(output_dir), "runtime_seconds": round(elapsed, 3)}, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    build(args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
