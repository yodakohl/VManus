"""Post-result accounting only, declared after primary outcome; no model changes."""
import gzip,json,statistics
from pathlib import Path
B=Path(__file__).resolve().parents[1]
es=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes()));out={}
for ed in ['ZL3b','IT2a','RF1b']:
 rows=[e for e in es if e['reader']==ed and e['global_unseen']];r={}
 for name,positive in [('H_positive',True),('H_zero',False)]:
  sub=[e for e in rows if (e['h']>0)==positive];r[name]={'occurrences':len(sub),'token_mean_gain_m1':statistics.fmean(e['gain_m1'] for e in sub),'missing_train_cell':sum(e['cell_train_N']==0 for e in sub)}
 out[ed]=r
result={'timing':'Post-result descriptive partition of globally unseen words; not a new gate or renormalized predictor.','readers':out}
(B/'artifacts/POST_RESULT_DESCRIPTION.json').write_text(json.dumps(result,indent=2)+'\n')
