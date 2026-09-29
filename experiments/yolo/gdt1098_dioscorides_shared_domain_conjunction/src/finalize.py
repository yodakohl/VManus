"""Bind registration or completed artifacts without changing frozen scientific files."""
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
P963='experiments/yolo/gdt963_dioscorides_complete_content_code'
P1096='experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains'
P1097='experiments/yolo/gdt1097_dioscorides_complete_interval_code'
NOTE='research_registry/proposals/laufenberg_f85r2_20260926/DIOSCORIDES_SHARED_DOMAIN_DECISION_20260929.md'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    inputs=[NOTE,P963+'/src/SOURCE.json',P963+'/REPORT.md',P1096+'/artifacts/CASES.json',
            P1096+'/artifacts/CERTIFICATES.json.gz',P1096+'/REPORT.md',P1096+'/METHOD.md',
            P1097+'/artifacts/SOLVER_RESULTS.json.gz',P1097+'/REPORT.md',P1097+'/METHOD.md']
    fixed=['METHOD.md','PREREGISTRATION.md','src/model.py','src/controls.py','src/prepare.py',
           'src/run.py','src/validate.py','artifacts/CONTROLS.json','artifacts/INPUT_DOMAINS.json.gz','artifacts/CASE_PREDICTIONS.tsv']
    lock_path=E/'src/PREREG_LOCK.json'
    locks={p:digest(ROOT/p) for p in inputs}
    locks.update({str((E/p).relative_to(ROOT)):digest(E/p) for p in fixed})
    if lock_path.exists():
        old=json.loads(lock_path.read_text())
        assert old['files']==locks,'Frozen file changed; no silent rebinding'
    else:
        lock_path.write_text(json.dumps(dict(scope='Public pre-execution binding; unchanged source/channel',files=locks),indent=2)+'\n')
    result_path=E/'artifacts/RESULT.json'
    status=json.loads(result_path.read_text())['status'] if result_path.exists() else 'REGISTERED_UNSCORED'
    manifest=json.loads((E/'experiment.json').read_text())
    manifest.update(title='Finite shared recurrent domains across all four Dioscorides records',status=status,
                    question='Can all13 shared locally recurrent atoms have nonempty common code domains on any four distinct whole-page leaves under the unchanged source/channel?',
                    claim_ceiling='Finite necessary-condition page-tuple accounting only; no complete code, independent meaning confirmation, significance or word.',
                    dependencies=['GDT963','GDT1096','GDT1097'])
    manifest['inputs']=[dict(path=p,role='unchanged parent evidence or decision contract',sha256=digest(ROOT/p)) for p in inputs]
    outputs=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]
    manifest['outputs']=[dict(path=str(p.relative_to(ROOT)),role='reproducibility source, contract or artifact',sha256=digest(p)) for p in outputs]
    vp=E/'artifacts/VALIDATION.json'
    manifest['validation']=dict(status='PASS' if vp.exists() else 'NOT_RUN',artifact=str(vp.relative_to(ROOT)) if vp.exists() else None)
    (E/'experiment.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(status)


if __name__=='__main__':
    main()
