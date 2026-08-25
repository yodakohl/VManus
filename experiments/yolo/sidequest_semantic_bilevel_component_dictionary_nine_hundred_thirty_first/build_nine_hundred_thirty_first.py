#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
B=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'

def read(n):
 with (B/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

# Abstrakter Kern, Werkstattlesung, Bild-/Adresslesung.
X={
'Y':('REFERENT','dieser Arbeitsgegenstand','dieser Bildplatz'),
'OK':('AKTIVIEREN','Arbeitsgang ansetzen','Bildplatz aktivieren'),
'E':('GRAD_1','kurz oder direkt','erster Grad'),
'DY':('ABSCHLUSS','Arbeitsschritt schließen','Bildeintrag schließen'),
'O':('LAUF','Arbeitsgang ausführen','Reihe aufrufen'),
'OL':('FORTSETZUNG','im selben Arbeitsgang fortfahren','dieselbe Reihe fortführen'),
'EE':('GRAD_2','länger oder gehalten','zweiter Grad'),
'OT':('NAECHSTER','danach oder nächster Posten','nächster Bildplatz'),
'AL':('ZIEL','Ziel- oder Anschlussstelle','Zielplatz'),
'CH':('AUSWAHL_ENTNAHME','bezeichneten Anteil entnehmen','Klasse oder Figur kennzeichnen'),
'D_ADDR':('UNTERADRESSE','bezeichneter Teil','Unterplatz'),
'SH':('HALTEN','Arbeitsgegenstand halten','Bezug festhalten'),
'AR':('QUELLE','Entnahmestelle','Quell- oder Bezugsstelle'),
'K':('ZUORDNUNG','Material zugeben','Wert zuordnen'),
'AIIN':('SOLLWERT','Sollmaß','verzeichneter Sollwert'),
'S':('AUSWAHL','Arbeitsvariante auswählen','Bildklasse auswählen'),
'CHD':('WECHSEL','Arbeitsgut umsetzen','zu Gegen- oder Folgeplatz wechseln'),
'OR':('EINTRAG','Ansatz oder Zubereitung','Eintragsklasse'),
'L':('VERBINDUNG','entlang des Arbeitswegs führen','Bildverbindung'),
'T':('EINSTELLUNG','Arbeitsgang einstellen','Platz oder Wert einstellen'),
'AIN':('EINHEIT','Portion','Einheit oder Index'),
'R':('MARKE','Zustand kennzeichnen','Zustandsmarke'),
'P':('EINSETZUNG','Material einsetzen','Platz besetzen'),
'CTH':('BEREITSTATUS','bis bereit führen','Bereitschaftsklasse'),
'SHED':('ABSETZUNG','absetzen lassen','Absetzklasse'),
'CKH':('DURCHLASS','durch einen Durchlass führen','Verbindung oder Durchlass'),
'AM_ADDR':('INNENADRESSE','Innenstelle','Innenplatz'),
'CHEO':('LOKALINHALT','Auszug','lokaler Eintrag'),
'DA':('STUFE_2','zweite Arbeitsstufe','zweite Bildstufe'),
'CARRIER_Q':('EINTRITT','neuen Kartenblock beginnen','Eintrittsform einer Bildkarte'),
'A_ADDR':('ADRESSE','lokale Arbeitsstelle','lokale Bildadresse'),
'AIR':('LAUFWEG','Flüssigkeits- oder Stationslauf','Ringlauf'),
'CHK':('BEHANDLUNG','Arbeitsgegenstand behandeln','Behandlungsklasse'),
'IIN':('STUFE','Arbeitsstufe','Wertstufe'),
'S_ADDR':('STERNADRESSE','bezeichnete s-Stelle','Stern- oder s-Stelle'),
'SOLK':('SAMMELSTELLE','auffangen','Sammelstelle'),
'EEE':('GRAD_3','vollständig','dritter oder voller Grad'),
'LSH':('SPUELUNG','spülen','Spülklasse'),
'CPH':('GEGENLAUF','umleiten','Gegenplatz'),
'HO':('TEIL','Teil des sichtbaren Gegenstands','Teil oder Mitglied der Bildklasse'),
'AN':('ZUSATZ','weiteren Posten zugeben','zusätzlicher Eintrag'),
'CFH':('TRENNUNG','trennen','Trennklasse'),
'OS':('ADDITION','dazu oder außerdem','zusätzlicher Bildposten'),
'LD':('BEFESTIGUNG','befestigen','Befestigungsstelle'),
'RESUME_CARD':('WIEDERAUFNAHME','vorigen Posten wieder aufnehmen','vorigen Bildbezug wieder aufnehmen'),
}

components=read('PASS924_56_CURRENT_COMPONENTS.tsv');events=read('PASS924_2511_CURRENT_EVENT_LEDGER.tsv')
chan=defaultdict(Counter)
for r in events:
 for c in r['component_recipe'].split('+'):chan[c][r['current_channel']]+=1

dictionary=[]
for r in components:
 c=r['component']
 if c in X:abstract,prose,address=X[c]
 elif r['shelf']=='FORMAL_ADDRESS_SIGN':abstract,prose,address=('LOKALE_ADRESSE',r['fixed_default_de'].lower(),r['fixed_default_de'].lower())
 elif r['shelf']=='LOCAL_WRITING_SIGN':abstract,prose,address=(r['fixed_default_de'].replace('-ZEICHEN',''),'lokales Schreibzeichen','lokales Bildzeichen')
 else:abstract,prose,address=(r['fixed_default_de'].replace('/','_'),r['fixed_default_de'].lower(),r['fixed_default_de'].lower())
 pc=chan[c]['WORKSHOP_PROSE'];ac=chan[c]['OWNER_ADDRESS_OR_DIAGRAM']
 dictionary.append({'component':c,'shelf':r['shelf'],'abstract_core_de':abstract,'workshop_prose_de':prose,'owner_address_de':address,'prose_atom_occurrences':pc,'address_atom_occurrences':ac,'total_atom_occurrences':pc+ac,'channel_status':'BIVALENT' if pc and ac else ('PROSE_ONLY' if pc else 'ADDRESS_ONLY'),'composition_rule_de':f'{abstract} bleibt invariant; das Register erweitert zu „{prose}“ oder „{address}“.'})
write('PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv',list(dictionary[0]),dictionary)
lookup={r['component']:r for r in dictionary};atoms=[];aid=0
for e in events:
 for pos,c in enumerate(e['component_recipe'].split('+'),1):
  aid+=1;d=lookup[c]
  expansion=d['workshop_prose_de'] if e['current_channel']=='WORKSHOP_PROSE' else d['owner_address_de']
  atoms.append({'atom_id':f'P931-A{aid:05d}','event_id':e['event_id'],'physical_page':e['physical_page'],'locus':e['locus'],'surface':e['surface'],'channel':e['current_channel'],'component_position':pos,'component':c,'abstract_core_de':d['abstract_core_de'],'register_expansion_de':expansion})
write('PASS931_6513_COMPONENT_ATOMS.tsv',list(atoms[0]),atoms)

book=['# Pass 931 — gemeinsamer Kern und Registerbedeutung','',
      'Jeder Eintrag hat genau zwei Ebenen: einen kurzen gemeinsamen Kern und eine konkrete Lesung im Werkstatt- beziehungsweise Bildregister. So bleibt die Komposition vorhersagbar, ohne AIR im Tierkreis zu Wasser oder CH in einem Bildlabel zu einer Entnahmehandlung zu zwingen.','']
for r in dictionary:
 book += [f"## {r['component']} — {r['abstract_core_de']}",'',f"Werkstatt: **{r['workshop_prose_de']}**. Bild/Diagramm: **{r['owner_address_de']}**. ({r['prose_atom_occurrences']} + {r['address_atom_occurrences']} Atome)",'']
(H/'PASS931_BILEVEL_DICTIONARY.md').write_text('\n'.join(book).rstrip()+'\n',encoding='utf-8')
bi=sum(r['channel_status']=='BIVALENT' for r in dictionary)
report=f"""# Pass 931 — ein einziges Wörterbuch für beide Register

## Ergebnis

Die 56 Komponenten besitzen jetzt je einen kurzen abstrakten Kern sowie je eine
Werkstatt- und Bildlesung. {bi} Komponenten kommen tatsächlich in beiden
Kanälen vor. Alle {len(atoms)} Komponentenatome der 2.511 sichtbaren Gruppen
sind an diese zweistufige Lesung gebunden.

## Die wichtigsten gemeinsamen Kerne

- `O = LAUF`: Werkstattgang ausführen / Bildreihe aufrufen;
- `OK = AKTIVIEREN`: Arbeitsgang ansetzen / Bildplatz aktivieren;
- `CH = AUSWAHL_ENTNAHME`: Anteil entnehmen / Klasse kennzeichnen;
- `K = ZUORDNUNG`: Material zugeben / Wert zuordnen;
- `AIR = LAUFWEG`: Flüssigkeits- oder Stationslauf / Ringlauf;
- `AL = ZIEL`, `AR = QUELLE`, `Y = REFERENT` funktionieren in beiden Registern
  beinahe wörtlich gleich.

## Konsequenz

Das System braucht weder zwei unabhängige Sprachen noch satzlange
Wortbedeutungen. Ein kleines abstraktes Karteninventar wird im jeweiligen
Register konkretisiert. Genau diese Mischung aus produktiver Kurznotation und
lokal gelernten Karten ist derzeit unsere stärkste Schreiberhypothese.
"""
(H/'PASS931_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv','PASS931_6513_COMPONENT_ATOMS.tsv','PASS931_BILEVEL_DICTIONARY.md','PASS931_REPORT.md']
(H/'PASS931_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','components':len(dictionary),'atoms':len(atoms),'bivalent_components':bi,'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
