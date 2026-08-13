#!/usr/bin/env python3
"""Frequent complete source groups as homophonic plaintext-character codes."""

import csv,hashlib,json,math
from collections import Counter
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(paths,k):
    freq=Counter(w for p in paths for w in p.words);vocab=[w for w,_ in sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:k]];ix={w:i for i,w in enumerate(vocab)};seqs=[];counts=np.zeros(k);residual=[];lengths=Counter();modes=Counter()
    for p in paths:
        run=[]
        for w in p.words:
            if w in ix:x=ix[w];run.append(x);counts[x]+=1;modes['CODE']+=1
            else:
                modes['RESIDUAL']+=1;residual.append(tuple(LETTERS.index(c) for c in w));lengths[len(w)]+=1
                if run:seqs.append(run);run=[]
        if run:seqs.append(run)
    dictionary=universal_uint_bits(k)+sum(universal_uint_bits(len(w))+len(w)*math.log2(25) for w in vocab)
    maximum=max(lengths,default=0);common=dictionary+categorical_bits([modes['CODE'],modes['RESIDUAL']])+universal_uint_bits(maximum)+categorical_bits([lengths[n] for n in range(1,maximum+1)])+kt_ngram_bits(residual,25,2)
    return seqs,counts,np.zeros(k,dtype=np.int64),vocab,None,common


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);source_null=json.load(open(ROOT/'gdt001_source_selected_null_results.json'))['selected_source_null'];rows=[];maps=[];screen=[]
    for k in (16,32,64,128,256):
        seqs,counts,cats,vocab,space,common=encoded(paths,k);matched=kt_ngram_bits(seqs,k,2);null_key=3+universal_uint_bits(2)+common;null_total=null_key+matched+fixed;rows.append({'model':'MATCHED_GROUP_CODE_NULL','k':k,'language':'_','seed':0,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_matched_null_bits':0.,'gap_vs_source_winner_bits':null_total-source_null['total_bits'],'key_bits':null_key,'payload_bits':matched,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical(vocab)).hexdigest(),'cpu_exact':True})
        for lang in PACK_NAMES:
            bits,mapping,digest=search_encoded(seqs,counts,cats,vocab,space,train_pack(lang,2),19101,population=4096,generations=15);key=3+math.log2(6)+universal_uint_bits(2)+common+k*math.log2(27);total=key+bits+fixed;item={'model':'GROUP_CHARACTER_LANGUAGE','k':k,'language':lang,'seed':19101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_source_winner_bits':total-source_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    w=min(screen,key=lambda x:x['total_bits']);seqs,counts,cats,vocab,space,common=encoded(paths,w['k']);null_total=next(x['total_bits'] for x in rows if x['model']=='MATCHED_GROUP_CODE_NULL' and x['k']==w['k']);lm=train_pack(w['language'],2)
    for seed in (19102,19103):
        bits,mapping,digest=search_encoded(seqs,counts,cats,vocab,space,lm,seed,population=4096,generations=15);key=3+math.log2(6)+universal_uint_bits(2)+common+w['k']*math.log2(27);total=key+bits+fixed;item={'model':'GROUP_CHARACTER_LANGUAGE','k':w['k'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_source_winner_bits':total-source_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min((x for x in rows if x['model']=='GROUP_CHARACTER_LANGUAGE'),key=lambda x:x['total_bits']);same=[x for x in rows if x['model']=='GROUP_CHARACTER_LANGUAGE' and x['k']==w['k'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_GROUP_CHARACTER_CODE_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_GROUP_CHARACTER_CODE_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'k':w['k'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory complete-group character code; no group has an established letter, sound, word, meaning, or plaintext.'};(ROOT/'gdt001_group_character_code_results.json').write_bytes(canonical(result));(ROOT/'gdt001_group_character_code_mappings.json').write_bytes(canonical({'schema':'GDT001_GROUP_CHARACTER_CODE_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_group_character_code_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_k':best['k'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'source_winner_gap_bits':best['gap_vs_source_winner_bits']}))


if __name__=='__main__':main()
