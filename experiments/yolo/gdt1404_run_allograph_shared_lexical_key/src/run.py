#!/usr/bin/env python3
"""Finite shared injective-key lexical capacity; no meanings assigned."""
import argparse,collections,gzip,hashlib,itertools,json,re,time
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def collapse(u):return [x for j,x in enumerate(u) if not(j and x in ('e','i') and x==u[j-1])]
def pattern(u):
 d={};return tuple(d.setdefault(x,len(d)) for x in u)
def sources(s):
 a=read(R/s['recipe_path']);b=read(R/s['deot_path']);c=read(R/s['other_path']);out={}
 for n in s['source_names']:
  if n in ('b4','w1','bs1','gr1'):out[n]=[w for rec in a[n] for w in rec['words']]
  elif n=='deot':out[n]=[w for sec in b['source_sections'] for w in sec['words']]
  else:out[n]=[x['unit'] for x in c[n]['PRIMARY']['units']];assert len(out[n])==8000
 return out
class Limit(Exception):pass
def solve(groups,words,signs,mode,s):
 start=time.monotonic();checks=0;nodes=0;trace=[];W=sorted(set(words));alphabet=sorted(set(''.join(W)));unique=sorted({tuple(g) for g in groups});tables={}
 def tick():
  nonlocal checks
  checks+=1
  if checks>s['candidate_checks_cap']:raise Limit('candidate_checks')
  if time.monotonic()-start>s['seconds_per_case']:raise Limit('wall_seconds')
 def compatible(row,key,rev):
  tick();return all((u not in key or key[u]==a) and (a not in rev or rev[a]==u) for u,a in row)
 try:
  if len(alphabet)<len(signs):return {'status':'UNSAT','reason':'full_alphabet_injection_impossible','checks':0,'nodes':0,'trace':[]}
  by=collections.defaultdict(list)
  for w in W:
   for d,z in [('FWD',w)]+([('REV',w[::-1])] if mode=='BIDIR' else []):
    tick();by[pattern(z)].append((z,w,d))
  for u in unique:
   rows={}
   for z,w,d in by[pattern(u)]:
    row=tuple(sorted(set(zip(u,z))));rows.setdefault(row,(w,d))
   tables[u]=sorted(rows);trace.append({'units':list(u),'candidate_maps':len(rows)})
   if not rows:return {'status':'UNSAT','reason':'empty_initial_word_table','checks':checks,'nodes':nodes,'trace':trace}
  def visit(key,rev,left):
   nonlocal nodes
   nodes+=1
   if nodes>s['nodes_cap']:raise Limit('nodes')
   if time.monotonic()-start>s['seconds_per_case']:raise Limit('wall_seconds')
   if not left:return key
   best=None;domain=None
   for u in left:
    choices=[row for row in tables[u] if compatible(row,key,rev)]
    if not choices:return None
    if domain is None or len(choices)<len(domain):best=u;domain=choices
   rest=[u for u in left if u!=best]
   for row in domain:
    k=dict(key);r=dict(rev)
    for u,a in row:k[u]=a;r[a]=u
    found=visit(k,r,rest)
    if found is not None:return found
   return None
  key=visit({}, {},unique)
  if key is None:return {'status':'UNSAT','reason':'exhausted_exact_search','checks':checks,'nodes':nodes,'trace':trace}
  active=dict(key);available=iter(a for a in alphabet if a not in set(key.values()))
  for u in signs:
   if u not in key:key[u]=next(available)
  cert=[]
  for u in groups:
   z=''.join(key[x] for x in u)
   if z in W:cert.append({'units':u,'source_word':z,'direction':'FWD'})
   else:assert mode=='BIDIR' and z[::-1] in W;cert.append({'units':u,'source_word':z[::-1],'direction':'REV'})
  return {'status':'SAT','key':key,'active_key':active,'arbitrary_extension_units':[u for u in signs if u not in active],'certificate':cert,'checks':checks,'nodes':nodes,'trace':trace,'warning':'Formal lexical certificate only; source strings have no adopted native meaning.'}
 except Limit as e:return {'status':'UNKNOWN','reason':str(e),'checks':checks,'nodes':nodes,'trace':trace}
def controls():
 s={'candidate_checks_cap':1000000,'nodes_cap':100000,'seconds_per_case':10};count=0
 for words in [['xy','xz'],['xy','xz','yz'],['xx','xy','yz'],['xxx','yxy','xzy']]:
  for groups in [[list('ab'),list('ac'),list('bc')],[list('aa'),list('bc')],[list('aba')],[list('abc')]]:
   for mode in ['FWD','BIDIR']:
    alphabet=sorted(set(''.join(words)));signs=list('abc');expected=False
    if len(alphabet)>=3:
     for p in itertools.permutations(alphabet,3):
      k=dict(zip(signs,p));ok=True
      for g in groups:
       z=''.join(k[x] for x in g);ok&=(z in words or mode=='BIDIR' and z[::-1] in words)
      expected|=ok
    got=solve(groups,words,signs,mode,s);assert got['status']==('SAT' if expected else 'UNSAT'),(words,groups,mode,got);count+=1
 assert solve([list('ab'),list('ac'),list('bc')],['xy','xz'],list('abc'),'BIDIR',s)['status']=='UNSAT'
 assert solve([list('ab'),list('ac'),list('bc')],['xy','xz','yz'],list('abc'),'FWD',s)['status']=='SAT'
 tiny=dict(s,nodes_cap=0);assert solve([list('ab')],['xy','yz'],list('abc'),'BIDIR',tiny)['status']=='UNKNOWN'
 return {'status':'PASS','exhaustive_comparison_cases':count,'joint_triangle_star_negative':True,'forced_capacity_limit_returns_UNKNOWN':True,'native_data_read':False}
def verifylock():
 lock=read(B/'LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
def generated(s,allwords):
 words=allwords['deot'];chars=sorted(set(''.join(words)));assert len(chars)==len(s['signs'])==22
 key={u:chars[(7*j+3)%22] for j,u in enumerate(s['signs'])};inverse={v:k for k,v in key.items()};e=key['e'];i=key['i'];chosen=None
 for j in range(len(words)-76):
  window=words[j:j+77]
  if e not in ''.join(window) or i not in ''.join(window):continue
  if any(e+e in w or i+i in w for w in window):continue
  chosen=(j,window);break
 if chosen is None:return {'status':'DOMAIN_WINDOW_ABSENT'}
 j,window=chosen;original=[[inverse[a] for a in w] for w in window];encoded=[]
 for wi,g in enumerate(original):encoded.append([u for ui,u in enumerate(g) for _ in range(1+(wi+ui)%3 if u in ('e','i') else 1)])
 collapsed=[collapse(g) for g in encoded];assert collapsed==original
 return {'status':'GENERATED','source':'deot','window_start':j,'source_words':window,'planted_key':key,'encoded_groups':encoded,'collapsed_groups':collapsed}
def nativegroups(s):
 ws=read(R/s['worksheet_path']);us=[u for u in ws['units'] if u['unit_id']==s['passage_unit']];assert len(us)==1
 rx=re.compile('|'.join(map(re.escape,sorted(s['signs'],key=lambda u:(-len(u),u)))));groups=[];original=[]
 for line in us[0]['lines']:
  assert line['metadata']['page']=='f75v' and line['metadata']['edition']=='IT2a'
  for g in line['original_groups']:
   raw=g[2];u=rx.findall(raw);assert ''.join(u)==raw;groups.append(collapse(u));original.append(g)
 assert len(groups)==77;return groups,original
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--gate',action='store_true');ap.add_argument('--native',action='store_true');a=ap.parse_args()
 if a.controls:print(json.dumps(controls()));return
 verifylock();s=read(B/'src/SPEC.json');W=sources(s)
 if a.gate:
  assert not (B/'artifacts/CONTROL.json').exists();c=generated(s,W)
  c['source_free_controls']=controls()
  if c['status']=='GENERATED':c['result']=solve(c['collapsed_groups'],W['deot'],s['signs'],'BIDIR',s)
  save('CONTROL.json',c);print(json.dumps({'control':c['status'],'solver':c.get('result',{}).get('status')}));return
 assert a.native and read(B/'artifacts/GATE_VALIDATION.json')['status']=='PASS';assert read(B/'artifacts/CONTROL.json')['result']['status']=='SAT';assert not(B/'artifacts/RESULT.json').exists()
 groups,original=nativegroups(s);cases=[]
 for n in s['source_names']:
  for mode in s['modes']:
   result=solve(groups,W[n],s['signs'],mode,s);cases.append({'source':n,'mode':mode,'result':result});print(json.dumps({'source':n,'mode':mode,'status':result['status'],'checks':result['checks'],'nodes':result['nodes']}),flush=True)
 save('RESULT.json',{'status':'LOCAL_SHARED_KEY_CAPACITY_SCREEN','groups':groups,'original_groups':original,'cases':cases,'claim_ceiling':s['claim_ceiling'],'global1403failures_retained':True})
if __name__=='__main__':main()
