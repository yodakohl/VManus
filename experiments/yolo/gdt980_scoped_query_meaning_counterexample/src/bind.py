import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');args=a.parse_args()
up=['research_registry/proposals/raw_scoped_spatial_query_compounds.json','research_registry/work_batches/ten_hours_20260915/FINITE_COMPOSITION_CONTENT_RAW_SUPPLY_20260919.md','experiments/yolo/gdt879_plant_topology_endpoint_pilot/REPORT.md','experiments/yolo/gdt881_f99v_text_graphic_stroke_interface/REPORT.md','experiments/yolo/gdt346_compositional_operator_manifold/REPORT.md','experiments/yolo/gdt608_compositional_stem_orientation/REPORT.md']
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 dump(lock,{'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'FIXED_SOURCE_ONLY_CONTROL','files':{p.relative_to(R).as_posix():sha(p) for p in paths}})
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Source-only counterexample to scoped-query meaning sufficiency',question='Does truth of a grammar-complete account using all eleven atoms determine the stipulated whole scene, compared with the original content description?',status=json.loads(rr.read_text())['status'] if rr.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Designed source/control finding only; no manuscript access, fitted code, significance, or translated word.',dependencies=['GDT879','GDT881','GDT346','GDT608'],inputs=[{'path':n,'sha256':sha(R/n),'role':'fixed_input'} for n in up],outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation={'status':json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if vv.exists() else None})
dump(E/'experiment.json',m);print(m['status'])
