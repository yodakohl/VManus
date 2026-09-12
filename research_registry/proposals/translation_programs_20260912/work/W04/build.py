"""Render finite authored role variants and all argument/quality consequences."""
import collections, csv, hashlib, itertools, json
from pathlib import Path

E = Path(__file__).resolve().parent
P = E.parent / 'W02'
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
spec = json.loads((E / 'SPEC.json').read_text())
for f in spec['input_files']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], f['path']
source = json.loads((P / 'SOURCE.json').read_text())
alt = json.loads((P / 'ALTERNATE_LINES.json').read_text())['readings']
D = {r['form']:r for r in csv.DictReader((P / 'LEXICON.tsv').open(), delimiter='\t')}
prior = json.loads((E.parent / 'W03' / 'SPEC.json').read_text())
F = collections.defaultdict(list)
for f in prior['features']:
    F[f['form']].append(f)
ACTIONS = {'ACTION', 'MIX', 'REPEAT_ACTION', 'REPEAT_COOL', 'ACTION_TYPED'}
MATERIALS = {'MATERIAL', 'MATERIAL_DOSE'}

def table(name, rows):
    with (E / name).open('w') as out:
        w = csv.DictWriter(out, fieldnames=list(rows[0])+['row_status'], delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(dict(r, row_status='recorded') for r in rows)

def save(name, obj):
    (E / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def gloss(word, model):
    if word in spec['variants'][model]:
        return spec['variants'][model][word]
    if word == 'qotchy':
        return 'trenne … von … [verbinde … mit … bleibt Rivale]'
    g = D.get(word, {}).get('hypothesis', '[ungelesen: '+word+']')
    if any(f['kind']=='BARE_NOMINAL' for f in F[word]):
        g += ' [nominale Qualität: Stoffkonstitution]'
    return g

def analyze(p, model, edition):
    overrides = spec['variants'][model]
    flat = []
    for line in p['lines']:
        for i,w in enumerate(line['words'],1):
            flat.append(dict(id=line['locus']+':'+str(i), locus=line['locus'], index=i,
                             form=w, offset=len(flat), role='ACTION' if w in overrides else D.get(w,{}).get('role','OPEN')))
    mats = [x for x in flat if x['role'] in MATERIALS]
    ops = [x for x in flat if x['role'] in ACTIONS]
    args = []
    for x in ops:
        left = [m for m in mats if m['locus']==x['locus'] and m['offset']<x['offset']]
        nxt = min([o['offset'] for o in ops if o['locus']==x['locus'] and o['offset']>x['offset']], default=10**9)
        right = [m for m in mats if m['locus']==x['locus'] and x['offset']<m['offset']<nxt]
        earlier = [m for m in mats if m['offset']<x['offset']]
        patient = left[-1] if left else right[0] if right else earlier[-1] if earlier else None
        rule = 'LOCAL_LEFT' if left else 'LOCAL_RIGHT' if right else 'PARAGRAPH_CARRY' if earlier else 'MISSING'
        debts = []
        if not patient:
            debts.append('MISSING_PATIENT')
        else:
            lo,hi = sorted([patient['offset'],x['offset']])
            debts += ['UNREAD_BETWEEN:'+v['id'] for v in flat if lo<v['offset']<hi and v['role']=='OPEN']
            if rule=='PARAGRAPH_CARRY': debts.append('IMPLICIT_SUBJECT_CONTINUATION')
        second = None
        if x['role']=='MIX':
            other = [m for m in left+right if not patient or m['id']!=patient['id']]
            second = other[-1] if other else None
            if not second: debts.append('MISSING_COINGREDIENT')
        if x['role']=='ACTION_TYPED' and (not patient or patient['form'] not in {'cheor','okeeor','okeor','keeor','cheeor','sheeor'}):
            debts.append('EXTRACT_PATIENT_NOT_BOUND')
        if x['form']=='qotchy':
            prev = max([o['offset'] for o in ops if o['locus']==x['locus'] and o['offset']<x['offset']],default=-1)
            local_left=[m for m in left if m['offset']>prev]
            patient=local_left[-1] if local_left else right[0] if right else None
            other=[m for m in right+list(reversed(local_left)) if not patient or m['id']!=patient['id']]
            second=other[0] if other else None
            rule='RELATION_LOCAL'; debts=[]
            if not patient or not second: debts.append('MISSING_RELATION_PARTNER')
        args.append(dict(edition=edition, model=model, paragraph=p['id'], operation=x['id'], form=x['form'],
            meaning=gloss(x['form'],model), patient=patient['id'] if patient else '',
            patient_form=patient['form'] if patient else '', rule=rule,
            coingredient=second['id'] if second else '', debts=';'.join(debts)))
    byop={r['operation']:r for r in args}; byid={x['id']:x for x in flat}
    qualities=[]
    for attachment in spec['attachment_variants']:
        for x in flat:
            for f in F[x['form']]:
                kind=f['kind']; patient=None; rule=''; debts=[]
                if x['form'] in overrides:
                    kind='ACTION_EFFECT'; ar=byop[x['id']]
                    patient=byid.get(ar['patient']); rule='REGISTERED_ACTION_RESULT'; debts=[ar['debts']] if ar['debts'] else []
                elif kind!='STANDALONE':
                    patient=x; rule='NOMINAL_INPUT'
                else:
                    lineops=[o for o in ops if o['locus']==x['locus']]
                    prev=[o for o in lineops if o['offset']<x['offset']]
                    lo=prev[-1]['offset'] if prev else -1
                    hi=min([o['offset'] for o in lineops if o['offset']>x['offset']],default=10**9)
                    local=[m for m in mats if m['locus']==x['locus'] and lo<m['offset']<hi]
                    left=[m for m in local if m['offset']<x['offset']]
                    right=[m for m in local if m['offset']>x['offset']]
                    patient=left[-1] if left else right[0] if right else None
                    rule='LOCAL_LEFT' if left else 'LOCAL_RIGHT' if right else 'MISSING'
                    if not patient and attachment=='R' and prev:
                        ar=byop[prev[-1]['id']]; patient=byid.get(ar['patient'])
                        if patient:
                            rule='ACTION_RESULT_REFERENCE'
                            debts.append('ASSUMED_RESULT_OR_PROCESS_CONDITION:'+prev[-1]['id'])
                            if ar['debts']: debts.append(ar['debts'])
                if patient and kind=='STANDALONE':
                    lo,hi=sorted([patient['offset'],x['offset']])
                    debts += ['UNREAD_BETWEEN:'+v['id'] for v in flat if lo<v['offset']<hi and v['role']=='OPEN']
                if not patient: debts.append('MISSING_MATERIAL_BINDING')
                # Each written material mention is a separate local carrier, not an inferred batch identity.
                phase=0
                if patient and kind not in {'BARE_NOMINAL','PROCESSED_NOMINAL'}:
                    phase=sum(o['locus']==x['locus'] and o['offset']<=x['offset'] and byop[o['id']]['patient']==patient['id'] for o in ops)
                qualities.append(dict(edition=edition,model=model,attachment=attachment,paragraph=p['id'],
                    locus=x['locus'],mention=x['id'],form=x['form'],kind=kind,axis=f['axis'],value=f['value'],
                    scope='CONSTITUTION' if kind=='BARE_NOMINAL' else 'PHYSICAL',
                    patient=patient['id'] if patient else '',patient_form=patient['form'] if patient else '',
                    phase=phase,rule=rule,debts=';'.join(dict.fromkeys(debts))))
    return flat,args,qualities

allargs,allqualities,allcand,align,contradictions,paragraph_rows=[],[],[],[],[],[]
critical_alternates=[]
primary={}
for edition in ['ZL3b','IT2a','RF1b']:
    mapped={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in alt[edition]}
    for target in source['targets']:
        host=target['hosts']['ZL3b'][0]
        p=dict(id=host['id'],lines=[dict(locus=l['locus'],words=mapped[l['locus']]) for l in host['lines']])
        if edition=='ZL3b': assert p['lines']==[{'locus':l['locus'],'words':l['words']} for l in host['lines']]
        for model in spec['variants']:
            flat,args,qualities=analyze(p,model,edition)
            for x in flat:
                if x['form'] in {'chol','oty'}:
                    ar=next((r for r in args if r['operation']==x['id']),None)
                    qr={r['attachment']:r for r in qualities if r['mention']==x['id']}
                    allcand.append(dict(edition=edition,model=model,paragraph=p['id'],position=x['id'],form=x['form'],
                        meaning=gloss(x['form'],model),role=x['role'],raw_line=' '.join(mapped[x['locus']]),
                        action_patient=ar['patient'] if ar else '',action_patient_form=ar['patient_form'] if ar else '',
                        action_rule=ar['rule'] if ar else '',action_debts=ar['debts'] if ar else '',
                        L_patient=qr['L']['patient'],L_debts=qr['L']['debts'],R_patient=qr['R']['patient'],R_debts=qr['R']['debts']))
            if edition!='ZL3b':
                critical_alternates += [r for r in qualities if r['locus'] in {'f9v.10','f22v.9'}]
                continue
            allargs+=args;allqualities+=qualities;primary[(model,p['id'])]=(p,flat,args,qualities)
            paragraph_rows.append(dict(model=model,paragraph=p['id'],groups=len(flat),
                commands=len(args),new_commands=sum(r['form'] in spec['variants'][model] for r in args),
                command_debts=sum(bool(r['debts']) for r in args)))
            if model=='N':
                for x in flat:
                    align.append(dict(paragraph=p['id'],locus=x['locus'],index=x['index'],raw=x['form'],
                        status='ASSUMED' if x['form'] in D else 'UNREAD',**{m:gloss(x['form'],m) for m in spec['variants']}))

groups=collections.defaultdict(list)
for r in allqualities:
    if r['patient']: groups[(r['model'],r['attachment'],r['locus'],r['patient'],r['phase'],r['axis'],r['scope'])].append(r)
for key, rows in groups.items():
    for a,b in itertools.combinations(rows,2):
        if sorted([a['value'],b['value']]) in [sorted(x) for x in prior['opposed'][a['axis']]]:
            contradictions.append(dict(model=key[0],attachment=key[1],locus=key[2],patient=key[3],phase=key[4],
                axis=key[5],scope=key[6],first=a['mention'],first_form=a['form'],second=b['mention'],second_form=b['form'],
                status='CONDITIONAL_SAME_PHASE_CONTRADICTION'))

base={r['operation']:r for r in allargs if r['model']=='N'}
changes=[]
for r in allargs:
    if r['model']=='N' or r['operation'] not in base: continue
    old=base[r['operation']]
    altered=[k for k in ['patient','rule','coingredient','debts'] if r[k]!=old[k]]
    if altered:
        changes.append(dict(model=r['model'],operation=r['operation'],form=r['form'],changed_fields=';'.join(altered),
            old_patient=old['patient'],old_patient_form=old['patient_form'],new_patient=r['patient'],new_patient_form=r['patient_form'],
            old_rule=old['rule'],new_rule=r['rule'],old_debts=old['debts'],new_debts=r['debts'],
            old_coingredient=old['coingredient'],new_coingredient=r['coingredient']))

repeats=[]
for target in source['targets']:
    for line in target['hosts']['ZL3b'][0]['lines']:
        for word in ['chol','oty']:
            positions=[i for i,w in enumerate(line['words'],1) if w==word]
            if len(positions)>1:
                for model in spec['variants']:
                    rows=[r for r in allcand if r['edition']=='ZL3b' and r['model']==model and r['position'] in [line['locus']+':'+str(i) for i in positions]]
                    repeats.append(dict(model=model,locus=line['locus'],form=word,positions=';'.join(str(i) for i in positions),
                        meaning=gloss(word,model),patients=';'.join(r['action_patient'] or r['L_patient'] or 'UNBOUND' for r in rows),
                        status='EVERY_WRITTEN_OCCURRENCE_RETAINED'))

for name,rows in [('ALIGNMENT.tsv',align),('ARGUMENTS.tsv',allargs),('QUALITY_ASSERTIONS.tsv',allqualities),
    ('CANDIDATE_TABLE.tsv',allcand),('CHANGED_OLD_ARGUMENTS.tsv',changes),('CONTRADICTIONS.tsv',contradictions),
    ('REPEATED_FORMS.tsv',repeats),('PARAGRAPH_TABLE.tsv',paragraph_rows),('CRITICAL_ALTERNATE_QUALITIES.tsv',critical_alternates)]:
    table(name,rows)

summary=[]
for model in spec['variants']:
    for attachment in spec['attachment_variants']:
        ar=[r for r in allargs if r['model']==model];q=[r for r in allqualities if r['model']==model and r['attachment']==attachment]
        c=[r for r in contradictions if r['model']==model and r['attachment']==attachment]
        summary.append(dict(model=model,attachment=attachment,commands=len(ar),
            new_commands=sum(r['form'] in spec['variants'][model] for r in ar),
            new_commands_with_debts=sum(r['form'] in spec['variants'][model] and bool(r['debts']) for r in ar),
            all_commands_with_debts=sum(bool(r['debts']) for r in ar),
            changed_old_patient_count=sum(r['model']==model and r['old_patient']!=r['new_patient'] for r in changes),
            quality_assertions=len(q),unbound_quality_assertions=sum(not r['patient'] for r in q),
            result_reference_assertions=sum(r['rule']=='ACTION_RESULT_REFERENCE' for r in q),
            conditional_contradictions=len(c),contradiction_loci=';'.join(sorted({r['locus'] for r in c}))))
table('MODEL_COMPARISON.tsv',summary)
for model in spec['variants']:
    text=['# '+model+': vollständiger hypothetischer Wortentwurf','',
        'Alle Werte sind Annahmen. Keine Übersetzung bestätigt. L/R ändern Bezüge und Zeitphasen, nicht diese Wortwerte; die zugehörigen Tabellen sind maßgebend. Q1-Stoffkonstitution, qotchy-Trennfassung und ychor≈ferner sind weiter unentschiedene Darstellungswahlen.','']
    for target in source['targets']:
        p=target['hosts']['ZL3b'][0];text+=['## '+p['id'],'']
        for line in p['lines']:
            text += [line['locus']+': `'+' '.join(line['words'])+'`','',' · '.join(gloss(w,model) for w in line['words']),'']
    (E/('READING_'+model+'.md')).write_text('\n'.join(text))
save('RESULT.json',dict(status='EXPOSED_ROLE_VARIANTS_EVALUATED',paragraphs=len(source['targets']),
    lines=len({r['locus'] for r in align}),groups=len(align),assigned=sum(r['status']=='ASSUMED' for r in align),
    unread=sum(r['status']=='UNREAD' for r in align),models=summary,
    candidate_counts={ed:dict(collections.Counter(r['form'] for r in allcand if r['edition']==ed and r['model']=='N')) for ed in alt},
    meaning_identifications=0,independent_confirmation_capacity=0,held_access=False,significance_claim=False))
print(json.dumps(summary,ensure_ascii=False,indent=2))
