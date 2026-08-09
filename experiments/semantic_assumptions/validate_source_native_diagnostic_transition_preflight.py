#!/usr/bin/env python3
"""Clean-room reconstruction of diagnostic transition calibration."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,math,multiprocessing as mp
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_diagnostic_transition_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_diagnostic_transition_capacity_validation.json";FAMILY_ATLAS=RESULTS/"source_native_transition_atlas.tsv";FAMILY_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";CORE=BASE/"source_native_diagnostic_transition_core.py";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_PREFLIGHT_SPEC.md";RUNNER=BASE/"run_source_native_diagnostic_transition_preflight.py";PRODUCTION=RESULTS/"source_native_diagnostic_transition_preflight.json";PRODUCTION_REPORT=RESULTS/"source_native_diagnostic_transition_preflight_report.md";TARGET_OUT=RESULTS/"source_native_diagnostic_transition_target.json";TARGET_REPORT=RESULTS/"source_native_diagnostic_transition_target_report.md";OUT=RESULTS/"source_native_diagnostic_transition_preflight_validation.json";REPORT=RESULTS/"source_native_diagnostic_transition_preflight_validation_report.md"
FROZEN={PANEL_PATH:"7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",CAPACITY_VALIDATION:"0a1257ffd8e1b88a3f94fade1381516c95f2cbdf9eeba3d0dc41a64ca5b23033",FAMILY_ATLAS:"f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",FAMILY_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",CORE:"4494da0ec8969b44c5636c419fb55b3485d4ddad98c3406c6f0cf09a3595a211",SPEC:"1af65aeb3c2c0bccc5c9f3157e2a4587f6cd0deb3948bc3bf24d3fd15955cd25",RUNNER:"48da7981a585161d6e83f574dcf1c70bf9d707cd41ac84dc7115ddf1ad2392a0",PRODUCTION:"5cc253813a24f3f87eca44d4c71a8f5b0d09bfc4690876b7fda6717cf28add97",PRODUCTION_REPORT:"c595a21b20d1c21a66a5e89f7ff57dc99d2210aa025f7e2ff8d097a86a5920f1"};ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={value:index for index,value in enumerate(ALPHABET)};FAVORED=frozenset(("DA","AQ","QK","KJ","LJ","PK"));DISFAVORED=frozenset(("AA","AJ","AK","AL","BB","BC","BF","BG","BJ","BU","CB","CC","CJ","CQ","DB","DJ","DK","DL","DP","DQ","JC","JF","JG","JJ","JK","JL","KC","KF","KG","KL","KP","KQ","LB","LC","LG","LL","LQ","PB","PJ","PQ","QB","QC","QF","QG","QP","QQ","QU","UB","UC","UG","UK","UQ"));FAV=np.zeros((24,24),dtype=np.bool_);DIS=np.zeros((24,24),dtype=np.bool_)
for pair in FAVORED:FAV[INDEX[pair[0]],INDEX[pair[1]]]=True
for pair in DISFAVORED:DIS[INDEX[pair[0]],INDEX[pair[1]]]=True
SUCCESSORS={INDEX[left]:tuple(INDEX[pair[1]] for pair in sorted(FAVORED) if pair[0]==left) for left in ALPHABET};TASKS=([('POSITION_ONLY',world) for world in range(64)]+[('GRAPH',100+world) for world in range(8)]+[('ONE_SECTION',200+world) for world in range(8)]+[('ONE_FOLIO',300+world) for world in range(8)]+[('POSITION_CHAIN',400+world) for world in range(8)]);PANEL=None
@dataclass
class Panel:rows:list[dict];lengths:np.ndarray;folios:tuple[str,...];folio_index:np.ndarray
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(text):return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'little')
def load_panel():
 with PANEL_PATH.open(encoding='utf-8',newline='') as handle:rows=list(csv.DictReader(handle,delimiter='\t'))
 if len(rows)!=1382 or len({row['unit_id'] for row in rows})!=1382:raise ValueError('identity')
 lengths=np.asarray([int(row['symbol_count']) for row in rows],dtype=np.int64);folios=tuple(sorted({row['physical_folio'] for row in rows},key=lambda value:int(value[1:])));mapping={value:index for index,value in enumerate(folios)}
 return Panel(rows,lengths,folios,np.asarray([mapping[row['physical_folio']] for row in rows],dtype=np.int64))
def validate(panel,sequences):
 if len(panel.rows)!=1382 or len({row['unit_id'] for row in panel.rows})!=1382 or len(panel.lengths)!=1382 or len(panel.folio_index)!=1382 or len(panel.folios)!=26:raise ValueError('panel')
 if len(sequences)!=1382 or any(len(sequence)!=length for sequence,length in zip(sequences,panel.lengths)):raise ValueError('geometry')
 if any(not sequence or any(symbol<0 or symbol>=24 for symbol in sequence) for sequence in sequences):raise ValueError('symbol')
def splitmix(values):
 mask=np.uint64(0xffffffffffffffff);result=(values+np.uint64(0x9E3779B97F4A7C15))&mask;result=((result^(result>>np.uint64(30)))*np.uint64(0xBF58476D1CE4E5B9))&mask;result=((result^(result>>np.uint64(27)))*np.uint64(0x94D049BB133111EB))&mask;return result^(result>>np.uint64(31))
def grouped(panel,ensemble):
 result=defaultdict(list)
 for index,row in enumerate(panel.rows):result[(row['section'],row['kind'],row['symbol_count']) if ensemble=='SECTION_KIND_LENGTH' else (row['physical_folio'],row['kind'],row['symbol_count'])].append(index)
 return [(key,np.asarray(value,dtype=np.int64)) for key,value in sorted(result.items())]
def compute(panel,sequences,ensemble,assignments):
 validate(panel,sequences);fav=np.zeros(assignments,dtype=np.int32);dis=np.zeros(assignments,dtype=np.int32);ff=np.zeros((assignments,26),dtype=np.int32);df=np.zeros((assignments,26),dtype=np.int32);digest=hashlib.sha256()
 for key,indices in grouped(panel,ensemble):
  length=int(panel.lengths[indices[0]]);size=len(indices);matrix=np.asarray([sequences[index] for index in indices],dtype=np.int16);recipient=np.arange(size,dtype=np.int64);columns=[]
  for position in range(length):
   values=np.arange(assignments,dtype=np.uint64)^np.uint64(stable('SNWGDX1|'+ensemble+'|'+'|'.join(key)+'|'+str(position)));shift=(splitmix(values)%np.uint64(size)).astype(np.int64);shift[0]=0;digest.update(np.asarray(shift,dtype='<i8').tobytes());columns.append(matrix[(recipient[None,:]-shift[:,None])%size,position])
  for position in range(1,length):
   favored=FAV[columns[position-1],columns[position]];avoided=DIS[columns[position-1],columns[position]];fav+=favored.sum(axis=1,dtype=np.int32);dis+=avoided.sum(axis=1,dtype=np.int32)
   for folio in np.unique(panel.folio_index[indices]):
    mask=panel.folio_index[indices]==folio;ff[:,folio]+=favored[:,mask].sum(axis=1,dtype=np.int32);df[:,folio]+=avoided[:,mask].sum(axis=1,dtype=np.int32)
 return fav,dis,ff,df,digest.hexdigest()
def summarize(panel,data):
 fav,dis,ff,df,shift=data;nf=fav[1:];nd=dis[1:];transitions=int(np.maximum(0,panel.lengths-1).sum());fr=ff[0]-ff[1:].mean(axis=0);dr=df[0]-df[1:].mean(axis=0);fden=float(np.abs(fr).sum());dden=float(np.abs(dr).sum())
 return {'assignments':len(fav),'observed_favored':int(fav[0]),'observed_disfavored':int(dis[0]),'null_mean_favored':float(nf.mean()),'null_mean_disfavored':float(nd.mean()),'favored_excess_rate':float((fav[0]-nf.mean())/transitions),'disfavored_deficit_rate':float((nd.mean()-dis[0])/transitions),'favored_upper_p':float(np.mean(fav>=fav[0])),'disfavored_lower_p':float(np.mean(dis<=dis[0])),'favored_positive_folios':int((fr>0).sum()),'disfavored_negative_folios':int((dr<0).sum()),'favored_max_abs_contribution_fraction':float(np.abs(fr).max()/fden) if fden else 1.,'disfavored_max_abs_contribution_fraction':float(np.abs(dr).max()/dden) if dden else 1.,'favored_orbit_sha256':hashlib.sha256(fav.astype('<i4').tobytes()).hexdigest(),'disfavored_orbit_sha256':hashlib.sha256(dis.astype('<i4').tobytes()).hexdigest(),'favored_folio_orbit_sha256':hashlib.sha256(ff.astype('<i4').tobytes()).hexdigest(),'disfavored_folio_orbit_sha256':hashlib.sha256(df.astype('<i4').tobytes()).hexdigest(),'shift_sha256':shift}
def passes(summary,limit):return summary['favored_upper_p']<=limit and summary['disfavored_lower_p']<=limit and summary['favored_excess_rate']>=.01 and summary['disfavored_deficit_rate']>=.01 and summary['favored_positive_folios']>=18 and summary['disfavored_negative_folios']>=18 and summary['favored_max_abs_contribution_fraction']<=.25 and summary['disfavored_max_abs_contribution_fraction']<=.25
def evaluate(panel,sequences,assignments,limit):
 result={}
 for ensemble in ('SECTION_KIND_LENGTH','FOLIO_KIND_LENGTH'):
  result[ensemble]=summarize(panel,compute(panel,sequences,ensemble,assignments));result[ensemble]['TRANSFER_PASS']=passes(result[ensemble],limit)
 result['DIAGNOSTIC_TRANSFER_PASS']=all(result[ensemble]['TRANSFER_PASS'] for ensemble in ('SECTION_KIND_LENGTH','FOLIO_KIND_LENGTH'));return result
def synthetic(panel,world,mode,strength=.65):
 active_section=('A','B','C','H','P','T','Z')[world%7];active_folio=panel.folios[world%26];chain=tuple(INDEX[value] for value in 'DAQKJ');output=[]
 for row,length_value in zip(panel.rows,panel.lengths):
  length=int(length_value);sequence=[];active=mode=='GRAPH' or (mode=='ONE_SECTION' and row['section']==active_section) or (mode=='ONE_FOLIO' and row['physical_folio']==active_folio)
  for position in range(length):
   ranking=sorted(range(24),key=lambda value:stable(f"SNWGDX1|{world}|BASE|{row['section']}|{row['kind']}|{length}|{position}|{value}"));u=(stable(f"SNWGDX1|{world}|U|{row['unit_id']}|{position}")+.5)/(1<<64);symbol=ranking[0] if u<.32 else (ranking[1] if u<.53 else stable(f"SNWGDX1|{world}|R|{row['unit_id']}|{position}")%24)
   if mode=='POSITION_CHAIN':symbol=chain[position%5] if u<.72 else symbol
   if active and position>0:
    dependency=(stable(f"SNWGDX1|{world}|D|{row['unit_id']}|{position}")+.5)/(1<<64);successors=SUCCESSORS.get(sequence[-1],())
    if successors and dependency<strength:symbol=successors[stable(f"SNWGDX1|{world}|S|{row['unit_id']}|{position}")%len(successors)]
    if DIS[sequence[-1],symbol]:
     choices=[value for value in range(24) if not DIS[sequence[-1],value]];symbol=choices[stable(f"SNWGDX1|{world}|A|{row['unit_id']}|{position}")%len(choices)]
   sequence.append(int(symbol))
  output.append(tuple(sequence))
 return output
def worker(payload):
 mode,world=payload;return {'mode':mode,'world':world,**evaluate(PANEL,synthetic(PANEL,world,mode),2048,.02)}
def numeric_max(left,right):
 if isinstance(left,dict):return math.inf if set(left)!=set(right) else max((numeric_max(left[key],right[key]) for key in left),default=0.)
 if isinstance(left,list):return math.inf if len(left)!=len(right) else max((numeric_max(a,b) for a,b in zip(left,right)),default=0.)
 if isinstance(left,(int,float)) and not isinstance(left,bool):return abs(float(left)-float(right))
 return 0. if left==right else math.inf
def main():
 global PANEL
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(condition,name):
  nonlocal checks;checks+=1
  if not condition:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 PANEL=load_panel()
 with mp.get_context('fork').Pool(32) as pool:rebuilt=pool.map(worker,TASKS)
 rebuilt.sort(key=lambda row:TASKS.index((row['mode'],row['world'])));production=json.loads(PRODUCTION.read_text());stored={(row['mode'],row['world']):row for row in production['records']};maximum=0.
 for row in rebuilt:
  key=(row['mode'],row['world']);delta=numeric_max(row,stored[key]);maximum=max(maximum,delta);check(delta==0,f'record:{key}')
 counts={mode:{'worlds':sum(candidate==mode for candidate,_ in TASKS),'passes':sum(row['DIAGNOSTIC_TRANSFER_PASS'] for row in rebuilt if row['mode']==mode)} for mode in ('POSITION_ONLY','GRAPH','ONE_SECTION','ONE_FOLIO','POSITION_CHAIN')};check(production['counts']==counts,'counts');large={mode:{'mode':mode,'world':world,**evaluate(PANEL,synthetic(PANEL,world,mode),8192,.01)} for mode,world in (('POSITION_ONLY',0),('GRAPH',100))};check(numeric_max(production['target_size_checks'],large)==0,'large')
 reference=synthetic(PANEL,100,'GRAPH');mutations={}
 for name,altered in (('missing_sequence',reference[:-1]),('length_mismatch',[tuple()]+reference[1:]),('invalid_symbol',[(-1,)+reference[0][1:]]+reference[1:])):
  try:evaluate(PANEL,altered,128,.02)
  except ValueError:mutations[name]=True
  else:mutations[name]=False
 bad_rows=[dict(row) for row in PANEL.rows];bad_rows[0]['unit_id']=bad_rows[1]['unit_id'];bad=type(PANEL)(bad_rows,PANEL.lengths,PANEL.folios,PANEL.folio_index)
 try:evaluate(bad,reference,128,.02)
 except ValueError:mutations['duplicate_unit_id']=True
 else:mutations['duplicate_unit_id']=False
 check(production['mutations']==mutations,'mutations');pattern=counts['POSITION_ONLY']['passes']<=1 and counts['GRAPH']['passes']>=7 and all(counts[mode]['passes']==0 for mode in ('ONE_SECTION','ONE_FOLIO','POSITION_CHAIN'));gates={'expected_synthetic_pattern':pattern,'target_size_null_rejects':not large['POSITION_ONLY']['DIAGNOSTIC_TRANSFER_PASS'],'target_size_graph_passes':large['GRAPH']['DIAGNOSTIC_TRANSFER_PASS'],'target_size_decisions_match_calibration':large['POSITION_ONLY']['DIAGNOSTIC_TRANSFER_PASS']==rebuilt[0]['DIAGNOSTIC_TRANSFER_PASS'] and large['GRAPH']['DIAGNOSTIC_TRANSFER_PASS']==next(row['DIAGNOSTIC_TRANSFER_PASS'] for row in rebuilt if row['mode']=='GRAPH' and row['world']==100),'finite_summaries':True,'mutation_guards':all(mutations.values()),'exact_capacity':len(PANEL.rows)==1382 and len(PANEL.folios)==26 and int(np.maximum(0,PANEL.lengths-1).sum())==4857,'target_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists()};check(production['gates']==gates and all(gates.values()),'gates');check(production['status']=='PASS_TARGET_FREE_DIAGNOSTIC_TRANSITION_PREFLIGHT' and production['decision']=='GO_INDEPENDENTLY_VALIDATE_DIAGNOSTIC_TRANSITION_PREFLIGHT','decision');check(production['target_source_opened'] is False and production['target_family_sequences_accessed']==0 and production['target_scores_computed']==0 and production['target_outputs_absent'] is True,'isolation')
 expected_report=f"""# Diagnostic transition-transfer preflight

Status: **{production['status']}**

The 2,048-assignment grid yields **{counts['POSITION_ONLY']['passes']}/64**
position-only false passes, **{counts['GRAPH']['passes']}/8** global graph
passes, and **{counts['ONE_SECTION']['passes']}/8** one-section,
**{counts['ONE_FOLIO']['passes']}/8** one-folio, and
**{counts['POSITION_CHAIN']['passes']}/8** position-chain passes. The null and
graph decisions remain unchanged at the target-size 8,192 assignments. All
remaining gates are **passing**.

Zero diagnostic family sequences or target scores were opened. Decision:
**{production['decision']}**. No wordhood, ownership, label meaning, picture identity, sound,
language, cipher, plaintext, or translation follows.
""";check(PRODUCTION_REPORT.read_text()==expected_report,'report')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_PREFLIGHT_VALIDATION','status':'PASS_INDEPENDENT_96_WORLD_DUAL_ENSEMBLE_RECONSTRUCTION','checks':checks,'failures':[],'maximum_numeric_delta':maximum,'reconstructed_worlds':96,'counts':counts,'target_size_checks':2,'mutations':4,'target_source_opened':False,'target_family_sequences_accessed':0,'target_scores_computed':0,'target_outputs_absent':True,'english_glosses':0,'inputs':{path.name:sha(path) for path in FROZEN},'claim_ceiling':'Independent target-free calibration reconstruction only; no wordhood, ownership, label meaning, sound, language, cipher, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Diagnostic transition preflight validation

Status: **{result['status']}**

A production-free implementation reconstructs all **96** calibration worlds,
both target-size checks, rotation and score digests, mutations, gates, decision,
and report in **{checks}** checks with zero numeric discrepancy. The target
remains absent.

This validates calibration only and supplies no wordhood, ownership, label
meaning, sound, language, cipher, plaintext, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks,'max_delta':maximum},sort_keys=True))
if __name__=='__main__':main()
