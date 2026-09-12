"""P12 authored reference models over full guarded f83r. No decoder or fit search."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

P=Path('research_registry/proposals/translation_programs_20260912/work/P12')
def dump(name,x):
    (P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(name,rows,fields):
    with (P/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def read(name):
    with (P/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))
s=json.loads((P/'SOURCE.json').read_text())
assert hashlib.sha256(Path(s['source']).read_bytes()).hexdigest()==s['sha256']
assert hashlib.sha256((P/'PROSE.tsv').read_bytes()).hexdigest()==s['projection_sha256']
lines=read('PROSE.tsv');assert len(lines)==51 and {x['page'] for x in lines}=={'f83r'}
names={'shedy':{'slot':'A','meaning':'Flüssigkeit','type':'MATERIAL'},
       'qokaiin':{'slot':'B','meaning':'Gefäß','type':'CONTAINER'},
       'lchedy':{'slot':'C','meaning':'Zusatzstoff','type':'MATERIAL'}}
acts={'chedy':'erwärme','qokeedy':'fülle ein'}
dump('MODEL.json',{'hypothetical_only':True,'names':names,'actions':acts,
 'L0':'last explicitly mentioned A/B/C','L1':'last explicitly mentioned A/C; B only updates destination',
 'T0':'first explicitly mentioned A/C remains topic through record end',
 'identity_REUSE':'repeated whole form reuses one local candidate; not observed individual identity',
 'identity_FRESH':'each mention introduces a new instance of the same type',
 'reset':'every record, including embedded Q1/Q2; no lookahead, image default or inherited argument',
 'destination':'most recent explicit B in record; remains missing before first mention',
 'unknown_groups':'conserved open; cannot change memory in this limited model, not claimed semantically empty'})
tokens=[]
for line in lines:
    for i,w in enumerate(line['zl3b_line'].split(),1):
        tokens.append({**{k:line[k] for k in ['page','panel_id','record_id','locus']},'position':i,'word':w,'mention':line['locus']+':'+str(i)})
assert len(tokens)==341
all_events=[];all_mentions=[];all_trace=[];summaries=[]
def display(entity):
    return '[Teilnehmer fehlt]' if entity is None else entity['meaning']+' '+entity['id']
for identity in ['REUSE','FRESH']:
    for model in ['L0','L1','T0']:
        events=[];traces=[];mentions=[]
        for record in dict.fromkeys(t['record_id'] for t in tokens):
            last=material=topic=dest=None
            for t in [x for x in tokens if x['record_id']==record]:
                before={'L0':last,'L1':material,'T0':topic}[model]
                if t['word'] in names:
                    n=names[t['word']]
                    e={**n,'id':record+':'+n['slot']+('@'+t['mention'] if identity=='FRESH' else ''),'introduced_at':t['mention']}
                    last=e
                    if n['type']=='MATERIAL':
                        material=e
                        if topic is None:topic=e
                    else:dest=e
                    mentions.append({**t,'model':model,'identity':identity,'entity':e['id'],'type':e['type'],
                        'meaning':e['meaning'],'destination_after':display(dest)})
                after={'L0':last,'L1':material,'T0':topic}[model]
                traces.append({**t,'model':model,'identity':identity,'active_before':display(before),'active_after':display(after),
                    'trigger':t['word'] if t['word'] in names else 'NONE','destination':display(dest)})
                if t['word'] not in acts:continue
                issues=[]
                if after is None:issues.append('MISSING_PATIENT')
                if t['word']=='qokeedy':
                    if dest is None:issues.append('MISSING_DESTINATION')
                    if after and after['type']!='MATERIAL':issues.append('CONTAINER_AS_FILL_MATERIAL')
                    if after and dest and after['id']==dest['id']:issues.append('SELF_FILL')
                sentence='Erwärme ['+display(after)+'].' if t['word']=='chedy' else 'Fülle ['+display(after)+'] in ['+display(dest)+'] ein.'
                events.append({**t,'model':model,'identity':identity,
                    'patient':after['id'] if after else 'MISSING','patient_slot':after['slot'] if after else 'MISSING',
                    'patient_trigger':after['introduced_at'] if after else 'MISSING',
                    'destination':dest['id'] if dest else 'MISSING',
                    'destination_trigger':dest['introduced_at'] if dest else 'MISSING',
                    'issues':'|'.join(issues) or 'NONE_UNDER_HYPOTHESES',
                    'implicit_agent':'ADDRESSEE:'+record,'reading':sentence})
        all_events+=events;all_trace+=traces;all_mentions+=mentions
        summaries.append({'model':model,'identity':identity,'actions':len(events),
            'missing_patient':sum('MISSING_PATIENT' in e['issues'] for e in events),
            'missing_destination':sum('MISSING_DESTINATION' in e['issues'] for e in events),
            'container_as_material':sum('CONTAINER_AS_FILL_MATERIAL' in e['issues'] for e in events),
            'self_fill':sum('SELF_FILL' in e['issues'] for e in events),
            'issue_free_under_assumptions':sum(e['issues']=='NONE_UNDER_HYPOTHESES' for e in events)})
        if identity=='REUSE':
            byevent={e['mention']:e for e in events}
            bymention={e['mention']:e for e in mentions}
            rows=[]
            for t in tokens:
                if t['mention'] in byevent:value=byevent[t['mention']]['reading'];status='HYPOTHETICAL_ACTION_AND_REFERENCE'
                elif t['mention'] in bymention:value='['+bymention[t['mention']]['entity']+': '+bymention[t['mention']]['meaning']+']';status='HYPOTHETICAL_PARTICIPANT'
                else:value='⟦'+t['word']+'⟧';status='OPEN'
                rows.append({**t,'model':model,'reading':value,'status':status})
            table('ALIGNMENT_'+model+'.tsv',rows,list(rows[0]))
            text=['# P12 '+model+' — gesamte dokumentierte f83r-Prosa','',
                 'Fünf ganze Wortannahmen; ergänzte Handlungsteilnehmer in Klammern. Alle übrigen Wörter bleiben ungelöst.','']
            for line in lines:
                text+=['**'+line['locus']+' · '+line['record_id']+'**','','`'+line['zl3b_line']+'`','',
                        ' / '.join(x['reading'] for x in rows if x['locus']==line['locus']),'']
            (P/('READING_'+model+'.md')).write_text('\n'.join(text))
            reread=read('ALIGNMENT_'+model+'.tsv')
            assert [(x['locus'],int(x['position']),x['word']) for x in reread]==[(x['locus'],x['position'],x['word']) for x in tokens]
table('ACTION_REFERENCES.tsv',all_events,list(all_events[0]))
table('MENTIONS.tsv',all_mentions,list(all_mentions[0]))
table('MEMORY_TRACE.tsv',all_trace,list(all_trace[0]))
table('MODEL_SUMMARY.tsv',summaries,list(summaries[0]))
comparisons=[]
for identity in ['REUSE','FRESH']:
    ev={m:{e['mention']:e for e in all_events if e['model']==m and e['identity']==identity} for m in ['L0','L1','T0']}
    for loc in ev['L0']:
        refs=[ev[m][loc]['patient'] for m in ['L0','L1','T0']]
        comparisons.append({'identity':identity,'locus':loc,'word':ev['L0'][loc]['word'],
            'L0':refs[0],'L1':refs[1],'T0':refs[2],
            'L1_trigger':ev['L1'][loc]['patient_trigger'],'T0_trigger':ev['T0'][loc]['patient_trigger'],
            'L1_T0_differ':refs[1]!=refs[2],'any_differ':len(set(refs))>1})
table('ALL_MODEL_COMPARISONS.tsv',comparisons,list(comparisons[0]))
word_at={t['mention']:t['word'] for t in tokens}
trigger_rows=[]
for c in comparisons:
    if c['identity']=='REUSE' and c['L1_T0_differ']:
        loc=c['L1_trigger'];line,pos=loc.rsplit(':',1)
        trigger_rows.append({'action':c['locus'],'action_word':c['word'],'new_material_trigger':loc,
            'trigger_word':word_at[loc],'previous_whole_word':word_at.get(line+':'+str(int(pos)-1),'LINE_START'),
            'L1_target':c['L1'],'T0_target':c['T0'],
            'switch_status':'C_mention_changes_L1_only; no independently_identified_topic_marker'})
table('TRANSITION_TRIGGERS.tsv',trigger_rows,list(trigger_rows[0]))
records=[]
for record in dict.fromkeys(t['record_id'] for t in tokens):
    tt=[x for x in tokens if x['record_id']==record]
    records.append({'record':record,'groups':len(tt),'participant_mentions':sum(t['word'] in names for t in tt),
       'actions':sum(t['word'] in acts for t in tt),'untranslated':sum(t['word'] not in names and t['word'] not in acts for t in tt)})
table('RECORD_COVERAGE.tsv',records,list(records[0]))
units=[]
for record in dict.fromkeys(t['record_id'] for t in tokens):
    ts=[x for x in tokens if x['record_id']==record]
    cuts=sorted({0,len(ts)}|{i for i,t in enumerate(ts) if t['word'] in acts})
    for a,b in zip(cuts,cuts[1:]):
        units.append({'record':record,'start':ts[a]['mention'],'end':ts[b-1]['mention'],
                      'source':' '.join(t['word'] for t in ts[a:b]),'unit_type':'ACTION_START' if ts[a]['word'] in acts else 'OPEN_PREFIX'})
table('PROVISIONAL_UNITS.tsv',units,list(units[0]))
assert sum(len(x['source'].split()) for x in units)==341
result={'status':'PARTIAL_REFERENCE_COMPARISON_NO_CONFIRMED_ANAPHORA','groups':341,'lines':51,'records':7,
 'whole_word_assumptions':5,'word_counts':dict(Counter(t['word'] for t in tokens if t['word'] in names or t['word'] in acts)),
 'hypothesis_positions':sum(t['word'] in names or t['word'] in acts for t in tokens),
 'open_positions':sum(t['word'] not in names and t['word'] not in acts for t in tokens),
 'models':summaries,'L1_T0_differences_REUSE':sum(x['L1_T0_differ'] for x in comparisons if x['identity']=='REUSE'),
 'L1_T0_differences_FRESH':sum(x['L1_T0_differ'] for x in comparisons if x['identity']=='FRESH'),
 'confirmed_individual_identities':0,'identified_topic_switch_words':0,'confirmed_meanings':0,
 'independent_confirmation_capacity':0,'held_pages_opened':0}
dump('RESULT.json',result)
dump('VALIDATION.json',{'status':'PASS_SOURCE_AND_MEMORY_RULE_EXECUTION_ONLY','alignments':3,'groups_each':341,
 'identity_model_combinations':6,'all_source_groups_in_units_once':True,'meaning_validated':False})
print(json.dumps(result,ensure_ascii=False,indent=2))
