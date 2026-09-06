#!/usr/bin/env python3
"""Bind GDT835 stages and committed predecessor inputs."""
import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];OLD=E.parent/'gdt834_role_blind_mixed_control'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def output_files():return sorted(p for p in E.rglob('*') if p.is_file() and not {'runtime','__pycache__'}.intersection(p.relative_to(E).parts) and p.name!='experiment.json')
def sections():
    d=[OLD/'artifacts/FIT_LOCK.json',OLD/'src/ENCODER_SPEC.json',OLD/'src/decoder.cpp']
    h=[OLD/'sealed/source_truth.json',OLD/'artifacts/VALIDATION.json',OLD/'artifacts/RESULT.json',OLD/'artifacts/POST_RESULT_AUDIT.json']
    for world in (83401,83402,83403):
        h.append(OLD/f'sealed/world_{world}_truth.json')
        for arm in ('BLIND','TYPED'):
            pre='typed_' if arm=='TYPED' else ''
            d.append(OLD/f'prepared/world_{world}_{pre}discovery.json');h.append(OLD/f'prepared/world_{world}_{pre}held.json')
            d.extend(OLD/f'artifacts/fits/world_{world}_{arm}_start{s}.json' for s in range(8))
    provenance=[OLD/'src/prepare.py',OLD/'prepared/reference.jsonl',E.parent/'gdt833_reference_orthography_intervention/src/prepare.py',E.parent/'gdt832_joint_family_context_control/src/prepare.py']
    return {name:{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)} for name,paths in [('discovery_input_sha256',d),('confirmation_input_sha256',h),('provenance_input_sha256',provenance)]}
def main():
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',required=True);p.add_argument('--validation',default='artifacts/TESTS.json');a=p.parse_args();parts=sections()
    if a.register:
        target=E/'src/PREREG_LOCK.json'
        if target.exists():raise RuntimeError('refuse registration overwrite')
        code=[f for f in output_files() if f.relative_to(E).parts[0]=='src' or f.name in ('METHOD.md','PREREGISTRATION.md')]
        save(target,{'schema':'GDT835_REGISTRATION_V1','stage':'before new discovery classifications; predecessor keys/truth alreadypublic; source-context census exploratory', 'code_sha256':{f.relative_to(E).as_posix():sha(f) for f in code},**parts})
    m=json.loads((E/'experiment.json').read_text());rel=E.relative_to(ROOT).as_posix();bound={k:v for section in parts.values() for k,v in section.items()}
    m.update(title='Necessary wholeword precedence on the frozen GDT834 key panel',question='Does the mandatory wholeword-first inverse condition separate correct and incorrect observed key maps in the complete frozen GDT834 restart panel?',claim_ceiling='Retrospective fixed-panel necessary mandatory-W compatibility; not full suffix inversion, optional abbreviation, new end-to-end recovery or Voynich evidence.',status=a.status,updated='2026-09-06',dependencies=['GDT832','GDT833','GDT834'],inputs=[{'path':k,'sha256':v,'role':'fixed_predecessor_input'} for k,v in sorted(bound.items())],commands={'run':f'python3 {rel}/src/run.py --gate','validate':f'python3 {rel}/src/validate.py --check'},validation={'status':'PASS','artifact':f'{rel}/{a.validation}'})
    m['outputs']=[{'path':f.relative_to(ROOT).as_posix(),'sha256':sha(f),'role':'primary_report' if f.name=='REPORT.md' else 'reproducible_source_or_artifact'} for f in output_files()]
    save(E/'experiment.json',m);print(json.dumps({'status':a.status,'inputs':len(bound),'outputs':len(m['outputs'])}))
if __name__=='__main__':main()
