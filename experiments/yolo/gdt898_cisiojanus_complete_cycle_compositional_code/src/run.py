#!/usr/bin/env python3
"""Exact whole-model obstruction; no search or fitted alignment is needed."""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def calculate():
    source_path = BASE / 'artifacts/SOURCE_INPUT.json'
    target_path = BASE / 'artifacts/TARGET_INPUT.json'
    source = json.loads(source_path.read_text())
    target = json.loads(target_path.read_text())
    cells = source['cells']
    assert [c['day'] for c in cells] == list(range(1, 29))
    for c in cells:
        assert re.fullmatch(r'[A-Za-z*\.\-\s]+', c['raw_text'])
        assert ''.join(re.findall('[a-z]', c['raw_text'].lower())) == c['written_atoms']
    words = [c['written_atoms'] for c in cells]
    assert all(words) and len(set(words)) == 28
    entries = target['entries']
    assert {e['locus'] for e in entries} == {f'f69v.{n}' for n in range(4, 32)}
    assert len(entries) == 28
    panels = {}
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        classes = defaultdict(list)
        for e in entries:
            assert e['raw_groups'][edition]
            classes[' '.join(e['raw_groups'][edition])].append(e['locus'])
        repeated = {v: loci for v, loci in classes.items() if len(loci) > 1}
        assert 'f69v.14' in repeated['okeod'] and 'f69v.18' in repeated['okeod']
        panels[edition] = {
            'status': 'UNSAT_BY_INJECTIVITY',
            'complete_target_entries': 28,
            'distinct_whole_target_strings': len(classes),
            'duplicate_classes': repeated,
            'common_certificate': {'loci': ['f69v.14', 'f69v.18'], 'raw_groups_each': ['okeod']},
        }
    return {
        'schema': 'GDT898_RESULT_V1',
        'status': 'CONDITIONAL_EDITED_SOURCE_ALL_THREE_PANELS_UNSAT',
        'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (source_path, target_path)},
        'source_cells': 28, 'source_distinct_strings': len(set(words)),
        'panels': panels,
        'proof': [
            'Distinct nonempty prefix-free atom codewords give a uniquely decodable concatenation code.',
            'If two source strings had the same image, compare their first atom codewords. One would be a prefix of the other; prefix freedom and atom injectivity force the first atoms equal. Cancel and repeat. Nonemptiness prevents an unmatched suffix.',
            'Therefore the morphism is injective on all finite source strings.',
            'All28 source strings are distinct, so every bijection to28 target inscriptions requires28 distinct output strings.',
            'The two complete target inscriptions f69v.14 and f69v.18 coincide exactly in each reading panel. This contradicts the requirement, independently of inscription order.',
        ],
        'excluded_alignment_scope': 'Every bijection, hence all56 cyclic phase/direction alignments. No independently certified cyclic order is required for this negative.',
        'claim_ceiling': 'Only the fixed edited February source, complete-cell pairing and injective prefix-free channel conjunction. No general calendar, historical-version or language refutation; no meanings.',
        'discovery_timing': 'Proof noticed after source/target receipt exposure, before any solver implementation. It is not a blind preregistered statistical result.',
    }


if __name__ == '__main__':
    result = calculate()
    (BASE / 'artifacts/RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(result['status'])
