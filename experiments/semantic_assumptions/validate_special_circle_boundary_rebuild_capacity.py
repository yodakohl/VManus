#!/usr/bin/env python3
"""Independent compact reconstruction of circle-boundary capacity."""
import csv,hashlib,itertools,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions';I=B/'results/special_circle_text_blind_array_inventory.tsv';S=B/'results/source_native_structural_interlinear_v1.tsv';R=B/'results/special_circle_boundary_rebuild_capacity.json';M=B/'results/special_circle_boundary_rebuild_capacity_report.md';OUT=B/'results/special_circle_boundary_rebuild_capacity_validation.json';OM=B/'results/special_circle_boundary_rebuild_capacity_validation_report.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return (json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def fam(s):return ''.join(re.sub(r'\d+$','',x) for x in s.split())
def main():
 checks=[];src=defaultdict(list)
 for r in csv.DictReader(S.open(encoding='utf-8'),delimiter='\t'):src[r['locus']].append(r)
 for v in src.values():v.sort(key=lambda r:int(r['group_index']))
 inv=list(csv.DictReader(I.open(encoding='utf-8'),delimiter='\t'));c=Counter();kept=[]
 for aid,g in itertools.groupby(inv,key=lambda r:r['array_id']):
  g=list(g)
  for a,b in zip(g,g[1:]):
   c['candidate_linear_adjacencies']+=1
   if a['occupancy_state']!='TRANSCRIBED' or b['occupancy_state']!='TRANSCRIBED':c['nontranscribed_endpoint']+=1;continue
   if a['source_locus'] not in src or b['source_locus'] not in src:c['missing_source_native_endpoint']+=1;continue
   c['both_endpoints_mapped']+=1;lr=(src[a['source_locus']][-1],src[b['source_locus']][0])
   if not all(all(fam(r[k])==r['family_surface'] for k in ('zl_sta_codes','it_sta_codes','rf_sta_codes')) for r in lr):c['all_reading_family_instability']+=1;continue
   c['retained_all_reading_stable']+=1;kept.append((aid,a['physical_folio'],a['page']))
 assert c==Counter({'candidate_linear_adjacencies':459,'both_endpoints_mapped':299,'retained_all_reading_stable':218,'missing_source_native_endpoint':156,'all_reading_family_instability':81,'nontranscribed_endpoint':4});checks.append('edge_partition')
 assert len({x[0] for x in kept})==43 and len({x[2] for x in kept})==23;checks.append('array_page_support')
 fol=Counter(x[1] for x in kept);assert fol==Counter({'f72':62,'f68':41,'f70':30,'f69':28,'f67':26,'f73':16,'f71':15});checks.append('folio_support')
 units={'f67':'A','f68':'A','f69':'B','f70':'B','f71':'C','f72':'C','f73':'D'};bif=Counter(units[x[1]] for x in kept);assert bif==Counter({'C':77,'A':67,'B':58,'D':16}) and 1/2**len(bif)==.0625;checks.append('bifolio_floor')
 stored=json.loads(R.read_text());assert stored['counts']==dict(c) and stored['retained']['edges']==218 and stored['retained']['minimum_one_sided_sign_p']==.0625;checks.append('stored_counts')
 assert stored['gates']=={'at_least_200_retained_edges':True,'at_least_40_retained_arrays':True,'all_seven_extant_folios_represented':True,'at_least_seven_independent_bifolio_units':False,'one_sided_bifolio_sign_floor_at_most_0_01':False,'zero_boundary_scores_effects_or_null_worlds':True};checks.append('gates')
 assert stored['access']=={'source_native_endpoint_families_accessed_for_all_reading_stability':True,'boundary_scores_computed':False,'boundary_effects_computed':False,'null_worlds_run':0,'endpoint_identities_emitted':False,'fully_analyst_blind':False,'development_diagnostic_anonymous_endpoint_pairs_displayed':20};checks.append('access_disclosure')
 assert 'minimum p **.0625**' in M.read_text() and 'No reset-likeness score' in M.read_text();checks.append('report')
 v={'experiment':'SPECIAL_CIRCLE_BOUNDARY_REBUILD_CAPACITY_VALIDATION','schema':'SPECIAL_CIRCLE_BOUNDARY_REBUILD_CAPACITY_VALIDATION_V1','status':'PASS_8_CHECK_INDEPENDENT_RECONSTRUCTION','check_count':8,'checks':checks,'validated_result_sha256':sha(R),'validated_report_sha256':sha(M),'claim_ceiling':'Validation confirms only the four-bifolio capacity stop and supplies no translation.'};OUT.write_bytes(canon(v));OM.write_text('# Special-circle boundary rebuild capacity validation\n\nStatus: **PASS — 8 independent checks**.\n\nIndependent code reconstructs the edge partition, supports, bifolio floor, gates, access disclosure, and report. It supplies no translation.\n')
if __name__=='__main__':main()
