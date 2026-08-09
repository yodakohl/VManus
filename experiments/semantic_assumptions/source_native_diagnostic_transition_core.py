#!/usr/bin/env python3
"""Target-free rotation engine for diagnostic transition transfer."""

from __future__ import annotations
import csv,hashlib,math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import numpy as np

ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={value:index for index,value in enumerate(ALPHABET)};FAVORED=frozenset(("DA","AQ","QK","KJ","LJ","PK"));DISFAVORED=frozenset(("AA","AJ","AK","AL","BB","BC","BF","BG","BJ","BU","CB","CC","CJ","CQ","DB","DJ","DK","DL","DP","DQ","JC","JF","JG","JJ","JK","JL","KC","KF","KG","KL","KP","KQ","LB","LC","LG","LL","LQ","PB","PJ","PQ","QB","QC","QF","QG","QP","QQ","QU","UB","UC","UG","UK","UQ"));FIELDS=("unit_id","locus","page","physical_folio","section","currier","kind","symbol_count")
FAV=np.zeros((24,24),dtype=np.bool_);DIS=np.zeros((24,24),dtype=np.bool_)
for pair in FAVORED:FAV[INDEX[pair[0]],INDEX[pair[1]]]=True
for pair in DISFAVORED:DIS[INDEX[pair[0]],INDEX[pair[1]]]=True
SUCCESSORS={INDEX[left]:tuple(INDEX[pair[1]] for pair in sorted(FAVORED) if pair[0]==left) for left in ALPHABET}
@dataclass
class Panel:rows:list[dict];lengths:np.ndarray;folios:tuple[str,...];folio_index:np.ndarray
def stable(text):return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'little')
def sha_array(array):return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()
def load_panel(path):
 with path.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t')
  if tuple(reader.fieldnames or ())!=FIELDS:raise ValueError('schema')
  rows=list(reader)
 if len(rows)!=1382 or len({row['unit_id'] for row in rows})!=1382:raise ValueError('identity')
 lengths=np.asarray([int(row['symbol_count']) for row in rows],dtype=np.int64);folios=tuple(sorted({row['physical_folio'] for row in rows},key=lambda value:int(value[1:])));mapping={value:index for index,value in enumerate(folios)}
 if len(folios)!=26 or int(lengths.max())!=10 or int(np.maximum(0,lengths-1).sum())!=4857:raise ValueError('capacity')
 return Panel(rows,lengths,folios,np.asarray([mapping[row['physical_folio']] for row in rows],dtype=np.int64))
def validate_sequences(panel,sequences):
 if len(panel.rows)!=1382 or len({row['unit_id'] for row in panel.rows})!=1382 or len(panel.lengths)!=1382 or len(panel.folio_index)!=1382 or len(panel.folios)!=26:raise ValueError('panel identity')
 if len(sequences)!=len(panel.rows) or any(len(sequence)!=length for sequence,length in zip(sequences,panel.lengths)):raise ValueError('geometry')
 if any(not sequence or any(symbol<0 or symbol>=24 for symbol in sequence) for sequence in sequences):raise ValueError('symbol')
def strata(panel,ensemble):
 if ensemble not in {'SECTION_KIND_LENGTH','FOLIO_KIND_LENGTH'}:raise ValueError('ensemble')
 grouped=defaultdict(list)
 for index,row in enumerate(panel.rows):
  key=(row['section'],row['kind'],row['symbol_count']) if ensemble=='SECTION_KIND_LENGTH' else (row['physical_folio'],row['kind'],row['symbol_count'])
  grouped[key].append(index)
 return [(key,np.asarray(indices,dtype=np.int64)) for key,indices in sorted(grouped.items())]
def splitmix(values):
 mask=np.uint64(0xffffffffffffffff);z=(values+np.uint64(0x9E3779B97F4A7C15))&mask;z=((z^(z>>np.uint64(30)))*np.uint64(0xBF58476D1CE4E5B9))&mask;z=((z^(z>>np.uint64(27)))*np.uint64(0x94D049BB133111EB))&mask;return z^(z>>np.uint64(31))
def shifts(ensemble,key,position,size,assignments):
 values=np.arange(assignments,dtype=np.uint64)^np.uint64(stable('SNWGDX1|'+ensemble+'|'+'|'.join(key)+'|'+str(position)));answer=(splitmix(values)%np.uint64(size)).astype(np.int64);answer[0]=0;return answer
def rotation_scores(panel,sequences,ensemble,assignments):
 validate_sequences(panel,sequences)
 if assignments<128 or assignments>8192:raise ValueError('assignments')
 favored=np.zeros(assignments,dtype=np.int32);disfavored=np.zeros(assignments,dtype=np.int32);favored_folio=np.zeros((assignments,len(panel.folios)),dtype=np.int32);disfavored_folio=np.zeros((assignments,len(panel.folios)),dtype=np.int32);digest=hashlib.sha256()
 for key,indices in strata(panel,ensemble):
  length=int(panel.lengths[indices[0]]);size=len(indices);matrix=np.asarray([sequences[index] for index in indices],dtype=np.int16);recipient=np.arange(size,dtype=np.int64);columns=[]
  for position in range(length):
   shift=shifts(ensemble,key,position,size,assignments);digest.update(np.asarray(shift,dtype='<i8').tobytes());source=(recipient[None,:]-shift[:,None])%size;columns.append(matrix[source,position])
  for position in range(1,length):
   previous,current=columns[position-1],columns[position];fav=FAV[previous,current];dis=DIS[previous,current];favored+=fav.sum(axis=1,dtype=np.int32);disfavored+=dis.sum(axis=1,dtype=np.int32)
   for folio in np.unique(panel.folio_index[indices]):
    mask=panel.folio_index[indices]==folio;favored_folio[:,folio]+=fav[:,mask].sum(axis=1,dtype=np.int32);disfavored_folio[:,folio]+=dis[:,mask].sum(axis=1,dtype=np.int32)
 return {'favored':favored,'disfavored':disfavored,'favored_folio':favored_folio,'disfavored_folio':disfavored_folio,'shift_sha256':digest.hexdigest()}
def tail_summary(panel,orbit):
 favored=orbit['favored'];disfavored=orbit['disfavored'];null_favored=favored[1:];null_disfavored=disfavored[1:];transitions=int(sum(np.maximum(0,panel.lengths-1)));fav_res=orbit['favored_folio'][0]-orbit['favored_folio'][1:].mean(axis=0);dis_res=orbit['disfavored_folio'][0]-orbit['disfavored_folio'][1:].mean(axis=0);fav_den=float(np.abs(fav_res).sum());dis_den=float(np.abs(dis_res).sum())
 return {'assignments':len(favored),'observed_favored':int(favored[0]),'observed_disfavored':int(disfavored[0]),'null_mean_favored':float(null_favored.mean()),'null_mean_disfavored':float(null_disfavored.mean()),'favored_excess_rate':float((favored[0]-null_favored.mean())/transitions),'disfavored_deficit_rate':float((null_disfavored.mean()-disfavored[0])/transitions),'favored_upper_p':float(np.mean(favored>=favored[0])),'disfavored_lower_p':float(np.mean(disfavored<=disfavored[0])),'favored_positive_folios':int((fav_res>0).sum()),'disfavored_negative_folios':int((dis_res<0).sum()),'favored_max_abs_contribution_fraction':float(np.abs(fav_res).max()/fav_den) if fav_den else 1.,'disfavored_max_abs_contribution_fraction':float(np.abs(dis_res).max()/dis_den) if dis_den else 1.,'favored_orbit_sha256':sha_array(favored.astype('<i4')),'disfavored_orbit_sha256':sha_array(disfavored.astype('<i4')),'favored_folio_orbit_sha256':sha_array(orbit['favored_folio'].astype('<i4')),'disfavored_folio_orbit_sha256':sha_array(orbit['disfavored_folio'].astype('<i4')),'shift_sha256':orbit['shift_sha256']}
def transfer_pass(summary,p_limit):return summary['favored_upper_p']<=p_limit and summary['disfavored_lower_p']<=p_limit and summary['favored_excess_rate']>=.01 and summary['disfavored_deficit_rate']>=.01 and summary['favored_positive_folios']>=18 and summary['disfavored_negative_folios']>=18 and summary['favored_max_abs_contribution_fraction']<=.25 and summary['disfavored_max_abs_contribution_fraction']<=.25
def evaluate(panel,sequences,assignments,p_limit):
 validate_sequences(panel,sequences);result={}
 for ensemble in ('SECTION_KIND_LENGTH','FOLIO_KIND_LENGTH'):
  result[ensemble]=tail_summary(panel,rotation_scores(panel,sequences,ensemble,assignments));result[ensemble]['TRANSFER_PASS']=transfer_pass(result[ensemble],p_limit)
 result['DIAGNOSTIC_TRANSFER_PASS']=all(result[ensemble]['TRANSFER_PASS'] for ensemble in ('SECTION_KIND_LENGTH','FOLIO_KIND_LENGTH'))
 return result
def synthetic_sequences(panel,world,mode,strength=.65):
 if mode not in {'POSITION_ONLY','GRAPH','ONE_SECTION','ONE_FOLIO','POSITION_CHAIN'}:raise ValueError('mode')
 active_section=('A','B','C','H','P','T','Z')[world%7];active_folio=panel.folios[world%len(panel.folios)];chain=tuple(INDEX[value] for value in 'DAQKJ');output=[]
 for row,length_value in zip(panel.rows,panel.lengths):
  length=int(length_value);sequence=[];active=mode=='GRAPH' or (mode=='ONE_SECTION' and row['section']==active_section) or (mode=='ONE_FOLIO' and row['physical_folio']==active_folio)
  for position in range(length):
   ranking=sorted(range(24),key=lambda value:stable(f"SNWGDX1|{world}|BASE|{row['section']}|{row['kind']}|{length}|{position}|{value}"));u=(stable(f"SNWGDX1|{world}|U|{row['unit_id']}|{position}")+.5)/(1<<64);symbol=ranking[0] if u<.32 else (ranking[1] if u<.53 else stable(f"SNWGDX1|{world}|R|{row['unit_id']}|{position}")%24)
   if mode=='POSITION_CHAIN':symbol=chain[position%len(chain)] if u<.72 else symbol
   if active and position>0:
    dependency=(stable(f"SNWGDX1|{world}|D|{row['unit_id']}|{position}")+.5)/(1<<64);successors=SUCCESSORS.get(sequence[-1],())
    if successors and dependency<strength:symbol=successors[stable(f"SNWGDX1|{world}|S|{row['unit_id']}|{position}")%len(successors)]
    if DIS[sequence[-1],symbol]:
     choices=[value for value in range(24) if not DIS[sequence[-1],value]];symbol=choices[stable(f"SNWGDX1|{world}|A|{row['unit_id']}|{position}")%len(choices)]
   sequence.append(int(symbol))
  output.append(tuple(sequence))
 return output
