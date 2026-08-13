#!/usr/bin/env python3
"""Sparse first/last group-edge language channels with exact residual coding."""

import csv,hashlib,json,math
from collections import Counter
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(paths,scheme):
    seqs=[];counts=np.zeros(25);residual=[];lengths=Counter();line_counts=Counter()
    for p in paths:
        seq=[];line_counts[len(p.words)]+=1
        for w in p.words:
            if scheme=='INITIAL':carrier=w[:1];rest=w[1:]
            elif scheme=='FINAL':carrier=w[-1:];rest=w[:-1]
            else:carrier=w if len(w)==1 else w[:1]+w[-1:];rest=w[1:-1]
            lengths[len(rest)]+=1;residual.append(tuple(LETTERS.index(c) for c in rest))
            for c in carrier:x=LETTERS.index(c);seq.append(x);counts[x]+=1
        seqs.append(seq)
    common=universal_uint_bits(max(lengths,default=0))+categorical_bits([lengths[n] for n in range(max(lengths,default=0)+1)])+categorical_bits([line_counts[n] for n in sorted(line_counts)])+kt_ngram_bits(residual,25,2)
    return seqs,counts,np.zeros(25,dtype=np.int64),list(LETTERS),None,common


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);source=json.load(open(ROOT/'gdt001_source_selected_null_results.json'))['selected_source_null'];rows=[];maps=[];screen=[]
    for scheme in ('INITIAL','FINAL','EDGES'):
        seqs,counts,cats,labels,space,common=encoded(paths,scheme);matched=kt_ngram_bits(seqs,25,2);null_key=3+math.log2(3)+universal_uint_bits(2)+common;null_total=null_key+matched+fixed;rows.append({'model':'MATCHED_EDGE_NULL','scheme':scheme,'language':'_','seed':0,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_matched_null_bits':0.,'gap_vs_source_winner_bits':null_total-source['total_bits'],'key_bits':null_key,'payload_bits':matched,'common_residual_bits':common,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical({'scheme':scheme,'order':2})).hexdigest(),'cpu_exact':True})
        for lang in PACK_NAMES:
            bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,train_pack(lang,2),21101,population=4096,generations=15);key=3+math.log2(3)+math.log2(6)+universal_uint_bits(2)+common+25*math.log2(27);total=key+bits+fixed;item={'model':'EDGE_LANGUAGE','scheme':scheme,'language':lang,'seed':21101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_source_winner_bits':total-source['total_bits'],'key_bits':key,'payload_bits':bits,'common_residual_bits':common,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    w=min(screen,key=lambda x:x['total_bits']);seqs,counts,cats,labels,space,common=encoded(paths,w['scheme']);null_total=next(x['total_bits'] for x in rows if x['model']=='MATCHED_EDGE_NULL' and x['scheme']==w['scheme']);lm=train_pack(w['language'],2)
    for seed in (21102,21103):
        bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,lm,seed,population=4096,generations=15);key=3+math.log2(3)+math.log2(6)+universal_uint_bits(2)+common+25*math.log2(27);total=key+bits+fixed;item={'model':'EDGE_LANGUAGE','scheme':w['scheme'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_source_winner_bits':total-source['total_bits'],'key_bits':key,'payload_bits':bits,'common_residual_bits':common,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min((x for x in rows if x['model']=='EDGE_LANGUAGE'),key=lambda x:x['total_bits']);same=[x for x in rows if x['model']=='EDGE_LANGUAGE' and x['scheme']==w['scheme'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_EDGE_CARRIER_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_EDGE_CARRIER_LANGUAGE_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','theory_origin':'CODEX_SELF_ORIGINATED','decision':decision,'screen_winner':{'scheme':w['scheme'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory sparse group-edge language channel; no edge sign is an established sound, letter, meaning, or plaintext.'};(ROOT/'gdt001_edge_carrier_language_results.json').write_bytes(canonical(result));(ROOT/'gdt001_edge_carrier_language_mappings.json').write_bytes(canonical({'schema':'GDT001_EDGE_CARRIER_LANGUAGE_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_edge_carrier_language_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_scheme':best['scheme'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'source_winner_gap_bits':best['gap_vs_source_winner_bits']}))


if __name__=='__main__':main()
