#!/usr/bin/env python3
"""Independent validation for clock-half and fRos alias capacity."""

from __future__ import annotations

import csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv';I=ROOT/'experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv';P=ROOT/'experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv';X=ROOT/'transcription/voynich_stolfi25e1_lines.tsv';R=ROOT/'experiments/semantic_assumptions/results/post_direction_transfer_capacity.json';O=ROOT/'experiments/semantic_assumptions/results/post_direction_transfer_capacity_validation.json'
READINGS={'IT2a','RF1b','ZL3b'}; OBJ=r'(?:plant|root(?:s)?|leaf|leaves|stem|nymph(?:s)?|pond|channel|funnel|man|container|moon|sun|star(?:s)?|road|rosette|canopy|triangle|spikes?)'
def load(p):return list(csv.DictReader(p.open(newline='',encoding='utf-8'),delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads(R.read_text());a=load(A);old={x['source_locus'] for x in load(P)};cov=defaultdict(set)
 for x in load(I):cov[x['locus']].add(x['edition'])
 clock=re.compile(r'\b(?:at|sector at|moon at|star at)\s*(\d{1,2}):(\d{2})\b',re.I);ctx=re.compile(r'circle|band|diagram|sector|star|moon|rosette|radial|nymph|label',re.I);rows=[]
 for x in a:
  if x['certainty']!='UNHEDGED' or x['relation_scope']!='EXACT_LOCAL_COMMENT' or x['source_locus'] in old or cov[x['source_locus']]!=READINGS or not ctx.search(x['unit_description']+' '+x['local_comment']):continue
  pos={(int(h)%12)*60+int(m) for h,m in clock.findall(x['local_comment'])}
  if len(pos)==1 and next(iter(pos)) not in (0,360):
   m=next(iter(pos));rows.append((x,'EAST_HALF' if m<360 else 'WEST_HALF'))
 g=defaultdict(list)
 for x,c in rows:g[(x['page'],x['unit'],x['normalized_code'],x['object_tags'])].append((x,c))
 matched={k:v for k,v in g.items() if len({c for x,c in v})==2};folios={re.match(r'^f\d+',k[0]).group() for k in matched}
 cross=defaultdict(list)
 for x in load(X):cross[x['source_locus']].append(x)
 ros=[x for x in a if x['page']=='f85v2'];mapped=[cross[x['source_locus']] for x in ros];strict=[]
 for x in ros:
  if x['certainty']!='UNHEDGED' or x['relation_scope']!='EXACT_LOCAL_COMMENT':continue
  t=x['local_comment'].lower();e=bool(re.search(rf'\beast of (?:the )?{OBJ}\b',t));w=bool(re.search(rf'\bwest of (?:the )?{OBJ}\b',t));mix=bool(re.search(r'\beast(?:ward|wards)?\b',t)) and bool(re.search(r'\bwest(?:ward|wards)?\b',t))
  if not mix and e!=w:strict.append((x,'EAST' if e else 'WEST'))
 checks={'hashes':s['inputs']=={'annotations':sha(A),'interlinear':sha(I),'prior_panel':sha(P),'manual_line_crosswalk':sha(X)},'clock_58':len(rows)==58,'clock_classes':Counter(c for x,c in rows)=={'EAST_HALF':25,'WEST_HALF':33},'clock_6_units_49_rows':len(matched)==6 and sum(map(len,matched.values()))==49,'clock_two_folios':folios=={'f67','f68'},'rosette_158':len(ros)==158,'all_unique_fRos':all(len(v)==1 and v[0]['page']=='fRos' for v in mapped),'all_code_exact':all(x['normalized_code']==v[0]['code'] for x,v in zip(ros,mapped)),'all_two_reading_only':Counter(tuple(sorted(cov[v[0]['locus']])) for v in mapped)=={('RF1b','ZL3b'):158},'strict_two_west':[(x['source_locus'],c) for x,c in strict]==[('f85v2.56','WEST'),('f85v2.138','WEST')],'zero_rosette_contrast':s['rosette_alias']['matched_strata']==0,'transfer_stopped':s['decision']['bound_e_transfer_authorized'] is False and s['voynich_feature_scored'] is False}
 checks={k:bool(v) for k,v in checks.items()};out={'status':'PASS' if all(checks.values()) else 'FAIL','checks_passed':sum(checks.values()),'checks_total':len(checks),'checks':checks,'result_sha256':sha(R)};O.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
