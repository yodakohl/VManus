#!/usr/bin/env python3
import csv,hashlib,json,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=read(S/'existing_human_exact_locus_annotations.tsv');tab=read(R/'gdt002_aca_replication_capacity.tsv');res=json.loads((R/'gdt002_aca_replication_capacity_result.json').read_text());c=defaultdict(Counter)
for x in src:
 if x['page']=='f84r' or len(x['normalized_code'])<2 or x['normalized_code'][1]!='L':continue
 t=set(x['object_tags'].split(';'));a='WATER_OR_APPARATUS' in t;f='FIGURE' in t
 s='APPARATUS_EXCLUSIVE' if a and not f else 'FIGURE_EXCLUSIVE' if f and not a else 'MIXED' if a and f else ''
 if s:c[x['page']][f'{s}_{x["certainty"]}']+=1
by={x['page']:x for x in tab};eligible=[];row_exact=True
for p,v in c.items():
 physical=p.split('r')[0].split('v')[0]
 if physical not in {'f77','f82'} and v['APPARATUS_EXCLUSIVE_UNHEDGED']>=2 and v['FIGURE_EXCLUSIVE_UNHEDGED']>=2:eligible.append(p)
for p,v in c.items():
 r=by.get(p,{})
 expected={'apparatus_unhedged':v['APPARATUS_EXCLUSIVE_UNHEDGED'],'apparatus_hedged':v['APPARATUS_EXCLUSIVE_HEDGED'],'figure_unhedged':v['FIGURE_EXCLUSIVE_UNHEDGED'],'figure_hedged':v['FIGURE_EXCLUSIVE_HEDGED'],'mixed_unhedged':v['MIXED_UNHEDGED'],'mixed_hedged':v['MIXED_HEDGED']}
 used=r.get('already_used_folio')=='1';eligible_state=r.get('clean_independent_eligible')=='1'
 expected_state='CLEAN_INDEPENDENT_ELIGIBLE' if eligible_state else 'ALREADY_USED_PHYSICAL_FOLIO' if used else 'NOT_CLEAN_INDEPENDENT_ELIGIBLE'
 row_exact &= all(r.get(k)==str(n) for k,n in expected.items()) and r.get('audit_state')==expected_state
checks={'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='yolo/gdt002-visual-grammar-constraints','page_count':len(tab)==26 and len(by)==26 and set(by)==set(c),'all_page_counts_exact':row_exact,'zero_clean':eligible==[] and sum(int(x['clean_independent_eligible']) for x in tab)==0,'used_pages':by['f77r']['apparatus_unhedged']=='6' and by['f77r']['figure_unhedged']=='4' and by['f82r']['apparatus_unhedged']=='3' and by['f82r']['figure_unhedged']=='8','f83_fallback':by['f83r']['apparatus_unhedged']=='0' and by['f83r']['figure_unhedged']=='2' and by['f83r']['mixed_hedged']=='2','f84_absent':'f84r' not in by and res['holdout']['formal_payload_opened'] is False,'ledger_row':sum(1 for x in read(R/'GDT002_YOLO_LEDGER.tsv') if x['checkpoint_id']=='GDT002_CKPT011')==1,'input_hashes':all(sha(R/k)==v for k,v in res['inputs'].items()),'document_hashes':all(sha(R/k)==v for k,v in res['documents'].items()),'output_hashes':all(sha(R/k)==v for k,v in res['outputs'].items()),'claim_ceiling':'does not close permissive exploration' in res['claim_ceiling'] and 'translation' in res['claim_ceiling']}
failed=[k for k,v in checks.items() if not v];out={'artifact':'GDT002_ACA_REPLICATION_CAPACITY_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'result_sha256':sha(R/'gdt002_aca_replication_capacity_result.json'),'scope':'Independent source-only page/state counts, eligibility, f83 fallback, holdout exclusion, and hashes; no formal values or images.'}
(R/'gdt002_aca_replication_capacity_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed});sys.exit(bool(failed))
