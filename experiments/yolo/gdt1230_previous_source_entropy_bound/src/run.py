#!/usr/bin/env python3
"""Finite empirical necessary bound; never constructs a historical-source key."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
from itertools import product,permutations
import hashlib,json,math
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def save(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def conditional(table):
    # Each key is (context_tuple, current_symbol).
    totals=Counter()
    for (context,x),v in table.items():totals[context]+=v
    n=sum(table.values());assert n
    return -sum(v/n*math.log2(v/totals[context]) for (context,x),v in table.items())
def bound(events):return conditional(Counter({(tuple(k[:2]),k[2]):v for k,v in events.items()}))
def events(sections,orientation,reset):
    count=Counter()
    for paragraph in sections:
        history=[]
        for raw in paragraph:
            word=raw if orientation=='logical' else raw[::-1]
            if reset=='word':history=[]
            for j,x in enumerate(word):
                if j:
                    p=history[-1];q=history[-2] if len(history)>=2 else 'RESET';count[q,p,x]+=1
                history.append(x)
    return count

def fixtures():
    known=[['a','ba','ab'],['b','aa']]
    assert events(known,'logical','paragraph')==Counter({('a','b','a'):1,('a','a','b'):1,('b','a','a'):1})
    assert events(known,'logical','word')==Counter({('RESET','b','a'):1,('RESET','a','b'):1,('RESET','a','a'):1})
    assert events([['ab']],'logical','paragraph')==Counter({('RESET','a','b'):1})
    assert abs(bound(events(known,'logical','word'))-2/3)<1e-12
    uniform=Counter({(q,p,x):1 for q,p,x in product(range(2),repeat=3)})
    deterministic=Counter({(q,p,p^q):1 for q,p in product(range(2),repeat=2)})
    results=[]
    for name,counts in [('uniform',uniform),('deterministic',deterministic)]:
        low=bound(counts)
        for row0,row1 in product(list(permutations(range(2))),repeat=2):
            rows=[row0,row1];pairs=Counter()
            for (q,p,x),c in counts.items():pairs[(rows[q][p],),rows[p][x]]+=c
            high=conditional(pairs);assert high+1e-12>=low
            results.append({'fixture':name,'rows':[row0,row1],'lower_bound':low,'output_H2':high})
    assert any(x['output_H2']>x['lower_bound']+.5 for x in results)
    # A constant noninjective output violates the uniform-source lower bound.
    invalid_output=conditional(Counter({((0,),0):8}));assert invalid_output<bound(uniform)
    return {'exhaustive_binary_cases':results,'noninjective_null':{'output_H2':invalid_output,'source_bound':bound(uniform),'violates':True},'reset_and_one_letter_fixtures':'PASS'}

def main():
    assert not(A/'RESULT.json').exists();started=datetime.now(timezone.utc).isoformat();s=json.loads((D/'src/SPEC.json').read_text())
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    save('FIXTURES.json',fixtures())
    src=json.loads((ROOT/s['source_projection']).read_text());sections=[r['words'] for r in src['source_sections']];words=[w for row in sections for w in row]
    assert len(words)==6288 and len(sections)==71 and max(map(len,words))<=24 and set(''.join(words))<=set(s['source_alphabet'])
    native=json.loads((ROOT/s['native_result']).read_text());assert native['source_tokens']==len(words) and json.loads((ROOT/s['native_validation']).read_text())['status']=='PASS'
    ceilings={}
    for ed in ['IT2a','RF1b','ZL3b']:
        cs=[c for c in native['cells'] if c['reader']==ed and c['capacity']=='SCOREABLE'];values=[x['metrics']['conditional_entropy'] for c in cs for x in c['samples']]
        assert len(cs)==8 and len(values)==1024
        ceilings[ed]={'samples':len(values),'scoreable_cells':len(cs),'native_H2_min':min(values),'native_H2_max':max(values),'largest_allowed_H2':max(values)+.30,'no_capacity_cells':[{'field':c['field'],'value':c['value'],'eligible_groups':c['eligible_groups']} for c in native['cells'] if c['reader']==ed and c['capacity']=='NO_CAPACITY']}
    pair_count=sum(len(w)-1 for w in words);result=[]
    for case in s['cases']:
        counts=events(sections,**case);assert sum(counts.values())==pair_count
        low=bound(counts);decisions={}
        for ed,reference in ceilings.items():
            margin=low-reference['largest_allowed_H2'];decisions[ed]={'margin_over_largest_allowed_H2':margin,'decision':'ALL_PREVIOUS_LETTER_PERMUTATIONS_EXCLUDED' if margin>1e-8 else 'BOUND_INCONCLUSIVE'}
        result.append({**case,'positions':pair_count,'contexts':len({k[:2] for k in counts}),'distinct_triples':len(counts),'reset_context_pairs':sum(v for k,v in counts.items() if k[0]=='RESET'),'lower_bound':low,'context_counts':[[*k,v] for k,v in sorted(counts.items())],'decisions':decisions})
    excluded=sum(d['decision']=='ALL_PREVIOUS_LETTER_PERMUTATIONS_EXCLUDED' for case in result for d in case['decisions'].values())
    status='ALL_FOUR_SOURCE_CASES_EXCLUDED_ALL_READINGS' if excluded==12 else 'SOME_SOURCE_CASES_EXCLUDED' if excluded else 'ENTROPY_BOUND_INCONCLUSIVE_ALL_CASES'
    output={'experiment':'GDT1230','status':status,'source_tokens':len(words),'source_sections':len(sections),'source_letters':sum(map(len,words)),'within_word_pairs':pair_count,'native_ceilings':ceilings,'cases':result,'claim_ceiling':s['claim_ceiling']};save('RESULT.json',output)
    save('RUN_RECEIPT.json',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'new_native_queries':0,'source_keys_or_writers_constructed':0})
    print(json.dumps({'status':status,'within_word_pairs':pair_count,'cases':[{k:v for k,v in c.items() if k!='context_counts'} for c in result]},indent=2))
if __name__=='__main__':main()
