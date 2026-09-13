"""W07: finite whole-word remainder/portion contracts on the exposed packet."""
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

def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def table(name, data):
    with (E / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]) + ['row_status'], delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(dict(r, row_status='recorded') for r in data)

source = json.loads((W2 / 'SOURCE.json').read_text())
alternate = json.loads((W2 / 'ALTERNATE_LINES.json').read_text())['readings']
lex = {r['form']: r for r in rows(W2 / 'LEXICON.tsv')}
old = rows(W5 / 'ARGUMENTS.tsv')
alignment = rows(W5 / 'ALIGNMENT.tsv')
gloss = {r['raw']: r['unchanged_W04_C'] for r in alignment}
hosts = [t['hosts']['ZL3b'][0] for t in source['targets']]
flats, coverage, fields, cases = {}, [], [], []
prior, following, models = [], [], []
for edition, lines in alternate.items():
    lm = {r['metadata']['locus']: r['groups'] for r in lines}
    for p in hosts:
        assert not p['page'].startswith('f84')
        flat = []
        for line in p['lines']:
            raw = lm[line['locus']]
            if edition == 'ZL3b':
                assert [g['ivtff_group_raw'] for g in raw] == line['words']
            for i, g in enumerate(raw, 1):
                word = g['ivtff_group_raw']
                flat.append(dict(id=f"{line['locus']}:{i}", locus=line['locus'], index=i,
                    form=word, offset=len(flat), role=lex.get(word, {}).get('role', 'OPEN'),
                    left_separator=g['left_separator'], right_separator=g['right_separator']))
        flats[edition, p['id']] = flat
        byid = {x['id']: x for x in flat}
        ar = {g: [r for r in old if r['edition'] == edition and r['paragraph'] == p['id'] and r['variant'] == g]
              for g in S['retained_grammars']}
        assert {r['operation'] for r in ar['B']} == {r['operation'] for r in ar['J']} == {r['operation'] for r in ar['M']}
        action_ids = {r['operation'] for r in ar['B']}
        targets = [x for x in flat if x['form'] == S['target']]
        coverage.append(dict(edition=edition, paragraph=p['id'], lines=len(p['lines']), groups=len(flat), dam=len(targets)))
        for x in targets:
            base = dict(edition=edition, paragraph=p['id'], target=x['id'])
            local = [y for y in flat if y['locus'] == x['locus']]
            quantities = [y for y in local if y['role'] in S['quantity_roles']]
            target_field = None
            for q in quantities:
                left_bound = max([byid[a]['offset'] for a in action_ids if byid[a]['locus'] == x['locus']
                                  and byid[a]['offset'] < q['offset']], default=-1)
                right_bound = min([byid[a]['offset'] for a in action_ids if byid[a]['locus'] == x['locus']
                                   and byid[a]['offset'] > q['offset']], default=10**9)
                region = [y for y in local if left_bound < y['offset'] < right_bound and y['role'] in S['material_roles']]
                left = [y for y in region if y['offset'] < q['offset']]
                right = [y for y in region if y['offset'] > q['offset']]
                carrier = left[-1] if left else right[0] if right else None
                debt = []
                if carrier:
                    lo, hi = sorted([carrier['offset'], q['offset']])
                    debt = ['UNREAD_BETWEEN:' + y['id'] for y in local if lo < y['offset'] < hi and y['role'] == 'OPEN']
                else:
                    debt = ['MISSING_QUANTITY_CARRIER']
                r = dict(**base, quantity=q['id'], form=q['form'], inherited_meaning=lex[q['form']]['hypothesis'],
                    carrier=carrier['id'] if carrier else '', carrier_form=carrier['form'] if carrier else '',
                    rule='LOCAL_LEFT' if left else 'LOCAL_RIGHT' if right else 'MISSING',
                    debts=';'.join(debt), numerical_value='', equation='')
                fields.append(r)
                if q['id'] == x['id']:
                    target_field = r
            assert target_field is not None
            c = target_field['carrier']
            cname = target_field['carrier_form']
            cut = max(x['offset'], byid[c]['offset'] if c else -1)
            repeats = [y for y in flat if y['offset'] > cut and y['form'] == cname] if c else []
            next_fields = [y for y in flat if y['offset'] > cut and y['role'] in set(S['quantity_roles'] + S['material_roles'])]
            for y in next_fields:
                following.append(dict(**base, grammar='ALL', kind='MATERIAL' if y['role'] in S['material_roles'] else 'QUANTITY',
                    mention=y['id'], form=y['form'], patient='', second='',
                    relation_to_dam='SAME_OR_NEW_UNRESOLVED' if y['form'] == cname else 'NO_IDENTIFIED_REMAINDER_REFERENCE',
                    debts='', additional_grammar_assumption=''))
            local_relations = {}
            for grammar, aa in ar.items():
                compatible = []
                for a in aa:
                    o = byid[a['operation']]
                    argument_ids = set(filter(None, [a['patient'], a['coingredient']]))
                    same_id = bool(c and c in argument_ids)
                    same_form = bool(cname and cname in {byid[v]['form'] for v in argument_ids})
                    complete_pair = bool(a['form'] == 'qotchy' and a['patient'] and a['coingredient'])
                    if o['offset'] < x['offset']:
                        prior.append(dict(**base, grammar=grammar, operation=a['operation'], form=a['form'],
                            patient=a['patient'], second=a['coingredient'],
                            carrier_same_written_argument=same_id, carrier_same_form=same_form,
                            complete_qotchy_pair=complete_pair, debts=a['debts'],
                            relation='LOCAL_REMAINDER_PAIR_CANDIDATE' if same_id and complete_pair else 'NO_BOUND_SUBTRACTION'))
                        if same_id and complete_pair:
                            compatible.append(a)
                    elif o['offset'] > x['offset']:
                        later_named = {y['id'] for y in repeats}
                        rel = ('SAME_WRITTEN_CARRIER' if same_id else
                               'SAME_REMENTION_ASSUMPTION_REQUIRED' if argument_ids & later_named else
                               'NO_IDENTIFIED_REMAINDER_REFERENCE')
                        following.append(dict(**base, grammar=grammar, kind='ACTION', mention=a['operation'], form=a['form'],
                            patient=a['patient'], second=a['coingredient'], relation_to_dam=rel,
                            debts=a['debts'], additional_grammar_assumption=a['additional_grammar_assumption']))
                local_relations[grammar] = compatible
            # Group the unchanged grammar rivals only after checking all of them.
            signatures = {tuple((a['operation'], a['patient'], a['coingredient']) for a in aa)
                          for aa in local_relations.values()}
            assert len(signatures) == 1
            candidates = local_relations['B']
            case = dict(**base, raw_line=' '.join(y['form'] for y in local),
                        carrier=c, carrier_form=cname, attachment_rule=target_field['rule'],
                        attachment_debts=target_field['debts'], local_pair_operations=';'.join(a['operation'] for a in candidates),
                        later_same_form_mentions=';'.join(y['id'] for y in repeats),
                        same_line_quantity_fields=';'.join(q['id'] for q in quantities),
                        grammars_grouped='B;J;M', mix_models_grouped='U;D')
            cases.append(case)
            for model in S['models']:
                for rival in S['relation_rivals']:
                    active = candidates if rival == 'T' and model == 'R' else []
                    others = [a['coingredient'] if a['patient'] == c else a['patient'] for a in active]
                    status = ('PORTION_WITHOUT_SUBTRACTION_CLAIM' if model == 'P' else
                              'SEPARATED_PAIR_WITHOUT_WRITTEN_ORIGIN_STOCK' if active else
                              'NO_BOUND_ORIGIN_OR_WITHDRAWAL')
                    models.append(dict(**base, model=model, dam_meaning=S['models'][model], qotchy_rival=rival,
                        grammars='B;J;M', mix_rivals='U;D', carrier=c, carrier_form=cname,
                        attachment_debts=target_field['debts'], possible_separation=';'.join(a['operation'] for a in active),
                        counterpart_candidate=';'.join(others), origin_stock='', bound_withdrawal='',
                        written_remainder_reference=x['id'] if model == 'R' else '', symbolic_equation='', status=status,
                        later_same_form_mentions=case['later_same_form_mentions'],
                        independent_confirmation_capacity=0))

table('COVERAGE.tsv', coverage)
table('CASES.tsv', cases)
table('QUANTITY_FIELDS.tsv', fields)
table('CANDIDATES.tsv', models)
table('PRIOR_ACTIONS.tsv', prior)
table('CONTINUATIONS.tsv', following)

outalign = []
mixforms = {w for w, r in lex.items() if r['role'] == 'MIX'}
for r in alignment:
    a = {k: r[k] for k in ['paragraph', 'locus', 'index', 'raw', 'status']}
    for model in S['models']:
        for mix in S['retained_mix_models']:
            value = S['models'][model] if r['raw'] == 'dam' else (
                'arbeite gleichmäßig durch' if mix == 'U' else 'vermische zwei Materialien') if r['raw'] in mixforms else r['unchanged_W04_C']
            a[model + '_' + mix] = value
    outalign.append(a)
table('ALIGNMENT.tsv', outalign)
reading = ['# Vollständiger Arbeitsleser: dam als Restmenge oder Portion', '',
    'Alle Wortwerte, Mengenbindungen und Stoffbezüge sind Hypothesen. R/P ändern ausschließlich dam. '
    'U/D bleiben die globalen W06-Mischrivalen; qotchy=T wird angezeigt, V bleibt offen. '
    'Gleiche Angaben an einem Material sind keine automatisch addierbaren Portionen. '
    'Alle W05-B/J/M-Handlungsargumente und W04/W05-Qualitätsprobleme bleiben bestehen.', '']
for p in hosts:
    reading += ['## ' + p['id'], '']
    for line in p['lines']:
        aligned = [r for r in outalign if r['locus'] == line['locus']]
        reading += [line['locus'] + ': `' + ' '.join(line['words']) + '`', '']
        variants = {}
        for col in ['R_U', 'P_U', 'R_D', 'P_D']:
            value = ' · '.join(r[col] for r in aligned)
            variants.setdefault(value, []).append(col)
        for value, labels in variants.items():
            reading += [' / '.join(labels) + ': ' + value, '']
        for c in cases:
            if c['edition'] == 'ZL3b' and c['target'].rsplit(':', 1)[0] == line['locus']:
                reading += [f"dam-Träger: {c['carrier']} {c['carrier_form']}; Bindungsschuld: {c['attachment_debts'] or 'keine im lokalen Vertrag'}. "
                            f"Vorangehendes gleiches Trennpaar: {c['local_pair_operations'] or 'keines'}; "
                            f"spätere gleiche Form: {c['later_same_form_mentions'] or 'keine'}. "
                            'Ursprünglicher Gesamtbestand und abgezogene Menge sind nicht als Herkunftskette gebunden.', '']
(E / 'READING.md').write_text('\n'.join(reading).rstrip() + '\n')

result = dict(status='PORTION_EDITORIAL_DEFAULT_REMAINDER_OPEN', primary_paragraphs=len(hosts),
    primary_lines=sum(len(p['lines']) for p in hosts), primary_groups=len(outalign),
    assumed_groups=sum(r['status'] == 'ASSUMED' for r in outalign), unread_groups=sum(r['status'] == 'UNREAD' for r in outalign),
    source_cases=len(cases), primary_cases=sum(c['edition'] == 'ZL3b' for c in cases),
    candidate_rows=len(models), quantity_fields=len(fields), prior_action_rows=len(prior), continuation_rows=len(following),
    local_separation_candidates=sum(c['edition'] == 'ZL3b' and bool(c['local_pair_operations']) for c in cases),
    primary_later_same_form_cases=sum(c['edition'] == 'ZL3b' and bool(c['later_same_form_mentions']) for c in cases),
    complete_origin_withdrawal_remainder_chains=0, bound_symbolic_equations=0,
    empirical_global_winner=None, editorial_display='dam≈Portion; R≈Restmenge remains open',
    meaning_identifications=0, independent_confirmation_capacity=0, significance_claim=False, held_access=False)
(E / 'RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
