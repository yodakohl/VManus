#!/usr/bin/env python3
"""Independent integrity and selected-statistic validator for GDT002 exploration."""
import csv,hashlib,itertools,json,math,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signed(mask,y,strata):
 v=[]
 for s in sorted(set(strata)):
  p=[mask[i] for i,z in enumerate(strata) if z==s and y[i]];n=[mask[i] for i,z in enumerate(strata) if z==s and not y[i]]
  if p and n:v.append(sum(p)/len(p)-sum(n)/len(n))
 return (sum(v)/len(v) if v else 0.0,len(v))
def worlds(y,strata):
 b=[]
 for s in sorted(set(strata)):
  ix=[i for i,z in enumerate(strata) if z==s];b.append((ix,list(itertools.combinations(ix,sum(y[i] for i in ix)))))
 for q in itertools.product(*(x[1] for x in b)):
  z=[0]*len(y)
  for chosen in q:
   for i in chosen:z[i]=1
  yield z
def mi(mask,y,strata):
 n=len(y);v=0.0
 for s in sorted(set(strata)):
  ix=[i for i,z in enumerate(strata) if z==s];ns=len(ix);joint=Counter((mask[i],y[i]) for i in ix);a=Counter(mask[i] for i in ix);b=Counter(y[i] for i in ix)
  for (u,w),k in joint.items():v+=(k/n)*math.log2(k*ns/(a[u]*b[w]))
 return v
def close(a,b,t=1e-12):return abs(float(a)-float(b))<=t

j=read(R/'gdt002_exploratory_visual_formal_join.tsv');a=read(R/'gdt002_exploratory_candidate_atlas.tsv');res=json.loads((R/'gdt002_exploratory_discovery_results.json').read_text())
contact=[x for x in j if x['channel']=='CONTACT_GAP'];hard=[x for x in contact if x['visual_state'] in {'CONTACT','CLEAR_GAP'}];y=[int(x['visual_state']=='CONTACT') for x in hard];strata=[x['array_id'] for x in hard];ws=list(worlds(y,strata))
amap={(x['channel'],x['formal_feature']):x for x in a}
zl_a1=[int('A1' in x['ZL3b_member_expression'].replace('|',' ').split()) for x in hard];kfam=[int('K' in x['family_expression']) for x in hard];length=[int(x['symbol_count']) for x in hard]
def p_signed(mask):
 e=signed(mask,y,strata)[0];return e,sum(abs(signed(mask,z,strata)[0])>=abs(e)-1e-12 for z in ws)/len(ws)
a1e,a1p=p_signed(zl_a1);ke,kp=p_signed(kfam);lengthmi=mi(length,y,strata);lengthp=sum(mi(length,z,strata)>=lengthmi-1e-12 for z in ws)/len(ws)
a1=amap[('CONTACT_GAP','MEMBER_TOKEN_ZL3b:A1')];kk=amap[('CONTACT_GAP','FAMILY_1GRAM:K')];ln=amap[('CONTACT_GAP','TOTAL_SYMBOL_COUNT')];mg=amap[('CONTACT_GAP','MULTI_GROUP')]
f82=[x for x in j if x['channel']=='HUMAN_LAYOUT' and x['page']=='f82r'];top=[x for x in f82 if x['array_id']=='F82_BOTTOM_REGION_TOP_ROW' and x['family_expression']];bottom=[x for x in f82 if x['array_id']=='F82_BOTTOM_REGION_BOTTOM_ROW' and x['family_expression']];appa=[x for x in f82 if x['visual_state']=='APPARATUS_POSITION' and x['family_expression']];fig=[x for x in f82 if x['visual_state']=='FIGURE_POSITION' and x['family_expression']]
old=json.loads((R/'gdt002_contact_gap_result.json').read_text());ext=json.loads((R/'gdt002_contact_gap_extension_result.json').read_text());rep=json.loads((R/'gdt002_contact_gap_replication_result.json').read_text())
provenance=read(R/'gdt002_contact_gap_replication_reviewer_provenance.tsv')
ledger=read(R/'GDT002_YOLO_LEDGER.tsv')
hyp=json.loads((R/'gdt002_exploratory_joint_hypotheses.json').read_text())
def ngram_counts(row):
 name=row['formal_feature'];k=int(name.split('GRAM:',1)[0].rsplit('_',1)[1]);token=name.split('GRAM:',1)[1]
 mask=[int(any(token in g for g in x['family_expression'].split('|'))) for x in hard]
 return sum(mask[i] for i in range(len(mask)) if y[i]),sum(mask[i] for i in range(len(mask)) if not y[i])
ngram_rows=[x for x in a if x['channel']=='CONTACT_GAP' and x['feature_level']=='FAMILY_COMPONENT' and 'GRAM:' in x['formal_feature'] and x['formal_feature'].split('_',1)[0]=='FAMILY']
checks={
 'branch_exact':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='yolo/gdt002-visual-grammar-constraints',
 'canonical_files_unchanged':subprocess.run(['git','diff','--quiet','c7874a9','--','VOYNICH_ACTIVE_STATE.md','experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv','experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv'],cwd=R).returncode==0,
 'join_counts':len(j)==80 and len(contact)==27 and len({x['locus'] for x in contact})==27 and Counter(x['visual_state'] for x in contact)=={'CLEAR_GAP':18,'CONTACT':8,'UNCERTAIN':1},
 'canonical_arrays':Counter(x['array_id'] for x in contact)=={'F99V_L1':8,'F99V_L2':6,'F100R_L2':6,'F100V_L1':4,'F89R2_L4':3},
 'no_f84_rows':all(x['page']!='f84r' and not x['locus'].startswith('f84r.') for x in j),
 'contact_formal_coverage':all(x['family_expression'] for x in contact),
 'contact_metadata_invariant':{(x['section'],x['currier'],x['hand'],x['code'],x['kind'],x['grammar_scope']) for x in contact}=={('P','A','1','@Lf','L','DIAGNOSTIC_NONPROSE')},
 'family_stability':sum(x['family_edition_stable']=='1' for x in contact)==27,
 'member_stability':sum(x['member_edition_stable']=='1' for x in contact)==17,
 'atlas_count_unique':len(a)==len({(x['channel'],x['candidate_id']) for x in a})==res['counts']['candidate_atlas_rows'],
 'label_vocab':{x['label'] for x in a}<={'INTERESTING_EXPLORATORY','WEAK','LIKELY_PAGE_CONFOUND','UNSTABLE','NO_SIGNAL'},
 'primary_world_count':len(ws)==2520 and int(a1['exact_permutation_worlds'])==2520,
 'a1_selected_arithmetic':close(a1e,-.6833333333333332) and close(a1p,1/36) and close(a1['within_array_signed_effect'],a1e) and close(a1['exact_signed_p'],a1p) and int(a1['positive_with_feature'])==5 and int(a1['negative_with_feature'])==17 and a1['label']=='WEAK',
 'k_selected_arithmetic':close(ke,5/12) and close(kp,1/12) and close(kk['within_array_signed_effect'],ke) and close(kk['exact_signed_p'],kp) and int(kk['positive_with_feature'])==2 and int(kk['negative_with_feature'])==3 and kk['label']=='WEAK',
 'length_selected_arithmetic':close(lengthmi,.39578823290205056) and close(lengthp,5/84) and close(ln['conditional_mutual_information_bits_per_row'],lengthmi) and close(ln['exact_cmi_p'],lengthp) and ln['label']=='UNSTABLE',
 'drawing_interruption_coupled':int(mg['positive_with_feature'])==2 and int(mg['negative_with_feature'])==0 and 'DIRECT_VISUAL_TRANSCRIPTION_COUPLING' in mg['obvious_confounds'] and mg['label']=='LIKELY_PAGE_CONFOUND',
 'family_boundaries_preserved':all('|' in x['family_expression'] for x in hard if int(x['group_count'])>1) and not any(x['formal_feature'] in {'EXACT_FAMILY:BACACA','EXACT_FAMILY:AQACKA'} for x in a),
 'family_ngrams_within_groups':all(ngram_counts(x)==(int(float(x['positive_with_feature'])),int(float(x['negative_with_feature']))) for x in ngram_rows),
 'joint_edition_robustness_unassigned':all(x['edition_min_mask_jaccard']=='' and x['edition_signed_effects']=='NOT_EVALUATED_POSTSELECTED_JOINT' and 'EDITION_ROBUSTNESS_NOT_EVALUATED' in x['obvious_confounds'] for x in a if x['feature_level']=='JOINT_DEPTH2'),
 'f82_aqa_row_contrast':len(top)==4 and len(bottom)==6 and all(x['family_expression'].startswith('AQA') for x in top) and not any(x['family_expression'].startswith('AQA') for x in bottom),
 'f82_aca_apparatus_contrast':len(appa)==3 and len(fig)==10 and sum('ACA' in x['family_expression'] for x in appa)==3 and sum('ACA' in x['family_expression'] for x in fig)==1,
 'uncertain_retained':sum(x['visual_state']=='UNCERTAIN' for x in contact)==1 and all('AS_CONTACT' in x['uncertainty_dependence'] and 'AS_CLEAR_GAP' in x['uncertainty_dependence'] for x in a if x['channel']=='CONTACT_GAP'),
 'historical_stops_preserved':old['status']==res['historical_gate_statuses_preserved'][0] and ext['status']==res['historical_gate_statuses_preserved'][1] and rep['status']==res['historical_gate_statuses_preserved'][2],
 'reviewer_separation_bound':len(provenance)==2 and {x['reviewer_artifact'] for x in provenance}=={'gdt002_contact_gap_replication_reviewer_b.tsv','gdt002_contact_gap_replication_reviewer_c.tsv'} and all(x['fork_context']=='NONE' and x['source_access']=='BLINDED_PACKET_ONLY' and x['valid_for_consensus']=='1' for x in provenance),
 'ledger_ckpt009':sum(x['checkpoint_id']=='GDT002_CKPT009' and x['status']=='EXPLORATORY_SEARCH_COMPLETE_NO_FROZEN_SEMANTIC_ROLE' for x in ledger)==1,
 'coverage_disclosed':sum(x['channel']=='BFE_ENCLOSURE' and bool(x['family_expression']) for x in j)==29 and sum(x['channel']=='HUMAN_LAYOUT' and x['array_id']=='F80_TOP_TEXT_POSITIONS' and bool(x['family_expression']) for x in j)==8,
 'semantic_roles_unassigned':hyp['evidence_class']=='FORMAL_ASSOCIATION_HYPOTHESIS' and all(x['semantic_role']=='UNASSIGNED' for x in hyp['hypotheses']) and all(x['semantic_roles']=='UNASSIGNED' for x in hyp['joint_worlds']),
 'holdout_sealed':res['holdout']['page']=='f84r' and all(res['holdout'][k] is False for k in ('formal_payload_opened','formal_payload_joined','used_in_search')) and not any(R.glob('gdt002_f84r_*projection.tsv')),
 'input_hashes':all(sha(R/k)==v for k,v in res['inputs'].items()),
 'document_hashes':all(sha(R/k)==v for k,v in res['documents_and_hypotheses'].items()),
 'output_hashes':all(sha(R/k)==v for k,v in res['outputs'].items()),
 'claim_ceiling':all(q in res['claim_ceiling'] for q in ('postselected','No semantic role','translation')),
}
failed=[k for k,v in checks.items() if not v]
out={'artifact':'GDT002_EXPLORATORY_ASSOCIATION_VALIDATION_V1','status':'PASS' if not failed else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),'failed':failed,'result_sha256':sha(R/'gdt002_exploratory_discovery_results.json'),'scope':'Independent canonical-row/count audit, source-boundary n-gram reconstruction, selected A1/K/length/f82 arithmetic, reviewer/ledger/history checks, f84 exclusion, and file-hash integrity. It does not independently reconstruct every postselected joint mask or replay observed-data library selection under each permutation.'}
(R/'gdt002_exploratory_discovery_validation.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print({'status':out['status'],'passed':out['passed'],'total':out['total'],'failed':failed});sys.exit(bool(failed))
