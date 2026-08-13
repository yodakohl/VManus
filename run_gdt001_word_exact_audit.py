#!/usr/bin/env python3
"""Exact small-codebook language audit and dense source-null sweep."""

import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
import numpy as np
from gdt001_core import ROOT,canonical,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_word_nomenclator import split


def lm(language,k,order,alpha=.5):
    lines=[];freq=Counter()
    for raw in (ROOT/'.gdt001/language_packs'/f'{language}.txt').read_text().splitlines():ws=raw.split();lines.append(ws);freq.update(ws)
    vocab=[w for w,_ in sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:k]];ix={w:i for i,w in enumerate(vocab)};bos=k;contexts=defaultdict(Counter)
    for ws in lines:
        h=[bos]*order
        for w in ws:
            if w in ix:
                contexts[tuple(h)][ix[w]]+=1
                if order:h=h[1:]+[ix[w]]
            else:h=[bos]*order
    shape=(k+1,)*order+(k,);costs=np.empty(shape,dtype=np.float64)
    for history in itertools.product(range(k+1),repeat=order):
        c=contexts[history];den=sum(c.values())+alpha*k
        costs[history]=[-math.log2((c[x]+alpha)/den) for x in range(k)]
    return vocab,costs


def exact(runs,k,order,costs):
    bos=k;c=Counter()
    for run in runs:
        h=[bos]*order
        for x in run:c[tuple(h)+(x,)]+=1;h=h[1:]+[x] if order else []
    keys=np.asarray(list(c),dtype=np.int64);freq=np.asarray(list(c.values()),dtype=np.float64);best=None
    permutations=np.asarray(list(itertools.permutations(range(k))),dtype=np.int64)
    for st in range(0,len(permutations),4096):
        p=permutations[st:st+4096];ext=np.concatenate([p,np.full((len(p),1),k,dtype=np.int64)],1);target=ext[:,keys]
        idx=tuple(target[:,:,i] for i in range(order+1));scores=(costs[idx]*freq).sum(1);i=int(np.argmin(scores));candidate=(float(scores[i]),tuple(map(int,p[i])))
        if best is None or candidate<best:best=candidate
    return best


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);old=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));null_rows=[]
    for k in (*range(1,17),20,24,32,48,64,96,128,192,256,384,512):
        source,runs,common=split(paths,k)
        for order in range(4):
            payload=kt_ngram_bits(runs,k,order);key=3+universal_uint_bits(order)+common;total=key+payload+fixed;null_rows.append({'model':'SOURCE_WORD_NULL','k':k,'order':order,'language':'_','total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_old_null_bits':total-old['total_bits'],'gap_vs_matched_null_bits':0.,'key_bits':key,'payload_bits':payload,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical({'source':source,'order':order})).hexdigest(),'cpu_exact':True})
    best_null=min(null_rows,key=lambda x:x['total_bits']);language_rows=[];decoders=[]
    # Exact K<=8 enumeration, all packs and word orders 0..3.
    for k in range(1,9):
        source,runs,common=split(paths,k);matched={o:next(r for r in null_rows if r['k']==k and r['order']==o) for o in range(4)}
        for order in range(4):
            for language in PACK_NAMES:
                target,cost=lm(language,k,order);bits,p=exact(runs,k,order,cost);key=3+math.log2(6)+universal_uint_bits(order)+common+math.lgamma(k+1)/math.log(2);total=key+bits+fixed;mapping=[{'source_group':source[i],'target_word':target[p[i]]} for i in range(k)];digest=hashlib.sha256(canonical(mapping)).hexdigest();language_rows.append({'model':'EXACT_WORD_NOMENCLATOR','k':k,'order':order,'language':language,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_old_null_bits':total-old['total_bits'],'gap_vs_matched_null_bits':total-matched[order]['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});decoders.append({'k':k,'order':order,'language':language,'decoder_hash':digest,'mapping':mapping})
    best_lang=min(language_rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best_lang['gap_vs_matched_null_bits']<0 else 'STOP')+'_EXACT_WORD_LANGUAGE';result={'schema':'GDT001_WORD_EXACT_AUDIT_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'new_nonsemantic_leader':best_null,'best_exact_language':best_lang,'null_rows':null_rows,'language_rows':language_rows,'claim_ceiling':'Exact small-codebook audit; source atoms and target words are formal code assignments, not confirmed readings or meanings.'};(ROOT/'gdt001_word_exact_audit_results.json').write_bytes(canonical(result));(ROOT/'gdt001_word_exact_audit_decoders.json').write_bytes(canonical({'schema':'GDT001_WORD_EXACT_AUDIT_DECODERS_V1','decoders':decoders}))
    rows=null_rows+language_rows
    with (ROOT/'gdt001_word_exact_audit_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'new_null_k':best_null['k'],'new_null_order':best_null['order'],'new_null_bps':best_null['bits_per_symbol'],'gain_vs_old_bits':-best_null['gap_vs_old_null_bits'],'language_k':best_lang['k'],'language_order':best_lang['order'],'language':best_lang['language'],'language_matched_gap_bits':best_lang['gap_vs_matched_null_bits']}))


if __name__=='__main__':main()
