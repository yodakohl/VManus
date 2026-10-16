from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(n):return json.loads((B/'artifacts'/n).read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for n in ['REGISTRATION_LOCK.json','CROP_LOCK.json','ANALYSIS_CODE_LOCK.json']:
  for path,h in read(n)['hashes'].items():assert digest(R/path)==h,path
 a=read('STAGE_A.json');assert digest(B/'artifacts/STAGE_A.json')==read('STAGE_A_LOCK.json')['sha256']
 spec=json.loads((B/'src/SPEC.json').read_text());cases=[]
 if not a['complete_and_discriminating']:
  assert not (B/'artifacts/STAGE_B.json').exists();status='REFERENCE_OR_TARGET_CAPACITY_STOP';reason='Prior free templates not complete and discriminating.'
 else:
  b=read('STAGE_B.json');assert b['stage_a_sha256']==digest(B/'artifacts/STAGE_A.json')
  assert {c['target'] for c in b['cases']}==set(spec['target_ids']) and len(b['cases'])==2
  for c in b['cases']:
   expected=spec['expected_high_template'][c['target']];other='REF_B' if expected=='REF_A' else 'REF_A'
   lo=c['low_motif']['status'];hi=c['high_'+expected[-1]]['status'];wrong=c['high_'+other[-1]]['status']
   assert all(x in ['COMPATIBLE','INCOMPATIBLE','UNRESOLVED'] for x in [lo,hi,wrong])
   loc=c['localization']=='SUFFICIENT';contradiction=loc and 'INCOMPATIBLE' in [lo,hi]
   match=loc and lo==hi=='COMPATIBLE' and wrong=='INCOMPATIBLE'
   cases.append({'target':c['target'],'source_id':spec['target_ids'][c['target']],'expected_template':expected,'wrong_template':other,'low_status':lo,'expected_high_status':hi,'wrong_high_status':wrong,'localization_sufficient':loc,'fixed_case_decision':'CONTRADICTED' if contradiction else 'CROSSED_COMPATIBLE' if match else 'UNSCORABLE'})
  status='FIXED_GRAPHIC_COMPOSITION_CONTRADICTED' if any(c['fixed_case_decision']=='CONTRADICTED' for c in cases) else 'CROSSED_GRAPHIC_COMPATIBILITY_BOTH_TARGETS' if all(c['fixed_case_decision']=='CROSSED_COMPATIBLE' for c in cases) else 'REFERENCE_OR_TARGET_CAPACITY_STOP'
  reason='Frozen qualitative motif comparison only; no reinterpretation of uncertain/missing features as visible incompatibility.'
 out={'status':status,'reason':reason,'cases':cases,'source_physical_leaves':1,'observer_count':1,'native_linguistic_units_identified':0,'confirmed_word_meanings':0,'old1348decision':'UNCHANGED_TEMPLATE_CAPACITY_STOP','claim_ceiling':spec['claim_ceiling'],'chronology_limit':'Hash/time receipts record the declared workflow, not external attestation of mental exposure or perception.'}
 (B/'artifacts/RESULT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
