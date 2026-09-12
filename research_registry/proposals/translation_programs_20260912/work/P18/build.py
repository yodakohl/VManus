#!/usr/bin/env python3
"""Finite authored sentence-boundary comparison; no learned decoder."""
from pathlib import Path
import json,csv,hashlib
from collections import defaultdict
D=Path('research_registry/proposals/translation_programs_20260912/work/P18');P=D.parent/'P11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def tab(n,rs):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
source=json.loads((P/'INPUT.json').read_text());model=json.loads((P/'MODEL.json').read_text());pred=model['predicates'];materials=model['materials'];locations=model['locations'];lex=materials|locations|model['other']|{w:v['D0'] for w,v in pred.items()}
records=defaultdict(list)
for r in source['lines']:
 for i,w in enumerate(r['groups'],1):records[r['locus'].split('.')[0]].append({'locus':r['locus']+':'+str(i),'line':r['locus'],'word':w})
assert sum(map(len,records.values()))==145
js('SOURCE.json',{'input':str(P/'INPUT.json'),'input_sha256':sha(P/'INPUT.json'),'fixed_model':str(P/'MODEL.json'),'fixed_model_sha256':sha(P/'MODEL.json'),'decision_sha256':sha(D/'DECISION.md'),'held_pages_opened':0})
allevents=[];allunits=[];allcuts=[];allopposites=[];summary=[];alignments={}
for rule in ['L','R','V']:
 partitions={}
 for rec,words in records.items():
  starts={0:'PARAGRAPH_START'}
  if rule=='L':
   for j,w in enumerate(words):
    if j and w['line']!=words[j-1]['line']:starts[j]='LINE_START'
  elif rule=='R':
   seen=set();line=None
   for j,w in enumerate(words):
    if w['line']!=line:seen=set();line=w['line']
    if w['word'] in seen:starts[j]='REPEATED_WHOLE_FORM_IN_LINE'
    seen.add(w['word'])
  else:
   for j,w in enumerate(words):
    if w['word'] not in pred:continue
    k=j+1;kind=pred[w['word']]['right']
    if kind and k<len(words) and words[k]['word'] in (materials if kind=='MATERIAL' else locations):k+=1
    if k<len(words):starts[k]='AFTER_AUTHORED_PREDICATE_AND_COMPLEMENT'
  keys=sorted(starts);ids={}
  for n,start in enumerate(keys,1):
   end=keys[n] if n<len(keys) else len(words);unit=rec+':'+rule+str(n)
   for j in range(start,end):ids[j]=unit
   allcuts.append({'rule':rule,'record':rec,'unit':unit,'start':words[start]['locus'],'reason':starts[start]})
  partitions[rec]=ids
 for mode in ['LOCAL','CARRY']:
  tag=rule+'_'+mode;alignment=[];events=[];opposites=[]
  for rec,words in records.items():
   ids=partitions[rec];topic=None;unit=None;claimed=set();states={}
   for j,w in enumerate(words):
    u=ids[j]
    if u!=unit:
     unit=u
     if mode=='LOCAL':topic=None
    word=w['word'];loc=w['locus'];reading=lex.get(word,'['+word+']');status='HYPOTHESIS' if word in lex else 'OPEN'
    if word in materials and j not in claimed:topic=loc
    if word in pred:
     right=pred[word]['right'];target='NA';issues=[];severed='NA'
     if topic is None:issues.append('MISSING_BEARER')
     if right:
      if j+1<len(words) and words[j+1]['word'] in (materials if right=='MATERIAL' else locations):
       if ids[j+1]==u:target=words[j+1]['locus'];claimed.add(j+1)
       else:issues.append('SEVERED_RIGHT_COMPLEMENT');severed=words[j+1]['locus']
      else:issues.append('NO_TYPED_IMMEDIATE_COMPLEMENT')
     reading=(lex[words[next(k for k,x in enumerate(words) if x['locus']==topic)]['word']] if topic else '?Gegenstand')+' '+pred[word]['D0']
     if right:reading+=' '+(lex[words[j+1]['word']] if target!='NA' else '?Ergänzung')
     events.append({'rule':rule,'mode':mode,'record':rec,'unit':u,'locus':loc,'word':word,'bearer':topic or 'MISSING','right_complement':target,'severed_candidate':severed,'issues':';'.join(issues) or 'NONE','reading':reading})
     if topic and word in ['chol','shol']:
      if topic in states and states[topic][0]!=word:
       old,oldloc,oldunit=states[topic];opposites.append({'rule':rule,'mode':mode,'record':rec,'bearer':topic,'earlier':oldloc,'later':loc,'scope':'WITHIN_UNIT' if oldunit==u else 'ACROSS_UNITS_UNDATED'})
      states[topic]=(word,loc,u)
    alignment.append({'record':rec,'unit':u,'locus':loc,'word':word,'reading':reading,'status':status,'claimed_complement':int(j in claimed)})
  assert len(alignment)==145
  alignments[tag]=alignment;tab('ALIGNMENT_'+tag+'.tsv',alignment)
  out=['# P18 '+tag+' — vollständige hypothetische Lesung','','Satzzeichen markieren die versuchte Gliederung. Keine gelesenen Autorengrenzen. Alle Klammerwörter bleiben offen.']
  for u in dict.fromkeys(x['unit'] for x in alignment):
   a=[x for x in alignment if x['unit']==u];ev=[x for x in events if x['unit']==u]
   allunits.append({'rule':rule,'mode':mode,'unit':u,'record':a[0]['record'],'first':a[0]['locus'],'last':a[-1]['locus'],'groups':len(a),'predicates':len(ev),'open_groups':sum(x['status']=='OPEN' for x in a),'missing_bearers':sum(x['bearer']=='MISSING' for x in ev)})
   out+=['','## '+u+' / '+a[0]['locus']+'–'+a[-1]['locus'],'','Quelle: '+' '.join(x['word'] for x in a),'','Lesung: '+' · '.join(x['reading'] for x in a)+'.']
  (D/('READING_'+tag+'.md')).write_text('\n'.join(out)+'\n')
  units=[x for x in allunits if x['rule']==rule and x['mode']==mode]
  summary.append({'rule':rule,'mode':mode,'units':len(units),'units_without_predicate':sum(x['predicates']==0 for x in units),'missing_bearers':sum(x['bearer']=='MISSING' for x in events),'severed_right_complements':sum(x['severed_candidate']!='NA' for x in events),'bound_right_complements':sum(x['right_complement']!='NA' for x in events),'within_unit_opposites':sum(x['scope']=='WITHIN_UNIT' for x in opposites),'across_unit_opposites':sum(x['scope']=='ACROSS_UNITS_UNDATED' for x in opposites)})
  allevents+=events;allopposites+=opposites
for name,rs in [('EVENTS.tsv',allevents),('UNITS.tsv',allunits),('BOUNDARIES.tsv',allcuts),('OPPOSITES.tsv',allopposites)]:tab(name,rs)
comparison=[]
for rec,words in records.items():
 for w in words:
  if w['word'] not in pred:continue
  row={'record':rec,'locus':w['locus'],'word':w['word']}
  for rule in ['L','R','V']:
   for mode in ['LOCAL','CARRY']:
    e=next(x for x in allevents if x['rule']==rule and x['mode']==mode and x['locus']==w['locus']);row[rule+'_'+mode]=e['bearer']+' / '+e['right_complement']
  comparison.append(row)
tab('ALL_PREDICATE_COMPARISONS.tsv',comparison)
result={'status':'PARTIAL_BOUNDARY_REFERENCE_COMPARISON','groups_each':145,'whole_word_values_unchanged_from_P11':True,'hypothesis_positions':sum(x['status']=='HYPOTHESIS' for x in alignments['L_LOCAL']),'open_positions':sum(x['status']=='OPEN' for x in alignments['L_LOCAL']),'predicates_each':20,'summaries':summary,'confirmed_sentence_boundaries':0,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_pages_opened':0};js('RESULT.json',result);print(json.dumps(result,indent=2))
