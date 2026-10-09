import gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SIGNS=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh']
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def loadgz(p):return json.loads(gzip.decompress((R/p).read_bytes()))
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def path(reader,side):return ('experiments/yolo/gdt1234_prefix_quotient_code_capacity/artifacts/CERTIFICATE_' if side=='LEFT' else 'experiments/yolo/gdt1241_suffix_quotient_expansion/artifacts/CLOSURE_')+reader+'.json.gz'
def fixtures():
 square=quotient=0
 for n in range(1,5):
  ps=list(itertools.permutations(range(n)))
  for t in ps:
   for s in range(n):
    if t[s]==t[t[s]]:assert t[s]==s
    square+=1
  if n<=3:
   for u,v in itertools.product(ps,repeat=2):
    for s in range(n):
     if u[s]==s and v[u[s]]==s:assert v[s]==s
     if u[s]==s and u[v[s]]==s:assert v[s]==s
     quotient+=1
 # The square rule fails for a noninjective constant map.
 const=[1,1];assert const[0]==const[const[0]] and const[0]!=0
 # A reset by space could erase a variable pre-reset end, outside this rule.
 # A square alone does not force the component generator: aa,aaaa,b all fix0.
 a=[1,0];b=[0,1]
 assert a[a[0]]==0 and a[a[a[a[0]]]]==0 and b[0]==0 and a[0]!=0
 return {'status':'PASS','square_cases':square,'quotient_cases':quotient,'noninjective_square_counterexample':{'map':const,'start':0,'end':1},'insufficient_generator_example':{'A':a,'B':b,'words':['AA','AAAA','B'],'start':0,'end':0}}
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fix=fixtures();data=loadgz(CACHE);proofs={};summaries={};source_total=sum(map(len,data.values()))
 for reader in ['ZL3b','IT2a','RF1b']:
  byword={}
  for r in data[reader]:
   assert not r['page'].startswith('f84') and r['page']!='f116v'
   assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
   assert ''.join(r['units'])==r['ivtff_group_raw'] and set(r['units'])<=set(SIGNS)
   byword.setdefault(tuple(r['units']),[]).append(r)
  square={w:[{'id':r['id'],'page':r['page'],'locus':r['locus'],'word':r['ivtff_group_raw'],'units':r['units']} for r in sorted(byword.get(tuple(w),[]),key=lambda r:r['id'])] for w in ['ol','olol']}
  nodes={side:loadgz(path(reader,side))['nodes'] for side in ['LEFT','RIGHT']}
  indices={side:{tuple(n['word']):i for i,n in enumerate(ns)} for side,ns in nodes.items()};needed={side:set() for side in nodes};targets={};missing=[]
  def visit(side,i):
   if i in needed[side]:return
   n=nodes[side][i];needed[side].add(i)
   if n['parents'] is not None:
    for p in n['parents']:assert p<i;visit(side,p)
  for g in SIGNS:
   side=next((s for s in ['LEFT','RIGHT'] if (g,) in indices[s]),None)
   if side is None:missing.append(g);continue
   i=indices[side][(g,)];targets[g]=[side,i];visit(side,i)
  selected={};seedtypes=set()
  for side in nodes:
   selected[side]=[]
   for i in sorted(needed[side]):
    n=nodes[side][i];rec={'old_id':i,'word':n['word'],'parents':n['parents']}
    if n['parents'] is None:
     w=tuple(n['word']);assert w in byword;seedtypes.add(w);rs=byword[w]
     rec.update(source_ids=sorted(r['id'] for r in rs),frequency=len(rs),pages=sorted({r['page'] for r in rs}))
    else:
     u,v=[nodes[side][p]['word'] for p in n['parents']]
     assert v==(u+n['word'] if side=='LEFT' else n['word']+u)
    selected[side].append(rec)
  status='NONTRIVIAL_REVERSIBLE_WORD_COMPLETION_EXCLUDED' if not missing and all(square.values()) else 'INCONCLUSIVE_BRIDGE'
  proofs[reader]={'square':square,'targets':targets,'chains':selected}
  summaries[reader]={'status':status,'whole_groups':len(data[reader]),'whole_types':len(byword),'square_counts':{w:len(v) for w,v in square.items()},'forced_units':[g for g in SIGNS if g in targets],'missing_units':missing,'left_targets':sum(v[0]=='LEFT' for v in targets.values()),'right_targets':sum(v[0]=='RIGHT' for v in targets.values()),'chain_nodes':sum(map(len,selected.values())),'seed_types':len(seedtypes),'singleton_frequency_seed_types':[''.join(w) for w in sorted(seedtypes) if len(byword[w])==1],'seed_occurrences':sum(len(byword[w]) for w in seedtypes)}
 result={'status':'ALL_READERS_REVERSIBLE_WORD_COMPLETION_EXCLUDED' if all(v['status']=='NONTRIVIAL_REVERSIBLE_WORD_COMPLETION_EXCLUDED' for v in summaries.values()) else 'INCONCLUSIVE_BRIDGE','source_occurrences':source_total,'readers':summaries,'ceiling':'Natural common word endpoint before whitespace reset, fixed reversible unit maps and nontrivial reachable orbit only; no general writer or semantic exclusion.'}
 save('FIXTURES',fix);save('PROOFS',proofs);save('RESULT',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
