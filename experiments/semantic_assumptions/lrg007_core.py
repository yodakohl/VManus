#!/usr/bin/env python3
"""Target-free core for LRG007 A/D edge-transfer inference."""
from __future__ import annotations
import csv,hashlib
from dataclasses import dataclass
from pathlib import Path
import numpy as np
A=8192;SEED=70072026
@dataclass(frozen=True)
class Geometry:
 unit:np.ndarray;cell:np.ndarray;folio:np.ndarray;section:np.ndarray;position:np.ndarray;cells:tuple[str,...];folios:tuple[str,...];margins:dict[str,tuple[int,int,int,int]]
def ah(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def load(panel:Path,margins:Path):
 p=tab(panel);q=tab(margins)
 if len(p)!=4911 or len(q)!=132 or len({r['unit_id'] for r in p})!=4911:raise RuntimeError('geometry')
 cell=np.asarray([r['cell_id'] for r in p]);folio=np.asarray([r['physical_folio'] for r in p]);section=np.asarray([r['section'] for r in p]);position=np.asarray([r['position'] for r in p]);cells=tuple(sorted({r['cell_id'] for r in p}));folios=tuple(sorted(set(folio),key=lambda z:int(z[1:])));m={r['cell_id']:(int(r['A_rows']),int(r['D_rows']),int(r['other_rows']),int(r['total_rows'])) for r in q}
 if len(cells)!=132 or len(folios)!=16 or set(cells)!=set(m):raise RuntimeError('counts')
 for c in cells:
  idx=np.flatnonzero(cell==c);a,d,o,n=m[c]
  if len(idx)!=n or a+d+o!=n or min(a,d,o)<0 or {'FIRST','CORE','LAST'}-set(position[idx]) or len(set(folio[idx]))!=1 or len(set(section[idx]))!=1:raise RuntimeError('cell')
 return Geometry(np.asarray([r['unit_id'] for r in p]),cell,folio,section,position,cells,folios,m)
def weights(g):
 w=np.zeros((len(g.unit),2));counts={f:len(set(g.cell[g.folio==f])) for f in g.folios}
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);f=str(g.folio[idx[0]]);base=1/(len(g.folios)*counts[f]);first=idx[g.position[idx]=='FIRST'];core=idx[g.position[idx]=='CORE'];last=idx[g.position[idx]=='LAST'];w[first,0]=base/len(first);w[core,0]=-base/len(core);w[last,1]=base/len(last);w[core,1]=-base/len(core)
 return w
def null_orbit(g,w):
 rng=np.random.default_rng(SEED);out=np.zeros((A,2))
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);a,d,o,n=g.margins[c];values=np.asarray([1]*a+[-1]*d+[0]*o,dtype=np.int8);order=np.argsort(rng.random((A,n)),axis=1);out+=values[order]@w[idx]
 return out
def synthetic(g,kind,i,kinds):
 rng=np.random.default_rng(7_000_000+1000*kinds.index(kind)+i);x=np.zeros(len(g.unit),dtype=np.int8)
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);a,d,_o,_n=g.margins[c];pos=g.position[idx];u=np.zeros(len(idx));amp=0.
  if kind=='BOTH_FULL':u=np.where(pos=='CORE',-1.,1.);amp=3.
  elif kind=='BOTH_REDUCED':u=np.where(pos=='CORE',-1.,1.);amp=1.8
  elif kind=='FIRST_ONLY':u=(pos=='FIRST').astype(float);amp=3.
  elif kind=='LAST_ONLY':u=(pos=='LAST').astype(float);amp=3.
  elif kind=='ONE_FOLIO':u=np.where(pos=='CORE',-1.,1.);amp=3.;u*=g.folio[idx]==g.folios[0]
  elif kind=='ONE_SECTION':u=np.where(pos=='CORE',-1.,1.);amp=3.;u*=g.section[idx]=='B'
  elif kind=='ONE_PARITY':u=np.where(pos=='CORE',-1.,1.);amp=3.;u*=int(str(g.folio[idx[0]])[1:])%2==0
  elif kind=='FOLIO_RANDOM':
   sign=1 if hashlib.sha256(f'{i}|{g.folio[idx[0]]}'.encode()).digest()[0]&1 else -1;u=sign*np.where(pos=='CORE',-1.,1.);amp=3.
  elif kind=='OPPOSITE_EDGES':u=np.where(pos=='FIRST',1.,np.where(pos=='LAST',-1.,0.));amp=3.
  elif kind=='REVERSED':u=np.where(pos=='CORE',1.,-1.);amp=3.
  elif kind!='NULL':raise RuntimeError(kind)
  priority=rng.standard_normal(len(idx))+amp*u;order=np.argsort(priority)
  if d:x[idx[order[:d]]]=-1
  if a:x[idx[order[-a:]]]=1
 return x
def folio_effects(x,g):
 out=[]
 for f in g.folios:
  values=[]
  for c in sorted(set(g.cell[g.folio==f])):
   idx=np.flatnonzero(g.cell==c);values.append((float(x[idx[g.position[idx]=='FIRST']].mean()-x[idx[g.position[idx]=='CORE']].mean()),float(x[idx[g.position[idx]=='LAST']].mean()-x[idx[g.position[idx]=='CORE']].mean())))
  out.append(np.asarray(values).mean(0))
 return np.stack(out)
def evaluate(x,g,w,null):
 if x.shape!=(len(g.unit),) or not set(np.unique(x))<={-1,0,1}:raise RuntimeError('feature')
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);a,d,o,_=g.margins[c]
  if (int(np.count_nonzero(x[idx]==1)),int(np.count_nonzero(x[idx]==-1)),int(np.count_nonzero(x[idx]==0)))!=(a,d,o):raise RuntimeError('margin')
 fe=folio_effects(x,g);afe=folio_effects((x==1).astype(float),g);dfe=-folio_effects((x==-1).astype(float),g);t=fe.mean(0);mu=null.mean(0);sd=null.std(0,ddof=0)
 if np.any(sd<=0) or not np.isfinite(null).all():raise RuntimeError('numeric')
 z=(t-mu)/sd;nz=(null-mu)/sd;mx=nz.max(1);nums=np.asarray([int(f[1:]) for f in g.folios]);sf=np.asarray([str(g.section[np.flatnonzero(g.folio==f)[0]]) for f in g.folios]);metrics=[]
 for j,name in enumerate(('FIRST_MINUS_CORE','LAST_MINUS_CORE')):
  vals=fe[:,j];p=(1+int(np.count_nonzero(mx>=z[j])))/(A+1);sec={s:float(vals[sf==s].mean()) for s in ('B','P')};par={'ODD':float(vals[nums%2==1].mean()),'EVEN':float(vals[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');dele=[float(np.delete(vals,k).mean()) for k in range(len(g.folios))];den=float(np.abs(vals).sum());con=float(np.max(np.abs(vals))/den) if den else 1.;ac=float(afe[:,j].mean());dc=float(dfe[:,j].mean());gates={'fwer_p_at_most_001':p<=.01,'z_at_least_3':z[j]>=3,'effect_at_least_008':t[j]>=.08,'positive_folios_at_least_12':int(np.count_nonzero(vals>0))>=12,'both_sections_at_least_004':min(sec.values())>=.04,'section_balance_at_least_025':sb>=.25,'both_parities_at_least_004':min(par.values())>=.04,'parity_balance_at_least_035':pb>=.35,'all_deletions_at_least_004':min(dele)>=.04,'concentration_at_most_030':con<=.30,'A_component_at_least_0015':ac>=.015,'D_component_at_least_0015':dc>=.015};metrics.append({'channel':name,'effect':float(t[j]),'null_mean':float(mu[j]),'null_sd':float(sd[j]),'z':float(z[j]),'fwer_p':p,'positive_folios':int(np.count_nonzero(vals>0)),'folio_effects':{f:float(v) for f,v in zip(g.folios,vals,strict=True)},'section_effects':sec,'section_balance_ratio':sb,'parity_effects':par,'parity_balance_ratio':pb,'minimum_deletion':min(dele),'maximum_absolute_folio_concentration':con,'A_component':ac,'D_component':dc,'gates':gates,'passes':all(gates.values())})
 return {'metrics':metrics,'joint_pass':all(m['passes'] for m in metrics),'feature_sha256':ah(x),'null_sha256':ah(null),'weight_sha256':ah(w)}
