#!/usr/bin/env python3
"""Frozen-input checks and complete positive-equation replay."""
import hashlib,itertools,json
from pathlib import Path
from source import load,tables,TRAVERSALS
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sp=BASE/'artifacts/SOURCE_INPUT.json';tp=BASE/'artifacts/TARGET_INPUT.json'
    assert sha(sp)=='7647eb754fd68d939d041d7a6a35e1711d1783f936f316a5f669b0f58f39846c'
    assert sha(tp)=='dfb5f1981b609fadaf4c93c406ad86042d928f60296d8010a022fe303033df6a'
    source=load(sp);target=json.loads(tp.read_text())
    counts={p:len(w) for p,w in target['panels'].items()}
    assert counts=={'CONSENSUS':0,'IT2a':6710,'RF1b':73,'ZL3b':142}
    for panel,ws in target['panels'].items():
        assert len({w['id'] for w in ws})==len(ws)
        for w in ws:
            assert len(w['words'])==len(w['source_group_ids'])==18
            assert not w['page'].startswith('f84') and int(w['physical_folio'][1:])%2==1
    phase='REGISTERED_INPUTS_ONLY';witnesses=0
    rp=BASE/'artifacts/RESULT.json'
    if rp.exists():
        phase='RESULTS';r=json.loads(rp.read_text())
        assert r['source_sha256']==sha(sp) and r['target_sha256']==sha(tp)
        assert len(r['cases'])==576
        assert len({(c['panel'],c['variant'],c['scheme'],c['traversal']) for c in r['cases']})==576
        assert r['complete']==all(c['status'] in ['UNSAT','SAT_ENUMERATED'] for c in r['cases'])
        byid={p:{w['id']:w for w in ws} for p,ws in target['panels'].items()}
        for s in r['joint_solutions']:
            key={tuple(x['unit']):x['value'] for x in s['code']};assert all(key.values())
            assert all(not a.startswith(b) and not b.startswith(a) for a,b in itertools.combinations(key.values(),2))
            ct=tables(source,source['variants'][s['variant']],s['scheme'],TRAVERSALS[s['traversal']])
            used=[]
            for tab,field in zip(ct,['present_window','imperfect_window']):
                w=byid[s['panel']][s[field]];used.append(set(w['source_group_ids']))
                for c,word in zip(tab['cells'],w['words']):assert ''.join(key[u] for u in c['units'])==word
            assert not used[0]&used[1];witnesses+=1
        assert sum(c['joint_solutions'] for c in r['cases'])==witnesses
    result={'schema':'GDT900_VALIDATION_V1','status':'PASS','phase':phase,
            'source_sha256':sha(sp),'target_sha256':sha(tp),'target_windows':counts,
            'whole_positive_witnesses_replayed':witnesses,
            'limit':'Frozen provenance and positive witness replay; complete exclusion requires independent domain/enumeration validation.'}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','phase':phase,'witnesses':witnesses}))
if __name__=='__main__':main()
