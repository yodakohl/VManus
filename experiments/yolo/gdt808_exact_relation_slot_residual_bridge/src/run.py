#!/usr/bin/env python3
"""Official GDT808 exact-relation / slot-residual builder.

Mixed transcription TSVs are accessed only through the guarded dispatcher.
Every result is structural and has zero semantic or renderer credit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
RUN, METHOD, PREREG, MANIFEST = SRC / "run.py", BASE / "METHOD.md", BASE / "PREREGISTRATION.md", BASE / "experiment.json"
ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
LINES_RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
G759_SPANS = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G768_ANCHORS = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/ANCHOR_404_OCCURRENCE_ATLAS.tsv"
G757_OPENERS = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv"
VMANUS_EXP = ROOT / "vmanus-exp"
GUARDED_TOOL, EDGE_TOOL = ROOT / "tools/guarded_tsv_query.py", ROOT / "tools/relation_edge_intake.py"
CONTROL_SPECS, CORE_SPECS = SRC / "CONTROL_SPECS.tsv", SRC / "CORE_CARRIER_SPECS.tsv"
FEATURE_SPECS, HISTORICAL_SPECS = SRC / "FEATURE_DECK_SPECS.tsv", SRC / "HISTORICAL_TOPOLOGY_SPECS.tsv"
IMPLEMENTATION_SPECS, QUARANTINE_SPECS = SRC / "IMPLEMENTATION_SPECS.tsv", SRC / "QUARANTINE_SPECS.tsv"
MODEL_SPECS, RIVAL_DECISION_SPECS = SRC / "RELATION_MODEL_SPECS.tsv", SRC / "RIVAL_DECISION_SPECS.tsv"
SEMANTIC_RIVAL_SPECS = SRC / "SEMANTIC_RIVAL_SPECS.tsv"

TAILS = ("eody", "eol", "edy", "ol")
ALPHA = 0.5
EXPECTED = {"selectors": 179, "source_lines": 4137, "source_tokens": 32339,
            "strict_paragraphs": 665, "strict_lines": 3807, "strict_tokens": 31938,
            "outside_lines": 330, "outside_tokens": 401, "core_events": 1777,
            "all28_events": 2208}
EXPECTED_CORE_TAILS = {"ol": 641, "eol": 273, "edy": 715, "eody": 148}
EXPECTED_ALL28_TAILS = {"ol": 759, "eol": 332, "edy": 939, "eody": 178}
OUTPUT_NAMES = (
    "SOURCE_LOCK.tsv", "GDT808_IMPLEMENTATION_CLARIFICATIONS.tsv", "GDT808_GUARDED_QUERY_STATS.tsv",
    "GDT808_SOURCE_CENSUS.tsv", "GDT808_RAW35_ALL28_CORE13_CARRIER_CENSUS.tsv",
    "GDT808_Q152_EXACT_QUARANTINE.tsv", "GDT808_1777_CORE_EVENT_ATLAS.tsv",
    "GDT808_FEATURE_DECK_CAPACITY.tsv", "GDT808_COMPONENT_HELD_FOLDS.tsv",
    "GDT808_HELD_PREDICTIONS.tsv", "GDT808_DECK_SCORE_SUMMARY.tsv",
    "GDT808_CONDITIONAL_CONCORDANCE.tsv", "GDT808_POSITION_MASK_SLOT_ABLATIONS.tsv",
    "GDT808_CARRIER_DIRECTION_DIAGNOSTICS.tsv", "GDT808_NULL_STRATUM_AUDIT.tsv",
    "GDT808_NULL_SCORES.tsv", "GDT808_ALL28_SENSITIVITY.tsv", "GDT808_ED1_SENSITIVITY.tsv",
    "GDT808_THIN_KOL_TAL.tsv", "GDT808_LEARNED_CHEOL_OTAL.tsv",
    "GDT808_HISTORICAL_RIVAL_CARD.tsv", "GDT808_GDT388_RELATION_PACKET.tsv",
    "GDT808_GDT388_EDGE_INTAKE.json", "GDT808_STRUCTURAL_CARD.tsv", "RESULT.json")
EDGE_FIELDS = ("edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
               "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
               "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
               "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
               "source_aware_localizer", "relation_reviewer", "relation_confidence", "ambiguity_state",
               "formal_access_state", "fold_assignment", "eligibility_status")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str] | None = None) -> None:
    material = list(rows)
    if fields is None:
        if not material:
            raise RuntimeError(f"empty TSV without schema: {path.name}")
        fields = tuple(material[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in material:
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


def pipe(values: Iterable[Any]) -> str:
    material = [str(value) for value in values if str(value)]
    return "|".join(material) if material else "NONE"


def selector_sort_key(value: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", value)
    return ((int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), value)
            if match else (10**9, 9, 9, value))


def physical_folio(selector: str) -> str:
    match = re.match(r"^(f[0-9]+[rv])", selector)
    if not match:
        raise RuntimeError(f"cannot normalize physical folio: {selector}")
    return match.group(1)


def leaf_folio(selector: str) -> str:
    match = re.match(r"^(f[0-9]+)", selector)
    if not match:
        raise RuntimeError(f"cannot normalize leaf folio: {selector}")
    return match.group(1)


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
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError(f"guard statistics missing: {query_id}")
    stats = json.loads(stat_lines[0][12:])
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    assert_no_sealed(rows)
    return rows, {"query_id": query_id, "source_path": rel(path), "selector_column": "page",
                  "allowed_value_count": len(pages), "output_columns": ",".join(columns),
                  "forbidden_prefixes": "f84|f84r", "selected_rows": int(stats["selected"]),
                  "skipped_forbidden_rows": int(stats["skipped_forbidden"]),
                  "skipped_not_allowed_rows": int(stats["skipped_not_allowed"]),
                  "query_returncode": completed.returncode}


def parse_surface(surface: str) -> tuple[str, str] | None:
    for tail in TAILS:
        if surface.endswith(tail) and len(surface) > len(tail):
            return surface[:-len(tail)], tail
    return None


def lcs_table(left: Sequence[str], right: Sequence[str]) -> list[list[int]]:
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(len(left) - 1, -1, -1):
        for j in range(len(right) - 1, -1, -1):
            table[i][j] = 1 + table[i + 1][j + 1] if left[i] == right[j] else max(table[i + 1][j], table[i][j + 1])
    return table


def exact_lcs_alignment(reference: Sequence[str], alternate: Sequence[str], index: int) -> tuple[str, int | str, int]:
    suffix, optimum = lcs_table(reference, alternate), lcs_table(reference, alternate)[0][0]
    prefix = [[0] * (len(alternate) + 1) for _ in range(len(reference) + 1)]
    for i, left in enumerate(reference):
        for j, right in enumerate(alternate):
            prefix[i + 1][j + 1] = 1 + prefix[i][j] if left == right else max(prefix[i][j + 1], prefix[i + 1][j])
    partners = [j for j, value in enumerate(alternate)
                if reference[index] == value and prefix[index][j] + 1 + suffix[index + 1][j + 1] == optimum]
    without = list(reference[:index]) + list(reference[index + 1:])
    forced = lcs_table(without, alternate)[0][0] < optimum
    if forced and len(partners) == 1:
        return "UNIQUE_FORCED_EXACT", partners[0] + 1, optimum
    if forced:
        return "FORCED_DUPLICATE_EXACT", "NA", optimum
    return ("OPTIONAL_OR_DUPLICATE_EXACT" if partners else "NO_EXACT_ALIGNMENT"), "NA", optimum


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + int(a != b)))
        previous = current
    return previous[-1]


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
    stable: tuple[int, ...]
    cross: dict[str, str]


@dataclass
class Paragraph:
    paragraph_id: str
    ordinal: int
    page_ordinal: int
    page: str
    folio: str
    section: str
    language: str
    hand: str
    lines: tuple[Line, ...]


@dataclass
class Event:
    event_id: str
    carrier: str
    tail: str
    axis: str
    label: int
    surface: str
    page: str
    folio: str
    locus: str
    line_number: int
    token_index: int
    line: Line
    paragraph: Paragraph
    paragraph_line_index: int
    own_surfaces: tuple[str, ...]
    it2a_ordinal: int | str
    rf1b_ordinal: int | str
    features: dict[str, frozenset[str]] = field(default_factory=dict)
    features_ed1: dict[str, frozenset[str]] = field(default_factory=dict)
    targetfree_line_length_bin: int = 0


def load_corpus() -> tuple[list[Line], list[Paragraph], dict[str, Paragraph], list[dict[str, Any]], list[dict[str, str]]]:
    pages = [row["page"] for row in read_tsv(ALLOWLIST)]
    if len(pages) != 179 or len(set(pages)) != 179 or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list drift or sealed selector")
    line_rows, line_stats = guarded_query(LINES_RAW, pages,
        ("page", "locus", "line_number", "section", "language", "hand", "paragraph_start", "paragraph_end", "token_count", "eva_clean"), "ZL3B_LINES_179")
    token_rows, token_stats = guarded_query(TOKENS_RAW, pages,
        ("page", "locus", "token_index", "eva", "section", "language", "hand"), "ZL3B_TOKENS_179")
    cross_rows, cross_stats = guarded_query(CROSS_RAW, pages,
        ("page", "locus", "all_three_present", "all_present_exact", "zl3b_clean", "it2a_clean", "rf1b_clean"), "CROSS_READER_LINES_179")
    if (len(line_rows), len(token_rows), len(cross_rows)) != (4137, 32339, 4137):
        raise RuntimeError("guarded source cardinality drift")
    line_map, cross_map = ({(row["page"], row["locus"]): row for row in rows} for rows in (line_rows, cross_rows))
    if len(line_map) != len(line_rows) or set(line_map) != set(cross_map):
        raise RuntimeError("line/cross key drift")
    token_map: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        token_map[(row["page"], row["locus"])].append(row)
    for key, values in token_map.items():
        values.sort(key=lambda row: int(row["token_index"]))
        if [int(row["token_index"]) for row in values] != list(range(1, len(values) + 1)):
            raise RuntimeError(f"noncontiguous token indexes: {key}")
    lines: list[Line] = []
    for row in sorted(line_rows, key=lambda value: (selector_sort_key(value["page"]), int(value["line_number"]))):
        key, cross = (row["page"], row["locus"]), cross_map[(row["page"], row["locus"])]
        tokens = tuple(value["eva"] for value in token_map.get(key, []))
        if " ".join(tokens) != row["eva_clean"] or row["eva_clean"] != cross["zl3b_clean"] or len(tokens) != int(row["token_count"]):
            raise RuntimeError(f"line/token/cross parity drift at {row['locus']}")
        ranks: Counter[str] = Counter()
        readers = [cross[name].split() for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        stable: list[int] = []
        for surface in tokens:
            ranks[surface] += 1
            stable.append(int(ranks[surface] <= min(reader.count(surface) for reader in readers)))
        lines.append(Line(row["page"], row["locus"], int(row["line_number"]), row["section"], row["language"], row["hand"],
                          row["paragraph_start"] == "1", row["paragraph_end"] == "1", tokens, tuple(stable), cross))
    paragraphs, outside = [], []
    by_page: defaultdict[str, list[Line]] = defaultdict(list)
    for line in lines:
        by_page[line.page].append(line)
    ordinal = 0
    for page in sorted(by_page, key=selector_sort_key):
        current: list[Line] | None = None
        page_ordinal = 0
        for line in sorted(by_page[page], key=lambda value: value.number):
            if line.paragraph_start:
                if current is not None:
                    raise RuntimeError(f"nested paragraph at {line.locus}")
                current = []
            if current is None:
                outside.append(line)
                if line.paragraph_end:
                    raise RuntimeError(f"orphan paragraph end at {line.locus}")
                continue
            current.append(line)
            if line.paragraph_end:
                ordinal, page_ordinal = ordinal + 1, page_ordinal + 1
                metadata = {(value.section, value.language, value.hand) for value in current}
                if len(metadata) != 1:
                    raise RuntimeError(f"paragraph metadata drift: {page}:{page_ordinal}")
                section, language, hand = next(iter(metadata))
                paragraphs.append(Paragraph(f"G808-P{ordinal:04d}", ordinal, page_ordinal, page, physical_folio(page), section, language, hand, tuple(current)))
                current = None
        if current is not None:
            raise RuntimeError(f"unclosed paragraph at {page}")
    actual = {"strict_paragraphs": len(paragraphs), "strict_lines": sum(len(p.lines) for p in paragraphs),
              "strict_tokens": sum(len(line.tokens) for p in paragraphs for line in p.lines), "outside_lines": len(outside),
              "outside_tokens": sum(len(line.tokens) for line in outside)}
    for name, value in actual.items():
        if value != EXPECTED[name]:
            raise RuntimeError(f"strict corpus drift: {name}={value} expected={EXPECTED[name]}")
    paragraph_by_locus = {line.locus: paragraph for paragraph in paragraphs for line in paragraph.lines}
    if len(paragraph_by_locus) != EXPECTED["strict_lines"]:
        raise RuntimeError("duplicate strict locus")
    return lines, paragraphs, paragraph_by_locus, [line_stats, token_stats, cross_stats], token_rows


def spec_sets() -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    lookup = {row["identifier"]: row["surfaces_or_rule"].split("|") for row in read_tsv(QUARANTINE_SPECS)}
    values = tuple(lookup[name] for name in ("RAW35", "ALL28", "CORE13", "THIN9", "OVERLAP6"))
    if tuple(map(len, values)) != (35, 28, 13, 9, 6) or values[2] != [row["carrier"] for row in read_tsv(CORE_SPECS)]:
        raise RuntimeError("registered carrier-set drift")
    return values  # type: ignore[return-value]


def carrier_census(lines: Sequence[Line], raw35: Sequence[str], all28: Sequence[str], core13: Sequence[str]) -> tuple[list[dict[str, Any]], dict[tuple[str, str], list[tuple[Line, int]]]]:
    occurrences: defaultdict[tuple[str, str], list[tuple[Line, int]]] = defaultdict(list)
    for line in lines:
        for index, surface in enumerate(line.tokens):
            parsed = parse_surface(surface)
            if parsed:
                occurrences[parsed].append((line, index))
    carriers = sorted({carrier for carrier, _ in occurrences})
    computed_raw = [carrier for carrier in carriers if all(occurrences.get((carrier, tail)) for tail in TAILS)]
    computed_all = [carrier for carrier in computed_raw if all(any(line.stable[i] for line, i in occurrences[(carrier, tail)]) for tail in TAILS)]
    computed_core = [carrier for carrier in computed_all if all(
        sum(line.stable[i] for line, i in occurrences[(carrier, tail)]) >= 3 and
        len({physical_folio(line.page) for line, i in occurrences[(carrier, tail)] if line.stable[i]}) >= 3 for tail in TAILS)]
    if computed_raw != sorted(raw35) or computed_all != sorted(all28) or computed_core != sorted(core13):
        raise RuntimeError("raw35/ALL28/CORE13 reconstruction drift")
    rows = []
    for carrier in carriers:
        row: dict[str, Any] = {"carrier": carrier, "raw_complete": int(carrier in raw35),
            "all28_stable_complete": int(carrier in all28), "core13": int(carrier in core13),
            "semantic_credit": 0, "component_export_credit": 0}
        for tail in TAILS:
            cell = occurrences.get((carrier, tail), [])
            row[f"{tail}_raw_occurrences"] = len(cell)
            row[f"{tail}_stable_occurrences"] = sum(line.stable[i] for line, i in cell)
            row[f"{tail}_stable_physical_folios"] = len({physical_folio(line.page) for line, i in cell if line.stable[i]})
        rows.append(row)
    return rows, occurrences


def build_q152(raw35: Sequence[str], thin9: Sequence[str], overlap6: Sequence[str]) -> tuple[frozenset[str], list[dict[str, Any]]]:
    main, thin, overlap = ({carrier + tail for carrier in raw35 for tail in TAILS},
                           {carrier + tail for carrier in thin9 for tail in ("kol", "tal")}, set(overlap6))
    if main & thin != overlap or len(main | thin) != 152:
        raise RuntimeError("Q152 arithmetic/overlap drift")
    q152 = frozenset(main | thin)
    return q152, [{"surface": surface, "raw35_four_cell_member": int(surface in main),
                   "thin9_pair_member": int(surface in thin), "deduplicated_overlap6": int(surface in overlap),
                   "quarantine_rule": "EXACT_COMPLETE_SURFACE_ONLY", "substring_rule": 0,
                   "semantic_credit": 0, "component_export_credit": 0} for surface in sorted(q152)]


def family_surfaces(carrier: str) -> tuple[str, ...]:
    return tuple(carrier + tail for tail in TAILS)


def collect_events(lines: Sequence[Line], paragraphs: Sequence[Paragraph], paragraph_by_locus: Mapping[str, Paragraph], carriers: set[str]) -> list[Event]:
    output: list[Event] = []
    paragraph_line_index = {(p.paragraph_id, line.locus): i for p in paragraphs for i, line in enumerate(p.lines, 1)}
    for line in lines:
        paragraph = paragraph_by_locus.get(line.locus)
        if paragraph is None:
            continue
        for index, surface in enumerate(line.tokens):
            parsed = parse_surface(surface)
            if not parsed or parsed[0] not in carriers or not line.stable[index]:
                continue
            carrier, tail = parsed
            own = family_surfaces(carrier)
            if sum(token in own for token in line.tokens) != 1:
                continue
            it_status, it_ordinal, _ = exact_lcs_alignment(line.tokens, line.cross["it2a_clean"].split(), index)
            rf_status, rf_ordinal, _ = exact_lcs_alignment(line.tokens, line.cross["rf1b_clean"].split(), index)
            if it_status != "UNIQUE_FORCED_EXACT" or rf_status != "UNIQUE_FORCED_EXACT":
                continue
            output.append(Event("", carrier, tail, "L" if tail in {"eol", "ol"} else "DY",
                int(tail in {"eol", "eody"}), surface, line.page, physical_folio(line.page), line.locus,
                line.number, index + 1, line, paragraph, paragraph_line_index[(paragraph.paragraph_id, line.locus)],
                own, it_ordinal, rf_ordinal))
    output.sort(key=lambda event: (selector_sort_key(event.page), event.line_number, event.token_index, event.carrier, event.tail))
    for ordinal, event in enumerate(output, 1):
        event.event_id = f"G808-E{ordinal:04d}"
    return output


def collect_pair_events(lines: Sequence[Line], paragraphs: Sequence[Paragraph], paragraph_by_locus: Mapping[str, Paragraph], pairs: Mapping[str, tuple[str, str]], prefix: str) -> list[Event]:
    output: list[Event] = []
    line_pos = {(p.paragraph_id, line.locus): i for p in paragraphs for i, line in enumerate(p.lines, 1)}
    surface_map = {surface: (carrier, label) for carrier, pair in pairs.items() for label, surface in enumerate((pair[1], pair[0]))}
    for line in lines:
        paragraph = paragraph_by_locus.get(line.locus)
        if paragraph is None:
            continue
        for index, surface in enumerate(line.tokens):
            if surface not in surface_map or not line.stable[index]:
                continue
            carrier, label = surface_map[surface]
            own = pairs[carrier]
            if sum(token in own for token in line.tokens) != 1:
                continue
            it_status, it_ordinal, _ = exact_lcs_alignment(line.tokens, line.cross["it2a_clean"].split(), index)
            rf_status, rf_ordinal, _ = exact_lcs_alignment(line.tokens, line.cross["rf1b_clean"].split(), index)
            if it_status == rf_status == "UNIQUE_FORCED_EXACT":
                output.append(Event("", carrier, "POS" if label else "NEG", prefix, label, surface,
                    line.page, physical_folio(line.page), line.locus, line.number, index + 1, line, paragraph,
                    line_pos[(paragraph.paragraph_id, line.locus)], tuple(own), it_ordinal, rf_ordinal))
    output.sort(key=lambda event: (selector_sort_key(event.page), event.line_number, event.token_index, event.surface))
    for ordinal, event in enumerate(output, 1):
        event.event_id = f"G808-{prefix}-E{ordinal:04d}"
    return output


def length_bin(n: int) -> int:
    return int(math.floor(math.log2(n + 1)))


def index_bin(index: int) -> str:
    return str(index) if index <= 4 else "5PLUS"


def quartile(index: int, count: int) -> int:
    return min(4, 1 + int(math.floor(4 * (index - 1) / count)))


def count_bin(value: int) -> str:
    return str(value) if value <= 2 else "3PLUS"


def word_length_bin(value: int) -> str:
    return str(value) if value <= 6 else "7PLUS"


def position_name(index: int, count: int) -> str:
    return "SINGLE" if count == 1 else "FIRST" if index == 1 else "LAST" if index == count else "MIDDLE"


def build_event_features(event: Event, quarantine: frozenset[str], end_classes: Sequence[str]) -> dict[str, frozenset[str]]:
    own = set(event.own_surfaces)
    topic: set[str] = set()
    for line in event.paragraph.lines:
        if line.locus == event.locus or set(line.tokens) & own:
            continue
        topic.update(f"TOPIC:WHOLE={surface}" for surface in line.tokens if surface not in quarantine)
    template, focal = set(), event.token_index - 1
    for index, surface in enumerate(event.line.tokens):
        delta = index - focal
        if abs(delta) <= 2 or surface in quarantine:
            continue
        side, distance = ("L" if delta < 0 else "R"), abs(delta)
        bucket = f"{side}{distance}" if distance in (3, 4) else f"{side}5PLUS"
        template.add(f"TEMPLATE:{bucket}={surface}")
    line_tokens = [surface for surface in event.line.tokens if surface not in quarantine]
    paragraph_tokens = [surface for line in event.paragraph.lines for surface in line.tokens if surface not in quarantine]
    form_base = {f"FORM:SECTION={event.paragraph.section}", f"FORM:LANGUAGE={event.paragraph.language}",
        f"FORM:HAND={event.paragraph.hand}", f"FORM:JOINT={event.paragraph.section}/{event.paragraph.language}/{event.paragraph.hand}",
        f"FORM:TARGETFREE_LINE_LENGTH_BIN={length_bin(len(line_tokens))}",
        f"FORM:TARGETFREE_PARAGRAPH_LENGTH_BIN={length_bin(len(paragraph_tokens))}",
        f"FORM:PARAGRAPH_LINE_COUNT_BIN={length_bin(len(event.paragraph.lines))}",
        f"FORM:PARAGRAPH_LINE_POSITION={position_name(event.paragraph_line_index, len(event.paragraph.lines))}",
        f"FORM:PARAGRAPH_LINE_FORWARD_INDEX={index_bin(event.paragraph_line_index)}",
        f"FORM:PARAGRAPH_LINE_REVERSE_INDEX={index_bin(len(event.paragraph.lines) - event.paragraph_line_index + 1)}",
        f"FORM:PARAGRAPH_LINE_QUARTILE={quartile(event.paragraph_line_index, len(event.paragraph.lines))}"}
    for scope, tokens in (("LINE", line_tokens), ("PARAGRAPH", paragraph_tokens)):
        lengths, ends = Counter(word_length_bin(len(surface)) for surface in tokens), Counter(surface[-1] for surface in tokens if surface)
        for bucket in ("1", "2", "3", "4", "5", "6", "7PLUS"):
            form_base.add(f"FORM:{scope}_WORD_LENGTH_{bucket}_COUNT={count_bin(lengths[bucket])}")
        for ending in end_classes:
            form_base.add(f"FORM:{scope}_END_{ending}_COUNT={count_bin(ends[ending])}")
    position = {f"POSITION:FOCAL_HOLE={position_name(event.token_index, len(event.line.tokens))}",
        f"POSITION:FORWARD_INDEX={index_bin(event.token_index)}",
        f"POSITION:REVERSE_INDEX={index_bin(len(event.line.tokens) - event.token_index + 1)}",
        f"POSITION:QUARTILE={quartile(event.token_index, len(event.line.tokens))}"}
    slot, raw_slot, visible, raw_visible, mask = set(), set(), {}, {}, set()
    names = {-2: "L2", -1: "L1", 1: "R1", 2: "R2"}
    for offset, name in names.items():
        index = focal + offset
        if not 0 <= index < len(event.line.tokens):
            mask.add(f"MASK:{name}=BOUNDARY")
            continue
        surface = event.line.tokens[index]
        if surface in quarantine:
            mask.add(f"MASK:{name}=QUARANTINED")
            continue
        raw_visible[offset] = surface
        raw_slot.add(f"RAW_SLOT:{name}={surface}")
        if event.line.stable[index]:
            visible[offset] = surface
            slot.add(f"SLOT:{name}={surface}")
            mask.add(f"MASK:{name}=VISIBLE_STABLE")
        else:
            mask.add(f"MASK:{name}=UNSTABLE")
    for left, right, name in ((-2, -1, "L2_L1"), (-1, 1, "L1_R1"), (1, 2, "R1_R2")):
        if left in visible and right in visible:
            slot.add(f"SLOT:{name}={visible[left]}>{visible[right]}")
        if left in raw_visible and right in raw_visible:
            raw_slot.add(f"RAW_SLOT:{name}={raw_visible[left]}>{raw_visible[right]}")
    mask.update((f"MASK:LINE_Q_COUNT={count_bin(sum(s in quarantine for s in event.line.tokens))}",
                 f"MASK:LINE_UNSTABLE_COUNT={count_bin(sum(not x for x in event.line.stable))}"))
    return {"TOPIC": frozenset(topic), "TEMPLATE": frozenset(template),
        "FORM_REGIME": frozenset(form_base | position), "FORM_BASE": frozenset(form_base),
        "POSITION": frozenset(position), "SLOT_HOLE": frozenset(slot), "RAW_SLOT": frozenset(raw_slot),
        "MASK_STATUS": frozenset(mask)}


def attach_features(events: Sequence[Event], q152: frozenset[str], ed1: frozenset[str], end_classes: Sequence[str]) -> None:
    for event in events:
        event.features = build_event_features(event, q152, end_classes)
        event.features_ed1 = build_event_features(event, frozenset(q152 | ed1), end_classes)
        event.targetfree_line_length_bin = length_bin(sum(surface not in q152 for surface in event.line.tokens))


@dataclass(frozen=True)
class NBModel:
    weights: Mapping[str, float]
    vocabulary: frozenset[str]
    positive_mass: float
    negative_mass: float


PRIMARY_DECKS = {
    "topic": ("TOPIC",), "template": ("TEMPLATE",), "form": ("FORM_REGIME",),
    "slot": ("SLOT_HOLE",), "union_nuisance": ("TOPIC", "TEMPLATE", "FORM_REGIME"),
    "union_augmented": ("TOPIC", "TEMPLATE", "FORM_REGIME", "SLOT_HOLE"),
    "form_base": ("FORM_BASE",), "position": ("POSITION",), "mask": ("MASK_STATUS",),
    "raw_slot": ("RAW_SLOT",)}


def features_for(event: Event, variant: str, names: Sequence[str]) -> frozenset[str]:
    decks = event.features_ed1 if variant == "ED1" else event.features
    return frozenset(feature for name in names for feature in decks[name])


def train_nb(events: Sequence[Event], getter: Callable[[Event], frozenset[str]],
             label_override: Mapping[str, int] | None = None,
             require_two_carriers: bool = True) -> NBModel:
    carriers: defaultdict[str, set[str]] = defaultdict(set)
    folios: defaultdict[str, set[str]] = defaultdict(set)
    cells: Counter[tuple[str, int]] = Counter()
    for event in events:
        label = label_override[event.event_id] if label_override is not None else event.label
        cells[(event.carrier, label)] += 1
        for feature in getter(event):
            carriers[feature].add(event.carrier)
            folios[feature].add(event.folio)
    vocabulary = frozenset(feature for feature in carriers
                           if (len(carriers[feature]) >= 2 or not require_two_carriers)
                           and len(folios[feature]) >= 2)
    positive, negative = Counter(), Counter()
    for event in events:
        label = label_override[event.event_id] if label_override is not None else event.label
        weight = 1.0 / cells[(event.carrier, label)]
        target = positive if label else negative
        for feature in getter(event) & vocabulary:
            target[feature] += weight
    pos_mass, neg_mass = math.fsum(positive.values()), math.fsum(negative.values())
    if not vocabulary:
        return NBModel({}, vocabulary, pos_mass, neg_mass)
    pos_denom, neg_denom = pos_mass + ALPHA * len(vocabulary), neg_mass + ALPHA * len(vocabulary)
    weights = {feature: math.log((positive[feature] + ALPHA) / pos_denom)
               - math.log((negative[feature] + ALPHA) / neg_denom) for feature in vocabulary}
    return NBModel(weights, vocabulary, pos_mass, neg_mass)


def nb_score(model: NBModel, features: frozenset[str]) -> tuple[float, int]:
    known = features & model.vocabulary
    return ((math.fsum(model.weights[feature] for feature in known) / len(known), len(known))
            if known else (0.0, 0))


def train_bundle(events: Sequence[Event], variant: str = "EXACT",
                 label_override: Mapping[str, int] | None = None,
                 auxiliary: bool = True, require_two_carriers: bool = True) -> dict[str, NBModel]:
    included = tuple(PRIMARY_DECKS) if auxiliary else (
        "topic", "template", "form", "slot", "union_nuisance", "union_augmented")
    return {name: train_nb(events,
                           lambda event, deck_names=deck_names: features_for(event, variant, deck_names),
                           label_override, require_two_carriers)
            for name, deck_names in PRIMARY_DECKS.items() if name in included}


def score_bundle(bundle: Mapping[str, NBModel], event: Event, variant: str = "EXACT") -> dict[str, float | int]:
    output: dict[str, float | int] = {}
    for name, model in bundle.items():
        score, known = nb_score(model, features_for(event, variant, PRIMARY_DECKS[name]))
        output[name], output[f"{name}_known"] = score, known
    output["nuisance"] = float(output["topic"]) + float(output["template"]) + float(output["form"])
    output["augmented"] = float(output["nuisance"]) + float(output["slot"])
    if "form_base" in output:
        output["nuisance_without_position"] = float(output["topic"]) + float(output["template"]) + float(output["form_base"])
        output["nuisance_plus_mask"] = float(output["nuisance"]) + float(output["mask"])
        output["augmented_raw"] = float(output["nuisance"]) + float(output["raw_slot"])
    return output


def model_events(events: Sequence[Event], axis: str) -> list[Event]:
    return [event for event in events if event.axis == axis]


def run_relation_model(spec: Mapping[str, str], population_events: Sequence[Event],
                       variant: str = "EXACT", auxiliary: bool = True) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source, target = model_events(population_events, spec["source_axis"]), model_events(population_events, spec["target_axis"])
    groups: defaultdict[tuple[str, str], list[Event]] = defaultdict(list)
    for event in target:
        groups[(event.carrier, event.folio)].append(event)
    predictions, fold_rows = [], []
    for carrier, folio in sorted(groups):
        test = sorted(groups[(carrier, folio)], key=lambda event: (selector_sort_key(event.page), event.line_number, event.token_index, event.event_id))
        train = [event for event in source if event.carrier != carrier and event.folio != folio]
        remaining = sorted({event.carrier for event in train})
        expected_remaining = len({event.carrier for event in source}) - 1
        if {event.label for event in train} != {0, 1} or len(remaining) != expected_remaining:
            raise RuntimeError(f"held fold capacity drift: {spec['model_id']}:{carrier}:{folio}")
        bundle = train_bundle(train, variant, auxiliary=auxiliary)
        fold_rows.append({"model_id": spec["model_id"], "population": spec["population"],
            "source_axis": spec["source_axis"], "target_axis": spec["target_axis"],
            "held_carrier": carrier, "held_physical_folio": folio, "train_events": len(train),
            "train_positive_events": sum(event.label for event in train),
            "train_negative_events": sum(1 - event.label for event in train), "train_carriers": len(remaining),
            "train_physical_folios": len({event.folio for event in train}), "test_events": len(test),
            "test_positive_events": sum(event.label for event in test),
            "test_negative_events": sum(1 - event.label for event in test),
            "carrier_excluded": int(all(event.carrier != carrier for event in train)),
            "physical_folio_excluded": int(all(event.folio != folio for event in train)),
            "topic_vocabulary": len(bundle["topic"].vocabulary), "template_vocabulary": len(bundle["template"].vocabulary),
            "form_vocabulary": len(bundle["form"].vocabulary), "slot_vocabulary": len(bundle["slot"].vocabulary),
            "union_nuisance_vocabulary": len(bundle["union_nuisance"].vocabulary),
            "union_augmented_vocabulary": len(bundle["union_augmented"].vocabulary), "fold_scoreable": 1})
        for event in test:
            values = score_bundle(bundle, event, variant)
            row: dict[str, Any] = {"prediction_id": f"{spec['model_id']}:{event.event_id}",
                "model_id": spec["model_id"], "population": spec["population"],
                "source_axis": spec["source_axis"], "target_axis": spec["target_axis"],
                "event_id": event.event_id, "carrier": event.carrier, "target_tail": event.tail,
                "true_label": event.label, "page": event.page, "physical_folio": event.folio,
                "paragraph_id": event.paragraph.paragraph_id, "locus": event.locus,
                "line_number": event.line_number, "token_index": event.token_index,
                "section": event.paragraph.section, "language": event.paragraph.language,
                "hand": event.paragraph.hand, "targetfree_line_length_bin": event.targetfree_line_length_bin,
                "variant": variant}
            for name, value in values.items():
                row[name if name.endswith("_known") else f"{name}_score"] = value if name.endswith("_known") else f12(float(value))
            predictions.append(row)
    if len(predictions) != len(target):
        raise RuntimeError(f"target prediction coverage drift: {spec['model_id']}")
    return predictions, fold_rows


def auc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positive, negative = ([score for label, score in zip(labels, scores) if label == value] for value in (1, 0))
    if not positive or not negative:
        return None
    return math.fsum(1 if pos > neg else .5 if pos == neg else 0 for pos in positive for neg in negative) / (len(positive) * len(negative))


def balanced_accuracy(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positive, negative = ([score for label, score in zip(labels, scores) if label == value] for value in (1, 0))
    if not positive or not negative:
        return None
    pos = math.fsum(1 if score > 0 else .5 if score == 0 else 0 for score in positive) / len(positive)
    neg = math.fsum(1 if score < 0 else .5 if score == 0 else 0 for score in negative) / len(negative)
    return (pos + neg) / 2


def balanced_logloss(labels: Sequence[int], scores: Sequence[float], carriers: Sequence[str]) -> float | None:
    if not labels:
        return None
    cells = Counter(zip(carriers, labels))
    weighted, weights = 0.0, 0.0
    for label, score, carrier in zip(labels, scores, carriers):
        probability = 1 / (1 + math.exp(-max(-35.0, min(35.0, score))))
        loss = -(label * math.log(max(probability, 1e-15)) + (1 - label) * math.log(max(1 - probability, 1e-15)))
        weight = 1 / cells[(carrier, label)]
        weighted, weights = weighted + weight * loss, weights + weight
    return weighted / weights


def metrics(rows: Sequence[Mapping[str, Any]], score_field: str,
            label_override: Mapping[str, int] | None = None) -> dict[str, Any]:
    labels = [label_override[str(row["event_id"])] if label_override is not None else int(row["true_label"]) for row in rows]
    scores, carriers = [float(row[score_field]) for row in rows], [str(row["carrier"]) for row in rows]
    per_carrier: dict[str, float] = {}
    for carrier in sorted(set(carriers)):
        indexes = [i for i, value in enumerate(carriers) if value == carrier]
        value = auc([labels[i] for i in indexes], [scores[i] for i in indexes])
        if value is not None:
            per_carrier[carrier] = value
    return {"micro_auc": auc(labels, scores),
        "carrier_macro_auc": math.fsum(per_carrier.values()) / len(per_carrier) if per_carrier else None,
        "balanced_accuracy": balanced_accuracy(labels, scores),
        "balanced_log_loss": balanced_logloss(labels, scores, carriers),
        "carriers_scored": len(per_carrier), "carriers_auc_above_half": sum(value > .5 for value in per_carrier.values()),
        "carriers_auc_below_half": sum(value < .5 for value in per_carrier.values()),
        "per_carrier": per_carrier, "events": len(rows), "positive_events": sum(labels),
        "negative_events": len(labels) - sum(labels)}


SCORE_FIELDS = {"TOPIC": "topic_score", "TEMPLATE": "template_score", "FORM_REGIME": "form_score",
    "SLOT_HOLE": "slot_score", "NUISANCE": "nuisance_score", "AUGMENTED": "augmented_score",
    "UNION_NUISANCE": "union_nuisance_score", "UNION_AUGMENTED": "union_augmented_score"}


def score_summary(model_specs: Sequence[Mapping[str, str]], predictions: Sequence[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    output, lookup = [], {}
    for spec in model_specs:
        subset = [row for row in predictions if row["model_id"] == spec["model_id"]]
        for channel, field in SCORE_FIELDS.items():
            result = metrics(subset, field)
            lookup[(spec["model_id"], channel)] = result
            output.append({"model_id": spec["model_id"], "population": spec["population"],
                "source_axis": spec["source_axis"], "target_axis": spec["target_axis"], "score_channel": channel,
                "events": result["events"], "positive_events": result["positive_events"],
                "negative_events": result["negative_events"], "micro_auc": f12(result["micro_auc"]),
                "carrier_macro_auc": f12(result["carrier_macro_auc"]),
                "balanced_accuracy": f12(result["balanced_accuracy"]),
                "balanced_log_loss": f12(result["balanced_log_loss"]), "carriers_scored": result["carriers_scored"],
                "carriers_auc_above_half": result["carriers_auc_above_half"],
                "carriers_auc_below_half": result["carriers_auc_below_half"], "post_score_sign_flip": 0,
                "semantic_credit": 0, "component_export_credit": 0})
    return output, lookup


def conditional_concordance(rows: Sequence[Mapping[str, Any]], score_field: str,
                            label_override: Mapping[str, int] | None = None) -> tuple[float | None, float | None, list[dict[str, Any]]]:
    groups: defaultdict[tuple[str, str, str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["carrier"]), str(row["section"]), str(row["language"]), str(row["hand"]),
                str(row["targetfree_line_length_bin"]))].append(row)
    by_carrier_credit: Counter[str] = Counter()
    by_carrier_pairs: Counter[str] = Counter()
    audit = []
    for key, values in sorted(groups.items()):
        positives = [row for row in values if (label_override[str(row["event_id"])] if label_override else int(row["true_label"])) == 1]
        negatives = [row for row in values if (label_override[str(row["event_id"])] if label_override else int(row["true_label"])) == 0]
        credit = math.fsum(1 if float(pos[score_field]) > float(neg[score_field]) else .5 if float(pos[score_field]) == float(neg[score_field]) else 0
                           for pos in positives for neg in negatives)
        pairs = len(positives) * len(negatives)
        by_carrier_credit[key[0]] += credit
        by_carrier_pairs[key[0]] += pairs
        audit.append({"carrier": key[0], "section": key[1], "language": key[2], "hand": key[3],
            "targetfree_line_length_bin": key[4], "events": len(values), "positive_events": len(positives),
            "negative_events": len(negatives), "comparable_pairs": pairs,
            "concordance": f12(credit / pairs if pairs else None)})
    carrier_values = [by_carrier_credit[carrier] / by_carrier_pairs[carrier] for carrier in sorted(by_carrier_pairs) if by_carrier_pairs[carrier]]
    total_pairs = sum(by_carrier_pairs.values())
    macro = math.fsum(carrier_values) / len(carrier_values) if carrier_values else None
    pooled = math.fsum(by_carrier_credit.values()) / total_pairs if total_pairs else None
    return macro, pooled, audit


def make_conditional_rows(model_specs: Sequence[Mapping[str, str]], predictions: Sequence[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, str], float | None]]:
    output, lookup = [], {}
    for spec in model_specs:
        subset = [row for row in predictions if row["model_id"] == spec["model_id"]]
        for channel, field in (("NUISANCE", "nuisance_score"), ("SLOT_HOLE", "slot_score"), ("AUGMENTED", "augmented_score")):
            macro, pooled, strata = conditional_concordance(subset, field)
            lookup[(spec["model_id"], channel)] = macro
            output.append({"row_type": "SUMMARY", "model_id": spec["model_id"], "score_channel": channel,
                "carrier": "ALL", "section": "ALL", "language": "ALL", "hand": "ALL",
                "targetfree_line_length_bin": "ALL", "events": len(subset),
                "positive_events": sum(int(row["true_label"]) for row in subset),
                "negative_events": sum(1 - int(row["true_label"]) for row in subset),
                "comparable_pairs": sum(int(row["comparable_pairs"]) for row in strata),
                "concordance": f12(macro), "pooled_pair_concordance_audit": f12(pooled)})
            for row in strata:
                if int(row["comparable_pairs"]):
                    output.append({"row_type": "STRATUM", "model_id": spec["model_id"], "score_channel": channel,
                                   **row, "pooled_pair_concordance_audit": "NA"})
    return output, lookup


def rotate_target_labels(rows: Sequence[Mapping[str, Any]], k: int) -> tuple[dict[str, int], list[dict[str, Any]]]:
    groups: defaultdict[tuple[str, str, str, str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["target_axis"]), str(row["carrier"]), str(row["section"]), str(row["language"]),
                str(row["hand"]), str(row["targetfree_line_length_bin"]))].append(row)
    labels, audit = {}, []
    for key, values in sorted(groups.items()):
        ordered = sorted(values, key=lambda row: (selector_sort_key(str(row["page"])), int(row["line_number"]),
                                                  int(row["token_index"]), str(row["event_id"])))
        n, moved = len(ordered), 0
        for index, row in enumerate(ordered):
            label = int(ordered[(index - (k % n)) % n]["true_label"])
            labels[str(row["event_id"])] = label
            moved += int(label != int(row["true_label"]))
        audit.append({"null_family": "C01_TARGET_LABEL_ROTATION", "null_id": f"K{k:02d}",
            "model_id": str(rows[0]["model_id"]), "target_axis": key[0], "carrier": key[1],
            "section": key[2], "language": key[3], "hand": key[4], "targetfree_line_length_bin": key[5],
            "stratum_events": n, "offset_mod_n": k % n, "moved_labels": moved,
            "identity_labels": n - moved, "flipped_source_carriers": "NA"})
    return labels, audit


def carrier_null_predictions(spec: Mapping[str, str], core_events: Sequence[Event], repetition: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source, target = model_events(core_events, spec["source_axis"]), model_events(core_events, spec["target_axis"])
    groups: defaultdict[tuple[str, str], list[Event]] = defaultdict(list)
    for event in target:
        groups[(event.carrier, event.folio)].append(event)
    output, audit_map = [], {}
    for carrier, folio in sorted(groups):
        train = [event for event in source if event.carrier != carrier and event.folio != folio]
        remaining = sorted({event.carrier for event in train})
        if len(remaining) != 12:
            raise RuntimeError(f"C02 expected twelve carriers: {spec['model_id']}:{carrier}:{folio}")
        flipped = {remaining[(repetition + offset) % 12] for offset in range(6)}
        override = {event.event_id: 1 - event.label if event.carrier in flipped else event.label for event in train}
        models = {name: train_nb(train, lambda event, names=names: features_for(event, "EXACT", names), override)
                  for name, names in (("topic", ("TOPIC",)), ("template", ("TEMPLATE",)),
                                      ("form", ("FORM_REGIME",)))}
        value = pipe(sorted(flipped))
        if carrier in audit_map and audit_map[carrier] != value:
            raise RuntimeError("carrier-null block changed with held folio")
        audit_map[carrier] = value
        for event in groups[(carrier, folio)]:
            scores = [nb_score(models[name], features_for(event, "EXACT", names))[0]
                      for name, names in (("topic", ("TOPIC",)), ("template", ("TEMPLATE",)),
                                          ("form", ("FORM_REGIME",)))]
            output.append({"event_id": event.event_id, "carrier": event.carrier,
                           "true_label": event.label, "score": math.fsum(scores)})
    audit = [{"null_family": "C02_CARRIER_SIGN_ROTATION", "null_id": f"R{repetition:02d}",
        "model_id": spec["model_id"], "target_axis": spec["target_axis"], "carrier": carrier,
        "section": "ALL", "language": "ALL", "hand": "ALL", "targetfree_line_length_bin": "ALL",
        "stratum_events": "NA", "offset_mod_n": repetition, "moved_labels": "NA", "identity_labels": "NA",
        "flipped_source_carriers": flipped} for carrier, flipped in sorted(audit_map.items())]
    return output, audit


def null_experiments(primary_specs: Sequence[Mapping[str, str]], core_events: Sequence[Event],
                     predictions: Sequence[dict[str, Any]], score_lookup: Mapping[tuple[str, str], dict[str, Any]],
                     conditional_lookup: Mapping[tuple[str, str], float | None]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    null_rows, audits, ranks = [], [], {}
    for spec in primary_specs:
        model_id = spec["model_id"]
        subset = [row for row in predictions if row["model_id"] == model_id]
        observed_gain = float(score_lookup[(model_id, "AUGMENTED")]["carrier_macro_auc"]) - float(score_lookup[(model_id, "NUISANCE")]["carrier_macro_auc"])
        observed_conditional = (conditional_lookup[(model_id, "AUGMENTED")] or 0) - (conditional_lookup[(model_id, "NUISANCE")] or 0)
        gains = []
        for k in range(1, 25):
            labels, audit = rotate_target_labels(subset, k)
            audits.extend(audit)
            nuisance, augmented, slot = (metrics(subset, field, labels)
                for field in ("nuisance_score", "augmented_score", "slot_score"))
            cond_n, _, _ = conditional_concordance(subset, "nuisance_score", labels)
            cond_a, _, _ = conditional_concordance(subset, "augmented_score", labels)
            gain = float(augmented["carrier_macro_auc"]) - float(nuisance["carrier_macro_auc"])
            gains.append(gain)
            moved = sum(int(row["moved_labels"]) for row in audit)
            changed_fraction = moved / len(subset)
            null_rows.append({"null_family": "C01_TARGET_LABEL_ROTATION", "null_id": f"K{k:02d}",
                "model_id": model_id, "carrier_macro_auc": f12(augmented["carrier_macro_auc"]),
                "nuisance_carrier_macro_auc": f12(nuisance["carrier_macro_auc"]),
                "slot_carrier_macro_auc": f12(slot["carrier_macro_auc"]), "local_gain": f12(gain),
                "conditional_local_gain": f12((cond_a or 0) - (cond_n or 0)), "changed_labels": moved,
                "changed_fraction": f12(changed_fraction), "mobility_warning": "LOW_MOBILITY" if changed_fraction < .20 else "NONE",
                "observed_reference": 0, "ties_count_against_target": 1})
        carrier_aucs = []
        for repetition in range(12):
            null_predictions, audit = carrier_null_predictions(spec, core_events, repetition)
            audits.extend(audit)
            result = metrics(null_predictions, "score")
            value = float(result["carrier_macro_auc"])
            carrier_aucs.append(value)
            null_rows.append({"null_family": "C02_CARRIER_SIGN_ROTATION", "null_id": f"R{repetition:02d}",
                "model_id": model_id, "carrier_macro_auc": f12(value), "nuisance_carrier_macro_auc": f12(value),
                "slot_carrier_macro_auc": "NA", "local_gain": "NA", "conditional_local_gain": "NA",
                "changed_labels": "NA", "changed_fraction": "NA", "mobility_warning": "NA",
                "observed_reference": 0, "ties_count_against_target": 1})
        nuisance_observed = float(score_lookup[(model_id, "NUISANCE")]["carrier_macro_auc"])
        local_rank = 1 + sum(value >= observed_gain for value in gains)
        portability_rank = 1 + sum(value >= nuisance_observed for value in carrier_aucs)
        ranks[model_id] = {"local_gain_rank": local_rank, "nuisance_portability_rank": portability_rank,
                           "observed_gain": observed_gain, "observed_conditional_gain": observed_conditional}
        null_rows.append({"null_family": "OBSERVED", "null_id": "OBSERVED_PRIMARY", "model_id": model_id,
            "carrier_macro_auc": f12(score_lookup[(model_id, "AUGMENTED")]["carrier_macro_auc"]),
            "nuisance_carrier_macro_auc": f12(nuisance_observed),
            "slot_carrier_macro_auc": f12(score_lookup[(model_id, "SLOT_HOLE")]["carrier_macro_auc"]),
            "local_gain": f12(observed_gain), "conditional_local_gain": f12(observed_conditional),
            "changed_labels": 0, "changed_fraction": 0, "mobility_warning": "OBSERVED",
            "observed_reference": 1, "ties_count_against_target": 1})
        null_rows.append({"null_family": "RANK", "null_id": "EXACT_RANKS", "model_id": model_id,
            "carrier_macro_auc": "NA", "nuisance_carrier_macro_auc": "NA", "slot_carrier_macro_auc": "NA",
            "local_gain": local_rank, "conditional_local_gain": portability_rank, "changed_labels": "NA",
            "changed_fraction": "NA", "mobility_warning": "NA", "observed_reference": 1,
            "ties_count_against_target": 1})
    return null_rows, audits, ranks


def ablation_rows(primary_specs: Sequence[Mapping[str, str]], predictions: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    channels = {"SLOT_STABLE_ONLY": "slot_score", "SLOT_RAW_ONLY": "raw_slot_score",
        "POSITION_ONLY": "position_score", "MASK_STATUS_ONLY": "mask_score",
        "FORM_WITHOUT_POSITION": "form_base_score", "FORM_REGIME_PRIMARY": "form_score",
        "NUISANCE_WITHOUT_POSITION": "nuisance_without_position_score", "NUISANCE_PRIMARY": "nuisance_score",
        "NUISANCE_PLUS_MASK": "nuisance_plus_mask_score", "AUGMENTED_STABLE": "augmented_score",
        "AUGMENTED_RAW": "augmented_raw_score"}
    output = []
    for spec in primary_specs:
        subset = [row for row in predictions if row["model_id"] == spec["model_id"]]
        nuisance = float(metrics(subset, "nuisance_score")["carrier_macro_auc"])
        for channel, field in channels.items():
            result = metrics(subset, field)
            output.append({"model_id": spec["model_id"], "audit_channel": channel, "events": len(subset),
                "micro_auc": f12(result["micro_auc"]), "carrier_macro_auc": f12(result["carrier_macro_auc"]),
                "balanced_accuracy": f12(result["balanced_accuracy"]),
                "balanced_log_loss": f12(result["balanced_log_loss"]),
                "increment_over_primary_nuisance_macro_auc": f12(float(result["carrier_macro_auc"]) - nuisance),
                "selection_credit": ("PRIMARY" if channel in {"SLOT_STABLE_ONLY", "AUGMENTED_STABLE", "NUISANCE_PRIMARY"}
                                     else "AUDIT_ONLY")})
    return output


def carrier_direction_rows(model_specs: Sequence[Mapping[str, str]], predictions: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for spec in model_specs:
        subset = [row for row in predictions if row["model_id"] == spec["model_id"]]
        for carrier in sorted({row["carrier"] for row in subset}):
            values = [row for row in subset if row["carrier"] == carrier]
            for channel, field in (("NUISANCE", "nuisance_score"), ("SLOT_HOLE", "slot_score"),
                                   ("AUGMENTED", "augmented_score"), ("UNION_AUGMENTED", "union_augmented_score")):
                result = metrics(values, field)
                value = result["micro_auc"]
                output.append({"model_id": spec["model_id"], "population": spec["population"],
                    "carrier": carrier, "score_channel": channel, "events": len(values),
                    "positive_events": result["positive_events"], "negative_events": result["negative_events"],
                    "auc": f12(value), "direction": ("EXPANDED" if value is not None and value > .5 else
                        "BASE" if value is not None and value < .5 else "TIE_OR_UNSCORABLE"),
                    "semantic_credit": 0, "component_export_credit": 0})
    return output


def feature_capacity(events: Sequence[Event], population: str) -> list[dict[str, Any]]:
    output = []
    for deck in ("TOPIC", "TEMPLATE", "FORM_REGIME", "SLOT_HOLE", "RAW_SLOT", "POSITION", "MASK_STATUS"):
        counts = [len(event.features[deck]) for event in events]
        features = {feature for event in events for feature in event.features[deck]}
        carriers, folios = defaultdict(set), defaultdict(set)
        for event in events:
            for feature in event.features[deck]:
                carriers[feature].add(event.carrier)
                folios[feature].add(event.folio)
        supported = {feature for feature in features if len(carriers[feature]) >= 2 and len(folios[feature]) >= 2}
        output.append({"population": population, "deck_id": deck, "events": len(events),
            "nonempty_events": sum(value > 0 for value in counts), "empty_events": sum(value == 0 for value in counts),
            "feature_types": len(features), "global_two_carrier_two_folio_supported_types": len(supported),
            "mean_features_per_event": f12(math.fsum(counts) / len(counts) if counts else 0),
            "max_features_per_event": max(counts, default=0), "feature_value": "BINARY_PRESENCE"})
    return output


def custom_control_scores(events: Sequence[Event], mode: str) -> list[dict[str, Any]]:
    predictions = []
    groups: defaultdict[tuple[str, str], list[Event]] = defaultdict(list)
    for event in events:
        groups[(event.carrier if mode == "COMPONENT_AND_FOLIO_HELD" else "ALL_CARRIERS", event.folio)].append(event)
    for (held_carrier, folio), test in sorted(groups.items()):
        train = [event for event in events if event.folio != folio and
                 (mode != "COMPONENT_AND_FOLIO_HELD" or event.carrier != held_carrier)]
        if {event.label for event in train} != {0, 1}:
            raise RuntimeError(f"control missing class: {mode}:{held_carrier}:{folio}")
        bundle = train_bundle(train, auxiliary=False)
        for event in test:
            values = score_bundle(bundle, event)
            predictions.append({"event_id": event.event_id, "carrier": event.carrier, "true_label": event.label,
                **{f"{name}_score": f12(float(value)) for name, value in values.items() if not name.endswith("_known")}})
    output = []
    for carrier in sorted({event.carrier for event in events}):
        values = [event for event in events if event.carrier == carrier]
        output.append({"row_type": "CENSUS", "carrier": carrier,
            "surface_positive": next((event.surface for event in values if event.label), "NA"),
            "surface_negative": next((event.surface for event in values if not event.label), "NA"),
            "events": len(values), "positive_events": sum(event.label for event in values),
            "negative_events": sum(1 - event.label for event in values), "physical_folios": len({event.folio for event in values}),
            "score_channel": "NA", "micro_auc": "NA", "carrier_macro_auc": "NA", "balanced_accuracy": "NA",
            "balanced_log_loss": "NA", "holdout": mode, "selection_credit": "CALIBRATION_ONLY", "semantic_credit": 0})
    for channel, field in SCORE_FIELDS.items():
        result = metrics(predictions, field)
        output.append({"row_type": "SCORE", "carrier": "ALL", "surface_positive": "NA", "surface_negative": "NA",
            "events": len(events), "positive_events": sum(event.label for event in events),
            "negative_events": sum(1 - event.label for event in events), "physical_folios": len({event.folio for event in events}),
            "score_channel": channel, "micro_auc": f12(result["micro_auc"]),
            "carrier_macro_auc": f12(result["carrier_macro_auc"]), "balanced_accuracy": f12(result["balanced_accuracy"]),
            "balanced_log_loss": f12(result["balanced_log_loss"]), "holdout": mode,
            "selection_credit": "CALIBRATION_ONLY", "semantic_credit": 0})
    return output


def stage_census(lines: Sequence[Line], paragraph_by_locus: Mapping[str, Paragraph], carriers: set[str], population: str) -> list[dict[str, Any]]:
    expected = {
        ("CORE13", "L"): (1335, 7, 1328, 1169, 1154, 914),
        ("CORE13", "DY"): (1834, 9, 1825, 1124, 1063, 863),
        ("ALL28", "L"): (1541, 8, 1533, 1352, 1337, 1091),
        ("ALL28", "DY"): (2262, 12, 2250, 1395, 1331, 1117)}
    output = []
    for axis, allowed_tails in (("L", {"ol", "eol"}), ("DY", {"edy", "eody"})):
        raw = outside = strict = stable = lcs = singleton = 0
        strict_folios, accepted_lines, accepted_paragraphs = set(), set(), set()
        for line in lines:
            paragraph = paragraph_by_locus.get(line.locus)
            for index, surface in enumerate(line.tokens):
                parsed = parse_surface(surface)
                if not parsed or parsed[0] not in carriers or parsed[1] not in allowed_tails:
                    continue
                raw += 1
                if paragraph is None:
                    outside += 1
                    continue
                strict += 1
                strict_folios.add(physical_folio(line.page))
                if not line.stable[index]:
                    continue
                stable += 1
                it_status, _, _ = exact_lcs_alignment(line.tokens, line.cross["it2a_clean"].split(), index)
                rf_status, _, _ = exact_lcs_alignment(line.tokens, line.cross["rf1b_clean"].split(), index)
                if it_status != "UNIQUE_FORCED_EXACT" or rf_status != "UNIQUE_FORCED_EXACT":
                    continue
                lcs += 1
                own = family_surfaces(parsed[0])
                if sum(token in own for token in line.tokens) == 1:
                    singleton += 1
                    accepted_lines.add((line.page, line.locus))
                    accepted_paragraphs.add(paragraph.paragraph_id)
        observed = (raw, outside, strict, stable, lcs, singleton)
        if observed != expected[(population, axis)]:
            raise RuntimeError(f"{population}/{axis} stage census drift: {observed}")
        output.append({"scope": population, "item": f"{axis}_FILTER_FUNNEL", "count": singleton,
            "expected": singleton, "status": "PASS", "raw_parsed": raw, "outside_strict": outside,
            "strict_parsed": strict, "rank_stable": stable, "unique_forced_lcs": lcs,
            "own_family_singleton": singleton, "rank_stable_rate_strict_prefilter": f12(stable / strict),
            "accepted_paragraphs": len(accepted_paragraphs), "accepted_focal_lines": len(accepted_lines),
            "strict_candidate_physical_folios": len(strict_folios)})
    return output


def clean_contact_metrics(core_events: Sequence[Event], q152: frozenset[str]) -> tuple[dict[str, float | int | None], list[dict[str, Any]]]:
    spans: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    span_rows = read_tsv(G759_SPANS)
    assert_no_sealed(span_rows)
    for row in span_rows:
        # Direct derived input; page and locus must both agree and folio is replayed.
        if physical_folio(row["page"]).startswith("f84"):
            raise RuntimeError("sealed overlay row")
        left, right = int(row["left_token_ordinal"]), int(row["right_token_ordinal"])
        if row["left_surface"] in q152 or row["right_surface"] in q152:
            continue
        spans[(row["page"], row["locus"])].append({"left": left, "right": right, "family": row["family"]})
    anchors: defaultdict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    anchor_rows = read_tsv(G768_ANCHORS)
    assert_no_sealed(anchor_rows)
    for row in anchor_rows:
        if row["reader_exact"] == "1" and row["surface"] not in q152:
            anchors[(row["page"], row["locus"])].append((int(row["token_index"]), row["surface"]))
    openers: defaultdict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    opener_rows = read_tsv(G757_OPENERS)
    assert_no_sealed(opener_rows)
    for row in opener_rows:
        if row["surface"] not in q152:
            openers[(row["page"], row["locus"])].append((1, row["surface"]))
    contacts = []
    for event in core_events:
        key, ordinal = (event.page, event.locus), event.token_index
        amount = quality = False
        for span in spans[key]:
            left, right = int(span["left"]), int(span["right"])
            outside = ordinal < left or ordinal > right
            distance = min(abs(ordinal - left), abs(ordinal - right))
            if not outside or distance not in (1, 2):
                continue
            amount |= span["family"] == "QUANTITY_VALUE"
            quality |= span["family"] in {"PART_STATE", "PREPARATION_VALUE"}
        part = any(abs(ordinal - index) in (1, 2) for index, _ in anchors[key])
        formula = any(abs(ordinal - index) in (1, 2) for index, _ in openers[key])
        contacts.append({"event": event, "AMOUNT": amount, "QUALITY": quality, "PART": part, "FORMULA": formula})
    expected_cells = {("AMOUNT", "L"): (4, 269, 4, 637), ("AMOUNT", "DY"): (4, 144, 1, 714),
        ("PART", "L"): (10, 263, 59, 582), ("PART", "DY"): (5, 143, 11, 704),
        ("FORMULA", "L"): (4, 269, 3, 638), ("FORMULA", "DY"): (0, 148, 1, 714),
        ("QUALITY", "L"): (0, 273, 0, 641), ("QUALITY", "DY"): (0, 148, 0, 715)}
    result: dict[str, float | int | None] = {}
    audit = []
    for kind in ("AMOUNT", "QUALITY", "PART", "FORMULA"):
        choices = []
        for axis in ("L", "DY"):
            values = [row for row in contacts if row["event"].axis == axis]
            a = sum(bool(row[kind]) and row["event"].label == 1 for row in values)
            b = sum(not bool(row[kind]) and row["event"].label == 1 for row in values)
            c = sum(bool(row[kind]) and row["event"].label == 0 for row in values)
            d = sum(not bool(row[kind]) and row["event"].label == 0 for row in values)
            if (a, b, c, d) != expected_cells[(kind, axis)]:
                raise RuntimeError(f"clean contact cell drift {kind}/{axis}: {(a,b,c,d)}")
            log_or = None if a + c == 0 else math.log(((a + .5) * (d + .5)) / ((b + .5) * (c + .5)))
            folios = len({row["event"].folio for row in values if row[kind]})
            audit.append({"contact_kind": kind, "axis": axis, "expanded_contact": a,
                "expanded_no_contact": b, "base_contact": c, "base_no_contact": d,
                "haldane_log_or": f12(log_or), "absolute_log_or": f12(abs(log_or) if log_or is not None else None),
                "contact_physical_folios": folios, "winning_axis": 0,
                "selection_credit": "AUDIT_ONLY" if kind == "FORMULA" else "TOPOLOGY_ONLY"})
            if log_or is not None:
                choices.append((abs(log_or), axis, folios))
        if choices:
            # Maximum magnitude, then lexically first axis on an exact tie.
            magnitude, winner_axis, winner_folios = sorted(choices, key=lambda item: (-item[0], item[1]))[0]
            result[f"{kind}_ABS_LOG_OR"] = magnitude
            result[f"{kind}_FOLIOS"] = winner_folios
            result[f"{kind}_WINNING_AXIS"] = winner_axis
            for row in audit:
                if row["contact_kind"] == kind and row["axis"] == winner_axis:
                    row["winning_axis"] = 1
        else:
            result[f"{kind}_ABS_LOG_OR"], result[f"{kind}_FOLIOS"], result[f"{kind}_WINNING_AXIS"] = None, 0, "NONE"
    return result, audit


def rival_card(score_lookup: Mapping[tuple[str, str], dict[str, Any]],
               contacts: Mapping[str, float | int | None], reader_stable_rate: float) -> tuple[list[dict[str, Any]], str, dict[str, float | int | None]]:
    def cm(model: str, channel: str) -> float:
        return float(score_lookup[(model, channel)]["carrier_macro_auc"])
    l_gain = cm("M01_L_TO_L", "AUGMENTED") - cm("M01_L_TO_L", "NUISANCE")
    dy_gain = cm("M02_DY_TO_DY", "AUGMENTED") - cm("M02_DY_TO_DY", "NUISANCE")
    values: dict[str, float | int | None] = {
        "MIN_WITHIN_NUISANCE_MACRO_AUC": min(cm("M01_L_TO_L", "NUISANCE"), cm("M02_DY_TO_DY", "NUISANCE")),
        "DY_LOCAL_GAIN": dy_gain, "L_LOCAL_GAIN": l_gain,
        "MIN_CROSS_SLOT_MACRO_AUC": min(cm("M03_L_TO_DY", "SLOT_HOLE"), cm("M04_DY_TO_L", "SLOT_HOLE")),
        "MIN_LOCAL_GAIN": min(l_gain, dy_gain), "QUALITY_VALUE_CONTACT_ABS_LOG_OR": contacts["QUALITY_ABS_LOG_OR"],
        "QUALITY_VALUE_CONTACT_FOLIOS": contacts["QUALITY_FOLIOS"],
        "PART_FORM_CONTACT_ABS_LOG_OR": contacts["PART_ABS_LOG_OR"], "PART_FORM_CONTACT_FOLIOS": contacts["PART_FOLIOS"],
        "AMOUNT_CONTACT_ABS_LOG_OR": contacts["AMOUNT_ABS_LOG_OR"], "AMOUNT_CONTACT_FOLIOS": contacts["AMOUNT_FOLIOS"],
        "MIN_WITHIN_TOPIC_OR_FORM_MACRO_AUC": min(max(cm("M01_L_TO_L", "TOPIC"), cm("M01_L_TO_L", "FORM_REGIME")),
                                                      max(cm("M02_DY_TO_DY", "TOPIC"), cm("M02_DY_TO_DY", "FORM_REGIME"))),
        "MAX_LOCAL_GAIN": max(l_gain, dy_gain),
        "MAX_CROSS_NUISANCE_INVERTED_AUC": max(1 - cm("M03_L_TO_DY", "NUISANCE"), 1 - cm("M04_DY_TO_L", "NUISANCE")),
        "MIN_WITHIN_FORM_MACRO_AUC": min(cm("M01_L_TO_L", "FORM_REGIME"), cm("M02_DY_TO_DY", "FORM_REGIME")),
        "MIN_TARGET_READER_STABLE_RATE": reader_stable_rate,
        "MAX_WITHIN_NUISANCE_MACRO_AUC": max(cm("M01_L_TO_L", "NUISANCE"), cm("M02_DY_TO_DY", "NUISANCE")),
        "MAX_REVERSED_CARRIER_COUNT": max(score_lookup[("M01_L_TO_L", "AUGMENTED")]["carriers_auc_below_half"],
                                              score_lookup[("M02_DY_TO_DY", "AUGMENTED")]["carriers_auc_below_half"])}
    theories = {row["rival_id"]: row for row in read_tsv(SEMANTIC_RIVAL_SPECS)}
    rules = read_tsv(RIVAL_DECISION_SPECS)
    totals: Counter[str] = Counter()
    evidence: defaultdict[str, list[str]] = defaultdict(list)
    points = []
    for rule in rules:
        value, threshold = values[rule["metric"]], float(rule["threshold"])
        passed = value is not None and (float(value) >= threshold if rule["operator"] == "GE" else float(value) < threshold)
        awarded = int(rule["points"]) if passed else 0
        totals[rule["rival_id"]] += awarded
        evidence[rule["rival_id"]].append(f"{rule['evidence_id']}={'PASS' if passed else 'FAIL'}")
        points.append({"row_type": "EVIDENCE_POINT", "rival_id": rule["rival_id"], "rank": "NA",
            "total_points": "NA", "evidence_id": rule["evidence_id"], "metric": rule["metric"],
            "observed_value": f12(float(value)) if value is not None else "NA", "operator": rule["operator"],
            "threshold": rule["threshold"], "points_available": rule["points"], "points_awarded": awarded,
            "passed": int(passed), "working_theory": theories[rule["rival_id"]]["working_theory"],
            "historical_sources": "NONE", "selection_credit": "TOPOLOGY_ONLY", "semantic_credit": 0})
    ordered = sorted(theories, key=lambda rival: (-totals[rival], rival))
    historical = read_tsv(HISTORICAL_SPECS)
    role_map = {"R01_ATTRIBUTIVE_BINDING_PLUS_PREPARATION": {"QUALITY_DEGREE", "PART_FORM_SCOPE", "RECORD_CHANNEL"},
        "R02_SHARED_FORM_STAGE": {"RELATION_SUBSTITUTE", "PART_FORM_SCOPE"},
        "R03_QUALITY_OR_DEGREE": {"QUALITY_DEGREE"}, "R04_PART_OR_FORM_SCOPE": {"PART_FORM_SCOPE"},
        "R05_GROUP_DOSE_OR_UNIT_VALUE": {"GROUP_DOSE", "UNIT_VALUE"}, "R06_RECORD_CHANNEL": {"RECORD_CHANNEL"},
        "R07_BREVIGRAPH_OR_ORTHOGRAPHY": set(), "R08_CARRIER_BOUND_LEARNED_WHOLES": set()}
    rivals = []
    for rank, rival in enumerate(ordered, 1):
        sources = [row["source_id"] for row in historical if set(row["mapped_role"].split("|")) & role_map[rival]]
        rivals.append({"row_type": "RIVAL", "rival_id": rival, "rank": rank, "total_points": totals[rival],
            "evidence_id": pipe(evidence[rival]), "metric": "POINT_TOTAL", "observed_value": totals[rival],
            "operator": "DESC", "threshold": "NA",
            "points_available": sum(int(rule["points"]) for rule in rules if rule["rival_id"] == rival),
            "points_awarded": totals[rival], "passed": "NA", "working_theory": theories[rival]["working_theory"],
            "historical_sources": pipe(sources), "selection_credit": "REPLACEABLE_WORKING_RIVAL", "semantic_credit": 0})
    source_rows = [{"row_type": "HISTORICAL_SOURCE", "rival_id": "NONE", "rank": row["rank"],
        "total_points": "NA", "evidence_id": row["source_id"], "metric": row["mapped_role"],
        "observed_value": row["attested_architecture"], "operator": "NA", "threshold": "NA",
        "points_available": 0, "points_awarded": 0, "passed": "NA", "working_theory": row["fit_to_relation"],
        "historical_sources": row["primary_url"], "selection_credit": "TOPOLOGY_ONLY", "semantic_credit": 0}
                   for row in historical]
    return rivals + points + source_rows, ordered[0], values


def decision_for_axis(model_id: str, all28_model_id: str,
                      scores: Mapping[tuple[str, str], dict[str, Any]],
                      conditional: Mapping[tuple[str, str], float | None],
                      ranks: Mapping[str, Mapping[str, Any]]) -> tuple[str, dict[str, Any]]:
    def cm(model: str, channel: str) -> float:
        return float(scores[(model, channel)]["carrier_macro_auc"])
    nuisance, augmented = cm(model_id, "NUISANCE"), cm(model_id, "AUGMENTED")
    gain = augmented - nuisance
    logloss_gain = float(scores[(model_id, "NUISANCE")]["balanced_log_loss"]) - float(scores[(model_id, "AUGMENTED")]["balanced_log_loss"])
    conditional_gain = (conditional[(model_id, "AUGMENTED")] or 0) - (conditional[(model_id, "NUISANCE")] or 0)
    slot_carriers = int(scores[(model_id, "SLOT_HOLE")]["carriers_auc_above_half"])
    all_augmented = cm(all28_model_id, "AUGMENTED")
    all_gain = all_augmented - cm(all28_model_id, "NUISANCE")
    union_gain = cm(model_id, "UNION_AUGMENTED") - cm(model_id, "UNION_NUISANCE")
    direction_gates = (augmented >= .60 and gain >= .02 and logloss_gain > 0 and slot_carriers >= 9
                       and conditional_gain >= .02 and all_augmented >= .55 and all_gain > 0)
    if direction_gates and ranks[model_id]["local_gain_rank"] == 1 and union_gain > 0:
        decision = "PORTABLE_LOCAL_SLOT_RELATION"
    elif direction_gates and (ranks[model_id]["local_gain_rank"] in {2, 3}
                              or (ranks[model_id]["local_gain_rank"] == 1 and union_gain <= 0)):
        decision = "PROVISIONAL_OR_SCORER_SENSITIVE_LOCAL_LEAD"
    elif (nuisance >= .60 and int(scores[(model_id, "NUISANCE")]["carriers_auc_above_half"]) >= 9
          and cm(all28_model_id, "NUISANCE") >= .55 and ranks[model_id]["nuisance_portability_rank"] <= 3
          and gain < .02):
        decision = "PORTABLE_RECORD_OR_FORM_RELATION"
    else:
        decision = "NO_PORTABLE_RELATION_SIGNAL"
    return decision, {"nuisance_macro_auc": nuisance, "augmented_macro_auc": augmented,
        "local_gain": gain, "fixed_logloss_gain": logloss_gain, "slot_carriers_above_half": slot_carriers,
        "conditional_gain": conditional_gain, "local_gain_rank_of_25": ranks[model_id]["local_gain_rank"],
        "nuisance_rank_of_13": ranks[model_id]["nuisance_portability_rank"],
        "all28_augmented_macro_auc": all_augmented, "all28_local_gain": all_gain,
        "union_local_gain": union_gain, "direction_gates_pass": int(direction_gates)}


def joint_topology(l_decision: str, dy_decision: str,
                   scores: Mapping[tuple[str, str], dict[str, Any]]) -> str:
    transfers = [value != "NO_PORTABLE_RELATION_SIGNAL" for value in (l_decision, dy_decision)]
    cross_slot = [float(scores[(model, "SLOT_HOLE")]["carrier_macro_auc"])
                  for model in ("M03_L_TO_DY", "M04_DY_TO_L")]
    cross_nuisance = [float(scores[(model, "NUISANCE")]["carrier_macro_auc"])
                      for model in ("M03_L_TO_DY", "M04_DY_TO_L")]
    if all(transfers) and min(cross_slot) >= .60:
        return "SHARED_EXPANDED_SIDE_DIRECTION"
    if all(transfers) and max(cross_slot) <= .40:
        return "OPPOSED_LOCAL_RELATIONS"
    if all(transfers) and max(cross_nuisance) <= .40:
        return "OPPOSED_REGISTER_DIRECTIONS__NO_SHARED_SLOT_INFERENCE"
    if all(transfers):
        return "TWO_DISTINCT_OR_AXIS_BOUND_RELATIONS"
    if any(transfers):
        return "ONE_AXIS_TRANSFERABLE_RELATION"
    return "NO_PORTABLE_RELATION_SIGNAL"


def edge_packet(core_events: Sequence[Event]) -> list[dict[str, Any]]:
    output = []
    for carrier in sorted({event.carrier for event in core_events}):
        for axis in ("L", "DY"):
            values = [event for event in core_events if event.carrier == carrier and event.axis == axis]
            expanded, base = next(event for event in values if event.label), next(event for event in values if not event.label)
            output.append({"edge_id": f"G808E{len(output) + 1:04d}", "batch_id": "GDT808_EXACT_FORMAL_RECTANGLE",
                "page": expanded.page, "physical_folio": leaf_folio(expanded.page),
                "diagram_unit_id": f"FORMAL_RECTANGLE_{carrier}_{axis}",
                "pivot_visual_id": f"EXACT_BASE_{base.surface}", "pivot_locus": f"{base.locus}@{base.token_index}",
                "target_visual_id": f"EXACT_EXPANDED_{expanded.surface}",
                "target_locus": f"{expanded.locus}@{expanded.token_index}",
                "relation_type": f"FORMAL_{axis}_BASE_TO_EXPANDED",
                "direction_basis": "REGISTERED_EXACT_SURFACE_AXIS",
                "ownership_basis": "ANALYST_CARRIER_RECTANGLE_NOT_IMAGE_OWNERSHIP",
                "geometry_only_selection": "FALSE", "source_manifest_id": "GDT808",
                "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
                "source_aware_localizer": "GDT808_GUARDED_TRANSCRIPTION_BUILDER",
                "relation_reviewer": "PENDING_EXTERNAL",
                "relation_confidence": "EXACT_FORMAL_SURFACE_PAIR_ZERO_SEMANTIC_CREDIT",
                "ambiguity_state": "FORMAL_TEXT_RELATION_NOT_AUTHORIAL_VISUAL_EDGE",
                "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "COMPONENT_AND_PHYSICAL_FOLIO_HELD",
                "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION"})
    return output


def run_edge_intake(packet: Path, output: Path, expected_rows: int) -> dict[str, Any]:
    completed = subprocess.run([str(VMANUS_EXP), "check-edge-packet", str(packet)], cwd=ROOT,
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 1 or completed.stderr:
        raise RuntimeError(f"GDT388 intake drift rc={completed.returncode}: {completed.stderr}")
    result = json.loads(completed.stdout)
    if (result.get("status") != "INVALID_PACKET" or result.get("packet_rows") != expected_rows
            or result.get("eligible_edges") != 0 or result.get("score_ready") is not False):
        raise RuntimeError("GDT388 packet did not fail closed")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def source_lock() -> list[dict[str, Any]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["experiment_id"] != "GDT808" or manifest["sealed_data"] != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise RuntimeError("manifest identity/sealed state drift")
    raw_paths = {rel(LINES_RAW), rel(CROSS_RAW), rel(TOKENS_RAW)}
    output = []
    for item in manifest["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise RuntimeError(f"manifest input hash drift: {item['path']}")
        output.append({"path": item["path"], "sha256": item["sha256"], "purpose": item["role"],
            "access_mode": "MANIFEST_HASH__MIXED_TSV_GUARDED_ONLY" if item["path"] in raw_paths else "DIRECT_SAFE_INPUT",
            "manifest_hash_match": 1})
    for path, purpose in ((RUN, "official GDT808 builder"), (VMANUS_EXP, "guarded query and edge dispatcher"),
                          (GUARDED_TOOL, "selector-before-materialization guard"), (EDGE_TOOL, "GDT388 packet intake")):
        output.append({"path": rel(path), "sha256": sha256(path), "purpose": purpose,
                       "access_mode": "RUNTIME_IMPLEMENTATION", "manifest_hash_match": "NA"})
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()

    raw35, all28, core13, thin9, overlap6 = spec_sets()
    lines, paragraphs, paragraph_by_locus, query_stats, token_rows = load_corpus()
    carrier_rows, _ = carrier_census(lines, raw35, all28, core13)
    q152, q_rows = build_q152(raw35, thin9, overlap6)
    all_events = collect_events(lines, paragraphs, paragraph_by_locus, set(all28))
    core_events = [event for event in all_events if event.carrier in core13]
    if len(all_events) != 2208 or Counter(event.tail for event in all_events) != EXPECTED_ALL28_TAILS:
        raise RuntimeError(f"ALL28 event drift: {len(all_events)} {Counter(event.tail for event in all_events)}")
    if len(core_events) != 1777 or Counter(event.tail for event in core_events) != EXPECTED_CORE_TAILS:
        raise RuntimeError(f"CORE13 event drift: {len(core_events)} {Counter(event.tail for event in core_events)}")
    if (len({event.paragraph.paragraph_id for event in core_events}), len({(event.page, event.locus) for event in core_events}),
            len({event.folio for event in core_events})) != (559, 1403, 169):
        raise RuntimeError("CORE13 paragraph/line/folio capacity drift")
    if (len({event.paragraph.paragraph_id for event in all_events}), len({(event.page, event.locus) for event in all_events}),
            len({event.folio for event in all_events})) != (596, 1643, 169):
        raise RuntimeError("ALL28 paragraph/line/folio capacity drift")
    for row in carrier_rows:
        row["eligible_events"] = sum(event.carrier == row["carrier"] for event in all_events)
        for tail in TAILS:
            row[f"{tail}_eligible_events"] = sum(event.carrier == row["carrier"] and event.tail == tail for event in all_events)

    stages = stage_census(lines, paragraph_by_locus, set(core13), "CORE13") + stage_census(lines, paragraph_by_locus, set(all28), "ALL28")
    core_stage = {row["item"].split("_")[0]: row for row in stages if row["scope"] == "CORE13"}
    reader_stable_rate = min(float(core_stage[axis]["rank_stable_rate_strict_prefilter"]) for axis in ("L", "DY"))
    observed_surfaces = {surface for line in lines for surface in line.tokens}
    ed1 = frozenset(surface for surface in observed_surfaces if surface not in q152
                    and any(levenshtein(surface, quarantined) <= 1 for quarantined in q152))
    end_classes = sorted({surface[-1] for surface in observed_surfaces if surface})
    attach_features(all_events, q152, ed1, end_classes)

    model_specs = read_tsv(MODEL_SPECS)
    predictions, fold_rows = [], []
    for spec in model_specs:
        population = core_events if spec["population"] == "CORE13" else all_events
        values, folds = run_relation_model(spec, population, auxiliary=True)
        predictions.extend(values)
        fold_rows.extend(folds)
    summary_rows, score_lookup = score_summary(model_specs, predictions)
    conditional_rows, conditional_lookup = make_conditional_rows(model_specs, predictions)
    primary_specs = [spec for spec in model_specs if spec["model_id"] in {"M01_L_TO_L", "M02_DY_TO_DY"}]
    null_rows, null_audits, ranks = null_experiments(primary_specs, core_events, predictions, score_lookup, conditional_lookup)

    ed1_predictions = []
    for spec in primary_specs:
        values, _ = run_relation_model(spec, core_events, variant="ED1", auxiliary=False)
        ed1_predictions.extend(values)
    ed1_summary, _ = score_summary(primary_specs, ed1_predictions)

    thin_pairs = {carrier: (carrier + "kol", carrier + "tal") for carrier in thin9}
    thin_events = collect_pair_events(lines, paragraphs, paragraph_by_locus, thin_pairs, "THIN")
    attach_features(thin_events, q152, ed1, end_classes)
    thin_rows = custom_control_scores(thin_events, "COMPONENT_AND_FOLIO_HELD")
    learned_events = collect_pair_events(lines, paragraphs, paragraph_by_locus,
                                         {"LEARNED_PAIR": ("cheol", "otal")}, "LEARNED")
    for event in learned_events:
        event.carrier = event.surface
    attach_features(learned_events, q152, ed1, end_classes)
    learned_rows = custom_control_scores(learned_events, "LEAVE_ONE_PHYSICAL_FOLIO_OUT")

    contacts, contact_audit = clean_contact_metrics(core_events, q152)
    historical_rows, leading_rival, rival_metrics = rival_card(score_lookup, contacts, reader_stable_rate)
    for row in contact_audit:
        historical_rows.append({"row_type": "CONTACT_AUDIT", "rival_id": "NONE", "rank": "NA",
            "total_points": "NA", "evidence_id": f"{row['contact_kind']}_{row['axis']}",
            "metric": "CLEAN_EXACT_ORDINAL_CONTACT", "observed_value": row["absolute_log_or"],
            "operator": "NA", "threshold": "NA", "points_available": 0, "points_awarded": 0,
            "passed": "NA", "working_theory": json.dumps(row, sort_keys=True, separators=(",", ":")),
            "historical_sources": "NONE", "selection_credit": row["selection_credit"], "semantic_credit": 0})

    l_decision, l_values = decision_for_axis("M01_L_TO_L", "M05_L_TO_L_ALL28", score_lookup, conditional_lookup, ranks)
    dy_decision, dy_values = decision_for_axis("M02_DY_TO_DY", "M06_DY_TO_DY_ALL28", score_lookup, conditional_lookup, ranks)
    topology = joint_topology(l_decision, dy_decision, score_lookup)

    event_rows = [{"event_id": event.event_id, "carrier": event.carrier, "tail": event.tail,
        "axis": event.axis, "expanded_label": event.label, "surface": event.surface, "page": event.page,
        "physical_folio": event.folio, "paragraph_id": event.paragraph.paragraph_id, "locus": event.locus,
        "line_number": event.line_number, "token_index": event.token_index, "line_token_count": len(event.line.tokens),
        "paragraph_line_index": event.paragraph_line_index, "section": event.paragraph.section,
        "language": event.paragraph.language, "hand": event.paragraph.hand, "rank_stable_all_three": 1,
        "it2a_unique_forced_exact_ordinal": event.it2a_ordinal,
        "rf1b_unique_forced_exact_ordinal": event.rf1b_ordinal, "own_family_raw_line_count": 1,
        "targetfree_line_length_bin": event.targetfree_line_length_bin,
        "topic_features": pipe(sorted(event.features["TOPIC"])),
        "template_features": pipe(sorted(event.features["TEMPLATE"])),
        "form_regime_features": pipe(sorted(event.features["FORM_REGIME"])),
        "slot_hole_features": pipe(sorted(event.features["SLOT_HOLE"])),
        "mask_status_audit_features": pipe(sorted(event.features["MASK_STATUS"])),
        "raw_slot_sensitivity_features": pipe(sorted(event.features["RAW_SLOT"])),
        "semantic_credit": 0, "component_export_credit": 0} for event in core_events]

    census_rows = [
        {"scope": "ALLOWLIST", "item": "selectors", "count": len({line.page for line in lines}), "expected": 179, "status": "PASS"},
        {"scope": "GUARDED_SOURCE", "item": "lines", "count": len(lines), "expected": 4137, "status": "PASS"},
        {"scope": "GUARDED_SOURCE", "item": "tokens", "count": len(token_rows), "expected": 32339, "status": "PASS"},
        {"scope": "STRICT", "item": "paragraphs", "count": len(paragraphs), "expected": 665, "status": "PASS"},
        {"scope": "STRICT", "item": "lines", "count": sum(len(p.lines) for p in paragraphs), "expected": 3807, "status": "PASS"},
        {"scope": "STRICT", "item": "tokens", "count": sum(len(line.tokens) for p in paragraphs for line in p.lines), "expected": 31938, "status": "PASS"},
        {"scope": "CORE13", "item": "eligible_events", "count": len(core_events), "expected": 1777, "status": "PASS"},
        {"scope": "ALL28", "item": "eligible_events", "count": len(all_events), "expected": 2208, "status": "PASS"},
        {"scope": "Q152", "item": "exact_surfaces", "count": len(q152), "expected": 152, "status": "PASS"},
        {"scope": "ED1", "item": "additional_observed_surfaces", "count": len(ed1), "expected": "NA", "status": "AUDIT"}]
    census_rows.extend(stages)
    clarifications = [
        {"issue": "FORM_REGIME_POSITION", "resolution": "Position geometry is primary FORM_REGIME and separately audited; FORM_BASE omits it.", "selection_credit": "PRIMARY_AND_AUDIT"},
        {"issue": "HISTOGRAM_SCOPE", "resolution": "Word-length and end-class buckets are separate for target-free focal line and strict paragraph.", "selection_credit": "PRIMARY"},
        {"issue": "CONDITIONAL_AGGREGATION", "resolution": "Same-stratum pairs pool within carrier, then carrier concordances macro-average; pooled-all-pair result is audit only.", "selection_credit": "PRIMARY"},
        {"issue": "UNION_SUPPORT", "resolution": "Union MNB uses the same two-carrier and two-physical-folio support gate.", "selection_credit": "REQUIRED_SENSITIVITY"},
        {"issue": "LEARNED_CONTROL_SUPPORT", "resolution": "cheol and otal are descriptive class-carrier identities for support/cell weighting; only physical folio is held.", "selection_credit": "CALIBRATION_ONLY"},
        {"issue": "OVERLAY_SELF_EXCLUSION", "resolution": "Exact page+locus+ordinal join; nonzero outside-span distance; every overlay surface Q152-clean; winning-axis folios coupled.", "selection_credit": "TOPOLOGY_ONLY"},
        {"issue": "READER_STABILITY", "resolution": "Minimum strict parsed CORE13 axis stable rate is measured before stable/LCS/singleton filters.", "selection_credit": "TOPOLOGY_ONLY"},
        {"issue": "GDT388_PACKET", "resolution": "One formal pair per CORE13 carrier/axis must fail closed as formally accessed nonvisual evidence.", "selection_credit": "AUDIT_ONLY"}]
    feature_rows = feature_capacity(core_events, "CORE13") + feature_capacity(all_events, "ALL28")
    ablations = ablation_rows(primary_specs, predictions)
    directions = carrier_direction_rows(model_specs, predictions)
    all28_rows = [row for row in summary_rows if row["population"] == "ALL28"]
    structural_rows = [
        {"card_id": "L_AXIS", "formal_scope": "Xol::Xeol", "decision": l_decision,
         "joint_topology": topology, "leading_historical_rival": leading_rival,
         "metrics_json": json.dumps(l_values, sort_keys=True, separators=(",", ":")),
         "claim_ceiling": "FORMAL_RELATION_ONLY", "semantic_credit": 0, "renderer_credit": 0},
        {"card_id": "DY_AXIS", "formal_scope": "Xedy::Xeody", "decision": dy_decision,
         "joint_topology": topology, "leading_historical_rival": leading_rival,
         "metrics_json": json.dumps(dy_values, sort_keys=True, separators=(",", ":")),
         "claim_ceiling": "FORMAL_RELATION_ONLY", "semantic_credit": 0, "renderer_credit": 0},
        {"card_id": "JOINT", "formal_scope": "L_AND_DY_RECTANGLE", "decision": topology,
         "joint_topology": topology, "leading_historical_rival": leading_rival,
         "metrics_json": json.dumps(rival_metrics, sort_keys=True, separators=(",", ":")),
         "claim_ceiling": "ZERO_LEXEMES_ZERO_COMPONENT_EXPORT", "semantic_credit": 0, "renderer_credit": 0}]

    write_tsv(output_dir / "GDT808_IMPLEMENTATION_CLARIFICATIONS.tsv", clarifications)
    write_tsv(output_dir / "GDT808_GUARDED_QUERY_STATS.tsv", query_stats)
    write_tsv(output_dir / "GDT808_SOURCE_CENSUS.tsv", census_rows)
    write_tsv(output_dir / "GDT808_RAW35_ALL28_CORE13_CARRIER_CENSUS.tsv", carrier_rows)
    write_tsv(output_dir / "GDT808_Q152_EXACT_QUARANTINE.tsv", q_rows)
    write_tsv(output_dir / "GDT808_1777_CORE_EVENT_ATLAS.tsv", event_rows)
    write_tsv(output_dir / "GDT808_FEATURE_DECK_CAPACITY.tsv", feature_rows)
    write_tsv(output_dir / "GDT808_COMPONENT_HELD_FOLDS.tsv", fold_rows)
    write_tsv(output_dir / "GDT808_HELD_PREDICTIONS.tsv", predictions)
    write_tsv(output_dir / "GDT808_DECK_SCORE_SUMMARY.tsv", summary_rows)
    write_tsv(output_dir / "GDT808_CONDITIONAL_CONCORDANCE.tsv", conditional_rows)
    write_tsv(output_dir / "GDT808_POSITION_MASK_SLOT_ABLATIONS.tsv", ablations)
    write_tsv(output_dir / "GDT808_CARRIER_DIRECTION_DIAGNOSTICS.tsv", directions)
    write_tsv(output_dir / "GDT808_NULL_STRATUM_AUDIT.tsv", null_audits)
    write_tsv(output_dir / "GDT808_NULL_SCORES.tsv", null_rows)
    write_tsv(output_dir / "GDT808_ALL28_SENSITIVITY.tsv", all28_rows)
    write_tsv(output_dir / "GDT808_ED1_SENSITIVITY.tsv", ed1_summary)
    write_tsv(output_dir / "GDT808_THIN_KOL_TAL.tsv", thin_rows)
    write_tsv(output_dir / "GDT808_LEARNED_CHEOL_OTAL.tsv", learned_rows)
    write_tsv(output_dir / "GDT808_HISTORICAL_RIVAL_CARD.tsv", historical_rows)
    write_tsv(output_dir / "GDT808_STRUCTURAL_CARD.tsv", structural_rows)
    write_tsv(output_dir / "SOURCE_LOCK.tsv", source_lock())

    edges = edge_packet(core_events)
    packet = output_dir / "GDT808_GDT388_RELATION_PACKET.tsv"
    write_tsv(packet, edges, EDGE_FIELDS)
    intake = run_edge_intake(packet, output_dir / "GDT808_GDT388_EDGE_INTAKE.json", len(edges))
    artifact_hashes = {(rel(path) if path.is_relative_to(ROOT) else path.name): sha256(path)
                       for path in sorted(output_dir.iterdir()) if path.name in OUTPUT_NAMES and path.name != "RESULT.json"}
    result = {"experiment_id": "GDT808", "status": f"{topology}__L_{l_decision}__DY_{dy_decision}",
        "runtime_seconds": round(time.time() - started, 6), "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "counts": {"strict_paragraphs": len(paragraphs), "raw_complete_carriers": len(raw35),
            "all28_carriers": len(all28), "core13_carriers": len(core13), "q152_surfaces": len(q152),
            "ed1_additional_surfaces": len(ed1), "core_events": len(core_events), "all28_events": len(all_events),
            "core_event_paragraphs": len({event.paragraph.paragraph_id for event in core_events}),
            "core_event_focal_lines": len({(event.page, event.locus) for event in core_events}),
            "core_event_physical_folios": len({event.folio for event in core_events}),
            "held_predictions": len(predictions), "held_folds": len(fold_rows), "thin_events": len(thin_events),
            "learned_events": len(learned_events), "target_rotation_models": 2, "target_rotations_each": 24,
            "carrier_null_models": 2, "carrier_null_repetitions_each": 12, "gdt388_packet_rows": len(edges)},
        "axis_decisions": {"L": {"decision": l_decision, **l_values}, "DY": {"decision": dy_decision, **dy_values}},
        "joint_topology": topology, "leading_historical_rival": leading_rival,
        "reader_stable_rate_strict_prefilter_min_axis": reader_stable_rate,
        "clean_contacts": contacts,
        "gdt388_intake": {"status": intake["status"], "eligible_edges": intake["eligible_edges"], "score_ready": intake["score_ready"]},
        "claim_ceiling": "formal carrier-held relations and zero-semantic role-family ranking only; zero lexemes, component values, plaintext, translation, or renderer credit",
        "artifact_sha256": artifact_hashes}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name in OUTPUT_NAMES:
        path = output_dir / name
        if not path.is_file():
            raise RuntimeError(f"missing output: {name}")
        if path.stat().st_size >= 5_000_000:
            raise RuntimeError(f"artifact exceeds 5 MB: {name}={path.stat().st_size}")
    print(json.dumps({"status": result["status"], "runtime_seconds": result["runtime_seconds"],
                      "core_events": len(core_events), "all28_events": len(all_events),
                      "held_predictions": len(predictions), "leading_rival": leading_rival}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
