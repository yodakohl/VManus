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
EXP = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge"
SRC = EXP / "src"
ART = EXP / "artifacts"
LINE_READER = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
LABEL_ATLAS = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
TRANSITIONS = ROOT / "experiments/yolo/gdt799_f70_f71_f72_homolog_clothing_transition/artifacts/GDT799_9_FIXED_HOMOLOG_TRANSITIONS.tsv"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
NATIVE_AUDIT = SRC / "NATIVE_A09_GLYPH_AUDIT.tsv"
MODEL_SPECS = SRC / "CANDIDATE_MODEL_SPECS.tsv"

OCCURRENCES = ART / "GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
STEMS = ART / "GDT800_155_MATCHED_STEM_SUMMARY.tsv"
HOMOLOGS = ART / "GDT800_156_HOMOLOG_PAIR_CENSUS.tsv"
LABEL_TERMINALS = ART / "GDT800_27_LABEL_TERMINAL_ATLAS.tsv"
CROSS_REGISTER = ART / "GDT800_4_CROSS_REGISTER_STEM_CARDS.tsv"
POSITION_TESTS = ART / "GDT800_POSITION_TESTS.tsv"
STRATIFIED = ART / "GDT800_STRATIFIED_RESULTS.tsv"
CANDIDATES = ART / "GDT800_CANDIDATE_ADJUDICATION.tsv"
STRUCTURAL_CARD = ART / "GDT800_STRUCTURAL_CARD.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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


def f12(value: float) -> str:
    if math.isinf(value):
        return "INF"
    return f"{value:.12g}"


def rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def last_member(sequence: str) -> str:
    return sequence.split("|")[-1].split(".")[-1]


def levenshtein(left: str, right: str) -> int:
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        nxt = [i]
        for j, b in enumerate(right, 1):
            nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = nxt
    return row[-1]


def log_choose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hypergeom_distribution(n: int, final_total: int, m_total: int) -> list[tuple[int, float]]:
    lo = max(0, m_total - (n - final_total))
    hi = min(m_total, final_total)
    logs = [
        log_choose(final_total, k)
        + log_choose(n - final_total, m_total - k)
        - log_choose(n, m_total)
        for k in range(lo, hi + 1)
    ]
    peak = max(logs)
    weights = [math.exp(value - peak) for value in logs]
    total = sum(weights)
    return [(lo + i, value / total) for i, value in enumerate(weights)]


def exact_conditional_upper(tables: Iterable[tuple[int, int, int, int]]) -> float:
    distribution = [1.0]
    observed = 0
    informative = 0
    for a, b, c, d in tables:
        n = a + b + c + d
        m_total = a + b
        l_total = c + d
        final_total = a + c
        nonfinal_total = b + d
        if not (m_total and l_total and final_total and nonfinal_total):
            continue
        informative += 1
        observed += a
        local = hypergeom_distribution(n, final_total, m_total)
        nxt = [0.0] * (len(distribution) + local[-1][0])
        for i, p_left in enumerate(distribution):
            if not p_left:
                continue
            for k, p_right in local:
                nxt[i + k] += p_left * p_right
        distribution = nxt
    if not informative:
        return 1.0
    return min(1.0, sum(distribution[observed:]))


def build_tables(
    rows: Sequence[dict[str, Any]],
    strata: Sequence[str],
    final_fn: Callable[[dict[str, Any]], bool],
) -> list[tuple[int, int, int, int]]:
    cells: dict[tuple[Any, ...], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for row in rows:
        key = tuple(row[field] for field in strata)
        is_final = final_fn(row)
        if row["terminal"] == "m":
            cells[key][0 if is_final else 1] += 1
        else:
            cells[key][2 if is_final else 3] += 1
    return [tuple(values) for values in cells.values()]


def mh_result(
    rows: Sequence[dict[str, Any]],
    strata: Sequence[str],
    final_fn: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    tables = build_tables(rows, strata, final_fn)
    numerator = 0.0
    denominator = 0.0
    informative = 0
    for a, b, c, d in tables:
        n = a + b + c + d
        if not n or not (a + b) or not (c + d) or not (a + c) or not (b + d):
            continue
        informative += 1
        numerator += a * d / n
        denominator += b * c / n
    odds_ratio = numerator / denominator if denominator else (float("inf") if numerator else 0.0)
    return {
        "strata": len(tables),
        "informative_strata": informative,
        "odds_ratio": odds_ratio,
        "exact_upper_p": exact_conditional_upper(tables),
    }


def binomial_upper(successes: int, trials: int) -> float:
    return sum(math.comb(trials, k) for k in range(successes, trials + 1)) / (2**trials)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    for lock in read_tsv(SOURCE_LOCK):
        path = ROOT / lock["path"]
        if sha(path) != lock["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {lock['path']}")

    line_rows = read_tsv(LINE_READER)
    if len(line_rows) != 4128:
        raise RuntimeError(f"unexpected line count: {len(line_rows)}")
    if any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in line_rows):
        raise RuntimeError("sealed f84/f84r selector reached materialization")

    all_terminal: list[dict[str, Any]] = []
    total_tokens = 0
    for line in line_rows:
        tokens = line["zl3b_line"].split()
        if len(tokens) != int(line["token_count"]):
            raise RuntimeError(f"token-count mismatch at {line['locus']}")
        total_tokens += len(tokens)
        for index, surface in enumerate(tokens, 1):
            if not surface.endswith(("l", "m")):
                continue
            all_terminal.append(
                {
                    "page": line["page"], "locus": line["locus"],
                    "section": line["section"], "language": line["language"],
                    "hand": line["hand"], "token_index": index,
                    "token_count": len(tokens), "surface": surface,
                    "stem": surface[:-1], "terminal": surface[-1],
                    "distance_from_end": len(tokens) - index,
                    "any_line_final": index == len(tokens),
                    "multi_line_final": len(tokens) > 1 and index == len(tokens),
                    "single_token_line": len(tokens) == 1,
                }
            )

    endings_by_stem: dict[str, set[str]] = defaultdict(set)
    for row in all_terminal:
        endings_by_stem[row["stem"]].add(row["terminal"])
    empty_prefix_events = sum(row["stem"] == "" for row in all_terminal)
    paired_stems = {stem for stem, endings in endings_by_stem.items() if stem and endings == {"l", "m"}}
    paired_occ = [row for row in all_terminal if row["stem"] in paired_stems]
    paired_occ.sort(key=lambda row: (row["page"], row["locus"], row["token_index"]))
    for ordinal, row in enumerate(paired_occ, 1):
        row["occurrence_id"] = f"GDT800-O{ordinal:04d}"
        row["position_class"] = (
            "SINGLE" if row["single_token_line"] else
            "FINAL" if row["any_line_final"] else
            "FIRST" if row["token_index"] == 1 else "INTERNAL"
        )
        row["semantic_ceiling"] = "FORMAL_TERMINAL_OCCURRENCE__NO_MEANING"

    if total_tokens != 32339 or len(all_terminal) != 5767 or empty_prefix_events != 169 or len(paired_stems) != 155 or len(paired_occ) != 4137:
        raise RuntimeError(
            f"unexpected census: tokens={total_tokens} terminal={len(all_terminal)} "
            f"stems={len(paired_stems)} paired={len(paired_occ)}"
        )
    occurrence_fields = [
        "occurrence_id", "page", "locus", "section", "language", "hand",
        "token_index", "token_count", "surface", "stem", "terminal",
        "distance_from_end", "position_class", "any_line_final",
        "multi_line_final", "single_token_line", "semantic_ceiling",
    ]
    write_tsv(OCCURRENCES, paired_occ, occurrence_fields)

    grouped_occ: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in paired_occ:
        grouped_occ[row["stem"]].append(row)
    stem_rows: list[dict[str, Any]] = []
    for stem, rows in grouped_occ.items():
        l_rows = [row for row in rows if row["terminal"] == "l"]
        m_rows = [row for row in rows if row["terminal"] == "m"]
        l_final = sum(row["multi_line_final"] for row in l_rows)
        m_final = sum(row["multi_line_final"] for row in m_rows)
        l_rate = rate(l_final, len(l_rows))
        m_rate = rate(m_final, len(m_rows))
        one = mh_result(rows, ["stem"], lambda row: bool(row["multi_line_final"]))
        stem_rows.append(
            {
                "stem": stem, "l_surface": stem + "l", "m_surface": stem + "m",
                "l_occurrences": len(l_rows), "m_occurrences": len(m_rows),
                "l_pages": len({row["page"] for row in l_rows}),
                "m_pages": len({row["page"] for row in m_rows}),
                "l_multi_line_final": l_final, "m_multi_line_final": m_final,
                "l_final_rate": f12(l_rate), "m_final_rate": f12(m_rate),
                "m_minus_l_rate": f12(m_rate - l_rate),
                "direction": "M_HIGHER" if m_rate > l_rate else "L_HIGHER" if l_rate > m_rate else "TIE",
                "raw_odds_ratio": f12(one["odds_ratio"]),
                "one_sided_exact_p": f12(one["exact_upper_p"]),
                "both_endings_at_least_5": int(len(l_rows) >= 5 and len(m_rows) >= 5),
                "semantic_ceiling": "EXACT_SURFACE_PAIR__NO_EQUIVALENCE_OR_MEANING",
            }
        )
    stem_rows.sort(key=lambda row: (-(row["l_occurrences"] + row["m_occurrences"]), row["stem"]))
    write_tsv(STEMS, stem_rows, list(stem_rows[0]))

    label_rows = read_tsv(LABEL_ATLAS)
    if len(label_rows) != 101 or any(row["physical_folio"].startswith("f84") for row in label_rows):
        raise RuntimeError("unexpected or sealed label atlas")
    homolog_rows: list[dict[str, Any]] = []
    grouped_member: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in label_rows:
        grouped_member[row["kluge_a_member"]].append(row)
    for member in sorted(grouped_member, key=int):
        for left, right in itertools.combinations(grouped_member[member], 2):
            if left["array_id"] == right["array_id"]:
                continue
            if int(left["family_atlas_ordinal"]) > int(right["family_atlas_ordinal"]):
                left, right = right, left
            ls, rs = left["complete_label_surface"], right["complete_label_surface"]
            lc, rc = ls.replace(" ", ""), rs.replace(" ", "")
            is_a09 = {left["locus"], right["locus"]} == {"f70v1.5", "f72r1.5"}
            homolog_rows.append(
                {
                    "pair_id": "", "kluge_a_member": member,
                    "left_template": left["template_id"], "right_template": right["template_id"],
                    "left_array": left["array_id"], "right_array": right["array_id"],
                    "left_folio": left["physical_folio"], "right_folio": right["physical_folio"],
                    "left_locus": left["locus"], "right_locus": right["locus"],
                    "left_surface": ls, "right_surface": rs,
                    "surface_edit_distance": levenshtein(ls, rs),
                    "compact_edit_distance": levenshtein(lc, rc),
                    "same_boundary_family": int(left["canonical_boundary_family"] == right["canonical_boundary_family"]),
                    "same_zl_member_sequence": int(left["zl_member_sequence"] == right["zl_member_sequence"]),
                    "cross_physical_folio": int(left["physical_folio"] != right["physical_folio"]),
                    "terminal_lm_same_stem": int(
                        len(lc) == len(rc) and lc[:-1] == rc[:-1] and {lc[-1:], rc[-1:]} == {"l", "m"}
                    ),
                    "a09_holdout": int(is_a09),
                    "semantic_ceiling": "ANALYST_HOMOLOG_COMPARISON__NO_EDGE_OR_MEANING",
                }
            )
    homolog_rows.sort(key=lambda row: (int(row["kluge_a_member"]), row["left_locus"], row["right_locus"]))
    for ordinal, row in enumerate(homolog_rows, 1):
        row["pair_id"] = f"GDT800-H{ordinal:03d}"
    if len(homolog_rows) != 156:
        raise RuntimeError(f"unexpected homolog count: {len(homolog_rows)}")
    write_tsv(HOMOLOGS, homolog_rows, list(homolog_rows[0]))

    terminal_labels: list[dict[str, Any]] = []
    label_endings: dict[str, set[str]] = defaultdict(set)
    for row in label_rows:
        surface = row["complete_label_surface"]
        compact = surface.replace(" ", "")
        if not compact.endswith(("l", "m")):
            continue
        ending = compact[-1]
        members = [last_member(row[f"{reader}_member_sequence"]) for reader in ("zl", "it", "rf")]
        expected = "B2" if ending == "l" else "B3"
        terminal_support = sum(member == expected for member in members)
        if terminal_support < 2:
            raise RuntimeError(f"terminal source majority failed at {row['locus']}: {members}")
        stem = compact[:-1]
        label_endings[stem].add(ending)
        terminal_labels.append(
            {
                "label_terminal_id": "", "physical_folio": row["physical_folio"],
                "source_selector": row["source_selector"], "array_id": row["array_id"],
                "locus": row["locus"], "slot_index": row["slot_index"],
                "slot_count": row["slot_count"], "kluge_a_member": row["kluge_a_member"],
                "complete_label_surface": surface, "normalized_stem": stem,
                "eva_terminal": ending, "source_terminal_member": expected,
                "zl_terminal_member": members[0], "it_terminal_member": members[1],
                "rf_terminal_member": members[2],
                "terminal_member_support": terminal_support,
                "terminal_member_agreement": "ALL3" if terminal_support == 3 else "TWO_OF_THREE",
                "canonical_boundary_family": row["canonical_boundary_family"],
                "same_array_opposition": 0, "paired_label_stem": 0,
                "semantic_ceiling": "PHYSICAL_TERMINAL_CONTRAST__NO_VALUE",
            }
        )
    for row in terminal_labels:
        row["paired_label_stem"] = int(label_endings[row["normalized_stem"]] == {"l", "m"})
        row["same_array_opposition"] = int(
            any(
                other["array_id"] == row["array_id"]
                and other["normalized_stem"] == row["normalized_stem"]
                and other["eva_terminal"] != row["eva_terminal"]
                for other in terminal_labels
            )
        )
    terminal_labels.sort(key=lambda row: (row["source_selector"], int(row["slot_index"]), row["locus"]))
    for ordinal, row in enumerate(terminal_labels, 1):
        row["label_terminal_id"] = f"GDT800-L{ordinal:02d}"
    if len(terminal_labels) != 27 or Counter(row["source_terminal_member"] for row in terminal_labels) != Counter({"B3": 15, "B2": 12}):
        raise RuntimeError("unexpected terminal label census")
    write_tsv(LABEL_TERMINALS, terminal_labels, list(terminal_labels[0]))

    cross_rows: list[dict[str, Any]] = []
    common_label_stems = sorted(stem for stem, endings in label_endings.items() if endings == {"l", "m"})
    for stem in common_label_stems:
        label_l = [row for row in terminal_labels if row["normalized_stem"] == stem and row["eva_terminal"] == "l"]
        label_m = [row for row in terminal_labels if row["normalized_stem"] == stem and row["eva_terminal"] == "m"]
        run_l = [row for row in paired_occ if row["stem"] == stem and row["terminal"] == "l"]
        run_m = [row for row in paired_occ if row["stem"] == stem and row["terminal"] == "m"]
        cross_rows.append(
            {
                "normalized_stem": stem,
                "label_l_surfaces": "|".join(sorted({row["complete_label_surface"] for row in label_l})),
                "label_m_surfaces": "|".join(sorted({row["complete_label_surface"] for row in label_m})),
                "label_l_loci": "|".join(row["locus"] for row in label_l),
                "label_m_loci": "|".join(row["locus"] for row in label_m),
                "same_array_label_opposition": int(any(row["same_array_opposition"] for row in label_l + label_m)),
                "running_l_occurrences": len(run_l), "running_m_occurrences": len(run_m),
                "running_l_multi_line_final": sum(row["multi_line_final"] for row in run_l),
                "running_m_multi_line_final": sum(row["multi_line_final"] for row in run_m),
                "running_l_pages": len({row["page"] for row in run_l}),
                "running_m_pages": len({row["page"] for row in run_m}),
                "bridge_reading": "RECURRENT_BOUND_TERMINAL_OPPOSITION__SEMANTIC_VALUE_OPEN",
                "component_export_credit": "FORMAL_POSITION_ONLY",
            }
        )
    if common_label_stems != ["oka", "okala", "ota", "otara"]:
        raise RuntimeError(f"unexpected cross-register stems: {common_label_stems}")
    write_tsv(CROSS_REGISTER, cross_rows, list(cross_rows[0]))

    transitions = read_tsv(TRANSITIONS)
    a09_transition = next(row for row in transitions if row["a_member"] == "9")
    if not (
        a09_transition["f70_locus"] == "f70v1.5"
        and a09_transition["f72_locus"] == "f72r1.5"
        and a09_transition["f70_state"] == "TORSO_COVERED"
        and a09_transition["f72_state"] == "TORSO_UNCOVERED"
    ):
        raise RuntimeError("A09 transition binding changed")

    all_counts = Counter(row["terminal"] for row in all_terminal)
    all_any_final = Counter(row["terminal"] for row in all_terminal if row["any_line_final"])
    paired_counts = Counter(row["terminal"] for row in paired_occ)
    paired_multi_final = Counter(row["terminal"] for row in paired_occ if row["multi_line_final"])
    primary_stem = mh_result(paired_occ, ["stem"], lambda row: bool(row["multi_line_final"]))
    multi_token_occ = [row for row in paired_occ if not row["single_token_line"]]
    primary_stem_multitoken_only = mh_result(
        multi_token_occ, ["stem"], lambda row: bool(row["multi_line_final"])
    )
    primary_meta = mh_result(
        paired_occ, ["stem", "section", "language", "hand"],
        lambda row: bool(row["multi_line_final"]),
    )
    primary_page = mh_result(paired_occ, ["stem", "page"], lambda row: bool(row["multi_line_final"]))

    directions = Counter(row["direction"] for row in stem_rows)
    sign_trials = directions["M_HIGHER"] + directions["L_HIGHER"]
    sign_p = binomial_upper(directions["M_HIGHER"], sign_trials)
    thick = [row for row in stem_rows if row["both_endings_at_least_5"]]
    thick_m_higher = sum(row["direction"] == "M_HIGHER" for row in thick)
    thick_sign_p = binomial_upper(thick_m_higher, len(thick))

    last_penult_rows = [row for row in paired_occ if row["token_count"] > 1 and row["distance_from_end"] in {0, 1}]
    last_vs_penult = mh_result(last_penult_rows, ["stem"], lambda row: row["distance_from_end"] == 0)
    nonfinal_rows = [row for row in paired_occ if row["token_count"] > 1 and row["distance_from_end"] >= 1]
    penult_vs_earlier = mh_result(nonfinal_rows, ["stem"], lambda row: row["distance_from_end"] == 1)

    position_rows = [
        {
            "test_id": "ALL_LM_ANY_LINE_FINAL",
            "scope": "all admitted l/m terminal running tokens; singleton lines count final",
            "m_n": all_counts["m"], "m_positive": all_any_final["m"],
            "l_n": all_counts["l"], "l_positive": all_any_final["l"],
            "odds_ratio": f12((all_any_final["m"] * (all_counts["l"] - all_any_final["l"])) / ((all_counts["m"] - all_any_final["m"]) * all_any_final["l"])),
            "exact_upper_p": "DESCRIPTIVE_PREDECESSOR_REPLICATION",
            "result": "REPLICATE_GDT634_POSITION_MARKER",
        },
        {
            "test_id": "PAIRED_STEM_MULTI_LINE_RAW",
            "scope": f"{len(paired_stems)} nonempty exact stems; only final token of multi-token line is positive",
            "m_n": paired_counts["m"], "m_positive": paired_multi_final["m"],
            "l_n": paired_counts["l"], "l_positive": paired_multi_final["l"],
            "odds_ratio": f12((paired_multi_final["m"] * (paired_counts["l"] - paired_multi_final["l"])) / ((paired_counts["m"] - paired_multi_final["m"]) * paired_multi_final["l"])),
            "exact_upper_p": "NA_UNCONDITIONED", "result": "M_BOUNDARY_ENRICHED",
        },
        {
            "test_id": "PAIRED_STEM_CONDITIONAL", "scope": "fixed exact stem margins",
            "m_n": paired_counts["m"], "m_positive": paired_multi_final["m"],
            "l_n": paired_counts["l"], "l_positive": paired_multi_final["l"],
            "odds_ratio": f12(primary_stem["odds_ratio"]), "exact_upper_p": f12(primary_stem["exact_upper_p"]),
            "result": "PASS_PRIMARY" if primary_stem["odds_ratio"] > 5 and primary_stem["exact_upper_p"] < .001 else "FAIL_PRIMARY",
        },
        {
            "test_id": "STEM_CONDITIONAL_MULTITOKEN_ONLY", "scope": "singleton lines removed; fixed exact stem margins",
            "m_n": sum(row["terminal"] == "m" for row in multi_token_occ),
            "m_positive": sum(row["terminal"] == "m" and row["multi_line_final"] for row in multi_token_occ),
            "l_n": sum(row["terminal"] == "l" for row in multi_token_occ),
            "l_positive": sum(row["terminal"] == "l" and row["multi_line_final"] for row in multi_token_occ),
            "odds_ratio": f12(primary_stem_multitoken_only["odds_ratio"]),
            "exact_upper_p": f12(primary_stem_multitoken_only["exact_upper_p"]),
            "result": "SENSITIVITY_RETAINS" if primary_stem_multitoken_only["odds_ratio"] > 5 and primary_stem_multitoken_only["exact_upper_p"] < .001 else "SENSITIVITY_FAILS",
        },
        {
            "test_id": "STEM_SECTION_LANGUAGE_HAND_CONDITIONAL", "scope": "fixed stem, section, language and hand margins",
            "m_n": paired_counts["m"], "m_positive": paired_multi_final["m"],
            "l_n": paired_counts["l"], "l_positive": paired_multi_final["l"],
            "odds_ratio": f12(primary_meta["odds_ratio"]), "exact_upper_p": f12(primary_meta["exact_upper_p"]),
            "result": "PASS_TRANSFER" if primary_meta["odds_ratio"] > 3 and primary_meta["exact_upper_p"] < .01 else "FAIL_TRANSFER",
        },
        {
            "test_id": "STEM_PAGE_CONDITIONAL", "scope": "fixed stem and page margins",
            "m_n": paired_counts["m"], "m_positive": paired_multi_final["m"],
            "l_n": paired_counts["l"], "l_positive": paired_multi_final["l"],
            "odds_ratio": f12(primary_page["odds_ratio"]), "exact_upper_p": f12(primary_page["exact_upper_p"]),
            "result": "PASS_TRANSFER" if primary_page["odds_ratio"] > 3 and primary_page["exact_upper_p"] < .01 else "FAIL_TRANSFER",
        },
        {
            "test_id": "STEM_DIRECTION_SIGN", "scope": "per-stem final-rate direction; ties removed",
            "m_n": sign_trials, "m_positive": directions["M_HIGHER"],
            "l_n": sign_trials, "l_positive": directions["L_HIGHER"],
            "odds_ratio": "NA_SIGN_TEST", "exact_upper_p": f12(sign_p),
            "result": "PASS_BROAD" if sign_p < .001 else "FAIL_BROAD",
        },
        {
            "test_id": "THICK_STEM_DIRECTION_SIGN", "scope": "stems with at least five l and five m occurrences",
            "m_n": len(thick), "m_positive": thick_m_higher,
            "l_n": len(thick), "l_positive": len(thick) - thick_m_higher,
            "odds_ratio": "NA_SIGN_TEST", "exact_upper_p": f12(thick_sign_p),
            "result": "PASS_ALL_THICK" if thick_m_higher == len(thick) else "MIXED",
        },
        {
            "test_id": "LAST_VS_PENULTIMATE", "scope": "multi-token lines, fixed stem, distance 0 versus 1",
            "m_n": sum(row["terminal"] == "m" for row in last_penult_rows),
            "m_positive": sum(row["terminal"] == "m" and row["distance_from_end"] == 0 for row in last_penult_rows),
            "l_n": sum(row["terminal"] == "l" for row in last_penult_rows),
            "l_positive": sum(row["terminal"] == "l" and row["distance_from_end"] == 0 for row in last_penult_rows),
            "odds_ratio": f12(last_vs_penult["odds_ratio"]), "exact_upper_p": f12(last_vs_penult["exact_upper_p"]),
            "result": "BOUNDARY_GRADIENT",
        },
        {
            "test_id": "PENULTIMATE_VS_EARLIER", "scope": "nonfinal positions, fixed stem, distance 1 versus 2+",
            "m_n": sum(row["terminal"] == "m" for row in nonfinal_rows),
            "m_positive": sum(row["terminal"] == "m" and row["distance_from_end"] == 1 for row in nonfinal_rows),
            "l_n": sum(row["terminal"] == "l" for row in nonfinal_rows),
            "l_positive": sum(row["terminal"] == "l" and row["distance_from_end"] == 1 for row in nonfinal_rows),
            "odds_ratio": f12(penult_vs_earlier["odds_ratio"]), "exact_upper_p": f12(penult_vs_earlier["exact_upper_p"]),
            "result": "PREBOUNDARY_GRADIENT",
        },
    ]
    write_tsv(POSITION_TESTS, position_rows, list(position_rows[0]))

    stratified_rows: list[dict[str, Any]] = []
    for field, values in (
        ("section", sorted({row["section"] for row in paired_occ})),
        ("language", sorted({row["language"] for row in paired_occ})),
        ("hand", sorted({row["hand"] for row in paired_occ})),
    ):
        for value in values:
            subset = [row for row in paired_occ if row[field] == value]
            result = mh_result(subset, ["stem"], lambda row: bool(row["multi_line_final"]))
            counts = Counter(row["terminal"] for row in subset)
            finals = Counter(row["terminal"] for row in subset if row["multi_line_final"])
            stratified_rows.append(
                {
                    "analysis": field.upper(), "held_or_value": value,
                    "m_n": counts["m"], "m_final": finals["m"],
                    "l_n": counts["l"], "l_final": finals["l"],
                    "informative_strata": result["informative_strata"],
                    "mh_odds_ratio": f12(result["odds_ratio"]),
                    "exact_upper_p": f12(result["exact_upper_p"]),
                    "decision": "DIRECTION_RETAINED" if result["odds_ratio"] > 1 else "THIN_OR_REVERSED",
                }
            )
    leaveout_pass = True
    for held in sorted({row["section"] for row in paired_occ}):
        subset = [row for row in paired_occ if row["section"] != held]
        result = mh_result(
            subset, ["stem", "section", "language", "hand"],
            lambda row: bool(row["multi_line_final"]),
        )
        counts = Counter(row["terminal"] for row in subset)
        finals = Counter(row["terminal"] for row in subset if row["multi_line_final"])
        passed = result["odds_ratio"] > 3 and result["exact_upper_p"] < .01
        leaveout_pass &= passed
        stratified_rows.append(
            {
                "analysis": "LEAVE_ONE_SECTION_OUT", "held_or_value": held,
                "m_n": counts["m"], "m_final": finals["m"],
                "l_n": counts["l"], "l_final": finals["l"],
                "informative_strata": result["informative_strata"],
                "mh_odds_ratio": f12(result["odds_ratio"]),
                "exact_upper_p": f12(result["exact_upper_p"]),
                "decision": "PASS" if passed else "FAIL",
            }
        )
    write_tsv(STRATIFIED, stratified_rows, list(stratified_rows[0]))

    a09_homologs = [row for row in homolog_rows if row["a09_holdout"]]
    homolog_lm = [row for row in homolog_rows if row["terminal_lm_same_stem"]]
    same_array_contrast = any(row["same_array_opposition"] for row in terminal_labels)
    c1_selected = (
        primary_stem["odds_ratio"] > 5 and primary_stem["exact_upper_p"] < .001
        and primary_meta["odds_ratio"] > 3 and primary_meta["exact_upper_p"] < .01
        and primary_page["odds_ratio"] > 3 and primary_page["exact_upper_p"] < .01
        and leaveout_pass
    )
    obligatory_rejected = (
        paired_counts["m"] - paired_multi_final["m"] >= 10
        and paired_multi_final["l"] >= 10
    )
    candidate_rows = [
        {
            "candidate_id": "C1", "candidate": "BOUNDARY_FAVOURED_TERMINAL_SURFACE_FIELD",
            "decision": "SELECT_STRUCTURAL" if c1_selected else "NOT_SELECTED",
            "evidence": f"{len(paired_stems)} nonempty paired stems; stem OR={f12(primary_stem['odds_ratio'])}; metadata OR={f12(primary_meta['odds_ratio'])}; page OR={f12(primary_page['odds_ratio'])}",
            "counterevidence": f"{paired_counts['m'] - paired_multi_final['m']} paired m events are not multi-line-final and {paired_multi_final['l']} paired l events are",
            "confidence": "HIGH_FORMAL__MECHANISM_OPEN", "component_export_credit": "FORMAL_POSITION_ONLY", "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "C2", "candidate": "OBLIGATORY_LINE_FINAL_ALLOGRAPH",
            "decision": "REJECT_DETERMINISTIC" if obligatory_rejected else "RETAIN",
            "evidence": "strong exact-stem boundary preference",
            "counterevidence": f"nonfinal paired m={paired_counts['m'] - paired_multi_final['m']}; final paired l={paired_multi_final['l']}",
            "confidence": "REJECTED_AS_OBLIGATORY", "component_export_credit": "ZERO", "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "C3", "candidate": "PORTABLE_SEMANTIC_L_M_SUFFIX",
            "decision": "HOLD_NO_INDEPENDENT_STATE_GAIN", "evidence": "four normalized compact label bases have nonempty exact running-text counterparts",
            "counterevidence": "physical line position explains a large transferable share; no repeated mobile image or record-state contrast is supplied here",
            "confidence": "C0_MECHANISM_RIVAL", "component_export_credit": "ZERO_SEMANTIC", "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "C4", "candidate": "PAGE_LEVEL_ALLOGRAPH",
            "decision": "REJECT_PAGE_ONLY" if same_array_contrast else "RETAIN", "evidence": "none beyond source locality",
            "counterevidence": "ota-l/m and otara-l/m each occur within one source array with the same immediate stem",
            "confidence": "PAGE_ONLY_REJECTED", "component_export_credit": "ZERO", "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "C5", "candidate": "WHOLE_LABEL_CLOTHING_STATUS",
            "decision": "REJECT_PORTABLE", "evidence": "A09 alone changes B2/covered to B3/uncovered",
            "counterevidence": "GDT799 f72 is state-pure/nonmobile and the four stem oppositions recur outside this homolog and in running text",
            "confidence": "A09_SINGLETON_ONLY", "component_export_credit": "ZERO", "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "C6", "candidate": "INDIVISIBLE_LEARNED_WHOLES_ONLY",
            "decision": "RETAIN_SECONDARY_NOT_SUFFICIENT", "evidence": "A09 direction itself is not predicted and exact wholes remain designation candidates",
            "counterevidence": f"the same ending preference transfers across {len(paired_stems)} nonempty stems, every thick stem, sections, hands and pages",
            "confidence": "WHOLE_PLUS_BOUND_FIELD_PRIMARY", "component_export_credit": "WHOLE_ONLY", "confirmed_lexeme": "NO",
        },
    ]
    write_tsv(CANDIDATES, candidate_rows, list(candidate_rows[0]))

    card_rows = [
        {
            "card_id": "GDT800-SC1",
            "scope": "ZL3b terminal m on a complete surface whose l counterpart is attested in the admitted running cache",
            "structural_tag": "BOUNDARY_FAVOURED_TERMINAL_SURFACE",
            "german_display": "zeilenrandbevorzugte Endform; Wert offen",
            "confidence": "HIGH_FORMAL__LOW_MECHANISM__ZERO_LEXICAL",
            "positive_evidence": f"m final {paired_multi_final['m']}/{paired_counts['m']} versus l {paired_multi_final['l']}/{paired_counts['l']}; stem-conditioned OR {f12(primary_stem['odds_ratio'])}; exact p {f12(primary_stem['exact_upper_p'])}",
            "counterevidence": f"m nonfinal {paired_counts['m'] - paired_multi_final['m']}; l final {paired_multi_final['l']}; A09 labels are both standalone and the B2/B3 direction is not predicted",
            "equivalence_license": "NONE__DO_NOT_NORMALIZE_M_TO_L", "semantic_export": "ZERO", "plaintext_value": "UNKNOWN",
        }
    ]
    write_tsv(STRUCTURAL_CARD, card_rows, list(card_rows[0]))

    homolog_dist1 = sum(row["compact_edit_distance"] == 1 for row in homolog_rows)
    homolog_same_family = sum(row["same_boundary_family"] for row in homolog_rows)
    status = "PARTIAL__155_NONEMPTY_PAIRED_STEMS__BOUNDARY_FIELD_SELECTED__OBLIGATORY_ALLOGRAPH_REJECTED__A09_DIRECTION_OPEN__ZERO_LEXEMES"
    report = f"""# GDT800 — terminal B2/B3 line-final bridge

Status: **{status}**

## Outcome

The A09 change licenses neither a portable clothing reading nor dismissal as a
mere transcription accident.
All three alternate readings distinguish terminal B2 in f70 `okalal` from B3
in f72 `okalam`, and direct inspection of the already admitted Yale crops finds
two visible terminal ink forms without decisive damage. The coarse family
`AQABAB` hides this member difference and must not be read as glyph identity.

The complete homolog census contains **{len(homolog_rows)}** cross-array
same-Kluge-member pairs. Only **{len(homolog_lm)}** is a terminal `l/m`
same-stem change: A09 itself. It is therefore not a repeated homolog
operation. Across all circular labels, however, four normalized compact bases
contrast B2/B3: `oka`, `okala`, `ota`, and `otara`. Two contrasts occur within
one source array, rejecting page-only allography.

## Running-text bridge

The independent admitted running cache contains **{len(paired_stems)}** exact
nonempty surface stems attested with both `l` and `m`, covering **{len(paired_occ)}**
occurrences. On multi-token lines, `m` is final in
**{paired_multi_final['m']}/{paired_counts['m']}**, while `l` is final in
**{paired_multi_final['l']}/{paired_counts['l']}**. Conditioning on the exact
stem gives OR **{f12(primary_stem['odds_ratio'])}** and exact one-sided
`p={f12(primary_stem['exact_upper_p'])}`. Stem×section×language×hand remains
OR **{f12(primary_meta['odds_ratio'])}**; stem×page remains OR
**{f12(primary_page['odds_ratio'])}**. Every leave-one-section-out gate passes.
Removing the {sum(row['single_token_line'] for row in paired_occ)} singleton-line
events rather than coding them nonfinal retains OR
**{f12(primary_stem_multitoken_only['odds_ratio'])}**
(`p={f12(primary_stem_multitoken_only['exact_upper_p'])}`).

The effect is broad: {directions['M_HIGHER']} stems favor `m`,
{directions['L_HIGHER']} favor `l`, and {directions['TIE']} tie. All
{len(thick)} stems with at least five occurrences of each ending favor `m`.
The four compact label/running bridges therefore sit inside a large formal
opposition across the admitted cache rather than an A09 invention.

The paired-stem population explicitly excludes **{empty_prefix_events}**
one-sign `l`/`m` tokens. They have no preceding surface and therefore cannot
constitute a stem pair. The broad predecessor replication still reports them
in the all-terminal descriptive census, but they receive no stem-model weight.

## What the ending now means—and does not mean

The selected renderer tag is **BOUNDARY_FAVOURED_TERMINAL_SURFACE**, displayed
as “zeilenrandbevorzugte Endform; Wert offen”. This is a structural field, not
a word translation. It improves the architecture from indivisible wholes to
**learned stem/whole plus bound terminal realization**.

The evidence does not license `m=l`, an obligatory final allograph, a case
ending, abbreviation, sound or semantic suffix. There are
**{paired_counts['m'] - paired_multi_final['m']}** paired nonfinal `m` events
and **{paired_multi_final['l']}** paired final `l` events. Both A09 labels are
standalone units, so the running-text edge model cannot predict why f70 takes
B2 and f72 B3. That direction remains a local whole-label/status rival.

## Concrete A09 reading

For now the least misleading structured display is:

```text
f70 A09  okala + B2-terminal   learned A09 designation; terminal variant B2
f72 A09  okala + B3-terminal   learned A09 designation; boundary-favoured variant B3
```

Neither line says “covered”, “uncovered”, a zodiac name, person, day or degree.
The inherited clothing difference remains a negative control because f72's
outer ring is visually nonmobile.

## Next discriminator

Use the existing GDT791 record/panel spine to ask whether record or field
closure adds held-page predictive value beyond exact physical line position.
Added record-closure transfer would favor a bound status/grammar field; no
added gain would favor scribal/layout realization. Open no new page.

## Access correction

Before the guarded build, one broad repository text search traversed filenames
under a mixed semantic-assumptions directory. It displayed no f84/f84r row or
value, and nothing from that search enters a source, score or hypothesis. All
material inputs above are explicit hash-locked f84-free predecessor artifacts;
subsequent mixed-TSV access remains restricted to `vmanus-exp query-tsv`.
"""
    REPORT.write_text(report, encoding="utf-8")

    outputs = [
        OCCURRENCES, STEMS, HOMOLOGS, LABEL_TERMINALS, CROSS_REGISTER,
        POSITION_TESTS, STRATIFIED, CANDIDATES, STRUCTURAL_CARD, REPORT,
    ]
    inputs = [LINE_READER, LABEL_ATLAS, TRANSITIONS, SOURCE_LOCK, NATIVE_AUDIT, MODEL_SPECS]
    result: dict[str, Any] = {
        "schema": "GDT800_RESULT_V1", "experiment": "GDT800", "status": status,
        "decision": "LEARNED_WHOLE_OR_STEM_PLUS_BOUNDARY_FAVOURED_TERMINAL_FIELD",
        "running_cache": {
            "lines": len(line_rows), "tokens": total_tokens,
            "all_l": all_counts["l"], "all_m": all_counts["m"],
            "all_l_any_line_final": all_any_final["l"], "all_m_any_line_final": all_any_final["m"],
            "paired_stems": len(paired_stems), "paired_occurrences": len(paired_occ),
            "empty_prefix_events_excluded_from_stem_model": empty_prefix_events,
            "paired_l": paired_counts["l"], "paired_m": paired_counts["m"],
            "paired_l_multi_line_final": paired_multi_final["l"],
            "paired_m_multi_line_final": paired_multi_final["m"],
        },
        "primary_tests": {
            "stem": primary_stem, "stem_multitoken_only": primary_stem_multitoken_only,
            "stem_section_language_hand": primary_meta,
            "stem_page": primary_page, "leave_one_section_out_all_pass": leaveout_pass,
            "m_higher_stems": directions["M_HIGHER"], "l_higher_stems": directions["L_HIGHER"],
            "tie_stems": directions["TIE"], "thick_stems": len(thick), "thick_m_higher": thick_m_higher,
        },
        "labels": {
            "atlas_loci": len(label_rows), "terminal_b2_b3": len(terminal_labels),
            "B2": 12, "B3": 15, "cross_register_stems": common_label_stems,
            "homolog_pairs": len(homolog_rows), "homolog_distance_one": homolog_dist1,
            "homolog_same_family": homolog_same_family, "homolog_terminal_lm": len(homolog_lm),
            "a09_holdout_pairs": len(a09_homologs),
        },
        "a09": {
            "f70": {"locus": "f70v1.5", "surface": "okalal", "member": "B2", "state": a09_transition["f70_state"]},
            "f72": {"locus": "f72r1.5", "surface": "okalam", "member": "B3", "state": a09_transition["f72_state"]},
            "direction_predicted": False,
        },
        "semantic_exports": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "f84_or_f84r_accessed": False,
        "claim_ceiling": "FORMAL_BOUNDARY_FIELD_ONLY__NO_EQUIVALENCE_MORPHEME_WORD_OR_TRANSLATION",
        "inputs": {rel(path): sha(path) for path in inputs},
        "outputs": {rel(path): sha(path) for path in outputs},
        "implementation": {rel(Path(__file__)): sha(Path(__file__))},
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(
        f"paired stems={len(paired_stems)} occurrences={len(paired_occ)}; "
        f"m final={paired_multi_final['m']}/{paired_counts['m']} l final={paired_multi_final['l']}/{paired_counts['l']}"
    )
    print(
        f"stem OR={f12(primary_stem['odds_ratio'])} p={f12(primary_stem['exact_upper_p'])}; "
        f"meta OR={f12(primary_meta['odds_ratio'])}; page OR={f12(primary_page['odds_ratio'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
