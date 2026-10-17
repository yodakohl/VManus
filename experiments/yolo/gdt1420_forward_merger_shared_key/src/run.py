#!/usr/bin/env python3
"""Bounded exact shared forward letter-merger word-row search; no word meanings."""
import argparse,gzip,hashlib,itertools,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
 p=A/name
 if p.exists():assert read(p)==obj,name
 else:p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def setup():
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 return read(E/'src/SPEC.json')
def records(s):
 recipes=read(ROOT/s['recipe_path']);deot=read(ROOT/s['deot_path'])
 return {'b4':[r['words'] for r in recipes['b4']], 'w1':[r['words'] for r in recipes['w1']], 'deot':[r['words'] for r in deot['source_sections']]}
class Limit(Exception):pass

def solve(groups,rs,s,seconds,block=None):
 started=time.monotonic();nodes=0;checks=0
 words=sorted({w for r in rs for w in r});ids={w:i for i,w in enumerate(words)}
 alphabet=sorted(set(''.join(words)));ci={c:i for i,c in enumerate(alphabet)};units=s['signs'];ui={u:i for i,u in enumerate(units)}
 assert groups and all(g and all(u in ui for u in g) for g in groups)
 successors=[set() for _ in words];predecessors=[set() for _ in words]
 for r in rs:
  for a,b in zip(r,r[1:]):successors[ids[a]].add(ids[b]);predecessors[ids[b]].add(ids[a])
 rows=[];domains=[]
 def tick(count=1):
  nonlocal checks
  checks+=count
  if checks>s['checks_cap']:raise Limit('CHECK_CAP')
  if time.monotonic()-started>seconds:raise Limit('TIME_CAP')
 try:
  for g in groups:
   table={}
   for wid,w in enumerate(words):
    if len(w)!=len(g):continue
    tick();row={};valid=True
    for c,u in zip(w,g):
     a,b=ci[c],ui[u]
     if a in row and row[a]!=b:valid=False;break
     row[a]=b
    if valid:table[wid]=tuple(sorted(row.items()))
   rows.append(table);domains.append(frozenset(table))
  def propagate(d,k):
   d=list(d);k=list(k);changed=True
   while changed:
    tick(0);changed=False
    for i,dom in enumerate(d):
     allowed=set()
     for w in dom:
      tick()
      if all(k[c]<0 or k[c]==v for c,v in rows[i][w]):allowed.add(w)
     if not allowed:return None
     if allowed!=dom:d[i]=frozenset(allowed);changed=True
    for i in range(len(d)-1):
     left=frozenset(a for a in d[i] if successors[a]&d[i+1])
     if not left:return None
     right=frozenset(b for b in d[i+1] if predecessors[b]&left)
     if not right:return None
     if left!=d[i]:d[i]=left;changed=True
     if right!=d[i+1]:d[i+1]=right;changed=True
    for i,dom in enumerate(d):
     if len(dom)!=1:continue
     w=next(iter(dom))
     for c,v in rows[i][w]:
      if k[c]>=0 and k[c]!=v:return None
      if k[c]<0:k[c]=v;changed=True
   return tuple(d),tuple(k)
  def visit(d,k):
   nonlocal nodes
   tick(0)
   if nodes>=s['nodes_cap']:raise Limit('NODE_CAP')
   nodes+=1;p=propagate(d,k)
   if p is None:return None
   d,k=p
   if all(len(x)==1 for x in d):
    chosen=[words[next(iter(x))] for x in d]
    return None if chosen==block else (chosen,k)
   i=min((j for j,x in enumerate(d) if len(x)>1),key=lambda j:(len(d[j]),j))
   for word in sorted(d[i]):
    branch=list(d);branch[i]=frozenset([word]);answer=visit(tuple(branch),k)
    if answer is not None:return answer
   return None
  answer=visit(tuple(domains),tuple([-1]*len(alphabet)))
  if answer is None:return {'status':'UNSAT','reason':'EXHAUSTIVE_WORD_ROW_SEARCH','nodes':nodes,'checks':checks}
  chosen,key=answer;key={c:units[key[i]] if key[i]>=0 else units[0] for i,c in enumerate(alphabet)}
  assert [[key[c] for c in w] for w in chosen]==groups
  assert all(ids[b] in successors[ids[a]] for a,b in zip(chosen,chosen[1:])) and chosen!=block
  return {'status':'SAT','source_words':chosen,'key':key,'nodes':nodes,'checks':checks}
 except Limit as exc:return {'status':'UNKNOWN','reason':str(exc),'nodes':nodes,'checks':checks}

def controls():
 small={'signs':['X','Y'],'nodes_cap':10000,'checks_cap':1000000}
 fixtures=[[['a','b'],['b','a']],[['aa','ab'],['ba','bb']],[['a'],['b']],[['ab','ac']],[['a'],['bc']]]
 messages=[[[u]] for u in 'XY']+[[list(a),list(b)] for a in ['X','Y','XX','XY'] for b in ['X','Y','XX','YX']]
 count=0
 for rs in fixtures:
  W=sorted({w for r in rs for w in r});edges={e for r in rs for e in zip(r,r[1:])};chars=sorted(set(''.join(W)))
  for groups in messages:
   possible=[]
   for values in itertools.product('XY',repeat=len(chars)):
    key=dict(zip(chars,values))
    options=[[w for w in W if [key[c] for c in w]==g] for g in groups]
    possible.extend(ws for ws in itertools.product(*options) if all(e in edges for e in zip(ws,ws[1:])))
   result=solve(groups,rs,small,3)
   assert result['status']==('SAT' if possible else 'UNSAT'),(groups,rs,result)
   if result['status']=='SAT':
    assert tuple(result['source_words']) in possible
    second=solve(groups,rs,small,3,block=result['source_words'])
    assert second['status']==('SAT' if any(list(ws)!=result['source_words'] for ws in possible) else 'UNSAT')
   count+=1
 assert solve([['X','Y'],['Y','X']],[['ab','ac']],small,3)['status']=='UNSAT'
 assert solve([['X','X']],[['ab']],small,3)['status']=='SAT'
 assert solve([['X']],[['a']],dict(small,nodes_cap=0),3)['status']=='UNKNOWN'
 return {'status':'PASS','complete_function_and_path_cases':count,'message_blocking_checked':True,'merging_allowed':True,'global_conflict_rejected':True,'cap_unknown':True}

def gate(s):
 source_free=controls();rs=records(s)['deot'];alphabet=sorted(set(''.join(w for r in rs for w in r)))
 index=next((i for i,r in enumerate(rs) if len(r)>=s['control_words']),None)
 if len(alphabet)!=22 or index is None:
  save('CONTROL.json',{'status':'DOMAIN_ABSENT','reason':'ALPHABET_OR_CONTIGUOUS_SECTION','source_free_controls':source_free});return
 words=rs[index][:s['control_words']];active=set(''.join(words));pairs=[[alphabet[0],alphabet[20]],[alphabet[1],alphabet[21]]]
 key={c:s['signs'][j%20] for j,c in enumerate(alphabet)};groups=[[key[c] for c in w] for w in words]
 packet={'source_section_index':index,'source_words':words,'planted_key':key,'encoded_groups':groups,'active_collision_pairs':pairs,'source_free_controls':source_free,'lock_sha256':sha(E/'LOCK.json')}
 if any(not set(pair)<=active for pair in pairs):packet.update(status='DOMAIN_ABSENT',reason='TWO_ACTIVE_COLLISIONS_REQUIRED');save('CONTROL.json',packet);return
 result=solve(groups,rs,s,s['primary_seconds']);packet['result']=result;packet['second_message']=None
 if result['status']=='SAT':
  if result['source_words']!=words:packet['status']='AMBIGUOUS'
  else:
   assert all(result['key'][c]==key[c] for c in active)
   second=solve(groups,rs,s,s['primary_seconds'],block=words);packet['second_message']=second
   packet['status']='PASS_EXACT_UNIQUE' if second['status']=='UNSAT' else ('AMBIGUOUS' if second['status']=='SAT' else 'UNKNOWN')
 else:packet['status']='UNKNOWN' if result['status']=='UNKNOWN' else 'INVALID_PLANTED_CONTROL_UNSAT'
 save('CONTROL.json',packet);print(json.dumps({'control_status':packet['status'],'nodes':result['nodes'],'checks':result['checks']}))

def native(s):
 assert read(A/'GATE_VALIDATION.json')['status']=='PASS'
 assert read(A/'CONTROL.json')['status']==read(A/'INDEPENDENT_CONTROL.json')['status']=='PASS_EXACT_UNIQUE'
 packet=read(ROOT/s['native_path']);groups=packet['original_units'];assert len(groups)==77
 rs=records(s);cases=[]
 for name in s['native_sources']:
  result=solve(groups,rs[name],s,s['native_seconds']);second=None
  if result['status']=='SAT':second=solve(groups,rs[name],s,s['native_seconds'],block=result['source_words'])
  cases.append({'source':name,'result':result,'second_message':second});print(json.dumps({'source':name,'status':result['status'],'reason':result.get('reason'),'nodes':result['nodes'],'checks':result['checks']}),flush=True)
 save('RESULT.json',{'experiment_id':'GDT1420','status':'SHARED_FORWARD_MERGER_CAPACITY','groups':groups,'original_groups':packet['original_groups'],'cases':cases,'lock_sha256':sha(E/'LOCK.json'),'claim_ceiling':s['claim_ceiling']})

def main():
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--selftest',action='store_true');args=p.parse_args()
 if args.selftest:print(json.dumps(controls()));return
 s=setup()
 if args.gate:gate(s)
 elif args.native:native(s)
 else:p.error('choose gate or native')
if __name__=='__main__':main()
