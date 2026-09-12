"""Independent list-prefix role reconstruction and per-vessel event replay."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(n):return list(csv.DictReader((H/n).open(),delimiter='\t'))
manifest=json.loads((H/'SOURCE.json').read_text())
for x in manifest['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
lines=list(csv.DictReader((R/manifest['files'][0]['path']).open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 for n,w in enumerate(line['zl3b_line'].split(),1):raw.append((line['record_id'],line['locus'],line['locus']+':'+str(n),w))
assert len(raw)==341 and len(lines)==51
assert [tuple(x[k] for k in ['record','locus','at','word']) for x in read('INPUT.tsv')]==raw
mat={'shedy':'A','lchedy':'C'};boundaries={'qokeedy','qokedy','qokeey'};operations=boundaries|{'chedy'}
def requested(i,op):
 if op in {'HEAT','FILL'}:return next((j for j in range(i-1,-1,-1) if raw[j][0]==raw[i][0] and raw[j][3] in mat),None)
 if op!='WITHDRAW':return None
 stop=next((j for j in range(i+1,len(raw)) if raw[j][0]!=raw[i][0] or raw[j][3] in boundaries),len(raw))
 return next((j for j in range(i+1,stop) if raw[j][3] in mat),None)
result=json.loads((H/'RESULT.json').read_text());total=0
for mode in ['D','R','E']:
 for initial in ['0','?']:
  tag=mode+('0' if initial=='0' else 'U');rows=read('EVENTS_'+tag+'.tsv');align=read('ALIGNMENT_'+tag+'.tsv');assert [tuple(x[k] for k in ['record','locus','at','word']) for x in align]==raw
  assert [x['at'] for x in rows]==[x[2] for x in raw if x[3] in operations]
  eventmap={e['at']:e for e in rows};states={};first_problem='NONE';first_conflict='NONE'
  for i,x in enumerate(raw):
   relevant=[p for p in raw[:i+1] if p[3]=='qokaiin' and (mode!='R' or p[0]==x[0])]
   device=(x[0] if mode=='R' else 'SHARED') if relevant else 'NONE'
   if device!='NONE' and device not in states:states[device]=(frozenset(),initial=='?')
   if x[3] in operations:
    e=eventmap[x[2]];op={'chedy':'HEAT','qokeedy':'FILL','qokedy':'WITHDRAW','qokeey':'EMPTY' if mode=='E' else 'OPEN'}[x[3]];target=requested(i,op);c=mat[raw[target][3]] if target is not None else 'NONE'
    assert e['vessel']==device and e['material_source']==(raw[target][2] if target is not None else 'NONE') and e['component']==c and e['op']==op
    s,u=states.get(device,(frozenset(),False));before=(s,u)
    assert e['before']=='NO_VESSEL' if device=='NONE' else json.loads(e['before'])=={'components':sorted(s),'unknown':u}
    missing=[]
    if op in {'HEAT','FILL','WITHDRAW'} and target is None:missing.append('MATERIAL')
    if op in {'FILL','WITHDRAW','EMPTY'} and device=='NONE':missing.append('VESSEL')
    if op=='OPEN':status='OPEN'
    elif missing:status='MISSING_'+'_AND_'.join(missing)
    elif op=='HEAT':status='BOUND_NO_COMPONENT_CHANGE'
    elif op=='FILL':s=s|{c};status='COMPLETE'
    elif op=='EMPTY':s=frozenset();u=False;status='COMPLETE'
    elif any(t!=c for t in s):status='CONFLICT_OTHER_COMPONENT'
    elif u:status='UNRESOLVED_INITIAL_CONTENT'
    elif len(s)==0:status='CONFLICT_EMPTY'
    else:s=frozenset();status='COMPLETE'
    assert e['status']==status and e['prior_problem']==first_problem
    if status.startswith(('MISSING','CONFLICT','UNRESOLVED')) and first_problem=='NONE':first_problem=x[2]
    if status.startswith('CONFLICT') and first_conflict=='NONE':first_conflict=x[2]
    if device!='NONE':states[device]=(s,u);assert json.loads(e['after'])=={'components':sorted(s),'unknown':u}
    else:assert e['after']=='NO_VESSEL'
    if status.startswith(('MISSING','CONFLICT','UNRESOLVED')):assert (s,u)==before
    total+=1
   a=align[i];assert a['word']+' → '+a['render'] in (H/('READING_'+tag+'.md')).read_text()
   assert a['vessel']==device
   if device!='NONE':assert json.loads(a['inventory'])=={'components':sorted(states[device][0]),'unknown':states[device][1]}
  summary=result['variants'][mode+initial]
  assert summary['first_problem']==first_problem and summary['first_conflict']==first_conflict
  assert summary['withdrawals']==dict(Counter(e['status'] for e in rows if e['op']=='WITHDRAW'))
  assert summary['fills']==dict(Counter(e['status'] for e in rows if e['op']=='FILL'))
  assert summary['hypothetical_positions']==sum(x['read_status']=='HYPOTHESIS' for x in align)
  assert summary['open_positions']==sum(x['read_status']=='OPEN' for x in align)
  assert summary['final_vessels']=={k:{'components':sorted(s),'unknown':u} for k,(s,u) in states.items()}
assert total==222
report={'status':'PASS','groups_per_reading':341,'readings':6,'event_rows':total,'withdrawal_rows':78,'source_hashes':3,'checks':['prefix-only input/device and fixed right output','all state transitions and retained failed states','unknown initial content not converted to empty','all records and devices retained'],'limit':'No semantic proof; later conflicting states are conditional after earlier missing/conflicting/unresolved events'}
(H/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
