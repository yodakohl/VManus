from pathlib import Path
import collections,gzip,hashlib,itertools,json,random
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());I={u:i for i,u in enumerate(U)}
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,x):
 raw=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def sat(clauses,n):
 if () in clauses:return False
 graph=[[] for _ in range(2*n)];rev=[[] for _ in graph]
 def vertex(l):return 2*(abs(l)-1)+(l<0)
 for clause in clauses:
  a=vertex(clause[0]);b=vertex(clause[-1])
  for p,q in ((a^1,b),(b^1,a)):graph[p].append(q);rev[q].append(p)
 seen=set();order=[]
 def visit(v):
  seen.add(v)
  for w in graph[v]:
   if w not in seen:visit(w)
  order.append(v)
 for v in range(2*n):
  if v not in seen:visit(v)
 labels={}
 def label(v,c):
  labels[v]=c
  for w in rev[v]:
   if w not in labels:label(w,c)
 for v in reversed(order):
  if v not in labels:label(v,len(labels))
 return all(labels[2*i]!=labels[2*i+1] for i in range(n))
def least_model(clauses,n):
 if not sat(clauses,n):return None
 prefix=[];bits=[]
 for i in range(n):
  bit=0 if sat(clauses+prefix+[(-(i+1),)],n) else 1;bits.append(bit);prefix.append(((i+1) if bit else -(i+1),))
 return bits
def run_plan(n,px,py,left,right):
 dp={p:((0 if left is None else int(left!=p//2)),(p,)) for p in (px,py)}
 for _ in range(1,n):dp={p:min((cost+int(last%2!=p//2),seq+(p,)) for last,(cost,seq) in dp.items()) for p in (px,py)}
 return min((cost+(0 if right is None else int(last%2!=right)),seq) for last,(cost,seq) in dp.items())[1]
def render(word,pair,ports):
 x,y=pair;dp={None:(0,(),())}
 for u in word:
  choices=(x,y) if u in pair else (u,);nxt={}
  for g in choices:
   p=ports[I[g]];nxt[g]=min((cost+(0 if last is None else int(ports[I[last]]%2!=p//2)),seq+(p,),out+(g,)) for last,(cost,seq,out) in dp.items())
  dp=nxt
 return min(dp.values())[2]
def runs(words,pair):
 ans=set()
 for w in words:
  i=0
  while i<len(w):
   if w[i] not in pair:i+=1;continue
   j=i+1
   while j<len(w) and w[j] in pair:j+=1
   ans.add((w[i-1] if i else 'BOS',w[i:j],w[j] if j<len(w) else 'EOS'));i=j
 return sorted(ans)
def clauses_for(rs,pair,px,py):
 clauses=set();x,y=pair
 for u,p in ((x,px),(y,py)):
  for k,v in ((0,p//2),(1,p%2)):
   j=2*I[u]+k+1;clauses.add((j if v else -j,))
 cache={}
 for left,observed,right in rs:
  target=tuple(px if u==x else py for u in observed)
  for l in ([None] if left=='BOS' else [0,1]):
   for r in ([None] if right=='EOS' else [0,1]):
    key=(len(observed),l,r)
    if key not in cache:cache[key]=run_plan(len(observed),px,py,l,r)
    if cache[key]==target:continue
    clause=[]
    if l is not None:
     j=2*I[left]+2;clause.append(j if l==0 else -j)
    if r is not None:
     j=2*I[right]+1;clause.append(j if r==0 else -j)
    clauses.add(tuple(sorted(clause)))
 return sorted(clauses)
def fixtures():
 checks=0
 for px,py in itertools.permutations(range(4),2):
  for n in range(1,7):
   for left,right in itertools.product((None,0,1),repeat=2):
    possible=[]
    for seq in itertools.product((px,py),repeat=n):
     cost=sum(a%2!=b//2 for a,b in zip(seq,seq[1:]));cost+=0 if left is None else left!=seq[0]//2;cost+=0 if right is None else seq[-1]%2!=right;possible.append((cost,seq))
    assert run_plan(n,px,py,left,right)==min(possible)[1];checks+=1
 rng=random.Random(1334);cnfs=0
 for n in range(1,4):
  lit=list(range(1,n+1))+list(range(-n,0))
  for _ in range(300):
   clauses=[tuple(rng.choice(lit) for _ in range(rng.randrange(3))) for _ in range(rng.randrange(9))];valid=[bits for bits in itertools.product((0,1),repeat=n) if all(any(bool(bits[abs(l)-1])==(l>0) for l in c) for c in clauses)];assert sat(clauses,n)==bool(valid);assert least_model(clauses,n)==(list(min(valid)) if valid else None);cnfs+=1
 assert run_plan(2,0,3,1,1)==(3,3)
 # Both single replacements in the low/low run tie its cost and lose lexical preference.
 def cost(s):return sum(a%2!=b//2 for a,b in zip((3,)+s,s+(3,)))
 assert cost((0,0))==cost((3,0))==cost((0,3))==2 and cost((3,3))==0
 return {'status':'PASS','run_dp_vs_exhaustive_cases':checks,'small_cnf_bruteforce_cases':cnfs,'local_optimum_not_global':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 controls=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');out={};decisions={}
 for ed,rows in sorted(data.items()):
  contexts=collections.defaultdict(dict);byunit=collections.defaultdict(set);words=sorted({tuple(r['units']) for r in rows})
  for row in sorted(rows,key=lambda r:r['id']):
   w=row['units']
   for i,u in enumerate(w):
    ctx=(w[i-1] if i else 'BOS',w[i+1] if i+1<len(w) else 'EOS');contexts[u].setdefault(ctx,{'row':row,'index':i});byunit[u].add(row['id'])
  table=[]
  for pair in itertools.combinations(U,2):
   x,y=pair;common=sorted(set(contexts[x])&set(contexts[y]));record={'pair':list(pair),'x_groups':len(byunit[x]),'y_groups':len(byunit[y]),'union_groups':len(byunit[x]|byunit[y]),'intersection_groups':len(byunit[x]&byunit[y]),'minority_mass':[min(len(byunit[x]),len(byunit[y])),len(rows)]}
   if common:
    ctx=common[0];record.update(status='LOCAL_REPLACEMENT_CONTRADICTION',first_context=list(ctx),witnesses=[contexts[x][ctx],contexts[y][ctx]],port_cases=[])
   else:
    rs=runs(words,pair);cases=[]
    for px,py in itertools.permutations(range(4),2):
     clauses=clauses_for(rs,pair,px,py);bits=least_model(clauses,44);case={'pair_ports':[px,py],'clauses':[list(c) for c in clauses],'status':'PORT_UNSAT' if bits is None else 'CANONICAL_WRITER_EXISTS','bits':bits}
     if bits is not None:
      ports=[2*bits[2*i]+bits[2*i+1] for i in range(22)]
      for word in words:assert render(word,pair,ports)==word,(ed,pair,px,py,word)
      case['full_unique_words_checked']=len(words)
     cases.append(case)
    record.update(status='EXACT_PAIR_WRITER_EXISTS' if any(c['bits'] is not None for c in cases) else 'ALL_PORTS_UNSAT',port_cases=cases,distinct_alias_runs=len(rs))
   table.append(record)
  valid=[r for r in table if r['status']=='EXACT_PAIR_WRITER_EXISTS'];decisions[ed]=table;out[ed]={'groups':len(rows),'word_types':len(words),'pairs':len(table),'local_conflict_pairs':sum(r['status']=='LOCAL_REPLACEMENT_CONTRADICTION' for r in table),'all_ports_unsat_pairs':sum(r['status']=='ALL_PORTS_UNSAT' for r in table),'compatible_pairs':[r['pair'] for r in valid],'SAT_port_cases':sum(c['bits'] is not None for r in table for c in r['port_cases']),'status':'EXACT_PAIR_WRITER_WITNESSES' if valid else 'NONTRIVIAL_TWO_PORT_ALIAS_FAMILY_EXCLUDED'};print(ed,json.dumps(out[ed]),flush=True)
 save('PAIR_RESULTS.json.gz',decisions);save('RESULT.json',{'status':'EXACT_CANONICAL_PORT_CAPACITY','fixtures':controls,'readers':out})
if __name__=='__main__':main()
