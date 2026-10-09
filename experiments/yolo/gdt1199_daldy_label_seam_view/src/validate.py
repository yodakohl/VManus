from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text());obs=json.loads((A/'OBSERVATION.json').read_text());r=json.loads((A/'RESULT.json').read_text());seal=json.loads((A/'OBSERVATION_SEAL.json').read_text())
 for p,d in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
 assert hashlib.sha256((A/'OBSERVATION.json').read_bytes()).hexdigest()==seal['observation_sha256']
 assert hashlib.sha256((D/'PREREGISTRATION.md').read_bytes()).hexdigest()==seal['registration_sha256']
 p=ROOT/obs['source_image'];assert hashlib.sha256(p.read_bytes()).hexdigest()==obs['image_sha256']==lock['image_sha256']
 with Image.open(p) as im:assert im.size==(2868,3735)
 ts={x['locus']:x for x in obs['targets']};assert len(ts)==2 and set(ts)=={'f75v.22','f75v.32'}
 for t in ts.values():assert type(t['located']) is bool and t['seam'] in {'SPACE_LIKE','INTERNAL_LIKE','UNRESOLVED','UNLOCATED'} and t['observation'] and t['rivals']
 positive=ts['f75v.22']['located'] and ts['f75v.32']['located'] and ((ts['f75v.22']['seam']=='SPACE_LIKE' and ts['f75v.32']['seam']=='INTERNAL_LIKE') or (ts['f75v.32']['seam']=='SPACE_LIKE' and ts['f75v.22']['seam']=='INTERNAL_LIKE'))
 assert r['status']==('SOURCE_AWARE_QUALITATIVE_LOCAL_CONTRAST' if positive else 'NO_CLEAR_LOCAL_CONTRAST')
 assert r['observer_count']==1 and r['independent_confirmation_capacity']==0 and not r['meaning_assigned'] and not r['authorial_word_boundary_confirmed']
 out={'status':'PASS','scope':'Exact original-image identity/dimensions, prior registration, sealed observation, two-target schema and decision reduction only','palaeography_validated':False,'scientific_status':r['status'],'new_images':0}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
