"""Reduce sealed manual observation; no image inference."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (A/'RESULT.json').exists(),'Retained result exists'
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 op=A/'OBSERVATION.json';o=json.loads(op.read_text());seal=json.loads((A/'OBSERVATION_SEAL.json').read_text())
 assert hashlib.sha256(op.read_bytes()).hexdigest()==seal['sha256']
 vals=[o['repeated_shape'],o['outer_shapes'],o['external_clearances']]
 if o['location']=='UNLOCATED':status='UNLOCATED'
 elif any(v in ('CONTRADICTED','DIFFERENT') for v in vals) or (o['body_count'] is not None and o['body_count']!=4):status='VISUAL_COUNTEREVIDENCE'
 elif o['body_count']==4 and vals==['COMPATIBLE','COMPATIBLE','SPACE_LIKE']:status='SOURCE_AWARE_FOUR_BODY_COMPATIBILITY'
 else:status='UNRESOLVED'
 result={'experiment':'GDT1242','status':status,'body_count':o['body_count'],'native_meanings':0,'scope':'One source-aware photographic judgment; not native alphabet, pen movement, expansion or meaning confirmation','observation_sha256':seal['sha256']}
 write(A/'RESULT.json',result);write(A/'RUN_RECEIPT.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),'status':'COMPLETE'});print(json.dumps(result))
if __name__=='__main__':main()
