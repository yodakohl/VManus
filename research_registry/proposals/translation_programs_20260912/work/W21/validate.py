"""Independent exhaustive source and before/after use reconstruction."""
import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
s=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
for r in s['inputs']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];flats={};rawtargets=set()
for ed,ll in alt.items():
 lines={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for line in p['lines']:
   assert not line['locus'].startswith('f84');words=lines[line['locus']]
   if ed=='ZL3b':assert words==line['words']
   flat.extend((line['locus']+':'+str(i),w) for i,w in enumerate(words,1))
  flats[(ed,p['id'])]=flat;rawtargets.update((ed,p['id'],loc) for loc,w in flat if w=='ychor')
orig=[r for r in rows(W/'W16/TAKE_ARGUMENTS.tsv') if r['model']=='PR'];aa=[r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'];qq=[r for r in rows(W/'W16/QUALITY_BINDINGS.tsv') if r['model']=='PR'];key=lambda r:(r['edition'],r['paragraph'],r['grammar'],r['target']);old={key(r):r for r in orig};out=rows(E/'TARGETS.tsv');assert len(out)==len(old)==120
em=set();ea=set();eq=set()
for r in out:
 n=old.pop(key(r));ed,p,g=r['edition'],r['paragraph'],r['grammar'];flat=flats[(ed,p)];pos={l:i for i,(l,w) in enumerate(flat)};forms=dict(flat);assert r['patient']==n['patient'] and r['take_debts']==n['debts'];tick=max(pos[n['target']],pos[n['patient']] if n['patient'] else pos[n['target']]);prior=[];later=[];pa=[];fa=[];fq=[]
 if n['patient']:
  for loc,w in flat:
   if w!=n['patient_form']:continue
   side='PRIOR' if pos[loc]<pos[n['target']] else 'FOLLOWING_MENTION' if pos[loc]>tick else 'TAKE_PATIENT';em.add(key(r)+(loc,side))
   if side=='PRIOR':prior.append(loc)
   if side=='FOLLOWING_MENTION':later.append(loc)
  for a in aa:
   if (a['edition'],a['paragraph'],a['variant'])!=(ed,p,g) or not any(a[k] and forms[a[k]]==n['patient_form'] for k in ('patient','coingredient')):continue
   at=max(pos[a[k]] for k in ('operation','patient','coingredient') if a[k]);side='PRIOR' if at<tick else 'FOLLOWING';(pa if side=='PRIOR' else fa).append(a['operation']);ea.add(key(r)+(a['operation'],side))
  if ed=='ZL3b':
   for q in qq:
    if (q['paragraph'],q['grammar'])!=(p,g) or not q['patient'] or forms[q['patient']]!=n['patient_form']:continue
    qt=pos[q['patient']] if q['input_eligible']=='True' else max(pos[q['mention']],pos[q['patient']]);side='PRIOR' if qt<tick else 'FOLLOWING';eq.add(key(r)+(q['mention'],side))
    if side=='FOLLOWING':fq.append(q['mention'])
 for col,v in [('prior_mentions',prior),('following_mentions',later),('prior_actions',pa),('following_actions',fa),('following_qualities',fq)]:assert r[col]==';'.join(v)
 status='NO_PATIENT' if not n['patient'] else 'NO_PRIOR_WRITTEN_SAME_FORM' if not prior else 'PRIOR_WITH_FOLLOWING_USE' if fa or fq else 'PRIOR_WITHOUT_FOLLOWING_USE';assert r['status']==status
assert not old and {(r['edition'],r['paragraph'],r['target']) for r in out}==rawtargets
for filename,expected,idcol in [('MATERIAL_MENTIONS.tsv',em,'mention'),('PROCESSING_USES.tsv',ea,'operation'),('QUALITY_USES.tsv',eq,'mention')]:
 r=rows(E/filename);assert len(r)==len(expected) and {key(x)+(x[idcol],x['side']) for x in r}==expected
v={'status':'PASS','target_rows':120,'raw_targets':40,'same_form_processing_uses':len(ea),'primary_quality_uses':len(eq),'capacity_candidates':0,'legacy_files_verified':len(s['inputs']),'alternate_quality_coverage':'NOT_EVALUATED','semantic_confirmation':False}
(E/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
