#!/usr/bin/env python3
"""Historical language only on confirmed prose; nonprose remains source-coded."""

import csv,hashlib,json,math
import numpy as np
from gdt001_core import ROOT,LETTERS,SOURCE_ALPHABET,canonical,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(paths):
    seqs=[];counts=np.zeros(25);space=25
    for p in paths:
        seq=[]
        for c in p.source_line:
            if c==' ':seq.append(space)
            else:x=LETTERS.index(c);seq.append(x);counts[x]+=1
        seqs.append(seq)
    return seqs,counts,np.zeros(25,dtype=np.int64),list(LETTERS),space


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);prose=[p for l,p in zip(lines,paths) if l.grammar_scope=='CONFIRMED_PROSE'];other=[p for l,p in zip(lines,paths) if l.grammar_scope!='CONFIRMED_PROSE'];fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);source_winner=json.load(open(ROOT/'gdt001_source_selected_null_results.json'))['selected_source_null'];other_bits=kt_ngram_bits([p.source_ids for p in other],len(SOURCE_ALPHABET),2);prose_null=kt_ngram_bits([p.source_ids for p in prose],len(SOURCE_ALPHABET),2);matched_key=3+1+2*universal_uint_bits(2);matched_total=matched_key+other_bits+prose_null+fixed;rows=[];maps=[];args=encoded(prose)
    for lang in PACK_NAMES:
        bits,mapping,digest=search_encoded(*args,train_pack(lang,2),20101,population=4096,generations=15);key=3+1+math.log2(6)+2*universal_uint_bits(2)+25*math.log2(27);total=key+other_bits+bits+fixed;item={'language':lang,'seed':20101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_split_null_bits':total-matched_total,'gap_vs_source_winner_bits':total-source_winner['total_bits'],'key_bits':key,'prose_language_reverse_bits':bits,'nonprose_source_bits':other_bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    w=min(rows,key=lambda x:x['total_bits']);lm=train_pack(w['language'],2)
    for seed in (20102,20103):
        bits,mapping,digest=search_encoded(*args,lm,seed,population=4096,generations=15);key=3+1+math.log2(6)+2*universal_uint_bits(2)+25*math.log2(27);total=key+other_bits+bits+fixed;item={'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_split_null_bits':total-matched_total,'gap_vs_source_winner_bits':total-source_winner['total_bits'],'key_bits':key,'prose_language_reverse_bits':bits,'nonprose_source_bits':other_bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);same=[x for x in rows if x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_split_null_bits']<0 else 'STOP')+'_PROSE_LANGUAGE_HYBRID_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_PROSE_LANGUAGE_HYBRID_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'counts':{'confirmed_prose_lines':len(prose),'nonprose_lines':len(other)},'matched_split_null':{'total_bits':matched_total,'bits_per_symbol':matched_total/symbols,'prose_source_bits':prose_null,'nonprose_source_bits':other_bits},'best':best,'rows':rows,'claim_ceiling':'Exploratory metadata-conditioned hybrid; no confirmed language, plaintext, meaning, or translation.'};(ROOT/'gdt001_prose_language_hybrid_results.json').write_bytes(canonical(result));(ROOT/'gdt001_prose_language_hybrid_mappings.json').write_bytes(canonical({'schema':'GDT001_PROSE_LANGUAGE_HYBRID_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_prose_language_hybrid_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_split_bps':matched_total/symbols,'matched_gap_bits':best['gap_vs_matched_split_null_bits'],'source_winner_gap_bits':best['gap_vs_source_winner_bits']}))


if __name__=='__main__':main()
