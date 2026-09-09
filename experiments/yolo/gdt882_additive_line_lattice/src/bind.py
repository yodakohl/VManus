import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--register',action='store_true');a=a.parse_args()
up=['experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py','experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv','tools/guarded_tsv_query.py']
lock=E/'src/PREREG_LOCK.json'
if a.register:
 assert not lock.exists()
 put(lock,{p.relative_to(ROOT).as_posix():sha(p) for p in [*sorted((E/'src').glob('*.py')),E/'src/SPEC.json',E/'METHOD.md',*[ROOT/n for n in up]]})
for n,v in json.loads(lock.read_text()).items():assert sha(ROOT/n)==v,n
result=E/'artifacts/RESULT.json';validation=E/'artifacts/VALIDATION.json';status=json.loads(result.read_text())['status'] if result.exists() else 'REGISTERED_UNSCORED'
m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
files=sorted(p for p in E.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='experiment.json')
m.update(title='Fixed additive whole-line integer lattice',question='Do complete concordant prose lines admit any nonzero fixed literal-character additive invariant into an abelian group?',claim_ceiling='Exact declared literal-character whole-line mechanism only; no error-tolerant, stateful, positional, nonlinear, phonetic or semantic verdict.',status=status,dependencies=['GDT631','GDT829'],inputs=[dict(path=n,sha256=sha(ROOT/n),role='frozen_source_or_reader') for n in up],outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact') for p in files],validation=dict(status='PASS' if validation.exists() else 'NOT_RUN',artifact=rel+'/artifacts/VALIDATION.json' if validation.exists() else None))
put(E/'experiment.json',m);print(status)
