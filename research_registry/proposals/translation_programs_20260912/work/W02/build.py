"""Render fixed authored hypotheses and expose all argument debts. No fitting/search."""
import csv,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent
S=json.loads((E/'SOURCE.json').read_text())
D={r['form']:r for r in csv.DictReader((E/'LEXICON.tsv').open(),delimiter='\t')}
ACTIONS={'ACTION','MIX','REPEAT_ACTION','REPEAT_COOL','ACTION_TYPED'}
def dump(name,data):(E/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def tsv(name,rows,cols):
 with (E/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)
def gloss(w,model='A'):
 if w=='ychor' and model=='B':return 'nimm'
 return D[w]['hypothesis'] if w in D else '[ungelesen: '+w+']'
allalign=[];bindings=[];counts=[];frames=[];repeats=[];read={m:['# '+('A: additive Herstellungsfassung' if m=='A' else 'B: Befehlsgegenfassung'),'','Alle Bedeutungen sind ausdrücklich erfundene Arbeitshypothesen. Originalgruppen bleiben vollständig erhalten. Punkte und Semikola sind Darstellungszeichen, keine identifizierte Syntax. Q/P/R bleiben unbekannte Größen, keine gelesenen Zahlen.',''] for m in ['A','B']}
for target in S['targets']:
 p=target['hosts']['ZL3b'][0];flat=[]
 for l in p['lines']:
  for i,w in enumerate(l['words'],1):
   flat.append({'id':l['locus']+':'+str(i),'locus':l['locus'],'index':i,'form':w,'role':D.get(w,{}).get('role','OPEN'),'offset':len(flat)})
 materials=[x for x in flat if x['role'] in {'MATERIAL','MATERIAL_DOSE'}];assigned=sum(x['form'] in D for x in flat)
 counts.append({'target':target['target'],'paragraph':p['id'],'lines':len(p['lines']),'groups':len(flat),'hypothetical':assigned,'unread':len(flat)-assigned,'IT_host':target['hosts']['IT2a'][0]['id'] if target['hosts']['IT2a'] else 'UNAVAILABLE'})
 for x in flat:
  allalign.append({'paragraph':p['id'],'locus':x['locus'],'group_index':x['index'],'raw':x['form'],'A':gloss(x['form']),'B':gloss(x['form'],'B'),'role_A':x['role'],'status':'ASSUMED' if x['form'] in D else 'UNREAD'})
 for m in read:
  read[m]+=['## '+p['id'],'','Fester Zielort: '+target['target']+'. Alle Zeilen des ZL-Absatzes:','']
  for l in p['lines']:read[m]+=[l['locus']+': `'+ ' '.join(l['words'])+'`','', ' · '.join(gloss(w,m) for w in l['words']), '']
 # Every material mention and its earlier exact-form mentions; identity remains a separate hypothesis.
 for mat in materials:
  old=[x for x in materials if x['offset']<mat['offset'] and x['form']==mat['form']]
  repeats.append({'paragraph':p['id'],'mention':mat['id'],'form':mat['form'],'meaning':D[mat['form']]['hypothesis'],'earlier_exact_mentions':';'.join(x['id'] for x in old),'identity':'SAME_FORM_NOT_PROVEN_SAME_MATERIAL_INSTANCE'})
 def bind(x,model):
  # Local precedence: nearest explicit material on left; else first material on right before next action.
  left=[v for v in materials if v['locus']==x['locus'] and v['offset']<x['offset']]
  next_actions=[v['offset'] for v in flat if v['offset']>x['offset'] and v['locus']==x['locus'] and v['role'] in ACTIONS]
  bound=min(next_actions,default=10**9)
  right=[v for v in materials if v['locus']==x['locus'] and x['offset']<v['offset']<bound]
  if left:patient=left[-1];rule='LOCAL_LEFT'
  elif right:patient=right[0];rule='LOCAL_RIGHT'
  else:
   old=[v for v in materials if v['offset']<x['offset']]
   patient=old[-1] if old else None;rule='PARAGRAPH_CARRY' if old else 'MISSING'
  debt=[];px='';pf='';extra=''
  if patient:
   px=patient['id'];pf=patient['form'];lo,hi=sorted([x['offset'],patient['offset']]);unknown=[v['id'] for v in flat if lo<v['offset']<hi and v['role']=='OPEN']
   if unknown:debt.append('UNREAD_BETWEEN:'+','.join(unknown))
   if rule=='PARAGRAPH_CARRY':debt.append('IMPLICIT_SUBJECT_CONTINUATION')
  else:debt.append('MISSING_PATIENT')
  if x['role']=='MIX':
   candidates=[v for v in left+right if not patient or v['id']!=patient['id']]
   if candidates:extra=candidates[-1]['id']
   else:debt.append('MISSING_COINGREDIENT')
  if x['role']=='ACTION_TYPED' and pf not in {'cheor','okeeor','okeor','keeor','cheeor','sheeor'}:debt.append('EXTRACT_PATIENT_NOT_BOUND')
  if x['form']=='qotchy' and pf not in {'sho','sheol','cheor','cheo','okeol','cheol','sheo','qotol','okeor','qokol','okol'}:debt.append('LIQUID_INPUT_NOT_BOUND')
  return {'model':model,'paragraph':p['id'],'operation':x['id'],'form':x['form'],'meaning':gloss(x['form'],model),'patient':px,'patient_form':pf,'rule':rule,'coingredient':extra,'debts':';'.join(debt)}
 for model in ['A','B']:
  for x in flat:
   if x['role'] in ACTIONS or (model=='B' and x['form']=='ychor'):bindings.append(bind(x,model))
 tline=next(l for l in p['lines'] if l['locus']==target['target']);tx=next(x for x in flat if x['locus']==target['target'] and x['form']=='ychor')
 before_ops=[x['id'] for x in flat if x['offset']<tx['offset'] and x['role'] in ACTIONS]
 after_ops=[x['id'] for x in flat if x['offset']>tx['offset'] and x['role'] in ACTIONS]
 near=next(b for b in bindings if b['model']=='B' and b['operation']==tx['id'])
 frames.append({'target':target['target'],'paragraph':p['id'],'W01_matches_raw':' '.join(tline['words'])==target['W01_line'],'earlier_assumed_actions':';'.join(before_ops),'later_assumed_actions':';'.join(after_ops),'B_take_patient':near['patient'],'B_take_patient_form':near['patient_form'],'B_debts':near['debts'],'A_additive_anchor':'earlier instruction inventory; meaningful common aim remains assumed'})
for m,lines in read.items():(E/('READING_'+m+'.md')).write_text('\n'.join(lines))
tsv('ALIGNMENT.tsv',allalign,list(allalign[0]));tsv('ARGUMENTS.tsv',bindings,list(bindings[0]));tsv('MATERIAL_MENTIONS.tsv',repeats,list(repeats[0]));tsv('PARAGRAPH_TABLE.tsv',counts,list(counts[0]));tsv('FRAME_COMPARISON.tsv',frames,list(frames[0]))
result={'status':'EXPOSED_AUTHORED_PARAGRAPH_READING','paragraphs':len(counts),'lines':sum(x['lines'] for x in counts),'groups':len(allalign),'dictionary_assumptions':len(D),'hypothetically_assigned':sum(x['status']=='ASSUMED' for x in allalign),'unread':sum(x['status']=='UNREAD' for x in allalign),'first_paragraph':counts[0],'hypothetical_operations':dict(collections.Counter(x['model'] for x in bindings)),'operations_with_debts':dict(collections.Counter(x['model'] for x in bindings if x['debts'])),'same_form_rementions':sum(bool(x['earlier_exact_mentions']) for x in repeats),'W01_target_raw_differences':[x['target'] for x in frames if not x['W01_matches_raw']],'meaning_identifications':0,'held_access':False,'significance_claim':False,'independent_confirmation_capacity':0}
dump('RESULT.json',result);print(json.dumps(result))
