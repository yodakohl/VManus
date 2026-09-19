import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
up=['experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json', 'experiments/yolo/gdt976_dioscorides_shared_referent_projection/artifacts/DOMAINS.json', 'experiments/yolo/gdt976_dioscorides_shared_referent_projection/artifacts/CANDIDATES.json.gz', 'experiments/yolo/gdt977_dioscorides_leaf_breadth_projection/artifacts/CASES.json.gz', 'experiments/yolo/gdt963_dioscorides_complete_content_code/REPORT.md', 'experiments/yolo/gdt963_dioscorides_complete_content_code/METHOD.md', 'experiments/yolo/gdt976_dioscorides_shared_referent_projection/REPORT.md', 'experiments/yolo/gdt977_dioscorides_leaf_breadth_projection/REPORT.md', 'experiments/yolo/gdt978_dioscorides_all_recurrent_content/REPORT.md', 'experiments/yolo/gdt978_dioscorides_all_recurrent_content/METHOD.md', 'experiments/yolo/gdt900_cumanicus_complete_trilingual_tables/REPORT.md', 'experiments/yolo/gdt965_genizah_complete_record_grapheme_code/REPORT.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 dump(lock,{'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'FIXED_FULL_REMAINDER_PREFIX_COMPATIBILITY','files':{p.relative_to(R).as_posix():sha(p) for p in paths}})
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Whole remainder prefix compatibility of fixed name codes',question='Can all607 non-name occurrences coexist with both fixed name codes under the unchanged full prefix-free writer on four distinct whole pages?',status=json.loads(rr.read_text())['status'] if rr.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Conditional exposed-text test; no independent semantic relation, significance, reserved access or translated word.',dependencies=['GDT963','GDT976','GDT977','GDT978'],inputs=[{'path':n,'sha256':sha(R/n),'role':'fixed_input'} for n in up],outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation={'status':json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if vv.exists() else None})
m['artifact_policy']['large_artifact_justification']='Lossless compressed complete local class/role/page decisions and per-class complete boundary examples; every candidate must be auditable, without raw unadmitted data.'
dump(E/'experiment.json',m);print(m['status'])
