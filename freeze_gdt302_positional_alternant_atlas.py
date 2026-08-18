#!/usr/bin/env python3
"""Freeze score-blind capacities for GDT302 atlas."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'gdt278_native_event_inventory.tsv';M=R/'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_METHOD.md';C=R/'gdt302_capacity.tsv';D=R/'gdt302_design.json';F=R/'gdt302_freeze_manifest.tsv';ART=['gdt301_result.json','gdt300_result.json','gdt299_result.json','gdt297_result.json','gdt278_native_event_inventory.tsv','gdt276_event_inventory.tsv']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=[x for x in read(S) if x['control_id']=='VOYNICH_REFERENCE' and int(x['group_count'])>=2];assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);hf=defaultdict(set);sf=defaultdict(set)
 for x in rows:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 E=[x for x in rows if len(hf[x['page_host']])>=2 and len(sf[x['source_surface_sha256']])>=2];hc=Counter(x['page_host'] for x in E);fc=Counter((x['page_host'],x['source_surface_sha256']) for x in E);ff=defaultdict(set)
 for x in E:ff[(x['page_host'],x['source_surface_sha256'])].add(x['physical_folio'])
 ok={(h,s) for (h,s),n in fc.items() if n>=8 and len(ff[(h,s)])>=4 and hc[h]>=20};by=Counter(h for h,s in ok);ok={q for q in ok if by[q[0]]>=2};cap=[{'metric':'gdt299_events','value':len(E)},{'metric':'eligible_hosts','value':len({h for h,s in ok})},{'metric':'eligible_forms','value':len(ok)},{'metric':'eligible_form_events','value':sum(fc[q] for q in ok)},{'metric':'raw_join_rows','value':len(read(R/'gdt276_event_inventory.tsv'))}];write(C,cap);write(F,[{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART]);d={'schema':'GDT302_HOST_POSITIONAL_ALTERNANT_ATLAS_DESIGN_V1','status':'FROZEN_BEFORE_GDT302_ROLE_SCORING','population':'EXACT_GDT299_6844_EVENTS','form_min_events':8,'form_min_folios':4,'host_min_events':20,'host_min_scored_forms':2,'role_ratio_threshold':1.5,'stratum_min_form_events':2,'stratum_min_other_host_events':2,'stable_min_powered_strata':2,'models':'EXACT_GDT299_LOFO_HOST_AND_WHOLE_FORM','classification':{'stable':'POSITIVE_LOFO_GAIN_RATIO_GE1.5_ALL_POWERED_STRATA_SAME_SIGN_MIN2','provisional':'POSITIVE_GAIN_RATIO_GE1.25','weak':'POSITIVE_GAIN_OTHER','counterexample':'NONPOSITIVE_GAIN'},'source_strings_displayed_after_exact_join':True,'substrings_mined':0,'semantic_assignments':0,'claim_ceiling':'Whole-form physical positional alternants and normalization candidates only; no grammatical semantic role meaning sound language plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(C),'freeze_manifest_sha256':sha(F),'method_sha256':sha(M),'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=can(d);D.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'capacity':cap},sort_keys=True))
if __name__=='__main__':main()
