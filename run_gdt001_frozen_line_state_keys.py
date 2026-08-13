#!/usr/bin/env python3
"""Frozen anonymous line states conditioning one or two homophonic keys."""

import hashlib
import json
import math

import numpy as np

from gdt001_core import LETTERS, ROOT, canonical, categorical_bits, fixed_costs, load_lattice, sha256_file, universal_uint_bits
from gdt001_language_models import train_pack
from run_gdt001_contextual_language import scores_cpu
from run_gdt001_source_selected_nulls import encoded


LANGUAGE="middle_high_german"; ORDER=2; SEEDS=(65101,65102,65103); RARE=frozenset("juz")


def selected_paths(lines):
    import csv
    rows=list(csv.DictReader(open(ROOT/'candidates/nonsemantic_ngram_o2/segmentation.tsv'),delimiter='\t'))
    if len(rows)!=len(lines):raise ValueError('segmentation length')
    return [next(p for p in line.paths if p.path_id==row['selected_path_id']) for line,row in zip(lines,rows)]


def frozen_states(lines):
    result=json.load(open(ROOT/'gdt001_latent_line_state_results.json'));assign=json.load(open(ROOT/'gdt001_latent_line_state_assignments.json'))
    best=result['best'];run=next(x for x in assign['runs'] if x['requested_k']==best['requested_k'] and x['seed']==best['seed'])
    if run['decoder_hash']!=best['decoder_hash'] or len(run['assignments'])!=len(lines):raise ValueError('state binding')
    return [int(x) for x in run['assignments']],best


def state_encoded(paths,states,k):
    seqs,_,_,active,space,_=encoded(paths,RARE);genes=len(active)*k;counts=np.zeros(genes);cats=np.repeat(np.arange(k),len(active));labels=[f"STATE_{s}:{c}" for s in range(k) for c in active];out=[]
    for seq,state in zip(seqs,states):
        row=[]
        for token in seq:
            if token==space:row.append(genes)
            else:index=state*len(active)+token;row.append(index);counts[index]+=1
        out.append(row)
    return out,counts,cats,labels,genes


def search(data,lm,seed,initial=None):
    sequences,counts,categories,labels,fixed_space=data;rng=np.random.default_rng(seed);mapping=(rng.integers(0,26,size=len(labels),dtype=np.int64) if initial is None else np.asarray(initial,dtype=np.int64).copy());score=float(scores_cpu(lm,sequences,mapping[None,:],counts,categories,fixed_space)[0]);passes=0
    while passes<20:
        changed=False
        for source in rng.permutation(len(labels)):
            trials=np.repeat(mapping[None,:],26,axis=0);trials[:,source]=np.arange(26);values=scores_cpu(lm,sequences,trials,counts,categories,fixed_space);target=int(np.argmin(values))
            if values[target]<score-1e-10:mapping[source]=target;score=float(values[target]);changed=True
        passes+=1
        if not changed:break
    rows=[{'source_state':label,'target':chr(97+int(value)),'occurrences':int(counts[i])} for i,(label,value) in enumerate(zip(labels,mapping))]
    return score,rows,hashlib.sha256(canonical(rows)).hexdigest(),passes


def main():
    _,lines=load_lattice();paths=selected_paths(lines);states,state_source=frozen_states(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);_,_,_,active,_,side=encoded(paths,RARE);state_bits=state_source['state_assignment_bits'];original_state_selector=math.log2(8);state_key=state_source['key_bits']+original_state_selector;lm=train_pack(LANGUAGE,ORDER);leader=json.load(open(ROOT/'gdt001_online_context_mixer_results.json'))['best']['total_bits']+1;matched=state_source['total_bits']+original_state_selector;rows=[]
    k1_starts={}
    for k in (1,2):
        used=[0]*len(states) if k==1 else states;data=state_encoded(paths,used,k);genes=len(active)*k
        for seed in SEEDS:
            initial=None if k==1 else np.tile(k1_starts[seed],2)
            bits,mapping,digest,passes=search(data,lm,seed,initial);numeric=np.asarray([ord(item['target'])-97 for item in mapping],dtype=np.int64)
            if k==1:k1_starts[seed]=numeric
            overlay_key=1+math.log2(6)+math.log2(2)+math.log2(len(SEEDS))+genes*math.log2(26);key=state_key+overlay_key;total=fixed+side+state_bits+key+bits;decoder={'schema':'GDT001_FROZEN_LINE_STATE_KEYS_DECODER_V1','language_pack':LANGUAGE,'order':ORDER,'key_count':k,'frozen_state_decoder_hash':state_source['decoder_hash'],'mapping':mapping,'rare_symbols':'juz','manual_boundaries':'fixed target SPACE; source signs emit letters a-z only'};rows.append({'key_count':k,'seed':seed,'initialization':'RANDOM' if k==1 else 'DUPLICATED_SAME_SEED_K1_MAP','total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_leader_bits':total-float(leader),'gap_vs_matched_anonymous_bits':total-matched,'fixed_bits':fixed,'rare_side_bits':side,'frozen_state_bits':state_bits,'original_state_restart_selector_bits':original_state_selector,'frozen_state_key_bits':state_key,'overlay_key_bits':overlay_key,'key_bits':key,'language_and_reverse_bits':bits,'coordinate_passes':passes,'mapping_hash':digest,'decoder_hash':hashlib.sha256(canonical(decoder)).hexdigest(),'decoder':decoder,'mapping':mapping,'cpu_exact_retained_mapping_score':True})
    best=min(rows,key=lambda x:(x['total_bits'],x['key_count'],x['seed']));k1=min(r['total_bits'] for r in rows if r['key_count']==1);k2=min(r['total_bits'] for r in rows if r['key_count']==2);same=[r for r in rows if r['key_count']==best['key_count']];stable=len({r['mapping_hash'] for r in same})==1;decision='STOP_FROZEN_LINE_STATE_KEYS' if best['total_bits']>=float(leader) or k2>=k1 or not stable else 'CONTINUE_FROZEN_LINE_STATE_KEYS'
    output={'schema':'GDT001_FROZEN_LINE_STATE_KEYS_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'scope':'one versus two explicit homophonic keys conditioned by frozen anonymous latentline_k2_s28104 line states; Middle High German order 2 only','search_scope':'three deterministic coordinate-descent starts for each key count; exact CPU rescoring of retained maps, not exact global key optimization','inputs':{name:sha256_file(ROOT/name) for name in ('gdt001_corpus_lattice.json','gdt001_language_pack_manifest.json','gdt001_latent_line_state_results.json','gdt001_latent_line_state_assignments.json','candidates/nonsemantic_ngram_o2/segmentation.tsv','gdt001_online_context_mixer_results.json')},'implementation':sha256_file(ROOT/'run_gdt001_frozen_line_state_keys.py'),'state_counts':{str(x):states.count(x) for x in sorted(set(states))},'matched_anonymous_frozen_state_bits':matched,'global_leader_bits':float(leader),'best_k1_bits':k1,'best_k2_bits':k2,'two_key_gain_bits':k1-k2,'stable_best_mapping':stable,'best':best,'rows':rows,'claim_ceiling':'Bounded frozen-state switching-key screen only; no general state-conditioned decoder, state, key, letter, word, language, plaintext, meaning, or translation is established.'};(ROOT/'gdt001_frozen_line_state_keys_results.json').write_bytes(canonical(output));print(json.dumps({'decision':decision,'best':(best['key_count'],best['seed'],best['total_bits']),'k2_gain':k1-k2,'gap_matched':best['gap_vs_matched_anonymous_bits'],'gap_leader':best['gap_vs_global_leader_bits'],'stable':stable}))


if __name__=='__main__':main()
