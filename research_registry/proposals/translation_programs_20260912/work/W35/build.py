"""Capacity census only; frozen effects and identities, no state propagation engine."""
from pathlib import Path
import csv,json,hashlib,collections
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True)
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
def component(edges,start):
 seen={start};todo=[start]
 while todo:
  x=todo.pop()
  for a,b in edges:
   if x in (a,b):
    y=b if x==a else a
    if y not in seen:seen.add(y);todo.append(y)
 return sorted(seen)
def thermal(r):
 if r['kind']=='ACTION' and r['status']=='ASSUMED_EFFECT_APPLIED' and r['assertion']:
  f=json.loads(r['assertion'])
  if f['axis']=='thermal':return ('ACTION',f['value'])
 if r['kind']!='ACTION' and r['assertion'].startswith('PHYSICAL:thermal='):return ('ASSERTION',r['assertion'].split('=',1)[1])
 return None
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for r in S['inputs']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
relations=[];actions=[];future=[];candidates=[];worlds=[]
for lex in S['lexicons']:
 for shol in S['shol']:
  B=W/('W28' if lex=='C' else 'W33');prefix=shol if lex=='C' else 'O_'+shol
  traces=collections.defaultdict(list)
  for r in rows(B/(prefix+'_EVENTS.tsv')):
   assert not r['location'].startswith('f84')
   traces[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
  for key,trace in traces.items():
   p,g,chol,timing=key
   for mix in S['mix_models']:
    for rel in S['relation_models']:
     meta=dict(lexicon=lex,shol=shol,paragraph=p,grammar=g,chol=chol,timing=timing,mix=mix,relation=rel);edges=set();transfers=[]
     for i,r in enumerate(trace):
      if r['kind']!='ACTION':continue
      a,b=r['object'],r['second_object'];form=r['form']
      if form in S['mix_forms'] or form=='qotchy':
       before=sorted(edges);op=('JOIN' if mix=='D' else 'UNCHANGED') if form in S['mix_forms'] else ('JOIN' if rel=='V' else 'REMOVE_PAIR')
       status='UNARY_NO_EDGE' if op=='UNCHANGED' else 'MISSING_PARTICIPANT' if not a or not b else 'SAME_OBJECT' if a==b else 'APPLIED'
       if status=='APPLIED':
        pair=tuple(sorted((a,b)))
        if op=='JOIN':edges.add(pair)
        else:edges.discard(pair)
       relations.append(dict(**meta,index=i,operation=r['location'],form=form,patient=r['patient'],second=r['second'],object=a,second_object=b,contract=op,status=status,before=js(before),after=js(sorted(edges)),debts=r['debts']))
      t=thermal(r)
      if t:
       members=component(edges,a) if a else [];others=[x for x in members if x!=a]
       actions.append(dict(**meta,index=i,operation=r['location'],form=form,object=a,value=t[1],members=js(members),recipient_count=len(others),debts=r['debts']))
       for other in others:transfers.append((i,r,other,t[1],sorted(edges)))
     for i,r,other,value,connection_edges in transfers:
      later=[(j,x) for j,x in enumerate(trace) if j>i and (x['object']==other or x['second_object']==other)]
      checks=[(j,x,thermal(x)) for j,x in later if x['object']==other and thermal(x)]
      first=checks[0] if checks else None
      competing=[rr['location'] for j,rr,o,v,es in transfers if i<j<(first[0] if first else len(trace)) and o==other]
      status='NO_LATER_THERMAL_EVENT' if not first else 'OVERWRITTEN_BEFORE_CHECK' if first[2][0]=='ACTION' else 'COMPETING_TRANSFER_NEEDS_JOINT_MODEL' if competing else 'CHECKABLE_ASSERTION'
      L=json.loads(first[1]['before']).get('PHYSICAL:thermal','UNBOUND') if first else '';written=first[2][1] if first and first[2][0]=='ASSERTION' else ''
      def outcome(v):return 'UNBOUND' if v=='UNBOUND' else 'MATCH' if v==written else 'CONFLICT' if 'cold' in (v,written) and ('hot' in (v,written) or 'warm' in (v,written)) else 'DIFFERENT_NOT_OPPOSED'
      cid=dict(**meta,action=r['location'],recipient=other)
      candidates.append(dict(**cid,action_form=r['form'],acting_object=r['object'],connection=js(connection_edges),H_prediction=value,L_prediction=L,first_thermal_event=first[1]['location'] if first else '',written_value=written,status=status,competing=js(competing),H_result=outcome(value) if written else '',L_result=outcome(L) if written else '',later_events=len(later),independent_confirmation_capacity=0,debts=r['debts']))
      for j,x in later:future.append(dict(**cid,index=j,location=x['location'],kind=x['kind'],form=x['form'],object=x['object'],second_object=x['second_object'],assertion=x['assertion'],status=x['status'],before=x['before'],after=x['after'],debts=x['debts']))
     worlds.append(dict(**meta,events=len(trace),final_edges=js(sorted(edges)),potential_transfers=len(transfers)))
meta=['lexicon','shol','paragraph','grammar','chol','timing','mix','relation']
for n,rr,cols in [('RELATIONS.tsv',relations,meta+['index','operation','form','patient','second','object','second_object','contract','status','before','after','debts']),('THERMAL_ACTIONS.tsv',actions,meta+['index','operation','form','object','value','members','recipient_count','debts']),('CANDIDATES.tsv',candidates,meta+['action','recipient','action_form','acting_object','connection','H_prediction','L_prediction','first_thermal_event','written_value','status','competing','H_result','L_result','later_events','independent_confirmation_capacity','debts']),('ALL_RECIPIENT_FUTURES.tsv',future,meta+['action','recipient','index','location','kind','form','object','second_object','assertion','status','before','after','debts']),('WORLDS.tsv',worlds,meta+['events','final_edges','potential_transfers'])]:table(n,rr,cols)
result=dict(idea='IDEA000232',worlds=len(worlds),relation_cases=len(relations),thermal_action_cases=len(actions),potential_transfers=len(candidates),physical_transfer_pairs=len(set((r['action'],r['recipient']) for r in candidates)),recipient_future_events=len(future),candidate_statuses=dict(collections.Counter(r['status'] for r in candidates)),differing_checkable_predictions=sum(r['status']=='CHECKABLE_ASSERTION' and r['H_prediction']!=r['L_prediction'] for r in candidates),independent_confirmation_capacity=0,confirmed_meanings=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(js(result))
