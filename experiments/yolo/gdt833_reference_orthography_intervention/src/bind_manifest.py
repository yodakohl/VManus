#!/usr/bin/env python3
"""Bind stage-specific GDT833 artifacts without displaying control truth."""
import argparse
import hashlib
import json
from pathlib import Path

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
UPSTREAM=EXP.parent/'gdt832_joint_family_context_control'/'src'
REUSED=['decoder.cpp','reference_model.py','run.py','prepare.py']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def files(truth=False):
    return sorted(p for p in EXP.rglob('*') if p.is_file()
                  and not {'runtime','__pycache__'}.intersection(p.relative_to(EXP).parts)
                  and (truth or 'sealed' not in p.relative_to(EXP).parts)
                  and p.name!='experiment.json')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--register',action='store_true')
    p.add_argument('--include-truth',action='store_true')
    p.add_argument('--status',required=True)
    p.add_argument('--validation',default='artifacts/SOURCE_VALIDATION.json')
    args=p.parse_args()
    upstream={str((UPSTREAM/name).relative_to(ROOT)):sha(UPSTREAM/name) for name in REUSED}
    if args.register:
        target=EXP/'src/PREREG_LOCK.json'
        if target.exists():raise RuntimeError('Refuse to overwrite an existing preregistration')
        paths=[f for f in files() if f.relative_to(EXP).parts[0] in ('src','sources','prepared')
               or f.name in ('METHOD.md','PREREGISTRATION.md')]
        held=[f for f in paths if f.name.endswith('_held.json')]
        fit=[f for f in paths if f not in held]
        truth=sorted((EXP/'sealed').glob('*.json'))
        write(target,{'schema':'GDT833_PREREG_LOCK_V1',
                      'stage':'after disclosed source-only capacity; before any decoder fit/recovery score',
                      'sha256':{f.relative_to(EXP).as_posix():sha(f) for f in fit},
                      'upstream_sha256':upstream,
                      'held_commitments':{f.relative_to(EXP).as_posix():sha(f) for f in held},
                      'sealed_commitments':{f.relative_to(EXP).as_posix():sha(f) for f in truth}})
    manifest=json.loads((EXP/'experiment.json').read_text())
    rel=EXP.relative_to(ROOT).as_posix()
    manifest.update({'title':'Paired reference orthography intervention with fresh original-spelling recovery',
                     'status':args.status,'updated':'2026-09-06',
                     'question':'Does removing only reference-side v/u distinction impair exact original-spelling recovery and reverse a legal v/z oracle-key contrast on a fresh historical work?',
                     'claim_ceiling':'Known mixed control roles/boundaries; paired references, original gold spelling, one fresh source split and three key replicates. No repaired GDT832 score or Voynich language/meaning/translation.',
                     'dependencies':['GDT832'],
                     'inputs':[{'path':path,'sha256':digest,'role':'unchanged_upstream_implementation'} for path,digest in upstream.items()],
                     'commands':{'run':f'python3 {rel}/src/run.py --fit',
                                 'validate':f'python3 {rel}/src/validate.py --data-dir {rel} --source-dir {rel}/runtime/udante_source --model-root {rel}/runtime --check'},
                     'validation':{'status':'PASS','artifact':f'{rel}/{args.validation}'}})
    manifest['outputs']=[{'path':f.relative_to(ROOT).as_posix(),'sha256':sha(f),
                         'role':'primary_report' if f.name=='REPORT.md' else 'reproducible_source_or_artifact'} for f in files(args.include_truth)]
    write(EXP/'experiment.json',manifest)
    print(json.dumps({'status':args.status,'bindings':len(manifest['outputs']),
                      'upstream_files':len(upstream),'truth_published':args.include_truth}))


if __name__=='__main__':
    main()
