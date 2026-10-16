"""Independent record/hash/conjunction checks; never validates palaeography."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
E = Path(__file__).resolve().parents[1]
ROOT = next(p for p in E.parents if (p/'vmanus-work').exists())
A = E/'artifacts'
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def time(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def main():
    lock=load(E/'src/VIEW_LOCK.json')
    for path,digest in lock['files'].items(): assert sha(ROOT/path)==digest,path
    result_lock=load(E/'src/RESULT_LOCK.json')
    for path,digest in result_lock['hashes'].items(): assert sha(ROOT/path)==digest,path
    inherited=load(ROOT/'experiments/yolo/gdt852_f75v_native_join_split_spacing/artifacts/SOURCES.json')
    assert load(A/'INHERITED_SOURCES.json')==inherited
    assert sha(ROOT/lock['native_image_relative_path'])==inherited['sha256']
    viewers={v:load(A/('VIEWER_'+v+'.json')) for v in ('A','B')}
    seal=load(A/'A_SEAL.json')
    assert seal['path']==str((A/'VIEWER_A.json').relative_to(ROOT))
    assert sha(ROOT/seal['path'])==seal['sha256']
    assert seal['before_observerB_assignment'] is True
    assert time(lock['utc'])<=time(viewers['A']['recorded_utc'])<=time(seal['sealed_utc'])<time(viewers['B']['recorded_utc'])
    assignment=A/'B_ASSIGNMENT.json'
    assignment_verified=False
    if assignment.exists():
        receipt=load(assignment)
        assert time(seal['sealed_utc'])<time(receipt['assigned_utc'])<=time(viewers['B']['recorded_utc'])
        assignment_verified=True
    for v,r in viewers.items():
        assert r['image_sha256']==inherited['sha256']
        assert r['T1'] in ('SPACE_LIKE','INTERNAL_LIKE','UNCLEAR')
        assert r['T2'] in ('SPACE_LIKE','INTERNAL_LIKE','UNCLEAR')
        assert r['contrast'] in ('LOCAL_CONTRAST','NO_CLEAR_CONTRAST','UNSCORABLE')
    source=ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/R_COMPLETE_UNITS.json'
    units=load(source)['units']; u=next(u for u in units if u['edition']=='IT2a')
    line=next(l for l in u['lines'] if l['metadata']['locus']=='f75v.47')
    targets=[dict(zip(u['group_columns'],g)) for g in line['groups'] if int(g[1]) in (5,6,10)]
    assert [(r['source_group_index'],r['ivtff_group_raw']) for r in targets]==[('5','ol'),('6','shedy'),('10','olshedy')]
    assert [r['source_group_id'] for r in targets]==['IT2a|f75v.47|G005','IT2a|f75v.47|G006','IT2a|f75v.47|G010']
    assert targets[0]['right_separator']==targets[1]['left_separator']=='DEFINITE_SPACE'
    supported=all(r.get('location_confidence')=='SUFFICIENT' and r['T1']=='SPACE_LIKE' and r['T2']=='INTERNAL_LIKE' and r['contrast']=='LOCAL_CONTRAST' for r in viewers.values())
    result=load(A/'RESULT.json')
    assert result['status']==('LOCAL_SPACING_CONTRAST_SUPPORTED' if supported else 'SPACING_CONTRAST_UNRESOLVED')
    assert result['image_sha256']==inherited['sha256']
    assert result['viewer_hashes']=={k:sha(A/('VIEWER_'+k+'.json')) for k in viewers}
    assert result['qualified']=={k:r.get('location_confidence')=='SUFFICIENT' and r['T1']=='SPACE_LIKE' and r['T2']=='INTERNAL_LIKE' and r['contrast']=='LOCAL_CONTRAST' for k,r in viewers.items()}
    assert result['views']=={k:{f:r[f] for f in ('location_confidence','T1','T2','contrast')} for k,r in viewers.items()}
    expected_source=dict(path=str(source.relative_to(ROOT)),sha256=sha(source),metadata=line['metadata'],group_columns=u['group_columns'],groups=[g for g in line['groups'] if int(g[1]) in (5,6,10)])
    assert load(A/'SOURCE.json')==expected_source
    report=dict(status='PASS_RECORDS_HASHES_FIXED_CONJUNCTION_ONLY',image_sha256=inherited['sha256'],
        verified_decision=result['status'],source_targets=targets,source_sha256=sha(source),
        a_seal_before_b_record=True,assignment_receipt_verified=assignment_verified,
        chronology_limit='File timestamps and asserted seal bind recorded sequence; tool-history chronology is not independently proven by these fields.',
        reviewer_viewed_image=False,palaeographic_validation=False,semantic_confirmation=False,
        hashes={n:sha(A/n) for n in ('VIEWER_A.json','VIEWER_B.json','A_SEAL.json','RESULT.json')},
        limitations=['B knew supplied group/internal target structure and live-route prior spacing summary; not completely structurally blind.',
                    'Two AI judgments of one physical image, not independent physical witnesses or human consensus.',
                    'No lexical identity, attachment, intention, actual word boundaries or population claim follows.'])
    (A/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'decision':result['status']}))
if __name__=='__main__': main()
