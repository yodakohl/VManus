import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((E/'experiment.json').read_text())
m.update(title='Joint Alphita name incidence with held even-leaf records',question='Does one global six-name compiler fit complete training mention counts and uniquely predict held Senecio record bodies?',claim_ceiling='Conditional named-source graph reconstruction; no confirmed meanings or scored relation evidence without GDT388 gates.',dependencies=['GDT187','GDT214','GDT341','GDT342','GDT735','GDT737','GDT887'])
inputs=['experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/artifacts/SELECTED.json','experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/artifacts/VALIDATION.json','experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/src/PREREG_LOCK.json']
m['inputs']=[dict(path=p,role='previously_guarded_complete_source_cache',sha256=sha(ROOT/p)) for p in inputs]
m['outputs']=[dict(path=p.relative_to(ROOT).as_posix(),role='primary_report' if p.name=='REPORT.md' else 'source_or_artifact',sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]
m['artifact_policy']=dict(max_inline_bytes=30000000,large_artifact_justification='Complete blinded training input and exhaustive solution sets preserve source correspondence and ambiguity.')
if (E/'artifacts/VALIDATION.json').exists():
 v=json.loads((E/'artifacts/VALIDATION.json').read_text());assert v['status']=='PASS'
 r=json.loads((E/'artifacts/RESULT.json').read_text())
 m['status']='INCOMPLETE_BUDGET' if not r['complete'] else 'TRAINING_COMPLETE_HELD_PENDING' if any(e['status']=='WAITING_HELD_RELEASE' for e in r['evaluations'].values()) else 'COMPLETED_FIXED_NAME_COMPILER'
 m['validation']=dict(status='PASS',artifact=(E/'artifacts/VALIDATION.json').relative_to(ROOT).as_posix())
(E/'experiment.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
