from collections import Counter
import math
import numpy as np
from codec import SIGNS
BOOKS=['b4','w1','bs1','gr1']
def close(a,b):
 if isinstance(a,dict):
  assert set(a)==set(b),(set(a)^set(b));[close(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b);[close(x,y) for x,y in zip(a,b)]
 elif isinstance(a,float):assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
 else:assert a==b,(a,b)
def js(a,b):
 p=a/a.sum();q=b/b.sum();mid=(p+q)/2;pa=p>0;qa=q>0
 return float(.5*((p[pa]*np.log2(p[pa]/mid[pa])).sum()+(q[qa]*np.log2(q[qa]/mid[qa])).sum()))
def ent(counts):
 p=counts[counts>0]/counts.sum();return float(-(p*np.log2(p)).sum())
def adjacency(lengths,recipes):
 keep=np.zeros(len(lengths)-1,dtype=bool);size=0;previous=-1
 for i,(length,recipe) in enumerate(zip(lengths.tolist(),recipes.tolist())):
  if recipe!=previous:size=0
  if size and size+1+length<=48:keep[i-1]=True;size+=1+length
  else:size=length
  previous=recipe
 return keep

def measure(matrix,lengths,recipes,signs):
 n=len(matrix);width=matrix.shape[1];packed=np.ascontiguousarray(matrix,dtype=np.int8).view(f'V{width}').ravel();_,counts=np.unique(packed,return_counts=True)
 gc=np.bincount(matrix[matrix>=0],minlength=22);first=np.bincount(matrix[:,0],minlength=22);last=np.bincount(matrix[np.arange(n),lengths-1],minlength=22);lc=np.bincount(lengths);left=matrix[:,:-1];right=matrix[:,1:];ok=(left>=0)&(right>=0);bc=np.bincount(left[ok]*22+right[ok],minlength=484).reshape(22,22);prev=bc.sum(axis=1);rows,cols=np.nonzero(bc);values=bc[rows,cols];h2=float(-(values*np.log2(values/prev[rows])).sum()/bc.sum())
 keep=adjacency(lengths,recipes);a=matrix[:-1][keep];b=matrix[1:][keep];la=lengths[:-1][keep];lb=lengths[1:][keep];different=(a!=b).sum(axis=1);equal=la==lb;one=equal&(different==1);unequal=abs(la-lb)==1
 if unequal.any():
  x=a[unequal].copy();y=b[unequal].copy();lx=la[unequal];ly=lb[unequal];swap=lx<ly;tmp=x[swap].copy();x[swap]=y[swap];y[swap]=tmp;short=np.minimum(lx,ly);firstdiff=np.argmax(x!=y,axis=1);positions=np.arange(width)[None,:];indices=np.minimum(positions+(positions>=firstdiff[:,None]),width-1);deleted=np.take_along_axis(x,indices,axis=1);one[unequal]=((deleted==y)|(positions>=short[:,None])).all(axis=1)
 q=signs.index('q');yindex=signs.index('y');o=signs.index('o')
 return {'tokens':n,'types':len(counts),'type_ratio':len(counts)/n,'mean_length':float(lengths.mean()),'sd_length':float(lengths.std()),'top10_share':int(np.sort(counts)[-10:].sum())/n,'word_entropy':ent(counts),'glyph_entropy':ent(gc),'conditional_entropy':h2,'first_last_js':js(first,last),'adjacent_pairs':int(keep.sum()),'exact_repeat':int((different==0).sum())/int(keep.sum()),'edit1_repeat':int(one.sum())/int(keep.sum()),'glyph_counts':{g:int(gc[i]) for i,g in enumerate(signs) if gc[i]},'length_counts':{str(i):int(v) for i,v in enumerate(lc) if v},'q_followed_o':float(bc[q,o]/prev[q]) if prev[q] else None,'q_count':int(gc[q]),'y_final':float(last[yindex]/n)}

class Cache:
 def __init__(self,codec,source):
  self.signs=SIGNS[:];self.unit_index={u:i for i,u in enumerate(codec.units)};self.width=max(1+len(ds) for _,ds in codec.pool);self.pool=np.full((len(codec.pool),self.width),-1,dtype=np.int16);self.lengths=np.empty(len(codec.pool),dtype=np.int16)
  for i,(rank,ds) in enumerate(codec.pool):
   self.lengths[i]=len(ds)+1;self.pool[i,0]=rank
   for j,d in enumerate(ds,1):self.pool[i,j]=(25 if j==len(ds) else 22)+d
  self.books={};self.neighbors=[];self.observed=set()
  for book in BOOKS:
   data=[]
   for recipe_index,recipe in enumerate(source[book]):
    state=0;previous=None
    for word in recipe['words']:
     units=codec.split(word)
     for j,u in enumerate(units):
      style=1 if previous is None else 2 if previous in '.,;:!?' else 0;data.append([self.unit_index[u],state,style,int(j!=len(units)-1),recipe_index]);state=(state+len(u))%6;previous=u[-1]
      if len(data)==8000:break
     if len(data)==8000:break
    if len(data)==8000:break
   assert len(data)==8000;data=np.array(data,dtype=np.int32);self.books[book]=data;self.observed.update(data[:,0].tolist())
   for a,b in zip(data,data[1:]):
    if a[4]==b[4]:self.neighbors.append((int(a[0]),int(b[0])))
  self.observed=sorted(self.observed);bytail={}
  for i,(rank,ds) in enumerate(codec.pool):bytail.setdefault(ds,[]).append(i)
  self.alternatives={i:[j for j in bytail[ds] if codec.pool[j][0]!=rank] for i,(rank,ds) in enumerate(codec.pool)}
 def matrices(self,assignment,alph):
  assignment=np.asarray(assignment);mapping=np.array([self.signs.index(g) for g in alph['initial']+alph['medial'][:3]+alph['final'][:6]],dtype=np.int16)
  for book,data in self.books.items():
   ids=assignment[data[:,0]];mat=self.pool[ids].copy();lengths=self.lengths[ids];rows=np.arange(len(data));mat[:,0]=data[:,2]*7+(mat[:,0]+data[:,1])%7;mat[rows,lengths-1]+=3*data[:,3];valid=mat>=0;mat[valid]=mapping[mat[valid]]
   yield book,mat,lengths,data[:,4]
 def metrics(self,assignment,alph):return {b:measure(mat,l,r,self.signs) for b,mat,l,r in self.matrices(assignment,alph)}
