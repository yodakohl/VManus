#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent
B924=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
B931=H.parent/'sidequest_semantic_bilevel_component_dictionary_nine_hundred_thirty_first'
B935=H.parent/'sidequest_semantic_atomic_pocket_lexicon_nine_hundred_thirty_fifth'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

events=read(B924/'PASS924_2511_CURRENT_EVENT_LEDGER.tsv')
bi={r['component']:r for r in read(B931/'PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv')}
atom={r['component']:r['atomic_pocket_value_de'] for r in read(B935/'PASS935_56_ATOMIC_POCKET_LEXICON.tsv')}
by=defaultdict(list)
for r in events:by[r['surface']].append(r)
rows=[]
for surface,rr in by.items():
 recipes={r['component_recipe'] for r in rr};assert len(recipes)==1
 recipe=next(iter(recipes));cs=recipe.split('+')
 channels=sorted({r['current_channel'] for r in rr})
 rows.append({'surface':surface,'component_recipe':recipe,'atomic_pocket_gloss_de':' + '.join(atom[c] for c in cs),'workshop_composition_de':'; '.join(bi[c]['workshop_prose_de'] for c in cs),'image_composition_de':'; '.join(bi[c]['owner_address_de'] for c in cs),'events':len(rr),'physical_pages':'|'.join(sorted({r['physical_page'] for r in rr})),'registers':'|'.join(sorted({r['register'] for r in rr})),'observed_channels':'|'.join(channels),'channel_class':'BICHANNEL' if len(channels)==2 else ('PROSE_ONLY' if channels==['WORKSHOP_PROSE'] else 'IMAGE_ONLY'),'event_ids':'|'.join(r['event_id'] for r in rr),'visible_owner_examples':'|'.join(dict.fromkeys(r['visible_owner_de'] for r in rr))})
rows.sort(key=lambda r:(-int(r['events']),r['surface']))
write('PASS936_1078_COMPLETE_SURFACE_DICTIONARY.tsv',list(rows[0]),rows)
classes=Counter(r['channel_class'] for r in rows)
doc=['# Pass 936 — vollständiges Oberflächenwörterbuch','',
     'Die ersten 200 Einträge sind nach Häufigkeit geordnet. Die vollständigen 1.078 Einträge stehen im TSV. Jede Oberfläche hat genau ein Komponentenrezept, aber je nach Register eine Werkstatt- oder Bildexpansion.','']
for r in rows[:200]:
 doc += [f"## `{r['surface']}` — {r['atomic_pocket_gloss_de']}",'',f"Rezept `{r['component_recipe']}`; Werkstatt: **{r['workshop_composition_de']}**; Bild: **{r['image_composition_de']}**. {r['events']}× auf {r['physical_pages']} ({r['channel_class']}).",'']
(H/'PASS936_SURFACE_DICTIONARY_TOP200.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report=f"""# Pass 936 — unser gesamtes aktuelles Wörterbuch

## Ergebnis

Die 2.511 Gruppen verwenden 1.078 verschiedene sichtbare Oberflächen. Jede
dieser Oberflächen hat im aktuellen 14-Seiten-System genau ein Komponentenrezept.
Das Wörterbuch enthält {classes['BICHANNEL']} Oberflächen in beiden Kanälen,
{classes['PROSE_ONLY']} nur in Werkstattprosa und {classes['IMAGE_ONLY']} nur
als Bild-/Diagrammkarte.

Jede Zeile zeigt:

`Oberfläche → Komponentenrezept → atomare Einwortglosse → Werkstattlesung → Bildlesung`.

Damit ist das Wörterbuch nicht mehr eine Liste frei erfundener langer
Übersetzungen. Eine Oberfläche wie `okedy` wird stabil als
`OK+E+DY = START+KURZ+ENDE` gespeichert. Erst ihr Ort macht daraus „kurz
ansetzen und schließen“ oder „Platz ersten Grades aktivieren und Eintrag
schließen“.

## Praktischer Nutzen

Bei einer später freigegebenen Seite kann jede bekannte Oberfläche sofort
nachgeschlagen werden. Eine neue Oberfläche wird zuerst gegen die 56 Stammwerte
zerlegt; nur ein wirklich neuer Rest braucht eine neue gelernte Karte.
"""
(H/'PASS936_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS936_1078_COMPLETE_SURFACE_DICTIONARY.tsv','PASS936_SURFACE_DICTIONARY_TOP200.md','PASS936_REPORT.md']
(H/'PASS936_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','surfaces':len(rows),'events':sum(int(r['events']) for r in rows),'classes':dict(classes),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
