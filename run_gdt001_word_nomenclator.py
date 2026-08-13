#!/usr/bin/env python3
"""Whole-group nomenclator against external historical word bigrams."""

import csv,hashlib,json,math
from collections import Counter,defaultdict
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths


def word_lm(language,k,alpha=.5):
    lines=[];freq=Counter()
    for raw in (ROOT/'.gdt001/language_packs'/f'{language}.txt').read_text().splitlines():
        ws=raw.split();lines.append(ws);freq.update(ws)
    vocab=[w for w,_ in sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:k]];ix={w:i for i,w in enumerate(vocab)};bos=k;counts=np.zeros((k+1,k),dtype=np.float64)
    for ws in lines:
        prev=bos
        for w in ws:
            if w in ix:counts[prev,ix[w]]+=1;prev=ix[w]
            else:prev=bos
    costs=-np.log2((counts+alpha)/(counts.sum(1,keepdims=True)+alpha*k))
    return vocab,costs


def split(paths,k):
    freq=Counter(w for p in paths for w in p.words);vocab=[w for w,_ in sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:k]];ix={w:i for i,w in enumerate(vocab)};runs=[];residual=[];residual_lengths=[];modes=[];line_lengths=[]
    for p in paths:
        line_lengths.append(len(p.words));mode=[];run=[]
        for w in p.words:
            if w in ix:mode.append(1);run.append(ix[w])
            else:
                mode.append(0);residual.append(tuple(LETTERS.index(c) for c in w));residual_lengths.append(len(w))
                if run:runs.append(run);run=[]
        if run:runs.append(run)
        modes.extend(mode)
    common=universal_uint_bits(k)+sum(universal_uint_bits(len(w))+len(w)*math.log2(25) for w in vocab)
    common+=categorical_bits([modes.count(0),modes.count(1)])+categorical_bits([Counter(line_lengths)[n] for n in sorted(set(line_lengths))])
    common+=kt_ngram_bits(residual,25,2)
    maximum=max(residual_lengths,default=0);length_counts=Counter(residual_lengths)
    common+=universal_uint_bits(maximum)+categorical_bits([length_counts[n] for n in range(1,maximum+1)])
    return vocab,runs,common


def sufficient(runs,k):
    c=Counter();bos=k
    for run in runs:
        prev=bos
        for x in run:c[(prev,x)]+=1;prev=x
    keys=np.asarray(list(c),dtype=np.int64);freq=np.asarray(list(c.values()),dtype=np.float64)
    return keys,freq


def score_cpu(costs,keys,freq,maps):
    out=[];k=maps.shape[1]
    for m in maps:
        total=0.
        for (a,b),n in zip(keys,freq):total+=n*costs[k if a==k else m[a],m[b]]
        out.append(total)
    return np.asarray(out)


def score_gpu(costs,keys_np,freq_np,maps):
    import torch
    keys=torch.as_tensor(keys_np,device='cuda');freq=torch.as_tensor(freq_np,device='cuda',dtype=torch.float64);cost=torch.as_tensor(costs,device='cuda',dtype=torch.float64);out=[];k=maps.shape[1]
    for st in range(0,len(maps),1024):
        m=torch.as_tensor(maps[st:st+1024],device='cuda');n=len(m);ext=torch.cat([m,torch.full((n,1),k,device='cuda')],1);out.append((cost[ext[:,keys[:,0]],m[:,keys[:,1]]]*freq).sum(1).cpu().numpy())
    return np.concatenate(out)


def search(costs,runs,k,seed):
    keys,freq=sufficient(runs,k);rng=np.random.default_rng(seed);pop=np.asarray([rng.permutation(k) for _ in range(32768)],dtype=np.int64)
    for _ in range(35):
        s=score_gpu(costs,keys,freq,pop);elite=pop[np.argsort(s)[:128]].copy();ch=elite[rng.integers(0,128,len(pop)-128)].copy();r=np.arange(len(ch));a=rng.integers(0,k,len(ch));b=rng.integers(0,k,len(ch));tmp=ch[r,a].copy();ch[r,a]=ch[r,b];ch[r,b]=tmp;pop=np.vstack([elite,ch])
    s=score_gpu(costs,keys,freq,pop);i=int(np.argmin(s));exact=float(score_cpu(costs,keys,freq,pop[i:i+1])[0]);assert abs(exact-s[i])<2e-6
    return exact,pop[i]


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);global_null=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));rows=[];decoders=[];screen=[]
    for k in (8,16,32):
        source,runs,common=split(paths,k);matched=kt_ngram_bits(runs,k,1);null_key=3+universal_uint_bits(1)+common;null_total=null_key+matched+fixed;rows.append({'model':'MATCHED_WORD_NULL','k':k,'language':'_','seed':0,'total_bits':null_total,'bits_per_symbol':null_total/symbols,'gap_vs_matched_null_bits':0.,'gap_vs_global_null_bits':null_total-global_null['total_bits'],'key_bits':null_key,'payload_bits':matched,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical(source)).hexdigest(),'cpu_exact':True})
        for language in PACK_NAMES:
            target,costs=word_lm(language,k);bits,mapping=search(costs,runs,k,13101);key=3+math.log2(6)+universal_uint_bits(1)+common+math.lgamma(k+1)/math.log(2);total=key+bits+fixed;mapping_rows=[{'source_group':source[i],'target_word':target[int(mapping[i])]} for i in range(k)];digest=hashlib.sha256(canonical(mapping_rows)).hexdigest();item={'model':'WORD_NOMENCLATOR','k':k,'language':language,'seed':13101,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_global_null_bits':total-global_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);screen.append(item);decoders.append(item|{'mapping':mapping_rows})
    w=min(screen,key=lambda x:x['total_bits']);source,runs,common=split(paths,w['k']);target,costs=word_lm(w['language'],w['k']);null_total=next(x['total_bits'] for x in rows if x['model']=='MATCHED_WORD_NULL' and x['k']==w['k'])
    for seed in (13102,13103):
        bits,mapping=search(costs,runs,w['k'],seed);key=3+math.log2(6)+universal_uint_bits(1)+common+math.lgamma(w['k']+1)/math.log(2);total=key+bits+fixed;mapping_rows=[{'source_group':source[i],'target_word':target[int(mapping[i])]} for i in range(w['k'])];digest=hashlib.sha256(canonical(mapping_rows)).hexdigest();item={'model':'WORD_NOMENCLATOR','k':w['k'],'language':w['language'],'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_null_bits':total-null_total,'gap_vs_global_null_bits':total-global_null['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);decoders.append(item|{'mapping':mapping_rows})
    best=min(screen+rows[-2:],key=lambda x:x['total_bits']);same=[x for x in rows if x['model']=='WORD_NOMENCLATOR' and x['k']==w['k'] and x['language']==w['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_matched_null_bits']<0 else 'STOP')+'_WORD_NOMENCLATOR_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_WORD_NOMENCLATOR_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'screen_winner':{'k':w['k'],'language':w['language']},'best':best,'rows':rows,'claim_ceiling':'Exploratory whole-group codebook only; target words are model assignments, not confirmed readings or meanings.'};(ROOT/'gdt001_word_nomenclator_results.json').write_bytes(canonical(result));(ROOT/'gdt001_word_nomenclator_decoders.json').write_bytes(canonical({'schema':'GDT001_WORD_NOMENCLATOR_DECODERS_V1','decoders':decoders}))
    with (ROOT/'gdt001_word_nomenclator_results.tsv').open('w',newline='',encoding='utf-8') as h:wri=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
    print(json.dumps({'decision':decision,'best_k':best['k'],'best_language':best['language'],'best_bps':best['bits_per_symbol'],'matched_gap_bits':best['gap_vs_matched_null_bits'],'global_gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
