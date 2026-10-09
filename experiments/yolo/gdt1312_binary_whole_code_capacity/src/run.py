import collections,csv,gzip,hashlib,itertools,json,subprocess,time
from fractions import Fraction
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2];CACHE=R/'.cache/gdt1312';A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split();READERS=['ZL3b','IT2a','RF1b'];SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def write_panel(path,alphabet,order,panels):
 maxlen=max(len(w['units']) for rows in panels for w in rows);assert 1<=maxlen<=20
 with path.open('w') as f:
  f.write(f'{alphabet} {len(panels)} {maxlen}\n'+' '.join(map(str,order))+'\n')
  for rows in panels:
   f.write(str(len(rows))+'\n')
   for w in rows:f.write(str(w['count'])+' '+str(len(w['units']))+' '+' '.join(map(str,w['units']))+'\n')
def cpp(source,name):
 p=CACHE/name;subprocess.run(['g++','-O3','-std=c++17',str(B/'src'/source),'-o',str(p)],check=True);return p

def fixtures(exe,checker):
 checks=0
 for n in range(2,7):
  words=[tuple((i*j+i+j)%n for j in range(length)) for length in range(1,6) for i in range(n+2)]
  words+=list(itertools.product(range(n),repeat=2));counts=collections.Counter(words);panel=[{'units':list(w),'count':c+1} for w,c in sorted(counts.items())]
  inp=CACHE/f'toy{n}.txt';out=CACHE/f'toy{n}.bin';write_panel(inp,n,list(range(1,n)),[panel]);subprocess.run([str(exe),str(inp),str(out)],check=True,capture_output=True);subprocess.run([str(checker),str(inp),str(out)],check=True,capture_output=True)
  got=np.frombuffer(out.read_bytes(),dtype='<u2')
  for idx,k in enumerate(got):
   mask=idx<<1;patterns={tuple((mask>>a)&1 for a in w) for w in counts};assert int(k)==len(patterns);checks+=1
 assert len({2,4,5})==3 # 0,00,01 have distinct sentinel representations.
 code={'P':'0','Q':'01','R':'10'};classes={'A':'0','B':'0','C':'1','D':'1'};written=['B','AD','CB'];inverse={v:k for k,v in code.items()};assert ''.join(inverse[''.join(classes[g] for g in w)] for w in written)=='PQR'
 return {'status':'PASS','direct_projection_assignments':checks,'toy_alphabets':[2,3,4,5,6],'leading_zero_and_length_preserved':True,'nonprefix_code_delimited_roundtrip':'PQR','native_meanings_assigned':0}

def witness(mask,rows):
 buckets={};occ=[0]*22
 for row in rows:
  u=row['units'];c=row['count'];bits=''.join(str((mask>>g)&1) for g in u);b=buckets.setdefault(bits,{'types':0,'tokens':0});b['types']+=1;b['tokens']+=c
  for g in u:occ[g]+=c
 one=sum(occ[g] for g in range(22) if mask>>g&1);total=sum(occ)
 return {'mask':int(mask),'class0':[s for i,s in enumerate(A) if not(mask>>i&1)],'class1':[s for i,s in enumerate(A) if mask>>i&1],'patterns':[{'bits':s,**buckets[s]} for s in sorted(buckets,key=lambda x:(len(x),x))],'K':len(buckets),'unit_occurrences':total,'bit1_occurrences':one,'minority_occurrences':min(one,total-one),'minority_share':str(Fraction(min(one,total-one),total))}

def summarize(panel,arrays):
 ids=np.arange(1<<21,dtype=np.uint32);results={};masses=[];totals=[];feasibles=[]
 for reader,rows,ks in zip(READERS,panel,arrays):
  weights=[sum(w['count']*w['units'].count(g) for w in rows) for g in range(22)];total=sum(weights);ones=np.zeros(len(ids),dtype=np.uint32)
  for j in range(21):ones+=((ids>>j)&1)*weights[j+1]
  minor=np.minimum(ones,total-ones);masses.append(minor);totals.append(total);feasible=ks<=32;feasible[0]=False;feasibles.append(feasible)
  mink=int(ks[1:].min());minidx=int(np.flatnonzero((ks==mink)&(ids>0))[0]);fi=np.flatnonzero(feasible);best=None
  if len(fi):
   maxmass=int(minor[fi].max());bi=int(fi[np.flatnonzero(minor[fi]==maxmass)[0]]);best=witness(bi<<1,rows)
  results[reader]={'source_types':len(rows),'source_tokens':sum(w['count'] for w in rows),'unit_occurrences':total,'partitions_tested':len(ids)-1,'minimum_K':mink,'minimum_witness':witness(minidx<<1,rows),'feasible_at_most32':len(fi),'most_balanced_feasible':best,'zero_mask_reference_K':int(ks[0])}
 common=np.logical_and.reduce(feasibles);ci=np.flatnonzero(common);bestidx=None;bestshare=Fraction(-1)
 for index in ci:
  index=int(index);share=min(Fraction(int(m[index]),t) for m,t in zip(masses,totals))
  if share>bestshare:bestshare=share;bestidx=index
 return {'status':'CAPACITY_FEASIBLE' if all(r['feasible_at_most32'] for r in results.values()) else 'READER_SPECIFIC_OR_NO_CAPACITY','readers':results,'common_partition_separate_codebooks':{'count':len(ci),'best_worst_share':str(bestshare) if bestidx is not None else None,'witnesses':{r:witness(bestidx<<1,rows) for r,rows in zip(READERS,panel)} if bestidx is not None else None},'claim_ceiling':'Exact finite bitword budget only; no plaintext, native partition, glyph-choice law or historical writer.'}

def main():
 CACHE.mkdir(parents=True,exist_ok=True)
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 exe=cpp('gray.cpp','primary');check=cpp('recurse.cpp','checker');fx=fixtures(exe,check);save('FIXTURES.json',fx)
 data=json.loads(gzip.decompress((R/SOURCE).read_bytes()));allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panel=[]
 for reader in READERS:
  counter=collections.Counter()
  for row in data[reader]:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert ''.join(row['units'])==row['ivtff_group_raw'];u=tuple(A.index(g) for g in row['units']);assert 1<=len(u)<=20;counter[u]+=1
  assert len(counter)<=65535;panel.append([{'units':list(w),'count':c} for w,c in sorted(counter.items())])
 order=sorted(range(1,22),key=lambda g:(sum(g in w['units'] for rows in panel for w in rows),A[g]));save('PANEL.json',{'alphabet':A,'readers':READERS,'runtime_order':order,'panels':panel})
 inp=B/'artifacts/PANEL.txt';write_panel(inp,22,order,panel);out=CACHE/'native_counts.bin';start=time.monotonic();subprocess.run([str(exe),str(inp),str(out)],check=True);elapsed=time.monotonic()-start
 raw=out.read_bytes();assert len(raw)==3*(1<<21)*2;arrays=np.frombuffer(raw,dtype='<u2').reshape(3,-1)
 for reader,a in zip(READERS,arrays):(B/f'artifacts/COUNTS_{reader}.u16.gz').write_bytes(gzip.compress(a.tobytes(),mtime=0))
 result=summarize(panel,arrays);save('RESULT.json',result);save('COUNT_FORMAT.json',{'dtype':'little-endian unsigned16','entries_per_reader':1<<21,'index':'original22unitmask>>1, unit0(a)fixed0','index0':'reference only; excluded from every selection','compression':'gzip mtime0'})
 print(json.dumps({'status':result['status'],'readers':{r:{'minimum_K':v['minimum_K'],'feasible':v['feasible_at_most32'],'best_share':v['most_balanced_feasible']['minority_share'] if v['most_balanced_feasible'] else None} for r,v in result['readers'].items()},'common':result['common_partition_separate_codebooks']['count'],'seconds':elapsed},indent=2))
if __name__=='__main__':main()
