import collections,gzip,hashlib,itertools,json,math
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,o):
 data=(json.dumps(o,indent=2)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(data,mtime=0) if n.endswith('.gz') else data)
def fit(counts):
 left=collections.Counter();right=collections.defaultdict(collections.Counter);end=collections.Counter()
 for u,c in counts.items():
  k=len(u)//2;l=u[:k];r=u[k:];left[l]+=c;right[l[-1]][r]+=c;end[l[-1]]+=c
 return left,right,end,sum(counts.values())
def prob(f,u):
 left,right,end,N=f;k=len(u)//2;l=u[:k];r=u[k:]
 if not left[l]:return 0.0
 return (left[l]/N)*(right[l[-1]][r]/end[l[-1]])
def summarize(es):
 result={}
 for cohort in ['ALL','GLOBAL_UNSEEN','GLOBAL_KNOWN','Q_ZERO','H_POSITIVE','H_ZERO']:
  rows=[e for e in es if cohort=='ALL' or (cohort=='GLOBAL_UNSEEN' and e['global_unseen']) or (cohort=='GLOBAL_KNOWN' and not e['global_unseen']) or (cohort=='Q_ZERO' and e['q']==0) or (cohort=='H_POSITIVE' and e['h']>0) or (cohort=='H_ZERO' and e['h']==0)]
  leaves=collections.defaultdict(list)
  for e in rows:leaves[e['leaf']].append(e)
  per={str(leaf):sum(e['gain_m1'] for e in ev)/len(ev) for leaf,ev in sorted(leaves.items())};means_q={str(leaf):sum(e['gain_whole'] for e in ev)/len(ev) for leaf,ev in sorted(leaves.items())};n=len(rows);L=len(leaves);mean=sum(per.values())/L if L else None;pos=sum(x>0 for x in per.values());gate=n>=100 and L>=10 and mean>=.01 and pos*3>=2*L
  result[cohort]={'words':n,'leaves':L,'positive_leaves':pos,'equal_leaf_gain_m1':mean,'token_gain_m1':sum(e['gain_m1'] for e in rows)/n if n else None,'equal_leaf_gain_whole':sum(means_q.values())/L if L else None,'mean_mix_h_loss':-sum(math.log(e['mix_h']) for e in rows)/n if n else None,'per_leaf_gain_m1':per,'per_leaf_gain_whole':means_q,'material_gate':bool(gate)}
 return result

def fixtures():
 train={tuple(w):1 for w in ['aaaa','aabb','baba']};f=fit(train);ws=list(itertools.product('ab',repeat=4));mass=sum(Fraction(f[0][w[:2]],f[3])*Fraction(f[1][w[1]][w[2:]],f[2][w[1]]) if f[0][w[:2]] else 0 for w in ws);assert mass==1;assert prob(f,tuple('babb'))>0 and tuple('babb') not in train;assert prob(f,tuple('bbbb'))==0
 return {'status':'PASS','binary_words':16,'exact_mass':str(mass),'unseen_recombination':'babb','unsupported_left_zero':'bbbb'}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();old=R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts';model=read(old/'MODEL.json');events=read(old/'EVENTS.json.gz');all_scores=[];results={};tables={}
 for ed in ['ZL3b','IT2a','RF1b']:
  fits={};q={};known=set();table=[]
  for entry in model[ed]['whole']:
   cell=tuple(entry['cell']);counts={tuple(x['units']):x['count'] for x in entry['counts']};q[cell]=counts;known.update(counts);f=fit(counts);fits[cell]=f;left,right,end,N=f
   assert sum(Fraction(c,N)*Fraction(sum(right[l[-1]].values()),end[l[-1]]) for l,c in left.items())==1
   table.append({'cell':cell,'N':N,'left':[{'units':u,'count':c} for u,c in sorted(left.items())],'right':[{'last_left':a,'units':u,'count':c} for a,cnt in sorted(right.items()) for u,c in sorted(cnt.items())],'end':dict(sorted(end.items()))})
  tables[ed]=table;es=[]
  for e in events:
   if e['reader']!=ed:continue
   u=tuple(e['units']);cell=(e['c'],len(u));f=fits.get(cell);p=e['p'];h=prob(f,u) if f else 0;mh=(p+h)/2 if f else p;assert e['global_unseen']==(u not in known)
   es.append({**e,'h':h,'mix_h':mh,'gain_m1':math.log(mh/p),'gain_whole':math.log(mh/e['mix'])})
  cohorts=summarize(es);lead=cohorts['ALL']['material_gate'] and cohorts['GLOBAL_UNSEEN']['material_gate'];results[ed]={'cohorts':cohorts,'lead':lead,'train_cells':len(fits),'left_entries':sum(len(f[0]) for f in fits.values()),'right_seam_entries':sum(sum(len(v) for v in f[1].values()) for f in fits.values()),'whole_cell_entries':sum(len(v) for v in q.values())};all_scores.extend(es)
  print(ed,'lead',lead,'ALL',cohorts['ALL']['equal_leaf_gain_m1'],cohorts['ALL']['positive_leaves'],'UNSEEN',cohorts['GLOBAL_UNSEEN']['equal_leaf_gain_m1'],cohorts['GLOBAL_UNSEEN']['positive_leaves'],flush=True)
 save('MODEL_H.json',tables);save('EVENTS.json.gz',all_scores);save('RESULT.json',{'status':'PRODUCTIVE_HALF_FORM_LEAD' if results['ZL3b']['lead'] else 'NO_PRODUCTIVE_HALF_FORM_LEAD','fixtures':fx,'readers':results,'ceiling':'Fixed exposed predictive component only; midpoint fragments are not identified morphemes, a source encoder or word meanings.'})
if __name__=='__main__':main()
