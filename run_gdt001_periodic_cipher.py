#!/usr/bin/env python3
"""Periodic polyalphabetic homophonic screens with explicit phase resets."""

import csv,hashlib,json,math
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,fixed_costs,load_lattice,universal_uint_bits
from gdt001_language_models import train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(paths,period,reset):
    labels=[f'P{p}:{c}' for p in range(period) for c in LETTERS];counts=np.zeros(period*25);seqs=[];space=period*25
    for path in paths:
        seq=[];phase=0
        for wi,w in enumerate(path.words):
            if wi:seq.append(space)
            if reset=='GROUP':phase=0
            for c in w:
                s=phase*25+LETTERS.index(c);seq.append(s);counts[s]+=1;phase=(phase+1)%period
        seqs.append(seq)
    return seqs,counts,np.repeat(np.arange(period),25),labels,space


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());lm=train_pack('middle_high_german',2);rows=[];maps=[];screen=[]
    for reset in ('GROUP','LINE'):
        for period in (2,3,4):
            args=encoded(paths,period,reset);bits,mapping,digest=search_encoded(*args,lm,11101);key=3+math.log2(6)+math.log2(2)+math.log2(3)+(period*25)*math.log2(27)+universal_uint_bits(2);total=key+bits+fixed;item={'reset':reset,'period':period,'seed':11101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-base['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    w=min(screen,key=lambda x:x['total_bits']);args=encoded(paths,w['period'],w['reset'])
    for seed in (11102,11103):
        bits,mapping,digest=search_encoded(*args,lm,seed);key=3+math.log2(6)+math.log2(2)+math.log2(3)+(w['period']*25)*math.log2(27)+universal_uint_bits(2);total=key+bits+fixed;item={'reset':w['reset'],'period':w['period'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-base['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);same=[x for x in rows if x['reset']==w['reset'] and x['period']==w['period']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_null_bits']<0 else 'STOP')+'_PERIODIC_CIPHER_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_PERIODIC_CIPHER_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'reset':w['reset'],'period':w['period']},'best':best,'rows':rows,'claim_ceiling':'Exploratory periodic key screen only; no cipher, language, or plaintext claim.'};(ROOT/'gdt001_periodic_cipher_results.json').write_bytes(canonical(result));(ROOT/'gdt001_periodic_cipher_mappings.json').write_bytes(canonical({'schema':'GDT001_PERIODIC_CIPHER_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_periodic_cipher_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_reset':best['reset'],'best_period':best['period'],'best_bps':best['bits_per_symbol'],'null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
