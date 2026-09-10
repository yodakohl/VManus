#!/usr/bin/env python3
"""Exact complete-record division-chain discovery; no language scoring."""
import collections,hashlib,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def scan(words):
    n=len(words); partitions=[]; candidates=[]
    for width in range(4,n//3+1):
        if n%width:continue
        rows=[words[i:i+width] for i in range(0,n,width)];k=len(rows)
        cols=list(zip(*rows));vary={i for i,c in enumerate(cols) if len(set(c))>1}
        receipt={'width':width,'steps':k,'varying_columns':sorted(vary),'role_placements':0,'transfer_pairs':0,'candidates':0}
        if len(vary)<=4:
            # A,B,R must change strictly across steps: get literal transfer pairs first.
            links=[(a,b) for a in range(width) for b in range(width) if a!=b and cols[a][1:]==cols[b][:-1]]
            receipt['transfer_pairs']=len(links)
            for a,b in links:
                for bb,r in links:
                    if bb!=b or len({a,b,r})<3:continue
                    if any(len({row[a],row[b],row[r]})!=3 for row in rows):continue
                    for q in range(width):
                        if q in (a,b,r):continue
                        roles=(a,b,q,r)
                        if not vary<=set(roles):continue
                        receipt['role_placements']+=1
                        candidates.append({'width':width,'steps':k,'roles':list(roles),'equations':[[row[i] for i in roles] for row in rows]})
                        receipt['candidates']+=1
        partitions.append(receipt)
    return partitions,candidates

def fit(equations,limit):
    solutions=0; first=[]; ranges={}; prediction_count=0
    for a0 in range(2,limit+1):
        for b0 in range(1,a0):
            a,b=a0,b0;key={};inverse={};ok=True;predicted=False
            for step,tokens in enumerate(equations):
                if b==0:ok=False;break
                q,r=divmod(a,b);values=(a,b,q,r)
                if step==len(equations)-1:predicted=all(t in key for t in tokens)
                for token,value in zip(tokens,values):
                    if (token in key and key[token]!=value) or (value in inverse and inverse[value]!=token):ok=False;break
                    key[token]=value;inverse[value]=token
                if not ok:break
                a,b=b,r
            if not ok:continue
            solutions+=1;prediction_count+=predicted
            if len(first)<2:first.append(key)
            for token,value in key.items():
                old=ranges.setdefault(token,[value,value]);old[0]=min(old[0],value);old[1]=max(old[1],value)
    return {'solutions':solutions,'first_two_keys':first,'value_ranges':ranges,'full_solutions_last_step_vocabulary_preassigned':prediction_count,'prediction_claim':'None: count conditions on full-chain acceptance, not agreement of all preceding-only keys.'}

def main():
    s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source']['sha256'];source=json.loads(raw)
    partitions=[];candidates=[];summaries={}
    for reading in s['readings']:
        targets=source['panels'][reading];counts=collections.Counter();leaves=set()
        for t in targets:
            assert not t['page'].startswith('f84') and int(t['physical_folio'][1:])%2==1
            assert t['text']==' '.join(t['words'])
            leaves.add(t['physical_folio']);pp,cc=scan(t['words']);counts['paragraphs']+=1;counts['partitions']+=len(pp);counts['at_most_four_varying']+=sum(len(p['varying_columns'])<=4 for p in pp);counts['candidates']+=len(cc)
            partitions.append({'reading':reading,'id':t['id'],'page':t['page'],'groups':len(t['words']),'partitions':pp})
            for c in cc:
                c.update(reading=reading,id=t['id'],page=t['page']);c['arithmetic']=fit(c['equations'],s['numeric_maximum']);candidates.append(c)
        summaries[reading]=dict(counts,physical_leaves=len(leaves))
    result={'readings':summaries,'structural_candidates':len(candidates),'numeric_candidates':sum(c['arithmetic']['solutions']>0 for c in candidates),'status':'NO_FIXED_TEMPLATE_CHAIN' if not candidates else 'EXPLORATORY_CANDIDATES_NO_MEANING','claim_ceiling':'Fixed complete-paragraph one-group numeral template only; no general arithmetic rejection or identified translation.'}
    for name,data in [('PARTITIONS',partitions),('CANDIDATES',candidates),('RESULT',result)]: (E/'artifacts'/f'{name}.json').write_text(enc(data))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
