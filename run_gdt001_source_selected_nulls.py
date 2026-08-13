#!/usr/bin/env python3
"""Select null signs by source-only MDL, then test language without reselection."""

import csv,hashlib,itertools,json,math
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded

_PATHS=None;_FIXED=0.;_SYMBOLS=0.;_BASE_TOTAL=0.


def encoded(paths,nulls):
    active=[c for c in LETTERS if c not in nulls];ix={c:i for i,c in enumerate(active)};space=len(active);seqs=[];counts=np.zeros(len(active));flags=[];nul=[]
    for p in paths:
        seq=[]
        for wi,w in enumerate(p.words):
            if wi:seq.append(space)
            for c in w:
                if c in nulls:flags.append(1);nul.append(c)
                else:x=ix[c];seq.append(x);counts[x]+=1;flags.append(0)
        seqs.append(seq)
    common=categorical_bits([flags.count(0),flags.count(1)])+categorical_bits([nul.count(c) for c in sorted(nulls)])
    return seqs,counts,np.zeros(len(active),dtype=np.int64),active,space,common


def score_null(tup):
    k=len(tup);subset=math.log2(math.comb(25,k));seqs,counts,cats,active,space,common=encoded(_PATHS,frozenset(tup));payload=kt_ngram_bits(seqs,len(active)+1,2);key=3+universal_uint_bits(k)+subset+universal_uint_bits(2)+common;total=key+payload+_FIXED
    return {'null_symbols':''.join(tup),'total_bits':total,'bits_per_symbol':total/_SYMBOLS,'gap_vs_global_null_bits':total-_BASE_TOTAL,'key_bits':key,'payload_bits':payload,'fixed_bits':_FIXED,'decoder_hash':hashlib.sha256(canonical({'nulls':tup,'order':2})).hexdigest(),'cpu_exact':True}


def main():
    global _PATHS,_FIXED,_SYMBOLS,_BASE_TOTAL
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));_PATHS=paths;_FIXED=fixed;_SYMBOLS=symbols;_BASE_TOTAL=base['total_bits'];jobs=[t for k in (1,2,3) for t in itertools.combinations(LETTERS,k)]
    with ProcessPoolExecutor(max_workers=32) as pool:null_rows=list(pool.map(score_null,jobs,chunksize=4))
    winner=min(null_rows,key=lambda x:x['total_bits']);nulls=frozenset(winner['null_symbols']);seqs,counts,cats,active,space,common=encoded(paths,nulls);language_rows=[];maps=[]
    for lang in PACK_NAMES:
        bits,mapping,digest=search_encoded(seqs,counts,cats,active,space,train_pack(lang,2),17101,population=4096,generations=15);k=len(nulls);key=3+math.log2(6)+universal_uint_bits(k)+math.log2(math.comb(25,k))+universal_uint_bits(2)+common+len(active)*math.log2(27);total=key+bits+fixed;item={'null_symbols':winner['null_symbols'],'language':lang,'seed':17101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_selected_null_bits':total-winner['total_bits'],'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};language_rows.append(item);maps.append(item|{'mapping':mapping})
    w=min(language_rows,key=lambda x:x['total_bits']);lm=train_pack(w['language'],2)
    for seed in (17102,17103):
        bits,mapping,digest=search_encoded(seqs,counts,cats,active,space,lm,seed,population=4096,generations=15);k=len(nulls);key=3+math.log2(6)+universal_uint_bits(k)+math.log2(math.comb(25,k))+universal_uint_bits(2)+common+len(active)*math.log2(27);total=key+bits+fixed;item={'null_symbols':winner['null_symbols'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_selected_null_bits':total-winner['total_bits'],'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};language_rows.append(item);maps.append(item|{'mapping':mapping})
    best=min(language_rows,key=lambda x:x['total_bits']);same=[x for x in language_rows if x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_selected_null_bits']<0 else 'STOP')+'_SOURCE_SELECTED_NULLS_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_SOURCE_SELECTED_NULLS_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'selected_source_null':winner,'best_language':best,'null_candidates':len(null_rows),'null_rows':null_rows,'language_rows':language_rows,'claim_ceiling':'Exploratory source-selected deletion channel; null signs and language mappings are not established readings or meanings.'};(ROOT/'gdt001_source_selected_null_results.json').write_bytes(canonical(result));(ROOT/'gdt001_source_selected_null_mappings.json').write_bytes(canonical({'schema':'GDT001_SOURCE_SELECTED_NULL_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_source_selected_null_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(null_rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(null_rows)
    with (ROOT/'gdt001_source_selected_null_language.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(language_rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(language_rows)
    print(json.dumps({'decision':decision,'selected_nulls':winner['null_symbols'],'selected_null_bps':winner['bits_per_symbol'],'selected_null_global_gap':winner['gap_vs_global_null_bits'],'best_language':best['language'],'language_bps':best['bits_per_symbol'],'language_gap_vs_selected':best['gap_vs_selected_null_bits']}))


if __name__=='__main__':main()
