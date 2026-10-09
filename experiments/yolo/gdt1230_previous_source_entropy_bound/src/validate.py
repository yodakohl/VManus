#!/usr/bin/env python3
"""Independent source traversal, entropy identities and high-precision checks."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
from decimal import Decimal,localcontext
import hashlib,html,itertools,json,math,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
s=json.loads((D/'src/SPEC.json').read_text());r=json.loads((A/'RESULT.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
old=json.loads((ROOT/s['source_spec']).read_text());point=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]');finals={'ך':'כ','ם':'מ','ן':'נ','ף':'פ','ץ':'צ'};sections=[]
for c,path in enumerate(old['hebrew_files'],1):
    obj=json.loads((ROOT/path).read_text());assert obj['sections']==[str(c)] and not obj['warnings'];vs=obj['versions'];assert len(vs)==1 and vs[0]['versionTitle']=='Torat Emet 363'
    for j,raw in enumerate(vs[0]['text'],1):
        text=html.unescape(re.sub(r'</?small(?:\s[^>]*)?>','',raw));assert '<' not in text and '>' not in text
        text=point.sub('',text).replace('"','').replace("'",'');words=[''.join(finals.get(x,x) for x in w) for w in re.findall('[א-ת]+',text)];assert words
        sections.append({'ref':f'{c}:{j}','words':words})
assert sections==json.loads((ROOT/s['source_projection']).read_text())['source_sections'];words=[w for x in sections for w in x['words']]
assert len(words)==6288==r['source_tokens'] and len(sections)==71==r['source_sections'] and max(map(len,words))<=24
assert sum(map(len,words))==r['source_letters'] and sum(len(w)-1 for w in words)==r['within_word_pairs']
def counts_from_offsets(paragraphs,orientation,reset):
    counts=Counter()
    for para in paragraphs:
        ws=[w if orientation=='logical' else ''.join(reversed(w)) for w in para];flat=''.join(ws);offset=0
        for w in ws:
            for j in range(1,len(w)):
                index=offset+j;p=flat[index-1];x=flat[index]
                q='RESET' if reset=='word' and j==1 or index==1 else flat[index-2]
                counts[q,p,x]+=1
            offset+=len(w)
        assert offset==len(flat)
    return counts
assert counts_from_offsets([['a','ba','ab'],['b','aa']],'logical','paragraph')==Counter({('a','b','a'):1,('a','a','b'):1,('b','a','a'):1})
assert counts_from_offsets([['a','ba','ab'],['b','aa']],'logical','word')==Counter({('RESET','b','a'):1,('RESET','a','b'):1,('RESET','a','a'):1})
assert counts_from_offsets([['ab']],'logical','paragraph')==Counter({('RESET','a','b'):1})
def H(counts):
    n=sum(counts.values());return math.log2(n)-sum(v*math.log2(v) for v in counts.values())/n
def right_bound(counts):
    context=Counter()
    for (q,p,x),c in counts.items():context[q,p]+=c
    return H(counts)-H(context)
def decimal_bound(counts):
    context=Counter()
    for (q,p,x),c in counts.items():context[q,p]+=c
    with localcontext() as ctx:
        ctx.prec=50;n=Decimal(sum(counts.values()));log2=Decimal(2).ln()
        return sum(Decimal(c)*(Decimal(context[q,p])/Decimal(c)).ln()/log2 for (q,p,x),c in counts.items())/n
# Independently rebuild all four binary row tables and both declared fixtures.
fx=json.loads((A/'FIXTURES.json').read_text());expect=[]
for label in ['uniform','deterministic']:
    seq=[(q,p,x) for q in range(2) for p in range(2) for x in range(2) if label=='uniform' or x==p^q];counts=Counter(seq);lb=right_bound(counts)
    for bits in itertools.product(range(2),repeat=2):
        table=[[i^bits[p] for i in range(2)] for p in range(2)];pairs=Counter((table[q][p],table[p][x]) for q,p,x in seq);left=Counter()
        for (a,b),c in pairs.items():left[a]+=c
        h2=H(pairs)-H(left);assert h2+1e-12>=lb
        expect.append({'fixture':label,'rows':table,'lower_bound':lb,'output_H2':h2})
assert fx['exhaustive_binary_cases']==expect and fx['noninjective_null']=={'output_H2':0.0,'source_bound':1.0,'violates':True}
assert any(x['output_H2']-x['lower_bound']>.5 for x in expect)
native=json.loads((ROOT/s['native_result']).read_text());assert native['source_tokens']==6288 and json.loads((ROOT/s['native_validation']).read_text())['status']=='PASS'
for ed,actual in r['native_ceilings'].items():
    cells=[c for c in native['cells'] if c['reader']==ed and c['capacity']=='SCOREABLE'];values=[x['metrics']['conditional_entropy'] for c in cells for x in c['samples']]
    assert actual=={'samples':len(values),'scoreable_cells':len(cells),'native_H2_min':min(values),'native_H2_max':max(values),'largest_allowed_H2':max(values)+.30,'no_capacity_cells':[{'field':c['field'],'value':c['value'],'eligible_groups':c['eligible_groups']} for c in native['cells'] if c['reader']==ed and c['capacity']=='NO_CAPACITY']}
assert set(r['native_ceilings'])=={'IT2a','RF1b','ZL3b'} and len(r['cases'])==4
precision=[];excluded=0
for expected,case in zip(s['cases'],r['cases']):
    assert all(case[k]==v for k,v in expected.items());counts=counts_from_offsets([x['words'] for x in sections],**expected)
    assert case['context_counts']==[[*k,v] for k,v in sorted(counts.items())]
    assert case['positions']==sum(counts.values())==r['within_word_pairs'] and case['contexts']==len({k[:2] for k in counts}) and case['distinct_triples']==len(counts)
    assert case['reset_context_pairs']==sum(c for k,c in counts.items() if k[0]=='RESET')
    value=right_bound(counts);precise=decimal_bound(counts);assert abs(value-case['lower_bound'])<1e-10 and abs(float(precise)-case['lower_bound'])<1e-10
    for ed,summary in r['native_ceilings'].items():
        margin=float(precise)-summary['largest_allowed_H2'];got=case['decisions'][ed];assert abs(margin-got['margin_over_largest_allowed_H2'])<1e-10
        verdict='ALL_PREVIOUS_LETTER_PERMUTATIONS_EXCLUDED' if margin>1e-8 else 'BOUND_INCONCLUSIVE';assert got['decision']==verdict;excluded+=verdict=='ALL_PREVIOUS_LETTER_PERMUTATIONS_EXCLUDED'
    precision.append({**expected,'decimal50_lower_bound':str(precise)})
status='ALL_FOUR_SOURCE_CASES_EXCLUDED_ALL_READINGS' if excluded==12 else 'SOME_SOURCE_CASES_EXCLUDED' if excluded else 'ENTROPY_BOUND_INCONCLUSIVE_ALL_CASES';assert status==r['status']
v={'experiment':'GDT1230','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'source_tokens':len(words),'source_sections':len(sections),'within_word_pairs':r['within_word_pairs'],'high_precision_bounds':precision,'checks':['frozen inputs and proof/code','independent raw source projection','flat-offset traversal including first pairs one-letter words and reset sentinels','full four context-count certificates','exhaustive binary permutations and essential noninjective null','joint-minus-context entropy and50digit Decimal logs','unchanged cached native sample ceilings capacities and all decisions'],'claim':'Separate computation by same root; producer independently checked proof before source output. Neither establishes native meaning or historical use.'}
(A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
