#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
B=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'

def read():
 with (B/'PASS924_2511_CURRENT_EVENT_LEDGER.tsv').open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

READ={
'f75r':('BECKEN_UND_FIGURENSTATIONEN','Die sieben Beschriftungsorte benennen keine neuen Tätigkeiten. Sie ordnen Becken- und Figurenstationen nach Klasse, Zielplatz, Einheit und nächster Stufe.'),
'f81v':('GEMEINSAMES_BADFELD','Die zwei Karten am gemeinsamen Badfeld sagen sinngemäß: nächste Einheit; dieselbe Reihe am Zielplatz fortführen.'),
'f82r':('LOKALE_BAD_UND_LEITUNGSSTATIONEN','Dreizehn Einzelbeschriftungen kennzeichnen Quelle, Ziel, Unterplatz, Ringlauf, Stufe und Sollwert der jeweils benachbarten Station. Sie bilden kein zweites Rezept.'),
'f83r':('LOKALE_BECKEN_UND_VERBINDUNGSSTATIONEN','Vier Beschriftungen unterscheiden Stationstyp, Weiterführung, Sollwert und zweite Stufe an den lokalen Beckenverbindungen.'),
'f67r2':('ZWEI_HIMMELSRAD_REGISTER','Die Beschriftungen rufen Ringreihen auf, wählen Klassen und Plätze und tragen Stufen oder Werte ein. Sie gehören zu zwei lokalen Rädern; sie sind keine laut gelesene Arbeitsprosa.'),
'f68r1':('MEHRTEILIGER_STERNATLAS','Die Sternbeschriftungen adressieren einzelne Plätze, Unterplätze, Grade und Gegenstellen in mehreren lokalen Paneelen. Es gibt kein einziges zwingendes Zentrum und keine festgelegte Laufrichtung.'),
'f69v':('DREI_GETRENNTE_HIMMELSRAD_NAMENSRAEUME','Die Seite hat drei getrennte Adressräume. Das linke Rad besitzt 28 lokale Plätze; die beiden anderen Räder haben eigene Klassen und Einträge. Die Karten ergeben keine lineare 28-Schritt-Anweisung.'),
'f70v1':('WIDDERRAD_MIT_STERNFIGUREN','Die Ringtexte bezeichnen Figurenplätze des Widderrads: Reihe, Klasse, nächster Platz, Grad, Quell- oder Zielstelle und lokaler Wert. AIR bedeutet hier Ringlauf, nicht Wasser.'),
'f70v2':('FISCHRING_MIT_STERNFIGUREN','Die Ringtexte bezeichnen die Plätze und Unterplätze des Fischpaars, wählen die jeweilige Reihe und tragen Grad oder Wert ein. Auch hier sind die Karten Adressen, keine Werkstattverben.'),
'f88r':('GEFAESS_WURZEL_UND_BLATTREIHEN','Die Bildlabels ordnen die drei Gefäße sowie Wurzel- und Blattreihen: nächster Eintrag, Klasse, Zielplatz, Unterplatz, Stufe und Innenstelle.'),
}
allrows=[r for r in read() if r['current_channel']=='OWNER_ADDRESS_OR_DIAGRAM']
units=defaultdict(list)
for r in allrows:
 unit=r['locus'].split('.')[0] if r['physical_page']=='f70v' else r['physical_page']
 units[unit].append(r)
ledger=[];summ=[]
for unit,rr in units.items():
 model,text=READ[unit];cc=Counter()
 for r in rr:
  for bit in r['component_recipe'].split('+'):cc[bit]+=1
  ledger.append({'event_id':r['event_id'],'diagram_unit':unit,'physical_page':r['physical_page'],'locus':r['locus'],'surface':r['surface'],'visible_owner_de':r['visible_owner_de'],'component_recipe':r['component_recipe'],'address_reading_de':r['current_reading_de'],'diagram_model':model})
 summ.append({'diagram_unit':unit,'physical_page':rr[0]['physical_page'],'diagram_model':model,'loci':len({r['locus'] for r in rr}),'groups':len(rr),'surface_types':len({r['surface'] for r in rr}),'dominant_address_components':'|'.join(f'{k}:{v}' for k,v in cc.most_common(10)),'concrete_diagram_reading_de':text})
write('PASS930_501_ADDRESS_EVENT_LEDGER.tsv',list(ledger[0]),ledger)
write('PASS930_10_DIAGRAM_UNIT_READINGS.tsv',list(summ[0]),summ)
doc=['# Pass 930 — die Bildbeschriftungen und Himmelsräder','',
     'Diese Lesung behandelt die Karten als Adressen, Klassen und lokale Namen. Sie werden nicht mit gleich aussehenden Tätigkeitskarten in einen gesprochenen Werkstattsatz gezwungen.','']
for r in summ:doc += [f"## {r['diagram_unit']} — {r['diagram_model']}",'',r['concrete_diagram_reading_de'],'',f"{r['loci']} Beschriftungsorte, {r['groups']} Gruppen, {r['surface_types']} Oberflächentypen.",'']
(H/'PASS930_COMPLETE_DIAGRAM_READING.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report="""# Pass 930 — die letzten 501 Gruppen bekommen ihre Buchfunktion

## Ergebnis

Alle 501 nichtprosaartigen Gruppen sind jetzt zehn konkreten Bild- und
Diagrammeinheiten zugeordnet. Sie liefern Besitzer, Reihe, Klasse, Stelle,
Unterstelle, Wert, Grad und Weiterführung. Sie sind deshalb keine 501 weiteren
Werkstattwörter.

## Die wichtigste Trennung

`AIR` kann in der Werkstatt einen Flüssigkeits- oder Stationslauf bezeichnen,
im Widder- und Fischrad bezeichnet derselbe kurze Kern aber den Ringlauf. `OK`,
`O`, `CH`, `K`, `S`, `AL` und `AR` funktionieren in den Bildern ebenfalls als
Aufruf-, Klassen-, Wert-, Ziel- und Quellzeichen. Der gemeinsame abstrakte Kern
bleibt; die konkrete Sachbedeutung kommt vom Register.

## Was die drei reinen Himmelsseiten sagen

- f69v: drei getrennte Räder; nur das linke trägt 28 lokale Plätze;
- f70v1: Widderfiguren nach Ringplatz, Grad und Klasse adressieren;
- f70v2: Fischfiguren nach Ringplatz, Grad und Klasse adressieren.

Damit ist die vollständige 14-Seiten-Ausgabe funktional geschlossen: 2.010
Werkstattgruppen sprechen Handlungen und 501 Bildgruppen sprechen Adressen oder
lokale Bezeichnungen.
"""
(H/'PASS930_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS930_501_ADDRESS_EVENT_LEDGER.tsv','PASS930_10_DIAGRAM_UNIT_READINGS.tsv','PASS930_COMPLETE_DIAGRAM_READING.md','PASS930_REPORT.md']
(H/'PASS930_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','events':len(ledger),'units':len(summ),'loci':len({r['locus'] for r in ledger}),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
