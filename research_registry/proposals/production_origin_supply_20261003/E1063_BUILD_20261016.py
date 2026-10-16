"""Project two nominated iteration families; no native state or truth evaluation."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = next(p for p in BASE.parents if (p / 'vmanus-work').exists())
PLAN = BASE / 'E1063_CONSTRUCTION_PLAN_20261016.json'
LOCK = BASE / 'E1063_CODE_LOCK_20261016.json'
OUTPUT = BASE / 'E1063_SCAFFOLD_20261016.json'
VALIDATOR = BASE / 'E1063_VALIDATE_20261016.py'
PATTERNS = [('D', 'F', re.compile(r'^qok(e*)dy$')),
            ('Y', 'G', re.compile(r'^qok(e*)y$'))]
LIMITS = [
    'Partial construction, not a complete reading, empirical test or translation.',
    'F/G are fixed unknown partial endofunctions; no actual execution or truth evaluated.',
    'Each block has its own unbound input; boundaries are not established semantic resets.',
    'UNKNOWN groups may affect arguments, state and scope; none is a no-op.',
    'ZERO and ONE are global alternatives; no choice by occurrence or family.',
    'Endpoint normalization preserves ordered terms; no F/G commutation or inequality assumed.',
    'All readers describe one exposed physical folio; no holdout or independent replication.',
    'No R771 operator meanings, global e/dy/q morphology, event counts or time values imported.'
]


def relative(path):
    return str(path.relative_to(ROOT))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def classify(raw, profiled):
    for family, root, pattern in PATTERNS:
        match = pattern.fullmatch(raw)
        if match:
            assert raw in profiled, ('UNPROFILED_MATCH', raw)
            return family, root, len(match.group(1))
    return None


def joined(left, right):
    return (int(right['source_group_index']) == int(left['source_group_index']) + 1
            and left['right_separator'] == right['left_separator'] == 'DEFINITE_SPACE')


def formulas(terms):
    result = {}
    for name, delta in [('ZERO', 0), ('ONE', 1)]:
        factors = [dict(root=t['root'], exponent=t['e_count'] + delta,
                        source_group_id=t['source_group_id']) for t in terms]
        normal = []
        for factor in factors:
            if factor['exponent'] == 0:
                continue
            if normal and normal[-1]['root'] == factor['root']:
                normal[-1]['exponent'] += factor['exponent']
                normal[-1]['source_ids'].append(factor['source_group_id'])
            else:
                normal.append(dict(root=factor['root'], exponent=factor['exponent'],
                                   source_ids=[factor['source_group_id']]))
        result[name] = dict(ordered_factors=factors, normal_form=normal)
    return result


def boundary(rows, matches, start, end, left):
    if (left and start == 0) or (not left and end == len(rows)):
        return dict(reason='line_start' if left else 'line_end', source_id=None)
    j = start - 1 if left else end
    a, b = (rows[j], rows[start]) if left else (rows[end - 1], rows[j])
    reason = ('unknown' if matches[j] is None else 'nonconsecutive'
              if int(b['source_group_index']) != int(a['source_group_index']) + 1
              else 'uncertain_seam')
    assert reason == 'unknown' or not joined(a, b)
    return dict(reason=reason, source_id=rows[j]['source_group_id'])


def main():
    lock, plan = read(LOCK), read(PLAN)
    locked = {x['path']: x['sha256'] for x in lock['files']}
    assert len(locked) == len(lock['files']) and lock['locked_utc']
    required = {relative(PLAN), relative(Path(__file__).resolve()), relative(VALIDATOR)}
    required.update(x['path'] for x in plan['inputs'])
    assert required <= locked.keys(), ('MISSING_LOCK_INPUTS', sorted(required - locked.keys()))
    for path, expected in locked.items():
        assert digest(ROOT / path) == expected, ('LOCK_HASH', path)
    for item in plan['inputs']:
        assert locked[item['path']] == item['sha256'], ('PLAN_HASH', item['path'])
    profile_paths = [x['path'] for x in plan['inputs'] if '_PROFILES_' in x['path']]
    profiled = {p['form'] for path in profile_paths for p in read(ROOT / path)['profiles']}
    assert profiled == {'qok' + 'e' * n + tail for n in range(5) for tail in ('dy', 'y')}
    output = dict(schema_version=1, status='PARTIAL_SHARED_POWER_CONSTRUCTION_NO_MEANING_SELECTION',
                  idea='IDEA001063', pins=[dict(path=k, sha256=v) for k, v in sorted(locked.items())],
                  code_lock=dict(path=relative(LOCK), sha256=digest(LOCK), locked_utc=lock['locked_utc']),
                  profiled_forms=sorted(profiled), source_units=[], annotations=[], blocks=[],
                  unknown_spans=[], accounting=dict(units=[], total={}), limits=LIMITS)
    seen_units, seen_groups = set(), set()
    for path in plan['source_scope']['documents']:
        assert path in locked
        units = read(ROOT / path)['units']
        assert sorted(u['edition'] for u in units) == ['IT2a', 'RF1b', 'ZL3b']
        for unit in units:
            reader = unit['edition']
            pages = {line['metadata']['page'] for line in unit['lines']}
            assert len(pages) == 1 and pages <= {'f75r', 'f75v'}
            uid = next(iter(pages)) + '_' + reader
            assert uid not in seen_units
            seen_units.add(uid)
            output['source_units'].append(dict(unit_id=uid, source_path=path, source_unit=unit))
            count = Counter(source_groups=0, candidates=0, unknown_groups=0, blocks=0, unknown_spans=0)
            for line in unit['lines']:
                locus = line['metadata']['locus']
                assert line['metadata']['edition'] == reader
                rows = [dict(zip(unit['group_columns'], row)) for row in line['groups']]
                assert all(len(row) == len(unit['group_columns']) for row in line['groups'])
                matches = [classify(row['ivtff_group_raw'], profiled) for row in rows]
                for row, match in zip(rows, matches):
                    sid, raw = row['source_group_id'], row['ivtff_group_raw']
                    assert sid not in seen_groups and sid.startswith(reader + '|' + locus + '|G')
                    seen_groups.add(sid)
                    family, root, n = match if match else (None, None, None)
                    output['annotations'].append(dict(unit_id=uid, source_group_id=sid, locus=locus,
                        raw=raw, status='CANDIDATE' if match else 'UNKNOWN', family=family, root=root,
                        e_count=n, exponents=dict(ZERO=n, ONE=n + 1) if match else None))
                    count['source_groups'] += 1
                    count['candidates' if match else 'unknown_groups'] += 1
                i = 0
                while i < len(rows):
                    end = i + 1
                    if matches[i] is None:
                        while end < len(rows) and matches[end] is None:
                            end += 1
                        output['unknown_spans'].append(dict(unit_id=uid, locus=locus,
                            source_ids=[r['source_group_id'] for r in rows[i:end]],
                            raw=[r['ivtff_group_raw'] for r in rows[i:end]]))
                        count['unknown_spans'] += 1
                    else:
                        while end < len(rows) and matches[end] is not None and joined(rows[end - 1], rows[end]):
                            end += 1
                        terms = [dict(source_group_id=rows[j]['source_group_id'], raw=rows[j]['ivtff_group_raw'],
                            family=matches[j][0], root=matches[j][1], e_count=matches[j][2]) for j in range(i, end)]
                        bid = 'B' + str(len(output['blocks']) + 1).zfill(4)
                        output['blocks'].append(dict(block_id=bid, unit_id=uid, locus=locus,
                            source_ids=[t['source_group_id'] for t in terms], terms=terms,
                            formulas=formulas(terms), input='s_' + bid,
                            left_boundary=boundary(rows, matches, i, end, True),
                            right_boundary=boundary(rows, matches, i, end, False)))
                        count['blocks'] += 1
                    i = end
            output['accounting']['units'].append(dict(unit_id=uid, **count))
    assert len(seen_units) == 6
    totals = {k: sum(row[k] for row in output['accounting']['units'])
              for k in ('source_groups', 'candidates', 'unknown_groups', 'blocks', 'unknown_spans')}
    output['accounting']['total'] = dict(source_units=len(seen_units), **totals)
    assert totals['source_groups'] == totals['candidates'] + totals['unknown_groups']
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status=output['status'], accounting=output['accounting']), ensure_ascii=False))


if __name__ == '__main__':
    main()
