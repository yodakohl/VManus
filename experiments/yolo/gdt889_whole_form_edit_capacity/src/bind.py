import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((E/'experiment.json').read_text())
m.update(title='Exact whole-form one-edit-correction message capacity',question='How many distinct messages can all fixed valid whole forms carry under guaranteed context-free one-edit correction?',claim_ceiling='Exact finite code-capacity bound under valid-codeword and complete one-edit assumptions; no meaning or general redundancy rejection.',dependencies=['GDT338','GDT883'])
inputs=['experiments/yolo/gdt883_overlapping_digram_constraints/artifacts/SELECTED_GROUPS.json','experiments/yolo/gdt883_overlapping_digram_constraints/artifacts/VALIDATION.json']
m['inputs']=[dict(path=p,role='published_guarded_concordant_source',sha256=sha(ROOT/p)) for p in inputs]
m['outputs']=[dict(path=p.relative_to(ROOT).as_posix(),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]
if (E/'artifacts/VALIDATION.json').exists():
 v=json.loads((E/'artifacts/VALIDATION.json').read_text());assert v['status']=='PASS'
 m['status']='EXACT_FINITE_ERROR_CORRECTION_CAPACITY';m['validation']=dict(status='PASS',artifact=(E/'artifacts/VALIDATION.json').relative_to(ROOT).as_posix())
(E/'experiment.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
