#!/usr/bin/env python3
"""Fast boundary-free and position-allographic language tests."""

from __future__ import annotations

import csv, hashlib, json, math
from collections import Counter
import numpy as np

from gdt001_core import ROOT, SOURCE_ALPHABET, TARGET_ALPHABET, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import TARGET_BOS, train_pack
from gdt001_scaffold_payload import common_selected_paths


def encoded(paths, scheme):
    sequences=[]; counts=None; categories=None; labels=None; fixed_space=None
    if scheme == "BOUNDARY_FREE":
        labels=list(SOURCE_ALPHABET); categories=np.zeros(26,dtype=np.int64); counts=np.zeros(26); fixed_space=None
        for p in paths:
            seq=[SOURCE_ALPHABET.index(c) for c in p.source_line]; sequences.append(seq)
            for x in seq: counts[x]+=1
    else:
        labels=[f"{cls}:{c}" for cls in ("INITIAL","MEDIAL","FINAL") for c in SOURCE_ALPHABET[:-1]]
        categories=np.repeat(np.arange(3),25); counts=np.zeros(75); fixed_space=75
        for p in paths:
            seq=[]
            for wi,word in enumerate(p.words):
                if wi: seq.append(fixed_space)
                for i,c in enumerate(word):
                    cls=0 if i==0 else 2 if i==len(word)-1 else 1
                    state=cls*25+SOURCE_ALPHABET[:-1].index(c);seq.append(state);counts[state]+=1
            sequences.append(seq)
    return sequences,counts,categories,labels,fixed_space


def sufficient(sequences,bos):
    c=Counter()
    for seq in sequences:
        h=[bos,bos]
        for x in seq:c[tuple(h)+(x,)]+=1;h=[h[1],x]
    return np.asarray(list(c),np.int64),np.asarray(list(c.values()),np.float64)


def scores_gpu(lm,sequences,maps,counts,categories,fixed_space):
    import torch
    genes=maps.shape[1];bos=genes+(1 if fixed_space is not None else 0)
    keys_np,freq_np=sufficient(sequences,bos);keys=torch.as_tensor(keys_np,device='cuda');freq=torch.as_tensor(freq_np,device='cuda',dtype=torch.float64);cost=torch.as_tensor(lm.costs,device='cuda',dtype=torch.float64)
    scount=torch.as_tensor(counts,device='cuda',dtype=torch.float64);cat=torch.as_tensor(categories,device='cuda');out=[];buckets=(int(categories.max())+1)*27
    for start in range(0,len(maps),512):
        m=torch.as_tensor(maps[start:start+512],device='cuda');n=len(m)
        tail=[26,27] if fixed_space is not None else [27]
        ext=torch.cat([m,torch.tensor(tail,device='cuda').repeat(n,1)],1)
        idx=[ext[:,keys[:,i]] for i in range(3)];v=(cost[tuple(idx)]*freq).sum(1)
        bucket=cat.unsqueeze(0)*27+m;mult=torch.zeros((n,buckets),device='cuda',dtype=torch.float64);tot=torch.zeros_like(mult);member=torch.zeros_like(mult)
        mult.scatter_add_(1,bucket,torch.ones_like(bucket,dtype=torch.float64));tot.scatter_add_(1,bucket,scount.expand(n,-1));const=torch.lgamma(scount+.5)-torch.lgamma(torch.tensor(.5,device='cuda',dtype=torch.float64));member.scatter_add_(1,bucket,const.expand(n,-1))
        logp=torch.lgamma(.5*mult)-torch.lgamma(tot+.5*mult)+member;v+=torch.where(mult>0,-logp/math.log(2),0).sum(1);out.append(v.cpu().numpy())
    return np.concatenate(out)


def scores_cpu(lm,sequences,maps,counts,categories,fixed_space):
    genes=maps.shape[1];bos=genes+(1 if fixed_space is not None else 0);keys,freq=sufficient(sequences,bos);out=[]
    for m in maps:
        ext=np.concatenate([m,[26,27] if fixed_space is not None else [27]]);target=ext[keys];bits=float(np.sum(lm.costs[tuple(target[:,i] for i in range(3))]*freq))
        groups={}
        for i,t in enumerate(m):groups.setdefault((int(categories[i]),int(t)),[]).append(i)
        for ids in groups.values():
            total=sum(counts[i] for i in ids);k=len(ids);logp=math.lgamma(.5*k)-math.lgamma(total+.5*k)+sum(math.lgamma(counts[i]+.5)-math.lgamma(.5) for i in ids);bits-=logp/math.log(2)
        out.append(bits)
    return np.asarray(out)


def search_encoded(sequences,counts,categories,labels,fixed_space,lm,seed):
    rng=np.random.default_rng(seed);pop=rng.integers(0,27,size=(32768,len(labels)),dtype=np.int64)
    for _ in range(30):
        s=scores_gpu(lm,sequences,pop,counts,categories,fixed_space);elite=pop[np.argsort(s)[:128]].copy();children=elite[rng.integers(0,128,len(pop)-128)].copy();rows=np.arange(len(children));pos=rng.integers(0,len(labels),len(children));children[rows,pos]=rng.integers(0,27,len(children));pop=np.vstack([elite,children])
    s=scores_gpu(lm,sequences,pop,counts,categories,fixed_space);i=int(np.argmin(s));cpu=float(scores_cpu(lm,sequences,pop[i:i+1],counts,categories,fixed_space)[0]);assert abs(cpu-s[i])<2e-6
    mapping=[{"source_state":label,"target":" " if value==26 else chr(97+int(value)),"occurrences":int(counts[j])} for j,(label,value) in enumerate(zip(labels,pop[i]))]
    return cpu,mapping,hashlib.sha256(canonical(mapping)).hexdigest()


def search(paths,lm,scheme,seed):
    return search_encoded(*encoded(paths,scheme),lm,seed)


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);lm=train_pack('middle_high_german',2);fixed=sum(fixed_costs(paths).values());symbols=sum(c!=' ' for p in paths for c in p.source_line);null=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];maps=[]
    for scheme in ('BOUNDARY_FREE','POSITIONAL_3'):
        genes=26 if scheme=='BOUNDARY_FREE' else 75;key=math.log2(2)+math.log2(6)+genes*math.log2(27)+universal_uint_bits(2)
        for seed in (3101,3102,3103):
            bits,mapping,digest=search(paths,lm,scheme,seed);total=3+key+bits+fixed;rows.append({'scheme':scheme,'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'decoder_hash':digest,'cpu_exact':True});maps.append({'scheme':scheme,'seed':seed,'decoder_hash':digest,'mapping':mapping})
    best=min(rows,key=lambda r:r['total_bits']);stable=all(len({r['decoder_hash'] for r in rows if r['scheme']==s})==1 for s in ('BOUNDARY_FREE','POSITIONAL_3'));decision='STOP_CONTEXTUAL_LANGUAGE_LOSES' if best['total_bits']>=null['total_bits'] else 'CONTINUE_CONTEXTUAL_LANGUAGE';decision+=('_KEYS_UNSTABLE' if not stable else '_KEYS_STABLE')
    result={'schema':'GDT001_CONTEXTUAL_LANGUAGE_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'null_bits_per_symbol':null['bits_per_symbol'],'best':best,'keys_stable':stable,'rows':rows,'claim_ceiling':'Exploratory context/boundary decoder test only; no language or plaintext claim.'};(ROOT/'gdt001_contextual_language_results.json').write_bytes(canonical(result));(ROOT/'gdt001_contextual_language_mappings.json').write_bytes(canonical({'schema':'GDT001_CONTEXTUAL_LANGUAGE_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_contextual_language_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_scheme':best['scheme'],'best_bps':best['bits_per_symbol'],'null_bps':null['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
