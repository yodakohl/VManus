import json,gzip,re,itertools
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
def one(a,b):
    if a==b:return False
    if len(a)==len(b):
        d=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
        return len(d)==1 or (len(d)==2 and d[1]==d[0]+1 and a[d[0]]==b[d[1]] and a[d[1]]==b[d[0]])
    if len(a)>len(b):a,b=b,a
    if len(b)!=len(a)+1:return False
    i=0
    while i<len(a) and a[i]==b[i]:i+=1
    return a[i:]==b[i+1:]
def control():
    # Separate brute operation oracle, only synthetic inputs.
    strings=[t for n in range(5) for t in itertools.product('ab',repeat=n)]
    for a in strings:
        edit=set()
        for i in range(len(a)):
            edit.add(a[:i]+a[i+1:])
            for c in 'ab':edit.add(a[:i]+(c,)+a[i+1:])
        for i in range(len(a)+1):
            for c in 'ab':edit.add(a[:i]+(c,)+a[i:])
        for i in range(len(a)-1):edit.add(a[:i]+(a[i+1],a[i])+a[i+2:])
        edit.discard(a)
        for b in strings:assert one(a,b)==(b in edit)
    return len(strings)**2

def main():
    controls=control()
    cache=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
    train={r:{tuple(g['units'][1:-1]) for g in gs if len(g['units'])>=5 and int(re.search(r'\d+',g['page'])[0])%2==1} for r,gs in cache.items()}
    old=[p for p in json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1265_paired_interior_position_control/artifacts/PAIRS.json.gz').read_bytes())) if p['cohort']=='UNSEEN_INTERIOR']
    new=json.loads(gzip.decompress((P/'artifacts/CLASSIFIED_PAIRS.json.gz').read_bytes()))
    assert len(old)==len(new)
    memo={}; sums=defaultdict(lambda:defaultdict(list))
    for orig,p in zip(old,new):
        assert orig=={k:v for k,v in p.items() if k not in ['category','train_neighbors']}
        ws=[]
        for side in ['left','right']:
            x=tuple(p[side]['interior']); key=(p['reader'],x)
            assert x not in train[p['reader']]
            if key not in memo:memo[key]=sorted(t for t in train[p['reader']] if abs(len(t)-len(x))<=1 and one(x,t))
            ws.append([list(t) for t in memo[key]])
        assert ws==p['train_neighbors']
        cat='BOTH_NEAR' if all(ws) else 'MIXED' if any(ws) else 'BOTH_FAR'
        assert cat==p['category']; sums[(p['reader'],cat)][p['left']['leaf']].append(p)
    result=json.loads((P/'artifacts/RESULT.json').read_text());assert result['total_pairs']==len(old)
    for report in result['reports']:
        byleaf=sums[(report['reader'],report['category'])]; assert len(byleaf)==len(report['leaves'])
        vals=[];count=0
        for l in report['leaves']:
            ps=byleaf[l['leaf']]; ex=sum((Fraction(p['observed'])-Fraction(*p['expected']) for p in ps),Fraction()); den=sum(len(p['left']['interior'])+len(p['right']['interior'])-2 for p in ps)
            n=sum(p['maximum']>p['minimum'] for p in ps);count+=n
            assert l['pairs']==len(ps) and l['informative_pairs']==n and Fraction(*l['excess'])==ex and l['denominator']==den and Fraction(*l['rate'])==ex/den
            if n:vals.append(ex/den)
        mean=sum(vals,Fraction())/len(vals) if vals else Fraction(); pos=sum(v>0 for v in vals)
        gate='CAPACITY_STOP' if len(vals)<10 else 'DISTANT_INTERIOR_LEAD_RETAINED' if pos*3>=len(vals)*2 and mean>=Fraction(1,100) else 'NONCONFIRMATION'
        assert report['gate']==gate and report['mean_exact']==[mean.numerator,mean.denominator] and report['mean']==float(mean)
        assert report['positive_leaves']==pos and report['informative_leaves']==len(vals) and report['pairs']==sum(map(len,byleaf.values())) and report['informative_pairs']==count
    assert result['status']==next(r['gate'] for r in result['reports'] if r['reader']=='ZL3b' and r['category']=='BOTH_FAR')
    out=dict(status='PASS',pairs=len(old),distinct_reader_interiors=len(memo),synthetic_comparisons=controls,independent_algorithm='direct tuple alignment; no primary imports')
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':
    import sys
    if '--controls' in sys.argv:print(control())
    else:main()
