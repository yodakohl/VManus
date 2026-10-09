from pathlib import Path
import sys,json,hashlib,random,math,time,os
import codec as c
import fast
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1184_contextual_initial_styles/src'))
import run as engine
m=engine.m
BOOKS=fast.BOOKS
def save(n,x):(A/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def writepages(n,ps):(A/n).write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in ps)+'\n')
def evaluate(cache,assignment,alph,targets):
 metrics=cache.metrics(assignment,alph);comparisons={};tight={};energy=0;full=True
 for b,met in metrics.items():
  comparisons[b]={ed:m.compare(met,t) for ed,t in targets.items()};tight[b]={ed:abs(met['edit1_repeat']-t['edit1_repeat'])<=.01 for ed,t in targets.items()}
  for ed,comp in comparisons[b].items():
   for k,x in comp['diagnostics'].items():
    limit=.01 if k=='edit1_repeat' else x['limit'];ratio=x['difference']/limit;energy+=max(0,ratio-1)**2+.0001*ratio*ratio
   full=full and comp['joint_screen'] and tight[b][ed]
 return energy,full,metrics,comparisons,tight

def parity(codec,cache,source,targets,alph,index):
 rng=random.Random(1191000+index);identity=list(range(len(codec.units)));checks=0
 for fixture in range(4):
  p=identity[:];aa={k:v[:] for k,v in alph.items()}
  if fixture:
   for _ in range(20):a,b=rng.sample(range(len(p)),2);p[a],p[b]=p[b],p[a]
   while True:
    aa={k:v[:] for k,v in alph.items()};key=rng.choice(['initial','medial','final']);a,b=rng.sample(range(22),2);aa[key][a],aa[key][b]=aa[key][b],aa[key][a]
    if engine.coverage(aa):break
  probe=c.Codec(codec.model_name,json.loads(engine.TABLES.read_text()),aa,p);met=cache.metrics(p,aa)
  for book in BOOKS:
   ps,_=engine.pages(probe,source[book]);fast.close(met[book],engine.measure(ps));checks+=1
 return checks

def search(codec,cache,alph,targets,index):
 rng=random.Random(119100+index);current=list(range(len(codec.units)));aa={k:v[:] for k,v in alph.items()};energy,full,*_=evaluate(cache,current,aa,targets);best={'assignment':current[:],'alphabets':{k:v[:] for k,v in aa.items()},'energy':energy,'full_pass':full,'step':-1};log=[];accepted=invalid=guided=attempted=0;start=time.monotonic()
 for step in range(6000):
  if full:break
  attempted=step+1
  trial=current[:];ab={k:v[:] for k,v in aa.items()}
  if rng.random()<.2:
   which=rng.randrange(4);key='initial' if which<2 else 'medial' if which==2 else 'final';a,b=rng.sample(range(22),2);ab[key][a],ab[key][b]=ab[key][b],ab[key][a]
   if not engine.coverage(ab):invalid+=1;continue
  else:
   a=b=None
   if rng.random()<.5:
    first,second=rng.choice(cache.neighbors);options=cache.alternatives[current[first]]
    if options:a=second;b=current.index(rng.choice(options));guided+=1
   if a is None or a==b:a,b=rng.sample(cache.observed,2)
   trial[a],trial[b]=trial[b],trial[a]
  value,passes,*_=evaluate(cache,trial,ab,targets)
  if passes or value<best['energy']:best={'assignment':trial[:],'alphabets':{k:v[:] for k,v in ab.items()},'energy':value,'full_pass':passes,'step':step}
  if passes:full=True;break
  temperature=max(1e-6,.02*(1-step/6000))
  if value<=energy or rng.random()<math.exp(min(0,(energy-value)/temperature)):current=trial;aa=ab;energy=value;accepted+=1
  if step%250==0:
   rec={'model':codec.model_name,'step':step,'best_energy':best['energy'],'elapsed_seconds':round(time.monotonic()-start,1)};log.append(rec);print(json.dumps(rec),flush=True);save('SEARCH_LOG.json',{'model':codec.model_name,'log':log,'best':best})
 best['search']={'seed':119100+index,'attempted':attempted,'accepted':accepted,'coverage_rejections':invalid,'guided':guided,'elapsed_seconds':time.monotonic()-start,'log':log};return best

def main():
 assert os.environ.get("PYTHONHASHSEED")=="0", "Run with PYTHONHASHSEED=0 for reproducible objective summation"
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(engine.SOURCE.read_text());tables=json.loads(engine.TABLES.read_text());targets=json.loads(engine.TARGET.read_text())['targets'];old=json.loads((ROOT/'experiments/yolo/gdt1184_contextual_initial_styles/artifacts/RESULT.json').read_text());result={'experiment':'GDT1191','models':{},'parity_checks':{},'selected':None}
 for index,model in enumerate(c.MODELS):
  alph=old['design']['M'+model[1:]]['alphabets'];codec=c.Codec(model,tables,alph);codec.model_name=model;cache=fast.Cache(codec,source)
  result['parity_checks'][model]=parity(codec,cache,source,targets,alph,index);save('PARITY.json',result['parity_checks']);print(json.dumps({'stage':'PARITY','model':model,'checks':result['parity_checks'][model]}),flush=True)
  best=search(codec,cache,alph,targets,index);writer=c.Codec(model,tables,best['alphabets'],best['assignment']);metrics={};comparison={};tight={}
  for book in BOOKS:
   ps,_=engine.pages(writer,source[book]);metrics[book]=engine.measure(ps);comparison[book]={ed:m.compare(metrics[book],t) for ed,t in targets.items()};tight[book]={ed:abs(metrics[book]['edit1_repeat']-t['edit1_repeat'])<=.01 for ed,t in targets.items()};writepages(f'{model}_{book}.txt',ps)
  e,full,fm,fc,ft=evaluate(cache,best['assignment'],best['alphabets'],targets);fast.close(fm,metrics);fast.close(fc,comparison);assert ft==tight and full==best['full_pass'];best.update(metrics=metrics,comparison=comparison,tight_edit1=tight,units=writer.units,table_entries=len(writer.units));result['models'][model]=best
  save(model+'_PUBLIC_TABLE.json',{'model':model,'alphabets':best['alphabets'],'entries':{u:{'rank':r,'tail':list(ds)} for u,(r,ds) in writer.encoded.items()},'source_rules':'Longest matching literal fragment, no cross-word match; E/C terminal, visible recipe reset, state modulo6, initial rotation modulo7; code groups delimited by spaces.'});save('RESULT.json',result);print(json.dumps({'stage':'FINAL','model':model,'full_pass':full,'energy':e}),flush=True)
  if full:result['selected']=model;break
 result['status']='FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS' if result['selected'] else 'SOURCE_CODE_ASSIGNMENT_SEARCH_FAILS';result['claim_ceiling']='Fitted artificial complete-source writer only; no native word meaning, historical practicality, independent confirmation or stronger structural pass.';save('RESULT.json',result)
if __name__=='__main__':main()
