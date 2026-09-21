import csv, hashlib, itertools, json
from datetime import datetime, timezone
from pathlib import Path
E = Path(__file__).resolve().parents[1]
R = E.parents[2]
A = E / 'artifacts'
def read(p): return json.loads(Path(p).read_text())
def write(p, x): Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def source(): return read(E/'src/SOURCE.json')
def spec(): return read(E/'src/SPEC.json')
def table(p, rows):
    with Path(p).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(rows)
def check_lock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items(): assert sha(R/p)==h,p
def worlds():
    out=[]
    for same in [False, True]:
        people=['A'] if same else ['A','W']
        keys=list(itertools.product(people,['P_rite','P_attach','P_purpose']))
        for bits in itertools.product([False,True], repeat=len(keys)):
            for pure in itertools.product([False,True], repeat=len(people)):
                out.append(dict(id=f'W{len(out):03}', actor='A',recipient='A' if same else 'W',
                    knowledge={p:{q:bits[keys.index((p,q))] for q in ['P_rite','P_attach','P_purpose']} for p in people},
                    purity=dict(zip(people,pure))))
    assert len(out)==272
    return out
def good_world():
    return dict(id='POSITIVE',actor='A',recipient='W',knowledge={'A':dict.fromkeys(['P_rite','P_attach','P_purpose'],True),'W':dict.fromkeys(['P_rite','P_attach','P_purpose'],False)},purity={'A':True,'W':True})
