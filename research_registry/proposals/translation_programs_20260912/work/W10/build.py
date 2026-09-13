"""One frozen whole-word action rival; reuse W09's pure simulator only."""
import ast
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
W = E.parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
S = json.loads((E / 'SPEC.json').read_text())
for f in S['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']


def read(name):
    with (W / name).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def table(name, rows, cols=None):
    cols = cols or list(rows[0])
    if 'row_status' not in cols:
        cols = cols + ['row_status']
        rows = [dict(r, row_status='recorded') for r in rows]
    with (E / name).open('w') as f:
        wr = csv.DictWriter(f, fieldnames=cols, delimiter='\t', lineterminator='\n')
        wr.writeheader()
        wr.writerows(rows)


oldspec = json.loads((W / 'W09/SPEC.json').read_text())
source = json.loads((W / 'W02/SOURCE.json').read_text())
alternate = json.loads((W / 'W02/ALTERNATE_LINES.json').read_text())['readings']
D = {r['form']: r for r in read('W02/LEXICON.tsv')}
for word, override in json.loads((W / 'W05/SPEC.json').read_text())['word_overrides'].items():
    D[word].update(override)
features = collections.defaultdict(list)
for f in json.loads((W / 'W03/SPEC.json').read_text())['features']:
    if f['kind'] != 'STANDALONE': features[f['form']].append(f)
args, quality = read('W05/ARGUMENTS.tsv'), read('W05/QUALITY_ASSERTIONS.tsv')
oldworlds, oldpairs = read('W09/WORLDS.tsv'), read('W09/ALL_PARENT_PAIRS.tsv')
old_events = collections.defaultdict(list)
for r in read('W09/EVENTS.tsv'): old_events[r['world']].append(r)
alignment = read('W09/ALIGNMENT.tsv')

# Function-only extraction prevents W09's module body and writes from running.
module = ast.parse((W / 'W09/build.py').read_text())
definitions = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in {'js', 'snapshots', 'execute'}]
assert len(definitions) == 3
namespace = dict(json=json, features=features, material_roles={'MATERIAL', 'MATERIAL_DOSE'},
                 opposed={'moisture': {frozenset(('wet', 'dry'))}, 'thermal': {frozenset(('cold', 'warm')), frozenset(('cold', 'hot'))}})
exec(compile(ast.Module(body=definitions, type_ignores=[]), 'frozen_W09_functions', 'exec'), namespace)

events, differences, targets, continuations, liquids, repeated, summaries, oldlinks = [], [], [], [], [], [], [], []
for edition, lines in alternate.items():
    mapped = {r['metadata']['locus']: r['groups'] for r in lines}
    for host in source['targets']:
        p = host['hosts']['ZL3b'][0]
        flat = []
        for line in p['lines']:
            for i, g in enumerate(mapped[line['locus']], 1):
                word = g['ivtff_group_raw']
                flat.append(dict(id=line['locus'] + ':' + str(i), locus=line['locus'], index=i,
                                 form=word, role=D.get(word, {}).get('role', 'OPEN'), offset=len(flat)))
        byid = {r['id']: r for r in flat}
        for grammar in S['grammars']:
            aa = [a for a in args if (a['edition'], a['variant'], a['paragraph']) == (edition, grammar, p['id'])]
            qq = [q for q in quality if q['paragraph'] == p['id'] and q['variant'] == grammar and q['kind'] == 'STANDALONE'] if edition == 'ZL3b' else []
            worlds = [dict(world='E|' + '|'.join((edition, grammar, p['id'])), target=None, parent_form=None)]
            worlds += [r for r in oldworlds if (r['edition'], r['grammar'], r['paragraph']) == (edition, grammar, p['id'])]
            for world in worlds:
                traces = {}
                for model in S['models']:
                    effect = {k: v for k, v in S['models'][model].items() if k in ('axis', 'value')}
                    namespace['S'] = dict(effects={**oldspec['effects'], 'chol': effect})
                    trace, _, _ = namespace['execute'](flat, aa, qq, world['target'], world['parent_form'])
                    traces[model] = trace
                    for n, r in enumerate(trace):
                        events.append(dict(candidate=model, world=world['world'], event=n, **r))
                    if model == 'D':
                        assert len(trace) == len(old_events[world['world']])
                        for r, previous in zip(trace, old_events[world['world']]):
                            assert all(str(v) == previous[k] for k, v in r.items()), (world['world'], r['location'])
                    summaries.append(dict(edition=edition, grammar=grammar, paragraph=p['id'], world=world['world'], candidate=model,
                                          conflicts=sum(r['status'] == 'CONFLICT' for r in trace),
                                          different_not_opposed=sum(r['status'] == 'DIFFERENT_NOT_OPPOSED' for r in trace),
                                          unbound_assertions=sum(r['status'] == 'MISSING_PATIENT' for r in trace)))
                for n, (a, b) in enumerate(zip(traces['D'], traces['H'])):
                    assert all(a[k] == b[k] for k in ('kind', 'location', 'form', 'patient', 'second', 'object', 'second_object', 'debts', 'alias_collision'))
                    if any(a[k] != b[k] for k in ('before', 'after', 'status', 'assertion', 'state_origin')):
                        differences.append(dict(world=world['world'], event=n, location=a['location'], form=a['form'], kind=a['kind'],
                                                patient=a['patient'], object=a['object'], D_before=a['before'], H_before=b['before'],
                                                D_after=a['after'], H_after=b['after'], D_status=a['status'], H_status=b['status'],
                                                assertion_D=a['assertion'], assertion_H=b['assertion'], debts=a['debts']))
                if world['target']:
                    for pair in oldpairs:
                        if pair['target_id'] != edition + '|' + grammar + '|' + world['target'] or pair['patient_form'] != world['parent_form'] or pair['status'] != 'CANDIDATE': continue
                        expected = json.loads(pair['expected'])
                        h = S['models']['H'] if pair['operation_form'] == 'chol' else oldspec['effects'].get(pair['operation_form'], {})
                        supports = any(h.get('axis') == x['axis'] and h.get('value') == x['value'] for x in expected)
                        target_effects = {model: [r for r in trace if r['location'] == world['target'] and r['kind'] == 'PROCESSED_NOMINAL'] for model, trace in traces.items()}
                        oldlinks.append(dict(world=world['world'], edition=edition, grammar=grammar, target=world['target'], target_form=world['target_form'],
                                             parent=world['parent_form'], operation=pair['operation'], operation_form=pair['operation_form'],
                                             D_support=True, H_support=supports,
                                             D_target=';'.join(r['status'] for r in target_effects['D']), H_target=';'.join(r['status'] for r in target_effects['H']),
                                             H_status='EFFECT_SUPPORT_RETAINED' if supports else 'DRYING_ORIGIN_NO_LONGER_EXPLAINED'))
                    continue
                for n, (a, b) in enumerate(zip(traces['D'], traces['H'])):
                    if a['kind'] != 'ACTION' or a['form'] != 'chol': continue
                    patient_form = byid[a['patient']]['form'] if a['patient'] else ''
                    targets.append(dict(edition=edition, grammar=grammar, paragraph=p['id'], operation=a['location'], patient=a['patient'], patient_form=patient_form,
                                        D='trockne', H='erhitze', D_before=a['before'], H_before=b['before'], D_after=a['after'], H_after=b['after'], debts=a['debts']))
                    for j in range(n + 1, len(traces['D'])):
                        x, y = traces['D'][j], traces['H'][j]
                        if not a['object'] or a['object'] not in (x['object'], x['second_object']): continue
                        continuations.append(dict(edition=edition, grammar=grammar, operation=a['location'], patient=a['patient'], location=x['location'],
                                                  form=x['form'], kind=x['kind'], D_before=x['before'], H_before=y['before'], D_after=x['after'], H_after=y['after'],
                                                  D_status=x['status'], H_status=y['status'], assertion=x['assertion'], debts=x['debts']))
                    if patient_form in S['liquid_forms']:
                        later = [r['location'] for r in traces['D'][n + 1:] if r['kind'] == 'MATERIAL' and r['object'] == a['object'] and r['form'] in S['liquid_forms']]
                        liquids.append(dict(edition=edition, grammar=grammar, operation=a['location'], patient=a['patient'], patient_form=patient_form,
                                            later_liquid_mentions=';'.join(later), D='COMPLETE_DRYING_ASSERTED', H='NO_COMPLETE_DRYING_ASSERTED_NO_PHASE_GUARANTEE'))
                for model, trace in traces.items():
                    actions = [r for r in trace if r['kind'] == 'ACTION']
                    for a, b in zip(actions, actions[1:]):
                        if not a['patient'] or a['patient'] != b['patient'] or a['status'] != 'ASSUMED_EFFECT_APPLIED' or b['status'] != 'ASSUMED_EFFECT_APPLIED' or a['assertion'] != b['assertion']: continue
                        repeated.append(dict(candidate=model, edition=edition, grammar=grammar, paragraph=p['id'], first=a['location'], first_form=a['form'],
                                             second=b['location'], second_form=b['form'], patient=a['patient'], effect=a['assertion'],
                                             debts=';'.join(x for x in (a['debts'], b['debts']) if x)))

for name, data in [('EVENTS.tsv', events), ('DIFFERENCES.tsv', differences), ('TARGETS.tsv', targets), ('CONTINUATIONS.tsv', continuations),
                   ('LIQUIDS.tsv', liquids), ('REPEATED_EFFECTS.tsv', repeated), ('WORLD_SUMMARY.tsv', summaries), ('OLD_RESULT_LINKS.tsv', oldlinks)]:
    table(name, data)
# Readout of already computed continuations, not a new accept/reject threshold.
thermal_resets = []
for r in events:
    if not r['world'].startswith('E|') or r['kind'] != 'ACTION': continue
    before, after = json.loads(r['before']), json.loads(r['after'])
    if before.get('PHYSICAL:thermal') == 'hot' and after.get('PHYSICAL:thermal') == 'warm':
        thermal_resets.append(dict(candidate=r['candidate'], world=r['world'], location=r['location'], form=r['form'],
                                   patient=r['patient'], debts=r['debts'],
                                   limit='CATEGORICAL_HOT_TO_WARM_ASSIGNMENT_NOT_A_PROVEN_PHYSICAL_COOLING_OR_HEAT_MAINTENANCE'))
table('HOT_TO_WARM_ACTIONS.tsv', thermal_resets)
out = [dict(paragraph=r['paragraph'], locus=r['locus'], index=r['index'], raw=r['raw'], D=r['N'], H='erhitze' if r['raw'] == 'chol' else r['N'], status=r['status']) for r in alignment]
table('ALIGNMENT.tsv', out)
text = ['# W10 — vollständiger Heiz- und Trockenvergleich', '', 'H ändert ausschließlich chol in erhitze. D bleibt trockne. Beide sind Bedeutungsannahmen; alle offenen Formen und anderen Rivalen bleiben erhalten.', '']
for host in source['targets']:
    p = host['hosts']['ZL3b'][0]
    text += ['## ' + p['id'], '']
    for line in p['lines']:
        rr = [r for r in out if r['locus'] == line['locus']]
        text += [line['locus'] + ': `' + ' '.join(r['raw'] for r in rr) + '`', '', 'H: ' + ' · '.join(r['H'] for r in rr), '']
        if any(r['raw'] == 'chol' for r in rr): text += ['D: ' + ' · '.join(r['D'] for r in rr), '']
(E / 'READING.md').write_text('\n'.join(text).rstrip() + '\n')
stats = []
for edition in alternate:
    for grammar in S['grammars']:
        for model in S['models']:
            rr = [r for r in summaries if r['edition'] == edition and r['grammar'] == grammar and r['candidate'] == model and r['world'].startswith('E|')]
            stats.append(dict(edition=edition, grammar=grammar, candidate=model, baseline_conflicts=sum(r['conflicts'] for r in rr), different_not_opposed=sum(r['different_not_opposed'] for r in rr)))
result = dict(status='WHOLE_CHOL_HEATING_RIVAL_EXECUTED', primary_paragraphs=13, primary_lines=152, primary_groups=900, primary_changed_positions=24,
              target_rows=len(targets), event_rows=len(events), world_candidates=len(summaries), statistics=stats,
              old_result_link_rows=len(oldlinks), lost_drying_support=sum(not r['H_support'] for r in oldlinks),
              meaning_identifications=0, independent_confirmation_capacity=0, held_access=False, significance_claim=False)
(E / 'RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
