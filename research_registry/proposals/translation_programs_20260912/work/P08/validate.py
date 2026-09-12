import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P08')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for f in s['sources']:assert hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
x=json.loads(Path(s['sources'][0]['path']).read_text());seq=[(r['locus'].split('.')[0],'H',r['locus']+':'+str(i),w) for r in x['lines'] for i,w in enumerate(r['groups'],1)]
seq += [(r['record_id'],'B',r['locus']+':'+str(i),w) for r in csv.DictReader(Path(s['sources'][1]['path']).open(),delimiter='\t') for i,w in enumerate(r['zl3b_line'].split(),1)]
assert len(seq)==486
for m in ['A','D']:assert [(r['record'],r['domain'],r['at'],r['word']) for r in read('ALIGNMENT_'+m+'.tsv')]==seq
model=json.loads((D/'MODEL.json').read_text());es=read('ALL_RELATIONS.tsv');idx={a:i for i,(_,_,a,_) in enumerate(seq)}
assert [e['at'] for e in es]==[a for _,_,a,w in seq if w in ['daiin','shey']]
for e in es:
 i=idx[e['at']]
 for side,direction in [('left',-1),('right',1)]:
  j=i+direction;target='';gap=[]
  while 0<=j<len(seq):
   r,d,a,w=seq[j]
   if r!=e['record'] or w in ['daiin','shey']:break
   if w in model['nouns'][d]:target=a;break
   gap.append(a+'='+w);j+=direction
  assert e[side]==target
  assert e[side+'_gap']==' '.join(gap if direction==1 else reversed(gap))
 assert (e['self_edge']=='True')==(bool(e['left']) and bool(e['right']) and e['left_word']==e['right_word'])
expected={(a['at'],b['at']) for a in es for b in es if a is not b and a['record']==b['record'] and not a['missing'] and not b['missing'] and a['right']==b['left']}
assert {(c['first'],c['second']) for c in read('CHAINS.tsv')}==expected
assert len(expected)==3
result=json.loads((D/'RESULT.json').read_text())
for d in ['H','B']:
 assert result['summary'][d]['complete']==sum(e['domain']==d and not e['missing'] for e in es)
# Strict cycles are independently checked by depth-first walks.
for m in ['A','D']:
 expected_cycles=set()
 for r in {t[0] for t in seq}:
  graph={}
  for e in es:
   rel=model['relations'][m][e['domain']][e['word']]
   if e['record']!=r or e['missing'] or rel not in ['enthält','ist Teil von']:continue
   a,b=(e['right_word'],e['left_word']) if rel=='enthält' else (e['left_word'],e['right_word']);graph.setdefault(a,set()).add(b)
  for a in graph:
   queue=list(graph[a]);seen=set()
   while queue:
    b=queue.pop()
    if b==a:expected_cycles.add((r,a));break
    if b not in seen:seen.add(b);queue.extend(graph.get(b,[]))
 actual={(i['record'],i['at']) for i in read('ISSUES.tsv') if i['mode']==m and i['status']=='STRICT_CYCLE'}
 assert actual==expected_cycles
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['input and decision hashes','both486group alignments','all18relations and bounded endpoints','all intervening unknowns','all three shared-position chains','self identities','independent strict-cycle search'],limitation='Not GDT388 score-ready relation evidence or independent meaning validation'),indent=2)+'\n')
print('PASS')
