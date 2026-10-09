from pathlib import Path
import sys, json, re, hashlib
from collections import Counter, defaultdict
from fractions import Fraction as F
D=Path(__file__).resolve().parents[1]; ROOT=D.parents[2]; A=D/'artifacts'
sys.path.insert(0,str(ROOT))
from tools import word_profiles as wp
ED=('ZL3b','IT2a','RF1b')
def dump(name,x): (A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def frac(x):return {'numerator':x.numerator,'denominator':x.denominator,'decimal':float(x)}
def moments(rows):
    n=len(rows); l=Counter(r['u'] for r in rows); r=Counter(r['v'] for r in rows)
    s=sum(l[b]*r[b] for b in l); e=F(s,n)
    same=sum(l[b]*(l[b]-1)*r[b]*(r[b]-1) for b in l)
    cross=s*s-sum((l[b]*r[b])**2 for b in l)
    variance=e+F(same+cross,n*(n-1))-e*e if n>1 else F(0)
    assert variance>=0
    return sum(x['u']==x['v'] for x in rows),e,variance

def aggregate(rows):
    strata=defaultdict(list)
    for r in rows:strata[tuple(r['stratum'])].append(r)
    t=0;e=F(0);v=F(0);mobile=0
    for members in strata.values():
        ti,ei,vi=moments(members);t+=ti;e+=ei;v+=vi;mobile+=vi>0
    return {'events':len(rows),'strata':len(strata),'mobile_strata':mobile,'observed':t,'expected':frac(e),'variance':frac(v),'excess':frac(F(t)-e)}

def main():
    if (A/'RESULT.json').exists():raise RuntimeError('Retained result exists; use an isolated reproduction copy.')
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    c=wp.ensure_cache(ROOT); receipt=wp.receipt(c)
    old=json.loads((ROOT/'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts/SOURCE_RECEIPT.json').read_text())
    assert receipt['inputs']==old['inputs']
    rows=[dict(x) for x in c.execute('SELECT '+','.join(wp.COLUMNS)+' FROM groups ORDER BY edition,page,locus,source_group_index')];c.close()
    allowed=set(receipt['inputs']['selectors']);assert len(allowed)==179
    events=[];excluded=Counter()
    for r in rows:
        assert r['page'] in allowed and not r['page'].startswith('f84') and r['page']!='f116v'
        w=r['ivtff_group_raw'];i=int(r['source_group_index']);n=int(r['source_group_count'])
        if r['kind']!='P' or not re.fullmatch('[a-z]+',w) or not w.endswith('dy'):continue
        stem=w[:-2]
        if len(stem)<4 or len(stem)%2:continue
        if (i>1 and r['left_separator']!='DEFINITE_SPACE') or (i<n and r['right_separator']!='DEFINITE_SPACE'):
            excluded[r['edition']]+=1;continue
        h=len(stem)//2;u,v=stem[:h],stem[h:]
        pos='single' if n==1 else 'start' if i==1 else 'end' if i==n else 'middle'
        leaf=re.match(r'f\d+',r['page']).group()
        events.append({**r,'leaf':leaf,'u':u,'v':v,'stratum':[r['section'],r['currier'],r['hand'],h,u[-1],v[0],pos]})
    views={};deletions={};strata_out=[]
    for ed in ED:
        own=[r for r in events if r['edition']==ed];views[ed]=aggregate(own)
        deletions[ed]=[{'leaf':leaf,**aggregate([r for r in own if r['leaf']!=leaf])} for leaf in sorted({r['leaf'] for r in own})]
        grouped=defaultdict(list)
        for r in own:grouped[tuple(r['stratum'])].append(r)
        for key,rs in sorted(grouped.items()):
            t,e,v=moments(rs)
            strata_out.append({'edition':ed,'stratum':list(key),'n':len(rs),'observed':t,'expected':frac(e),'variance':frac(v),'left':dict(Counter(x['u'] for x in rs)),'right':dict(Counter(x['v'] for x in rs))})
    primary=ED[:2]
    if any(views[e]['variance']['numerator']==0 for e in primary):status='NO_PRIMARY_COMPARISON_CAPACITY'
    elif all(views[e]['excess']['numerator']>0 and all(x['excess']['numerator']>0 and x['variance']['numerator']>0 for x in deletions[e]) for e in primary):status='RETAINED_CONDITIONAL_DIAGONAL_EXCESS'
    else:status='NO_ROBUST_PRIMARY_DIAGONAL_EXCESS'
    result={'status':status,'readers':views,'boundary_exclusions':dict(excluded),'diagonal_forms':{ed:dict(Counter(x['ivtff_group_raw'] for x in events if x['edition']==ed and x['u']==x['v'])) for ed in ED},'claim_ceiling':'Conditional exposed association only; no significance, copying operation, native morphology, word meaning or independent-reader replication.'}
    dump('EVENTS.json',events);dump('STRATA.json',strata_out);dump('LEAF_DELETIONS.json',deletions);dump('SOURCE_RECEIPT.json',receipt);dump('RESULT.json',result)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
