import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
ap=argparse.ArgumentParser();ap.add_argument('--lock',action='store_true');ap.add_argument('--status',default='REGISTERED_UNSCORED');a=ap.parse_args()
s=read(E/'src/SPEC.json');inputs=[s[k] for k in ('input','source_facts','source_builder','source_primary','source_decision')]+['research_registry/work_batches/ten_hours_20260915/CENNINI_SOURCE_FACTS_AUDIT_20260920.md']
science=['DECISION.md','METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/records.py','src/finite.py','src/reverse.py','src/independent.py','src/run.py','src/validate.py','src/preflight.py','artifacts/PREDICTIONS.json','artifacts/PREFLIGHT.json']
if a.lock:
 assert not (E/'PREREG_LOCK.json').exists(),'Existing registration must not be replaced'
 write(E/'PREREG_LOCK.json',dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={n:sha(R/n) for n in inputs+[str((E/n).relative_to(R)) for n in science]}))
m=read(E/'experiment.json');m.update(question='Does a complete fixed Cennini content account admit a globally shared reversible full/delta field code on any whole admitted1–4paragraph bundle?',claim_ceiling='Conditional source-record codes only; all meanings and source identity assumed, no independent meaning confirmation or significance.',dependencies=['GDT345','GDT569','GDT928','GDT989','GDT1001','GDT1003','GDT1004'],status=a.status,inputs=[dict(path=n,sha256=sha(R/n),role='fixed_input') for n in inputs],outputs=[])
for path in sorted(E.rglob('*')):
 if path.is_file() and path.name!='experiment.json' and '__pycache__' not in path.parts and 'runtime' not in path.parts:m['outputs'].append(dict(path=str(path.relative_to(R)),role='primary_report' if path.name=='REPORT.md' else 'source_or_artifact',sha256=sha(path)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=read(E/'artifacts/VALIDATION.json')['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
m['artifact_policy']['large_artifact_justification']='Complete all-bundle census and full source predictions preserve every tested candidate; large JSON files, if any, are needed to audit omitted-fit claims without resampling.'
write(E/'experiment.json',m)
