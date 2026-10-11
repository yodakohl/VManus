from pathlib import Path
import hashlib,itertools,json
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
r=json.loads((P/'SINGLE_ACCENT_CAPACITY_REVIEW_20261011.json').read_text())
for p,h in r['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
source=json.loads((R/'experiments/yolo/gdt1296_categorical_harmony_capacity/artifacts/RESULT.json').read_text())
total=len(list(itertools.combinations(range(22),2)));required=len(list(itertools.combinations(range(11),2)));assert total==231 and required==55
for ed,v in source['readers'].items():
 absent=total-v['cooccurrence_edges'];assert r['readers'][ed]=={'old_groups':v['groups'],'old_cooccurring_pairs':v['cooccurrence_edges'],'absent_pairs':absent,'required_absent_pairs':required,'compatible':False};assert absent<required
 assert max(k for k in range(23) if len(list(itertools.combinations(range(k),2)))<=absent)==5
print(json.dumps({'status':'PASS','old_aggregate_readers':3,'new_native_counts':0,'required_absent_pairs':required,'scope':'Input hashes and cardinality corollary only; does not recompute old graph or establish physical units.'}))
