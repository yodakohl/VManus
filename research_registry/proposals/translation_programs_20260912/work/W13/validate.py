"""Independent full expected-delta validator; no builder import."""
import csv,json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(p):return json.loads(p.read_text())
s=js(E/'SPEC.json')
for f in s['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];raw={};targets=set()
for edition,ll in alt.items():
 lookup={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];rr=[]
  for l in p['lines']:
   loc=l['locus'];assert not loc.startswith('f84')
   for i,g in enumerate(lookup[loc]['groups'],1):
    w=g['ivtff_group_raw'];rr.append((loc+':'+str(i),loc,w))
    if w=='ychor':targets.add((edition,loc+':'+str(i)))
  raw[(edition,p['id'])]=rr
assert len(targets)==40
baseline={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W05/ARGUMENTS.tsv')}
takes={(r['edition'],r['grammar'],r['target']):r for r in rows(W/'W08/TAKE_ARGUMENTS.tsv')}
actual=rows(E/'ARGUMENTS.tsv');assert len(actual)==len(baseline)*3+len(takes)==2829
seen={};changed=0
for r in actual:
 key=(r['edition'],r['variant'],r['operation']);unique=(r['model'],)+key;assert unique not in seen;seen[unique]=r
 if key in takes:
  assert r['model']=='N';old=takes[key]
  for k in ('patient','patient_form','rule','debts'):assert r[k]==old[k]
  continue
 old=baseline[key].copy()
 if r['model']=='P':
  if r['operation']=='f106r.9:2':old.update(patient='f106r.9:1',patient_form='ychor',rule='LOCAL_LEFT');changed+=1
  elif r['edition']=='IT2a' and r['operation']=='f93r.10:2':old.update(patient='f93r.10:1',patient_form='ychor',rule='LOCAL_LEFT',debts='');changed+=1
 for k in ('patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption'):assert r[k]==old[k],(unique,k)
assert changed==12
tr=rows(E/'TARGETS.tsv');assert len(tr)==360
for m in ('A','N','P'):
 for v in ('B','J','M'):assert {(r['edition'],r['mention']) for r in tr if r['model']==m and r['variant']==v}==targets
for t in tr:
 rr=raw[(t['edition'],t['paragraph'])];loc=t['mention'].rsplit(':',1)[0]
 assert t['raw_line']==' '.join(w for _,l,w in rr if l==loc)
 if t['model']=='P':
  expected=[r['operation'] for r in actual if r['edition']==t['edition'] and r['variant']==t['variant'] and r['model']=='P' and t['mention'] in (r['patient'],r['coingredient'])]
  assert t['material_uses']==';'.join(expected)
oldq={(q['variant'],q['paragraph'],q['mention'],q['axis']):q for q in rows(W/'W05/QUALITY_ASSERTIONS.tsv')}
qq=rows(E/'QUALITY_ASSERTIONS.tsv');assert len(qq)==len(oldq)*3
qdelta=0
for q in qq:
 before=oldq[(q['variant'],q['paragraph'],q['mention'],q['axis'])].copy()
 if q['model']=='P' and q['mention'] in ('f19v.9:2','f106r.9:2'):
  before.update(patient=q['mention'].rsplit(':',1)[0]+':1',patient_form='ychor');qdelta+=1
  if q['mention']=='f19v.9:2':before['rule']='LOCAL_LEFT'
 for k in ('patient','patient_form','rule','debts','axis','value','kind','scope'):assert q[k]==before[k],(q,k)
 assert q['old_phase_not_recomputed']==before['phase']
assert qdelta==6
rep=rows(E/'CHOR_CENSUS.tsv');expected=[]
for (edition,p),rr in raw.items():
 for i,(x,l,w) in enumerate(rr):
  if w!='ychor':continue
  for j,(y,ll,ww) in enumerate(rr):
   if ww=='chor':expected.append((edition,p,x,y,'AFTER' if j>i else 'BEFORE',str(j==i+1 and l==ll)))
assert {(r['edition'],r['paragraph'],r['target'],r['chor'],r['relative'],r['direct_next']) for r in rep}==set(expected)
assert sum(e[0]=='ZL3b' and e[-1]=='True' for e in expected)==2
future=rows(E/'FUTURES.tsv')
for t in tr:
 rr=raw[(t['edition'],t['paragraph'])];pos={x:i for i,(x,_,_) in enumerate(rr)}
 body=[r for r in actual if r['edition']==t['edition'] and r['variant']==t['variant'] and r['model']==t['model'] and r['paragraph']==t['paragraph'] and r['form']!='ychor' and pos[r['operation']]>pos[t['mention']]]
 ff=[r for r in future if r['edition']==t['edition'] and r['variant']==t['variant'] and r['model']==t['model'] and r['target']==t['mention']]
 assert {r['later_action'] for r in ff}=={r['operation'] for r in body}
 for r in ff:
  a=seen[(t['model'],t['edition'],t['variant'],r['later_action'])];assert r['patient']==a['patient'] and r['debts']==a['debts']
before=rows(W/'W10/ALIGNMENT.tsv');after=rows(E/'ALIGNMENT.tsv');assert len(before)==len(after)==900
for a,b in zip(before,after):
 for k,v in a.items():assert b[k]==v
 if a['raw']!='ychor':assert b['A']==b['N']==b['P']==a['H']
result={'status':'PASS','source_preregistration_hashes':True,'argument_rows':len(actual),'target_rows':len(tr),'quality_rows':len(qq),'body_delta_rows':changed,'quality_binding_delta_rows':qdelta,'complete_chor_and_future_census':True,'primary_groups':900,'semantic_validation':False,'independent_confirmation_capacity':0}
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
