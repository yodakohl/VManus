#!/usr/bin/env python3
"""Bind the public stage and seal fit inputs before optimization."""
import argparse
import hashlib
import json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def files(truth=False):return sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and (truth or 'sealed' not in p.relative_to(E).parts) and p.name!='experiment.json')
def inputs():
    base=E.parent
    paths=[base/'gdt832_joint_family_context_control/src'/n for n in ['decoder.cpp','reference_model.py','prepare.py']]
    paths += [base/'gdt833_reference_orthography_intervention'/n for n in ['src/prepare.py','src/ENCODER_SPEC.json','prepared/reference_native.jsonl','prepared/reference_ids.json','prepared/candidates.json','prepared/families.json']]
    paths += [base/f'gdt833_reference_orthography_intervention/prepared/world_{w}_discovery.json' for w in [83301,83302,83303]]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}
def main():
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--include-truth',action='store_true');p.add_argument('--status',required=True);p.add_argument('--validation',default='artifacts/SOURCE_VALIDATION.json');args=p.parse_args()
    upstream=inputs()
    if args.register:
        dest=E/'src/PREREG_LOCK.json'
        if dest.exists():raise RuntimeError('refuse preregistration overwrite')
        paths=[f for f in files() if f.relative_to(E).parts[0] in ('src','sources','prepared') or f.name in ('METHOD.md','PREREGISTRATION.md') or f.name in ('ROLE_AMBIGUITY.json','ROLE_AUDIT_833.json')]
        held=[f for f in paths if f.name.endswith('_held.json')]
        save(dest,{'schema':'GDT834_PREREG_LOCK_V1','stage':'after source and positional ambiguity gates; before every fresh fit and recovery evaluation','sha256':{f.relative_to(E).as_posix():sha(f) for f in paths if f not in held},'upstream_sha256':upstream,'held_commitments':{f.relative_to(E).as_posix():sha(f) for f in held},'sealed_commitments':{f.relative_to(E).as_posix():sha(f) for f in sorted((E/'sealed').glob('*.json'))}})
    m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix()
    m.update(title='Paired mixed control with individual symbol roles hidden',question='Can a fresh mixed-code control be recovered with individual symbol roles hidden while exact boundaries and nominal role capacities remain supplied?',claim_ceiling='Known architecture and boundaries, finite per-symbol role disambiguation; three encryption keys share one contentsplit; no general segmentation or Voynich language/meaning/translation.',status=args.status,updated='2026-09-06',dependencies=['GDT832','GDT833'],inputs=[{'path':f,'sha256':h,'role':'bound_predecessor_resource_or_implementation'} for f,h in upstream.items()],commands={'run':f'python3 {rel}/src/run.py --fit','validate':f'python3 {rel}/src/validate.py --check'},validation={'status':'PASS','artifact':f'{rel}/{args.validation}'})
    m['outputs']=[{'path':f.relative_to(ROOT).as_posix(),'sha256':sha(f),'role':'primary_report' if f.name=='REPORT.md' else 'reproducible_source_or_artifact'} for f in files(args.include_truth)]
    save(E/'experiment.json',m);print(json.dumps({'status':args.status,'bindings':len(m['outputs']),'truth_public':args.include_truth}))
if __name__=='__main__':main()
