#!/usr/bin/env python3
"""Freeze preregistration once; bind only the intended public experiment files."""
import argparse
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def own_files():
    return sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and p.name!='experiment.json')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--register',action='store_true')
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    if args.register and args.final:raise ValueError('choose registration or final')
    inherited={
        'gdt832_joint_family_context_control':['src/prepare.py','src/reference_model.py'],
        'gdt833_reference_orthography_intervention':['src/prepare.py'],
        'gdt834_role_blind_mixed_control':['src/prepare.py','prepared/reference.jsonl','prepared/reference_ids.json','prepared/candidates.json','prepared/families.json'],
        'gdt836_integrated_wholeword_precedence':['src/decoder.cpp','src/ENCODER_SPEC.json'],
    }
    upstream=sorted(E.parent/folder/name for folder,names in inherited.items() for name in names)
    lockpath=E/'src/PREREG_LOCK.json'
    if args.register:
        if lockpath.exists():raise ValueError('registration already frozen')
        if (E/'artifacts/FIT_LOCK.json').exists() or (E/'artifacts/fits').exists():raise ValueError('registration must precede fits')
        held=sorted((E/'prepared').glob('world_*_held.json.gz'))
        confirmation=sorted((E/'confirmation').glob('*.json.gz'))
        if len(held)!=3 or len(confirmation)!=4:raise ValueError('commitment inventory')
        bound=[p for p in own_files() if p.parts[len(E.parts)] in ('src','prepared','sources') and p not in held]
        bound += [E/name for name in ('METHOD.md','PREREGISTRATION.md','REPRODUCE.md')]
        write(lockpath,{'schema':'GDT837_PREREG_LOCK_V1','real_initialization_or_fit_started':False,
            'sha256':{p.relative_to(E).as_posix():sha(p) for p in sorted(bound)},
            'upstream_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in upstream},
            'held_commitments':{p.relative_to(E).as_posix():sha(p) for p in held},
            'confirmation_commitments':{p.relative_to(E).as_posix():sha(p) for p in confirmation}})
    if not lockpath.exists():raise ValueError('freeze registration first')
    lock=json.loads(lockpath.read_text())
    for rel,h in lock['sha256'].items():
        if sha(E/rel)!=h:raise ValueError('frozen registration changed '+rel)
    for rel,h in lock['upstream_sha256'].items():
        if sha(ROOT/rel)!=h:raise ValueError('frozen upstream changed '+rel)
    for field in ('held_commitments','confirmation_commitments'):
        for rel,h in lock[field].items():
            if sha(E/rel)!=h:raise ValueError('commitment changed '+rel)
    outputs=[p for p in own_files() if args.final or 'confirmation' not in p.relative_to(E).parts]
    status=json.loads((E/'artifacts/RESULT.json').read_text())['status'] if args.final and (E/'artifacts/RESULT.json').exists() else 'INITIALIZATION_STOP' if args.final and (E/'artifacts/RUN_STOP.json').exists() else 'REGISTERED_UNSCORED'
    validation='artifacts/VALIDATION.json' if args.final and (E/'artifacts/VALIDATION.json').exists() else 'artifacts/SOURCE_VALIDATION.json'
    manifest=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
    manifest.update(title='SCG paired integrated mandatory wholeword control',
        question='Does unchanged integrated mandatory wholeword precedence recover a new SCG ciphertext control and improve held recovery over the paired relaxed search?',
        claim_ceiling='Known mandatory-W synthetic architecture on historical source sentences with supplied boundaries and nominal26L4S8W counts; three keys share one split; no full suffix inverse, optional abbreviation rule or Voynich reading.',
        status=status,updated='2026-09-06',dependencies=['GDT832','GDT833','GDT834','GDT836'],
        inputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'frozen_upstream_source_or_resource'} for p in upstream],
        outputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'reproducible_source_or_artifact'} for p in outputs],
        commands={'run':f'python3 {rel}/src/run.py --fit','validate':f'python3 {rel}/src/validate.py --check' if args.final else f'python3 {rel}/src/validate.py --source-only --check'},
        validation={'status':'PASS','artifact':f'{rel}/{validation}'})
    write(E/'experiment.json',manifest)
    print(json.dumps({'status':status,'inputs':len(upstream),'outputs':len(outputs),'confirmation_public':args.final}))

if __name__=='__main__':main()
