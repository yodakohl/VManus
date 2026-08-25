#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent
B924=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
B931=H.parent/'sidequest_semantic_bilevel_component_dictionary_nine_hundred_thirty_first'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

ROOTS=['P','OK','CH','K','O','T','S','CTH','R','CHK','CHD','SH','CPH','SOLK']
BASE={'P':'p','OK':'ok','CH':'ch','K':'k','O':'o','T':'t','S':'s','CTH':'cth','R':'r','CHK':'chk','CHD':'ched','SH':'sh','CPH':'cph','SOLK':'solk'}
GRADES=['NONE','E','EE','EEE'];ENDS=['Y','DY']
comp={r['component']:r for r in read(B931/'PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv')}
cards=read(B924/'PASS924_1384_CURRENT_CARD_DICTIONARY.tsv')
recipes=defaultdict(list);surface_recipes=defaultdict(set)
for r in cards:
 recipes[r['component_recipe']].append(r)
 for s in r['surfaces'].split('|'):surface_recipes[s].add(r['component_recipe'])

def stem(root,grade):
 b=BASE[root]
 if grade=='NONE':return b
 n={'E':1,'EE':2,'EEE':3}[grade]
 if root=='CHK':return 'ch'+'e'*n+'k'
 return b+'e'*n

def candidate_surface(root,grade,end):
 # CHK writes part of the grade inside CHEK/CHEEK and repeats the grade vowel
 # before the closed DY endpoint.  This reproduces CHEKY/CHEEKY/CHEKEEDY and
 # yields the deliberately predicted missing CHEKEDY cell.
 if root=='CHK':
  if grade=='NONE': return 'chky' if end=='Y' else 'chkdy'
  if grade=='E': return 'cheky' if end=='Y' else 'chekedy'
  if grade=='EE': return 'cheeky' if end=='Y' else 'chekeedy'
  return 'cheeeky' if end=='Y' else 'chekeeedy'
 return stem(root,grade)+('y' if end=='Y' else 'dy')

grid=[]
support={}
for root in ROOTS:
 support[root]=sum(1 for g in GRADES for end in ENDS if '+'.join(x for x in (root,None if g=='NONE' else g,end) if x) in recipes)
for root in ROOTS:
 for grade in GRADES:
  for end in ENDS:
   q='+'.join(x for x in (root,None if grade=='NONE' else grade,end) if x)
   seen=recipes.get(q,[])
   cand=candidate_surface(root,grade,end)
   collision=sorted(surface_recipes.get(cand,set())-{q})
   comps=q.split('+')
   abstract=' → '.join(comp[x]['abstract_core_de'] for x in comps)
   prose='; '.join(comp[x]['workshop_prose_de'] for x in comps)
   address='; '.join(comp[x]['owner_address_de'] for x in comps)
   if seen:status='OBSERVED'
   elif collision:status='MISSING_SEMANTIC_CELL__SURFACE_COLLISION_REQUIRES_WRAPPER'
   elif support[root]>=5:status='STRONG_PREDICTION'
   elif support[root]>=3:status='WORKING_PREDICTION'
   else:status='CREATIVE_PREDICTION'
   grid.append({'root':root,'grade':grade,'endpoint':end,'component_recipe':q,'paradigm_support_cells':support[root],'status':status,'observed_surfaces':'|'.join(r['surfaces'] for r in seen) or 'NONE','candidate_bare_surface':cand,'candidate_q_entry_surface':'q'+cand,'surface_collision_recipes':'|'.join(collision) or 'NONE','abstract_prediction_de':abstract,'workshop_prediction_de':prose,'owner_address_prediction_de':address})
write('PASS933_112_PARADIGM_CELLS.tsv',list(grid[0]),grid)
pred=[r for r in grid if r['status']!='OBSERVED'];pred.sort(key=lambda r:(0 if r['status']=='STRONG_PREDICTION' else 1 if r['status']=='WORKING_PREDICTION' else 2 if r['status']=='CREATIVE_PREDICTION' else 3,-int(r['paradigm_support_cells']),r['root'],r['grade'],r['endpoint']))
write('PASS933_MISSING_CELL_PREDICTIONS.tsv',list(pred[0]),pred)

book=['# Pass 933 — vorhergesagte Kartenkompositionen','',
      'Diese Formen sind kreative Vorhersagen der aktuellen Stamm- und Rendererregel. Ein Kandidat ist keine neu beobachtete Voynichkarte; er sagt, welche Bedeutung eine solche Karte auf einer später freigegebenen Seite haben müsste.','']
for i,r in enumerate(pred[:40],1):
 book += [f"## {i}. `{r['candidate_bare_surface']}` / `{r['candidate_q_entry_surface']}`",'',f"Rezept `{r['component_recipe']}`: Werkstatt **{r['workshop_prediction_de']}**; Bild **{r['owner_address_prediction_de']}**. Status: {r['status']}.",'']
(H/'PASS933_TOP_PREDICTIONS.md').write_text('\n'.join(book).rstrip()+'\n',encoding='utf-8')
counts=Counter(r['status'] for r in grid)
chek=next(r for r in grid if r['component_recipe']=='CHK+E+DY')
report=f"""# Pass 933 — die Grammatik sagt neue Karten voraus

## Ergebnis

Vierzehn Tätigkeitskerne wurden mit vier Graden und zwei Endpunkten zu 112
semantischen Zellen gekreuzt. Beobachtet sind {counts['OBSERVED']};
{counts['STRONG_PREDICTION']} fehlende Zellen sind durch ein dichtes
Nachbarparadigma stark vorhergesagt, {counts['WORKING_PREDICTION']} weitere sind
brauchbare Arbeitsvorhersagen. {counts['MISSING_SEMANTIC_CELL__SURFACE_COLLISION_REQUIRES_WRAPPER']}
Zellen brauchen wegen einer bereits belegten Oberfläche einen Wrapper oder ein
anderes Allograph.

## Konkreteste neue Form

`{chek['candidate_bare_surface']}` = `{chek['component_recipe']}` =
„{chek['workshop_prediction_de']}“. Im Bildregister wäre dieselbe Komposition
„{chek['owner_address_prediction_de']}“. Das ist die bereits im 3×2×2-Raster
fehlende kurze CHK-Schlussform.

## Warum das wichtig ist

Unsere Bedeutungen sind jetzt vorwärtsgerichtet. Wir müssen eine neue Oberfläche
nicht nachträglich mit einem langen Satz belegen: Stamm, Grad und Endpunkt sagen
vorab, welche kurze Funktion sie haben müsste. Oberflächenkollisionen sind dabei
kein Scheitern; sie zeigen, an welchen Stellen der Schreiber einen q-Träger,
Wrapper oder gelernten Allograph braucht.
"""
(H/'PASS933_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS933_112_PARADIGM_CELLS.tsv','PASS933_MISSING_CELL_PREDICTIONS.tsv','PASS933_TOP_PREDICTIONS.md','PASS933_REPORT.md']
(H/'PASS933_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','cells':len(grid),'counts':dict(counts),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
