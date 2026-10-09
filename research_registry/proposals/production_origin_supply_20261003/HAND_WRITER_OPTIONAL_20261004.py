#!/usr/bin/env python3
"""Two globally oriented optional-ligature writers over abstract motif names.

These are constructed writing systems, not recovered Voynich sound values.
"""
import hashlib
import itertools
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
G0 = BASE / 'HAND_WRITER_NATIVE_G0_20261004.json'
G0_SHA = '04f272e17ca6863a730fb66b869079c667115fff938cd594415a41c466215c0b'
HIGH = frozenset('ktpf')


def read(surface, direction, units):
    """Deterministic inverse. Never varies orientation within one model."""
    assert direction in ('BH', 'HB')
    out = []
    pos = 0
    while pos < len(surface):
        if (surface[pos] == 'c' and pos + 2 < len(surface)
                and surface[pos + 1] in HIGH and surface[pos + 2] == 'h'):
            high = surface[pos + 1]
            out.extend(('ch', high) if direction == 'BH' else (high, 'ch'))
            pos += 3
        elif surface[pos:pos + 2] in ('ch', 'sh'):
            out.append(surface[pos:pos + 2])
            pos += 2
        else:
            if surface[pos] not in units:
                raise ValueError('outside the fixed demonstration alphabet')
            out.append(surface[pos])
            pos += 1
    assert all(u in units for u in out)
    return tuple(out)


def write(sequence, direction):
    """Enumerate every allowed per-pair choice, including never joining."""
    assert direction in ('BH', 'HB')
    if not sequence:
        yield ''
        return
    for tail in write(sequence[1:], direction):
        yield sequence[0] + tail
    if len(sequence) < 2:
        return
    if direction == 'BH' and sequence[0] == 'ch' and sequence[1] in HIGH:
        high = sequence[1]
    elif direction == 'HB' and sequence[0] in HIGH and sequence[1] == 'ch':
        high = sequence[0]
    else:
        return
    for tail in write(sequence[2:], direction):
        yield 'c' + high + 'h' + tail


def main():
    assert hashlib.sha256(G0.read_bytes()).hexdigest() == G0_SHA
    units = tuple(sorted(json.loads(G0.read_text())['motif_recipes']))
    assert len(units) == 16 and 'c' not in units and 'h' not in units
    synthetic = {}
    for direction in ('BH', 'HB'):
        n_inputs = n_writings = 0
        owners = {}
        for n in range(4):
            for sequence in itertools.product(units, repeat=n):
                n_inputs += 1
                alternatives = list(write(sequence, direction))
                assert len(alternatives) == len(set(alternatives))
                for surface in alternatives:
                    assert read(surface, direction, units) == sequence
                    assert surface not in owners or owners[surface] == sequence
                    owners[surface] = sequence
                    n_writings += 1
        synthetic[direction] = {'input_sequences_through_length3': n_inputs,
                                'all_allowed_writings_checked': n_writings,
                                'decode_errors': 0, 'cross_input_collisions': 0}

    original = json.loads((BASE / 'HAND_WRITER_NATIVE_ACCOUNT_20261004.json').read_text())
    records = []
    for row in original['records']:
        item = {key: row[key] for key in ('edition', 'locus', 'source_group_index',
                                        'ivtff_group_raw', 'left_separator', 'right_separator')}
        for direction in ('BH', 'HB'):
            sequence = read(row['ivtff_group_raw'], direction, units)
            alternatives = sorted(write(sequence, direction))
            assert row['ivtff_group_raw'] in alternatives
            item[direction] = {'abstract_input': sequence,
                               'allowed_spellings': alternatives,
                               'original_is_allowed': True}
        records.append(item)
    assert len(records) == 53
    report = {'status': 'CONSTRUCTED_OPTIONAL_WRITERS_NO_RECOVERED_KEY',
              'alphabet': units, 'G0_sha256': G0_SHA,
              'rules': {'BH': 'optional CH then HIGH -> embedded HIGH in CH; inverse always CH,HIGH',
                        'HB': 'optional HIGH then CH -> embedded HIGH in CH; inverse always HIGH,CH'},
              'synthetic_verification': synthetic, 'records': records,
              'claim_ceiling': 'Two separately fixed reversible writers; no orientation selected. '
                               'Native two-line representation is fitted descriptive coverage, '
                               'not independent recovery, a glyph recognizer, word identity or translation.'}
    (BASE / 'HAND_WRITER_OPTIONAL_RESULT_20261004.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(synthetic, indent=2))
    for surface in ('cthor', 'ckhey', 'chky', 'ckhy'):
        print(surface, {d: read(surface, d, units) for d in ('BH', 'HB')})
    print('All53 original reader/group records preserved in each separate model.')


if __name__ == '__main__':
    main()
