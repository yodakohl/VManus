#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent
B=H.parent/'sidequest_semantic_complete_process_maps_nine_hundred_twenty_sixth'

def read(n):
 with (B/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

READINGS={
'f10r':('PFLANZENZUBEREITUNG_MIT_BEREITSCHAFTSPRUEFUNG','Vom gezeigten Kraut werden nacheinander Teile entnommen, in mehreren Gängen verarbeitet und bis zum gebrauchsfertigen Zustand geführt. Weitere Teile werden nach Sollmaß bereitgestellt und durch einen Durchlass weitergegeben. Der erste große Arbeitsgang schließt; der zweite bleibt als Fortsetzung offen.'),
'f11r':('GEHALTENE_UND_ABGETRENNTE_PFLANZENPORTION','Halte die bezeichneten Pflanzenteile, entnimm davon Portionen, gib sie in den Ansatz und arbeite sie weiter. Nach erneutem Halten wird ein Teil getrennt oder umgeleitet; der erste Zug schließt, der zweite Artikelzug bleibt offen.'),
'f13r':('FUENF_KURZE_PFLANZENARBEITSGAENGE','Bereite den Ansatz, setze das bezeichnete Material ein und entnimm die benötigten Teile. Gib nach Sollmaß zu, halte den Posten, führe ihn durch den angegebenen Gang und schließe vier kurze Arbeitsschritte. Ein letzter Zusatz- und Ansatzschritt bleibt zur Fortsetzung offen.'),
'f55v':('MEHRFACH_ZUGEGEBENE_PFLANZENZUBEREITUNG','Setze die Pflanzenzubereitung an und gib ihre Bestandteile in mehreren notierten Portionen zu. Stelle, behandle und versetze den Ansatz zwischen den angegebenen Stellen; entnimm zwischendurch Proben und führe sie durch den Durchlass. Vier Teilgänge schließen, der lange Hauptgang bleibt offen.'),
'f56r':('PORTIONSWEISE_ENTNAHME_UND_NEUANSATZ','Entnimm aus dem gezeigten Pflanzenmaterial wiederholt kleine Anteile und setze sie in mehreren Stufen neu an. Gib weitere Anteile zu, halte und prüfe einzelne Züge und führe das Arbeitsgut zur nächsten Stelle. Zwei große Gänge schließen; der letzte bleibt als anschließende Verwendung offen.'),
'f75r':('BAD_UND_STATIONSARBEIT_IN_KURZEN_ZELLEN','Arbeite die gezeigten Bade- und Stationsposten zellenweise ab: ansetzen, kurz oder länger halten, zur nächsten Stelle umsetzen, dort neu ansetzen und den jeweiligen Schritt schließen. Entnahme, Zugabe, Auffangen und Absetzen erscheinen als lokale Varianten. Fast jede Zelle ist ein eigener kleiner Arbeitsauftrag, nicht Teil eines einzigen langen Satzes.'),
'f81v':('ANWENDUNGS_UND_TRANSFERFOLGE','Setze den jeweiligen Posten an der gezeigten Station an, gib die bezeichnete Menge zu und halte sie für die notierte Stufe. Führe das Arbeitsgut danach über den nächsten Lauf, setze es dort neu an und lass einzelne Züge absetzen. Die Seite ist eine Folge geschlossener Anwendungs- und Transferzellen.'),
'f82r':('MARKIERTE_STATIONSFOLGE_MIT_DURCHLASS','Wähle an jeder dargestellten Station den aktiven Posten, setze ihn an, markiere seinen Zustand und führe ihn über Anschluss oder Durchlass weiter. Wiederhole Zugabe, Halten und Umsetzen gemäß der örtlichen Zeichnung; fange einzelne Ausgänge auf. Fast alle Stationszellen schließen für sich.'),
'f83r':('VARIANTENREGISTER_FUER_UMSETZEN_UND_ABSETZEN','Diese Seite verzeichnet viele kurze Varianten desselben Stationsbetriebs: auswählen, ansetzen, halten, umsetzen, am neuen Ort wieder ansetzen und schließlich absetzen oder auffangen. Die sichtbaren Becken und Verbindungen bestimmen jeweils den Besitzer; der Text liefert die lokale Handlung und Stufe. Es gibt keinen einzigen durchgehenden Kreislauf, sondern viele abgeschlossene Varianten.'),
'f67r2':('RING_UND_TABELLENPOSTEN_AUSWAEHLEN','Wähle den bezeichneten Ring- oder Tabellenposten, führe die für ihn eingetragene Operation aus und wechsle zur zugeordneten Stelle oder Stufe. Wiederholtes Auswählen, Einstellen und Kennzeichnen spricht eine Nachschlagetafel, nicht eine fortlaufende Pflanzen- oder Badrezeptur. Nur wenige Blöcke schließen ausdrücklich.'),
'f68r1':('STERNSTELLEN_KURZ_ZUORDNEN','Entnimm oder wähle den bezeichneten Eintrag, führe seine lokale Anweisung aus und ordne ihn der markierten Sternstelle zu. Die drei Textblöcke begleiten räumliche Stationen; sie ergeben keine feste Umlaufrichtung und keine Verbindung zur benachbarten 28er-Seite.'),
'f88r':('ZUTATEN_UND_VORRATSREGISTER','Wähle aus den bezeichneten Vorrats- oder Zutatenposten, entnimm den nötigen Anteil, setze die Zubereitung an und gib weitere Bestandteile zu. Halte, prüfe und verteile den Ansatz auf die angegebenen Stellen; einzelne Passagen führen durch einen Durchlass. Die Seite liest sich als kompaktes Zubereitungs- und Zuteilungsregister.'),
}
maps=read('PASS926_354_PROCESS_MAPS.tsv');by=defaultdict(list)
for r in maps:by[r['physical_page']].append(r)
pages=[];bindings=[]
for page,rr in by.items():
 vc=Counter()
 for r in rr:
  for bit in r['verb_counts'].split(';'):
   if bit!='NONE':v,n=bit.split(':');vc[v]+=int(n)
 model,text=READINGS[page]
 pages.append({'physical_page':page,'register':rr[0]['register'],'page_model':model,'clauses':len(rr),'events':sum(int(r['events']) for r in rr),'instructions':sum(int(r['instructions']) for r in rr),'closed_clauses':sum(r['end_reason']=='LICENSED_DY_CLOSE' for r in rr),'open_clauses':sum(r['end_reason']!='LICENSED_DY_CLOSE' for r in rr),'dominant_verbs':'|'.join(f'{v}:{n}' for v,n in vc.most_common(8)),'concrete_page_reading_de':text})
 for r in rr:bindings.append({'physical_page':page,'page_model':model,'clause_id':r['clause_id'],'start_event':r['start_event'],'end_event':r['end_event'],'events':r['events'],'natural_process_summary_de':r['natural_process_summary_de']})
write('PASS929_12_CONCRETE_PAGE_READINGS.tsv',list(pages[0]),pages)
write('PASS929_354_CLAUSE_BINDINGS.tsv',list(bindings[0]),bindings)
doc=['# Pass 929 — was die zwölf Textseiten in unserer Arbeitstheorie sagen','',
     'Diese Fassung spricht die aktuelle Werkstatttheorie möglichst direkt aus. Die darunterliegenden Klausel- und Ereignisbindungen stehen in den TSV-Dateien.','']
for r in pages:doc += [f"## {r['physical_page']} — {r['page_model']}",'',r['concrete_page_reading_de'],'',f"Gebunden: {r['events']} sichtbare Gruppen, {r['instructions']} Arbeitszüge, {r['clauses']} Klauseln ({r['closed_clauses']} geschlossen, {r['open_clauses']} offen).",'']
(H/'PASS929_TWELVE_PAGE_TRANSLATION.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report="""# Pass 929 — konkrete Seitenaussagen

## Ergebnis

Die zwölf Seiten mit Werkstattprosa haben jetzt je eine konkrete, kurze
Gesamtlesung. Die fünf Pflanzenblätter bilden keine Liste von Pflanzennamen,
sondern Seitenartikel mit Entnahme, Ansatz, Portion, Behandlung und Weitergabe.
Die vier Biological-Seiten lesen sich am besten als viele lokale Bade-,
Anwendungs- und Stationsaufträge. Die zwei Himmelsseiten sind Auswahl- und
Zuordnungstafeln. f88r ist ein dichtes Zutaten-/Vorratsregister.

## Wichtigste Korrektur

Die Textmenge einer Seite ist nicht die Länge eines Satzes. Besonders f75r,
f81v, f82r und f83r bestehen aus vielen kleinen geschlossenen Zellen unter
wechselnden sichtbaren Besitzern. Umgekehrt enthalten die Pflanzenblätter lange
offene Arbeitsartikel, die über Zeilen hinweg weiterlaufen.

## Derzeit beste Buchidee

Ein bildgeführtes praktisches Kompendium: Pflanzenmaterial auswählen und
zubereiten; es in lokalen Bade-/Anwendungsstationen führen; getrennte
himmelsbezogene Tafeln zur Auswahl oder Zuordnung verwenden. Die technische
Lesung bleibt als enger Rivale erhalten, aber die neue Prosa liest sich nicht
mehr wie ein reines Wasserwerk.
"""
(H/'PASS929_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS929_12_CONCRETE_PAGE_READINGS.tsv','PASS929_354_CLAUSE_BINDINGS.tsv','PASS929_TWELVE_PAGE_TRANSLATION.md','PASS929_REPORT.md']
(H/'PASS929_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','pages':len(pages),'clauses':len(bindings),'events':sum(int(x['events']) for x in pages),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
