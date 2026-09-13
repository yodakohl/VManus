from pathlib import Path
import json,csv,re
import hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=Path('experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/GDT590_FOUR_BATH_READER.md').read_text()
r=list(csv.DictReader((D/'PASSAGES.tsv').open(),delimiter='\t'))
assert len(r)==4 and len({x['id'] for x in r})==4
assert [x['surface'] for x in r]==re.findall(r'Oberfläche: `([^`]+)`',s)
a,b='cheey','lsheey'
assert 'l'+a!=b and 'l'+a.replace('c','s',1)==b
# One edit cannot suffice: lengths differ by one, but deleting any single
# character from the longer string never yields the shorter.
assert all(b[:i]+b[i+1:]!=a for i in range(len(b)))
v=json.loads((D/'RESULT.json').read_text());assert v['contrast']['character_levenshtein']==2
assert 'lcheey' not in r[1]['surface'].split()
x=dict(status='PASS',scope='four-source coverage, source integrity and literal contrast only',semantic_judgments_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
