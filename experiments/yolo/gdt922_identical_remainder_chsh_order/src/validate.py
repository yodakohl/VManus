#!/usr/bin/env python3
"""Independent same-remainder adjacency and full permutation replay."""
import json,hashlib,re,random,math
from pathlib import Path
from collections import defaultdict,Counter
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];OLD=E.parent/'gdt915_terminal_lr_phrase_transfer'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def eq(a,b):
 if isinstance(a,dict):assert a.keys()==b.keys();[eq(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b),(len(a),len(b));[eq(x,y) for x,y in zip(a,b)]
 elif isinstance(a,float):assert math.isclose(a,b,abs_tol=1e-13,rel_tol=1e-10),(a,b)
 else:assert a==b,(a,b)
def eligible(g):return bool(re.fullmatch('(ch|sh)[a-z]+',g['ivtff_group_raw'])) and g['left_separator'] in ['LINE_START','DEFINITE_SPACE'] and g['right_separator'] in ['LINE_END','DEFINITE_SPACE']
def position(i,n):return 'SINGLE' if n==1 else 'FIRST' if i==1 else 'LAST' if i==n else 'INTERNAL'
def cell(x,y):return ('C' if x else 'S')+('C' if y else 'S')
def cells(ps,ts):
 c=dict.fromkeys(['CC','CS','SC','SS'],0)
 for p in ps:c[cell(ts[p['a']]['x'],ts[p['b']]['x'])]+=1
 return c

def build(rows):
 ts=[];ps=[];strata=defaultdict(list)
 for m,gs in sorted(rows,key=lambda r:(r[0]['page'],int(r[0]['source_row_index']))):
  if m['kind']!='P':continue
  local={}
  for g in sorted(gs,key=lambda g:int(g['source_group_index'])):
   if not eligible(g):continue
   i=int(g['source_group_index']);n=int(m['source_group_count']);w=g['ivtff_group_raw'];leaf=re.match(r'f\d+',m['page'])[0];pos=position(i,n);key=(leaf,w[2:],pos);idx=len(ts)
   ts.append(dict(R=w[2:],id=g['source_group_id'],index=i,leaf=leaf,locus=m['locus'],page=m['page'],position=pos,row=int(m['source_row_index']),stratum=list(key),word=w,x=int(w.startswith('ch'))));local[i]=idx;strata[key].append(idx)
  for i,a in sorted(local.items()):
   if i+1 in local:
    b=local[i+1]
    if ts[a]['R']==ts[b]['R']:ps.append(dict(R=ts[a]['R'],a=a,b=b,leaf=ts[a]['leaf'],locus=m['locus'],primary=ts[a]['R'] not in ['or','ol'],words=[ts[a]['word'],ts[b]['word']]))
 ss=[];prob={};mobile=set()
 for key,ix in sorted(strata.items()):
  p=sum(ts[i]['x'] for i in ix)/len(ix);ss.append(dict(indices=ix,key=list(key),pCH=p))
  for i in ix:prob[i]=p
  if 0<p<1:mobile.update(ix)
 byR=defaultdict(list);byLeaf=defaultdict(list)
 for p in ps:
  byR[p['R']].append(p)
  if p['primary']:byLeaf[p['leaf']].append(p)
 rt=[];lt=[]
 for r,rs in sorted(byR.items()):rt.append(dict(R=r,cells=cells(rs,ts),leaves=sorted({p['leaf'] for p in rs}),primary=r not in ['or','ol'],witnesses=[dict(group_indices=[ts[p['a']]['index'],ts[p['b']]['index']],locus=p['locus'],words=p['words']) for p in rs]))
 for leaf,ls in sorted(byLeaf.items()):
  c=cells(ls,ts);lt.append(dict(T=(c['CS']-c['SC'])/len(ls),cells=c,leaf=leaf,mu=sum(prob[p['a']]-prob[p['b']] for p in ls)/len(ls),pairs=len(ls)))
 prim=[p for p in ps if p['primary']];nr=len({p['R'] for p in prim});nm=len({p['leaf'] for p in prim if p['a'] in mobile or p['b'] in mobile});t=sum(x['T'] for x in lt)/max(1,len(lt));mu=sum(x['mu'] for x in lt)/max(1,len(lt))
 stats=dict(T=t,all_pairs=len(ps),capacity=nr>=5 and nm>=5,cells=cells(prim,ts),eligible_tokens=len(ts),mobile_leaves=nm,mu=mu,primary_R_count=nr,primary_leaves=len(lt),primary_pairs=len(prim),residual=t-mu)
 return dict(R_table=rt,leaf_table=lt,pairs=ps,statistics=stats,strata=ss,tokens=ts)
def toys():
 assert position(1,1)=='SINGLE' and position(1,3)=='FIRST' and position(3,3)=='LAST' and position(2,3)=='INTERNAL'
 for x in [0,1]:
  for y in [0,1]:assert int(cell(x,y)=='CS')-int(cell(x,y)=='SC')==x-y
 for bits in [[1,0,1,0],[0,1,0],[1,1,0]]:assert sum(a-b for a,b in zip(bits,bits[1:]))==bits[0]-bits[-1]
 m=dict(kind='P',page='f1r',locus='f1r.1',source_row_index='1',source_group_count='3')
 def g(i,w):return dict(source_group_id=str(i),source_group_index=str(i),ivtff_group_raw=w,left_separator='DEFINITE_SPACE',right_separator='DEFINITE_SPACE')
 gs=[g(1,'chey'),g(2,'shey'),g(3,'chey')];c=build([(m,gs)]);assert c['statistics']['primary_pairs']==2 and c['statistics']['T']==0
 gs[1]['left_separator']='UNCERTAIN_SPACE';assert build([(m,gs)])['pairs']==[]
 assert not eligible(g(1,'ch')) and not eligible(g(1,'qchey'))
 return 11

def main():
 lock=load(E/'PREREG_LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 summaries={};primary=None
 for ed in ['ZL3b','IT2a','RF1b']:
  rows=[]
  for phase in ['DISCOVERY','EVALUATION']:
   d=load(OLD/'artifacts'/f'SOURCE_{phase}_{ed}.json')
   for row in d['lines']:
    m=row['metadata'];assert m['edition']==ed and not m['page'].startswith('f84')
    rows.append((m,[dict(zip(d['group_columns'],g)) for g in row['groups']]))
  c=build(rows);eq(c,load(E/'artifacts'/f'CENSUS_{ed}.json'));summaries[ed]=c['statistics']
  if ed=='ZL3b':primary=c
 c=primary;ts=c['tokens'];op=[p for p in c['pairs'] if p['primary']];den=Counter(p['leaf'] for p in op);coeff=defaultdict(float)
 for p in op:
  weight=1/len(den)/den[p['leaf']];coeff[p['a']]+=weight;coeff[p['b']]-=weight
 worlds=[]
 for j in range(1024):
  rng=random.Random(922000+j);bits=[t['x'] for t in ts]
  for s in c['strata']:
   ix=s['indices'];values=[bits[i] for i in ix];before=sum(values);rng.shuffle(values);assert sum(values)==before
   for i,v in zip(ix,values):bits[i]=v
  t=sum(weight*bits[i] for i,weight in coeff.items());r=t-c['statistics']['mu'];worlds.append(dict(T=t,absolute_residual=abs(r),residual=r,world=j))
 eq(worlds,load(E/'artifacts/WORLDS.json'));obs=abs(c['statistics']['residual']);ge=sum(w['absolute_residual']>=obs-1e-12 for w in worlds);nonconstant=max(w['T'] for w in worlds)-min(w['T'] for w in worlds)>1e-12;rank=(1+ge)/1025
 result=load(E/'artifacts/RESULT.json');eq(result['editions'],summaries);eq(result['rank_fraction'],rank);assert result['worlds_ge_observed']==ge and result['null_nonconstant']==nonconstant
 assert result['confirmed_meanings']==result['fresh_confirmation_leaves']==0 and result['status']=='ORDER_NOT_ESTABLISHED' and rank>.05
 receipt=dict(status='PASS',validator_sha256=sha(Path(__file__)),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),locked_files_verified=len(lock['files']),output_sha256={p.name:sha(p) for p in sorted((E/'artifacts').glob('*.json')) if p.name!='VALIDATION.json'},editions=summaries,worlds_replayed=1024,worlds_ge_observed=ge,rank_fraction=rank,synthetic_checks=toys(),scope='Full tokens, opportunities including CC/SS, sorted strata, R witnesses, leaf statistics and all worlds replayed. Independent endpoint-coefficient null evaluation preserves shared overlapping tokens. Written ordering not established; no semantic inference.')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
