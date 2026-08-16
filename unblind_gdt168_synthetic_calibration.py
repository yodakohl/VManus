#!/usr/bin/env python3
"""Join frozen GDT168 truth after blind outputs and score diagnostic recovery."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLIND = ROOT / "gdt168_blind_synthetic_corpora.json.gz"
TRUTH = ROOT / "gdt168_synthetic_ground_truth.json.gz"
CODEBOOK = ROOT / "gdt168_codebook_truth.tsv"
FREEZE = ROOT / "gdt168_source_encoder_freeze.json"
BLIND_RESULT = ROOT / "gdt168_blind_result.json"
BLIND_SUMMARY = ROOT / "gdt168_blind_diagnostic_summary.tsv"
METHOD = ROOT / "GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_METHOD.md"
REPORT = ROOT / "GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_REPORT.md"
INFO = ROOT / "gdt168_ground_truth_information.tsv"
DECODER = ROOT / "gdt168_ground_truth_decoder.tsv"
RECOVERY = ROOT / "gdt168_diagnostic_recovery_matrix.tsv"
COUNTER = ROOT / "gdt168_counterexamples.tsv"
RESULT = ROOT / "gdt168_result.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def write(path, rows):
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with Path(path).open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fields,delimiter="\t",lineterminator="\n");writer.writeheader()
        writer.writerows([{field:row.get(field,"NA") for field in fields} for row in rows])


def entropy(counts):
    total=sum(counts.values())
    return -sum(n/total*math.log2(n/total) for n in counts.values() if n) if total else 0.0


def conditional_entropy(rows, key):
    groups=defaultdict(Counter);total=len(rows)
    for row in rows:groups[key(row)][int(row["concept_index"])]+=1
    return sum(sum(c.values())/total*entropy(c) for c in groups.values())


def compiler(row):
    return (row["wrapper"],row["local_frame"],row["right_family"],row["closure_value"],row["dy_closure"],row["b3"])


def representations():
    return {
        "PAGE_HOST":lambda x:x["page_host"],
        "COMPILER_ONLY":compiler,
        "PAGE_HOST_PLUS_SLOT":lambda x:(x["page_host"],x["slot"]),
        "FULL_TUPLE_PLUS_SLOT":lambda x:(x["page_host"],compiler(x),x["slot"]),
        "RAW_SURFACE":lambda x:x["surface"],
    }


def held_decoder(rows,key):
    units=sorted({x["source_unit_id"] for x in rows});correct=covered=0;total=0;positive=0
    for held in units:
        maps=defaultdict(Counter)
        for row in rows:
            if row["source_unit_id"]!=held:maps[key(row)][int(row["concept_index"])]+=1
        fold_correct=fold_covered=fold_total=0
        for row in rows:
            if row["source_unit_id"]!=held:continue
            fold_total+=1;k=key(row)
            if k in maps:
                fold_covered+=1;prediction=sorted(maps[k].items(),key=lambda x:(-x[1],x[0]))[0][0]
                fold_correct+=int(prediction==int(row["concept_index"]))
        total+=fold_total;covered+=fold_covered;correct+=fold_correct;positive+=int(fold_correct>0)
    return {"predictions":covered,"correct":correct,"total_rows":total,"coverage":covered/total,
            "accuracy_on_predictions":correct/covered if covered else 0.0,"positive_units":positive,"units":len(units)}


def main():
    blind_result=json.loads(BLIND_RESULT.read_text());assert blind_result["status"]=="BLIND_DIAGNOSTICS_COMPLETE_TRUTH_NOT_READ" and blind_result["truth_files_read"]==[]
    with gzip.open(BLIND,"rt",encoding="utf-8") as handle:blind=json.load(handle)["rows"]
    with gzip.open(TRUTH,"rt",encoding="utf-8") as handle:truth=json.load(handle)["rows"]
    assert len(blind)==len(truth)==240000
    tmap={x["blind_id"]:x for x in truth};assert len(tmap)==len(truth)
    joined=[]
    for row in blind:
        t=tmap[row["blind_id"]];joined.append({**row,**t})
    assert all((x["corpus_view"]=="CONTROL_X")== (x["system"]=="SYSTEM_A") for x in joined)
    primary={system:[x for x in joined if x["system"]==system and x["renderer"]=="R1_S1"] for system in ("SYSTEM_A","SYSTEM_B")}
    info=[];dec=[]
    for system,rows in primary.items():
        concept_entropy=entropy(Counter(int(x["concept_index"]) for x in rows))
        for name,key in representations().items():
            cond=conditional_entropy(rows,key);mi=concept_entropy-cond
            info.append({"system":system,"representation":name,"rows":len(rows),"concept_entropy_bits":concept_entropy,
                         "conditional_entropy_bits":cond,"mutual_information_bits":mi,"fraction_concept_entropy":mi/concept_entropy})
            dec.append({"system":system,"representation":name,**held_decoder(rows,key)})
    info_by={(x["system"],x["representation"]):x for x in info}
    dec_by={(x["system"],x["representation"]):x for x in dec}
    s=blind_result["summary"]
    matrix=[
        {"diagnostic":"GDT113_RECORD_CLOSURE","known_property_a":"RECORD_GRAMMAR_PRESENT","known_property_b":"RECORD_GRAMMAR_PRESENT","blind_a":"PERFECT","blind_b":"PERFECT","assessment":"TRUE_POSITIVE_BOTH_NONDISCRIMINATING"},
        {"diagnostic":"GDT160_COMPATIBLE_PAIRING","known_property_a":"SEPARATE_POSITIONAL_COMPILER","known_property_b":"DISTRIBUTED_COMPILER_CODE","blind_a":f"density={s['CONTROL_X']['GDT160_SURFACE_ALGEBRA:compatible_pair_density']:.6f}","blind_b":f"density={s['CONTROL_Y']['GDT160_SURFACE_ALGEBRA:compatible_pair_density']:.6f}","assessment":"POSITIVE_BOTH_BUT_STRONGLY_ENRICHED_FOR_DISTRIBUTED_CODE"},
        {"diagnostic":"GDT162_SHORT_HOST","known_property_a":"TRUE_INJECTIVE_SHORT_CODEBOOK","known_property_b":"100_WAY_NONLEXICAL_HOST_DIGIT","blind_a":"SHORT_AND_RECURRENT","blind_b":"SHORT_AND_RECURRENT","assessment":"NONDISCRIMINATING_BY_LENGTH_RECURRENCE"},
        {"diagnostic":"GDT162_HOST_TO_COMPILER","known_property_a":"HOST_LEXICAL_COMPILER_INDEPENDENT","known_property_b":"HOST_PARTIAL_DIGIT_COMPILER_CARRIES_REMAINDER","blind_a":f"{s['CONTROL_X']['GDT162_167_CONTEXT:COMPILER_GAIN_PER_EVENT']:+.6f}","blind_b":f"{s['CONTROL_Y']['GDT162_167_CONTEXT:COMPILER_GAIN_PER_EVENT']:+.6f}","assessment":"NEGATIVE_BOTH_FALSE_NEGATIVE_FOR_TRUE_CODEBOOK"},
        {"diagnostic":"GDT163_SAME_GROUP_SUBSTITUTION","known_property_a":"NO_PRODUCTIVE_INTERNAL_OPERATOR","known_property_b":"HOST_DIGIT_COUPLED_TO_COMPILER_DIGITS","blind_a":f"{s['CONTROL_X']['GDT163_164_SUBSTITUTION:COMPILER_DELTA_COSINE']:+.6f}","blind_b":f"{s['CONTROL_Y']['GDT163_164_SUBSTITUTION:COMPILER_DELTA_COSINE']:+.6f}","assessment":"CORRECTLY_LOCALIZES_DISTRIBUTED_COMPILER_COUPLING"},
        {"diagnostic":"GDT164_EXTERNAL_SUBSTITUTION","known_property_a":"NO_SUBSTITUTION_OPERATOR","known_property_b":"NO_EXTERNAL_SUBSTITUTION_OPERATOR","blind_a":f"{s['CONTROL_X']['GDT163_164_SUBSTITUTION:EXTERNAL_WINDOW_DELTA_COSINE']:+.6f}","blind_b":f"{s['CONTROL_Y']['GDT163_164_SUBSTITUTION:EXTERNAL_WINDOW_DELTA_COSINE']:+.6f}","assessment":"TRUE_NEGATIVE_BOTH"},
        {"diagnostic":"GDT165_NEXT_HOST","known_property_a":"LEXICAL_IDENTITIES_IN_REAL_SOURCE_ORDER","known_property_b":"MANY_TO_ONE_HOST_DIGITS","blind_a":f"{s['CONTROL_X']['GDT162_167_CONTEXT:NEXT_HOST_GAIN_PER_EVENT']:+.6f}","blind_b":f"{s['CONTROL_Y']['GDT162_167_CONTEXT:NEXT_HOST_GAIN_PER_EVENT']:+.6f}","assessment":"NEGATIVE_BOTH_FALSE_NEGATIVE_FOR_LEXICAL_CODEBOOK"},
        {"diagnostic":"GDT166_UNORDERED_CONTEXT","known_property_a":"LEXICAL_IDENTITIES_IN_REAL_SOURCE_CONTEXT","known_property_b":"MANY_TO_ONE_HOST_DIGITS","blind_a":f"line={s['CONTROL_X']['GDT162_167_CONTEXT:WHOLE_LINE_GAIN_PER_EVENT']:+.6f}","blind_b":f"line={s['CONTROL_Y']['GDT162_167_CONTEXT:WHOLE_LINE_GAIN_PER_EVENT']:+.6f}","assessment":"NEGATIVE_BOTH_AND_NONLEXICAL_WORLD_LOOKS_LESS_NEGATIVE"},
        {"diagnostic":"GDT167_RENDERER_ALIGNMENT","known_property_a":"COMMON_CODEBOOK_UNDER_SYMBOL_PERMUTATION","known_property_b":"COMMON_NONLEXICAL_HOST_DIGITS_UNDER_SYMBOL_PERMUTATION","blind_a":f"{s['CONTROL_X']['GDT167_ALIGNMENT:CROSS_REGISTER_MEAN_CORRELATION']:.6f}","blind_b":f"{s['CONTROL_Y']['GDT167_ALIGNMENT:CROSS_REGISTER_MEAN_CORRELATION']:.6f}","assessment":"TRUE_RENDER_ALIGNMENT_BUT_FALSE_POSITIVE_IF_CALLED_LEXICAL"},
        {"diagnostic":"GDT113_TRUTH_RETRIEVAL","known_property_a":"HOST_ALONE_EXACT_IN_ENCODER","known_property_b":"FULL_TUPLE_PLUS_SLOT_EXACT_IN_ENCODER","blind_a":f"host_MI={info_by['SYSTEM_A','PAGE_HOST']['fraction_concept_entropy']:.3f}","blind_b":f"host_MI={info_by['SYSTEM_B','PAGE_HOST']['fraction_concept_entropy']:.3f};full_MI={info_by['SYSTEM_B','FULL_TUPLE_PLUS_SLOT']['fraction_concept_entropy']:.3f}","assessment":"UNBLIND_TRUTH_SEPARATES_WORLDS_WHERE_FORMAL_CONTEXT_TESTS_DO_NOT"},
    ]
    counters=[
        {"counterexample":"NEGATIVE_HOST_CONTEXT_IMPLIES_NO_LEXICAL_CODEBOOK","evidence":f"System A is injective but compiler/next/window/line gains are {s['CONTROL_X']['GDT162_167_CONTEXT:COMPILER_GAIN_PER_EVENT']:+.3f}/{s['CONTROL_X']['GDT162_167_CONTEXT:NEXT_HOST_GAIN_PER_EVENT']:+.3f}/{s['CONTROL_X']['GDT162_167_CONTEXT:WINDOW_PM2_GAIN_PER_EVENT']:+.3f}/{s['CONTROL_X']['GDT162_167_CONTEXT:WHOLE_LINE_GAIN_PER_EVENT']:+.3f} bits/event.","impact":"GDT162-166 negatives have low sensitivity to a sparse true codebook whose compiler is content-independent."},
        {"counterexample":"STRONG_COMPATIBILITY_IMPLIES_LEXICAL_COMPOSITION","evidence":f"Distributed System B density {s['CONTROL_Y']['GDT160_SURFACE_ALGEBRA:compatible_pair_density']:.3f} exceeds lexical System A {s['CONTROL_X']['GDT160_SURFACE_ALGEBRA:compatible_pair_density']:.3f}.","impact":"Compatibility can be generated more strongly by distributed record notation than by lexical hosts."},
        {"counterexample":"CROSS_REGISTER_ALIGNMENT_IMPLIES_SHARED_LEXICON","evidence":"Both systems align at correlation 1.0 under parallel symbol-permutation renderers.","impact":"GDT167 detects shared renderer geometry, not whether host values are lexical."},
        {"counterexample":"SHORT_RECURRENT_HOST_IMPLIES_CODEBOOK","evidence":"System B has only 100 short hosts with recurrent mass 1.0 but host alone is deliberately many-to-one.","impact":"Length and recurrence require truth-sensitive retrieval or an independent content endpoint."},
        {"counterexample":"CALIBRATION_IDENTIFIES_VOYNICH_ARCHITECTURE","evidence":"Both controls are constructed and no Voynich source or image is read.","impact":"Only instrument sensitivity/specificity is calibrated."},
    ]
    write(INFO,info);write(DECODER,dec);write(RECOVERY,matrix);write(COUNTER,counters)
    a_host=info_by["SYSTEM_A","PAGE_HOST"];b_host=info_by["SYSTEM_B","PAGE_HOST"];b_full=info_by["SYSTEM_B","FULL_TUPLE_PLUS_SLOT"]
    report=f"""# GDT168 — synthetic architecture calibration report

Status: **HOST_NEGATIVES_DO_NOT_DISTINGUISH_LEXICAL_FROM_DISTRIBUTED_CODE**.

## Ground truth

| system | true architecture | host information fraction | full tuple + slot information fraction | held-unit host decoder accuracy/coverage |
|---|---|---:|---:|---:|
| A | injective 2--3-character concept codebook | {a_host['fraction_concept_entropy']:.3f} | {info_by['SYSTEM_A','FULL_TUPLE_PLUS_SLOT']['fraction_concept_entropy']:.3f} | {dec_by['SYSTEM_A','PAGE_HOST']['accuracy_on_predictions']:.3f}/{dec_by['SYSTEM_A','PAGE_HOST']['coverage']:.3f} |
| B | slot/wrapper/100-way host/right/closure mixed-radix code | {b_host['fraction_concept_entropy']:.3f} | {b_full['fraction_concept_entropy']:.3f} | {dec_by['SYSTEM_B','PAGE_HOST']['accuracy_on_predictions']:.3f}/{dec_by['SYSTEM_B','PAGE_HOST']['coverage']:.3f} |

The encoders are exactly reversible by construction.  Held-unit decoders are
stricter empirical tests: they cannot decode representations absent from all
other source units.

## What the blind diagnostics recovered

| diagnostic | A | B | calibration verdict |
|---|---|---|---|
"""+"".join(f"| {x['diagnostic']} | {x['blind_a']} | {x['blind_b']} | {x['assessment']} |\n" for x in matrix)+f"""

## Main finding

The negative exact-host results do **not** distinguish the two hypotheses.
The true lexical codebook loses every held compiler/external-context test,
while the nonlexical distributed host often looks less negative.  Conversely,
surface compatibility and perfect cross-register alignment are positive in
both systems and are stronger in the distributed notation on compatibility.

The one useful discriminator is endpoint localization: compiler-coupled
one-glyph substitution coherence appears in B ({s['CONTROL_Y']['GDT163_164_SUBSTITUTION:COMPILER_DELTA_COSINE']:.3f})
but not A ({s['CONTROL_X']['GDT163_164_SUBSTITUTION:COMPILER_DELTA_COSINE']:.3f}),
and disappears on the parser-independent external endpoint in both.  That is
exactly the pattern expected from distributed same-group coding rather than a
productive external lexical relation.

## Consequence for Voynich work

GDT162--167 negative host likelihoods may reject a *predictive opaque context
codebook at their tested resolution*, but they cannot reject a real sparse
lexical address whose compiler is independent of content.  GDT167 alignment
can establish re-rendering geometry but not lexicality.  To distinguish the
hypotheses, a future test needs an external content endpoint or recoverable
cross-record referent, not another host-to-neighbor likelihood.

No Voynich source table or image was used.  f84r was not accessed.
"""
    REPORT.write_text(report,encoding="utf-8")
    result={"schema":"GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_RESULT_V1","status":"HOST_NEGATIVES_DO_NOT_DISTINGUISH_LEXICAL_FROM_DISTRIBUTED_CODE",
            "ground_truth":{"system_a_host_information_fraction":a_host["fraction_concept_entropy"],"system_b_host_information_fraction":b_host["fraction_concept_entropy"],"system_b_full_tuple_slot_information_fraction":b_full["fraction_concept_entropy"],
                            "system_a_host_decoder":dec_by["SYSTEM_A","PAGE_HOST"],"system_b_host_decoder":dec_by["SYSTEM_B","PAGE_HOST"],"system_b_full_decoder":dec_by["SYSTEM_B","FULL_TUPLE_PLUS_SLOT"]},
            "blind_result_sha256":sha(BLIND_RESULT),"interpretation":"Negative exact-host context transfer is not sensitive to every genuine lexical codebook; compatibility and renderer alignment are not specific to lexical hosts.",
            "inputs":{p.name:sha(p) for p in (BLIND,TRUTH,CODEBOOK,FREEZE,BLIND_RESULT,BLIND_SUMMARY)},"implementation":{Path(__file__).name:sha(Path(__file__))},
            "outputs":{p.name:sha(p) for p in (INFO,DECODER,RECOVERY,COUNTER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},
            "f84r":{"opened":False,"queried":False,"retained":False,"joined":False,"scored":False},
            "claim_ceiling":"Synthetic instrument calibration only; no Voynich word, code value, language, semantic role, meaning, plaintext, or translation."}
    result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"a_host_info":a_host["fraction_concept_entropy"],"b_host_info":b_host["fraction_concept_entropy"],"b_full_info":b_full["fraction_concept_entropy"]},sort_keys=True))


if __name__=="__main__":main()
