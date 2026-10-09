import gzip,json,re,hashlib
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
CACHE=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
PAIRS=ROOT/'experiments/yolo/gdt1265_paired_interior_position_control/artifacts/PAIRS.json.gz'
ALPHA='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def near(x):
    out=set()
    for i in range(len(x)):
        out.add(x[:i]+x[i+1:])
        for c in ALPHA: out.add(x[:i]+(c,)+x[i+1:])
    for i in range(len(x)+1):
        for c in ALPHA: out.add(x[:i]+(c,)+x[i:])
    for i in range(len(x)-1): out.add(x[:i]+(x[i+1],x[i])+x[i+2:])
    out.discard(x)
    return out

def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for path,digest in lock['sha256'].items(): assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    src=json.loads(gzip.decompress(CACHE.read_bytes()))
    train={r:{tuple(g['units'][1:-1]) for g in rows if int(re.match(r'f(\d+)',g['page'])[1])%2 and len(g['units'])>=5} for r,rows in src.items()}
    packets=[]; stats=defaultdict(lambda:defaultdict(lambda:[0,Fraction(0),0,0]))
    witness_cache={}
    for p in json.loads(gzip.decompress(PAIRS.read_bytes())):
        if p['cohort']!='UNSEEN_INTERIOR': continue
        r=p['reader']; witnesses=[]
        for side in ['left','right']:
            x=tuple(p[side]['interior']); assert x not in train[r]
            key=(r,x)
            if key not in witness_cache: witness_cache[key]=sorted(near(x)&train[r])
            witnesses.append(witness_cache[key])
        category=['BOTH_FAR','MIXED','BOTH_NEAR'][sum(bool(w) for w in witnesses)]
        row=dict(p,category=category,train_neighbors=witnesses)
        packets.append(row)
        leaf=p['left']['leaf']; assert leaf==p['right']['leaf']
        s=stats[(r,category)][leaf]
        s[0]+=1; s[1]+=p['observed']-Fraction(*p['expected']); s[2]+=2*(p['length']-1); s[3]+=int(p['informative'])
    reports=[]
    for r in sorted(train):
        for cat in ['BOTH_FAR','MIXED','BOTH_NEAR']:
            leaves=[]
            for leaf,(n,ex,den,info) in sorted(stats[(r,cat)].items()):
                val=ex/den; leaves.append(dict(leaf=leaf,pairs=n,informative_pairs=info,excess=[ex.numerator,ex.denominator],denominator=den,rate=[val.numerator,val.denominator]))
            active=[l for l in leaves if l['informative_pairs']]; pos=sum(Fraction(*l['rate'])>0 for l in active)
            mean=sum((Fraction(*l['rate']) for l in active),Fraction())/len(active) if active else Fraction()
            status='CAPACITY_STOP' if len(active)<10 else 'DISTANT_INTERIOR_LEAD_RETAINED' if 3*pos>=2*len(active) and mean>=Fraction(1,100) else 'NONCONFIRMATION'
            reports.append(dict(reader=r,category=cat,pairs=sum(l['pairs'] for l in leaves),informative_pairs=sum(l['informative_pairs'] for l in leaves),positive_leaves=pos,informative_leaves=len(active),mean=float(mean),mean_exact=[mean.numerator,mean.denominator],gate=status,leaves=leaves))
    result=dict(status=next(r['gate'] for r in reports if r['reader']=='ZL3b' and r['category']=='BOTH_FAR'),reports=reports,total_pairs=len(packets))
    (P/'artifacts/CLASSIFIED_PAIRS.json.gz').write_bytes(gzip.compress(json.dumps(packets,sort_keys=True).encode(),mtime=0))
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({**result,'reports':[{k:v for k,v in r.items() if k!='leaves'} for r in reports]},indent=2))
if __name__=='__main__': main()
