#!/usr/bin/env python3
"""Bind the fixed f83r direct observations and exposed formal comparison."""
import csv,hashlib,itertools,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
obs=read(R/'gdt002_f83r_direct_visual_observations.tsv');ann={x['locus']:x for x in read(S/'existing_human_exact_locus_annotations.tsv')};fam={x['locus']:x for x in read(S/'source_sta_family_consensus_loci.tsv')}
assert {x['locus'] for x in obs}=={'f83r.45','f83r.46','f83r.50','f83r.51'}
for x in obs:
 assert x['prior_human_tags']==ann[x['locus']]['object_tags'] and x['prior_human_certainty']==ann[x['locus']]['certainty']
 assert x['formal_family_expression']==fam[x['locus']]['family_sequence']
 assert int(x['contains_ACA'])==int('ACA' in x['formal_family_expression'])
lower=[x for x in obs if x['normalized_geometry_class'].startswith('LOWER_')];arch=[x for x in obs if x['normalized_geometry_class'].startswith('ARCH_')]
effect=sum(int(x['contains_ACA']) for x in lower)/len(lower)-sum(int(x['contains_ACA']) for x in arch)/len(arch)
states=[int(x['contains_ACA']) for x in obs];worlds=list(set(itertools.permutations(states)));tail=sum((sum(w[:2])/2-sum(w[2:])/2)>=effect-1e-12 for w in worlds)
result={'artifact':'GDT002_F83R_DIRECT_VISUAL_REINSPECTION_V1','status':'F83R_PANEL_TAG_SCOPE_CORRECTED_NO_INDEPENDENT_ACA_CONTRAST','mode':'POST_EXPOSURE_EXPLORATORY_DIRECT_VISUAL','counts':{'rows':4,'arch_end_mixed':2,'lower_outlet_no_local_figure':2,'ACA_arch':sum(int(x['contains_ACA']) for x in arch),'ACA_lower':sum(int(x['contains_ACA']) for x in lower)},'comparison':{'effect_lower_minus_arch':effect,'exact_worlds':len(worlds),'one_sided_exact_p':tail/len(worlds),'tail':tail,'interpretation':'Descriptive post-exposure within-page comparison only; the lower 2/2 versus arch 1/2 contrast is weak and supplies no independent negative visual state.'},'provenance_correction':'The inherited FIGURE tag on f83r.50/.51 describes the larger illustrated panel and must not be treated as evidence that either inscription is locally owned by a human figure. Native inspection places both beside lower structure outlets/bases.','holdout':{'page':'f84r','formal_payload_opened':False,'formal_payload_joined':False,'used':False},'inputs':{str(p.relative_to(R)):sha(p) for p in [R/'gdt002_f83r_direct_visual_observations.tsv',S/'existing_human_exact_locus_annotations.tsv',S/'source_sta_family_consensus_loci.tsv',R/'gdt002_aca_replication_capacity_result.json',R/'gdt002_targeted_transfer_results.json',R/'GDT002_YOLO_LEDGER.tsv',R/'build_gdt002_f83r_direct_visual.py']},'documents':{str(p.relative_to(R)):sha(p) for p in [R/'GDT002_METHOD.md',R/'GDT002_F83R_DIRECT_VISUAL_REPORT.md',R/'GDT002_CURRENT_SUMMARY.md']},'claim_ceiling':'Exploratory visible geometry and tag-scope correction only. Ownership remains PROXIMITY_ONLY or ambiguous; no semantic role, object name, word, meaning, or translation is established.'}
(R/'gdt002_f83r_direct_visual_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(result['status'],result['counts'],result['comparison'])
