#!/usr/bin/env python3
"""Exact reversible line-entry/word-slot record grammar."""

import csv, hashlib, json, math
from collections import Counter,defaultdict
from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


def pos(i,n):
    if n==1:return 'SOLE'
    if i==0:return 'INITIAL'
    if i==n-1:return 'FINAL'
    return 'MEDIAL'


def score(paths,model):
    line_counts=Counter();lengths=defaultdict(Counter);chars=defaultdict(Counter);prev='<BOS>'
    for p in paths:
        line_counts[len(p.words)]+=1
        for wi,w in enumerate(p.words):
            role='ENTRY' if wi==0 else 'BODY';lengths[role if model in ('ROLE','ROLE_BIGRAM') else 'ALL'][len(w)]+=1
            prev='<BOS>'
            for i,c in enumerate(w):
                context=[]
                if model in ('ROLE','ROLE_BIGRAM'):context.append(role)
                context.append(pos(i,len(w)))
                if model in ('POS_BIGRAM','ROLE_BIGRAM'):context.append(prev)
                chars[tuple(context)][c]+=1;prev=c
    bits=categorical_bits([line_counts[k] for k in sorted(line_counts)])
    bits+=sum(categorical_bits([v[k] for k in sorted(v)]) for v in lengths.values())
    bits+=sum(categorical_bits([v.get(c,0) for c in LETTERS]) for v in chars.values())
    decoder={'model':model,'line_group_count_counts':dict(sorted(line_counts.items())),'length_contexts':{str(k):dict(sorted(v.items())) for k,v in lengths.items()},'character_context_count':len(chars),'reconstruction':'line group count + per-role lengths + exact character slot emissions'}
    return bits,decoder


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];decoders=[]
    for model in ('POS','ROLE','POS_BIGRAM','ROLE_BIGRAM'):
        payload,decoder=score(paths,model);key=3+math.log2(4)+universal_uint_bits(len(decoder['length_contexts']))+universal_uint_bits(decoder['character_context_count']);total=key+payload+fixed;digest=hashlib.sha256(canonical(decoder)).hexdigest();rows.append({'model':model,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_bits':payload,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});decoders.append(decoder|{'decoder_hash':digest})
    best=min(rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best['gap_vs_global_null_bits']<0 else 'STOP')+'_SLOT_GRAMMAR'
    result={'schema':'GDT001_SLOT_GRAMMAR_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','theory_origin':'CODEX_SELF_ORIGINATED','decision':decision,'best':best,'rows':rows,'claim_ceiling':'Exploratory formal record-slot grammar only; no field meaning, language, or plaintext claim.'};(ROOT/'gdt001_slot_grammar_results.json').write_bytes(canonical(result));(ROOT/'gdt001_slot_grammar_decoders.json').write_bytes(canonical({'schema':'GDT001_SLOT_GRAMMAR_DECODERS_V1','decoders':decoders}))
    with (ROOT/'gdt001_slot_grammar_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_model':best['model'],'best_bps':best['bits_per_symbol'],'null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
