#!/usr/bin/env python3
"""Differentiable multi-restart proposals plus exact discrete key refinement."""

import csv,hashlib,json,math
import numpy as np
from gdt001_core import ROOT,LETTERS,canonical,fixed_costs,load_lattice,universal_uint_bits
from gdt001_language_models import PACK_NAMES,cpu_population_scores,gpu_population_scores,source_ngram_counts,train_pack
from gdt001_scaffold_payload import common_selected_paths


def proposals(lm,paths,seed,restarts=32,steps=80):
    import torch
    torch.manual_seed(seed);keys_np,freq_np=source_ngram_counts(paths,2);keys=torch.as_tensor(keys_np,device='cuda');freq=torch.as_tensor(freq_np,device='cuda',dtype=torch.float32);cost=torch.as_tensor(lm.costs,device='cuda',dtype=torch.float32);logits=torch.randn((restarts,25,26),device='cuda')*.1;logits.requires_grad_();opt=torch.optim.Adam([logits],lr=.16)
    for step in range(steps):
        temp=1.5*(.08/1.5)**(step/(steps-1));p=torch.softmax(logits/temp,dim=-1);fixed=torch.zeros((restarts,2,28),device='cuda');fixed[:,0,26]=1;fixed[:,1,27]=1;pext=torch.cat([torch.nn.functional.pad(p,(0,2)),fixed],1);loss=torch.zeros(restarts,device='cuda')
        for st in range(0,len(keys),128):
            q=keys[st:st+128];f=freq[st:st+128];a=pext[:,q[:,0],:];b=pext[:,q[:,1],:];c=pext[:,q[:,2],:27];tmp=torch.einsum('rma,abc->rmbc',a,cost);v=(tmp*b.unsqueeze(-1)).sum(2);loss+=((v*c).sum(-1)*f).sum(1)
        entropy=-(p*torch.log2(p+1e-9)).sum((1,2));objective=(loss+.03*entropy).sum();opt.zero_grad();objective.backward();opt.step()
    return logits.detach().argmax(-1).cpu().numpy()


def refine(lm,paths,maps,sweeps=6):
    scores=gpu_population_scores(lm,paths,maps,True);order=np.argsort(scores)[:8];best=[]
    for m in maps[order].copy():
        current=m.copy();current_score=float(gpu_population_scores(lm,paths,current[None],True)[0])
        for _ in range(sweeps):
            variants=[]
            for pos in range(25):
                block=np.repeat(current[None],26,axis=0);block[:,pos]=np.arange(26);variants.append(block)
            variants=np.vstack(variants);s=gpu_population_scores(lm,paths,variants,True);i=int(np.argmin(s))
            if s[i]>=current_score-1e-9:break
            current=variants[i].copy();current_score=float(s[i])
        best.append(current)
    candidates=np.asarray(best);scores=cpu_population_scores(lm,paths,candidates,True);i=int(np.argmin(scores));return candidates[i],float(scores[i])


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);null=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));rows=[];maps=[]
    key=3+math.log2(6)+universal_uint_bits(2)+25*math.log2(26)
    winner=None
    for li,language in enumerate(PACK_NAMES):
        lm=train_pack(language,2)
        for seed in (15101,):
            proposed=proposals(lm,paths,seed+100*li);mapping,bits=refine(lm,paths,proposed);total=key+bits+fixed;mapping_rows=[{'source':LETTERS[i],'target':chr(97+int(x))} for i,x in enumerate(mapping)];digest=hashlib.sha256(canonical(mapping_rows)).hexdigest();item={'language':language,'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True};rows.append(item);maps.append({'language':language,'seed':seed,'decoder_hash':digest,'mapping':mapping_rows})
    winner=min(rows,key=lambda x:x['total_bits'])['language'];lm=train_pack(winner,2);li=PACK_NAMES.index(winner)
    for seed in (15102,15103):
        proposed=proposals(lm,paths,seed+100*li);mapping,bits=refine(lm,paths,proposed);total=key+bits+fixed;mapping_rows=[{'source':LETTERS[i],'target':chr(97+int(x))} for i,x in enumerate(mapping)];digest=hashlib.sha256(canonical(mapping_rows)).hexdigest();rows.append({'language':winner,'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_null_bits':total-null['total_bits'],'key_bits':key,'modeled_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});maps.append({'language':winner,'seed':seed,'decoder_hash':digest,'mapping':mapping_rows})
    best=min(rows,key=lambda x:x['total_bits']);same=[x for x in rows if x['language']==best['language']];stable=len({x['decoder_hash'] for x in same})==1;decision=('CONTINUE' if best['gap_vs_null_bits']<0 else 'STOP')+'_DIFFERENTIABLE_KEYS_'+('STABLE' if stable else 'UNSTABLE')
    result={'schema':'GDT001_DIFFERENTIABLE_KEYS_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'optimizer':{'proposal':'32 parallel differentiable restarts, annealed softmax','finish':'8 exact discrete coordinate descents, CPU final score'},'best':best,'rows':rows,'claim_ceiling':'Exploratory optimizer audit for explicit homophonic keys; no language or plaintext claim.'};(ROOT/'gdt001_differentiable_key_results.json').write_bytes(canonical(result));(ROOT/'gdt001_differentiable_key_mappings.json').write_bytes(canonical({'schema':'GDT001_DIFFERENTIABLE_KEY_MAPPINGS_V1','mappings':maps}))
    with (ROOT/'gdt001_differentiable_key_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_language':best['language'],'best_bps':best['bits_per_symbol'],'null_bps':null['bits_per_symbol'],'gap_bits':best['gap_vs_null_bits']}))


if __name__=='__main__':main()
