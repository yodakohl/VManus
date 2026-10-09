from pathlib import Path
import sys,importlib.util,json,hashlib,os,copy,random,math,time
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';OLD=ROOT/'experiments/yolo/gdt1194_paired_tail_orthography';sys.path.insert(0,str(OLD/'src'));spec=importlib.util.spec_from_file_location('notation',OLD/'src/run.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
def save(n,o):(A/n).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def solve(counts):
 z=x.z3;s=z.Solver();s.set(timeout=10000,random_seed=1195);vars=[[z.Bool(f'ctx{c}_{i}') for i in range(6)] for c in range(13)]
 for row in vars:s.add(z.PbEq([(v,1) for v in row],1))
 for b in range(4):
  total=z.Sum([z.If(vars[c][i],int(counts[b,c,i]),0) for c in range(13) for i in range(6)]);s.add(total>=2922,total<=3364)
 status=s.check();out={'status':str(status),'choice':None,'reason':s.reason_unknown() if status==z.unknown else None}
 if status==z.sat:
  model=s.model();choice=[next(i for i in range(6) if z.is_true(model.eval(vars[c][i]))) for c in range(13)];values=[sum(int(counts[b,c,i]) for c,i in enumerate(choice)) for b in range(4)];assert all(2922<=n<=3364 for n in values);out.update(choice=choice,book_counts=values,verified=True)
 return out

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source,tables,targets,base,inner,cache=x.prepare();fast=x.Fast(cache,base);candidates,qcounts=fast.candidates(targets);assert candidates==json.loads((OLD/'artifacts/LENGTH_CANDIDATES.json').read_text());counts=fast.y_counts(2);witness=solve(counts);save('CAPACITY.json',{'counts':counts.tolist(),'witness':witness});print(json.dumps(witness),flush=True);result={'experiment':'GDT1195','witness':witness,'best':None,'selected':False,'status':'STOP_NO_VERIFIED_CAPACITY'}
 if witness['choice'] is None:save('RESULT.json',result);return
 p=x.initial_params(2,candidates[0],witness['choice'],base);assert x.legal(p);result['parity_checks']=x.parity(fast,inner,source,p,candidates,targets,1);print(json.dumps({'stage':'PARITY','checks':result['parity_checks']}),flush=True);rng=random.Random(119401);energy,full,*_=x.evaluate(fast,p,targets);best={'params':copy.deepcopy(p),'energy':energy,'full_pass':full,'step':-1};accepted=invalid=0;start=time.monotonic();log=[];attempted=0;budget_stop=False
 for step in range(6000):
  if full:break
  if time.time()>=1791190380:budget_stop=True;break
  attempted=step+1;trial=x.mutate(p,candidates,rng)
  if not x.legal(trial):invalid+=1;continue
  value,passed,*_=x.evaluate(fast,trial,targets)
  if passed or value<best['energy']:best={'params':copy.deepcopy(trial),'energy':value,'full_pass':passed,'step':step}
  if passed:full=True;break
  temp=max(1e-6,.03*(1-step/6000))
  if value<=energy or rng.random()<math.exp(min(0,(energy-value)/temp)):p=trial;energy=value;accepted+=1
  if step%250==0:
   rec={'step':step,'best_energy':best['energy'],'seconds':round(time.monotonic()-start,1)};log.append(rec);save('SEARCH_LOG.json',{'log':log,'best':best});print(json.dumps(rec),flush=True)
 best['search']={'proposals':attempted,'accepted':accepted,'invalid':invalid,'seed':119401,'seconds':time.monotonic()-start,'log':log,'budget_stop':budget_stop};writer=x.Writer(inner,best['params']);e,full,met,comp,extra=x.evaluate(fast,best['params'],targets);roundtrips=0
 for b in x.BOOKS:
  ps,_=x.w.engine.pages(writer,source[b]);x.w.fast.close(x.w.engine.measure(ps),met[b]);roundtrips+=len(source[b]);(A/(b+'.txt')).write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in ps)+'\n')
 best.update(metrics=met,comparison=comp,extra=extra,complete_recipe_roundtrips=roundtrips);result.update(best=best,selected=full,status='FULL_STRENGTHENED_CONTROL_SCREEN_PASS' if full else 'BUDGET_CHECKPOINT_NOT_A_PASS' if budget_stop else 'FIXED_DEPTH2_SEARCH_FAILS');save('RESULT.json',result);print(json.dumps({'status':result['status'],'energy':e}),flush=True)
if __name__=='__main__':main()
