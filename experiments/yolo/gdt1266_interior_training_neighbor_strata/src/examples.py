import json,gzip
from pathlib import Path
p=Path(__file__).resolve().parents[1]
rows=json.loads(gzip.decompress((p/'artifacts/CLASSIFIED_PAIRS.json.gz').read_bytes()))
out=[]
for cat in ['BOTH_NEAR','MIXED','BOTH_FAR']:
 r=next(r for r in rows if r['reader']=='ZL3b' and r['category']==cat)
 out.append({k:r[k] for k in ['reader','category','left','right','train_neighbors','observed','expected','informative']})
(p/'artifacts/POSTRESULT_EXAMPLES.json').write_text(json.dumps({'selection':'first saved ZL pair in each category, post-result illustrative only','examples':out},indent=2)+'\n')
