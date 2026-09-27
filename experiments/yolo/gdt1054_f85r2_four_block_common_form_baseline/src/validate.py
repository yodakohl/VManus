#!/usr/bin/env python3
import csv
import hashlib
import json
import math
import random
from collections import Counter
from itertools import combinations
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'


def probability_every_block(sizes: list[int], copies: int) -> float:
    total = sum(sizes)
    denominator = math.comb(total, copies)
    numerator = 0
    for omitted in range(5):
        for chosen in combinations(range(4), omitted):
            available = total - sum(sizes[i] for i in chosen)
            if available >= copies:
                numerator += (-1) ** omitted * math.comb(available, copies)
    return numerator / denominator


def independent_replay(words: list[str], sizes: list[int], trials: int, seed: int) -> int:
    rng = random.Random(seed)
    frequent = [w for w, count in Counter(words).items() if count >= 4]
    success = 0
    for _ in range(trials):
        copy = words[:]
        rng.shuffle(copy)
        slices = []
        left = 0
        for width in sizes:
            slices.append(set(copy[left:left + width]))
            left += width
        success += any(all(form in part for part in slices) for form in frequent)
    return success


def main() -> int:
    record = json.loads((HERE / 'artifacts/RESULT.json').read_text())
    manifest = json.loads((HERE / 'experiment.json').read_text())
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert source_hash == record['source_sha256'] == manifest['inputs'][0]['sha256']
    assert record['experiment_id'] == 'GDT1054'
    assert record['selection_status'] == 'post_selection_exploratory_diagnostic'
    assert record['readers_are_alternate_transcriptions'] is True
    assert record['trials_per_reader'] == 100000 and record['seed'] == 1054
    rows = list(csv.DictReader(SOURCE.open(newline=''), delimiter='\t'))
    assert len(rows) == 473
    checks = 0
    for offset, reader in enumerate(('ZL3b', 'IT2a', 'RF1b')):
        sample = [r for r in rows if r['edition'] == reader and r['block'] in ('N', 'E', 'S', 'W')]
        blocks = [[r['ivtff_group_raw'] for r in sample if r['block'] == side] for side in ('N', 'E', 'S', 'W')]
        words = [word for block in blocks for word in block]
        sizes = [len(block) for block in blocks]
        observed = record['results'][reader]
        assert observed['total_groups'] == len(words)
        assert observed['block_sizes'] == dict(zip(('N', 'E', 'S', 'W'), sizes))
        assert observed['aiin_by_block'] == dict(zip(('N', 'E', 'S', 'W'), [block.count('aiin') for block in blocks]))
        counts = Counter(words)
        assert observed['frequent_wholes'] == {word: n for word, n in sorted(counts.items()) if n >= 4}
        assert observed['all_four_wholes'] == sorted(set.intersection(*(set(block) for block in blocks)))
        assert abs(observed['aiin_preselected_occupancy_probability'] - probability_every_block(sizes, counts['aiin'])) < 1e-12
        hits = independent_replay(words, sizes, record['trials_per_reader'], record['seed'] + offset)
        assert observed['any_four_shuffle_hits'] == hits
        assert observed['any_four_shuffle_fraction'] == hits / record['trials_per_reader']
        checks += 8
    verification = {'experiment_id': 'GDT1054', 'status': 'PASS', 'checks': checks, 'source_sha256': source_hash, 'scope': 'mechanical_and_null_replay_only'}
    (HERE / 'artifacts/VALIDATION.json').write_text(json.dumps(verification, indent=2, sort_keys=True) + '\n')
    print(json.dumps(verification))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
