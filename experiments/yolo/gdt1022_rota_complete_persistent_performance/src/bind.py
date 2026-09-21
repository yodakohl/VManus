from common import *
import argparse

p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
s=source();sources=[b['path'] for b in s['source_bindings']]+['research_registry/proposals/raw_f83r_rota_complete_persistent_voices_20260921.json']
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science=['DECISION.md','METHOD.md','PREREGISTRATION.md','artifacts/PREFLIGHT.json','artifacts/PREDICTIONS.tsv','artifacts/SOURCE_SCOPE_AUDIT.json']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file()]
    write(E/'PREREG_LOCK.json',dict(registered_utc=now(),files={p:sha(R/p) for p in sources+[str((E/f).relative_to(R)) for f in science]}))
m=read(E/'experiment.json');m.update(question='Does the complete fixed 62-group rota-instruction hypothesis compile every clause and preserve performer, part, cue and pause obligations throughout startup and all retained full-period executions?',claim_ceiling='Complete exploratory P12 projection only; 53 guessed meanings, 14 fitted productions and four external score referents; two diplomatic forms unbound; no translated word.',dependencies=['GDT578','GDT928','GDT970'],status=args.status,inputs=[dict(path=p,sha256=sha(R/p),role='fixed_input') for p in sources],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact'))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
