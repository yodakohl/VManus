#!/usr/bin/env python3
"""Blind ordinary-word calibration for registered experiment F69C001.

This file deliberately contains no target strings or target locus identifiers.
It must succeed before a separate target runner may be written.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
TARGET_ARTIFACT = HERE / "TARGET_RESULT.json"
COMMON_DIR = ROOT / "archive_pre_reset_2026-08-06" / "semantic_assumptions"
sys.path.insert(0, str(COMMON_DIR))
from common import parse_rows  # noqa: E402


SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
ASCII_WORD = re.compile(r"[a-z]+")
ALPHABET = tuple("abcdefghijklmnopqrstuvwxyz$")
ALPHA = 0.5
MAX_PER_PAGE = 2
MAX_TRIALS = 128


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_dihedral(order: tuple[int, ...]) -> tuple[int, ...]:
    n = len(order)
    rotations = [order[i:] + order[:i] for i in range(n)]
    reversed_order = tuple(reversed(order))
    rotations.extend(
        reversed_order[i:] + reversed_order[:i] for i in range(n)
    )
    return min(rotations)


PERMUTATIONS = tuple(itertools.permutations(range(6)))
PERM_ORBITS = {perm: canonical_dihedral(perm) for perm in PERMUTATIONS}
ORBIT_KEYS = tuple(sorted(set(PERM_ORBITS.values())))
assert len(PERMUTATIONS) == 720
assert len(ORBIT_KEYS) == 60
assert all(sum(orbit == key for orbit in PERM_ORBITS.values()) == 12
           for key in ORBIT_KEYS)


def transitions(word: str) -> Counter[tuple[str, str]]:
    padded = "^^" + word + "$"
    return Counter((padded[i:i + 2], padded[i + 2])
                   for i in range(len(word) + 1))


def digest_json(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def make_chunks(surface: str, pair_start: int) -> tuple[str, ...]:
    chunks: list[str] = []
    index = 0
    while index < len(surface):
        if index == pair_start:
            chunks.append(surface[index:index + 2])
            index += 2
        else:
            chunks.append(surface[index])
            index += 1
    output = tuple(chunks)
    assert len(output) == 6
    assert "".join(output) == surface
    return output


def load_reading(path: Path, reading: str) -> tuple[list[dict], dict]:
    rows = parse_rows(path)
    page_words: dict[str, list[str]] = defaultdict(list)
    eligible_by_page: dict[str, list[dict]] = defaultdict(list)

    for row in rows:
        if row.kind != "P" or row.page.startswith("f69"):
            continue
        for word_index, surface in enumerate(row.words):
            if not ASCII_WORD.fullmatch(surface):
                continue
            page_words[row.page].append(surface)
            if len(surface) != 7:
                continue
            key = f"{reading}|{row.page}|{row.locus}|{word_index}|{surface}"
            raw_hash = hashlib.sha256(key.encode("ascii")).digest()
            pair_start = int.from_bytes(raw_hash[:8], "big") % 6
            chunks = make_chunks(surface, pair_start)
            if len(set(chunks)) != 6:
                continue
            eligible_by_page[row.page].append({
                "page": row.page,
                "locus": row.locus,
                "word_index": word_index,
                "surface": surface,
                "chunks": chunks,
                "raw_hash": raw_hash,
                "hash": raw_hash.hex(),
            })

    presample_count = sum(len(items) for items in eligible_by_page.values())
    page_limited: list[dict] = []
    for page in sorted(eligible_by_page):
        items = sorted(
            eligible_by_page[page],
            key=lambda item: (
                item["raw_hash"], item["locus"], item["word_index"],
                item["surface"],
            ),
        )
        page_limited.extend(items[:MAX_PER_PAGE])
    selected = sorted(
        page_limited,
        key=lambda item: (
            item["raw_hash"], item["page"], item["locus"],
            item["word_index"], item["surface"],
        ),
    )[:MAX_TRIALS]

    metadata = {
        "parsed_rows": len(rows),
        "training_pages": len(page_words),
        "training_words": sum(len(words) for words in page_words.values()),
        "eligible_occurrences_before_page_cap": presample_count,
        "eligible_pages_before_page_cap": len(eligible_by_page),
        "page_limited_occurrences": len(page_limited),
        "selected_trials": len(selected),
        "selected_pages": len({item["page"] for item in selected}),
    }
    return selected, {"page_words": page_words, "metadata": metadata}


def build_count_indexes(page_words: dict[str, list[str]]) -> dict:
    global_transitions: Counter[tuple[str, str]] = Counter()
    global_surfaces: Counter[str] = Counter()
    page_transitions: dict[str, Counter[tuple[str, str]]] = {}
    page_surfaces: dict[str, Counter[str]] = {}

    for page, words in page_words.items():
        page_t: Counter[tuple[str, str]] = Counter()
        page_s = Counter(words)
        for surface, frequency in page_s.items():
            for key, multiplicity in transitions(surface).items():
                page_t[key] += frequency * multiplicity
        page_transitions[page] = page_t
        page_surfaces[page] = page_s
        global_transitions.update(page_t)
        global_surfaces.update(page_s)
    return {
        "global_transitions": global_transitions,
        "global_surfaces": global_surfaces,
        "page_transitions": page_transitions,
        "page_surfaces": page_surfaces,
    }


def heldout_model(indexes: dict, page: str,
                  candidate_surfaces: set[str]) -> tuple[Counter, Counter]:
    counts = indexes["global_transitions"].copy()
    counts.subtract(indexes["page_transitions"][page])
    global_surfaces = indexes["global_surfaces"]
    local_surfaces = indexes["page_surfaces"][page]

    for surface in candidate_surfaces:
        outside_frequency = global_surfaces[surface] - local_surfaces[surface]
        if outside_frequency <= 0:
            continue
        for key, multiplicity in transitions(surface).items():
            counts[key] -= outside_frequency * multiplicity

    counts = Counter({key: value for key, value in counts.items() if value > 0})
    context_totals: Counter[str] = Counter()
    for (context, _symbol), value in counts.items():
        context_totals[context] += value
    return counts, context_totals


def markov_score(surface: str, counts: Counter,
                 context_totals: Counter) -> float:
    total = 0.0
    for (context, symbol), multiplicity in transitions(surface).items():
        numerator = counts[(context, symbol)] + ALPHA
        denominator = context_totals[context] + ALPHA * len(ALPHABET)
        total += multiplicity * math.log(numerator / denominator)
    return total / (len(surface) + 1)


def score_trial(trial: dict, indexes: dict) -> tuple[int, int]:
    chunks = trial["chunks"]
    surfaces = {
        "".join(chunks[index] for index in permutation)
        for permutation in PERMUTATIONS
    }
    counts, context_totals = heldout_model(indexes, trial["page"], surfaces)
    orbit_scores = {key: -math.inf for key in ORBIT_KEYS}
    for permutation in PERMUTATIONS:
        surface = "".join(chunks[index] for index in permutation)
        score = markov_score(surface, counts, context_totals)
        orbit = PERM_ORBITS[permutation]
        if score > orbit_scores[orbit]:
            orbit_scores[orbit] = score

    true_orbit = canonical_dihedral(tuple(range(6)))
    true_score = orbit_scores[true_orbit]
    true_rank = sum(score >= true_score for score in orbit_scores.values())

    nontrue_orbits = [key for key in ORBIT_KEYS if key != true_orbit]
    pseudo_index = int.from_bytes(trial["raw_hash"][8:16], "big") % 59
    pseudo_orbit = nontrue_orbits[pseudo_index]
    pseudo_score = orbit_scores[pseudo_orbit]
    pseudo_rank = sum(score >= pseudo_score for score in orbit_scores.values())
    return true_rank, pseudo_rank


def rank_histogram(ranks: list[int]) -> dict[str, int]:
    counts = Counter(ranks)
    return {str(rank): counts[rank] for rank in range(1, 61)}


def run_reading(reading: str, path: Path) -> dict:
    trials, corpus = load_reading(path, reading)
    indexes = build_count_indexes(corpus["page_words"])
    true_ranks: list[int] = []
    pseudo_ranks: list[int] = []
    for trial in trials:
        true_rank, pseudo_rank = score_trial(trial, indexes)
        true_ranks.append(true_rank)
        pseudo_ranks.append(pseudo_rank)

    trial_count = len(trials)
    selected_pages = len({trial["page"] for trial in trials})
    rank1_count = sum(rank == 1 for rank in true_ranks)
    pseudo_rank1_count = sum(rank == 1 for rank in pseudo_ranks)
    median_rank = statistics.median(true_ranks) if true_ranks else math.inf
    rank1_fraction = rank1_count / trial_count if trial_count else 0.0
    pseudo_rank1_fraction = pseudo_rank1_count / trial_count if trial_count else 1.0
    gates = {
        "trials_at_least_96": trial_count >= 96,
        "pages_at_least_40": selected_pages >= 40,
        "true_rank1_fraction_at_least_0_35": rank1_fraction >= 0.35,
        "median_true_rank_at_most_3": median_rank <= 3,
        "pseudo_rank1_fraction_at_most_0_08": pseudo_rank1_fraction <= 0.08,
    }

    result = dict(corpus["metadata"])
    result.update({
        "source_sha256": sha256_file(path),
        "selection_hash_sha256": digest_json(
            [trial["hash"] for trial in trials]
        ),
        "true_rank_vector_sha256": digest_json(true_ranks),
        "pseudo_rank_vector_sha256": digest_json(pseudo_ranks),
        "true_rank_histogram": rank_histogram(true_ranks),
        "pseudo_rank_histogram": rank_histogram(pseudo_ranks),
        "true_rank1_count": rank1_count,
        "true_rank1_fraction": rank1_fraction,
        "median_true_inclusive_rank": median_rank,
        "pseudo_rank1_count": pseudo_rank1_count,
        "pseudo_rank1_fraction": pseudo_rank1_fraction,
        "gates": gates,
        "reading_pass": all(gates.values()),
    })
    return result


def write_report(payload: dict, path: Path) -> None:
    lines = [
        "# F69C001 prescore calibration",
        "",
        f"Decision: **{payload['decision']}**",
        "",
        "This target-blind control asks whether the frozen character model can",
        "recover the circular order of known seven-character prose words. No",
        "f69r target string or target locus was accessed or scored.",
        "",
        "| Reading | Trials | Pages | True rank 1 | Median rank | Pseudo rank 1 | Pass |",
        "|---|---:|---:|---:|---:|---:|:---:|",
    ]
    for reading, result in payload["readings"].items():
        lines.append(
            f"| {reading} | {result['selected_trials']} | "
            f"{result['selected_pages']} | "
            f"{result['true_rank1_count']}/{result['selected_trials']} "
            f"({result['true_rank1_fraction']:.3f}) | "
            f"{result['median_true_inclusive_rank']:.1f} | "
            f"{result['pseudo_rank1_count']}/{result['selected_trials']} "
            f"({result['pseudo_rank1_fraction']:.3f}) | "
            f"{'yes' if result['reading_pass'] else 'no'} |"
        )
    lines.extend([
        "",
        "All thresholds were registered before this run. A calibration failure",
        "forbids target scoring. A pass authorizes independent reconstruction",
        "only; it does not itself supply a Voynich meaning or translation.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if TARGET_ARTIFACT.exists():
        raise SystemExit("target artifact exists before blind calibration")
    start = time.perf_counter()
    reading_results = {
        reading: run_reading(reading, path)
        for reading, path in SOURCES.items()
    }
    decision = (
        "CALIBRATION_PASS"
        if all(result["reading_pass"] for result in reading_results.values())
        else "CALIBRATION_FAIL_TARGET_FORBIDDEN"
    )
    payload = {
        "experiment": "F69C001",
        "stage": "prescore_ordinary_word_calibration",
        "model": {
            "order": 2,
            "alpha": ALPHA,
            "alphabet_size": len(ALPHABET),
            "candidate_assignments": len(PERMUTATIONS),
            "dihedral_orbits": len(ORBIT_KEYS),
            "orientations_per_orbit": 12,
            "max_trials_per_reading": MAX_TRIALS,
            "max_trials_per_page": MAX_PER_PAGE,
        },
        "readings": reading_results,
        "all_readings_pass": all(
            result["reading_pass"] for result in reading_results.values()
        ),
        "target_artifact_absent_before_and_after": not TARGET_ARTIFACT.exists(),
        "decision": decision,
        "elapsed_seconds": time.perf_counter() - start,
        "claim_ceiling": (
            "calibration adequacy only; no target order, start, handedness, "
            "sound, lexeme, language, plaintext, or translation"
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS / "f69c001_prescore_calibration.json"
    report_path = RESULTS / "f69c001_prescore_calibration_report.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    write_report(payload, report_path)
    if TARGET_ARTIFACT.exists():
        raise SystemExit("target artifact appeared during blind calibration")
    print(json.dumps({
        "decision": decision,
        "elapsed_seconds": payload["elapsed_seconds"],
        "readings": {
            reading: {
                "trials": result["selected_trials"],
                "pages": result["selected_pages"],
                "true_rank1_fraction": result["true_rank1_fraction"],
                "median_true_rank": result["median_true_inclusive_rank"],
                "pseudo_rank1_fraction": result["pseudo_rank1_fraction"],
                "pass": result["reading_pass"],
            }
            for reading, result in reading_results.items()
        },
        "target_artifact_absent": not TARGET_ARTIFACT.exists(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
