#!/usr/bin/env python3
import csv,hashlib,io,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
def rows(n):
 with (R/n).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def emit(n,rs):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs);(R/n).write_text(out.getvalue())

sel=rows('gdt002_contact_gap_replication_selection.tsv');loc={r['target_id']:r for r in rows('gdt002_contact_gap_replication_localizations.tsv')}
old={r['target_id']:r for r in rows('gdt002_contact_gap_observations.tsv')};b={r['blind_review_id']:r for r in rows('gdt002_contact_gap_replication_reviewer_b.tsv')};c={r['blind_review_id']:r for r in rows('gdt002_contact_gap_replication_reviewer_c.tsv')}
obs=[];counts=defaultdict(Counter)
for r in sel:
 if r['call_source']=='INHERITED_FROZEN_CALL':
  o=old[r['inherited_from_target_id']];state=o['review_state'];source='INHERITED_FROZEN_PRIOR_CALL';agreement='NOT_REREVIEWED'
 else:
  blind=loc[r['target_id']]['blind_review_id'];rb,rc=b[blind],c[blind];state=rb['review_state'] if rb['review_state']==rc['review_state'] else 'UNCERTAIN';source='TWO_INDEPENDENT_SOURCE_FREE_CROP_REVIEWS';agreement='AGREE' if rb['review_state']==rc['review_state'] else 'DISAGREE_TO_UNCERTAIN'
 obs.append({'target_id':r['target_id'],'array_id':r['array_id'],'call_source':r['call_source'],'inherited_from_target_id':r['inherited_from_target_id'],'blind_review_id':loc[r['target_id']]['blind_review_id'] if r['call_source']=='NEW_CALL' else '','consensus_state':state,'review_agreement':agreement,'consensus_source':source,'provenance':'AI_DIRECT_VISUAL_OBSERVATION'})
 counts[r['array_id']][state]+=1
emit('gdt002_contact_gap_replication_observations.tsv',obs)
summary={a:{s:counts[a][s] for s in ('CONTACT','CLEAR_GAP','UNCERTAIN')} for a in sorted(counts)}
gates={a:v['CONTACT']>=1 and v['CLEAR_GAP']>=2 and v['UNCERTAIN']==0 for a,v in summary.items()}
visual_pass=all(gates.values())
status='VISUAL_GATE_PASS_READY_FOR_FROZEN_FORMAL_COMPARISON' if visual_pass else 'STOP_VISUAL_GATE_FAILED_NO_FORMAL_COMPARISON'
failure='' if visual_pass else 'F100V_L1 has zero CONTACT and four CLEAR_GAP calls; every candidate array required >=1 CONTACT, >=2 CLEAR_GAP, and zero UNCERTAIN.'
result={'experiment':'GDT002_CONTACT_GAP_COMPLETE_ARRAY_REPLICATION','status':status,'counts_by_array':summary,'visual_gate_by_array':gates,'visual_gate_passed':visual_pass,'decisive_failure':failure,'access':{'all_four_array_censuses_exact':True,'new_target_states_reviewed_after_registration':True,'valid_source_free_reviewers':2,'valid_source_free_reviewer_tasks':['/root/gdt002_blind_review_b','/root/gdt002_blind_review_c'],'source_aware_reviewer_a_calls_excluded_due_role_contamination':True,'inherited_calls_changed_or_rereviewed':False,'formal_payload_joined_or_opened_for_replication':False,'joint_solver_run':False,'ocr_or_automated_vision_used':False},'inputs':{n:sha(n) for n in ['GDT002_CONTACT_GAP_REPLICATION_METHOD.md','gdt002_contact_gap_replication_selection.tsv','gdt002_contact_gap_replication_selection_validation.json','build_gdt002_contact_gap_replication_localizations.py','gdt002_contact_gap_replication_localizations.tsv','gdt002_contact_gap_replication_reviewer_b.tsv','gdt002_contact_gap_replication_reviewer_c.tsv','gdt002_contact_gap_replication_reviewer_provenance.tsv','gdt002_contact_gap_selection.tsv','gdt002_contact_gap_observations.tsv','build_gdt002_contact_gap_replication_result.py']},'outputs':{'gdt002_contact_gap_replication_observations.tsv':sha('gdt002_contact_gap_replication_observations.tsv')},'claim_ceiling':'Three arrays in the frozen two-folio panel contain recorded CONTACT/CLEAR_GAP mobility, but F100V_L1 has no CONTACT and the frozen four-array visual gate fails. No formal construction association, semantic role, word, POS, sound, language, plaintext, meaning, or translation was tested or inferred.'}
(R/'gdt002_contact_gap_replication_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print({'status':result['status'],'counts':summary})
