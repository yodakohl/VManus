from pathlib import Path
from itertools import combinations
from collections import defaultdict
from functools import lru_cache
import gzip,hashlib,json,re,csv
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'experiments/yolo/gdt1368_fragment_window_nucleus_capacity'
def encoded(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
@lru_cache(None)
def partition(hits):
 n=len(hits)
 for left,right in [(0,0),(0,1),(1,0),(1,1)]:
  end=n-right;reachable=[False]*(n+1);reachable[left]=True
  for i in range(left+1,end+1):reachable[i]=(reachable[i-1] and hits[i-1]) or (i-left>=2 and reachable[i-2] and (hits[i-2] or hits[i-1]))
  if reachable[end]:
   blocks=[];i=end
   while i>left:
    length=1 if reachable[i-1] and hits[i-1] else 2;blocks.append([i-length,i]);i-=length
   return {'leading_external':left,'trailing_external':right,'blocks':blocks[::-1]}
 return None
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 old=json.loads(gzip.decompress((OLD/'artifacts/WINDOWS.json.gz').read_bytes()));prior=json.loads((OLD/'artifacts/RESULT.json').read_text())['panels'];allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={};runoutput={}
 for reader,windows in sorted(old.items()):
  unique={}
  for win in windows:
   for row in win['sources']:
    if row['id'] in unique:assert unique[row['id']]==row
    unique[row['id']]=row
  groups=defaultdict(dict)
  for row in unique.values():
   assert row['edition']==reader and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['kind']=='P';assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   raw=row['ivtff_group_raw'];units=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',raw);assert ''.join(units)==raw and units==row['units'];i=int(row['source_group_index']);assert row['id']==f"{reader}|{row['locus']}|G{i:03d}" and row['locus'].split('.')[0]==row['page'];g=groups[(row['page'],row['locus'])];assert i not in g;g[i]=row
  runs=[]
  for key,g in sorted(groups.items()):
   current=[];prev=None
   for i in sorted(g):
    if prev is not None and i!=prev+1:
     assert len(current)>=3;runs.append({'sources':current});current=[]
    current.append(g[i]);prev=i
   assert len(current)>=3;runs.append({'sources':current})
  replay=[{'sources':r['sources'][i:i+3],'support':sorted({c for row in r['sources'][i:i+3] for c in row['ivtff_group_raw']})} for r in runs for i in range(len(r['sources'])-2)];assert replay==windows
  alphabet=prior[reader]['alphabet'];assert prior[reader]['tau_or_null']==4;bit={c:1<<i for i,c in enumerate(alphabet)};wm=sorted({sum(bit[c] for c in w['support']) for w in windows});rm=[[sum(bit[c] for c in set(row['ivtff_group_raw'])) for row in r['sources']] for r in runs]
  byk={};best=None;canonical=None
  for k in [4,5]:
   candidates=[]
   for chars in combinations(alphabet,k):
    mask=sum(bit[c] for c in chars)
    if not all(mask&m for m in wm):continue
    fail=next((i for i,r in enumerate(rm) if partition(tuple(bool(m&mask) for m in r)) is None),None);candidates.append({'set':list(chars),'first_failed_run':fail})
    if fail is None and best is None:best=k;canonical=list(chars)
   byk[str(k)]={'window_survivors':len(candidates),'partition_survivors':sum(c['first_failed_run'] is None for c in candidates),'candidates':candidates}
  upper=None
  if canonical is not None:
   mask=sum(bit[c] for c in canonical);upper=[partition(tuple(bool(m&mask) for m in r)) for r in rm];assert all(p is not None for p in upper)
  panels[reader]={'runs':len(runs),'groups':len(unique),'windows':len(windows),'alphabet':alphabet,'by_k':byk,'minimum_or_null':best,'canonical_hitset':canonical,'canonical_partitions':upper};runoutput[reader]=runs
  print(reader,len(runs),len(unique),best,canonical,{k:(v['window_survivors'],v['partition_survivors']) for k,v in byk.items()})
 (B/'artifacts/RESULT.json').write_bytes(encoded({'status':'OPEN_EDGE_FRAGMENT_PARTITION','panels':panels}));(B/'artifacts/RUNS.json.gz').write_bytes(gzip.compress(encoded(runoutput),mtime=0))
if __name__=='__main__':main()
