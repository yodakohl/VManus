"""Minimal explicit value exclusions; no opposite-value inference."""
import json

def replay_negative(source_rows,shifts,negative):
 def encode(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
 schedule=[]
 for i,r in enumerate(source_rows):
  tick=int(r['order']);priority=1 if r['kind']=='ACTION' else 2 if r['kind']=='QUALITY' else 0
  if r['kind']=='QUALITY' and r['location'] in shifts:tick=shifts[r['location']];priority=.5
  schedule.append((tick,priority,i,r))
 state={};origin={};out=[]
 for tick,priority,i,old in sorted(schedule,key=lambda x:x[:3]):
  r=old.copy();oid=r['object'];before=state.get(oid,{}).copy();r['order']=str(tick);r['state_origin']='';neg=r['location'] in negative and r['kind'] in ['ACTION','QUALITY'];r['polarity']='NEGATIVE' if neg else 'POSITIVE'
  if r['kind']=='MATERIAL':state.setdefault(oid,{})
  elif r['kind']=='ACTION':
   effect=json.loads(r['assertion']) if r['assertion'] else None;invalid=not oid or any(d in r['debts'].split(';') for d in ['EXTRACT_PATIENT_NOT_BOUND','MISSING_RELATION_PARTNER'])
   r['status']=('FORBIDDEN_ACTION_UNBOUND_PATIENT' if invalid else 'FORBIDDEN_ACTION_NOT_EXECUTED') if neg else 'ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED'
   if not neg and not invalid and effect:
    k='PHYSICAL:'+effect['axis'];state[oid][k]=effect['value'];origin[oid,k]=r['location']
    for x in list(state[oid]):
     if x.startswith('NOT:'+k+'='):del state[oid][x];origin.pop((oid,x),None)
  else:
   k,v=r['assertion'].split('=',1);prior=before.get(k);nk='NOT:'+k+'='+v
   if neg:
    r['status']='MISSING_PATIENT' if not oid else 'CONFLICT' if prior==v else 'MATCH' if prior is not None or nk in before else 'NEGATIVE_CONSTRAINT';r['state_origin']=origin.get((oid,k if prior is not None else nk),'')
    if oid and prior!=v:state[oid][nk]=True;origin.setdefault((oid,nk),r['location'])
   else:
    opposed=k.endswith(':moisture') and {prior,v}=={'wet','dry'} or k.endswith(':thermal') and ((prior=='cold' and v in ['hot','warm']) or (v=='cold' and prior in ['hot','warm']))
    r['status']='MISSING_PATIENT' if not oid else 'CONFLICT' if nk in before else 'INITIAL_CONSTRAINT' if prior is None else 'MATCH' if prior==v else 'CONFLICT' if opposed else 'DIFFERENT_NOT_OPPOSED';r['state_origin']=origin.get((oid,nk if nk in before else k),'')
    if oid and prior is None and nk not in before:state[oid][k]=v;origin[oid,k]=r['location']
  r['before']=encode(before);r['after']=encode(state.get(oid,{}));out.append((i,r))
 return out
