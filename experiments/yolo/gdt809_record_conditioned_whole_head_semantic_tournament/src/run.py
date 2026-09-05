#!/usr/bin/env python3
"""Build GDT809's exact whole-head / record-relation semantic tournament."""

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
BASE = ROOT / "experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
MANIFEST = BASE / "experiment.json"
RUN = SRC / "run.py"
VALIDATOR = SRC / "validate.py"
HEAD_SPECS = SRC / "HEAD_POOL_SPECS.tsv"
RELATION_SPECS = SRC / "RELATION_DECISION_SPECS.tsv"
MANUAL_SPECS = SRC / "MANUAL_EVIDENCE_SPECS.tsv"
LANDMARK_SPECS = SRC / "LANDMARK_SPECS.tsv"
SEMANTIC_SPECS = SRC / "SEMANTIC_PROFILE_SPECS.tsv"
ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
LINES_RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
G625_REPORT = ROOT / "experiments/yolo/gdt625_ordered_quality_state_transitions/REPORT.md"
G755_HISTORICAL = ROOT / "experiments/yolo/gdt755_top24_historical_register_crosswalk/src/HISTORICAL_EXPRESSION_BANK.tsv"
G757_FORMULA = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv"
G759_SPANS = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G760_DECK = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/CONTENT_ANCHOR_35_CANDIDATE_DECK.tsv"
G760_ATTACH = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/CONTENT_45_ATTACHMENT_ATLAS.tsv"
G760_AMOUNT = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv"
G764_X_DAIIN = ROOT / "experiments/yolo/gdt764_bounded_value_field_dispatch/artifacts/X_DAIIN_9_EXACT_BIGRAM_ATLAS.tsv"
G768_ANCHORS = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/ANCHOR_404_OCCURRENCE_ATLAS.tsv"
G791_VISUAL = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
G808_EVENTS = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_1777_CORE_EVENT_ATLAS.tsv"
G808_Q152 = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_Q152_EXACT_QUARANTINE.tsv"
G808_RESULT = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts/RESULT.json"
VMANUS_EXP = ROOT / "vmanus-exp"

EXPECTED = {
    "selectors": 179, "lines": 4137, "tokens": 32339,
    "strict_paragraphs": 665, "strict_lines": 3807, "strict_tokens": 31938,
    "core_events": 1777, "pool_union": 41, "q152": 152, "active_heads": 35,
    "stable_head_occurrences": 1032, "occurrence_edges": 211, "distinct_links": 209,
    "contacted_pivots": 199, "contacted_folios": 103, "unique_windows": 189,
    "ed1_safe_heads": 18, "ed1_occurrence_edges": 91, "ed1_distinct_links": 90,
    "ed1_contacted_pivots": 86, "ed1_unique_windows": 82,
}
ALPHA = 0.5
ROTATIONS = 24
OUTPUT_NAMES = (
    "SOURCE_LOCK.tsv", "GDT809_GUARDED_QUERY_STATS.tsv", "GDT809_HEAD_POOL_CENSUS.tsv",
    "GDT809_1032_HEAD_OCCURRENCE_ATLAS.tsv", "GDT809_211_HEAD_PIVOT_OCCURRENCE_EDGES.tsv",
    "GDT809_209_HEAD_PIVOT_LINKS.tsv", "GDT809_189_UNIQUE_HEAD_WINDOWS.tsv",
    "GDT809_RELATION_NULL_SCORES.tsv", "GDT809_HEAD_AXIS_RELATION_SCORECARD.tsv",
    "GDT809_ED1_HEAD_AXIS_SENSITIVITY.tsv", "GDT809_EXTERNAL_HEAD_OCCURRENCES.tsv",
    "GDT809_EXTERNAL_RECORD_PROFILES.tsv", "GDT809_HEAD_FEATURE_PROFILES.tsv",
    "GDT809_SEMANTIC_CANDIDATE_SCOREBOARD.tsv", "GDT809_CANDIDATE_GATE_COVERAGE.tsv",
    "GDT809_35_WORKING_DICTIONARY.tsv",
    "GDT809_GDT388_RELATION_PACKET.tsv", "GDT809_GDT388_EDGE_INTAKE.json", "RESULT.json",
)
EDGE_FIELDS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id", "pivot_visual_id",
    "pivot_locus", "target_visual_id", "target_locus", "relation_type", "direction_basis",
    "ownership_basis", "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
    "relation_confidence", "ambiguity_state", "formal_access_state", "fold_assignment",
    "eligibility_status",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str] | None = None) -> None:
    material = list(rows)
    if fields is None:
        if not material:
            raise RuntimeError(f"empty TSV without schema: {path.name}")
        fields = tuple(material[0])
    allowed = set(fields)
    for number, row in enumerate(material, 1):
        extras = set(row) - allowed
        if extras:
            raise RuntimeError(f"unexpected fields in {path.name} row {number}: {sorted(extras)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
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


def split_pipe(value: str) -> tuple[str, ...]:
    return tuple(item for item in value.split("|") if item and item != "NONE")


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


def length_bin(value: int) -> int:
    return int(math.floor(math.log2(value + 1)))


def position_name(index: int, count: int) -> str:
    return "SINGLE" if count == 1 else "FIRST" if index == 1 else "LAST" if index == count else "MIDDLE"


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + int(a != b)))
        previous = current
    return previous[-1]


def assert_no_sealed(rows: Iterable[Mapping[str, Any]]) -> None:
    for row in rows:
        for field in ("page", "source_selector", "locus", "physical_folio", "physical_page"):
            if str(row.get(field, "")).startswith("f84"):
                raise RuntimeError(f"sealed selector materialized: {field}={row.get(field)}")


def guarded_query(path: Path, pages: Sequence[str], columns: Sequence[str], query_id: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    command = [str(VMANUS_EXP), "query-tsv", rel(path), "--selector", "page"]
    for page in sorted(pages, key=selector_sort_key):
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded query failed: {query_id}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError(f"guard stats missing: {query_id}")
    stats = json.loads(stat_lines[0][12:])
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
    stable: tuple[int, ...]


def load_corpus() -> tuple[list[Line], dict[tuple[str, str], Line], dict[str, tuple[str, int, int]], list[dict[str, Any]]]:
    pages = [row["page"] for row in read_tsv(ALLOWLIST)]
    if len(pages) != EXPECTED["selectors"] or len(set(pages)) != len(pages) or any(p.startswith("f84") for p in pages):
        raise RuntimeError("allow-list drift or sealed selector")
    line_rows, line_stats = guarded_query(
        LINES_RAW, pages,
        ("page", "locus", "line_number", "section", "language", "hand", "paragraph_start", "paragraph_end", "token_count", "eva_clean"),
        "ZL3B_LINES_179")
    token_rows, token_stats = guarded_query(
        TOKENS_RAW, pages, ("page", "locus", "token_index", "eva", "section", "language", "hand"),
        "ZL3B_TOKENS_179")
    cross_rows, cross_stats = guarded_query(
        CROSS_RAW, pages,
        ("page", "locus", "all_three_present", "all_present_exact", "zl3b_clean", "it2a_clean", "rf1b_clean"),
        "CROSS_READER_LINES_179")
    if (len(line_rows), len(token_rows), len(cross_rows)) != (EXPECTED["lines"], EXPECTED["tokens"], EXPECTED["lines"]):
        raise RuntimeError("guarded source cardinality drift")
    cross_map = {(row["page"], row["locus"]): row for row in cross_rows}
    token_map: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        token_map[(row["page"], row["locus"])].append(row)
    for key, values in token_map.items():
        values.sort(key=lambda row: int(row["token_index"]))
        if [int(row["token_index"]) for row in values] != list(range(1, len(values) + 1)):
            raise RuntimeError(f"noncontiguous token indexes: {key}")
    lines: list[Line] = []
    for row in sorted(line_rows, key=lambda x: (selector_sort_key(x["page"]), int(x["line_number"]))):
        key = row["page"], row["locus"]
        cross = cross_map[key]
        tokens = tuple(item["eva"] for item in token_map[key])
        if " ".join(tokens) != row["eva_clean"] or row["eva_clean"] != cross["zl3b_clean"] or len(tokens) != int(row["token_count"]):
            raise RuntimeError(f"line/token/cross parity drift at {row['locus']}")
        readers = [cross[name].split() for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        ranks: Counter[str] = Counter()
        stable: list[int] = []
        for surface in tokens:
            ranks[surface] += 1
            stable.append(int(ranks[surface] <= min(reader.count(surface) for reader in readers)))
        lines.append(Line(row["page"], row["locus"], int(row["line_number"]), row["section"],
                          row["language"], row["hand"], row["paragraph_start"] == "1",
                          row["paragraph_end"] == "1", tokens, tuple(stable)))
    by_page: defaultdict[str, list[Line]] = defaultdict(list)
    for line in lines:
        by_page[line.page].append(line)
    paragraph_info: dict[str, tuple[str, int, int]] = {}
    paragraph_count = strict_line_count = strict_token_count = 0
    for page in sorted(by_page, key=selector_sort_key):
        current: list[Line] | None = None
        for line in sorted(by_page[page], key=lambda x: x.number):
            if line.paragraph_start:
                if current is not None:
                    raise RuntimeError(f"nested paragraph at {line.locus}")
                current = []
            if current is None:
                if line.paragraph_end:
                    raise RuntimeError(f"orphan paragraph end at {line.locus}")
                continue
            current.append(line)
            if line.paragraph_end:
                paragraph_count += 1
                paragraph_id = f"G809-P{paragraph_count:04d}"
                if len({(x.section, x.language, x.hand) for x in current}) != 1:
                    raise RuntimeError(f"paragraph metadata drift: {page}:{paragraph_count}")
                for index, member in enumerate(current, 1):
                    paragraph_info[member.locus] = paragraph_id, index, len(current)
                strict_line_count += len(current)
                strict_token_count += sum(len(x.tokens) for x in current)
                current = None
        if current is not None:
            raise RuntimeError(f"unclosed paragraph at {page}")
    if (paragraph_count, strict_line_count, strict_token_count) != (
        EXPECTED["strict_paragraphs"], EXPECTED["strict_lines"], EXPECTED["strict_tokens"]):
        raise RuntimeError("strict paragraph reconstruction drift")
    return lines, {(line.page, line.locus): line for line in lines}, paragraph_info, [line_stats, token_stats, cross_stats]


def build_head_pool() -> tuple[list[dict[str, Any]], set[str], set[str], set[str]]:
    specs = read_tsv(HEAD_SPECS)
    g760 = {row["content_surface"]: row for row in read_tsv(G760_DECK)}
    g764_rows = read_tsv(G764_X_DAIIN)
    g764: dict[str, dict[str, str]] = {}
    for row in g764_rows:
        old = g764.get(row["x_surface"])
        if old and old["x_selected_field_type"] != row["x_selected_field_type"]:
            raise RuntimeError(f"GDT764 role drift: {row['x_surface']}")
        g764[row["x_surface"]] = row
    q152 = {row["surface"] for row in read_tsv(G808_Q152)}
    union = set(g760) | set(g764)
    if (len(g760), len(g764), len(union), len(q152)) != (35, 6, EXPECTED["pool_union"], EXPECTED["q152"]):
        raise RuntimeError("source head-pool cardinality drift")
    spec_map = {row["surface"]: row for row in specs}
    if set(spec_map) != union or len(spec_map) != EXPECTED["pool_union"]:
        raise RuntimeError("registered head-pool surface drift")
    active = union - q152
    if len(active) != EXPECTED["active_heads"]:
        raise RuntimeError("active head count drift")
    balanced = {row["surface"] for row in specs if row["balanced_four_cell_head"] == "1"}
    if balanced != {"dal", "qoty", "sheor", "cheo", "cheal", "chckhey"}:
        raise RuntimeError("balanced head block drift")
    output = []
    for surface in sorted(union):
        spec = spec_map[surface]
        expected_source = pipe(name for name, present in (
            ("GDT760_AMOUNT_CONTENT", surface in g760), ("GDT764_X_DAIIN", surface in g764)) if present)
        source_role = g760[surface]["current_content_axes"] if surface in g760 else g764[surface]["x_selected_field_type"]
        if spec["source_pool"] != expected_source or spec["registered_prior_role"] != source_role:
            raise RuntimeError(f"registered source/role drift: {surface}")
        if int(spec["active_after_q152"]) != int(surface in active) or int(spec["q152_exact_excluded"]) != int(surface in q152):
            raise RuntimeError(f"registered Q152 status drift: {surface}")
        minimum = min(levenshtein(surface, target) for target in q152)
        output.append({**spec, "observed_source_pool": expected_source, "observed_source_role": source_role,
                       "source_pool_evidence_channel": "OBSERVED_SOURCE_MEMBERSHIP",
                       "source_role_evidence_channel": "INHERITED_SEMANTIC_PRIOR",
                       "source_role_is_observed_identity": 0,
                       "source_provenance": pipe(rel(path) for path in (G760_DECK, G764_X_DAIIN)
                                                 if (path == G760_DECK and surface in g760) or (path == G764_X_DAIIN and surface in g764)),
                       "ed1_minimum_to_q152": minimum, "ed1_safe_from_q152": int(minimum > 1),
                       "head_status": "ACTIVE_EXACT_HEAD" if surface in active else "EXACT_Q152_EXCLUDED",
                       "component_export_credit": 0})
    ed1_safe = {row["surface"] for row in output if row["active_after_q152"] == "1" and row["ed1_safe_from_q152"] == 1}
    if len(ed1_safe) != EXPECTED["ed1_safe_heads"]:
        raise RuntimeError("ED1-safe head count drift")
    return output, active, ed1_safe, q152


def visual_map() -> dict[tuple[str, str, int, str], dict[str, str]]:
    output: dict[tuple[str, str, int, str], dict[str, str]] = {}
    rows = read_tsv(G791_VISUAL)
    assert_no_sealed(rows)
    for row in rows:
        key = row["source_selector"], row["locus"], int(row["token_ordinal_in_line"]), row["surface"]
        if key in output:
            raise RuntimeError(f"duplicate GDT791 occurrence: {key}")
        output[key] = row
    return output


def contact_atlases(event_rows: Sequence[dict[str, str]], line_map: Mapping[tuple[str, str], Line],
                     heads: set[str], prefix: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    occurrence_edges: list[dict[str, Any]] = []
    event_heads: defaultdict[str, defaultdict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    event_lookup = {row["event_id"]: row for row in event_rows}
    for event in event_rows:
        line = line_map[event["page"], event["locus"]]
        focal = int(event["token_index"]) - 1
        if line.tokens[focal] != event["surface"]:
            raise RuntimeError(f"GDT808 event/token drift: {event['event_id']}")
        for offset in (-2, -1, 1, 2):
            index = focal + offset
            if 0 <= index < len(line.tokens) and line.stable[index] and line.tokens[index] in heads:
                head = line.tokens[index]
                event_heads[event["event_id"]][head].append(offset)
                occurrence_edges.append({
                    "edge_id": f"{prefix}-OE{len(occurrence_edges) + 1:04d}", "event_id": event["event_id"],
                    "head": head, "signed_offset": offset, "axis": event["axis"],
                    "expanded_label": event["expanded_label"], "pivot_surface": event["surface"],
                    "carrier": event["carrier"], "page": event["page"],
                    "physical_folio": event["physical_folio"], "locus": event["locus"],
                    "pivot_token_index": event["token_index"], "head_token_index": index + 1,
                    "rank_stable_head": 1, "semantic_credit": 0, "component_export_credit": 0})
    links: list[dict[str, Any]] = []
    unique_rows: list[dict[str, Any]] = []
    unique_map: dict[str, str] = {}
    for event_id in sorted(event_heads, key=lambda value: int(value.split("E")[-1])):
        event = event_lookup[event_id]
        distinct = len(event_heads[event_id])
        for head in sorted(event_heads[event_id]):
            offsets = sorted(event_heads[event_id][head])
            row = {
                "link_id": f"{prefix}-L{len(links) + 1:04d}", "event_id": event_id, "head": head,
                "axis": event["axis"], "expanded_label": event["expanded_label"],
                "direction_label": "EXPANDED" if event["expanded_label"] == "1" else "BASE",
                "pivot_surface": event["surface"], "carrier": event["carrier"], "page": event["page"],
                "physical_folio": event["physical_folio"], "locus": event["locus"],
                "pivot_token_index": event["token_index"], "signed_offsets": pipe(offsets),
                "head_occurrence_edges": len(offsets), "distinct_heads_in_window": distinct,
                "primary_unique_head_window": int(distinct == 1),
                "weighted_sensitivity_weight": f12(1 / distinct), "semantic_credit": 0,
                "component_export_credit": 0}
            links.append(row)
            if distinct == 1:
                unique_map[event_id] = head
                unique_rows.append({"primary_window_id": f"{prefix}-U{len(unique_rows) + 1:04d}", **row})
    return occurrence_edges, links, unique_rows, unique_map


def rotated_labels(events: Sequence[dict[str, str]], rotation: int) -> tuple[dict[str, int], int]:
    groups: defaultdict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for event in events:
        groups[(event["axis"], event["carrier"], event["section"], event["language"],
                event["hand"], event["targetfree_line_length_bin"])].append(event)
    labels: dict[str, int] = {}
    moved = 0
    for values in groups.values():
        ordered = sorted(values, key=lambda row: (selector_sort_key(row["page"]), int(row["line_number"]),
                                                  int(row["token_index"]), row["event_id"]))
        count = len(ordered)
        for index, row in enumerate(ordered):
            label = int(ordered[(index - rotation % count) % count]["expanded_label"])
            labels[row["event_id"]] = label
            moved += int(label != int(row["expanded_label"]))
    return labels, moved


def association(events: Sequence[dict[str, str]], unique_map: Mapping[str, str], head: str, axis: str,
                labels: Mapping[str, int], excluded_folio: str | None = None) -> dict[str, Any]:
    a = b = c = d = 0
    contact_folios: set[str] = set()
    for event in events:
        if event["axis"] != axis or (excluded_folio is not None and event["physical_folio"] == excluded_folio):
            continue
        is_head = unique_map.get(event["event_id"]) == head
        label = labels[event["event_id"]]
        if is_head:
            contact_folios.add(event["physical_folio"])
            if label:
                a += 1
            else:
                b += 1
        elif label:
            c += 1
        else:
            d += 1
    log_or = math.log((a + ALPHA) * (d + ALPHA) / ((b + ALPHA) * (c + ALPHA)))
    return {"expanded": a, "base": b, "other_expanded": c, "other_base": d,
            "log_or": log_or, "contact_folios": contact_folios}


RECORD_FIELDS = ("section", "language", "hand", "line_position", "paragraph_line_position", "targetfree_line_length_bin")


def event_record_features(event: Mapping[str, str], paragraph_info: Mapping[str, tuple[str, int, int]]) -> dict[str, str]:
    _, pindex, pcount = paragraph_info[event["locus"]]
    return {"section": event["section"], "language": event["language"], "hand": event["hand"],
            "line_position": position_name(int(event["token_index"]), int(event["line_token_count"])),
            "paragraph_line_position": position_name(pindex, pcount),
            "targetfree_line_length_bin": event["targetfree_line_length_bin"]}


def record_model(events: Sequence[dict[str, str]], axis: str, excluded_folios: set[str],
                 paragraph_info: Mapping[str, tuple[str, int, int]]) -> dict[str, Any]:
    train = [row for row in events if row["axis"] == axis and row["physical_folio"] not in excluded_folios]
    cells = Counter((row["carrier"], int(row["expanded_label"])) for row in train)
    counts = {field: {0: Counter(), 1: Counter()} for field in RECORD_FIELDS}
    totals = {field: {0: 0.0, 1: 0.0} for field in RECORD_FIELDS}
    vocabulary = {field: set() for field in RECORD_FIELDS}
    for row in train:
        label = int(row["expanded_label"])
        weight = 1 / cells[(row["carrier"], label)]
        for field, value in event_record_features(row, paragraph_info).items():
            counts[field][label][value] += weight
            totals[field][label] += weight
            vocabulary[field].add(value)
    return {"counts": counts, "totals": totals, "vocabulary": vocabulary,
            "training_events": len(train), "training_folios": len({row["physical_folio"] for row in train}),
            "training_folio_set": {row["physical_folio"] for row in train}}


def score_record(model: Mapping[str, Any], features: Mapping[str, str]) -> float:
    score = 0.0
    for field in RECORD_FIELDS:
        values = model["vocabulary"][field]
        if not values:
            continue
        value = features[field]
        positive = (model["counts"][field][1][value] + ALPHA) / (model["totals"][field][1] + ALPHA * len(values))
        negative = (model["counts"][field][0][value] + ALPHA) / (model["totals"][field][0] + ALPHA * len(values))
        score += math.log(positive / negative)
    return score


def build_occurrences(lines: Sequence[Line], paragraph_info: Mapping[str, tuple[str, int, int]], active: set[str],
                      q152: set[str], event_rows: Sequence[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    discovery = {(row["page"], row["locus"], int(row["content_ordinal"])) for row in read_tsv(G760_ATTACH)
                 if row["content_surface"] in active}
    discovery.update({(row["page"], row["locus"], int(row["x_ordinal"])) for row in read_tsv(G764_X_DAIIN)
                      if row["x_surface"] in active})
    pivots: defaultdict[tuple[str, str], list[int]] = defaultdict(list)
    for event in event_rows:
        pivots[event["page"], event["locus"]].append(int(event["token_index"]))
    visuals = visual_map()
    landmarks = [(row["landmark_id"], set(split_pipe(row["surfaces"])), row["structural_tag"], int(row["maximum_radius"]))
                 for row in read_tsv(LANDMARK_SPECS)]
    all_rows: list[dict[str, Any]] = []
    external_rows: list[dict[str, Any]] = []
    for line in lines:
        pinfo = paragraph_info.get(line.locus)
        for index, surface in enumerate(line.tokens, 1):
            if surface not in active or not line.stable[index - 1]:
                continue
            near_pivots = [abs(index - pivot) for pivot in pivots.get((line.page, line.locus), [])]
            minimum_pivot_distance = min(near_pivots) if near_pivots else 999
            is_discovery = (line.page, line.locus, index) in discovery
            external = not is_discovery and minimum_pivot_distance > 2
            visual = visuals.get((line.page, line.locus, index, surface), {})
            hits: list[str] = []
            hit_tags: set[str] = set()
            if external:
                for landmark_id, landmark_surfaces, tag, radius in landmarks:
                    for other_index, other in enumerate(line.tokens, 1):
                        if other_index != index and abs(other_index - index) <= radius and other in landmark_surfaces:
                            hits.append(f"{landmark_id}:{tag}:{other}@{other_index - index:+d}")
                            hit_tags.add(tag)
            paragraph_id, paragraph_index, paragraph_count = pinfo if pinfo else ("NONE", 0, 0)
            row = {
                "occurrence_id": f"G809-HO{len(all_rows) + 1:04d}", "head": surface, "page": line.page,
                "physical_folio": physical_folio(line.page), "locus": line.locus, "line_number": line.number,
                "token_index": index, "line_token_count": len(line.tokens),
                "line_position": position_name(index, len(line.tokens)), "section": line.section,
                "language": line.language, "hand": line.hand, "rank_stable_all_three": 1,
                "strict_paragraph": int(pinfo is not None), "paragraph_id": paragraph_id,
                "paragraph_line_index": paragraph_index if pinfo else "NA",
                "paragraph_line_count": paragraph_count if pinfo else "NA",
                "paragraph_line_position": position_name(paragraph_index, paragraph_count) if pinfo else "OUTSIDE",
                "targetfree_line_length_bin": length_bin(sum(token not in q152 for token in line.tokens)),
                "source_discovery_coordinate": int(is_discovery),
                "minimum_core_pivot_distance": minimum_pivot_distance if near_pivots else "NONE",
                "strict_external_occurrence": int(external), "landmark_tags": pipe(sorted(hit_tags)),
                "landmark_hits": pipe(sorted(hits)), "visual_occurrence_kind": visual.get("occurrence_kind", "NONE"),
                "visual_topology_family": visual.get("topology_family", "NONE"),
                "visual_context_scope": visual.get("context_scope", "NONE"),
                "visual_owner_id": visual.get("context_owner_id", "NONE"),
                "visual_evidence_channel": "CACHED_CONTEXT_NOT_TOKEN_PART_OWNER" if visual else "UNOBSERVED",
                "visual_source_provenance": rel(G791_VISUAL) if visual else "NONE",
                "occurrence_source_provenance": pipe((rel(LINES_RAW), rel(TOKENS_RAW), rel(CROSS_RAW))),
                "written_line_eva": " ".join(line.tokens), "literal_credit": 0, "component_export_credit": 0}
            all_rows.append(row)
            if external:
                external_rows.append({"external_id": f"G809-EX{len(external_rows) + 1:04d}", **row})
    if len(all_rows) != EXPECTED["stable_head_occurrences"]:
        raise RuntimeError(f"stable head occurrence drift: {len(all_rows)}")
    return all_rows, external_rows


def relation_tables(event_rows: Sequence[dict[str, str]], unique_map: Mapping[str, str], links: Sequence[dict[str, Any]],
                    active: set[str], external: Sequence[dict[str, Any]], paragraph_info: Mapping[str, tuple[str, int, int]],
                    population: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    observed_labels = {row["event_id"]: int(row["expanded_label"]) for row in event_rows}
    rotations: list[dict[str, int]] = []
    mobility: dict[int, float] = {}
    for k in range(1, ROTATIONS + 1):
        labels, moved = rotated_labels(event_rows, k)
        rotations.append(labels)
        mobility[k] = moved / len(event_rows)
    weighted: defaultdict[tuple[str, str, int], float] = defaultdict(float)
    for row in links:
        weighted[row["head"], row["axis"], int(row["expanded_label"])] += float(row["weighted_sensitivity_weight"])
    external_by_head: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in external:
        external_by_head[row["head"]].append(row)
    null_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    decision_specs = read_tsv(RELATION_SPECS)
    for head in sorted(active):
        for axis in ("L", "DY"):
            observed = association(event_rows, unique_map, head, axis, observed_labels)
            null_values: list[float] = []
            null_rows.append({"population": population, "head": head, "axis": axis, "null_id": "OBSERVED",
                              "expanded_contacts": observed["expanded"], "base_contacts": observed["base"],
                              "haldane_log_or": f12(observed["log_or"]),
                              "absolute_log_or": f12(abs(observed["log_or"])), "changed_label_fraction": 0,
                              "observed_reference": 1, "ties_count_against_head": 1})
            for k, labels in enumerate(rotations, 1):
                result = association(event_rows, unique_map, head, axis, labels)
                null_values.append(result["log_or"])
                null_rows.append({"population": population, "head": head, "axis": axis, "null_id": f"K{k:02d}",
                                  "expanded_contacts": result["expanded"], "base_contacts": result["base"],
                                  "haldane_log_or": f12(result["log_or"]),
                                  "absolute_log_or": f12(abs(result["log_or"])),
                                  "changed_label_fraction": f12(mobility[k]), "observed_reference": 0,
                                  "ties_count_against_head": 1})
            rank = 1 + sum(abs(value) >= abs(observed["log_or"]) - 1e-12 for value in null_values)
            contact_folios = observed["contact_folios"]
            jackknife = [association(event_rows, unique_map, head, axis, observed_labels, folio)["log_or"]
                         for folio in sorted(contact_folios)]
            sign_agreement = (sum(value * observed["log_or"] > 0 for value in jackknife) / len(jackknife)) if jackknife else 0.0
            contact_external = [row for row in external_by_head[head]
                                if row["strict_paragraph"] == 1 and row["physical_folio"] not in contact_folios]
            model = record_model(event_rows, axis, contact_folios, paragraph_info)
            external_folios = {row["physical_folio"] for row in contact_external}
            overlap = external_folios & model["training_folio_set"]
            external_scores = [score_record(model, {field: str(row[field]) for field in RECORD_FIELDS})
                               for row in contact_external]
            mean_external = math.fsum(external_scores) / len(external_scores) if external_scores else None
            external_agrees = int(mean_external is not None and mean_external * observed["log_or"] > 0)
            primary_n = observed["expanded"] + observed["base"]
            metrics = {"primary_unique_events": primary_n, "primary_contact_folios": len(contact_folios),
                       "absolute_haldane_log_or": abs(observed["log_or"]),
                       "target_rotation_absolute_rank": rank,
                       "leave_one_contact_folio_sign_agreement": sign_agreement,
                       "folio_disjoint_external_occurrences": len(contact_external),
                       "external_record_compatibility_direction_agrees": external_agrees}
            local_pass = int(decision_gate(decision_specs, "LOCAL_ASSOCIATION_PASS", metrics))
            relation_pass = int(local_pass and decision_gate(decision_specs, "RELATION_CONDITIONED_RECORD_HEAD", metrics))
            weighted_expanded = weighted[head, axis, 1]
            weighted_base = weighted[head, axis, 0]
            other_expanded = sum(int(row["expanded_label"]) for row in event_rows if row["axis"] == axis) - weighted_expanded
            other_base = sum(1 - int(row["expanded_label"]) for row in event_rows if row["axis"] == axis) - weighted_base
            weighted_log_or = math.log((weighted_expanded + ALPHA) * (other_base + ALPHA)
                                       / ((weighted_base + ALPHA) * (other_expanded + ALPHA)))
            score_rows.append({
                "population": population, "head": head, "axis": axis, "primary_unique_events": primary_n,
                "primary_contact_folios": len(contact_folios), "base_contacts": observed["base"],
                "expanded_contacts": observed["expanded"], "haldane_log_or": f12(observed["log_or"]),
                "absolute_haldane_log_or": f12(abs(observed["log_or"])),
                "direction": direction_name(observed["log_or"]),
                "target_rotation_absolute_rank": rank, "target_rotation_denominator": ROTATIONS + 1,
                "leave_one_contact_folio_sign_agreement": f12(sign_agreement),
                "weighted_base_contacts": f12(weighted_base), "weighted_expanded_contacts": f12(weighted_expanded),
                "weighted_haldane_log_or": f12(weighted_log_or),
                "weighted_direction_agrees": int(weighted_log_or * observed["log_or"] > 0),
                "folio_disjoint_external_occurrences": len(contact_external),
                "folio_disjoint_external_folios": len({row["physical_folio"] for row in contact_external}),
                "external_record_compatibility_mean_score": f12(mean_external),
                "external_record_compatibility_direction": direction_name(mean_external),
                "external_record_compatibility_direction_agrees": external_agrees,
                "record_training_external_overlap_folios": len(overlap),
                "record_training_external_overlap_occurrences": sum(row["physical_folio"] in overlap for row in contact_external),
                "record_compatibility_not_independent_semantics": 1, "local_association_pass": local_pass,
                "relation_conditioned_record_head": relation_pass, "literal_credit": 0,
                "component_export_credit": 0})
            profile_rows.append({
                "population": population, "head": head, "axis": axis,
                "excluded_contact_folios": pipe(sorted(contact_folios)),
                "record_model_training_events": model["training_events"],
                "record_model_training_folios": model["training_folios"],
                "folio_disjoint_external_occurrences": len(contact_external),
                "folio_disjoint_external_folios": len({row["physical_folio"] for row in contact_external}),
                "external_record_compatibility_mean_score": f12(mean_external),
                "external_record_compatibility_direction": direction_name(mean_external),
                "direct_relation_direction": direction_name(observed["log_or"]),
                "direction_agrees": external_agrees, "model_features": pipe(RECORD_FIELDS),
                "record_training_external_overlap_folios": len(overlap),
                "record_training_external_overlap_folio_ids": pipe(sorted(overlap, key=selector_sort_key)),
                "record_training_external_overlap_occurrences": sum(row["physical_folio"] in overlap for row in contact_external),
                "evidence_channel": "FORMAL_RECORD_COMPATIBILITY",
                "source_provenance": pipe((rel(G808_EVENTS), rel(LINES_RAW), rel(TOKENS_RAW), rel(CROSS_RAW))),
                "record_compatibility_not_independent_semantics": 1,
                "semantic_credit": 0, "component_export_credit": 0})
    return score_rows, null_rows, profile_rows


def direction_name(score: float | None) -> str:
    return "NA" if score is None else "EXPANDED" if score > 0 else "BASE" if score < 0 else "TIE"


def decision_gate(specs: Sequence[Mapping[str, str]], applies_to: str, metrics: Mapping[str, Any]) -> bool:
    selected = [row for row in specs if row["applies_to"] == applies_to]
    if not selected:
        raise RuntimeError(f"missing decision specification: {applies_to}")
    comparisons = {"GE": lambda a, b: a >= b, "LE": lambda a, b: a <= b, "EQ": lambda a, b: a == b}
    return all(comparisons[row["operator"]](float(metrics[row["metric"]]), float(row["threshold"])) for row in selected)


def prior_tag(role: str, name: str) -> bool:
    return name in role.split("|") or name in role


def role_default(role: str) -> str:
    if "QUALITY_HEAD" in role:
        return "Qualitäts-/Gradkopf"
    if "MATERIAL_MEASURE" in role:
        return "abgemessener Material-/Wertkopf"
    if "NOMINAL_FIELD" in role:
        return "nominales Inhalts-/Wertfeld"
    if "OPEN_FIELD" in role:
        return "offenes Inhalts-/Wertfeld"
    if "PART" in role and "MATERIAL" in role:
        return "Drogenteil oder Pflanzenmaterial"
    if "PREPARATION" in role and "PROCESS" in role:
        return "Zubereitungs- oder Vorgangskopf"
    if "PREPARATION" in role:
        return "Zubereitungskopf"
    if "MATERIAL" in role:
        return "Drogenmaterialkopf"
    if "AMOUNT" in role:
        return "mengenbezogener Kopf"
    return "offener gelernter Ganzwortkopf"


# This registry distinguishes implemented measurements from requested but absent
# candidate discriminators. Adding a name to a profile never creates evidence.
GATE_REQUIREMENTS = {
    "PATIENT_MEDIUM_DURATION_OR_PROCESS": "independently grounded patient, medium and ordered duration/process",
    "QUALIFIED_OR_ADMIN_MEDIUM": "independently grounded qualified or administered medium",
    "PRODUCED_RESULT_OR_MEASURED_MIXING_MEDIUM": "independently grounded produced result or mixing medium",
    "SALT_SPECIFIC_ANCHOR": "salt-specific independent anchor",
    "MANUAL_LEAF_OWNER_MULTI_FOLIO": "direct leaf-specific token owners on multiple folios",
    "MANUAL_ROOT_OWNER_MULTI_FOLIO": "direct root-specific token owners on multiple folios",
    "MANUAL_FLOWER_OWNER_MULTI_FOLIO": "direct flower-specific token owners on multiple folios",
    "MANUAL_SEED_OWNER_MULTI_FOLIO": "direct seed-specific token owners on multiple folios",
    "MULTI_NAME_INGREDIENT_LIST": "independently grounded command-governed multiple-ingredient list",
    "POWDER_SPECIFIC_ANCHOR": "powder-specific independent anchor",
    "MANUAL_WOOD_OWNER_MULTI_FOLIO": "direct wood-specific token owners on multiple folios",
    "SOLID_PATIENT_THEN_MIX_OR_SIEVE": "independently grounded solid patient and ordered mixing/sieving",
    "MULTIPLE_PATIENTS_THEN_NEXT_STEP": "independently grounded multiple patients and ordered successor step",
    "UPSTREAM_LIQUID_THEN_RESULT": "independently grounded upstream liquid and ordered result",
    "PATIENT_HOT_PROCESS_ENDPOINT": "independently grounded patient, hot process and endpoint",
    "PATIENT_DRY_PROCESS_FORM_OR_STORAGE": "independently grounded patient, drying and resulting form/storage",
    "MANUAL_VESSEL_OWNER_MULTI_FOLIO": "direct vessel-specific token owners on multiple folios",
    "QUALITY_IDENTITY_DIRECTION_ANCHOR": "independent quality/degree identity and orientation anchor",
    "MANUAL_AERIAL_HERB_OWNER_MULTI_FOLIO": "direct aerial-herb-specific token owners on multiple folios",
    "BOTANICAL_HEAD_DISCRIMINATING_SIGNATURE": "head-specific discriminator between named part and opaque botanical head",
}
PRIOR_FEATURES = {f"PRIOR_{name}" for name in (
    "DRY", "MOIST", "HOT", "COLD", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "AMOUNT", "QUALITY"
)} | {"MEDIUM_ROLE_PROXY", "LIQUID_OR_PRODUCT_PROXY", "DRY_INGREDIENT_PROXY", "QUALITY_VALUE_FIELD",
      "GDT764_QUALITY_GRADE_FIELD", "EXACT_QUALITY_VALUE_PARALLEL"}
FEATURE_PRODUCERS: dict[str, tuple[str, tuple[Path, ...]]] = {
    **{feature: ("INHERITED_SEMANTIC_PRIOR", (HEAD_SPECS, G760_DECK, G764_X_DAIIN)) for feature in PRIOR_FEATURES},
    "SOURCE_CONTENT_HEAD": ("SOURCE_POOL_MEMBERSHIP", (G760_DECK,)),
    "SOURCE_VALUE_FIELD_HEAD": ("SOURCE_POOL_MEMBERSHIP", (G764_X_DAIIN,)),
    "VALUE_FIELD_ANY": ("OBSERVED_EXACT_X_DAIIN_FRAME", (G764_X_DAIIN,)),
    **{feature: ("OBSERVED_INHERITED_ATTACHMENT_COORDINATES", (G760_DECK, G760_ATTACH)) for feature in (
        "AMOUNT_CONTACT_ANY", "AMOUNT_CONTACT_RECURRENT", "AMOUNT_CONTACT_3_FOLIOS")},
    **{feature: ("OBSERVED_CACHED_REGISTER_POSITION", (LINES_RAW, TOKENS_RAW, CROSS_RAW)) for feature in (
        "EXTERNAL_3_FOLIOS", "HERBAL_DOMINANT_75", "HERBAL_DOMINANT_90", "NONHERBAL_DOMINANT_75",
        "LINE_FIRST_20", "LINE_LAST_20", "PARAGRAPH_START_20")},
    **{feature: ("OBSERVED_EXACT_LANDMARK_PROXIMITY", (LANDMARK_SPECS, TOKENS_RAW, CROSS_RAW)) for feature in (
        "NEAR_CHOR_SHOR_2_FOLIOS", "NEAR_CTHY_2_FOLIOS", "NEAR_VALUE_FORM_2_FOLIOS", "NEAR_AMOUNT_2_FOLIOS")},
    **{feature: ("CACHED_VISUAL_CONTEXT_NOT_TOKEN_OWNER", (G791_VISUAL,)) for feature in (
        "VISUAL_WHOLE_PLANT_3", "VISUAL_POOL_3", "VISUAL_MATERIAL_3", "VISUAL_RADIAL_3", "VISUAL_TEXT_3")},
    **{feature: ("FORMAL_RECORD_COMPATIBILITY", (G808_EVENTS, RELATION_SPECS, RUN)) for feature in (
        "REL_L_BASE", "REL_L_EXPANDED", "REL_DY_BASE", "REL_DY_EXPANDED",
        "REL_EXTERNAL_RECORD_AGREES", "REL_ED1_SAFE")},
    "BOTANICAL_PAGE_CONTEXT_MULTI_FOLIO": ("INHERITED_REPORTED_BOTANICAL_CONTEXT", (G625_REPORT, MANUAL_SPECS)),
}


def feature_state(feature: str, present: set[str]) -> str:
    if feature in PRIOR_FEATURES:
        return "PRIOR_PRESENT" if feature in present else "PRIOR_NOT_LISTED"
    if feature in FEATURE_PRODUCERS:
        return "OBSERVED_PRESENT" if feature in present else "OBSERVED_NOT_MET"
    if feature in GATE_REQUIREMENTS:
        return "UNOBSERVED"
    raise RuntimeError(f"unregistered semantic feature or gate: {feature}")


def feature_sources(features: Iterable[str]) -> str:
    return pipe(sorted({rel(path) for feature in features for path in FEATURE_PRODUCERS.get(feature, ("", ()))[1]}))


def feature_channels(features: Iterable[str]) -> str:
    return pipe(sorted({FEATURE_PRODUCERS[feature][0] for feature in features if feature in FEATURE_PRODUCERS}))


def feature_provenance(features: Iterable[str]) -> str:
    return pipe(f"{feature}:{FEATURE_PRODUCERS[feature][0]}:{','.join(rel(path) for path in FEATURE_PRODUCERS[feature][1])}"
                for feature in sorted(features) if feature in FEATURE_PRODUCERS)


def feature_profiles(external: Sequence[dict[str, Any]], pool_map: Mapping[str, dict[str, Any]],
                     relation_rows: Sequence[dict[str, Any]], ed1_rows: Sequence[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    external_by_head: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in external:
        external_by_head[row["head"]].append(row)
    amount_map = {row["content_surface"]: row for row in read_tsv(G760_DECK)}
    value_rows: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(G764_X_DAIIN):
        value_rows[row["x_surface"]].append(row)
    manual: defaultdict[str, set[str]] = defaultdict(set)
    for row in read_tsv(MANUAL_SPECS):
        tags = set(split_pipe(row["evidence_tags"]))
        if tags - FEATURE_PRODUCERS.keys() or tags & GATE_REQUIREMENTS.keys():
            raise RuntimeError("manual context cannot create an unregistered identity discriminator")
        if row["measurement_state"] != "PRIOR":
            manual[row["surface"]].update(tags)
    relation_map = {(row["head"], row["axis"]): row for row in relation_rows}
    ed1_map = {(row["head"], row["axis"]): row for row in ed1_rows}
    output: list[dict[str, Any]] = []
    feature_map: dict[str, set[str]] = {}
    for head in sorted(pool_map):
        spec = pool_map[head]
        values = external_by_head[head]
        tags: set[str] = set(manual[head])
        if "GDT760_AMOUNT_CONTENT" in spec["source_pool"]:
            tags.add("SOURCE_CONTENT_HEAD")
        if "GDT764_X_DAIIN" in spec["source_pool"]:
            tags.update(("SOURCE_VALUE_FIELD_HEAD", "VALUE_FIELD_ANY"))
        role = spec["registered_prior_role"]
        for name in ("DRY", "MOIST", "HOT", "COLD", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "AMOUNT", "QUALITY"):
            if prior_tag(role, name):
                tags.add(f"PRIOR_{name}")
        amount = amount_map.get(head)
        if amount:
            attachments, pages = int(amount["amount_attachment_occurrences"]), int(amount["amount_attachment_pages"])
            if attachments:
                tags.add("AMOUNT_CONTACT_ANY")
            if attachments >= 2:
                tags.add("AMOUNT_CONTACT_RECURRENT")
            if pages >= 3:
                tags.add("AMOUNT_CONTACT_3_FOLIOS")
        if any(row["selected_local_dispatch"] == "QUALITY_GRADE_III" for row in value_rows[head]):
            tags.update(("GDT764_QUALITY_GRADE_FIELD", "EXACT_QUALITY_VALUE_PARALLEL"))
        folios = {row["physical_folio"] for row in values}
        if len(folios) >= 3:
            tags.add("EXTERNAL_3_FOLIOS")
        section = Counter(row["section"] for row in values)
        count = len(values)
        herbal_share = section["H"] / count if count else 0.0
        if count and herbal_share >= .75:
            tags.add("HERBAL_DOMINANT_75")
        if count and herbal_share >= .90:
            tags.add("HERBAL_DOMINANT_90")
        if count and 1 - herbal_share >= .75:
            tags.add("NONHERBAL_DOMINANT_75")
        line_positions = Counter(row["line_position"] for row in values)
        paragraph_positions = Counter(row["paragraph_line_position"] for row in values if row["strict_paragraph"] == 1)
        strict_count = sum(int(row["strict_paragraph"]) for row in values)
        if count and line_positions["FIRST"] / count >= .20:
            tags.add("LINE_FIRST_20")
        if count and line_positions["LAST"] / count >= .20:
            tags.add("LINE_LAST_20")
        if strict_count and paragraph_positions["FIRST"] / strict_count >= .20:
            tags.add("PARAGRAPH_START_20")
        landmark_folios: defaultdict[str, set[str]] = defaultdict(set)
        for row in values:
            for tag in split_pipe(str(row["landmark_tags"])):
                landmark_folios[tag].add(row["physical_folio"])
        for tag, feature in {"NEAR_CHOR_SHOR": "NEAR_CHOR_SHOR_2_FOLIOS", "NEAR_CTHY": "NEAR_CTHY_2_FOLIOS",
                             "NEAR_VALUE_FORM": "NEAR_VALUE_FORM_2_FOLIOS", "NEAR_AMOUNT_FORM": "NEAR_AMOUNT_2_FOLIOS"}.items():
            if len(landmark_folios[tag]) >= 2:
                tags.add(feature)
        visual_counts = Counter(row["visual_topology_family"] for row in values if row["visual_topology_family"] != "NONE")
        for topology, feature in {"WHOLE_PLANT_ARTICLE": "VISUAL_WHOLE_PLANT_3", "POOL_APPARATUS_NETWORK": "VISUAL_POOL_3",
                                  "MATERIAL_REGISTER": "VISUAL_MATERIAL_3", "RADIAL_ARRAY": "VISUAL_RADIAL_3",
                                  "TEXT_BLOCK": "VISUAL_TEXT_3"}.items():
            if visual_counts[topology] >= 3:
                tags.add(feature)
        if "PRIOR_MOIST" in tags and "PRIOR_PREPARATION" in tags:
            tags.add("MEDIUM_ROLE_PROXY")
        if "PRIOR_PREPARATION" in tags and tags & {"PRIOR_MOIST", "PRIOR_COLD", "PRIOR_CLOSE"}:
            tags.add("LIQUID_OR_PRODUCT_PROXY")
        if "PRIOR_DRY" in tags and "PRIOR_MATERIAL" in tags and "PRIOR_PREPARATION" not in tags:
            tags.add("DRY_INGREDIENT_PROXY")
        if "SOURCE_VALUE_FIELD_HEAD" in tags and tags & {"PRIOR_QUALITY", "PRIOR_COLD", "PRIOR_HOT", "PRIOR_DRY", "PRIOR_MOIST"}:
            tags.add("QUALITY_VALUE_FIELD")
        relation_summaries = []
        for axis in ("L", "DY"):
            relation = relation_map[head, axis]
            if int(relation["relation_conditioned_record_head"]):
                direction = relation["direction"]
                tags.update((f"REL_{axis}_{direction}", "REL_EXTERNAL_RECORD_AGREES"))
                relation_summaries.append(f"{axis}:{direction}:rank{relation['target_rotation_absolute_rank']}")
                ed1 = ed1_map.get((head, axis))
                if ed1 and int(ed1["relation_conditioned_record_head"]) and ed1["direction"] == direction:
                    tags.add("REL_ED1_SAFE")
        feature_map[head] = tags
        if tags - FEATURE_PRODUCERS.keys():
            raise RuntimeError(f"unregistered feature producer: {sorted(tags - FEATURE_PRODUCERS.keys())}")
        output.append({
            "head": head, "registered_prior_role": role, "role_default_de": role_default(role),
            "external_occurrences": count, "external_folios": len(folios),
            "external_herbal_occurrences": section["H"], "external_herbal_share": f12(herbal_share),
            "external_line_first": line_positions["FIRST"], "external_line_last": line_positions["LAST"],
            "external_paragraph_first_lines": paragraph_positions["FIRST"],
            "near_chor_shor_folios": len(landmark_folios["NEAR_CHOR_SHOR"]),
            "near_cthy_folios": len(landmark_folios["NEAR_CTHY"]),
            "near_value_form_folios": len(landmark_folios["NEAR_VALUE_FORM"]),
            "near_amount_form_folios": len(landmark_folios["NEAR_AMOUNT_FORM"]),
            "visual_whole_plant_occurrences": visual_counts["WHOLE_PLANT_ARTICLE"],
            "visual_pool_occurrences": visual_counts["POOL_APPARATUS_NETWORK"],
            "visual_material_occurrences": visual_counts["MATERIAL_REGISTER"],
            "visual_radial_occurrences": visual_counts["RADIAL_ARRAY"],
            "relation_summary": pipe(relation_summaries), "evidence_features": pipe(sorted(tags)),
            "inherited_prior_features": pipe(sorted(tags & PRIOR_FEATURES)),
            "observed_compatibility_features": pipe(sorted(tags - PRIOR_FEATURES)),
            "evidence_channels": feature_channels(tags), "source_provenance": feature_sources(tags),
            "feature_provenance": feature_provenance(tags),
            "independent_candidate_identity_evidence": "UNOBSERVED",
            "literal_credit": 0, "component_export_credit": 0})
    return output, feature_map


def semantic_tournament(feature_rows: Sequence[dict[str, Any]], feature_map: Mapping[str, set[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    profiles = read_tsv(SEMANTIC_SPECS)
    decision_specs = read_tsv(RELATION_SPECS)
    if not decision_gate(decision_specs, "ALL_CANDIDATES", {"identity_promotion_authorized": 0}):
        raise RuntimeError("candidate deck cannot grant literal identity promotion authority")
    if len({row["candidate_id"] for row in profiles}) != len(profiles):
        raise RuntimeError("duplicate semantic candidate identifier")
    if not {f"S{number:02d}" for number in range(1, 19)} <= {row["candidate_id"] for row in profiles}:
        raise RuntimeError("an original exploratory candidate was removed")
    external_folios = {row["head"]: int(row["external_folios"]) for row in feature_rows}
    raw: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for head in sorted(feature_map):
        features = feature_map[head]
        for profile in profiles:
            required, positive = set(split_pipe(profile["required_features"])), set(split_pipe(profile["positive_features"]))
            negative, gate = set(split_pipe(profile["hard_negative_features"])), set(split_pipe(profile["candidate_specific_gate"]))
            if not gate or not gate <= GATE_REQUIREMENTS.keys():
                raise RuntimeError(f"candidate gate lacks independent discriminator registration: {profile['candidate_id']}")
            all_features = required | positive | negative | gate
            states = {feature: feature_state(feature, features) for feature in all_features}
            observed = {feature for feature, state in states.items() if state == "OBSERVED_PRESENT"}
            observed_required = required - PRIOR_FEATURES
            matched_required, matched_positive = required & observed, positive & observed
            matched_negative = negative & observed
            matched_gate = gate & observed
            matched_prior = all_features & features & PRIOR_FEATURES
            score = 2 * len(matched_required) + len(matched_positive) - 2 * len(matched_negative)
            prior_score = 2 * len(required & matched_prior) + len(positive & matched_prior) - 2 * len(negative & matched_prior)
            for feature in sorted(gate):
                producer = FEATURE_PRODUCERS.get(feature)
                coverage.append({
                    "head": head, "candidate_id": profile["candidate_id"], "candidate_de": profile["candidate_de"],
                    "candidate_gate_feature": feature, "gate_state": states[feature],
                    "observed_gate_value": "NA" if producer is None else int(feature in observed),
                    "registered_producer_available": int(producer is not None),
                    "gate_reachable_from_current_inputs": int(producer is not None and feature not in PRIOR_FEATURES),
                    "evidence_channel": producer[0] if producer else "UNOBSERVED_CANDIDATE_SPECIFIC_EVIDENCE",
                    "source_provenance": feature_sources((feature,)), "requirement_spec_source": rel(SEMANTIC_SPECS),
                    "required_new_discriminator": GATE_REQUIREMENTS[feature],
                    "unobserved_is_not_counterevidence": 1, "literal_identity_promotion_authorized": 0,
                    "confirmed_lexeme": 0, "component_export_credit": 0})
            raw.append({
                "head": head, "candidate_id": profile["candidate_id"], "candidate_de": profile["candidate_de"],
                "historical_lemma": profile["historical_lemma"], "family": profile["family"], "score": score,
                "score_channel": "OBSERVED_CONTEXT_COMPATIBILITY_NOT_IDENTITY", "inherited_prior_score": prior_score,
                "inherited_prior_discriminatory_credit": 0, "matched_inherited_prior_features": pipe(sorted(matched_prior)),
                "required_matches": len(matched_required), "required_total": len(observed_required),
                "required_complete": int(matched_required == observed_required),
                "matched_required_features": pipe(sorted(matched_required)),
                "missing_required_features": pipe(sorted(observed_required - observed)),
                "inherited_prior_required_features": pipe(sorted(required & PRIOR_FEATURES)),
                "positive_matches": len(matched_positive), "positive_total": len(positive - PRIOR_FEATURES),
                "matched_positive_features": pipe(sorted(matched_positive)),
                "hard_negative_matches": len(matched_negative),
                "matched_hard_negative_features": pipe(sorted(matched_negative)),
                "unobserved_hard_negative_features": pipe(sorted(feature for feature in negative if states[feature] == "UNOBSERVED")),
                "candidate_gate_matches": len(matched_gate), "candidate_gate_total": len(gate),
                "candidate_gate_complete": int(matched_gate == gate),
                "candidate_gate_state": "UNOBSERVED" if any(states[feature] == "UNOBSERVED" for feature in gate) else "OBSERVED",
                "candidate_gate_reachable_from_current_inputs": int(all(feature in FEATURE_PRODUCERS and feature not in PRIOR_FEATURES for feature in gate)),
                "missing_candidate_gate": pipe(sorted(gate - observed)),
                "feature_measurement_states": pipe(f"{feature}:{states[feature]}" for feature in sorted(states)),
                "evidence_channels": feature_channels(observed), "source_provenance": feature_sources(observed),
                "inherited_prior_source_provenance": feature_sources(matched_prior),
                "external_folios": external_folios[head], "formal_ed1_relation_present": int("REL_ED1_SAFE" in features),
                "original_18_candidate": int(profile["candidate_id"] in {f"S{number:02d}" for number in range(1, 19)}),
                "candidate_scope": "OPAQUE_NULL" if profile["historical_lemma"] == "OPAQUE_BOTANICAL_HEAD" else "EXPLORATORY_HISTORICAL_RIVAL",
                "minimum_behavior": profile["minimum_behavior"], "literal_identity_promotion_authorized": 0,
                "literal_credit": 0, "component_export_credit": 0})
    grouped: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in raw:
        grouped[row["head"], row["family"]].append(row)
    for values in grouped.values():
        values.sort(key=lambda row: (-int(row["score"]), row["candidate_id"]))
        top_score = int(values[0]["score"])
        for row in values:
            rank = 1 + sum(int(other["score"]) > int(row["score"]) for other in values)
            rivals = [int(other["score"]) for other in values if other is not row]
            row["family_rank"] = rank
            row["family_size"] = len(values)
            row["family_top_tie_count"] = sum(int(other["score"]) == top_score for other in values)
            row["family_margin"] = int(row["score"]) - max(rivals) if rivals else "NA"
            row["family_margin_status"] = "SINGLETON_NOT_APPLICABLE" if not rivals else "MEASURED_CONTEXT_SCORE_MARGIN"
            margin_spec = next(spec for spec in decision_specs if spec["metric"] == "semantic_family_margin")
            row["family_margin_gate_pass"] = int(rank == 1 and (not rivals or int(row["family_margin"]) >= float(margin_spec["threshold"])))
            row["exploratory_candidate_readiness"] = int(rank == 1 and decision_gate(
                decision_specs, "EXPLORATORY_CANDIDATE_READINESS", {
                    "semantic_observed_required_features_complete": row["required_complete"],
                    "semantic_candidate_gate_complete": row["candidate_gate_complete"],
                    "semantic_observed_hard_negative_count": row["hard_negative_matches"],
                    "semantic_external_folios": row["external_folios"],
                    "semantic_family_margin": float("inf") if not rivals else row["family_margin"]}))
            row["decision"] = ("EXPLORATORY_RIVAL__IDENTITY_GATE_UNOBSERVED" if row["candidate_gate_state"] == "UNOBSERVED"
                               else "EXPLORATORY_RIVAL__NO_LITERAL_PROMOTION_AUTHORITY")
    raw.sort(key=lambda row: (row["head"], row["family"], int(row["family_rank"]), row["candidate_id"]))
    role_defaults = {row["head"]: (row["role_default_de"], row["registered_prior_role"], row["relation_summary"])
                     for row in feature_rows}
    dictionary: list[dict[str, Any]] = []
    for head in sorted(feature_map):
        values = sorted((row for row in raw if row["head"] == head), key=lambda row: (-int(row["score"]), row["candidate_id"]))
        best = values[0]
        tied = [row for row in values if row["score"] == best["score"]]
        tied_observed = {feature for row in tied for column in (
            "matched_required_features", "matched_positive_features", "matched_hard_negative_features")
            for feature in split_pipe(row[column])}
        confidence = "C0_EXPLORATORY_CONTEXT_TIE" if len(tied) > 1 else "C0_EXPLORATORY_CONTEXT_RANK"
        dictionary.append({
            "head": head, "structural_role_default_de": role_defaults[head][0],
            "structural_role_evidence_channel": "INHERITED_SEMANTIC_PRIOR",
            "registered_prior_role": role_defaults[head][1], "best_concrete_candidate_de": pipe(row["candidate_de"] for row in tied),
            "best_historical_lemma": pipe(row["historical_lemma"] for row in tied), "best_candidate_score": best["score"],
            "best_candidate_decision": best["decision"], "confidence": confidence,
            "top_tied_candidate_ids": pipe(row["candidate_id"] for row in tied), "top_tie_count": len(tied),
            "second_candidate_de": values[1]["candidate_de"], "third_candidate_de": values[2]["candidate_de"],
            "relation_summary": role_defaults[head][2],
            "observed_context_compatibility": pipe(sorted({feature for row in tied for column in (
                "matched_required_features", "matched_positive_features") for feature in split_pipe(row[column])})),
            "inherited_prior_support": pipe(sorted({feature for row in tied for feature in split_pipe(row["matched_inherited_prior_features"])})),
            "unobserved_identity_gates": pipe(sorted({feature for row in tied for feature in split_pipe(row["missing_candidate_gate"])})),
            "observed_profile_counterevidence": pipe(sorted({feature for row in tied for feature in split_pipe(row["matched_hard_negative_features"])})),
            "unobserved_evidence_is_not_falsehood": 1, "literal_identity_selected": 0,
            "evidence_channels": feature_channels(tied_observed), "source_provenance": feature_sources(tied_observed),
            "hypothesis_not_plaintext": 1, "confirmed_lexeme": 0, "component_export_credit": 0})
    return raw, dictionary, coverage


def relation_packet(score_rows: Sequence[dict[str, Any]], unique_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in unique_rows:
        lookup[row["head"], row["axis"]].append(row)
    packet = []
    for score in score_rows:
        if not int(score["relation_conditioned_record_head"]):
            continue
        head, axis, direction = score["head"], score["axis"], score["direction"]
        example = sorted(lookup[head, axis], key=lambda row: (selector_sort_key(row["page"]),
                         int(row["pivot_token_index"]), row["event_id"]))[0]
        head_index = int(example["pivot_token_index"]) + int(split_pipe(example["signed_offsets"])[0])
        packet.append({
            "edge_id": f"G809E{len(packet) + 1:04d}", "batch_id": "GDT809_FORMAL_HEAD_RECORD_RELATION",
            "page": example["page"], "physical_folio": leaf_folio(example["page"]),
            "diagram_unit_id": f"FORMAL_HEAD_{head}_{axis}", "pivot_visual_id": f"EXACT_HEAD_{head}",
            "pivot_locus": f"{example['locus']}@{head_index}",
            "target_visual_id": f"EXACT_{axis}_{direction}_{example['pivot_surface']}",
            "target_locus": f"{example['locus']}@{example['pivot_token_index']}",
            "relation_type": f"FORMAL_HEAD_TO_{axis}_{direction}",
            "direction_basis": "REGISTERED_SIGNED_EXACT_HEAD_PIVOT_ASSOCIATION",
            "ownership_basis": "ANALYST_TEXT_WINDOW_NOT_IMAGE_OWNERSHIP", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT809", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT809_GUARDED_TRANSCRIPTION_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "FORMAL_RECORD_RELATION_ZERO_VISUAL_EDGE_CREDIT",
            "ambiguity_state": "FORMAL_TEXT_RELATION_NOT_AUTHORIAL_VISUAL_EDGE",
            "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "HEAD_AND_PHYSICAL_FOLIO_AUDITED",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION"})
    return packet


def run_edge_intake(packet: Path, output: Path, expected_rows: int) -> dict[str, Any]:
    completed = subprocess.run([str(VMANUS_EXP), "check-edge-packet", str(packet)], cwd=ROOT,
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    expected_returncode = 1 if expected_rows else 0
    if completed.returncode != expected_returncode or completed.stderr:
        raise RuntimeError(f"GDT388 intake drift rc={completed.returncode}: {completed.stderr}")
    result = json.loads(completed.stdout)
    expected_errors = [f"edge row {number}: formal access is not sealed" for number in range(2, expected_rows + 2)]
    expected_status = "INVALID_PACKET" if expected_rows else "VALID_ACQUISITION_NOT_SCORE_READY"
    if (result.get("status") != expected_status or result.get("packet_rows") != expected_rows
            or result.get("eligible_edges") != 0 or result.get("score_ready") is not False
            or result.get("errors") != expected_errors):
        raise RuntimeError("GDT388 packet did not fail closed for the intended reason")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def source_lock() -> list[dict[str, Any]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["experiment_id"] != "GDT809" or manifest["sealed_data"] != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise RuntimeError("manifest identity or seal drift")
    guarded = {rel(LINES_RAW), rel(TOKENS_RAW), rel(CROSS_RAW)}
    rows = []
    for item in manifest["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise RuntimeError(f"manifest input hash drift: {item['path']}")
        rows.append({"path": item["path"], "sha256": item["sha256"], "purpose": item["role"],
                     "access_mode": "MANIFEST_HASH__GUARDED_QUERY_ONLY" if item["path"] in guarded else "DIRECT_SAFE_INPUT",
                     "manifest_hash_match": 1})
    outputs = {item["path"]: item for item in manifest["outputs"]}
    for path, purpose in ((RUN, "official GDT809 builder"), (VALIDATOR, "independent GDT809 validator")):
        item = outputs.get(rel(path))
        if item is None or item["sha256"] != sha256(path):
            raise RuntimeError(f"manifest implementation hash drift: {rel(path)}")
        rows.append({"path": rel(path), "sha256": item["sha256"], "purpose": purpose,
                     "access_mode": "MANIFEST_BOUND_IMPLEMENTATION", "manifest_hash_match": 1})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    if not output_dir.is_relative_to(ROOT):
        raise RuntimeError("output directory must remain inside repository")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    lock_rows = source_lock()
    lines, line_map, paragraph_info, query_stats = load_corpus()
    pool_rows, active, ed1_safe, q152 = build_head_pool()
    events = read_tsv(G808_EVENTS)
    assert_no_sealed(events)
    if len(events) != EXPECTED["core_events"] or len({row["event_id"] for row in events}) != len(events):
        raise RuntimeError("GDT808 CORE event atlas drift")
    occurrence_edges, links, unique_rows, unique_map = contact_atlases(events, line_map, active, "G809")
    if (len(occurrence_edges), len(links), len({row["event_id"] for row in links}),
            len({row["physical_folio"] for row in links}), len(unique_rows)) != (
        EXPECTED["occurrence_edges"], EXPECTED["distinct_links"], EXPECTED["contacted_pivots"],
        EXPECTED["contacted_folios"], EXPECTED["unique_windows"]):
        raise RuntimeError("exact head/pivot capacity drift")
    ed1_edges, ed1_links, ed1_unique, ed1_map = contact_atlases(events, line_map, ed1_safe, "G809-ED1")
    if (len(ed1_edges), len(ed1_links), len({row["event_id"] for row in ed1_links}), len(ed1_unique)) != (
        EXPECTED["ed1_occurrence_edges"], EXPECTED["ed1_distinct_links"], EXPECTED["ed1_contacted_pivots"],
        EXPECTED["ed1_unique_windows"]):
        raise RuntimeError("ED1 head/pivot capacity drift")
    occurrence_rows, external_rows = build_occurrences(lines, paragraph_info, active, q152, events)
    relation_rows, null_rows, profile_rows = relation_tables(events, unique_map, links, active, external_rows,
                                                              paragraph_info, "EXACT35")
    ed1_relation_rows, ed1_null_rows, ed1_profile_rows = relation_tables(events, ed1_map, ed1_links, ed1_safe,
                                                                         external_rows, paragraph_info, "ED1_SAFE18")
    null_rows.extend(ed1_null_rows)
    profile_rows.extend(ed1_profile_rows)
    ed1_lookup = {(row["head"], row["axis"]): row for row in ed1_relation_rows}
    ed1_output = []
    for head in sorted(active):
        for axis in ("L", "DY"):
            if (head, axis) in ed1_lookup:
                ed1_output.append({"head_ed1_safe": 1, **ed1_lookup[head, axis]})
            else:
                ed1_output.append({"head_ed1_safe": 0, "population": "ED1_SAFE18", "head": head, "axis": axis,
                    "primary_unique_events": 0, "primary_contact_folios": 0, "base_contacts": 0,
                    "expanded_contacts": 0, "haldane_log_or": "NA", "absolute_haldane_log_or": "NA",
                    "direction": "REMOVED_ED1", "target_rotation_absolute_rank": "NA",
                    "target_rotation_denominator": ROTATIONS + 1, "leave_one_contact_folio_sign_agreement": "NA",
                    "weighted_base_contacts": "NA", "weighted_expanded_contacts": "NA",
                    "weighted_haldane_log_or": "NA", "weighted_direction_agrees": 0,
                    "folio_disjoint_external_occurrences": 0, "folio_disjoint_external_folios": 0,
                    "external_record_compatibility_mean_score": "NA", "external_record_compatibility_direction": "NA",
                    "external_record_compatibility_direction_agrees": 0,
                    "record_training_external_overlap_folios": 0, "record_training_external_overlap_occurrences": 0,
                    "record_compatibility_not_independent_semantics": 1, "local_association_pass": 0,
                    "relation_conditioned_record_head": 0, "literal_credit": 0, "component_export_credit": 0})
    active_pool_map = {row["surface"]: row for row in pool_rows if row["active_after_q152"] == "1"}
    features, feature_map = feature_profiles(external_rows, active_pool_map, relation_rows, ed1_output)
    semantic_rows, dictionary, gate_coverage = semantic_tournament(features, feature_map)
    packet_rows = relation_packet(relation_rows, unique_rows)
    write_tsv(output_dir / "SOURCE_LOCK.tsv", lock_rows)
    write_tsv(output_dir / "GDT809_GUARDED_QUERY_STATS.tsv", query_stats)
    write_tsv(output_dir / "GDT809_HEAD_POOL_CENSUS.tsv", pool_rows)
    write_tsv(output_dir / "GDT809_1032_HEAD_OCCURRENCE_ATLAS.tsv", occurrence_rows)
    write_tsv(output_dir / "GDT809_211_HEAD_PIVOT_OCCURRENCE_EDGES.tsv", occurrence_edges)
    write_tsv(output_dir / "GDT809_209_HEAD_PIVOT_LINKS.tsv", links)
    write_tsv(output_dir / "GDT809_189_UNIQUE_HEAD_WINDOWS.tsv", unique_rows)
    write_tsv(output_dir / "GDT809_RELATION_NULL_SCORES.tsv", null_rows)
    write_tsv(output_dir / "GDT809_HEAD_AXIS_RELATION_SCORECARD.tsv", relation_rows)
    write_tsv(output_dir / "GDT809_ED1_HEAD_AXIS_SENSITIVITY.tsv", ed1_output)
    write_tsv(output_dir / "GDT809_EXTERNAL_HEAD_OCCURRENCES.tsv", external_rows)
    write_tsv(output_dir / "GDT809_EXTERNAL_RECORD_PROFILES.tsv", profile_rows)
    write_tsv(output_dir / "GDT809_HEAD_FEATURE_PROFILES.tsv", features)
    write_tsv(output_dir / "GDT809_SEMANTIC_CANDIDATE_SCOREBOARD.tsv", semantic_rows)
    write_tsv(output_dir / "GDT809_CANDIDATE_GATE_COVERAGE.tsv", gate_coverage)
    write_tsv(output_dir / "GDT809_35_WORKING_DICTIONARY.tsv", dictionary)
    write_tsv(output_dir / "GDT809_GDT388_RELATION_PACKET.tsv", packet_rows, EDGE_FIELDS)
    intake = run_edge_intake(output_dir / "GDT809_GDT388_RELATION_PACKET.tsv",
                             output_dir / "GDT809_GDT388_EDGE_INTAKE.json", len(packet_rows))
    relations = [f"{row['head']}:{row['axis']}:{row['direction']}" for row in relation_rows
                 if int(row["relation_conditioned_record_head"])]
    if any(row["literal_credit"] or row["literal_identity_promotion_authorized"] for row in semantic_rows):
        raise RuntimeError("context compatibility cannot authorize a literal identity")
    identities: list[str] = []
    artifact_hashes = {name: sha256(output_dir / name) for name in OUTPUT_NAMES
                       if name != "RESULT.json" and (output_dir / name).is_file()}
    status = ("PARTIAL__RELATION_CONDITIONED_HEADS__" +
              ("_".join(item.replace(":", "_") for item in relations) if relations else "NONE") +
              "__IDENTITY_GATES_UNOBSERVED__ZERO_LITERAL_IDENTITIES" +
              "__ZERO_CONFIRMED_LEXEMES")
    result = {
        "experiment_id": "GDT809", "status": status, "runtime_seconds": round(time.time() - started, 6),
        "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "source_census": {"selectors": EXPECTED["selectors"], "lines": EXPECTED["lines"],
                          "tokens": EXPECTED["tokens"], "strict_paragraphs": EXPECTED["strict_paragraphs"]},
        "head_census": {"source_union": len(pool_rows), "active_exact_heads": len(active),
                        "ed1_safe_heads": len(ed1_safe), "rank_stable_occurrences": len(occurrence_rows),
                        "strict_external_occurrences": len(external_rows)},
        "relation_census": {"occurrence_edges": len(occurrence_edges), "distinct_links": len(links),
                            "contacted_pivots": len({row["event_id"] for row in links}),
                            "contacted_folios": len({row["physical_folio"] for row in links}),
                            "unique_head_windows": len(unique_rows), "target_rotations": ROTATIONS,
                            "selected_relation_heads": relations},
        "ed1_census": {"occurrence_edges": len(ed1_edges), "distinct_links": len(ed1_links),
                       "contacted_pivots": len({row["event_id"] for row in ed1_links}),
                       "unique_head_windows": len(ed1_unique)},
        "semantic_census": {"historical_candidates": len(read_tsv(SEMANTIC_SPECS)),
                            "candidate_rows": len(semantic_rows), "working_dictionary_rows": len(dictionary),
                            "original_exploratory_candidates": 18,
                            "candidate_gate_coverage_rows": len(gate_coverage),
                            "candidate_gate_unobserved_rows": sum(row["gate_state"] == "UNOBSERVED" for row in gate_coverage),
                            "identity_promotion_authorized": False,
                            "provisional_identities": identities, "confirmed_lexemes": 0, "component_exports": 0},
        "edge_intake": {"packet_rows": len(packet_rows), "eligible_edges": intake["eligible_edges"],
                        "score_ready": intake["score_ready"], "status": intake["status"]},
        "artifact_sha256": artifact_hashes,
        "claim_ceiling": "Formal exact-head relations and exploratory context compatibility only; unobserved identity gates are not negative findings. No literal identity promotion, confirmed lexeme, plaintext, character, substring, sound, cipher, language or renderer export."}
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "active_heads": len(active), "unique_windows": len(unique_rows),
                      "external_occurrences": len(external_rows), "relation_heads": relations,
                      "provisional_identities": identities, "runtime_seconds": result["runtime_seconds"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
