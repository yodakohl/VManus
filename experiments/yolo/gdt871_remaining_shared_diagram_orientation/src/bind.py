import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
up=['experiments/semantic_assumptions/RBR002_F67R2_COMPLETE_UNDERLAYER_CAPACITY_METHOD.md','experiments/yolo/gdt867_shared_canvas_native_orientation/REPORT.md','experiments/yolo/gdt867_shared_canvas_native_orientation/src/PAGE_ADMISSIONS.tsv','experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv']
lock=E/'src/PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    bound=[*sorted((E/'src').glob('*.py')),E/'src/SPEC.json',E/'METHOD.md',E/'PREREGISTRATION.md',E/'SOURCES.json',E/'src/PAGE_ADMISSIONS.tsv']+[ROOT/n for n in up]
    write(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in bound})
for name,h in json.loads(lock.read_text()).items():assert sha(ROOT/name)==h,name
validation_file=E/'artifacts/VALIDATION.json'
validation_status=json.loads(validation_file.read_text())['status'] if validation_file.exists() else 'NOT_RUN'
result=E/'artifacts/RESULT.json';status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED'
outputs=sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and p.name!='experiment.json')
m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
m.update(title='Remaining shared diagram native orientation',question='What do the two remaining admitted diagram originals look like with explicit sibling-panel scope?',claim_ceiling='Personal orientation only; no count, direction, underlayer, glyph, ownership or meaning',status=status,dependencies=['GDT791','GDT867'],inputs=[{'path':n,'sha256':sha(ROOT/n),'role':'frozen_source_or_extractor'} for n in up],outputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in outputs],validation={'status':validation_status,'artifact':rel+'/artifacts/VALIDATION.json' if validation_file.exists() else None})
write(E/'experiment.json',m);print(status)
