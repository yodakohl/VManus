import collections, hashlib, itertools, json, math
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
def h2(pairs):
    c=collections.Counter(pairs);n=sum(c.values());left=collections.Counter()
    for (a,b),v in c.items():left[a]+=v
    return sum(v/n*math.log2(left[a]/v) for (a,b),v in c.items()) if n else 0.0

def encode(words, rows, transition, initial, reset):
    state=initial;out=[]
    for word in words:
        if reset=='word':state=initial
        dest=[]
        for letter in word:
            dest.append(rows[state][letter]);state=transition[state*3+letter]
        out.append(dest)
    return out

def main():
    lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h,p
    spec=json.loads((B/'src/SPEC.json').read_text());inputs=[]
    for i in spec['inputs']:
        raw=(R/i['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==i['sha256'];inputs.append(json.loads(raw))
    old,prior=inputs
    ceilings={}
    for reader in ('IT2a','RF1b','ZL3b'):
        cells=[c for c in old['cells'] if c['reader']==reader and c['capacity']=='SCOREABLE']
        high=max(c['ranges']['conditional_entropy'][1] for c in cells)+spec['entropy_allowance']
        assert abs(high-prior['native_ceilings'][reader]['largest_allowed_H2'])<1e-12
        ceilings[reader]={'largest_allowed_H2':high,'scoreable_cells':len(cells),'no_capacity_cells':prior['native_ceilings'][reader]['no_capacity_cells']}
    cases=[]
    for orientation,metrics in old['candidate_metrics'].items():
        low=metrics['conditional_entropy']-math.log2(spec['K'])
        cases.append({'orientation':orientation,'source_H2':metrics['conditional_entropy'],'lower_bound':low,'margins':{r:low-c['largest_allowed_H2'] for r,c in ceilings.items()}})
    words=spec['fixture_words'];pairs=lambda ws:[(a,b) for w in ws for a,b in zip(w,w[1:])]
    baseline=h2(pairs(words));records=[];perms=list(itertools.permutations(spec['fixture_alphabet']))
    for rows in itertools.product(perms,repeat=2):
        for transition in itertools.product(range(2),repeat=6):
            for initial in range(2):
                for reset in spec['resets']:
                    out=encode(words,rows,transition,initial,reset);value=h2(pairs(out));assert value+1e-12>=baseline-1
                    records.append([list(rows[0]),list(rows[1]),list(transition),initial,reset,value])
    sharp={'source':[[0,0],[0,1]],'output':[[0,0],[1,0]],'source_H2':1.0,'output_H2':0.0,'states':2,'boundary':'flip after each word; identity state update inside word','rows':[[0,1],[1,0]]}
    assert h2(pairs(sharp['source']))==1 and h2(pairs(sharp['output']))==0
    negative={'source_H2':1.0,'output_H2':0.0,'claimed_states':1,'reason':'constant noninjective row violates the injective-row premise'}
    assert negative['output_H2']<negative['source_H2']-math.log2(negative['claimed_states'])
    result={'status':'ALL_AT_MOST_TWO_STATE_FIXED_SOURCE_WRITERS_EXCLUDED','K':spec['K'],'source_tokens':old['source_tokens'],'ceilings':ceilings,'cases':cases,'all_margins_positive':all(v>0 for c in cases for v in c['margins'].values()),'fixture_cases':len(records),'fixture_source_H2':baseline,'sharp_example':sharp,'noninjective_countercontrol':negative,'ceiling':'Conditional fixed-source operational screen; no native state count, source identification or meaning.'}
    assert result['all_margins_positive']
    (B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (B/'artifacts/FIXTURES.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
    print(json.dumps({'status':result['status'],'cases':cases,'fixture_cases':len(records)},indent=2))
if __name__=='__main__':main()
