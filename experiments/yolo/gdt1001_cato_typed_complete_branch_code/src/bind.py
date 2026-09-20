import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=argparse.ArgumentParser();a.add_argument('--lock',action='store_true');a.add_argument('--status',default='REGISTERED_UNSCORED');args=a.parse_args();s=read(E/'src/SPEC.json');source=read(E/'src/SOURCE.json')
inputs=[s['input'],source['source_packet'],source['source_packet'].replace('.json','.md'),source['source_review']]
assert sha(R/s['input'])==s['input_sha256'];assert sha(R/source['source_packet'])==source['source_packet_sha256']
science=['METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/SOURCE.json','src/compile_source.py','src/finite.py','src/reverse.py','src/fixtures.py','src/run.py','src/validate.py']
if args.lock:write(E/'PREREG_LOCK.json',dict(files={p:sha(R/p) for p in inputs+[str((E/p).relative_to(R)) for p in science]}))
m=read(E/'experiment.json');m.update(question='Does a complete Cato133 procedural tree admit a type-local shared component code in any whole exposed paragraph under two fixed serializers?',claim_ceiling='Complete conditional compatibility only; no confirmed words, source identity, units, names, or significance.',dependencies=['GDT928','GDT879','GDT986','GDT987','GDT988','GDT993','GDT997','GDT1000'],status=args.status,inputs=[dict(path=p,role='fixed_input',sha256=sha(R/p)) for p in inputs],outputs=[])
m['artifact_policy']['large_artifact_justification']='Complete case records retain both writers, all source groups, provenance, codes, failures and unknowns; the table does not select only favorable passages.'
for p in sorted(E.rglob('*')):
 if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts and 'runtime' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)))
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status=read(E/'artifacts/VALIDATION.json')['status'],artifact=str((E/'artifacts/VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
