"""Fixed qokeeo comparison; source already exposed, no decoder or state repair."""
import ast,copy,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def js(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def table(n,data,columns=None):
 columns=columns or list(data[0])
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=[c for c in columns if c!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in data)
S=js(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];rules=js(W/'W05/SPEC.json')
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
for word,o in rules['word_overrides'].items():D[word]={**D[word],**o}
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles'])
extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
alignment=rows(W/'W10/ALIGNMENT.tsv');glosses={r['raw']:r['H'] for r in alignment}
for path,name in [(W/'W05/build.py','base_arguments'),(W/'W11/build.py','solve')]:
 node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'))
old={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W05/ARGUMENTS.tsv')}
allargs=[];targets=[];observables=[];sequences=[];contexts=[];changed=[];futures=[]
comparison=['patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption']
for edition,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];raw=[]
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84');ww=[g['ivtff_group_raw'] for g in mapped[loc]['groups']]
   if edition=='ZL3b':assert ww==line['words']
   for i,word in enumerate(ww,1):raw.append(dict(id=loc+':'+str(i),locus=loc,index=i,offset=len(raw),form=word,role=D.get(word,{}).get('role','OPEN')))
  affected=any(x['form']=='qokeeo' for x in raw)
  for model,role in S['models'].items():
   flat=copy.deepcopy(raw)
   D['qokeeo']={'role':role,'hypothesis':{'U':'[ungelesen: qokeeo]','R':'rühre','C':'fahre mit der vorherigen Handlung fort'}[model]}
   glosses['qokeeo']=D['qokeeo']['hypothesis']
   for x in flat:
    if x['form']=='qokeeo':x['role']=role
   byid={x['id']:x for x in flat};versions=solve(flat)
   for v,aa in versions.items():
    amap={a['operation']:a for a in aa}
    for a in aa:
     allargs.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],**a))
     prior=old.get((edition,v,a['operation']))
     if model=='U':assert prior and all(a[k]==prior[k] for k in comparison),(edition,a)
     elif prior and any(a[k]!=prior[k] for k in comparison):
      changed.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],operation=a['operation'],old_patient=prior['patient'],new_patient=a['patient'],old_debts=prior['debts'],new_debts=a['debts'],old_rule=prior['rule'],new_rule=a['rule']))
    for x in flat:
     if not affected:continue
     if x['form']=='qokeeo':
      antecedent='';a=None;debts=[]
      if model=='R':a=amap[x['id']];debts=[d for d in a['debts'].split(';') if d]
      elif model=='C':
       earlier=[y for y in flat if y['offset']<x['offset'] and y['role'] in ACT and y['form']!='qokeeo']
       if not earlier:debts.append('MISSING_ANTECEDENT_ACTION')
       else:
        op=earlier[-1];antecedent=op['id'];a=amap[antecedent]
        if not a['patient']:debts.append('MISSING_INHERITED_PATIENT')
        debts+=['ANTECEDENT_UNREAD_BETWEEN:'+y['id'] for y in flat if op['offset']<y['offset']<x['offset'] and y['role']=='OPEN']
        if op['locus']!=x['locus']:debts.append('CROSS_LINE_ACTION_CARRY')
        debts.append('ONGOING_ACTION_NOT_ESTABLISHED')
        debts+=['INHERITED:'+d for d in a['debts'].split(';') if d]
      else:debts.append('UNREAD_WORD')
      patient=a['patient'] if a else ''
      gap=[y['id'] for y in flat if patient and byid[patient]['offset']<y['offset']<x['offset'] and y['role']=='OPEN']
      targets.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],mention=x['id'],meaning=D['qokeeo']['hypothesis'],antecedent=antecedent,antecedent_form=byid[antecedent]['form'] if antecedent else '',patient=patient,patient_form=a['patient_form'] if a else '',patient_to_target_unread=';'.join(gap),debts=';'.join(debts),new_mechanical_event=model=='R',raw_line=' '.join(y['form'] for y in flat if y['locus']==x['locus'])))
     if x['role'] in ACT or x['form']=='qokeeo':
      a=amap.get(x['id']);tr=next((z for z in reversed(targets) if z['edition']==edition and z['model']==model and z['variant']==v and z['mention']==x['id']),None) if x['form']=='qokeeo' else None
      sequences.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],position=x['offset'],mention=x['id'],form=x['form'],meaning=glosses.get(x['form'],D.get(x['form'],{}).get('hypothesis','OPEN')),patient=(tr or a or {}).get('patient',''),antecedent=tr['antecedent'] if tr else '',debts=(tr or a or {}).get('debts','')))
     if x['role'] in {'AMOUNT','NUMBER','DISTRIBUTIVE','STATE','QUALITY_VALUE','MATERIAL_DOSE','MATERIAL'}:
      observables.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],mention=x['id'],form=x['form'],role=x['role'],meaning=glosses.get(x['form'],D.get(x['form'],{}).get('hypothesis','OPEN')),interpretation='UNCHANGED_NO_NEW_STIR_DURATION_OR_CONTINUATION_BINDING'))
    if affected:
     for target in [z for z in targets if z['edition']==edition and z['model']==model and z['variant']==v and z['paragraph']==p['id']]:
      for a in aa:
       if byid[a['operation']]['offset']<=byid[target['mention']]['offset']:continue
       futures.append(dict(edition=edition,model=model,variant=v,paragraph=p['id'],target=target['mention'],later_action=a['operation'],form=a['form'],patient=a['patient'],same_written_patient=bool(target['patient'] and a['patient']==target['patient']),debts=a['debts']))
   if affected:
    for line in p['lines']:
     rr=[x for x in flat if x['locus']==line['locus']]
     contexts.append(dict(edition=edition,model=model,paragraph=p['id'],locus=line['locus'],raw=' '.join(x['form'] for x in rr),reading=' · '.join(glosses.get(x['form'],'[ungelesen: '+x['form']+']') for x in rr)))
table('ARGUMENTS.tsv',allargs);table('TARGETS.tsv',targets);table('EVENT_SEQUENCE.tsv',sequences);table('OBSERVABLES.tsv',observables);table('FUTURES.tsv',futures);table('CONTEXTS.tsv',contexts)
table('OLD_ARGUMENT_CHANGES.tsv',changed,['edition','model','variant','paragraph','operation','old_patient','new_patient','old_debts','new_debts','old_rule','new_rule'])
full=[];reader=['# W12 — vollständige primäre Arbeitslesung','W10 H angezeigt; D bleibt Rivale. W11 sheeody nicht ausgewählt. Alle Wortwerte hypothetisch.']
for r in alignment:
 full.append(dict(r,U=r['H'],R='rühre' if r['raw']=='qokeeo' else r['H'],C='fahre mit der vorherigen Handlung fort' if r['raw']=='qokeeo' else r['H']))
for p in dict.fromkeys(r['paragraph'] for r in full):
 reader+=['','## '+p]
 for loc in dict.fromkeys(r['locus'] for r in full if r['paragraph']==p):
  rr=[r for r in full if r['locus']==loc]
  reader+=['',loc+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join('{R: rühre / C: fahre fort / U: ungelesen}' if r['raw']=='qokeeo' else r['H'] for r in rr)]
table('ALIGNMENT.tsv',full);(E/'READING.md').write_text('\n'.join(reader)+'\n')
result={'primary_groups':len(full),'primary_targets':sum(r['raw']=='qokeeo' for r in full),'targets_by_reading':{e:sum(t['edition']==e and t['model']=='U' and t['variant']=='B' for t in targets) for e in alt},'baseline_parity':True,'argument_rows':len(allargs),'old_argument_changed_rows':len(changed),'old_patient_changes':sum(r['old_patient']!=r['new_patient'] for r in changed),'new_stirring_events_primary_B':sum(r['edition']=='ZL3b' and r['model']=='R' and r['variant']=='B' for r in targets),'unread_primary_U':sum(r['status']=='UNREAD' for r in full),'unread_primary_R_C':sum(r['status']=='UNREAD' and r['raw']!='qokeeo' for r in full),'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_access':False}
save('RESULT.json',result);print(json.dumps(result))
