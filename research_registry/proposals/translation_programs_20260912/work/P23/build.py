"""P23: fixed nominal descriptions; no new data or inferred actions."""
import csv, json, hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[5]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'research_registry/proposals/translation_programs_20260912/work/P12/PROSE.tsv'
def dump(name,obj): (HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def table(name,rows):
    with (HERE/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
model={'hypotheses_only':True,'names':{'shedy':'Flüssigkeit','lchedy':'Zusatzstoff','qokaiin':'Gefäß','sol':'Ansatz'},'descriptions':{'solkeedy':'zuvor erwärmter Ansatz','solchedy':'zuvor filtrierter Ansatz'},'actions':{'chedy':'erwärme','qokeedy':'fülle ein'},'reset':'record','K':'unique previous description type; zero missing, two ambiguous','W':'sol is unqualified Ansatz','identity':'mention positions, no proven individual identity','scope':'complete existing f83r prose workpack; no labels or new pages'}
dump('MODEL.json',model)
paths=[SOURCE,HERE/'DECISION.md',HERE/'MODEL.json']
dump('SOURCE.json',{'files':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in paths],'exposure':'All f83r text and motivating pairs previously exposed; no independent confirmation','sealed':['f84','f84r']})
lines=list(csv.DictReader(SOURCE.open(),delimiter='\t'))
assert len(lines)==51 and {r['page'] for r in lines}=={'f83r'}
groups=[]
for line in lines:
    for i,word in enumerate(line['zl3b_line'].split(),1):
        groups.append({'record':line['record_id'],'locus':line['locus'],'position':str(i),'source':line['locus']+':'+str(i),'word':word})
assert len(groups)==341
table('INPUT.tsv',[dict(g,row_status='recorded') for g in groups])
family=[]
for word in sorted({g['word'] for g in groups if g['word'].startswith('sol')}):
    obs=[g for g in groups if g['word']==word]
    family.append({'word':word,'count':len(obs),'sources':','.join(g['source'] for g in obs),'card':'SHORT' if word=='sol' else 'DESCRIPTION' if word in model['descriptions'] else 'OPEN','row_status':'recorded'})
table('SOL_FORMS.tsv',family)
all_align={};all_events={};all_refs={};coverage=[]
for version in ['K','W']:
    align=[];events=[];refs=[];record=None;prior={};patient=None;vessel=None
    for g in groups:
        if g['record']!=record: record=g['record'];prior={};patient=None;vessel=None
        word=g['word'];render='['+word+' — offen]';role='OPEN';qual='NA';license='NA'
        if word in model['descriptions']:
            prior.setdefault(word,[]).append(g['source'])
            render=model['descriptions'][word];role='MATERIAL';qual=word
            patient=(g['source'],render,qual)
        elif word=='sol':
            license='MISSING_INTRODUCTION' if not prior else 'LICENSED' if len(prior)==1 else 'AMBIGUOUS'
            qual=next(iter(prior)) if version=='K' and license=='LICENSED' else 'AMBIGUOUS' if version=='K' and license=='AMBIGUOUS' else 'UNKNOWN'
            render=model['descriptions'][qual] if qual in model['descriptions'] else 'Ansatz [Qualifikation '+('mehrdeutig' if qual=='AMBIGUOUS' else 'offen')+']'
            role='MATERIAL';patient=(g['source'],render,qual)
            refs.append(dict(g,version=version,introduction_types=','.join(prior) or 'NONE',introduction_sources=','.join(s for sources in prior.values() for s in sources) or 'NONE',license=license if version=='K' else 'INDEPENDENT_WORD',qualification=qual,render=render,row_status='recorded'))
        elif word in model['names']:
            render=model['names'][word]
            if word=='qokaiin': role='DESTINATION';vessel=g['source']
            else: role='MATERIAL';qual='UNKNOWN';patient=(g['source'],render,qual)
        elif word in model['actions']:
            role='ACTION';need=word=='qokeedy';missing=[]
            if patient is None: missing.append('MATERIAL')
            if need and vessel is None: missing.append('DESTINATION')
            status='MISSING_'+'_AND_'.join(missing) if missing else 'COMPLETE'
            render=model['actions'][word]+' '+(patient[1] if patient else '?Material')+(' in Gefäß@'+(vessel or '?') if need else '')
            events.append(dict(g,version=version,patient_source=patient[0] if patient else 'NONE',patient_description=patient[1] if patient else 'NONE',qualification=patient[2] if patient else 'NA',destination_source=vessel if need and vessel else 'NONE',status=status,render=render,row_status='recorded'))
        align.append(dict(g,version=version,role=role,qualification=qual,render=render,row_status='recorded'))
    table('ALIGNMENT_'+version+'.tsv',align);table('REFERENCES_'+version+'.tsv',refs);table('ACTIONS_'+version+'.tsv',events)
    out=['# P23 '+version+' — alle Gruppen, Bedeutungen hypothetisch','', 'Eckige offene Gruppen sind nicht übersetzt. Ausführliche Nominalbeschreibungen führen keine Handlung aus.','']
    for line in lines:
        subset=[r for r in align if r['locus']==line['locus']]
        out.extend(['**'+line['record_id']+' / '+line['locus']+'**', '', ' · '.join(r['word']+' → '+r['render'] for r in subset),''])
    (HERE/('READING_'+version+'.md')).write_text('\n'.join(out).rstrip()+'\n')
    all_align[version]=align;all_events[version]=events;all_refs[version]=refs
    for rec in dict.fromkeys(g['record'] for g in groups):
        a=[x for x in align if x['record']==rec];e=[x for x in events if x['record']==rec];r=[x for x in refs if x['record']==rec]
        coverage.append({'version':version,'record':rec,'groups':len(a),'hypothetical':sum(x['role']!='OPEN' for x in a),'open':sum(x['role']=='OPEN' for x in a),'shorts':len(r),'licensed':sum(x['license']=='LICENSED' for x in r),'actions':len(e),'complete_actions':sum(x['status']=='COMPLETE' for x in e),'row_status':'recorded'})
table('COVERAGE.tsv',coverage)
changed=[]
for k,w in zip(all_events['K'],all_events['W']):
    assert k['source']==w['source'] and k['patient_source']==w['patient_source'] and k['destination_source']==w['destination_source'] and k['status']==w['status']
    if k['qualification']!=w['qualification']:
        changed.append({'action_source':k['source'],'patient_source':k['patient_source'],'K_qualification':k['qualification'],'W_qualification':w['qualification'],'K_reading':k['render'],'W_reading':w['render'],'status':k['status'],'row_status':'recorded'})
table('CHANGED_ACTIONS.tsv',changed)
# Audit semantic redundancy: an explicit earlier heating already supplies heated
# history to the same mention in both versions. No cross-mention identity assumed.
history=[]
for index,(k,w) in enumerate(zip(all_events['K'],all_events['W'])):
    prior_heat=[e['source'] for e in all_events['W'][:index] if e['record']==w['record'] and e['word']=='chedy' and e['patient_source']==w['patient_source'] and w['patient_source']!='NONE']
    def facts(e):
        f=set()
        if e['qualification']=='solkeedy': f.add('HEATED')
        if e['qualification']=='solchedy': f.add('FILTERED')
        if prior_heat: f.add('HEATED')
        return f
    kf,wf=facts(k),facts(w)
    history.append({'action_source':k['source'],'patient_source':k['patient_source'],'earlier_explicit_heat':','.join(prior_heat) or 'NONE','K_history':','.join(sorted(kf)) or 'UNKNOWN','W_history':','.join(sorted(wf)) or 'UNKNOWN','additional_K_history':','.join(sorted(kf-wf)) or 'NONE','row_status':'recorded'})
table('HISTORY_AUDIT.tsv',history)
result={'status':'PARTIAL_NOMINAL_SHORT_REFERENCE_THREE_LICENSED_FOUR_UNINTRODUCED','groups':len(groups),'records':len({g['record'] for g in groups}),'hypothetical_positions':sum(x['role']!='OPEN' for x in all_align['K']),'open_positions':sum(x['role']=='OPEN' for x in all_align['K']),'sol_form_types':len(family),'short_references':len(all_refs['K']),'K_licenses':dict(Counter(r['license'] for r in all_refs['K'])),'description_mentions':sum(g['word'] in model['descriptions'] for g in groups),'actions_per_version':len(all_events['K']),'action_statuses':dict(Counter(e['status'] for e in all_events['K'])),'actions_with_changed_qualification':len(changed),'actions_with_additional_history':sum(x['additional_K_history']!='NONE' for x in history),'qualification_differences_redundant_after_explicit_heat':sum(x['qualification']!=y['qualification'] and h['additional_K_history']=='NONE' for x,y,h in zip(all_events['K'],all_events['W'],history)),'newly_complete_actions':0,'competing_description_cases':sum(r['license']=='AMBIGUOUS' for r in all_refs['K']),'independent_confirmation_capacity':0,'confirmed_meanings':0,'decision':'W remains base reading; K retained as bounded development rival, not selected translation'}
dump('RESULT.json',result)
print(json.dumps(result,ensure_ascii=False))
