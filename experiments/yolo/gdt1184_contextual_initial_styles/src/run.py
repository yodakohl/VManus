from pathlib import Path
from collections import Counter
import json,sys,hashlib,math,random
import numpy as np
import codec as c
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/src'))
import metrics as m
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
NECESSARY=['mean_length','sd_length','top10_share','type_ratio','exact_repeat','length_tv']
def save(name,obj):(A/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def wrap(words):
 lines=[];line=[];size=0
 for word in words:
  n=len(m.glyphs(word))
  if line and size+1+n>48:lines.append(line);line=[];size=0
  size+=n+bool(line);line.append(word)
 if line:lines.append(line)
 return lines

def pages(codec,recipes):
 encoded=[];numeric=[]
 for recipe in recipes:
  nums=codec.numeric(recipe['words']);ws=codec.render(nums);assert codec.decode([m.glyphs(w) for w in ws])==recipe['words'];encoded.append(wrap(ws));numeric+=nums
 return encoded,numeric[:8000]
def measure(pages):return m.measure([line for page in pages for line in page])
def writepages(name,pages):(A/name).write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in pages)+'\n')
def profile(words):
 gc=np.zeros(31);fc=np.zeros(31);lc=np.zeros(31);bc=np.zeros((31,31))
 for w in words:
  fc[w[0]]+=1;lc[w[-1]]+=1
  for g in w:gc[g]+=1
  for a,b in zip(w,w[1:]):bc[a,b]+=1
 return gc,fc,lc,bc

def js(a,b):
 p=a/a.sum();q=b/b.sum();mid=(p+q)/2;pa=p>0;qa=q>0
 return .5*((p[pa]*np.log2(p[pa]/mid[pa])).sum()+(q[qa]*np.log2(q[qa]/mid[qa])).sum())
def mapped(prof,alph):
 mapping=np.array([c.SIGNS.index(g) for g in alph['initial']+alph['medial'][:3]+alph['final'][:6]]);gc,fc,lc,bc=prof
 out=[np.bincount(mapping,weights=counts,minlength=22) for counts in [gc,fc,lc]]
 pairmap=(mapping[:,None]*22+mapping[None,:]).ravel();pairs=np.bincount(pairmap,weights=bc.ravel(),minlength=484).reshape(22,22);prev=pairs.sum(axis=1);rows,cols=np.nonzero(pairs);vals=pairs[rows,cols];h2=float(-(vals*np.log2(vals/prev[rows])).sum()/pairs.sum())
 return h2,float(js(out[1],out[2])),out[0]
def coverage(alph):return len(set(alph['initial'][:21]+alph['medial'][:3]+alph['final'][:6]))==22

def optimize(profiles,targets,seed):
 target=[(t['conditional_entropy'],t['first_last_js'],np.array([t['glyph_counts'].get(g,0) for g in c.SIGNS])) for t in targets.values()]
 def objective(alph):
  total=0
  for prof in profiles.values():
   h,e,g=mapped(prof,alph)
   for th,te,tg in target:
    ratios=[abs(h-th)/.3,abs(e-te)/.12,float(js(g,tg))/.1]
    total+=sum(max(0,r-1)**2+.0001*r*r for r in ratios)
  return float(total)
 rng=random.Random(seed);current=c.default_alphabets();assert coverage(current);score=objective(current);best={k:v[:] for k,v in current.items()};bestscore=score;accepted=invalid=0
 for step in range(4000):
  which=rng.randrange(4);key='initial' if which<2 else 'medial' if which==2 else 'final';a,b=rng.sample(range(22),2);trial={k:v[:] for k,v in current.items()};trial[key][a],trial[key][b]=trial[key][b],trial[key][a]
  if not coverage(trial):invalid+=1;continue
  value=objective(trial);temp=max(1e-6,.08*(1-step/4000))
  if value<=score or rng.random()<math.exp(min(0,(score-value)/temp)):
   current=trial;score=value;accepted+=1
   if value<bestscore:best={k:v[:] for k,v in current.items()};bestscore=value
 return best,{'seed':seed,'proposals':4000,'accepted':accepted,'coverage_rejections':invalid,'best_objective':bestscore}

TABLES=ROOT/'experiments/yolo/gdt1183_initial_prefix_contraction/artifacts/TABLES.json'
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];tables=json.loads(TABLES.read_text());save('TABLES.json',tables);stage={};designs={}
 for grid_index,model in enumerate(c.MODELS):
  codec=c.Codec(model,tables);entry={'books':{}};profs={};ok=True
  for col in ['b4','w1']:
   ps,nums=pages(codec,source[col]);met=measure(ps);writepages(f'A_{model}_{col}.txt',ps);comp={ed:m.compare(met,t) for ed,t in targets.items()};checks={ed:{k:v['diagnostics'][k] for k in NECESSARY} for ed,v in comp.items()};entry['books'][col]={'necessary_checks':checks,'complete_recipes':len(source[col]),'all_exact':True};ok=ok and all(row['within'] for ed in checks.values() for row in ed.values());profs[col]=profile(nums)
  entry['necessary_pass']=ok;stage[model]=entry;save('STAGE_A.json',stage);print(json.dumps({'stage':'A','model':model,'necessary':ok}),flush=True)
  if not ok:continue
  restarts=[]
  for restart in range(4):
   alph,optimization=optimize(profs,targets,118400+10*grid_index+restart);restarts.append({'alphabets':alph,'optimization':optimization});print(json.dumps({'stage':'FIT','model':model,'restart':restart,'objective':optimization['best_objective']}),flush=True)
  best=min(range(4),key=lambda i:restarts[i]['optimization']['best_objective']);alph=restarts[best]['alphabets'];codec=c.Codec(model,tables,alph);met={};comparison={}
  for col in ['b4','w1']:
   ps,_=pages(codec,source[col]);met[col]=measure(ps);comparison[col]={ed:m.compare(met[col],t) for ed,t in targets.items()};writepages(f'B_{model}_{col}.txt',ps)
   h,e,g=mapped(profs[col],alph);assert abs(h-met[col]['conditional_entropy'])<1e-12 and abs(e-met[col]['first_last_js'])<1e-12;assert all(int(g[i])==met[col]['glyph_counts'].get(sign,0) for i,sign in enumerate(c.SIGNS))
  full=all(row['joint_screen'] for book in comparison.values() for row in book.values());designs[model]={'alphabets':alph,'restarts':restarts,'chosen_restart':best,'metrics':met,'comparison':comparison,'full_design_pass':full,'table_entries':len(codec.codes)};save('DESIGN.json',designs);print(json.dumps({'stage':'B','model':model,'full_design_pass':full}),flush=True)
 save('DESIGN_LOCK.json',{'designs':designs,'table_sha256':hashlib.sha256((A/'TABLES.json').read_bytes()).hexdigest(),'decision':'Both fixed design outcomes frozen before any transfer measurement'})
 transfer={}
 for model,design in designs.items():
  if not design['full_design_pass']:continue
  codec=c.Codec(model,tables,design['alphabets']);metrics={};comparison={};roundtrips={}
  for col,rs in source.items():
   ps,_=pages(codec,rs);writepages(f'T_{model}_{col}.txt',ps);metrics[col]=measure(ps);comparison[col]={ed:m.compare(metrics[col],t) for ed,t in targets.items()};roundtrips[col]={'complete_recipes':len(rs),'exact':True}
  full=all(row['joint_screen'] for book in comparison.values() for row in book.values());transfer[model]={'full_pass':full,'metrics':metrics,'comparison':comparison,'roundtrips':roundtrips};print(json.dumps({'stage':'TRANSFER','model':model,'full_pass':full}),flush=True)
 passing=[model for model,t in transfer.items() if t['full_pass']];status='FULL_BASIC_SCREEN_PASS' if passing else 'CONTEXTUAL_STYLES_FAIL_TRANSFER' if transfer else 'STOP_NO_DESIGN_STYLE_WRITER';result={'experiment':'GDT1184','status':status,'passing_models':passing,'stage_A':stage,'design':designs,'transfer':transfer,'claim_ceiling':'Openly target-summary-fitted source construction; no native values, independent confirmation, stronger structure or historical usability claim.'};save('RESULT.json',result);print(json.dumps({'status':status,'passing_models':passing}),flush=True)
if __name__=='__main__':main()
