#!/usr/bin/env python3
"""Post-result explanation only: a short forced-letter contradiction in w1."""
import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(E/'src/SPEC.json');result=read(E/'artifacts/RESULT.json')
assert next(c for c in result['cases'] if c['source']=='w1')['result']['status']=='UNSAT'
packet=read(ROOT/s['native_path']);groups=packet['original_units'];rs=[r['words'] for r in read(ROOT/s['recipe_path'])['w1']]
W={w for r in rs for w in r};edges={e for r in rs for e in zip(r,r[1:])}
def row(w,g):
 if len(w)!=len(g):return None
 d={}
 for c,u in zip(w,g):
  if c in d and d[c]!=u:return None
  d[c]=u
 return d
D=[{w:row(w,g) for w in W if row(w,g) is not None} for g in groups]
succ={w:set() for w in W};pred={w:set() for w in W}
for a,b in edges:succ[a].add(b);pred[b].add(a)
changed=True
while changed:
 changed=False
 for i in range(len(D)-1):
  left={w:v for w,v in D[i].items() if succ[w]&D[i+1].keys()}
  right={w:v for w,v in D[i+1].items() if pred[w]&left.keys()}
  if len(left)!=len(D[i]):D[i]=left;changed=True
  if len(right)!=len(D[i+1]):D[i+1]=right;changed=True
forced={};conflicts=[]
for i,d in enumerate(D):
 assert d
 for c in sorted(set.intersection(*(set(v) for v in d.values()))):
  values={v[c] for v in d.values()}
  if len(values)!=1:continue
  u=next(iter(values));detail={'position':i+1,'original_group':packet['original_groups'][i],'native_units':groups[i],'all_source_candidates':sorted(d),'source_codepoint':c,'required_working_unit':u}
  if c in forced and forced[c]['required_working_unit']!=u:conflicts.append([forced[c],detail])
  else:forced.setdefault(c,detail)
assert conflicts
receipt={'status':'POST_RESULT_EXPLANATORY_CONTRADICTION_ONLY','source':'w1','selected_first_conflict':conflicts[0],'projection':'All sourcewords compatible with per-word forwardfunction and some complete77position source-bigram walk. Repeated arc pruning on an acyclic position chain computes the exact per-position projections; no cross-word key constraints imposed.','reason':'The same sourcecodepoint is forced to two distinct workingunits by every possible surviving choice at these two original positions. No fixed forward function can satisfy both.','limits':['Diagnostic selected after dualUNSAT, not a preregistered prediction or a new nativelexicalassignment.','Sourcewords are hypothetical alternatives under the rejected fixedsourcegraph contract, not translations of the native words.','Other source graphs, mappings, group boundaries or writer architectures are not excluded by this literal witness.'],'lock_sha256':sha(E/'LOCK.json'),'primary_result_sha256':sha(E/'artifacts/RESULT.json'),'diagnostic_code_sha256':sha(Path(__file__))}
p=E/'artifacts/FUNCTION_CONFLICT.json';data=json.dumps(receipt,ensure_ascii=False,indent=2)+'\n'
if p.exists():assert p.read_text()==data
else:p.write_text(data)
print(json.dumps({'source':'w1','positions':[x['position'] for x in conflicts[0]],'source_codepoint':conflicts[0][0]['source_codepoint'],'required_units':[x['required_working_unit'] for x in conflicts[0]]}))
