#!/usr/bin/env python3
"""Validate frozen inputs and replay any complete positive witnesses."""
import hashlib
import itertools
import json
from pathlib import Path
from source import load_source, compile_program
BASE = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    sp, tp = [BASE / 'artifacts' / x for x in ['SOURCE_PROGRAMS.json', 'TARGET_INPUT.json']]
    assert sha(sp) == 'ee1f78c739102e46db5f2dd2b0fb9c76182fff716ed4b4e4efc3e7d93308ac81'
    assert sha(tp) == 'd360ccbcbae0641b33d4af5e36ae5e121baacbe482334dc2f18bc490a6f3dd40'
    source = load_source(sp)
    target = json.loads(tp.read_text())
    assert {k: len(v) for k, v in target['panels'].items()} == {'ZL3b': 14, 'IT2a': 259, 'RF1b': 11, 'CONSENSUS': 1}
    for panel in target['panels'].values():
        assert len({p['id'] for p in panel}) == len(panel)
        for p in panel:
            assert not p['page'].startswith('f84') and int(p['physical_folio'][1:]) % 2 == 1
            assert p['text'] == ' '.join(p['words'])
    source_review = json.loads((BASE / 'artifacts/SOURCE_VALIDATION.json').read_text())
    assert source_review['source_programs_sha256'] == sha(sp)
    assert source_review['independent_fitter_sha256'] == sha(BASE / 'src/independent_z3.py')
    cases = []
    for engine in ['cvc5', 'z3']:
        for path in sorted((BASE / 'artifacts' / engine).glob('case_*.json')):
            r = json.loads(path.read_text())
            assert r['source_sha256'] == sha(sp) and r['target_sha256'] == sha(tp)
            assert r['header_order'] in source['header_orders']
            status = r.get('status', r.get('first_status'))
            assert status in ['SAT', 'UNSAT'] or status.startswith('UNKNOWN')
            if status == 'SAT':
                code = r.get('codeword_witness', r.get('codewords'))
                assert set(code) == set(source['vocabulary']) and all(code.values())
                assert all(not code[a].startswith(code[b]) and not code[b].startswith(code[a])
                           for a, b in itertools.combinations(code, 2))
                outputs = [''.join(code[a] for a in compile_program(p, r['header_order'])) for p in source['programs']]
                assert len(set(outputs)) == 24
                assert set(outputs) <= {p['text'] for p in target['panels']['IT2a']}
            cases.append({'engine': engine, 'header_order': r['header_order'], 'status': status, 'artifact_sha256': sha(path)})
    if cases:
        assert len(cases) == 12
        assert len({(c['engine'], tuple(c['header_order'])) for c in cases}) == 12
    result = {'schema': 'GDT899_VALIDATION_V1', 'status': 'PASS', 'phase': 'RESULTS' if cases else 'REGISTERED_INPUTS_ONLY',
              'source_sha256': sha(sp), 'target_sha256': sha(tp), 'compiled_complete_source_programs': 24,
              'header_orders': 6, 'checked_cases': cases,
              'limit': 'UNSAT statuses are solver results, not independently checked proof objects; timeout is unresolved.'}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'phase': result['phase'], 'cases': len(cases)}))
if __name__ == '__main__':
    main()
