#!/usr/bin/env python3
"""Reversible learned prefix/core/suffix grammar with complete MDL."""

import csv,hashlib,json,math
from collections import Counter
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


def inventory(paths,k,side):
    c=Counter()
    for p in paths:
        for w in p.words:
            for n in (1,2,3):
                if len(w)>n:c[w[:n] if side=='PREFIX' else w[-n:]]+=1
    return [x for x,_ in sorted(c.items(),key=lambda z:(-z[1],z[0]))[:k]]


def parse(w,prefixes,suffixes):
    p=max((x for x in prefixes if w.startswith(x)),key=len,default='');rest=w[len(p):]
    s=max((x for x in suffixes if rest.endswith(x)),key=len,default='');core=rest[:-len(s)] if s else rest
    return p,core,s


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));rows=[];decoders=[]
    for kp in (0,4,8,16,32):
        for ks in (0,4,8,16,32):
            prefixes=inventory(paths,kp,'PREFIX');suffixes=inventory(paths,ks,'SUFFIX');pc=Counter();sc=Counter();length=Counter();line_n=Counter();cores=[];programs=[]
            for p in paths:
                line_n[len(p.words)]+=1;rec=[]
                for w in p.words:
                    pre,core,suf=parse(w,prefixes,suffixes);pc[pre]+=1;sc[suf]+=1;length[len(core)]+=1;cores.append(tuple(LETTERS.index(c) for c in core));rec.append({'prefix':pre,'core':core,'suffix':suf})
                    if pre+core+suf!=w:raise AssertionError(w)
                programs.append(rec)
            payload=categorical_bits([pc[x] for x in ['',*prefixes]])+categorical_bits([sc[x] for x in ['',*suffixes]])+categorical_bits([length[x] for x in sorted(length)])+categorical_bits([line_n[x] for x in sorted(line_n)])+kt_ngram_bits(cores,25,2)
            inv=universal_uint_bits(kp)+universal_uint_bits(ks)+sum(universal_uint_bits(len(x))+len(x)*math.log2(25) for x in prefixes+suffixes);key=3+universal_uint_bits(2)+inv;total=key+payload+fixed;decoder={'prefixes':prefixes,'suffixes':suffixes,'parse':'longest prefix then longest suffix of remainder','prefix_counts':dict(pc),'suffix_counts':dict(sc)};digest=hashlib.sha256(canonical(decoder)).hexdigest();rows.append({'prefix_count':kp,'suffix_count':ks,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_bits':payload,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});decoders.append(decoder|{'decoder_hash':digest})
    best=min(rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best['gap_vs_global_null_bits']<0 else 'STOP')+'_MORPHOLOGY_GRAMMAR'
    result={'schema':'GDT001_MORPHOLOGY_GRAMMAR_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'best':best,'rows':rows,'claim_ceiling':'Exploratory reversible prefix/core/suffix grammar; components have no sounds, meanings, language, or plaintext status.'};(ROOT/'gdt001_morphology_grammar_results.json').write_bytes(canonical(result));(ROOT/'gdt001_morphology_grammar_decoders.json').write_bytes(canonical({'schema':'GDT001_MORPHOLOGY_GRAMMAR_DECODERS_V1','decoders':decoders}))
    with (ROOT/'gdt001_morphology_grammar_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_prefixes':best['prefix_count'],'best_suffixes':best['suffix_count'],'best_bps':best['bits_per_symbol'],'null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
