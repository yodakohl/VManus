#!/usr/bin/env python3
"""Independent, fail-closed validation for GDT807.

The validator intentionally does not import the experiment builder. It obtains
mixed transcription tables only through ``vmanus-exp query-tsv``, reconstructs
strict paragraphs and registered scores, then audits builder artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
VMANUS_EXP = ROOT / "vmanus-exp"

ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
LINES_RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
GDT805_ATLAS = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv"
GDT800_OCCURRENCES = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
GDT804_POOLS = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_NEAREST_CONTROL_POOLS.tsv"
GDT757_WHOLES = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_11_WHOLE_ROLE_ATLAS.tsv"
GDT757_OCCURRENCES = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv"
GDT757_CONTROLS = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/LOW_PURITY_HIGH_TRIAD_COMPARATORS.tsv"
PAIR_SPECS = SRC / "TARGET_PAIR_SPECS.tsv"
VIEW_SPECS = SRC / "MODEL_VIEW_SPECS.tsv"
POSITIONAL_SPECS = SRC / "POSITIONAL_MARKER_SPECS.tsv"
RIVAL_SPECS = SRC / "CONCRETE_RIVAL_DISPLAY_SPECS.tsv"

ALL_TARGETS = frozenset((
    "chal", "chedal", "cheol", "okail", "okal", "ol", "otal",
    "qokeol", "qokol", "qotal", "sail",
))
MASK_TARGETS = frozenset(("cheol", "otal", "okal", "ol", "qokeol", "qokol", "qotal"))
VIEWS = ("RAW_PAIRED", "STABLE_PAIRED", "RAW_ED1_SENSITIVITY", "STABLE_ED1_SENSITIVITY")
ALPHA = 0.5
EXPECTED_AMENDMENT = "390645a1"
EXPECTED_COUNTS = {
    "allowlist_selectors": 179, "raw_lines": 4137, "raw_tokens": 32339,
    "cross_lines": 4137, "strict_paragraphs": 665, "included_lines": 3807,
    "included_tokens": 31938, "outside_lines": 330, "outside_tokens": 401,
    "gdt805_occurrences": 1086, "gdt805_stable_occurrences": 916,
    "gdt800_occurrences": 4137, "gdt800_paired_stems": 155,
    "primary_k12_rows": 132,
}
MIXED_PATHS = {LINES_RAW.resolve(), CROSS_RAW.resolve(), TOKENS_RAW.resolve()}
FLOAT_TOL = 5e-10


@dataclass(frozen=True)
class Line:
    page: str
    locus: str
    number: int
    paragraph_start: bool
    paragraph_end: bool
    tokens: tuple[str, ...]
    section: str
    language: str
    hand: str


@dataclass(frozen=True)
class Paragraph:
    paragraph_id: str
    page: str
    physical_folio: str
    start_locus: str
    end_locus: str
    section: str
    language: str
    hand: str
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class Remainder:
    paragraph_id: str
    features: tuple[str, ...]
    retained_line_count: int
    retained_token_count: int
    masked_loci: tuple[str, ...]
    eligible: bool


@dataclass(frozen=True)
class Example:
    paragraph_id: str
    folio: str
    label: int
    features: tuple[str, ...]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    if path.resolve() in MIXED_PATHS:
        raise AssertionError(f"mixed source must be guarded: {rel(path)}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def truth(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "pass"}


def natural_page_key(page: str) -> tuple[Any, ...]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if not match:
        return (10**9, page)
    return (int(match.group(1)), 0 if match.group(2) == "r" else 1,
            int(match.group(3) or 0), page)


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+[rv])", page)
    if not match:
        raise AssertionError(f"cannot normalize physical folio: {page}")
    return match.group(1)


def locus_number(locus: str) -> int:
    try:
        return int(locus.rsplit(".", 1)[1])
    except (IndexError, ValueError) as exc:
        raise AssertionError(f"non-numeric locus: {locus}") from exc


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prior = list(range(len(b) + 1))
    for index_a, char_a in enumerate(a, 1):
        current = [index_a]
        for index_b, char_b in enumerate(b, 1):
            current.append(min(current[-1] + 1, prior[index_b] + 1,
                               prior[index_b - 1] + (char_a != char_b)))
        prior = current
    return prior[-1]


def guarded_query(path: Path, selector: str, allowed: Sequence[str],
                  columns: Sequence[str]) -> tuple[list[dict[str, str]], dict[str, Any], list[str]]:
    command = [str(VMANUS_EXP), "query-tsv", rel(path), "--selector", selector]
    for value in sorted(allowed, key=natural_page_key):
        command.extend(("--allow", value))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84",
                    "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, check=False, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        raise AssertionError(f"guarded query failed for {rel(path)}: {completed.stderr.strip()}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise AssertionError(f"missing/duplicate GUARD_STATS for {rel(path)}")
    stats = json.loads(stat_lines[0][12:])
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if rows and list(rows[0]) != list(columns):
        raise AssertionError(f"guarded query header drift for {rel(path)}")
    for row in rows:
        if row.get(selector, "").startswith("f84"):
            raise AssertionError(f"sealed selector materialized: {row[selector]}")
        if any(row.get(field, "").startswith("f84") for field in ("page", "locus")):
            raise AssertionError("sealed locus materialized")
    return rows, stats, command


def source_data() -> tuple[list[Line], dict[str, dict[str, tuple[str, ...]]], dict[str, tuple[str, ...]], dict[str, Any]]:
    allow_rows = read_tsv(ALLOWLIST)
    if read_header(ALLOWLIST) != ["page"]:
        raise AssertionError("allow-list header drift")
    pages = [row["page"] for row in allow_rows]
    if len(pages) != EXPECTED_COUNTS["allowlist_selectors"] or len(set(pages)) != len(pages):
        raise AssertionError("allow-list capacity/uniqueness drift")
    if any(page.startswith("f84") for page in pages):
        raise AssertionError("sealed page in allow-list")
    line_columns = ("page", "locus", "line_number", "paragraph_start", "paragraph_end",
                    "token_count", "eva_clean", "section", "language", "hand")
    line_rows, line_stats, line_command = guarded_query(LINES_RAW, "page", pages, line_columns)
    cross_columns = ("page", "locus", "zl3b_clean", "it2a_clean", "rf1b_clean")
    cross_rows, cross_stats, cross_command = guarded_query(CROSS_RAW, "page", pages, cross_columns)
    token_columns = ("page", "locus", "token_index", "eva")
    token_rows, token_stats, token_command = guarded_query(TOKENS_RAW, "page", pages, token_columns)
    if len(line_rows) != EXPECTED_COUNTS["raw_lines"]:
        raise AssertionError(f"line census drift: {len(line_rows)}")
    if len(cross_rows) != EXPECTED_COUNTS["cross_lines"]:
        raise AssertionError(f"cross-reader census drift: {len(cross_rows)}")
    if len(token_rows) != EXPECTED_COUNTS["raw_tokens"]:
        raise AssertionError(f"token census drift: {len(token_rows)}")
    lines: list[Line] = []
    line_loci: set[str] = set()
    for row in line_rows:
        tokens = tuple(row["eva_clean"].split())
        if len(tokens) != int(row["token_count"]):
            raise AssertionError(f"line token-count mismatch: {row['locus']}")
        if row["locus"] in line_loci:
            raise AssertionError(f"duplicate raw locus: {row['locus']}")
        line_loci.add(row["locus"])
        if int(row["line_number"]) != locus_number(row["locus"]):
            raise AssertionError(f"line-number/locus mismatch: {row['locus']}")
        lines.append(Line(row["page"], row["locus"], int(row["line_number"]),
                          truth(row["paragraph_start"]), truth(row["paragraph_end"]),
                          tokens, row["section"], row["language"], row["hand"]))
    lines.sort(key=lambda line: (natural_page_key(line.page), line.number, line.locus))
    cross: dict[str, dict[str, tuple[str, ...]]] = {}
    for row in cross_rows:
        if row["locus"] in cross:
            raise AssertionError(f"duplicate cross-reader locus: {row['locus']}")
        cross[row["locus"]] = {"zl3b": tuple(row["zl3b_clean"].split()),
                                "it2a": tuple(row["it2a_clean"].split()),
                                "rf1b": tuple(row["rf1b_clean"].split())}
    if set(cross) != line_loci:
        raise AssertionError("line/cross locus parity drift")
    token_map_mut: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in token_rows:
        token_map_mut[row["locus"]].append((int(row["token_index"]), row["eva"]))
    token_map: dict[str, tuple[str, ...]] = {}
    for locus, indexed in token_map_mut.items():
        indexed.sort()
        if [index for index, _ in indexed] != list(range(1, len(indexed) + 1)):
            raise AssertionError(f"non-contiguous token ordinals: {locus}")
        token_map[locus] = tuple(token for _, token in indexed)
    line_by_locus = {line.locus: line for line in lines}
    if not set(token_map) <= line_loci:
        raise AssertionError("token source contains a locus absent from line source")
    for locus in line_loci:
        token_map.setdefault(locus, ())
    for locus, tokens in token_map.items():
        if tokens != line_by_locus[locus].tokens or cross[locus]["zl3b"] != tokens:
            raise AssertionError(f"guarded token/line/cross parity drift: {locus}")
    return lines, cross, token_map, {
        "lines": {"stats": line_stats, "command": line_command, "rows": len(line_rows)},
        "cross": {"stats": cross_stats, "command": cross_command, "rows": len(cross_rows)},
        "tokens": {"stats": token_stats, "command": token_command, "rows": len(token_rows)},
    }


def strict_paragraphs(lines: Sequence[Line]) -> tuple[list[Paragraph], list[Line]]:
    paragraphs: list[Paragraph] = []
    outside: list[Line] = []
    active: list[Line] = []
    active_page: str | None = None

    def abandon() -> None:
        nonlocal active, active_page
        outside.extend(active)
        active = []
        active_page = None

    for line in lines:
        if active and line.page != active_page:
            abandon()
        if line.paragraph_start:
            if active:
                abandon()
            active = [line]
            active_page = line.page
        elif active:
            active.append(line)
        else:
            outside.append(line)
        if line.paragraph_end and active:
            values = {(item.section, item.language, item.hand) for item in active}
            if len(values) != 1:
                raise AssertionError(f"mixed metadata in paragraph ending {line.locus}")
            section, language, hand = next(iter(values))
            ordinal = len(paragraphs) + 1
            paragraphs.append(Paragraph(f"G807-P{ordinal:04d}", active[0].page,
                                        physical_folio(active[0].page), active[0].locus,
                                        active[-1].locus, section, language, hand, tuple(active)))
            active = []
            active_page = None
    abandon()
    observed = {
        "strict_paragraphs": len(paragraphs),
        "included_lines": sum(len(paragraph.lines) for paragraph in paragraphs),
        "included_tokens": sum(len(line.tokens) for paragraph in paragraphs for line in paragraph.lines),
        "outside_lines": len(outside), "outside_tokens": sum(len(line.tokens) for line in outside),
    }
    for key, value in observed.items():
        if value != EXPECTED_COUNTS[key]:
            raise AssertionError(f"strict paragraph census drift {key}: {value} != {EXPECTED_COUNTS[key]}")
    inside_loci = [line.locus for paragraph in paragraphs for line in paragraph.lines]
    if len(set(inside_loci)) != len(inside_loci) or set(inside_loci) & {line.locus for line in outside}:
        raise AssertionError("strict inside/outside paragraph partition is not disjoint")
    return paragraphs, outside


def stable_exact_occurrence(cross: Mapping[str, Mapping[str, tuple[str, ...]]],
                            locus: str, token_index: int, surface: str) -> bool:
    readers = cross.get(locus)
    if readers is None:
        raise AssertionError(f"occurrence locus absent from cross data: {locus}")
    zl = readers["zl3b"]
    if not 1 <= token_index <= len(zl) or zl[token_index - 1] != surface:
        raise AssertionError(f"occurrence ordinal/surface mismatch: {locus}:{token_index}:{surface}")
    rank = sum(token == surface for token in zl[:token_index])
    return all(sum(token == surface for token in tokens) >= rank for tokens in readers.values())


def membership_sources(paragraphs: Sequence[Paragraph], cross: Mapping[str, Mapping[str, tuple[str, ...]]]) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]], dict[str, frozenset[str]], dict[str, frozenset[str]], set[str], dict[str, Any]]:
    locus_to_pid = {line.locus: paragraph.paragraph_id for paragraph in paragraphs for line in paragraph.lines}
    pids = {paragraph.paragraph_id for paragraph in paragraphs}
    target_raw: dict[str, set[str]] = {pid: set() for pid in pids}
    target_stable: dict[str, set[str]] = {pid: set() for pid in pids}
    atlas = read_tsv(GDT805_ATLAS)
    if (len(atlas) != EXPECTED_COUNTS["gdt805_occurrences"]
            or not {row["surface"] for row in atlas} <= set(ALL_TARGETS)
            or set(ALL_TARGETS) - {row["surface"] for row in atlas} != {"okail"}):
        raise AssertionError("GDT805 occurrence atlas capacity/target drift")
    if len({row["occurrence_id"] for row in atlas}) != len(atlas):
        raise AssertionError("duplicate GDT805 occurrence ID")
    reconstructed_stable = 0
    atlas_outside = 0
    for row in atlas:
        observed = stable_exact_occurrence(cross, row["locus"], int(row["token_index"]), row["surface"])
        if observed != truth(row["target_token_stable_all_three"]):
            raise AssertionError(f"GDT805 stability mismatch: {row['occurrence_id']}")
        reconstructed_stable += int(observed)
        pid = locus_to_pid.get(row["locus"])
        if pid is None:
            atlas_outside += 1
        else:
            target_raw[pid].add(row["surface"])
            if observed:
                target_stable[pid].add(row["surface"])
    if reconstructed_stable != EXPECTED_COUNTS["gdt805_stable_occurrences"]:
        raise AssertionError("GDT805 stable occurrence capacity drift")
    gdt800 = read_tsv(GDT800_OCCURRENCES)
    if len(gdt800) != EXPECTED_COUNTS["gdt800_occurrences"] or len({row["stem"] for row in gdt800}) != EXPECTED_COUNTS["gdt800_paired_stems"]:
        raise AssertionError("GDT800 paired occurrence/stem capacity drift")
    surfaces_by_stem: dict[str, set[str]] = defaultdict(set)
    terminals_by_stem: dict[str, set[str]] = defaultdict(set)
    for row in gdt800:
        surfaces_by_stem[row["stem"]].add(row["surface"])
        terminals_by_stem[row["stem"]].add(row["terminal"])
    if any(terminals != {"l", "m"} for terminals in terminals_by_stem.values()):
        raise AssertionError("non-paired stem in GDT800 atlas")
    partners: set[str] = set()
    for target in ALL_TARGETS:
        stem = target[:-1]
        expected = {target, f"{stem}m"}
        if not target.endswith("l") or not expected <= surfaces_by_stem.get(stem, set()):
            raise AssertionError(f"missing exact GDT800 partner for {target}")
        partners.add(f"{stem}m")
    pools = [row for row in read_tsv(GDT804_POOLS) if row["pool_variant"] == "PRIMARY_K12"]
    if len(pools) != EXPECTED_COUNTS["primary_k12_rows"]:
        raise AssertionError("GDT804 PRIMARY_K12 capacity drift")
    by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in pools:
        by_target[row["target_surface"]].append(row)
    if set(by_target) != set(ALL_TARGETS):
        raise AssertionError("GDT804 PRIMARY_K12 target drift")
    for target, rows in by_target.items():
        if sorted(int(row["neighbor_rank"]) for row in rows) != list(range(1, 13)) or len({row["control_surface"] for row in rows}) != 12:
            raise AssertionError(f"GDT804 PRIMARY_K12 rank/control drift: {target}")
    controls = {row["control_surface"] for row in pools}
    control_raw: dict[str, set[str]] = {pid: set() for pid in pids}
    control_stable: dict[str, set[str]] = {pid: set() for pid in pids}
    k12_occurrences = k12_stable = k12_outside = 0
    gdt800_control_counts: Counter[str] = Counter()
    for row in gdt800:
        surface = row["surface"]
        if row["terminal"] != "l" or surface not in controls:
            continue
        k12_occurrences += 1
        gdt800_control_counts[surface] += 1
        stable = stable_exact_occurrence(cross, row["locus"], int(row["token_index"]), surface)
        k12_stable += int(stable)
        pid = locus_to_pid.get(row["locus"])
        if pid is None:
            k12_outside += 1
        else:
            control_raw[pid].add(surface)
            if stable:
                control_stable[pid].add(surface)
    guarded_control_counts = Counter(
        token for readers in cross.values() for token in readers["zl3b"] if token in controls
    )
    if guarded_control_counts != gdt800_control_counts:
        differences = {
            surface: (gdt800_control_counts[surface], guarded_control_counts[surface])
            for surface in sorted(controls)
            if gdt800_control_counts[surface] != guarded_control_counts[surface]
        }
        raise AssertionError(f"GDT800 l/control guarded all-token parity drift: {differences}")
    freeze = lambda source: {key: frozenset(value) for key, value in source.items()}
    audit = {
        "gdt805_rows": len(atlas), "gdt805_stable_rows": reconstructed_stable,
        "gdt805_outside_paragraph_rows": atlas_outside, "gdt800_rows": len(gdt800),
        "gdt800_paired_stems": len(surfaces_by_stem), "terminal_partner_surfaces": sorted(partners),
        "primary_k12_rows": len(pools), "primary_k12_control_surfaces": len(controls),
        "k12_gdt800_l_occurrences": k12_occurrences,
        "k12_gdt800_l_stable_occurrences": k12_stable,
        "k12_gdt800_l_outside_paragraph_occurrences": k12_outside,
        "k12_guarded_all_token_parity": True,
        "k12_gdt800_l_counts": dict(sorted(gdt800_control_counts.items())),
        "primary_k12": {target: [row["control_surface"] for row in sorted(rows, key=lambda item: int(item["neighbor_rank"]))] for target, rows in sorted(by_target.items())},
    }
    return freeze(target_raw), freeze(target_stable), freeze(control_raw), freeze(control_stable), partners, audit


def build_remainders(paragraphs: Sequence[Paragraph], quarantine: set[str],
                     extra_line_mask: frozenset[str] = frozenset(),
                     ed1_targets: frozenset[str] = frozenset()) -> dict[str, Remainder]:
    line_mask = MASK_TARGETS | extra_line_mask
    feature_quarantine = set(quarantine) | set(extra_line_mask)
    if ed1_targets:
        vocabulary = {token for paragraph in paragraphs for line in paragraph.lines for token in line.tokens}
        feature_quarantine.update(token for token in vocabulary if any(levenshtein(token, target) <= 1 for target in ed1_targets))
    result: dict[str, Remainder] = {}
    for paragraph in paragraphs:
        kept_lines: list[tuple[str, ...]] = []
        masked: list[str] = []
        basis_token_count = 0
        basis_nonempty_lines = 0
        for line in paragraph.lines:
            if set(line.tokens) & line_mask:
                masked.append(line.locus)
                continue
            basis_token_count += len(line.tokens)
            basis_nonempty_lines += int(bool(line.tokens))
            filtered = tuple(token for token in line.tokens if token not in feature_quarantine)
            if filtered:
                kept_lines.append(filtered)
        features = tuple(token for line in kept_lines for token in line)
        result[paragraph.paragraph_id] = Remainder(
            paragraph.paragraph_id, features, basis_nonempty_lines, basis_token_count,
            tuple(masked), basis_token_count >= 12 and basis_nonempty_lines >= 2)
    return result


def examples_for_pair(positive: str, negative: str, paragraphs: Sequence[Paragraph],
                      remainders: Mapping[str, Remainder], memberships: Mapping[str, frozenset[str]]) -> tuple[list[Example], int]:
    examples: list[Example] = []
    dual = 0
    for paragraph in paragraphs:
        remainder = remainders[paragraph.paragraph_id]
        if not remainder.eligible:
            continue
        members = memberships[paragraph.paragraph_id]
        has_positive, has_negative = positive in members, negative in members
        if has_positive and has_negative:
            dual += 1
        elif has_positive ^ has_negative:
            examples.append(Example(paragraph.paragraph_id, paragraph.physical_folio,
                                    1 if has_positive else 0, remainder.features))
    return examples, dual


def build_vocabulary(training: Sequence[Example]) -> tuple[str, ...]:
    token_counts: Counter[str] = Counter()
    paragraph_counts: Counter[str] = Counter()
    for example in training:
        token_counts.update(example.features)
        paragraph_counts.update(set(example.features))
    return tuple(sorted(token for token, count in token_counts.items() if count >= 2 and paragraph_counts[token] >= 2))


def train_weights(training: Sequence[Example], vocabulary: Sequence[str]) -> dict[str, float]:
    vocab = set(vocabulary)
    class_counts = {0: Counter(), 1: Counter()}
    totals = Counter()
    for example in training:
        filtered = [token for token in example.features if token in vocab]
        class_counts[example.label].update(filtered)
        totals[example.label] += len(filtered)
    width = len(vocabulary)
    if not width:
        return {}
    return {token: math.log((class_counts[1][token] + ALPHA) / (totals[1] + ALPHA * width)) - math.log((class_counts[0][token] + ALPHA) / (totals[0] + ALPHA * width)) for token in vocabulary}


def score_features(features: Sequence[str], weights: Mapping[str, float]) -> tuple[float, int]:
    values = [weights[token] for token in features if token in weights]
    return (math.fsum(values) / len(values), len(values)) if values else (0.0, 0)


def auc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positives = [score for label, score in zip(labels, scores) if label == 1]
    negatives = [score for label, score in zip(labels, scores) if label == 0]
    if not positives or not negatives:
        return None
    wins = sum(1.0 if positive > negative else 0.5 if positive == negative else 0.0
               for positive in positives for negative in negatives)
    return wins / (len(positives) * len(negatives))


def balanced_accuracy(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positives, negatives = sum(label == 1 for label in labels), sum(label == 0 for label in labels)
    if not positives or not negatives:
        return None
    tp = sum(label == 1 and score > 0 for label, score in zip(labels, scores))
    tn = sum(label == 0 and score < 0 for label, score in zip(labels, scores))
    zero_positive = sum(label == 1 and score == 0 for label, score in zip(labels, scores))
    zero_negative = sum(label == 0 and score == 0 for label, score in zip(labels, scores))
    return 0.5 * ((tp + 0.5 * zero_positive) / positives + (tn + 0.5 * zero_negative) / negatives)


def held_folio_score(examples: Sequence[Example]) -> dict[str, Any]:
    folios = sorted({example.folio for example in examples}, key=natural_page_key)
    class_folios = {label: {example.folio for example in examples if example.label == label} for label in (0, 1)}
    predictions: list[dict[str, Any]] = []
    fold_audit: list[dict[str, Any]] = []
    for held in folios:
        training = [example for example in examples if example.folio != held]
        testing = [example for example in examples if example.folio == held]
        fold_scoreable = {example.label for example in training} == {0, 1}
        if not fold_scoreable:
            fold_audit.append({"held_physical_folio": held, "training_paragraphs": len(training),
                               "test_paragraphs": len(testing), "scoreable": False,
                               "vocabulary_size": 0, "all_oov_test_paragraphs": 0})
            continue
        vocabulary = build_vocabulary(training)
        weights = train_weights(training, vocabulary)
        zero_count = 0
        for example in testing:
            score, in_vocab = score_features(example.features, weights)
            zero_count += int(in_vocab == 0)
            predictions.append({"paragraph_id": example.paragraph_id, "physical_folio": example.folio,
                                "label": example.label, "score": score,
                                "in_vocabulary_tokens": in_vocab, "vocabulary_size": len(vocabulary)})
        fold_audit.append({"held_physical_folio": held, "training_paragraphs": len(training),
                           "test_paragraphs": len(testing), "scoreable": True,
                           "vocabulary_size": len(vocabulary), "all_oov_test_paragraphs": zero_count})
    labels = [row["label"] for row in predictions]
    scores = [row["score"] for row in predictions]
    pair_scoreable = (
        bool(examples)
        and len(predictions) == len(examples)
        and {row["label"] for row in predictions} == {0, 1}
        and all(row["scoreable"] for row in fold_audit)
    )
    return {
        "scoreable": pair_scoreable,
        "positive_paragraphs": sum(example.label == 1 for example in examples),
        "negative_paragraphs": sum(example.label == 0 for example in examples),
        "positive_folios": len(class_folios[1]), "negative_folios": len(class_folios[0]),
        "total_folios": len(folios), "scoreable_folds": sum(row["scoreable"] for row in fold_audit),
        "auc": auc(labels, scores) if pair_scoreable else None,
        "balanced_accuracy": balanced_accuracy(labels, scores) if pair_scoreable else None,
        "zero_score_votes": sum(row["score"] == 0.0 for row in predictions),
        "all_oov_votes": sum(row["in_vocabulary_tokens"] == 0 for row in predictions),
        "predictions": predictions, "folds": fold_audit,
    }


def rotated_memberships(paragraphs: Sequence[Paragraph], remainders: Mapping[str, Remainder],
                        memberships: Mapping[str, frozenset[str]], offset: int) -> tuple[dict[str, frozenset[str]], dict[str, Any]]:
    paragraph_by_id = {paragraph.paragraph_id: paragraph for paragraph in paragraphs}
    strata: dict[tuple[str, str, str, int], list[str]] = defaultdict(list)
    for paragraph in paragraphs:
        remainder = remainders[paragraph.paragraph_id]
        if remainder.eligible:
            length_bin = int(math.floor(math.log2(remainder.retained_token_count)))
            strata[(paragraph.section, paragraph.language, paragraph.hand, length_bin)].append(paragraph.paragraph_id)
    result = dict(memberships)
    moved_sets = moved_target_flags = identity_assignments = 0
    for key in sorted(strata):
        ids = sorted(strata[key], key=lambda pid: (paragraph_by_id[pid].page,
                                                   paragraph_by_id[pid].lines[0].number, pid))
        n, shift = len(ids), offset % len(ids)
        original = [memberships[pid] & MASK_TARGETS for pid in ids]
        assigned = [original[(index - shift) % n] for index in range(n)]
        for pid, old, new in zip(ids, original, assigned):
            result[pid] = frozenset(new)
            moved_sets += int(old != new)
            identity_assignments += int(old == new)
            moved_target_flags += len(old ^ new)
    return result, {"offset": offset, "strata": len(strata),
                    "eligible_paragraphs": sum(map(len, strata.values())),
                    "moved_membership_sets": moved_sets,
                    "identity_assignments": identity_assignments,
                    "moved_target_flags": moved_target_flags}


def removal_diagnostics(examples: Sequence[Example]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for omitted in sorted({example.folio for example in examples}, key=natural_page_key):
        reduced = [example for example in examples if example.folio != omitted]
        result = held_folio_score(reduced)
        rows.append({"omitted_physical_folio": omitted, "remaining_paragraphs": len(reduced),
                     "scoreable": result["scoreable"], "auc": result["auc"],
                     "auc_gt_half": bool(result["scoreable"] and result["auc"] is not None and result["auc"] > 0.5)})
    return rows


def k24_specs(primary_k12: Mapping[str, Sequence[str]], positive: str, negative: str) -> list[dict[str, Any]]:
    positives, negatives = list(primary_k12[positive]), list(primary_k12[negative])
    if len(positives) != 12 or len(negatives) != 12:
        raise AssertionError("K24 source width drift")
    result: list[dict[str, Any]] = []
    for family, shift in (("MATCHED", 0), ("SHIFTED", 1)):
        for index, control_a in enumerate(positives):
            negative_index, attempts = (index + shift) % 12, 0
            while negatives[negative_index] == control_a and attempts < 12:
                negative_index, attempts = (negative_index + 1) % 12, attempts + 1
            if attempts == 12:
                raise AssertionError("no distinct K24 negative surface")
            result.append({"pseudo_pair_index": len(result) + 1, "family": family,
                           "positive_rank": index + 1,
                           "negative_initial_rank": ((index + shift) % 12) + 1,
                           "negative_effective_rank": negative_index + 1,
                           "positive_control": control_a, "negative_control": negatives[negative_index],
                           "collision_advances": attempts})
    return result


def rank_ties_against(target: float, controls: Sequence[float]) -> int:
    return 1 + sum(value >= target for value in controls)


def median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        raise AssertionError("median of empty list")
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2


def landmark_audit(pair_id: str, examples: Sequence[Example]) -> list[dict[str, Any]]:
    """Rebuild the fixed full-data-sign landmark diagnostic independently."""
    vocabulary = build_vocabulary(examples)
    full_weights = train_weights(examples, vocabulary)
    paragraph_counts: Counter[str] = Counter()
    folios_by_surface: dict[str, set[str]] = defaultdict(set)
    class_tokens = {0: Counter(), 1: Counter()}
    for example in examples:
        paragraph_counts.update(set(example.features))
        class_tokens[example.label].update(example.features)
        for surface in set(example.features):
            folios_by_surface[surface].add(example.folio)
    folios = sorted({example.folio for example in examples}, key=natural_page_key)
    output: list[dict[str, Any]] = []
    for surface in vocabulary:
        full_weight = full_weights[surface]
        full_sign = 1 if full_weight > 0 else -1 if full_weight < 0 else 0
        scoreable_folds = same_sign_folds = zero_sign_folds = 0
        for held in folios:
            training = [example for example in examples if example.folio != held]
            if {example.label for example in training} != {0, 1}:
                continue
            fold_vocab = build_vocabulary(training)
            if surface not in fold_vocab:
                continue
            fold_weight = train_weights(training, fold_vocab)[surface]
            fold_sign = 1 if fold_weight > 0 else -1 if fold_weight < 0 else 0
            scoreable_folds += 1
            same_sign_folds += int(full_sign != 0 and fold_sign == full_sign)
            zero_sign_folds += int(fold_sign == 0)
        rate = same_sign_folds / scoreable_folds if scoreable_folds else None
        capacity = paragraph_counts[surface] >= 5 and len(folios_by_surface[surface]) >= 4
        direction = rate is not None and rate >= 0.8
        output.append({
            "pair_id": pair_id, "surface": surface,
            "positive_token_count": class_tokens[1][surface],
            "negative_token_count": class_tokens[0][surface],
            "eligible_paragraphs_with_surface": paragraph_counts[surface],
            "eligible_folios_with_surface": len(folios_by_surface[surface]),
            "full_training_log_odds": full_weight,
            "full_direction": "POSITIVE" if full_sign > 0 else "NEGATIVE" if full_sign < 0 else "TIE",
            "scoreable_folds": scoreable_folds,
            "same_direction_folds": same_sign_folds,
            "zero_direction_folds": zero_sign_folds,
            "same_direction_rate": rate,
            "capacity_gate": capacity, "direction_gate": direction,
            "landmark_status": "PARAGRAPH_ECOLOGY_LANDMARK" if capacity and direction and full_sign else "NOT_LANDMARK",
        })
    return output


def positional_overlay_audit(
    lines: Sequence[Line], paragraphs: Sequence[Paragraph],
    cross: Mapping[str, Mapping[str, tuple[str, ...]]],
    exact_remainders: Mapping[str, Remainder],
    remainders_by_view: Mapping[str, Mapping[str, Remainder]],
    memberships_by_view: Mapping[str, Mapping[str, frozenset[str]]],
    pair_specs: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    specs = {row["surface"]: row for row in read_tsv(POSITIONAL_SPECS)}
    if len(specs) != 15:
        raise AssertionError("positional marker spec capacity drift")
    line_by_locus = {line.locus: line for line in lines}
    paragraph_by_locus = {
        line.locus: paragraph for paragraph in paragraphs for line in paragraph.lines
    }
    events: dict[str, list[str]] = defaultdict(list)
    high_rows = read_tsv(GDT757_OCCURRENCES)
    if len(high_rows) != 79:
        raise AssertionError("GDT757 high positional occurrence capacity drift")
    for row in high_rows:
        surface, locus = row["surface"], row["locus"]
        if (surface not in specs
                or specs[surface]["marker_class"] != "HIGH_LINE_INITIAL_PURITY_WHOLE"):
            raise AssertionError(f"unregistered high positional whole: {surface}")
        line = line_by_locus.get(locus)
        if line is None or line.page != row["page"] or not line.tokens or line.tokens[0] != surface:
            raise AssertionError(f"GDT757 high positional replay mismatch: {row['occurrence_id']}")
        events[surface].append(locus)
    low_source = {row["surface"]: row for row in read_tsv(GDT757_CONTROLS)}
    expected_low = {"ykar": (6, 5), "yteedy": (8, 5), "qotor": (11, 11), "dchey": (11, 9)}
    for surface, (all_initial, stable_initial) in expected_low.items():
        all_loci = [line.locus for line in lines if line.tokens and line.tokens[0] == surface]
        stable_loci = [
            line.locus for line in lines if line.tokens and line.tokens[0] == surface
            and stable_exact_occurrence(cross, line.locus, 1, surface)
        ]
        if len(all_loci) != all_initial or len(stable_loci) != stable_initial:
            raise AssertionError(f"low positional guarded census drift: {surface}")
        if surface not in low_source or int(low_source[surface]["reader_exact_line_initial_occurrences"]) != stable_initial:
            raise AssertionError(f"low positional GDT757 census mismatch: {surface}")
        events[surface].extend(stable_loci)
    rows: list[dict[str, Any]] = []
    for pair in pair_specs:
        pair_id, positive, negative = pair["pair_id"], pair["positive_surface"], pair["negative_surface"]
        for view in VIEWS:
            examples, _dual = examples_for_pair(
                positive, negative, paragraphs, remainders_by_view[view], memberships_by_view[view],
            )
            units = {example.paragraph_id: example for example in examples}
            for surface, spec in specs.items():
                strict = [locus for locus in events[surface] if locus in paragraph_by_locus]
                surviving = [
                    locus for locus in strict
                    if locus not in exact_remainders[paragraph_by_locus[locus].paragraph_id].masked_loci
                ]
                eligible = [locus for locus in surviving if paragraph_by_locus[locus].paragraph_id in units]
                positive_pids = {
                    paragraph_by_locus[locus].paragraph_id for locus in eligible
                    if units[paragraph_by_locus[locus].paragraph_id].label == 1
                }
                negative_pids = {
                    paragraph_by_locus[locus].paragraph_id for locus in eligible
                    if units[paragraph_by_locus[locus].paragraph_id].label == 0
                }
                rows.append({
                    "pair_id": pair_id, "view_id": view, "marker_surface": surface,
                    "marker_class": spec["marker_class"],
                    "source_line_initial_events": len(events[surface]),
                    "strict_paragraph_events": len(strict),
                    "common_masked_line_events": len(strict) - len(surviving),
                    "common_surviving_line_events": len(surviving),
                    "eligible_exclusive_pair_events": len(eligible),
                    "positive_paragraphs_with_marker": len(positive_pids),
                    "negative_paragraphs_with_marker": len(negative_pids),
                    "eligible_paragraphs_with_marker": len(positive_pids | negative_pids),
                    "eligible_folios_with_marker": len({
                        paragraph_by_locus[locus].physical_folio for locus in eligible
                    }),
                })
    return rows


def reconstruct() -> dict[str, Any]:
    lines, cross, token_map, query_audit = source_data()
    paragraphs, outside = strict_paragraphs(lines)
    target_raw, target_stable, control_raw, control_stable, partners, source_audit = membership_sources(paragraphs, cross)
    quarantine = set(ALL_TARGETS) | partners
    if len(quarantine) != 22 or len(partners) != 11:
        raise AssertionError("exact-family quarantine must be Q22 (11 l targets + 11 m partners)")
    exact_remainders = build_remainders(paragraphs, quarantine)
    ed1_remainders = build_remainders(paragraphs, quarantine, ed1_targets=MASK_TARGETS)
    remainders_by_view = {"RAW_PAIRED": exact_remainders, "STABLE_PAIRED": exact_remainders,
                          "RAW_ED1_SENSITIVITY": ed1_remainders, "STABLE_ED1_SENSITIVITY": ed1_remainders}
    memberships_by_view = {"RAW_PAIRED": target_raw, "STABLE_PAIRED": target_stable,
                           "RAW_ED1_SENSITIVITY": target_raw, "STABLE_ED1_SENSITIVITY": target_stable}
    pair_specs = read_tsv(PAIR_SPECS)
    if [row["pair_id"] for row in pair_specs] != ["G807-P01", "G807-P02", "G807-P03"]:
        raise AssertionError("registered pair spec drift")
    if [row["view_id"] for row in read_tsv(VIEW_SPECS)] != list(VIEWS):
        raise AssertionError("registered model view drift")
    pair_results: dict[str, Any] = {}
    all_landmarks: list[dict[str, Any]] = []
    for spec in pair_specs:
        pair_id, positive, negative = spec["pair_id"], spec["positive_surface"], spec["negative_surface"]
        views: dict[str, Any] = {}
        for view in VIEWS:
            examples, dual = examples_for_pair(positive, negative, paragraphs, remainders_by_view[view], memberships_by_view[view])
            scored = held_folio_score(examples)
            scored["dual_membership_paragraphs_excluded"] = dual
            scored["eligible_background_paragraphs"] = sum(rem.eligible for rem in remainders_by_view[view].values())
            views[view] = scored
        null_by_view: dict[str, list[dict[str, Any]]] = {}
        for view in VIEWS:
            null_rows: list[dict[str, Any]] = []
            for offset in range(1, 13):
                rotated, rotation_audit = rotated_memberships(
                    paragraphs, remainders_by_view[view], memberships_by_view[view], offset,
                )
                examples, dual = examples_for_pair(
                    positive, negative, paragraphs, remainders_by_view[view], rotated,
                )
                score = held_folio_score(examples)
                null_rows.append({**rotation_audit, "view_id": view,
                                  "dual_membership_paragraphs_excluded": dual,
                                  "positive_paragraphs": score["positive_paragraphs"],
                                  "negative_paragraphs": score["negative_paragraphs"],
                                  "positive_folios": score["positive_folios"],
                                  "negative_folios": score["negative_folios"],
                                  "scoreable": score["scoreable"], "auc": score["auc"],
                                  "balanced_accuracy": score["balanced_accuracy"]})
            null_by_view[view] = null_rows
        stable_null_rows = null_by_view["STABLE_PAIRED"]
        if not all(row["scoreable"] and row["auc"] is not None for row in stable_null_rows):
            raise AssertionError(f"unscoreable primary stable cyclic null: {pair_id}")
        stable_auc = views["STABLE_PAIRED"]["auc"]
        if stable_auc is None:
            raise AssertionError(f"unscoreable stable pair: {pair_id}")
        pseudo_rows: list[dict[str, Any]] = []
        for pseudo in k24_specs(source_audit["primary_k12"], positive, negative):
            control_a, control_b = pseudo["positive_control"], pseudo["negative_control"]
            extra_mask = frozenset((control_a, control_b))
            pseudo_remainders = build_remainders(paragraphs, quarantine, extra_line_mask=extra_mask)
            examples, dual = examples_for_pair(control_a, control_b, paragraphs, pseudo_remainders, control_stable)
            score = held_folio_score(examples)
            residual_tokens = sum(token in extra_mask for rem in pseudo_remainders.values() for token in rem.features)
            residual_lines = sum(line.locus not in pseudo_remainders[p.paragraph_id].masked_loci
                                 for p in paragraphs for line in p.lines if set(line.tokens) & extra_mask)
            if residual_tokens or residual_lines:
                raise AssertionError(f"K24 defining-surface leakage: {pair_id}/{pseudo['pseudo_pair_index']}")
            pseudo_rows.append({**pseudo, "dual_membership_paragraphs_excluded": dual,
                                "positive_paragraphs": score["positive_paragraphs"],
                                "negative_paragraphs": score["negative_paragraphs"],
                                "positive_folios": score["positive_folios"],
                                "negative_folios": score["negative_folios"],
                                "eligible_background_paragraphs": sum(rem.eligible for rem in pseudo_remainders.values()),
                                "scoreable": score["scoreable"], "auc": score["auc"],
                                "balanced_accuracy": score["balanced_accuracy"],
                                "all_oov_votes": score["all_oov_votes"],
                                "residual_defining_tokens": residual_tokens,
                                "residual_defining_lines": residual_lines})
        scoreable_k24 = [row for row in pseudo_rows if row["scoreable"] and row["auc"] is not None]
        k24_values = [row["auc"] for row in scoreable_k24]
        unique_k24_pairs = len({(row["positive_control"], row["negative_control"]) for row in pseudo_rows})
        expected_unique = 22 if pair_id == "G807-P01" else 24
        if unique_k24_pairs != expected_unique:
            raise AssertionError(
                f"{pair_id} K24 unique surface-pair capacity drift: "
                f"{unique_k24_pairs} != {expected_unique}"
            )
        stable_examples = examples_for_pair(positive, negative, paragraphs, exact_remainders, target_stable)[0]
        landmarks = landmark_audit(pair_id, stable_examples)
        all_landmarks.extend(landmarks)
        removals = removal_diagnostics(stable_examples)
        scoreable_removals = [row for row in removals if row["scoreable"]]
        removal_successes = sum(row["auc_gt_half"] for row in scoreable_removals)
        removal_fraction = removal_successes / len(scoreable_removals) if scoreable_removals else 0.0
        raw, stable, stable_ed1 = views["RAW_PAIRED"], views["STABLE_PAIRED"], views["STABLE_ED1_SENSITIVITY"]
        capacity_gate = stable["positive_paragraphs"] >= 24 and stable["negative_paragraphs"] >= 24 and stable["positive_folios"] >= 16 and stable["negative_folios"] >= 16
        direct_gate = raw["auc"] is not None and stable["auc"] is not None and raw["auc"] >= .60 and stable["auc"] >= .60
        ed1_gate = (
            stable_ed1["auc"] is not None
            and stable["balanced_accuracy"] is not None
            and stable_ed1["auc"] >= .60
            and stable["balanced_accuracy"] >= .60
        )
        null_values = [row["auc"] for row in stable_null_rows]
        null_median, null_rank = median(null_values), rank_ties_against(stable_auc, null_values)
        null_gate = stable_auc - null_median >= .03 and null_rank <= 3
        k24_rank = rank_ties_against(stable_auc, k24_values)
        k24_gate = len(scoreable_k24) >= 18 and k24_rank <= 6
        removal_gate = bool(scoreable_removals) and removal_fraction >= .80
        robust = capacity_gate and direct_gate and ed1_gate and null_gate and k24_gate and removal_gate
        provisional = raw["auc"] is not None and stable["auc"] is not None and stable["balanced_accuracy"] is not None and raw["auc"] >= .60 and stable["auc"] >= .60 and stable["balanced_accuracy"] >= .60
        decision = "ROBUST_NONLOCAL_PARAGRAPH_ECOLOGY_SPLIT" if robust else "PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT" if provisional else "NO_PARAGRAPH_ECOLOGY_SPLIT"
        pair_results[pair_id] = {
            "positive_surface": positive, "negative_surface": negative, "views": views,
            "cyclic_null_by_view": null_by_view, "null_median_auc": null_median,
            "null_target_rank_of_13_ties_against": null_rank, "k24": pseudo_rows,
            "k24_scoreable": len(scoreable_k24), "k24_unique_surface_pairs": unique_k24_pairs,
            "k24_target_rank_ties_against": k24_rank,
            "folio_removals": removals, "folio_removal_scoreable": len(scoreable_removals),
            "folio_removal_successes": removal_successes,
            "folio_removal_success_fraction": removal_fraction,
            "landmarks": landmarks,
            "gates": {"stable_capacity": capacity_gate, "raw_stable_auc": direct_gate,
                      "stable_ed1_auc_and_stable_paired_balanced_accuracy": ed1_gate,
                      "cyclic_exchange": null_gate, "k24_specificity": k24_gate,
                      "single_folio_removal": removal_gate}, "decision": decision}
    positional_overlay = positional_overlay_audit(
        lines, paragraphs, cross, exact_remainders, remainders_by_view,
        memberships_by_view, pair_specs,
    )
    return {"query_audit": query_audit, "source_audit": source_audit,
            "paragraphs": paragraphs, "outside_lines": outside,
            "target_raw_memberships": target_raw, "target_stable_memberships": target_stable,
            "control_raw_memberships": control_raw, "control_stable_memberships": control_stable,
            "exact_remainders": exact_remainders, "ed1_remainders": ed1_remainders,
            "pair_results": pair_results, "landmarks": all_landmarks,
            "positional_overlay": positional_overlay,
            "token_map": token_map}


def parse_float(value: str) -> float | None:
    return None if value in {"", "NA", "NONE", "null", "None"} else float(value)


def close_float(observed: float | None, expected: float | None) -> bool:
    return observed is expected if observed is None or expected is None else math.isclose(observed, expected, rel_tol=FLOAT_TOL, abs_tol=FLOAT_TOL)


def find_column(row: Mapping[str, str], *names: str) -> str:
    for name in names:
        if name in row:
            return row[name]
    raise AssertionError(f"none of required columns present: {names}")


def compare_outputs(rebuilt: Mapping[str, Any]) -> list[str]:
    checks: list[str] = []
    result_path = ART / "RESULT.json"
    if not result_path.is_file():
        raise AssertionError("builder RESULT.json is absent")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    checks.append("builder_result_json_parse")
    if result.get("official_registered_basis_commit") != "390645a1":
        raise AssertionError("RESULT registered-basis commit drift")
    corpus = result.get("corpus", {})
    for key, value in (("strict_complete_paragraphs", 665), ("strict_included_lines", 3807),
                       ("strict_included_tokens", 31938), ("outside_lines", 330),
                       ("outside_tokens", 401)):
        if corpus.get(key) != value:
            raise AssertionError(f"RESULT source census {key}: {corpus.get(key)} != {value}")
    if (result.get("mask", {}).get("exact_quarantine_size") != 22
            or not result.get("mask", {}).get("eligibility_before_feature_quarantine")):
        raise AssertionError("RESULT Q22/eligibility declaration drift")
    model = result.get("model", {})
    if (model.get("vocabulary_min_tokens"), model.get("vocabulary_min_paragraphs"),
            model.get("all_oov_score"), model.get("balanced_accuracy_zero_credit")) != (2, 2, 0, .5):
        raise AssertionError("RESULT model mechanics declaration drift")
    if (result.get("semantic_promotions"), result.get("confirmed_plaintexts"),
            result.get("confirmed_lexemes"), result.get("new_pages_opened")) != (0, 0, 0, 0):
        raise AssertionError("RESULT exceeded claim/page ceiling")
    if result.get("sealed_data") != {"f84": "NOT_OPENED", "f84r": "NOT_OPENED"}:
        raise AssertionError("RESULT sealed-data claim drift")
    for recorded_path, digest in result.get("outputs", {}).items():
        output_path = ROOT / recorded_path if "/" in recorded_path else ART / recorded_path
        if not output_path.is_file() or sha256(output_path) != digest:
            raise AssertionError(f"RESULT output hash mismatch: {recorded_path}")
    checks.append("result_output_hashes")
    checks.append("strict_source_census")

    lock_path = ART / "SOURCE_LOCK.tsv"
    query_path = ART / "GDT807_GUARDED_QUERY_STATS.tsv"
    if not lock_path.is_file() or not query_path.is_file():
        raise AssertionError("source-lock or guarded-query audit absent")
    lock_rows = read_tsv(lock_path)
    lock_index = {row["path"]: row for row in lock_rows}
    if len(lock_index) != len(lock_rows):
        raise AssertionError("duplicate SOURCE_LOCK path")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"]:
        row = lock_index.get(item["path"])
        if row is None or row["sha256"] != item["sha256"]:
            raise AssertionError(f"SOURCE_LOCK/manifest mismatch: {item['path']}")
    if result.get("inputs") != {row["path"]: row["sha256"] for row in lock_rows}:
        raise AssertionError("RESULT input-lock map mismatch")
    query_rows = read_tsv(query_path)
    expected_query_rows = {"ZL3B_LINES_179": 4137, "ZL3B_TOKENS_179": 32339,
                           "CROSS_READER_LINES_179": 4137}
    query_index = {row["query_id"]: row for row in query_rows}
    if set(query_index) != set(expected_query_rows):
        raise AssertionError("guarded-query ID universe drift")
    for query_id, selected in expected_query_rows.items():
        row = query_index[query_id]
        if (int(row["selected_rows"]) != selected
                or row["forbidden_prefixes"] != "f84|f84r"
                or int(row["query_returncode"]) != 0):
            raise AssertionError(f"guarded-query audit mismatch: {query_id}")
    checks.append("manifest_source_lock_and_three_guarded_queries")

    paragraph_path = ART / "GDT807_665_STRICT_PARAGRAPH_ATLAS.tsv"
    if not paragraph_path.is_file():
        raise AssertionError("strict paragraph atlas absent")
    paragraph_rows = read_tsv(paragraph_path)
    paragraph_index = {row["paragraph_id"]: row for row in paragraph_rows}
    if len(paragraph_rows) != 665 or len(paragraph_index) != 665:
        raise AssertionError("strict paragraph atlas cardinality/identity drift")
    for paragraph in rebuilt["paragraphs"]:
        row = paragraph_index.get(paragraph.paragraph_id)
        if row is None:
            raise AssertionError(f"strict paragraph missing from artifact: {paragraph.paragraph_id}")
        exact = rebuilt["exact_remainders"][paragraph.paragraph_id]
        ed1 = rebuilt["ed1_remainders"][paragraph.paragraph_id]
        exact_counts, ed1_counts = Counter(exact.features), Counter(ed1.features)
        expected_values = {
            "page": paragraph.page, "physical_folio": paragraph.physical_folio,
            "start_locus": paragraph.start_locus, "end_locus": paragraph.end_locus,
            "section": paragraph.section, "language": paragraph.language, "hand": paragraph.hand,
            "source_line_count": len(paragraph.lines),
            "source_token_count": sum(len(line.tokens) for line in paragraph.lines),
            "common_masked_line_count": len(exact.masked_loci),
            "surviving_line_count": len(paragraph.lines) - len(exact.masked_loci),
            "basis_retained_token_count": exact.retained_token_count,
            "basis_nonempty_retained_lines": exact.retained_line_count,
            "basis_eligible_12_tokens_2_lines": int(exact.eligible),
            "exact_feature_token_count": sum(exact_counts.values()),
            "exact_feature_type_count": len(exact_counts),
            "ed1_feature_token_count": sum(ed1_counts.values()),
            "ed1_feature_type_count": len(ed1_counts),
        }
        for field, expected in expected_values.items():
            observed: Any = row[field]
            if isinstance(expected, int):
                observed = int(observed)
            if observed != expected:
                raise AssertionError(f"paragraph atlas mismatch {paragraph.paragraph_id}/{field}")
        expected_raw = rebuilt["target_raw_memberships"][paragraph.paragraph_id] & MASK_TARGETS
        expected_stable = rebuilt["target_stable_memberships"][paragraph.paragraph_id] & MASK_TARGETS
        decode = lambda value: frozenset() if value in {"", "NONE"} else frozenset(value.split("|"))
        if decode(row["raw_target_memberships"]) != expected_raw or decode(row["stable_target_memberships"]) != expected_stable:
            raise AssertionError(f"paragraph target-membership mismatch: {paragraph.paragraph_id}")
    checks.append("all_665_strict_paragraphs_masks_features_and_memberships_reproduced")
    p0186 = paragraph_index["G807-P0186"]
    if (p0186["page"], int(p0186["source_line_count"]),
            int(p0186["common_masked_line_count"]), int(p0186["surviving_line_count"]),
            int(p0186["basis_nonempty_retained_lines"])) != ("f49v", 25, 1, 24, 22):
        raise AssertionError("P0186 physical-survivor versus nonempty-line regression")
    checks.append("p0186_two_empty_surviving_lines_kept_physical_but_not_nonempty")
    score_path = ART / "GDT807_PAIR_SCORE_SUMMARY.tsv"
    if not score_path.is_file():
        raise AssertionError("pair score summary artifact absent")
    score_rows = read_tsv(score_path)
    score_index = {(row["pair_id"], row["view_id"]): row for row in score_rows if "pair_id" in row and "view_id" in row}
    expected_keys = {(pair_id, view) for pair_id in rebuilt["pair_results"] for view in VIEWS}
    if set(score_index) != expected_keys:
        raise AssertionError(f"pair/view summary key drift in {score_path.name}")
    for pair_id, pair in rebuilt["pair_results"].items():
        for view, expected in pair["views"].items():
            row = score_index[(pair_id, view)]
            aliases = {"positive_paragraphs": ("positive_paragraphs", "positive_n", "a_paragraphs"),
                       "negative_paragraphs": ("negative_paragraphs", "negative_n", "b_paragraphs"),
                       "positive_folios": ("positive_folios", "positive_folio_n", "a_folios"),
                       "negative_folios": ("negative_folios", "negative_folio_n", "b_folios")}
            for name, options in aliases.items():
                if int(find_column(row, *options)) != expected[name]:
                    raise AssertionError(f"{pair_id}/{view} {name} mismatch")
            if not close_float(parse_float(find_column(row, "auc", "auc_ties_half", "held_folio_auc", "lofo_auc")), expected["auc"]):
                raise AssertionError(f"{pair_id}/{view} AUC mismatch")
            if not close_float(parse_float(find_column(row, "balanced_accuracy", "balanced_accuracy_zero_ties_half", "held_folio_balanced_accuracy", "ba")), expected["balanced_accuracy"]):
                raise AssertionError(f"{pair_id}/{view} BA mismatch")
    checks.append("all_12_pair_view_scores_independently_reproduced")

    fold_path = ART / "GDT807_FOLD_VOCABULARY_AUDIT.tsv"
    prediction_path = ART / "GDT807_HELD_FOLIO_PREDICTIONS.tsv"
    if not fold_path.is_file() or not prediction_path.is_file():
        raise AssertionError("direct fold/prediction audit artifacts absent")
    fold_rows = read_tsv(fold_path)
    fold_index = {
        (row["pair_id"], row["view_id"], row["held_physical_folio"]): row
        for row in fold_rows if row.get("context") == "TARGET"
    }
    expected_fold_count = sum(
        len(view["folds"])
        for pair in rebuilt["pair_results"].values() for view in pair["views"].values()
    )
    if len(fold_index) != expected_fold_count:
        raise AssertionError("direct fold-vocabulary audit capacity drift")
    expected_predictions: dict[tuple[str, str, str], dict[str, Any]] = {}
    for pair_id, pair in rebuilt["pair_results"].items():
        for view_id, view in pair["views"].items():
            for fold in view["folds"]:
                row = fold_index[(pair_id, view_id, fold["held_physical_folio"])]
                if (int(row["train_paragraphs"]) != fold["training_paragraphs"]
                        or int(row["test_paragraphs"]) != fold["test_paragraphs"]
                        or int(row["training_vocabulary_types"]) != fold["vocabulary_size"]
                        or truth(row["fold_scoreable"]) != fold["scoreable"]):
                    raise AssertionError(
                        f"fold-vocabulary mismatch {pair_id}/{view_id}/{fold['held_physical_folio']}"
                    )
            for prediction in view["predictions"]:
                expected_predictions[(pair_id, view_id, prediction["paragraph_id"])] = prediction
    prediction_rows = read_tsv(prediction_path)
    prediction_index = {
        (row["pair_id"], row["view_id"], row["paragraph_id"]): row
        for row in prediction_rows if row.get("context") == "TARGET"
    }
    if set(prediction_index) != set(expected_predictions):
        raise AssertionError("held-folio prediction key/capacity drift")
    for key, expected in expected_predictions.items():
        row = prediction_index[key]
        if (int(row["true_label"]) != expected["label"]
                or int(row["test_tokens_in_fold_vocabulary"]) != expected["in_vocabulary_tokens"]
                or int(row["training_vocabulary_types"]) != expected["vocabulary_size"]
                or not close_float(parse_float(row["score"]), expected["score"])):
            raise AssertionError(f"held-folio prediction mismatch: {key}")
    checks.append("training_surface_in_two_paragraphs_gate_and_all_direct_predictions_reproduced")
    null_path = ART / "GDT807_CYCLIC_EXCHANGE_NULL.tsv"
    null_rows = read_tsv(null_path)
    if len(null_rows) != 144:
        raise AssertionError(f"cyclic-null row count drift: {len(null_rows)}")
    null_index = {(row["pair_id"], row["view_id"], int(row["offset"])): row for row in null_rows}
    if len(null_index) != 144:
        raise AssertionError("cyclic-null key uniqueness drift")
    for pair_id, pair in rebuilt["pair_results"].items():
        for view, expected_rows in pair["cyclic_null_by_view"].items():
            for expected in expected_rows:
                row = null_index[(pair_id, view, expected["offset"])]
                if not close_float(parse_float(find_column(row, "auc", "auc_ties_half", "held_folio_auc", "null_auc")), expected["auc"]):
                    raise AssertionError(f"{pair_id}/{view} cyclic offset {expected['offset']} AUC mismatch")
                identity = find_column(row, "identity_membership_sets", "identity_assignments")
                if int(row["moved_membership_sets"]) != expected["moved_membership_sets"] or int(identity) != expected["identity_assignments"]:
                    raise AssertionError(f"{pair_id}/{view} cyclic moved/identity mismatch")
    checks.append("all_144_cyclic_exchange_scores_independently_reproduced")
    k24_path = ART / "GDT807_K24_PSEUDO_PAIR_SCORES.tsv"
    k24_spec_path = ART / "GDT807_K24_PSEUDO_PAIR_SPECS.tsv"
    k24_rows = read_tsv(k24_path)
    k24_spec_rows = read_tsv(k24_spec_path)
    if len(k24_rows) != 72:
        raise AssertionError(f"K24 row count drift: {len(k24_rows)}")
    spec_by_id = {row["pseudo_pair_id"]: row for row in k24_spec_rows}
    k24_index = {
        (find_column(row, "pair_id", "target_pair_id"),
         int(re.search(r"K(\d+)$", row["pseudo_pair_id"]).group(1))): row
        for row in k24_rows
    }
    if len(k24_index) != 72:
        raise AssertionError("K24 key uniqueness drift")
    for pair_id, pair in rebuilt["pair_results"].items():
        for expected in pair["k24"]:
            row = k24_index[(pair_id, expected["pseudo_pair_index"])]
            spec_row = spec_by_id[row["pseudo_pair_id"]]
            if find_column(row, "positive_control", "positive_control_surface", "control_a", "positive_surface") != expected["positive_control"] or find_column(row, "negative_control", "negative_control_surface", "control_b", "negative_surface") != expected["negative_control"]:
                raise AssertionError(f"{pair_id} K24 surface construction mismatch")
            if int(spec_row["surface_pair_multiplicity"]) not in {1, 2}:
                raise AssertionError(f"{pair_id} K24 multiplicity field malformed")
            if truth(find_column(row, "scoreable", "model_scoreable")) != expected["scoreable"]:
                raise AssertionError(f"{pair_id} K24 scoreable mismatch")
            if not close_float(parse_float(find_column(row, "auc", "auc_ties_half", "held_folio_auc", "control_auc")), expected["auc"]):
                raise AssertionError(f"{pair_id} K24 AUC mismatch")
            for leak in ("residual_defining_tokens", "residual_defining_lines"):
                if leak in row and int(row[leak]) != 0:
                    raise AssertionError(f"{pair_id} K24 defining-surface leakage")
    checks.append("all_72_k24_scores_and_self_surface_masks_reproduced")
    for pair_id, expected_unique in (("G807-P01", 22), ("G807-P02", 24), ("G807-P03", 24)):
        observed_unique = len({row["surface_pair_key"] for row in k24_spec_rows if row["target_pair_id"] == pair_id})
        if observed_unique != expected_unique:
            raise AssertionError(f"{pair_id} K24 unique-pair disclosure mismatch")
    checks.append("k24_nonindependence_disclosed_22_24_24_unique_pairs")
    removal_path = ART / "GDT807_FOLIO_REMOVAL_DIAGNOSTICS.tsv"
    removal_rows = read_tsv(removal_path)
    removal_index = {(row["pair_id"], find_column(row, "removed_physical_folio", "omitted_physical_folio", "omitted_folio")): row for row in removal_rows}
    expected_count = sum(len(pair["folio_removals"]) for pair in rebuilt["pair_results"].values())
    if len(removal_index) != expected_count:
        raise AssertionError("folio-removal capacity drift")
    for pair_id, pair in rebuilt["pair_results"].items():
        for expected in pair["folio_removals"]:
            row = removal_index[(pair_id, expected["omitted_physical_folio"])]
            if truth(find_column(row, "scoreable", "removal_scoreable")) != expected["scoreable"] or not close_float(parse_float(find_column(row, "auc", "auc_ties_half", "held_folio_auc", "remaining_auc")), expected["auc"]):
                raise AssertionError(f"{pair_id} removal mismatch for {expected['omitted_physical_folio']}")
    checks.append("single_folio_removals_independently_reproduced")

    landmark_path = ART / "GDT807_LANDMARKS.tsv"
    if not landmark_path.is_file():
        raise AssertionError("landmark audit artifact absent")
    landmark_rows = read_tsv(landmark_path)
    landmark_index = {(row["pair_id"], row["surface"]): row for row in landmark_rows}
    expected_landmarks = {
        (row["pair_id"], row["surface"]): row for row in rebuilt["landmarks"]
    }
    if set(landmark_index) != set(expected_landmarks):
        raise AssertionError("landmark full-vocabulary key drift")
    for key, expected in expected_landmarks.items():
        row = landmark_index[key]
        for field in (
            "positive_token_count", "negative_token_count",
            "eligible_paragraphs_with_surface", "eligible_folios_with_surface",
            "scoreable_folds", "same_direction_folds", "zero_direction_folds",
        ):
            if int(row[field]) != expected[field]:
                raise AssertionError(f"landmark paragraph/fold counter mismatch {key}/{field}")
        for field in ("full_training_log_odds", "same_direction_rate"):
            if not close_float(parse_float(row[field]), expected[field]):
                raise AssertionError(f"landmark score mismatch {key}/{field}")
        if row["full_direction"] != expected["full_direction"] or row["landmark_status"] != expected["landmark_status"]:
            raise AssertionError(f"landmark direction/status mismatch: {key}")
        if row.get("semantic_credit") != "0" or row.get("structural_label_only") != "1":
            raise AssertionError(f"landmark exceeded structural claim ceiling: {key}")
    checks.append("landmark_paragraph_presence_and_fold_direction_reproduced")

    marker_path = ART / "GDT807_POSITIONAL_MARKER_OVERLAY.tsv"
    if not marker_path.is_file():
        raise AssertionError("positional marker overlay absent")
    marker_rows = read_tsv(marker_path)
    marker_index = {
        (row["pair_id"], row["view_id"], row["marker_surface"]): row
        for row in marker_rows
    }
    expected_markers = {
        (row["pair_id"], row["view_id"], row["marker_surface"]): row
        for row in rebuilt["positional_overlay"]
    }
    if set(marker_index) != set(expected_markers) or len(marker_index) != 180:
        raise AssertionError("positional overlay pair/view/whole capacity drift")
    marker_count_fields = (
        "source_line_initial_events", "strict_paragraph_events",
        "common_masked_line_events", "common_surviving_line_events",
        "eligible_exclusive_pair_events", "positive_paragraphs_with_marker",
        "negative_paragraphs_with_marker", "eligible_paragraphs_with_marker",
        "eligible_folios_with_marker",
    )
    for key, expected in expected_markers.items():
        row = marker_index[key]
        if any(int(row[field]) != expected[field] for field in marker_count_fields):
            raise AssertionError(f"positional marker counter mismatch: {key}")
        if any(row[field] != "0" for field in ("selection_credit", "semantic_credit", "german_renderer_credit")):
            raise AssertionError(f"positional marker received forbidden credit: {key}")
    low_counts = {
        surface: next(row["source_line_initial_events"] for row in rebuilt["positional_overlay"] if row["marker_surface"] == surface)
        for surface in ("ykar", "yteedy", "qotor", "dchey")
    }
    if low_counts != {"ykar": 5, "yteedy": 5, "qotor": 11, "dchey": 9}:
        raise AssertionError(f"stable line-initial low-control census drift: {low_counts}")
    checks.append("positional_overlay_including_low_stable_initial_5_5_11_9_reproduced")
    decision_path = ART / "GDT807_STRUCTURAL_CARD.tsv"
    decisions = read_tsv(decision_path)
    decision_index = {row["pair_id"]: row for row in decisions if "pair_id" in row}
    if set(decision_index) != set(rebuilt["pair_results"]):
        raise AssertionError("decision table pair universe drift")
    for pair_id, expected in rebuilt["pair_results"].items():
        row = decision_index[pair_id]
        if find_column(row, "decision", "gdt807_decision") != expected["decision"]:
            raise AssertionError(f"{pair_id} decision mismatch")
        raw = expected["views"]["RAW_PAIRED"]
        stable = expected["views"]["STABLE_PAIRED"]
        stable_ed1 = expected["views"]["STABLE_ED1_SENSITIVITY"]
        exact_gate_expectations = {
            "gate_stable_capacity_24_paragraphs_16_folios_each": expected["gates"]["stable_capacity"],
            "gate_raw_paired_auc_ge_0_60": bool(raw["scoreable"] and raw["auc"] >= .60),
            "gate_stable_paired_auc_ge_0_60": bool(stable["scoreable"] and stable["auc"] >= .60),
            "gate_stable_ed1_auc_ge_0_60": bool(stable_ed1["scoreable"] and stable_ed1["auc"] >= .60),
            "gate_stable_paired_balanced_accuracy_ge_0_60": bool(
                stable["scoreable"] and stable["balanced_accuracy"] >= .60
            ),
            "gate_cyclic_delta_ge_0_03_rank_le_3": expected["gates"]["cyclic_exchange"],
            "gate_k24_n_ge_18_rank_le_6": expected["gates"]["k24_specificity"],
            "gate_removal_success_rate_ge_0_80": expected["gates"]["single_folio_removal"],
            "fallback_raw_stable_auc_and_stable_ba_ge_0_60": (
                raw["scoreable"] and stable["scoreable"]
                and raw["auc"] >= .60 and stable["auc"] >= .60
                and stable["balanced_accuracy"] >= .60
            ),
        }
        for gate, value in exact_gate_expectations.items():
            if gate not in row or truth(row[gate]) != value:
                raise AssertionError(f"{pair_id} gate mismatch/missing: {gate}")
        if "gate_stable_ed1_balanced_accuracy_ge_0_60" in row:
            raise AssertionError("obsolete STABLE_ED1 balanced-accuracy robust gate is still published")
        if int(row["k24_unique_surface_pairs"]) != expected["k24_unique_surface_pairs"]:
            raise AssertionError(f"{pair_id} K24 unique-pair structural-card mismatch")
        for field in ("semantic_credit", "renderer_license", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit"):
            if field in row and row[field] not in {"0", "NONE", "NO", "ZERO", "FALSE", "False"}:
                raise AssertionError(f"forbidden credit: {pair_id}/{field}={row[field]}")
    checks.append("three_pair_decisions_and_zero_credit_ceiling")
    rivals = read_tsv(RIVAL_SPECS)
    if len(rivals) != 7 or any(row["score_credit"] != "0" or row["semantic_credit"] != "0" or row["renderer_credit"] != "0" for row in rivals):
        raise AssertionError("concrete-rival zero-credit drift")
    positional = read_tsv(POSITIONAL_SPECS)
    if len(positional) != 15 or any(row["selection_credit"] != "0" or row["semantic_credit"] != "0" or row["german_renderer_credit"] != "0" for row in positional):
        raise AssertionError("positional zero-credit drift")
    checks.append("registered_overlays_zero_credit")

    packet_path = ART / "GDT807_GDT388_PARAGRAPH_EDGE_PACKET.tsv"
    intake_path = ART / "GDT807_GDT388_EDGE_INTAKE.json"
    if not packet_path.is_file() or not intake_path.is_file():
        raise AssertionError("GDT388 packet/intake artifacts absent")
    packet_rows = read_tsv(packet_path)
    expected_edges = sum(
        len(rebuilt["target_stable_memberships"][paragraph.paragraph_id] & MASK_TARGETS)
        for paragraph in rebuilt["paragraphs"]
        if rebuilt["exact_remainders"][paragraph.paragraph_id].eligible
    )
    if len(packet_rows) != expected_edges:
        raise AssertionError(f"GDT388 edge capacity mismatch: {len(packet_rows)} != {expected_edges}")
    completed = subprocess.run(
        [str(VMANUS_EXP), "check-edge-packet", str(packet_path)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode != 1 or completed.stderr:
        raise AssertionError("GDT388 packet did not fail closed with registered return contract")
    live_intake = json.loads(completed.stdout)
    stored_intake = json.loads(intake_path.read_text(encoding="utf-8"))
    if live_intake != stored_intake:
        raise AssertionError("stored GDT388 intake is not independently replayable")
    if (live_intake.get("status") != "INVALID_PACKET"
            or live_intake.get("eligible_edges") != 0
            or live_intake.get("score_ready") is not False):
        raise AssertionError("GDT388 edge packet unexpectedly score-ready")
    checks.append("gdt388_packet_independently_replayed_and_failed_closed")

    selector_fields = {
        "page", "source_selector", "physical_folio", "locus", "start_locus",
        "end_locus", "pivot_locus", "target_locus",
    }
    for path in sorted(ART.glob("*.tsv")):
        rows = read_tsv(path)
        for row in rows:
            for field in selector_fields & set(row):
                if row[field].startswith("f84"):
                    raise AssertionError(f"sealed selector in output {path.name}/{field}")
    checks.append("all_tsv_selector_fields_sealed_f84_free")
    return checks


def manifest_input_checks() -> list[str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("experiment_id") != "GDT807" or manifest.get("sealed_data") != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise AssertionError("manifest identity/sealed gate drift")
    seen: set[str] = set()
    for item in manifest.get("inputs", []):
        path = ROOT / item["path"]
        if item["path"] in seen or not path.is_file():
            raise AssertionError(f"manifest input missing/duplicated: {item['path']}")
        seen.add(item["path"])
        if path.resolve() in MIXED_PATHS:
            completed = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", item["path"]], cwd=ROOT, check=False)
            if completed.returncode != 0:
                raise AssertionError(f"mixed input differs from HEAD: {item['path']}")
        elif sha256(path) != item["sha256"]:
            raise AssertionError(f"manifest input hash mismatch: {item['path']}")
    required = {rel(path) for path in (ALLOWLIST, LINES_RAW, CROSS_RAW, TOKENS_RAW, GDT805_ATLAS,
                GDT800_OCCURRENCES, GDT804_POOLS, GDT757_WHOLES, GDT757_OCCURRENCES,
                GDT757_CONTROLS, PAIR_SPECS, VIEW_SPECS, POSITIONAL_SPECS, RIVAL_SPECS)}
    if not required <= seen:
        raise AssertionError(f"manifest misses locks: {sorted(required - seen)}")
    if subprocess.run(["git", "merge-base", "--is-ancestor", EXPECTED_AMENDMENT, "HEAD"], cwd=ROOT, check=False).returncode != 0:
        raise AssertionError("final GDT807 scoring amendment is not in HEAD history")
    return ["manifest_identity_and_sealed_gate", "all_manifest_input_hashes_or_guarded_tracked_locks", "final_scoring_amendment_ancestor"]


def builder_process_active() -> bool:
    completed = subprocess.run(["ps", "-eo", "pid=,args="], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE)
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        pid_text, _, args = stripped.partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid != os.getpid() and "gdt807_target_masked_paragraph_exchange_codebook/src/run.py" in args:
            return True
    return False


def artifact_snapshot() -> dict[str, tuple[int, int, str]]:
    return {path.name: (path.stat().st_size, path.stat().st_mtime_ns, sha256(path))
            for path in sorted(ART.glob("*")) if path.is_file() and path.name != "VALIDATION.json"}


def replay_builder(skip: bool) -> list[str]:
    if skip:
        return ["builder_replay_explicitly_skipped"]
    official = {path.name: sha256(path) for path in ART.glob("*") if path.is_file() and path.name not in {"VALIDATION.json", "README.md", "RESULT.json"}}
    official_result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    # Keep the disposable replay under the repository so the canonical GDT388
    # path guard accepts its packet; TemporaryDirectory removes it on exit.
    with tempfile.TemporaryDirectory(prefix=".validator-replay-", dir=EXP) as tmp:
        replay_dir = Path(tmp) / "artifacts"
        completed = subprocess.run(["python3", str(RUN), "--output-dir", str(replay_dir)], cwd=ROOT,
                                   check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode != 0:
            raise AssertionError("builder replay failed: " + (completed.stderr or completed.stdout)[-2000:])
        replayed = {path.name: sha256(path) for path in replay_dir.glob("*") if path.is_file() and path.name not in {"VALIDATION.json", "README.md", "RESULT.json"}}
        if replayed != official:
            missing, extra = sorted(set(official) - set(replayed)), sorted(set(replayed) - set(official))
            changed = sorted(name for name in set(official) & set(replayed) if official[name] != replayed[name])
            raise AssertionError(f"builder replay not byte-identical: missing={missing} extra={extra} changed={changed}")
        replay_result = json.loads((replay_dir / "RESULT.json").read_text(encoding="utf-8"))
        # RESULT records its output location: normalize only that intentional
        # default-vs-temp path difference, then demand semantic identity.
        def normalize_result(value: dict[str, Any]) -> dict[str, Any]:
            normalized = json.loads(json.dumps(value))
            normalized["outputs"] = {
                Path(name).name: digest for name, digest in normalized.get("outputs", {}).items()
            }
            return normalized
        if normalize_result(replay_result) != normalize_result(official_result):
            raise AssertionError("builder replay RESULT differs beyond normalized output paths")
    return ["builder_replay_all_nonselflocating_artifacts_byte_identical",
            "builder_replay_result_semantically_identical_after_path_normalization"]


def compact_summary(rebuilt: Mapping[str, Any]) -> dict[str, Any]:
    return {pair_id: {"decision": pair["decision"],
                      "raw_auc": pair["views"]["RAW_PAIRED"]["auc"],
                      "stable_auc": pair["views"]["STABLE_PAIRED"]["auc"],
                      "stable_balanced_accuracy": pair["views"]["STABLE_PAIRED"]["balanced_accuracy"],
                      "stable_ed1_auc": pair["views"]["STABLE_ED1_SENSITIVITY"]["auc"],
                      "stable_ed1_balanced_accuracy": pair["views"]["STABLE_ED1_SENSITIVITY"]["balanced_accuracy"],
                      "null_median_auc": pair["null_median_auc"], "null_rank_of_13": pair["null_target_rank_of_13_ties_against"],
                      "k24_scoreable": pair["k24_scoreable"], "k24_rank": pair["k24_target_rank_ties_against"],
                      "removal_scoreable": pair["folio_removal_scoreable"], "removal_successes": pair["folio_removal_successes"],
                      "removal_success_fraction": pair["folio_removal_success_fraction"], "gates": pair["gates"]}
            for pair_id, pair in rebuilt["pair_results"].items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-replay", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    if builder_process_active():
        raise SystemExit("GDT807 builder active; refusing moving artifacts")
    first = artifact_snapshot()
    checks = manifest_input_checks()
    rebuilt = reconstruct()
    checks.extend(compare_outputs(rebuilt))
    checks.extend(replay_builder(args.skip_replay))
    if first != artifact_snapshot():
        raise AssertionError("artifact tree changed during validation")
    checks.append("artifact_tree_stable_during_validation")
    payload = {"experiment": "GDT807", "status": "PASS",
               "validator_independent_of_builder_import": True,
               "mixed_sources_accessed_only_by_guarded_query": True,
               "sealed_f84_rows_materialized": 0, "checks_passed": checks,
               "check_count": len(checks),
               "source_census": {"strict_paragraphs": len(rebuilt["paragraphs"]),
                    "included_lines": sum(len(p.lines) for p in rebuilt["paragraphs"]),
                    "included_tokens": sum(len(line.tokens) for p in rebuilt["paragraphs"] for line in p.lines),
                    "outside_lines": len(rebuilt["outside_lines"]),
                    "outside_tokens": sum(len(line.tokens) for line in rebuilt["outside_lines"])},
               "k12_membership_population": "GDT800_EXACT_L_TERMINAL_OCCURRENCE_UNIVERSE_ONLY",
               "pair_summary": compact_summary(rebuilt),
               "claim_ceiling": "structural target-masked paragraph ecology only; no meaning, lexeme, plaintext, renderer licence, component, ingredient, process, quality, plant, disease, patient, measure or language"}
    if not args.no_write:
        temporary = VALIDATION.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(VALIDATION)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
