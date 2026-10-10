import collections,csv,gzip,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def save(n,o):(B/'artifacts'/n).write_text(json.dumps(o,indent=2)+'\n')
def solve(rows,alphabet):
 p={g:g for g in alphabet}
 def find(g):
  while p[g]!=g:g=p[g]
  return g
 proof=[]
 while True:
  changed=False
  for row in rows:
   w=row['units']
   for i in range(len(w)):
    for j in range(i+2,len(w)):
     if find(w[i])!=find(w[j]):continue
     for k in range(i+1,j):
      x,y=find(w[i]),find(w[k])
      if x!=y:
       proof.append({'witness':row,'i':i,'j':j,'k':k,'merged_classes':[sorted(g for g in alphabet if find(g)==x),sorted(g for g in alphabet if find(g)==y)]});p[max(x,y)]=min(x,y);changed=True
  if not changed:break
 groups=collections.defaultdict(list)
 for g in sorted(alphabet):groups[find(g)].append(g)
 classes=sorted(groups.values());labels={g:i for i,gs in enumerate(classes) for g in gs};multi=0
 for row in rows:
  w=[labels[g] for g in row['units']];runs=[v for i,v in enumerate(w) if i==0 or w[i-1]!=v];assert len(runs)==len(set(runs));multi+=len(runs)>1
 return {'classes':classes,'maximum_classes':len(classes),'multiblock_groups':multi,'certificate':proof}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={};joins=0
 for ed,rows in data.items():
  source={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    for g in line['groups']:source[g[0]]=(line['metadata'],g)
  leaves=collections.defaultdict(set)
  for row in rows:
   m,g=source[row['id']];assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert m['page']==row['page'] and m['locus']==row['locus'] and m['edition']==ed and m['kind']==row['kind']=='P';assert row['ivtff_group_raw']==g[2]==''.join(row['units']);assert int(g[1])==int(row['source_group_index']);assert row['left_separator']==row['right_separator']==g[3]==g[4]=='DEFINITE_SPACE';assert set(row['units'])<=set(A);joins+=1;leaves[tuple(row['units'])].add(int(re.match(r'f(\d+)',row['page'])[1]))
  for name,panel in [('FULL',rows),('PHYSICAL_LEAVES_GE2',[row for row in rows if len(leaves[tuple(row['units'])])>=2])]:
   active=sorted({g for row in panel for g in row['units']});r=solve(panel,active);r.update(groups=len(panel),types=len({tuple(row['units']) for row in panel}),active_units=active,status='ONE_CLASS_ONLY' if r['maximum_classes']==1 else 'MULTICLASS_CAPACITY');results[ed+'_'+name]=r;print(ed,name,'classes',r['classes'],'multi',r['multiblock_groups'],flush=True)
 save('RESULT.json',{'status':'NONRETURNING_BLOCK_CAPACITY','source_joins':joins,'panels':results})
if __name__=='__main__':main()
