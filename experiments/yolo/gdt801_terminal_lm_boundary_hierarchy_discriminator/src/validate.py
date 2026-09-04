#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt801_terminal_lm_boundary_hierarchy_discriminator"
SRC = BASE / "src"
ART = BASE / "artifacts"
G800_OCC = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G800_STEMS = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv"
G800_CARD = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_STRUCTURAL_CARD.tsv"
G791_SPINE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
G791_LINES = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv"
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
VALIDATION = ART / "VALIDATION.json"
REPORT = BASE / "REPORT.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truth(value: object) -> bool:
    if value in (True, 1, "1", "True"):
        return True
    if value in (False, 0, "0", "False"):
        return False
    raise ValueError(f"not boolean: {value!r}")


def close(left: float, right: float, tolerance: float = 2e-10) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=1e-14)


def cells(
    rows: Iterable[dict[str, Any]],
    strata: Sequence[str],
    positive: Callable[[dict[str, Any]], bool],
) -> list[tuple[int, int, int, int]]:
    table: dict[tuple[Any, ...], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        cell = table[tuple(row[field] for field in strata)]
        if row["terminal"] == "m":
            cell[0 if positive(row) else 1] += 1
        else:
            cell[2 if positive(row) else 3] += 1
    return [tuple(table[key]) for key in sorted(table, key=lambda item: tuple(map(str, item)))]


def analyse(
    rows: Sequence[dict[str, Any]],
    strata: Sequence[str],
    positive: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    tables = cells(rows, strata, positive)
    numerator = 0.0
    denominator = 0.0
    distribution: dict[int, float] = {0: 1.0}
    observed = 0
    expected = 0.0
    informative = 0
    for a, b, c, d in tables:
        n = a + b + c + d
        m_total = a + b
        l_total = c + d
        positive_total = a + c
        negative_total = b + d
        if not (n and m_total and l_total and positive_total and negative_total):
            continue
        informative += 1
        numerator += a * d / n
        denominator += b * c / n
        observed += a
        expected += positive_total * m_total / n
        low = max(0, positive_total - l_total)
        high = min(m_total, positive_total)
        divisor = math.comb(n, positive_total)
        local = {
            value: math.comb(m_total, value) * math.comb(l_total, positive_total - value) / divisor
            for value in range(low, high + 1)
        }
        updated: dict[int, float] = defaultdict(float)
        for old_value, old_probability in distribution.items():
            for value, probability in local.items():
                updated[old_value + value] += old_probability * probability
        distribution = dict(updated)
    odds: float | None
    if not informative:
        odds = None
    elif denominator:
        odds = numerator / denominator
    elif numerator:
        odds = math.inf
    else:
        odds = None
    upper = min(1.0, sum(probability for value, probability in distribution.items() if value >= observed)) if informative else 1.0
    lower = min(1.0, sum(probability for value, probability in distribution.items() if value <= observed)) if informative else 1.0
    counts = Counter(row["terminal"] for row in rows)
    positives = Counter(row["terminal"] for row in rows if positive(row))
    return {
        "n_rows": len(rows), "m_n": counts["m"], "m_positive": positives["m"],
        "l_n": counts["l"], "l_positive": positives["l"], "strata": len(tables),
        "informative_strata": informative, "observed_m_positive": observed,
        "expected_m_positive": expected, "odds_ratio": odds,
        "exact_upper_p": upper, "exact_lower_p": lower,
    }


def numeric(value: str) -> float | None:
    if value == "NA":
        return None
    if value == "INF":
        return math.inf
    return float(value)


def last_events(rows: Sequence[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        identifier = row[field]
        if identifier == "NONE":
            continue
        if identifier not in result or int(row["occurrence_ordinal"]) > int(result[identifier]["occurrence_ordinal"]):
            result[identifier] = row
    return result


def main() -> int:
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    unhashed = dict(result)
    content_hash = unhashed.pop("content_hash")
    check("result_content_hash", content_hash == hashlib.sha256(json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    for category in ("inputs", "outputs", "implementation"):
        for path, digest in result[category].items():
            check(f"{category}_hash:{path}", sha(ROOT / path) == digest)

    join_schema = [
        "join_ordinal", "gdt800_occurrence_id", "gdt791_occurrence_ordinal", "gdt791_occurrence_id",
        "source_selector", "physical_page", "locus", "token_index", "token_count", "surface", "stem", "terminal",
        "section", "language", "hand", "distance_from_end", "position_class", "any_line_final",
        "multi_line_final", "single_token_line", "occurrence_kind", "line_kind", "paragraph_start",
        "paragraph_end_line", "paragraph_role", "paragraph_close", "legacy_statement_id", "statement_close",
        "record_id", "record_close", "panel_id", "panel_close", "topology_family", "register", "context_scope",
        "structurally_internal", "semantic_export_credit",
    ]
    projection_schema = [
        "projection_ordinal", "in_exact_542_join", "gdt800_occurrence_id", "gdt791_occurrence_ordinal",
        "gdt791_occurrence_id", "source_selector", "physical_page", "locus", "token_index", "token_count",
        "surface", "stem", "terminal", "distance_from_end", "position_class", "any_line_final",
        "multi_line_final", "single_token_line", "occurrence_kind", "line_kind", "paragraph_start",
        "paragraph_end_line", "paragraph_role", "paragraph_close", "legacy_statement_id", "statement_close",
        "record_id", "record_close", "panel_id", "panel_close", "topology_family", "register", "context_scope",
        "structurally_internal", "semantic_export_credit",
    ]
    schemas = {
        JOIN: join_schema,
        INTERIOR: join_schema,
        PROJECTION: projection_schema,
        LOCAL: projection_schema,
        ENDPOINTS: ["boundary_ordinal", "boundary_type", "structure_id", "physical_page", "source_selector", "endpoint_occurrence_id", "locus", "line_number", "token_index", "token_count", "surface", "physical_line_final", "paired_target", "paired_stem", "terminal", "coincident_record_panel_endpoint", "capacity_class", "semantic_export_credit"],
        DEEP: ["deep_ordinal", "gdt800_occurrence_id", "gdt791_occurrence_id", "physical_page", "source_selector", "locus", "surface", "stem", "terminal", "record_id", "panel_id", "record_line_rank", "record_line_count", "record_line_progress", "record_lines_after", "record_events_after", "panel_line_rank", "panel_line_count", "panel_line_progress", "panel_lines_after", "panel_events_after", "record_close", "panel_close", "semantic_export_credit"],
        HIERARCHY: ["boundary_type", "group_count", "internal_end_count", "multi_line_final_end_count", "singleton_end_count", "identifiability_note"],
        TESTS: ["test_id", "population", "row_filter", "outcome", "strata_fields", "n_rows", "m_n", "m_positive", "l_n", "l_positive", "strata", "informative_strata", "observed_m_positive", "expected_m_positive", "mh_odds_ratio", "exact_upper_p", "exact_lower_p", "decision"],
        CAPACITY: ["population", "boundary_type", "group_count", "target_rows", "m_rows", "l_rows", "multi_line_final_rows", "physical_line_internal_rows", "physical_line_internal_m", "physical_line_internal_l", "distinct_stems", "distinct_source_selectors", "distinct_physical_pages", "informative_stem_x_line_final_strata", "terminal_margin_page_gate", "increment_capacity_pass", "internal_discriminator_pass", "failure_reason"],
        PROGRESS: ["test_id", "axis", "n_rows", "m_n", "l_n", "observed_m_mean", "observed_l_mean", "m_minus_l", "permutation_worlds", "exact_upper_p", "exact_lower_p", "direction_gate", "decision"],
        CANDIDATES: ["candidate_id", "candidate", "capacity_status", "statistical_status", "decision", "positive_evidence", "counterevidence", "claim_ceiling"],
        CARD: ["card_id", "scope", "structural_tag", "german_display", "confidence", "positive_evidence", "counterevidence", "token_display_rule", "equivalence_license", "semantic_export", "plaintext_value"],
    }
    expected_outputs = {path.relative_to(ROOT).as_posix() for path in schemas} | {REPORT.relative_to(ROOT).as_posix()}
    check("result_output_set_exact", set(result["outputs"]) == expected_outputs)
    for path, schema in schemas.items():
        rows = read_tsv(path)
        check(f"schema:{path.name}", header(path) == schema)
        check(f"no_blank_cells:{path.name}", all(all(row[field] != "" for field in schema) for row in rows))

    source_locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    check("five_source_locks", len(source_locks) == 5)
    check("source_lock_hashes", all(sha(ROOT / row["path"]) == row["sha256"] for row in source_locks))
    check("source_lock_paths_relative", all(not Path(row["path"]).is_absolute() for row in source_locks))
    check("seven_candidate_specs", {row["candidate_id"] for row in read_tsv(SRC / "CANDIDATE_MODEL_SPECS.tsv")} == {f"C{i}" for i in range(1, 8)})

    g800 = read_tsv(G800_OCC)
    stem_summary = read_tsv(G800_STEMS)
    inherited_card = read_tsv(G800_CARD)
    spine = read_tsv(G791_SPINE)
    lines = read_tsv(G791_LINES)
    check("source_card", len(inherited_card) == 1 and inherited_card[0]["structural_tag"] == "BOUNDARY_FAVOURED_TERMINAL_SURFACE")
    check("source_counts", (len(g800), len(stem_summary), len(spine), len(lines)) == (4137, 155, 5866, 1007))
    check("source_stems_nonempty", all(row["stem"] for row in g800 + stem_summary))
    material = g800 + spine + lines
    check("sealed_selectors_absent", all(not any(value.startswith("f84") for value in row.values()) for row in material))

    spine_by_key: dict[tuple[str, str, int], dict[str, str]] = {}
    spine_by_id: dict[str, dict[str, str]] = {}
    for row in spine:
        key = (row["source_selector"], row["locus"], int(row["token_ordinal_in_line"]))
        check(f"spine_key_unique:{row['occurrence_id']}", key not in spine_by_key and row["occurrence_id"] not in spine_by_id)
        spine_by_key[key] = row
        spine_by_id[row["occurrence_id"]] = row
    line_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in lines:
        key = (row["source_selector"], row["locus"])
        check(f"line_key_unique:{row['source_selector']}:{row['locus']}", key not in line_by_key)
        line_by_key[key] = row

    expected_join: dict[str, tuple[dict[str, str], dict[str, str], dict[str, str]]] = {}
    physical_join_count = 0
    selector_mismatch = Counter()
    for source in g800:
        occurrence = spine_by_key.get((source["page"], source["locus"], int(source["token_index"])))
        if occurrence is None:
            continue
        check(f"join_surface_source:{source['occurrence_id']}", source["surface"] == occurrence["surface"])
        line = line_by_key[(occurrence["source_selector"], occurrence["locus"])]
        expected_join[occurrence["occurrence_id"]] = (source, occurrence, line)
        if source["page"] == occurrence["physical_page"]:
            physical_join_count += 1
        else:
            selector_mismatch[(source["page"], occurrence["physical_page"])] += 1
    check("source_selector_join_542", len(expected_join) == 542)
    check("physical_page_join_would_be_499", physical_join_count == 499)
    check("selector_normalization_43", selector_mismatch == Counter({("f89r1", "f89r"): 31, ("f95v1", "f95v"): 10, ("f95v2", "f95v"): 2}))

    running_spine = [row for row in spine if row["occurrence_kind"] == "RUNNING_EVENT"]
    statement_last = last_events(running_spine, "legacy_statement_id")
    record_last = last_events(running_spine, "record_id")
    panel_last = last_events(running_spine, "panel_id")
    statement_ids = {row["occurrence_id"] for row in statement_last.values()}
    record_ids = {row["occurrence_id"] for row in record_last.values()}
    panel_ids = {row["occurrence_id"] for row in panel_last.values()}

    join_rows = read_tsv(JOIN)
    check("join_rows_542", len(join_rows) == 542 and len({row["gdt791_occurrence_id"] for row in join_rows}) == 542)
    check("join_id_set", {row["gdt791_occurrence_id"] for row in join_rows} == set(expected_join))
    check("join_kind_counts", Counter(row["occurrence_kind"] for row in join_rows) == Counter({"RUNNING_EVENT": 530, "LOCAL_ADDRESS_OR_LABEL": 12}))
    check("join_scope_counts", len({row["source_selector"] for row in join_rows}) == 24 and len({row["physical_page"] for row in join_rows}) == 23)
    for row in join_rows:
        source, occurrence, line = expected_join[row["gdt791_occurrence_id"]]
        token_index = int(occurrence["token_ordinal_in_line"])
        token_count = int(line["token_count"])
        final = token_index == token_count
        singleton = token_count == 1
        paragraph_close = occurrence["occurrence_kind"] == "RUNNING_EVENT" and line["paragraph_end"] == "1" and final
        strict = occurrence["occurrence_kind"] == "RUNNING_EVENT" and line["paragraph_start"] == line["paragraph_end"] == "0" and occurrence["occurrence_id"] not in statement_ids | record_ids | panel_ids
        check(f"join_identity:{row['join_ordinal']}", row["gdt800_occurrence_id"] == source["occurrence_id"] and row["surface"] == occurrence["surface"] and row["stem"] == source["stem"] and row["terminal"] == source["terminal"])
        check(f"join_location:{row['join_ordinal']}", row["source_selector"] == occurrence["source_selector"] and row["physical_page"] == occurrence["physical_page"] and row["locus"] == occurrence["locus"] and int(row["token_index"]) == token_index and int(row["token_count"]) == token_count)
        check(f"join_line_flags:{row['join_ordinal']}", truth(row["any_line_final"]) == final and truth(row["multi_line_final"]) == (final and not singleton) and truth(row["single_token_line"]) == singleton and int(row["distance_from_end"]) == token_count - token_index)
        check(f"join_boundary_flags:{row['join_ordinal']}", truth(row["paragraph_close"]) == paragraph_close and truth(row["statement_close"]) == (occurrence["occurrence_id"] in statement_ids) and truth(row["record_close"]) == (occurrence["occurrence_id"] in record_ids) and truth(row["panel_close"]) == (occurrence["occurrence_id"] in panel_ids) and truth(row["structurally_internal"]) == strict)

    direct_running = [row for row in join_rows if row["occurrence_kind"] == "RUNNING_EVENT"]
    interior_rows = read_tsv(INTERIOR)
    expected_interior = {row["gdt791_occurrence_id"] for row in direct_running if truth(row["structurally_internal"])}
    check("strict_interior_411", len(expected_interior) == len(interior_rows) == 411)
    check("strict_interior_exact", {row["gdt791_occurrence_id"] for row in interior_rows} == expected_interior)
    check("higher_endpoints_nested_in_paragraph_end_lines", all(truth(row["paragraph_end_line"]) for row in direct_running if truth(row["statement_close"]) or truth(row["record_close"]) or truth(row["panel_close"])))

    frozen_stems = {row["stem"] for row in stem_summary}
    expected_projection = {
        row["occurrence_id"]: row for row in spine
        if len(row["surface"]) > 1 and row["surface"][-1] in {"l", "m"} and row["surface"][:-1] in frozen_stems
    }
    projection_rows = read_tsv(PROJECTION)
    check("projection_743", len(projection_rows) == len(expected_projection) == 743)
    check("projection_exact_ids", {row["gdt791_occurrence_id"] for row in projection_rows} == set(expected_projection))
    check("projection_kind_counts", Counter(row["occurrence_kind"] for row in projection_rows) == Counter({"RUNNING_EVENT": 663, "LOCAL_ADDRESS_OR_LABEL": 80}))
    check("projection_join_split", Counter(row["in_exact_542_join"] for row in projection_rows) == Counter({"1": 542, "0": 201}))
    for row in projection_rows:
        occurrence = expected_projection[row["gdt791_occurrence_id"]]
        line = line_by_key[(occurrence["source_selector"], occurrence["locus"])]
        token_index = int(occurrence["token_ordinal_in_line"])
        token_count = int(line["token_count"])
        check(f"projection_identity:{row['projection_ordinal']}", row["surface"] == occurrence["surface"] and row["stem"] == occurrence["surface"][:-1] and row["terminal"] == occurrence["surface"][-1])
        check(f"projection_flags:{row['projection_ordinal']}", truth(row["any_line_final"]) == (token_index == token_count) and truth(row["single_token_line"]) == (token_count == 1) and truth(row["in_exact_542_join"]) == (row["gdt791_occurrence_id"] in expected_join))
    local_rows = read_tsv(LOCAL)
    check("local_projection_exact", len(local_rows) == 80 and {row["gdt791_occurrence_id"] for row in local_rows} == {row["gdt791_occurrence_id"] for row in projection_rows if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"})

    projected_running = [row for row in projection_rows if row["occurrence_kind"] == "RUNNING_EVENT"]
    direct_endings: dict[str, set[str]] = defaultdict(set)
    projected_endings: dict[str, set[str]] = defaultdict(set)
    for row in direct_running:
        direct_endings[row["stem"]].add(row["terminal"])
    for row in projected_running:
        projected_endings[row["stem"]].add(row["terminal"])
    direct_bi = {stem for stem, endings in direct_endings.items() if endings == {"l", "m"}}
    projected_bi = {stem for stem, endings in projected_endings.items() if endings == {"l", "m"}}
    direct_bi_rows = [row for row in direct_running if row["stem"] in direct_bi]
    projected_bi_rows = [row for row in projected_running if row["stem"] in projected_bi]
    check("next_deck_28_388", len(direct_bi) == 28 and len(direct_bi_rows) == 388 and Counter(row["terminal"] for row in direct_bi_rows) == Counter({"l": 336, "m": 52}))
    check("projection_deck_30_478", len(projected_bi) == 30 and len(projected_bi_rows) == 478 and sum(truth(row["in_exact_542_join"]) for row in projected_bi_rows) == 391)

    endpoint_rows = read_tsv(ENDPOINTS)
    expected_endpoint_keys = {("RECORD", key, row["occurrence_id"]) for key, row in record_last.items()} | {("PANEL", key, row["occurrence_id"]) for key, row in panel_last.items()}
    check("endpoint_23_exact", len(endpoint_rows) == 23 and {(row["boundary_type"], row["structure_id"], row["endpoint_occurrence_id"]) for row in endpoint_rows} == expected_endpoint_keys)
    check("endpoint_all_line_final", all(truth(row["physical_line_final"]) for row in endpoint_rows))
    paired_endpoints = [row for row in endpoint_rows if truth(row["paired_target"])]
    check("one_unique_paired_endpoint", len(paired_endpoints) == 2 and {row["endpoint_occurrence_id"] for row in paired_endpoints} == {"G407-E3795"} and {(row["surface"], row["terminal"]) for row in paired_endpoints} == {("cthal", "l")})

    hierarchy_rows = {row["boundary_type"]: row for row in read_tsv(HIERARCHY)}
    expected_hierarchy = {
        "PARAGRAPH": (88, 0, 84, 4), "LEGACY_STATEMENT": (793, 631, 158, 4),
        "RECORD": (13, 0, 13, 0), "PANEL": (10, 0, 10, 0),
    }
    check("hierarchy_types", set(hierarchy_rows) == set(expected_hierarchy))
    for boundary, expected in expected_hierarchy.items():
        row = hierarchy_rows[boundary]
        check(f"hierarchy:{boundary}", tuple(int(row[field]) for field in ("group_count", "internal_end_count", "multi_line_final_end_count", "singleton_end_count")) == expected)

    capacity_rows = read_tsv(CAPACITY)
    capacity_by_key = {(row["population"], row["boundary_type"]): row for row in capacity_rows}
    check("eight_capacity_rows", len(capacity_rows) == len(capacity_by_key) == 8)
    check("capacity_only_projected_statement", {key for key, row in capacity_by_key.items() if truth(row["increment_capacity_pass"])} == {("FROZEN_STEM_RUNNING", "LEGACY_STATEMENT")})
    projected_statement = capacity_by_key[("FROZEN_STEM_RUNNING", "LEGACY_STATEMENT")]
    check("projected_statement_capacity_counts", tuple(int(projected_statement[field]) for field in ("target_rows", "m_rows", "l_rows", "physical_line_internal_rows", "physical_line_internal_m", "physical_line_internal_l", "distinct_physical_pages", "informative_stem_x_line_final_strata")) == (14, 6, 8, 1, 0, 1, 11, 7))
    check("direct_capacity_all_stop", all(not truth(capacity_by_key[("DIRECT_RUNNING", boundary)]["increment_capacity_pass"]) for boundary in expected_hierarchy))

    test_rows = read_tsv(TESTS)
    tests = {row["test_id"]: row for row in test_rows}
    check("thirty_three_tests", len(test_rows) == len(tests) == 33)

    def verify_test(test_id: str, rows: Sequence[dict[str, Any]], strata: Sequence[str], positive: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
        expected = analyse(rows, strata, positive)
        observed = tests[test_id]
        for key in ("n_rows", "m_n", "m_positive", "l_n", "l_positive", "strata", "informative_strata", "observed_m_positive"):
            check(f"test_count:{test_id}:{key}", int(observed[key]) == expected[key])
        check(f"test_expected:{test_id}", close(float(observed["expected_m_positive"]), expected["expected_m_positive"]))
        for saved, key in (("mh_odds_ratio", "odds_ratio"), ("exact_upper_p", "exact_upper_p"), ("exact_lower_p", "exact_lower_p")):
            observed_value = numeric(observed[saved])
            expected_value = expected[key]
            condition = observed_value is expected_value is None or (
                observed_value is not None and expected_value is not None and
                ((math.isinf(observed_value) and math.isinf(expected_value)) or close(observed_value, expected_value))
            )
            check(f"test_stat:{test_id}:{saved}", condition)
        return expected

    final = lambda row: truth(row["multi_line_final"])
    direct_stem = verify_test("DIRECT_LINE_FINAL_STEM", direct_running, ["stem"], final)
    verify_test("DIRECT_LINE_FINAL_STEM_HAND", direct_running, ["stem", "hand"], final)
    verify_test("DIRECT_LINE_FINAL_STEM_TOPOLOGY", direct_running, ["stem", "topology_family"], final)
    verify_test("DIRECT_LINE_FINAL_STEM_PHYSICAL_PAGE", direct_running, ["stem", "physical_page"], final)
    strict_stem = verify_test("STRUCTURAL_INTERIOR_LINE_FINAL_STEM", interior_rows, ["stem"], final)
    verify_test("STRUCTURAL_INTERIOR_LINE_FINAL_STEM_HAND", interior_rows, ["stem", "hand"], final)
    verify_test("STRUCTURAL_INTERIOR_LINE_FINAL_STEM_TOPOLOGY", interior_rows, ["stem", "topology_family"], final)
    strict_page = verify_test("STRUCTURAL_INTERIOR_LINE_FINAL_STEM_PHYSICAL_PAGE", interior_rows, ["stem", "physical_page"], final)
    frozen_statement_stats = verify_test("FROZEN_LEGACY_STATEMENT_INCREMENT", projected_running, ["stem", "multi_line_final"], lambda row: truth(row["statement_close"]))
    label_any_page = verify_test("LABEL_STATUS_GIVEN_ANY_FINAL_PHYSICAL_PAGE", projection_rows, ["stem", "any_line_final", "physical_page"], lambda row: row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL")
    label_multi_page = verify_test("LABEL_STATUS_GIVEN_MULTI_FINAL_PHYSICAL_PAGE", projection_rows, ["stem", "multi_line_final", "physical_page"], lambda row: row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL")
    full_rows = [{**row, "multi_line_final": int(truth(row["multi_line_final"]))} for row in g800]
    verify_test("GDT800_LINE_LENGTH_CONTROL", full_rows, ["stem", "token_count"], final)
    verify_test("GDT800_SELECTOR_LINE_LENGTH_CONTROL", full_rows, ["stem", "page", "token_count"], final)
    check("direct_primary_counts", (direct_stem["m_n"], direct_stem["m_positive"], direct_stem["l_n"], direct_stem["l_positive"]) == (65, 41, 465, 54))
    check("direct_primary_stat", close(direct_stem["odds_ratio"], 10.729492872838126) and close(direct_stem["exact_upper_p"], 6.833597337270585e-11))
    check("strict_primary_counts", (strict_stem["m_n"], strict_stem["m_positive"], strict_stem["l_n"], strict_stem["l_positive"]) == (44, 28, 367, 43))
    check("strict_page_gate", close(strict_page["odds_ratio"], 10.733333333333334) and close(strict_page["exact_upper_p"], 0.00882464096749811))
    check("projected_statement_no_gain", close(frozen_statement_stats["odds_ratio"], 1.1) and close(frozen_statement_stats["exact_upper_p"], 0.6064814814814813))
    check("label_page_thin", label_any_page["informative_strata"] == 3 and close(label_any_page["exact_upper_p"], 0.4311111111111111) and label_multi_page["informative_strata"] == 6 and close(label_multi_page["exact_upper_p"], 0.4))

    deep_rows = read_tsv(DEEP)
    check("deep_24", len(deep_rows) == 24 and Counter(row["terminal"] for row in deep_rows) == Counter({"l": 19, "m": 5}))
    check("deep_exact_population", {row["gdt791_occurrence_id"] for row in deep_rows} == {row["gdt791_occurrence_id"] for row in direct_running if row["physical_page"] in {"f77r", "f82r", "f83r"} and truth(row["multi_line_final"])})
    check("deep_page_margins", {(page, sum(row["terminal"] == "m" for row in deep_rows if row["physical_page"] == page), sum(1 for row in deep_rows if row["physical_page"] == page)) for page in {"f77r", "f82r", "f83r"}} == {("f77r", 2, 11), ("f82r", 2, 4), ("f83r", 1, 9)})
    progress_rows = {row["axis"]: row for row in read_tsv(PROGRESS)}
    choices: list[list[tuple[int, ...]]] = []
    for page in sorted({row["physical_page"] for row in deep_rows}):
        indices = [index for index, row in enumerate(deep_rows) if row["physical_page"] == page]
        count = sum(deep_rows[index]["terminal"] == "m" for index in indices)
        choices.append(list(itertools.combinations(indices, count)))
    assignments = list(itertools.product(*choices))
    check("deep_worlds_2970", len(assignments) == 2970)
    for axis in ("record", "panel"):
        values = [float(row[f"{axis}_line_progress"]) for row in deep_rows]
        observed_indices = {index for index, row in enumerate(deep_rows) if row["terminal"] == "m"}
        observed = sum(values[index] for index in observed_indices) / 5 - sum(values[index] for index in range(24) if index not in observed_indices) / 19
        null = []
        for assignment in assignments:
            selected = set().union(*(set(part) for part in assignment))
            null.append(sum(values[index] for index in selected) / 5 - sum(values[index] for index in range(24) if index not in selected) / 19)
        upper = sum(value >= observed - 1e-12 for value in null) / len(null)
        lower = sum(value <= observed + 1e-12 for value in null) / len(null)
        saved = progress_rows[axis.upper()]
        check(f"progress_difference:{axis}", close(float(saved["m_minus_l"]), observed))
        check(f"progress_p:{axis}", close(float(saved["exact_upper_p"]), upper) and close(float(saved["exact_lower_p"]), lower))
    check("progress_directions", all(row["decision"] == "FAILS_M_LATER_DIRECTION" for row in progress_rows.values()))

    local_endings: dict[str, set[str]] = defaultdict(set)
    for row in local_rows:
        local_endings[row["stem"]].add(row["terminal"])
    bridges = set(projected_endings) & set(local_endings)
    full_crossings = {stem for stem in bridges if projected_endings[stem] == local_endings[stem] == {"l", "m"}}
    check("label_bridges", len(bridges) == 27 and full_crossings == {"a", "oka", "ota"})

    candidate_rows = {row["candidate_id"]: row for row in read_tsv(CANDIDATES)}
    check("seven_candidate_rows", set(candidate_rows) == {f"C{i}" for i in range(1, 8)})
    check("physical_edge_selected", candidate_rows["C1"]["decision"] == "SELECT_REFINED_STRUCTURAL")
    check("higher_only_rejected", candidate_rows["C2"]["decision"] == "REJECT_AS_SOLE_CAUSE")
    check("statement_not_selected", candidate_rows["C3"]["decision"] == "NOT_SELECTED_IN_ONLY_SCOREABLE_SENSITIVITY")
    check("record_panel_stop", candidate_rows["C4"]["decision"] == "STOP_INSUFFICIENT_CAPACITY")
    check("label_not_selected", candidate_rows["C6"]["decision"] == "NOT_SELECTED_NO_PAGE_CONTROLLED_INCREMENT")
    check("next_context_test", candidate_rows["C7"]["decision"] == "NEXT_HELD_STEM_TEST")
    card_rows = read_tsv(CARD)
    check("one_structural_card", len(card_rows) == 1)
    card = card_rows[0]
    check("card_structural_only", card["structural_tag"] == "PHYSICAL_LINE_EDGE_FAVOURED_TERMINAL_SURFACE__HIGHER_SCOPE_UNTESTED" and card["semantic_export"] == "ZERO" and card["plaintext_value"] == "UNKNOWN")
    check("no_equivalence", card["equivalence_license"] == "NONE__DO_NOT_NORMALIZE_M_TO_L")

    expected_status = "PARTIAL__542_EXACT_JOINS__530_RUNNING__411_STRICT_INTERIOR__PHYSICAL_LINE_EDGE_RETAINS__DIRECT_HIGHER_CLOSURE_CAPACITY_STOP__PROJECTED_STATEMENT_NO_GAIN__ZERO_LEXEMES"
    check("result_status", result["status"] == expected_status)
    check("result_decision", result["decision"] == "PHYSICAL_LINE_EDGE_PRIMARY__DIRECT_HIGHER_CLOSURE_UNIDENTIFIED__PROJECTED_LEGACY_STATEMENT_NO_GAIN")
    check("result_join", result["join"] == {"rows": 542, "running": 530, "local": 12, "source_selectors": 24, "physical_pages": 23, "selector_not_physical_page": 43, "strict_interior": 411})
    check("result_next", result["next_test"]["exact_join_bidirectional_running_stems"] == 28 and result["next_test"]["events"] == 388)
    check("result_projection_audit", result["projection"]["bidirectional_running_stems"] == 30 and result["projection"]["bidirectional_running_events"] == 478 and result["projection"]["bidirectional_running_exact_join"] == 391 and result["projection"]["bidirectional_running_projection_only"] == 87)
    check("result_capacity", result["higher_boundary_capacity"]["all_direct_increment_gates_fail"] is True and result["higher_boundary_capacity"]["frozen_projection_legacy_statement"] is True)
    check("zero_semantics", result["semantic_exports"] == result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["equivalence_licenses"] == 0)
    check("sealed_result", result["f84_or_f84r_accessed"] is False)
    report = REPORT.read_text(encoding="utf-8")
    check("report_core_counts", "**41/65**" in report and "**54/465**" in report and "**28/44**" in report and "**43/367**" in report)
    check("report_capacity", "OR\n1.1" in report and "`p=0.606481481481`" in report and "one composite exclusion" in report)
    check("report_projection_audit", "30\nbidirectional stems and 478 events" in report and "391 exact joins" in report and "87 projection-only" in report)
    check("report_no_meaning", "No terminal label value is selected" in report and "neither equates `l/m`" in report)

    replay_paths = list(schemas) + [REPORT, RESULT]
    before = {str(path): sha(path) for path in replay_paths}
    command = ["python3", str(SRC / "run.py")]
    first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    after_first = {str(path): sha(path) for path in replay_paths}
    second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    after_second = {str(path): sha(path) for path in replay_paths}
    check("builder_replay_one", before == after_first)
    check("builder_replay_two", after_first == after_second)
    check("builder_stdout", expected_status in first.stdout and expected_status in second.stdout)

    validation: dict[str, Any] = {
        "schema": "GDT801_VALIDATION_V1", "status": "PASS",
        "checks_passed": len(checks), "checks_total": len(checks), "checks": checks,
        "independent_statistics": {
            "direct_stem": direct_stem, "strict_stem": strict_stem,
            "strict_stem_physical_page": strict_page,
            "frozen_legacy_statement": frozen_statement_stats,
            "label_any_final_physical_page": label_any_page,
            "label_multi_final_physical_page": label_multi_page,
        },
        "result_hash": sha(RESULT), "validator_hash": sha(Path(__file__)),
        "builder_replays": 2, "f84_or_f84r_accessed": False,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(checks)}/{len(checks)}; independent joins/statistics; two byte-identical builder replays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
