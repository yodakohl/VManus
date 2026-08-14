#!/usr/bin/env python3
"""Independent integrity validator for GDT005."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def rd(p):
    with (R/p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sh(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
checks=[]
def ck(n,v):
    checks.append({'name':n,'pass':bool(v)})
    if not v:raise AssertionError(n)
s=rd('gdt005_matched_cut_selection.tsv'); o=rd('gdt005_matched_cut_observations.tsv'); r=json.loads((R/'gdt005_matched_cut_result.json').read_text())
ck('nine_pairs',len(s)==len(o)==9); ck('unique_folios',len({x['locus'].split('.')[0][:-1] if x['locus'].split('.')[0][-1] in 'rv' else x['locus'].split('.')[0] for x in s})==9)
ck('no_f84',all('f84' not in str(x) for x in (s+o)) and not r['holdout']['f84r_opened'])
ck('direct_visual',all(x['provenance']=='AI_DIRECT_VISUAL_OBSERVATION' for x in o))
tr=sum(int(x['target_registered_cuts']) for x in o); cr=sum(int(x['control_registered_pseudo_cuts']) for x in o)
tl=sum(int(x['target_secure_cuts']) for x in o); cl=sum(int(x['control_secure_cuts']) for x in o)
ck('registered_cut_counts',tr==cr==17); ck('secure_cut_counts',tl==3 and cl==0)
ck('wrong_target_boxes',sum(x['target_group_state']=='LOCALIZATION_INVALIDATED_WRONG_BOX' for x in o)==2)
ck('result_arithmetic',r['registered_target_cuts']==tr and r['registered_control_pseudo_cuts']==cr and r['securely_localized_target_cuts']==tl and r['securely_localized_control_cuts']==cl)
ck('status',r['status']=='INVALIDATED_NO_MATCHED_LOCALIZATION_CAPACITY' and r['matched_difference']=='NOT_COMPUTED_NO_SECURE_CONTROL_CUTS')
ck('microspacing_ceiling',r['microspacing_or_stroke_test'].startswith('NOT_SCORED'))
for p,h in r['inputs'].items():ck('hash_'+p,sh(p)==h)
ck('claim_ceiling','no matched spacing result' in r['claim_ceiling'] and 'translation' in r['claim_ceiling'])
payload={'status':'PASS_RECORD_AND_CLAIM_INTEGRITY','checks_passed':len(checks),'checks':checks,'result_sha256':sh('gdt005_matched_cut_result.json'),'report_sha256':sh('GDT005_MATCHED_PHYSICAL_CUT_REPORT.md'),'validator_sha256':sh('validate_gdt005_matched_physical_cut.py'),'branch_ledger_sha256':sh('GDT002_YOLO_LEDGER.tsv'),'scope':'Checks registered pairs, corrected localization capacity, hashes, holdout exclusion, and ceiling; does not repeat direct visual localization.'}
(R/'gdt005_matched_cut_validation.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
