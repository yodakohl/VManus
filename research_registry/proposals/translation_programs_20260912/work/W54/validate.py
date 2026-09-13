from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
src=list(csv.DictReader((D.parent/'W41/EVENTS.tsv').open(),delimiter='\t'))
out=list(csv.DictReader((D/'ALL_RECORDS.tsv').open(),delimiter='\t'))
assert len(src)==162 and len(out)==42
for r in out:
 events=[e for e in src if (e['world'],e['record'])==(r['world'],r['record'])]
 for kind in ('HEAT','TRANSFER','MARKER'): assert int(r[kind.lower()])==sum(e['kind']==kind for e in events)
 assert int(r['heat_patient_B'])==sum(e['kind']=='HEAT' and e['patient']==r['record']+':B' for e in events)==0
 assert int(r['transfer_destination_B'])==sum(e['kind']=='TRANSFER' and e['destination']==r['record']+':B' for e in events)
 assert int(r['heat_actor_B'])==sum(e['kind']=='HEAT' and e['actor_before']==r['record']+':B' for e in events)
 assert int(r['heat_patient_missing'])==sum(e['kind']=='HEAT' and e['patient']=='MISSING' for e in events)
assert sum(int(r['heat'])+int(r['transfer'])+int(r['marker']) for r in out)==len(src)
a=[l for l in (D/'COMPLETE_LINES.md').read_text().splitlines() if l.startswith('f83r.')]
b=[l for l in (D.parent/'W41/READING.md').read_text().splitlines() if l.startswith('f83r.')]
assert a==b and len(a)==51
v=dict(status='PASS',scope='complete existing event aggregation and source integrity',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
