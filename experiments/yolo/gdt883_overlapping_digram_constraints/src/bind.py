#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser(); a.add_argument('--register',action='store_true'); a=a.parse_args()
spec=json.loads((E/'src/SPEC.json').read_text())
up=[spec['source_lines'],spec['sta_atlas'],'tools/guarded_tsv_query.py']
lock=E/'src/PREREG_LOCK.json'
if a.register:
 assert not lock.exists()
 put(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in [*sorted((E/'src').glob('*.py')),E/'src/SPEC.json',E/'METHOD.md',*[ROOT/n for n in up]]})
for n,v in json.loads(lock.read_text()).items(): assert sha(ROOT/n)==v,n
result=E/'artifacts/RESULT.json'; val=E/'artifacts/VALIDATION.json'
m=json.loads((E/'experiment.json').read_text()); rel=E.relative_to(ROOT).as_posix()
files=sorted(p for p in E.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='experiment.json')
m.update(title='Unknown overlapping-block code constraints',question='Do fixed overlapping pairs, and the implied fixed-window block class, admit an injective assignment on concordant literal or exact STA transcription units?',claim_ceiling='Exact fixed unit and overlap mechanism; no semantic, language, historical or general cipher identification.',status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED',dependencies=['GDT882'],inputs=[dict(path=n,sha256=sha(ROOT/n),role='frozen_source_or_reader') for n in up],outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in files],validation=dict(status='PASS' if val.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if val.exists() else None))
put(E/'experiment.json',m); print(m['status'])
