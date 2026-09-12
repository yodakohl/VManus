import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P07')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());source=Path(s['source'])
assert hashlib.sha256(source.read_bytes()).hexdigest()==s['sha256']
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
expected=[(r['record_id'],r['locus']+':'+str(i),w) for r in csv.DictReader(source.open(),delimiter='\t') for i,w in enumerate(r['zl3b_line'].split(),1)]
assert len(expected)==341
lookup={p:(i,r,w) for i,(r,p,w) in enumerate(expected)}
for scope in ['RECORD','PANEL']:
 for world in ['BODY','STATION']:
  a=read('ALIGNMENT_'+world+'_'+scope+'.tsv')
  assert [(r['record'],r['at'],r['word']) for r in a]==expected
 for e in read('EVENTS_'+scope+'.tsv'):
  i,r,w=lookup[e['at']];assert w==e['word']
  for key in ['site','water','wet_producer']:
   if e[key]:
    j,r2,w2=lookup[e[key]];assert j<i
    if scope=='RECORD':assert r2==r
  if e['target']:
   j,r2,w2=lookup[e['target']];assert j>i and r2==r
   assert not any(x[2] in ['chedy','qokeedy','qokedy','qokaiin','shedy','lchedy'] for x in expected[i+1:j])
  if e['wet_producer']:
   producers={x['at']:x for x in read('EVENTS_'+scope+'.tsv')}
   assert not producers[e['wet_producer']]['missing']
 b=read('ALIGNMENT_BODY_'+scope+'.tsv');t=read('ALIGNMENT_STATION_'+scope+'.tsv')
 for x,y in zip(b,t):
  norm=x['reading']
  for a,z in [('Unterkörper','Auslass'),('Hand','Einlass'),('Rumpf','Mittelbecken')]:norm=norm.replace(a,z)
  assert norm==y['reading']
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source and decision hashes','all four complete alignments','antecedent direction and primary record scope','nearest eligible target','complete wet-state producer','body/station exact renaming equivalence'],limitation='Internal artifact validation; not independent meaning evidence'),indent=2)+'\n')
print('PASS')
