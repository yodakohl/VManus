"""Fixed guarded repetition; complete exposed f83r, no novel decoder."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4];P=H.parent/'P12'
def js(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rows):
 with (H/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
lex={'shedy':'Flüssigkeit A','lchedy':'Zusatzstoff C','qokaiin':'Gefäß B','chedy':'erwärme','qokeedy':'fülle ein','qokeey':'laufendes Einfüllen','qokedy':'ist eingefüllt'}
js('MODEL.json',{'common_whole_hypotheses':lex,'qoteedy':{'N':'ein Einfülldurchgang','PRE':'prüfe Zielzustand vor Einfüllen','POST':'fülle einmal ein, dann prüfe Zielzustand'},'guard_source':'previous qokedy same local material/container pair','body':'qokeedy sets FILLED in one step','limit':'no written false guard, no multi-iteration test'})
js('SOURCE.json',{'files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [P/'PROSE.tsv',H/'DECISION.md',H/'MODEL.json']],'sealed':['f84','f84r'],'exposure':'all text and motivating repeat exposed in P15'})
lines=list(csv.DictReader((P/'PROSE.tsv').open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 for n,w in enumerate(line['zl3b_line'].split(),1):raw.append({'record':line['record_id'],'locus':line['locus'],'at':line['locus']+':'+str(n),'word':w})
assert len(raw)==341 and len(lines)==51
tab('INPUT.tsv',[dict(x,row_status='recorded') for x in raw])
all_events={};all_calls={};summaries={}
for mode in ['N','PRE','POST']:
 record=None;patient=None;destination=None;states={};causes={};guards={};events=[];align=[];calls=[]
 for x in raw:
  if x['record']!=record:record=x['record'];patient=None;destination=None;states={};causes={};guards={}
  w=x['word'];render=lex.get(w,'['+w+' — offen]');hyp=w in lex or w=='qoteedy'
  if w in {'shedy','lchedy'}:patient=(w,x['at'])
  elif w=='qokaiin':destination=x['at']
  else:
   pair=(patient[0], 'B') if patient and destination else None
   prior=states.get(pair,'UNKNOWN') if pair else 'UNBOUND_PAIR';cause=causes.get(pair,'NONE');guard=guards.get(pair,'NONE');body=0;status='NONE'
   if w in {'chedy','qokeedy','qokeey','qokedy','qoteedy'}:
    if w=='chedy':status='BOUND' if patient else 'MISSING_MATERIAL'
    elif pair is None:status='MISSING_PARTICIPANT'
    elif w=='qokeey':status='RUNNING_WITHOUT_COMPLETION'
    elif w=='qokedy':status='ASSERT_FILLED';states[pair]='FILLED';causes[pair]=x['at'];guards[pair]=x['at']
    elif w=='qokeedy':status='EXECUTE_FILL';states[pair]='FILLED';causes[pair]=x['at']
    elif mode!='N' and guard=='NONE':status='MISSING_WRITTEN_CONDITION'
    else:
     body=0 if mode=='PRE' and prior=='FILLED' else 1;status='SKIP_SATISFIED' if body==0 else 'EXECUTE_BODY'
     if body:states[pair]='FILLED';causes[pair]=x['at']
    row=dict(x,mode=mode,patient=patient[0] if patient else 'NONE',patient_source=patient[1] if patient else 'NONE',destination=destination or 'NONE',prior_state=prior,prior_cause=cause,written_condition=guard,body_executions=body,status=status,after_state=states.get(pair,'UNKNOWN') if pair else 'UNBOUND_PAIR',row_status='recorded')
    events.append(row)
    if w=='qoteedy':calls.append(row)
    render=(lex.get(w,{'N':'einmal einfüllen','PRE':'bis eingefüllt: vorher prüfen','POST':'einfüllen, dann Ziel prüfen'}[mode]))+' '+(patient[0] if patient else '?Material')+' / B@'+(destination or '?')+'; '+status+(' Körper='+str(body) if w=='qoteedy' else '')
  align.append(dict(x,mode=mode,render=render,read_status='HYPOTHESIS' if hyp else 'OPEN',row_status='recorded'))
 tab('EVENTS_'+mode+'.tsv',events);tab('CALLS_'+mode+'.tsv',calls);tab('ALIGNMENT_'+mode+'.tsv',align)
 text=['# S04 '+mode+' — alle Gruppen; Bedeutungen hypothetisch','']
 for line in lines:text+=['**'+line['record_id']+' / '+line['locus']+'**','', ' · '.join(x['word']+' → '+x['render'] for x in align if x['locus']==line['locus']),'']
 (H/('READING_'+mode+'.md')).write_text('\n'.join(text).rstrip()+'\n')
 summaries[mode]={'hypothetical_positions':sum(a['read_status']=='HYPOTHESIS' for a in align),'open_positions':sum(a['read_status']=='OPEN' for a in align),'call_statuses':dict(Counter(c['status'] for c in calls)),'additional_body_executions':sum(c['body_executions'] for c in calls),'explicit_fills_executed':sum(e['status']=='EXECUTE_FILL' for e in events)}
 all_events[mode]=events;all_calls[mode]=calls
comparisons=[]
for n,p,q in zip(all_calls['N'],all_calls['PRE'],all_calls['POST']):
 comparisons.append({'at':n['at'],'patient':p['patient'],'destination':p['destination'],'written_condition':p['written_condition'],'N_status':n['status'],'PRE_status':p['status'],'POST_status':q['status'],'N_executions':n['body_executions'],'PRE_executions':p['body_executions'],'POST_executions':q['body_executions'],'PRE_after':p['after_state'],'POST_after':q['after_state'],'row_status':'recorded'})
tab('ALL_CALL_COMPARISONS.tsv',comparisons)
observations=[]
for p,q in zip(all_events['PRE'],all_events['POST']):
 if p['word'] in {'qokedy','chedy'}:
  observations.append({'at':p['at'],'word':p['word'],'patient':p['patient'],'destination':p['destination'],'PRE_prior':p['prior_state'],'POST_prior':q['prior_state'],'PRE_cause':p['prior_cause'],'POST_cause':q['prior_cause'],'state_equal':p['prior_state']==q['prior_state'],'row_status':'recorded'})
tab('ALL_STATE_COMPARISONS.tsv',observations)
res={'status':'PARTIAL_GUARDED_REPEAT_ZERO_VS_ONE_SAME_OBSERVED_STATES','groups':341,'variants':summaries,'calls':5,'licensed_guard_calls':sum(c['written_condition']!='NONE' and c['destination']!='NONE' for c in all_calls['PRE']),'written_false_guards':0,'multi_iteration_capacity':0,'state_comparisons':len(observations),'different_PRE_POST_states':sum(not o['state_equal'] for o in observations),'confirmed_meanings':0,'independent_confirmation_capacity':0}
js('RESULT.json',res);print(json.dumps(res))
