import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P17');W=D.parent
S=W/'P12/PROSE.tsv';P=W/'P12/MODEL.json'
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rr):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0])+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
lines=list(csv.DictReader(S.open(),delimiter='\t'));model=json.loads(P.read_text());names=model['names'];actions=model['actions']
flat=[]
for r in lines:
 for i,w in enumerate(r['zl3b_line'].split(),1):flat.append(dict(record=r['record_id'],line=r['locus'],locus=f'{r["locus"]}:{i}',word=w))
js('SOURCE.json',{'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,P,D/'DECISION.md']},'scope':'51 exposed f83r prose lines, first P1-P3 then remaining four records; no whole-image completeness claim','exposure':'All records known, no independent confirmation','sealed':['f84','f84r']})
js('MODEL.json',{'lexicon':model,'N':'First occurrence of each material type activates it; later mentions never switch.','R':'First material activates; different material switches only upon a repeated occurrence.','L1':'Every material mention updates. P12 baseline.','T0':'First material only. P12 baseline.','boundaries':'Activation/switch until next different activation or record end; B only destination; no unknown inferred marker.'})
tab('INPUT.tsv',flat)
mentions=[];pred=[];blocks=[];allalign={}
for mode in ['N','R','L1','T0']:
 rec=None;align=[];block=None
 for j,t in enumerate(flat):
  if rec!=t['record']:
   rec=t['record'];seen={};topic='NA';origin='NA';destination='NA';dest_source='NA';block=None
  w=t['word'];loc=t['locus'];kind='OPEN';render=f'⟦{w}⟧';role='NA'
  if w in names:
   name=names[w];slot=name['slot'];kind='NOUN'
   if slot=='B':
    role='DESTINATION_REPEAT' if destination!='NA' else 'DESTINATION_INTRODUCTION';destination='B';dest_source=loc
   else:
    was=topic;known=slot in seen
    activate=topic=='NA' or (mode=='L1') or (mode=='N' and not known) or (mode=='R' and known)
    switch=activate and topic!=slot
    if switch:
     if block is not None:block['end_before']=loc;block['end_reason']='NEXT_TOPIC_SWITCH'
     topic=slot;origin=loc
     block=dict(mode=mode,record=rec,block_id=mode+':'+loc,origin=loc,topic=topic,previous_topic=was,kind='INITIAL' if was=='NA' else 'SWITCH',end_before='RECORD_END',end_reason='RECORD_END',actions=[])
     blocks.append(block)
     role='INITIAL_TOPIC' if was=='NA' else ('CONTRAST_SWITCH_ASSUMED' if known else 'NEW_TOPIC_SWITCH')
    elif slot==topic:role='TOPIC_RESUMPTION'
    else:role='KNOWN_BACKGROUND' if known else 'NEW_BACKGROUND'
    seen[slot]=loc
   mentions.append(dict(mode=mode,**t,slot=slot,role=role,active_topic=topic,topic_origin=origin,block_id=block['block_id'] if block else 'NA'))
   render=f'{name["meaning"]}[{slot};{role}]'
  elif w in actions:
   kind='PREDICATE';role='IMPLICIT_PATIENT'
   complete=topic!='NA' and (w=='chedy' or destination!='NA')
   p=dict(mode=mode,**t,patient=topic,patient_source=seen.get(topic,origin) if mode=='L1' else origin,destination=destination if w=='qokeedy' else 'NA',destination_source=dest_source if w=='qokeedy' else 'NA',block_id=block['block_id'] if block else 'NA',status='COMPLETE' if complete else 'MISSING_PATIENT' if topic=='NA' else 'MISSING_DESTINATION')
   pred.append(p)
   if block:block['actions'].append(loc)
   render=f'{actions[w]}([ergänzt:{topic};Bezugquelle={p["patient_source"]}]'+(f';Ziel={destination};Quelle={dest_source}' if w=='qokeedy' else '')+')'
  align.append(dict(mode=mode,**t,kind=kind,role=role,rendering=render))
 allalign[mode]=align;tab(f'ALIGNMENT_{mode}.tsv',align)
lookup={(p['mode'],p['locus']):p for p in pred}
brows=[]
for b in blocks:
 ps=[lookup[(b['mode'],loc)] for loc in b['actions']]
 brows.append({k:v for k,v in b.items() if k!='actions'}|{'actions':','.join(b['actions']) or 'NONE','predicate_count':len(ps),'complete_predicates':sum(p['status']=='COMPLETE' for p in ps),'different_from_L1':sum(p['patient']!=lookup[('L1',p['locus'])]['patient'] for p in ps),'different_from_T0':sum(p['patient']!=lookup[('T0',p['locus'])]['patient'] for p in ps)})
tab('TOPIC_BLOCKS.tsv',brows);tab('MENTIONS.tsv',mentions);tab('PREDICATIONS.tsv',pred)
comparisons=[]
for p in pred:
 if p['mode']=='N':comparisons.append({'record':p['record'],'locus':p['locus'],'word':p['word']}|{m:lookup[(m,p['locus'])]['patient'] for m in ['N','R','L1','T0']}|{'destination':p['destination'],'status':p['status']})
tab('ALL_PREDICATE_COMPARISONS.tsv',comparisons)
summary={}
for mode,aa in allalign.items():
 text=[f'# P17 — vollständige Fassung {mode}','','Alle Bedeutungen sind P12-Hypothesen. Ergänzte Argumente stehen ausdrücklich in Klammern; ⟦…⟧ bleibt offen. Ein Themenbaum ist keine beobachtete Autorenstruktur.','']
 for rec in dict.fromkeys(t['record'] for t in flat):
  text += [f'## {rec}','']
  for line in lines:
   if line['record_id']==rec:text += [f'**{line["locus"]}** `{line["zl3b_line"]}`','',' · '.join(r['rendering'] for r in aa if r['line']==line['locus']),'']
  text += ['### Themenbaum und sämtliche ergänzten Bezüge','']
  for b in brows:
   if b['mode']==mode and b['record']==rec:
    text += [f'- {b["origin"]}: Thema {b["topic"]}, {b["kind"]}; Ende vor {b["end_before"]}. Aktionen: {b["actions"]}.']
  for p in pred:
   if p['mode']==mode and p['record']==rec:text += [f'- {p["locus"]}: ausgelassenes Material → {p["patient"]} aus {p["patient_source"]}; Füllziel → {p["destination"]} aus {p["destination_source"]}; {p["status"]}.']
  text+=['']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
 pp=[p for p in pred if p['mode']==mode];bs=[b for b in brows if b['mode']==mode];switches=[b for b in bs if b['kind']=='SWITCH']
 summary[mode]={'groups':len(aa),'hypothesis':sum(r['kind']!='OPEN' for r in aa),'open':sum(r['kind']=='OPEN' for r in aa),'predications':dict(Counter(p['status'] for p in pp)),'missing_patient_total':sum(p['patient']=='NA' for p in pp),'missing_destination_total':sum(p['word']=='qokeedy' and p['destination']=='NA' for p in pp),'topic_blocks':len(bs),'switches':len(switches),'switch_blocks_with_two_predicates':sum(b['predicate_count']>=2 for b in switches),'switch_blocks_two_changes_vs_L1':sum(b['different_from_L1']>=2 for b in switches),'switch_blocks_two_changes_vs_T0':sum(b['different_from_T0']>=2 for b in switches),'switch_blocks_two_changes_vs_both':sum(b['different_from_L1']>=2 and b['different_from_T0']>=2 for b in switches)}
js('RESULT.json',{'status':'PARTIAL_TOPIC_READING_EXPLICIT_MULTI_PREDICATE_RIVALS','models':summary,'meaning_identifications':0,'independent_confirmation_capacity':0,'interpretation':'Joint reference changes are conditional model outputs, not a recovered discourse marker or preferred translation.'})
report=['# P17 — Themenwechsel mit gemeinsamem Geltungsbereich','','Die beiden neuen Diskursfassungen N und R sind auf dem gesamten f83r-Prose-Arbeitsblatt ausgeführt. Keine neue Wortbedeutung wurde ergänzt. Sie halten ausdrücklich fest, welche Materialnennungen das Thema ändern und welche Hintergrund bleiben. Die folgenden Unterschiede sind Konsequenzen dieser Annahmen, keine Bestätigung ihrer Richtigkeit.','','| Modell | Wechsel | Wechselblöcke mit ≥2 Aussagen | ≥2 andere Bezüge als L1 | ≥2 andere Bezüge als T0 | beides im selben Block |','|---|---:|---:|---:|---:|---:|']
for mode,c in summary.items():report.append(f'| {mode} | {c["switches"]} | {c["switch_blocks_with_two_predicates"]} | {c["switch_blocks_two_changes_vs_L1"]} | {c["switch_blocks_two_changes_vs_T0"]} | {c["switch_blocks_two_changes_vs_both"]} |')
report+=['','N macht eine erste Materialnennung zum neuen Thema und lässt spätere bekannte Nennungen im Hintergrund. R wechselt erst bei erneuter Nennung des anderen Materials. Die Wiederholung des aktuellen Themas ist in beiden nur Wiederaufnahme. L1 (letztes Material) und T0 (erstes Material) sind die unveränderten P12-Baselines. Ein Block endet am nächsten tatsächlichen Themenwechsel oder an der Recordgrenze. B=Gefäß aktualisiert nur das Ziel. Keine Bildposition und kein unbekanntes Wort liefert einen freien Themenmarker.','','Alle vier Fassungen: 341 Gruppen, 50 Positionen mit P12-Hypothesen, 291 offen; 20 Prädikationen. Ein gemeinsames Thema kann fehlende Ziele nicht ersetzen. Die exakten Vollständigkeitszahlen stehen in RESULT.json und an jedem Prädikat.','','## Alle Wechselblöcke der neuen Modelle','','| Modell | Beginn | Wechsel | Ende vor | sämtliche Aktionen | vollständig | andere Bezüge L1 / T0 |','|---|---|---|---|---|---:|---|']
for b in brows:
 if b['mode'] in ['N','R'] and b['kind']=='SWITCH':report.append(f'| {b["mode"]} | {b["origin"]} | {b["previous_topic"]}→{b["topic"]} | {b["end_before"]} | {b["actions"]} | {b["complete_predicates"]} | {b["different_from_L1"]} / {b["different_from_T0"]} |')
report+=['','## Sämtliche Prädikationen im direkten Vergleich','','| Ort | Wort | N | R | L1 | T0 | Ziel |','|---|---|---|---|---|---|---|']
for p in comparisons:report.append('| '+' | '.join(p[k] for k in ['locus','word','N','R','L1','T0','destination'])+' |')
report+=['','## Konkrete bedingte Lesungsfolge','','N eröffnet bei lchedy auf f83r.3:7 das Thema Zusatzstoff. Dadurch heißen .4:9, .6:6 und .6:7 hypothetisch: Erwärme den Zusatzstoff; erwärme ihn; fülle ihn in das genannte Gefäß. L1 und T0 beziehen diese drei Aktionen auf die Flüssigkeit. Das geerbte Verb und das Füllziel bleiben gleich. Die schriftlichen shedy-Wiederholungen auf .4/.5 werden in N Hintergrund, nicht jeweils neue Patienten; genau diese starke Annahme bleibt sichtbar.','','Im späteren Record P5 eröffnet shedy auf .37:5 das neue Thema Flüssigkeit. N bindet beide Erwärmungen .42:5/.43:3 an sie, obwohl lchedy auf .41:3 dazwischensteht. R/L1/T0 bleiben dort beim Zusatzstoff. Beide Aktionen sind derselbe angenommene Verbtyp, also keine zwei unabhängigen Bedeutungsbelege. Beide N-Blöcke enden erst mit ihrem Record; eine innere Beendigung durch einen weiteren neuen Materialtyp ist bei nur A/C nach dem zweiten Typ nicht möglich. Diese lexikalisch bedingte Kapazitätsgrenze wurde nicht als entdecktes Satzende ausgegeben.','','## Entscheidung und Grenzen','','N besitzt zwei Wechselblöcke, die jeweils mindestens zwei Bezüge gegenüber beiden Baselines verändern. R hat keinen Wechsel mit zwei nachfolgenden Prädikationen; seine mehrteiligen Unterschiede entstehen nur durch initiale Themenpersistenz. Für die weitere Ausarbeitung einer echten Wechselregel bietet N damit den konkreteren Arbeitskandidaten, ohne als richtige Übersetzung gewählt zu sein. Ein Wechselblock liefert nur dann eine neue mehrteilige Lesungskonsequenz gegenüber den Baselines, wenn tatsächlich mehrere Bezüge abweichen. Initiale Persistenz, reine Umbenennung und passende Einzelbezüge werden nicht dafür gezählt. Die Tabellen zeigen alle Fälle einschließlich leerer Wechselblöcke; keine nachträgliche Kürzung oder Umverteilung. Keine dieser Zählungen ist ein Test gegen unabhängige richtige Argumente. N/R bleiben deshalb Diskursrivalen; eine kleinere Anzahl Wechsel oder flüssigere deutsche Formulierung wählt kein Modell aus.','','A=Flüssigkeit und C=Zusatzstoff können inhaltlich anders heißen, ohne die Themenrechnung zu ändern. Selbst die als Kontrast bezeichnete R-Umschaltung hat keinen gebundenen semantischen Gegensatz. Die fünf geerbten Wortkarten bleiben Annahmen. Die 291 offenen Gruppen könnten Satz-, Themen- oder Gegenstandsgrenzen enthalten; ihre Behandlung als für dieses begrenzte Register wirkungslos ist keine Entzifferung.','','P1–P3 dienen der ersten Ausarbeitung; die übrigen vier Records werden unverändert mitgerechnet. Alle waren vorher exponiert, also keine unabhängige Bestätigung. Q1/Q2 werden als eigene Records behandelt, nicht mit einem Bildthema aufgefüllt. Keine Bildlabels oder neuen Seiten geöffnet; f84/f84r bleiben geschlossen. Keine Signifikanz oder score-ready Relationsevidenz.','','## Quellen und Reproduktion','','GDT790/792/809/220 und P12/P18 bleiben unverändert. Die Diskursregeln sind in DECISION.md vor Ausführung festgelegt; SOURCE.json bindet sie und die begrenzte P12-Projektion. TOPIC_BLOCKS.tsv und MENTIONS.tsv ergeben den vollständigen Themenbaum; PREDICATIONS.tsv listet jedes ergänzte Material und Ziel samt Schriftquelle. READING_N/R/L1/T0.md zeigen sämtliche Zeilen einschließlich aller unübersetzten Gruppen.','','`python3 '+str(D/'build.py')+'`; `python3 '+str(D/'validate.py')+'` aus dem Repository.']
(D/'REPORT.md').write_text('\n'.join(report)+'\n');print(json.dumps(summary))
