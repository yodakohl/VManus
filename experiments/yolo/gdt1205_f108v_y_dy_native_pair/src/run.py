"""Apply the frozen decision to one sealed, source-aware visual observation."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def load(name):return json.loads((A/name).read_text())
def main():
    lock=load('REGISTRATION_LOCK.json')
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    obs=load('OBSERVATION.json');seal=load('OBSERVATION_SEAL.json')
    for file,key in [('OBSERVATION.json','observation_sha256'),('SOURCE_IMAGE.json','source_receipt_sha256'),('REGION_IMAGES.json','region_receipt_sha256')]:assert hashlib.sha256((A/file).read_bytes()).hexdigest()==seal[key]
    assert hashlib.sha256((D/'PREREGISTRATION.md').read_bytes()).hexdigest()==seal['registration_sha256']
    ts=obs['targets'];flanks=obs['flank_pairs'];assert [x['locus'] for x in ts]==['f108v.35','f108v.52'] and [x['side'] for x in flanks]==['left','right']
    located=all(t['located'] for t in ts)
    counter=located and (ts[0]['center_extra_body']=='PRESENT' or ts[1]['center_extra_body']=='ABSENT' or any(t['boundaries']=='CONTRADICTED' for t in ts) or any(f['classification']=='DIFFERENT_SEQUENCE' for f in flanks))
    support=located and ts[0]['center_extra_body']=='ABSENT' and ts[1]['center_extra_body']=='PRESENT' and all(t['boundaries']=='BOTH_SPACE_LIKE' for t in ts) and all(f['classification']=='SAME_SEQUENCE_COMPATIBLE' for f in flanks)
    status='VISUAL_COUNTEREVIDENCE' if counter else 'SOURCE_AWARE_VISUAL_SUPPORT' if support else 'UNRESOLVED_NATIVE_PAIR'
    result={'experiment':'GDT1205','status':status,'targets':[{k:t[k] for k in ('locus','located','center_extra_body','boundaries')} for t in ts],
        'flank_pairs':[{k:f[k] for k in ('side','classification')} for f in flanks],'observer_count':1,'source_photographs':1,'source_regions':2,'independent_confirmation_capacity':0,
        'native_meanings_assigned':0,'word_identity_proven':False,'earlier_literal_result_replaced':False,
        'scope':'One informed qualitative visual check; source and software validation do not independently establish palaeographic truth, lexical identity, morphology or meaning.'}
    (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(A/'RUN_RECEIPT.json').write_text(json.dumps({'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
