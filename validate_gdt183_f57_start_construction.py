#!/usr/bin/env python3
"""Independent retained-artifact validator for GDT183."""

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name):
    with (ROOT/name).open(encoding="utf-8") as h: return list(csv.DictReader(h, delimiter="\t"))

def main():
    result=json.loads((ROOT/"gdt183_result.json").read_text())
    occ=rows("gdt183_start_construction_occurrences.tsv")
    stats=rows("gdt183_start_construction_statistics.tsv")
    counter=rows("gdt183_counterexamples.tsv")
    checks=[]
    assert len(occ)==5 and occ[0]["locus"]=="f57v.1"; checks.append("occurrence_count")
    prose=occ[1:]
    assert all(r["family"]=="BAFAB" and r["position"]=="FIRST" for r in prose); checks.append("four_first")
    assert len({r["record_state"] for r in prose})==3; checks.append("state_heterogeneity")
    vals={r["test"]:r for r in stats}
    n=int(vals["D_WRAPPER_FIRST_RATE"]["denominator"]); k=int(vals["D_WRAPPER_FIRST_RATE"]["numerator"])
    p=math.comb(k,4)/math.comb(n,4)
    assert abs(float(vals["BAFAB_VS_D_WRAPPER_HYPERGEOMETRIC"]["value"])-p)<1e-15; checks.append("hypergeometric")
    assert (int(vals["COUNT4_FAMILY_SEARCH_RATE"]["numerator"]),int(vals["COUNT4_FAMILY_SEARCH_RATE"]["denominator"]))==(2,83); checks.append("family_search")
    assert len(counter)==6; checks.append("counterexamples")
    assert result["status"]=="D_WRAPPED_BAFAB_ENTRY_ENRICHED_WHOLE_WORD_START_GLOSS_NOT_SUPPORTED"; checks.append("status")
    assert result["interpretation"]["best_parse"].startswith("d[ENTRY_WRAPPER]"); checks.append("parse_ceiling")
    for name,digest in result["inputs"].items(): assert sha(ROOT/name)==digest; checks.append("input:"+name)
    for name,digest in result["outputs"].items(): assert sha(ROOT/name)==digest; checks.append("output:"+name)
    for name,digest in result["documents"].items(): assert sha(ROOT/name)==digest; checks.append("document:"+name)
    assert sha(ROOT/"run_gdt183_f57_start_construction.py")==result["implementation"]; checks.append("implementation")
    assert not result["f84r_accessed"] and not any(r["page"].startswith("f84") for r in occ); checks.append("f84r_seal")
    validation={"experiment":result["experiment"],"status":"PASS","checks_passed":len(checks),"checks":checks,"result_sha256":sha(ROOT/"gdt183_result.json")}
    (ROOT/"gdt183_validation.json").write_text(json.dumps(validation,sort_keys=True,indent=2)+"\n")
    print(f"PASS {len(checks)}/{len(checks)}")

if __name__=="__main__": main()
