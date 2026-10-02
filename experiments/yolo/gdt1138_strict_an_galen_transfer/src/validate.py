#!/usr/bin/env python3
"""Independent read-only source validation; author review added after freezes."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_source():
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    baseline = json.loads((BASE / 'src/BASELINE34.json').read_text())
    core = json.loads((BASE / 'src/C_FIXED_OPERATORS.json').read_text())
    pp = ROOT / source['parent_path']
    assert sha(pp) == source['parent_sha256'] == baseline['parent_sha256']
    parent = json.loads(pp.read_text())
    assert source['whole_record'] == parent['target_choice']['whole_record']
    assert source['alternative_reader_records'] == parent['target_choice']['alternative_reader_records']
    assert source['complete_selected_source'] == parent['complete_selected_source']
    expected = [x for x in parent['lexicon'] if x['form'] not in {'aiin', 'daiin'}]
    assert baseline['entries'] == expected and len(expected) == 34
    cp = ROOT / core['parent_path']
    assert sha(cp) == core['parent_sha256']
    original = json.loads(cp.read_text())
    assert core['families'] == [x for x in original['families'] if x['id'] in {'aN', 'd'}]
    assert core['initial_exact_entries'] == {k: original['initial_exact_entries'][k] for k in ['aiin', 'daiin']}
    assert sha(ROOT / core['implementation_receipt']['path']) == core['implementation_receipt']['sha256']
    counts = {}
    for edition, packet in [('ZL3b', source['whole_record']), ('IT2a', source['alternative_reader_records']['IT2a'])]:
        counts[edition] = sum(len(x['words']) for x in packet['lines'])
        for line in packet['lines']:
            assert len(line['words']) == len(line['source_ids'])
            assert line['locus'] in {'f107v.' + str(i) for i in range(45, 50)}
            assert all(s.startswith(edition + '|' + line['locus'] + '|') for s in line['source_ids'])
    assert counts == {'ZL3b': 49, 'IT2a': 51}
    assert 'NOT_PRESENT' in source['separator_metadata']
    assert 'No matching complete' in source['RF_status']
    return {'status': 'SOURCE_MECHANICAL_PASS_AUTHOR_NOT_EVALUATED', 'groups': counts,
            'baseline_types': 34, 'confirmed_words': 0, 'independent_confirmation_capacity': 0}


if __name__ == '__main__':
    print(json.dumps(check_source(), indent=2))
