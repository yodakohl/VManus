#!/usr/bin/env python3
"""Exact reversible carrier/payload channel splits proposed by Codex."""

import csv, hashlib, json, math
from gdt001_core import ROOT, SOURCE_ALPHABET, canonical, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


def split_word(word,scheme):
    if scheme=='ODD_EVEN':return (word[::2],word[1::2])
    if scheme=='EDGE_CORE':return (word[:1]+word[-1:] if len(word)>1 else word,word[1:-1])
    if scheme=='INITIAL_INTERNAL_FINAL':return (word[:1],word[1:-1],word[-1:] if len(word)>1 else '')
    raise ValueError(scheme)


def channels(paths,scheme):
    n=3 if scheme=='INITIAL_INTERNAL_FINAL' else 2;out=[[] for _ in range(n)]
    for p in paths:
        parts=[[] for _ in range(n)]
        for w in p.words:
            values=split_word(w,scheme)
            for i,value in enumerate(values):parts[i].append(value)
        for i in range(n):
            text=' '.join(parts[i]);out[i].append(tuple(SOURCE_ALPHABET.index(c) for c in text))
    return out


def reconstructable(paths,scheme):
    for p in paths:
        for w in p.words:
            x=split_word(w,scheme)
            if scheme=='ODD_EVEN':r=''.join(a+b for a,b in zip(x[0],x[1]))+(x[0][-1:] if len(x[0])>len(x[1]) else '')
            elif scheme=='EDGE_CORE':r=x[0][:1]+x[1]+x[0][1:]
            else:r=x[0]+x[1]+x[2]
            if r!=w:raise AssertionError((scheme,w,x,r))


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[]
    for scheme in ('ODD_EVEN','EDGE_CORE','INITIAL_INTERNAL_FINAL'):
        reconstructable(paths,scheme)
        for order in (0,1,2,3):
            streams=channels(paths,scheme);payload=sum(kt_ngram_bits(s,len(SOURCE_ALPHABET),order) for s in streams);key=3+math.log2(3)+universal_uint_bits(order);total=key+payload+fixed;decoder={'scheme':scheme,'order':order,'channels':len(streams),'reconstruction':'deterministic per-word inverse'}
            rows.append({'scheme':scheme,'order':order,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_bits':payload,'fixed_bits':fixed,'decoder_hash':hashlib.sha256(canonical(decoder)).hexdigest(),'cpu_exact':True})
    best=min(rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best['gap_vs_global_null_bits']<0 else 'STOP')+'_INTERLEAVED_CHANNELS'
    result={'schema':'GDT001_INTERLEAVED_CHANNELS_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','theory_origin':'CODEX_SELF_ORIGINATED','decision':decision,'best':best,'rows':rows,'claim_ceiling':'Exploratory reversible formal channel split; no payload meaning, sound, language, or plaintext claim.'};(ROOT/'gdt001_interleaved_channel_results.json').write_bytes(canonical(result))
    with (ROOT/'gdt001_interleaved_channel_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_scheme':best['scheme'],'best_order':best['order'],'best_bps':best['bits_per_symbol'],'null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
