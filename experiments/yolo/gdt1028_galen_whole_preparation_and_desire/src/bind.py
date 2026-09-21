from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
s=source();paths=[b['path'] for b in s['scope_receipts']]+['research_registry/proposals/raw_galen_2442_target_development_20260921.json']
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science=['DECISION.md','METHOD.md','PREREGISTRATION.md','artifacts/PREFLIGHT.json','artifacts/PREDICTIONS.tsv']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
    write(E/'PREREG_LOCK.json',dict(registered_utc=now(),files={p:sha(R/p) for p in paths+[str((E/f).relative_to(R)) for f in science]}))
m=read(E/'experiment.json');m.update(question='Does the complete49-group RAW496 Galen preparation/desire reading preserve food, water and own-juice identity without conflating intention, capability and actuality?',claim_ceiling='Conditional whole II44.2 hypothesis only;36 guesses,5 productions,15 bindings plus optional B16. Three ownership-rival denotations rebound; ideal rival reinterprets one more. No source identification, physical or clinical observation, significance or independent meaning.',dependencies=['GDT928','GDT762'],status=args.status,inputs=[dict(path=p,sha256=sha(R/p),role='fixed_input') for p in paths],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact'))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
