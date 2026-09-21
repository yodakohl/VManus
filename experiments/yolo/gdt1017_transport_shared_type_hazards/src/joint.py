"""Direct bidirectional positive-edge union over separate complete worlds."""
from common import *
import copy


def canonical_original(case):
    originals = {r['id']: r for r in read(A/'ORIGINAL_CANDIDATES.json')}
    member = case['members'][0]
    row = originals[member['original_id']]
    rename = member['original_to_canonical'][0]
    return [dict(cl, symbols=[rename.get(v, v) for v in cl['symbols']]) for cl in row['parse']]


def apply_union(local, union, s, independent=False):
    result = copy.deepcopy(local)
    if 'paths' not in result:
        return result
    present = set(result['cargo'])
    active = [edge for edge in union if set(edge) <= present]
    result['asserted_hazards'] = result['hazards']
    result['hazards'] = active
    for path in result['paths']:
        if not independent:
            bad = load(s['model'], 'safety993').unsafe_states(path['trace'], active)
        else:
            names = ['M'] + sorted(present)
            index = {name: i for i, name in enumerate(names)}
            bad = []
            for step in path['trace']:
                mask = sum(1 << index[name] for name in names if step['positions'][name] == 'R')
                agent_right = bool(mask & (1 << index['M']))
                for a, b in active:
                    left = bool(mask & (1 << index[a]))
                    right = bool(mask & (1 << index[b]))
                    if left == right and left != agent_right:
                        bad.append(dict(after=step['clause'], pair=[a, b], bank='R' if left else 'L'))
        path['safety_violations'] = bad
        path['consistent'] = path['without_safety_consistent'] and not bad
    result['status'] = 'COHERENT' if any(p['consistent'] for p in result['paths']) else 'CONTRADICTED'
    return result


def replay_joint(original_parse, added_parse, variant, s, independent=False):
    original = replay(original_parse, variant, s, independent)
    added = replay(added_parse, variant, s, independent)
    if 'paths' not in original or 'paths' not in added:
        return dict(status='BINDING_CONTRADICTION', original=original, added=added)
    union = [list(p) for p in sorted({tuple(sorted(edge)) for r in (original, added) for edge in r['hazards']})]
    first = apply_union(original, union, s, independent)
    second = apply_union(added, union, s, independent)
    result = dict(second, original=first, union_hazards=union,
                  local_original_status=original['status'], local_added_status=added['status'])
    result['status'] = 'COHERENT' if first['status'] == second['status'] == 'COHERENT' else 'CONTRADICTED'
    return result
