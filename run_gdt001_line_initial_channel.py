#!/usr/bin/env python3
"""Literal physical-line-initial language channel with a matched source control."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict

import numpy as np

from gdt001_core import LETTERS, ROOT, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, sha256_file, universal_uint_bits
from gdt001_language_models import PACK_NAMES, train_pack
from run_gdt001_online_context_mixer import PREDICTORS, probability
from run_gdt001_source_selected_nulls import encoded


SEEDS=(64101,64102,64103); ORDER=2; SHARE=1/64; RARE=frozenset('juz')


def selected_paths(lines):
    with (ROOT/'candidates/nonsemantic_ngram_o2/segmentation.tsv').open() as handle:
        rows=list(__import__('csv').DictReader(handle,delimiter='\t'))
    if len(rows)!=len(lines):raise ValueError('segmentation length')
    output=[]
    for line,row in zip(lines,rows):
        if row['locus']!=line.locus:raise ValueError(f"segmentation locus {line.locus}")
        output.append(next(path for path in line.paths if path.path_id==row['selected_path_id']))
    return output


def numeric_order(lines,paths):
    rows=[]
    for line,path in zip(lines,paths):
        if line.grammar_scope != 'CONFIRMED_PROSE':continue
        prefix,suffix=line.locus.rsplit('.',1)
        if not suffix.isdigit() or prefix.casefold()!=line.page.casefold():raise ValueError(f"non-numeric physical-line locus {line.locus}")
        # The frozen lattice contains a few physical rows with no modeled
        # source signs.  They have no literal initial and are outside this
        # channel, while remaining in the separately coded source corpus.
        if not path.source_line:continue
        if path.source_line[0]==' ':raise ValueError(f"space initial {line.locus}")
        rows.append((line.page,int(suffix),line,path))
    return sorted(rows,key=lambda row:(row[0],row[1],row[2].locus))


def initial_sequences(ordered):
    by_page=defaultdict(list)
    for page,_,_,path in ordered:by_page[page].append(LETTERS.index(path.source_line[0]))
    return [by_page[page] for page in sorted(by_page)]


def body_mixer(lines,paths):
    sequences,_,_,active,_,side=encoded(paths,RARE);alphabet=len(active)+1;bos=alphabet;shared=defaultdict(Counter);longer=defaultdict(Counter)
    metadata={name:defaultdict(Counter) for name,_ in PREDICTORS[1:]};weights={};payload=0.
    for line,path,sequence in zip(lines,paths,sequences):
        history=[bos,bos,bos]
        for position,token in enumerate(sequence):
            context=tuple(history[-2:]);counters=[shared[context],longer[(context,history[-3])]]
            for name,field in PREDICTORS[1:]:counters.append(metadata[name][(context,getattr(line,field) or '_')])
            probs=[probability(counter,token,alphabet) for counter in counters];current=weights.setdefault(context,[1/len(counters)]*len(counters));mixture=sum(w*p for w,p in zip(current,probs))
            # The literal first sign is decoded by the separate channel but is
            # known before the body, so it updates the causal experts for free.
            if not (position==0 and line.grammar_scope=='CONFIRMED_PROSE' and path.source_line):payload-=math.log2(mixture)
            posterior=[w*p/mixture for w,p in zip(current,probs)];weights[context]=[(1-SHARE)*value+SHARE/len(counters) for value in posterior]
            for counter in counters:counter[token]+=1
            history=history[1:]+[token]
    return payload,side


def sufficient(page_sequences):
    events=Counter();counts=np.zeros(25,dtype=np.int64)
    for sequence in page_sequences:
        history=[25,25]
        for token in sequence:events[tuple(history)+(token,)]+=1;counts[token]+=1;history=history[1:]+[token]
    return np.asarray(list(events),dtype=np.int64),np.asarray(list(events.values()),dtype=np.float64),counts


def mapping_score(lm,keys,freq,counts,mapping):
    extended=np.concatenate([mapping,[27]]);target=extended[keys];bits=float(np.sum(lm.costs[tuple(target[:,i] for i in range(3))]*freq));groups=defaultdict(list)
    for source,value in enumerate(mapping):groups[int(value)].append(int(counts[source]))
    return bits+sum(categorical_bits(group) for group in groups.values())


def search(language,page_sequences,seed):
    lm=train_pack(language,ORDER);keys,freq,counts=sufficient(page_sequences);rng=np.random.default_rng(seed);mapping=rng.integers(0,27,size=25,dtype=np.int64);score=mapping_score(lm,keys,freq,counts,mapping);passes=0
    while passes<20:
        changed=False
        for source in rng.permutation(25):
            best=(score,int(mapping[source]));original=int(mapping[source])
            for target in range(27):
                if target==original:continue
                trial=mapping.copy();trial[source]=target;value=mapping_score(lm,keys,freq,counts,trial)
                if (value,target)<best:best=(value,target)
            if best[1]!=original:mapping[source]=best[1];score=best[0];changed=True
        passes+=1
        if not changed:break
    rows=[{'source':LETTERS[i],'target':' ' if value==26 else chr(97+int(value)),'occurrences':int(counts[i])} for i,value in enumerate(mapping)]
    return score,rows,hashlib.sha256(canonical(rows)).hexdigest(),passes


def main():
    _,lines=load_lattice();paths=selected_paths(lines);ordered=numeric_order(lines,paths);page_sequences=initial_sequences(ordered);fixed=sum(fixed_costs(paths).values());body,side=body_mixer(lines,paths);symbols=sum(len(w) for p in paths for w in p.words);raw_leader=float(json.loads((ROOT/'gdt001_online_context_mixer_results.json').read_text())['best']['total_bits']);leader=raw_leader+1
    rare_key=universal_uint_bits(len(RARE))+math.log2(math.comb(len(LETTERS),len(RARE)))
    body_key=3+rare_key+math.log2(2)+math.log2(6)
    shared_channel_key=1+universal_uint_bits(ORDER)+math.log2(7)
    anonymous_initial=kt_ngram_bits(page_sequences,25,ORDER);anonymous_key=shared_channel_key;anonymous_total=fixed+side+body_key+body+anonymous_key+anonymous_initial
    rows=[]
    for language in PACK_NAMES:
        for seed in SEEDS:
            payload,mapping,digest,passes=search(language,page_sequences,seed);language_key=shared_channel_key+math.log2(len(SEEDS))+25*math.log2(27);total=fixed+side+body_key+body+language_key+payload
            supported=[item for item in mapping if item['occurrences']]
            decoder={'schema':'GDT001_LINE_INITIAL_LANGUAGE_DECODER_V1','language_pack':language,'language_model_order':ORDER,'mapping':mapping,'scope':'first modeled sign of each nonempty CONFIRMED_PROSE physical line','serialization':'numeric physical-line suffix within page; page reset','body_channel':'juz-rare causal seven-expert source mixer; decoded initial updates experts before remaining line events'}
            rows.append({'language':language,'order':ORDER,'seed':seed,'total_bits':total,'bits_per_symbol':total/symbols,'gap_vs_matched_anonymous_bits':total-anonymous_total,'gap_vs_global_leader_bits':total-leader,'key_bits':body_key+language_key,'rare_side_bits':side,'body_bits':body,'initial_payload_and_reverse_bits':payload,'fixed_bits':fixed,'coordinate_passes':passes,'mapping_hash':digest,'supported_mapping_hash':hashlib.sha256(canonical(supported)).hexdigest(),'decoder_hash':hashlib.sha256(canonical(decoder)).hexdigest(),'decoder':decoder,'mapping':mapping,'cpu_exact_retained_mapping_score':True})
    best=min(rows,key=lambda row:(row['total_bits'],row['language'],row['seed']));same=[r for r in rows if r['language']==best['language']];stable=len({r['supported_mapping_hash'] for r in same})==1
    supported_indices=[i for i,item in enumerate(same[0]['mapping']) if item['occurrences']]
    agreements=[]
    for left in range(len(same)):
        for right in range(left+1,len(same)):
            a=[same[left]['mapping'][i]['target'] for i in supported_indices];b=[same[right]['mapping'][i]['target'] for i in supported_indices]
            agreements.append(sum(x==y for x,y in zip(a,b))/len(a))
    decision='STOP_LINE_INITIAL_LANGUAGE_CHANNEL' if best['total_bits']>=leader or best['total_bits']>=anonymous_total or not stable else 'CONTINUE_LINE_INITIAL_LANGUAGE_CHANNEL'
    stream=[{'locus':line.locus,'source_initial':path.source_line[0]} for _,_,line,path in ordered]
    result={'schema':'GDT001_LINE_INITIAL_CHANNEL_V1','status':'EXPLORATORY_NOT_CONFIRMED_TRANSLATION','decision':decision,'scope':'exact first modeled source sign per nonempty CONFIRMED_PROSE physical line; numeric top-to-bottom order within page; page reset','search_scope':'six frozen historical packs at order 2; three deterministic coordinate-descent starts per pack; exact CPU rescoring of each retained mapping, not exact global key optimization','accounting':'complete corpus code conditional on the frozen lattice: selected prose initials are decoded first; the rare-sign context mixer then codes every other active event while causally updating from those already decoded initials; its rare side channel is paid unchanged; a common seven-way selector chooses anonymous or one of six language channels, and a three-way selector is paid for a retained language restart; comparison to the raw global winner adds one outer family-selector bit to that winner','initial_stream_sha256':hashlib.sha256(canonical(stream)).hexdigest(),'selected_path_digest':hashlib.sha256(canonical([p.path_id for p in paths])).hexdigest(),'inputs':{name:sha256_file(ROOT/name) for name in ('gdt001_corpus_lattice.json','gdt001_language_pack_manifest.json','candidates/nonsemantic_ngram_o2/segmentation.tsv','gdt001_online_context_mixer_results.json')},'implementation':sha256_file(ROOT/'run_gdt001_line_initial_channel.py'),'counts':{'lattice_physical_lines':len(lines),'confirmed_prose_initials':len(ordered),'excluded_other_or_empty_lines':len(lines)-len(ordered),'pages':len(page_sequences),'initial_events':sum(map(len,page_sequences)),'supported_initial_signs':len(supported_indices)},'body':{'model':'frozen-structure juz-rare seven-expert source mixer at fixed share 1/64 in canonical lattice order; selected prose initials update but are not charged','bits':body,'rare_side_bits':side,'key_bits':body_key},'matched_anonymous':{'order':ORDER,'initial_bits':anonymous_initial,'key_bits':anonymous_key,'total_bits':anonymous_total},'raw_global_leader_bits':raw_leader,'selector_adjusted_global_leader_bits':leader,'best':best,'rows':rows,'stable_best_language_mapping':stable,'best_language_pairwise_supported_mapping_agreement':agreements,'claim_ceiling':'Exploratory literal confirmed-prose line-initial channel only; no acrostic, letter, word, language, plaintext, meaning, or translation is established.'}
    (ROOT/'gdt001_line_initial_channel_results.json').write_bytes(canonical(result));print(json.dumps({'decision':decision,'best_language':best['language'],'best_total_bits':best['total_bits'],'gap_matched':best['gap_vs_matched_anonymous_bits'],'gap_global':best['gap_vs_global_leader_bits'],'stable':stable}))


if __name__=='__main__':main()
