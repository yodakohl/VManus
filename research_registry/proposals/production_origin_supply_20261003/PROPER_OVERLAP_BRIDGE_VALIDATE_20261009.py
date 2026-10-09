#!/usr/bin/env python3
"""Verify compact witnesses without importing replay or recomputing its domains."""
from pathlib import Path
import gzip,hashlib,json
B=Path(__file__).resolve().parent;R=B.parents[2]
d=json.loads((B/'PROPER_OVERLAP_SINGLETON_BRIDGE_RESULT_20261009.json').read_text())
for p,h in d['bindings'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
source=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
checked=0
for reader,proof in d['readers'].items():
 rows={x['id']:x for x in source[reader]};known=set()
 for step in proof['steps']:
  g=step['head'];assert set(step['previous_forced_singletons'])==known and g not in known
  remainders=[]
  for w in step['witnesses']:
   q=rows[w['id']];assert q['ivtff_group_raw']==w['raw'] and q['units']==w['units']
   assert q['left_separator']==q['right_separator']=='DEFINITE_SPACE' and q['kind']=='P'
   i=w['offset_after_forced_singletons'];assert 0<=i<len(q['units']) and all(x in known for x in q['units'][:i])
   rem=q['units'][i:];assert rem==w['remainder'] and rem[0]==g;remainders.append(rem);checked+=1
  assert any(len(x)==1 for x in remainders) or len({x[1] for x in remainders})>=2
  assert step['common_prefix']==[g];known.add(g)
 assert len(known)==22
 counts={x:0 for x in known}
 for q in rows.values():counts[q['units'][0]]+=1
 assert counts==proof['original_initial_head_counts']
 assert proof['at_most22_arbitrary_heads_bridge']==all(counts.values())
out={'status':'PASS','proof_steps':66,'exact_source_witnesses':checked,'source_hashes_verified':len(d['bindings']),'native_scope':'Sameoldcache; no newglyph/wordboundaries, no meaning. Differentimplementationbyrootnotindependentpalaeography','logical_scope':'Witness-onlycheck supports singleton induction stated in dossier, doesnottransfer generalbacktracking results.'}
(B/'PROPER_OVERLAP_BRIDGE_VALIDATION_20261009.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
