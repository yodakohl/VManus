from pathlib import Path
import json,hashlib,itertools
B=Path(__file__).resolve().parent;R=B.parents[2]
p=B/'COVER_COLUMN_REPEAT_SCOPE_20261011.json';d=json.loads(p.read_text())
for name,h in d['primary_hashes'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h
c=d['countermodel'];tables=c['columns_source_to_packet'];inverse=[{w:i for i,w in enumerate(col)} for col in tables];assert all(len(x)==4 for x in inverse)
count=0
for phase in range(3):
 for n in range(5):
  for message in itertools.product(range(4),repeat=n):
   output=[tables[(phase+i)%3][s] for i,s in enumerate(message)];restored=tuple(inverse[(phase+i)%3][w] for i,w in enumerate(output));assert restored==message;count+=1
witness=[tables[i][s] for i,s in enumerate(c['witness_source'])];assert witness==c['witness_output']==['W0']*3;assert [inverse[i]['W0'] for i in range(3)]==[0,1,2]
# Exhaust all8possible three-phase memberships for a fixed packet.
cases=0
for bits in itertools.product([False,True],repeat=3):
 sets=[({'W0'} if b else set()) for b in bits];intersection=set.intersection(*sets);valid=all('W0' in sets[i] for i in range(3));assert valid==('W0' in intersection);cases+=1
out={'status':'PASS','complete_roundtrips':count,'three_phase_membership_cases':cases,'repeat_output':witness,'decoded_source':[0,1,2],'scope':'Formal countermodel and intersection condition only; no actual historical-table census, native count or meaning.'};(B/'COVER_COLUMN_REPEAT_VALIDATION_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
