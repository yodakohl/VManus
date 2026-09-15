from pathlib import Path
import argparse,hashlib,json
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
up=['experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv','experiments/yolo/gdt867_shared_canvas_native_orientation/src/PAGE_ADMISSIONS.tsv','experiments/yolo/gdt871_remaining_shared_diagram_orientation/src/PAGE_ADMISSIONS.tsv','experiments/yolo/gdt871_remaining_shared_diagram_orientation/artifacts/IMAGE_METADATA.json','experiments/yolo/gdt867_shared_canvas_native_orientation/artifacts/IMAGE_METADATA.json','docs/visual_overview/SOURCES.json','docs/VOYNICH_DATA_SCOPE.md']
lock=E/'PREREG_LOCK.json'
if a.register:
 assert not lock.exists()
 bound=[E/'METHOD.md',*sorted((E/'src').glob('*')),*[R/n for n in up]]
 write(lock,{'files':{p.relative_to(R).as_posix():sha(p) for p in bound if p.is_file()},'stage':'BEFORE_CURRENT_NATIVE_VIEWS'})
for name,h in json.loads(lock.read_text())['files'].items():assert sha(R/name)==h,name
m=json.loads((E/'experiment.json').read_text());result=E/'artifacts/RESULT.json';val=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Source-predicted shared-pole arc framework',question='Do any entire circular units in six currently admitted astronomical renderings instantiate the necessary two-pole arc framework of Digby40chapter2?',claim_ceiling='Necessary topological predicate only; no metric code, ownership or meaning',status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED',dependencies=['GDT791','GDT867','GDT871','GDT878'],inputs=[{'path':n,'sha256':sha(R/n),'role':'fixed_scope_or_source'} for n in up],outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts)],validation={'status':json.loads(val.read_text())['status'] if val.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if val.exists() else None})
m['commands']={'run':'python3 '+rel+'/src/run.py --acquire --compare','validate':'python3 '+rel+'/src/validate.py'}
m['artifact_policy']['large_artifact_justification']='Previously admitted public images are retained only in ignored runtime; no source pixels are committed.'
write(E/'experiment.json',m);print(m['status'])
