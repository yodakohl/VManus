from pathlib import Path
from itertools import combinations
from collections import defaultdict
import csv,gzip,hashlib,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def encode(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={};allwindows={}
 for reader,rows in sorted(data.items()):
  grouped=defaultdict(dict)
  for row in rows:
   assert row['edition']==reader and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   w=row['ivtff_group_raw'];u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',w);assert ''.join(u)==w and u==row['units'];i=int(row['source_group_index']);assert row['id']==f"{reader}|{row['locus']}|G{i:03d}";assert row['locus'].split('.')[0]==row['page'];g=grouped[(row['page'],row['locus'])];assert i not in g;g[i]=row
  alphabet=sorted({c for row in rows for c in row['ivtff_group_raw']});assert len(alphabet)==18
  windows=[]
  for key,g in sorted(grouped.items()):
   for i in sorted(g):
    if i+1 in g and i+2 in g:
     sources=[g[j] for j in (i,i+1,i+2)];windows.append({'sources':sources,'support':sorted({c for row in sources for c in row['ivtff_group_raw']})})
  assert windows,'UNAPPLICABLE'
  bits={c:1<<i for i,c in enumerate(alphabet)};masks=[sum(bits[c] for c in w['support']) for w in windows];size=1<<len(alphabet);full=size-1;subtotal=[0]*size
  for m in masks:subtotal[m]+=1
  for bit in (1<<i for i in range(len(alphabet))):
   for start in range(0,size,bit*2):
    for mask in range(start+bit,start+bit*2):subtotal[mask]+=subtotal[mask-bit]
  tau=None;canonical=None;nsets=0
  for k in range(6):
   for chars in combinations(alphabet,k):
    mask=sum(bits[c] for c in chars)
    if subtotal[full^mask]==0:
     nsets+=1
     if canonical is None:canonical=list(chars)
   if nsets:tau=k;break
  lb=6 if tau is None else tau;cert=[]
  for chars in combinations(alphabet,5 if tau is None else tau-1):
   mask=sum(bits[c] for c in chars);miss=next(i for i,m in enumerate(masks) if not(m&mask));cert.append({'set':list(chars),'first_missed_window':miss})
  panels[reader]={'groups':len(rows),'windows':len(windows),'loci':len({(w['sources'][0]['page'],w['sources'][0]['locus']) for w in windows}),'leaves':len({int(re.match(r'f(\d+)',w['sources'][0]['page']).group(1)) for w in windows}),'alphabet':alphabet,'tau_or_null':tau,'lower_bound':lb,'minimum_sets':nsets,'canonical_hitset':canonical,'decision':'K5_EXCLUDED_BY_RETAINED_WINDOWS' if tau is None else 'K5_NOT_EXCLUDED_BY_RETAINED_WINDOWS','lower_certificate':cert};allwindows[reader]=windows
  print(reader,{k:v for k,v in panels[reader].items() if k not in ('lower_certificate','alphabet')})
 (B/'artifacts/RESULT.json').write_bytes(encode({'status':'FRAGMENT_WINDOW_NUCLEUS_CAPACITY','panels':panels}));(B/'artifacts/WINDOWS.json.gz').write_bytes(gzip.compress(encode(allwindows),mtime=0))
if __name__=='__main__':main()
