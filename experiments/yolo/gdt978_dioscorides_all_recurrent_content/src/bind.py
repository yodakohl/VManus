import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
a963='experiments/yolo/gdt963_dioscorides_complete_content_code/';a976='experiments/yolo/gdt976_dioscorides_shared_referent_projection/';a977='experiments/yolo/gdt977_dioscorides_leaf_breadth_projection/'
up=[a963+n for n in ['src/SOURCE.json','src/ALIASES.json','METHOD.md','REPORT.md']]+[a976+n for n in ['artifacts/DOMAINS.json','artifacts/CANDIDATES.json.gz','REPORT.md']]+[a977+n for n in ['artifacts/CASES.json.gz','artifacts/RESULT.json','REPORT.md']]+['docs/VOYNICH_DATA_SCOPE.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists();paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 write(lock,dict(stage='REGISTERED_ALL_RECURRENCE_NECESSARY_PROJECTION',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={p.relative_to(R).as_posix():sha(p) for p in paths}))
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='All recurrent Dioscorides content under one shared code',question='Can the unchanged four whole records jointly realize all78 recurrent atoms/358occurrences and208exact adjacent seams, relaxing only singleton runs?',status=json.loads(rr.read_text())['status'] if rr.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Necessary recurrent-code projection, not full singleton code or meaning; unknowns remain unknown, solver UNSAT not independently proved.',dependencies=['GDT963','GDT976','GDT977'],inputs=[dict(path=n,sha256=sha(R/n),role='fixed_input') for n in up],outputs=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation=dict(status=json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if vv.exists() else None))
write(E/'experiment.json',m);print(m['status'])
