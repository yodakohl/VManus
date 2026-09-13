"""W11 fixed whole-word role comparison on the already exposed W02 cache."""
import ast,copy,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent; W=E.parent
ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(n,x,cols=None):
 cols=cols or list(x[0])
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=[c for c in cols if c!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in x)
S=read(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f
source=read(W/'W02/SOURCE.json'); alternate=read(W/'W02/ALTERNATE_LINES.json')['readings'];rules=read(W/'W05/SPEC.json')
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
for w,o in rules['word_overrides'].items():D[w]={**D[w],**o}
ACT=set(rules['action_roles']); MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles'])
extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
glosses={r['raw']:r['H'] for r in rows(W/'W10/ALIGNMENT.tsv')}
# Extract only the existing pure function, never execute the legacy module.
fn=next(n for n in ast.parse((W/'W05/build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='base_arguments')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_W05_base','exec'))
def solve(flat):
 versions={v:copy.deepcopy(base_arguments(flat)) for v in S['variants']}
 for locus in dict.fromkeys(x['locus'] for x in flat):
  row=[x for x in flat if x['locus']==locus];i=0
  while i<len(row):
   if row[i]['role'] not in ACT:i+=1;continue
   j=i+1
   while j<len(row) and row[j]['role'] in ACT:j+=1
   if j-i>=2:
    run=row[i:j];ids={x['id'] for x in run};rid=run[0]['id']+'-'+str(run[-1]['index'])
    for v in ('J','M'):
     pos=j
     if v=='M':
      while pos<len(row) and row[pos]['role'] in MOD:pos+=1
     if pos<len(row) and row[pos]['role'] in MAT:
      a=row[pos];tail=[];k=pos
      while k<len(row) and row[k]['role'] in MAT|MOD:
       if row[k]['role'] in MAT:tail.append(row[k])
       k+=1
      for arg in versions[v]:
       if arg['operation'] not in ids:continue
       x=next(x for x in run if x['id']==arg['operation']);b=None;debt=[]
       if x['role']=='MIX' or x['form']=='qotchy':
        b=tail[1] if len(tail)>1 else None
        if not b:debt.append('MISSING_COINGREDIENT' if x['role']=='MIX' else 'MISSING_RELATION_PARTNER')
       if x['role']=='ACTION_TYPED' and a['form'] not in extracts:debt.append('EXTRACT_PATIENT_NOT_BOUND')
       arg.update(patient=a['id'],patient_form=a['form'],coingredient=b['id'] if b else '',rule='SHARED_RIGHT_'+v,debts=';'.join(debt),shared_run=rid,additional_grammar_assumption='COMMON_ARGUMENT_OF_ADJACENT_ASSUMED_VERBS')
   i=j
 return versions
args=[];targets=[];roles=[];allflat={};qualitydebts=[]
for edition,lines in alternate.items():
 mapped={l['metadata']['locus']:l for l in lines}
 for target in source['targets']:
  p=target['hosts']['ZL3b'][0];original=[]
  for line in p['lines']:
   assert not line['locus'].startswith('f84')
   words=[g['ivtff_group_raw'] for g in mapped[line['locus']]['groups']]
   if edition=='ZL3b':assert words==line['words']
   for i,w in enumerate(words,1):original.append(dict(id=line['locus']+':'+str(i),locus=line['locus'],index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(original)))
  affected=any(x['form']=='sheeody' for x in original)
  for model,role in S['models'].items():
   flat=copy.deepcopy(original)
   for x in flat:
    if x['form']=='sheeody':x['role']=role
   allflat[(edition,p['id'],model)]=flat
   versions=solve(flat)
   for v,aa in versions.items():
    for a in aa:
     op=next(x for x in flat if x['id']==a['operation']);following=next((x for x in flat if x['offset']==op['offset']+1 and x['locus']==op['locus']),None)
     tool=following['id'] if model=='T' and op['form']=='ckhy' and following and following['role']=='TOOL' else ''
     args.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],**a,instrument=tool,instrument_assumption='UNMARKED_RIGHT_TOOL_AFTER_CKHY' if tool else ''))
   for x in flat:
    if x['form']=='sheeody':
     left=next((y for y in flat if y['offset']==x['offset']-1 and y['locus']==x['locus']),None)
     uses=[(v,a) for v,aa in versions.items() for a in aa if x['id'] in (a['patient'],a['coingredient'])]
     targets.append(dict(edition=edition,model=model,paragraph=p['id'],mention=x['id'],role=role,left=left['form'] if left else '',material_uses=';'.join(v+':'+a['operation'] for v,a in uses),raw_line=' '.join(y['form'] for y in flat if y['locus']==x['locus'])))
    if affected and (x['form'] in ('lor','ckhy') or x['role']=='MATERIAL_DOSE'):
     right=next((y for y in flat if y['offset']==x['offset']+1 and y['locus']==x['locus']),None)
     prior=[y for y in flat if y['locus']==x['locus'] and y['offset']<x['offset'] and y['role'] in ACT]
     relation='FIXED_OWN_MATERIAL_DOSE' if x['role']=='MATERIAL_DOSE' else 'ACTION_PATIENTS_IN_ARGUMENTS' if x['form']=='ckhy' else 'TOOL_PHRASE' if right and right['role']=='TOOL' else 'MATERIAL_ACCOMPANIMENT' if right and right['role'] in MAT else 'UNRESOLVED_COMPLEMENT'
     roles.append(dict(edition=edition,model=model,paragraph=p['id'],mention=x['id'],form=x['form'],relation=relation,right=right['id'] if right else '',governing_action=prior[-1]['id'] if prior and x['form']=='lor' else '',debt='MISSING_GOVERNING_ACTION' if x['form']=='lor' and not prior else 'NO_ADJACENCY_BASED_DOSE_TRANSFER' if x['role']=='MATERIAL_DOSE' else ''))
base={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W05/ARGUMENTS.tsv')}
compare=['patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption']
for r in args:
 if r['model']=='U':assert all(r[k]==base[(r['edition'],r['variant'],r['operation'])][k] for k in compare),r
changes=[]
for r in args:
 old=base[(r['edition'],r['variant'],r['operation'])]
 if r['model']!='U' and any(r[k]!=old[k] for k in compare):
  changes.append(dict(edition=r['edition'],model=r['model'],variant=r['variant'],paragraph=r['paragraph'],operation=r['operation'],form=r['form'],old_patient=old['patient'],new_patient=r['patient'],old_second=old['coingredient'],new_second=r['coingredient'],old_debts=old['debts'],new_debts=r['debts']))
for q in rows(W/'W05/QUALITY_ASSERTIONS.tsv'):
 for c in changes:
  if c['edition']!='ZL3b' or c['variant']!=q['variant'] or c['paragraph']!=q['paragraph']:continue
  if c['operation']==q['mention'] or c['operation'] in q['debts']:
   qualitydebts.append(dict(model=c['model'],variant=c['variant'],operation=c['operation'],quality_mention=q['mention'],old_patient=q['patient'],new_action_patient=c['new_patient'],status='NOT_RECOMPUTED_NO_STATE_CLAIM'))
table('ARGUMENTS.tsv',args);table('TARGETS.tsv',targets);table('ROLE_CENSUS.tsv',roles)
table('CHANGES.tsv',changes,['edition','model','variant','paragraph','operation','form','old_patient','new_patient','old_second','new_second','old_debts','new_debts'])
table('QUALITY_DEBTS.tsv',qualitydebts,['model','variant','operation','quality_mention','old_patient','new_action_patient','status'])
alignment=[];reading=['# W11 — vollständige exponierte Arbeitsabsätze','Alle Werte sind Hypothesen. D/H bleiben trockne/erhitze-Rivalen; hier H angezeigt. Nur sheeody wird in T/P ergänzt.']
for r in rows(W/'W10/ALIGNMENT.tsv'):
 alignment.append(dict(r,U=r['H'],T='Mörser [Werkzeughypothese]' if r['raw']=='sheeody' else r['H'],P='Pulver [Materialhypothese]' if r['raw']=='sheeody' else r['H']))
for p in dict.fromkeys(r['paragraph'] for r in alignment):
 reading+=['','## '+p]
 for locus in dict.fromkeys(r['locus'] for r in alignment if r['paragraph']==p):
  rr=[r for r in alignment if r['locus']==locus]
  reading+=['',locus+': `'+' '.join(r['raw'] for r in rr)+'`','', ' · '.join('{T: '+r['T']+' / P: '+r['P']+' / U: ungelesen}' if r['raw']=='sheeody' else r['H'] for r in rr)]
table('ALIGNMENT.tsv',alignment);(E/'READING.md').write_text('\n'.join(reading)+'\n')
# Entire alternate contexts, not snippets or normalized words.
altreading=['# W11 — vollständige IT/RF-Projektionen der betroffenen ZL-Absätze','Gleiche Manuskriptstellen, keine unabhängige Bestätigung; keine behaupteten IT/RF-Absatzgrenzen.']
for (edition,p,model),flat in allflat.items():
 if edition=='ZL3b' or model!='U' or not any(x['form']=='sheeody' for x in flat):continue
 altreading+=['','## '+edition+' '+p]
 for locus in dict.fromkeys(x['locus'] for x in flat):altreading+=['',locus+': `'+' '.join(x['form'] for x in flat if x['locus']==locus)+'`']
(E/'ALTERNATE_CONTEXTS.md').write_text('\n'.join(altreading)+'\n')
result={'baseline_parity':True,'primary_groups':len(alignment),'primary_unread_U':sum(r['status']=='UNREAD' for r in alignment),'primary_unread_T_P':sum(r['status']=='UNREAD' and r['raw']!='sheeody' for r in alignment),'targets_by_reading':{e:sum(r['edition']==e and r['model']=='U' for r in targets) for e in alternate},'changed_argument_rows':len(changes),'instrument_rows':sum(bool(r['instrument']) for r in args),'quality_debts':len(qualitydebts),'meanings_confirmed':0,'independent_confirmation_capacity':0,'sealed_access':False}
save('RESULT.json',result);print(json.dumps(result))
