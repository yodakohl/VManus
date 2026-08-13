#!/usr/bin/env python3
import csv,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
def rows(n):
 with (R/n).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
sel=rows('gdt002_contact_gap_replication_selection.tsv');loc=rows('gdt002_contact_gap_replication_localizations.tsv');obs=rows('gdt002_contact_gap_replication_observations.tsv');b=rows('gdt002_contact_gap_replication_reviewer_b.tsv');c=rows('gdt002_contact_gap_replication_reviewer_c.tsv');provenance=rows('gdt002_contact_gap_replication_reviewer_provenance.tsv');old={r['target_id']:r for r in rows('gdt002_contact_gap_observations.tsv')};result=json.loads((R/'gdt002_contact_gap_replication_result.json').read_text())
sd={r['target_id']:r for r in sel};ld={r['target_id']:r for r in loc};bd={r['blind_review_id']:r for r in b};cd={r['blind_review_id']:r for r in c}
join_fields=('target_id','inherited_from_target_id','page','physical_folio','locus','array_id','ordinal_in_complete_unit','canvas_id','width','height','official_image_url','panel_role','call_source')
def box(r,k):return tuple(map(int,r[k].split(',')))
def in_bounds(r,q):return 0<=q[0]<q[0]+q[2]<=int(r['width']) and 0<=q[1]<q[1]+q[3]<=int(r['height'])
def contains(outer,inner):return outer[0]<=inner[0] and outer[1]<=inner[1] and inner[0]+inner[2]<=outer[0]+outer[2] and inner[1]+inner[3]<=outer[1]+outer[3]
calc=[];counts=defaultdict(Counter)
for o in obs:
 r=sd[o['target_id']]
 if r['call_source']=='INHERITED_FROZEN_CALL': expected=old[r['inherited_from_target_id']]['review_state']
 else:
  blind=ld[r['target_id']]['blind_review_id'];expected=bd[blind]['review_state'] if bd[blind]['review_state']==cd[blind]['review_state'] else 'UNCERTAIN'
 calc.append(expected==o['consensus_state']);counts[r['array_id']][o['consensus_state']]+=1
summary={a:{s:counts[a][s] for s in ('CONTACT','CLEAR_GAP','UNCERTAIN')} for a in sorted(counts)};gates={a:v['CONTACT']>=1 and v['CLEAR_GAP']>=2 and v['UNCERTAIN']==0 for a,v in summary.items()}
checks={
'cardinality_24_24':len(sel)==len(loc)==len(obs)==24,'new_reviewers_15_each':len(b)==len(c)==15 and set(bd)==set(cd)=={r['blind_review_id'] for r in loc if r['call_source']=='NEW_CALL'},
'selection_localization_exact_join':set(sd)==set(ld) and all(all(sd[k][f]==ld[k][f] for f in join_fields) for k in sd),
'all_censuses_exact':all(r['array_census_state']=='EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_ANNOTATED_UNIT' and r['array_census_confidence']=='HIGH' for r in loc),
'all_localizations_in_bounds':all(in_bounds(r,box(r,'context_xywh')) and in_bounds(r,box(r,'target_xywh')) and contains(box(r,'context_xywh'),box(r,'target_xywh')) for r in loc),
'localization_hashes_well_formed':all(all(len(r[k])==64 and set(r[k])<={'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'} for k in ('full_image_sha256','context_png_sha256','target_png_sha256','marked_png_sha256')) for r in loc),
'localizer_never_judged_state':all(r['localizer_state_judgment']=='CONTACT_GAP_NOT_JUDGED' for r in loc),
'review_vocab':all(r['review_state'] in {'CONTACT','CLEAR_GAP','UNCERTAIN'} for r in b+c),
'reviewer_scopes_exact':all(r['reviewer_scope']=='SOURCE_FREE_CROP_ONLY_REVIEWER_B' for r in b) and all(r['reviewer_scope']=='SOURCE_FREE_CROP_ONLY_REVIEWER_C' for r in c),
'reviewer_provenance_exact':provenance==[{'reviewer_artifact':'gdt002_contact_gap_replication_reviewer_b.tsv','reviewer_agent_task':'/root/gdt002_blind_review_b','fork_context':'NONE','source_access':'BLINDED_PACKET_ONLY','valid_for_consensus':'1'},{'reviewer_artifact':'gdt002_contact_gap_replication_reviewer_c.tsv','reviewer_agent_task':'/root/gdt002_blind_review_c','fork_context':'NONE','source_access':'BLINDED_PACKET_ONLY','valid_for_consensus':'1'}],
'two_valid_reviewers_agree_all':all(bd[k]['review_state']==cd[k]['review_state'] for k in bd),
'consensus_independent':all(calc),'counts_exact':summary==result['counts_by_array']=={'F100R_L2':{'CONTACT':1,'CLEAR_GAP':5,'UNCERTAIN':0},'F100V_L1':{'CONTACT':0,'CLEAR_GAP':4,'UNCERTAIN':0},'F99V_L1':{'CONTACT':4,'CLEAR_GAP':4,'UNCERTAIN':0},'F99V_L2':{'CONTACT':1,'CLEAR_GAP':5,'UNCERTAIN':0}},
'gates_exact':gates==result['visual_gate_by_array']=={'F100R_L2':True,'F100V_L1':False,'F99V_L1':True,'F99V_L2':True},
'stop_exact':not result['visual_gate_passed'] and result['status']=='STOP_VISUAL_GATE_FAILED_NO_FORMAL_COMPARISON','no_formal_payload_columns':not ({'family_surface','sta_codes','transcription','root'}&set(obs[0])),
'access_exact':result['access']=={'all_four_array_censuses_exact':True,'formal_payload_joined_or_opened_for_replication':False,'inherited_calls_changed_or_rereviewed':False,'joint_solver_run':False,'new_target_states_reviewed_after_registration':True,'ocr_or_automated_vision_used':False,'source_aware_reviewer_a_calls_excluded_due_role_contamination':True,'valid_source_free_reviewers':2,'valid_source_free_reviewer_tasks':['/root/gdt002_blind_review_b','/root/gdt002_blind_review_c']},
'input_hashes':all(sha(n)==h for n,h in result['inputs'].items()),'output_hashes':all(sha(n)==h for n,h in result['outputs'].items()),'claim_ceiling':all(x in result['claim_ceiling'] for x in ('No formal construction association','semantic role','translation'))}
failed=[k for k,v in checks.items() if not v];out={'artifact':'GDT002_CONTACT_GAP_REPLICATION_RESULT_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'result_sha256':sha('gdt002_contact_gap_replication_result.json'),'scope':'Independent table joins, census/localization bounds, two-reviewer consensus, inherited-call binding, counts, gates, access assertions, and hashes. Pixel judgments are recorded and not independently re-inspected by this validator.'};(R/'gdt002_contact_gap_replication_result_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed});sys.exit(bool(failed))
