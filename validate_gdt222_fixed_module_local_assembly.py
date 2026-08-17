#!/usr/bin/env python3
"""Independent integrity/arithmetic validator for GDT222."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent; RES=R/'gdt222_result.json'; OUT=R/'gdt222_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content_hash',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='FIXED_MODULE_LOCAL_ASSEMBLY_LEAD_COVERAGE_UNSTABLE_NO_TRANSFER_TARGET')
ck('module_list',r['modules']==['ar','ol','dal','dar','sy','te','tee','dy'])
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('document_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('implementation_'+n,sha(R/n)==h)
inv=read(R/'gdt222_assembly_module_inventory.tsv');ck('inventory_rows',len(inv)==16)
ck('inventory_pages',set(x['page'] for x in inv)=={'f75v','f83r'})
ck('no_f84_inventory',not any(x['page'].startswith('f84') for x in inv))
scores=read(R/'gdt222_assignment_scores.tsv');ck('score_rows',len(scores)==4)
primary={x['page']:float(x['correct_assignment_lead']) for x in scores if x['scope']=='ALL_AVAILABLE_PRIMARY'}
ck('page_leads',all(abs(primary[p]-r['primary']['page_leads'][p])<1e-10 for p in primary))
ck('aggregate',abs(sum(primary.values())-r['primary']['aggregate_lead'])<1e-10)
ck('positive_two',sum(x>0 for x in primary.values())==2)
ck('four_world_p',r['primary']['exact_worlds']==4 and abs(r['primary']['exact_assignment_p']-.25)<1e-15)
corr=read(R/'gdt222_module_correspondence.tsv');ck('correspondence_rows',len(corr)==32)
ar=[x for x in corr if x['module']=='ar' and x['scope']=='ALL_AVAILABLE_PRIMARY'];ck('ar_two_pages',len(ar)==2 and all(int(x['discriminating_pattern_match']) for x in ar))
ck('ar_orientation_reversal',{x['orientation'] for x in ar}=={'TOP','BOTTOM'})
ck('only_ar_two_page',sum(1 for m in r['modules'] if sum(int(x['discriminating_pattern_match']) for x in corr if x['scope']=='ALL_AVAILABLE_PRIMARY' and x['module']==m)==2)==1)
ck('complete_ar_zero_pages',r['complete_line_sensitivity']['ar_supported_pages']==0)
ck('complete_f83_reverses',r['complete_line_sensitivity']['page_leads']['f83r']<0 and r['complete_line_sensitivity']['aggregate_lead']<0)
lomo=read(R/'gdt222_leave_one_module_out.tsv');ck('lomo_rows',len(lomo)==16)
ck('ar_removal_flips_f83',float(next(x['correct_assignment_lead'] for x in lomo if x['excluded_module']=='ar' and x['page']=='f83r'))<0)
ck('missing_exact',r['missing_label_loci']==['f75v.22','f75v.23','f83r.50'])
ck('claim_ceiling',all(k not in r['interpretation'].lower() for k in ('translation','plaintext')))
ck('f84_flags',not any(r['f84'].values()))
v={'schema':'GDT222_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")
