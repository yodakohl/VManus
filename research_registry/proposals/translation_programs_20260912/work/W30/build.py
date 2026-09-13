"""Registered scope census; fixed W28 event topology, polarity only."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;B=W/'W28';ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
def js(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
scopes=[];events=[];changes=[];later=[];summary=[];candidates=[];capacity=[]
source=read(B/'SOURCE.json')['paragraphs']
for sm in ['Q','A']:
 flat=rows(B/(sm+'_SOURCE_FLAT.tsv'));old=rows(B/(sm+'_EVENTS.tsv'));acts={r['location'] for r in old if r['kind']=='ACTION' and r['form']!='chey'};quals={r['location'] for r in old if r['kind']=='QUALITY'}
 local=[]
 for p in source:
  ff=[r for r in flat if r['paragraph']==p['id']]
  for i,x in enumerate(ff):
   if x['form']!='chey':continue
   for contract in ['P16_LITERAL','TRANSFER']:
    target=None;barrier='PARAGRAPH_END';gap=[]
    for y in ff[i+1:]:
     if y['form'] in S['scope_barriers']:barrier=y['id'];break
     hit=y['form'] in S['literal_P16_predicates'] if contract=='P16_LITERAL' else y['id'] in acts|quals
     if hit:target=y;break
     gap.append(y)
    local.append(dict(shol=sm,paragraph=p['id'],chey=x['id'],contract=contract,target=target['id'] if target else '',target_form=target['form'] if target else '',target_kind=('ACTION' if target['id'] in acts else 'QUALITY' if target['id'] in quals else 'NOT_CURRENT_PREDICATE') if target else '',stop='TARGET' if target else barrier,interval=';'.join(y['id']+'='+y['form'] for y in gap),open_interval=';'.join(y['id']+'='+y['form'] for y in gap if y['role']=='OPEN')))
 for r in local:r['parity']=sum(x['contract']==r['contract'] and x['paragraph']==r['paragraph'] and x['target']==r['target'] for x in local)%2 if r['target'] else ''
 scopes+=local;tt=[r for r in local if r['contract']=='TRANSFER'];negative={r['target'] for r in tt if r['target'] and r['parity']==1};bound={r['chey']:r for r in tt};state_targets=[r for r in tt if r['target_kind']=='QUALITY']
 capacity.append(dict(shol=sm,chey=len(tt),bound=sum(bool(r['target']) for r in tt),state_targets=len(state_targets),executable=not state_targets))
 # Capacity is assessed for the entire model; all candidate wording is still emitted.
 alignment={r['locus']+':'+r['index']:r for r in rows(B/(sm+'_ALIGNMENT.tsv'))}
 for t in tt:
  for g in ['B','J','M']:
   for model in ['D','H']:
    for timing in ['O','I']:
     rr=[r for r in old if (r['paragraph'],r['grammar'],r['model'],r['timing'])==(t['paragraph'],g,model,timing)]
     c=next(r for r in rr if r['location']==t['chey'] and r['kind']=='ACTION')
     target=next((r for r in rr if r['location']==t['target'] and r['kind'] in ['ACTION','QUALITY']),None)
     gloss=alignment[t['target']][model] if target else '[ungebunden]'
     patient=target['patient'] if target else ''
     candidates.append(dict(shol=sm,paragraph=t['paragraph'],grammar=g,model=model,timing=timing,chey=t['chey'],C_patient=c['patient'],C_object=c['object'],C_status=c['status'],N_target=t['target'],N_kind=t['target_kind'],N_form=t['target_form'],N_patient=patient,N_patient_gloss=alignment[patient][model] if patient else '[ungebunden]',N_wording=('nicht: ' if t['parity']==1 else 'gerade Negationszahl: ')+gloss,N_object=target['object'] if target else '',baseline_target_status=target['status'] if target else '',baseline_before=target['before'] if target else '',debts=target['debts'] if target else '',scope_open=t['open_interval'],physical_result='NOT_REPLAYED_STATE_TARGET_CAPACITY'))
table('SCOPES.tsv',scopes,list(scopes[0]));table('CAPACITY.tsv',capacity,list(capacity[0]));table('CANDIDATES.tsv',candidates,list(candidates[0]))
res=dict(idea='IDEA000227',status='SCOPE_COMPLETE_PHYSICAL_COMPARISON_NOT_EXECUTED',capacity=capacity,scope_rows=len(scopes),candidate_cases=len(candidates),replayed_worlds=0,later_requirements=None,constraint_discriminators=None,new_conflicts=None,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
