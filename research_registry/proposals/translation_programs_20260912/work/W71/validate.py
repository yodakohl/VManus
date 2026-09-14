from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
ps=[p for p in json.loads((D.parent/'W63/PARAGRAPHS.json').read_text()) if p['page']=='f75v'];ev=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));rows=list(csv.DictReader((D/'TRACE.tsv').open(),delimiter='\t'));effects=json.loads((D.parent/'W09/SPEC.json').read_text())['effects'];features=json.loads((D.parent/'W03/SPEC.json').read_text())['features'];initial={f['form']:f['value'] for f in features if f['axis']=='thermal' and f['kind']=='PROCESSED_NOMINAL'}
assert not any(f['form']=='dy' for f in features)
assert len(rows)==32;count=0
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])];pos={a:i for i,(a,w) in enumerate(flat)}
 for m in ['NRC','AMV']:
  rr=[r for r in rows if r['edition']==p['edition'] and r['model']==m];ee=[e for e in ev if e['edition']==p['edition'] and e['paragraph']==p['id'] and e['model']==m];assert [r['at'] for r in rr]==[e['at'] for e in ee]
  for j,(r,e) in enumerate(zip(rr,ee)):
   vals=[v for a,w in flat[:pos[r['at']]] if a==r['patient'] for v in [initial.get(w)] if v];before=vals[-1] if vals else 'UNKNOWN'
   prior=[x for x in rr[:j] if x['patient']==r['patient'] and x['status']=='ASSIGNED']
   if prior:before=prior[-1]['after']
   effect=effects.get(e['word'],{});status='NOT_A_THERMAL_ACTION'
   if e['kind']=='ACTION' and effect.get('axis')=='thermal':status='NEGATIVE_NOT_APPLIED' if e['polarity']=='NEGATIVE' else 'MISSING_PATIENT' if not e['patient'] else 'ASSIGNED'
   after=effect['value'] if status=='ASSIGNED' else before
   assert (r['before'],r['after'],r['status'])==(before,after,status)
   assert r['hot_to_warm']==str(status=='ASSIGNED' and before=='hot' and after=='warm');count+=1
v=dict(status='PASS',predicate_rows=count,hot_to_warm_rows=sum(r['hot_to_warm']=='True' for r in rows),physical_validation=False,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
