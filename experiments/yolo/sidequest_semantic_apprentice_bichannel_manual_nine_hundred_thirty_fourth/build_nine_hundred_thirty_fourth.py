#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
B=H.parent/'sidequest_semantic_bilevel_card_composition_nine_hundred_thirty_second'

def read(n):
 with (B/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

RULES=[
('R01','BILD_ZUERST','Bestimme zuerst, welches Bild, Gefäß, Becken oder Rad den Eintrag besitzt.'),
('R02','KANAL','Laufender Text spricht Werkstattprosa; eine Karte unmittelbar an Figur oder Ring spricht Adresse.'),
('R03','REZEPT','Zerlege die Karte in ihre gelernte Komponentenfolge; ändere die Reihenfolge nicht.'),
('R04','REFERENT','Y hält den aktuellen Arbeitsgegenstand oder Bildplatz aktiv.'),
('R05','ABSCHLUSS','Eine lizenzierte DY-Karte schließt Arbeitsschritt oder Bildeintrag.'),
('R06','GRAD','E, EE und EEE geben ersten, zweiten und vollen Grad.'),
('R07','LAUF','O ruft einen Lauf auf: Arbeitsgang in Prosa, Bildreihe im Diagramm.'),
('R08','AKTIVIEREN','OK aktiviert: Arbeitsgang ansetzen oder Bildplatz öffnen.'),
('R09','AUSWAHL','CH wählt den relevanten Teil; in Prosa wird er entnommen, im Bild als Klasse gekennzeichnet.'),
('R10','ZUORDNUNG','K ordnet zu: Stoff zugeben oder Bildwert eintragen.'),
('R11','RICHTUNG','AR ist Quelle, AL Ziel, L Verbindung und AIR der jeweilige Laufweg.'),
('R12','MENGE','AIN ist Einheit, AIIN Sollwert und IIN Stufe.'),
('R13','REIHENFOLGE','OL setzt dieselbe Reihe fort; OT wechselt zum nächsten Posten.'),
('R14','EINTRITTSFORM','q ist eine Eintrittsform am Karten- oder Feldanfang, kein zusätzliches Sachwort.'),
('R15','ALLOGRAPH','Wähle die gelernte Oberflächenform nach Stelle und Hand, behalte aber dasselbe Komponentenrezept.'),
('R16','RUECKLESEN','Lies zuerst den abstrakten Kern, dann ergänze die Sachwörter aus Register und Bildbesitzer.'),
]
rules=[{'rule_id':a,'short_name':b,'apprentice_rule_de':c} for a,b,c in RULES]
write('PASS934_16_APPRENTICE_RULES.tsv',list(rules[0]),rules)

examples=read('PASS932_CROSS_CHANNEL_SURFACE_EXAMPLES.tsv')[:30]
ex=[]
for i,r in enumerate(examples,1):
 ex.append({'exercise_id':f'P934-X{i:02d}','surface':r['surface'],'component_recipe':r['prose_recipe'],'abstract_core_de':r['shared_abstract_if_same_recipe'],'workshop_scene_prompt_de':'Die Karte steht in einem laufenden Arbeitsfeld.','workshop_reading_de':r['prose_reading_de'],'diagram_scene_prompt_de':'Dieselbe Karte steht unmittelbar an Figur, Ring oder Station.','diagram_reading_de':r['address_reading_de'],'apprentice_decision_de':'Oberfläche und Rezept bleiben gleich; nur die registergebundene Expansion wechselt.'})
write('PASS934_30_BICHANNEL_EXERCISES.tsv',list(ex[0]),ex)

manual=['# Pass 934 — Lehrblatt der kleinen Schreiberwerkstatt','',
        '## Die sechzehn Regeln','']
for r in rules:manual += [f"{r['rule_id']}. **{r['short_name']}** — {r['apprentice_rule_de']}",'']
manual += ['## Dreißig Doppelübungen','']
for r in ex:manual += [f"### {r['surface']} = {r['component_recipe']}",'',f"Werkstatt: **{r['workshop_reading_de']}**",'',f"Bild: **{r['diagram_reading_de']}**",'']
(H/'PASS934_COMPACT_APPRENTICE_MANUAL.md').write_text('\n'.join(manual).rstrip()+'\n',encoding='utf-8')
report=f"""# Pass 934 — so könnte ein Schreiber das System lernen

## Ergebnis

Sechzehn kurze Regeln und dreißig Doppelübungen genügen, um die zentrale
Registerumschaltung praktisch zu lehren. Jede Übung benutzt eine wirklich in
beiden Kanälen sichtbare Oberfläche mit demselben Komponentenrezept.

Beispiele:

- `daiin = AIIN`: Sollmaß im Arbeitsfeld, verzeichneter Sollwert am Bild;
- `dal = AL`: Ziel-/Anschlussstelle im Arbeitsfeld, Zielplatz am Bild;
- `chedy = CHD+Y`: diesen Posten umsetzen / zu diesem Bildplatz wechseln;
- `okedy = OK+E+DY`: kurz ansetzen und schließen / Platz ersten Grades
  aktivieren und Eintrag schließen.

## Werkstattplausibilität

Der Lehrling braucht keine unbekannte Lautsprache zu entziffern. Er lernt ein
kleines Kartenrepertoire, eine feste Komponentenreihenfolge, einige
Positionsallographe und die Regel „Bild bestimmt das Sachgebiet“. Neue lokale
Namen werden aus dem Exemplar kopiert; produktive Arbeitskarten kann er selbst
zusammensetzen.
"""
(H/'PASS934_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS934_16_APPRENTICE_RULES.tsv','PASS934_30_BICHANNEL_EXERCISES.tsv','PASS934_COMPACT_APPRENTICE_MANUAL.md','PASS934_REPORT.md']
(H/'PASS934_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','rules':len(rules),'exercises':len(ex),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
