import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
up=['experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/experiment.json', 'experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/src/SPEC.json']
lock=E/'src/PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    bound=[*sorted((E/'src').glob('*.py')),E/'src/SPEC.json',E/'METHOD.md',E/'PREREGISTRATION.md']+[ROOT/n for n in up]
    write(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in bound})
for name,h in json.loads(lock.read_text()).items():assert sha(ROOT/name)==h,name
result=E/'artifacts/RESULT.json';status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED'
outputs=sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and p.name!='experiment.json')
m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
m.update(title='Exact-unspaced-whole spacing context transfer',question='Does joined versus one-cut spacing predict external neighbors conditional on exact W in matched held-folio pairs?'     ,claim_ceiling='Exploratory text-level context transfer only; no untouched confirmation, exact null probability, meaning, language or authorial intent.',status=status,dependencies=['GDT851'],inputs=[{'path':n,'sha256':sha(ROOT/n),'role':'frozen_source_or_extractor'} for n in up],outputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in outputs],validation={'status':'PASS' if result.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if result.exists() else None})
source_spec=json.loads((E/'src/SPEC.json').read_text())
m['inputs'].append({'path':source_spec['source'],'sha256':source_spec['source_sha256'],'role':'published_source_hash_from_GDT851_manifest_checked_on_GO'})
write(E/'experiment.json',m);print(status)
