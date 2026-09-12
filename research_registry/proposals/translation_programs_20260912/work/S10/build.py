from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def tab(n,k,rs):
 with (D/n).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(k+['row_status']);w.writerows([list(x)+['recorded'] for x in rs])
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=read(W/'S05/INPUT.tsv');lex={'chor':'Blütenmaterial','shor':'Samenmaterial','chol':'trocken','shol':'feucht','chkaiin':'annehmen','qody':'verwerfen'}
js('MODEL.json',{'lexicon':lex,'all_hypothetical':True,'claim':'first chor/shor per record','features':'later chor/shor per record same alleged ware','rule':'any unlike feature=>reject;else matching feature and latest dry=>accept;else unknown','exposure':'authored after all contexts known','list':'no claimed ware; nominal acceptance/rejection'})
roles=[];dec=[];recstats=[]
for rec in dict.fromkeys(x['record'] for x in s):
 claim=None;features=[];quality=None;rr=[x for x in s if x['record']==rec]
 for x in rr:
  w=x['word']
  if w in {'chor','shor'}:
   role='CLAIM' if claim is None else 'OBSERVED_CLASS'
   if claim is None:claim=x
   else:features.append(x)
   roles.append((rec,x['at'],w,role,claim['at']))
  if w in {'chol','shol'}:quality=x
  if w in {'chkaiin','qody'}:
   unlike=[f for f in features if claim and f['word']!=claim['word']];like=[f for f in features if claim and f['word']==claim['word']]
   expected='REJECT' if unlike else ('ACCEPT' if like and quality and quality['word']=='chol' else 'UNKNOWN')
   actual='ACCEPT' if w=='chkaiin' else 'REJECT';flipped='REJECT' if actual=='ACCEPT' else 'ACCEPT'
   verdict=lambda v:'UNBOUND' if expected=='UNKNOWN' else ('MODEL_MATCH' if v==expected else 'MODEL_CONTRADICTION')
   dec.append((rec,x['at'],w,claim['at'] if claim else 'NONE',claim['word'] if claim else 'NONE',','.join(f['at'] for f in features) or 'NONE',quality['at'] if quality else 'NONE',expected,actual,verdict(actual),flipped,verdict(flipped),'UNKNOWN_WITHOUT_CLAIM_ROLE'))
 recstats.append((rec,claim['at'] if claim else 'NONE',len(features),sum(x['word'] in {'chkaiin','qody'} for x in rr)))
tab('CLASS_ROLES.tsv',['record','at','word','role','claim_at'],roles)
tab('ALL_DECISIONS.tsv',['record','at','word','claim_at','claim_word','feature_loci','latest_quality','expected','assigned_decision','result','swapped_decision','swapped_result','list_role_ablation'],dec)
tab('ALL_RECORDS.tsv',['record','claim_at','feature_count','decision_count'],recstats)
for mode in ['T','L']:
 gloss=lex.copy()
 if mode=='L':gloss.update(chkaiin='Annahme',qody='Verwerfung')
 tab(f'ALIGNMENT_{mode}.tsv',['record','at','word','gloss','status'],[(x['record'],x['at'],x['word'],gloss.get(x['word'],'OPEN'),'HYPOTHESIS' if x['word'] in lex else 'OPEN') for x in s])
 out=[f'# S10 {mode} — vollständige exponierte Teil-Lesung','','Sechs frei angesetzte Karten; alle übrigen Wörter offen. Rollen und Schlussregel sind zusätzliche Hypothesen. Kein identifiziertes Handelsdokument und keine bestätigte Übersetzung.','']
 for locus in dict.fromkeys(x['locus'] for x in s):
  rr=[x for x in s if x['locus']==locus];out+=['## '+locus,'','`'+' '.join(x['word'] for x in rr)+'`','',' · '.join(gloss.get(x['word'],'⟦OPEN: '+x['word']+'⟧') for x in rr),'']
  for z in roles:
   if z[1].rsplit(':',1)[0]==locus:out += [z[1]+': '+(('behauptete Warenklasse' if z[3]=='CLAIM' else 'ermittelte Klasse derselben Ware') if mode=='T' else 'Stoffposten ohne Warenidentitätsvergleich')+'.','']
  for z in dec:
   if z[1].rsplit(':',1)[0]==locus:out += [z[1]+': '+(f'Regel erwartet {z[7]}; zugewiesenes Entscheidungswort {z[8]}; {z[9]}.' if mode=='T' else 'Verfahrensnomen ohne gebundenen Entscheidungsgrund.')+' Keine unabhängige Bestätigung.','']
 (D/f'READING_{mode}.md').write_text('\n'.join(out).rstrip()+'\n')
js('RESULT.json',{'groups':len(s),'hypothesis_occurrences':sum(x['word'] in lex for x in s),'class_occurrences':len(roles),'decisions':len(dec),'model_matches':sum(x[9]=='MODEL_MATCH' for x in dec),'model_contradictions':sum(x[9]=='MODEL_CONTRADICTION' for x in dec),'unbound':sum(x[9]=='UNBOUND' for x in dec),'swapped_contradictions':sum(x[11]=='MODEL_CONTRADICTION' for x in dec),'without_claim_role_unknown':len(dec),'independent_meaning_checks':0,'confirmed_meanings':0,'held_access':False,'decision':'two authored chains, no empirical selection from exposed fitted rule'})
files=['S05/INPUT.tsv','P01/REPORT.md','P25/MODEL.json','P13/REPORT.md','S10/DECISION.md']
js('SOURCE.json',{'files':[{'path':str((W/p).relative_to(R)),'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()} for p in files],'exposure':'all145groups and decision contexts known before rule construction','sealed':['f84','f84r'],'new_pages':False})
print((D/'RESULT.json').read_text())
