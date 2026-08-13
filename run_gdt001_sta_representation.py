#!/usr/bin/env python3
"""Whole-manuscript STA-family/member representation under exact reconstruction."""

import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
from gdt001_core import ROOT,LETTERS,SOURCE_ALPHABET,canonical,categorical_bits,fixed_costs,kt_ngram_bits,load_lattice,universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


def rules():
    out={}
    for raw in (ROOT/'transcription/sources/sta/STA-Eva_def.bit').read_text().splitlines():
        m=re.match(r'^([A-Z][0-9a-z])\s+(.+?)\s*$',raw)
        if m:
            value=m.group(2).replace('{','').replace('}','').replace("'",'')
            out[m.group(1)]=value if set(value)<=set(LETTERS) else None
    return out


def boundary_bits(text):
    compact=text.replace(' ','');n=len(compact);positions=[i for i,c in enumerate(text) if c==' '];k=len(positions)
    return universal_uint_bits(k)+(math.log2(math.comb(max(0,n-1),k)) if k and n>1 else 0.)


def main():
    corpus=json.load(open(ROOT/'gdt001_corpus_lattice.json'));_,lines=load_lattice();paths=common_selected_paths(lines);fixed=sum(fixed_costs(paths).values());base=json.load(open(ROOT/'.gdt001/runs/nonsemantic_ngram_o2.json'));rule=rules();fields={'ZL3b':'zl_sta_codes','IT2a':'it_sta_codes','RF1b':'rf_sta_codes'}
    aligned=[];unaligned=[];family_members=defaultdict(Counter);member_sequences=[];family_sequences=[];boundaries=0.;mismatch=Counter();literal_residual=0.;records=[]
    for line,path,obj in zip(lines,paths,corpus['lines']):
        a=obj['sta_alignment']
        if not a:unaligned.append(path.source_ids);continue
        edition=path.editions[0];members=a[fields[edition]];families=list(a['family_sequence'])
        if len(members)!=len(families) or any(m[0]!=f for m,f in zip(members,families)):raise AssertionError(line.locus)
        for f,m in zip(families,members):family_members[f][m]+=1
        family_sequences.append(families);member_sequences.append(members);boundaries+=boundary_bits(path.source_line)
        generated=''.join(rule.get(m) or '?' for m in members);actual=path.source_line.replace(' ','');ok=generated==actual;mismatch[ok]+=1
        if not ok:literal_residual+=universal_uint_bits(len(actual))+len(actual)*math.log2(25)
        records.append({'locus':line.locus,'edition':edition,'family_sequence':''.join(families),'member_sequence':' '.join(members),'surface_exact_from_members':ok})
    mismatch_bits=categorical_bits([mismatch[True],mismatch[False]])+literal_residual
    member_conditional=sum(categorical_bits([c[m] for m in sorted(c)]) for c in family_members.values())
    unaligned_bits=kt_ngram_bits(unaligned,len(SOURCE_ALPHABET),2);family_vocab=sorted({x for s in family_sequences for x in s});fi={x:i for i,x in enumerate(family_vocab)};family_ids=[[fi[x] for x in s] for s in family_sequences]
    member_vocab=sorted({x for s in member_sequences for x in s});mi={x:i for i,x in enumerate(member_vocab)};member_ids=[[mi[x] for x in s] for s in member_sequences];rows=[]
    for representation in ('FAMILY_PLUS_MEMBER','EXACT_MEMBER'):
        for order in range(0,6):
            if representation=='FAMILY_PLUS_MEMBER':struct=kt_ngram_bits(family_ids,len(family_vocab),order)+member_conditional;vocab=len(family_vocab)
            else:struct=kt_ngram_bits(member_ids,len(member_vocab),order);vocab=len(member_vocab)
            key=3+math.log2(2)+universal_uint_bits(order)+universal_uint_bits(vocab);payload=struct+boundaries+mismatch_bits+unaligned_bits;total=key+payload+fixed;decoder={'representation':representation,'order':order,'vocabulary':family_vocab if representation.startswith('FAMILY') else member_vocab,'aligned_lines':len(aligned) or len(records),'unaligned_lines':len(unaligned),'exact_surface_lines':mismatch[True],'literal_residual_lines':mismatch[False]};digest=hashlib.sha256(canonical(decoder)).hexdigest();rows.append({'representation':representation,'order':order,'total_bits':total,'bits_per_symbol':total/base['source_symbols'],'gap_vs_character_null_bits':total-base['total_bits'],'key_bits':key,'structural_bits':struct,'boundary_bits':boundaries,'surface_residual_bits':mismatch_bits,'unaligned_character_bits':unaligned_bits,'fixed_bits':fixed,'decoder_hash':digest,'cpu_exact':True})
    best=min(rows,key=lambda x:x['total_bits']);decision=('CONTINUE' if best['gap_vs_character_null_bits']<0 else 'STOP')+'_STA_REPRESENTATION'
    result={'schema':'GDT001_STA_REPRESENTATION_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'counts':{'aligned_lines':len(records),'unaligned_lines':len(unaligned),'member_surface_exact':mismatch[True],'member_surface_literal_residual':mismatch[False],'family_vocabulary':len(family_vocab),'member_vocabulary':len(member_vocab)},'best':best,'rows':rows,'claim_ceiling':'Exploratory exact formal representation comparison; STA families/members are not sounds, language units, meanings, or plaintext.'};(ROOT/'gdt001_sta_representation_results.json').write_bytes(canonical(result));(ROOT/'gdt001_sta_representation_decoder.json').write_bytes(canonical({'schema':'GDT001_STA_REPRESENTATION_DECODER_V1','rules_source':'STA-Eva_def.bit','family_member_counts':{f:dict(sorted(c.items())) for f,c in sorted(family_members.items())},'line_records':records}))
    with (ROOT/'gdt001_sta_representation_results.tsv').open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'decision':decision,'best_representation':best['representation'],'best_order':best['order'],'best_bps':best['bits_per_symbol'],'character_null_bps':base['bits_per_symbol'],'gap_bits':best['gap_vs_character_null_bits'],'exact_lines':mismatch[True]}))


if __name__=='__main__':main()
