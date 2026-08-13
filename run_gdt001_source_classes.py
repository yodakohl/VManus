#!/usr/bin/env python3
"""Source-only contextual allograph classes, with full map and inverse costs."""

import csv,hashlib,json,math
from collections import Counter
import numpy as np
from gdt001_core import ROOT,LETTERS,SOURCE_ALPHABET,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def profiles(paths):
    x=np.zeros((25,54),dtype=np.float64)
    for p in paths:
        for w in p.words:
            for i,c in enumerate(w):
                a=LETTERS.index(c);left=25 if i==0 else LETTERS.index(w[i-1]);right=25 if i+1==len(w) else LETTERS.index(w[i+1]);x[a,left]+=1;x[a,26+right]+=1;x[a,52+(i==0)]+=1
    x=(x+.5)/(x.sum(1,keepdims=True)+.5*x.shape[1]);return x


def hierarchy(x):
    clusters=[(i,) for i in range(25)];snap={25:clusters[:]}
    while len(clusters)>2:
        best=None
        for i in range(len(clusters)):
            for j in range(i+1,len(clusters)):
                a=np.mean(x[list(clusters[i])],0);b=np.mean(x[list(clusters[j])],0);cost=float(np.sum((a-b)**2))*len(clusters[i])*len(clusters[j])/(len(clusters[i])+len(clusters[j]));cand=(cost,clusters[i],clusters[j],i,j)
                if best is None or cand<best:best=cand
        _,a,b,i,j=best;clusters=[c for z,c in enumerate(clusters) if z not in (i,j)]+[tuple(sorted(a+b))];clusters.sort();snap[len(clusters)]=clusters[:]
    return snap


def encode(paths,clusters):
    mapping={s:i for i,c in enumerate(clusters) for s in c};space=len(clusters);seqs=[];counts=np.zeros(len(clusters));symbol_counts=Counter()
    for p in paths:
        seq=[]
        for c in p.source_line:
            if c==' ':seq.append(space)
            else:s=LETTERS.index(c);x=mapping[s];seq.append(x);counts[x]+=1;symbol_counts[s]+=1
        seqs.append(seq)
    inverse=sum(categorical_bits([symbol_counts[s] for s in c]) for c in clusters)
    return seqs,counts,np.zeros(len(clusters),dtype=np.int64),[''.join(LETTERS[s] for s in c) for c in clusters],space,inverse


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));snap=hierarchy(profiles(paths));rows=[]
    for k in range(2,26):
        seqs,counts,cats,labels,space,inverse=encode(paths,snap[k]);payload=kt_ngram_bits(seqs,k+1,2)+inverse;key=3+universal_uint_bits(k)+25*math.log2(k)+universal_uint_bits(2);total=key+payload+fixed;decoder={'classes':labels,'order':2,'inverse':'Dirichlet-1/2 within class'};rows.append({'class_count':k,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_and_inverse_bits':payload,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical(decoder)).hexdigest(),'cpu_exact':True})
    winner=min(rows,key=lambda x:x['total_bits']);seqs,counts,cats,labels,space,inverse=encode(paths,snap[winner['class_count']]);language=[];maps=[]
    for lang in PACK_NAMES:
        bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,train_pack(lang,2),18101,population=4096,generations=15);key=3+math.log2(6)+universal_uint_bits(winner['class_count'])+25*math.log2(winner['class_count'])+universal_uint_bits(2)+winner['class_count']*math.log2(27);total=key+bits+inverse+fixed;item={'class_count':winner['class_count'],'language':lang,'seed':18101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_source_class_bits':total-winner['total_bits'],'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'language_and_inverse_bits':bits+inverse,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};language.append(item);maps.append(item|{'mapping':mapping,'classes':labels})
    w=min(language,key=lambda x:x['total_bits']);lm=train_pack(w['language'],2)
    for seed in (18102,18103):
        bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,lm,seed,population=4096,generations=15);key=3+math.log2(6)+universal_uint_bits(winner['class_count'])+25*math.log2(winner['class_count'])+universal_uint_bits(2)+winner['class_count']*math.log2(27);total=key+bits+inverse+fixed;item={'class_count':winner['class_count'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_source_class_bits':total-winner['total_bits'],'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'language_and_inverse_bits':bits+inverse,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};language.append(item);maps.append(item|{'mapping':mapping,'classes':labels})
    best=min(language,key=lambda x:x['total_bits']);same=[x for x in language if x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_source_class_bits']<0 else 'STOP')+'_SOURCE_CLASSES_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_SOURCE_CLASSES_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'selected_source_classes':winner,'selected_classes':labels,'best_language':best,'rows':rows,'language_rows':language,'claim_ceiling':'Exploratory anonymous source classes and language mappings; no class is an established glyph, sound, meaning, or plaintext unit.'};(ROOT/'gdt001_source_class_results.json').write_bytes(canonical(result));(ROOT/'gdt001_source_class_mappings.json').write_bytes(canonical({'schema':'GDT001_SOURCE_CLASS_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_source_class_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    with (ROOT/'gdt001_source_class_language.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(language[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(language)
    print(json.dumps({'decision':decision,'source_classes':winner['class_count'],'source_bps':winner['bits_per_symbol'],'source_gap':winner['gap_vs_global_null_bits'],'best_language':best['language'],'language_bps':best['bits_per_symbol'],'language_gap_vs_source':best['gap_vs_source_class_bits']}))


if __name__=='__main__':main()
