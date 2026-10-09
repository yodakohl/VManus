"""Source/protocol/decision-account validation, not visual truth."""
import hashlib,json,struct
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 lock=json.loads((B/'src/PREREG_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 o=json.loads((B/'artifacts/OBSERVATION.json').read_text());r=json.loads((B/'artifacts/RESULT.json').read_text());raw=json.loads((B/'artifacts/FIXED_RAW_LINES.json').read_text());assert hashlib.sha256((B/'artifacts/OBSERVATION.json').read_bytes()).hexdigest()==r['observation_sha256']
 for reader,lines in raw.items():
  source=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_DISCOVERY_{reader}.json').read_text());expected=[l for l in source['lines'] if l['metadata']['locus'] in ['f77r.25','f77r.31','f77r.32']];assert expected==lines
  target=next(l for l in lines if l['metadata']['locus']=='f77r.32');assert [g[2] for g in target['groups'][:3]]==['qor','ain','cheol'] and target['groups'][0][4]==target['groups'][1][3]=='DEFINITE_SPACE'
  if reader!='RF1b':assert target['metadata']['paragraph_start']=='0' and next(l for l in lines if l['metadata']['locus']=='f77r.25')['metadata']['paragraph_start']=='1'
 from PIL import Image
 assert tuple(o['dimensions_pixels'])==Image.open(R/o['source']).size==(2000,2687)
 assert o['candidate_localization']['status']=='PRESENT' and o['independent_right_limit']['status']=='UNRESOLVED' and o['width_assumptions']['status']=='UNRESOLVED'
 assert all(o['width_assumptions'][k] is None for k in ['numeric_R','numeric_F_H','numeric_F_HB'])
 assert o['decision']==r['status']=='NO_BOUND_GEOMETRY_FOR_GREEDY_TEST' and not r['numeric_packing_test_executed'] and r['models_selected']==[]
 v={'status':'PASS_ACCOUNTING_ONLY','source_hashes':'PASS','source_lines':'PASS','image_dimensions':'PASS','fixed_decision_reduction':'PASS','limits':'Does not validate correctnessofvisualjudgment,wordpixelboxes,writinglimit,counterfactualwidths,meaningsorindependentpalaeography.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
if __name__=='__main__':main()
