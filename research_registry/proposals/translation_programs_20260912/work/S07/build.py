from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,keys,rows):
 with (D/n).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(keys+['row_status']);w.writerows([list(r)+['recorded'] for r in rows])
r=read(W/'S05/INPUT.tsv');lex={x['form']:x['meaning_hypothesis'] for x in read(W/'P05/LEXICON_v03.tsv')};mat=set(json.loads((W/'P05/REFERENCE_RULE_v02.json').read_text())['material_forms'])
actions=set('cphos she shckhy otchy qotchy skey cpho chy chetchy shytchy chey shey shot'.split())
tab('ALIGNMENT.tsv',['record','locus','at','word','gloss','status'],[(x['record'],x['locus'],x['at'],x['word'],lex.get(x['word'],'OPEN'),'HYPOTHESIS' if x['word'] in lex else 'OPEN') for x in r])
cases=[]
for rec in dict.fromkeys(x['record'] for x in r):
 rr=[x for x in r if x['record']==rec]
 for i,x in enumerate(rr):
  kind=None;end=i;targets=[]
  if i+1<len(rr) and x['word'] in {'chol','daiin'} and rr[i+1]['word']==x['word']:
   kind='DOSE_XX' if x['word']=='daiin' else 'STATE_XX';end=i+1
   for z in reversed(rr[:i]):
    if z['word'] in mat and z['word'] not in [a['word'] for a in targets]:targets.append(z)
    if len(targets)==2:break
   targets.reverse()
  elif i+3<len(rr) and x['word'] in mat and rr[i+1]['word']=='daiin' and rr[i+2]['word'] in mat and rr[i+3]['word']=='daiin':
   kind='DOSE_NQ_NQ';end=i+3;targets=[x,rr[i+2]]
  if kind:
   prev=next((a for a in reversed(rr[:i]) if a['word'] in actions),None)
   later=[a['at'] for a in rr[end+1:] if a['word'] in [t['word'] for t in targets]]
   cases.append({'id':'C'+str(len(cases)+1),'record':rec,'kind':kind,'start':x['at'],'end':rr[end]['at'],'text':' '.join(a['word'] for a in rr[i:end+1]),'targets':targets,'previous_action':prev,'later_same_forms':later})
js('CASES.json',cases)
tab('CENSUS.tsv',['id','record','kind','start','end','text','target1','target2','previous_action','later_same_forms'],[(c['id'],c['record'],c['kind'],c['start'],c['end'],c['text'],c['targets'][0]['at'],c['targets'][1]['at'],c['previous_action']['at'] if c['previous_action'] else 'NONE',','.join(c['later_same_forms']) or 'NONE') for c in cases])
dose=[c for c in cases if c['kind'].startswith('DOSE')]
oblig=[]
for c in dose:
 a=c['previous_action'];assert a['word'] in {'shckhy','skey'}
 for mode in ['I','O','A']:
  if a['word']=='shckhy':
   result={'I':('zwei vorhandene Eingaben vermischen','ein gemeinsames Mischprodukt nur impliziert; spätere Identität offen'), 'O':('zwei verschiedene dosierte Ausgaben der Mischung','Aufteilung oder zwei getrennte Ansätze nicht durch vermische bezeichnet'), 'A':('genau einen der beiden Stoffe zum Vermischen wählen','Auswahlkriterium und weiterer Mischpartner fehlen')}[mode]
  else:
   result={'I':('beide vorhandenen Portionen zurückhalten','Herkunft offen; Zurückhalten erzeugt die Stoffe nicht'), 'O':('zwei erzeugte Ausgaben an Zurückhalten binden','Herstellung/Trennung fehlt im Verb; qotchy als vorgeschaltete Herkunft wäre Zusatzbindung'), 'A':('genau eine der beiden Portionen zurückhalten','Auswahlkriterium und Schicksal der anderen Portion fehlen')}[mode]
  oblig.append((c['id'],mode,a['at'],a['word'],result[0],result[1],'NONE','HYPOTHESIS_NOT_SELECTED'))
tab('ROLE_CONSEQUENCES.tsv',['case','mode','action_at','action_word','reading','missing_or_added','later_same_target_form','decision'],oblig)
for mode in ['I','O','A']:
 out=[f'# S07 {mode} — vollständige exponierte Wortlesung','','Unbestätigte P05-Werte. ⟦OPEN: Wort⟧ bleibt offen. Jede Zeile wird vollständig wiedergegeben; zusätzliche Rollenprosa folgt nur an den beiden dosierten Paaren. Keine neue Übersetzung durch den Renderer.','']
 for locus in dict.fromkeys(x['locus'] for x in r):
  rr=[x for x in r if x['locus']==locus];out += ['## '+locus,'','`'+' '.join(x['word'] for x in rr)+'`','',' · '.join(lex.get(x['word'],'⟦OPEN: '+x['word']+'⟧') for x in rr),'']
  for c in cases:
   if c['end'].rsplit(':',1)[0]!=locus:continue
   names=' / '.join(lex[t['word']] for t in c['targets'])
   if c['kind']=='STATE_XX':out+=['Gemeinsame Zustandslesung: trocken für '+names+'. Kein Dosisvergleich.','']
   else:
    o=next(o for o in oblig if o[0]==c['id'] and o[1]==mode)
    out += ['Zusätzliche Rollenlesung: '+names+', je Q. '+o[4]+'. Offen: '+o[5]+'.','']
 (D/f'READING_{mode}.md').write_text('\n'.join(out).rstrip()+'\n')
js('RESULT.json',{'groups':len(r),'hypothesis_occurrences':sum(x['word'] in lex for x in r),'open_occurrences':sum(x['word'] not in lex for x in r),'immediate_dose_doubles':sum(c['kind']=='DOSE_XX' for c in cases),'separate_NQ_NQ':sum(c['kind']=='DOSE_NQ_NQ' for c in cases),'state_doubles':sum(c['kind']=='STATE_XX' for c in cases),'dose_physical_folios':sorted({c['record'].rstrip('rv') for c in dose}),'role_consequences':len(oblig),'later_exact_target_rementions':sum(len(c['later_same_forms']) for c in dose),'decision':'I is a concrete working formulation with preexisting portions; O and A require unbound extra relations; no empirical selection','meanings_confirmed':0,'independent_confirmation_capacity':0,'held_access':False})
files=['S05/INPUT.tsv','P05/LEXICON_v03.tsv','P05/REFERENCE_RULE_v02.json','P05/REPORT.md','P04/MODEL.json','P25/REPORT.md','S06/REPORT.md','S07/DECISION.md']
js('SOURCE.json',{'files':[{'path':str((W/p).relative_to(R)),'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()} for p in files],'exposure':'all145groups and earlier models already seen; not blind','sealed':['f84','f84r'],'no_new_pages':True})
print((D/'RESULT.json').read_text())
