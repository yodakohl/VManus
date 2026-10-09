#!/usr/bin/env python3
"""Necessary-condition check for four declared deterministic ligature pairs.

Uses the existing guarded word-profile cache; no language or image decoder.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import word_profiles as wp

BASE = Path(__file__).resolve().parent
PAIRS = (
    ('bench_before_high_k', 'ckhy', 'chky', 'ckh', 'chk'),
    ('bench_before_high_t', 'cthy', 'chty', 'cth', 'cht'),
    ('high_before_bench_k', 'ckhey', 'kchey', 'ckh', 'kch'),
    ('high_before_bench_t', 'cthor', 'tchor', 'cth', 'tch'),
)
CONDITIONS = {
    'word_only': (),
    'word_and_known_hand': ('hand',),
    'word_and_page': ('page',),
    'word_page_position': ('page', 'position'),
}
SAFE_LEFT = {'DEFINITE_SPACE', 'LINE_START'}
SAFE_RIGHT = {'DEFINITE_SPACE', 'LINE_END'}


def main():
    conn = wp.ensure_cache(ROOT)
    forms = sorted({form for p in PAIRS for form in p[1:3]})
    profiles = [wp.profile(conn, form, limit=2) for form in forms]
    occurrences = {form: wp.occurrences(conn, form) for form in forms}
    inputs = {'source_receipt': wp.receipt(conn), 'profiles': profiles,
              'occurrences': occurrences}
    input_path = BASE / 'HAND_WRITER_TRIGGER_INPUTS_20261004.json'
    input_path.write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + '\n')
    results = []
    for name, fused, plain, old, new in PAIRS:
        assert fused.replace(old, new) == plain
        for edition in wp.EDITIONS:
            selected = [dict(r, spelling='fused' if form == fused else 'plain')
                        for form in (fused, plain) for r in occurrences[form]
                        if r['edition'] == edition]
            eligible = [r for r in selected if r['left_separator'] in SAFE_LEFT
                        and r['right_separator'] in SAFE_RIGHT]
            checks = {}
            for label, fields in CONDITIONS.items():
                buckets = defaultdict(lambda: {'fused': [], 'plain': []})
                for row in eligible:
                    if 'hand' in fields and row['hand'] not in {'1', '2', '3', '4', '5'}:
                        continue
                    key = tuple(row[f] for f in fields)
                    buckets[key][row['spelling']].append(row['source_group_id'])
                conflicts = [dict(condition=dict(zip(fields, key)), **values)
                             for key, values in sorted(buckets.items())
                             if values['fused'] and values['plain']]
                checks[label] = {'conflicting_conditions': len(conflicts),
                                 'witnesses': conflicts}
            item = {'pair': name, 'fused': fused, 'plain': plain,
                    'assumed_expanded_input': plain, 'edition': edition,
                    'all_exact_counts': {form: sum(r['ivtff_group_raw'] == form for r in selected)
                                         for form in (fused, plain)},
                    'safe_boundary_counts': {form: sum(r['ivtff_group_raw'] == form for r in eligible)
                                            for form in (fused, plain)},
                    'conditions': checks}
            results.append(item)
            print(edition, name, item['safe_boundary_counts'],
                  {k: v['conflicting_conditions'] for k, v in checks.items()})
    out = {'status': 'EXPOSED_CONDITIONAL_WRITER_CHECK_NO_MEANING',
           'source': input_path.name,
           'source_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
           'pairs': PAIRS, 'conditions': CONDITIONS,
           'claim_ceiling': 'A conflict rejects only deterministic rendering from the declared '
                           'expanded input and condition. Expansion equivalence is assumed, '
                           'not proved; no native-image authentication, significance or meaning.',
           'results': results}
    (BASE / 'HAND_WRITER_TRIGGER_RESULT_20261004.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    # Give one bounded concrete locus pair per orientation, keeping reader fixed.
    for name in (PAIRS[0][0], PAIRS[3][0]):
        row = next(r for r in results if r['pair'] == name and r['edition'] == 'ZL3b')
        print('ZL witness', name,
              row['conditions']['word_page_position']['witnesses'][:1])


if __name__ == '__main__':
    main()
