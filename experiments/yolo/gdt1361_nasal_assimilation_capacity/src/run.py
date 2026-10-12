from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def write(w,pairs):
 d=dict(pairs)
 return tuple(d[c] if i+1<len(w) and c in d and w[i+1]==d[c] else c for i,c in enumerate(w))
def legal(w,pairs):
 return all(i+2<len(w) and w[i+2]==t for n,t in pairs for i in range(len(w)-1) if w[i:i+2]==(n,t))
def inverse(w,pairs):
 x=list(w)
 for n,t in pairs:
  for i in range(len(w)-1):
   if w[i:i+2]==(n,t):x[i+1]=n
 return tuple(x)
def controls():
 out=[]
 for alphabet,pairs,limit in [('NTX',[('N','T')],8),('NTMSX',[('N','T'),('M','S')],6)]:
  count=0
  for length in range(limit+1):
   words=list(itertools.product(alphabet,repeat=length));image={write(w,pairs) for w in words};accepted={w for w in words if legal(w,pairs)};assert image==accepted
   for w in accepted:assert write(inverse(w,pairs),pairs)==w
   count+=len(words)
  out.append({'alphabet':alphabet,'pairs':pairs,'max_length':limit,'source_cases':count})
 assert write(tuple('NNT'),[('N','T')])==tuple('NTT')
 save(B/'artifacts/CONTROLS.json',{'status':'PASS','cases':out})
def run():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};result={}
 for reader,rows in sorted(data.items()):
  alphabet=sorted({u for row in rows for u in row['units']});assert len(alphabet)==22
  for row in rows:
   assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
   assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   assert row['units']==re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw']) and ''.join(row['units'])==row['ivtff_group_raw']
  pairs=[];events=Counter();leaves={};bad_counts=Counter();firsts={}
  for row in rows:
   w=tuple(row['units']);leaf=int(re.match(r'f(\d+)',row['page']).group(1));bad_here=set()
   for i in range(len(w)-1):
    pair=w[i:i+2];events[pair]+=1;leaves.setdefault(pair,set()).add(leaf)
    if pair[0]!=pair[1] and (i+2==len(w) or w[i+2]!=pair[1]):
     bad_here.add(pair)
     firsts.setdefault(pair,{'source':row,'offset_zero_based':i})
   bad_counts.update(bad_here)
  for n,t in itertools.permutations(alphabet,2):
   pairs.append({'N':n,'T':t,'violating_groups':bad_counts[n,t],'NT_events':events[n,t],'TT_events':events[t,t],'NT_leaves':len(leaves.get((n,t),set())),'TT_leaves':len(leaves.get((t,t),set())),'first_violation':firsts.get((n,t))})
  survivors=[p for p in pairs if p['violating_groups']==0];active=[p for p in survivors if p['TT_events']];rec=[p for p in active if p['TT_leaves']>=2]
  result[reader]={'groups':len(rows),'pairs':pairs,'survivors':[[p['N'],p['T']] for p in survivors],'active_survivors':[[p['N'],p['T']] for p in active],'recurrent_TT_survivors':[[p['N'],p['T']] for p in rec],'active_with_visible_NT':[[p['N'],p['T']] for p in active if p['NT_events']]}
  print(reader,'survivors',len(survivors),'active',len(active),'recurrentTT',len(rec),flush=True)
 save(B/'artifacts/RESULT.json',{'status':'PAIR_CAPACITY_ENUMERATED','readers':result,'scope':'Conditional simultaneous writer output capacity only; no native sound, source word, actual assimilation or statistical model fit.'})
if __name__=='__main__':
 import sys
 if '--controls' in sys.argv:controls()
 else:run()
