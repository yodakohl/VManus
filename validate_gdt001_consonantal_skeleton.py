#!/usr/bin/env python3
"""Independent Python reconstruction of the consonantal-skeleton screen."""

from __future__ import annotations

import csv
import hashlib
import heapq
import json
import math
from collections import Counter, defaultdict

import numpy as np

from gdt001_core import LETTERS, ROOT, TARGET_ALPHABET, canonical, categorical_bits, fixed_costs, load_lattice, sha256_file, universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_code_high_order import dense_costs, lm

ORDER=2; VOWELS="aeiou"; CONSONANTS="bcdfghjklmnpqrstvwxyz"; EPSILON=tuple(TARGET_ALPHABET.index(c) for c in VOWELS+" "); BOS=27


def epsilon_closure(costs, start, initial=False):
    distance=np.full(784,np.inf); origin=start[0]*28+start[1];distance[origin]=0.;queue=[(0.,origin)]
    while queue:
        value,node=heapq.heappop(queue)
        if value!=distance[node]:continue
        left,right=divmod(node,28)
        for emitted in EPSILON:
            if emitted==26 and (right==26 or (initial and node==origin)):continue
            target=right*28+emitted;candidate=value+float(costs[left,right,emitted])
            if candidate<distance[target]-1e-12:distance[target]=candidate;heapq.heappush(queue,(candidate,target))
    return distance


def tables(costs):
    ids=[TARGET_ALPHABET.index(c) for c in CONSONANTS];starts=np.full((21,28),np.inf);first=epsilon_closure(costs,(BOS,BOS),True)
    for d,required in enumerate(ids):
        for node,value in enumerate(first):
            left,right=divmod(node,28);starts[d,right]=min(starts[d,right],value+float(costs[left,right,required]))
    transitions=np.full((21,21,28,28),np.inf);terminals=np.full((21,28),np.inf)
    for c,current in enumerate(ids):
        for previous in range(28):
            distance=epsilon_closure(costs,(previous,current));terminals[c,previous]=min(v for n,v in enumerate(distance) if n%28!=26)
            for d,required in enumerate(ids):
                for node,value in enumerate(distance):
                    left,right=divmod(node,28);transitions[c,d,previous,right]=min(transitions[c,d,previous,right],value+float(costs[left,right,required]))
    return starts,transitions,terminals


def python_score(sequences,mapping,starts,transitions,terminals):
    total=0.
    for sequence in sequences:
        if not sequence:continue
        previous=int(mapping[sequence[0]]);state=starts[previous].copy()
        for token in sequence[1:]:
            target=int(mapping[token]);state=np.min(state[:,None]+transitions[previous,target],axis=0);previous=target
        total+=float(np.min(state+terminals[previous]))
    return total


def main():
    result=json.loads((ROOT/'gdt001_consonantal_skeleton_results.json').read_text());checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    need(result['schema']=='GDT001_CONSONANTAL_SKELETON_V1','schema');need(result['decision']=='STOP_PROJECTED_KEY_DIAGNOSTIC_LOSES_NO_FAMILY_INFERENCE','decision')
    need([r['language'] for r in result['rows']]==list(PACK_NAMES),'languages')
    need(result['implementation']=={n:sha256_file(ROOT/n) for n in ('run_gdt001_consonantal_skeleton.py','gdt001_skeleton_score.cpp')},'implementation')
    need(result['projected_key_source']=={'artifact':'gdt001_latent_space_homophonic_results.json','sha256':sha256_file(ROOT/'gdt001_latent_space_homophonic_results.json'),'selection':'same language, order 2 screen mapping'},'key_provenance')
    need(result['inputs']=={name:sha256_file(ROOT/name) for name in ('gdt001_corpus_lattice.json','gdt001_language_pack_manifest.json','gdt001_latent_space_homophonic_results.json')},'input_hashes')
    screen=json.loads((ROOT/'gdt001_latent_space_homophonic_results.json').read_text())['screen'];_,lines=load_lattice();paths=common_selected_paths(lines)
    sequences=[];counts=np.zeros(25,dtype=np.int64)
    for path in paths:
        sequence=[LETTERS.index(c) for word in path.words for c in word];sequences.append(sequence)
        for token in sequence:counts[token]+=1
    fixed=sum(fixed_costs(paths).values());totals=[]
    for stored in result['rows']:
        direct=next(r['mapping'] for r in screen if r['language']==stored['language'] and r['order']==ORDER);projected=[]
        for value in direct:
            position=int(value)
            while chr(97+position%26) not in CONSONANTS:position+=1
            projected.append(CONSONANTS.index(chr(97+position%26)))
        mapping_rows=[{'source':LETTERS[i],'required_consonant':CONSONANTS[value],'occurrences':int(counts[i])} for i,value in enumerate(projected)]
        need(stored['mapping']==mapping_rows,f"{stored['language']}:mapping");need(stored['mapping_hash']==hashlib.sha256(canonical(mapping_rows)).hexdigest(),f"{stored['language']}:mapping_hash")
        starts,transitions,terminals=tables(dense_costs(lm(stored['language'],ORDER),ORDER));language_bits=python_score(sequences,np.asarray(projected),starts,transitions,terminals)
        groups=defaultdict(list)
        for source,target in enumerate(projected):groups[target].append(int(counts[source]))
        reverse=sum(categorical_bits(group) for group in groups.values());key=3+math.log2(6)+universal_uint_bits(2)+25*math.log2(21);total=fixed+key+language_bits+reverse
        for field,value in (('fixed_bits',fixed),('key_bits',key),('language_bits',language_bits),('reverse_bits',reverse),('total_bits',total)):need(abs(float(stored[field])-value)<1e-7,f"{stored['language']}:{field}")
        totals.append(total)
    best_index=int(np.argmin(totals));need(result['best']==result['rows'][best_index],'best');need(totals[best_index]>result['current_source_leader_bits'],'early_stop')
    with (ROOT/'GDT001_YOLO_LEDGER.tsv').open() as handle:ledger=list(csv.DictReader(handle,delimiter='\t'))
    registered=[r for r in ledger if r['run_id'].startswith('skeleton_screen_')];need(len(registered)==6,'ledger_count')
    for stored in result['rows']:
        row=next(r for r in registered if r['run_id']==f"skeleton_screen_{stored['language']}_o2")
        need(abs(float(row['total_bits'])-stored['total_bits'])<1e-5,f"{stored['language']}:ledger_total");need(row['decoder_hash']==stored['mapping_hash'],f"{stored['language']}:ledger_hash")
    output={'schema':'GDT001_CONSONANTAL_SKELETON_VALIDATION_V2','status':'PASS_INDEPENDENT_PYTHON_PROJECTED_KEY_DIAGNOSTIC','check_count':len(checks),'checks':checks,'result_sha256':sha256_file(ROOT/'gdt001_consonantal_skeleton_results.json'),'best_total_bits':totals[best_index],'claim_ceiling':'Independent arithmetic, Python DP, provenance, and ledger validation of one projected-key diagnostic only; no inference about unsearched keys, language, plaintext, meaning, or translation.'}
    (ROOT/'gdt001_consonantal_skeleton_validation.json').write_bytes(canonical(output));print(json.dumps({'status':output['status'],'checks':len(checks),'best_total_bits':totals[best_index]}))


if __name__=='__main__':main()
