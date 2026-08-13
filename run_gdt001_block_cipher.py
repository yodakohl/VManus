#!/usr/bin/env python3
"""Fixed-size source block homophones mapped to plaintext letters."""

import csv,hashlib,json,math
from collections import Counter
import numpy as np
from gdt001_core import ROOT,canonical,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(paths,n):
    blocks=[];raw=[]
    for p in paths:
        seq=[]
        for w in p.words:
            for i in range(0,len(w),n):b=w[i:i+n];seq.append(b);raw.append(b)
        blocks.append(seq)
    vocab=sorted(set(raw));ix={x:i for i,x in enumerate(vocab)};seqs=[[ix[x] for x in s] for s in blocks];counts=np.zeros(len(vocab))
    for s in seqs:
        for x in s:counts[x]+=1
    dictionary=universal_uint_bits(len(vocab))+sum(universal_uint_bits(len(x))+len(x)*math.log2(25) for x in vocab)
    return seqs,counts,np.zeros(len(vocab),dtype=np.int64),vocab,None,dictionary


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);global_null=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));rows=[];maps=[];screen=[]
    for n in (2,3,4):
        seqs,counts,cats,vocab,space,dictionary=encoded(paths,n);matched=kt_ngram_bits(seqs,len(vocab),2);null_key=3+universal_uint_bits(2)+dictionary;null_total=null_key+matched+fixed;rows.append({'model':'MATCHED_BLOCK_NULL','block_size':n,'language':'_','seed':0,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_matched_null_bits':0.,'gap_vs_global_null_bits':null_total-global_null['total_bits'],'key_bits':null_key,'payload_bits':matched,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical(vocab)).hexdigest(),'cpu_exact':True})
        for language in PACK_NAMES:
            bits,mapping,digest=search_encoded(seqs,counts,cats,vocab,space,train_pack(language,2),16101,population=4096,generations=15);key=3+math.log2(6)+universal_uint_bits(2)+dictionary+len(vocab)*math.log2(27);total=key+bits+fixed;item={'model':'BLOCK_LANGUAGE','block_size':n,'language':language,'seed':16101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_global_null_bits':total-global_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    w=min(screen,key=lambda x:x['total_bits']);seqs,counts,cats,vocab,space,dictionary=encoded(paths,w['block_size']);null_total=next(x['total_bits'] for x in rows if x['model']=='MATCHED_BLOCK_NULL' and x['block_size']==w['block_size']);lm=train_pack(w['language'],2)
    for seed in (16102,16103):
        bits,mapping,digest=search_encoded(seqs,counts,cats,vocab,space,lm,seed,population=4096,generations=15);key=3+math.log2(6)+universal_uint_bits(2)+dictionary+len(vocab)*math.log2(27);total=key+bits+fixed;item={'model':'BLOCK_LANGUAGE','block_size':w['block_size'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_global_null_bits':total-global_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min((x for x in rows if x['model']=='BLOCK_LANGUAGE'),key=lambda x:x['total_bits']);same=[x for x in rows if x['model']=='BLOCK_LANGUAGE' and x['block_size']==w['block_size'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_BLOCK_CIPHER_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_BLOCK_CIPHER_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'block_size':w['block_size'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory fixed source-block cipher only; no language, sound, or plaintext claim.'};(ROOT/'gdt001_block_cipher_results.json').write_bytes(canonical(result));(ROOT/'gdt001_block_cipher_mappings.json').write_bytes(canonical({'schema':'GDT001_BLOCK_CIPHER_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_block_cipher_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_block_size':best['block_size'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'global_gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
