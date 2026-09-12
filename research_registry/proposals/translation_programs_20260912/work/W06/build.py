"""Apply W06's two contracts to frozen W05 arguments; no learned decoder."""
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
W2, W5 = E.parent / 'W02', E.parent / 'W05'
S = json.loads((E / 'SPEC.json').read_text())
for f in S['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']

def read(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def table(name, rows, cols=None):
    cols = cols or list(rows[0])
    with (E / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=cols + ['row_status'], delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(dict(r, row_status='recorded') for r in rows)

def save(name, data):
    (E / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

source = json.loads((W2 / 'SOURCE.json').read_text())
raw = json.loads((W2 / 'ALTERNATE_LINES.json').read_text())['readings']
lex = {r['form']: r for r in read(W2 / 'LEXICON.tsv')}
assert set(S['mix_forms']) == {w for w, r in lex.items() if r['role'] == 'MIX'}
args = read(W5 / 'ARGUMENTS.tsv')
old_alignment = read(W5 / 'ALIGNMENT.tsv')
gloss = {r['raw']: r['unchanged_W04_C'] for r in old_alignment}
paragraphs = [t['hosts']['ZL3b'][0] for t in source['targets']]
flats, coverage, alignment = {}, [], []

for edition, lines in raw.items():
    mapped = {l['metadata']['locus']: l for l in lines}
    for p in paragraphs:
        assert not p['page'].startswith('f84')
        flat = []
        for line in p['lines']:
            groups = mapped[line['locus']]['groups']
            if edition == 'ZL3b':
                assert [g['ivtff_group_raw'] for g in groups] == line['words']
            for i, g in enumerate(groups, 1):
                word = g['ivtff_group_raw']
                flat.append(dict(id=f"{line['locus']}:{i}", locus=line['locus'], index=i,
                                 offset=len(flat), form=word, role=lex.get(word, {}).get('role', 'OPEN'),
                                 left_separator=g['left_separator'], right_separator=g['right_separator']))
        flats[edition, p['id']] = flat
        coverage.append(dict(edition=edition, paragraph=p['id'], lines=len(p['lines']), groups=len(flat),
                             mix_events=sum(x['form'] in S['mix_forms'] for x in flat)))
        if edition == 'ZL3b':
            for x in flat:
                alignment.append(dict(paragraph=p['id'], locus=x['locus'], index=x['index'], raw=x['form'],
                    U=S['U_gloss'] if x['form'] in S['mix_forms'] else gloss[x['form']],
                    D=S['D_gloss'] if x['form'] in S['mix_forms'] else gloss[x['form']],
                    status='ASSUMED' if x['form'] in lex else 'UNREAD'))

events, later_materials, later_actions, relations, states = [], [], [], [], []
for a in args:
    if a['form'] not in S['mix_forms']:
        continue
    edition, grammar, paragraph = a['edition'], a['variant'], a['paragraph']
    flat = flats[edition, paragraph]
    byid = {x['id']: x for x in flat}
    op = byid[a['operation']]
    primary, secondary = a['patient'], a['coingredient']
    input_ids = {v for v in [primary, secondary] if v}
    input_forms = {byid[v]['form'] for v in input_ids}
    # Written right arguments may follow the operation. Same-run next verbs
    # remain later semantic actions even before those written arguments.
    cut = max([op['offset']] + [byid[v]['offset'] for v in input_ids])
    same_args = [r for r in args if (r['edition'], r['variant'], r['paragraph']) == (edition, grammar, paragraph)]
    secondary_owners = [r['operation'] for r in same_args
                        if r['operation'] != a['operation'] and secondary
                        and secondary in {r['patient'], r['coingredient']}]
    base = dict(edition=edition, grammar=grammar, paragraph=paragraph, operation=a['operation'], form=a['form'])
    for model in S['mix_models']:
        debts = a['debts'].split(';') if a['debts'] else []
        if model == 'U':
            debts = [d for d in debts if d != 'MISSING_COINGREDIENT']
        composition = f'X({primary})' if primary else 'UNBOUND_PATIENT'
        if model == 'D':
            composition += '+' + (f'X({secondary})' if secondary else 'UNBOUND_SECOND')
        events.append(dict(**base, model=model, patient=primary, patient_form=a['patient_form'],
            inherited_second=secondary, second_form=byid[secondary]['form'] if secondary else '',
            second_used_by_mix=secondary if model == 'D' else '',
            second_not_used_by_mix=secondary if model == 'U' else '',
            second_other_operations=';'.join(secondary_owners),
            rule=a['rule'], additional_grammar_assumption=a['additional_grammar_assumption'],
            inherited_debts=a['debts'], remaining_debts=';'.join(debts),
            composition=composition, written_product_name='',
            status='CONDITIONAL_COMPOSITION' if primary and (model == 'U' or secondary) else 'INCOMPLETE_INPUTS'))
    for x in flat:
        if x['offset'] > cut and x['role'] in S['material_roles']:
            later_materials.append(dict(**base, mention=x['id'], material=x['form'],
                same_form_as_input=x['form'] in input_forms,
                identity='SAME_OR_NEW_UNRESOLVED' if x['form'] in input_forms else 'DIFFERENT_FORM_NO_PRODUCT_BINDING',
                independently_bound_composition=False))
        if x['offset'] > op['offset'] and x['form'] == 'oees':
            states.append(dict(**base, mention=x['id'], state_form=x['form'], assumed_meaning='gemischt',
                composition_discriminator=False, reason='NO_COMPOSITION_OR_PRODUCT_IDENTITY_BOUND'))
    following = [r for r in same_args if byid[r['operation']]['offset'] > op['offset']]
    for r in following:
        r_inputs = {v for v in [r['patient'], r['coingredient']] if v}
        exact = input_ids & r_inputs
        form_repeat = {byid[v]['form'] for v in r_inputs} & input_forms
        later_actions.append(dict(**base, next_operation=r['operation'], next_form=r['form'],
            next_patient=r['patient'], next_second=r['coingredient'],
            identical_written_inputs=';'.join(sorted(exact)),
            same_form_input_classes=';'.join(sorted(form_repeat)),
            next_debts=r['debts'],
            next_grammar_assumption=r['additional_grammar_assumption'],
            output_binding='NO_AUTOMATIC_MIX_OUTPUT_CARRY'))
        if r['form'] != 'qotchy':
            continue
        same_pair = bool(primary and secondary and r['patient'] and r['coingredient'] and input_ids == r_inputs)
        # U does not consume the secondary, but the same two written participants
        # can still be named by the following T/V instruction under W05 J/M.
        for model in S['mix_models']:
            for rival in S['relation_rivals']:
                if same_pair:
                    consequence = {('D', 'T'): 'JOIN_THEN_SEPARATE_SAME_WRITTEN_PAIR',
                                   ('U', 'T'): 'WORK_THEN_SEPARATE_PRIOR_JOIN_NOT_ESTABLISHED',
                                   ('D', 'V'): 'JOIN_THEN_JOIN_AGAIN_NO_AUTOMATIC_CONTRADICTION',
                                   ('U', 'V'): 'WORK_THEN_JOIN_SAME_WRITTEN_PAIR'}[model, rival]
                else:
                    consequence = 'NO_IDENTICAL_COMPLETE_INPUT_PAIR'
                relations.append(dict(**base, model=model, rival=rival, next_operation=r['operation'],
                    next_patient=r['patient'], next_second=r['coingredient'], identical_complete_pair=same_pair,
                    consequence=consequence, meaning_evidence=False))

table('ALIGNMENT.tsv', alignment)
table('COVERAGE.tsv', coverage)
table('MIX_COMPARISON.tsv', events)
table('LATER_MATERIALS.tsv', later_materials)
table('LATER_ACTIONS.tsv', later_actions)
table('RELATION_SEQUENCES.tsv', relations)
table('LATER_MIXED_STATES.tsv', states)

# All paragraph text, including paragraphs with no MIX event, stays reviewable.
reading = ['# Vollständige U/D-Lesungen auf dem unveränderten W05-Wortgerüst', '',
           'Jede deutsche Bedeutung ist eine Hypothese. U/D ändern nur die drei MIX-Ganzwörter; '
           'alle 900 Rohgruppen bleiben erhalten. B/J/M sind offene Satzrivalen. '
           'qotchy wird im Gerüst als „trenne“ gezeigt, der Verbinden-Rivale bleibt offen. '
           'Alle unveränderten Handlungsargumente und Qualitätsprobleme stehen weiterhin in W05/ARGUMENTS.tsv '
           'und W05/REPORT.md. Die folgenden Mischzeilen ersetzen allein die dortigen Mischverträge.', '']
for p in paragraphs:
    reading += ['## ' + p['id'], '']
    for line in p['lines']:
        rr = [r for r in alignment if r['locus'] == line['locus']]
        reading += [line['locus'] + ': `' + ' '.join(line['words']) + '`', '']
        if any(w in S['mix_forms'] for w in line['words']):
            reading += ['U: ' + ' · '.join(r['U'] for r in rr), '', 'D: ' + ' · '.join(r['D'] for r in rr), '']
            for e in events:
                if e['edition'] != 'ZL3b' or e['operation'].rsplit(':', 1)[0] != line['locus']:
                    continue
                reading += [f"- {e['grammar']}/{e['model']} {e['operation']}: A={e['patient']} {e['patient_form']}; "
                    f"B={e['second_used_by_mix'] or 'kein gebundener zweiter Eingang'}; "
                    f"nicht von MIX beanspruchter Zweitpartner={e['second_not_used_by_mix'] or '—'}; "
                    f"andere Verben an diesem Partner={e['second_other_operations'] or '—'}; "
                    f"offene Bezüge={e['remaining_debts'] or 'keine in diesem Teilvertrag'}; "
                    f"Zusatzgrammatik={e['additional_grammar_assumption'] or '—'}." ]
            reading.append('')
        else:
            reading += ['U=D: ' + ' · '.join(r['U'] for r in rr), '']
(E / 'READING.md').write_text('\n'.join(reading).rstrip() + '\n')

stats = []
for edition in raw:
    for grammar in S['grammars']:
        for model in S['mix_models']:
            selected = [r for r in events if (r['edition'], r['grammar'], r['model']) == (edition, grammar, model)]
            seq = [r for r in relations if (r['edition'], r['grammar'], r['model']) == (edition, grammar, model)]
            stats.append(dict(edition=edition, grammar=grammar, model=model, mix_events=len(selected),
                complete_input_sets=sum(r['status'] == 'CONDITIONAL_COMPOSITION' for r in selected),
                missing_seconds=sum('MISSING_COINGREDIENT' in r['remaining_debts'] for r in selected),
                events_with_other_debts=sum(bool(r['remaining_debts'].replace('MISSING_COINGREDIENT', '').strip(';')) for r in selected),
                written_second_not_used_by_mix=sum(bool(r['second_not_used_by_mix']) for r in selected),
                unused_second_without_other_operation=sum(bool(r['second_not_used_by_mix']) and not r['second_other_operations'] for r in selected),
                conditional_join_then_separate=sum(r['consequence'] == 'JOIN_THEN_SEPARATE_SAME_WRITTEN_PAIR' for r in seq)))
table('MODEL_SUMMARY.tsv', stats)
save('RESULT.json', dict(status='TWO_GLOBAL_CONTRACTS_RETAINED_LOCAL_D_T_SEQUENCE',
    primary_paragraphs=len(paragraphs), primary_lines=sum(len(p['lines']) for p in paragraphs),
    primary_groups=len(alignment), assumed_groups=sum(r['status'] == 'ASSUMED' for r in alignment),
    unread_groups=sum(r['status'] == 'UNREAD' for r in alignment), model_summary=stats,
    later_material_rows=len(later_materials), later_action_rows=len(later_actions),
    later_same_form_material_rows=sum(r['same_form_as_input'] for r in later_materials),
    relation_rows=len(relations), later_mixed_state_rows=len(states),
    independent_composition_bindings=0, meaning_identifications=0,
    independent_confirmation_capacity=0, significance_claim=False, held_access=False))
print(json.dumps({'events': len(events), 'later_materials': len(later_materials),
                  'later_actions': len(later_actions), 'relations': len(relations),
                  'primary_summary': [s for s in stats if s['edition'] == 'ZL3b']}, ensure_ascii=False, indent=2))
