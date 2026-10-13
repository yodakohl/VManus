from pathlib import Path
from collections import defaultdict
import gzip,hashlib,json,math
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 model=read(R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts/MODEL.json');old=R/'experiments/yolo/gdt1316_fixed_half_form_prediction';htables=read(old/'artifacts/MODEL_H.json');events=read(old/'artifacts/EVENTS.json.gz');prior=read(old/'artifacts/RESULT.json');assert prior['status']=='NO_PRODUCTIVE_HALF_FORM_LEAD';cells={};clamps=[];scores=[];funcs={}
 for rd in sorted(model):
  t={tuple(z['context']):z['counts'] for z in model[rd]['m1']};known={tuple(z['units']) for w in model[rd]['whole'] for z in w['counts']};hf={}
  for z in htables[rd]:hf[tuple(z['cell'])]=(z['N'],{tuple(a['units']):a['count'] for a in z['left']},{(a['last_left'],tuple(a['units'])):a['count'] for a in z['right']},z['end'])
  def pp(c,u,t=t):
   factors=[]
   for i,s in enumerate(u):
    ct=t.get((c,len(u),i,u[i-1] if i else '^'),{});factors.append((ct.get(s,0)+.5)/(sum(ct.values())+11))
   return math.prod(factors)
  def hp(c,u,hf=hf):
   fit=hf.get((c,len(u)))
   if fit is None:return None
   n,l,r,ends=fit;k=len(u)//2;left=u[:k];right=u[k:];lc=l.get(left,0)
   return (lc/n)*(r.get((left[-1],right),0)/ends[left[-1]]) if lc else 0.0
  heldcells=sorted({(e['c'],len(e['units'])) for e in events if e['reader']==rd});rows=[]
  for c,n in heldcells:
   seen=sorted(u for u in known if len(u)==n);ps=math.fsum(pp(c,u) for u in seen);has=(c,n) in hf;hs=math.fsum(hp(c,u) for u in seen) if has else None
   if hs is not None and (hs<0 or hs>1):
    assert -1e-12<=hs<=1+1e-12;clamps.append({'reader':rd,'cell':[c,n],'h_seen_before':hs});hs=min(1.0,max(0.0,hs))
   assert 0<=ps<1;ms=(ps+hs)/2 if has else ps
   rows.append({'cell':[c,n],'train_cell':has,'seen_types':len(seen),'p_seen':ps,'p_unseen':1-ps,'h_seen':hs,'h_unseen':None if hs is None else 1-hs,'m_seen':ms,'m_unseen':1-ms})
  cells[rd]=rows;funcs[rd]=(pp,hp,known,{tuple(z['cell']):z for z in rows})
 for e in events:
  rd=e['reader'];u=tuple(e['units']);c=e['c'];pp,hp,known,ct=funcs[rd];assert e['leaf']%2==0 and e['global_unseen']==(u not in known);p=pp(c,u);h=hp(c,u);m=p if h is None else (p+h)/2
  assert math.isclose(p,e['p'],rel_tol=1e-12) and math.isclose(m,e['mix_h'],rel_tol=1e-12)
  z=ct[(c,len(u))];kind='unseen' if e['global_unseen'] else 'seen';pc=z['p_'+kind];mc=z['m_'+kind];assert pc>0 and mc>0
  raw=e['gain_m1'];category=math.log(mc/pc);conditional=math.log((m/mc)/(p/pc));assert abs(raw-category-conditional)<1e-11
  scores.append({'id':e['id'],'reader':rd,'leaf':e['leaf'],'cell':[c,len(u)],'unseen':e['global_unseen'],'raw_gain':raw,'category_gain':category,'conditional_gain':conditional})
 result={}
 for rd in sorted(model):
  co={}
  for cohort in ['ALL','GLOBAL_UNSEEN','GLOBAL_KNOWN']:
   es=[e for e in scores if e['reader']==rd and (cohort=='ALL' or e['unseen']==(cohort=='GLOBAL_UNSEEN'))];by=defaultdict(list)
   for e in es:by[e['leaf']].append(e)
   pl={str(leaf):{'words':len(v),**{k:math.fsum(e[k+'_gain'] for e in v)/len(v) for k in ['raw','category','conditional']}} for leaf,v in sorted(by.items())}
   s={'words':len(es),'leaves':len(by),'per_leaf':pl}
   for k in ['raw','category','conditional']:s[k+'_equal_leaf']=math.fsum(z[k] for z in pl.values())/len(pl);s[k+'_token']=math.fsum(e[k+'_gain'] for e in es)/len(es)
   oldc=prior['readers'][rd]['cohorts'][cohort];assert s['words']==oldc['words'] and s['leaves']==oldc['leaves'] and abs(s['raw_equal_leaf']-oldc['equal_leaf_gain_m1'])<1e-11;co[cohort]=s
  result[rd]=co;print(rd,{k:{m:round(v[m+'_equal_leaf'],6) for m in ['raw','category','conditional']} for k,v in co.items()})
 save('CELLS.json',cells);save('SCORES.json.gz',scores);save('RESULT.json',{'status':'FROZEN_NOVELTY_SCORE_ACCOUNTING','readers':result,'clamps':clamps})
if __name__=='__main__':main()
