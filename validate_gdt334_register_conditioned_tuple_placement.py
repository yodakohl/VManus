#!/usr/bin/env python3
"""Validate GDT334 retained fold arithmetic and provenance."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'gdt334_result.json';OUT=R/'gdt334_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    v=json.loads(P.read_text());s=v.pop('content_sha256');f=read('gdt334_folds.tsv');r=read('gdt334_register_scores.tsv');src=read('gdt327_joint_tuple_interlinear.tsv');z=v['summary'];checks={'content':s==can(v),'source':len(src)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in src),'folds':len(f)==z['folds']==92,'registers':len(r)==5,'events':sum(int(x['scored_events']) for x in f)==z['scored_events'],'components':sum(int(x['component_predictions']) for x in f)==z['component_predictions']==4*z['scored_events'],'gain':abs(sum(float(x['tuple_gain']) for x in f)-z['tuple_gain'])<1e-8,'bits':abs(sum(float(x['coordinate_bits']) for x in f)-z['coordinate_bits'])<1e-8 and abs(sum(float(x['tuple_shrunk_bits']) for x in f)-z['tuple_shrunk_bits'])<1e-8,'positive_folds':sum(int(x['positive_gain']) for x in f)==z['positive_folds'],'positive_regs':sum(float(x['tuple_gain'])>0 for x in r)==z['positive_registers'],'alphas':all(int(x['selected_alpha']) in {2,4,8,16,32,64} for x in f),'inputs':all(v['inputs'][n]==sha(R/n) for n in v['inputs']),'docs':all(v['documents'][n]==sha(R/n) for n in v['documents']),'impl':all(v['implementation'][n]==sha(R/n) for n in v['implementation']),'outputs':all(v['outputs'][n]==sha(R/n) for n in v['outputs']),'f84':v['f84']['input_rows']==0 and not any(x for k,x in v['f84'].items() if k!='input_rows')};assert all(checks.values()),checks;q={'schema':'GDT334_VALIDATION_V1','status':'PASS','scope':'RETAINED_NESTED_FOLD_ARITHMETIC_ALPHA_DOMAIN_HASHES','checks_passed':len(checks),'result_sha256':sha(P),'note':'Integrity and arithmetic validation; nested model refit is not independently replayed.'};q['content_sha256']=can(q);OUT.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
