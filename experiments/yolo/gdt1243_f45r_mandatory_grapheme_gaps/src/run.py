"""Reduce a sealed manual observation. No automatic image inference."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 o=json.loads((A/'OBSERVATION.json').read_text()); seal=json.loads((A/'OBSERVATION_SEAL.json').read_text())
 assert hashlib.sha256((A/'OBSERVATION.json').read_bytes()).hexdigest()==seal['sha256']
 t=json.loads((A/'TARGETS.json').read_text());assert [x['id'] for x in o['seams']]==t['seams']
 values=[x['judgment'] for x in o['seams']];assert set(values)<={'CLEAR_WHITE_GAP','DEFINITE_INK_CONTACT','UNRESOLVED'}
 status='SOURCE_AWARE_GAP_RULE_COUNTEREVIDENCE' if 'DEFINITE_INK_CONTACT' in values else ('LOCAL_NECESSARY_GAPS_NOT_CONTRADICTED' if all(v=='CLEAR_WHITE_GAP' for v in values) else 'UNRESOLVED')
 result={'experiment':'GDT1243','status':status,'counts':{v:values.count(v) for v in sorted(set(values))},'confirmed_meanings':0,'claim_ceiling':'Single informed image judgment of a necessary condition under literal body binding; no palaeographic or semantic confirmation.'}
 assert not (A/'RESULT.json').exists()
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 (A/'RUN_RECEIPT.json').write_text(json.dumps({'completed_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
