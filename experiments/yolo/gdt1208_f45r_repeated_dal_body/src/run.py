"""Reduce sealed observation; no image recognition or lexical inference."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 o=json.loads((A/'OBSERVATION.json').read_text());s=json.loads((A/'OBSERVATION_SEAL.json').read_text())
 assert sha(A/'OBSERVATION.json')==s['observation_sha256']
 answer='UNRESOLVED'
 if o['location']=='UNLOCATED':answer='UNLOCATED'
 elif o['shared_body']=='DIFFERENT' or 'CONTRADICTED' in (o['endings'],o['clearances']):answer='VISUAL_COUNTEREVIDENCE'
 elif (o['shared_body'],o['endings'],o['clearances'])==('COMPATIBLE','DISTINCT_COMPATIBLE','SPACE_LIKE'):answer='SOURCE_AWARE_LOCAL_SHAPE_SUPPORT'
 r={k:o[k] for k in ('location','shared_body','endings','clearances')}
 r.update(status=answer,locus='f45r.10',targets=['daldy','dalor','dal'],observer_count=1,independent_confirmation_capacity=0,native_meanings_assigned=0,morpheme_proven=False,native_unit_segmentation_proven=False)
 (A/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
 (A/'RUN_RECEIPT.json').write_text(json.dumps({'runner_sha256':sha(Path(__file__)),'observation_sha256':sha(A/'OBSERVATION.json')},indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
