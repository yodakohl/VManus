import json,gzip,hashlib,sys
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];OLD=ROOT/'experiments/yolo/gdt1259_paragraph_integer_balance'
def scan(units,h,phase):
    pairs=[];single=[];pending=None
    for j,u in enumerate(units):
        if phase and j==0:continue
        if pending is not None:pairs.append([pending[0],pending[1],u]);pending=None
        elif h is not None and u==h:single.append(j)
        else:pending=(j,u)
    return dict(pairs=pairs,singletons=single,dangling=None if pending is None else pending[0])
def tokenize(raw,alphabet):
    paths={0:[()]}
    for i in range(len(raw)):
        for old in paths.get(i,[]):
            for u in alphabet:
                if raw.startswith(u,i):paths.setdefault(i+len(u),[]).append(old+(u,))
    assert len(paths.get(len(raw),[]))==1,raw
    return paths[len(raw)][0]
def controls():
    assert scan('xbcx','x',1)==dict(pairs=[[1,'b','c']],singletons=[3],dangling=None)
    assert scan('abxc','x',0)==dict(pairs=[[0,'a','b']],singletons=[2],dangling=3)
    assert scan('abxc','x',1)==dict(pairs=[[1,'b','x']],singletons=[],dangling=3)
    assert scan('','x',1)==dict(pairs=[],singletons=[],dangling=None)
    assert scan('x','x',0)==dict(pairs=[],singletons=[0],dangling=None)
    assert scan('x','x',1)==dict(pairs=[],singletons=[],dangling=None)
    ss=[]
    for s in ['aba','bab']:
        a,b=[{tuple(x[1:]) for x in scan(s,None,k)['pairs']} for k in (0,1)];ss.append(a&b)
    assert set.union(*ss)==set()
    return dict(status='PASS',named_checks=7)

def main():
    for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    old=json.loads((OLD/'artifacts/CERTIFICATES.json').read_text());alphabet=json.loads((OLD/'src/SPEC.json').read_text())['working_signs']
    result=json.loads((P/'artifacts/RESULT.json').read_text());packets=json.loads(gzip.decompress((P/'artifacts/PAIR_CERTIFICATES.json.gz').read_bytes()))
    assert len(packets)==46 and len(result['reports'])==2
    indexed={(p['reader'],p['marker']):p for p in packets};assert len(indexed)==46
    checks=0;witnesses=0
    for r in result['reports']:
        reader=r['reader'];snippets={};totalunits=0
        for entry in old[reader]:
            para=entry['paragraph'];raw=entry['raw_groups'];assert all(g['page']==para['page'] and g['edition']==reader and g['kind']=='P' for g in raw)
            assert not para['page'].startswith('f84') and para['page']!='f116v'
            rows=list(dict.fromkeys(int(g['source_row_index']) for g in raw));assert rows==para['source_rows']==list(range(rows[0],rows[-1]+1))
            for row in rows:
                gs=[g for g in raw if int(g['source_row_index'])==row]
                assert [int(g['source_group_index']) for g in gs]==list(range(1,int(gs[0]['source_group_count'])+1))
            units=[];pointers=[]
            for g in raw:
                for j,u in enumerate(tokenize(g['ivtff_group_raw'],alphabet)):
                    units.append(u);pointers.append(dict(id=reader+'|'+g['locus']+'|G'+str(int(g['source_group_index'])).zfill(3),unit_offset=j,page=g['page'],locus=g['locus']))
            assert [Counter(units)[u] for u in alphabet]==para['counts'];snippets[para['id']]=(units,pointers);totalunits+=len(units)
        assert r['snippets']==len(snippets)==23 and r['units']==totalunits
        assert len(r['cases'])==23 and {x['marker'] for x in r['cases']}==set(alphabet)|{None}
        for case in r['cases']:
            marker=case['marker'];packet=indexed[(reader,marker)];expected_union=set();support={}
            assert [x['id'] for x in packet['snippets']]==list(snippets)
            for p in packet['snippets']:
                units,ptr=snippets[p['id']];phases=[scan(units,marker,k) for k in (0,1)];assert phases==p['parses'];checks+=2
                common={tuple(x[1:]) for x in phases[0]['pairs']} & {tuple(x[1:]) for x in phases[1]['pairs']}
                assert [list(x) for x in sorted(common)]==p['mandatory_pairs'];expected_union.update(common)
                for pair in common:support.setdefault(pair,[]).append((p['id'],phases,ptr))
            assert case['mandatory_pairs']==[list(x) for x in sorted(expected_union)]
            assert case['mandatory_pair_count']==len(expected_union) and case['excluded_at32']==(len(expected_union)>32)
            assert len(packet['witnesses'])==len(expected_union)
            assert {tuple(w['pair']) for w in packet['witnesses']}==expected_union
            for w in packet['witnesses']:
                pair=tuple(w['pair']);sid,phases,ptr=support[pair][0];assert sid==w['snippet']
                idx=[min(x[0] for x in phase['pairs'] if tuple(x[1:])==pair) for phase in phases];assert idx==w['indices']
                assert w['provenance']==[[ptr[i],ptr[i+1]] for i in idx];witnesses+=1
        lower=min(c['mandatory_pair_count'] for c in r['cases']);assert r['minimum_necessary_pair_count']==lower
        assert r['minimizers']==[c['marker'] for c in r['cases'] if c['mandatory_pair_count']==lower] and r['excluded_at32']==(lower>32)
    status='ALL_SMALL_PAIR_TABLES_EXCLUDED' if all(r['excluded_at32'] for r in result['reports']) else 'PARTIAL_PAIR_TABLE_CAPACITY_BOUND';assert result['status']==status and result['pair_entry_cap']==32
    out=dict(status='PASS',reader_configurations=46,snippet_phase_parses=checks,mandatory_type_witnesses=witnesses,source_snippets=46,verification='independent pending-state parser, dynamic unique working-unit segmentation, continuity and both-phase source certificates; no primary imports')
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
    if '--controls' in sys.argv:
        out=controls();(P/'artifacts/VALIDATOR_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
    else:main()
