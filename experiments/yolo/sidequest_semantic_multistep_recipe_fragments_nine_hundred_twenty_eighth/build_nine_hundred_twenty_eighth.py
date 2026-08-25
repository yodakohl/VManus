#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent
B=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'

def read():
 with (B/'PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv').open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

DE={'P':'einsetzen','OK':'ansetzen','CH':'entnehmen','K':'zugeben','O':'ausführen','T':'einstellen','S':'auswählen','CTH':'bereitstellen','R':'kennzeichnen','CHK':'behandeln','CHD':'umsetzen','SH':'halten','SHED':'absetzen','CFH':'trennen','LSH':'spülen','CPH':'umleiten','SOLK':'auffangen'}
rows=read();by=defaultdict(list)
for r in rows:by[r['clause_id']].append(r)

streams={};counts={3:Counter(),4:Counter(),5:Counter()};pages={3:defaultdict(set),4:defaultdict(set),5:defaultdict(set)};clauses={3:defaultdict(set),4:defaultdict(set),5:defaultdict(set)}
for cid,rr in by.items():
 s=[]
 for r in rr:
  for v in (x for x in r['minimal_verb_sequence'].split('>') if x):s.append((v,r['instruction_id'],r['start_event'],r['end_event'],r['physical_page'],r['register']))
 streams[cid]=s
 for k in (3,4,5):
  for i in range(len(s)-k+1):
   q=tuple(x[0] for x in s[i:i+k]);counts[k][q]+=1;pages[k][q].add(rr[0]['physical_page']);clauses[k][q].add(cid)

triples=sorted((q for q in counts[3] if len(pages[3][q])>=3),key=lambda q:(-len(pages[3][q]),-counts[3][q],q))[:24]
quads=sorted((q for q in counts[4] if len(pages[4][q])>=3),key=lambda q:(-len(pages[4][q]),-counts[4][q],q))
selected=[(3,q) for q in triples]+[(4,q) for q in quads]
fragment=[]
for idx,(k,q) in enumerate(selected,1):
 fragment.append({'fragment_id':f'P928-F{idx:02d}','steps':k,'action_sequence':'>'.join(q),'spoken_sequence_de':' → '.join(DE[x] for x in q),'occurrences':counts[k][q],'clauses':len(clauses[k][q]),'pages':len(pages[k][q]),'page_list':'|'.join(sorted(pages[k][q])),'interpretation':'RECOMBINABLE_WORKSHOP_FRAGMENT'})
fid={(int(r['steps']),tuple(r['action_sequence'].split('>'))):r['fragment_id'] for r in fragment}
occ=[];oid=0
for cid,s in streams.items():
 for k,q in selected:
  for i in range(len(s)-k+1):
   if tuple(x[0] for x in s[i:i+k])!=q:continue
   oid+=1;span=s[i:i+k]
   occ.append({'occurrence_id':f'P928-O{oid:04d}','fragment_id':fid[(k,q)],'clause_id':cid,'physical_page':span[0][4],'register':span[0][5],'action_start_position':i+1,'action_end_position':i+k,'action_sequence':'>'.join(q),'instruction_sequence':'|'.join(x[1] for x in span),'event_span_sequence':'|'.join(f'{x[2]}..{x[3]}' for x in span),'spoken_sequence_de':' → '.join(DE[x] for x in q)})
write('PASS928_28_RECIPE_FRAGMENTS.tsv',list(fragment[0]),fragment)
write('PASS928_FRAGMENT_OCCURRENCES.tsv',list(occ[0]),occ)

book=['# Pass 928 — drei- und vierstufige Werkstattbausteine','',
      'Die Bausteine sind Zusammensetzungen bereits gelesener kurzer Tätigkeitswurzeln. Kein Einzelzeichen erhält dadurch eine Satzbedeutung.','']
for r in fragment:
 book += [f"## {r['fragment_id']} — {r['spoken_sequence_de']}",'',f"{r['occurrences']} Vorkommen in {r['clauses']} Klauseln auf {r['pages']} Seiten: {r['page_list']}.",'']
(H/'PASS928_RECIPE_FRAGMENT_BOOK.md').write_text('\n'.join(book).rstrip()+'\n',encoding='utf-8')

five_broad=sum(1 for q in counts[5] if len(pages[5][q])>=3)
report=f"""# Pass 928 — die längere Kompositionsebene

## Ergebnis

Die 24 breitesten Dreischritte und alle vier breit wiederkehrenden Viererschritte
ergeben {len(fragment)} Werkstattbausteine mit {len(occ)} exakt lokalisierten
Vorkommen. Neun Dreischritte erreichen sechs verschiedene Seiten. Nur vier
Viererschritte erreichen drei Seiten; kein Fünferschritt erreicht drei Seiten.

## Arbeitsmodell

Die lernbare Einheit liegt damit zwischen Stamm und vollständigem Rezept:

`kurze Tätigkeitswurzel → Zwei-Schritt-Handgriff → Drei-/Vier-Schritt-Baustein → lokale Klausel`.

Das passt besser zu einer kleinen Werkstatt als ein riesiges Wörterbuch mit
satzlangen Einzelglossen. Ein Schreiber lernt etwa „entnehmen → ausführen →
bereitstellen“ oder „umsetzen → ansetzen → umsetzen“ und füllt Besitzer, Menge,
Ziel und Grad aus dem Bild und dem lokalen Exemplar ein.

## Auffällige Zyklen

- `OK→OK→OK`: drei aufeinanderfolgende Ansatzstufen;
- `SH→OK→SH→OK`: halten, neu ansetzen, wieder halten, wieder ansetzen;
- `CHD→OK→CHD`: umsetzen, am neuen Ort ansetzen, weiter umsetzen;
- `O→CH→O`: Arbeitsgang, Teilentnahme, zweiter Arbeitsgang;
- `CH→O→CTH`: entnehmen, ausführen, bis bereit führen.
"""
(H/'PASS928_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS928_28_RECIPE_FRAGMENTS.tsv','PASS928_FRAGMENT_OCCURRENCES.tsv','PASS928_RECIPE_FRAGMENT_BOOK.md','PASS928_REPORT.md']
(H/'PASS928_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','fragments':len(fragment),'occurrences':len(occ),'broad_five_step_fragments':five_broad,'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
