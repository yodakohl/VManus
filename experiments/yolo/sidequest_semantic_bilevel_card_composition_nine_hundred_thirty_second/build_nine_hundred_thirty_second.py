#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent
B924=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
B931=H.parent/'sidequest_semantic_bilevel_component_dictionary_nine_hundred_thirty_first'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

components=read(B931/'PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv');comp={r['component']:r for r in components}
cards=read(B924/'PASS924_1384_CURRENT_CARD_DICTIONARY.tsv');events=read(B924/'PASS924_2511_CURRENT_EVENT_LEDGER.tsv')
outcards=[]
for r in cards:
 cs=r['component_recipe'].split('+')
 abstract=' → '.join(comp[c]['abstract_core_de'] for c in cs)
 prose='; '.join(comp[c]['workshop_prose_de'] for c in cs)
 address='; '.join(comp[c]['owner_address_de'] for c in cs)
 outcards.append({'dictionary_entry_id':r['dictionary_entry_id'],'surfaces':r['surfaces'],'component_recipe':r['component_recipe'],'abstract_composition_de':abstract,'workshop_prose_composition_de':prose,'owner_address_composition_de':address,'observed_events':r['events'],'physical_pages':r['physical_pages'],'registers':r['registers'],'observed_channel':r['channels'],'observed_channel_reading_de':prose if r['channels']=='WORKSHOP_PROSE' else address,'composition_status':'FULLY_COMPOSED_NO_NEW_WHOLE_GLOSS'})
write('PASS932_1384_BILEVEL_CARD_DICTIONARY.tsv',list(outcards[0]),outcards)
cardmap={r['dictionary_entry_id']:r for r in outcards};oute=[]
for e in events:
 d=cardmap[e['dictionary_entry_id']]
 reading=d['workshop_prose_composition_de'] if e['current_channel']=='WORKSHOP_PROSE' else d['owner_address_composition_de']
 oute.append({'event_id':e['event_id'],'dictionary_entry_id':e['dictionary_entry_id'],'physical_page':e['physical_page'],'locus':e['locus'],'surface':e['surface'],'channel':e['current_channel'],'visible_owner_de':e['visible_owner_de'],'component_recipe':e['component_recipe'],'abstract_composition_de':d['abstract_composition_de'],'register_composition_de':reading,'current_fluent_or_address_de':e['current_reading_de']})
write('PASS932_2511_COMPOSED_EVENT_READINGS.tsv',list(oute[0]),oute)

# Surface families that visibly occur in both channels illustrate the expansion rule.
by_surface={}
for e in oute:
 for s in e['surface'].split('|'):
  by_surface.setdefault(s,[]).append(e)
examples=[]
for s,rr in by_surface.items():
 ch={r['channel'] for r in rr}
 if len(ch)<2:continue
 p=next(r for r in rr if r['channel']=='WORKSHOP_PROSE');a=next(r for r in rr if r['channel']=='OWNER_ADDRESS_OR_DIAGRAM')
 examples.append({'surface':s,'events':len(rr),'pages':'|'.join(sorted({r['physical_page'] for r in rr})),'prose_recipe':p['component_recipe'],'prose_reading_de':p['register_composition_de'],'address_recipe':a['component_recipe'],'address_reading_de':a['register_composition_de'],'shared_abstract_if_same_recipe':p['abstract_composition_de'] if p['component_recipe']==a['component_recipe'] else 'SURFACE_ALLOGRAPH_RECIPES_DIFFER'})
examples.sort(key=lambda r:(-int(r['events']),r['surface']))
write('PASS932_CROSS_CHANNEL_SURFACE_EXAMPLES.tsv',list(examples[0]),examples)

doc=['# Pass 932 — vollständiges kompositionelles Kartenwörterbuch','',
     'Jede der 1.384 Karten wird aus den 56 zweistufigen Komponenten gelesen. Die Bild- und Werkstattspalte sind Vorhersagen aus demselben abstrakten Rezept; die beobachtete Kanalspalte entscheidet, welche davon im jeweiligen Ereignis gesprochen wird.','']
for r in outcards[:120]:
 doc += [f"## {r['dictionary_entry_id']} — {r['surfaces']}",'',f"Rezept: `{r['component_recipe']}`. Kern: {r['abstract_composition_de']}. Werkstatt: {r['workshop_prose_composition_de']}. Bild: {r['owner_address_composition_de']}.",'']
doc += ['## Vollständige Tabelle','', 'Alle 1.384 Einträge stehen in `PASS932_1384_BILEVEL_CARD_DICTIONARY.tsv`.','']
(H/'PASS932_CARD_DICTIONARY_EXCERPT.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report=f"""# Pass 932 — Karten werden wieder aus Stämmen gebaut

## Ergebnis

Alle 1.384 exakten Karten und alle 2.511 sichtbaren Ereignisse erhalten ihre
Lesung jetzt mechanisch aus dem 56-Komponenten-Wörterbuch. Es wird keine neue
satzlange Ganzwortbedeutung eingeführt. {len(examples)} sichtbare
Oberflächenfamilien kommen in beiden Kanälen vor und zeigen die
Registerumschaltung unmittelbar.

## Beispielprinzip

`OK + E + DY` bedeutet abstrakt `AKTIVIEREN → GRAD_1 → ABSCHLUSS`.
In der Werkstatt wird daraus „kurz ansetzen; Schritt schließen“, im Bildregister
„Platz aktivieren; erster Grad; Eintrag schließen“. Die Karte bleibt
kompositionell gleich, nur ihre konkrete Domäne wechselt.

`O + ...` verhält sich ebenso: Arbeitsgang ausführen oder Bildreihe aufrufen.
`K` gibt Stoff zu oder ordnet einen Wert zu. `CH` entnimmt einen Anteil oder
kennzeichnet eine Klasse. Diese Regel erklärt, warum dieselben Oberflächen in
Pflanzenprosa und Himmelsrädern nicht dieselben langen deutschen Sätze meinen.
"""
(H/'PASS932_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS932_1384_BILEVEL_CARD_DICTIONARY.tsv','PASS932_2511_COMPOSED_EVENT_READINGS.tsv','PASS932_CROSS_CHANNEL_SURFACE_EXAMPLES.tsv','PASS932_CARD_DICTIONARY_EXCERPT.md','PASS932_REPORT.md']
(H/'PASS932_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','cards':len(outcards),'events':len(oute),'cross_channel_surfaces':len(examples),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
