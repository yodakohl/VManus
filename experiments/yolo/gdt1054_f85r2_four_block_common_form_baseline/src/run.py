#!/usr/bin/env python3
import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'
BLOCKS = ('N', 'E', 'S', 'W')
READERS = ('ZL3b', 'IT2a', 'RF1b')
SEED = 1054
TRIALS = 100000


def allocation_probability(sizes: list[int], count: int) -> float:
    denominator = math.comb(sum(sizes), count)
    numerator = 0
    for first in itertools.product(range(1, count + 1), repeat=3):
        last = count - sum(first)
        allotment = (*first, last)
        if last < 1 or any(n > size for n, size in zip(allotment, sizes)):
            continue
        numerator += math.prod(math.comb(size, n) for size, n in zip(sizes, allotment))
    return numerator / denominator


def shuffle_any_four(words: list[str], sizes: list[int], trials: int, seed: int) -> int:
    candidates = {word for word, count in Counter(words).items() if count >= 4}
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        deck = words.copy()
        rng.shuffle(deck)
        cursor = 0
        common = candidates.copy()
        for size in sizes:
            common.intersection_update(deck[cursor:cursor + size])
            cursor += size
            if not common:
                break
        hits += bool(common)
    return hits


def main() -> int:
    manifest = json.loads((HERE / 'experiment.json').read_text())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == manifest['inputs'][0]['sha256']
    rows = list(csv.DictReader(SOURCE.open(newline=''), delimiter='\t'))
    assert all(row['edition'] in READERS and row['block'] in (*BLOCKS, 'OUTSIDE') for row in rows)
    results = {}
    for reader_index, reader in enumerate(READERS):
        groups = {block: [row['ivtff_group_raw'] for row in rows if row['edition'] == reader and row['block'] == block] for block in BLOCKS}
        sizes = [len(groups[block]) for block in BLOCKS]
        words = [word for block in BLOCKS for word in groups[block]]
        counts = Counter(words)
        common = set.intersection(*(set(groups[block]) for block in BLOCKS))
        hits = shuffle_any_four(words, sizes, TRIALS, SEED + reader_index)
        results[reader] = {
            'block_sizes': dict(zip(BLOCKS, sizes)),
            'total_groups': len(words),
            'aiin_by_block': {block: groups[block].count('aiin') for block in BLOCKS},
            'frequent_wholes': {word: n for word, n in sorted(counts.items()) if n >= 4},
            'all_four_wholes': sorted(common),
            'aiin_preselected_occupancy_probability': allocation_probability(sizes, counts['aiin']),
            'any_four_shuffle_hits': hits,
            'any_four_shuffle_fraction': hits / TRIALS,
        }
    output = {
        'experiment_id': 'GDT1054',
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'selection_status': 'post_selection_exploratory_diagnostic',
        'seed': SEED,
        'trials_per_reader': TRIALS,
        'readers_are_alternate_transcriptions': True,
        'results': results,
    }
    path = HERE / 'artifacts/RESULT.json'
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps({reader: (result['aiin_preselected_occupancy_probability'], result['any_four_shuffle_fraction']) for reader, result in results.items()}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
