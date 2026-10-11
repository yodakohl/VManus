from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,re
import z3
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());I={u:i for i,u in enumerate(U)}
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def canonical(options,ports,left=None,right=None):
 n=len(options);tail=[{} for _ in range(n+1)]
 for v in (0,1):tail[n][v]=0 if right is None else int(v!=right)
 for i in range(n-1,-1,-1):
  for prev in (0,1):tail[i][prev]=min(int(prev!=ports[g]//2)+tail[i+1][ports[g]%2] for g in options[i])
 remain=tail[0][left] if left is not None else min(tail[1][ports[g]%2] for g in options[0]);out=[];prev=left
 for i,choices in enumerate(options):
  for g in sorted(choices,key=lambda g:ports[g]):
   edge=0 if prev is None else int(prev!=ports[g]//2)
   if edge+tail[i+1][ports[g]%2]==remain:out.append(g);remain-=edge;prev=ports[g]%2;break
  else:raise AssertionError('no canonical continuation')
 return tuple(out)
def derive_clauses(words,pair,px,py):
 x,y=pair;clauses=set();runtypes=set();cache={}
 for g,p in ((x,px),(y,py)):
  for k,v in enumerate((p//2,p%2)):
   j=2*g+k+1;clauses.add((j if v else -j,))
 for word in words:
  positions=[i for i,g in enumerate(word) if g in pair]
  for _,indices in itertools.groupby(enumerate(positions),key=lambda v:v[1]-v[0]):
   indices=[v for _,v in indices];a,b=indices[0],indices[-1]+1;left=word[a-1] if a else None;right=word[b] if b<len(word) else None;obs=word[a:b];runtypes.add((left,obs,right))
 for left,obs,right in runtypes:
  for lv,rv in itertools.product((None,) if left is None else (0,1),(None,) if right is None else (0,1)):
   k=(len(obs),lv,rv)
   if k not in cache:cache[k]=canonical([pair]*len(obs),{x:px,y:py},lv,rv)
   if cache[k]==obs:continue
   terms=[]
   for neighbor,side,value in ((left,1,lv),(right,0,rv)):
    if neighbor is not None:
     v=2*neighbor+side+1;terms.append(v if value==0 else -v)
   clauses.add(tuple(sorted(terms)))
 return sorted(clauses),len(runtypes)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');saved=read(B/'artifacts/PAIR_RESULTS.json.gz');res=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};pattern=re.compile('|'.join(sorted(U,key=lambda s:(-len(s),s))));joins=0;portcases=0;fullchecks=0;literalpairs=0;satcases=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set()
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert pattern.findall(g[2])==r['units'];assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1
  assert seen==set(byid);words=sorted({tuple(I[u] for u in r['units']) for r in rows});contexts=collections.defaultdict(list)
  for r in rows:
   w=r['units']
   for i,u in enumerate(w):contexts[u].append(((w[i-1] if i else 'BOS',w[i+1] if i+1<len(w) else 'EOS'),r['id'],i))
  assert len(saved[ed])==231;compatible=[];conflicts=0;unsatpairs=0;nsat=0
  for record,pair in zip(saved[ed],itertools.combinations(U,2)):
   x,y=pair;assert record['pair']==list(pair);gx={r['id'] for r in rows if x in r['units']};gy={r['id'] for r in rows if y in r['units']}
   for k,v in {'x_groups':len(gx),'y_groups':len(gy),'union_groups':len(gx|gy),'intersection_groups':len(gx&gy),'minority_mass':[min(len(gx),len(gy)),len(rows)]}.items():assert record[k]==v
   cx={c for c,_,_ in contexts[x]};cy={c for c,_,_ in contexts[y]};common=sorted(cx&cy)
   if common:
    assert record['status']=='LOCAL_REPLACEMENT_CONTRADICTION' and record['first_context']==list(common[0]) and record['port_cases']==[];expected=[]
    for u in pair:
     _,rid,i=min(t for t in contexts[u] if t[0]==common[0]);expected.append({'row':byid[rid],'index':i})
    assert record['witnesses']==expected;conflicts+=1;literalpairs+=1;continue
   pi=tuple(I[u] for u in pair);assert len(record['port_cases'])==12;anysat=False
   for case,(px,py) in zip(record['port_cases'],itertools.permutations(range(4),2)):
    assert case['pair_ports']==[px,py];clauses,nruns=derive_clauses(words,pi,px,py);assert [list(c) for c in clauses]==case['clauses'];assert nruns==record['distinct_alias_runs'];vs=[z3.Bool('v'+str(i)) for i in range(44)];solver=z3.Solver();solver.set(timeout=10000)
    for clause in clauses:solver.add(z3.Or([vs[abs(l)-1] if l>0 else z3.Not(vs[abs(l)-1]) for l in clause]))
    decision=solver.check();assert decision in (z3.sat,z3.unsat);bits=case['bits'];assert (decision==z3.sat)==(bits is not None);assert case['status']==('CANONICAL_WRITER_EXISTS' if bits is not None else 'PORT_UNSAT');portcases+=1
    if bits is not None:
     assert len(bits)==44 and all(v in (0,1) for v in bits);assert all(any(bool(bits[abs(l)-1])==(l>0) for l in c) for c in clauses)
     for i,bit in enumerate(bits):
      if bit:
       solver.push();solver.add(z3.Not(vs[i]));assert solver.check()==z3.unsat;solver.pop()
      solver.add(vs[i] if bit else z3.Not(vs[i]))
     ports=[2*bits[2*i]+bits[2*i+1] for i in range(22)];assert ports[pi[0]]==px and ports[pi[1]]==py
     for w in words:
      opts=[pi if u in pi else (u,) for u in w];assert canonical(opts,ports)==w;fullchecks+=1
     assert case['full_unique_words_checked']==len(words);anysat=True;nsat+=1;satcases+=1
   assert record['status']==('EXACT_PAIR_WRITER_EXISTS' if anysat else 'ALL_PORTS_UNSAT')
   if anysat:compatible.append(list(pair))
   else:unsatpairs+=1
  expected={'groups':len(rows),'word_types':len(words),'pairs':231,'local_conflict_pairs':conflicts,'all_ports_unsat_pairs':unsatpairs,'compatible_pairs':compatible,'SAT_port_cases':nsat,'status':'EXACT_PAIR_WRITER_WITNESSES' if compatible else 'NONTRIVIAL_TWO_PORT_ALIAS_FAMILY_EXCLUDED'};assert expected==res['readers'][ed];print(ed,'validated',flush=True)
 assert res['fixtures']=={'status':'PASS','run_dp_vs_exhaustive_cases':648,'small_cnf_bruteforce_cases':900,'local_optimum_not_global':True}
 controls=0
 for px,py in itertools.permutations(range(4),2):
  for n in range(1,6):
   for left,right in itertools.product((None,0,1),repeat=2):
    candidates=[]
    for w in itertools.product((0,1),repeat=n):
     ports={0:px,1:py};cost=sum(ports[a]%2!=ports[b]//2 for a,b in zip(w,w[1:]));cost+=0 if left is None else left!=ports[w[0]]//2;cost+=0 if right is None else ports[w[-1]]%2!=right;candidates.append((cost,tuple(ports[u] for u in w),w))
    assert canonical([(0,1)]*n,{0:px,1:py},left,right)==min(candidates)[2];controls+=1
 out={'status':'PASS','source_joins':joins,'literal_pair_contradictions':literalpairs,'independent_Z3_port_decisions':portcases,'SAT_port_models':satcases,'full_word_canonical_checks':fullchecks,'independent_exhaustive_run_controls':controls,'method':'Original915joins/rawparse; per-pair context intersection; backward run/wholewordDP; independently derived2CNF checked with Z3 vs primary SCC including lexleast models.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
