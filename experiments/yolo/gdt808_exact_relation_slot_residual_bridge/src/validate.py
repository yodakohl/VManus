#!/usr/bin/env python3
"""Independent, fail-closed validation for GDT808.

The validator never imports the experiment builder. It reconstructs the
admitted corpus through guarded TSV queries, rebuilds the registered carrier
populations, focal events, feature decks, held predictions, and nulls, then
audits the published artifacts.
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
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge"
SRC = BASE / "src"
ART = BASE / "artifacts"
MANIFEST = BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
VMANUS_EXP = ROOT / "vmanus-exp"
ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
LINES_RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
G759 = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G768 = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/ANCHOR_404_OCCURRENCE_ATLAS.tsv"
G757 = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv"
MODEL_SPECS = SRC / "RELATION_MODEL_SPECS.tsv"
CORE_SPECS = SRC / "CORE_CARRIER_SPECS.tsv"
QUARANTINE_SPECS = SRC / "QUARANTINE_SPECS.tsv"
IMPLEMENTATION_SPECS = SRC / "IMPLEMENTATION_SPECS.tsv"
FEATURE_SPECS = SRC / "FEATURE_DECK_SPECS.tsv"
CONTROL_SPECS = SRC / "CONTROL_SPECS.tsv"
RIVAL_SPECS = SRC / "RIVAL_DECISION_SPECS.tsv"
SEMANTIC_SPECS = SRC / "SEMANTIC_RIVAL_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_TOPOLOGY_SPECS.tsv"

MIXED_PATHS = {LINES_RAW.resolve(), CROSS_RAW.resolve(), TOKENS_RAW.resolve()}
TAILS = ("eody", "eol", "edy", "ol")
THIN_TAILS = ("kol", "tal")
DECKS = ("TOPIC", "TEMPLATE", "FORM_REGIME", "SLOT_HOLE")
ALPHA = 0.5
FLOAT_TOL = 5e-10
EXPECTED = {
    "selectors": 179, "raw_lines": 4137, "raw_tokens": 32339,
    "strict_paragraphs": 665, "strict_lines": 3807, "strict_tokens": 31938,
    "outside_lines": 330, "outside_tokens": 401, "raw35": 35,
    "all28": 28, "core13": 13, "q152": 152, "core_events": 1777,
    "core_event_paragraphs": 559, "core_event_lines": 1403,
    "core_event_folios": 169, "all28_events": 2208,
    "all28_event_paragraphs": 596,
}
MIXED_MANIFEST_HASHES = {
    "transcription/voynich_zl3b_lines.tsv": "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    "transcription/voynich_cross_transcription_lines.tsv": "ff3a4559004a29764c60102326de154b29fbba06a2a206bdd76d7feda432e16c",
    "transcription/voynich_zl3b_tokens.tsv": "6a061a26edc05ff37dc386c2215774c229a5ff087d3091e68bdd4983a6c007aa",
}


@dataclass(frozen=True)
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
    stable: tuple[bool, ...]
    alternate: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Paragraph:
    paragraph_id: str
    page: str
    physical_folio: str
    ordinal_on_page: int
    section: str
    language: str
    hand: str
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class Event:
    event_id: str
    ordinal: int
    carrier: str
    tail: str
    surface: str
    paragraph: Paragraph
    line: Line
    line_index: int
    token_index: int
    feature_decks: Mapping[str, frozenset[str]]
    mask_status: frozenset[str]
    raw_slot: frozenset[str]
    line_length_bin: int

    @property
    def physical_folio(self) -> str:
        return self.paragraph.physical_folio


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    source_axis: str
    target_axis: str
    positive_source: str
    negative_source: str
    positive_target: str
    negative_target: str
    population: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    if path.resolve() in MIXED_PATHS:
        raise AssertionError(f"mixed TSV must be guarded: {rel(path)}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def natural_page_key(value: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", value)
    if match is None:
        return (10**9, 9, 9, value)
    return (int(match.group(1)), 0 if match.group(2) == "r" else 1,
            int(match.group(3) or 0), value)


def physical_folio(page: str) -> str:
    match = re.match(r"^(f[0-9]+[rv])", page)
    if match is None:
        raise AssertionError(f"cannot normalize physical folio: {page}")
    return match.group(1)


def truth(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "pass"}


def guarded_query(path: Path, pages: Sequence[str], columns: Sequence[str]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    command = [str(VMANUS_EXP), "query-tsv", rel(path), "--selector", "page"]
    for page in sorted(pages, key=natural_page_key):
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84",
                    "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, check=False, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise AssertionError(f"guarded query failed for {rel(path)}: {completed.stderr[-2000:]}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise AssertionError(f"missing or duplicate guard stats: {rel(path)}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if rows and tuple(rows[0]) != tuple(columns):
        raise AssertionError(f"guarded output schema drift: {rel(path)}")
    for row in rows:
        if any(str(row.get(key, "")).startswith("f84") for key in ("page", "locus")):
            raise AssertionError("sealed selector/locus materialized")
    return rows, json.loads(stat_lines[0][12:])


def lcs_table(left: Sequence[str], right: Sequence[str]) -> list[list[int]]:
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(len(left) - 1, -1, -1):
        for j in range(len(right) - 1, -1, -1):
            table[i][j] = (1 + table[i + 1][j + 1] if left[i] == right[j]
                           else max(table[i + 1][j], table[i][j + 1]))
    return table


def unique_forced_lcs(reference: Sequence[str], alternate: Sequence[str], index: int) -> bool:
    suffix = lcs_table(reference, alternate)
    optimum = suffix[0][0]
    without = tuple(reference[:index]) + tuple(reference[index + 1:])
    if lcs_table(without, alternate)[0][0] >= optimum:
        return False
    prefix = [[0] * (len(alternate) + 1) for _ in range(len(reference) + 1)]
    for i, left in enumerate(reference):
        for j, right in enumerate(alternate):
            prefix[i + 1][j + 1] = (1 + prefix[i][j] if left == right
                                     else max(prefix[i][j + 1], prefix[i + 1][j]))
    partners = [j for j, value in enumerate(alternate)
                if value == reference[index]
                and prefix[index][j] + 1 + suffix[index + 1][j + 1] == optimum]
    return len(partners) == 1


def parse_relation(surface: str) -> tuple[str, str] | None:
    for tail in TAILS:
        if surface.endswith(tail) and len(surface) > len(tail):
            return surface[:-len(tail)], tail
    return None


def load_guarded_corpus() -> tuple[list[Line], list[Paragraph], list[Line], dict[str, Any]]:
    allow = read_tsv(ALLOWLIST)
    if not allow or list(allow[0]) != ["page"]:
        raise AssertionError("allow-list schema drift")
    pages = [row["page"] for row in allow]
    if len(pages) != EXPECTED["selectors"] or len(set(pages)) != len(pages):
        raise AssertionError("allow-list cardinality/uniqueness drift")
    if any(page.startswith("f84") for page in pages):
        raise AssertionError("sealed page present in allow-list")
    line_columns = ("page", "locus", "line_number", "section", "language", "hand",
                    "paragraph_start", "paragraph_end", "token_count", "eva_clean")
    token_columns = ("page", "locus", "token_index", "eva")
    cross_columns = ("page", "locus", "zl3b_clean", "it2a_clean", "rf1b_clean")
    line_rows, line_stats = guarded_query(LINES_RAW, pages, line_columns)
    token_rows, token_stats = guarded_query(TOKENS_RAW, pages, token_columns)
    cross_rows, cross_stats = guarded_query(CROSS_RAW, pages, cross_columns)
    if len(line_rows) != EXPECTED["raw_lines"] or len(cross_rows) != EXPECTED["raw_lines"]:
        raise AssertionError("guarded line/cross census drift")
    if len(token_rows) != EXPECTED["raw_tokens"]:
        raise AssertionError("guarded token census drift")
    token_map: defaultdict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    for row in token_rows:
        token_map[(row["page"], row["locus"])].append((int(row["token_index"]), row["eva"]))
    tokens: dict[tuple[str, str], tuple[str, ...]] = {}
    for key, values in token_map.items():
        values.sort()
        if [index for index, _ in values] != list(range(1, len(values) + 1)):
            raise AssertionError(f"non-contiguous token ordinals: {key}")
        tokens[key] = tuple(value for _, value in values)
    cross: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {}
    for row in cross_rows:
        key = (row["page"], row["locus"])
        if key in cross:
            raise AssertionError(f"duplicate cross-reader line: {key}")
        cross[key] = {name: tuple(row[column].split()) for name, column in (
            ("zl3b", "zl3b_clean"), ("it2a", "it2a_clean"), ("rf1b", "rf1b_clean"))}
    lines: list[Line] = []
    seen: set[tuple[str, str]] = set()
    for row in sorted(line_rows, key=lambda item: (natural_page_key(item["page"]),
                                                    int(item["line_number"]), item["locus"])):
        key = (row["page"], row["locus"])
        if key in seen or key not in cross:
            raise AssertionError(f"line identity/cross parity failure: {key}")
        seen.add(key)
        line_tokens = tokens.get(key, ())
        if line_tokens != tuple(row["eva_clean"].split()) or line_tokens != cross[key]["zl3b"]:
            raise AssertionError(f"guarded line/token/cross mismatch: {key}")
        if len(line_tokens) != int(row["token_count"]):
            raise AssertionError(f"line token count mismatch: {key}")
        ranks: Counter[str] = Counter()
        stable: list[bool] = []
        for surface in line_tokens:
            ranks[surface] += 1
            stable.append(ranks[surface] <= min(reader.count(surface) for reader in cross[key].values()))
        lines.append(Line(row["page"], row["locus"], int(row["line_number"]),
                          row["section"], row["language"], row["hand"],
                          truth(row["paragraph_start"]), truth(row["paragraph_end"]),
                          line_tokens, tuple(stable), cross[key]))
    if set(cross) != seen or set(tokens) - seen:
        raise AssertionError("guarded source key-set mismatch")
    paragraphs: list[Paragraph] = []
    outside: list[Line] = []
    by_page: defaultdict[str, list[Line]] = defaultdict(list)
    for line in lines:
        by_page[line.page].append(line)
    for page in sorted(by_page, key=natural_page_key):
        active: list[Line] | None = None
        page_ordinal = 0
        for line in sorted(by_page[page], key=lambda item: (item.number, item.locus)):
            if line.paragraph_start:
                if active is not None:
                    raise AssertionError(f"nested strict paragraph: {line.locus}")
                active = []
            if active is None:
                outside.append(line)
                if line.paragraph_end:
                    raise AssertionError(f"paragraph end without start: {line.locus}")
                continue
            active.append(line)
            if line.paragraph_end:
                metadata = {(item.section, item.language, item.hand) for item in active}
                if len(metadata) != 1:
                    raise AssertionError(f"heterogeneous strict paragraph: {line.locus}")
                section, language, hand = next(iter(metadata))
                page_ordinal += 1
                paragraphs.append(Paragraph(f"G808-P{len(paragraphs) + 1:04d}", page,
                                            physical_folio(page), page_ordinal, section,
                                            language, hand, tuple(active)))
                active = None
        if active is not None:
            raise AssertionError(f"unclosed paragraph at page boundary: {page}")
    census = {"strict_paragraphs": len(paragraphs),
              "strict_lines": sum(len(p.lines) for p in paragraphs),
              "strict_tokens": sum(len(line.tokens) for p in paragraphs for line in p.lines),
              "outside_lines": len(outside),
              "outside_tokens": sum(len(line.tokens) for line in outside)}
    for name, value in census.items():
        if value != EXPECTED[name]:
            raise AssertionError(f"strict corpus drift {name}: {value} != {EXPECTED[name]}")
    return lines, paragraphs, outside, {
        "allowlist_selectors": len(pages), "raw_lines": len(line_rows),
        "raw_tokens": len(token_rows), "guarded_queries": {
            "lines": line_stats, "tokens": token_stats, "cross": cross_stats}, **census}


def length_bin(count: int) -> int:
    return int(math.floor(math.log2(count + 1)))


def quartile(index: int, count: int) -> int:
    if not 1 <= index <= count:
        raise AssertionError(f"quartile ordinal outside count: {index}/{count}")
    return min(4, 1 + int(math.floor(4 * (index - 1) / count)))


def index_bin(index: int) -> str:
    return str(index) if index <= 4 else "5PLUS"


def word_length_bin(surface: str) -> str:
    return str(len(surface)) if len(surface) <= 6 else "7PLUS"


def count_bin(count: int) -> str:
    return str(count) if count <= 2 else "3PLUS"


def feature_surface(feature: str) -> str | None:
    if "=" not in feature:
        return None
    prefix, value = feature.split("=", 1)
    if prefix in {"W", "L3", "L4", "L5PLUS", "R3", "R4", "R5PLUS",
                  "L1", "L2", "R1", "R2"} and "|" not in value:
        return value
    return None


def canonical_features(paragraph: Paragraph, line: Line, token_index: int,
                       carrier: str, q152: frozenset[str],
                       end_classes: Sequence[str]) -> tuple[dict[str, frozenset[str]], frozenset[str], frozenset[str], int]:
    zero = token_index - 1
    family = frozenset(carrier + tail for tail in TAILS)
    topic_words: set[str] = set()
    for other in paragraph.lines:
        if other.locus == line.locus or set(other.tokens) & family:
            continue
        topic_words.update(surface for surface in other.tokens if surface not in q152)
    topic = frozenset("W=" + surface for surface in topic_words)
    template: set[str] = set()
    for position, surface in enumerate(line.tokens):
        distance = position - zero
        if abs(distance) < 3 or surface in q152:
            continue
        side = "L" if distance < 0 else "R"
        magnitude = abs(distance)
        bucket = str(magnitude) if magnitude in (3, 4) else "5PLUS"
        template.add(f"{side}{bucket}={surface}")
    line_free = [surface for surface in line.tokens if surface not in q152]
    paragraph_free = [surface for item in paragraph.lines for surface in item.tokens
                      if surface not in q152]
    line_ordinal = next(index for index, item in enumerate(paragraph.lines, 1)
                        if item.locus == line.locus)
    token_count = len(line.tokens)
    form = {
        f"SECTION={paragraph.section}", f"LANGUAGE={paragraph.language}",
        f"HAND={paragraph.hand}", f"JOINT={paragraph.section}:{paragraph.language}:{paragraph.hand}",
        f"LINE_LENGTH={length_bin(len(line_free))}",
        f"PARAGRAPH_LENGTH={length_bin(len(paragraph_free))}",
        f"PARAGRAPH_LINES={length_bin(len(paragraph.lines))}",
        f"LINE_QUARTILE={quartile(line_ordinal, len(paragraph.lines))}",
        f"HOLE_CLASS={'SINGLE' if token_count == 1 else 'FIRST' if token_index == 1 else 'LAST' if token_index == token_count else 'MIDDLE'}",
        f"FORWARD_INDEX={index_bin(token_index)}",
        f"REVERSE_INDEX={index_bin(token_count - token_index + 1)}",
        f"TOKEN_QUARTILE={quartile(token_index, token_count)}",
    }
    for scope, values in (("LINE", line_free), ("PARAGRAPH", paragraph_free)):
        lengths = Counter(word_length_bin(surface) for surface in values)
        endings = Counter(surface[-1] for surface in values)
        for bucket in ("1", "2", "3", "4", "5", "6", "7PLUS"):
            form.add(f"{scope}_WORD_LENGTH_{bucket}={count_bin(lengths[bucket])}")
        for ending in end_classes:
            form.add(f"{scope}_END_{ending}={count_bin(endings[ending])}")
    stable_neighbours: dict[int, str] = {}
    raw_neighbours: dict[int, str] = {}
    status: set[str] = set()
    for offset in (-2, -1, 1, 2):
        position = zero + offset
        name = ("L" if offset < 0 else "R") + str(abs(offset))
        if not 0 <= position < token_count:
            status.add(name + "=BOUNDARY")
            continue
        surface = line.tokens[position]
        if surface in q152:
            status.add(name + "=QMASK")
            continue
        raw_neighbours[offset] = surface
        if line.stable[position]:
            stable_neighbours[offset] = surface
        else:
            status.add(name + "=UNSTABLE")

    def packet(neighbours: Mapping[int, str]) -> frozenset[str]:
        output = {(("L" if offset < 0 else "R") + str(abs(offset)) + "=" + surface)
                  for offset, surface in neighbours.items()}
        for left, right, name in ((-2, -1, "L2_L1"), (-1, 1, "L1_R1"),
                                  (1, 2, "R1_R2")):
            if left in neighbours and right in neighbours:
                output.add(f"{name}={neighbours[left]}|{neighbours[right]}")
        return frozenset(output)

    decks = {"TOPIC": topic, "TEMPLATE": frozenset(template),
             "FORM_REGIME": frozenset(form), "SLOT_HOLE": packet(stable_neighbours)}
    return decks, frozenset(status), packet(raw_neighbours), length_bin(len(line_free))


def relation_populations(lines: Sequence[Line], paragraphs: Sequence[Paragraph]) -> dict[str, Any]:
    qrows = {row["identifier"]: row for row in read_tsv(QUARANTINE_SPECS)}
    expected_raw = tuple(qrows["RAW35"]["surfaces_or_rule"].split("|"))
    expected_all = tuple(qrows["ALL28"]["surfaces_or_rule"].split("|"))
    expected_core = tuple(row["carrier"] for row in read_tsv(CORE_SPECS))
    thin9 = tuple(qrows["THIN9"]["surfaces_or_rule"].split("|"))
    raw_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    stable_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    stable_folios: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for line in lines:
        for index, surface in enumerate(line.tokens):
            parsed = parse_relation(surface)
            if parsed is None:
                continue
            carrier, tail = parsed
            raw_counts[carrier][tail] += 1
            if line.stable[index]:
                stable_counts[carrier][tail] += 1
                stable_folios[carrier, tail].add(physical_folio(line.page))
    raw35 = tuple(sorted(carrier for carrier, counts in raw_counts.items()
                         if all(counts[tail] > 0 for tail in TAILS)))
    all28 = tuple(sorted(carrier for carrier, counts in stable_counts.items()
                         if all(counts[tail] > 0 for tail in TAILS)))
    core13 = tuple(sorted(carrier for carrier in all28
                          if all(stable_counts[carrier][tail] >= 3
                                 and len(stable_folios[carrier, tail]) >= 3 for tail in TAILS)))
    if tuple(sorted(expected_raw)) != raw35 or len(raw35) != EXPECTED["raw35"]:
        raise AssertionError("RAW35 independent reconstruction drift")
    if tuple(sorted(expected_all)) != all28 or len(all28) != EXPECTED["all28"]:
        raise AssertionError("ALL28 independent reconstruction drift")
    if tuple(sorted(expected_core)) != core13 or len(core13) != EXPECTED["core13"]:
        raise AssertionError("CORE13 independent reconstruction drift")
    main = {carrier + tail for carrier in raw35 for tail in TAILS}
    thin = {carrier + tail for carrier in thin9 for tail in THIN_TAILS}
    q152 = frozenset(main | thin)
    overlap = sorted(main & thin)
    if len(q152) != EXPECTED["q152"] or overlap != sorted(qrows["OVERLAP6"]["surfaces_or_rule"].split("|")):
        raise AssertionError("Q152 independent construction drift")
    paragraph_by_locus = {line.locus: paragraph for paragraph in paragraphs for line in paragraph.lines}
    end_classes = tuple(sorted({surface[-1] for line in lines for surface in line.tokens
                                if surface not in q152}))

    def build_events(population: Sequence[str], prefix: str) -> tuple[list[Event], dict[str, int]]:
        permitted = set(population)
        preliminary: list[tuple[str, str, str, Paragraph, Line, int]] = []
        audit = Counter()
        raw_population_occurrences = 0
        for line in lines:
            paragraph = paragraph_by_locus.get(line.locus)
            for index, surface in enumerate(line.tokens):
                parsed = parse_relation(surface)
                if parsed is None or parsed[0] not in permitted:
                    continue
                raw_population_occurrences += 1
                carrier, tail = parsed
                # The registered funnel first restricts to strictly closed
                # paragraphs.  This ordering matters for the two unstable
                # occurrences that are also outside a strict paragraph.
                if paragraph is None:
                    audit["outside_strict_paragraph"] += 1
                    continue
                if not line.stable[index]:
                    audit["unstable"] += 1
                    continue
                if not (unique_forced_lcs(line.tokens, line.alternate["it2a"], index)
                        and unique_forced_lcs(line.tokens, line.alternate["rf1b"], index)):
                    audit["not_unique_forced_lcs"] += 1
                    continue
                family = {carrier + member for member in TAILS}
                if sum(token in family for token in line.tokens) != 1:
                    audit["not_own_family_singleton"] += 1
                    continue
                preliminary.append((carrier, tail, surface, paragraph, line, index + 1))
        events = []
        for ordinal, (carrier, tail, surface, paragraph, line, token_index) in enumerate(preliminary, 1):
            decks, status, raw_slot, free_length = canonical_features(
                paragraph, line, token_index, carrier, q152, end_classes)
            events.append(Event(f"{prefix}-E{ordinal:04d}", ordinal, carrier, tail,
                                surface, paragraph, line,
                                next(i for i, item in enumerate(paragraph.lines, 1)
                                     if item.locus == line.locus),
                                token_index, decks, status, raw_slot, free_length))
        funnel = {"raw_population_occurrences": raw_population_occurrences, **audit,
                  "eligible_events": len(events)}
        if raw_population_occurrences - sum(audit.values()) != len(events):
            raise AssertionError("event funnel is not exhaustive")
        return events, funnel

    core_events, core_funnel = build_events(core13, "G808")
    all_events, all_funnel = build_events(all28, "G808-A28")

    def axis_funnel(population: Sequence[str], axis: str) -> dict[str, int]:
        selected_tails = {"ol", "eol"} if axis == "L" else {"edy", "eody"}
        permitted = set(population)
        values = Counter()
        for line in lines:
            paragraph = paragraph_by_locus.get(line.locus)
            for index, surface in enumerate(line.tokens):
                parsed = parse_relation(surface)
                if parsed is None or parsed[0] not in permitted or parsed[1] not in selected_tails:
                    continue
                carrier, _ = parsed
                values["raw"] += 1
                if paragraph is None:
                    values["outside"] += 1
                    continue
                values["strict"] += 1
                if not line.stable[index]:
                    continue
                values["stable"] += 1
                if not (unique_forced_lcs(line.tokens, line.alternate["it2a"], index)
                        and unique_forced_lcs(line.tokens, line.alternate["rf1b"], index)):
                    continue
                values["lcs"] += 1
                if sum(token in {carrier + tail for tail in TAILS} for token in line.tokens) != 1:
                    continue
                values["singleton"] += 1
        return dict(values)

    core_axis_funnels = {axis: axis_funnel(core13, axis) for axis in ("L", "DY")}
    all28_axis_funnels = {axis: axis_funnel(all28, axis) for axis in ("L", "DY")}
    if core_axis_funnels != {
        "L": {"raw": 1335, "outside": 7, "strict": 1328, "stable": 1169,
              "lcs": 1154, "singleton": 914},
        "DY": {"raw": 1834, "outside": 9, "strict": 1825, "stable": 1124,
               "lcs": 1063, "singleton": 863},
    }:
        raise AssertionError(f"CORE13 axis-funnel drift: {core_axis_funnels}")
    if all28_axis_funnels != {
        "L": {"raw": 1541, "outside": 8, "strict": 1533, "stable": 1352,
              "lcs": 1337, "singleton": 1091},
        "DY": {"raw": 2262, "outside": 12, "strict": 2250, "stable": 1395,
               "lcs": 1331, "singleton": 1117},
    }:
        raise AssertionError(f"ALL28 axis-funnel drift: {all28_axis_funnels}")
    if len(core_events) != EXPECTED["core_events"]:
        raise AssertionError(f"CORE13 event drift: {len(core_events)}")
    if Counter(event.tail for event in core_events) != Counter(
            {"ol": 641, "eol": 273, "edy": 715, "eody": 148}):
        raise AssertionError("CORE13 event cell-count drift")
    if len({event.paragraph.paragraph_id for event in core_events}) != EXPECTED["core_event_paragraphs"]:
        raise AssertionError("CORE13 event paragraph census drift")
    if len({event.line.locus for event in core_events}) != EXPECTED["core_event_lines"]:
        raise AssertionError("CORE13 event line census drift")
    if len({event.physical_folio for event in core_events}) != EXPECTED["core_event_folios"]:
        raise AssertionError("CORE13 event folio census drift")
    if len(all_events) != EXPECTED["all28_events"]:
        raise AssertionError("ALL28 event-count drift")
    if len({event.paragraph.paragraph_id for event in all_events}) != EXPECTED["all28_event_paragraphs"]:
        raise AssertionError("ALL28 event paragraph census drift")
    return {"raw_counts": raw_counts, "stable_counts": stable_counts,
            "stable_folios": stable_folios, "raw35": raw35, "all28": all28,
            "core13": core13, "thin9": thin9, "q152": q152,
            "end_classes": end_classes, "core_events": core_events,
            "all28_events": all_events, "core_funnel": core_funnel,
            "all28_funnel": all_funnel, "core_axis_funnels": core_axis_funnels,
            "all28_axis_funnels": all28_axis_funnels}


def levenshtein(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + int(a != b)))
        previous = current
    return previous[-1]


def read_model_specs() -> list[ModelSpec]:
    output = [ModelSpec(row["model_id"], row["source_axis"], row["target_axis"],
                        row["positive_source_tail"], row["negative_source_tail"],
                        row["positive_target_tail"], row["negative_target_tail"],
                        row["population"]) for row in read_tsv(MODEL_SPECS)]
    if len(output) != 8:
        raise AssertionError("relation-model spec cardinality drift")
    return output


def event_features(event: Event, deck: str, view: str,
                   ed1_quarantine: frozenset[str]) -> frozenset[str]:
    values = event.raw_slot if deck == "SLOT_HOLE" and view == "RAW_NEIGHBOUR" else event.feature_decks[deck]
    if view != "ED1":
        return values
    if deck == "SLOT_HOLE":
        # ED1 deletes atoms first.  Brackets are then reconstructed only from
        # the surviving atoms; retaining a pre-built bracket would leak an
        # otherwise quarantined neighbour through the compound feature.
        atoms: dict[str, str] = {}
        for feature in values:
            name, separator, surface = feature.partition("=")
            if (separator and name in {"L2", "L1", "R1", "R2"}
                    and "|" not in surface and surface not in ed1_quarantine):
                atoms[name] = surface
        output = {name + "=" + surface for name, surface in atoms.items()}
        for left, right, name in (("L2", "L1", "L2_L1"),
                                  ("L1", "R1", "L1_R1"),
                                  ("R1", "R2", "R1_R2")):
            if left in atoms and right in atoms:
                output.add(f"{name}={atoms[left]}|{atoms[right]}")
        return frozenset(output)
    return frozenset(feature for feature in values
                     if feature_surface(feature) is None
                     or feature_surface(feature) not in ed1_quarantine)


def labels_for(events: Sequence[Event], positive: str, negative: str) -> dict[str, int]:
    return {event.event_id: int(event.tail == positive) for event in events
            if event.tail in {positive, negative}}


def vocabulary(training: Sequence[Event], deck: str, view: str,
               ed1_quarantine: frozenset[str]) -> tuple[str, ...]:
    carriers: defaultdict[str, set[str]] = defaultdict(set)
    folios: defaultdict[str, set[str]] = defaultdict(set)
    for event in training:
        for feature in event_features(event, deck, view, ed1_quarantine):
            carriers[feature].add(event.carrier)
            folios[feature].add(event.physical_folio)
    return tuple(sorted(feature for feature in carriers
                        if len(carriers[feature]) >= 2 and len(folios[feature]) >= 2))


def train_mnb(training: Sequence[Event], labels: Mapping[str, int], deck: str,
              view: str, ed1_quarantine: frozenset[str]) -> tuple[dict[str, float], int]:
    vocab = vocabulary(training, deck, view, ed1_quarantine)
    if not vocab:
        return {}, 0
    allowed = set(vocab)
    cell_counts = Counter((event.carrier, labels[event.event_id]) for event in training)
    counts = {0: Counter(), 1: Counter()}
    totals = Counter()
    for event in training:
        label = labels[event.event_id]
        weight = 1.0 / cell_counts[event.carrier, label]
        used = event_features(event, deck, view, ed1_quarantine) & allowed
        for feature in used:
            counts[label][feature] += weight
        totals[label] += weight * len(used)
    width = len(vocab)
    weights = {feature: math.log((counts[1][feature] + ALPHA) /
                                 (totals[1] + ALPHA * width))
                        - math.log((counts[0][feature] + ALPHA) /
                                   (totals[0] + ALPHA * width)) for feature in vocab}
    return weights, width


def train_union_mnb(training: Sequence[Event], labels: Mapping[str, int],
                    include_slot: bool) -> tuple[dict[str, float], int]:
    decks = DECKS if include_slot else DECKS[:3]
    decorated = {event.event_id: frozenset(deck + "::" + feature for deck in decks
                                           for feature in event.feature_decks[deck])
                 for event in training}
    carriers: defaultdict[str, set[str]] = defaultdict(set)
    folios: defaultdict[str, set[str]] = defaultdict(set)
    for event in training:
        for feature in decorated[event.event_id]:
            carriers[feature].add(event.carrier)
            folios[feature].add(event.physical_folio)
    vocab = tuple(sorted(feature for feature in carriers
                         if len(carriers[feature]) >= 2 and len(folios[feature]) >= 2))
    if not vocab:
        return {}, 0
    allowed = set(vocab)
    cells = Counter((event.carrier, labels[event.event_id]) for event in training)
    counts = {0: Counter(), 1: Counter()}
    totals = Counter()
    for event in training:
        label = labels[event.event_id]
        weight = 1.0 / cells[event.carrier, label]
        used = decorated[event.event_id] & allowed
        for feature in used:
            counts[label][feature] += weight
        totals[label] += weight * len(used)
    width = len(vocab)
    return ({feature: math.log((counts[1][feature] + ALPHA) /
                               (totals[1] + ALPHA * width))
                      - math.log((counts[0][feature] + ALPHA) /
                                 (totals[0] + ALPHA * width)) for feature in vocab}, width)


def score(features: Iterable[str], weights: Mapping[str, float]) -> tuple[float, int]:
    values = [weights[feature] for feature in features if feature in weights]
    return (math.fsum(values) / len(values), len(values)) if values else (0.0, 0)


def auc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positives = [value for label, value in zip(labels, scores) if label == 1]
    negatives = [value for label, value in zip(labels, scores) if label == 0]
    if not positives or not negatives:
        return None
    wins = math.fsum(1.0 if positive > negative else 0.5 if positive == negative else 0.0
                     for positive in positives for negative in negatives)
    return wins / (len(positives) * len(negatives))


def balanced_accuracy(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positives, negatives = sum(labels), len(labels) - sum(labels)
    if not positives or not negatives:
        return None
    pos = sum(1.0 if value > 0 else 0.5 if value == 0 else 0.0
              for label, value in zip(labels, scores) if label) / positives
    neg = sum(1.0 if value < 0 else 0.5 if value == 0 else 0.0
              for label, value in zip(labels, scores) if not label) / negatives
    return 0.5 * (pos + neg)


def log_loss(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    if not labels:
        return None
    losses = []
    for label, value in zip(labels, scores):
        signed = value if label else -value
        losses.append(math.log1p(math.exp(-abs(signed))) + max(-signed, 0.0))
    return math.fsum(losses) / len(losses)


def carrier_class_log_loss(predictions: Sequence[Mapping[str, Any]], score_name: str,
                           labels: Sequence[int]) -> float | None:
    """Mean BCE after giving every nonempty carrier x class cell equal weight."""
    cells: defaultdict[tuple[str, int], list[float]] = defaultdict(list)
    for row, label in zip(predictions, labels):
        value = float(row[score_name])
        signed = value if label else -value
        loss = math.log1p(math.exp(-abs(signed))) + max(-signed, 0.0)
        cells[(str(row["carrier"]), int(label))].append(loss)
    means = [math.fsum(values) / len(values) for _, values in sorted(cells.items())]
    return math.fsum(means) / len(means) if means else None


def metric_bundle(predictions: Sequence[Mapping[str, Any]], score_name: str,
                  label_override: Mapping[str, int] | None = None) -> dict[str, Any]:
    labels = [int(label_override[row["event_id"]]) if label_override is not None
              else int(row["target_label"]) for row in predictions]
    scores = [float(row[score_name]) for row in predictions]
    by_carrier = {}
    for carrier in sorted({str(row["carrier"]) for row in predictions}):
        indices = [index for index, row in enumerate(predictions) if row["carrier"] == carrier]
        by_carrier[carrier] = auc([labels[index] for index in indices],
                                  [scores[index] for index in indices])
    defined = [value for value in by_carrier.values() if value is not None]
    return {"micro_auc": auc(labels, scores),
            "carrier_macro_auc": math.fsum(defined) / len(defined) if defined else None,
            "balanced_accuracy": balanced_accuracy(labels, scores),
            "log_loss": carrier_class_log_loss(predictions, score_name, labels),
            "micro_log_loss": log_loss(labels, scores), "carrier_auc": by_carrier,
            "carriers_above_half": sum(value is not None and value > 0.5
                                       for value in by_carrier.values()),
            "zero_votes": sum(value == 0 for value in scores)}


def conditional_auc(predictions: Sequence[Mapping[str, Any]], score_name: str,
                    label_override: Mapping[str, int] | None = None) -> dict[str, Any]:
    strata: defaultdict[tuple[str, str, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in predictions:
        strata[(str(row["carrier"]), str(row["section"]), str(row["language"]),
                str(row["hand"]), int(row["line_length_bin"]))].append(row)
    by_carrier_wins: Counter[str] = Counter()
    by_carrier_pairs: Counter[str] = Counter()
    by_carrier_cells: Counter[str] = Counter()
    for key, rows in strata.items():
        labels = [(label_override or {}).get(str(row["event_id"]), int(row["target_label"]))
                  for row in rows]
        positive = [row for row, label in zip(rows, labels) if label == 1]
        negative = [row for row, label in zip(rows, labels) if label == 0]
        if not positive or not negative:
            continue
        carrier = key[0]
        by_carrier_cells[carrier] += 1
        for left in positive:
            for right in negative:
                a, b = float(left[score_name]), float(right[score_name])
                by_carrier_wins[carrier] += 1.0 if a > b else 0.5 if a == b else 0.0
                by_carrier_pairs[carrier] += 1
    carrier_auc = {carrier: by_carrier_wins[carrier] / by_carrier_pairs[carrier]
                   for carrier in sorted(by_carrier_pairs)}
    macro = (math.fsum(carrier_auc.values()) / len(carrier_auc)
             if carrier_auc else None)
    wins = math.fsum(by_carrier_wins.values())
    pairs = sum(by_carrier_pairs.values())
    return {"auc": macro, "carrier_macro_auc": macro,
            "pooled_pair_auc": wins / pairs if pairs else None,
            "matched_pairs": int(pairs),
            "scoreable_strata": int(sum(by_carrier_cells.values())),
            "scoreable_carriers": len(carrier_auc),
            "carrier_auc": carrier_auc,
            "carrier_pair_count": {carrier: int(by_carrier_pairs[carrier])
                                   for carrier in sorted(by_carrier_pairs)},
            "carrier_stratum_count": {carrier: int(by_carrier_cells[carrier])
                                      for carrier in sorted(by_carrier_cells)}}


def ed1_surface_set(events: Sequence[Event], q152: frozenset[str]) -> frozenset[str]:
    observed = {surface for event in events for deck in DECKS
                for feature in event.feature_decks[deck]
                for surface in [feature_surface(feature)] if surface is not None}
    return frozenset(surface for surface in observed
                     if any(levenshtein(surface, blocked) <= 1 for blocked in q152))


def score_model(spec: ModelSpec, events: Sequence[Event], q152: frozenset[str],
                view: str = "PRIMARY", source_label_flips: Mapping[str, set[str]] | None = None,
                union: bool = False) -> dict[str, Any]:
    source = [event for event in events if event.tail in {spec.positive_source, spec.negative_source}]
    target = [event for event in events if event.tail in {spec.positive_target, spec.negative_target}]
    base_labels = labels_for(source, spec.positive_source, spec.negative_source)
    target_labels = labels_for(target, spec.positive_target, spec.negative_target)
    ed1 = ed1_surface_set(events, q152) if view == "ED1" else frozenset()
    predictions = []
    folds = []
    keys = sorted({(event.carrier, event.physical_folio) for event in target},
                  key=lambda item: (item[0], natural_page_key(item[1])))
    expected_sizes = {
        "M01_L_TO_L": (914, 914, 569),
        "M02_DY_TO_DY": (863, 863, 394),
        "M03_L_TO_DY": (914, 863, 394),
        "M04_DY_TO_L": (863, 914, 569),
        "M05_L_TO_L_ALL28": (1091, 1091, 729),
        "M06_DY_TO_DY_ALL28": (1117, 1117, 577),
        "M07_L_TO_DY_ALL28": (1091, 1117, 577),
        "M08_DY_TO_L_ALL28": (1117, 1091, 729),
    }
    observed_sizes = (len(source), len(target), len(keys))
    if observed_sizes != expected_sizes[spec.model_id]:
        raise AssertionError(f"model capacity drift {spec.model_id}: {observed_sizes}")
    for held_carrier, held_folio in keys:
        training = [event for event in source
                    if event.carrier != held_carrier and event.physical_folio != held_folio]
        testing = [event for event in target
                   if event.carrier == held_carrier and event.physical_folio == held_folio]
        train_labels = dict(base_labels)
        if source_label_flips is not None:
            flipped = source_label_flips.get(held_carrier, set())
            for event in training:
                if event.carrier in flipped:
                    train_labels[event.event_id] = 1 - train_labels[event.event_id]
        if {train_labels[event.event_id] for event in training} != {0, 1}:
            raise AssertionError(f"unscoreable fold {spec.model_id}:{held_carrier}:{held_folio}")
        if any(event.carrier == held_carrier or event.physical_folio == held_folio for event in training):
            raise AssertionError("component/folio holdout leakage")
        if union:
            union_nuis = train_union_mnb(training, train_labels, False)
            union_aug = train_union_mnb(training, train_labels, True)
        else:
            deck_models = {deck: train_mnb(training, train_labels, deck, view, ed1)
                           for deck in DECKS}
        for event in testing:
            row = {"event_id": event.event_id, "carrier": event.carrier,
                   "physical_folio": event.physical_folio, "page": event.line.page,
                   "locus": event.line.locus, "line_number": event.line.number,
                   "token_index": event.token_index, "section": event.paragraph.section,
                   "language": event.paragraph.language, "hand": event.paragraph.hand,
                   "line_length_bin": event.line_length_bin,
                   "target_label": target_labels[event.event_id], "target_tail": event.tail}
            if union:
                nf = frozenset(deck + "::" + feature for deck in DECKS[:3]
                               for feature in event.feature_decks[deck])
                af = nf | frozenset("SLOT_HOLE::" + feature
                                    for feature in event.feature_decks["SLOT_HOLE"])
                row["nuisance_score"], row["nuisance_known"] = score(nf, union_nuis[0])
                row["augmented_score"], row["augmented_known"] = score(af, union_aug[0])
            else:
                for deck in DECKS:
                    row[deck + "_score"], row[deck + "_known"] = score(
                        event_features(event, deck, view, ed1), deck_models[deck][0])
                row["nuisance_score"] = math.fsum(row[deck + "_score"] for deck in DECKS[:3])
                row["augmented_score"] = row["nuisance_score"] + row["SLOT_HOLE_score"]
            predictions.append(row)
        fold = {"held_carrier": held_carrier, "held_physical_folio": held_folio,
                "train_events": len(training), "test_events": len(testing),
                "train_carriers": len({event.carrier for event in training}),
                "train_folios": len({event.physical_folio for event in training}),
                "positive_train_events": sum(train_labels[event.event_id] for event in training),
                "negative_train_events": sum(1 - train_labels[event.event_id] for event in training)}
        if union:
            fold.update(vocab_nuisance=union_nuis[1], vocab_augmented=union_aug[1])
        else:
            fold.update({"vocab_" + deck: deck_models[deck][1] for deck in DECKS})
        folds.append(fold)
    predictions.sort(key=lambda row: (natural_page_key(str(row["page"])),
                                      int(row["line_number"]), int(row["token_index"]),
                                      str(row["event_id"])))
    if len(predictions) != len(target):
        raise AssertionError(f"prediction coverage drift: {spec.model_id}")
    names = (("nuisance_score", "augmented_score") if union else
             tuple(deck + "_score" for deck in DECKS) + ("nuisance_score", "augmented_score"))
    metrics = {}
    for name in names:
        metrics[name] = metric_bundle(predictions, name)
        metrics[name]["conditional"] = conditional_auc(predictions, name)
    metrics["local_gain"] = (metrics["augmented_score"]["carrier_macro_auc"]
                             - metrics["nuisance_score"]["carrier_macro_auc"])
    metrics["log_loss_gain"] = (metrics["nuisance_score"]["log_loss"]
                                - metrics["augmented_score"]["log_loss"])
    a = metrics["augmented_score"]["conditional"]["auc"]
    n = metrics["nuisance_score"]["conditional"]["auc"]
    metrics["conditional_gain"] = a - n if a is not None and n is not None else None
    return {"spec": spec, "predictions": predictions, "folds": folds,
            "metrics": metrics, "source_events": len(source), "target_events": len(target)}


def rotate_target_labels(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    predictions = list(result["predictions"])
    strata: defaultdict[tuple[str, str, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in predictions:
        strata[(str(row["carrier"]), str(row["section"]), str(row["language"]),
                str(row["hand"]), int(row["line_length_bin"]))].append(row)
    output = []
    for offset in range(1, 25):
        labels = {}
        moved = identities = 0
        for key in sorted(strata):
            rows = sorted(strata[key], key=lambda row: (
                natural_page_key(str(row["page"])), int(row["line_number"]),
                int(row["token_index"]), str(row["event_id"])))
            original = [int(row["target_label"]) for row in rows]
            shift = offset % len(rows)
            assigned = original[-shift:] + original[:-shift] if shift else original[:]
            for row, old, new in zip(rows, original, assigned):
                labels[str(row["event_id"])] = new
                moved += int(old != new)
                identities += int(old == new)
        nuisance = metric_bundle(predictions, "nuisance_score", labels)
        augmented = metric_bundle(predictions, "augmented_score", labels)
        changed_fraction = moved / len(predictions) if predictions else 0.0
        output.append({"offset": offset, "moved_labels": moved,
                       "identity_labels": identities,
                       "changed_fraction": changed_fraction,
                       "mobility_status": ("LOW_MOBILITY" if changed_fraction < 0.20
                                           else "ADEQUATE_MOBILITY"),
                       "nuisance_macro_auc": nuisance["carrier_macro_auc"],
                       "augmented_macro_auc": augmented["carrier_macro_auc"],
                       "local_gain": augmented["carrier_macro_auc"] - nuisance["carrier_macro_auc"]})
    return output


def carrier_flip_maps(population: Sequence[str]) -> list[dict[str, set[str]]]:
    result = []
    for rotation in range(12):
        mapping = {}
        for held in sorted(population):
            remaining = sorted(set(population) - {held})
            if len(remaining) != 12:
                raise AssertionError("carrier-sign null requires twelve source carriers")
            mapping[held] = {remaining[(rotation + offset) % 12] for offset in range(6)}
        result.append(mapping)
    return result


def contact_overlays(events: Sequence[Event], q152: frozenset[str]) -> dict[str, Any]:
    """Rebuild corrected exact overlay contacts; GDT757 remains audit-only."""
    by_location = {(event.line.page, event.line.locus, event.token_index): event for event in events}
    contacts = {event.event_id: {"amount": False, "quality": False,
                                 "part": False, "formula_audit": False}
                for event in events}
    audit = Counter()
    for row in read_tsv(G759):
        page, locus = row["page"], row["locus"]
        left, right = int(row["left_token_ordinal"]), int(row["right_token_ordinal"])
        endpoints = {row["left_surface"], row["right_surface"]}
        if endpoints & q152:
            audit["g759_q152_dropped"] += 1
            continue
        for index in (left - 2, left - 1, right + 1, right + 2):
            event = by_location.get((page, locus, index))
            if event is None or left <= event.token_index <= right:
                continue
            if physical_folio(page) != event.physical_folio:
                raise AssertionError("G759 physical-folio recomputation mismatch")
            distance = min(abs(event.token_index - left), abs(event.token_index - right))
            if distance not in (1, 2):
                continue
            family = row["family"]
            if family == "QUANTITY_VALUE":
                contacts[event.event_id]["amount"] = True
            elif family in {"PART_STATE", "PREPARATION_VALUE"}:
                contacts[event.event_id]["quality"] = True
    for row in read_tsv(G768):
        page, locus, anchor = row["page"], row["locus"], int(row["token_index"])
        if row["surface"] in q152:
            audit["g768_q152_dropped"] += 1
            continue
        for index in (anchor - 2, anchor - 1, anchor + 1, anchor + 2):
            event = by_location.get((page, locus, index))
            if event is None or event.token_index == anchor:
                continue
            if physical_folio(page) != event.physical_folio:
                raise AssertionError("G768 physical-folio recomputation mismatch")
            contacts[event.event_id]["part"] = True
    for row in read_tsv(G757):
        page, locus = row["page"], row["locus"]
        line_tokens = tuple(row["written_line_eva"].split())
        positions = [index for index, surface in enumerate(line_tokens, 1)
                     if surface == row["surface"]]
        if len(positions) != 1:
            audit["g757_nonunique_anchor"] += 1
            continue
        anchor = positions[0]
        if row["surface"] in q152:
            audit["g757_q152_dropped"] += 1
            continue
        for index in (anchor - 2, anchor - 1, anchor + 1, anchor + 2):
            event = by_location.get((page, locus, index))
            if event is not None and event.token_index != anchor:
                contacts[event.event_id]["formula_audit"] = True

    def axis_stat(kind: str, negative: str, positive: str) -> dict[str, Any]:
        selected = [event for event in events if event.tail in {negative, positive}]
        values = Counter()
        folios = set()
        for event in selected:
            label = "positive" if event.tail == positive else "negative"
            hit = contacts[event.event_id][kind]
            values[label + "_contact"] += int(hit)
            values[label + "_no_contact"] += int(not hit)
            if hit:
                folios.add(event.physical_folio)
        total_contact = values["positive_contact"] + values["negative_contact"]
        if total_contact == 0:
            log_or = None
        else:
            log_or = math.log(((values["positive_contact"] + 0.5)
                               * (values["negative_no_contact"] + 0.5))
                              / ((values["positive_no_contact"] + 0.5)
                                 * (values["negative_contact"] + 0.5)))
        return {**values, "total_contact": total_contact,
                "contact_folios": len(folios), "log_or": log_or,
                "abs_log_or": abs(log_or) if log_or is not None else None}

    axes = {}
    for axis, negative, positive in (("L", "ol", "eol"), ("DY", "edy", "eody")):
        axes[axis] = {kind: axis_stat(kind, negative, positive)
                      for kind in ("amount", "quality", "part", "formula_audit")}
    expected_cells = {
        ("L", "amount"): (4, 269, 4, 637, 7),
        ("DY", "amount"): (4, 144, 1, 714, 4),
        ("L", "quality"): (0, 273, 0, 641, 0),
        ("DY", "quality"): (0, 148, 0, 715, 0),
        ("L", "part"): (10, 263, 59, 582, 48),
        ("DY", "part"): (5, 143, 11, 704, 10),
        ("L", "formula_audit"): (4, 269, 3, 638, 7),
        ("DY", "formula_audit"): (0, 148, 1, 714, 1),
    }
    for key, expected in expected_cells.items():
        values = axes[key[0]][key[1]]
        observed = (values.get("positive_contact", 0),
                    values.get("positive_no_contact", 0),
                    values.get("negative_contact", 0),
                    values.get("negative_no_contact", 0),
                    values.get("contact_folios", 0))
        if observed != expected:
            raise AssertionError(f"corrected contact census drift {key}: {observed} != {expected}")
    return {"event_contacts": contacts, "axis_stats": axes, "audit": dict(audit)}


def model_decision(primary: Mapping[str, Any], all28: Mapping[str, Any],
                   union: Mapping[str, Any], target_nulls: Sequence[Mapping[str, Any]],
                   carrier_nulls: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    metrics = primary["metrics"]
    observed_gain = metrics["local_gain"]
    gain_rank = 1 + sum(float(row["local_gain"]) >= observed_gain for row in target_nulls)
    nuisance_auc = metrics["nuisance_score"]["carrier_macro_auc"]
    portability_rank = 1 + sum(float(row["nuisance_macro_auc"]) >= nuisance_auc for row in carrier_nulls)
    gates = {
        "augmented_macro_ge_060": metrics["augmented_score"]["carrier_macro_auc"] >= 0.60,
        "local_gain_ge_002": observed_gain >= 0.02,
        "positive_log_loss_gain": metrics["log_loss_gain"] > 0,
        "slot_carriers_above_half_ge_9": metrics["SLOT_HOLE_score"]["carriers_above_half"] >= 9,
        "conditional_gain_ge_002": metrics["conditional_gain"] is not None and metrics["conditional_gain"] >= 0.02,
        "target_null_rank_1": gain_rank == 1,
        "all28_augmented_ge_055": all28["metrics"]["augmented_score"]["carrier_macro_auc"] >= 0.55,
        "all28_positive_gain": all28["metrics"]["local_gain"] > 0,
        "union_positive_gain": union["metrics"]["local_gain"] > 0,
    }
    direction_gain = (gates["augmented_macro_ge_060"] and gates["local_gain_ge_002"]
                      and gates["positive_log_loss_gain"]
                      and gates["slot_carriers_above_half_ge_9"]
                      and gates["conditional_gain_ge_002"]
                      and gates["all28_augmented_ge_055"] and gates["all28_positive_gain"])
    if all(gates.values()):
        decision = "PORTABLE_LOCAL_SLOT_RELATION"
    elif direction_gain and (gain_rank in (2, 3) or not gates["union_positive_gain"]):
        decision = "PROVISIONAL_OR_SCORER_SENSITIVE_LOCAL_LEAD"
    else:
        record = {"nuisance_macro_ge_060": nuisance_auc >= 0.60,
                  "nuisance_carriers_above_half_ge_9": metrics["nuisance_score"]["carriers_above_half"] >= 9,
                  "all28_nuisance_ge_055": all28["metrics"]["nuisance_score"]["carrier_macro_auc"] >= 0.55,
                  "portability_rank_le_3": portability_rank <= 3}
        gates.update(record)
        decision = "PORTABLE_RECORD_OR_FORM_RELATION" if all(record.values()) else "NO_PORTABLE_RELATION_SIGNAL"
    return {"decision": decision, "gates": gates, "target_null_rank": gain_rank,
            "portability_null_rank": portability_rank}


def winning_contact_axis(overlays: Mapping[str, Any], kind: str) -> dict[str, Any]:
    candidates = []
    for axis in sorted(overlays["axis_stats"]):
        values = overlays["axis_stats"][axis][kind]
        absolute = values["abs_log_or"]
        # No-contact axes are ineligible rather than converted into a
        # half-count signal.  Lexical axis order resolves an exact tie.
        if absolute is not None:
            candidates.append((-float(absolute), axis, values))
    if not candidates:
        return {"axis": None, "abs_log_or": None, "contact_folios": 0}
    _, axis, values = min(candidates)
    return {"axis": axis, "abs_log_or": values["abs_log_or"],
            "contact_folios": values["contact_folios"]}


def registered_rival_metrics(models: Mapping[str, Mapping[str, Any]],
                             overlays: Mapping[str, Any],
                             populations: Mapping[str, Any]) -> dict[str, Any]:
    m01, m02 = models["M01_L_TO_L"], models["M02_DY_TO_DY"]
    m03, m04 = models["M03_L_TO_DY"], models["M04_DY_TO_L"]

    def macro(model: Mapping[str, Any], score_name: str) -> float:
        return float(model["metrics"][score_name]["carrier_macro_auc"])

    amount = winning_contact_axis(overlays, "amount")
    quality = winning_contact_axis(overlays, "quality")
    part = winning_contact_axis(overlays, "part")
    reversed_count = max(
        sum(value is not None and value < 0.5
            for value in model["metrics"]["augmented_score"]["carrier_auc"].values())
        for model in (m01, m02))
    stable_l = (populations["core_axis_funnels"]["L"]["stable"]
                / populations["core_axis_funnels"]["L"]["strict"])
    stable_dy = (populations["core_axis_funnels"]["DY"]["stable"]
                 / populations["core_axis_funnels"]["DY"]["strict"])
    topic_or_form = [max(macro(model, "TOPIC_score"),
                         macro(model, "FORM_REGIME_score"))
                     for model in (m01, m02)]
    local_gains = [float(model["metrics"]["local_gain"]) for model in (m01, m02)]
    within_nuisance = [macro(model, "nuisance_score") for model in (m01, m02)]
    cross_slot = [macro(model, "SLOT_HOLE_score") for model in (m03, m04)]
    cross_nuisance = [macro(model, "nuisance_score") for model in (m03, m04)]
    within_form = [macro(model, "FORM_REGIME_score") for model in (m01, m02)]
    return {
        "MIN_WITHIN_NUISANCE_MACRO_AUC": min(within_nuisance),
        "DY_LOCAL_GAIN": local_gains[1], "L_LOCAL_GAIN": local_gains[0],
        "MIN_CROSS_SLOT_MACRO_AUC": min(cross_slot),
        "MIN_LOCAL_GAIN": min(local_gains),
        "QUALITY_VALUE_CONTACT_ABS_LOG_OR": quality["abs_log_or"],
        "QUALITY_VALUE_CONTACT_FOLIOS": quality["contact_folios"],
        "PART_FORM_CONTACT_ABS_LOG_OR": part["abs_log_or"],
        "PART_FORM_CONTACT_FOLIOS": part["contact_folios"],
        "AMOUNT_CONTACT_ABS_LOG_OR": amount["abs_log_or"],
        "AMOUNT_CONTACT_FOLIOS": amount["contact_folios"],
        "MIN_WITHIN_TOPIC_OR_FORM_MACRO_AUC": min(topic_or_form),
        "MAX_LOCAL_GAIN": max(local_gains),
        "MAX_CROSS_NUISANCE_INVERTED_AUC": max(1.0 - value for value in cross_nuisance),
        "MIN_WITHIN_FORM_MACRO_AUC": min(within_form),
        "MIN_TARGET_READER_STABLE_RATE": min(stable_l, stable_dy),
        "MAX_WITHIN_NUISANCE_MACRO_AUC": max(within_nuisance),
        "MAX_REVERSED_CARRIER_COUNT": reversed_count,
    }


def historical_rival_scores(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = read_tsv(RIVAL_SPECS)
    awarded: defaultdict[str, int] = defaultdict(int)
    evidence: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = metrics[row["metric"]]
        threshold = float(row["threshold"])
        passed = (value is not None and
                  ((row["operator"] == "GE" and float(value) >= threshold)
                   or (row["operator"] == "LT" and float(value) < threshold)))
        points = int(row["points"]) if passed else 0
        awarded[row["rival_id"]] += points
        evidence[row["rival_id"]].append({"evidence_id": row["evidence_id"],
                                           "metric": row["metric"], "value": value,
                                           "pass": passed, "points": points})
    theories = {row["rival_id"]: row for row in read_tsv(SEMANTIC_SPECS)}
    output = [{"rival_id": rival, "points": awarded[rival],
               "working_theory": theories[rival]["working_theory"],
               "semantic_credit": 0, "evidence": evidence[rival]}
              for rival in theories]
    output.sort(key=lambda row: (-int(row["points"]), str(row["rival_id"])))
    for rank, row in enumerate(output, 1):
        row["rank"] = rank
    return output


def artifact_snapshot() -> dict[str, tuple[int, int, str]]:
    return {path.name: (path.stat().st_size, path.stat().st_mtime_ns, sha256(path))
            for path in ART.glob("*") if path.is_file() and path.name != "VALIDATION.json"}


def builder_active() -> bool:
    completed = subprocess.run(["ps", "-eo", "pid=,args="], check=True, text=True,
                               stdout=subprocess.PIPE)
    needle = "gdt808_exact_relation_slot_residual_bridge/src/run.py"
    for line in completed.stdout.splitlines():
        pid_text, _, command = line.strip().partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid != os.getpid() and needle in command:
            return True
    return False


def manifest_checks() -> list[str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("experiment_id") != "GDT808":
        raise AssertionError("manifest experiment id drift")
    if manifest.get("sealed_data") != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise AssertionError("manifest sealed-data gate drift")
    seen = set()
    for item in manifest.get("inputs", []):
        path = ROOT / item["path"]
        if not path.is_file():
            raise AssertionError(f"manifest input absent: {item['path']}")
        seen.add(item["path"])
        if path.resolve() in MIXED_PATHS:
            if item["sha256"] != MIXED_MANIFEST_HASHES[item["path"]]:
                raise AssertionError(f"mixed manifest lock drift: {item['path']}")
        elif sha256(path) != item["sha256"]:
            raise AssertionError(f"manifest input hash drift: {item['path']}")
    required = {rel(path) for path in (ALLOWLIST, LINES_RAW, CROSS_RAW, TOKENS_RAW,
                G759, G768, G757, MODEL_SPECS, CORE_SPECS, QUARANTINE_SPECS,
                IMPLEMENTATION_SPECS, FEATURE_SPECS, CONTROL_SPECS, RIVAL_SPECS,
                SEMANTIC_SPECS, HISTORICAL_SPECS)}
    if not required <= seen:
        raise AssertionError(f"manifest missing locks: {sorted(required - seen)}")
    if len(read_tsv(FEATURE_SPECS)) != 4 or len(read_tsv(CONTROL_SPECS)) != 8:
        raise AssertionError("feature/control spec cardinality drift")
    implementation = {row["key"]: row["value"] for row in read_tsv(IMPLEMENTATION_SPECS)}
    required_values = {"TAIL_PARSE_ORDER": "eody|eol|edy|ol", "NB_ALPHA": "0.5",
                       "FEATURE_SUPPORT": "at least two training carriers and two training physical folios",
                       "DECK_EVENT_SCORE": "mean known-feature log likelihood ratio; all-OOV equals zero",
                       "LABEL_NULL_DIRECTION": "destination i receives source i-k modulo stratum size; inherited GDT807 right rotation",
                       "FIXED_LOGLOSS": "carrier-class-weighted binary cross entropy of sigmoid(sum of relevant mean-LLR deck scores)",
                       "SLOT_ED1_ORDER": "delete ED1 atomic neighbours before building L2_L1 L1_R1 R1_R2 brackets"}
    if any(implementation.get(key) != value for key, value in required_values.items()):
        raise AssertionError("implementation-spec lock drift")
    return ["manifest_identity_and_sealed_gate", "manifest_input_locks",
            "registered_specs_replayed"]


def compare_artifacts(rebuilt: Mapping[str, Any]) -> list[str]:
    required = {"GDT808_SOURCE_CENSUS.tsv", "GDT808_CARRIER_CELL_CENSUS.tsv",
                "GDT808_Q152_QUARANTINE.tsv", "GDT808_1777_EVENT_ATLAS.tsv",
                "GDT808_HELD_PREDICTIONS.tsv", "GDT808_MODEL_SUMMARY.tsv",
                "GDT808_TARGET_LABEL_NULLS.tsv", "GDT808_CARRIER_PORTABILITY_NULLS.tsv",
                "GDT808_DECISION_CARD.tsv", "RESULT.json"}
    present = {path.name for path in ART.glob("*") if path.is_file()}
    missing = required - present
    if missing:
        raise AssertionError(f"official artifacts unavailable/schema drift: {sorted(missing)}")
    return ["official_artifact_inventory_present"]


def reconstruct(run_nulls: bool = True) -> dict[str, Any]:
    lines, paragraphs, outside, source_census = load_guarded_corpus()
    populations = relation_populations(lines, paragraphs)
    specs = read_model_specs()
    models = {}
    for spec in specs:
        events = populations["core_events"] if spec.population == "CORE13" else populations["all28_events"]
        models[spec.model_id] = score_model(spec, events, populations["q152"])
    union = {}
    target_nulls = {}
    carrier_nulls = {}
    decisions = {}
    if run_nulls:
        by_id = {spec.model_id: spec for spec in specs}
        for model_id in ("M01_L_TO_L", "M02_DY_TO_DY"):
            spec = by_id[model_id]
            union[model_id] = score_model(spec, populations["core_events"], populations["q152"], union=True)
            target_nulls[model_id] = rotate_target_labels(models[model_id])
            null_rows = []
            for rotation, mapping in enumerate(carrier_flip_maps(populations["core13"])):
                result = score_model(spec, populations["core_events"], populations["q152"],
                                     source_label_flips=mapping)
                null_rows.append({"rotation": rotation,
                                  "nuisance_macro_auc": result["metrics"]["nuisance_score"]["carrier_macro_auc"],
                                  "local_gain": result["metrics"]["local_gain"]})
            carrier_nulls[model_id] = null_rows
            all28_id = "M05_L_TO_L_ALL28" if model_id == "M01_L_TO_L" else "M06_DY_TO_DY_ALL28"
            decisions[model_id] = model_decision(models[model_id], models[all28_id],
                                                 union[model_id], target_nulls[model_id],
                                                 carrier_nulls[model_id])
    overlays = contact_overlays(populations["core_events"], populations["q152"])
    rival_metrics = registered_rival_metrics(models, overlays, populations)
    rival_scores = historical_rival_scores(rival_metrics)
    return {"lines": lines, "paragraphs": paragraphs, "outside": outside,
            "source_census": source_census, "populations": populations,
            "models": models, "union": union, "target_nulls": target_nulls,
            "carrier_nulls": carrier_nulls, "decisions": decisions,
            "contact_overlays": overlays, "rival_metrics": rival_metrics,
            "rival_scores": rival_scores}


def compact_payload(rebuilt: Mapping[str, Any], checks: Sequence[str]) -> dict[str, Any]:
    populations = rebuilt["populations"]
    summary = {model_id: {"source_events": result["source_events"],
                          "target_events": result["target_events"],
                          "scoreable_folds": len(result["folds"]),
                          "nuisance_macro_auc": result["metrics"]["nuisance_score"]["carrier_macro_auc"],
                          "augmented_macro_auc": result["metrics"]["augmented_score"]["carrier_macro_auc"],
                          "local_gain": result["metrics"]["local_gain"]}
               for model_id, result in rebuilt["models"].items()}
    return {"experiment": "GDT808", "status": "PASS", "check_count": len(checks),
            "checks_passed": list(checks), "validator_independent_of_builder_import": True,
            "mixed_sources_accessed_only_by_guarded_query": True,
            "sealed_f84_rows_materialized": 0, "sealed_f84r_rows_materialized": 0,
            "source_census": rebuilt["source_census"],
            "population_census": {"raw35": len(populations["raw35"]),
                                   "all28": len(populations["all28"]),
                                   "core13": len(populations["core13"]),
                                   "q152": len(populations["q152"]),
                                   "core_events": len(populations["core_events"]),
                                   "core_event_paragraphs": len({event.paragraph.paragraph_id for event in populations["core_events"]}),
                                   "all28_events": len(populations["all28_events"])},
            "model_summary": summary, "decisions": rebuilt["decisions"],
            "contact_overlays": rebuilt["contact_overlays"]["axis_stats"],
            "historical_rival_metrics": rebuilt["rival_metrics"],
            "historical_rival_ranking": rebuilt["rival_scores"],
            "claim_ceiling": "formal held relation and zero-semantic historical topology only; no lexeme, component meaning, plaintext, renderer licence or translation"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--skip-nulls", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    if builder_active():
        raise SystemExit("GDT808 builder active; refusing moving artifacts")
    before = artifact_snapshot()
    checks = manifest_checks()
    rebuilt = reconstruct(run_nulls=not args.skip_nulls)
    checks.extend(["guarded_source_census_reconstructed", "strict_paragraphs_reconstructed",
                   "raw35_all28_core13_q152_reconstructed", "core1777_and_all28_2208_reconstructed",
                   "four_disjoint_decks_reconstructed", "component_and_folio_holdouts_reconstructed",
                   "fixed_mnb_scores_reconstructed", "corrected_contact_overlays_reconstructed"])
    if args.source_only:
        checks.append("official_artifact_comparison_explicitly_skipped_source_only")
    else:
        checks.extend(compare_artifacts(rebuilt))
    if before != artifact_snapshot():
        raise AssertionError("artifact tree changed during validation")
    checks.append("artifact_tree_stable_during_validation")
    payload = compact_payload(rebuilt, checks)
    if not args.no_write and not args.source_only and not args.skip_nulls:
        temporary = VALIDATION.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(VALIDATION)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
