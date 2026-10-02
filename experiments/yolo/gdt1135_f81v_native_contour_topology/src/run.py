#!/usr/bin/env python3
"""Package native observer receipts; no visual inference or semantic score."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
def main():
    lock=json.loads((P/'artifacts/PREREG_LOCK.json').read_text())
    for name,digest in lock['sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    schema=json.loads((P/'src/OBSERVATION_SCHEMA.json').read_text())
    source=json.loads((P/'src/SOURCE.json').read_text())
    files=[P/'artifacts/OBSERVER_ROOT.json',P/'artifacts/OBSERVER_B.json']
    if any(not f.exists() for f in files):
        print(json.dumps({'status':'REGISTERED_WAITING_FOR_NATIVE_OBSERVATIONS'}));return 2
    receipts=[]
    for f in files:
        d=json.loads(f.read_text())
        assert all(k in d for k in schema['required_fields']),f.name
        assert d['source_sha256']==source['sha256'],f.name
        receipts.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'observer':d['observer'],'topology':d['topology']})
    result={'status':'TWO_NATIVE_RECEIPTS_PACKAGED_NO_VISUAL_TRUTH_CERTIFICATION','receipts':receipts,'semantic_scoring':False,'confirmed_words':0,'independent_meaning_confirmation_capacity':0}
    (P/'artifacts/RECEIPT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));return 0
if __name__=='__main__':raise SystemExit(main())
