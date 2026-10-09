import csv,hashlib,json
from pathlib import Path
from datetime import datetime
from PIL import Image
B=Path(__file__).resolve().parents[1];A=B/'artifacts';ROOT=B.parents[2]
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text());meta=json.loads((A/'CANVAS_METADATA.json').read_text())['canvas'];assert meta['label']=={'none':['76v']}
 assert meta['id'].endswith('/1006211') and (meta['width'],meta['height'])==(2823,3712)
 for p,h in lock['files'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 assert hashlib.sha256((ROOT/lock['scope_file']).read_bytes()).hexdigest()==lock['scope_sha256']
 rec=[json.loads((A/(x+'.json')).read_text()) for x in ['IMAGE_RECEIPT','REGION_RECEIPT']]
 for x in rec:
  p=ROOT/x['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'];assert Image.open(p).size==(x['width'],x['height'])
 selection=json.loads((A/'REGION_SELECTION.json').read_text());box=selection['rectangle_xywh'];assert box==[760,2070,1910,160]
 assert box[0]+box[2]<=2823 and box[1]+box[3]<=3712
 assert '/760,2070,1910,160/full/' in rec[1]['url']
 obs=json.loads((A/'OBSERVATION.json').read_text());result=json.loads((A/'RESULT.json').read_text())
 assert datetime.fromisoformat(lock['locked_utc'])<datetime.fromisoformat(rec[0]['acquired_utc'])<datetime.fromisoformat(selection['selected_utc'])<datetime.fromisoformat(rec[1]['acquired_utc'])<datetime.fromisoformat(obs['recorded_utc'])
 assert obs['status']==result['status']=='UNRESOLVED_REGION_MISLOCALIZED'
 assert all(obs[k]=='UNRESOLVED' for k in ['left_exterior','internal_seam','right_exterior'])
 rows=list(csv.DictReader((A/'SOURCE_LINES.tsv').open(),delimiter='\t'));assert len(rows)==result['source_rows']==93
 for ed in ['ZL3b','IT2a','RF1b']:
  r=sorted([x for x in rows if x['edition']==ed and x['locus']=='f76v.28'],key=lambda x:int(x['source_group_index']))
  w=[x['ivtff_group_raw'] for x in r]
  if ed=='IT2a':assert w[2:4]==['cheol','chey'] and r[2]['right_separator']==r[3]['left_separator']=='DEFINITE_SPACE'
  else:assert w[2]=='cheolchey'
 out={'status':'PASS','scope':'Provenance, chronology, transcript accounting and faithfully retained unresolved decision only. Does not verify visual localization or erase the disclosed region-scope deviation.'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
