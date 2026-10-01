#!/usr/bin/env python3
"""Registered finite AST interpreter for a conditional nominal continuation."""
import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def write(name,data):(E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def label(s):return s.replace(' ','_').replace('-','_')
def spell(x):
 op=x['op']
 if op=='root':return x['value']
 if op in ['qualify','nominal_event']:return spell(x['left'])+spell(x['right'])
 return op+spell(x['arg'])
class State:
 def __init__(self,author,policy,initial,rows):
  self.lex=author['roots']|author['whole_residuals'];self.policy=policy;self.initial=initial;self.rows={r['position']:r for r in rows}
  self.topic=self.current=self.owner=None;self.entities={};self.parents=[];self.events=[];self.assertions=[];self.writes=[];self.trace=[]
 def context(self):
  obj=self.topic if self.policy=='TOPIC' else self.current
  assert obj in self.entities and self.entities[obj]['sort']=='Material','unbound context'
  return obj
 def descriptor(self,x):
  op=x['op']
  if op=='root':
   meaning,sort=self.lex[x['value']];assert sort in ['MaterialSchema','ContainerSchema','MaterialProperty']
   return sort,[label(meaning)]
  if op=='qualify':
   l,lp=self.descriptor(x['left']);r,rp=self.descriptor(x['right']);assert l=='MaterialSchema' and r=='MaterialProperty'
   return 'MaterialSchema',lp+rp
  if op=='o':
   sort,props=self.descriptor(x['arg']);assert sort=='MaterialProperty';return 'NominalExpr',['dispersed']+props
  if op=='d':
   sort,props=self.descriptor(x['arg']);assert sort in ['MaterialSchema','MaterialProperty'];return sort,['dense']+props
  raise AssertionError('unsupported descriptor '+op)
 def resolve(self,x,pos):
  sort,props=self.descriptor(x);assert sort in ['MaterialSchema','NominalExpr','MaterialProperty']
  obj=self.context();self.entities[obj]['attributes']=sorted(set(self.entities[obj]['attributes']+props))
  self.assertions.append({'position':pos,'source_id':self.rows[pos]['raw_id'],'input':obj,'attributes':props,'output_inheritance':False})
  return obj,sort
 def new_part(self,pos,parent,kind):
  obj=('W' if kind=='working_part' else 'P')+str(pos);before=self.current
  assert obj not in self.entities and parent in self.entities
  self.entities[obj]={'sort':'Material','initial_attributes':[],'attributes':[],'parent':parent,'relation':kind,'introduced_id':self.rows[pos]['raw_id']}
  self.parents.append({'child':obj,'parent':parent,'relation':kind,'introduced_id':self.rows[pos]['raw_id']})
  self.current=obj;self.writes.append({'position':pos,'before':before,'after':obj,'parent':parent})
  return obj
 def event(self,x,pos,patient=None):
  assert x['op']=='root';meaning,sort=self.lex[x['value']]
  assert sort in ['Event(Material)->same Material','Event(Material)->new Material part']
  patient=self.context() if patient is None else patient;assert patient in self.entities and self.entities[patient]['sort']=='Material'
  before=self.current;out=patient
  if sort.endswith('new Material part'):out=self.new_part(pos,patient,'retained_part')
  self.events.append({'position':pos,'source_id':self.rows[pos]['raw_id'],'predicate':x['value'],'patient':patient,'output':out,'current_before':before,'current_after':self.current,'writes_current':self.current!=before})
  return out,sort
 def record(self,pos,typ,output):
  self.trace.append({'position':pos,'source_id':self.rows[pos]['raw_id'],'surface':self.rows[pos]['raw_surface'],'expression_sort':typ,'output_sort':self.entities[output]['sort'],'output':output,'selected_context':self.context(),'topic':self.topic,'current':self.current,'owner':self.owner})
 def execute(self,x,pos):
  op=x['op']
  if op=='p':
   sort,props=self.descriptor(x['arg']);assert sort=='MaterialSchema'
   obj=self.initial;assert obj not in self.entities;self.entities[obj]={'sort':'Material','initial_attributes':props,'attributes':sorted(set(props)),'parent':None,'introduced_id':self.rows[pos]['raw_id']}
   self.topic=self.current=obj;out,typ=obj,'Material'
  elif op=='sh':
   sort,props=self.descriptor(x['arg']);assert sort=='ContainerSchema';parent=self.context();self.owner='C1'
   self.entities['C1']={'sort':'Container','attributes':props,'contains':parent,'introduced_id':self.rows[pos]['raw_id']};out,typ='C1','Container'
  elif op in ['q','s']:
   sort,_=self.descriptor(x['arg']);assert sort in ['MaterialSchema','NominalExpr']
   parent,_=self.resolve(x['arg'],pos);out=self.new_part(pos,parent,'proper_portion' if op=='q' else 'working_part');typ='Material'
  elif op=='nominal_event':
   patient,_=self.resolve(x['left'],pos);out,typ=self.event(x['right'],pos,patient)
  elif op=='root' and self.lex[x['value']][1].startswith('Event('):out,typ=self.event(x,pos)
  else:out,typ=self.resolve(x,pos)
  self.record(pos,typ,out)
 def semantic_graph(self):return {'entities':self.entities,'parents':self.parents,'events':self.events,'assertions':self.assertions,'writes':self.writes,'final_state':{'topic':self.topic,'current':self.current,'owner':self.owner}}
 def joined(self,x,leftpos,rightpos):
  assert x['op']=='nominal_event';patient,typ=self.resolve(x['left'],leftpos);self.record(leftpos,typ,patient)
  out,typ=self.event(x['right'],rightpos,patient);self.record(rightpos,typ,out)
def main():
 spec=json.loads((E/'src/SPEC.json').read_text());binding=json.loads((E/'src/BINDINGS.json').read_text());assert hashlib.sha256((E/'src/SPEC.json').read_bytes()).hexdigest()==binding['spec_sha256']
 data={}
 for k,b in spec['inputs'].items():
  raw=(ROOT/b['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256'];data[k]=json.loads(raw)
 a,t=data['author'],data['target'];assert a['target_sha256']==spec['inputs']['target']['sha256'];assert len(a['positions'])==129
 for c in t['contexts']:
  rows=[x for x in a['positions'] if x['context']==c['context']]
  for x,r in zip(rows,c['groups']):
   assert x['raw_id']==r['source_group_id'] and x['raw_surface']==r['ivtff_group_raw'] and ''.join(x['segmentation'])==x['raw_surface']
   assert x['left_separator']==r['left_separator'] and x['right_separator']==r['right_separator']
 rows=[x for x in a['positions'] if x['context']=='f80v.30-37'];f85=[x for x in a['positions'] if x['context']=='f85r1.1-6'];cases=[]
 for c in spec['candidates']:
  st=State(a,c['policy'],'M2',rows);pos=1
  while pos<=18:
   x=spec['f80_plan'][pos-1]
   if pos==13 and c['scope']=='NOMINAL_EVENT':
    assert spell(spec['scope_override']['NOMINAL_EVENT']['ast'])==rows[12]['raw_surface']+rows[13]['raw_surface']
    st.joined(spec['scope_override']['NOMINAL_EVENT']['ast'],13,14);pos=15;continue
   assert spell(x)==rows[pos-1]['raw_surface'];st.execute(x,pos);pos+=1
  parentmap={x['child']:x['parent'] for x in st.parents};events={str(x['position']):x['patient'] for x in st.events}
  assert parentmap==spec['predictions']['parents'][c['policy']] and events==spec['predictions']['events'][c['policy']]
  assert next(x for x in st.events if x['position']==16)['current_after']==spec['predictions']['current_after16']
  assert rows[18]['status']=='UNBOUND_UNPAID' and rows[18]['raw_surface']=='shol'
  graph=st.semantic_graph();digest=hashlib.sha256(json.dumps(graph,sort_keys=True).encode()).hexdigest()
  base=State(a,c['policy'],'M1',f85)
  for i,x in enumerate(spec['f85_plan'],1):assert spell(x)==f85[i-1]['raw_surface'];base.execute(x,i)
  cases.append({**c,'status':'CONDITIONAL_PROJECTION_CONSISTENT','graph_sha256':digest,'graph':graph,'trace':st.trace,'f85_graph':base.semantic_graph(),'f85_trace':base.trace,'stop':{'f80_position':19,'f80_surface':'shol','f85_position':4,'f85_surface':'otchdy'},'meaning_selected':False,'whole_complete':False})
 groups={}
 for x in cases:groups.setdefault(x['graph_sha256'],[]).append(x['id'])
 assert len(groups)==spec['predictions']['scope_groups']==2
 result={'experiment':'GDT1123','status':'CONDITIONAL_CONTINUATION_10_MORE_GROUPS__TWO_POLICY_CLASSES__WHOLE_PARTIAL','cases':cases,'graph_equivalence_groups':list(groups.values()),'primary_groups':129,'projected_groups':21,'newly_executed_groups':10,'remaining_unconsumed':108,'whole_contexts_complete':0,'lexical_values_changed':False,'rules_changed':False,'confirmed_words':0,'independent_confirmation_capacity':0,'significance_claim':False,'claim_ceiling':'Fixed finite nominal/context AST projection only; no generic parser theorem, meaningful corpus translation or policy winner'}
 write('RESULT.json',result)
 with (E/'artifacts/CANDIDATES.tsv').open('w',newline='') as f:
  keys=['id','policy','scope','status','graph_sha256','SHEY8_patient','CHEDY14_patient','SHEY16_patient','CURRENT_after16','remaining_unconsumed','meaning_selected'];w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader()
  for x in cases:
   ev={r['position']:r for r in x['graph']['events']};w.writerow({**{k:x[k] for k in keys[:5]},'SHEY8_patient':ev[8]['patient'],'CHEDY14_patient':ev[14]['patient'],'SHEY16_patient':ev[16]['patient'],'CURRENT_after16':ev[16]['current_after'],'remaining_unconsumed':108,'meaning_selected':False})
 with (E/'artifacts/ALL_POSITIONS.tsv').open('w',newline='') as f:
  keys=['context','position','raw_id','raw_surface','segmentation','original_status']+[x['id'] for x in cases];w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader()
  for row in a['positions']:
   out={k:row[k] for k in keys[:4]};out['segmentation']='+'.join(row['segmentation']);out['original_status']=row['status']
   for c in cases:
    tr=c['trace'] if row['context'].startswith('f80') else c['f85_trace'];match=next((x for x in tr if x['position']==row['position']),None)
    out[c['id']]=json.dumps(match,ensure_ascii=False,sort_keys=True) if match else 'UNBOUND_NOT_CONSUMED'
   w.writerow(out)
 print(json.dumps({k:result[k] for k in ['status','projected_groups','newly_executed_groups','remaining_unconsumed','graph_equivalence_groups','whole_contexts_complete']}))
if __name__=='__main__':main()
