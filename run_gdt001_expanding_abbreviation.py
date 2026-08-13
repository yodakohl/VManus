#!/usr/bin/env python3
"""Explicit one-or-two-letter emission transducer with exact CPU/GPU MDL."""

import csv, hashlib, json, math
from collections import Counter
import numpy as np

from gdt001_core import ROOT, LETTERS, SOURCE_ALPHABET, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import train_pack
from gdt001_scaffold_payload import common_selected_paths

CODE_COUNT=26+26*26


def sufficient(paths):
    c=Counter();counts=np.zeros(25)
    for p in paths:
        h=[26,26]
        for x in p.source_ids:
            c[tuple(h)+(x,)]+=1;h=[h[1],x]
            if x<25:counts[x]+=1
    return np.asarray(list(c),np.int64),np.asarray(list(c.values()),np.float64),counts


def decode(code):
    return (code,) if code<26 else ((code-26)//26,(code-26)%26)


def cpu(lm,keys,freq,counts,maps):
    out=[]
    for m in maps:
        bits=0.
        for (a,b,c),n in zip(keys,freq):
            def emit(x): return (27,) if x==26 else (26,) if x==25 else decode(int(m[x]))
            ea,eb,ec=emit(a),emit(b),emit(c);hist=(ea+eb)[-2:]
            bits+=n*lm.costs[hist[0],hist[1],ec[0]]
            if len(ec)==2:bits+=n*lm.costs[hist[1],ec[0],ec[1]]
        groups={}
        for s,t in enumerate(m):groups.setdefault(int(t),[]).append(s)
        bits+=sum(categorical_bits([int(counts[s]) for s in ss]) for ss in groups.values())
        bits+=categorical_bits([int(sum(counts[s] for s,t in enumerate(m) if t<26)),int(sum(counts[s] for s,t in enumerate(m) if t>=26))])
        out.append(bits)
    return np.asarray(out)


def gpu(lm,keys_np,freq_np,counts_np,maps):
    import torch
    keys=torch.as_tensor(keys_np,device='cuda');freq=torch.as_tensor(freq_np,device='cuda',dtype=torch.float64);cost=torch.as_tensor(lm.costs,device='cuda',dtype=torch.float64);counts=torch.as_tensor(counts_np,device='cuda',dtype=torch.float64);outs=[]
    for st in range(0,len(maps),512):
        m=torch.as_tensor(maps[st:st+512],device='cuda');n=len(m)
        ext=torch.cat([m,torch.full((n,1),-1,device='cuda'),torch.full((n,1),-2,device='cuda')],1)
        codes=[ext[:,keys[:,i]] for i in range(3)]
        def parts(x):
            special_space=x==-1;special_bos=x==-2;two=x>=26
            first=torch.where(special_space,26,torch.where(special_bos,27,torch.where(two,(x-26)//26,x)))
            second=torch.where(two,(x-26)%26,first)
            return first,second,two
        af,asec,at=parts(codes[0]);bf,bsec,bt=parts(codes[1]);cf,csec,ct=parts(codes[2]);h1=torch.where(bt,bsec,bf);h0=torch.where(bt,bf,torch.where(at,asec,af))
        v=(cost[h0,h1,cf]*freq).sum(1)+(cost[h1,cf,csec]*freq*ct).sum(1)
        mult=torch.zeros((n,CODE_COUNT),device='cuda',dtype=torch.float64);tot=torch.zeros_like(mult);mem=torch.zeros_like(mult);mult.scatter_add_(1,m,torch.ones_like(m,dtype=torch.float64));tot.scatter_add_(1,m,counts.expand(n,-1));const=torch.lgamma(counts+.5)-torch.lgamma(torch.tensor(.5,device='cuda',dtype=torch.float64));mem.scatter_add_(1,m,const.expand(n,-1));lp=torch.lgamma(.5*mult)-torch.lgamma(tot+.5*mult)+mem;v+=torch.where(mult>0,-lp/math.log(2),0).sum(1)
        n2=((m>=26)*counts).sum(1);n1=counts.sum()-n2;v+=(-torch.lgamma(torch.tensor(1.,device='cuda'))+torch.lgamma(n1+n2+1.)-torch.lgamma(n1+.5)-torch.lgamma(n2+.5)+2*torch.lgamma(torch.tensor(.5,device='cuda')))/math.log(2)
        outs.append(v.cpu().numpy())
    return np.concatenate(outs)


def search(lm,keys,freq,counts,seed):
    rng=np.random.default_rng(seed);pop=rng.integers(0,CODE_COUNT,size=(32768,25),dtype=np.int64)
    for _ in range(35):
        s=gpu(lm,keys,freq,counts,pop);elite=pop[np.argsort(s)[:128]].copy();ch=elite[rng.integers(0,128,len(pop)-128)].copy();r=np.arange(len(ch));p=rng.integers(0,25,len(ch));ch[r,p]=rng.integers(0,CODE_COUNT,len(ch));pop=np.vstack([elite,ch])
    s=gpu(lm,keys,freq,counts,pop);i=int(np.argmin(s));exact=float(cpu(lm,keys,freq,counts,pop[i:i+1])[0]);assert abs(exact-s[i])<2e-6
    rows=[]
    for j,code in enumerate(pop[i]):rows.append({'source':LETTERS[j],'plaintext':''.join(chr(97+x) for x in decode(int(code))),'occurrences':int(counts[j])})
    return exact,rows,hashlib.sha256(canonical(rows)).hexdigest()


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);keys,freq,counts=sufficient(paths);lm=train_pack('middle_high_german',2);fixed=sum(fixed_costs(paths).values());symbols=int(counts.sum());null=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];maps=[]
    key=3+math.log2(6)+universal_uint_bits(2)+25*math.log2(CODE_COUNT)
    for seed in (6101,6102,6103):
        bits,mapping,digest=search(lm,keys,freq,counts,seed);total=key+bits+fixed;rows.append({'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'key_bits':key,'latent_reverse_length_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});maps.append({'seed':seed,'decoder_hash':digest,'mapping':mapping})
    best=min(rows,key=lambda x:x['total_bits']);stable=len({x['decoder_hash'] for x in rows})==1;decision=('CONTINUE' if best['gap_vs_null_bits']<0 else 'STOP')+'_EXPANDING_ABBREVIATION_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_EXPANDING_ABBREVIATION_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'best':best,'null_bits_per_symbol':null['bits_per_symbol'],'rows':rows,'claim_ceiling':'Exploratory explicit one-or-two-letter transducer only; no language or plaintext claim.'};(ROOT/'gdt001_expanding_abbreviation_results.json').write_bytes(canonical(result));(ROOT/'gdt001_expanding_abbreviation_mappings.json').write_bytes(canonical({'schema':'GDT001_EXPANDING_ABBREVIATION_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_expanding_abbreviation_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_bps':best['bits_per_symbol'],'null_bps':null['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
