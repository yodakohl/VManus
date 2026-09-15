from pathlib import Path
import argparse
import datetime
import hashlib
import json
E=Path(__file__).resolve().parents[1]
R=E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
up=['research_registry/work_batches/ten_hours_20260915/NEXT_GLOBAL_MEANING_SUPPLY.md','research_registry/work_batches/ten_hours_20260915/ALLOY_VARIABLE_CONTENT_REVIEW.md','research_registry/proposals/raw_global_alloy_composition.json']
lock=E/'PREREG_LOCK.json'
if a.register:
    assert not lock.exists()
    own=['README.md','METHOD.md','PREREGISTRATION.md','src/run.py','src/bind.py','src/SOURCE.json','artifacts/PREFLIGHT.json']
    paths=[E/x for x in own]+[R/x for x in up]
    write(lock,dict(stage='EXPOSED_SOURCE_ONLY_BEFORE_DIGIT_ENUMERATION',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={x.relative_to(R).as_posix():sha(x) for x in paths}))
for n,h in json.loads(lock.read_text())['files'].items(): assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());r=E/'artifacts/RESULT.json';v=E/'artifacts/VALIDATION.json'
vs=json.loads(v.read_text())['status'] if v.exists() else 'NOT_RUN'
if vs!='PASS': vs='NOT_RUN'
rel=E.relative_to(R).as_posix()
m.update(title='Alloy numerical binding exposed-source control',question='Do complete final balances of all five source alloy accounts identify their numeral values under a shared decimal digit permutation, preserving native mixed-number components?',status=json.loads(r.read_text())['status'] if r.exists() else 'REGISTERED_UNSCORED',claim_ceiling='Known-role exposed source control only; no complete prose renderer, Voynich data, historical code, metal noun, significance or independently confirmed meaning.',dependencies=['GDT882','GDT902','GDT969'],inputs=[dict(path=x,sha256=sha(R/x),role='source_or_predecessor_review') for x in up],outputs=[dict(path=x.relative_to(R).as_posix(),sha256=sha(x),role='primary_report' if x.name=='REPORT.md' else 'source_or_artifact') for x in sorted(E.rglob('*')) if x.is_file() and x.name!='experiment.json' and not {'__pycache__','runtime'}.intersection(x.relative_to(E).parts)],validation=dict(status=vs,artifact=rel+'/artifacts/VALIDATION.json' if v.exists() else None))
write(E/'experiment.json',m);print(m['status'])
