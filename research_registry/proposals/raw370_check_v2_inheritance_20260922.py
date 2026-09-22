#!/usr/bin/env python3
"""Byte and inherited-block check only; manual semantics remain hypotheses."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
p = ROOT/'research_registry/proposals/raw370_powder_partition_v2_material_contract_20260922.json'
assert hashlib.sha256(p.read_bytes()).hexdigest() == '7676250faf7adabc2fd240635a520852c65c2d7a2f8070fb82717351a8ab6d78'
x = json.loads(p.read_text())
base = ROOT/x['base_offer']
assert hashlib.sha256(base.read_bytes()).hexdigest() == x['base_offer_sha256']
old = json.loads(base.read_text())
for name,block in x['unchanged_inherited_blocks'].items():
    assert old[name] == block, name
for name,sha in [('author_clarification','author_clarification_sha256'),('human_contract_and_complete_manual_state_ledgers','human_contract_sha256')]:
    assert hashlib.sha256((ROOT/x[name]).read_bytes()).hexdigest() == x[sha]
print(json.dumps({'status':'PASS','unchanged_blocks':len(x['unchanged_inherited_blocks']),
                  'lexical_values':len(old['lexicon']),'reader_alternatives':len(old['alternative_reading_values']),
                  'surface_productions':len(old['schematic_productions']['rules']),
                  'semantic_model_executed':False,'meaning_validation':False}))
