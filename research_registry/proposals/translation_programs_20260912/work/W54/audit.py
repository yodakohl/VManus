from pathlib import Path
import csv,json,hashlib,collections
D=Path(__file__).parent
S=D.parent/'W41'
e=list(csv.DictReader((S/'EVENTS.tsv').open(),delimiter='\t'))
spec=json.loads((S/'SPEC.json').read_text())
rows=[]
for world in sorted({r['world'] for r in e}):
 for record in spec['records']:
  x=[r for r in e if r['world']==world and r['record']==record]
  heat=[r for r in x if r['kind']=='HEAT']; transfer=[r for r in x if r['kind']=='TRANSFER']; marker=[r for r in x if r['kind']=='MARKER']
  rows.append(dict(world=world,record=record,heat=len(heat),transfer=len(transfer),marker=len(marker),heat_patient_B=sum(r['patient']==record+':B' for r in heat),transfer_destination_B=sum(r['destination']==record+':B' for r in transfer),heat_actor_B=sum(r['actor_before']==record+':B' for r in heat),heat_patient_missing=sum(r['patient']=='MISSING' for r in heat),events=';'.join(r['at']+':'+r['kind']+':patient='+r['patient']+':destination='+r['destination'] for r in x)))
with (D/'ALL_RECORDS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
# Preserve every already-exposed complete source line, without selecting words.
lines=[l for l in (S/'READING.md').read_text().splitlines() if l.startswith('f83r.')]
(D/'COMPLETE_LINES.md').write_text('# Vollständige exponierte W41-Zeilen\n\n'+'\n\n'.join(lines)+'\n')
result=dict(status='EXISTING_MODEL_ROLE_AUDIT',worlds=6,records_per_world=7,event_rows=len(e),complete_lines=len(lines),heat_patient_B=sum(r['heat_patient_B'] for r in rows),new_semantic_model=False,confirmed_words=[],independent_meaning_confirmation=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
