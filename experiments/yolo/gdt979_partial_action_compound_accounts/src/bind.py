import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
up=['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json','experiments/yolo/gdt928_multi_anchor_complete_paragraphs/REPORT.md','experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json','research_registry/proposals/raw_permission_partial_action_compounds.json','research_registry/proposals/raw_benedict_status_reentry_rule.json','research_registry/work_batches/ten_hours_20260915/FINITE_COMPOSITION_CONTENT_RAW_SUPPLY_20260919.md','research_registry/work_batches/ten_hours_20260915/PARTIAL_ACTION_DECISION_20260919.md','docs/VOYNICH_DATA_SCOPE.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 write(lock,dict(stage='REGISTERED_PARTIAL_ACTION_COMPOUND_ACCOUNTS',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={p.relative_to(R).as_posix():sha(p) for p in paths}))
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Complete partial-action compound accounts under one shared code',question='Can complete exposed paragraphs on distinct leaves jointly instantiate the fixed six-atom partial-action contract, with and without permission, under one common bounded code?',status=json.loads(rr.read_text())['status'] if rr.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Finite stipulated state/code fit only; uncertain sources and caps unresolved; no independently bound institutional or other meanings.',dependencies=['GDT928','GDT915','GDT608','GDT885','GDT903','GDT930','GDT949'],inputs=[dict(path=n,sha256=sha(R/n),role='fixed_input') for n in up],outputs=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation=dict(status=json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if vv.exists() else None))
m['commands']['validate']='python3 '+rel+'/src/validate.py --full'
write(E/'experiment.json',m);print(m['status'])
