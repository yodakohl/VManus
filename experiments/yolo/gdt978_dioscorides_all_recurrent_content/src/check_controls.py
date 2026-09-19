"""Source-only exact controls; no target material accessed."""
import copy,json
from pathlib import Path
from compile_source import compile_source
from run import solve_job
from validate import source_check,witness_check
E=Path(__file__).resolve().parents[1]
def main():
 src={'records':[dict(id=k,atoms=v) for k,v in [('I.1',['IRIS','SINGLE','XIPHION','IRIS']),('I.2',['IRIS','XIPHION']),('I.3',['IRIS','XIPHION']),('IV.20',['XIPHION','IRIS'])]]};model=compile_source(src)
 assert not source_check(src,model)
 ds={rid:[dict(page=rid,physical_leaf=rid,text=t)] for rid,t in [('I.1','aaba'),('I.2','ab'),('I.3','ab'),('IV.20','ba')]}
 job=dict(model=model,domains=ds,name_cases=[dict(id=0,iris_code='a',xiphion_code='b',xiphion_page='IV.20')],solver_seconds=2)
 controls=[]
 for label,alter,expected in [('singleton_prefix_collision_relaxed',None,'SAT_RECURRENT_PROJECTION'),('zero_length_singleton_forbidden','zero','UNSAT_NONEMPTY_LENGTH'),('same_physical_leaf_forbidden','leaf','UNSAT_SOLVER'),('adjacent_recurrent_insert_forbidden','adjacent','UNSAT_SOLVER')]:
  j=copy.deepcopy(job)
  if alter=='zero':j['domains']['I.1'][0]['text']='aba'
  if alter=='leaf':j['domains']['I.3'][0]['physical_leaf']='I.2'
  if alter=='adjacent':j['domains']['I.2'][0]['text']='acb'
  out=solve_job(j);assert out['status']==expected,(label,out)
  if expected=='SAT_RECURRENT_PROJECTION':
   es,al=witness_check(model,j['domains'],out);assert not es,es
   assert list(out['gaps'].values())==['a'],'This control must exhibit collision with the fixed IRIS code, proving no full-code inference.'
  controls.append(dict(name=label,status=out['status'],expected=expected,version=out.get('version')))
 result=dict(status='PASS',controls=controls,scope='Synthetic necessities and relaxation ceiling only; no manuscript significance')
 (E/'artifacts/CONTROL_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
