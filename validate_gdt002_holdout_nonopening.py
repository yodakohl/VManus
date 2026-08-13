#!/usr/bin/env python3
import csv,hashlib,json,sys
from pathlib import Path

R=Path(__file__).resolve().parent
def sha(name): return hashlib.sha256((R/name).read_bytes()).hexdigest()
def load(name): return json.loads((R/name).read_text())
def pages(name):
 with (R/name).open(newline='',encoding='utf-8') as f:return {r['page'] for r in csv.DictReader(f,delimiter='\t')}

p=load('gdt002_frozen_holdout_prediction.json');h=load('gdt002_holdout_results.json')
d=load('gdt002_discovery_results.json');j=load('gdt002_joint_hypotheses.json')
c=load('gdt002_checkpoint_result.json');first=load('gdt002_contact_gap_result.json');extension=load('gdt002_contact_gap_extension_result.json');r=load('gdt002_contact_gap_replication_result.json')
checks={
 'prediction_status':p['status']=='NO_PREDICTION_FROZEN_NO_IDENTIFIABLE_DISCOVERY_WORLD',
 'empty_discovery_beam':d['retained_hypotheses']==[] and j['templates']==[] and p['retained_hypotheses']==[] and p['predictions']==[],
 'holdout_status':h['status']=='NOT_RUN_HOLDOUT_REMAINS_UNOPENED',
 'no_scores':h['scores']==[] and h['retained_hypotheses']==0,
 'no_open_join_score_solver':all(h[k] is False for k in ('formal_payload_opened','formal_payload_joined','holdout_scored','solver_run')),
 'checkpoint_access':c['access']['f84r_exact_projection_published'] is False and c['access']['f84r_exact_projection_displayed_or_manually_inspected'] is False and c['access']['f84r_exact_projection_joined_or_used_for_discovery'] is False,
 'discovery_tables_exclude_f84r':pages('gdt002_grammar_projection.tsv')=={'f80r','f82r'} and pages('gdt002_grammar_consensus_projection.tsv')=={'f80r','f82r'},
 'replication_stopped_preformal':r['visual_gate_passed'] is False and r['access']['formal_payload_joined_or_opened_for_replication'] is False and r['access']['joint_solver_run'] is False,
 'first_acquisition_stopped_preformal':first['status']=='STOP_CAPACITY_GATE_FAILED_NO_FORMAL_COMPARISON' and first['access']['formal_visual_join_or_role_solver_run'] is False,
 'extension_stopped_preformal':extension['status']=='STOP_CENSUS_UNCERTAIN_EDITORIAL_UNIT_BOUNDARY_NO_REVIEW_NO_FORMAL_COMPARISON' and extension['access']['formal_payload_joined_or_opened_for_extension'] is False and extension['access']['joint_solver_run'] is False,
 'prediction_input_hashes':all(sha(n)==v for n,v in p['inputs'].items()),
 'holdout_input_hashes':all(sha(n)==v for n,v in h['inputs'].items()),
 'claim_ceiling':all(x in p['claim_ceiling']+h['claim_ceiling'] for x in ('No semantic role','plaintext','translation')),
}
failed=[k for k,v in checks.items() if not v]
out={'artifact':'GDT002_HOLDOUT_NONOPENING_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'prediction_sha256':sha('gdt002_frozen_holdout_prediction.json'),'holdout_result_sha256':sha('gdt002_holdout_results.json'),'scope':'Integrity validation of the empty discovery beam, pre-formal stops, discovery-table page scope, input hashes, and explicit f84r non-opening decision.'}
(R/'gdt002_holdout_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed});sys.exit(bool(failed))
