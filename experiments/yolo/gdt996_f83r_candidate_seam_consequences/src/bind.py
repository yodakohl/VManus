import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--status',default='REGISTERED_UNSCORED');p.add_argument('--lock',action='store_true');a=p.parse_args()
s=read(E/'src/SPEC.json');inputs=[s[k] for k in ('image_path','source_packet','grammar','source_draft')]
scientific=['METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/run.py','src/validate.py']
if a.lock:write(E/'PREREG_LOCK.json',dict(files={n:sha(R/n) for n in inputs+[str((E/n).relative_to(R)) for n in scientific]}))
m=read(E/'experiment.json');m.update(question='Do two fixed image seams support the physical token premises of the complete GDT993 reading?',claim_ceiling='One source-aware native AI judgment and formal endpoint-pattern consequences; no lexical or authorial word-boundary confirmation.',status=a.status,dependencies=['GDT993','GDT994','GDT852','GDT864'],inputs=[dict(path=n,role='fixed_input',sha256=sha(R/n)) for n in inputs],outputs=[])
for path in sorted(E.rglob('*')):
 if path.is_file() and path.name!='experiment.json' and '__pycache__' not in path.parts and 'runtime' not in path.parts:
  m['outputs'].append(dict(path=str(path.relative_to(R)),role='primary_report' if path.name=='REPORT.md' else 'source_or_artifact',sha256=sha(path)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=read(E/'artifacts/VALIDATION.json')['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
