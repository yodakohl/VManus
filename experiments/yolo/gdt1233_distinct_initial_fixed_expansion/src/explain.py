#!/usr/bin/env python3
"""Post-result illustrative witnesses; no new selection, score or data query."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import json,gzip,hashlib
D=Path(__file__).resolve().parents[1];A=D/'artifacts'

def read(name):return json.loads(gzip.decompress((A/name).read_bytes()))
def main():
    groups=read('GROUPS.json.gz');out={'status':'POST_RESULT_PROOF_ILLUSTRATIONS','created_utc':datetime.now(timezone.utc).isoformat(),'selection':'For each already certified forced-head step, compare a terminal remainder against two distinct nonterminal successor buckets; maximize the minimum exact-form eligible count, then prefer fewer examples and lexical order. Each successor bucket uses its most frequent form. Frequencies concern this exact eligible panel only; illustrations are not selection/confirmation data.','readings':{}}
    for ed,rows in groups.items():
        count=Counter(r['ivtff_group_raw']for r in rows);pages=defaultdict(set);first={}
        for row in rows:
            raw=row['ivtff_group_raw'];first.setdefault(raw,row);pages[raw].add(row['page'])
        node=read(f'CERTIFICATE_{ed}.json.gz');fixed=set();steps=[]
        while node['kind']=='branch':
            g=node['head'];assert node['options']==[[g]]and len(node['children'])==1
            buckets=defaultdict(list)
            for raw,row in first.items():
                units=row['units'];p=0
                while p<len(units)and units[p]in fixed:p+=1
                if p<len(units)and units[p]==g:
                    following=units[p+1]if p+1<len(units)else'<END>'
                    buckets[following].append({'word':raw,'id':row['id'],'units':units,'offset':p,'already_forced_prefix':units[:p],'following':following,'eligible_form_count':count[raw],'eligible_form_pages':sorted(pages[raw])})
            best={k:min(v,key=lambda x:(-x['eligible_form_count'],x['word'],x['id']))for k,v in buckets.items()}
            ordinary=[v for k,v in best.items()if k!='<END>']
            candidates=[]
            if len(ordinary)>=2:
                pair=sorted(ordinary,key=lambda x:(-x['eligible_form_count'],x['word'],x['id']))[:2]
                assert pair[0]['following']!=pair[1]['following']
                candidates.append(('two_different_next_signs',pair))
            if '<END>'in best:candidates.append(('complete_single_head_remainder',[best['<END>']]))
            assert candidates
            reason,chosen=min(candidates,key=lambda x:(-min(w['eligible_form_count']for w in x[1]),len(x[1]),tuple(w['word']for w in x[1])))
            assert all(set(w['already_forced_prefix'])<=fixed for w in chosen)
            steps.append({'step':len(steps)+1,'head':g,'forced_code':[g],'reason':reason,'witnesses':chosen})
            fixed.add(g);node=node['children'][0]['node']
        assert node['kind']=='identity_only'and len(fixed)==22
        out['readings'][ed]=steps
    (A/'FORCING_EXAMPLES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    for ed,steps in out['readings'].items():
        print(ed)
        for s in steps:print(s['head'],[(w['word'],w['offset'],w['following'],w['eligible_form_count'])for w in s['witnesses']])
if __name__=='__main__':main()
