import hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parent;r=b.parents[4]
for p,h in json.loads((b/'SOURCE.json').read_text()).items():assert hashlib.sha256((r/p).read_bytes()).hexdigest()==h
print('PASS: source bytes only; no semantic validation')
