#!/usr/bin/env python3
"""Core statistics for LRG005 joint D1-extension calibration and target."""
from __future__ import annotations
import csv,hashlib
from dataclasses import dataclass
from pathlib import Path
import numpy as np

ASSIGNMENTS=8192
SEED=510052026
CHANNELS=("D1_BARE","D1_OTHER")

@dataclass(frozen=True)
class Geometry:
    unit_ids:np.ndarray;cell_ids:np.ndarray;folios:np.ndarray;sections:np.ndarray
    labels_per_cell:dict[str,int];cells:tuple[str,...];folio_names:tuple[str,...]

def array_hash(a:np.ndarray)->str:return hashlib.sha256(np.ascontiguousarray(a).tobytes(order="C")).hexdigest()

def _table(path:Path)->list[dict[str,str]]:
    with path.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))

def load_geometry(panel_path:Path,quota_path:Path)->Geometry:
    p=_table(panel_path);q=_table(quota_path)
    if len(p)!=536 or len(q)!=68 or len({r["unit_id"] for r in p})!=536 or len({r["cell_id"] for r in q})!=68:raise RuntimeError("geometry count drift")
    quota={r["cell_id"]:int(r["label_rows"]) for r in q};total={r["cell_id"]:int(r["total_rows"]) for r in q}
    by={c:[] for c in quota}
    for i,r in enumerate(p):
        if r["cell_id"] not in by or r["section"] not in {"B","P"}:raise RuntimeError("geometry category drift")
        by[r["cell_id"]].append(i)
    for c,idx in by.items():
        if len(idx)!=total[c] or not 0<quota[c]<len(idx):raise RuntimeError("quota drift")
        if len({p[i]["physical_folio"] for i in idx})!=1 or len({p[i]["section"] for i in idx})!=1:raise RuntimeError("mixed cell metadata")
    folios=tuple(sorted({r["physical_folio"] for r in p},key=lambda x:int(x[1:])))
    if len(folios)!=13:raise RuntimeError("folio drift")
    return Geometry(np.asarray([r["unit_id"] for r in p]),np.asarray([r["cell_id"] for r in p]),np.asarray([r["physical_folio"] for r in p]),np.asarray([r["section"] for r in p]),quota,tuple(sorted(quota)),folios)

def random_labels(g:Geometry,rng:np.random.Generator)->np.ndarray:
    y=np.zeros(len(g.unit_ids),dtype=np.int8)
    for c in g.cells:
        idx=np.flatnonzero(g.cell_ids==c);h=g.labels_per_cell[c];ranks=rng.random(len(idx));chosen=idx[np.argpartition(ranks,h-1)[:h]];y[chosen]=1
    return y

def assignment_coefficients(g:Geometry)->np.ndarray:
    out=np.zeros((ASSIGNMENTS,len(g.unit_ids)),dtype=np.float64);rng=np.random.default_rng(SEED)
    for c in g.cells:
        idx=np.flatnonzero(g.cell_ids==c);f=str(g.folios[idx[0]]);cell_count=len(set(g.cell_ids[g.folios==f]));h=g.labels_per_cell[c];lo=len(idx)-h
        out[:,idx]=-1.0/(len(g.folio_names)*cell_count*lo)
        ranks=rng.random((ASSIGNMENTS,len(idx)));chosen_local=np.argpartition(ranks,h-1,axis=1)[:,:h];chosen=idx[chosen_local]
        out[np.arange(ASSIGNMENTS)[:,None],chosen]=1.0/(len(g.folio_names)*cell_count*h)
    if not np.isfinite(out).all() or np.max(np.abs(out.sum(axis=1)))>1e-12:raise RuntimeError("coefficient failure")
    return out

def folio_effects(scores:np.ndarray,y:np.ndarray,g:Geometry)->np.ndarray:
    if scores.shape!=(len(y),2) or set(np.unique(y))- {0,1} or not np.isfinite(scores).all():raise RuntimeError("invalid score input")
    result=[]
    for f in g.folio_names:
        values=[]
        for c in sorted(set(g.cell_ids[g.folios==f])):
            idx=np.flatnonzero(g.cell_ids==c);hi=idx[y[idx]==1];lo=idx[y[idx]==0]
            if not len(hi) or not len(lo):raise RuntimeError("unmixed observed cell")
            values.append(scores[hi].mean(axis=0)-scores[lo].mean(axis=0))
        result.append(np.stack(values).mean(axis=0))
    return np.stack(result)

def evaluate(scores:np.ndarray,y:np.ndarray,g:Geometry,coef:np.ndarray,null_values:np.ndarray|None=None)->dict[str,object]:
    effects=folio_effects(scores,y,g);observed=effects.mean(axis=0)
    null=np.asarray(coef@scores if null_values is None else null_values,dtype=np.float64)
    if null.shape!=(ASSIGNMENTS,2) or not np.isfinite(null).all():raise RuntimeError("null shape")
    metrics=[]
    nums=np.asarray([int(f[1:]) for f in g.folio_names]);section_by_folio=np.asarray([str(g.sections[np.flatnonzero(g.folios==f)[0]]) for f in g.folio_names])
    for j,name in enumerate(CHANNELS):
        vals=effects[:,j];t=float(observed[j]);mu=float(null[:,j].mean());sd=float(null[:,j].std(ddof=0));p=(1+int(np.count_nonzero(null[:,j]>=t)))/(ASSIGNMENTS+1);z=(t-mu)/sd if sd>0 else float("-inf")
        sections={s:float(vals[section_by_folio==s].mean()) for s in ("B","P")};parity={"ODD":float(vals[nums%2==1].mean()),"EVEN":float(vals[nums%2==0].mean())};deletions=[float(np.delete(vals,k).mean()) for k in range(len(vals))];den=float(np.abs(vals).sum());concentration=float(np.max(np.abs(vals))/den) if den else 1.0
        gates={"p_at_most_001":p<=.01,"z_at_least_3":z>=3,"effect_at_least_010":t>=.10,"support_at_least_10":int(np.count_nonzero(vals>0))>=10,"both_sections_at_least_005":min(sections.values())>=.05,"both_parities_at_least_005":min(parity.values())>=.05,"all_deletions_at_least_005":min(deletions)>=.05,"concentration_at_most_025":concentration<=.25}
        metrics.append({"channel":name,"effect":t,"null_mean":mu,"null_sd":sd,"z":z,"p":p,"positive_folios":int(np.count_nonzero(vals>0)),"folio_effects":{f:float(v) for f,v in zip(g.folio_names,vals,strict=True)},"section_effects":sections,"parity_effects":parity,"minimum_deletion":min(deletions),"maximum_absolute_folio_concentration":concentration,"null_sha256":array_hash(null[:,j]),"gates":gates,"passes":all(gates.values())})
    return {"metrics":metrics,"joint_pass":all(m["passes"] for m in metrics),"score_sha256":array_hash(scores),"label_sha256":array_hash(y)}
