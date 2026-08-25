#!/usr/bin/env python3
"""Build Pass 918: one short invariant default for every action stem."""

import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
P917=ROOT/'experiments/yolo/sidequest_semantic_fluent_prose_nine_hundred_seventeenth'

def read(n):
    with (P917/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
    with (OUT/n).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

VERBS={
 'P':('EINSETZEN','einen Stoff oder Posten in den laufenden Gang bringen'),
 'OK':('ANSETZEN','einen bezeichneten Arbeitsgang aktiv beginnen'),
 'CH':('ENTNEHMEN','einen Teil aus dem aktiven Besitzer nehmen'),
 'K':('ZUGEBEN','einen Posten dem aktiven Gang hinzufügen'),
 'O':('AUSFÜHREN','den bezeichneten Arbeitsgang ausführen'),
 'T':('EINSTELLEN','einen Posten oder Wert auf die bezeichnete Stufe stellen'),
 'S':('WÄHLEN','Quelle, Portion, Ziel oder Möglichkeit auswählen'),
 'CTH':('BEREITSTELLEN','den Posten in den verwendbaren Zustand bringen'),
 'R':('KENNZEICHNEN','den erreichten Zustand kenntlich machen'),
 'CHK':('BEHANDELN','den Posten einer Zustandsbehandlung unterziehen'),
 'CHD':('UMSETZEN','den aktiven Posten in den nächsten Zustand oder Ort überführen'),
 'SH':('HALTEN','den aktiven Posten am Ort oder im Zustand halten'),
 'SHED':('ABSETZEN','den Posten ruhen oder sich setzen lassen'),
 'CFH':('PRESSEN','den Posten pressen und dadurch trennen'),
 'LSH':('SPÜLEN','den Posten oder Durchlass spülen'),
 'CPH':('RÜCKFÜHREN','den Posten in einen Gegen- oder Empfangsgang führen'),
 'SOLK':('AUFFANGEN','den Posten an einer Sammelstelle aufnehmen'),
}

CON={'OT':'danach','OL':'weiter','OS':'auch','RESUME_CARD':'davon ausgehend'}
OBJ={'Y':'diesen Posten','OR':'den Ansatz','CHEO':'den Auszug','HO':'den Stoffteil'}
SRC={'AR':'von der Entnahmestelle','D_ADDR':'aus diesem Teil','A_ADDR':'von der lokalen Stelle'}
QTY={'AIIN':'nach Sollmaß','AIN':'als eine Portion','IIN':'auf der angegebenen Stufe','DA':'auf der zweiten Stufe'}
TGT={'AL':'zur Ziel- oder Anschlussstelle','AM_ADDR':'zur Innenstelle','L':'in den nächsten Lauf','CKH':'durch den Durchlass','AIR':'entlang des Laufs','S_ADDR':'zur bezeichneten s-Stelle'}
GRADE={'E':'kurz','EE':'länger','EEE':'vollständig'}
DETAIL={'CARRIER_Q':'unter q-Träger','D_LABEL':'mit d-Zeichen','M_LOCAL':'mit m-Zeichen','LOCAL_CHAR_B':'mit b-Zeichen','LOCAL_CHAR_F':'mit f-Zeichen','LOCAL_CHAR_G':'mit g-Zeichen','LOCAL_CHAR_I':'mit i-Zeichen','LOCAL_CHAR_J':'mit j-Zeichen'}

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
def render(atoms):
 con=uniq(CON[a] for a in atoms if a in CON);obj=uniq(OBJ[a] for a in atoms if a in OBJ)
 src=uniq(SRC[a] for a in atoms if a in SRC);qty=uniq(QTY[a] for a in atoms if a in QTY)
 tgt=uniq(TGT[a] for a in atoms if a in TGT);grade=uniq(GRADE[a] for a in atoms if a in GRADE)
 detail=uniq(DETAIL[a] for a in atoms if a in DETAIL);acts=[]
 for a in atoms:
  if a in VERBS and (not acts or acts[-1]!=VERBS[a][0].lower()):acts.append(VERBS[a][0].lower())
 pieces=[' '.join(con),' '.join(src),' '.join(qty),join(obj),' '.join(grade),join(acts),' '.join(tgt),' '.join(detail)]
 if not acts:pieces.append('weiterarbeiten')
 s=' '.join(x for x in pieces if x).strip()
 if 'DY' in atoms:s+='; fertig'
 return s[0].upper()+s[1:]+'.'

def main():
 ins=read('PASS917_1435_FLUENT_INSTRUCTIONS.tsv');clauses=read('PASS917_354_FLUENT_CLAUSES.tsv')
 counts=Counter();pages=defaultdict(Counter);examples=defaultdict(list);out=[]
 for r in ins:
  atoms=[a for card in r['component_sequence'].split(' | ') for a in card.split('+')]
  for a in atoms:
   if a in VERBS:
    counts[a]+=1;pages[a][r['physical_page']]+=1
    if len(examples[a])<5:examples[a].append(r['surface_sequence'])
  z=dict(r);z['minimal_verb_sequence']='>'.join(a for a in atoms if a in VERBS)
  z['revised_fluent_de']=render(atoms);out.append(z)
 idmap={r['instruction_id']:r for r in out};cout=[]
 for c in clauses:
  ids=c['instruction_ids'].split('|');z=dict(c)
  z['revised_fluent_clause_de']=' '.join(idmap[x]['revised_fluent_de'] for x in ids);cout.append(z)
 deck=[]
 for v,(word,definition) in VERBS.items():
  deck.append({'stem':v,'fixed_verb_de':word,'short_definition_de':definition,'events_in_1435_instructions':str(counts[v]),
               'pages':','.join(f'{p}:{n}' for p,n in sorted(pages[v].items())),'examples':' | '.join(examples[v]),
               'distinction':'KEEP_ONE_VERB'})
 write('PASS918_17_VERB_DECK.tsv',deck,list(deck[0]));write('PASS918_1435_REVISED_INSTRUCTIONS.tsv',out,list(out[0]));write('PASS918_354_REVISED_CLAUSES.tsv',cout,list(cout[0]))
 md=['# Pass 918 — Prosafassung mit 17 eindeutigen Verben','']
 for p in dict.fromkeys(x['physical_page'] for x in cout):
  md += [f'## {p}','']
  for x in cout:
   if x['physical_page']==p:md.append(f"- **{x['clause_id']}** {x['revised_fluent_clause_de']}")
  md.append('')
 (OUT/'PASS918_TWELVE_PAGE_REVISED_EDITION.md').write_text('\n'.join(md),encoding='utf-8')
 report=f'''# Pass 918 — minimales Verbdeck

## Neue feste Trennung

Die komplette Prosafassung verwendet jetzt genau **17 kurze Handlungsstämme**.
Jeder Stamm hat ein einziges Defaultverb:

`P einsetzen`, `OK ansetzen`, `CH entnehmen`, `K zugeben`, `O ausführen`,
`T einstellen`, `S wählen`, `CTH bereitstellen`, `R kennzeichnen`, `CHK behandeln`,
`CHD umsetzen`, `SH halten`, `SHED absetzen`, `CFH pressen`, `LSH spülen`,
`CPH rückführen`, `SOLK auffangen`.

Die wichtigste Verbesserung ist die Auflösung des alten Sammelverbs
„bearbeiten/prüfen“: `O` trägt den Arbeitsgang, `T` stellt einen Wert/Posten ein,
`S` wählt eine Alternative, `CTH` bringt auf Bereitschaft, `R` kennzeichnet den
erreichten Zustand und `CHK` behandelt diesen Zustand.

Alle 1435 Arbeitszüge und 354 Klauseln wurden damit neu gesprochen. Kein Ereignis
bekommt eine zweite Verbdeutung. Als Nächstes kann die Komposition dieser Verben
mit Quelle, Menge, Ziel und Grad gezielt auf den vier neuen Seiten gelesen werden.
'''
 (OUT/'PASS918_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS918_17_VERB_DECK.tsv','PASS918_1435_REVISED_INSTRUCTIONS.tsv','PASS918_354_REVISED_CLAUSES.tsv','PASS918_TWELVE_PAGE_REVISED_EDITION.md','PASS918_REPORT.md']
 summary={'status':'BUILT','verbs':17,'instructions':len(out),'clauses':len(cout),'verb_events':sum(counts.values()),'verb_counts':dict(counts),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS918_BUILD_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
