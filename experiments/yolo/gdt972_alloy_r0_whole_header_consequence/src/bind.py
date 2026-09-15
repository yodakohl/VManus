from pathlib import Path
import argparse,datetime,hashlib,json
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
d='research_registry/work_batches/ten_hours_20260915/'
up=[d+x for x in ['ALLOY_FINITE_GRAMMAR.md','ALLOY_FINITE_GRAMMAR.json','ALLOY_SOURCE_EQUATIONS.json','ALLOY_GRAMMAR_CHECKS.json','alloy_finite_grammar.py']]
up+=['experiments/yolo/gdt971_alloy_numeral_binding_control/REPORT.md','experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json','experiments/yolo/gdt970_rota_whole_part_conjugacy/PREREG_LOCK.json','experiments/yolo/gdt970_rota_whole_part_conjugacy/REPORT.md','experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json','docs/VOYNICH_DATA_SCOPE.md','research_registry/proposals/linear_material_register_program.json','research_registry/work_batches/luna_throughput_20260914/OPERATORS_RESULT.json']
lock=E/'PREREG_LOCK.json'
if args.register:
    assert not lock.exists()
    own=['README.md','METHOD.md','PREREGISTRATION.md','src/run.py','src/bind.py','artifacts/PREFLIGHT.json']
    paths=[E/x for x in own]+[R/x for x in up]
    write(lock,dict(stage='SOURCE_SYNTHETICS_ONLY_BEFORE_R0_TARGET_HEADER_CENSUS',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={x.relative_to(R).as_posix():sha(x) for x in paths}))
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());r=E/'artifacts/RESULT.json';v=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
vs=json.loads(v.read_text())['status'] if v.exists() else 'NOT_RUN'
if vs!='PASS':vs='NOT_RUN'
m.update(title='R0 whole-account necessary header consequence',question='Does any complete admitted literal paragraph satisfy the unavoidable header code conditions of the unchanged variable-account alloy grammar R0?',status=json.loads(r.read_text())['status'] if r.exists() else 'REGISTERED_UNSCORED',claim_ceiling='Necessary R0 header only; no complete parse, numeric fit, source identity, confirmed word, significance or independent manuscript confirmation.',dependencies=['GDT915','GDT970','GDT971'],inputs=[dict(path=x,sha256=sha(R/x),role='fixed_source_scope_or_primary') for x in up],outputs=[dict(path=x.relative_to(R).as_posix(),sha256=sha(x),role='primary_report' if x.name=='REPORT.md' else 'source_or_artifact') for x in sorted(E.rglob('*')) if x.is_file() and x.name!='experiment.json' and not {'__pycache__','runtime'}.intersection(x.relative_to(E).parts)],validation=dict(status=vs,artifact=rel+'/artifacts/VALIDATION.json' if v.exists() else None))
write(E/'experiment.json',m);print(m['status'])
