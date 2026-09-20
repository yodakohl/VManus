#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
ap=argparse.ArgumentParser();ap.add_argument('--lock',action='store_true');ap.add_argument('--status',default='REGISTERED_UNSCORED');a=ap.parse_args();s=read(E/'src/SPEC.json')
inputs=[s['target'],s['source'],'experiments/yolo/gdt900_cumanicus_complete_trilingual_tables/artifacts/TARGET_VALIDATION.json']
assert sha(R/s['target'])==s['target_sha256']
science=['METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/core.py','src/run.py','src/validate.py','src/preflight.py']
if a.lock:write(E/'PREREG_LOCK.json',dict(files={n:sha(R/n) for n in inputs+[str((E/n).relative_to(R)) for n in science]}))
m=read(E/'experiment.json');m.update(question='Can both complete trilingual six-person tense tables share one exact concatenative stem/person/tense writer in all exposed whole-window candidates?',claim_ceiling='Conditional complete feature-table fit only; source identity and feature meanings assumed, no independent semantic confirmation.',dependencies=['GDT900','GDT419','GDT608','GDT892','GDT997'],status=a.status,inputs=[dict(path=n,sha256=sha(R/n),role='fixed_input') for n in inputs],outputs=[])
for p in sorted(E.rglob('*')):
 if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts and 'runtime' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=read(E/'artifacts/VALIDATION.json')['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
