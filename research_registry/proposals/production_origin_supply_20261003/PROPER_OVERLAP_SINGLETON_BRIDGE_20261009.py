#!/usr/bin/env python3
"""Replay only singleton chains; not the general1233search or a new native fit."""
from pathlib import Path
import gzip,hashlib,itertools,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
SRC=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts'
def get(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def encode(word,table,full=False):
 out=table[word[0]];prev=out
 for a in word[1:]:
  nxt=table[a];limit=min(len(prev),len(nxt))-(0 if full else 1)
  overlap=max([0]+[k for k in range(1,limit+1) if prev[-k:]==nxt[:k]])
  out+=nxt[overlap:];prev=nxt
 return out

def main():
 paths=[SRC/'GROUPS.json.gz',ROOT/'experiments/yolo/gdt1293_prefix_only_marker_capacity/artifacts/RESULT.json']+[SRC/f'CERTIFICATE_{r}.json.gz' for r in ['ZL3b','IT2a','RF1b']]
 data=get(paths[0]);counts=get(paths[1]);result={};total=0
 for r,rows in data.items():
  cert=get(SRC/f'CERTIFICATE_{r}.json.gz');known=set();steps=[];node=cert
  while node['kind']=='branch':
   g=node['head'];assert g not in known and node['options']==[[g]] and len(node['children'])==1 and node['children'][0]['code']==[g]
   residual=[]
   for q in rows:
    w=q['units'];i=0
    while i<len(w) and w[i] in known:i+=1
    if i<len(w) and w[i]==g:residual.append((q,i,w[i:]))
   assert residual
   common=list(residual[0][2])
   for _,_,rest in residual[1:]:
    n=0
    while n<min(len(common),len(rest)) and common[n]==rest[n]:n+=1
    common=common[:n]
   assert common==[g]
   residual.sort(key=lambda x:x[0]['id']);short=[x for x in residual if len(x[2])==1]
   if short:witnesses=short[:1]
   else:
    first=residual[0];second=next(x for x in residual if x[2][1]!=first[2][1]);witnesses=[first,second]
   steps.append({'head':g,'previous_forced_singletons':sorted(known),'common_prefix':common,'witnesses':[{'id':q['id'],'raw':q['ivtff_group_raw'],'units':q['units'],'offset_after_forced_singletons':i,'remainder':rest} for q,i,rest in witnesses]})
   known.add(g);node=node['children'][0]['node'];total+=1
  assert node['kind']=='identity_only' and len(known)==22 and set(node['used_heads'])==known
  initials={u:sum(q['units'][0]==u for q in rows) for u in known}
  assert initials=={u:z['initial_groups'] for u,z in counts['readers'][r]['stats'].items()}
  result[r]={'singleton_chain_steps':len(steps),'steps':steps,'original_initial_head_counts':dict(sorted(initials.items())),'positive_initial_heads':sum(v>0 for v in initials.values()),'at_most22_arbitrary_heads_bridge':all(v>0 for v in initials.values())}
 assert [result[r]['positive_initial_heads'] for r in ['ZL3b','IT2a','RF1b']]==[20,21,22]
 table={'a':'aa','b':'bb'};seen={};checks=0
 for n in range(1,11):
  for w in map(''.join,itertools.product('ab',repeat=n)):
   out=encode(w,table);assert out not in seen;seen[out]=w;checks+=1
   # Independent inverse: every maximal visible run has one more sign than source run.
   runs=[(c,len(list(gr))) for c,gr in itertools.groupby(out)];assert all(n>=2 for _,n in runs)
   back=''.join(c*(n-1) for c,n in runs);assert back==w
 assert {encode(w,table) for w in ['a','aa','b','bb']}=={'aa','aaa','bb','bbb'}
 assert encode('a',table,True)==encode('aa',table,True)=='aa'
 out={'status':'PROPER_OVERLAP_SINGLETON_BRIDGE_VERIFIED','type':'mathematical_consequence_and_old_certificate_replay_not_new_native_search','bindings':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'readers':result,'singleton_steps_total':total,'source_free_control_words':checks,'control_limit':'Finite2046checks support explicit all-run inverse proof; ordinary result alone is insufficient','full_self_overlap':'Maximal overlap allowing complete identical codes collapses a and aa; no claim about every rule allowing some full overlaps','native_new_meanings':0,'scope':'Allreaders onlywithEXPLICITdistinctfirstheads;atmost22arbitraryheadscodefamily onlyRF. Shared ink insideworkingunits outside.'}
 (B/'PROPER_OVERLAP_SINGLETON_BRIDGE_RESULT_20261009.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','singleton_steps_total','source_free_control_words','scope']}))
if __name__=='__main__':main()
