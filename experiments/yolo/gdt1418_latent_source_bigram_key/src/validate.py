#!/usr/bin/env python3
"""Independent character-trie / finite-key oracle; imports no primary code."""
import argparse, collections, concurrent.futures, gzip, hashlib, itertools, json, re, sys, time
from pathlib import Path
sys.setrecursionlimit(10000)
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def configuration():
 lock=read(E/'LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 return read(E/'src/SPEC.json')
def source_sections(s):
 recipes=read(ROOT/s['recipe_path']);hebrew=read(ROOT/s['deot_path']);other=read(ROOT/s['other_path']);out={}
 for n in s['source_names']:
  if n in recipes:batches=[r['words'] for r in recipes[n]]
  elif n=='deot':batches=[r['words'] for r in hebrew['source_sections']]
  else:
   rows=other[n]['PRIMARY']['units'];assert len(rows)==8000
   batches=[]
   for _,group in itertools.groupby(rows,key=lambda r:r['sentence_index']):batches.append([r['unit'] for r in group])
  assert all(all(isinstance(w,str) and w for w in batch) for batch in batches)
  out[n]=batches
 return out

def graph(batches):
 words=set();edges=set()
 for b in batches:words.update(b);edges.update(zip(b,b[1:]))
 nxt={w:set() for w in words}
 for a,b in edges:nxt[a].add(b)
 return words,nxt

def direct(result,stream,G,signs,mode):
 W,nxt=G;k=result['key'];alphabet=set(''.join(W))
 assert set(k)==set(signs) and len(set(k.values()))==len(signs)
 assert all(isinstance(c,str) and len(c)==1 and c in alphabet for c in k.values())
 seq=stream if mode=='FWD' else stream[::-1]
 decoded=''.join(k[u] for u in seq);ws=result['source_words']
 assert ws and ''.join(ws)==decoded and all(w in W for w in ws)
 assert all(b in nxt[a] for a,b in zip(ws,ws[1:]))
 assert result['decoded_stream']==decoded
 cursor=0;ends=[]
 for w in ws:cursor+=len(w);ends.append(cursor)
 assert result['breaks']==ends and cursor==len(seq)
 return {'units':len(seq),'words':len(ws),'singleton_words':sum(len(w)==1 for w in ws),'longest_singleton_run':max((sum(1 for _ in g) for x,g in itertools.groupby(ws,key=lambda w:len(w)==1) if x),default=0)}

class Stop(Exception):pass

def solve(stream,G,signs,mode,limits):
 started=time.monotonic();W,nxt=G;alphabet=sorted(set(''.join(W)))
 if len(alphabet)<len(signs):return {'status':'UNSAT','reason':'alphabet_cardinality','nodes':0,'checks':0}
 seq=list(stream) if mode=='FWD' else list(reversed(stream))
 if not seq:return {'status':'UNSAT','reason':'nonempty_message_required','nodes':0,'checks':0}
 cache={};failed=set();assign=[None]*len(signs);slot={u:i for i,u in enumerate(signs)};used=set();nodes=checks=0
 def trie(previous):
  if previous not in cache:
   links=[{}];ends=[None]
   for word in sorted(W if previous is None else nxt[previous]):
    node=0
    for c in word:
     if c not in links[node]:links[node][c]=len(links);links.append({});ends.append(None)
     node=links[node][c]
    ends[node]=word
   cache[previous]=(links,ends)
  return cache[previous]
 def tick(candidate=False):
  nonlocal nodes,checks
  if candidate:checks+=1
  else:nodes+=1
  if nodes>limits['nodes_cap'] or checks>limits['candidate_checks_cap'] or time.monotonic()-started>limits['seconds_per_case']:raise Stop()
 def visit(p,previous,node,done):
  tick();links,ends=trie(previous)
  if p==len(seq):return (assign[:],done+[ends[node]]) if ends[node] is not None else None
  state=(p,previous,node,tuple(assign))
  if state in failed:return None
  if ends[node] is not None:
   found=visit(p,ends[node],0,done+[ends[node]])
   if found is not None:return found
  idx=slot[seq[p]];c=assign[idx]
  choices=[(c,links[node][c])] if c in links[node] else []
  if c is None:choices=[(char,to) for char,to in sorted(links[node].items()) if char not in used]
  for char,to in choices:
   tick(True);fresh=assign[idx] is None
   if fresh:assign[idx]=char;used.add(char)
   found=visit(p+1,previous,to,done)
   if fresh:assign[idx]=None;used.remove(char)
   if found is not None:return found
  failed.add(state);return None
 try:
  answer=visit(0,None,0,[])
  if answer is None:return {'status':'UNSAT','reason':'exhaustive_context_character_trie','nodes':nodes,'checks':checks}
  values,words=answer;free=iter(c for c in alphabet if c not in values)
  key={u:(values[j] if values[j] is not None else next(free)) for j,u in enumerate(signs)}
  ends=[];p=0
  for w in words:p+=len(w);ends.append(p)
  result={'status':'SAT','key':key,'source_words':words,'breaks':ends,'decoded_stream':''.join(key[u] for u in seq),'nodes':nodes,'checks':checks}
  direct(result,stream,G,signs,mode);return result
 except Stop:return {'status':'UNKNOWN','reason':'independent_budget','nodes':nodes,'checks':checks}

def oracle(stream,G,signs,mode):
 W,nxt=G;seq=stream if mode=='FWD' else stream[::-1];alphabet=sorted(set(''.join(W)))
 if not seq:return False
 for vals in itertools.permutations(alphabet,len(signs)):
  key=dict(zip(signs,vals));t=''.join(key[u] for u in seq);reachable={(0,None)}
  for i in range(len(t)):
   for pos,prev in list(reachable):
    if pos!=i:continue
    for w in W if prev is None else nxt[prev]:
     if t.startswith(w,i):reachable.add((i+len(w),w))
  if any(p==len(t) for p,w in reachable):return True
 return False

def controls():
 batches=[[['x','y','x']],[['xx','yy','xx']],[['xy','yx'],['x','yy']],[['x'],['y']],[['x','x','y'],['yx','xy']],[['xy','xy'],['yx','yx']]]
 lim={'nodes_cap':100000,'candidate_checks_cap':1000000,'seconds_per_case':5};n=0
 for rows in batches:
  G=graph(rows)
  for size in range(5):
   for tup in itertools.product('ab',repeat=size):
    for mode in ('FWD','REVERSE'):
     stream=list(tup);wanted=oracle(stream,G,list('ab'),mode);r=solve(stream,G,list('ab'),mode,lim)
     assert r['status']==('SAT' if wanted else 'UNSAT'),(rows,stream,mode,r)
     if wanted:direct(r,stream,G,list('ab'),mode)
     n+=1
 assert solve(list('ab'),graph([['xy','yx']]),list('ab'),'FWD',dict(lim,nodes_cap=0))['status']=='UNKNOWN'
 return {'status':'PASS','exhaustive_key_and_directed_wordbreak_comparisons':n,'primary_imported':False,'forced_cap_unknown':True}

def gate(s):
 own=controls();allsections=source_sections(s);batches=allsections['deot'];i=next(i for i,b in enumerate(batches) if len(b)>=32);G=graph(batches);control=read(A/'CONTROL.json')
 words=batches[i][:32];alphabet=sorted(set(''.join(G[0])));assert len(alphabet)==len(s['signs'])==22
 planted={u:alphabet[(7*j+3)%22] for j,u in enumerate(s['signs'])};inverse={c:u for u,c in planted.items()};encoded=[inverse[c] for c in ''.join(words)]
 assert control['source']=='deot' and control['source_section_index']==i
 assert control['source_words']==words and control['planted_key']==planted and control['encoded_stream']==encoded
 assert control['result']['status']=='SAT','New generated control not recovered; native gate stays closed'
 receipt=direct(control['result'],encoded,G,s['signs'],'FWD')
 independent=solve(encoded,G,s['signs'],'FWD',dict(s,seconds_per_case=s['control_seconds']))
 assert independent['status']=='SAT','Independent control capacity not obtained; stop before native'
 independent_receipt=direct(independent,encoded,G,s['signs'],'FWD')
 save('INDEPENDENT_CONTROL.json',{'result':independent,'receipt':independent_receipt})
 save('GATE_VALIDATION.json',{'status':'PASS','experiment_id':'GDT1418','independent_toys':own,'control':receipt,'independent_control':independent_receipt,'new_control_selected_before_results':True,'1408_original_stop_unchanged':True,'semantic_truth':False})
 print(json.dumps({'gate':'PASS','toys':own,'control_words':receipt['words']}))

def extract(s):
 x=read(ROOT/s['worksheet_path']);wrapper=x['source_original_wrapper'];assert wrapper['unit_id']==s['passage_unit'];unit=wrapper['source_unit']
 signs=sorted(s['signs'],key=lambda u:(-len(u),u));rx=re.compile('|'.join(map(re.escape,signs)));groups=[];parsed=[]
 assert [line['metadata']['locus'] for line in unit['lines']]==['f75v.'+str(i) for i in range(43,50)]
 for line in unit['lines']:
  assert line['metadata']['edition']=='IT2a' and line['metadata']['page']=='f75v'
  assert len(line['groups'])==int(line['metadata']['source_group_count'])
  for index,row in enumerate(line['groups'],1):
   assert len(row)==5 and int(row[1])==index
   pieces=rx.findall(row[2]);assert ''.join(pieces)==row[2];groups.append(row);parsed.append(pieces)
 assert len(groups)==s['expected_passage_groups']==77
 return unit,groups,parsed,list(itertools.chain.from_iterable(parsed))

def one_case(args):
 source,mode,stream,G,s=args;return {'source':source,'mode':mode,'result':solve(stream,G,s['signs'],mode,s)}

def native(s):
 assert read(A/'GATE_VALIDATION.json')['status']=='PASS'
 unit,groups,units,stream=extract(s);x=read(A/'NATIVE_INPUT.json');result=read(A/'RESULT.json')
 assert x['original_groups']==groups and x['original_units']==units and x['stream']==stream and x['lines']==unit['lines']
 sections=source_sections(s);graphs={n:graph(rows) for n,rows in sections.items()}
 expected=[(n,m) for n in s['source_names'] for m in s['directions']]
 assert [(c['source'],c['mode']) for c in result['cases']]==expected
 with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:
  own=list(pool.map(one_case,[(n,m,stream,graphs[n],s) for n,m in expected]))
 checks=[]
 for p,q in zip(result['cases'],own):
  name,mode=p['source'],p['mode'];pr=p['result'];qr=q['result'];receipts=[]
  for label,r in [('primary',pr),('independent',qr)]:
   if r['status']=='SAT':receipts.append({'engine':label,**direct(r,stream,graphs[name],s['signs'],mode)})
  assert not ({pr['status'],qr['status']}=={'SAT','UNSAT'}),'conflicting exact results'
  effective='SAT' if receipts else 'UNSAT' if pr['status']==qr['status']=='UNSAT' else 'UNRESOLVED'
  checks.append({'source':name,'mode':mode,'primary':pr['status'],'independent':qr['status'],'effective':effective,'certificates':receipts})
 save('INDEPENDENT_RESULT.json',{'experiment_id':'GDT1418','cases':own})
 save('VALIDATION.json',{'status':'PASS','experiment_id':'GDT1418','source_and_original77group_provenance':'PASS','native_units':len(stream),'cases':checks,'semantic_truth':False,'scope':'Exact certificates and paired finite search results only. UNSAT requires two exhaustive engines; UNKNOWN is unresolved.'})
 print(json.dumps({'status':'PASS','counts':dict(collections.Counter(c['effective'] for c in checks))}))

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--gate',action='store_true');g.add_argument('--native',action='store_true');a=p.parse_args();s=configuration()
 if a.gate:gate(s)
 else:native(s)
if __name__=='__main__':main()
