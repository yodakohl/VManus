import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
up=['experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_unit_inventory.tsv', 'experiments/yolo/gdt605_multisymbol_unit_alphabet/REPORT.md', 'experiments/yolo/gdt605_multisymbol_unit_alphabet/METHOD.md', 'experiments/yolo/gdt605_multisymbol_unit_alphabet/src/unit_inventory.py', 'experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py']
lock=E/'src/PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    bound=[*sorted((E/'src').glob('*.py')),E/'src/SPEC.json',E/'METHOD.md',E/'PREREGISTRATION.md']+[ROOT/n for n in up]
    write(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in bound})
for name,h in json.loads(lock.read_text()).items():assert sha(ROOT/name)==h,name
result=E/'artifacts/RESULT.json';status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED'
outputs=sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and p.name!='experiment.json')
m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
m.update(title='Free unique decodability of published GDT605 codewords',question='Is the exact published98-unit collapsed-symbol code freely uniquely decodable?'     ,claim_ceiling='Finite aggregate-code property only; no manuscript sequence, canonical BPE legality, synchronization or semantic claim.',status=status,dependencies=['GDT605'],inputs=[{'path':n,'sha256':sha(ROOT/n),'role':'frozen_source_or_extractor'} for n in up],outputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in outputs],validation={'status':'PASS' if result.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if result.exists() else None})
write(E/'experiment.json',m);print(status)
