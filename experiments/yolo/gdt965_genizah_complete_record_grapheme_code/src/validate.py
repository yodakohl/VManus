#!/usr/bin/env python3
"""Independent source, intake, certificate and witness validation for GDT965.

Never imports GDT965 run.py. Exhaustive replay alone reuses GDT900's engine.
No timestamp or elapsed timing is serialized in this reproducible receipt.
"""
from __future__ import annotations
import argparse, collections, csv, gzip, hashlib, importlib.util, json, re, sys, time, unicodedata
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
ART = E / 'artifacts'
G915 = ROOT / 'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
TARGET = ROOT / 'experiments/yolo/gdt963_dioscorides_complete_content_code/artifacts/TARGET_FRAMES.json.gz'
EDS = ('ZL3b', 'IT2a', 'RF1b')
IDS = ('PEACH', 'POMEGRANATE', 'QUINCE')
CHECKS = []

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def check(name, condition, **details):
    CHECKS.append({'name': name, 'ok': bool(condition), **details})

def require(condition, message):
    if not condition:
        raise ValueError(message)

def source_clusters(word):
    units = []
    for char in unicodedata.normalize('NFD', word):
        if unicodedata.combining(char):
            require(bool(units), 'orphan combining mark')
            units[-1] += char
        else:
            require('\u05d0' <= char <= '\u05ea', 'non-Hebrew selected source base')
            units.append(char)
    return units

def replay_source(source):
    blocks = source['transcription']
    require([b['face'] for b in blocks] == ['recto', 'verso', 'verso, right margin'], 'transcription faces')
    for block, count in zip(blocks, (21, 21, 4)):
        require([line['n'] for line in block['lines']] == list(range(1, count + 1)), 'source line numbers')
    r, v, _ = [[line['text'] for line in b['lines']] for b in blocks]
    require(r[4].startswith('אלכוך.'), 'peach start')
    require(r[12].count('אלרמֹאן') == 1 and r[12].endswith('אלרמֹאן'), 'pomegranate boundary')
    require(v[4].count('אלספרגֹל') == 1 and v[4].endswith('אלספרגֹל'), 'quince boundary')
    require(v[14].startswith('אלתֹפאחֹ'), 'apple exclusive boundary')
    spans = [r[4:12] + [r[12].split('אלרמֹאן')[0].rstrip()],
             ['אלרמֹאן'] + r[13:] + v[:4] + [v[4].split('אלספרגֹל')[0].rstrip()],
             ['אלספרגֹל'] + v[5:14]]
    require([r['id'] for r in source['records']] == list(IDS), 'source role identity/order')
    rebuilt, errors = {}, []
    for rid, lines, stored, size in zip(IDS, spans, source['records'], ((64, 285), (102, 464), (75, 326))):
        words = ' '.join(lines).replace('.', '').replace(';', '').split()
        graph_words = [source_clusters(word) for word in words]
        units = [unit for word in graph_words for unit in word]
        expected = {'lines': lines, 'words': words, 'grapheme_words': graph_words,
                    'word_count': len(words), 'grapheme_count': len(units),
                    'unit_counts': dict(collections.Counter(units)), 'word_type_count': len(set(words))}
        errors.extend(rid + ':' + key for key, value in expected.items() if stored.get(key) != value)
        require((len(words), len(units)) == size, 'audited source denominator')
        rebuilt[rid] = dict(expected, id=rid, units=units)
    marked = collections.Counter(u for r in rebuilt.values() for u in r['units'] if len(u) > 1)
    require(marked == {'גֹ': 16, 'צֹ': 7, 'ץֹ': 3, 'טֹ': 2, 'מֹ': 1, 'דֹֹֹ': 1}, 'mark inventory')
    require(len({u for r in rebuilt.values() for u in r['units']}) == 32, 'global source unit inventory')
    check('full_transcription_boundary_and_grapheme_replay', not errors, errors=errors,
          words=[rebuilt[k]['word_count'] for k in IDS], clusters=[rebuilt[k]['grapheme_count'] for k in IDS])
    return rebuilt

def replay_frames():
    spec = read(G915 / 'src/SPEC.json')
    require(tuple(spec['editions']) == EDS, 'registered editions')
    frames = []
    for edition in EDS:
        pages = collections.defaultdict(list)
        for phase in ('DISCOVERY', 'EVALUATION'):
            cache = read(G915 / 'artifacts' / f'SOURCE_{phase}_{edition}.json')
            for row in cache['lines']:
                meta = row['metadata']; page = meta['page']
                require(page in spec['partitions'][phase], 'unregistered cache page')
                require(not page.startswith('f84') and page != 'f116v', 'forbidden cache page')
                if meta['section'] == 'H' and meta['kind'] == 'P' and page != 'f1r':
                    pages[page].append((meta, [dict(zip(cache['group_columns'], g)) for g in row['groups']]))
        for page in sorted(pages):
            rows = sorted(pages[page], key=lambda x: int(x[0]['source_row_index']))
            reasons, groups, words = [], [], []
            for meta, gs in rows:
                locus = meta['locus']
                if not gs or [int(g['source_group_index']) for g in gs] != list(range(1, int(meta['source_group_count']) + 1)):
                    reasons.append([locus, 'INCOMPLETE_GROUP_INDICES'])
                if any(re.fullmatch('[a-z]+', g['ivtff_group_raw']) is None for g in gs):
                    reasons.append([locus, 'NONLITERAL_GROUP'])
                if gs and (gs[0]['left_separator'] != 'LINE_START' or gs[-1]['right_separator'] != 'LINE_END'):
                    reasons.append([locus, 'OUTER_BOUNDARY'])
                for left, right in zip(gs, gs[1:]):
                    if left['right_separator'] != right['left_separator'] or left['right_separator'] not in ('DEFINITE_SPACE', 'DRAWING_INTERRUPTION'):
                        reasons.append([locus, 'UNKNOWN_INTERNAL_SEAM', left['source_group_id'], right['source_group_id']])
                words.extend(g['ivtff_group_raw'] for g in gs)
                groups.extend(dict(locus=locus, **g) for g in gs)
            text = None if reasons else ''.join(words)
            frames.append({'id': edition + ':' + page, 'edition': edition, 'page': page,
                           'physical_leaf': re.match(r'f\d+', page).group(), 'eligible': not reasons,
                           'reasons': reasons, 'line_count': len(rows), 'group_count': len(groups),
                           'groups': groups, 'text': text, 'characters': len(text) if text else None,
                           'alphabet': sorted(set(text)) if text else []})
    with gzip.open(TARGET, 'rt', encoding='utf-8') as handle:
        stored = json.load(handle)
    check('original_six_cache_target_reconstruction', frames == stored, frames=len(frames))
    check('all_target_denominators', len(frames) == 357 and all(sum(f['edition'] == ed for f in frames) == 119 for ed in EDS))
    return frames

def consequences(units, text):
    require(bool(text), 'empty literal target')
    n, m = len(units), len(text); first, last = units[0], units[-1]
    nf, nl = units.count(first), units.count(last)
    cf, cl = text.count(text[0]), text.count(text[-1]); same = first == last
    upper = (m - n + nf) // nf if same else None
    borders = [k for k in range(1, max(0, upper) + 1) if text[:k] == text[-k:]] if same else None
    obs = {'required_characters': n, 'observed_characters': m, 'first_source_unit': first,
           'required_first_character_count': nf, 'target_first_character': text[0],
           'observed_first_character_count': cf, 'last_source_unit': last,
           'required_last_character_count': nl, 'target_last_character': text[-1],
           'observed_last_character_count': cl, 'same_boundary_unit': same,
           'boundary_code_max_length': upper, 'allowed_equal_boundary_lengths': borders}
    bad = [label for label, condition in [('NONEMPTY_LENGTH', m < n), ('FIRST_UNIT_RECURRENCE', cf < nf),
           ('LAST_UNIT_RECURRENCE', cl < nl), ('SAME_BOUNDARY_UNIT', same and not borders)] if condition]
    return obs, bad

def witness_ok(code, equations):
    required = {unit for units, _ in equations for unit in units}
    if not isinstance(code, dict) or set(code) != required:
        return False
    values = list(code.values())
    if any(not isinstance(v, str) or not v for v in values):
        return False
    if any(a.startswith(b) or b.startswith(a) for i, a in enumerate(values) for b in values[i + 1:]):
        return False
    return all(''.join(code[u] for u in units) == text for units, text in equations)

def engine():
    directory = ROOT / 'experiments/yolo/gdt900_cumanicus_complete_trilingual_tables/src'
    sys.path.insert(0, str(directory)); sys.setrecursionlimit(10000)
    spec = importlib.util.spec_from_file_location('gdt965_validation_gdt900', directory / 'run.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def replay_joint(old, records, domains, deadline):
    order = sorted(IDS, key=lambda k: (len(domains[k]), k))
    def visit(index, key, chosen, leaves):
        if time.monotonic() > deadline:
            raise old.Budget
        if index == len(order):
            yield {'code': key, 'assignments': chosen}; return
        role = order[index]
        for frame in sorted(domains[role], key=lambda f: f['id']):
            if frame['physical_leaf'] not in leaves:
                for code in old.extend_word(records[role]['units'], frame['text'], key, deadline):
                    yield from visit(index + 1, code, dict(chosen, **{role: frame['id']}), leaves | {frame['physical_leaf']})
    return visit(0, {}, {}, set())

def validate_artifacts(records, frames, old):
    names = ('NECESSARY_CASES.json', 'ALL_CASES.json', 'EQUIVALENT_OBSERVATIONS.json', 'CANDIDATE_TABLE.tsv', 'RESULT.json')
    missing = [name for name in names if not (ART / name).exists()]
    check('complete_evaluation_artifacts', not missing, missing=missing)
    if missing:
        return {'status': 'NOT_EVALUATED'}
    initial, cases, result = read(ART / names[0]), read(ART / names[1]), read(ART / names[4])
    expected = []
    for frame in frames:
        for rid in IDS:
            record = records[rid]
            case = {'id': frame['id'] + ':' + rid, 'frame_id': frame['id'], 'edition': frame['edition'],
                    'page': frame['page'], 'physical_leaf': frame['physical_leaf'], 'source_id': rid,
                    'source_group_count': record['word_count'], 'target_group_count': frame['group_count'],
                    'independent_confirmation_capacity': 0}
            if not frame['eligible']:
                case.update(status='UNKNOWN_SOURCE', source_reasons=frame['reasons'])
            else:
                obs, bad = consequences(record['units'], frame['text'])
                case.update(observations=obs, contradictions=bad, status='CONTRADICTED_NECESSARY' if bad else 'PENDING')
            expected.append(case)
    check('all_1071_four_necessary_certificates', initial == expected and len(expected) == 1071)
    prediction_fields = ['candidate', 'source_id', 'edition', 'page', 'minimum_characters', 'first_unit',
                         'minimum_first_character_count', 'last_unit', 'minimum_last_character_count',
                         'same_boundary_code_required', 'condition']
    predicted = []
    for case in expected:
        units = records[case['source_id']]['units']
        values = [case['id'], case['source_id'], case['edition'], case['page'], len(units), units[0],
                  units.count(units[0]), units[-1], units.count(units[-1]), units[0] == units[-1],
                  'All four necessary conditions and exact shared prefix code; whole-source UNKNOWN if target is nonliteral']
        predicted.append(dict(zip(prediction_fields, map(str, values))))
    with (ART / 'PREDICTIONS.tsv').open(encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t'); header, predictions = reader.fieldnames, list(reader)
    check('all_1071_preregistered_source_page_predictions', header == prediction_fields and predictions == predicted)
    require(len(cases) == len(expected), 'final case denominator')
    fmap = {f['id']: f for f in frames}; errors, incomplete = [], []; replayed = 0
    for original, case in zip(expected, cases):
        cid = original['id']; status = case.get('status')
        if any(case.get(k) != v for k, v in original.items() if k != 'status'):
            errors.append(cid + ':identity_or_observations')
        if original['status'] != 'PENDING':
            if case != original:
                errors.append(cid + ':fixed_status_or_source_unknown_changed')
            continue
        seq, text = records[original['source_id']]['units'], fmap[original['frame_id']]['text']
        if status == 'SAT_WITNESS':
            if not witness_ok(case.get('code'), [(seq, text)]):
                errors.append(cid + ':invalid_code')
        elif status == 'UNSAT_EXACT':
            try:
                if next(old.extend_word(seq, text, {}, time.monotonic() + 2), None) is not None:
                    errors.append(cid + ':false_unsat')
                else:
                    replayed += 1
            except old.Budget:
                incomplete.append(cid)
        elif status != 'UNKNOWN_COMPUTATION':
            errors.append(cid + ':unregistered_status')
        if status != 'SAT_WITNESS' and 'code' in case:
            errors.append(cid + ':unexpected_code')
    check('complete_cases_and_local_witnesses', not errors, error_count=len(errors), errors=errors[:60])
    check('claimed_exact_local_unsat_replay', not incomplete, replayed=replayed, incomplete=incomplete)
    groups = collections.defaultdict(list)
    for case in cases:
        sig = {'source_id': case['source_id'], 'observations': case.get('observations'),
               'status': case['status'], 'contradictions': case.get('contradictions')}
        groups[json.dumps(sig, ensure_ascii=False, sort_keys=True)].append(case['id'])
    check('equivalent_observations_all_identities', read(ART / names[2]) ==
          [{'signature': json.loads(key), 'cases': values} for key, values in groups.items()])
    fields = ['id', 'source_id', 'edition', 'page', 'physical_leaf', 'status', 'required_characters',
              'observed_characters', 'required_first_character_count', 'observed_first_character_count',
              'required_last_character_count', 'observed_last_character_count', 'same_boundary_unit',
              'allowed_equal_boundary_lengths', 'contradictions', 'independent_confirmation_capacity']
    expected_rows = []
    for case in cases:
        merged = dict(case, **case.get('observations', {})); row = {}
        for field in fields:
            value = merged.get(field)
            row[field] = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else '' if value is None else str(value)
        expected_rows.append(row)
    with (ART / names[3]).open(encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t'); actual_fields, rows = reader.fieldnames, list(reader)
    check('complete_candidate_table', actual_fields == fields and rows == expected_rows, rows=len(rows))
    joint_errors, joint_incomplete = [], []; joints = result.get('joint', {})
    require(set(joints) == set(EDS), 'joint edition keys')
    for ed in EDS:
        joint = joints[ed]; status, witnesses = joint.get('status'), joint.get('witnesses', [])
        unknown = [f['id'] for f in frames if f['edition'] == ed and not f['eligible']]
        domains = {rid: [fmap[c['frame_id']] for c in cases if c['edition'] == ed and c['source_id'] == rid
                        and c['status'] in ('SAT_WITNESS', 'UNKNOWN_COMPUTATION')] for rid in IDS}
        empty = [rid for rid in IDS if not domains[rid]]
        leaves = {f['physical_leaf'] for domain in domains.values() for f in domain}
        if joint.get('source_unknown_frames') != unknown:
            joint_errors.append(ed + ':source_unknowns_not_preserved')
        if joint.get('whole_scope_exclusion') != (not unknown and isinstance(status, str) and status.startswith('UNSAT')):
            joint_errors.append(ed + ':whole_scope_overclaim')
        if empty:
            if status != 'UNSAT_LITERAL_DOMAIN' or joint.get('empty_roles') != empty or witnesses or joint.get('complete_enumeration') is not True:
                joint_errors.append(ed + ':empty_literal_roles')
        elif len(leaves) < 3:
            if status != 'NO_LITERAL_CAPACITY' or witnesses or joint.get('complete_enumeration') is not True:
                joint_errors.append(ed + ':physical_leaf_capacity')
        else:
            if joint.get('source_search_order') != sorted(IDS, key=lambda rid: (len(domains[rid]), rid)):
                joint_errors.append(ed + ':source_search_order')
            statuses = {'SAT_AT_LEAST_TWO': (2, False), 'SAT_ONE_EXHAUSTIVE': (1, True),
                        'SAT_ONE_UNRESOLVED': (1, False), 'UNSAT_LITERAL_JOINT': (0, True), 'UNKNOWN_JOINT': (0, False)}
            if (len(witnesses), joint.get('complete_enumeration')) != statuses.get(status):
                joint_errors.append(ed + ':joint_status_accounting')
            if status in ('UNSAT_LITERAL_JOINT', 'SAT_ONE_EXHAUSTIVE'):
                try:
                    replay = []
                    for w in replay_joint(old, records, domains, time.monotonic() + 120):
                        replay.append(w)
                        if len(replay) > 1:
                            break
                    if replay != witnesses:
                        joint_errors.append(ed + ':false_exhaustive_joint')
                except old.Budget:
                    joint_incomplete.append(ed)
        unique = set()
        for witness in witnesses:
            assignments = witness.get('assignments', {})
            if set(assignments) != set(IDS) or any(assignments[rid] not in {f['id'] for f in domains[rid]} for rid in IDS):
                joint_errors.append(ed + ':witness_assignment_domain'); continue
            chosen = [fmap[assignments[rid]] for rid in IDS]
            equations = [(records[rid]['units'], fmap[assignments[rid]]['text']) for rid in IDS]
            if len({f['physical_leaf'] for f in chosen}) != 3 or not witness_ok(witness.get('code'), equations):
                joint_errors.append(ed + ':invalid_joint_witness')
            unique.add(json.dumps(witness, ensure_ascii=False, sort_keys=True))
        if len(unique) != len(witnesses):
            joint_errors.append(ed + ':duplicate_joint_witness')
    check('joint_domains_capacity_unknowns_and_witnesses', not joint_errors, errors=joint_errors)
    check('claimed_exhaustive_joint_replay', not joint_incomplete, incomplete=joint_incomplete)
    counts = dict(collections.Counter(c['status'] for c in cases))
    check('result_denominators_and_claim_limits', result.get('status') == 'FIXED_PANEL_EVALUATED' and
          result.get('case_count') == 1071 and result.get('counts') == counts and
          result.get('exact_local_search_count') == sum(c['status'] == 'PENDING' for c in expected) and
          result.get('observation_groups') == len(groups) and result.get('confirmed_words') == 0 and
          result.get('independent_confirmation_capacity') == 0)
    return {'evaluation': 'ARTIFACTS_CHECKED', 'cases': len(cases), 'counts': counts,
            'joint_statuses': {ed: joints[ed]['status'] for ed in EDS},
            'target_frames_by_edition': {ed: {'literal': sum(f['edition'] == ed and f['eligible'] for f in frames),
                                             'source_unknown': sum(f['edition'] == ed and not f['eligible'] for f in frames)} for ed in EDS},
            'incomplete_search_replays': len(incomplete) + len(joint_incomplete)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true', help='do not read target frames')
    args = parser.parse_args(); summary = {}
    try:
        lock = E / 'PREREG_LOCK.json'; lock_errors = []
        if lock.exists():
            for relative, expected in read(lock)['files'].items():
                path = ROOT / relative
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                    lock_errors.append(relative)
            check('registered_input_lock', not lock_errors, errors=lock_errors)
        else:
            check('registered_input_lock', args.source_only, status='NOT_REGISTERED')
        records = replay_source(read(E / 'src/SOURCE.json'))
        if args.source_only:
            summary = {'evaluation': 'SOURCE_ONLY_NOT_EVALUATED'}
        else:
            require(lock.exists() and not lock_errors, 'registration required before target validation')
            summary = validate_artifacts(records, replay_frames(), engine())
    except Exception as error:
        check('validation_execution', False, error_type=type(error).__name__, message=str(error))
    ok = all(c['ok'] for c in CHECKS)
    status = 'SOURCE_VALIDATION_PASS' if ok and args.source_only else 'VALIDATION_PASS' if ok else 'VALIDATION_FAIL'
    output = {'experiment_id': 'GDT965', 'status': status,
              'independent_algorithm': 'full-transcription source replay; original-cache frame reconstruction; four certificate replay; independent code witnesses; GDT900 exhaustive search replay',
              'checks': CHECKS, 'summary': summary,
              'claim_ceiling': 'Fixed source/code validation only; no confirmed meanings; source unknowns remain undecided.'}
    filename = 'SOURCE_VALIDATION.json' if args.source_only else 'VALIDATION.json'
    (ART / filename).write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'checks': len(CHECKS),
                      'failed_checks': [c['name'] for c in CHECKS if not c['ok']], **summary}, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main())
