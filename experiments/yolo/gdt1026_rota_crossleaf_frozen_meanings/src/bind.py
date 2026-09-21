from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
s=source();paths=[b['path'] for b in s['source_bindings']]+['research_registry/proposals/raw_f76v_rota_complete_frozen71_scope_variants_20260921.json']
for base,files in [(OLD,['src/model.py','src/independent.py','src/common.py','src/SOURCE.json','src/SPEC.json','artifacts/GRAPHS.json','artifacts/PERFORMANCES.json','REPORT.md','PREREG_LOCK.json']),(SECOND,['src/model.py','src/independent.py','src/common.py','src/SOURCE.json','artifacts/GRAPHS.json','artifacts/DIPLOMATIC_SCOPE.json','REPORT.md','PREREG_LOCK.json'])]:
    paths += [str((base/f).relative_to(R)) for f in files]
paths=list(dict.fromkeys(paths))
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science=['DECISION.md','METHOD.md','PREREGISTRATION.md','artifacts/PREFLIGHT.json','artifacts/PREDICTIONS.tsv']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
    write(E/'PREREG_LOCK.json',dict(registered_utc=now(),files={p:sha(R/p) for p in paths+[str((E/f).relative_to(R)) for f in science]}))
m=read(E/'experiment.json');m.update(question='Can a complete55-group crossleaf paragraph preserve all71 existing hypothetical music values and both earlier paragraphs under two fixed negation scopes and all12 original source conditions?',claim_ceiling='Conditional150group account with20new guessed values,11new productions and10binding conventions; no source identification, independent meaning or confirmed words.',dependencies=['GDT928','GDT1022','GDT1024'],status=args.status,inputs=[dict(path=p,sha256=sha(R/p),role='fixed_input') for p in paths],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact'))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
