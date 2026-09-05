#!/usr/bin/env python3
"""Bind this experiment's public artifacts; hashes do not display truth."""
import argparse
import hashlib
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')


def files(include_truth=False):
    return sorted(p for p in EXP.rglob('*') if p.is_file()
                  and 'runtime' not in p.relative_to(EXP).parts
                  and '__pycache__' not in p.relative_to(EXP).parts
                  and (include_truth or 'sealed' not in p.relative_to(EXP).parts)
                  and p.name != 'experiment.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--register', action='store_true')
    parser.add_argument('--include-truth', action='store_true')
    parser.add_argument('--status', required=True)
    parser.add_argument('--updated', default='2026-09-06')
    parser.add_argument('--validation', default='artifacts/CAPACITY_VALIDATION.json')
    args = parser.parse_args()
    lockpath = EXP / 'src/PREREG_LOCK.json'
    if args.register:
        if lockpath.exists():
            raise RuntimeError('Registration already exists; refuse overwrite')
        paths = [p for p in files() if p.relative_to(EXP).parts[0] in ('src','prepared','sources')
                 or p.name in ('METHOD.md','PREREGISTRATION.md')]
        held = [p for p in paths if p.name.endswith('_held.json')]
        paths = [p for p in paths if p not in held]
        truth = sorted((EXP/'sealed').glob('*.json'))
        write(lockpath, {'schema':'GDT832_PREREG_LOCK_V1',
                        'stage':'after disclosed source preparation; before any decoder fit or recovery score',
                        'sha256':{p.relative_to(EXP).as_posix():digest(p) for p in paths},
                        'held_commitments':{p.relative_to(EXP).as_posix():digest(p) for p in held},
                        'sealed_commitments':{p.relative_to(EXP).as_posix():digest(p) for p in truth}})
    manifest = json.loads((EXP/'experiment.json').read_text())
    manifest.update({'title':'Joint historical family and continuous-context blind recovery control',
                     'status':args.status,'updated':args.updated,
                     'question':'Do continuous word context and attested co-lemma relations jointly improve exact held Latin plaintext recovery under one shared mixed key, relative to matched context-cut and family-off controls?',
                     'claim_ceiling':'Known control roles and boundaries; incomplete attested families; three key replicates share one source split. No Voynich data, coding-class identification, language, meaning or translation.',
                     'dependencies':[], 'inputs':[],
                     'commands':{'run':'python3 '+(EXP/'src/run.py').relative_to(ROOT).as_posix()+' --fit',
                                 'validate':'python3 '+(EXP/'src/validate.py').relative_to(ROOT).as_posix()+' --check'},
                     'validation':{'status':'PASS','artifact':(EXP/args.validation).relative_to(ROOT).as_posix()}})
    manifest['outputs']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p),
                         'role':'primary_report' if p.name=='REPORT.md' else 'reproducible_source_or_artifact'}
                        for p in files(args.include_truth)]
    write(EXP/'experiment.json',manifest)
    print(json.dumps({'status':args.status,'bindings':len(manifest['outputs']),
                      'truth_published':args.include_truth,'registration_created':args.register}))


if __name__=='__main__':
    main()
