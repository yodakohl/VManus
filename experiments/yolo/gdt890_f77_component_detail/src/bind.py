import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((E/'experiment.json').read_text());m.update(title='f77r strict component-detail correspondence',question='Do two independent geometry inventories permit the middle drawing to enlarge an upper component under the existing exact label/opener relation?',claim_ceiling='Local discovery geometry and reference hypothesis only; no meaning or scored relation.',dependencies=['GDT198','GDT790','GDT791','GDT792','GDT811'])
inputs=['experiments/yolo/gdt790_panel_owner_image_grammar_overlay/src/IMAGE_SOURCE_SPECS.tsv','experiments/yolo/gdt790_panel_owner_image_grammar_overlay/src/LABEL_OWNER_SPECS.tsv','experiments/yolo/gdt811_four_page_content_synthesis/src/F77_HISTORICAL_READING.md']
m['inputs']=[dict(path=p,role='existing_source_contract',sha256=sha(ROOT/p)) for p in inputs]
m['outputs']=[dict(path=p.relative_to(ROOT).as_posix(),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]
if (E/'artifacts/VALIDATION.json').exists():
 v=json.loads((E/'artifacts/VALIDATION.json').read_text());assert v['status']=='PASS';m['validation']=dict(status='PASS',artifact=(E/'artifacts/VALIDATION.json').relative_to(ROOT).as_posix())
 m['status']=json.loads((E/'artifacts/RESULT.json').read_text())['status']
(E/'experiment.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
