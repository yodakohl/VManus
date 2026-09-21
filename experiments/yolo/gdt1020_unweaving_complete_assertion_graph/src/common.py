import datetime,hashlib,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def put(n,x):write(A/n,x)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def checklock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def inputs():return read(E/'src/SPEC.json'),read(E/'src/SOURCE.json')

def temporal_witness(events,edges):
    """Integer ranks solve all nonstrict/strict precedence difference bounds."""
    ranks={e['id']:0 for e in events}
    for _ in range(len(ranks)+1):
        changed=False
        for a,b,strict in edges:
            assert a in ranks and b in ranks
            value=ranks[a]+int(strict)
            if ranks[b]<value:ranks[b]=value;changed=True
        if not changed:return ranks
    raise ValueError('STRICT_TEMPORAL_CYCLE')
