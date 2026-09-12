"""Expose complete continuations and costs of the C working variant; no new fitting."""
import collections, csv, json
from pathlib import Path
E=Path(__file__).resolve().parent;P=E.parent/'W02'
def read(name):return list(csv.DictReader((E/name).open(),delimiter='\t'))
def table(name,rows):
    with (E/name).open('w') as out:
        w=csv.DictWriter(out,fieldnames=list(rows[0])+['row_status'],delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)
D={r['form']:r for r in csv.DictReader((P/'LEXICON.tsv').open(),delimiter='\t')}
source=json.loads((P/'SOURCE.json').read_text())
args=read('ARGUMENTS.tsv');candidates=read('CANDIDATE_TABLE.tsv');qualities=read('QUALITY_ASSERTIONS.tsv')
drying=[];continuations=[]
for target in source['targets']:
    p=target['hosts']['ZL3b'][0]
    flat=[dict(id=l['locus']+':'+str(i),word=w,locus=l['locus']) for l in p['lines'] for i,w in enumerate(l['words'],1)]
    offsets={x['id']:i for i,x in enumerate(flat)}
    for r in args:
        if r['model']!='C' or r['paragraph']!=p['id'] or r['form']!='chol':continue
        meaning=D.get(r['patient_form'],{}).get('hypothesis','UNKNOWN')
        typ='EXPLICIT_LIQUID' if 'Flüssigkeit' in meaning or 'flüssig' in meaning else 'EXTRACT' if 'Auszug' in meaning else 'OTHER_OR_UNSPECIFIED'
        subsequent=[x for x in flat if x['word']==r['patient_form'] and offsets[x['id']]>offsets[r['operation']] and x['id']!=r['patient']]
        drying.append(dict(operation=r['operation'],patient=r['patient'],form=r['patient_form'],meaning=meaning,
            assumed_type=typ,later_exact_mentions=';'.join(x['id'] for x in subsequent),
            consequence='DRYING_A_LIQUID_REQUIRES_LOSS_OF_LIQUID_FORM;NO_PRODUCT_NAME_IDENTIFIED' if typ=='EXPLICIT_LIQUID' else
                'EXTRACT_PHYSICAL_FORM_UNSPECIFIED' if typ=='EXTRACT' else 'NO_ADDITIONAL_TYPE_CLAIM',
            same_instance_issue='LATER_LIQUID_REQUIRES_UNEXPLAINED_RESTORATION_UNDER_COMPLETE_DRYING' if typ=='EXPLICIT_LIQUID' and subsequent else '',
            identity='SAME_AND_NEW_REMAIN_OPEN',debts=r['debts']))
        for x in subsequent:
            later_ops=[a for a in args if a['model']=='C' and a['paragraph']==p['id'] and a['patient']==x['id'] and offsets[a['operation']]>offsets[r['operation']]]
            continuations.append(dict(operation=r['operation'],patient_form=r['patient_form'],later_mention=x['id'],
                subsequent_actions=';'.join(a['operation']+'='+a['meaning'] for a in later_ops),
                status='FORM_REPETITION_NOT_BATCH_IDENTITY'))
table('ALL_DRYING_CONTEXTS.tsv',drying);table('LATER_EXACT_MATERIAL_MENTIONS.tsv',continuations)
delta=[]
for attachment in ['L','R']:
    old={r['mention']:r for r in qualities if r['model']=='N' and r['attachment']==attachment and r['kind']=='STANDALONE'}
    for r in qualities:
        if r['model']!='C' or r['attachment']!=attachment or r['mention'] not in old or r['form']=='chol':continue
        b=old[r['mention']]
        if any(r[k]!=b[k] for k in ['patient','phase','rule']):
            delta.append(dict(attachment=attachment,mention=r['mention'],form=r['form'],old_patient=b['patient'],new_patient=r['patient'],
                old_phase=b['phase'],new_phase=r['phase'],old_rule=b['rule'],new_rule=r['rule'],
                status='BECOMES_UNBOUND' if b['patient'] and not r['patient'] else 'CHANGED_BINDING_OR_PHASE'))
table('UNCHANGED_STATE_WORD_DELTAS.tsv',delta)
text=['# Jede chol-/oty-Stelle des primären Pakets','',
      'chol wird hier in C als trockne geprüft; die oty-Zeilen zeigen daneben die nicht bevorzugte T-Änderung zu kühle. Alle N/C/T/CT-Werte und beide Zustandsbindungen, auch IT/RF, stehen in CANDIDATE_TABLE.tsv. Die Materialnamen sind W02-Annahmen. Keine Häufigkeit ist ein Bedeutungsbeleg.','',
      '| Ort | Ganzwort / hypothetischer Befehl | Gebundenes Material | Bezug / offene Abhängigkeit |',
      '|---|---|---|---|']
for r in candidates:
    if r['edition']!='ZL3b' or (r['form']=='chol' and r['model']!='C') or (r['form']=='oty' and r['model']!='T'):continue
    text.append('| '+r['position']+' | '+r['form']+'≈'+r['meaning']+' | '+r['action_patient_form']+'≈'+D.get(r['action_patient_form'],{}).get('hypothesis','ungebunden')+' ('+r['action_patient']+') | '+r['action_rule']+'; '+(r['action_debts'] or 'keine markierte Argumentlücke')+' |')
(E/'ALL_CANDIDATES.md').write_text('\n'.join(text)+'\n')
print(json.dumps(dict(drying_cases=len(drying),explicit_liquid=[r['operation'] for r in drying if r['assumed_type']=='EXPLICIT_LIQUID'],
    extract_cases=[r['operation'] for r in drying if r['assumed_type']=='EXTRACT'],
    later_liquid_problem=[r['operation'] for r in drying if r['same_instance_issue']],
    L_newly_unbound=[r['mention'] for r in delta if r['attachment']=='L' and r['status']=='BECOMES_UNBOUND'])))
