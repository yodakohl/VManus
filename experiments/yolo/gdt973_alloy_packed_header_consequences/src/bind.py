import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
d='research_registry/work_batches/ten_hours_20260915/'
up=[d+n for n in ['ALLOY_FINITE_GRAMMAR.json','alloy_finite_grammar.py','ALLOY_R1_WRITING_MODEL.md','alloy_r1_source_encoder.py','ALLOY_R2_WRITING_MODEL.md','alloy_r2_source_encoder.py']]
up+=['research_registry/proposals/raw_alloy_r1_compositional_group_code.json','research_registry/proposals/raw_alloy_r2_operator_allomorph_code.json','experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json','experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json','experiments/yolo/gdt972_alloy_r0_whole_header_consequence/REPORT.md','docs/VOYNICH_DATA_SCOPE.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 own=['README.md','METHOD.md','PREREGISTRATION.md','src/run.py','src/validate.py','src/bind.py','artifacts/PREFLIGHT.json','SOURCE_INDEPENDENT_REVIEW.md']
 paths=[E/n for n in own]+[R/n for n in up];write(lock,dict(stage='SOURCE_ONLY_BEFORE_R1_R2_TARGET_CENSUS',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={p.relative_to(R).as_posix():sha(p) for p in paths}))
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
status='REGISTERED_UNSCORED'
if rr.exists():
 v=json.loads(rr.read_text())['survivors'];status='BOTH_PACKED_WRITERS_CONTRADICTED' if not any(v.values()) else 'NECESSARY_FORM_SURVIVORS_NO_FULL_READING'
m.update(title='Unchanged packed-account writers R1/R2 necessary forms',question='Do any complete literal paragraphs satisfy all fixed necessary form consequences of the two prospectively specified packed alloy writers?',status=status,claim_ceiling='Necessary forms only; no full parse/code/arithmetic, source identity, significance, confirmed words or independent manuscript confirmation.',dependencies=['GDT915','GDT970','GDT971','GDT972'],inputs=[dict(path=n,sha256=sha(R/n),role='fixed_source_scope') for n in up],outputs=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation=dict(status=json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if vv.exists() else None))
write(E/'experiment.json',m);print(status)
