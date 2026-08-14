#!/usr/bin/env python3
"""Source-only capacity audit for a clean ACA apparatus/figure replication page."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=read(S/'existing_human_exact_locus_annotations.tsv');counts=defaultdict(Counter);loci=defaultdict(lambda:defaultdict(list))
for x in rows:
 if x['page']=='f84r' or len(x['normalized_code'])<2 or x['normalized_code'][1]!='L':continue
 tags=set(x['object_tags'].split(';'));a='WATER_OR_APPARATUS' in tags;f='FIGURE' in tags
 state='APPARATUS_EXCLUSIVE' if a and not f else 'FIGURE_EXCLUSIVE' if f and not a else 'MIXED' if a and f else ''
 if not state:continue
 key=f'{state}_{x["certainty"]}';counts[x['page']][key]+=1;loci[x['page']][key].append(x['locus'])
out=[]
for page in sorted(counts):
 c=counts[page];physical=page.split('r')[0].split('v')[0];used=physical in {'f77','f82'}
 eligible=not used and c['APPARATUS_EXCLUSIVE_UNHEDGED']>=2 and c['FIGURE_EXCLUSIVE_UNHEDGED']>=2
 audit_state='CLEAN_INDEPENDENT_ELIGIBLE' if eligible else 'ALREADY_USED_PHYSICAL_FOLIO' if used else 'NOT_CLEAN_INDEPENDENT_ELIGIBLE'
 out.append({'page':page,'physical_folio':physical,'already_used_folio':int(used),'apparatus_unhedged':c['APPARATUS_EXCLUSIVE_UNHEDGED'],'apparatus_hedged':c['APPARATUS_EXCLUSIVE_HEDGED'],'figure_unhedged':c['FIGURE_EXCLUSIVE_UNHEDGED'],'figure_hedged':c['FIGURE_EXCLUSIVE_HEDGED'],'mixed_unhedged':c['MIXED_UNHEDGED'],'mixed_hedged':c['MIXED_HEDGED'],'clean_independent_eligible':int(eligible),'apparatus_loci':';'.join(loci[page]['APPARATUS_EXCLUSIVE_UNHEDGED']),'figure_loci':';'.join(loci[page]['FIGURE_EXCLUSIVE_UNHEDGED']),'mixed_loci':';'.join(loci[page]['MIXED_UNHEDGED']+loci[page]['MIXED_HEDGED']),'audit_state':audit_state})
with (R/'gdt002_aca_replication_capacity.tsv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out)
fresh=[x for x in out if x['clean_independent_eligible']]
result={'artifact':'GDT002_ACA_REPLICATION_CAPACITY_V1','status':'NO_CLEAN_INDEPENDENT_PAGE_IN_CURRENT_HUMAN_ANNOTATIONS','selection':'All non-f84r existing exact-locus rows with label layout code, classified only by unhedged/hedged and exclusive/mixed FIGURE/WATER_OR_APPARATUS human tags. No Voynich form selects a page.','counts':{'pages':len(out),'clean_independent_pages':len(fresh),'used_clean_pages':['f77r','f82r']},'best_exploratory_fallback':{'page':'f83r','physical_folio':'f83','figure_unhedged':2,'mixed_hedged':2,'apparatus_unhedged':0,'state':'REQUIRES_NEW_VISUAL_ADJUDICATION; FORMAL_VALUES_ALREADY_EXPOSED; EXPLORATORY_ONLY'},'holdout':{'page':'f84r','excluded_before_row_classification':True,'formal_payload_opened':False},'inputs':{str(p.relative_to(R)):sha(p) for p in [S/'existing_human_exact_locus_annotations.tsv',R/'gdt002_targeted_transfer_results.json',R/'GDT002_YOLO_LEDGER.tsv',R/'run_gdt002_aca_replication_capacity.py']},'documents':{str(p.relative_to(R)):sha(p) for p in [R/'GDT002_METHOD.md',R/'GDT002_ACA_REPLICATION_CAPACITY_REPORT.md',R/'GDT002_CURRENT_SUMMARY.md']},'outputs':{'gdt002_aca_replication_capacity.tsv':sha(R/'gdt002_aca_replication_capacity.tsv')},'claim_ceiling':'Capacity audit only. This does not close permissive exploration, assign any mixed row, establish ACA as a role, or infer a word, meaning, or translation.'}
(R/'gdt002_aca_replication_capacity_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(result['status'],result['counts'],result['best_exploratory_fallback'])
