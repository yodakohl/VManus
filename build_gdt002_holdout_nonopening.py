#!/usr/bin/env python3
"""Publish the deterministic GDT002 holdout non-opening decision."""
import hashlib,json
from pathlib import Path

R=Path(__file__).resolve().parent
def sha(name): return hashlib.sha256((R/name).read_bytes()).hexdigest()
def load(name): return json.loads((R/name).read_text())
def write(name,value): (R/name).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')

discovery=load('gdt002_discovery_results.json')
hypotheses=load('gdt002_joint_hypotheses.json')
checkpoint=load('gdt002_checkpoint_result.json')
replication=load('gdt002_contact_gap_replication_result.json')
assert discovery['retained_hypotheses']==[] and hypotheses['templates']==[]
assert checkpoint['access']['f84r_exact_projection_published'] is False
assert checkpoint['access']['f84r_exact_projection_joined_or_used_for_discovery'] is False
assert replication['visual_gate_passed'] is False
assert replication['access']['formal_payload_joined_or_opened_for_replication'] is False

prediction={
 'artifact':'GDT002_FROZEN_HOLDOUT_PREDICTION_V1',
 'status':'NO_PREDICTION_FROZEN_NO_IDENTIFIABLE_DISCOVERY_WORLD',
 'holdout_page':'f84r','physical_folio':'f84','retained_hypotheses':[],
 'predictions':[],
 'formal_payload_access':'COMMITMENT_ONLY_NOT_EXPORTED_INSPECTED_JOINED_OR_SCORED',
 'reason':'The source-only discovery beam is empty, and every bounded visual-relation augmentation stopped before formal comparison. Freezing a role prediction would invent an unsupported hypothesis.',
 'inputs':{n:sha(n) for n in ['build_gdt002_holdout_nonopening.py','gdt002_checkpoint_result.json','gdt002_discovery_results.json','gdt002_joint_hypotheses.json','gdt002_f84r_holdout_projection_commitment.json','gdt002_contact_gap_result.json','gdt002_contact_gap_extension_result.json','gdt002_contact_gap_replication_result.json']},
 'claim_ceiling':'This is a frozen non-opening decision, not a role prediction or holdout score. No semantic role, word, meaning, plaintext, or translation is inferred.'}
write('gdt002_frozen_holdout_prediction.json',prediction)

result={
 'artifact':'GDT002_HOLDOUT_RESULT_V1','status':'NOT_RUN_HOLDOUT_REMAINS_UNOPENED',
 'holdout_page':'f84r','prediction_state':prediction['status'],'retained_hypotheses':0,
 'scores':[],'formal_payload_opened':False,'formal_payload_joined':False,
 'holdout_scored':False,'solver_run':False,
 'decisive_reasons':['NO_IDENTIFIABLE_DISCOVERY_WORLD','CONTACT_GAP_COMPLETE_ARRAY_VISUAL_GATE_FAILED'],
 'inputs':{n:sha(n) for n in ['gdt002_frozen_holdout_prediction.json','gdt002_f84r_holdout_projection_commitment.json','gdt002_discovery_results.json','gdt002_contact_gap_replication_result.json','gdt002_contact_gap_replication_result_validation.json']},
 'claim_ceiling':'No GDT002 holdout result exists. The committed f84r formal payload remains unopened; no semantic role, word, meaning, plaintext, or translation is inferred.'}
write('gdt002_holdout_results.json',result)
print({'prediction_status':prediction['status'],'holdout_status':result['status']})
