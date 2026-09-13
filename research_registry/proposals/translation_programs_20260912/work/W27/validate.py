"""Independent exhaustive ancestry eligibility and future-capacity audit."""
import collections,csv,json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
ff=rows(W/'W26/Q_SOURCE_FLAT.tsv');byid={x['id']:x for x in ff};para=collections.defaultdict(list)
for x in ff:x['offset']=int(x['offset']);para[x['paragraph']].append(x)
pp=rows(E/'ALL_ACTION_PAIRS.tsv');pairix={(r['shol'],r['paragraph'],r['grammar'],r['chol'],r['timing'],r['target'],r['operation']):r for r in pp};tt=rows(E/'TARGETS.tsv');targetix={(r['shol'],r['paragraph'],r['grammar'],r['chol'],r['timing'],r['target']):r for r in tt};gg=rows(E/'ORIGIN_GROUPS.tsv');seenpairs=set();seentargets=set();expected_groups={};expected_later=[]
for sm in ['Q','A']:
 worlds=collections.defaultdict(list)
 for r in rows(W/('W26/'+sm+'_EVENTS.tsv')):worlds[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
 for key,trace in worlds.items():
  p,g,c,t=key;indices={id(r):i for i,r in enumerate(trace)}
  for x in para[p]:
   if x['form'] not in S['target_forms']:continue
   tk=(sm,p,g,c,t,x['id']);seentargets.add(tk);first=not any(y['form']==x['form'] and y['offset']<x['offset'] for y in para[p]);target=next(r for r in trace if r['kind']=='MATERIAL' and r['location']==x['id']);ti=indices[id(target)];objects=collections.defaultdict(list);eligible_count=0;n=0
   for a in trace:
    if a['kind']!='ACTION' or byid[a['location']]['offset']>=x['offset']:continue
    n+=1;pk=(*tk,a['location']);seenpairs.add(pk);r=pairix[pk];patient=byid.get(a['patient']);earlier_same=[z for z in trace[:ti] if a['object'] and z['object']==a['object']];state=json.loads(earlier_same[-1]['after']) if earlier_same else {};wet=state.get('PHYSICAL:moisture','')
    checks=[(first,'REPEAT_NOT_NEW_NAME'),(bool(patient),'MISSING_PATIENT'),(not patient or patient['offset']<x['offset'],'PATIENT_NOT_WRITTEN_BEFORE_TARGET'),(indices[id(a)]<ti,'ACTION_NOT_EXECUTED_BEFORE_TARGET'),(a['status']=='ASSUMED_EFFECT_APPLIED','NO_APPLIED_EFFECT'),(bool(a['assertion']) and json.loads(a['assertion'])=={'axis':'moisture','value':'wet'},'NOT_WETTING_EFFECT'),(not patient or patient['form']!=x['form'],'SAME_WRITTEN_FORM'),(wet=='wet','CURRENT_NOT_WET')]
    origins=[z['location'] for z in earlier_same if (z['kind']=='ACTION' and z['status']=='ASSUMED_EFFECT_APPLIED' and z['assertion'] and json.loads(z['assertion']).get('axis')=='moisture') or (z['status']=='INITIAL_CONSTRAINT' and z['assertion'].startswith('PHYSICAL:moisture='))]
    assert r['current_moisture_origin']==(origins[-1] if origins else '')
    reasons=';'.join(reason for ok,reason in checks if not ok);assert r['reasons']==reasons and r['eligible']==str(not reasons) and r['current_moisture']==wet
    for field in ['object','patient','action_status','action_debts']:assert r[field]==a[{'action_status':'status','action_debts':'debts'}.get(field,field)]
    if not reasons:objects[a['object']].append(a['location']);eligible_count+=1
   tr=targetix[tk];assert int(tr['earlier_action_pairs'])==n and int(tr['eligible_actions'])==eligible_count and int(tr['origin_objects'])==len(objects) and tr['first_target']==str(first)
   for oid,actions in objects.items():
    expected_groups[(*tk,oid)]=actions
    for z in trace[ti+1:]:
     if z['kind'] in ['ACTION','QUALITY'] and z['object'] in [oid,target['object']]:expected_later.append((*tk,oid,z['kind'],z['location'],z['object']))
assert seenpairs==set(pairix) and len(pairix)==len(pp)==996
assert seentargets==set(targetix) and len(targetix)==len(tt)==192
assert set(expected_groups)=={(r['shol'],r['paragraph'],r['grammar'],r['chol'],r['timing'],r['target'],r['source_object']) for r in gg} and len(gg)==14
for r in gg:
 key=(r['shol'],r['paragraph'],r['grammar'],r['chol'],r['timing'],r['target'],r['source_object']);assert r['witness_actions'].split(';')==expected_groups[key]
 assert r['later_target_requirements']=='0' and r['later_source_requirements']=='0' and r['alias_simulation']=='NOT_RUN_NO_TARGET_FUTURE_CAPACITY'
later=rows(E/'ALL_LATER_REQUIREMENTS.tsv');assert not expected_later and not later
result=dict(status='PASS',frozen_files=len(S['inputs']),target_cases=192,exhaustive_action_pairs=996,eligible_action_pairs=sum(r['eligible']=='True' for r in pp),origin_groups=14,later_requirements=0,aliases_selected=0,limits='Independent new eligibility/capacity audit; source lexicon, action roles and state history remain hypotheses')
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
