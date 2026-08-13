#!/usr/bin/env python3
"""Exact fixed-null-set screens with reversible deletion-position coding."""

import csv,hashlib,json,math
from collections import Counter
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded

SETS=("q","y","i","e","a","o","qy","dst","qdst")


def encoded(paths,nulls):
    active=[c for c in LETTERS if c not in nulls];index={c:i for i,c in enumerate(active)};space=len(active);seqs=[];counts=np.zeros(len(active));flags=Counter();nul=Counter()
    for p in paths:
        seq=[]
        for wi,w in enumerate(p.words):
            if wi:seq.append(space)
            for c in w:
                if c in nulls:flags['NULL']+=1;nul[c]+=1
                else:x=index[c];seq.append(x);counts[x]+=1;flags['ACTIVE']+=1
        seqs.append(seq)
    extra=categorical_bits([flags['NULL'],flags['ACTIVE']])+categorical_bits([nul[c] for c in sorted(nulls)])
    return (seqs,counts,np.zeros(len(active),dtype=np.int64),active,space),extra


def run(paths,nulls,language,seed):
    args,extra=encoded(paths,nulls);bits,mapping,digest=search_encoded(*args,train_pack(language,2),seed);k=len(nulls);subset=math.log2(math.comb(25,k));key=3+math.log2(6)+universal_uint_bits(2)+universal_uint_bits(k)+subset+(25-k)*math.log2(27);return bits+extra,key,mapping,digest,extra


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];maps=[];screen=[]
    for nulls in SETS:
        bits,key,mapping,digest,extra=run(paths,nulls,'middle_high_german',10101);total=bits+key+fixed;item={'null_symbols':nulls,'language':'middle_high_german','seed':10101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-base['total_bits'],'key_bits':key,'modeled_and_deletion_bits':bits,'deletion_bits':extra,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    ns=min(screen,key=lambda x:x['total_bits'])['null_symbols']
    for language in PACK_NAMES:
        if language=='middle_high_german':continue
        bits,key,mapping,digest,extra=run(paths,ns,language,10101);total=bits+key+fixed;item={'null_symbols':ns,'language':language,'seed':10101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-base['total_bits'],'key_bits':key,'modeled_and_deletion_bits':bits,'deletion_bits':extra,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    lang=min(rows,key=lambda x:x['total_bits'])['language']
    for seed in (10102,10103):
        bits,key,mapping,digest,extra=run(paths,ns,lang,seed);total=bits+key+fixed;item={'null_symbols':ns,'language':lang,'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-base['total_bits'],'key_bits':key,'modeled_and_deletion_bits':bits,'deletion_bits':extra,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);same=[x for x in rows if x['null_symbols']==ns and x['language']==lang];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_null_bits']<0 else 'STOP')+'_NULL_SYMBOLS_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_NULL_SYMBOLS_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner_nulls':ns,'screen_winner_language':lang,'best':best,'rows':rows,'claim_ceiling':'Exploratory fixed-null-symbol transducer only; no language, sound, or plaintext claim.'};(ROOT/'gdt001_null_symbol_results.json').write_bytes(canonical(result));(ROOT/'gdt001_null_symbol_mappings.json').write_bytes(canonical({'schema':'GDT001_NULL_SYMBOL_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_null_symbol_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_nulls':best['null_symbols'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
