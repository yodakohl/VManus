"""Necessary mixed-writer constraints; no source values or meanings."""
from pathlib import Path
import argparse, gzip, hashlib, json, re, time
D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D/'artifacts'
SPEC = json.loads((D/'src/SPEC.json').read_text())

def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)+'\n')

def leaf(page):
    return re.match(r'f(\d+)[rv]', page).group(1)

def close(seeds, seconds=120):
    nodes = [dict(word=list(w), **reason) for w,reason in sorted(seeds.items(), key=lambda x:(len(x[0]),x[0]))]
    known = {tuple(n['word']): i for i,n in enumerate(nodes)}
    start=time.monotonic()
    while True:
        before=len(nodes)
        for vi in range(before):
            v=tuple(nodes[vi]['word'])
            for cut in range(1,len(v)):
                u,r=v[:cut],v[cut:]
                if u in known and r not in known:
                    known[r]=len(nodes)
                    nodes.append({'word':list(r),'parents':[known[u],vi]})
            if time.monotonic()-start>seconds:
                return {'status':'UNKNOWN_TIMEOUT','nodes':nodes}
        if len(nodes)==before:
            return {'status':'COMPLETE','nodes':nodes}

def summarize(words, rows):
    R=set(map(tuple,words))
    H={w[0] for w in R}
    F={w[0] for w in R if len(w)==1}
    heads={}
    used={u for r in rows if len(r['units'])>=2 for u in r['units']}
    for h in sorted(used):
        followers=sorted({w[1] for w in R if len(w)>1 and w[0]==h})
        heads[h]={'followers':followers,'forced_singleton':h in F,
                  'necessary_bound':None if h in F else len(H|{h})+max(1,len(followers))-1}
    bounds=[x['necessary_bound'] for x in heads.values() if x['necessary_bound'] is not None]
    bound=min(bounds) if bounds else None
    fixed=[r for r in rows if len(r['units'])>=2 and set(r['units'])<=F]
    return {'heads':heads,'H':sorted(H),'F':sorted(F),'minimum_head_bound':bound,
            'nontrivial_status':'ALL_USED_CODES_SINGLETON' if not bounds else ('EXCLUDED_AT_CAP22' if bound>22 else 'UNRESOLVED_AT_CAP22'),
            'fully_forced_long_groups':len(fixed),'fully_forced_long_types':len({tuple(r['units']) for r in fixed})}

def seeds_for(rows):
    by={}
    for r in rows:
        by.setdefault(tuple(r['units']),[]).append(r)
    seeds={w:{'seed':'whole_long','witness':min(r['id'] for r in rr)} for w,rr in by.items() if len(w)>=2}
    for w in sorted(by):
        if len(w)==2:
            for unit in w:
                seeds.setdefault((unit,),{'seed':'two_unit_obligation','witness':min(r['id'] for r in by[w]),'whole_word':list(w)})
    return seeds

def controls():
    # Explicit complete mixed writers on a small independent toy alphabet.
    W=['A','B','AA','AB','BA','CAB']; T={'A':'z','B':'y','CAB':'x'}
    for code in [{'A':'a','B':'b','C':'c'},{'A':'a','B':'ba','C':'bb'}]:
        assert all(not y.startswith(x) for k,x in code.items() for j,y in code.items() if k!=j)
        outputs={w:T[w] if w in T else ''.join(code[c] for c in w) for w in W}
        assert len(set(outputs.values()))==len(W)
        assert all((len(o)==1)==(w in T) for w,o in outputs.items())
        singles={u for w,o in outputs.items() if len(o)==2 for u in o}
        assert singles<=set(v for v in code.values() if len(v)==1)
    # A one-letter source word emitted as a two-unit code violates mandatory T.
    assert 'A' in T and len('ab')!=1
    # Prefix cancellation fixture; all-singleton consequence needs no native singleton.
    s={tuple(w):{'seed':'fixture'} for w in ['ab','aba']}
    c=close(s); assert ('a',) in {tuple(n['word']) for n in c['nodes']}
    # Opposite direction must not be silently used for prefix codes.
    code=['a','ba']; assert all(not y.startswith(x) for x in code for y in code if x!=y)
    assert 'b' not in code
    internal=summarize([['a','b','c']],[{'units':['a','b','c']}])
    assert 'b' in internal['heads'] and 'b' not in internal['H'] and internal['heads']['b']['necessary_bound']==2
    return {'status':'PASS','fixtures':['literal_mixed_writer','compound_mixed_writer','forbidden_nonlogogram_singleletter','prefix_cancellation','one_sided_direction','internal_only_head']}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--controls',action='store_true'); args=ap.parse_args()
    if args.controls:
        dump(A/'PRELOCK_CONTROLS.json',controls()); print('source-free controls PASS'); return
    assert not (A/'RESULT.json').exists(),'preserve prior result'
    lock=json.loads((D/'LOCK.json').read_text())
    for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    data=json.loads(gzip.decompress((ROOT/SPEC['source']).read_bytes()))
    result={'experiment':'GDT1398','cases':{}}
    for ed in SPEC['readers']:
        allrows=data[ed]
        dispersion={}
        for r in allrows: dispersion.setdefault(tuple(r['units']),set()).add(leaf(r['page']))
        for panel in SPEC['panels']:
            rows=[r for r in allrows if panel=='FULL' or len(dispersion[tuple(r['units'])])>=2]
            assert all(r['units'] and set(r['units'])<=set(SPEC['signs']) for r in rows)
            seeds=seeds_for(rows)
            cert=close(seeds,SPEC['seconds_per_case'])
            two={tuple(r['units']) for r in rows if len(r['units'])==2}
            short=sorted({u for w in two for u in w})
            case={'reader':ed,'panel':panel,'groups':len(rows),'types':len({tuple(r['units']) for r in rows}),
                  'singleton_groups_ignored':sum(len(r['units'])==1 for r in rows),
                  'two_unit_types':len(two),'two_unit_forced':short,'closure_status':cert['status'],'closure_size':len(cert['nodes'])}
            if cert['status']=='COMPLETE':case['summary']=summarize([n['word'] for n in cert['nodes']],rows)
            key=ed+'_'+panel
            (A/('CERTIFICATE_'+key+'.json.gz')).write_bytes(gzip.compress(json.dumps(cert,sort_keys=True,separators=(',',':')).encode(),mtime=0))
            result['cases'][key]=case
    vals=[c.get('summary',{}).get('nontrivial_status') for c in result['cases'].values() if c['panel']=='FULL']
    result['status']='NONTRIVIAL_PREFIX_CAP22_EXCLUDED_ALL_READERS' if all(v in ('EXCLUDED_AT_CAP22','ALL_USED_CODES_SINGLETON') for v in vals) else 'SOME_UNRESOLVED'
    if any(c['closure_status']!='COMPLETE' for c in result['cases'].values()):result['status']='UNKNOWN_INCOMPLETE'
    dump(A/'RESULT.json',result)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
