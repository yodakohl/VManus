#!/usr/bin/env python3
"""Validate GDT331 by checking sources, scores, null bytes, and hashes."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'gdt331_result.json';OUT=R/'gdt331_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 v=json.loads(P.read_text());s=v.pop('content_sha256');checks={'content':s==can(v),'source':len(read('gdt327_joint_tuple_interlinear.tsv'))==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in read('gdt327_joint_tuple_interlinear.tsv')),'candidates':len(read('gdt331_formula_context_scores.tsv'))==44,'null':len(read('gdt331_null.tsv'))==8193,'lead_rank':read('gdt331_formula_context_scores.tsv')[0]['formula_id']==v['lead']['formula_id'],'triple':v['three_host_formula']['formula_id']=='GDT328_9CBFB2F759E75414','status':v['status']=='NO_RECURRENT_FORMULA_HAS_SEARCH_STABLE_EXTERNAL_TEMPLATE','inputs':all(v['inputs'][n]==sha(R/n) for n in v['inputs']),'docs':all(v['documents'][n]==sha(R/n) for n in v['documents']),'impl':all(v['implementation'][n]==sha(R/n) for n in v['implementation']),'outputs':all(v['outputs'][n]==sha(R/n) for n in v['outputs']),'f84':v['f84']['input_rows']==0 and not any(x for k,x in v['f84'].items() if k!='input_rows')};assert all(checks.values()),checks;q={'schema':'GDT331_VALIDATION_V1','status':'PASS','scope':'SOURCE_COUNTS_OUTPUT_INTEGRITY_RETAINED_SCORE_AND_NULL_HASHES','checks_passed':len(checks),'result_sha256':sha(P),'note':'Numerical permutation replay is deterministic in the producer; this validator is integrity-oriented.'};q['content_sha256']=can(q);OUT.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
