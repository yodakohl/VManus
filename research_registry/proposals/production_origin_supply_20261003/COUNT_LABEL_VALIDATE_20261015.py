"""Independent equality audit of three fixed existing label loci, no source query."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDS = ('IT2a', 'ZL3b', 'RF1b')
LOCI = ('f66r.82', 'f82v.3', 'f89v1.24')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    packet_path = HERE / 'COUNT_LABEL_SOURCE_20261015.json'
    packet = json.loads(packet_path.read_bytes())
    assert packet['schema'] == 'count-label-source-v1'
    assert packet['status'] == 'EXACT_EXISTING_LABEL_PROJECTION_NO_OWNER_OR_COUNT_BINDING'
    assert packet['selected_loci'] == list(LOCI)
    assert set(packet['readers']) == set(EDS)
    expected_paths = {f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json'
                      for phase in ('DISCOVERY', 'EVALUATION') for ed in EDS}
    receipts = {r['path']: r['sha256'] for r in packet['sources']}
    assert len(packet['sources']) == len(receipts) == 6
    assert set(receipts) == expected_paths
    for field in ('selection_plan', 'extractor'):
        receipt = packet[field]
        assert sha(ROOT / receipt['path']) == receipt['sha256']
    plan = json.loads((ROOT / packet['selection_plan']['path']).read_bytes())
    assert set(plan['source_selection']['label_loci']) == set(LOCI)
    original = {}
    for relative in sorted(expected_paths):
        path = ROOT / relative
        assert sha(path) == receipts[relative]
        source = json.loads(path.read_bytes())
        for line in source['lines']:
            meta = line['metadata']
            if meta['locus'] not in LOCI:
                continue
            key = meta['edition'], meta['locus']
            assert key not in original
            assert meta['kind'] == 'L' and meta['page'] == meta['locus'].split('.')[0]
            assert f"_{meta['edition']}.json" in relative
            original[key] = (relative, source['group_columns'], line)
    assert set(original) == {(ed, loc) for ed in EDS for loc in LOCI}
    summaries = {}
    rows = []
    for ed in EDS:
        view = packet['readers'][ed]
        assert set(view['loci']) == set(LOCI)
        raw_count = 0
        for loc in LOCI:
            entry = view['loci'][loc]
            assert entry['status'] == 'PRESENT' and len(entry['records']) == 1
            saved = entry['records'][0]
            relative, columns, line = original[ed, loc]
            assert saved == {'source': relative, 'group_columns': columns, 'line': line}
            groups = [dict(zip(columns, g)) for g in line['groups']]
            assert all(len(g) == len(columns) for g in line['groups'])
            assert int(line['metadata']['source_group_count']) == len(groups)
            assert [int(g['source_group_index']) for g in groups] == list(range(1, len(groups) + 1))
            assert len({g['source_group_id'] for g in groups}) == len(groups)
            raw_count += len(groups)
            rows.append({'reader': ed, 'locus': loc,
                         'raw_groups': [g['ivtff_group_raw'] for g in groups],
                         'metadata_and_all_group_cells_equal': True})
        assert view['present_loci'] == 3 and view['raw_groups'] == raw_count
        summaries[ed] = {'loci': 3, 'raw_groups': raw_count}
    forms = {(r['reader'], r['locus']): r['raw_groups'] for r in rows}
    assert 'daiin' not in forms['IT2a', 'f66r.82']
    assert all('daiin' in forms[e, 'f66r.82'] for e in ('ZL3b', 'RF1b'))
    assert forms['IT2a', 'f82v.3'] == forms['RF1b', 'f82v.3'] == ['daiin', 'oty']
    assert forms['ZL3b', 'f82v.3'] == ['daiinoty']
    assert forms['IT2a', 'f89v1.24'] == ['opal', 'daiin']
    assert forms['ZL3b', 'f89v1.24'] == forms['RF1b', 'f89v1.24'] == ['opaldaiin']
    result = {
        'status': 'PASS_EXACT_CACHED_LABEL_PROJECTION_ONLY',
        'packet_sha256': sha(packet_path), 'validator_sha256': sha(Path(__file__)),
        'source_files': 6, 'reader_locus_records': 9, 'readers': summaries,
        'reviewed_records': rows,
        'method': 'No extractor import. Independently locate complete records in six pinned caches and compare every saved metadata/group/column value; verify exact ID scope, completeness and reader contrasts.',
        'conclusions': [
            'No one-word exact DAIIN label is supplied by these records. Exact DAIIN forms occur inside multi-group label loci; fused strings remain separate raw forms.',
            'Initial DAIIN at f82v.3 does not satisfy the existing written-X postfix construction without a separately stated argument realization. It does not by itself refute all DAIIN syntax or CountSpec.',
            'The IT opal daiin sequence is an available written-head candidate, not a selected OPAL meaning, licensed opaldaiin expansion or counted group.',
            'kind L and exact source equality establish neither caption ownership nor group membership or individuation.',
            'No numerical rejection, numeral value, semantic confirmation, new image admission, fresh holdout or universal postfix rescue follows.'
        ],
        'limits': 'Existing exposed records only. No images, source downloads, raw TSV query, neighboring-locus output, corpus census or empirical CountSpec test. Original source authenticity and visual label ownership were not independently verified.'
    }
    (HERE / 'COUNT_LABEL_VALIDATION_20261015.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'records': 9, 'readers': summaries}))

if __name__ == '__main__':
    main()
