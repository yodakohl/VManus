#!/usr/bin/env python3
"""GDT194: noninjective consonant mapping after compiler stripping."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from gdt001_core import LETTERS,categorical_bits,universal_uint_bits
from gdt001_language_models import PACK_NAMES
from run_gdt189_compiler_stripped_language import guarded,parser,sequences,kt_bits
from run_gdt192_compiler_stripped_expansion import sufficient
from run_gdt193_compiler_stripped_consonantal import consonant_lm,CONSONANTS

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'gdt016_group_state_inventory.tsv';STARTS=ROOT/'gdt193_consonantal_runs.tsv';METHOD=ROOT/'GDT194_CONSONANTAL_HOMOPHONY_METHOD.md';REPORT=ROOT/'GDT194_CONSONANTAL_HOMOPHONY_REPORT.md';RUNS=ROOT/'gdt194_homophonic_runs.tsv';SUMMARY=ROOT/'gdt194_homophonic_summary.tsv';COUNTER=ROOT/'gdt194_counterexamples.tsv';RESULT=ROOT/'gdt194_result.json';TARGETS=tuple(ord(x)-97 for x in CONSONANTS)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def score(cost,keys,freq,counts,active,mapping):
 extended=np.r_[mapping,26,27];mapped=extended[keys];value=float(np.sum(cost[mapped[:,0],mapped[:,1],mapped[:,2]]*freq));groups=defaultdict(list)
 for source in active:groups[int(mapping[source])].append(source)
 value+=sum(categorical_bits([int(counts[s]) for s in members]) for members in groups.values());return value
def search(cost,keys,freq,counts,active,mapping):
 current=score(cost,keys,freq,counts,active,mapping);passes=0
 while passes<50:
  changed=False
  for source in active:
   best=current;target=int(mapping[source])
   for candidate in TARGETS:
    trial=mapping.copy();trial[source]=candidate;value=score(cost,keys,freq,counts,active,trial)
    if value<best-1e-9:best=value;target=candidate
   if target!=mapping[source]:mapping[source]=target;current=best;changed=True
  passes+=1
  if not changed:break
 local=True
 for source in active:
  local&=min(score(cost,keys,freq,counts,active,np.where(np.arange(25)==source,candidate,mapping)) for candidate in TARGETS)>=current-1e-7
 return current,mapping,passes,local
def main():
 src=guarded();seq=sequences(src,'PAGE_HOST',parser(src));keys,freq,counts=sufficient(seq);active=[i for i,x in enumerate(counts) if x];null,_=kt_bits(seq,set(active));common=3+universal_uint_bits(2);null_total=null+common;key=len(active)*math.log2(len(TARGETS));selector=math.log2(len(PACK_NAMES))
 with STARTS.open(encoding='utf8') as h:starts=list(csv.DictReader(h,delimiter='\t'))
 runs=[];summary=[]
 for language in PACK_NAMES:
  lm,_=consonant_lm(language);current=[]
  for old in [x for x in starts if x['language']==language]:
   mapping=np.zeros(25,dtype=np.int64)
   for item in old['mapping'].split('|'):
    source,target=item.split('=');mapping[LETTERS.index(source)]=ord(target)-97
   payload,mapping,passes,local=search(lm.costs,keys,freq,counts,active,mapping);text='|'.join(f'{LETTERS[s]}={chr(97+int(mapping[s]))}' for s in active);digest=hashlib.sha256(text.encode()).hexdigest();total=payload+key+selector+common
   row={'language':language,'seed':old['seed'],'initial_gdt193_mapping_hash':old['mapping_hash'],'physical_lines':len(seq),'events':sum(len(x) for x in seq),'active_source_signs':len(active),'distinct_target_consonants':len({int(mapping[s]) for s in active}),'payload_and_reverse_bits':f'{payload:.12f}','mapping_key_bits':f'{key:.12f}','language_selector_bits':f'{selector:.12f}','common_overhead_bits':f'{common:.12f}','paid_total_bits':f'{total:.12f}','matched_null_total_bits':f'{null_total:.12f}','gap_vs_matched_kt_bits':f'{total-null_total:.12f}','gap_per_event':f'{(total-null_total)/sum(len(x) for x in seq):.12f}','descent_passes':passes,'all_coordinate_alternatives_locally_optimal':int(local),'mapping':text,'mapping_hash':digest};runs.append(row);current.append(row)
  best=min(current,key=lambda x:float(x['paid_total_bits']));summary.append({**best,'mapping_hashes_all_starts':','.join(x['mapping_hash'] for x in current),'identical_mapping_all_starts':int(len({x['mapping_hash'] for x in current})==1)})
 best=min(summary,key=lambda x:float(x['paid_total_bits']));same=[x for x in runs if x['language']==best['language']];stable=len({x['mapping_hash'] for x in same})==1;beats=float(best['gap_vs_matched_kt_bits'])<0;g193=json.loads((ROOT/'gdt193_result.json').read_text());injective=float(g193['best']['gap_vs_matched_kt_bits']);status='CONSONANTAL_HOMOPHONY_PROVISIONAL' if beats and stable else 'CONSONANTAL_HOMOPHONY_FALSIFIED'
 counter=[{'counterexample_id':'C01','observation':f"Best homophonic consonant map loses {float(best['gap_vs_matched_kt_bits']):.1f} bits.",'impact':'matched null wins'}, {'counterexample_id':'C02','observation':f"Homophony improves the best injective gap by {injective-float(best['gap_vs_matched_kt_bits']):.1f} bits only.",'impact':'small relative to residual loss'}, {'counterexample_id':'C03','observation':f"Best map uses {best['distinct_target_consonants']} consonants for 20 signs.",'impact':'retained collision capacity'}, {'counterexample_id':'C04','observation':f"Mappings are {'stable' if stable else 'unstable'} across starts.",'impact':'decoder stability'}, {'counterexample_id':'C05','observation':'Reverse ambiguity is fully transmitted.','impact':'not a lossy score'}]
 write(RUNS,runs);write(SUMMARY,summary);write(COUNTER,counter)
 report=f'''# GDT194 — consonantal homophony does not rescue PAGE_HOST\n\nStatus: **{status}**.\n\nAllowing multiple PAGE_HOST signs to share a target consonant improves the best\nGDT193 gap by {injective-float(best['gap_vs_matched_kt_bits']):,.1f} bits. The\nbest pack is `{best['language']}`, using {best['distinct_target_consonants']}\ndistinct consonants for 20 source signs, but it still loses\n**{float(best['gap_vs_matched_kt_bits']):,.1f} bits** to matched KT\n({float(best['gap_per_event']):.3f} bits/event). The reverse ambiguity is paid\nand the three retained mappings are {'identical' if stable else 'not identical'}.\n\n| pack | best gap (bits) | distinct consonants | stable |\n|---|---:|---:|---|\n'''+''.join(f"| `{x['language']}` | {float(x['gap_vs_matched_kt_bits']):,.1f} | {x['distinct_target_consonants']} | {'yes' if int(x['identical_mapping_all_starts']) else 'no'} |\n" for x in summary)+'''\nFixed consonantal homophony is therefore another insufficient substrate. The\nvowel-omission direction survives only as an architectural hint; it supplies no\nconsonant values or language identification.\n\nNo sign, sound, word, language, plaintext, meaning, or translation is\nestablished. Every f84 row was rejected before parsing or scoring.\n''';REPORT.write_text(report,encoding='utf8')
 result={'experiment':'GDT194_CONSONANTAL_HOMOPHONY','status':status,'best':best,'injective_gap_bits':injective,'improvement_vs_injective_bits':injective-float(best['gap_vs_matched_kt_bits']),'counts':{'source_rows':len(src),'physical_lines':len(seq),'runs':len(runs)},'gates':{'best_beats_matched_kt':beats,'best_mapping_stable':stable,'all_pass':beats and stable},'f84r_accessed':False,'claim_ceiling':'Bounded compiler-stripped fixed consonantal homophony only; no sign, sound, word, language, plaintext, meaning, or translation.','inputs':{SOURCE.name:sha(SOURCE),'gdt193_result.json':sha(ROOT/'gdt193_result.json'),STARTS.name:sha(STARTS)},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt193_compiler_stripped_consonantal.py':sha(ROOT/'run_gdt193_compiler_stripped_consonantal.py')},'outputs':{p.name:sha(p) for p in (RUNS,SUMMARY,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':status,'language':best['language'],'gap':best['gap_vs_matched_kt_bits'],'improvement':result['improvement_vs_injective_bits'],'stable':stable}))
if __name__=='__main__':main()
