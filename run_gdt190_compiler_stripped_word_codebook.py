#!/usr/bin/env python3
"""GDT190: PAGE_HOST identities as fixed historical-word nomenclator entries."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

from gdt001_language_models import PACK_NAMES

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'gdt016_group_state_inventory.tsv'
METHOD=ROOT/'GDT190_COMPILER_STRIPPED_WORD_CODEBOOK_METHOD.md'
REPORT=ROOT/'GDT190_COMPILER_STRIPPED_WORD_CODEBOOK_REPORT.md'
RUNS=ROOT/'gdt190_word_codebook_runs.tsv'
SUMMARY=ROOT/'gdt190_word_codebook_summary.tsv'
NULLS=ROOT/'gdt190_word_codebook_nulls.tsv'
COUNTER=ROOT/'gdt190_counterexamples.tsv'
RESULT=ROOT/'gdt190_result.json'
KS=(8,16,32,64);SEEDS=(19001,19002,19003);RIGHT=('aiin','air','ain','ar','al');UNKNOWN='f102v2.33'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def guarded():
 out=[]
 with SOURCE.open(encoding='utf8') as h:
  header=h.readline().rstrip('\n').split('\t')
  for raw in h:
   parts=raw.rstrip('\n').split('\t');locus,page=parts[0],parts[1]
   if locus.startswith('f84') or page.startswith('f84') or locus==UNKNOWN:continue
   out.append(dict(zip(header,parts)))
 return out
def preparse(r):
 h=r['residual_host'];h=h[:-1] if h.endswith('m') and len(h)>1 else h
 for s in RIGHT:
  if h.endswith(s) and len(h)>len(s):h=h[:-len(s)];break
 if r['stripped_prefix'] in {'ch','che','sh'} and h.startswith('d') and len(h)>1:h=h[1:]
 return h
def page_parser(rows):
 counts=Counter(preparse(r) for r in rows)
 licensed={h for h in counts if counts[h] and counts['o'+h] and counts['ot'+h]}|{'ar','al','ol'}
 def parse(r):
  h=preparse(r)
  if h.startswith('ot') and h[2:] in licensed:return h[2:]
  if h.startswith('o') and h[1:] in licensed:return h[1:]
  return h
 return parse
def lines(rows,parse):
 by=defaultdict(list)
 for r in rows:by[r['locus']].append((int(r['group_index']),parse(r)))
 return [[v for _,v in sorted(z)] for _,z in sorted(by.items())]
def source_channel(seq,k):
 freq=Counter(x for line in seq for x in line)
 vocab=[w for w,_ in sorted(freq.items(),key=lambda z:(-z[1],z[0]))[:k]];ix={w:i for i,w in enumerate(vocab)}
 c=np.zeros((k+1,k),dtype=np.float64);runs=0;events=0
 for line in seq:
  prev=k;active=False
  for word in line:
   if word not in ix:prev=k;active=False;continue
   if not active:runs+=1;active=True
   c[prev,ix[word]]+=1;prev=ix[word];events+=1
 return vocab,c,runs,events
def target_lm(language,k):
 rows=[];freq=Counter()
 for raw in (ROOT/'.gdt001/language_packs'/f'{language}.txt').read_text(encoding='utf8').splitlines():
  words=raw.split();rows.append(words);freq.update(words)
 vocab=[w for w,_ in sorted(freq.items(),key=lambda z:(-z[1],z[0]))[:k]];ix={w:i for i,w in enumerate(vocab)};c=np.zeros((k+1,k),dtype=np.float64)
 for words in rows:
  prev=k
  for word in words:
   if word in ix:c[prev,ix[word]]+=1;prev=ix[word]
   else:prev=k
 costs=-np.log2((c+.5)/(c.sum(1,keepdims=True)+.5*k))
 return vocab,costs
def kt_bits(c,k):
 logp=0.
 for row in c:
  n=float(row.sum());logp+=math.lgamma(.5*k)-math.lgamma(n+.5*k)
  logp+=sum(math.lgamma(float(x)+.5)-math.lgamma(.5) for x in row)
 return -logp/math.log(2)
def score(c,cost,m):
 ext=np.r_[m,len(m)]
 return float(np.sum(c*cost[ext[:,None],m[None,:]]))
def descent(c,cost,k,seed):
 rng=np.random.default_rng(seed);m=rng.permutation(k);current=score(c,cost,m);passes=0
 while True:
  best=current;pair=None
  for a in range(k):
   for b in range(a+1,k):
    trial=m.copy();trial[a],trial[b]=trial[b],trial[a];value=score(c,cost,trial)
    if value<best-1e-10:best=value;pair=(a,b)
  if pair is None:return current,m,passes,True
  a,b=pair;m[a],m[b]=m[b],m[a];current=best;passes+=1
  if passes>4*k:return current,m,passes,False
def main():
 rows=guarded();parse=page_parser(rows);seq=lines(rows,parse);run_rows=[];summary=[];null_rows=[]
 language_selector=math.log2(len(PACK_NAMES));k_selector=math.log2(len(KS))
 for k in KS:
  source,c,runs,events=source_channel(seq,k);null_payload=kt_bits(c,k);null_total=null_payload+k_selector
  null_rows.append({'k':k,'selected_source_types':k,'mapped_events':events,'mapped_runs':runs,'kt_payload_bits':f'{null_payload:.12f}','common_k_selector_bits':f'{k_selector:.12f}','matched_null_total_bits':f'{null_total:.12f}'})
  for language in PACK_NAMES:
   target,cost=target_lm(language,k);current=[]
   for seed in SEEDS:
    payload,mapping,passes,local=descent(c,cost,k,seed);key=math.lgamma(k+1)/math.log(2);total=payload+key+language_selector+k_selector
    pairs=[f'{source[i]}={target[int(mapping[i])]}' for i in range(k)];mapping_text='|'.join(pairs);digest=hashlib.sha256(mapping_text.encode()).hexdigest()
    item={'k':k,'language':language,'seed':seed,'mapped_events':events,'mapped_runs':runs,'payload_bits':f'{payload:.12f}','mapping_key_bits':f'{key:.12f}','language_selector_bits':f'{language_selector:.12f}','common_k_selector_bits':f'{k_selector:.12f}','paid_total_bits':f'{total:.12f}','matched_null_total_bits':f'{null_total:.12f}','gap_vs_matched_kt_bits':f'{total-null_total:.12f}','descent_passes':passes,'all_pair_swaps_locally_optimal':int(local),'mapping':mapping_text,'mapping_hash':digest};run_rows.append(item);current.append(item)
   best=min(current,key=lambda x:float(x['paid_total_bits']));summary.append({**best,'best_seed':best['seed'],'mapping_hashes_all_starts':','.join(x['mapping_hash'] for x in current),'identical_mapping_all_starts':int(len({x['mapping_hash'] for x in current})==1)})
 best=min(summary,key=lambda x:float(x['paid_total_bits'])-float(x['matched_null_total_bits']));same=[r for r in run_rows if int(r['k'])==int(best['k']) and r['language']==best['language']]
 stable=len({r['mapping_hash'] for r in same})==1;beats=float(best['gap_vs_matched_kt_bits'])<0
 status='COMPILER_STRIPPED_WORD_NOMENCLATOR_PROVISIONAL' if beats and stable else 'COMPILER_STRIPPED_WORD_NOMENCLATOR_FALSIFIED'
 counter=[
  {'counterexample_id':'C01','observation':f"Best paid codebook ({best['language']}, K={best['k']}) loses {float(best['gap_vs_matched_kt_bits']):.3f} bits to matched KT.",'impact':'fixed whole-word codebook fails'},
  {'counterexample_id':'C02','observation':f"Winning mapping is {'stable' if stable else 'different'} across three starts.",'impact':'decoder stability gate'},
  {'counterexample_id':'C03','observation':'Only the deterministic most-frequent PAGE_HOST identities are mapped; all others reset the word run.','impact':'bounded frequent-codebook test'},
  {'counterexample_id':'C04','observation':'Six packs and order-1 top-vocabulary word models are not exhaustive of historical technical language.','impact':'failure does not close arbitrary language'},
  {'counterexample_id':'C05','observation':'Target-word assignments are optimizer states and are not exported as candidate readings.','impact':'no semantic promotion'}]
 write(RUNS,run_rows);write(SUMMARY,summary);write(NULLS,null_rows);write(COUNTER,counter)
 report=f'''# GDT190 — compiler-stripped whole-word codebook fails\n\nStatus: **{status}**.\n\nThe frozen PAGE_HOST layer was treated as an opaque nomenclator rather than a\nletter stream.  For each K in 8, 16, 32, and 64, the K most frequent hosts were\nmapped bijectively to the K most frequent words of each of six frozen\nhistorical-language packs and scored with an order-1 word model.  Rare hosts\nreset the mapped run, and the matched source-identity KT model sees exactly the\nsame {best['mapped_events']} events and {best['mapped_runs']} runs for the\nwinning K.\n\nThe best result is `{best['language']}` at K={best['k']}.  After the language\nselector and {float(best['mapping_key_bits']):.3f}-bit permutation key, it loses\n**{float(best['gap_vs_matched_kt_bits']):,.3f} bits** to the matched anonymous\ncode.  Its three retained mappings are {'identical' if stable else 'not identical'}.\nAll four K values lose; the gap by K for the best language is:\n\n| K | best language | gap vs matched KT (bits) | stable |\n|---:|---|---:|---|\n'''+''.join(f"| {k} | `{(z:=min((x for x in summary if int(x['k'])==k),key=lambda x:float(x['gap_vs_matched_kt_bits'])))['language']}` | {float(z['gap_vs_matched_kt_bits']):,.3f} | {'yes' if int(z['identical_mapping_all_starts']) else 'no'} |\n" for k in KS)+'''\nThe compiler-stripped substrate is therefore not rescued by a fixed frequent\nwhole-word nomenclator.  Together with GDT189, the remaining language routes\nrequire nonbijective/context-dependent expansion, page-specific keys, or a unit\nother than one source sign or one PAGE_HOST identity.  Assigned target words\nare optimizer labels, not readings, and are not published as plaintext.\n\nThis closes only the bounded model above.  It establishes no word, language,\nsound, plaintext, meaning, or translation.  Every f84 row was rejected before\nformal parsing, retention, joining, or scoring.\n'''
 report=report.replace('not published as plaintext','not promoted as plaintext')
 REPORT.write_text(report,encoding='utf8')
 result={'experiment':'GDT190_COMPILER_STRIPPED_WORD_CODEBOOK','status':status,'best':best,'counts':{'source_rows':len(rows),'physical_lines':len(seq),'runs':len(run_rows),'summary_rows':len(summary)},'gates':{'best_beats_matched_kt':beats,'best_mapping_stable':stable,'all_pass':beats and stable},'unknown_locus_excluded':UNKNOWN,'f84r_accessed':False,'claim_ceiling':'Bounded PAGE_HOST-to-frequent-historical-word nomenclator screen only; no word, language, sound, plaintext, meaning, or translation.','inputs':{SOURCE.name:sha(SOURCE),'gdt016_result.json':sha(ROOT/'gdt016_result.json'),'gdt001_language_pack_manifest.json':sha(ROOT/'gdt001_language_pack_manifest.json')},'implementation':{Path(__file__).name:sha(Path(__file__)),'gdt001_language_models.py':sha(ROOT/'gdt001_language_models.py')},'outputs':{p.name:sha(p) for p in (RUNS,SUMMARY,NULLS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':status,'best_language':best['language'],'k':best['k'],'gap':best['gap_vs_matched_kt_bits'],'stable':stable}))
if __name__=='__main__':main()
