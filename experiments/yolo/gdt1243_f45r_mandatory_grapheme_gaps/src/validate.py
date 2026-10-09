"""Separate source/chronology/reduction validator; does not infer image truth."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(name):return json.loads((A/name).read_text())
def main():
 lock=read('REGISTRATION_LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 t=read('TARGETS.json');old=json.loads((ROOT/'experiments/yolo/gdt1208_f45r_repeated_dal_body/artifacts/REGION_IMAGES.json').read_text())[0]
 assert t['source_path']==old['path'] and t['source_sha256']==old['sha256']
 assert hashlib.sha256((ROOT/t['source_path']).read_bytes()).hexdigest()==old['sha256']
 o=read('OBSERVATION.json');seal=read('OBSERVATION_SEAL.json');r=read('RESULT.json')
 assert hashlib.sha256((A/'OBSERVATION.json').read_bytes()).hexdigest()==seal['sha256']
 assert datetime.fromisoformat(lock['registered_utc'])<datetime.fromisoformat(o['observed_utc'])<=datetime.fromisoformat(seal['sealed_utc'])<=datetime.fromisoformat(read('RUN_RECEIPT.json')['completed_utc'])
 assert [x['id'] for x in o['seams']]==t['seams'] and len(t['seams'])==10
 n_contact=n_gap=n_unknown=0
 for row in o['seams']:
  assert row['reason']
  if row['judgment']=='DEFINITE_INK_CONTACT':n_contact+=1;assert row['located'] is True
  elif row['judgment']=='CLEAR_WHITE_GAP':n_gap+=1;assert row['located'] is True
  else:assert row['judgment']=='UNRESOLVED';n_unknown+=1
 if n_contact:expected='SOURCE_AWARE_GAP_RULE_COUNTEREVIDENCE'
 elif n_gap==10:expected='LOCAL_NECESSARY_GAPS_NOT_CONTRADICTED'
 else:expected='UNRESOLVED'
 assert r['status']==expected and r['confirmed_meanings']==0
 assert r['counts']=={k:v for k,v in [('DEFINITE_INK_CONTACT',n_contact),('CLEAR_WHITE_GAP',n_gap),('UNRESOLVED',n_unknown)] if v}
 out={'status':'PASS','experiment':'GDT1243','validated_utc':datetime.now(timezone.utc).isoformat(),'frozen_files':len(lock['files']),'seams':10,'scope':'Source/hash/chronology/schema/reduction only; no validation of physical ink or meaning.'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
