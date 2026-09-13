"""Independent endpoint reconstruction, exhaustive cases and future audit."""
import csv,json,hashlib,collections,itertools
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;B=W/'W28';ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
scopes=rows(E/'SCOPES.tsv');cases=rows(E/'CANDIDATES.tsv');future=rows(E/'ALL_LATER_REQUIREMENTS.tsv');expected={};data={};events={}
for sm in ['Q','A']:
 flat=rows(B/(sm+'_SOURCE_FLAT.tsv'));assert len(flat)==1045;data[sm]=flat;ee=rows(B/(sm+'_EVENTS.tsv'));events[sm]=ee;actionids={r['location'] for r in ee if r['kind']=='ACTION'}
 for p in dict.fromkeys(r['paragraph'] for r in flat):
  ff=[r for r in flat if r['paragraph']==p];pos={r['id']:i for i,r in enumerate(ff)};cuts=[i for i,r in enumerate(ff) if r['id'] in actionids or r['form'] in ['ol','lor']]+[len(ff)];aa=[i for i,r in enumerate(ff) if r['id'] in actionids]
  for i,x in enumerate(ff):
   if x['form'] not in ['ol','lor']:continue
   stop=min(j for j in cuts if j>i);mm=[j for j in range(i+1,stop) if ff[j]['role'] in ['MATERIAL','MATERIAL_DOSE']];comp=ff[mm[0]] if mm else None
   for direction in ['P','F']:
    available=[j for j in aa if j<i] if direction=='P' else [j for j in aa if j>(pos[comp['id']] if comp else i)];idx=(max(available) if direction=='P' else min(available)) if available else None;gov=ff[idx] if idx is not None else None
    expected[sm,x['id'],direction]=(p,comp,gov)
assert len(expected)==len(scopes)==68
for r in scopes:
 p,c,g=expected[r['shol'],r['marker'],r['direction']];assert r['paragraph']==p and r['companion']==(c['id'] if c else '') and r['governor']==(g['id'] if g else '')
seen=set();expected_future=[]
for r in cases:
 key=r['shol'],r['marker'],r['direction'];p,c,g=expected[key];world=r['grammar'],r['model'],r['timing'];assert key+world not in seen;seen.add(key+world)
 rr=[x for x in events[r['shol']] if (x['paragraph'],x['grammar'],x['model'],x['timing'])==(p,*world)];a=next((x for x in rr if g and x['location']==g['id'] and x['kind']=='ACTION'),None);b=next((x for x in rr if c and x['location']==c['id'] and x['kind']=='MATERIAL'),None)
 assert r['patient']==(a['patient'] if a else '') and r['companion_object']==(b['object'] if b else '')
 debts=[]
 if not b:debts.append('MISSING_COMPANION')
 if not a:debts.append('MISSING_GOVERNOR')
 elif not a['object']:debts.append('MISSING_PATIENT')
 if a and b and a['object']==b['object']:debts.append('SAME_OBJECT_ACCOMPANIMENT')
 if a and b and a['second_object'] and a['second_object']!=b['object']:debts.append('DIFFERENT_EXISTING_SECOND_OBJECT')
 if a and a['status']=='ARGUMENT_INCOMPLETE':debts.append('EXISTING_ACTION_INCOMPLETE')
 assert r['attachment_issues']==';'.join(debts)
 valid=bool(a and b and a['object'] and a['object']!=b['object']);assert r['distinct_bound_pair']==str(valid)
 if valid:
  for idx,x in enumerate(rr):
   if idx<=rr.index(a) or idx<=rr.index(b) or x['kind']=='MATERIAL':continue
   if x['object'] in {a['object'],b['object']} or x['second_object'] in {a['object'],b['object']}:expected_future.append((key,world,x['location'],x['kind'],x['object'],x['status'],x['assertion'],x['before'],x['after']))
assert len(seen)==68*12==len(cases)
got=[((r['shol'],r['marker'],r['direction']),(r['grammar'],r['model'],r['timing']),r['location'],r['kind'],r['object'],r['status'],r['assertion'],r['before'],r['after']) for r in future];assert collections.Counter(got)==collections.Counter(expected_future)
result=json.loads((E/'RESULT.json').read_text());assert result['candidate_cases']==len(cases) and result['later_requirement_rows']==len(future) and result['marker_positions']==17
out=dict(status='PASS',bound_files=len(S['inputs']),source_groups=1045,marker_positions=17,scope_rows=68,candidate_rows=len(cases),future_rows=len(future),unchanged_baseline=True,limits='Endpoint/capacity audit, no semantic or physical effect confirmation')
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
reader=(E/'READINGS.md').read_text()
for p in json.loads((B/'SOURCE.json').read_text())['paragraphs']:
 for l in p['lines']:assert reader.count('`'+' '.join(l['words'])+'`')==1
out['full_reader_groups']=1045
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
groups=rows(E/'PREDICTION_GROUPS.tsv');assert len(groups)==40 and sum(int(g['case_count']) for g in groups)==816
for g in groups:
 match=[r for r in cases if all(r[k]==g[k] for k in ['marker','direction','companion','governor','patient','existing_second','attachment_issues'])]
 assert len(match)==int(g['case_count']) and g['members']==';'.join('|'.join(r[k] for k in ['shol','grammar','model','timing']) for r in match)
out['attachment_groups']=40
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
