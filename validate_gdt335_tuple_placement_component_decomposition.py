#!/usr/bin/env python3
"""Validate GDT335 additive decomposition and hashes."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'gdt335_result.json';OUT=R/'gdt335_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 v=json.loads(P.read_text());s=v.pop('content_sha256');rows=read('gdt335_component_gains.tsv');allrows={x['component']:float(x['held_gain_bits']) for x in rows if x['scope']=='ALL'};reg={r:{x['component']:float(x['held_gain_bits']) for x in rows if x['scope']==r} for r in ('HERBAL_A','HERBAL_B','OTHER_A','OTHER_B','STARS_RECIPE_B')};checks={'content':s==can(v),'rows':len(rows)==24,'events':v['events']==6626 and all(int(x['scored_events'])==6626 for x in rows if x['scope']=='ALL'),'components':set(allrows)=={'LINE_FIRST','WITHIN_FIELD_POSITION','FIELD_ORDINAL','LINE_QUARTILE'},'component_result':all(abs(allrows[k]-v['component_gains'][k])<1e-9 for k in allrows),'register_additivity':all(abs(sum(reg[r][k] for r in reg)-allrows[k])<1e-8 for k in allrows),'total':abs(sum(allrows.values())-696.524737419407)<1e-8,'field_negative':all(reg[r]['FIELD_ORDINAL']<0 for r in reg),'line_first_positive':all(reg[r]['LINE_FIRST']>0 for r in reg),'inputs':all(v['inputs'][n]==sha(R/n) for n in v['inputs']),'docs':all(v['documents'][n]==sha(R/n) for n in v['documents']),'impl':all(v['implementation'][n]==sha(R/n) for n in v['implementation']),'outputs':all(v['outputs'][n]==sha(R/n) for n in v['outputs']),'f84':v['f84']['input_rows']==0 and not any(x for k,x in v['f84'].items() if k!='input_rows')};assert all(checks.values()),checks;q={'schema':'GDT335_VALIDATION_V1','status':'PASS','scope':'RETAINED_COMPONENT_ARITHMETIC_REGISTER_ADDITIVITY_HASHES','checks_passed':len(checks),'result_sha256':sha(P)};q['content_sha256']=can(q);OUT.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
