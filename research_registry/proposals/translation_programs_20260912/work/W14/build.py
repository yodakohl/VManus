"""Replay fixed W10 E worlds with one preregistered input-attribute timing rule."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def js(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def encode(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def table(n,rr,cols=None):
 cols=cols or list(rr[0])
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=[k for k in cols if k!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=js(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];lex={r['form']:r['role'] for r in rows(W/'W02/LEXICON.tsv')};args=rows(W/'W05/ARGUMENTS.tsv');qq=rows(W/'W05/QUALITY_ASSERTIONS.tsv');flat={};census=[];eligible={};transcriptions=[]
for t in source['targets']:
 p=t['hosts']['ZL3b'][0];rr=[]
 for line in p['lines']:
  assert not line['locus'].startswith('f84')
  for i,w in enumerate(line['words'],1):rr.append({'id':line['locus']+':'+str(i),'locus':line['locus'],'word':w,'offset':len(rr),'role':lex.get(w,'OPEN')})
 flat[p['id']]=rr;byid={x['id']:x for x in rr}
 for q in qq:
  if q['paragraph']!=p['id'] or q['kind']!='STANDALONE':continue
  x=byid[q['mention']];m=byid.get(q['patient']);earlier=[]
  if m:earlier=[a for a in args if a['edition']=='ZL3b' and a['variant']==q['variant'] and a['paragraph']==p['id'] and a['patient']==m['id'] and byid[a['operation']]['locus']==m['locus'] and byid[a['operation']]['offset']<m['offset']]
  reason='MISSING_PATIENT' if not m else 'NOT_DIRECT_PRECEDING_MATERIAL' if m['locus']!=x['locus'] or m['offset']!=x['offset']-1 or m['role'] not in ('MATERIAL','MATERIAL_DOSE') else 'NO_PRECEDING_ACTION_ON_POSTPOSED_MATERIAL' if not earlier else 'ELIGIBLE'
  census.append(dict(grammar=q['variant'],paragraph=p['id'],mention=x['id'],form=x['word'],patient=q['patient'],patient_form=q['patient_form'],axis=q['axis'],value=q['value'],status=reason,operations=';'.join(a['operation'] for a in earlier),new_input_order=m['offset'] if reason=='ELIGIBLE' else '',raw_line=' '.join(y['word'] for y in rr if y['locus']==x['locus'])))
  if reason=='ELIGIBLE':eligible[(q['variant'],p['id'],x['id'])]=m['offset']
for loc in dict.fromkeys(r['mention'].rsplit(':',1)[0] for r in census if r['status']=='ELIGIBLE'):
 for ed,ll in alt.items():
  line=next(l for l in ll if l['metadata']['locus']==loc)
  transcriptions.append(dict(edition=ed,locus=loc,raw_line=' '.join(g['ivtff_group_raw'] for g in line['groups']),meaning_transfer='NOT_PERFORMED'))
table('ELIGIBILITY.tsv',census);table('ALTERNATE_TARGET_LINES.tsv',transcriptions,['edition','locus','raw_line','meaning_transfer'])
worlds=collections.defaultdict(list)
for r in rows(W/'W10/EVENTS.tsv'):
 if r['world'].startswith('E|ZL3b|'):worlds[(r['candidate'],r['world'])].append(r)
assert len(worlds)==78
opposed={'moisture':{frozenset(('wet','dry'))},'thermal':{frozenset(('cold','warm')),frozenset(('cold','hot'))}}
def replay(source_rows,shifts):
 state={};origin={};schedule=[]
 for i,r in enumerate(source_rows):
  tick=int(r['order']);priority=1 if r['kind']=='ACTION' else 2 if r['kind']=='QUALITY' else 0
  if r['kind']=='QUALITY' and r['location'] in shifts:tick=shifts[r['location']];priority=.5
  schedule.append((tick,priority,i,r))
 schedule.sort(key=lambda x:x[:3]);out=[]
 for tick,priority,i,old in schedule:
  r=old.copy();r['order']=str(tick);oid=r['object'];before=state.get(oid,{}).copy();r['state_origin']=''
  if r['kind']=='MATERIAL':
   state.setdefault(oid,{});origin.setdefault(oid,{})
  elif r['kind']=='ACTION':
   effect=json.loads(r['assertion']) if r['assertion'] else None
   invalid=not oid or 'EXTRACT_PATIENT_NOT_BOUND' in r['debts'] or 'MISSING_RELATION_PARTNER' in r['debts']
   r['status']='ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED'
   if not invalid and effect:
    key='PHYSICAL:'+effect['axis'];state[oid][key]=effect['value'];origin[oid][key]=r['location']
  else:
   key,value=r['assertion'].split('=',1);prior=state.get(oid,{}).get(key)
   r['status']='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if prior is None else 'MATCH' if prior==value else 'CONFLICT' if frozenset((prior,value)) in opposed[key.split(':')[1]] else 'DIFFERENT_NOT_OPPOSED'
   r['state_origin']=origin.get(oid,{}).get(key,'')
   if oid and prior is None:state[oid][key]=value;origin[oid][key]=r['location']
  r['before']=encode(before);r['after']=encode(state.get(oid,{}));out.append((i,r))
 return out
allrows=[];differences=[];target_results=[];summary=[];endstates=[]
for (chol,world),old in worlds.items():
 _,ed,g,p=world.split('|',3);shifts={loc:order for (gram,para,loc),order in eligible.items() if gram==g and para==p}
 traces={m:replay(old,shifts if m=='I' else {}) for m in S['timing']}
 for i,r in traces['O']:
  before=old[i]
  for k in ('before','after'):assert json.loads(r[k])==json.loads(before[k]),(world,i,k)
  for k in ('status','order','state_origin'):assert r[k]==before[k],(world,i,k,r[k],before[k])
 base=dict(traces['O']);modified=dict(traces['I'])
 for m,trace in traces.items():
  summary.append(dict(chol=chol,world=world,timing=m,eligible_count=len(shifts),conflicts=sum(r['status']=='CONFLICT' for _,r in trace),unequal=sum(r['status']=='DIFFERENT_NOT_OPPOSED' for _,r in trace)))
  for serial,(i,r) in enumerate(trace):allrows.append(dict(timing=m,source_event=i,execution_index=serial,**r))
  last={}
  for _,r in trace:
   if r['object']:last[r['object']]=r['after']
  for oid,st in last.items():endstates.append(dict(chol=chol,world=world,timing=m,object=oid,state=st))
 for i,a in base.items():
  b=modified[i]
  if a['kind']=='QUALITY' and a['location'] in shifts:target_results.append(dict(chol=chol,world=world,grammar=g,mention=a['location'],patient=a['patient'],O_status=a['status'],I_status=b['status'],O_before=a['before'],I_before=b['before'],O_after=a['after'],I_after=b['after'],O_order=a['order'],I_order=b['order']))
  if any(a[k]!=b[k] for k in ('before','after','status','order','state_origin')):differences.append(dict(chol=chol,world=world,source_event=i,kind=a['kind'],location=a['location'],patient=a['patient'],O_before=a['before'],I_before=b['before'],O_after=a['after'],I_after=b['after'],O_status=a['status'],I_status=b['status'],O_origin=a['state_origin'],I_origin=b['state_origin']))
table('EVENTS.tsv',allrows);table('TARGET_RESULTS.tsv',target_results,['chol','world','grammar','mention','patient','O_status','I_status','O_before','I_before','O_after','I_after','O_order','I_order']);table('DIFFERENCES.tsv',differences);table('WORLD_SUMMARY.tsv',summary);table('FINAL_STATES.tsv',endstates)
# Preserve every primary word with a local timing annotation only at registered eligible mentions.
a=rows(W/'W10/ALIGNMENT.tsv');full=[];reader=['# W14 — vollständige Arbeitslesung mit Zeitrivalen','Wortwerte unverändert hypothetisch; H angezeigt, D bleibt offen. I markiert nur feste lokale Eingangsattribute.']
for r in a:
 grammars=[g for g,p,loc in eligible if p==r['paragraph'] and loc==r['locus']+':'+r['index']]
 full.append(dict(r,input_attribute_grammars=','.join(grammars),timing_note='I: Qualität des Eingangs vor den gebundenen Verben; O: bisherige Schriftzeit' if grammars else 'UNCHANGED'))
for p in dict.fromkeys(r['paragraph'] for r in full):
 reader+=['','## '+p]
 for loc in dict.fromkeys(r['locus'] for r in full if r['paragraph']==p):
  rr=[r for r in full if r['locus']==loc];reader+=['',loc+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['H']+(' {I-Eingangsattribut unter '+r['input_attribute_grammars']+'}' if r['input_attribute_grammars'] else '') for r in rr)]
table('ALIGNMENT.tsv',full);(E/'READING.md').write_text('\n'.join(reader)+'\n')
result={'eligible_rows':len(eligible),'eligible_mentions':sorted({loc for g,p,loc in eligible}),'quality_census_rows':len(census),'base_worlds':len(worlds),'timing_worlds':len(summary),'event_rows':len(allrows),'difference_rows':len(differences),'primary_groups':len(full),'baseline_parity':True,'meanings_confirmed':0,'independent_confirmation_capacity':0,'held_access':False}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
