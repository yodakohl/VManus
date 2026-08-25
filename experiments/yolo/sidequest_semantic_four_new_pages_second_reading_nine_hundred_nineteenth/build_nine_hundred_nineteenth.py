#!/usr/bin/env python3
"""Build Pass 919: reread the four newly admitted pages with the mature grammar."""

import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P912=ROOT/'experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth'
P917=ROOT/'experiments/yolo/sidequest_semantic_fluent_prose_nine_hundred_seventeenth'
P918=ROOT/'experiments/yolo/sidequest_semantic_minimal_verb_deck_nine_hundred_eighteenth'
PAGES=['f13r','f75r','f70v1','f70v2','f88r']

def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

LABEL={
 'OT':'nächster Platz','OL':'gleiche Reihe weiter','OS':'zusätzlicher Eintrag','RESUME_CARD':'Bezug wiederaufnehmen',
 'Y':'dieser Platz','OR':'Eintragsklasse','CHEO':'lokaler Eintrag','HO':'Objektklasse','AIIN':'verzeichneter Wert',
 'AIN':'Einheit','IIN':'Indexstufe','DA':'zweite Stufe','AR':'Quell- oder Bezugsstelle','D_ADDR':'Unterplatz',
 'A_ADDR':'lokale Adresse','AL':'Zielplatz','AM_ADDR':'Innenplatz','L':'Verbindung','CKH':'Verbindungsweg',
 'AIR':'Ringlauf','S_ADDR':'Sternbezug','Z_ADDR':'z-Stelle','O':'Reihe aufrufen','OK':'Platz aktivieren','CH':'Klassenkennung',
 'K':'Wert zuordnen','T':'Platz markieren','S':'Klassenzeichen','P':'Eintrag beginnen','CTH':'Statusklasse',
 'R':'Zustandsmarke','SH':'Bezug halten','SHED':'Endstatus','CHD':'zum nächsten Platz wechseln','CHK':'Bedingungsklasse',
 'CPH':'Gegenplatz','SOLK':'Sammelgruppe','E':'erster Grad','EE':'zweiter Grad','EEE':'voller Grad','DY':'Eintrag schließen',
 'CARRIER_Q':'q-Träger','D_LABEL':'d-Zeichen','G_LABEL':'g-Zeichen','S_LABEL':'s-Zeichen','M_LOCAL':'m-Zeichen','LOCAL_CHAR_B':'b-Zeichen',
 'LOCAL_CHAR_F':'f-Zeichen','LOCAL_CHAR_G':'g-Zeichen','LOCAL_CHAR_I':'i-Zeichen','LOCAL_CHAR_J':'j-Zeichen',
 'AN':'Zusatzklasse','CFH':'Trennklasse','LSH':'Durchlaufklasse','LD':'Bindung',
}
def label_reading(recipe,owner):
 vals=[]
 for a in recipe.split('+'):
  v=LABEL[a]
  if not vals or vals[-1]!=v:vals.append(v)
 return f"{owner}: "+', '.join(vals)+'.'

def main():
 base=[r for r in read(P912/'PASS912_2511_EVENT_INTERLINEAR.tsv') if r['source_page'] in PAGES]
 bindings={r['event_id']:r for r in read(P917/'PASS917_2010_EVENT_BINDINGS.tsv')}
 inst={r['instruction_id']:r for r in read(P918/'PASS918_1435_REVISED_INSTRUCTIONS.tsv')}
 out=[]
 for r in base:
  z=dict(r)
  if r['usage_class']=='PROSE':
   b=bindings[r['event_id']];ii=inst[b['instruction_id']]
   z.update({'reading_channel':'WORKSHOP_PROSE','spoken_unit_id':b['instruction_id'],
             'second_reading_de':ii['revised_fluent_de'],'transfer_decision':'COMPOSED_PROSE_KEEP'})
  else:
   owner=r['visible_owner_de'] if r['visible_owner_de']!='NOT_APPLICABLE' else r['owner_description_de']
   z.update({'reading_channel':'OWNER_ADDRESS_LABEL','spoken_unit_id':r['locus'],
             'second_reading_de':label_reading(r['component_recipe'],owner),
             'transfer_decision':'RING_TEXT_RECAST_AS_ADDRESS' if r['usage_class']=='RING_TEXT' else 'VISIBLE_LABEL_KEEP'})
  out.append(z)
 write('PASS919_863_EVENT_SECOND_READING.tsv',out,list(out[0]))

 loci=[]
 for page in PAGES:
  order=[];groups=defaultdict(list)
  for r in out:
   if r['source_page']!=page:continue
   if r['locus'] not in groups:order.append(r['locus'])
   groups[r['locus']].append(r)
  for loc in order:
   rs=groups[loc];seen=[]
   for r in rs:
    key=(r['spoken_unit_id'],r['second_reading_de'])
    if key not in seen:seen.append(key)
   loci.append({'source_page':page,'physical_page':rs[0]['physical_page'],'locus':loc,'usage_classes':','.join(dict.fromkeys(r['usage_class'] for r in rs)),
                'visible_owner_de':rs[0]['visible_owner_de'],'events':str(len(rs)),'surfaces':' · '.join(r['surface'] for r in rs),
                'recipes':' | '.join(r['component_recipe'] for r in rs),'spoken_units':str(len(seen)),
                'complete_second_reading_de':' '.join(x[1] for x in seen)})
 write('PASS919_144_LOCUS_SECOND_READING.tsv',loci,list(loci[0]))

 doc=['# Pass 919 — zweite Lesung der vier neuen Seiten','']
 for p in PAGES:
  title={'f70v1':'f70v1 — Widder','f70v2':'f70v2 — Fische'}.get(p,p)
  doc += [f'## {title}','']
  for x in loci:
   if x['source_page']==p:doc.append(f"- **{x['locus']}** {x['complete_second_reading_de']}")
  doc.append('')
 (OUT/'PASS919_FOUR_PAGE_COMPLETE_EDITION.md').write_text('\n'.join(doc),encoding='utf-8')

 mode=Counter(r['meaning_mode'] for r in out);channel=Counter(r['reading_channel'] for r in out)
 report=f'''# Pass 919 — Reality-Check, zweite Runde

## Umfang

Die vier neu freigegebenen physischen Seiten ergeben **863 Gruppen in 144 Loci**:
f13r 77, f75r 418, f70v 218 und f88r 150. Davon laufen {channel['WORKSHOP_PROSE']}
Gruppen durch die neue 17-Verb-Prosa und {channel['OWNER_ADDRESS_LABEL']} durch die
Besitzer-/Adresslesung.

## Wichtigste Korrektur

Der Kreistext von f70v wird nicht mehr wie Pflanzen-/Stationsprosa gesprochen.
Er verwendet dieselben Formen als **Adress- und Listenkanal**: `O` ruft eine Reihe
auf, `OK` aktiviert einen Platz, `T` markiert, `S` klassifiziert, `K` ordnet einen
Wert zu, `OT/OL` heißen nächster/gleicher Platz, und `AL/AR/AIR` geben Ziel,
Bezug und Ringlauf an. Das Bild entscheidet den Kanal.

## Was die vier Seiten der Komposition hinzufügen

- f13r verhält sich wie ein weiterer offener Pflanzen-Arbeitsartikel;
- f75r vervielfacht dieselbe Handlungsgrammatik über lokale Becken und Stationen;
- f70v zeigt, dass die Kürzel nicht bloß Sachwörter sind, sondern auch ein
  Listen-/Adressregister schreiben;
- f88r verbindet konkrete Wurzel-/Behälterbesitzer mit derselben Prosaordnung.

Die 863 Gruppen bestehen aus {mode['LEARNED_COMPONENT_RECIPE']} bereits bekannten
Kompositionen, {mode['NEW_COMPONENT_COMPOSITION']+mode['REPAIRED_COMPONENT_COMPOSITION']+mode['CPH_COMPONENT_COMPOSITION']}
neu gebauten Kompositionen, {mode['OWNER_BOUND_COMPOUND_LABEL']} bildgebundenen
Namen/Klassen und {mode['REGISTER_COMPOSITION_WITH_LOCAL_SIGN']} lokalen Zeichenformen.
Es wird keine neue lange Wortbedeutung benötigt.

## Nächster Schritt

Jetzt lohnt sich ein echtes Rückleseexperiment im lockeren Werkstattmodus: aus
deutschen Arbeitsanweisungen werden mit dem 53-Kern-/44-Phrasen-/17-Verbdeck neue
Kartenfolgen erzeugt und anschließend wieder gelesen. Wo mehrere Schreibungen
gleich gut passen, wird die einfachste Schreiberregel ausgewählt.
'''
 (OUT/'PASS919_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS919_863_EVENT_SECOND_READING.tsv','PASS919_144_LOCUS_SECOND_READING.tsv','PASS919_FOUR_PAGE_COMPLETE_EDITION.md','PASS919_REPORT.md']
 summary={'status':'BUILT','events':len(out),'loci':len(loci),'channels':dict(channel),'meaning_modes':dict(mode),'pages':dict(Counter(r['source_page'] for r in out)),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS919_BUILD_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
