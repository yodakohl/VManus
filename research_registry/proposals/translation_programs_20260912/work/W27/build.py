"""Enumerate live wet origins without fitting or renaming any object."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
features=read(W/'W03/SPEC.json')['features'];assert set(S['target_forms'])=={f['form'] for f in features if f['kind']=='PROCESSED_NOMINAL' and f['axis']=='moisture' and f['value']=='wet'}
flat=rows(W/'W26/Q_SOURCE_FLAT.tsv');bypara=collections.defaultdict(list)
for r in flat:r['offset']=int(r['offset']);bypara[r['paragraph']].append(r)
allpairs=[];targets=[];groups=[];futures=[]
for sm in S['models']:
 worlds=collections.defaultdict(list)
 for r in rows(W/('W26/'+sm+'_EVENTS.tsv')):worlds[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
 for (p,g,chol,timing),trace in worlds.items():
  ff=bypara[p];ix={r['id']:r for r in ff};acts=[r for r in trace if r['kind']=='ACTION'];first={}
  for x in ff:
   if x['form'] in S['target_forms']:first.setdefault(x['form'],x['id'])
  for x in [r for r in ff if r['form'] in S['target_forms']]:
   meta=dict(shol=sm,paragraph=p,grammar=g,chol=chol,timing=timing,target=x['id'],target_form=x['form']);new=first[x['form']]==x['id'];event=next(r for r in trace if r['kind']=='MATERIAL' and r['location']==x['id']);ti=trace.index(event);states={};moisture_origin={}
   for r in trace[:ti]:
    if not r['object']:continue
    states[r['object']]=json.loads(r['after'])
    if r['kind']=='ACTION' and r['status']=='ASSUMED_EFFECT_APPLIED' and r['assertion']:
     effect=json.loads(r['assertion'])
     if effect['axis']=='moisture':moisture_origin[r['object']]=r['location']
    elif r['status']=='INITIAL_CONSTRAINT' and r['assertion'].startswith('PHYSICAL:moisture='):moisture_origin[r['object']]=r['location']
   candidates=collections.defaultdict(list);earlier=[r for r in acts if ix[r['location']]['offset']<x['offset']]
   for a in earlier:
    patient=ix.get(a['patient']);effect=json.loads(a['assertion']) if a['assertion'] else None;current=states.get(a['object'],{}).get('PHYSICAL:moisture','');reasons=[]
    if not new:reasons.append('REPEAT_NOT_NEW_NAME')
    if not patient:reasons.append('MISSING_PATIENT')
    elif patient['offset']>=x['offset']:reasons.append('PATIENT_NOT_WRITTEN_BEFORE_TARGET')
    if trace.index(a)>=ti:reasons.append('ACTION_NOT_EXECUTED_BEFORE_TARGET')
    if a['status']!='ASSUMED_EFFECT_APPLIED':reasons.append('NO_APPLIED_EFFECT')
    if effect!={'axis':'moisture','value':'wet'}:reasons.append('NOT_WETTING_EFFECT')
    if patient and patient['form']==x['form']:reasons.append('SAME_WRITTEN_FORM')
    if current!='wet':reasons.append('CURRENT_NOT_WET')
    r=dict(meta,operation=a['location'],operation_form=a['form'],patient=a['patient'],patient_form=patient['form'] if patient else '',object=a['object'],effect=a['assertion'],action_status=a['status'],action_debts=a['debts'],current_moisture=current,current_moisture_origin=moisture_origin.get(a['object'],''),first_target=new,eligible=not reasons,reasons=';'.join(reasons));allpairs.append(r)
    if not reasons:candidates[a['object']].append(r)
   targets.append(dict(meta,first_target=new,earlier_action_pairs=len(earlier),eligible_actions=sum(len(v) for v in candidates.values()),origin_objects=len(candidates),status='REPEAT_NOT_NEW_NAME' if not new else 'POSSIBLE_ORIGINS' if candidates else 'NO_ELIGIBLE_ORIGIN'))
   for oid,cc in candidates.items():
    after=[r for r in trace[ti+1:] if r['kind'] in ['ACTION','QUALITY'] and r['object'] in [oid,event['object']]];target_after=[r for r in after if r['object']==event['object']]
    groups.append(dict(meta,source_object=oid,source_form=ix[oid]['form'],witness_actions=';'.join(r['operation'] for r in cc),current_moisture_origin=moisture_origin.get(oid,''),state_before_target=json.dumps(states[oid],sort_keys=True,separators=(',',':')),target_object=event['object'],later_target_requirements=len(target_after),later_source_requirements=len(after)-len(target_after),alias_simulation='NOT_RUN_NO_TARGET_FUTURE_CAPACITY' if not target_after else 'REQUIRES_SEPARATE_DECISION'))
    for r in after:futures.append(dict(meta,source_object=oid,location=r['location'],kind=r['kind'],form=r['form'],object=r['object'],status=r['status'],role='TARGET' if r['object']==event['object'] else 'SOURCE'))
for n,rr in [('ALL_ACTION_PAIRS',allpairs),('TARGETS',targets),('ORIGIN_GROUPS',groups)]:table(n+'.tsv',rr)
table('ALL_LATER_REQUIREMENTS.tsv',futures,['shol','paragraph','grammar','chol','timing','target','target_form','source_object','location','kind','form','object','status','role'])
result=dict(target_positions=len({r['target'] for r in targets}),target_cases=len(targets),first_name_positions=len({r['target'] for r in targets if r['first_target']}),action_pairs=len(allpairs),eligible_pairs=sum(r['eligible'] for r in allpairs),origin_groups=len(groups),origins_by_shol={s:sum(r['shol']==s for r in groups) for s in S['models']},live_wet_exclusions=[{k:r[k] for k in ['shol','grammar','chol','timing','target','operation','object','current_moisture','current_moisture_origin']} for r in allpairs if r['reasons']=='CURRENT_NOT_WET' and r['effect']=='{"axis":"moisture","value":"wet"}'],later_target_capacity=sum(r['later_target_requirements']>0 for r in groups),later_rows=len(futures),aliases_selected=0,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
