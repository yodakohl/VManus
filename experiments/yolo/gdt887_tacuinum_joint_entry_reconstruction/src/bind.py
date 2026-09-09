import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((E/'experiment.json').read_text())
m.update(title='Joint reconstruction of three complete named Tacuinum records',question='Does the fixed complete-record compiler identify the withheld corrective entity across all eligible paragraph assignments?',claim_ceiling='Conditional lexeme/group and entity-prefix notation model; no confirmed manuscript meaning, no independent held-folio test.',dependencies=['GDT631','GDT735','GDT737','GDT807','GDT809','GDT814'])
inputs=['experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv','experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/artifacts/GDT807_665_STRICT_PARAGRAPH_ATLAS.tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv','experiments/semantic_assumptions/results/source_sta_group_alignment.tsv']
m['inputs']=[dict(path=p,role='selector_guarded_source' if 'PAGE_ALLOWLIST' not in p else 'scope_allowlist',sha256=sha(ROOT/p)) for p in inputs]
m['outputs']=[dict(path=p.relative_to(ROOT).as_posix(),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]
m['artifact_policy']=dict(max_inline_bytes=30000000,large_artifact_justification='Complete admitted paragraph projections preserve all raw groups, STA sequences, exclusions and source IDs for independent replay.')
if (E/'artifacts/VALIDATION.json').exists():
 v=json.loads((E/'artifacts/VALIDATION.json').read_text());assert v['status']=='PASS'
 r=json.loads((E/'artifacts/RESULT.json').read_text());m['status']='COMPLETED_FIXED_COMPILER' if r['complete'] else 'INCOMPLETE_BUDGET'
 m['validation']=dict(status='PASS',artifact=(E/'artifacts/VALIDATION.json').relative_to(ROOT).as_posix())
(E/'experiment.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
