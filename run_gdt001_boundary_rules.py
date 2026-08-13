#!/usr/bin/env python3
"""Compact source-conditioned plaintext boundary rules with matched nulls."""

import csv,hashlib,json,math
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def keep(scheme,left,right):
    return {'ALL':True,'NONE':False,'AFTER_Y':left.endswith('y'),'BEFORE_Q':right.startswith('q'),'Y_OR_Q':left.endswith('y') or right.startswith('q'),'AFTER_SUFFIX':left[-1] in 'ynrlmsdg','BEFORE_CARRIER':right[0] in 'qdst','LONG_PAIR':len(left)>=5 and len(right)>=5,'SHORT_PAIR':len(left)<=3 or len(right)<=3}[scheme]


def encoded(paths,scheme):
    seqs=[];counts=np.zeros(25);space=25;retained=total=internal=0
    for p in paths:
        seq=[]
        for wi,w in enumerate(p.words):
            if wi:
                total+=1
                if keep(scheme,p.words[wi-1],w):seq.append(space);retained+=1
            for c in w:x=LETTERS.index(c);seq.append(x);counts[x]+=1
            internal+=max(0,len(w)-1)
        seqs.append(seq)
    omitted=total-retained
    boundary_side=0.0 if omitted==0 else categorical_bits([internal,omitted])
    return seqs,counts,np.zeros(25,dtype=np.int64),list(LETTERS),space,retained,total,boundary_side


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);source=json.load(open(ROOT/'gdt001_source_selected_null_results.json'))['selected_source_null'];schemes=('ALL','NONE','AFTER_Y','BEFORE_Q','Y_OR_Q','AFTER_SUFFIX','BEFORE_CARRIER','LONG_PAIR','SHORT_PAIR');rows=[];maps=[];screen=[]
    for scheme in schemes:
        seqs,counts,cats,labels,space,retained,total,boundary_side=encoded(paths,scheme);matched=kt_ngram_bits(seqs,26,2);key0=3+math.log2(len(schemes))+universal_uint_bits(2);null_total=key0+matched+boundary_side+fixed;rows.append({'model':'MATCHED_BOUNDARY_NULL','scheme':scheme,'language':'_','seed':0,'retained_boundaries':retained,'total_boundaries':total,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_matched_null_bits':0.,'gap_vs_source_winner_bits':null_total-source['total_bits'],'key_bits':key0,'boundary_side_bits':boundary_side,'payload_bits':matched,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical({'scheme':scheme,'order':2,'boundary_side':'KT_BINARY_GAP_MASK'})).hexdigest(),'cpu_exact':True})
        for lang in PACK_NAMES:
            bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,train_pack(lang,2),22101,population=4096,generations=15);key=3+math.log2(len(schemes))+math.log2(6)+universal_uint_bits(2)+25*math.log2(27);total_bits=key+bits+boundary_side+fixed;item={'model':'BOUNDARY_LANGUAGE','scheme':scheme,'language':lang,'seed':22101,'retained_boundaries':retained,'total_boundaries':total,'total_bits':total_bits,'bits_per_symbol':total_bits/symbols,'gap_vs_matched_null_bits':total_bits-null_total,'gap_vs_source_winner_bits':total_bits-source['total_bits'],'key_bits':key,'boundary_side_bits':boundary_side,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);maps.append(item|{'mapping':mapping})
    w=min(screen,key=lambda x:x['total_bits']);seqs,counts,cats,labels,space,retained,total,boundary_side=encoded(paths,w['scheme']);null_total=next(x['total_bits'] for x in rows if x['model']=='MATCHED_BOUNDARY_NULL' and x['scheme']==w['scheme']);lm=train_pack(w['language'],2)
    for seed in (22102,22103):
        bits,mapping,digest=search_encoded(seqs,counts,cats,labels,space,lm,seed,population=4096,generations=15);key=3+math.log2(len(schemes))+math.log2(6)+universal_uint_bits(2)+25*math.log2(27);total_bits=key+bits+boundary_side+fixed;item={'model':'BOUNDARY_LANGUAGE','scheme':w['scheme'],'language':w['language'],'seed':seed,'retained_boundaries':retained,'total_boundaries':total,'total_bits':total_bits,'bits_per_symbol':total_bits/symbols,'gap_vs_matched_null_bits':total_bits-null_total,'gap_vs_source_winner_bits':total_bits-source['total_bits'],'key_bits':key,'boundary_side_bits':boundary_side,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append(item|{'mapping':mapping})
    best=min((x for x in rows if x['model']=='BOUNDARY_LANGUAGE'),key=lambda x:x['total_bits']);same=[x for x in rows if x['model']=='BOUNDARY_LANGUAGE' and x['scheme']==w['scheme'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_BOUNDARY_RULES_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_BOUNDARY_RULES_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'scheme':w['scheme'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory source-conditioned plaintext-boundary rules; no source separator, language, word, or plaintext interpretation is established.'};(ROOT/'gdt001_boundary_rule_results.json').write_bytes(canonical(result));(ROOT/'gdt001_boundary_rule_mappings.json').write_bytes(canonical({'schema':'GDT001_BOUNDARY_RULE_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_boundary_rule_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_scheme':best['scheme'],'best_language':best['language'],'retained':best['retained_boundaries'],'total_boundaries':best['total_boundaries'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'source_winner_gap_bits':best['gap_vs_source_winner_bits']}))


if __name__=='__main__':main()
