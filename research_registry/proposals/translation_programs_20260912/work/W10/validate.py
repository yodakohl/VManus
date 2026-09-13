"""Independent replay of both effects on the fully frozen W09 event structure."""
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
W = E.parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())


def read(name):
    with (W / name).open() as f: return list(csv.DictReader(f, delimiter='\t'))


spec = json.loads((E / 'SPEC.json').read_text())
for f in spec['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']
oldspec = json.loads((W / 'W09/SPEC.json').read_text())
old, new = collections.defaultdict(list), collections.defaultdict(list)
for r in read('W09/EVENTS.tsv'): old[r['world']].append(r)
for r in read('W10/EVENTS.tsv'): new[(r['candidate'], r['world'])].append(r)
assert set(new) == {(c, w) for c in spec['models'] for w in old}
checked = 0
structural = ('event', 'order', 'kind', 'location', 'form', 'patient', 'second', 'object', 'second_object', 'source_object', 'debts', 'alias_collision')
for (candidate, world), rows in new.items():
    assert len(rows) == len(old[world])
    state, origin = {}, {}
    for r, previous in zip(rows, old[world]):
        assert all(r[k] == previous[k] for k in structural)
        if candidate == 'D':
            assert all(r[k] == v for k, v in previous.items())
        oid, loc = r['object'], r['location']
        before = state.get(oid, {})
        assert json.loads(r['before']) == before
        if r['kind'] == 'MATERIAL':
            state.setdefault(oid, {})
            assert r['status'] == previous['status'] and not r['assertion']
        elif r['kind'] == 'ACTION':
            effect = {k: spec['models'][candidate][k] for k in ('axis', 'value')} if r['form'] == 'chol' else oldspec['effects'].get(r['form'])
            invalid = not oid or any(s in r['debts'] for s in ('EXTRACT_PATIENT_NOT_BOUND', 'MISSING_RELATION_PARTNER'))
            expected = 'ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED'
            assert r['status'] == expected
            assert (json.loads(r['assertion']) if r['assertion'] else None) == effect
            if effect and not invalid:
                key = 'PHYSICAL:' + effect['axis']
                state[oid][key] = effect['value']
                origin[(oid, key)] = loc
        else:
            assert r['assertion'] == previous['assertion']
            key, val = r['assertion'].split('=')
            initial = state.get(oid, {}).get(key)
            opposite = {initial, val} == {'dry', 'wet'} if key.endswith(':moisture') else 'cold' in {initial, val} and bool({'hot', 'warm'} & {initial, val})
            expected = 'MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if initial is None else 'MATCH' if initial == val else 'CONFLICT' if opposite else 'DIFFERENT_NOT_OPPOSED'
            assert r['status'] == expected and r['state_origin'] == origin.get((oid, key), '')
            if oid and initial is None:
                state[oid][key] = val
                origin[(oid, key)] = loc
        assert json.loads(r['after']) == state.get(oid, {})
        checked += 1

actual_diff = read('W10/DIFFERENCES.tsv')
expected_diff = set()
for world in old:
    for i, (a, b) in enumerate(zip(new[('D', world)], new[('H', world)])):
        if any(a[k] != b[k] for k in ('before', 'after', 'status', 'assertion', 'state_origin')):
            expected_diff.add((world, str(i)))
assert {(r['world'], r['event']) for r in actual_diff} == expected_diff
assert len(actual_diff) == len(expected_diff)
targets = read('W10/TARGETS.tsv')
expected_targets = {(world, r['location']) for world, rr in old.items() if world.startswith('E|') for r in rr if r['kind'] == 'ACTION' and r['form'] == 'chol'}
actual_targets = {('E|' + r['edition'] + '|' + r['grammar'] + '|' + r['paragraph'], r['operation']) for r in targets}
assert expected_targets == actual_targets and len(targets) == len(expected_targets)
arguments = read('W05/ARGUMENTS.tsv')
assert len(targets) == sum(r['form'] == 'chol' for r in arguments)
for r in targets:
    a = next(a for a in arguments if (a['edition'], a['variant'], a['operation']) == (r['edition'], r['grammar'], r['operation']))
    assert all(r[k] == a[k] for k in ('patient', 'patient_form', 'debts'))
links = read('W10/OLD_RESULT_LINKS.tsv')
oldworlds = read('W09/WORLDS.tsv')
assert {r['world'] for r in links} == {r['world'] for r in oldworlds}
for r in links:
    w = next(w for w in oldworlds if w['world'] == r['world'])
    assert r['operation'] in w['supporting_operations'].split(';')
    assert r['H_support'] == str(r['operation_form'] != 'chol')
    for c in ('D', 'H'):
        assertions = [a['status'] for a in new[(c, r['world'])] if a['location'] == r['target'] and a['kind'] == 'PROCESSED_NOMINAL']
        assert r[c + '_target'] == ';'.join(assertions)

expected_cont, expected_liquid, expected_repeat = set(), set(), set()
for world, trace in old.items():
    if not world.startswith('E|'): continue
    for n, r in enumerate(trace):
        if r['kind'] != 'ACTION' or r['form'] != 'chol': continue
        for later in trace[n + 1:]:
            if r['object'] and r['object'] in (later['object'], later['second_object']):
                expected_cont.add((world, r['location'], later['location'], later['kind'], later['assertion']))
        target = next(a for a in targets if ('E|' + a['edition'] + '|' + a['grammar'] + '|' + a['paragraph'], a['operation']) == (world, r['location']))
        if target['patient_form'] in spec['liquid_forms']:
            later = ';'.join(a['location'] for a in trace[n + 1:] if a['kind'] == 'MATERIAL' and a['object'] == r['object'] and a['form'] in spec['liquid_forms'])
            expected_liquid.add((world, r['location'], later))
    for c in spec['models']:
        actions = [a for a in new[(c, world)] if a['kind'] == 'ACTION']
        for a, b in zip(actions, actions[1:]):
            if a['patient'] and a['patient'] == b['patient'] and a['status'] == b['status'] == 'ASSUMED_EFFECT_APPLIED' and a['assertion'] == b['assertion']:
                expected_repeat.add((world, c, a['location'], b['location']))
continuations = read('W10/CONTINUATIONS.tsv')
target_para = {(r['edition'], r['grammar'], r['operation']): r['paragraph'] for r in targets}
assert {('E|' + r['edition'] + '|' + r['grammar'] + '|' + target_para[(r['edition'], r['grammar'], r['operation'])], r['operation'], r['location'], r['kind'], r['assertion']) for r in continuations} == expected_cont
liquids = read('W10/LIQUIDS.tsv')
assert {('E|' + r['edition'] + '|' + r['grammar'] + '|' + target_para[(r['edition'], r['grammar'], r['operation'])], r['operation'], r['later_liquid_mentions']) for r in liquids} == expected_liquid
repeated = read('W10/REPEATED_EFFECTS.tsv')
assert {('E|' + r['edition'] + '|' + r['grammar'] + '|' + r['paragraph'], r['candidate'], r['first'], r['second']) for r in repeated} == expected_repeat
resets = read('W10/HOT_TO_WARM_ACTIONS.tsv')
expected_resets = {(candidate, world, r['location']) for (candidate, world), rr in new.items() if world.startswith('E|') for r in rr if r['kind'] == 'ACTION' and json.loads(r['before']).get('PHYSICAL:thermal') == 'hot' and json.loads(r['after']).get('PHYSICAL:thermal') == 'warm'}
assert {(r['candidate'], r['world'], r['location']) for r in resets} == expected_resets
assert len(resets) == len(expected_resets)
alignment = read('W10/ALIGNMENT.tsv')
original = read('W09/ALIGNMENT.tsv')
assert len(alignment) == len(original) == 900
for a, b in zip(alignment, original):
    assert all(a[k] == b[k] for k in ('paragraph', 'locus', 'index', 'raw', 'status'))
    assert a['D'] == b['N'] and a['H'] == ('erhitze' if b['raw'] == 'chol' else b['N'])
assert sum(a['D'] != a['H'] for a in alignment) == 24
result = json.loads((E / 'RESULT.json').read_text())
assert result['event_rows'] == checked and result['target_rows'] == len(targets)
validation = dict(status='PASS', checked_events=checked, fixed_worlds=len(old), exact_target_rows=len(targets),
                  primary_groups=900, changed_primary_positions=24, old_result_links=len(links),
                  source_and_D_parity=True, full_independent_effect_replay=True,
                  independent_observer=False, meaning_validation=False, held_access=False,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(E / 'VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(validation, indent=2))
