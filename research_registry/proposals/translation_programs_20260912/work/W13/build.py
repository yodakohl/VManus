"""W13 complete nominal ychor rival, frozen action and quality attachment rules."""
import ast,copy,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def js(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def table(n,rr,cols=None):
 cols=cols or list(rr[0])
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=[k for k in cols if k!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=js(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];rules=js(W/'W05/SPEC.json')
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
for word,o in rules['word_overrides'].items():D[word]={**D[word],**o}
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
alignment=rows(W/'W10/ALIGNMENT.tsv');glosses={r['raw']:r['H'] for r in alignment}
for path,name in [(W/'W05/build.py','base_arguments'),(W/'W11/build.py','solve')]:
 fn=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path),'exec'))
old={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W05/ARGUMENTS.tsv')}
takes={(r['edition'],r['grammar'],r['target']):r for r in rows(W/'W08/TAKE_ARGUMENTS.tsv')};oldq=rows(W/'W05/QUALITY_ASSERTIONS.tsv')
args=[];targets=[];repeats=[];changes=[];qualities=[];qchanges=[];future=[];primary_flat={}
cols=['patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption']
def requal(q,flat,aa):
 r=q.copy();byid={x['id']:x for x in flat};byop={a['operation']:a for a in aa};x=byid[q['mention']];ops=[y for y in flat if y['role'] in ACT];mats=[y for y in flat if y['role'] in MAT]
 if q['kind']=='ACTION_EFFECT':
  a=byop[q['mention']];r.update(patient=a['patient'],patient_form=a['patient_form'],debts=a['debts']);return r
 if q['kind']!='STANDALONE':return r
 prev=[a for a in ops if a['locus']==x['locus'] and a['offset']<x['offset']]
 lo=prev[-1]['offset'] if prev else -1;hi=min([a['offset'] for a in ops if a['locus']==x['locus'] and a['offset']>x['offset']],default=10**9)
 local=[m for m in mats if m['locus']==x['locus'] and lo<m['offset']<hi];left=[m for m in local if m['offset']<x['offset']];right=[m for m in local if m['offset']>x['offset']]
 a=left[-1] if left else right[0] if right else None;rule='LOCAL_LEFT' if left else 'LOCAL_RIGHT' if right else 'MISSING';debt=[]
 if not a and prev:
  ar=byop[prev[-1]['id']];a=byid.get(ar['patient'])
  if a:
   rule='ACTION_RESULT_REFERENCE';debt.append('ASSUMED_RESULT_OR_PROCESS_CONDITION:'+prev[-1]['id'])
   if ar['debts']:debt.append(ar['debts'])
 if a:
  lo,hi=sorted((a['offset'],x['offset']));debt+=['UNREAD_BETWEEN:'+v['id'] for v in flat if lo<v['offset']<hi and v['role']=='OPEN']
 else:debt.append('MISSING_MATERIAL_BINDING')
 r.update(patient=a['id'] if a else '',patient_form=a['form'] if a else '',rule=rule,debts=';'.join(debt));return r
for edition,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];raw=[]
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84');ww=[g['ivtff_group_raw'] for g in mapped[loc]['groups']]
   if edition=='ZL3b':assert ww==line['words']
   for i,w in enumerate(ww,1):raw.append(dict(id=loc+':'+str(i),locus=loc,index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(raw)))
  if edition=='ZL3b':primary_flat[p['id']]=raw
  for model in S['models']:
   flat=copy.deepcopy(raw)
   for x in flat:
    if x['form']=='ychor' and model=='P':x['role']='MATERIAL'
   byid={x['id']:x for x in flat};versions=solve(flat)
   for v,aa in versions.items():
    for a in aa:
     prior=old[(edition,v,a['operation'])]
     if model in ('A','N'):assert all(a[k]==prior[k] for k in cols)
     args.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],**a))
     if model=='P' and any(a[k]!=prior[k] for k in cols):changes.append(dict(edition=edition,variant=v,paragraph=p['id'],operation=a['operation'],form=a['form'],old_patient=prior['patient'],old_form=prior['patient_form'],new_patient=a['patient'],new_form=a['patient_form'],old_second=prior['coingredient'],new_second=a['coingredient'],old_rule=prior['rule'],new_rule=a['rule'],old_debts=prior['debts'],new_debts=a['debts']))
    for x in [x for x in flat if x['form']=='ychor']:
     take=takes[(edition,v,x['id'])]
     uses=[a for a in aa if x['id'] in (a['patient'],a['coingredient'])]
     targets.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],mention=x['id'],meaning={'A':'ferner','N':'nimm','P':'Blüten [gleiche Klasse wie chor, hypothetisch]'}[model],added_commands=int(model=='N'),added_material_mentions=int(model=='P'),take_patient=take['patient'] if model=='N' else '',take_patient_form=take['patient_form'] if model=='N' else '',take_debts=take['debts'] if model=='N' else '',material_uses=';'.join(a['operation'] for a in uses) if model=='P' else '',raw_line=' '.join(y['form'] for y in flat if y['locus']==x['locus'])))
     for a in aa:
      if byid[a['operation']]['offset']<=x['offset']:continue
      future.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],target=x['id'],later_action=a['operation'],form=a['form'],patient=a['patient'],patient_form=a['patient_form'],is_target_patient=a['patient']==x['id'],debts=a['debts']))
     if model=='N':args.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],operation=x['id'],form='ychor',meaning='nimm',patient=take['patient'],patient_form=take['patient_form'],coingredient='',rule=take['rule'],debts=take['debts'],shared_run='',additional_grammar_assumption='FROZEN_W08_TAKE_CONTRACT'))
    if edition=='ZL3b':
     for q in oldq:
      if q['variant']!=v or q['paragraph']!=p['id']:continue
      qr=requal(q,flat,aa)
      if model in ('A','N'):assert all(qr[k]==q[k] for k in ('patient','patient_form','rule','debts')),(q,qr)
      r={k:val for k,val in (qr if model=='P' else q).items() if k not in ('phase','row_status')};r.update(model=model,old_phase_not_recomputed=q['phase'])
      qualities.append(r)
      if model=='P' and any(qr[k]!=q[k] for k in ('patient','patient_form','rule','debts')):qchanges.append(dict(variant=v,paragraph=p['id'],mention=q['mention'],form=q['form'],kind=q['kind'],axis=q['axis'],value=q['value'],old_patient=q['patient'],old_form=q['patient_form'],new_patient=qr['patient'],new_form=qr['patient_form'],old_rule=q['rule'],new_rule=qr['rule'],old_debts=q['debts'],new_debts=qr['debts']))
  for x in [x for x in raw if x['form']=='ychor']:
   for y in raw:
    if y['form']=='chor':repeats.append(dict(edition=edition,paragraph=p['id'],target=x['id'],chor=y['id'],relative='AFTER' if y['offset']>x['offset'] else 'BEFORE',direct_next=y['offset']==x['offset']+1 and y['locus']==x['locus'],identity='SAME_RENAMING_OR_FRESH_PORTION_UNRESOLVED'))
table('ARGUMENTS.tsv',args);table('TARGETS.tsv',targets);table('CHOR_CENSUS.tsv',repeats);table('FUTURES.tsv',future);table('BODY_CHANGES.tsv',changes);table('QUALITY_ASSERTIONS.tsv',qualities);table('QUALITY_CHANGES.tsv',qchanges)
full=[];reader=['# W13 — drei vollständige ychor-Fassungen','Alle Wortwerte hypothetisch. N aus W08, A allgemeines ferner, P ganze Materialform ohne Präfixregel. H angezeigt, D bleibt offen; keine W11/W12-Auswahl.']
for r in alignment:full.append(dict(r,A='ferner' if r['raw']=='ychor' else r['H'],N=r['H'],P='Blüten [ychor=chor-Klasse?]' if r['raw']=='ychor' else r['H']))
for p in dict.fromkeys(r['paragraph'] for r in full):
 reader+=['','## '+p]
 for loc in dict.fromkeys(r['locus'] for r in full if r['paragraph']==p):
  rr=[r for r in full if r['locus']==loc];reader+=['',loc+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join('{A: ferner / N: nimm / P: Blüten?}' if r['raw']=='ychor' else r['H'] for r in rr)]
table('ALIGNMENT.tsv',full);(E/'READING.md').write_text('\n'.join(reader)+'\n')
result={'primary_groups':len(full),'target_counts':{e:sum(t['edition']==e and t['model']=='A' and t['variant']=='B' for t in targets) for e in alt},'argument_rows':len(args),'body_change_rows':len(changes),'primary_body_patient_change_operations':sorted({r['operation'] for r in changes if r['edition']=='ZL3b' and r['old_patient']!=r['new_patient']}),'primary_quality_change_mentions':sorted({r['mention'] for r in qchanges if r['old_patient']!=r['new_patient']}),'direct_ychor_chor_pairs':sum(r['edition']=='ZL3b' and r['direct_next'] for r in repeats),'baseline_parity':True,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_access':False}
save('RESULT.json',result);print(json.dumps(result))
