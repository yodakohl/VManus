import csv,hashlib,json
from datetime import datetime
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def main():
 s=json.loads((B/'src/SPEC.json').read_text());im=json.loads((A/'IMAGE_RECEIPT.json').read_text());obs=json.loads((A/'OBSERVATION.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 assert hashlib.sha256((ROOT/s['scope']).read_bytes()).hexdigest()==s['scope_sha256']
 assert s['rectangle_xywh']==[760,2180,1910,110] and im['url']==s['source_url']
 assert hashlib.sha256((ROOT/im['path']).read_bytes()).hexdigest()==im['sha256'] and Image.open(ROOT/im['path']).size==(1910,110)
 assert datetime.fromisoformat(s['registered_utc'])<datetime.fromisoformat(im['acquired_utc'])<datetime.fromisoformat(obs['recorded_utc'])
 assert json.loads((ROOT/'experiments/yolo/gdt1251_f76v_cheol_seam_view/artifacts/RESULT.json').read_text())['status']=='UNRESOLVED_REGION_MISLOCALIZED'
 assert obs['left_exterior']==obs['right_exterior']=='SPACE_LIKE' and obs['internal_cheol_chey_seam']=='INTERNAL_LIKE'
 assert json.loads((A/'RESULT.json').read_text())['status']==obs['status']=='LOCAL_INTERNAL_LIKE_SUPPORT'
 rows=list(csv.DictReader((ROOT/s['raw_lines']).open(),delimiter='\t'));assert {r['edition'] for r in rows}=={'ZL3b','IT2a','RF1b'}
 out={'status':'PASS','scope':'Source identity, corrected-box declaration, chronology and faithful decision accounting only; no software validation of visual judgment, meaning or independent confirmation.'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
