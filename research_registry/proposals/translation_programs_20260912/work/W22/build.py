"""Project frozen sho identities through existing physical events, no new decoder."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def enc(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
old=rows(W/'W18/EVENTS.tsv');worlds=collections.defaultdict(list)
for r in old:worlds[(r['model'],r['world'])].append(r)
assert len(worlds)==117
opposed={'moisture':{frozenset(('wet','dry'))},'thermal':{frozenset(('cold','warm')),frozenset(('cold','hot'))}}
allrows=[];diff=[];summ=[];reps=[];witnesses=[];hotwarm=[]
for (m,world),original in worlds.items():
 for verb in S['candidates']:
  state={};origins={};trace=[]
  for serial,old in enumerate(original):
   r={k:v for k,v in old.items() if k!='row_status'};r['verb']=verb
   oid=r['object'];sid=r['second_object'];before=state.get(oid,{}).copy();r['state_origin']='';r['alias_collision']=str(bool(oid and sid==oid))
   if verb=='G' and r['form']=='qokeor' and r['kind']=='ACTION':
    r['debts']=';'.join(d for d in r['debts'].split(';') if d and d!='EXTRACT_PATIENT_NOT_BOUND')
   if r['kind']=='MATERIAL':
    if oid:state.setdefault(oid,{});origins.setdefault(oid,{})
   elif r['kind']=='ACTION':
    effect=json.loads(r['assertion']) if r['assertion'] else None
    invalid=not oid or 'EXTRACT_PATIENT_NOT_BOUND' in r['debts'] or 'MISSING_RELATION_PARTNER' in r['debts'] or bool(r['second'] and not sid)
    r['status']='ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED'
    if not invalid and effect:
     key='PHYSICAL:'+effect['axis'];assert oid in state
     if key=='PHYSICAL:thermal' and state[oid].get(key)=='hot' and effect['value']=='warm':hotwarm.append(dict(verb=verb,model=m,world=world,operation=r['location'],form=r['form'],object=oid,prior_origin=origins[oid].get(key,''),classification='HOT_TO_WARM_ASSIGNMENT'))
     state[oid][key]=effect['value'];origins[oid][key]=r['location']
   else:
    key,value=r['assertion'].split('=',1);prior=state.get(oid,{}).get(key);r['state_origin']=origins.get(oid,{}).get(key,'')
    r['status']='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if prior is None else 'MATCH' if prior==value else 'CONFLICT' if frozenset((prior,value)) in opposed[key.split(':')[1]] else 'DIFFERENT_NOT_OPPOSED'
    if oid and prior is None:state[oid][key]=value;origins[oid][key]=r['location']
   r['before']=enc(before);r['after']=enc(state.get(oid,{}));trace.append(r);allrows.append(r)
   checked=['object','second_object','before','after','status','state_origin','debts','alias_collision']
   if verb=='X':assert all(r[k]==old[k] for k in checked),(world,serial,[(k,r[k],old[k]) for k in checked if r[k]!=old[k]])
   else:
    changed=[k for k in checked if r[k]!=old[k]]
    if changed:diff.append(dict(verb=verb,model=m,world=world,source_event=old['source_event'],location=r['location'],kind=r['kind'],form=r['form'],changed_fields=','.join(changed),E_object=old['object'],new_object=oid,E_before=old['before'],new_before=r['before'],E_after=old['after'],new_after=r['after'],E_status=old['status'],new_status=r['status'],E_origin=old['state_origin'],new_origin=r['state_origin']))
   if r['kind']=='ACTION' and r['form'] in ('ykeey','yteey'):
    effect=json.loads(r['assertion']);prior=[z for z in trace[:-1] if oid and z['object']==oid and z['kind']=='ACTION' and z['status']=='ASSUMED_EFFECT_APPLIED'];exact=[z for z in prior if json.loads(z['assertion'])==effect];hot=[z for z in prior if json.loads(z['assertion'])=={'axis':'thermal','value':'hot'}]
    reps.append(dict(verb=verb,model=m,world=world,target=r['location'],form=r['form'],object=oid,status=r['status'],exact_effect_witnesses=len(exact),prior_hot_actions=len(hot),before=r['before']))
    for typ,ww in [('REP_EXACT',exact),('PRIOR_HOT',hot)]:
     for z in ww:witnesses.append(dict(verb=verb,model=m,world=world,target=r['location'],witness=z['location'],form=z['form'],object=oid,kind=typ))
  summ.append(dict(verb=verb,model=m,world=world,events=len(trace),conflicts=sum(r['status']=='CONFLICT' for r in trace),unequal=sum(r['status']=='DIFFERENT_NOT_OPPOSED' for r in trace),incomplete_actions=sum(r['kind']=='ACTION' and r['status']=='ARGUMENT_INCOMPLETE' for r in trace),missing_material_references=sum(r['status']=='MISSING_REFERENT' for r in trace),exact_repeat_targets=sum(r['verb']==verb and r['world']==world and r['model']==m and r['exact_effect_witnesses']>0 for r in reps)))
table('EVENTS.tsv',allrows);table('DIFFERENCES.tsv',diff);table('WORLD_SUMMARY.tsv',summ);table('REPEAT_TARGETS.tsv',reps);table('REPEAT_WITNESSES.tsv',witnesses,['verb','model','world','target','witness','form','object','kind']);table('HOT_TO_WARM.tsv',hotwarm)
result={'worlds':len(summ),'events':len(allrows),'difference_rows':len(diff),'X_parity':True,'candidates':{v:{m:{'conflicts':sum(r['conflicts'] for r in summ if r['model']==m and r['verb']==v),'unequal':sum(r['unequal'] for r in summ if r['model']==m and r['verb']==v),'exact_repeat_targets':sum(r['model']==m and r['verb']==v and r['exact_effect_witnesses']>0 for r in reps),'hot_to_warm_assignments':sum(r['model']==m and r['verb']==v for r in hotwarm)} for m in S['models']} for v in S['candidates']},'meanings_confirmed':0,'held_access':False,'independent_confirmation_capacity':0,'scope':S['scope']}
arguments=[]
for r in rows(W/'W17/ACTION_CONSEQUENCES.tsv'):
 if r['form']=='qokeor':
  for v in S['candidates']:
   arguments.append(dict(r,verb=v,gloss='erhitze den Auszug' if v=='X' else 'erhitze',extract_requirement='required' if v=='X' else 'not_required',interpretation='Authored assumption; fixed patient and object'))
table('ARGUMENTS.tsv',arguments)
alignment=[]
for r in rows(W/'W17/ALIGNMENT.tsv'):
 alignment.append(dict(r,X=r['joint'],G='erhitze' if r['raw']=='qokeor' else r['joint']))
table('ALIGNMENT.tsv',alignment)
reader=['# W22 vollständige hypothetische Lesung','G: qokeor≈erhitze; X bleibt die Alternative erhitze den Auszug. Alle übrigen Annahmen und E/P/R-Verweise unverändert. Keine bestätigte Übersetzung.']
for p in dict.fromkeys(r['paragraph'] for r in alignment):
 reader.append('\n## '+p)
 for loc in dict.fromkeys(r['locus'] for r in alignment if r['paragraph']==p):
  rr=[r for r in alignment if r['paragraph']==p and r['locus']==loc]
  reader.append('\n'+loc+'\n\n'+' · '.join(r['raw']+' ['+r['G']+('; '+r['reference_alternatives'] if r.get('reference_alternatives') else '')+']' for r in rr))
(E/'READING.md').write_text('\n'.join(reader)+'\n')
result.update(arguments=len(arguments),raw_groups=len(alignment),changed_gloss_positions=sum(r['X']!=r['G'] for r in alignment))
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
