#!/usr/bin/env python3
"""Build the stopped GDT002 complete-unit census result."""
import csv, hashlib, io, json
from pathlib import Path

R=Path(__file__).resolve().parent
def sha(name): return hashlib.sha256((R/name).read_bytes()).hexdigest()
def write_tsv(name, records):
    out=io.StringIO(newline='')
    w=csv.DictWriter(out,fieldnames=list(records[0]),delimiter='\t',lineterminator='\n')
    w.writeheader(); w.writerows(records); (R/name).write_text(out.getvalue())

rows=[
 {'array_id':'F99V_L2','page':'f99v','physical_folio':'f99','canvas_id':'1006247','width':'2802','height':'3697','full_image_sha256':'111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5','census_state':'NOT_COMPLETED_AFTER_DECISIVE_STOP','confidence':'NA','unit_context_xywh':'','far_left_mapped_c1_xywh':'','visible_inscription_count':'','frozen_locus_count':'6','image_access':'FULL_PAGE_UNIT_AND_TWO_COMPLETION_TARGET_REGIONS_INSPECTED','judgment_stage':'NO_CONTACT_GAP_JUDGMENT','neutral_note':'Localization work began before the f88 census stop; no census or visual-state call was finalized.'},
 {'array_id':'F100R_L2','page':'f100r','physical_folio':'f100','canvas_id':'1006248','width':'2676','height':'3756','full_image_sha256':'6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429','census_state':'NOT_COMPLETED_AFTER_DECISIVE_STOP','confidence':'NA','unit_context_xywh':'','far_left_mapped_c1_xywh':'','visible_inscription_count':'','frozen_locus_count':'6','image_access':'FULL_PAGE_UNIT_AND_ONE_COMPLETION_TARGET_REGION_INSPECTED','judgment_stage':'NO_CONTACT_GAP_JUDGMENT','neutral_note':'Localization work began before the f88 census stop; no census or visual-state call was finalized.'},
 {'array_id':'F88R_L1','page':'f88r','physical_folio':'f88','canvas_id':'1037112','width':'2714','height':'3735','full_image_sha256':'a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013','census_state':'UNCERTAIN','confidence':'HIGH','unit_context_xywh':'500,250,2200,900','far_left_mapped_c1_xywh':'630,335,245,125','visible_inscription_count':'6','frozen_locus_count':'5','image_access':'FULL_PAGE_UNIT_AND_FAR_LEFT_REGION_INSPECTED','judgment_stage':'CENSUS_ONLY_NO_CONTACT_GAP_JUDGMENT','neutral_note':'Six mapped inscriptions span one uninterrupted top-row geometry. The far-left inscription is f88r.1/C1 and the five subsequent inscriptions are f88r.2-.6/L1; no author-visible boundary secures that editorial C1/L1 split.'},
 {'array_id':'F102V1_L1','page':'f102v1','physical_folio':'f102','canvas_id':'1006252','width':'2981','height':'3795','full_image_sha256':'8cdb1030d805b968932146124915cb0d86f7abf853167ffec028b59599820fad','census_state':'NOT_COMPLETED_AFTER_DECISIVE_STOP','confidence':'NA','unit_context_xywh':'300,250,2500,1150','far_left_mapped_c1_xywh':'','visible_inscription_count':'','frozen_locus_count':'5','image_access':'FULL_PAGE_INSPECTED_UNIT_CROP_GENERATED_NOT_VIEWED_NO_TARGET_REGIONS','judgment_stage':'NO_CONTACT_GAP_JUDGMENT','neutral_note':'Full page was opened before the f88 stop; no target crop, census conclusion, or visual-state call was made.'},
]
write_tsv('gdt002_contact_gap_extension_census.tsv',rows)
result={
 'experiment':'GDT002_CONTACT_GAP_COMPLETE_UNIT_EXTENSION',
 'status':'STOP_CENSUS_UNCERTAIN_EDITORIAL_UNIT_BOUNDARY_NO_REVIEW_NO_FORMAL_COMPARISON',
 'provenance':'EXPLORATORY_AI_DIRECT_VISUAL_OBSERVATION',
 'decisive_observation':{'array_id':'F88R_L1','census_state':'UNCERTAIN','visible_inscriptions':6,'frozen_l1_loci':5,'far_left_mapped_locus':'f88r.1','reason':'No author-visible boundary separates source-assigned C1 from L1 in the uninterrupted top-row geometry.','confidence':'HIGH'},
 'gates':{'f88_exact_locus_set_exhausts_visible_annotated_unit':False,'randomized_two_reviewer_stage_authorized':False,'formal_construction_comparison_authorized':False},
 'access':{'new_target_images_opened_after_registration':True,'f99_f100_completion_regions_localized_but_not_judged':True,'f102_full_page_opened_but_target_regions_not_opened':True,'f88_census_completed':True,'contact_gap_review_calls_made':False,'formal_payload_joined_or_opened_for_extension':False,'joint_solver_run':False,'ocr_or_automated_vision_used':False},
 'inputs':{n:sha(n) for n in ['GDT002_CONTACT_GAP_EXTENSION_METHOD.md','gdt002_contact_gap_extension_selection.tsv','gdt002_contact_gap_extension_selection_validation.json','gdt002_contact_gap_observations.tsv','gdt002_contact_gap_result.json','build_gdt002_contact_gap_extension_result.py']},
 'outputs':{'gdt002_contact_gap_extension_census.tsv':sha('gdt002_contact_gap_extension_census.tsv')},
 'claim_ceiling':'The f88 transfer-unit census is uncertain because no author-visible boundary separates mapped f88r.1/C1 from frozen f88r.2-.6/L1 in the uninterrupted six-inscription row. Review and formal comparison stopped. No relation state, construction association, role, word, meaning, or translation is inferred.',
}
(R/'gdt002_contact_gap_extension_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')

if __name__=='__main__': print(json.dumps({'status':result['status'],'rows':len(rows)}))
