"""Reproduce a carrier bound against an unchanged published inventory only."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2]
x=json.loads((B/'AGREEMENT_CARRIER_HEAD_ASSESSMENT_20261010.json').read_text())
for field in ['raw_contract','source_artifact']:
 s=x[field];assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
def head(c):return 'L'+str(ord(c)-ord('a')) if 'a'<=c<='u' else 'E'
starts={head(c) for c in ['"','a','n','l','c','w']};assert starts=={'E','L0','L13','L11','L2'}
old=json.loads((R/x['source_artifact']['path']).read_text());counts={ed:len({v for v in r['active_nodes'] if v.startswith('I:')}) for ed,r in old['readers'].items()};assert counts=={'ZL3b':20,'IT2a':21,'RF1b':21};assert all(n>len(starts) for n in counts.values())
r={'status':'PASS_CONDITIONAL_CARRIER_CONTRADICTION','possible_initial_drawings':sorted(starts),'old_published_initial_counts':counts,'source_joins_repeated':0,'scope':'Checks finite carrier head enumeration and old artifact integrity/counts only. Exhaustiveness follows the grammar proof, not a new native census or semantic test.'}
(B/'AGREEMENT_CARRIER_HEAD_VALIDATION_20261010.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
