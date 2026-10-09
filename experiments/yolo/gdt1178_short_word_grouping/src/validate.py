#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import json
import run
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
gs,r=run.execute();stored=json.loads((A/'RESULT.json').read_text());assert r==stored
source=json.loads(run.SOURCE.read_text())
for col,variants in gs.items():
 for name,rows in variants.items():
  assert [[w for g in row for w in g] for row in rows]==[x['words'] for x in source[col]]
  flat=[tuple(g) for row in rows for g in row][:8000];c=Counter(flat)
  assert len(c)/8000==r['metrics'][col][name]['type_ratio']
  assert sum(sorted(c.values(),reverse=True)[:10])/8000==r['metrics'][col][name]['top10_share']
assert not r['passing_partitions']
(A/'VALIDATION.json').write_text(json.dumps({'status':'PASS','scientific_result':'SHORT_WORD_RULES_BOTH_FAIL','scope':'Frozen files, full source reversal and independent two-metric counts'},indent=2)+'\n')
print('PASS scoped validation; both rules fail necessary joint gate')
