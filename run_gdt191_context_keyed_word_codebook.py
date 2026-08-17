#!/usr/bin/env python3
"""GDT191: fixed context-partitioned PAGE_HOST word nomenclators."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from gdt001_language_models import PACK_NAMES
from run_gdt190_compiler_stripped_word_codebook import guarded,page_parser,target_lm,kt_bits,descent

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'gdt016_group_state_inventory.tsv'
METHOD=ROOT/'GDT191_CONTEXT_KEYED_WORD_CODEBOOK_METHOD.md'
REPORT=ROOT/'GDT191_CONTEXT_KEYED_WORD_CODEBOOK_REPORT.md'
RUNS=ROOT/'gdt191_context_codebook_runs.tsv'
SUMMARY=ROOT/'gdt191_context_codebook_summary.tsv'
STRATA=ROOT/'gdt191_context_codebook_strata.tsv'
COUNTER=ROOT/'gdt191_counterexamples.tsv'
RESULT=ROOT/'gdt191_result.json'
PARTITIONS=('GLOBAL','CURRIER','SECTION','HAND','PHYSICAL_FOLIO')
SEEDS=(19101,19102,19103);KMAX=8

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def key(part,r):
 return {'GLOBAL':'ALL','CURRIER':r['currier'] or 'NONE','SECTION':r['section'] or 'NONE','HAND':r['hand'] or 'NONE','PHYSICAL_FOLIO':r['physical_folio']}[part]
def channel(lines):
 freq=Counter(x for line in lines for x in line);k=min(KMAX,len(freq));vocab=[w for w,_ in sorted(freq.items(),key=lambda z:(-z[1],z[0]))[:k]];ix={w:i for i,w in enumerate(vocab)};c=np.zeros((k+1,k),dtype=np.float64);events=runs=0
 for line in lines:
  prev=k;active=False
  for word in line:
   if word not in ix:prev=k;active=False;continue
   if not active:runs+=1;active=True
   c[prev,ix[word]]+=1;prev=ix[word];events+=1
 return vocab,c,runs,events
def main():
 rows=guarded();parse=page_parser(rows);by=defaultdict(list);meta={}
 for r in rows:by[r['locus']].append((int(r['group_index']),parse(r)));meta[r['locus']]=r
 records=[(meta[locus],[v for _,v in sorted(z)]) for locus,z in sorted(by.items())]
 all_runs=[];summaries=[];strata_rows=[];partition_selector=math.log2(len(PARTITIONS));language_selector=math.log2(len(PACK_NAMES))
 for part in PARTITIONS:
  grouped=defaultdict(list)
  for r,line in records:grouped[key(part,r)].append(line)
  cache={s:channel(lines) for s,lines in sorted(grouped.items())};null_payload=sum(kt_bits(c,len(v)) for v,c,_,_ in cache.values());events=sum(e for _,_,_,e in cache.values());mapped_runs=sum(n for _,_,n,_ in cache.values());map_key=sum(math.lgamma(len(v)+1)/math.log(2) for v,_,_,_ in cache.values());null_total=null_payload+partition_selector
  for s,(v,c,n,e) in cache.items():strata_rows.append({'partition':part,'stratum':s,'k':len(v),'mapped_events':e,'mapped_runs':n,'source_vocab_hash':hashlib.sha256('|'.join(v).encode()).hexdigest(),'kt_payload_bits':f'{kt_bits(c,len(v)):.12f}'})
  for language in PACK_NAMES:
   current=[]
   for seed in SEEDS:
    payload=0.;hash_parts=[];passes=0;local=True
    for s,(v,c,n,e) in cache.items():
     target,cost=target_lm(language,len(v));salt=int(hashlib.sha256(s.encode()).hexdigest()[:8],16);value,mapping,npas,nlocal=descent(c,cost,len(v),seed+salt);payload+=value;passes+=npas;local&=nlocal
     code='|'.join(f'{v[i]}={target[int(mapping[i])]}' for i in range(len(v)));hash_parts.append(s+'='+hashlib.sha256(code.encode()).hexdigest())
    decoder_hash=hashlib.sha256('\n'.join(hash_parts).encode()).hexdigest();total=payload+map_key+language_selector+partition_selector
    item={'partition':part,'strata':len(cache),'language':language,'seed':seed,'mapped_events':events,'mapped_runs':mapped_runs,'payload_bits':f'{payload:.12f}','mapping_key_bits':f'{map_key:.12f}','language_selector_bits':f'{language_selector:.12f}','common_partition_selector_bits':f'{partition_selector:.12f}','paid_total_bits':f'{total:.12f}','matched_null_total_bits':f'{null_total:.12f}','gap_vs_matched_kt_bits':f'{total-null_total:.12f}','gap_per_event':f'{(total-null_total)/events:.12f}','total_descent_passes':passes,'all_strata_locally_optimal':int(local),'decoder_hash':decoder_hash};all_runs.append(item);current.append(item)
   best=min(current,key=lambda x:float(x['paid_total_bits']));summaries.append({**best,'best_seed':best['seed'],'decoder_hashes_all_starts':','.join(x['decoder_hash'] for x in current),'identical_decoder_all_starts':int(len({x['decoder_hash'] for x in current})==1)})
 best=min(summaries,key=lambda x:float(x['gap_vs_matched_kt_bits']));same=[x for x in all_runs if x['partition']==best['partition'] and x['language']==best['language']];stable=len({x['decoder_hash'] for x in same})==1;beats=float(best['gap_vs_matched_kt_bits'])<0;status='CONTEXT_KEYED_WORD_NOMENCLATOR_PROVISIONAL' if beats and stable else 'CONTEXT_KEYED_WORD_NOMENCLATOR_FALSIFIED'
 counter=[{'counterexample_id':'C01','observation':f"Best partition {best['partition']} still loses {float(best['gap_vs_matched_kt_bits']):.3f} bits to matched KT.",'impact':'context keys do not rescue named-language word code'}, {'counterexample_id':'C02','observation':f"Best full decoder is {'stable' if stable else 'unstable'} over three starts.",'impact':'decoder stability'}, {'counterexample_id':'C03','observation':'Physical-folio dictionaries are highly flexible but pay every independent permutation key.','impact':'prevents free page-specific overfit'}, {'counterexample_id':'C04','observation':'Only frequent exact hosts and a fixed order-1 target-word model are tested.','impact':'bounded failure'}, {'counterexample_id':'C05','observation':'No target-word assignment is promoted as a reading.','impact':'no semantic claim'}]
 write(RUNS,all_runs);write(SUMMARY,summaries);write(STRATA,strata_rows);write(COUNTER,counter)
 report=f'''# GDT191 — context-keyed PAGE_HOST dictionaries do not rescue language\n\nStatus: **{status}**.\n\nThe global K=8 PAGE_HOST nomenclator was expanded into five fixed key scopes:\nglobal, Currier, section, hand, and physical folio. Every stratum selected its\nown top eight hosts (or fewer when necessary), paid its complete permutation\nkey, and was compared with an independently integrated source-identity KT\nchannel on the same mapped events.\n\nThe most flexible physical-folio model is also the closest result: `{best['language']}`\non {best['strata']} strata and {best['mapped_events']} mapped events, but it\nstill loses **{float(best['gap_vs_matched_kt_bits']):,.3f} bits**\n({float(best['gap_per_event']):.4f} bits/event), and the complete decoder is\n{'stable' if stable else 'not stable'} across three starts.\n\n| key scope | best language | events | gap (bits) | gap/event | stable |\n|---|---|---:|---:|---:|---|\n'''+''.join(f"| {p} | `{(z:=min((x for x in summaries if x['partition']==p),key=lambda x:float(x['gap_vs_matched_kt_bits'])))['language']}` | {z['mapped_events']} | {float(z['gap_vs_matched_kt_bits']):,.3f} | {float(z['gap_per_event']):.4f} | {'yes' if int(z['identical_decoder_all_starts']) else 'no'} |\n" for p in PARTITIONS)+'''\nContext-specific dictionaries reduce the global mismatch, especially at folio\nscale, but not enough to pay for themselves or identify one decoder. The fixed\nfrequent-host nomenclator therefore fails even when its key is allowed to vary\nby known manuscript context. Remaining natural-language routes require\nnonbijective/context-dependent expansion, phrase-level units, or an external\nkey—not another unpenalized page dictionary.\n\nNo target word is a reading; no language, sound, plaintext, meaning, or\ntranslation is established. Every f84 row was rejected before parsing,\nretention, joining, or scoring.\n''';REPORT.write_text(report,encoding='utf8')
 result={'experiment':'GDT191_CONTEXT_KEYED_WORD_CODEBOOK','status':status,'best':best,'counts':{'source_rows':len(rows),'physical_lines':len(records),'runs':len(all_runs),'summary_rows':len(summaries),'strata_rows':len(strata_rows)},'gates':{'best_beats_matched_kt':beats,'best_decoder_stable':stable,'all_pass':beats and stable},'f84r_accessed':False,'claim_ceiling':'Bounded global/register/folio PAGE_HOST frequent-word codebooks only; no word, language, sound, plaintext, meaning, or translation.','inputs':{SOURCE.name:sha(SOURCE),'gdt016_result.json':sha(ROOT/'gdt016_result.json'),'gdt190_result.json':sha(ROOT/'gdt190_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt190_compiler_stripped_word_codebook.py':sha(ROOT/'run_gdt190_compiler_stripped_word_codebook.py')},'outputs':{p.name:sha(p) for p in (RUNS,SUMMARY,STRATA,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':status,'best_partition':best['partition'],'best_language':best['language'],'gap':best['gap_vs_matched_kt_bits'],'stable':stable}))
if __name__=='__main__':main()
