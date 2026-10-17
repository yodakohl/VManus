#!/usr/bin/env python3
"""Independent packed-Int search; explicit inherited source/certificate checking."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
OLD='experiments/yolo/gdt1431_arbitrary_word_order_syriac_key/src/validate.py'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=A/n
 if p.exists():assert read(p)==x,'Refuse changed overwrite '+n
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def config():
 pins=read(E/'LOCK.json')['files'];assert isinstance(pins,dict)
 for path,h in pins.items():assert not Path(path).is_absolute() and sha(ROOT/path)==h,path
 s=read(E/'src/SPEC.json')
 for path,h in s['predecessor_sha256'].items():assert sha(ROOT/path)==h,path
 assert s['mode']=='PACKED_BAG_KEY' and s['native_groups']==59 and s['control_groups']==32
 assert len(s['signs'])==len(set(s['signs']))==22
 assert s['independent_search']=={'preparation_seconds':20,'solver_seconds':20}
 assert s['primary_search']=={'preparation_seconds':20,'solver_seconds':20}
 assert OLD in s['predecessor_sha256'] and OLD in pins
 publication=read(E/'REGISTRATION_PUBLICATION.json')
 assert publication['status']=='PUSH_VERIFIED' and publication['lock_sha256']==sha(E/'LOCK.json')
 assert publication['commit'] and isinstance(publication['verified_epoch'],(int,float))
 for path in [E/'src/integer_engine.py',Path(__file__),E/'src/SPEC.json']:
  assert path.relative_to(ROOT).as_posix() in pins
 lib=load_module(ROOT/OLD,'inherited1431_certificates')
 return s,lib

def search(s,groups,W):
 engine=load_module(E/'src/integer_engine.py','independent_packed_integer')
 start=time.monotonic();r=engine.solve(groups,W,s['signs'],s['independent_search'])
 return r,time.monotonic()-start

def check_wrapper(z,path):
 assert z['input_sha256']==sha(path)
 assert z['result']['status'] in ['SAT','UNSAT','UNKNOWN']
 assert z['status'] in [z['result']['status'],'PASS' if z['result']['status']=='SAT' else 'STOP']
 assert z['lock_sha256']==sha(E/'LOCK.json')
 assert z['started_epoch']>=read(E/'REGISTRATION_PUBLICATION.json')['verified_epoch']
def gate_report(s,lib,W,c):
 a=read(A/'CONTROL_PRIMARY.json');b=read(A/'INDEPENDENT_CONTROL.json')
 for z in [a,b]:
  check_wrapper(z,ROOT/s['control_input'])
  if z['result']['status']=='SAT':lib.cert(z['result'],c['groups'],set(W),s['signs'])
 lib.cert({'status':'SAT','key':c['planted_key'],'words':c['planted_words']},c['groups'],set(W),s['signs'])
 statuses=[a['result']['status'],b['result']['status']];invalid='UNSAT' in statuses;passed=statuses==['SAT','SAT']
 if not passed:assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
 return {'status':'PASS' if passed else 'STOP','reason':'BOTH_ANY_CERTIFICATES_VERIFIED' if passed else 'INVALID_KNOWN_POSITIVE_UNSAT' if invalid else 'CONTROL_SEARCH_UNKNOWN',
   'known_positive_result_invalid':invalid,'primary_status':statuses[0],'independent_status':statuses[1],
   'control_input_sha256':sha(ROOT/s['control_input']),'primary_sha256':sha(A/'CONTROL_PRIMARY.json'),
   'independent_sha256':sha(A/'INDEPENDENT_CONTROL.json'),'lock_sha256':sha(E/'LOCK.json'),
   'scope':'ANY carry-free multiset certificate only; no exact recovery or uniqueness. Two formulations share Z3. Inherited1431 direct certificate/source helpers reused explicitly.'}
def gate():
 s,lib=config();_,W,c,_=lib.inputs(s);assert not (A/'INDEPENDENT_CONTROL.json').exists()
 assert (A/'CONTROL_PRIMARY.json').exists()
 started=time.time();r,elapsed=search(s,c['groups'],W)
 if r['status']=='SAT':lib.cert(r,c['groups'],set(W),s['signs'])
 save('INDEPENDENT_CONTROL.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'started_epoch':started,'input_sha256':sha(ROOT/s['control_input']),'source_projection_sha256':sha(ROOT/s['source_projection']),'lock_sha256':sha(E/'LOCK.json')})
 g=gate_report(s,lib,W,c);save('GATE_VALIDATION.json',g);print(json.dumps(g))
def native():
 s,lib=config();_,W,c,n=lib.inputs(s);g=gate_report(s,lib,W,c)
 assert g==read(A/'GATE_VALIDATION.json') and g['status']=='PASS'
 assert not (A/'INDEPENDENT_RESULT.json').exists()
 started=time.time();r,elapsed=search(s,n['groups'],W)
 if r['status']=='SAT':lib.cert(r,n['groups'],set(W),s['signs'])
 save('INDEPENDENT_RESULT.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'started_epoch':started,'input_sha256':sha(ROOT/s['native_input']),'source_projection_sha256':sha(ROOT/s['source_projection']),'lock_sha256':sha(E/'LOCK.json')})
 print(json.dumps({'independent_status':r['status']}))
def validate():
 s,lib=config();_,W,c,n=lib.inputs(s);g=gate_report(s,lib,W,c);assert g==read(A/'GATE_VALIDATION.json');inverse={}
 if g['status']!='PASS':
  assert read(A/'NATIVE_STOP.json')['native_cases_executed']==0
  final='INVALID_CONTROL_UNSAT' if g['known_positive_result_invalid'] else 'CONTROL_STOP_NO_NATIVE_SEARCH';statuses={};executed=False
 else:
  a=read(A/'RESULT.json');b=read(A/'INDEPENDENT_RESULT.json');statuses={};executed=True
  for label,z in [('primary',a),('independent',b)]:
   check_wrapper(z,ROOT/s['native_input']);r=z['result'];statuses[label]=r['status']
   if r['status']=='SAT':lib.cert(r,n['groups'],set(W),s['signs']);inverse[label]=lib.inverses(r,n,W)
  ss=set(statuses.values())
  final='INVALID_DISAGREEMENT' if ss=={'SAT','UNSAT'} else 'SAT_CAPACITY_UNASSESSED' if 'SAT' in ss else 'DUAL_FORMULATION_UNSAT_ARBITRARY_WORD_ORDER' if ss=={'UNSAT'} else 'UNKNOWN_OPEN'
 decision={'status':final,'confirmed_words':0,'native_executed':executed,'native_cases':int(executed),'engine_statuses':statuses,
  'gate_status':g['status'],'source_projection_sha256':sha(ROOT/s['source_projection']),'native_input_sha256':sha(ROOT/s['native_input']),
  'lock_sha256':sha(E/'LOCK.json'),'claim_ceiling':s['claim_ceiling']}
 save('FINAL_DECISION.json',decision)
 if inverse:save('INVERSE_WORD_SETS.json',{'status':'UNASSESSED_FULL_PREIMAGE_SETS','source_projection_sha256':sha(ROOT/s['source_projection']),'by_engine':inverse})
 save('VALIDATION.json',{'status':'INVALID_ENGINE_RESULT' if final.startswith('INVALID') else 'PASS_PACKED_INTEGER_AND_CERTIFICATE_ACCOUNTING',
  'validator_sha256':sha(Path(__file__)),'integer_engine_sha256':sha(E/'src/integer_engine.py'),'inherited_helper_sha256':sha(ROOT/OLD),
  'decision_sha256':sha(A/'FINAL_DECISION.json'),'control_gate':g,'native_engine_statuses':statuses,'full_inverse_keys':sorted(inverse),
  'limits':['Unchanged1431 inputs/cert/inverses reused as pinned functions, not independently re-authored extraction.',
            'New independent unbounded-integer packed equality engine; primary bitvector encoding not imported.',
            'Both formulations share Z3; no solver-engine diversity or semantic confirmation.',
            'The original1431 preparation stop remains unchanged; no native result is inferred from a control certificate.']})
 print(json.dumps(decision))
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for mode in ['fixtures','gate','native','validate']:g.add_argument('--'+mode,action='store_true')
 a=p.parse_args()
 if a.fixtures:
  receipt=load_module(E/'src/integer_engine.py','integer_sourcefree').fixtures()
  save('INDEPENDENT_FIXTURES.json',receipt);print(json.dumps(receipt))
 elif a.gate:gate()
 elif a.native:native()
 else:validate()
if __name__=='__main__':main()
