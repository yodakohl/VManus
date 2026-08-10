#!/usr/bin/env python3
"""Simultaneous held-folio initial-family discovery core for LRG004."""

from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from lrg001_core import Geometry, cell_indices, load_geometry, sha256_array

ASSIGNMENTS=8192;SEED=4042026;FAMILY_COUNT=24

def fixed_labels(g:Geometry)->np.ndarray:
    y=np.zeros(len(g.row_ids),dtype=np.int8)
    for cell in sorted(set(g.cell_ids)):
        indices=np.flatnonzero(g.cell_ids==cell);y[indices[:g.labels_per_cell[cell]]]=1
    if int(y.sum())!=288:raise RuntimeError("label quota")
    return y

def folio_effects(categories:np.ndarray,y:np.ndarray,g:Geometry)->np.ndarray:
    onehot=np.eye(FAMILY_COUNT,dtype=np.float64)[categories];output=[]
    for folio in sorted(set(g.folios),key=lambda value:int(value[1:])):
        current=g.folios==folio;contrasts=[]
        for indices in cell_indices(g,current):contrasts.append(onehot[indices[y[indices]==1]].mean(0)-onehot[indices[y[indices]==0]].mean(0))
        output.append(np.mean(np.stack(contrasts),axis=0))
    return np.stack(output)

def coefficients(g:Geometry)->np.ndarray:
    result=np.zeros((ASSIGNMENTS,len(g.row_ids)),dtype=np.float32);rng=np.random.default_rng(SEED);folios=sorted(set(g.folios),key=lambda value:int(value[1:]));assignment_rows=np.arange(ASSIGNMENTS)
    for folio in folios:
        cells=cell_indices(g,g.folios==folio)
        for indices in cells:
            quota=g.labels_per_cell[str(g.cell_ids[indices[0]])];low=len(indices)-quota;base=-1.0/(len(folios)*len(cells)*low);high=1.0/(len(folios)*len(cells)*quota);result[:,indices]=base;ranks=rng.random((ASSIGNMENTS,len(indices)));chosen=indices[np.argpartition(ranks,quota-1,axis=1)[:,:quota]];result[assignment_rows[:,None],chosen]=high
    return result

def evaluate(categories:np.ndarray,y:np.ndarray,g:Geometry,coefficient:np.ndarray)->dict[str,object]:
    if categories.shape!=(len(g.row_ids),) or categories.min()<0 or categories.max()>=FAMILY_COUNT:raise RuntimeError("category array")
    folios=sorted(set(g.folios),key=lambda value:int(value[1:]));effects=folio_effects(categories,y,g);overall=effects.mean(0);onehot=np.eye(FAMILY_COUNT,dtype=np.float32)[categories];null=np.asarray(coefficient@onehot,dtype=np.float64);null_max=np.max(np.abs(null),axis=1);numbers=np.asarray([int(value[1:]) for value in folios]);sections=np.asarray([str(g.sections[np.flatnonzero(g.folios==folio)[0]]) for folio in folios]);metrics=[];registered=[]
    for index,effect in enumerate(overall):
        sign=1.0 if effect>=0 else -1.0;signed=effects[:,index]*sign;section_values={section:float(effects[sections==section,index].mean()*sign) for section in ("B","P")};parity_values={"ODD":float(effects[numbers%2==1,index].mean()*sign),"EVEN":float(effects[numbers%2==0,index].mean()*sign)};deletions=np.asarray([(effects[:,index].sum()-effects[row,index])/(len(folios)-1)*sign for row in range(len(folios))]);denominator=float(np.abs(effects[:,index]).sum());p=(1+int(np.count_nonzero(null_max>=abs(effect))))/(ASSIGNMENTS+1)
        section_max=max(section_values.values());parity_max=max(parity_values.values());section_balance=min(section_values.values())/section_max if section_max>0 else -math.inf;parity_balance=min(parity_values.values())/parity_max if parity_max>0 else -math.inf;gates={"fwer_p_at_most_001":bool(p<=.01),"absolute_effect_at_least_004":bool(abs(effect)>=.04),"directional_folio_support_at_least_10":bool(int(np.count_nonzero(signed>0))>=10),"both_sections_at_least_002":bool(all(value>=.02 for value in section_values.values())),"both_parities_at_least_002":bool(all(value>=.02 for value in parity_values.values())),"section_balance_ratio_at_least_035":bool(section_balance>=.35),"parity_balance_ratio_at_least_035":bool(parity_balance>=.35),"all_deletions_at_least_002":bool(float(deletions.min())>=.02),"concentration_at_most_025":bool(float(np.abs(effects[:,index]).max()/denominator) <=.25) if denominator else False};passed=bool(all(gates.values()));record={"index":index,"direction":"POSITIVE" if sign>0 else "NEGATIVE","effect":float(effect),"fwer_p":p,"folio_effects":{folio:float(value) for folio,value in zip(folios,effects[:,index],strict=True)},"directional_folio_support":int(np.count_nonzero(signed>0)),"section_signed_effects":section_values,"section_balance_ratio":section_balance,"parity_signed_effects":parity_values,"parity_balance_ratio":parity_balance,"minimum_deletion_signed_effect":float(deletions.min()),"maximum_absolute_folio_concentration":float(np.abs(effects[:,index]).max()/denominator) if denominator else math.inf,"gates":gates,"registers":passed};metrics.append(record)
        if passed:registered.append({"index":index,"direction":record["direction"]})
    return {"category_sha256":sha256_array(categories),"folio_effects_sha256":sha256_array(effects),"null_max_sha256":sha256_array(null_max),"metrics":metrics,"registered":registered}
