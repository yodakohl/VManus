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
def mapped(prof,perm):
 mapping=np.array([c.SIGNS.index(g) for g in perm+c.MEDIAL+c.FINAL['E']+c.FINAL['C']]);gc,fc,lc,bc=prof
 out=[np.bincount(mapping,weights=counts,minlength=22) for counts in [gc,fc,lc]]
 pairmap=(mapping[:,None]*22+mapping[None,:]).ravel();pairs=np.bincount(pairmap,weights=bc.ravel(),minlength=484).reshape(22,22);prev=pairs.sum(axis=1);rows,cols=np.nonzero(pairs);vals=pairs[rows,cols];h2=float(-(vals*np.log2(vals/prev[rows])).sum()/pairs.sum())
 return h2,float(js(out[1],out[2])),out[0]
def optimize(profiles,targets,K,seed):
 target_h=sum(t['conditional_entropy'] for t in targets.values())/3;target_edge=sum(t['first_last_js'] for t in targets.values())/3;gs=[np.array([t['glyph_counts'].get(g,0) for g in c.SIGNS]) for t in targets.values()]
 suffix=set(c.MEDIAL+c.FINAL['E']+c.FINAL['C']);initial=[g for g in c.SIGNS if g not in suffix]+[g for g in c.SIGNS if g in suffix]
 def objective(perm):
  total=0
  for prof in profiles.values():
   h,e,g=mapped(prof,perm);total+=((h-target_h)/.3)**2+((e-target_edge)/.12)**2+sum((js(g,t)/.1)**2 for t in gs)
  return float(total)
 rng=random.Random(seed);current=initial[:];score=objective(current);best=current[:];bestscore=score;accepted=0;invalid=0
 for step in range(5000):
  a,b=rng.sample(range(22),2);trial=current[:];trial[a],trial[b]=trial[b],trial[a]
  if len(set(trial[:K])|suffix)<22:invalid+=1;continue
  value=objective(trial);temp=max(1e-6,.05*(1-step/5000))
  if value<=score or rng.random()<math.exp(min(0,(score-value)/temp)):
   current=trial;score=value;accepted+=1
   if value<bestscore:best=current[:];bestscore=value
 return best,{'seed':seed,'proposals':5000,'accepted':accepted,'coverage_rejections':invalid,'best_objective':bestscore}

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];tables=c.train(source);save('TABLES.json',tables)
 stage={};passers=[];designs={}
 for grid_index,model in enumerate(c.MODELS):
  codec=c.Codec(model,tables);entry={'actual_frontier':codec.K,'offered_capacity_possible':codec.K>=13,'books':{}};profs={};ok=True
  for col in ['b4','w1']:
   ps,nums=pages(codec,source[col]);met=measure(ps);writepages(f'A_{model}_{col}.txt',ps);comp={ed:m.compare(met,t) for ed,t in targets.items()};checks={ed:{k:v['diagnostics'][k] for k in NECESSARY} for ed,v in comp.items()};entry['books'][col]={'necessary_checks':checks,'complete_recipes':len(source[col]),'source_words':sum(len(r['words']) for r in source[col]),'all_exact':True};ok=ok and all(row['within'] for ed in checks.values() for row in ed.values());profs[col]=profile(nums)
  entry['necessary_pass']=ok;stage[model]=entry;save('STAGE_A.json',stage);print(json.dumps({'stage':'A','model':model,'K':codec.K,'necessary':ok,'failed':{col:{ed:[k for k,v in rows.items() if not v['within']] for ed,rows in b['necessary_checks'].items()} for col,b in entry['books'].items()}}),flush=True)
  if not ok or codec.K<13:continue
  perm,optimization=optimize(profs,targets,codec.K,118300+grid_index);codec=c.Codec(model,tables,perm);met={};comparison={}
  for col in ['b4','w1']:
   ps,_=pages(codec,source[col]);met[col]=measure(ps);comparison[col]={ed:m.compare(met[col],t) for ed,t in targets.items()};writepages(f'B_{model}_{col}.txt',ps)
   h,e,g=mapped(profs[col],perm);assert abs(h-met[col]['conditional_entropy'])<1e-12 and abs(e-met[col]['first_last_js'])<1e-12
   assert all(int(g[i])==met[col]['glyph_counts'].get(sign,0) for i,sign in enumerate(c.SIGNS))
  full=all(row['joint_screen'] for book in comparison.values() for row in book.values());designs[model]={'permutation':perm,'optimization':optimization,'metrics':met,'comparison':comparison,'full_design_pass':full,'table_entries':len(codec.codes),'frontier':codec.K};save('DESIGN.json',designs)
  if full:passers.append(model)
  print(json.dumps({'stage':'B','model':model,'full_design_pass':full,'objective':optimization['best_objective']}),flush=True)
 if not passers:
  result={'experiment':'GDT1183','status':'STOP_NO_DESIGN_WRITER','selected':None,'stage_A':stage,'design':designs,'transfer_scored':False,'claim_ceiling':'Necessary/fitted construction on exposed design books only; no native values, transfer success or complete writer retained.'};save('RESULT.json',result);return
 selected=min(passers,key=lambda model:(designs[model]['table_entries'],designs[model]['frontier'],designs[model]['optimization']['best_objective'],model));choice={'model':selected,'permutation':designs[selected]['permutation'],'design':designs[selected],'table_sha256':hashlib.sha256((A/'TABLES.json').read_bytes()).hexdigest()};save('SELECTION_LOCK.json',choice)
 codec=c.Codec(selected,tables,choice['permutation']);metrics={};comparison={};roundtrips={}
 for col,rs in source.items():
  ps,_=pages(codec,rs);writepages(f'SELECTED_{col}.txt',ps);metrics[col]=measure(ps);comparison[col]={ed:m.compare(metrics[col],t) for ed,t in targets.items()};roundtrips[col]={'complete_recipes':len(rs),'source_words':sum(len(r['words']) for r in rs),'exact':True}
 full=all(row['joint_screen'] for book in comparison.values() for row in book.values());result={'experiment':'GDT1183','status':'FULL_BASIC_SCREEN_PASS' if full else 'SELECTED_WRITER_FAILS_TRANSFER','selected':selected,'stage_A':stage,'design':designs,'metrics':metrics,'comparison':comparison,'roundtrips':roundtrips,'transfer_scored':True,'claim_ceiling':'Fitted exposed-source construction only; no native key, historical usability or stronger structural validation.'};save('RESULT.json',result);print(json.dumps({'status':result['status'],'selected':selected}),flush=True)
if __name__=='__main__':main()
