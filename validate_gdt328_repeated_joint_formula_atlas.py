#!/usr/bin/env python3
"""Independently validate GDT328 without importing the producer."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt328_result.json';OUT=R/'gdt328_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def check(n,c):
  if not c:raise AssertionError(n)
  checks.append(n)
 res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');check('result_content',stored==can(res))
 rows=read('gdt327_joint_tuple_interlinear.tsv');check('source_rows',len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows))
 fields=defaultdict(list)
 for x in rows:fields[(x['page'],x['locus'],x['field_ordinal'])].append(x)
 for v in fields.values():v.sort(key=lambda x:int(x['group_index']))
 check('field_counts',len(fields)==2400 and sum(len(v)>=2 for v in fields.values())==1713)
 rebuilt={}
 for level,key in [('EXACT_JOINT_SEQUENCE','joint_tuple_id'),('PAGE_HOST_SEQUENCE','host_id')]:
  d=defaultdict(list)
  for fk,v in fields.items():
   if len(v)>=2:d[tuple(x[key] for x in v)].append((fk,v))
  for seq,z in d.items():
   if len({v[0]['physical_folio'] for _,v in z})>=2:rebuilt[(level,seq)]=z
 atlas=read('gdt328_formula_atlas.tsv');occ=read('gdt328_formula_occurrences.tsv')
 check('type_counts',len(atlas)==44 and Counter(x['level'] for x in atlas)=={'PAGE_HOST_SEQUENCE':29,'EXACT_JOINT_SEQUENCE':15})
 check('atlas_rebuild',len(rebuilt)==len(atlas))
 for i,a in enumerate(atlas):
  seq=tuple(a['formula_sequence_ids'].split('|'));z=rebuilt[(a['level'],seq)];ords=Counter(k[2] for k,_ in z);mode,mc=sorted(ords.items(),key=lambda q:(-q[1],int(q[0])))[0]
  check(f'atlas_{i}',int(a['occurrences'])==len(z) and int(a['physical_folios'])==len({v[0]['physical_folio'] for _,v in z}) and int(a['group_length'])==len(seq) and a['modal_field_ordinal']==mode and int(a['modal_field_count'])==mc and abs(float(a['modal_field_purity'])-mc/len(z))<1e-11)
 check('occ_count',len(occ)==res['summary']['formula_occurrences'])
 triple=[a for a in atlas if a['level']=='PAGE_HOST_SEQUENCE' and a['group_length']=='3'];check('unique_triple',len(triple)==1 and triple[0]['occurrences']=='3' and triple[0]['physical_folios']=='3' and triple[0]['modal_field_ordinal']=='3' and triple[0]['modal_field_purity']=='1.000000000000')
 to=[x for x in occ if x['formula_id']==triple[0]['formula_id']];check('triple_loci',{x['locus'] for x in to}=={'f82r.2','f83r.6','f107v.35'} and all(x['field_ordinal']=='3' for x in to));check('triple_displays',{x['surface_formula_display'] for x in to}=={'qokain|dy|qokeedy','qokaiin|chedy|qokeedy'})
 by=defaultdict(Counter)
 for v in fields.values():
  if len(v)==3:by[v[0]['register']][v[0]['field_ordinal']]+=1
 p=math.prod(by[x['register']]['3']/sum(by[x['register']].values()) for x in to);common=set.intersection(*[set(by[x['register']]) for x in to]);pa=sum(math.prod(by[x['register']][o]/sum(by[x['register']].values()) for x in to) for o in common)
 check('positional_probability',abs(p-res['summary']['three_host_observed_ordinal_probability_register_length_conditioned'])<1e-15 and abs(pa-res['summary']['three_host_any_common_ordinal_probability_register_length_conditioned'])<1e-15)
 check('inputs',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));check('docs',all(res['documents'][n]==sha(R/n) for n in res['documents']));check('impl',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));check('outputs',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));check('f84',res['f84']['input_rows']==0 and not any(v for k,v in res['f84'].items() if k!='input_rows'))
 v={'schema':'GDT328_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_FIELD_REBUILD_ALL_FORMULAS_ALL_ATLAS_ROWS_LEADING_OCCURRENCES_POSITIONAL_DIAGNOSTIC_HASHES','checks_passed':len(checks),'result_sha256':sha(RESULT),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
