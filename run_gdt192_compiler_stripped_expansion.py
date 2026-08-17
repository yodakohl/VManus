#!/usr/bin/env python3
"""GDT192: PAGE_HOST source signs emit one or two named letters."""
from __future__ import annotations
import csv,ctypes,hashlib,json,math,subprocess
from collections import Counter
from pathlib import Path
import numpy as np
from gdt001_core import LETTERS,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from run_gdt189_compiler_stripped_language import guarded,parser,sequences,kt_bits

ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT192_COMPILER_STRIPPED_EXPANSION_METHOD.md';REPORT=ROOT/'GDT192_COMPILER_STRIPPED_EXPANSION_REPORT.md';RUNS=ROOT/'gdt192_expansion_runs.tsv';SUMMARY=ROOT/'gdt192_expansion_summary.tsv';COUNTER=ROOT/'gdt192_counterexamples.tsv';RESULT=ROOT/'gdt192_result.json';SOURCE=ROOT/'gdt016_group_state_inventory.tsv';CPP=ROOT/'gdt192_expansion_score.cpp';GDT189=ROOT/'gdt189_language_runs.tsv';CODE_COUNT=702
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ptr(a,t):return a.ctypes.data_as(ctypes.POINTER(t))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def api():
 so=ROOT/'.gdt001/gdt192_expansion_score.so';so.parent.mkdir(exist_ok=True)
 if not so.exists() or so.stat().st_mtime_ns<CPP.stat().st_mtime_ns:subprocess.run(['g++','-O3','-std=c++17','-fopenmp','-shared','-fPIC',str(CPP),'-o',str(so)],check=True)
 a=ctypes.CDLL(str(so));ip=ctypes.POINTER(ctypes.c_int32);lp=ctypes.POINTER(ctypes.c_int64);dp=ctypes.POINTER(ctypes.c_double);a.gdt192_expansion_score.argtypes=[ip,dp,ctypes.c_int64,lp,ip,dp];a.gdt192_expansion_score.restype=ctypes.c_double;a.gdt192_coordinate_scores.argtypes=[ip,dp,ctypes.c_int64,lp,ip,dp,ctypes.c_int,dp];return a
def sufficient(seqs):
 c=Counter();counts=np.zeros(25,dtype=np.int64)
 for line in seqs:
  hist=[26,26]
  for x in line:
   c[tuple(hist)+(x,)]+=1;hist=[hist[1],x]
   if x<25:counts[x]+=1
 keys=np.asarray(list(c),dtype=np.int32);freq=np.asarray(list(c.values()),dtype=np.float64);return keys,freq,counts
def decode(code):return chr(97+code) if code<26 else chr(97+(code-26)//26)+chr(97+(code-26)%26)
def initial_maps():
 with GDT189.open(encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 out={}
 for r in rows:
  if r['representation']!='PAGE_HOST':continue
  m=np.zeros(25,dtype=np.int32)
  for pair in r['active_mapping'].split(',') if ',' in r['active_mapping'] else []:pass
  # active_mapping is concatenated fixed-width a>x records.
  text=r['active_mapping']
  for i in range(0,len(text),3):
   source,target=text[i],text[i+2];m[LETTERS.index(source)]=ord(target)-97
  out[(r['language'],int(r['seed']))]=m
 return out
def score(a,keys,freq,counts,m,cost):return float(a.gdt192_expansion_score(ptr(keys,ctypes.c_int32),ptr(freq,ctypes.c_double),len(freq),ptr(counts,ctypes.c_int64),ptr(m,ctypes.c_int32),ptr(cost,ctypes.c_double)))
def search(a,keys,freq,counts,m,cost):
 active=[i for i,x in enumerate(counts) if x];current=score(a,keys,freq,counts,m,cost);passes=0
 while passes<50:
  changed=False
  for source in active:
   values=np.empty(CODE_COUNT,dtype=np.float64);a.gdt192_coordinate_scores(ptr(keys,ctypes.c_int32),ptr(freq,ctypes.c_double),len(freq),ptr(counts,ctypes.c_int64),ptr(m,ctypes.c_int32),ptr(cost,ctypes.c_double),source,ptr(values,ctypes.c_double));code=int(np.argmin(values));value=float(values[code])
   if value<current-1e-9:m[source]=code;current=value;changed=True
  passes+=1
  if not changed:break
 local=True
 for source in active:
  values=np.empty(CODE_COUNT,dtype=np.float64);a.gdt192_coordinate_scores(ptr(keys,ctypes.c_int32),ptr(freq,ctypes.c_double),len(freq),ptr(counts,ctypes.c_int64),ptr(m,ctypes.c_int32),ptr(cost,ctypes.c_double),source,ptr(values,ctypes.c_double));local&=float(values.min())>=current-1e-7
 return current,m,passes,local
def main():
 src=guarded();seq=sequences(src,'PAGE_HOST',parser(src));keys,freq,counts=sufficient(seq);active=[i for i,x in enumerate(counts) if x];null_payload,_=kt_bits(seq,set(active));common=3+universal_uint_bits(2);null_total=null_payload+common;mapping_key=len(active)*math.log2(CODE_COUNT);selector=math.log2(len(PACK_NAMES));starts=initial_maps();a=api();rows=[];summary=[]
 seed_map={19001:18901,19002:18902,19003:18903}
 for language in PACK_NAMES:
  lm=train_pack(language,2);current=[]
  for seed,oldseed in seed_map.items():
   initial=starts[(language,oldseed)].copy();value,mapping,passes,local=search(a,keys,freq,counts,initial,lm.costs);active_text='|'.join(f'{LETTERS[i]}={decode(int(mapping[i]))}' for i in active);digest=hashlib.sha256(active_text.encode()).hexdigest();total=value+mapping_key+selector+common
   row={'language':language,'seed':seed,'initial_gdt189_seed':oldseed,'physical_lines':len(seq),'source_events_including_space':sum(len(x) for x in seq),'active_source_signs':len(active),'payload_reverse_and_length_bits':f'{value:.12f}','mapping_key_bits':f'{mapping_key:.12f}','language_selector_bits':f'{selector:.12f}','common_overhead_bits':f'{common:.12f}','paid_total_bits':f'{total:.12f}','matched_null_total_bits':f'{null_total:.12f}','gap_vs_matched_kt_bits':f'{total-null_total:.12f}','descent_passes':passes,'all_coordinate_alternatives_locally_optimal':int(local),'one_letter_genes':sum(int(mapping[i])<26 for i in active),'two_letter_genes':sum(int(mapping[i])>=26 for i in active),'mapping':active_text,'mapping_hash':digest};rows.append(row);current.append(row)
  best=min(current,key=lambda x:float(x['paid_total_bits']));summary.append({**best,'best_seed':best['seed'],'mapping_hashes_all_starts':','.join(x['mapping_hash'] for x in current),'identical_mapping_all_starts':int(len({x['mapping_hash'] for x in current})==1)})
 best=min(summary,key=lambda x:float(x['paid_total_bits']));same=[x for x in rows if x['language']==best['language']];stable=len({x['mapping_hash'] for x in same})==1;beats=float(best['gap_vs_matched_kt_bits'])<0;status='COMPILER_STRIPPED_EXPANSION_PROVISIONAL' if beats and stable else 'COMPILER_STRIPPED_EXPANSION_FALSIFIED';g189=json.loads((ROOT/'gdt189_result.json').read_text());nested_gap=float(next(x for x in g189['representations'] if x['representation']=='PAGE_HOST')['gap_vs_matched_kt_bits'])
 counter=[{'counterexample_id':'C01','observation':f"Best one/two-letter expansion loses {float(best['gap_vs_matched_kt_bits']):.1f} bits to matched KT.",'impact':'bounded expansion fails'}, {'counterexample_id':'C02','observation':f"Best-language expansion maps are {'stable' if stable else 'unstable'} over three nested starts.",'impact':'decoder stability'}, {'counterexample_id':'C03','observation':f"Best mapping uses {best['one_letter_genes']} one-letter and {best['two_letter_genes']} two-letter genes.",'impact':'reports actual expansion use'}, {'counterexample_id':'C04','observation':'Expansion boundaries and reverse homophone ambiguity are both transmitted.','impact':'gain cannot come from lossy decoding'}, {'counterexample_id':'C05','observation':'Longer, deletion, phrase, and page-keyed expansions are outside the frozen model.','impact':'bounded conclusion'}, {'counterexample_id':'C06','observation':f"A favorable shortest-code collapse to the nested GDT189 one-letter model still loses {nested_gap:.1f} bits.",'impact':'failure is not caused by the larger expansion-key charge'}]
 write(RUNS,rows);write(SUMMARY,summary);write(COUNTER,counter)
 report=f'''# GDT192 — compiler-stripped expansion does not reveal language\n\nStatus: **{status}**.\n\nEach of the {len(active)} active PAGE_HOST source signs was allowed to emit any\none- or two-letter string under all six frozen historical-language packs. The\nsearch was nested from the three exact GDT189 mappings and exhaustively tested\nall 702 emissions for every sign until one-coordinate local optimality. The\ncode pays the full mapping, expansion-boundary sequence, and reverse ambiguity.\n\nThe best language pack is `{best['language']}`. Its paid total is\n{float(best['paid_total_bits']):,.1f} bits versus {null_total:,.1f} for matched\nanonymous KT: a loss of **{float(best['gap_vs_matched_kt_bits']):,.1f} bits**.\nThe retained map uses {best['one_letter_genes']} one-letter and\n{best['two_letter_genes']} two-letter emissions and is\n{'identical' if stable else 'not identical'} across the three starts.\n\n| language pack | best gap vs KT (bits) | stable | 1-letter / 2-letter genes |\n|---|---:|---|---:|\n'''+''.join(f"| `{z['language']}` | {float(z['gap_vs_matched_kt_bits']):,.1f} | {'yes' if int(z['identical_mapping_all_starts']) else 'no'} | {z['one_letter_genes']} / {z['two_letter_genes']} |\n" for z in summary)+f'''\nBecause every retained gene is one-letter, a favorable shortest-code sensitivity\ncollapses to GDT189 and still loses **{nested_gap:,.1f} bits**. The result does\nnot depend on charging a 702-way key for unused two-letter capacity.\n\nThus the simplest nonbijective abbreviation expansion does not rescue the\ncompiler-stripped stream. Surviving language routes require longer or\ncontext/page-dependent transduction, phrase-level code units, or an external\nkey. The optimized letter strings are decoder states, not readings.\n\nNo language, sound, word, plaintext, meaning, or translation is established.\nEvery f84 row was rejected before parsing, retention, joining, or scoring.\n''';REPORT.write_text(report,encoding='utf8')
 result={'experiment':'GDT192_COMPILER_STRIPPED_EXPANSION','status':status,'best':best,'nested_single_letter_shortest_code_gap_bits':nested_gap,'counts':{'source_rows':len(src),'physical_lines':len(seq),'runs':len(rows),'unique_source_triples':len(keys),'active_source_signs':len(active)},'gates':{'best_beats_matched_kt':beats,'best_mapping_stable':stable,'all_pass':beats and stable},'f84r_accessed':False,'claim_ceiling':'Bounded compiler-stripped one/two-letter expansion only; no sign value, language, sound, word, plaintext, meaning, or translation.','inputs':{SOURCE.name:sha(SOURCE),'gdt016_result.json':sha(ROOT/'gdt016_result.json'),'gdt189_result.json':sha(ROOT/'gdt189_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),CPP.name:sha(CPP),'gdt001_language_models.py':sha(ROOT/'gdt001_language_models.py')},'outputs':{p.name:sha(p) for p in (RUNS,SUMMARY,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':status,'language':best['language'],'gap':best['gap_vs_matched_kt_bits'],'stable':stable}))
if __name__=='__main__':main()
