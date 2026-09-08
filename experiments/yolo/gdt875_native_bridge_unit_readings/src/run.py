import csv,hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];S=json.loads((B/'src/SPEC.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=R/'experiments/yolo/gdt874_raw_multigroup_record_bridge';receipt=json.loads((R/S['text_source']).read_text());p=source/'runtime/ATLAS.tsv'
 if not p.exists():subprocess.run([sys.executable,str(source/'src/run.py')],check=True,cwd=R)
 assert sha(p)==next(x['projection_sha256']for x in receipt if x['name']=='ATLAS')
 out={}
 for row in csv.DictReader(p.open(),delimiter='\t'):
  if row['locus'] in S['targets']:out.setdefault(row['locus'],{}).setdefault(row['edition'],[]).append({k:row[k]for k in ['source_group_index','source_group_count','ivtff_group_raw','left_separator','right_separator']})
 assert set(out)==set(S['targets']) and all(set(x)=={'ZL3b','IT2a','RF1b'}for x in out.values())
 for editions in out.values():
  for rows in editions.values():rows.sort(key=lambda x:int(x['source_group_index']))
 for im in S['images']:assert sha(R/im['cache_path'])==im['sha256']
 (B/'artifacts/READINGS.json').write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n');print('Four-locus guarded reading packet and two source hashes PASS')
if __name__=='__main__':main()
