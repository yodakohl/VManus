#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
P = 'experiments/yolo/gdt990_smaragdina_complete_role_frames/'
INPUTS = [P+x for x in ('src/SOURCE.json','METHOD.md','DECISION.md','PREREG_LOCK.json','REPORT.md',
          'INTERRUPTION_NOTE.md','artifacts/INTERRUPTED_CASES.json.gz','artifacts/INTERRUPTED_CANDIDATES.tsv',
          'artifacts/INTERRUPTION_RESULT.json','artifacts/INTERRUPTION_VALIDATION.json')]
INPUTS += ['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json']
INPUTS += ['experiments/yolo/' + slug + '/' + f for slug, f in (
 ('gdt987_anastasia_finite_word_proof','METHOD.md'),('gdt978_dioscorides_all_recurrent_content','REPORT.md'),
 ('gdt984_name_code_remainder_prefix_capacity','REPORT.md'))]
SCIENCE = ['DECISION.md','METHOD.md','PREREGISTRATION.md','PRE_RUN_DEVELOPMENT.md',
 'src/SOURCE.json','src/prepare.py','src/pattern.py','src/reverse.py','src/fixtures.py','src/run.py','src/validate.py',
 'artifacts/PRE_RUN_FIXTURES.json','artifacts/SOURCE_PREDICTIONS.json']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

p = argparse.ArgumentParser()
p.add_argument('--register', action='store_true')
p.add_argument('--status', default='REGISTERED_UNSCORED')
a = p.parse_args()
lock = E / 'PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    names = INPUTS + [str((E / s).relative_to(ROOT)) for s in SCIENCE]
    lock.write_text(json.dumps(dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       files={n:sha(ROOT/n) for n in names}),indent=2)+'\n')
else:
    for n,h in json.loads(lock.read_text())['files'].items():
        assert sha(ROOT/n)==h,n
m=json.loads((E/'experiment.json').read_text())
m.update(title='Complete Tabula role-form pattern and original-code factorization',
 question='Can any of the1980interrupted GDT990cases realize its entire repeated root/slot sequence, and does a saved whole pattern factor into the unchanged original code?',
 status=a.status, dependencies=['GDT928','GDT978','GDT984','GDT987','GDT990'],
 claim_ceiling='Necessary pattern certificates or conditional complete code only; no identified language, unique code, search significance or independently confirmed meaning.',
 inputs=[dict(path=n,role='fixed_input',sha256=sha(ROOT/n)) for n in INPUTS],outputs=[])
for f in sorted(E.rglob('*')):
    if f.is_file() and f.name!='experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:
        m['outputs'].append(dict(path=str(f.relative_to(ROOT)),role='primary_report' if f.name=='REPORT.md' else 'source_or_artifact',sha256=sha(f)))
v=E/'artifacts/VALIDATION.json'
if v.exists():m['validation']=dict(status=json.loads(v.read_text())['status'],artifact=str(v.relative_to(ROOT)))
(E/'experiment.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps(dict(status=m['status'],inputs=len(m['inputs']),outputs=len(m['outputs']))))
