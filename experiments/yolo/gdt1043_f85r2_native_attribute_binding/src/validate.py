#!/usr/bin/env python3
"""Integrity/scope only; no visual or semantic validation."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1]
R=B.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    result=json.loads((B/'artifacts/RESULT.json').read_text())
    lock=json.loads((B/'src/PREREG_LOCK.json').read_text())
    for path,h in {**lock['files'],**result['receipts']}.items(): assert sha(R/path)==h,path
    assert not lock['target_pixels_opened']
    originals={'OBSERVER_B_INITIAL.json':'f66d1604ca6a25d353f73fe979aa3e84906744991bc0a6a2dc3765ac007d336b','OBSERVER_ROOT.json':'012c000b907e8d5a498b15890a6857a872c476b81d784abd5ca162d7bb5569ff','OBSERVER_ROOT_DETAILS.json':'40287225d965d33f4ecc561a018b3ea43b7af0629416d45417bd09eb420e1fc2'}
    for p,h in originals.items(): assert sha(B/'artifacts'/p)==h,p
    source=json.loads((B/'artifacts/SOURCE_FINAL.json').read_text())
    details=json.loads((B/'artifacts/DETAIL_SOURCES_B.json').read_text())['details']
    assert source['region']==[0,0,3000,3890] and len(details)==9
    checked=0
    for d in [source]+details:
        x,y,w,h=d['region']
        assert min(x,y)>=0 and w>0 and h>0 and x+w<=3000 and y+h<=3890
        assert d['url'].startswith('https://collections.library.yale.edu/iiif/2/1006229/')
        p=R/d['path']
        if p.exists():
            assert sha(p)==d['sha256'],str(p.relative_to(R))
            checked+=1
    cells=result['cells']
    assert len(cells)==6 and {c['attribute'] for c in cells}==set(range(1,7))
    assert all(not c['binding'] and c['alternatives'] for c in cells)
    assert result['confirmed_words']==result['independent_meaning_capacity']==0
    assert not result['significance_claim'] and not result['score_ready_relation_packet']
    out=dict(status='PASS_RECEIPTS_SCOPE_AND_COMPLETENESS',claim_ceiling='Integrity only, not independent visual or meaning confirmation',registered_attributes=6,bounded_image_receipts=10,locally_verified_images=checked,result_sha256=sha(B/'artifacts/RESULT.json'))
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))
if __name__=='__main__': main()
