#!/usr/bin/env python3
"""Independent finite cut oracle for small complete role-form equations."""
import itertools
import json
from pathlib import Path
from pattern import solve, factor, replay
from reverse import check

E = Path(__file__).resolve().parents[1]


def brute(events, words):
    text = ''.join(words)
    seams = set(itertools.accumulate(map(len, words))) - {len(text)}
    if len(text) < len(events):
        return False
    for cuts in itertools.combinations(range(1, len(text)), len(events) - 1):
        if not seams.issubset(cuts):
            continue
        starts = (0,) + cuts
        ends = cuts + (len(text),)
        values = {}
        for e, a, b in zip(events, starts, ends):
            k = (e['root'], e['role'])
            if k in values and values[k] != text[a:b]:
                break
            values[k] = text[a:b]
        else:
            return True
    return False


def main():
    count = 0
    for size in range(1, 5):
        for stream in itertools.product(('A', 'B'), repeat=size):
            events = [dict(root=x, role=0) for x in stream]
            for length in range(1, 5):
                for chars in itertools.product('ab', repeat=length):
                    text = ''.join(chars)
                    for mask in range(1 << (length - 1)):
                        starts = [0] + [i for i in range(1, length) if mask & (1 << (i - 1))]
                        ends = starts[1:] + [length]
                        words = [text[a:b] for a, b in zip(starts, ends)]
                        expected = brute(events, words)
                        got = solve(events, words, seconds=1)
                        assert (got['status'] == 'COMPLETE_ROLE_FORM_PATTERN_WITNESS') == expected
                        assert (check(events, words)['status'] == 'REVERSE_WITNESS') == expected
                        count += 1
    events = [dict(root='A', role=1), dict(root='B', role=2), dict(root='A', role=2), dict(root='B', role=1)]
    values = {('A',1):'pa', ('A',2):'qa', ('B',1):'pb', ('B',2):'qb'}
    words = ['paqb', 'qapb']
    replay(events, words, values)
    f = factor(events, words, values)
    assert f['status'] == 'FULL_ORIGINAL_CODE_WITNESS'
    bad = [dict(root='A', role=0), dict(root='B', role=0)]
    relaxed = solve(bad, ['aa'])
    assert relaxed['status'] == 'COMPLETE_ROLE_FORM_PATTERN_WITNESS'
    assert relaxed['factorization']['status'] == 'NO_FACTOR_FOR_THIS_WITNESS'
    assert solve([dict(root='A', role=1)]*2, ['p','apa'])['status'] == 'NO_COMPLETE_ROLE_FORM_PATTERN'
    source = json.loads((E.parent / 'gdt990_smaragdina_complete_role_frames/src/SOURCE.json').read_text())
    whole = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for variant, spec in source['variants'].items():
        for writer, stream in spec['streams'].items():
            roots = {name: 'a' + alphabet[i // 26] + alphabet[i % 26] for i, name in enumerate(sorted(spec['counts']))}
            words = [('pqr'[e['role'] - 1] + roots[e['root']] + 'uvw'[e['role'] - 1]) if e['role'] else roots[e['root']] for e in stream]
            got = solve(stream, words, seconds=1)
            assert got['status'] == 'COMPLETE_ROLE_FORM_PATTERN_WITNESS'
            assert got['factorization']['status'] == 'FULL_ORIGINAL_CODE_WITNESS'
            assert check(stream, words)['status'] == 'REVERSE_WITNESS'
            seen = set()
            for i, e in enumerate(stream):
                k = (e['root'], e['role'])
                if k in seen:
                    bad_words = list(words)
                    bad_words[i] += 'z'
                    break
                seen.add(k)
            assert solve(stream, bad_words, seconds=1)['status'] == 'NO_COMPLETE_ROLE_FORM_PATTERN'
            assert check(stream, bad_words)['status'] == 'REVERSE_EXHAUSTED'
            whole.append(dict(variant=variant, writer=writer, positive=True, changed_repeat_rejected=True))
    result = dict(status='PASS', exhaustive_small_cases=count, full_frame_fixture=f,
                  full_source_controls=whole,
                  relaxed_collision_retained=True, seam_crossing_rejected=True,
                  scope='engineering controls only; no target or meaning validation')
    (E / 'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
