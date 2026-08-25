#!/usr/bin/env python3
"""Build Pass 925: natural phase-based German for the thirty longest clauses."""

import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P924=ROOT/'experiments/yolo/sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
def read(n):
 with (P924/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

PHASES=[('TRANSFER',{'CHD','CPH','LSH','CFH','SOLK'}),('CONDITION',{'SH','SHED','CHK','CTH','R'}),('PREPARE',{'OK','P','K'}),('EXECUTE',{'O','T'}),('SELECT',{'CH','S'})]
VERB={'P':'setze ein','OK':'setze an','CH':'entnimm','K':'gib zu','O':'führe den Gang aus','T':'stelle ein','S':'wähle aus','CTH':'stelle bereit','R':'kennzeichne','CHK':'behandle','CHD':'setze um','SH':'halte','SHED':'lass absetzen','CFH':'trenne','LSH':'spüle','CPH':'leite um','SOLK':'fange auf'}
OBJ={'Y':'den aktuellen Posten','OR':'den Ansatz','CHEO':'den Auszug','HO':'den Teil'}
SRC={'D_ADDR':'aus dem bezeichneten Teil','AR':'von der Entnahmestelle','A_ADDR':'von der lokalen Stelle'}
QTY={'AIIN':'nach Sollmaß','AIN':'als Portion','IIN':'auf der angegebenen Stufe','DA':'auf der zweiten Stufe'}
TGT={'AL':'zur Ziel- oder Anschlussstelle','AM_ADDR':'zur Innenstelle','L':'in den nächsten Lauf','CKH':'durch den Durchlass','AIR':'entlang des Laufs','S_ADDR':'zur bezeichneten s-Stelle'}
GRADE={'E':'kurz','EE':'länger','EEE':'vollständig'}
def uniq(xs):
 o=[]
 for x in xs:
  if x not in o:o.append(x)
 return o
def join(xs):
 if not xs:return ''
 if len(xs)==1:return xs[0]
 if len(xs)==2:return xs[0]+' und '+xs[1]
 return ', '.join(xs[:-1])+' und '+xs[-1]
def phase(atoms):
 s=set(atoms)
 for name,roots in PHASES:
  if s&roots:return name
 return 'CONTEXT'
def render(atoms,phase_no):
 objects=uniq(OBJ[a] for a in atoms if a in OBJ);sources=uniq(SRC[a] for a in atoms if a in SRC);qty=uniq(QTY[a] for a in atoms if a in QTY);targets=uniq(TGT[a] for a in atoms if a in TGT);grades=uniq(GRADE[a] for a in atoms if a in GRADE)
 vc=Counter(a for a in atoms if a in VERB);order=uniq(a for a in atoms if a in VERB)
 acts=[VERB[a]+(f' ({vc[a]}×)' if vc[a]>1 else '') for a in order]
 opening='Dann ' if phase_no>1 or any(a in {'OT','OL','OS','RESUME_CARD'} for a in atoms) else ''
 obj=join(objects) if objects else 'den bezeichneten Arbeitsgang'
 context=' '.join(sources+qty)
 text=f"{opening}nimm {obj}"+(f" {context}" if context else '')+" in Arbeit"
 text+=': '+join(acts) if acts else ': arbeite damit weiter'
 text+='.'
 if targets:text+=' Führe ihn '+join(targets)+'.'
 if grades:text+=' Arbeite '+join(grades)+'.'
 if 'DY' in atoms:text+=' Schließe den Schritt.'
 return text[0].upper()+text[1:]

def main():
 clauses=read('PASS924_354_CURRENT_CLAUSES.tsv');instructions=read('PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv');events=read('PASS924_2511_CURRENT_EVENT_LEDGER.tsv')
 imap={r['instruction_id']:r for r in instructions};eidx={r['event_id']:i for i,r in enumerate(events)}
 top=sorted(clauses,key=lambda r:(-int(r['events']),r['clause_id']))[:30]
 phase_rows=[];clause_rows=[];bindings=[];phase_id=0
 for rank,c in enumerate(top,1):
  ids=c['instruction_ids'].split('|');groups=[];cur=[];curphase=None
  for iid in ids:
   atoms=[a for card in imap[iid]['component_sequence'].split(' | ') for a in card.split('+')];p=phase(atoms)
   if cur and (p!=curphase or len(cur)>=4):groups.append((curphase,cur));cur=[]
   curphase=p;cur.append((iid,atoms))
  if cur:groups.append((curphase,cur))
  local=[]
  for n,(p,group) in enumerate(groups,1):
   phase_id+=1;pid=f'P925-P{phase_id:03d}';flat=[a for _,atoms in group for a in atoms];gids=[x[0] for x in group]
   first=imap[gids[0]];last=imap[gids[-1]];reading=render(flat,n)
   prow={'phase_id':pid,'ranked_clause':str(rank),'clause_id':c['clause_id'],'physical_page':c['physical_page'],'register':c['register'],'phase_order':str(n),'phase_type':p,'instruction_ids':'|'.join(gids),'instructions':str(len(gids)),'start_event':first['start_event'],'end_event':last['end_event'],'component_sequence':' | '.join(imap[x]['component_sequence'] for x in gids),'natural_phase_de':reading}
   phase_rows.append(prow);local.append(pid)
   lo,hi=eidx[first['start_event']],eidx[last['end_event']]
   for e in events[lo:hi+1]:
    if e['current_channel']!='WORKSHOP_PROSE':continue
    bindings.append({'event_id':e['event_id'],'phase_id':pid,'clause_id':c['clause_id'],'physical_page':c['physical_page'],'locus':e['locus'],'surface':e['surface'],'component_recipe':e['component_recipe'],'current_spoken_unit':e['current_spoken_unit'],'current_reading_de':e['current_reading_de']})
  clause_rows.append({'rank':str(rank),'clause_id':c['clause_id'],'physical_page':c['physical_page'],'register':c['register'],'events':c['events'],'instructions':c['instruction_count'],'phases':str(len(local)),'phase_ids':'|'.join(local),'crosses_physical_line':c['crosses_physical_line'],'end_reason':c['end_reason'],'natural_paragraph_de':' '.join(next(x['natural_phase_de'] for x in phase_rows if x['phase_id']==pid) for pid in local)})
 write('PASS925_30_NATURAL_CLAUSES.tsv',clause_rows,list(clause_rows[0]));write('PASS925_PHASES.tsv',phase_rows,list(phase_rows[0]));write('PASS925_856_EVENT_BINDINGS.tsv',bindings,list(bindings[0]))
 doc=['# Pass 925 — die 30 längsten Klauseln in natürlichem Werkstattdeutsch','', 'Die Absätze sind redaktionelle Paraphrasen; die TSV-Bindung bewahrt jede Karte und ihre Reihenfolge.','']
 for r in clause_rows:doc += [f"## {r['rank']}. {r['clause_id']} — {r['physical_page']}",'',r['natural_paragraph_de'],'']
 (OUT/'PASS925_NATURAL_LONG_CLAUSE_EDITION.md').write_text('\n'.join(doc),encoding='utf-8')
 report=f'''# Pass 925 — lange Klauseln werden lesbar

## Ergebnis

Die 30 längsten Klauseln enthalten 856 sichtbare Ereignisse und sind nun in
{len(phase_rows)} kurze Prozessphasen gegliedert. Keine Phase folgt automatisch
einer physischen Zeile. Jede Originalkarte bleibt über Ereignis→Arbeitszug→Phase
gebunden.

Die Redaktion benutzt fünf normale Werkstattphasen: AUSWÄHLEN/ENTNEHMEN,
VORBEREITEN/ZUGEBEN, AUSFÜHREN/EINSTELLEN, HALTEN/BEHANDELN sowie
UMSETZEN/SPÜLEN/TRENNEN/AUFFANGEN. Innerhalb einer Phase werden Wiederholungen
als `2×`, `3×` usw. gesprochen, statt denselben Satz immer neu hinzuschreiben.

## Wirkung

Die größten Pflanzen- und Stationsklauseln lesen sich jetzt wie Arbeitsprotokolle:
Nimm den bildlich bestimmten Posten, entnimm Quelle oder Portion, setze ihn an,
halte oder behandle ihn in einem Grad, führe ihn zu Anschluss/Durchlass und
schließe den Schritt. Lokale Zeichen bleiben im exakten Binding, überladen aber
nicht mehr den flüssigen Absatz.

## Nächster Schritt

Dasselbe Redaktionsverfahren wird auf die übrigen 324 kürzeren Klauseln angewandt.
Danach liegt eine einheitliche natürliche Prosafassung aller zwölf Prosaseiten vor.
'''
 (OUT/'PASS925_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS925_30_NATURAL_CLAUSES.tsv','PASS925_PHASES.tsv','PASS925_856_EVENT_BINDINGS.tsv','PASS925_NATURAL_LONG_CLAUSE_EDITION.md','PASS925_REPORT.md']
 s={'status':'BUILT','clauses':len(clause_rows),'events':len(bindings),'phases':len(phase_rows),'instructions':sum(int(r['instructions']) for r in clause_rows),'phase_types':dict(Counter(r['phase_type'] for r in phase_rows)),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS925_BUILD_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
