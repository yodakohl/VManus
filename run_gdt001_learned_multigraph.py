#!/usr/bin/env python3
"""Data-selected reversible multigraph libraries with matched language/null MDL."""

import csv,hashlib,json,math
from collections import Counter
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from gdt001_abbreviation_model import cpu_scores,gpu_scores,unit_sequences


def library(paths,k):
    freq=Counter()
    for p in paths:
        for w in p.words:
            for n in (2,3,4):
                for i in range(len(w)-n+1):freq[w[i:i+n]]+=1
    chosen=[x for x,_ in sorted(freq.items(),key=lambda z:(-z[1],z[0]))[:k]]
    units=tuple(sorted(set(chosen)|set(LETTERS),key=lambda x:(-len(x),-freq[x],x)))
    return chosen,units


def search(lm,seqs,counts,n,seed):
    rng=np.random.default_rng(seed);pop=rng.integers(0,26,size=(32768,n),dtype=np.int64)
    for _ in range(35):
        s=gpu_scores(lm,seqs,pop,counts);elite=pop[np.argsort(s)[:128]].copy();ch=elite[rng.integers(0,128,len(pop)-128)].copy();r=np.arange(len(ch));pos=rng.integers(0,n,len(ch));ch[r,pos]=rng.integers(0,26,len(ch));pop=np.vstack([elite,ch])
    s=gpu_scores(lm,seqs,pop,counts);i=int(np.argmin(s));exact=float(cpu_scores(lm,seqs,pop[i:i+1],counts)[0]);assert abs(exact-s[i])<2e-6
    return exact,pop[i]


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);global_null=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));rows=[];decoders=[];screen=[]
    for k in (8,16,32,64):
        chosen,units=library(paths,k);seqs,counts,_,_=unit_sequences(paths,units,frozenset());dictionary=universal_uint_bits(k)+sum(universal_uint_bits(len(x))+len(x)*math.log2(25) for x in chosen);null_payload=kt_ngram_bits(seqs,len(units)+1,2);null_key=3+universal_uint_bits(2)+dictionary;null_total=null_key+null_payload+fixed;rows.append({'model':'MATCHED_UNIT_NULL','k':k,'language':'_','seed':0,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_matched_null_bits':0.,'gap_vs_global_null_bits':null_total-global_null['total_bits'],'key_bits':null_key,'payload_bits':null_payload,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical({'chosen':chosen,'units':units})).hexdigest(),'cpu_exact':True})
        for language in PACK_NAMES:
            bits,mapping=search(train_pack(language,2),seqs,counts,len(units),14101);key=3+math.log2(6)+universal_uint_bits(2)+dictionary+len(units)*math.log2(26);total=key+bits+fixed;mapping_rows=[{'source_unit':unit,'target':chr(97+int(mapping[i])),'occurrences':int(counts[i])} for i,unit in enumerate(units)];digest=hashlib.sha256(canonical(mapping_rows)).hexdigest();item={'model':'LEARNED_MULTIGRAPH_LANGUAGE','k':k,'language':language,'seed':14101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_global_null_bits':total-global_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);decoders.append(item|{'selected_multigraphs':chosen,'unit_order':units,'mapping':mapping_rows})
    w=min(screen,key=lambda x:x['total_bits']);chosen,units=library(paths,w['k']);seqs,counts,_,_=unit_sequences(paths,units,frozenset());dictionary=universal_uint_bits(w['k'])+sum(universal_uint_bits(len(x))+len(x)*math.log2(25) for x in chosen);null_total=next(x['total_bits'] for x in rows if x['model']=='MATCHED_UNIT_NULL' and x['k']==w['k']);lm=train_pack(w['language'],2)
    for seed in (14102,14103):
        bits,mapping=search(lm,seqs,counts,len(units),seed);key=3+math.log2(6)+universal_uint_bits(2)+dictionary+len(units)*math.log2(26);total=key+bits+fixed;mapping_rows=[{'source_unit':unit,'target':chr(97+int(mapping[i])),'occurrences':int(counts[i])} for i,unit in enumerate(units)];digest=hashlib.sha256(canonical(mapping_rows)).hexdigest();item={'model':'LEARNED_MULTIGRAPH_LANGUAGE','k':w['k'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_global_null_bits':total-global_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);decoders.append(item|{'selected_multigraphs':chosen,'unit_order':units,'mapping':mapping_rows})
    best=min((x for x in rows if x['model']!='MATCHED_UNIT_NULL'),key=lambda x:x['total_bits']);same=[x for x in rows if x['model']!='MATCHED_UNIT_NULL' and x['k']==w['k'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_LEARNED_MULTIGRAPH_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_LEARNED_MULTIGRAPH_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'k':w['k'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory data-selected reversible multigraph transducer; no unit sound, language, meaning, or plaintext claim.'};(ROOT/'gdt001_learned_multigraph_results.json').write_bytes(canonical(result));(ROOT/'gdt001_learned_multigraph_decoders.json').write_bytes(canonical({'schema':'GDT001_LEARNED_MULTIGRAPH_DECODERS_V1','decoders':decoders}))
    with (ROOT/'gdt001_learned_multigraph_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_k':best['k'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'global_gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
