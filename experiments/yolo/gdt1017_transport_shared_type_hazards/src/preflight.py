"""Synthetic union/masking/complete-world fixtures; no new target-law query."""
from common import *
from joint import apply_union
from worker import bounded
import itertools
import concurrent.futures
import collections

NAMES = ('C', 'G', 'W')
PAIRS = list(itertools.combinations(NAMES, 2))
STAR = {('C', 'G'), ('C', 'W')}
VARIANT = dict(exclude='EXCLUDING', copy='FIRST', other='OTHER', first='FIRST', there='GOAL')


def subsets(items):
    return [list(x for i, x in enumerate(items) if mask & (1 << i)) for mask in range(1 << len(items))]


def paragraph(order, hazards, copy_mode=None):
    moves = ([order[0]] if len(order) == 1 else [order[0], None, order[1]] if len(order) == 2
             else [order[0], None, order[1], order[0], order[2], None, order[0]])
    clauses = [('INITIAL', ['INIT', 'CARGOS', 'COLOC', 'M', 'HOME']),
               ('GOAL', ['GOAL', 'FAR_BANK', 'WITHOUT_HARM', 'HARM']),
               ('SAFETY', ['UNSAFE', 'PAIRS', 'FORBIDDEN', 'WHEN', 'WITHOUT_AGENT', 'M']),
               ('CAPACITY', ['AT_MOST_ONE', 'BESIDES', 'M', 'EXAMPLE', order[0]])]
    for cargo in moves:
        clauses.append(('ALONE', ['RETURN', 'ALONE']) if cargo is None else ('FERRY', ['FERRY', cargo]))
    for a, b in hazards:
        clauses.append(('PAIR', [a, 'PAIRED_WITH', 'UNATTENDED', b, 'WOULD_BE', 'UNSAFE']))
    if copy_mode:
        assert hazards == [('C', 'W')] and len(order) == 3
        clauses.append(('COPY', ['LIKEWISE', 'OTHER_CARGO']))
    clauses.append(('CONCLUSION', ['THUS', 'ALL', 'UNHARMED', 'THERE', 'ATTENDED_BY', 'M']))
    parsed, words = [], []
    for kind, symbols in clauses:
        start = len(words)
        words.extend(symbols)
        parsed.append(dict(start=start, end=len(words), kind=kind, symbols=symbols))
    return dict(words=words), {w: w for w in words}, parsed, moves


def literal_expected(order, moves, local_edges):
    # Independent explicit bit-state walk; no use of either model or union checker.
    union = STAR | {tuple(sorted(e)) for e in local_edges}
    if ('G', 'W') in union:
        return False  # Four first-load triangle proof is separately retained.
    position = {x: False for x in order}
    agent = False
    for cargo in moves:
        if cargo is not None:
            assert position[cargo] == agent
        agent = not agent
        if cargo is not None:
            position[cargo] = agent
        for a, b in union:
            if a in position and b in position and position[a] == position[b] != agent:
                return False
    return agent and all(position.values())


def job(j):
    payload = dict(paragraph=j['paragraph'], lexicon=j['lexicon'], variant=j['variant'], fixed_layout=j['parse'])
    one, two = bounded('primary', payload), bounded('independent', payload)
    expected = 'sat' if j['expected'] else 'unsat'
    assert one['status'] == two['status'] == expected, (j['id'], one, two, expected)
    args = dict(original_parse=j['original_parse'], parse=j['parse'], variant=j['variant'])
    a, b = bounded('joint', args), bounded('joint', dict(**args, independent=True))
    assert a['status'] == b['status'] == 'COMPLETE', (j['id'], a, b)
    assert a['result'] == b['result'], j['id']
    assert (a['result']['status'] == 'COHERENT') == j['expected'], j['id']
    return dict(id=j['id'], expected=expected, primary=one['status'], independent=two['status'], direct_union=a['result']['status'])


def main():
    s, g = inputs()
    mask_rows = []
    for n in (1, 2, 3):
        for present in itertools.combinations(NAMES, n):
            for graph in subsets(PAIRS):
                for bits in itertools.product((False, True), repeat=n+1):
                    positions = dict(zip(('M', *present), ('R' if bit else 'L' for bit in bits)))
                    expected = [list((a, b)) for a, b in graph if a in present and b in present
                                and positions[a] == positions[b] != positions['M']]
                    local = dict(cargo=list(present), hazards=[], paths=[dict(trace=[dict(clause='S', positions=positions)], without_safety_consistent=True)])
                    a = apply_union(local, [list(p) for p in graph], s)
                    b = apply_union(local, [list(p) for p in graph], s, True)
                    assert a == b
                    assert [x['pair'] for x in a['paths'][0]['safety_violations']] == expected
                    mask_rows.append(dict(present=present, graph=graph, bits=bits, violations=expected))
    assert len(mask_rows) == 416
    original = paragraph(('C', 'G', 'W'), [('C', 'G'), ('C', 'W')])[2]
    jobs = []
    for n in (1, 2, 3):
        for order in itertools.permutations(NAMES, n):
            for graph in subsets(list(itertools.combinations(sorted(order), 2))):
                p, lex, parsed, moves = paragraph(order, graph)
                jobs.append(dict(id=f'F{len(jobs):03}', paragraph=p, lexicon=lex, parse=parsed,
                                 original_parse=original, variant=VARIANT,
                                 expected=literal_expected(order, moves, graph)))
    for order in itertools.permutations(NAMES):
        for mode in ('FIRST', 'SECOND'):
            p, lex, parsed, moves = paragraph(order, [('C', 'W')], mode)
            graph = [('C', 'W'), ('G', 'W') if mode == 'FIRST' else ('C', 'G')]
            jobs.append(dict(id=f'F{len(jobs):03}', paragraph=p, lexicon=lex, parse=parsed,
                             original_parse=original, variant=dict(VARIANT, copy=mode),
                             expected=literal_expected(order, moves, graph)))
    assert len(jobs) == 75
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:
        rows = list(pool.map(job, jobs))
    put('PREFLIGHT.json', dict(status='PASS', mask_fixtures=mask_rows, synthetic_complete_worlds=rows,
                               full_fixture_inputs=jobs, counts=dict(collections.Counter(r['expected'] for r in rows)),
                               target_union_queries=0, old_semantic_fixtures='1152 inherited from GDT1013',
                               completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    print(json.dumps(dict(status='PASS', masks=len(mask_rows), complete_fixtures=len(rows), counts=dict(collections.Counter(r['expected'] for r in rows)))))


if __name__ == '__main__':
    main()
