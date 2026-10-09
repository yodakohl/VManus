from pathlib import Path
import json,sys,hashlib,random,math,importlib.util
import numpy as np
import codec as c
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1184_contextual_initial_styles/src'))
import run as engine
spec=importlib.util.spec_from_file_location('capacity',ROOT/'experiments/yolo/gdt1186_exact_edit_one_capacity/src/run.py');cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
m=engine.m
BOOKS=['b4','w1','bs1','gr1']
def save(n,x):(A/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def writepages(n,ps):(A/n).write_text('\n\n'.join('\n'.join(' '.join(line) for line in p) for p in ps)+'\n')
def optimize(profs,adj,targets,seed):
 ts=[(t['conditional_entropy'],t['first_last_js'],np.array([t['glyph_counts'].get(g,0) for g in c.SIGNS]),t['edit1_repeat']) for t in targets.values()]
 def objective(alph):
  score=0
  for book,prof in profs.items():
   h,e,g=engine.mapped(prof,alph);rate=cap.predicted(adj[book],alph)/adj[book]['denominator']
   for th,te,tg,tr in ts:
    ratios=[abs(h-th)/.3,abs(e-te)/.12,float(engine.js(g,tg))/.1,abs(rate-tr)/.01]
    score+=sum(max(0,x-1)**2+.0001*x*x for x in ratios)
  return float(score)
 rng=random.Random(seed);current=c.default_alphabets();score=objective(current);best={k:v[:] for k,v in current.items()};bestscore=score;accepted=invalid=0
 for step in range(5000):
  which=rng.randrange(4);key='initial' if which<2 else 'medial' if which==2 else 'final';a,b=rng.sample(range(22),2);trial={k:v[:] for k,v in current.items()};trial[key][a],trial[key][b]=trial[key][b],trial[key][a]
  if not engine.coverage(trial):invalid+=1;continue
  value=objective(trial);temp=max(1e-6,.08*(1-step/5000))
  if value<=score or rng.random()<math.exp(min(0,(score-value)/temp)):
   current=trial;score=value;accepted+=1
   if value<bestscore:best={k:v[:] for k,v in current.items()};bestscore=value
 return best,{'seed':seed,'proposals':5000,'accepted':accepted,'coverage_rejections':invalid,'best_objective':bestscore}

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(engine.SOURCE.read_text());tables=json.loads(engine.TABLES.read_text());targets=json.loads(engine.TARGET.read_text())['targets'];out={'experiment':'GDT1188','stage_A':{},'design':{}}
 for index,model in enumerate(c.MODELS):
  codec=c.Codec(model,tables);necessary=True;entry={'books':{}};profs={};adj={}
  for book in BOOKS:
   ps,nums=engine.pages(codec,source[book]);met=engine.measure(ps);checks={ed:{k:m.compare(met,t)['diagnostics'][k] for k in engine.NECESSARY} for ed,t in targets.items()};ok=all(x['within'] for ch in checks.values() for x in ch.values());necessary=necessary and ok
   entry['books'][book]={'metrics':met,'necessary_checks':checks,'all_exact':True,'complete_recipes':len(source[book])};profs[book]=engine.profile(nums);adj[book],_=cap.summarize(cap.numeric_lines(codec,source[book]));writepages(f'A_{model}_{book}.txt',ps)
  entry['necessary_pass']=necessary;out['stage_A'][model]=entry;save('RESULT.json',out);print(json.dumps({'stage':'A','model':model,'necessary':necessary,'failed':{b:[k for k,x in e['necessary_checks']['ZL3b'].items() if not x['within']] for b,e in entry['books'].items()}}),flush=True)
  if not necessary:continue
  restarts=[]
  for restart in range(3):
   alph,log=optimize(profs,adj,targets,118800+10*index+restart);restarts.append({'alphabets':alph,'optimization':log});print(json.dumps({'stage':'FIT','model':model,'restart':restart,'objective':log['best_objective']}),flush=True)
  chosen=min(range(3),key=lambda i:restarts[i]['optimization']['best_objective']);alph=restarts[chosen]['alphabets'];codec=c.Codec(model,tables,alph);metrics={};comparison={};tight={}
  for book in BOOKS:
   ps,_=engine.pages(codec,source[book]);metrics[book]=engine.measure(ps);comparison[book]={ed:m.compare(metrics[book],t) for ed,t in targets.items()};tight[book]={ed:abs(metrics[book]['edit1_repeat']-t['edit1_repeat'])<=.01 for ed,t in targets.items()};assert abs(metrics[book]['edit1_repeat']-cap.predicted(adj[book],alph)/adj[book]['denominator'])<1e-15;writepages(f'B_{model}_{book}.txt',ps)
  full=all(x['joint_screen'] for book in comparison.values() for x in book.values()) and all(x for book in tight.values() for x in book.values());out['design'][model]={'restarts':restarts,'chosen_restart':chosen,'alphabets':alph,'metrics':metrics,'comparison':comparison,'tight_edit1':tight,'full_pass':full,'table_entries':len(codec.codes)};save('RESULT.json',out);print(json.dumps({'stage':'B','model':model,'full_pass':full}),flush=True)
 out['passing_models']=[name for name,e in out['design'].items() if e['full_pass']];out['status']='FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS' if out['passing_models'] else 'GREEDY_DICTIONARIES_FAIL_FULL_SCREEN' if out['design'] else 'STOP_ALL_FOUR_SOURCE_INVARIANTS';out['claim_ceiling']='Known-summary fitted source construction only, no independent confirmation/native values/historical usability.';save('RESULT.json',out);print(json.dumps({'status':out['status'],'passing_models':out['passing_models']}),flush=True)
if __name__=='__main__':main()
