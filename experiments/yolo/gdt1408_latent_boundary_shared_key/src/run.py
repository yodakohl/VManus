#!/usr/bin/env python3
"""Exact finite word-star/injective-key capacity with latent source boundaries."""
from pathlib import Path
import argparse,collections,concurrent.futures,functools,gzip,hashlib,itertools,json,time
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def pattern(u):
 d={};return tuple(d.setdefault(v,len(d)) for v in u)
def sources(s):
 a=read(R/s['recipe_path']);b=read(R/s['deot_path']);c=read(R/s['other_path']);out={}
 for n in s['source_names']:
  if n in ('b4','w1','bs1','gr1'):out[n]=sorted({w for rec in a[n] for w in rec['words']})
  elif n=='deot':out[n]=sorted({w for sec in b['source_sections'] for w in sec['words']})
  else:out[n]=sorted({x['unit'] for x in c[n]['PRIMARY']['units']});assert len(c[n]['PRIMARY']['units'])==8000
  assert out[n] and all(out[n])
 return out
class Limit(Exception):pass
def solve(stream,words,signs,s):
 start=time.monotonic();checks=0;nodes=0;N=len(stream);alphabet=sorted(set(''.join(words)));memo=set()
 def tick():
  nonlocal checks
  checks+=1
  if checks>s['candidate_checks_cap']:raise Limit('candidate_checks_cap')
  if checks%256==0 and time.monotonic()-start>s['seconds_per_case']:raise Limit('wall_seconds')
 def compatible(bind,key,rev):
  tick();return all((u not in key or key[u]==v) and (v not in rev or rev[v]==u) for u,v in bind)
 def output(status,**kw):return dict(status=status,nodes=nodes,checks=checks,**kw)
 try:
  if len(alphabet)<len(signs):return output('UNSAT',reason='global_injection_alphabet_capacity')
  by=collections.defaultdict(list)
  for w in words:by[(len(w),pattern(w))].append(w)
  lengths=sorted({len(w) for w in words},reverse=True);edges=[]
  for p in range(N):
   row=[]
   for L in lengths:
    if p+L>N:continue
    u=stream[p:p+L]
    for w in by[(L,pattern(u))]:
     tick();row.append((p+L,w,tuple(sorted(set(zip(u,w))))))
   edges.append(row)
  @functools.lru_cache(maxsize=64)
  def relaxed_suffix(keytuple):
   key={u:v for u,v in zip(signs,keytuple) if v is not None};rev={v:u for u,v in key.items()};can=bytearray(N+1);can[N]=1
   for p in range(N-1,-1,-1):
    for end,w,bind in edges[p]:
     if can[end] and compatible(bind,key,rev):can[p]=1;break
   return bytes(can)
  def visit(p,key,rev):
   nonlocal nodes
   nodes+=1
   if nodes>s['nodes_cap']:raise Limit('nodes_cap')
   if time.monotonic()-start>s['seconds_per_case']:raise Limit('wall_seconds')
   if p==N:return key,[]
   kt=tuple(key.get(u) for u in signs);state=(p,kt)
   if state in memo:return None
   if len(key)>=s['suffix_prune_min_bound_units'] and not relaxed_suffix(kt)[p]:memo.add(state);return None
   for end,w,bind in edges[p]:
    if not compatible(bind,key,rev):continue
    nk=dict(key);nr=dict(rev)
    for u,v in bind:nk[u]=v;nr[v]=u
    got=visit(end,nk,nr)
    if got is not None:
     k,path=got;return k,[{'start':p,'end':end,'source_word':w}]+path
   memo.add(state);return None
  got=visit(0,{}, {})
  if got is None:return output('UNSAT',reason='exhausted_exact_wordstar_and_key_search')
  key,path=got;active=dict(key);available=iter(v for v in alphabet if v not in set(key.values()))
  for u in signs:
   if u not in key:key[u]=next(available)
  decoded=''.join(key[u] for u in stream)
  assert decoded==''.join(x['source_word'] for x in path) and len(set(key.values()))==len(signs)
  return output('SAT',key=key,active_key=active,arbitrary_extension_units=[u for u in signs if u not in active],source_words=[x['source_word'] for x in path],segments=path,decoded_unspaced=decoded)
 except Limit as e:return output('UNKNOWN',reason=str(e))
def wordbreak(s,W):
 dp=[False]*(len(s)+1);dp[0]=True
 for p in range(len(s)):
  if dp[p]:
   for w in W:
    if s.startswith(w,p):dp[p+len(w)]=True
 return dp[-1]
def controls(s,ws):
 cfg=dict(s,nodes_cap=1000000,candidate_checks_cap=10000000,seconds_per_case=10,suffix_prune_min_bound_units=2);count=0;hist=collections.Counter();toyrows=[]
 toyW=[['x','yz'],['xy','xz'],['x','y','z'],['xx','y','z'],['xy','zx','yz']]
 for W in toyW:
  A=sorted(set(''.join(W)))
  for n in range(1,5):
   for t in itertools.product('abc',repeat=n):
    expected=any(wordbreak(''.join(dict(zip('abc',key))[u] for u in t),W) for key in itertools.permutations(A,3))
    got=solve(list(t),W,list('abc'),cfg);assert got['status']==('SAT' if expected else 'UNSAT'),(t,W,got)
    hist[got['status']]+=1;count+=1;toyrows.append({'stream':list(t),'words':W,'signs':list('abc'),'result':got,'expected_oracle_status':'SAT' if expected else 'UNSAT'})
 tiny=dict(cfg,nodes_cap=0);assert solve(list('abc'),['x','y','z'],list('abc'),tiny)['status']=='UNKNOWN'
 save('TOY_CONTROLS.json',{'cases':toyrows,'primary_algorithm_same_as_native':True})
 words=ws['deot'][:32];A=sorted(set(''.join(ws['deot'])));assert len(A)==len(s['signs'])==22
 key={u:A[(7*j+3)%22] for j,u in enumerate(s['signs'])};inv={v:k for k,v in key.items()};stream=[inv[c] for c in ''.join(words)]
 got=solve(stream,ws['deot'],s['signs'],s)
 control={'source_selection':'sorted distinct W words indices0..31','source':'deot','source_words':words,'planted_key':key,'encoded_stream':stream,'result':got,'success':'any verified SATkey and sourcewordsegmentation, not unique planted plaintext/key recovery'}
 save('GENERATED_CONTROL.json',control)
 status='PASS' if got['status']=='SAT' else 'STOP_GENERATED_CONTROL_NOT_RECOVERED'
 result={'status':status,'oracle_cases':count,'oracle_outcomes':dict(hist),'forced_cap_is_UNKNOWN':True,'generated_status':got['status'],'native_data_read':False,'key_and_wordbreak_identification':'capacityonly; wordbooksequence not semanticreading'}
 save('CONTROLS.json',result);return result
def native(s):
 x=read(R/s['worksheet_path']);source=x['source_original_wrapper']['source_unit'];rows=[];stream=[];ordered=sorted(s['signs'],key=lambda u:(-len(u),u))
 for line in source['lines']:
  for g in line['groups']:
   raw=g[2];pos=0;u=[]
   while pos<len(raw):
    candidates=[a for a in ordered if raw.startswith(a,pos)];assert candidates,(g[0],pos)
    a=candidates[0];u.append(a);pos+=len(a)
   rows.append({'original_group':g,'units':u,'start':len(stream),'end':len(stream)+len(u)});stream+=u
 assert len(rows)==77 and ''.join(stream)==''.join(g['original_group'][2] for g in rows)
 packet={'original_source':source,'groups':rows,'forward_stream':stream,'group_count':77,'raw_runs_preserved':True,'native_word_meanings':'UNASSIGNED'};save('NATIVE_INPUT.json',packet);return stream
def onecase(task):
 name,direction,stream,W,signs,s=task
 if direction=='REVERSE':stream=stream[::-1]
 return {'source':name,'direction':direction,'source_word_types':len(W),'stream_units':len(stream),'result':solve(stream,W,signs,s)}
def verifylock():
 lock=read(B/'LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args();verifylock();s=read(B/'src/SPEC.json');ws=sources(s)
 if args.controls:print(json.dumps(controls(s,ws)));raise SystemExit
 assert not(B/'artifacts/RESULT.json').exists();gate=read(B/'artifacts/CONTROLS.json');assert gate['status']=='PASS' and gate['generated_status']=='SAT'
 independent_gate=read(B/'artifacts/GATE_VALIDATION.json');assert independent_gate['status']=='PASS'
 stream=native(s);tasks=[(n,d,stream,ws[n],s['signs'],s) for n in s['source_names'] for d in s['directions']]
 with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:cases=list(pool.map(onecase,tasks))
 result={'experiment_id':'GDT1408','status':'COMPLETE_BOUNDED_WORDSTAR_SHARED_KEY_SCREEN','cases':cases,'claim_ceiling':s['claim_ceiling'],'source_meanings_assigned':0};save('RESULT.json',result);print(json.dumps([(c['source'],c['direction'],c['result']['status'],c['result'].get('reason')) for c in cases]))
