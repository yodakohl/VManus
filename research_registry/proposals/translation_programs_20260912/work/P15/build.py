#!/usr/bin/env python3
"""Execute authored P15 hypotheses, not a decoder or meaning validator."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P15')
S=D.parent/'P12/PROSE.tsv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tsv(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
source=list(csv.DictReader(S.open(),delimiter='\t'))
assert len(source)==51 and {r['page'] for r in source}=={'f83r'}
words=[(r,i,w) for r in source for i,w in enumerate(r['zl3b_line'].split(),1)]
assert len(words)==341
lex={'shedy':'Flüssigkeit A','lchedy':'Zusatzstoff C','qokaiin':'Gefäß B','chedy':'erwärme','qokeedy':'fülle ein','qokeey':'laufendes Einfüllen','qokedy':'erreichter Füllzustand','qoteedy':'erneutes Einfüllen'}
js(D/'SOURCE.json',{'source':str(S),'sha256':sha(S),'original_guard_receipt':str(D.parent/'P12/SOURCE.json'),'decision_sha256':sha(D/'DECISION.md'),'scope':'f83r only, previously exposed','groups':341})
js(D/'MODEL.json',{'whole_word_hypotheses':lex,'reference':'P12 L1/REUSE, record reset','all_meanings_hypothetical':True,'unknown_words':'retained; no modeled transition, not proven inert'})
all_events=[];summaries=[];coverage=[]
for model in ['I','R']:
 alignment=[];events=[];record=None;active=None;vessel=None;ongoing={};completed={};states={};clock=0
 for r,i,w in words:
  rec=r['record_id'];loc=f"{r['locus']}:{i}"
  if rec!=record:
   record=rec;active=None;vessel=None;ongoing={};completed={};states={};clock=0
  before=json.dumps({'patient':active,'vessel':vessel,'running':ongoing,'completed':completed,'states':states},ensure_ascii=False,sort_keys=True)
  gloss='['+w+']';kind='OPEN';issues=[];prior='NA';used='NA';cause='NA';repeatstate=False
  if w in ['shedy','lchedy','qokaiin']:
   kind='MENTION';gloss=lex[w]
   if w=='qokaiin': vessel='B'
   else: active='A' if w=='shedy' else 'C'
  elif w in lex:
   kind={'chedy':'HEAT','qokeedy':'DIRECT','qokeey':'RUNNING','qokedy':'COMPLETE' if model=='I' else 'STATE','qoteedy':'REPEAT'}[w]
   if active is None: issues.append('MISSING_PATIENT')
   if kind!='HEAT' and vessel is None: issues.append('MISSING_DESTINATION')
   pair=active+'>'+vessel if active and vessel else None
   if kind!='STATE': clock+=1
   if kind=='HEAT':
    matches=[(k,v) for k,v in states.items() if k.startswith(str(active)+'>')]
    if matches: used=';'.join(v for k,v in matches)
    gloss='erwärme '+str(active or '?Stoff')
   else:
    noun=str(active or '?Stoff')+' in '+str(vessel or '?Gefäß')
    gloss=({'RUNNING':'beginne einzufüllen ' if model=='I' else 'wird gerade eingefüllt: ','DIRECT':'fülle ein: ','COMPLETE':'schließe Einfüllen ab: ','STATE':'ist eingefüllt: ','REPEAT':'fülle erneut ein: ' if model=='I' else 'wird erneut eingefüllt: '}[kind])+noun
    if pair:
     prior=completed.get(pair,'NA')
     if kind in ['RUNNING','REPEAT']:
      if pair in ongoing: issues.append('NEW_START_WHILE_RUNNING')
      if kind=='REPEAT' and pair not in completed: issues.append('NO_PRIOR_COMPLETED_EVENT')
      ongoing[pair]=loc
     elif kind=='DIRECT':
      cause=loc;completed[pair]=loc;states[pair]=loc;ongoing.pop(pair,None)
     elif kind=='COMPLETE':
      if pair not in ongoing: issues.append('NO_PRIOR_RUNNING_EVENT')
      else:
       cause=ongoing.pop(pair);completed[pair]=loc;states[pair]=loc
     elif kind=='STATE':
      repeatstate=pair in states
      if pair in ongoing:
       cause=ongoing.pop(pair);completed[pair]=loc
      elif pair in completed: cause=completed[pair]
      else: issues.append('UNNARRATED_STATE_CAUSE')
      states[pair]=loc
    else:
     issues.append('TEMPORAL_LINK_UNRESOLVED')
   events.append({'model':model,'record':rec,'locus':loc,'word':w,'kind':kind,'narrative_position':len(alignment)+1,'event_index':clock,'patient':active or 'MISSING','destination':vessel or 'MISSING' if kind!='HEAT' else 'NA','prior_completed_event':prior,'state_used_by_heat':used,'cause_or_start':cause,'repeated_state_assertion':int(repeatstate),'issues':';'.join(issues) or 'NONE','reading':gloss})
  after=json.dumps({'patient':active,'vessel':vessel,'running':ongoing,'completed':completed,'states':states},ensure_ascii=False,sort_keys=True)
  alignment.append({'record':rec,'locus':loc,'word':w,'kind':kind,'reading':gloss,'event_index':clock,'before':before,'after':after})
 assert [x['word'] for x in alignment]==[w for r,i,w in words]
 tsv('ALIGNMENT_'+model+'.tsv',alignment)
 lines=['# P15 '+model+' — vollständige hypothetische Lesung','', 'Eckige Klammern bewahren ungelöste Ganzformen; Satzbau und Zeitgliederung sind Annahmen. Keine bestätigte Übersetzung.','']
 for r in source:
  part=[x for x in alignment if x['locus'].rsplit(':',1)[0]==r['locus']]
  lines+=['## '+r['record_id']+' / '+r['locus'],'','Quelle: `'+r['zl3b_line']+'`','','Lesung: '+' · '.join(x['reading'] for x in part),'']
 (D/('READING_'+model+'.md')).write_text('\n'.join(lines).rstrip()+'\n')
 counts=Counter(z for x in events for z in x['issues'].split(';') if z!='NONE')
 summaries.append({'model':model,'temporal_or_action_positions':len(events),'issues':dict(counts),'heat_uses_prior_filled_state':sum(x['state_used_by_heat']!='NA' for x in events),'repeated_state_assertions':sum(x['repeated_state_assertion'] for x in events),'repeat_with_prior_completed_event':sum(x['kind']=='REPEAT' and x['prior_completed_event']!='NA' for x in events)})
 all_events+=events
 for rec in dict.fromkeys(r['record_id'] for r in source):
  a=[x for x in alignment if x['record']==rec];ev=[x for x in events if x['record']==rec]
  coverage.append({'model':model,'record':rec,'groups':len(a),'hypothesis_positions':sum(x['kind']!='OPEN' for x in a),'open_positions':sum(x['kind']=='OPEN' for x in a),'event_positions':len(ev),'heat_uses_state':sum(x['state_used_by_heat']!='NA' for x in ev),'repeat_supported':sum(x['kind']=='REPEAT' and x['prior_completed_event']!='NA' for x in ev)})
tsv('EVENTS.tsv',all_events);tsv('RECORD_COVERAGE.tsv',coverage)
counts=Counter(w for r,i,w in words if w in lex)
result={'status':'EXPLORATORY_PARTIAL_ASPECT_READING','groups':341,'whole_word_assumptions':len(lex),'hypothesis_positions':sum(counts.values()),'open_positions':341-sum(counts.values()),'word_counts':dict(counts),'models':summaries,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_pages_opened':0}
js(D/'RESULT.json',result);js(D/'VALIDATION.json',{'status':'PASS_SOURCE_CONSERVATION_AND_EXECUTION_ONLY','source_sha256':sha(S),'all_groups_each_model':341,'models':2,'meaning_validated':False})
print(json.dumps(result,indent=2))
