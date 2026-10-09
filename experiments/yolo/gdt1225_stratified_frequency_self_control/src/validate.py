#!/usr/bin/env python3
"""Separate regex/page-bucket reconstruction; imports neither runner nor metrics."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import csv, hashlib, io, json, random, re, subprocess

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'


def main():
    started = datetime.now(timezone.utc).isoformat()
    spec = json.loads((D / 'src/SPEC.json').read_text())
    for path, value in json.loads((A / 'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value, path
    allowed = json.loads((ROOT / spec['scope_spec']).read_text())['allowed']
    assert len(set(allowed)) == len(allowed) == 179
    assert all(not p.startswith('f84') and p != 'f116v' for p in allowed)
    receipts = []

    def query(path, columns):
        command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
        for page in allowed:
            command += ['--allow', page]
        command += ['--columns', columns]
        call = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
        receipts.append({'source': path, 'columns': columns, 'receipt': call.stderr.strip(),
                         'output_sha256': hashlib.sha256(call.stdout.encode()).hexdigest()})
        return csv.DictReader(io.StringIO(call.stdout), delimiter='\t')

    meta = {}
    for row in query(spec['metadata_source'], 'page,edition,source_group_index,locus,section,hand,currier'):
        key = row['edition'] + '|' + row['locus'] + '|G' + str(int(row['source_group_index'])).zfill(3)
        assert key not in meta
        meta[key] = row
    # Literal list, not the old parsing code or its alphabet constant.
    signs = 'a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
    assert signs == spec['working_alphabet']
    pattern = re.compile('|'.join(re.escape(x) for x in sorted(signs, key=lambda x: (-len(x), x))))
    page_buckets = defaultdict(lambda: defaultdict(list))
    page_set = set()
    value_sets = {field: set() for field in spec['stratum_fields']}
    seen = set()
    good_words = {}
    for row in query(spec['source'], 'page,edition,locus,source_group_index,kind,left_separator,right_separator,ivtff_group_raw'):
        if row['kind'] != 'P':
            continue
        key = row['edition'] + '|' + row['locus'] + '|G' + str(int(row['source_group_index'])).zfill(3)
        assert key not in seen
        seen.add(key)
        assert key in meta and row['page'] == meta[key]['page']
        page_set.add(row['page'])
        for field in spec['stratum_fields']:
            value_sets[field].add(meta[key][field])
        word = row['ivtff_group_raw']
        if word not in good_words:
            parts = pattern.findall(word)
            good_words[word] = bool(parts) and ''.join(parts) == word
        if not good_words[word] or row['left_separator'] not in ['LINE_START', 'DEFINITE_SPACE'] or row['right_separator'] not in ['LINE_END', 'DEFINITE_SPACE']:
            continue
        page_buckets[row['edition']][row['page']].append((row['locus'], int(row['source_group_index']), key, word,
                                                       tuple(meta[key][f] for f in spec['stratum_fields'])))
    for by_page in page_buckets.values():
        for entries in by_page.values():
            entries.sort(key=lambda r: (r[0], r[1]))
    targets = json.loads((ROOT / spec['reference']).read_text())
    old = json.loads((ROOT / spec['prior_control']).read_text())
    old_ids = json.loads((ROOT / spec['anchor_ids']).read_text())
    assert sorted(page_buckets) == sorted(targets['targets'])
    assert len(page_set) == old['prose_page_universe'] == 179
    populations = {ed: sum(map(len, by_page.values())) for ed, by_page in page_buckets.items()}
    assert populations == old['eligible_groups']
    assert populations == {ed: v['eligible_groups'] for ed, v in targets['scope'].items()}

    def collect(ed, ordered_pages, field_index=None, value=None):
        histogram = {}
        selected_ids = []
        used = set()
        for page in ordered_pages:
            for entry in page_buckets[ed].get(page, []):
                if field_index is not None and entry[4][field_index] != value:
                    continue
                word = entry[3]
                histogram[word] = histogram.get(word, 0) + 1
                selected_ids.append(entry[2])
                used.add(page)
                if len(selected_ids) == spec['sample_groups']:
                    break
            if len(selected_ids) == spec['sample_groups']:
                break
        assert len(selected_ids) == 8000
        ntypes = len(histogram)
        ntop = sum(sorted(histogram.values())[-10:])
        target = targets['targets'][ed]
        info = {'types': ntypes, 'top10_count': ntop,
                'types_within': target['types'] - 400 <= ntypes <= target['types'] + 400,
                'top10_within': round(8000 * target['top10_share']) - 400 <= ntop <= round(8000 * target['top10_share']) + 400,
                'sample_ids_sha256': hashlib.sha256(json.dumps(selected_ids, separators=(',', ':')).encode()).hexdigest(),
                'pages_touched': len(used), 'last_group_id': selected_ids[-1]}
        return info, selected_ids

    # Compute full capacities even for cells that will remain unscored.
    actual_cells = []
    for ed in sorted(page_buckets):
        for fi, field in enumerate(spec['stratum_fields']):
            for value in sorted(value_sets[field]):
                total = sum(entry[4][fi] == value for entries in page_buckets[ed].values() for entry in entries)
                actual_cells.append({'reader': ed, 'field': field, 'value': value, 'eligible_groups': total,
                                     'capacity': 'SCOREABLE' if total >= 8000 else 'NO_CAPACITY', 'samples': []})
    anchor = {}
    for seed in [1174] + list(range(128)):
        pages = sorted(page_set)
        random.Random(seed).shuffle(pages)
        for ed in sorted(page_buckets):
            info, ids = collect(ed, pages)
            expected_old = old['anchor']['readers'][ed] if seed == 1174 else old['samples'][seed]['readers'][ed]
            assert info == expected_old
            if seed == 1174:
                assert ids == old_ids[ed]
                anchor[ed] = info
        if seed == 1174:
            continue
        for cell in actual_cells:
            if cell['capacity'] == 'NO_CAPACITY':
                continue
            fi = spec['stratum_fields'].index(cell['field'])
            info, _ = collect(cell['reader'], pages, fi, cell['value'])
            cell['samples'].append({'seed': seed, **info})
    for cell in actual_cells:
        if cell['capacity'] == 'NO_CAPACITY':
            cell['decision'] = 'NO_CAPACITY'
            continue
        samples = cell['samples']
        target = targets['targets'][cell['reader']]
        t = target['types']
        top = round(8000 * target['top10_share'])
        successes = len([x for x in samples if x['types_within'] and x['top10_within']])
        cell.update(joint_passes=successes,
                    types_range=[min(x['types'] for x in samples), max(x['types'] for x in samples)],
                    top10_range=[min(x['top10_count'] for x in samples), max(x['top10_count'] for x in samples)],
                    directional_failures={'types_low': len([x for x in samples if x['types'] < t-400]),
                                          'types_high': len([x for x in samples if x['types'] > t+400]),
                                          'top10_low': len([x for x in samples if x['top10_count'] < top-400]),
                                          'top10_high': len([x for x in samples if x['top10_count'] > top+400])},
                    decision='WITHIN_FIXED_OPERATIONAL_GATE' if successes >= 122 else 'BELOW_FIXED_OPERATIONAL_GATE')
    result = json.loads((A / 'RESULT.json').read_text())
    assert actual_cells == result['cells']
    assert anchor == result['anchor'] and populations == result['eligible_groups']
    assert len(seen) == result['metadata_joined_prose_groups'] and result['pooled_all128_reproduced']
    counts = {label: sum(c['capacity'] == label for c in actual_cells) for label in ['SCOREABLE', 'NO_CAPACITY']}
    failed = sum(c['decision'] == 'BELOW_FIXED_OPERATIONAL_GATE' for c in actual_cells)
    status = 'POOLED_FREQUENCY_BANDS_NOT_PORTABLE_TO_ALL_LARGE_STRATA' if failed else 'STRATIFIED_FREQUENCY_BANDS_NONREFUTED' if counts['SCOREABLE'] else 'NO_LARGE_STRATUM_CAPACITY'
    assert (status, counts['SCOREABLE'], counts['NO_CAPACITY'], failed) == (result['status'], result['scoreable_cells'], result['no_capacity_cells'], result['failed_cells'])
    answer = {'status': 'PASS', 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'scientific_status': status, 'all_cells': len(actual_cells), 'scoreable_cells': counts['SCOREABLE'],
              'failed_cells': failed, 'no_capacity_cells': counts['NO_CAPACITY'],
              'joined_prose_groups': len(seen), 'pooled128and_anchor_reproduced': True,
              'independent_regex_page_bucket_counts_every_id_hash_and_decision': True,
              'scope': 'Same-author independent implementation, not independent native or semantic confirmation.',
              'projections': receipts}
    (A / 'VALIDATION.json').write_text(json.dumps(answer, indent=2)+'\n')
    print(json.dumps({k: v for k, v in answer.items() if k != 'projections'}, indent=2))


if __name__ == '__main__':
    main()
