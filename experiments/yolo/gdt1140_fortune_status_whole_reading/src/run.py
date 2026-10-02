#!/usr/bin/env python3
"""Reproduce the frozen authored-account inventory, not manuscript meanings."""
import json
import hashlib
from collections import Counter
from pathlib import Path
P = Path(__file__).resolve().parents[1]

def main():
    account_path = P / 'artifacts/AUTHOR_ACCOUNT.json'
    account = json.loads(account_path.read_text())
    receipt = json.loads((P / 'artifacts/CORE_FREEZE_RECEIPT.json').read_text())
    root = P.parents[2]
    for rel, expected in receipt['core_hashes'].items():
        assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == expected
    rows = account['primary_account']
    by_block = {}
    for block in ['N','E','S','W']:
        rs = [r for r in rows if r['native']['block'] == block]
        by_block[block] = {'positions': len(rs), 'semantic_status': dict(Counter(r['semantic_status'] for r in rs)), 'syntax_status': dict(Counter(r['syntax_status'] for r in rs))}
    result = {
        'experiment': 'GDT1140', 'decision': 'PARTIAL_SCOPED_C0',
        'account_sha256': hashlib.sha256(account_path.read_bytes()).hexdigest(),
        'counts': account['counts'], 'blocks': by_block,
        'unknown_positions': [r['native']['source_group_id'] for r in rows if r['semantic_status'] == 'UNKNOWN_WORD'],
        'scope_discrepancy': account['scope_discrepancy'],
        'result_limits': account['result_limits'],
        'additional_review_debt': 'AGAIN/FUTURE scope and AGAIN/CONTINUE antecedent semantics are underdefined; no automatic contradiction.',
        'coverage': 'Deterministic frozen-account inventory. Independent validator and human-readable reviews assess separate contract/linguistic obligations. No semantic truth test.'
    }
    assert len(result['unknown_positions']) == account['counts']['semantic_unknown_positions']
    (P / 'artifacts/RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'decision':result['decision'],'counts':result['counts'],'semantic_validation':False}))

if __name__ == '__main__':
    main()
