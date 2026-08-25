#!/usr/bin/env python3
"""Build Pass 921: explicit one-change/one-meaning contrasts and one prediction."""

import csv,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P912=ROOT/'experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth'
P920=ROOT/'experiments/yolo/sidequest_semantic_apprentice_encoder_nine_hundred_twentieth'
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

ROOTS={'OK':('ANSETZEN','ansetzen'),'SH':('HALTEN','halten'),'CHK':('BEHANDELN','behandeln')}
GRADES={'E':('KURZ','kurz'),'EE':('LAENGER','länger')}
ENDS={'Y':('VERFUEGBAR','den Posten verfügbar lassen'),'DY':('SCHLUSS','den Schritt schließen')}

def main():
 ev=read(P912/'PASS912_2511_EVENT_INTERLINEAR.tsv');forms=defaultdict(Counter)
 for r in ev:forms[r['component_recipe']][r['surface']]+=1
 def base(rec):
  c=forms[rec];pool=[(s,n) for s,n in c.items() if not s.startswith('q')]
  return max(pool,key=lambda x:(x[1],-len(x[0]),x[0]))[0] if pool else (c.most_common(1)[0][0] if c else '')
 lattice=[]
 for root,grade,end in itertools.product(ROOTS,GRADES,ENDS):
  rec='+'.join([root,grade,end]);n=sum(forms[rec].values());pred=(rec=='CHK+E+DY' and n==0)
  surface=base(rec) if n else ('chekedy' if pred else '')
  lattice.append({'root':root,'root_meaning_de':ROOTS[root][0],'grade':grade,'grade_meaning_de':GRADES[grade][0],
                  'endpoint':end,'endpoint_meaning_de':ENDS[end][0],'component_recipe':rec,'preferred_surface':surface,
                  'observed_events':str(n),'status':'PREDICTED_MISSING_CARD' if pred else 'OBSERVED',
                  'composed_reading_de':f"{GRADES[grade][1]} {ROOTS[root][1]}; {ENDS[end][1]}"})
 write('PASS921_3X2X2_ACTION_CUBE.tsv',lattice,list(lattice[0]))

 pairs=[]
 def add(axis,a,b,change):
  pairs.append({'contrast_id':f'K{len(pairs)+1:02d}','axis':axis,'recipe_a':a,'surface_a':base(a),
                'events_a':str(sum(forms[a].values())),'recipe_b':b,'surface_b':base(b),
                'events_b':str(sum(forms[b].values())),'single_meaning_change_de':change,
                'both_observed':'YES' if forms[a] and forms[b] else 'NO'})
 for root in ROOTS:
  for end in ENDS:
   if forms[f'{root}+E+{end}'] and forms[f'{root}+EE+{end}']:
    add('GRADE',f'{root}+E+{end}',f'{root}+EE+{end}','kurz → länger')
 for root in ROOTS:
  for grade in GRADES:
   if forms[f'{root}+{grade}+Y'] and forms[f'{root}+{grade}+DY']:
    add('ENDPOINT',f'{root}+{grade}+Y',f'{root}+{grade}+DY','verfügbar lassen → Schritt schließen')
 for root in ['OK','K','S']:add('QUANTITY',f'{root}+AIN',f'{root}+AIIN','Portion → vorgeschriebenes Maß')
 for root in ['OK','S','CHK']:add('DIRECTION',f'{root}+AR',f'{root}+AL','Entnahmestelle → Zielstelle')
 for grade,end in [('E','Y'),('EE','Y'),('E','DY'),('EE','DY')]:add('ACTION',f'OK+{grade}+{end}',f'SH+{grade}+{end}','ansetzen → halten')
 for grade,end in [('E','Y'),('EE','Y'),('EE','DY')]:add('ACTION',f'SH+{grade}+{end}',f'CHK+{grade}+{end}','halten → behandeln')
 add('PATH','CHD+Y','CKH+Y','umsetzen → durch einen Durchlass führen')
 add('ORDER','OL+Y','OT+Y','fortsetzen → nächster Posten')
 write('PASS921_25_MINIMAL_CONTRASTS.tsv',pairs,list(pairs[0]))

 enc=read(P920/'PASS920_44_PHRASE_ENCODER.tsv');allographs=[]
 for r in enc:
  if r['q_entry_alternation']=='YES':
   allographs.append({'pair_id':f'Q{len(allographs)+1:02d}','macro_id':r['macro_id'],'component_recipe':r['component_recipe'],
                     'meaning_de':r['intention_de'],'internal_surface':r['internal_surface'],
                     'post_close_entry_surface':r['post_close_entry_surface'],'meaning_change':'NONE','function_change':'ENTRY_POSITION_ONLY'})
 write('PASS921_19_Q_ALLOGRAPHS.tsv',allographs,list(allographs[0]))

 prediction='''# Pass 921 — vorhergesagte fehlende Karte

## `chekedy`

Das Raster enthält elf beobachtete von zwölf möglichen Kombinationen:

- Handlung: ANSETZEN / HALTEN / BEHANDELN;
- Grad: KURZ / LÄNGER;
- Ende: POSTEN BLEIBT VERFÜGBAR / SCHRITT SCHLIESSEN.

Es fehlt nur **CHK+E+DY**. Die natürliche interne Oberfläche ist kreativ
`chekedy`, gelesen als **„kurz behandeln; Schritt schließen“**. Die Form wird
nicht als bereits belegt ausgegeben. Sie ist die konkrete Schreibvorhersage,
die ein Lehrmeister aus `cheky` (kurz behandeln), `cheeky` (länger behandeln)
und `chekeedy` (länger behandeln; schließen) ableiten würde.

Falls eine spätere freigegebene Seite genau diese Karte in einem kurzen
Behandlungsfeld zeigt, wächst das Modell. Falls eine ganz andere Funktion dort
notwendig wird, muss nicht das ganze System fallen, sondern speziell die
E/EE×Y/DY-Analogie bei CHK.
'''
 (OUT/'PASS921_PREDICTED_MISSING_CARD.md').write_text(prediction,encoding='utf-8')
 report=f'''# Pass 921 — Bedeutungswürfel

## Ergebnis

Das Schreibsystem besitzt jetzt {len(pairs)} konkrete Minimalpaare. Jede Paarzeile
ändert genau eine Achse: Handlung, Grad, Ende, Menge, Richtung, Weg oder Reihenfolge.
Die 19 `q`-Paare ändern dagegen ausdrücklich **keine** Bedeutung; sie markieren
nur den Eintritt nach einem geschlossenen Feld.

Der stärkste Würfel ist `OK/SH/CHK × E/EE × Y/DY`. Elf seiner zwölf Zellen sind
auf den 14 Seiten sichtbar. Die einzige fehlende Zelle ist `CHK+E+DY`, kreativ
vorhergesagt als **`chekedy` = kurz behandeln; schließen**.

## Warum das ein Fortschritt ist

Wir raten nun nicht mehr für jede Oberfläche eine neue Langglosse. Ein Schreiber
kann gezielt eine einzige Achse ändern:

- `okain → okaiin`: Portion → Sollmaß;
- `okar → okal`: Quelle → Ziel;
- `okedy → okeedy`: kurz → länger;
- `okey → okedy`: offen/verfügbar → geschlossen;
- `okey → shey → cheky`: ansetzen → halten → behandeln.

## Nächster Schritt

Nun wird geprüft, welche der 53 Kerne noch keinen solchen Kontrastpartner haben.
Diese isolierten Kerne sind die verbleibenden Kandidaten für echte gelernte
Ganzwörter; alles mit einem Partner bleibt produktive Fachkürzung.
'''
 (OUT/'PASS921_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS921_3X2X2_ACTION_CUBE.tsv','PASS921_25_MINIMAL_CONTRASTS.tsv','PASS921_19_Q_ALLOGRAPHS.tsv','PASS921_PREDICTED_MISSING_CARD.md','PASS921_REPORT.md']
 s={'status':'BUILT','cube_cells':len(lattice),'observed_cells':sum(x['status']=='OBSERVED' for x in lattice),'predicted_cells':sum(x['status'].startswith('PREDICTED') for x in lattice),'contrasts':len(pairs),'q_allographs':len(allographs),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS921_BUILD_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
