from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
PRIOR='experiments/yolo/gdt1361_nasal_assimilation_capacity/artifacts/RESULT.json'
SAMPLES=['daldy','qokeedy','qokedy','daiin','keeees']
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def fib(n):
 a,b=0,1
 for _ in range(n):a,b=b,a+b
 return a
def count(w,n,t):
 ans=1;i=0
 while i<len(w):
  if w[i]!=t:i+=1;continue
  j=i+1
  while j<len(w) and w[j]==t:j+=1
  r=j-i;preceded=i>0 and w[i-1]==n
  if preceded and r<2:return 0
  ans*=fib(r-1 if preceded else r+1);i=j
 return ans
def controls():
 total=0
 for length in range(9):
  words=list(itertools.product('NTX',repeat=length));image=Counter(tuple('T' if c=='N' and i+1<len(w) and w[i+1]=='T' else c for i,c in enumerate(w)) for w in words)
  for w in words:assert count(w,'N','T')==image[w]
  total+=len(words)
 assert count(tuple('NTT'),'N','T')==1
 assert count(tuple('TTTT'),'N','T')==5
 save(B/'artifacts/CONTROLS.json',{'status':'PASS','ternary_cases':total,'TTTT_preimages':5,'NTT_preimages':1})
def run():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));prior=json.loads((R/PRIOR).read_text())['readers'];allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};out={}
 for reader,rows in sorted(data.items()):
  counts=Counter();first={};units={}
  for row in rows:
   assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   form=row['ivtff_group_raw'];w=tuple(re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',form));assert ''.join(w)==form and list(w)==row['units'];counts[form]+=1;first.setdefault(form,row['id']);units[form]=w
  U=sorted({t for n,t in prior[reader]['active_survivors']});rigid=[f for f in sorted(counts) if not any(a==b and a in U for a,b in zip(units[f],units[f][1:]))];pairs=[];examples={f:{'count':counts[f],'first_id':first.get(f),'globally_rigid':f in rigid,'pair_counts':[]} for f in SAMPLES}
  for n,t in prior[reader]['survivors']:
   z={'N':n,'T':t,**{k+s:0 for k in ['unique_literal','unique_changed','ambiguous'] for s in ['_groups','_types']},'literal_preimage_groups':0,'max_preimages':0,'max_form':None,'max_first_id':None}
   for f in sorted(counts):
    w=units[f];c=count(w,n,t);assert c>0;hasNT=any(a==n and b==t for a,b in zip(w,w[1:]));hasTT=any(a==b==t for a,b in zip(w,w[1:]));kind='ambiguous' if c>1 else ('unique_changed' if hasNT else 'unique_literal');assert (kind=='unique_literal')==(not hasTT)
    z[kind+'_groups']+=counts[f];z[kind+'_types']+=1
    if not hasNT:z['literal_preimage_groups']+=counts[f]
    if c>z['max_preimages']:z.update(max_preimages=c,max_form=f,max_first_id=first[f])
    if f in examples:examples[f]['pair_counts'].append({'N':n,'T':t,'preimages':c})
   pairs.append(z)
  rigidforms=[{'form':f,'count':counts[f],'first_id':first[f]} for f in rigid];out[reader]={'groups':len(rows),'types':len(counts),'active_T':U,'pairs':pairs,'rigid_groups':sum(counts[f] for f in rigid),'rigid_types':len(rigid),'rigid_forms':rigidforms,'examples':examples}
  print(reader,'rigid',out[reader]['rigid_groups'],'/',len(rows),'types',len(rigid),'/',len(counts),flush=True)
 save(B/'artifacts/RESULT.json',{'status':'EXACT_INVERSE_ACCOUNTED','readers':out,'scope':'Conditional preimage cardinality and literal-substitution core only; no meanings, sound values, source likelihood or actual assimilation.'})
if __name__=='__main__':
 import sys
 controls() if '--controls' in sys.argv else run()
