#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];O=E.parent/'gdt837_scg_integrated_wholeword_control'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def relative(p):return str(p.relative_to(R))
def inputs():
 names=['METHOD.md','REPORT.md','src/PREREG_LOCK.json','src/ENCODER_SPEC.json','src/SPEC.json','artifacts/FIT_LOCK.json','artifacts/RESULT.json','prepared/reference.jsonl','prepared/families.json','prepared/candidates.json','confirmation/source_truth.json.gz']
 names+=read(O/'artifacts/FIT_LOCK.json')['restarts']+read(O/'artifacts/FIT_LOCK.json')['selected']
 for w in read(O/'src/SPEC.json')['world_ids']:
  names += [f'prepared/world_{w}_discovery.json.gz',f'prepared/world_{w}_held.json.gz',f'confirmation/world_{w}_truth.json.gz']
 out=[relative(O/n) for n in names]
 out+=['experiments/yolo/gdt832_joint_family_context_control/src/'+n for n in ['reference_model.py','prepare.py']]
 return sorted(set(out))
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');a=p.parse_args()
lock=E/'PREREG_LOCK.json';ins=inputs();science=['METHOD.md','PREREGISTRATION.md','src/run.py','src/validate.py','src/test_inverse.py','src/bind.py']
if a.register:
 assert not lock.exists()
 lock.write_text(json.dumps(dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),retrospective=True,
  files={n:sha(R/n) for n in ins+[relative(E/n) for n in science]}),indent=2,sort_keys=True)+'\n')
else:
 for n,h in read(lock)['files'].items():assert sha(R/n)==h,n
m=read(E/'experiment.json');m.update(title='Conditional full suffix inverse on frozen GDT837 keys',
 question='Does complete forward compatibility constrain all frozen keys and their finite suffix-only completions?',status=a.status,
 dependencies=['GDT832','GDT835','GDT836','GDT837'],claim_ceiling='Retrospective conditional known-architecture control only; no fresh blind recovery, Voynich language or word.',
 commands=dict(run='python3 '+relative(E/'src/run.py')+' audit',validate='python3 '+relative(E/'src/validate.py')),
 inputs=[dict(path=n,role='frozen_control_input',sha256=sha(R/n)) for n in ins],outputs=[])
for f in sorted(E.rglob('*')):
 if f.is_file() and f.name!='experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:
  m['outputs'].append(dict(path=relative(f),role='primary_report' if f.name=='REPORT.md' else 'source_or_artifact',sha256=sha(f)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=read(E/'artifacts/VALIDATION.json')['status'],artifact=relative(E/'artifacts/VALIDATION.json'))
(E/'experiment.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status=a.status,inputs=len(ins),outputs=len(m['outputs']))))
