#!/usr/bin/env python3
"""Independent raw-window reconstruction; no arithmetic score."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'
PREREG_SHA = '39a29a975d6944d8a0a5fd6f3c855dd38bae6415792ec03770d621c9fb75e0e5'
SPEC_SHA = '51fe285cc6b83b154be386b09018e10ce377993fa03fb41773a5d0803ae99842'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def tail(row):
    word = row['ivtff_group_raw']
    if not word or any(c < 'a' or c > 'z' for c in word):
        return None
    if row['clean_ascii_fragments'] != word or row['clean_ascii_fragment_count'] != '1':
        return None
    for n in range(4):
        ending = 'a' + 'i' * n + 'n'
        if word.endswith(ending) and len(word) > len(ending):
            return word[:-len(ending)], n
    return None


def windows(rows):
    result = []
    for start in range(len(rows) - 2):
        triple = rows[start:start + 3]
        if any(r['kind'] != 'P' for r in triple):
            continue
        indices = [int(r['source_group_index']) for r in triple]
        if indices != list(range(indices[0], indices[0] + 3)):
            continue
        if any(triple[j]['right_separator'] != 'DEFINITE_SPACE' or triple[j + 1]['left_separator'] != 'DEFINITE_SPACE' for j in (0, 1)):
            continue
        parsed = [tail(r) for r in triple]
        if any(p is None for p in parsed) or len({p[0] for p in parsed}) != 1:
            continue
        result.append({'head': parsed[0][0], 'raw_groups': [r['ivtff_group_raw'] for r in triple], 'minim_runs': [p[1] for p in parsed], 'indices': indices})
    return result


def reconstruct(rows, editions):
    grouped = defaultdict(list)
    ids = set()
    for row in rows:
        assert row['source_group_id'] not in ids
        ids.add(row['source_group_id'])
        grouped[row['page'], row['locus'], row['edition']].append(row)
    ws = {}
    for key, group in grouped.items():
        group.sort(key=lambda r: int(r['source_group_index']))
        assert [int(r['source_group_index']) for r in group] == list(range(1, len(group) + 1)), key
        assert all(int(r['source_group_count']) == len(group) for r in group), key
        assert all(group[i]['right_separator'] == group[i + 1]['left_separator'] for i in range(len(group) - 1)), key
        ws[key] = windows(group)
    candidates = []
    for (page, locus, edition), found in sorted(ws.items()):
        if edition != 'ZL3b':
            continue
        for w in found:
            joins = {}
            for e in editions:
                matches = [x['indices'] for x in ws.get((page, locus, e), []) if x['raw_groups'] == w['raw_groups']]
                joins[e] = {'match_count': len(matches), 'indices': matches}
            candidates.append({'page': page, 'locus': locus, 'head': w['head'], 'raw_groups': w['raw_groups'], 'minim_runs': w['minim_runs'], 'zl_indices': w['indices'], 'joins': joins, 'consensus': all(j['match_count'] == 1 for j in joins.values())})
    return candidates


def synthetic_checks():
    def row(word, i):
        return {'ivtff_group_raw': word, 'clean_ascii_fragments': word, 'clean_ascii_fragment_count': '1', 'kind': 'P', 'source_group_index': str(i), 'left_separator': 'DEFINITE_SPACE', 'right_separator': 'DEFINITE_SPACE'}
    clean = [row(w, i + 1) for i, w in enumerate(['xan', 'xain', 'xaiin'])]
    assert len(windows(clean)) == 1
    altered = [dict(r) for r in clean]
    altered[1]['ivtff_group_raw'] = '<!gap>xain'
    assert not windows(altered)
    altered = [dict(r) for r in clean]
    altered[1]['right_separator'] = altered[2]['left_separator'] = 'DRAWING_INTERRUPTION'
    assert not windows(altered)
    interstitial = [row(w, i + 1) for i, w in enumerate(['xan', 'zz', 'xain', 'xaiin'])]
    assert not windows(interstitial)
    repeated = [row('xain', i + 1) for i in range(4)]
    assert len(windows(repeated)) == 2
    assert tail(row('aiin', 1)) is None
    assert tail(row('xaiiiin', 1)) is None
    assert len(windows([row(w, i + 1) for i, w in enumerate(['xan', 'yain', 'xaiin'])])) == 0
    return 8


def main():
    assert sha(E / 'PREREGISTRATION.md') == PREREG_SHA
    assert sha(E / 'src/SPEC.json') == SPEC_SHA
    s = read(E / 'src/SPEC.json')
    assert s['sealed_data'] == {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'}
    assert len(s['selectors']) == len(set(s['selectors'])) == 163
    assert not any(x.startswith('f84') for x in s['selectors'])
    assert sha(ROOT / s['allowlist_source']) == s['allowlist_sha256']
    assert sha(ROOT / s['printed_loci_source']) == s['printed_loci_source_sha256']
    printed = sorted(set(re.findall(r'f\d+[rv]\d*\.\d+', (ROOT / s['printed_loci_source']).read_text())))
    assert printed == s['printed_loci']
    excluded = sorted(set(re.match(r'f\d+', x).group() for x in printed))
    assert excluded == s['excluded_physical_leaves']
    allow = [r['page'] for r in csv.DictReader((ROOT / s['allowlist_source']).open(), delimiter='\t')]
    assert s['selectors'] == [p for p in allow if re.match(r'f\d+', p).group() not in excluded]
    cmd = ['./vmanus-exp', 'query-tsv', s['source'], '--selector', 'page']
    for page in s['selectors']:
        cmd.extend(['--allow', page])
    cmd.extend(['--columns', ','.join(s['columns']), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r'])
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(x[len('GUARD_STATS '):]) for x in p.stderr.splitlines() if x.startswith('GUARD_STATS ')]
    assert len(stats) == 1
    rows = list(csv.DictReader(io.StringIO(p.stdout), delimiter='\t'))
    assert len(rows) == stats[0]['selected'] > 0
    assert all(r['page'] in s['selectors'] for r in rows)
    expected = reconstruct(rows, s['editions'])
    actual = read(A / 'CANDIDATES.json')
    def key(x):
        return x['page'], x['locus'], x['zl_indices']
    assert sorted(actual, key=key) == sorted(expected, key=key)
    loci = {(x['page'], x['locus']) for x in expected}
    retained = [r for r in rows if (r['page'], r['locus']) in loci]
    assert read(A / 'SOURCE_ROWS.json') == retained
    receipt = read(A / 'SOURCE_RECEIPT.json')
    assert receipt['source'] == s['source']
    assert receipt['projection_sha256'] == hashlib.sha256(p.stdout.encode()).hexdigest()
    assert receipt['guard_stats'] == stats[0]
    assert receipt['retained_rows'] == len(retained)
    assert receipt['preregistration_sha256'] == PREREG_SHA and receipt['spec_sha256'] == SPEC_SHA
    primary = [x for x in expected if x['consensus']]
    counts = {'zl_candidate_windows': len(expected), 'consensus_windows': len(primary), 'consensus_lines': len({(x['page'], x['locus']) for x in primary}), 'physical_leaves': len({re.match(r'f\d+', x['page']).group() for x in primary}), 'heads': len({x['head'] for x in primary})}
    result = read(A / 'RESULT.json')
    assert all(result[k] == v for k, v in counts.items())
    triage = counts['consensus_lines'] >= 20 and counts['physical_leaves'] >= 5 and counts['heads'] >= 2
    status = 'DESIGN_REVIEW_CAPACITY_ONLY' if triage else 'STOP_INSUFFICIENT_IMMEDIATE_TRIPLE_CAPACITY'
    assert result['status'] == status and result['experiment_id'] == 'GDT880'
    n = synthetic_checks()
    print(json.dumps({'experiment_id': 'GDT880', 'status': 'PASS', 'counts': counts, 'synthetic_checks': n, 'scope': 'guarded source replay, exact raw windows, joins and resource-triage logic; no arithmetic or meaning', 'errors': []}))


if __name__ == '__main__':
    main()
