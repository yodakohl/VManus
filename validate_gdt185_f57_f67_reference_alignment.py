#!/usr/bin/env python3
"""Independent retained-artifact validation for GDT185 (no runner import)."""

import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
RESULT=ROOT/"gdt185_result.json"; SCORES=ROOT/"gdt185_alignment_scores.tsv"
BEST=ROOT/"gdt185_best_alignment.tsv"; COUNTER=ROOT/"gdt185_counterexamples.tsv"
METHOD=ROOT/"GDT185_F57_F67_REFERENCE_ALIGNMENT_METHOD.md"; REPORT=ROOT/"GDT185_F57_F67_REFERENCE_ALIGNMENT_REPORT.md"
VALID=ROOT/"gdt185_validation.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with p.open(encoding="utf-8") as h:return list(csv.DictReader(h,delimiter="\t"))

def selected_rows():
    target={f"f67v1.{i}" for i in range(13,30)}
    raw=[]
    with SOURCE.open(encoding="utf-8") as h:
        header=h.readline().rstrip("\n").split("\t")
        for line in h:
            prefix=line.split("\t",3); locus=prefix[2]
            if locus!="f57v.3" and locus not in target: continue
            assert not locus.startswith("f84"); parts=line.rstrip("\n").split("\t"); raw.append(parts)
    digest=hashlib.sha256(("\t".join(header)+"\n"+"\n".join("\t".join(x) for x in raw)+"\n").encode()).hexdigest()
    return [dict(zip(header,x)) for x in raw],digest

def direct_best(key,targets,mode):
    best=-1
    for reflected in (False,True):
        base=list(reversed(key)) if reflected else list(key)
        for rotation in range(17):
            assigned=base[rotation:]+base[:rotation]
            score=0
            for symbol,target in zip(assigned,targets):
                score += symbol in target if mode=="ANY" else symbol==target[0] if mode=="FIRST" else symbol==target[-1]
            best=max(best,score)
    return best

def main():
    r=json.loads(RESULT.read_text()); s=read(SCORES); b=read(BEST); c=read(COUNTER); checks=[]
    def ck(name, cond):
        assert cond, name; checks.append(name)
    ck("status",r["status"]=="F57_R2_DOES_NOT_INDEX_F67V1_17_SECTOR_TEXT")
    ck("score_rows",len(s)==18); ck("best_rows",len(b)==18); ck("counter_rows",len(c)==5)
    ck("editions",{x["edition"] for x in s}=={"ZL3b","IT2a","RF1b"})
    ck("six_metrics_each",all(sum(x["edition"]==e for x in s)==6 for e in ("ZL3b","IT2a","RF1b")))
    ck("metric_set",{x["metric"] for x in s}=={f"{a}_{b}" for a in ("CODE","FAMILY") for b in ("ANY","FIRST","LAST")})
    zl={x["metric"]:x for x in s if x["edition"]=="ZL3b"}
    ck("zl_code_any",int(zl["CODE_ANY"]["observed_best"])==7)
    ck("zl_no_local_signal",all(float(x["local_p"])>.80 for x in zl.values()))
    ck("all_max_six_nonpositive",all(float(v["max_six_p"])>.05 for v in r["reading_summary"].values()))
    ck("gates_fail",not r["gates"]["all_pass"])
    ck("source_count",r["counts"]["selected_source_rows"]==375)
    rows,digest=selected_rows()
    ck("independent_selected_source_count",len(rows)==375)
    ck("independent_selected_source_digest",digest==r["provenance"]["selected_source_payload_sha256"])
    rebuilt={}; loci=[f"f67v1.{i}" for i in range(13,30)]
    for edition in ("ZL3b","IT2a","RF1b"):
        r2=sorted((x for x in rows if x["edition"]==edition and x["locus"]=="f57v.3"),key=lambda x:int(x["source_group_index"]))[:17]
        for representation in ("CODE","FAMILY"):
            key=[x["primary_sta_codes"].split()[0] if representation=="CODE" else x["primary_sta_families"][0] for x in r2]
            targets=[]
            for locus in loci:
                rr=sorted((x for x in rows if x["edition"]==edition and x["locus"]==locus),key=lambda x:int(x["source_group_index"]))
                targets.append([z for x in rr for z in (x["primary_sta_codes"].split() if representation=="CODE" else list(x["primary_sta_families"]))])
            for mode in ("ANY","FIRST","LAST"):
                rebuilt[(edition,f"{representation}_{mode}")]=direct_best(key,targets,mode)
    ck("independent_observed_alignment_scores",all(rebuilt[(x["edition"],x["metric"])]==int(x["observed_best"]) for x in s))
    ck("target_count",r["counts"]["target_sectors"]==17)
    ck("null_count",r["counts"]["null_worlds_per_reading"]==65536)
    ck("no_f84_output",all("f84" not in p.read_text().lower() for p in (SCORES,BEST,COUNTER)))
    ck("f84_flags",not r["f84r_accessed"] and not r["provenance"]["f84r_formal_payload_retained_parsed_joined_scored"] and r["provenance"]["nonselected_rows_guarded_before_formal_field_parsing"])
    ck("output_hashes",all(r["outputs"][p.name]==sha(p) for p in (SCORES,BEST,COUNTER)))
    ck("document_hashes",all(r["documents"][p.name]==sha(p) for p in (METHOD,REPORT)))
    ck("implementation_hash",r["implementation"]==sha(ROOT/"run_gdt185_f57_f67_reference_alignment.py"))
    out={"experiment":"GDT185_VALIDATION","status":"PASS","checks":len(checks),"check_names":checks,"result_sha256":sha(RESULT)}
    VALID.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("PASS",len(checks))
if __name__=="__main__":main()
