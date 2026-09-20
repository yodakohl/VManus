import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');a=p.parse_args()
s=read(E/'src/SPEC.json');inputs=[s[k] for k in ('source_paragraphs','source_draft','grammar','model','old_cases')]+['experiments/yolo/gdt993_complete_transport_consequence_audit/src/validate.py','experiments/yolo/gdt994_frozen_transport_whole_transfer/src/validate.py']
science=['METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/core.py','src/run.py','src/validate.py','src/preflight.py']
if a.lock:write(E/'PREREG_LOCK.json',dict(files={n:sha(R/n) for n in inputs+[str((E/n).relative_to(R)) for n in science]}))
m=read(E/'experiment.json');m.update(question='Can additional complete exposed paragraphs extend the frozen transport construction with one existing terminal value per new whole spelling?',claim_ceiling='Finite grammatical completion and conditional witness replay;all meanings assumed,no independent translation or joint alias confirmation.',dependencies=['GDT993','GDT994','GDT996'],status=a.status,inputs=[dict(path=n,sha256=sha(R/n),role='fixed_input') for n in inputs],outputs=[])
for path in sorted(E.rglob('*')):
 if path.is_file() and path.name!='experiment.json' and '__pycache__' not in path.parts and 'runtime' not in path.parts:m['outputs'].append(dict(path=str(path.relative_to(R)),role='primary_report' if path.name=='REPORT.md' else 'source_or_artifact',sha256=sha(path)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=read(E/'artifacts/VALIDATION.json')['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
