import argparse
from common import *
p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
s=source();paths=[b['path'] for b in s['scope_receipts']]+['research_registry/proposals/raw_vitruvius_ix89_complete_continuation_20260921.json','experiments/yolo/gdt885_reversible_three_state_line_machine/REPORT.md','experiments/yolo/gdt903_universal_reversible_line_action/REPORT.md','experiments/semantic_assumptions/results/f69m001_target_validation.md'];paths=sorted(set(paths))
if args.lock:
 assert not (E/'PREREG_LOCK.json').exists()
 science=['DECISION.md','METHOD.md','PREREGISTRATION.md','artifacts/PREFLIGHT.json','artifacts/PREDICTIONS.tsv']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
 write(E/'PREREG_LOCK.json',dict(registered_utc=now(),files={p:sha(R/p) for p in paths+[str((E/f).relative_to(R)) for f in science]}))
m=read(E/'experiment.json');m.update(question='Does the complete40-group RAW503 clock hypothesis preserve coupled motion, seasonal display and same-month references while separating unbound actuation and temporal consequences?',claim_ceiling='33 guessed values,27 singleton forms,4 productions/3 discontinuous,20 bindings plus explicit temporal witness convention. Conditional source account, not a word/source identity or independent meaning confirmation.',status=args.status,dependencies=['GDT928','GDT214','GDT885','GDT903'],inputs=[dict(path=p,sha256=sha(R/p),role='fixed_input') for p in paths],outputs=[])
for p in sorted(E.rglob('*')):
 if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact'))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
