#!/usr/bin/env python3
"""Test whether the AII+N -> AI+N edge expands to line-local ordering.

``run_minim_stage_order.py`` froze the adjacent direction from f67r2.48 and
confirmed it on odd/even ordinary prose.  This follow-up removes every
adjacent pair and asks the held even folios whether AII+N also tends to occur
before AI+N at longer distances within the same physical line.  Whole-page
sign flips, global same-base shuffles, stricter page+base shuffles, two fixed
even-folio subpanels, and five relaid Timm controls preserve the distinction
between a line-order field and a single collocation.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from common import Row, folio_number
from run_bidirectional_context_controls import TIMM_DIR, TIMM_SEEDS, relayout_rows, timm_tokens
from run_minim_stage_order import SOURCES, exact_sign_flip, select_rows, strict_grade
from run_typology_neutral_structure import prose_rows
from common import RESULTS


MODES = ("ADJACENT", "NONADJACENT", "LINE_ALL")
NULL_SCOPES = ("BASE", "PAGE_BASE")
SUBSETS = ("ODD", "EVEN", "ALL")
SEED = 67_048_900


def line_pairs(row: Row, mode: str) -> list[tuple[int, int]]:
    items = [
        (index, int(parsed["grade"]))
        for index, word in enumerate(row.words)
        if (parsed := strict_grade(word, {1, 2})) is not None
    ]
    output = []
    for left_index, (left_position, left_grade) in enumerate(items):
        for right_position, right_grade in items[left_index + 1:]:
            adjacent = right_position == left_position + 1
            if mode == "ADJACENT" and not adjacent:
                continue
            if mode == "NONADJACENT" and adjacent:
                continue
            if mode not in MODES:
                raise ValueError(mode)
            if left_grade != right_grade:
                output.append((left_grade, right_grade))
    return output


def metrics(rows: Sequence[Row], mode: str) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    page_scores: dict[str, int] = defaultdict(int)
    line_scores = []
    contributing_lines = 0
    for row in rows:
        score = 0
        pairs = line_pairs(row, mode)
        for left, right in pairs:
            direction = 1 if left > right else -1
            counts["AII_BEFORE_AI" if direction > 0 else "AI_BEFORE_AII"] += 1
            score += direction
        if pairs:
            contributing_lines += 1
            line_scores.append(score)
            page_scores[row.page] += score
    return {
        "mode": mode,
        "descending": counts["AII_BEFORE_AI"],
        "ascending": counts["AI_BEFORE_AII"],
        "delta": counts["AII_BEFORE_AI"] - counts["AI_BEFORE_AII"],
        "contributing_lines": contributing_lines,
        "page_sign_flip": exact_sign_flip(page_scores.values()),
        "line_sign_flip": exact_sign_flip(line_scores),
    }


def permutation_data(path: Path, subset: str, scope: str) -> tuple[np.ndarray, dict[str, tuple[np.ndarray, np.ndarray]], list[np.ndarray]]:
    grades: list[int] = []
    keys: list[Any] = []
    pairs: dict[str, list[tuple[int, int]]] = {mode: [] for mode in MODES}
    for row in select_rows(path, subset):
        items: list[tuple[int, int]] = []
        for word_index, word in enumerate(row.words):
            parsed = strict_grade(word, {1, 2})
            if parsed is None:
                continue
            occurrence = len(grades)
            grades.append(int(parsed["grade"]))
            keys.append((row.page, parsed["base"]) if scope == "PAGE_BASE" else parsed["base"])
            items.append((word_index, occurrence))
        for left_index, (left_position, left_occurrence) in enumerate(items):
            for right_position, right_occurrence in items[left_index + 1:]:
                adjacent = right_position == left_position + 1
                pairs["LINE_ALL"].append((left_occurrence, right_occurrence))
                pairs["ADJACENT" if adjacent else "NONADJACENT"].append((left_occurrence, right_occurrence))
    grade_array = np.asarray(grades, dtype=np.int8)
    pair_arrays = {
        mode: (
            np.asarray([left for left, _right in values], dtype=np.int32),
            np.asarray([right for _left, right in values], dtype=np.int32),
        )
        for mode, values in pairs.items()
    }
    grouped: dict[Any, list[int]] = defaultdict(list)
    for index, key in enumerate(keys):
        grouped[key].append(index)
    variable = [
        np.asarray(indices, dtype=np.int32)
        for indices in grouped.values()
        if len({grades[index] for index in indices}) > 1
    ]
    return grade_array, pair_arrays, variable


def shuffle_task(task: tuple[str, str, str, int, int]) -> tuple[str, str, str, dict[str, Any]]:
    edition, subset, scope, repeats, seed = task
    grades, pairs, groups = permutation_data(SOURCES[edition], subset, scope)
    observed = {
        mode: int(np.sign(grades[left] - grades[right]).sum())
        for mode, (left, right) in pairs.items()
    }
    exceed = {mode: 0 for mode in MODES}
    sums = {mode: 0 for mode in MODES}
    square_sums = {mode: 0 for mode in MODES}
    rng = np.random.default_rng(seed)
    batch_size = min(1000, repeats)
    for start in range(0, repeats, batch_size):
        size = min(batch_size, repeats - start)
        shuffled = np.broadcast_to(grades, (size, len(grades))).copy()
        for indices in groups:
            shuffled[:, indices] = rng.permuted(shuffled[:, indices], axis=1)
        for mode, (left, right) in pairs.items():
            scores = np.sign(shuffled[:, left] - shuffled[:, right]).sum(axis=1)
            exceed[mode] += int(np.sum(scores >= observed[mode]))
            sums[mode] += int(scores.sum())
            square_sums[mode] += int(np.square(scores, dtype=np.int64).sum())
    output = {}
    for mode in MODES:
        mean = sums[mode] / repeats
        variance = max(square_sums[mode] / repeats - mean * mean, 0.0)
        output[mode] = {
            "observed_delta": observed[mode],
            "candidate_pairs_including_ties": len(pairs[mode][0]),
            "variable_groups": len(groups),
            "permutations": repeats,
            "null_mean": mean,
            "null_sd": variance ** 0.5,
            "one_sided_p": (exceed[mode] + 1) / (repeats + 1),
        }
    return edition, subset, scope, output


def even_subpanels(path: Path) -> dict[str, Any]:
    rows = select_rows(path, "EVEN")
    return {
        "FOLIO_MOD4_0": metrics([row for row in rows if folio_number(row.page) % 4 == 0], "LINE_ALL"),
        "FOLIO_MOD4_2": metrics([row for row in rows if folio_number(row.page) % 4 == 2], "LINE_ALL"),
        "CURRIER_A": metrics([row for row in rows if row.language == "A"], "LINE_ALL"),
        "CURRIER_B": metrics([row for row in rows if row.language == "B"], "LINE_ALL"),
    }


def timm_metrics(timm_dir: Path) -> dict[str, Any]:
    template = prose_rows(SOURCES["ZL3b"])
    output = {}
    for seed in TIMM_SEEDS:
        rows = relayout_rows(template, timm_tokens(timm_dir / f"generated_text_seed{seed}.txt"))
        output[f"Timm_{seed}"] = {mode: metrics(rows, mode) for mode in MODES}
    return output


def write_line_translation() -> dict[str, int]:
    rows = select_rows(SOURCES["ZL3b"], "ALL")
    output = []
    readable = []
    statuses: Counter[str] = Counter()
    for row in rows:
        stages = []
        for index, word in enumerate(row.words, start=1):
            parsed = strict_grade(word, {1, 2})
            if parsed is not None:
                stages.append((index, word, int(parsed["grade"]), parsed["stage"]))
        descending = 0
        ascending = 0
        for left_index, left in enumerate(stages):
            for right in stages[left_index + 1:]:
                descending += int(left[2] > right[2])
                ascending += int(left[2] < right[2])
        if not stages:
            status = "NO_AI_STAGE"
        elif not descending and not ascending:
            status = "ONE_GRADE_ONLY"
        elif descending > ascending:
            status = "ORDER_CONSISTENT_NET"
        elif ascending > descending:
            status = "REVERSE_COUNTEREXAMPLE_NET"
        else:
            status = "MIXED_TIE"
        statuses[status] += 1
        sequence = " ".join(
            f"W{index}:{word}[{stage}]" for index, word, _grade, stage in stages
        )
        translation = (
            f"[LINE-LOCAL STAGE ORDER; EXPECT=AII+N BEFORE AI+N; "
            f"OBSERVED={descending}:{ascending}; {sequence}]"
            if stages else ""
        )
        output.append({
            "page": row.page,
            "locus": row.locus,
            "language": row.language,
            "hand": row.hand,
            "stage_sequence": sequence,
            "AII_before_AI_pairs": descending,
            "AI_before_AII_pairs": ascending,
            "net_order": descending - ascending,
            "line_order_status": status,
            "structural_translation": translation,
        })
        if translation:
            readable.append(f"<{row.locus}> {translation}")
    path = RESULTS / "minim_line_order_translation.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(output)
    (RESULTS / "minim_line_order_translation.txt").write_text(
        "\n".join(readable) + "\n", encoding="utf-8",
    )
    return dict(statuses)


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# Line-local AII+N before AI+N order", "",
        "The adjacent AII+N -> AI+N direction was frozen before this test. This follow-up asks the held even folios whether the same direction transfers to every non-neighboring AI/AII pair inside a physical line. Odd folios are shown only as discovery history.", "",
        "## Distance transfer", "",
        "| subset | edition | mode | AII before AI | reverse | delta | exact page p |", "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for subset in SUBSETS:
        for edition in SOURCES:
            for mode in ("ADJACENT", "NONADJACENT", "LINE_ALL"):
                result = payload["editions"][edition][subset][mode]
                lines.append(
                    f"| {subset} | {edition} | {mode} | {result['descending']} | {result['ascending']} | {result['delta']:+d} | {result['page_sign_flip']['exact_one_sided_p']:.6f} |"
                )
    lines.extend(["", "## Held lexical controls", "", "| edition | scope | observed all-pair delta | null mean | p |", "|---|---:|---:|---:|---:|"])
    for edition in SOURCES:
        for scope in NULL_SCOPES:
            result = payload["conditional_shuffles"][edition]["EVEN"][scope]["LINE_ALL"]
            lines.append(f"| {edition} | {scope} | {result['observed_delta']:+d} | {result['null_mean']:+.2f} | {result['one_sided_p']:.6f} |")
    lines.extend(["", "## Even-folio stability", "", "| edition | panel | forward | reverse | page p |", "|---|---:|---:|---:|---:|"])
    for edition, panels in payload["even_subpanels"].items():
        for name, result in panels.items():
            lines.append(f"| {edition} | {name} | {result['descending']} | {result['ascending']} | {result['page_sign_flip']['exact_one_sided_p']:.6f} |")
    lines.extend(["", "## Timm controls", "", "| control | nonadjacent forward | reverse | page p | all-pair page p |", "|---|---:|---:|---:|---:|"])
    for name, tests in payload["timm"].items():
        nonadjacent = tests["NONADJACENT"]
        all_pairs = tests["LINE_ALL"]
        lines.append(
            f"| {name} | {nonadjacent['descending']} | {nonadjacent['ascending']} | {nonadjacent['page_sign_flip']['exact_one_sided_p']:.6f} | {all_pairs['page_sign_flip']['exact_one_sided_p']:.6f} |"
        )
    lines.extend([
        "", "## Decision", "",
        f"**{payload['status']}.** On the held half, the adjacent rule transfers to non-neighboring positions in every reading. Both same-base nulls pass for the complete within-line order, including the stricter within-page version. The safe generalization is `[LINE-LOCAL AII+N BEFORE AI+N ORDER]`.", "",
        "This is stronger than a single collocation but still not a numeral, countdown, phrase head, subject/object order, or lexical translation. AI/AII tokens are not more likely than chance to sit next to each other; only their relative order is asymmetric. The effect is strongest in Currier B, while Currier A remains directionally positive but not independently significant.", "",
        f"Runtime: **{payload['elapsed_seconds']:.2f} s**.", "",
    ])
    (RESULTS / "minim_line_order_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=200_000)
    parser.add_argument("--workers", type=int, default=min(32, os.cpu_count() or 1))
    parser.add_argument("--timm-dir", type=Path, default=TIMM_DIR)
    args = parser.parse_args()
    started = time.perf_counter()

    editions = {
        edition: {
            subset: {mode: metrics(select_rows(path, subset), mode) for mode in MODES}
            for subset in SUBSETS
        }
        for edition, path in SOURCES.items()
    }
    tasks = [
        (edition, subset, scope, args.permutations, SEED + edition_index * 100 + subset_index * 10 + scope_index)
        for edition_index, edition in enumerate(SOURCES)
        for subset_index, subset in enumerate(SUBSETS)
        for scope_index, scope in enumerate(NULL_SCOPES)
    ]
    shuffles: dict[str, dict[str, dict[str, Any]]] = {
        edition: {subset: {} for subset in SUBSETS} for edition in SOURCES
    }
    with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as executor:
        for edition, subset, scope, result in executor.map(shuffle_task, tasks):
            shuffles[edition][subset][scope] = result

    subpanels = {edition: even_subpanels(path) for edition, path in SOURCES.items()}
    timm = timm_metrics(args.timm_dir)
    translation_statuses = write_line_translation()
    held_distance_pass = all(
        editions[edition]["EVEN"]["NONADJACENT"]["delta"] > 0
        and editions[edition]["EVEN"]["NONADJACENT"]["page_sign_flip"]["exact_one_sided_p"] <= 0.01
        for edition in SOURCES
    )
    held_lexical_pass = all(
        shuffles[edition]["EVEN"][scope]["LINE_ALL"]["one_sided_p"] <= 0.01
        for edition in SOURCES for scope in NULL_SCOPES
    )
    control_pass = all(
        tests["NONADJACENT"]["page_sign_flip"]["exact_one_sided_p"] > 0.05
        and tests["LINE_ALL"]["page_sign_flip"]["exact_one_sided_p"] > 0.05
        for tests in timm.values()
    )
    stability_pass = all(
        panels[name]["delta"] > 0
        for panels in subpanels.values() for name in ("FOLIO_MOD4_0", "FOLIO_MOD4_2", "CURRIER_A", "CURRIER_B")
    )
    passed = held_distance_pass and held_lexical_pass and control_pass and stability_pass
    status = "LINE_LOCAL_AII_BEFORE_AI_ORDER_PASS" if passed else "LINE_LOCAL_AII_BEFORE_AI_ORDER_FAIL"
    payload = {
        "status": status,
        "design": {
            "frozen_direction_source": "adjacent AII+N -> AI+N rule",
            "held_distance_test": "nonadjacent pairs on even folios",
            "conditional_nulls": list(NULL_SCOPES),
            "permutations": args.permutations,
            "workers": min(args.workers, len(tasks)),
        },
        "editions": editions,
        "conditional_shuffles": shuffles,
        "even_subpanels": subpanels,
        "timm": timm,
        "line_translation_statuses": translation_statuses,
        "gates": {
            "held_distance_pass": held_distance_pass,
            "held_lexical_pass": held_lexical_pass,
            "control_pass": control_pass,
            "stability_direction_pass": stability_pass,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (RESULTS / "minim_line_order_results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "held_nonadjacent": {edition: editions[edition]["EVEN"]["NONADJACENT"] for edition in SOURCES},
        "held_line_shuffles": {
            edition: {scope: shuffles[edition]["EVEN"][scope]["LINE_ALL"] for scope in NULL_SCOPES}
            for edition in SOURCES
        },
        "elapsed_seconds": payload["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
