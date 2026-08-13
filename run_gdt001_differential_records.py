#!/usr/bin/env python3
"""Reversible adjacent-group edit-record grammar with learned opcode tables."""

import csv,hashlib,json,math
from collections import Counter,defaultdict
from gdt001_core import ROOT,LETTERS,canonical,categorical_bits,fixed_costs,levenshtein_program,load_lattice,universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


def parse(program):
    out=[]
    for raw in program.split():
        op=raw[:raw.index('(')]
        payload=raw[raw.index('(')+1:-1]
        out.append((op,payload))
    return out


def main():
    _,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words);base=json.loads((ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json').read_text());rows=[];decoders=[]
    for scope in ('LINE','PAGE'):
        ops=Counter();ins=Counter();subs=Counter();literal_chars=Counter();modes=Counter();programs=[];page_prior={}
        for line,p in zip(lines,paths):
            prior='' if scope=='LINE' else page_prior.get(line.page,'')
            rec=[]
            for w in p.words:
                literal=1+universal_uint_bits(len(w))+len(w)*math.log2(25)
                _,program=levenshtein_program(prior,w);parsed=parse(program);rough=1+universal_uint_bits(len(parsed))+len(parsed)*2+sum(math.log2(25) for op,_ in parsed if op in ('INS','SUB'))
                if not prior or literal<=rough:
                    modes['LITERAL']+=1;literal_chars.update(w);rec.append({'word':w,'mode':'LITERAL'});prior=w
                else:
                    modes['EDIT']+=1
                    for op,payload in parsed:
                        ops[op]+=1
                        if op=='INS':ins[payload]+=1
                        elif op=='SUB':subs[payload.split('>')[1]]+=1
                    rec.append({'word':w,'mode':'EDIT','source':prior,'program':program});prior=w
            if scope=='PAGE':page_prior[line.page]=prior
            programs.append({'locus':line.locus,'words':rec})
        bits=categorical_bits([modes[x] for x in ('LITERAL','EDIT')])+categorical_bits([ops[x] for x in ('KEEP','SUB','DEL','INS')])
        bits+=categorical_bits([literal_chars.get(c,0) for c in LETTERS])+categorical_bits([ins.get(c,0) for c in LETTERS])+categorical_bits([subs.get(c,0) for c in LETTERS])
        bits+=sum(universal_uint_bits(len(w['program'].split())) for l in programs for w in l['words'] if w['mode']=='EDIT')
        bits+=sum(universal_uint_bits(len(w['word'])) for l in programs for w in l['words'] if w['mode']=='LITERAL')
        key=3+1+universal_uint_bits(4);total=key+bits+fixed;decoder={'scope':scope,'modes':dict(modes),'opcodes':dict(ops),'insert_counts':dict(ins),'substitute_target_counts':dict(subs),'line_programs':programs};digest=hashlib.sha256(canonical(decoder)).hexdigest();rows.append({'scope':scope,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_global_null_bits':total-base['total_bits'],'key_bits':key,'payload_bits':bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True});decoders.append(decoder|{'decoder_hash':digest})
    best=min(rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best['gap_vs_global_null_bits']<0 else 'STOP')+'_DIFFERENTIAL_RECORDS'
    result={'schema':'GDT001_DIFFERENTIAL_RECORDS_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','theory_origin':'CODEX_SELF_ORIGINATED','decision':decision,'best':best,'rows':rows,'claim_ceiling':'Exploratory formal edit-record code only; no semantics, language, plaintext, or copying chronology claim.'};(ROOT/'gdt001_differential_record_results.json').write_bytes(canonical(result));(ROOT/'gdt001_differential_record_decoders.json').write_bytes(canonical({'schema':'GDT001_DIFFERENTIAL_RECORD_DECODERS_V1','decoders':decoders}))
    with (ROOT/'gdt001_differential_record_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_scope':best['scope'],'best_bps':best['bits_per_symbol'],'null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_global_null_bits']}))


if __name__=='__main__':main()
