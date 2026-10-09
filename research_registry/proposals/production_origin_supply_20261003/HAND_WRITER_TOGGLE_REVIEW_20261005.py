#!/usr/bin/env python3
"""Conditional size check plus two invented writers; no manuscript key fit."""
import hashlib
import itertools
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PAYLOADS = tuple('g' + str(i) for i in range(1, 14))
SYMBOLS = ('T',) + PAYLOADS


def write(plain, persistent):
    mode = 0
    out = []
    for char in plain:
        number = ord(char) - ord('A')
        assert 0 <= number < 26
        bank, column = divmod(number, 13)
        if persistent:
            if bank != mode:
                out.append('T')
                mode = bank
        elif bank:
            out.append('T')
        out.append(PAYLOADS[column])
    return tuple(out)


def read(surface, persistent):
    if not surface:
        return None
    mode, pending, out = 0, False, []
    for sign in surface:
        if sign == 'T':
            if pending:
                return None
            mode = 1 - mode if persistent else 1
            pending = True
        else:
            if sign not in PAYLOADS:
                return None
            out.append(chr(ord('A') + 13 * mode + PAYLOADS.index(sign)))
            pending = False
            if not persistent:
                mode = 0
    return None if pending else ''.join(out)


def legal_by_blocks(surface):
    """Independent recognition as one or more T?G blocks."""
    if not surface:
        return False
    i = 0
    while i < len(surface):
        if surface[i] == 'T':
            i += 1
        if i == len(surface) or surface[i] not in PAYLOADS:
            return False
        i += 1
    return True


def main():
    cp = BASE / 'HAND_WRITER_TOGGLE_REVIEW_CONTRACT_20261005.json'
    contract = json.loads(cp.read_text())
    for name, expected in contract['inputs'].items():
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == expected
    source = json.loads((BASE / 'HAND_WRITER_NATIVE_ACCOUNT_20261004.json').read_text())
    counts = []
    for reader in ('ZL3b', 'IT2a', 'RF1b'):
        witnesses, kept, omitted = {}, [], []
        for row in source['records']:
            if row['edition'] != reader:
                continue
            assert not row['locus'].startswith('f84')
            ref = {'locus': row['locus'], 'group': row['source_group_index'], 'raw': row['ivtff_group_raw']}
            if row['left_separator'] not in {'LINE_START', 'DEFINITE_SPACE'} or row['right_separator'] not in {'LINE_END', 'DEFINITE_SPACE'}:
                omitted.append(ref)
                continue
            units = row['G1_post_application_extension']
            assert all(u['resolved_symbolically'] for u in units)
            assert ''.join(u['surface'] for u in units) == row['ivtff_group_raw']
            kept.append(dict(ref, units=[u['surface'] for u in units]))
            for unit in units:
                witnesses.setdefault(unit['surface'], ref)
        n = len(witnesses)
        counts.append({'reader': reader, 'eligible_groups': len(kept), 'excluded': omitted,
                       'observed_atomic_surface_types': n, 'available_output_signs': 14,
                       'excess': n - 14, 'fixed_size_possible': n <= 14,
                       'one_existing_witness_per_type': witnesses})
    checked = legal = different = 0
    owners = {True: {}, False: {}}
    for n in range(4):
        for surface in itertools.product(SYMBOLS, repeat=n):
            checked += 1
            expected = legal_by_blocks(surface)
            answers = [read(surface, m) for m in (True, False)]
            assert all((p is not None) == expected for p in answers)
            if not expected:
                continue
            legal += 1
            different += answers[0] != answers[1]
            assert len(answers[0]) == len(answers[1])
            for mode, plain in zip((True, False), answers):
                assert write(plain, mode) == surface
                assert plain not in owners[mode] or owners[mode][plain] == surface
                owners[mode][plain] = surface
    witness = ('T', 'g1', 'g2', 'g3')
    readings = {'persistent': read(witness, True), 'one_payload_only': read(witness, False)}
    assert readings == {'persistent': 'NOP', 'one_payload_only': 'NBC'}
    result = {'status': 'FIXED_G1_SIZE_CONTRADICTED_SCOPE_NOT_IDENTIFIED_BY_SURFACE_LEGALITY',
              'contract_sha256': hashlib.sha256(cp.read_bytes()).hexdigest(),
              'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'fixed_size_check': counts,
              'construction_check': {'surface_strings_including_empty_through_length3': checked,
                                     'legal_nonempty': legal, 'differently_decoded_among_checked': different,
                                     'grammar_and_roundtrips': 'PASS', 'example_surface': witness,
                                     'example_readings': readings,
                                     'all_length_reason': 'Every nonempty T?G block sequence has a unique persistent-bank reading and a unique per-payload-bank reading; each inverse reencodes it exactly. Both reject precisely empty strings, adjacent T and trailing T over the fixed alphabet.'},
              'limits': ['The source alphabet and values in the example are invented, not Voynich assignments.',
                         'G1 surface-as-atomic-code binding is conditional; different native atomizations untested.',
                         'No larger table, candidate native switch, source language or corpus decoder fitted.',
                         'Equal legality does not imply equal decoded character statistics under language constraints.',
                         'Readers remain separate; two exposed lines, no independent confirmation.']}
    (BASE / 'HAND_WRITER_TOGGLE_REVIEW_RESULT_20261005.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for row in counts:
        print(row['reader'], row['observed_atomic_surface_types'], '>14', not row['fixed_size_possible'])
    print(result['construction_check'])


if __name__ == '__main__':
    main()
