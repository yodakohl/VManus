#!/usr/bin/env python3
"""Independently reconstruct every GDT332 portability count."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'gdt332_result.json';OUT=R/'gdt332_validation.json';REGS={'HERBAL_A','HERBAL_B','OTHER_A','OTHER_B','STARS_RECIPE_B'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,c):
  if not c:raise AssertionError(n)
  checks.append(n)
 v=json.loads(P.read_text());s=v.pop('content_sha256');ck('content',s==can(v));rows=read('gdt327_joint_tuple_interlinear.tsv');ck('source',len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));d=defaultdict(list)
 for x in rows:d[x['joint_tuple_id']].append(x)
 atlas={x['joint_tuple_id']:x for x in read('gdt332_joint_tuple_portability.tsv')};ck('atlas_types',len(atlas)==len(d)==1676)
 for i,(k,z) in enumerate(sorted(d.items())):
  a=atlas[k];regs={x['register'] for x in z};ck(f'row_{i}',int(a['events'])==len(z) and int(a['physical_folios'])==len({x['physical_folio'] for x in z}) and int(a['cross_folio'])==(len({x['physical_folio'] for x in z})>=2) and int(a['cross_register'])==(len(regs)>=2) and int(a['all_five_registers'])==(regs==REGS) and int(a['register_private'])==(len(regs)==1) and a['semantic_state']==a['translation_state']=='UNASSIGNED')
 j=v['joint_tuple_summary'];ck('summary',j['types']==1676 and j['events']==8448 and j['singleton_types']==1078 and j['cross_folio_types']==586 and j['cross_folio_event_mass']==7343 and j['cross_register_types']==467 and j['cross_register_event_mass']==7001 and j['cross_hand_types']==440 and j['cross_hand_event_mass']==6906 and j['all_five_register_types']==53 and j['all_five_register_event_mass']==3836 and j['register_private_types']==1209 and j['register_private_event_mass']==1447);ck('inputs',all(v['inputs'][n]==sha(R/n) for n in v['inputs']));ck('docs',all(v['documents'][n]==sha(R/n) for n in v['documents']));ck('impl',all(v['implementation'][n]==sha(R/n) for n in v['implementation']));ck('outputs',all(v['outputs'][n]==sha(R/n) for n in v['outputs']));ck('f84',v['f84']['input_rows']==0 and not any(x for k,x in v['f84'].items() if k!='input_rows'))
 q={'schema':'GDT332_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_ALL_TUPLE_ROWS_AND_PORTABILITY_COUNTS_HASHES','checks_passed':len(checks),'result_sha256':sha(P),'f84_rows':0};q['content_sha256']=can(q);OUT.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
