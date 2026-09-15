"""Acquire fixed existing images or compare sealed native observation records."""
from pathlib import Path
import argparse, hashlib, json, urllib.request
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
def locks():
 for name,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items(): assert sha(R/name)==h,name

def compare(a,b):
 rows=[]
 for ar,br in zip(a['images'],b['images']):
  assert ar['canvas_id']==br['canvas_id']
  same_count=len(ar['units'])==len(br['units'])
  for i in range(max(len(ar['units']),len(br['units']))):
   au=ar['units'][i] if i<len(ar['units']) else None
   bu=br['units'][i] if i<len(br['units']) else None
   joint=au['status'] if same_count and au and bu and au['status']==bu['status'] else 'UNRESOLVED'
   rows.append({'canvas_id':ar['canvas_id'],'unit_index':i+1,'joint':joint,'A':au,'B':bu,'same_unit_count':same_count})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--acquire',action='store_true');ap.add_argument('--compare',action='store_true');a=ap.parse_args();locks()
 spec=json.loads((E/'src/SOURCES.json').read_text())
 if a.acquire:
  for x in spec['images']:
   p=R/x['runtime'];p.parent.mkdir(parents=True,exist_ok=True)
   if not p.exists():
    req=urllib.request.Request(x['image_url'],headers={'User-Agent':'VManus research source retrieval'})
    with urllib.request.urlopen(req,timeout=90) as f:p.write_bytes(f.read())
   assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['canvas_id']
  print('SIX_FIXED_IMAGES_BOUND; acquisition does not constitute native viewing')
 if a.compare:
  aa=json.loads((E/'artifacts/A_OBSERVATION.json').read_text());bb=json.loads((E/'artifacts/B_OBSERVATION.json').read_text());rows=compare(aa,bb)
  assert rows
  states=[r['joint'] for r in rows]
  status='CANDIDATE_FRAMEWORK_ONLY' if 'MATCH' in states else 'UNRESOLVED_FRAMEWORK_CAPACITY' if 'UNRESOLVED' in states else 'ALL_REPRESENTATIVE_FRAMEWORKS_CONTRADICTED'
  result={'status':status,'joint_units':rows,'counts':{s:states.count(s) for s in ['MATCH','CONTRADICTED','UNRESOLVED']},'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'claim_ceiling':'Necessary topological framework only; no metric construction, text ownership, decoder, language or word meaning.'}
  write(E/'artifacts/RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='joint_units'},indent=2))
 if not a.acquire and not a.compare: print('BOUND_REGISTRATION; supply --acquire or --compare')
if __name__=='__main__': main()
