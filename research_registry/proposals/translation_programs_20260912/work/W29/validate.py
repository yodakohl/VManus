"""Independent name-account and state audit; no W09 execute/W14 replay imports."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;B=W/'W28';ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
source=read(B/'SOURCE.json')['paragraphs'];assert len(source)==17
flat={sm:rows(B/(sm+'_SOURCE_FLAT.tsv')) for sm in ['Q','A']}
T=rows(E/'TARGETS.tsv');events=rows(E/'EVENTS.tsv');worlds=collections.defaultdict(list)
keys=['shol','paragraph','grammar','chol','timing','target']
for r in events:worlds[tuple(r[k] for k in keys)+ (r['reference'],)].append(r)
assert len(T)==48 and len(worlds)==96
expected_targets=[]
for sm in ['Q','A']:
 for p in source:
  for x in flat[sm]:
   if x['paragraph']==p['id'] and x['form']=='sal':
    assert not x['locus'].startswith('f84')
    for g in ['B','J','M']:
     for m in ['D','H']:
      for timing in ['O','I']:expected_targets.append((sm,p['id'],g,m,timing,x['id']))
assert {tuple(r[k] for k in keys) for r in T}==set(expected_targets)
later=[];changes=[];newconflicts=0
for t in T:
 key=tuple(t[k] for k in keys);sm,p,g,m,timing,target=key;ff=[r for r in flat[sm] if r['paragraph']==p];byid={r['id']:r for r in ff};off=int(byid[target]['offset']);parents=[r for r in ff if int(r['offset'])<off and r['role'] in ['MATERIAL','MATERIAL_DOSE']];parent=parents[-1];assert (t['antecedent'],t['antecedent_form'])==(parent['id'],parent['form'])
 trE=worlds[key+('E',)];trR=worlds[key+('R',)];old=[r for r in rows(B/(sm+'_EVENTS.tsv')) if (r['paragraph'],r['grammar'],r['model'],r['timing'])==(p,g,m,timing)]
 assert len(trE)==len(trR)==len(old)
 for a,b in zip(trE,old):assert all(a[k]==v for k,v in b.items() if k!='model')
 for ref,trace in [('E',trE),('R',trR)]:
  names={};mentions={};state={};origin={};effects=read(W/'W09/SPEC.json')['effects'];effects['chol']=S['models'][m]
  if sm=='A':effects['shol']={'axis':'moisture','value':'wet'}
  for idx,r in enumerate(trace):
   assert int(r['execution_index'])==idx
   if r['kind']=='MATERIAL':
    form=r['form'];loc=r['location']
    if loc==target and ref=='R':names[form]=names[parent['form']];expected='RENAMED_EXISTING_PORTION'
    elif form in names:expected='SAME_FORM_REMENTION'
    else:names[form]=loc;expected='EXTERNAL_PORTION'
    oid=names[form];mentions[loc]=oid;state.setdefault(oid,{});assert r['status']==expected and r['object']==oid
   elif r['kind']=='ACTION':
    oid=mentions.get(r['patient'],'');assert r['object']==oid and r['second_object']==mentions.get(r['second'],'')
   elif r['kind']=='QUALITY':oid=mentions.get(r['patient'],'');assert r['object']==oid
   else:oid=mentions[r['location']];assert r['object']==oid
   before=state.get(oid,{}).copy();assert json.loads(r['before'])==before
   if r['kind']=='ACTION':
    effect=effects.get(r['form']);assert (json.loads(r['assertion']) if r['assertion'] else None)==effect
    invalid=not oid or any(d in r['debts'].split(';') for d in ['EXTRACT_PATIENT_NOT_BOUND','MISSING_RELATION_PARTNER'])
    assert r['status']==('ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED')
    if not invalid and effect:k='PHYSICAL:'+effect['axis'];state[oid][k]=effect['value'];origin[oid,k]=r['location']
   elif r['kind']!='MATERIAL':
    k,v=r['assertion'].split('=',1);prior=before.get(k);opp=k.endswith(':moisture') and {prior,v}=={'wet','dry'} or k.endswith(':thermal') and ((prior=='cold' and v in ['warm','hot']) or (v=='cold' and prior in ['warm','hot']))
    expected='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if prior is None else 'MATCH' if prior==v else 'CONFLICT' if opp else 'DIFFERENT_NOT_OPPOSED'
    assert r['status']==expected and r['state_origin']==origin.get((oid,k),'')
    if oid and prior is None:state[oid][k]=v;origin[oid,k]=r['location']
   assert json.loads(r['after'])==state.get(oid,{})
 targetindex=next(i for i,r in enumerate(trE) if r['kind']=='MATERIAL' and r['location']==target);targetoid=trE[targetindex]['object'];parentoid=next(r['object'] for r in trE if r['kind']=='MATERIAL' and r['location']==parent['id']);assert parentoid==t['antecedent_object']
 assert t['E_state']==trE[targetindex]['before'] and t['R_state']==trR[targetindex]['before']
 earlier=[r['location'] for r in trE[:targetindex] if r['kind']=='ACTION' and r['object']==parentoid and int(byid[r['location']]['offset'])<off and int(r['order'])<off and r['status']=='ASSUMED_EFFECT_APPLIED'];assert t['earlier_applied_actions']==';'.join(earlier)
 for i,(a,b) in enumerate(zip(trE,trR)):
  assert all(a[k]==b[k] for k in ['kind','location','form','patient','second','assertion','order'])
  payload=['order','kind','location','form','patient','second','object','second_object','source_object','before','after','assertion','status','debts','state_origin','alias_collision']
  if any(a[k]!=b[k] for k in payload):changes.append((key,a['source_event']))
  if b['status']=='CONFLICT' and a['status']!='CONFLICT':newconflicts+=1
  if i>targetindex and a['kind']!='MATERIAL' and (a['object'] in [parentoid,targetoid] or a['second_object'] in [parentoid,targetoid]):later.append((key,a['source_event'],a['location'],a['kind'],a['status'],b['status']))
C=rows(E/'ALL_CHANGES.tsv');assert collections.Counter(changes)==collections.Counter((tuple(r[k] for k in keys),r['event']) for r in C)
L=rows(E/'ALL_LATER_REQUIREMENTS.tsv');assert collections.Counter(later)==collections.Counter((tuple(r[k] for k in keys),r['event'],r['location'],r['kind'],r['E_status'],r['R_status']) for r in L)
a=rows(E/'F93R_ALIGNMENT.tsv');assert a==[r for r in rows(B/'A_ALIGNMENT.tsv') if r['paragraph'].startswith('f93r|')];assert len(a)==152 and len(set(r['locus'] for r in a))==32
text=(E/'F93R_READING.md').read_text()
for loc in dict.fromkeys(r['locus'] for r in a):assert text.count('`'+' '.join(r['raw'] for r in a if r['locus']==loc)+'`')==1
assert rows(E/'F93R_ARGUMENTS.tsv')==[r for r in rows(B/'A_ARGUMENTS.tsv') if r['paragraph'].startswith('f93r|')]
assert rows(E/'F93R_TAKE.tsv')==[r for r in rows(B/'A_TAKE_ARGUMENTS.tsv') if r['paragraph'].startswith('f93r|')]
r=read(E/'RESULT.json');assert r['events']==len(events) and r['changes']==len(C) and r['later_requirements']==len(L) and r['new_R_conflicts']==newconflicts and r['constraint_discriminators']==sum(a[3]!='ACTION' and a[4]!=a[5] for a in later)
out=dict(status='PASS',bound_files=len(S['inputs']),independent_account_and_state_events=len(events),target_cases=len(T),all_later_requirements=len(L),changes=len(C),f93r_groups=len(a),f93r_lines=32,baseline_target_parity=True,limits='Independent state/account implementation; lexical meanings and grammar remain hypotheses; no independent meaning confirmation')
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
