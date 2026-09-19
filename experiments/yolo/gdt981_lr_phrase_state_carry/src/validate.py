"""Independent source reconstruction and exact permutation cross-check."""
import collections, hashlib, itertools, json, subprocess, sys
from pathlib import Path
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
def read(n): return json.loads((E/'artifacts'/n).read_text())
def main():
    spec=json.loads((E/'src/SPEC.json').read_text())
    for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    families=json.loads((R/spec['families']).read_text())
    panels=json.loads((R/spec['paragraphs']).read_text())
    expected=[]; expected_chains=[]; scopes={}
    for ed,ps in panels.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            scopes[(ed,p['id'])]=p
            for a,b in families:
                found=[]
                for li,line in enumerate(p['lines']):
                    if not line['anchor_eligible']: continue
                    for wi in range(len(line['words'])-1):
                        x,y=line['words'][wi:wi+2]
                        if x in (a+'r',a+'l') and y in (b+'r',b+'l'):
                            key=(ed,p['id'],a+'/'+b,li,wi)
                            expected.append(key);found.append((key,x[-1]+y[-1]))
                for old,new in zip(found,found[1:]):
                    clear=all(l['anchor_eligible'] for l in p['lines'][old[0][3]:new[0][3]+1])
                    expected_chains.append((old[0],new[0],clear,old[1][1],new[1][0],old[1][0],new[1][1]))
    events=read('EVENTS.json'); em={e['id']:e for e in events}
    key=lambda e:(e['edition'],e['paragraph'],e['family'],e['line_index'],e['word_index'])
    assert sorted(expected)==sorted(map(key,events))
    actual=[]
    for c in read('CHAINS.json'):
        old,new=em[c['previous']],em[c['next']]
        actual.append((key(old),key(new),c['clear'],c['F_expected'],c['F_observed'],c['R_expected'],c['R_observed']))
        for d in 'FR':
            want='UNRESOLVED' if not c['clear'] else 'MATCH' if c[d+'_expected']==c[d+'_observed'] else 'CONTRADICTION'
            assert c[d+'_result']==want
    assert sorted(actual)==sorted(expected_chains)
    brute_checks=0
    for row in read('ORDER_CAPACITY.json'):
        es=[e['ends'] for e in events if e['edition']==row['edition'] and e['paragraph']==row['paragraph'] and e['family']==row['family']]
        assert len(es)<=9, 'Explicit validation budget: do not silently skip a large permutation case'
        io=(1,0) if row['direction']=='F' else (0,1)
        vals=[sum(a[io[0]]==b[io[1]] for a,b in zip(order,order[1:])) for order in set(itertools.permutations(es))]
        assert (min(vals),max(vals))==(row['minimum'],row['maximum'])
        assert row['mobile']==(min(vals)!=max(vals));brute_checks+=1
    cs=read('CHAINS.json')
    cand=read('CANDIDATES.json')
    assert len(cand)==len(panels)*len(families)*2
    for row in cand:
        subset=[c for c in cs if c['edition']==row['edition'] and c['family']==row['family']]
        counter=collections.Counter(c[row['direction']+'_result'] for c in subset)
        assert row['matches']==counter['MATCH'] and row['contradictions']==counter['CONTRADICTION'] and row['unresolved']==counter['UNRESOLVED']
    for pid,p in read('COMPLETE_CHAIN_PARAGRAPHS.json').items():
        ed=pid.split('|')[0]
        assert p==scopes[(ed,p['id'])]
    names=['EVENTS.json','CHAINS.json','ORDER_CAPACITY.json','COMPLETE_CHAIN_PARAGRAPHS.json','CANDIDATES.json','RESULT.json','CANDIDATE_TABLE.tsv','CONSEQUENCES.tsv']
    before={n:(E/'artifacts'/n).read_bytes() for n in names}
    subprocess.run([sys.executable,str(E/'src/run.py')],check=True,stdout=subprocess.DEVNULL)
    assert all((E/'artifacts'/n).read_bytes()==v for n,v in before.items())
    result=dict(status='PASS',source_events=len(events),source_chains=len(cs),candidate_rows=len(cand),brute_force_order_checks=brute_checks,exact_regeneration=True,independent_implementation=True,independent_author=False,semantic_confirmation=False)
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__': main()
