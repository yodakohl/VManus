#!/usr/bin/env python3
"""Preceding-source-conditioned allographic language key."""

import csv,hashlib,json,math
import numpy as np
from gdt001_core import ROOT, LETTERS, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def encoded(paths):
    labels=[f'{p}>{c}' for p in ('<BOS>',*LETTERS) for c in LETTERS];counts=np.zeros(650);seqs=[];space=650
    for path in paths:
        seq=[]
        for wi,w in enumerate(path.words):
            if wi:seq.append(space)
            prev=0
            for c in w:
                s=prev*25+LETTERS.index(c);seq.append(s);counts[s]+=1;prev=LETTERS.index(c)+1
        seqs.append(seq)
    return seqs,counts,np.repeat(np.arange(26),25),labels,space


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);args=encoded(paths);lm=train_pack('middle_high_german',2);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);null=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];maps=[]
    key=3+math.log2(6)+universal_uint_bits(2)+650*math.log2(27)
    for seed in (9101,9102,9103):
        bits,mapping,digest=search_encoded(*args,lm,seed);total=key+bits+fixed;rows.append({'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});maps.append({'seed':seed,'decoder_hash':digest,'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);stable=len({x['decoder_hash'] for x in rows})==1;decision=('CONTINUE' if best['gap_vs_null_bits']<0 else 'STOP')+'_PREVIOUS_CONTEXT_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_PREVIOUS_CONTEXT_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'best':best,'rows':rows,'claim_ceiling':'Exploratory preceding-source-conditioned allography only; no language or plaintext claim.'};(ROOT/'gdt001_previous_context_results.json').write_bytes(canonical(result));(ROOT/'gdt001_previous_context_mappings.json').write_bytes(canonical({'schema':'GDT001_PREVIOUS_CONTEXT_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_previous_context_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_bps':best['bits_per_symbol'],'null_bps':null['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
