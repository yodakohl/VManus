"""Compare fixed additive links and take-arguments; do not learn word values."""
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
W2, W5, W7 = (E.parent / n for n in ['W02', 'W05', 'W07'])
S = json.loads((E / 'SPEC.json').read_text())
for f in S['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']

def rows(p):
    with p.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def table(name, data, cols=None):
    with (E / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=(cols or list(data[0])) + ['row_status'], delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(dict(r, row_status='recorded') for r in data)

source = json.loads((W2 / 'SOURCE.json').read_text())
raw = json.loads((W2 / 'ALTERNATE_LINES.json').read_text())['readings']
lex = {r['form']: r for r in rows(W2 / 'LEXICON.tsv')}
args = rows(W5 / 'ARGUMENTS.tsv')
qualities = rows(W5 / 'QUALITY_ASSERTIONS.tsv')
oldalign = rows(W7 / 'ALIGNMENT.tsv')
gloss = {r['raw']: r['P_U'] for r in oldalign}
w5spec = json.loads((W5 / 'SPEC.json').read_text())
mods = set(w5spec['transparent_roles'])
hosts = [t['hosts']['ZL3b'][0] for t in source['targets']]
kernels, frames, links, comparisons, take, effects = [], [], [], [], [], []
flats = {}
for edition, lines in raw.items():
    lm = {l['metadata']['locus']: l['groups'] for l in lines}
    for p in hosts:
        assert not p['page'].startswith('f84')
        flat = []
        for line in p['lines']:
            groups = lm[line['locus']]
            if edition == 'ZL3b': assert [g['ivtff_group_raw'] for g in groups] == line['words']
            for i, g in enumerate(groups, 1):
                word = g['ivtff_group_raw']
                flat.append(dict(id=f"{line['locus']}:{i}", locus=line['locus'], form=word, index=i, offset=len(flat),
                                 role=lex.get(word, {}).get('role', 'OPEN')))
        flats[edition, p['id']] = flat
        byid = {x['id']: x for x in flat}
        targets = [x for x in flat if x['form'] == 'ychor']
        for x in targets:
            assert x['index'] == 1, 'Unexpected noninitial target; do not silently apply first-word take rule.'
            loci = [l['locus'] for l in p['lines']]
            previous = loci[loci.index(x['locus']) - 1] if loci.index(x['locus']) else ''
            frames.append(dict(edition=edition, paragraph=p['id'], target=x['id'], previous_locus=previous,
                previous_raw=' '.join(z['form'] for z in flat if z['locus'] == previous),
                target_raw=' '.join(z['form'] for z in flat if z['locus'] == x['locus']),
                all_prior_loci=';'.join(loci[:loci.index(x['locus'])])))
        for grammar in S['grammars']:
            aa = [a for a in args if a['edition'] == edition and a['paragraph'] == p['id'] and a['variant'] == grammar]
            amap = {a['operation']: a for a in aa}
            kk = []
            for a in aa:
                debts = set(filter(None, a['debts'].split(';')))
                common = bool(a['patient']) and not (debts & {'MISSING_PATIENT', 'MISSING_RELATION_PARTNER', 'EXTRACT_PATIENT_NOT_BOUND'})
                k = dict(edition=edition, grammar=grammar, paragraph=p['id'], kernel=a['operation'] + ':ACT',
                    mention=a['operation'], locus=byid[a['operation']]['locus'], kind='ACTION', form=a['form'],
                    patient=a['patient'], patient_form=a['patient_form'], second=a['coingredient'],
                    predicate='ACT:' + a['form'], complete_U=common,
                    complete_D=common and 'MISSING_COINGREDIENT' not in debts,
                    interpretation=a['meaning'], debts=a['debts'], extra_grammar=a['additional_grammar_assumption'])
                kk.append(k)
            if edition == 'ZL3b':
                for q in qualities:
                    if q['variant'] != grammar or q['paragraph'] != p['id'] or q['kind'] not in S['primary_quality_kinds']: continue
                    kk.append(dict(edition=edition, grammar=grammar, paragraph=p['id'],
                        kernel=q['mention'] + ':STATE:' + q['axis'], mention=q['mention'], locus=q['locus'],
                        kind='STATE', form=q['form'], patient=q['patient'], patient_form=q['patient_form'], second='',
                        predicate='STATE:' + ':'.join(q[v] for v in ['axis', 'value', 'scope']),
                        complete_U=bool(q['patient']), complete_D=bool(q['patient']),
                        interpretation=' / '.join(q[v] for v in ['axis', 'value', 'scope']),
                        debts=q['debts'], extra_grammar=''))
            kernels.extend(kk)
            for x in targets:
                prior = [k for k in kk if byid[k['mention']]['offset'] < x['offset']]
                body = [k for k in kk if k['locus'] == x['locus']]
                for mix in S['mix_models']:
                    for model in ['AT', 'AP']:
                        found = []
                        for q in body:
                            for prev in prior:
                                if not q['complete_' + mix] or not prev['complete_' + mix]: continue
                                same_material = q['patient_form'] == prev['patient_form']
                                same_predicate = q['predicate'] == prev['predicate']
                                matches = (same_material and not same_predicate) if model == 'AT' else (same_predicate and not same_material)
                                if matches:
                                    r = dict(edition=edition, grammar=grammar, mix=mix, model=model, paragraph=p['id'], target=x['id'],
                                        prior_kernel=prev['kernel'], body_kernel=q['kernel'],
                                        prior_predicate=prev['predicate'], body_predicate=q['predicate'],
                                        prior_patient=prev['patient'], body_patient=q['patient'],
                                        prior_material=prev['patient_form'], body_material=q['patient_form'],
                                        prior_debts=prev['debts'], body_debts=q['debts'],
                                        identity='MATERIAL_CLASS_ONLY_NOT_BATCH' if model == 'AT' else 'DIFFERENT_WRITTEN_MATERIAL_CLASSES',
                                        independent_evidence=False)
                                    links.append(r); found.append(r)
                        covered = {r['body_kernel'] for r in found}
                        complete = sum(k['complete_' + mix] for k in body)
                        comparisons.append(dict(edition=edition, grammar=grammar, mix=mix, model=model, paragraph=p['id'], target=x['id'],
                            prior_kernels=len(prior), body_kernels=len(body), complete_body_kernels=complete,
                            linked_body_kernels=len(covered), possible_prior_links=len(found),
                            all_registered_body_kernels_linked=bool(body) and len(covered) == len(body),
                            status='NO_REGISTERED_BODY_PREDICATION' if not body else
                                   'ALL_REGISTERED_KERNELS_LINKED' if len(covered) == len(body) else 'INCOMPLETE_ADDITIVE_LINK',
                            scope='ACTIONS_AND_FIXED_STANDALONE_QUALITIES' if edition == 'ZL3b' else 'ACTIONS_ONLY'))
                # N adds one take command; first position means no local-left material.
                on_line = [z for z in flat if z['locus'] == x['locus']]
                acts = [z for z in on_line if z['id'] in amap]
                stop = min([z['offset'] for z in acts], default=10**9)
                right = [z for z in on_line if x['offset'] < z['offset'] < stop and z['role'] in S['material_roles']]
                earlier = [z for z in flat if z['offset'] < x['offset'] and z['role'] in S['material_roles']]
                a = right[0] if right else earlier[-1] if earlier else None
                rule = 'LOCAL_RIGHT' if right else 'PARAGRAPH_CARRY' if earlier else 'MISSING'
                debt = []
                if a:
                    lo, hi = sorted([a['offset'], x['offset']])
                    debt = ['UNREAD_BETWEEN:' + z['id'] for z in flat if lo < z['offset'] < hi and z['role'] == 'OPEN']
                    if rule == 'PARAGRAPH_CARRY': debt.append('IMPLICIT_SUBJECT_CONTINUATION')
                else: debt = ['MISSING_PATIENT']
                shared = []
                j = 1
                while j < len(on_line) and on_line[j]['id'] in amap:
                    shared.append(on_line[j]); j += 1
                if shared and grammar in ['J', 'M']:
                    if grammar == 'M':
                        while j < len(on_line) and on_line[j]['role'] in mods: j += 1
                    if j < len(on_line) and on_line[j]['role'] in S['material_roles']:
                        a = on_line[j]; rule = 'SHARED_RIGHT_' + grammar; debt = []
                        for z in shared:
                            previous_arg = amap[z['id']]
                            effects.append(dict(edition=edition, grammar=grammar, target=x['id'], old_operation=z['id'],
                                old_patient=previous_arg['patient'], N_patient=a['id'],
                                patient_changes=previous_arg['patient'] != a['id'],
                                new_grammar_assumption='TAKE_AND_FOLLOWING_VERB_SHARE_RIGHT_OBJECT'))
                take.append(dict(edition=edition, grammar=grammar, paragraph=p['id'], target=x['id'],
                    patient=a['id'] if a else '', patient_form=a['form'] if a else '', rule=rule, debts=';'.join(debt),
                    added_commands=1, shared_grammar=rule.startswith('SHARED_RIGHT'),
                    new_written_product='', independent_evidence=False))

table('FRAMES.tsv', frames)
table('KERNELS.tsv', kernels)
table('ADDITIVE_LINKS.tsv', links, ['edition','grammar','mix','model','paragraph','target','prior_kernel','body_kernel',
    'prior_predicate','body_predicate','prior_patient','body_patient','prior_material','body_material','prior_debts','body_debts','identity','independent_evidence'])
table('ADDITIVE_COMPARISON.tsv', comparisons)
table('TAKE_ARGUMENTS.tsv', take)
table('TAKE_OLD_EFFECTS.tsv', effects)
chains = []
for n in take:
    for a in args:
        if (a['edition'], a['variant'], a['paragraph']) != (n['edition'], n['grammar'], n['paragraph']): continue
        if not n['patient'] or a['patient'] != n['patient']: continue
        if a['operation'].rsplit(':', 1)[0] != n['target'].rsplit(':', 1)[0]: continue
        chains.append(dict(edition=n['edition'], grammar=n['grammar'], paragraph=n['paragraph'], target=n['target'],
            body_operation=a['operation'], body_form=a['form'], common_patient=n['patient'], material=n['patient_form'],
            take_debts=n['debts'], body_debts=a['debts'], new_product_identity=False))
table('TAKE_BODY_CHAINS.tsv', chains)

align, reading = [], ['# Vollständige AT/AP-, N- und Z-Körperlesungen', '',
    'Alle Inhalte und Bindungen sind Hypothesen. AT/AP zeigen ferner mit verschiedenen engen Anschlussregeln; '
    'N ergänzt nimm; Z lässt ychor semantisch offen. dam wird redaktionell als Portion gezeigt, Restmenge bleibt Rivale. '
    'U/D, qotchy T/V und B/J/M bleiben offen. Alle unveränderten Material-/Qualitätsprobleme aus W04–W07 bestehen fort.', '']
for p in hosts:
    reading += ['## ' + p['id'], '']
    for l in p['lines']:
        reading += [l['locus'] + ': `' + ' '.join(l['words']) + '`', '']
        values = []
        for i, w in enumerate(l['words'], 1):
            common = gloss[w]
            if lex.get(w, {}).get('role') == 'MIX': common = 'durcharbeiten [U] / zwei Materialien vermischen [D]'
            a = dict(paragraph=p['id'], locus=l['locus'], index=i, raw=w,
                additive='ferner' if w == 'ychor' else common,
                N='nimm' if w == 'ychor' else common,
                Z='[ychor: Rahmenbedeutung offen]' if w == 'ychor' else common,
                status='TARGET_HYPOTHESES' if w == 'ychor' else 'ASSUMED' if w in lex else 'UNREAD')
            align.append(a); values.append(a)
        for label, col in [('AT/AP', 'additive'), ('N', 'N'), ('Z', 'Z')] if 'ychor' in l['words'] else [('alle', 'additive')]:
            reading += [label + ': ' + ' · '.join(a[col] for a in values), '']
table('ALIGNMENT.tsv', align)
(E / 'READING.md').write_text('\n'.join(reading).rstrip() + '\n')
summary = []
for ed in raw:
    for g in S['grammars']:
        for mix in S['mix_models']:
            for model in ['AT', 'AP']:
                rr = [r for r in comparisons if (r['edition'], r['grammar'], r['mix'], r['model']) == (ed, g, mix, model)]
                summary.append(dict(edition=ed, grammar=g, mix=mix, model=model, targets=len(rr),
                    targets_without_registered_body_kernel=sum(r['body_kernels'] == 0 for r in rr),
                    targets_with_any_link=sum(r['possible_prior_links'] > 0 for r in rr),
                    targets_with_all_registered_kernels_linked=sum(r['all_registered_body_kernels_linked'] for r in rr),
                    possible_links=sum(r['possible_prior_links'] for r in rr)))
table('MODEL_SUMMARY.tsv', summary)
result = dict(status='EXPLICIT_ANTECEDENT_AND_TAKE_CONSEQUENCES_RECORDED', primary_paragraphs=len(hosts),
    primary_lines=sum(len(p['lines']) for p in hosts), primary_groups=len(align), primary_targets=sum(a['status'] == 'TARGET_HYPOTHESES' for a in align),
    body_assumed_groups=sum(a['status'] == 'ASSUMED' for a in align), unread_body_groups=sum(a['status'] == 'UNREAD' for a in align),
    frame_rows=len(frames), kernel_rows=len(kernels), comparison_rows=len(comparisons), link_rows=len(links),
    take_rows=len(take), take_old_effect_rows=len(effects), changed_old_patients=sum(e['patient_changes'] for e in effects),
    take_body_chain_rows=len(chains),
    primary_summary=[r for r in summary if r['edition'] == 'ZL3b'],
    primary_take_summary=[dict(grammar=g, commands=sum(r['edition'] == 'ZL3b' and r['grammar'] == g for r in take),
                              missing_patient=sum(r['edition'] == 'ZL3b' and r['grammar'] == g and not r['patient'] for r in take)) for g in S['grammars']],
    empirical_global_winner=None, meaning_identifications=0, independent_confirmation_capacity=0, significance_claim=False, held_access=False)
(E / 'RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
