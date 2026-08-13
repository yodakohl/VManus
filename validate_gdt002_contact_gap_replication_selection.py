#!/usr/bin/env python3
import csv,hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parent; RES=R/'experiments/semantic_assumptions/results'
def rows(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=rows(R/'gdt002_contact_gap_replication_selection.tsv'); e={r['locus']:r for r in rows(RES/'existing_human_exact_locus_annotations.tsv')}; c={r['locus']:r for r in rows(RES/'source_sta_family_consensus_loci.tsv')}
oldsel={r['locus']:r for r in rows(R/'gdt002_contact_gap_selection.tsv')}; oldobs={r['target_id']:r for r in rows(R/'gdt002_contact_gap_observations.tsv')}
wanted={'F100R_L2':[f'f100r.{i}' for i in range(6,12)],'F100V_L1':[f'f100v.{i}' for i in range(1,5)],'F99V_L1':[f'f99v.{i}' for i in range(2,10)],'F99V_L2':[f'f99v.{i}' for i in range(15,21)]}
meta={'F100R_L2':('f100r','f100','1006248','2676','3756','DISCOVERY'),'F100V_L1':('f100v','f100','1006249','7486','3715','DISCOVERY'),'F99V_L1':('f99v','f99','1006247','2802','3697','TRANSFER'),'F99V_L2':('f99v','f99','1006247','2802','3697','TRANSFER')}
expected=[]
for a,loci in wanted.items():
 page,folio,canvas,w,h,role=meta[a]
 for i,locus in enumerate(loci,1): expected.append((page,folio,locus,a,str(i),canvas,w,h,role))
checks={
 'rows_24':len(s)==24,'unique_ids':len({r['target_id'] for r in s})==24,'opaque_ids':all(re.fullmatch(r'CGR[0-9A-F]{12}',r['target_id']) for r in s),
 'four_candidate_array_locus_sets':all([r['locus'] for r in s if r['array_id']==a]==ls for a,ls in wanted.items()),
 'counts_6_4_8_6':[sum(r['array_id']==a for r in s) for a in wanted]==[6,4,8,6],
 'two_physical_folios':{r['physical_folio'] for r in s}=={'f99','f100'},
 'discovery_transfer_whole_folio':all((r['physical_folio']=='f100')==(r['panel_role']=='DISCOVERY') for r in s),
 'new15_inherited9':sum(r['call_source']=='NEW_CALL' for r in s)==15 and sum(r['call_source']=='INHERITED_FROZEN_CALL' for r in s)==9,
 'exact_row_tuples':[(r['page'],r['physical_folio'],r['locus'],r['array_id'],r['ordinal_in_complete_unit'],r['canvas_id'],r['width'],r['height'],r['panel_role']) for r in s]==expected,
 'call_source_and_old_id_exact':all((r['locus'] in oldsel)==(r['call_source']=='INHERITED_FROZEN_CALL') and r['inherited_from_target_id']==(oldsel[r['locus']]['target_id'] if r['locus'] in oldsel else '') for r in s),
 'inherited_observations_exist':all(r['inherited_from_target_id'] in oldobs for r in s if r['call_source']=='INHERITED_FROZEN_CALL'),
 'all_source_rows_exist':all(r['locus'] in e for r in s),
 'unit_assignments_exact':all(e[r['locus']]['unit']==r['array_id'].split('_')[-1] for r in s),
 'all_strict_except_f100r6':all(c[r['locus']]['strict_zero_alternative']=='1' for r in s if r['locus']!='f100r.6') and c['f100r.6']['strict_zero_alternative']=='0',
 'source_confirms_counts':all(x in e[l]['local_comment'] for l,x in [('f100r.6','There are 6 plants and 6 labels'),('f100v.1','there are 4 plants and 4 labels'),('f99v.2','eight labels on eight plants'),('f99v.15','There are 6 labels and 6 plants')]),
 'no_formal_payload':not ({'family_surface','sta_codes','local_comment','transcription'}&set(s[0])),
 'official_urls':all(r['official_image_url']==f"https://collections.library.yale.edu/iiif/2/{r['canvas_id']}/full/full/0/default.jpg" for r in s),
}
out={'artifact':'GDT002_CONTACT_GAP_REPLICATION_SELECTION_VALIDATION_V1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'counts':{'targets':24,'new_calls':15,'inherited_calls':9,'candidate_arrays_pending_census':4,'physical_folios':2},'bindings':{p.name:sha(p) for p in [R/'GDT002_CONTACT_GAP_REPLICATION_METHOD.md',R/'gdt002_contact_gap_replication_selection.tsv',R/'gdt002_contact_gap_selection.tsv',R/'gdt002_contact_gap_observations.tsv',R/'gdt002_contact_gap_result.json',RES/'existing_human_exact_locus_annotations.tsv',RES/'source_sta_family_consensus_loci.tsv']},'access':{'f99v16_f99v19_f100r6_regions_opened_for_localization_before_freeze':True,'f100v_prior_repository_visual_exposure':True,'new_15_target_states_reviewed_after_this_freeze':False,'formal_payload_opened_for_replication_selection':False,'automated_vision_used':False},'claim_ceiling':'Registration only; candidate arrays remain pending visual census; no new visual state, construction association, role, word, meaning, or translation.'}
(R/'gdt002_contact_gap_replication_selection_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print({'status':out['status'],'passed':out['passed'],'total':out['total']});sys.exit(0 if out['status']=='PASS' else 1)
