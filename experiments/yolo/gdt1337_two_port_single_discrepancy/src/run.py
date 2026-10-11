from pathlib import Path
import collections,gzip,hashlib,importlib.util,itertools,json,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1];R=B.parents[2]
OLD=R/'experiments/yolo/gdt1334_canonical_two_port_alias_capacity/src/run.py'
spec=importlib.util.spec_from_file_location('frozen1334',OLD);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
U=old.U;I=old.I

def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,x):
 raw=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def core_of(clauses):
 if () in clauses:return [()]
 adj=collections.defaultdict(list)
 for c in clauses:
  a,b=c[0],c[-1];adj[-a].append((b,c));adj[-b].append((a,c))
 def path(a,b):
  seen={a:None};q=collections.deque([a])
  while q and b not in seen:
   u=q.popleft()
   for v,c in adj[u]:
    if v not in seen:seen[v]=(u,c);q.append(v)
  if b not in seen:return None
  out=[];v=b
  while v!=a:u,c=seen[v];out.append(c);v=u
  return out
 for i in range(1,45):
  p=path(i,-i)
  if p is not None:
   q=path(-i,i)
   if q is not None:
    core=sorted(set(p+q));assert not old.sat(core,44);return core
 raise AssertionError('UNSAT core absent')
def fixed(pair,px,py):
 return set(old.clauses_for([],pair,px,py))
def supported(rs,pair,px,py):
 mandatory=fixed(pair,px,py);supp=collections.defaultdict(set)
 for run,words in rs.items():
  for c in old.clauses_for([run],pair,px,py):
   if c not in mandatory:supp[c].update(words)
 return mandatory,dict(supp)
def check_toys():
 assert not old.sat(core_of([(1,),(-1,2),(-2,)]),44)
 assert core_of([()])==[()]
 support={(1,):{'a','b'},(-1,):{'c'}}
 assert [c for c,s in support.items() if s!={'a'}]==[(1,),(-1,)]
 assert [c for c,s in support.items() if s!={'c'}]==[(1,)]
 return {'shared_clause_support':True,'empty_and_implication_core':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 toys=check_toys();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');tables={};summary={}
 for ed,rows in sorted(data.items()):
  byword=collections.defaultdict(list);contexts={u:collections.defaultdict(set) for u in U};byunit={u:set() for u in U}
  for r in rows:
   w=tuple(r['units']);byword[w].append(r)
   for i,u in enumerate(w):contexts[u][(w[i-1] if i else 'BOS',w[i+1] if i+1<len(w) else 'EOS')].add(w);byunit[u].add(r['id'])
  words=sorted(byword);hap={w for w in words if len(byword[w])==1};table=[];witnesses=[]
  for pair in itertools.combinations(U,2):
   x,y=pair;common=sorted(set(contexts[x])&set(contexts[y]));candidates=None;steps=[]
   for ctx in common:
    possible=set()
    for side in pair:
     ss=contexts[side][ctx]
     if len(ss)==1:
      w=next(iter(ss))
      if w in hap:possible.add(w)
    candidates=possible if candidates is None else candidates&possible
    steps.append({'context':list(ctx),'removable_words':[''.join(w) for w in sorted(possible)]})
    if not candidates:break
   rec={'pair':list(pair),'shared_contexts':len(common),'context_steps':steps,'context_candidates':None if candidates is None else [''.join(w) for w in sorted(candidates)],'port_cases':[]}
   if candidates==set():rec['status']='NO_SINGLE_DISCREPANCY_CONTEXT';table.append(rec);continue
   rs=collections.defaultdict(set)
   for w in words:
    for run in old.runs([w],pair):rs[run].add(w)
   for px,py in itertools.permutations(range(4),2):
    mandatory,support=supported(rs,pair,px,py);clauses=sorted(mandatory|set(support));assert not old.sat(clauses,44)
    core=[]
    if candidates is None:
     core=core_of(clauses);eligible=set()
     for c in core:
      if c not in mandatory and len(support[c])==1:
       w=next(iter(support[c]))
       if w in hap:eligible.add(w)
    else:eligible=set(candidates)
    case={'pair_ports':[px,py],'unsat_core':[list(c) for c in core],'candidate_words':[''.join(w) for w in sorted(eligible)],'checks':[]}
    for w in sorted(eligible):
     nx=len(byunit[x])-int(x in w);ny=len(byunit[y])-int(y in w);test={'removed_word':''.join(w),'accepted_x_groups':nx,'accepted_y_groups':ny}
     if not nx or not ny:test.update(status='INACTIVE_ALIAS_MEMBER',bits=None);case['checks'].append(test);continue
     remaining=sorted(mandatory|{c for c,ss in support.items() if ss!={w}});bits=old.least_model(remaining,44);test.update(status='UNSAT' if bits is None else 'ONE_DISCREPANCY_WRITER',bits=bits)
     if bits is not None:
      ports=[2*bits[2*i]+bits[2*i+1] for i in range(22)];bad=[v for v in words if old.render(v,pair,ports)!=v];assert bad==[w] and len(byword[w])==1;accepted=[r for r in rows if tuple(r['units'])!=w];gx=[r for r in accepted if x in r['units']];gy=[r for r in accepted if y in r['units']];assert len(gx)==nx and len(gy)==ny
      witness={'pair':list(pair),'pair_ports':[px,py],'bits':bits,'residual':byword[w][0],'canonical_residual':' '.join(old.render(w,pair,ports)),'accepted_x_groups':nx,'accepted_y_groups':ny,'accepted_union':len({r['id'] for r in gx}|{r['id'] for r in gy}),'accepted_intersection':len({r['id'] for r in gx}&{r['id'] for r in gy}),'x_pages':sorted({r['page'] for r in gx}),'y_pages':sorted({r['page'] for r in gy}),'minority_mass':[min(nx,ny),len(rows)],'full_word_types_checked':len(words)};witnesses.append(witness)
     case['checks'].append(test)
    rec['port_cases'].append(case)
   rec['status']='ONE_DISCREPANCY_PAIR_WITNESSES' if any(c['status']=='ONE_DISCREPANCY_WRITER' for p in rec['port_cases'] for c in p['checks']) else 'NO_SINGLE_DISCREPANCY_RUN';table.append(rec)
  maximum=max((w['minority_mass'][0] for w in witnesses),default=None)
  summary[ed]={'groups':len(rows),'types':len(words),'pairs':len(table),'context_excluded_pairs':sum(t['status']=='NO_SINGLE_DISCREPANCY_CONTEXT' for t in table),'port_branches':sum(len(t['port_cases']) for t in table),'candidate_checks':sum(len(p['checks']) for t in table for p in t['port_cases']),'SAT_witnesses':len(witnesses),'compatible_pairs':[t['pair'] for t in table if t['status']=='ONE_DISCREPANCY_PAIR_WITNESSES'],'residual_types':sorted({w['residual']['ivtff_group_raw'] for w in witnesses}),'maximum_single_pair_minority_mass':None if maximum is None else [maximum,len(rows)],'status':'EXACT_USED_ALIAS_RADIUS_ONE' if witnesses else 'USED_ALIAS_RADIUS_AT_LEAST_TWO'}
  tables[ed]={'pairs':table,'witnesses':witnesses};print(ed,json.dumps(summary[ed]),flush=True)
 save('DECISIONS.json.gz',tables);save('RESULT.json',{'status':'COMPLETE_ONE_DISCREPANCY_CLASSIFICATION','readers':summary,'fixtures':toys,'scope':'Fixed word-local port model; no error diagnosis, physical alias binding, joint-pair model or meaning.'})
if __name__=='__main__':main()
