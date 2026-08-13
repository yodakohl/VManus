#!/usr/bin/env python3
"""Fast screens for Currier-conditioned keys and within-group transpositions."""

import csv, hashlib, json, math
from collections import Counter
import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def state_model(lines, paths, scheme):
    labels=[]; sequences=[]
    if scheme == "CURRIER_2":
        labels=[f"{c}:{x}" for c in ("A","B","OTHER") for x in LETTERS]
        categories=np.repeat(np.arange(3),25); counts=np.zeros(75); space=75
        for line,path in zip(lines,paths):
            ci={"A":0,"B":1}.get(line.currier,2); seq=[]
            for wi,word in enumerate(path.words):
                if wi: seq.append(space)
                for x in word:
                    s=ci*25+LETTERS.index(x);seq.append(s);counts[s]+=1
            sequences.append(seq)
        return sequences,counts,categories,labels,space
    transform={
        "REVERSE":lambda w:w[::-1],
        "ROTATE_LEFT":lambda w:w[1:]+w[:1],
        "ODD_EVEN":lambda w:w[::2]+w[1::2],
    }[scheme]
    labels=list(LETTERS);categories=np.zeros(25,dtype=np.int64);counts=np.zeros(25);space=25
    for path in paths:
        seq=[]
        for wi,word in enumerate(path.words):
            if wi:seq.append(space)
            for x in transform(word):
                s=LETTERS.index(x);seq.append(s);counts[s]+=1
        sequences.append(seq)
    return sequences,counts,categories,labels,space


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);lm=train_pack("middle_high_german",2)
    fixed=sum(fixed_costs(paths).values());symbols=sum(c!=' ' for p in paths for c in p.source_line)
    null=json.loads((ROOT/".gdt001/runs/nonsemantic_ngram_o2.json").read_text());rows=[];maps=[]
    # One screen per transposition, then two extra restarts only for its winner.
    screened=[]
    for scheme in ("REVERSE","ROTATE_LEFT","ODD_EVEN"):
        bits,mapping,digest=search_encoded(*state_model(lines,paths,scheme),lm,4101)
        screened.append((bits,scheme,mapping,digest))
    winner=min(screened)[1]
    jobs=[(scheme,4101,bits,mapping,digest) for bits,scheme,mapping,digest in screened]
    for seed in (4102,4103):
        bits,mapping,digest=search_encoded(*state_model(lines,paths,winner),lm,seed);jobs.append((winner,seed,bits,mapping,digest))
    for seed in (4201,4202,4203):
        bits,mapping,digest=search_encoded(*state_model(lines,paths,"CURRIER_2"),lm,seed);jobs.append(("CURRIER_2",seed,bits,mapping,digest))
    for scheme,seed,bits,mapping,digest in jobs:
        genes=75 if scheme=="CURRIER_2" else 25
        key=3+math.log2(6)+math.log2(4)+genes*math.log2(27)+universal_uint_bits(2)
        total=key+bits+fixed
        rows.append({"scheme":scheme,"seed":seed,"total_bits":total,"bits_per_symbol":total/symbols,"gap_vs_null_bits":total-null["total_bits"],"key_bits":key,"modeled_bits":bits,"fixed_bits":fixed,"decoder_hash":digest,"cpu_exact":True})
        maps.append({"scheme":scheme,"seed":seed,"decoder_hash":digest,"mapping":mapping})
    best=min(rows,key=lambda x:x["total_bits"]);same=[r for r in rows if r["scheme"]==best["scheme"]]
    stable=len(same)==3 and len({r["decoder_hash"] for r in same})==1
    decision=("CONTINUE" if best["gap_vs_null_bits"]<0 else "STOP")+"_KEY_VARIANTS_"+("STABLE" if stable else "UNSTABLE")
    result={"schema":"GDT001_KEY_VARIANTS_V1","status":"EXPLORATORY_NOT_CONFIRMED_TRANSLATION","decision":decision,"transposition_screen_winner":winner,"best":best,"null_bits_per_symbol":null["bits_per_symbol"],"rows":rows,"claim_ceiling":"Exploratory key/transposition screen only; no language or plaintext claim."}
    (ROOT/"gdt001_key_variant_results.json").write_bytes(canonical(result));(ROOT/"gdt001_key_variant_mappings.json").write_bytes(canonical({"schema":"GDT001_KEY_VARIANT_MAPPINGS_V1","mappings":maps}))
    with (ROOT/"gdt001_key_variant_results.tsv").open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
    print(json.dumps({"decision":decision,"best_scheme":best["scheme"],"best_bps":best["bits_per_symbol"],"null_bps":null["bits_per_symbol"],"gap_bits":best["gap_vs_null_bits"]}))


if __name__=="__main__":main()
