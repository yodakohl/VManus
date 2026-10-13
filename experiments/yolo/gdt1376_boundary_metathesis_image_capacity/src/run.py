from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
ALPHABET=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def swap(words,a,b):
 out=[list(w) for w in words]
 for i in range(len(words)-1):
  if words[i][-1]==a and words[i+1][0]==b:out[i][-1]=b;out[i+1][0]=a
 return out
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};result={};allruns={}
 for rd,rows in sorted(data.items()):
  groups=defaultdict(dict)
  for row in rows:
   assert row['edition']==rd and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   u=row['units'];raw=row['ivtff_group_raw'];assert re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',raw)==u and ''.join(u)==raw and set(u)<=set(ALPHABET);i=int(row['source_group_index']);assert row['id']==f"{rd}|{row['locus']}|G{i:03d}";g=groups[(row['page'],row['locus'])];assert i not in g;g[i]=row
  runs=[]
  for key,g in sorted(groups.items()):
   current=[];prev=None
   for i in sorted(g):
    if prev is not None and i!=prev+1:runs.append({'sources':current});current=[]
    current.append(g[i]);prev=i
   if current:runs.append({'sources':current})
  counts=Counter();non=Counter();bad=Counter();leaves=defaultdict(set);first={};boundaries=0;wordruns=[]
  for ri,run in enumerate(runs):
   words=[r['units'] for r in run['sources']];wordruns.append(words);leaf=int(re.match(r'f(\d+)',run['sources'][0]['page']).group(1))
   for i,(left,right) in enumerate(zip(words,words[1:])):
    boundaries+=1;a,b=left[-1],right[0]
    if a==b:continue
    key=(a,b);counts[key]+=1
    if len(left)>=2 and len(right)>=2:non[key]+=1
    left_rescue=len(left)==1 and (i==0 or words[i-1][-1]==b);right_rescue=len(right)==1 and (i+2==len(words) or words[i+2][0]==a)
    if not(left_rescue or right_rescue):
     bad[key]+=1;leaves[key].add(leaf);first.setdefault(key,{'run_index':ri,'boundary_index':i})
  keys=[]
  for a in ALPHABET:
   for b in ALPHABET:
    if a==b:continue
    key=(a,b);digest=None
    if not bad[key]:
     h=hashlib.sha256()
     for words in wordruns:
      padded=[[b,b]]+words+[[a,a]];pre=swap(padded,b,a);assert swap(pre,a,b)==padded
      h.update((json.dumps(pre[1:-1],ensure_ascii=False,separators=(',',':'))+'\n').encode())
     digest=h.hexdigest()
    keys.append({'A':a,'B':b,'ab_count':counts[key],'nonsingleton_ab':non[key],'unsupported_ab':bad[key],'unsupported_leaves':len(leaves[key]),'first_unsupported':first.get(key),'ba_opportunities':counts[b,a],'status':'EXCLUDED' if bad[key] else 'LOCAL_IMAGE_CAPACITY','canonical_preimage_sha256':digest})
  survivors=[z for z in keys if z['status']=='LOCAL_IMAGE_CAPACITY'];result[rd]={'groups':len(rows),'runs':len(runs),'boundaries':boundaries,'keys':keys,'excluded_keys':len(keys)-len(survivors),'surviving_keys':len(survivors),'survivors_with_ba':sum(z['ba_opportunities']>0 for z in survivors),'survivors_requiring_change':sum(z['ab_count']>0 for z in survivors)};allruns[rd]=runs
  print(rd,{k:v for k,v in result[rd].items() if k!='keys'},flush=True)
 save('RUNS.json.gz',allruns);save('RESULT.json',{'status':'BOUNDARY_METATHESIS_IMAGE_CAPACITY','readers':result})
if __name__=='__main__':main()
