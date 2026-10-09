from common import *
from array_model import Fast
import numpy as np
import z3,os,hashlib,random,math,time,copy

def save(n,obj):(A/n).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def evaluate(fast,p,targets):
 met=fast.metrics(p);comp={};extra={};energy=0.;full=True
 for b,m in met.items():
  comp[b]={};extra[b]={}
  for ed,t in targets.items():
   cc=w.m.compare(m,t);comp[b][ed]=cc;dd={k:(v['difference'],.01 if k=='edit1_repeat' else v['limit']) for k,v in cc['diagnostics'].items()}
   ee={'q_followed_o':(abs(m['q_followed_o']-t['q_followed_o']),.03),'q_count':(abs(m['q_count']-t['q_count']),.25*t['q_count']),'y_final':(abs(m['y_final']-t['y_final']),.05),'glyph_entropy':(abs(m['glyph_entropy']-t['glyph_entropy']),.15),'word_entropy':(abs(m['word_entropy']-t['word_entropy']),.30)};extra[b][ed]={k:{'difference':float(a),'limit':float(limit),'within':bool(a<=limit)} for k,(a,limit) in ee.items()};dd.update(ee)
   ratios=[d/limit for d,limit in dd.values()];energy+=sum(max(0,v-1)**2+.0001*v*v for v in ratios);full=full and all(v<=1 for v in ratios)
 return energy,full,met,comp,extra

def y_solution(counts,targets):
 solver=z3.Optimize();solver.set(timeout=10000);C=counts.shape[1];xs=[[z3.Bool(f'c{c}_{i}') for i in range(6)] for c in range(C)]
 for row in xs:solver.add(z3.PbEq([(x,1) for x in row],1))
 possible=range(8001);valid=[n for n in possible if all(abs(n/8000-t['y_final'])<=.05 for t in targets.values())];lower,upper=min(valid),max(valid)
 for b in range(4):
  total=z3.Sum([z3.If(xs[c][i],int(counts[b,c,i]),0) for c in range(C) for i in range(6)]);solver.add(total>=lower,total<=upper)
 solver.minimize(z3.Sum([z3.If(xs[c][i],(c+1)*(i+1),0) for c in range(C) for i in range(6)]));status=solver.check()
 if status!=z3.sat:return None,{'solver_status':str(status),'reason':solver.reason_unknown() if status==z3.unknown else 'No feasible final-y assignment','allowed_counts':[lower,upper]}
 model=solver.model();choice=[next(i for i in range(6) if z3.is_true(model.eval(xs[c][i]))) for c in range(C)];totals=[sum(int(counts[b,c,i]) for c,i in enumerate(choice)) for b in range(4)];assert all(lower<=n<=upper for n in totals);return choice,{'solver_status':'verified_feasible','choice':choice,'source_counts':totals,'allowed_counts':[lower,upper],'objective_optimality_not_required':True}

def initial_params(depth,candidate,choice,base):
 _,mask,qpos=candidate;ii=base['alphabets']['initial'][:];old=ii.index('q');ii[old],ii[qpos]=ii[qpos],ii[old];body=[g for g in base['alphabets']['medial'][:3] if g!='q'];body+=[g for g in NQ if g not in body];final=[]
 for cat in choice:
  order=['y']+[g for g in base['alphabets']['final'][:6] if g not in ['q','y']];order+=[g for g in NQ if g not in order];order[0],order[cat]=order[cat],order[0];final.append(order)
 p={'depth':depth,'mask':mask,'qpos':qpos,'initial':ii,'body':body,'final':final};return p

def mutate(p,candidates,rng):
 pp=copy.deepcopy(p);which=rng.randrange(4)
 if which==0:
  choices=[i for i in range(22) if i!=pp['qpos']];a,b=rng.sample(choices,2);pp['initial'][a],pp['initial'][b]=pp['initial'][b],pp['initial'][a]
 elif which==1:
  a,b=rng.sample(range(21),2);pp['body'][a],pp['body'][b]=pp['body'][b],pp['body'][a]
 elif which==2:
  row=rng.choice(pp['final']);a,b=rng.sample(range(21),2);row[a],row[b]=row[b],row[a]
 else:
  _,mask,qpos=rng.choice(candidates);old=pp['qpos'];pp['initial'][old],pp['initial'][qpos]=pp['initial'][qpos],pp['initial'][old];pp['qpos']=qpos;pp['mask']=mask
 return pp

def parity(fast,inner,source,p,candidates,targets,index):
 rng=random.Random(1194000+index);checks=0
 for fixture in range(4):
  pp=copy.deepcopy(p)
  if fixture:
   for _ in range(12):
    trial=mutate(pp,candidates,rng)
    if legal(trial):pp=trial
  writer=Writer(inner,pp);met=fast.metrics(pp)
  for b in BOOKS:
   ps,_=w.engine.pages(writer,source[b]);w.fast.close(met[b],w.engine.measure(ps));checks+=1
 return checks

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source,tables,targets,base,inner,cache=prepare();fast=Fast(cache,base);candidates,qcounts=fast.candidates(targets);save('LENGTH_CANDIDATES.json',candidates);result={'experiment':'GDT1194','length_candidates':len(candidates),'q_counts':qcounts,'arms':{},'selected':None,'dependencies':{'numpy':np.__version__,'z3':z3.get_version_string()}}
 if not candidates:result['status']='NO_NECESSARY_LENGTH_CANDIDATE';save('RESULT.json',result);print(json.dumps(result));return
 for index,depth in enumerate((1,2)):
  counts=fast.y_counts(depth);choice,ys=y_solution(counts,targets);arm={'y_feasibility':ys,'contexts':len(counts[0])};result['arms'][str(depth)]=arm;save('RESULT.json',result);print(json.dumps({'stage':'CAPACITY','depth':depth,'length_candidates':len(candidates),'y':ys}),flush=True)
  if choice is None:continue
  p=initial_params(depth,candidates[0],choice,base);assert legal(p);arm['parity_checks']=parity(fast,inner,source,p,candidates,targets,index);print(json.dumps({'stage':'PARITY','depth':depth,'checks':arm['parity_checks']}),flush=True);rng=random.Random(119400+index);energy,full,*_=evaluate(fast,p,targets);best={'params':copy.deepcopy(p),'energy':energy,'full_pass':full,'step':-1};accepted=invalid=0;start=time.monotonic();log=[];attempted=0
  for step in range(6000):
   if full:break
   attempted=step+1;trial=mutate(p,candidates,rng)
   if not legal(trial):invalid+=1;continue
   value,passed,*_=evaluate(fast,trial,targets)
   if passed or value<best['energy']:best={'params':copy.deepcopy(trial),'energy':value,'full_pass':passed,'step':step}
   if passed:full=True;break
   temp=max(1e-6,.03*(1-step/6000))
   if value<=energy or rng.random()<math.exp(min(0,(energy-value)/temp)):p=trial;energy=value;accepted+=1
   if step%250==0:
    rec={'depth':depth,'step':step,'best_energy':best['energy'],'seconds':round(time.monotonic()-start,1)};log.append(rec);save('SEARCH_LOG.json',{'log':log,'best':best});print(json.dumps(rec),flush=True)
  best['search']={'proposals':attempted,'accepted':accepted,'invalid':invalid,'seed':119400+index,'seconds':time.monotonic()-start,'log':log};writer=Writer(inner,best['params']);ee,ff,met,comp,extra=evaluate(fast,best['params'],targets);assert ff==best['full_pass'];roundtrips=0
  for b in BOOKS:
   ps,_=w.engine.pages(writer,source[b]);w.fast.close(w.engine.measure(ps),met[b]);roundtrips+=len(source[b]);(A/f'D{depth}_{b}.txt').write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in ps)+'\n')
  best.update(metrics=met,comparison=comp,extra=extra,complete_recipe_roundtrips=roundtrips);arm['best']=best;save('RESULT.json',result);print(json.dumps({'stage':'FINAL','depth':depth,'full_pass':ff,'energy':ee}),flush=True)
  if ff:result['selected']=depth;break
 result['status']='FULL_STRENGTHENED_CONTROL_SCREEN_PASS' if result['selected'] else 'PAIRED_NOTATION_BOUNDED_SEARCH_FAILS';result['claim_ceiling']='Artificial target-fitted control, not native translation, historical simplicity, independent confirmation, or complete word-family/section matching.';save('RESULT.json',result);print(json.dumps({'status':result['status'],'selected':result['selected']}),flush=True)
if __name__=='__main__':main()
