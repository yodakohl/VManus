#!/usr/bin/env python3
"""Compact reading-order screen across every frozen historical language pack."""

import csv, hashlib, json, math
import numpy as np
from gdt001_core import ROOT, LETTERS, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES, train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(lines,paths,scheme):
    seqs=[];counts=np.zeros(25);space=25;page=None;page_line=0
    for line,p in zip(lines,paths):
        if line.page != page: page=line.page;page_line=0
        words=list(p.words)
        if scheme=='GROUP_REVERSE':words.reverse()
        elif scheme=='LINE_REVERSE':words=[w[::-1] for w in words[::-1]]
        elif scheme=='BOUSTROPHEDON' and page_line%2:words=[w[::-1] for w in words[::-1]]
        seq=[]
        for wi,w in enumerate(words):
            if wi:seq.append(space)
            for c in w:x=LETTERS.index(c);seq.append(x);counts[x]+=1
        seqs.append(seq)
        page_line+=1
    return seqs,counts,np.zeros(25,dtype=np.int64),list(LETTERS),space


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);null=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];maps=[];screen=[];key=3+math.log2(6)+math.log2(3)+universal_uint_bits(2)+25*math.log2(27)
    for scheme in ('GROUP_REVERSE','LINE_REVERSE','BOUSTROPHEDON'):
        args=encoded(lines,paths,scheme)
        for language in PACK_NAMES:
            bits,mapping,digest=search_encoded(*args,train_pack(language,2),8101);total=key+bits+fixed;item={'scheme':scheme,'language':language,'seed':8101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    winner=min(screen,key=lambda x:x['total_bits']);args=encoded(lines,paths,winner['scheme']);lm=train_pack(winner['language'],2)
    for seed in (8102,8103):
        bits,mapping,digest=search_encoded(*args,lm,seed);total=key+bits+fixed;item={'scheme':winner['scheme'],'language':winner['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);same=[x for x in rows if x['scheme']==winner['scheme'] and x['language']==winner['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_null_bits']<0 else 'STOP')+'_READING_ORDER_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_READING_ORDER_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'scheme':winner['scheme'],'language':winner['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory reading-order screen only; no historical direction, language, or plaintext claim.'};(ROOT/'gdt001_reading_order_results.json').write_bytes(canonical(result));(ROOT/'gdt001_reading_order_mappings.json').write_bytes(canonical({'schema':'GDT001_READING_ORDER_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_reading_order_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_scheme':best['scheme'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'null_bps':null['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
