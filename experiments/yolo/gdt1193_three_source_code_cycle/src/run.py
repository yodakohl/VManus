from pathlib import Path
import sys,json,hashlib,os,importlib.util,bisect,heapq,time
import numpy as np
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';OLD=ROOT/'experiments/yolo/gdt1191_source_codebook_assignment'
sys.path.insert(0,str(OLD/'src'));spec=importlib.util.spec_from_file_location('assignment',OLD/'src/run.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
MODEL='H2048-S6-K7';CAP=2048;LIMIT=2000

def save(n,x):(A/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def prepare():
 source=json.loads(w.engine.SOURCE.read_text());tables=json.loads(w.engine.TABLES.read_text());targets=json.loads(w.engine.TARGET.read_text())['targets'];base=json.loads((OLD/'artifacts/RESULT.json').read_text())['models'][MODEL];codec=w.c.Codec(MODEL,tables,base['alphabets'],base['assignment']);cache=w.fast.Cache(codec,source);return source,tables,targets,base,codec,cache

def tv_interval(ra,rb,rc,base_l1,fi,fj,orientation,budget=3200):
 if orientation==0:p=fi-ra;q=rc+fj;r=budget-(base_l1-abs(ra)-abs(rb)-abs(rc))-abs(rb-fj+fi)
 else:p=fj-rb;q=rc+fi;r=budget-(base_l1-abs(ra)-abs(rb)-abs(rc))-abs(ra-fi+fj)
 return -((-(p+q-r))//2),(p+q+r)//2,r>=abs(p-q)

class Ranges:
 def __init__(self,values):
  groups={}
  for n,v in enumerate(values):groups[int(v)]=groups.get(int(v),0)|(1<<n)
  self.values=sorted(groups);self.prefix=[0]
  for v in self.values:self.prefix.append(self.prefix[-1]|groups[v])
 def between(self,lo,hi):
  if lo>hi:return 0
  return self.prefix[bisect.bisect_right(self.values,int(hi))]&~self.prefix[bisect.bisect_left(self.values,int(lo))]

def candidates(cache,base,targets,progress=False):
 U=len(base['assignment']);lens=cache.lengths[np.array(base['assignment'])].astype(np.int64);freq=np.stack([np.bincount(cache.books[b][:,0],minlength=U) for b in w.BOOKS],axis=1).astype(np.int64);tot=freq.sum(axis=1);W=max(int(lens.max()),max(int(k) for t in targets.values() for k in t['length_counts']))+1
 hs=np.stack([np.bincount(lens[cache.books[b][:,0]],minlength=W) for b in w.BOOKS]);sums=hs@np.arange(W);th=np.stack([np.array([t['length_counts'].get(str(k),0) for k in range(W)]) for t in targets.values()]);res=hs[:,None,:]-th[None,:,:];l1=abs(res).sum(axis=2)
 possible=np.arange(8000*W+1,dtype=np.int64);ok=np.ones(len(possible),bool)
 for t in targets.values():ok&=abs(possible/8000-t['mean_length'])<=.2*t['mean_length']+1e-12
 valid=possible[ok];assert len(valid) and np.all(np.diff(valid)==1);lower=int(valid[0]);upper=int(valid[-1]);classes={int(l):np.flatnonzero(lens==l) for l in np.unique(lens)};lengths=sorted(classes);ranges={l:[Ranges(freq[ids,b]) for b in range(4)]+[Ranges(tot[ids])] for l,ids in classes.items()};heap=[];survivors=0;pair_count=0;theoretical=0;started=time.monotonic()
 for ai,a in enumerate(lengths):
  for bi in range(ai+1,len(lengths)):
   b=lengths[bi];js=classes[b];fj=freq[js];
   for c in lengths[bi+1:]:
    ks=classes[c];theoretical+=2*len(classes[a])*len(js)*len(ks)
    for orientation in (0,1):
     for i in classes[a]:
      fi=freq[i];pair_count+=len(js);costij=tot[i]+tot[js];keep=costij<=CAP;lo=np.zeros((len(js),4),dtype=np.int64);hi=np.full_like(lo,8000)
      if orientation==0:K=sums+fi*(b-a)+fj*(c-b);delta=c-a
      else:K=sums+fi*(c-a)+fj*(a-b);delta=c-b
      lo=np.maximum(lo,-((-(K-upper))//delta));hi=np.minimum(hi,(K-lower)//delta)
      for ed in range(len(targets)):
       rr=res[:,ed,:];tl,tu,valid_tv=tv_interval(rr[:,a],rr[:,b],rr[:,c],l1[:,ed],fi,fj,orientation);lo=np.maximum(lo,tl);hi=np.minimum(hi,tu);keep&=np.all(valid_tv,axis=1)
      keep&=np.all(lo<=hi,axis=1)
      for ji in np.flatnonzero(keep):
       j=int(js[ji]);mask=ranges[c][4].between(0,CAP-int(costij[ji]))
       for book in range(4):mask&=ranges[c][book].between(lo[ji,book],hi[ji,book])
       survivors+=mask.bit_count()
       while mask:
        bit=mask&-mask;ki=bit.bit_length()-1;k=int(ks[ki]);item=(int(costij[ji]+tot[k]),int(i),j,k,orientation);negative=tuple(-z for z in item)
        if len(heap)<LIMIT:heapq.heappush(heap,negative)
        elif negative>heap[0]:heapq.heapreplace(heap,negative)
        mask-=bit
    if progress:print(json.dumps({'lengths':[a,b,c],'survivors':survivors,'seconds':round(time.monotonic()-started,2)}),flush=True)
 result=sorted([[-z for z in item] for item in heap]);summary={'units':U,'distinct_length_cycles_before_cost_filter':int(theoretical),'pair_range_queries':int(pair_count),'cost_cap':CAP,'mean_tv_survivors':survivors,'retained':len(result),'integer_mean_total_range':[lower,upper],'length_classes':{str(l):len(v) for l,v in classes.items()},'histograms':{book:{str(k):int(v) for k,v in enumerate(hs[n]) if v} for n,book in enumerate(w.BOOKS)}};return result,summary

def apply_cycle(base,row):
 _,i,j,k,orientation=row;p=base['assignment'][:]
 if orientation==0:p[i],p[j],p[k]=p[j],p[k],p[i]
 else:p[i],p[j],p[k]=p[k],p[i],p[j]
 return p

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source,tables,targets,base,codec,cache=prepare();rows,summary=candidates(cache,base,targets,True);save('LENGTH_FILTER.json',summary);save('CANDIDATES.json',rows);tested=[];selected=None
 for rank,row in enumerate(rows):
  p=apply_cycle(base,row);energy,full,met,comp,tight=w.evaluate(cache,p,base['alphabets'],targets);tested.append({'rank':rank,'cycle':row,'energy':energy,'full_pass':full})
  if full:
   selected={'rank':rank,'cycle':row,'source_entries':[codec.units[u] for u in row[1:4]],'assignment':p,'alphabets':base['alphabets'],'metrics':met,'comparison':comp,'tight_edit1':tight,'energy':energy};break
  if rank%100==0:print(json.dumps(tested[-1]),flush=True);save('TESTED.json',tested)
 if selected:
  writer=w.c.Codec(MODEL,tables,selected['alphabets'],selected['assignment']);roundtrips=0
  for book in w.BOOKS:
   ps,_=w.engine.pages(writer,source[book]);w.fast.close(w.engine.measure(ps),selected['metrics'][book]);roundtrips+=len(source[book]);(A/(book+'.txt')).write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in ps)+'\n')
  selected['complete_recipe_roundtrips']=roundtrips;save('PUBLIC_TABLE.json',{'model':MODEL,'alphabets':selected['alphabets'],'entries':{u:{'rank':r,'tail':list(ds)} for u,(r,ds) in writer.encoded.items()},'rules':'Longest matching literal source fragment, no cross-word match. Source character count modulo6 rotates initial rank modulo7. Public initial styles: recipe first, after punctuation, otherwise. E/C marks source word end/continuation. Visible group spaces and recipe resets.'})
 status='FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS' if selected else 'THREE_CYCLE_COST_CAPPED_FILTER_FAILS' if summary['mean_tv_survivors']==0 else 'THREE_CYCLE_BOUNDED_PREFIX_FAILS'
 result={'experiment':'GDT1193','status':status,'model':MODEL,'filter':summary,'tested_count':len(tested),'all_filtered_examined':len(tested)==summary['mean_tv_survivors'],'selected':selected,'claim_ceiling':'Artificial fitted source-control writer under known basic summaries; no native meanings, independent confirmation, historical usability or stronger structural fit.'};save('TESTED.json',tested);save('RESULT.json',result);print(json.dumps({'status':status,'tested_count':len(tested),'selected_rank':None if selected is None else selected['rank']}),flush=True)
if __name__=='__main__':main()
