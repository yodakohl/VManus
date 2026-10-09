"""Reduce frozen visual observations; no automatic image interpretation."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 for p,h in json.loads((B/'src/PREREG_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 o=json.loads((B/'artifacts/OBSERVATION.json').read_text());s=[o[k]['status'] for k in ['candidate_localization','independent_right_limit','width_assumptions']];assert all(x in ['PRESENT','ABSENT','UNRESOLVED'] for x in s)
 status='LOCALIZATION_UNRESOLVED' if s[0]!='PRESENT' else ('MEASUREMENT_CAPACITY' if all(x=='PRESENT' for x in s) else 'NO_BOUND_GEOMETRY_FOR_GREEDY_TEST');assert status==o['decision']
 out={'status':status,'observation_sha256':hashlib.sha256((B/'artifacts/OBSERVATION.json').read_bytes()).hexdigest(),'prerequisite_statuses':s,'numeric_packing_test_executed':False,'models_selected':[],'claim_ceiling':'Oneinformedcached-imagecapacityobservation;no widthestimate,entryallomorphy,nonbreakinggrammar,meaningorindependentphysicalconfirmation.'};(B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
