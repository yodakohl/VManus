#!/usr/bin/env python3
import csv
import hashlib
import json
from collections import defaultdict
from itertools import combinations
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


def main() -> int:
    result = json.loads((HERE / 'artifacts/RESULT.json').read_text())
    manifest = json.loads((HERE / 'experiment.json').read_text())
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert digest == result['source_sha256'] == SOURCE_SHA256
    for item in manifest['inputs']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    assert result['experiment_id'] == 'GDT1055'
    assert result['selection_status'] == 'post_discovery_complete_descriptive_audit'
    assert result['readers_are_alternate_transcriptions'] is True
    reader_names = ('ZL3b', 'IT2a', 'RF1b')
    source_rows = list(csv.DictReader(SOURCE.open(newline=''), delimiter='\t'))
    by_line = defaultdict(list)
    for row in source_rows:
        assert row['edition'] in reader_names
        assert row['page'] not in ('f84', 'f84r')
        if row['kind'] == 'P':
            by_line[(row['edition'], row['source_row_index'], row['locus'], row['page'])].append(row)
    expected = {reader: [] for reader in reader_names}
    counts = {reader: {str(n): 0 for n in range(3, 7)} for reader in reader_names}
    word_index = {reader: defaultdict(list) for reader in reader_names}
    complete = {}
    for (reader, _, locus, page), rows in by_line.items():
        rows.sort(key=lambda row: int(row['source_group_index']))
        assert [int(row['source_group_index']) for row in rows] == list(range(1, len(rows) + 1))
        complete[(reader, locus)] = [row['ivtff_group_raw'] for row in rows]
        for width in (3, 4, 5, 6):
            for start in range(0, len(rows) - width + 1):
                part = rows[start:start + width]
                if not all(row['left_separator'] == 'DEFINITE_SPACE' for row in part[1:]):
                    continue
                counts[reader][str(width)] += 1
                key = (width, tuple(row['ivtff_group_raw'] for row in part))
                word_index[reader][key].append((page, locus, start + 1))
    for reader in reader_names:
        for (width, words), locations in word_index[reader].items():
            for a, b in combinations(sorted(set(locations)), 2):
                if a[0] != b[0]:
                    expected[reader].append({'n': width, 'groups': list(words), 'left': list(a), 'right': list(b)})
        expected[reader].sort(key=lambda row: (row['n'], row['groups'], row['left'], row['right']))
        assert result['opportunities'][reader] == counts[reader]
        assert result['matches'][reader] == expected[reader]
    intersection = set.intersection(*(set(json.dumps(x, sort_keys=True) for x in expected[reader]) for reader in reader_names))
    stable = [json.loads(x) for x in sorted(intersection)]
    assert result['all_reader_same_pair'] == stable
    assert len(stable) == 2
    assert all(row['n'] == 3 for row in stable)
    assert all(counts[reader][str(n)] > 0 for reader in reader_names for n in (3, 4, 5, 6))
    for row in result['stable_complete_line_contexts']:
        pair = next(x for x in stable if x['groups'] == row['groups'] and x['left'] == row['left'] and x['right'] == row['right'])
        for reader in reader_names:
            assert row['complete_lines'][reader]['left'] == complete[(reader, pair['left'][1])]
            assert row['complete_lines'][reader]['right'] == complete[(reader, pair['right'][1])]
    assert len(result['stable_complete_line_contexts']) == len(stable)
    validation = {'experiment_id': 'GDT1055', 'status': 'PASS', 'source_sha256': digest, 'reader_cross_page_counts': {r: len(expected[r]) for r in reader_names}, 'stable_all_reader_pairs': len(stable), 'scope': 'source_and_enumeration_only'}
    (HERE / 'artifacts/VALIDATION.json').write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
    print(json.dumps(validation))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
