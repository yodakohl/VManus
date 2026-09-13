"""Complete capacity census for fixed take-patient identity alternatives."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];takes=[r for r in rows(W/'W16/TAKE_ARGUMENTS.tsv') if r['model']=='PR'];args=[r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'];qs=[r for r in rows(W/'W16/QUALITY_BINDINGS.tsv') if r['model']=='PR'];fx=read(W/'W09/SPEC.json')['effects'];fx['chol']={'axis':'thermal','value':'hot'};flats={};contexts=[]
for ed,ll in alt.items():
 lines={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84')
   if ed=='ZL3b':assert lines[loc]==line['words']
   for i,w in enumerate(lines[loc],1):
    flat.append(dict(id=loc+':'+str(i),form=w,offset=len(flat),locus=loc))
    if w=='ychor':contexts.append(dict(edition=ed,paragraph=p['id'],target=loc+':'+str(i),raw_line=' '.join(lines[loc])))
  flats[(ed,p['id'])]=flat
out=[];mentions=[];actions=[];qualities=[]
for n in takes:
 ed,p,g=n['edition'],n['paragraph'],n['grammar'];flat=flats[(ed,p)];byid={x['id']:x for x in flat};x=byid[n['target']];patient=byid.get(n['patient']);tick=max(x['offset'],patient['offset'] if patient else x['offset']);prior=[];later=[];preactions=[];postactions=[];postqualities=[]
 for z in flat:
  if not patient or z['form']!=patient['form']:continue
  side='PRIOR' if z['offset']<x['offset'] else 'FOLLOWING_MENTION' if z['offset']>tick else 'TAKE_PATIENT'
  if side=='PRIOR':prior.append(z)
  if side=='FOLLOWING_MENTION':later.append(z)
  mentions.append(dict(edition=ed,paragraph=p,grammar=g,target=x['id'],patient_form=n['patient_form'],mention=z['id'],side=side))
 for a in args:
  if not patient or (a['edition'],a['paragraph'],a['variant'])!=(ed,p,g):continue
  roles=[k for k in ('patient','coingredient') if a[k] and byid[a[k]]['form']==patient['form']]
  if not roles:continue
  at=max([byid[a['operation']]['offset']]+[byid[a[k]]['offset'] for k in ('patient','coingredient') if a[k]])
  side='PRIOR' if at<tick else 'FOLLOWING';(preactions if side=='PRIOR' else postactions).append(a)
  actions.append(dict(edition=ed,paragraph=p,grammar=g,target=x['id'],operation=a['operation'],form=a['form'],patient=a['patient'],patient_form=a['patient_form'],same_form_roles=','.join(roles),side=side,execution_offset=at,effect_card=json.dumps(fx.get(a['form']),sort_keys=True),debts=a['debts']))
 if ed=='ZL3b':
  for q in qs:
   if not patient or (q['paragraph'],q['grammar'])!=(p,g) or not q['patient'] or byid[q['patient']]['form']!=patient['form']:continue
   qt=byid[q['patient']]['offset'] if q['input_eligible']=='True' else max(byid[q['mention']]['offset'],byid[q['patient']]['offset']);side='PRIOR' if qt<tick else 'FOLLOWING'
   if side=='FOLLOWING':postqualities.append(q)
   qualities.append(dict(edition=ed,paragraph=p,grammar=g,target=x['id'],mention=q['mention'],patient=q['patient'],form=q['form'],axis=q['axis'],value=q['value'],side=side,debts=q['debts']))
 status='NO_PATIENT' if not patient else 'NO_PRIOR_WRITTEN_SAME_FORM' if not prior else 'PRIOR_WITH_FOLLOWING_USE' if postactions or postqualities else 'PRIOR_WITHOUT_FOLLOWING_USE'
 out.append(dict(edition=ed,paragraph=p,grammar=g,target=x['id'],patient=n['patient'],patient_form=n['patient_form'],status=status,prior_mentions=';'.join(z['id'] for z in prior),prior_actions=';'.join(a['operation'] for a in preactions),following_actions=';'.join(a['operation'] for a in postactions),following_qualities=';'.join(q['mention'] for q in postqualities),following_mentions=';'.join(z['id'] for z in later),take_debts=n['debts']))
table('TARGETS.tsv',out);table('MATERIAL_MENTIONS.tsv',mentions);table('PROCESSING_USES.tsv',actions);table('QUALITY_USES.tsv',qualities,['edition','paragraph','grammar','target','mention','patient','form','axis','value','side','debts']);table('CONTEXTS.tsv',contexts)
result={'take_rows':len(out),'raw_targets':len(contexts),'counts':{ed:dict(collections.Counter(r['status'] for r in out if r['edition']==ed)) for ed in alt},'candidate_loci':{ed:sorted({r['target'] for r in out if r['edition']==ed and r['status']=='PRIOR_WITH_FOLLOWING_USE'}) for ed in alt},'processing_use_rows':len(actions),'quality_use_rows':len(qualities),'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_access':False,'state_simulation':False}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
