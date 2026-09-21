from common import *
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--lock',action='store_true');ap.add_argument('--status',default='REGISTERED_UNSCORED');args=ap.parse_args();s,g=inputs()
inputs_=[v for k,v in s.items() if k.startswith('source_') or k in ['grammar','model','bit_replay','binding_checker']]
inputs_=list(dict.fromkeys(inputs_))
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
if args.lock:
    assert not (E/'PREREG_LOCK.json').exists()
    science=['DECISION.md','METHOD.md','PREREGISTRATION.md','requirements.txt','artifacts/PANEL.json','artifacts/PREDICTIONS.json','artifacts/ORIGINAL_CANDIDATES.json','artifacts/PREFLIGHT.json','artifacts/PREFLIGHT_CASES.json','artifacts/PREPUBLIC_CORRECTIONS.json']+[str(p.relative_to(E)) for p in sorted((E/'src').glob('*')) if p.is_file() and p.name!='bind.py']
    write(E/'PREREG_LOCK.json',dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={x:sha(R/x) for x in inputs_+[str((E/x).relative_to(R)) for x in science]}))
m=read(E/'experiment.json');m.update(question='Can any of the20complete-content classes retain a full original-plus-f50r world with unchanged words, references, hazards and physical rules?',claim_ceiling='Complete fixed-content existence per20classes;unsampled dictionary ambiguity retained;no independently confirmed meaning,word,source or significance.',dependencies=['GDT928','GDT993','GDT994','GDT1002','GDT1006','GDT1007','GDT1008','GDT1009','GDT1010','GDT1011','GDT1012'],status=args.status,inputs=[dict(path=x,role='fixed_input',sha256=sha(R/x)) for x in inputs_],outputs=[])
for p in sorted(E.rglob('*')):
    if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts and 'runtime' not in p.parts:m['outputs'].append(dict(path=str(p.relative_to(R)),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)))
m['artifact_policy']['large_artifact_justification']='Complete differential preflight cases/results,all20full-content primary/independent outputs,all312member decisions and every lifted positive trace;failures and unknowns preserved.'
if (A/'VALIDATION.json').exists():m['validation']=dict(status=read(A/'VALIDATION.json')['status'],artifact=str((A/'VALIDATION.json').relative_to(R)))
write(E/'experiment.json',m)
