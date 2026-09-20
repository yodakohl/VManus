#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
INPUTS=['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json']
INPUTS+=['experiments/yolo/gdt987_anastasia_finite_word_proof/'+p for p in ['METHOD.md','src/finite.py','src/validate.py','artifacts/PRE_RUN_FIXTURES.json']]
INPUTS+=['experiments/yolo/'+slug+'/REPORT.md' for slug in ['gdt969_fibonacci_generated_root_trace','gdt971_alloy_numeral_binding_control','gdt991_smaragdina_complete_form_pattern']]
INPUTS+=['research_registry/proposals/raw_global_simultaneous_grouping.json']
INPUTS+=['research_registry/work_batches/ten_hours_20260915/'+p for p in ['SUNZI_SECTION26_SOURCE_AUDIT_20260920.md','SOURCE_TREE_REVIEW_20260920.md','SUNZI_WHOLE_CONTENT_DECISION_20260920.md']]
SCIENCE=['METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/build_source.py','src/preflight.py','src/shared.py','src/run.py','src/validate.py','artifacts/PRE_RUN_FIXTURES.json','artifacts/SOURCE_PREDICTIONS.json','artifacts/WORKER_IO_FIXTURES.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');a=p.parse_args();lock=E/'PREREG_LOCK.json'
if a.register:
 assert not lock.exists()
 names=INPUTS+[str((E/n).relative_to(R)) for n in SCIENCE]
 lock.write_text(json.dumps(dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={n:sha(R/n) for n in names}),indent=2)+'\n')
else:
 for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());m.update(title='Complete contextual grouping and reconstruction source reading',question='Can the full Sunzi question/answer/method/general-rule content fit any whole admitted paragraph under either fixed contextual tree code?',status=a.status,dependencies=['GDT928','GDT969','GDT971','GDT987','GDT991'],claim_ceiling='Conditional complete source writing only; no identified language, word, unique key or independently confirmed meaning.',inputs=[dict(path=n,role='fixed_input',sha256=sha(R/n)) for n in INPUTS],outputs=[])
for f in sorted(E.rglob('*')):
 if f.is_file() and f.name!='experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:m['outputs'].append(dict(path=str(f.relative_to(R)),role='primary_report' if f.name=='REPORT.md' else 'source_or_artifact',sha256=sha(f)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=json.loads((E/'artifacts/VALIDATION.json').read_text())['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
(E/'experiment.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(status=m['status'],inputs=len(m['inputs']),outputs=len(m['outputs']))))
