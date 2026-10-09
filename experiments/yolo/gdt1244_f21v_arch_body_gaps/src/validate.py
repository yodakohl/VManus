"""Separate source, chronology and decision check; no physical-truth claim."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(n):return json.loads((A/n).read_text())
def main():
 lock=read('REGISTRATION_LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 t=read('TARGETS.json');r=json.loads((ROOT/'experiments/yolo/gdt1242_f21v_four_body_source/artifacts/REGION_IMAGE.json').read_text())
 assert (t['source_path'],t['source_sha256'],t['source_url'])==(r['path'],r['sha256'],r['url'])
 assert hashlib.sha256((ROOT/t['source_path']).read_bytes()).hexdigest()==r['sha256']
 o=read('OBSERVATION.json');seal=read('OBSERVATION_SEAL.json');result=read('RESULT.json')
 assert hashlib.sha256((A/'OBSERVATION.json').read_bytes()).hexdigest()==seal['sha256']
 assert datetime.fromisoformat(lock['registered_utc'])<datetime.fromisoformat(o['observed_utc'])<=datetime.fromisoformat(seal['sealed_utc'])<=datetime.fromisoformat(read('RUN_RECEIPT.json')['completed_utc'])
 assert [x['id'] for x in o['seams']]==t['seams']==['LEFT_K_E','RIGHT_E_S']
 contact=gap=0
 for x in o['seams']:
  assert x['reason']
  if x['judgment']=='DEFINITE_INK_CONTACT':contact+=1;assert x['located'] is True
  elif x['judgment']=='CLEAR_WHITE_GAP':gap+=1;assert x['located'] is True
  else:assert x['judgment']=='UNRESOLVED'
 expected='UNRESOLVED'
 if gap==2:expected='LOCAL_MIXED_GAPS_NOT_CONTRADICTED'
 if contact:expected='SOURCE_AWARE_MIXED_GAP_COUNTEREVIDENCE'
 assert result['status']==expected and result['judgments']==[x['judgment'] for x in o['seams']] and result['confirmed_meanings']==0
 out={'experiment':'GDT1244','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'frozen_files':len(lock['files']),'scope':'Source/hash/chronology/schema/reduction; not palaeography or meaning.'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
