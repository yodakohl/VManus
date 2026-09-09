#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');a=a.parse_args()
up=['experiments/yolo/gdt882_additive_line_lattice/artifacts/SELECTED_LINES.json','experiments/yolo/gdt882_additive_line_lattice/artifacts/VALIDATION.json']
lock=E/'src/PREREG_LOCK.json'
if a.register:
 assert not lock.exists()
 paths=[*sorted((E/'src').glob('*.py')),*sorted((E/'src').glob('*.cpp')),E/'METHOD.md',*[ROOT/p for p in up]]
 put(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in paths})
for n,h in json.loads(lock.read_text()).items():assert sha(ROOT/n)==h,n
res=E/'artifacts/RESULT.json';val=E/'artifacts/VALIDATION.json';m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
files=sorted(p for p in E.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='experiment.json')
m.update(title='Exhaustive reversible three-state line endpoint machines',question='Can fixed character permutations on three states send a common start with nontrivial orbit to one common endpoint for all413 fixed GDT882 literal lines?',claim_ceiling='Exact reversible at-most-three-state mechanism on the declared literal lines; not group-product equality, general automata, historical script or meaning.',status=json.loads(res.read_text())['status'] if res.exists() else 'REGISTERED_UNSCORED',dependencies=['GDT882'],inputs=[dict(path=n,sha256=sha(ROOT/n),role='frozen_source_or_validation') for n in up],outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in files],validation=dict(status='PASS' if val.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if val.exists() else None))
put(E/'experiment.json',m);print(m['status'])
