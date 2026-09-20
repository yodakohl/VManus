"""Finite complete-tree equations with shared frames on terminal arguments.

This is a hypothetical writer, not an identified manuscript parser.
"""
import bisect
import collections
import itertools
import time

INFIX = frozenset(('AND', 'IF', 'PURPOSE', 'BECAUSE'))
WRITERS = ('PREFIX_FORWARD', 'PREFIX_REVERSE', 'POSTFIX_FORWARD', 'POSTFIX_REVERSE')


def compile_trees(clauses, writer):
    assert writer in WRITERS
    prefix = writer.startswith('PREFIX')
    reverse = writer.endswith('REVERSE')
    out = []

    def walk(node, role, clause, path):
        if isinstance(node, str):
            out.append(dict(root=node, role=role, clause=clause, path=path, terminal=True))
            return
        head, *children = node
        assert 1 <= len(children) <= 3
        own = dict(root=head, role=0, clause=clause, path=path, terminal=False)
        if head in INFIX:
            assert len(children) == 2
            walk(children[0], 1, clause, path + [1])
            out.append(own)
            walk(children[1], 2, clause, path + [2])
            return
        if prefix:
            out.append(own)
        indexed = list(enumerate(children, 1))
        if reverse:
            indexed.reverse()
        for slot, child in indexed:
            walk(child, slot, clause, path + [slot])
        if not prefix:
            out.append(own)

    for clause in clauses:
        walk(clause['tree'], 0, clause['id'], [])
    return out


def form_value(event, roots, frames):
    r = event['role']
    return frames.get(f'P{r}', '') + roots[event['root']] + frames.get(f'S{r}', '')


def injective_length_bound(counts, alphabet):
    """Shortest distinct nonempty strings, without prefix-freeness."""
    if alphabet < 1:
        return None
    weights = sorted(counts.values(), reverse=True)
    cost = 0
    start = 0
    length = 1
    while start < len(weights):
        capacity = min(alphabet ** length, len(weights) - start)
        cost += length * sum(weights[start:start + capacity])
        start += capacity
        length += 1
    return cost


def necessary(events, words):
    counts = collections.Counter(x['root'] for x in events)
    n = sum(map(len, words))
    basic = dict(forms=len(events), root_types=len(counts), characters=n,
                 groups=len(words), alphabet=len(set(''.join(words))))
    bound = injective_length_bound(counts, basic['alphabet'])
    basic['injective_root_length_bound'] = bound
    if len(events) > n:
        return dict(basic, status='CONTRADICTED_NONEMPTY_LENGTH')
    if len(words) > len(events):
        return dict(basic, status='CONTRADICTED_WORD_BOUNDARIES')
    if bound is None or bound > n:
        return dict(basic, status='CONTRADICTED_INJECTIVE_LENGTH')
    pieces = {w[i:j] for w in words for i in range(len(w)) for j in range(i + 1, len(w) + 1)}
    available = {p: sum(w.count(p) for w in words) for p in pieces}
    upper = {a: min(max(map(len, words)), (n - (len(events) - k)) // k)
             for a, k in counts.items()}
    domains = {a: sorted(p for p in pieces if len(p) <= upper[a] and available[p] >= k)
               for a, k in counts.items() if k > 1}
    empty = sorted(a for a, d in domains.items() if not d)
    if empty:
        return dict(basic, status='CONTRADICTED_REPEATED_ROOT_DOMAIN', empty_roots=empty)
    role_counts = collections.Counter(x['role'] for x in events if x['role'])
    frame_domains = {f'{side}{r}': [''] + sorted(p for p in pieces
                           if len(p) < max(map(len, words)) and available[p] >= k)
                     for r, k in role_counts.items() for side in ('P', 'S')}
    return dict(basic, status='REQUIRES_FULL_EQUATION', root_upper=upper,
                root_domains=domains, frame_domains=frame_domains)


def witness(events, words, roots, frames):
    errors = []
    names = {e['root'] for e in events}
    roles = {e['role'] for e in events if e['role']}
    wanted_frames = {f'{side}{r}' for r in roles for side in ('P', 'S')}
    if set(roots) != names or any(not isinstance(v, str) or not v for v in roots.values()):
        return dict(valid=False, errors=['root_coverage_or_nonempty'])
    if len(set(roots.values())) != len(roots):
        errors.append('root_collision')
    if set(frames) != wanted_frames or any(not isinstance(v, str) for v in frames.values()):
        return dict(valid=False, errors=errors + ['frame_coverage'])
    values = [form_value(e, roots, frames) for e in events]
    text = ''.join(words)
    if ''.join(values) != text:
        errors.append('whole_equation')
    seams = list(itertools.accumulate(map(len, words)))
    ends = list(itertools.accumulate(map(len, values)))
    if not set(seams).issubset(set(ends)):
        errors.append('seam_inside_framed_form')
    counts = collections.Counter(e['root'] for e in events)
    alignment = []
    start = 0
    for i, (event, value, end) in enumerate(zip(events, values, ends)):
        wi = bisect.bisect_right(seams, start)
        alignment.append(dict(event=i, **event, value=value, start=start, end=end,
                              word_index=wi, word=words[wi] if wi < len(words) else None))
        start = end
    singleton_chars = sum(len(roots[e['root']]) for e in events if counts[e['root']] == 1)
    return dict(valid=not errors, errors=errors, alignment=alignment,
                singleton_root_characters=singleton_chars, characters=len(text),
                singleton_root_character_share=singleton_chars / len(text) if text else None,
                nonempty_frame_fields=sum(bool(v) for v in frames.values()))


def solve(events, words, seconds=30, project=False, pins=None):
    import cvc5
    from cvc5 import Kind as K
    began = time.monotonic()
    pre = necessary(events, words)
    if pre['status'] != 'REQUIRES_FULL_EQUATION':
        return dict(status=pre['status'], necessary=pre, elapsed_seconds=time.monotonic() - began)
    s = cvc5.Solver()
    s.setLogic('QF_SLIA')
    for key, value in (('produce-models', 'true'), ('incremental', 'true'), ('strings-exp', 'true')):
        s.setOption(key, value)
    def t(kind, *args):
        return s.mkTerm(kind, *args)
    def disj(terms):
        return terms[0] if len(terms) == 1 else t(K.OR, *terms)
    def concat(terms):
        return terms[0] if len(terms) == 1 else t(K.STRING_CONCAT, *terms)
    roots = {a: s.mkConst(s.getStringSort(), f'root_{i}')
             for i, a in enumerate(sorted(pre['root_upper']))}
    frames = {f: s.mkConst(s.getStringSort(), f'frame_{f}') for f in sorted(pre['frame_domains'])}
    for a, variable in roots.items():
        length = t(K.STRING_LENGTH, variable)
        s.assertFormula(t(K.GEQ, length, s.mkInteger(1)))
        s.assertFormula(t(K.LEQ, length, s.mkInteger(pre['root_upper'][a])))
        if a in pre['root_domains']:
            s.assertFormula(disj([t(K.EQUAL, variable, s.mkString(x)) for x in pre['root_domains'][a]]))
    if len(roots) > 1:
        s.assertFormula(t(K.DISTINCT, *roots.values()))
    for f, variable in frames.items():
        s.assertFormula(disj([t(K.EQUAL, variable, s.mkString(x)) for x in pre['frame_domains'][f]]))
    forms = []
    for e in events:
        r = e['role']
        forms.append(concat([frames[f'P{r}'], roots[e['root']], frames[f'S{r}']]) if r else roots[e['root']])
    s.assertFormula(t(K.EQUAL, concat(forms), s.mkString(''.join(words))))
    position = s.mkInteger(0)
    ends = []
    for i, form in enumerate(forms):
        nxt = s.mkConst(s.getIntegerSort(), f'form_end_{i}')
        s.assertFormula(t(K.EQUAL, nxt, t(K.ADD, position, t(K.STRING_LENGTH, form))))
        ends.append(nxt)
        position = nxt
    for seam in list(itertools.accumulate(map(len, words)))[:-1]:
        s.assertFormula(disj([t(K.EQUAL, end, s.mkInteger(seam)) for end in ends[:-1]]))
    for family, variables in (('roots', roots), ('frames', frames)):
        for name, value in (pins or {}).get(family, {}).items():
            s.assertFormula(t(K.EQUAL, variables[name], s.mkString(value)))
    def check(limit):
        s.setOption('tlimit-per', str(max(1, int(limit * 1000))))
        answer = s.checkSat()
        return 'SAT' if answer.isSat() else 'UNSAT' if answer.isUnsat() else 'UNKNOWN_SOLVER'
    def values():
        return ({k: s.getValue(v).getStringValue() for k, v in roots.items()},
                {k: s.getValue(v).getStringValue() for k, v in frames.items()})
    status = check(seconds)
    result = dict(status=status, necessary={k: v for k, v in pre.items()
                                          if k not in ('root_upper', 'root_domains', 'frame_domains')})
    if status == 'SAT':
        root_values, frame_values = values()
        ground = witness(events, words, root_values, frame_values)
        assert ground['valid'], ground['errors']
        result.update(roots=root_values, frames=frame_values, witness=ground, projections={})
        if project:
            counts = collections.Counter(e['root'] for e in events)
            queries = [('root:' + a, roots[a], root_values[a]) for a in sorted(roots) if counts[a] > 1]
            queries += [('frame:' + f, frames[f], frame_values[f]) for f in sorted(frames)]
            for name, variable, first in queries:
                s.push()
                s.assertFormula(t(K.NOT, t(K.EQUAL, variable, s.mkString(first))))
                q = dict(status=check(1), first_value=first)
                if q['status'] == 'SAT':
                    rr, ff = values()
                    assert witness(events, words, rr, ff)['valid']
                    q.update(roots=rr, frames=ff)
                result['projections'][name] = q
                s.pop()
    result['elapsed_seconds'] = time.monotonic() - began
    return result
