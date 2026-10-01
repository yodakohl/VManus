#!/usr/bin/env python3
"""Finite state projection of frozen entry traces; no global decoder/parser."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def dump(name,data):(E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def load():
 s=json.loads((E/'src/SPEC.json').read_text());data={}
 for k,b in s['inputs'].items():
  raw=(ROOT/b['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256'];data[k]=json.loads(raw)
 return s,data
def early(a,rows,policy):
 st={'topic':None,'current':None,'entities':{},'owner':None};trace=[]
 def context():
  x=st['topic' if policy=='TOPIC' else 'current'];assert x in st['entities'];return x
 for r in rows:
  seg=r['segmentation'];root=seg[-1];meaning,sort=(a['roots']|a['whole_residuals'])[root];operand=None;effect=None
  if seg[0]=='p':
   assert sort=='MaterialSchema' and seg in [['p','d','sheody'],['p','ol']]
   obj='M1' if root=='sheody' else 'M2';st['entities'][obj]={'sort':'Material','parent':None};st['topic']=st['current']=obj;operand=obj;effect='Introduce described Material by R3'
  elif seg[0]=='sh':
   assert seg==['sh','dol'] and sort=='ContainerSchema';operand=context();st['owner']='C1';effect='Introduce C1 Contains(C1,'+operand+') by R4'
  elif seg[0]=='q':
   assert seg==['q','o','kaiin'] and sort=='MaterialProperty';operand=context();st['entities']['P5']={'sort':'Material','parent':operand};st['current']='P5';effect='Introduce proper part P5 by R5 from explicit property/context expression R7'
  elif sort=='Event(Material)->same Material':
   assert root=='shey';operand=context();effect='Macerate '+operand+'; preserve identity D1/D2'
  else:
   assert sort in ['MaterialProperty','MaterialSchema'];operand=context()
   if len(seg)==2 and seg[0]=='ol':assert a['roots']['ol'][1]=='MaterialSchema' and sort=='MaterialProperty'
   elif len(seg)==2:assert seg[0]=='o' and sort=='MaterialProperty'
   effect='Assert paid schema/property of '+operand+' by R2/R7/R9/D3'
  trace.append(dict(context=r['context'],policy=policy,position=r['position'],raw_id=r['raw_id'],surface=r['raw_surface'],segmentation=seg,root_sort=sort,operand=operand,selected_context=context(),effect=effect,state=json.loads(json.dumps(st))))
 return trace

def main():
 s,d=load();a,t=d['author'],d['target'];assert a['target_sha256']==s['inputs']['target']['sha256']
 assert len(a['positions'])==129 and len(a['roots'])==20 and len(a['whole_residuals'])==1
 raw=[(c['context'],r) for c in t['contexts'] for r in c['groups']]
 for x,(ctx,r) in zip(a['positions'],raw):
  assert (x['context'],x['raw_id'],x['raw_surface'],x['position'])==(ctx,r['source_group_id'],r['ivtff_group_raw'],r['position'])
  assert ''.join(x['segmentation'])==x['raw_surface'] and x['left_separator']==r['left_separator'] and x['right_separator']==r['right_separator']
 traces=[];cases=[]
 for ctx,n in s['early_prefix_lengths'].items():
  rows=[x for x in a['positions'] if x['context']==ctx]
  for policy in s['policies']:
   tr=early(a,rows[:n],policy);traces+=tr
   for x,actual in zip(rows[:n],tr):assert x['computed_or_UNBOUND_patient'][policy]==actual['selected_context']
   cases.append(dict(context=ctx,policy=policy,first_shey_position=n,predicted_patient=rows[n-1]['computed_or_UNBOUND_patient'][policy],observed_projected_patient=tr[-1]['operand'],contradiction=False,meaning_selected=False,whole_complete=False,independent_confirmation=0))
  assert all(all(v=='UNBOUND' for v in x['computed_or_UNBOUND_patient'].values()) for x in rows[n:])
 # Conditional late trace of the stated sequential QOL48/QOL49/KAIN50 reading.
 late=[]
 for policy in s['policies']:
  topic=current='X';parts=[]
  for pos,obj in [(48,'A'),(49,'B')]:
   parent=topic if policy=='TOPIC' else current;parts.append({'position':pos,'introduced':obj,'parent':parent});current=obj
  actual=topic if policy=='TOPIC' else current
  late.append(dict(policy=policy,hypothetical_input='X',parts=parts,bare_kain_patient_by_D3=actual,author_stated_kain_patient='B',sequential_trace_mismatch=actual!='B',actual_manuscript_state_bound=False))
 profiles={x['form'] for x in d['priors']['profiles'] if x['status'].startswith('SUPPLIED')}|{x['form'] for x in d['additional_priors']['profiles']}
 assert profiles=={x['raw_surface'] for x in a['positions']}
 counts=dict(Counter(x['status'] for x in a['positions']))
 result=dict(experiment='GDT1122',status='PARTIAL_SHARED_ENTRY__SCOPE_UNSELECTED__LATE_TRACE_DEBT',groups=129,forms=len(profiles),author_counts=a['counts'],status_counts=counts,early_worked_groups=11,remaining_unbound_groups=118,whole_complete_contexts=0,candidates=cases,late_conditional=late,first_unmet=a['first_unmet'],confirmed_words=0,independent_confirmation_capacity=0,significance_claim=False,claim_ceiling='Finite declared early entry projection and conditioned late sequential trace, not a full grammar or independent meaning test')
 dump('RESULT.json',result);dump('ENTRY_TRACE.json',traces)
 with (E/'artifacts/CANDIDATES.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(cases[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(cases)
 with (E/'artifacts/ALL_POSITIONS.tsv').open('w',newline='') as f:
  keys=['context','position','raw_id','raw_surface','segmentation','contribution','status','computed_or_UNBOUND_patient'];w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader()
  for x in a['positions']:w.writerow({k:json.dumps(x[k],ensure_ascii=False) if isinstance(x[k],(list,dict)) else x[k] for k in keys})
 print(json.dumps({k:result[k] for k in ['status','groups','forms','status_counts','early_worked_groups','remaining_unbound_groups','whole_complete_contexts']}))
if __name__=='__main__':main()
