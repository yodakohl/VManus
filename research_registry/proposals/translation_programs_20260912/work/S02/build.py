"""S02 finite component inventory; no decoded quantities or new manuscript data."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
S=R/'research_registry/proposals/translation_programs_20260912/work/P12/PROSE.tsv'
def js(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rows):
 with (H/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
lex={'shedy':'Flüssigkeit A','lchedy':'Zusatzstoff C','qokaiin':'Gefäß','chedy':'erwärme','qokeedy':'fülle ein','qokedy':'entnimm gesamten Inhalt als reinen folgenden Stoff'}
mat={'shedy':'A','lchedy':'C'}
js('MODEL.json',{'lexicon':lex,'E_extra':{'qokeey':'entleere vollständig'},'variants':['D0','D?','R0','R?','E0','E?'],'type_identity':'A and C distinct hypotheses; no identified portions','failed_transition':'no inventory change; later states conditional','unknown_start':'known components plus unknown remainder'})
js('SOURCE.json',{'files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [S,H/'DECISION.md',H/'MODEL.json']],'sealed':['f84','f84r'],'exposure':'all workpack and selected examples previously exposed'})
lines=list(csv.DictReader(S.open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 for n,w in enumerate(line['zl3b_line'].split(),1):raw.append({'record':line['record_id'],'locus':line['locus'],'at':line['locus']+':'+str(n),'word':w})
assert len(raw)==341 and len(lines)==51
tab('INPUT.tsv',[dict(x,row_status='recorded') for x in raw])
def right(i):
 for j in range(i+1,len(raw)):
  if raw[j]['record']!=raw[i]['record'] or raw[j]['word'] in {'qokeedy','qokedy','qokeey'}:return None
  if raw[j]['word'] in mat:return j
 return None
def state(v):return json.dumps({'components':sorted(v['components']),'unknown':v['unknown']},sort_keys=True,separators=(',',':')) if v else 'NO_VESSEL'
summary={};comparison=[]
for mode in ['D','R','E']:
 for initial in ['0','?']:
  name=mode+initial;tag=mode+('0' if initial=='0' else 'U');vessels={};active=None;patient=None;record=None;events=[];align=[];first_problem='NONE';first_conflict='NONE'
  for i,x in enumerate(raw):
   w=x['word'];before=state(vessels.get(active));render=lex.get(w,'['+w+' — offen]');status='HYPOTHESIS' if w in lex else 'OPEN';detail='NONE'
   if x['record']!=record:
    record=x['record'];patient=None
    if mode=='R':active=None
    before=state(vessels.get(active))
   if w in mat:patient=i
   elif w=='qokaiin':
    active=record if mode=='R' else 'SHARED'
    if active not in vessels:vessels[active]={'components':set(),'unknown':initial=='?'}
    render='Gefäß@'+active
   elif w in {'chedy','qokeedy','qokedy','qokeey'}:
    op={'chedy':'HEAT','qokeedy':'FILL','qokedy':'WITHDRAW','qokeey':'EMPTY' if mode=='E' else 'OPEN'}[w]
    target=right(i) if op=='WITHDRAW' else patient if op in {'HEAT','FILL'} else None
    component=mat[raw[target]['word']] if target is not None else 'NONE';v=vessels.get(active);prior_problem=first_problem
    if op=='OPEN':outcome='OPEN'
    else:
     missing=[]
     if op in {'HEAT','FILL','WITHDRAW'} and target is None:missing.append('MATERIAL')
     if op in {'FILL','WITHDRAW','EMPTY'} and v is None:missing.append('VESSEL')
     if missing:outcome='MISSING_'+'_AND_'.join(missing)
     elif op=='HEAT':outcome='BOUND_NO_COMPONENT_CHANGE'
     elif op=='FILL':v['components'].add(component);outcome='COMPLETE'
     elif op=='EMPTY':v['components'].clear();v['unknown']=False;outcome='COMPLETE'
     elif v['components']-{component}:outcome='CONFLICT_OTHER_COMPONENT';detail=','.join(sorted(v['components']-{component}))
     elif v['unknown']:outcome='UNRESOLVED_INITIAL_CONTENT'
     elif not v['components']:outcome='CONFLICT_EMPTY'
     else:v['components'].clear();outcome='COMPLETE'
    if outcome.startswith(('MISSING','CONFLICT','UNRESOLVED')) and first_problem=='NONE':first_problem=x['at']
    if outcome.startswith('CONFLICT') and first_conflict=='NONE':first_conflict=x['at']
    after=state(v)
    events.append(dict(x,version=name,op=op,material_source=raw[target]['at'] if target is not None else 'NONE',component=component,vessel=active or 'NONE',before=before,after=after,status=outcome,foreign_components=detail,prior_problem=prior_problem,row_status='recorded'))
    if op!='OPEN':render=op+' '+component+' Material@'+(raw[target]['at'] if target is not None else '?')+' Gefäß@'+(active or '?')+'; '+outcome;status='HYPOTHESIS'
   align.append(dict(x,version=name,render=render,read_status=status,vessel=active or 'NONE',inventory=state(vessels.get(active)),row_status='recorded'))
  tab('EVENTS_'+tag+'.tsv',events);tab('ALIGNMENT_'+tag+'.tsv',align)
  tab('FINAL_VESSELS_'+tag+'.tsv',[{'vessel':key,'state':state(v),'row_status':'recorded'} for key,v in vessels.items()])
  out=['# S02 '+name+' — alle Gruppen; Wortwerte und Gefäßidentität hypothetisch','']
  for line in lines:out+=['**'+line['record_id']+' / '+line['locus']+'**','', ' · '.join(x['word']+' → '+x['render'] for x in align if x['locus']==line['locus']),'']
  (H/('READING_'+tag+'.md')).write_text('\n'.join(out).rstrip()+'\n')
  withdrawals=[e for e in events if e['op']=='WITHDRAW'];fills=[e for e in events if e['op']=='FILL']
  summary[name]={'hypothetical_positions':sum(x['read_status']=='HYPOTHESIS' for x in align),'open_positions':sum(x['read_status']=='OPEN' for x in align),'vessels':len(vessels),'fills':dict(Counter(e['status'] for e in fills)),'withdrawals':dict(Counter(e['status'] for e in withdrawals)),'first_problem':first_problem,'first_conflict':first_conflict,'final_vessels':{k:json.loads(state(v)) for k,v in vessels.items()}}
  comparison+=withdrawals
tab('ALL_WITHDRAWALS.tsv',comparison)
js('RESULT.json',{'status':'PARTIAL_VESSEL_INVENTORY_PURE_WITHDRAWAL_CONTRACT_CONFLICTS','groups_per_reading':341,'readings':6,'variants':summary,'confirmed_meanings':0,'independent_confirmation_capacity':0,'decision':'No fully evidenced reading; R? unresolved, later conflicts conditional on unapplied failed/unknown actions. No chosen translation'})
print(json.dumps(summary,ensure_ascii=False))
