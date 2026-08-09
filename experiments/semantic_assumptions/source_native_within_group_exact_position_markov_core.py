#!/usr/bin/env python3
"""Exact-position-controlled local transition model."""

from __future__ import annotations
import csv,hashlib,math
from collections import Counter,defaultdict
from dataclasses import dataclass
from pathlib import Path
import numpy as np
ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");ALPHA=.5;FIELDS=("unit_id","locus","page","physical_folio","section","currier","hand","kind","symbol_count","split")
@dataclass
class Panel:rows:list[dict];lengths:np.ndarray;splits:np.ndarray;curriers:np.ndarray;folios:np.ndarray
def stable(text):return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],"little")
def load_panel(path):
 with path.open(encoding='utf-8',newline='') as h:
  reader=csv.DictReader(h,delimiter='\t')
  if tuple(reader.fieldnames or ())!=FIELDS:raise ValueError('schema')
  rows=list(reader)
 if len(rows)!=21899 or len({r['unit_id'] for r in rows})!=21899 or Counter(r['split'] for r in rows)!={'TRAIN':10753,'CAL':5516,'TEST':5630}:raise ValueError('panel')
 lengths=np.asarray([int(r['symbol_count']) for r in rows],dtype=np.int64)
 return Panel(rows,lengths,np.asarray([r['split'] for r in rows]),np.asarray([r['currier'] for r in rows]),np.asarray([r['physical_folio'] for r in rows]))
def fit(panel,sequences,markov):
 contexts=24 if markov else 1;counts={(c,l,j):np.full((contexts,24),ALPHA,dtype=np.float64) for c in 'AB' for l in range(2,12) for j in range(1,l)}
 for row,seq,length in zip(panel.rows,sequences,panel.lengths):
  if row['split']!='TRAIN' or length<2:continue
  for j in range(1,len(seq)):counts[(row['currier'],int(length),j)][seq[j-1] if markov else 0,seq[j]]+=1.
 return {k:v/v.sum(axis=1,keepdims=True) for k,v in counts.items()}
def probability(seq,length,currier,model,markov):return sum(math.log(model[(currier,length,j)][seq[j-1] if markov else 0,seq[j]]) for j in range(1,len(seq)))
def sign_p(pos,total):return sum(math.comb(total,k) for k in range(pos,total+1))/(2**total)
def summary(values):
 effects=[]
 for folio in sorted(values,key=lambda v:int(v[1:])):effects.append(sum(x for x,_ in values[folio])/sum(n for _,n in values[folio]))
 a=np.asarray(effects,dtype=np.float64);deletion=(a.sum()-a)/(len(a)-1);den=float(np.abs(a).sum())
 return {'effect_equal_folio':float(a.mean()),'positive_folios':int((a>0).sum()),'folios':len(a),'sign_p':sign_p(int((a>0).sum()),len(a)),'minimum_leave_one_folio_out':float(deletion.min()),'max_abs_contribution_fraction':float(np.abs(a).max()/den) if den else 1.}
def evaluate(panel,sequences):
 if len(panel.rows)!=21899 or len({r['unit_id'] for r in panel.rows})!=21899 or len(panel.lengths)!=21899 or len(panel.splits)!=21899 or len(panel.curriers)!=21899 or len(panel.folios)!=21899:raise ValueError('panel identity')
 if any(int(n)<1 or int(n)>11 for n in panel.lengths):raise ValueError('panel length')
 if len(sequences)!=len(panel.rows) or any(len(s)!=n for s,n in zip(sequences,panel.lengths)):raise ValueError('geometry')
 if any(not s or any(x<0 or x>=24 for x in s) for s in sequences):raise ValueError('symbol')
 base=fit(panel,sequences,False);full=fit(panel,sequences,True);cal=0.;cs=0
 for row,seq,length in zip(panel.rows,sequences,panel.lengths):
  if row['split']=='CAL' and length>=2:cal+=probability(seq,int(length),row['currier'],full,True)-probability(seq,int(length),row['currier'],base,False);cs+=len(seq)-1
 by,unseen_by=defaultdict(list),defaultdict(list);cur={'A':defaultdict(list),'B':defaultdict(list)};train={(r['currier'],int(n),s) for r,n,s in zip(panel.rows,panel.lengths,sequences) if r['split']=='TRAIN'};total=ut=0.;tg=ts=ug=us=0
 for row,seq,length in zip(panel.rows,sequences,panel.lengths):
  if row['split']!='TEST' or length<2:continue
  gain=probability(seq,int(length),row['currier'],full,True)-probability(seq,int(length),row['currier'],base,False);n=len(seq)-1;folio=row['physical_folio'];by[folio].append((gain,n));cur[row['currier']][folio].append((gain,n));total+=gain;tg+=1;ts+=n
  if (row['currier'],int(length),seq) not in train:unseen_by[folio].append((gain,n));ut+=gain;ug+=1;us+=n
 return {'cal_gain_per_symbol':cal/cs,'test_groups':tg,'test_symbols':ts,'gain_equal_symbol':total/ts,'gain':summary(by),'unseen':{'groups':ug,'symbols':us,'gain_equal_symbol':ut/us,**summary(unseen_by)},'currier':{c:{'gain':summary(cur[c])} for c in 'AB'}}
def passes(r):return r['cal_gain_per_symbol']>0 and r['test_groups']==5521 and r['test_symbols']==17435 and r['gain']['folios']==24 and r['gain']['effect_equal_folio']>=.005 and r['gain']['positive_folios']>=18 and r['gain']['sign_p']<=.01 and r['gain']['minimum_leave_one_folio_out']>0 and r['gain']['max_abs_contribution_fraction']<=.15 and r['unseen']['groups']>=500 and r['unseen']['effect_equal_folio']>=.003 and r['unseen']['minimum_leave_one_folio_out']>0 and all(r['currier'][c]['gain']['effect_equal_folio']>=.002 and r['currier'][c]['gain']['minimum_leave_one_folio_out']>0 and r['currier'][c]['gain']['positive_folios']/r['currier'][c]['gain']['folios']>=.65 for c in 'AB')
def synthetic_sequences(panel,world,mode,strength=.45):
 if mode not in {'POSITION_ONLY','MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'}:raise ValueError('mode')
 folios=sorted(set(panel.folios),key=lambda v:int(v[1:]));active_folio=folios[world%len(folios)];maps={c:tuple(sorted(range(24),key=lambda x:stable(f"SNWGM2|{world}|MAP|{c}|{x}"))) for c in 'AB'};out=[]
 for row,length_value in zip(panel.rows,panel.lengths):
  length=int(length_value);bucket=stable(f"SNWGM2|BUCKET|{row['unit_id']}")%128;position_maps={j:sorted(range(24),key=lambda x:stable(f"SNWGM2|{world}|BASE|{row['currier']}|{length}|{j}|{x}")) for j in range(length)};transition=maps[row['currier']]
  if mode=='FOLIO_RANDOM':transition=tuple(sorted(range(24),key=lambda x:stable(f"SNWGM2|{world}|FMAP|{row['physical_folio']}|{row['currier']}|{x}")))
  seq=[]
  for j in range(length):
   u=(stable(f"SNWGM2|{world}|U|{row['split']}|{row['currier']}|{length}|{bucket}|{j}")+.5)/(1<<64);base=position_maps[j];symbol=base[0] if u<.36 else (base[1] if u<.57 else stable(f"SNWGM2|{world}|R|{row['split']}|{row['currier']}|{length}|{bucket}|{j}")%24);active=mode in {'MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'} and (mode!='CURRIER_ONE' or row['currier']=='B') and (mode!='ONE_FOLIO' or row['physical_folio']==active_folio)
   if active and j>0 and u<strength:symbol=transition[seq[-1]]
   seq.append(int(symbol))
  out.append(tuple(seq))
 return out
