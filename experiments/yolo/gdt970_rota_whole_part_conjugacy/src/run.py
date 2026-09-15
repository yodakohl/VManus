#!/usr/bin/env python3
"""Fixed necessary whole-part consequence; no event decoder or language model."""
import argparse
import collections
import csv
import datetime
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re
import time

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
D = R / 'research_registry/work_batches/ten_hours_20260915'
P = R / 'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
Q = R / 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs'
EDS = ['ZL3b', 'IT2a', 'RF1b']
DECISIONS = ['TOO_SHORT', 'UNEQUAL_LENGTH', 'UNEQUAL_INVENTORY', 'UNEQUAL_CYCLIC_ORDER', 'NECESSARY_CONSEQUENCE_ONLY']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (E / 'artifacts' / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')


def canonical(s):
    """Least character rotation, using two competing start indices."""
    if not s:
        return ''
    doubled, n, i, j, k = s + s, len(s), 0, 1, 0
    while i < n and j < n and k < n:
        a, b = doubled[i + k], doubled[j + k]
        if a == b:
            k += 1
            continue
        if a > b:
            i += k + 1
            if i == j:
                i += 1
        else:
            j += k + 1
            if i == j:
                j += 1
        k = 0
    start = min(i, j)
    return doubled[start:start + n]


def offsets(a, b):
    if len(a) != len(b) or not a:
        return []
    out, start, haystack = [], 0, a + a[:-1]
    while (i := haystack.find(b, start)) >= 0:
        out.append(i)
        start = i + 1
    return out


def defects(groups):
    bad = []
    if not groups:
        bad.append('EMPTY_LINE')
    if any(re.fullmatch('[a-z]+', g['ivtff_group_raw']) is None for g in groups):
        bad.append('NONLITERAL_GROUP')
    if any(int(b['source_group_index']) != int(a['source_group_index']) + 1 for a, b in zip(groups, groups[1:])):
        bad.append('NONCONSECUTIVE_GROUP_INDICES')
    if any(a['right_separator'] != 'DEFINITE_SPACE' or b['left_separator'] != 'DEFINITE_SPACE' for a, b in zip(groups, groups[1:])):
        bad.append('UNRESOLVED_INTERIOR_BOUNDARY')
    return bad


def source_only():
    s = json.loads((D / 'ROTA_SOURCE_EVENTS.json').read_text())
    variants = []
    for branch in s['documentary_duration_branches']:
        ds = dict(s['baseline_conditional_duration_breves'])
        ds.update(branch['changes'])
        parts = {p: [] for p in ['M', 'P1', 'P2']}
        for event in s['events']:
            pitch = None if event['kind'] == 'pause' else event['pitch_reading']['conventional_pitch']
            parts[event['part']].append([pitch, ds[event['id']]])
        assert parts['P1'][5:] + parts['P1'][:5] == parts['P2']
        variants.append({'branch': branch['id'], 'parts': parts, 'A': parts['P1'][:5], 'B': parts['P1'][5:]})
    return {'source_path': (D / 'ROTA_SOURCE_EVENTS.json').relative_to(R).as_posix(), 'source_sha256': sha(D / 'ROTA_SOURCE_EVENTS.json'), 'scope': 'Necessary whole-pes relation; main numeric branches conditional, not exhaustive', 'variants': variants, 'prediction': 'For every eligible pair: >=9letters per part and projected cyclic equality are necessary, not sufficient.'}


def selftest():
    checked = 0
    for n in range(1, 10):
        for letters in itertools.product('ab', repeat=n):
            s = ''.join(letters)
            assert canonical(s) == min(s[i:] + s[:i] for i in range(n))
            checked += 1
    assert offsets('abcabc', 'abcabc') == [0, 3]
    assert offsets('abcdef', 'defabc') == [3]
    assert collections.Counter('abcabd') == collections.Counter('abacbd')
    assert canonical('abcabd') != canonical('abacbd')
    assert canonical('ab') == canonical('ba')
    assert canonical('ab ') != canonical('ba ')
    # Distinct prefix-free codes can collapse to the same projected string.
    h = dict(zip('FGgACBR', ['aaaa', ' aaa', ' a a', 'aa a', 'a aa', 'aaa ', 'a a ']))
    assert len(set(h.values())) == 7
    upper, lower = 'FGFgACBCR', 'CBCRFGFgA'
    full = [''.join(h[e] for e in part).strip(' ') for part in [upper, lower]]
    assert list(map(len, full)) == [35, 36]
    assert full[0] != full[1]
    assert full[0].replace(' ', '') == full[1].replace(' ', '') == 'a' * 27
    for h in [{'a': 'x ', 'b': 'yz '}, {'a': 'ok', 'b': 'al cho'}]:
        x, y = [h[a] + h[b] for a, b in [('a', 'b'), ('b', 'a')]]
        assert canonical(x.replace(' ', '')) == canonical(y.replace(' ', ''))
    # Necessary conjugacy alone does not satisfy repeated source events.
    assert canonical('abcdefghi') == canonical('fghiabcde')
    assert 'abcdefghi'[0] != 'abcdefghi'[2]
    g = {'ivtff_group_raw': 'okal', 'source_group_index': 1, 'left_separator': 'LINE_START', 'right_separator': 'LINE_END'}
    assert defects([g]) == []
    assert defects([]) == ['EMPTY_LINE']
    assert defects([dict(g, ivtff_group_raw='ok?al')]) == ['NONLITERAL_GROUP']
    g2 = dict(g, source_group_index=2)
    assert defects([g, g2]) == ['UNRESOLVED_INTERIOR_BOUNDARY']
    assert defects([dict(g, right_separator='DEFINITE_SPACE'), dict(g2, left_separator='DEFINITE_SPACE')]) == []
    consequence = source_only()
    return {'status': 'PASS_SOURCE_AND_SYNTHETICS', 'exhaustive_binary_cycle_cases': checked, 'source_branches': len(consequence['variants']), 'target_access': False, 'limits': 'Software checks and source notation only; no empirical null or native numeric-duration certification.'}


def intake():
    loader_spec = importlib.util.spec_from_file_location('gdt928_frozen_intake', Q / 'src/run.py')
    loader = importlib.util.module_from_spec(loader_spec)
    loader_spec.loader.exec_module(loader)
    panels, assembly = loader.load()
    allowed = set(json.loads((P / 'src/SPEC.json').read_text())['allowed_selectors'])
    assert len(allowed) == 179 and not any(p.startswith('f84') or p == 'f116v' for p in allowed)
    for ed in EDS:
        info = {}
        for phase in ['DISCOVERY', 'EVALUATION']:
            cache = json.loads((P / 'artifacts' / f'SOURCE_{phase}_{ed}.json').read_text())
            for line in cache['lines']:
                meta = line['metadata']
                assert meta['page'] in allowed and not meta['page'].startswith('f84')
                if meta['kind'] != 'P':
                    continue
                key = (meta['page'], int(meta['source_row_index']))
                assert key not in info
                groups = [dict(zip(cache['group_columns'], g)) for g in line['groups']]
                info[key] = defects(groups)
        for para in panels[ed]:
            para['defects'] = [{'locus': line['locus'], 'reasons': info[(para['page'], line['row'])]} for line in para['lines'] if info[(para['page'], line['row'])]]
            para['literal_eligible'] = not para['defects']
            words = [w for line in para['lines'] for w in line['words']]
            para['full_text'] = ' '.join(words)
            para['projection'] = ''.join(words) if para['literal_eligible'] else None
            para['canonical_cycle'] = canonical(para['projection']) if para['literal_eligible'] else None
            para['min_pes_letters'] = len(para['projection']) >= 9 if para['literal_eligible'] else None
    return panels, assembly


def decide(a, b):
    x, y = a['projection'], b['projection']
    if min(len(x), len(y)) < 9:
        return 'TOO_SHORT', []
    if len(x) != len(y):
        return 'UNEQUAL_LENGTH', []
    if collections.Counter(x) != collections.Counter(y):
        return 'UNEQUAL_INVENTORY', []
    if a['canonical_cycle'] != b['canonical_cycle']:
        return 'UNEQUAL_CYCLIC_ORDER', []
    return 'NECESSARY_CONSEQUENCE_ONLY', offsets(x, y)


def verify_lock():
    lock = json.loads((E / 'PREREG_LOCK.json').read_text())
    for name, expected in lock['files'].items():
        assert sha(R / name) == expected, name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    if args.source_only:
        write('SOURCE_CONSEQUENCES.json', source_only())
        result = selftest()
        write('PREFLIGHT.json', result)
        print(json.dumps(result))
        return
    verify_lock()
    start = time.monotonic()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    panels, assembly = intake()
    equal_pairs, summary, partners = {}, {}, {}
    for ed, paras in panels.items():
        eligible = [p for p in paras if p['literal_eligible']]
        partners[ed] = collections.defaultdict(list)
        counts = collections.Counter({k: 0 for k in DECISIONS})
        eq = []
        same_leaf_pairs = 0
        for a, b in itertools.combinations(eligible, 2):
            status, shifts = decide(a, b)
            counts[status] += 1
            same_leaf_pairs += a['leaf'] == b['leaf']
            if len(a['projection']) == len(b['projection']):
                eq.append({'a': a['id'], 'b': b['id'], 'decision': status, 'offsets': shifts})
            if status == 'NECESSARY_CONSEQUENCE_ONLY':
                assert shifts
                partners[ed][a['id']].append(b['id'])
                partners[ed][b['id']].append(a['id'])
        equal_pairs[ed] = eq
        summary[ed] = {'complete_paragraphs': len(paras), 'literal_paragraphs': len(eligible), 'literal_physical_leaves': len({p['leaf'] for p in eligible}), 'ineligible_paragraphs': len(paras) - len(eligible), 'literal_below9letters': sum(not p['min_pes_letters'] for p in eligible), 'all_literal_pairs': len(eligible) * (len(eligible) - 1) // 2, 'same_leaf_pairs': same_leaf_pairs, 'different_leaf_pairs': sum(counts.values()) - same_leaf_pairs, 'equal_projection_length_pairs': len(eq), 'pair_decisions': dict(counts), 'status': 'NO_COMPLETE_PARAGRAPH_CAPACITY' if not paras else 'NO_LITERAL_PAIR_CAPACITY' if len(eligible) < 2 else 'NECESSARY_CONSEQUENCE_CAPACITY' if counts['NECESSARY_CONSEQUENCE_ONLY'] else 'FIXED_LITERAL_WHOLE_PART_CODE_CONTRADICTED'}
    write('PARAGRAPHS.json', panels)
    write('PAIR_CONSEQUENCES.json', equal_pairs)
    result = {'status': 'COMPLETE_NECESSARY_CONSEQUENCE_CENSUS', 'started_utc': started, 'elapsed_seconds': time.monotonic() - start, 'assembly_denominators': assembly, 'panels': summary, 'translated_words': 0, 'independent_confirmation_capacity': 0, 'significance_claim': False, 'reserve_access': False, 'full_code_tested': False, 'main_melody_tested': False}
    write('RESULT.json', result)
    with (E / 'artifacts/CANDIDATE_PREDICTIONS.tsv').open('w') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['edition', 'paragraph', 'page', 'physical_leaf', 'literal_status', 'projected_length', 'source_minimum_met', 'required_cyclic_string', 'observed_partners', 'decision', 'independent_confirmation_capacity'])
        for ed, paras in panels.items():
            for p in paras:
                eligible = p['literal_eligible']
                mate = partners[ed][p['id']]
                decision = 'UNKNOWN_LITERAL_CONTENT' if not eligible else 'TOO_SHORT' if not p['min_pes_letters'] else 'NECESSARY_CONSEQUENCE_ONLY' if mate else 'NO_COMPATIBLE_WHOLE_PARTNER'
                w.writerow([ed, p['id'], p['page'], p['leaf'], 'LITERAL' if eligible else json.dumps(p['defects'], separators=(',', ':')), len(p['projection']) if eligible else '', p['min_pes_letters'] if eligible else '', p['canonical_cycle'] or '', json.dumps(mate, separators=(',', ':')), decision, 0])
    with (E / 'artifacts/LENGTH_PARTITION.tsv').open('w') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['edition', 'projected_length', 'paragraph_count', 'all_same_length_pairs', 'paragraph_ids'])
        for ed, paras in panels.items():
            groups = collections.defaultdict(list)
            for p in paras:
                if p['literal_eligible']:
                    groups[len(p['projection'])].append(p['id'])
            for length, ids in sorted(groups.items()):
                w.writerow([ed, length, len(ids), len(ids) * (len(ids) - 1) // 2, json.dumps(ids, separators=(',', ':'))])
    print(json.dumps(result))


if __name__ == '__main__':
    main()
