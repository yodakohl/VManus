"""Reproduce source accounting only; handwriting observation remains frozen."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 native=json.loads((B/'artifacts/NATIVE_OBSERVATION.json').read_text());packet=json.loads((B/'artifacts/TEXT_PACKET.json').read_text());targets=[]
 for reader,lines in packet.items():
  for line in lines:
   m=line['metadata'];expected='oeees' if m['locus']=='f102v2.21' else 'aiiin';hits=[g for g in line['groups'] if g[2]==expected];assert len(hits)==1
   g=hits[0];targets.append({'reader':reader,'locus':m['locus'],'group_id':g[0],'raw':g[2],'left_separator':g[3],'right_separator':g[4]})
 result={'status':native['status'],'source_canvas':'1006252','native_observation_sha256':hashlib.sha256((B/'artifacts/NATIVE_OBSERVATION.json').read_bytes()).hexdigest(),'targets':targets,'source_lines':6,'image_views':{'overview':1,'fixed_crops':2},'manual_judgment_recomputed':False,'claim_ceiling':native['claim_ceiling']}
 (B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'source_lines':6,'targets':len(targets),'manual_judgment_recomputed':False}))
if __name__=='__main__':main()
