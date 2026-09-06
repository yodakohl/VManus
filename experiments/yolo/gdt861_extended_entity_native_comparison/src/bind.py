import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
up=['experiments/yolo/gdt859_f56r_initial_bar_separator/REPORT.md', 'experiments/yolo/gdt860_extended_bar_entity_recurrence/REPORT.md', 'experiments/yolo/gdt860_extended_bar_entity_recurrence/artifacts/HITS.json', 'experiments/yolo/gdt860_extended_bar_entity_recurrence/artifacts/SOURCE_LINES.json']
lock=E/'src/PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    bound=[*sorted((E/'src').glob('*.py')),E/'src/SPEC.json',E/'src/PAGE_ADMISSIONS.tsv',E/'METHOD.md',E/'PREREGISTRATION.md']+[ROOT/n for n in up]
    write(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in bound})
for name,h in json.loads(lock.read_text()).items():assert sha(ROOT/name)==h,name
validation_file=E/'artifacts/VALIDATION.json'
validation_status=json.loads(validation_file.read_text())['status'] if validation_file.exists() else 'NOT_RUN'
result=E/'artifacts/RESULT.json';status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED'
outputs=sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and p.name!='experiment.json')
m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
m.update(title='Two exact entity locator native comparisons',question='Do two registered literal text locators permit localized visible extended upper connection comparisons?',claim_ceiling='Two same-photo native comparisons only; no glyph identity, paired code, pen motion or meaning',status=status,dependencies=['GDT859','GDT860'],inputs=[{'path':n,'sha256':sha(ROOT/n),'role':'frozen_source_or_extractor'} for n in up],outputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in outputs],validation={'status':validation_status,'artifact':rel+'/artifacts/VALIDATION.json' if validation_file.exists() else None})
write(E/'experiment.json',m);print(status)
