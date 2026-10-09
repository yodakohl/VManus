"""Separate count-vector, log-domain and linear inverse-CDF reconstruction."""
import csv,gzip,hashlib,itertools,json,math,random,re
from collections import defaultdict
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
A=tuple('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()); IDX={a:i for i,a in enumerate(A)}
READERS=['ZL3b','IT2a','RF1b']
def read(p):return json.loads(p.read_text())
def compare(a,b,path=''):
 if isinstance(a,dict):
  assert set(a)==set(b),(path,set(a)^set(b))
  for k in a:compare(a[k],b[k],path+'/'+str(k))
 elif isinstance(a,list):
  assert len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
 elif isinstance(a,float):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(path,a,b)
 else:assert a==b,(path,a,b)

def tables(rows):
 transitions={}; empirical={}; totals=defaultdict(int); known=set()
 for r in rows:
  if r['leaf']%2!=1:continue
  c=r['c']; u=r['u']; n=len(u); cell=(c,n); known.add(u); totals[cell]+=1
  empirical.setdefault(cell,defaultdict(int))[u]+=1
  prev='^'
  for i,s in enumerate(u):
   k=(c,n,i,prev); transitions.setdefault(k,[0]*22)[IDX[s]]+=1; prev=s
 return transitions,empirical,totals,known

def values(rows,tab):
 t,q,N,known=tab; es=[]
 for r in rows:
  if r['leaf']%2:continue
  u=r['u']; c=r['c']; cell=(c,len(u)); total=N.get(cell,0); freq=q.get(cell,{}).get(u,0)/total if total else 0; lp=0
  for i,s in enumerate(u):
   v=t.get((c,len(u),i,u[i-1] if i else '^'),[0]*22); lp+=math.log(v[IDX[s]]+.5)-math.log(sum(v)+11)
  p=math.exp(lp); m=(p+freq)/2 if total else p; gain=math.log(m)-lp
  if not freq and total:assert math.isclose(gain,-math.log(2),abs_tol=1e-12)
  es.append({'id':r['id'],'leaf':r['leaf'],'c':c,'units':list(u),'p':p,'q':freq,'mix':m,'gain':gain,'cell_train_N':total,'global_unseen':u not in known})
 return es

def aggregate(es):
 result={}
 for name in ['ALL','Q_POSITIVE','Q_ZERO','GLOBAL_UNSEEN']:
  selected=[e for e in es if name=='ALL' or name=='Q_POSITIVE' and e['q']>0 or name=='Q_ZERO' and e['q']==0 or name=='GLOBAL_UNSEEN' and e['global_unseen']]
  n=len(selected); groups=defaultdict(list)
  for e in selected:groups[str(e['leaf'])].append(e)
  leafmeans={k:math.fsum(e['gain'] for e in group)/len(group) for k,group in groups.items()}; l=len(leafmeans); positive=sum(v>0 for v in leafmeans.values()); avg=math.fsum(leafmeans.values())/l if l else None
  result[name]={'words':n,'leaves':l,'positive_leaves':positive,'equal_leaf_gain':avg,'token_mean_gain':math.fsum(e['gain'] for e in selected)/n if n else None,'mean_m1_loss':-math.fsum(math.log(e['p']) for e in selected)/n if n else None,'mean_mix_loss':-math.fsum(math.log(e['mix']) for e in selected)/n if n else None,'per_leaf':leafmeans,'material_gate':bool(n>=100 and l>=10 and avg>=.01 and positive>=2*l/3)}
 return result

def generated(rows,tab,seed):
 t=tab[0]; rng=random.Random(seed); out=[]; h=hashlib.sha256(); cdfs={}
 for r in rows:
  u=[]; n=len(r['u'])
  for i in range(n):
   k=(r['c'],n,i,u[-1] if u else '^')
   if k not in cdfs:
    v=t.get(k,[0]*22); accum=[]; total=0
    for x in v:total+=x+.5;accum.append(total)
    cdfs[k]=accum
   accum=cdfs[k]; target=rng.random()*accum[-1]; j=0
   while accum[j]<=target:j+=1
   u.append(A[j])
  h.update((' '.join(u)+'\n').encode()); out.append(dict(r,u=tuple(u)))
 return out,h.hexdigest()

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 assert hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()==read(B/'artifacts/MODEL_LOCK.json')['sha256']
 allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes())); events=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes())); expected=read(B/'artifacts/RESULT.json'); simulations=read(B/'artifacts/SIMULATIONS.json'); models=read(B/'artifacts/MODEL.json'); result={}; totaljoins=0; nscores=0; nsims=0
 # Four-bit distributions supply exact normalization and parity arithmetic.
 toy=list(itertools.product(range(2),repeat=4)); normal=0
 for w in toy:
  even=sum(w)%2==0; mix=(1/16+(1/8 if even else 0))/2; normal+=mix
  assert math.isclose(math.log(mix*16),math.log(1.5) if even else -math.log(2),abs_tol=1e-12)
 assert normal==1
 for ri,reader in enumerate(READERS):
  lookup={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json')['lines']:
    for g in line['groups']:lookup[(line['metadata']['locus'],g[0])]=(line['metadata'],g)
  rows=[]
  for r in data[reader]:
   assert r['page'] in allowed and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v')
   meta,g=lookup[(r['locus'],r['id'])];assert meta['edition']==reader and meta['page']==r['page'] and meta['kind']==r['kind']=='P' and g[2]==r['ivtff_group_raw']
   assert ''.join(r['units'])==r['ivtff_group_raw'] and all(x in A for x in r['units']) and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';totaljoins+=1
   if len(r['units'])>=4:rows.append({'id':r['id'],'c':meta['currier'],'leaf':int(re.match(r'f(\d+)',r['page']).group(1)),'u':tuple(r['units'])})
  tab=tables(rows);t,q,N,known=tab
  # Check every stored fitted cell, not only queried cells.
  mt=[{'context':list(k),'counts':{A[j]:v[j] for j in range(22) if v[j]}} for k,v in sorted(t.items())]
  mq=[{'cell':list(k),'counts':[{'units':list(w),'count':n} for w,n in sorted(v.items())]} for k,v in sorted(q.items())]
  compare({'m1':mt,'whole':mq},models[reader],reader+'/model')
  es=values(rows,tab);native=[{k:v for k,v in e.items() if k!='reader'} for e in events if e['reader']==reader];compare(es,native,reader+'/events');scores=aggregate(es);nscores+=len(es)
  simg=[]
  for rep in range(32):
   seed=1308000+1000*ri+rep; sr,h=generated(rows,tab,seed); ss=aggregate(values(sr,tables(sr)))['ALL']; compare({'replicate':rep,'seed':seed,'draw_sha256':h,'ALL':ss},simulations[reader][rep],reader+'/simulation/'+str(rep));simg.append(ss['equal_leaf_gain']);nsims+=1
  nativegain=scores['ALL']['equal_leaf_gain'];result[reader]={'cohorts':scores,'train_words':sum(N.values()),'train_distinct_wholes':len(known),'train_whole_cell_entries':sum(map(len,q.values())),'train_cells':len(q),'m1_observed_contexts':len(t),'synthetic_max_gain':max(simg),'synthetic_min_gain':min(simg),'synthetic_at_least_native':sum(g>=nativegain for g in simg),'lead':scores['ALL']['material_gate'] and nativegain>max(simg)}
  print(reader,'independent reconstruction PASS',flush=True)
 compare(result,expected['readers'],'results');assert totaljoins==expected['joined_groups']==61181
 assert expected['status']==('WHOLE_FORM_PREDICTIVE_LEAD' if result['ZL3b']['lead'] else 'NO_WHOLE_FORM_LEAD')
 out={'status':'PASS','source_joins':totaljoins,'native_word_scores':nscores,'regenerated_simulations':nsims,'source_free_binary_words':16,'implementation':'separate count vectors, log-domain products, linear inverse-CDF and fsum aggregation; no runner imports','ceiling':'Numerical/source fidelity only; same-author independent implementation, not independent manuscript confirmation.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
