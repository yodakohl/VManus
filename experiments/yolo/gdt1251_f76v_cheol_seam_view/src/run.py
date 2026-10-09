import csv,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];A=B/'artifacts';ROOT=B.parents[2]
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 assert hashlib.sha256((ROOT/lock['scope_file']).read_bytes()).hexdigest()==lock['scope_sha256']
 for name in ['IMAGE_RECEIPT','REGION_RECEIPT']:
  r=json.loads((A/(name+'.json')).read_text());assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 obs=json.loads((A/'OBSERVATION.json').read_text());assert obs['status']=='UNRESOLVED_REGION_MISLOCALIZED'
 rows=list(csv.DictReader((A/'SOURCE_LINES.tsv').open(),delimiter='\t'));assert len(rows)==93 and {r['locus'] for r in rows}=={'f76v.27','f76v.28','f76v.29'}
 result={'status':obs['status'],'source_rows':len(rows),'image_views':['full original','one fixed IIIF region'],'scientific_spacing_decision':'UNRESOLVED','scope_deviation':obs['deviation'],'observer_count':1,'independent_confirmation':False}
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
