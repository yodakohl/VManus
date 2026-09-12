"""Enumerate consequences of SPEC; no fitting, decoding or source expansion."""
import collections, csv, hashlib, itertools, json
from pathlib import Path

E = Path(__file__).resolve().parent
P = E.parent / 'W02'
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
spec = json.loads((E / 'SPEC.json').read_text())
for src in spec['inputs']:
    assert hashlib.sha256((ROOT / src['path']).read_bytes()).hexdigest() == src['sha256'], src['path']
S = json.loads((P / 'SOURCE.json').read_text())
D = {x['form']: x for x in csv.DictReader((P / 'LEXICON.tsv').open(), delimiter='\t')}
oldargs = list(csv.DictReader((P / 'ARGUMENTS.tsv').open(), delimiter='\t'))
alt = json.loads((P / 'ALTERNATE_LINES.json').read_text())['readings']
actions = {'ACTION', 'MIX', 'REPEAT_ACTION', 'REPEAT_COOL', 'ACTION_TYPED'}
material = {'MATERIAL', 'MATERIAL_DOSE'}
F = collections.defaultdict(list)
for f in spec['features']:
    F[f['form']].append(f)

def save(name, obj):
    (E / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def table(name, rows, cols):
    with (E / name).open('w') as out:
        w = csv.DictWriter(out, fieldnames=cols + ['row_status'], delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(dict(r, row_status='recorded') for r in rows)

def gloss(word, relation='T'):
    if word == 'qotchy':
        return spec['relation_models'][relation]
    value = D.get(word, {}).get('hypothesis', '[ungelesen: ' + word + ']')
    bare = [x for x in F[word] if x['kind'] == 'BARE_NOMINAL']
    if bare:
        value += ' [angegebene Qualität als Stoffkonstitution]'
    return value

align, qualities, conflicts, pairs, later = [], [], [], [], []
readings = {k: ['# Q1 / ' + k + ': vollständige hypothetische Ausrichtung', '',
    'Jeder Wortwert ist angenommen. Die Anmerkung Stoffkonstitution ändert global die Reichweite der angegebenen nominalen Qualität; ausdrücklich verarbeitete Zustände bleiben physisch. Unbekanntes bleibt stehen. Zeilen und Trennpunkte sind keine entschlüsselte Syntax. ychor≈ferner bleibt Arbeitswert; nimm ist weiter möglich.', ''] for k in ['T', 'V']}
all_loci = []
for target in S['targets']:
    p = target['hosts']['ZL3b'][0]
    flat = []
    for l in p['lines']:
        for i, word in enumerate(l['words'], 1):
            flat.append(dict(id=l['locus'] + ':' + str(i), locus=l['locus'], index=i, form=word,
                             offset=len(flat), role=D.get(word, {}).get('role', 'OPEN')))
    for k in readings:
        readings[k] += ['## ' + p['id'], '']
    for l in p['lines']:
        all_loci.append(l['locus'])
        row = [x for x in flat if x['locus'] == l['locus']]
        for k in readings:
            readings[k] += [l['locus'] + ': `' + ' '.join(l['words']) + '`', '',
                            ' · '.join(gloss(w, k) for w in l['words']), '']
        for x in row:
            align.append(dict(paragraph=p['id'], locus=x['locus'], index=x['index'], raw=x['form'],
                              old_A=D.get(x['form'], {}).get('hypothesis', 'UNREAD'),
                              Q1_T=gloss(x['form']), Q1_V=gloss(x['form'], 'V'),
                              role=x['role'], status='ASSUMED' if x['form'] in D else 'UNREAD'))
            left_barrier = max([v['offset'] for v in row if v['offset'] < x['offset'] and v['role'] in actions], default=-1)
            right_barrier = min([v['offset'] for v in row if v['offset'] > x['offset'] and v['role'] in actions], default=10**9)
            mats = [v for v in row if left_barrier < v['offset'] < right_barrier and v['role'] in material]
            left = [v for v in mats if v['offset'] < x['offset']]
            right = [v for v in mats if v['offset'] > x['offset']]
            for f in F[x['form']]:
                patient = x if f['kind'] != 'STANDALONE' else (left[-1] if left else right[0] if right else None)
                debt = []
                if not patient:
                    debt.append('MISSING_MATERIAL_IN_FIXED_LOCAL_SCOPE')
                else:
                    lo, hi = sorted([x['offset'], patient['offset']])
                    debt += ['UNREAD_BETWEEN:' + v['id'] for v in row if lo < v['offset'] < hi and v['role'] == 'OPEN']
                for q in ['Q0', 'Q1']:
                    qualities.append(dict(model=q, paragraph=p['id'], locus=x['locus'], mention=x['id'], form=x['form'],
                        kind=f['kind'], axis=f['axis'], value=f['value'],
                        scope='CONSTITUTION' if q == 'Q1' and f['kind'] == 'BARE_NOMINAL' else 'PHYSICAL',
                        patient=patient['id'] if patient else '', patient_form=patient['form'] if patient else '',
                        debts=';'.join(debt)))
            if x['form'] != 'qotchy':
                continue
            a = left[-1] if left else right[0] if right else None
            b_options = [v for v in right + list(reversed(left)) if not a or v['id'] != a['id']]
            b = b_options[0] if b_options else None
            debts = []
            if not a or not b:
                debts.append('MISSING_EXPLICIT_PARTNER')
            else:
                lo, hi = min(a['offset'], b['offset'], x['offset']), max(a['offset'], b['offset'], x['offset'])
                debts += ['UNREAD_BETWEEN:' + v['id'] for v in row if lo < v['offset'] < hi and v['role'] == 'OPEN']
            old = next(v for v in oldargs if v['model'] == 'A' and v['operation'] == x['id'])
            pairs.append(dict(paragraph=p['id'], operation=x['id'], raw_line=' '.join(l['words']),
                A=a['id'] if a else '', A_form=a['form'] if a else '', A_hypothesis=gloss(a['form']) if a else '',
                B=b['id'] if b else '', B_form=b['form'] if b else '', B_hypothesis=gloss(b['form']) if b else '',
                T='trenne A von B', V='verbinde A mit B', debts=';'.join(debts),
                old_patient=old['patient_form'], old_debts=old['debts'], decision='T_V_UNRESOLVED'))
            for label, mat in [('A', a), ('B', b)]:
                if not mat:
                    continue
                # Includes the original mention for operations that follow it; remmentions separately labelled.
                mentions = [v for v in flat if v['form'] == mat['form'] and v['offset'] >= mat['offset']]
                for mention in mentions:
                    ops = [v for v in oldargs if v['model'] == 'A' and v['paragraph'] == p['id'] and
                        v['patient'] == mention['id'] and v['operation'] != x['id'] and
                        next(t['offset'] for t in flat if t['id'] == v['operation']) > x['offset']]
                    later.append(dict(operation=x['id'], partner=label, form=mat['form'], mention=mention['id'],
                        status='ORIGINAL_MENTION' if mention['id'] == mat['id'] else 'LATER_EXACT_FORM',
                        later_actions=';'.join(v['operation'] + '=' + v['meaning'] for v in ops),
                        action_debts=';'.join(v['debts'] for v in ops if v['debts']),
                        identity='SAME_OR_NEW_UNRESOLVED', isolation_evidence='NONE_FROM_FORM_IDENTITY_ALONE'))

grouped = collections.defaultdict(list)
for q in qualities:
    if q['patient']:
        grouped[(q['model'], q['locus'], q['patient'], q['axis'], q['scope'])].append(q)
for key, qs in grouped.items():
    for a, b in itertools.combinations(qs, 2):
        if [a['value'], b['value']] not in spec['opposed'][a['axis']] and [b['value'], a['value']] not in spec['opposed'][a['axis']]:
            continue
        conflicts.append(dict(model=key[0], locus=key[1], patient=key[2], axis=key[3], scope=key[4],
            first=a['mention'], first_form=a['form'], first_value=a['value'],
            second=b['mention'], second_form=b['form'], second_value=b['value'],
            status='CONDITIONAL_CONTRADICTION_UNDER_FIXED_BINDING'))

alt_rows, alt_occurrences, alt_pairs, critical_quality_lines = [], [], [], []
relation_loci = {r['operation'].rsplit(':', 1)[0] for r in pairs}
critical_loci = {r['locus'] for r in conflicts}
for edition, lines in alt.items():
    assert {x['metadata']['locus'] for x in lines} == set(all_loci)
    for line in lines:
        locus = line['metadata']['locus']
        words = [g['ivtff_group_raw'] for g in line['groups']]
        if locus in critical_loci:
            critical_quality_lines.append(dict(edition=edition, locus=locus, raw_line=' '.join(words),
                                               status='ALTERNATE_READING_NOT_INDEPENDENT_CONFIRMATION'))
        if locus in relation_loci:
            alt_rows.append(dict(edition=edition, locus=locus, raw_line=' '.join(words),
                                 literal_qotchy_count=words.count('qotchy'), meaning_test='NOT_INDEPENDENT'))
        for i, word in enumerate(words, 1):
            if word == 'qotchy':
                alt_occurrences.append(dict(edition=edition, locus=locus, index=i,
                    in_ZL_three_loci=locus in relation_loci, raw_line=' '.join(words)))
                roles = [D.get(w, {}).get('role', 'OPEN') for w in words]
                left_end = max([j for j in range(i-1) if roles[j] in actions], default=-1)
                right_end = min([j for j in range(i, len(words)) if roles[j] in actions], default=len(words))
                left = [j for j in range(left_end+1, i-1) if roles[j] in material]
                right = [j for j in range(i, right_end) if roles[j] in material]
                a = left[-1] if left else right[0] if right else None
                other = [j for j in right+list(reversed(left)) if j != a]
                b = other[0] if other else None
                alt_pairs.append(dict(edition=edition, locus=locus, index=i,
                    A_form=words[a] if a is not None else '', B_form=words[b] if b is not None else '',
                    complete=a is not None and b is not None,
                    decision='T_V_UNRESOLVED' if a is not None and b is not None else 'BOTH_HAVE_UNBOUND_ARGUMENTS',
                    raw_line=' '.join(words)))
outputs = [('ALIGNMENT.tsv', align), ('QUALITY_BINDINGS.tsv', qualities), ('QUALITY_CONTRADICTIONS.tsv', conflicts),
           ('RELATION_CANDIDATES.tsv', pairs), ('RELATION_CONTINUATIONS.tsv', later),
           ('RELATION_ALTERNATE_LINES.tsv', alt_rows), ('ALL_READING_QOTCHY_OCCURRENCES.tsv', alt_occurrences)]
outputs += [('ALL_READING_RELATION_BINDINGS.tsv', alt_pairs), ('CRITICAL_QUALITY_ALTERNATE_LINES.tsv', critical_quality_lines)]
for name, rows in outputs:
    assert rows, name
    table(name, rows, list(rows[0]))
for k, lines in readings.items():
    (E / ('READING_Q1_' + k + '.md')).write_text('\n'.join(lines))
save('RESULT.json', dict(status='EXPOSED_AUTHORED_REVISION_WITH_UNRESOLVED_RIVALS',
    paragraphs=len(S['targets']), lines=len(all_loci), groups=len(align),
    dictionary_assumptions=len(D), assigned=sum(x['status'] == 'ASSUMED' for x in align),
    unread=sum(x['status'] == 'UNREAD' for x in align),
    quality_assertions_per_model=len(qualities)//2,
    quality_unbound_per_model=sum(x['model']=='Q0' and not x['patient'] for x in qualities),
    bare_nominal_forms=len({f['form'] for f in spec['features'] if f['kind']=='BARE_NOMINAL'}),
    changed_nominal_positions=sum(any(f['kind']=='BARE_NOMINAL' for f in F[x['raw']]) for x in align),
    conflicts={q:[{k:v for k,v in x.items() if k!='model'} for x in conflicts if x['model']==q] for q in ['Q0','Q1']},
    explicit_qotchy_pairs=sum(bool(x['A'] and x['B']) for x in pairs),
    qotchy_cases=len(pairs), literal_qotchy_by_reading=dict(collections.Counter(x['edition'] for x in alt_occurrences)),
    complete_qotchy_pairs_by_reading=dict(collections.Counter(x['edition'] for x in alt_pairs if x['complete'])),
    incomplete_alternate_relation_cases=[x for x in alt_pairs if not x['complete']],
    relation_rival_selected=False, quality_revision_solves_draft=False,
    meaning_identifications=0, independent_confirmation_capacity=0, held_access=False, significance_claim=False))
print(json.dumps(json.loads((E/'RESULT.json').read_text()), ensure_ascii=False))
