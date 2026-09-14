"""Post-result presentation only; does not select or modify any tested candidate."""
import csv
import json
from pathlib import Path
from collections import Counter
E=Path(__file__).resolve().parents[1]
a=E/'artifacts'
r=json.loads((a/'RESULT.json').read_text())
p=json.loads((E/'src/SOURCE_PREDICTIONS.json').read_text())
s=json.loads((E/'src/SPEC.json').read_text())
def table(name,fields,rows):
 with (a/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
rows=[]
for model,ts in p.items():
 for t in ts:
  rows.append({'model':model,'tuple_id':t['id'],'values':json.dumps(t['values'],separators=(',',':')),**t['counts']})
table('COMPLETE_SOURCE_PREDICTIONS.tsv',['model','tuple_id','values',*s['sign_order']],rows)
rows=[]
for x in r['results']:
 h=x['hall_certificate']
 row={k:x[k] for k in ['model','edition','scope','definite_slots','unknown_slots','definite_types','maximum_matching_size','status']}
 row.update({'hall_labels':len(h['label_ids']) if h else 0,'hall_tuple_neighbors':len(h['tuple_ids']) if h else 0,'hall_deficiency':h['deficiency'] if h else 0,'surviving_complete_assignments':0 if not x['feasible'] else 'NOT_ENUMERATED','confirmed_words':0,'fresh_independent_meaning_capacity':0})
 rows.append(row)
table('REVIEW_TABLE.tsv',list(rows[0]),rows)
rows=[]
for edition in s['editions']:
 for sign in s['sign_order']:
  ins=[v for v in r['inscriptions'] if v['edition']==edition and v['sign']==sign]
  c=Counter(tuple(v['groups']) for v in ins if v['definite'])
  rows.append({'edition':edition,'sign':sign,'definite_slots':sum(c.values()),'definite_types':len(c),'unknown_slots':sum(not v['definite'] for v in ins),'T3_source_types':sum(t['counts'][sign]>0 for t in p['T3']),'T4_source_types':sum(t['counts'][sign]>0 for t in p['T4']),'observed_repeats':json.dumps([{'groups':list(k),'count':v} for k,v in sorted(c.items()) if v>1],separators=(',',':'))})
table('SIGN_COUNTS.tsv',list(rows[0]),rows)
rows=[]
for x in r['results']:
 h=x['hall_certificate']; by={v['id']:v for v in x['labels']}
 for wid in h['label_ids'] if h else []:
  w=by[wid]
  rows.append({'model':x['model'],'edition':x['edition'],'scope':x['scope'],'label_id':wid,'groups':json.dumps(w['groups'],separators=(',',':')),'counts':json.dumps(w['counts'],separators=(',',':')),'loci':json.dumps(w['loci'],separators=(',',':')),'tuple_domain':json.dumps(x['domains'][wid],separators=(',',':'))})
table('ALL_HALL_LABELS.tsv',list(rows[0]),rows)
print(json.dumps({'source_prediction_rows':sum(map(len,p.values())),'candidate_rows':len(r['results']),'hall_label_rows':len(rows)}))
