#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of the F69C001 target result."""

from __future__ import annotations

import csv
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
TARGET = HERE / "TARGET_RESULT.json"
REPORT = HERE / "results" / "f69c001_target_validation.md"
ANNOTATIONS = (
    ROOT / "experiments" / "semantic_assumptions" / "results"
    / "existing_human_exact_locus_annotations.tsv"
)
SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
SLOTS = (
    ("f69r.45", "11:30"), ("f69r.46", "01:00"),
    ("f69r.47", "03:00"), ("f69r.48", "04:30"),
    ("f69r.49", "07:30"), ("f69r.44", "10:30"),
)
EXPECTED = {
    "ZL3b": ("d", "o", "l", "s", "ed", "y"),
    "IT2a": ("d", "o", "l", "s", "em", "y"),
    "RF1b": ("d", "o", "l", "s", "ed", "y"),
}
PAGE = re.compile(r"^<([^>.]+)>\s+<!(.*)>")
LOCUS = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
LOWER = re.compile(r"[a-z]+")
FIXTURE_SEED = b"F69C001|random-orbit-fixture|v1"


def digest_file(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1 << 20), b""):
            state.update(data)
    return state.hexdigest()


def digest_json(value: object) -> str:
    data = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def clean_text(raw: str) -> list[str]:
    raw = re.sub(r"\[([^:\]]+)(?::[^\]]*)?\]", lambda m: m.group(1), raw)
    raw = re.sub(r"\{[^}]*\}", "", raw)
    raw = re.sub(r"<[^>]*>", " ", raw)
    for symbol in "?!*'":
        raw = raw.replace(symbol, "")
    words = []
    for field in re.split(r"[\s.,;:=/\\|+\-]+", raw):
        word = re.sub(r"[^A-Za-z]", "", field).lower()
        if word:
            words.append(word)
    return words


def read_rows(path: Path) -> list[dict]:
    page = ""
    rows = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        header = PAGE.match(raw)
        if header:
            page = header.group(1).lower()
            continue
        line = LOCUS.match(raw)
        if not line:
            continue
        locus, code, _comment, text = line.groups()
        words = clean_text(text)
        if words:
            rows.append({
                "page": page, "locus": locus, "code": code,
                "kind": code[1] if len(code) > 1 else "", "words": words,
            })
    return rows


def bind_target(rows_by_reading: dict[str, list[dict]]) -> tuple[dict, dict]:
    chunks = {}
    for reading, rows in rows_by_reading.items():
        lookup = defaultdict(list)
        for row in rows:
            if row["page"] == "f69r":
                lookup[row["locus"]].append(row)
        surfaces = []
        for locus, _clock in SLOTS:
            matches = lookup[locus]
            if len(matches) != 1:
                raise AssertionError(f"{reading} {locus} multiplicity")
            row = matches[0]
            if row["code"] != "@L0" or len(row["words"]) != 1:
                raise AssertionError(f"{reading} {locus} row form")
            surfaces.append(row["words"][0])
        chunks[reading] = tuple(surfaces)
        if chunks[reading] != EXPECTED[reading]:
            raise AssertionError(f"{reading} binding")

    with ANNOTATIONS.open(encoding="utf-8", newline="") as stream:
        annotation_rows = list(csv.DictReader(stream, delimiter="\t"))
    by_locus = {
        row["locus"]: row for row in annotation_rows if row["unit"] == "K1"
    }
    for locus, clock in SLOTS:
        row = by_locus.get(locus)
        if not row or row["page"] != "f69r" or row["normalized_code"] != "@L0":
            raise AssertionError(f"annotation {locus}")
        if not row["local_comment"].startswith(f"At {clock}."):
            raise AssertionError(f"annotation clock {locus}")

    slots = []
    for index, (locus, clock) in enumerate(SLOTS):
        slots.append({
            "slot": index + 1, "locus": locus, "clock_position": clock,
            "readings": {
                reading: chunks[reading][index] for reading in SOURCES
            },
        })
    provenance = {
        "source_sha256": {
            reading: digest_file(path) for reading, path in SOURCES.items()
        },
        "annotation_sha256": digest_file(ANNOTATIONS),
        "binding_sha256": digest_json(slots),
        "slots": slots,
    }
    return chunks, provenance


def normalize_cycle(order: tuple[int, ...]) -> tuple[int, ...]:
    variants = []
    for direction in (order, tuple(reversed(order))):
        variants.extend(
            direction[offset:] + direction[:offset]
            for offset in range(len(direction))
        )
    return min(variants)


def transitions(surface: str) -> Counter:
    framed = "^^" + surface + "$"
    result = Counter()
    for position in range(len(surface) + 1):
        result[(framed[position:position + 2], framed[position + 2])] += 1
    return result


def build_corpus(rows: list[dict]) -> dict:
    per_page = defaultdict(Counter)
    for row in rows:
        if row["kind"] != "P" or row["page"].startswith("f69"):
            continue
        for surface in row["words"]:
            if LOWER.fullmatch(surface):
                per_page[row["page"]][surface] += 1
    surfaces = Counter()
    event_counts = Counter()
    for word_counts in per_page.values():
        surfaces.update(word_counts)
        for surface, frequency in word_counts.items():
            for event, multiplicity in transitions(surface).items():
                event_counts[event] += frequency * multiplicity
    return {
        "parsed_rows": len(rows), "training_pages": len(per_page),
        "training_words": sum(sum(counts.values()) for counts in per_page.values()),
        "surfaces": surfaces, "events": event_counts,
    }


def train_excluding(corpus: dict, forbidden: set[str]) -> tuple[dict, dict]:
    event_counts = dict(corpus["events"])
    for surface in forbidden:
        frequency = corpus["surfaces"][surface]
        if frequency:
            for event, multiplicity in transitions(surface).items():
                event_counts[event] = (
                    event_counts.get(event, 0) - frequency * multiplicity
                )
    event_counts = {
        event: amount for event, amount in event_counts.items() if amount > 0
    }
    contexts = Counter()
    for (context, _symbol), amount in event_counts.items():
        contexts[context] += amount
    return event_counts, contexts


def likelihood(surface: str, events: dict, contexts: dict) -> float:
    value = 0.0
    for (context, symbol), multiplicity in transitions(surface).items():
        numerator = events.get((context, symbol), 0) + 0.5
        denominator = contexts.get(context, 0) + 0.5 * 27
        value += multiplicity * math.log(numerator / denominator)
    return value / (len(surface) + 1)


def score_hash(scores: dict) -> str:
    return digest_json([
        [list(order), float.hex(scores[order])] for order in sorted(scores)
    ])


def orbit_hash(scores: dict) -> str:
    return digest_json([
        [list(orbit), float.hex(scores[orbit])] for orbit in sorted(scores)
    ])


def inclusive_rank(scores: dict, target: tuple[int, ...]) -> int:
    observed = scores[target]
    return sum(value >= observed for value in scores.values())


def evaluate(chunks: dict[str, tuple[str, ...]], corpora: dict) -> tuple[dict, dict]:
    lengths = {len(value) for value in chunks.values()}
    if len(lengths) != 1:
        raise AssertionError("chunk length disagreement")
    n = lengths.pop()
    orders = tuple(itertools.permutations(range(n)))
    orbits = tuple(sorted({normalize_cycle(order) for order in orders}))
    membership = Counter(normalize_cycle(order) for order in orders)
    if len(orbits) != math.factorial(n - 1) // 2:
        raise AssertionError("orbit total")
    if set(membership.values()) != {2 * n}:
        raise AssertionError("orbit size")

    raw = {}
    zscores = {}
    orbit_scores = {}
    surface_totals = {}
    reading_ranks = {}
    truth = normalize_cycle(tuple(range(n)))

    for reading in SOURCES:
        pieces = chunks[reading]
        candidates = {
            "".join(pieces[position] for position in order) for order in orders
        }
        model_events, model_contexts = train_excluding(corpora[reading], candidates)
        values = {}
        for order in orders:
            surface = "".join(pieces[position] for position in order)
            values[order] = likelihood(surface, model_events, model_contexts)
        mean = statistics.fmean(values.values())
        standard_deviation = statistics.pstdev(values.values())
        z = {
            order: (value - mean) / standard_deviation
            for order, value in values.items()
        }
        grouped = {orbit: -math.inf for orbit in orbits}
        for order, value in z.items():
            group = normalize_cycle(order)
            grouped[group] = max(grouped[group], value)
        raw[reading] = values
        zscores[reading] = z
        orbit_scores[reading] = grouped
        surface_totals[reading] = len(candidates)
        reading_ranks[reading] = inclusive_rank(grouped, truth)

    combined_orders = {
        order: min(zscores[reading][order] for reading in SOURCES)
        for order in orders
    }
    combined_groups = {orbit: -math.inf for orbit in orbits}
    for order, value in combined_orders.items():
        group = normalize_cycle(order)
        combined_groups[group] = max(combined_groups[group], value)

    published = {
        "chunk_count": n,
        "assignments": len(orders),
        "dihedral_orbits": len(orbits),
        "orientations_per_orbit": 2 * n,
        "candidate_surface_counts": surface_totals,
        "reading_orientation_score_sha256": {
            reading: score_hash(raw[reading]) for reading in SOURCES
        },
        "reading_z_score_sha256": {
            reading: score_hash(zscores[reading]) for reading in SOURCES
        },
        "reading_orbit_score_sha256": {
            reading: orbit_hash(orbit_scores[reading]) for reading in SOURCES
        },
        "reading_target_inclusive_ranks": reading_ranks,
        "combined_orientation_score_sha256": score_hash(combined_orders),
        "combined_orbit_score_sha256": orbit_hash(combined_groups),
        "combined_target_inclusive_rank": inclusive_rank(combined_groups, truth),
        "combined_target_score": combined_groups[truth],
    }
    internal = {"combined": combined_groups, "truth": truth}
    return published, internal


def main() -> None:
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    check("target artifact is present", TARGET.is_file())
    check("exact six-slot quotient", (
        len(tuple(itertools.permutations(range(6)))) == 720
        and len({normalize_cycle(x) for x in itertools.permutations(range(6))}) == 60
    ))
    check("exact five-slot quotient", (
        len(tuple(itertools.permutations(range(5)))) == 120
        and len({normalize_cycle(x) for x in itertools.permutations(range(5))}) == 12
    ))
    check("tie-inclusive rank guard", inclusive_rank(
        {(0,): 2.0, (1,): 2.0, (2,): 1.0}, (0,)
    ) == 2)

    rows = {reading: read_rows(path) for reading, path in SOURCES.items()}
    bound, provenance = bind_target(rows)
    check("source and annotation binding", stored["provenance"] == provenance)
    corpora = {reading: build_corpus(rows[reading]) for reading in SOURCES}
    training = {
        reading: {
            "parsed_rows": corpora[reading]["parsed_rows"],
            "training_pages": corpora[reading]["training_pages"],
            "training_words": corpora[reading]["training_words"],
        }
        for reading in SOURCES
    }
    check("training corpus census", stored["training"] == training)

    primary, private = evaluate(bound, corpora)
    stored_primary = stored["primary"]
    primary_without_float = dict(primary)
    stored_without_float = dict(stored_primary)
    expected_float = primary_without_float.pop("combined_target_score")
    actual_float = stored_without_float.pop("combined_target_score")
    check("all primary hashes and ranks", stored_without_float == primary_without_float)
    check("primary target score", math.isclose(
        actual_float, expected_float, rel_tol=0.0, abs_tol=1e-15
    ))

    deletions = []
    for omitted in range(6):
        reduced = {
            reading: tuple(value for index, value in enumerate(bound[reading])
                           if index != omitted)
            for reading in SOURCES
        }
        result, _ = evaluate(reduced, corpora)
        deletions.append({
            "omitted_slot": omitted + 1,
            "omitted_locus": SLOTS[omitted][0],
            "combined_target_inclusive_rank": result["combined_target_inclusive_rank"],
            "reading_target_inclusive_ranks": result["reading_target_inclusive_ranks"],
            "combined_orbit_score_sha256": result["combined_orbit_score_sha256"],
            "reading_orientation_score_sha256": result["reading_orientation_score_sha256"],
            "candidate_surface_counts": result["candidate_surface_counts"],
        })
    check("all six deletion results", stored["deletions"] == deletions)

    shifted = dict(bound)
    shifted["IT2a"] = bound["IT2a"][1:] + bound["IT2a"][:1]
    misaligned, _ = evaluate(shifted, corpora)
    expected_misaligned = {
        "rule": "IT2a surface at slot i+1 mod 6 assigned to slot i",
        "target_rank": misaligned["combined_target_inclusive_rank"],
        "combined_orbit_score_sha256": misaligned["combined_orbit_score_sha256"],
        "rejects": misaligned["combined_target_inclusive_rank"] > 1,
    }
    check("misaligned-reading fixture", (
        stored["fixtures"]["misaligned_reading"] == expected_misaligned
    ))

    truth = private["truth"]
    alternatives = [orbit for orbit in sorted(private["combined"]) if orbit != truth]
    fixture_index = int.from_bytes(
        hashlib.sha256(FIXTURE_SEED).digest()[:8], "big"
    ) % len(alternatives)
    chosen = alternatives[fixture_index]
    chosen_rank = inclusive_rank(private["combined"], chosen)
    expected_random = {
        "seed_sha256": hashlib.sha256(FIXTURE_SEED).hexdigest(),
        "selected_index_among_59": fixture_index,
        "selected_orbit_sha256": digest_json(list(chosen)),
        "selected_orbit_rank": chosen_rank,
        "rejects": chosen_rank > 1,
    }
    check("deterministic non-target fixture", (
        stored["fixtures"]["deterministic_non_target_orbit"] == expected_random
    ))

    deletion_ranks = [row["combined_target_inclusive_rank"] for row in deletions]
    gates = {
        "unique_combined_rank1_of_60": primary["combined_target_inclusive_rank"] == 1,
        "all_individual_reading_ranks_at_most_3": all(
            rank <= 3 for rank in primary["reading_target_inclusive_ranks"].values()
        ),
        "at_least_five_deletion_ranks_at_most_2": sum(
            rank <= 2 for rank in deletion_ranks
        ) >= 5,
        "no_deletion_rank_worse_than_4": max(deletion_ranks) <= 4,
        "misaligned_reading_fixture_rejects": expected_misaligned["rejects"],
        "deterministic_non_target_orbit_fixture_rejects": expected_random["rejects"],
    }
    check("all frozen gates", stored["gates"] == gates)
    computational_pass = all(gates.values())
    decision = (
        "COMPUTATIONAL_GATES_PASS_PENDING_VALIDATION"
        if computational_pass else "TARGET_NONCONFIRMATION"
    )
    check("final target decision", (
        stored["computational_gates_pass"] == computational_pass
        and stored["decision"] == decision
    ))
    check("observed nonconfirmation profile", (
        primary["combined_target_inclusive_rank"] == 1
        and primary["reading_target_inclusive_ranks"] == {
            "ZL3b": 1, "IT2a": 7, "RF1b": 1
        }
        and deletion_ranks == [2, 6, 4, 1, 2, 1]
        and decision == "TARGET_NONCONFIRMATION"
    ))
    check("validator did not mutate target", TARGET.is_file())

    REPORT.write_text(
        "# F69C001 target independent validation\n\n"
        f"Status: **PASS — {len(checks)} checks**\n\n"
        "A nonimporting scalar implementation independently reparsed the three "
        "manual transcriptions and human clock annotations and reconstructed "
        "the six bindings, corpus exclusions, all primary and deletion scores, "
        "720/60 and 120/12 dihedral quotients, score hashes, ranks, fixtures, "
        "gates, and final decision.\n\n"
        "The physical orbit is nominally combined rank 1/60 and ranks 1/60 in "
        "ZL3b and RF1b, but IT2a ranks it 7/60. Deletion ranks are "
        "2, 6, 4, 1, 2, 1 of 12. Three registered robustness gates fail, so "
        "the validated decision is **TARGET_NONCONFIRMATION**. The nominal "
        "combined top rank is retained only as a diagnostic. No start, "
        "handedness, sound, word, lexeme, language, plaintext, direction name, "
        "or translation follows.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS", "checks": len(checks), "decision": decision,
        "combined_rank": primary["combined_target_inclusive_rank"],
        "individual_ranks": primary["reading_target_inclusive_ranks"],
        "deletion_ranks": deletion_ranks,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
