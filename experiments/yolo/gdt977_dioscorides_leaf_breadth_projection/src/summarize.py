"""Group all registered cases by unchanged name-code class; no new target search."""
import collections,csv,gzip,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
with gzip.open(R/'experiments/yolo/gdt976_dioscorides_shared_referent_projection/artifacts/CANDIDATES.json.gz','rt') as f:cs=json.load(f)
with gzip.open(E/'artifacts/CASES.json.gz','rt') as f:rs=json.load(f)
assert [r['id'] for r in rs]==list(range(len(cs)))
groups=collections.defaultdict(collections.Counter)
for c,r in zip(cs,rs):groups[c['edition'],c['iris_code'],c['xiphion_code']][r['status']]+=1
with (E/'artifacts/NAME_CLASS_RESULTS.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition','iris_code','xiphion_code','old_rows','witness_rows','contradicted_rows','unknown_rows'])
 for key,z in sorted(groups.items()):w.writerow([*key,sum(z.values()),z['PARTIAL_FOUR_ATOM_WITNESS'],z['FOUR_ATOM_PROJECTION_CONTRADICTED'],sum(n for k,n in z.items() if k.startswith('UNKNOWN'))])
assert len(groups)==1320 and sum(sum(z.values()) for z in groups.values())==8990
print('Grouped',len(groups),'name-code classes; no new fit')
