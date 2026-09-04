#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt801_terminal_lm_boundary_hierarchy_discriminator"
SRC = EXP / "src"
ART = EXP / "artifacts"
G800_OCC = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G800_STEMS = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv"
G800_CARD = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_STRUCTURAL_CARD.tsv"
G791_SPINE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
G791_LINES = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
MODEL_SPECS = SRC / "CANDIDATE_MODEL_SPECS.tsv"

JOIN = ART / "GDT801_542_SOURCE_SELECTOR_BOUNDARY_JOIN.tsv"
INTERIOR = ART / "GDT801_411_STRICT_INTERIOR_EVENTS.tsv"
PROJECTION = ART / "GDT801_743_FROZEN_STEM_SPINE.tsv"
ENDPOINTS = ART / "GDT801_23_RECORD_PANEL_ENDPOINT_CAPACITY.tsv"
DEEP = ART / "GDT801_24_DEEP_LINEFINAL_PROGRESS.tsv"
LOCAL = ART / "GDT801_80_LOCAL_LABEL_PROJECTION.tsv"
HIERARCHY = ART / "GDT801_4_GLOBAL_HIERARCHY_CENSUS.tsv"
TESTS = ART / "GDT801_BOUNDARY_TESTS.tsv"
CAPACITY = ART / "GDT801_8_TARGET_BOUNDARY_CAPACITY.tsv"
PROGRESS = ART / "GDT801_DEEP_PROGRESS_TESTS.tsv"
CANDIDATES = ART / "GDT801_CANDIDATE_ADJUDICATION.tsv"
CARD = ART / "GDT801_STRUCTURAL_CARD.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def truth(value: str | bool | int) -> bool:
    if value in (True, 1, "1", "True"):
        return True
    if value in (False, 0, "0", "False"):
        return False
    raise ValueError(f"not boolean: {value!r}")


def f12(value: float | None) -> str:
    if value is None:
        return "NA"
    if math.isinf(value):
        return "INF"
    return f"{value:.12g}"


def build_tables(
    rows: Iterable[dict[str, Any]],
    strata: Sequence[str],
    positive: Callable[[dict[str, Any]], bool],
) -> list[tuple[int, int, int, int]]:
    cells: dict[tuple[Any, ...], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        cell = cells[tuple(row[field] for field in strata)]
        if row["terminal"] == "m":
            cell[0 if positive(row) else 1] += 1
        else:
            cell[2 if positive(row) else 3] += 1
    return [tuple(cells[key]) for key in sorted(cells, key=lambda key: tuple(map(str, key)))]


def conditional_distribution(
    cells: Iterable[tuple[int, int, int, int]],
) -> tuple[dict[int, float], int, float, int]:
    distribution: dict[int, float] = {0: 1.0}
    observed = 0
    expected = 0.0
    informative = 0
    for a, b, c, d in cells:
        n = a + b + c + d
        m_total = a + b
        l_total = c + d
        positive_total = a + c
        negative_total = b + d
        if not (m_total and l_total and positive_total and negative_total):
            continue
        informative += 1
        observed += a
        expected += positive_total * m_total / n
        low = max(0, positive_total - l_total)
        high = min(m_total, positive_total)
        denominator = math.comb(n, positive_total)
        local = {
            k: math.comb(m_total, k) * math.comb(l_total, positive_total - k) / denominator
            for k in range(low, high + 1)
        }
        next_distribution: dict[int, float] = defaultdict(float)
        for old_k, old_p in distribution.items():
            for new_k, new_p in local.items():
                next_distribution[old_k + new_k] += old_p * new_p
        distribution = dict(next_distribution)
    return distribution, observed, expected, informative


def analyse(
    rows: Sequence[dict[str, Any]],
    strata: Sequence[str],
    positive: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    cells = build_tables(rows, strata, positive)
    numerator = 0.0
    denominator = 0.0
    for a, b, c, d in cells:
        n = a + b + c + d
        if n and (a + b) and (c + d) and (a + c) and (b + d):
            numerator += a * d / n
            denominator += b * c / n
    distribution, observed, expected, informative = conditional_distribution(cells)
    odds_ratio: float | None
    if not informative:
        odds_ratio = None
    elif denominator:
        odds_ratio = numerator / denominator
    elif numerator:
        odds_ratio = math.inf
    else:
        odds_ratio = None
    upper = min(1.0, sum(probability for value, probability in distribution.items() if value >= observed)) if informative else 1.0
    lower = min(1.0, sum(probability for value, probability in distribution.items() if value <= observed)) if informative else 1.0
    counts = Counter(row["terminal"] for row in rows)
    positives = Counter(row["terminal"] for row in rows if positive(row))
    return {
        "n_rows": len(rows), "m_n": counts["m"], "m_positive": positives["m"],
        "l_n": counts["l"], "l_positive": positives["l"],
        "strata": len(cells), "informative_strata": informative,
        "observed_m_positive": observed, "expected_m_positive": expected,
        "odds_ratio": odds_ratio, "exact_upper_p": upper, "exact_lower_p": lower,
    }


def last_events(rows: Sequence[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        identifier = row[field]
        if identifier == "NONE":
            continue
        if identifier not in result or int(row["occurrence_ordinal"]) > int(result[identifier]["occurrence_ordinal"]):
            result[identifier] = row
    return result


def paragraph_role(line: dict[str, str]) -> str:
    start = line["paragraph_start"] == "1"
    end = line["paragraph_end"] == "1"
    return "SINGLE_LINE" if start and end else "START" if start else "END" if end else "MIDDLE"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    for lock in read_tsv(SOURCE_LOCK):
        path = ROOT / lock["path"]
        if sha(path) != lock["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {lock['path']}")

    g800 = read_tsv(G800_OCC)
    stem_summary = read_tsv(G800_STEMS)
    inherited_card = read_tsv(G800_CARD)
    spine = read_tsv(G791_SPINE)
    lines = read_tsv(G791_LINES)
    if len(g800) != 4137 or len(stem_summary) != 155 or len(spine) != 5866 or len(lines) != 1007:
        raise RuntimeError("predecessor cardinality changed")
    if any(not row["stem"] for row in g800 + stem_summary):
        raise RuntimeError("empty predecessor stem")
    if inherited_card[0]["structural_tag"] != "BOUNDARY_FAVOURED_TERMINAL_SURFACE":
        raise RuntimeError("GDT800 structural card changed")
    material = g800 + spine + lines
    if any(any(value.startswith("f84") for value in row.values()) for row in material):
        raise RuntimeError("sealed f84/f84r selector reached materialization")

    spine_by_key: dict[tuple[str, str, int], dict[str, str]] = {}
    spine_by_id: dict[str, dict[str, str]] = {}
    for row in spine:
        key = (row["source_selector"], row["locus"], int(row["token_ordinal_in_line"]))
        if key in spine_by_key or row["occurrence_id"] in spine_by_id:
            raise RuntimeError(f"duplicate GDT791 occurrence key: {key}")
        spine_by_key[key] = row
        spine_by_id[row["occurrence_id"]] = row
    line_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in lines:
        key = (row["source_selector"], row["locus"])
        if key in line_by_key:
            raise RuntimeError(f"duplicate GDT791 line key: {key}")
        line_by_key[key] = row

    running_spine = [row for row in spine if row["occurrence_kind"] == "RUNNING_EVENT"]
    statement_last = last_events(running_spine, "legacy_statement_id")
    record_last = last_events(running_spine, "record_id")
    panel_last = last_events(running_spine, "panel_id")
    statement_end_ids = {row["occurrence_id"] for row in statement_last.values()}
    record_end_ids = {row["occurrence_id"] for row in record_last.values()}
    panel_end_ids = {row["occurrence_id"] for row in panel_last.values()}

    def decorate(base: dict[str, Any], occurrence: dict[str, str], line: dict[str, str]) -> dict[str, Any]:
        token_index = int(occurrence["token_ordinal_in_line"])
        token_count = int(line["token_count"])
        any_final = token_index == token_count
        singleton = token_count == 1
        role = paragraph_role(line)
        paragraph_close = occurrence["occurrence_kind"] == "RUNNING_EVENT" and line["paragraph_end"] == "1" and any_final
        statement_close = occurrence["occurrence_id"] in statement_end_ids
        record_close = occurrence["occurrence_id"] in record_end_ids
        panel_close = occurrence["occurrence_id"] in panel_end_ids
        strict = (
            occurrence["occurrence_kind"] == "RUNNING_EVENT"
            and line["paragraph_start"] == "0" and line["paragraph_end"] == "0"
            and not statement_close and not record_close and not panel_close
        )
        base.update(
            {
                "gdt791_occurrence_ordinal": int(occurrence["occurrence_ordinal"]),
                "gdt791_occurrence_id": occurrence["occurrence_id"],
                "source_selector": occurrence["source_selector"],
                "physical_page": occurrence["physical_page"],
                "locus": occurrence["locus"], "token_index": token_index,
                "token_count": token_count, "surface": occurrence["surface"],
                "distance_from_end": token_count - token_index,
                "position_class": "SINGLE" if singleton else "FINAL" if any_final else "FIRST" if token_index == 1 else "INTERNAL",
                "any_line_final": int(any_final), "multi_line_final": int(any_final and not singleton),
                "single_token_line": int(singleton), "occurrence_kind": occurrence["occurrence_kind"],
                "line_kind": line["line_kind"], "paragraph_start": int(line["paragraph_start"]),
                "paragraph_end_line": int(line["paragraph_end"]), "paragraph_role": role,
                "paragraph_close": int(paragraph_close), "legacy_statement_id": occurrence["legacy_statement_id"],
                "statement_close": int(statement_close), "record_id": occurrence["record_id"],
                "record_close": int(record_close), "panel_id": occurrence["panel_id"],
                "panel_close": int(panel_close), "topology_family": occurrence["topology_family"],
                "register": occurrence["register"], "context_scope": occurrence["context_scope"],
                "structurally_internal": int(strict),
                "semantic_export_credit": "ZERO__STRUCTURAL_BOUNDARY_ONLY",
            }
        )
        return base

    join_rows: list[dict[str, Any]] = []
    for source in g800:
        key = (source["page"], source["locus"], int(source["token_index"]))
        occurrence = spine_by_key.get(key)
        if occurrence is None:
            continue
        if source["surface"] != occurrence["surface"]:
            raise RuntimeError(f"surface mismatch at {key}")
        line = line_by_key[(occurrence["source_selector"], occurrence["locus"])]
        if int(source["token_count"]) != int(line["token_count"]):
            raise RuntimeError(f"line-token mismatch at {key}")
        base = {
            "join_ordinal": 0, "gdt800_occurrence_id": source["occurrence_id"],
            "stem": source["stem"], "terminal": source["terminal"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
        }
        decorated = decorate(base, occurrence, line)
        if decorated["any_line_final"] != int(truth(source["any_line_final"])):
            raise RuntimeError(f"line-final mismatch at {key}")
        join_rows.append(decorated)
    join_rows.sort(key=lambda row: int(row["gdt800_occurrence_id"].split("O")[-1]))
    for index, row in enumerate(join_rows, 1):
        row["join_ordinal"] = index
    join_fields = [
        "join_ordinal", "gdt800_occurrence_id", "gdt791_occurrence_ordinal", "gdt791_occurrence_id",
        "source_selector", "physical_page", "locus", "token_index", "token_count", "surface", "stem", "terminal",
        "section", "language", "hand", "distance_from_end", "position_class", "any_line_final",
        "multi_line_final", "single_token_line", "occurrence_kind", "line_kind", "paragraph_start",
        "paragraph_end_line", "paragraph_role", "paragraph_close", "legacy_statement_id", "statement_close",
        "record_id", "record_close", "panel_id", "panel_close", "topology_family", "register", "context_scope",
        "structurally_internal", "semantic_export_credit",
    ]
    if len(join_rows) != 542 or Counter(row["occurrence_kind"] for row in join_rows) != Counter({"RUNNING_EVENT": 530, "LOCAL_ADDRESS_OR_LABEL": 12}):
        raise RuntimeError("exact source-selector join changed")
    write_tsv(JOIN, join_rows, join_fields)

    direct_running = [row for row in join_rows if row["occurrence_kind"] == "RUNNING_EVENT"]
    interior_rows = [row for row in direct_running if row["structurally_internal"]]
    if len(interior_rows) != 411:
        raise RuntimeError(f"strict interior changed: {len(interior_rows)}")
    write_tsv(INTERIOR, interior_rows, join_fields)

    frozen_stems = {row["stem"] for row in stem_summary}
    joined_by_g791 = {row["gdt791_occurrence_id"]: row for row in join_rows}
    projection_rows: list[dict[str, Any]] = []
    for occurrence in spine:
        surface = occurrence["surface"]
        if len(surface) <= 1 or surface[-1] not in {"l", "m"} or surface[:-1] not in frozen_stems:
            continue
        line = line_by_key[(occurrence["source_selector"], occurrence["locus"])]
        direct = joined_by_g791.get(occurrence["occurrence_id"])
        base = {
            "projection_ordinal": 0, "in_exact_542_join": int(direct is not None),
            "gdt800_occurrence_id": direct["gdt800_occurrence_id"] if direct else "NONE",
            "stem": surface[:-1], "terminal": surface[-1],
        }
        projection_rows.append(decorate(base, occurrence, line))
    projection_rows.sort(key=lambda row: row["gdt791_occurrence_ordinal"])
    for index, row in enumerate(projection_rows, 1):
        row["projection_ordinal"] = index
    projection_fields = [
        "projection_ordinal", "in_exact_542_join", "gdt800_occurrence_id", "gdt791_occurrence_ordinal",
        "gdt791_occurrence_id", "source_selector", "physical_page", "locus", "token_index", "token_count",
        "surface", "stem", "terminal", "distance_from_end", "position_class", "any_line_final",
        "multi_line_final", "single_token_line", "occurrence_kind", "line_kind", "paragraph_start",
        "paragraph_end_line", "paragraph_role", "paragraph_close", "legacy_statement_id", "statement_close",
        "record_id", "record_close", "panel_id", "panel_close", "topology_family", "register", "context_scope",
        "structurally_internal", "semantic_export_credit",
    ]
    if len(projection_rows) != 743 or Counter(row["occurrence_kind"] for row in projection_rows) != Counter({"RUNNING_EVENT": 663, "LOCAL_ADDRESS_OR_LABEL": 80}):
        raise RuntimeError("frozen-stem projection changed")
    write_tsv(PROJECTION, projection_rows, projection_fields)
    local_rows = [row for row in projection_rows if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"]
    write_tsv(LOCAL, local_rows, projection_fields)

    endpoint_rows: list[dict[str, Any]] = []
    for boundary_type, mapping in (("RECORD", record_last), ("PANEL", panel_last)):
        for structure_id, occurrence in sorted(mapping.items()):
            line = line_by_key[(occurrence["source_selector"], occurrence["locus"])]
            direct = joined_by_g791.get(occurrence["occurrence_id"])
            endpoint_rows.append(
                {
                    "boundary_ordinal": 0, "boundary_type": boundary_type, "structure_id": structure_id,
                    "physical_page": occurrence["physical_page"], "source_selector": occurrence["source_selector"],
                    "endpoint_occurrence_id": occurrence["occurrence_id"], "locus": occurrence["locus"],
                    "line_number": occurrence["line_number"], "token_index": occurrence["token_ordinal_in_line"],
                    "token_count": line["token_count"], "surface": occurrence["surface"],
                    "physical_line_final": int(occurrence["token_ordinal_in_line"] == line["token_count"]),
                    "paired_target": int(direct is not None), "paired_stem": direct["stem"] if direct else "NA",
                    "terminal": direct["terminal"] if direct else "NA",
                    "coincident_record_panel_endpoint": int(occurrence["occurrence_id"] in record_end_ids and occurrence["occurrence_id"] in panel_end_ids),
                    "capacity_class": "PAIRED_TARGET" if direct else "NO_PAIRED_TARGET",
                    "semantic_export_credit": "ZERO__CAPACITY_ONLY",
                }
            )
    endpoint_rows.sort(key=lambda row: (row["physical_page"], row["boundary_type"], row["structure_id"]))
    for index, row in enumerate(endpoint_rows, 1):
        row["boundary_ordinal"] = index
    endpoint_fields = list(endpoint_rows[0])
    if len(endpoint_rows) != 23 or sum(row["paired_target"] for row in endpoint_rows) != 2:
        raise RuntimeError("record/panel endpoint capacity changed")
    write_tsv(ENDPOINTS, endpoint_rows, endpoint_fields)

    paragraph_end_events: list[dict[str, str]] = []
    for line in lines:
        if line["line_kind"] != "RUNNING_PROSE" or line["paragraph_end"] != "1":
            continue
        paragraph_end_events.append(spine_by_key[(line["source_selector"], line["locus"], int(line["token_count"]))])
    hierarchy_rows: list[dict[str, Any]] = []
    for boundary_type, events in (
        ("PARAGRAPH", paragraph_end_events), ("LEGACY_STATEMENT", list(statement_last.values())),
        ("RECORD", list(record_last.values())), ("PANEL", list(panel_last.values())),
    ):
        classes = Counter()
        for event in events:
            line = line_by_key[(event["source_selector"], event["locus"])]
            if int(line["token_count"]) == 1:
                classes["SINGLETON"] += 1
            elif event["token_ordinal_in_line"] == line["token_count"]:
                classes["MULTI_FINAL"] += 1
            else:
                classes["INTERNAL"] += 1
        hierarchy_rows.append(
            {
                "boundary_type": boundary_type, "group_count": len(events),
                "internal_end_count": classes["INTERNAL"], "multi_line_final_end_count": classes["MULTI_FINAL"],
                "singleton_end_count": classes["SINGLETON"],
                "identifiability_note": "GLOBAL_GDT791_CAPACITY__NOT_TERMINAL_MEANING",
            }
        )
    write_tsv(HIERARCHY, hierarchy_rows, list(hierarchy_rows[0]))

    projected_running = [row for row in projection_rows if row["occurrence_kind"] == "RUNNING_EVENT"]
    boundary_specs = [
        ("PARAGRAPH", "paragraph_close", len(paragraph_end_events)),
        ("LEGACY_STATEMENT", "statement_close", len(statement_last)),
        ("RECORD", "record_close", len(record_last)),
        ("PANEL", "panel_close", len(panel_last)),
    ]
    capacity_rows: list[dict[str, Any]] = []
    gate_map: dict[tuple[str, str], bool] = {}
    for population_name, population in (("DIRECT_RUNNING", direct_running), ("FROZEN_STEM_RUNNING", projected_running)):
        for boundary_type, field, group_count in boundary_specs:
            targets = [row for row in population if row[field]]
            counts = Counter(row["terminal"] for row in targets)
            internal = [row for row in targets if not row["any_line_final"]]
            informative = analyse(population, ["stem", "multi_line_final"], lambda row, field=field: bool(row[field]))["informative_strata"]
            internal_counts = Counter(row["terminal"] for row in internal)
            target_pages = {row["physical_page"] for row in targets}
            margin_pass = counts["m"] > 0 and counts["l"] > 0 and len(target_pages) >= 2 and informative > 0
            internal_pass = bool(internal)
            capacity_pass = margin_pass and internal_pass
            failures = []
            if not counts["m"]: failures.append("NO_M_TARGET")
            if not counts["l"]: failures.append("NO_L_TARGET")
            if informative == 0: failures.append("NO_INFORMATIVE_STEM_X_LINE_FINAL_STRATUM")
            if len(target_pages) < 2: failures.append("PHYSICAL_PAGES_LT2")
            if not internal_pass: failures.append("NO_PHYSICAL_LINE_INTERNAL_TARGET")
            gate_map[(population_name, boundary_type)] = capacity_pass
            capacity_rows.append(
                {
                    "population": population_name, "boundary_type": boundary_type,
                    "group_count": group_count, "target_rows": len(targets), "m_rows": counts["m"],
                    "l_rows": counts["l"], "multi_line_final_rows": sum(row["multi_line_final"] for row in targets),
                    "physical_line_internal_rows": len(internal),
                    "physical_line_internal_m": internal_counts["m"],
                    "physical_line_internal_l": internal_counts["l"],
                    "distinct_stems": len({row["stem"] for row in targets}),
                    "distinct_source_selectors": len({row["source_selector"] for row in targets}),
                    "distinct_physical_pages": len(target_pages),
                    "informative_stem_x_line_final_strata": informative,
                    "terminal_margin_page_gate": int(margin_pass),
                    "increment_capacity_pass": int(capacity_pass), "internal_discriminator_pass": int(internal_pass),
                    "failure_reason": "NONE" if not failures else "|".join(failures),
                }
            )
    passed_capacity = {(row["population"], row["boundary_type"]) for row in capacity_rows if row["increment_capacity_pass"]}
    if passed_capacity != {("FROZEN_STEM_RUNNING", "LEGACY_STATEMENT")}:
        raise RuntimeError(f"unexpected higher-boundary capacity map: {passed_capacity}")
    write_tsv(CAPACITY, capacity_rows, list(capacity_rows[0]))

    test_rows: list[dict[str, Any]] = []
    test_stats: dict[str, dict[str, Any]] = {}

    def add_test(
        test_id: str, population_name: str, row_filter: str, outcome: str,
        strata: Sequence[str], rows: Sequence[dict[str, Any]],
        positive: Callable[[dict[str, Any]], bool], decision: str,
    ) -> None:
        stats = analyse(rows, strata, positive)
        test_stats[test_id] = stats
        test_rows.append(
            {
                "test_id": test_id, "population": population_name, "row_filter": row_filter,
                "outcome": outcome, "strata_fields": "|".join(strata),
                "n_rows": stats["n_rows"], "m_n": stats["m_n"], "m_positive": stats["m_positive"],
                "l_n": stats["l_n"], "l_positive": stats["l_positive"],
                "strata": stats["strata"], "informative_strata": stats["informative_strata"],
                "observed_m_positive": stats["observed_m_positive"],
                "expected_m_positive": f12(stats["expected_m_positive"]),
                "mh_odds_ratio": f12(stats["odds_ratio"]),
                "exact_upper_p": f12(stats["exact_upper_p"]), "exact_lower_p": f12(stats["exact_lower_p"]),
                "decision": decision,
            }
        )

    line_final = lambda row: bool(row["multi_line_final"])
    for suffix, strata in (
        ("STEM", ["stem"]), ("STEM_HAND", ["stem", "hand"]),
        ("STEM_TOPOLOGY", ["stem", "topology_family"]),
        ("STEM_PHYSICAL_PAGE", ["stem", "physical_page"]),
    ):
        add_test(f"DIRECT_LINE_FINAL_{suffix}", "DIRECT_RUNNING", "ALL", "MULTI_LINE_FINAL", strata, direct_running, line_final, "LINE_EDGE_RETAINS")
    paragraph_start_rows = [row for row in direct_running if row["paragraph_start"]]
    paragraph_end_line_rows = [row for row in direct_running if row["paragraph_end_line"]]
    add_test("PARAGRAPH_START_LINE_EDGE_STEM", "DIRECT_RUNNING", "PARAGRAPH_START_LINE", "MULTI_LINE_FINAL", ["stem"], paragraph_start_rows, line_final, "DIAGNOSTIC")
    add_test("PARAGRAPH_END_LINE_EDGE_STEM", "DIRECT_RUNNING", "PARAGRAPH_END_LINE", "MULTI_LINE_FINAL", ["stem"], paragraph_end_line_rows, line_final, "DIAGNOSTIC")
    for suffix, strata in (
        ("STEM", ["stem"]), ("STEM_HAND", ["stem", "hand"]),
        ("STEM_TOPOLOGY", ["stem", "topology_family"]),
        ("STEM_PHYSICAL_PAGE", ["stem", "physical_page"]),
    ):
        add_test(f"STRUCTURAL_INTERIOR_LINE_FINAL_{suffix}", "DIRECT_RUNNING", "STRICT_STRUCTURAL_INTERIOR", "MULTI_LINE_FINAL", strata, interior_rows, line_final, "PRIMARY_RETAINS")

    removal_specs = [
        ("NO_PARAGRAPH_CLOSE_LINE_EDGE", "paragraph_close"),
        ("NO_PARAGRAPH_END_LINE_EDGE", "paragraph_end_line"),
        ("NO_STATEMENT_CLOSE_LINE_EDGE", "statement_close"),
        ("NO_RECORD_CLOSE_LINE_EDGE", "record_close"),
        ("NO_PANEL_CLOSE_LINE_EDGE", "panel_close"),
    ]
    for test_id, field in removal_specs:
        rows = [row for row in direct_running if not row[field]]
        add_test(test_id, "DIRECT_RUNNING", f"EXCLUDE_{field.upper()}", "MULTI_LINE_FINAL", ["stem"], rows, line_final, "LINE_EDGE_RETAINS")

    for boundary_type, field, _ in boundary_specs:
        add_test(
            f"DIRECT_{boundary_type}_INCREMENT", "DIRECT_RUNNING", "ALL", field.upper(),
            ["stem", "multi_line_final"], direct_running, lambda row, field=field: bool(row[field]),
            "SCORE_READY_DIAGNOSTIC" if gate_map[("DIRECT_RUNNING", boundary_type)] else "NOT_SCORE_READY_CAPACITY",
        )
    add_test("FROZEN_RUNNING_LINE_EDGE_STEM", "FROZEN_STEM_RUNNING", "ALL", "MULTI_LINE_FINAL", ["stem"], projected_running, line_final, "LINE_EDGE_RETAINS")
    add_test("FROZEN_RUNNING_LINE_EDGE_STEM_TOPOLOGY", "FROZEN_STEM_RUNNING", "ALL", "MULTI_LINE_FINAL", ["stem", "topology_family"], projected_running, line_final, "LINE_EDGE_RETAINS")
    for boundary_type, field, _ in boundary_specs:
        add_test(
            f"FROZEN_{boundary_type}_INCREMENT", "FROZEN_STEM_RUNNING", "ALL", field.upper(),
            ["stem", "multi_line_final"], projected_running, lambda row, field=field: bool(row[field]),
            "SCORE_READY_DIAGNOSTIC" if gate_map[("FROZEN_STEM_RUNNING", boundary_type)] else "NOT_SCORE_READY_CAPACITY",
        )
    add_test("LABEL_MULTI_LINE_FINAL", "FROZEN_LOCAL_LABEL", "ALL", "MULTI_LINE_FINAL", ["stem"], local_rows, line_final, "DIAGNOSTIC_NOT_TRANSFER")
    add_test("LABEL_ANY_LINE_FINAL", "FROZEN_LOCAL_LABEL", "ALL", "ANY_LINE_FINAL", ["stem"], local_rows, lambda row: bool(row["any_line_final"]), "SINGLETON_CONFOUNDED")
    add_test("LABEL_STATUS_GIVEN_ANY_FINAL", "FROZEN_STEM_ALL", "ALL", "LOCAL_LABEL_STATUS", ["stem", "any_line_final"], projection_rows, lambda row: row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL", "NO_INCREMENT")
    add_test("LABEL_STATUS_GIVEN_MULTI_FINAL", "FROZEN_STEM_ALL", "ALL", "LOCAL_LABEL_STATUS", ["stem", "multi_line_final"], projection_rows, lambda row: row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL", "NO_INCREMENT")
    add_test("LABEL_STATUS_GIVEN_ANY_FINAL_PHYSICAL_PAGE", "FROZEN_STEM_ALL", "ALL", "LOCAL_LABEL_STATUS", ["stem", "any_line_final", "physical_page"], projection_rows, lambda row: row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL", "PAGE_CAPACITY_THIN_NO_INCREMENT")
    add_test("LABEL_STATUS_GIVEN_MULTI_FINAL_PHYSICAL_PAGE", "FROZEN_STEM_ALL", "ALL", "LOCAL_LABEL_STATUS", ["stem", "multi_line_final", "physical_page"], projection_rows, lambda row: row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL", "PAGE_CAPACITY_THIN_NO_INCREMENT")

    full_rows: list[dict[str, Any]] = []
    for row in g800:
        full_rows.append({**row, "multi_line_final": int(truth(row["multi_line_final"]))})
    add_test("GDT800_LINE_LENGTH_CONTROL", "GDT800_FULL", "ALL", "MULTI_LINE_FINAL", ["stem", "token_count"], full_rows, line_final, "LINE_EDGE_RETAINS")
    add_test("GDT800_SELECTOR_LINE_LENGTH_CONTROL", "GDT800_FULL", "ALL", "MULTI_LINE_FINAL", ["stem", "page", "token_count"], full_rows, line_final, "LINE_EDGE_RETAINS")
    write_tsv(TESTS, test_rows, list(test_rows[0]))

    record_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    panel_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in running_spine:
        if event["record_id"] != "NONE": record_groups[event["record_id"]].append(event)
        if event["panel_id"] != "NONE": panel_groups[event["panel_id"]].append(event)

    def positions(groups: dict[str, list[dict[str, str]]], field: str) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for identifier, events in groups.items():
            ordered = sorted(events, key=lambda event: int(event["occurrence_ordinal"]))
            unique_lines: list[tuple[str, str]] = []
            for event in ordered:
                key = (event["source_selector"], event["locus"])
                if key not in unique_lines: unique_lines.append(key)
            line_index = {key: index for index, key in enumerate(unique_lines)}
            event_index = {event["occurrence_id"]: index for index, event in enumerate(ordered)}
            for event in ordered:
                key = (event["source_selector"], event["locus"])
                index = line_index[key]
                result[event["occurrence_id"]] = {
                    f"{field}_line_rank": index + 1,
                    f"{field}_line_count": len(unique_lines),
                    f"{field}_line_progress": index / (len(unique_lines) - 1) if len(unique_lines) > 1 else 1.0,
                    f"{field}_lines_after": len(unique_lines) - 1 - index,
                    f"{field}_events_after": len(ordered) - 1 - event_index[event["occurrence_id"]],
                }
        return result

    record_positions = positions(record_groups, "record")
    panel_positions = positions(panel_groups, "panel")
    deep_rows: list[dict[str, Any]] = []
    for row in direct_running:
        if row["physical_page"] not in {"f77r", "f82r", "f83r"} or not row["multi_line_final"]:
            continue
        event_id = row["gdt791_occurrence_id"]
        deep_rows.append(
            {
                "deep_ordinal": 0, "gdt800_occurrence_id": row["gdt800_occurrence_id"],
                "gdt791_occurrence_id": event_id, "physical_page": row["physical_page"],
                "source_selector": row["source_selector"], "locus": row["locus"], "surface": row["surface"],
                "stem": row["stem"], "terminal": row["terminal"], "record_id": row["record_id"],
                "panel_id": row["panel_id"], **record_positions[event_id], **panel_positions[event_id],
                "record_close": row["record_close"], "panel_close": row["panel_close"],
                "semantic_export_credit": "ZERO__PROGRESS_DIAGNOSTIC",
            }
        )
    deep_rows.sort(key=lambda row: (row["physical_page"], row["gdt791_occurrence_id"]))
    for index, row in enumerate(deep_rows, 1):
        row["deep_ordinal"] = index
        row["record_line_progress"] = f12(row["record_line_progress"])
        row["panel_line_progress"] = f12(row["panel_line_progress"])
    if len(deep_rows) != 24 or Counter(row["terminal"] for row in deep_rows) != Counter({"l": 19, "m": 5}):
        raise RuntimeError("deep line-final population changed")
    write_tsv(DEEP, deep_rows, list(deep_rows[0]))

    progress_rows: list[dict[str, Any]] = []
    pages = sorted({row["physical_page"] for row in deep_rows})
    choices: list[list[tuple[int, ...]]] = []
    for page in pages:
        indices = [index for index, row in enumerate(deep_rows) if row["physical_page"] == page]
        m_count = sum(deep_rows[index]["terminal"] == "m" for index in indices)
        choices.append(list(itertools.combinations(indices, m_count)))
    assignments = list(itertools.product(*choices))
    if len(assignments) != 2970:
        raise RuntimeError(f"unexpected page-blocked worlds: {len(assignments)}")
    for axis in ("record", "panel"):
        field = f"{axis}_line_progress"
        values = [float(row[field]) for row in deep_rows]
        observed_m = [values[index] for index, row in enumerate(deep_rows) if row["terminal"] == "m"]
        observed_l = [values[index] for index, row in enumerate(deep_rows) if row["terminal"] == "l"]
        observed_difference = sum(observed_m) / len(observed_m) - sum(observed_l) / len(observed_l)
        null_differences = []
        for assignment in assignments:
            m_indices = set().union(*(set(item) for item in assignment))
            m_values = [values[index] for index in m_indices]
            l_values = [values[index] for index in range(len(values)) if index not in m_indices]
            null_differences.append(sum(m_values) / len(m_values) - sum(l_values) / len(l_values))
        upper = sum(value >= observed_difference - 1e-12 for value in null_differences) / len(null_differences)
        lower = sum(value <= observed_difference + 1e-12 for value in null_differences) / len(null_differences)
        progress_rows.append(
            {
                "test_id": f"DEEP_{axis.upper()}_LINE_PROGRESS", "axis": axis.upper(),
                "n_rows": len(deep_rows), "m_n": len(observed_m), "l_n": len(observed_l),
                "observed_m_mean": f12(sum(observed_m) / len(observed_m)),
                "observed_l_mean": f12(sum(observed_l) / len(observed_l)),
                "m_minus_l": f12(observed_difference), "permutation_worlds": len(null_differences),
                "exact_upper_p": f12(upper), "exact_lower_p": f12(lower),
                "direction_gate": "M_LATER", "decision": "FAILS_M_LATER_DIRECTION",
            }
        )
    write_tsv(PROGRESS, progress_rows, list(progress_rows[0]))

    running_endings: dict[str, set[str]] = defaultdict(set)
    local_endings: dict[str, set[str]] = defaultdict(set)
    for row in projected_running: running_endings[row["stem"]].add(row["terminal"])
    for row in local_rows: local_endings[row["stem"]].add(row["terminal"])
    projected_bidirectional_stems = {
        stem for stem, endings in running_endings.items() if endings == {"l", "m"}
    }
    projected_bidirectional_events = [
        row for row in projected_running if row["stem"] in projected_bidirectional_stems
    ]
    bridge_stems = set(running_endings) & set(local_endings)
    fully_crossed = {stem for stem in bridge_stems if running_endings[stem] == local_endings[stem] == {"l", "m"}}
    local_label_gate = (
        len(local_rows) >= 40 and Counter(row["terminal"] for row in local_rows)["m"] >= 10
        and Counter(row["terminal"] for row in local_rows)["l"] >= 10
        and test_stats["LABEL_STATUS_GIVEN_ANY_FINAL"]["informative_strata"] >= 10
        and len({row["source_selector"] for row in local_rows}) >= 5
    )
    primary_ids = [
        "STRUCTURAL_INTERIOR_LINE_FINAL_STEM", "STRUCTURAL_INTERIOR_LINE_FINAL_STEM_HAND",
        "STRUCTURAL_INTERIOR_LINE_FINAL_STEM_TOPOLOGY", "STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE",
    ]
    primary_pass = all(
        test_stats[test_id]["odds_ratio"] is not None and test_stats[test_id]["odds_ratio"] > 3
        and test_stats[test_id]["exact_upper_p"] < .01 for test_id in primary_ids
    )
    candidate_rows = [
        {
            "candidate_id": "C1", "candidate": "PHYSICAL_LINE_EDGE_FAVOURED_TERMINAL_SURFACE",
            "capacity_status": "PASS_411_STRICT_INTERIOR", "statistical_status": "ALL4_OR_GT3_P_LT01" if primary_pass else "PRIMARY_FAIL",
            "decision": "SELECT_REFINED_STRUCTURAL" if primary_pass else "NOT_SELECTED",
            "positive_evidence": "line-edge enrichment survives one composite paragraph-line/higher-endpoint exclusion under stem, hand, topology and physical-page controls",
            "counterevidence": "probabilistic only; nonfinal m and final l remain; mechanism open",
            "claim_ceiling": "physical-line association only",
        },
        {
            "candidate_id": "C2", "candidate": "HIGHER_SCOPE_CLOSURE_ONLY",
            "capacity_status": "PHYSICAL_INTERIOR_AVAILABLE", "statistical_status": "STRICT_INTERIOR_LINE_EFFECT_RETAINS",
            "decision": "REJECT_AS_SOLE_CAUSE", "positive_evidence": "none beyond coincident boundary events",
            "counterevidence": "411 strict interior events retain the line-edge association",
            "claim_ceiling": "does not exclude unannotated microfields or modulation",
        },
        {
            "candidate_id": "C3", "candidate": "PARAGRAPH_OR_STATEMENT_INCREMENT",
            "capacity_status": "DIRECT_FAIL__FROZEN_LEGACY_STATEMENT_PASS_ONE_INTERNAL_TARGET",
            "statistical_status": f"FROZEN_STATEMENT_OR_{f12(test_stats['FROZEN_LEGACY_STATEMENT_INCREMENT']['odds_ratio'])}_P_{f12(test_stats['FROZEN_LEGACY_STATEMENT_INCREMENT']['exact_upper_p'])}",
            "decision": "NOT_SELECTED_IN_ONLY_SCOREABLE_SENSITIVITY", "positive_evidence": "six of ten direct paragraph-close targets and five of nine direct statement-close targets end in m",
            "counterevidence": "zero direct internal endpoints; wider frozen-stem statement sensitivity has fourteen targets, one internal l and no m-specific gain",
            "claim_ceiling": "direct capacity failure is not absence; projected null does not prove equivalence",
        },
        {
            "candidate_id": "C4", "candidate": "RECORD_OR_PANEL_INCREMENT",
            "capacity_status": "FAIL_ONE_UNIQUE_TARGET_ENDPOINT_L_ONLY", "statistical_status": "NOT_IDENTIFIABLE_ABOVE_LINE_EDGE",
            "decision": "STOP_INSUFFICIENT_CAPACITY", "positive_evidence": "one paired target reaches both a record and panel endpoint",
            "counterevidence": "the target is cthal with l; no m endpoint and no internal record/panel target",
            "claim_ceiling": "no record or panel closing meaning",
        },
        {
            "candidate_id": "C5", "candidate": "STRONG_MONOTONE_RECORD_PANEL_CLOSE",
            "capacity_status": "24_DEEP_LINE_FINAL_TARGETS_2970_WORLDS", "statistical_status": "M_PROGRESS_DIRECTION_OPPOSITE",
            "decision": "NOT_SUPPORTED", "positive_evidence": "five deep m events are line-final",
            "counterevidence": "all five remain 3 to13 record lines before closure; one-sided later-progress tests fail",
            "claim_ceiling": "does not exclude weak or nonlinear status effects",
        },
        {
            "candidate_id": "C6", "candidate": "LOCAL_LABEL_REGISTER_TERMINAL",
            "capacity_status": f"LABEL_MARGIN_PASS__{len(fully_crossed)}_FULL_CROSSINGS__PAGE_STRATA_THIN",
            "statistical_status": f"ANY_FINAL_PAGE_P_{f12(test_stats['LABEL_STATUS_GIVEN_ANY_FINAL_PHYSICAL_PAGE']['exact_upper_p'])}__MULTI_FINAL_PAGE_P_{f12(test_stats['LABEL_STATUS_GIVEN_MULTI_FINAL_PHYSICAL_PAGE']['exact_upper_p'])}",
            "decision": "NOT_SELECTED_NO_PAGE_CONTROLLED_INCREMENT", "positive_evidence": "80 local projections include20 m and60 l",
            "counterevidence": f"{len(bridge_stems)} bridge stems and {len(fully_crossed)} full crossings, but page controls retain only {test_stats['LABEL_STATUS_GIVEN_ANY_FINAL_PHYSICAL_PAGE']['informative_strata']}/{test_stats['LABEL_STATUS_GIVEN_MULTI_FINAL_PHYSICAL_PAGE']['informative_strata']} informative strata and no selected gain",
            "claim_ceiling": "no label meaning or terminal register value",
        },
        {
            "candidate_id": "C7", "candidate": "CONTEXT_ROLE_ASSOCIATED_TERMINAL",
            "capacity_status": "28_EXACT_JOIN_BIDIRECTIONAL_RUNNING_STEMS_388_EVENTS", "statistical_status": "UNTESTED_HERE",
            "decision": "NEXT_HELD_STEM_TEST", "positive_evidence": "masked complete-form neighbours can be tested on held physical pages and stems after physical-position control",
            "counterevidence": "distribution alone supplies no role or gloss",
            "claim_ceiling": "future structural role only before an independent semantic anchor",
        },
    ]
    write_tsv(CANDIDATES, candidate_rows, list(candidate_rows[0]))

    card_rows = [
        {
            "card_id": "GDT801-SC1",
            "scope": "observed terminal m on a complete surface with a nonempty attested l counterpart in the admitted GDT800 population",
            "structural_tag": "PHYSICAL_LINE_EDGE_FAVOURED_TERMINAL_SURFACE__HIGHER_SCOPE_UNTESTED",
            "german_display": "physisch zeilenrandbevorzugte Endform; Absatz-/Record-/Morphologiewert offen",
            "confidence": "HIGH_PHYSICAL_ASSOCIATION__DIRECT_HIGHER_SCOPE_CAPACITY_FAIL__ZERO_LEXICAL",
            "positive_evidence": f"strict interior page-controlled OR {f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE']['odds_ratio'])}, exact p {f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE']['exact_upper_p'])}",
            "counterevidence": "direct higher endpoints are collinear with physical line edge; projected legacy-statement sensitivity has no gain; A09 labels remain unexplained; l and m are not interchangeable",
            "token_display_rule": "show observed terminal and actual physical position only; never substitute one surface for the other",
            "equivalence_license": "NONE__DO_NOT_NORMALIZE_M_TO_L", "semantic_export": "ZERO",
            "plaintext_value": "UNKNOWN",
        }
    ]
    write_tsv(CARD, card_rows, list(card_rows[0]))

    # The next experiment is licensed from the exact GDT800-to-GDT791 join,
    # not from the wider projection-only sensitivity population.  Keeping the
    # two populations distinct yields the frozen 28-stem/388-event deck.
    direct_running_endings: dict[str, set[str]] = defaultdict(set)
    for row in direct_running:
        direct_running_endings[row["stem"]].add(row["terminal"])
    bidirectional_running_stems = {
        stem for stem, endings in direct_running_endings.items() if endings == {"l", "m"}
    }
    bidirectional_running_events = [row for row in direct_running if row["stem"] in bidirectional_running_stems]
    status = "PARTIAL__542_EXACT_JOINS__530_RUNNING__411_STRICT_INTERIOR__PHYSICAL_LINE_EDGE_RETAINS__DIRECT_HIGHER_CLOSURE_CAPACITY_STOP__PROJECTED_STATEMENT_NO_GAIN__ZERO_LEXEMES"
    report = f"""# GDT801 — terminal `l/m` boundary-hierarchy discriminator

Status: **{status}**

## Outcome

The valid source-selector join contains **{len(join_rows)}** exact events:
**{len(direct_running)}** running events and **{len(join_rows) - len(direct_running)}**
local labels on {len({row['source_selector'] for row in join_rows})} selectors/{len({row['physical_page'] for row in join_rows})}
physical pages. Forty-three correct matches have selector names distinct from
their normalized physical folio; a physical-page join would wrongly lose them.

In running text, `m` is physical multi-token-line-final in
**{test_stats['DIRECT_LINE_FINAL_STEM']['m_positive']}/{test_stats['DIRECT_LINE_FINAL_STEM']['m_n']}**
events versus `l` in
**{test_stats['DIRECT_LINE_FINAL_STEM']['l_positive']}/{test_stats['DIRECT_LINE_FINAL_STEM']['l_n']}**.
Exact-stem conditioning gives OR
**{f12(test_stats['DIRECT_LINE_FINAL_STEM']['odds_ratio'])}** and
`p={f12(test_stats['DIRECT_LINE_FINAL_STEM']['exact_upper_p'])}`.

## Higher-boundary exclusion

The strict test removes every paragraph-start and paragraph-end line plus every
joined legacy-statement, record and panel endpoint. Its **{len(interior_rows)}**
remaining events still give `m` final
**{test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM']['m_positive']}/{test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM']['m_n']}**
versus `l`
**{test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM']['l_positive']}/{test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM']['l_n']}**.
Stem OR is **{f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM']['odds_ratio'])}**;
stem×hand **{f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_HAND']['odds_ratio'])}**;
stem×topology **{f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_TOPOLOGY']['odds_ratio'])}**;
and stem×physical-page **{f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE']['odds_ratio'])}**
with exact `p={f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE']['exact_upper_p'])}`.
Thus annotated higher-scope closure cannot be the sole cause of the line-edge
association.

This is one composite exclusion, not four independent robustness wins: all
nine direct statement endpoints and the sole direct record/panel endpoint are
already on paragraph-end lines. The higher endpoint flags therefore remove no
additional direct target after paragraph-start/end lines are excluded.

## Why record and panel value remain open

All ten joined paragraph-close targets and all nine joined legacy-statement
close targets are themselves line-final. Across thirteen records and ten
panels, only one unique joined endpoint exists: f83r.55 `cthal`, ending in `l`.
There is no `m` record/panel endpoint and no internal direct target endpoint.
All four **direct-join** increment gates therefore stop before scoring. This is
non-identifiability, not evidence that higher structure has no effect.

The wider frozen-stem projection supplies exactly one scoreable sensitivity:
fourteen legacy-statement endpoints include six `m`, eight `l` and one
physical-line-internal `l`. Its stem×line-position estimate is OR
{f12(test_stats['FROZEN_LEGACY_STATEMENT_INCREMENT']['odds_ratio'])} with
`p={f12(test_stats['FROZEN_LEGACY_STATEMENT_INCREMENT']['exact_upper_p'])}`.
It supplies no positive `m`-specific statement gain, but one projection-only
internal counterexample cannot establish absence. The inherited legacy
statement segmentation is used only as an analyst boundary axis; GDT801 does
not revalidate or translate its old `DY` interpretation.

The 24 deep-page line-final targets provide only a strong-monotone diagnostic.
The five `m` events occur 13, 9, 8, 3 and 7 record lines before closure. Their
mean record progress is {progress_rows[0]['observed_m_mean']} versus
{progress_rows[0]['observed_l_mean']} for `l` (`p={progress_rows[0]['exact_upper_p']}`
for `m` later); panel progress is {progress_rows[1]['observed_m_mean']} versus
{progress_rows[1]['observed_l_mean']} (`p={progress_rows[1]['exact_upper_p']}`).
A strong monotone record/panel-close rule is not supported.

## Refined renderer and label sensitivity

The selected tag is now
**PHYSICAL_LINE_EDGE_FAVOURED_TERMINAL_SURFACE__HIGHER_SCOPE_UNTESTED**.
It is displayed as “physisch zeilenrandbevorzugte Endform; Absatz-/Record-/
Morphologiewert offen”. It neither equates `l/m` nor identifies allography,
inflection, abbreviation, case, sound or meaning.

The separate frozen-stem projection contains {len(projection_rows)} events,
including {len(local_rows)} local labels. Local unit finality is singleton- and
page-confounded, and {len(bridge_stems)} stems bridge local/running registers
and **{len(fully_crossed)}** provide a complete `l/m × local/running` crossing.
After physical-page control, label-status tests retain only {test_stats['LABEL_STATUS_GIVEN_ANY_FINAL_PHYSICAL_PAGE']['informative_strata']}
and {test_stats['LABEL_STATUS_GIVEN_MULTI_FINAL_PHYSICAL_PAGE']['informative_strata']} informative strata
(`p={f12(test_stats['LABEL_STATUS_GIVEN_ANY_FINAL_PHYSICAL_PAGE']['exact_upper_p'])}`
and `p={f12(test_stats['LABEL_STATUS_GIVEN_MULTI_FINAL_PHYSICAL_PAGE']['exact_upper_p'])}`).
No terminal label value is selected.

For bookkeeping, the wider projected running population has {len(projected_bidirectional_stems)}
bidirectional stems and {len(projected_bidirectional_events)} events:
{sum(row['in_exact_542_join'] for row in projected_bidirectional_events)} exact joins plus
{sum(not row['in_exact_542_join'] for row in projected_bidirectional_events)} projection-only events. It receives no
independent-evidence credit and does not replace the cleaner exact-join deck
below.

## Next discriminator

The exact joined running population contains {len(bidirectional_running_stems)} stems with both endings
represented somewhere in that population and {len(bidirectional_running_events)} events. This does not
require both endings on the same page.
Mask the target and test whether complete neighbouring surfaces predict the
terminal on held stems and held physical pages after physical position is
fixed. The f95v1/f95v2 selectors must remain in one f95v page fold; selector
holdout is only a nested sensitivity.
Cross-stem context gain would support a bound role field; only within-stem gain
would favor separately learned wholes; no gain would favor the layout rival.
No new page is required.
"""
    REPORT.write_text(report, encoding="utf-8")

    outputs = [
        JOIN, INTERIOR, PROJECTION, ENDPOINTS, DEEP, LOCAL, HIERARCHY, TESTS,
        CAPACITY, PROGRESS, CANDIDATES, CARD, REPORT,
    ]
    inputs = [G800_OCC, G800_STEMS, G800_CARD, G791_SPINE, G791_LINES, SOURCE_LOCK, MODEL_SPECS]
    result: dict[str, Any] = {
        "schema": "GDT801_RESULT_V1", "experiment": "GDT801", "status": status,
        "decision": "PHYSICAL_LINE_EDGE_PRIMARY__DIRECT_HIGHER_CLOSURE_UNIDENTIFIED__PROJECTED_LEGACY_STATEMENT_NO_GAIN",
        "join": {
            "rows": len(join_rows), "running": len(direct_running), "local": len(join_rows) - len(direct_running),
            "source_selectors": len({row["source_selector"] for row in join_rows}),
            "physical_pages": len({row["physical_page"] for row in join_rows}),
            "selector_not_physical_page": sum(row["source_selector"] != row["physical_page"] for row in join_rows),
            "strict_interior": len(interior_rows),
        },
        "projection": {
            "rows": len(projection_rows), "running": len(projected_running), "local": len(local_rows),
            "exact_join": sum(row["in_exact_542_join"] for row in projection_rows),
            "projection_only": sum(not row["in_exact_542_join"] for row in projection_rows),
            "represented_stems": len({row["stem"] for row in projection_rows}),
            "local_running_bridge_stems": len(bridge_stems), "fully_crossed_stems": len(fully_crossed),
            "local_label_margin_gate": local_label_gate,
            "bidirectional_running_stems": len(projected_bidirectional_stems),
            "bidirectional_running_events": len(projected_bidirectional_events),
            "bidirectional_running_exact_join": sum(row["in_exact_542_join"] for row in projected_bidirectional_events),
            "bidirectional_running_projection_only": sum(not row["in_exact_542_join"] for row in projected_bidirectional_events),
            "projection_bidirectional_license": "NONE__SENSITIVITY_ONLY",
        },
        "primary": {
            "all_four_strict_interior_pass": primary_pass,
            "direct_stem": test_stats["DIRECT_LINE_FINAL_STEM"],
            "strict_stem": test_stats["STRUCTURAL_INTERIOR_LINE_FINAL_STEM"],
            "strict_stem_hand": test_stats["STRUCTURAL_INTERIOR_LINE_FINAL_STEM_HAND"],
            "strict_stem_topology": test_stats["STRUCTURAL_INTERIOR_LINE_FINAL_STEM_TOPOLOGY"],
            "strict_stem_physical_page": test_stats["STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE"],
        },
        "higher_boundary_capacity": {
            "paragraph": gate_map[("DIRECT_RUNNING", "PARAGRAPH")],
            "legacy_statement": gate_map[("DIRECT_RUNNING", "LEGACY_STATEMENT")],
            "record": gate_map[("DIRECT_RUNNING", "RECORD")],
            "panel": gate_map[("DIRECT_RUNNING", "PANEL")],
            "all_direct_increment_gates_fail": not any(
                gate_map[("DIRECT_RUNNING", boundary)]
                for boundary in ("PARAGRAPH", "LEGACY_STATEMENT", "RECORD", "PANEL")
            ),
            "frozen_projection_legacy_statement": gate_map[("FROZEN_STEM_RUNNING", "LEGACY_STATEMENT")],
            "frozen_projection_legacy_statement_test": test_stats["FROZEN_LEGACY_STATEMENT_INCREMENT"],
            "record_panel_unique_target_endpoint": "f83r.55:cthal:l",
        },
        "deep_progress": {
            "targets": len(deep_rows), "m": 5, "l": 19, "worlds": 2970,
            "record": progress_rows[0], "panel": progress_rows[1],
        },
        "next_test": {
            "exact_join_bidirectional_running_stems": len(bidirectional_running_stems),
            "events": len(bidirectional_running_events),
            "route": "HELD_STEM_MASKED_COMPLETE_NEIGHBOUR_CONTEXT_AFTER_PHYSICAL_POSITION_CONTROL",
        },
        "semantic_exports": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "equivalence_licenses": 0, "f84_or_f84r_accessed": False,
        "claim_ceiling": "PHYSICAL_LINE_ASSOCIATION_ONLY__HIGHER_SCOPE_UNTESTED__NO_EQUIVALENCE_MORPHEME_OR_TRANSLATION",
        "inputs": {rel(path): sha(path) for path in inputs},
        "outputs": {rel(path): sha(path) for path in outputs},
        "implementation": {rel(Path(__file__)): sha(Path(__file__))},
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(
        f"join={len(join_rows)} running={len(direct_running)} local={len(join_rows)-len(direct_running)}; "
        f"strict interior={len(interior_rows)}"
    )
    print(
        f"strict stem OR={f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM']['odds_ratio'])} "
        f"page OR={f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE']['odds_ratio'])} "
        f"p={f12(test_stats['STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE']['exact_upper_p'])}"
    )
    print("direct higher closure capacity: STOP; projected legacy-statement sensitivity OR=1.1 p=0.606481481481")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
