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
BASE = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge"
SRC = BASE / "src"
ART = BASE / "artifacts"
LINE_READER = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
LABEL_ATLAS = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
TRANSITIONS = ROOT / "experiments/yolo/gdt799_f70_f71_f72_homolog_clothing_transition/artifacts/GDT799_9_FIXED_HOMOLOG_TRANSITIONS.tsv"
OCCURRENCES = ART / "GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
STEMS = ART / "GDT800_155_MATCHED_STEM_SUMMARY.tsv"
HOMOLOGS = ART / "GDT800_156_HOMOLOG_PAIR_CENSUS.tsv"
LABELS = ART / "GDT800_27_LABEL_TERMINAL_ATLAS.tsv"
CROSS_REGISTER = ART / "GDT800_4_CROSS_REGISTER_STEM_CARDS.tsv"
POSITION_TESTS = ART / "GDT800_POSITION_TESTS.tsv"
STRATIFIED = ART / "GDT800_STRATIFIED_RESULTS.tsv"
CANDIDATES = ART / "GDT800_CANDIDATE_ADJUDICATION.tsv"
STRUCTURAL_CARD = ART / "GDT800_STRUCTURAL_CARD.tsv"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
REPORT = BASE / "REPORT.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truth(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"not a serialized boolean: {value!r}")


def close(left: float, right: float, rel_tol: float = 2e-9) -> bool:
    return math.isclose(left, right, rel_tol=rel_tol, abs_tol=1e-250)


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def terminal_member(sequence: str) -> str:
    return sequence.split("|")[-1].split(".")[-1]


def tables(
    rows: Iterable[dict[str, str]],
    strata: Sequence[str],
    positive: Callable[[dict[str, str]], bool],
) -> list[tuple[int, int, int, int]]:
    cells: dict[tuple[str, ...], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        cell = cells[tuple(row[field] for field in strata)]
        is_positive = positive(row)
        if row["terminal"] == "m":
            cell[0 if is_positive else 1] += 1
        else:
            cell[2 if is_positive else 3] += 1
    return [tuple(cell) for cell in cells.values()]


def mh_or(cells: Iterable[tuple[int, int, int, int]]) -> tuple[float, int]:
    numerator = 0.0
    denominator = 0.0
    informative = 0
    for a, b, c, d in cells:
        n = a + b + c + d
        if not n or not (a + b) or not (c + d) or not (a + c) or not (b + d):
            continue
        informative += 1
        numerator += a * d / n
        denominator += b * c / n
    return (numerator / denominator if denominator else math.inf), informative


def conditional_upper(cells: Iterable[tuple[int, int, int, int]]) -> float:
    """Independent fixed-margin convolution using integer combinations."""
    distribution: dict[int, float] = {0: 1.0}
    observed = 0
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
        low = max(0, m_total - negative_total)
        high = min(m_total, positive_total)
        denominator = math.comb(n, m_total)
        local = {
            k: math.comb(positive_total, k) * math.comb(negative_total, m_total - k) / denominator
            for k in range(low, high + 1)
        }
        next_distribution: dict[int, float] = defaultdict(float)
        for old_k, old_p in distribution.items():
            for new_k, new_p in local.items():
                next_distribution[old_k + new_k] += old_p * new_p
        distribution = dict(next_distribution)
    if not informative:
        return 1.0
    return min(1.0, sum(probability for successes, probability in distribution.items() if successes >= observed))


def main() -> int:
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    unhashed = dict(result)
    content_hash = unhashed.pop("content_hash")
    check(
        "result_content_hash",
        content_hash == hashlib.sha256(json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    )
    for category in ("inputs", "outputs", "implementation"):
        for path, digest in result[category].items():
            check(f"{category}_hash:{path}", sha(ROOT / path) == digest)

    schemas = {
        OCCURRENCES: ["occurrence_id", "page", "locus", "section", "language", "hand", "token_index", "token_count", "surface", "stem", "terminal", "distance_from_end", "position_class", "any_line_final", "multi_line_final", "single_token_line", "semantic_ceiling"],
        STEMS: ["stem", "l_surface", "m_surface", "l_occurrences", "m_occurrences", "l_pages", "m_pages", "l_multi_line_final", "m_multi_line_final", "l_final_rate", "m_final_rate", "m_minus_l_rate", "direction", "raw_odds_ratio", "one_sided_exact_p", "both_endings_at_least_5", "semantic_ceiling"],
        HOMOLOGS: ["pair_id", "kluge_a_member", "left_template", "right_template", "left_array", "right_array", "left_folio", "right_folio", "left_locus", "right_locus", "left_surface", "right_surface", "surface_edit_distance", "compact_edit_distance", "same_boundary_family", "same_zl_member_sequence", "cross_physical_folio", "terminal_lm_same_stem", "a09_holdout", "semantic_ceiling"],
        LABELS: ["label_terminal_id", "physical_folio", "source_selector", "array_id", "locus", "slot_index", "slot_count", "kluge_a_member", "complete_label_surface", "normalized_stem", "eva_terminal", "source_terminal_member", "zl_terminal_member", "it_terminal_member", "rf_terminal_member", "terminal_member_support", "terminal_member_agreement", "canonical_boundary_family", "same_array_opposition", "paired_label_stem", "semantic_ceiling"],
        CROSS_REGISTER: ["normalized_stem", "label_l_surfaces", "label_m_surfaces", "label_l_loci", "label_m_loci", "same_array_label_opposition", "running_l_occurrences", "running_m_occurrences", "running_l_multi_line_final", "running_m_multi_line_final", "running_l_pages", "running_m_pages", "bridge_reading", "component_export_credit"],
        POSITION_TESTS: ["test_id", "scope", "m_n", "m_positive", "l_n", "l_positive", "odds_ratio", "exact_upper_p", "result"],
        STRATIFIED: ["analysis", "held_or_value", "m_n", "m_final", "l_n", "l_final", "informative_strata", "mh_odds_ratio", "exact_upper_p", "decision"],
        CANDIDATES: ["candidate_id", "candidate", "decision", "evidence", "counterevidence", "confidence", "component_export_credit", "confirmed_lexeme"],
        STRUCTURAL_CARD: ["card_id", "scope", "structural_tag", "german_display", "confidence", "positive_evidence", "counterevidence", "equivalence_license", "semantic_export", "plaintext_value"],
    }
    expected_builder_outputs = {path.relative_to(ROOT).as_posix() for path in schemas} | {REPORT.relative_to(ROOT).as_posix()}
    check("result_output_set_exact", set(result["outputs"]) == expected_builder_outputs)
    for path, schema in schemas.items():
        rows = read_tsv(path)
        check(f"schema:{path.name}", tsv_header(path) == schema)
        check(f"no_blank_cells:{path.name}", all(all(row[field] != "" for field in schema) for row in rows))

    source_lock = read_tsv(SRC / "SOURCE_LOCK.tsv")
    native = read_tsv(SRC / "NATIVE_A09_GLYPH_AUDIT.tsv")
    model_specs = read_tsv(SRC / "CANDIDATE_MODEL_SPECS.tsv")
    check("four_source_locks", len(source_lock) == 4)
    check("source_locks_match", all(sha(ROOT / row["path"]) == row["sha256"] for row in source_lock))
    check("source_paths_relative", all(not Path(row["path"]).is_absolute() for row in source_lock))
    check("sealed_absent_from_locks", all("f84" not in row["path"].lower() for row in source_lock))
    check("two_native_audits", len(native) == 2 and {row["locus"] for row in native} == {"f70v1.5", "f72r1.5"})
    check("native_members", {(row["surface"], row["final_member"]) for row in native} == {("okalal", "B2"), ("okalam", "B3")})
    check("native_hashes_frozen", all(len(row["canvas_sha256"]) == len(row["crop_sha256"]) == 64 for row in native))
    local_prefixes = (chr(47) + "home" + chr(47), chr(47) + "tmp" + chr(47))
    check("native_no_local_paths", all(not any(prefix in "|".join(row.values()) for prefix in local_prefixes) for row in native))
    check("six_candidate_specs", len(model_specs) == 6 and {row["candidate_id"] for row in model_specs} == {f"C{i}" for i in range(1, 7)})

    line_rows = read_tsv(LINE_READER)
    check("line_reader_count", len(line_rows) == 4128)
    check("line_reader_sealed_absent", all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in line_rows))
    all_terminal: list[dict[str, Any]] = []
    token_total = 0
    for line in line_rows:
        tokens = line["zl3b_line"].split()
        check(f"line_token_count:{line['locus']}", len(tokens) == int(line["token_count"]))
        token_total += len(tokens)
        for token_index, surface in enumerate(tokens, 1):
            if surface.endswith(("l", "m")):
                all_terminal.append(
                    {
                        "page": line["page"], "locus": line["locus"], "section": line["section"],
                        "language": line["language"], "hand": line["hand"], "token_index": token_index,
                        "token_count": len(tokens), "surface": surface, "stem": surface[:-1],
                        "terminal": surface[-1], "distance_from_end": len(tokens) - token_index,
                    }
                )
    ending_sets: dict[str, set[str]] = defaultdict(set)
    for row in all_terminal:
        ending_sets[row["stem"]].add(row["terminal"])
    empty_prefix_events = sum(row["stem"] == "" for row in all_terminal)
    paired_stems = {stem for stem, endings in ending_sets.items() if stem and endings == {"l", "m"}}
    expected_occ = {
        (row["page"], row["locus"], row["token_index"]): row
        for row in all_terminal if row["stem"] in paired_stems
    }
    occurrence_rows = read_tsv(OCCURRENCES)
    check("token_total", token_total == 32339)
    check("all_terminal_total", len(all_terminal) == 5767)
    check("empty_prefix_events_excluded", empty_prefix_events == 169)
    check("paired_stem_total", len(paired_stems) == 155 and "" not in paired_stems)
    check("paired_occurrence_total", len(occurrence_rows) == len(expected_occ) == 4137)
    check("occurrence_ids_unique", len({row["occurrence_id"] for row in occurrence_rows}) == 4137)
    check("occurrence_stems_nonempty", all(row["stem"] for row in occurrence_rows))
    observed_occ_keys = {(row["page"], row["locus"], int(row["token_index"])) for row in occurrence_rows}
    check("occurrence_keys_exact", observed_occ_keys == set(expected_occ))
    for row in occurrence_rows:
        key = (row["page"], row["locus"], int(row["token_index"]))
        expected = expected_occ[key]
        check(f"occ_surface:{row['occurrence_id']}", row["surface"] == expected["surface"] == row["stem"] + row["terminal"])
        check(f"occ_context:{row['occurrence_id']}", all(row[field] == expected[field] for field in ("page", "locus", "section", "language", "hand", "stem", "terminal")))
        check(f"occ_position:{row['occurrence_id']}", int(row["token_count"]) == expected["token_count"] and int(row["distance_from_end"]) == expected["distance_from_end"])
        expected_final = expected["distance_from_end"] == 0
        expected_single = expected["token_count"] == 1
        check(f"occ_flags:{row['occurrence_id']}", truth(row["any_line_final"]) == expected_final and truth(row["single_token_line"]) == expected_single and truth(row["multi_line_final"]) == (expected_final and not expected_single))
        expected_class = "SINGLE" if expected_single else "FINAL" if expected_final else "FIRST" if expected["token_index"] == 1 else "INTERNAL"
        check(f"occ_class:{row['occurrence_id']}", row["position_class"] == expected_class)

    occurrence_by_stem: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrence_rows:
        occurrence_by_stem[row["stem"]].append(row)
    stem_rows = read_tsv(STEMS)
    check("stem_summary_total", len(stem_rows) == 155 and {row["stem"] for row in stem_rows} == paired_stems)
    check("stem_summary_nonempty", all(row["stem"] for row in stem_rows))
    for row in stem_rows:
        events = occurrence_by_stem[row["stem"]]
        l_events = [event for event in events if event["terminal"] == "l"]
        m_events = [event for event in events if event["terminal"] == "m"]
        l_final = sum(truth(event["multi_line_final"]) for event in l_events)
        m_final = sum(truth(event["multi_line_final"]) for event in m_events)
        l_rate = l_final / len(l_events)
        m_rate = m_final / len(m_events)
        check(f"stem_surfaces:{row['stem']}", row["l_surface"] == row["stem"] + "l" and row["m_surface"] == row["stem"] + "m")
        check(f"stem_counts:{row['stem']}", (int(row["l_occurrences"]), int(row["m_occurrences"]), int(row["l_multi_line_final"]), int(row["m_multi_line_final"])) == (len(l_events), len(m_events), l_final, m_final))
        check(f"stem_pages:{row['stem']}", int(row["l_pages"]) == len({event["page"] for event in l_events}) and int(row["m_pages"]) == len({event["page"] for event in m_events}))
        check(f"stem_rates:{row['stem']}", close(float(row["l_final_rate"]), l_rate) and close(float(row["m_final_rate"]), m_rate) and close(float(row["m_minus_l_rate"]), m_rate - l_rate))
        direction = "M_HIGHER" if m_rate > l_rate else "L_HIGHER" if l_rate > m_rate else "TIE"
        check(f"stem_direction:{row['stem']}", row["direction"] == direction)

    paired_counts = Counter(row["terminal"] for row in occurrence_rows)
    paired_finals = Counter(row["terminal"] for row in occurrence_rows if truth(row["multi_line_final"]))
    all_counts = Counter(row["terminal"] for row in all_terminal)
    all_finals = Counter(row["terminal"] for row in all_terminal if row["distance_from_end"] == 0)
    check("paired_counts", paired_counts == Counter({"l": 3484, "m": 653}))
    check("paired_final_counts", paired_finals == Counter({"m": 450, "l": 310}))
    check("all_counts", all_counts == Counter({"l": 4929, "m": 838}))
    check("all_final_counts", all_finals == Counter({"m": 591, "l": 482}))

    stem_cells = tables(occurrence_rows, ["stem"], lambda row: truth(row["multi_line_final"]))
    multitoken_cells = tables(
        (row for row in occurrence_rows if not truth(row["single_token_line"])),
        ["stem"], lambda row: truth(row["multi_line_final"]),
    )
    meta_cells = tables(occurrence_rows, ["stem", "section", "language", "hand"], lambda row: truth(row["multi_line_final"]))
    page_cells = tables(occurrence_rows, ["stem", "page"], lambda row: truth(row["multi_line_final"]))
    independently_computed: dict[str, tuple[float, int, float]] = {}
    for name, cells in (("stem", stem_cells), ("stem_multitoken_only", multitoken_cells), ("stem_section_language_hand", meta_cells), ("stem_page", page_cells)):
        odds_ratio, informative = mh_or(cells)
        p_value = conditional_upper(cells)
        independently_computed[name] = (odds_ratio, informative, p_value)
        saved = result["primary_tests"][name]
        check(f"{name}_strata", len(cells) == saved["strata"] and informative == saved["informative_strata"])
        check(f"{name}_mh_or", close(odds_ratio, saved["odds_ratio"]))
        check(f"{name}_exact_p", close(p_value, saved["exact_upper_p"], rel_tol=3e-8))

    label_source = read_tsv(LABEL_ATLAS)
    label_rows = read_tsv(LABELS)
    check("label_source_total", len(label_source) == 101)
    check("label_source_sealed_absent", all(not row["physical_folio"].startswith("f84") for row in label_source))
    source_by_locus = {row["locus"]: row for row in label_source}
    check("terminal_label_total", len(label_rows) == 27 and Counter(row["source_terminal_member"] for row in label_rows) == Counter({"B3": 15, "B2": 12}))
    check("terminal_label_keys_unique", len({row["label_terminal_id"] for row in label_rows}) == len({row["locus"] for row in label_rows}) == 27)
    for row in label_rows:
        source = source_by_locus[row["locus"]]
        compact = source["complete_label_surface"].replace(" ", "")
        ending = compact[-1]
        expected_member = "B2" if ending == "l" else "B3"
        members = [terminal_member(source[f"{reader}_member_sequence"]) for reader in ("zl", "it", "rf")]
        support = sum(member == expected_member for member in members)
        check(f"label_binding:{row['locus']}", row["complete_label_surface"] == source["complete_label_surface"] and row["normalized_stem"] == compact[:-1] and row["eva_terminal"] == ending)
        check(f"label_members:{row['locus']}", row["source_terminal_member"] == expected_member and [row["zl_terminal_member"], row["it_terminal_member"], row["rf_terminal_member"]] == members)
        check(f"label_support:{row['locus']}", int(row["terminal_member_support"]) == support and row["terminal_member_agreement"] == ("ALL3" if support == 3 else "TWO_OF_THREE"))
        check(f"label_context:{row['locus']}", all(row[field] == source[field] for field in ("physical_folio", "source_selector", "array_id", "slot_index", "slot_count", "kluge_a_member", "canonical_boundary_family")))

    homolog_rows = read_tsv(HOMOLOGS)
    expected_pairs: set[frozenset[str]] = set()
    for left, right in itertools.combinations(label_source, 2):
        if left["kluge_a_member"] == right["kluge_a_member"] and left["array_id"] != right["array_id"]:
            expected_pairs.add(frozenset((left["locus"], right["locus"])))
    observed_pairs = {frozenset((row["left_locus"], row["right_locus"])) for row in homolog_rows}
    check("homolog_total", len(homolog_rows) == len(expected_pairs) == 156)
    check("homolog_pairs_exact", observed_pairs == expected_pairs)
    check("homolog_ids_unique", len({row["pair_id"] for row in homolog_rows}) == 156)
    for row in homolog_rows:
        left = source_by_locus[row["left_locus"]]
        right = source_by_locus[row["right_locus"]]
        left_surface = left["complete_label_surface"]
        right_surface = right["complete_label_surface"]
        left_compact = left_surface.replace(" ", "")
        right_compact = right_surface.replace(" ", "")
        terminal_lm = len(left_compact) == len(right_compact) and left_compact[:-1] == right_compact[:-1] and {left_compact[-1:], right_compact[-1:]} == {"l", "m"}
        check(f"homolog_member:{row['pair_id']}", left["kluge_a_member"] == right["kluge_a_member"] == row["kluge_a_member"] and left["array_id"] != right["array_id"])
        check(f"homolog_surfaces:{row['pair_id']}", row["left_surface"] == left_surface and row["right_surface"] == right_surface)
        check(f"homolog_distances:{row['pair_id']}", int(row["surface_edit_distance"]) == levenshtein(left_surface, right_surface) and int(row["compact_edit_distance"]) == levenshtein(left_compact, right_compact))
        check(f"homolog_features:{row['pair_id']}", int(row["same_boundary_family"]) == (left["canonical_boundary_family"] == right["canonical_boundary_family"]) and int(row["same_zl_member_sequence"]) == (left["zl_member_sequence"] == right["zl_member_sequence"]) and int(row["cross_physical_folio"]) == (left["physical_folio"] != right["physical_folio"]) and int(row["terminal_lm_same_stem"]) == terminal_lm)
    check("homolog_distance_one", sum(int(row["compact_edit_distance"]) == 1 for row in homolog_rows) == 2)
    check("homolog_same_family", sum(int(row["same_boundary_family"]) for row in homolog_rows) == 2)
    check("homolog_cross_folio", sum(int(row["cross_physical_folio"]) for row in homolog_rows) == 128)
    check("a09_only_terminal_homolog", [(row["left_locus"], row["right_locus"]) for row in homolog_rows if row["terminal_lm_same_stem"] == "1"] == [("f70v1.5", "f72r1.5")])
    check("a09_holdout_only", sum(row["a09_holdout"] == "1" for row in homolog_rows) == 1)

    cross_rows = read_tsv(CROSS_REGISTER)
    check("cross_register_stems", [row["normalized_stem"] for row in cross_rows] == ["oka", "okala", "ota", "otara"])
    check("cross_register_keys_unique", len({row["normalized_stem"] for row in cross_rows}) == 4)
    for row in cross_rows:
        stem = row["normalized_stem"]
        events = occurrence_by_stem[stem]
        check(f"cross_running_counts:{stem}", int(row["running_l_occurrences"]) == sum(event["terminal"] == "l" for event in events) and int(row["running_m_occurrences"]) == sum(event["terminal"] == "m" for event in events))
        check(f"cross_running_finals:{stem}", int(row["running_l_multi_line_final"]) == sum(event["terminal"] == "l" and truth(event["multi_line_final"]) for event in events) and int(row["running_m_multi_line_final"]) == sum(event["terminal"] == "m" and truth(event["multi_line_final"]) for event in events))
    check("same_array_oppositions", {row["normalized_stem"] for row in cross_rows if row["same_array_label_opposition"] == "1"} == {"ota", "otara"})

    test_rows = read_tsv(POSITION_TESTS)
    test_by_id = {row["test_id"]: row for row in test_rows}
    check("ten_position_tests", len(test_rows) == len(test_by_id) == 10)
    check("raw_test_counts", (test_by_id["PAIRED_STEM_MULTI_LINE_RAW"]["m_n"], test_by_id["PAIRED_STEM_MULTI_LINE_RAW"]["m_positive"], test_by_id["PAIRED_STEM_MULTI_LINE_RAW"]["l_n"], test_by_id["PAIRED_STEM_MULTI_LINE_RAW"]["l_positive"]) == ("653", "450", "3484", "310"))
    for test_id, key in (("PAIRED_STEM_CONDITIONAL", "stem"), ("STEM_CONDITIONAL_MULTITOKEN_ONLY", "stem_multitoken_only"), ("STEM_SECTION_LANGUAGE_HAND_CONDITIONAL", "stem_section_language_hand"), ("STEM_PAGE_CONDITIONAL", "stem_page")):
        saved = test_by_id[test_id]
        odds_ratio, _, p_value = independently_computed[key]
        check(f"position_or:{test_id}", close(float(saved["odds_ratio"]), odds_ratio))
        check(f"position_p:{test_id}", close(float(saved["exact_upper_p"]), p_value, rel_tol=3e-8))
    check("gradient_tests", test_by_id["LAST_VS_PENULTIMATE"]["result"] == "BOUNDARY_GRADIENT" and float(test_by_id["LAST_VS_PENULTIMATE"]["odds_ratio"]) > 8 and test_by_id["PENULTIMATE_VS_EARLIER"]["result"] == "PREBOUNDARY_GRADIENT" and float(test_by_id["PENULTIMATE_VS_EARLIER"]["odds_ratio"]) > 2)
    check("singleton_sensitivity", sum(truth(row["single_token_line"]) for row in occurrence_rows) == 26 and test_by_id["STEM_CONDITIONAL_MULTITOKEN_ONLY"]["result"] == "SENSITIVITY_RETAINS")

    stratified_rows = read_tsv(STRATIFIED)
    check("nineteen_stratified_rows", len(stratified_rows) == 19)
    check("stratified_inventory", Counter(row["analysis"] for row in stratified_rows) == Counter({"SECTION": 6, "LANGUAGE": 2, "HAND": 5, "LEAVE_ONE_SECTION_OUT": 6}))
    check("stratified_keys_unique", len({(row["analysis"], row["held_or_value"]) for row in stratified_rows}) == 19)
    stratified_by_key = {(row["analysis"], row["held_or_value"]): row for row in stratified_rows}
    independently_passing_leaveouts = []
    for held in sorted({row["section"] for row in occurrence_rows}):
        subset = [row for row in occurrence_rows if row["section"] != held]
        check(f"leaveout_complement:{held}", subset and all(row["section"] != held for row in subset))
        cells = tables(subset, ["stem", "section", "language", "hand"], lambda row: truth(row["multi_line_final"]))
        odds_ratio, informative = mh_or(cells)
        p_value = conditional_upper(cells)
        counts = Counter(row["terminal"] for row in subset)
        finals = Counter(row["terminal"] for row in subset if truth(row["multi_line_final"]))
        saved = stratified_by_key[("LEAVE_ONE_SECTION_OUT", held)]
        check(f"leaveout_counts:{held}", (int(saved["m_n"]), int(saved["m_final"]), int(saved["l_n"]), int(saved["l_final"])) == (counts["m"], finals["m"], counts["l"], finals["l"]))
        check(f"leaveout_informative:{held}", int(saved["informative_strata"]) == informative)
        check(f"leaveout_or:{held}", close(float(saved["mh_odds_ratio"]), odds_ratio))
        check(f"leaveout_p:{held}", close(float(saved["exact_upper_p"]), p_value, rel_tol=3e-8))
        passed = odds_ratio > 3 and p_value < .01
        independently_passing_leaveouts.append(passed)
        check(f"leaveout_decision:{held}", saved["decision"] == ("PASS" if passed else "FAIL"))
    check("leaveout_all_pass", all(row["decision"] == "PASS" for row in stratified_rows if row["analysis"] == "LEAVE_ONE_SECTION_OUT"))
    check("leaveout_result_gate", all(independently_passing_leaveouts) == result["primary_tests"]["leave_one_section_out_all_pass"])
    check("section_counts_partition", sum(int(row["m_n"]) for row in stratified_rows if row["analysis"] == "SECTION") == 653 and sum(int(row["l_n"]) for row in stratified_rows if row["analysis"] == "SECTION") == 3484)

    candidate_rows = read_tsv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    check("six_candidate_rows", len(candidate_rows) == len(candidate_by_id) == 6)
    check("boundary_field_selected", candidate_by_id["C1"]["decision"] == "SELECT_STRUCTURAL")
    check("deterministic_allograph_rejected", candidate_by_id["C2"]["decision"] == "REJECT_DETERMINISTIC")
    check("semantic_suffix_not_selected", candidate_by_id["C3"]["decision"] == "HOLD_NO_INDEPENDENT_STATE_GAIN")
    check("page_only_rejected", candidate_by_id["C4"]["decision"] == "REJECT_PAGE_ONLY")
    check("clothing_rejected", candidate_by_id["C5"]["decision"] == "REJECT_PORTABLE")
    check("zero_confirmed_candidate_lexemes", all(row["confirmed_lexeme"] == "NO" for row in candidate_rows))

    card_rows = read_tsv(STRUCTURAL_CARD)
    check("one_structural_card", len(card_rows) == 1)
    card = card_rows[0]
    check("structural_not_semantic", card["structural_tag"] == "BOUNDARY_FAVOURED_TERMINAL_SURFACE" and card["semantic_export"] == "ZERO" and card["plaintext_value"] == "UNKNOWN")
    check("no_equivalence_license", card["equivalence_license"] == "NONE__DO_NOT_NORMALIZE_M_TO_L")

    transition_rows = read_tsv(TRANSITIONS)
    a09 = next(row for row in transition_rows if row["a_member"] == "9")
    check("a09_visual_binding", a09["f70_locus"] == "f70v1.5" and a09["f72_locus"] == "f72r1.5" and a09["f70_state"] == "TORSO_COVERED" and a09["f72_state"] == "TORSO_UNCOVERED")
    check("result_status", result["status"] == "PARTIAL__155_NONEMPTY_PAIRED_STEMS__BOUNDARY_FIELD_SELECTED__OBLIGATORY_ALLOGRAPH_REJECTED__A09_DIRECTION_OPEN__ZERO_LEXEMES")
    check("result_decision", result["decision"] == "LEARNED_WHOLE_OR_STEM_PLUS_BOUNDARY_FAVOURED_TERMINAL_FIELD")
    check("result_counts", result["running_cache"]["paired_stems"] == 155 and result["running_cache"]["paired_occurrences"] == 4137 and result["running_cache"]["empty_prefix_events_excluded_from_stem_model"] == 169 and result["labels"]["terminal_b2_b3"] == 27 and result["labels"]["homolog_terminal_lm"] == 1)
    check("result_zero_semantics", result["semantic_exports"] == result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == 0)
    check("result_sealed_absent", result["f84_or_f84r_accessed"] is False)
    report = REPORT.read_text(encoding="utf-8")
    report_flat = " ".join(report.split())
    check("report_counts", "**450/653**" in report and "**310/3484**" in report and "**203** paired nonfinal `m`" in report and "**169**" in report)
    check("report_a09", "f70 A09  okala + B2-terminal" in report and "f72 A09  okala + B3-terminal" in report)
    check("report_no_translation_claim", "Neither line says" in report_flat and "not a word translation" in report_flat)

    replay_paths = [OCCURRENCES, STEMS, HOMOLOGS, LABELS, CROSS_REGISTER, POSITION_TESTS, STRATIFIED, CANDIDATES, STRUCTURAL_CARD, REPORT, RESULT]
    before = {str(path): sha(path) for path in replay_paths}
    command = ["python3", str(SRC / "run.py")]
    first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    after_first = {str(path): sha(path) for path in replay_paths}
    second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    after_second = {str(path): sha(path) for path in replay_paths}
    check("builder_replay_one", before == after_first)
    check("builder_replay_two", after_first == after_second)
    check("builder_status_stdout", result["status"] in first.stdout and result["status"] in second.stdout)

    validation: dict[str, Any] = {
        "schema": "GDT800_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "independent_statistics": {
            key: {"odds_ratio": value[0], "informative_strata": value[1], "exact_upper_p": value[2]}
            for key, value in independently_computed.items()
        },
        "result_hash": sha(RESULT),
        "validator_hash": sha(Path(__file__)),
        "builder_replays": 2,
        "f84_or_f84r_accessed": False,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(checks)}/{len(checks)}; independent fixed-margin statistics; two byte-identical builder replays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
