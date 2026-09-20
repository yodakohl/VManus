import argparse,datetime
from common import *
ap=argparse.ArgumentParser();ap.add_argument('--lock',action='store_true');ap.add_argument('--status',default='REGISTERED_UNSCORED');args=ap.parse_args()
s=read(E/'src/SPEC.json');inputs=[s[k] for k in ('grammar','source_packet','source_draft','old_cases','model','independent_model','binding_checker','source_decision')]
science=['DECISION.md','METHOD.md','PREREGISTRATION.md','requirements.txt','src/SPEC.json','src/common.py','src/grammar.py','src/independent.py','src/bit_replay.py','src/prepare.py','src/preflight.py','src/run.py','src/validate.py','artifacts/PANEL.json','artifacts/PREDICTIONS.json','artifacts/PREFLIGHT.json']
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
if args.lock:
 assert not (E/'PREREG_LOCK.json').exists()
 write(E/'PREREG_LOCK.json',dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={p:sha(R/p) for p in inputs+[str((E/p).relative_to(R)) for p in science]}))
m=read(E/'experiment.json');m.update(question='Which original word roles and reference settings survive when all47old glosses are freed under the complete17clause three-cargo seven-voyage hypothesis?',claim_ceiling='Conditional content-template role recovery only; prior source/template exposure, no morphology, historical meaning, source identity or significance.',dependencies=['GDT993','GDT994','GDT1002','GDT1003','GDT1004','GDT1005'],status=args.status,inputs=[dict(path=p,role='fixed_input',sha256=sha(R/p)) for p in inputs],outputs=[])
for p in sorted(E.rglob('*')):
 if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts and 'runtime' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
m['artifact_policy']['large_artifact_justification']='Every evaluated full dictionary, complete clause tiling and32variant outcomes is retained, including all failed candidates and positive projection witnesses; large artifacts are needed for finite exhaustion and ambiguity audit.'
write(E/'experiment.json',m)
