import csv,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def source():return read(E/'src/SOURCE.json')
def spec():return read(E/'src/SPEC.json')
def cases():return read(E/'src/CASES.json')
def table(p,rows):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def read_table(p):
 with Path(p).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def check_lock():
 for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
