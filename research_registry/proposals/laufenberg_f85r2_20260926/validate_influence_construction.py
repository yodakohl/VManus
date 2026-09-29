#!/usr/bin/env python3
"""Independent input-accounting and hand-derived local-direction checks only."""
import csv
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
R = B.parents[2]


def main():
    lock = json.loads((B / 'INFLUENCE_CONSTRUCTION_LOCK_20260929.json').read_text())
    for path, digest in lock['inputs'].items():
        assert hashlib.sha256((R / path).read_bytes()).hexdigest() == digest
    def read(path):
        with path.open() as f:
            return list(csv.DictReader(f, delimiter='\t'))
    source = read(B / 'source_supply_20260929/E_WHOLE_CONTEXT_TABLE.tsv')
    table = read(B / 'INFLUENCE_CONSTRUCTION_TABLE_20260929.tsv')
    fields = ('edition', 'locus', 'group_index', 'raw_group')
    assert len(source) == len(table) == 288
    assert [tuple(x[k] for k in fields) for x in source] == [tuple(x[k] for k in fields) for x in table]
    result = json.loads((B / 'INFLUENCE_CONSTRUCTION_RESULT_20260929.json').read_text())
    assert len(result['clauses']) == 18
    assert len(result['exact_okol_occurrences']) == 12
    assert {c['predicate_key'][1] for c in result['clauses']} == {'f68r2.31', 'f89v1.14'}
    for c in result['clauses']:
        variant = c['model'][0]
        if c['unit'] == 'f68r2.31':
            expected = ('okeo' if c['edition'] == 'IT2a' else 'okey', 'okol')
        elif c['edition'] == 'RF1b' and variant in 'HP':
            assert c['status'] == 'UNRESOLVED_RF_MARKER_NO_EMENDATION'
            assert c['source_head'] is None and c['recipient_head'] is None
            continue
        elif variant == 'A':
            expected = ('cho@152;y' if c['edition'] == 'RF1b' else 'chody', 'dal')
        else:
            expected = {'H': ('okol', 'dal'), 'P': ('dal', 'okol')}[variant]
        assert (c['source_head']['raw'], c['recipient_head']['raw']) == expected
    assert sum(x['same_recipient_to_source_class'] for x in result['class_links']) == 2
    assert sum(x['same_recipient_class'] for x in result['class_links']) == 2
    conditional = [c for c in result['clauses'] if c['boundary_assumptions']]
    assert len(conditional) == 3
    for c in conditional:
        assert c['edition'] == 'ZL3b' and c['unit'] == 'f89v1.13-20'
        assert c['status'] == 'C0_LOCAL_DERIVATION_REQUIRES_UNCERTAIN_BOUNDARY'
        assert c['boundary_assumptions'] == [{
            'key': ['ZL3b', 'f89v1.14', 8], 'edge': 'right_separator',
            'raw_flag': 'UNCERTAIN_SMALL_SPACE',
            'choice_needed': 'Treat this uncertain gap as the chosen NP boundary.'}]
    assert result['complete_readings'] == result['confirmed_word_meanings'] == 0
    assert not result['draw_away_relation_bound'] and not result['excluded_body_region_bound']
    names = ['INFLUENCE_CONSTRUCTION_PREFLIGHT_20260929.md',
             'INFLUENCE_CONSTRUCTION_LOCK_20260929.json',
             'INFLUENCE_CONSTRUCTION_TABLE_20260929.tsv',
             'INFLUENCE_CONSTRUCTION_RESULT_20260929.json',
             'influence_construction.py', 'validate_influence_construction.py']
    report = {'status': 'PASS_ACCOUNTING_AND_DECLARED_LOCAL_DERIVATIONS_ONLY',
              'input_hashes_checked': len(lock['inputs']), 'unchanged_input_groups': 288,
              'checked_local_model_reader_cases': 18,
              'cases_requiring_uncertain_boundary_choice': 3, 'semantic_validation': False,
              'files': {n: hashlib.sha256((B/n).read_bytes()).hexdigest() for n in names}}
    (B / 'INFLUENCE_CONSTRUCTION_VALIDATION_20260929.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
