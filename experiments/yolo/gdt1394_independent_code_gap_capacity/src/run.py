#!/usr/bin/env python3
"""Frozen independent-code-gap model, historical fixed cohort; no glosses."""
import argparse, collections, hashlib, itertools, json, math, re
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
def read(p): return json.loads(p.read_text())
def save(p,x): p.write_text(json.dumps(x,indent=2)+'\n')
def pmf(N,M):
 assert 1<=M<=N
 if N==M:return {M:1},1
 den=math.comb(N-1,M-1); out={}
 for k in range(M+1):
  n=N-M-1;j=M-k-1
  if 0<=j<=n:out[k]=math.comb(M,k)*math.comb(n,j)
 assert sum(out.values())==den
 return out,den
def bound(ds,X,s):
 values=[]
 for lam in s['lambda_grid']:
  logs=[]
  for d,den in ds:
   ts=[math.log(v)-lam*k for k,v in d.items()];top=max(ts)
   logs.append(top+math.log(math.fsum(math.exp(t-top) for t in ts))-math.log(den))
  values.append(lam*X+math.fsum(logs))
 i=min(range(len(values)),key=lambda j:(values[j],j))
 return min(0.,values[i]+s['log_safety']),s['lambda_grid'][i]
def controls():
 checked=0
 for N in range(1,13):
  for M in range(1,N+1):
   got,den=pmf(N,M);ref=collections.Counter()
   for cut in itertools.combinations(range(1,N),M-1):
    pts=(0,)+cut+(N,);ref[sum(pts[j+1]-pts[j]==1 for j in range(M))]+=1
   assert got==dict(ref);checked+=den
 return {'status':'PASS','enumerated_compositions':checked,'native_access':False}
def projection(s):
 old=R/'experiments/yolo/gdt1259_paragraph_integer_balance';cert=read(old/'artifacts/CERTIFICATES.json');census=read(old/'artifacts/CENSUS.json')
 pat=re.compile('|'.join(sorted(s['working_signs'],key=lambda x:(-len(x),x))));data={}
 for reader in s['readers']:
  assert len(cert[reader])==23
  data[reader]=[];byid={p['id']:p for p in census[reader]}
  for entry in cert[reader]:
   p=entry['paragraph'];assert p==byid[p['id']]
   assert not p['page'].startswith('f84') and p['page'] not in ('f116v','f1r')
   groups=[];counts=collections.Counter()
   for g in entry['raw_groups']:
    raw=g['ivtff_group_raw'];units=pat.findall(raw);assert raw and ''.join(units)==raw
    counts.update(units);gid=reader+'|'+g['locus']+'|G'+str(int(g['source_group_index'])).zfill(3)
    groups.append({'id':gid,'raw':raw,'units':units})
   assert [counts[u] for u in s['working_signs']]==p['counts'] and len(groups)==p['groups']
   data[reader].append({'paragraph_id':p['id'],'page':p['page'],'leaf':re.match(r'f\d+',p['page']).group(),'groups':groups,'counts':p['counts']})
 return {'readers':data}
def case(paras,head,s):
 out={'head':head};rows=[];ds=[];total=0;expect=Fraction(0);var=0;vleaves=set();leaves={}
 for p in paras:
  sizes=[]
  for g in p['groups']:
   u=g['units'];i=0;count=0
   while i<len(u):
    if u[i]==head:
     reason='ESCAPE_AT_GROUP_END' if i+1==len(u) else ('DOUBLE_ESCAPE' if u[i+1]==head else None)
     if reason:
      out.update(status='INVALID_CARRIER',first_failure={'para':p['paragraph_id'],'group_id':g['id'],'raw':g['raw'],'reason':reason});return out
     i+=2
    else:i+=1
    count+=1
   sizes.append(count)
  N=sum(sizes);M=len(sizes);X=sizes.count(1);d,den=pmf(N,M)
  ex=sum((Fraction(k*v,den) for k,v in d.items()),Fraction(0));ds.append((d,den));total+=X;expect+=ex
  if len(d)>1:var+=1;vleaves.add(p['leaf'])
  leaf=leaves.setdefault(p['leaf'],[0,Fraction(0)]);leaf[0]+=X;leaf[1]+=ex
  rows.append({'id':p['paragraph_id'],'page':p['page'],'leaf':p['leaf'],'N':N,'M':M,'X':X,'expected_numerator':ex.numerator,'expected_denominator':ex.denominator,'pmf_support':sorted(d),'pmf_counts':[str(d[k]) for k in sorted(d)],'pmf_denominator':str(den)})
 logb,lam=bound(ds,total,s);ratio=float(Fraction(total)/expect) if expect else None
 capacity=var>=s['min_variable_paragraphs'] and len(vleaves)>=s['min_variable_leaves']
 reject=capacity and ratio is not None and ratio<=s['ratio_max'] and logb<=math.log(s['alpha']/s['correction'])
 out.update(status='SHORTFALL_REJECTED' if reject else ('NOT_REJECTED' if capacity else 'CAPACITY_STOP'),paragraphs=rows,total_X=total,expected_num=str(expect.numerator),expected_den=str(expect.denominator),ratio=ratio,log_bound=logb,best_lambda=lam,variable_paragraphs=var,variable_leaves=len(vleaves),leaf_summaries=[{'leaf':k,'total_X':v[0],'expected_num':str(v[1].numerator),'expected_den':str(v[1].denominator)} for k,v in sorted(leaves.items())])
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args()
 if a.controls:print(json.dumps(controls()));return
 lock=read(B/'LOCK.json')
 for f in lock['files']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
 s=read(B/'src/SPEC.json');data=projection(s);result={'readers':{}}
 for reader in s['readers']:
  cases=[case(data['readers'][reader],h,s) for h in s['working_signs']]
  valid=[x for x in cases if x['status']!='INVALID_CARRIER']
  excluded=all(x['status'] in ('INVALID_CARRIER','SHORTFALL_REJECTED') for x in cases)
  result['readers'][reader]={'status':'EXCLUDED' if excluded else 'NOT_EXCLUDED','cases':cases,'valid_heads':len(valid),'worst_log_bound':max((x['log_bound'] for x in valid),default=None)}
 result['status']='INDEPENDENT_CODE_GAP_MODEL_REJECTED' if all(x['status']=='EXCLUDED' for x in result['readers'].values()) else 'NOT_REJECTED'
 save(B/'artifacts/DATA.json',data);save(B/'artifacts/RESULT.json',result)
 print(json.dumps({'status':result['status'],'readers':{r:{k:v for k,v in x.items() if k!='cases'} for r,x in result['readers'].items()}},indent=2))
if __name__=='__main__':main()
