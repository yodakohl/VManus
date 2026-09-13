import csv,json,hashlib
from collections import defaultdict
from pathlib import Path
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text());old=Path(S['old'])
read=lambda p:list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
raw=read(S['source']);events=read(D/'EVENTS.tsv');portions=read(D/'PORTIONS.tsv');stocks=read(D/'STOCKS.tsv');al=read(D/'ALIGNMENT.tsv')
assert len(raw)==341 and len(events)==252
nchecks=0;positive_checks=0
for mode in S['modes']:
 es=read(old/('EVENTS_'+mode+'.tsv'))
 execution=[e for e in es if e['status'] in ['EXECUTE_FILL','EXECUTE_BODY']]
 assert all(int(e['body_executions'])==int(e['status']=='EXECUTE_BODY') for e in es)
 pp=[p for p in portions if p['mode']==mode]
 assert [p['at'] for p in pp]==[e['at'] for e in execution]
 seen=defaultdict(int)
 for e,p in zip(execution,pp):
  seen[e['record']]+=1
  assert (p['record'],p['material'],p['recipient_mention'])==(e['record'],e['patient'],e['destination'])
  assert p['recipient']==e['record']+':B'
  assert int(p['illustrative_time'])==seen[e['record']] and int(p['illustrative_amount'])==1
  assert p['portion']=='d['+e['at']+']'
 for family in ['R','C']:
  world=mode+'_'+family;out=[e for e in events if e['world']==world]
  assert [{k:e[k] for k in es[0]} for e in out]==es
  for e in out:
   n=int(e['status'] in ['EXECUTE_FILL','EXECUTE_BODY'])
   assert int(e['executions'])==n
   if family=='C' and n:assert e['consumption']=='d['+e['at']+']' and e['appointment']=='t['+e['at']+']'
   else:assert not e['consumption'].startswith('d[')
   nchecks+=1
  aa=[a for a in al if a['world']==world]
  assert [(a['at'],a['word']) for a in aa]==[(r['at'],r['word']) for r in raw]
  ss=[s for s in stocks if s['world']==world]
  assert len(ss)==14
  for s in ss:
   need=[p for p in pp if p['record']==s['record'] and p['material']==s['material']];n=len(need)
   assert int(s['executed_bodies'])==n
   assert int(s['new_portions'])==(n if family=='C' else 0)
   expected='+'.join(p['portion'] for p in need) if family=='C' and n else '0_IN_THIS_SUBSYSTEM'
   assert s['partial_consumption']==expected
   start=int(s['illustrative_initial']);end=int(s['illustrative_final'])
   assert start==n+1 and end==start-(n if family=='C' else 0) and end>0
   positive_checks+=1
text=(D/'READING.md').read_text()
for line in dict.fromkeys(r['locus'] for r in raw):assert line+': `'+ ' '.join(r['word'] for r in raw if r['locus']==line)+'`' in text
result=dict(status='PASS',bound_files=len(S['hashes']),groups=len(raw),unchanged_old_event_projections=nchecks,executed_body_witnesses=len(portions),positive_stock_assignments=positive_checks,complete_alignment_rows=len(al),independent_meaning_validation=False,scope='resource subsystem only; no validation of clinical meaning or full S04 success')
(D/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
