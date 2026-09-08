"""Post-observation mechanical rendering of the preregistered location rule.
No native judgement is made by this script.
"""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
a=json.loads((B/'artifacts/VIEWER_A.json').read_text())['observations'];b=json.loads((B/'artifacts/VIEWER_B.json').read_text())['observations']
old={'f67r2.72':'LEFT_CIRCULAR_BAND','f67r2.73':'RIGHT_CIRCULAR_BAND','f67r2.74':'UNRESOLVED'};out=[]
for locus,prior in old.items():
 agreed=a[locus]['localized']and b[locus]['localized']and a[locus]['region']==b[locus]['region'];region=a[locus]['region']if agreed else'UNRESOLVED'
 verdict='OLD_DEFINITE_WRITTEN_LOCATION_CONTRADICTED'if agreed and prior!='UNRESOLVED'and region!=prior else'WRITTEN_LOCATION_NARROWED_REFERENT_UNRESOLVED'if agreed and prior=='UNRESOLVED'else'NO_LOCATION_CORRECTION'
 out.append(dict(locus=locus,old_definite_written_region=prior,agreed_written_region=region,verdict=verdict,semantic_referent='UNRESOLVED',scope='Written position only; do not infer a new depicted owner or revise transcription.'))
sources={p:hashlib.sha256((R/p).read_bytes()).hexdigest()for p in ['experiments/yolo/sidequest_theory_candidates_v71/V71_R1_build_owner_map.py','experiments/yolo/sidequest_theory_candidates_v71/build_v71_r3_owner_ledger.py','experiments/yolo/sidequest_theory_candidates_v71/V71_R3_TECHNICAL_REPORT.md']}
(B/'artifacts/CORRECTIONS.json').write_text(json.dumps({'status':'TWO_OLD_DEFINITE_PLACEMENTS_CONTRADICTED','rule':'Predeclared native agreement rule rendered after observations; no image analysis by software.','records':out,'historical_sources':sources},indent=2,sort_keys=True)+'\n');print(json.dumps(out))
