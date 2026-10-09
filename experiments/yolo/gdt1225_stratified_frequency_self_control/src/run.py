#!/usr/bin/env python3
"""Fixed portability check; no writer, band, or category tuning."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv, hashlib, io, json, random, subprocess, sys

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'
sys.path.insert(0, str(ROOT / 'experiments/yolo/gdt1174_ten_scribes_forward_comparison/src'))
import metrics


def digest(values):
    return hashlib.sha256(json.dumps(values, separators=(',', ':')).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(row):
    return row['edition'], row['locus'], int(row['source_group_index'])


def group_id(row):
    return f"{row['edition']}|{row['locus']}|G{int(row['source_group_index']):03d}"


def guarded(path, columns, allowed):
    cmd = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in allowed:
        cmd.extend(['--allow', page])
    cmd.extend(['--columns', ','.join(columns)])
    call = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    receipt = {'command': cmd, 'receipt': call.stderr.strip(),
               'output_sha256': hashlib.sha256(call.stdout.encode()).hexdigest()}
    return list(csv.DictReader(io.StringIO(call.stdout), delimiter='\t')), receipt


def main():
    assert not (A / 'RESULT.json').exists(), 'Do not replace original results.'
    started = datetime.now(timezone.utc).isoformat()
    s = json.loads((D / 'src/SPEC.json').read_text())
    for rel, expected in json.loads((A / 'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert sha(ROOT / rel) == expected, rel
    allowed = json.loads((ROOT / s['scope_spec']).read_text())['allowed']
    assert len(allowed) == 179 and len(set(allowed)) == 179
    assert not any(p.startswith('f84') or p == 'f116v' for p in allowed)
    rows, r1 = guarded(s['source'], ['edition', 'page', 'locus', 'kind', 'source_group_index',
                                   'ivtff_group_raw', 'left_separator', 'right_separator'], allowed)
    metadata, r2 = guarded(s['metadata_source'], ['edition', 'page', 'locus', 'source_group_index',
                                               'currier', 'section', 'hand'], allowed)
    meta = {}
    for row in metadata:
        key = identity(row)
        assert key not in meta, ('duplicate metadata', key)
        meta[key] = row
    prose = [r for r in rows if r['kind'] == 'P']
    assert len({identity(r) for r in prose}) == len(prose)
    pages = sorted({r['page'] for r in prose})
    values = {field: set() for field in s['stratum_fields']}
    eligible = defaultdict(list)
    parsed = {}
    for row in prose:
        key = identity(row)
        assert key in meta and meta[key]['page'] == row['page'], key
        for field in s['stratum_fields']:
            row[field] = meta[key][field]
            values[field].add(row[field])
        word = row['ivtff_group_raw']
        if word not in parsed:
            parsed[word] = bool(metrics.glyphs(word))
        if row['left_separator'] in ('DEFINITE_SPACE', 'LINE_START') and row['right_separator'] in ('DEFINITE_SPACE', 'LINE_END') and parsed[word]:
            eligible[row['edition']].append(row)
    target_file = json.loads((ROOT / s['reference']).read_text())
    target = target_file['targets']
    old = json.loads((ROOT / s['prior_control']).read_text())
    old_ids = json.loads((ROOT / s['anchor_ids']).read_text())
    assert set(eligible) == set(target)
    assert len(pages) == old['prose_page_universe'] == 179
    for ed, items in eligible.items():
        assert len(items) == target_file['scope'][ed]['eligible_groups'] == old['eligible_groups'][ed]

    def measure(items, ed):
        chosen = items[:s['sample_groups']]
        assert len(chosen) == s['sample_groups']
        counts = Counter(r['ivtff_group_raw'] for r in chosen)
        top = sum(sorted(counts.values(), reverse=True)[:10])
        ids = [group_id(r) for r in chosen]
        answer = {'types': len(counts), 'top10_count': top,
                  'types_within': abs(len(counts) - target[ed]['types']) <= s['count_tolerance'],
                  'top10_within': abs(top - round(s['sample_groups'] * target[ed]['top10_share'])) <= s['count_tolerance'],
                  'sample_ids_sha256': digest(ids), 'pages_touched': len({r['page'] for r in chosen}),
                  'last_group_id': ids[-1]}
        return answer, ids

    cells = []
    for ed, items in sorted(eligible.items()):
        for field in s['stratum_fields']:
            for value in sorted(values[field]):
                n = sum(r[field] == value for r in items)
                cells.append({'reader': ed, 'field': field, 'value': value, 'eligible_groups': n,
                              'capacity': 'SCOREABLE' if n >= s['sample_groups'] else 'NO_CAPACITY', 'samples': []})
    anchor = {}
    pooled_reproduced = []
    for seed in [s['reproduction_seed']] + s['seeds']:
        order = pages.copy()
        random.Random(seed).shuffle(order)
        rank = {page: i for i, page in enumerate(order)}
        ordered = {ed: sorted(items, key=lambda r: (rank[r['page']], r['locus'], int(r['source_group_index'])))
                   for ed, items in eligible.items()}
        pooled = {}
        for ed, items in sorted(ordered.items()):
            row, ids = measure(items, ed)
            pooled[ed] = row
            if seed == s['reproduction_seed']:
                assert ids == old_ids[ed]
                assert row == old['anchor']['readers'][ed]
            else:
                assert row == old['samples'][seed]['readers'][ed]
        if seed == s['reproduction_seed']:
            anchor = pooled
            continue
        pooled_reproduced.append(seed)
        for cell in cells:
            if cell['capacity'] == 'NO_CAPACITY':
                continue
            row, _ = measure([r for r in ordered[cell['reader']] if r[cell['field']] == cell['value']], cell['reader'])
            cell['samples'].append({'seed': seed, **row})
    for cell in cells:
        if cell['capacity'] == 'NO_CAPACITY':
            cell['decision'] = 'NO_CAPACITY'
            continue
        samples = cell['samples']
        passed = sum(r['types_within'] and r['top10_within'] for r in samples)
        ed = cell['reader']
        t = target[ed]['types']
        c = round(s['sample_groups'] * target[ed]['top10_share'])
        tol = s['count_tolerance']
        cell.update(joint_passes=passed,
                    types_range=[min(r['types'] for r in samples), max(r['types'] for r in samples)],
                    top10_range=[min(r['top10_count'] for r in samples), max(r['top10_count'] for r in samples)],
                    directional_failures={'types_low': sum(r['types'] < t-tol for r in samples),
                                          'types_high': sum(r['types'] > t+tol for r in samples),
                                          'top10_low': sum(r['top10_count'] < c-tol for r in samples),
                                          'top10_high': sum(r['top10_count'] > c+tol for r in samples)},
                    decision='WITHIN_FIXED_OPERATIONAL_GATE' if passed >= s['required_joint_passes_per_reader_stratum'] else 'BELOW_FIXED_OPERATIONAL_GATE')
    scoreable = [c for c in cells if c['capacity'] == 'SCOREABLE']
    failed = [c for c in scoreable if c['decision'] == 'BELOW_FIXED_OPERATIONAL_GATE']
    status = 'POOLED_FREQUENCY_BANDS_NOT_PORTABLE_TO_ALL_LARGE_STRATA' if failed else 'STRATIFIED_FREQUENCY_BANDS_NONREFUTED' if scoreable else 'NO_LARGE_STRATUM_CAPACITY'
    result = {'experiment': s['experiment'], 'status': status, 'fields': s['stratum_fields'],
              'sample_groups': s['sample_groups'], 'seeds': s['seeds'],
              'required_joint_passes_per_reader_stratum': s['required_joint_passes_per_reader_stratum'],
              'metadata_joined_prose_groups': len(prose), 'prose_page_universe': len(pages),
              'eligible_groups': {ed: len(items) for ed, items in sorted(eligible.items())},
              'pooled_all128_reproduced': pooled_reproduced == s['seeds'], 'anchor': anchor,
              'scoreable_cells': len(scoreable), 'failed_cells': len(failed),
              'no_capacity_cells': len(cells)-len(scoreable), 'cells': cells,
              'claim_ceiling': s['dependence'] + ' No cause, native value, source language, new band or old writer rescue.'}
    (A / 'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    (A / 'RUN_RECEIPT.json').write_text(json.dumps({'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
                                                 'projections': [r1, r2]}, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'scoreable_cells', 'failed_cells', 'no_capacity_cells', 'metadata_joined_prose_groups']}, indent=2))
    print(json.dumps([{k: v for k, v in c.items() if k != 'samples'} for c in scoreable], indent=2))


if __name__ == '__main__':
    main()
