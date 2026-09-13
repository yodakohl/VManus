"""Run registered, exposed, one-at-a-time result-name hypotheses. No decoder."""
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
W = E.parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
S = json.loads((E / 'SPEC.json').read_text())
for item in S['inputs']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']


def read(name):
    with (W / name).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def table(name, rows, columns):
    if 'row_status' not in columns:
        columns = columns + ['row_status']
        rows = [dict(row, row_status='recorded') for row in rows]
    with (E / name).open('w') as f:
        out = csv.DictWriter(f, fieldnames=columns, delimiter='\t', lineterminator='\n')
        out.writeheader()
        out.writerows(rows)


def dump(name, data):
    (E / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def js(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


D = {r['form']: r for r in read('W02/LEXICON.tsv')}
for word, override in json.loads((W / 'W05/SPEC.json').read_text())['word_overrides'].items():
    D[word] = dict(D[word], **override)
features = collections.defaultdict(list)
for item in json.loads((W / 'W03/SPEC.json').read_text())['features']:
    if item['kind'] != 'STANDALONE':
        features[item['form']].append(item)
processed = {f for f, ff in features.items() if any(x['kind'] == 'PROCESSED_NOMINAL' for x in ff)}
source = json.loads((W / 'W02/SOURCE.json').read_text())
alternates = json.loads((W / 'W02/ALTERNATE_LINES.json').read_text())['readings']
args = read('W05/ARGUMENTS.tsv')
quals = read('W05/QUALITY_ASSERTIONS.tsv')
alignment = read('W08/ALIGNMENT.tsv')
display = {r['raw']: r['N'] for r in alignment}
material_roles = {'MATERIAL', 'MATERIAL_DOSE'}
quantity_roles = {'MATERIAL_DOSE', 'AMOUNT', 'NUMBER', 'DISTRIBUTIVE', 'QUALITY_VALUE'}
opposed = {'moisture': {frozenset(('wet', 'dry'))},
           'thermal': {frozenset(('cold', 'warm')), frozenset(('cold', 'hot'))}}


def snapshots(obj):
    return {key: value['value'] for key, value in sorted(obj['state'].items())}


def execute(flat, operations, quality, target=None, parent_form=None):
    """An E baseline or one R world; all written names share one fixed SAME rule."""
    byid = {x['id']: x for x in flat}
    schedule = []
    for x in flat:
        if x['role'] in material_roles:
            schedule.append((x['offset'], 0, x['offset'], 'MATERIAL', x))
    for a in operations:
        positions = [byid[a['operation']]['offset']]
        positions += [byid[a[k]]['offset'] for k in ('patient', 'coingredient') if a[k]]
        schedule.append((max(positions), 1, byid[a['operation']]['offset'], 'ACTION', a))
    for q in quality:
        positions = [byid[q['mention']]['offset']]
        if q['patient']:
            positions.append(byid[q['patient']]['offset'])
        schedule.append((max(positions), 2, byid[q['mention']]['offset'], 'QUALITY', q))
    schedule.sort(key=lambda v: v[:3])
    names, mentions, objects, rows = {}, {}, {}, []

    def assertion(key, value, obj, location, debt, kind, order):
        old = obj['state'].get(key) if obj else None
        status = 'MISSING_PATIENT' if not obj else 'INITIAL_CONSTRAINT' if old is None else (
            'MATCH' if old['value'] == value else 'CONFLICT' if frozenset((old['value'], value)) in opposed[key.split(':')[1]] else 'DIFFERENT_NOT_OPPOSED')
        before = snapshots(obj) if obj else {}
        if obj and old is None:
            obj['state'][key] = {'value': value, 'origin': location}
        rows.append(dict(order=order, kind=kind, location=location, form=byid[location]['form'],
                         patient='', second='', object=obj['id'] if obj else '', second_object='',
                         source_object='', before=js(before), after=js(snapshots(obj) if obj else {}),
                         assertion=key + '=' + value, status=status, debts=debt,
                         state_origin=old['origin'] if old else '', alias_collision=False))

    for tick, _, written, kind, x in schedule:
        if kind == 'MATERIAL':
            word, location = x['form'], x['id']
            if location == target:
                assert word not in names and parent_form in names
                names[word] = names[parent_form]
                status = 'RENAMED_EXISTING_PORTION'
            elif word not in names:
                names[word] = location
                objects[location] = {'id': location, 'state': {}}
                status = 'EXTERNAL_PORTION'
            else:
                status = 'SAME_FORM_REMENTION'
            obj = objects[names[word]]
            mentions[location] = obj['id']
            rows.append(dict(order=tick, kind=kind, location=location, form=word, patient=location,
                             second='', object=obj['id'], second_object='', source_object='',
                             before=js(snapshots(obj)), after=js(snapshots(obj)), assertion='',
                             status=status, debts='SAME_FORM_IDENTITY_ASSUMED' if status == 'SAME_FORM_REMENTION' else '',
                             state_origin='', alias_collision=False))
            for f in features[word]:
                scope = 'PHYSICAL' if f['kind'] == 'PROCESSED_NOMINAL' else 'CONSTITUTION'
                assertion(scope + ':' + f['axis'], f['value'], obj, location, '', f['kind'], tick)
        elif kind == 'ACTION':
            patient = objects.get(mentions.get(x['patient']))
            second = objects.get(mentions.get(x['coingredient']))
            before = snapshots(patient) if patient else {}
            effect = S['effects'].get(x['form'])
            invalid = not patient or 'EXTRACT_PATIENT_NOT_BOUND' in x['debts'] or 'MISSING_RELATION_PARTNER' in x['debts']
            if invalid:
                status = 'ARGUMENT_INCOMPLETE'
            elif effect:
                patient['state']['PHYSICAL:' + effect['axis']] = {'value': effect['value'], 'origin': x['operation']}
                status = 'ASSUMED_EFFECT_APPLIED'
            else:
                status = 'NO_STATE_TRANSITION_MODELLED'
            rows.append(dict(order=tick, kind=kind, location=x['operation'], form=x['form'],
                             patient=x['patient'], second=x['coingredient'],
                             object=patient['id'] if patient else '', second_object=second['id'] if second else '',
                             source_object='', before=js(before), after=js(snapshots(patient) if patient else {}),
                             assertion=js(effect) if effect else '', status=status, debts=x['debts'], state_origin='',
                             alias_collision=bool(patient and second and patient['id'] == second['id'])))
        else:
            obj = objects.get(mentions.get(x['patient']))
            assertion(x['scope'] + ':' + x['axis'], x['value'], obj, x['mention'], x['debts'], kind, tick)
            rows[-1]['patient'] = x['patient']
    return rows, names, objects


targets, pairs, world_rows, traces, futures, quantities, paragraph_rows = [], [], [], [], [], [], []
world_number = 0
for edition, raw_lines in alternates.items():
    byline = {r['metadata']['locus']: r for r in raw_lines}
    for host in source['targets']:
        p = host['hosts']['ZL3b'][0]
        flat = []
        for line in p['lines']:
            for i, g in enumerate(byline[line['locus']]['groups'], 1):
                word = g['ivtff_group_raw']
                flat.append(dict(id=line['locus'] + ':' + str(i), locus=line['locus'], index=i,
                                 form=word, role=D.get(word, {}).get('role', 'OPEN'), offset=len(flat)))
        byid = {r['id']: r for r in flat}
        if edition == 'ZL3b':
            assert [r['form'] for r in flat] == [w for line in p['lines'] for w in line['words']]
        seen, target_list = set(), []
        for x in flat:
            if x['form'] in processed:
                target_list.append((x, x['form'] not in seen))
            seen.add(x['form'])
            if x['role'] in quantity_roles:
                quantities.append(dict(edition=edition, paragraph=p['id'], location=x['id'], form=x['form'],
                                       hypothesis=display.get(x['form'], D[x['form']]['hypothesis']), role=x['role'],
                                       amount_value='NOT_NUMERICALLY_IDENTIFIED', lineage_quantity='NOT_BOUND'))
        for grammar in S['grammars']:
            aa = [a for a in args if a['edition'] == edition and a['paragraph'] == p['id'] and a['variant'] == grammar]
            qq = [q for q in quals if q['paragraph'] == p['id'] and q['variant'] == grammar and q['kind'] == 'STANDALONE'] if edition == 'ZL3b' else []
            base, base_names, base_objs = execute(flat, aa, qq)
            base_key = 'E|' + edition + '|' + grammar + '|' + p['id']
            for n, row in enumerate(base):
                traces.append(dict(world=base_key, event=n, **row))
            paragraph_rows.append(dict(edition=edition, grammar=grammar, paragraph=p['id'],
                                       processed_mentions=len(target_list), first_names=sum(first for _, first in target_list),
                                       material_portions=len(base_objs), actions=len(aa),
                                       baseline_conflicts=sum(r['status'] == 'CONFLICT' for r in base)))
            for x, first in target_list:
                target_id = edition + '|' + grammar + '|' + x['id']
                expected = [f for f in features[x['form']] if f['kind'] == 'PROCESSED_NOMINAL']
                matching = []
                if first:
                    for a in aa:
                        if byid[a['operation']]['offset'] >= x['offset']:
                            continue
                        effect = S['effects'].get(a['form'])
                        when = max([byid[a['operation']]['offset']] + [byid[a[k]]['offset'] for k in ('patient', 'coingredient') if a[k]])
                        valid = bool(a['patient']) and not any(k in a['debts'] for k in ('MISSING_PATIENT', 'EXTRACT_PATIENT_NOT_BOUND', 'MISSING_RELATION_PARTNER'))
                        state_match = bool(effect and any(effect['axis'] == f['axis'] and effect['value'] == f['value'] for f in expected))
                        reason = 'INCOMPLETE_ARGUMENT' if not valid else 'COMPLETES_AT_OR_AFTER_TARGET' if when >= x['offset'] else 'SAME_WRITTEN_NAME' if a['patient_form'] == x['form'] else 'NO_REGISTERED_EFFECT_MATCH' if not state_match else 'CANDIDATE'
                        between = [z['id'] for z in flat if when < z['offset'] < x['offset'] and z['role'] == 'OPEN']
                        row = dict(target_id=target_id, target=x['id'], target_form=x['form'],
                                   operation=a['operation'], operation_form=a['form'], patient=a['patient'], patient_form=a['patient_form'],
                                   effect=js(effect), expected=js(expected), completion=when,
                                   status=reason, argument_debts=a['debts'], unread_bridge=';'.join(between))
                        pairs.append(row)
                        if reason == 'CANDIDATE':
                            matching.append(row)
                groups = collections.defaultdict(list)
                for a in matching:
                    groups[a['patient_form']].append(a)
                targets.append(dict(edition=edition, grammar=grammar, paragraph=p['id'], target=x['id'], form=x['form'],
                                    first_form_mention=first, matching_operations=len(matching), distinct_parent_names=len(groups),
                                    status='REMENTION_TRACKED' if not first else 'CANDIDATES' if groups else 'NO_REGISTERED_PARENT',
                                    source_names=';'.join(groups)))
                for parent_form, parents in groups.items():
                    world_number += 1
                    wid = 'R' + str(world_number).zfill(4)
                    trial, names, objects = execute(flat, aa, qq, x['id'], parent_form)
                    assert len(base) == len(trial)
                    new_conflicts, removed_conflicts, changes, later_actions, later_new_actions = [], [], [], [], []
                    physical_future_changes, bound_new_actions = [], []
                    parent_id = base_names[parent_form]
                    target_old_id = base_names[x['form']]
                    for n, (old, new) in enumerate(zip(base, trial)):
                        assert (old['kind'], old['location'], old['assertion']) == (new['kind'], new['location'], new['assertion'])
                        traces.append(dict(world=wid, event=n, **new))
                        if old['status'] != 'CONFLICT' and new['status'] == 'CONFLICT':
                            new_conflicts.append(new['location'] + '=' + new['assertion'])
                        if old['status'] == 'CONFLICT' and new['status'] != 'CONFLICT':
                            removed_conflicts.append(new['location'] + '=' + new['assertion'])
                        relevant = new['order'] >= x['offset'] and (new['object'] == parent_id or new['second_object'] == parent_id)
                        if not relevant:
                            continue
                        state_changed = old['before'] != new['before'] or old['after'] != new['after']
                        if state_changed:
                            changes.append(new['location'] + ':' + new['kind'])
                        physical_changed = any(
                            {k: v for k, v in json.loads(old[part]).items() if k.startswith('PHYSICAL:')} !=
                            {k: v for k, v in json.loads(new[part]).items() if k.startswith('PHYSICAL:')}
                            for part in ('before', 'after'))
                        beyond_introduction = new['location'] != x['id']
                        if physical_changed and beyond_introduction:
                            physical_future_changes.append(new['location'] + ':' + new['kind'])
                        if new['kind'] == 'ACTION' and old['object'] == target_old_id:
                            bound_new_actions.append(new['location'])
                        if new['kind'] == 'ACTION' and new['order'] > x['offset']:
                            later_actions.append(new['location'])
                            if old['object'] == target_old_id:
                                later_new_actions.append(new['location'])
                        futures.append(dict(world=wid, event=n, location=new['location'], form=new['form'], kind=new['kind'],
                                            E_object=old['object'], R_object=new['object'], E_second=old['second_object'], R_second=new['second_object'],
                                            E_before=old['before'], R_before=new['before'], E_after=old['after'], R_after=new['after'],
                                            E_status=old['status'], R_status=new['status'], state_values_differ=state_changed,
                                            debts=new['debts'], assertion=new['assertion'], alias_collision=new['alias_collision'],
                                            physical_values_differ=physical_changed,
                                            beyond_target_introduction=beyond_introduction))
                    target_checks = [r for r in trial if r['location'] == x['id'] and r['kind'] in ('PROCESSED_NOMINAL', 'BARE_NOMINAL')]
                    signature = hashlib.sha256(js([{k: r[k] for k in ('order', 'kind', 'location', 'form', 'patient', 'second', 'object', 'second_object', 'before', 'after', 'assertion', 'status', 'debts', 'alias_collision')} for r in trial]).encode()).hexdigest()
                    world_rows.append(dict(world=wid, edition=edition, grammar=grammar, paragraph=p['id'],
                                           target=x['id'], target_form=x['form'], parent_form=parent_form, parent_portion=parent_id,
                                           supporting_operations=';'.join(a['operation'] for a in parents),
                                           target_assertions=';'.join(r['assertion'] + ':' + r['status'] for r in target_checks),
                                           new_conflicts=';'.join(new_conflicts), removed_conflicts=';'.join(removed_conflicts),
                                           later_actions=';'.join(later_actions), later_actions_on_new_name=';'.join(later_new_actions),
                                           all_actions_on_new_name_after_binding=';'.join(bound_new_actions),
                                           physical_future_differences=';'.join(physical_future_changes),
                                           state_differences=len(changes), alias_collisions=sum(r['alias_collision'] for r in trial),
                                           E_portions=len(base_objs), R_portions=len(objects),
                                           unread_to_target=';'.join(sorted(set(v for a in parents for v in a['unread_bridge'].split(';') if v))),
                                           prediction_group=signature))

for name, rows in [('TARGETS.tsv', targets), ('ALL_PARENT_PAIRS.tsv', pairs), ('WORLDS.tsv', world_rows),
                   ('EVENTS.tsv', traces), ('FUTURE_COMPARISON.tsv', futures), ('QUANTITIES.tsv', quantities), ('PARAGRAPHS.tsv', paragraph_rows)]:
    table(name, rows, list(rows[0]))
table('ALIGNMENT.tsv', alignment, list(alignment[0]))
groups = collections.defaultdict(list)
for row in world_rows:
    groups[row['prediction_group']].append(row['world'])
table('PREDICTION_GROUPS.tsv', [dict(signature=k, worlds=';'.join(v), count=len(v)) for k, v in groups.items()], ['signature', 'worlds', 'count'])
summary = []
for edition in alternates:
    for grammar in S['grammars']:
        tt = [r for r in targets if r['edition'] == edition and r['grammar'] == grammar]
        ww = [r for r in world_rows if r['edition'] == edition and r['grammar'] == grammar]
        summary.append(dict(edition=edition, grammar=grammar, processed_mentions=len(tt), first_names=sum(r['first_form_mention'] for r in tt),
                            targets_with_candidates=sum(r['status'] == 'CANDIDATES' for r in tt), worlds=len(ww),
                            worlds_with_added_conflicts=sum(bool(r['new_conflicts']) for r in ww),
                            worlds_with_later_new_name_actions=sum(bool(r['later_actions_on_new_name']) for r in ww),
                            worlds_with_physical_future_differences=sum(bool(r['physical_future_differences']) for r in ww)))
dump('RESULT.json', dict(status='PAIRWISE_RESULT_RENAMING_FUTURES_RECORDED', paragraphs=13, lines=152, groups=900,
                         processed_forms=sorted(processed), summary=summary, target_rows=len(targets), parent_pair_rows=len(pairs),
                         world_rows=len(world_rows), prediction_groups=len(groups), event_rows=len(traces), future_rows=len(futures),
                         simultaneous_renamings=1, repeat_identity='SAME_ASSUMED', empirical_winner=None,
                         meaning_identifications=0, independent_confirmation_capacity=0, held_access=False, significance_claim=False))
lines = ['# W09 — vollständiger Wortlaut und bedingte Stoffverläufe', '',
         'Alle Wortwerte stammen aus W08; N≈nimm bleibt eine Hypothese. R/E ändern nur eine Stoffidentität, keine Wortübersetzung. Die einzelnen R-Konten sind Alternativen und nicht gemeinsam ausgewählte Verbindungen.', '']
for host in source['targets']:
    p = host['hosts']['ZL3b'][0]
    lines += ['## ' + p['id'], '']
    for line in p['lines']:
        rr = [r for r in alignment if r['locus'] == line['locus']]
        lines += [line['locus'] + ': `' + ' '.join(r['raw'] for r in rr) + '`', '', ' · '.join(r['N'] for r in rr), '']
        for r in world_rows:
            if r['edition'] == 'ZL3b' and r['target'].rsplit(':', 1)[0] == line['locus']:
                lines += [r['world'] + ' / ' + r['grammar'] + ': ' + r['target_form'] + ' könnte ' + r['parent_form'] +
                          ' nach ' + r['supporting_operations'] + ' neu bezeichnen; alternativ eigene Portion. Ziel: ' + r['target_assertions'] +
                          '. Zusätzliche Konflikte: ' + (r['new_conflicts'] or 'keine im begrenzten Konto') + '.', '']
(E / 'READING.md').write_text('\n'.join(lines).rstrip() + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))
