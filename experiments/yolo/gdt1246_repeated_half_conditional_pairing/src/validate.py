from pathlib import Path
import sys,json,re,hashlib,itertools,datetime
from collections import Counter,defaultdict
from fractions import Fraction as Q
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT))
from tools import word_profiles as wp

def unpack(x):return Q(x['numerator'],x['denominator'])
def separate_moments(pairs):
    n=len(pairs)
    if not n:return 0,Q(0),Q(0)
    l=Counter(a for a,b in pairs);r=Counter(b for a,b in pairs)
    mean=sum((Q(count*r[a],n) for a,count in l.items()),Q(0))
    variance=sum((count*Q(r[a],n)*(1-Q(r[a],n)) for a,count in l.items()),Q(0))
    if n>1:
        for a,ca in l.items():
            for b,cb in l.items():
                ordered=ca*(cb-(a==b))
                joint=Q(r[a]*(r[b]-(a==b)),n*(n-1))
                variance+=ordered*(joint-Q(r[a]*r[b],n*n))
    assert variance>=0
    return sum(a==b for a,b in pairs),mean,variance

def summary(rows):
    groups=defaultdict(list)
    for e in rows:groups[tuple(e['stratum'])].append((e['u'],e['v']))
    vals=[separate_moments(pairs) for pairs in groups.values()]
    t=sum(x[0] for x in vals);mean=sum((x[1] for x in vals),Q(0));var=sum((x[2] for x in vals),Q(0))
    return len(rows),len(groups),sum(v>0 for t,m,v in vals),t,mean,var,Q(t)-mean

def check_summary(rows,s):
    actual=summary(rows)
    expected=(s['events'],s['strata'],s['mobile_strata'],s['observed'],unpack(s['expected']),unpack(s['variance']),unpack(s['excess']))
    assert actual==expected,(actual,expected)
    for name in ('expected','variance','excess'):assert float(unpack(s[name]))==s[name]['decimal']

def main():
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    fixtures=[ [('a','a')], [('a','a'),('a','a')], [('a','a'),('b','b')], [('a','b'),('a','a'),('b','a'),('c','c')], [('a','x'),('b','x'),('b','a'),('c','c'),('c','a')] ]
    for pairs in fixtures:
        t,m,v=separate_moments(pairs)
        # Enumerate labelled right-position permutations; equal strings remain separate tokens.
        scores=[sum(pairs[i][0]==pairs[j][1] for i,j in enumerate(p)) for p in itertools.permutations(range(len(pairs)))]
        em=Q(sum(scores),len(scores));ev=sum(((Q(s)-em)**2 for s in scores),Q(0))/len(scores)
        assert (m,v)==(em,ev)
    receipt=json.loads((A/'SOURCE_RECEIPT.json').read_text())
    pages=receipt['inputs']['selectors']
    assert len(pages)==179 and all(not p.startswith('f84') and p!='f116v' for p in pages)
    rows,stats=wp._guarded_rows(ROOT,pages)
    events=[];excluded=Counter()
    for r in rows:
        word=r['ivtff_group_raw'];match=re.fullmatch(r'([a-z]{4,})dy',word)
        if r['kind']!='P' or not match:continue
        body=match[1];half,odd=divmod(len(body),2)
        if odd:continue
        i,n=int(r['source_group_index']),int(r['source_group_count'])
        left_ok=i==1 or r['left_separator']=='DEFINITE_SPACE'
        right_ok=i==n or r['right_separator']=='DEFINITE_SPACE'
        if not left_ok or not right_ok:excluded[r['edition']]+=1;continue
        u=''.join(body[j] for j in range(half));v=''.join(body[j] for j in range(half,len(body)))
        position={ (True,True):'single',(True,False):'start',(False,True):'end',(False,False):'middle'}[i==1,i==n]
        leaf=re.match('f[0-9]+',r['page'])[0]
        events.append({**r,'leaf':leaf,'u':u,'v':v,'stratum':[r['section'],r['currier'],r['hand'],half,u[-1],v[0],position]})
    retained=json.loads((A/'EVENTS.json').read_text())
    key=lambda e:e['source_group_id']
    assert sorted(events,key=key)==sorted(retained,key=key)
    result=json.loads((A/'RESULT.json').read_text());deletions=json.loads((A/'LEAF_DELETIONS.json').read_text())
    assert dict(excluded)==result['boundary_exclusions']
    strata=json.loads((A/'STRATA.json').read_text())
    actual_strata=defaultdict(list)
    for r in events:actual_strata[r['edition'],tuple(r['stratum'])].append(r)
    assert len(strata)==len(actual_strata)
    for s in strata:
        own=actual_strata[s['edition'],tuple(s['stratum'])]
        t,m,v=separate_moments([(r['u'],r['v']) for r in own])
        assert (t,m,v)==(s['observed'],unpack(s['expected']),unpack(s['variance']))
        assert s['n']==len(own) and s['left']==dict(Counter(r['u'] for r in own)) and s['right']==dict(Counter(r['v'] for r in own))
    for ed in ('ZL3b','IT2a','RF1b'):
        own=[x for x in events if x['edition']==ed]
        check_summary(own,result['readers'][ed])
        assert result['diagonal_forms'][ed]==dict(Counter(r['ivtff_group_raw'] for r in own if r['u']==r['v']))
        assert [x['leaf'] for x in deletions[ed]]==sorted({r['leaf'] for r in own})
        for s in deletions[ed]:check_summary([r for r in own if r['leaf']!=s['leaf']],s)
    primary=[result['readers'][ed] for ed in ('ZL3b','IT2a')]
    if any(unpack(s['variance'])==0 for s in primary):status='NO_PRIMARY_COMPARISON_CAPACITY'
    elif all(unpack(s['excess'])>0 for s in primary) and all(unpack(s['excess'])>0 and unpack(s['variance'])>0 for ed in ('ZL3b','IT2a') for s in deletions[ed]):status='RETAINED_CONDITIONAL_DIAGONAL_EXCESS'
    else:status='NO_ROBUST_PRIMARY_DIAGONAL_EXCESS'
    assert status==result['status']
    out={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'events':len(events),'strata':len(strata),'leaf_deletions':sum(map(len,deletions.values())),'synthetic_exhaustive_cases':len(fixtures),'guard_stats':stats,'scope':'Independent code reconstruction by same author; shared source and fixed assumptions. No semantic or independent manuscript confirmation.'}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
