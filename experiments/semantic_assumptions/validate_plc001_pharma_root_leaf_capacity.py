#!/usr/bin/env python3
"""Independent compact validation of PLC001 capacity stop."""
from __future__ import annotations
import csv,hashlib,itertools,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions';R=B/'results';ANN=R/'existing_human_exact_locus_annotations.tsv';SRC=R/'source_sta_family_consensus_groups.tsv';RES=R/'plc001_pharma_root_leaf_capacity.json';REP=R/'plc001_pharma_root_leaf_capacity_report.md';OUT=R/'plc001_pharma_root_leaf_capacity_validation.json';OM=R/'plc001_pharma_root_leaf_capacity_validation_report.md';ED=('zl_sta_codes','it_sta_codes','rf_sta_codes')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fam(s):return ''.join(re.sub(r'\d+$','',x) for x in s.split())
def main():
 src=defaultdict(list)
 for r in csv.DictReader(SRC.open(),delimiter='\t'):src[r['locus']].append(r)
 for v in src.values():v.sort(key=lambda x:int(x['consensus_group_index']))
 got=[];parsed=0
 for r in csv.DictReader(ANN.open(),delimiter='\t'):
  if (r['normalized_code'],r['certainty'],r['relation_scope'])!=('@Lf','UNHEDGED','EXACT_LOCAL_COMMENT'):continue
  c=r['local_comment'];defs={m.group(1):m.group(2).strip().lower() for m in re.finditer(r'plant\s+(<f[^>]+>\[[^]]+\])\s*-\s*(.*?)(?=\s+(?:East|West|Above|Below|Near|Within|Against|On top|Under|Between)\b|[.;]|$)',c,re.I)};ms=list(re.finditer(r'\b(?:East|West|Above|Below|Near|Within|Against|On top|Under|Between)\b',c,re.I));rel=c[ms[-1].start():] if ms else '';refs=list(dict.fromkeys(re.findall(r'plant\s+(<f[^>]+>\[[^]]+\])',rel,re.I)))
  if len(refs)!=1 or refs[0] not in defs or re.search(r'\bbetween\b',rel,re.I):continue
  d=defs[refs[0]];root=bool(re.search(r'\b(?:root|roots|tuber|tubers|bulb|bulbous)\b',d));leaf=bool(re.search(r'\b(?:leaf|leaves)\b',d));other=bool(re.search(r'\b(?:flower|flowers|stem|stems|twig|twigs|sprout|sprouts|berries|infloresc)',d));state='ROOT_ONLY' if root and not leaf and not other else ('LEAF_BEARING' if leaf else None)
  if not state:continue
  parsed+=1;g=src.get(r['locus'],[])
  if g and all(x['strict_zero_alternative']=='1' and all(fam(x[k])==x['family_surface'] for k in ED) for x in g):got.append((state,re.match(r'f\d+',r['page']).group(),r['page'],r['locus'],tuple(int(x['symbol_count']) for x in g)))
 checks=[];assert parsed==30;checks.append('parsed_30');assert Counter(x[0] for x in got)==Counter({'LEAF_BEARING':18,'ROOT_ONLY':6});checks.append('stable_24_partition');assert sorted({x[1] for x in got if x[0]=='ROOT_ONLY'})==['f102','f89','f99'];checks.append('root_folios');assert sorted({x[1] for x in got if x[0]=='LEAF_BEARING'})==['f100','f102','f88','f89'];checks.append('leaf_folios');assert sorted(f for f in {x[1] for x in got} if {x[0] for x in got if x[1]==f}=={'ROOT_ONLY','LEAF_BEARING'})==['f102','f89'];checks.append('mixed_folios');assert sorted(p for p in {x[2] for x in got} if {x[0] for x in got if x[2]==p}=={'ROOT_ONLY','LEAF_BEARING'})==['f89r1'];checks.append('mixed_page');assert not [(a,b) for a,b in itertools.combinations(got,2) if a[1]==b[1] and a[0]!=b[0] and a[4]==b[4]];checks.append('zero_length_pairs');stored=json.loads(RES.read_text());assert stored['counts']['stable_retained']==24 and stored['access']=={'association_scores_computed':False,'label_surface_or_family_accessed':False,'null_worlds_run':0,'root_or_role_accessed':False} and 'There are **0**' in REP.read_text();checks.append('stored_stop')
 v={'experiment':'PLC001_CAPACITY_VALIDATION','schema':'PLC001_CAPACITY_VALIDATION_V1','status':'PASS_8_CHECK_INDEPENDENT_RECONSTRUCTION','check_count':8,'checks':checks,'validated_result_sha256':sha(RES),'validated_report_sha256':sha(REP),'claim_ceiling':'Validation confirms only the filler-blind capacity stop and supplies no translation.'};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');OM.write_text('# PLC001 capacity validation\n\nStatus: **PASS — 8 independent checks**.\n\nIndependent code reconstructs the parser panel, state and folio support, mixed support, zero exact-length pairs, and sealed access contract. It supplies no translation.\n')
if __name__=='__main__':main()
