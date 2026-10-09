"""Reduce sealed manual judgments; no image inference."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 o=json.loads((A/'OBSERVATION.json').read_text());seal=json.loads((A/'OBSERVATION_SEAL.json').read_text())
 assert hashlib.sha256((A/'OBSERVATION.json').read_bytes()).hexdigest()==seal['sha256']
 assert [r['id'] for r in o['seams']]==['LEFT_K_E','RIGHT_E_S']
 v=[r['judgment'] for r in o['seams']];assert set(v)<={'CLEAR_WHITE_GAP','DEFINITE_INK_CONTACT','UNRESOLVED'}
 status='SOURCE_AWARE_MIXED_GAP_COUNTEREVIDENCE' if 'DEFINITE_INK_CONTACT' in v else ('LOCAL_MIXED_GAPS_NOT_CONTRADICTED' if v==['CLEAR_WHITE_GAP']*2 else 'UNRESOLVED')
 out={'experiment':'GDT1244','status':status,'judgments':v,'confirmed_meanings':0,'scope':'One informed observation of two mandatory mixed seams under fixed literal body binding; not independent palaeography.'}
 assert not (A/'RESULT.json').exists();(A/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
 (A/'RUN_RECEIPT.json').write_text(json.dumps({'completed_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
