"""Exact finite local factorization, without target access at import."""
from itertools import permutations

ORDERS = [''.join(p) for p in permutations('RPT')]
LAYOUTS = ['ROW_MAJOR', 'COLUMN_MAJOR']

def matrix(words, layout):
    assert len(words) == 18
    return [[words[r*3+c if layout == 'ROW_MAJOR' else c*6+r]
             for c in range(3)] for r in range(6)]

def length_failure(m):
    for r in range(len(m)):
        for c in range(len(m[0])):
            expected = len(m[r][0])+len(m[0][c])-len(m[0][0])
            if len(m[r][c]) != expected:
                return dict(row=r, column=c, observed=len(m[r][c]), expected=expected)
    return None

def strip_unknown(word, order, unknown, known):
    i = order.index(unknown)
    a = ''.join(known[k] for k in order[:i])
    b = ''.join(known[k] for k in order[i+1:])
    if len(word) < len(a)+len(b) or not word.startswith(a) or not word.endswith(b):
        return None
    return word[len(a):len(word)-len(b) if b else len(word)]

def factor(m, order):
    found = []
    w = m[0][0]
    for a in range(len(w)+1):
        for b in range(a,len(w)+1):
            k = dict(zip(order, (w[:a],w[a:b],w[b:])))
            if not k['R']:
                continue
            roots = [strip_unknown(m[0][c],order,'R',k) for c in range(len(m[0]))]
            persons = [strip_unknown(m[r][0],order,'P',k) for r in range(len(m))]
            if None in roots or None in persons or '' in roots:
                continue
            if len(set(roots)) != len(m[0]) or len(set(persons)) != len(m):
                continue
            if all(m[r][c] == ''.join(dict(R=roots[c],P=persons[r],T=k['T'])[v]
                                     for v in order) for r in range(len(m)) for c in range(len(m[0]))):
                found.append(dict(order=order, roots=roots, persons=persons, tense=k['T']))
    return found

def signature(w):
    return (w['panel'],w['layout'],w['order'],tuple(w['roots']),tuple(w['persons']))
