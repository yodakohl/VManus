#!/usr/bin/env python3
"""Reproduce this frozen partial-account result; does not execute unknown prose."""
from pathlib import Path
import csv
import hashlib
import json
from collections import Counter

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[2]
def read(name):
    return json.loads((P / name).read_text())
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    lock = read('src/PREREG_LOCK.json')
    freeze = read('artifacts/AUTHOR_FREEZE.json')
    for bindings in (lock['hashes'], freeze['hashes']):
        for path, pin in bindings.items():
            assert digest(P / path) == pin, path
    source = read('src/SOURCE.json')
    assert digest(ROOT / source['source']) == source['sha256']
    with (P / 'artifacts/TARGET.tsv').open() as stream:
        lines = list(csv.DictReader(stream, delimiter='\t'))
    assert len(lines) == 8 and all(r['page'] == 'f83r' and r['record_id'] == 'F83_P1' for r in lines)
    actual = [(r['locus'] + ':' + str(i), word) for r in lines for i, word in enumerate(r['zl3b_line'].split(), 1)]
    account = read('artifacts/AUTHOR_ACCOUNT.json')
    rows = account['accounting']['rows']
    assert [(r['at'], r['word']) for r in rows] == actual and len(rows) == 72
    guesses = [r for r in rows if r['value_id'] is not None]
    unknowns = [r for r in rows if r['value_id'] is None]
    assert len(guesses) == 8 and len(unknowns) == 64
    assert all(r['status'] == 'proposed_value_unbound' for r in guesses)
    assert all(r['status'] == 'unknown_unassigned' and r['rule'] is None for r in unknowns)
    assert not freeze['accounting']['complete_chain']
    first = next(i for i, r in enumerate(rows) if r['word'] == 'qoteedy')
    before = sum(r['word'] == 'qokaiin' for r in rows[:first])
    result = {
        'experiment': 'GDT1145', 'decision': 'PARTIAL_ACCOUNT',
        'secondary_status': 'NO_EXECUTED_WRITTEN_MEMBERSHIP_CHAIN',
        'lines': len(lines), 'groups': len(rows),
        'provisional_whole_form_values': len(account['lexical_values']),
        'uniform_proposed_rules': len(account['rules']),
        'proposed_value_occurrences': len(guesses), 'unknown_occurrences': len(unknowns),
        'proposed_form_counts': dict(Counter(r['word'] for r in guesses)),
        'all_proposed_positions': [{k:r[k] for k in ('at','word','rule','status')} for r in guesses],
        'first_selector': rows[first]['at'],
        'proposed_introduction_tokens_before_first_selector': before,
        'count_limit': 'Token count only, not executed state; earlier unknowns remain semantically open.',
        'whole_record_execution': 'NOT_AVAILABLE',
        'current_order_vs_original_slot': 'NOT_EVALUABLE_NO_WRITTEN_CHAIN',
        'removal_withheld_intervention': 'NOT_EXECUTED_NO_BOUND_REMOVAL_OR_DUTY',
        'confirmed_words': 0, 'independent_meaning_confirmation_capacity': 0,
        'scope': 'one exposed ZL paragraph; no semantic refutation, significance or scored relation claim',
        'author_account_sha256': digest(P / 'artifacts/AUTHOR_ACCOUNT.json')
    }
    (P / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:result[k] for k in ('decision','groups','proposed_value_occurrences','unknown_occurrences','whole_record_execution')}))
if __name__ == '__main__':
    main()
