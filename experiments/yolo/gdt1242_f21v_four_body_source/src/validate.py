"""Source/chronology and reduction validation, not visual-truth validation."""
import csv,hashlib,json,subprocess,io
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 lock=read(A/'REGISTRATION_LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 meta=read(A/'CANVAS_METADATA.json');assert meta['label']=='21v' and meta['canvas_id'].endswith('/1006115')
 assert (meta['width'],meta['height'])==(2849,3769)
 source=read(A/'SOURCE_IMAGE.json');assert source['url']==meta['image_body']['id'];assert sha(ROOT/source['path'])==source['sha256']
 assert source['acquired_utc']>lock['frozen_utc']
 op=A/'OBSERVATION.json';o=read(op);seal=read(A/'OBSERVATION_SEAL.json');assert sha(op)==seal['sha256']
 assert seal['sealed_utc']>source['acquired_utc']
 if o['location']=='LOCATED':
  plan=read(A/'REGION_PLAN.json');reg=read(A/'REGION_IMAGE.json')
  assert plan['registered_utc']>=source['acquired_utc'] and reg['acquired_utc']>=plan['registered_utc']
  assert seal['sealed_utc']>=reg['acquired_utc'];assert sha(ROOT/reg['path'])==reg['sha256']
  x,y,w,h=plan['rectangle'];assert min(x,y)>=0 and min(w,h)>0 and x+w<=2849 and y+h<=3769
  assert reg['url']==f'https://collections.library.yale.edu/iiif/2/1006115/{x},{y},{w},{h}/full/0/default.jpg'
 cmd=['./vmanus-exp','query-tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv','--selector','locus','--allow','f21v.2','--allow','f21v.3','--allow','f21v.4','--columns','source_group_id,edition,locus,page,source_group_index,left_separator,right_separator,ivtff_group_raw']
 q=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
 assert q.stdout==(A/'TARGET_ROWS.tsv').read_text()
 rows=list(csv.DictReader(io.StringIO(q.stdout),delimiter='\t'));assert len(rows)==75
 for reader in ('IT2a','RF1b','ZL3b'):
  line=sorted([r for r in rows if r['edition']==reader and r['locus']=='f21v.3'],key=lambda r:int(r['source_group_index']))
  assert [r['ivtff_group_raw'] for r in line]==['qotol','keeees','chotchy','tcho','choty','chor','qotol','daiin','dal']
  assert line[1]['left_separator']==line[1]['right_separator']=='DEFINITE_SPACE'
 assert o['location'] in ('LOCATED','UNLOCATED')
 assert o['body_count'] is None or isinstance(o['body_count'],int)
 assert o['repeated_shape'] in ('COMPATIBLE','DIFFERENT','UNRESOLVED')
 assert o['outer_shapes'] in ('COMPATIBLE','CONTRADICTED','UNRESOLVED')
 assert o['external_clearances'] in ('SPACE_LIKE','CONTRADICTED','UNRESOLVED')
 if o['location']=='UNLOCATED':expected='UNLOCATED'
 elif o['repeated_shape']=='DIFFERENT' or o['outer_shapes']=='CONTRADICTED' or o['external_clearances']=='CONTRADICTED' or (o['body_count'] is not None and o['body_count']!=4):expected='VISUAL_COUNTEREVIDENCE'
 elif o['body_count']==4 and o['repeated_shape']=='COMPATIBLE' and o['outer_shapes']=='COMPATIBLE' and o['external_clearances']=='SPACE_LIKE':expected='SOURCE_AWARE_FOUR_BODY_COMPATIBILITY'
 else:expected='UNRESOLVED'
 result=read(A/'RESULT.json');assert result['status']==expected and result['body_count']==o['body_count'] and result['observation_sha256']==seal['sha256']
 out={'status':'PASS','completed_utc':datetime.now(timezone.utc).isoformat(),'source_rows_rechecked':75,'scope':'Source bytes, scope, chronology and reduction only; no validation of manual visual truth'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
