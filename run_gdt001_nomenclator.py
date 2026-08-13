#!/usr/bin/env python3
"""Limited frequent-group nomenclator plus shared language/null payload."""

import csv, hashlib, json, math
from collections import Counter
import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def split(paths,k):
    freq=Counter(w for p in paths for w in p.words); dictionary=[w for w,_ in sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:k]]; known=set(dictionary)
    sequences=[];counts=np.zeros(25);nom=Counter();route=Counter()
    for p in paths:
        run=[]
        for word in p.words:
            if word in known:
                route['NOM']+=1;nom[word]+=1
                if run:sequences.append(run);run=[]
            else:
                route['LANG']+=1
                if run:run.append(25)
                for c in word:x=LETTERS.index(c);run.append(x);counts[x]+=1
        if run:sequences.append(run)
    dictionary_bits=universal_uint_bits(k)+sum(universal_uint_bits(len(w))+len(w)*math.log2(25) for w in dictionary)
    route_bits=categorical_bits([route['NOM'],route['LANG']]);nom_bits=categorical_bits([nom[w] for w in dictionary]) if dictionary else 0.
    return sequences,counts,dictionary,nom,dictionary_bits+route_bits+nom_bits


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);lm=train_pack('middle_high_german',2);global_null=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];maps=[];screen=[]
    for k in (0,16,32,64,128,256):
        seqs,counts,dictionary,nom,common=split(paths,k);null_payload=kt_ngram_bits(seqs,26,2);null_key=3+universal_uint_bits(2)+common;null_total=null_key+null_payload+fixed
        rows.append({'model':'MATCHED_NULL','nomenclator_size':k,'seed':0,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_global_null_bits':null_total-global_null['total_bits'],'gap_vs_matched_null_bits':0.,'key_common_bits':null_key,'payload_bits':null_payload,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical(dictionary)).hexdigest(),'cpu_exact':True})
        bits,mapping,digest=search_encoded(seqs,counts,np.zeros(25,dtype=np.int64),list(LETTERS),25,lm,7101);key=3+math.log2(6)+universal_uint_bits(2)+25*math.log2(27)+common;total=key+bits+fixed
        item={'model':'NOMENCLATOR_MHG','nomenclator_size':k,'seed':7101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-global_null['total_bits'],'gap_vs_matched_null_bits':total-null_total,'key_common_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append({'nomenclator_size':k,'seed':7101,'dictionary':[{'source_group':w,'latent':f'NOM_{i:03d}','occurrences':nom[w]} for i,w in enumerate(dictionary)],'mapping':mapping,'decoder_hash':digest})
    winner=min(screen,key=lambda x:x['total_bits'])['nomenclator_size']
    seqs,counts,dictionary,nom,common=split(paths,winner);null_total=next(r['total_bits'] for r in rows if r['model']=='MATCHED_NULL' and r['nomenclator_size']==winner)
    for seed in (7102,7103):
        bits,mapping,digest=search_encoded(seqs,counts,np.zeros(25,dtype=np.int64),list(LETTERS),25,lm,seed);key=3+math.log2(6)+universal_uint_bits(2)+25*math.log2(27)+common;total=key+bits+fixed
        rows.append({'model':'NOMENCLATOR_MHG','nomenclator_size':winner,'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-global_null['total_bits'],'gap_vs_matched_null_bits':total-null_total,'key_common_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});maps.append({'nomenclator_size':winner,'seed':seed,'dictionary':[{'source_group':w,'latent':f'NOM_{i:03d}','occurrences':nom[w]} for i,w in enumerate(dictionary)],'mapping':mapping,'decoder_hash':digest})
    best=min((r for r in rows if r['model']=='NOMENCLATOR_MHG'),key=lambda x:x['total_bits']);stable=len({r['decoder_hash'] for r in rows if r['model']=='NOMENCLATOR_MHG' and r['nomenclator_size']==winner})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_NOMENCLATOR_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_NOMENCLATOR_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner_size':winner,'best':best,'rows':rows,'claim_ceiling':'Exploratory limited opaque nomenclator; anonymous entries and tentative language units have no confirmed meanings.'};(ROOT/'gdt001_nomenclator_results.json').write_bytes(canonical(result));(ROOT/'gdt001_nomenclator_decoders.json').write_bytes(canonical({'schema':'GDT001_NOMENCLATOR_DECODERS_V1','decoders':maps}))
    with (ROOT/'gdt001_nomenclator_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_k':best['nomenclator_size'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'global_gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
