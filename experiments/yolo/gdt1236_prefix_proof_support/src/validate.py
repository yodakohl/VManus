"""Independent proof-event, fixed-point and unweighted-threshold reconstruction."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import gzip,json,hashlib

D=Path('experiments/yolo/gdt1236_prefix_proof_support'); A=D/'artifacts'


def closure(W):
    R=set(W)
    while True:
        old=len(R)
        for v in sorted(R,key=lambda w:(len(w),w)):
            for k in range(1,len(v)):
                if v[:k] in R:R.add(v[k:])
        if len(R)==old:return R


def certificate(source,c):
    U=list(map(tuple,c['universe'])); assert len(U)==len(set(U))
    assert set(U)=={w[k:] for w in source for k in range(len(w))}
    values=dict(zip(U,c['weights'])); assert len(values)==len(c['weights'])
    latest={};events=[];seeds={}
    for j,(i,n,parents)in enumerate(c['events']):
        assert 0<=i<len(U) and n>0
        w=U[i]
        if parents is None:
            assert w in source and n==source[w] and w not in seeds
            seeds[w]=n
        else:
            x,y=parents; assert 0<=x<j and 0<=y<j
            a,na=events[x];b,nb=events[y]
            assert a+w==b and n==min(na,nb)
        if w in latest:assert events[latest[w]][1]<n
        latest[w]=j;events.append((w,n))
    assert seeds==source
    for i,w in enumerate(U):
        assert c['final_event'][i]==latest.get(w,-1)
        assert values[w]==(events[latest[w]][1]if w in latest else 0)
        for k in range(1,len(w)):
            if w[:k] in values:
                assert values[w[k:]]>=min(values[w[:k]],values[w])
    return values


def summary(R,used):
    H={w[0]for w in R};F={w[0]for w in R if len(w)==1};T={w for w in R if len(w)==2}
    second={h:{w[1]for w in R if len(w)>1 and w[0]==h}for h in used}
    heads={}
    for g in sorted(used):
        N={g}
        for unused in used:
            N|={a for a,b in T if b in N}
        conflict=sorted(N&F)
        heads[g]={'predecessors':sorted(N),'forced_conflict':conflict,
                  'direct_bound':None if conflict else len(H|{g})+max(1,len(second[g]))-1,
                  'bound':None if conflict else len(H|{g})+sum(max(1,len(second[h]))-1 for h in N)}
    bounds=[x['bound']for x in heads.values()if x['bound']is not None];bound=min(bounds)if bounds else None
    P=[w for w in sorted(R,key=lambda w:(len(w),w))if all(w[:k]not in R for k in range(1,len(w)))]
    out = {'used_signs':sorted(used),'H':sorted(H),'F':sorted(F),'T':[list(w)for w in sorted(T)],
            'second_signs':{h:sorted(second[h])for h in used},'heads':heads,'necessary_nontrivial_bound':bound,
            'prefix_basis':[list(w)for w in P],'prefix_basis_size':len(P),
            'status':'ALL_USED_CODES_SINGLETON'if not bounds else 'NECESSARY_BOUND_ONLY',
            'caps':{str(k):'EXCLUDED_NONTRIVIAL'if not bounds or bound>k else 'NOT_EXCLUDED'for k in(22,26,28)}}
    if not R:
        out['status']='NO_RETAINED_WORDS';out['caps']={str(k):'NOT_ASSESSABLE'for k in(22,26,28)}
    return out


def main():
    s=json.loads((D/'src/SPEC.json').read_text());lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    fixtures=json.loads((A/'FIXTURES.json').read_text())
    for case in fixtures['named']:
        source={tuple(w):n for w,n in case['source']};v=certificate(source,case['certificate'])
        for t in set(source.values()):assert closure({w for w,n in source.items()if n>=t})=={w for w,n in v.items()if n>=t}
    groups=json.loads(gzip.decompress(Path(s['source']).read_bytes()));result=json.loads((A/'RESULT.json').read_text())
    original=json.loads(Path(s['previous']).read_text());checks={}
    for reader in s['readers']:
        rows=groups[reader];counts=Counter(tuple(r['units'])for r in rows);pages=defaultdict(set)
        for r in rows:pages[tuple(r['units'])].add(r['page'])
        rec=result['readers'][reader];assert rec['original_tokens']==len(rows)and rec['original_types']==len(counts)
        checks[reader]={}
        for measure in s['measures']:
            source=dict(counts)if measure=='occurrences'else{w:len(p)for w,p in pages.items()}
            c=json.loads(gzip.decompress((A/('CERTIFICATE_'+reader+'_'+measure+'.json.gz')).read_bytes()))
            values=certificate(source,c);m=rec['measures'][measure]
            assert m['singleton_maximum_support']=={w[0]:n for w,n in values.items()if len(w)==1 and n>0}
            assert [x['threshold']for x in m['thresholds']]==s['thresholds']
            for row in m['thresholds']:
                t=row['threshold'];W={w for w,n in source.items()if n>=t};R=closure(W)
                assert R=={w for w,n in values.items()if n>=t}
                sm=summary(R,{a for w in W for a in w});assert sm==row['summary']
                if t==1:assert sm==original['readers'][reader]['summary']
                assert row['retained_types']==len(W)and row['retained_tokens']==sum(counts[w]for w in W)
                assert row['closure_size']==len(R)
                assert row['all_original_tokens_using_only_forced_singletons']==sum(n for w,n in counts.items()if set(w)<=set(sm['F']))
            checks[reader][measure]={'events':len(c['events']),'suffix_universe':len(values),'thresholds':len(m['thresholds'])}
    out={'status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'source_hashes':'PASS','original_full_result_retained':'PASS','named_controls':'PASS'}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

if __name__=='__main__':main()
