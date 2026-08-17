#!/usr/bin/env python3
import csv,hashlib,itertools,json
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):
 with(R/n).open(encoding='utf8',newline='')as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 x=json.loads((R/'gdt198_result.json').read_text());links=read('gdt198_f77_payload_links.tsv');null=read('gdt198_assignment_null.tsv');counter=read('gdt198_counterexamples.tsv');checks=[];add=lambda n,v:checks.append((n,bool(v)))
 add('status',x['status']=='LOCAL_PAYLOAD_REUSE_LEAD_NOT_ABOVE_ROLE_ASSIGNMENT_NULL');add('counts',x['stable_labels']==9 and x['tube_labels']==6 and x['figure_labels_primary']==3);add('links',len(links)==4);add('matched_pairs',[(r['figure_locus'],r['matching_tube_loci'])for r in links if r['cross_class_payload_match']=='1']==[('f77r.8','f77r.3'),('f77r.49','f77r.6')]);add('no_full_tuple',all(r['full_tuple_match']!='1'for r in links));add('reading_sensitive',links[-1]['figure_locus']=='f77r.50'and links[-1]['cross_class_payload_match']=='NOT_SCORED');add('null',len(null)==1 and int(null[0]['worlds'])==84 and int(null[0]['worlds_at_least_observed'])==20 and abs(float(null[0]['inclusive_p'])-20/84)<1e-12);add('result_null',x['cross_class_payload_matches']==2 and x['worlds_at_least_observed']==20 and abs(x['inclusive_p']-20/84)<1e-12);add('counter',len(counter)==5);add('no_f84',not any('f84' in r['figure_locus'] or 'f84' in r['matching_tube_loci']for r in links));add('flags',all(v is False for v in x['f84r'].values()))
 for group in('inputs','implementation','outputs','documents'):
  for n,d in x[group].items():add('hash:'+group+':'+n,sha(n)==d)
 raw=dict(x);d=raw.pop('result_content_sha256');add('content_hash',csha(raw)==d)
 out={'schema':'GDT198_VALIDATION_V1','status':'PASS'if all(v for _,v in checks)else'FAIL','checks_passed':sum(v for _,v in checks),'checks_total':len(checks),'failed':[n for n,v in checks if not v],'result_sha256':sha('gdt198_result.json'),'scope':'Independent retained-link, exact-null, provenance, and hash validation; semantic interpretation remains exposed and unconfirmed.'};(R/'gdt198_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
 if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
