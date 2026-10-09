import collections,csv,gzip,hashlib,json,subprocess
from fractions import Fraction
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2];CACHE=R/'.cache/gdt1312'
A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split();READERS=['ZL3b','IT2a','RF1b']
def read(p):return json.loads(p.read_text())
def segment(raw):
 dp=[[] for _ in range(len(raw)+1)];dp[0]=[()]
 for i in range(len(raw)):
  for pre in dp[i]:
   for j,s in enumerate(A):
    if raw.startswith(s,i):dp[i+len(s)].append(pre+(j,))
 assert len(dp[-1])==1,raw
 return dp[-1][0]
def reconstruct_witness(mask,rows):
 bins=collections.defaultdict(lambda:[0,0]);total=one=0
 for row in rows:
  bits=[]
  for g in row['units']:
   value=bool(mask&(1<<g));bits.append('1' if value else '0');total+=row['count'];one+=row['count']*value
  s=''.join(bits);bins[s][0]+=1;bins[s][1]+=row['count']
 return {'mask':mask,'class0':[A[g] for g in range(22) if not mask&(1<<g)],'class1':[A[g] for g in range(22) if mask&(1<<g)],'patterns':[{'bits':s,'types':bins[s][0],'tokens':bins[s][1]} for s in sorted(bins,key=lambda s:(len(s),s))],'K':len(bins),'unit_occurrences':total,'bit1_occurrences':one,'minority_occurrences':min(one,total-one),'minority_share':str(Fraction(min(one,total-one),total))}
def main():
 CACHE.mkdir(parents=True,exist_ok=True)
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels=[];parsed={};groups=0
 for reader in READERS:
  freq=collections.Counter()
  for row in data[reader]:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   raw=row['ivtff_group_raw']
   if raw not in parsed:parsed[raw]=segment(raw)
   u=parsed[raw];assert [A[i] for i in u]==row['units'] and 1<=len(u)<=20;freq[u]+=1;groups+=1
  panels.append([{'units':list(w),'count':c} for w,c in sorted(freq.items())])
 incidence=[sum(i in set(w['units']) for rows in panels for w in rows) for i in range(22)];order=sorted(range(1,22),key=lambda i:(incidence[i],A[i]));assert read(B/'artifacts/PANEL.json')=={'alphabet':A,'readers':READERS,'runtime_order':order,'panels':panels}
 M=max(len(w['units']) for rows in panels for w in rows);lines=[f'22 3 {M}',' '.join(map(str,order))]
 for rows in panels:
  lines.append(str(len(rows)))
  lines.extend(f"{w['count']} {len(w['units'])} "+' '.join(map(str,w['units'])) for w in rows)
 encoded=('\n'.join(lines)+'\n').encode();assert encoded==(B/'artifacts/PANEL.txt').read_bytes();inp=CACHE/'verify_panel.txt';inp.write_bytes(encoded)
 bodies=[gzip.decompress((B/f'artifacts/COUNTS_{reader}.u16.gz').read_bytes()) for reader in READERS];assert all(len(b)==2*(1<<21) for b in bodies);output=CACHE/'verify_counts.bin';output.write_bytes(b''.join(bodies))
 exe=CACHE/'independent_check';subprocess.run(['g++','-O3','-std=c++17',str(B/'src/recurse.cpp'),'-o',str(exe)],check=True);subprocess.run([str(exe),str(inp),str(output)],check=True)
 arrays=[np.frombuffer(b,dtype='<u2') for b in bodies];result=read(B/'artifacts/RESULT.json');indices=np.arange(1<<21,dtype=np.uint32);minorities=[];totals=[];valids=[]
 for reader,rows,ks in zip(READERS,panels,arrays):
  expected=result['readers'][reader];weights=[sum(w['count'] for w in rows for g in w['units'] if g==i) for i in range(22)];total=sum(weights);totals.append(total)
  # Two independent subset-sum tables, rather than the primary per-bit vector loop.
  low=np.array([sum(weights[j+1] for j in range(10) if mask>>j&1) for mask in range(1<<10)],dtype=np.uint32)
  high=np.array([sum(weights[j+11] for j in range(11) if mask>>j&1) for mask in range(1<<11)],dtype=np.uint32)
  ones=low[indices&1023]+high[indices>>10];minor=np.minimum(ones,total-ones);minorities.append(minor);valid=(ks<=32)&(indices!=0);valids.append(valid);ids=np.flatnonzero(valid)
  m=int(min(ks[1:]));mi=int(np.flatnonzero((ks==m)&(indices!=0))[0]);assert reconstruct_witness(mi*2,rows)==expected['minimum_witness'];assert expected['minimum_K']==m
  assert expected['source_types']==len(rows) and expected['source_tokens']==sum(w['count'] for w in rows) and expected['unit_occurrences']==total and expected['partitions_tested']==(1<<21)-1 and expected['feasible_at_most32']==len(ids)
  assert expected['zero_mask_reference_K']==len({len(w['units']) for w in rows})==int(ks[0])
  if len(ids):
   maxn=int(max(minor[ids]));best=int(min(ids[minor[ids]==maxn]));assert reconstruct_witness(best*2,rows)==expected['most_balanced_feasible']
  else:assert expected['most_balanced_feasible'] is None
 common=np.logical_and.reduce(valids);ci=np.flatnonzero(common);actual=result['common_partition_separate_codebooks'];assert actual['count']==len(ci);candidates=[]
 if len(ci):
  # Split by which reader realizes the minimum ratio, then maximize an integer
  # numerator in that region; cross-products and Fraction resolve exact ties.
  for r in range(3):
   relevant=np.ones(len(ci),dtype=bool)
   for s in range(3):relevant&=minorities[r][ci].astype(np.uint64)*totals[s]<=minorities[s][ci].astype(np.uint64)*totals[r]
   js=ci[relevant]
   if len(js):
    mx=int(minorities[r][js].max());ix=int(js[np.flatnonzero(minorities[r][js]==mx)[0]]);candidates.append((Fraction(mx,totals[r]),ix))
  bestshare=max(x[0] for x in candidates);bestidx=min(x[1] for x in candidates if x[0]==bestshare);assert actual['best_worst_share']==str(bestshare)
  for reader,rows in zip(READERS,panels):assert actual['witnesses'][reader]==reconstruct_witness(bestidx*2,rows)
 else:assert actual['best_worst_share'] is None and actual['witnesses'] is None
 status='CAPACITY_FEASIBLE' if all(v['feasible_at_most32'] for v in result['readers'].values()) else 'READER_SPECIFIC_OR_NO_CAPACITY';assert result['status']==status
 out={'status':'PASS','source_groups':groups,'distinct_raw_forms_reparsed':len(parsed),'nontrivial_partitions_per_reader':(1<<21)-1,'all_count_entries_checked':3*(1<<21),'method':'separate recursive type-multiplicity traversal with rollback, every saved Kchecked; independent raw parse, subset-sum activity and exact rational witness checks','ceiling':'Finite capacity and arithmetic only; no source-language key, native meaning or independent manuscript confirmation.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
