import numpy as np
from functools import lru_cache
from common import *
class Fast:
 def __init__(self,cache,base):
  self.cache=cache;self.base=base;self.data={};self.pools={};self.assignment=np.array(base['assignment']);self.codebodies=[(cache.pool[i,1:int(cache.lengths[i])-1]-22).tolist() for i in range(len(cache.pool))];self.contexts={d:np.array([context(body,d) for body in self.codebodies]) for d in (1,2)}
  for b,data in cache.books.items():
   ids=self.assignment[data[:,0]];initial=data[:,2]*7+(cache.pool[ids,0]+data[:,1])%7;self.data[b]=(ids,initial,data[:,3],data[:,4]);
  for mask in range(512):
   bodies=[contract(body,mask) for body in self.codebodies];width=max(map(len,bodies));matrix=np.full((len(bodies),width),-1,dtype=np.int16);lengths=np.array(list(map(len,bodies)),dtype=np.int16)
   for i,body in enumerate(bodies):matrix[i,:len(body)]=body
   self.pools[mask]=(matrix,lengths)
 @lru_cache(maxsize=24)
 def virtual(self,depth,mask,qpos):
  output={};pool,bodylen=self.pools[mask]
  for b,(ids,initial,cont,recipes) in self.data.items():
   n=len(ids);guard=initial==qpos;offset=1+guard.astype(np.int16);lengths=2+bodylen[ids]+guard;mat=np.full((n,int(lengths.max())),-1,dtype=np.int16);rows=np.arange(n);mat[:,0]=initial;mat[guard,1]=21;bb=pool[ids]
   for j in range(pool.shape[1]):
    keep=bb[:,j]>=0;mat[rows[keep],offset[keep]+j]=22+bb[keep,j]
   finals=self.cache.pool[ids,self.cache.lengths[ids]-1]-25+3*cont;mat[rows,lengths-1]=34+6*self.contexts[depth][ids]+finals;output[b]=(mat,lengths,recipes)
  return output
 def metrics(self,p):
  mapping=np.array([SIGNS.index(g) for g in p['initial'][:21]+['o']+p['body'][:12]+[g for row in p['final'] for g in row[:6]]],dtype=np.int16);out={}
  for b,(mat,lengths,recipes) in self.virtual(p['depth'],p['mask'],p['qpos']).items():
   mm=mat.copy();valid=mm>=0;mm[valid]=mapping[mm[valid]];out[b]=w.fast.measure(mm,lengths,recipes,SIGNS)
  return out
 def candidates(self,targets):
  out=[];qcounts={q:{b:int((data[1]==q).sum()) for b,data in self.data.items()} for q in range(7)}
  for q in range(7):
   if not all(abs(count-t['q_count'])<=.25*t['q_count'] for count in qcounts[q].values() for t in targets.values()):continue
   for mask,(pool,bodylens) in self.pools.items():
    valid=True;energy=0
    for b,(ids,initial,cont,recipes) in self.data.items():
     lengths=2+bodylens[ids]+(initial==q);mean=float(lengths.mean());sd=float(lengths.std());hist=np.bincount(lengths)
     for t in targets.values():
      tv=sum(abs((int(hist[k]) if k<len(hist) else 0)-t['length_counts'].get(str(k),0)) for k in range(max(len(hist),1+max(map(int,t['length_counts'])))))/16000
      ratios=[abs(mean-t['mean_length'])/(.2*t['mean_length']),abs(sd-t['sd_length'])/(.25*t['sd_length']),tv/.2];valid&=all(v<=1+1e-12 for v in ratios);energy+=sum(z*z for z in ratios)
    if valid:out.append([energy,mask,q])
  out.sort();return out,qcounts
 def y_counts(self,depth):
  counts=np.zeros((4,4 if depth==1 else 13,6),dtype=np.int64)
  for bi,b in enumerate(BOOKS):
   ids,initial,cont,recipes=self.data[b];ctx=self.contexts[depth][ids];cat=self.cache.pool[ids,self.cache.lengths[ids]-1]-25+3*cont;np.add.at(counts[bi],(ctx,cat),1)
  return counts
