import datetime,hashlib,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def put(n,x):write(A/n,x)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,R/p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def inputs():return read(E/'src/SPEC.json')
def checklock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
