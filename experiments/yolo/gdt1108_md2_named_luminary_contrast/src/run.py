#!/usr/bin/env python3
"""Check retained acquisition and publish the fixed manual comparison as JSON.
Does not decode an image or establish the correctness of the native reading.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
def main():
    receipt=json.loads((HERE/'artifacts/SOURCE_RECEIPT.json').read_text())
    assert receipt['folio']==receipt['canvas_label']=='41r'
    assert hashlib.sha256((ROOT/receipt['image_path']).read_bytes()).hexdigest()==receipt['sha256']
    lock=json.loads((HERE/'PREREG_LOCK.json').read_text())
    for name,digest in lock['input_hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    comparison=json.loads((HERE/'artifacts/MANUAL_OBSERVATIONS.json').read_text())
    result={'experiment_id':'GDT1108','decision':'NO_NATIVE_PORTRAIT_OWNER_BINDING__TARGET_UNRANKED','source':receipt,'observations':comparison,'native_owner_gate':False,'full_phase_binding':False,'new_target_access':False,'confirmed_words':0,'independent_target_confirmation_folios':0,'claim_ceiling':'One complete source page and all four visual comparisons; no selected Sun/Moon word or full-phase identity.'}
    (HERE/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['decision'])
if __name__=='__main__':main()
