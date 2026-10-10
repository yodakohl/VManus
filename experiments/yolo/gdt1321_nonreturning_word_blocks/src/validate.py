import collections,csv,gzip,hashlib,itertools,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def closure(words,alphabet):
 n=len(alphabet);ix={g:i for i,g in enumerate(alphabet)};rel=[[i==j for j in range(n)] for i in range(n)];ww=[[ix[g] for g in w] for w in words]
 while True:
  old=[r[:] for r in rel]
  for w in ww:
   for i in range(len(w)):
    for j in range(i+2,len(w)):
     if rel[w[i]][w[j]]:
      for k in range(i+1,j):rel[w[i]][w[k]]=rel[w[k]][w[i]]=True
  for k in range(n):
   for i in range(n):
    if rel[i][k]:
     for j in range(n):rel[i][j]=rel[i][j] or rel[k][j]
  if old==rel:break
 return sorted({tuple(alphabet[j] for j in range(n) if rel[i][j]) for i in range(n)})
def valid(words,labels):
 for w in words:
  runs=[]
  for g in w:
   if not runs or runs[-1]!=labels[g]:runs.append(labels[g])
  if len(runs)!=len(set(runs)):return False
 return True
def fixtures():
 alphabet=['a','b','c'];partitions=[]
 for labels in itertools.product(range(3),repeat=3):
  if labels[0]==0 and all(labels[i]<=1+max(labels[:i]) for i in range(1,3)):partitions.append(dict(zip(alphabet,labels)))
 words=[w for n in range(1,4) for w in itertools.product(alphabet,repeat=n)];count=0
 for i,a in enumerate(words):
  for b in words[i:]:
   ww=[a,b];cs=closure(ww,alphabet);ok=[p for p in partitions if valid(ww,p)];assert len(cs)==max(len(set(p.values())) for p in ok)
   for component in cs:
    for x,y in itertools.product(component,repeat=2):assert all(p[x]==p[y] for p in ok)
   assert valid(ww,{g:i for i,c in enumerate(cs) for g in c});count+=1
 assert closure(['ab','ba'],['a','b'])==[('a',),('b',)];assert closure(['aba'],['a','b'])==[('a','b')];assert not valid(['abc'],{'a':0,'b':1,'c':0})
 return count

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 fx=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=steps=0
 for ed,rows in data.items():
  byid={row['id']:row for row in rows};found=set()
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     row=byid[g[0]];assert row['page']==m['page'] and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['locus']==m['locus'] and row['kind']==m['kind']=='P' and m['edition']==ed;assert g[2]==row['ivtff_group_raw']==''.join(row['units']);assert int(g[1])==int(row['source_group_index']);assert g[3]==g[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert g[0] not in found;found.add(g[0]);joins+=1
  assert len(found)==len(rows);types={tuple(row['units']) for row in rows};leaves={u:set() for u in types}
  for row in rows:leaves[tuple(row['units'])].add(int(re.match(r'f(\d+)',row['page'])[1]))
  for name in ['FULL','PHYSICAL_LEAVES_GE2']:
   panel=[r for r in rows if name=='FULL' or len(leaves[tuple(r['units'])])>=2];alphabet=sorted({g for r in panel for g in r['units']});words=[list(u) for u in sorted({tuple(r['units']) for r in panel})];cs=closure(words,alphabet);r=result['panels'][ed+'_'+name];assert [list(c) for c in cs]==r['classes'];labels={g:i for i,c in enumerate(cs) for g in c};assert valid(words,labels);assert len(cs)==r['maximum_classes'];assert r['active_units']==alphabet and r['groups']==len(panel) and r['types']==len(words);assert sum(len({labels[g] for g in x['units']})>1 for x in panel)==r['multiblock_groups'];assert r['status']==('ONE_CLASS_ONLY' if len(cs)==1 else 'MULTICLASS_CAPACITY')
   components=[{g} for g in alphabet];ids={x['id'] for x in panel}
   for proof in r['certificate']:
    witness=proof['witness'];assert witness['id'] in ids and witness==byid[witness['id']];w=witness['units'];i,j,k=[proof[x] for x in ['i','j','k']];assert 0<=i<k<j<len(w);left=next(c for c in components if w[i] in c);right=next(c for c in components if w[k] in c);assert w[j] in left and left!=right;assert proof['merged_classes']==[sorted(left),sorted(right)];components.remove(left);components.remove(right);components.append(left|right);steps+=1
   assert sorted(tuple(sorted(c)) for c in components)==cs
 assert joins==result['source_joins'];receipt={'status':'PASS','source_joins':joins,'panels':6,'forced_merge_steps':steps,'exhaustive_toy_panels':fx,'scope':'Exact block capacity and provenance; no native field, glyph identity or meaning identification.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
