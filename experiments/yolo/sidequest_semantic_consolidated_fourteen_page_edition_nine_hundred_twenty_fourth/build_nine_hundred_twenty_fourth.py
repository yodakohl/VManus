#!/usr/bin/env python3
"""Build Pass 924: consolidated creative edition over all fourteen pages."""

import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P912=ROOT/'experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth'
P917=ROOT/'experiments/yolo/sidequest_semantic_fluent_prose_nine_hundred_seventeenth'
P918=ROOT/'experiments/yolo/sidequest_semantic_minimal_verb_deck_nine_hundred_eighteenth'
P920=ROOT/'experiments/yolo/sidequest_semantic_apprentice_encoder_nine_hundred_twentieth'
P922=ROOT/'experiments/yolo/sidequest_semantic_component_shelves_nine_hundred_twenty_second'
P923=ROOT/'experiments/yolo/sidequest_semantic_learned_root_readings_nine_hundred_twenty_third'
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

LABEL={
 'OT':'nächster Platz','OL':'gleiche Reihe weiter','OS':'zusätzlicher Eintrag','RESUME_CARD':'Bezug wiederaufnehmen','Y':'dieser Platz',
 'OR':'Eintragsklasse','CHEO':'lokaler Eintrag','HO':'Teil','AIIN':'verzeichneter Sollwert','AIN':'Einheit','IIN':'Indexstufe','DA':'zweite Stufe',
 'AR':'Quell- oder Bezugsstelle','D_ADDR':'Unterplatz','A_ADDR':'lokale Adresse','AL':'Zielplatz','AM_ADDR':'Innenplatz','L':'Verbindung',
 'CKH':'Verbindungsweg','AIR':'Ringlauf','S_ADDR':'Sternbezug','Z_ADDR':'z-Stelle','O':'Reihe aufrufen','OK':'Platz aktivieren',
 'CH':'Klassenkennung','K':'Wert zuordnen','T':'Platz einstellen','S':'Klasse wählen','P':'Eintrag beginnen','CTH':'Bereitschaftsklasse',
 'R':'Zustandsmarke','SH':'Bezug halten','SHED':'Endstatus','CHD':'zum nächsten Platz wechseln','CHK':'Bedingungsklasse','CPH':'Gegenplatz',
 'SOLK':'Sammelgruppe','LSH':'Durchlaufklasse','CFH':'Trennklasse','AN':'Zusatzklasse','LD':'Bindung','E':'erster Grad','EE':'zweiter Grad',
 'EEE':'voller Grad','DY':'Eintrag schließen','CARRIER_Q':'q-Träger','D_LABEL':'d-Zeichen','G_LABEL':'g-Zeichen','S_LABEL':'s-Zeichen',
 'M_LOCAL':'m-Zeichen','LOCAL_CHAR_B':'b-Zeichen','LOCAL_CHAR_F':'f-Zeichen','LOCAL_CHAR_G':'g-Zeichen','LOCAL_CHAR_I':'i-Zeichen',
 'LOCAL_CHAR_J':'j-Zeichen','LOCAL_CHAR_Z':'z-Zeichen',
}
def revise(s):
 return s.replace('rückführen','umleiten').replace('Rückführen','Umleiten').replace('Stoffteil','Teil').replace('stoffteil','teil').replace('Pressen','Trennen').replace('pressen','trennen')
def label_read(r):
 vals=[]
 for a in r['component_recipe'].split('+'):
  v=LABEL[a]
  if not vals or vals[-1]!=v:vals.append(v)
 owner=r['visible_owner_de'] if r['visible_owner_de']!='NOT_APPLICABLE' else r['owner_description_de']
 return f"{owner}: "+', '.join(vals)+'.'

def main():
 base=read(P912/'PASS912_2511_EVENT_INTERLINEAR.tsv');bindings={r['event_id']:r for r in read(P917/'PASS917_2010_EVENT_BINDINGS.tsv')}
 oldins=read(P918/'PASS918_1435_REVISED_INSTRUCTIONS.tsv');ins=[];imap={}
 for r in oldins:
  z=dict(r);z['current_fluent_de']=revise(r['revised_fluent_de']);ins.append(z);imap[r['instruction_id']]=z
 write('PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv',ins,list(ins[0]))
 oldclauses=read(P918/'PASS918_354_REVISED_CLAUSES.tsv');clauses=[]
 for r in oldclauses:
  z=dict(r);z['current_fluent_clause_de']=' '.join(imap[x]['current_fluent_de'] for x in r['instruction_ids'].split('|'));clauses.append(z)
 write('PASS924_354_CURRENT_CLAUSES.tsv',clauses,list(clauses[0]))

 ledger=[]
 for r in base:
  z=dict(r)
  if r['usage_class']=='PROSE':
   iid=bindings[r['event_id']]['instruction_id'];reading=imap[iid]['current_fluent_de'];channel='WORKSHOP_PROSE';unit=iid
  else:
   reading=label_read(r);channel='OWNER_ADDRESS_OR_DIAGRAM';unit=r['event_id']
  z.update({'current_channel':channel,'current_spoken_unit':unit,'current_reading_de':reading})
  ledger.append(z)
 write('PASS924_2511_CURRENT_EVENT_LEDGER.tsv',ledger,list(ledger[0]))

 # Revised component shelf.
 roots={r['root']:r for r in read(P923/'PASS923_10_LEARNED_ROOT_DECISIONS.tsv')}
 components=[]
 for r in read(P922/'PASS922_56_COMPONENT_SHELVES.tsv'):
  z=dict(r)
  if r['component'] in roots:
   z['fixed_default_de']=roots[r['component']]['fixed_default_de'];z['teaching_note_de']=roots[r['component']]['short_teaching_rule_de']
  components.append(z)
 write('PASS924_56_CURRENT_COMPONENTS.tsv',components,list(components[0]));cmean={r['component']:r['fixed_default_de'] for r in components}

 # Revised verb deck.
 verbs=[]
 for r in read(P918/'PASS918_17_VERB_DECK.tsv'):
  z=dict(r)
  if r['stem']=='CPH':z['fixed_verb_de']='UMLEITEN';z['short_definition_de']='in Gegen-, Empfangs- oder zweiten Lauf führen'
  if r['stem']=='CFH':z['fixed_verb_de']='TRENNEN';z['short_definition_de']='den Posten trennen; lokal auspressen'
  verbs.append(z)
 write('PASS924_17_CURRENT_VERBS.tsv',verbs,list(verbs[0]))

 # Exact-card dictionary.
 grouped=defaultdict(list);order=[]
 for r in ledger:
  k=r['dictionary_entry_id']
  if k not in grouped:order.append(k)
  grouped[k].append(r)
 dictionary=[]
 for k in order:
  rs=grouped[k];recipes=list(dict.fromkeys(r['component_recipe'] for r in rs));assert len(recipes)==1
  recipe=recipes[0];atoms=recipe.split('+');channels=list(dict.fromkeys(r['current_channel'] for r in rs))
  dictionary.append({'dictionary_entry_id':k,'surfaces':','.join(dict.fromkeys(r['surface'] for r in rs)),'component_recipe':recipe,
                     'short_component_reading_de':' + '.join(cmean[a] for a in atoms),'events':str(len(rs)),'physical_pages':','.join(dict.fromkeys(r['physical_page'] for r in rs)),
                     'registers':','.join(dict.fromkeys(r['register'] for r in rs)),'channels':','.join(channels),
                     'default_rule':'COMPOSE_COMPONENTS_THEN_APPLY_PROSE_OR_OWNER_CHANNEL'})
 write('PASS924_1384_CURRENT_CARD_DICTIONARY.tsv',dictionary,list(dictionary[0]))

 # Locus edition in source order.
 loci=[];groups=defaultdict(list);locorder=[]
 for r in ledger:
  key=(r['source_page'],r['locus'])
  if key not in groups:locorder.append(key)
  groups[key].append(r)
 for page,loc in locorder:
  rs=groups[(page,loc)];seen=[]
  for r in rs:
   key=(r['current_spoken_unit'],r['current_reading_de'])
   if key not in seen:seen.append(key)
  loci.append({'physical_page':rs[0]['physical_page'],'source_page':page,'locus':loc,'register':rs[0]['register'],'usage_classes':','.join(dict.fromkeys(r['usage_class'] for r in rs)),
               'visible_owner_de':rs[0]['visible_owner_de'],'events':str(len(rs)),'surfaces':' · '.join(r['surface'] for r in rs),'recipes':' | '.join(r['component_recipe'] for r in rs),
               'spoken_units':str(len(seen)),'current_complete_reading_de':' '.join(x[1] for x in seen)})
 write('PASS924_464_CURRENT_LOCUS_EDITION.tsv',loci,list(loci[0]))

 doc=['# Pass 924 — konsolidierte 14-Seiten-Ausgabe','']
 for page in dict.fromkeys(r['physical_page'] for r in loci):
  doc += [f'## {page}','']
  for r in loci:
   if r['physical_page']==page:doc.append(f"- **{r['source_page']} / {r['locus']}** {r['current_complete_reading_de']}")
  doc.append('')
 (OUT/'PASS924_FOURTEEN_PAGE_CURRENT_EDITION.md').write_text('\n'.join(doc),encoding='utf-8')

 phrase=read(P920/'PASS920_44_PHRASE_ENCODER.tsv');write('PASS924_44_CURRENT_PHRASES.tsv',phrase,list(phrase[0]))
 manual='''# Pass 924 — kompaktes Schreiberhandbuch

## Lernstoff

- 30 produktive Bedeutungskerne mit Austauschpartnern;
- 10 kurze gelernte Werkstattwurzeln;
- 5 Adresszeichen und 11 lokale Schreibzeichen;
- 17 eindeutige Handlungsverben;
- 44 häufige Ganzphrasen;
- 19 belegte interne/q-Eintrittspaare.

## Schreiben

1. Das Bild setzt Besitzer und Sachklasse.
2. Wähle Quelle/Teil, Maß oder Portion, Handlung, Ziel/Weg, Grad und Ende.
3. Nutze eine gelernte Phrase, wenn die Kombination im 44er-Deck steht.
4. Direkt nach einem geschlossenen Feld darf die erste Phrase die q-Eintrittsform tragen.
5. Seltene Namen und lokale Klassen werden aus dem Exemplar kopiert.
6. Eine Zeile ist Raum, kein notwendiges Satzende.

## Lesen

1. Bestimme zuerst Prosa- oder Bild/Listenkanal.
2. Zerlege längste bekannte Phrase vor Einzelkernen.
3. Im Prosakanal sprich: Reihenfolge → Quelle → Menge → Posten → Grad → Handlung → Ziel → Schluss.
4. Im Bildkanal sprich dieselben Formen als Reihe, Platz, Klasse, Adresse, Index und Grad.
5. CPH heißt UMLEITEN, HO heißt TEIL, CFH heißt TRENNEN; die engere Sachausführung kommt vom Register.
'''
 (OUT/'PASS924_COMPACT_SCRIBAL_HANDBOOK.md').write_text(manual,encoding='utf-8')
 report='''# Pass 924 — neue konsolidierte Arbeitsbasis

## Stand

Die gesamte kreative 14-Seiten-Ausgabe ist neu gebaut:

- 2511 sichtbare Gruppen;
- 1384 exakte Karten;
- 464 Loci;
- 1435 flüssige Prosaarbeitszüge in 354 Klauseln;
- 56 analysierte Kerne, 17 Verben und 44 gelehrte Phrasen.

Die Ausgabe trennt konsequent zwei Lesekanäle. In Prosa werden die Komponenten als
Arbeitsanweisung gesprochen. An Figuren, Sternen, Ringen und Zutatenbildern werden
sie als Reihe, Platz, Klasse, Adresse, Index und Grad gelesen. Dadurch muss `O`
nicht gleichzeitig das Sachwort „Wasser“ und eine Sternkennung sein.

## Aktuelle konkrete Kernthese

Ein kleiner Werkstattverbund schreibt mit einer Mischung aus produktiven Kürzeln,
gelernten Ganzphrasen, q-Eintrittsallographen und exemplarisch kopierten lokalen
Namen. Die Bilder setzen den nicht ausgeschriebenen Besitzer. Pflanzenblätter
enthalten offene Stoff-/Arbeitsartikel, Biological-Blätter lokale Becken- und
Stationshandlungen, f70/f67/f68/f69 himmlische Adresslisten und f88 eine
Zutaten-/Behälterseite mit Arbeitsprosa.

## Noch nicht fest

Die eigentlichen Pflanzen-, Stern-, Figuren- und Zutatenbezeichnungen bleiben
lokale Namen/Klassen. Auch der Gesamtzweck Medizin versus allgemeine praktische
Natur-/Badewerkstatt bleibt offen. Fest innerhalb der Arbeitstheorie ist jetzt nur
die ausführbare Schreib- und Lesemaschine.

## Nächster Schritt

Als nächstes werden die längsten 30 Klauseln redaktionell in wirklich natürliche
deutsche Anweisungen umgeschrieben. Dabei darf kein Kern verschwinden; Ziel ist
eine menschlich lesbare Übersetzung, nicht noch eine neue Tabelle.
'''
 (OUT/'PASS924_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS924_2511_CURRENT_EVENT_LEDGER.tsv','PASS924_1384_CURRENT_CARD_DICTIONARY.tsv','PASS924_464_CURRENT_LOCUS_EDITION.tsv','PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv','PASS924_354_CURRENT_CLAUSES.tsv','PASS924_56_CURRENT_COMPONENTS.tsv','PASS924_17_CURRENT_VERBS.tsv','PASS924_44_CURRENT_PHRASES.tsv','PASS924_FOURTEEN_PAGE_CURRENT_EDITION.md','PASS924_COMPACT_SCRIBAL_HANDBOOK.md','PASS924_REPORT.md']
 s={'status':'BUILT','events':len(ledger),'dictionary':len(dictionary),'loci':len(loci),'instructions':len(ins),'clauses':len(clauses),'components':len(components),'verbs':len(verbs),'phrases':len(phrase),'channels':dict(Counter(r['current_channel'] for r in ledger)),'physical_pages':len({r['physical_page'] for r in ledger}),'source_pages':len({r['source_page'] for r in ledger}),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS924_BUILD_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
