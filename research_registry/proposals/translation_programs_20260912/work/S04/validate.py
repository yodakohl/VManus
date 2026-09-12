"""Independent prefix enumeration of written guards and completion causes."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(n):return list(csv.DictReader((H/n).open(),delimiter='\t'))
manifest=json.loads((H/'SOURCE.json').read_text())
for item in manifest['files']:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
lines=list(csv.DictReader((R/manifest['files'][0]['path']).open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 for n,w in enumerate(line['zl3b_line'].split(),1):raw.append((line['record_id'],line['locus'],line['locus']+':'+str(n),w))
assert len(raw)==341 and len(lines)==51
keys=['record','locus','at','word'];assert [tuple(x[k] for k in keys) for x in read('INPUT.tsv')]==raw
idx={x[2]:i for i,x in enumerate(raw)};materials={'shedy','lchedy'}
def ref(i):
 p=next((j for j in range(i-1,-1,-1) if raw[j][0]==raw[i][0] and raw[j][3] in materials),None)
 d=next((j for j in range(i-1,-1,-1) if raw[j][0]==raw[i][0] and raw[j][3]=='qokaiin'),None)
 return p,d
def pair(i):
 p,d=ref(i);return (raw[i][0],raw[p][3]) if p is not None and d is not None else None
def guard(i):return next((j for j in range(i-1,-1,-1) if raw[j][3]=='qokedy' and pair(i) is not None and pair(j)==pair(i)),None)
def executed(i,mode):
 if pair(i) is None:return 0
 if mode=='N':return 1
 if guard(i) is None:return 0
 # A licensed written qokedy already supplies FILLED and no model action negates it.
 return 0 if mode=='PRE' else 1
res=json.loads((H/'RESULT.json').read_text());all_events={};total=0
for mode in ['N','PRE','POST']:
 align=read('ALIGNMENT_'+mode+'.tsv');events=read('EVENTS_'+mode+'.tsv');assert [tuple(x[k] for k in keys) for x in align]==raw
 assert [e['at'] for e in events]==[x[2] for x in raw if x[3] in {'chedy','qokeedy','qokeey','qokedy','qoteedy'}]
 for e in events:
  i=idx[e['at']];p,d=ref(i);k=pair(i);g=guard(i)
  assert e['patient']==(raw[p][3] if p is not None else 'NONE') and e['patient_source']==(raw[p][2] if p is not None else 'NONE')
  assert e['destination']==(raw[d][2] if d is not None else 'NONE')
  assert e['written_condition']==(raw[g][2] if g is not None else 'NONE')
  causes=[j for j in range(i) if k is not None and pair(j)==k and (raw[j][3] in {'qokedy','qokeedy'} or raw[j][3]=='qoteedy' and executed(j,mode))]
  prior='UNBOUND_PAIR' if k is None else 'FILLED' if causes else 'UNKNOWN'
  assert e['prior_state']==prior and e['prior_cause']==(raw[causes[-1]][2] if causes else 'NONE')
  w=raw[i][3];body=executed(i,mode) if w=='qoteedy' else 0
  if w=='chedy':status='BOUND' if p is not None else 'MISSING_MATERIAL'
  elif k is None:status='MISSING_PARTICIPANT'
  elif w=='qokeey':status='RUNNING_WITHOUT_COMPLETION'
  elif w=='qokedy':status='ASSERT_FILLED'
  elif w=='qokeedy':status='EXECUTE_FILL'
  elif mode!='N' and g is None:status='MISSING_WRITTEN_CONDITION'
  else:status='EXECUTE_BODY' if body else 'SKIP_SATISFIED'
  assert e['status']==status and int(e['body_executions'])==body
  expected='FILLED' if status in {'ASSERT_FILLED','EXECUTE_FILL','EXECUTE_BODY'} else prior
  assert e['after_state']==expected;total+=1
 calls=[e for e in events if e['word']=='qoteedy'];assert calls==read('CALLS_'+mode+'.tsv')
 assert res['variants'][mode]['call_statuses']==dict(Counter(c['status'] for c in calls))
 assert res['variants'][mode]['additional_body_executions']==sum(int(c['body_executions']) for c in calls)
 for a,x in zip(align,raw):assert x[3]+' → '+a['render'] in (H/('READING_'+mode+'.md')).read_text()
 assert sum(a['read_status']=='HYPOTHESIS' for a in align)==72 and sum(a['read_status']=='OPEN' for a in align)==269
 all_events[mode]=events
obs=read('ALL_STATE_COMPARISONS.tsv');expected=[(p,q) for p,q in zip(all_events['PRE'],all_events['POST']) if p['word'] in {'qokedy','chedy'}]
assert len(obs)==len(expected)==27
for o,(p,q) in zip(obs,expected):
 assert o['at']==p['at']==q['at'] and o['PRE_prior']==p['prior_state'] and o['POST_prior']==q['prior_state'] and o['state_equal']=='True'
 assert o['PRE_cause']==p['prior_cause'] and o['POST_cause']==q['prior_cause']
assert total==126
out={'status':'PASS','raw_groups_per_reading':341,'readings':3,'events':126,'call_rows':15,'state_comparisons':27,'PRE_POST_state_differences':0,'scope':'independent prefix reconstruction; no false guard, multi-iteration, semantic or held-data confirmation'}
(H/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
