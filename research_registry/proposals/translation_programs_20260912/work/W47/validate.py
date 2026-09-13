import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path(__file__).parent;s=json.loads((D/'SPEC.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def rows(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allowed=set(read(s['allow_source'])['allowed_selectors']);occ=rows(D/'OCCURRENCES.tsv');ctx=read(D/'CONTEXTS.json');alllines={};expected=[];counts=Counter()
for src in s['sources']:
 d=read(src);cols=d['group_columns'];wi=cols.index('ivtff_group_raw');si=cols.index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84');ed=m['edition'];key=(ed,m['locus']);assert key not in alllines
  alllines[key]=(m,l['groups'],cols);counts[ed,'lines']+=1;counts[ed,'groups']+=len(l['groups'])
  for g in l['groups']:
   if g[wi]=='sheey':expected.append((ed,m['locus'],g[si]));counts[ed,'hits']+=1
assert sorted(expected)==sorted((r['edition'],r['locus'],r['source_id']) for r in occ)
assert {(x['metadata']['edition'],x['metadata']['locus']) for x in ctx['lines']}=={(e,l) for e,l,i in expected}
for x in ctx['lines']:
 m,gs,cols=alllines[x['metadata']['edition'],x['metadata']['locus']];assert x['metadata']==m and x['groups']==[dict(zip(cols,g)) for g in gs]
paras=read(s['paragraphs']);needed={(ed,p['id']) for ed,pp in paras.items() for p in pp if any((ed,l['locus']) in {(e,lo) for e,lo,i in expected} for l in p['lines'])}
assert {(p['edition'],p['id']) for p in ctx['paragraphs']}==needed
for p in ctx['paragraphs']:assert {k:v for k,v in p.items() if k!='edition'}==next(x for x in paras[p['edition']] if x['id']==p['id'])
mat=set(read(s['material_source'])['material_roles']);feat={x['form'] for x in read(s['feature_source'])['features'] if x['kind']=='STANDALONE'}
found=[]
for branch,p in s['roles'].items():
 role={r['form']:r['role'] for r in rows(p)}
 for (ed,loc),(m,gs,cols) in alllines.items():
  words=[g[cols.index('ivtff_group_raw')] for g in gs]
  for start in range(len(words)-2):
   a,b,c=words[start:start+3]
   if c not in feat or role.get(c)!='STATE':continue
   if (a=='sheey' and role.get(b) in mat) or (b=='sheey' and role.get(a) in mat):found.append((branch,ed,loc,start))
assert found==[] and rows(D/'PATTERNS.tsv')==[] and rows(D/'PREDICTIONS.tsv')==[]
r=read(D/'RESULT.json')
for ed,dd in r['counts'].items():
 for k,v in dd.items():assert v==counts[ed,k]
assert r['distinct_source_lines']==len({l for ed,l,i in expected}) and r['patterns']==0
cc=rows(D/'CANDIDATES.tsv');assert {r['candidate'] for r in cc}==set(read(s['candidate_source'])['candidates']) and all(r['decision']=='NO_ELIGIBLE_TEST' and r['other_exposed_cases']=='0' for r in cc)
out=dict(status='PASS',exact_reading_occurrences=len(expected),complete_paragraphs=len(needed),candidate_cases=5,eligible_patterns=0,source_groups=sum(v for (ed,k),v in counts.items() if k=='groups'),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
