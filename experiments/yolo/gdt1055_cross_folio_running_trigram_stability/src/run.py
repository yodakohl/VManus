#!/usr/bin/env python3
import csv
import hashlib
import itertools
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/yolo/gdt874_raw_multigroup_record_bridge/runtime/ATLAS.tsv'
SOURCE_SHA256 = '3b303196be0f3411de7b26d348f858cdda27c847a13c73d058292b3bce306bea'
READERS = ('ZL3b', 'IT2a', 'RF1b')


def physical_leaf(page: str) -> str:
    match = re.match(r'^(f\d+)[rv]', page)
    assert match, page
    return match.group(1)


def inventory(rows: list[dict]) -> tuple[dict, dict, dict]:
    lines = defaultdict(list)
    for row in rows:
        if row['kind'] == 'P':
            lines[(row['edition'], row['locus'], row['page'])].append(row)
    patterns = {reader: defaultdict(list) for reader in READERS}
    opportunities = {reader: {str(n): 0 for n in range(3, 7)} for reader in READERS}
    whole_lines = {}
    for (reader, locus, page), group_rows in lines.items():
        group_rows.sort(key=lambda r: int(r['source_group_index']))
        assert [int(r['source_group_index']) for r in group_rows] == list(range(1, len(group_rows) + 1))
        whole_lines[(reader, locus)] = [r['ivtff_group_raw'] for r in group_rows]
        for n in range(3, 7):
            for pos in range(len(group_rows) - n + 1):
                window = group_rows[pos:pos + n]
                if any(r['left_separator'] != 'DEFINITE_SPACE' for r in window[1:]):
                    continue
                opportunities[reader][str(n)] += 1
                gram = tuple(r['ivtff_group_raw'] for r in window)
                patterns[reader][(n, gram)].append((page, locus, pos + 1))
    return patterns, opportunities, whole_lines


def cross_page_pairs(patterns: dict) -> dict:
    output = {}
    for reader in READERS:
        pairs = []
        for (n, gram), occurrences in patterns[reader].items():
            for left, right in itertools.combinations(sorted(set(occurrences)), 2):
                if physical_leaf(left[0]) != physical_leaf(right[0]):
                    pairs.append({'n': n, 'groups': list(gram), 'left': list(left), 'right': list(right)})
        output[reader] = sorted(pairs, key=lambda r: (r['n'], r['groups'], r['left'], r['right']))
    return output


def main() -> int:
    manifest = json.loads((HERE / 'experiment.json').read_text())
    for item in manifest['inputs']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    if not SOURCE.exists():
        subprocess.run(['python3', str(ROOT / 'experiments/yolo/gdt874_raw_multigroup_record_bridge/src/run.py')], cwd=ROOT, check=True)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert source_hash == SOURCE_SHA256
    rows = list(csv.DictReader(SOURCE.open(newline=''), delimiter='\t'))
    assert all(row['edition'] in READERS and row['page'] not in ('f84', 'f84r') for row in rows)
    patterns, opportunities, whole_lines = inventory(rows)
    matches = cross_page_pairs(patterns)
    pair_sets = [{json.dumps(pair, sort_keys=True) for pair in matches[reader]} for reader in READERS]
    stable = [json.loads(value) for value in sorted(set.intersection(*pair_sets))]
    contexts = []
    for pair in stable:
        contexts.append({
            'groups': pair['groups'],
            'left': pair['left'],
            'right': pair['right'],
            'complete_lines': {
                reader: {
                    'left': whole_lines[(reader, pair['left'][1])],
                    'right': whole_lines[(reader, pair['right'][1])],
                }
                for reader in READERS
            },
        })
    result = {
        'experiment_id': 'GDT1055',
        'selection_status': 'post_discovery_complete_descriptive_audit',
        'source_sha256': source_hash,
        'scope': 'GDT874 fixed thirty-page raw P-line atlas',
        'opportunities': opportunities,
        'matches': matches,
        'all_reader_same_pair': stable,
        'stable_complete_line_contexts': contexts,
        'readers_are_alternate_transcriptions': True,
    }
    (HERE / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'cross_page_pairs': {reader: len(matches[reader]) for reader in READERS}, 'stable_all_reader_pairs': len(stable)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
