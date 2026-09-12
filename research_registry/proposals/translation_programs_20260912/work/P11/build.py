"""Authored P11 six-predicate hypothesis; full exposed source and argument traces.
No decoder, optimizer, legacy grammar import, or semantic truth validation.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE=Path('research_registry/proposals/translation_programs_20260912/work')
P=BASE/'P11'
def dump(name,obj):
    (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def table(name,rows,fields):
    with (P/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

source=json.loads((BASE/'P09/INPUT.json').read_text())
assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['sha256']
dump('INPUT.json',source)
materials={
 'tcho':'Pflanzenmaterial','cthy':'Kraut','chor':'Blüten','shor':'Früchte',
 'cthey':'Arzneiform A','qody':'fertige Zubereitung','okaiin':'Ansatz',
 'tshaiin':'Flüssigauszug','chy':'Wasser','qotaiin':'abgeteilte Portion',
 'qotchol':'Trockenmaterial','otchol':'Trockenmaterial','ctho':'Pflanzenpulver',
 'shan':'Feinanteil','chocthy':'Pflanzenmark','cthaiin':'Pflanzenportion',
 'keol':'Öl','cthol':'Trockenmaterial','kooiin':'Wurzelmaterial',
 'qotcheaiin':'Feinpulver','cthold':'Pflanzenrückstand','ytchor':'zerkleinerte Blüten',
 'odaiin':'Zusatzportion'}
locations={'cfhy':'Filterstelle','taiin':'Auffanggefäß','kor':'Mörser','cho':'Inneres'}
other={'ol':'auch','s':'und','daiin':'Maß Γ','dain':'Maß Β','dair':'Anteil Β','dary':'Teilmenge',
       'shy':'feucht','otshy':'kalt-feucht','oltchy':'kalt-trocken'}
preds={
 'chol':{'D0':'ist trocken','I0':'trockne','D_roles':['bearer'],'I_roles':['agent','material'],'right':None},
 'shol':{'D0':'ist feucht','I0':'befeuchte','D_roles':['bearer'],'I_roles':['agent','material'],'right':None},
 'sho':{'D0':'enthält','I0':'führe zu','D_roles':['bearer','content'],'I_roles':['agent','material','recipient'],'right':'MATERIAL'},
 'qotchy':{'D0':'befindet sich bei','I0':'überführe nach','D_roles':['material','location'],'I_roles':['agent','material','destination'],'right':'LOCATION'},
 'shey':{'D0':'ist heiß','I0':'erwärme','D_roles':['bearer'],'I_roles':['agent','material'],'right':None},
 'chkaiin':{'D0':'ist gemischt','I0':'vermische','D_roles':['bearer'],'I_roles':['agent','material'],'right':None}}
dump('MODEL.json',{'hypothetical_only':True,'materials':materials,'locations':locations,'other':other,'predicates':preds,
 'identity':'each unclaimed noun mention introduces a mention-ID; repeated spelling is not automatic object identity',
 'topic':'latest unclaimed material mention inside paragraph; no lookahead or cross-page inheritance',
 'right_argument':'immediately next whole group inside paragraph; claimed once and not promoted to topic',
 'agent':'one implicit addressee per paragraph, shared by all I0 predicates',
 'D1':'same descriptive values and argument alignment as D0; assume nondecreasing time across every paragraph assertion, equal states may share time; no imperative established',
 'initial_location':'audit only; nearest preceding place does not prove containment or transfer origin'})
tokens=[]
for line in source['lines']:
    assert line['raw_line'].split()==line['groups']
    for i,w in enumerate(line['groups'],1):
        tokens.append({'page':line['locus'].split('.')[0],'locus':line['locus'],'position':i,'word':w,
                       'mention':line['locus']+':'+str(i)})
assert len(tokens)==145
events=[]; states=[]; conflicts=[]; claims=[]; scopes=[]
for page in dict.fromkeys(t['page'] for t in tokens):
    ts=[t for t in tokens if t['page']==page]
    current=None; last_place=None; claimed={}; properties={}
    for j,t in enumerate(ts):
        word=t['word']
        if word in materials and j not in claimed:
            current=t
        if word in locations and j not in claimed:
            last_place=t
        scopes.append({**t,'current_material':current['mention'] if current else 'UNWRITTEN_TOPIC:'+page,
                       'claimed_as_right_argument':claimed.get(j,'NA')})
        if word not in preds:continue
        card=preds[word]; right=ts[j+1] if j+1<len(ts) and card['right'] else None
        actual='MATERIAL' if right and right['word'] in materials else 'LOCATION' if right and right['word'] in locations else 'OPEN'
        status='NOT_REQUIRED' if not card['right'] else 'HYPOTHETICAL_TYPE_MATCH' if actual==card['right'] else 'UNRESOLVED_OR_TYPE_CONFLICT'
        if right:
            assert j+1 not in claimed
            claimed[j+1]=t['mention']
            claims.append({'predicate':t['mention'],'argument':right['mention'],'word':right['word'],'required_type':card['right'],'hypothetical_type':actual,'status':status})
        subject=current['mention'] if current else 'UNWRITTEN_TOPIC:'+page
        events.append({**t,'subject':subject,'subject_word':current['word'] if current else 'UNWRITTEN',
            'subject_value':materials[current['word']] if current else '[Absatzgegenstand]',
            'right_argument':right['mention'] if right else 'NA','right_word':right['word'] if right else 'NA',
            'right_value':(materials|locations).get(right['word'],'⟦'+right['word']+'⟧') if right else 'NA',
            'right_status':status,'D_arity':len(card['D_roles']),'I_arity':len(card['I_roles']),
            'I_agent':'IMPLICIT_ADDRESSEE:'+page,
            'nearest_prior_unclaimed_place':last_place['mention'] if last_place else 'NONE',
            'initial_location_of_material':'UNESTABLISHED_NOT_OBLIGATORY_VALENCY',
            'later_same_mention_reference':'NOT_IDENTIFIED'})
        if word in {'chol','shol'}:
            value='DRY' if word=='chol' else 'WET'
            before=properties.get(subject,'UNSPECIFIED')
            if before not in {'UNSPECIFIED',value}:
                conflicts.append({'predicate':t['mention'],'subject':subject,'previous_value':before,'new_value':value,
                                  'D0':'CONFLICT_IF_SAME_TIME_AND_AXIS','I0_or_D1':'STATE_CHANGE_IF_TEMPORAL_ORDER'})
            states.append({'predicate':t['mention'],'word':word,'subject':subject,'before':before,'after':value,'changed':before!=value})
            properties[subject]=value
table('PARTICIPANTS.tsv',events,list(events[0]))
role_rows=[]
for e in events:
    for model in ['D0','I0']:
        for role in preds[e['word']]['D_roles' if model=='D0' else 'I_roles']:
            if role=='agent':
                target,status=e['I_agent'],'SHARED_IMPLICIT_AGENT'
            elif role in {'content','location','destination'} or (model=='I0' and e['word']=='sho' and role=='material'):
                target,status=e['right_argument'],e['right_status']
            else:
                target,status=e['subject'],'HYPOTHETICAL_TOPIC_BINDING'
            role_rows.append({'model':model,'predicate':e['mention'],'word':e['word'],'role':role,'target':target,'status':status})
table('ROLE_BINDINGS.tsv',role_rows,list(role_rows[0]))
table('RIGHT_ARGUMENTS.tsv',claims,list(claims[0]))
table('TOPIC_TRACE.tsv',scopes,list(scopes[0]))
table('STATE_TRACE.tsv',states,list(states[0]))
table('STATIC_CONFLICTS.tsv',conflicts,list(conflicts[0]))

cards=[]
for w,c in preds.items():
    ev=[e for e in events if e['word']==w]
    cards.append({'word':w,'D0_value':c['D0'],'D0_roles':','.join(c['D_roles']),'I0_value':c['I0'],
       'I0_roles':','.join(c['I_roles']),'occurrences':len(ev),'loci':','.join(x['mention'] for x in ev),
       'meaning_status':'HYPOTHESIS_ONLY; valency not independently identified'})
table('SIX_PREDICATE_CARDS.tsv',cards,list(cards[0]))
common=materials|locations|other
lexrows=[]
for w,v in common.items():
    origin='P11_authored_concrete_assumption; overlaps earlier conjectures but no evidence credit'
    lexrows.append({'word':w,'value':v,'type':'MATERIAL' if w in materials else 'LOCATION' if w in locations else 'OTHER',
                    'origin':origin,'loci':','.join(t['mention'] for t in tokens if t['word']==w)})
table('COMMON_LEXICON.tsv',lexrows,list(lexrows[0]))
for model in ['D0','I0']:
    lex=common|{w:c[model] for w,c in preds.items()}
    alignment=[{**t,'reading':lex.get(t['word'],'⟦'+t['word']+'⟧'),'status':'HYPOTHESIS_ONLY' if t['word'] in lex else 'OPEN'} for t in tokens]
    table('ALIGNMENT_'+model+'.tsv',alignment,list(alignment[0]))
    text=['# P11 '+model+' — vier vollständige partielle Absatzlesungen','',
          'Jeder deutsche Wert ist angenommen; ⟦…⟧ bleibt offen. Physische Zeilen werden nicht mit Sätzen gleichgesetzt.','']
    for line in source['lines']:
        rr=[x for x in alignment if x['locus']==line['locus']]
        text+=['**'+line['locus']+'**','','`'+line['raw_line']+'`','',' / '.join(x['reading'] for x in rr),'']
    text+=['Vollständige Mitspielerzuweisung: PARTICIPANTS.tsv; zusammenhängende Inhaltsentwürfe: CHAPTER.md.','']
    (P/('READING_'+model+'.md')).write_text('\n'.join(text))

# Preserve every group in provisional predicate-delimited units; no hidden residue.
units=[]
for page in dict.fromkeys(t['page'] for t in tokens):
    ts=[t for t in tokens if t['page']==page]; cuts=sorted({0}|{i for i,t in enumerate(ts) if t['word'] in preds}|{len(ts)})
    for a,b in zip(cuts,cuts[1:]):
        units.append({'page':page,'start':ts[a]['mention'],'end':ts[b-1]['mention'],
                      'source':' '.join(t['word'] for t in ts[a:b]),'predicate':ts[a]['word'] if ts[a]['word'] in preds else 'OPEN_PREFIX'})
table('PROVISIONAL_UNITS.tsv',units,list(units[0]))
assert sum(len(u['source'].split()) for u in units)==145
result={'status':'PARTIAL_SHARED_PARTICIPANT_GRAMMAR_NO_MEANING_IDENTIFICATION','groups':145,
 'predicate_types':6,'predicate_occurrences':len(events),'common_word_assumptions':len(common),
 'hypothesis_positions':sum(t['word'] in common or t['word'] in preds for t in tokens),
 'open_positions':sum(t['word'] not in common and t['word'] not in preds for t in tokens),
 'unwritten_topic_uses':sum(e['subject_word']=='UNWRITTEN' for e in events),
 'right_argument_slots':len(claims),'right_type_matches_under_hypotheses':sum(c['status']=='HYPOTHETICAL_TYPE_MATCH' for c in claims),
 'I0_shared_implicit_agents':len({e['I_agent'] for e in events}),
 'D0_role_slots':sum(e['D_arity'] for e in events),'I0_role_slots':sum(e['I_arity'] for e in events),
 'static_opposite_state_transitions':len(conflicts),'transfer_initial_locations_established':0,
 'motion_after_qotchy_confirmed':0,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_pages_opened':0}
dump('RESULT.json',result)
dump('VALIDATION.json',{'status':'PASS_SOURCE_AND_FIXED_ARGUMENT_RULE_ONLY','groups':145,'predicate_cards':6,
 'all_groups_in_units_once':True,'all_right_arguments_consumed_once':True,'semantic_truth_validated':False})
print(json.dumps(result,ensure_ascii=False,indent=2))
