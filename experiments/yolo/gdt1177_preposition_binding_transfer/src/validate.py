#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import json
import run
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
def main():
 source=json.loads((A/'SOURCE_TEXTS.json').read_text());groups=json.loads((A/'PARTITIONS.json').read_text());r=json.loads((A/'RESULT.json').read_text())
 rr,ee,gg,expected=run.execute()
 assert rr==source and gg==groups and expected==r
 target=json.loads((run.ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets']
 n=8000
 for col,pp in groups.items():
  for name,rows in pp.items():
   assert [[w for g in row for w in g] for row in rows]==[x['words'] for x in source[col]]
   seen={};total=0
   for row in rows:
    for g in row:
     if total<n:seen[tuple(g)]=seen.get(tuple(g),0)+1;total+=1
   assert total==n
   c=r['metrics'][col][name]
   assert c['types']==len(seen) and c['top10_share']==sum(sorted(seen.values(),reverse=True)[:10])/n
 for name in r['comparison']:
  joint=all(abs(r['metrics'][col][name][key]-t[key])<=.05 for col in groups for t in target.values() for key in ['type_ratio','top10_share'])
  assert joint==r['comparison'][name]['all_necessary_gates']
 assert not r['passing_partitions']
 out={'status':'PASS','scope':'hash lock, complete source tuple reversal, independent counts and unchanged joint gate','scientific_result':'NARROW_BINDING_FAILS_TRANSFER'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
