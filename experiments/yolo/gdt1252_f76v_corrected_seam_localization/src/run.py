import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=B/'artifacts'
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 s=json.loads((B/'src/SPEC.json').read_text());assert hashlib.sha256((R/s['scope']).read_bytes()).hexdigest()==s['scope_sha256']
 im=json.loads((A/'IMAGE_RECEIPT.json').read_text());assert hashlib.sha256((R/im['path']).read_bytes()).hexdigest()==im['sha256']
 o=json.loads((A/'OBSERVATION.json').read_text());assert o['status']=='LOCAL_INTERNAL_LIKE_SUPPORT'
 assert [o[x] for x in ['left_exterior','internal_cheol_chey_seam','right_exterior']]==['SPACE_LIKE','INTERNAL_LIKE','SPACE_LIKE']
 out={'status':o['status'],'fixed_locus':'f76v.28','judgment':'Qualitative local spacing only','original1251status':'UNRESOLVED_REGION_MISLOCALIZED','no_meaning':True}
 (A/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
