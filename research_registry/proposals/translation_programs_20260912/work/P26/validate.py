import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P26')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());p=Path(s['source'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
source=[(r['record_id'],r['locus']+':'+str(i),w) for r in csv.DictReader(p.open(),delimiter='\t') for i,w in enumerate(r['zl3b_line'].split(),1)]
idx={at:(i,r,w) for i,(r,at,w) in enumerate(source)}
assert len(source)==341
assert [w for r,a,w in source if a in ['f83r.6:'+str(i) for i in range(5,10)]]==['qokaiin','chedy','qokeedy','lchedy','qoky']
for mode in ['M','N']:
 a=read('ALIGNMENT_'+mode+'.tsv');assert [(r['record'],r['at'],r['word']) for r in a]==source
 events=read('EVENTS_'+mode+'.tsv');by={e['at']:e for e in events}
 assert len(events)==40
 for e in events:
  i,r,w=idx[e['at']];left=source[:i]
  candidates=[a for rr,a,ww in left if rr==r and ww in ['qokaiin','shedy']]
  assert e['material']==(candidates[-1] if candidates else '')
  if w=='qoky':
   v=[a for rr,a,ww in left if rr==r and ww=='lchedy'];assert e['vessel']==(v[-1] if v else '')
  if w=='qokeedy':
   v=''
   for rr,at,ww in source[i+1:]:
    if rr!=r or ww in ['chedy','qokeedy','qokedy','qoky','qokaiin','shedy']:break
    if ww=='lchedy':v=at;break
   assert e['vessel']==v
  if e['producer']:
   prod=e['producer'].split('#')[0];q=by[prod];assert idx[prod][0]<i and q['record']==r and not q['missing']
   assert q['material_word']==e['material_word']
   assert q['kind']=='call' or (q['word']=='qokeedy' and json.loads(q['before']).get('heat'))
   assert not any(x['word']=='chedy' and x['material_word']==e['material_word'] and idx[prod][0]<idx[x['at']][0]<i for x in events)
  if e['kind']=='call':
   after=json.loads(e['after']);before=json.loads(e['before'])
   if e['missing']:assert before==after
   else:assert after['prepared']==e['at']+'#2' and after['heat']==e['at']+'#1'
 calls=read('CALLS_'+mode+'.tsv');assert len(calls)==7
 assert [x['at'] for x in calls]==[a for _,a,w in source if w=='qoky']
 if mode=='M':assert sum(x['kind']=='definition' for x in calls)==1 and sum(x['kind']=='call' for x in calls)==6
 else:assert all(x['kind']=='noun' for x in calls)
comp=read('ALL_STATE_COMPARISONS.tsv');assert len(comp)==13
assert [r['at'] for r in comp if r['M_only']=='true']==['f83r.21:2']
res=json.loads((D/'RESULT.json').read_text());assert res['hypothesis_positions']==70 and res['open_positions']==271
for mode in ['M','N']:
 es=read('EVENTS_'+mode+'.tsv');assert res['summary'][mode]['traced_states']==sum(bool(e['producer']) for e in es)
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source and pre-run decision hashes','all source positions both readers','actual definition sequence','nearest typed left parameters and bounded right targets','all seven qoky occurrences','state producer completeness and intervening reheating','fixed two-step call state','all thirteen state comparisons'],limitation='Internal reproducibility checks, not independent semantic validation'),indent=2)+'\n')
print('PASS')
