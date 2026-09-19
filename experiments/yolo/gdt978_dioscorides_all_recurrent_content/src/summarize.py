"""All registered partitions in a human-readable table; no new search."""
import collections,csv,gzip,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def main():
 pred=json.loads((E/'artifacts/PARTITION_PREDICTIONS.json').read_text())
 with gzip.open(E/'artifacts/PARTITION_RESULTS.json.gz','rt') as f:rows=json.load(f)
 assert [r['id'] for r in rows]==[p['id'] for p in pred]
 with (E/'artifacts/PARTITION_RESULTS.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['partition','edition','iris_page','included_base_rows','status','construction_seconds','solver_seconds','witnessed_base_id'])
  for p,r in zip(pred,rows):w.writerow([p['id'],p['edition'],p['iris_page'],len(p['base_ids']),r['status'],r.get('construction_seconds','NA'),r.get('solver_seconds','NA'),r.get('witnessed_base_id','NA')])
 result=json.loads((E/'artifacts/RESULT.json').read_text());assert result['partition_counts']==dict(collections.Counter(r['status'] for r in rows))
 print('All',len(rows),'partitions rendered; statuses',result['partition_counts'])
if __name__=='__main__':main()
