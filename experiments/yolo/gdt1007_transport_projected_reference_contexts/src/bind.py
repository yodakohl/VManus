from common import *
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--lock',action='store_true');ap.add_argument('--status',default='REGISTERED_UNSCORED');args=ap.parse_args();s,g=inputs()
inputs_=[s[k] for k in ['source_paragraphs','source_candidates','source_validation','grammar','primary','independent','model','bit_replay','binding_checker','source_decision']]
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science=['DECISION.md','METHOD.md','PREREGISTRATION.md','requirements.txt','src/SPEC.json','src/common.py','src/prepare.py','src/preflight.py','src/run.py','src/validate.py','artifacts/CANDIDATE_PREDICTIONS.json','artifacts/CENSUS.json','artifacts/PANEL.json','artifacts/PREDICTIONS.json','artifacts/PREFLIGHT.json']
    write(E/'PREREG_LOCK.json',dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={x:sha(R/x) for x in inputs_+[str((E/x).relative_to(R)) for x in science]}))
m=read(E/'experiment.json');m.update(question='Do any complete exposed short chedy contexts distinguish the36 retained original role/reference projections, under a liberal necessary world transfer?',claim_ceiling='Conditional eleven-role projection transfer only; no common full original47word dictionary, morphology, source identity, significance or independent meaning.',dependencies=['GDT993','GDT994','GDT997','GDT1003','GDT1004','GDT1006'],status=args.status,inputs=[dict(path=x,role='fixed_input',sha256=sha(R/x)) for x in inputs_],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts and 'runtime' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)))
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
m['artifact_policy']['large_artifact_justification']='Every candidate/context query, full positive map, whole parse and replay is retained for complete scope and ambiguity checking.'
write(E/'experiment.json',m)
