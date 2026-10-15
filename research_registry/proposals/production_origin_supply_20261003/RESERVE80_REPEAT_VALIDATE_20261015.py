"""Independent fixed-line source equality and two-state R_TOKEN check."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source_path = HERE / 'RESERVE80_REPEAT_SOURCE_20261015.json'
    packet = json.loads(source_path.read_bytes())
    assert packet['schema'] == 'reserve80-repeat-source-v1'
    assert packet['locus'] == 'f115r.17'
    for k in ('contract', 'extractor', 'rule_source'):
        assert sha(ROOT / packet[k]['path']) == packet[k]['sha256']
    contract = json.loads((ROOT / packet['contract']['path']).read_bytes())
    assert contract['scope']['locus'] == packet['locus']
    for r in contract['source_rule_primaries']:
        assert sha(ROOT / r['path']) == r['sha256']
    rules = json.loads((ROOT / packet['rule_source']['path']).read_bytes())
    assert 'All markers in that run share the argument.' in rules['composition'][1]
    local = json.loads((HERE / 'LOCAL_RELATION95_PLAN_20261015.json').read_bytes())
    assert any('markers within one maximal run share one argument' in s for s in local['retained'])
    eds = ('IT2a', 'ZL3b', 'RF1b')
    paths = {f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json'
             for ed in eds for ph in ('DISCOVERY', 'EVALUATION')}
    receipts = {r['path']: r['sha256'] for r in packet['sources']}
    assert set(receipts) == paths and len(packet['sources']) == 6
    originals = {}
    for rel in sorted(paths):
        assert sha(ROOT / rel) == receipts[rel]
        obj = json.loads((ROOT / rel).read_bytes())
        for line in obj['lines']:
            m = line['metadata']
            if m['locus'] != 'f115r.17':
                continue
            ed = m['edition']
            assert ed in eds and ed not in originals and rel.endswith('_' + ed + '.json')
            originals[ed] = {'source': rel, 'group_columns': obj['group_columns'], 'line': line}
    assert set(originals) == set(packet['readers']) == set(eds)
    expected = 'qol cheey qotchy daiin daiin cheocthy dolkeedy qotaiin chol oteeedchey okeedain'.split()
    reviewed = []
    for ed in eds:
        r = packet['readers'][ed]
        assert r['status'] == 'PRESENT' and r['records'] == [originals[ed]]
        record = originals[ed]
        m = record['line']['metadata']
        assert m['kind'] == 'P' and m['page'] == 'f115r'
        gs = [dict(zip(record['group_columns'], a)) for a in record['line']['groups']]
        assert len(gs) == int(m['source_group_count']) == 11
        assert [int(g['source_group_index']) for g in gs] == list(range(1, 12))
        assert [g['ivtff_group_raw'] for g in gs] == expected
        assert all(len(a) == len(record['group_columns']) for a in record['line']['groups'])
        markers = set(rules['free_markers'])
        assert gs[2]['ivtff_group_raw'] not in markers | set(rules['bound_forms'])
        assert gs[5]['ivtff_group_raw'] not in markers
        assert all(g[k] == 'DEFINITE_SPACE' for g in gs[2:6] for k in ('left_separator', 'right_separator'))
        assert r['all_source_conditions_hold'] and all(r['source_conditions'].values())
        reviewed.append({'reader': ed, 'head_id': gs[2]['source_group_id'],
                         'run_ids': [g['source_group_id'] for g in gs[3:5]],
                         'full_record_equal': True, 'maximal_marker_run': True})
    scenarios = []
    for initial in ('AVAILABLE', 'COMMITTED'):
        taken = initial == 'COMMITTED'
        trace = []
        for ordinal in (1, 2):
            if taken:
                trace.append({'commitment': ordinal, 'outcome': 'INVALID_ALREADY_COMMITTED'})
                break
            trace.append({'commitment': ordinal, 'outcome': 'SUCCESS_NOW_COMMITTED'})
            taken = True
        assert trace[-1]['outcome'] == 'INVALID_ALREADY_COMMITTED'
        scenarios.append({'initial': initial, 'trace': trace, 'complete_run_valid': False})
    out = {'status': 'R_TOKEN_CONDITIONAL_CONJUNCTION_CONTRADICTED', 'source_validation': 'PASS',
           'source_packet_sha256': sha(source_path), 'validator_sha256': sha(Path(__file__)),
           'source_files': 6, 'complete_lines': reviewed, 'state_cases': scenarios,
           'scope': 'Exact fixed whole-line replay and conditional same-argument, two-distinct-commitment logic. No physical resource identity, noun or marker meaning established.',
           'preserved': ['Original R80 per-construction model is not refuted.',
                         'No general resource, imperative, numeral or cipher exclusion.',
                         'Idempotent restatement is not selected; no canonical delta/SET writer is rescued.',
                         'Alternate readers concern one manuscript; no new image, corpus census, raw TSV query or fresh confirmation.']}
    (HERE / 'RESERVE80_REPEAT_RESULT_20261015.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'source_validation': 'PASS', 'readers': len(reviewed)}))

if __name__ == '__main__':
    main()
