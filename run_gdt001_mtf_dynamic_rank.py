#!/usr/bin/env python3
"""Bounded line-reset move-to-front dynamic-rank cipher screen."""

from __future__ import annotations

import ctypes
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np

from gdt001_core import LETTERS, ROOT, canonical, fixed_costs, load_lattice, sha256_file, universal_uint_bits
from gdt001_controls import transform
from gdt001_language_models import PACK_NAMES, train_pack


ORDER = 2
SEEDS = (67101, 67102, 67103)
CONTROL_NAMES = ("WITHIN_LINE_SYMBOL_SHUFFLE", "TIMM_COPY_MODIFY_SYNTHETIC")


def selected_paths(lines):
    with (ROOT / "candidates/nonsemantic_ngram_o2/segmentation.tsv").open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != len(lines): raise ValueError("segmentation length")
    output = []
    for line, row in zip(lines, rows):
        if line.locus != row["locus"]: raise ValueError("segmentation locus")
        output.append(next(path for path in line.paths if path.path_id == row["selected_path_id"]))
    return output


def arrays(paths):
    tokens, offsets = [], [0]
    for path in paths:
        tokens.extend(25 if char == " " else LETTERS.index(char) for char in path.source_line)
        offsets.append(len(tokens))
    return np.asarray(tokens, dtype=np.int32), np.asarray(offsets, dtype=np.int64)


def compile_library():
    source = ROOT / "gdt001_mtf_score.cpp"
    library = ROOT / ".gdt001/gdt001_mtf_score.so"
    library.parent.mkdir(exist_ok=True)
    if not library.exists() or library.stat().st_mtime_ns < source.stat().st_mtime_ns:
        subprocess.run(["g++", "-O3", "-std=c++17", "-fopenmp", "-shared", "-fPIC", str(source), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    ip = ctypes.POINTER(ctypes.c_int32); lp = ctypes.POINTER(ctypes.c_int64); dp = ctypes.POINTER(ctypes.c_double)
    api.gdt001_mtf_lm_score.argtypes = [ip, lp, ctypes.c_int64, ip, ip, dp]; api.gdt001_mtf_lm_score.restype = ctypes.c_double
    api.gdt001_static_lm_score.argtypes = [ip, lp, ctypes.c_int64, ip, dp]; api.gdt001_static_lm_score.restype = ctypes.c_double
    api.gdt001_mtf_kt_score.argtypes = [ip, lp, ctypes.c_int64, ip]; api.gdt001_mtf_kt_score.restype = ctypes.c_double
    api.gdt001_mtf_lm_swap_scores.argtypes = [ip, lp, ctypes.c_int64, ip, ip, dp, ctypes.c_int, dp]
    api.gdt001_static_lm_swap_scores.argtypes = [ip, lp, ctypes.c_int64, ip, dp, dp]
    api.gdt001_mtf_kt_swap_scores.argtypes = [ip, lp, ctypes.c_int64, ip, dp]
    return api


def ptr(a, kind): return a.ctypes.data_as(ctypes.POINTER(kind))


def pair(size, index):
    left = 0
    while index >= size - left - 1:
        index -= size - left - 1; left += 1
    return left, left + 1 + index


def initialization(seed):
    rng = np.random.default_rng(seed)
    return rng.permutation(25).astype(np.int32), rng.permutation(26).astype(np.int32)


def mtf_score(api, tokens, offsets, ranks, initial, costs):
    return float(api.gdt001_mtf_lm_score(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                        ptr(ranks, ctypes.c_int32), ptr(initial, ctypes.c_int32), ptr(costs, ctypes.c_double)))


def static_score(api, tokens, offsets, mapping, costs):
    return float(api.gdt001_static_lm_score(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                           ptr(mapping, ctypes.c_int32), ptr(costs, ctypes.c_double)))


def kt_score(api, tokens, offsets, ranks):
    return float(api.gdt001_mtf_kt_score(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                        ptr(ranks, ctypes.c_int32)))


def search_mtf(api, tokens, offsets, costs, seed):
    ranks, initial = initialization(seed); score = mtf_score(api, tokens, offsets, ranks, initial, costs); passes = 0
    while passes < 100:
        changed = False
        for mode, size in ((0, 25), (1, 26)):
            values = np.empty(size*(size-1)//2, dtype=np.float64)
            api.gdt001_mtf_lm_swap_scores(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                          ptr(ranks, ctypes.c_int32), ptr(initial, ctypes.c_int32), ptr(costs, ctypes.c_double), mode,
                                          ptr(values, ctypes.c_double))
            index = int(np.argmin(values)); candidate = float(values[index])
            if candidate < score - 1e-9:
                left, right = pair(size, index); (ranks if mode == 0 else initial)[[left, right]] = (ranks if mode == 0 else initial)[[right, left]]
                score = candidate; changed = True
        passes += 1
        if not changed: break
    local = []
    for mode, size in ((0, 25), (1, 26)):
        values = np.empty(size*(size-1)//2, dtype=np.float64)
        api.gdt001_mtf_lm_swap_scores(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                      ptr(ranks, ctypes.c_int32), ptr(initial, ctypes.c_int32), ptr(costs, ctypes.c_double), mode,
                                      ptr(values, ctypes.c_double))
        local.append(float(values.min()) >= score - 1e-8)
    return score, ranks, initial, passes, all(local)


def search_static(api, tokens, offsets, costs, seed):
    _, mapping = initialization(seed); score = static_score(api, tokens, offsets, mapping, costs); passes = 0
    while passes < 100:
        values = np.empty(325, dtype=np.float64)
        api.gdt001_static_lm_swap_scores(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                         ptr(mapping, ctypes.c_int32), ptr(costs, ctypes.c_double), ptr(values, ctypes.c_double))
        index = int(np.argmin(values)); candidate = float(values[index])
        passes += 1
        if candidate >= score - 1e-9: break
        left, right = pair(26, index); mapping[[left, right]] = mapping[[right, left]]; score = candidate
    values = np.empty(325, dtype=np.float64)
    api.gdt001_static_lm_swap_scores(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                     ptr(mapping, ctypes.c_int32), ptr(costs, ctypes.c_double), ptr(values, ctypes.c_double))
    return score, mapping, passes, float(values.min()) >= score - 1e-8


def search_kt(api, tokens, offsets, seed):
    ranks, _ = initialization(seed); score = kt_score(api, tokens, offsets, ranks); passes = 0
    while passes < 100:
        values = np.empty(300, dtype=np.float64)
        api.gdt001_mtf_kt_swap_scores(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                      ptr(ranks, ctypes.c_int32), ptr(values, ctypes.c_double))
        index = int(np.argmin(values)); candidate = float(values[index])
        passes += 1
        if candidate >= score - 1e-9: break
        left, right = pair(25, index); ranks[[left, right]] = ranks[[right, left]]; score = candidate
    values = np.empty(300, dtype=np.float64)
    api.gdt001_mtf_kt_swap_scores(ptr(tokens, ctypes.c_int32), ptr(offsets, ctypes.c_int64), len(offsets)-1,
                                  ptr(ranks, ctypes.c_int32), ptr(values, ctypes.c_double))
    return score, ranks, passes, float(values.min()) >= score - 1e-8


def decode_lines(paths, ranks, initial):
    output = []
    for path in paths:
        state = list(map(int, initial)); chars = []
        for char in path.source_line:
            if char == " ": chars.append(" "); continue
            rank = int(ranks[LETTERS.index(char)]); target = state[rank]; chars.append(chr(97+target)); state.pop(rank); state.insert(0, target)
        output.append("".join(chars))
    return output


def inverse_lines(decoded, ranks, initial):
    inverse = {int(rank): LETTERS[source] for source, rank in enumerate(ranks)}; output = []
    for text in decoded:
        state = list(map(int, initial)); chars = []
        for char in text:
            if char == " ": chars.append(" "); continue
            target = ord(char)-97; rank = state.index(target); chars.append(inverse[rank]); state.pop(rank); state.insert(0, target)
        output.append("".join(chars))
    return output


def digest_rows(ranks, initial):
    rows = [{"source": LETTERS[i], "fixed_rank": int(ranks[i])} for i in range(25)]
    order = "".join(chr(97+int(x)) for x in initial)
    return rows, order, hashlib.sha256(canonical({"rank_key": rows, "initial_target_order": order})).hexdigest()


def main():
    _, lines = load_lattice(); paths = selected_paths(lines); tokens, offsets = arrays(paths); api = compile_library()
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(word) for path in paths for word in path.words)
    leader = float(json.loads((ROOT/"gdt001_online_context_mixer_results.json").read_text())["best"]["total_bits"]) + 1.0
    log25f = math.lgamma(26)/math.log(2); log26f = math.lgamma(27)/math.log(2)
    mtf_key = 3 + math.log2(6) + universal_uint_bits(ORDER) + math.log2(3) + log25f + log26f
    static_key = 3 + math.log2(6) + universal_uint_bits(ORDER) + math.log2(3) + log26f
    null_key = 3 + universal_uint_bits(ORDER) + math.log2(3) + log25f
    rows = []
    for language in PACK_NAMES:
        costs = np.ascontiguousarray(train_pack(language, ORDER).costs, dtype=np.float64)
        for seed in SEEDS:
            payload, ranks, initial, passes, local = search_mtf(api, tokens, offsets, costs, seed); mapping, initial_order, digest = digest_rows(ranks, initial)
            decoded = decode_lines(paths, ranks, initial); roundtrip = inverse_lines(decoded, ranks, initial) == [path.source_line for path in paths]
            decoder = {"schema":"GDT001_MTF_DYNAMIC_RANK_DECODER_V1","language_pack":language,"order":ORDER,"line_reset":True,"frozen_source_space_events":"fixed and do not update state","rank_key":mapping,"initial_target_order":initial_order}
            total = fixed + mtf_key + payload
            rows.append({"model":"HISTORICAL_MTF","language":language,"seed":seed,"total_bits":total,"bits_per_symbol":total/symbols,"fixed_bits":fixed,"key_bits":mtf_key,"payload_bits":payload,"gap_vs_selector_adjusted_leader_bits":total-leader,"passes":passes,"roundtrip":roundtrip,"all_pair_swaps_locally_optimal":local,"mapping_hash":digest,"decoded_stream_hash":hashlib.sha256(canonical(decoded)).hexdigest(),"decoder_hash":hashlib.sha256(canonical(decoder)).hexdigest(),"decoder":decoder,"cpu_exact_retained_key_score":True,"heuristic_search":True})
    static_rows = []
    for language in PACK_NAMES:
        costs = np.ascontiguousarray(train_pack(language, ORDER).costs, dtype=np.float64)
        for seed in SEEDS:
            payload, mapping, passes, local = search_static(api, tokens, offsets, costs, seed); order = "".join(chr(97+int(x)) for x in mapping)
            total = fixed + static_key + payload; decoder = {"schema":"GDT001_STATIC_INJECTIVE_COMPARATOR_V1","language_pack":language,"order":ORDER,"source_mapping":order[:25],"omitted_target":order[25],"frozen_source_space_events":"fixed"}
            static_rows.append({"model":"STATIC_INJECTIVE","language":language,"seed":seed,"total_bits":total,"bits_per_symbol":total/symbols,"fixed_bits":fixed,"key_bits":static_key,"payload_bits":payload,"passes":passes,"all_pair_swaps_locally_optimal":local,"mapping":order,"decoder_hash":hashlib.sha256(canonical(decoder)).hexdigest(),"decoder":decoder,"cpu_exact_retained_key_score":True,"heuristic_search":True})
    null_rows = []
    for seed in SEEDS:
        payload, ranks, passes, local = search_kt(api, tokens, offsets, seed); mapping, _, digest = digest_rows(ranks, np.arange(26,dtype=np.int32)); total = fixed + null_key + payload
        decoder = {"schema":"GDT001_ANONYMOUS_MTF_KT_DECODER_V1","order":ORDER,"line_reset":True,"rank_key":mapping,"target_labels":"25 reachable anonymous labels plus frozen source-space event; canonical initial order has one inert item"}
        null_rows.append({"model":"ANONYMOUS_MTF_KT","seed":seed,"total_bits":total,"bits_per_symbol":total/symbols,"fixed_bits":fixed,"key_bits":null_key,"payload_bits":payload,"passes":passes,"all_pair_swaps_locally_optimal":local,"mapping_hash":digest,"decoder_hash":hashlib.sha256(canonical(decoder)).hexdigest(),"decoder":decoder,"cpu_exact_retained_key_score":True,"heuristic_search":True})
    best = min(rows,key=lambda x:(x["total_bits"],x["language"],x["seed"])); best_static=min(static_rows,key=lambda x:(x["total_bits"],x["language"],x["seed"])); best_null=min(null_rows,key=lambda x:(x["total_bits"],x["seed"]))
    same = [row for row in rows if row["language"] == best["language"]]; stable = len({row["decoder_hash"] for row in same}) == 1
    controls=[]
    for name in CONTROL_NAMES:
        control_paths=transform(lines,paths,name); ctokens,coffsets=arrays(control_paths); costs=np.ascontiguousarray(train_pack(best["language"],ORDER).costs,dtype=np.float64)
        candidate=[]; anonymous=[]
        for seed in SEEDS:
            pb,rk,ini,ps,pl=search_mtf(api,ctokens,coffsets,costs,seed); mr,io,mh=digest_rows(rk,ini); candidate.append({"seed":seed,"total_bits":fixed+mtf_key+pb,"payload_bits":pb,"passes":ps,"all_pair_swaps_locally_optimal":pl,"rank_key":mr,"initial_target_order":io,"mapping_hash":mh})
            nb,nr,npas,nl=search_kt(api,ctokens,coffsets,seed); nmr,_,nmh=digest_rows(nr,np.arange(26,dtype=np.int32)); anonymous.append({"seed":seed,"total_bits":fixed+null_key+nb,"payload_bits":nb,"passes":npas,"all_pair_swaps_locally_optimal":nl,"rank_key":nmr,"mapping_hash":nmh})
        cb=min(candidate,key=lambda x:x["total_bits"]); nb=min(anonymous,key=lambda x:x["total_bits"]); events=len(ctokens);controls.append({"control":name,"selected_path_stream_sha256":hashlib.sha256(canonical([path.source_line for path in control_paths])).hexdigest(),"source_events_with_spaces":events,"candidate":cb,"matched_anonymous":nb,"gain_vs_matched_anonymous_bits":nb["total_bits"]-cb["total_bits"],"gain_bits_per_source_event":(nb["total_bits"]-cb["total_bits"])/events,"specificity_role":"REQUIRED_LENGTH_PRESERVING_GATE" if name=="WITHIN_LINE_SYMBOL_SHUFFLE" else "VARIABLE_LENGTH_DIAGNOSTIC_ONLY"})
    identity_paths=transform(lines,paths,"BOUNDARY_PRESERVING_IDENTITY_PERMUTATION"); identity_tokens,identity_offsets=arrays(identity_paths); source_permutation={}
    for original,changed in zip(paths,identity_paths):
        for left,right in zip(original.source_line,changed.source_line):
            if left!=" ": source_permutation[left]=right
    best_ranks=np.asarray([item["fixed_rank"] for item in best["decoder"]["rank_key"]],dtype=np.int32); identity_ranks=np.empty(25,dtype=np.int32)
    for source,changed in source_permutation.items(): identity_ranks[LETTERS.index(changed)]=best_ranks[LETTERS.index(source)]
    best_initial=np.asarray([ord(char)-97 for char in best["decoder"]["initial_target_order"]],dtype=np.int32); best_costs=np.ascontiguousarray(train_pack(best["language"],ORDER).costs,dtype=np.float64)
    identity_payload=mtf_score(api,identity_tokens,identity_offsets,identity_ranks,best_initial,best_costs); identity_decoded=decode_lines(identity_paths,identity_ranks,best_initial); real_decoded=decode_lines(paths,best_ranks,best_initial)
    equivariance={"payload_bits":identity_payload,"real_payload_bits":best["payload_bits"],"payload_equal":abs(identity_payload-best["payload_bits"])<1e-8,"decoded_stream_equal":identity_decoded==real_decoded,"source_permutation":"".join(source_permutation[c] for c in LETTERS)}
    within=next(row for row in controls if row["control"]=="WITHIN_LINE_SYMBOL_SHUFFLE");gates={"roundtrip_all":all(row["roundtrip"] for row in rows),"identity_permutation_equivariance":equivariance["payload_equal"] and equivariance["decoded_stream_equal"],"beats_matched_anonymous":best["total_bits"]<best_null["total_bits"],"beats_static_injective":best["total_bits"]<best_static["total_bits"],"beats_selector_adjusted_global_leader":best["total_bits"]<leader,"stable_winning_language_decoder":stable,"real_specificity_exceeds_within_line_shuffle":best_null["total_bits"]-best["total_bits"]>within["gain_vs_matched_anonymous_bits"]}
    decision="CONTINUE_MTF_DYNAMIC_RANK" if all(gates.values()) else "STOP_MTF_DYNAMIC_RANK_SCREEN"
    result={"schema":"GDT001_MTF_DYNAMIC_RANK_V1","status":"EXPLORATORY_NOT_CONFIRMED_TRANSLATION","decision":decision,"scope":"line-reset 25-source-rank/26-target-letter move-to-front cipher; frozen GDT001 ASCII source-space stream including human-separator-derived and cleaner-fragment boundaries; order 2; six frozen historical packs; three deterministic starts","search_scope":"alternating exact all-pair-swap descent; exact CPU retained-key scoring, not global key optimization","inputs":{name:sha256_file(ROOT/name) for name in ("gdt001_corpus_lattice.json","gdt001_language_pack_manifest.json","candidates/nonsemantic_ngram_o2/segmentation.tsv","gdt001_online_context_mixer_results.json","gdt001_counterfactual_manifest.json","gdt001_controls.py")},"implementation":{name:sha256_file(ROOT/name) for name in ("run_gdt001_mtf_dynamic_rank.py","gdt001_mtf_score.cpp","GDT001_MTF_DYNAMIC_RANK_METHOD.md")},"counts":{"physical_lines":len(paths),"source_signs":symbols,"source_events_with_spaces":len(tokens)},"accounting":{"fixed_bits":fixed,"order_code_bits":universal_uint_bits(ORDER),"restart_selector_bits":math.log2(3),"anonymous_kt_outcomes":26,"log2_25_factorial":log25f,"log2_26_factorial":log26f,"historical_mtf_key_bits":mtf_key,"static_injective_key_bits":static_key,"anonymous_mtf_key_bits":null_key,"selector_adjusted_global_leader_bits":leader},"best":best,"best_static_injective":best_static,"best_matched_anonymous":best_null,"historical_rows":rows,"static_rows":static_rows,"anonymous_rows":null_rows,"identity_permutation_equivariance":equivariance,"controls":controls,"gates":gates,"claim_ceiling":"Bounded reversible dynamic-rank cipher screen only; no source sign, rank, letter, language, word, plaintext, meaning, or translation is established."}
    (ROOT/"gdt001_mtf_dynamic_rank_results.json").write_bytes(canonical(result))
    print(json.dumps({"decision":decision,"best":(best["language"],best["seed"],best["total_bits"]),"matched":best_null["total_bits"],"static":best_static["total_bits"],"leader":leader,"stable":stable,"gates":gates}))


if __name__ == "__main__": main()
