#!/usr/bin/env python3
"""First and only frozen target run for F69C001."""

from __future__ import annotations

import csv
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
CALIBRATION = RESULTS / "f69c001_prescore_calibration.json"
CALIBRATION_VALIDATION = RESULTS / "f69c001_prescore_validation.md"
ANNOTATIONS = (
    ROOT / "experiments" / "semantic_assumptions" / "results"
    / "existing_human_exact_locus_annotations.tsv"
)
COMMON_DIR = ROOT / "archive_pre_reset_2026-08-06" / "semantic_assumptions"
sys.path.insert(0, str(COMMON_DIR))
from common import parse_rows  # noqa: E402


SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
SLOTS = (
    ("f69r.45", "11:30"),
    ("f69r.46", "01:00"),
    ("f69r.47", "03:00"),
    ("f69r.48", "04:30"),
    ("f69r.49", "07:30"),
    ("f69r.44", "10:30"),
)
EXPECTED = {
    "ZL3b": ("d", "o", "l", "s", "ed", "y"),
    "IT2a": ("d", "o", "l", "s", "em", "y"),
    "RF1b": ("d", "o", "l", "s", "ed", "y"),
}
ALPHABET_SIZE = 27
ALPHA = 0.5
ASCII_WORD = re.compile(r"[a-z]+")
RANDOM_FIXTURE_SEED = b"F69C001|random-orbit-fixture|v1"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_hash(value: object) -> str:
    data = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def canonical_cycle(order: tuple[int, ...]) -> tuple[int, ...]:
    candidates = []
    for base in (order, tuple(reversed(order))):
        for shift in range(len(base)):
            candidates.append(base[shift:] + base[:shift])
    return min(candidates)


def transition_bag(surface: str) -> Counter[tuple[str, str]]:
    framed = "^^" + surface + "$"
    return Counter(
        (framed[index:index + 2], framed[index + 2])
        for index in range(len(surface) + 1)
    )


def validate_binding() -> tuple[dict[str, tuple[str, ...]], dict]:
    bound: dict[str, tuple[str, ...]] = {}
    source_hashes = {}
    for reading, path in SOURCES.items():
        source_hashes[reading] = file_hash(path)
        by_locus = defaultdict(list)
        for row in parse_rows(path):
            if row.page == "f69r":
                by_locus[row.locus].append(row)
        words = []
        for locus, _position in SLOTS:
            matches = by_locus[locus]
            if len(matches) != 1:
                raise AssertionError(f"{reading} {locus} row multiplicity")
            row = matches[0]
            if row.code != "@L0" or len(row.words) != 1:
                raise AssertionError(f"{reading} {locus} is not one @L0 word")
            words.append(row.words[0])
        bound[reading] = tuple(words)
        if bound[reading] != EXPECTED[reading]:
            raise AssertionError(f"{reading} target binding mismatch")

    with ANNOTATIONS.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    annotation_rows = {row["locus"]: row for row in rows if row["unit"] == "K1"}
    for locus, position in SLOTS:
        row = annotation_rows.get(locus)
        if row is None or row["page"] != "f69r" or row["normalized_code"] != "@L0":
            raise AssertionError(f"annotation binding missing for {locus}")
        if not row["local_comment"].startswith(f"At {position}."):
            raise AssertionError(f"annotation clock mismatch for {locus}")

    binding_rows = [
        {
            "slot": index + 1,
            "locus": locus,
            "clock_position": position,
            "readings": {
                reading: bound[reading][index] for reading in SOURCES
            },
        }
        for index, (locus, position) in enumerate(SLOTS)
    ]
    provenance = {
        "source_sha256": source_hashes,
        "annotation_sha256": file_hash(ANNOTATIONS),
        "binding_sha256": json_hash(binding_rows),
        "slots": binding_rows,
    }
    return bound, provenance


def prose_tables(path: Path) -> dict:
    page_surfaces: dict[str, Counter[str]] = defaultdict(Counter)
    parsed_rows = 0
    for row in parse_rows(path):
        parsed_rows += 1
        if row.kind != "P" or row.page.startswith("f69"):
            continue
        for surface in row.words:
            if ASCII_WORD.fullmatch(surface):
                page_surfaces[row.page][surface] += 1

    total_surfaces = Counter()
    total_events: Counter[tuple[str, str]] = Counter()
    for word_bag in page_surfaces.values():
        total_surfaces.update(word_bag)
        for surface, frequency in word_bag.items():
            for event, multiplicity in transition_bag(surface).items():
                total_events[event] += frequency * multiplicity
    return {
        "parsed_rows": parsed_rows,
        "training_pages": len(page_surfaces),
        "training_words": sum(sum(bag.values()) for bag in page_surfaces.values()),
        "surface_counts": total_surfaces,
        "event_counts": total_events,
    }


def excluded_model(tables: dict, candidate_surfaces: set[str]) -> tuple[dict, dict]:
    counts = tables["event_counts"].copy()
    for surface in candidate_surfaces:
        frequency = tables["surface_counts"][surface]
        if frequency <= 0:
            continue
        for event, multiplicity in transition_bag(surface).items():
            counts[event] -= frequency * multiplicity
    counts = {event: value for event, value in counts.items() if value > 0}
    context_counts = Counter()
    for (context, _symbol), frequency in counts.items():
        context_counts[context] += frequency
    return counts, context_counts


def word_score(surface: str, event_counts: dict, context_counts: dict) -> float:
    score = 0.0
    for (context, symbol), multiplicity in transition_bag(surface).items():
        numerator = event_counts.get((context, symbol), 0) + ALPHA
        denominator = context_counts.get(context, 0) + ALPHA * ALPHABET_SIZE
        score += multiplicity * math.log(numerator / denominator)
    return score / (len(surface) + 1)


def reading_orientation_scores(chunks: tuple[str, ...], tables: dict,
                               orders: tuple[tuple[int, ...], ...]) -> tuple[dict, int]:
    candidates = {
        "".join(chunks[index] for index in order) for order in orders
    }
    events, contexts = excluded_model(tables, candidates)
    scores = {
        order: word_score(
            "".join(chunks[index] for index in order), events, contexts
        )
        for order in orders
    }
    return scores, len(candidates)


def score_digest(scores: dict[tuple[int, ...], float]) -> str:
    serial = [
        [list(order), float.hex(scores[order])] for order in sorted(scores)
    ]
    return json_hash(serial)


def orbit_digest(scores: dict[tuple[int, ...], float]) -> str:
    serial = [
        [list(orbit), float.hex(scores[orbit])] for orbit in sorted(scores)
    ]
    return json_hash(serial)


def rank_of(scores: dict[tuple[int, ...], float], target: tuple[int, ...]) -> int:
    target_value = scores[target]
    return sum(value >= target_value for value in scores.values())


def score_panel(chunks_by_reading: dict[str, tuple[str, ...]],
                tables_by_reading: dict[str, dict]) -> tuple[dict, dict]:
    sizes = {len(chunks) for chunks in chunks_by_reading.values()}
    if len(sizes) != 1:
        raise AssertionError("reading chunk counts disagree")
    size = sizes.pop()
    orders = tuple(itertools.permutations(range(size)))
    expected_orbits = math.factorial(size - 1) // 2
    orbits = tuple(sorted({canonical_cycle(order) for order in orders}))
    orbit_members = Counter(canonical_cycle(order) for order in orders)
    if len(orbits) != expected_orbits or set(orbit_members.values()) != {2 * size}:
        raise AssertionError("dihedral quotient mismatch")

    raw_by_reading = {}
    z_by_reading = {}
    candidate_counts = {}
    reading_orbit_scores = {}
    reading_ranks = {}
    target_orbit = canonical_cycle(tuple(range(size)))

    for reading, chunks in chunks_by_reading.items():
        raw, candidate_count = reading_orientation_scores(
            chunks, tables_by_reading[reading], orders
        )
        mean = statistics.fmean(raw.values())
        spread = statistics.pstdev(raw.values())
        if spread <= 0:
            raise AssertionError(f"zero score variance for {reading}")
        zscores = {order: (value - mean) / spread for order, value in raw.items()}
        orbit_scores = {orbit: -math.inf for orbit in orbits}
        for order, value in zscores.items():
            orbit = canonical_cycle(order)
            orbit_scores[orbit] = max(orbit_scores[orbit], value)
        raw_by_reading[reading] = raw
        z_by_reading[reading] = zscores
        candidate_counts[reading] = candidate_count
        reading_orbit_scores[reading] = orbit_scores
        reading_ranks[reading] = rank_of(orbit_scores, target_orbit)

    combined_orientations = {
        order: min(z_by_reading[reading][order] for reading in SOURCES)
        for order in orders
    }
    combined_orbits = {orbit: -math.inf for orbit in orbits}
    for order, value in combined_orientations.items():
        orbit = canonical_cycle(order)
        combined_orbits[orbit] = max(combined_orbits[orbit], value)

    public = {
        "chunk_count": size,
        "assignments": len(orders),
        "dihedral_orbits": len(orbits),
        "orientations_per_orbit": 2 * size,
        "candidate_surface_counts": candidate_counts,
        "reading_orientation_score_sha256": {
            reading: score_digest(raw) for reading, raw in raw_by_reading.items()
        },
        "reading_z_score_sha256": {
            reading: score_digest(zscores)
            for reading, zscores in z_by_reading.items()
        },
        "reading_orbit_score_sha256": {
            reading: orbit_digest(scores)
            for reading, scores in reading_orbit_scores.items()
        },
        "reading_target_inclusive_ranks": reading_ranks,
        "combined_orientation_score_sha256": score_digest(combined_orientations),
        "combined_orbit_score_sha256": orbit_digest(combined_orbits),
        "combined_target_inclusive_rank": rank_of(combined_orbits, target_orbit),
        "combined_target_score": combined_orbits[target_orbit],
    }
    private = {
        "combined_orbits": combined_orbits,
        "target_orbit": target_orbit,
    }
    return public, private


def preflight() -> None:
    assert math.factorial(6) == 720
    assert len({canonical_cycle(order) for order in itertools.permutations(range(6))}) == 60
    assert len({canonical_cycle(order) for order in itertools.permutations(range(5))}) == 12
    tied = {(0,): 4.0, (1,): 4.0, (2,): 3.0}
    assert rank_of(tied, (0,)) == 2
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    assert calibration["decision"] == "CALIBRATION_PASS"
    validation = CALIBRATION_VALIDATION.read_text(encoding="utf-8")
    assert "PASS — 15 checks" in validation


def write_report(payload: dict) -> None:
    primary = payload["primary"]
    deletion_ranks = [row["combined_target_inclusive_rank"]
                      for row in payload["deletions"]]
    lines = [
        "# F69C001 target result",
        "",
        f"Decision: **{payload['decision']}**",
        "",
        "The test asks whether the six f69r center fragments form an unusually",
        "ordinary-word-like circular order under the pre-registered internal",
        "character model. Rotation and reversal are quotiented, so this test",
        "cannot identify a start or reading direction.",
        "",
        f"- Combined target orbit rank: {primary['combined_target_inclusive_rank']}/60",
        "- Individual ranks: " + ", ".join(
            f"{reading} {rank}/60" for reading, rank in
            primary["reading_target_inclusive_ranks"].items()
        ),
        f"- Leave-one-slot-out ranks: {', '.join(map(str, deletion_ranks))}/12",
        f"- Misaligned-reading fixture rank: {payload['fixtures']['misaligned_reading']['target_rank']}/60",
        f"- Deterministic non-target fixture rank: {payload['fixtures']['deterministic_non_target_orbit']['selected_orbit_rank']}/60",
        "",
        "This first runner's result remains pending independent reconstruction",
        "if its computational gates pass. Under no outcome does it supply a",
        "sound, lexeme, language, plaintext, direction name, or translation.",
        "",
    ]
    (RESULTS / "f69c001_target_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    if TARGET_ARTIFACT.exists():
        raise SystemExit("F69C001 target artifact already exists; rerun forbidden")
    preflight()
    start = time.perf_counter()
    bound, provenance = validate_binding()
    tables = {reading: prose_tables(path) for reading, path in SOURCES.items()}

    primary, primary_private = score_panel(bound, tables)

    deletions = []
    for omitted in range(6):
        reduced = {
            reading: tuple(chunk for index, chunk in enumerate(chunks)
                           if index != omitted)
            for reading, chunks in bound.items()
        }
        result, _private = score_panel(reduced, tables)
        deletions.append({
            "omitted_slot": omitted + 1,
            "omitted_locus": SLOTS[omitted][0],
            "combined_target_inclusive_rank": result["combined_target_inclusive_rank"],
            "reading_target_inclusive_ranks": result["reading_target_inclusive_ranks"],
            "combined_orbit_score_sha256": result["combined_orbit_score_sha256"],
            "reading_orientation_score_sha256": result["reading_orientation_score_sha256"],
            "candidate_surface_counts": result["candidate_surface_counts"],
        })

    misaligned = dict(bound)
    misaligned["IT2a"] = bound["IT2a"][1:] + bound["IT2a"][:1]
    misaligned_result, _misaligned_private = score_panel(misaligned, tables)

    target_orbit = primary_private["target_orbit"]
    other_orbits = [
        orbit for orbit in sorted(primary_private["combined_orbits"])
        if orbit != target_orbit
    ]
    fixture_index = (
        int.from_bytes(hashlib.sha256(RANDOM_FIXTURE_SEED).digest()[:8], "big")
        % len(other_orbits)
    )
    selected_orbit = other_orbits[fixture_index]
    selected_rank = rank_of(primary_private["combined_orbits"], selected_orbit)

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
        "misaligned_reading_fixture_rejects": (
            misaligned_result["combined_target_inclusive_rank"] > 1
        ),
        "deterministic_non_target_orbit_fixture_rejects": selected_rank > 1,
    }
    computational_pass = all(gates.values())
    decision = (
        "COMPUTATIONAL_GATES_PASS_PENDING_VALIDATION"
        if computational_pass else "TARGET_NONCONFIRMATION"
    )
    payload = {
        "experiment": "F69C001",
        "stage": "first_frozen_target_run",
        "provenance": provenance,
        "training": {
            reading: {
                "parsed_rows": table["parsed_rows"],
                "training_pages": table["training_pages"],
                "training_words": table["training_words"],
            }
            for reading, table in tables.items()
        },
        "primary": primary,
        "deletions": deletions,
        "fixtures": {
            "misaligned_reading": {
                "rule": "IT2a surface at slot i+1 mod 6 assigned to slot i",
                "target_rank": misaligned_result["combined_target_inclusive_rank"],
                "combined_orbit_score_sha256": misaligned_result["combined_orbit_score_sha256"],
                "rejects": misaligned_result["combined_target_inclusive_rank"] > 1,
            },
            "deterministic_non_target_orbit": {
                "seed_sha256": hashlib.sha256(RANDOM_FIXTURE_SEED).hexdigest(),
                "selected_index_among_59": fixture_index,
                "selected_orbit_sha256": json_hash(list(selected_orbit)),
                "selected_orbit_rank": selected_rank,
                "rejects": selected_rank > 1,
            },
        },
        "gates": gates,
        "computational_gates_pass": computational_pass,
        "decision": decision,
        "elapsed_seconds": time.perf_counter() - start,
        "claim_ceiling": (
            "circular ordinary-word-likeness under one internal model only; "
            "no start, handedness, sound, word, root, lexeme, language, "
            "plaintext, direction name, or translation"
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    TARGET_ARTIFACT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(payload)
    print(json.dumps({
        "decision": decision,
        "combined_rank": primary["combined_target_inclusive_rank"],
        "individual_ranks": primary["reading_target_inclusive_ranks"],
        "deletion_ranks": deletion_ranks,
        "misaligned_fixture_rank": misaligned_result["combined_target_inclusive_rank"],
        "non_target_fixture_rank": selected_rank,
        "gates": gates,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
