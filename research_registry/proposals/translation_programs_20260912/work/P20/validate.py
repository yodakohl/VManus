import json,csv,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P20')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());p=Path(s['source'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'];assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
x=json.loads(p.read_text());seq=[(r['locus'].split('.')[0],r['locus']+':'+str(i),w) for r in x['lines'] for i,w in enumerate(r['groups'],1)];idx={a:i for i,(_,a,_) in enumerate(seq)}
m=json.loads((D/'MODEL.json').read_text());tech=m['technical_wholes'];units=m['units'];whole=m['whole_rival']
for mode in ['M','W']:assert [(r['record'],r['at'],r['word']) for r in read('ALIGNMENT_'+mode+'.tsv')]==seq
cs=read('ALL_CLASSES.tsv');assert [(r['record'],r['at'],r['word']) for r in cs]==seq
for c in cs:
 w=c['word']
 if w in tech:assert c['M_class']=='TECH' and not c['parts'];continue
 # Enumerate all complete parses independently rather than longest-match code.
 def parses(rest):
  if not rest:return [[]]
  return [[u]+tail for u in units if rest.startswith(u) for tail in parses(rest[len(u):])]
 ps=parses(w)
 if c['parts']:
  parts=c['parts'].split('+');assert parts in ps and ''.join(parts)==w
  assert c['target']==''.join(units[u] for u in parts)
 else:assert not ps
for e in read('ALL_GRAMMAR_BINDINGS.tsv'):
 i=idx[e['at']]
 for side,step in [('left',-1),('right',1)]:
  if side=='left' and e['word']=='dain':continue
  j=i+step;found=''
  while 0<=j<len(seq):
   r,a,w=seq[j]
   if r!=e['record'] or w in whole:break
   if w in tech:found=a;break
   j+=step
  assert e[side]==found
for a,b in zip(read('ALIGNMENT_M.tsv'),read('ALIGNMENT_W.tsv')):
 if a['word'] in whole or a['word'] in tech:assert a['reading'].split(' [Pakete=')[0]==b['reading']
res=json.loads((D/'RESULT.json').read_text());assert res['new_interpreted_wholes']==[]
assert res['bound_grammar']==sum(not r['missing'] for r in read('ALL_GRAMMAR_BINDINGS.tsv'))==7
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source/decision hashes','both145group alignments','independent complete package enumeration','technical-whole priority','all17grammar endpoints','semantic equality of the two readers on interpreted forms'],limitation='No Latin language, phonetic value, case or meaning identification'),indent=2)+'\n')
print('PASS')
