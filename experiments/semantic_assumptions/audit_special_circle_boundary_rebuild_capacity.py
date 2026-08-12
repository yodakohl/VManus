#!/usr/bin/env python3
"""Score-blind capacity for a new special-circle boundary rebuild."""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions'
METHOD=B/'SPECIAL_CIRCLE_BOUNDARY_REBUILD_CAPACITY_METHOD.md';INV=B/'results/special_circle_text_blind_array_inventory.tsv';SRC=B/'results/source_native_structural_interlinear_v1.tsv';BIF=B/'results/public_circle_bifolio_class_capacity.json';OUT=B/'results/special_circle_boundary_rebuild_capacity.json';REPORT=B/'results/special_circle_boundary_rebuild_capacity_report.md'
E=('zl_sta_codes','it_sta_codes','rf_sta_codes')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return (json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def fam(s):return ''.join(re.sub(r'\d+$','',x) for x in s.split())
def stable(r):return all(fam(r[k])==r['family_surface'] for k in E)
def build():
 inv=list(csv.DictReader(INV.open(encoding='utf-8',newline=''),delimiter='\t'));srcrows=list(csv.DictReader(SRC.open(encoding='utf-8',newline=''),delimiter='\t'));by=defaultdict(list)
 for r in srcrows:by[r['locus']].append(r)
 for v in by.values():v.sort(key=lambda r:int(r['group_index']))
 counts=Counter();kept=[]
 for aid,g in itertools.groupby(inv,key=lambda r:r['array_id']):
  g=list(g)
  for a,b in zip(g,g[1:]):
   counts['candidate_linear_adjacencies']+=1
   if a['occupancy_state']!='TRANSCRIBED' or b['occupancy_state']!='TRANSCRIBED':counts['nontranscribed_endpoint']+=1;continue
   if a['source_locus'] not in by or b['source_locus'] not in by:counts['missing_source_native_endpoint']+=1;continue
   counts['both_endpoints_mapped']+=1
   left,right=by[a['source_locus']][-1],by[b['source_locus']][0]
   if not(stable(left) and stable(right)):counts['all_reading_family_instability']+=1;continue
   counts['retained_all_reading_stable']+=1;kept.append((aid,a['physical_folio'],a['page']))
 bif=json.loads(BIF.read_text());assert bif['scope']['bifolio_units']==4
 units={'f67':'BIFOLIO_F67_F68','f68':'BIFOLIO_F67_F68','f69':'BIFOLIO_F69_F70','f70':'BIFOLIO_F69_F70','f71':'BIFOLIO_F71_F72','f72':'BIFOLIO_F71_F72','f73':'BIFOLIO_F73_F74_MISSING'}
 folios=Counter(x[1] for x in kept);bifs=Counter(units[x[1]] for x in kept);floor=1/(2**len(bifs))
 gates={'at_least_200_retained_edges':len(kept)>=200,'at_least_40_retained_arrays':len({x[0] for x in kept})>=40,'all_seven_extant_folios_represented':len(folios)==7,'at_least_seven_independent_bifolio_units':len(bifs)>=7,'one_sided_bifolio_sign_floor_at_most_0_01':floor<=.01,'zero_boundary_scores_effects_or_null_worlds':True}
 result={'experiment':'SPECIAL_CIRCLE_BOUNDARY_REBUILD_CAPACITY','schema':'SPECIAL_CIRCLE_BOUNDARY_REBUILD_CAPACITY_V1','status':'STOP_SCORE_BLIND_FOUR_BIFOLIO_INFERENCE_FLOOR','decision':'DO_NOT_CALIBRATE_OR_SCORE_NEW_ARRAY_BOUNDARY_REBUILD','counts':dict(counts),'retained':{'edges':len(kept),'arrays':len({x[0] for x in kept}),'pages':len({x[2] for x in kept}),'extant_folios':len(folios),'bifolio_units':len(bifs),'edges_by_folio':dict(sorted(folios.items())),'edges_by_bifolio':dict(sorted(bifs.items())),'one_sided_complete_sign_orbit_size':2**len(bifs),'minimum_one_sided_sign_p':floor},'gates':gates,'access':{'source_native_endpoint_families_accessed_for_all_reading_stability':True,'boundary_scores_computed':False,'boundary_effects_computed':False,'null_worlds_run':0,'endpoint_identities_emitted':False,'fully_analyst_blind':False,'development_diagnostic_anonymous_endpoint_pairs_displayed':20},'inputs':{str(p.relative_to(ROOT)):sha(p) for p in (METHOD,INV,SRC,BIF)},'claim_ceiling':'Capacity stops a new special-circle boundary reconstruction at four independent bifolio units. It establishes no graphical record boundary, slot function, word, plaintext, meaning, or translation.'}
 report=f"# Special-circle boundary rebuild capacity\n\nStatus: **STOP — FOUR-BIFOLIO INFERENCE FLOOR**.\n\nOf **{counts['candidate_linear_adjacencies']}** linear array adjacencies, **{counts['both_endpoints_mapped']}** have two mapped transcribed endpoints and **{len(kept)}** retain exact source-native family agreement across ZL3b/IT2a/RF1b. They span **{len(set(x[0] for x in kept))}** arrays, **{len(set(x[2] for x in kept))}** pages, and all seven extant folios.\n\nThose folios are only four bifolio production units. A complete one-sided bifolio sign orbit has size 16 and minimum p **.0625**, above the frozen `.01` requirement. No reset-likeness score, boundary effect, or null world was computed. A development diagnostic had displayed 20 anonymous endpoint pairs, so this audit is score-blind rather than fully analyst-blind.\n\nDo not treat {len(kept)} dependent edges as independent evidence. This establishes no graphical record boundary, slot value, word, plaintext, meaning, or translation.\n"
 return result,report
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r,m=build()
 if a.write:OUT.write_bytes(canon(r));REPORT.write_text(m,encoding='utf-8')
 else:print(canon(r).decode(),end='')
if __name__=='__main__':main()
