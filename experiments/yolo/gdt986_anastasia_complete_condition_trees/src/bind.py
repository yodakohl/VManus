#!/usr/bin/env python3
"""Bind only this experiment and its fixed, public predecessor inputs."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1];R=E.parents[2]
INPUTS=[
 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json',
 'experiments/yolo/gdt967_balneis_joint_body_term_incidence/artifacts/TARGET.json',
 'experiments/yolo/gdt967_balneis_joint_body_term_incidence/artifacts/SCOPE.json',
 'experiments/yolo/gdt963_dioscorides_complete_content_code/src/run.py',
 'research_registry/work_batches/ten_hours_20260915/balneis_cache/ALIM553.txt',
 'research_registry/work_batches/ten_hours_20260915/BALNEIS_COMPLETE_CONTENT_20260920.md',
 'research_registry/work_batches/ten_hours_20260915/BALNEIS_COMPLETE_CONTENT_20260920.json',
 'research_registry/work_batches/ten_hours_20260915/BALNEIS_BODMER_RECEIPT_20260920.json',
]
SCIENCE=['DECISION.md','METHOD.md','PREREGISTRATION.md','requirements.txt','src/compile_source.py','src/SOURCE.json','src/model.py','src/run.py','src/validate.py']


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');args=p.parse_args()
 lock=E/'PREREG_LOCK.json'
 if args.register:
  assert not lock.exists(),'Do not overwrite an existing registration'
  paths=INPUTS+[str((E/x).relative_to(R)) for x in SCIENCE]
  lock.write_text(json.dumps({'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{x:digest(R/x) for x in paths}},indent=2)+'\n')
 else:
  for path,h in json.loads(lock.read_text())['files'].items():assert digest(R/path)==h,path
 m=json.loads((E/'experiment.json').read_text())
 m.update(title='Complete Anastasia condition trees',question='Can a complete bath paragraph express all nine fixed Anastasia assertion trees under either semantic writer while retaining every written word boundary?',status=args.status,
  dependencies=['GDT928','GDT963','GDT967'],claim_ceiling='Conditional whole-content code only; no confirmed word, historical source identification, significance or independent meaning confirmation.',
  inputs=[{'path':x,'role':'fixed_input','sha256':digest(R/x)} for x in INPUTS],outputs=[])
 for f in sorted(E.rglob('*')):
  if not f.is_file() or f.name=='experiment.json' or 'runtime' in f.parts or '__pycache__' in f.parts:continue
  m['outputs'].append({'path':str(f.relative_to(R)),'role':'primary_report' if f.name=='REPORT.md' else 'source_or_artifact','sha256':digest(f)})
 v=E/'artifacts/VALIDATION.json'
 if v.exists():m['validation']={'artifact':str(v.relative_to(R)),'status':json.loads(v.read_text())['status']}
 (E/'experiment.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps({'status':m['status'],'inputs':len(m['inputs']),'outputs':len(m['outputs'])}))


if __name__=='__main__':main()
