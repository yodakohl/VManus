#!/usr/bin/env python3
"""Independent validation of the pre-control GDT278 magnitude freeze."""
import csv,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def rows(p):
 with (R/p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
d=json.loads((R/'gdt278_magnitude_design.json').read_text());fm=rows('gdt278_gdt277_freeze_manifest.tsv');rr=rows('gdt278_reference_magnitude.tsv')
ck('frozen_before_controls',d['status']=='FROZEN_BEFORE_EXPANDED_CONTROL_ADMISSION_OR_SCORING')
ck('gdt277_byte_frozen',len(fm)==21 and all(sha(x['artifact'])==x['frozen_sha256'] for x in fm))
ck('two_reference_views',len(rr)==2 and {x['view'] for x in rr}=={'LENGTH_MATCHED_OVERLAY','NATIVE_ORDER'})
for x in rr:
 ck('reference_arithmetic_'+x['view'],math.isclose(float(x['saving_bits'])/int(x['events']),float(x['saving_bits_per_event']),rel_tol=0,abs_tol=1e-12) and math.isclose(float(x['saving_bits'])/float(x['null_sd_bits']),float(x['null_z']),rel_tol=0,abs_tol=1e-12))
ck('matched_reference_exact',next(x for x in rr if x['view']=='LENGTH_MATCHED_OVERLAY')['saving_bits']=='1607.821831893495983')
ck('native_reference_exact',next(x for x in rr if x['view']=='NATIVE_ORDER')['saving_bits']=='3080.522234827526972')
ck('endpoint_exact',d['endpoint']['primary_coordinate']=='SAVING_BITS_PER_EVENT' and d['endpoint']['mandatory_companion']=='NULL_Z' and d['endpoint']['null_worlds']==64)
ck('no_tolerance_or_composite',d['comparison_rule']['tolerance_band']=='NONE' and d['comparison_rule']['composite_score']=='NONE')
ck('lofo_required','MANDATORY' in d['representation']['lofo_safe'])
ck('prohibitions',{'HPR1_SEMANTICS','VOYNICH_SUBSTRING_MINING','MEANING','PLAINTEXT','TRANSLATION','POSTHOC_THRESHOLD'}==set(d['prohibitions']))
ck('f84_false',not any(d['f84'].values()))
q=dict(d);h=q.pop('content_sha256');ck('content_hash',hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()==h)
out={'schema':'GDT278_MAGNITUDE_ENDPOINT_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'design_sha256':sha('gdt278_magnitude_design.json'),'freeze_manifest_sha256':sha('gdt278_gdt277_freeze_manifest.tsv'),'reference_sha256':sha('gdt278_reference_magnitude.tsv')};out['content_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt278_magnitude_design_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
