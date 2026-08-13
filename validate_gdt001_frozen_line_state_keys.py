#!/usr/bin/env python3
"""Independent CPU reconstruction of the frozen-line-state key screen."""

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict

from gdt001_core import LETTERS, ROOT, canonical, categorical_bits, fixed_costs, load_lattice, sha256_file
from gdt001_language_models import train_pack
from run_gdt001_source_selected_nulls import encoded


RARE=frozenset('juz'); ORDER=2; SEEDS=(65101,65102,65103)


def selected_paths(lines):
    rows=list(csv.DictReader(open(ROOT/'candidates/nonsemantic_ngram_o2/segmentation.tsv'),delimiter='\t'))
    if len(rows)!=len(lines):raise AssertionError('segmentation length')
    output=[]
    for line,row in zip(lines,rows):
        if row['locus']!=line.locus:raise AssertionError('segmentation locus')
        output.append(next(path for path in line.paths if path.path_id==row['selected_path_id']))
    return output


def state_source(lines):
    result=json.load(open(ROOT/'gdt001_latent_line_state_results.json'));assign=json.load(open(ROOT/'gdt001_latent_line_state_assignments.json'));best=result['best'];run=next(x for x in assign['runs'] if x['requested_k']==best['requested_k'] and x['seed']==best['seed'])
    if run['decoder_hash']!=best['decoder_hash'] or len(run['assignments'])!=len(lines):raise AssertionError('state source')
    return [int(x) for x in run['assignments']],best


def statistics(paths,states,k):
    sequences,_,_,active,space,side=encoded(paths,RARE);genes=len(active)*k;counts=[0]*genes;categories=[i//len(active) for i in range(genes)];events=Counter()
    for sequence,state in zip(sequences,states):
        history=[genes+1,genes+1]
        for token in sequence:
            source=genes if token==space else state*len(active)+token
            if source<genes:counts[source]+=1
            events[tuple(history)+(source,)]+=1;history=history[1:]+[source]
    labels=[f'STATE_{state}:{char}' for state in range(k) for char in active]
    return events,counts,categories,labels,side


def score(lm,events,counts,categories,mapping):
    extended=[*mapping,26,27];total=0.
    for key,frequency in events.items():
        mapped=tuple(extended[x] for x in key);total+=float(lm.costs[mapped])*frequency
    groups=defaultdict(list)
    for source,target in enumerate(mapping):groups[(categories[source],target)].append(counts[source])
    return total+sum(categorical_bits(group) for group in groups.values())


def main():
    result=json.load(open(ROOT/'gdt001_frozen_line_state_keys_results.json'));checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    need(result['schema']=='GDT001_FROZEN_LINE_STATE_KEYS_V1','schema');need(result['status']=='EXPLORATORY_NOT_CONFIRMED_TRANSLATION','status');need(result['decision']=='STOP_FROZEN_LINE_STATE_KEYS','decision')
    need(result['implementation']==sha256_file(ROOT/'run_gdt001_frozen_line_state_keys.py'),'implementation')
    need(result['inputs']=={name:sha256_file(ROOT/name) for name in result['inputs']},'inputs')
    _,lines=load_lattice();paths=selected_paths(lines);states,parent=state_source(lines);need(result['state_counts']=={'0':2482,'1':2904},'state_counts')
    fixed=sum(fixed_costs(paths).values());matched=parent['total_bits']+math.log2(8);need(abs(result['matched_anonymous_frozen_state_bits']-matched)<1e-9,'matched')
    leader=json.load(open(ROOT/'gdt001_online_context_mixer_results.json'))['best']['total_bits']+1;need(abs(result['global_leader_bits']-leader)<1e-9,'leader')
    lm=train_pack('middle_high_german',ORDER);totals=[]
    need([(r['key_count'],r['seed']) for r in result['rows']]==[(k,s) for k in (1,2) for s in SEEDS],'row_order')
    for row in result['rows']:
        k=row['key_count'];used=[0]*len(states) if k==1 else states;events,counts,categories,labels,side=statistics(paths,used,k);mapping_rows=row['mapping'];need(row['initialization']==('RANDOM' if k==1 else 'DUPLICATED_SAME_SEED_K1_MAP'),f"{k}:{row['seed']}:initialization");need([x['source_state'] for x in mapping_rows]==labels,f"{k}:{row['seed']}:labels");need([x['occurrences'] for x in mapping_rows]==counts,f"{k}:{row['seed']}:counts");mapping=[ord(x['target'])-97 for x in mapping_rows];need(all(0<=x<26 for x in mapping),f"{k}:{row['seed']}:targets");need(row['mapping_hash']==hashlib.sha256(canonical(mapping_rows)).hexdigest(),f"{k}:{row['seed']}:map_hash")
        expected_decoder={'schema':'GDT001_FROZEN_LINE_STATE_KEYS_DECODER_V1','language_pack':'middle_high_german','order':ORDER,'key_count':k,'frozen_state_decoder_hash':parent['decoder_hash'],'mapping':mapping_rows,'rare_symbols':'juz','manual_boundaries':'fixed target SPACE; source signs emit letters a-z only'};need(row['decoder']==expected_decoder and row['decoder_hash']==hashlib.sha256(canonical(expected_decoder)).hexdigest(),f"{k}:{row['seed']}:decoder")
        language=score(lm,events,counts,categories,mapping);state_key=parent['key_bits']+math.log2(8);overlay=1+math.log2(6)+math.log2(2)+math.log2(3)+len(mapping)*math.log2(26);key=state_key+overlay;total=fixed+side+parent['state_assignment_bits']+key+language
        for field,value in (('fixed_bits',fixed),('rare_side_bits',side),('frozen_state_bits',parent['state_assignment_bits']),('frozen_state_key_bits',state_key),('overlay_key_bits',overlay),('key_bits',key),('language_and_reverse_bits',language),('total_bits',total),('gap_vs_matched_anonymous_bits',total-matched),('gap_vs_global_leader_bits',total-leader)):need(abs(float(row[field])-value)<1e-7,f"{k}:{row['seed']}:{field}")
        for source in range(len(mapping)):
            for target in range(26):
                trial=mapping.copy();trial[source]=target;need(score(lm,events,counts,categories,trial)>=language-1e-9,f"{k}:{row['seed']}:local:{source}:{target}")
        totals.append(total)
    # Every K2 run starts from the duplicated same-seed K1 map; independently
    # verify that its retained language/reverse score never exceeds that nested state.
    for k2row in [r for r in result['rows'] if r['key_count']==2]:
        k1row=next(r for r in result['rows'] if r['key_count']==1 and r['seed']==k2row['seed']);events,counts,categories,_,_=statistics(paths,states,2);base=[ord(x['target'])-97 for x in k1row['mapping']]*2;need(k2row['language_and_reverse_bits']<=score(lm,events,counts,categories,base)+1e-8,f"nested:{k2row['seed']}")
    best_index=min(range(len(totals)),key=lambda i:(totals[i],result['rows'][i]['key_count'],result['rows'][i]['seed']));need(result['best']==result['rows'][best_index],'best');k1=min(t for t,r in zip(totals,result['rows']) if r['key_count']==1);k2=min(t for t,r in zip(totals,result['rows']) if r['key_count']==2);need(abs(result['best_k1_bits']-k1)<1e-8 and abs(result['best_k2_bits']-k2)<1e-8 and abs(result['two_key_gain_bits']-(k1-k2))<1e-8 and k2<k1,'key_comparison');same=[r for r in result['rows'] if r['key_count']==result['best']['key_count']];need(result['stable_best_mapping']==(len({r['mapping_hash'] for r in same})==1)==False,'instability');need(result['best']['total_bits']>matched>leader,'stop')
    with open(ROOT/'GDT001_YOLO_LEDGER.tsv') as handle:ledger=list(csv.DictReader(handle,delimiter='\t'))
    registered=[x for x in ledger if x['run_id'].startswith('frozenlinekey_')];need(len(registered)==6,'ledger_count')
    for row in result['rows']:
        stored=next(x for x in registered if x['run_id']==f"frozenlinekey_k{row['key_count']}_s{row['seed']}");need(abs(float(stored['total_bits'])-row['total_bits'])<1e-5,f"ledger:{row['key_count']}:{row['seed']}:total");need(stored['decoder_hash']==row['decoder_hash'],f"ledger:{row['key_count']}:{row['seed']}:hash")
    output={'schema':'GDT001_FROZEN_LINE_STATE_KEYS_VALIDATION_V1','status':'PASS_INDEPENDENT_CPU_EXACT_STOP','check_count':len(checks),'checks':checks,'result_sha256':sha256_file(ROOT/'gdt001_frozen_line_state_keys_results.json'),'best_total_bits':result['best']['total_bits'],'claim_ceiling':'Independent score/local-optimum/state/input/ledger validation only; no state, key, language, plaintext, meaning, or translation.'};(ROOT/'gdt001_frozen_line_state_keys_validation.json').write_bytes(canonical(output));print(json.dumps({'status':output['status'],'checks':len(checks),'best':output['best_total_bits']}))


if __name__=='__main__':main()
