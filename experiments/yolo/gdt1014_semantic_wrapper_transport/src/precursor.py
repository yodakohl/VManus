from pathlib import Path
import json,datetime,hashlib
from wrappers import relations,contradictions
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
if __name__=='__main__':
    reg=A/'PRECURSOR_LOCK.json'
    assert not reg.exists(),'precursor has already been registered'
    source=R/'experiments/yolo/gdt1012_transport_necessary_bank_sequence/artifacts/ORIGINAL_CANDIDATES.json'
    paths=[source,E/'DECISION.md',E/'PRECURSOR_REGISTRATION.md',E/'src/precursor.py',E/'src/wrappers.py']
    reg.write_text(json.dumps(dict(registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')
    cases=json.loads(source.read_text());groups=relations(cases[0]['code']);rows=[]
    for case in cases:
        errors=contradictions(case['code'],groups);rows.append(dict(id=case['id'],contradictions=errors,status='CONTRADICTED' if errors else 'COMPATIBLE'))
    out=dict(registered_before_check=True,public_before_check=False,disclosure='Original-only preflight of previously exposed fixed dictionaries;new unconstrained extension not queried.',groups=groups,rows=rows,counts={v:sum(r['status']==v for r in rows) for v in ('COMPATIBLE','CONTRADICTED')},completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (A/'PRECURSOR.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
