#!/usr/bin/env python3
"""Reversible anonymous-unit MDL screen, followed by one matched language test."""

import csv, hashlib, json, math
from collections import Counter
import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded


def learn(paths, maximum=256):
    words=[[LETTERS.index(c) for c in word] for path in paths for word in path.words]
    expansions={i:LETTERS[i] for i in range(25)}; rules=[]; snapshots={0:([x[:] for x in words],dict(expansions),rules[:])}
    wanted={8,16,32,64,128,256}
    for step in range(1,maximum+1):
        counts=Counter((w[i],w[i+1]) for w in words for i in range(len(w)-1))
        if not counts:break
        pair,count=min(counts.items(),key=lambda x:(-x[1],x[0]));new=25+len(rules)
        rewritten=[]
        for w in words:
            out=[];i=0
            while i<len(w):
                if i+1<len(w) and (w[i],w[i+1])==pair:out.append(new);i+=2
                else:out.append(w[i]);i+=1
            rewritten.append(out)
        words=rewritten;expansions[new]=expansions[pair[0]]+expansions[pair[1]]
        rules.append({"token":new,"left":pair[0],"right":pair[1],"expansion":expansions[new],"training_occurrences":count})
        if step in wanted:snapshots[step]=([x[:] for x in words],dict(expansions),rules[:])
    return snapshots


def line_sequences(paths, flat_words, token_count):
    it=iter(flat_words);seqs=[];space=token_count
    for path in paths:
        seq=[]
        for wi in range(len(path.words)):
            if wi:seq.append(space)
            seq.extend(next(it))
        seqs.append(seq)
    return seqs


def rule_bits(k):
    # Each ordered merge names two symbols from the then-current vocabulary.
    return universal_uint_bits(k)+sum(2*math.log2(25+i) for i in range(k))


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values())
    symbols=sum(c!=' ' for p in paths for c in p.source_line);snapshots=learn(paths);rows=[];models=[]
    for k,(words,expansions,rules) in sorted(snapshots.items()):
        seqs=line_sequences(paths,words,25+k);payload=kt_ngram_bits(seqs,26+k,2);key=3+universal_uint_bits(2)+rule_bits(k);total=key+payload+fixed
        row={"model":"BPE_NULL","merges":k,"seed":0,"total_bits":total,"bits_per_symbol":total/symbols,"key_bits":key,"payload_bits":payload,"fixed_bits":fixed,"decoder_hash":hashlib.sha256(canonical(rules)).hexdigest(),"cpu_exact":True};rows.append(row)
        models.append({"merges":k,"rules":rules,"token_count":25+k})
    best_null=min((r for r in rows if r["model"]=="BPE_NULL"),key=lambda r:r["total_bits"]);k=best_null["merges"]
    words,expansions,rules=snapshots[k];seqs=line_sequences(paths,words,25+k);counts=np.zeros(25+k)
    for s in seqs:
        for x in s:
            if x<25+k:counts[x]+=1
    categories=np.zeros(25+k,dtype=np.int64);labels=[expansions[i] for i in range(25+k)];lm=train_pack("middle_high_german",2)
    language_maps=[]
    for seed in (5101,5102,5103):
        bits,mapping,digest=search_encoded(seqs,counts,categories,labels,25+k,lm,seed)
        key=3+math.log2(6)+universal_uint_bits(2)+rule_bits(k)+(25+k)*math.log2(27);total=key+bits+fixed
        rows.append({"model":"BPE_MHG","merges":k,"seed":seed,"total_bits":total,"bits_per_symbol":total/symbols,"key_bits":key,"payload_bits":bits,"fixed_bits":fixed,"decoder_hash":digest,"cpu_exact":True});language_maps.append({"seed":seed,"decoder_hash":digest,"mapping":mapping})
    best_lang=min((r for r in rows if r["model"]=="BPE_MHG"),key=lambda r:r["total_bits"])
    decision="CONTINUE_BPE_NOTATION" if best_null["merges"] and best_null["total_bits"]<rows[0]["total_bits"] else "STOP_BPE_NOTATION"
    if best_lang["total_bits"]<best_null["total_bits"]:decision+="_LANGUAGE_ADVANTAGE"
    else:decision+="_ANONYMOUS_NULL_WINS"
    result={"schema":"GDT001_BPE_NOTATION_V1","status":"EXPLORATORY_NOT_CONFIRMED_TRANSLATION","decision":decision,"character_null":rows[0],"best_anonymous":best_null,"best_language":best_lang,"rows":rows,"claim_ceiling":"Exploratory reversible anonymous-unit grammar; units have no meanings, sounds, or established glyph status."}
    (ROOT/"gdt001_bpe_notation_results.json").write_bytes(canonical(result));(ROOT/"gdt001_bpe_notation_codebook.json").write_bytes(canonical({"schema":"GDT001_BPE_CODEBOOK_V1","models":models,"language_mapping":language_maps}))
    with (ROOT/"gdt001_bpe_notation_results.tsv").open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
    print(json.dumps({"decision":decision,"best_merges":k,"bpe_bps":best_null["bits_per_symbol"],"language_bps":best_lang["bits_per_symbol"],"char_bps":rows[0]["bits_per_symbol"]}))


if __name__=="__main__":main()
