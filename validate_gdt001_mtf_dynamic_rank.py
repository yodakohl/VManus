#!/usr/bin/env python3
"""Independent pure-Python validation of the retained MTF dynamic-rank screen."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict

from gdt001_core import LETTERS, ROOT, canonical, categorical_bits, fixed_costs, load_lattice, sha256_file, universal_uint_bits
from gdt001_controls import transform
from gdt001_language_models import PACK_NAMES, train_pack


ORDER=2; SEEDS=(67101,67102,67103)


def paths_for(lines):
    rows=list(csv.DictReader(open(ROOT/'candidates/nonsemantic_ngram_o2/segmentation.tsv'),delimiter='\t'))
    if len(rows)!=len(lines):raise AssertionError('segmentation length')
    return [next(path for path in line.paths if path.path_id==row['selected_path_id'] and line.locus==row['locus']) for line,row in zip(lines,rows)]


def parse_rank(decoder):
    rows=decoder['rank_key'];
    if [row['source'] for row in rows]!=list(LETTERS):raise AssertionError('rank key source')
    ranks=[int(row['fixed_rank']) for row in rows]
    if sorted(ranks)!=list(range(25)):raise AssertionError('rank permutation')
    return ranks


def decode(paths,ranks,initial):
    output=[]
    for path in paths:
        state=list(initial);chars=[]
        for char in path.source_line:
            if char==' ':chars.append(' ');continue
            rank=ranks[LETTERS.index(char)];target=state[rank];chars.append(chr(97+target));state.pop(rank);state.insert(0,target)
        output.append(''.join(chars))
    return output


def inverse(decoded,ranks,initial):
    inv={rank:LETTERS[i] for i,rank in enumerate(ranks)};out=[]
    for text in decoded:
        state=list(initial);chars=[]
        for char in text:
            if char==' ':chars.append(' ');continue
            target=ord(char)-97;rank=state.index(target);chars.append(inv[rank]);state.pop(rank);state.insert(0,target)
        out.append(''.join(chars))
    return out


def lm_bits(paths,ranks,initial,language):
    costs=train_pack(language,ORDER).costs;total=0.
    for text in decode(paths,ranks,initial):
        h=[27,27]
        for char in text:
            target=26 if char==' ' else ord(char)-97;total+=float(costs[h[0],h[1],target]);h=[h[1],target]
    return total


def static_bits(paths,mapping,language):
    costs=train_pack(language,ORDER).costs;total=0.
    for path in paths:
        h=[27,27]
        for char in path.source_line:
            target=26 if char==' ' else mapping[LETTERS.index(char)];total+=float(costs[h[0],h[1],target]);h=[h[1],target]
    return total


def kt_bits(paths,ranks):
    contexts=defaultdict(Counter)
    for text in decode(paths,ranks,range(26)):
        h=[26,26]
        for char in text:
            target=25 if char==' ' else ord(char)-97;contexts[tuple(h)][target]+=1;h=[h[1],target]
    return sum(categorical_bits([counter.get(x,0) for x in range(26)]) for counter in contexts.values())


def main():
    checks=[]
    def need(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    result=json.load(open(ROOT/'gdt001_mtf_dynamic_rank_results.json'));_,lines=load_lattice();paths=paths_for(lines);fixed=sum(fixed_costs(paths).values());symbols=sum(len(w) for p in paths for w in p.words)
    need(result['schema']=='GDT001_MTF_DYNAMIC_RANK_V1','schema');need(result['status']=='EXPLORATORY_NOT_CONFIRMED_TRANSLATION','status');need(result['decision']=='STOP_MTF_DYNAMIC_RANK_SCREEN','decision');need(result['inputs']=={name:sha256_file(ROOT/name) for name in result['inputs']},'inputs');need(result['implementation']=={name:sha256_file(ROOT/name) for name in result['implementation']},'implementation');need(result['counts']=={'physical_lines':len(paths),'source_signs':symbols,'source_events_with_spaces':sum(len(p.source_line) for p in paths)},'counts');need(abs(result['accounting']['fixed_bits']-fixed)<1e-9,'fixed')
    log25=math.lgamma(26)/math.log(2);log26=math.lgamma(27)/math.log(2);mtf_key=3+math.log2(6)+universal_uint_bits(2)+math.log2(3)+log25+log26;static_key=3+math.log2(6)+universal_uint_bits(2)+math.log2(3)+log26;null_key=3+universal_uint_bits(2)+math.log2(3)+log25
    need(abs(result['accounting']['historical_mtf_key_bits']-mtf_key)<1e-12,'mtf_key');need(abs(result['accounting']['static_injective_key_bits']-static_key)<1e-12,'static_key');need(abs(result['accounting']['anonymous_mtf_key_bits']-null_key)<1e-12,'null_key')
    for row in result['historical_rows']:
        decoder=row['decoder'];ranks=parse_rank(decoder);initial=[ord(x)-97 for x in decoder['initial_target_order']];need(sorted(initial)==list(range(26)),f"initial:{row['language']}:{row['seed']}");decoded=decode(paths,ranks,initial);need(inverse(decoded,ranks,initial)==[p.source_line for p in paths],f"roundtrip:{row['language']}:{row['seed']}");bits=lm_bits(paths,ranks,initial,row['language']);need(abs(bits-row['payload_bits'])<1e-6,f"language:{row['language']}:{row['seed']}");need(abs(row['total_bits']-(fixed+mtf_key+bits))<1e-6,f"total:{row['language']}:{row['seed']}");need(row['decoded_stream_hash']==hashlib.sha256(canonical(decoded)).hexdigest(),f"stream:{row['language']}:{row['seed']}");need(row['decoder_hash']==hashlib.sha256(canonical(decoder)).hexdigest(),f"decoder:{row['language']}:{row['seed']}")
    for row in result['static_rows']:
        mapping=[ord(x)-97 for x in row['mapping']];need(sorted(mapping)==list(range(26)),f"static_map:{row['language']}:{row['seed']}");bits=static_bits(paths,mapping,row['language']);need(abs(bits-row['payload_bits'])<1e-6,f"static_bits:{row['language']}:{row['seed']}");need(abs(row['total_bits']-(fixed+static_key+bits))<1e-6,f"static_total:{row['language']}:{row['seed']}")
    for row in result['anonymous_rows']:
        ranks=parse_rank(row['decoder']);bits=kt_bits(paths,ranks);need(abs(bits-row['payload_bits'])<1e-6,f"null_bits:{row['seed']}");need(abs(row['total_bits']-(fixed+null_key+bits))<1e-6,f"null_total:{row['seed']}")
    best=min(result['historical_rows'],key=lambda x:(x['total_bits'],x['language'],x['seed']));static=min(result['static_rows'],key=lambda x:(x['total_bits'],x['language'],x['seed']));null=min(result['anonymous_rows'],key=lambda x:(x['total_bits'],x['seed']));need(result['best']==best,'best');need(result['best_static_injective']==static,'static_best');need(result['best_matched_anonymous']==null,'null_best')
    identity=transform(lines,paths,'BOUNDARY_PRESERVING_IDENTITY_PERMUTATION');perm={}
    for left,right in zip(paths,identity):
        for a,b in zip(left.source_line,right.source_line):
            if a!=' ':perm[a]=b
    ranks=parse_rank(best['decoder']);transformed=[0]*25
    for a,b in perm.items():transformed[LETTERS.index(b)]=ranks[LETTERS.index(a)]
    initial=[ord(x)-97 for x in best['decoder']['initial_target_order']];need(decode(identity,transformed,initial)==decode(paths,ranks,initial),'identity_equivariance')
    control_gains={}
    for record in result['controls']:
        control_paths=transform(lines,paths,record['control']);need(record['selected_path_stream_sha256']==hashlib.sha256(canonical([path.source_line for path in control_paths])).hexdigest(),f"control_stream:{record['control']}");need(record['source_events_with_spaces']==sum(len(path.source_line) for path in control_paths),f"control_events:{record['control']}");candidate=record['candidate'];anonymous=record['matched_anonymous'];cranks=[int(x['fixed_rank']) for x in candidate['rank_key']];cinitial=[ord(x)-97 for x in candidate['initial_target_order']];cbits=lm_bits(control_paths,cranks,cinitial,best['language']);need(abs(cbits-candidate['payload_bits'])<1e-6,f"control_language:{record['control']}");nranks=[int(x['fixed_rank']) for x in anonymous['rank_key']];nbits=kt_bits(control_paths,nranks);need(abs(nbits-anonymous['payload_bits'])<1e-6,f"control_null:{record['control']}");gain=(fixed+null_key+nbits)-(fixed+mtf_key+cbits);need(abs(gain-record['gain_vs_matched_anonymous_bits'])<1e-6,f"control_gain:{record['control']}");need(abs(gain/record['source_events_with_spaces']-record['gain_bits_per_source_event'])<1e-12,f"control_rate:{record['control']}");control_gains[record['control']]=gain
    expected_gates={'roundtrip_all':True,'identity_permutation_equivariance':True,'beats_matched_anonymous':best['total_bits']<null['total_bits'],'beats_static_injective':best['total_bits']<static['total_bits'],'beats_selector_adjusted_global_leader':best['total_bits']<result['accounting']['selector_adjusted_global_leader_bits'],'stable_winning_language_decoder':len({row['decoder_hash'] for row in result['historical_rows'] if row['language']==best['language']})==1,'real_specificity_exceeds_within_line_shuffle':null['total_bits']-best['total_bits']>control_gains['WITHIN_LINE_SYMBOL_SHUFFLE']};need(result['gates']==expected_gates,'gates');need(not all(expected_gates.values()),'stop')
    out={'schema':'GDT001_MTF_DYNAMIC_RANK_VALIDATION_V1','status':'PASS_INDEPENDENT_PYTHON_EXACT_STOP','check_count':len(checks),'checks':checks,'result_sha256':sha256_file(ROOT/'gdt001_mtf_dynamic_rank_results.json'),'best_total_bits':best['total_bits'],'matched_anonymous_total_bits':null['total_bits'],'static_injective_total_bits':static['total_bits'],'selector_adjusted_global_leader_bits':result['accounting']['selector_adjusted_global_leader_bits'],'validation_scope':'independently reconstructs retained-key payloads, inversion, controls, accounting, and decision; does not independently reproduce heuristic search or exhaustive local-optimum checks','claim_ceiling':'Independent retained-key score, inversion, control, accounting, and decision reconstruction only; no sign, rank, letter, language, plaintext, meaning, or translation.'};(ROOT/'gdt001_mtf_dynamic_rank_validation.json').write_bytes(canonical(out));print(json.dumps({'status':out['status'],'checks':len(checks),'best':best['total_bits']}))


if __name__=='__main__':main()
