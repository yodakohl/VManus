"""Separate source census and closed-form identity / full state-trace check."""
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
W = E.parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


spec = json.loads((E / 'SPEC.json').read_text())
for item in spec['inputs']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
D = {r['form']: r for r in rows(W / 'W02/LEXICON.tsv')}
for word, override in json.loads((W / 'W05/SPEC.json').read_text())['word_overrides'].items():
    D[word].update(override)
features = collections.defaultdict(list)
for r in json.loads((W / 'W03/SPEC.json').read_text())['features']:
    if r['kind'] != 'STANDALONE':
        features[r['form']].append(r)
processed = {r['form'] for ff in features.values() for r in ff if r['kind'] == 'PROCESSED_NOMINAL'}
source = json.loads((W / 'W02/SOURCE.json').read_text())
alternates = json.loads((W / 'W02/ALTERNATE_LINES.json').read_text())['readings']
arguments = rows(W / 'W05/ARGUMENTS.tsv')
quality = rows(W / 'W05/QUALITY_ASSERTIONS.tsv')
saved_targets = rows(E / 'TARGETS.tsv')
saved_pairs = rows(E / 'ALL_PARENT_PAIRS.tsv')
worlds = rows(E / 'WORLDS.tsv')
events = collections.defaultdict(list)
for row in rows(E / 'EVENTS.tsv'):
    events[row['world']].append(row)
flat_packets, schedules, identities, target_lookup = {}, {}, {}, {}
expected_targets, expected_pair_keys, expected_worlds = set(), set(), set()

for edition, lines in alternates.items():
    payload = {r['metadata']['locus']: r['groups'] for r in lines}
    for host in source['targets']:
        p = host['hosts']['ZL3b'][0]
        flat = [(line['locus'] + ':' + str(i), g['ivtff_group_raw'])
                for line in p['lines'] for i, g in enumerate(payload[line['locus']], 1)]
        position = {ident: n for n, (ident, word) in enumerate(flat)}
        form = dict(flat)
        first = {}
        for ident, word in flat:
            first.setdefault(word, ident)
        mats = {ident for ident, word in flat if D.get(word, {}).get('role') in {'MATERIAL', 'MATERIAL_DOSE'}}
        for grammar in spec['grammars']:
            key = (edition, grammar, p['id'])
            flat_packets[key] = flat
            identities[key] = {ident: first[word] for ident, word in flat if ident in mats}
            aa = [a for a in arguments if (a['edition'], a['variant'], a['paragraph']) == key]
            qq = [q for q in quality if q['variant'] == grammar and q['paragraph'] == p['id'] and q['kind'] == 'STANDALONE'] if edition == 'ZL3b' else []
            schedule = []
            for ident, word in flat:
                if ident not in mats:
                    continue
                schedule.append((position[ident], 0, position[ident], 0, 'MATERIAL', ident, None))
                for sub, feature in enumerate(features[word], 1):
                    schedule.append((position[ident], 0, position[ident], sub, feature['kind'], ident, feature))
            for a in aa:
                refs = [a['operation']] + [a[k] for k in ('patient', 'coingredient') if a[k]]
                schedule.append((max(position[x] for x in refs), 1, position[a['operation']], 0, 'ACTION', a['operation'], a))
            for q in qq:
                refs = [q['mention']] + ([q['patient']] if q['patient'] else [])
                schedule.append((max(position[x] for x in refs), 2, position[q['mention']], 0, 'QUALITY', q['mention'], q))
            schedules[key] = sorted(schedule, key=lambda x: x[:4])
            for ident, word in flat:
                if word not in processed:
                    continue
                tkey = (edition, grammar, ident)
                target_lookup[tkey] = (key, position[ident], word)
                expected_targets.add(tkey)
                actual = next(r for r in saved_targets if (r['edition'], r['grammar'], r['target']) == tkey)
                assert actual['first_form_mention'] == str(first[word] == ident)
                donor_names = set()
                matching_count = 0
                if first[word] == ident:
                    for a in aa:
                        if position[a['operation']] >= position[ident]:
                            continue
                        pid = '|'.join(tkey)
                        expected_pair_keys.add((pid, a['operation']))
                        pair = next(r for r in saved_pairs if (r['target_id'], r['operation']) == (pid, a['operation']))
                        done = max(position[x] for x in [a['operation'], a['patient'], a['coingredient']] if x)
                        valid = bool(a['patient']) and not any(x in a['debts'] for x in ('MISSING_PATIENT', 'EXTRACT_PATIENT_NOT_BOUND', 'MISSING_RELATION_PARTNER'))
                        effect = spec['effects'].get(a['form'])
                        matches = effect is not None and any(f['kind'] == 'PROCESSED_NOMINAL' and effect == {'axis': f['axis'], 'value': f['value']} for f in features[word])
                        status = 'INCOMPLETE_ARGUMENT' if not valid else 'COMPLETES_AT_OR_AFTER_TARGET' if done >= position[ident] else 'SAME_WRITTEN_NAME' if a['patient_form'] == word else 'NO_REGISTERED_EFFECT_MATCH' if not matches else 'CANDIDATE'
                        assert pair['status'] == status
                        assert pair['patient'] == a['patient'] and pair['patient_form'] == a['patient_form']
                        assert pair['argument_debts'] == a['debts'] and int(pair['completion']) == done
                        if status == 'CANDIDATE':
                            donor_names.add(a['patient_form'])
                            matching_count += 1
                            expected_worlds.add((edition, grammar, p['id'], ident, a['patient_form']))
                assert int(actual['matching_operations']) == matching_count
                assert int(actual['distinct_parent_names']) == len(donor_names)

assert {(r['edition'], r['grammar'], r['target']) for r in saved_targets} == expected_targets
assert len(saved_targets) == len(expected_targets)
assert {(r['target_id'], r['operation']) for r in saved_pairs} == expected_pair_keys
assert len(saved_pairs) == len(expected_pair_keys)
assert {(r['edition'], r['grammar'], r['paragraph'], r['target'], r['parent_form']) for r in worlds} == expected_worlds
assert len(worlds) == len(expected_worlds)

checks = 0
world_keys = {}
for key in schedules:
    world_keys['E|' + '|'.join(key)] = (key, None)
for w in worlds:
    world_keys[w['world']] = ((w['edition'], w['grammar'], w['paragraph']), w)
assert set(events) == set(world_keys)
for wid, (key, trial) in world_keys.items():
    flat = flat_packets[key]
    form = dict(flat)
    identity = dict(identities[key])
    if trial:
        old_root = identity[trial['target']]
        source_root = next(identity[ident] for ident, word in flat if word == trial['parent_form'])
        identity = {ident: source_root if root == old_root else root for ident, root in identity.items()}
    state, origins, introduced = {}, {}, set()
    actual_rows = events[wid]
    assert len(actual_rows) == len(schedules[key])
    for n, (r, event) in enumerate(zip(actual_rows, schedules[key])):
        tick, _, _, _, kind, location, data = event
        assert int(r['event']) == n and int(r['order']) == tick
        assert (r['kind'], r['location'], r['form']) == (kind, location, form[location])
        if kind == 'MATERIAL':
            root = identity[location]
            status = 'RENAMED_EXISTING_PORTION' if trial and location == trial['target'] else 'EXTERNAL_PORTION' if form[location] not in introduced else 'SAME_FORM_REMENTION'
            introduced.add(form[location])
            state.setdefault(root, {})
            assert r['object'] == root and r['status'] == status
            assert json.loads(r['before']) == state[root] == json.loads(r['after'])
        elif kind == 'ACTION':
            root, second = identity.get(data['patient'], ''), identity.get(data['coingredient'], '')
            assert (r['patient'], r['second'], r['object'], r['second_object']) == (data['patient'], data['coingredient'], root, second)
            assert r['debts'] == data['debts']
            assert json.loads(r['before']) == state.get(root, {})
            invalid = not root or 'EXTRACT_PATIENT_NOT_BOUND' in data['debts'] or 'MISSING_RELATION_PARTNER' in data['debts']
            effect = spec['effects'].get(data['form'])
            status = 'ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED'
            if effect and not invalid:
                fkey = 'PHYSICAL:' + effect['axis']
                state[root][fkey] = effect['value']
                origins[(root, fkey)] = location
            assert json.loads(r['after']) == state.get(root, {}) and r['status'] == status
            assert r['alias_collision'] == str(bool(root and second and root == second))
        else:
            root = identity.get(data['patient'], '') if kind == 'QUALITY' else identity[location]
            scope = data['scope'] if kind == 'QUALITY' else 'PHYSICAL' if kind == 'PROCESSED_NOMINAL' else 'CONSTITUTION'
            fkey, value = scope + ':' + data['axis'], data['value']
            previous = state.get(root, {}).get(fkey)
            opposed = ({previous, value} == {'dry', 'wet'} if data['axis'] == 'moisture' else 'cold' in {previous, value} and bool({'warm', 'hot'} & {previous, value}))
            status = 'MISSING_PATIENT' if not root else 'INITIAL_CONSTRAINT' if previous is None else 'MATCH' if previous == value else 'CONFLICT' if opposed else 'DIFFERENT_NOT_OPPOSED'
            assert r['object'] == root and r['assertion'] == fkey + '=' + value and r['status'] == status
            assert json.loads(r['before']) == state.get(root, {})
            assert r['state_origin'] == origins.get((root, fkey), '')
            if root and previous is None:
                state[root][fkey] = value
                origins[(root, fkey)] = location
            assert json.loads(r['after']) == state.get(root, {})
        checks += 1
    if trial:
        assert int(trial['R_portions']) == len(set(identity.values()))
        assert int(trial['E_portions']) == len(set(identities[key].values()))
        assert int(trial['E_portions']) - int(trial['R_portions']) == 1

saved_futures = rows(E / 'FUTURE_COMPARISON.tsv')
expected_future_keys = set()
for w in worlds:
    key = (w['edition'], w['grammar'], w['paragraph'])
    pos = dict((ident, n) for n, (ident, word) in enumerate(flat_packets[key]))
    base = events['E|' + '|'.join(key)]
    trial = events[w['world']]
    matching_ops = [p['operation'] for p in saved_pairs if p['target_id'] == w['edition'] + '|' + w['grammar'] + '|' + w['target'] and p['status'] == 'CANDIDATE' and p['patient_form'] == w['parent_form']]
    assert w['supporting_operations'] == ';'.join(matching_ops)
    extra_conflicts, removed_conflicts, physical_changes, new_actions = [], [], [], []
    for i, (a, b) in enumerate(zip(base, trial)):
        if b['status'] == 'CONFLICT' and a['status'] != 'CONFLICT': extra_conflicts.append(b['location'] + '=' + b['assertion'])
        if a['status'] == 'CONFLICT' and b['status'] != 'CONFLICT': removed_conflicts.append(b['location'] + '=' + b['assertion'])
        if int(b['order']) < pos[w['target']] or w['parent_portion'] not in (b['object'], b['second_object']): continue
        expected_future_keys.add((w['world'], str(i)))
        out = next(r for r in saved_futures if (r['world'], r['event']) == (w['world'], str(i)))
        for prefix, original in [('E', a), ('R', b)]:
            for column in ('object', 'before', 'after', 'status'):
                assert out[prefix + '_' + column] == original[column]
        physical = any({k: v for k, v in json.loads(a[part]).items() if k.startswith('PHYSICAL:')} != {k: v for k, v in json.loads(b[part]).items() if k.startswith('PHYSICAL:')} for part in ('before', 'after'))
        assert out['physical_values_differ'] == str(physical)
        if physical and b['location'] != w['target']: physical_changes.append(b['location'] + ':' + b['kind'])
        if b['kind'] == 'ACTION' and a['object'] == identities[key][w['target']]: new_actions.append(b['location'])
    assert w['new_conflicts'] == ';'.join(extra_conflicts) and w['removed_conflicts'] == ';'.join(removed_conflicts)
    assert w['physical_future_differences'] == ';'.join(physical_changes)
    assert w['all_actions_on_new_name_after_binding'] == ';'.join(new_actions)
assert {(r['world'], r['event']) for r in saved_futures} == expected_future_keys
assert len(saved_futures) == len(expected_future_keys)
prediction_groups = collections.defaultdict(list)
for w in worlds:
    normalized = []
    for row in events[w['world']]:
        data = {k: row[k] for k in ('order', 'kind', 'location', 'form', 'patient', 'second', 'object', 'second_object', 'before', 'after', 'assertion', 'status', 'debts', 'alias_collision')}
        data['order'] = int(data['order'])
        data['alias_collision'] = data['alias_collision'] == 'True'
        normalized.append(data)
    signature = hashlib.sha256(json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert w['prediction_group'] == signature
    prediction_groups[signature].append(w['world'])
saved_groups = rows(E / 'PREDICTION_GROUPS.tsv')
assert {r['signature']: r['worlds'].split(';') for r in saved_groups} == dict(prediction_groups)
assert all(int(r['count']) == len(r['worlds'].split(';')) for r in saved_groups)
quantity_rows = rows(E / 'QUANTITIES.tsv')
expected_quantity_positions = {(edition, paragraph, ident) for (edition, grammar, paragraph), flat in flat_packets.items() if grammar == 'B' for ident, word in flat if D.get(word, {}).get('role') in {'MATERIAL_DOSE', 'AMOUNT', 'NUMBER', 'DISTRIBUTIVE', 'QUALITY_VALUE'}}
assert {(r['edition'], r['paragraph'], r['location']) for r in quantity_rows} == expected_quantity_positions
assert len(quantity_rows) == len(expected_quantity_positions)
display = {r['raw']: r['N'] for r in rows(W / 'W08/ALIGNMENT.tsv')}
assert all(r['hypothesis'] == display.get(r['form'], D[r['form']]['hypothesis']) for r in quantity_rows)
assert (E / 'ALIGNMENT.tsv').read_bytes() == (W / 'W08/ALIGNMENT.tsv').read_bytes()
assert len(rows(E / 'ALIGNMENT.tsv')) == 900
result = json.loads((E / 'RESULT.json').read_text())
assert result['world_rows'] == len(worlds) and result['event_rows'] == checks
assert result['parent_pair_rows'] == len(saved_pairs) and result['target_rows'] == len(saved_targets)
assert result['prediction_groups'] == len(prediction_groups)
validation = dict(status='PASS', checked_events=checks, target_rows=len(saved_targets), parent_pair_rows=len(saved_pairs),
                  full_worlds=len(world_keys), rename_worlds=len(worlds), future_rows=len(saved_futures),
                  prediction_groups=len(prediction_groups), quantity_positions=len(quantity_rows),
                  method='Source-complete schedule; closed-form alias partition; separate full state replay; all candidates and future comparisons',
                  independent_observer=False, meaning_validation=False, held_access=False,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(E / 'VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(validation, indent=2))
