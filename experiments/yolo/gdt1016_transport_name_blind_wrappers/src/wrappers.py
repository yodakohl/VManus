"""Exact inherited scope; new participant-neutral unary operation law."""
import collections
import itertools
import re

CARGO = ('W', 'G', 'C')


def relations(words):
    good = {w for w in words if re.fullmatch('[a-z]+', w)}
    groups = collections.defaultdict(set)
    for base in sorted(good):
        for out in sorted(good):
            if not 1 <= len(out) - len(base) <= 3:
                continue
            if out.endswith(base):
                groups[('L', out[:-len(base)])].add((base, out))
            if out.startswith(base):
                groups[('R', out[len(base):])].add((base, out))
    return [dict(side=s, affix=a, pairs=[list(p) for p in sorted(ps)])
            for (s, a), ps in sorted(groups.items()) if len(ps) >= 2]


def contradictions(code, groups):
    """Orbit normal form, also valid for only the known cells of a joint scope."""
    errors = []
    for group in groups:
        fixed, cargo_action = {}, None
        for base, word in group['pairs']:
            if base not in code or word not in code:
                continue
            x, y = code[base], code[word]
            reason = None
            if x not in CARGO:
                if y in CARGO:
                    reason = 'invariant_input_selects_named_cargo'
                elif x in fixed and fixed[x] != y:
                    reason = 'same_input_different_output'
                fixed[x] = y
            else:
                if y in CARGO and y != x:
                    reason = 'single_cargo_selects_different_cargo'
                action = ('IDENTITY',) if y == x else ('CONSTANT', y)
                if cargo_action is not None and action != cargo_action:
                    reason = 'inconsistent_action_on_cargo_orbit'
                cargo_action = action
            if reason:
                errors.append(dict(side=group['side'], affix=group['affix'],
                                   base=base, word=word, input=x, output=y, reason=reason))
    return errors


def impose_z3(built, groups):
    import z3
    solver, num, lex = built['solver'], built['num'], built['lexicon']
    value = lambda w: z3.IntVal(num[lex[w]]) if w in lex else built['xs'][w]
    cargo = lambda x: z3.Or([x == num[k] for k in CARGO])
    count = 0
    for group in groups:
        cells = [(value(a), value(b)) for a, b in group['pairs']]
        for x, y in cells:
            solver.add(z3.Implies(z3.Not(cargo(x)), z3.Not(cargo(y))))
            solver.add(z3.Implies(z3.And(cargo(x), cargo(y)), x == y))
            count += 2
        for (x, y), (u, v) in itertools.combinations(cells, 2):
            solver.add(z3.Implies(x == u, y == v))
            solver.add(z3.Implies(z3.And(cargo(x), cargo(u)),
                                 z3.Or(z3.And(y == x, v == u),
                                       z3.And(z3.Not(cargo(y)), y == v))))
            count += 2
    return count
