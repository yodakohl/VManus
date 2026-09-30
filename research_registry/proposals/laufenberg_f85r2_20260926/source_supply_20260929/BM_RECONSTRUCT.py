#!/usr/bin/env python3
"""Reproduce an admitted f56r paragraph reading; no decoder or semantic score."""
import csv
import hashlib
import io
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW = ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
COLS = ('source_group_id,edition,locus,page,kind,grammar_scope,code,'
        'source_group_index,source_group_count,paragraph_start,paragraph_end,'
        'left_separator,right_separator,ivtff_group_raw')

def build():
    assert 'f56r' in {r['page'] for r in csv.DictReader(ALLOW.open(), delimiter='\t')}
    projected = subprocess.check_output([
        str(ROOT / 'vmanus-exp'), 'query-tsv', str(SOURCE), '--selector', 'page',
        '--allow', 'f56r', '--columns', COLS], text=True)
    rows = list(csv.DictReader(io.StringIO(projected), delimiter='\t'))
    lines = defaultdict(list)
    for r in rows:
        assert r['page'] == 'f56r' and r['kind'] == 'P'
        lines[(r['edition'], int(r['locus'].split('.')[1]))].append(r)
    units = []
    rendered = ['# BM — complete f56r native paragraphs and RF comparison windows',
                '', 'All groups retained; no translation or inferred sentence boundaries.']
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        assert {n for e, n in lines if e == edition} == set(range(1, 20))
        if edition != 'RF1b':
            starts = [n for (e, n), rs in lines.items() if e == edition
                      and {r['paragraph_start'] for r in rs} == {'1'}]
            ends = [n for (e, n), rs in lines.items() if e == edition
                    and {r['paragraph_end'] for r in rs} == {'1'}]
            assert starts == [1, 9] and ends == [8, 19]
        else:
            assert all(r['paragraph_start'] == r['paragraph_end'] == '0'
                       for r in rows if r['edition'] == edition)
        for label, lo, hi in [('A', 1, 8), ('B', 9, 19)]:
            unit = {'edition': edition, 'unit': label,
                    'boundary_basis': 'native_flags' if edition != 'RF1b' else 'aligned_window',
                    'lines': []}
            rendered += ['', f'## {edition} {label}: f56r.{lo}–{hi} ({unit["boundary_basis"]})', '']
            for n in range(lo, hi + 1):
                rs = sorted(lines[(edition, n)], key=lambda r: int(r['source_group_index']))
                assert [int(r['source_group_index']) for r in rs] == list(range(1, len(rs) + 1))
                assert {int(r['source_group_count']) for r in rs} == {len(rs)}
                unit['lines'].append({'locus': f'f56r.{n}', 'groups': rs})
                rendered.append(f'{n:02d}. ' + ' '.join(r['ivtff_group_raw'] for r in rs))
            unit['group_count'] = sum(len(x['groups']) for x in unit['lines'])
            units.append(unit)
    assert sum(u['group_count'] for u in units) == len(rows) == 301
    assert len({r['source_group_id'] for r in rows}) == len(rows)
    result = {'status': 'EXPLORATORY_COMPLETE_CONTEXT_NO_SELECTED_MEANING',
              'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'allowlist_sha256': hashlib.sha256(ALLOW.read_bytes()).hexdigest(),
              'projected_groups': len(rows), 'physical_leaf_count': 1,
              'native_paragraphs': 2, 'alternate_readings_independent': False,
              'units': [{k: v for k, v in u.items() if k != 'lines'} for u in units],
              'confirmed_words': 0, 'independent_confirmation_capacity': 0,
              'semantic_validation': False, 'significance_claim': False}
    return projected, units, '\n'.join(rendered) + '\n', result

if __name__ == '__main__':
    projected, units, rendered, result = build()
    (BASE / 'BM_F56_PROJECTED.tsv').write_text(projected)
    (BASE / 'BM_COMPLETE_CONTEXTS.json').write_text(json.dumps(units, indent=2) + '\n')
    (BASE / 'BM_COMPLETE_CONTEXTS.md').write_text(rendered)
    (BASE / 'BM_RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
