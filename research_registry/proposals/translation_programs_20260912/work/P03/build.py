import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P03');W=D.parent
S=W/'P11/INPUT.json';L=W/'P11/COMMON_LEXICON.tsv'
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rr,fields=None):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=(fields or list(rr[0]))+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
source=json.loads(S.read_text());lines=source['lines'];lex=list(csv.DictReader(L.open(),delimiter='\t'))
materials={r['word']:r['value'] for r in lex if r['type']=='MATERIAL'}
other={r['word']:r['value'] for r in lex if r['type']=='LOCATION' or r['word'] in ['ol','s','shy','otshy','oltchy']}
other.update(chol='trocken',shol='feucht')
verbs={'cphos':'zerreibe','cpho':'zerstoße','qotchy':'zerkleinere','shytchy':'benetze','shot':'erwärme'}
values={'dair':'A','dain':'B','daiin':'C','dary':'D','ar':'E'}
worlds={'T':{'she':'Patient','sho':'verabreiche','shey':'beruhigt','sy':'gebessert'},'M':{'she':'Grundansatz','sho':'füge hinzu','shey':'ruhend','sy':'abgesetzt'}}
model={'materials':materials,'other':other,'manufacture':verbs,'quantities':values,'worlds':worlds,'quantity_modes':{'D':'Anwendungsmenge','H':'Herstellungsmenge','G':'Stärke'},'reference':'One E per record introduced only by prior she. Same whole material type reused within record; no aliasing by German gloss.','scope':'HERB4 paragraphs only; product forward on same line before verb; material/quantity reference backward within record; unknowns retained.'}
js('MODEL.json',model)
js('SOURCE.json',{'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,L,D/'DECISION.md']},'legacy_source':source['source'],'scope':['f17r.4-6','f21r.8-12','f32v.7-11','f29v.1-4'],'exposure':'All four work paragraphs repeatedly exposed; no independent confirmation set','sealed':['f84','f84r']})
flat=[]
for line in lines:
 for i,w in enumerate(line['groups'],1):flat.append({'record':line['locus'].split('.')[0],'line':line['locus'],'locus':f'{line["locus"]}:{i}','word':w})
assert len(flat)==145
tab('INPUT.tsv',flat)
allalign={};oprows=[];effrows=[];qrows=[];invrows=[];summary={}
for mode,terms in worlds.items():
 align=[];record=None
 for j,t in enumerate(flat):
  word=t['word'];loc=t['locus']
  if record!=t['record']:
   record=t['record'];lastmat=None;recipient=None;amount={};states={};prepared={};applications=[]
  kind='OPEN';render='⟦'+word+'⟧';ref='NA'
  if word in materials:
   kind='MATERIAL';ref=word;render=materials[word]+'['+word+']';lastmat=(word,loc)
   invrows.append(dict(mode=mode,**t,material=word,state=states.get(word,'Eingangszustand offen'),prior_manufacture=prepared.get(word,'NA')))
  elif word=='she':
   kind='RECIPIENT';ref='E';render=terms[word]+'[E]';recipient=loc
  elif word in verbs:
   kind='MANUFACTURE';ref=lastmat[0] if lastmat else 'NA'
   previous=states.get(ref,'Eingangszustand offen');after=verbs[word]+'-bearbeitet' if lastmat else 'UNBOUND'
   render=f'{verbs[word]}({ref if lastmat else "MATERIAL FEHLT"})'
   op=dict(mode=mode,**t,operation=verbs[word],kind=kind,material=ref,material_source=lastmat[1] if lastmat else 'NA',recipient='NA',recipient_source='NA',prior_manufacture=prepared.get(ref,'NA'),amount='NA',amount_source='NA',before=previous,after=after,remainder='unbestimmt',status=('BOUND_PRIMARY_MISSING_LIQUID' if word=='shytchy' else 'BOUND') if lastmat else 'MISSING_MATERIAL',extra_input='Benetzungsflüssigkeit ungebunden' if word=='shytchy' else 'NA')
   oprows.append(op)
   if lastmat:states[ref]=after;prepared[ref]=loc
  elif word=='sho':
   kind='APPLICATION';following=[]
   for u in flat[j+1:]:
    if u['line']!=t['line'] or u['word'] in verbs or u['word']=='sho':break
    if u['word'] in materials:following.append(u);break
   mat=following[0]['word'] if following else 'NA';ref=mat;dose=amount.get(mat)
   status='BOUND' if following and recipient else ('MISSING_RECIPIENT' if following else 'MISSING_MATERIAL_AND_OR_RECIPIENT')
   render=f'{terms[word]}(Mittel={materials.get(mat,"FEHLT")}[{mat}];Empfänger={terms["she"]+"[E]" if recipient else "FEHLT"})'
   op=dict(mode=mode,**t,operation=terms[word],kind=kind,material=mat,material_source=following[0]['locus'] if following else 'NA',recipient='E' if recipient else 'NA',recipient_source=recipient or 'NA',prior_manufacture=prepared.get(mat,'NA'),amount=dose[0] if dose else 'NA',amount_source=dose[1] if dose else 'NA',before=states.get(mat,'Eingangszustand offen'),after='Teilmenge zu E übertragen' if status=='BOUND' else 'nicht ausführbar',remainder='unbestimmt',status=status,extra_input='NA')
   oprows.append(op)
   if status=='BOUND':applications.append(loc)
  elif word in ['shey','sy']:
   kind='ENDPOINT';ref='E' if recipient else 'NA'
   status='REFERENCE_MISSING' if not recipient else ('AFTER_APPLICATION' if applications else 'BEFORE_APPLICATION')
   effrows.append(dict(mode=mode,**t,meaning=terms[word],recipient=ref,recipient_source=recipient or 'NA',prior_application=applications[-1] if applications else 'NA',status=status))
   render=f'{terms[word]}({ref};{status})'
  elif word in values:
   kind='QUANTITY';ref=lastmat[0] if lastmat else 'NA'
   qrows.append(dict(mode=mode,**t,value=values[word],material=ref,material_source=lastmat[1] if lastmat else 'NA',status='BOUND' if lastmat else 'MISSING_MATERIAL'))
   if lastmat:amount[ref]=(values[word],loc)
   render=f'{{DIM}} {values[word]}({ref})'
  elif word in other:kind='OTHER';render=other[word]
  align.append(dict(mode=mode,**t,kind=kind,reference=ref,rendering=render))
 allalign[mode]=align;tab(f'ALIGNMENT_{mode}.tsv',align)
 for dim,title in model['quantity_modes'].items():
  text=[f'# P03 — {mode}/{dim}: '+('therapeutische' if mode=='T' else 'herstellende')+' Arbeitsfassung','', 'Sämtliche deutschen Werte sind Annahmen, ⟦…⟧ bleibt offen. Gleichbleibende Wort-ID bedeutet hypothetisch denselben Materialtyp, keine bewiesene Portion.','']
  for rec in dict.fromkeys(t['record'] for t in flat):
   aa=[r for r in align if r['record']==rec];oo=[r for r in oprows if r['mode']==mode and r['record']==rec];ee=[r for r in effrows if r['mode']==mode and r['record']==rec]
   text += [f'## Rezeptblatt {rec}','', 'Anlass: kein ausdrücklicher Krankheits-/Herstellungsanlass gebunden.','', 'Bestandteile: '+', '.join(materials[w]+'['+w+']' for w in dict.fromkeys(r['word'] for r in aa if r['kind']=='MATERIAL'))+'.','']
   for line in lines:
    if line['locus'].split('.')[0]!=rec:continue
    text += [f'**{line["locus"]}** `{line["raw_line"]}`','',' · '.join(r['rendering'].replace('{DIM}',title) for r in aa if r['line']==line['locus']),'']
   text += ['### Durchspielen','']
   for op in oo:
    if op['kind']=='MANUFACTURE':text.append(f'- {op["locus"]}: {op["operation"]} {op["material"]}; {op["before"]} → {op["after"]}; {op["status"]}. Zusatzrolle: {op["extra_input"]}.')
    else:text.append(f'- {op["locus"]}: {op["operation"]} {op["material"]} aus {op["material_source"]} an {op["recipient"]}, erwähnt {op["recipient_source"]}; {op["status"]}. Frühere Herstellung desselben Materials: {op["prior_manufacture"]}. '+(f'Anwendungsmenge {op["amount"]} aus {op["amount_source"]}.' if dim=='D' else 'Anwendungsmenge nicht angegeben; Herstellungsmenge/Stärke ersetzt sie nicht.')+' Restmenge unbestimmt.')
   if not oo:text+=['- Keine der festgelegten Hauptoperationen im Absatz vorhanden.']
   text+=['','Endbedingung: '+('; '.join(r['locus']+' '+r['meaning']+' '+r['status'] for r in ee) or 'kein gewählter Endbefund vorhanden')+'.','', 'Ausführbarkeitslücken: offene Gruppen bleiben unübersetzt; keine Dosiszahl oder Anfangsmenge, keine ungeschriebenen Patienten, keine angenommene Heilwirkung. H/G/D sind rivalisierende Größenarten.','']
  (D/f'READING_{mode}_{dim}.md').write_text('\n'.join(text).rstrip()+'\n')
tab('OPERATIONS.tsv',oprows);tab('ENDPOINTS.tsv',effrows);tab('QUANTITIES.tsv',qrows);tab('INVENTORY.tsv',invrows)
qcon=[]
for q in qrows:
 uses=[r['locus'] for r in oprows if r['mode']==q['mode'] and r['amount_source']==q['locus']]
 qcon.append(dict(mode=q['mode'],record=q['record'],locus=q['locus'],word=q['word'],value=q['value'],material=q['material'],D_application=','.join(uses) or 'NONE',H='Herstellungsmenge '+q['value'] if q['status']=='BOUND' else 'UNBOUND',G='Stärke '+q['value'] if q['status']=='BOUND' else 'UNBOUND',decision='free symbolic value; no numerical execution'))
tab('QUANTITY_CONSEQUENCES.tsv',qcon)
for mode in worlds:
 aa=allalign[mode];oo=[r for r in oprows if r['mode']==mode];apps=[r for r in oo if r['kind']=='APPLICATION'];ee=[r for r in effrows if r['mode']==mode]
 summary[mode]={'groups':len(aa),'hypothesis':sum(r['kind']!='OPEN' for r in aa),'open':sum(r['kind']=='OPEN' for r in aa),'manufacturing':dict(Counter(r['status'] for r in oo if r['kind']=='MANUFACTURE')),'applications':dict(Counter(r['status'] for r in apps)),'endpoints':dict(Counter(r['status'] for r in ee)),'applications_with_written_dose':sum(r['amount']!='NA' for r in apps),'applications_with_prior_same_material_manufacture':sum(r['prior_manufacture']!='NA' for r in apps),'quantity_occurrences':sum(r['mode']==mode for r in qrows),'quantity_bindings':dict(Counter(r['status'] for r in qrows if r['mode']==mode))}
js('RESULT.json',{'status':'PARTIAL_THERAPEUTIC_READING_NO_POST_APPLICATION_EFFECT_BINDING','worlds':summary,'meaning_identifications':0,'independent_confirmation_capacity':0,'symmetry':'T/M participant graph identical under Patient↔Grundansatz and administer↔add renaming; endpoint ordering and dose gaps identical.','scope':'Four exposed HERB4 paragraphs, not complete pages.'})
rep=['# P03 — Mittel, Empfänger und Wirkung gemeinsam binden','', 'Die therapeutische Fassung bindet drei der vier angenommenen Verabreichungen an einen ausdrücklich angesetzten Empfänger. Keiner der drei angesetzten Endbefunde folgt einer solchen Anwendung. Die Herstellungsversion hat denselben Referenzgraphen; die Wortwerte bleiben unentschieden.','', 'Dies ist ein tatsächlich ausgeführter erster Teilentwurf, keine vollständige Übersetzung. Alle 145 Gruppen in vier exponierten HERB4-Absätzen stehen in beiden Fassungen und allen drei Mengengegenlesungen.','', '| Fassung | Hypothesen / offen | Herstellung | Anwendung/Zugabe | Endbefunde |','|---|---|---|---|---|']
for m,c in summary.items():rep.append(f'| {m} | {c["hypothesis"]} / {c["open"]} | {c["manufacturing"]} | {c["applications"]} | {c["endpoints"]} |')
rep+=['','T: she≈Patient, sho≈verabreiche, shey≈beruhigt, sy≈gebessert. M: she≈Grundansatz, sho≈füge hinzu, shey≈ruhend, sy≈abgesetzt. Das sind bewusst rivalisierende Hypothesen, keine übernommenen Bedeutungsbelege. sheey bleibt offen. Gemeinsame Materialkarten stammen aus P11; die feste Herstellungsregel und neue Wortwerte sind in DECISION.md/MODEL.json angegeben.','','## Alle Anwendungsstellen (T; M hat dieselben Bindungen)','','| Ort | Mittel / Quelle | Empfängerquelle | Dosis | Frühere Bearbeitung desselben Mittels | Befund |','|---|---|---|---|---|---|']
for r in oprows:
 if r['mode']=='T' and r['kind']=='APPLICATION':rep.append(f'| {r["locus"]} | {r["material"]} / {r["material_source"]} | {r["recipient_source"]} | {r["amount"]} | {r["prior_manufacture"]} | {r["status"]} |')
rep+=['','## Alle angesetzten Endbefunde','','| Ort | Wort | Empfängerquelle | Vorherige Anwendung | Konsequenz |','|---|---|---|---|---|']
for r in effrows:
 if r['mode']=='T':rep.append(f'| {r["locus"]} | {r["word"]} | {r["recipient_source"]} | {r["prior_application"]} | {r["status"]} |')
rep+=['','## Rezept- und Mengenkonsequenzen','','f17r besitzt in diesem festen Wörterbuch keine Herstellungs-/Anwendungsoperation. f21r hat eine ausdrücklich angesetzte Flüssigauszug-Gabe, aber keinen zuvor geschriebenen she-Empfänger. f32v ergibt unter T Öl und danach Wasser für denselben Patienten; M liest Öl und danach Wasser als Zugaben zu demselben Grundansatz. f29v ergibt eine Ansatz-Gabe nach dem angenommenen Patienten, doch sy=gebessert steht schon davor. Vorherige Besserung ist keine logische Unmöglichkeit: Sie liefert hier keinen Nachweis einer Wirkung der späteren Gabe.','','Elf der zwölf Größenstellen haben einen Materialbezug; dain auf f32v.7:7 hat keinen. BOUND_PRIMARY_MISSING_LIQUID bei shytchy bedeutet nur gebundenes Zielmaterial, keine vollständige Benetzungsoperation.','','Alle zwölf Größenstellen mit fünf freien Symbolen stehen einzeln in QUANTITY_CONSEQUENCES.tsv. D (Anwendungsmenge), H (Herstellungsmenge) und G (Stärke) behalten dieselben Materialbindungen. Keine der vier Anwendungen hat unter der festen chronologischen Gleichwortregel eine zugehörige frühere Dosis. Unbenutzte D-Angaben sind nicht nachträglich auf andere Mittel übertragbar; sie bleiben als Anwendungsangaben unverbunden. H und G haben dieselben bloßen Materialzuordnungen und werden dadurch nicht unterschieden. Keine tatsächliche Zahl oder Maßeinheit wurde erkannt.','','Die beiden daiin auf f32v.8 beziehen sich unter dieser Regel auf dasselbe otchol. Anders als P05 wird keine Verteilung auf zwei Materialien angenommen. Es sind zwei sichtbare Aussagen desselben freien Wertes, kein Beleg für Doppeldosis. qotaiin bleibt ein hypothetischer Portionsname und ist keine identifizierte Zahl.','','Die sichtbare Erwärmung auf f29v.4:7 bindet cthy, die folgende Gabe okaiin. Die Lesung darf deshalb nicht stillschweigend behaupten, der verabreichte Ansatz sei gerade erwärmt worden. Kein Anwendungsstoff hat hier eine frühere zugeordnete Herstellung. Roh oder zuvor hergestellte Mittel wären möglich; eine ungeschriebene Vorgeschichte wird nicht als Textbefund eingetragen. Alle Restmengen bleiben unbestimmt. Benetzen auf f29v.1 hat zusätzlich keine gebundene Benetzungsflüssigkeit.','','## Entscheidung','','T als partielle therapeutische Hypothese weiter zulässig, aber nicht vor M ausgewählt. Die ausdrücklich geforderte Empfänger→Gabe→späterer Befund-Kette entsteht nicht. Drei vollständige Rollenbindungen sind modellinterne Konsequenzen, keine drei Übersetzungstreffer. Patient und Grundansatz lassen sich im ganzen Graphen vertauschen; dieser Test bindet den semantischen Unterschied Mensch/Material nicht. Auch eine hypothetische Endzustandsaussage würde allein noch keine Kausalität beweisen.','','Es wurden sämtliche Gegenfälle und Lücken behalten. Fehlende Rollen, fehlende Ausführungsgrößen und fehlende Bedeutungsbindung sind getrennt; weder eine ungebundene Aussage noch eine zeitlich frühere Besserung wird pauschal zur widerlegten Rezeptgattung erklärt. Eine spätere Version braucht einen tatsächlich getragenen Unterschied zwischen Empfänger und Ansatz bzw. einen anschließenden Wirkungsbezug, keinen Namenstausch.','','GDT809/769/904 sowie P05/P14 bleiben unverändert. Kein neuer Decoder, kein historischer Quellensatz eingepasst. Alle vier Absätze sind vorbelastetes Material; keine unabhängige Bestätigungskapazität, kein Signifikanzanspruch, kein bestätigter Pflanzenname. f84/f84r und weitere Reserven bleiben geschlossen.','','## Nachrechnung','','`python3 '+str(D/'build.py')+'` und `python3 '+str(D/'validate.py')+'` aus dem Repository. SOURCE.json bindet Quellen und vor Ausführung festgelegte Entscheidung. INPUT/ALIGNMENT bewahren jede Gruppe; OPERATIONS, INVENTORY, ENDPOINTS und QUANTITIES sämtliche Rollen. READING_T_D/H/G.md und READING_M_D/H/G.md enthalten alle vier Rezeptblätter mit offenem Anlass und Endbedingungen.']
(D/'REPORT.md').write_text('\n'.join(rep)+'\n')
print(json.dumps(summary,ensure_ascii=False))
