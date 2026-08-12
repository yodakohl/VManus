#!/usr/bin/env python3
"""Compact target-blind calibration for FPR001 ordered-root page retrieval."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SPEC = BASE / "FPR001_ORDERED_ROOT_TARGET_BLIND_CALIBRATION_SPEC.md"
CAPACITY = BASE / "results/fpr001_fifth_relation_ordered_root_capacity.json"
SOURCE = BASE / "results/pre_grounding_interlinear.tsv"
OUT = BASE / "results/fpr001_ordered_root_target_blind_calibration.json"
REPORT = BASE / "results/fpr001_ordered_root_target_blind_calibration_report.md"
QUERY = ("ot", "od", "e", "od", "or")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
FAMILIES = (
    ("NULL", 64), ("FULL_ORDERED", 8), ("REDUCED_ORDERED", 8),
    ("UNORDERED_BAG", 8), ("ONE_EDGE", 8), ("CROSS_WORD_SPLIT", 8),
    ("ONE_READING", 8), ("READING_DISAGREEMENT", 8),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def lcs(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    prior = [0] * (len(b) + 1)
    for x in a:
        current = [0]
        for index, y in enumerate(b, 1):
            current.append(prior[index - 1] + 1 if x == y else max(prior[index], current[-1]))
        prior = current
    return prior[-1]


def rename(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("R:" + item for item in items)


def background() -> tuple[list[str], dict[str, dict[str, int]], int, bool]:
    scores = {edition: defaultdict(int) for edition in EDITIONS}
    skipped = 0
    renaming_invariant = True
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] == "f37v":
                skipped += 1
                continue
            if (row["section"], row["currier"], row["hand"], row["grammar_scope"]) != (
                "H", "A", "1", "CONFIRMED_PROSE"
            ):
                continue
            edition = row["edition"]
            for word in row["root_sequence"].split():
                atoms = tuple(word.split("+"))
                score = lcs(QUERY, atoms)
                renaming_invariant &= score == lcs(rename(QUERY), rename(atoms))
                scores[edition][row["page"]] = max(scores[edition][row["page"]], score)
    pages = sorted(set.intersection(*(set(scores[e]) for e in EDITIONS)))
    if len(pages) != 94 or any(set(scores[e]) != set(pages) for e in EDITIONS):
        raise RuntimeError("background page geometry")
    return pages, {e: dict(scores[e]) for e in EDITIONS}, skipped, renaming_invariant


def fixture_words(family: str, index: int, edition: str) -> tuple[tuple[str, ...], ...]:
    if family == "NULL":
        return ()
    if family == "FULL_ORDERED":
        return (QUERY,)
    if family == "REDUCED_ORDERED":
        return (QUERY[:3],)
    if family == "UNORDERED_BAG":
        return (("e", "or", "od", "od", "ot"),)
    if family == "ONE_EDGE":
        return (("x", "ot", "od", "x"),)
    if family == "CROSS_WORD_SPLIT":
        return (("ot", "od"), ("e", "x"), ("od", "or"))
    if family == "ONE_READING":
        return (QUERY[:3],) if edition == EDITIONS[index % len(EDITIONS)] else ()
    if family == "READING_DISAGREEMENT":
        return (QUERY[:3],) if edition in EDITIONS[:2] else ()
    raise RuntimeError(("family", family))


def fixture_score(family: str, index: int, edition: str) -> int:
    words = fixture_words(family, index, edition)
    return max((lcs(QUERY, word) for word in words), default=0)


def world_pass(pages: list[str], base: dict[str, dict[str, int]], family: str, index: int) -> bool:
    target = pages[index % len(pages)]
    values = {edition: dict(base[edition]) for edition in EDITIONS}
    for edition in EDITIONS:
        values[edition][target] = max(values[edition][target], fixture_score(family, index, edition))
    reading_pass = []
    for edition in EDITIONS:
        observed = values[edition][target]
        inclusive_rank = sum(score >= observed for score in values[edition].values())
        reading_pass.append(observed >= 3 and inclusive_rank == 1 and inclusive_rank / 95 <= 0.02)
    pooled_target = sum(values[e][target] for e in EDITIONS)
    pooled_rank = sum(sum(values[e][page] for e in EDITIONS) >= pooled_target for page in pages)
    return all(reading_pass) and pooled_rank == 1 and pooled_rank / 95 <= 0.02


def build() -> tuple[dict[str, object], str]:
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_TARGET_PAGE_MASKED_CAPACITY":
        raise RuntimeError("capacity gate")
    pages, base, skipped, renaming_invariant = background()
    records = []
    pass_counts = Counter()
    for family, count in FAMILIES:
        for index in range(count):
            passed = world_pass(pages, base, family, index)
            pass_counts[family] += passed
            records.append({"ordinal": len(records), "family": family, "world": index, "passes": passed})
    gates = {
        "null_0_of_64": pass_counts["NULL"] == 0,
        "full_ordered_8_of_8": pass_counts["FULL_ORDERED"] == 8,
        "reduced_ordered_8_of_8": pass_counts["REDUCED_ORDERED"] == 8,
        "unordered_bag_0_of_8": pass_counts["UNORDERED_BAG"] == 0,
        "one_edge_0_of_8": pass_counts["ONE_EDGE"] == 0,
        "cross_word_split_0_of_8": pass_counts["CROSS_WORD_SPLIT"] == 0,
        "one_reading_0_of_8": pass_counts["ONE_READING"] == 0,
        "reading_disagreement_0_of_8": pass_counts["READING_DISAGREEMENT"] == 0,
        "page_reversal_invariant": all(
            world_pass(list(reversed(pages)), base, family, index) == record["passes"]
            for record, (family, index) in zip(records, ((f, i) for f, n in FAMILIES for i in range(n)))
        ),
        "root_renaming_lcs_invariant": renaming_invariant and all(
            lcs(QUERY, word) == lcs(rename(QUERY), rename(word))
            for family, count in FAMILIES for index in range(count)
            for edition in EDITIONS for word in fixture_words(family, index, edition)
        ),
        "literal_fixture_score_contract": all(
            tuple(fixture_score(family, index, edition) for edition in EDITIONS) == expected
            for family, count, expected in (
                ("FULL_ORDERED", 8, (5, 5, 5)),
                ("REDUCED_ORDERED", 8, (3, 3, 3)),
                ("UNORDERED_BAG", 8, (2, 2, 2)),
                ("ONE_EDGE", 8, (2, 2, 2)),
                ("CROSS_WORD_SPLIT", 8, (2, 2, 2)),
                ("READING_DISAGREEMENT", 8, (3, 3, 0)),
            ) for index in range(count)
        ) and all(
            sorted(fixture_score("ONE_READING", index, edition) for edition in EDITIONS) == [0, 0, 3]
            for index in range(8)
        ),
        "f37v_skipped_before_formal_access": skipped == 69,
    }
    decision = "GO_FREEZE_ONE_SHOT_F37V_TARGET" if all(gates.values()) else "STOP_CALIBRATION"
    result: dict[str, object] = {
        "experiment": "FPR001_ORDERED_ROOT_TARGET_BLIND_CALIBRATION",
        "schema": "FPR001_ORDERED_ROOT_TARGET_BLIND_CALIBRATION_V1",
        "status": "PASS_COMPACT_120_WORLD_CALIBRATION" if all(gates.values()) else "STOP_COMPACT_CALIBRATION",
        "decision": decision,
        "background": {
            "pages_per_reading": len(pages),
            "maximum_word_lcs_by_reading": {e: max(base[e].values()) for e in EDITIONS},
            "page_max_lcs_histogram_by_reading": {
                e: {str(k): v for k, v in sorted(Counter(base[e].values()).items())} for e in EDITIONS
            },
            "f37v_rows_skipped_before_formal_access": skipped,
        },
        "pass_counts": dict(pass_counts),
        "world_count": len(records),
        "world_outcome_sha256": hashlib.sha256(bytes(record["passes"] for record in records)).hexdigest(),
        "gates": gates,
        "target_access": {
            "f37v_formal_rows_accessed": False,
            "f37v_score_computed": False,
            "f37v_rank_computed": False,
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (SPEC, CAPACITY, SOURCE)},
        "claim_ceiling": (
            "Calibration validates only a fixed within-word ordered-root held-page statistic. It opens no f37v "
            "formal content and supplies no plant name, word, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    report = (
        "# FPR001 ordered-root target-blind calibration\n\n"
        f"Decision: **{decision}**.\n\n"
        "The compact 120-world suite yields 0/64 NULL, 8/8 FULL_ORDERED, 8/8 REDUCED_ORDERED, and 0/8 in each "
        "UNORDERED_BAG, ONE_EDGE, CROSS_WORD_SPLIT, ONE_READING, and READING_DISAGREEMENT family. Page reversal "
        "is invariant. All 69 f37v reading rows were skipped before formal-field access; no target score or rank was "
        "computed. Literal root fixtures and injective root renaming also pass their frozen controls.\n\n"
        "This authorizes only a separately frozen one-shot f37v target. No plant name, word, plaintext, meaning, or "
        "translation follows.\n"
    )
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result, report = build()
    if args.write:
        OUT.write_bytes(canonical(result))
        REPORT.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
