#!/usr/bin/env python3
"""Independent fixed-cohort code/gap audit; never imports the primary."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
import re
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E/'artifacts'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')


def parse(raw, signs):
    """Forward segmentation, retaining at most two paths to detect ambiguity."""
    ways = [[] for _ in range(len(raw)+1)]
    ways[0] = [()]
    for i in range(len(raw)):
        if not ways[i]:
            continue
        for sign in signs:
            if raw.startswith(sign, i):
                end = i+len(sign)
                ways[end].extend(p+(sign,) for p in ways[i])
                ways[end] = ways[end][:2]
    assert len(ways[-1]) == 1, ('Not uniquely parsed', raw)
    return list(ways[-1][0])


def code_lengths(units, prefix):
    result = []
    i = 0
    while i < len(units):
        if units[i] == prefix:
            if i+1 == len(units) or units[i+1] == prefix:
                return None, i
            result.append(2)
            i += 2
        else:
            result.append(1)
            i += 1
    return result, None


def composition_counts(N, M):
    assert 1 <= M <= N
    surplus = N-M
    if surplus == 0:
        return {M:1}, 1
    total = math.comb(N-1, M-1)
    counts = {}
    # Choose r nonsingletons, then split the surplus into r positive parts.
    for r in range(1, min(M, surplus)+1):
        counts[M-r] = math.comb(M,r)*math.comb(surplus-1,r-1)
    assert sum(counts.values()) == total
    expected = sum(Fraction(k*v,total) for k,v in counts.items())
    assert expected == Fraction(M*(M-1),N-1)
    return counts, total


def log_mgf(counts, total, lam):
    if lam == 0:
        return 0.0
    terms = [math.log(v)-lam*k for k,v in counts.items()]
    top = max(terms)
    return top+math.log(math.fsum(math.exp(x-top) for x in terms))-math.log(total)


def chernoff(distributions, observed):
    choices = []
    for step in range(201):
        lam = step/20
        value = lam*observed + math.fsum(log_mgf(counts,total,lam) for counts,total in distributions)
        choices.append(value)
    index = min(range(len(choices)), key=lambda i: (choices[i],i))
    return {'lambda':index/20, 'raw_log_bound':choices[index],
            'log_bound':min(0.0, choices[index]+1e-8)}


def brute_counts(N,M):
    out = Counter()
    for cuts in itertools.combinations(range(1,N),M-1):
        points = (0,)+cuts+(N,)
        out[sum(points[i+1]-points[i]==1 for i in range(M))] += 1
    return dict(out)


def controls():
    compositions = 0
    for N in range(1,15):
        for M in range(1,N+1):
            counts,total = composition_counts(N,M)
            assert counts == brute_counts(N,M)
            assert total == math.comb(N-1,M-1)
            compositions += total
    checked_bounds = 0
    for pairs in [((1,1),(4,2)), ((5,3),(6,2)), ((7,4),(8,5)), ((4,4),(5,1))]:
        distributions = [composition_counts(*pair) for pair in pairs]
        mass = {0:Fraction(1)}
        for counts,total in distributions:
            nxt = defaultdict(Fraction)
            for x,p in mass.items():
                for k,v in counts.items():
                    nxt[x+k] += p*Fraction(v,total)
            mass = dict(nxt)
        for observed in range(max(mass)+1):
            exact = sum(p for k,p in mass.items() if k<=observed)
            bound = chernoff(distributions,observed)
            assert math.exp(bound['log_bound'])+1e-12 >= float(exact)
            checked_bounds += 1
    signs = ['a','b','ch']
    assert parse('achb',signs) == ['a','ch','b']
    assert code_lengths(['a','b','ch'],'a') == ([2,1],None)
    assert code_lengths(['a','a'],'a') == (None,0)
    assert code_lengths(['b','a'],'a') == (None,1)
    try:
        parse('aa',['a','aa'])
    except AssertionError:
        pass
    else:
        raise AssertionError('Ambiguity not rejected')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','compositions_enumerated':compositions,
            'small_exact_CDF_bound_checks':checked_bounds,
            'exact_integer_PMFs':True, 'native_access':False}


def projection(signs, readers):
    old = ROOT/'experiments/yolo/gdt1259_paragraph_integer_balance'
    cert = read(old/'artifacts/CERTIFICATES.json')
    census = read(old/'artifacts/CENSUS.json')
    oldspec = read(old/'src/SPEC.json')
    assert signs == oldspec['working_signs'] and readers == oldspec['readers']
    assert len(signs) == len(set(signs)) == 22
    result = {}
    for reader in readers:
        assert len(cert[reader]) == 23
        oldrows = {p['id']:p for p in census[reader]}
        result[reader] = []
        for entry in cert[reader]:
            paragraph = entry['paragraph']
            assert paragraph == oldrows[paragraph['id']]
            page = paragraph['page']
            assert not page.startswith('f84') and page not in ('f116v','f1r')
            rawgroups = entry['raw_groups']
            assert rawgroups and len(rawgroups) == paragraph['groups']
            assert str(rawgroups[0]['paragraph_start']) == '1'
            assert str(rawgroups[-1]['paragraph_end']) == '1'
            groups, counts = [], Counter()
            loci = []
            source_rows = []
            byline = defaultdict(list)
            for rawgroup in rawgroups:
                assert rawgroup['edition'] == reader and rawgroup['page'] == page
                assert rawgroup['kind'] == 'P'
                assert rawgroup['left_separator'] in oldspec['permitted_separators']
                assert rawgroup['right_separator'] in oldspec['permitted_separators']
                locus = rawgroup['locus']
                if locus not in loci:
                    loci.append(locus)
                    source_rows.append(int(rawgroup['source_row_index']))
                byline[locus].append(rawgroup)
                units = parse(rawgroup['ivtff_group_raw'], signs)
                counts.update(units)
                group_id = reader+'|'+locus+'|G'+str(int(rawgroup['source_group_index'])).zfill(3)
                groups.append({'id':group_id, 'raw':rawgroup['ivtff_group_raw'], 'units':units})
            assert loci == paragraph['loci'] and source_rows == paragraph['source_rows']
            for line in byline.values():
                assert [int(g['source_group_index']) for g in line] == list(range(1,len(line)+1))
                assert all(int(g['source_group_count']) == len(line) for g in line)
                for key in ('paragraph_start','paragraph_end','source_row_index'):
                    assert len({str(g[key]) for g in line}) == 1
            vector = [counts[s] for s in signs]
            assert vector == paragraph['counts']
            result[reader].append({'paragraph_id':paragraph['id'], 'page':page,
                                  'leaf':re.match(r'f\d+',page).group(0),
                                  'groups':groups, 'counts':vector})
    return result


def evaluate_head(paragraphs, head):
    summaries, distributions = [], []
    total_X, expectation = 0, Fraction(0)
    leafs = defaultdict(lambda: {'X':0, 'E':Fraction(0), 'variable':False})
    variable = 0
    for paragraph in paragraphs:
        lengths = []
        for group in paragraph['groups']:
            codes, bad_index = code_lengths(group['units'],head)
            if codes is None:
                return {'invalid':True, 'paragraph':paragraph['paragraph_id'],
                        'group_id':group['id'], 'raw':group['raw'], 'unit_index':bad_index,
                        'trailing':bad_index+1 == len(group['units'])}
            lengths.append(len(codes))
        N, M = sum(lengths), len(lengths)
        X = lengths.count(1)
        counts, denominator = composition_counts(N,M)
        ex = sum((Fraction(k*v,denominator) for k,v in counts.items()),Fraction(0))
        distributions.append((counts,denominator))
        nondegenerate = len(counts)>1
        variable += nondegenerate
        total_X += X
        expectation += ex
        leaf = leafs[paragraph['leaf']]
        leaf['X'] += X
        leaf['E'] += ex
        leaf['variable'] |= nondegenerate
        summaries.append({'id':paragraph['paragraph_id'], 'page':paragraph['page'], 'leaf':paragraph['leaf'],
                          'N':N, 'M':M, 'X':X, 'expected_numerator':ex.numerator,
                          'expected_denominator':ex.denominator,
                          'pmf_support':sorted(counts), 'pmf_counts':[str(counts[k]) for k in sorted(counts)],
                          'pmf_denominator':str(denominator)})
    bound = chernoff(distributions,total_X)
    return {'invalid':False, 'paragraphs':summaries, 'total_X':total_X, 'E':expectation,
            'ratio':float(Fraction(total_X)/expectation) if expectation else None,
            'log_bound':bound['log_bound'], 'best_lambda':bound['lambda'],
            'variable_paragraphs':variable,
            'variable_leaves':sum(leaf['variable'] for leaf in leafs.values()),
            'leaf_summaries':dict(leafs)}


def validate():
    lockpath = E/'LOCK.json'
    lock = read(lockpath)
    pins = {entry['path']:entry['sha256'] for entry in lock['files']}
    old = ROOT/'experiments/yolo/gdt1259_paragraph_integer_balance'
    required = [E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'PREREGISTRATION.md',E/'METHOD.md',
                old/'src/SPEC.json',old/'artifacts/CERTIFICATES.json',old/'artifacts/CENSUS.json']
    for path in required:
        key = str(path.relative_to(ROOT))
        assert key in pins and sha(path) == pins[key],key
    spec = read(E/'src/SPEC.json')
    for entry in spec['inputs']:
        assert pins[entry['path']] == entry['sha256'] == sha(ROOT/entry['path'])
    assert spec['readers'] == ['ZL3b','IT2a']
    assert spec['lambda_grid'] == [i/20 for i in range(201)]
    assert spec['log_safety'] == 1e-8 and spec['ratio_max'] == .75
    assert spec['alpha'] == .01 and spec['correction'] == 44
    assert spec['min_variable_paragraphs'] == 12 and spec['min_variable_leaves'] == 10
    projected = projection(spec['working_signs'],spec['readers'])
    assert read(A/'DATA.json') == {'readers':projected}
    result = read(A/'RESULT.json')
    cutoff = math.log(.01/44)
    evidence = {}
    statuses = []
    for reader in spec['readers']:
        primary = result['readers'][reader]
        cases = primary['cases']
        assert len(cases) == 22 and [c['head'] for c in cases] == spec['working_signs']
        statuses_case, valid_bounds = [], []
        for case in cases:
            recomputed = evaluate_head(projected[reader],case['head'])
            if recomputed['invalid']:
                expected_failure = {'para':recomputed['paragraph'], 'group_id':recomputed['group_id'],
                                    'raw':recomputed['raw'],
                                    'reason':'ESCAPE_AT_GROUP_END' if recomputed['trailing'] else 'DOUBLE_ESCAPE'}
                assert case['first_failure'] == expected_failure
                assert case['status'] == 'INVALID_CARRIER'
                statuses_case.append('INVALID_CARRIER')
                continue
            assert case['paragraphs'] == recomputed['paragraphs']
            for field in ('total_X','variable_paragraphs','variable_leaves'):
                assert case[field] == recomputed[field]
            ex = recomputed['E']
            assert int(case['expected_num']) == ex.numerator and int(case['expected_den']) == ex.denominator
            if recomputed['ratio'] is None:
                assert case['ratio'] is None
            else:
                assert abs(case['ratio']-recomputed['ratio']) < 1e-12
            assert abs(case['log_bound']-recomputed['log_bound']) < 1e-7
            # Different exact PMF evaluation may move a nearly tied minimum.
            assert case['best_lambda'] in spec['lambda_grid']
            if case['best_lambda'] != recomputed['best_lambda']:
                dists = [(dict(zip(p['pmf_support'],map(int,p['pmf_counts']))),int(p['pmf_denominator'])) for p in recomputed['paragraphs']]
                at_lambda = case['best_lambda']*recomputed['total_X']+math.fsum(log_mgf(c,d,case['best_lambda']) for c,d in dists)
                assert abs(min(0,at_lambda+1e-8)-recomputed['log_bound']) < 1e-7
            capacity = recomputed['variable_paragraphs']>=12 and recomputed['variable_leaves']>=10
            rejected = capacity and ex>0 and Fraction(recomputed['total_X'])/ex<=Fraction(3,4) and recomputed['log_bound']<=cutoff
            expected_status = 'CAPACITY_STOP' if not capacity else 'SHORTFALL_REJECTED' if rejected else 'NOT_REJECTED'
            assert case['status'] == expected_status
            statuses_case.append(expected_status)
            valid_bounds.append(recomputed['log_bound'])
            if 'leaf_summaries' in case:
                leaves = case['leaf_summaries']
                assert [leaf['leaf'] for leaf in leaves] == sorted(recomputed['leaf_summaries'])
                for leaf in leaves:
                    values = recomputed['leaf_summaries'][leaf['leaf']]
                    assert leaf['total_X'] == values['X']
                    assert int(leaf['expected_num']) == values['E'].numerator
                    assert int(leaf['expected_den']) == values['E'].denominator
        excluded = all(s in ('INVALID_CARRIER','SHORTFALL_REJECTED') for s in statuses_case)
        assert primary['valid_heads'] == len(valid_bounds)
        if valid_bounds:
            assert abs(primary['worst_log_bound']-max(valid_bounds)) < 1e-7
        else:
            assert primary['worst_log_bound'] is None
        expected_reader = 'EXCLUDED' if excluded else 'NOT_EXCLUDED'
        assert primary['status'] == expected_reader
        statuses.append(expected_reader)
        evidence[reader] = {'status':expected_reader,'case_status_counts':dict(Counter(statuses_case)),
                            'max_valid_log_bound':max(valid_bounds) if valid_bounds else None,
                            'paragraphs':len(projected[reader])}
    expected_top = 'INDEPENDENT_CODE_GAP_MODEL_REJECTED' if all(s=='EXCLUDED' for s in statuses) else 'NOT_REJECTED'
    assert result['status'] == expected_top
    receipt = {'experiment_id':'GDT1394','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':expected_top,
               'readers':evidence,'source_free_controls':controls(),
               'implementation':'Independent forward segmentation, explicit code scanning, surplus-allocation exact integer PMFs, separate Chernoff calculation; no primary imports.',
               'source_scope':'Only original23whole certificate paragraphs perreader; census used only to verify their existing metadata/counts.',
               'pins':{'code_lock_sha256':sha(lockpath),'spec_sha256':sha(E/'src/SPEC.json'),
                       'data_sha256':sha(A/'DATA.json'),'result_sha256':sha(A/'RESULT.json'),
                       'validator_sha256':sha(Path(__file__))},
               'limits':['Conditional fixed-cohort spacing-law result, not independent manuscript confirmation.',
                         'Source units and raw group boundaries are inherited, not new palaeographic findings.',
                         'RF1b remains unscorable; no lexical meaning or general source-grammar exclusion.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':expected_top,'readers':evidence},sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls',action='store_true')
    args = parser.parse_args()
    if args.controls:
        print(json.dumps(controls(),sort_keys=True))
    else:
        validate()
