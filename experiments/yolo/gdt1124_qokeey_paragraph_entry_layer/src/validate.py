#!/usr/bin/env python3
"""Recompute entry projection and strict register consequences; no meaning test."""
import csv,hashlib,io,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent.parent; ROOT=D.parents[2]
spec=json.loads((D/"src/SPEC.json").read_text())
for name,digest in spec["hashes"].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest

def projection(path,selector,values,cols):
    cmd=["./vmanus-exp","query-tsv",path,"--selector",selector]
    for v in sorted(values):cmd.extend(["--allow",v])
    cmd.extend(["--columns",",".join(cols),"--forbid-prefix","f84","--forbid-prefix","f84r"])
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    return r.stdout,list(csv.DictReader(io.StringIO(r.stdout),delimiter="\t"))
B="experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts/"
text,blocks=projection(B+"BLOCKS.tsv","page",spec["pages"],["block_id","page","kind","complete","first","last","qokeey_targets_json"])
assert text==(D/"artifacts/SOURCE_BLOCKS.tsv").read_text()
chosen={b["block_id"]:b for b in blocks if b["kind"]=="P" and b["complete"]=="1" and json.loads(b["qokeey_targets_json"])}
text,groups=projection(B+"SOURCE_GROUPS.tsv","locus",{b["first"] for b in chosen.values()},["source_group_id","edition","locus","page","source_group_index","paragraph_start","left_separator","right_separator","ivtff_group_raw"])
assert text==(D/"artifacts/SOURCE_FIRST_LINES.tsv").read_text()
first={(g["locus"],g["edition"]):g for g in groups if int(g["source_group_index"])==1}
entries=list(csv.DictReader((D/"artifacts/ENTRY_TABLE.tsv").open(),delimiter="\t"))
assert {(e["block_id"],e["edition"]) for e in entries}=={(b,e) for b in chosen for e in spec["editions"]}
assert len(entries)==len(chosen)*len(spec["editions"])
counter=[];boundary_unscored=0;other_unscored=0
for e in entries:
    g=first[chosen[e["block_id"]]["first"],e["edition"]]
    assert e["source_group_id"]==g["source_group_id"] and e["first_raw"]==g["ivtff_group_raw"]
    assert g["left_separator"]=="LINE_START" and e["source_paragraph_start"]==g["paragraph_start"]
    if g["paragraph_start"]!="1":expected="UNSCOREABLE_NATIVE_BOUNDARY";boundary_unscored+=1
    elif g["ivtff_group_raw"]=="qokeey":expected="STRICT_ENTRY_LAYER_UNDERFLOW";counter.append(g["source_group_id"])
    else:expected="NOT_TESTED_BY_ENTRY_SCREEN";other_unscored+=1
    assert e["result"]==expected
result=json.loads((D/"artifacts/RESULT.json").read_text())
assert result["complete_target_blocks"]==len(chosen) and result["reader_entries"]==len(entries)
assert result["exact_initial_qokeey"]==len(counter)
assert result["unscoreable_native_boundary"]==boundary_unscored and result["other_entries_not_tested"]==other_unscored
post=json.loads((D/"artifacts/POSTHOC_PAINT_ENTRY.json").read_text())
assert len(post["whole_table"])==len(entries)
assert {c["source_group_id"] for c in post["cases"]}=={g["source_group_id"] for g in first.values() if g["paragraph_start"]=="1" and g["ivtff_group_raw"]=="qokeedy"}
v={"status":"PASS_SOURCE_ENTRY_ACCOUNTING_ONLY","complete_blocks":len(chosen),"reader_entries":len(entries),"initial_qokeey_countercases":len(counter),"RF_boundary_unscored":boundary_unscored,"posthoc_qokeedy_cases":len(post["cases"]),"semantic_validation":False,"whole_grammar_executed":False,"registered_qokeey_support":False}
(D/"artifacts/VALIDATION.json").write_text(json.dumps(v,indent=2)+"\n");print(json.dumps(v))
