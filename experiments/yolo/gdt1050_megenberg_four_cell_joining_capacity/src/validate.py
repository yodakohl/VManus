#!/usr/bin/env python3
"""Independent GDT1050 finite-writer and guarded-cache validator.
Does not import or read the experiment runner. Semantic truth is not certified.
"""
from __future__ import annotations
import collections
import copy
import datetime as dt
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys
import traceback

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
EDITIONS = ('ZL3b', 'IT2a', 'RF1b')
LITERAL = re.compile(r'[a-z]+\Z')
CLAUSES = ((0, 0, True), (1, 1, True), (1, 0, False), (0, 1, False))
checks = []


def verify(condition, label, detail=None):
    if not condition:
        raise AssertionError(f'{label}: {detail}')
    checks.append({'check': label, 'status': 'PASS'})


def readj(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(page, locus):
    m = re.fullmatch(re.escape(page) + r'\.(\d+)', locus)
    return int(m[1]) if m else None


def collect_complete(lines):
    """Start/end state machine, without consulting the old paragraph bank."""
    by_page = collections.defaultdict(list)
    for line in lines:
        if line['metadata']['kind'] == 'P':
            by_page[(line['metadata']['edition'], line['metadata']['page'])].append(line)
    out = {e: [] for e in EDITIONS}
    for (edition, page), source in sorted(by_page.items()):
        active, previous = [], None
        for line in sorted(source, key=lambda a: int(a['metadata']['source_row_index'])):
            meta = line['metadata']
            locnum = number(page, meta['locus'])
            start, end = meta['paragraph_start'] == '1', meta['paragraph_end'] == '1'
            if start:
                active, previous = [], None
            elif active and (locnum is None or previous is None or locnum != previous + 1):
                active, previous = [], None
            if start or active:
                active.append(line)
                previous = locnum
            if end:
                if active:
                    pid = page + '|' + active[0]['metadata']['locus'] + '-' + meta['locus']
                    flat = []
                    old_lines = []
                    for rawline in active:
                        m = rawline['metadata']
                        groups = rawline['groups']
                        anchor = len(groups) >= 2 and all(LITERAL.fullmatch(g['ivtff_group_raw']) for g in groups)
                        anchor = anchor and [int(g['source_group_index']) for g in groups] == list(range(1, len(groups) + 1))
                        anchor = anchor and all(a['right_separator'] == b['left_separator'] == 'DEFINITE_SPACE' for a, b in zip(groups, groups[1:]))
                        old_lines.append({'locus': m['locus'], 'row': int(m['source_row_index']),
                            'start': m['paragraph_start'] == '1', 'end': m['paragraph_end'] == '1',
                            'words': [g['ivtff_group_raw'] for g in groups],
                            'source_ids': [g['source_group_id'] for g in groups],
                            'anchor_eligible': bool(anchor), 'offset': len(flat)})
                        for g in groups:
                            flat.append(dict(g, locus=m['locus'], page=page, edition=edition,
                                source_group_count=int(m['source_group_count']), source_row_index=int(m['source_row_index'])))
                    old = {'id': pid, 'page': page, 'leaf': int(re.match(r'f(\d+)', page)[1]), 'lines': old_lines, 'groups': len(flat)}
                    out[edition].append({'original': old, 'flat': flat})
                active, previous = [], None
    for edition in out:
        out[edition].sort(key=lambda p: p['original']['id'])
    return out


def eligibility(window):
    why = set()
    if any(not LITERAL.fullmatch(g['ivtff_group_raw']) for g in window):
        why.add('NON_LITERAL_GROUP')
    for a, b in zip(window, window[1:]):
        ai, bi = int(a['source_group_index']), int(b['source_group_index'])
        if a['locus'] == b['locus']:
            if bi != ai + 1:
                why.add('NONCONSECUTIVE_GROUP_INDEX')
            if a['right_separator'] != 'DEFINITE_SPACE' or b['left_separator'] != 'DEFINITE_SPACE':
                why.add('NONDEFINITE_INTERNAL_SEAM')
        elif (a['page'] != b['page'] or ai != a['source_group_count'] or bi != 1
                or number(a['page'], a['locus']) is None
                or number(b['page'], b['locus']) != number(a['page'], a['locus']) + 1):
            why.add('INVALID_PHYSICAL_LINE_TRANSITION')
    return why


def make_schemas(bank):
    schemas = []
    for order in itertools.permutations(('P', 'ARG1', 'ARG2')):
        for placement in ('before_clause', 'after_clause'):
            tokens, positions = [], []
            for ci, (a, b, neg) in enumerate(CLAUSES):
                roles = {'P': 'P', 'ARG1': ('A', 'B')[a], 'ARG2': ('A', 'B')[b]}
                chunk = [(roles[slot], ci, slot) for slot in order]
                if neg:
                    chunk.insert(0 if placement == 'before_clause' else len(chunk), ('N', ci, 'N'))
                for token, clause, slot in chunk:
                    tokens.append(token); positions.append({'clause': clause, 'slot': slot})
            schemas.append({'family': 'ATOMIC14', 'slot_order': list(order), 'negative_placement': placement,
                'pattern': tokens, 'positions': positions, 'fixed': {}, 'pair': None,
                'first_role_A_suffix': None, 'cross_role_alignment': None})
    for x, y in bank:
        for suffix in ('r', 'l'):
            other = 'l' if suffix == 'r' else 'r'
            for alignment in ('preserve_suffix', 'reverse_suffix'):
                ys = (suffix, other) if alignment == 'preserve_suffix' else (other, suffix)
                fixed = {'X_A': x + suffix, 'X_B': x + other, 'Y_A': y + ys[0], 'Y_B': y + ys[1]}
                for placement in ('before_clause', 'after_clause'):
                    tokens, positions = [], []
                    for ci, (a, b, neg) in enumerate(CLAUSES):
                        chunk = [('X_' + ('A', 'B')[a], ci, 'ARG1'), ('Y_' + ('A', 'B')[b], ci, 'ARG2')]
                        if neg:
                            chunk.insert(0 if placement == 'before_clause' else len(chunk), ('N', ci, 'N'))
                        for token, clause, slot in chunk:
                            tokens.append(token); positions.append({'clause': clause, 'slot': slot})
                    schemas.append({'family': 'ROLE10', 'slot_order': None, 'negative_placement': placement,
                        'pattern': tokens, 'positions': positions, 'fixed': fixed, 'pair': [x, y],
                        'first_role_A_suffix': suffix, 'cross_role_alignment': alignment})
    for s in schemas:
        if s['family'] == 'ATOMIC14':
            rename = {}
            s['surface'] = tuple(rename.setdefault(t, len(rename)) for t in s['pattern'])
        else:
            s['surface'] = tuple(s['fixed'].get(t, '$N') for t in s['pattern'])
    return schemas


def binding(schema, words):
    if len(words) != len(schema['pattern']):
        return None
    values = dict(schema['fixed'])
    for symbol, word in zip(schema['pattern'], words):
        if not LITERAL.fullmatch(word):
            return None
        if symbol in values:
            if values[symbol] != word:
                return None
        elif word in values.values():
            return None
        else:
            values[symbol] = word
    return values if len(set(values.values())) == len(values) else None


def census(paragraphs, schemas):
    denoms, matches = {}, []
    bylen = {n: [(i, s) for i, s in enumerate(schemas) if len(s['pattern']) == n] for n in (10, 14)}
    for edition in EDITIONS:
        denoms[edition] = {}
        for length in (10, 14):
            total, good, failures = 0, 0, collections.Counter()
            bad_raw = bad_seam = bad_both = 0
            for paragraph in paragraphs[edition]:
                flat = paragraph['flat']
                for offset in range(max(0, len(flat) - length + 1)):
                    total += 1
                    run = flat[offset:offset + length]
                    reasons = eligibility(run)
                    if reasons:
                        failures.update(reasons)
                        raw_problem = 'NON_LITERAL_GROUP' in reasons
                        seam_problem = bool(reasons - {'NON_LITERAL_GROUP'})
                        bad_raw += raw_problem
                        bad_seam += seam_problem
                        bad_both += raw_problem and seam_problem
                        continue
                    good += 1
                    words = [g['ivtff_group_raw'] for g in run]
                    for si, schema in bylen[length]:
                        values = binding(schema, words)
                        if values is not None:
                            matches.append({'schema_index': si, 'edition': edition,
                                'paragraph_id': paragraph['original']['id'], 'start_offset': offset,
                                'end_offset_exclusive': offset + length, 'mapping': values,
                                'source_ids': [g['source_group_id'] for g in run], 'words': words})
            denoms[edition][str(length)] = {'total_windows': total, 'eligible_windows': good,
                'ineligible_windows': total - good, 'invalid_raw': bad_raw, 'invalid_seam': bad_seam,
                'both_invalid': bad_both, 'failure_reasons_nonexclusive': dict(failures)}
    return denoms, matches


def fixture_line(words, start=True, end=True, locus='f2r.1'):
    count = len(words)
    return {'metadata': {'kind': 'P', 'edition': 'ZL3b', 'page': 'f2r', 'locus': locus,
        'paragraph_start': str(int(start)), 'paragraph_end': str(int(end)),
        'source_row_index': str(number('f2r', locus)), 'source_group_count': str(count)},
        'groups': [{'source_group_id': f'ZL3b|{locus}|G{i:03d}', 'source_group_index': str(i),
            'ivtff_group_raw': word, 'left_separator': 'LINE_START' if i == 1 else 'DEFINITE_SPACE',
            'right_separator': 'LINE_END' if i == count else 'DEFINITE_SPACE'} for i, word in enumerate(words, 1)]}


def fixtures(schemas):
    counts = collections.Counter()
    for si, schema in enumerate(schemas):
        values = dict(schema['fixed']) or {'A': 'zza', 'B': 'zzb', 'P': 'zzpred'}
        values['N'] = 'zzneg'
        words = [values[t] for t in schema['pattern']]
        block = collect_complete([fixture_line(words)])['ZL3b'][0]['flat']
        assert not eligibility(block) and binding(schema, words) == values, si
        counts['positive_raw_branch'] += 1
        # Wrong second argument in the first self-cell and first cross-cell.
        for clause in (0, 2):
            damaged = words[:]
            idx = next(i for i, p in enumerate(schema['positions']) if p == {'clause': clause, 'slot': 'ARG2'})
            alternatives = (values['A'], values['B']) if schema['family'] == 'ATOMIC14' else (values['Y_A'], values['Y_B'])
            damaged[idx] = next(v for v in alternatives if v != damaged[idx])
            assert binding(schema, damaged) is None, (si, clause)
            counts['wrong_self_cell' if clause == 0 else 'wrong_cross_cell'] += 1
        ni = [i for i, t in enumerate(schema['pattern']) if t == 'N']
        damaged = words[:]; damaged[ni[1]] = 'zzother'
        assert binding(schema, damaged) is None
        counts['wrong_negator_identity'] += 1
        damaged = words[:]; damaged.pop(ni[1])
        assert binding(schema, damaged) is None
        counts['dropped_negator'] += 1
        damaged = copy.deepcopy(block); damaged[0]['right_separator'] = 'UNCERTAIN_SPACE'
        assert eligibility(damaged)
        counts['illegal_space'] += 1
        damaged = copy.deepcopy(block); damaged[0]['ivtff_group_raw'] += '?'
        assert eligibility(damaged)
        counts['unknown_raw_glyph'] += 1
        assert not collect_complete([fixture_line(words, start=False)])['ZL3b']
        assert not collect_complete([fixture_line(words, end=False)])['ZL3b']
        counts['missing_complete_boundary'] += 1
        split = len(words) // 2
        two = [fixture_line(words[:split], end=False), fixture_line(words[split:], start=False, locus='f2r.2')]
        grouped = collect_complete(two)['ZL3b'][0]['flat']
        assert not eligibility(grouped) and binding(schema, [g['ivtff_group_raw'] for g in grouped]) == values
        counts['positive_crossline'] += 1
        damaged = copy.deepcopy(grouped); damaged[split]['source_group_index'] = '2'
        assert eligibility(damaged)
        counts['invalid_crossline_start'] += 1
        two[1]['metadata']['locus'] = 'f2r.3'
        assert not collect_complete(two)['ZL3b']
        counts['missing_physical_line'] += 1
    # Whole-host uncertainty outside the run must not remove an otherwise valid run.
    schema = schemas[0]; values = {'A': 'zza', 'B': 'zzb', 'P': 'zzpred', 'N': 'zzneg'}
    words = [values[t] for t in schema['pattern']]
    block = collect_complete([fixture_line(['?'] + words + ['?'])])['ZL3b'][0]['flat']
    assert eligibility(block) and not eligibility(block[1:-1])
    counts['outside_uncertainty_preserved'] += 1
    return dict(counts)


def main():
    lock = readj(BASE / 'src/PREREG_LOCK.json')
    hashes = {}
    for path, expected in lock['files'].items():
        hashes[path] = digest(ROOT / path)
        verify(hashes[path] == expected, 'Locked input hash: ' + path)
    verify(lock['pre_target_census'] is True, 'Registered before target census')
    begin, end = [dt.datetime.fromisoformat(lock[k]) for k in ('registered_utc', 'deadline_utc')]
    verify((end - begin).total_seconds() == 1500, 'Inclusive preregistered 25-minute budget')
    spec = readj(BASE / 'src/SPEC.json')
    source = readj(BASE / 'src/SOURCE.json')
    raw = (ROOT / source['whole_cache_path']).read_bytes()
    verify(hashlib.sha256(raw).hexdigest() == source['whole_cache_sha256'], 'Whole source raw hash')
    for tag in ('complete_chapter', 'corrected_argument'):
        a, b = source[tag + '_byte_range']
        verify(hashlib.sha256(raw[a:b]).hexdigest() == source[tag + '_sha256'], 'Source interval hash: ' + tag)
    verify(spec['clauses'] == [{'arg1': a, 'arg2': b, 'negative': neg} for a, b, neg in CLAUSES], 'Fixed source four-cell order')
    allow = set(readj(ROOT / spec['allowed_selectors_spec'])['allowed_selectors'])
    verify(len(allow) == 179 and not any(p.startswith('f84') or p == 'f116v' for p in allow), 'Unchanged 179-selector scope')
    cached, seen_lines, seen_groups = [], set(), set()
    for path in spec['raw_caches']:
        content = readj(ROOT / path)
        # Selector authorization precedes creation of each cached group dictionary.
        for line in content['lines']:
            meta = line['metadata']
            if meta['page'] not in allow or meta['page'].startswith('f84') or meta['page'] == 'f116v':
                raise AssertionError('Forbidden cached selector')
            linekey = meta['edition'], meta['locus']
            assert linekey not in seen_lines
            seen_lines.add(linekey)
            groups = [dict(zip(content['group_columns'], values)) for values in line['groups']]
            assert len(groups) == int(meta['source_group_count'])
            assert [int(g['source_group_index']) for g in groups] == list(range(1, len(groups) + 1))
            for g in groups:
                assert g['source_group_id'] not in seen_groups
                assert g['source_group_id'] == f"{meta['edition']}|{meta['locus']}|G{int(g['source_group_index']):03d}"
                seen_groups.add(g['source_group_id'])
            cached.append({'metadata': meta, 'groups': groups})
    verify(True, 'Six guarded caches: selectors, source IDs, line uniqueness, group counts and order')
    paragraphs = collect_complete(cached)
    prior = readj(ROOT / spec['paragraphs'])
    for edition in EDITIONS:
        rebuilt = {p['original']['id']: p['original'] for p in paragraphs[edition]}
        original = {p['id']: p for p in prior[edition]}
        verify(rebuilt == original, 'Independent complete-paragraph reconstruction: ' + edition)
    verify([len(paragraphs[e]) for e in EDITIONS] == [659, 690, 0], 'Complete paragraph census 659/690/0')
    bank = readj(ROOT / spec['bank'])
    verify(len(bank) == 22 and len({tuple(p) for p in bank}) == 22, 'All 22 fixed ordered stem pairs')
    schemas = make_schemas(bank)
    verify(collections.Counter(s['family'] for s in schemas) == {'ATOMIC14': 12, 'ROLE10': 176}, 'All 188 raw branches generated independently')
    fixture_counts = fixtures(schemas)
    verify(fixture_counts['positive_raw_branch'] == 188, 'Every raw branch positive fixture and registered negatives')
    # The table is symmetric under renaming, and complementation plus reversed polarity.
    table = {(a, b): a != b for a in (0, 1) for b in (0, 1)}
    verify([table[a, b] for a, b, _ in CLAUSES] == [False, False, True, True], 'Symbolic relation table')
    verify(all(table[a, b] == table[1-a, 1-b] for a, b in table), 'A/B name-swap ambiguity retained')
    verify(all((not table[a, b]) == neg for a, b, neg in CLAUSES), 'Complement relation with inverted polarity remains an alternative')
    denoms, matches = census(paragraphs, schemas)
    comparison = compare_outputs(schemas, paragraphs, denoms, matches)
    return {'status': 'PASS', 'completed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'validator_sha256': digest(__file__), 'runner_read_or_imported': False,
        'independent_cache_reconstruction': True, 'checks': checks, 'locked_hashes': hashes,
        'paragraph_counts': {e: len(paragraphs[e]) for e in EDITIONS}, 'window_census': denoms,
        'raw_branch_counts': dict(collections.Counter(s['family'] for s in schemas)),
        'surface_class_counts': {f: len({s['surface'] for s in schemas if s['family'] == f}) for f in ('ATOMIC14', 'ROLE10')},
        'match_count': len(matches), 'fixtures': fixture_counts, 'output_comparison': comparison,
        'scientific_ceiling': 'Exact extraction and fixed-writer capacity only; no semantic truth, source identity, metal name, polarity meaning, independent confirmation, or significance.'}


def compare_outputs(schemas, paragraphs, denoms, matches):
    actual = readj(BASE / 'artifacts/SCHEMAS.json')
    verify(len(actual) == len(schemas) == 188, 'Published schema row coverage')
    surface_to_class, class_to_surface = {}, {}
    raw_counts = collections.Counter()
    anonymous = collections.defaultdict(set)
    for i, (want, got) in enumerate(zip(schemas, actual)):
        family = want['family']; raw_counts[family] += 1
        expected_id = ('A' if family == 'ATOMIC14' else 'R') + f'{raw_counts[family]:03d}'
        assert got['id'] == expected_id and got['family'] == family
        pattern = [want['fixed'].get(t, t) for t in want['pattern']]
        assert got['pattern'] == pattern
        assert got['negative_placement'] == want['negative_placement']
        if family == 'ATOMIC14':
            assert got['slot_order'] == want['slot_order']
            assert got['variables'] == ['P', 'N', 'A', 'B']
        else:
            assert got['variables'] == ['N']
            assert got['ordered_stems'] == want['pair'] and got['bank_index'] == (i - 12) // 8
            assert got['forms'] == want['fixed']
            assert got['first_role_A_suffix'] == want['first_role_A_suffix']
            assert got['cross_role_alignment'] == want['cross_role_alignment']
        expected_roles = []
        for pos in want['positions']:
            ci, slot = pos['clause'], pos['slot']
            a, b, neg = CLAUSES[ci]
            argument = a if slot == 'ARG1' else b if slot == 'ARG2' else None
            label = ('X_ARG1' if slot == 'ARG1' else 'Y_ARG2' if slot == 'ARG2' else slot) if family == 'ROLE10' else slot
            expected_roles.append({'clause': ci, 'slot': label, 'argument': argument, 'reported_J': not neg})
        assert got['roles'] == expected_roles
        rename = {}; skeleton = [rename.setdefault(t, len(rename)) for t in pattern]
        assert got['anonymous_equality_skeleton'] == skeleton
        anonymous[family].add(tuple(skeleton))
        key = (family, want['surface']); eq = got['equivalence_class']
        assert surface_to_class.setdefault(key, eq) == eq
        assert class_to_surface.setdefault(eq, key) == key
        assert isinstance(got['semantic_mapping'], str) and got['semantic_mapping']
    verify(True, 'Every published branch pattern, variable, role-position, mapping and equality skeleton')
    verify(len(surface_to_class) == len(class_to_surface), 'Exact surface-equivalence classes and retained semantic maps')
    published_census = readj(BASE / 'artifacts/CENSUS.json')
    ids = [s['id'] for s in actual]
    for edition in EDITIONS:
        got = published_census[edition]
        assert got['complete_paragraphs'] == len(paragraphs[edition])
        assert got['total_groups'] == sum(len(p['flat']) for p in paragraphs[edition])
        for length in ('10', '14'):
            want = denoms[edition][length]
            assert got['windows'][length] == {'total': want['total_windows'], 'eligible': want['eligible_windows'],
                'invalid_raw': want['invalid_raw'], 'invalid_seam': want['invalid_seam'], 'both_invalid': want['both_invalid']}
        counts = collections.Counter(m['schema_index'] for m in matches if m['edition'] == edition)
        assert got['branch_counts'] == {sid: counts[i] for i, sid in enumerate(ids)}
    verify(True, 'Every reader, 10/14 window denominator, invalid overlap and all 188 branch counts')
    # The independent exhaustive enumeration is zero; there are consequently no
    # real source-position predictions or complete candidate hosts to compare.
    verify(matches == [], 'Independent exhaustive fixed-writer enumeration has no candidate')
    verify(readj(BASE / 'artifacts/MATCHES.json') == matches, 'All candidate matches and position records: empty, not sampled')
    verify(readj(BASE / 'artifacts/CANDIDATE_PARAGRAPHS.json') == [], 'All full candidate hosts: empty')
    result = readj(BASE / 'artifacts/RESULT.json')
    assert result['status'] == 'COMPLETE_FIXED_FOUR_CELL_CAPACITY_CENSUS' and result['primary'] == 'ZL3b'
    assert result['all_raw_branches'] == 188
    assert result['equivalence'] == {'literal_equivalence_classes': len(surface_to_class),
        'anonymous_skeleton_counts': {f: len(v) for f, v in anonymous.items()}, 'raw_branches': dict(raw_counts)}
    for edition in EDITIONS:
        for family, length in (('ATOMIC14', '14'), ('ROLE10', '10')):
            capacity = denoms[edition][length]['eligible_windows']
            decision = 'NO_NATIVE_PARAGRAPH_CAPACITY' if not paragraphs[edition] else 'NO_ELIGIBLE_WINDOWS' if not capacity else 'NO_REALIZATION_IN_FIXED_COMPLETE_PARAGRAPHS'
            assert result['decisions'][edition][family] == {'matches': 0, 'unique_host_paragraphs': 0,
                'eligible_windows': capacity, 'decision': decision}
    assert result['reported_source_table'] == [[False, True], [True, False]]
    assert result['independent_confirmation_capacity'] == result['confirmed_translated_words'] == result['whole_source_duties_expressed'] == 0
    assert result['source_copy_identified'] is False and result['significance_claim'] is False
    assert len(result['semantic_symmetries']) >= 4
    verify(True, 'Published decisions, symbolic table and semantic/confirmation ceilings')
    names = ['SCHEMAS.json', 'CENSUS.json', 'MATCHES.json', 'CANDIDATE_PARAGRAPHS.json', 'RESULT.json']
    return {'artifact_hashes': {name: digest(BASE / 'artifacts' / name) for name in names},
        'checked_raw_branches': 188, 'checked_branch_reader_cells': 564,
        'all_matches_compared': True, 'all_hosts_compared': True,
        'real_positive_position_records': 0, 'synthetic_position_predictions_covered': 188,
        'no_raw_source_publication': True}


if __name__ == '__main__':
    try:
        result = main()
    except Exception as exc:
        result = {'status': 'FAIL', 'error': str(exc), 'traceback': traceback.format_exc(), 'checks': checks,
            'validator_sha256': digest(__file__), 'runner_read_or_imported': False}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'error', 'paragraph_counts', 'match_count') if k in result}))
    sys.exit(0 if result['status'] == 'PASS' else 1)
