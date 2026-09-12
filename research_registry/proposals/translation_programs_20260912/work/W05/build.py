"""Enumerate registered shared-object readings. No search or new word values."""
import collections,copy,csv,hashlib,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent/'W02';W4=E.parent/'W04'
ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
S=json.loads((E/'SPEC.json').read_text())
for f in S['inputs']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
source=json.loads((P/'SOURCE.json').read_text())
alternate=json.loads((P/'ALTERNATE_LINES.json').read_text())['readings']
D={r['form']:r for r in csv.DictReader((P/'LEXICON.tsv').open(),delimiter='\t')}
for word,override in S['word_overrides'].items():D[word]={**D[word],**override}
ACT=set(S['action_roles']);MAT=set(S['material_roles']);MOD=set(S['transparent_roles'])
previous=list(csv.DictReader((W4/'ARGUMENTS.tsv').open(),delimiter='\t'))
oldqualities=list(csv.DictReader((W4/'QUALITY_ASSERTIONS.tsv').open(),delimiter='\t'))
alignment=list(csv.DictReader((W4/'ALIGNMENT.tsv').open(),delimiter='\t'))
glosses={r['raw']:r['C'] for r in alignment}
extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}

def save(name,value):(E/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def table(name,rows,columns=None):
    columns=columns or list(rows[0])
    with (E/name).open('w') as out:
        w=csv.DictWriter(out,fieldnames=columns+['row_status'],delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)

def base_arguments(flat):
    materials=[x for x in flat if x['role'] in MAT];actions=[x for x in flat if x['role'] in ACT]
    rows=[]
    for x in actions:
        left=[v for v in materials if v['locus']==x['locus'] and v['offset']<x['offset']]
        end=min([v['offset'] for v in actions if v['locus']==x['locus'] and v['offset']>x['offset']],default=10**9)
        right=[v for v in materials if v['locus']==x['locus'] and x['offset']<v['offset']<end]
        earlier=[v for v in materials if v['offset']<x['offset']]
        a=left[-1] if left else right[0] if right else earlier[-1] if earlier else None
        rule='LOCAL_LEFT' if left else 'LOCAL_RIGHT' if right else 'PARAGRAPH_CARRY' if earlier else 'MISSING'
        debt=[]
        if a:
            lo,hi=sorted([a['offset'],x['offset']])
            debt+=['UNREAD_BETWEEN:'+v['id'] for v in flat if lo<v['offset']<hi and v['role']=='OPEN']
            if rule=='PARAGRAPH_CARRY':debt.append('IMPLICIT_SUBJECT_CONTINUATION')
        else:debt.append('MISSING_PATIENT')
        b=None
        if x['role']=='MIX':
            second=[v for v in left+right if not a or v['id']!=a['id']]
            b=second[-1] if second else None
            if not b:debt.append('MISSING_COINGREDIENT')
        if x['role']=='ACTION_TYPED' and (not a or a['form'] not in extracts):debt.append('EXTRACT_PATIENT_NOT_BOUND')
        if x['form']=='qotchy':
            start=max([v['offset'] for v in actions if v['locus']==x['locus'] and v['offset']<x['offset']],default=-1)
            left=[v for v in left if v['offset']>start]
            a=left[-1] if left else right[0] if right else None
            second=[v for v in right+list(reversed(left)) if not a or v['id']!=a['id']]
            b=second[0] if second else None;rule='RELATION_LOCAL';debt=[]
            if not a or not b:debt.append('MISSING_RELATION_PARTNER')
        rows.append(dict(operation=x['id'],form=x['form'],meaning=glosses.get(x['form'],D[x['form']]['hypothesis']),
            patient=a['id'] if a else '',patient_form=a['form'] if a else '',coingredient=b['id'] if b else '',
            rule=rule,debts=';'.join(debt),shared_run='',additional_grammar_assumption=''))
    return rows

allargs=[];allcases=[];changes=[];qualities=[];full=[];primary_material={};line_payload={}
for edition,lines in alternate.items():
    mapped={l['metadata']['locus']:l for l in lines}
    for target in source['targets']:
        p=target['hosts']['ZL3b'][0];flat=[]
        for line in p['lines']:
            raw=mapped[line['locus']]
            words=[g['ivtff_group_raw'] for g in raw['groups']]
            if edition=='ZL3b':assert words==line['words']
            for i,g in enumerate(raw['groups'],1):
                flat.append(dict(id=line['locus']+':'+str(i),locus=line['locus'],index=i,form=g['ivtff_group_raw'],
                    role=D.get(g['ivtff_group_raw'],{}).get('role','OPEN'),offset=len(flat),
                    left_separator=g['left_separator'],right_separator=g['right_separator']))
            line_payload[(edition,line['locus'])]=words
        byid={x['id']:x for x in flat};base=base_arguments(flat)
        versions={v:copy.deepcopy(base) for v in S['variants']}
        # Census every maximal raw-adjacent action run, including all blocked tails.
        runs=[]
        for line in p['lines']:
            row=[x for x in flat if x['locus']==line['locus']];i=0
            while i<len(row):
                if row[i]['role'] not in ACT:i+=1;continue
                j=i+1
                while j<len(row) and row[j]['role'] in ACT:j+=1
                if j-i>=2:runs.append((row,i,j))
                i=j
        for row,start,end in runs:
            run=row[start:end];rid=run[0]['id']+'-'+str(run[-1]['index'])
            case=dict(edition=edition,paragraph=p['id'],run=rid,locus=run[0]['locus'],
                verbs=' '.join(x['form'] for x in run),operations=';'.join(x['id'] for x in run),
                raw_line=' '.join(x['form'] for x in row),
                run_separators=';'.join(x['right_separator'] for x in run),
                same_word_repeat=len({x['form'] for x in run})<len(run))
            for variant in ['J','M']:
                pos=end;bridge=[]
                if variant=='M':
                    while pos<len(row) and row[pos]['role'] in MOD:bridge.append(row[pos]);pos+=1
                a=row[pos] if pos<len(row) and row[pos]['role'] in MAT else None
                tail=[]
                if a:
                    k=pos
                    while k<len(row) and row[k]['role'] in MAT|MOD:
                        if row[k]['role'] in MAT:tail.append(row[k])
                        k+=1
                case[variant+'_status']='SHARED_EXPLICIT_RIGHT' if a else 'LINE_END' if pos==len(row) else 'BLOCKED_'+row[pos]['role']
                case[variant+'_bridge']=';'.join(x['id']+'='+x['form'] for x in bridge)
                case[variant+'_primary']=a['id'] if a else ''
                case[variant+'_primary_form']=a['form'] if a else ''
                case[variant+'_tail']=';'.join(x['id'] for x in tail)
                case[variant+'_tail_separators']=';'.join(x['right_separator'] for x in row[end:pos+1])
                if not a:continue
                for arg in versions[variant]:
                    if arg['operation'] not in {x['id'] for x in run}:continue
                    x=byid[arg['operation']];debt=[];b=None
                    if x['role']=='MIX' or x['form']=='qotchy':
                        b=tail[1] if len(tail)>1 else None
                        if not b:debt.append('MISSING_COINGREDIENT' if x['role']=='MIX' else 'MISSING_RELATION_PARTNER')
                    if x['role']=='ACTION_TYPED' and a['form'] not in extracts:debt.append('EXTRACT_PATIENT_NOT_BOUND')
                    arg.update(patient=a['id'],patient_form=a['form'],coingredient=b['id'] if b else '',
                        rule='SHARED_RIGHT_'+variant,debts=';'.join(debt),shared_run=rid,
                        additional_grammar_assumption='COMMON_ARGUMENT_OF_ADJACENT_ASSUMED_VERBS')
            for v in S['variants']:
                members=[a for a in versions[v] if a['operation'] in {x['id'] for x in run}]
                case[v+'_patients']=';'.join(a['patient'] or 'UNBOUND' for a in members)
                case[v+'_seconds']=';'.join(a['coingredient'] or '-' for a in members)
                case[v+'_debts']=' | '.join(a['operation']+':'+a['debts'] for a in members if a['debts'])
            allcases.append(case)
        base_byid={r['operation']:r for r in base}
        for v,args in versions.items():
            for r in args:
                allargs.append(dict(edition=edition,variant=v,paragraph=p['id'],**r))
                old=base_byid[r['operation']]
                if any(old[k]!=r[k] for k in ['patient','coingredient','debts']):
                    changes.append(dict(edition=edition,variant=v,paragraph=p['id'],operation=r['operation'],form=r['form'],
                        old_patient=old['patient'],new_patient=r['patient'],old_patient_form=old['patient_form'],new_patient_form=r['patient_form'],
                        old_second=old['coingredient'],new_second=r['coingredient'],old_debts=old['debts'],new_debts=r['debts']))
        if edition!='ZL3b':continue
        for x in flat:
            full.append(dict(paragraph=p['id'],locus=x['locus'],index=x['index'],raw=x['form'],
                             unchanged_W04_C=glosses[x['form']],status='ASSUMED' if x['form'] in D else 'UNREAD'))
        primary_material[p['id']]=flat
        old={r['operation']:r for r in previous if r['model']=='C' and r['paragraph']==p['id']}
        for r in base:
            assert all(r[k]==old[r['operation']][k] for k in ['patient','patient_form','rule','coingredient','debts']),r['operation']
        for variant,args in versions.items():
            amap={r['operation']:r for r in args}
            ops=[x for x in flat if x['role'] in ACT]
            for q in oldqualities:
                if q['model']!='C' or q['attachment']!='R' or q['paragraph']!=p['id']:continue
                r={k:v for k,v in q.items() if k not in {'edition','model','attachment','row_status'}}
                x=byid[r['mention']]
                if r['kind']=='ACTION_EFFECT':
                    a=amap[r['mention']];r.update(patient=a['patient'],patient_form=a['patient_form'],debts=a['debts'])
                elif r['rule']=='ACTION_RESULT_REFERENCE':
                    op=max([o for o in ops if o['locus']==x['locus'] and o['offset']<x['offset']],key=lambda o:o['offset'])
                    a=amap[op['id']];r.update(patient=a['patient'],patient_form=a['patient_form'])
                    debt=['ASSUMED_RESULT_OR_PROCESS_CONDITION:'+op['id']]
                    if a['debts']:debt.append(a['debts'])
                    if a['patient']:
                        lo,hi=sorted([x['offset'],byid[a['patient']]['offset']])
                        debt+=['UNREAD_BETWEEN:'+z['id'] for z in flat if lo<z['offset']<hi and z['role']=='OPEN']
                    r['debts']=';'.join(debt)
                phase=0
                if r['patient'] and r['kind'] not in {'BARE_NOMINAL','PROCESSED_NOMINAL'}:
                    phase=sum(o['locus']==x['locus'] and o['offset']<=x['offset'] and amap[o['id']]['patient']==r['patient'] for o in ops)
                r['phase']=phase
                qualities.append(dict(variant=variant,**r))

conflicts=[];groups=collections.defaultdict(list)
for q in qualities:
    if q['patient']:groups[tuple(q[k] for k in ['variant','locus','patient','phase','axis','scope'])].append(q)
prior=json.loads((E.parent/'W03/SPEC.json').read_text())
for key,rows in groups.items():
    for a,b in itertools.combinations(rows,2):
        if sorted([a['value'],b['value']]) in [sorted(pair) for pair in prior['opposed'][a['axis']]]:
            conflicts.append(dict(variant=key[0],locus=key[1],patient=key[2],phase=key[3],first=a['mention'],second=b['mention']))
for name,rows in [('ALIGNMENT.tsv',full),('ALL_VERB_RUNS.tsv',allcases),('ARGUMENTS.tsv',allargs),('CHANGED_ARGUMENTS.tsv',changes),('QUALITY_ASSERTIONS.tsv',qualities)]:table(name,rows)
table('CONTRADICTIONS.tsv',conflicts,['variant','locus','patient','phase','first','second'])
stats=[]
for edition in alternate:
    for variant in S['variants']:
        ar=[r for r in allargs if r['edition']==edition and r['variant']==variant]
        cases=[r for r in allcases if r['edition']==edition]
        changed=[r for r in changes if r['edition']==edition and r['variant']==variant]
        stats.append(dict(edition=edition,variant=variant,commands=len(ar),maximal_runs=len(cases),
            eligible_runs=sum(r.get(variant+'_status')=='SHARED_EXPLICIT_RIGHT' for r in cases),
            shared_argument_commands=sum(bool(r['shared_run']) for r in ar),
            changed_patients=sum(r['old_patient']!=r['new_patient'] for r in changed),
            changed_secondary_arguments=sum(r['old_second']!=r['new_second'] for r in changed),
            commands_with_incomplete_arguments=sum(bool(r['debts']) for r in ar)))
table('MODEL_COMPARISON.tsv',stats)
text=['# Vollständiges Absatzpaket mit festen W04-C-Wortwerten und B/J/M-Bezügen','',
    'Alle Wortwerte und sämtliche gemeinsamen Objektbezüge sind Hypothesen. Rohgruppen bleiben erhalten. Änderungen der B/J/M-Argumente stehen unmittelbar unter der jeweiligen ganzen Zeile; fehlende zweite Argumente bleiben in ARGUMENTS.tsv sichtbar. Keine neue Wortübersetzung.','']
for target in source['targets']:
    p=target['hosts']['ZL3b'][0];text+=['## '+p['id'],'']
    for line in p['lines']:
        text+=[line['locus']+': `'+' '.join(line['words'])+'`','',' · '.join(glosses[w] for w in line['words']),'']
        ar=[r for r in allargs if r['edition']=='ZL3b' and r['operation'].rsplit(':',1)[0]==line['locus']]
        for variant in S['variants']:
            if not ar:continue
            display=[r['form']+' → '+(r['patient_form']+' ('+r['patient']+')' if r['patient'] else '[Patient fehlt]')+
                (' + '+r['coingredient'] if r['coingredient'] else '') for r in ar if r['variant']==variant]
            text += [variant+': '+'; '.join(display),'']
(E/'READING.md').write_text('\n'.join(text))
save('RESULT.json',dict(status='EXPOSED_SHARED_OBJECT_VARIANTS_EVALUATED',paragraphs=13,lines=152,groups=len(full),
    assumed=sum(r['status']=='ASSUMED' for r in full),unread=sum(r['status']=='UNREAD' for r in full),models=stats,
    primary_quality={v:dict(assertions=sum(r['variant']==v for r in qualities),
        unbound=sum(r['variant']==v and not r['patient'] for r in qualities),
        local_phase_contradictions=sum(r['variant']==v for r in conflicts)) for v in S['variants']},
    meaning_identifications=0,independent_confirmation_capacity=0,held_access=False,significance_claim=False))
print(json.dumps(stats,ensure_ascii=False,indent=2))
