from pathlib import Path
import argparse,datetime,hashlib,json
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
D='research_registry/work_batches/ten_hours_20260915/'
up=[D+n for n in ['ROOT_EXTRACTION_SOURCE_SUPPLY.md','ROOT_EXTRACTION_PREDECESSOR_CORRECTION.md','ROOT_EXTRACTION_CONTENT_INVENTORY.json','ROOT_EXTRACTION_CONTENT_INVENTORY.md','ROOT_EXTRACTION_GENERATED_PROGRAM_REVIEW.md','ROOT_TRACE_DECISION.md','ROOT_TRACE_TIMING_CORRECTION.md','root_trace_capacity.py','ROOT_TRACE_CAPACITY.json','ROOT_TRACE_CAPACITY_REVIEW.md']]
P='experiments/yolo/gdt915_terminal_lr_phrase_transfer/'
up+=[P+'src/SPEC.json',*[P+'artifacts/SOURCE_'+phase+'_'+ed+'.json' for phase in ['DISCOVERY','EVALUATION'] for ed in ['ZL3b','IT2a','RF1b']]]
up+=['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/'+n for n in ['PREREGISTRATION.md','PREREG_LOCK.json','src/run.py']]
up+=['docs/VOYNICH_DATA_SCOPE.md']
lock=E/'PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    bound=[E/n for n in ['README.md','METHOD.md','PREREGISTRATION.md','src/run.py','src/bind.py','artifacts/SOURCE_PROGRAMMES.tsv','artifacts/SOURCE_PROGRAMME_SUMMARY.json']]+[R/n for n in up]
    write(lock,{'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'stage':'AFTER_METADATA_PREFLIGHT_BEFORE_NUMERIC_TARGET_FIT',
        'files':{p.relative_to(R).as_posix():sha(p) for p in bound}})
for name,h in json.loads(lock.read_text())['files'].items():assert sha(R/name)==h,name
m=json.loads((E/'experiment.json').read_text());result=E/'artifacts/RESULT.json';val=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
vs=json.loads(val.read_text())['status'] if val.exists() else 'NOT_RUN'
if vs=='PASS_REGISTRATION_ONLY':vs='NOT_RUN'
m.update(title='Complete generated square-root result traces',
    question='Can three different complete23-group calculations on three physical leaves share one global decimal digit and arithmetic opcode code?',
    claim_ceiling='Conditional generated arithmetic reading only; no literal source copy, confirmed word or significance; zero independent meaning confirmation.',
    status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED',
    dependencies=['GDT607','GDT608','GDT880','GDT882','GDT898','GDT901','GDT902','GDT909','GDT915','GDT928'],
    inputs=[{'path':n,'sha256':sha(R/n),'role':'fixed_scope_or_reviewed_source'} for n in up],
    outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts)],
    validation={'status':vs,'artifact':rel+'/artifacts/VALIDATION.json' if val.exists() else None})
m['commands']={'run':'python3 '+rel+'/src/run.py','validate':'python3 '+rel+'/src/validate.py'}
m['artifact_policy']['large_artifact_justification']='Complete finite n/width first-contradiction rows retain the entire checked scope if large; no images or reserve data.'
write(E/'experiment.json',m);print(m['status'])
