"""Two fixed contracts for r; complete patient and follow-up consequences."""
import ast,collections,copy,csv,hashlib,json
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
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')};rules=read(W/'W05/SPEC.json')
for w,o in rules['word_overrides'].items():D[w]={**D[w],**o}
D['sheeody']={'role':'MATERIAL'};D['qokeeo']={'role':'ACTION'};ACT=set(rules['action_roles']);MAT=set(rules['material_roles'])
fn=next(n for n in ast.parse((W/'W13/build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='requal');exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_W13_requal','exec'))
base=[r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'];oldq=rows(W/'W05/QUALITY_ASSERTIONS.tsv');targets=[];contexts=[];allargs=[];future=[];quality=[];collisions=[];flats={}
for ed,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84');words=[g['ivtff_group_raw'] for g in mapped[loc]['groups']]
   if ed=='ZL3b':assert words==line['words']
   for i,w in enumerate(words,1):flat.append(dict(id=loc+':'+str(i),locus=loc,index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(flat)))
  flats[(ed,p['id'])]=flat;byid={x['id']:x for x in flat};first={}
  for x in flat:
   if x['role'] in MAT:first.setdefault(x['form'],x['id'])
  rr=[x for x in flat if x['form']=='r']
  for x in rr:contexts.append(dict(edition=ed,paragraph=p['id'],target=x['id'],raw_line=' '.join(z['form'] for z in flat if z['locus']==x['locus'])))
  for g in S['grammars']:
   old=[r for r in base if (r['edition'],r['paragraph'],r['variant'])==(ed,p['id'],g)];updated=copy.deepcopy(old);amap={a['operation']:a for a in updated};rows_for=[]
   def order(a):return max([byid[a['operation']]['offset']]+[byid[a[k]]['offset'] for k in ('patient','coingredient') if a[k]]),byid[a['operation']]['offset']
   for x in rr:
    prior=[a for a in old if byid[a['operation']]['offset']<x['offset']];after=[a for a in old if byid[a['operation']]['offset']>x['offset']];left=[z for z in flat if z['role'] in MAT and z['offset']<x['offset']]
    a=prior[-1] if prior else None;b=after[0] if after else None;m=left[-1] if left else None
    oldpatient=b['patient'] if b else '';newpatient=m['id'] if m and b else '';gap=[z for z in flat if m and b and m['offset']<z['offset']<byid[b['operation']]['offset']]
    if b:
     nb=amap[b['operation']];debt=['ASSUMED_R_PATIENT_CARRY']+['UNREAD_BETWEEN:'+z['id'] for z in gap if z['role']=='OPEN']
     if not m:debt.append('MISSING_PATIENT')
     if b['form']=='qokeor' and (not m or m['form'] not in ('cheor','okeeor','okeor','keeor','cheeor','sheeor')):debt.append('EXTRACT_PATIENT_NOT_BOUND')
     if 'MISSING_COINGREDIENT' in b['debts']:debt.append('MISSING_COINGREDIENT')
     if 'MISSING_RELATION_PARTNER' in b['debts']:debt.append('MISSING_RELATION_PARTNER')
     nb.update(patient=newpatient,patient_form=m['form'] if m else '',rule='R_PATIENT_CARRY',debts=';'.join(debt),additional_grammar_assumption=b['additional_grammar_assumption']+';R_PATIENT_CARRY')
    oldform=byid[oldpatient]['form'] if oldpatient else '';newform=m['form'] if m and b else ''
    row=dict(edition=ed,paragraph=p['id'],grammar=g,target=x['id'],prior_action=a['operation'] if a else '',next_action=b['operation'] if b else '',next_form=b['form'] if b else '',T_order='ALREADY_ORDERED' if a and b and order(a)<order(b) else 'ORDER_CONFLICT' if a and b else 'MISSING_EVENT',P_material=m['id'] if m else '',P_form=m['form'] if m else '',old_patient=oldpatient,old_form=oldform,new_patient=newpatient,new_form=newform,same_form_object=bool(oldform and oldform==newform),unread_between=';'.join(z['id'] for z in gap if z['role']=='OPEN'),intervening_materials=';'.join(z['id'] for z in gap if z['role'] in MAT),old_debts=b['debts'] if b else '',new_debts=amap[b['operation']]['debts'] if b else '',old_patient_other_uses=';'.join(z['operation'] for z in old if b and z['operation']!=b['operation'] and oldpatient and oldpatient in (z['patient'],z['coingredient'])))
    targets.append(row);rows_for.append(row)
   for model,aa in [('T',old),('P',updated)]:
    allargs.extend(dict(r,model=model) for r in aa)
    for x in rr:
     for a in aa:
      if byid[a['operation']]['offset']>x['offset']:future.append(dict(edition=ed,paragraph=p['id'],grammar=g,model=model,target=x['id'],operation=a['operation'],form=a['form'],patient=a['patient'],patient_form=a['patient_form'],coingredient=a['coingredient'],debts=a['debts']))
    runs=collections.defaultdict(list)
    for a in aa:
     if a['shared_run']:runs[a['shared_run']].append(a)
    for run,aaa in runs.items():
     if len({a['patient'] for a in aaa})>1:collisions.append(dict(edition=ed,paragraph=p['id'],grammar=g,model=model,run=run,operations=';'.join(a['operation'] for a in aaa),patients=';'.join(a['patient'] for a in aaa)))
    if ed=='ZL3b':
     for q in oldq:
      if q['paragraph']!=p['id'] or q['variant']!=g or q['kind']!='STANDALONE':continue
      qr=requal(q,flat,aa)
      if model=='T':assert all(qr[k]==q[k] for k in ('patient','patient_form','rule','debts'))
      quality.append(dict(model=model,grammar=g,paragraph=p['id'],mention=q['mention'],form=q['form'],axis=q['axis'],value=q['value'],old_patient=q['patient'],new_patient=qr['patient'],old_debts=q['debts'],new_debts=qr['debts'],rule=qr['rule']))
table('TARGETS.tsv',targets);table('CONTEXTS.tsv',contexts);table('ARGUMENTS.tsv',allargs);table('FUTURES.tsv',future);table('QUALITY_BINDINGS.tsv',quality);table('SHARED_GROUP_CONFLICTS.tsv',collisions,['edition','paragraph','grammar','model','run','operations','patients'])
result={'target_mentions':{ed:sum(r['edition']==ed for r in contexts) for ed in alt},'target_rows':len(targets),'argument_rows':len(allargs),'future_rows':len(future),'temporal_order_counts':dict(collections.Counter(r['T_order'] for r in targets)),'different_material_targets':{ed:sorted({r['target'] for r in targets if r['edition']==ed and r['old_form']!=r['new_form']}) for ed in alt},'shared_group_conflict_rows':len(collisions),'quality_patient_changes':sorted({r['mention'] for r in quality if r['model']=='P' and r['old_patient']!=r['new_patient']}),'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_access':False}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
# Full primary text with scoped alternatives, no changes to other word cards.
alignment=rows(W/'W16/ALIGNMENT.tsv');reader=['# W20 – vollständige Arbeitslesung mit r-Alternativen','','Alle Wortwerte bleiben hypothetisch. T ordnet Schritte zeitlich; P setzt den letzten Materialpatienten in den nächsten Verarbeitungsbefehl ein. M dient nur der durchgehenden Anzeige; B/J stehen vollständig in TARGETS und ARGUMENTS. Keine sho-Referenzfassung wird hier still hinzugefügt.']
for p in dict.fromkeys(r['paragraph'] for r in alignment):
 reader+=['','## '+p]
 for loc in dict.fromkeys(r['locus'] for r in alignment if r['paragraph']==p):
  rr=[r for r in alignment if r['locus']==loc];reader+=['',loc+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['joint']+(' {T: zeitlich danach / P: Materialfortführung}' if r['raw']=='r' else '')+(' {Eingangsattribut J/M}' if r['input_attribute_grammars'] else '')+(' {erneut: Vorbedingung offen}' if r['repeat_obligation']!='UNCHANGED' else '') for r in rr)]
  for t in targets:
   if t['edition']=='ZL3b' and t['grammar']=='M' and t['target'].rsplit(':',1)[0]==loc:reader+=['','T: '+t['prior_action']+' vor '+t['next_action']+'. P: '+t['next_form']+' bei '+t['next_action']+' bearbeitet '+t['new_form']+' ('+t['new_patient']+') statt '+t['old_form']+' ('+t['old_patient']+'). Offene Gruppen: '+(t['unread_between'] or 'keine')+'.']
(E/'READING.md').write_text('\n'.join(reader)+'\n')
