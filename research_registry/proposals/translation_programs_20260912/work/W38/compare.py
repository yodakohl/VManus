from pathlib import Path
import csv,json,collections,hashlib
E=Path(__file__).resolve().parent;B=E.parent/'W37'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(x):return json.dumps(x,sort_keys=True,ensure_ascii=False)
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
cases=[];history=[];future=[];changes=[];groups=[]
meta=['scope','shol','paragraph','grammar','model','timing','target']
for scope in ['P','C']:
 for sm in ['Q','A']:
  prefix=scope+'_'+sm;events=rows(E/(prefix+'_EVENTS.tsv'));traces=collections.defaultdict(list)
  for r in events:traces[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
  for key,trace in traces.items():
   for loc in dict.fromkeys(r['location'] for r in trace if r['form']=='chkaiin'):
    tt=[r for r in trace if r['location']==loc and r['kind']=='QUALITY'];assert len(tt)==2
    th=next(r for r in tt if ':thermal=' in r['assertion']);mo=next(r for r in tt if ':moisture=' in r['assertion']);oid=th['object'];assert mo['object']==oid
    m=dict(zip(meta,[scope,sm,*key,loc]));cases.append(dict(**m,patient=th['patient'],object=oid,thermal_prediction='hot',moisture_prediction='dry',thermal_before=th['before'],moisture_before=mo['before'],thermal_status=th['status'],moisture_status=mo['status'],thermal_origin=th['state_origin'],moisture_origin=mo['state_origin'],debts=th['debts'],independent_confirmation_capacity=0))
    first=min(int(r['execution_index']) for r in tt);last=max(int(r['execution_index']) for r in tt)
    if not oid:continue
    for r in trace:
     if r['object']!=oid and r['second_object']!=oid:continue
     if int(r['execution_index'])<first:history.append(dict(**m,location=r['location'],kind=r['kind'],form=r['form'],assertion=r['assertion'],status=r['status'],before=r['before'],after=r['after'],debts=r['debts']))
     if int(r['execution_index'])>last:future.append(dict(**m,location=r['location'],kind=r['kind'],form=r['form'],assertion=r['assertion'],status=r['status'],before=r['before'],after=r['after'],debts=r['debts']))
  for name,keys in [('ARGUMENTS',['paragraph','grammar','operation']),('QUALITY',['paragraph','grammar','mention','axis']),('TAKE_ARGUMENTS',['paragraph','grammar','target']),('EVENTS',['paragraph','grammar','model','timing','kind','location','assertion'])]:
   old={tuple(r[k] for k in keys):r for r in rows(B/('S_'+sm+'_'+name+'.tsv'))};new={tuple(r[k] for k in keys):r for r in rows(E/(prefix+'_'+name+'.tsv'))}
   for key in sorted(old.keys()|new.keys()):
    a=old.get(key,{});b=new.get(key,{});diff=[k for k in a.keys()|b.keys() if k not in ['source_event','execution_index','row_status'] and a.get(k)!=b.get(k)]
    if diff:changes.append(dict(scope=scope,shol=sm,table=name,key='|'.join(key),fields=';'.join(sorted(diff)),baseline=js(a),new=js(b)))
  groups.append(dict(scope=scope,shol=sm,digest=hashlib.sha256(js(events).encode()).hexdigest(),scope_note='Complete event trace, not independent evidence'))
table('CANDIDATES.tsv',cases,list(cases[0]));cols=meta+['location','kind','form','assertion','status','before','after','debts'];table('ALL_PRIOR_CARRIER_EVENTS.tsv',history,cols);table('ALL_LATER_CARRIER_EVENTS.tsv',future,cols);table('ALL_CHANGES.tsv',changes,list(changes[0]));table('PREDICTION_GROUPS.tsv',groups,list(groups[0]))
r=dict(idea='IDEA000235',source_paragraphs=17,source_groups=1045,new_worlds=816,new_events=22272,target_cases=len(cases),target_assertions=2*len(cases),prior_carrier_events=len(history),later_carrier_events=len(future),new_target_conflicts=sum(c[k]=='CONFLICT' for c in cases for k in ['thermal_status','moisture_status']),new_target_missing=sum(c[k]=='MISSING_PATIENT' for c in cases for k in ['thermal_status','moisture_status']),changes=dict(collections.Counter(c['scope']+'_'+c['table'] for c in changes)),semantic_assumption_positions=614,structural_hypothesis_positions=1,unread_positions=430,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(js(r))
