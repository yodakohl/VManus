from pathlib import Path
import re,json,csv,hashlib
D=Path(__file__).parent
S=Path('experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/GDT590_FOUR_BATH_READER.md')
text=S.read_text();blocks=re.split(r'(?m)^## ',text)[1:]
checks={
'G407-E2404':('Station vorbereiten, dann Körper im Bad','Wechsel des Governors erlaubt neue Körperrolle','Stationsansatz bleibt Badeobjekt','Keine Empfindung/Reaktion oder identifizierte neue Person'),
'G407-E2637':('cheey Körper, später lsheey Station','Host-Blocker setzt die Rollen; Ganzwortkontrast ist nicht nur l','Unterschiedliche Operations-/Relationsformen am Stationsansatz','cheey zu lsheey verändert l und ch/sh; kein reiner l-Kontrast'),
'G407-E2652':('Station vorher, Körper unter bloßem sh','Entfernte AIIN/Y-Bindung und Governorwechsel','Station bleibt Objekt des Bades','Kein exaktes bloßes-SH-Körperminimalpaar laut Primärbericht'),
'G407-E3182':('Grad II, anschließend Grad I am Körper','Grade und Körperrollen schon vorausgesetzt','Grad II und Grad I am Stationsansatz','Zweistufigkeit setzt keinen menschlichen Träger voraus; keine Temperaturidentifikation')}
rows=[]
for b in blocks:
 key=b.split()[0]
 if key not in checks:continue
 surface=re.search(r'Oberfläche: `([^`]+)`',b).group(1)
 a,c,r,g=checks[key]
 rows.append(dict(id=key,surface=surface,body_reading=a,assumption=c,station_rival=r,missing_discriminator=g,independent_body_consequence='NOT_IDENTIFIED'))
assert {r['id'] for r in rows}==set(checks)
with (D/'PASSAGES.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def lev(a,b):
 d=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  n=[i]
  for j,y in enumerate(b,1):n.append(min(n[-1]+1,d[j]+1,d[j-1]+(x!=y)))
  d=n
 return d[-1]
a,b='cheey','lsheey'
result=dict(status='FOUR_PRIOR_PREFERENCES_AUDITED',passages=4,independent_body_consequence_identified=0,contrast=dict(left=a,right=b,character_levenshtein=lev(a,b),prefix_l_only=('l'+a==b),required_l_only_counterpart='lcheey',counterpart_in_same_passage='lcheey' in rows[1]['surface'].split()),semantic_meanings_confirmed=[],new_admission=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
