"""Bounded exact reader for the fixed IDEA361 contract."""
import argparse, collections, concurrent.futures, csv, gzip, hashlib, json, re, time
from pathlib import Path
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
SPEC=json.loads((E/'src/SPEC.json').read_text())
def dump(name,obj):
 data=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode()
 (E/'artifacts'/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def prefix_free(key):
 vals=[x for x in key if x is not None]
 return all(not a.startswith(b) and not b.startswith(a) for i,a in enumerate(vals) for b in vals[i+1:])
def replay(words,w,model):
 key=w['key'];groups=w['groups'];state=0;seq=[]
 if len(key)!=6 or not prefix_free(key) or len(words)!=len(groups):return False
 if any(v is not None and not re.fullmatch('[a-z]{1,3}',v) for v in key):return False
 for word,atoms in zip(words,groups):
  if not 1<=len(atoms)<=3:return False
  if any(not isinstance(a,int) or not 0<=a<6 or key[a] is None for a in atoms):return False
  if ''.join(key[a] for a in atoms)!=word:return False
  for a in atoms:
   state=SPEC['models'][model][a][state]
   if state<0:return False
   seq.append(a)
 return bool(seq) and len(seq)<=24 and 0 in seq and seq[-1]==3 and state==0 and w['has_p']==(1 in seq)
def source_cases():
 allowed=set(json.loads((R/SPEC['allow']).read_text())['allowed_selectors'])
 data=json.loads((R/SPEC['source']).read_text());cases=[]
 for reading,paras in data.items():
  for p in paras:
   assert p['page'] in allowed and not p['page'].startswith('f84') and p['page']!='f116v'
   words=[w for line in p['lines'] for w in line['words']]
   ids=[s for line in p['lines'] for s in line['source_ids']]
   assert len(words)==len(ids)==p['groups']
   unknown=any(not line['anchor_eligible'] and not (len(line['words'])==1 and re.fullmatch('[a-z]+',line['words'][0])) for line in p['lines'])
   reasons=[]
   if unknown:reasons=['source_not_fully_literal_with_certain_inner_boundaries']
   else:
    if len(words)>24:reasons.append('more_than_24_groups')
    if sum(map(len,words))>72:reasons.append('more_than_72_characters')
    if any(len(w)>9 for w in words):reasons.append('group_longer_than_9')
    if len({w[0] for w in words})>6:reasons.append('more_than_6_initial_characters')
    if len({w[-1] for w in words})>6:reasons.append('more_than_6_final_characters')
   status='SOURCE_UNKNOWN' if unknown else 'CAPACITY_CONTRADICTION' if reasons else 'PENDING'
   for model in SPEC['models']:
    cases.append(dict(reading=reading,id=p['id'],page=p['page'],leaf=p['leaf'],model=model,words=words,source_ids=ids,status=status,reasons=reasons,nodes=0,witnesses=[]))
 return cases,{ed:len(ps) for ed,ps in data.items()}
class Limit(Exception):pass
def solve(case):
 started=time.monotonic();words=case['words'];transitions=SPEC['models'][case['model']]
 key=[None]*6;groups=[];current=[];found={};nodes=0;stopped=None
 def visit(i,pos,k,state,n,last,seen_l,seen_p):
  nonlocal nodes
  nodes+=1
  if nodes>SPEC['max_nodes']:raise Limit('node_cap')
  if nodes%128==0 and time.monotonic()-started>SPEC['case_seconds']:raise Limit('wall_cap')
  if i==len(words):
   if n and state==0 and last==3 and seen_l:
    kt=tuple(key)
    if kt not in found:
     found[kt]=dict(key=list(key),groups=[list(g) for g in groups],has_p=seen_p)
     if len(found)>=SPEC['max_witnesses']:raise Limit('witness_cap')
   return
  if pos==len(words[i]):
   if k:
    old=current[:];groups.append(old);current.clear()
    visit(i+1,0,0,state,n,last,seen_l,seen_p)
    current.extend(old);groups.pop()
   return
  if n>=24 or k>=3 or n+len(words)-i>24:return
  tail=words[i][pos:]
  for atom in range(6):
   ns=transitions[atom][state]
   if ns<0:continue
   old=key[atom]
   choices=[old] if old is not None else [tail[:m] for m in range(1,min(3,len(tail))+1)]
   for value in choices:
    if not tail.startswith(value):continue
    if old is None:
     key[atom]=value
     if not prefix_free(key):key[atom]=None;continue
    current.append(atom)
    visit(i,pos+len(value),k+1,ns,n+1,atom,seen_l or atom==0,seen_p or atom==1)
    current.pop();key[atom]=old
 try:visit(0,0,0,0,0,None,False,False)
 except Limit as e:stopped=str(e)
 ws=[found[k] for k in sorted(found,key=lambda k:tuple(v or '' for v in k))]
 for w in ws:assert replay(words,w,case['model'])
 case.update(nodes=nodes,witnesses=ws,status='UNKNOWN' if stopped else 'SAT_COMPLETE' if ws else 'EXHAUSTED',reasons=[stopped] if stopped else [],seconds=time.monotonic()-started)
 return case
def merge(a,b):
 if any(x is not None and y is not None and x!=y for x,y in zip(a,b)):return None
 z=[x if x is not None else y for x,y in zip(a,b)]
 return z if prefix_free(z) else None
def complete_key(key):
 out=list(key)
 for i,value in enumerate(out):
  if value is None:
   used={x[0] for x in out if x is not None}
   out[i]=next(c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in used)
 assert prefix_free(out)
 return out
def joint(cases,deadline=None):
 pairs=[];coverage={}
 for reading in ['ZL3b','IT2a','RF1b']:
  for model in SPEC['models']:
   subset=[c for c in cases if c['reading']==reading and c['model']==model]
   yes=[(c,i,w) for c in subset for i,w in enumerate(c['witnesses']) if w['has_p']]
   no=[(c,i,w) for c in subset for i,w in enumerate(c['witnesses']) if not w['has_p']]
   comparisons=0;hits=0;total=len(yes)*len(no);wall_capped=False
   for a,wi,wa in yes:
    for b,wj,wb in no:
     if comparisons>=SPEC['max_pair_comparisons']:break
     if deadline is not None and comparisons%4096==0 and time.monotonic()>=deadline:wall_capped=True;break
     comparisons+=1
     if a['leaf']==b['leaf']:continue
     key=merge(wa['key'],wb['key'])
     if key is not None:
      pairs.append(dict(reading=reading,model=model,a=a['id'],b=b['id'],wi=wi,wj=wj,key=key,completed_key=complete_key(key)));hits+=1
    if wall_capped or comparisons>=SPEC['max_pair_comparisons']:break
   coverage[reading+'/'+model]=dict(p_paragraph_witnesses=len(yes),no_p_paragraph_witnesses=len(no),total_saved_witness_pairs=total,comparisons=comparisons,joint_witness_pairs=hits,wall_capped=wall_capped,status='NO_PARAGRAPH_CAPACITY' if not subset else 'UNKNOWN_PAIR_CAP' if comparisons<total else 'COMPLETE_SAVED_WITNESSES',case_enumeration_complete=all(c['status']!='UNKNOWN' for c in subset))
 return pairs,coverage
def controls():
 key=list('abcdef')
 def witness(groups):return dict(key=key,groups=groups,has_p=any(1 in g for g in groups))
 fixtures=[('no_permission',['ae','cd'],[[0,4],[2,3]],'M',True),('permission',['ae','bf','cd'],[[0,4],[1,5],[2,3]],'M',True),('canceling_identity',['ae','bf','cd'],[[0,4],[1,5],[2,3]],'D',False),('undefined',['b','d'],[[1],[3]],'M',False),('cross_space',['a','e','c','d'],[[0,4],[2,3]],'M',False),('group_limit',['aecd'],[[0,4,2,3]],'M',False),('atom_limit',['d']*22+['a','c','d'],[[3]]*22+[[0],[2],[3]],'M',False)]
 out=[]
 for name,words,gs,model,want in fixtures:
  actual=replay(words,witness(gs),model);assert actual==want
  out.append(dict(name=name,expected=want,observed=actual))
 assert not prefix_free(['a','ab',None,None,None,None]);out.append(dict(name='prefix_collision',expected=False,observed=False))
 tiny=solve(dict(words=['ae','cd'],model='M'))
 assert tiny['status']=='SAT_COMPLETE' and any(w['key'][0]=='a' and w['key'][2]=='c' and w['key'][3]=='d' and w['key'][4]=='e' for w in tiny['witnesses'])
 impossible=solve(dict(words=['a'],model='M'))
 long_group=solve(dict(words=['abcdefghijkl'],model='M'))
 assert impossible['status']==long_group['status']=='EXHAUSTED'
 dump('CONTROL_RESULTS.json',dict(status='PASS',controls=out,enumeration_fixture_status=tiny['status'],single_atom_contradiction=impossible['status'],group_capacity_contradiction=long_group['status']))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args()
 if args.controls:controls();return
 for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 started=time.monotonic();cases,den=source_cases();pending=[i for i,c in enumerate(cases) if c['status']=='PENDING']
 with concurrent.futures.ProcessPoolExecutor(max_workers=SPEC['workers']) as pool:
  futures={pool.submit(solve,cases[i]):i for i in pending}
  try:
   for f in concurrent.futures.as_completed(futures,timeout=max(0.001,SPEC['execution_seconds']-(time.monotonic()-started))):cases[futures[f]]=f.result()
  except concurrent.futures.TimeoutError:
   for f,i in futures.items():
    if f.done():cases[i]=f.result()
    else:f.cancel();cases[i].update(status='UNKNOWN',reasons=['whole_run_cap'])
   for process in pool._processes.values():process.terminate()
 pairs,coverage=joint(cases,started+SPEC['execution_seconds']);panels={}
 for ed in ['ZL3b','IT2a','RF1b']:
  for model in SPEC['models']:
   subset=[c for c in cases if c['reading']==ed and c['model']==model]
   panels[ed+'/'+model]=dict(cases=len(subset),statuses=dict(collections.Counter(c['status'] for c in subset)),witnesses=sum(len(c['witnesses']) for c in subset))
 unresolved=any(c['status']=='UNKNOWN' for c in cases) or any(v['status']=='UNKNOWN_PAIR_CAP' for v in coverage.values())
 result=dict(status='HYPOTHETICAL_JOINT_FITS_FOUND' if pairs else 'BOUNDED_SEARCH_UNRESOLVED' if unresolved else 'NO_LITERAL_JOINT_FIT_SOURCE_UNCERTAINTY_RETAINED',source_denominators=den,panels=panels,pair_coverage=coverage,joint_witness_pairs=len(pairs),confirmed_words=0,independent_confirmation_leaves=0,reserve_access=False,elapsed_seconds=time.monotonic()-started)
 dump('CASES.json.gz',cases);dump('PAIRS.json.gz',pairs);dump('RESULT.json',result)
 with (E/'artifacts/CASE_TABLE.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['reading','paragraph','leaf','model','groups','characters','status','reasons','nodes','witnesses'])
  for c in cases:w.writerow([c['reading'],c['id'],c['leaf'],c['model'],len(c['words']),sum(map(len,c['words'])),c['status'],';'.join(c['reasons']),c['nodes'],len(c['witnesses'])])
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
