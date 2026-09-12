"""S03 shared versus exclusive postposed patient, frozen P12 lexicon."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4];P=H.parent/'P12'
def js(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rows):
 with (H/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
model=json.loads((P/'MODEL.json').read_text());nouns={w:x['meaning'] for w,x in model['names'].items()};mats={w for w,x in model['names'].items() if x['type']=='MATERIAL'};verbs=model['actions'];known=set(nouns)|set(verbs)
js('MODEL.json',{'lexicon_source':'P12/MODEL.json','variants':{'L':'last previous material','S':'all predicates since previous material share next material','X':'only last such predicate takes next material'},'destination':'last previous qokaiin in record; fixed for all','unknowns':'retained, no free skips or meanings','meaning_status':'hypothetical'})
js('SOURCE.json',{'files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [P/'PROSE.tsv',P/'MODEL.json',H/'DECISION.md',H/'MODEL.json']],'sealed':['f84','f84r'],'exposure':'all scope and motivating examples previously exposed'})
lines=list(csv.DictReader((P/'PROSE.tsv').open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 for n,w in enumerate(line['zl3b_line'].split(),1):raw.append({'record':line['record_id'],'locus':line['locus'],'at':line['locus']+':'+str(n),'word':w})
assert len(raw)==341 and len(lines)==51
pos=lambda i:raw[i]['at'] if i is not None else 'NONE'
tab('INPUT.tsv',[dict(x,row_status='recorded') for x in raw])
groups=[];byidx={}
for record in dict.fromkeys(x['record'] for x in raw):
 indices=[i for i,x in enumerate(raw) if x['record']==record];pending=[];group_number=0
 def add(indices,target):
  global group_number
  group_number+=1;gid=record+'_G'+str(group_number);actions=[i for i in indices if raw[i]['word'] in verbs]
  groups.append({'group':gid,'record':record,'start':pos(indices[0]),'end':pos(indices[-1]),'target':pos(target),'target_word':raw[target]['word'] if target is not None else 'NONE','actions':','.join(pos(i) for i in actions) or 'NONE','action_words':','.join(raw[i]['word'] for i in actions) or 'NONE','action_count':len(actions),'distinct_actions':len({raw[i]['word'] for i in actions}),'groups':len(indices),'open_groups':sum(raw[i]['word'] not in known for i in indices),'raw':' '.join(raw[i]['word'] for i in indices),'row_status':'recorded'})
  for i in indices:byidx[i]=(gid,target,actions)
 for i in indices:
  pending.append(i)
  if raw[i]['word'] in mats:add(pending,i);pending=[]
 if pending:add(pending,None)
tab('ALL_GROUPS.tsv',groups)
all_events={};summary={}
for version in ['L','S','X']:
 events=[];align=[]
 for i,x in enumerate(raw):
  word=x['word'];render=nouns.get(word,'['+word+' — offen]')
  if word in verbs:
   gid,right,actions=byidx[i];before=[j for j in range(i) if raw[j]['record']==x['record']]
   left=next((j for j in reversed(before) if raw[j]['word'] in mats),None)
   vessel=next((j for j in reversed(before) if raw[j]['word']=='qokaiin'),None) if word=='qokeedy' else None
   if version=='L':patient=left;reason='BOUND' if patient is not None else 'NO_LEFT_MATERIAL'
   elif right is None:patient=None;reason='NO_RIGHT_MATERIAL'
   elif version=='X' and actions[-1]!=i:patient=None;reason='SUPERSEDED_UNBOUND'
   else:patient=right;reason='BOUND'
   missing=[]
   if patient is None:missing.append('MATERIAL')
   if word=='qokeedy' and vessel is None:missing.append('VESSEL')
   status='MISSING_'+'_AND_'.join(missing) if missing else 'COMPLETE'
   span=range(min(i,patient)+1,max(i,patient)) if patient is not None else []
   events.append(dict(x,version=version,group=gid,patient=pos(patient),patient_word=raw[patient]['word'] if patient is not None else 'NONE',destination=pos(vessel),binding=reason,status=status,intervening_groups=abs(patient-i)-1 if patient is not None else 'NA',intervening_open=sum(raw[j]['word'] not in known for j in span) if patient is not None else 'NA',row_status='recorded'))
   render=verbs[word]+' '+(nouns[raw[patient]['word']]+'@'+pos(patient) if patient is not None else '?Material')+(' in Gefäß@'+pos(vessel) if word=='qokeedy' else '')+'; '+status
  align.append(dict(x,version=version,render=render,read_status='HYPOTHESIS' if word in known else 'OPEN',row_status='recorded'))
 tab('ACTIONS_'+version+'.tsv',events);tab('ALIGNMENT_'+version+'.tsv',align);all_events[version]=events
 text=['# S03 '+version+' — unveränderte P12-Worthypothesen','']
 for line in lines:text+=['**'+line['record_id']+' / '+line['locus']+'**','', ' · '.join(x['word']+' → '+x['render'] for x in align if x['locus']==line['locus']),'']
 (H/('READING_'+version+'.md')).write_text('\n'.join(text).rstrip()+'\n')
 summary[version]={'action_statuses':dict(Counter(x['status'] for x in events)),'patient_bindings':dict(Counter(x['binding'] for x in events)),'hypothetical_positions':sum(x['read_status']=='HYPOTHESIS' for x in align),'open_positions':sum(x['read_status']=='OPEN' for x in align)}
comparison=[]
for l,s,x in zip(all_events['L'],all_events['S'],all_events['X']):
 comparison.append({'at':l['at'],'word':l['word'],'L_patient':l['patient'],'S_patient':s['patient'],'X_patient':x['patient'],'L_type':l['patient_word'],'S_type':s['patient_word'],'L_status':l['status'],'S_status':s['status'],'X_status':x['status'],'destination':l['destination'],'row_status':'recorded'})
tab('ALL_COMPARISONS.tsv',comparison)
clusters=[]
for g in groups:
 if g['action_count']>=2:
  acts=[x for x in all_events['S'] if x['group']==g['group']]
  clusters.append(dict(g,all_roles_complete=all(x['status']=='COMPLETE' for x in acts),S_reading='; '.join(verbs[x['word']]+' '+nouns.get(x['patient_word'],'?Material') for x in acts)))
tab('MULTI_PREDICATE_GROUPS.tsv',clusters)
result={'status':'PARTIAL_POSTPOSED_SHARED_PATIENT_READING_NO_SYNTAX_IDENTIFICATION','groups_per_reading':341,'actions_per_reading':20,'variants':summary,'groups':len(groups),'multiple_predicate_groups':len(clusters),'closed_mixed_action_groups':sum(g['target']!='NONE' and g['distinct_actions']==2 for g in clusters),'complete_mixed_action_groups':sum(g['target']!='NONE' and g['distinct_actions']==2 and g['all_roles_complete'] for g in clusters),'L_to_S_type_changes_when_both_bound':sum(c['L_type']!='NONE' and c['S_type']!='NONE' and c['L_type']!=c['S_type'] for c in comparison),'L_to_S_newly_complete':sum(c['L_status']!='COMPLETE' and c['S_status']=='COMPLETE' for c in comparison),'L_to_S_lost_complete':sum(c['L_status']=='COMPLETE' and c['S_status']!='COMPLETE' for c in comparison),'confirmed_meanings':0,'independent_confirmation_capacity':0}
js('RESULT.json',result);print(json.dumps(result))
