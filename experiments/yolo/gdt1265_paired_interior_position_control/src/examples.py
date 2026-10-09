"""Post-result illustrations only; no new selection gate."""
import gzip,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];pairs=json.loads(gzip.decompress((B/'artifacts/PAIRS.json.gz').read_bytes()));chosen=[]
for polarity in ['positive','negative','fixed']:
 for p in pairs:
  if p['reader']!='ZL3b' or p['cohort']!='UNSEEN_INTERIOR':continue
  delta=p['observed']*p['expected'][1]-p['expected'][0]
  if (polarity=='positive' and p['informative'] and delta>0) or(polarity=='negative' and p['informative'] and delta<0) or(polarity=='fixed' and not p['informative']):chosen.append({'selection':polarity,'pair':p});break
(B/'artifacts/POSTRESULT_EXAMPLES.json').write_text(json.dumps({'status':'POSTRESULT_ILLUSTRATION_NO_NEW_GATE','selection':'First saved ZL UNSEEN_INTERIOR pair per positive/negative/fixed category; not best examples; every original pair remains.','examples':chosen},indent=2)+'\n')
