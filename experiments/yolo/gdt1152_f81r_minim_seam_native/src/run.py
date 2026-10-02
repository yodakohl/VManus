#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2]
def load(p):return json.loads(p.read_text())
def main():
 src=load(P/'src/SOURCE.json')
 for x in src['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 for s,h in load(P/'src/PREREG_LOCK.json')['hashes'].items():assert hashlib.sha256((P/s).read_bytes()).hexdigest()==h
 assert hashlib.sha256((P/'artifacts/ORIGINAL.jpg').read_bytes()).hexdigest()==src['image']['sha256']
 obs={}
 for who in ('A','B'):
  path=P/f'artifacts/OBSERVER_{who}.json';r=load(path);freeze=load(P/f'artifacts/OBSERVER_{who}_FREEZE.json');assert hashlib.sha256(path.read_bytes()).hexdigest()==freeze['sha256'];assert r['image_sha256']==src['image']['sha256'];r={**r,'location':r['location'].split(':',1)[0],'seams':{k:(v['status'] if isinstance(v,dict) else v) for k,v in r['seams'].items()}};obs[who]=r
  for k in ['motif1_to_motif2','motif2_to_motif3','motif3_to_minims']:assert r['seams'][k] in ('SPACE_LIKE','INTERNAL_LIKE','UNRESOLVED')
 ratings=[v['seams']['motif3_to_minims'] for v in obs.values()]
 if any(v['location']!='LOCATED' for v in obs.values()) or ratings[0]!=ratings[1] or 'UNRESOLVED' in ratings:decision='NATIVE_SEAM_UNRESOLVED'
 elif ratings[0]=='SPACE_LIKE':decision='LOCAL_SEPARATION_SUPPORTED'
 else:decision='LOCAL_JOIN_SUPPORTED'
 r={'experiment':'GDT1152','decision':decision,'observer_seams':{k:v['seams'] for k,v in obs.items()},'source_image_sha256':src['image']['sha256'],'scope':'f81r.5 third repeated motif before minim group, physical spacing only','GDT1151':'UNCHANGED_REFUTED_FIXED_PAIRED_FIELD_SCOPE','confirmed_words':0,'independent_meaning_confirmation_capacity':0,'significance':'NOT_CLAIMED'}
 (P/'artifacts/RESULT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
