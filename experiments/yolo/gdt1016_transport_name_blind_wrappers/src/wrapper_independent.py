"""Independent trimmed inventory and total-function/permutation equations."""
import collections
import itertools
from cvc5 import pythonic as c

CARGO = ('W', 'G', 'C')


def relations_independent(words):
    vocab = {w for w in words if w and all('a' <= x <= 'z' for x in w)}
    d = collections.defaultdict(set)
    for whole in vocab:
        for n in (1, 2, 3):
            if len(whole) <= n:
                continue
            if whole[n:] in vocab:
                d[('L', whole[:n])].add((whole[n:], whole))
            if whole[:-n] in vocab:
                d[('R', whole[-n:])].add((whole[:-n], whole))
    return [dict(side=k[0], affix=k[1], pairs=[list(p) for p in sorted(v)])
            for k, v in sorted(d.items()) if len(v) > 1]


def saturation_errors(code, groups):
    """Transport each supplied cell by every permutation, including stabilizers."""
    failures = []
    for group in groups:
        table = {}
        for a, b in group['pairs']:
            if a not in code or b not in code:
                continue
            for perm in itertools.permutations(CARGO):
                rename = dict(zip(CARGO, perm))
                x = rename.get(code[a], code[a])
                y = rename.get(code[b], code[b])
                if x in table and table[x] != y:
                    failures.append(dict(side=group['side'], affix=group['affix'],
                                         base=a, word=b, input=x, previous=table[x], output=y))
                table[x] = y
    return failures


def constrain_groups(solver, groups, lex, xs, code):
    for group in groups:
        f = c.Function('equivariant_' + group['side'] + '_' + group['affix'], c.IntSort(), c.IntSort())
        for x in code.values():
            solver.add(f(x) >= 0, f(x) < len(code))
        for perm in itertools.permutations(CARGO):
            rename = dict(zip(CARGO, perm))
            def move(value):
                return c.If(value == code['W'], code[rename['W']],
                            c.If(value == code['G'], code[rename['G']],
                                 c.If(value == code['C'], code[rename['C']], value)))
            for symbol, x in code.items():
                solver.add(f(code[rename.get(symbol, symbol)]) == move(f(x)))
        def value(w):
            return c.IntVal(code[lex[w]]) if w in lex else xs[w]
        for a, b in group['pairs']:
            solver.add(f(value(a)) == value(b))


def constrain(solver, raw, lex, xs, code):
    constrain_groups(solver, relations_independent(set(raw) | set(lex)), lex, xs, code)
