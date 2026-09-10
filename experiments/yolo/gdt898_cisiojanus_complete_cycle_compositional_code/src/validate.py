#!/usr/bin/env python3
"""Bind the independently replayed input premises to the complete-model proof."""
import hashlib
import json
from pathlib import Path
from run import calculate

base=Path(__file__).resolve().parents[1]
a=base/'artifacts'
result=json.loads((a/'RESULT.json').read_text())
assert result==calculate()
independent=json.loads((a/'INDEPENDENT_VALIDATION.json').read_text())
assert independent['status']=='PASS_CONDITIONAL_MODEL_IMPOSSIBLE'
for name,key in [('SOURCE_INPUT.json','source_input_sha256'),('TARGET_INPUT.json','target_input_sha256')]:
    assert hashlib.sha256((a/name).read_bytes()).hexdigest()==independent[key]
assert independent['distinct_source_strings']==28
assert independent['target_entries_replayed']==28
assert independent['target_group_rows_replayed']==100
assert len(independent['duplicate_witnesses'])==3
validation={'status':'PASS','result':'CONDITIONAL_EDITED_SOURCE_ALL_THREE_PANELS_UNSAT','primary_result_rebuild':'BYTE_CONTENT_EQUIVALENT','independent_primary_source_replay':'PASS','source_exact_diplomatic_reading':'UNRESOLVED','native_order_independently_certified':False,'claim':'Only fixed edited source/complete-cell/injective-prefix-code conjunction; no meanings.'}
(a/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
print('PASS')
