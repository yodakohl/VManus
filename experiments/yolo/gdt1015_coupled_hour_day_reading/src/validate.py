"""Separate literal-circle replay. Does not import the primary engine."""
import json,hashlib,collections,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1];A=P/'artifacts'
def load(p):return json.loads(p.read_text())
def main():
 lock=load(P/'CANDIDATE_LOCK.json')
 for f,h in lock['files'].items():assert hashlib.sha256((P/f).read_bytes()).hexdigest()==h
 m=load(P/'MODEL_v01.json');s=load(P/'src/SOURCE.json');rows=load(A/'ROWS.json')
 positions=[]
 for c in m['clauses']:
  positions+=list(range(c['start'],c['end']+1))
  assert c['words']==s['words'][c['start']-1:c['end']]
  assert [m['lexicon'][w]['value'] for w in c['words']]==c['pattern']
 assert positions==list(range(1,81)) and len(m['lexicon'])==60
 assert {w:e['origin'] for w,e in m['lexicon'].items() if e['origin']=='RAW379_HYPOTHESIS'}=={w:'RAW379_HYPOTHESIS' for w in s['old_hypotheses']}
 numeric={'SEVEN':7,'TWENTY_FOUR':24,'THREE':3,'ONE_MEMBER':1}
 num=lambda pos:numeric[m['lexicon'][s['words'][pos-1]]['value']]
 size,span,removed=num(10),num(41),num(52)
 circle=m['arithmetic']['label_order_for_source_example'];assert len(circle)==size==len(set(circle))
 successor={circle[i]:circle[i+1] if i+1<size else circle[0] for i in range(size)}
 predecessor={v:k for k,v in successor.items()}
 units=[num(66),num(67)];candidates={r['id']:r for r in m['candidates']}
 expected={(c['id'],d,p) for c in m['candidates'] for d in (range(1,span) if c['id'] in ['NIGHT_RESET','NIGHT_REVERSE'] else [None]) for p in range(size)}
 assert {(r['candidate'],r['daylight_hours'],r['initial_phase']) for r in rows}==expected and len(rows)==len(expected)
 residual=list(range(span))
 for _ in range(removed):
  for _ in circle: residual.pop(0)
 assert len(residual)<size
 checked=[]
 for r in rows:
  o=candidates[r['candidate']]['overrides'];d=r['daylight_hours'];start=circle[r['initial_phase']]
  literal=[start]
  for hour in range(1,span+1):
   if o.get('night_reset') and hour==d: item=start
   elif o.get('night_direction')==-1 and hour-1>=d:item=predecessor[literal[-1]]
   else:item=successor[literal[-1]]
   literal.append(item)
  assert literal==r['hour_trace_names']
  a=literal[-2] if o.get('method_a_endpoint')=='last' else literal[-1]
  current=start;counted=[]
  for amount in ([max(units)] if o.get('double_unit')=='same_skipped_member' else units):
   for _ in range(amount):current=successor[current];counted.append(current)
  current=successor[current]
  if o.get('selection')=='one_past_first_unskipped':current=successor[current]
  b=current;agree=a==b;final=True if o.get('comparison')=='B_B' else agree
  assert (a,b,agree,final,len(residual))==(r['method_a_ruler'],r['method_b_ruler'],r['C11_same'],r['C12_agrees'],r['remainder'])
  assert r['argument_coherent']==(agree and final)
  assert r['source_continuous_hours']==all(successor[x]==y for x,y in zip(literal,literal[1:]))
  checked.append({'setting':r['setting'],'phase':r['initial_phase'],'A':a,'B':b,'skipped_members':counted,'coherent':agree and final})
 validation={'status':'PASS','full_coverage_positions':len(positions),'independent_literal_replays':len(checked),'known_source_first_three_days':[circle[0],successor[successor[successor[circle[0]]]],successor[successor[successor[successor[successor[successor[circle[0]]]]]]]],'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'meaning_validation':False,'confirmed_words':0}
 (A/'INDEPENDENT.json').write_text(json.dumps(checked,indent=2)+'\n');(A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
 print(json.dumps(validation,indent=2))
if __name__=='__main__':main()
