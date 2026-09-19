"""Source-only independent segment-first enumeration; never loads target cases."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parents[1]
RUNNER = E / 'src/run.py'
loader = importlib.util.spec_from_file_location('audited_run', RUNNER)
reader = importlib.util.module_from_spec(loader)
loader.loader.exec_module(reader)


def splits(word):
    def extend(position, parts):
        if position == len(word):
            if 1 <= len(parts) <= 3:
                yield tuple(parts)
            return
        if len(parts) >= 3:
            return
        for width in range(1, 4):
            if position + width <= len(word):
                yield from extend(position + width, parts + [word[position:position + width]])
    return list(extend(0, []))


def independent(words, model):
    """First split surface groups, then assign distinct segment values to atoms."""
    found = set()
    for groups in itertools.product(*(splits(word) for word in words)):
        values = sorted({value for group in groups for value in group})
        if len(values) > 6:
            continue
        if any(x.startswith(y) or y.startswith(x) for x, y in itertools.combinations(values, 2)):
            continue
        sequence_values = [value for group in groups for value in group]
        if not 1 <= len(sequence_values) <= 24:
            continue
        for atoms in itertools.permutations(range(6), len(values)):
            assignment = dict(zip(values, atoms))
            sequence = [assignment[value] for value in sequence_values]
            if 0 not in sequence or sequence[-1] != 3:
                continue
            state = 0
            for atom in sequence:
                state = reader.SPEC['models'][model][atom][state]
                if state < 0:
                    break
            if state != 0:
                continue
            key = [None] * 6
            for value, atom in assignment.items():
                key[atom] = value
            found.add(tuple(key))
    return found


def main():
    rows = []
    examples = [['a'], ['a', 'b', 'c'], ['ab', 'cd'], ['ab', 'ca', 'bd'],
                ['abca', 'bc', 'ad'], ['abc', 'def']]
    for model in ['M', 'D']:
        for words in examples:
            primary = reader.solve(dict(words=words, model=model))
            expected = independent(words, model)
            assert primary['status'] != 'UNKNOWN'
            actual = {tuple(witness['key']) for witness in primary['witnesses']}
            assert actual == expected, (model, words, len(actual), len(expected))
            rows.append(dict(model=model, words=words, status=primary['status'],
                             primary_keys=len(actual), independent_keys=len(expected),
                             exact_key_set_match=True))
    boundaries = []
    for count in [24, 25]:
        words = ['a'] * (count - 3) + ['b', 'c', 'a']
        result = reader.solve(dict(words=words, model='M'))
        assert (len(result['witnesses']) > 0) == (count == 24)
        boundaries.append(dict(groups=count, status=result['status'], witnesses=len(result['witnesses'])))
    old_cap = reader.SPEC['max_witnesses']
    try:
        reader.SPEC['max_witnesses'] = 1
        capped = reader.solve(dict(words=['ab', 'cd'], model='M'))
        assert capped['status'] == 'UNKNOWN' and capped['witnesses']
        assert all(reader.replay(['ab', 'cd'], witness, 'M') for witness in capped['witnesses'])
    finally:
        reader.SPEC['max_witnesses'] = old_cap
    receipt = dict(
        status='PASS_SOURCE_ONLY_SYNTHETIC_CONTROLS',
        runner_sha256=hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
        specification_sha256=hashlib.sha256((E / 'src/SPEC.json').read_bytes()).hexdigest(),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cases=rows, total_matched_keys=sum(row['primary_keys'] for row in rows),
        atom_group_boundaries=boundaries,
        interrupted_trace=dict(status=capped['status'], witnesses=len(capped['witnesses']), replay=True),
        scope='Synthetic controls only. Independent segmentation and assignment enumeration uses the same declared transition specification; it does not independently establish the source meanings. No target cases, results, joint-pair enumeration or data capacity were read. Finite controls support the code audit but are not a proof of all target search outcomes.')
    (E / 'artifacts/SEGMENTATION_CONTROLS.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], cases=len(rows), exact_keys=receipt['total_matched_keys'])))


if __name__ == '__main__':
    main()
