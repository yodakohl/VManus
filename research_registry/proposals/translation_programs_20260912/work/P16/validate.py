import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P16')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());src=Path(s['source'])
assert hashlib.sha256(src.read_bytes()).hexdigest()==s['sha256']
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
seq=[(r['record_id'],r['locus']+':'+str(i),w) for r in csv.DictReader(src.open(),delimiter='\t') for i,w in enumerate(r['zl3b_line'].split(),1)]
idx={at:(i,r,w) for i,(r,at,w) in enumerate(seq)}
for mode in ['C','U']:assert [(r['record'],r['at'],r['word']) for r in read('ALIGNMENT_'+mode+'.tsv')]==seq
pp=read('PROPOSITIONS.tsv');by={p['at']:p for p in pp};rr=read('RULES.tsv');ops=read('OPERATORS.tsv')
assert len(seq)==341 and len(pp)==38 and len(ops)==15
for p in pp:
 i,r,w=idx[p['at']];left=[(a,x) for z,a,x in seq[:i] if z==r and x in ['qokaiin','shedy']]
 assert p['material_locus']==(left[-1][0] if left else '')
 assert (p['negative']=='True')==(len(p['negations'].split(','))%2==1 if p['negations'] else False)
for o in ops:
 i,r,w=idx[o['at']]
 for side,direction in [('right',1),('left',-1)]:
  if w=='chey' and side=='left':continue
  candidate='';j=i+direction
  while 0<=j<len(seq):
   z,a,x=seq[j]
   if z!=r or x in ['sol','qokal']:break
   if a in by:candidate=a;break
   j+=direction
  assert o[side]==candidate
for rule in rr:
 assert not rule['issues'] and by[rule['left']]['kind']=='state'
 assert by[rule['left']]['material'] and by[rule['right']]['material']
cases=read('ALL_CASES.tsv');assert len(cases)==126
for c in cases:
 local=[p for p in pp if p['record']==c['record']];rules=[r for r in rr if r['record']==c['record']]
 consumed={r[k] for r in rules for k in ['left','right']} if c['mode']=='C' else set()
 active={p['at'] for p in local if p['at'] not in consumed}
 def truth(p):return (c[p['material']]==p['value']) != (p['negative']=='True')
 if c['mode']=='C':
  for r in rules:
   if truth(by[r['left']])==(r['word']=='sol'):active.add(r['right'])
 assert active==set(filter(None,c['active'].split(',')))
 bad={a for a in active if by[a]['material'] and by[a]['kind']=='state' and not truth(by[a])}
 assert bad==set(filter(None,c['violated_states'].split(',')))
 req={};forbid={}
 for a in active:
  p=by[a]
  if p['material'] and p['kind']=='action':(forbid if p['negative']=='True' else req).setdefault(p['value']+'('+p['material']+')',set()).add(a)
 assert req=={k:set(v) for k,v in json.loads(c['required']).items()}
 assert forbid=={k:set(v) for k,v in json.loads(c['forbidden']).items()}
 assert (c['consistent']=='True')==(not bad and not(set(req)&set(forbid)))
res=json.loads((D/'RESULT.json').read_text())
for x in res['summary']:
 for m in ['C','U']:assert x[m+'_consistent']==sum(c['record']==x['record'] and c['mode']==m and c['consistent']=='True' for c in cases)
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source and decision hashes','both complete alignments','material antecedents','nearest bounded connector endpoints','negation parity','all126 cases independently replayed as assertion and command sets'],limitation='Not independent semantic evidence'),indent=2)+'\n')
print('PASS')
