#!/usr/bin/env python3
"""Independent source compilation, complete fitting and frozen prediction replay.

The enumerator receives only the blind template and odd-body/even-head panel.
No producer fitting or evaluation logic is imported. Source answers stay outside
enumeration; the cached reader is imported exclusively for projection replay.
"""
import argparse
import copy
import hashlib
import itertools
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
ROOT = EXPERIMENT.parents[2]
EDITIONS = ('ZL3b', 'IT2a', 'RF1b', 'CONSENSUS')
ROLES = ('C', 'B', 'D', 'L', 'M', 'S')
TRAINING = ROLES[:-1]
CORE_KEYS = ('paragraphs', 'prefix_head', 'prefix_body', 'bodies',
             'head_forms', 'mention_forms', 'held_head_paragraphs')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def words(text):
    """Scan literal Latin-letter words without aliases or editorial corrections."""
    result, current = [], []
    for character in text.lower() + ' ':
        if 'a' <= character <= 'z':
            current.append(character)
        elif current:
            result.append(''.join(current))
            current = []
    return result


def source_mentions(body, headwords):
    tokens = words(body)
    names = sorted(((words(name), role) for role, name in headwords.items()),
                   key=lambda item: (-len(item[0]), item[1]))
    result, position = [], 0
    while position < len(tokens):
        for spelling, role in names:
            if tokens[position:position + len(spelling)] == spelling:
                result.append({'body_word_start_zero_based': position,
                               'target': role, 'written_name': ' '.join(spelling)})
                position += len(spelling)
                break
        else:
            position += 1
    return result


def audit_source():
    source = read_json(HERE / 'SOURCE.json')
    template = read_json(HERE / 'FIT_TEMPLATE.json')
    assert source['node_order'] == list(ROLES)
    assert source['headwords'] == {
        'C': 'Cardo', 'B': 'Cardo benedictus', 'D': 'Carduncellus',
        'L': 'Labrum ueneris', 'M': 'Matrona', 'S': 'Senecio'}
    assert set(source['entries']) == set(ROLES)
    compiled = {}
    for role in ROLES:
        entry = source['entries'][role]
        mentions = source_mentions(entry['body'], source['headwords'])
        assert mentions == entry['mentions'], ('source mention mismatch', role)
        compiled[role] = [mention['target'] for mention in mentions]
    assert compiled == {'C': ['L'], 'B': ['D', 'S', 'L', 'S'], 'D': ['B'],
                        'L': ['C'], 'M': ['C'], 'S': ['B', 'D']}
    assert template == {'nodes': list(ROLES), 'training_roles': list(TRAINING),
                        'held_role': 'S', 'rows': {r: compiled[r] for r in TRAINING}}
    # Zero the WHOLE S row first, then test all 6! unlabelled permutations.
    graph = {r: Counter(compiled[r]) if r != 'S' else Counter() for r in ROLES}
    automorphisms = []
    for permutation in itertools.permutations(ROLES):
        mapping = dict(zip(ROLES, permutation))
        if all(graph[a][b] == graph[mapping[a]][mapping[b]] for a in ROLES for b in ROLES):
            automorphisms.append(permutation)
    assert automorphisms == [ROLES], ('withheld-row graph not asymmetric', automorphisms)
    reached = {ROLES[0]}
    while True:
        expanded = reached | {b for a in reached for b in ROLES if graph[a][b] or graph[b][a]}
        if expanded == reached:
            break
        reached = expanded
    assert reached == set(ROLES), 'withheld-row graph not weakly connected'
    return {'status': 'PASS', 'compiled_rows': compiled, 'whole_S_row_withheld': True,
            'unlabelled_automorphisms': len(automorphisms), 'weakly_connected': True,
            'source_sha256': digest(HERE / 'SOURCE.json'),
            'fit_template_sha256': digest(HERE / 'FIT_TEMPLATE.json')}


def validate_panel_input(panel, template):
    assert template['nodes'] == list(ROLES)
    assert template['training_roles'] == list(TRAINING)
    assert template['held_role'] == 'S'
    assert set(template) == {'nodes', 'training_roles', 'held_role', 'rows'}
    assert set(template['rows']) == set(TRAINING), 'held source row leaked to fitter'
    assert all(value in ROLES for row in template['rows'].values() for value in row)
    assert set(panel) == {'train', 'held_heads'}
    ids = set()
    for partition, odd in (('train', True), ('held_heads', False)):
        for record in panel[partition]:
            assert set(record) == ({'paragraph_id', 'page', 'physical_folio', 'head', 'body'}
                                   if odd else {'paragraph_id', 'page', 'physical_folio', 'head'})
            assert record['paragraph_id'] not in ids, 'duplicate paragraph identifier'
            ids.add(record['paragraph_id'])
            page = record['page']
            assert isinstance(page, str) and not page.startswith('f84'), 'sealed selector'
            match = re.match(r'f([0-9]+)', page)
            assert match and record['physical_folio'] == match.group()
            assert (int(match.group(1)) % 2 == 1) == odd, 'physical-leaf split mismatch'
            groups = [record['head']] + (record['body'] if odd else [])
            assert all(isinstance(group, list) and group and
                       all(isinstance(member, str) and member for member in group)
                       for group in groups), 'invalid literal STA member group'


def surface_lexicons(solutions):
    lexicons = {}
    for solution in solutions:
        lexicon = {key: solution[key] for key in ('head_forms', 'mention_forms')}
        lexicons[canonical(lexicon)] = lexicon
    return [lexicons[key] for key in sorted(lexicons)]


def enumerate_panel(panel, template, deadline=None):
    """Independent CSP seeded by B's double S mention and eligible even heads.

    Every solution has a B record, a 0..2 head prefix and a twice-written S
    mention. Its 0..2 body-prefix removal fixes S's nonempty body, which must
    match an eligible even head with the same head prefix. These seeds are
    exhaustive. Recursion then visits all D,L,C,M records and excludes only
    body/leaf collisions or already determined exact matrix-cell violations.
    """
    validate_panel_input(panel, template)
    required = {role: Counter(template['rows'][role]) for role in TRAINING}
    assert required['B']['S'] == 2, 'seed requires frozen double-S row'
    train = panel['train']
    head_codes = [tuple(record['head']) for record in train]
    body_counts = [Counter(map(tuple, record['body'])) for record in train]
    even_by_head = defaultdict(list)
    for record in panel['held_heads']:
        even_by_head[tuple(record['head'])].append(record['paragraph_id'])
    solutions, complete, seed_count = [], True, 0

    def over_budget():
        return deadline is not None and time.monotonic() > deadline

    # Count the producer's prefix search domain as a separate diagnostic;
    # the independent search below never visits that Cartesian product.
    prefix_domains = {}
    for code in head_codes:
        for size in range(min(3, len(code))):
            ph = code[:size]
            if ph not in prefix_domains:
                active = [i for i, head in enumerate(head_codes)
                          if len(head) > size and head[:size] == ph]
                held = any(len(head) > size and head[:size] == ph for head in even_by_head)
                if len({train[i]['physical_folio'] for i in active}) >= 5 and held:
                    pc = {group[:n] for i in active for group in body_counts[i]
                          for n in range(min(3, len(group)))}
                    prefix_domains[ph] = (active, pc)
                else:
                    prefix_domains[ph] = ([], set())
    prefix_pairs = sum(len(pc) for _, pc in prefix_domains.values())

    for b_index, b_head in enumerate(head_codes):
        if over_budget():
            complete = False
            break
        for h_size in range(min(3, len(b_head))):
            ph, bb = b_head[:h_size], b_head[h_size:]
            active, _ = prefix_domains[ph]
            if not active:
                continue
            body_for_index = {i: head_codes[i][h_size:] for i in active}
            for s_mention, multiplicity in body_counts[b_index].items():
                if multiplicity != 2:
                    continue
                for p_size in range(min(3, len(s_mention))):
                    if over_budget():
                        complete = False
                        break
                    pc, sb = s_mention[:p_size], s_mention[p_size:]
                    if sb == bb or ph + sb not in even_by_head:
                        continue
                    if body_counts[b_index][pc + bb] != required['B']['B']:
                        continue
                    seed_count += 1
                    assigned, bodies = {'B': b_index}, {'B': bb, 'S': sb}
                    leaves = {train[b_index]['physical_folio']}

                    def extend(depth):
                        nonlocal complete
                        if over_budget():
                            complete = False
                            return
                        if depth == 4:
                            solutions.append({
                                'paragraphs': {r: train[assigned[r]]['paragraph_id'] for r in TRAINING},
                                'prefix_head': list(ph), 'prefix_body': list(pc),
                                'bodies': {r: list(bodies[r]) for r in ROLES},
                                'head_forms': {r: list(ph + bodies[r]) for r in ROLES},
                                'mention_forms': {r: list(pc + bodies[r]) for r in ROLES},
                                'held_head_paragraphs': sorted(even_by_head[ph + sb])})
                            return
                        role = ('D', 'L', 'C', 'M')[depth]
                        for index in active:
                            value, leaf = body_for_index[index], train[index]['physical_folio']
                            if value in bodies.values() or leaf in leaves:
                                continue
                            # New column in every assigned row, including zeros.
                            if any(body_counts[old_index][pc + value] != required[old_role][role]
                                   for old_role, old_index in assigned.items()):
                                continue
                            # New row against every assigned column, including S.
                            if any(body_counts[index][pc + old_body] != required[role][old_role]
                                   for old_role, old_body in bodies.items()):
                                continue
                            if body_counts[index][pc + value] != required[role][role]:
                                continue
                            assigned[role], bodies[role] = index, value
                            leaves.add(leaf)
                            extend(depth + 1)
                            leaves.remove(leaf)
                            del assigned[role], bodies[role]
                            if not complete:
                                return

                    extend(0)
                    if not complete:
                        break
                if not complete:
                    break
            if not complete:
                break
        if not complete:
            break
    solutions.sort(key=canonical)
    assert len(solutions) == len({canonical(solution) for solution in solutions})
    return {'complete': complete, 'solutions': solutions,
            'lexicons': surface_lexicons(solutions), 'prefix_pairs': prefix_pairs,
            'independent_B_S_seeds': seed_count}


def compare_panel(expected, reported):
    assert expected['complete'] is True and reported['complete'] is True, 'enumeration incomplete'
    assert expected['prefix_pairs'] == reported['prefix_pairs'], 'prefix-domain count mismatch'
    actual = reported['solutions']
    assert all(set(solution) == set(CORE_KEYS) for solution in actual), 'unexpected solution fields'
    assert len(actual) == len({canonical(value) for value in actual}), 'duplicate reported solutions'
    assert sorted(map(canonical, expected['solutions'])) == sorted(map(canonical, actual)), 'solution set mismatch'
    assert len(reported['lexicons']) == len({canonical(value) for value in reported['lexicons']}), 'duplicate lexicons'
    assert sorted(map(canonical, expected['lexicons'])) == sorted(map(canonical, reported['lexicons'])), 'lexicon set mismatch'
    assert surface_lexicons(actual) == expected['lexicons'], 'surface-lexicon reduction mismatch'


def fixture(head_prefix=('h',), mention_prefix=('m',), stem_prefix=(), namespace='a', leaf_offset=0):
    template = {'nodes': list(ROLES), 'training_roles': list(TRAINING), 'held_role': 'S',
                'rows': {'C': ['L'], 'B': ['D', 'S', 'L', 'S'], 'D': ['B'], 'L': ['C'], 'M': ['C']}}
    bodies = {role: tuple(stem_prefix) + (namespace + role,) for role in ROLES}
    records = []
    for position, role in enumerate(TRAINING):
        leaf = leaf_offset + 2 * position + 1
        records.append({'paragraph_id': namespace + role, 'page': f'f{leaf}r',
                        'physical_folio': f'f{leaf}', 'head': list(tuple(head_prefix) + bodies[role]),
                        'body': [list(tuple(mention_prefix) + bodies[target]) for target in template['rows'][role]]})
    held = [{'paragraph_id': namespace + 'S', 'page': f'f{leaf_offset + 2}r',
             'physical_folio': f'f{leaf_offset + 2}', 'head': list(tuple(head_prefix) + bodies['S'])}]
    return {'train': records, 'held_heads': held}, template


def brute_fixture_oracle(panel, template):
    """Tiny-fixture oracle: all five-record permutations, no B/S seed pruning."""
    solutions = set()
    required = {role: Counter(template['rows'][role]) for role in TRAINING}
    for records in itertools.permutations(panel['train'], 5):
        if len({r['physical_folio'] for r in records}) != 5:
            continue
        heads = {role: tuple(record['head']) for role, record in zip(TRAINING, records)}
        counts = {role: Counter(map(tuple, record['body'])) for role, record in zip(TRAINING, records)}
        for n in range(min(3, len(heads['C']))):
            ph = heads['C'][:n]
            if any(len(head) <= n or head[:n] != ph for head in heads.values()):
                continue
            bodies = {role: head[n:] for role, head in heads.items()}
            for held_head in sorted({tuple(record['head']) for record in panel['held_heads']}):
                if len(held_head) <= n or held_head[:n] != ph:
                    continue
                bodies['S'] = held_head[n:]
                if len(set(bodies.values())) != 6:
                    continue
                body_prefixes = {group[:k] for record in records for group_list in record['body']
                                 for group in [tuple(group_list)] for k in range(min(3, len(group)))}
                for pc in body_prefixes:
                    if not all(counts[r][pc + bodies[c]] == required[r][c] for r in TRAINING for c in ROLES):
                        continue
                    solution = {'paragraphs': {r: record['paragraph_id'] for r, record in zip(TRAINING, records)},
                                'prefix_head': list(ph), 'prefix_body': list(pc),
                                'bodies': {r: list(bodies[r]) for r in ROLES},
                                'head_forms': {r: list(ph + bodies[r]) for r in ROLES},
                                'mention_forms': {r: list(pc + bodies[r]) for r in ROLES},
                                'held_head_paragraphs': sorted(r['paragraph_id'] for r in panel['held_heads'] if tuple(r['head']) == held_head)}
                    solutions.add(canonical(solution))
    return solutions


def selftest():
    passed = []
    names = {'C': 'Cardo', 'B': 'Cardo benedictus', 'D': 'Carduncellus',
             'L': 'Labrum ueneris', 'M': 'Matrona', 'S': 'Senecio'}
    sample = source_mentions('Cardo benedictus; cardo. Matrana Matrona. Senecium Senicion Senecio; carduncellus [terestris].', names)
    assert [value['target'] for value in sample] == ['B', 'C', 'M', 'S', 'D']
    passed.append('literal_longest_names_without_aliases')
    base, template = fixture()
    positive = enumerate_panel(base, template)
    assert positive['complete'] and len(positive['solutions']) == len(positive['lexicons']) == 1
    assert positive['solutions'][0]['paragraphs'] == {role: 'a' + role for role in TRAINING}
    passed.append('unique_positive_complete_incidence')
    for head_prefix, mention_prefix in (((), ()), ((), ('m', 'n')), (('h', 'j'), ()), (('h', 'j'), ('m', 'n'))):
        panel, fit = fixture(head_prefix, mention_prefix)
        outcome = enumerate_panel(panel, fit)
        assert len(outcome['solutions']) == len(outcome['lexicons']) == 1
        assert outcome['solutions'][0]['prefix_head'] == list(head_prefix)
        assert outcome['solutions'][0]['prefix_body'] == list(mention_prefix)
    passed.append('zero_and_two_member_prefix_boundaries')
    ambiguity, fit = fixture(stem_prefix=('q',))
    alternate = enumerate_panel(ambiguity, fit)
    assert len(alternate['solutions']) == 2 and len(alternate['lexicons']) == 1
    assert {tuple(s['prefix_head']) for s in alternate['solutions']} == {('h',), ('h', 'q')}
    passed.append('alternate_prefixes_one_surface_lexicon')
    for panel in (base, ambiguity):
        assert set(map(canonical, enumerate_panel(panel, template)['solutions'])) == brute_fixture_oracle(panel, template)
    passed.append('all_assignment_prefix_brute_oracle_agreement')
    retained = copy.deepcopy(base)
    retained['train'].append(dict(copy.deepcopy(base['train'][1]), paragraph_id='aB_second', page='f11r', physical_folio='f11'))
    retained['held_heads'] += [dict(base['held_heads'][0], paragraph_id='aS_verso', page='f2v'),
                               dict(base['held_heads'][0], paragraph_id='aS_other_leaf', page='f4r', physical_folio='f4')]
    outcome = enumerate_panel(retained, template)
    assert len(outcome['solutions']) == 2 and len(outcome['lexicons']) == 1
    assert all(s['held_head_paragraphs'] == ['aS', 'aS_other_leaf', 'aS_verso'] for s in outcome['solutions'])
    passed.append('all_assignments_and_matching_even_heads_retained')
    competitor, _ = fixture(namespace='z', leaf_offset=10)
    combined = {key: base[key] + competitor[key] for key in base}
    outcome = enumerate_panel(combined, template)
    assert len(outcome['solutions']) == len(outcome['lexicons']) == 2
    passed.append('competing_lexicons_not_ranked_or_collapsed')
    negative = copy.deepcopy(base)
    negative['train'][1]['body'].pop()
    assert not enumerate_panel(negative, template)['solutions']
    passed.append('missing_repeated_S_mention_rejected')
    negative = copy.deepcopy(base)
    negative['train'][0]['body'].append(['m', 'aM'])
    assert not enumerate_panel(negative, template)['solutions']
    passed.append('unexpected_zero_cell_mention_rejected')
    negative = copy.deepcopy(base)
    negative['train'][4]['page'], negative['train'][4]['physical_folio'] = 'f1v', 'f1'
    assert not enumerate_panel(negative, template)['solutions']
    passed.append('five_distinct_physical_leaves_required')
    negative = copy.deepcopy(base)
    negative['train'][4]['head'] = list(base['train'][0]['head'])
    assert not enumerate_panel(negative, template)['solutions']
    passed.append('distinct_name_bodies_required')
    negative = copy.deepcopy(base)
    negative['train'][4]['head'] = ['h']
    assert not enumerate_panel(negative, template)['solutions']
    passed.append('empty_residual_body_rejected')
    panel, fit = fixture(head_prefix=('h', 'i', 'j'))
    assert not enumerate_panel(panel, fit)['solutions']
    passed.append('prefix_longer_than_two_rejected')
    no_held = copy.deepcopy(base)
    no_held['held_heads'] = []
    assert not enumerate_panel(no_held, template)['solutions']
    passed.append('matching_even_S_head_required')
    unmapped = copy.deepcopy(base)
    unmapped['train'][0]['body'] += [['unmodelled'], ['unmodelled']]
    assert enumerate_panel(unmapped, template)['solutions'] == positive['solutions']
    passed.append('outside_name_universe_left_unmodelled')
    leaked = copy.deepcopy(base)
    leaked['held_heads'][0]['body'] = [['forbidden']]
    try:
        enumerate_panel(leaked, template)
    except AssertionError:
        pass
    else:
        raise AssertionError('even body accepted by blind enumerator')
    answer = copy.deepcopy(template)
    answer['rows']['S'] = ['B', 'D']
    try:
        enumerate_panel(base, answer)
    except AssertionError:
        pass
    else:
        raise AssertionError('held source answer accepted by enumerator')
    passed.append('held_body_and_source_answer_input_rejected')
    assert enumerate_panel(base, template, deadline=time.monotonic() - 1)['complete'] is False
    passed.append('deadline_never_reports_complete')
    return passed


def audit_predictions(result, fit_input, source_check):
    """Freeze exactly the common surface lexicon and all matching even heads."""
    source_counts = Counter(source_check['compiled_rows']['S'])
    counts = {role: source_counts[role] for role in ROLES}
    panels, statuses = {}, {}
    for edition, fitted in result['panels'].items():
        if not fitted['complete']:
            status = 'INCOMPLETE_FIT'
        elif not fitted['lexicons']:
            status = 'NO_TRAINING_SOLUTION'
        elif len(fitted['lexicons']) > 1:
            status = 'NONUNIQUE_TRAINING_LEXICON'
        else:
            status = 'WAITING_HELD_RELEASE'
            lexicon = fitted['lexicons'][0]
            ids = sorted(record['paragraph_id'] for record in fit_input['panels'][edition]['held_heads']
                         if record['head'] == lexicon['head_forms']['S'])
            assert ids and all(solution['held_head_paragraphs'] == ids for solution in fitted['solutions'])
            panels[edition] = {'lexicon': lexicon, 'expected_counts': counts, 'paragraph_ids': ids}
        statuses[edition] = {'status': status}
    expected = {'experiment_id': 'GDT888', 'panels': panels,
                'ceiling': 'Frozen conditional predictions; no held bodies used in fitting.'}
    return expected, statuses


def audit_held(predicted, fit_input, initial):
    """Called only for EVALUATED phase after complete unique-lexicon checking."""
    evaluations = copy.deepcopy(initial)
    if not predicted['panels']:
        return evaluations
    cache = read_json(ROOT / fit_input['source'])
    frames = {frame['paragraph_id']: frame for frame in cache['frames']}
    assert len(frames) == len(cache['frames']), 'duplicate cached paragraph'
    for edition, prediction in predicted['panels'].items():
        observations = []
        for paragraph_id in prediction['paragraph_ids']:
            frame = frames[paragraph_id]
            assert not frame['page'].startswith('f84')
            assert int(frame['physical_folio'][1:]) % 2 == 0
            reading = frame['readings'][edition]
            assert reading['eligible'] is True
            assert reading['groups'][0]['sta'] == prediction['lexicon']['head_forms']['S']
            observed = {role: 0 for role in ROLES}
            matches = []
            for group in reading['groups'][1:]:
                roles = [role for role in ROLES if group['sta'] == prediction['lexicon']['mention_forms'][role]]
                assert len(roles) <= 1
                if roles:
                    role = roles[0]
                    observed[role] += 1
                    matches.append({'role': role, **{key: group[key] for key in ('source_group_id', 'locus', 'raw', 'sta')}})
            observations.append({'paragraph_id': paragraph_id, 'page': frame['page'],
                                 'physical_folio': frame['physical_folio'], 'observed_counts': observed,
                                 'expected_counts': prediction['expected_counts'],
                                 'passed': observed == prediction['expected_counts'], 'matched_groups': matches})
        evaluations[edition] = {'status': 'HELD_ALL_PASS' if all(o['passed'] for o in observations) else 'HELD_FAILURE',
                                'observations': observations,
                                'held_leaves': sorted({o['physical_folio'] for o in observations}),
                                'score_ready': False}
    return evaluations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selftest', action='store_true', help='source and synthetic only; no target access')
    parser.add_argument('--check', action='store_true', help='compare saved validation instead of writing')
    args = parser.parse_args()
    source_check = audit_source()
    tests = selftest()
    if args.selftest:
        print(json.dumps({'status': 'PASS', 'source': source_check, 'selftests': tests}, sort_keys=True))
        return 0
    for relative, expected_hash in read_json(HERE / 'PREREG_LOCK.json').items():
        assert digest(ROOT / relative) == expected_hash, ('preregistration hash mismatch', relative)
    input_path = EXPERIMENT / 'artifacts/FIT_INPUT.json'
    result_path = EXPERIMENT / 'artifacts/RESULT.json'
    prediction_path = EXPERIMENT / 'artifacts/PREDICTIONS.json'
    fit_input = read_json(input_path)
    from prepare import prepare  # Projection replay only; no fitting/evaluation import.
    assert prepare() == fit_input, 'blinded cached projection replay mismatch'
    assert set(fit_input) == {'source', 'source_sha256', 'panels'}
    assert digest(ROOT / fit_input['source']) == fit_input['source_sha256']
    assert set(fit_input['panels']) == set(EDITIONS)
    result = read_json(result_path)
    assert result['experiment_id'] == 'GDT888' and result['complete'] is True
    assert set(result['panels']) == set(EDITIONS)
    template = read_json(HERE / 'FIT_TEMPLATE.json')
    panels = {}
    for edition in EDITIONS:
        independent = enumerate_panel(fit_input['panels'][edition], template)
        compare_panel(independent, result['panels'][edition])
        panels[edition] = {'complete': True, 'solutions': len(independent['solutions']),
                           'surface_lexicons': len(independent['lexicons']),
                           'prefix_pairs': independent['prefix_pairs'],
                           'independent_B_S_seeds': independent['independent_B_S_seeds']}
    predicted, evaluations = audit_predictions(result, fit_input, source_check)
    assert read_json(prediction_path) == predicted, 'frozen prediction mismatch'
    assert result['phase'] in ('FIT_ONLY', 'EVALUATED')
    if result['phase'] == 'EVALUATED':
        evaluations = audit_held(predicted, fit_input, evaluations)
    assert result['evaluations'] == evaluations, 'held phase/status/evaluation mismatch'
    validation = {'status': 'PASS', 'source': source_check, 'selftests': tests, 'panels': panels,
                  'fit_input_sha256': digest(input_path), 'result_sha256': digest(result_path),
                  'predictions_sha256': digest(prediction_path), 'validator_sha256': digest(__file__),
                  'blinded_projection_replayed': True, 'independent_complete_solution_sets_replayed': True,
                  'phase': result['phase'], 'prediction_panels': sorted(predicted['panels']),
                  'held_evaluations_replayed': result['phase'] == 'EVALUATED' and bool(predicted['panels'])}
    destination = EXPERIMENT / 'artifacts/VALIDATION.json'
    if args.check:
        assert read_json(destination) == validation, 'stored validation mismatch'
    else:
        destination.write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
