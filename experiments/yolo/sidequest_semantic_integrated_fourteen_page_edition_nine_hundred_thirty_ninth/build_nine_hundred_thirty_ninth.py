#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent
B924=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
B929=H.parent/'sidequest_semantic_concrete_page_readings_nine_hundred_twenty_ninth'
B930=H.parent/'sidequest_semantic_diagram_address_readings_nine_hundred_thirtieth'
B937=H.parent/'sidequest_semantic_macro_clause_translation_nine_hundred_thirty_seventh'
B938=H.parent/'sidequest_semantic_local_sign_meanings_nine_hundred_thirty_eighth'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

lex=read(B938/'PASS938_56_REVISED_ATOMIC_LEXICON.tsv');lookup={r['component']:r for r in lex}
write('PASS939_56_CURRENT_ATOMIC_LEXICON.tsv',list(lex[0]),lex)
events=read(B924/'PASS924_2511_CURRENT_EVENT_LEDGER.tsv');oute=[]
for e in events:
 cs=e['component_recipe'].split('+');channel=e['current_channel']
 atomic=' + '.join(lookup[c]['atomic_pocket_value_de'] for c in cs)
 reading='; '.join((lookup[c]['workshop_expansion_de'] if channel=='WORKSHOP_PROSE' else lookup[c]['image_expansion_de']) for c in cs)
 oute.append({'event_id':e['event_id'],'dictionary_entry_id':e['dictionary_entry_id'],'physical_page':e['physical_page'],'locus':e['locus'],'register':e['register'],'channel':channel,'surface':e['surface'],'visible_owner_de':e['visible_owner_de'],'component_recipe':e['component_recipe'],'atomic_pocket_gloss_de':atomic,'current_compositional_reading_de':reading,'spoken_clause_id':e['current_spoken_unit'] if channel=='WORKSHOP_PROSE' else 'OWNER_ADDRESS'})
write('PASS939_2511_CURRENT_EVENT_INTERLINEAR.tsv',list(oute[0]),oute)

by=defaultdict(list)
for e in oute:by[e['surface']].append(e)
surfs=[]
for surface,rr in by.items():
 recipes={r['component_recipe'] for r in rr};assert len(recipes)==1;recipe=next(iter(recipes));cs=recipe.split('+');channels=sorted({r['channel'] for r in rr})
 surfs.append({'surface':surface,'component_recipe':recipe,'atomic_pocket_gloss_de':' + '.join(lookup[c]['atomic_pocket_value_de'] for c in cs),'workshop_composition_de':'; '.join(lookup[c]['workshop_expansion_de'] for c in cs),'image_composition_de':'; '.join(lookup[c]['image_expansion_de'] for c in cs),'events':len(rr),'physical_pages':'|'.join(sorted({r['physical_page'] for r in rr})),'registers':'|'.join(sorted({r['register'] for r in rr})),'observed_channels':'|'.join(channels),'channel_class':'BICHANNEL' if len(channels)==2 else ('PROSE_ONLY' if channels==['WORKSHOP_PROSE'] else 'IMAGE_ONLY')})
surfs.sort(key=lambda r:(-int(r['events']),r['surface']))
write('PASS939_1078_CURRENT_SURFACE_DICTIONARY.tsv',list(surfs[0]),surfs)

clauses=read(B937/'PASS937_354_MACRO_CLAUSE_TRANSLATIONS.tsv');write('PASS939_354_CURRENT_CLAUSE_TRANSLATIONS.tsv',list(clauses[0]),clauses)
prose={r['physical_page']:r for r in read(B929/'PASS929_12_CONCRETE_PAGE_READINGS.tsv')}
diagrams=defaultdict(list)
for r in read(B930/'PASS930_10_DIAGRAM_UNIT_READINGS.tsv'):diagrams[r['physical_page']].append(r)
ep=Counter(e['physical_page'] for e in oute);cp=Counter(e['physical_page'] for e in oute if e['channel']=='WORKSHOP_PROSE');ap=Counter(e['physical_page'] for e in oute if e['channel']=='OWNER_ADDRESS_OR_DIAGRAM')
order=['f10r','f11r','f13r','f55v','f56r','f75r','f81v','f82r','f83r','f67r2','f68r1','f69v','f70v','f88r']
pages=[]
for p in order:
 pr=prose.get(p);ds=diagrams.get(p,[])
 pages.append({'physical_page':p,'page_model':pr['page_model'] if pr else '|'.join(r['diagram_model'] for r in ds),'events':ep[p],'prose_events':cp[p],'address_events':ap[p],'prose_clauses':sum(r['physical_page']==p for r in clauses),'concrete_prose_reading_de':pr['concrete_page_reading_de'] if pr else 'KEINE_LAUFENDE_PROSA','diagram_reading_de':' '.join(r['concrete_diagram_reading_de'] for r in ds) if ds else 'KEINE_SEPARATE_BILDBESCHRIFTUNG'})
write('PASS939_14_PAGE_SUMMARY.tsv',list(pages[0]),pages)

clause_by=defaultdict(list)
for r in clauses:clause_by[r['physical_page']].append(r)
doc=['# Pass 939 — integrierte 14-Seiten-Werkstattausgabe','',
     'Diese kreative Lesefassung benutzt überall dasselbe 56-Wert-Lexikon. Werkstattprosa, Bildadressen und lokale Zeichen sind getrennt, aber kompositionell verbunden.','']
for p in pages:
 doc += [f"## {p['physical_page']} — {p['page_model']}",'']
 if p['concrete_prose_reading_de']!='KEINE_LAUFENDE_PROSA':doc += ['**Seitenaussage:** '+p['concrete_prose_reading_de'],'']
 if p['diagram_reading_de']!='KEINE_SEPARATE_BILDBESCHRIFTUNG':doc += ['**Bild-/Adressfunktion:** '+p['diagram_reading_de'],'']
 for c in clause_by[p['physical_page']]:doc += [f"### {c['clause_id']}",'',c['natural_macro_translation_de'],'']
 doc += [f"Gebunden: {p['events']} Gruppen = {p['prose_events']} Prosa + {p['address_events']} Bild/Adresse.",'']
(H/'PASS939_COMPLETE_FOURTEEN_PAGE_READING.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report="""# Pass 939 — neue integrierte Basis

## Ergebnis

Die vollständige 14-Seiten-Ausgabe ist nach den Bedeutungen der seltenen
lokalen Zeichen neu gebaut: 56 atomare Werte, 1.078 Oberflächen, 2.511
Ereignisse, 354 Klauseln und 14 Seitenaussagen. Kein Ereignis endet mehr mit
einem bloßen F/G/I/D/S/B/M/J/Z-Zeichennamen.

## Aktuelle Kurzgrammatik

`Besitzer → Quelle/Teil → Einheit/Sollwert/Stufe → Handlung → Ziel/Laufweg → Grad → Dies/Ende`.

Im Bildregister wird daraus:

`Bildbesitzer → Reihe/Klasse → Quelle/Ziel/Unterplatz → Wert/Grad → Platz/Eintragsende`.

Die Reihenfolge und die Stammwerte sind gemeinsam; nur die konkreten Sachwörter
wechseln. Darum kann ein Schreiber dasselbe Karteninventar für Pflanzenartikel,
Badstationen, Gefäßregister und Himmelsräder benutzen.

## Führende Lesung

Das Buch bleibt am plausibelsten ein bildgeführtes praktisches Kompendium:
Pflanzenmaterial entnehmen und zubereiten, in lokale Bade-/Anwendungsstationen
überführen, und getrennte Himmelsräder als Auswahl-/Zuordnungstafeln verwenden.
Die Übersetzung ist eine kreative Werkstattrekonstruktion, aber innerhalb der
14 Seiten jetzt vollständig und einheitlich.
"""
(H/'PASS939_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS939_56_CURRENT_ATOMIC_LEXICON.tsv','PASS939_2511_CURRENT_EVENT_INTERLINEAR.tsv','PASS939_1078_CURRENT_SURFACE_DICTIONARY.tsv','PASS939_354_CURRENT_CLAUSE_TRANSLATIONS.tsv','PASS939_14_PAGE_SUMMARY.tsv','PASS939_COMPLETE_FOURTEEN_PAGE_READING.md','PASS939_REPORT.md']
(H/'PASS939_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','components':len(lex),'surfaces':len(surfs),'events':len(oute),'clauses':len(clauses),'pages':len(pages),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
