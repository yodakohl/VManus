#!/usr/bin/env python3
"""Post-result closure check; does not pass the original control gate."""
from pathlib import Path
import hashlib,importlib.util,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=B/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
lock=read(B/'LOCK.json')
for p,h in lock['files'].items():assert sha(R/p)==h,p
spec=read(B/'src/SPEC.json');control=read(A/'CONTROLS.json');generated=read(A/'GENERATED_CONTROL.json')
assert control['status']=='STOP_GENERATED_CONTROL_NOT_RECOVERED' and control['generated_status']=='UNKNOWN'
assert generated['result']['status']=='UNKNOWN' and generated['result']['reason'] in ['candidate_checks_cap','wall_seconds','nodes_cap']
for n in ['NATIVE_INPUT.json','RESULT.json','VALIDATION.json','GATE_VALIDATION.json']:assert not(A/n).exists(),n
module_spec=importlib.util.spec_from_file_location('independent_stop_checker',B/'src/validate.py');ind=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(ind)
words=ind.sources(spec);W=sorted(set(words['deot']));assert generated['source_words']==W[:32]
key=generated['planted_key'];assert len(key)==len(set(key.values()))==22
assert ''.join(key[u] for u in generated['encoded_stream'])==''.join(generated['source_words'])
toys=read(A/'TOY_CONTROLS.json')['cases'];assert len(toys)==600
for row in toys:
 wanted='SAT' if ind.oracle(row['stream'],row['words'],row['signs'],'FWD') else 'UNSAT'
 assert row['result']['status']==row['expected_oracle_status']==wanted
 if wanted=='SAT':ind.verify_sat(row['result'],row['stream'],row['words'],row['signs'],'FWD')
review=read(A/'CONTROL_STOP_REVIEW.json')
assert review['native_fit_authorized'] is False
out={'status':'PASS_CONTROL_STOP_RECORD_ONLY','original_control_gate':'FAILED_CAPACITY_UNKNOWN','native_fit_authorized':False,'planted_witness_readback':'PASS_KNOWN_SAT_EXISTS','primary_toys_verified':600,'native_outputs_absent':True,'scientific_code_unchanged':True,'post_result_closure_tool':True,'word_meanings_assigned':0,'lock_sha256':sha(B/'LOCK.json'),'review_sha256':sha(A/'CONTROL_STOP_REVIEW.json'),'verifier_sha256':sha(Path(__file__))}
(A/'VALIDATION_STOP.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out))
