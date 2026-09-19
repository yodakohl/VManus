import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
up=['experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/CANDIDATES.json', 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json', 'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json', 'docs/NONLOCAL_AGREEMENT_REVIEW.md', 'experiments/yolo/gdt915_terminal_lr_phrase_transfer/REPORT.md', 'experiments/yolo/gdt916_unseen_lr_stem_pair_transfer/REPORT.md', 'experiments/yolo/gdt949_phrase_readings_observable_consequences/REPORT.md', 'experiments/yolo/gdt950_meteorological_phase_output_contrast/REPORT.md', 'experiments/yolo/gdt437_future_card_state_transition_order_repair/REPORT.md', 'experiments/yolo/gdt591_bath_episode_continuity/REPORT.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 dump(lock,{'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'FIXED_EXPOSED_PARAGRAPH_CONSEQUENCE','files':{p.relative_to(R).as_posix():sha(p) for p in paths}})
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Complete phrase state prerequisites across paragraphs',question='Do successive instances of the 22 fixed r/l phrase families preserve a state prerequisite within complete paragraphs?',status=json.loads(rr.read_text())['status'] if rr.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Conditional exposed-text test; no independent semantic relation, significance, reserved access or translated word.',dependencies=['GDT915','GDT916','GDT928','GDT949','GDT950'],inputs=[{'path':n,'sha256':sha(R/n),'role':'fixed_input'} for n in up],outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation={'status':json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if vv.exists() else None})
dump(E/'experiment.json',m);print(m['status'])
