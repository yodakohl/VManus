#!/usr/bin/env python3
"""Small arithmetic/order certificate for the already reported P02 exclusion."""
import collections,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
s=next(r for r in read('SOURCE.json')['records'] if r['id']=='P02')['lexical']
seed=[i for i,a in enumerate(s) if a=='LEX:semen']; assert seed==[0,2,8,10,12,14,16,18]
assert s[3:7]==['LEX:ruta','LEX:baca','LEX:ruta','LEX:baca']
required=[b-a-1 for a,b in zip(seed,seed[1:])];tail=len(s)-seed[-1]-1
needed=collections.Counter(collections.Counter(s).values()); summary=collections.Counter();details=[]
for p in read('TARGET.json')['panels']['IT2a']:
    ws=p['words'];counts=collections.Counter(ws)
    if len(ws)<len(s):summary['too_short']+=1;continue
    hist=collections.Counter(counts.values())
    if any(hist[k]<n for k,n in needed.items()):summary['multiplicity_inventory']+=1;continue
    summary['remaining_paragraphs']+=1
    for w,n in counts.items():
        if n!=8:continue
        positions=[i for i,v in enumerate(ws) if v==w];gaps=[b-a-1 for a,b in zip(positions,positions[1:])]
        failures=[dict(gap=i+1,available=x,required=y) for i,(x,y) in enumerate(zip(gaps,required)) if x<y]
        record=dict(paragraph_id=p['paragraph_id'],page=p['page'],candidate_seed_code=w,positions_1based=[i+1 for i in positions])
        if failures:record.update(reason='INSUFFICIENT_BETWEEN_CODE_SLOTS',failures=failures)
        elif len(ws)-positions[-1]-1<tail:
            record.update(reason='INSUFFICIENT_TRAILING_SLOTS',available=len(ws)-positions[-1]-1,required=tail)
        else:
            # Two globally twice-occurring distinct types must both occur twice
            # between the second and third seed occurrence (ruta,baca,ruta,baca).
            middle=collections.Counter(ws[positions[1]+1:positions[2]])
            candidates=sorted(v for v,c in counts.items() if c==2 and middle[v]==2)
            assert len(candidates)<2, 'This short certificate does not decide the pair'
            record.update(reason='MISSING_TWO_REPEATED_INNER_TYPES',available_types=candidates,required_distinct_types=2)
        details.append(record)
assert sum(summary.values())==259
result=dict(status='PASS_COMPLETE_P02_EXCLUSION_CERTIFICATE',source_sha256=hashlib.sha256((E/'artifacts/SOURCE.json').read_bytes()).hexdigest(),target_sha256=hashlib.sha256((E/'artifacts/TARGET.json').read_bytes()).hexdigest(),source_atom='LEX:semen',source_count=8,required_gaps=required,required_tail=tail,summary=dict(summary),remaining_value_cases=details,scope='Explanation of registered full-source lexical necessary condition; no extra target selection or inferred meaning.')
(E/'artifacts/ORDER_CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps(dict(status=result['status'],summary=result['summary'],value_cases=len(details))))
