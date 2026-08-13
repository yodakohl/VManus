#!/usr/bin/env python3
"""Independent record-integrity validation of the stopped extension."""
import csv, hashlib, json, sys
from pathlib import Path
R=Path(__file__).resolve().parent
def rows(name):
    with (R/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()

census=rows('gdt002_contact_gap_extension_census.tsv')
selection=rows('gdt002_contact_gap_extension_selection.tsv')
result=json.loads((R/'gdt002_contact_gap_extension_result.json').read_text())
exact=rows('experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv')
f88=[r for r in exact if r['page']=='f88r' and r['unit']=='L1']
f88_c1=[r for r in exact if r['locus']=='f88r.1' and r['unit']=='C1']
cr={r['array_id']:r for r in census}
checks={
 'four_units':len(census)==4 and set(cr)=={'F99V_L2','F100R_L2','F88R_L1','F102V1_L1'},
 'selection_13':len(selection)==13,
 'f88_five_frozen_rows':len([r for r in selection if r['array_id']=='F88R_L1'])==5==len(f88),
 'human_source_says_six':any('There are 6 labels alternating with 5 plants' in r['local_comment'] for r in f88),
 'far_left_source_mapped_c1':len(f88_c1)==1,
 'f88_census_uncertain_exact':cr['F88R_L1']['census_state']=='UNCERTAIN' and cr['F88R_L1']['visible_inscription_count']=='6' and cr['F88R_L1']['frozen_locus_count']=='5',
 'f88_bounds':cr['F88R_L1']['unit_context_xywh']=='500,250,2200,900' and cr['F88R_L1']['far_left_mapped_c1_xywh']=='630,335,245,125',
 'other_units_not_completed':all(cr[u]['census_state']=='NOT_COMPLETED_AFTER_DECISIVE_STOP' for u in ('F99V_L2','F100R_L2','F102V1_L1')),
 'completion_access_matches_selection':cr['F99V_L2']['image_access']=='FULL_PAGE_UNIT_AND_TWO_COMPLETION_TARGET_REGIONS_INSPECTED' and cr['F100R_L2']['image_access']=='FULL_PAGE_UNIT_AND_ONE_COMPLETION_TARGET_REGION_INSPECTED' and len([r for r in selection if r['array_id']=='F99V_L2'])==2 and len([r for r in selection if r['array_id']=='F100R_L2'])==1,
 'no_contact_gap_judgments':all('NO_CONTACT_GAP_JUDGMENT' in r['judgment_stage'] for r in census),
 'stop_exact':result['status']=='STOP_CENSUS_UNCERTAIN_EDITORIAL_UNIT_BOUNDARY_NO_REVIEW_NO_FORMAL_COMPARISON',
 'gates_all_closed':result['gates']=={'f88_exact_locus_set_exhausts_visible_annotated_unit':False,'formal_construction_comparison_authorized':False,'randomized_two_reviewer_stage_authorized':False},
 'access_exact':result['access']=={'contact_gap_review_calls_made':False,'f102_full_page_opened_but_target_regions_not_opened':True,'f88_census_completed':True,'f99_f100_completion_regions_localized_but_not_judged':True,'formal_payload_joined_or_opened_for_extension':False,'joint_solver_run':False,'new_target_images_opened_after_registration':True,'ocr_or_automated_vision_used':False},
 'input_hashes':all(sha(n)==h for n,h in result['inputs'].items()),
 'output_hashes':all(sha(n)==h for n,h in result['outputs'].items()),
 'no_formal_payload_columns':not ({'family_surface','sta_codes','transcription','root','member'} & set(census[0])),
 'claim_ceiling_no_role':all(x in result['claim_ceiling'] for x in ('no author-visible boundary','No relation state','role','translation')),
}
failed=[k for k,v in checks.items() if not v]
out={'artifact':'GDT002_CONTACT_GAP_EXTENSION_RESULT_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'result_sha256':sha('gdt002_contact_gap_extension_result.json'),'scope':'Independent source-row census, access-state, stop-gate, schema, and hash validation. The direct visual census is recorded, not independently re-inspected by this validator.'}
(R/'gdt002_contact_gap_extension_result_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed}))
sys.exit(bool(failed))
