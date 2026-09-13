"""Independent event-state replay, reference projection and exhaustive REP witnesses."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
s=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
for r in s['inputs']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
base=[r for r in rows(W/'W14/EVENTS.tsv') if r['timing']=='I' and r['candidate']=='H'];orig={(r['world'],r['source_event']):r for r in base};assert len(orig)==len(base)==1176
obj={(r['paragraph'],r['model'],r['mention']):r for r in rows(W/'W17/OBJECTS.tsv') if r['edition']=='ZL3b'}
typeclaims={(r['paragraph'],r['model'],r['grammar'],r['operation']):r for r in rows(W/'W17/ACTION_CONSEQUENCES.tsv') if r['edition']=='ZL3b'}
raw={r['locus']+':'+r['index']:r['raw'] for r in rows(W/'W17/ALIGNMENT.tsv')}
rr=rows(E/'EVENTS.tsv');assert len(rr)==3528;worlds=collections.defaultdict(list)
for r in rr:worlds[(r['model'],r['world'])].append(r)
assert len(worlds)==117
expectedwitnesses=set();expectedhot=set();repeatresults={};differences=set()
for (model,world),trace in worlds.items():
 _,ed,g,p=world.split('|',3);state={};origin={};seen=[]
 assert [r['source_event'] for r in trace]==[r['source_event'] for r in base if r['world']==world]
 for r in trace:
  b=orig[(world,r['source_event'])]
  for k in ['timing','candidate','event','order','execution_index','kind','location','form','patient','second','assertion']:assert r[k]==b[k]
  mention=r['location'] if r['kind'] in ('MATERIAL','BARE_NOMINAL','PROCESSED_NOMINAL') else r['patient']
  oid=obj[(p,model,mention)]['object'] if raw.get(mention)=='sho' else b['object'];sid=obj[(p,model,r['second'])]['object'] if raw.get(r['second'])=='sho' else b['second_object'];assert r['object']==oid and r['second_object']==sid
  assert json.loads(r['before'])==state.get(oid,{})
  debt=b['debts']
  if model!='E' and r['kind']=='ACTION' and r['form']=='qokeor':
   dd=[x for x in debt.split(';') if x and x!='EXTRACT_PATIENT_NOT_BOUND']
   if typeclaims[(p,model,g,r['location'])]['type_status']=='EXTRACT_NOT_BOUND':dd.append('EXTRACT_PATIENT_NOT_BOUND')
   debt=';'.join(dd)
  assert r['debts']==debt
  expectedorigin=''
  if r['kind']=='MATERIAL':
   if oid:state.setdefault(oid,{});origin.setdefault(oid,{})
   status=('ASSUMED_REFERENCE' if oid else 'MISSING_REFERENT') if model!='E' and r['form']=='sho' else b['status']
  elif r['kind']=='ACTION':
   effect=json.loads(r['assertion']) if r['assertion'] else None
   valid=bool(oid) and 'EXTRACT_PATIENT_NOT_BOUND' not in debt and 'MISSING_RELATION_PARTNER' not in debt and not (r['second'] and not sid)
   status='ARGUMENT_INCOMPLETE' if not valid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED'
   if valid and effect:
    key='PHYSICAL:'+effect['axis']
    if key=='PHYSICAL:thermal' and state[oid].get(key)=='hot' and effect['value']=='warm':expectedhot.add((model,world,r['location'],oid,origin[oid].get(key,'')))
    state[oid][key]=effect['value'];origin[oid][key]=r['location']
   if r['form'] in ('ykeey','yteey'):
    matches=[];hots=[]
    for prev in seen:
     if not oid or prev['object']!=oid or prev['kind']!='ACTION' or prev['status']!='ASSUMED_EFFECT_APPLIED':continue
     pe=json.loads(prev['assertion'])
     if pe==effect:matches.append(prev);expectedwitnesses.add((model,world,r['location'],prev['location'],oid,'REP_EXACT'))
     if pe=={'axis':'thermal','value':'hot'}:hots.append(prev);expectedwitnesses.add((model,world,r['location'],prev['location'],oid,'PRIOR_HOT'))
    repeatresults[(model,world,r['location'])]=(len(matches),len(hots))
  else:
   key,val=r['assertion'].split('=',1);prev=state.get(oid,{}).get(key);expectedorigin=origin.get(oid,{}).get(key,'')
   bad=(key.endswith(':thermal') and {prev,val} in ({'cold','warm'},{'cold','hot'})) or (key.endswith(':moisture') and {prev,val}=={'wet','dry'})
   status='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if prev is None else 'MATCH' if prev==val else 'CONFLICT' if bad else 'DIFFERENT_NOT_OPPOSED'
   if oid and prev is None:state[oid][key]=val;origin[oid][key]=r['location']
  assert r['status']==status and r['state_origin']==expectedorigin and json.loads(r['after'])==state.get(oid,{})
  changed=any(r[k]!=b[k] for k in ['object','second_object','before','after','status','state_origin','debts','alias_collision'])
  if model=='E':assert not changed
  elif changed:differences.add((model,world,r['source_event']))
  seen.append(r)
ww=rows(E/'REPEAT_WITNESSES.tsv');assert len(ww)==len(expectedwitnesses) and {(r['model'],r['world'],r['target'],r['witness'],r['object'],r['kind']) for r in ww}==expectedwitnesses
rt=rows(E/'REPEAT_TARGETS.tsv');assert len(rt)==len(repeatresults)==45
for r in rt:assert (int(r['exact_effect_witnesses']),int(r['prior_hot_actions']))==repeatresults[(r['model'],r['world'],r['target'])]
hw=rows(E/'HOT_TO_WARM.tsv');assert len(hw)==len(expectedhot) and {(r['model'],r['world'],r['operation'],r['object'],r['prior_origin']) for r in hw}==expectedhot
diff=rows(E/'DIFFERENCES.tsv');assert len(diff)==len(differences)==60 and {(r['model'],r['world'],r['source_event']) for r in diff}==differences
assert {(r['model'],r['target']) for r in rt if int(r['exact_effect_witnesses'])}>={('R','f102v2.38:8')}
assert sum(int(r['exact_effect_witnesses'])>0 for r in rt)==3
v={'status':'PASS','legacy_files_verified':len(s['inputs']),'complete_worlds':117,'events_replayed':3528,'baseline_events_identical':1176,'repeat_targets_checked':45,'new_positive_repeat_loci':['f102v2.38:8'],'positive_model':'R','independent_semantic_confirmation':False}
(E/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
