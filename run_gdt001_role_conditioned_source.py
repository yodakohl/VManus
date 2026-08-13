#!/usr/bin/env python3
"""Line-record source grammar with sole/entry/body/exit emissions."""

import csv,hashlib,json,math
from collections import Counter
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths

ROLES=('SOLE','ENTRY','BODY','EXIT')


def role(i,n):
    return 'SOLE' if n==1 else 'ENTRY' if i==0 else 'EXIT' if i==n-1 else 'BODY'


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);source=json.load(open(ROOT/'gdt001_source_selected_null_results.json'))['selected_source_null'];rows=[];decoders=[]
    seq={r:[] for r in ROLES};role_counts=Counter();length_counts={r:Counter() for r in ROLES};line_word_counts=Counter()
    for p in paths:
        n=len(p.words);line_word_counts[n]+=1
        for i,w in enumerate(p.words):
            r=role(i,n);role_counts[r]+=1;length_counts[r][len(w)]+=1;seq[r].append(tuple(LETTERS.index(c) for c in w))
    max_words=max(line_word_counts);structure_bits=universal_uint_bits(max_words)+categorical_bits([line_word_counts[i] for i in range(1,max_words+1)])
    for r in ROLES:
        max_length=max(length_counts[r],default=0);structure_bits+=universal_uint_bits(max_length)+categorical_bits([length_counts[r][i] for i in range(1,max_length+1)])
    for shared in (True,False):
        for order in range(6):
            if shared:
                payload=kt_ngram_bits(sum((seq[r] for r in ROLES),[]),25,order);contexts=1
            else:payload=sum(kt_ngram_bits(seq[r],25,order) for r in ROLES);contexts=4
            key=3+1+universal_uint_bits(order)+universal_uint_bits(contexts);total=key+structure_bits+payload+fixed;decoder={'roles':ROLES,'role_counts':dict(role_counts),'shared_character_process':shared,'order':order,'line_program':'SOLE or ENTRY + BODY* + EXIT','line_word_counts':dict(sorted(line_word_counts.items())),'word_length_counts':{r:dict(sorted(length_counts[r].items())) for r in ROLES}};digest=hashlib.sha256(canonical(decoder)).hexdigest();rows.append({'shared_process':shared,'order':order,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_source_winner_bits':total-source['total_bits'],'key_bits':key,'structure_bits':structure_bits,'payload_bits':payload,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});decoders.append(decoder|{'decoder_hash':digest})
    best=min(rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best['gap_vs_source_winner_bits']<0 else 'STOP')+'_ROLE_CONDITIONED_SOURCE'
    result={'schema':'GDT001_ROLE_CONDITIONED_SOURCE_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','theory_origin':'CODEX_SELF_ORIGINATED','decision':decision,'best':best,'rows':rows,'claim_ceiling':'Exploratory source record grammar; roles are structural positions, not syntax, POS, meanings, or plaintext.'};(ROOT/'gdt001_role_conditioned_source_results.json').write_bytes(canonical(result));(ROOT/'gdt001_role_conditioned_source_decoders.json').write_bytes(canonical({'schema':'GDT001_ROLE_CONDITIONED_SOURCE_DECODERS_V1','decoders':decoders}))
    with (ROOT/'gdt001_role_conditioned_source_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'shared':best['shared_process'],'order':best['order'],'best_bps':best['bits_per_symbol'],'old_source_bps':source['bits_per_symbol'],'gain_bits':-best['gap_vs_source_winner_bits']}))


if __name__=='__main__':main()
