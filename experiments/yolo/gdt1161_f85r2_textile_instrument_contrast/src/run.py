#!/usr/bin/env python3
"""Account for frozen manual observations. No automatic image interpretation."""
import hashlib
import json
from pathlib import Path
B = Path(__file__).resolve().parents[1]
R = B.parents[2]
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    spec = json.loads((B/'SPEC.json').read_text())
    images = json.loads((B/'src/IMAGE_SOURCES.json').read_text())['images']
    allowed = {x['path'] for x in images}
    for x in images:
        assert digest(R/x['path']) == x['sha256']
    packets = []
    for name in spec['observers']:
        d = json.loads((B/'artifacts'/('OBSERVER_'+name+'.json')).read_text())
        assert d['observer'] == name
        assert set(d['features']) == set(spec['features'])
        assert d['recorded_utc'] != 'REPLACE' and d['prior_exposure'] != 'Describe honestly'
        for v in d['features'].values():
            assert v['value'] in spec['values'] and v['image'] in allowed
            assert v['visible'] and v['uncertain']
            assert type(v['usable_entire_object_area']) is bool
            if v['value'] == 'ABSENT':
                assert v['usable_entire_object_area'], 'absence without usable object view'
        packets.append(d)
    rows = []
    for k in spec['features']:
        vals = [p['features'][k]['value'] for p in packets]
        rows.append({'feature': k, 'ROOT': vals[0], 'B': vals[1], 'agree': len(set(vals)) == 1})
    positive = all(p['features'][k]['value'] == 'PRESENT' for p in packets for k in spec['textile_required'])
    negative = all(p['features']['E_vessel']['value'] == 'PRESENT' and p['features']['E_frame']['value'] == 'ABSENT' and p['features']['E_frame']['usable_entire_object_area'] for p in packets)
    assert not (positive and negative)
    status = 'TEXTILE_JOINT_SUPPORTED' if positive else 'TEXTILE_JOINT_CONTRADICTED' if negative else 'NO_DISTINCTIVE_TEXTILE_SUPPORT_OR_CAPACITY'
    inputs = [B/'SPEC.json',B/'src/IMAGE_SOURCES.json',B/'artifacts/OBSERVER_ROOT.json',B/'artifacts/OBSERVER_B.json']
    result = {'experiment':'GDT1161','status':status,'features':rows,'source_alignment':spec['source_alignment'],'confirmed_words':0,'independent_confirmation_leaves':0,'new_target_admissions':0,'claim_ceiling':'Fixed exploratory visual tool account only; no translation or copying claim.','bindings':{str(p.relative_to(R)):digest(p) for p in inputs}}
    (B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(status)
if __name__ == '__main__':
    main()
