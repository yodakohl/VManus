#!/usr/bin/env python3
"""Map formal STA families/members directly to frozen historical language packs."""

import csv,hashlib,json,math
from collections import Counter,defaultdict
import numpy as np
from gdt001_core import ROOT,canonical,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def data():
    corpus=json.load(open(ROOT/'gdt001_corpus_lattice.json'));_,lines=load_lattice();paths=common_selected_paths(lines);fields={'ZL3b':'zl_sta_codes','IT2a':'it_sta_codes','RF1b':'rf_sta_codes'};fseq=[];mseq=[];fm=defaultdict(Counter)
    for path,obj in zip(paths,corpus['lines']):
        a=obj['sta_alignment']
        if not a:continue
        fs=list(a['family_sequence']);ms=a[fields[path.editions[0]]];fseq.append(fs);mseq.append(ms)
        for f,m in zip(fs,ms):fm[f][m]+=1
    cond=sum(__import__('gdt001_core').categorical_bits([c[m] for m in sorted(c)]) for c in fm.values())
    out={}
    for name,seqs,extra in [('FAMILY_PLUS_MEMBER',fseq,cond),('EXACT_MEMBER',mseq,0.)]:
        vocab=sorted({x for s in seqs for x in s});idx={x:i for i,x in enumerate(vocab)};ids=[[idx[x] for x in s] for s in seqs];counts=np.zeros(len(vocab))
        for s in ids:
            for x in s:counts[x]+=1
        out[name]=(ids,counts,np.zeros(len(vocab),dtype=np.int64),vocab,None,extra)
    return out


def main():
    D=data();sta=json.load(open(ROOT/'gdt001_sta_representation_results.json'));nulls={r['representation']:r for r in sta['rows'] if r['order']==2};rows=[];maps=[];screen=[]
    for rep,args in D.items():
        seqs,counts,cats,labels,space,extra=args
        for lang in PACK_NAMES:
            bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,train_pack(lang,2),12101);n=len(labels);key=3+math.log2(6)+math.log2(2)+universal_uint_bits(2)+n*math.log2(27);constant=nulls[rep]['total_bits']-nulls[rep]['structural_bits']-nulls[rep]['key_bits'];total=key+bits+extra+constant;item={'representation':rep,'language':lang,'seed':12101,'total_bits':total,'bits_per_symbol':total/194324,'gap_vs_matched_sta_null_bits':total-nulls[rep]['total_bits'],'gap_vs_character_null_bits':total-593383.2936568179,'key_bits':key,'language_reverse_bits':bits,'member_residual_bits':extra,'constant_reconstruction_bits':constant,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    w=min(screen,key=lambda x:x['total_bits']);args=D[w['representation']];lm=train_pack(w['language'],2)
    for seed in (12102,12103):
        seqs,counts,cats,labels,space,extra=args;bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,lm,seed);n=len(labels);key=3+math.log2(6)+math.log2(2)+universal_uint_bits(2)+n*math.log2(27);constant=nulls[w['representation']]['total_bits']-nulls[w['representation']]['structural_bits']-nulls[w['representation']]['key_bits'];total=key+bits+extra+constant;item={'representation':w['representation'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/194324,'gap_vs_matched_sta_null_bits':total-nulls[w['representation']]['total_bits'],'gap_vs_character_null_bits':total-593383.2936568179,'key_bits':key,'language_reverse_bits':bits,'member_residual_bits':extra,'constant_reconstruction_bits':constant,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);same=[x for x in rows if x['representation']==w['representation'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_sta_null_bits']<0 else 'STOP')+'_STA_LANGUAGE_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_STA_LANGUAGE_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'representation':w['representation'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory formal-token language mapping only; no STA sound, language, meaning, or plaintext claim.'};(ROOT/'gdt001_sta_language_results.json').write_bytes(canonical(result));(ROOT/'gdt001_sta_language_mappings.json').write_bytes(canonical({'schema':'GDT001_STA_LANGUAGE_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_sta_language_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_representation':best['representation'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_sta_null_bits'],'character_gap_bits':best['gap_vs_character_null_bits']}))


if __name__=='__main__':main()
