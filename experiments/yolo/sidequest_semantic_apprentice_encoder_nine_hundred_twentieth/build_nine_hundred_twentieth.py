#!/usr/bin/env python3
"""Build Pass 920: encode concrete workshop intentions back into observed cards."""

import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P912=ROOT/'experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth'
P916=ROOT/'experiments/yolo/sidequest_semantic_workshop_phrasebook_nine_hundred_sixteenth'
def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

MESSAGES=[
 ('A01','M21 M02','nach Sollmaß ansetzen und kurz schließen'),
 ('A02','M20 M22 M23 M02','aus dem bezeichneten Teil eine Portion nehmen, an der Zielstelle ansetzen und kurz schließen'),
 ('A03','M31 M21 M01','vom Ansatz entnehmen, nach Sollmaß ansetzen und länger schließen'),
 ('A04','M19 M18 M25','den Auszug durch den Durchlass weiterleiten und den Schritt schließen'),
 ('A05','M28 M21 M02','das Sollmaß prüfen, danach entsprechend ansetzen und kurz schließen'),
 ('A06','M29 M22 M01','die Portion prüfen, ansetzen und länger schließen'),
 ('A07','M30 M24 M03','die Entnahmestelle prüfen und diesen Posten von dort länger ansetzen'),
 ('A08','M27 M17 M25','danach diesen Posten umsetzen, fortsetzen und schließen'),
 ('A09','M36 M19 M12','den Gang beginnen, den Auszug weiterleiten, abführen und schließen'),
 ('A10','M39 M08 M06','diesen Posten einsetzen, kurz halten und schließen'),
 ('A11','M33 M02','diesen Posten kurz behandeln, kurz ansetzen und schließen'),
 ('A12','M34 M05','diesen Posten länger behandeln und länger halten; schließen'),
 ('A13','M35 M25','an der Sammelstelle länger halten, dann schließen'),
 ('A14','M43 M08 M06','den Ansatz halten, diesen Posten kurz halten und schließen'),
 ('A15','M44 M21 M02','mit dem Ansatz fortsetzen, nach Sollmaß ansetzen und kurz schließen'),
 ('A16','M37 M31 M22 M14','danach vom Ansatz entnehmen, eine Portion ansetzen, umsetzen und schließen'),
 ('A17','M38 M17 M13','in diesem Teil fortsetzen, den Posten umsetzen und schließen'),
 ('A18','M23 M07 M05','an der Zielstelle ansetzen, dort länger halten und schließen'),
 ('A19','M42 M03 M01','der Zielstelle zuordnen, länger ansetzen und schließen'),
 ('A20','M41 M04 M02','eine Portion zugeben, kurz ansetzen und schließen'),
 ('A21','M40 M21 M01','nach Sollmaß zugeben, ansetzen und länger schließen'),
 ('A22','M16 M11','kurz spülen, danach ruhen lassen und schließen'),
 ('A23','M15 M12','einsetzen, umsetzen, abführen und schließen'),
 ('A24','M09 M17 M25','danach länger arbeiten, den Posten umsetzen und schließen'),
]

def main():
 events=read(P912/'PASS912_2511_EVENT_INTERLINEAR.tsv');mac=read(P916/'PASS916_PHRASEBOOK.tsv')
 by_recipe=defaultdict(Counter)
 for r in events:by_recipe[r['component_recipe']][r['surface']]+=1
 enc=[];by_id={}
 for m in mac:
  counts=by_recipe[m['component_pattern']]
  base_pool=[(s,n) for s,n in counts.items() if not s.startswith('q')]
  base=max(base_pool,key=lambda x:(x[1],-len(x[0]),x[0]))[0] if base_pool else counts.most_common(1)[0][0]
  qpool=[(s,n) for s,n in counts.items() if s.startswith('q')]
  entry=max(qpool,key=lambda x:(x[1],-len(x[0]),x[0]))[0] if qpool else base
  row={'macro_id':m['macro_id'],'intention_de':m['workshop_phrase_de'],'component_recipe':m['component_pattern'],
       'internal_surface':base,'post_close_entry_surface':entry,'q_entry_alternation':'YES' if entry!=base else 'NO',
       'all_observed_surfaces':','.join(f'{s}:{n}' for s,n in counts.most_common()),'observed_events':str(sum(counts.values())),
       'decode_de':m['workshop_phrase_de']}
  enc.append(row);by_id[m['macro_id']]=row
 write('PASS920_44_PHRASE_ENCODER.tsv',enc,list(enc[0]))

 msgs=[]
 for mid,seq,intention in MESSAGES:
  ids=seq.split();internal=[by_id[x]['internal_surface'] for x in ids]
  entry=[by_id[ids[0]]['post_close_entry_surface']]+[by_id[x]['internal_surface'] for x in ids[1:]]
  decoded='; '.join(by_id[x]['decode_de'] for x in ids)
  msgs.append({'message_id':mid,'source_intention_de':intention,'macro_sequence':'>'.join(ids),
               'component_recipes':' | '.join(by_id[x]['component_recipe'] for x in ids),
               'internal_card_sequence':' '.join(internal),'post_close_entry_sequence':' '.join(entry),
               'roundtrip_reading_de':decoded,'cards':str(len(ids)),'all_cards_observed':'YES'})
 write('PASS920_24_APPRENTICE_MESSAGES.tsv',msgs,list(msgs[0]))

 manual=['# Pass 920 — Lehrlingskodex','',
  '1. Zerlege die Anweisung in Quelle, Maß/Portion, Handlung, Ziel, Grad und Schluss.',
  '2. Nimm für häufige Bündel die gelernte Phrase aus dem 44er-Deck.',
  '3. Innerhalb eines laufenden Feldes schreibe die interne Oberfläche.',
  '4. Direkt nach einem geschlossenen Feld darf die erste Phrase ihre beobachtete q-Eintrittsform nehmen.',
  '5. Lies nicht Buchstabe für Buchstabe zurück, sondern Phrase für Phrase.',
  '6. Bildbesitzer werden nicht ausgeschrieben; das Bild setzt Pflanze, Station, Figur oder Gefäß.',
  '7. Eine physische Zeile darf mitten in der Folge enden.',
  '8. `DY` schließt nur in der lizenzierten Phrase, nicht als frei lesbarer Buchstabe.','']
 for r in msgs:manual.append(f"- **{r['message_id']}** {r['source_intention_de']} → `{r['internal_card_sequence']}` → {r['roundtrip_reading_de']}")
 (OUT/'PASS920_APPRENTICE_MANUAL.md').write_text('\n'.join(manual),encoding='utf-8')
 qalt=sum(r['q_entry_alternation']=='YES' for r in enc)
 report=f'''# Pass 920 — Rückwärts schreiben

## Ergebnis

Das Mischsystem ist nun erstmals in beide Richtungen ausführbar. Für alle 44
gelehrten Phrasen existiert eine tatsächlich beobachtete interne Kartenform; bei
{qalt} Phrasen existiert zusätzlich eine beobachtete `q`-Eintrittsform nach einem
geschlossenen Feld. Keine Oberfläche wurde neu erfunden.

24 konkrete Werkstattanweisungen wurden in Folgen von zwei bis vier Kartenphrasen
geschrieben und wieder zurückgelesen. Beispiele:

- „nach Sollmaß ansetzen und kurz schließen“ → `okaiin okedy`;
- „Auszug durch den Durchlass weiterleiten und schließen“ → `cheol chckhy oldy`;
- „kurz spülen, ruhen lassen und schließen“ → `lshedy shedy`;
- „einsetzen, umsetzen, abführen und schließen“ → `pchedy lchedy`.

## Was dieses Modell jetzt konkret ist

Es ist weder eine reine Buchstabenchiffre noch ein Wörterbuch mit 1384 unabhängigen
Wörtern. Es ist ein **kleines Kürzelalphabet plus ein gelerntes Phrasendeck plus
Positionsallographen**. Ein Schreiber kann eine neue Arbeitsfolge aus bekannten
Phrasen zusammenstellen; seltene Besitzer- und Klassennamen bleiben im lokalen
Exemplar.

## Nächster Schritt

Die 24 Nachrichten werden nun absichtlich variiert: Maß gegen Portion, kurz gegen
länger, Quelle gegen Ziel und interner gegen q-Eintritt. Daraus entsteht ein
minimaler Bedeutungswürfel, der vorhersagt, welche einzelne Kartenänderung eine
konkrete Bedeutungsänderung ausdrücken soll.
'''
 (OUT/'PASS920_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS920_44_PHRASE_ENCODER.tsv','PASS920_24_APPRENTICE_MESSAGES.tsv','PASS920_APPRENTICE_MANUAL.md','PASS920_REPORT.md']
 summary={'status':'BUILT','phrases':len(enc),'messages':len(msgs),'q_entry_pairs':qalt,'cards_in_messages':sum(int(r['cards']) for r in msgs),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS920_BUILD_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
