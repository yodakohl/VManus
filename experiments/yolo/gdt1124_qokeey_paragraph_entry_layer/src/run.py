#!/usr/bin/env python3
"""Necessary initial-register check only. Not a decoder or whole grammar."""
import csv, hashlib, io, json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent.parent
ROOT=D.parents[2]
B="experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts"

def query(path,selector,values,columns):
    args=["./vmanus-exp","query-tsv",path,"--selector",selector]
    for value in sorted(values):args.extend(["--allow",value])
    args.extend(["--columns",",".join(columns),"--forbid-prefix","f84","--forbid-prefix","f84r"])
    result=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,check=True)
    return list(csv.DictReader(io.StringIO(result.stdout),delimiter="\t")),result.stdout,{"command":args,"guard_stats":result.stderr.strip()}

def write_tsv(path,rows,columns):
    with path.open("w",newline="") as out:
        w=csv.DictWriter(out,fieldnames=columns,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)

def main():
    spec=json.loads((D/"src/SPEC.json").read_text())
    for path,expected in spec["hashes"].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    assert all(not p.startswith("f84") for p in spec["pages"])
    bc=["block_id","page","kind","complete","first","last","qokeey_targets_json"]
    blocks,btext,g1=query(B+"/BLOCKS.tsv","page",spec["pages"],bc)
    chosen=[b for b in blocks if b["kind"]=="P" and b["complete"]=="1" and json.loads(b["qokeey_targets_json"])]
    assert chosen
    cols=["source_group_id","edition","locus","page","source_group_index","paragraph_start","left_separator","right_separator","ivtff_group_raw"]
    source,stext,g2=query(B+"/SOURCE_GROUPS.tsv","locus",{b["first"] for b in chosen},cols)
    first={(r["locus"],r["edition"]):r for r in source if r["source_group_index"]=="1"}
    rows=[]
    for b in chosen:
        for edition in spec["editions"]:
            r=first[b["first"],edition]
            assert r["left_separator"]=="LINE_START"
            boundary=r["paragraph_start"]=="1"
            exact=r["ivtff_group_raw"]==spec["target"]
            rows.append({"block_id":b["block_id"],"page":b["page"],"edition":edition,"source_group_id":r["source_group_id"],"first_raw":r["ivtff_group_raw"],"initial_Layer_count":0,"source_paragraph_start":r["paragraph_start"],"required_Layer_count":1 if exact and boundary else "NOT_TESTED","result":"UNSCOREABLE_NATIVE_BOUNDARY" if not boundary else ("STRICT_ENTRY_LAYER_UNDERFLOW" if exact else "NOT_TESTED_BY_ENTRY_SCREEN")})
    (D/"artifacts/SOURCE_BLOCKS.tsv").write_text(btext)
    (D/"artifacts/SOURCE_FIRST_LINES.tsv").write_text(stext)
    write_tsv(D/"artifacts/ENTRY_TABLE.tsv",rows,list(rows[0]))
    counter=[r for r in rows if r["result"]=="STRICT_ENTRY_LAYER_UNDERFLOW"]
    result={"experiment_id":"GDT1124","status":"STRICT_ENTRY_COUNTERCASE" if counter else "NO_FIRST_GROUP_COUNTERCASE__NO_MEANING_SUPPORT","complete_target_blocks":len(chosen),"reader_entries":len(rows),"physical_leaves":len({r["page"].split('r')[0].split('v')[0] for r in rows}),"exact_initial_qokeey":len(counter),"countercases":counter,"other_entries_not_tested":sum(r["result"]=="NOT_TESTED_BY_ENTRY_SCREEN" for r in rows),"unscoreable_native_boundary":sum(r["result"]=="UNSCOREABLE_NATIVE_BOUNDARY" for r in rows),"whole_grammar_executed":False,"confirmed_words":0,"independent_meaning_credit":0,"new_admissions":0,"sealed":["f84","f84r"],"guarded_queries":[g1,g2]}
    (D/"artifacts/RESULT.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ["guarded_queries","countercases"]},ensure_ascii=False))
if __name__=="__main__":main()
