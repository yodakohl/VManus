import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P22');W=D.parent;S=W/'P11/INPUT.json'
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rows):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rows)
lines=json.loads(S.read_text())['lines'];flat=[]
for line in lines:
 for i,w in enumerate(line['groups'],1):flat.append(dict(record=line['locus'].split('.')[0],line=line['locus'],locus=f'{line["locus"]}:{i}',word=w))
heads={'ctho':'Pulver','cthy':'Kraut','chor':'Blüten','shor':'Früchte','chocthy':'Mark','cthaiin':'Pflanzenportion','keol':'Öl','chy':'Wasser','okaiin':'Ansatz','otchol':'Trockenmaterial'}
adj={'chol':'trocken','shol':'feucht'};verbs={'sho':'vermische','qotchy':'zerkleinere'}
js('MODEL.json',{'heads':heads,'adjectives':adj,'verbs':verbs,'daiin':'OBJECT case; W free particle, M free or bound marker','segmentation':'W identity; M every nonempty X+daiin splits, no exceptions','NP':'new head or verb/record end closes previous NP; unknown split stem makes opaque NP','valency':'first following known NP on same line before next verb must be OBJECT','duplicate_case':'reported, not removed','language':'unidentified; no sounds or inflection paradigm'})
js('SOURCE.json',{'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,D/'DECISION.md']},'scope':'Four previously exposed HERB4 paragraphs in original order','boundary_motivation':'GDT809 already reports RF cthodaiin vs ZL/IT ctho daiin at f32v.8; no new transcription or native boundary claim','sealed':['f84','f84r']});tab('INPUT.tsv',flat)
summary={};allcases=[];allops=[];allnps=[];allsplit=[]
for mode in ['W','M']:
 elements=[]
 for t in flat:
  w=t['word'];split=mode=='M' and w.endswith('daiin') and w!='daiin';ss=[w[:-5],'daiin'] if split else [w];offset=0
  for k,part in enumerate(ss):
   elements.append(dict(mode=mode,**t,element_id=t['locus']+'/'+str(k+1),start=offset,end=offset+len(part),piece=part,bound='YES' if split else 'NO',known=part in heads or part in adj or part in verbs or part=='daiin'));offset+=len(part)
  if split:allsplit.append(dict(mode=mode,**t,pieces='+'.join(ss),stem_status='KNOWN' if ss[0] in heads else 'UNKNOWN_STEM'))
 nps=[];cases=[];current=None;record=None;render={}
 for idx,e in enumerate(elements):
  if record!=e['record']:record=e['record'];current=None
  piece=e['piece'];opaque=e['bound']=='YES' and piece!='daiin' and piece not in heads
  if piece in heads or opaque:
   if current is not None:current['end_before']=e['element_id']
   current=dict(mode=mode,record=record,line=e['line'],np_id=e['element_id'],head=piece,head_known=not opaque,head_index=idx,case='UNMARKED',case_sources=[],adjectives=[],end_before='RECORD_END',used_by=[])
   nps.append(current);render[e['element_id']]=heads.get(piece,'⟦'+piece+'⟧')+'['+e['element_id']+']'
  elif piece in verbs:
   if current is not None:current['end_before']=e['element_id']
   current=None;render[e['element_id']]=verbs[piece]
  elif piece=='daiin':
   status='MISSING_HEAD' if current is None else 'UNKNOWN_STEM' if not current['head_known'] else 'DUPLICATE_CASE' if current['case']=='OBJECT' else 'MARKED_OBJECT'
   cases.append(dict(mode=mode,record=record,line=e['line'],locus=e['locus'],element_id=e['element_id'],bound=e['bound'],head=current['head'] if current else 'NA',np_id=current['np_id'] if current else 'NA',status=status))
   if current is not None:
    current['case_sources'].append(e['element_id'])
    if current['head_known']:current['case']='OBJECT'
   render[e['element_id']]='OBJ['+status+';NP='+ (current['np_id'] if current else 'NA')+']'
  elif piece in adj:
   if current is not None:current['adjectives'].append(piece)
   render[e['element_id']]=adj[piece]+'[NP='+ (current['np_id'] if current else 'NA')+']'
  else:render[e['element_id']]='⟦'+piece+'⟧'
 ops=[]
 for idx,e in enumerate(elements):
  if e['piece'] not in verbs:continue
  stop=next((k for k in range(idx+1,len(elements)) if elements[k]['line']!=e['line'] or elements[k]['piece'] in verbs),len(elements))
  candidates=[n for n in nps if idx<n['head_index']<stop and n['head_known']];target=candidates[0] if candidates else None
  gap=elements[idx+1:target['head_index']] if target else elements[idx+1:stop]
  status='MISSING_ARGUMENT' if target is None else 'MATCH_OBJECT' if target['case']=='OBJECT' else 'UNMARKED_ARGUMENT'
  if target:target['used_by'].append(e['element_id'])
  o=dict(mode=mode,record=e['record'],line=e['line'],locus=e['locus'],word=e['piece'],np_id=target['np_id'] if target else 'NA',head=target['head'] if target else 'NA',case=target['case'] if target else 'NA',status=status,open_intervening=','.join(x['element_id']+':'+x['piece'] for x in gap if not x['known']) or 'NONE')
  ops.append(o);render[e['element_id']]+=f'({o["head"]};{status};NP={o["np_id"]})'
 output_elements=[dict(e,rendering=render[e['element_id']]) for e in elements];tab(f'ELEMENTS_{mode}.tsv',output_elements)
 output_nps=[{k:v for k,v in n.items() if k not in ['case_sources','adjectives','used_by']}|{'case_sources':','.join(n['case_sources']) or 'NONE','adjectives':','.join(n['adjectives']) or 'NONE','used_by':','.join(n['used_by']) or 'NONE'} for n in nps]
 allnps+=output_nps;allcases+=cases;allops+=ops
 aligned=[]
 for t in flat:
  es=[e for e in elements if e['locus']==t['locus']];known=sum(e['known'] for e in es)
  aligned.append(dict(mode=mode,**t,pieces='+'.join(e['piece'] for e in es),coverage='FULL_HYPOTHESIS' if known==len(es) else 'PARTIAL_HYPOTHESIS' if known else 'OPEN',rendering=' + '.join(render[e['element_id']] for e in es)))
 tab(f'ALIGNMENT_{mode}.tsv',aligned)
 text=[f'# P22 — vollständige Fassung {mode}','','Alle Glossen sind hypothetisch. OBJ bezeichnet eine versuchsweise Objektfunktion, keinen identifizierten Lautwert oder lateinischen Kasus. ⟦…⟧ bleibt offen.','']
 for page in dict.fromkeys(t['record'] for t in flat):
  text+=['## '+page,'']
  for l in lines:
   if l['locus'].split('.')[0]==page:text+=['**'+l['locus']+'** `'+l['raw_line']+'`','',' · '.join(r['rendering'] for r in aligned if r['line']==l['locus']),'']
  text+=['### Handlungsargumente','']
  po=[o for o in ops if o['record']==page]
  for o in po:text.append(f'- {o["locus"]}: {verbs[o["word"]]} {heads.get(o["head"],"[Argument fehlt]")}; {o["status"]}. Offene Zwischenstücke: {o["open_intervening"]}.')
  if not po:text.append('- Keine gewählte Handlung; Katalogrest ohne Prüfung der Verbgrammatik.')
  text+=['']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
 summary[mode]={'groups':len(flat),'elements':len(elements),'raw_coverage':dict(Counter(a['coverage'] for a in aligned)),'case_occurrences':dict(Counter(c['status'] for c in cases)),'operations':dict(Counter(o['status'] for o in ops)),'marked_NPs':sum(n['case']=='OBJECT' for n in nps),'marked_NPs_without_governing_verb':sum(n['case']=='OBJECT' and not n['used_by'] for n in nps)}
tab('NOUN_PHRASES.tsv',allnps);tab('CASE_MARKERS.tsv',allcases);tab('OPERATIONS.tsv',allops);tab('ALL_SPLITS.tsv',allsplit)
js('RESULT.json',{'status':'PARTIAL_BOUNDARY_CASE_READING_NO_GRAMMATICAL_SELECTION','models':summary,'new_splits':len(allsplit),'language_identified':False,'phonetic_values_identified':0,'confirmed_meanings':0,'independent_confirmation_capacity':0,'scope':'145 previously exposed HERB4 groups; no legacy decoding restart'})
rep=['# P22 — Zerlegung muss dieselbe Grammatik tragen','','M zerlegt zwei Gruppen nach derselben festen Regel: cthodaiin wird ctho+daiin, odaiin wird o+daiin. Nur ctho besitzt eine angesetzte Stammkarte. Die zusätzliche Pulver-Objektphrase auf f21r.8 bleibt ohne regierende Handlung. An allen sechs Handlungsstellen haben W und M dieselben Ergebnisse; die Grenzregel wählt deshalb keine tragfähige Objektgrammatik aus.','','| Modell | Quellgruppen / Elemente | vollständige / partielle Hypothesen / offen | Fallmarker | Handlungen |','|---|---|---|---|---|']
for mode,r in summary.items():rep.append(f'| {mode} | {r["groups"]} / {r["elements"]} | {r["raw_coverage"]} | {r["case_occurrences"]} | {r["operations"]} |')
rep+=['','W behält Gruppen als Wörter und daiin als freie Objektpartikel. M trennt jedes nichtleere X+daiin und liest daiin als freie oder gebundene Objektmarkierung. Eine gemeinsame hypothetische Funktion, keine Laut- oder Sprachidentifikation. Zehn feste Materialköpfe und zwei Verben werden in allen vier Absätzen gleich verwendet. Die vollständige Schriftstückausrichtung steht in ELEMENTS_W/M.tsv mit Zeichenintervallen; keine Quellgrenze wird überschrieben.','','## Die beiden neuen Zerlegungen','','| Ort | Gruppe | Zerlegung | Konsequenz |','|---|---|---|---|','| f21r.8:7 | cthodaiin | ctho + daiin | Pulver als OBJECT; kein regierendes Verb im Modell |','| f29v.3:5 | odaiin | o + daiin | Stamm o unbekannt; keine Zusatzportion erfunden und kein Rückgriff auf einen fremden Kopf |','','ctho+daiin auf f21r.8 und geschriebenes ctho daiin auf f32v.8 erhalten in M dieselbe innere Hypothese. Beide markierten NPs sind hier unregiert. GDT809 hatte die alternative RF-Grenze auf f32v.8 schon dokumentiert; die Zeichenübereinstimmung ist kein neuer Fund. Die gemeinsame Funktion wurde eingesetzt, nicht unabhängig entdeckt.','','## Sämtliche Handlungsargumente (W und M identisch)','','| Ort | Verb | angenommener Kopf | Objektmarkierung | Befund | offene Zwischenstücke |','|---|---|---|---|---|---|']
for o in allops:
 if o['mode']=='W':rep.append(f'| {o["locus"]} | {o["word"]} | {o["head"]} | {o["case"]} | {o["status"]} | {o["open_intervening"]} |')
rep+=['','## Grammatische Gegenfälle','','Das doppelte daiin auf f32v.8:2–3 markiert denselben otchol-Kopf zweimal und verletzt die festgelegte Einmalregel. Die Wiederholung bleibt stehen; sie wird weder zu einer Zahl noch zu einer Ausnahme umgedeutet. Ein markierter Materialkopf bei qotchy auf f32v.9 passt zur angesetzten Valenz, aber cfhy und skey bleiben zwischen Verb und Kopf offen; das ist keine unabhängig bestätigte Satzanalyse. Vier andere Argumente sind unmarkiert, ein Argument fehlt.','','Der Startabsatz f17r enthält kein daiin und keine gewählte Handlung; er bietet keine Kapazität für die Grenz-/Objektregel. Er wird vollständig als partieller Katalogrest erhalten. Unregierte markierte NPs und unbekannte Wortstücke werden nicht als grammatische Erfolge gezählt. Auch die deutsche Pluralform Blüten liefert kein gelesenes Numerusparadigma.','','## Entscheidung','','Die Ein-Regel-Zerlegung erzeugt genau eine zusätzliche vollständig hypothetisch lesbare Rohgruppe, aber keine zusätzliche passende Handlung. W und M bleiben hinsichtlich aller Handlungsargumente ununterscheidbar; die feste allgemeine Objektmarkierung passt nicht durchgängig. M ist eine dokumentierte Grenzhypothese, keine ausgewählte Wortanalyse. Eine flektierende Sprache, Silbenwerte und ein Flexionsparadigma wurden nicht bestimmt. Das umfassendere P22-Programm bleibt partiell; kein allgemeines Urteil gegen variable Wortgrenzen.','','GDT605/616/895/906/911 und GDT629 bleiben unverändert. Insbesondere kein Neustart alter Einheiten-/CV-Decoder und keine gelockerte GDT616-Entscheidung. P20s feste technische Ganzwörter und P21s Ganzformfälle sind Vorgänger, keine unabhängigen Belege. Alle vier HERB4-Absätze waren exponiert. Keine Reservenöffnung, keine Bedeutung oder Signifikanz behauptet; f84/f84r geschlossen.','','## Reproduktion','','`python3 '+str(D/'build.py')+'`; `python3 '+str(D/'validate.py')+'` aus dem Repository. SOURCE.json bindet die begrenzte Quelle und vor Ausführung festgelegte DECISION.md. ALL_SPLITS.tsv enthält jeden Schnitt; CASE_MARKERS/OPERATIONS/NOUN_PHRASES sämtliche grammatischen Folgen; READING_W/M.md alle vier Absätze.']
(D/'REPORT.md').write_text('\n'.join(rep)+'\n');print(json.dumps(summary))
