#!/usr/bin/env python3
"""Bounded checks of constructed model support and a declared motif binding."""
import hashlib
import importlib.util
import itertools
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    pins = json.loads((BASE / 'HAND_WRITER_IDENTIFIABILITY_INPUTS_20261004.json').read_text())
    paths = {
        'g2_source_sha256': 'HAND_WRITER_OPTIONAL_20261004.py',
        'idea929_sha256': 'HAND_WRITER_FOLDED_COORDINATES_RAW_20261004.json',
        'native_account_sha256': 'HAND_WRITER_NATIVE_ACCOUNT_20261004.json',
    }
    for key, path in paths.items():
        assert hashlib.sha256((BASE / path).read_bytes()).hexdigest() == pins[key]
    spec = importlib.util.spec_from_file_location('g2_frozen', BASE / paths['g2_source_sha256'])
    g2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g2)
    units = tuple(sorted(json.loads((BASE / 'HAND_WRITER_NATIVE_G0_20261004.json').read_text())['motif_recipes']))
    surface_units = units + tuple('c' + h + 'h' for h in sorted(g2.HIGH))
    assert len(set(surface_units)) == 20
    checked = 0
    for n in range(4):
        for pieces in itertools.product(surface_units, repeat=n):
            surface = ''.join(pieces)
            a = g2.read(surface, 'BH', units)
            b = g2.read(surface, 'HB', units)
            assert len(a) == len(b) and Counter(a) == Counter(b)
            for direction, decoded in [('BH', a), ('HB', b)]:
                assert surface in set(g2.write(decoded, direction))
            checked += 1
    assert checked == 8421
    alias_witness = {
        direction: {w: g2.read(w, direction, units) for w in ('ckhy', 'chky', 'kchy')}
        for direction in ('BH', 'HB')
    }
    assert alias_witness['BH']['ckhy'] == alias_witness['BH']['chky']
    assert alias_witness['BH']['ckhy'] != alias_witness['BH']['kchy']
    assert alias_witness['HB']['ckhy'] == alias_witness['HB']['kchy']
    assert alias_witness['HB']['ckhy'] != alias_witness['HB']['chky']

    source = json.loads((BASE / paths['native_account_sha256']).read_text())
    witness_rows = [r for r in source['records']
                    if r['locus'] == 'f25v.1' and r['ivtff_group_raw'] == 'sos']
    assert {r['edition'] for r in witness_rows} == {'ZL3b', 'IT2a', 'RF1b'}
    fold_cases = []
    for row in witness_rows:
        assignments = []
        for choices in itertools.product('RC', repeat=2):
            table = dict(zip(('s', 'o'), choices))
            classes = ''.join(table[x] for x in 'sos')
            valid = (len(classes) % 2 == 0 and len(classes) > 0
                     and classes == 'R' * (len(classes) // 2) + 'C' * (len(classes) // 2))
            assignments.append({'classes': classes, 'valid': valid})
        boundary_ok = (row['left_separator'] in {'DEFINITE_SPACE', 'LINE_START'}
                       and row['right_separator'] in {'DEFINITE_SPACE', 'LINE_END'})
        fold_cases.append({key: row[key] for key in ('edition', 'locus', 'source_group_index',
                                                   'ivtff_group_raw', 'left_separator', 'right_separator')}
                          | {'boundary_eligible': boundary_ok,
                             'fixed_motifs': ['s', 'o', 's'],
                             'all_class_assignments': assignments,
                             'compatible_assignments': sum(a['valid'] for a in assignments)})
    assert {c['edition'] for c in fold_cases if c['boundary_eligible']} == {'IT2a', 'RF1b'}
    assert all(c['compatible_assignments'] == 0 for c in fold_cases)
    out = {
        'status': 'CONSTRUCTION_SUPPORT_EQUAL_ALIAS_PARTITIONS_DIFFER',
        'model_support': {
            'all_length_argument': 'Both accept every nonempty sequence of the same20 surface motifs. '
                                   'Read each composite in the chosen order and choose precisely the '
                                   'observed joins when rewriting. Both reproduce any such surface.',
            'finite_check_including_empty': checked,
            'same_latent_length_and_motif_counts': True,
            'same_alias_partition': False,
            'constructed_alias_witness_not_an_occurrence_claim': alias_witness,
            'ceiling': 'No source-language or writer-choice distribution is specified. '
                       'Equal support does not imply equality of all possible probabilistic models. '
                       'Bound word identity, linguistic restrictions or justified choice laws could distinguish them.'},
        'idea929': {
            'status': 'F25V_FIXED_MOTIF_BINDING_CONTRADICTED_UNBOUND_NATIVE_CODE_UNTESTED',
            'border_argument': 'A nonempty R^n C^n string has no nonempty proper border: '
                               'a shared prefix/suffix would either start the suffix in C or force '
                               'the shared prefix to contain C before the suffix restarts in R.',
            'rows': fold_cases,
            'native_limit': 'The equal s motifs and complete-group binding are inherited from the '
                            'declared f25v reading; no independent atomic inventory or sound identity established. '
                            'IT/RF are alternate readings of the same one manuscript locus.'},
        'access': 'No new transcription query; only pinned exposed two-line account and same admitted crop.'}
    (BASE / 'HAND_WRITER_IDENTIFIABILITY_RESULT_20261004.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print('G2 support check:', checked, 'constructed surfaces; both accept all; lengths/counts equal.')
    print('Alias equivalence differs by orientation; no general model equivalence claimed.')
    print('IDEA929:', [(r['edition'], r['boundary_eligible'], r['compatible_assignments']) for r in fold_cases])


if __name__ == '__main__':
    main()
