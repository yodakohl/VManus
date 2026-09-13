"""Independent slice-based bindings and graph-potential algebra verification."""
import csv,json,hashlib
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
D=Path(__file__).parent
spec=json.loads((D/'SPEC.json').read_text())
for p,h in spec['source_hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
model=json.loads(Path(spec['model']).read_text())
raw=list(csv.DictReader(Path(spec['source']).open(),delimiter='\t'))
fields=list(csv.DictReader((D/'FIELDS.tsv').open(),delimiter='\t'))
records=defaultdict(list)
for r in raw:records[r['paragraph']].append(r)
assert set(records)==set(spec['paragraphs']) and len(raw)==1045
expected=[]
for scope in spec['scopes']:
 for record,rows in records.items():
  for i,r in enumerate(rows):
   if r['form'] not in model['values']:continue
   left=rows[:i]
   if scope=='LINE':left=[x for x in left if x['locus']==r['locus']]
   ms=[x for x in left if x['form'] in model['materials']]
   m=ms[-1] if ms else None
   ds=[x for x in ms if x['form']!=m['form']] if m else []
   d=ds[-1] if ds else None
   since=left[left.index(m)+1:] if m else left
   qs=[x for x in since if x['form'] in model['qualities']]
   q=qs[-1] if qs else None
   e=dict(scope=scope,record=record,at=r['id'],word=r['form'],value=model['values'][r['form']],material=m['id'] if m else '',material_word=m['form'] if m else '',quality=q['id'] if q else '',quality_word=q['form'] if q else '',denominator=d['id'] if d else '',denominator_word=d['form'] if d else '',G_missing=','.join(k for k,b in [('material',not m),('quality',not q)] if b),M_missing='material' if not m else '',R_missing=','.join(k for k,b in [('material',not m),('denominator',not d)] if b),row_status='recorded')
   expected.append(e)
assert expected==fields
# Exact old input inclusion and old binding parity, not just total counts.
old=json.loads((D.parent/'P11/INPUT.json').read_text())
byline=defaultdict(list)
for r in raw:byline[r['locus']].append(r['form'])
for line in old['lines']:assert byline[line['locus']]==line['groups'],line['locus']
old_count=0
for scope in spec['scopes']:
 for oldrow in csv.DictReader((D.parent/'P14'/('FIELDS_'+scope+'.tsv')).open(),delimiter='\t'):
  new=next(x for x in fields if x['scope']==scope and x['at']==oldrow['at'])
  for k,v in oldrow.items():
   if k!='record':assert new[k]==v,(k,oldrow['at'])
  old_count+=1
# Each equation is reconstructed independently from verified fields.
algebra=json.loads((D/'ALGEBRA.json').read_text())
def rank(rows):
 a=[list(map(F,row)) for row in rows];p=0
 for c in range(3):
  k=next((j for j in range(p,len(a)) if a[j][c]),None)
  if k is None:continue
  a[p],a[k]=a[k],a[p];v=a[p][c];a[p]=[x/v for x in a[p]]
  for j in range(p+1,len(a)):
   v=a[j][c];a[j]=[x-v*y for x,y in zip(a[j],a[p])]
  p+=1
 return p
checks={}
for key,a in algebra.items():
 scope,mode=key.split('_');eq=[]
 for f in expected:
  if f['scope']!=scope or f[mode+'_missing']:continue
  x=f['record']+':'+f['material_word']
  y=f['record']+':'+(f['denominator_word'] if mode=='R' else 'UNIT_U')
  eq.append(dict(at=f['at'],terms={x:1,y:-1},value=f['value']))
 assert eq==a['equations']
 graph=defaultdict(list)
 for e in eq:
  x=next(n for n,v in e['terms'].items() if v==1);y=next(n for n,v in e['terms'].items() if v==-1)
  v=tuple(F(int(e['value']==c)) for c in 'ABC')
  graph[y].append((x,v));graph[x].append((y,tuple(-z for z in v)))
 potentials={};cycles=[]
 for start in graph:
  if start in potentials:continue
  potentials[start]=(F(0),)*3;stack=[start]
  while stack:
   x=stack.pop()
   for y,delta in graph[x]:
    want=tuple(a+b for a,b in zip(potentials[x],delta))
    if y not in potentials:potentials[y]=want;stack.append(y)
    else:cycles.append(tuple(a-b for a,b in zip(want,potentials[y])))
 basis=[[F(c['log_value_coefficients'][v]) for v in 'ABC'] for c in a['constraints']]
 assert rank(cycles)==rank(basis)==a['value_constraint_rank']
 assert rank(cycles+basis)==rank(cycles)
 byat={e['at']:e for e in eq}
 for c in a['constraints']:
  total=defaultdict(F);val=[F(0)]*3
  for at,k in c['witness'].items():
   e=byat[at];k=F(k)
   for n,v in e['terms'].items():total[n]+=k*v
   val['ABC'.index(e['value'])]-=k
  assert not any(total.values()) and val==[F(c['log_value_coefficients'][v]) for v in 'ABC']
 checks[key]=dict(equations=len(eq),graph_value_rank=rank(cycles),witnesses=len(basis))
readings=list(csv.DictReader((D/'READINGS.tsv').open(),delimiter='\t'))
for scope in spec['scopes']:
 assert [(r['at'],r['word']) for r in readings if r['scope']==scope]==[(r['id'],r['form']) for r in raw]
text=(D/'READING.md').read_text()
for locus,words in byline.items():assert locus+': `'+ ' '.join(words)+'`' in text
res=dict(status='PASS',bound_source_files=len(spec['source_hashes']),groups=len(raw),paragraphs=len(records),value_bindings=len(fields),old_field_parity=old_count,old_source_groups=sum(len(x['groups']) for x in old['lines']),graph_checks=checks,meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
