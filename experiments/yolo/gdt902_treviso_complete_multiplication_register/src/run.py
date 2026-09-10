#!/usr/bin/env python3
import gzip,hashlib,json,time
from pathlib import Path
from domains import build
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 start=time.monotonic();sp=BASE/'artifacts/SOURCE_INPUT.json';tp=BASE/'artifacts/TARGET_INPUT.json'
 assert sha(sp)=='aec96b65f3bc4248fd6979a3e69556720ad841523eca5c85d52ef6ce1c3e87cf'
 assert sha(tp)=='850582c870458a96ee5b8a541e280f9bba3c56732f2432fe362f08289820f194'
 source=json.loads(sp.read_text());target=json.loads(tp.read_text());panels=[]
 for panel,rows in target['panels'].items():
  r=build(source,rows);p=BASE/'artifacts'/('DOMAINS_'+panel+'.json.gz');p.write_bytes(gzip.compress((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
  panels.append({'panel':panel,'status':r['status'],'available':len(rows),'empty_atoms':r.get('empty_atoms',[]),'surviving_operator_pairs':len(r.get('operator_pairs',[])),'artifact':p.name,'artifact_sha256':sha(p)})
 excluded=all(p['status'] in ['CAPACITY_STOP','EMPTY_ATOM_DOMAINS_UNSAT','OPERATOR_PAIR_DOMAINS_UNSAT'] for p in panels)
 out={'schema':'GDT902_COMPLETE_NECESSARY_DOMAIN_RESULT_V1','status':'ALL_PANELS_EXCLUDED_BY_NECESSARY_CONSTRAINTS' if excluded else 'FULL_DECIMAL_SOLVER_REQUIRED','source_sha256':sha(sp),'target_sha256':sha(tp),'panels':panels,'elapsed_seconds':time.monotonic()-start,'model_excluded_in_all_panels':excluded,'claim_ceiling':'The fixed44equation/decimal/globalbackground/wholeparagraph conjunction only; no confirmed numeral or general arithmetic conclusion.'}
 (BASE/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
