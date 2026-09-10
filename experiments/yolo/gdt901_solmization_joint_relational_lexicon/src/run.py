#!/usr/bin/env python3
"""Complete necessary domains for all ten preregistered morphology cases."""
import hashlib,json
from pathlib import Path
from source import load
from role_source import CASES,compile_case
from domains import build
BASE=Path(__file__).resolve().parents[1]
def main():
 sp=BASE/'artifacts/SOURCE_INPUT.json';tp=BASE/'artifacts/TARGET_INPUT.json';mp=BASE/'artifacts/MODEL_SPEC.json'
 source=load(sp);target=json.loads(tp.read_text());spec=json.loads(mp.read_text());assert spec['cases']==CASES
 results=[]
 for panel,rows in target['panels'].items():
  for i,case in enumerate(CASES):
   compiled=compile_case(source,case);r=build(compiled,rows)
   file=BASE/'artifacts'/f'DOMAINS_{panel}_{i:02}.json';file.write_text(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
   results.append({'panel':panel,'case':i,'role_partition':case,'status':r['status'],
       'available':r['available'],'required':r['required'],'form_count':len(compiled['atoms']),
       'empty_forms':r.get('empty_atoms',[]),'artifact':file.name,'artifact_sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 complete=all(r['status'] in ['CAPACITY_STOP','EMPTY_ATOM_DOMAINS_UNSAT'] for r in results)
 out={'schema':'GDT901_COMPLETE_ROLE_DOMAIN_RESULT_V1','source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'model_spec_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),
      'status':'ALL_TEN_MORPHOLOGY_CASES_EXCLUDED' if complete else 'FULL_MORPHOLOGICAL_SOLVER_REQUIRED',
      'model_excluded_in_all_panels':complete,'cases':results,
      'claim_ceiling':'Exactroot-affix/operationalprojection/head/globalbackground/scope conjunction only; no general music or meaning conclusion.'}
 (BASE/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'cases':[{'panel':r['panel'],'case':r['case'],'status':r['status'],'empty_forms':r['empty_forms']} for r in results]}))
if __name__=='__main__':main()
