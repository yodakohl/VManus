#!/usr/bin/env python3
"""Independent identity/coverage checks only; manual meaning is not validated."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
def main():
    result=json.loads((HERE/'artifacts/RESULT.json').read_text())
    receipt=json.loads((HERE/'artifacts/SOURCE_RECEIPT.json').read_text())
    lock=json.loads((HERE/'PREREG_LOCK.json').read_text())
    assert result['source']==receipt
    assert datetime.datetime.fromisoformat(lock['registered_utc'])<datetime.datetime.fromisoformat(receipt['received_utc'])
    image=(ROOT/receipt['image_path']).read_bytes()
    assert len(image)==receipt['bytes'] and image[:2]==b'\xff\xd8'
    assert hashlib.sha256(image).hexdigest()==receipt['sha256']
    for path,digest in lock['input_hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    manual=json.loads((HERE/'artifacts/MANUAL_OBSERVATIONS.json').read_text())
    assert result['observations']==manual
    fields={'named_owner','geometry','face_direction','radial_marks','colored_fields','facial_marks','text_relationship'}
    assert len(manual['luminary_portraits'])==2
    assert all(set(x['features'])==fields for x in manual['luminary_portraits'])
    pairs={(x['target'],x['source']) for x in manual['pairings']}
    assert pairs=={(t,s) for t in ('upper','lower') for s in ('left','right')}
    assert all(x['matches'] and x['mismatches_or_unknowns'] for x in manual['pairings'])
    assert result['native_owner_gate'] is False and result['confirmed_words']==0
    assert result['decision']=='NO_NATIVE_PORTRAIT_OWNER_BINDING__TARGET_UNRANKED'
    validation={'status':'PASS','scope':'Pinned inputs, preregistration-before-acquisition, full JPEG identity, two source inventories and four-pair conservation, zero-word ceiling; NOT native reading, image classification, semantics or source lineage.','new_target_access':False}
    (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation))
if __name__=='__main__':main()
