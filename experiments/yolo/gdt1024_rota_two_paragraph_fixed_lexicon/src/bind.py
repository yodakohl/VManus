from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
s=source();paths=[b['path'] for b in s['source_bindings']]+['research_registry/proposals/raw_f83r_rota_second_paragraph_frozen53_20260921.json']
paths += [str((OLD/f).relative_to(R)) for f in ['src/model.py','src/independent.py','src/SOURCE.json','artifacts/GRAPHS.json','artifacts/PERFORMANCES.json','REPORT.md','PREREG_LOCK.json']]
paths=list(dict.fromkeys(paths))
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science=['DECISION.md','METHOD.md','PREREGISTRATION.md','artifacts/PREFLIGHT.json','artifacts/PREDICTIONS.tsv','artifacts/SOURCE_SCOPE_AUDIT.json']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
    write(E/'PREREG_LOCK.json',dict(registered_utc=now(),files={p:sha(R/p) for p in paths+[str((E/f).relative_to(R)) for f in science]}))
m=read(E/'experiment.json');m.update(question='Can a complete second projected paragraph retain all 53 music meanings and constrain the same full performances without duplicate entry, role merger or phase reset?',claim_ceiling='Two projected paragraphs only; 18 new guesses and six fitted productions; four raw ZL gaps, IT conflict, no independent meaning.',dependencies=['GDT928','GDT940','GDT947','GDT970','GDT1022'],status=args.status,inputs=[dict(path=p,sha256=sha(R/p),role='fixed_input') for p in paths],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact'))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
