#!/usr/bin/env python3
"""Core statistics for LRG006 conditional A1-member inference."""
from __future__ import annotations
import csv,hashlib
from dataclasses import dataclass
from pathlib import Path
import numpy as np
A=8192;SEED=60062026
@dataclass(frozen=True)
class Geometry:unit:np.ndarray;cell:np.ndarray;folio:np.ndarray;section:np.ndarray;quota:dict[str,int];cells:tuple[str,...];folios:tuple[str,...]
def ah(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def load(panel:Path,quotas:Path):
 p=tab(panel);q=tab(quotas)
 if len(p)!=677 or len(q)!=69 or len({r['unit_id'] for r in p})!=677:raise RuntimeError('geometry')
 quota={r['cell_id']:int(r['label_rows']) for r in q};total={r['cell_id']:int(r['total_rows']) for r in q};cell=np.asarray([r['cell_id'] for r in p]);folio=np.asarray([r['physical_folio'] for r in p]);section=np.asarray([r['section'] for r in p]);cells=tuple(sorted(quota));folios=tuple(sorted(set(folio),key=lambda x:int(x[1:])))
 for c in cells:
  idx=np.flatnonzero(cell==c)
  if len(idx)!=total[c] or not 0<quota[c]<len(idx) or len(set(folio[idx]))!=1 or len(set(section[idx]))!=1:raise RuntimeError('cell')
 if len(folios)!=13:raise RuntimeError('folios')
 return Geometry(np.asarray([r['unit_id'] for r in p]),cell,folio,section,quota,cells,folios)
def random_labels(g,rng):
 y=np.zeros(len(g.unit),dtype=np.int8)
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);h=g.quota[c];y[idx[np.argpartition(rng.random(len(idx)),h-1)[:h]]]=1
 return y
def coef(g):
 out=np.zeros((A,len(g.unit)));rng=np.random.default_rng(SEED)
 for c in g.cells:
  idx=np.flatnonzero(g.cell==c);f=str(g.folio[idx[0]]);nc=len(set(g.cell[g.folio==f]));h=g.quota[c];lo=len(idx)-h;out[:,idx]=-1/(len(g.folios)*nc*lo);chosen=idx[np.argpartition(rng.random((A,len(idx))),h-1,axis=1)[:,:h]];out[np.arange(A)[:,None],chosen]=1/(len(g.folios)*nc*h)
 if np.max(np.abs(out.sum(1)))>1e-12:raise RuntimeError('coefficient')
 return out
def folio_effects(x,y,g):
 out=[]
 for f in g.folios:
  vals=[]
  for c in sorted(set(g.cell[g.folio==f])):
   idx=np.flatnonzero(g.cell==c);hi=idx[y[idx]==1];lo=idx[y[idx]==0]
   if not len(hi) or not len(lo):raise RuntimeError('mixed')
   vals.append(float(x[hi].mean()-x[lo].mean()))
  out.append(float(np.mean(vals)))
 return np.asarray(out)
def evaluate(x,y,g,coefficient,null=None):
 if x.shape!=(len(g.unit),) or y.shape!=x.shape or set(np.unique(y))-{0,1} or not np.isfinite(x).all():raise RuntimeError('input')
 fe=folio_effects(x,y,g);t=float(fe.mean());n=np.asarray(coefficient@x if null is None else null);mu=float(n.mean());sd=float(n.std(ddof=0));z=(t-mu)/sd if sd>0 else 0.;p=(1+int(np.count_nonzero(np.abs(n)>=abs(t))))/(A+1);sign=1 if t>=0 else -1;nums=np.asarray([int(f[1:]) for f in g.folios]);sf=np.asarray([str(g.section[np.flatnonzero(g.folio==f)[0]]) for f in g.folios]);sec={s:sign*float(fe[sf==s].mean()) for s in ('B','P')};par={'ODD':sign*float(fe[nums%2==1].mean()),'EVEN':sign*float(fe[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');dele=[sign*float(np.delete(fe,k).mean()) for k in range(13)];den=float(np.abs(fe).sum());con=float(np.max(np.abs(fe))/den) if den else 1.;gates={'p_at_most_001':p<=.01,'absolute_z_at_least_3':abs(z)>=3,'absolute_effect_at_least_008':abs(t)>=.08,'directional_support_at_least_10':int(np.count_nonzero(sign*fe>0))>=10,'both_sections_signed_at_least_004':min(sec.values())>=.04,'section_balance_at_least_035':sb>=.35,'both_parities_signed_at_least_004':min(par.values())>=.04,'parity_balance_at_least_035':pb>=.35,'all_deletions_signed_at_least_004':min(dele)>=.04,'concentration_at_most_030':con<=.30};return {'effect':t,'direction':'A1_POSITIVE' if sign>0 else 'A1_NEGATIVE','null_mean':mu,'null_sd':sd,'z':z,'p':p,'positive_direction_folios':int(np.count_nonzero(sign*fe>0)),'folio_effects':{f:float(v) for f,v in zip(g.folios,fe,strict=True)},'signed_section_effects':sec,'section_balance_ratio':sb,'signed_parity_effects':par,'parity_balance_ratio':pb,'minimum_signed_deletion':min(dele),'maximum_absolute_folio_concentration':con,'null_sha256':ah(n),'feature_sha256':ah(x),'label_sha256':ah(y),'gates':gates,'passes':all(gates.values())}
