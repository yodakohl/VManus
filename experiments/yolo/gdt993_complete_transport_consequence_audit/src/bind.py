#!/usr/bin/env python3
import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
INPUTS=['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json']
INPUTS+=['experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_DISCOVERY_'+e+'.json' for e in ('ZL3b','IT2a','RF1b')]
INPUTS+=['research_registry/proposals/raw_f83r_transport_explicit_reference_grammar.json']
INPUTS+=['research_registry/work_batches/ten_hours_20260915/TRANSPORT_RAW377_COMPLETE_EXPLORATORY_READING_20260920.'+ext for ext in ('json','md')]
SCIENCE=['METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/model.py','src/build_packet.py','src/preflight.py','src/run.py','src/validate.py','src/bind.py','artifacts/PRE_RUN_FIXTURES.json','artifacts/SOURCE_PACKET.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');a=p.parse_args();lock=E/'PREREG_LOCK.json'
if a.register:
 assert not lock.exists()
 names=INPUTS+[str((E/n).relative_to(R)) for n in SCIENCE]
 lock.write_text(json.dumps(dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={n:sha(R/n) for n in names}),indent=2)+'\n')
else:
 for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());m.update(title='Complete hypothetical transport reading: finite consequence audit',question='Which of32 frozen full readings of exposed f83r.18-24 preserve all explicit voyages, references, safety constraints and final goal?',status=a.status,dependencies=['GDT915','GDT928'],claim_ceiling='Conditional consistency of a constructed complete reading only;41new whole-form guesses, uncertain ZL seam,0independent meaning capacity,0confirmed words or significance.',inputs=[dict(path=n,role='fixed_input',sha256=sha(R/n)) for n in INPUTS],outputs=[])
for f in sorted(E.rglob('*')):
 if f.is_file() and f.name!='experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:m['outputs'].append(dict(path=str(f.relative_to(R)),role='primary_report' if f.name=='REPORT.md' else 'source_or_artifact',sha256=sha(f)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=json.loads((E/'artifacts/VALIDATION.json').read_text())['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
(E/'experiment.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(status=m['status'],inputs=len(m['inputs']),outputs=len(m['outputs']))))
