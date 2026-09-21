"""Post-result certificate replay for the preregistered all-negative stop.

No new model or extension search. Each certificate is a single fixed cell and
a permutation fixing its input while changing its output.
"""
from common import *
from wrapper_independent import relations_independent, saturation_errors
from wrappers import contradictions
import collections
import csv
import itertools


def certificate(code, groups):
    for group in groups:
        for a, b in group['pairs']:
            if a not in code or b not in code:
                continue
            x, y = code[a], code[b]
            for perm in itertools.permutations(('W', 'G', 'C')):
                rename = dict(zip(('W', 'G', 'C'), perm))
                xx, yy = rename.get(x, x), rename.get(y, y)
                if x == xx and y != yy:
                    return dict(side=group['side'], affix=group['affix'], base=a,
                                word=b, input=x, output=y, permutation=rename,
                                unchanged_input=xx, conflicting_output=yy,
                                proof='F(x)=y and F(sigma(x))=sigma(y);same input,different required outputs.')
    raise AssertionError('No single-cell certificate;do not infer one from a failed general completion.')


def main():
    checklock()
    s, g = inputs()
    precursor = read(A/'PRECURSOR.json')
    assert precursor['continue_full_worlds'] is False and precursor['survivor_count'] == 0
    cases, panel = read(A/'PREDICTIONS.json'), read(A/'PANEL.json')
    originals = read(A/'ORIGINAL_CANDIDATES.json')
    original_by_id = {r['id']: r for r in originals}
    assert len(originals) == 36 and len(cases) == 52
    assert originals == read(R/s['source_candidates']) and cases == read(R/s['source_predictions'])
    observed = {(r['original_id'], r['context_index']): r for r in precursor['rows']}
    original_rows, canonical_rows, members = [], [], []
    for original in originals:
        for index in (2, 4):
            groups = relations_independent(set(original['code']) | set(panel[index]['words']))
            proof = certificate(original['code'], groups)
            row = observed[original['id'], index]
            assert row['status'] == 'CONTRADICTED'
            assert contradictions(original['code'], groups) == row['orbit_errors']
            assert saturation_errors(original['code'], groups) == row['permutation_errors']
            original_rows.append(dict(original=original['id'], context_index=index,
                                      decision='FIXED_ORIGINAL_CELL_CONTRADICTION', certificate=proof))
    for case in cases:
        groups = relations_independent(set(case['canonical_lexicon']) | set(panel[case['context_index']]['words']))
        assert groups == case['groups']
        proof = certificate(case['canonical_lexicon'], groups)
        canonical_rows.append(dict(case=case['id'], family=case['family'], context_index=case['context_index'],
                                   variant=case['variant_index'], decision='FIXED_ORIGINAL_CELL_CONTRADICTION',
                                   full_world_solver='NOT_RUN_REGISTERED_STOP', certificate=proof))
        for member in case['members']:
            original = original_by_id[member['original_id']]
            rename = member['original_to_canonical']
            assert {w: rename.get(v, v) for w, v in original['code'].items()} == case['canonical_lexicon']
            assert case['variant_index'] in original['valid_variants']
            members.append(dict(original=original['id'], context_index=case['context_index'],
                                variant=case['variant_index'], case=case['id'],
                                decision='FIXED_ORIGINAL_CELL_CONTRADICTION',
                                full_world_solver='NOT_RUN_REGISTERED_STOP', independent_meaning_capacity=0))
    expected = [(o['id'], index, v) for o in originals for index in (2, 4) for v in o['valid_variants']]
    assert collections.Counter((r['original'], r['context_index'], r['variant']) for r in members) == collections.Counter(expected)
    assert len(original_rows) == 72 and len(members) == 312
    put('CONTRADICTION_CERTIFICATES.json', dict(original=original_rows, canonical=canonical_rows))
    with (A/'CANDIDATES.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(members[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(members)
    with (A/'ORIGINAL_PREDICTIONS.tsv').open('w', newline='') as f:
        columns = ['original', 'context_index', 'base', 'word', 'input', 'output', 'side', 'affix',
                   'unchanged_input', 'conflicting_output', 'decision']
        w = csv.DictWriter(f, fieldnames=columns, delimiter='\t', lineterminator='\n')
        w.writeheader()
        for row in original_rows:
            data = {**row, **row['certificate']}
            w.writerow({key: data[key] for key in columns})
    put('RESULT.json', dict(experiment='GDT1016', status='ALL_ORIGINALS_CONTRADICT_PARTICIPANT_NEUTRAL_UNARY_WRITER',
                           original_codes=36, joint_inventory_checks=72, compatible=0,
                           canonical_full_cases_necessarily_incompatible=52,
                           member_cases_necessarily_incompatible=312,
                           full_world_solver_calls=0, registered_stop_obeyed=True,
                           confirmed_words=0, independent_meaning_capacity=0, significance=False))
    put('VALIDATION.json', dict(status='PASS', scope='Post-result direct permutation certificates for registered precursor stop;not full-world solver replay.',
                               original_certificates=72, canonical_certificates=52, complete_membership=312,
                               normal_form_and_saturation_agree=True, full_world_models_unchanged=True,
                               completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                               confirmed_words=0))
    print('PASS:72 original certificates,52 necessary full-case contradictions,312 members;zero full-world queries.')


if __name__ == '__main__':
    main()
