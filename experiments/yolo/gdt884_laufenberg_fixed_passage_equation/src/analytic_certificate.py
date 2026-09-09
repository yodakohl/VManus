#!/usr/bin/env python3
"""Post-search proof for the unchanged frozen GDT884 word equations.

This is a necessary-condition certificate, not another decoder search.
Every square and every split of its root is covered. A fixed nonempty image
must occur disjointly as often as its source code; a unique target letter
must be emitted by a globally singleton source code.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

E = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def max_disjoint(text, word):
    assert word
    count = offset = 0
    while True:
        found = text.find(word, offset)
        if found < 0:
            return count
        count += 1
        offset = found + len(word)


def certify(groups, target):
    assert groups[1]['codes'] == groups[2]['codes'] == ['A1', 'C1']
    source = [c for g in groups for c in g['codes']]
    frequency = Counter(source)
    rest_frequency = Counter(c for g in groups[3:] for c in g['codes'])
    assert target.count('x') == 1
    x_position = target.index('x')
    x_suffix = target[x_position + 1:]
    x_available = Counter(x_suffix)
    candidates = []
    survivors = []
    # The first group and every group after the repeated pair are nonempty.
    min_suffix = len(groups) - 3
    for start in range(1, len(target)):
        for width in range(1, (len(target) - start - min_suffix) // 2 + 1):
            word = target[start:start + width]
            if word != target[start + width:start + 2 * width]:
                continue
            suffix = target[start + 2 * width:]
            for split in range(width + 1):
                images = {'A1': word[:split], 'C1': word[split:]}
                item = dict(start=start, width=width, split=split, **images)
                for code, image in images.items():
                    if not image:
                        continue
                    available = max_disjoint(suffix, image)
                    required = rest_frequency[code]
                    if available < required:
                        item.update(reason='substring_capacity', code=code,
                                    image=image, required=required, available=available)
                        break
                else:
                    allocations = []
                    for position, code in enumerate(source):
                        if frequency[code] != 1:
                            continue
                        required = Counter(''.join(images.get(c, '') for c in source[position + 1:]))
                        missing = required - x_available
                        if not missing:
                            survivors.append(dict(**item, singleton_position=position))
                            continue
                        letter = sorted(missing)[0]
                        allocations.append(dict(source_position=position, code=code,
                                                letter=letter, required=required[letter],
                                                available=x_available[letter]))
                    assert len(allocations) == sum(n == 1 for n in frequency.values())
                    item.update(reason='unique_x_tail', x_position=x_position,
                                x_suffix=x_suffix, allocations=allocations)
                candidates.append(item)
    assert not survivors
    return dict(status='UNSAT_ANALYTIC', target_length=len(target),
                source_units=len(source), source_types=len(frequency),
                square_split_count=len(candidates),
                substring_rejected=sum(c['reason'] == 'substring_capacity' for c in candidates),
                unique_x_rejected=sum(c['reason'] == 'unique_x_tail' for c in candidates),
                survivors=survivors, candidates=candidates)


def main():
    input_path = E / 'artifacts/INPUT.json'
    data = json.loads(input_path.read_text())
    cases = [dict(edition=edition, variant=v['id'], **certify(groups, v['text']))
             for edition, groups in sorted(data['editions'].items())
             for v in data['source_variants']]
    result = dict(status='UNSAT_ANALYTIC', input_sha256=sha(input_path),
                  base_result_sha256=sha(E / 'artifacts/RESULT.json'),
                  method='post-search necessary conditions; frozen solver unchanged',
                  cases=cases)
    (E / 'artifacts/ANALYTIC_CERTIFICATE.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          square_splits=sum(c['square_split_count'] for c in cases),
                          unique_x_rejected=sum(c['unique_x_rejected'] for c in cases))))


if __name__ == '__main__':
    main()
