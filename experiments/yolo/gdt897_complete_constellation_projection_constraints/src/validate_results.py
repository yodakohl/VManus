"""Replay every ordered witness tuple and compare independent search scope.

No search is rerun. UNKNOWN is not a conflicting mathematical conclusion.
Geometry validation is a separately hash-bound prerequisite, not rerun here.
"""
import gzip
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def flat(t,n):
    z=0
    for v in t:
        z=z*n+v
    return z

def flip(m):
    return ((m&1)<<2)|(m&2)|((m&4)>>2)

def witness_check(case,record):
    n=case['n']; k=3 if case['mode']=='gnomonic' else 4
    w=record['witness']; g=record.get('g',record.get('orientation'))
    if g not in (-1,1) or len(w)!=n or any(type(x) is not int for x in w) or sorted(w)!=list(range(n)):
        raise ValueError('invalid witness bijection/orientation')
    source=case['source_masks']; target=case['target_masks']; count=0
    # Every ordered distinct tuple; no reliance on a tensor-symmetry shortcut.
    for t in itertools.permutations(range(n),k):
        a=source[flat(t,n)]; b=target[flat(tuple(w[u] for u in t),n)]
        if not ((flip(a) if g==-1 else a)&b):
            raise ValueError('witness violates a packet constraint')
        count+=1
    return count

def main():
    names=['SEARCH_PACKET.json.gz','RESULT.json','INDEPENDENT_RESULT.json','GEOMETRY_VALIDATION.json']
    raw={name:(ROOT/'artifacts'/name).read_bytes() for name in names}
    packet=json.loads(gzip.decompress(raw[names[0]]))
    primary=json.loads(raw[names[1]]); independent=json.loads(raw[names[2]])
    geometry=json.loads(raw[names[3]])
    ph=sha(raw[names[0]])
    for record in (primary,independent,geometry):
        if record['packet_sha256']!=ph:
            raise ValueError('packet hash mismatch')
    if geometry['status']!='PASS':
        raise ValueError('geometry validation did not pass')
    def indexed(rows):
        out={r['case_id']:r for r in rows}
        if len(out)!=len(rows):
            raise ValueError('duplicate case ID')
        return out
    cases=indexed(packet['cases']); pp=indexed(primary['cases']); ii=indexed(independent['cases'])
    if set(cases)!=set(pp) or set(cases)!=set(ii):
        raise ValueError('case coverage mismatch')
    results=[]; total=0; failures=0; unsupported=0
    for cid,case in cases.items():
        p=pp[cid]; q=ii[cid]; checked=[]
        if sorted(o['g'] for o in p['orientations'])!=[-1,1]:
            raise ValueError('primary orientation coverage mismatch')
        for origin,record in [('primary',p),('independent',q)]:
            for o in record['orientations']:
                if o['status']=='INVARIANT_COMPATIBLE':
                    count=witness_check(case,o); total+=count
                    checked.append(dict(origin=origin,orientation=o.get('g',o.get('orientation')),ordered_tuples=count))
        pu=all(o['status']=='UNSAT_INVARIANTS' for o in p['orientations'])
        pc=any(o['status']=='INVARIANT_COMPATIBLE' for o in p['orientations'])
        qu=q['status']=='UNSAT'
        qc=q['status']=='INVARIANT_COMPATIBLE'
        pby={o['g']:o['status'] for o in p['orientations']}
        qby={o['orientation']:o['status'] for o in q['orientations']}
        if len(qby)!=len(q['orientations']) or any(g not in (-1,1) for g in qby):
            raise ValueError('invalid independent orientation coverage')
        orientation_conflict=any(
            (pby[g]=='UNSAT_INVARIANTS' and status=='INVARIANT_COMPATIBLE') or
            (pby[g]=='INVARIANT_COMPATIBLE' and status=='UNSAT')
            for g,status in qby.items())
        if qu and (sorted(o['orientation'] for o in q['orientations'])!=[-1,1] or
                   any(o['status']!='UNSAT' for o in q['orientations'])):
            raise ValueError('independent UNSAT lacks both exhausted orientations')
        if orientation_conflict or (pu and qc) or (pc and qu):
            status='FAIL_CONTRADICTORY_SEARCH_RESULTS'; failures+=1
        elif pu and qu:
            status='PASS_INDEPENDENTLY_REPRODUCED_INVARIANT_EXCLUSION'
        elif pu:
            status='PRIMARY_EXCLUSION_NOT_INDEPENDENTLY_REPRODUCED'; unsupported+=1
        elif pc:
            status='PASS_WITNESS_ONLY_NO_CONTINUOUS_FEASIBILITY_CLAIM'
        else:
            status='UNKNOWN_SEARCH_SCOPE'
        results.append(dict(case_id=cid,mode=case['mode'],status=status,
                            primary_orientation_statuses=[o['status'] for o in p['orientations']],
                            independent_status=q['status'],witness_checks=checked))
    out=dict(schema='GDT897_RESULT_VALIDATION_V1',
             status='FAIL' if failures else 'PASS_WITH_UNREPRODUCED_EXCLUSIONS' if unsupported else 'PASS',
             packet_sha256=ph,input_sha256={n:sha(b) for n,b in raw.items()},
             validator_sha256=sha(Path(__file__).read_bytes()),geometry_validation_status='PASS',
             geometry_validation_scope=geometry['scope'],ordered_witness_tuples_checked=total,
             unreproduced_primary_exclusions=unsupported,cases=results,
             claim_ceiling='Unknown independent searches do not contradict primary exclusions; only reproduced exclusions receive independent credit. Witnesses establish necessary-invariant compatibility, not a continuous projection, object identification, or names.')
    (ROOT/'artifacts/RESULT_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','ordered_witness_tuples_checked','unreproduced_primary_exclusions')}))

if __name__=='__main__':
    main()
