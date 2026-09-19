import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
parser=argparse.ArgumentParser();parser.add_argument('--register',action='store_true');args=parser.parse_args()
old='experiments/yolo/gdt976_dioscorides_shared_referent_projection/';source='experiments/yolo/gdt963_dioscorides_complete_content_code/'
up=[source+n for n in ['src/SOURCE.json','src/ALIASES.json','METHOD.md','REPORT.md']]+[old+n for n in ['artifacts/DOMAINS.json','artifacts/CANDIDATES.json.gz','artifacts/RESULT.json','METHOD.md','REPORT.md']]+['docs/VOYNICH_DATA_SCOPE.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 write(lock,dict(stage='REGISTERED_FOUR_ATOM_FOLLOWUP_ON_EXPOSED_DOMAIN',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={p.relative_to(R).as_posix():sha(p) for p in paths}))
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());result=E/'artifacts/RESULT.json';validation=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Shared leaf and breadth projection of all GDT976 candidates',question='Can each frozen name-code/page candidate extend to common LEAF and BROAD values across four complete records on distinct leaves?',status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Existential necessary four-atom projection only; one witness is not exhaustive new-code identification; no full code or meaning.',dependencies=['GDT963','GDT976'],inputs=[dict(path=n,sha256=sha(R/n),role='fixed_input') for n in up],outputs=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation=dict(status=json.loads(validation.read_text())['status'] if validation.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if validation.exists() else None))
m['commands']['validate']=f'python3 {rel}/src/validate.py --full'
m['artifact_policy']['large_artifact_justification']='Complete 8990-case prediction table and factored witness/exhaustion certificates; compressed certificate JSON retained to reproduce every status without selecting favorable cases.'
write(E/'experiment.json',m);print(m['status'])
