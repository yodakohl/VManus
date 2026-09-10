"""Independent provenance/result audit of the single Bernstein refinement.

No geometry computation or search reruns. Original boxes and source masks
must be identical; full target tensors must alternate and only lose signs.
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from independent_search import check_tensor
from validate_results import witness_check

ROOT=Path(__file__).resolve().parents[1]
FREEZE='2fd54a53'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    names=['SEARCH_PACKET.json.gz','BERNSTEIN_PACKET.json.gz','BERNSTEIN_VALIDATION.json',
           'REFINED_RESULT.json','REFINED_INDEPENDENT_RESULT.json','PRECISION_AMENDMENT.json']
    raw={name:(ROOT/'artifacts'/name).read_bytes() for name in names}
    old=json.loads(gzip.decompress(raw[names[0]])); new=json.loads(gzip.decompress(raw[names[1]]))
    report=json.loads(raw[names[2]]); primary=json.loads(raw[names[3]]); independent=json.loads(raw[names[4]])
    oldhash=sha(raw[names[0]]); newhash=sha(raw[names[1]])
    assert new['refinement_of_sha256']==oldhash
    assert report['status']=='PASS' and report['old_packet_sha256']==oldhash and report['refined_packet_sha256']==newhash
    assert primary['packet_sha256']==independent['packet_sha256']==newhash
    assert primary['implementation']=='primary' and independent['implementation']=='independent'
    assert all(new[key]==value for key,value in old.items() if key!='cases')
    assert set(new)==set(old)|{'refinement','refinement_of_sha256'}
    # Bind kernels, producers, search engines and amendment to pre-run commit.
    repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())
    frozen={}
    for relative in ['src/bernstein.cpp','src/bernstein_reference.cpp','src/prepare_refined.py',
                     'src/run_refined.py','src/search.cpp','src/run.py','src/independent_search.py',
                     'artifacts/PRECISION_AMENDMENT.json','artifacts/SEARCH_PACKET.json.gz']:
        path=ROOT/relative; rel=path.relative_to(repo).as_posix()
        before=subprocess.check_output(['git','show',FREEZE+':'+rel],cwd=repo)
        assert before==path.read_bytes(),relative
        frozen[relative]=sha(before)
    for name,digest in report['kernels'].items():
        assert frozen['src/'+name]==digest
    def index(rows):
        out={r['case_id']:r for r in rows}
        assert len(out)==len(rows)
        return out
    previous=index([c for c in old['cases'] if c['mode']=='stereographic'])
    cases=index(new['cases']); pp=index(primary['cases']); ii=index(independent['cases'])
    assert set(previous)==set(cases)==set(pp)==set(ii)
    changed=0; maskcells=0; checkedtargets=set(); totals=0; unsupported=0; failures=0; results=[]
    for cid,c in cases.items():
        before=previous[cid]
        assert {k:v for k,v in c.items() if k!='target_masks'}=={k:v for k,v in before.items() if k!='target_masks'}
        assert len(c['target_masks'])==len(before['target_masks'])
        assert all((a&b)==a for a,b in zip(c['target_masks'],before['target_masks']))
        check_tensor(c['source_masks'],c['n'],4)
        targetkey=c['target_id']
        if targetkey not in checkedtargets:
            check_tensor(c['target_masks'],c['n'],4)
            changed+=sum(a!=b for a,b in zip(c['target_masks'],before['target_masks']))
            maskcells+=len(c['target_masks']); checkedtargets.add(targetkey)
        else:
            assert c['target_masks']==next(v['target_masks'] for v in cases.values() if v['target_id']==targetkey)
        p=pp[cid]; q=ii[cid]
        pm={o['g']:o['status'] for o in p['orientations']}
        qm={o['orientation']:o['status'] for o in q['orientations']}
        assert len(pm)==len(p['orientations'])==2 and set(pm)=={-1,1}
        assert len(qm)==len(q['orientations']) and set(qm)<={-1,1}
        checks=[]
        for origin,r in [('primary',p),('independent',q)]:
            for o in r['orientations']:
                if o['status']=='INVARIANT_COMPATIBLE':
                    count=witness_check(c,o); totals+=count
                    checks.append(dict(origin=origin,orientation=o.get('g',o.get('orientation')),ordered_tuples=count))
        pu=all(s=='UNSAT_INVARIANTS' for s in pm.values())
        pc='INVARIANT_COMPATIBLE' in pm.values()
        qu=q['status']=='UNSAT'; qc=q['status']=='INVARIANT_COMPATIBLE'
        if qu:
            assert set(qm)=={-1,1} and all(s=='UNSAT' for s in qm.values())
        if qc:
            assert 'INVARIANT_COMPATIBLE' in qm.values()
        conflict=any((pm[g]=='UNSAT_INVARIANTS' and s=='INVARIANT_COMPATIBLE') or
                     (pm[g]=='INVARIANT_COMPATIBLE' and s=='UNSAT') for g,s in qm.items())
        if conflict or (pu and qc) or (pc and qu):
            status='FAIL_CONTRADICTORY_SEARCH_RESULTS'; failures+=1
        elif pu and qu:
            status='PASS_INDEPENDENTLY_REPRODUCED_INVARIANT_EXCLUSION'
        elif pu:
            status='PRIMARY_EXCLUSION_NOT_INDEPENDENTLY_REPRODUCED'; unsupported+=1
        elif pc or qc:
            status='PASS_WITNESS_ONLY_NO_CONTINUOUS_FEASIBILITY_CLAIM'
        else:
            status='UNKNOWN_BUDGET_NO_EXCLUSION'
        results.append(dict(case_id=cid,status=status,primary_orientations=pm,
                            independent_orientations=qm,independent_status=q['status'],witness_checks=checks))
    out=dict(schema='GDT897_REFINED_VALIDATION_V1',status='FAIL' if failures else
             'PASS_WITH_UNREPRODUCED_EXCLUSIONS' if unsupported else 'PASS',
             freeze_commit=FREEZE,frozen_sha256=frozen,input_sha256={n:sha(b) for n,b in raw.items()},
             validator_sha256=sha(Path(__file__).read_bytes()),unchanged_source_cases_and_boxes=True,
             only_original_stereographic_cases=True,all_refined_masks_subset_original=True,
             alternating_target_tensor_cells_checked=maskcells,changed_target_tensor_cells=changed,
             bernstein_kernel_validation='PASS',ordered_witness_tuples_checked=totals,
             unreproduced_primary_exclusions=unsupported,cases=results,
             claim_ceiling='Provenance and necessary-invariant result validation only. UNKNOWN does not contradict UNSAT and does not certify exclusion. No continuous map or celestial/name identification.')
    (ROOT/'artifacts/REFINED_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','ordered_witness_tuples_checked','unreproduced_primary_exclusions']}))

if __name__=='__main__':
    main()
