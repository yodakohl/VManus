#!/usr/bin/env python3
"""Reproduce the documented core-gate result, not a semantic execution."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
def main():
    receipt=json.loads((P/'artifacts/FINAL_AUTHOR_FREEZE.json').read_text())
    for name,digest in receipt['files'].items():
        assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
    result={k:receipt[k] for k in ('experiment','decision','stage2_released','accepted_core','attempted_cores','actual_dependency_tests','native_scope','whole_reading_authored','confirmed_words','independent_confirmation_capacity','scope')}
    result['basis']='Frozen core gate and author clarification; no semantic interpreter or whole-reading run.'
    result['candidate02_debts']=receipt['candidate02_author_clarification']
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
