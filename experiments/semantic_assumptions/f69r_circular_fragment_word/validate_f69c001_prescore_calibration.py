#!/usr/bin/env python3
"""Nonimporting scalar reconstruction of the F69C001 prescore calibration."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULT = HERE / "results" / "f69c001_prescore_calibration.json"
VALIDATION_REPORT = HERE / "results" / "f69c001_prescore_validation.md"
TARGET_ARTIFACT = HERE / "TARGET_RESULT.json"
RUNNER = HERE / "run_f69c001_prescore_calibration.py"
SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}

PAGE = re.compile(r"^<([^>.]+)>\s+<!(.*)>")
LOCUS = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
LOWER = re.compile(r"[a-z]+")
LETTERS = "abcdefghijklmnopqrstuvwxyz$"


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1 << 20), b""):
            state.update(data)
    return state.hexdigest()


def clean(raw: str) -> list[str]:
    raw = re.sub(r"\[([^:\]]+)(?::[^\]]*)?\]", lambda m: m.group(1), raw)
    raw = re.sub(r"\{[^}]*\}", "", raw)
    raw = re.sub(r"<[^>]*>", " ", raw)
    raw = raw.replace("?", "").replace("!", "").replace("*", "").replace("'", "")
    output = []
    for part in re.split(r"[\s.,;:=/\\|+\-]+", raw):
        normalized = re.sub(r"[^A-Za-z]", "", part).lower()
        if normalized:
            output.append(normalized)
    return output


def parse_source(path: Path) -> list[dict]:
    rows = []
    current_page = ""
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        page_match = PAGE.match(raw)
        if page_match:
            current_page = page_match.group(1).lower()
            continue
        line_match = LOCUS.match(raw)
        if not line_match:
            continue
        locus, code, _comment, text = line_match.groups()
        words = clean(text)
        if words:
            rows.append({
                "page": current_page,
                "locus": locus,
                "code": code,
                "kind": code[1] if len(code) > 1 else "",
                "words": words,
            })
    return rows


def cycle_key(sequence: tuple[int, ...]) -> tuple[int, ...]:
    candidates = []
    for base in (sequence, tuple(reversed(sequence))):
        for shift in range(len(base)):
            candidates.append(base[shift:] + base[:shift])
    return min(candidates)


ORDERS = list(itertools.permutations(range(6)))
GROUP_FOR = {order: cycle_key(order) for order in ORDERS}
GROUPS = sorted(set(GROUP_FOR.values()))


def events(surface: str) -> Counter:
    framed = "^^" + surface + "$"
    bag = Counter()
    for position in range(len(surface) + 1):
        bag[(framed[position:position + 2], framed[position + 2])] += 1
    return bag


def hash_json(item: object) -> str:
    encoded = json.dumps(
        item, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def split_surface(surface: str, pair: int) -> tuple[str, ...]:
    parts = []
    cursor = 0
    while cursor < 7:
        width = 2 if cursor == pair else 1
        parts.append(surface[cursor:cursor + width])
        cursor += width
    return tuple(parts)


def prepare(path: Path, reading: str) -> tuple[list[dict], dict, dict]:
    rows = parse_source(path)
    words_by_page = defaultdict(list)
    possible = defaultdict(list)
    for row in rows:
        if row["kind"] != "P" or row["page"].startswith("f69"):
            continue
        for number, surface in enumerate(row["words"]):
            if not LOWER.fullmatch(surface):
                continue
            words_by_page[row["page"]].append(surface)
            if len(surface) != 7:
                continue
            identity = f"{reading}|{row['page']}|{row['locus']}|{number}|{surface}"
            raw = hashlib.sha256(identity.encode("ascii")).digest()
            pair = int.from_bytes(raw[0:8], "big") % 6
            parts = split_surface(surface, pair)
            if len(parts) != 6 or len(set(parts)) != 6:
                continue
            possible[row["page"]].append({
                "page": row["page"], "locus": row["locus"],
                "number": number, "surface": surface, "parts": parts,
                "raw": raw, "hex": raw.hex(),
            })

    limited = []
    for page in sorted(possible):
        ordered = sorted(
            possible[page],
            key=lambda x: (x["raw"], x["locus"], x["number"], x["surface"]),
        )
        limited.extend(ordered[:2])
    chosen = sorted(
        limited,
        key=lambda x: (
            x["raw"], x["page"], x["locus"], x["number"], x["surface"]
        ),
    )[:128]
    facts = {
        "parsed_rows": len(rows),
        "training_pages": len(words_by_page),
        "training_words": sum(map(len, words_by_page.values())),
        "eligible_occurrences_before_page_cap": sum(map(len, possible.values())),
        "eligible_pages_before_page_cap": len(possible),
        "page_limited_occurrences": len(limited),
        "selected_trials": len(chosen),
        "selected_pages": len({item["page"] for item in chosen}),
    }
    return chosen, dict(words_by_page), facts


def corpus_tables(words_by_page: dict) -> dict:
    total_events = Counter()
    total_words = Counter()
    page_events = {}
    page_words = {}
    for page, words in words_by_page.items():
        word_bag = Counter(words)
        event_bag = Counter()
        for word, amount in word_bag.items():
            for event, multiplicity in events(word).items():
                event_bag[event] += amount * multiplicity
        page_words[page] = word_bag
        page_events[page] = event_bag
        total_words.update(word_bag)
        total_events.update(event_bag)
    return {
        "total_events": total_events, "total_words": total_words,
        "page_events": page_events, "page_words": page_words,
    }


def reconstruct_model(tables: dict, page: str, surfaces: set[str]) -> tuple[dict, dict]:
    counts = dict(tables["total_events"])
    for event, amount in tables["page_events"][page].items():
        counts[event] = counts.get(event, 0) - amount
    for surface in surfaces:
        remaining = (
            tables["total_words"][surface]
            - tables["page_words"][page][surface]
        )
        if remaining:
            for event, multiplicity in events(surface).items():
                counts[event] = counts.get(event, 0) - remaining * multiplicity
    counts = {event: value for event, value in counts.items() if value > 0}
    contexts = Counter()
    for (context, _symbol), amount in counts.items():
        contexts[context] += amount
    return counts, contexts


def likelihood(surface: str, counts: dict, contexts: dict) -> float:
    value = 0.0
    for (context, symbol), multiplicity in events(surface).items():
        top = counts.get((context, symbol), 0) + 0.5
        bottom = contexts.get(context, 0) + 0.5 * len(LETTERS)
        value += multiplicity * math.log(top / bottom)
    return value / (len(surface) + 1)


def trial_ranks(item: dict, tables: dict) -> tuple[int, int]:
    parts = item["parts"]
    surfaces = {
        "".join(parts[position] for position in order) for order in ORDERS
    }
    counts, contexts = reconstruct_model(tables, item["page"], surfaces)
    group_scores = {group: -math.inf for group in GROUPS}
    for order in ORDERS:
        surface = "".join(parts[position] for position in order)
        value = likelihood(surface, counts, contexts)
        group = GROUP_FOR[order]
        group_scores[group] = max(group_scores[group], value)
    truth = cycle_key(tuple(range(6)))
    true_value = group_scores[truth]
    true_rank = sum(value >= true_value for value in group_scores.values())
    alternatives = [group for group in GROUPS if group != truth]
    selection = int.from_bytes(item["raw"][8:16], "big") % len(alternatives)
    pseudo_value = group_scores[alternatives[selection]]
    pseudo_rank = sum(value >= pseudo_value for value in group_scores.values())
    return true_rank, pseudo_rank


def histogram(ranks: list[int]) -> dict[str, int]:
    counts = Counter(ranks)
    return {str(value): counts[value] for value in range(1, 61)}


def rebuild(path: Path, reading: str) -> dict:
    chosen, pages, facts = prepare(path, reading)
    tables = corpus_tables(pages)
    pairs = [trial_ranks(item, tables) for item in chosen]
    true = [pair[0] for pair in pairs]
    pseudo = [pair[1] for pair in pairs]
    count = len(chosen)
    rank1 = sum(value == 1 for value in true)
    pseudo1 = sum(value == 1 for value in pseudo)
    median = statistics.median(true) if true else math.inf
    true_rate = rank1 / count if count else 0.0
    pseudo_rate = pseudo1 / count if count else 1.0
    gates = {
        "trials_at_least_96": count >= 96,
        "pages_at_least_40": facts["selected_pages"] >= 40,
        "true_rank1_fraction_at_least_0_35": true_rate >= 0.35,
        "median_true_rank_at_most_3": median <= 3,
        "pseudo_rank1_fraction_at_most_0_08": pseudo_rate <= 0.08,
    }
    facts.update({
        "source_sha256": file_hash(path),
        "selection_hash_sha256": hash_json([item["hex"] for item in chosen]),
        "true_rank_vector_sha256": hash_json(true),
        "pseudo_rank_vector_sha256": hash_json(pseudo),
        "true_rank_histogram": histogram(true),
        "pseudo_rank_histogram": histogram(pseudo),
        "true_rank1_count": rank1,
        "true_rank1_fraction": true_rate,
        "median_true_inclusive_rank": median,
        "pseudo_rank1_count": pseudo1,
        "pseudo_rank1_fraction": pseudo_rate,
        "gates": gates,
        "reading_pass": all(gates.values()),
    })
    return facts


def main() -> None:
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    check("720 labeled assignments", len(ORDERS) == 720)
    check("60 dihedral orbits", len(GROUPS) == 60)
    sizes = Counter(GROUP_FOR.values())
    check("12 orientations in every orbit", set(sizes.values()) == {12})
    check("tie-inclusive rank guard", sum(x >= 4.0 for x in [4.0, 4.0, 3.0]) == 2)
    check("target artifact absent before reconstruction", not TARGET_ARTIFACT.exists())

    reconstructed = {
        reading: rebuild(path, reading) for reading, path in SOURCES.items()
    }
    exact_fields = [
        "parsed_rows", "training_pages", "training_words",
        "eligible_occurrences_before_page_cap",
        "eligible_pages_before_page_cap", "page_limited_occurrences",
        "selected_trials", "selected_pages", "source_sha256",
        "selection_hash_sha256", "true_rank_vector_sha256",
        "pseudo_rank_vector_sha256", "true_rank_histogram",
        "pseudo_rank_histogram", "true_rank1_count",
        "median_true_inclusive_rank", "pseudo_rank1_count", "gates",
        "reading_pass",
    ]
    float_fields = ["true_rank1_fraction", "pseudo_rank1_fraction"]
    for reading in SOURCES:
        actual = stored["readings"][reading]
        expected = reconstructed[reading]
        check(
            f"{reading} exact aggregates and digests",
            all(actual[field] == expected[field] for field in exact_fields),
        )
        check(
            f"{reading} exact rates",
            all(math.isclose(actual[field], expected[field], rel_tol=0.0,
                             abs_tol=1e-15) for field in float_fields),
        )

    expected_pass = all(result["reading_pass"] for result in reconstructed.values())
    expected_decision = (
        "CALIBRATION_PASS" if expected_pass
        else "CALIBRATION_FAIL_TARGET_FORBIDDEN"
    )
    check("global gate and decision", (
        stored["all_readings_pass"] == expected_pass
        and stored["decision"] == expected_decision
    ))
    check("stored target-absence guard", stored["target_artifact_absent_before_and_after"] is True)
    check("runner contains no target locus identifier", not re.search(
        r"f69r\.(?:44|45|46|47|48|49)(?!\d)",
        RUNNER.read_text(encoding="utf-8"), re.I,
    ))
    check("target artifact absent after reconstruction", not TARGET_ARTIFACT.exists())

    VALIDATION_REPORT.write_text(
        "# F69C001 prescore independent validation\n\n"
        f"Status: **PASS — {len(checks)} checks**\n\n"
        "A nonimporting scalar implementation independently reconstructed the "
        "manual-source parser, deterministic samples, page and candidate-surface "
        "exclusions, all 720 assignments, the exact 60-orbit quotient, true and "
        "pseudo ranks, every aggregate, every gate, and the global decision. "
        "The target artifact was absent before and after validation.\n\n"
        "This validates calibration adequacy only; it supplies no target order, "
        "start, handedness, sound, lexeme, language, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS",
        "checks": len(checks),
        "decision": expected_decision,
        "target_artifact_absent": not TARGET_ARTIFACT.exists(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
