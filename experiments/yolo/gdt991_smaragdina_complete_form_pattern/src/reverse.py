"""Separate reverse-direction pattern construction using the standard re engine."""
import itertools
import re


def check(events, words):
    names = {}
    pattern = []
    for i, entry in enumerate(reversed(events)):
        symbol = (entry['root'], entry['role'])
        if symbol not in names:
            name = 'x' + str(len(names))
            names[symbol] = name
            piece = '(?P<' + name + '>[^|]+)'
        else:
            piece = '(?P=' + names[symbol] + ')'
        left = len(events) - i
        capacity = '(?=(?:[^|]*[|]){0,' + str(left - 1) + '}[^|]*\\Z)'
        capacity += '(?=(?:[^|][|]*){' + str(left) + '})'
        pattern.append(capacity + piece)
    target = '|'.join(w[::-1] for w in reversed(words))
    match = re.fullmatch(r'\|?'.join(pattern), target)
    if match is None:
        return dict(status='REVERSE_EXHAUSTED')
    dictionary = {k: match.group(n)[::-1] for k, n in names.items()}
    pieces = [dictionary[(e['root'], e['role'])] for e in events]
    assert ''.join(pieces) == ''.join(words)
    boundaries = set(itertools.accumulate(map(len, pieces)))
    assert set(itertools.accumulate(map(len, words))).issubset(boundaries)
    return dict(status='REVERSE_WITNESS', forms=[dict(root=n, role=r, value=v) for (n, r), v in dictionary.items()])
