"""Complete frozen shared-refrain capacity census; no lexical decoder."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import csv
import hashlib
import json
import re

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
BOUND = {'DEFINITE_SPACE', 'LINE_START', 'LINE_END'}


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def suffix(groups, n):
    if len(groups) < n:
        return {'status': 'INSUFFICIENT_FIXED_GROUP_CAPACITY', 'words': [g['ivtff_group_raw'] for g in groups], 'source_ids': [g['source_group_id'] for g in groups], 'reasons': ['TOO_FEW_GROUPS']}
    chosen = groups[-n:]
    reasons = []
    if any(not re.fullmatch('[a-z]+', g['ivtff_group_raw']) for g in chosen):
        reasons.append('NONLITERAL_GROUP')
    if any(g['left_separator'] not in BOUND or g['right_separator'] not in BOUND for g in chosen):
        reasons.append('UNCERTAIN_BOUNDARY')
    for a, b in zip(chosen, chosen[1:]):
        expected = ('DEFINITE_SPACE', 'DEFINITE_SPACE') if a['locus'] == b['locus'] else ('LINE_END', 'LINE_START')
        if (a['right_separator'], b['left_separator']) != expected:
            reasons.append('INCOMPATIBLE_ADJACENCY')
    return {'status': 'UNKNOWN' if reasons else 'KNOWN', 'words': [g['ivtff_group_raw'] for g in chosen], 'source_ids': [g['source_group_id'] for g in chosen], 'reasons': sorted(set(reasons))}


def classify(suffixes, n):
    known = [(i, s) for i, s in enumerate(suffixes) if s['status'] == 'KNOWN']
    conflicts = [[a + 1, b + 1] for (a, x), (b, y) in combinations(known, 2) if x['words'] != y['words']]
    noninjective = [i + 1 for i, s in known if n == 5 and len(set(s['words'])) != 5]
    if any(s['status'] == 'INSUFFICIENT_FIXED_GROUP_CAPACITY' for s in suffixes):
        status = 'INSUFFICIENT_FIXED_GROUP_CAPACITY'
    elif conflicts or noninjective:
        status = 'CONTRADICTED'
    elif any(s['status'] == 'UNKNOWN' for s in suffixes):
        status = 'UNRESOLVED_ONLY'
    else:
        status = 'OBSERVED_RECURRENT_CLOSURE'
    return status, conflicts, noninjective


def build():
    lock = read(E / 'PREREG_LOCK.json')
    for rel, sha in lock['files'].items():
        assert digest(R / rel) == sha, rel
    spec = read(E / 'src/SPEC.json')
    allowed = set(read(R / spec['allow_source'])['allowed_selectors'])
    assert len(allowed) == 179 and not any(s.startswith('f84') or s == 'f116v' for s in allowed)
    lines = {}
    for rel in spec['sources']:
        source = read(R / rel)
        for line in source['lines']:
            md = line['metadata']
            assert md['page'] in allowed
            key = md['edition'], md['locus']
            assert key not in lines
            lines[key] = [dict(md, **dict(zip(source['group_columns'], g))) for g in line['groups']]
    paragraphs = read(R / spec['paragraph_source'])
    all_cases, suffix_rows, remaining, denom = [], [], {}, {}
    for edition in spec['editions']:
        by_page = defaultdict(list)
        suffixes = {}
        for p in paragraphs.get(edition, []):
            assert p['page'] in allowed and p['lines']
            groups = []
            for line in p['lines']:
                gs = lines[edition, line['locus']]
                assert [g['ivtff_group_raw'] for g in gs] == line['words']
                assert [g['source_group_id'] for g in gs] == line['source_ids']
                groups.extend(gs)
            assert len(groups) == p['groups']
            by_page[p['page']].append(p)
            for model, width in spec['models'].items():
                s = suffix(groups, width)
                suffixes[p['id'], model] = s
                suffix_rows.append({'edition': edition, 'page': p['page'], 'paragraph': p['id'], 'model': model, **s})
        windows, rejected_gap = 0, 0
        outcomes = {m: Counter() for m in spec['models']}
        for page, ps in sorted(by_page.items()):
            ps.sort(key=lambda p: p['lines'][0]['row'])
            for start in range(len(ps) - 6):
                chosen = ps[start:start + 7]
                adjacent = all(int(b['lines'][0]['locus'].rsplit('.', 1)[1]) == int(a['lines'][-1]['locus'].rsplit('.', 1)[1]) + 1 for a, b in zip(chosen, chosen[1:]))
                if not adjacent:
                    rejected_gap += 1
                    continue
                windows += 1
                for model, width in spec['models'].items():
                    ss = [suffixes[p['id'], model] for p in chosen]
                    status, conflicts, noninjective = classify(ss, width)
                    outcomes[model][status] += 1
                    case = {'edition': edition, 'page': page, 'physical_leaf': chosen[0]['leaf'],
                            'window_start': chosen[0]['id'], 'model': model, 'status': status,
                            'paragraph_ids': [p['id'] for p in chosen], 'suffixes': ss,
                            'contradictory_paragraph_pairs_1based': conflicts,
                            'R5_noninjective_paragraphs_1based': noninjective,
                            'independent_confirmation_leaves': 0}
                    all_cases.append(case)
                    if status in {'UNRESOLVED_ONLY', 'OBSERVED_RECURRENT_CLOSURE'}:
                        for p in chosen:
                            remaining[edition + '|' + p['id']] = {'edition': edition, **p}
        denom[edition] = {'complete_paragraphs': len(paragraphs.get(edition, [])), 'source_pages': len(by_page),
                          'seven_paragraph_windows': windows, 'rejected_gapped_windows': rejected_gap,
                          'paragraph_capacity': 'AVAILABLE' if by_page else 'NO_PARAGRAPH_CAPACITY',
                          'models': {m: dict(c) for m, c in outcomes.items()}}
    result = {'status': 'COMPLETE_FIXED_REFRAIN_SCREEN', 'source_prayers': 7,
              'source_refrain_translation_hypothesis': 'Come quickly with your spirits.',
              'editions': denom, 'case_rows': len(all_cases), 'suffix_rows': len(suffix_rows),
              'remaining_context_paragraphs': len(remaining), 'confirmed_words': 0,
              'claim_ceiling': 'Necessary shared-closure condition only; preceding names and source identity not established; no significance or independent leaf confirmation.'}
    return result, all_cases, suffix_rows, remaining


def main():
    result, cases, suffixes, remaining = build()
    for name, value in [('RESULT.json', result), ('ALL_CANDIDATES.json', cases), ('ALL_PARAGRAPH_SUFFIXES.json', suffixes), ('REMAINING_CONTEXTS.json', remaining)]:
        (E / 'artifacts' / name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')
    with (E / 'artifacts/CANDIDATE_TABLE.tsv').open('w', newline='') as f:
        fields = ['edition', 'page', 'physical_leaf', 'window_start', 'model', 'status', 'paragraph_ids', 'observed_suffixes', 'unknown_suffixes', 'pair_conflicts', 'R5_noninjective', 'independent_confirmation_leaves']
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t'); writer.writeheader()
        for c in cases:
            writer.writerow({**{k: c[k] for k in fields if k in c and k != 'paragraph_ids'},
                             'paragraph_ids': ';'.join(c['paragraph_ids']),
                             'observed_suffixes': ';'.join(' '.join(s['words']) for s in c['suffixes']),
                             'unknown_suffixes': sum(s['status'] == 'UNKNOWN' for s in c['suffixes']),
                             'pair_conflicts': json.dumps(c['contradictory_paragraph_pairs_1based'], separators=(',', ':')),
                             'R5_noninjective': ','.join(map(str, c['R5_noninjective_paragraphs_1based']))})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
