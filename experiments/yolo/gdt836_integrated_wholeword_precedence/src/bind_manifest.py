#!/usr/bin/env python3
"""Bind source-stop and engineering artifacts without asserting historical recovery."""
import argparse
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--validation',default='artifacts/VALIDATION.json')
    args=parser.parse_args()
    names={
        'gdt832_joint_family_context_control':['src/prepare.py','src/reference_model.py'],
        'gdt833_reference_orthography_intervention':['src/prepare.py'],
        'gdt834_role_blind_mixed_control':['src/decoder.cpp','src/run.py','src/test_roles.py','src/ENCODER_SPEC.json','prepared/reference.jsonl','prepared/reference_ids.json','prepared/candidates.json','prepared/families.json'],
        'gdt835_wholeword_precedence_audit':['src/source_context_audit.py','src/run.py'],
    }
    upstream=[E.parent/folder/name for folder,entries in names.items() for name in entries]
    outputs=sorted(path for path in E.rglob('*') if path.is_file()
                   and not {'runtime','__pycache__'}.intersection(path.relative_to(E).parts)
                   and path.name!='experiment.json')
    manifest=json.loads((E/'experiment.json').read_text())
    relative=E.relative_to(ROOT).as_posix()
    manifest.update(
        title='Integrated mandatory wholeword precedence with a stopped fresh-source control',
        question='Can mandatory wholeword precedence be enforced during search and assessed on the fixed fresh Questio split?',
        claim_ceiling='Engine implementation and invented-fixture validation only; fresh historical source fails held-literal coverage before keys/cipher/fits; no comparative recovery, full inverse or Voynich evidence.',
        status='SOURCE_CAPACITY_STOP', updated='2026-09-06',
        dependencies=['GDT832','GDT833','GDT834','GDT835'],
        inputs=[{'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'role':'bound_predecessor_implementation_or_resource'} for path in sorted(upstream)],
        outputs=[{'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'role':'primary_report' if path.name=='REPORT.md' else 'reproducible_source_or_artifact'} for path in outputs],
        commands={'run':f'python3 {relative}/src/run.py --fit','validate':f'python3 {relative}/src/validate.py --check'},
        validation={'status':'PASS','artifact':f'{relative}/{args.validation}'},
    )
    (E/'experiment.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':manifest['status'],'inputs':len(upstream),'outputs':len(outputs)}))

if __name__=='__main__':
    main()
