"""Post-result novelty accounting, not a pre-registered scientific test."""
from pathlib import Path
import json,gzip,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
    source=Path('experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');prior=Path('experiments/yolo/gdt1235_ud_short_word_capacity/artifacts/RESULT.json');bridge=Path('experiments/yolo/gdt1267_general_ud_two_sided_closure/REPORT.md')
    old=json.loads((R/prior).read_text());data=json.loads(gzip.decompress((R/source).read_bytes()));new=json.loads((B/'artifacts/RESULT.json').read_text())['panels'];out={'scope':'Post-result novelty accounting only, not another hypothesis test. Prior union includes1267K/E/S, not merely1235short-code set. FULLpremises only, not applied toGE2.','source_hashes':{str(p):hashlib.sha256((R/p).read_bytes()).hexdigest() for p in [source,prior,bridge]},'readers':{}}
    for reader,rows in data.items():
        before=set(old['readers'][reader]['summary']['forced_singletons_from_short_code_condition'])|set('kes');after=set(new[reader+'_FULL']['forced_singletons']);assert before<=after
        oldfixed=sum(set(r['units'])<=before for r in rows);newfixed=sum(set(r['units'])<=after for r in rows);changed=[r for r in rows if set(r['units'])<=after and not set(r['units'])<=before]
        out['readers'][reader]={'prior_forced':sorted(before),'new_additions':sorted(after-before),'prior_fully_forced_groups':oldfixed,'current_fully_forced_groups':newfixed,'additional_fully_forced_groups':newfixed-oldfixed,'additional_fixed_types':len({tuple(r['units']) for r in changed})}
    (B/'artifacts/PRIOR_COMPARISON.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['readers']))
if __name__=='__main__':main()
