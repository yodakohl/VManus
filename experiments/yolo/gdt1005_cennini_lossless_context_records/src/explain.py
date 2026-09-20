"""Post-run certificates explaining every packing failure; no new selection."""
import json
from pathlib import Path
from records import profile,packing
from independent import pack
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
s=read(E/'src/SPEC.json');records=read(R/s['source_facts'])['records'];ps={w:profile(records,w) for w in s['writers']};bs=read(A/'BUNDLES.json');rows=[]
for c in read(A/'CASES.json'):
 if c['status']!='CONTRADICTED_RECORD_PACKING':continue
 b=bs[c['bundle']];minimum=ps[c['writer']]['record_minimum_lengths'];okay,stages=packing(minimum,list(map(len,b['words'])))
 assert not okay and not pack(minimum,list(map(len,b['words'])))
 i=c['first_empty_word'];assert i and not stages[i] and stages[i-1]
 choices=[dict(after_record=k,next_record=k+1,minimum_characters=minimum[k]) for k in stages[i-1] if k<len(minimum)]
 assert choices and all(len(b['words'][i-1])<v['minimum_characters'] for v in choices)
 rows.append(dict(case=c['case'],writer=c['writer'],paragraphs=b['paragraphs'],word_index=i,word=b['words'][i-1],observed_characters=len(b['words'][i-1]),remaining_possible_next_records=choices,scope='Necessary nonempty component lengths only; all120orders covered; no semantic word value inferred.'))
out=dict(status='PASS',packing_failures=len(rows),certificates=rows)
(A/'EXPLANATIONS.json').write_text(json.dumps(out,indent=2)+'\n')
lines=['# Complete packing-failure certificates','','Every packing failure after the registered count and total-character checks. No favorable subset.','','|Case|Writer|First impossible word|Characters|Minimum next record across every surviving packing|','|---|---|---|---:|---:|']
for r in rows:lines.append(f"|{r['case']}|{r['writer']}|{r['word_index']}: {r['word']}|{r['observed_characters']}|{min(x['minimum_characters'] for x in r['remaining_possible_next_records'])}|")
(A/'PACKING_FAILURES.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(status='PASS',packing_failures=len(rows))))
