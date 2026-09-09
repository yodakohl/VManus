import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((E/'experiment.json').read_text());m.update(title='Unknown symbol collation in two physical label rows',question='Can a fixed total order of literal EVA or exact STA symbols sort the two six-label rows on f88r?',claim_ceiling='Conditional sorted encoded-spelling model on one physical folio; no phonetic values or meanings.',dependencies=['GDT794'])
inputs=['experiments/semantic_assumptions/results/source_separator_transcription.tsv','experiments/semantic_assumptions/results/source_sta_group_alignment.tsv','experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv']
m['inputs']=[dict(path=p,role='selector_guarded_source' if p.endswith('.tsv') else 'source',sha256=sha(ROOT/p)) for p in inputs]
m['outputs']=[dict(path=p.relative_to(ROOT).as_posix(),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]
if (E/'artifacts/VALIDATION.json').exists():m['validation']=dict(status='PASS',artifact=(E/'artifacts/VALIDATION.json').relative_to(ROOT).as_posix());m['status']='COMPLETED_FIXED_COLLATION_TEST'
(E/'experiment.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
