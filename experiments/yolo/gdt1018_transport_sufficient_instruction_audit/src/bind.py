from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
s=inputs();sources=[v for k,v in s.items() if k.startswith('source_') or k in ('grammar','model','bit_replay','binding_checker')]
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    files=['DECISION.md','METHOD.md','PREREGISTRATION.md','artifacts/PREFLIGHT.json']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
    write(E/'PREREG_LOCK.json',dict(registered_utc=now(),files={p:sha(R/p) for p in sources+[str((E/f).relative_to(R)) for f in files]}))
m=read(E/'experiment.json');m.update(question='Which complete saved transport readings give sufficient instructions under every locally safe permitted load choice?',claim_ceiling='Conditional fixed-witness instruction adequacy; no full extension-space exclusion, independent meaning or significance.',status=args.status,dependencies=['GDT993','GDT994','GDT1006','GDT1011','GDT1013'],inputs=[dict(path=p,sha256=sha(R/p),role='fixed_input') for p in sources],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact'))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
