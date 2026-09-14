from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
base=[r for r in csv.DictReader((D.parent/'W63/ALIGNMENT.tsv').open(),delimiter='\t') if r['model']=='N'];rs=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));changes=list(csv.DictReader((D/'NEW_ASSUMPTIONS.tsv').open(),delimiter='\t'))
assert len(rs)==1160 and len(changes)==32
for m,lex in {'F':{'solchey':'dasselbe Material','okain':'Maß P'},'T':{'solchey':'nächster Arbeitsgang','okain':'Zusatz E'}}.items():
 rows=[r for r in rs if r['model']==m];assert [(r['at'],r['word']) for r in rows]==[(r['at'],r['word']) for r in base]
 for r,b in zip(rows,base):assert r['hypothesis']==lex.get(b['word'],b['hypothesis'])
assert changes==[r for r in rs if r['word'] in ('okain','solchey')]
v=dict(status='PASS',scope='complete1160positions and32explicit new assumptions',meaning_validated=False,reference_identity_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
