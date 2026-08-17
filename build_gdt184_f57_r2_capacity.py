#!/usr/bin/env python3
"""Re-evaluate the semantic capacity of f57 R2 from frozen GDT179 facts."""

import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
R2=ROOT/"gdt179_r2_partition.tsv"
G179=ROOT/"gdt179_result.json"
G182=ROOT/"gdt182_result.json"
METHOD=ROOT/"GDT184_F57_R2_REFERENCE_RING_METHOD.md"
REPORT=ROOT/"GDT184_F57_R2_REFERENCE_RING_REPORT.md"
COLUMNS=ROOT/"gdt184_r2_capacity.tsv"
MODELS=ROOT/"gdt184_r2_model_comparison.tsv"
COUNTER=ROOT/"gdt184_counterexamples.tsv"
RESULT=ROOT/"gdt184_result.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with p.open(encoding="utf-8") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows):
    with p.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)

def main():
    r2=read(R2); g179=json.loads(G179.read_text()); g182=json.loads(G182.read_text())
    assert len(r2)==4 and [r["r2_slot9_state"] for r in r2]==["f","f","p","p"]
    assert g179["counts"]["r2_stable_changing_columns"]==1
    assert not g179["f84r_accessed"] and not g182["f84r_accessed"]
    profiles=[r["r2_slot9_state"] for r in r2]
    unique=len(set(profiles)); bits=math.log2(unique)
    columns=[
      {"quantity":"periods","value":4,"interpretation":"FOUR_PHYSICAL_REPETITIONS"},
      {"quantity":"positions_per_period","value":17,"interpretation":"ORDERED_REFERENCE_SEQUENCE_LENGTH"},
      {"quantity":"all_reading_stable_changing_columns","value":1,"interpretation":"ONLY_SLOT9_DISTINGUISHES_PERIODS_STABLY"},
      {"quantity":"stable_noncontrasting_columns","value":16,"interpretation":"NO_STABLE_PERIOD_ID_INFORMATION"},
      {"quantity":"unique_stable_period_profiles","value":unique,"interpretation":"FF_VERSUS_PP_ONLY"},
      {"quantity":"stable_profile_capacity_bits","value":bits,"interpretation":"ONE_BIT_CANNOT_IDENTIFY_FOUR_SECTORS"},
      {"quantity":"bits_needed_for_four_unique_sector_ids","value":2,"interpretation":"MINIMUM_UNIQUE_ID_CAPACITY"},
    ];write(COLUMNS,columns)
    models=[
      {"model":"FOUR_ELEMENT_ID_TABLE","fit":"FAILED_CAPACITY","reason":"One stable bit supplies two profiles, not four unique sector identities.","rank":4},
      {"model":"FOUR_ELEMENT_SINGLE_BINARY_PROPERTY","fit":"POSSIBLE_BUT_NONIDENTIFYING","reason":"The f,f,p,p column can encode one two-versus-two property, but hot/cold, page half, and Latin gender remain exact aliases.","rank":2},
      {"model":"FOURFOLD_REFERENCE_OR_CALIBRATION_SEQUENCE","fit":"LEADING","reason":"A 17-position ordered sequence is copied four times with one stable binary variant and no need for four semantic row IDs.","rank":1},
      {"model":"CIPHER_KEY_OR_ALPHABET","fit":"WEAK_SPECULATION","reason":"Repetition is compatible with a key/reference function, but no mapping, rotation, or strict alphabetic inventory is demonstrated.","rank":3},
      {"model":"ORNAMENTAL_OR_SCRIBAL_REPETITION","fit":"LIVE_ALTERNATIVE","reason":"Near-copying alone does not establish technical function.","rank":2},
    ];write(MODELS,models)
    counter=[
      {"id":"C1","finding":"Only slot 9 changes stably across all readings.","impact":"R2 cannot provide four stable element identifiers."},
      {"id":"C2","finding":"The stable pattern is f,f,p,p.","impact":"Rows 1/2 and 3/4 are indistinguishable at the stable contrast."},
      {"id":"C3","finding":"The same split is hot/cold, upper/lower, and Latin masculine/feminine under the exposed comparator.","impact":"Even the one bit has no unique semantic value."},
      {"id":"C4","finding":"GDT182 found the nearby four-label decoders nonunique after feature multiplicity.","impact":"The ring cannot inherit semantic certainty from those labels."},
      {"id":"C5","finding":"No rotation, substitution table, or readable key legend is present.","impact":"Reference/calibration is a generative role, not a proven cipher key."},
    ];write(COUNTER,counter)
    result={
      "experiment":"GDT184_F57_R2_SEMANTIC_CAPACITY_REASSESSMENT",
      "status":"R2_FOURFOLD_REFERENCE_SEQUENCE_LEADING_FOUR_ELEMENT_ID_TABLE_FAILED",
      "headline":"f57 R2 has one stable bit for four periods and therefore behaves more like a repeated reference/calibration sequence than four uniquely identified semantic records.",
      "counts":{"periods":4,"positions_per_period":17,"stable_changing_columns":1,"stable_noncontrasting_columns":16,"unique_stable_profiles":unique},
      "capacity":{"available_bits":bits,"required_unique_sector_bits":2,"deficit_bits":1},
      "leading_model":"FOURFOLD_REFERENCE_OR_CALIBRATION_SEQUENCE_WITH_ONE_BINARY_VARIANT",
      "demoted_model":"FOUR_ELEMENT_PROPERTY_TABLE_AS_FOUR_IDENTIFIED_ROWS",
      "claim_ceiling":"A capacity-based role hypothesis for one exposed f57 ring. It establishes no alphabet, cipher key, element, quality, glyph value, word, language, plaintext, or translation.",
      "inputs":{p.name:sha(p) for p in (R2,G179,G182)},
      "outputs":{p.name:sha(p) for p in (COLUMNS,MODELS,COUNTER)},
      "documents":{p.name:sha(p) for p in (METHOD,REPORT)},
      "implementation":sha(Path(__file__)),"f84r_accessed":False,
    }
    RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(result["status"])
if __name__=="__main__":main()
