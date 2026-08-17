#!/usr/bin/env python3
"""GDT189: static injective language scoring after frozen compiler stripping."""
from __future__ import annotations
import csv,ctypes,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

from gdt001_core import LETTERS, universal_uint_bits
from gdt001_language_models import PACK_NAMES, train_pack
from run_gdt001_mtf_dynamic_rank import compile_library, search_static

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'gdt016_group_state_inventory.tsv';METHOD=ROOT/'GDT189_COMPILER_STRIPPED_LANGUAGE_METHOD.md';REPORT=ROOT/'GDT189_COMPILER_STRIPPED_LANGUAGE_REPORT.md';ROWS=ROOT/'gdt189_language_runs.tsv';SUMMARY=ROOT/'gdt189_language_summary.tsv';REPS=ROOT/'gdt189_representation_summary.tsv';NULLS=ROOT/'gdt189_matched_nulls.tsv';COUNTER=ROOT/'gdt189_counterexamples.tsv';RESULT=ROOT/'gdt189_result.json'
SEEDS=(18901,18902,18903);RIGHT=('aiin','air','ain','ar','al');REPRESENTATIONS=('RAW_VISIBLE','RESIDUAL_HOST','PAGE_HOST');UNKNOWN_LOCUS='f102v2.33'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def guarded():
 out=[]
 with SOURCE.open(encoding='utf8') as h:
  header=h.readline().rstrip('\n').split('\t')
  for raw in h:
   parts=raw.rstrip('\n').split('\t');locus,page=parts[0],parts[1]
   if locus.startswith('f84') or page.startswith('f84') or locus==UNKNOWN_LOCUS:continue
   out.append(dict(zip(header,parts)))
 return out
def preparse(r):
 h=r['residual_host'];b3=int(h.endswith('m')and len(h)>1);h=h[:-1] if b3 else h;right='NONE'
 for s in RIGHT:
  if h.endswith(s)and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(r['stripped_prefix'] in {'ch','che','sh'} and h.startswith('d') and len(h)>1);h=h[1:] if inner else h
 return h
def parser(source):
 counts=Counter(preparse(r) for r in source);licensed={h for h in counts if counts[h] and counts['o'+h] and counts['ot'+h]}|{'ar','al','ol'}
 def parse(r):
  h=preparse(r)
  if h.startswith('ot')and h[2:] in licensed:h=h[2:]
  elif h.startswith('o')and h[1:] in licensed:h=h[1:]
  return h
 return parse
def sequences(source,rep,parse):
 by=defaultdict(list)
 for r in source:
  value=r['token'] if rep=='RAW_VISIBLE' else r['residual_host'] if rep=='RESIDUAL_HOST' else parse(r)
  assert value and all(ch in LETTERS for ch in value),(r['locus'],value)
  by[r['locus']].append((int(r['group_index']),value))
 seq=[]
 for locus,z in sorted(by.items()):
  line=[]
  for index,(_,value) in enumerate(sorted(z)):
   if index:line.append(25)
   line.extend(LETTERS.index(ch) for ch in value)
  seq.append(line)
 return seq
def arrays(seqs):
 tokens=[];offsets=[0]
 for seq in seqs:tokens.extend(seq);offsets.append(len(tokens))
 return np.asarray(tokens,dtype=np.int32),np.asarray(offsets,dtype=np.int64)
def kt_bits(seqs,active):
 remap={value:index for index,value in enumerate(sorted(active))};space=len(remap);k=space+1;counts=defaultdict(Counter);totals=Counter();bits=0.;bos=(-1,-1)
 for seq in seqs:
  history=list(bos)
  for old in seq:
   value=space if old==25 else remap[old];ctx=tuple(history);bits-=math.log2((counts[ctx][value]+.5)/(totals[ctx]+.5*k));counts[ctx][value]+=1;totals[ctx]+=1;history=[history[1],value]
 return bits,k
def mapping_key(k):return sum(math.log2(26-index) for index in range(k))
def main():
 source=guarded();parse=parser(source);api=compile_library();run_rows=[];sum_rows=[];rep_rows=[];null_rows=[];seq_cache={}
 common=3+universal_uint_bits(2);selector=math.log2(len(PACK_NAMES))
 for rep in REPRESENTATIONS:
  seqs=sequences(source,rep,parse);seq_cache[rep]=seqs;tokens,offsets=arrays(seqs);active={x for seq in seqs for x in seq if x!=25};null,k=kt_bits(seqs,active);key=mapping_key(len(active));null_total=null+common
  null_rows.append({'representation':rep,'physical_lines':len(seqs),'events':len(tokens),'active_source_signs':len(active),'anonymous_outcomes':k,'kt_payload_bits':f'{null:.12f}','common_overhead_bits':f'{common:.12f}','matched_null_total_bits':f'{null_total:.12f}','bits_per_event':f'{null_total/len(tokens):.12f}'})
  for language in PACK_NAMES:
   lm=train_pack(language,2);current=[]
   for seed in SEEDS:
    payload,mapping,passes,local=search_static(api,tokens,offsets,lm.costs,seed);active_map=''.join(f'{LETTERS[i]}>{chr(97+int(mapping[i]))}' for i in sorted(active));digest=hashlib.sha256(active_map.encode()).hexdigest();total=payload+common+selector+key;row={'representation':rep,'language':language,'seed':seed,'physical_lines':len(seqs),'events':len(tokens),'active_source_signs':len(active),'payload_bits':f'{payload:.12f}','key_bits':f'{key:.12f}','language_selector_bits':f'{selector:.12f}','common_overhead_bits':f'{common:.12f}','paid_total_bits':f'{total:.12f}','gap_vs_matched_kt_bits':f'{total-null_total:.12f}','bits_per_event':f'{total/len(tokens):.12f}','passes':passes,'all_pair_swaps_locally_optimal':int(local),'active_mapping':active_map,'mapping_hash':digest};run_rows.append(row);current.append(row)
   best=min(current,key=lambda x:float(x['paid_total_bits']));sum_rows.append({**best,'mapping_hashes_all_starts':','.join(x['mapping_hash'] for x in current),'identical_mapping_all_starts':int(len({x['mapping_hash'] for x in current})==1),'best_seed':best['seed']})
  best_rep=min((x for x in sum_rows if x['representation']==rep),key=lambda x:float(x['paid_total_bits']));same_language=[x for x in run_rows if x['representation']==rep and x['language']==best_rep['language']];rep_rows.append({'representation':rep,'physical_lines':len(seqs),'events':len(tokens),'active_source_signs':len(active),'best_language':best_rep['language'],'best_seed':best_rep['seed'],'best_paid_total_bits':best_rep['paid_total_bits'],'matched_null_total_bits':f'{null_total:.12f}','gap_vs_matched_kt_bits':best_rep['gap_vs_matched_kt_bits'],'gap_per_event':f'{float(best_rep["gap_vs_matched_kt_bits"])/len(tokens):.12f}','best_language_identical_mapping_all_starts':int(len({x["mapping_hash"] for x in same_language})==1),'best_language_mapping_hashes':','.join(x['mapping_hash'] for x in same_language)})
 page=next(x for x in rep_rows if x['representation']=='PAGE_HOST');raw=next(x for x in rep_rows if x['representation']=='RAW_VISIBLE');resid=next(x for x in rep_rows if x['representation']=='RESIDUAL_HOST')
 gates={'page_host_beats_matched_kt':float(page['gap_vs_matched_kt_bits'])<0,'page_host_mapping_stable':bool(int(page['best_language_identical_mapping_all_starts'])),'compiler_stripping_reduces_gap_per_event_vs_raw':float(page['gap_per_event'])<float(raw['gap_per_event']),'all_pass':False};gates['all_pass']=all(v for k,v in gates.items() if k!='all_pass')
 status='COMPILER_STRIPPED_INJECTIVE_LANGUAGE_FALSIFIED' if not gates['page_host_beats_matched_kt'] else 'COMPILER_STRIPPED_INJECTIVE_LANGUAGE_PROVISIONAL'
 counter=[{'counterexample_id':'C01','observation':f"PAGE_HOST best paid language loses {float(page['gap_vs_matched_kt_bits']):.1f} bits to matched KT.",'impact':'direct named-letter substrate fails'}, {'counterexample_id':'C02','observation':f"PAGE_HOST gap is {float(page['gap_per_event']):.4f} bits/event versus raw {float(raw['gap_per_event']):.4f}.",'impact':'stripping does not create a competitive language channel'}, {'counterexample_id':'C03','observation':f"PAGE_HOST winning-language mappings are {'stable' if int(page['best_language_identical_mapping_all_starts']) else 'unstable'} across three starts.",'impact':'mapping stability gate'}, {'counterexample_id':'C04','observation':'Six language packs are genre-imperfect and not exhaustive.','impact':'failure is bounded'}, {'counterexample_id':'C05','observation':'PAGE_HOST is a derived representation, not a reversible manuscript plaintext layer.','impact':'no decoded sample is promoted'}]
 write(ROWS,run_rows);write(SUMMARY,sum_rows);write(REPS,rep_rows);write(NULLS,null_rows);write(COUNTER,counter)
 report=f"""# GDT189 — compiler stripping does not expose an injective language

## Result

Status: **{status}**.

The experiment scores the visible groups, wrapper/DY-stripped residual hosts,
and full PAGE_HOST layer under the same six historical language packs and a
matched anonymous order-2 KT control.  PAGE_HOST contains {page['events']}
events on {page['physical_lines']} physical lines with
{page['active_source_signs']} active signs.

The best PAGE_HOST language is `{page['best_language']}` at
{float(page['best_paid_total_bits']):.1f} paid bits, but its matched anonymous
control costs only {float(page['matched_null_total_bits']):.1f}: a loss of
{float(page['gap_vs_matched_kt_bits']):,.1f} bits
({float(page['gap_per_event']):.3f} bits/event).  The corresponding gaps per
event are {float(raw['gap_per_event']):.3f} for raw visible groups and
{float(resid['gap_per_event']):.3f} for residual hosts.  Compiler stripping
therefore changes the size of the failure but does not reveal a competitive
named-letter language layer.  PAGE_HOST's winning-language mapping is
{'identical' if int(page['best_language_identical_mapping_all_starts']) else 'not identical'}
across the three deterministic starts.

## Consequence

The visible system is not rescued by the simplest “strip HPR2, then substitute
letters” theory.  If natural language remains underneath, the PAGE_HOST values
must behave as a noninjective abbreviation/codebook, a context-dependent code,
or a unit above/below letters—not as stable one-to-one plaintext characters.
The winning pack is a compression ranking only and is not a language
identification; no candidate plaintext is exported.

This closes one bounded compiler-stripped model, not every language or cipher.
No sign, sound, word, language, plaintext, or translation is established.
f84r was rejected before parsing and was not retained, joined, or scored.
""";REPORT.write_text(report,encoding='utf8')
 result={'experiment':'GDT189_COMPILER_STRIPPED_LANGUAGE','status':status,'representations':rep_rows,'gates':gates,'unknown_locus_excluded':UNKNOWN_LOCUS,'counts':{'source_rows':len(source),'physical_lines':len(seq_cache['PAGE_HOST']),'runs':len(run_rows),'summary_rows':len(sum_rows)},'f84r_accessed':False,'claim_ceiling':'Bounded compiler-stripped injective language screen only; no sign, sound, word, language, plaintext, meaning, or translation.','inputs':{SOURCE.name:sha(SOURCE),'gdt016_result.json':sha(ROOT/'gdt016_result.json'),'gdt001_language_pack_manifest.json':sha(ROOT/'gdt001_language_pack_manifest.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),'gdt001_language_models.py':sha(ROOT/'gdt001_language_models.py'),'run_gdt001_mtf_dynamic_rank.py':sha(ROOT/'run_gdt001_mtf_dynamic_rank.py'),'gdt001_mtf_score.cpp':sha(ROOT/'gdt001_mtf_score.cpp')},'outputs':{p.name:sha(p) for p in (ROWS,SUMMARY,REPS,NULLS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(status,rep_rows)
if __name__=='__main__':main()
